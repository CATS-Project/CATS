__author__ = "Adrien Guille"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "adrien.guille@univ-lyon2.fr"
__status__ = "Production"

from flask import Flask, Response, render_template, request
from indexing.vocabulary_index import VocabularyIndex
from search_mongo import Search
import pymongo
from nlplib.lemmatize_text import LemmatizeText
from indexing.ne_index import NEIndex
from mllib.train_lda import TrainLDA
from mabed.mabed_files import MabedFiles
import subprocess
import os, shutil
from functools import wraps
import threading
import pickle
from streaming.stream import Streaming
import datetime

# Connecting to the database
client = pymongo.MongoClient()
dbname = 'TwitterDB_demo'
db = client[dbname]
can_collect_tweets = False

app = Flask(__name__)

query = {}

query_pretty = ""

def check_auth(username, password):
    return username == 'demo' and password == 'ilikecats'

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def getTweetCount():
    return db.documents.find(query).count()

@app.route('/cats/collection')
def collection_dashboard_page(name=None):
    print dbname, can_collect_tweets
    if can_collect_tweets and os.path.isfile('collecting.lock'):
        lock = open('collecting.lock','r').read()
        corpus_info = lock.split(';')
        return render_template('collection.html', collecting_corpus=corpus_info)
    elif not can_collect_tweets:
        lock = open('demonstration.info','r').read()
        corpus_info = lock.split(';')
        return render_template('collection.html', collected_corpus=corpus_info)
    else:
        return render_template('collection.html')

@app.route('/cats/collection', methods=['POST'])
@requires_auth
def collection_dashboard_page2():
    if can_collect_tweets and not os.path.isfile('collecting.lock'):
        lock = open("collecting.lock", "w")
        if request.form.get('collection_duration'):
            duration = int(request.form.get('collection_duration'))
        else:
            duration = 1
        if request.form.get('keyword_list'):
            keywords = request.form.get('keyword_list')
            lock.write(str(datetime.date.today())+';'+str(duration)+';'+keywords+';None;None')
        else:
            keywords = ""
        if request.form.get('user_list'):
            users = request.form.get('user_list')
            lock.write(str(datetime.date.today())+';'+str(duration)+';None;None;'+users)
        else:
            users = ""
        if request.form.get('bounding_box'):
            location = request.form.get('bounding_box')
            lock.write(str(datetime.date.today())+';'+str(duration)+';None;'+location+';None')
        else:
            location = ""
        lock.close()
        t = threading.Thread(target=threadCollection, args=(duration,keywords,users,location,))
        t.start()
        lock = open('collecting.lock','r').read()
        corpus_info = lock.split(';')
        return collection_dashboard_page()
    else:
        return render_template('collecting.html')

def threadCollection(duration,keywords,users,location):
    s = Streaming(dbname=dbname)
    s.collect_tweets(duration=duration, keys=keywords, follow=users, loc=location)

@app.route('/cats/analysis')
@requires_auth
def analysis_dashboard_page(name=None):
    print dbname
    tweetCount = getTweetCount()
    dates = ""
    keys = ""
    if query.get("words.word"):
        keys = ' '.join(query["words.word"].get("$in"))
    if query.get("date"): 
        dates = query["date"].get("$gt")+' '+query["date"].get("$lte")
    return render_template('analysis.html', tweetCount=tweetCount, dates=dates, keywords=keys)  

