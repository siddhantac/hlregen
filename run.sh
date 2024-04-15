#!/bin/sh

# dates=( "2023/01" "2023/02" "2023/03" "2023/04" )
dates=( "2023/01" )
accounts=( \
    "assets:bank:dbs_sid" \
    "assets:bank:dbs_twisha" \
    "assets:bank:ocbc_sid" \
    "liabilities:credit_card:citibank_prem_miles" \
    "liabilities:credit_card:amex" \
)

CONTINUE=1
for date in "${dates[@]}"
do
    # if [ $CONTINUE -eq 0 ]; then
    #     exit 0
    # fi

    for acc in "${accounts[@]}"
    do
        echo ""
        echo "---"
        # ./process.py --account "assets:bank:dbs_twisha" --date "$date"
        ./process.py --account "$acc" --date "$date"
        # gum confirm "Continue?" && CONTINUE=1 || CONTINUE=0
    done
done
