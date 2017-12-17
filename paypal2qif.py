#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from commonCsv2Qif import UnicodeReader, CreateOutFiles, WriteTaxedTransaction, WriteTransaction

TOTAL_COLUMN = "Order Total Amount (- Refund)"
TAX_CATEGORY_COLUMN = "Tax Category"
ZIP_COLUMN = "Postcode (Shipping)"
STATE_COLUMN = "State Code (Shipping)"
DATE_COLUMN = "Order Date"
PAYEE_COLUMN = "Full Name (Shipping)"
FEE_COLUMN = "Fee"

PAYPAL = 'paypal'

def Import(fileName):
    """
    Process the file
    """

    #reader = UnicodeReader(.open(file, 'rb'), csv.excel, 'cp1252', delimiter=',')
    reader = UnicodeReader(open(fileName, 'r'))

    outFileDict = {
        PAYPAL: {
            "accountName": "Paypal Pending",
            "accountType": "Bank",
            "accountDescription": "The pending paypal transactions"
        }
    }

    outFileDict = CreateOutFiles(fileName, outFileDict)
    outFileHandle = outFileDict[PAYPAL]['file']

    ## Let's get some indexes to make future code cleaner

    for row in reader:
        # First check what account type this is
        date = row.getDateValue(DATE_COLUMN, "%Y-%m-%d %H:%M")
        total = row.getFloatValue(TOTAL_COLUMN)
        state = row.getStringValue(STATE_COLUMN)
        zipCode = row.getStringValue(ZIP_COLUMN)
        taxCategory = row.getStringValue(TAX_CATEGORY_COLUMN)
        payee = row.getStringValue(PAYEE_COLUMN)
        fee = row.getFloatValue(FEE_COLUMN)

        if state == "MN":
            # This must be taxed
            categoryPrefix = 'Income:Sales:Taxable:Online:'
            WriteTaxedTransaction(outFileHandle, date, payee, categoryPrefix + zipCode, total, taxCategory)
        else:
            outOfStatePrefix = 'Income:Sales:Online-OutOfState:'
            WriteTransaction(outFileHandle, date, payee, outOfStatePrefix + state, total)
        WriteTransaction(outFileHandle, date, 'paypal fee', 'Expenses:Bank Service Charge:PayPal', fee * -1.0)

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
    