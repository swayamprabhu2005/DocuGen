"""NLP processing pipeline for DocuGen AI."""

from __future__ import annotations

from typing import Any, Dict, Optional
from docugen.input.normalizer import normalize_input
from docugen.nlp.extractor import EntityExtractor


class NLPPipeline:
    """Processes free-form unstructured text into normalized structured data."""

    def __init__(self, spacy_model: Optional[str] = None) -> None:
        self.extractor = EntityExtractor(spacy_model=spacy_model)

    def parse_text_to_data(self, text: str) -> Dict[str, Any]:
        """Extract fields and return normalized dictionary."""
        raw_fields = self.extractor.extract_fields(text)
        return normalize_input(raw_fields)