@app.route('/cats/analysis', methods=['POST'])
@requires_auth
def analysis_dashboard_page2():
    keywords = request.form['keyword']
    date = request.form['date']
    checked_genders = request.form.getlist('gender')
    checked_ages = request.form.getlist('age')
    print date,keywords,checked_genders,checked_ages
    lem = LemmatizeText(keywords)
    lem.createLemmaText()
    lem.createLemmas()
    wordList = []
    for word in lem.wordList:
        """
            If you want to use a regex,
            This example will construct a regex that contains the lemma
            similar in SQL to -> where word like '%fuck%'
        """
        #regex = re.compile(word.word, re.IGNORECASE)
        #wordList.append(regex)
        """
            this one will find only the tweets with the matching word
        """
        wordList.append(word.word)
    global query
    query = {}
    global query_pretty
    query_pretty = ""
    if wordList:
        query_pretty += "Keyword filter: "+' '.join(wordList)+"<br/>"
        query["words.word"] = { "$in": wordList }
    if date:
        query_pretty += "Date filter: "+date+"<br/>"
        start, end = date.split(" ") 
        query["date"] = { "$gt": start, "$lte": end }
    if checked_ages and 0 < len(checked_ages) < 6:
        query_pretty += "Age filter: "+' '.join(checked_ages)+"<br/>"
        query["age"] = { "$in": checked_ages }
    if checked_genders and len(checked_genders) == 1:
        query_pretty += "Gender filter: "+' '.join(checked_genders)+"<br/>"
        query["gender"] = checked_genders[0]
    if query:
        vocab = VocabularyIndex(dbname)
        vocab.createIndex(query)
    tweetCount = getTweetCount()
    return render_template('analysis.html', tweetCount=tweetCount, dates=date, keywords=' '.join(wordList))  
    
@app.route('/cats/about')
def about_page(name=None):
    return render_template('about.html', name=name)

@app.route('/cats/analysis/construct_vocabulary')
def construct_vocabulary():
    print("constructing vocab")	
    vocab = VocabularyIndex(dbname)
    vocab.createIndex()
    return analysis_dashboard_page()

@app.route('/cats/analysis/vocabulary_cloud')
def getTermCloud():
    if query:
        voc = db.vocabulary_query.find(fields={'word':1,'idf':1},limit=150, sort=[('idf',pymongo.ASCENDING)])
    else:
        voc = db.vocabulary.find(fields={'word':1,'idf':1},limit=150, sort=[('idf',pymongo.ASCENDING)])
    return render_template('word_cloud.html', voc=voc, filter=query_pretty)     
    
@app.route('/cats/analysis/vocabulary.csv')
def getTerms():
    if query:
        voc = db.vocabulary_query.find(fields={'word':1,'idf':1}, limit=1000, sort=[('idf',pymongo.ASCENDING)])
    else:
        voc = db.vocabulary.find(fields={'word':1,'idf':1}, limit=1000, sort=[('idf',pymongo.ASCENDING)])
    csv = 'word,idf\n'
    for doc in voc :
        csv += doc['word']+','+str(doc['idf'])+'\n'
    return Response(csv,mimetype="text/csv")   

@app.route('/cats/analysis/tweets',methods=['POST'])
def getTweets():
    searchPhrase = request.form['cooccurringwords']
    query_exists = False
    if query:
        query_exists = True
    search = Search(searchPhrase=searchPhrase, dbname=dbname, query=query_exists)
    results = search.results()
    return render_template('tweet_browser.html', results=results, filter=query_pretty) 

def namedEntities(limit=None):
    if query:
        # if there is a query then we construct a smaller NE_INDEX
        query_ner = {'namedEntities': {'$exists': 'true'}}
        query_ner.update(query)
        ne = NEIndex(dbname)
        ne.createIndex(query_ner)
        if limit:
            cursor = db.named_entities_query.find(sort=[('count',pymongo.DESCENDING)], limit=limit)
        else:
            cursor = db.named_entities_query.find(sort=[('count',pymongo.DESCENDING)])
    else:
        # use the already build NE_INDEX
        if limit:
            cursor = db.named_entities.find(sort=[('count',pymongo.DESCENDING)], limit=limit)
        else:
            cursor = db.named_entities.find(sort=[('count',pymongo.DESCENDING)])
    return cursor

@app.route('/cats/analysis/named_entities.csv')
def getNamedEntities():
    cursor = namedEntities()
    csv='named_entity,count,type\n'
    for elem in cursor:
        csv += elem['entity'].encode('utf8')+','+str(elem['count'])+','+elem['type']+'\n'
    return Response(csv,mimetype="text/csv") 
    
