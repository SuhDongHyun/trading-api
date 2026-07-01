import logging
from json import JSONDecodeError
from typing import Callable, Dict, Any, Optional
from requests import ConnectionError, Timeout, get, post, Response

from config import settings
from stock.infra.kis.kis_rate_limiter import acquire_kis_api_slot
from stock.infra.kis.kis_token_manager import auth_headers

logger = logging.getLogger(__name__)
SENSITIVE_HEADER_KEYS = {"authorization", "appkey", "appsecret"}
KIS_REQUEST_TIMEOUT_SECONDS = 10
KIS_EXPIRED_TOKEN_MSG_CODE = "EGW00123"


def build_url(path: str) -> str:
    """KIS base_url과 API path를 결합한다."""
    return f"{settings.kis.base_url}{path}"


def build_header(
    tr_id: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    force_refresh: bool = False,
):
    """인증 헤더에 TR ID와 호출별 추가 헤더를 병합한다."""

    headers = auth_headers({"tr_id": tr_id} if tr_id else None, force_refresh)
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


def is_expired_token_response(resp: Response) -> bool:
    """KIS가 토큰 만료를 HTTP 오류 본문으로 감싼 응답인지 확인한다."""

    if resp.status_code < 400:
        return False

    try:
        body = resp.json()
    except (JSONDecodeError, ValueError):
        return False

    return body.get("msg_cd") == KIS_EXPIRED_TOKEN_MSG_CODE


def log_failed_response(
    method: str,
    resp: Response,
    tr_id: Optional[str],
    payload_name: str,
    payload: Dict[str, Any],
    headers: Dict[str, str],
):
    logger.error(
        f"KIS {method} failed "
        f"status={resp.status_code} url={resp.url} tr_id={tr_id} "
        f"{payload_name}={payload} headers={safe_headers(headers)} "
        f"body={resp.text}"
    )


def send_request(
    method: str,
    request_func: Callable[..., Response],
    url: str,
    headers: Dict[str, str],
    tr_id: Optional[str],
    payload_name: str,
    payload: Dict[str, Any],
    **request_kwargs: Any,
) -> Response:
    acquire_kis_api_slot()
    try:
        return request_func(
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
    url = build_url(path)
    headers = build_header(tr_id, extra_headers)

    resp = send_request(
        method,
        request_func,
        url,
        headers,
        tr_id,
        payload_name,
        payload,
        **request_kwargs,
    )

    if is_expired_token_response(resp):
        logger.info("KIS token expired; refreshing access token and retrying once")
        headers = build_header(tr_id, extra_headers, force_refresh=True)
        resp = send_request(
            method,
            request_func,
            url,
            headers,
            tr_id,
            payload_name,
            payload,
            **request_kwargs,
        )

    if resp.status_code >= 400:
        log_failed_response(method, resp, tr_id, payload_name, payload, headers)

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
