"""
DocuGen AI – Custom Document Type Example
==========================================
Shows how to register a new document type (Offer Letter) with a custom schema,
composer, clauses, and validator — then generate documents using it.
"""

from pathlib import Path
from docugen.core.schemas import DocumentSchema, FieldDefinition, FieldType
from docugen.core.document_ir import Document, DocumentMetadata, Section, Paragraph
from docugen.generation.clause_engine import ClauseDefinition
from docugen.core.models import ValidationResult

import docugen


# ── Schema ─────────────────────────────────────────────────────────────────────
offer_letter_schema = DocumentSchema(
    document_type="offer_letter",
    title="Job Offer Letter",
    description="Formal employment offer letter",
    fields={
        "candidate_name": FieldDefinition(name="candidate_name", type=FieldType.STRING, required=True),
        "position": FieldDefinition(name="position", type=FieldType.STRING, required=True),
        "department": FieldDefinition(name="department", type=FieldType.STRING, required=False, default="Engineering"),
        "base_salary": FieldDefinition(name="base_salary", type=FieldType.NUMBER, required=True, minimum=0.0),
        "start_date": FieldDefinition(name="start_date", type=FieldType.DATE, required=True),
        "offer_expiry": FieldDefinition(name="offer_expiry", type=FieldType.DATE, required=False),
        "hiring_manager": FieldDefinition(name="hiring_manager", type=FieldType.STRING, required=False),
        "company_name": FieldDefinition(name="company_name", type=FieldType.STRING, required=False, default="Our Company"),
    },
)


# ── Custom Clause ──────────────────────────────────────────────────────────────
at_will_clause = ClauseDefinition(
    clause_id="at_will_employment",
    title="3.0 At-Will Employment",
    document_types=["offer_letter"],
    priority=30,
    required=True,
    template_text=(
        "Your employment with {{ company_name }} is at-will. Either you or "
        "{{ company_name }} may terminate the employment relationship at any "
        "time, with or without cause or notice."
    ),
)


# ── Composer ──────────────────────────────────────────────────────────────────
def compose_offer_letter(data, template):
    from docugen.generation.clause_engine import get_clause_engine
    from docugen.core.document_ir import (
        Heading, SignatureBlock, Signer, Paragraph, Section
    )

    clauses = list(get_clause_engine().resolve_clauses_for_document("offer_letter", data))

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
                    Paragraph.from_text(f"Dear {data.get('candidate_name')},", space_after=10.0),
                    Paragraph.from_text(
                        f"We are delighted to extend this offer of employment for the role of "
                        f"**{data.get('position')}** within the {data.get('department')} department "
                        f"at {data.get('company_name')}.",
                        space_after=10.0,
                    ),
                    Paragraph.from_text(
                        f"Compensation: ${float(data.get('base_salary', 0)):,.2f} per year, "
                        f"effective {data.get('start_date')}.",
                        space_after=10.0,
                    ),
                    *clauses,
                    Paragraph.from_text(
                        f"This offer expires on {data.get('offer_expiry', '30 days from the date of this letter')}. "
                        "Please sign and return a copy at your earliest convenience.",
                        space_after=20.0,
                    ),
                    SignatureBlock(
                        signers=[
                            Signer(name=data.get("hiring_manager", "Hiring Manager"), title="Hiring Manager"),
                            Signer(name=data.get("candidate_name", "Candidate"), title="Accepted By"),
                        ],
                    ),
                ],
            )
        ],
    )


# ── Custom Validator ───────────────────────────────────────────────────────────
def validate_salary_range(data, schema):
    result = ValidationResult(valid=True)
    salary = data.get("base_salary")
    if salary and salary > 500_000:
        result.add_warning(
            code="HIGH_SALARY",
            field="base_salary",
            message=f"Salary ${salary:,.0f} exceeds $500K — please verify this is correct.",
        )
    return result


# ── Register ───────────────────────────────────────────────────────────────────
def register():
    docugen.register_document_type(
        name="offer_letter",
        schema=offer_letter_schema,
        composer=compose_offer_letter,
        clauses=[at_will_clause],
        validators=[validate_salary_range],
    )
    print("✓ 'offer_letter' document type registered")


def main():
    print(f"DocuGen AI v{docugen.__version__}")
    print("=" * 50)
    print("Custom Document Type: Offer Letter\n")

    register()

    offer_data = {
        "candidate_name": "Priya Patel",
        "position": "Lead Machine Learning Engineer",
        "department": "AI Research",
        "base_salary": 185_000,
        "start_date": "2026-11-01",
        "offer_expiry": "2026-10-01",
        "hiring_manager": "Dr. Anjali Mehta",
        "company_name": "FutureTech AI",
    }

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # PDF
    result = docugen.generate_document(
        data=offer_data,
        template="offer_letter",
        output="pdf",
        output_path=str(output_dir / "offer_letter.pdf"),
    )
    if result.success:
        size_kb = Path(result.output_path).stat().st_size / 1024
        print(f"✓ PDF: {result.output_path}  ({size_kb:.1f} KB)")
    else:
        print(f"✗ Failed: {result.error}")

    print("\nDone!")


if __name__ == "__main__":
    main()
