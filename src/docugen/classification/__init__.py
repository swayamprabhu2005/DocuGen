"""Classification package for DocuGen AI."""

from docugen.classification.ml import MLDocumentClassifier
from docugen.classification.resolver import classify_document
from docugen.classification.rules import rule_based_classify

__all__ = [
    "classify_document",
    "rule_based_classify",
    "MLDocumentClassifier",
]
