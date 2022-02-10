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
    fileWithExt = os.path.split(origFile)[1]
    fileNoExt = os.path.splitext(fileWithExt)[0]

    for key in outfileDict:
        fileName = fileNoExt + ".%s.qif"%key
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

class UnknownZipException(Exception):
    """Raised when we have never seen this zip code before"""
    
    def __init__(self, zipCode, address, city):
        self.zip = zipCode
        self.address = "{0}, {1}, MN  {2}".format(address, city, zipCode)

def WriteTaxedByZipTransaction(outFile, date, payee, amount, zipCode, address="", city=""):
    taxCategoryDict = {
        '55005': 'State and Anoka Transit',
        '55014': 'State and Anoka Transit',
        '55016': 'State and Washington Transit',
        '55029': 'State',
        '55038': 'State and Washington Transit',
        '55040': 'State and Isanti Transit',
        '55044': 'State and Dakota Transit',
        '55051': 'State',
        '55057': 'State and Dakota Transit',
        '55057-3158': 'State and Rice County',
        '55068': 'State and Dakota Transit',
        '55072': 'State and Pine County',
        '55075': 'State and Dakota Transit',
        '55102': 'State, Ramsey, and St. Paul Transit',
        '55104': 'State, Ramsey, and St. Paul Transit',
        '55105': 'State, Ramsey, and St. Paul Transit',
        '55109': 'State and Ramsey Transit',
        '55110': 'State and Ramsey Transit',
        '55112': 'State and Ramsey Transit',
        '55113': 'State and Ramsey Transit',
        '55116': 'State, Ramsey, and St. Paul Transit',
        '55118': 'State and Dakota Transit',
        '55123': 'State and Dakota Transit',
        '55124': 'State and Dakota Transit',
        '55126': 'State and Ramsey Transit',
        '55128': 'State and Washington Transit',
        '55129': 'State and Washington Transit',
        '55303': 'State and Anoka Transit',
        '55304': 'State and Anoka Transit',
        '55304-7636': 'State and Anoka Transit',
        '55309': 'State and Sherburne County',
        '55330': 'State and Wright Transit',
        '55313': 'State and Wright Transit',
        '55318': 'State and Carver County',
        '55331': 'State, Hennepin Transit, and Hennepin',
        '55337': 'State and Dakota Transit',
        '55345': 'State, Hennepin Transit, and Hennepin',
        '55346': 'State, Hennepin Transit, and Hennepin',
        '55346-4134': 'State, Hennepin Transit, and Hennepin',
        '55352': 'State and Scott County',
        '55362': 'State and Wright Transit',
        '55369': 'State, Hennepin Transit, and Hennepin',
        '55371': 'State',
        '55376': 'State and Wright Transit',
        '55376-1064': 'State and Wright Transit',
        '55378': 'State and Scott County',
        '55379': 'State and Scott County',
        '55386': 'State and Carver County',
        '55398': 'State',
        '55407': 'State, Minneapolis, Hennepin Transit, and Hennepin',
        '55408': 'State, Minneapolis, Hennepin Transit, and Hennepin',
        '55413': 'State, Minneapolis, Hennepin Transit, and Hennepin',
        '55413-1939': 'State, Minneapolis, Hennepin Transit, and Hennepin',
        '55414': 'State, Minneapolis, Hennepin Transit, and Hennepin',
        '55417': 'State, Minneapolis, Hennepin Transit, and Hennepin',
        '55418': 'State, Minneapolis, Hennepin Transit, and Hennepin',
        '55418-1716': 'State, Hennepin Transit, and Hennepin',
        '55421': 'State and Ramsey Transit',
        '55428': 'State',
        '55429': 'State, Hennepin Transit, and Hennepin',
        '55432': 'State and Anoka Transit',
        '55434': 'State and Anoka Transit',
        '55438': 'State, Hennepin Transit, and Hennepin',
        '55441': 'State, Hennepin Transit, and Hennepin',
        '55442': 'State, Hennepin Transit, and Hennepin',
        '55443': 'State, Hennepin Transit, and Hennepin',
        '55444': 'State, Hennepin Transit, and Hennepin',
        '55445': 'State, Hennepin Transit, and Hennepin',
        '55446': 'State, Hennepin Transit, and Hennepin',
        '55448': 'State and Anoka Transit',
        '55449': 'State and Anoka Transit',
        '55614': 'State and Lake County',
        '55616': 'State and Lake County',
        '55735': 'State and Pine County',
        '55719': 'State and St. Louis County',
        '55812': 'State, St. Louis County, and Duluth',
        '55902': 'State and Olmsted County',
        '55912': 'State, Austin, and Mower County',
        '56071': 'State and Scott County',
        '56071-1226': 'State and Scott County',
        '56082': 'State and Nicollet County',
        '56308': 'State and Douglas County',
        '56373': 'State and Morrison County',
        '56401': 'State, Crow Wing County, and Brainerd',
        '56442': 'State and Crow Wing County',
        '56465': 'State and Crow Wing County',
        '56554': 'State and Becker County',
        '56560': 'State and Clay County',
        '55075-3306': 'State and Dakota Transit',
        '55303-2308': 'State and Anoka Transit',
        '55345-5734': 'State, Hennepin Transit, and Hennepin'
    }

    if zipCode not in taxCategoryDict:
        raise UnknownZipException(zipCode, address, city)
    
    categoryPrefix = 'Income:Sales:Taxable:'

    WriteTaxedTransaction(outFile, date, payee, "%s%s:Online"%(categoryPrefix, taxCategoryDict[zipCode]), amount, taxCategoryDict[zipCode])

def WriteTaxedTransaction(outFile, date, payee, category, amount, taxCategory):
    taxCategoryPrefix = "Income:Tax Collected:"
    taxDict = {
        "State": 0.06875,
        "State and Anoka Transit": 0.07125,
        "State and Becker County": 0.07375,
        "State and Carver County": 0.07375,
        "State and Clay County": 0.07375,
        "State and Crow Wing County": 0.07375,
        "State and Douglas County": 0.07375,
        "State and Dakota Transit": 0.07125,
        "State and Isanti Transit": 0.07375,
        "State and Lake County": 0.07375,
        "State and Morrison County": 0.07375,
        "State and Nicollet County": 0.07375,
        "State and Olmsted County": 0.07375,
        "State and Pine County": 0.07375,
        "State and Ramsey Transit": 0.07375,
        "State and Rice County": 0.07375,
        "State and Scott County": 0.07375,
        "State and Sherburne County": 0.07375,
        "State and St. Louis County": 0.07375,
        "State and Washington Transit": 0.07125,
        "State and Wright Transit": 0.07375,
        "State, Austin, and Mower County": 0.07875,
        "State, Crow Wing County, and Brainerd": 0.07875,
        "State, Hennepin Transit, and Hennepin": 0.07525,
        "State, Minneapolis, Hennepin Transit, and Hennepin": 0.08025,
        "State, Ramsey, and St. Paul Transit": 0.07875,
        "State, St. Louis County, and Duluth": 0.08875
    }

    if taxCategory not in taxDict:
        raise Exception("Bad Tax Category: %s"%taxCategory)

    WriteDatePayeeTotal(outFile, date, payee, amount)
    preTax = float(amount)/(1.0+taxDict[taxCategory])
    WriteSplit(outFile, category, preTax)
    WriteSplit(outFile, taxCategoryPrefix + taxCategory, amount - preTax)
    WriteEndTransaction(outFile)
