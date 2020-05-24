import findspark
import pandas as pd
import time
from flashtext import KeywordProcessor
from datetime import datetime

findspark.init()

from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import from_json, col, year, month, dayofmonth, hour, udf,to_timestamp
from unidecode import unidecode

from init_spark import spark

import pytz
# wait until Kafka is ready
time.sleep(30)

TOPIC_OLLAS_COMUNES_TWITTER = "ollas-comunes-topic"

TWITTER_STRUCT = StructType([
    StructField("id_str", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("text", StringType(), True),
    # StructField("user.id_str", StringType(), True),
])

COMUNAS_KEYWORDS = KeywordProcessor()
for i, row in pd.read_csv("comunas.csv").iterrows():
    comuna = row['comuna']
    variations = {comuna, unidecode(comuna), comuna.replace(' ', ''), unidecode(comuna.replace(' ', ''))}
    for comuna_var in variations:
        COMUNAS_KEYWORDS.add_keyword(comuna_var, comuna)

    if pd.notna(row['sinonimos']):
        pass



SANTIAGO_TZ = pytz.timezone('America/Santiago')


## Converting date string format
@udf(returnType=StringType())
def get_tweet_datetime(created_at):
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


def hello_world_spark_kafka():
    tweets_stream = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "broker:29092") \
        .option("subscribe", TOPIC_OLLAS_COMUNES_TWITTER) \
        .load()

    df = tweets_stream.selectExpr("CAST(value AS STRING) as json_data")
    df = df.select(from_json(col('json_data'), TWITTER_STRUCT).alias('parsed_data')).select("parsed_data.*")

    df = df.withColumn('comuna_identificada', comuna_tweet('text'))
    df = df.withColumn("datetime", to_timestamp(get_tweet_datetime("created_at")))
    df.printSchema()

    df = df \
        .withColumn("year", year(col("datetime"))) \
        .withColumn("month", month(col("datetime"))) \
        .withColumn("day", dayofmonth(col("datetime"))) \
        .withColumn("hour", hour(col("datetime")))

    output_path = "s3a://ollascomuneschile/data/processed_test4/"

    query = df \
        .writeStream \
        .option("checkpointLocation", "/tmp/1005/spark_checkpoints") \
        .outputMode("append") \
        .option("path", output_path) \
        .partitionBy("year", "month", "day", "hour") \
        .format("csv") \
        .trigger(processingTime="5 seconds") \
        .start()

    query.awaitTermination()


if __name__ == '__main__':
    hello_world_spark_kafka()
