#!/usr/bin/env python

import pygame

from OpenGLTools.GLRendering import SimpleSceneRenderer
from OpenGLTools.Basic3DShapes import *

test_data = open("Preprocessing/test_data_2000.txt", "r")

grid = Grid(width = 10, length = 10, color = (0.0, 1.0, 0.0))
box = Cube(sideLength = 0.5)

def parseCoords():
    line = test_data.readline()
    nums = line.split(":")
    return (float(nums[0]), 0.5, float(nums[1]))

def eventLoop():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    coords = parseCoords()
    box.setPosition(coords)

scene = SimpleSceneRenderer(eventLoop)

scene.addSceneItem(grid)
scene.addSceneItem(box)

scene.start()
