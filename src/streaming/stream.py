__author__ = "Adrien Guille"
__license__ = "GNU GPL"
__version__ = "0.1"
__email__ = "adrien.guille@univ-lyon2.fr"
__status__ = "Production"

from twitter import *
import datetime
import threading
import subprocess

tweets_per_file = 500


def quote(string):
    return '"'+string.encode('utf-8')+'"'


class Streaming:
    def __init__(self, dbname='TwitterDBTest', host='localhost', port=27017):
        self.db_name = dbname
        self.host = host
        self.port = port

    def threadUpdate(self,filename):
        print('Importing',filename,'...')
        filepath = 'streaming/data/'+str(filename)+'.csv'
        if filename == 1:
            subprocess.call(['sh','stream_run.sh', filepath, self.db_name, self.host, self.port])
        else:
            subprocess.call(['sh','stream_update.sh', filepath, self.db_name, self.host, self.port])
        print('Done.')

    def collect_tweets(self, duration=1, keys=None, follow=None, loc=None, lang='en'):
        nb_tweets = 0
        nb_tweets_infile = 0
        nb_files = 1
        last_import_day = datetime.datetime.now().day
        file = open('streaming/data/'+str(nb_files)+'.csv', 'w')
        auth = OAuth(
            consumer_key=str(open('streaming/consumer_key','r').read()),
            consumer_secret=str(open('streaming/consumer_secret','r').read()),
            token=str(open('streaming/token','r').read()),
            token_secret=str(open('streaming/token_secret','r').read())
        )
        twitter_stream = TwitterStream(auth=auth)
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=int(duration))
        if keys != "":
            print("keywords")
            iterator = twitter_stream.statuses.filter(track=keys, language=lang)
        elif follow != "":
            print("users")
            iterator = twitter_stream.statuses.filter(follow=follow, language=lang)
        elif loc != "":
            print("location")
            iterator = twitter_stream.statuses.filter(locations=loc, language=lang)
        else:
            print("sample")
            iterator = twitter_stream.statuses.sample(language=lang)
        for tweet in iterator:
            try:
                if tweet.get('text'):
                    print tweet
                    text = tweet['text']
                    text = text.replace('"',' ')
                    text = quote(text.replace('\n',' '))
                    geo = ''
                    if(tweet.get('geo')):
                        geo = str(tweet['geo']['coordinates'][0])+','+str(tweet['geo']['coordinates'][1])
                    geo = quote(geo)
                    timestamp = quote(datetime.datetime.fromtimestamp(float(tweet['timestamp_ms'])/1000).strftime('%Y-%m-%d %H:%M:%S'))
                    nb_tweets += 1
                    nb_tweets_infile += 1
                    description = ''
                    if(tweet['user'].get('description')):
                        description = tweet['user']['description']
                        description = description.replace('"',' ')
                        description = description.replace('\n',' ')
                    description = quote(description)
                    name = ''
                    if(tweet['user'].get('name')):
                        name = tweet['user']['name']
                    name = quote(name)
                    file.write(quote(str(tweet['id']))+'\t'+text+'\t'+timestamp+'\t'+quote(str(tweet['user']['id']))+'\t'+geo+'\t'+description+'\t'+name+'\t'+quote(tweet['lang'].upper())+'\n')
                    if datetime.datetime.now().hour == 0:
                        if not datetime.datetime.now().day == last_import_day:
                            last_import_day = datetime.datetime.now().day
                            current_date = datetime.date.today()
                            t = threading.Thread(target=self.threadUpdate, args=(nb_files,))
                            t.start()
                            if current_date <= end_date:
                                nb_files += 1
                                nb_tweets_infile = 0
                                file = open('streaming/data/'+str(nb_files)+'.csv', 'a')
                            else:
                                break
            except:
                print 'exception: ', tweet

if __name__ == '__main__':
    s = Streaming(dbname='TwitterDBTest')
    keywords = 'obama,hollande'
    s.collect_tweets(keys=keywords)
