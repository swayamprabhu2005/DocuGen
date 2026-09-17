"""Plugin protocols and interface specifications for DocuGen AI."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable
from docugen.core.document_ir import Document
from docugen.core.schemas import DocumentSchema
from docugen.generation.clause_engine import ClauseDefinition
from docugen.templates.registry import TemplateDefinition


@runtime_checkable
class DocuGenPlugin(Protocol):
    """Protocol for external DocuGen extension plugins."""

    name: str
    version: str

    def initialize(self) -> None:
        """Called when plugin is registered to install its components."""
        ...
