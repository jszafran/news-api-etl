import csv
import io
import logging
import os
import pathlib
from typing import List

import boto3

from news_api_etl.models import SourceAggregatedTopHeadlines


def create_csv_text(
    source_aggregated_top_headlines: SourceAggregatedTopHeadlines,
    header: str = "top_headlines",
) -> str:
    header = (header,)
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    writer.writerows(
        (headline.title,) for headline in source_aggregated_top_headlines.top_headlines
    )
    return buffer.getvalue()


class LocalDiskCSVLoader:
    def __init__(self, root_path: pathlib.Path) -> None:
        self._root_path = root_path

    def load_headlines(
        self, source_top_headlines: List[SourceAggregatedTopHeadlines], timestamp: str
    ) -> None:
        logging.info(
            f"Loading {len(source_top_headlines)} english sources top headlines to "
            f"local disk ({self._root_path.absolute()})."
        )
        if not self._root_path.exists():
            self._root_path.mkdir()
        for source_headlines in source_top_headlines:
            source_dir = self._root_path / source_headlines.source_id
            source_dir.mkdir(exist_ok=True)
            csv_path = source_dir / f"{timestamp}_headlines.csv"
            with open(str(csv_path.absolute()), "wt", encoding="utf-8") as f:
                f.write(create_csv_text(source_headlines))
        logging.info("Loading done.")


class S3CSVLoader:
    def __init__(
        self,
        bucket_name: str = os.getenv("BUCKET_NAME"),
        aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY"),
    ) -> None:
        self._bucket_name = bucket_name
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

    def load_headlines(
        self, source_top_headlines: List[SourceAggregatedTopHeadlines], timestamp: str
    ) -> None:
        logging.info(
            f"Loading {len(source_top_headlines)} english sources top headlines to S3 bucket s3://{self._bucket_name}/."
        )
        s3_client = boto3.client("s3")
        for source_headlines in source_top_headlines:
            key = f"{source_headlines.source_id}/{timestamp}_headlines.csv"
            s3_client.put_object(
                Body=create_csv_text(source_headlines),
                Bucket=self._bucket_name,
                Key=key,
            )
        logging.info("Loading done.")
