# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import time
import utils
from ddl_mongo_new import *
from indexing.queries import Queries


# try to parallelize this
def populateDB(filename, csv_delimiter, header, language='EN', dbname='TwitterDB', host='localhost', port=27017, mode=0, serialized=False):
    start = time.time() 
    h, lines = utils.readCSV(filename, csv_delimiter, header)
    populateDatabase(lines, language, dbname, host, port, mode, serialized)
    end = time.time() 
    print "time_populate.append(", (end - start), ")"


def constructIndexes(dbname, host, port):
    #build Vocabulary
    queries = Queries(dbname=dbname, host=host, port=port)
    start = time.time()
    queries.constructVocabulary()
    end = time.time()
    print "vocabulary_build.append(", (end - start) , ")"

    # built the NE Index
    start = time.time()
    queries.constructNamedEntities()
    end = time.time()
    print "ne_build.append(", (end - start) , ")"

def main(filename, csv_delimiter='\t', header=True, dbname='TwitterDB', host='localhost', port=27017, language='EN', initialize=0, mode=0, serialized=False):
    # print mode, serialized, header
    # initialize everything from the stat
    if initialize == 0:
        queries = Queries(dbname=dbname, host=host,port=port)
        queries.dropDocuments()
    populateDB(filename, csv_delimiter, header, language, dbname=dbname, host=host, port=port, mode=mode, serialized=serialized)
    constructIndexes(dbname, host, port)


# this script receives 7 parameters
#  1 - filename
#  2 - the csv delimiter: t - tab, c - coma, s - semicolon
#  3 - integer: 1 csv has header, 0 csv does not have hearer
#  4 - dbname = name of the database
#  5 - host = host of the database
#  6 - port of the database - integer
#  7 - language: EN or FR
#  8 - integer: 0 - create the database, 1 - update the database
#  9 - integer: 0 - use fast lemmatizer (not accurate), 1 - use slow lemmatizer (accurate)
# 10 - integer: 0 - use parallelized version, 1 - use serialized version
if __name__ == "__main__":
    filename = sys.argv[1] 
    csv_delimiter = utils.determineDelimiter(sys.argv[2])
    header = bool(int(sys.argv[3]))
    dbname = sys.argv[4]
    host = sys.argv[5]
    port = int(sys.argv[6])
    language = sys.argv[7] #currently EN & FR, FR does not work so well
    initialize = int(sys.argv[8])
    mode = int(sys.argv[9])
    serialized = bool(int(sys.argv[10]))

    main(filename=filename, csv_delimiter=csv_delimiter, header=header, dbname=dbname, host=host, port=port, language=language, initialize=initialize, mode=mode, serialized=serialized)
