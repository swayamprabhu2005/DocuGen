# DocuGen AI — Architecture

## Overview

DocuGen AI is structured as a **layered pipeline** where data flows from raw input to rendered output document:

```
Raw Input (dict / JSON / Pydantic / dataclass)
    ↓  [Input Layer]        adapt_input() → normalize_input()
    ↓  [Classification]     classify_document() → document_type
    ↓  [Schema Resolution]  get_schema(document_type)
    ↓  [Validation]         validate_data() → ValidationResult
    ↓  [Composition]        compose_document() → Document IR
    ↓  [Rendering]          render() → PDF / DOCX file
```

---

## Module Map

```
src/docugen/
├── __init__.py              Top-level package: re-exports public API
├── versioning/
│   └── metadata.py          GenerationMetadata, version constants
├── core/
│   ├── exceptions.py        Exception hierarchy
│   ├── configuration.py     DocuGenConfig (Pydantic), global config
│   ├── document_ir.py       Document IR: all node types (see below)
│   ├── schemas.py           FieldDefinition, DocumentSchema, CrossFieldRule
│   ├── models.py            ValidationResult, ClassificationResult, GenerationResult
│   └── schema_registry.py   Global schema registry + 7 built-in schemas
├── input/
│   ├── adapters.py          adapt_input(): dict/JSON/Pydantic/dataclass → dict
│   └── normalizer.py        normalize_input(): type coercion, alias resolution, defaults
├── validation/
│   ├── required_fields.py   check_required_fields()
│   ├── rules.py             check_field_rules(): type/min/max/enum/regex
│   ├── consistency.py       Cross-field rules: date ordering, arithmetic, distinctness
│   └── validator.py         validate_data() orchestrator + custom validator registry
├── templates/
│   ├── registry.py          TemplateRegistry, TemplateDefinition
│   ├── loader.py            SafeTemplateLoader (Jinja2 SandboxedEnvironment)
│   ├── builtins.py          Built-in template registrations
│   └── docx_parser.py       DOCX template file → Document IR
├── generation/
│   ├── clause_engine.py     ClauseEngine, ClauseDefinition, built-in clauses
│   ├── composer.py          compose_document() dispatcher + 7 built-in composers
│   └── generator.py         DocumentGenerator: 8-step pipeline
├── rendering/
│   ├── base.py              Renderer Protocol
│   ├── formatting.py        DocumentFormatting
│   ├── pdf.py               PdfRenderer (ReportLab Platypus)
│   └── docx.py              DocxRenderer (python-docx)
├── classification/
│   ├── rules.py             rule_based_classify() — field-signature scoring
│   ├── ml.py                MLDocumentClassifier (TF-IDF + NaiveBayes, optional)
│   └── resolver.py          classify_document() — hybrid resolver
├── nlp/
│   ├── extractor.py         EntityExtractor (regex + optional spaCy NER)
│   └── pipeline.py          NLPPipeline
├── plugins/
│   ├── interfaces.py        DocuGenPlugin Protocol
│   └── registry.py          register_plugin(), register_document_type()
├── api/
│   └── public.py            All public API functions
└── cli/
    └── main.py              CLI entry point (argparse)
```

---

## Document IR (Intermediate Representation)

The IR is the central data model that decouples composition from rendering.

```python
Document
  ├── metadata: DocumentMetadata
  ├── header: Optional[Header]
  ├── footer: Optional[Footer]
  ├── watermark: Optional[Watermark]
  └── sections: List[Section]
        └── Section
              ├── title: Optional[str]
              └── elements: List[BlockElement]
                    ├── Heading (level 1–6)
                    ├── Paragraph (runs of TextRun)
                    ├── ListBlock (ordered/unordered, ListItem[])
                    ├── Table (has_header, col_widths, TableRow[])
                    ├── SignatureBlock (Signer[], layout)
                    ├── ClauseIR (clause_id, title, body elements)
                    ├── Image (path, alt_text, width)
                    └── PageBreak
```

### Key Design Decisions

- **Separation of concerns**: Composition logic produces IR; renderers consume IR. Adding a new output format (e.g., HTML) only requires implementing the `Renderer` protocol.
- **`from __future__ import annotations`**: Used throughout to allow forward references in type hints (needed for circular-safe `BlockElement` union).
- **`TYPE_CHECKING` guard**: `composer.py` imports `TemplateDefinition` only during type checking to avoid circular imports with `templates/builtins.py`.

---

## Classification Pipeline

```
classify_document(data, explicit_type=None)
    ├── If explicit_type → return ClassificationResult(method="explicit", confidence=1.0)
    ├── schema_match: score each registered schema against input field names
    ├── If best_score ≥ 0.7 → return (method="schema_match")
    ├── rule_based: field-signature scoring (weighted by distinctive fields)
    ├── If score ≥ 0.5 → return (method="rule_based")
    ├── ml: TF-IDF + NaiveBayes (if sklearn installed)
    ├── If ml_confidence ≥ 0.6 → return (method="ml")
    └── Else → ClassificationResult(ambiguous=True, candidates=[…])
```

---

## Validation Pipeline

```
validate_data(data, schema, strict=True)
    ├── check_required_fields()      → missing/empty field errors
    ├── check_field_rules()          → type/min/max/enum/regex errors
    ├── check_schema_cross_field_rules()
    │     ├── date_order rules
    │     ├── table_sum rules
    │     └── party_match rules
    └── call custom validators registered for document_type
```

---

## Plugin System

`register_document_type()` atomically registers:
1. `DocumentSchema` → `schema_registry._SCHEMAS`
2. `TemplateDefinition` → `TemplateRegistry._templates`  
3. `ClauseDefinition[]` → `ClauseEngine._clauses`
4. Validator functions → `validation.validator._CUSTOM_VALIDATORS`

This ensures all subsystems are consistent after registration.

---

## Rendering Architecture

Both renderers implement the `Renderer` protocol:

```python
class Renderer(Protocol):
    def render(self, document: Document, output_path: Path) -> RenderResult: ...
```

### PdfRenderer (ReportLab)
- Uses Platypus `SimpleDocTemplate` with custom page templates
- `NumberedCanvas`: two-pass rendering for "Page N of M" in footers
- Diagonal watermarks drawn in `on_page` callback
- Table cells use `ParagraphStyle` for text wrapping

### DocxRenderer (python-docx)
- Adds `core_properties` metadata
- Signature blocks rendered as side-by-side or stacked tables
- Custom styles applied for headings, body text, captions
