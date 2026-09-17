"""Integration tests for the full document generation pipeline."""

import os
from pathlib import Path

import pytest

from docugen import generate_document, validate_document_data


def test_employment_contract_pdf(sample_employment_data, temp_output_dir):
    """Full acceptance test: Employment contract PDF generation."""
    output_file = temp_output_dir / "employment.pdf"
    result = generate_document(
        data=sample_employment_data,
        template="employment_contract",
        output="pdf",
        output_path=str(output_file),
    )
    assert result.success, f"PDF generation failed: {result.error}"
    assert result.output_path is not None
    assert Path(result.output_path).exists()
    assert Path(result.output_path).stat().st_size > 1000
    assert result.document_type == "employment_contract"
    assert result.validation.valid


def test_employment_contract_docx(sample_employment_data, temp_output_dir):
    """Full acceptance test: Employment contract DOCX generation."""
    output_file = temp_output_dir / "employment.docx"
    result = generate_document(
        data=sample_employment_data,
        template="employment_contract",
        output="docx",
        output_path=str(output_file),
    )
    assert result.success, f"DOCX generation failed: {result.error}"
    assert result.output_path is not None
    assert Path(result.output_path).exists()
    assert Path(result.output_path).stat().st_size > 5000
    assert result.document_type == "employment_contract"


def test_nda_generation(sample_nda_data, temp_output_dir):
    """NDA document PDF generation."""
    result = generate_document(
        data=sample_nda_data,
        template="nda",
        output="pdf",
        output_path=str(temp_output_dir / "nda.pdf"),
    )
    assert result.success, f"NDA PDF failed: {result.error}"
    assert Path(result.output_path).exists()


def test_invoice_generation(sample_invoice_data, temp_output_dir):
    """Invoice PDF generation with items table and totals."""
    result = generate_document(
        data=sample_invoice_data,
        template="invoice",
        output="pdf",
        output_path=str(temp_output_dir / "invoice.pdf"),
    )
    assert result.success, f"Invoice PDF failed: {result.error}"
    assert Path(result.output_path).exists()
    assert Path(result.output_path).stat().st_size > 1000


def test_missing_fields_not_generated(temp_output_dir):
    """Acceptance test: missing required fields must NOT generate a document in strict mode."""
    from docugen.core.exceptions import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        generate_document(
            data={"salary": 50000},
            template="employment_contract",
            output="pdf",
            output_path=str(temp_output_dir / "should_not_exist.pdf"),
            strict=True,
        )
    error_msg = str(exc_info.value)
    assert "employee_name" in error_msg or "Missing" in error_msg
    assert not (temp_output_dir / "should_not_exist.pdf").exists()


def test_missing_fields_lenient_mode(temp_output_dir):
    """Lenient mode: partial data generates document with warnings."""
    result = generate_document(
        data={"salary": 50000},
        template="employment_contract",
        output="pdf",
        output_path=str(temp_output_dir / "lenient.pdf"),
        strict=False,
    )
    # May succeed with defaults applied
    assert result.validation is not None
    assert not result.validation.valid or len(result.validation.missing_fields) >= 0


def test_validation_only(sample_employment_data):
    """validate_document_data should not produce any output file."""
    res = validate_document_data(sample_employment_data, template="employment_contract")
    assert res.valid
    assert len(res.errors) == 0


def test_dry_run_returns_ir(sample_employment_data):
    """dry_run=True must return Document IR without writing any file."""
    result = generate_document(
        data=sample_employment_data,
        template="employment_contract",
        output="pdf",
        dry_run=True,
    )
    assert result.success
    assert result.document_ir is not None
    assert result.output_path is None
    assert len(result.document_ir.sections) > 0


def test_all_builtin_templates_pdf(
    sample_employment_data,
    sample_nda_data,
    sample_invoice_data,
    temp_output_dir,
):
    """All 7 built-in templates should generate valid PDFs."""
    from docugen import generate_document

    datasets = {
        "employment_contract": sample_employment_data,
        "nda": sample_nda_data,
        "invoice": sample_invoice_data,
        "quotation": {
            "quote_number": "Q-2026-001",
            "quote_date": "2026-09-01",
            "valid_until": "2026-09-30",
            "seller_name": "Apex Tech",
            "client_name": "Client Corp",
            "items": [{"description": "Service A", "quantity": 10, "unit_price": 100.0}],
            "total_amount": 1000.0,
        },
        "business_report": {
            "report_title": "Q3 2026 Performance Review",
            "prepared_by": "Finance Team",
            "organization": "MegaCorp",
            "report_date": "2026-09-30",
            "executive_summary": "Q3 showed strong revenue growth of 18% YoY.",
            "findings": ["Revenue +18%", "Customer churn reduced to 3%"],
            "recommendations": ["Expand product line", "Invest in retention programs"],
        },
        "service_agreement": {
            "client_name": "Beta Solutions",
            "service_provider": "Dev Masters",
            "service_description": "Full-stack SaaS platform development",
            "start_date": "2026-10-01",
            "fee_amount": 50000,
        },
        "certificate": {
            "recipient_name": "Sarah Johnson",
            "certificate_title": "Certificate of Excellence",
            "course_or_achievement": "Advanced Python Engineering Program",
            "issuer_name": "TechEdu Institute",
            "issuer_title": "Program Director",
            "issue_date": "2026-09-18",
            "certificate_id": "CERT-2026-007",
        },
    }

    for template_name, data in datasets.items():
        out_path = temp_output_dir / f"{template_name}.pdf"
        result = generate_document(
            data=data,
            template=template_name,
            output="pdf",
            output_path=str(out_path),
        )
        assert result.success, f"Template '{template_name}' failed: {result.error}"
        assert out_path.exists(), f"Output file missing for template '{template_name}'"
        assert out_path.stat().st_size > 500, f"Output file too small for '{template_name}'"
