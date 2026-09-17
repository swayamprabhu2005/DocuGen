"""Pytest fixtures for DocuGen AI test suite."""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def sample_employment_data():
    return {
        "employee_name": "John Doe",
        "company_name": "Acme Innovations Ltd",
        "job_title": "Lead Systems Architect",
        "salary": 120000,
        "salary_period": "year",
        "joining_date": "2026-10-01",
        "work_location": "San Francisco, CA",
        "probation_period_months": 3,
        "notice_period_days": 30,
        "remote_work_allowed": True,
        "non_compete": True,
    }


@pytest.fixture
def sample_nda_data():
    return {
        "disclosing_party": "Alpha Corp",
        "receiving_party": "Beta LLC",
        "effective_date": "2026-09-01",
        "duration_years": 3,
        "purpose": "Evaluating potential joint venture opportunities in document intelligence",
        "jurisdiction": "State of New York",
        "mutual": True,
        "remedies_injunctive_relief": True,
    }


@pytest.fixture
def sample_invoice_data():
    return {
        "invoice_number": "INV-2026-0042",
        "issue_date": "2026-09-15",
        "due_date": "2026-10-15",
        "seller_name": "Apex Engineering Group",
        "seller_address": "100 Tech Blvd, Suite 400, Austin, TX",
        "buyer_name": "Global Retail Solutions",
        "buyer_address": "500 Market St, Floor 12, Seattle, WA",
        "items": [
            {
                "description": "Cloud Architecture Assessment",
                "quantity": 40,
                "unit_price": 150.0,
                "total": 6000.0,
            },
            {
                "description": "Custom API Pipeline Implementation",
                "quantity": 80,
                "unit_price": 175.0,
                "total": 14000.0,
            },
        ],
        "subtotal": 20000.0,
        "tax_rate": 0.08,
        "tax_amount": 1600.0,
        "total_amount": 21600.0,
        "currency": "USD",
        "payment_instructions": "Wire Transfer: Bank of Tech, Routing #123456789, Account #987654321",
    }


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
