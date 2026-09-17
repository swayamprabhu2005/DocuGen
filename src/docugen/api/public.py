"""Public API functions for DocuGen AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from docugen.classification.resolver import classify_document
from docugen.core.configuration import DocuGenConfig, get_default_config, set_default_config
from docugen.core.document_ir import Document
from docugen.core.exceptions import (
    DocuGenError,
    RenderingError,
    SchemaError,
    TemplateError,
    TemplateNotFoundError,
    ValidationError,
)
from docugen.core.models import (
    ClassificationResult,
    Diagnostic,
    GenerationResult,
    RenderResult,
    ValidationResult,
)
from docugen.core.schema_registry import get_schema, list_document_types
from docugen.core.schemas import DocumentSchema
from docugen.generation.clause_engine import ClauseDefinition, get_clause_engine
from docugen.generation.generator import generate
from docugen.input.adapters import adapt_input
from docugen.input.normalizer import normalize_input
from docugen.plugins.registry import register_document_type
from docugen.templates.registry import TemplateDefinition, get_template_registry, list_templates, register_template
from docugen.validation.validator import register_validator, validate_data


def generate_document(
    data: Any,
    template: Optional[Union[str, Path]] = None,
    document_type: Optional[str] = None,
    output: str = "pdf",
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[DocuGenConfig] = None,
    strict: Optional[bool] = None,
    dry_run: bool = False,
) -> GenerationResult:
    """Generate a document from input data into DOCX or PDF.

    Args:
        data: Python dictionary, JSON string, JSON file path, Pydantic model, or dataclass.
        template: Built-in template name (e.g. 'employment_contract') or path to custom template.
        document_type: Explicit document type name if not determined from template.
        output: Target format, either 'pdf' or 'docx'. Defaults to 'pdf'.
        output_path: Optional explicit output file destination.
        config: Optional custom DocuGenConfig.
        strict: If True, validation errors raise ValidationError.
        dry_run: If True, builds Document IR and validates without rendering file.

    Returns:
        GenerationResult: Object detailing status, output path, validation results, and metadata.
    """
    return generate(
        data=data,
        template=template,
        document_type=document_type,
        output=output,
        output_path=output_path,
        config=config,
        strict=strict,
        dry_run=dry_run,
    )


def validate_document_data(
    data: Any,
    document_type: Optional[str] = None,
    template: Optional[str] = None,
    strict: bool = False,
) -> ValidationResult:
    """Validate document data against the matching schema without generating output.

    Args:
        data: Raw input data (dict, JSON, etc.).
        document_type: Target document type name.
        template: Template name (used if document_type is not provided).
        strict: If True, raises ValidationError on failure.

    Returns:
        ValidationResult: Detailed validation diagnostics and missing fields.
    """
    raw_dict = adapt_input(data)

    target_type = document_type
    if not target_type and template:
        try:
            tmpl_def = get_template_registry().resolve(template)
            target_type = tmpl_def.document_type
        except Exception:
            target_type = template

    if not target_type:
        class_res = classify_document(raw_dict)
        target_type = class_res.document_type
        if not target_type:
            res = ValidationResult(valid=False)
            res.add_error("UNKNOWN_DOCUMENT_TYPE", "Unable to determine document type for validation.")
            return res

    schema = get_schema(target_type)
    normalized = normalize_input(raw_dict, schema=schema)
    return validate_data(normalized, schema, strict=strict)


def preview_document(
    data: Any,
    template: Optional[Union[str, Path]] = None,
    document_type: Optional[str] = None,
) -> Document:
    """Dry-run generation and return the structured Document Intermediate Representation (IR).

    Args:
        data: Input document data.
        template: Template name or path.
        document_type: Document type name.

    Returns:
        Document: Root Document IR object.
    """
    res = generate_document(
        data=data,
        template=template,
        document_type=document_type,
        dry_run=True,
    )
    if not res.document_ir:
        raise DocuGenError(f"Preview generation failed: {res.error}")
    return res.document_ir


def generate_clause(clause_id: str, data: Any) -> str:
    """Render a specific reusable clause with input data.

    Args:
        clause_id: Unique clause identifier.
        data: Input data context dictionary.

    Returns:
        str: Rendered clause text.
    """
    raw_dict = adapt_input(data)
    normalized = normalize_input(raw_dict)
    return get_clause_engine().render_clause_text(clause_id, normalized)


__all__ = [
    "generate_document",
    "validate_document_data",
    "classify_document",
    "generate_clause",
    "preview_document",
    "register_template",
    "register_document_type",
    "register_validator",
    "get_schema",
    "list_templates",
    "list_document_types",
    "DocuGenConfig",
    "get_default_config",
    "set_default_config",
    "GenerationResult",
    "ValidationResult",
    "ClassificationResult",
    "RenderResult",
    "Diagnostic",
    "DocuGenError",
    "ValidationError",
    "SchemaError",
    "TemplateError",
    "TemplateNotFoundError",
    "RenderingError",
]
