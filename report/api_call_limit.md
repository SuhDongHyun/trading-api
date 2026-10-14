# KIS API 호출 제한 적용 보고서

## 배경

KIS 호출 한도는 appkey 단위로 적용되며, 정확한 수치는 한국투자증권 API 포털의 최신 공지를 기준으로 한다. 이 서비스는 공지 한도보다 보수적으로, 한 요청이 여러 KIS API를 연달아 부르는 경우의 burst까지 막기 위해 초당 10건 창과 최소 150ms 간격을 적용한다. 두 제한을 함께 적용한 실효 상한은 약 6.6건/s다.

## 적용 방식

`pyrate-limiter`와 최소 간격 제한을 사용해 KIS GET 요청 전 공통 limiter를 통과시킨다.

- 제한값: 초당 최대 10건, 호출 사이 최소 150ms
- 동작 방식: 제한을 넘으면 대기한 뒤 호출
- 적용 위치: `stock/infra/kis/kis_http_client.py`
- 공통 limiter: `stock/infra/kis/kis_rate_limiter.py`

## 호출 흐름

```text
controller
  -> service
    -> KIS adapter
      -> KisHttpClient.get
        -> KisRateLimiter.acquire()
        -> requests.get
```

초당 10건 창과 150ms 간격을 모두 적용한다. 최소 간격이 실효 처리량을 약 6.6건/s로 제한한다.

## 운영 조건

현재 구현은 단일 uvicorn 프로세스 기준의 메모리 기반 limiter다. 단일 프로세스에서 전체 KIS GET 요청은 초당 약 6.6건 이하로 통과한다. 모의투자 REST는 실전보다 한도가 낮으므로 사용할 때는 공지된 한도에 맞게 별도 설정이 필요하다.

`uvicorn --workers 2`처럼 여러 worker를 띄우거나 API 서버 인스턴스를 여러 개 운영하면 프로세스마다 별도 limiter가 생성된다. 그런 운영 방식이 필요해지면 Redis 등 공유 저장소 기반 limiter로 전환해야 한다.

## 검증

`tests/test_kis_rate_limit.py`와 `tests/test_min_interval_throttle.py`에서 다음을 확인한다.

- KIS API 제한값이 초당 10건인지
- 공용 최소 간격 throttle이 150ms 대기를 적용하는지
- 제한 초과 시 `blocking=True`로 대기하는지
- GET 호출 전 limiter를 통과하는지
