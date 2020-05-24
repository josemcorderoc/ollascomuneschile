import os
#
import findspark
findspark.init()

from pyspark import SparkContext, SparkConf, SQLContext
from pyspark.sql import SparkSession

print(os.environ['AWS_ACCESS_KEY_ID'])
print(os.environ['AWS_SECRET_ACCESS_KEY'])

conf = (
    SparkConf()
        .set("spark.hadoop.fs.s3a.path.style.access", True)
        .set("spark.hadoop.fs.s3a.access.key", os.environ['AWS_ACCESS_KEY_ID'])
        .set("spark.hadoop.fs.s3a.secret.key", os.environ['AWS_SECRET_ACCESS_KEY'])
        .set("spark.hadoop.fs.s3a.endpoint", "s3.us-east-2.amazonaws.com")
        .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .set("spark.driver.extraJavaOptions", "-Dcom.amazonaws.services.s3.enableV4=true")
        .set("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", 2)
        .set("spark.speculation", False)

)


spark = SparkSession.builder.config(conf=conf).appName("ollascomuneschile").getOrCreate()

# sc = SparkContext(conf=conf)
print(f"Hadoop version = {spark.sparkContext._jvm.org.apache.hadoop.util.VersionInfo.getVersion()}")
