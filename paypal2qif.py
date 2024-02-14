#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
from commonCsv2Qif import UnicodeReader, CreateOutFiles, WriteTransaction
from commonCsv2QifTax import WriteTaxedByZipTransaction
from salesTaxInfo import freeFormAddress, updateZipCodes, BadAddressesError

TOTAL_COLUMN = "Order Total Amount (- Refund)"
ZIP_COLUMN = "Postcode (Shipping)"
ADDRESS_COLUMN = "Address 1&2 (Shipping)"
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

    addresses = []
    rows = []
    badZips = {}
    for row in reader:
        # First check what account type this is

        row = {
            'date': row.getDateValue(DATE_COLUMN, "%Y-%m-%d %H:%M"),
            'total': row.getFloatValue(TOTAL_COLUMN),
            'state': row.getStringValue(STATE_COLUMN),
            'zipCode': row.getStringValue(ZIP_COLUMN),
            'payee': row.getStringValue(PAYEE_COLUMN),
            'fee': row.getFloatValue(FEE_COLUMN),
            'address': row.getStringValue(ADDRESS_COLUMN),
            'city': row.getStringValue(CITY_COLUMN),
        }

        if row['state'] == 'MN':
            row['mnFullAddress'] = freeFormAddress(row['address'], row['city'], row['zipCode'])
        
        if row['total'] > 0:
            rows.append(row)
        else:
            print('skipping $%f transaction for %s'%(row['total'],row['payee']))

    addresses = []
    for row in rows:
        if 'mnFullAddress' in row:
            addresses.append(row['mnFullAddress'])

    try:
        addressesDict = updateZipCodes(addresses)

        for row in rows:
            state = row['state']
            date = row['date']
            payee = row['payee']
            total = row['total']
            fee = row['fee']
            if state == "MN":
                zipInfo = addressesDict[row['mnFullAddress']]['zipInfo']
                # This must be taxed
                WriteTaxedByZipTransaction(outFileHandle, date, payee, total, zipInfo['name'], zipInfo['rate'])
            else:
                outOfStatePrefix = 'Income:Sales:Online-OutOfState:'
                WriteTransaction(outFileHandle, date, payee, outOfStatePrefix + state, total)
            WriteTransaction(outFileHandle, date, 'paypal fee', 'Expenses:Bank Service Charge:PayPal', fee * -1.0)

    except BadAddressesError:
        print('Failed to generate file because we had bad addresses, please fix those first')
        os.remove(outFileDict[PAYPAL]['fileName'])

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
    