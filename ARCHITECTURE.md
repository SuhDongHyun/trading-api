# ARCHITECTURE

현재 저장소 코드 기준의 구조와 운영상 확인할 점을 정리합니다.

## 1. 개요

trading-api는 외부 시세·시장 데이터를 조회해 FastAPI 응답으로 변환하는 읽기 전용 서버입니다. 주문 기능이나 데이터베이스는 없습니다. Python 3.12 이상, uv, FastAPI와 dependency-injector를 사용합니다. 기본 서버 주소는 포트 9999입니다.

| 외부 소스 | 용도 | 연동 방식 |
| --- | --- | --- |
| 한국투자증권(KIS) Open API | 계좌, 종목 시세·뉴스, 국내외 지수, 환율, 국채 | requests를 쓰는 공통 HTTP client |
| FRED | VIX 시계열 | fredapi |
| CNN Fear & Greed | 공포탐욕지수 | fear-and-greed 라이브러리 |
| KRX Open API | VKOSPI | requests |
| Upbit Quotation API | 페어·현재가·호가·체결 | 공개 REST API, requests |
| FinanceDataReader | 국내 상장 종목 목록 | 라이브러리 |
| exchange-calendars | KRX 거래일 계산 | XKRX 캘린더와 프로세스 캐시 |

## 2. 디렉터리와 역할

- 루트의 main.py는 FastAPI 앱, 라우터 등록, lifespan의 KRX 캘린더 warm-up, 전역 예외 handler를 설정합니다. container.py는 객체 생성과 주입을 정의하고 config.py는 설정 소스를 합칩니다.
- common/exchange_calendar.py는 XKRX 캘린더를 프로세스 안에서 캐시합니다. common/min_interval_throttle.py는 여러 API에서 쓰는 최소 호출 간격과 동시성 제어를 제공합니다.
- stock/domain은 dataclass 도메인 모델, 포트(ABC), 애플리케이션 예외를 둡니다. 포트는 stock/domain/port 아래에 있습니다.
- stock/service는 계좌, 종목 시세, 뉴스, 시장 지표 유스케이스를 조합합니다. stock/service/indicator는 이동평균·RSI·MACD 계산과 일봉 조회 구간/warm-up 계산을 담당합니다. 날짜 구간 계산은 KRX 캘린더를 사용합니다.
- stock/infra는 외부 연동 어댑터를 둡니다. infra/kis에는 계좌·시세·뉴스·국내 지수·해외 지수 어댑터, 공통 HTTP client, 토큰 관리자, rate limiter와 조회 유틸이 있습니다. infra/krx의 KRXClient는 종목 목록과 VKOSPI 포트를 구현합니다. infra/fred는 VIX, infra/cnn은 공포탐욕지수를 담당합니다.
- stock/interface/controller는 FastAPI 라우터, stock/interface/schema는 Pydantic 요청·응답 모델을 둡니다.
- bitcoin/domain은 Upbit 페어·현재가·호가·체결 dataclass와 역할별 포트를 둡니다. bitcoin/service는 조회 유스케이스, bitcoin/infra/upbit은 공개 REST 어댑터·HTTP client·그룹별 rate limiter, bitcoin/interface는 `/bitcoin` 라우터와 schema를 둡니다.
- tests는 외부 호출을 대역(Mock/Fake)으로 바꾸는 단위 테스트와 TestClient 기반 API 테스트를 포함합니다.

stock과 bitcoin 패키지에는 __init__.py가 없어 Python namespace package로 동작합니다. 현재 pytest와 Ruff 실행에 문제는 없지만, 패키징 도구를 추가할 때 다시 확인할 수 있습니다.

## 3. 계층과 의존 방향

HTTP 요청은 controller에서 schema 검증을 거친 뒤 service를 호출합니다. service는 domain port와 순수 지표 계산 함수에 의존합니다. infra 어댑터가 port를 구현하며 외부 API 응답을 도메인 모델로 변환합니다. container.py가 어댑터를 service에 주입합니다.

domain은 FastAPI, KIS, requests 등 인프라 세부 사항을 참조하지 않습니다. 다만 stock/service/indicator/date_ranges.py는 거래일 기준 조회 구간을 계산하기 위해 common/exchange_calendar.py를 사용합니다.

## 4. 설정과 객체 생명주기

config.py의 AppSettings는 다음 순서로 설정을 합칩니다.

