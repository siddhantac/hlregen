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

# 9 error checking

import subprocess
import csv

account="assets:bank:ocbc_sid"
date="2023/05"

# 1 journal to csv
output = subprocess.run(["hledger", "print", account,  "-p", date, "-O", "csv"], capture_output=True, text=True)
csv_data = output.stdout 

lines = csv_data.split('\n')
data = []

for l in lines:
    if account not in l:
        data.append(l)

# 2 parse csv and load into memory
class Transaction:
    def __init__(self, txn_id, date, code, description, comment, account, credit, debit):
        self.txn_id = txn_id
        self.date = date
        self.description = description
        self.credit = credit
        self.debit = debit
        self.account = account
        self.comment = comment
        self.code = code
        self.keep_account = False

    def __str__(self):
        return f"{self.txn_id}, {self.date}, {self.description}, {self.credit}, {self.debit}, {self.account}, {self.comment}, {self.code}"


all_txns = []
for l in data[1:]:
    if len(l) == 0:
        continue
    cols = l.split(',')
    txn = Transaction(cols[0], cols[1], cols[4], cols[5], cols[6], cols[7], cols[10], cols[11])
    all_txns.append(txn)

# for t in all_txns:
#     print(t)

# 3 re-create without accounts
filename = '202305_ocbc_sid.csv' 
tmp_filename = 'tmp_' + filename
with open(tmp_filename,'w', newline='') as f:
    f.write("txn_id,date,description,credit,debit,account,comment,code\n")
    for txn in all_txns:
        f.write(f"{txn.txn_id},{txn.date},{txn.description},{txn.credit},{txn.debit},,{txn.comment},{txn.code}\n")


# [ ] 4 import csv with hledger and create new csv
output = subprocess.run(["hledger", "print", "-f", tmp_filename, "--rules-file", "ocbc.rules", "-O", "csv"], capture_output=True, text=True)

# [ ] 5 parse csv
lines = output.stdout.split('\n')
unknowns = []

# [ ] 6 filter out unknown txns
unknown_txns = []
for l in lines:
    if "unknown" in l:
        cols = l.split(",")
        txn = Transaction(cols[0], cols[1], cols[4], cols[5], cols[6], cols[7], cols[10], cols[11])
        unknown_txns.append(txn)


def txn_uniq_id(txn):
    return txn.date + txn.description + txn.credit + txn.debit

def find_txn_idx(txn, all_txns):
    uid = txn_uniq_id(txn)
    for idx, t in enumerate(all_txns):
        if uid == txn_uniq_id(t):
            return idx 
    return -1

# 7
for ut in unknown_txns:
    idx = find_txn_idx(ut, all_txns)
    if idx != -1:
        all_txns[idx].keep_account = True


with open(filename,'w', newline='') as f:
    for t in all_txns:
        if not t.keep_account:
            f.write(f"{t.txn_id},{t.date},{t.description},{t.credit},{t.debit},,{t.comment},{t.code}\n")
        else:
            f.write(f"{t.txn_id},{t.date},{t.description},{t.credit},{t.debit},{t.account},{t.comment},{t.code}\n")

# with open(filename,'w', newline='') as f:
#     for r in result:
#         print(r)
#         f.write(f"{r.txn_id},{r.date},{r.description},{r.credit},{r.debit},,{r.comment},{r.code}\n")
