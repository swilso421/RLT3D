#!/usr/bin/env python

import pygame

from OpenGLTools.GLRendering import SimpleSceneRenderer
from OpenGLTools.Basic3DShapes import *

#Opens the file generated by GenerateTestCoordinates.py
test_data = open("Preprocessing/test_data.txt", "r")

#Creates objects for the scene. The grid is for scale and the box is our moving object
grid = Grid(width = 10, length = 10, color = (0.0, 1.0, 0.0))
box = Cube(sideLength = 0.5)

#Reads a line from the file and returns the coordinates in a tuple
def parseCoords():
    line = test_data.readline()
    nums = line.split(":")
    return (float(nums[0]), 0.5, float(nums[1]))

#Called each frame by the scene
def eventLoop():
    for event in pygame.event.get():
        #Handles the user closing the window
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    #Reads a set of coordinates from the test data and updates the box's position
    coords = parseCoords()
    box.setPosition(coords)

#Initializes the renderer object. The parameter sent is the method to be called each frame
scene = SimpleSceneRenderer(eventLoop)

#Adds objects to the scene
scene.addSceneItem(grid)
scene.addSceneItem(box)

#Start rendering the scene
scene.start()
