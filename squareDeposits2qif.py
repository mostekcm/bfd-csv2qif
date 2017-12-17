#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from commonCsv2Qif import UnicodeReader, CreateOutFiles, WriteTransaction

TOTAL_COLUMN = "Deposited"
DATE_COLUMN = "Payment Date"
PAYEE = "Beauty Full Day LLC"

SQUARE = 'square'

def Import(fileName):
    """
    Convert the fileName from CSV to QIF
    @param fileName the filename to import from
    """

    reader = UnicodeReader(open(fileName, 'r'))

    outFileDict = {
        SQUARE: {
            "accountName": "Square Pending",
            "accountType": "Bank",
            "accountDescription": "Square account"
        }
    }

    outFileDict = CreateOutFiles(fileName, outFileDict)
    outFileHandle = outFileDict[SQUARE]['file']

    for row in reader:
        # First check what account type this is
        date = row.getStringValue(DATE_COLUMN)
        total = row.getFloatValue(TOTAL_COLUMN)

        WriteTransaction(outFileHandle, date, PAYEE, 'Assets:Current Assets:Checking Account', -1.0 * total)

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
    