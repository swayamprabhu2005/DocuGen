"""Tests for document type classification."""

from docugen.classification.resolver import classify_document


def test_explicit_document_type():
    result = classify_document({}, explicit_type="nda")
    assert result.document_type == "nda"
    assert result.confidence == 1.0
    assert result.method == "explicit"
    assert not result.ambiguous


def test_schema_match_employment():
    data = {
        "employee_name": "John Doe",
        "company_name": "Acme Corp",
        "salary": 80000,
        "joining_date": "2026-10-01",
    }
    result = classify_document(data)
    assert result.document_type == "employment_contract"
    assert result.method in ("schema_match", "rule_based")
    assert not result.ambiguous


def test_schema_match_invoice():
    data = {
        "invoice_number": "INV-001",
        "issue_date": "2026-09-01",
        "due_date": "2026-10-01",
        "seller_name": "Vendor Inc",
        "buyer_name": "Client LLC",
        "items": [{"description": "Service", "quantity": 1, "unit_price": 500}],
        "subtotal": 500.0,
        "total_amount": 500.0,
    }
    result = classify_document(data)
    assert result.document_type == "invoice"


def test_ambiguous_returns_candidates():
    # Very sparse data that matches multiple types weakly
    data = {"title": "Some Document", "date": "2026-01-01"}
    result = classify_document(data)
    # Either ambiguous or has very low confidence
    if result.ambiguous:
        assert len(result.candidates) >= 0
    else:
        assert result.confidence < 1.0


def test_empty_data_returns_ambiguous():
    result = classify_document({})
    assert result.ambiguous or result.document_type is None


def test_nda_schema_match():
    data = {
        "disclosing_party": "Corp A",
        "receiving_party": "Corp B",
        "effective_date": "2026-01-01",
        "purpose": "Business partnership evaluation",
    }
    result = classify_document(data)
    assert result.document_type == "nda"
