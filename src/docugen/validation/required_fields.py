"""Required fields checker for DocuGen AI."""

from __future__ import annotations

from typing import Any, Dict, List
from docugen.core.models import ValidationResult
from docugen.core.schemas import DocumentSchema


def check_required_fields(data: Dict[str, Any], schema: DocumentSchema, result: ValidationResult) -> None:
    """Verify that all required fields defined in the schema are present and non-empty.

    Args:
        data: Normalized input dictionary.
        schema: DocumentSchema definition.
        result: ValidationResult object to accumulate diagnostics into.
    """
    for field_name in schema.get_required_field_names():
        field_def = schema.fields.get(field_name)
        if field_name not in data or data[field_name] is None:
            desc = f" ({field_def.description})" if field_def and field_def.description else ""
            result.add_missing_field(
                field_name=field_name,
                message=f"Missing required field '{field_name}'{desc}.",
            )
            continue

        value = data[field_name]
        # Empty string check for required strings
        if isinstance(value, str) and not value.strip():
            result.add_missing_field(
                field_name=field_name,
                message=f"Required field '{field_name}' cannot be an empty or whitespace string.",
            )
        # Empty list check for required lists
        elif isinstance(value, list) and len(value) == 0:
            result.add_missing_field(
                field_name=field_name,
                message=f"Required list field '{field_name}' must contain at least one item.",
            )
