# trading-api

한국투자증권(KIS) Open API와 시장 데이터 소스를 연결하는 읽기 전용 FastAPI 서버입니다. 계좌와 종목 시세, 일봉 기반 기술적 지표, 국내외 시장 지표를 조회합니다. 주문 기능과 데이터베이스는 없습니다.

## 주요 기능

- 계좌 보유 종목과 계좌 요약 조회
- 국내 종목 현재가와 일봉 시계열 조회
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

계좌번호와 API 자격 증명은 환경변수 또는 프로젝트 루트(config.py와 같은 디렉터리)의 로컬 `.env`에서 설정합니다. `.env`는 저장소에 올리지 마세요. `config.yaml`에는 기본 KIS 주소와 상품 코드 등 비밀이 아닌 설정만 둡니다. 중첩 설정은 `__`로 구분합니다.

```dotenv
KIS__ACCOUNT_NUM=계좌번호
KIS__APPKEY=한국투자증권_appkey
KIS__APPSECRET=한국투자증권_appsecret
FRED__API_KEY=FRED_api_key
KRX__API_KEY=KRX_api_key
```

`KIS__APPKEY`와 `KIS__APPSECRET`은 현재가·일봉·지표·뉴스·시장 지수 등 모든 KIS 기반 API 호출에 필요합니다. `KIS__ACCOUNT_NUM`은 `GET /account`에만 필요하며, 비워 두어도 서버는 시작할 수 있습니다. VIX를 조회할 때는 `FRED__API_KEY`, VKOSPI를 조회할 때는 `KRX__API_KEY`를 설정합니다. 다른 KIS 주소나 계좌 상품 코드는 `config.yaml` 또는 `KIS__BASE_URL`, `KIS__ACCOUNT_CODE`로 지정할 수 있습니다.

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
