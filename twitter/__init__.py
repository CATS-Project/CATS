# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

import os
package_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
os.sys.path.append(package_dir)

#this is the init file for the project
__all__ = ['inverting', 'mllib', 'nlplib', 'models']

"""
import indexing
import nlplib
import mllib
import models


import twitter.indexing.vocabulary_index
import twitter.nlplib.clean_text
import twitter.nlplib.lemmatize_text
import twitter.nlplib.named_entities
import twitter.mllib.market_matrix
import twitter.mllib.topic_modeling
import twitter.models.mongo_models
"""