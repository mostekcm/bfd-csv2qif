import json
import salesTaxInfo

def run():
    mydict = salesTaxInfo.updateZipCodes([
        '1234 notarealaddress st, St. Paul, MN  55110',
        '12084 Waconia Cir NE, Blaine, MN  55449',
        '1332 9th Ave So, So St. Paul, MN  55076'
    ])

    print(json.dumps(mydict, indent=4, sort_keys=True))

if __name__ == "__main__":
    run()