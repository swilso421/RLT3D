#!/usr/bin/env python3

import WayfairAPI as wapi
import json
import os
import numpy as np
import cv2

classId = 349
baseDir = '/nfs/sleipnir1/WayfairModelRenderings'
categoryDir = os.path.join(baseDir, str(classId))

maskFilter = np.array([64,64,64], dtype = np.uint8)

skuPercents = {}
skuRatios = {}

for sku in wapi.databaseGetByClassID(classId):
    imageDir = os.path.join(categoryDir, sku)
    
    imagePercents = []
    imageRatios = []
    
    print('=============================================================')
    
    for elev in range(0, 90, 30):
        for orb in range(0, 360, 15):
            path = os.path.join(imageDir, 'elev:{};orb:{};.png'.format(elev, orb))
            
            print('*********************************')
            
            image = cv2.imread(path)
            
            mask = cv2.inRange(image, maskFilter, maskFilter)
            
            hist, _ = np.histogram(mask, bins=2)
            
            imagePercents.append(hist[1] / 518400)
            imageRatios.append(hist[0] / hist[1])
            
    skuPercents[sku] = imagePercents
    skuRatios[sku] = imageRatios
    
with open('data/percantage-analysis-{}.json'.format(classId), 'wt+') as f: f.write(json.dumps(skuPercents))

with open('data/ratio-analysis-{}.json'.format(classId), 'wt+') as f: f.write(json.dumps(skuRatios))
