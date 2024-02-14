#!/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
import csv
import codecs
import datetime

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    http://docs.python.org/library/csv.html
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def __next__(self):
        return self.reader.next().encode("utf-8")

class Row:
    """
    A Row of data from the CSV, you can get values from the header names
    """
    def __init__(self, header, dataRow):
        self.dataRow = dataRow
        self.header = header

    def getRawValue(self, columnName):
        if columnName not in self.header:
            raise Exception('Could not find %s in headers (%s)'%(columnName, ', '.join(self.header.keys())))
        return self.header[columnName]

    def getFloatValue(self, columnName):
        """
        Expects a string value in the row, will convert to float and remove a dollar sign if present
        """
        colIndex = self.getRawValue(columnName)
        value = self.dataRow[colIndex]
        value = value.replace(',', '')
        if value is None or len(value) == 0:
            return None
        sign = 1.0
        if value[0] == '-':
            sign = -1.0
            value = value[1:]
        if value[0] == '$':
            value = float(value[1:])
        else:
            value = float(value)
        return sign * value

    def getStringValue(self, columnName):
        colIndex = self.getRawValue(columnName)
        return self.dataRow[colIndex]

    def getDateValue(self, columnName, dateFormat="%m/%d/%Y"):
        strValue = self.getStringValue(columnName)
        dateObject = datetime.datetime.strptime(strValue, dateFormat)
        return dateObject.strftime("%m/%d/%Y")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    http://docs.python.org/library/csv.html
    """

    def __init__(self, fileHandle, delimiter=','):
        self.reader = csv.reader(fileHandle, delimiter=delimiter)
        header = next(self.reader)
        self.header = dict()
        for i in range(0, len(header)):
            self.header[header[i]] = i

    def __next__(self):
        row = next(self.reader)
        return Row(self.header, row)

    def __iter__(self):
        return self

def CreateOutFiles(origFile, outfileDict):
    directory = os.path.dirname(origFile)
    fileWithExt = os.path.split(origFile)[1]
    fileNoExt = os.path.splitext(fileWithExt)[0]

    for key in outfileDict:
        fileName = os.path.join(directory,fileNoExt + ".%s.qif"%key)
        if os.path.exists(fileName):
            print("Target (%s) does already exist"%(fileName))
            sys.exit(1)

        theFile = codecs.open(fileName, 'w', 'utf-8')
        outfileDict[key]['file'] = theFile
        outfileDict[key]['fileName'] = fileName
        WriteHeader(theFile, outfileDict[key]['accountName'], outfileDict[key]['accountType'], outfileDict[key]['accountDescription'])
    return outfileDict

def ToAscii(text):
    return text
    # text = text.replace(u'Ã¤', 'ae')
    # text = text.replace(u'Ã¶', 'oe')
    # text = text.replace(u'Ã¼', 'ue')
    # text = text.replace(u'ÃŸ', 'ss')
    # text = text.replace(u'Ã„', 'AE')
    # text = text.replace(u'Ã–', 'OE')
    # text = text.replace(u'Ãœ', 'UE')
    # #simply "flatten" the rest...
    # return unicodedata.normalize('NFKD', text).encode('ascii','ignore')

def ToDollar(amount):
    return "%.2f"%(float(amount))

def WriteHeader(outFile, accountName, accountType, description):
    outFile.write('!Account\n')
    outFile.write('N%s\n'%accountName)
    outFile.write('T%s\n'%accountType)
    outFile.write('D%s\n'%description)
    outFile.write('^\n')
    outFile.write('!Type:%s\n'%accountType)

def WriteDatePayeeTotal(outFile, date, payee, amount):
    outFile.write('D' + date + '\n')
    outFile.write(u'P%s\n'%(payee))
    outFile.write('T' + ToDollar(amount) + '\n')

def WriteEndTransaction(outFile):
    outFile.write('^\n')

def WriteCategory(outFile, category):
    outFile.write('L' + ToAscii(category) + '\n')

def WriteSplit(outFile, category, amount):
    outFile.write('S' + ToAscii(category) + '\n')
    outFile.write('$' + ToDollar(amount) + '\n')

def WriteTransaction(outFile, date, payee, category, amount):
    WriteDatePayeeTotal(outFile, date, payee, amount)
    WriteCategory(outFile, category)
    WriteEndTransaction(outFile)

def WriteSplitTransaction(outFile, date, payee, total, category1, category1Amount, category2):
    WriteDatePayeeTotal(outFile, date, payee, total)
    WriteSplit(outFile, category1, category1Amount)
    WriteSplit(outFile, category2, total-category1Amount)
    WriteEndTransaction(outFile)

