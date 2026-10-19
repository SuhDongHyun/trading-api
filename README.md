# trading-api

한국투자증권(KIS) Open API, Upbit Quotation API와 시장 데이터 소스를 연결하는 읽기 전용 FastAPI 서버입니다. 계좌와 주식·가상자산 시세, 일봉 기반 기술적 지표, 국내외 시장 지표를 조회합니다. 주문 기능과 데이터베이스는 없습니다.

## 주요 기능

- 계좌 보유 종목과 계좌 요약 조회
- 국내 종목 현재가와 일봉 시계열 조회
- Upbit 페어 목록, 현재가, 호가 정책, 호가, 최근 체결 내역과 초·분·일·주·월·연 캔들 조회
- 일봉 가격을 이용한 이동평균, RSI, RSI signal, MACD, MACD signal 계산
- KOSPI, KOSDAQ, S&P 500, VKOSPI, VIX, 공포탐욕지수 조회
- USD/KRW 환율과 한국·미국 국채 수익률 조회
- KIS 액세스 토큰 캐시, 만료 토큰 재시도, 프로세스 단위 호출 제한

## 실행

Python 3.12 이상과 `uv`가 필요합니다.

```bash
uv sync
uv run python main.py
```

서버는 기본적으로 `http://localhost:9999`에서 실행됩니다. FastAPI 문서는 `http://localhost:9999/docs`에서 확인할 수 있습니다.

## 설정

계좌번호와 API 자격 증명은 환경변수 또는 프로젝트 루트(config.py와 같은 디렉터리)의 로컬 `.env`에서 설정합니다. `.env`는 저장소에 올리지 마세요. `config.yaml`에는 기본 KIS·Upbit 주소와 상품 코드 등 비밀이 아닌 설정만 둡니다. 중첩 설정은 `__`로 구분합니다. Upbit Quotation API는 공개 API이므로 access key나 secret key를 설정하지 않습니다.

```dotenv
KIS__ACCOUNT_NUM=계좌번호
KIS__APPKEY=한국투자증권_appkey
KIS__APPSECRET=한국투자증권_appsecret
FRED__API_KEY=FRED_api_key
KRX__API_KEY=KRX_api_key
UPBIT__BASE_URL=https://api.upbit.com
```

`KIS__APPKEY`와 `KIS__APPSECRET`은 현재가·일봉·지표·뉴스·시장 지수 등 모든 KIS 기반 API 호출에 필요합니다. `KIS__ACCOUNT_NUM`은 `GET /account`에만 필요하며, 비워 두어도 서버는 시작할 수 있습니다. VIX를 조회할 때는 `FRED__API_KEY`, VKOSPI를 조회할 때는 `KRX__API_KEY`를 설정합니다. 다른 KIS 주소나 계좌 상품 코드는 `config.yaml` 또는 `KIS__BASE_URL`, `KIS__ACCOUNT_CODE`로 지정할 수 있습니다.

Upbit 주소는 기본적으로 `https://api.upbit.com`이며, 필요하면 `config.yaml` 또는 `UPBIT__BASE_URL`로 바꿀 수 있습니다.

## API 예시

### 현재가 조회

```bash
curl -X POST http://localhost:9999/stock_quote \
  -H "Content-Type: application/json" \
  -d '{"market":"J","code":"005930"}'
```

### 일봉 데이터 조회

```bash
curl -X POST http://localhost:9999/stock_quote/daily \
  -H "Content-Type: application/json" \
  -d '{"market":"J","code":"005930","start_date":"20260101","end_date":"20260107","adjusted_price":true}'
```

시세와 지표 API는 일봉만 지원합니다. 요청 본문에 `period`를 보내지 않습니다. 제거된 `period` 같은 추가 필드를 보내면 요청 검증에서 422를 반환합니다.

### 시장 지표 조회

```bash
curl -X POST http://localhost:9999/market-index/usd-krw-exchange-rate \
  -H "Content-Type: application/json" \
  -d '{"start_date":"20260101","end_date":"20260107"}'
```

```bash
curl -X POST http://localhost:9999/market-index/treasury-yield/us-10y \
  -H "Content-Type: application/json" \
  -d '{"start_date":"20260101","end_date":"20260107"}'
```

