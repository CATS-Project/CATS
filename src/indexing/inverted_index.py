# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import pymongo

mapFunction = """function() {
                    var ids = [];
                    ids.push(this._id)
                    for (var i in this.words){
                        var key = this.words[i].word;
                        var value = { 'ids': ids};
                        emit(key, value);
                    }
                }"""

reduceFunction = """function(key, values) {
                    var result = {'ids': []};
                    values.forEach(function (v) {
                        result.ids = v.ids.concat(result.ids)
                    });
                    return result;
                };"""

functionCreate = """function(){
                var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
                while(items.hasNext()){
                    var item = items.next();
                    doc = {word: item._id, createdAt: new Date(), docIDs: item.value.ids};
                    db.inverted_index.insert(doc);
                }
                db.temp_collection.drop();
            }"""

functionUpdate = """function(){
                var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
                while(items.hasNext()){
                    var item = items.next();
                    var wordID = item._id;
                    var exists = db.inverted_index.findOne({word: wordID}, {docIDs: 1, _id: 0});
                    if (exists){
                            var docIDs = exists.docIDs;
                            docIDs = docIDs.concat(item.value.ids);
                            db.inverted_index.update({word: wordID}, {$set: {docIDs: docIDs}});
                    }else{
                        doc = {word: wordID, createdAt: new Date(), docIDs: item.value.ids};
                        db.inverted_index.insert(doc);
                    }
                }
                db.temp_collection.drop();
            }"""

class InvertedIndex:
    def __init__(self, dbname):
        client = pymongo.MongoClient()
        self.db = client[dbname]


    def createIndex(self, query=None):
        self.db.inverted_index.drop()
        if query:
            self.db.documents.map_reduce(mapFunction, reduceFunction, "temp_collection", query = query)
        else:
            self.db.documents.map_reduce(mapFunction, reduceFunction, "temp_collection")
        self.db.eval(functionCreate)
        #self.db.inverted_index.ensure_index("word")

    def updateIndex(self, startDate):
        query = {"createdAt": {"$gt": startDate } }
        self.db.documents.map_reduce(mapFunction, reduceFunction, "temp_collection", query = query)        
        self.db.eval(functionUpdate)

    #docIDs - list of documents
    def deleteIndex(self, docIDs):
        self.db.inverted_index.update({ }, { "$pull": { "docIDs" : {"$in": docIDs} } },  multi=True)
        self.db.inverted_index.remove({"docIDs" : {"$size": 0}}, multi=True )
