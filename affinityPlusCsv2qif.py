#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from commonCsv2Qif import UnicodeReader, CreateOutFiles, WriteTransaction, WriteSplitTransaction

TOTAL_COLUMN = "Total"
DATE_COLUMN = "Date"
PAYEE_COLUMN = "Description"
ACCOUNT_COLUMN = "account"
ACCOUNT2_COLUMN = "account2"
ACCOUNT2_TOTAL_COLUMN = "account2 total"

CHECKING = "checking"

def Import(fileName):
    """
    Convert the fileName from CSV to QIF
    @param fileName the filename to import from
    """

    reader = UnicodeReader(open(fileName, 'r', encoding='utf-8-sig'))

    outFileDict = {
        CHECKING: {
            "accountName": "Affinity Plus FCU",
            "accountType": "Bank",
            "accountDescription": "Checking Account"
        }
    }

    outFileDict = CreateOutFiles(fileName, outFileDict)
    outFileHandle = outFileDict[CHECKING]['file']

    for row in reader:
        # First check what account type this is
        date = row.getStringValue(DATE_COLUMN)
        total = row.getFloatValue(TOTAL_COLUMN)
        payee = row.getStringValue(PAYEE_COLUMN)
        account = row.getStringValue(ACCOUNT_COLUMN)
        account2 = row.getStringValue(ACCOUNT2_COLUMN)
        account2Total = row.getFloatValue(ACCOUNT2_TOTAL_COLUMN)

        if account is None or len(account) == 0:
            raise Exception("Bad account for %s"%payee)

        if account2Total is None:
            WriteTransaction(outFileHandle, date, payee, account, total)
        else:
            WriteSplitTransaction(outFileHandle, date, payee, total, account2, account2Total, account)

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
    