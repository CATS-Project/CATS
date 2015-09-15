__author__ = "Adrien Guille"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "adrien.guille@univ-lyon2.fr"
__status__ = "Production"

from flask import Flask, Response, render_template, request, session, url_for, redirect
from search_mongo import Search
from nlplib.lemmatize_text import LemmatizeText
from mllib.train_lda import LDA
from mllib.train_lsa import LSA
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
import sqlite3


# User database
user_db_filename = 'users.db'

# Tweet database
queries = {}
host = 'localhost'
port = 27017

can_collect_tweets = False

lda_running = False
lsa_running = False
mabed_running = False

app = Flask(__name__)
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'


@app.route('/cats')
def index():
    return ""


@app.route('/cats/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        with sqlite3.connect(user_db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("select password, can_collect_tweets from user where username = '"+request.form['username']+"'")
            row = cursor.fetchone()
            if row is not None:
                password = row[0]
                if request.form['password'] == password:
                    session['name'] = request.form['username']
                    session['query'] = {}
                    session['query_pretty'] = ""
                    session['can_collect_tweets'] = row[1]
                    session['lda_running'] = False
                    session['lsa_running'] = False
                    session['mabed_running'] = False
                    session['lda'] = None
                    session['lsa'] = None
                    session['mabed'] = None
                    queries[session['name']] = Queries(dbname=session['name'], host=host, port=port)
                    print session['name'], 'can collect tweets:', session['can_collect_tweets']
                    cursor.execute("select * from oauth where username = '"+request.form['username']+"'")
                    row = cursor.fetchone()
                    if session['can_collect_tweets'] == 'True' and row is None:
                        print session['name'], ' needs to provide access tokens'
                        return redirect(url_for('initialization_page'))
                    else:
                        return redirect(url_for('collection_dashboard_page'))
                else:
                    error = 'Invalid credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/cats/analysis/tweets.csv', methods=['POST'])
def download_tweets():
    advanced_metadata = request.form.getlist('advanced_metadata')
    if len(advanced_metadata) == 1:
        return "export advanced metadata"
    else:
        return "export basic data"


def get_tweet_count():
    count = queries[session['name']].countDocuments(query=session['query'])
    if count > 0:
        return str(count)+' tweets'
    else:
        return '0 tweet'


@app.route('/cats/initialization', methods=['GET', 'POST'])
def initialization_page():
    if session.get('name') is not None:
        error = None
        if request.method == 'POST':
            consumer_key = request.form['consumer-key']
            consumer_secret = request.form['consumer-secret']
            token = request.form['token']
            token_secret = request.form['token-secret']
            if consumer_key != '' and consumer_secret != '' and token != '' and token_secret != '':
                with sqlite3.connect(user_db_filename) as conn:
                    conn.execute("insert into oauth (username, consumer_key, consumer_secret, token, token_secret) values ('"+session['name']+"','"+consumer_key+"','"+consumer_secret+"','"+token+"','"+token_secret+"')")
                    return redirect(url_for('collection_dashboard_page'))
            else:
                error = 'Invalid tokens. Please try again.'
        return render_template('initialization.html', user=session['name'], error=error)
    else:
        return redirect(url_for('login'))


