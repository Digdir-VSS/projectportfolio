import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import OperationalError
from utils.db_connection import DBConnector


@pytest.fixture
def db_connector():
    return DBConnector(engine=MagicMock())


def make_operational_error(message: str):
    return OperationalError("SELECT *", {}, Exception(message))


def make_context_session(mock_session):
    """Make a mock act like a context manager."""
    ctx = MagicMock()
    ctx.__enter__.return_value = mock_session
    ctx.__exit__.return_value = None
    return ctx


def test_retry_on_operational_error(monkeypatch, db_connector):
    mock_session = MagicMock()

    # Create mock Result object with .all()
    mock_result = MagicMock()
    mock_result.all.return_value = [("123", "Project A", "Dept", "Owner", "email@test.com")]

    mock_session.exec.side_effect = [
        make_operational_error("08S01 TCP Provider: Error code 0x20"),
        make_operational_error("08S01 TCP Provider: Error code 0x20"),
        mock_result,  # ✅ emulate Result object
    ]
    # context-managed session
    mock_ctx = make_context_session(mock_session)
    monkeypatch.setattr("utils.db_connection.Session", MagicMock(return_value=mock_ctx))

    result = db_connector.get_projects()

    assert len(result) == 1
    assert mock_session.exec.call_count == 3


def test_stops_after_max_retries(monkeypatch, db_connector):
    mock_session = MagicMock()
    mock_session.exec.side_effect = [
        make_operational_error("08S01 TCP Provider"),
        make_operational_error("08S01 TCP Provider"),
        make_operational_error("08S01 TCP Provider"),
    ]
    mock_ctx = make_context_session(mock_session)
    monkeypatch.setattr("utils.db_connection.Session", MagicMock(return_value=mock_ctx))

    with pytest.raises(OperationalError):
        db_connector.get_projects()

    assert mock_session.exec.call_count == 3


def test_no_retry_on_non_operational_error(monkeypatch, db_connector):
    mock_session = MagicMock()
    mock_session.exec.side_effect = ValueError("Some other error")
    mock_ctx = make_context_session(mock_session)
    monkeypatch.setattr("utils.db_connection.Session", MagicMock(return_value=mock_ctx))

    with pytest.raises(ValueError):
        db_connector.get_projects()

    assert mock_session.exec.call_count == 1
