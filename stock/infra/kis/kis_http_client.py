import logging
from typing import Callable, Dict, Any, Optional
from requests import ConnectionError, Timeout, get, post, Response

from config import settings
from stock.infra.kis.kis_rate_limiter import acquire_kis_api_slot
from stock.infra.kis.kis_token_manager import auth_headers

logger = logging.getLogger(__name__)
SENSITIVE_HEADER_KEYS = {"authorization", "appkey", "appsecret"}
KIS_REQUEST_TIMEOUT_SECONDS = 10


def build_url(path: str) -> str:
    """KIS base_url과 API path를 결합한다."""
    return f"{settings.kis.base_url}{path}"


def build_header(
    tr_id: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None
):
    """인증 헤더에 TR ID와 호출별 추가 헤더를 병합한다."""

    headers = auth_headers({"tr_id": tr_id} if tr_id else None)
    if extra_headers:
        headers.update(extra_headers)
    return headers


def safe_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """로그에 남기면 안 되는 인증 헤더를 제거한다."""

    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in SENSITIVE_HEADER_KEYS
    }


def _api_request(
    method: str,
    request_func: Callable[..., Response],
    path: str,
    *,
    tr_id: Optional[str],
    extra_headers: Optional[Dict[str, str]],
    payload_name: str,
    payload: Dict[str, Any],
    **request_kwargs: Any,
) -> Response:
    """공통 인증/에러 처리를 적용한 한국투자증권 HTTP 호출."""
    acquire_kis_api_slot()
    url = build_url(path)
    headers = build_header(tr_id, extra_headers)

    try:
        resp = request_func(
            url=url,
            headers=headers,
            timeout=KIS_REQUEST_TIMEOUT_SECONDS,
            **request_kwargs,
        )
    except (ConnectionError, Timeout):
        logger.exception(
            f"KIS {method} connection failed "
            f"url={url} tr_id={tr_id} "
            f"{payload_name}={payload} headers={safe_headers(headers)}"
        )
        raise

    if resp.status_code >= 400:
        logger.error(
            f"KIS {method} failed "
            f"status={resp.status_code} url={resp.url} tr_id={tr_id} "
            f"{payload_name}={payload} headers={safe_headers(headers)} "
            f"body={resp.text}"
        )

    resp.raise_for_status()
    return resp


def api_get(
    path: str,
    params: Dict[str, str] | None = None,
    tr_id: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Response:
    """공통 인증/에러 처리를 적용한 한국투자증권 GET 호출."""
    params = params or {}
    return _api_request(
        "GET",
        get,
        path,
        tr_id=tr_id,
        extra_headers=extra_headers,
        payload_name="params",
        payload=params,
        params=params,
    )


def api_post(
    path: str,
    body: Dict[str, Any] | None = None,
    tr_id: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Response:
    """공통 인증/에러 처리를 적용한 한국투자증권 POST 호출."""
    body = body or {}
    return _api_request(
        "POST",
        post,
        path,
        tr_id=tr_id,
        extra_headers=extra_headers,
        payload_name="body",
        payload=body,
        json=body,
    )
