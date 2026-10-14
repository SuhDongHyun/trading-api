import logging
from datetime import datetime

from stock.domain.news import News
from stock.domain.port.news_client import NewsClient
from stock.infra.kis.kis_http_client import KisHttpClient

logger = logging.getLogger(__name__)
KIS_NEWS_PAGE_SIZE = 40


class KisNewsClient(NewsClient):
    """KIS 종목 뉴스 API의 제한된 페이지를 도메인 뉴스로 변환한다."""

    def __init__(self, http_client: KisHttpClient):
        self._http_client = http_client

    def _get_news(self, code: str, search_date: str, search_time: str) -> list[dict]:
        """지정 종목과 검색 시각 이후의 KIS 뉴스 한 페이지를 조회한다."""

        path = "/uapi/domestic-stock/v1/quotations/news-title"
        params = {
            "FID_NEWS_OFER_ENTP_CODE": "",
            "FID_COND_MRKT_CLS_CODE": "",
            "FID_INPUT_ISCD": code,
            "FID_TITL_CNTT": "",
            "FID_INPUT_DATE_1": search_date,
            "FID_INPUT_HOUR_1": search_time,
            "FID_RANK_SORT_CLS_CODE": "",
            "FID_INPUT_SRNO": "",
        }
        logger.info(
            "Requesting KIS news code=%s search_date=%s search_time=%s params=%s",
            code,
            search_date,
            search_time,
            params,
        )
        resp = self._http_client.get(path, params=params, tr_id="FHKST01011800")
        return resp.json()["output"]

    def get_total_news(
        self, code: str, search_date: str, search_time: str
    ) -> list[News]:
        """40건 제한에 걸린 경우 마지막 발행 시각부터 더 오래된 뉴스 페이지를 읽는다."""

        news_by_key: dict[str, News] = {}
        search_day = datetime.strptime(search_date, "%Y%m%d").date()
        while True:
            news_list = self._get_news(code, search_date, search_time)
            code_cols = ["iscd1", "iscd2", "iscd3", "iscd4", "iscd5"]
            target_news = [
                News(
                    key=item["cntt_usiq_srno"],
                    title=item["hts_pbnt_titl_cntt"],
                    source=item["dorg"],
                    published_at=datetime.strptime(
                        item["data_dt"] + item["data_tm"], "%Y%m%d%H%M%S"
                    ),
                )
                for item in news_list
                if any(item.get(column) == code for column in code_cols)
            ]
            before_count = len(news_by_key)
            for news in target_news:
                if news.key not in news_by_key:
                    news_by_key[news.key] = news

            if len(news_list) < KIS_NEWS_PAGE_SIZE or len(news_by_key) == before_count:
                break

            # 경계 시각 기사가 다음 페이지에도 들어올 수 있어 기사 key로 중복을 거른다.
            last_published_at = target_news[-1].published_at
            if last_published_at.date() < search_day:
                break
            search_time = last_published_at.strftime("%H%M%S")

        return [
            news
            for news in news_by_key.values()
            if news.published_at.strftime("%Y%m%d") == search_date
        ]
