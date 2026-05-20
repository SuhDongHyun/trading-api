import time
import requests
from typing import Optional, Dict
from threading import Lock

from config import settings

# KIS 토큰은 프로세스 안에서 재사용해 불필요한 재발급을 줄인다.
_ACCESS_TOKEN: Optional[str] = None
_TOKEN_EXP: float = 0.0  # epoch seconds
_TOKEN_LOCK = Lock()


def _issue_access_token() -> tuple[str, float]:
    """한국투자증권 Open API 액세스 토큰을 발급하고 만료 시각을 반환한다."""

    url = f"{settings.kis.base_url}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": settings.kis.appkey,
        "appsecret": settings.kis.appsecret,
    }
    resp = requests.post(url, headers=headers, json=body, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"토큰 발급 실패: {data}")

    # KIS 개인 인증 토큰은 하루 단위 운용을 전제로 캐시한다.
    exp_epoch = time.time() + 86400
    return token, exp_epoch


def get_access_token(force_refresh: bool = False) -> str:
    """캐시된 액세스 토큰을 반환하되 필요하면 새 토큰을 발급한다."""

    global _ACCESS_TOKEN, _TOKEN_EXP

    now = time.time()
    if not force_refresh and _ACCESS_TOKEN and now < _TOKEN_EXP:
        return _ACCESS_TOKEN

    with _TOKEN_LOCK:
        now = time.time()
        if not force_refresh and _ACCESS_TOKEN and now < _TOKEN_EXP:
            return _ACCESS_TOKEN

        _ACCESS_TOKEN, _TOKEN_EXP = _issue_access_token()
        return _ACCESS_TOKEN


def clear_access_token_cache():
    """프로세스 안의 KIS 액세스 토큰 캐시를 초기화한다."""

    global _ACCESS_TOKEN, _TOKEN_EXP

    with _TOKEN_LOCK:
        _ACCESS_TOKEN = None
        _TOKEN_EXP = 0.0


def auth_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """KIS 호출에 필요한 공통 인증 헤더와 호출별 extra 헤더를 합친다."""

    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {get_access_token()}",
        "appkey": settings.kis.appkey,
        "appsecret": settings.kis.appsecret,
        "custtype": "P",
    }
    if extra:
        headers.update(extra)
    return headers
