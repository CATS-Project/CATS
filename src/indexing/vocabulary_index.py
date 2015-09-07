# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import pymongo
from time import time

mapFunction = """function() {
                    for (var idx=0; idx<this.words.length; idx++){
                        emit(this.words[idx].word, 1);
                    }
                }"""

reduceFunction = """function(key, values) {
                        return Array.sum(values);
                    }"""

functionCreate = """function(noDocs, all){
                        var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
                        var docs = Array();
                        while(items.hasNext()){
                            var item = items.next();
                            var idf = 1 + Math.round(Math.log(noDocs/item.value) * 100)/100;
                            doc = {word: item._id, IDF: idf};
                            docs.push(doc);
                        }
                        if (all == 1){
                            db.vocabulary.insert(docs);
                            db.vocabulary.ensureIndex({IDF:1});
                        }
                        else if (all == 0){
                            db.vocabulary_query.insert(docs);
                            db.vocabulary_query.ensureIndex({'IDF':1});
                        }
                        db.temp_collection.drop();
                    }"""


class VocabularyIndex:
    def __init__(self, dbname, host='localhost', port=27017):
        client = pymongo.MongoClient(host=host, port=port)
        self.db = client[dbname]
        self.db.documents.ensure_index([('words.word', pymongo.ASCENDING)])
    
    def createIndex(self, query=None):
        if query:
            self.db.vocabulary_query.drop()
            self.db.documents.map_reduce(mapFunction, reduceFunction, "temp_collection", query=query, sort={'words.word': 1})
            noDocs = self.db.documents.count(query)
            self.db.eval(functionCreate, noDocs, 0)
        else:
            self.db.vocabulary.drop()
            self.db.documents.map_reduce(mapFunction, reduceFunction, "temp_collection", sort={'words.word': 1})
            noDocs = self.db.documents.count()
            self.db.eval(functionCreate, noDocs, 1)


if __name__ == '__main__':
    print "Starting..."
    query = dict()
    query['gender'] = 'homme'
    query["words.word"] = {"$in": ['cat', 'dog'] }
    print "Starting initializing class..."
    start = time()
    vi = VocabularyIndex(dbname='TwitterDB_test')
    end = time()
    print "time:", (end-start)
    print "Starting Create Index without query..."
    start = time()
    vi.createIndex()
    end = time()
    print "time:", (end-start)
    print "Starting Create Index with query...", query
    start = time()
    vi.createIndex(query=query)
    end = time()
    print "time:", (end-start)

    # testing for OLAPDB
    # query['authors.genderid'] = 1
    # query["words.word"] = {"$in": ['cat', 'dog'] }
    # print "Starting initializing class..."
    # start = time()
    # vi = VocabularyIndex(dbname='OLAPDB')
    # end = time()
    # print "time:", (end-start)
    # print "Starting Create Index without query..."
    # start = time()
    # vi.createIndex(query={})
    # end = time()
    # print "time:", (end-start)
    # print "Starting Create Index with query...", query
    # start = time()
    # vi.createIndex(query=query)
    # end = time()
    # print "time:", (end-start)
