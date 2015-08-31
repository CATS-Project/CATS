# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

# This class is not used anymore
# the model has been moved to indexing

from mongoengine import *
from datetime import datetime
from bson.objectid import ObjectId
import pymongo


def connectDB(dbname='TwitterDB'):
    connect(dbname, host="127.0.0.1", port=27017, read_preference=True)


class Word(EmbeddedDocument):
    _auto_id_field = False
    word = StringField(max_length=255)
    pos = ListField()
    count = FloatField()
    tf = FloatField()
    idf = FloatField()

    meta = {
        'ordering': ['+word']
    }

class NamedEntities(EmbeddedDocument):
    _auto_id_field = False
    type = StringField()
    entity = StringField()

    meta = {
        'ordering': ['+entity']
    }

class Documents(Document):
    _auto_id_field = False
    # tweetID = StringField(max_length=255, required=True, unique=True) this is the _id field
    rawText = StringField()
    cleanText = StringField()  # intermediate text without stopwords, punctuation, etc
    lemmaText = StringField()  # lemma text
    # the date the element was inserted in the database
    createdAt = DateTimeField(default=datetime.now)
    gender = StringField()
    hashtags = ListField()
    attags = ListField()
    date = DateTimeField()
    language = StringField()
    words = ListField(EmbeddedDocumentField("Word"))
    namedEntities = ListField(EmbeddedDocumentField("NamedEntities"))
    tags = ListField()
    geoLocation = ListField()  # geo location, list with 2 elements: [x, y]
    author = StringField() # author ID
    gender = StringField()  # male or female
    age = StringField()  # age of author given as a range

    meta = {
        'ordering': ['+createdAt']
    }


class Docs(EmbeddedDocument):
    _auto_id_field = False
    docID = ObjectIdField()
    count = FloatField()
    tf = FloatField()
    wtype = StringField(max_length=255)


class Vocabulary(Document):
    word = StringField(max_length=255, required=True, unique=True)
    idf = FloatField()
    # wtype = StringField(max_length = 255, required = True) #not yet implemented
    createdAt = DateTimeField(default=datetime.now)
    docIDs = ListField(EmbeddedDocumentField("Docs"))

    meta = {
        'indexes': [
            {
                'fields': ['+word'],
                'unique': True,
                'sparse': False
            }
        ]
    }

class InvertedIndex(Document):
    word = StringField(max_length=255, required=True, unique=True)
    docIDs = ListField()
    createdAt = DateTimeField(default=datetime.now)

    meta = {
        'ordering': ['+createdAt']
    }


