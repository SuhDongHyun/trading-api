import time
import requests
from typing import Optional, Dict

from config import settings

# ---- 모듈 전역 캐시 (하루 1회 발급 전제) ----
_ACCESS_TOKEN: Optional[str] = None
_TOKEN_EXP: float = 0.0  # epoch seconds


def _issue_access_token() -> tuple[str, float]:
    """
    한국투자증권 Open API 액세스 토큰 발급.
    - POST {BASE_URL}/oauth2/tokenP
    - body: grant_type=client_credentials, appkey, appsecret
    - returns: (access_token, exp_epoch)
    """
    url = f"{settings.kis.base_url}oauth2/tokenP"
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

    # '하루 1회 발급'으로 간주, 안전하게 24시간(86,400초)으로 만료시간 설정
    exp_epoch = time.time() + 86400
    return token, exp_epoch


def get_access_token(force_refresh: bool = False) -> str:
    """
    액세스 토큰 반환.
    - 하루 1회 발급 전제: 캐시에 없거나 만료 시에만 새로 발급
    - force_refresh=True로 강제 재발급 가능
    """
    global _ACCESS_TOKEN, _TOKEN_EXP

    now = time.time()
    if not force_refresh and _ACCESS_TOKEN and now < _TOKEN_EXP:
        return _ACCESS_TOKEN

    _ACCESS_TOKEN, _TOKEN_EXP = _issue_access_token()
    return _ACCESS_TOKEN


def auth_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    공통 인증 헤더 생성.
    - Authorization: Bearer {token}
    - appkey/appsecret/custtype 포함
    - 주문/정정/취소 시 tr_id, hashkey 등은 extra 인자로 추가
    """
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
