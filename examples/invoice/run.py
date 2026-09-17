"""
DocuGen AI – Invoice Example
=============================
Demonstrates generating a professional invoice with line items.
"""

from pathlib import Path
import docugen


def main():
    print(f"DocuGen AI v{docugen.__version__}")
    print("=" * 50)
    print("Generating Invoice...")

    invoice_data = {
        "invoice_number": "INV-2026-0042",
        "issue_date": "2026-09-18",
        "due_date": "2026-10-18",
        "seller_name": "Digital Craft Studio",
        "seller_address": "742 Evergreen Terrace, Portland, OR 97201",
        "seller_email": "billing@digitalcraft.io",
        "buyer_name": "Global Enterprises Inc.",
        "buyer_address": "1000 Corporate Park, Chicago, IL 60601",
        "items": [
            {"description": "UI/UX Design – Phase 1 (Discovery & Wireframes)", "quantity": 1, "unit_price": 4800.00},
            {"description": "Frontend Development – React Application (80 hrs)", "quantity": 80, "unit_price": 95.00},
            {"description": "Backend API Development (Python/FastAPI)", "quantity": 60, "unit_price": 110.00},
            {"description": "QA Testing & Bug Fixes", "quantity": 20, "unit_price": 75.00},
        ],
        "subtotal": 21_900.00,
        "tax_rate": 8.5,
        "tax_amount": 1_861.50,
        "total_amount": 23_761.50,
        "payment_terms": "Net 30 days",
        "bank_details": "Chase Bank | Account: 8872453901 | Routing: 021000021",
        "currency": "USD",
    }

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # PDF
    pdf_result = docugen.generate_document(
        data=invoice_data,
        template="invoice",
        output="pdf",
        output_path=str(output_dir / "invoice.pdf"),
    )
    if pdf_result.success:
        size_kb = Path(pdf_result.output_path).stat().st_size / 1024
        print(f"✓ Invoice PDF: {pdf_result.output_path}  ({size_kb:.1f} KB)")

    # DOCX
    docx_result = docugen.generate_document(
        data=invoice_data,
        template="invoice",
        output="docx",
        output_path=str(output_dir / "invoice.docx"),
    )
    if docx_result.success:
        size_kb = Path(docx_result.output_path).stat().st_size / 1024
        print(f"✓ Invoice DOCX: {docx_result.output_path}  ({size_kb:.1f} KB)")

    print("\nDone!")


if __name__ == "__main__":
    main()
