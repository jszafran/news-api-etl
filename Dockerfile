FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY .env main.py ./
COPY news_api_etl ./news_api_etl
