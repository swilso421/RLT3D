#!/usr/bin/env python

import pygame
from pygame.locals import *

#from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
#from OpenGL.GLUT import *

class SimpleSceneRenderer:

    #Requires one important parameter, eventHandlerCallback. This is a function to be called by this renderer each
    #frame so that the user can inject code into each frame. See sample code for more detail.
    def __init__(self, eventHandlerCallback, displayDimensions = (800, 600), FOV = 80, cameraView = 'isometric'):

        #Initialize pygame
        pygame.init()

        #Initialize attributes
        self.displayDimensions = displayDimensions
        self.FOV = FOV

        #Stores the eventHandlerCallback for use during rendering
        self._eventHandler = eventHandlerCallback

        #Initializes the list of items in the scene
        #Each item MUST have a draw() method
        self._sceneItems = []

        #A state variable used to stop rendering
        self._keepRendering = False

        #Initialize display window via pygame
        pygame.display.set_mode(self.displayDimensions, DOUBLEBUF | OPENGL)

        #Initialize viewport parameters
        gluPerspective(self.FOV, (self.displayDimensions[0] / self.displayDimensions[1]), 0.1, 50.0)

        #Sets static camera viewpoint
        if cameraView == 'isometric':
            glRotatef(45, 0, 1, 0)
            glRotatef(45, 1, 0, 1)
            glTranslatef(5.0, -5.0, -5.0)
        elif cameraView == 'zoomed-out':
            glTranslatef(0.0, 0.0, -10.0)
            glRotatef(0, 0, 0, 0)
        else:
            glTranslatef(0.0, 0.0, 0.0)
            glRotatef(0, 0, 0, 0)

        #OpenGL Flags
        glEnable(GL_DEPTH_TEST)

    #Renders the objects of the scene
    def _renderScene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for item in self._sceneItems:
            item.draw()
        pygame.display.flip()

    #Adds an item to be rendered each frame
    #Item MUST have a draw() method
    def addSceneItem(self, item):
        self._sceneItems.append(item)
        #Returns the index of the newly added item
        return len(self._sceneItems) - 1

    #Removes an item from the scene
    def removeSceneItem(self, item):
        self._sceneItems.remove(item)

    #Removes an item from the scene by index, returning the removed item
    def removeSceneItemByIndex(self, index):
        item = self._sceneItems[index]
        self.removeItemFromScene(item)
        return item

    #Stops rendering the scene
    def stop(self):
        self._keepRendering = False

    #Starts the scene rendering
    def start(self):
        self._keepRendering = True

        #This loop is the main loop for whichever program uses this class.
        #This should be the last thing the user calls in their main program, other than stopping this.
        while self._keepRendering:

            #Calls any code the user has defined in eventHandlerCallback
            self._eventHandler()

            #See SimpleSceneRender._renderScene()
            self._renderScene()

            #Arbitrary delay to reduce processor load
            pygame.time.wait(10)
