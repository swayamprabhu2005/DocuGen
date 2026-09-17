"""Core data models for validation, classification, rendering, and generation results."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from docugen.core.document_ir import Document


class Diagnostic(BaseModel):
    """Structured diagnostic reporting validation errors, warnings, or inconsistencies."""

    code: str = Field(..., description="Machine-readable error/warning code")
    severity: Literal["error", "warning", "info"] = Field(default="error", description="Diagnostic severity level")
    field: Optional[str] = Field(default=None, description="Field associated with the diagnostic")
    message: str = Field(..., description="Human-readable diagnostic message")
    context: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic context metadata")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ValidationResult(BaseModel):
    """Structured result of schema validation and consistency checking."""

    valid: bool = Field(default=True, description="True if no blocking error diagnostics occurred")
    errors: List[Diagnostic] = Field(default_factory=list, description="List of error diagnostics")
    warnings: List[Diagnostic] = Field(default_factory=list, description="List of warning diagnostics")
    missing_fields: List[str] = Field(
        default_factory=list, description="List of required field names that were missing"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_error(
        self, code: str, message: str, field: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> None:
        self.valid = False
        self.errors.append(Diagnostic(code=code, severity="error", field=field, message=message, context=context or {}))

    def add_warning(
        self, code: str, message: str, field: Optional[str] = None, context: Optional[Dict[str, Any]] = None
    ) -> None:
        self.warnings.append(
            Diagnostic(code=code, severity="warning", field=field, message=message, context=context or {})
        )

    def add_missing_field(self, field_name: str, message: Optional[str] = None) -> None:
        self.valid = False
        if field_name not in self.missing_fields:
            self.missing_fields.append(field_name)
        msg = message or f"Missing required field: '{field_name}'"
        self.errors.append(Diagnostic(code="MISSING_REQUIRED_FIELD", severity="error", field=field_name, message=msg))


class ClassificationResult(BaseModel):
    """Result of document type classification."""

    document_type: Optional[str] = Field(default=None, description="Resolved document type")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score [0.0, 1.0]")
    method: str = Field(
        default="explicit",
        description="Classification method used ('explicit', 'schema_match', 'rule_based', 'ml', 'ambiguous')",
    )
    ambiguous: bool = Field(default=False, description="True if classification could not decisively resolve")
    candidates: List[Dict[str, Any]] = Field(default_factory=list, description="Ranked candidate matches")


class RenderResult(BaseModel):
    """Structured result of rendering Document IR to a physical format."""

    success: bool = True
    output_path: Optional[str] = None
    format: str = "pdf"
    file_size_bytes: int = 0
    page_count: Optional[int] = None
    error: Optional[str] = None


class GenerationResult(BaseModel):
    """Final structured result of document generation."""

    success: bool = True
    document_type: str
    output_path: Optional[str] = None
    output_format: str = "pdf"
    validation: ValidationResult = Field(default_factory=ValidationResult)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    document_ir: Optional[Document] = None
    render_result: Optional[RenderResult] = None
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
