"""
DocuGen AI – Employment Contract Example
=========================================
Demonstrates generating an employment contract in both PDF and DOCX format.
"""

import os
from pathlib import Path

import docugen


def main():
    print(f"DocuGen AI v{docugen.__version__}")
    print("=" * 50)
    print("Generating Employment Contract...")

    # ── Employee Data ──────────────────────────────────────────────────────────
    employee_data = {
        "employee_name": "Alexandra Chen",
        "company_name": "Quantum Technologies Ltd",
        "job_title": "Principal Software Engineer",
        "joining_date": "2026-10-15",
        "salary": 145_000,
        "salary_period": "year",
        "work_location": "San Francisco, CA (Hybrid)",
        "probation_months": 3,
        "notice_period_months": 2,
        "annual_leave_days": 25,
        "non_compete_months": 12,
        "remote_work_allowed": True,
        "benefits": "Health, Dental, Vision, 401(k) matching, Stock Options",
        "governing_law": "California",
    }

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # ── PDF Generation ─────────────────────────────────────────────────────────
    pdf_result = docugen.generate_document(
        data=employee_data,
        template="employment_contract",
        output="pdf",
        output_path=str(output_dir / "employment_contract.pdf"),
    )

    if pdf_result.success:
        size_kb = Path(pdf_result.output_path).stat().st_size / 1024
        print(f"✓ PDF generated: {pdf_result.output_path}  ({size_kb:.1f} KB)")
    else:
        print(f"✗ PDF generation failed: {pdf_result.error}")

    # ── DOCX Generation ────────────────────────────────────────────────────────
    docx_result = docugen.generate_document(
        data=employee_data,
        template="employment_contract",
        output="docx",
        output_path=str(output_dir / "employment_contract.docx"),
    )

    if docx_result.success:
        size_kb = Path(docx_result.output_path).stat().st_size / 1024
        print(f"✓ DOCX generated: {docx_result.output_path}  ({size_kb:.1f} KB)")
    else:
        print(f"✗ DOCX generation failed: {docx_result.error}")

    # ── Dry-run (Preview IR) ──────────────────────────────────────────────────
    dry_result = docugen.generate_document(
        data=employee_data,
        template="employment_contract",
        output="pdf",
        dry_run=True,
    )

    if dry_result.success and dry_result.document_ir:
        doc_ir = dry_result.document_ir
        print(f"\n📄 Document IR Preview:")
        print(f"   Title   : {doc_ir.metadata.title}")
        print(f"   Sections: {len(doc_ir.sections)}")
        for i, s in enumerate(doc_ir.sections, 1):
            print(f"     {i}. {s.title or '(untitled)'}  ({len(s.elements)} element(s))")

    # ── Validation Example ────────────────────────────────────────────────────
    print("\n🔍 Validation Example (incomplete data):")
    incomplete_data = {"salary": 80000}
    val_result = docugen.validate_document_data(
        incomplete_data,
        template="employment_contract",
        strict=False,
    )
    print(f"   Valid: {val_result.valid}")
    if val_result.missing_fields:
        print(f"   Missing: {', '.join(val_result.missing_fields)}")

    print("\nDone!")


if __name__ == "__main__":
    main()
