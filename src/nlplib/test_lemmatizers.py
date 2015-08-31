from gensim.utils import lemmatize
from pattern.en import parse
from nltk import word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from clean_text import CleanText
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from time import time

ct = CleanText()
wnl = WordNetLemmatizer()

def gensimTest(text):
    print 'gensim'
    start = time()
    lemmas = lemmatize(text)
    for lemma in lemmas:
        lemma = lemma.split('/')
        print lemma[0], lemma[1]
    end = time()
    print 'gensim time:', (end-start)
    print "********************************"

def replacePos(pos):
    pos = pos[0].lower().replace('j', 'a')
    if pos in ['n', 'a', 'v', 'r']:
        return pos
    return 'n'

def nltkTest(text):
    print 'nltk'
    start = time()
    tagged_words = pos_tag(word_tokenize(text))
    for word in tagged_words:
        print wnl.lemmatize(word[0], pos=replacePos(word[1])), word[1][:2]
    end = time()
    print 'nltk time:', (end-start)
    print "********************************"

def nltkMultiTest(text):
    print 'nltk multi-threading'
    start = time()
    workers = cpu_count()
    tagged_words = pos_tag(word_tokenize(text))

    with ThreadPoolExecutor(max_workers = workers) as e:
        for word in tagged_words:
            result = e.submit(wnl.lemmatize, word[0], replacePos(word[1]))
            print result.result(), word[1][:2]

    end = time()
    print 'nltk multi-threading time:', (end-start)
    print "********************************"

def patternTest(text):
    print 'pattern'
    start = time()
    pattern_text = parse(text, tags = False, chunks = False, lemmata=True).split()
    for word in pattern_text[0]:
        print word[2], word[1][:2]
    end = time()
    print 'pattern time:', (end-start)
    print "********************************"


#these are just tests
if __name__ == '__main__':
    text = "he is literally so scary, good on Reggie for doing it, must have took some guts! i had be shitting bricks!"
    #text1 = "he is literally so scary, good on Reggie for doing it, must have took some guts! i would be shitting bricks!"
    #text2 = "he is literally so scary, good on Reggie for doing it, must have took some guts! i would be shitting bricks!"
    #text3 = "he is literally so scary, good on Reggie for doing it, must have took some guts! i would be shitting bricks!"
    #text4 = "he is literally so scary, good on Reggie for doing it, must have took some guts! i would be shitting bricks! "
    text = ct.removePunctuation(ct.removeStopWords(text.lower(), 'EN'))
    #text1 = ct.removePunctuation(ct.removeStopWords(text1.lower(), 'EN'))
    #text2 = ct.removePunctuation(ct.removeStopWords(text2.lower(), 'EN'))
    #text3 = ct.removePunctuation(ct.removeStopWords(text3.lower(), 'EN'))
    #text4 = ct.removePunctuation(ct.removeStopWords(text4.lower(), 'EN'))
    gensimTest(text)
    patternTest(text)
    nltkTest(text)
    nltkTest(text)
    nltkMultiTest(text)

