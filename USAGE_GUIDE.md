# DocuGen Complete User & Developer Guide

Welcome to the comprehensive reference and usage guide for **DocuGen** (`docugen-library`). This guide covers every feature of the framework, from basic one-line document creation to advanced cryptographic signing, dynamic barcode generation, multi-language internationalization, and chatbot backend integrations.

---

## Table of Contents

1. [Introduction & Architectural Overview](#1-introduction--architectural-overview)
2. [Installation Options](#2-installation-options)
3. [Quick Start (30-Second Example)](#3-quick-start-30-second-example)
4. [Output Formats (PDF, DOCX, HTML, XLSX)](#4-output-formats-pdf-docx-html-xlsx)
5. [Advanced Watermarks (Text, Status & Image Logos)](#5-advanced-watermarks-text-status--image-logos)
6. [Cryptographic Digital Signatures & Verification](#6-cryptographic-digital-signatures--verification)
7. [Dynamic 1D Barcodes & 2D QR Codes](#7-dynamic-1d-barcodes--2d-qr-codes)
8. [Multi-Language & Currency in Words (i18n)](#8-multi-language--currency-in-words-i18n)
9. [High-Throughput Async & Batch Processing](#9-high-throughput-async--batch-processing)
10. [Custom Templates & Document Types](#10-custom-templates--document-types)
11. [Plugging DocuGen into AI Agents & Chatbots](#11-plugging-docugen-into-ai-agents--chatbots)
12. [Command-Line Interface (CLI) Reference](#12-command-line-interface-cli-reference)
13. [How to Publish DocuGen to PyPI (100% Free)](#13-how-to-publish-docugen-to-pypi-100-free)

---

## 1. Introduction & Architectural Overview

DocuGen is built on a **local-first, format-neutral Document Intermediate Representation (IR)** principle:

```
Raw Data (Dict / JSON / Pydantic)
               │
               ▼
   Normalization & Schema Validation
               │
               ▼
    Document Intermediate Representation (IR)
  (Sections, Paragraphs, Tables, QR, Watermarks, Signatures)
               │
  ┌────────────┼─────────────┬─────────────┐
  ▼            ▼             ▼             ▼
PDF Renderer  DOCX Renderer HTML Renderer XLSX Renderer
```

### Why this architecture matters:
- **Write Once, Render Anywhere**: You define or pass your data once, and you can render it into a PDF for printing, a Word DOCX for editing, an HTML page for web portals, or an Excel XLSX spreadsheet for financial records.
- **Strict Privacy (Zero Cloud Calls)**: All generation logic executes directly in Python. No patient, employee, or financial data ever leaves your server.
- **Deterministic & Auditable**: Built-in schema enforcement, clause logic, and cryptographic signing guarantee compliance and reproducibility.

---

## 2. Installation Options

### Option A: Install from PyPI (Recommended)
The easiest way to install DocuGen — works anywhere Python is available:
```bash
pip install docugen-library
```

### Option B: Direct Installation from Git
To install the latest development version directly from GitHub:
```bash
pip install git+https://github.com/swayamprabhu2005/DocuGen.git
```

### Option C: Local Editable Installation (Development)
If working within a local clone or contributing to the project:
```bash
git clone https://github.com/swayamprabhu2005/DocuGen.git
cd DocuGen
pip install -e .
```

---

## 3. Quick Start (30-Second Example)

Generate an official document in 4 lines of code:

```python
from docugen import generate_document

result = generate_document(
    data={
        "invoice_number": "INV-2026-001",
        "issue_date": "2026-10-02",
        "due_date": "2026-10-16",
        "seller_name": "Apex Engineering Ltd",
        "buyer_name": "Global Manufacturing Corp",
        "items": [
            {"description": "Industrial Robotics Calibration", "quantity": 2, "unit_price": 2500.0, "total": 5000.0},
            {"description": "Safety Audit & Compliance Cert", "quantity": 1, "unit_price": 1200.0, "total": 1200.0},
        ],
        "total_amount": 6200.0,
    },
    template="invoice",
    output="pdf",
    output_path="output/invoice.pdf",
)

if result.success:
    print(f"Generated {result.output_path} ({result.file_size_bytes} bytes)")
```

---

## 4. Output Formats (PDF, DOCX, HTML, XLSX)

DocuGen supports four output formats by simply altering the `output` parameter in `generate_document()`:

```python
# 1. High-Precision PDF
generate_document(data, template="invoice", output="pdf", output_path="invoice.pdf")

# 2. Microsoft Word DOCX
generate_document(data, template="invoice", output="docx", output_path="invoice.docx")

# 3. Responsive HTML (Web & Email Ready)
generate_document(data, template="invoice", output="html", output_path="invoice.html")

# 4. Microsoft Excel Spreadsheet (Formatted Data Grids)
generate_document(data, template="invoice", output="xlsx", output_path="invoice.xlsx")
```

### Dry Run (Preview IR Without Creating Files)
To inspect or serialize the intermediate representation without writing anything to disk:
```python
result = generate_document(data, template="invoice", dry_run=True)
doc_ir = result.document_ir
print("Document Title:", doc_ir.metadata.title)
print("Sections count:", len(doc_ir.sections))
```

---

## 5. Advanced Watermarks (Text, Status & Image Logos)

DocuGen supports diagonal text watermarks, semantic status badges, and background crest/logo watermarks across PDF and DOCX.

### A. Status Watermarks (PAID, DRAFT, CONFIDENTIAL, VOID)
```python
from docugen import generate_document
from docugen.core.document_ir import Watermark

# Using dictionary configuration
generate_document(
    data=invoice_data,
    template="invoice",
    output="pdf",
    output_path="paid_invoice.pdf",
    watermark={
        "status": "PAID",
        "text": "PAID - VERIFIED",
        "color": "#28a745",    # Forest green
        "opacity": 0.14,       # Subtle transparency
        "rotation": 45,        # 45-degree angle
        "font_size": 52.0,
    }
)
```

### B. Image Logo / Emblem Watermarks
To place a company seal or hospital emblem faintly in the background of every page:
```python
generate_document(
    data=clinical_data,
    template="medical_report",
    output="pdf",
    output_path="watermarked_report.pdf",
    watermark={
        "image_path": "assets/hospital_crest.png",
        "opacity": 0.18,
    }
)
```

---

## 6. Cryptographic Digital Signatures & Verification

DocuGen provides built-in enterprise-grade cryptographic digital signing for PDFs using 2048-bit RSA keys and SHA-256 digests. It allows automated generation of self-signed X.509 certificates and tamper detection.

### Step 1: Generate a Keypair & Certificate
```python
from pathlib import Path
from docugen import generate_self_signed_certificate

# Generate 2048-bit RSA private key and self-signed X.509 certificate
key_bytes, cert_bytes = generate_self_signed_certificate(
    common_name="Dr. Marcus Brody, MD (Chief Neurologist)",
    organization="Apollo Memorial Health System",
    country="US",
    validity_days=365,
)

Path("certs/doctor_key.pem").write_bytes(key_bytes)
Path("certs/doctor_cert.pem").write_bytes(cert_bytes)
```

### Step 2: Sign a Generated Document
```python
from docugen import generate_document, DigitalSignatureConfig

sig_config = DigitalSignatureConfig(
    certificate_path="certs/doctor_cert.pem",
    private_key_path="certs/doctor_key.pem",
    signer_name="Dr. Marcus Brody, MD",
    reason="Certified Clinical Approval and Verification",
    location="Mumbai Diagnostics Center",
    contact_info="marcus.brody@apollo.org",
)

result = generate_document(
    data=patient_record,
    template="medical_receipt",
    output="pdf",
    output_path="certified_record.pdf",
    digital_signature=sig_config,
)
```

### Step 3: Cryptographically Verify the Document
Anyone receiving the PDF can verify its authentic origin and check whether it was modified:

```python
from docugen import verify_pdf_signature

status = verify_pdf_signature("certified_record.pdf")

if status["valid"]:
    print(f"Document is AUTHENTIC and UNTAMPERED.")
    print(f"Signer: {status['signer']}")
    print(f"Organization: {status['organization']}")
    print(f"Timestamp: {status['timestamp']}")
    print(f"SHA-256 Digest: {status['digest']}")
else:
    print(f"WARNING: Verification failed! Reason: {status.get('error')}")
```

> **Tamper Proof**: If a third party changes even a single letter, number, or price in the PDF, `verify_pdf_signature` immediately reports: `"Document has been modified or tampered with since signing (digest mismatch)."`

---

## 7. Dynamic 1D Barcodes & 2D QR Codes

DocuGen includes a pure-Python barcode and QR generator that renders vector drawings in PDF, embedded pictures in DOCX, and inline base64 in HTML without any OS-level C binary dependencies.

### Adding Barcodes and QR Codes in Document IR:
```python
from docugen.core.document_ir import BarcodeElement, QRCodeElement

# 1D Code128 Barcode (Pharmacy dispense, inventory tracking)
barcode = BarcodeElement(
    data="RX202699384",
    barcode_type="code128",   # "code128", "ean13", "standard39"
    width=280.0,
    height=48.0,
    caption="Rx Code: RX202699384"
)

# 2D QR Code (URL link, cryptographic payload verification)
qr_code = QRCodeElement(
    data="https://health.apollo.org/verify?rx=RX202699384&hash=b1756a59",
    size=120.0,
    caption="Scan with any smartphone camera to verify record authenticity"
)
```

Both elements render cleanly and crisply across **PDF**, **Word DOCX**, and **HTML**.

---

## 8. Multi-Language & Currency in Words (i18n)

### A. Number to Words Conversion
DocuGen provides legal-grade numeric-to-words conversion supporting both the **Indian numbering system (Lakhs/Crores)** and the **International/Western system (Millions/Billions)**:

```python
from docugen import amount_to_words, format_currency

amount = 1450250.75

# Indian Rupee Format (Lakhs & Crores)
words_inr = amount_to_words(amount, currency="INR")
print(words_inr)
# → "Fourteen Lakh Fifty Thousand Two Hundred Fifty Rupees and Seventy Five Paise Only"

# US Dollar Format (Millions & Billions)
words_usd = amount_to_words(amount, currency="USD")
print(words_usd)
# → "One Million Four Hundred Fifty Thousand Two Hundred Fifty Dollars and Seventy Five Cents Only"

# Currency formatting with localized symbols
print(format_currency(amount, currency="INR"))  # ₹1,450,250.75
print(format_currency(amount, currency="USD"))  # $1,450,250.75
print(format_currency(amount, currency="EUR"))  # €1,450,250.75
```

### B. Multi-Language Translations & Jinja2 Filters
DocuGen contains built-in translation dictionaries for English (`en`), Spanish (`es`), French (`fr`), German (`de`), and Hindi (`hi`):

```python
from docugen import translate_term

print(translate_term("total_amount", lang="es"))  # Monto Total
print(translate_term("invoice", lang="hi"))       # चालान (Invoice)
print(translate_term("paid", lang="fr"))          # PAYÉ
```

In your Jinja2 templates, you can use the filters directly:
```jinja2
Total: {{ total_num | format_currency('INR') }}
In Words: {{ total_num | amount_to_words('INR') }}
Field Label: {{ 'due_date' | translate('es') }}
```

---

## 9. High-Throughput Async & Batch Processing

For web frameworks (FastAPI, Starlette, Tornado) or background worker queues (Celery, RQ, Redis Streams), DocuGen provides non-blocking async functions:

### Non-blocking FastAPI Endpoint:
```python
from fastapi import FastAPI
from docugen import generate_document_async

app = FastAPI()

@app.post("/documents/generate")
async def generate_bill(payload: dict):
    # Offloaded to thread pool, keeping the async event loop responsive
    result = await generate_document_async(
        data=payload,
        template="invoice",
        output="pdf",
        output_path=f"exports/{payload['id']}.pdf"
    )
    return {"status": "success", "file": result.output_path}
```

### Concurrent Batch Generation (Bounded Concurrency):
```python
import asyncio
from docugen import generate_documents_batch

async def run_batch():
    batch_jobs = [
        {
            "template": "invoice",
            "data": {"invoice_number": f"INV-{i}", "total_amount": 500.0 * i},
            "output": "pdf",
            "output_path": f"exports/batch_{i}.pdf",
        }
        for i in range(1, 21)
    ]

    # Concurrently generates 20 documents using 4 parallel workers
    results = await generate_documents_batch(batch_jobs, max_concurrency=4)
    print(f"Generated {len(results)} documents.")

asyncio.run(run_batch())
```

---

## 10. Custom Templates & Document Types

You can register your own document templates using a custom composer function:

```python
from docugen import register_template
from docugen.templates.registry import TemplateDefinition
from docugen.core.document_ir import Document, DocumentMetadata, Section, Paragraph, Table, TableRow, TableCell

def compose_lab_report(data, template):
    doc = Document(
        metadata=DocumentMetadata(title="Clinical Laboratory Findings", document_type="lab_report"),
        sections=[
            Section(
                title="Laboratory Investigations",
                elements=[
                    Paragraph.from_text(f"Patient Name: {data['patient_name']}"),
                    Table(rows=[
                        TableRow(is_header=True, cells=[
                            TableCell(content="Test", bold=True),
                            TableCell(content="Observed Value", bold=True),
                        ]),
                        TableRow(cells=[
                            TableCell(content="Hemoglobin"),
                            TableCell(content="14.2 g/dL"),
                        ])
                    ], bordered=True)
                ]
            )
        ]
    )
    return doc

# Register the template
register_template(TemplateDefinition(
    name="lab_report",
    document_type="lab_report",
    composer=compose_lab_report,
))

# Use it immediately
docugen.generate_document(
    data={"patient_name": "Eleanor Vance"},
    template="lab_report",
    output="pdf",
    output_path="lab_report.pdf"
)
```

---

## 11. Plugging DocuGen into AI Agents & Chatbots

Because all DocuGen entry points take standard dictionaries and Pydantic schemas, integrating DocuGen as an LLM Tool (Function Calling) takes less than 10 lines of code.

### Tool Definition for Gemini / OpenAI / Claude:
```python
docugen_tool_schema = {
    "name": "generate_document",
    "description": "Generate an official PDF, DOCX, HTML, or Excel document (invoice, receipt, contract, report).",
    "parameters": {
        "type": "object",
        "properties": {
            "template": {"type": "string", "enum": ["invoice", "nda", "employment_contract", "certificate", "business_report"]},
            "output": {"type": "string", "enum": ["pdf", "docx", "html", "xlsx"]},
            "data": {"type": "object", "description": "Structured fields matching the document type"},
            "watermark_status": {"type": "string", "description": "Optional watermark like PAID or DRAFT"}
        },
        "required": ["template", "data"]
    }
}
```

### Chatbot Webhook Execution:
```python
def execute_llm_tool(arguments: dict):
    from docugen import generate_document
    
    watermark = {"status": arguments["watermark_status"]} if "watermark_status" in arguments else None
    
    result = generate_document(
        data=arguments["data"],
        template=arguments["template"],
        output=arguments.get("output", "pdf"),
        output_path=f"chat_downloads/doc_{time.time()}.{arguments.get('output', 'pdf')}",
        watermark=watermark
    )
    return {"file_url": result.output_path, "success": result.success}
```

When a user in chat says: *"Create an invoice for 3 hours of consulting at $150/hr and mark it PAID"*, the chatbot calls the tool, DocuGen builds the file locally, and the user receives the download link instantly.

---

## 12. Command-Line Interface (CLI) Reference

DocuGen installs a native CLI executable `docugen`:

```bash
# Generate document from JSON data file
docugen generate --template invoice --data data.json --output invoice.pdf --format pdf

# Validate JSON data against document schema without generating
docugen validate --template employment_contract --data employee.json

# List registered templates
docugen templates list

# List registered schemas
docugen schemas list

# Show detailed schema fields and types for a document type
docugen schemas show invoice
```

---

## 13. How to Publish DocuGen to PyPI (100% Free)

Publishing open-source Python packages to **PyPI (Python Package Index)** is **100% completely free**. Once published, anyone in the world can run `pip install docugen-library`.

Here is the exact step-by-step process:

### Step 1: Create a Free Account on PyPI
1. Go to [https://pypi.org/account/register/](https://pypi.org/account/register/) and create a free account.
2. Under **Account Settings**, enable Two-Factor Authentication (2FA) and navigate to **API tokens**.
3. Create an API token (give it a name like `docugen-publish`) and copy the token string (`pypi-AgEI...`).

### Step 2: Install Build Tools
In your terminal, install standard packaging utilities:
```bash
pip install --upgrade build twine
```

### Step 3: Verify the Package Name
In `pyproject.toml`, the package name is set to:
```toml
[project]
name = "docugen-library"
version = "0.1.0"
```
*(You can verify on [pypi.org/search](https://pypi.org/search/?q=docugen-library) that `docugen-library` is available).*

### Step 4: Build Distribution Bundles
Run this command from the repository root:
```bash
python -m build
```
This generates a `dist/` directory containing two clean distribution files:
- `docugen_library-0.1.0.tar.gz` (Source Archive)
- `docugen_library-0.1.0-py3-none-any.whl` (Built Wheel)

### Step 5: (Optional) Test on TestPyPI First
If you want to do a dry-run test without affecting production PyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

### Step 6: Upload to Official PyPI
Upload your distribution to the official global repository:
```bash
python -m twine upload dist/*
```
- **Username**: `__token__`
- **Password**: *(Paste your API token starting with `pypi-...`)*

### That's it!
Your package is now live. Anyone can immediately install and use it in their projects:
```bash
pip install docugen-library
```
