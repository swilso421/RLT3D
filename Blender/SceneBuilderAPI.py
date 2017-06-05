#!/usr/bin/env python3.5

#Must be run using python 3.5

#import numpy as np
import argparse
import bpy
import bpy_types
import xml.etree.ElementTree as ET
from math import radians, sin, cos
import mathutils
import WayfairAPI as wapi
import os
import json

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

#Map of object names to their default rotation offsets
positionOffsets = {}
rotationOffsets = {}

#Converts a vector of angles from degrees to radians
def deg2rad(orientation):
    r = []
    for angle in orientation:
        r.append(radians(angle))
    return r

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

#Adjusts the SceneCamera via the given parameters. Focal length is in mm
def configureCamera(focalLength, position = (0.0, 0.0, 0.0), orientation = (0.0, 0.0, 0.0), inDegrees = True):
    if inDegrees:
        orientation = deg2rad(orientation)
    SceneCamera.lens = focalLength
    SceneCameraObject.location = mathutils.Vector(position)
    SceneCameraObject.rotation_euler = orientation

#Adjusts the SceneCamera based on supplied K and R matrices, and a T vector
def configureCameraFromMatrix(K, RT):
    loc, rot = decomposeRTMatrix(RT)
    SceneCamera.lens = K[0][0]
    SceneCameraObject.location = loc
    SceneCameraObject.rotation_euler = rot.to_euler()

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
        if name in SceneData.objects and not (name == 'Camera' or name == 'Lamp'):
            SceneData.objects[name].select = True
            try:
                registeredObjects.remove(name)
            except:
                continue
    bpy.ops.object.delete()

#Removes an object by name if it exists
def removeObject(objectName):
    removeObjects((objectName,))

#Removes anything not added through this API
def purgeScene():
    removeTargets = []
    for object in SceneData.objects:
        if object.name not in registeredObjects:
            removeTargets.append(object.name)
    removeObjects(removeTargets)

#Restores the scene to its initial state
def clearScene():
    removeTargets = registeredObjects.copy()
    removeTargets.remove('Camera')
    removeTargets.remove('Lamp')
    removeObjects(removeTargets)

#Loads a model from a file and gives it the specified name. Optionally accepts a vector for position
#DevNote: have name autofilled with regex; add orientation
def loadModel(path, name, position = (0.0, 0.0, 0.0), orientation = [0.0, 0.0, 0.0], inDegrees = True, autoPurge = True):
    fileType = getFileType(path)

    #Loads the 3D model with the correct function
    if fileType == 1:
        bpy.ops.import_scene.autodesk_3ds(filepath = path)
    elif fileType == 2:
        bpy.ops.import_scene.fbx(filepath = path, use_manual_orientation = False)
    elif fileType == 3:
        bpy.ops.import_scene.obj(filepath = path)
    else:
        print('File "{f}" is not a recognized file type'.format(f = path))
        return

    lastObject = getLastLoadedObject()

    #Updates name and position of loaded model
    lastObject.name = name

    positionOffsets[name] = lastObject.location

    lastObject.location += mathutils.Vector(position)

    rotationOffsets[name] = lastObject.rotation_euler.copy()

    if inDegrees:
        orientation = deg2rad(orientation)

    lastObject.rotation_euler.x += orientation[0]
    lastObject.rotation_euler.y += orientation[1]
    lastObject.rotation_euler.z += orientation[2]

    registeredObjects.append(lastObject.name)

    #Cleans up any unwanted objects
    if autoPurge:
        purgeScene()

    return lastObject

#Converts
def QuaternionVectorToRotationMatrix(quaternion = (0.0, 0.0, 0.0, 0.0)):
    return mathutils.Quaternion(quaternion).to_matrix()

#Converts a rotation matrix to a quaternion
def RotationMatrixToQuaternion(matrix):
    return matrix.to_quaternion()

#Converts a rotation matrix to an euler vector
def RotationMatrixToEuler(matrix):
    return matrix.to_euler()

#Converts a vector of (euler) angles into a rotation matrix
def VectorToRotationMatrix(orientation = (0.0, 0.0, 0.0), inDegrees = True):
    if len(orientation) == 3:
        if inDegrees:
            orientation = deg2rad(orientation)
        return mathutils.Euler(orientation, 'XYZ').to_matrix()
    elif len(orientation) == 4:
        return mathutils.Quaternion(orientation).to_matrix()

