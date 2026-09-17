"""Validation and consistency package for DocuGen AI."""

from docugen.validation.consistency import (
    check_consistency,
    check_date_ordering,
    check_invoice_totals,
    check_party_distinctness,
    register_consistency_checker,
)
from docugen.validation.required_fields import check_required_fields
from docugen.validation.rules import check_field_rules
from docugen.validation.validator import (
    get_custom_validators,
    register_validator,
    validate_data,
)

__all__ = [
    "check_required_fields",
    "check_field_rules",
    "check_consistency",
    "check_date_ordering",
    "check_party_distinctness",
    "check_invoice_totals",
    "register_consistency_checker",
    "register_validator",
    "get_custom_validators",
    "validate_data",
]
