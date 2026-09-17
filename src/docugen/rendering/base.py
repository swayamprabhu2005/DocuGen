"""Base renderer interface for DocuGen AI."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from docugen.core.document_ir import Document
from docugen.core.models import RenderResult


@runtime_checkable
class Renderer(Protocol):
    """Protocol defining the interface for document renderers."""

    def render(self, document: Document, destination: Path) -> RenderResult:
        """Render the Document IR into the target destination file."""
        ...
