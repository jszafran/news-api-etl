import logging
import os

from dotenv import load_dotenv

from news_api_etl.etl import NewsApiETL
from news_api_etl.loaders import S3CSVLoader
from news_api_etl.newsapi import NewsApiHTTPClient


def configure_logging() -> None:
    # configure simple default ETL logger
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
    # log only critical messages from botocore
    logging.getLogger("botocore").setLevel(logging.CRITICAL)


def main():
    load_dotenv()
    configure_logging()
    client = NewsApiHTTPClient(os.getenv("NEWS_API_KEY"))
    data_loader = S3CSVLoader(bucket_name=os.getenv("BUCKET_NAME"))
    NewsApiETL(news_api_client=client, data_loader=data_loader).run()


if __name__ == "__main__":
    main()
