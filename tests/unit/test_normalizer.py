"""Tests for input normalizer."""

from docugen.core.schemas import DocumentSchema, FieldDefinition, FieldType
from docugen.input.normalizer import (
    normalize_boolean,
    normalize_date,
    normalize_input,
    normalize_number,
    normalize_string,
)


def test_normalize_string():
    assert normalize_string("  hello   world  ") == "hello world"
    assert normalize_string("line 1   \n   line 2") == "line 1\nline 2"


def test_normalize_boolean():
    assert normalize_boolean("true") is True
    assert normalize_boolean("YES") is True
    assert normalize_boolean("1") is True
    assert normalize_boolean("false") is False
    assert normalize_boolean("no") is False
    assert normalize_boolean("0") is False
    assert normalize_boolean(True) is True


def test_normalize_number():
    assert normalize_number("50,000") == 50000
    assert normalize_number("$120,000.50") == 120000.50
    assert normalize_number("€ 2,500") == 2500
    assert normalize_number("₹ 99,999") == 99999
    assert normalize_number(42) == 42


def test_normalize_date():
    assert normalize_date("2026-10-01") == "2026-10-01"
    assert normalize_date("2026/10/01") == "2026-10-01"
    assert normalize_date("October 1, 2026") == "2026-10-01"
    assert normalize_date("01-10-2026") in ("2026-10-01", "2026-01-10")


def test_normalize_input_with_schema_aliases_and_defaults():
    schema = DocumentSchema(
        document_type="test_type",
        title="Test Type",
        fields={
            "employee_name": FieldDefinition(
                name="employee_name",
                type=FieldType.STRING,
                aliases=["employee", "worker"],
            ),
            "salary": FieldDefinition(
                name="salary",
                type=FieldType.NUMBER,
                aliases=["compensation"],
            ),
            "active": FieldDefinition(
                name="active",
                type=FieldType.BOOLEAN,
                default=True,
            ),
            "joining_date": FieldDefinition(
                name="joining_date",
                type=FieldType.DATE,
            ),
        },
    )

    raw_data = {
        "employee": "  Jane Doe  ",
        "compensation": "$75,000",
        "joining_date": "2026/11/15",
    }

    normalized = normalize_input(raw_data, schema=schema)

    assert normalized["employee_name"] == "Jane Doe"
    assert normalized["salary"] == 75000
    assert normalized["joining_date"] == "2026-11-15"
    assert normalized["active"] is True  # default populated
