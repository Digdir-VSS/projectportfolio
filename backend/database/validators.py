from datetime import datetime
from typing import Any, Union, Optional
import json

def to_datetime(value: Any) -> datetime | None:
    """Validator used by Pydantic: accept ISO datetimes and plain dates."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Try full ISO first: 2025-11-30T00:00:00
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
        # Fallback: pure date string: 2025-11-30
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None
    # Unknown type: just return as-is or None
    return None

def convert_to_int(number: Union[str, int, None]) -> Union[int, None]:
    if number:
        if isinstance(number, str):
            if number.isdigit():
                return int(number)
            else:
                return None
        if isinstance(number, int):
            return number
    else:
        return None

def convert_to_int_from_thousand_sign(text: Optional[str]) -> Optional[int]:
    if text is None:
        return None

    text = text.strip()
    if text == '':
        return None

    # Remove thousand separators (commas and spaces)
    clean = text.replace(',', '').replace(' ', '')

    try:
        return int(clean)
    except ValueError:
        return None

def add_thousand_split(number: Union[str, None]) -> Union[str, None]:
    if number is None:
        return None
    return f'{int(number):,}'

def to_list(value) ->list[str]:
    """Safely parse a JSON list or return [] if invalid."""
    if value is None:
        return []
    if isinstance(value, list):  # Already deserialized
        return value
    value = str(value).strip()
    if not value or value.lower() in ("null", "none"):
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []

def to_json(value: list[str] | None) -> str:
    """Convert UI list back to JSON string for the dataclass."""
    return json.dumps(value or [],  ensure_ascii=False)

def to_date_str(value: Union[datetime, None]) -> Union[str, None]:
    """Convert datetime/date to ISO date string (YYYY-MM-DD) for NiceGUI."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)

def turn_none_to_zero(year_input: int | None) -> int:
    if year_input is None:
        return 0
    else: 
        return year_input

def validate_budget_distribution(total: int, year_1: int | None, year_2: int | None, year_3: int | None) -> bool:
    converted_year_1 = turn_none_to_zero(convert_to_int(year_1))
    converted_year_2 = turn_none_to_zero(convert_to_int(year_2))
    converted_year_3 = turn_none_to_zero(convert_to_int(year_3))
    converted_total = turn_none_to_zero(convert_to_int(total))
    return converted_total != sum((converted_year_1, converted_year_2, converted_year_3))

def sort_selected_values(e):
    if isinstance(e.value, list):
        sorted_values = sorted(e.value)
        e.sender.value = sorted_values