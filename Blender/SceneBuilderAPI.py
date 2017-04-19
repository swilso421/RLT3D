#!/usr/bin/env python3.5
 
#Must be run using python 3.5
 
#import numpy as np
import bpy
import xml.etree.ElementTree as ET
 
#References to global blender objects
SceneData = bpy.data
SceneContext = bpy.context
SceneCamera = SceneData.cameras['Camera']

#XML globals; for loading and rendering from an XML file
xmlHandle = None
xmlRoot = None
isXMLLoaded = False
 
#Identifies the type of 3D model
def getFileType(filepath):
    if filepath.endswith('.3ds'):
        return 1
    elif filepath.endswith('.fbx'):
        return 2
    elif filepath.endswith('.obj'):
        return 3
    else:
        return 0
    
#Returns the object last added to the scene
#DevNote: make usage safe
def getLastLoadedObject():
    for obj in SceneData:
        if obj.select:
            return obj
    return None
 
#Loads a specified xml file
#DevNote: current system is not ideal, consider an OO approach
def loadXML(filepath):
    xmlHandle = ET.parse(filepath)
    xmlRoot = xmlHandle.getroot()
    isXMLLoaded = True
    
#Adjusts the SceneCamera via the given parameters. Focal length is in mm
def configureCamera(focalLength, position = (0.0, 0.0, 0.0), orientation = (0.0, 0.0, 0.0)):
    SceneCamera.lens = focalLength
    #Location and orientation are currently ignored. Will be changed soon
    #SceneCamera.location = position
    #SceneCamera.rotation = orientation
    
#Captures an image from the current camera and saves it to the specified path
def renderImage(outputPath):
    SceneContext.scene.render.filepath = outputPath
    bpy.ops.render.render( write_still = True)
    
#Loads a model from a file and gives it the specified name. Optionally accepts a vector for position
#DevNote: have name autofilled with regex; add orientation
def loadModel(path, name, position = (0.0, 0.0, 0.0)):
    fileType = getFileType(path)
     
    #Loads the 3D model with the correct function
    if fileType == 1:
        bpy.ops.import_scene.autodesk_3ds(filepath = path)
    elif fileType == 2:
        bpy.ops.import_scene.fbx(filepath = path)
    elif fileType == 3:
        bpy.ops.import_scene.obj(filepath = path)
    else:
        print('File "{f}" is not a recognized file type'.format(f = path))
        return
    
    lastObject = getLastLoadedObject()

    #Updates name and position of loaded model
    lastObject.name = name
    lastObject.location = position
    
    return lastObject

#Loads all models from the 'object' tag of the loaded XML document
def loadModelsFromXML():
    if not isXMLLoaded:
        print("Warning! No XML file has been loaded! Please make a call to loadXML() first!")
        return

    for obj in xmlRoot.iter('object'):
        name = obj.get('name')
        path = obj.get('path')
        x = float(obj.find('x').text)
        y = float(obj.find('y').text)
        z = float(obj.find('z').text)

        loadModel(path, name, (x, y, z))

#Renders images from the 'camera' tags of the loaded XML document
def renderImagesFromXML():
    if not isXMLLoaded:
        print("Warning! No XML file has been loaded! Please make a call to loadXML() first!")
        return

    outPath = xmlRoot.find('output_destination').get('directory')

    for camView in xmlRoot.iter('camera'):
        name = camView.get('name')
        focalLength = float(camView.text)

        configureCamera(focalLength)

        renderImage(outPath + '/{}.png'.format(name))

#Resets all views to a global view; supposedly fixes black screen issues
def correctLocalView():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces[0]
            if space.local_view: #check if using local view
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region} #override context
                        bpy.ops.view3d.localview(override) #switch to global view
                        
def main():
    print('SceneBuilderAPI')
    
if __name__ == '__main__':
    main()
