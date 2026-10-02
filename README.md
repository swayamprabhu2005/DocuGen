# DocuGen

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License Apache 2.0">
  <img src="https://img.shields.io/badge/formats-PDF%20%7C%20DOCX%20%7C%20HTML%20%7C%20XLSX-purple" alt="Output Formats">
  <img src="https://img.shields.io/badge/security-SHA--256%20%2B%20RSA%20Digital%20Signatures-red" alt="Digital Signatures">
  <img src="https://img.shields.io/badge/privacy-100%25%20Local%20%28Zero%20Cloud%20Calls%29-brightgreen" alt="Local First">
</p>

**DocuGen** is a production-grade, local-first Python library that transforms structured application data into professionally formatted, audit-ready documents across **PDF**, **Word DOCX**, **responsive HTML**, and **Excel XLSX** — entirely without cloud dependencies, API subscriptions, or external render services.

Whether generating hospital billing receipts, legal NDAs, employment contracts, laboratory diagnostic reports, or financial invoices, DocuGen combines strict schema validation, cryptographic digital signing, dynamic barcode/QR generation, multi-language localization, and high-throughput async orchestration into a single Python library.

```python
from docugen import generate_document, DigitalSignatureConfig

result = generate_document(
    data={
        "invoice_number": "INV-2026-901",
        "date": "2026-10-02",
        "buyer_name": "Acme Health Systems",
        "seller_name": "Apollo Care Solutions",
        "items": [{"description": "Specialist Consultation", "quantity": 1, "unit_price": 450.0, "total": 450.0}],
        "total_amount": 450.0,
    },
    template="invoice",
    output="pdf",                 # "pdf" | "docx" | "html" | "xlsx"
    output_path="output/invoice.pdf",
    watermark={"status": "PAID", "rotation": 45, "opacity": 0.15},
    digital_signature=DigitalSignatureConfig(
        signer_name="Dr. Marcus Brody, MD",
        reason="Certified Clinical Billing Approval"
    )
)
# → output/invoice.pdf ✓ (Signed, watermarked, audit-verified)
```

---

## ✨ Core Highlights & Features

| Capability | What It Does |
|---|---|
| **Multi-Format Matrix** | Render the same data into **PDF** (vector layout), **Word DOCX** (editable), **HTML** (responsive web & email), or **Excel XLSX** (styled multi-column grids). |
| **Cryptographic Digital Signatures** | Generate 2048-bit RSA X.509 self-signed certificates, sign PDFs with SHA-256 + RSA-PKCS1v15 tamper-evident blocks, and verify document integrity with `verify_pdf_signature()`. |
| **Dynamic 1D Barcodes & 2D QR Codes** | Pure-Python Code128 barcodes and QR codes embedded seamlessly as PDF flowables, DOCX inline pictures, and HTML base64 SVGs without missing binary dependencies. |
| **Advanced Watermarks** | Diagonal status watermarks (`PAID`, `CONFIDENTIAL`, `DRAFT`, `VOID`) with customizable opacity and rotation, plus centered translucent image logos/crests. |
| **i18n & Currency in Words** | Localized formatting and automatic conversion of monetary amounts into words for both **Indian (Lakhs/Crores)** and **Western (Millions/Billions)** numbering systems, with translation dictionaries for English, Spanish, French, German, and Hindi. |
| **High-Throughput Async Engine** | Non-blocking `generate_document_async()` and concurrent `generate_documents_batch()` offloaded to thread worker pools for FastAPI, Starlette, Celery, and background queues. |
| **Local-First & Zero Cloud Leakage** | 100% of generation occurs inside your Python process. Zero client data is transmitted over the network — compliant with HIPAA, GDPR, and air-gapped security enclaves. |
| **AI Agent & Chatbot Ready** | Pre-built for LLM Tool Use / Function Calling (Gemini, OpenAI, Claude, LangChain, LangGraph). AI bots can reliably generate certified files directly in user chats. |
| **Schema Validation & Hybrid Classification** | Field-level type/range/regex checks and automatic document classification from raw payload dictionaries. |

---

## 📦 Installation

### From PyPI (Recommended):
```bash
pip install docugen-library
```

### From GitHub (Latest Dev Version):
```bash
pip install git+https://github.com/swayamprabhu2005/DocuGen.git
```

### From Local Source (Editable):
```bash
git clone https://github.com/swayamprabhu2005/DocuGen.git
cd DocuGen
pip install -e .
```

### Optional Extras:
```bash
pip install "docugen-library[dev]"   # Adds pytest, ruff, mypy for development
pip install "docugen-library[ml]"    # Adds scikit-learn for advanced ML-based classification
pip install "docugen-library[nlp]"   # Adds spaCy for NLP entity extraction
```

---

## 🚀 Quick Start Guide

### 1. Generating Different Formats from One Schema

