#!/bin/env python
#-*- coding: utf-8 -*-

from commonCsv2Qif import WriteDatePayeeTotal, WriteSplit, WriteEndTransaction

def WriteTaxedByZipTransaction(outFile, date, payee, amount, taxCategory, taxRate):
    categoryPrefix = 'Income:Sales:Taxable:'

    WriteTaxedTransaction(outFile, date, payee, "%s%s:Online"%(categoryPrefix, taxCategory), amount, taxCategory, taxRate)

def WriteTaxedTransaction(outFile, date, payee, category, amount, taxCategory, taxRate):
    taxCategoryPrefix = "Income:Tax Collected:"

    WriteDatePayeeTotal(outFile, date, payee, amount)
    preTax = float(amount)/(1.0+taxRate)
    WriteSplit(outFile, category, preTax)
    WriteSplit(outFile, taxCategoryPrefix + taxCategory, amount - preTax)
    WriteEndTransaction(outFile)
