from typing import Callable

import requests
from requests import Response

from config import UpbitSetting
from stock.domain.exceptions import ExternalApiError, NotFoundError
from bitcoin.infra.upbit.upbit_rate_limiter import UpbitRateLimiter

UPBIT_REQUEST_TIMEOUT_SECONDS = 10


class UpbitHttpClient:
    """공개 Quotation GET 요청에 공통 timeout, limiter와 오류 매핑을 적용한다."""

    def __init__(
        self,
        upbit_settings: UpbitSetting,
        rate_limiter: UpbitRateLimiter,
        get: Callable[..., Response] | None = None,
    ):
        self._settings = upbit_settings
        self._rate_limiter = rate_limiter
        self._get = get or requests.get

    def get(
        self,
        path: str,
        params: dict[str, str | int] | None = None,
        rate_limit_group: str = "market",
    ) -> Response:
        """지정된 그룹 한도를 통과한 뒤 인증·Origin 헤더 없이 요청한다."""

        self._rate_limiter.acquire(rate_limit_group)
        response = self._get(
            url=f"{self._settings.base_url}{path}",
            params=params or {},
            timeout=UPBIT_REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code >= 400:
            diagnostic = self._diagnostic(path, response)
            if response.status_code == 404:
                raise NotFoundError(
                    "Upbit에서 요청한 시세 데이터를 찾을 수 없습니다.",
                    diagnostic=diagnostic,
                )
            raise ExternalApiError(
                "Upbit API 요청에 실패했습니다.", diagnostic=diagnostic
            )
        return response

    @staticmethod
    def _diagnostic(path: str, response: Response) -> str:
        """오류 응답의 식별 정보만 보존하고 요청 쿼리를 기록하지 않는다."""

        try:
            body = response.json()
        except ValueError:
            body = None
        error = body.get("error") if isinstance(body, dict) else None
        if not isinstance(error, dict):
            return f"Upbit GET failed path={path} status={response.status_code}"

        name = str(error.get("name", ""))[:100]
        message = str(error.get("message", ""))[:300]
        return (
            f"Upbit GET failed path={path} status={response.status_code} "
            f"error_name={name} error_message={message}"
        )