### Upbit 현재가와 호가 조회

```bash
curl -X POST http://localhost:9999/bitcoin/ticker \
  -H "Content-Type: application/json" \
  -d '{"markets":["KRW-BTC","KRW-ETH"]}'
```

```bash
curl -X POST http://localhost:9999/bitcoin/orderbook \
  -H "Content-Type: application/json" \
  -d '{"markets":["KRW-BTC"],"level":"0","count":10}'
```

### Upbit 캔들 조회

```bash
curl -X POST http://localhost:9999/bitcoin/candles/minutes/5 \
  -H "Content-Type: application/json" \
  -d '{"market":"KRW-BTC","to":"2025-07-01T00:00:00Z","count":200}'
```

캔들 요청은 `market`을 필수로 받으며 `count`는 1~200입니다. `to`는 ISO 8601 datetime이고, 분 단위 경로는 1, 3, 5, 10, 15, 30, 60, 240 중 하나를 사용합니다. 일 캔들 요청에는 선택적으로 `converting_price_unit: "KRW"`를 지정할 수 있습니다. 각 요청은 Upbit를 한 번 호출하며 페이지네이션은 하지 않습니다.

## 엔드포인트

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/account` | 보유 종목 및 계좌 요약 |
| POST | `/stock_quote` | 종목 현재가 |
| POST | `/stock_quote/daily` | 종목 일봉 시계열 |
| POST | `/stock_quote/daily/moving-average` | 이동평균 |
| POST | `/stock_quote/indicator/rsi` | RSI |
| POST | `/stock_quote/indicator/rsi-signal` | RSI와 EMA 신호 |
| POST | `/stock_quote/indicator/macd` | MACD |
| POST | `/stock_quote/indicator/macd-signal` | MACD와 EMA 신호 |
| POST | `/stock_news` | 종목 뉴스 |
| GET | `/market-index/korea-stock-list` | 국내 상장 종목 목록 |
| GET | `/market-index/fear-and-greed-index` | CNN 공포탐욕지수 |
| POST | `/market-index/vix-index` | FRED VIX 시계열 |
| POST | `/market-index/vkospi-index` | KRX VKOSPI 시계열 |
| POST | `/market-index/usd-krw-exchange-rate` | USD/KRW 환율 |
| POST | `/market-index/treasury-yield/{maturity}` | 국채 수익률 |
| POST | `/market-index/sp500-index` | S&P 500 시계열 |
| POST | `/market-index/kospi-index` | KOSPI 시계열 |
| POST | `/market-index/kosdaq-index` | KOSDAQ 시계열 |
| POST | `/bitcoin/trading-pairs` | Upbit 지원 페어 목록 |
| POST | `/bitcoin/ticker` | 페어별 현재가 |
| POST | `/bitcoin/ticker/quote` | KRW·BTC·USDT 호가 통화별 현재가 |
| POST | `/bitcoin/orderbook` | 페어 호가 |
| POST | `/bitcoin/orderbook/instruments` | 페어별 호가 정책 |
| POST | `/bitcoin/trades` | 최근 페어 체결 내역 |
| POST | `/bitcoin/candles/seconds` | 초 캔들 |
| POST | `/bitcoin/candles/minutes/{unit}` | 분 캔들(허용 단위: 1, 3, 5, 10, 15, 30, 60, 240) |
| POST | `/bitcoin/candles/days` | 일 캔들(선택적 KRW 종가 환산) |
| POST | `/bitcoin/candles/weeks` | 주 캔들 |
| POST | `/bitcoin/candles/months` | 월 캔들 |
| POST | `/bitcoin/candles/years` | 연 캔들 |

국채 만기 값은 `korea-1y`, `korea-3y`, `korea-5y`, `korea-10y`, `us-1y`, `us-10y`입니다. 날짜 입력은 YYYYMMDD 형식의 실제 날짜여야 하며, 잘못된 요청은 Pydantic 검증 오류(422)로 응답합니다.

## 노트북 의존성

노트북 실험에 필요한 패키지는 기본 설치에서 제외되어 있습니다. 사용할 때만 별도 group을 설치합니다.

```bash
uv sync --group notebook
```

## 테스트와 정적 검사

```bash
uv run pytest
uv run ruff check
```
