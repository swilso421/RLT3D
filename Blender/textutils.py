#!/usr/bin/env python3

import re

SPECIAL_CHARS = re.compile('[^\s\w]+')
SPACES = re.compile('\s+')

#Breaks a string into separate words
def splitWords(phrase):
    SPECIAL_CHARS.sub('', phrase.lower())
    words = SPACES.split(phrase)
    return words

#Calculates the Levenshtein distance between two strings
def Levenshtein(s1, s2):
    #Initialize a distance matrix of zeroes
    distances = [[0 for j in range(len(s2) + 1)] for k in range(len(s1) + 1)]

    #Initialize the left column of distances
    for k in range(1, len(s1) + 1):
        distances[k][0] = k

    #Initialize the top row of distances
    for j in range(1, len(s2) + 1):
        distances[0][j] = j

    #Fill the matrix with calculated distances
    for j in range(1, len(s2) + 1):
        for k in range(1, len(s1) + 1):
            subcost = 0 if s1[k-1] == s2[j-1] else 1
            distances[k][j] = min(distances[k-1][j] + 1, distances[k][j-1] + 1, distances[k-1][j-1] + subcost)

    #Return the Levenshtein distance (the last value in the matrix)
    return distances[len(s1)][len(s2)]