@app.route('/cats/analysis/named_entity_cloud')
def getNamedEntityCloud():
    return render_template('named_entity_cloud.html', ne=namedEntities(250), filter=query_pretty)
    
@app.route('/cats/analysis/train_lda',methods=['POST'])
def trainLDA():
    if not os.path.isfile('lda.lock'):
        k = int(request.form['k-lda'])
        t = threading.Thread(target=threadLDA, args=(k,))
        t.start()
        return render_template('waiting.html',method_name='LDA')
    else:
        return render_template('already_running.html',method_name='LDA')
   
def threadLDA(k):
    file = open("lda.lock", "w")
    file.write(" ")
    file.close()
    print "Training LDA..."
    lda = TrainLDA(dbname=dbname)
    results = lda.fitLDA(query=query, num_topics=k, num_words=10, iterations=500)
    scores = [0]*k
    for doc in results[1]:
        for topic in doc:
            scores[int(topic[0])] += float(topic[1])
    topics = []
    for i in range(0,k):
        print(results[0][i])
        topics.append([i,scores[i],results[0][i]])
    print "Done."
    os.remove('lda.lock')
    pickle.dump(topics,open("lda_topics.p","wb"))  
    pickle.dump(query_pretty,open("lda_query.p","wb"))  
       
@app.route('/cats/analysis/detect_events',methods=['POST']) 
def runMABED():
    if not os.path.isfile('mabed.lock'):
        k = int(request.form['k-mabed'])
        t = threading.Thread(target=threadMABED, args=(k,))
        t.start()
        return render_template('waiting.html',method_name='MABED')
    else:
        return render_template('already_running.html',method_name='MABED')
    
def threadMABED(k):
    file = open("mabed.lock", "w")
    file.write(" ")
    file.close()
    print "Running MABED..."
    for the_file in os.listdir('mabed/input'):
        file_path = os.path.join('mabed/input', the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception, e:
            print e
    mf = MabedFiles(dbname=dbname)
    mf.buildFiles(query, filepath='mabed/input/', slice=60*60)
    result = subprocess.check_output(['java', '-jar', './mabed/MABED-CATS.jar', '60', '40'])
    print "Done."
    os.remove('mabed.lock')
    pickle.dump(result,open("mabed_events.p","wb"))  
    pickle.dump(query_pretty,open("mabed_query.p","wb"))
    
@app.route('/cats/analysis/lda_topics.csv')
def getTopics():
    return ""   
    
@app.route('/cats/analysis/lda_topic_browser')
def browseTopics():
    if os.path.isfile('lda.lock'):
        return render_template('waiting.html',method_name='LDA')
    elif os.path.isfile('lda_topics.p'):
        r = pickle.load(open("lda_topics.p","rb"))
        qp = pickle.load(open("lda_query.p","rb"))
        return render_template('topic_browser.html', topics=r, filter=qp)
    else:
        return render_template('unavailable.html',method_name='LDA')
    
@app.route('/cats/analysis/mabed_events.csv')
def getEvents():
    return ""
    
@app.route('/cats/analysis/mabed_event_browser')
def browseEvents():
    if os.path.isfile('mabed.lock'):
        return render_template('waiting.html',method_name='MABED')
    elif os.path.isfile('mabed_events.p'):
        r = pickle.load(open("mabed_events.p","rb"))
        qp = pickle.load(open("mabed_query.p","rb"))
        return render_template('event_browser.html', events=r, filter=qp)
    else:
        return render_template('unavailable.html',method_name='MABED')
        
if __name__ == '__main__':
    # Demo
     app.run(debug=True,host='mediamining.univ-lyon2.fr',port=5000)
    # GERiiCO
    # Change dbname to TwitterGERiiCO and can_collect_tweets to True
    # app.run(debug=True,host='mediamining.univ-lyon2.fr',port=5001)