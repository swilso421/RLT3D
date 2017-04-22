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

#Downloads a specific model from a url. Technically, this is just a generic
#download function and could download any file type
#Also, this will overwrite any file with the same filepath
def downloadModelFromURL(filepath, url, stream = False):

    #Get a response object from the target URL
    response = requests.get(url, stream = stream)

    #Writes the downloaded file to disk
    if response.status_code == 200:
        with open(filepath, 'wb+') as handle:
            for data in tqdm(response.iter_content()):
                handle.write(data)
        return True
    else:
        return False

#Downloads the fbx file associated with the given SKU if it exists
#File will be downloaded to the given directory path with the filename being the SKU given
#DevNote: not currently finished, want to finish testing current download method
def fetchModel(sku, directory):

    #Prepare the appropriate url
    url = BASE_URL + MODEL_ENDPOINT + SKU_TAG.format(sku)

    #Prepare the filepath that will be used later
    filepath = os.path.join(directory, '{}.fbx'.format(sku))

    #Gets all the download urls for the target model
    response = requests.get(url, headers = HEADERS)

    #Attempts to read the models + urls table. If successful = false; the script
    #was probably flagged as a bot
    successful, data = getJSON(response)

    if not successful:
        return False, 'bad response'

    #If the model doesn't have an fbx download, return false
    if not 'fbx' in data[sku]:
        return False, 'Model {} does not have an fbx download'.format(sku)

    #Returns the result of the download; i.e. whether or not it was downloaded
    return downloadModelFromURL(filepath, data[sku]['fbx'])

#OUTDATED: Requires rewrite to utilize fetchModel()
#Downloads ALL fbx model files from the Wayfair database. This operation will take a couple HOURS to do
def downloadAllModels(directory):

    #Concatenates the appropriate url
    url = BASE_URL + MODEL_ENDPOINT + ALL_PAGES_TAG

    print('Requesting model URLs...')

    #Gets the list of all models by sku and all of their downloads
    response = requests.get(url, headers = HEADERS)

    print('Converting response to JSON...')

    #Attempts to read the models + urls table. If successful = false; the script
    #was probably flagged as a bot
    successful, data = getJSON(response)

    if not successful:
        return False, 'bad response'

    #Instantiates a dictionary for the download urls
    modelURLs = {}

    print('Parsing model URLs...')

    #Out of all the models found, we only care about models with fbx files.
    #This grabs only the fbx urls into our dictionary
    for entry in data:
        if 'fbx' in data[entry]:
            modelURLs[entry] = data[entry]['fbx']

    #Clear these variables since we wil reuse them
    del response, data

    modelCount = len(modelURLs)

    print('Downloading models...')

    for model in modelURLs:

        #Concatenates the appropriate filepath for the model to be downloaded
        filepath = os.path.join(directory, '{}.fbx'.format(model))

        #If the model isn't already downloaded, download it
        if not os.path.isfile(filepath):
            print('Downloading model {sku} to {path}'.format(sku = model, path = filepath))
            downloadModelFromURL(filepath, modelURLs[model])
        else:
            print('File {path} already exists; skipping'.format(path = filepath))

#If this API is run directly, it downloads all of the models
#Just here during testing
def main():
    downloadAllModels(/home/wilson/PyScripts/models)

if __name__ == '__main__':
    main()
