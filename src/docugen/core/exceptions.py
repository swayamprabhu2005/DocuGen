"""Custom exception hierarchy for DocuGen AI."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class DocuGenError(Exception):
    """Base exception for all DocuGen AI operations."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SchemaError(DocuGenError):
    """Raised when schema validation or resolution fails."""

    pass


class ValidationError(DocuGenError):
    """Raised when document data fails validation rules in strict mode."""

    def __init__(
        self,
        message: str,
        diagnostics: Optional[List[Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.diagnostics = diagnostics or []


class TemplateError(DocuGenError):
    """Raised when a template cannot be found, loaded, or rendered."""

    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a requested template does not exist."""

    pass


class RenderingError(DocuGenError):
    """Raised when document rendering (PDF/DOCX) fails."""

    pass


class ConfigurationError(DocuGenError):
    """Raised when invalid library configuration is provided."""

    pass


class ClassificationError(DocuGenError):
    """Raised when document type classification fails or is ambiguous."""

    pass


class AmbiguousDocumentTypeError(ClassificationError):
    """Raised when multiple candidate document types match with equal confidence."""

    def __init__(
        self,
        message: str,
        candidates: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, details)
        self.candidates = candidates or []


class PluginError(DocuGenError):
    """Raised when a plugin fails registration or execution."""

    pass


class ClauseError(DocuGenError):
    """Raised when clause resolution, dependency check, or evaluation fails."""

    pass


class AdapterError(DocuGenError):
    """Raised when an input adapter cannot parse the source data."""

    pass
