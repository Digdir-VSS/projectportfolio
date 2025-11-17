import datetime
from typing import Union

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
    