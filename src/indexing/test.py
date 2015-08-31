# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

from vocabulary_index import VocabularyIndex

#words with or 
query_or = {"words.word" : {"$in": ["shit", "fuck"] }, "date": {"$gt": "2015-04-10", "$lte":  "2015-04-12"}}
#words with and
query_and = {"$and": [{ "words.word": "shit"}, {'words.word': "fuck" } ], "date": {"$gt": "2015-04-10", "$lte":  "2015-04-12"}}

#"author" : "76570268", 
vocab = VocabularyIndex('TwitterDB')
vocab.createIndex(query=query_and)