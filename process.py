#!/usr/bin/env python3


# [x] 1 journal to csv
# [x] 2 parse csv, load into memory
# [x] 3 re-create csv without accounts
# [x] 4 import csv with hledger and create new csv
# [x] 5 parse csv
# [x] 6 filter out unknown txns
# [x] 7 find corresponding records in csv created in 2
# [x] 8 update the csv from 3 with account names only for records identified in 7
# [x] 9 print csv
# [ ] 10 balance!

# 10 error checking

import subprocess
import csv
import sys

account="assets:bank:ocbc_sid"
date="2023/05"

class Transaction:
    def __init__(self, cols):
        self.txn_id = cols[0]
        self.date = cols[1]
        self.code = cols[4]
        self.description = cols[5]
        self.comment = cols[6]
        self.account = cols[7]
        self.credit = cols[10]
        self.debit = cols[11]
        self.keep_account = False

    def __str__(self):
        return f"{self.txn_id}, {self.date}, {self.description}, {self.credit}, {self.debit}, {self.account}, {self.comment}, {self.code}"

    def __repr__(self):
        return f"id={self.txn_id}, date={self.date}, desc={self.description}, credit={self.credit}, debit={self.debit}, account={self.account}, comment={self.comment}, code={self.code}"

    def __eq__(self, other):
        return self.description == other.description and self.credit == other.credit and self.debit == other.debit and self.account == other.account and self.comment == self.comment and self.code == self.code

def txns_from_csv(command):
    csv_file = subprocess.run(command, capture_output=True, text=True)
    lines = csv_file.stdout.split('\n')

    header = lines[0]
    txns = []
    for l in lines[1:]:
        if len(l) == 0:
            continue
        cols = l.split(',')
        txn = Transaction(cols)
        txns.append(txn)

    return header, txns

# 1 journal to csv
# 2 parse csv and load into memory
header, all_txns = txns_from_csv(["hledger", "print", account,  "-p", date, "-O", "csv"])
filtered_txns = [t for t in all_txns if account not in t.account]

# 3 re-create csv without accounts
filename = '202305_ocbc_sid.csv' 
tmp_filename = 'tmp_' + filename
with open(tmp_filename,'w', newline='') as f:
    f.write("txn_id,date,description,credit,debit,account,comment,code\n")
    for txn in filtered_txns:
        f.write(f"{txn.txn_id},{txn.date},{txn.description},{txn.credit},{txn.debit},,{txn.comment},{txn.code}\n")


# [ ] 4 import csv with hledger and create new csv
# [ ] 5 parse csv
_, txns = txns_from_csv(["hledger", "print", "-f", tmp_filename, "--rules-file", "ocbc.rules", "-O", "csv"])

# [ ] 6 filter out unknown txns
unknown_txns = [t for t in txns if "unknown" in t.account]

def txn_uniq_id(txn):
    return txn.date + txn.description + txn.credit + txn.debit

def find_txn_idx(txn, txns):
    uid = txn_uniq_id(txn)
    for idx, t in enumerate(txns):
        if uid == txn_uniq_id(t):
            return idx 
    return -1

# 7
for ut in unknown_txns:
    idx = find_txn_idx(ut, filtered_txns)
    if idx != -1:
        filtered_txns[idx].keep_account = True
        print("unknowns found:", filtered_txns[idx])


with open(filename,'w', newline='') as f:
    f.write(header+"\n")
    for t in filtered_txns:
        if not t.keep_account:
            f.write(f"{t.txn_id},{t.date},{t.description},{t.credit},{t.debit},,{t.comment},{t.code}\n")
        else:
            f.write(f"{t.txn_id},{t.date},{t.description},{t.credit},{t.debit},{t.account},{t.comment},{t.code}\n")

# error checking

_, original_txns = txns_from_csv(["hledger", "print", account,  "-p", date, "-O", "csv"])
_, new_txns = txns_from_csv(["hledger", "print", "-f", filename, "--rules-file", "ocbc.rules", "-O", "csv"])

if len(original_txns) != len(new_txns):
    print("unequal no. of txns")
    print(len(original_txns), len(new_txns))
    sys.exit(1)

for idx, t in enumerate(original_txns):
    if t != new_txns[idx]:
        print("unequal txns", idx)
        print(t) 
        print(new_txns[idx])
        sys.exit(1)

