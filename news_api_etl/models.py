from dataclasses import dataclass
from typing import List, Optional, Protocol


@dataclass(frozen=True)
class NewsSource:
    id: str
    name: str


@dataclass(frozen=True)
class TopHeadline:
    title: str


@dataclass(frozen=True)
class SourceTopHeadline(TopHeadline):
    source_id: str


@dataclass(frozen=True)
class SourceAggregatedTopHeadlines:
    source_id: str
    top_headlines: List[TopHeadline]


class NewsApiClient(Protocol):
    def get_sources(self, language: Optional[str] = None) -> List[NewsSource]:
        pass

    def get_top_headlines(self, sources: List[NewsSource]) -> List[SourceTopHeadline]:
        pass


class DataLoader(Protocol):
    def load_headlines(
        self, source_top_headlines: List[SourceAggregatedTopHeadlines], timestamp: str
    ) -> None:
        pass
