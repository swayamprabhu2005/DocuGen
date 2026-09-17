"""Rule-based heuristic classifier for DocuGen AI."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

# Distinctive signature fields for each built-in document type
_TYPE_SIGNATURES: Dict[str, List[str]] = {
    "employment_contract": ["employee_name", "company_name", "salary", "joining_date", "job_title"],
    "nda": ["disclosing_party", "receiving_party", "purpose", "effective_date"],
    "service_agreement": ["client_name", "service_provider", "service_description", "fee_amount"],
    "invoice": ["invoice_number", "seller_name", "buyer_name", "items", "subtotal", "total_amount"],
    "quotation": ["quote_number", "seller_name", "client_name", "valid_until", "total_amount"],
    "business_report": ["report_title", "prepared_by", "organization", "executive_summary"],
    "certificate": ["recipient_name", "course_or_achievement", "issuer_name", "certificate_title"],
}


def rule_based_classify(data: Dict[str, Any]) -> List[Tuple[str, float]]:
    """Score candidate document types based on presence of key signature fields.

    Returns:
        List[Tuple[str, float]]: Sorted list of (document_type, confidence_score) pairs.
    """
    keys = {k.strip().lower() for k in data.keys()}
    scores: List[Tuple[str, float]] = []

    for doc_type, signature in _TYPE_SIGNATURES.items():
        matched = sum(1 for field in signature if field in keys)
        score = matched / len(signature)
        if score > 0.3:
            scores.append((doc_type, round(score, 3)))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
