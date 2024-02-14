import os
from os.path import exists

import pickle

from pprint import pprint

from smartystreets_python_sdk import StaticCredentials, exceptions, Batch, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup
from dotenv import load_dotenv
from commonCsv2Qif import UnicodeReader

singletonClient = None
singletonZipMap = None
singletonAddressMap = None

dir_path = os.path.dirname(os.path.realpath(__file__))
addressMapFileName = os.path.join(dir_path,'.addressMap.cache.pkl')

def getClient():
    global singletonClient 
    if singletonClient == None:
        load_dotenv()
        credentials = StaticCredentials(os.environ['SMARTY_ID'], os.environ['SMARTY_TOKEN'])
        singletonClient = ClientBuilder(credentials).with_licenses(['us-core-cloud']).build_us_street_api_client()
    return singletonClient

def freeFormAddress(address, city, zipCode):
    return "{0}, {1}, MN  {2}".format(address, city, zipCode)

def getAddressMap():
    global singletonAddressMap, addressMapFileName
    if singletonAddressMap == None:
        if exists(addressMapFileName):
            print('Loading address cache from %s'%addressMapFileName)
            fh = open(addressMapFileName, "rb")
            singletonAddressMap = pickle.load(fh)
            fh.close()
        else:
            print('No address cache found')
            singletonAddressMap = {} 
    return singletonAddressMap
        
def saveAddressMap():
    global singletonAddressMap, addressMapFileName
    fh = open(addressMapFileName, "wb")
    pickle.dump(singletonAddressMap,fh)
    fh.close()

def updateZipCodes(addresses):
    # First convert addresses to dict
    addressMap = getAddressMap()
    addressesDict = {}
    addressesById = {}
    id = 0
    for address in addresses:            
        addressesDict[address] = { 'id': str(id) }
        addressesById[str(id)] = address
        if address in addressMap:
            addressesDict[address]['zip'] = addressMap[address]['zip']
            addressesDict[address]['zipInfo'] = addressMap[address]['zipInfo']
        id += 1
        
    client = getClient()

    i = 0
    batch = Batch()
    addressesByIndex = []
    for address in addressesDict.keys():
        # Skip addresses that are already in the cache
        if 'zipInfo' in addressesDict[address]: continue
        print('Adding address: {}'.format(address))
        batch.add(StreetLookup(address))
        batch[i].input_id = addressesDict[address]['id']
        batch[i].match = "invalid"
        addressesByIndex.append(address)
        print('Batch {}'.format(batch[i]))
        i += 1

    foundBadAddress = False

    if i > 0:
        try:
            print('Trying to send batch of %d address(es)'%i)
            client.send_batch(batch)
        except exceptions.SmartyException as err:
            print(err)
            raise err

        for i, lookup in enumerate(batch):
            candidates = lookup.result

            if len(candidates) == 0:
                print("Address {} is invalid.\n".format(addressesByIndex[i]))
                foundBadAddress = True
                continue

            candidate = candidates[0]
            address = addressesById[candidate.input_id]
            addressData = addressesDict[address]
            addressData['zip'] = "{}-{}".format(candidate.components.zipcode,candidate.components.plus4_code)
            addressData['zipInfo'] = getZipToTaxMapping("{}{}".format(candidate.components.zipcode,candidate.components.plus4_code))
            addressMap[address] = addressData
            saveAddressMap()
    else:
        print("All addresses were in the cache")

    if foundBadAddress: raise BadAddressesError
    return addressesDict

def getZipToTaxMapping(zipLookup):
    global singletonZipMap
    if singletonZipMap == None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reader = UnicodeReader(open(os.path.join(dir_path,'mnZipCodes.tsv'), 'r'), delimiter='\t')
        singletonZipMap = {}
        ## Let's get some indexes to make future code cleaner

        for row in reader:
            # First check what account type this is
            rate = row.getFloatValue('Rate')
            name = row.getStringValue('Name')
            zip = row.getStringValue('ZIP')
            singletonZipMap[zip] = { 'name': name, 'rate': rate/100}

    res = min(enumerate(singletonZipMap.keys()), key=lambda x: abs(int(zipLookup) - int(x[1])))

    return singletonZipMap[res[1]]

class BadAddressesError(Exception):
    """Raised when we have never seen this zip code before"""
