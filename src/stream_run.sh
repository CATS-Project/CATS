#!/bin/bash

#__author__ = "Ciprian-Octavian Truică"
#__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
#__license__ = "GNU GPL"
#__version__ = "0.1"
#__email__ = "ciprian.truica@cs.pub.com"
#__status__ = "Production"

#args:
#1 - corpus csv format
#2 - delimiter (t -tab, c - comma, s - Semicolon)
#3 - has header (0 - false, 1 - true)
#4 - Database name
#5 - language, currently supports EN (English) and FR (French) - only lemmatization, not NER
#6 - type of opperations to do: 0(insert), 1(update), 2(delete)
#7 - mode for lemmatizer (works only for English): 0 (fast but not accurate), 1 (slow but accurate)
#8 - 1 - use serialized version, 0 - use parallelized version
HEADER=0
DELIMITER="t"
OP=1
LANGUAGE=EN
INIT=0
MODE=1
FILE=$1
DB=$2
HOST=$3
PORT=$4
python testing_tweets.py $FILE $DELIMITER $HEADER $DB $HOST $PORT $LANGUAGE $INIT $MODE 0


