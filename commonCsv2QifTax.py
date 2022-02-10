#!/bin/env python
#-*- coding: utf-8 -*-

from commonCsv2Qif import WriteDatePayeeTotal, WriteSplit, WriteEndTransaction

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
