#!/bin/sh -e

echo 'Analyzing `emerge -pvuDN --with-bdeps=y @world` ...'

emerge -pvuDN --with-bdeps=y @world --columns 2>&1 \
| awk '/^\[/{
    state=$2
    sub(/^\[[^]]+\] /, "")		# remove "[binary  NS   ~] "
    ebuild=$1				# sys-kernel/gentoo-sources-4.4.29:4.4.29::gentoo
    newv=$2				# [1.8.16::gentoo]
    oldv=$3				# [1.8.15-r1::gentoo]
    gsub(/^\[|:.*/, "", newv)		# [1.8.16::gentoo]	-> 1.8.16
    gsub(/^\[|:.*/, "", oldv)		# [1.8.15-r1::gentoo]	-> 1.8.15-r1

    if (state ~ /U/) {
        newm=newv
        sub(/^[^.][._-]/, "", newm)	# 1.8.16	-> 8.16
        sub(/[._-].*/, "", newm)	# 8.16		-> 8
        oldm=oldv
        sub(/^[^.][._-]/, "", oldm)	# 1.8.15-r1	-> 8.15-r1
        sub(/[._-].*/, "", oldm)	# 8.15-r1	-> 8
        if (newm > oldm)
            print "WARNING: " ebuild ": " oldv " -> " newv
    }
    else if (state !~ /[NrR]/)
        print "ERROR: unknown state '\''" state "'\''"
}'
