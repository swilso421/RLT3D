#!/usr/bin/env python3

import SceneBuilderAPI as sbapi
import WayfairAPI as wapi
import json
import os
from math import sqrt

classId = 147
baseDir = '/nfs/sleipnir1/WayfairModelRenderings'
categoryDir = os.path.join(baseDir, str(classId))
os.makedirs(categoryDir, exist_ok=True)

dimensions = {}

for sku in wapi.databaseGetByClassID(classId):
    data = wapi.databaseGetBySKU(sku)
    
    imageDir = os.path.join(categoryDir, sku)
    os.makedirs(imageDir, exist_ok=True)
    
    sbapi.loadModel(data['path'], data['name'])
    
    #sbapi.useLighting(False)
    
    modelDimensions = sbapi.SceneData.objects[data['name']].dimensions
    
    dimensions[sku] = (modelDimensions.x, modelDimensions.y, modelDimensions.z)
    
    distance = 1.5 * sqrt(modelDimensions.x ** 2 + modelDimensions.y ** 2 + modelDimensions.z ** 2)
    
    sbapi.generateArcballCameraXML('temp.xml', distance, 25, 15, 0, 360, 30, 0, 90, (0.0, 0.0, modelDimensions.z / 3))
    
    sbapi.parseCameraXML('temp.xml', imageDir)
    
    sbapi.clearScene()
    
with open(os.path.join(categoryDir, 'dimensions.dat'), 'wt+') as handle: handle.write(json.dumps(dimensions))

perimeters = sorted([dimensions[x][0] + dimensions[x][1] + dimensions[x][2] for x in dimensions])

#pMean = sum(perimeters) / len([perimeters)
#pVar = sum([(x - pMean) ** 2 for x in perimeters]) / (len(perimeters) - 1)
#pStd = sqrt(pVar)
pMedian = perimeters[int(len(perimeters) / 2)]
pIQR = perimeters[int(3 * len(perimeters) / 4)] - perimeters[int(len(perimeters) / 4)]


with open(os.path.join(categoryDir, 'flagged.txt'), 'wt+') as handle:
    for sku in dimensions:
        volume = dimensions[sku][0] + dimensions[sku][1] + dimensions[sku][2]
        if volume < (pMedian - 1.5 * pIQR):
            handle.write('{}\n'.format(sku))
