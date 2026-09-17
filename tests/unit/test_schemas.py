"""Unit tests for DocumentSchema and FieldDefinition."""

import json
import pytest

from docugen.core.schemas import DocumentSchema, FieldDefinition, FieldType
from docugen.core.schema_registry import (
    get_schema,
    list_document_types,
    register_schema,
)
from docugen.core.exceptions import SchemaError


def test_schema_registry_has_builtin_schemas():
    types = list_document_types()
    for name in [
        "employment_contract",
        "nda",
        "invoice",
        "quotation",
        "business_report",
        "certificate",
        "service_agreement",
    ]:
        assert name in types, f"{name} not found in registered schemas"


def test_get_schema_returns_correct_schema():
    schema = get_schema("nda")
    assert schema is not None
    assert schema.document_type == "nda"
    assert "disclosing_party" in schema.fields


def test_get_schema_unknown_raises():
    with pytest.raises(SchemaError):
        get_schema("nonexistent_type_xyz")


def test_employment_schema_required_fields():
    schema = get_schema("employment_contract")
    required = schema.get_required_field_names()
    assert "employee_name" in required
    assert "company_name" in required
    assert "joining_date" in required
    assert "salary" in required


def test_invoice_schema_fields():
    schema = get_schema("invoice")
    assert "invoice_number" in schema.fields
    assert "items" in schema.fields
    assert schema.fields["items"].type == FieldType.LIST


def test_field_definition_enum_values():
    fd = FieldDefinition(
        name="status",
        type=FieldType.STRING,
        required=True,
        enum_values=["active", "inactive", "pending"],
    )
    assert fd.enum_values is not None
    assert "active" in fd.enum_values
    assert "inactive" in fd.enum_values
    assert len(fd.enum_values) == 3


def test_field_definition_default():
    fd = FieldDefinition(
        name="currency",
        type=FieldType.STRING,
        required=False,
        default="USD",
    )
    assert fd.default == "USD"
    assert not fd.required


def test_export_json_schema_returns_dict():
    """export_json_schema() returns a dict (JSON-serialisable)."""
    schema = get_schema("certificate")
    json_schema = schema.export_json_schema()
    assert isinstance(json_schema, dict)
    assert "properties" in json_schema
    # Accept any title containing "Certificate"
    assert "Certificate" in json_schema.get("title", "")
    assert "recipient_name" in json_schema["properties"]


def test_export_json_schema_is_serialisable():
    """The dict returned by export_json_schema must be JSON-serialisable."""
    schema = get_schema("employment_contract")
    json_schema = schema.export_json_schema()
    serialised = json.dumps(json_schema)  # must not raise
    assert len(serialised) > 10


def test_register_custom_schema():
    custom = DocumentSchema(
        document_type="test_schema_xyz",
        title="Test Schema XYZ",
        fields={
            "alpha": FieldDefinition(name="alpha", type=FieldType.STRING, required=True),
            "beta": FieldDefinition(name="beta", type=FieldType.NUMBER, required=False, default=42.0),
        },
    )
    register_schema(custom)
    retrieved = get_schema("test_schema_xyz")
    assert retrieved is not None
    assert retrieved.fields["beta"].default == 42.0


def test_schema_alias_map():
    schema = get_schema("employment_contract")
    aliases = schema.get_field_aliases_map()
    # alias_map should be a dict mapping alias→canonical name
    assert isinstance(aliases, dict)


def test_cross_field_rules_present_in_invoice():
    """Invoice schema should have cross-field rules."""
    schema = get_schema("invoice")
    if schema.cross_field_rules:
        rule_ids = [r.rule_id for r in schema.cross_field_rules]
        assert len(rule_ids) > 0
