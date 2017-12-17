#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from commonCsv2Qif import UnicodeReader, CreateOutFiles, WriteTaxedTransaction, WriteTransaction

TOTAL_COLUMN = "Total Collected"
TAX_COLUMN = "Tax"
CREDIT_COLUMN = "Card"
TAX_CATEGORY_COLUMN = "Tax Category"
CATEGORY_COLUMN = "Category"
DATE_COLUMN = "Date"
PAYEE_COLUMN = "Payee"
FEE_COLUMN = "Fees"

CASH = 'cash'
SQUARE = 'square'
ACCOUNTS_RECEIVABLE = 'ar'

def Import(fileName):
    """
    Convert the fileName from CSV to QIF
    @param fileName the filename to import from
    """

    reader = UnicodeReader(open(fileName, 'r'))

    outFileDict = {
        CASH: {
            "accountName": "Cash Drawer",
            "accountType": "Cash",
            "accountDescription": "The cash drawer"
        },
        SQUARE: {
            "accountName": "Square Pending",
            "accountType": "Bank",
            "accountDescription": "Square account"
        }
    }

    outFileDict = CreateOutFiles(fileName, outFileDict)

    for row in reader:
        # First check what account type this is
        date = row.getStringValue(DATE_COLUMN)
        total = row.getFloatValue(TOTAL_COLUMN)
        tax = row.getFloatValue(TAX_COLUMN)
        credit = row.getFloatValue(CREDIT_COLUMN)
        category = row.getStringValue(CATEGORY_COLUMN)
        taxCategory = row.getStringValue(TAX_CATEGORY_COLUMN)
        payee = row.getStringValue(PAYEE_COLUMN)
        fee = row.getFloatValue(FEE_COLUMN)

        if tax > 0:
            if abs(credit) < 0.01:
                # If tax is > 0 and credit === 0, put this in the cash drawer
                WriteTaxedTransaction(outFileDict[CASH]['file'], date, payee, category, total, taxCategory)
            else:
                WriteTaxedTransaction(outFileDict[SQUARE]['file'], date, payee, category, total, taxCategory)
                WriteTransaction(outFileDict[SQUARE]['file'], date, 'square fee', 'Expenses:Bank Service Charge:Square', fee)
        else:
            WriteTransaction(outFileDict[SQUARE]['file'], date, payee, 'Assets:Accounts Receivable', total)
            WriteTransaction(outFileDict[SQUARE]['file'], date, 'square fee', 'Expenses:Bank Service Charge:Square', fee)

    for key in outFileDict:
        outFile = outFileDict[key]['file']
        outFile.flush()
        outFile.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: " + sys.argv[0] + " <input.csv>")
        sys.exit(1)

    FILE_NAME = sys.argv[1]
    if not os.path.isfile(FILE_NAME):
        print("Can not access file: " + FILE_NAME)
        sys.exit(1)

    Import(FILE_NAME)
    