import json
import tweepy
from kafka import KafkaProducer
import os
import time

TOPIC_OLLAS_COMUNES_TWITTER = "ollas-comunes-topic"

# Wait until Kafka server is loaded
time.sleep(30)

# Authenticate to Twitter

auth = tweepy.OAuthHandler(os.environ['CONSUMER_API_KEY'], os.environ["CONSUMER_API_SECRET_KEY"])
auth.set_access_token(os.environ["ACCESS_TOKEN"], os.environ["ACCESS_TOKEN_SECRET"])

# Create API object
api = tweepy.API(auth)

# Creates Kafka producer
ollascomunes_tweets_producer = KafkaProducer(bootstrap_servers='broker:29092')


class MyStreamListener(tweepy.StreamListener):
    i = 0

    def on_status(self, status):
        print('mensaje enviado', self.i, 'RT?', 'retweeted_status' in status._json, flush=True)
        self.i += 1
        # with open(f'data/twitter_query_example/{status._json["id_str"]}.json', 'w+') as outfile:
        #     json.dump(status._json, outfile)
        if 'retweeted_status' not in status._json:
            ollascomunes_tweets_producer.send(TOPIC_OLLAS_COMUNES_TWITTER,
                                              json.dumps(status._json).encode('utf-8'))

    def on_exception(self, exception):
        print(exception)
        return

if __name__ == '__main__':
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
    queries = ['#ollascomunes', '#ollacomun', 'olla comun']  # ollasolidario, menciones a @apoyalaolla
    myStream.filter(track=[queries])