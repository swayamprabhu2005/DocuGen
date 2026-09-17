"""Rule-based validation checks (types, ranges, enums, regex patterns)."""

from __future__ import annotations

import re
from typing import Any, Dict
from docugen.core.models import ValidationResult
from docugen.core.schemas import DocumentSchema, FieldDefinition, FieldType


def check_field_rules(data: Dict[str, Any], schema: DocumentSchema, result: ValidationResult) -> None:
    """Validate each present field against its defined schema rules."""
    for field_name, field_def in schema.fields.items():
        if field_name not in data or data[field_name] is None:
            continue

        value = data[field_name]
        _validate_single_field(field_name, field_def, value, result)


def _validate_single_field(field_name: str, field_def: FieldDefinition, value: Any, result: ValidationResult) -> None:
    """Validate a single field against its definition."""
    # 1. Type validation
    if field_def.type == FieldType.STRING:
        if not isinstance(value, str):
            result.add_error(
                code="INVALID_TYPE",
                field=field_name,
                message=f"Field '{field_name}' must be a string, got {type(value).__name__}.",
            )
            return
        if field_def.regex_pattern:
            if not re.match(field_def.regex_pattern, value):
                result.add_error(
                    code="PATTERN_MISMATCH",
                    field=field_name,
                    message=f"Field '{field_name}' value '{value}' does not match required pattern '{field_def.regex_pattern}'.",
                )

    elif field_def.type == FieldType.NUMBER:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            result.add_error(
                code="INVALID_TYPE",
                field=field_name,
                message=f"Field '{field_name}' must be a number, got {type(value).__name__}.",
            )
            return
        if field_def.minimum is not None and value < field_def.minimum:
            result.add_error(
                code="MINIMUM_VIOLATION",
                field=field_name,
                message=f"Field '{field_name}' value {value} is less than minimum {field_def.minimum}.",
            )
        if field_def.maximum is not None and value > field_def.maximum:
            result.add_error(
                code="MAXIMUM_VIOLATION",
                field=field_name,
                message=f"Field '{field_name}' value {value} exceeds maximum {field_def.maximum}.",
            )

    elif field_def.type == FieldType.INTEGER:
        if not isinstance(value, int) or isinstance(value, bool):
            result.add_error(
                code="INVALID_TYPE",
                field=field_name,
                message=f"Field '{field_name}' must be an integer, got {type(value).__name__}.",
            )
            return
        if field_def.minimum is not None and value < field_def.minimum:
            result.add_error(
                code="MINIMUM_VIOLATION",
                field=field_name,
                message=f"Field '{field_name}' value {value} is less than minimum {field_def.minimum}.",
            )
        if field_def.maximum is not None and value > field_def.maximum:
            result.add_error(
                code="MAXIMUM_VIOLATION",
                field=field_name,
                message=f"Field '{field_name}' value {value} exceeds maximum {field_def.maximum}.",
            )

    elif field_def.type == FieldType.BOOLEAN:
        if not isinstance(value, bool):
            result.add_error(
                code="INVALID_TYPE",
                field=field_name,
                message=f"Field '{field_name}' must be a boolean, got {type(value).__name__}.",
            )
            return

    elif field_def.type == FieldType.DATE:
        if not isinstance(value, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            result.add_error(
                code="INVALID_DATE_FORMAT",
                field=field_name,
                message=f"Field '{field_name}' must be an ISO date (YYYY-MM-DD), got '{value}'.",
            )
            return

    elif field_def.type == FieldType.LIST:
        if not isinstance(value, list):
            result.add_error(
                code="INVALID_TYPE",
                field=field_name,
                message=f"Field '{field_name}' must be a list, got {type(value).__name__}.",
            )
            return

    elif field_def.type == FieldType.OBJECT:
        if not isinstance(value, dict):
            result.add_error(
                code="INVALID_TYPE",
                field=field_name,
                message=f"Field '{field_name}' must be an object (dict), got {type(value).__name__}.",
            )
            return

    # 2. Enum validation
    if field_def.enum_values is not None:
        if value not in field_def.enum_values:
            allowed = ", ".join(repr(v) for v in field_def.enum_values)
            result.add_error(
                code="INVALID_ENUM_VALUE",
                field=field_name,
                message=f"Field '{field_name}' has invalid value {value!r}. Allowed: [{allowed}].",
            )