```python
import docugen

data = {
    "report_title": "Q3 Financial Diagnostics & Clinical Review",
    "prepared_by": "Finance & Compliance Division",
    "organization": "Apollo Health Partners",
    "report_date": "2026-10-02",
    "executive_summary": "Quarterly overview of diagnostic volumes, surgical yields, and patient satisfaction metrics.",
}

# Generate PDF
docugen.generate_document(data, template="business_report", output="pdf", output_path="report.pdf")

# Generate Microsoft Word DOCX
docugen.generate_document(data, template="business_report", output="docx", output_path="report.docx")

# Generate Responsive HTML
docugen.generate_document(data, template="business_report", output="html", output_path="report.html")

# Generate Excel Spreadsheet
docugen.generate_document(data, template="business_report", output="xlsx", output_path="report.xlsx")
```

---

### 2. Digital Signatures & Cryptographic Verification

```python
from docugen import generate_document, DigitalSignatureConfig, verify_pdf_signature

# 1. Sign during PDF generation
result = generate_document(
    data={"invoice_number": "INV-100", "total_amount": 5000.0, "items": []},
    template="invoice",
    output="pdf",
    output_path="signed_contract.pdf",
    digital_signature=DigitalSignatureConfig(
        signer_name="Dr. Marcus Brody, MD",
        reason="Clinical Billing Certification",
        location="Mumbai Hospital Enclave",
    )
)

# 2. Cryptographically verify anywhere
verification = verify_pdf_signature("signed_contract.pdf")
print("Authentic:", verification["valid"])          # True
print("Signer:", verification["signer"])            # Dr. Marcus Brody, MD
print("SHA-256 Digest:", verification["digest"])    # e.g. b1756a59...
```

If anyone modifies even a single byte of the signed PDF, `verify_pdf_signature()` flags the file as tampered (`valid=False`).

---

### 3. Number-to-Words & Multi-Currency (i18n)

```python
from docugen import amount_to_words, format_currency

# Indian Numbering (Lakhs & Crores)
print(amount_to_words(1450250.75, currency="INR"))
# → "Fourteen Lakh Fifty Thousand Two Hundred Fifty Rupees and Seventy Five Paise Only"

# Western Numbering (Millions & Billions)
print(amount_to_words(1450250.75, currency="USD"))
# → "One Million Four Hundred Fifty Thousand Two Hundred Fifty Dollars and Seventy Five Cents Only"

# Formatted currency prefixes
print(format_currency(1450250.75, currency="INR"))  # ₹1,450,250.75
print(format_currency(1450250.75, currency="EUR"))  # €1,450,250.75
```

---

### 4. High-Throughput Async & Batch Processing

```python
import asyncio
from docugen import generate_document_async, generate_documents_batch

async def main():
    # Single non-blocking generation (perfect for FastAPI routes)
    res = await generate_document_async(
        data={"invoice_number": "INV-001", "total_amount": 250.0},
        template="invoice",
        output_path="async_invoice.pdf"
    )

    # Parallel batch generation with bounded concurrency
    jobs = [
        {"template": "invoice", "data": {"invoice_number": f"INV-{i}", "total_amount": i * 100}, "output_path": f"inv_{i}.pdf"}
        for i in range(10)
    ]
    results = await generate_documents_batch(jobs, max_concurrency=4)
    print(f"Generated {len(results)} documents concurrently!")

asyncio.run(main())
```

---

## 🤖 Chatbot & AI Agent Tool Integration

DocuGen functions have strict type hints, making it effortless to register as a function/tool for Gemini, OpenAI, Claude, LangChain, or custom LLM bots:

```python
# LLM Tool Schema
tools = [{
    "type": "function",
    "function": {
        "name": "generate_patient_document",
        "description": "Generate an official medical bill, prescription, or lab report PDF with barcodes and QR codes.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {"type": "string"},
                "services": {"type": "array", "items": {"type": "object"}},
                "total_amount": {"type": "number"},
                "document_type": {"type": "string", "enum": ["invoice", "lab_report", "prescription"]}
            },
            "required": ["patient_name", "total_amount"]
        }
    }
}]

# Webhook / Handler
def on_chatbot_tool_call(arguments: dict):
    file_path = f"generated/{arguments['patient_name']}_record.pdf"
    docugen.generate_document(
        data=arguments,
        template=arguments.get("document_type", "invoice"),
        output="pdf",
        output_path=file_path,
        watermark={"status": "PAID"}
    )
    return {"download_url": f"https://myhealth.app/files/{file_path}"}
```

---

## 🖥️ Command-Line Interface (CLI)

DocuGen includes a full-featured CLI:

```bash
# Generate a document from a JSON file
docugen generate --template invoice --data billing.json --output invoice.pdf --format pdf

# Validate payload data against document schema without rendering
docugen validate --template nda --data agreement.json

# Inspect available templates and schemas
docugen templates list
docugen schemas list
docugen schemas show invoice
```

---

## 📖 In-Depth Documentation

For complete API documentation, custom template creation, advanced flowables, and real-world deployment patterns, read the [Comprehensive User & Developer Guide](USAGE_GUIDE.md).

---

## 🧪 Running Tests

```bash
# Run full unit and integration test suite
pytest tests/ -v

# Run verification script with all advanced features
python D:/Test/New/test_new_features.py
```

---

## 📝 License

Licensed under the [Apache License 2.0](LICENSE). Free for commercial and open-source use.
