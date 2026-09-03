"""Reproduction + regression tests for validate_hr_tickets."""

import pytest

from fake_spark import FakeDataFrame
import validate_hr_tickets as vt

VALID_COLUMNS = [
    "ticket_id",
    "employee_id",
    "category",
    "priority",
    "status",
    "created_timestamp",
    "resolved_timestamp",
]


def _valid_row(**overrides):
    row = {
        "ticket_id": "TCK-1",
        "employee_id": "E1",
        "category": "payroll",
        "priority": "high",
        "status": "open",
        "created_timestamp": "2025-01-01T10:00:00",
        "resolved_timestamp": None,
    }
    row.update(overrides)
    return row


def test_valid_batch_passes():
    df = FakeDataFrame(
        [_valid_row(ticket_id="TCK-1"), _valid_row(ticket_id="TCK-2")],
        VALID_COLUMNS,
    )
    result = vt.validate_hr_tickets(df)
    assert result["is_valid"] is True
    assert result["issues"] == []


def test_missing_ticket_id_column_is_reported_not_crashed():
    """Bug report: validation crashes when the ticket_id column is missing."""
    columns_without_key = [c for c in VALID_COLUMNS if c != "ticket_id"]
    rows = [
        {k: v for k, v in _valid_row().items() if k != "ticket_id"},
        {k: v for k, v in _valid_row().items() if k != "ticket_id"},
    ]
    df = FakeDataFrame(rows, columns_without_key)

    result = vt.validate_hr_tickets(df, raise_on_error=False)

    assert result["is_valid"] is False
    assert any("ticket_id" in issue for issue in result["issues"])
    assert "missing_columns" in result
    assert result["missing_columns"] == ["ticket_id"]


def test_null_ticket_id_values_not_reported_as_duplicates():
    """Null keys must be flagged as nulls, never miscounted as duplicate keys."""
    df = FakeDataFrame(
        [
            _valid_row(ticket_id="TCK-1"),
            _valid_row(ticket_id=None),
            _valid_row(ticket_id=None),
        ],
        VALID_COLUMNS,
    )

    result = vt.validate_hr_tickets(df, raise_on_error=False)

    assert result["is_valid"] is False
    assert any("null or empty" in issue for issue in result["issues"])
    assert not any("duplicate" in issue for issue in result["issues"])


def test_real_duplicate_ticket_id_still_flagged():
    df = FakeDataFrame(
        [_valid_row(ticket_id="TCK-1"), _valid_row(ticket_id="TCK-1")],
        VALID_COLUMNS,
    )
    result = vt.validate_hr_tickets(df, raise_on_error=False)
    assert any("duplicate" in issue for issue in result["issues"])


def test_raise_on_error_default_raises_valueerror():
    columns_without_key = [c for c in VALID_COLUMNS if c != "ticket_id"]
    rows = [{k: v for k, v in _valid_row().items() if k != "ticket_id"}]
    df = FakeDataFrame(rows, columns_without_key)
    with pytest.raises(ValueError):
        vt.validate_hr_tickets(df)
