"""Template registry for DocuGen AI."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from docugen.core.document_ir import Document
from docugen.core.exceptions import TemplateError, TemplateNotFoundError


# Composer function signature: receives (data, template_meta) and returns Document IR
ComposerFn = Callable[[Dict[str, Any], "TemplateDefinition"], Document]


class TemplateDefinition(BaseModel):
    """Metadata and definition of a registered template."""

    name: str
    document_type: str
    version: str = "1.0.0"
    description: Optional[str] = None
    file_path: Optional[str] = None
    is_builtin: bool = False
    composer: Optional[ComposerFn] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True


class TemplateRegistry:
    """Registry managing available document templates."""

    def __init__(self) -> None:
        self._templates: Dict[str, TemplateDefinition] = {}

    def register(self, template: TemplateDefinition) -> None:
        """Register a template definition."""
        self._templates[template.name.strip().lower()] = template

    def get(self, name: str) -> Optional[TemplateDefinition]:
        """Look up a template definition by name."""
        return self._templates.get(name.strip().lower())

    def list_templates(self) -> List[str]:
        """Return a sorted list of registered template names."""
        return sorted(list(self._templates.keys()))

    def resolve(self, template_identifier: Union[str, Path]) -> TemplateDefinition:
        """Resolve a template name, filesystem path, or alias.

        Raises:
            TemplateNotFoundError: If template cannot be located.
        """
        # If it's a Path or a string pointing to an existing file
        if isinstance(template_identifier, Path) or (
            isinstance(template_identifier, str) and Path(template_identifier).exists()
        ):
            path_obj = Path(template_identifier)
            stem = path_obj.stem
            # Create dynamic template definition for filesystem template
            return TemplateDefinition(
                name=stem,
                document_type=stem,
                file_path=str(path_obj.resolve()),
                is_builtin=False,
                description=f"User filesystem template loaded from {path_obj.name}",
            )

        name_str = str(template_identifier).strip().lower()
        if name_str in self._templates:
            return self._templates[name_str]

        raise TemplateNotFoundError(
            f"Template '{template_identifier}' not found in registry. "
            f"Available templates: {self.list_templates()}"
        )


_GLOBAL_TEMPLATE_REGISTRY = TemplateRegistry()


def get_template_registry() -> TemplateRegistry:
    return _GLOBAL_TEMPLATE_REGISTRY


def list_templates() -> List[str]:
    """Public helper to list all registered templates."""
    return _GLOBAL_TEMPLATE_REGISTRY.list_templates()


def register_template(
    name: str,
    document_type: str,
    composer: Optional[ComposerFn] = None,
    file_path: Optional[str] = None,
    description: Optional[str] = None,
    version: str = "1.0.0",
) -> None:
    """Public API to register a custom template."""
    _GLOBAL_TEMPLATE_REGISTRY.register(
        TemplateDefinition(
            name=name,
            document_type=document_type,
            composer=composer,
            file_path=file_path,
            description=description,
            version=version,
            is_builtin=False,
        )
    )
