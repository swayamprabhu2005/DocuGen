"""Command-line interface (CLI) for DocuGen AI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from docugen.api.public import (
    classify_document,
    generate_document,
    get_schema,
    list_document_types,
    list_templates,
    validate_document_data,
)
from docugen.input.adapters import adapt_input
from docugen.versioning.metadata import __version__


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docugen",
        description="DocuGen AI: Production-grade, local-first document generation framework",
    )
    parser.add_argument("--version", action="version", version=f"docugen {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. generate
    gen_parser = subparsers.add_parser("generate", help="Generate a document from input data")
    gen_parser.add_argument("-t", "--template", required=True, help="Template name or file path")
    gen_parser.add_argument("-d", "--data", required=True, help="Path to input JSON file or JSON string")
    gen_parser.add_argument("-o", "--output", help="Output file destination (e.g. output.pdf)")
    gen_parser.add_argument("-f", "--format", choices=["pdf", "docx"], default="pdf", help="Output format")
    gen_parser.add_argument("--strict", action="store_true", default=True, help="Enforce strict validation (default)")
    gen_parser.add_argument("--lenient", action="store_false", dest="strict", help="Allow generation with warnings")
    gen_parser.add_argument("--dry-run", action="store_true", help="Validate and assemble IR without rendering")

    # 2. validate
    val_parser = subparsers.add_parser("validate", help="Validate document input data against schema")
    val_parser.add_argument("-t", "--template", required=True, help="Template or document type name")
    val_parser.add_argument("-d", "--data", required=True, help="Path to input JSON file or JSON string")
    val_parser.add_argument("--strict", action="store_true", help="Exit with non-zero code on failure")

    # 3. templates
    tmpl_parser = subparsers.add_parser("templates", help="Manage and inspect templates")
    tmpl_sub = tmpl_parser.add_subparsers(dest="subcommand")
    tmpl_sub.add_parser("list", help="List all available templates")

    # 4. schemas
    schema_parser = subparsers.add_parser("schemas", help="Manage and inspect schemas")
    schema_sub = schema_parser.add_subparsers(dest="subcommand")
    schema_sub.add_parser("list", help="List all registered document types")
    show_p = schema_sub.add_parser("show", help="Show JSON schema for a document type")
    show_p.add_argument("document_type", help="Document type identifier")

    # 5. document-types list
    dt_parser = subparsers.add_parser("document-types", help="Inspect document types")
    dt_sub = dt_parser.add_subparsers(dest="subcommand")
    dt_sub.add_parser("list", help="List all registered document types")

    return parser


def main(args: Optional[Sequence[str]] = None) -> int:
    parser = create_parser()
    parsed = parser.parse_args(args)

    if not parsed.command:
        parser.print_help()
        return 0

    try:
        # Handle 'generate'
        if parsed.command == "generate":
            data = adapt_input(parsed.data)
            res = generate_document(
                data=data,
                template=parsed.template,
                output=parsed.format,
                output_path=parsed.output,
                strict=parsed.strict,
                dry_run=parsed.dry_run,
            )
            if res.success:
                print("[OK] Document generated successfully:")
                print(f"  Type:   {res.document_type}")
                print(f"  Format: {res.output_format}")
                print(f"  Output: {res.output_path or '(dry run)'}")
                if res.warnings:
                    print("  Warnings:")
                    for w in res.warnings:
                        print(f"    - {w}")
                return 0
            else:
                print(f"[ERROR] Document generation failed: {res.error}", file=sys.stderr)
                if res.validation and not res.validation.valid:
                    for err in res.validation.errors:
                        print(f"  [{err.code}] {err.message}", file=sys.stderr)
                return 1

        # Handle 'validate'
        elif parsed.command == "validate":
            data = adapt_input(parsed.data)
            res = validate_document_data(data=data, template=parsed.template, strict=parsed.strict)
            if res.valid:
                print(f"[OK] Data is valid for template '{parsed.template}'.")
                if res.warnings:
                    for w in res.warnings:
                        print(f"  [Warning: {w.code}] {w.message}")
                return 0
            else:
                print(f"[FAIL] Data failed validation for template '{parsed.template}':", file=sys.stderr)
                for err in res.errors:
                    print(f"  [{err.code}] {err.message}", file=sys.stderr)
                return 1

        # Handle 'templates'
        elif parsed.command == "templates":
            if parsed.subcommand == "list" or not parsed.subcommand:
                templates = list_templates()
                print("Available Templates:")
                for tmpl in templates:
                    print(f"  - {tmpl}")
                return 0

        # Handle 'schemas'
        elif parsed.command == "schemas":
            if parsed.subcommand == "list" or not parsed.subcommand:
                types = list_document_types()
                print("Registered Document Schemas:")
                for t in types:
                    print(f"  - {t}")
                return 0
            elif parsed.subcommand == "show":
                schema = get_schema(parsed.document_type)
                print(json.dumps(schema.export_json_schema(), indent=2))
                return 0

        # Handle 'document-types'
        elif parsed.command == "document-types":
            types = list_document_types()
            print("Registered Document Types:")
            for t in types:
                print(f"  - {t}")
            return 0

    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