1. 생성자 인자
2. 환경변수
3. 로컬 .env
4. config.yaml
5. 파일 secret

중첩 환경변수 구분자는 __입니다. .env 경로는 config.py가 있는 디렉터리를 기준으로 합니다. 계좌번호는 KIS__ACCOUNT_NUM 환경변수 또는 .env에서 받으며 기본값은 빈 문자열입니다. 따라서 계좌번호 없이도 앱은 시작할 수 있고, 계좌 조회를 하려면 값을 설정해야 합니다. config.yaml에는 기본 KIS 주소와 계좌 상품 코드 등 비밀이 아닌 설정이 있습니다. Upbit는 공개 Quotation API만 사용하며 base URL은 `app.upbit.base_url` 또는 `UPBIT__BASE_URL`로 지정합니다. Access key와 secret key 설정은 없습니다.

Container는 controller 패키지를 wiring_config로 자동 연결합니다. main.py에서 별도의 container.wire 호출은 하지 않습니다.

- KisTokenManager, KisRateLimiter, KisHttpClient는 Singleton입니다. 토큰과 호출 제한 상태를 프로세스 안에서 공유합니다.
- UpbitRateLimiter와 UpbitHttpClient는 Singleton입니다. 그룹별 호출 제한 상태를 프로세스 안에서 공유하며 인증 헤더와 Origin 헤더를 전송하지 않습니다.
- KIS 역할별 어댑터는 Factory이며 같은 KisHttpClient를 주입받습니다.
- Upbit 역할별 어댑터와 서비스는 Factory이며 같은 UpbitHttpClient를 주입받습니다.
- KRXClient는 Singleton으로 만들어 종목 목록 포트와 VKOSPI 포트가 같은 인스턴스를 사용합니다.
- 서비스와 나머지 외부 client는 Factory입니다.

## 5. 요청 흐름과 공통 동작

### 5.1 종목 시세와 지표

현재가 요청은 controller → StockQuoteService → StockQuoteClient → KisStockQuoteClient → KisHttpClient 순서로 처리됩니다. KIS의 기본 종목 정보와 현재가 응답을 합치고 요청받은 종목 코드를 보존해 StockInfo를 만듭니다.

일봉과 지표 요청은 KIS 기간 코드를 내부에서 D로 고정합니다. 요청 스키마에는 period가 없습니다. 국내 시세 구간은 KRX 거래일 기준 100개씩 나누고, 해외 지수는 KRX 휴장일 누락을 피하도록 달력일 기준 최대 100일씩 나눕니다. KIS 각 페이지는 최신순으로 오므로 유틸이 페이지를 뒤집어 시간순으로 합칩니다.

이동평균·RSI·MACD는 요청 시작일보다 앞선 가격이 필요한 경우 거래일 기준 warm-up 구간을 추가로 조회한 뒤 요청 구간을 계산합니다. RSI는 사용자가 확정한 단순 rolling mean 공식을 유지합니다. MACD의 EMA seed 오차 기준은 요청 구간의 마지막 종가를 사용하므로 현재가 API를 추가 호출하지 않습니다.

### 5.2 KIS HTTP, 토큰과 호출 제한

KisHttpClient.get은 토큰 관리자가 구성한 인증 헤더에 TR ID를 추가하고 GET 요청에 공통 limiter를 적용합니다. 토큰 관리자는 /oauth2/tokenP로 별도 POST 요청을 보내 토큰을 발급하며, 응답에 access_token이 없으면 ExternalApiError를 냅니다. Lock으로 동시 최초 발급을 한 번으로 제한하고 만료 60초 전부터 새 토큰을 사용합니다. 만료 오류 응답은 토큰을 갱신한 뒤 한 번 재시도합니다.

KisHttpClient.get은 JSON 응답에 rt_cd 필드가 있으면 확인하고, 값이 0이 아닐 때 응답의 msg_cd/msg1을 진단 정보로 포함한 외부 API 예외를 냅니다. rt_cd 필드가 없는 응답은 검사 없이 반환합니다. 토큰 발급 응답은 KisHttpClient.get을 거치지 않고 KisTokenManager가 직접 처리합니다. 연결 오류와 외부 HTTP 오류는 FastAPI handler에서 502로 변환되며, 로그에는 외부 요청의 query와 인증 정보를 남기지 않습니다.

