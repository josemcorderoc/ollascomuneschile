FROM python:3.8-slim

#RUN apt-get install -y python3-psycopg2
RUN apt-get update
RUN apt-get install -y python-dev libpq-dev gcc
RUN pip install pandas Flask plotly schedule gunicorn psycopg2

WORKDIR /app

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

ENV PYTHONUNBUFFERED 1

COPY . .

#ENTRYPOINT ["python", "app.py"]