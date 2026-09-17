# Changelog

All notable changes to DocuGen AI are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] – 2026-09-18

### Added

#### Core
- Complete Document Intermediate Representation (IR) with `Document`, `Section`, `Paragraph`, `TextRun`, `Heading`, `ListBlock`, `Table`, `SignatureBlock`, `ClauseIR`, `Header`, `Footer`, `Watermark`, `PageBreak`
- `DocumentSchema` with `FieldDefinition`, `CrossFieldRule`, and `export_json_schema()`
- `DocuGenConfig` (Pydantic-based) with global config helpers `get_default_config()` / `set_default_config()`
- Full exception hierarchy: `DocuGenError`, `SchemaError`, `ValidationError`, `TemplateError`, `RenderingError`, `ClassificationError`, `PluginError`, `ClauseError`, `AdapterError`

#### Built-in Document Types (7)
- `employment_contract` — Full employment contract with appointment, compensation, probation, remote work, non-compete, and termination clauses
- `nda` — Non-Disclosure Agreement with confidentiality, term, injunctive relief, and governing law clauses
- `invoice` — Professional invoice with itemized table, tax calculation, and payment terms
- `quotation` — Sales quotation with validity date and line items
- `service_agreement` — Service-level agreement with scope, deliverables, and fees
- `business_report` — Executive business report with findings and recommendations
- `certificate` — Certificate of completion/achievement

#### Rendering
- **PDF** via ReportLab Platypus: headers, footers, diagonal watermarks, two-pass "Page X of Y" numbering
- **DOCX** via python-docx: structured headings, tables, signatures, headers, footers, document metadata

#### Input Handling
- `adapt_input()`: accepts `dict`, JSON string, JSON file `Path`, Pydantic model (v1 and v2), dataclass
- `normalize_input()`: type coercion, date normalization, alias resolution, schema default injection

#### Validation Engine
- Required field detection (missing, empty, empty-list)
- Field-level rules: type, minimum, maximum, enum, regex pattern
- Cross-field consistency: date ordering, party distinctness, invoice arithmetic
- Custom validator registration via `register_validator()`

#### Classification
- Rule-based classifier using field-signature scoring
- Hybrid resolver: explicit → schema_match → rule_based → ML (optional) → ambiguous
- Optional ML classifier (TF-IDF + Naive Bayes, requires `[ml]` extra)

#### Template & Clause Engine
- Jinja2 `SandboxedEnvironment` for safe template rendering
- `ClauseEngine` with conditional clause resolution, dependency ordering, and priority
- Template registry supporting built-in, filesystem, and plugin templates
- DOCX template file parsing via `parse_and_merge_docx_template()`

#### Plugin System
- `register_document_type()` for atomic registration of schema + template + clauses + validators
- `DocuGenPlugin` Protocol for structured plugin packages

#### NLP (Optional)
- `EntityExtractor` with regex key-value patterns and optional spaCy NER
- `NLPPipeline` orchestrator (requires `[nlp]` extra)

#### CLI
- `docugen generate` — Generate a document from a JSON data file
- `docugen validate` — Validate data against a document schema
- `docugen templates list` — List all registered templates
- `docugen schemas list` — List all registered schemas
- `docugen schemas show <type>` — Display schema field definitions
- `docugen document-types list` — List all registered document types

#### Testing
- 40+ unit, validation, integration, rendering, and classification tests
- Conftest fixtures for all 7 built-in document types

---

## [Unreleased]

### Planned
- HTML renderer
- Markdown renderer
- Excel (XLSX) renderer for spreadsheet documents
- Asynchronous generation API
- PDF digital signatures
- Template marketplace / community registry
- Multi-language clause libraries
