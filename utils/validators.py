import datetime

def to_datetime(value):
    if isinstance(value, str):
        return datetime.strptime(value,"%Y-%m-%d")
    else:
        return value