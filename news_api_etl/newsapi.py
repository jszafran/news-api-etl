from dataclasses import dataclass
from typing import Iterable, List, Protocol

import requests


@dataclass
class NewsSource:
    id: str
    name: str


class NewsApiClient(Protocol):
    def get_sources_for_language(self, language: str = "en") -> List[NewsSource]:
        pass

    def get_top_headlines_for_sources(self, sources: Iterable[NewsSource]):
        pass


class NewsApiHTTPClient:
    def __init__(self, api_key: str, api_url: str = "https://newsapi.org/v2/") -> None:
        self._api_url = api_url
        self._headers = {"X-Api-Key": api_key}

    def get_sources_for_language(self, language: str = "en") -> List[NewsSource]:
        response = requests.get(
            self._api_url + f"sources?language={language}", headers=self._headers
        )
        response.raise_for_status()
        return [
            NewsSource(id=source["id"], name=source["name"])
            for source in response.json()["sources"]
        ]
