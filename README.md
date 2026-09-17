# DocuGen AI

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License Apache 2.0">
  <img src="https://img.shields.io/badge/version-0.1.0-orange" alt="Version 0.1.0">
  <img src="https://img.shields.io/badge/output-PDF%20%7C%20DOCX-lightgrey" alt="Output Formats">
</p>

**DocuGen AI** is a production-grade, local-first Python library that transforms structured data into professionally formatted documents — PDFs and DOCX files — without any cloud dependencies.

```python
import docugen

result = docugen.generate_document(
    data={
        "employee_name": "Alice Smith",
        "company_name": "Acme Corp",
        "salary": 90000,
        "joining_date": "2026-10-01",
    },
    template="employment_contract",
    output="pdf",
)
# → output/employment_contract.pdf  ✓
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **7 Built-in Document Types** | Employment Contract, NDA, Invoice, Quotation, Service Agreement, Business Report, Certificate |
| **Dual Output Formats** | PDF (ReportLab Platypus) and DOCX (python-docx) |
| **Intelligent Classification** | Auto-detects document type from input data using field-signature scoring |
| **Schema Validation** | Field-level type/range/enum/regex checks + cross-field consistency rules |
| **Clause Engine** | Conditional clause resolution with dependency ordering and Jinja2 templates |
| **Plugin System** | Register entirely new document types with custom schemas, composers, clauses, and validators |
| **NLP Extraction** | Regex + optional spaCy entity extraction for unstructured input text |
| **CLI** | `docugen generate`, `docugen validate`, `docugen schemas`, `docugen templates` |
| **Local-first** | No cloud calls, no API keys required |
| **Type-safe** | Full Pydantic v2 models throughout |

---

## 📦 Installation

### From PyPI (once published)
```bash
pip install docugen-ai
```

### From Source
```bash
git clone https://github.com/your-org/docugen-ai.git
cd docugen-ai
pip install -e ".[dev]"
```

### Optional Extras

```bash
pip install docugen-ai[ml]    # Adds scikit-learn for ML-based classification
pip install docugen-ai[nlp]   # Adds spaCy for NLP entity extraction
pip install docugen-ai[dev]   # Adds pytest, ruff, mypy for development
```

---

## 🚀 Quick Start

### Generate Documents via Python API

```python
import docugen

# ── Employment Contract ──────────────────────────────────────────────────────
result = docugen.generate_document(
    data={
        "employee_name": "Alexandra Chen",
        "company_name": "Quantum Technologies Ltd",
        "job_title": "Principal Software Engineer",
        "salary": 145_000,
        "joining_date": "2026-10-15",
    },
    template="employment_contract",
    output="pdf",               # "pdf" or "docx"
    output_path="output/contract.pdf",
)
print(result.success, result.output_path)

# ── Non-Disclosure Agreement ─────────────────────────────────────────────────
result = docugen.generate_document(
    data={
        "disclosing_party": "Innovatech Inc.",
        "receiving_party": "Venture Capital Partners",
        "effective_date": "2026-10-01",
        "purpose": "Evaluation of strategic investment",
    },
    template="nda",
    output="pdf",
)

# ── Invoice ──────────────────────────────────────────────────────────────────
result = docugen.generate_document(
    data={
        "invoice_number": "INV-2026-001",
        "issue_date": "2026-09-01",
        "due_date": "2026-10-01",
        "seller_name": "Digital Craft Studio",
        "buyer_name": "Global Enterprises Inc.",
        "items": [
            {"description": "Web Development", "quantity": 80, "unit_price": 95.0},
            {"description": "UI/UX Design", "quantity": 1, "unit_price": 4800.0},
        ],
        "subtotal": 12_400.0,
        "total_amount": 12_400.0,
    },
    template="invoice",
    output="pdf",
)
```

### Validate Without Generating

```python
result = docugen.validate_document_data(
    data={"salary": 50000},  # missing required fields
    template="employment_contract",
    strict=False,
)
print(result.valid)           # False
print(result.missing_fields)  # ['employee_name', 'company_name', 'joining_date']
```

### Dry Run (Preview Document IR)

```python
result = docugen.generate_document(
    data=my_data,
    template="employment_contract",
    output="pdf",
    dry_run=True,             # returns Document IR, no file written
)
doc_ir = result.document_ir
print(doc_ir.metadata.title)
print(len(doc_ir.sections), "sections")
```

### Classify Document Type from Data

```python
result = docugen.classify_document(
    data={"disclosing_party": "Corp A", "receiving_party": "Corp B"},
)
print(result.document_type)  # "nda"
print(result.confidence)     # 0.9
print(result.method)         # "rule_based"
```

---

## 🖥️ CLI Usage

```bash
# Generate a document
docugen generate \
  --template employment_contract \
  --data employee_data.json \
  --output contract.pdf \
  --format pdf

