"""Plugin registry and custom document type registration."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Union
from docugen.core.exceptions import PluginError
from docugen.core.schema_registry import register_schema
from docugen.core.schemas import DocumentSchema
from docugen.generation.clause_engine import ClauseDefinition, get_clause_engine
from docugen.plugins.interfaces import DocuGenPlugin
from docugen.templates.registry import TemplateDefinition, get_template_registry
from docugen.validation.validator import CustomValidatorFn, register_validator

logger = logging.getLogger("docugen.plugins")

_REGISTERED_PLUGINS: Dict[str, DocuGenPlugin] = {}


def register_plugin(plugin: DocuGenPlugin) -> None:
    """Register and initialize an external plugin."""
    try:
        plugin.initialize()
        _REGISTERED_PLUGINS[plugin.name] = plugin
        logger.info("Successfully registered plugin: %s v%s", plugin.name, getattr(plugin, "version", "1.0.0"))
    except Exception as exc:
        raise PluginError(f"Failed to initialize plugin '{getattr(plugin, 'name', 'unnamed')}': {exc}") from exc


def list_plugins() -> List[str]:
    """List all registered plugins."""
    return sorted(list(_REGISTERED_PLUGINS.keys()))


def register_document_type(
    name: str,
    schema: DocumentSchema,
    template: Optional[TemplateDefinition] = None,
    composer: Optional[Callable[[Dict[str, Any], TemplateDefinition], Any]] = None,
    clauses: Optional[List[ClauseDefinition]] = None,
    validator: Optional[CustomValidatorFn] = None,
) -> None:
    """Register a complete custom document type without modifying core code.

    Args:
        name: Unique document type identifier (e.g. 'offer_letter').
        schema: DocumentSchema defining fields and rules.
        template: Optional TemplateDefinition.
        composer: Optional custom composer function returning Document IR.
        clauses: Optional list of ClauseDefinitions.
        validator: Optional custom validation function.
    """
    clean_name = name.strip().lower()

    # 1. Register Schema
    schema.document_type = clean_name
    register_schema(schema)

    # 2. Register Template
    tmpl = template or TemplateDefinition(
        name=clean_name,
        document_type=clean_name,
        composer=composer,
        description=f"Custom template for {clean_name}",
    )
    if composer and not tmpl.composer:
        tmpl.composer = composer
    get_template_registry().register(tmpl)

    # 3. Register Clauses if provided
    if clauses:
        engine = get_clause_engine()
        for clause in clauses:
            if clean_name not in clause.document_types:
                clause.document_types.append(clean_name)
            engine.register(clause)

    # 4. Register Validator if provided
    if validator:
        register_validator(clean_name, validator)

    logger.info("Successfully registered custom document type: '%s'", clean_name)
