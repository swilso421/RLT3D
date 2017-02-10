#!/usr/bin/env python

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from math import sin, cos, radians

from Basic3DShapes import *

sceneObjects = []

def init():
    pygame.init()
    display = (1600, 900)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(80, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, -5.0, -10.0)
    glRotatef(45, 0, 1, 0)
    glRotatef(45, 1, 0, 1)
    glEnable(GL_DEPTH_TEST)

def addObjectToScene(object):
    sceneObjects.append(object)

def renderScene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    for object in sceneObjects:
        object.draw()
    pygame.display.flip()

init()

mover = Cube()

addObjectToScene(mover)
addObjectToScene(Cube((0.0, 0.5, 1.0), color = (0.0, 0.0, 0.0)))
addObjectToScene(Cube((1.0, 0.5, 1.0), color = (0.0, 0.0, 1.0)))
addObjectToScene(Cube((1.0, 0.5, 0.0), color = (0.0, 1.0, 0.0)))
addObjectToScene(Cube((1.0, 0.5, -1.0), color = (0.0, 1.0, 1.0)))
addObjectToScene(Cube((0.0, 0.5, -1.0), color = (1.0, 0.0, 0.0)))
addObjectToScene(Cube((-1.0, 0.5, -1.0), color = (1.0, 0.0, 1.0)))
addObjectToScene(Cube((-1.0, 0.5, 0.0), color = (1.0, 1.0, 0.0)))
addObjectToScene(Cube((-1.0, 0.5, 1.0), color = (1.0, 1.0, 1.0)))
addObjectToScene(Grid(width = 10, length = 10, color = (0.0, 1.0, 0.0)))
# addObjectToScene(Grid(rotationAngle = 90, rotationVector = (0, 0, -1), width = 10, length = 10, color = (0.0, 0.0, 1.0)))
# addObjectToScene(Grid(rotationAngle = 90, rotationVector = (-1, 0, 0), width = 10, length = 10, color = (1.0, 0.0, 0.0)))

#gluLookAt(0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0, 1, 0)

newPosition = [0.0, 0.0, 0.0]
oldPosition = [0.0, 0.0, 0.0]

counter = 0.0

while True:
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

    # camX = 10.0 * cos(radians(angle % 360))
    # camZ = 10.0 * sin(radians(angle % 360))
    # angle += 1
    # gluLookAt(camX, 10.0, camZ, 0.0, 2.0, -10.0, 0, 1, 0)

    # newPosition[1] = oldPosition[1] + 0.05
    # mover.setPosition(newPosition)
    # oldPosition = newPosition

    renderScene()
    pygame.time.wait(10)
