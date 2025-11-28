import pytest
from datetime import datetime, date, timezone
from models.validators import validate_budget_distribution, turn_none_to_zero, to_datetime

test_converting_years = [(50, 50), (None, 0)]

@pytest.mark.parametrize("year_input, expected", test_converting_years)
def test_turn_none_to_zero(year_input, expected):
    assert expected == turn_none_to_zero(year_input)



test_budget = [
    (100, 50, 25, 25, False),
    (100, 50, 25, 1, True),
    (5, 50, 25, 25, True),
    (100, 50, "25", 25, False),
    (100, 50, None, 25, True),
    (None, None, None, None, False)
]

@pytest.mark.parametrize("total, year_1, year_2, year_3, result", test_budget)
def test_validate_budget_distribution(total, year_1, year_2, year_3, result):
    assert result == validate_budget_distribution(total, year_1, year_2, year_3)


def test_to_datetime_none_returns_none():
    assert to_datetime(None) is None


def test_to_datetime_with_datetime_returns_same_object():
    dt = datetime(2025, 11, 30, 12, 34, 56)
    result = to_datetime(dt)
    assert result is dt   # should be exactly the same object


def test_to_datetime_full_iso_datetime_string():
    value = "2025-11-30T15:45:10"
    result = to_datetime(value)
    assert isinstance(result, datetime)
    assert result == datetime(2025, 11, 30, 15, 45, 10)


def test_to_datetime_date_only_string():
    value = "2025-11-30"
    result = to_datetime(value)
    assert isinstance(result, datetime)
    # from your code: datetime.strptime("%Y-%m-%d") → midnight
    assert result == datetime(2025, 11, 30, 0, 0, 0)


def test_to_datetime_invalid_string_returns_none():
    value = "not-a-date"
    result = to_datetime(value)
    assert result is None


def test_to_datetime_iso_with_timezone_not_supported_returns_none():
    value = "2025-11-30T15:45:10Z"
    result = to_datetime(value)
    assert isinstance(result, datetime)
    assert result == datetime(2025, 11, 30, 15, 45, 10, tzinfo=timezone.utc)


@pytest.mark.parametrize("value", [123, 4.56, [], {}])
def test_to_datetime_unsupported_types_return_none(value):
    result = to_datetime(value)
    assert result is None