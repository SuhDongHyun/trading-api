from datetime import datetime
from dataclasses import dataclass


@dataclass
class News:
    """단일 뉴스 항목의 도메인 모델."""

    key: str
    title: str
    source: str
    published_at: datetime
