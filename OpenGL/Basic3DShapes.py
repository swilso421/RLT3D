#!/usr/bin/env python

from OpenGL.GL import *
from OpenGL.GLU import *

class Cube:

    def __init__(self, coords = (0, 0, 0), sideLength = 1.0, rotationAngle = 0, rotationVector = (0, 1, 0), wireFrame = False, color = (1.0, 1.0, 1.0)):

        self._coords = coords
        self._sideLength = sideLength
        self._wireFrame = wireFrame
        self._color = color

        self._rotationAngle = rotationAngle
        self._rotationVector = rotationVector

        self._generateVertices()

        self._edges = (
        (0, 1),
        (0, 3),
        (0, 4),
        (2, 1),
        (2, 3),
        (2, 6),
        (5, 1),
        (5, 4),
        (5, 6),
        (7, 3),
        (7, 4),
        (7, 6),
        )

        self._surfaces = (
        (0, 1, 2, 3),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (0, 3, 7, 4),
        (4, 5, 6, 7),
        )

    def _generateVertices(self):
        #The delta values are the offsets of the vertices from the coords
        self._deltaX = float(self._sideLength / 2.0)
        self._deltaY = self._deltaX
        self._deltaZ = self._deltaY

        self._vertices = (
        (self._coords[0] + self._deltaX, self._coords[1] - self._deltaY, self._coords[2] - self._deltaZ),
        (self._coords[0] + self._deltaX, self._coords[1] + self._deltaY, self._coords[2] - self._deltaZ),
        (self._coords[0] - self._deltaX, self._coords[1] + self._deltaY, self._coords[2] - self._deltaZ),
        (self._coords[0] - self._deltaX, self._coords[1] - self._deltaY, self._coords[2] - self._deltaZ),
        (self._coords[0] + self._deltaX, self._coords[1] - self._deltaY, self._coords[2] + self._deltaZ),
        (self._coords[0] + self._deltaX, self._coords[1] + self._deltaY, self._coords[2] + self._deltaZ),
        (self._coords[0] - self._deltaX, self._coords[1] + self._deltaY, self._coords[2] + self._deltaZ),
        (self._coords[0] - self._deltaX, self._coords[1] - self._deltaY, self._coords[2] + self._deltaZ),
        )

    def _drawFilled(self):
        glPushMatrix()
        glRotatef(self._rotationAngle, self._rotationVector[0], self._rotationVector[1], self._rotationVector[2])
        glBegin(GL_QUADS)

        glColor3fv(self._color)

        for surface in self._surfaces:
            for vertex in surface:
                glVertex3fv(self._vertices[vertex])

        glEnd()
        glPopMatrix()

    def _drawOutline(self):
        glPushMatrix()
        glRotatef(self._rotationAngle, self._rotationVector[0], self._rotationVector[1], self._rotationVector[2])
        glBegin(GL_LINES)

        glColor3fv(self._color)

        for edge in self._edges:
            for vertex in edge:
                glVertex3fv(self._vertices[vertex])

        glEnd()
        glPopMatrix()

    def setPosition(self, coords = (0.0, 0.0, 0.0)):
        self._coords = coords
        self._generateVertices()

    def setRotation(self, degrees, x, y, z):
        self._rotationAngle = degrees
        self._rotationVector = (x, y, z)

    def draw(self):
        if self._wireFrame:
            self._drawOutline()
        else:
            self._drawFilled()

class Grid:

    def __init__(self, coords = (0.0, 0.0, 0.0), rotationAngle = 0, rotationVector = (0, 1, 0), width = 10, length = 10, color = (1.0, 1.0, 1.0)):

        self._coords = coords
        self._width = width
        self._length = length
        self._color = color
        self._rotationAngle = rotationAngle
        self._rotationVector = rotationVector

        self._vertices = []
        self._edges = []

        self._generateVertices()

    def _generateVertices(self):
        minX = self._coords[0] - float(self._width / 2.0)
        minZ = self._coords[2] - float(self._length / 2.0)

        for k in range(self._length + 1):
            self._vertices.append([])
            for j in range(self._width + 1):
                self._vertices[k].append((float(minX + j), self._coords[1], float(minZ + k)))

    def _drawEdges(self):
        glPushMatrix()
        glRotatef(self._rotationAngle, self._rotationVector[0], self._rotationVector[1], self._rotationVector[2])
        glBegin(GL_LINES)

        glColor3fv(self._color)

        for k in range(self._length + 1):
            for j in range(self._width):
                glVertex3fv(self._vertices[k][j])
                glVertex3fv(self._vertices[k][j + 1])

        for j in range(self._width + 1):
            for k in range(self._length):
                glVertex3fv(self._vertices[k][j])
                glVertex3fv(self._vertices[k + 1][j])

        glEnd()
        glPopMatrix()

    def setRotation(self, degrees, x, y, z):
        self._rotationAngle = degrees
        self._rotationVector = (x, y, z)

    def draw(self):
        self._drawEdges()
