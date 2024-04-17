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
import os
import sys
import argparse
import csv

parser = argparse.ArgumentParser(description='process journals')
parser.add_argument('--date', '-d', type=str, help='date')
parser.add_argument('--account', '-a', help='account', type=str)
args = parser.parse_args()

if args.account is None or args.date is None:
    print(parser.print_help())
    sys.exit(1)

account = args.account
date = args.date

account_name = account.split(":")[2]
base_filename = date.replace("/", "") + "_" + account_name
journal_filename = date.replace("/", "") + "_" + account_name + ".journal"
csvfile_dirname = '~/workspace/accounts/csv_regen/cleaned/'
csvfile = base_filename + '.csv'
csv_filename = os.path.join(csvfile_dirname, csvfile) 
rules_file = os.path.join("rules", account_name + ".rules")

print("Processing: ", journal_filename)

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
    reader = csv.reader(lines[1:])
    txns = []
    for row in reader:
        if row is None or len(row) == 0:
            continue
        txn = Transaction(row)
        txns.append(txn)
    return lines[0], txns

# 1 journal to csv
# 2 parse csv and load into memory
header, all_txns = txns_from_csv(["hledger", "print", account,  "-p", date, "-O", "csv"])
filtered_txns = [t for t in all_txns if account not in t.account]

# 3 re-create csv without accounts
tmp_csv_filename = os.path.join('tmp_csvfiles', csvfile)
with open(tmp_csv_filename,'w', newline='') as f:
    f.write("date,description,credit,debit,account,comment,code\n")
    for txn in filtered_txns:
        f.write(f"{txn.date},\"{txn.description}\",{txn.credit},{txn.debit},,{txn.comment},{txn.code}\n")


# [ ] 4 import csv with hledger and create new csv
# [ ] 5 parse csv
_, txns = txns_from_csv(["hledger", "print", "-f", tmp_csv_filename, "--rules-file", rules_file, "-O", "csv"])

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

# balance
is_credit_card = False
if "liabilities" in account:
    is_credit_card = True

if not is_credit_card:
    balance_cmd = ["hledger", "balance", account, "-p", date, "-H", "-O", "csv"]
    balance_csv = subprocess.run(balance_cmd, capture_output=True, text=True)
    balance_lines = balance_csv.stdout.split('\n')
    balance_str = balance_lines[1].split(",")[1]
    balance = balance_str.replace("SGD$", "")

with open(csv_filename,'w', newline='') as f:
    f.write("date,description,credit,debit,account,comment,code\n")
    for idx, t in enumerate(filtered_txns):
        if not t.keep_account:
            f.write(f"{t.date},\"{t.description}\",{t.credit},{t.debit},,{t.comment},{t.code}")
        else:
            f.write(f"{t.date},\"{t.description}\",{t.credit},{t.debit},{t.account},{t.comment},{t.code}")

        if not is_credit_card and idx == len(filtered_txns) - 1:
            f.write(f",{balance}")

        f.write("\n")

# error checking

new_journal_cmd = subprocess.run(["hledger", "print", "-f", csv_filename, "--rules-file", rules_file], capture_output=True, text=True)
new_journal = new_journal_cmd.stdout

journal_filepath = os.path.join("../../accounts/journals", journal_filename)
with open(journal_filepath, "r") as f:
    original_journal = f.read()
    if new_journal != original_journal:
        print("\njournal not equal")

        new_journal_file = os.path.join("journals", journal_filename)
        with open(new_journal_file, "w") as f2:
            f2.write(new_journal)
            print("wrote new journal to: ", new_journal_file)
            print("vimdiff ", journal_filepath, new_journal_file)

_, original_txns = txns_from_csv(["hledger", "print", account,  "-p", date, "-O", "csv"])
_, new_txns = txns_from_csv(["hledger", "print", "-f", csv_filename, "--rules-file", rules_file, "-O", "csv"])

if len(original_txns) != len(new_txns):
    print("\nunequal no. of txns")
    print(len(original_txns), len(new_txns))
    sys.exit(1)

for idx, t in enumerate(original_txns):
    if t != new_txns[idx]:
        print("\nunequal txn idx: ", idx)
        print("original:", t)
        print("new: ", new_txns[idx])

print("completed")
