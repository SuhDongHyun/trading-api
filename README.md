# trading-api

한국투자증권(KIS) Open API를 FastAPI로 감싼 국내 주식 조회 API입니다. 계좌 요약, 현재가, 일봉 데이터와 이동평균/RSI/MACD 같은 기술적 지표를 제공합니다.

```text
Client
  |
  v
FastAPI Controller  ->  Service  ->  KIS Adapter  ->  Korea Investment Open API
                         |
                         +-> Indicator calculators
```

## 주요 기능

- 계좌 보유 종목과 계좌 요약 조회
- 국내 주식 현재가 조회
- 일/주/월/년 단위 가격 데이터 조회
- 이동평균, RSI, RSI signal, MACD, MACD signal 계산
- KIS 인증 토큰 캐싱과 API 호출 속도 제한

## 실행

Python 3.12 이상과 `uv`가 필요합니다.

```bash
uv sync
uv run python main.py
```

서버는 기본적으로 `http://localhost:9999`에서 실행됩니다. FastAPI 문서는 `http://localhost:9999/docs`에서 확인할 수 있습니다.

## 설정

KIS 계정 정보는 `config.yaml`과 `.env`에서 읽습니다. 공개 저장소에는 실제 키를 올리지 마세요.

```yaml
# config.yaml
app:
  kis:
    base_url: "https://openapi.koreainvestment.com:9443/"
    account_num: "계좌번호"
    account_code: "상품코드"
```

```bash
# .env
KIS__APPKEY=your_app_key
KIS__APPSECRET=your_app_secret
```

## API 예시

### 현재가 조회

```bash
curl -X POST http://localhost:9999/stock_quote \
  -H "Content-Type: application/json" \
  -d '{"market":"J","code":"005930"}'
```

주요 필드 예시:

```json
{
  "market_name": "KOSPI",
  "code": "005930",
  "industry": "전기전자",
  "current_price": 72000,
  "price_diff": 500,
  "price_diff_rate": 0.7
}
```

### 일봉 데이터 조회

```bash
curl -X POST http://localhost:9999/stock_quote/daily \
  -H "Content-Type: application/json" \
  -d '{"market":"J","code":"005930","start_date":"20260101","end_date":"20260107","period":"D","adjusted_price":true}'
```

### 지표 조회

```bash
curl -X POST http://localhost:9999/stock_quote/indicator/rsi \
  -H "Content-Type: application/json" \
  -d '{"market":"J","code":"005930","start_date":"20260101","end_date":"20260131","period":"D","rsi_window":14}'
```

## 엔드포인트

| Method | Path | 설명 |
| --- | --- | --- |
| `GET` | `/account` | 보유 종목과 계좌 요약 조회 |
| `POST` | `/stock_quote` | 현재가 조회 |
| `POST` | `/stock_quote/daily` | 기간별 가격 데이터 조회 |
| `POST` | `/stock_quote/daily/moving-average` | 이동평균 조회 |
| `POST` | `/stock_quote/indicator/rsi` | RSI 조회 |
| `POST` | `/stock_quote/indicator/rsi-signal` | RSI signal 조회 |
| `POST` | `/stock_quote/indicator/macd` | MACD 조회 |
| `POST` | `/stock_quote/indicator/macd-signal` | MACD signal 조회 |

## 테스트

```bash
uv run pytest
```
