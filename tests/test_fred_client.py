from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from stock.infra.fred.fred_client import FredClient


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
def test_get_fear_and_greed_index_sets_condition_from_value(value, condition):
    updated_at = datetime(2026, 5, 31, 12, 0, 0)
    client = FredClient.__new__(FredClient)

    with patch(
        "stock.infra.fred.fred_client.fear_and_greed.get",
        return_value=SimpleNamespace(value=value, last_update=updated_at),
    ):
        result = client.get_fear_and_greed_index()

    assert result.value == value
    assert result.condition == condition
    assert result.updated_at == updated_at
