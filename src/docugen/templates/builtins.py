"""Built-in templates initialization for DocuGen AI."""

from __future__ import annotations

from docugen.generation.composer import (
    compose_business_report,
    compose_certificate,
    compose_employment_contract,
    compose_invoice,
    compose_nda,
    compose_quotation,
    compose_service_agreement,
)
from docugen.templates.registry import TemplateDefinition, get_template_registry


def init_builtin_templates() -> None:
    """Register default built-in templates into the global registry."""
    registry = get_template_registry()

    templates = [
        TemplateDefinition(
            name="employment_contract",
            document_type="employment_contract",
            description="Standard Employment Agreement between Employer and Employee",
            is_builtin=True,
            composer=compose_employment_contract,
        ),
        TemplateDefinition(
            name="nda",
            document_type="nda",
            description="Mutual or Unilateral Non-Disclosure and Confidentiality Agreement",
            is_builtin=True,
            composer=compose_nda,
        ),
        TemplateDefinition(
            name="service_agreement",
            document_type="service_agreement",
            description="Professional Master Services Consulting Agreement",
            is_builtin=True,
            composer=compose_service_agreement,
        ),
        TemplateDefinition(
            name="invoice",
            document_type="invoice",
            description="Commercial Billing Invoice with Line Items and Calculations",
            is_builtin=True,
            composer=compose_invoice,
        ),
        TemplateDefinition(
            name="quotation",
            document_type="quotation",
            description="Formal Price Quotation and Services Estimate",
            is_builtin=True,
            composer=compose_quotation,
        ),
        TemplateDefinition(
            name="business_report",
            document_type="business_report",
            description="Executive Business and Analytical Report",
            is_builtin=True,
            composer=compose_business_report,
        ),
        TemplateDefinition(
            name="certificate",
            document_type="certificate",
            description="Certificate of Completion and Achievement",
            is_builtin=True,
            composer=compose_certificate,
        ),
    ]

    for tmpl in templates:
        registry.register(tmpl)


# Initialize built-ins on module import
init_builtin_templates()
