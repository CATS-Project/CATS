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
    def __init__(self, dbname='TwitterDBTest'):
        self.db_name = dbname

    def threadUpdate(self,filename):
        print('Importing',filename,'...')
        filepath = 'streaming/data/'+str(filename)+'.csv'
        if filename == 1:
            subprocess.call(['sh','stream_run.sh',self.db_name,filepath])
        else:
            subprocess.call(['sh','stream_update.sh',self.db_name,filepath])
        print('Done.')

    def collect_tweets(self, duration=1, keys=None, follow=None, loc=None):
        nb_tweets = 0
        nb_tweets_infile = 0
        nb_files = 1
        last_import_day = datetime.datetime.now().day
        file = open('streaming/data/'+str(nb_files)+'.csv', 'a')
        auth = OAuth(
            consumer_key=str(open('streaming/consumer_key','r').read()),
            consumer_secret=str(open('streaming/consumer_secret','r').read()),
            token=str(open('streaming/token','r').read()),
            token_secret=str(open('streaming/token_secret','r').read())
        )
        twitter_stream = TwitterStream(auth=auth)
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=int(duration))
        lock = open("collection.lock", "w")
        if keys != "":
            print("keywords")
            lock.write(str(datetime.date.today())+';'+str(duration)+';'+keys+';None;None')
            iterator = twitter_stream.statuses.filter(track=keys)
        elif follow != "":
            print("users")
            lock.write(str(datetime.date.today())+';'+str(duration)+';None;',follow+';None')
            iterator = twitter_stream.statuses.filter(follow=follow)
        elif loc != "":
            print("location")
            lock.write(str(datetime.date.today())+';'+str(duration)+';None;None;'+loc)
            iterator = twitter_stream.statuses.filter(locations=loc)
        else:
            print("sample")
            lock.write(str(datetime.date.today())+';'+str(duration)+';None;None;None')
            iterator = twitter_stream.statuses.sample()
        lock.close()
        for tweet in iterator:
            if tweet.get('text'):
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
                #if(datetime.datetime.now().hour == 0):
                    #if(not datetime.now().day == last_import_day):
                if nb_tweets_infile == tweets_per_file:
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

if __name__ == '__main__':
    s = Streaming(dbname='TwitterDBTest')
    keywords = 'obama,hollande'
    users = '7302282,14857290,133663801'
    location = '-122.75,36.8,-121.75,37.8'
    s.collect_tweets(keys=keywords)