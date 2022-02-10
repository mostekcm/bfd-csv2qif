#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from commonCsv2Qif import UnicodeReader, CreateOutFiles, WriteTransaction

TOTAL_COLUMN = "amount"
DATE_COLUMN = "date"
PAYEE_COLUMN = "payee"
SHOW_COLUMN = "show"

ACCOUNTS_RECIEVABLE = "ar"

def Import(fileName):
    """
    Convert the fileName from CSV to QIF
    @param fileName the filename to import from
    """

    reader = UnicodeReader(open(fileName, 'r', encoding='utf-8-sig'))

    outFileDict = {
        ACCOUNTS_RECIEVABLE: {
            "accountName": "Accounts Receivable",
            "accountType": "Bank",
            "accountDescription": "Pending Payments"
        }
    }

    outFileDict = CreateOutFiles(fileName, outFileDict)
    outFileHandle = outFileDict[ACCOUNTS_RECIEVABLE]['file']

    for row in reader:
        # First check what account type this is
        date = row.getStringValue(DATE_COLUMN)
        total = row.getFloatValue(TOTAL_COLUMN)
        show = row.getStringValue(SHOW_COLUMN)
        payee = row.getStringValue(PAYEE_COLUMN)

        if (abs(total) > 0.01):
            WriteTransaction(outFileHandle, date, payee, show, total)
        else:
            print("Skipping payee (%s) for total (%f) on date (%s)"%(payee, total, date))

    outFileHandle.flush()
    outFileHandle.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: " + sys.argv[0] + " <input.csv>")
        sys.exit(1)

    FILE_NAME = sys.argv[1]
    if not os.path.isfile(FILE_NAME):
        print("Can not access file: " + FILE_NAME)
        sys.exit(1)

    Import(FILE_NAME)
    