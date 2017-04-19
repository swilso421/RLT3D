#!/usr/bin/env python3

import requests
import os.path
from tqdm import tqdm

#Global variables for various components of the api
BASE_URL = "https://www.wayfair.com/v/api/three_d_model/"
MODEL_ENDPOINT = "models?"
PRODUCT_ENDPOINT = "product_information?"
SKU_TAG = "sku={}"
CLASS_TAG = "class_id={}"
PAGE_TAG = "page={}"
ALL_PAGES_TAG = "page=-1"
TAG_COMBINE = "&"
BAUTH = ('tug59414@temple.edu', '58dd10632f4a7')

#Standard header group that (usually) allows access to the API
HEADERS = {
    'Accept': "*/*",
    'Accept-Encoding': "gzip, deflate",
    'Authorization': "Basic dHVnNTk0MTRAdGVtcGxlLmVkdTo1OGRkMTA2MzJmNGE3",
    'Cache-Control': "no-cache",
    'Connection': "close",
    'Host': "www.wayfair.com",
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }

#Attempts to get a JSON object out of the response
#If the request was flagged as a bot this will fail, and this function will return a boolean indicating this
def getJSON(response):
    try:
        data = response.json()
        return True, data
    except:
        return False, None


#OUTDATED: Requires rewrite to utilize fetchModel()
#Downloads ALL fbx model files from the Wayfair database. This operation will take a couple HOURS to do
def downloadAllModels():

    url = BASE_URL + MODEL_ENDPOINT + ALL_PAGES_TAG

    print('Requesting model URLs...')

    response = requests.get(url, headers = HEADERS)

    print('Converting response to JSON...')

    successful, data = getJSON(response)

    if not successful:
        return False, 'bad response'

    modelURLs = {}

    print('Parsing model URLs...')

    for entry in data:
        if 'fbx' in data[entry]:
            modelURLs[entry] = data[entry]['fbx']

    del response, data

    modelCount = len(modelURLs)
    modelNumber = 1

    count = 0

    print('Downloading models...')

    for model in modelURLs:
        print('Downloading model {current} of {total}...'.format(current = modelNumber, total = modelCount))
        modelNumber += 1

        response = requests.get(modelURLs[model])

        if response.status_code == 200:
            with open('/home/wilson/PyScripts/models/{}.fbx'.format(model), 'wb+') as handle:
                for data in tqdm(response.iter_content()):
                    handle.write(data)

#If this API is run directly, it downloads all of the models
#Just here during testing
def main():
    downloadAllModels()

if __name__ == '__main__':
    main()
