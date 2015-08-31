# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"


import pymongo
from gensim.utils import lemmatize
from nlplib.clean_text import CleanText
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
import time
import math

cleanText = CleanText()

# function = """function(){
#                 var items = db.search_index2.find().addOption(DBQuery.Option.noTimeout);
#                 while(items.hasNext()){
#                 var item = items.next();
#                     doc = {word: item._id, docIDs: item.value.docIDs};
#                     db.search_index.insert(doc);
#                 }
#             }"""
#
# mapFunction = """function() {
#                 var key = this.word;
#                 for (var idx=0; idx<this.docIDs.length; idx++){
#                     var tfidf = this.idf * this.docIDs[idx].tf;
#                     value = { 'docID': this.docIDs[idx].docID, 'TFIDF': tfidf };
#                     emit(key, {'docIDs': [value]});
#                 }
#             }"""
#
# reduceFunction = """function(key, values){
#                 var result = {'docIDs': []};
#                 values.forEach(function(v){
#                     result.docIDs = v.docIDs.concat(result.docIDs);
#                 });
#                 return result;
#             }"""

class Search:

    # def score(self, word):
    #     self.db.search_index2.drop()
    #     self.db.search_index.drop()
    #     if self.query:
    #         print 'I am here!'
    #         self.db.vocabulary_query.map_reduce(mapFunction, reduceFunction, 'search_index2', query={'word': word})
    #     else:
    #         self.db.vocabulary.map_reduce(mapFunction, reduceFunction, 'search_index2', query={'word': word})
    #     self.db.eval(function)
    #     response = self.db.search_index.find({'word': word}, {'docIDs': 1, '_id': 0})
    #     lista = {}
    #     #for value in response[0]['docIDs']:
    #     #    lista[value['docID']] = value['TFIDF']
    #     try:
    #         for value in response[0]['docIDs']:
    #             lista[value['docID']] = value['TFIDF']
    #     except Exception as exp:
    #         print exp
    #     self.db.search_index2.drop()
    #     self.db.search_index.drop()
    #     return lista

    def score(self, word):
        if self.query:
            cursor = self.db.vocabulary_query.find({'word': word}, fields={'idf': 1, 'docIDs': 1})
        else:
            cursor = self.db.vocabulary.find({'word': word}, fields={'idf': 1, 'docIDs': 1})
        lista = {}
        for elem in cursor:
            for doc in elem['docIDs']:
                lista[doc['docID']] = doc['tf'] * elem['idf']
        return lista

    def rank(self, searchPhrase):
        keys = []
        scorePhrase = {}
        for word in searchPhrase:
            if not keys:
                keys = self.listSearch[word].keys()
            else:
                keys = list(set(keys) & set(self.listSearch[word].keys()))
        for key in keys:
            score = 0
            for word in searchPhrase:
                score += self.listSearch[word][key]
            scorePhrase[key] = round(score, 2)
        #print searchPhrase, scorePhrase
        return scorePhrase, keys

    def results(self):
        no_threads = cpu_count()

        with ThreadPoolExecutor(max_workers = no_threads) as e:
            for word in self.words:
                result = e.submit(self.score, word)
                self.listSearch[word] = result.result()

        keys = {}
        rankedPhrase = {}
        w = ' '.join(word for word in self.words)
        rankedPhrase[w], keys[w] = self.rank(self.words)

        distinctKeys = []
        for key in keys:
            distinctKeys += keys[key]
        distinctKeys =list(set(distinctKeys))

        answer = {}
        for key in distinctKeys:
            if rankedPhrase[w].get(key, -1) != -1:
                answer[key] = max(rankedPhrase[w][key], answer.get(key, -1))

        if self.k != 0:
            answer = dict(sorted(answer.items(), key=lambda x: x[1], reverse=True)[:self.k])
        else:
            answer = dict(sorted(answer.items(), key=lambda x: x[1], reverse=True))
        l = []
        for key in answer:
            d = {}
            d = self.db.documents.find_one(spec_or_id={"_id": key})
            l.append({ 'id': key, 'rawText': d['rawText'], 'author': d['author'], 'date': d['date'], 'score':math.log(1+answer[key],2) })
        return l

    def __init__(self, searchPhrase, dbname='TwitterDB', query=False, k=0):
        client = pymongo.MongoClient()
        self.db = client[dbname]
        self.words = [word.split('/')[0] for word in lemmatize(cleanText.removeStopWords(cleanText.cleanText(searchPhrase)[0]))]
        self.listSearch = {}
        self.query = query
        self.k = k

if __name__ == "__main__":
    searchPhrase = "like get"
    time_words = []
    for j in range(0, 1):
        start = time.time()
        search = Search(searchPhrase = searchPhrase)
        l = search.results()
        print len(l)
        for i in range(0, len(l)):
            print l[i]
        end = time.time()
        time_words.append(end-start)
    print "no search words: k = ", 20, 'mean time:', round(sum(time_words)/len(time_words), 2)
