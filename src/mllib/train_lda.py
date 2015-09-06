# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import pymongo
from gensim import corpora, models
from nltk.corpus import stopwords
from collections import defaultdict

cachedStopWords_en = stopwords.words("english")
cachedStopWords_fr = stopwords.words("french") + ["ce", "cet", "cette", "le", "les"]


class LDA:
    def __init__(self, dbname='TwitterDB', host='localhost', port=27017, language='EN' ):
        client = pymongo.MongoClient(host=host, port=port)
        self.db = client[dbname]
        if language == 'EN':
            self.sw = cachedStopWords_en
        elif language == 'FR':
            self.sw = cachedStopWords_fr

    def apply(self, query={}, num_topics=15, num_words=10, iterations=500):
        try:
            documents = []
            documentsDB = self.db.documents.find(query, {'lemmaText': 1, '_id': 0})
            for document in documentsDB:
                documents.append([lemma for lemma in document['lemmaText'].split() if lemma not in self.sw])
            dictionary = corpora.Dictionary(documents)
            corpus = [dictionary.doc2bow(document) for document in documents]
            tfidf = models.TfidfModel(corpus)
            corpus_tfidf = tfidf[corpus]
            lda = models.LdaModel(corpus=corpus_tfidf, id2word=dictionary, iterations=iterations, num_topics=num_topics)
            corpus_lda = lda[corpus_tfidf]
            return [lda.show_topics(num_topics=num_topics, num_words=num_words, formatted=False), corpus_lda]
        except Exception as e:
            print e

