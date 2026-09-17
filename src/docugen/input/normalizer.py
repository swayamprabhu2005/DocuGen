"""Input data normalizer for DocuGen AI.

Provides deterministic, non-destructive normalization of input fields
(dates, numbers, currency, booleans, whitespace, and schema aliases)
prior to schema validation.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from docugen.core.schemas import DocumentSchema, FieldType


_CURRENCY_SYMBOLS = ["$", "€", "£", "¥", "₹", "CHF", "USD", "EUR", "GBP", "INR"]
_DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
]


def normalize_string(value: str) -> str:
    """Strip leading/trailing whitespace and collapse extraneous internal spaces."""
    if not isinstance(value, str):
        return value
    # Strip whitespace
    stripped = value.strip()
    # Normalize multiple tabs or spaces to single space, but preserve newlines
    lines = stripped.splitlines()
    normalized_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in lines]
    return "\n".join(normalized_lines)


def normalize_boolean(value: Any) -> Union[bool, Any]:
    """Coerce boolean strings ('true', 'yes', '1', etc.) to actual booleans."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "yes", "1", "y", "t"):
            return True
        if lowered in ("false", "no", "0", "n", "f"):
            return False
    elif isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    return value


def normalize_number(value: Any) -> Union[int, float, Any]:
    """Normalize numeric strings, stripping currency symbols and commas."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        clean = value.strip()
        for symbol in _CURRENCY_SYMBOLS:
            clean = clean.replace(symbol, "")
        clean = clean.replace(",", "").strip()
        # Try integer first
        try:
            if "." not in clean:
                return int(clean)
            return float(clean)
        except ValueError:
            return value
    return value


def normalize_date(value: Any) -> Union[str, Any]:
    """Attempt to parse date strings into ISO format YYYY-MM-DD."""
    if isinstance(value, str):
        clean = value.strip()
        for fmt in _DATE_FORMATS:
            try:
                parsed = datetime.strptime(clean, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
    elif hasattr(value, "strftime"):
        # datetime or date object
        return value.strftime("%Y-%m-%d")
    return value


def normalize_input(
    data: Dict[str, Any], schema: Optional[DocumentSchema] = None
) -> Dict[str, Any]:
    """Normalize raw input dictionary according to standard rules and schema hints.

    Args:
        data: Dictionary of input data.
        schema: Optional DocumentSchema for alias mapping and type-guided normalization.

    Returns:
        Dict[str, Any]: Cleaned and normalized dictionary.
    """
    normalized: Dict[str, Any] = {}

    alias_map: Dict[str, str] = {}
    if schema:
        alias_map = schema.get_field_aliases_map()

    for raw_key, value in data.items():
        # Clean key
        clean_key = raw_key.strip()
        canonical_key = alias_map.get(clean_key.lower(), clean_key)

        # Look up field definition from schema if available
        field_def = schema.fields.get(canonical_key) if schema else None

        # Recursively process nested dictionaries
        if isinstance(value, dict):
            normalized[canonical_key] = normalize_input(value)
            continue

        # Recursively process lists
        if isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(normalize_input(item))
                elif isinstance(item, str):
                    new_list.append(normalize_string(item))
                else:
                    new_list.append(item)
            normalized[canonical_key] = new_list
            continue

        # If schema specifies a particular type, apply targeted normalization
        if field_def:
            if field_def.type == FieldType.STRING and isinstance(value, str):
                normalized[canonical_key] = normalize_string(value)
            elif field_def.type in (FieldType.NUMBER, FieldType.INTEGER):
                normalized[canonical_key] = normalize_number(value)
            elif field_def.type == FieldType.DATE:
                normalized[canonical_key] = normalize_date(value)
            elif field_def.type == FieldType.BOOLEAN:
                normalized[canonical_key] = normalize_boolean(value)
            else:
                normalized[canonical_key] = value
        else:
            # General normalization heuristic
            if isinstance(value, str):
                cleaned_str = normalize_string(value)
                # Try date detection if key looks like a date
                if any(substr in canonical_key.lower() for substr in ["date", "dob", "deadline", "expiry"]):
                    cleaned_str = normalize_date(cleaned_str)
                normalized[canonical_key] = cleaned_str
            else:
                normalized[canonical_key] = value

    # Apply schema field default values if field not supplied
    if schema:
        for fname, fdef in schema.fields.items():
            if fname not in normalized and fdef.default is not None:
                normalized[fname] = fdef.default

    return normalized
