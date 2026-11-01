"""서비스와 외부 연동에서 사용하는 애플리케이션 예외 계층."""


class AppError(Exception):
    """HTTP 응답 상태와 운영 로그용 진단 정보를 함께 전달한다."""

    status_code = 500

    def __init__(self, message: str, *, diagnostic: str | None = None):
        super().__init__(message)
        self.diagnostic = diagnostic or message


class NotFoundError(AppError):
    """요청한 도메인 대상을 찾지 못한 경우에 사용한다."""

    status_code = 404


class ExternalApiError(AppError):
    """외부 API가 사용할 수 없는 응답을 반환한 경우에 사용한다."""

    status_code = 502


class ExternalApiUnavailableError(ExternalApiError):
    """외부 API의 일시적 오류가 재시도 후에도 계속된 경우에 사용한다."""

    status_code = 503
