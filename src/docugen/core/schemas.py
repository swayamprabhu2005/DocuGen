"""Schema engine models and definitions for DocuGen AI."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    LIST = "list"
    OBJECT = "object"


class FieldDefinition(BaseModel):
    """Specification of a single document data field."""

    name: str
    type: FieldType = FieldType.STRING
    required: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    enum_values: Optional[List[Any]] = None
    regex_pattern: Optional[str] = None
    # For list of items or nested tables
    item_type: Optional[FieldType] = None
    item_fields: Optional[Dict[str, "FieldDefinition"]] = None


class CrossFieldRule(BaseModel):
    """Specification of a cross-field consistency rule."""

    rule_id: str
    description: str
    rule_type: str  # e.g., 'date_order', 'numeric_comparison', 'party_match', 'table_sum'
    field_a: str
    field_b: Optional[str] = None
    operator: Optional[str] = None  # e.g., '<=', '==', '!='
    error_message: str


class DocumentSchema(BaseModel):
    """Schema defining required structure and rules for a document type."""

    document_type: str
    title: str
    category: str = "general"
    version: str = "1.0.0"
    description: Optional[str] = None
    fields: Dict[str, FieldDefinition] = Field(default_factory=dict)
    cross_field_rules: List[CrossFieldRule] = Field(default_factory=list)
    disclaimer: Optional[str] = None

    def get_required_field_names(self) -> List[str]:
        """Return list of field names that are marked required."""
        return [f_name for f_name, f_def in self.fields.items() if f_def.required]

    def get_field_aliases_map(self) -> Dict[str, str]:
        """Map each alias back to the canonical field name."""
        alias_map: Dict[str, str] = {}
        for f_name, f_def in self.fields.items():
            for alias in f_def.aliases:
                alias_map[alias.lower()] = f_name
        return alias_map

    def export_json_schema(self) -> Dict[str, Any]:
        """Export machine-readable JSON schema standard representation."""
        properties: Dict[str, Any] = {}
        required: List[str] = []

        type_mapping = {
            FieldType.STRING: "string",
            FieldType.NUMBER: "number",
            FieldType.INTEGER: "integer",
            FieldType.BOOLEAN: "boolean",
            FieldType.DATE: "string",
            FieldType.LIST: "array",
            FieldType.OBJECT: "object",
        }

        for fname, fdef in self.fields.items():
            prop: Dict[str, Any] = {
                "type": type_mapping.get(fdef.type, "string"),
                "description": fdef.description or "",
            }
            if fdef.type == FieldType.DATE:
                prop["format"] = "date"
            if fdef.default is not None:
                prop["default"] = fdef.default
            if fdef.minimum is not None:
                prop["minimum"] = fdef.minimum
            if fdef.maximum is not None:
                prop["maximum"] = fdef.maximum
            if fdef.enum_values:
                prop["enum"] = fdef.enum_values
            if fdef.regex_pattern:
                prop["pattern"] = fdef.regex_pattern

            properties[fname] = prop
            if fdef.required:
                required.append(fname)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": self.title,
            "type": "object",
            "properties": properties,
            "required": required,
            "description": self.description or "",
        }