#Returns the location vector and a rotation Quaternion from an RT matrix
#The rotation component returned is a Quaternion
def decomposeRTMatrix(RT):
    location, quaternion, _ = RT.decompose()
    return location, quaternion

#Converts a list or numpy matrix into a Blender matrix
def formatRTMatrix(matrix):
    mat = mathutils.Matrix()
    for k in range(3):
        for j in range(3):
            mat[k][j] = matrix[k][j]
        mat[k][3] = matrix[k][3]
    return mat

#Creates a Blender matrix object representing an RT matrix out of a position and orientation vector
def composeRTMatrix(rotation = (0.0, 0.0, 0.0), translation = (0.0, 0.0, 0.0), inDegrees = True):
    rot = VectorToRotationMatrix(rotation, inDegrees)

    mat = mathutils.Matrix()
    for k in range(3):
        for j in range(3):
            mat[k][j] = rot[k][j]
        mat[k][3] = translation[k]

    return mat

#Manipulates a preexisting object
def manipulateObject(sceneObject, position = None, orientation = None):
    if type(sceneObject) == str:
        name = sceneObject
        if name in SceneData.objects and name in registeredObjects:
            sceneObject = SceneData.objects[name]
        else:
            return False
    elif type(sceneObject) == bpy_types.Object:
        name = sceneObject.name
        if not (name in SceneData.objects and name in registeredObjects):
            return False

    if position is None:
        pass
    elif type(position) == tuple:
        position = mathutils.Vector(position)
        sceneObject.location = positionOffsets[name] + position
    elif type(position) == Vector:
        sceneObject.location = positionOffsets[name] + position

    if not orientation is None:
        sceneObject.rotation_euler = deg2rad(orientation)

    return True

#Loads models from an xml file into the scene
def parseSceneXML(filepath):
    xmlHandle = ET.parse(filepath)
    xmlRoot = xmlHandle.getroot()

    for obj in xmlRoot.iter('object'):
        name = obj.get('name')

        position = (float(obj.find('xpos').text), float(obj.find('ypos').text), float(obj.find('zpos').text))
        orientation = (float(obj.find('xrot').text), float(obj.find('yrot').text), float(obj.find('zrot').text))

        inDegrees = False if obj.get('unit') == 'rad' else True

        path = wapi.getPathToModelByType(obj.get('type'))

        if not path is None:
            loadModel(path, name, position, orientation, inDegrees)

#Renders camera views of the scene from an xml file
def parseCameraXML(filepath, directory = ''):
    xmlHandle = ET.parse(filepath)
    xmlRoot = xmlHandle.getroot()

    #Race condition here
    if not os.path.isdir(directory):
        os.makedirs(directory)

    for view in xmlRoot.iter('view'):
        name = view.get('name')

        focal = float(view.get('focal'))

        rotType = view.get('type')

        if rotType == 'matrix':
            rawMat = [[float(view.find('r1c1').text), float(view.find('r1c2').text), float(view.find('r1c3').text), float(view.find('r1c4').text)],
                      [float(view.find('r2c1').text), float(view.find('r2c2').text), float(view.find('r2c3').text), float(view.find('r2c4').text)],
                      [float(view.find('r3c1').text), float(view.find('r3c2').text), float(view.find('r3c3').text), float(view.find('r3c4').text)]]
            rotMat = formatRTMatrix(rawMat)
        elif rotType == 'euler':
            rotVec = (float(view.find('xrot').text), float(view.find('yrot').text), float(view.find('zrot').text))
            posVec = (float(view.find('xpos').text), float(view.find('ypos').text), float(view.find('zpos').text))
            inDegrees = False if view.find('unit').text == 'rad' else True
            rotMat = composeRTMatrix(rotVec, posVec, inDegrees)
        elif rotType == 'quaternion':
            rotVec = (float(view.find('wrot').text), float(view.find('xrot').text), float(view.find('yrot').text), float(view.find('zrot').text))
            posVec = (float(view.find('xpos').text), float(view.find('ypos').text), float(view.find('zpos').text))
            rotMat = composeRTMatrix(rotVec, posVec)

        renderImageFromMatrix(os.path.join(directory, '{}.png'.format(name)), [[focal]], rotMat)

