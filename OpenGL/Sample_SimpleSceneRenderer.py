#!/usr/bin/env python

import pygame
from pygame.locals import *

from GLRendering import SimpleSceneRenderer

from Basic3DShapes import *

#eventLoop will be called each frame as the eventHandlerCallback from SimpleSceneRender
#This allows it to be used for things like translating/rotating items or processing user input
def eventLoop():
    #This code is just an example which allows us to move the camera with the arrow keys
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                glTranslatef(0, -1, 0)
            if event.key == pygame.K_DOWN:
                glTranslatef(0, 1, 0)
            if event.key == pygame.K_RIGHT:
                glTranslatef(-1, 0, -1)
            if event.key == pygame.K_LEFT:
                glTranslatef(1, 0, 1)

#Initializes the renderer object. The parameter we sent is the method we want to be called each frame
scene = SimpleSceneRenderer(eventLoop)

#Creates a couple objects from the Basic3DShapes library. These are so we have something to look at in the scene
basePlane = Grid(width = 10, length = 10, color = (0.0, 1.0, 0.0))
box = Cube(coords = (0.0, 0.5, 0.0))

#Adds the objects we created to the scene
scene.addSceneItem(basePlane)
scene.addSceneItem(box)

#Finally, we start the scene
scene.start()
