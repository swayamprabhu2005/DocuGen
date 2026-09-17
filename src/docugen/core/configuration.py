"""Configuration management for DocuGen AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocuGenConfig(BaseModel):
    """Configuration settings for DocuGen generation and validation."""

    template_dirs: List[Path] = Field(
        default_factory=list,
        description="Custom directory paths to search for templates before built-ins",
    )
    output_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "output",
        description="Default directory for generated documents",
    )
    default_format: str = Field(
        default="pdf",
        description="Default output format ('pdf' or 'docx')",
    )
    strict_validation: bool = Field(
        default=True,
        description="If True, missing required fields or validation errors abort generation",
    )
    overwrite_existing: bool = Field(
        default=False,
        description="If True, existing output files are overwritten silently",
    )
    default_font_family: str = Field(
        default="Helvetica",
        description="Default font family for documents",
    )
    default_font_size: float = Field(
        default=10.5,
        description="Default body font size in points",
    )
    default_watermark: Optional[str] = Field(
        default=None,
        description="Optional global watermark (e.g. 'CONFIDENTIAL', 'DRAFT')",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level for docugen logger",
    )

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocuGenConfig":
        """Instantiate configuration from a dictionary."""
        cleaned = dict(data)
        if "template_dirs" in cleaned:
            cleaned["template_dirs"] = [Path(p) for p in cleaned["template_dirs"]]
        if "output_dir" in cleaned:
            cleaned["output_dir"] = Path(cleaned["output_dir"])
        return cls(**cleaned)


_DEFAULT_CONFIG: Optional[DocuGenConfig] = None


def get_default_config() -> DocuGenConfig:
    """Get the active global default configuration."""
    global _DEFAULT_CONFIG
    if _DEFAULT_CONFIG is None:
        _DEFAULT_CONFIG = DocuGenConfig()
    return _DEFAULT_CONFIG


def set_default_config(config: DocuGenConfig) -> None:
    """Set the active global default configuration."""
    global _DEFAULT_CONFIG
    _DEFAULT_CONFIG = config
