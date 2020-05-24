FROM jupyter/pyspark-notebook
RUN conda install tweepy findspark Unidecode pytz
RUN pip install kafka_python flashtext


ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

USER root
# Add essential packages
RUN apt-get update && apt-get install -y build-essential curl git gnupg2 nano apt-transport-https software-properties-common
# Set locale
RUN apt-get update && apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen
#
RUN wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk/1.7.4/aws-java-sdk-1.7.4.jar -P $SPARK_HOME/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/2.7.3/hadoop-aws-2.7.3.jar -P $SPARK_HOME/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.11/2.4.5/spark-sql-kafka-0-10_2.11-2.4.5.jar -P $SPARK_HOME/jars/
RUN wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/0.10.1.0/kafka-clients-0.10.1.0.jar -P $SPARK_HOME/jars/

WORKDIR /app

COPY . .

RUN $SPARK_HOME/bin/spark-submit --version
#RUN $SPARK_HOME/bin/spark-submit --master local --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5,com.amazonaws:aws-java-sdk:1.7.4,org.apache.hadoop:hadoop-aws:2.7.3 init_spark.py

#ENTRYPOINT $SPARK_HOME/bin/spark-submit --master local --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.5,com.amazonaws:aws-java-sdk:1.7.4,org.apache.hadoop:hadoop-aws:2.7.3 tweet_processing.py
ENTRYPOINT ["python", "tweet_processing.py"]
