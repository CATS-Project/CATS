# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import pymongo



mapFunction = """function() {
                    for (var idx=0; idx<this.words.length; idx++){
                        var key = this.words[idx].word;
                        pos = this.words[idx].pos;
                        var value = { 'pos': pos};
                        emit(key, value);
                    }
                }"""

reduceFunction = """function(key, values) {
                        var result = {'pos': []};
                        values.forEach(function (v) {
                            result.pos = v.pos.concat(result.pos);
                        });
                        return result;
                    }"""

functionCreate = """function(){
                        var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
                        while(items.hasNext()){
                            var item = items.next();
                            pos_uniq = item.value.pos.reduce(function(a,b){
                                    if (a.indexOf(b) < 0 ) {
                                        a.push(b);
                                    }
                                return a; },[]);
                            doc = {word: item._id, createdAt: new Date(), pos: pos_uniq};
                            db.pos_index.insert(doc);
                        }
                        db.temp_collection.drop();
                    }"""

functionUpdate = """function(){
                        var items = db.temp_collection.find().addOption(DBQuery.Option.noTimeout);
                        while(items.hasNext()){
                            var item = items.next();
                            var wordID = item._id;
                            var pos_uniq = item.value.pos.reduce(function(a,b){
                                    if (a.indexOf(b) < 0 ) {
                                        a.push(b);
                                    }
                            return a; },[]);
                            var exists = db.pos_index.findOne({word: wordID}, {pos: 1, _id: 0});
                            if (exists){
                                var pos = exists.pos;
                                pos = pos.concat(pos_uniq);
                                pos = pos.reduce(function(a,b){
                                            if (a.indexOf(b) < 0 ) {
                                                a.push(b);
                                            }
                                            return a; },[]);
                                db.pos_index.update({word: wordID}, {$set: {pos: pos}});
                            }else{
                                doc = {word: wordID, createdAt: new Date(), pos: pos_uniq};
                                db.pos_index.insert(doc);
                            }
                        }
                        db.temp_collection.drop();
                }"""

functionDelete = """function (){
                        //update pos_index
                        var words = db.pos_index.find({}, {_id: 0, word: 1}).addOption(DBQuery.Option.noTimeout).toArray();
                        var list_words = [];
                        for (var idx in words){
                            var exists = db.words.count({'words.word': words[idx].word});
                            if (exists == 0){
                                list_words.push(words[idx].word);
                            }
                        }
                        db.pos_index.remove({word: {$in: list_words}})
                    }"""

class POSIndex:
    def __init__(self, dbname):
        client = pymongo.MongoClient()
        self.db = client[dbname]
    
    def createIndex(self, query=None):
        self.db.pos_index.drop()
        if query:
            self.db.documents.map_reduce(mapFunction, reduceFunction, "temp_collection", query = query)
        else:
            self.db.documents.map_reduce(mapFunction, reduceFunction, "temp_collection")
        self.db.eval(functionCreate)
        #self.db.pos_index.ensure_index("word")
    
    #update index after docunemts are added
    #startDate - the date
    def updateIndex(self, startDate):
        query = {"createdAt": {"$gt": startDate } }
        self.db.documents.map_reduce(mapFunction, reduceFunction, "temp_collection", query = query)
        self.db.eval(functionUpdate)

    #docIDs - list of documents
    def deleteIndex(self):
        #self.db.eval(functionDelete)
        self.createIndex()



