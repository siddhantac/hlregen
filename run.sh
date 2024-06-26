#!/bin/sh

# dates=( "2023/01" "2023/02" "2023/03" "2023/04" )
# dates=( "2024/02" )

dates=
if [ -z "$1" ]; then
    echo "date is required"
    exit 1
fi

dates=( $1 )

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
    for acc in "${accounts[@]}"
    do
        if [ $CONTINUE -eq 0 ]; then
            exit 0
        fi

        echo ""
        echo "---"
        ./process.py --account "$acc" --date "$date"
        gum confirm "Continue?" && CONTINUE=1 || CONTINUE=0
    done
done
