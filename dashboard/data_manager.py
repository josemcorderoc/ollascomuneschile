import datetime
import threading
import time

import awswrangler as wr
import pandas as pd
import pytz

DATA_BUCKET_NAME = 'ollascomuneschile'
PROCESSED_DATA_PREFIX_KEY = 'data/processed_tweets_hola'
DATA_BUCKET_REGION = 'us-east-2'
SANTIAGO_TZ = pytz.timezone('America/Santiago')


class OllasComunesDB:
    def __init__(self):
        self.last_update = datetime.datetime.min
        self.df = pd.DataFrame()
        self.updates_history = []

        self.get_initial_data()
        self.thread_update_data()

    def get_last_update_string(self):
        return self.last_update.replace(tzinfo=pytz.UTC).astimezone(SANTIAGO_TZ).strftime("%d-%m-%Y %H:%M:%S")

    def thread_update_data(self):
        th = threading.Thread(target=self.update_data)
        th.daemon = True
        th.start()

    def get_current_info(self):
        return {
            'update_date': self.get_last_update_string(),
            'db_size': len(self.df),
            'db_size_unicos': len(self.df.drop_duplicates(subset=['tweet_id_str'])),
            'df_size_comunas_notnull': len(self.df[self.df['comuna_identificada'] != '']),
            'lista_comunas': self.get_lista_comunas(),
            'primer_tweet':
                self.df.sort_values(by='datetime', ascending=True).iloc[0].to_json(orient='records', force_ascii=False),
            'ultimo_tweet':
                self.df.sort_values(by='datetime', ascending=False).iloc[0].to_json(orient='records', force_ascii=False),
        }
    def update_data(self):
        current_update = datetime.datetime.now()
        updated_at = self.last_update
        print('Actualizando DB a las {}'.format(current_update.strftime("%d-%m-%Y %H:%M:%S")))

        hour_step = datetime.timedelta(hours=1)
        new_dfs = []
        while updated_at < current_update:
            path = f"s3://{DATA_BUCKET_NAME}/{PROCESSED_DATA_PREFIX_KEY}/" \
                   f"year={updated_at.year}/month={updated_at.month}/day={updated_at.day}/hour={updated_at.hour}/"
            try:
                df = wr.s3.read_parquet(path=path, dataset=True)
                new_dfs.append(df)
            except OSError:
                pass
            updated_at += hour_step
        updated_df = pd.concat([self.df] + new_dfs, ignore_index=True).drop_duplicates(subset=['tweet_id_str'])
        updated_df = updated_df.drop_duplicates(subset=['tweet_id_str'])

        # filter old tweets
        week_delta = datetime.timedelta(days=7)
        updated_df = updated_df[updated_df['datetime'] > current_update - week_delta]

        self.df = updated_df
        self.last_update = current_update

        self.updates_history.append(self.get_current_info())
        print('Base actualizada')
        threading.Timer(300.0, self.update_data).start()

    def get_initial_data(self):
        last_update = datetime.datetime.now()
        for i in range(1, 11):
            try:
                df = wr.s3.read_parquet(path=f"s3://{DATA_BUCKET_NAME}/{PROCESSED_DATA_PREFIX_KEY}/", dataset=True)
                self.df = df.drop_duplicates(subset=['tweet_id_str'])
                self.last_update = last_update
                return
            except OSError:
                print(f'Error: no existe la ruta (intento n.{i})')
                time.sleep(10)
        raise OSError('')


    def get_lista_comunas(self):
        return list(self.df['comuna_identificada'].dropna().unique())

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
