"""Version and generation metadata for DocuGen AI."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

__version__ = "0.1.0"
__package_name__ = "docugen-ai"
__import_name__ = "docugen"


class GenerationMetadata(BaseModel):
    """Metadata recorded on every generated document."""

    docugen_version: str = Field(default=__version__, description="DocuGen AI library version")
    document_type: str = Field(..., description="Document type identifier")
    template_name: Optional[str] = Field(default=None, description="Template name or path used")
    template_version: Optional[str] = Field(default="1.0.0", description="Version of the template")
    schema_version: Optional[str] = Field(default="1.0.0", description="Version of the schema")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of document generation",
    )
    generator: str = Field(default="DocuGen AI Local-First Engine", description="Generator signature")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary custom metadata")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
