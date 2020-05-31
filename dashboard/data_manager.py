import datetime
import os
import threading
import time

import pandas as pd
import psycopg2
import pytz

SANTIAGO_TZ = pytz.timezone('America/Santiago')


# TWEETS_DTYPES = {
#     'tweet_id_str': 'str',
#     'created_at': 'str',
#     'text': 'str',
#     'user_id_str': 'str',
#     'user_screen_name': 'str',
# }
#
# INTEGER_TYPES = {
#     'user_followers_count': 'int64',
#     'user_friends_count': 'int64',
#     'user_statuses_count': 'int64',
# }


class OllasComunesDB:
    def __init__(self):
        self.last_update = datetime.datetime.min
        self.df = pd.DataFrame()
        self.updates_history = []
        self.conn = psycopg2.connect(
            database="ollascomuneschile",
            user="postgres",
            host="db",
            password=os.environ['POSTGRES_PASSWORD']
        )
        self.get_initial_data()
        self.thread_update_data()

    def get_last_update_string(self):
        return self.last_update.strftime("%d-%m-%Y %H:%M:%S")

    def thread_update_data(self):
        th = threading.Thread(target=self.update_data)
        th.daemon = True
        th.start()

    def get_current_info(self):
        if len(self.df) == 0:
            return {
            'update_date': self.get_last_update_string(),
            'db_size': len(self.df),
            }

        return {
            'update_date': self.get_last_update_string(),
            'db_size': len(self.df),
            'df_size_comunas_notnull': len(
                self.df[self.df['comuna_identificada'] != '']['comuna_identificada'].dropna()),
            'lista_comunas': self.get_lista_comunas(),
            'primer_tweet':
                self.df.sort_values(by='datetime', ascending=True).iloc[0].to_json(orient='records', force_ascii=False),
            'ultimo_tweet':
                self.df.sort_values(by='datetime', ascending=False).iloc[0].to_json(orient='records',
                                                                                    force_ascii=False),
        }

    def update_data(self):
        # todo only update, not picking all data
        current_update = datetime.datetime.now().replace(tzinfo=pytz.UTC).astimezone(SANTIAGO_TZ)
        try:
            self.df = self.get_DB_tweets_df()
            self.last_update = current_update
            self.updates_history.append(self.get_current_info())
            print(f'Base actualizada a las {self.get_last_update_string()}')
        except FileNotFoundError as e:
            print(f'Error al actualizar base a las {self.get_last_update_string()}')
            print(e)
        threading.Timer(10.0, self.update_data).start()

    def get_DB_tweets_df(self):
        sql = "SELECT * FROM tweets_ollascomunes_processed WHERE datetime > NOW() - interval '1 week';"
        df = pd.read_sql_query(sql, self.conn)
        print(len(df))
        return df

    def get_initial_data(self):
        last_update = datetime.datetime.now().replace(tzinfo=pytz.UTC).astimezone(SANTIAGO_TZ)
        for i in range(1, 11):
            try:
                # self.df = self.get_s3_tweets_df(last_update)
                self.df = self.get_DB_tweets_df()
                self.last_update = last_update
                return
            except OSError:
                print(f'Error: no existe la ruta (intento n.{i})')
                time.sleep(10)
        raise OSError('')

    def get_lista_comunas(self):
        return list(self.df['comuna_identificada'].dropna().sort_values().unique())

    def get_tweets_comuna(self, comuna):
        '''
        Filtra tweets de la comuna correspondiente
        :param comuna: str
        :return: DataFrame
        '''
        df = self.df
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
        df = self.df
        df = df[df['comuna_identificada'] == comuna]
        ids = df.sort_values(by='datetime', ascending=False)['tweet_id_str'].unique()
        return list(ids)[:n]


def add_hover_text_linebreaks(text):
    try:
        return text[:40] + " <br> " + text[40:80] + " <br> " + text[80:]
    except TypeError:
        return ''
