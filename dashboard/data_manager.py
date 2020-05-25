import datetime
import awswrangler as wr
import pandas as pd
import schedule as schedule
import s3fs
import fastparquet as fp
fs = s3fs.S3FileSystem()
import pyarrow.parquet as pq

DATA_BUCKET_NAME = 'ollascomuneschile'
PROCESSED_DATA_PREFIX_KEY = 'data/processed_test_PARQUET2'
DATA_BUCKET_REGION = 'us-east-2'


class OllasComunesDB:
    def __init__(self):
        self.last_update = datetime.datetime.min
        self.df = pd.DataFrame()

        self.get_initial_data()
        # schedule.every(1).minutes.do(self.update_data)

    def get_last_update_string(self):
        return self.last_update.strftime("%d-%m-%Y %H:%M:%S")

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
        # todo filter old tweets


        self.df = updated_df
        self.last_update = current_update
        print('Base actualizada')

    def get_initial_data(self):
        last_update = datetime.datetime.now()
        # fp_obj = fp.ParquetFile(all_paths_from_s3, open_with=myopen)
        # df = fp_obj.to_pandas()
        # print(f"s3://{DATA_BUCKET_NAME}/{PROCESSED_DATA_PREFIX_KEY}/")
        # dataset = pq.ParquetDataset(f"s3://{DATA_BUCKET_NAME}/{PROCESSED_DATA_PREFIX_KEY}", filesystem=fs)
        # table = dataset.read()
        # df = table.to_pandas()

        df = wr.s3.read_parquet(path=f"s3://{DATA_BUCKET_NAME}/{PROCESSED_DATA_PREFIX_KEY}/", dataset=True)

        self.df = df
        self.last_update = last_update

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
        ids = df.sort_values(by='datetime', ascending=False)['tweet_id_str'].tolist()
        return ids[:n]


def add_hover_text_linebreaks(text):
    try:
        return text[:40] + " <br> " + text[40:80] + " <br> " + text[80:]
    except TypeError:
        return ''




import s3fs
import pyarrow.parquet as pq
fs = s3fs.S3FileSystem()

bucket_uri = f's3://{DATA_BUCKET_NAME}/{PROCESSED_DATA_PREFIX_KEY}'
dataset = pq.ParquetDataset(bucket_uri, filesystem=fs)
table = dataset.read()
df = table.to_pandas()



s3_path = "ollascomuneschile/data/processed_test_PARQUET2/*/*/*/*.parquet"
all_paths_from_s3 = fs.glob(path=s3_path)

myopen = s3.open
#use s3fs as the filesystem
fp_obj = fp.ParquetFile(all_paths_from_s3,open_with=myopen)
#convert to pandas dataframe
df = fp_obj.to_pandas()