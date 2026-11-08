import logging

from fastapi.testclient import TestClient

import main


def test_health_returns_ok_without_external_calls():
    response = TestClient(main.app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def make_access_record(path: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=0,
        msg='%s - "%s %s HTTP/%s" %d',
        args=("127.0.0.1:1234", "GET", path, "1.1", 200),
        exc_info=None,
    )


def test_health_access_log_is_filtered():
    access_filter = main.HealthCheckAccessFilter()

    assert access_filter.filter(make_access_record("/health")) is False
    assert access_filter.filter(make_access_record("/health?probe=1")) is False
    assert access_filter.filter(make_access_record("/stock_quote")) is True
