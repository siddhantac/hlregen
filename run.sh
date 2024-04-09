#!/bin/sh

dates=( "2023/01" "2023/02" "2023/03" "2023/04" )

CONTINUE=1
for date in "${dates[@]}"
do
    if [ $CONTINUE -eq 0 ]; then
        exit 0
    fi

    echo ""
    echo "---"
    ./process.py --account "assets:bank:dbs_twisha" --date "$date"
    gum confirm "Continue?" && CONTINUE=1 || CONTINUE=0
done
