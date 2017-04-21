#!/usr/bin/env python3.5

import SceneBuilderAPI as sbapi
from time import time

for object in sbapi.SceneData.objects:
    print(object)

print('+++++++++++++++++++++++++++++++++++++++++++++++++++++')

sbapi.removeStartingCube()

for object in sbapi.SceneData.objects:
    print(object)

print('+++++++++++++++++++++++++++++++++++++++++++++++++++++')


sbapi.loadModel('/home/wilson/PyScripts/models/ALCT1003.fbx', 'Something', position = (0.0, 0.0, 1.0), orientation = (0.0, 0.0, 0.0))
sbapi.loadModel('/home/wilson/PyScripts/models/AEON1080.fbx', 'Chair1', position = (0.0, 1.0, 0.0))
sbapi.loadModel('/home/wilson/PyScripts/models/AEON1080.fbx', 'Chair2', position = (0.0, -1.0, 0.0), orientation = (0.0, 0.0, -180.0))
sbapi.loadModel('/home/wilson/PyScripts/models/ANDO1280.fbx', 'Nightstand', position = (-1.0, 0.0, 0.0))



sbapi.renderImage('render-test-{}.png'.format(time()))

for object in sbapi.SceneData.objects:
    print(object)

#It appears this correction isn't necessary. If a black screen is rendered, try this first
#sbapi.correctLocalView()

#sbapi.configureCamera(50, position = [5.0, 0.0, 0.0], orientation = (0.0, 0.0, 0.0))

#sbapi.renderImage('camera0.png')

#sbapi.configureCamera(50, position = [5.0, 0.0, 0.0], orientation = (0.0, 0.0, 90.0))

#sbapi.renderImage('camera90.png')

#sbapi.configureCamera(50, position = [5.0, 0.0, 0.0], orientation = (0.0, 0.0, 180.0))

#sbapi.renderImage('camera180.png')

#sbapi.configureCamera(50, position = [5.0, 0.0, 0.0], orientation = (0.0, 0.0, 270.0))

#sbapi.renderImage('camera270.png')