# Validate data without generating
docugen validate --template nda --data nda_data.json

# List all available templates
docugen templates list

# List all registered schemas
docugen schemas list

# Show schema fields for a document type
docugen schemas show employment_contract

# List all document types
docugen document-types list
```

---

## 🔌 Custom Document Types (Plugin System)

Register entirely new document types with your own schema, composer, clauses, and validators:

```python
from docugen.core.schemas import DocumentSchema, FieldDefinition, FieldType
from docugen.core.document_ir import Document, DocumentMetadata, Section, Paragraph
from docugen.generation.clause_engine import ClauseDefinition
import docugen

# 1. Define schema
schema = DocumentSchema(
    document_type="offer_letter",
    title="Job Offer Letter",
    fields={
        "candidate_name": FieldDefinition(name="candidate_name", type=FieldType.STRING, required=True),
        "position": FieldDefinition(name="position", type=FieldType.STRING, required=True),
        "base_salary": FieldDefinition(name="base_salary", type=FieldType.NUMBER, required=True),
        "start_date": FieldDefinition(name="start_date", type=FieldType.DATE, required=True),
    },
)

# 2. Define composer
def compose_offer_letter(data, template):
    return Document(
        metadata=DocumentMetadata(title=f"Offer – {data['candidate_name']}", document_type="offer_letter"),
        sections=[
            Section(
                title="JOB OFFER LETTER",
                elements=[
                    Paragraph.from_text(f"Dear {data['candidate_name']},"),
                    Paragraph.from_text(
                        f"We offer you the role of {data['position']} at ${data['base_salary']:,.0f}/year "
                        f"starting {data['start_date']}."
                    ),
                ],
            )
        ],
    )

# 3. Register
docugen.register_document_type(
    name="offer_letter",
    schema=schema,
    composer=compose_offer_letter,
)

# 4. Use like any built-in type
result = docugen.generate_document(
    data={"candidate_name": "Jane", "position": "Engineer", "base_salary": 120000, "start_date": "2026-11-01"},
    template="offer_letter",
    output="pdf",
)
```

---

## 📚 Built-in Document Types

| Type | Required Fields |
|---|---|
| `employment_contract` | `employee_name`, `company_name`, `salary`, `joining_date` |
| `nda` | `disclosing_party`, `receiving_party`, `effective_date`, `purpose` |
| `invoice` | `invoice_number`, `issue_date`, `due_date`, `seller_name`, `buyer_name`, `items`, `total_amount` |
| `quotation` | `quote_number`, `quote_date`, `valid_until`, `seller_name`, `client_name`, `items`, `total_amount` |
| `service_agreement` | `client_name`, `service_provider`, `service_description`, `start_date`, `fee_amount` |
| `business_report` | `report_title`, `prepared_by`, `organization`, `report_date`, `executive_summary` |
| `certificate` | `recipient_name`, `certificate_title`, `course_or_achievement`, `issuer_name`, `issue_date` |

---

## 🏗️ Architecture

```
docugen/
├── core/            # IR, schemas, exceptions, config, registry, models
├── input/           # Adapters (dict/JSON/Pydantic/dataclass) + normalizer
├── validation/      # Required fields, type rules, cross-field consistency
├── templates/       # Template registry, Jinja2 sandbox, DOCX parser
├── generation/      # Clause engine, document composers, pipeline generator
├── rendering/       # PDF (ReportLab) + DOCX (python-docx) renderers
├── classification/  # Rule-based + ML classifier, hybrid resolver
├── nlp/             # Entity extractor, NLP pipeline (optional spaCy)
├── plugins/         # Plugin interfaces and registry
├── api/             # Public Python API
└── cli/             # Command-line interface
```

See [docs/architecture.md](docs/architecture.md) for detailed design documentation.

---

## 🧪 Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test groups
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/rendering/ -v
pytest tests/classification/ -v
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes with tests
4. Run: `pytest tests/ -v && ruff check src/`
5. Submit a pull request

---

## 📝 License

Apache License 2.0 — see [LICENSE](LICENSE).

---

## 🔒 Security

Please review [SECURITY.md](SECURITY.md) for our responsible disclosure policy.
