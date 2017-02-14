#!/usr/bin/env python

from random import *

print("Script for generating two dimensional coordinate data")
print("Data is stored in a txt file where each line has a pair of coordinates, delimited by a colon")
#print("Max distance in each dimension from previous point is 0.05")
print("Domain of each dimension is (-5.0, 5.0)")
#print("WARNING!: This script does not validate input or handle errors")

#filename = raw_input("Name of data file: ")
#n = int(raw_input("Number of coordinate pairs to generate: "))

n = 200

x = 0.0
z = 0.0

def distance(p1, p2):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

with open("test_data.txt", "w+") as f:

    for i in range(n):

        newx = 10.0 * random() - 5.0
        newz = 10.0 * random() - 5.0

        if newx > 5.0:
            newx = 5.0
        elif newx < -5.0:
            newx = -5.0
        if newz > 5.0:
            newz = 5.0
        elif newz < -5.0:
            newz = -5.0

        deltax = (newx - x) / 100.0
        deltaz = (newz - z) / 100.0

        for j in range(100):

            f.write("{0}:{1}\n".format(x + (j + 1) * deltax, z + (j + 1) *deltaz))

        x = newx
        z = newz