#Loads models from a json file into the scene
def parseSceneJSON(filepath):
    scene = {}
    with open(filepath, 'r') as f:
        scene = json.loads(f.read())

    for name in scene:
        path = wapi.getPathToModelByType(scene[name]['type'])

        if not path is None:
            loadModel(path, name, scene[name]['pos'], scene[name]['rot'], scene[name]['deg'])

#Renders camera views of the scene from a json file
def parseCameraJSON(filepath, directory = ''):
    cameras = {}
    with open(filepath, 'r') as f:
        cameras = json.loads(f.read())

    if not os.path.isdir(directory):
        os.makedirs(directory)

    for name in cameras:
        rotType = cameras[name]['type']
        if rotType == 'matrix':
            rotMat = formatRTMatrix(cameras[name]['matrix'])
        elif rotType == 'euler':
            rotMat = composeRTMatrix(cameras[name]['rot'], cameras[name]['pos'], cameras[name]['deg'])
        elif rotType == 'quaternion':
            rotMat = composeRTMatrix(cameras[name]['rot'], cameras[name]['pos'])

        renderImageFromMatrix(os.path.join(directory, '{}.png'.format(name)), [[cameras[name]['focal']]], rotMat)

#Converts an xml scene layout into a json scene layout
def convertSceneXMLToJSON(filepath):
    xmlHandle = ET.parse(filepath)
    xmlRoot = xmlHandle.getroot()

    newPath = filepath.replace('.xml', '.json')

    scene = {}

    for obj in xmlRoot.iter('object'):
        name = obj.get('name')

        scene[name] = {}

        scene[name]['pos'] = (float(obj.find('xpos').text), float(obj.find('ypos').text), float(obj.find('zpos').text))
        scene[name]['rot'] = (float(obj.find('xrot').text), float(obj.find('yrot').text), float(obj.find('zrot').text))
        scene[name]['type'] = obj.get('type')
        scene[name]['deg'] = False if obj.get('unit') == 'rad' else True

    with open(newPath, 'w+') as f:
        f.write(json.dumps(scene))

#Converts xml camera data into json camera data
def convertCameraXMLToJSON(filepath):
    xmlHandle = ET.parse(filepath)
    xmlRoot = xmlHandle.getroot()

    newPath = filepath.replace('.xml', '.json')

    cameras = {}

    for view in xmlRoot.iter('view'):
        name = view.get('name')

        cameras[name] = {}

        rotType = view.get('type')

        cameras[name]['focal'] = float(view.get('focal'))
        cameras[name]['type'] = view.get('type')

        if rotType == 'matrix':
            cameras[name]['matrix'] = [[float(view.find('r1c1').text), float(view.find('r1c2').text), float(view.find('r1c3').text), float(view.find('r1c4').text)],
                                       [float(view.find('r2c1').text), float(view.find('r2c2').text), float(view.find('r2c3').text), float(view.find('r2c4').text)],
                                       [float(view.find('r3c1').text), float(view.find('r3c2').text), float(view.find('r3c3').text), float(view.find('r3c4').text)]]
        elif rotType == 'euler':
            cameras[name]['rot'] = (float(view.find('xrot').text), float(view.find('yrot').text), float(view.find('zrot').text))
            cameras[name]['pos'] = (float(view.find('xpos').text), float(view.find('ypos').text), float(view.find('zpos').text))
            cameras[name]['deg'] = False if view.find('unit').text == 'rad' else True
        elif rotType == 'quaternion':
            cameras[name]['rot'] = (float(view.find('wrot').text), float(view.find('xrot').text), float(view.find('yrot').text), float(view.find('zrot').text))
            cameras[name]['pos'] = (float(view.find('xpos').text), float(view.find('ypos').text), float(view.find('zpos').text))

    with open(newPath, 'w+') as f:
        f.write(json.dumps(cameras))

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-x', '--xml', action='store', default='')
    group.add_argument('-j', '--json', action='store', default='')
    parser.add_argument('-d', '--output_directory', action='store', default='')

if __name__ == '__main__':
    main()
