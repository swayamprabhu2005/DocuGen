"""Built-in schema registry for DocuGen AI."""

from __future__ import annotations

from typing import Dict, List, Optional
from docugen.core.exceptions import SchemaError
from docugen.core.schemas import CrossFieldRule, DocumentSchema, FieldDefinition, FieldType


_SCHEMAS: Dict[str, DocumentSchema] = {}


def register_schema(schema: DocumentSchema) -> None:
    """Register a DocumentSchema into the registry."""
    _SCHEMAS[schema.document_type.strip().lower()] = schema


def get_schema(document_type: str) -> DocumentSchema:
    """Retrieve the DocumentSchema for a given document type.

    Raises:
        SchemaError: If document type has no registered schema.
    """
    key = document_type.strip().lower()
    if key not in _SCHEMAS:
        raise SchemaError(
            f"No schema registered for document type '{document_type}'. Available: {list_document_types()}"
        )
    return _SCHEMAS[key]


def list_document_types() -> List[str]:
    """Return a sorted list of all registered document types."""
    return sorted(list(_SCHEMAS.keys()))


def _init_builtin_schemas() -> None:
    """Initialize built-in schemas for standard document types."""

    # 1. Employment Contract
    register_schema(
        DocumentSchema(
            document_type="employment_contract",
            title="Employment Agreement",
            category="employment",
            description="Standard professional employment agreement between employer and employee",
            disclaimer="This document template is for informational purposes and does not constitute legal advice.",
            fields={
                "employee_name": FieldDefinition(
                    name="employee_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Full legal name of the employee",
                    aliases=["employee", "worker_name", "candidate_name"],
                ),
                "company_name": FieldDefinition(
                    name="company_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Full legal entity name of the employing company",
                    aliases=["employer", "company", "organization"],
                ),
                "job_title": FieldDefinition(
                    name="job_title",
                    type=FieldType.STRING,
                    required=False,
                    default="Staff Professional",
                    description="Position or job title",
                    aliases=["role", "position", "designation"],
                ),
                "salary": FieldDefinition(
                    name="salary",
                    type=FieldType.NUMBER,
                    required=True,
                    minimum=0.0,
                    description="Compensation amount",
                    aliases=["compensation", "remuneration", "base_pay", "ctc"],
                ),
                "salary_period": FieldDefinition(
                    name="salary_period",
                    type=FieldType.STRING,
                    required=False,
                    default="year",
                    enum_values=["year", "month", "hour", "annual", "monthly"],
                    description="Compensation period",
                ),
                "joining_date": FieldDefinition(
                    name="joining_date",
                    type=FieldType.DATE,
                    required=True,
                    description="First day of employment (YYYY-MM-DD)",
                    aliases=["start_date", "commencement_date"],
                ),
                "work_location": FieldDefinition(
                    name="work_location",
                    type=FieldType.STRING,
                    required=False,
                    default="Remote",
                    description="Workplace location or remote designation",
                    aliases=["location", "office"],
                ),
                "probation_period_months": FieldDefinition(
                    name="probation_period_months",
                    type=FieldType.INTEGER,
                    required=False,
                    default=3,
                    minimum=0,
                    description="Probation duration in months",
                ),
                "notice_period_days": FieldDefinition(
                    name="notice_period_days",
                    type=FieldType.INTEGER,
                    required=False,
                    default=30,
                    minimum=0,
                    description="Termination notice period in days",
                ),
                "remote_work_allowed": FieldDefinition(
                    name="remote_work_allowed",
                    type=FieldType.BOOLEAN,
                    required=False,
                    default=True,
                    description="Whether remote work is permitted",
                ),
                "non_compete": FieldDefinition(
                    name="non_compete",
                    type=FieldType.BOOLEAN,
                    required=False,
                    default=False,
                    description="Whether non-compete covenants apply",
                ),
            },
        )
    )

    # 2. Non-Disclosure Agreement (NDA)
    register_schema(
        DocumentSchema(
            document_type="nda",
            title="Non-Disclosure Agreement",
            category="legal",
            description="Confidentiality and non-disclosure agreement protecting proprietary information",
            disclaimer="This document template is for informational purposes and does not constitute legal advice.",
            fields={
                "disclosing_party": FieldDefinition(
                    name="disclosing_party",
                    type=FieldType.STRING,
                    required=True,
                    description="Party disclosing proprietary information",
                    aliases=["discloser", "party_a"],
                ),
                "receiving_party": FieldDefinition(
                    name="receiving_party",
                    type=FieldType.STRING,
                    required=True,
                    description="Party receiving proprietary information",
                    aliases=["recipient", "party_b"],
                ),
                "effective_date": FieldDefinition(
                    name="effective_date",
                    type=FieldType.DATE,
                    required=True,
                    description="Effective date of the agreement (YYYY-MM-DD)",
                    aliases=["date", "start_date"],
                ),
                "duration_years": FieldDefinition(
                    name="duration_years",
                    type=FieldType.INTEGER,
                    required=False,
                    default=2,
                    minimum=1,
                    description="Term of confidentiality in years",
                ),
                "purpose": FieldDefinition(
                    name="purpose",
                    type=FieldType.STRING,
                    required=True,
                    description="Specific purpose for disclosing information",
                ),
                "jurisdiction": FieldDefinition(
                    name="jurisdiction",
                    type=FieldType.STRING,
                    required=False,
                    default="State of Delaware",
                    description="Governing jurisdiction/law",
                ),
                "mutual": FieldDefinition(
                    name="mutual",
                    type=FieldType.BOOLEAN,
                    required=False,
                    default=False,
                    description="Whether agreement binds both parties mutually",
                ),
                "remedies_injunctive_relief": FieldDefinition(
                    name="remedies_injunctive_relief",
                    type=FieldType.BOOLEAN,
                    required=False,
                    default=True,
                    description="Include injunctive relief clause",
                ),
            },
        )
    )

    # 3. Service Agreement
    register_schema(
        DocumentSchema(
            document_type="service_agreement",
            title="Master Services Agreement",
            category="legal",
            description="Consulting and professional services agreement",
            disclaimer="This document template is for informational purposes and does not constitute legal advice.",
            fields={
                "client_name": FieldDefinition(
                    name="client_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Name of the client receiving services",
                    aliases=["client", "customer"],
                ),
                "service_provider": FieldDefinition(
                    name="service_provider",
                    type=FieldType.STRING,
                    required=True,
                    description="Name of the contractor / service provider",
                    aliases=["contractor", "provider", "consultant"],
                ),
                "service_description": FieldDefinition(
                    name="service_description",
                    type=FieldType.STRING,
                    required=True,
                    description="Scope and description of services",
                    aliases=["scope", "services"],
                ),
                "start_date": FieldDefinition(
                    name="start_date",
                    type=FieldType.DATE,
                    required=True,
                    description="Engagement start date (YYYY-MM-DD)",
                    aliases=["effective_date"],
                ),
                "end_date": FieldDefinition(
                    name="end_date",
                    type=FieldType.DATE,
                    required=False,
                    description="Engagement end date (YYYY-MM-DD)",
                ),
                "fee_amount": FieldDefinition(
                    name="fee_amount",
                    type=FieldType.NUMBER,
                    required=True,
                    minimum=0.0,
                    description="Total or recurring fee amount",
                    aliases=["fee", "price", "amount"],
                ),
                "payment_terms": FieldDefinition(
                    name="payment_terms",
                    type=FieldType.STRING,
                    required=False,
                    default="Net 30",
                    description="Payment term conditions",
                ),
                "deliverables": FieldDefinition(
                    name="deliverables",
                    type=FieldType.LIST,
                    required=False,
                    description="List of specific project deliverables",
                ),
            },
        )
    )

    # 4. Invoice
    register_schema(
        DocumentSchema(
            document_type="invoice",
            title="Commercial Invoice",
            category="invoices",
            description="Billing invoice detailing products or services and payable amounts",
            fields={
                "invoice_number": FieldDefinition(
                    name="invoice_number",
                    type=FieldType.STRING,
                    required=True,
                    description="Unique invoice identifier",
                    aliases=["inv_no", "number", "invoice_id"],
                ),
                "issue_date": FieldDefinition(
                    name="issue_date",
                    type=FieldType.DATE,
                    required=True,
                    description="Date the invoice was issued (YYYY-MM-DD)",
                    aliases=["date", "invoice_date"],
                ),
                "due_date": FieldDefinition(
                    name="due_date",
                    type=FieldType.DATE,
                    required=True,
                    description="Payment due date (YYYY-MM-DD)",
                ),
                "seller_name": FieldDefinition(
                    name="seller_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Vendor or billing entity name",
                    aliases=["vendor", "from_name", "company_name"],
                ),
                "seller_address": FieldDefinition(
                    name="seller_address",
                    type=FieldType.STRING,
                    required=False,
                    description="Vendor billing address",
                ),
                "buyer_name": FieldDefinition(
                    name="buyer_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Client or customer name",
                    aliases=["client_name", "customer_name", "to_name"],
                ),
                "buyer_address": FieldDefinition(
                    name="buyer_address",
                    type=FieldType.STRING,
                    required=False,
                    description="Client billing address",
                ),
                "items": FieldDefinition(
                    name="items",
                    type=FieldType.LIST,
                    required=True,
                    description="List of billed line items",
                ),
                "subtotal": FieldDefinition(
                    name="subtotal",
                    type=FieldType.NUMBER,
                    required=True,
                    minimum=0.0,
                    description="Subtotal before taxes",
                ),
                "tax_rate": FieldDefinition(
                    name="tax_rate",
                    type=FieldType.NUMBER,
                    required=False,
                    default=0.0,
                    description="Tax rate percentage (e.g., 0.10 for 10%)",
                ),
                "tax_amount": FieldDefinition(
                    name="tax_amount",
                    type=FieldType.NUMBER,
                    required=False,
                    default=0.0,
                    description="Calculated tax amount",
                ),
                "total_amount": FieldDefinition(
                    name="total_amount",
                    type=FieldType.NUMBER,
                    required=True,
                    minimum=0.0,
                    description="Final total payable amount",
                    aliases=["total"],
                ),
                "currency": FieldDefinition(
                    name="currency",
                    type=FieldType.STRING,
                    required=False,
                    default="USD",
                    description="Currency code (e.g., USD, EUR, INR)",
                ),
                "payment_instructions": FieldDefinition(
                    name="payment_instructions",
                    type=FieldType.STRING,
                    required=False,
                    description="Bank wire details or payment instructions",
                ),
            },
        )
    )

    # 5. Quotation
    register_schema(
        DocumentSchema(
            document_type="quotation",
            title="Price Quotation",
            category="invoices",
            description="Formal price estimate and quotation for proposed products or services",
            fields={
                "quote_number": FieldDefinition(
                    name="quote_number",
                    type=FieldType.STRING,
                    required=True,
                    description="Unique quotation number",
                    aliases=["quotation_number", "estimate_number"],
                ),
                "quote_date": FieldDefinition(
                    name="quote_date",
                    type=FieldType.DATE,
                    required=True,
                    description="Date quote is generated (YYYY-MM-DD)",
                    aliases=["date"],
                ),
                "valid_until": FieldDefinition(
                    name="valid_until",
                    type=FieldType.DATE,
                    required=True,
                    description="Expiration date of quotation (YYYY-MM-DD)",
                    aliases=["expiry_date", "expiration_date"],
                ),
                "seller_name": FieldDefinition(
                    name="seller_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Providing company name",
                    aliases=["company_name", "vendor"],
                ),
                "client_name": FieldDefinition(
                    name="client_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Client or recipient name",
                    aliases=["customer_name"],
                ),
                "items": FieldDefinition(
                    name="items",
                    type=FieldType.LIST,
                    required=True,
                    description="Quoted items or services",
                ),
                "total_amount": FieldDefinition(
                    name="total_amount",
                    type=FieldType.NUMBER,
                    required=True,
                    minimum=0.0,
                    description="Quoted total amount",
                    aliases=["total"],
                ),
                "currency": FieldDefinition(
                    name="currency",
                    type=FieldType.STRING,
                    required=False,
                    default="USD",
                    description="Currency code",
                ),
                "terms_and_conditions": FieldDefinition(
                    name="terms_and_conditions",
                    type=FieldType.STRING,
                    required=False,
                    description="Standard quotation terms",
                ),
            },
        )
    )

    # 6. Business Report
    register_schema(
        DocumentSchema(
            document_type="business_report",
            title="Business Report",
            category="reports",
            description="Executive and analytical business report",
            fields={
                "report_title": FieldDefinition(
                    name="report_title",
                    type=FieldType.STRING,
                    required=True,
                    description="Title of the report",
                    aliases=["title"],
                ),
                "prepared_by": FieldDefinition(
                    name="prepared_by",
                    type=FieldType.STRING,
                    required=True,
                    description="Author or team who prepared the report",
                    aliases=["author"],
                ),
                "organization": FieldDefinition(
                    name="organization",
                    type=FieldType.STRING,
                    required=True,
                    description="Issuing company or organization",
                    aliases=["company_name"],
                ),
                "report_date": FieldDefinition(
                    name="report_date",
                    type=FieldType.DATE,
                    required=True,
                    description="Date of the report (YYYY-MM-DD)",
                    aliases=["date"],
                ),
                "executive_summary": FieldDefinition(
                    name="executive_summary",
                    type=FieldType.STRING,
                    required=True,
                    description="High-level executive summary",
                    aliases=["summary"],
                ),
                "findings": FieldDefinition(
                    name="findings",
                    type=FieldType.LIST,
                    required=False,
                    description="List of key findings or observations",
                ),
                "recommendations": FieldDefinition(
                    name="recommendations",
                    type=FieldType.LIST,
                    required=False,
                    description="List of strategic recommendations",
                ),
            },
        )
    )

    # 7. Certificate
    register_schema(
        DocumentSchema(
            document_type="certificate",
            title="Certificate of Achievement",
            category="certificates",
            description="Official certificate of completion or achievement",
            fields={
                "recipient_name": FieldDefinition(
                    name="recipient_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Name of recipient",
                    aliases=["name", "candidate_name", "student_name"],
                ),
                "certificate_title": FieldDefinition(
                    name="certificate_title",
                    type=FieldType.STRING,
                    required=False,
                    default="Certificate of Completion",
                    description="Title of the certificate",
                ),
                "course_or_achievement": FieldDefinition(
                    name="course_or_achievement",
                    type=FieldType.STRING,
                    required=True,
                    description="Course, program, or achievement honored",
                    aliases=["program", "course", "achievement"],
                ),
                "issuer_name": FieldDefinition(
                    name="issuer_name",
                    type=FieldType.STRING,
                    required=True,
                    description="Name of authorizing person or institution",
                    aliases=["organization", "authorized_by"],
                ),
                "issuer_title": FieldDefinition(
                    name="issuer_title",
                    type=FieldType.STRING,
                    required=False,
                    default="Director",
                    description="Title of issuer",
                ),
                "issue_date": FieldDefinition(
                    name="issue_date",
                    type=FieldType.DATE,
                    required=True,
                    description="Date of issuance (YYYY-MM-DD)",
                    aliases=["date"],
                ),
                "certificate_id": FieldDefinition(
                    name="certificate_id",
                    type=FieldType.STRING,
                    required=False,
                    description="Unique verification ID",
                ),
            },
        )
    )


# Run built-in schemas initialization
_init_builtin_schemas()
