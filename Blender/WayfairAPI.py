#!/usr/bin/env python3

import requests
import json
import os.path
import sqlite3
import operator
import textutils

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

#Loads JSON from a file
def loadJSON(filepath):
    if os.path.isfile(filepath):
        with open(filepath, 'r') as handle:
            response = handle.read()
        return True, json.loads(response)
    else:
        return False, None

#Stores data as JSON in a file
def storeAsJSON(data, filepath):
    with open(filepath, 'w+') as handle:
        handle.write(json.dumps(data))

#Given a query, returns a list of candidate classes which may be the desired class.
#Candidate list is sorted by estimated likelihood
#DevNote: first attempt, pretty big time complexity. Look into optimizations or alternative fuzzy matching
def fuzzyClassMatch(query):
    #Breaks the query into constituent words and counts the number of words
    queryWords = textutils.splitWords(query)
    queryWordCount = len(queryWords)

    #Retrieves all of the class IDs and names from the database
    cursor.execute('''SELECT * From Classes''')
    classTable = cursor.fetchall()

    #Selects class names that contain any word of the query
    candidates = []
    for row in classTable:
        #candidates.append({'ClassID': row[0], 'ClassName': row[1]})
        for qword in queryWords:
            if qword in row[1]:
                candidates.append({'ClassID': row[0], 'ClassName': row[1]})
                break

    #Calculates the WeightedDistance for each candidate class name
    for candidate in candidates:
        #Breaks the candidate into words
        candidateWords = textutils.splitWords(candidate['ClassName'])

        #If the number of words in the candidate is less than the number of words in the query,
        #it probably isn't the category we're looking for. The WeightedDistance is set arbitrarily high
        #and we continue to the next iteration
        if len(candidateWords) < queryWordCount:
            candidate['WeightedDistance'] = 10000
            continue

        #Calculates the overall Levenshtein distance between the full class name and full query
        LDPhrase = textutils.Levenshtein(query, candidate['ClassName'])

        #Calculates the Levenshtein distances between each word in the candidate and query.
        #This is useful because it gives a better estimate of whether or not the candidate contains subwords from the query
        LDWord = 0
        for qword in queryWords:
            smallest = 10000
            for cword in candidateWords:
                distance = textutils.Levenshtein(cword, qword)
                if distance < smallest:
                    smallest = distance
            LDWord += smallest

        #Creates a weighted estimate of the similarity between the query and candidate
        #This helps balance out the
        candidate['WeightedDistance'] = 0.2 * LDPhrase + 0.8 * LDWord

    #Sorts the candidates so that the smallest weighte distances are at the front of the list
    candidates.sort(key = operator.itemgetter('WeightedDistance'))

    return candidates

#Determines if the database contains the target SKU
def databaseContains(sku):
    cursor.execute('''SELECT * FROM Models WHERE SKU = ?''', (sku,))
    if len(cursor.fetchall()) == 0:
        return False
    else:
        return True

#Sets the path field of the specified sku in the database
def databaseSetPath(sku, path):
    path = os.path.abspath(path)
    if databaseContains(sku):
        cursor.execute('''UPDATE Models SET Path = ? WHERE SKU = ?''', (path, sku))
    else:
        cursor.execute('''INSERT INTO Models(SKU, Path) VALUES(?, ?)''', (sku, path))
    database.commit()

#Sets the classID and productName fields of the specified sku in the database
def databaseSetInfo(sku, classID, productName):
    if databaseContains(sku):
        cursor.execute('''UPDATE Models SET ClassID = ?, ProductName = ? WHERE SKU = ?''', (classID, productName, sku))
    else:
        cursor.execute('''INSERT INTO Models(SKU, ClassID, ProductName) VALUES(?, ?, ?)''', (sku, classID, productName))
    database.commit()

#Retrieves info for a specified SKU
def databaseGetBySKU(sku):
    info = {}
    cursor.execute('''SELECT * FROM Models WHERE SKU = ?''', (sku,))
    data = cursor.fetchall()
    if not len(data) == 0:
        data = data[0]
        info['sku'] = data[0]
        info['name'] = data[1]
        info['ClassID'] = data[2]
        info['path'] = data[3]
    return info

#Returns a list of SKU's that belong to the specified class
def databaseGetByClassID(classID):
    cursor.execute('''SELECT SKU FROM Models WHERE ClassID = ?''', (classID,))
    return [item for sublist in cursor.fetchall() for item in sublist]

#This sets all of the paths in table Models to null. Useful when switching machines
def databasePurgePaths():
    cursor.execute('''UPDATE Models SET Path = ?''', (None,))
    database.commit()

#Returns a path to a model that hopefully matches the specified label
def getPathToModelByType(label):
    matches = fuzzyClassMatch(label)

    for match in matches:
        skus = databaseGetByClassID(match['ClassID'])
        if len(skus) > 0:
            for sku in skus:
                entry = databaseGetBySKU(sku)
                if not entry['path'] == None:
                    return entry['path']

    return None

#Downloads a specific model from a url. Technically, this is just a generic
#download function and could download any file type
#Also, this will overwrite any file with the same filepath
def downloadModelFromURL(filepath, url, stream = False):

    #Get a response object from the target URL
    response = requests.get(url, stream = stream)

    #Writes the downloaded file to disk
    if response.status_code == 200:
        with open(filepath, 'wb+') as handle:
            for data in response.iter_content():
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

    #Adds the path into the database
    databaseSetPath(sku, filepath)

    #Returns the result of the download; i.e. whether or not it was downloaded
    return downloadModelFromURL(filepath, data[sku]['fbx'])

#Downloads ALL fbx model files from the Wayfair database. This operation will take SEVERAL HOURS to do
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

    #Clear these variables since we will reuse them
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

        #Adds the path into the database
        databaseSetPath(model, filepath)

#Downloads product information from the WayfairAPI and saves it to the database
def downloadProductInformation(start = 0, count = 100000):
    #While loop counter
    currentPage = start

    #There is too much product info to fetch via the all pages tag
    #Instead, pages are polled individually. Not efficient, looking for workaround
    while (currentPage < count):
        #URL to fetch some product info
        url = BASE_URL + PRODUCT_ENDPOINT + PAGE_TAG.format(currentPage)

        print('Requesting product info...')

        #Fetch the product info
        response = requests.get(url, headers=HEADERS)

        print('Converting product info...')

        #Convert http response to JSON data
        successful, data = getJSON(response)

        #If the script was flagged as a bot
        if not successful:
            print('bad response')
            print('last successful page read was {}'.format(currentPage - 1))
            break
        elif data == 'No products found':
            print("last page")
            break

        print('Saving product info...')

        #Parse the wanted fields from the product info and load into infoDictionary
        for item in data:
            # newEntry = {}
            # newEntry['class_id'] = item['class_id']
            # newEntry['name'] = item['product_name']
            # infoDictionary[item['sku']] = newEntry
            databaseSetInfo(item['sku'], item['class_id'], item['product_name'])

        #Increment counter
        currentPage += 1

#If this API is run directly, it downloads all of the models
#Just here during testing
def main():
    initialize()
    downloadAllModels('/nfs/sleipnir1/WayfairModels')

#This is run if this API is loaded as a module
def initialize():
    global database
    global cursor
    database = sqlite3.connect('database')
    cursor = database.cursor()

if __name__ == '__main__':
    main()
elif __name__ == 'WayfairAPI':
    initialize()
