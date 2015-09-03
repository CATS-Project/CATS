__author__ = "Adrien Guille"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "adrien.guille@univ-lyon2.fr"
__status__ = "Production"

from flask import Flask, Response, render_template, request
from search_mongo_new import Search
from nlplib.lemmatize_text import LemmatizeText
from mllib.train_lda import TrainLDA
from mabed.mabed_files import MabedFiles
import subprocess
import os
import shutil
from functools import wraps
import threading
import pickle
from streaming.stream import Streaming
import datetime
from indexing.queries import Queries

# Connecting to the database

db_name = 'TwitterDB_demo'
host = 'localhost'
port = 27017
queries = Queries(dbname=db_name, host=host, port=port)
can_collect_tweets = False
lda_running = False
mabed_running = False

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


def get_tweet_count():
    return queries.countDocuments(query=query)


@app.route('/cats/collection')
def collection_dashboard_page():
    print db_name, can_collect_tweets
    if can_collect_tweets and os.path.isfile('collecting.lock'):
        lock = open('collecting.lock', 'r').read()
        corpus_info = lock.split(';')
        return render_template('collection.html', collecting_corpus=corpus_info)
    elif not can_collect_tweets:
        lock = open('demonstration.info', 'r').read()
        corpus_info = lock.split(';')
        return render_template('collection.html', collected_corpus=corpus_info)
    else:
        return render_template('collection.html')


@app.route('/cats/collection', methods=['POST'])
@requires_auth
def collection_dashboard_page2():
    if can_collect_tweets and not os.path.isfile('collecting.lock'):
        lock = open("collecting.lock", "w")
        checked_lang = request.form.getlist('lang')
        lang = checked_lang[0]
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
        t = threading.Thread(target=collection_thread, args=(duration,keywords,users,location,lang,))
        t.start()
        return collection_dashboard_page()
    else:
        return render_template('collecting.html')


def collection_thread(duration, keywords, users, location, language):
    s = Streaming(dbname=db_name)
    s.collect_tweets(duration=duration, keys=keywords, follow=users, loc=location, lang=language)


@app.route('/cats/analysis')
@requires_auth
def analysis_dashboard_page():
    print db_name
    tweet_count = get_tweet_count()
    dates = ""
    keys = ""
    if query.get("words.word"):
        keys = ' '.join(query["words.word"].get("$in"))
    if query.get("date"): 
        dates = query["date"].get("$gt")+' '+query["date"].get("$lte")
    return render_template('analysis.html', tweetCount=tweet_count, dates=dates, keywords=keys)


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
    word_list = []
    for word in lem.wordList:
        word_list.append(word.word)
    global query
    query = {}
    global query_pretty
    query_pretty = ""
    if word_list:
        query_pretty += "Keyword filter: "+' '.join(word_list)+"<br/>"
        query["words.word"] = {"$in": word_list }
    if date:
        query_pretty += "Date filter: "+date+"<br/>"
        start, end = date.split(" ") 
        query["date"] = {"$gt": start, "$lte": end }
    if checked_ages and 0 < len(checked_ages) < 6:
        query_pretty += "Age filter: "+' '.join(checked_ages)+"<br/>"
        query["age"] = {"$in": checked_ages }
    if checked_genders and len(checked_genders) == 1:
        query_pretty += "Gender filter: "+' '.join(checked_genders)+"<br/>"
        query["gender"] = checked_genders[0]
    if query:
        queries.constructVocabulary(query=query)
    tweet_count = get_tweet_count()
    return render_template('analysis.html', tweetCount=tweet_count, dates=date, keywords=' '.join(word_list))


@app.route('/cats/about')
def about_page():
    return render_template('about.html', name=name)


@app.route('/cats/analysis/construct_vocabulary')
def construct_vocabulary():
    print("constructing vocab")	
    queries.constructVocabulary()
    return analysis_dashboard_page()


@app.route('/cats/analysis/vocabulary_cloud')
def get_term_cloud():
    if query:
        voc = queries.getWords(fields={'word': 1,'IDF': 1}, limit=150, existing=True)
    else:
        voc = queries.getWords(fields={'word': 1,'IDF': 1}, limit=150, existing=False)
    return render_template('word_cloud.html', voc=voc, filter=query_pretty)     


@app.route('/cats/analysis/vocabulary.csv')
def get_term_list():
    if query:
        voc = queries.getWords(fields={'word': 1,'IDF': 1}, limit=1000, existing=True)
    else:
        voc = queries.getWords(fields={'word': 1,'IDF': 1}, limit=1000, existing=False)
    csv = 'word,IDF\n'
    for doc in voc :
        print doc['word'], doc['IDF']
        csv += doc['word']+','+str(doc['IDF'])+'\n'
    return Response(csv,mimetype="text/csv")   


