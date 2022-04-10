from typing import List, Optional

import requests

from news_api_etl.models import NewsSource, SourceTopHeadline


class NewsApiHTTPClient:
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://newsapi.org/v2/",
    ) -> None:
        self._api_url = api_url
        self._session = requests.Session()
        self._session.headers.update({"X-Api-Key": api_key})

    def _get(self, url):
        return self._session.get(self._api_url + url, timeout=5)

    def get_sources(self, language: Optional[str] = None) -> List[NewsSource]:
        endpoint_url = "sources"
        if language is not None:
            endpoint_url += f"?language={language}"
        response = self._get(endpoint_url)
        response.raise_for_status()
        return [
            NewsSource(id=source["id"], name=source["name"])
            for source in response.json()["sources"]
        ]

    def get_top_headlines(self, sources: List[NewsSource]) -> List[SourceTopHeadline]:
        sources_ids = ",".join(s.id for s in sources)
        endpoint_url = f"top-headlines/?sources={sources_ids}&pageSize=100"
        response = self._get(endpoint_url)
        response.raise_for_status()
        top_headlines = response.json()["articles"]
        source_top_headlines = [
            SourceTopHeadline(
                title=top_headline["title"], source_id=top_headline["source"]["id"]
            )
            for top_headline in top_headlines
        ]
        return source_top_headlines


class InMemoryNewsApiClient:
    def __init__(
        self, sources: List[NewsSource], top_headlines: List[SourceTopHeadline]
    ) -> None:
        self._sources = sources
        self._top_headlines = top_headlines

    def get_sources(self, language: Optional[str] = None) -> List[NewsSource]:
        return self._sources

    def get_top_headlines(self, sources: List[NewsSource]) -> List[SourceTopHeadline]:
        return self._top_headlines
