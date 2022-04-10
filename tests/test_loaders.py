from unittest import TestCase

from news_api_etl.loaders import create_csv_text
from news_api_etl.models import SourceAggregatedTopHeadlines, TopHeadline


class TestLoaders(TestCase):
    def test_create_csv_text(self):
        top_headlines = SourceAggregatedTopHeadlines(
            source_id="some-source",
            top_headlines=[
                TopHeadline(title="foo"),
                TopHeadline(title="bar"),
                TopHeadline(title="baz"),
                TopHeadline(title="ba'z"),
            ],
        )

        expected = "top_headlines\r\nfoo\r\nbar\r\nbaz\r\nba'z\r\n"
        received = create_csv_text(top_headlines)
        self.assertEqual(expected, received)
