#!/usr/bin/env python3.5

import SceneBuilderAPI as sbapi
import WayfairAPI as wapi
from time import time

#sbapi.loadModel('/home/wilson/PyScripts/models/ALCT1003.fbx', 'Rug', position = (-1.0, 0.0, 0.0))
sbapi.loadModel('/home/wilson/PyScripts/models/AEON1080.fbx', 'Chair1', position = (-0.5, 0.0, 0.0))
sbapi.loadModel('/nfs/sleipnir1/WayfairModels/ALCT2653.fbx', 'Chair2', position = (0.5, 0.0, 0.0))
#sbapi.loadModel('/home/wilson/PyScripts/models/ANDO1280.fbx', 'Nightstand', position = (2.0, 0.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/CHLH1406.fbx', 'Bedframe', position = (-2.0, 0.0, 0.0))

#sbapi.renderImage('test.png')

sbapi.renderImageFromMatrix('test.png', [[50]], sbapi.composeRTMatrix((45, 0, 45), (3, -3, 3)))

#vec1 = (90.0, 0.0, 0.0)
#vec2 = (90.0, 0.0, 90.0)

#mat1 = sbapi.EulerVectorToRTMatrix(vec1)
#mat2 = sbapi.EulerVectorToRTMatrix(vec2)

#sbapi.renderImageFromMatrix('test1.png', [[50]], mat1)
#sbapi.renderImageFromMatrix('test2.png', [[50]], mat2)

#for theta in range(0, 360, 10):
#	vec = (90.0, 0.0, theta)
#	mat = sbapi.composeRTMatrix(vec, (2, 0, 0))
#	sbapi.renderImageFromMatrix('matrix{}.png'.format(theta), [[50]], mat)
