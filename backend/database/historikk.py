"""Finding how a project looked at a date, from the versioned (SCD2) tables.

Every save adds a new row with its own sist_endret, so the version that applied at a
point in time is the newest row saved before it. A project is deleted when it has no
current row left, and its newest row then carries the time of deletion.
"""
from datetime import date, datetime, time, timedelta, timezone
from typing import Callable, Hashable, Iterable
from zoneinfo import ZoneInfo

OSLO = ZoneInfo("Europe/Oslo")


def end_of_day_utc(dato: date) -> datetime:
    """The moment a Norwegian date ends, as the naive UTC that sist_endret is stored in."""
    start_of_next_day = datetime.combine(dato + timedelta(days=1), time.min, tzinfo=OSLO)
    return start_of_next_day.astimezone(timezone.utc).replace(tzinfo=None)


def project_key(row) -> str:
    return str(row.prosjekt_id).lower()


def latest_versions(rows: Iterable, key: Callable[[object], Hashable] = project_key) -> dict:
    """The newest row per key."""
    latest = {}
    for row in rows:
        current = latest.get(key(row))
        if current is None or row.sist_endret >= current.sist_endret:
            latest[key(row)] = row
    return latest


def deleted_projects(versions: Iterable) -> dict[str, datetime]:
    """When each deleted project was deleted, from all its PortfolioProject versions."""
    versions = [version for version in versions if version.sist_endret is not None]
    active = {project_key(version) for version in versions if version.er_gjeldende}
    return {
        project: version.sist_endret
        for project, version in latest_versions(versions).items()
        if project not in active
    }
