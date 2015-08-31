# coding: utf-8

__author__ = "Ciprian-Octavian Truică"
__copyright__ = "Copyright 2015, University Politehnica of Bucharest"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "ciprian.truica@cs.pub.ro"
__status__ = "Production"

from clean_text import CleanText
from pattern.fr import parse as parseFR
from pattern.en import parse as parseEN
from nltk import word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer

ct = CleanText()
wnl = WordNetLemmatizer()

#TO_DO modify this class to accept french also
class LemmatizeText:
    class Word:
        def __init__(self):
            self.word = ""
            self.wtype = []
            self.count = 0
            self.tf = 0.0
    #mode: 0 - fast but not accurate, 1 - slow but accurate (works only for english)
    def __init__(self, rawText, language='EN', mode=0):
        self.wordList = []
        self.rawText = rawText
        self.cleanText = ""    
        self.words = []
        self.language = language
        self.mode = mode

    def createLemmaText(self):
        text = self.rawText
        text = text.lower()
        text = ct.removeStopWords(text, self.language)
        text = ct.removePunctuation(text)
        if self.language == 'EN':
            if self.mode == 0: #fast but not accurate
                text = parseEN(text, tags = False, chunks = False, lemmata=True).split()
            elif self.mode == 1: #slow but accurate
                text = pos_tag(word_tokenize(text))
        elif self.language == 'FR':
            text = parseFR(text, tags = False, chunks = False, lemmata=True).split()
        try:
            if text:
                if self.mode == 0 or self.language =='FR':#fast but not accurate
                    for word in text[0]:
                        self.words.append((word[2].lower(), word[1][:2]))
                elif self.mode == 1 and self.language == 'EN': #slow but accurate
                    for word in text:
                        pos = word[1][0].lower().replace('j', 'a')
                        if not pos in ['n', 'a', 'v', 'r']:
                            pos = 'n'
                        self.words.append((wnl.lemmatize(word[0], pos), word[1][:2]))
                self.cleanText = ' '.join(word[0] for word in self.words)
        except Exception as e:
            print e, self.rawText


    def createLemmas(self):
        if self.cleanText:
            for word in self.words:
                self.append(word[0], word[1])
            #sort wordList by word count
            self.wordList = sorted(self.wordList, key=lambda word: word.count)
            #calculate TF
            maxF = float(self.wordList[-1].count)
            for idx in xrange(0,len(self.wordList), 1):
                self.wordList[idx].tf = round(0.5 + (0.5 * float(self.wordList[idx].count))/maxF, 2)

    def append(self, word, wtype):
        if word:
            if not self.wordList:
                newWord = self.Word()
                newWord.count = 1
                newWord.word = word
                newWord.wtype = []
                newWord.wtype.append(wtype)
                self.wordList.append(newWord)
            else:
                notInList = True
                for idx in xrange(0,len(self.wordList), 1):
                    if word == self.wordList[idx].word:
                        if wtype not in self.wordList[idx].wtype:
                            self.wordList[idx].wtype.append(wtype)
                        self.wordList[idx].count += 1
                        notInList = False
                        break
                if notInList:
                    newWord = self.Word()
                    newWord.count = 1
                    newWord.word = word
                    newWord.wtype = []
                    newWord.wtype.append(wtype)
                    self.wordList.append(newWord)
    #testing
    def printList(self):
        for words in self.wordList:
            print words.word, "pos", words.wtype, "count:", words.count, "TF:", words.tf


# these are just tests
if __name__ == '__main__':
    lt1 = LemmatizeText('John has a cats', language='EN')
    lt1.createLemmaText()
    lt1.createLemmas()
    lt1.printList()
    lt2 = LemmatizeText('John has a cats', language='EN', mode=1)
    lt2.createLemmaText()
    lt2.createLemmas()
    lt2.printList()
    lt3 = LemmatizeText('Julien a un chat', language='FR')
    lt3.createLemmaText()
    lt3.createLemmas()
    lt3.printList()
    lt4 = LemmatizeText('Julien a un chat', language='FR', mode=1)
    lt4.createLemmaText()
    lt4.createLemmas()
    lt4.printList()