KIS limiter는 초당 10건 제한과 호출 사이 최소 150ms 간격을 함께 적용합니다. 실효 상한은 약 6.6건/s입니다. KRX VKOSPI 조회도 날짜별 순차 호출이며 각 호출 사이 최소 100ms를 둡니다.

### 5.3 시장 지표

MarketIndexService가 기능별 포트를 직접 호출합니다. KOSPI/KOSDAQ 코드, 환율 코드, S&P 500 코드와 국채 코드는 service에 매핑되어 있으며, 별도 조합형 MarketIndexClient는 없습니다.

| 항목 | 포트 | 어댑터/소스 |
| --- | --- | --- |
| 국내 상장 종목 | KoreaStockListClient | KRXClient → FinanceDataReader |
| VKOSPI | VkospiClient | KRXClient → KRX Open API |
| VIX | VixClient | FredClient → FRED VIXCLS |
| 공포탐욕지수 | FearGreedClient | CnnFearGreedClient → CNN 라이브러리 |
| 종목 계좌·시세·뉴스 | AccountClient, StockQuoteClient, NewsClient | 역할별 KIS 어댑터 |
| 국내·해외 시장 지수 | DomesticMarketIndexClient, OverseasMarketIndexClient | 역할별 KIS 어댑터 |

### 5.4 Upbit Quotation API

요청은 `/bitcoin` controller → 역할별 service → domain port → Upbit 어댑터 → 공통 `UpbitHttpClient` 흐름으로 처리됩니다. 어댑터는 응답 JSON을 dataclass로 바꾸고 controller가 Pydantic 응답 schema로 변환합니다. `market` 목록은 쉼표로 합쳐 Upbit에 전달합니다.

Upbit의 Quotation REST 호출 제한은 IP 기준 그룹별 초당 10회입니다. 페어 목록은 `market`, 캔들 여섯 종류는 공유 `candle`, 체결은 `trade`, 두 현재가 API는 공유 `ticker`, 호가와 호가 정책은 공유 `orderbook` 그룹을 사용합니다. 공개 API를 사용하므로 인증·Origin 헤더를 붙이지 않습니다. 404는 `NotFoundError`(404), 429·418 등 나머지 Upbit HTTP 오류는 `ExternalApiError`(502)로 변환합니다. 진단 정보는 오류 본문의 이름과 메시지를 포함하고 URL query는 기록하지 않습니다.

### 5.5 입력 검증과 오류 응답

Pydantic 스키마가 날짜 형식과 실제 날짜, 날짜 순서, 지표 window 등 요청 값을 검증합니다. 잘못된 입력은 FastAPI 기본 422 응답입니다. AppError 계층은 NotFoundError(404)와 ExternalApiError(502)를 제공하고 main.py의 handler가 상태 코드와 안전한 진단 로그를 기록합니다. requests.RequestException도 502로 변환합니다.

## 6. HTTP 엔드포인트

| Method | Path | 처리 |
| --- | --- | --- |
| GET | /account | 보유 종목 및 계좌 요약 |
| POST | /stock_quote | 종목 현재가 |
| POST | /stock_quote/daily | 종목 일봉 시세 |
| POST | /stock_quote/daily/moving-average | 이동평균 |
| POST | /stock_quote/indicator/rsi | RSI |
| POST | /stock_quote/indicator/rsi-signal | RSI 신호 |
| POST | /stock_quote/indicator/macd | MACD |
| POST | /stock_quote/indicator/macd-signal | MACD 신호 |
| POST | /stock_news | 종목 뉴스 |
| GET | /market-index/korea-stock-list | 국내 상장 종목 목록 |
| GET | /market-index/fear-and-greed-index | 공포탐욕지수 |
| POST | /market-index/vix-index | VIX |
| POST | /market-index/vkospi-index | VKOSPI |
| POST | /market-index/usd-krw-exchange-rate | USD/KRW 환율 |
| POST | /market-index/treasury-yield/{maturity} | 국채 수익률 |
| POST | /market-index/sp500-index | S&P 500 |
| POST | /market-index/kospi-index | KOSPI |
| POST | /market-index/kosdaq-index | KOSDAQ |
| POST | /bitcoin/trading-pairs | 지원 페어 목록 및 선택적 상세 정보 |
| POST | /bitcoin/ticker | 페어별 현재가 |
| POST | /bitcoin/ticker/quote | 호가 통화별 현재가 |
| POST | /bitcoin/orderbook | 실시간 호가 |
| POST | /bitcoin/orderbook/instruments | 페어별 호가 단위 정책 |
| POST | /bitcoin/trades | 최근 페어 체결 내역 |
| POST | /bitcoin/candles/seconds | 초 캔들 |
| POST | /bitcoin/candles/minutes/{unit} | 분 캔들(1, 3, 5, 10, 15, 30, 60, 240) |
| POST | /bitcoin/candles/days | 일 캔들(선택적 KRW 종가 환산) |
| POST | /bitcoin/candles/weeks | 주 캔들 |
| POST | /bitcoin/candles/months | 월 캔들 |
| POST | /bitcoin/candles/years | 연 캔들 |

