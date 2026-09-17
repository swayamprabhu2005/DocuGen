"""Tests for schema validation and required fields."""

import pytest
from docugen.api.public import validate_document_data
from docugen.core.exceptions import ValidationError
from docugen.core.schemas import DocumentSchema, FieldDefinition, FieldType
from docugen.validation.validator import validate_data


def test_missing_required_fields():
    data = {"salary": 50000}
    res = validate_document_data(data, template="employment_contract", strict=False)

    assert not res.valid
    assert "employee_name" in res.missing_fields
    assert "company_name" in res.missing_fields
    assert "joining_date" in res.missing_fields

    # In strict mode, raises ValidationError
    with pytest.raises(ValidationError) as exc_info:
        validate_document_data(data, template="employment_contract", strict=True)
    assert "employee_name" in str(exc_info.value)


def test_field_rules_and_types():
    schema = DocumentSchema(
        document_type="test_rules",
        title="Test Rules",
        fields={
            "age": FieldDefinition(name="age", type=FieldType.INTEGER, minimum=18, maximum=65),
            "department": FieldDefinition(name="department", type=FieldType.STRING, enum_values=["Engineering", "Sales"]),
            "email": FieldDefinition(name="email", type=FieldType.STRING, regex_pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"),
        },
    )

    # 1. Invalid type
    res_bad_type = validate_data({"age": "not_an_int"}, schema, strict=False)
    assert not res_bad_type.valid
    assert any(e.code == "INVALID_TYPE" for e in res_bad_type.errors)

    # 2. Out of range
    res_out_of_range = validate_data({"age": 16}, schema, strict=False)
    assert not res_out_of_range.valid
    assert any(e.code == "MINIMUM_VIOLATION" for e in res_out_of_range.errors)

    # 3. Invalid enum
    res_bad_enum = validate_data({"department": "Marketing"}, schema, strict=False)
    assert not res_bad_enum.valid
    assert any(e.code == "INVALID_ENUM_VALUE" for e in res_bad_enum.errors)

    # 4. Pattern mismatch
    res_bad_email = validate_data({"email": "not-an-email"}, schema, strict=False)
    assert not res_bad_email.valid
    assert any(e.code == "PATTERN_MISMATCH" for e in res_bad_email.errors)

    # 5. Valid input
    res_valid = validate_data(
        {"age": 30, "department": "Engineering", "email": "dev@example.com"},
        schema,
        strict=False,
    )
    assert res_valid.valid
    assert len(res_valid.errors) == 0
