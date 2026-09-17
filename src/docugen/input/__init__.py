"""Input adapters and normalization package."""

from docugen.input.adapters import adapt_input
from docugen.input.normalizer import (
    normalize_boolean,
    normalize_date,
    normalize_input,
    normalize_number,
    normalize_string,
)

__all__ = [
    "adapt_input",
    "normalize_input",
    "normalize_string",
    "normalize_number",
    "normalize_date",
    "normalize_boolean",
]
