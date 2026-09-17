"""Core document generator pipeline orchestrator."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from docugen.classification.resolver import classify_document
from docugen.core.configuration import DocuGenConfig, get_default_config
from docugen.core.document_ir import Document
from docugen.core.exceptions import (
    DocuGenError,
    RenderingError,
    TemplateNotFoundError,
    ValidationError,
)
from docugen.core.models import GenerationResult, RenderResult
from docugen.core.schema_registry import get_schema
from docugen.generation.composer import compose_document
from docugen.input.adapters import adapt_input
from docugen.input.normalizer import normalize_input
from docugen.rendering.docx import DocxRenderer
from docugen.rendering.pdf import PdfRenderer
from docugen.templates.registry import TemplateDefinition, get_template_registry
from docugen.validation.validator import validate_data
from docugen.versioning.metadata import GenerationMetadata

logger = logging.getLogger("docugen.generator")


def generate(
    data: Any,
    template: Optional[Union[str, Path]] = None,
    document_type: Optional[str] = None,
    output: str = "pdf",
    output_path: Optional[Union[str, Path]] = None,
    config: Optional[DocuGenConfig] = None,
    strict: Optional[bool] = None,
    dry_run: bool = False,
) -> GenerationResult:
    """Execute end-to-end document generation pipeline.

    Pipeline Steps:
        1. Adapt raw input data (dict, JSON, file, model, dataclass).
        2. Resolve document type and template (or classify if unspecified).
        3. Resolve schema.
        4. Normalize input data according to schema rules and types.
        5. Validate data (strict or lenient).
        6. Compose Document IR (applying clauses, tables, metadata).
        7. If dry_run=True, return GenerationResult with Document IR.
        8. Render Document IR to requested format (PDF or DOCX).
        9. Save to output path and return structured GenerationResult.

    Args:
        data: Input data source.
        template: Template name or filesystem path.
        document_type: Explicit document type identifier.
        output: Output format ('pdf' or 'docx').
        output_path: Destination file path.
        config: Optional custom configuration object.
        strict: Override strict validation setting.
        dry_run: If True, stop before rendering and return IR.

    Returns:
        GenerationResult: Comprehensive execution result.
    """
    cfg = config or get_default_config()
    is_strict = cfg.strict_validation if strict is None else strict

    # Step 1: Input Adaptation
    raw_dict = adapt_input(data)

    # Step 2: Document Type and Template Resolution
    template_reg = get_template_registry()
    resolved_template: Optional[TemplateDefinition] = None
    resolved_doc_type: Optional[str] = None

    if template is not None:
        resolved_template = template_reg.resolve(template)
        resolved_doc_type = resolved_template.document_type
    elif document_type is not None:
        resolved_doc_type = document_type.strip().lower()
        # Find matching template or fallback
        resolved_template = template_reg.get(resolved_doc_type)
        if not resolved_template:
            resolved_template = TemplateDefinition(
                name=resolved_doc_type,
                document_type=resolved_doc_type,
            )
    else:
        # Hybrid classification
        class_res = classify_document(raw_dict)
        if class_res.ambiguous or not class_res.document_type:
            return GenerationResult(
                success=False,
                document_type="unknown",
                error=f"Document type could not be resolved automatically. Candidates: {class_res.candidates}",
            )
        resolved_doc_type = class_res.document_type
        resolved_template = template_reg.get(resolved_doc_type)
        if not resolved_template:
            resolved_template = TemplateDefinition(
                name=resolved_doc_type,
                document_type=resolved_doc_type,
            )

    # Step 3: Schema Resolution
    schema = None
    try:
        schema = get_schema(resolved_doc_type)
    except Exception as exc:
        logger.warning("No schema found for '%s': %s", resolved_doc_type, exc)

    # Step 4: Normalization
    normalized_data = normalize_input(raw_dict, schema=schema)

    # Step 5: Validation
    if schema is not None:
        val_result = validate_data(normalized_data, schema, strict=is_strict)
    else:
        from docugen.core.models import ValidationResult
        val_result = ValidationResult(valid=True)

    # Step 6: Composition into Document IR
    doc_ir = compose_document(normalized_data, resolved_template)

    # Record generation metadata
    gen_meta = GenerationMetadata(
        document_type=resolved_doc_type,
        template_name=resolved_template.name,
        template_version=resolved_template.version,
        schema_version=schema.version if schema else "1.0.0",
    )
    doc_ir.metadata.custom["docugen_metadata"] = gen_meta.to_dict()

    # Apply default watermark if configured
    if cfg.default_watermark and not doc_ir.watermark:
        from docugen.core.document_ir import Watermark
        doc_ir.watermark = Watermark(text=cfg.default_watermark)

    warnings = [w.message for w in val_result.warnings]

    # Dry run check
    if dry_run:
        return GenerationResult(
            success=True,
            document_type=resolved_doc_type,
            output_format=output.lower(),
            validation=val_result,
            warnings=warnings,
            metadata=gen_meta.to_dict(),
            document_ir=doc_ir,
        )

    # Step 7: Resolve Output Destination
    fmt = output.lower().strip()
    if output_path is not None:
        dest_path = Path(output_path)
    else:
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{resolved_doc_type}_{resolved_template.name}.{fmt}"
        dest_path = cfg.output_dir / filename

    if dest_path.exists() and not cfg.overwrite_existing and output_path is None:
        # Create unique filename if not overwriting
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = dest_path.with_name(f"{dest_path.stem}_{ts}.{fmt}")

    # Ensure parent dir exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 8: Rendering
    render_res: RenderResult
    if fmt == "pdf":
        renderer = PdfRenderer()
        render_res = renderer.render(doc_ir, dest_path)
    elif fmt == "docx":
        renderer = DocxRenderer()
        render_res = renderer.render(doc_ir, dest_path)
    else:
        raise RenderingError(f"Unsupported output format '{output}'. Supported: ['pdf', 'docx']")

    return GenerationResult(
        success=render_res.success,
        document_type=resolved_doc_type,
        output_path=str(dest_path.resolve()) if render_res.success else None,
        output_format=fmt,
        validation=val_result,
        warnings=warnings,
        metadata=gen_meta.to_dict(),
        document_ir=doc_ir,
        render_result=render_res,
        error=render_res.error,
    )
