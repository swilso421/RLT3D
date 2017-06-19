#!/usr/bin/env python3

import argparse
import cv2
from darkflow.net.build import TFNet
import json
import numpy as np
import os
import re
import tensorflow as tf
import threading
from time import time

#Threaded image loading class
class ImageLoader(threading.Thread):
    def __init__(self, ID, imageDict, paths, first = 0, last = None):
        threading.Thread.__init__(self)

        self.ID = ID
        self.dict = imageDict
        self.paths = paths
        self.first = first
        self.last = last if last is not None else len(self.paths)

    def run(self):
        for i in range(self.first, self.last):
            self.dict[self.paths[i]] = cv2.imread(self.paths[i])
            print('Thread-{} loaded image {}'.format(self.ID, self.paths[i]))

#Threaded image prediction class
class ThreadedPredictor(threading.Thread):
    def __init__(self, ID, predictions, imageDict, paths, first = 0, last = None):
        threading.Thread.__init__(self)

        self.ID = ID
        self.predictions = predictions
        self.dict = imageDict
        self.paths = paths
        self.first = first
        self.last = last if last is not None else len(self.paths)

    def run(self):
        for i in range(self.first, self.last):
            self.predictions[self.paths[i]] = predict(self.dict[self.paths[i]])

#For converting numpy types when JSON encoding
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)

#Generator function to create n subarrays
def nsub(array, n):
    if n > len(array) or n < 1:
        print('{}:{}'.format(len(array), n))
        raise ValueError
    start = 0
    for i in range(n):
        stop = start + len(array[i::n])
        yield (start, stop)
        start = stop

#Formats a given path into a clean, absolute path
def cleanPath(path):
    return os.path.abspath(os.path.expanduser(os.path.normpath(path)))

#Cleans a list of paths
def cleanPaths(paths):
    for i in range(len(paths)):
        paths[i] = cleanPath(paths[i])

#Generates a color by hashing the input
def colorHash(var):
    h = lambda x, y: abs(hash(x)) % y
    return (h(var, 254), h(var, 255), h(var, 256))

#Returns filepaths to all .jpg and .png images in directory
def findImages(directory, clean = True):
    pathList = []
    for path in os.listdir(directory):
        if path.endswith('.jpg') or path.endswith('.png'):
            pathList.append(os.path.join(directory, path))
    if clean:
        cleanPaths(pathList)
    return pathList

#Returns an indicator as to what type of target the path is
def getTargetType(path):
    if os.path.isdir(path):
        return 'dir'
    elif os.path.isfile(path):
        if path.endswith('.txt'):
            return 'txt'
        elif path.endswith('.jpg') or path.endswith('.png'):
            return 'img'
        else:
            return 'unknown'
    else:
        return 'err'

#Loads an image from a filepath
def loadImage(path):
    return cv2.imread(cleanPath(path))

#Loads images from a list of filepaths. Returns a dictionary of the images with paths as keys
def loadImages(paths):
    images = {}
    for path in paths:
        try:
            images[path] = cv2.imread(path)
            print('Loaded image at {}'.format(path))
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print('Failed to load image at {}; skipping'.format(path))
            continue
    return images

#Formats prediction data into human readable format
def textOutputFormatter(path, predictions):
    lines = ['ImagePath: {}\n'.format(path)]
    for match in predictions:
        lines.append('Label: {}\n'.format(match['label']))
        lines.append('Confidence: {}\n'.format(match['confidence']))
        lines.append('X: {}\n'.format(match['topleft']['x']))
        lines.append('Y: {}\n'.format(match['topleft']['y']))
        lines.append('W: {}\n'.format(match['bottomright']['x'] - match['topleft']['x']))
        lines.append('H: {}\n'.format(match['bottomright']['y'] - match['topleft']['y']))
    lines.append('\n')
    return ''.join(lines)

