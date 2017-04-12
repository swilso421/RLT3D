#!/usr/bin/env python3.5

import requests
from tqdm import tqdm

BASE_URL = "https://www.wayfair.com/v/api/three_d_model/"
MODEL_ENDPOINT = "models?"
PRODUCT_ENDPOINT = "product_information?"
SKU_TAG = "sku={}"
CLASS_TAG = "class_id={}"
PAGE_TAG = "page={}"
ALL_PAGES_TAG = "page=-1"
TAG_COMBINE = "&"

HEADERS = {
    'Accept': "*/*",
    'Accept-Encoding': "gzip, deflate",
    'Authorization': "Basic dHVnNTk0MTRAdGVtcGxlLmVkdTo1OGRkMTA2MzJmNGE3",
    'Cache-Control': "no-cache",
    'Connection': "close",
    'Host': "www.wayfair.com",
    'User-Agent': "Mozilla/5.0"
    }

def getJSON(url):
    return requests.get(url, headers = HEADERS).json()

def fetchModel(sku, directory):
    return None

def downloadAllModels():

    url = BASE_URL + MODEL_ENDPOINT + ALL_PAGES_TAG

    print('Requesting model URLs...')

    response = requests.get(url, headers = HEADERS)

    print('Converting response to JSON...')

    try:

        data = response.json()

    except:

        print('Could not convert respone to JSON!')
        print(response)
        print(response.content)
        return

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

        response = requests.get(modelURLs[model], headers = HEADERS, stream = True)

        if response.status_code == 200:
            with open('/home/wilson/PyScripts/models/{}.fbx'.format(model), 'w+') as handle:
                for bytes in tqdm(response.iter_content()):
                    handle.write(bytes)

def main():
    downloadAllModels()

if __name__ == '__main__':
    main()
