"""Tests for cross-field consistency engine."""

from docugen.api.public import validate_document_data


def test_date_ordering_consistency():
    # End date before start date
    data = {
        "client_name": "Acme Corp",
        "service_provider": "Apex Devs",
        "service_description": "API Building",
        "start_date": "2026-10-01",
        "end_date": "2026-09-01",  # earlier than start date
        "fee_amount": 5000,
    }

    res = validate_document_data(data, template="service_agreement", strict=False)
    assert not res.valid
    assert any(e.code == "DATE_ORDER_VIOLATION" for e in res.errors)


def test_party_distinctness_consistency():
    # Identical parties in NDA
    data = {
        "disclosing_party": "Acme Global",
        "receiving_party": "Acme Global",  # identical
        "effective_date": "2026-10-01",
        "purpose": "Merger talks",
    }

    res = validate_document_data(data, template="nda", strict=False)
    assert not res.valid
    assert any(e.code == "IDENTICAL_PARTIES" for e in res.errors)


def test_invoice_arithmetic_consistency():
    data = {
        "invoice_number": "INV-101",
        "issue_date": "2026-10-01",
        "due_date": "2026-10-31",
        "seller_name": "Seller Inc",
        "buyer_name": "Buyer LLC",
        "items": [
            {"description": "Item 1", "quantity": 2, "unit_price": 100, "total": 300},  # 2*100 != 300
        ],
        "subtotal": 500,  # items sum is 200, subtotal 500
        "total_amount": 500,
    }

    res = validate_document_data(data, template="invoice", strict=False)
    # Should flag warnings for arithmetic mismatch
    assert any(w.code == "LINE_ITEM_TOTAL_MISMATCH" for w in res.warnings)
    assert any(w.code == "SUBTOTAL_MISMATCH" for w in res.warnings)
