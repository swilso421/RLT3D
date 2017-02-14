#!/usr/bin/env python

from random import *

print("Script for generating two dimensional coordinate data")
print("Data is stored in a txt file where each line has a pair of coordinates, delimited by a colon")
print("Max distance in each dimension from previous point is 0.1")
print("Domain of each dimension is (-5.0, 5.0)")
print("WARNING!: This script does not validate input or handle errors")

filename = raw_input("Name of data file: ")
n = int(raw_input("Number of coordinate pairs to generate: "))

x = 0.0
z = 0.0

with open("{}.txt".format(filename), "w+") as f:

    for i in range(n):

        x = x + (0.2 * random() - 0.1)
        z = z + (0.2 * random() - 0.1)

        if x > 5.0:
            x = 5.0
        elif x < -5.0:
            x = -5.0
        if z > 5.0:
            z = 5.0
        elif z < -5.0:
            z = -5.0

        f.write("{0}:{1}\n".format(x, z))
