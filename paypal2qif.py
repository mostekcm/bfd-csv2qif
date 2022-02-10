#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from commonCsv2Qif import UnicodeReader, CreateOutFiles, UnknownZipException, WriteTaxedByZipTransaction, WriteTransaction

TOTAL_COLUMN = "Order Total Amount (- Refund)"
ZIP_COLUMN = "Postcode (Shipping)"
ADDRESS_COLUMN = "Address 1&amp;2 (Shipping)"
CITY_COLUMN = "City (Shipping)"
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

    badZips = {}
    for row in reader:
        # First check what account type this is
        date = row.getDateValue(DATE_COLUMN, "%Y-%m-%d %H:%M")
        total = row.getFloatValue(TOTAL_COLUMN)
        state = row.getStringValue(STATE_COLUMN)
        zipCode = row.getStringValue(ZIP_COLUMN)
        payee = row.getStringValue(PAYEE_COLUMN)
        fee = row.getFloatValue(FEE_COLUMN)
        address = row.getStringValue(ADDRESS_COLUMN)
        city = row.getStringValue(CITY_COLUMN)

        if total > 0:
            if state == "MN":
                # This must be taxed
                try:
                    WriteTaxedByZipTransaction(outFileHandle, date, payee, total, zipCode, address, city)
                except UnknownZipException as err:
                    print('{0}, {1}'.format(err.zip, err.address))
                    badFile = True
                    if err.zip not in badZips:
                        badZips[err.zip] = []
                    badZips[err.zip].append(err.address)
            else:
                outOfStatePrefix = 'Income:Sales:Online-OutOfState:'
                WriteTransaction(outFileHandle, date, payee, outOfStatePrefix + state, total)
            WriteTransaction(outFileHandle, date, 'paypal fee', 'Expenses:Bank Service Charge:PayPal', fee * -1.0)
        else:
            print('skipping $%f transaction for %s'%(total,payee))
    
    outFileHandle.flush()
    outFileHandle.close()
    if len(badZips.keys()) > 0:
        print('Failing due to zip errors:')
        for zip in badZips.keys():
            print('{0}:'.format(zip))
            for address in badZips[zip]:
                print('      {0}'.format(address))

        os.remove(outFileDict[PAYPAL]['fileName'])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: " + sys.argv[0] + " <input.csv>")
        sys.exit(1)

    FILE_NAME = sys.argv[1]
    if not os.path.isfile(FILE_NAME):
        print("Can not access file: " + FILE_NAME)
        sys.exit(1)

    Import(FILE_NAME)
    