# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import pymongo
import codecs
from datetime import datetime, timedelta
from time import time

class MabedFiles:
    def __init__(self, dbname='TwitterDB', host='localhost', port=27017):
        client = pymongo.MongoClient(host=host, port=port)
        self.db = client[dbname]
        self.query = {}

    # slice is given in seconds
    def buildFiles(self, query={}, slice=3600, filepath='./'):
        try:
            #add / at the end of the file path if it doesn't exist
            if filepath[:-1] != '/':
                filepath += '/'
            # copy query into the class query not to change the original query
            self.query = query.copy()
            # get date
            if self.query and self.query.get("date"):
                startDate = datetime.strptime(self.query["date"]["$gt"] + " 00:00:00", '%Y-%m-%d %H:%M:%S')
                endDate = datetime.strptime(self.query["date"]["$lte"] + " 00:00:00", '%Y-%m-%d %H:%M:%S')
            else:
                startDate = datetime.strptime(self.db.documents.find(self.query, {'date': 1, '_id': 0}, limit=1, sort=[('date',pymongo.ASCENDING)])[0]['date'], '%Y-%m-%d %H:%M:%S') - timedelta(0, 1)
                endDate = datetime.strptime(self.db.documents.find(self.query, {'date': 1, '_id': 0}, limit=1, sort=[('date',pymongo.DESCENDING)])[0]['date'], '%Y-%m-%d %H:%M:%S')
            # print slice, startDate, endDate
            idx = 0
            filelen = 8
            while startDate < endDate:
                intDate = startDate + timedelta(0, slice)
                if intDate > endDate:
                    intDate = endDate
                self.query["date"] = { "$gt": str(startDate), "$lte": str(intDate) }
                # print idx, startDate, intDate, query
                documents = self.db.documents.find(self.query, {'rawText': 1, 'date': 1, '_id': 0})
                if documents.count() > 0:
                    filename = filepath + '/' + '0'*(filelen-len(str(idx))) + str(idx)
                    idx += 1
                    with codecs.open(filename+'.text', "w", "utf-8") as textfile, codecs.open(filename+'.time', "w", "utf-8") as timefile:
                        for elem in documents:
                            # encode string to UTF-8
                            # encode Escape character so that they can be removed
                            # remove carriage return and new line
                            text = elem['rawText'].encode('utf8').encode('string_escape').replace('\r', '').replace('\n', '')
                            textfile.write(text + '\n')
                            timefile.write(elem['date']+'\n')
                startDate = intDate
        except Exception as e:
            print e

if __name__ == '__main__':
    # make folders if you want to use the test
    # look at the filepath parameter used for this
    mf = MabedFiles(dbname='TwitterDB')
    query1 = {'words.word': {'$in': [u'fuck']}}
    query2 = {'date': {'$lte': u'2015-04-10', '$gt': u'2015-04-08'}}
    query3 = {'gender': u'femme', 'age': {'$in': [u'5-11', u'12-18', u'45-60', u'61-99']}, 'words.word': {'$in': [u'fuck']}}
    query4 = {'date': {'$lte': u'2015-04-10', '$gt': u'2015-04-08'}, 'gender': u'femme', 'age': {'$in': [u'5-11', u'12-18', u'45-60', u'61-99']}, 'words.word': {'$in': [u'fuck']}}
    query5 = {}
    start = time()
    mf.buildFiles(query1, filepath='test/1', slice=3600)
    end = time()
    print 'Time',(end-start), query1
    start = time()
    mf.buildFiles(query2, filepath='test/2', slice=3600)
    end = time()
    print 'Time',(end-start), query2
    start = time()
    mf.buildFiles(query3, filepath='test/3/', slice=3600)
    end = time()
    print 'Time',(end-start), query3
    start = time()
    mf.buildFiles(query4, filepath='test/4', slice=3600)
    end = time()
    print 'Time',(end-start), query4
    start = time()
    mf.buildFiles(query5, filepath='test/5/', slice=3600)
    end = time()
    print 'Time',(end-start), query5




