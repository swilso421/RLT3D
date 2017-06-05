#!/usr/bin/env python3.5

#Only one import necessary
import SceneBuilderAPI as sbapi

#Each model requires just one line to load and position itself. This is a task well suited for iteration
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/DEID1400.fbx', 'U1', (-3.0, 3.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/BRSD1939.fbx', 'U2', (-1.5, 3.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/LUNN1125.fbx', 'U3', (0.0, 3.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/ZPS1156.fbx', 'U4', (1.5, 3.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/TADN1734.fbx', 'U5', (3.0, 3.0, 0.0))

#sbapi.loadModel('/home/wilson/PyScripts/models/ALCT1003.fbx', 'Rug', position = (-3.0, 0.0, 0.0))
#sbapi.loadModel('/home/wilson/PyScripts/models/AEON1080.fbx', 'Chair1', position = (-1.5, 0.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/ALCT2653.fbx', 'Chair2', position = (0.0, 0.0, 0.0))
#sbapi.loadModel('/home/wilson/PyScripts/models/ANDO1280.fbx', 'Nightstand', position = (1.5, 0.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/CHLH1406.fbx', 'Bedframe', position = (3.0, 0.0, 0.0))

#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/ANDO4120.fbx', 'U6', (-3.0, -3.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/BUNR1209.fbx', 'U7', (-1.5, -3.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/HOHN7411.fbx', 'U8', (0.0, -3.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/OAWY1517.fbx', 'U9', (1.5, -3.0, 0.0))
#sbapi.loadModel('/nfs/sleipnir1/WayfairModels/VKGL1444.fbx', 'U10', (3.0, -3.0, 0.0))

sbapi.convertSceneXMLToJSON('sample_scene_layout.xml')
sbapi.convertCameraXMLToJSON('sample_camera_views.xml')

sbapi.parseSceneJSON('sample_scene_layout.json')

sbapi.parseCameraJSON('sample_camera_views.json', 'images')
#Renders images from the default camera position and orientaion
sbapi.renderImage('iso.png')

#Demonstration of rendering images from K and RT matrices. Here the RT matrices were generated from Euler vectors for my own readability
#sbapi.renderImageFromMatrix('z.png', [[50]], sbapi.composeRTMatrix((0, 0, 0), (0, 0, 25)))
#sbapi.renderImageFromMatrix('x.png', [[50]], sbapi.composeRTMatrix((90, 0, 90), (25, 0, 0)))
#sbapi.renderImageFromMatrix('y.png', [[50]], sbapi.composeRTMatrix((90, 0, 0), (0, -25, 0)))
