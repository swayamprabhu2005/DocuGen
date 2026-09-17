"""Templates package for DocuGen AI."""

import docugen.templates.builtins
from docugen.templates.loader import SafeTemplateLoader, get_safe_loader
from docugen.templates.registry import (
    TemplateDefinition,
    TemplateRegistry,
    get_template_registry,
    list_templates,
    register_template,
)

__all__ = [
    "TemplateDefinition",
    "TemplateRegistry",
    "get_template_registry",
    "list_templates",
    "register_template",
    "SafeTemplateLoader",
    "get_safe_loader",
]
