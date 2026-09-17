"""Central validator orchestrator for DocuGen AI."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from docugen.core.exceptions import ValidationError
from docugen.core.models import ValidationResult
from docugen.core.schemas import DocumentSchema
from docugen.validation.consistency import check_consistency
from docugen.validation.required_fields import check_required_fields
from docugen.validation.rules import check_field_rules

CustomValidatorFn = Callable[[Dict[str, Any], DocumentSchema], ValidationResult]
_CUSTOM_DOC_VALIDATORS: Dict[str, List[CustomValidatorFn]] = {}


def register_validator(document_type: str, validator: CustomValidatorFn) -> None:
    """Register a custom validator function for a specific document type."""
    normalized_type = document_type.strip().lower()
    if normalized_type not in _CUSTOM_DOC_VALIDATORS:
        _CUSTOM_DOC_VALIDATORS[normalized_type] = []
    _CUSTOM_DOC_VALIDATORS[normalized_type].append(validator)


def get_custom_validators(document_type: str) -> List[CustomValidatorFn]:
    """Retrieve registered custom validators for a document type."""
    return _CUSTOM_DOC_VALIDATORS.get(document_type.strip().lower(), [])


def validate_data(
    data: Dict[str, Any],
    schema: DocumentSchema,
    strict: bool = True,
) -> ValidationResult:
    """Validate normalized data against a document schema.

    Args:
        data: Normalized dictionary of document field values.
        schema: DocumentSchema instance.
        strict: If True and validation errors exist, raises ValidationError.

    Returns:
        ValidationResult: Structured diagnostics object.

    Raises:
        ValidationError: In strict mode when blocking validation errors are present.
    """
    result = ValidationResult(valid=True)

    # 1. Check required fields
    check_required_fields(data, schema, result)

    # 2. Check individual field rules (types, ranges, enums, regex)
    check_field_rules(data, schema, result)

    # 3. Check consistency across fields
    check_consistency(data, schema, result)

    # 4. Run any custom validators registered for this document type
    for custom_val in get_custom_validators(schema.document_type):
        custom_res = custom_val(data, schema)
        if not custom_res.valid:
            result.valid = False
        result.errors.extend(custom_res.errors)
        result.warnings.extend(custom_res.warnings)
        result.missing_fields.extend([f for f in custom_res.missing_fields if f not in result.missing_fields])

    # In strict mode, if invalid, raise ValidationError
    if strict and not result.valid:
        error_msgs = [f"[{e.code}] {e.message}" for e in result.errors]
        summary = f"Validation failed for document type '{schema.document_type}':\n" + "\n".join(
            f"  - {msg}" for msg in error_msgs
        )
        raise ValidationError(
            message=summary,
            diagnostics=result.errors,
            details={"document_type": schema.document_type, "missing_fields": result.missing_fields},
        )

    return result
