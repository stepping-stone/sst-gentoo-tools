#!/usr/bin/env python3

import sys, re
import argparse
import datetime

lang = None

class Atom:
    operator   = None
    category   = None
    name       = None
    version    = None
    release    = None
    revision   = None
    repository = None

    def __init__(self, atom):
        matches = re.match("""
            ^
            (?P<operator>[<>]?=?)
            ((?P<category>[^\/]+)\/)?
            (?P<name>\S+?)
            (-
                (?P<version>
                    (\d+(\.\d+)*[a-z]?
                        (_(?P<release>(alpha|beta|pre|rc|p)\d*))*
                        (-r(?P<revision>\d+))?
                    )?
                )
            )?
            (::(?P<repository>\S+))?
            $
        """, atom, re.VERBOSE)

        if not matches:
            return None

        self.__dict__.update(matches.groupdict())

def t(s):
    # Currently, only German is supported.
    langs = [ 'de' ]

    if lang not in langs:
        # Either English or an unknown language.
        return s

    idx = langs.index(lang)
    trans = { 'and'                     : [ 'und' ]
            , 'replaces'                : [ 'ersetzt' ]
            , 'replace'                 : [ 'ersetzen' ]
            , 'removed'                 : [ 'entfernt' ]
            , 'new'                     : [ 'neu' ]
            , 'Newly installed software': [ 'Neu installierte Software' ]
            , 'Removed software'        : [ 'Deinstallierte Software' ]
            , 'Upgrades or downgrades'  : [ 'Upgrades oder Downgrades' ]
            }

    return trans[s][idx] if s in trans else s

def ljoin(lst):
    if len(lst) == 1:
        return lst[0]
    elif len(lst) < 3:
        return '%s %s %s' % (lst[0], t('and'), lst[1])
    else:
        return '%s %s %s' % (', '.join(lst[:-1]), t('and'), lst[-1:][0])

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument('-l', '--logfile', type=str, help='path to emerge.log', default='/var/log/emerge.log')
    argparser.add_argument('-L', '--lang', type=str, help='output language (either "en" or "de")', default='de')
    argparser.add_argument('-c', '--compact', help='whether to use compact output', action='store_true', default=False)
    #argparser.add_argument('-d', '--date', help='select emerge events by date or time span. Possible values: "any", "YYYYMMDD-YYYYMMDD"', default='any')

    opts = argparser.parse_args(sys.argv[1:])
    lang = opts.lang
    atoms = {}

    with open(opts.logfile) as fp:
        lines = [ line.strip() for line in fp.readlines() ]

    for line in lines:
        matches = re.match('^([0-9]+):  ::: completed (emerge) \([0-9]+ of [0-9]+\) ([^ ]+) to .*', line)

        if not matches:
            matches = re.match('^([0-9]+):  >>> (unmerge) success: (.*)$', line)

        if matches:
            #date = datetime.datetime.fromtimestamp(int(matches.groups()[1]))
            atom = Atom(matches.groups()[2])
            pkg = '%s/%s' % (atom.category, atom.name)

            if pkg not in atoms:
                atoms[pkg] = { 'emerge': [], 'unmerge': [] }

            atoms[pkg][matches.groups()[1]].append(atom.version)

    new = []
    removed = []
    replaced = []

    for pkg in sorted(atoms):
        # "list . set" creates an unique list
        e = list(set(atoms[pkg]['emerge']))
        u = list(set(atoms[pkg]['unmerge']))
        remove = []

        for v in e:
            if v in u:
                remove.append(v)

        for v in remove:
            e.remove(v)
            u.remove(v)

        if len(e) == 0 and len(u) == 0:
            continue

        s = '* %s ' % pkg

        if len(e) > 0:
            s += ljoin(e)

        if len(u) > 0:
            if len(e) == 1:
                replaced.append(s + (' (%s %s)' % (t('replaces'), ljoin(u))))
            elif len(e) > 1:
                replaced.append(s + (' (%s %s)' % (t('replace'), ljoin(u))))
            else:
                removed.append(s + (('%s %s' % (ljoin(u), t('removed'))) if opts.compact else ljoin(u)))
        else:
            new.append(s + (' (%s)' % t('new') if opts.compact else ''))

    if opts.compact:
        for s in sorted(new + removed + replaced):
            print(s)
    else:
        if len(new) > 0:
            print(t('Newly installed software') + ':')
            for s in new:
                print(s)
            print()

        if len(removed) > 0:
            print(t('Removed software') + ':')
            for s in removed:
                print(s)
            print()

        if len(replaced) > 0:
            print(t('Upgrades or downgrades') + ':')
            for s in replaced:
                print(s)
