"""여러 기술적 지표 계산에서 공유하는 보조 함수."""


def simple_moving_average(values: list[float], period: int) -> float:
    """입력 목록의 마지막 period개 값으로 단순 이동평균을 계산한다."""

    return sum(values[-period:]) / period
