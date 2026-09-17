"""Tests for custom document type and plugin registration."""

from pathlib import Path
import pytest

from docugen import (
    Document,
    DocumentMetadata,
    Paragraph,
    Section,
    generate_document,
    list_document_types,
    list_templates,
    register_document_type,
    validate_document_data,
)
from docugen.core.schemas import DocumentSchema, FieldDefinition, FieldType
from docugen.generation.clause_engine import ClauseDefinition


def _make_offer_letter_schema():
    return DocumentSchema(
        document_type="offer_letter",
        title="Job Offer Letter",
        description="Formal employment offer letter",
        fields={
            "candidate_name": FieldDefinition(
                name="candidate_name", type=FieldType.STRING, required=True, description="Candidate full name"
            ),
            "position": FieldDefinition(
                name="position", type=FieldType.STRING, required=True, description="Job title being offered"
            ),
            "base_salary": FieldDefinition(
                name="base_salary", type=FieldType.NUMBER, required=True, minimum=0.0, description="Annual base salary"
            ),
            "start_date": FieldDefinition(
                name="start_date", type=FieldType.DATE, required=True, description="Proposed start date"
            ),
        },
    )


def _offer_letter_composer(data, template):
    return Document(
        metadata=DocumentMetadata(
            title=f"Offer Letter – {data.get('candidate_name')}",
            document_type="offer_letter",
            template_name=template.name,
        ),
        sections=[
            Section(
                title="JOB OFFER LETTER",
                elements=[
                    Paragraph.from_text(
                        f"Dear {data.get('candidate_name')},",
                        space_after=10.0,
                    ),
                    Paragraph.from_text(
                        f"We are pleased to offer you the position of {data.get('position')} "
                        f"with a base salary of ${float(data.get('base_salary', 0)):,.2f} per year, "
                        f"commencing on {data.get('start_date')}.",
                        space_after=12.0,
                    ),
                    Paragraph.from_text(
                        "This offer is subject to successful completion of background checks. "
                        "Please sign and return one copy of this letter.",
                    ),
                ],
            )
        ],
    )


def test_register_custom_document_type(temp_output_dir):
    """Acceptance test: registering a new document type and generating a document."""
    schema = _make_offer_letter_schema()
    register_document_type(
        name="offer_letter",
        schema=schema,
        composer=_offer_letter_composer,
    )

    # Verify it appears in registries
    assert "offer_letter" in list_document_types()
    assert "offer_letter" in list_templates()

    # Validate with missing field
    val_missing = validate_document_data(
        {"candidate_name": "Jane Smith"},
        template="offer_letter",
        strict=False,
    )
    assert not val_missing.valid
    assert "position" in val_missing.missing_fields

    # Full data – validate passes
    full_data = {
        "candidate_name": "Jane Smith",
        "position": "Senior Data Scientist",
        "base_salary": 195000,
        "start_date": "2026-11-01",
    }
    val_full = validate_document_data(full_data, template="offer_letter")
    assert val_full.valid

    # Generate PDF
    out_pdf = temp_output_dir / "offer_letter.pdf"
    result = generate_document(
        data=full_data,
        template="offer_letter",
        output="pdf",
        output_path=str(out_pdf),
    )
    assert result.success, f"Custom doc type PDF failed: {result.error}"
    assert out_pdf.exists()

    # Generate DOCX
    out_docx = temp_output_dir / "offer_letter.docx"
    result_docx = generate_document(
        data=full_data,
        template="offer_letter",
        output="docx",
        output_path=str(out_docx),
    )
    assert result_docx.success
    assert out_docx.exists()


def test_custom_clause_in_document_type(temp_output_dir):
    """Ensure custom clauses are properly resolved for custom document types."""
    schema = DocumentSchema(
        document_type="partnership_deed",
        title="Partnership Deed",
        fields={
            "partner_a": FieldDefinition(name="partner_a", type=FieldType.STRING, required=True),
            "partner_b": FieldDefinition(name="partner_b", type=FieldType.STRING, required=True),
            "profit_share": FieldDefinition(name="profit_share", type=FieldType.NUMBER, required=True),
        },
    )

    clause = ClauseDefinition(
        clause_id="partnership_profit",
        title="Profit Sharing",
        document_types=["partnership_deed"],
        priority=10,
        required=True,
        template_text=(
            "The parties {{ partner_a }} and {{ partner_b }} agree to share profits "
            "at a ratio of {{ profit_share }}% to {{ 100 - profit_share }}%."
        ),
    )

    def compose_deed(data, template):
        from docugen.generation.clause_engine import get_clause_engine

        clauses = get_clause_engine().resolve_clauses_for_document("partnership_deed", data)
        return Document(
            metadata=DocumentMetadata(title="Partnership Deed", document_type="partnership_deed"),
            sections=[Section(title="PARTNERSHIP DEED", elements=list(clauses))],
        )

    register_document_type(
        name="partnership_deed",
        schema=schema,
        clauses=[clause],
        composer=compose_deed,
    )

    data = {"partner_a": "Alice Ltd", "partner_b": "Bob Co", "profit_share": 60}
    result = generate_document(
        data=data,
        template="partnership_deed",
        output="pdf",
        output_path=str(temp_output_dir / "partnership.pdf"),
    )
    assert result.success, f"Partnership deed generation failed: {result.error}"


def test_custom_validator_integration():
    """Custom validator is called and can block generation."""
    from docugen.core.models import ValidationResult
    from docugen.validation.validator import register_validator

    def salary_cap_validator(data, schema):
        result = ValidationResult(valid=True)
        salary = data.get("salary") or data.get("base_salary")
        if salary and salary > 1_000_000:
            result.add_error(
                code="SALARY_EXCEEDS_CAP",
                field="salary",
                message="Salary exceeds the maximum permitted value of $1,000,000.",
            )
        return result

    register_validator("employment_contract", salary_cap_validator)

    valid_result = validate_document_data(
        {
            "employee_name": "Bob",
            "company_name": "Corp",
            "salary": 150000,
            "joining_date": "2026-10-01",
        },
        template="employment_contract",
        strict=False,
    )
    assert valid_result.valid

    invalid_result = validate_document_data(
        {
            "employee_name": "Rich Person",
            "company_name": "Corp",
            "salary": 2_000_000,
            "joining_date": "2026-10-01",
        },
        template="employment_contract",
        strict=False,
    )
    assert not invalid_result.valid
    assert any(e.code == "SALARY_EXCEEDS_CAP" for e in invalid_result.errors)
