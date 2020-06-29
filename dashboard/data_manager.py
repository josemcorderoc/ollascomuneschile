import datetime
import os
import threading
import time

import pandas as pd
import psycopg2
import pytz

SANTIAGO_TZ = pytz.timezone('America/Santiago')


class OllasComunesDB:
    def __init__(self):
        self.updates_history = []
        self.conn = psycopg2.connect(
            database="ollascomuneschile",
            user="postgres",
            # host="db",
            host='18.221.221.216',
            port='7777',
            password=os.environ['POSTGRES_PASSWORD']
        )

    # def get_last_update_string(self):
    #     return self.last_update.strftime("%d-%m-%Y %H:%M:%S")

    def get_lista_comunas(self):
        sql = "SELECT DISTINCT comuna_identificada FROM tweets_ollascomunes_processed;"
        df = pd.read_sql_query(sql, self.conn)
        return list(df['comuna_identificada'].dropna().sort_values())

    def get_tweets_comuna(self, comuna):
        '''
        Filtra tweets de la comuna correspondiente
        :param comuna: str
        :return: DataFrame
        '''
        sql = f"SELECT * FROM tweets_ollascomunes_processed WHERE comuna_identificada='{comuna}' ORDER BY datetime DESC LIMIT 20;"
        df = pd.read_sql_query(sql, self.conn)
        df = df[df['comuna_identificada'] == comuna]
        df['hover_text'] = df['text'].map(add_hover_text_linebreaks)
        return df

    def last_tweets_id_comuna(self, comuna, n):
        '''
        Ultimos n tweets para una comuna
        :param comuna: str
        :param n: int
        :return: lista de ids
        '''
        sql = f"SELECT * FROM tweets_ollascomunes_processed WHERE comuna_identificada='{comuna}' ORDER BY datetime DESC LIMIT {n};"
        df = pd.read_sql_query(sql, self.conn)
        ids = df.sort_values(by='datetime', ascending=False)['tweet_id_str'].unique()
        return list(ids)[:n]


def add_hover_text_linebreaks(text):
    try:
        return text[:40] + " <br> " + text[40:80] + " <br> " + text[80:]
    except TypeError:
        return ''
