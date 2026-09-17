"""Information extraction from unstructured or semi-structured text."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class EntityExtractor:
    """Extracts candidate document fields (names, dates, amounts, numbers) from raw text."""

    def __init__(self, spacy_model: Optional[str] = None) -> None:
        self._nlp = None
        if SPACY_AVAILABLE and spacy_model:
            try:
                self._nlp = spacy.load(spacy_model)
            except Exception:
                pass

    def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract structured fields using rule patterns and optional local NER."""
        extracted: Dict[str, Any] = {}

        # 1. Regex key-value extraction (e.g. "Employee Name: John Doe", "Salary: 50000")
        kv_patterns = [
            r"(?i)(?:employee(?:_|\s+)name|employee)\s*[:=]\s*([^\n,]+)",
            r"(?i)(?:company(?:_|\s+)name|company|employer)\s*[:=]\s*([^\n,]+)",
            r"(?i)(?:salary|compensation)\s*[:=]\s*([$€£₹]?\s*[\d,]+(?:\.\d{2})?)",
            r"(?i)(?:joining(?:_|\s+)date|start(?:_|\s+)date)\s*[:=]\s*([^\n,]+)",
            r"(?i)(?:job(?:_|\s+)title|role|position)\s*[:=]\s*([^\n,]+)",
            r"(?i)(?:invoice(?:_|\s+)number|inv\s*#)\s*[:=]\s*([^\n,]+)",
            r"(?i)(?:total(?:_|\s+)amount|total)\s*[:=]\s*([$€£₹]?\s*[\d,]+(?:\.\d{2})?)",
            r"(?i)(?:disclosing(?:_|\s+)party)\s*[:=]\s*([^\n,]+)",
            r"(?i)(?:receiving(?:_|\s+)party)\s*[:=]\s*([^\n,]+)",
            r"(?i)(?:purpose)\s*[:=]\s*([^\n,]+)",
        ]

        field_names = [
            "employee_name",
            "company_name",
            "salary",
            "joining_date",
            "job_title",
            "invoice_number",
            "total_amount",
            "disclosing_party",
            "receiving_party",
            "purpose",
        ]

        for pat, fname in zip(kv_patterns, field_names):
            match = re.search(pat, text)
            if match:
                val = match.group(1).strip()
                extracted[fname] = val

        # 2. Optional spaCy NER enrichment
        if self._nlp:
            doc = self._nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON" and "employee_name" not in extracted:
                    extracted["employee_name"] = ent.text
                elif ent.label_ == "ORG" and "company_name" not in extracted:
                    extracted["company_name"] = ent.text
                elif ent.label_ == "DATE" and "joining_date" not in extracted:
                    extracted["joining_date"] = ent.text
                elif ent.label_ == "MONEY" and "salary" not in extracted:
                    extracted["salary"] = ent.text

        return extracted
