from datetime import datetime
from typing import Union
import json

def to_datetime(value: str):
    if isinstance(value, str):
        return datetime.strptime(value,"%Y-%m-%d")
    else:
        return value

def convert_to_int(number: Union[str, int, None]):
    if isinstance(number, str):
        return int(number)
    if isinstance(number, int):
        return number
    return None

def to_list(value):
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

def to_json(value: list[str] | None):
    """Convert UI list back to JSON string for the dataclass."""
    return json.dumps(value or [],  ensure_ascii=False)

def to_date_str(value):
    print(type(value))
    """Convert datetime/date to ISO date string (YYYY-MM-DD) for NiceGUI."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    return str(value)