@app.route('/cats/collection')
def collection_dashboard_page():
    if session.get('name') is not None:
        corpus_info = None
        print 'Looking for corpora collected by', session['name']
        with sqlite3.connect(user_db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("select start, duration, language, keyword, location, user, running from collection where username = '"+session['name']+"'")
            row = cursor.fetchone()
            if row is not None:
                corpus_info = row
            print corpus_info
        return render_template('collection.html', corpus_info=corpus_info, user=session['name'])
    else:
        return redirect(url_for('login'))


@app.route('/cats/collection', methods=['POST'])
def collection_dashboard_page2():
    if session['can_collect_tweets'] == 'True' and not os.path.isfile('collecting.lock'):
        lock = open("collecting.lock", "w")
        checked_lang = request.form.getlist('lang')
        lang = checked_lang[0]
        if request.form.get('collection_duration'):
            duration = int(request.form.get('collection_duration'))
            if duration > 30:
                duration = 30
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
    s = Streaming(dbname=session['name'])
    s.collect_tweets(duration=duration, keys=keywords, follow=users, loc=location, lang=language)


@app.route('/cats/analysis')
def analysis_dashboard_page():
    if session.get('name') is not None:
        tweet_count = get_tweet_count()
        dates = ""
        keys = ""
        if session['query'].get("words.word"):
            keys = ','.join(session['query']["words.word"].get("$in"))
        if session['query'].get("date"):
            dates = session['query']['date'].get("$gt")+' '+session['query']['date'].get("$lte")
        return render_template('analysis.html', tweetCount=tweet_count, dates=dates, keywords=keys, user=session['name'])
    else:
        return redirect(url_for('login'))


@app.route('/cats/analysis', methods=['POST'])
def analysis_dashboard_page2():
    keywords = request.form['keyword']
    date = request.form['date']
    keywords = keywords.replace(',', ' ')
    lem = LemmatizeText(keywords)
    lem.createLemmaText()
    lem.createLemmas()
    word_list = []
    for word in lem.wordList:
        word_list.append(word.word)
    session['query'] = {}
    session['query_pretty'] = ""
    if word_list:
        session['query_pretty'] += "Keyword filter: "+','.join(word_list)+"<br/>"
        session['query']["words.word"] = {"$in": word_list}
    if date:
        session['query_pretty'] += "Date filter: "+date+"<br/>"
        start, end = date.split(" ") 
        session['query']['date'] = {"$gt": start, "$lte": end}
    if session.get('query'):
        queries[session['name']].constructVocabulary(query=session['query'])
    tweet_count = get_tweet_count()
    return render_template('analysis.html', tweetCount=tweet_count, dates=date, keywords=' '.join(word_list), user=session['name'])


@app.route('/cats/about')
def about_page():
    return render_template('about.html')


@app.route('/cats/analysis/construct_vocabulary')
def construct_vocabulary():
    print("constructing vocab")	
    queries[session['name']].constructVocabulary()
    return analysis_dashboard_page()


@app.route('/cats/analysis/vocabulary_cloud')
def get_term_cloud():
    if session.get('name') is not None:
        if session.get('query'):
            voc = queries[session['name']].getWords(fields={'word': 1, 'IDF': 1}, limit=150, existing=True)
        else:
            voc = queries[session['name']].getWords(fields={'word': 1, 'IDF': 1}, limit=150, existing=False)
        return render_template('word_cloud.html', voc=voc, filter=session['query_pretty'])
    else:
        return redirect(url_for('login'))


@app.route('/cats/analysis/vocabulary.csv')
def get_term_list():
    if session.get('name') is not None:
        if session.get('query'):
            voc = queries[session['name']].getWords(fields={'word': 1, 'IDF': 1}, limit=1000, existing=True)
        else:
            voc = queries[session['name']].getWords(fields={'word': 1, 'IDF': 1}, limit=1000, existing=False)
        csv = 'word,IDF\n'
        for doc in voc:
            print doc['word'], doc['IDF']
            csv += doc['word']+','+str(doc['IDF'])+'\n'
        return Response(csv, mimetype="text/csv")
    else:
        return redirect(url_for('login'))


@app.route('/cats/analysis/tweets', methods=['POST'])
def get_tweet_list():
    phrase = request.form['cooccurringwords']
    search = Search(searchPhrase=phrase, dbname=session['name'], host=host, port=port, query=session['query'])
    results = search.results()
    for i in range(len(results)):
        result = results[i]
        result['rawText'] = result['rawText'].replace('\\', '')
        results[i] = result
    return render_template('tweet_browser.html', results=results, filter=session['query_pretty'])


@app.route('/cats/analysis/tweets/<term>')
def get_tweet_list2(term):
    if session.get('name') is not None:
        search = Search(searchPhrase=term, dbname=session['name'], host=host, port=port, query=session['query'])
        results = search.results()
        for i in range(len(results)):
            result = results[i]
            result['rawText'] = result['rawText'].replace('\\', '')
            results[i] = result
        return render_template('tweet_browser.html', results=results, filter=session['query_pretty'])
    else:
        return redirect(url_for('login'))


def extract_named_entities(limit=0):
    return queries[session['name']].getNamedEntities(query=session['query'], limit=limit)


@app.route('/cats/analysis/named_entities.csv')
def get_named_entity_list():
    if session.get('name') is not None:
        cursor = extract_named_entities()
        csv = 'named_entity,count,type\n'
        for elem in cursor:
            csv += elem['entity'].encode('utf8')+','+str(elem['count'])+','+elem['type']+'\n'
        return Response(csv, mimetype="text/csv")
    else:
        return redirect(url_for('login'))


@app.route('/cats/analysis/named_entity_cloud')
def get_named_entity_cloud():
    if session.get('name') is not None:
        return render_template('named_entity_cloud.html', ne=extract_named_entities(250), filter=session['query_pretty'])
    else:
        return redirect(url_for('login'))


@app.route('/cats/analysis/train_lda', methods=['POST'])
def train_lda():
    if not lda_running:
        k = int(request.form['k-lda'])
        t = threading.Thread(target=thread_lda, args=(k,))
        t.start()
        return render_template('waiting.html', method_name='LDA')
    else:
        return render_template('already_running.html', method_name='LDA')


def thread_lda(k):
    global lda_running
    session['lda_running'] = True
    lda = LDA(dbname=session['name'], host=host, port=port)
    results = lda.apply(query=session['query'], num_topics=k, num_words=10, iterations=500)
    scores = [0]*k
    for doc in results[1]:
        for topic in doc:
            scores[int(topic[0])] += float(topic[1])
    topics = []
    for i in range(0, k):
        topics.append([i, scores[i], results[0][i]])
    session['lda_running'] = False
    session['lda'] = topics


@app.route('/cats/analysis/train_lsa', methods=['POST'])
def train_lsa():
    if not lsa_running:
        k = int(request.form['k-lsa'])
        t = threading.Thread(target=thread_lsa, args=(k,))
        t.start()
        return render_template('waiting.html', method_name='LSA')
    else:
        return render_template('already_running.html', method_name='LSA')


def thread_lsa(k):
    global lsa_running
    session['lsa_running'] = True
    lsa = LSA(dbname=session['name'], host=host, port=port)
    results = lsa.apply(query=session['query'], num_topics=k, num_words=10)
    print 'LSA\n', results
    topics = []
    for i in range(0, k):
        topics.append([i, 0, results[i]])
    session['lsa_running'] = False
    session['lsa'] = topics


@app.route('/cats/analysis/detect_events', methods=['POST'])
def run_mabed():
    if not mabed_running:
        k = int(request.form['k-mabed'])
        t = threading.Thread(target=thread_mabed, args=(k,))
        t.start()
        return render_template('waiting.html', method_name='MABED')
    else:
        return render_template('already_running.html', method_name='MABED')


def thread_mabed(k):
    global mabed_running
    session['mabed_running'] = True
    for the_file in os.listdir('mabed/input'):
        file_path = os.path.join('mabed/input', the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception, e:
            print e
    mf = MabedFiles(dbname=session['name'], host=host, port=port)
    mf.buildFiles(session['query'], filepath='mabed/'+session['name']+'/input/', slice=60*60)
    result = subprocess.check_output(['java', '-jar', './mabed/MABED-CATS.jar', '60', str(k)])
    session['mabed_running'] = False
    session['mabed'] = result


@app.route('/cats/analysis/lda_topics.csv')
def get_lda_topics():
    return ""   


@app.route('/cats/analysis/lda_topic_browser')
def browse_lda_topics():
    if session.get('name') is not None:
        if session['lda_running']:
            return render_template('waiting.html', method_name='LDA')
        elif session['lda'] is not None:
            return render_template('topic_browser.html', topics=session['lda'], filter=session['pretty_query'])
        else:
            return render_template('unavailable.html', method_name='LDA')
    else:
        return redirect(url_for('login'))


@app.route('/cats/analysis/lsa_topics.csv')
def get_lsa_topics():
    return ""


@app.route('/cats/analysis/lsa_topic_browser')
def browse_lsa_topics():
    if session.get('name') is not None:
        if session['lsa_running']:
            return render_template('waiting.html', method_name='LSA')
        elif session['lsa'] is not None:
            return render_template('topic_browser.html', topics=session['lsa'], filter=session['pretty_query'])
        else:
            return render_template('unavailable.html', method_name='LSA')
    else:
        login()


@app.route('/cats/analysis/mabed_events.csv')
def get_events():
    return ""


@app.route('/cats/analysis/mabed_event_browser')
def browse_events():
    if session.get('name') is not None:
        if session['mabed_running']:
            return render_template('waiting.html', method_name='MABED')
        elif session['mabed'] is not None:
            return render_template('event_browser.html', events=session['mabed'], filter=session['pretty_query'])
        else:
            return render_template('unavailable.html', method_name='MABED')
    else:
        return redirect(url_for('login'))
        
if __name__ == '__main__':
    # Demo
    app.run(debug=True, host='mediamining.univ-lyon2.fr', port=1988)

