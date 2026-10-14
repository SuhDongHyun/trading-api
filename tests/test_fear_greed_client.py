from datetime import datetime
from types import SimpleNamespace
import pytest

from stock.infra.cnn import fear_greed_client
from stock.infra.cnn.fear_greed_client import CnnFearGreedClient


@pytest.mark.parametrize(
    ("value", "condition"),
    [
        (0, "EXTREME FEAR"),
        (24, "EXTREME FEAR"),
        (25, "FEAR"),
        (44, "FEAR"),
        (45, "NEUTRAL"),
        (55, "NEUTRAL"),
        (56, "GREED"),
        (75, "GREED"),
        (76, "EXTREME GREED"),
        (100, "EXTREME GREED"),
    ],
)
def test_get_fear_and_greed_index_sets_condition_from_value(
    value, condition, monkeypatch
):
    updated_at = datetime(2026, 5, 31, 12, 0, 0)
    monkeypatch.setattr(
        fear_greed_client.fear_and_greed,
        "get",
        lambda: SimpleNamespace(value=value, last_update=updated_at),
    )
    result = CnnFearGreedClient().get_fear_and_greed_index()

    assert result.value == value
    assert result.condition == condition
    assert result.updated_at == updated_at
