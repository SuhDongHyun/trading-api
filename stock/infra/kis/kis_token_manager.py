import time
from threading import Lock
from typing import Callable

import requests

from config import KISSetting

TOKEN_EXPIRY_BUFFER_SECONDS = 60


class KisTokenManager:
    """컨테이너 Singleton으로 공유할 KIS 액세스 토큰을 발급하고 만료 전에 갱신한다."""

    def __init__(
        self,
        kis_settings: KISSetting,
        post: Callable | None = None,
        clock: Callable[[], float] | None = None,
    ):
        self._settings = kis_settings
        self._post = post or requests.post
        self._clock = clock or time.time
        self._access_token: str | None = None
        self._token_exp: float = 0.0
        self._lock = Lock()

    def _issue_access_token(self) -> tuple[str, float]:
        """KIS 토큰을 발급한다. 만료 여유를 빼 두어 사용 중인 토큰의 만료를 피한다."""

        url = f"{self._settings.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self._settings.appkey,
            "appsecret": self._settings.appsecret,
        }
        resp = self._post(url, headers=headers, json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        token = data.get("access_token")
        if not token:
            raise RuntimeError(f"토큰 발급 실패: {data}")

        expires_in = data.get("expires_in")
        if expires_in is None:
            raise RuntimeError(f"토큰 유효기간 누락: {data}")

        exp_epoch = self._clock() + int(expires_in) - TOKEN_EXPIRY_BUFFER_SECONDS
        return token, exp_epoch

    def get_access_token(self, force_refresh: bool = False) -> str:
        """프로세스 공유 토큰을 재사용하고, 최초 발급은 잠금으로 한 번만 수행한다."""

        now = self._clock()
        if not force_refresh and self._access_token and now < self._token_exp:
            return self._access_token

        with self._lock:
            now = self._clock()
            if not force_refresh and self._access_token and now < self._token_exp:
                return self._access_token

            self._access_token, self._token_exp = self._issue_access_token()
            return self._access_token

    def auth_headers(
        self, extra: dict[str, str] | None = None, force_refresh: bool = False
    ) -> dict[str, str]:
        """호출별 TR ID를 공통 인증 헤더와 병합한다."""

        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {self.get_access_token(force_refresh)}",
            "appkey": self._settings.appkey,
            "appsecret": self._settings.appsecret,
            "custtype": "P",
        }
        if extra:
            headers.update(extra)
        return headers