@app.route('/cats/analysis/tweets',methods=['POST'])
def get_tweet_list():
    phrase = request.form['cooccurringwords']
    search = Search(searchPhrase=phrase, dbname=db_name, host=host, port=port, query=query)
    results = search.results()
    for i in range(len(results)):
        result = results[i]
        result['rawText'] = result['rawText'].replace('\\', '')
        results[i] = result
    return render_template('tweet_browser.html', results=results, filter=query_pretty)


def namedEntities(limit=None):
    return queries.getNamedEntities(query=query, limit=limit)


@app.route('/cats/analysis/named_entities.csv')
def get_named_entity_list():
    cursor = namedEntities()
    csv='named_entity,count,type\n'
    for elem in cursor:
        csv += elem['entity'].encode('utf8')+','+str(elem['count'])+','+elem['type']+'\n'
    return Response(csv,mimetype="text/csv") 


@app.route('/cats/analysis/named_entity_cloud')
def get_named_entity_cloud():
    return render_template('named_entity_cloud.html', ne=namedEntities(250), filter=query_pretty)


@app.route('/cats/analysis/train_lda', methods=['POST'])
def train_lda():
    if not lda_running:
        k = int(request.form['k-lda'])
        t = threading.Thread(target=thread_lda, args=(k,))
        t.start()
        return render_template('waiting.html',method_name='LDA')
    else:
        return render_template('already_running.html',method_name='LDA')


def thread_lda(k):
    global lda_running
    lda_running = True
    lda = TrainLDA(dbname=db_name, host=host, port=port)
    results = lda.fitLDA(query=query, num_topics=k, num_words=10, iterations=500)
    scores = [0]*k
    for doc in results[1]:
        for topic in doc:
            scores[int(topic[0])] += float(topic[1])
    topics = []
    for i in range(0,k):
        print(results[0][i])
        topics.append([i, scores[i], results[0][i]])
    lda_running = False
    pickle.dump(topics, open("lda_topics.p", "wb"))
    pickle.dump(query_pretty, open("lda_query.p", "wb"))


@app.route('/cats/analysis/detect_events',methods=['POST']) 
def run_mabed():
    if not mabed_running:
        k = int(request.form['k-mabed'])
        t = threading.Thread(target=thread_mabed, args=(k,))
        t.start()
        return render_template('waiting.html',method_name='MABED')
    else:
        return render_template('already_running.html',method_name='MABED')


def thread_mabed(k):
    global mabed_running
    mabed_running = True
    for the_file in os.listdir('mabed/input'):
        file_path = os.path.join('mabed/input', the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception, e:
            print e
    mf = MabedFiles(dbname=db_name, host=host, port=port)
    mf.buildFiles(query, filepath='mabed/input/', slice=60*60)
    result = subprocess.check_output(['java', '-jar', './mabed/MABED-CATS.jar', '60', str(k)])
    mabed_running = False
    pickle.dump(result, open("mabed_events.p", "wb"))
    pickle.dump(query_pretty, open("mabed_query.p", "wb"))


@app.route('/cats/analysis/lda_topics.csv')
def get_topics():
    return ""   


@app.route('/cats/analysis/lda_topic_browser')
def browse_topics():
    if lda_running:
        return render_template('waiting.html', method_name='LDA')
    elif os.path.isfile('lda_topics.p'):
        r = pickle.load(open("lda_topics.p", "rb"))
        qp = pickle.load(open("lda_query.p", "rb"))
        return render_template('topic_browser.html', topics=r, filter=qp)
    else:
        return render_template('unavailable.html', method_name='LDA')


@app.route('/cats/analysis/mabed_events.csv')
def get_events():
    return ""


@app.route('/cats/analysis/mabed_event_browser')
def browse_events():
    if mabed_running:
        return render_template('waiting.html', method_name='MABED')
    elif os.path.isfile('mabed_events.p'):
        r = pickle.load(open("mabed_events.p", "rb"))
        qp = pickle.load(open("mabed_query.p", "rb"))
        return render_template('event_browser.html', events=r, filter=qp)
    else:
        return render_template('unavailable.html', method_name='MABED')
        
if __name__ == '__main__':
    # Demo
    app.run(debug=True, host='mediamining.univ-lyon2.fr', port=5000)
