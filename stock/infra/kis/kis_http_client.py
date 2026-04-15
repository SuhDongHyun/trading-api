from __future__ import annotations

from requests import get, post, Response
from typing import Dict, Any, Optional

from config import settings
from stock.infra.kis.kis_token_manager import auth_headers


def build_url(path: str) -> str:
    """BASE_URL + path 조합"""
    return f"{settings.kis.base_url}{path}"


def build_header(
    tr_id: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None
):
    headers = auth_headers({"tr_id": tr_id} if tr_id else None)
    if extra_headers:
        headers.update(extra_headers)
    return headers


def api_get(
    path: str,
    params: Dict[str, str] | None = None,
    tr_id: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Response:
    """한국투자증권 API 공통 GET 호출"""
    resp = get(
        url=build_url(path),
        headers=build_header(tr_id, extra_headers),
        params=params or {},
    )
    resp.raise_for_status()
    return resp


def api_post(
    path: str,
    body: Dict[str, Any] | None = None,
    tr_id: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Response:
    """한국투자증권 API 공통 POST 호출"""
    resp = post(
        url=build_url(path),
        headers=build_header(tr_id, extra_headers),
        json=body or {},
    )
    resp.raise_for_status()
    return resp
