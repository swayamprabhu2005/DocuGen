"""Consistency engine for cross-field validation and diagnostics."""

from __future__ import annotations

from typing import Any, Callable, Dict, List
from docugen.core.models import ValidationResult
from docugen.core.schemas import DocumentSchema


ConsistencyCheckFn = Callable[[Dict[str, Any], DocumentSchema, ValidationResult], None]


def check_date_ordering(data: Dict[str, Any], result: ValidationResult) -> None:
    """Validate chronological ordering across known date field pairs."""
    date_pairs = [
        ("start_date", "end_date"),
        ("joining_date", "end_date"),
        ("effective_date", "expiration_date"),
        ("effective_date", "expiry_date"),
        ("issue_date", "due_date"),
        ("quote_date", "valid_until"),
    ]

    for start_field, end_field in date_pairs:
        start_val = data.get(start_field)
        end_val = data.get(end_field)
        if start_val and end_val and isinstance(start_val, str) and isinstance(end_val, str):
            if start_val > end_val:
                result.add_error(
                    code="DATE_ORDER_VIOLATION",
                    field=end_field,
                    message=f"Date '{end_field}' ({end_val}) cannot be earlier than '{start_field}' ({start_val}).",
                    context={"start_field": start_field, "end_field": end_field},
                )


def check_party_distinctness(data: Dict[str, Any], result: ValidationResult) -> None:
    """Ensure contracting parties are distinct entities."""
    party_pairs = [
        ("disclosing_party", "receiving_party"),
        ("party_a", "party_b"),
        ("client_name", "contractor_name"),
        ("client_name", "service_provider"),
        ("buyer_name", "seller_name"),
        ("company_name", "employee_name"),
    ]

    for p1, p2 in party_pairs:
        val1 = data.get(p1)
        val2 = data.get(p2)
        if val1 and val2 and isinstance(val1, str) and isinstance(val2, str):
            if val1.strip().lower() == val2.strip().lower():
                result.add_error(
                    code="IDENTICAL_PARTIES",
                    field=p2,
                    message=f"Conflicting party names: '{p1}' and '{p2}' are identical ('{val1}').",
                    context={"party_1": p1, "party_2": p2, "value": val1},
                )


def check_invoice_totals(data: Dict[str, Any], result: ValidationResult) -> None:
    """Verify invoice arithmetic consistency (items subtotal, tax, total)."""
    items = data.get("items")
    if not items or not isinstance(items, list):
        return

    computed_subtotal = 0.0
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        qty = item.get("quantity")
        price = item.get("unit_price")
        if isinstance(qty, (int, float)) and isinstance(price, (int, float)):
            line_total = round(qty * price, 2)
            if "total" in item and isinstance(item["total"], (int, float)):
                if abs(item["total"] - line_total) > 0.05:
                    result.add_warning(
                        code="LINE_ITEM_TOTAL_MISMATCH",
                        field=f"items[{idx}].total",
                        message=f"Line item {idx + 1} total ({item['total']}) does not match quantity * unit_price ({line_total}).",
                    )
            computed_subtotal += line_total

    # Subtotal check
    if "subtotal" in data and isinstance(data["subtotal"], (int, float)):
        if abs(data["subtotal"] - computed_subtotal) > 0.05:
            result.add_warning(
                code="SUBTOTAL_MISMATCH",
                field="subtotal",
                message=f"Invoice subtotal ({data['subtotal']}) differs from calculated item sum ({round(computed_subtotal, 2)}).",
            )


def check_schema_cross_field_rules(
    data: Dict[str, Any], schema: DocumentSchema, result: ValidationResult
) -> None:
    """Evaluate explicit declarative cross-field rules on the schema."""
    for rule in schema.cross_field_rules:
        val_a = data.get(rule.field_a)
        val_b = data.get(rule.field_b) if rule.field_b else None

        if val_a is None or (rule.field_b and val_b is None):
            continue

        if rule.rule_type == "date_order":
            if isinstance(val_a, str) and isinstance(val_b, str):
                if val_a > val_b:
                    result.add_error(
                        code="CROSS_FIELD_VIOLATION",
                        field=rule.field_b,
                        message=rule.error_message,
                        context={"rule_id": rule.rule_id},
                    )

        elif rule.rule_type == "numeric_comparison":
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                violation = False
                if rule.operator == "<=" and not (val_a <= val_b):
                    violation = True
                elif rule.operator == "<" and not (val_a < val_b):
                    violation = True
                elif rule.operator == "==" and not (abs(val_a - val_b) < 0.001):
                    violation = True
                if violation:
                    result.add_error(
                        code="CROSS_FIELD_VIOLATION",
                        field=rule.field_b or rule.field_a,
                        message=rule.error_message,
                        context={"rule_id": rule.rule_id},
                    )


_CUSTOM_CONSISTENCY_CHECKERS: List[ConsistencyCheckFn] = []


def register_consistency_checker(fn: ConsistencyCheckFn) -> None:
    """Register a custom global consistency check function."""
    if fn not in _CUSTOM_CONSISTENCY_CHECKERS:
        _CUSTOM_CONSISTENCY_CHECKERS.append(fn)


def check_consistency(
    data: Dict[str, Any], schema: DocumentSchema, result: ValidationResult
) -> None:
    """Run all consistency checks on data."""
    check_date_ordering(data, result)
    check_party_distinctness(data, result)
    check_invoice_totals(data, result)
    check_schema_cross_field_rules(data, schema, result)

    for custom_fn in _CUSTOM_CONSISTENCY_CHECKERS:
        custom_fn(data, schema, result)
