# KIS API 호출 제한 적용 보고서

## 배경

한국투자증권 REST API는 초당 20건 호출 제한이 있다. Controller로 요청이 몰리거나, 하나의 요청이 내부적으로 여러 KIS API를 호출하면 `api_get`, `api_post` 호출 수가 제한을 초과할 수 있다.

## 적용 방식

`pyrate-limiter`를 사용해 KIS REST API 호출 전 공통 rate limiter를 통과하도록 수정했다.

- 제한값: 초당 20건
- 동작 방식: 제한 초과 시 실패하지 않고 호출 가능 슬롯이 생길 때까지 대기
- 적용 위치: `stock/infra/kis/kis_http_client.py`
- 공통 limiter: `stock/infra/kis/kis_rate_limiter.py`

## 호출 흐름

```text
controller
  -> service
    -> KISClient
      -> api_get / api_post
        -> acquire_kis_api_slot()
        -> requests.get / requests.post
```

`api_get`과 `api_post`가 같은 limiter key를 사용하므로 GET과 POST 호출이 합산되어 초당 20건으로 제한된다.

## 운영 조건

현재 구현은 단일 uvicorn 프로세스 기준의 메모리 기반 limiter다. 단일 프로세스로 실행할 때는 전체 KIS 호출이 초당 20건으로 제한된다.

`uvicorn --workers 2`처럼 여러 worker를 띄우거나 API 서버 인스턴스를 여러 개 운영하면 프로세스마다 별도 limiter가 생성된다. 그런 운영 방식이 필요해지면 Redis 등 공유 저장소 기반 limiter로 전환해야 한다.

## 검증

`tests/test_kis_rate_limit.py`를 추가해 다음을 확인했다.

- KIS API 제한값이 초당 20건인지
- 제한 초과 시 `blocking=True`로 대기하는지
- `api_get` 호출 전 limiter를 통과하는지
- `api_post` 호출 전 같은 limiter를 통과하는지
