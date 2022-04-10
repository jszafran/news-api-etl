import logging
from collections import defaultdict
from datetime import datetime
from typing import List

from news_api_etl.models import (
    DataLoader,
    NewsApiClient,
    SourceAggregatedTopHeadlines,
    SourceTopHeadline,
)


class NewsApiETL:
    def __init__(self, news_api_client: NewsApiClient, data_loader: DataLoader):
        self._news_api_client = news_api_client
        self._data_loader = data_loader

    def extract(self) -> List[SourceTopHeadline]:
        logging.info("Extracting English sources.")
        english_sources = self._news_api_client.get_sources(language="en")
        logging.info(f"Fetched {len(english_sources)} English sources from News Api.")
        sources_names = ", ".join(source.name for source in english_sources)
        logging.info(f"Extracting top headlines for English sources: {sources_names}")
        top_headlines = self._news_api_client.get_top_headlines(sources=english_sources)
        logging.info(
            f"Found {len(top_headlines)} top headlines coming from provided news sources."
        )
        return top_headlines

    def transform(
        self, top_headlines: List[SourceTopHeadline]
    ) -> List[SourceAggregatedTopHeadlines]:
        logging.info("Transforming data (aggregate top headlines by source name)")
        source_aggregated_top_headlines = defaultdict(list)
        for top_headline in top_headlines:
            source_aggregated_top_headlines[top_headline.source_id].append(
                top_headline.title
            )
        logging.info("Transformation done.")
        return [
            SourceAggregatedTopHeadlines(
                source_id=source_id, top_headlines=top_headlines
            )
            for source_id, top_headlines in source_aggregated_top_headlines.items()
        ]

    def load(
        self,
        aggregated_top_headlines: List[SourceAggregatedTopHeadlines],
        run_timestamp: str,
    ):
        self._data_loader.load_headlines(aggregated_top_headlines, run_timestamp)

    def run(self) -> None:
        logging.info("Starting NewsApi ETL process.")
        run_timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        data = self.extract()
        transformed_data = self.transform(data)
        self.load(transformed_data, run_timestamp)
        logging.info("ETL process finished.")
