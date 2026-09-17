# DocuGen AI — Developer Guide

## Project Setup

```bash
git clone https://github.com/your-org/docugen-ai.git
cd docugen-ai
pip install -e ".[dev]"
```

The project uses a `src/` layout — all library code is in `src/docugen/`.

---

## Running Tests

```bash
# All tests
pytest tests/ -v --tb=short

# Specific groups
pytest tests/unit/ -v               # Unit tests only
pytest tests/validation/ -v         # Validation engine tests
pytest tests/integration/ -v        # Full pipeline integration tests
pytest tests/rendering/ -v          # PDF + DOCX rendering tests
pytest tests/classification/ -v     # Classification tests

# With coverage
pytest tests/ --cov=src/docugen --cov-report=html
open htmlcov/index.html             # Linux/Mac
start htmlcov/index.html            # Windows
```

---

## Adding a New Built-in Document Type

Follow these 4 steps to add a new document type (e.g., `partnership_deed`):

### Step 1: Define the Schema (`core/schema_registry.py`)

In `_init_builtin_schemas()`, add a call to `register_schema()`:

```python
register_schema(DocumentSchema(
    document_type="partnership_deed",
    title="Partnership Deed",
    category="legal",
    fields={
        "partner_a": FieldDefinition(name="partner_a", type=FieldType.STRING, required=True),
        "partner_b": FieldDefinition(name="partner_b", type=FieldType.STRING, required=True),
        "profit_share": FieldDefinition(name="profit_share", type=FieldType.NUMBER, required=True),
    },
))
```

### Step 2: Write the Composer (`generation/composer.py`)

Add a new function and register it in the `_COMPOSERS` dict:

```python
def compose_partnership_deed(data: Dict[str, Any], template: "TemplateDefinition") -> Document:
    return Document(
        metadata=DocumentMetadata(title="Partnership Deed", document_type="partnership_deed"),
        sections=[
            Section(
                title="PARTNERSHIP DEED",
                elements=[
                    Paragraph.from_text(f"Between {data.get('partner_a')} and {data.get('partner_b')}."),
                ],
            )
        ],
    )

_COMPOSERS["partnership_deed"] = compose_partnership_deed
```

### Step 3: Add Clauses (`generation/clause_engine.py`)

In `_BUILTIN_CLAUSES`, add entries for your document type:

```python
ClauseDefinition(
    clause_id="profit_distribution",
    title="3.0 Profit Distribution",
    document_types=["partnership_deed"],
    priority=30,
    required=True,
    template_text="Profits shall be distributed at {{ profit_share }}% / {{ 100 - profit_share }}%.",
),
```

### Step 4: Register in Builtins (`templates/builtins.py`)

```python
get_template_registry().register(TemplateDefinition(
    name="partnership_deed",
    document_type="partnership_deed",
    description="Partnership deed template",
    composer_fn=compose_partnership_deed,
))
```

---

## Adding a Custom Validator

```python
from docugen.core.models import ValidationResult
from docugen.validation.validator import register_validator

def validate_expiry_date(data, schema):
    result = ValidationResult(valid=True)
    if data.get("expiry_date") and data.get("effective_date"):
        if data["expiry_date"] <= data["effective_date"]:
            result.add_error(
                code="EXPIRY_BEFORE_EFFECTIVE",
                field="expiry_date",
                message="Expiry date must be after effective date.",
            )
    return result

register_validator("nda", validate_expiry_date)
```

---

## Implementing a New Renderer

Implement the `Renderer` protocol:

```python
from pathlib import Path
from docugen.core.document_ir import Document
from docugen.core.models import RenderResult

class HtmlRenderer:
    def render(self, document: Document, output_path: Path) -> RenderResult:
        html_lines = [f"<html><body><h1>{document.metadata.title}</h1>"]
        for section in document.sections:
            html_lines.append(f"<h2>{section.title}</h2>")
            # ... render elements ...
        html_lines.append("</body></html>")
        output_path.write_text("\n".join(html_lines), encoding="utf-8")
        return RenderResult(
            success=True,
            format="html",
            output_path=output_path,
            file_size_bytes=output_path.stat().st_size,
        )
```

Then register it in `generation/generator.py`'s `_RENDERER_MAP`.

---

## Pydantic v2 Deprecation Notes

Some models use the older `class Config` syntax. Migrate to `model_config = ConfigDict(...)` in a future refactor:

```python
# Old (generates deprecation warning)
class MyModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

# New (Pydantic v2)
from pydantic import ConfigDict
class MyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
```

---

## Directory Structure Reference

```
d:\MyFiles\DocuGen\
├── .github/
│   └── workflows/
│       └── ci.yml              GitHub Actions CI (test/lint/build on 3 OSes × 3 Python versions)
├── docs/
│   ├── architecture.md         System design & module map
│   └── developer_guide.md      This file
├── examples/
│   ├── employment_contract/run.py
│   ├── nda/run.py
│   ├── invoice/run.py
│   └── custom_document_type/run.py
├── src/
│   └── docugen/               Source code (see architecture.md)
├── tests/
│   ├── conftest.py            Shared pytest fixtures
│   ├── unit/                  Unit tests (adapters, normalizer, IR, schemas, clause engine)
│   ├── validation/            Validation engine tests
│   ├── integration/           Full pipeline + CLI + plugin tests
│   ├── rendering/             PDF + DOCX renderer tests
│   └── classification/        Classification tests
├── pyproject.toml             Package config, dependencies, extras, pytest config
├── README.md
├── LICENSE                    Apache 2.0
├── CONTRIBUTING.md
├── SECURITY.md
└── CHANGELOG.md
```
