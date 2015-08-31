#!/bin/bash

#__author__ = "Ciprian-Octavian Truică"
#__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
#__license__ = "GNU GPL"
#__version__ = "0.1"
#__email__ = "ciprian.truica@cs.pub.com"
#__status__ = "Production"

#args:
#  1 - corpus csv format
#  2 - delimiter (t - tab, c - comma, s - Semicolon)
#  3 - has header (0 - false, 1 - true)
#  4 - Database name
#  5 - host = host of the database
#  6 - port of the database - integer
#  7 - language, currently supports EN (English) and FR (French) - only lemmatization, not NER
#  8 - type of opperations to do: 0(insert), 1(update), 2(delete)
#  9 - mode for lemmatizer (works only for English): 0 (fast but not accurate), 1 (slow but accurate)
# 10 - integer: 0 - use parallelized version, 1 - use serialized version
#example: python populateDB.py DATA_SETS/news_articles/rss.csv t 1 2 ERICDB localhost 27017 EN 1 1 0


HEADER=0
DELIMITER="t"
OP=1
LANGUAGE=EN
INIT_0=0
INIT_1=1
MODE=1
SERIAL=0
FILE="../DATA_SETS/tweets/corpus"
DB="TwitterDB_new"
HOST="localhost"
PORT=27017
echo $FILE

# testing PopulateDB & vocabulary build incremental
# give one parameter to set no of test

for j in `seq 1 60`
do
	if [ $j = 0 ]
	then
		# need init == 0 to drop the database
		python testing_tweets_new.py $FILE$j".csv" $DELIMITER $HEADER $DB $HOST $PORT $LANGUAGE $INIT_0 $MODE $SERIAL
	else
		# need init == 1 to do incremental insert
		python testing_tweets_new.py $FILE$j".csv" $DELIMITER $HEADER $DB $HOST $PORT $LANGUAGE $INIT_1 $MODE $SERIAL
	fi
done;
