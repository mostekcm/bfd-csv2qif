#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from commonCsv2Qif import UnicodeReader, CreateOutFiles, WriteTransaction

TOTAL_COLUMN = "To Num."
DATE_COLUMN = "Date"
PAYEE_COLUMN = "Description"
PAYMENT = "payment"
SALE = "sale"

ACCOUNTS_RECIEVABLE = "ar"

def Import(fileName):
    """
    Convert the fileName from CSV to QIF
    @param fileName the filename to import from
    """

    reader = UnicodeReader(open(fileName, 'r', encoding='utf-8-sig'))

    outFileHandle = open(fileName+'.txt', 'w')

    results = {}

    for row in reader:
        # First check what account type this is
        date = row.getStringValue(DATE_COLUMN)
        total = row.getFloatValue(TOTAL_COLUMN)
        payee = row.getStringValue(PAYEE_COLUMN)

        if date != '':
            if total < 0:
                # this is a payment
                transType = PAYMENT
                total = -1.0 * total
            else:
                transType = SALE
            if total not in results:
                results[total] = {
                    PAYMENT: [], SALE: []
                }
            results[total][transType].append({'date': date, 'payee': payee})

    for total in results.keys():
        if len(results[total][PAYMENT]) != len(results[total][SALE]):
            outFileHandle.write("%f: Payments(%s) Sales(%s)\n"%(total,results[total][PAYMENT], results[total][SALE]))

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
    