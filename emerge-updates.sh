#!/bin/sh -e

echo 'Analyzing `emerge -pvuDN --with-bdeps=y @world` ...'

emerge -pvuDN --with-bdeps=y @world --columns 2>&1 \
| awk '/^\[/ && $2 ~ /[UN]/ {
	state=$2
	ebuild=$4
	newv=$5
	gsub(/^\[|:.*/, "", newv)

	if ($2 == "N")
		printf "* %s, Version %s (neu)\n", ebuild, newv
	else {
		oldv=$6
		gsub(/^\[|:.*/, "", oldv)
		printf "* %s, von Version %s auf %s\n", ebuild, oldv, newv
	}
}'
