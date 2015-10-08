# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import pymongo
from ne_index import NEIndex
from vocabulary_index import VocabularyIndex

class Queries:
    def __init__(self, dbname, host='localhost', port=27017):
        #client = pymongo.MongoClient()
        self.host = host
        self.port = port
        client = pymongo.MongoClient(host=self.host, port=self.port)
        self.dbname = dbname
        self.db = client[self.dbname]

    def countDocuments(self, query=None):
        return self.db.documents.find(query).count()

    def dropDocuments(self):
        self.db.documents.drop()

    def getOneWord(self, query=None, fields=None, existing=False):
        if existing:
            return self.db.vocabulary_query.find_one(query, fields)
        else:
            return self.db.vocabulary.find_one(query, fields)

    def getWords(self, query=None, fields=None, limit=0, existing=False):
        if existing:
            return self.db.vocabulary_query.find(query, fields, limit=limit, sort=[('IDF',pymongo.ASCENDING)])
        else:
            return self.db.vocabulary.find(query, fields, limit=limit, sort=[('IDF',pymongo.ASCENDING)])

    def getNamedEntities(self, query=None, limit=0):
        if query:
            # if there is a query then we construct a smaller NE_INDEX
            query_ner = {'namedEntities': {'$exists': 'true'}}
            query_ner.update(query)
            self.constructNamedEntities(query=query_ner)
            return self.db.named_entities_query.find(sort=[('count',pymongo.DESCENDING)], limit=limit)
        else:
            # use the already build NE_INDEX
            return self.db.named_entities.find(sort=[('count',pymongo.DESCENDING)], limit=limit)

    def constructVocabulary(self, query=None):
        vocab = VocabularyIndex(dbname=self.dbname, host=self.host, port=self.port)
        vocab.createIndex(query)

    def constructNamedEntities(self, query=None):
        ner = NEIndex(dbname=self.dbname, host=self.host, port=self.port)
        ner.createIndex(query)

    def getDocuments(self, query=None, fields=None):
        return self.db.documents.find(query, fields)

    def getOneDocument(self, query=None, fields=None):
        return self.db.documents.find_one(query, fields)


    def bulkInsert(self, documents):
        try:
            self.db.documents.insert(documents, continue_on_error=True)
            self.db.documents.ensure_index([('date', pymongo.ASCENDING)])
            self.db.documents.ensure_index([('gender', pymongo.ASCENDING)])
            self.db.documents.ensure_index([('age', pymongo.ASCENDING)])
            self.db.documents.ensure_index([('words.word', pymongo.ASCENDING)])
            self.db.documents.ensure_index([('hashtags', pymongo.ASCENDING)])
        except pymongo.errors.DuplicateKeyError:
            pass

if __name__ == "__main__":
    queries = Queries('TwitterDB', 'localhost', 27017)
    queries.constructVocabulary()
    # x = queries.getOneWord(query={'word': 'fuck'}, fields={'IDF': 1}, existing=False)['IDF']
    print x
