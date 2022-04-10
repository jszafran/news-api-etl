from unittest import TestCase

import boto3
import freezegun
from moto import mock_s3

from news_api_etl.etl import NewsApiETLPipeline
from news_api_etl.loaders import S3CSVLoader
from news_api_etl.models import NewsSource, SourceTopHeadline
from news_api_etl.newsapi import InMemoryNewsApiClient


@mock_s3
class TestETL(TestCase):
    def test_whole_pipeline(self):
        def get_s3_object_body(s3_resource, bucket, key):
            return s3_resource.Object(bucket, key).get()["Body"].read().decode("utf-8")

        bucket_name = "test-bucket"
        s3 = boto3.resource("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=bucket_name)

        news_api_client = InMemoryNewsApiClient(
            sources=[
                NewsSource(id="abc-news", name="ABC News"),
                NewsSource(id="bbc", name="BBC"),
                NewsSource(id="cnn", name="CNN"),
            ],
            top_headlines=[
                SourceTopHeadline(source_id="abc-news", title="ABC Headline 1"),
                SourceTopHeadline(source_id="abc-news", title="ABC Headline 2"),
                SourceTopHeadline(source_id="abc-news", title="ABC Headline 3"),
                SourceTopHeadline(source_id="bbc", title="BBC Headline 1"),
                SourceTopHeadline(source_id="bbc", title="BBC Headline 2"),
                SourceTopHeadline(source_id="cnn", title="CNN Headline 1"),
            ],
        )
        data_loader = S3CSVLoader(
            bucket_name=bucket_name,
            aws_access_key_id="fake",
            aws_secret_access_key="fake",
        )

        pipeline = NewsApiETLPipeline(
            news_api_client=news_api_client, data_loader=data_loader
        )

        bucket_objects = list(s3.Bucket("test-bucket").objects.all())
        self.assertEqual(0, len(bucket_objects))

        run_timestamp = "20220410_100102"
        with freezegun.freeze_time("2022-04-10T10:01:02"):
            pipeline.run()

        bucket_objects = list(s3.Bucket("test-bucket").objects.all())
        self.assertEqual(3, len(bucket_objects))

        abc_news_csv_text = (
            "top_headlines\r\nABC Headline 1\r\nABC Headline 2\r\nABC Headline 3\r\n"
        )
        bbc_csv_text = "top_headlines\r\nBBC Headline 1\r\nBBC Headline 2\r\n"
        cnn_csv_text = "top_headlines\r\nCNN Headline 1\r\n"

        self.assertEqual(
            abc_news_csv_text,
            get_s3_object_body(
                s3, bucket_name, f"abc-news/{run_timestamp}_headlines.csv"
            ),
        )

        self.assertEqual(
            bbc_csv_text,
            get_s3_object_body(s3, bucket_name, f"bbc/{run_timestamp}_headlines.csv"),
        )

        self.assertEqual(
            cnn_csv_text,
            get_s3_object_body(s3, bucket_name, f"cnn/{run_timestamp}_headlines.csv"),
        )
