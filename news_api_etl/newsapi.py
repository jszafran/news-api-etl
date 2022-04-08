from dataclasses import dataclass
from typing import Iterable, List, Optional, Protocol

import requests


@dataclass
class NewsSource:
    id: str
    name: str


@dataclass
class TopHeadline:
    headline: str
    source_id: str


class NewsApiClient(Protocol):
    def get_sources(self, language: Optional[str] = None) -> List[NewsSource]:
        pass

    def get_top_headlines(self, sources: Optional[Iterable[NewsSource]] = None):
        pass


class NewsApiHTTPClient:
    def __init__(self, api_key: str, api_url: str = "https://newsapi.org/v2/") -> None:
        self._api_url = api_url
        self._session = requests.Session()
        self._session.headers.update({"X-Api-Key": api_key})

    def _get(self, url):
        return self._session.get(self._api_url + url)

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

    def get_top_headlines(self, sources: List[NewsSource]) -> List[TopHeadline]:
        sources_ids = ",".join(s.id for s in sources)
        endpoint_url = f"top-headlines/?sources={sources_ids}"
        response = self._get(endpoint_url)
        response.raise_for_status()
        top_headlines = response.json()["articles"]
        return [
            TopHeadline(
                headline=top_headline["title"], source_id=top_headline["source"]["id"]
            )
            for top_headline in top_headlines
        ]
