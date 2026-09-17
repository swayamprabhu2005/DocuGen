"""Versioning and metadata package."""

from docugen.versioning.metadata import (
    GenerationMetadata,
    __import_name__,
    __package_name__,
    __version__,
)

__all__ = [
    "GenerationMetadata",
    "__version__",
    "__package_name__",
    "__import_name__",
]
