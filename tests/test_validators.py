import pytest
from utils.validators import validate_budget_distribution, turn_none_to_zero


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