국채 maturity 값은 korea-1y, korea-3y, korea-5y, korea-10y, us-1y, us-10y입니다.

## 7. 테스트와 운영 범위

uv run pytest는 외부 서비스를 실제로 호출하지 않고 어댑터·서비스 동작을 대역 객체로 확인합니다. tests/test_interface_routes.py와 tests/test_exception_handlers.py는 실제 FastAPI 앱에 TestClient를 연결해 라우트 계약과 오류 매핑을 검증합니다.

토큰, 호출 limiter, 거래일 캘린더는 프로세스 메모리에 있습니다. 여러 uvicorn worker나 여러 서버 인스턴스를 실행하면 limiter와 캐시가 공유되지 않습니다. 다중 인스턴스 운영에는 분산 상태 저장소가 필요합니다.

## 8. 해결된 구조 문제와 남은 확인 사항

### 해결된 구조와 계약

- 포트는 계좌·시세·뉴스·시장 기능별로 나뉘며 구현 어댑터는 infra에 있습니다. KIS HTTP client, 토큰 관리자와 rate limiter는 공유 Singleton입니다. 시장 지표 service가 포트를 직접 사용하고 지표 코드를 매핑합니다.
- 응답 모델의 속성 변환, 공통 날짜 검증, 국채 경로 통합, Signal 타입, EMA 계산과 KIS 구간 조회 공통화가 적용되어 있습니다. 시세/지표 입력은 일봉이며 period 필드는 허용되지 않습니다. 날짜는 요청에서 필수로 받으며 하드코딩 기본 날짜는 없습니다.
- 종목 식별자와 숫자 응답을 정규화합니다. MACD seed 기준은 기존 가격 데이터로 계산하며 현재가 추가 호출은 하지 않습니다. RSI는 단순 rolling mean을 쓰고 avg_loss=0 경계를 처리합니다.
- 앱 설정은 KIS 계좌번호 없이도 구성됩니다. matplotlib, plotly, nbformat은 선택적 notebook dependency group에 있고, 운영 코드는 이 패키지들을 import하지 않습니다.

### 남은 항목과 검증 한계

- KIS의 HTTP 200 업무 오류는 rt_cd 검사로 처리하지만, 빈 페이지가 실제 KIS에서 rt_cd=0으로 오는지 확인하지 않았습니다. 아주 오래된 국내 지수 구간, 기사가 없는 날짜의 뉴스, 없는 종목코드 일봉에서의 rt_cd/msg_cd 동작은 mock 테스트만 있습니다. 실제 API 확인이 필요합니다.
- date_ranges.py가 캘린더를 직접 조회하므로 지표 구간 계산은 완전한 순수 함수 계층이 아닙니다. controller가 container를 import하는 구조도 유지됩니다.
- VKOSPI는 거래일마다 순차 호출하므로 긴 구간 조회가 느릴 수 있습니다. 간격 제한은 있으나 재시도나 일괄 구간 API는 없습니다.
- 데이터가 일부만 있는 종목 이력에서는 요청한 warm-up 길이를 채우지 못해 결과가 짧거나 EMA seed 영향이 남을 수 있습니다. 이는 신규 상장·거래 정지·과거 데이터 제공 한계와 관련된 위험입니다.
- stock은 namespace package로 유지합니다. 현재 pytest와 Ruff에는 문제가 없으나, 추가 패키징이나 타입 검사 도구가 도입되면 __init__.py 필요성을 확인할 수 있습니다.
- 테스트는 외부 API를 mock으로 격리하므로 실제 서비스 자격 증명, 응답 형식, 호출 제한과 빈 페이지 계약을 검증하지 않습니다.