#Overlays an image with bounding boxes and labels of its predictions
def drawPredictions(path, image, predictions):
    for match in predictions:
        topleft = (match['topleft']['x'], match['topleft']['y'])
        bottomright = (match['bottomright']['x'], match['bottomright']['y'])
        color = colorHash(match['label'])
        cv2.rectangle(image, topleft, bottomright, color, 3)
        cv2.putText(image, '{}: {:.2f}'.format(match['label'], match['confidence']), topleft, cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

#Sets the global tfnet with the specified parameters
def buildNet(model = 'cfg/yolo.cfg', weights = 'weights/yolo.weights', threshold = 0.25, gpu = '/gpu:0'):
    global tfnet
    
    gpuMatch = re.match('/gpu:\d+', gpu)
    
    if gpuMatch:
        os.environ['CUDA_VISIBLE_DEVICES'] = gpuMatch.group()[5:]
        options = {'model': model, 'load': weights, 'threshold': threshold, 'verbalise': False, 'gpu': 0.95, 'gpuName': gpuMatch.group()}
    else:
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        options = {'model': model, 'load': weights, 'threshold': threshold, 'verbalise': False, 'gpu': -1.0, 'gpuName': gpu}
        
    tfnet = TFNet(options)

#Makes predictions for the image using the global tfnet
def predict(image):
    global tfnet
    predictions = tfnet.return_predict(image)
    print('Found {} objects'.format(len(predictions)))
    return predictions

def batchPredict(imageDict):
    predictions = {}
    for path in imageDict:
        predictions[path] = predict(imageDict[path])
    return predictions

#Initializes the global tfnet in gpu mode when this is imported as a module
def init():
    buildNet(gpu = '/gpu:0')

#The command line interface
def main():

    #Create parser
    parser = argparse.ArgumentParser()

    #Positional arguments
    parser.add_argument('target', action='store', nargs='+', help='The target(s) to be processed. Can be any combination of paths to images, directories, or .txt files containing paths / directories. At least one of these is required')

    #Optional arguments
    parser.add_argument('-m', '--model', action='store', default='cfg/yolo.cfg', help='Path to the model configuration file')
    parser.add_argument('-w', '--weights', action='store', default='weights/yolo.weights', help='Path to the trained weight file')
    parser.add_argument('-t', '--threshold', action='store', default=0.25, help='Detection threshold; will only list matches of at least this confidence')
    parser.add_argument('-o', '--text_output', action='store', default='predictions.txt', help='Text file to write prediction data')
    parser.add_argument('-j', '--json', action='store', default='predictions.json', help='JSON file to write prediction data')
    parser.add_argument('-b', '--draw_boxes', action='store_true', help='Create image copies with bounding boxes overlayed')
    parser.add_argument('-d', '--dir', action='store', default='prediction-boxes', help='Directory to store images with drawn boxes')
    parser.add_argument('-e', '--predict_multithreaded', action='store_true', help='!EXPERIMENTAL! Enables multithreaded processing of image predictions')
    parser.add_argument('-z', '--threads', action='store', default='1', help='Number of threads to run jobs with')
    parser.add_argument('-g', '--gpu', action='store', default='/gpu:0', help='Selects a gpu to use. Should be in Tensorflow format: /gpu:#')

    args = parser.parse_args()

    paths = []
    cleanPaths(args.target)
    for item in args.target:
        targetType = getTargetType(item)
        if targetType == 'txt':
            with open(item, 'r') as f:
                for line in f:
                    args.target.append(cleanPath(line.rstrip()))
        elif targetType == 'img':
            if not item in paths: paths.append(item)
        elif targetType == 'dir':
            for path in findImages(item):
                if not path in paths: paths.append(path)

    if not os.path.isfile(args.model):
        print('ATTENTION: Model file {} does not exist or is not cfg file! Defaulting to cfg/yolo.cfg'.format(args.model))
        args.model = 'cfg/yolo.cfg'

    if not os.path.isfile(args.weights):
        print('ATTENTION: Weights file {} does not exist or is not weights file! Defaulting to weight/yolo.weights'.format(args.weights))
        args.weights = 'weights/yolo.weights'

    args.threshold = float(args.threshold)
    if args.threshold <= 0.0 or args.threshold >= 1.0:
        print('ATTENTION: Threshold value {} outside of range (0.0, 1.0)! Setting threshold to 0.25'.format(args.threshold))
        args.threshold = 0.25

    print('\n=====Building Network=====\n')

    buildNet(args.model, args.weights, args.threshold, args.gpu)

    print('\n=====Loading Images=====\n')
    timeStart = time()

    args.threads = len(paths) if int(args.threads) > len(paths) else int(args.threads)
    args.threads = 1 if args.threads < 1 else args.threads

    imageDict = {}
    loadThreads = []

    count = 1
    for start, stop in nsub(paths, args.threads):
        thread = ImageLoader(count, imageDict, paths, start, stop)
        loadThreads.append(thread)
        count += 1

    for thread in loadThreads: thread.start()

    for thread in loadThreads: thread.join()

    print('Loaded images in {} seconds'.format(time() - timeStart))
    print('\n=====Beginning Batch Predictions=====\n')
    timeStart = time()

    if args.predict_multithreaded:
        predictions = {}
        predictThreads = []

        count = 1
        for start, stop in nsub(paths, args.threads):
            thread = ThreadedPredictor(count, predictions, imageDict, paths, start, stop)
            predictThreads.append(thread)
            count += 1

        for thread in predictThreads: thread.start()

        for thread in predictThreads: thread.join()

    else:
        predictions = batchPredict(imageDict)

    print('Processed all images in {:.4f} seconds'.format(time() - timeStart))
    print('\n=====Saving Results=====\n')

    print('Writing JSON to {}...'.format(args.json))
    with open(args.json, 'w+') as f:
        f.write(json.dumps(predictions, cls=NumpyEncoder))

    print('Writing text to {}...'.format(args.text_output))
    with open(args.text_output, 'w+') as f:
        for path in predictions:
            f.write(textOutputFormatter(path, predictions[path]))

    if args.draw_boxes:
        print('\n=====Drawing Bounding Boxes=====\n')

        args.dir = cleanPath(args.dir)
        os.makedirs(args.dir, exist_ok=True)

        for path in predictions:
            drawPredictions(path, imageDict[path], predictions[path])
            newPath = os.path.join(args.dir, os.path.basename(path))
            print('Saving {}'.format(newPath))
            cv2.imwrite(newPath, imageDict[path])

#Standard boilerplate starts the command line interface if run directly and initializes the global tfnet if imported
if __name__ == '__main__':
    main()
else:
    init()
