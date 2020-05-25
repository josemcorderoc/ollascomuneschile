import findspark
import pandas as pd
import time
from flashtext import KeywordProcessor
from datetime import datetime

findspark.init()

from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.functions import from_json, col, year, month, dayofmonth, hour, udf, to_timestamp
from unidecode import unidecode

from init_spark import spark

import pytz


DATA_BUCKET_NAME = 'ollascomuneschile'
PROCESSED_DATA_PREFIX_KEY = 'data/processed_test_PARQUET2'
DATA_BUCKET_REGION = 'us-east-2'

TOPIC_OLLAS_COMUNES_TWITTER = "ollas-comunes-topic"
SANTIAGO_TZ = pytz.timezone('America/Santiago')

# columns: id_str, created_at, text, user.id_str, user.screen_name, user.followers_count, user.friends_count, user.statuses_count
TWITTER_STRUCT = StructType([
    StructField("id_str", StringType(), False),
    StructField("created_at", StringType(), False),
    StructField("text", StringType(), False),
    StructField("coordinates", StringType()),
    StructField("place", StringType()),
    StructField("user",
                StructType([
                    StructField('id_str', StringType()),
                    StructField('screen_name', StringType()),
                    StructField('followers_count', IntegerType()),
                    StructField('friends_count', IntegerType()),
                    StructField('statuses_count', IntegerType()),
                ]))
])

COMUNAS_KEYWORDS = KeywordProcessor()
for i, row in pd.read_csv("comunas.csv").iterrows():
    comuna = row['comuna']
    variations = {comuna, unidecode(comuna), comuna.replace(' ', ''), unidecode(comuna.replace(' ', ''))}
    for comuna_var in variations:
        COMUNAS_KEYWORDS.add_keyword(comuna_var, comuna)

    if pd.notna(row['sinonimos']):
        pass



@udf(returnType=StringType())
def get_tweet_datetime(created_at):
    '''
    Parses a 'created_at' tweet field to string datetime
    :param created_at:
    :return:
    '''
    return datetime.strptime(
        created_at, '%a %b %d %H:%M:%S +0000 %Y') \
        .replace(tzinfo=pytz.UTC) \
        .astimezone(SANTIAGO_TZ) \
        .strftime("%Y-%m-%d %H:%M:%S")



@udf(returnType=StringType())
def comuna_tweet(tweet):
    preprocessed_tweet = unidecode(tweet)
    keywords_found = COMUNAS_KEYWORDS.extract_keywords(preprocessed_tweet)
    return ",".join(keywords_found)


# todo broker:29092
def preprocess_save_tweets():
    '''
    Streams data from Kafka topic, preprocess and stores it in an S3 bucket,
    :return: None
    '''
    tweets_stream = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "broker:29092") \
        .option("subscribe", TOPIC_OLLAS_COMUNES_TWITTER) \
        .load()

    df = tweets_stream.selectExpr("CAST(value AS STRING) as json_data")
    df = df.select(from_json(col('json_data'), TWITTER_STRUCT).alias('parsed_data')).select("parsed_data.*")

    df = df.withColumnRenamed('id_str', 'tweet_id_str')
    df = df.select(
        "tweet_id_str",
        "created_at",
        "text",
        "user.*",
    )
    for user_column in ['id_str', 'screen_name', 'followers_count', 'friends_count', 'statuses_count']:
        df = df.withColumnRenamed(user_column, f"user_{user_column}")

    df = df.withColumn('comuna_identificada', comuna_tweet('text'))
    df = df.withColumn("datetime", to_timestamp(get_tweet_datetime("created_at")))
    df.printSchema()

    df = df \
        .withColumn("year", year(col("datetime"))) \
        .withColumn("month", month(col("datetime"))) \
        .withColumn("day", dayofmonth(col("datetime"))) \
        .withColumn("hour", hour(col("datetime")))

    output_path = f"s3a://{DATA_BUCKET_NAME}/{PROCESSED_DATA_PREFIX_KEY}/"
    # output_path = "/home/jose/PycharmProjects/ollascomuneschile/ollascomuneschile/data/EJ3/"

    query = df \
        .writeStream \
        .option("checkpointLocation", "/tmp/spark_checkpoints") \
        .outputMode("append") \
        .option("path", output_path) \
        .option("header", "true") \
        .partitionBy("year", "month", "day", "hour") \
        .format("parquet") \
        .trigger(processingTime="45 seconds") \
        .start()

    query.awaitTermination()


if __name__ == '__main__':
    # wait until Kafka is ready
    time.sleep(30)
    preprocess_save_tweets()
