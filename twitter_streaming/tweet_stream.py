import datetime
import json
import tweepy
from kafka import KafkaProducer
import os
import time
import psycopg2
import json

from psycopg2._json import Json

TOPIC_OLLAS_COMUNES_TWITTER = "ollas-comunes-topic"

# Wait until Kafka server is loaded
print('Waiting for Kafka')
time.sleep(45)
print('Ready')

# Authenticate to Twitter
auth = tweepy.OAuthHandler(os.environ['CONSUMER_API_KEY'], os.environ["CONSUMER_API_SECRET_KEY"])
auth.set_access_token(os.environ["ACCESS_TOKEN"], os.environ["ACCESS_TOKEN_SECRET"])

# Create API object
api = tweepy.API(auth)

# Creates Kafka producer
ollascomunes_tweets_producer = KafkaProducer(bootstrap_servers='broker:29092')
conn = psycopg2.connect(
    database="ollascomuneschile",
    user="postgres",
    host="db",
    password=os.environ['POSTGRES_PASSWORD']
)
cur = conn.cursor()


class MyStreamListener(tweepy.StreamListener):
    i = 0

    def on_status(self, status):
        if 'retweeted_status' not in status._json:
            self.i += 1
            print(f'Mensaje num {self.i} enviado a las {datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}')

            ollascomunes_tweets_producer.send(TOPIC_OLLAS_COMUNES_TWITTER,
                                              json.dumps(status._json).encode('utf-8'))
            json_text = json.dumps(status._json).replace("'", "''")
            try:
                cur.execute(
                    f"""INSERT INTO tweets_ollascomunes_raw (info) VALUES ( to_json('{json_text}'::text) );""")
                conn.commit()
            except Exception as e:
                print("ERROR", e)

    def on_exception(self, exception):
        print(exception)
        return


if __name__ == '__main__':
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
    queries = ['#ollascomunes', '#ollacomun', 'olla comun', 'acopio', 'ollacomun', 'olla común',
               '#ollacomún']  # ollasolidario, menciones a @apoyalaolla

    users = {
        '@apoyalaolla': '1262973661121859584',
        '@ComunOlla': '1259208616776732672',
        '@LaOlladeChile': '1263146335206887424'
    }
    myStream.filter(track=queries, follow=users.values())

    # if ends
    cur.close()
    conn.commit()
    conn.close()
