#!/usr/bin/env python3.5

#Must be run using python 3.5

#import numpy as np
import argparse
import bpy
import xml.etree.ElementTree as ET
import math
import mathutils

#References to global blender objects
SceneData = bpy.data
SceneContext = bpy.context
SceneCamera = SceneData.cameras['Camera']
SceneCameraObject = SceneData.objects['Camera']

#XML globals; for loading and rendering from an XML file
xmlHandle = None
xmlRoot = None
isXMLLoaded = False

#Array that holds all the objects that are supposed to be in the scene
registeredObjects = ['Camera', 'Lamp']

#Converts a vector of angles from degrees to radians
def deg2rad(orientation):
    radians = []
    for i in range(len(orientation)):
        radians.append(math.radians(orientation[i]))
    return radians

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
    for obj in SceneData.objects:
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
    SceneCameraObject.location = position
    SceneCameraObject.rotation_euler = deg2rad(orientation)

#Adjusts the SceneCamera based on supplied K and RT matrices
def configureCameraFromMatrix(K, RT):
    loc, rot = RTMatrixToVectors(RT)
    SceneCamera.lens = K[0][0]
    SceneCameraObject.location = loc
    SceneCameraObject.rotation_quaternion = rot

#Captures an image from the current camera and saves it to the specified path
def renderImage(outputPath):
    SceneContext.scene.render.filepath = outputPath
    bpy.ops.render.render( write_still = True)

#Configures the camera based on given matrices and renders an image
def renderImageFromMatrix(outputPath, KMatrix, RTMatrix):
    configureCameraFromMatrix(KMatrix, RTMatrix)
    renderImage(outputPath)

#Removes all objects from the scene if they exist
def removeObjects(objectNames):
    bpy.ops.object.select_all(action='DESELECT')
    for name in objectNames:
        if name in SceneData.objects:
            SceneData.objects[name].select = True
    bpy.ops.object.delete()

#Removes an object by name if it exists
def removeObject(objectName):
    removeObjects([objectName])

#Removes anything not added through this API
def purgeScene():
    removeTargets = []
    for object in SceneData.objects:
        if object.name not in registeredObjects:
            removeTargets.append(object.name)
    removeObjects(removeTargets)

#Loads a model from a file and gives it the specified name. Optionally accepts a vector for position
#DevNote: have name autofilled with regex; add orientation
def loadModel(path, name, position = (0.0, 0.0, 0.0), orientation = [0.0, 0.0, 0.0], autoPurge = True):
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
    lastObject.rotation_euler = deg2rad(orientation)

    registeredObjects.append(lastObject.name)

    #Cleans up any unwanted objects
    if autoPurge:
        purgeScene()

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

#Returns the location vector and a rotation Quaternion from an RT matrix
#The rotation component returned is a Quaternion
def RTMatrixToVectors(RT):
    mat = mathutils.Matrix() #Defaults to I4
    for k in range(3):
        for j in range(3):
            mat[k][j] = RT[k][j] #Copies the rotation matrix
        mat[k][3] = RT[k][3] #Copies the translation vector

    vectors = mat.decompose() #Vectors contains location, rotation(Quaternion), and scale

    return vectors[0], vectors[1] #Return location and rotation(Quaternion)

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-x', '--xml', action='store', default='')
    group.add_argument('-d', '--display', action='store', default='')
    parser.add_argument('-o', '--output', action='store', default='')

if __name__ == '__main__':
    main()
