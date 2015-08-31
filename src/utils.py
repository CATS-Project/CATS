# coding: utf-8
__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import csv

#author field parse
def getAuthorName(text, ch = ','):
    return [(' '.join(name.split(' ')[:-1]), name.split(' ')[-1]) for name in text.split(ch)]

#this part is for reading the file
def determineDelimiter(character):
    if character == 't':
        return '\t'
    elif character == 'c':
        return ','
    elif character == 's':
        return ';'

def readCSV(filename, csv_delimiter = ';', header = True):    
    with open(filename, 'rU') as csvfile:
        spamreader = csv.reader(csvfile, delimiter = csv_delimiter)        
        if header:    #the csv file contain a header
            h = spamreader.next()
            return h, [row for row in spamreader]
        else:
            return [], [row for row in spamreader]