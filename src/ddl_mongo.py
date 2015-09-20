# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import sys
from nlplib.lemmatize_text import LemmatizeText
from nlplib.named_entities import NamedEntitiesRegonizer
from nlplib.clean_text import CleanText
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor
from indexing.queries import Queries

reload(sys)
sys.setdefaultencoding('utf8')

ct = CleanText()


# params:
# elems is list of lists:
#   !!! KEEP THIS FORMAT FOR THE BULK INSERT TO WORK,
#   !!! OTHERWISE YOU WILL OPEN THE GATES OF HELL
#   !!! AND BRING UPON THEE MY WRATH
#   each elem in elems has the following structure:
#   * elem[0] = tweet ID - is the PK
#   * elem[1] = raw text of the document
#   * elem[2] = the date of the tweet
#   * elem[3] = author ID of the tweet
#   * elem[4] = location - coordinates
#   * elem[5] = author age
#   * elem[6] = author gender
#   * elem[7] = language of the tweet, default English

# language, default English
# param mode is for the lemmatizer 0 - fast but not accurate, 1 slow but more accurate
# param serialized: True - use serialized method, False - use parallelized method
global mode_global
global language_global

def populateDatabase(elems, language='EN', dbname='TwitterDB', host='localhost', port=27017, mode=0, serialized=True):
    if elems:
        documents = []
        if serialized:
            # single thread
            for elem in elems:
                if len(elem) >= 7:
                    document = processElement_serial(elem, language, mode)
                    if document:
                        documents.append(document)
                else:
                    try:
                        print "tweet with problems: ", elem[0]
                    except Exception, e:
                        print e
        else:
            # parallelized
            global language_global
            language_global = language
            global mode_global
            mode_global = mode
            no_threads = int(cpu_count()/2)
            with ProcessPoolExecutor(max_workers=no_threads) as worker:
                for result in worker.map(processElement_parallel, elems):
                    if result:
                        documents.append(result)
        if documents:
            queries = Queries(dbname=dbname, host=host, port=port)
            queries.bulkInsert(documents=documents)

gender = {'male': 1, 'female': 2, 'homme': 1, 'femme': 2}
# process one element serial
def processElement_serial(elem, language, mode=0):
    document = dict()
    # get language
    if len(elem) >= 8:
        lang = elem[7]
    else:
        lang = language
    # get clean text
    try:
        cleanText, hashtags, attags = ct.cleanText(elem[1], lang)
        # if clean text exists
        if len(ct.removePunctuation(cleanText)) > 0:
            # extract lemmas and part of speech
            lemmas = LemmatizeText(rawText=ct.removePunctuation(cleanText), language=lang, mode=mode)
            lemmas.createLemmaText()
            lemmaText = lemmas.cleanText
            if lemmaText and lemmaText != " ":
                lemmas.createLemmas()
                words = []
                for w in lemmas.wordList:
                    word = dict()
                    word['word'] = w.word
                    word['tf'] = w.tf
                    word['count'] = w.count
                    word['pos'] = w.wtype
                    words.append(word)

                # named entities:
                ner = NamedEntitiesRegonizer(text=cleanText, language=lang)
                ner.createNamedEntities()
                if ner.ner:
                    document['namedEntities'] = ner.ner

                # construct the document
                document['_id'] = elem[0]
                document['rawText'] = elem[1].encode('utf8').encode('string_escape').replace('\r', '').replace('\n', '')
                document['cleanText'] = cleanText.encode('utf8').encode('string_escape').replace('\r', '').replace('\n', '')
                document['lemmaText'] = lemmaText
                document['date'] = elem[2]
                document['author'] = elem[3]
                document['words'] = words
                # geo location [x, y]
                document['geoLocation'] = elem[4].split(' ')
                # author age
                # this are the change required for the moment when we will keep age as a number
                # age = elem[5].split('-')
                # document['age'] = int(age[1]) - int(age[0])
                document['age'] = elem[5]

                # this are the changes required for the moment when we will keep gender as a number
                # author gender - 1 male, 2 female, 0 unknown
                # document['gender'] = gender.get(elem[6], 0)
                document['gender'] = elem[6]

                if attags:
                    document['attags'] = attags
                if hashtags:
                    document['hashtags'] = hashtags
    except Exception as e:
        print e
    return document

# process one element parallel
def processElement_parallel(elem):
    document = dict()
    if len(elem) >= 7:
        # get language
        if len(elem) >= 8:
            lang = elem[7]
        else:
            global language_global
            lang = language_global
        # get clean text
        try:
            cleanText, hashtags, attags = ct.cleanText(elem[1], lang)
            # if clean text exists
            if len(ct.removePunctuation(cleanText)) > 0:
                # extract lemmas and part of speech
                global mode_global
                lemmas = LemmatizeText(rawText=ct.removePunctuation(cleanText), language=lang, mode=mode_global)
                lemmas.createLemmaText()
                lemmaText = lemmas.cleanText
                if lemmaText and lemmaText != " ":
                    lemmas.createLemmas()
                    words = []
                    for w in lemmas.wordList:
                        word = dict()
                        word['word'] = w.word
                        word['tf'] = w.tf
                        word['count'] = w.count
                        word['pos'] = w.wtype
                        words.append(word)

                    # named entities:
                    ner = NamedEntitiesRegonizer(text=cleanText, language=lang)
                    ner.createNamedEntities()
                    if ner.ner:
                        document['namedEntities'] = ner.ner

                    # construct the document
                    document['_id'] = elem[0]
                    document['rawText'] = elem[1].encode('utf8').encode('string_escape').replace('\r', '').replace('\n', '')
                    document['cleanText'] = cleanText.encode('utf8').encode('string_escape').replace('\r', '').replace('\n', '')
                    document['lemmaText'] = lemmaText
                    document['date'] = elem[2]
                    document['author'] = elem[3]
                    document['words'] = words
                    # geo location [x, y]
                    document['geoLocation'] = elem[4].split(' ')
                    # author age
                    # this are the change required for the moment when we will keep age as a number
                    # age = elem[5].split('-')
                    # document['age'] = int(age[1]) - int(age[0])
                    document['age'] = elem[5]

                    # this are the changes required for the moment when we will keep gender as a number
                    # author gender - 1 male, 2 female, 0 unknown
                    # document['gender'] = gender.get(elem[6], 0)
                    document['gender'] = elem[6]

                    if attags:
                        document['attags'] = attags
                    if hashtags:
                        document['hashtags'] = hashtags
        except Exception as e:
            print e
    return document
