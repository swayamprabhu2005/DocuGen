"""
DocuGen AI – NDA Example
=========================
Generates a Non-Disclosure Agreement with confidentiality clauses.
"""

from pathlib import Path
import docugen


def main():
    print(f"DocuGen AI v{docugen.__version__}")
    print("=" * 50)
    print("Generating Non-Disclosure Agreement...")

    nda_data = {
        "disclosing_party": "Innovatech Solutions Inc.",
        "receiving_party": "Venture Capital Partners LLC",
        "effective_date": "2026-10-01",
        "purpose": "Evaluation of a potential strategic investment and acquisition of Innovatech Solutions Inc.",
        "confidentiality_period_years": 3,
        "governing_law": "State of Delaware",
        "return_period_days": 30,
    }

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # PDF
    pdf_result = docugen.generate_document(
        data=nda_data,
        template="nda",
        output="pdf",
        output_path=str(output_dir / "nda.pdf"),
    )
    if pdf_result.success:
        size_kb = Path(pdf_result.output_path).stat().st_size / 1024
        print(f"✓ NDA PDF generated: {pdf_result.output_path}  ({size_kb:.1f} KB)")
        print(f"  Document type: {pdf_result.document_type}")
        print(f"  Classification: {pdf_result.classification.method}")

    # Validate
    result = docugen.validate_document_data(nda_data, template="nda")
    print(f"\n✓ Validation: {'PASSED' if result.valid else 'FAILED'}")
    if result.warnings:
        for w in result.warnings:
            print(f"  ⚠ {w.message}")

    print("\nDone!")


if __name__ == "__main__":
    main()
