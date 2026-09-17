"""Plugins package for DocuGen AI."""

from docugen.plugins.interfaces import DocuGenPlugin
from docugen.plugins.registry import (
    list_plugins,
    register_document_type,
    register_plugin,
)

__all__ = [
    "DocuGenPlugin",
    "register_plugin",
    "list_plugins",
    "register_document_type",
]
