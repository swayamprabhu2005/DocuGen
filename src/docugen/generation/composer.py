"""Document Composer for DocuGen AI.

Assembles normalized input data, resolved clauses, tables, metadata,
and layout styling into the format-neutral Document Intermediate Representation (IR).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List
from docugen.core.document_ir import (
    Alignment,
    ClauseIR,
    Document,
    DocumentMetadata,
    Footer,
    Header,
    Heading,
    ListBlock,
    ListItem,
    Paragraph,
    Section,
    SignatureBlock,
    Signer,
    Table,
    TableCell,
    TableRow,
    TextRun,
    Watermark,
)
from docugen.generation.clause_engine import get_clause_engine

if TYPE_CHECKING:
    from docugen.templates.registry import TemplateDefinition


def compose_employment_contract(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Compose Document IR for an Employment Contract."""
    doc = Document(
        metadata=DocumentMetadata(
            title=f"Employment Agreement - {data.get('employee_name')}",
            author=data.get("company_name"),
            organization=data.get("company_name"),
            document_type="employment_contract",
            template_name=template.name,
            version=template.version,
        ),
        header=Header(
            left_text=data.get("company_name"),
            right_text="CONFIDENTIAL",
        ),
        footer=Footer(
            left_text="Employment Agreement",
            center_text=f"{data.get('company_name')} | {data.get('employee_name')}",
            include_page_number=True,
        ),
    )

    # Section 1: Header / Title & Recitals
    s1 = Section(
        title="EMPLOYMENT AGREEMENT",
        elements=[
            Paragraph.from_text(
                f"This Employment Agreement (the 'Agreement') is made and entered into as of "
                f"{data.get('joining_date')} by and between {data.get('company_name')} "
                f"(the 'Company') and {data.get('employee_name')} (the 'Employee').",
                space_after=12.0,
            ),
            Paragraph.from_text(
                "WHEREAS, the Company desires to employ the Employee, and the Employee desires to "
                "be employed by the Company upon the terms, conditions, and covenants set forth herein.",
                space_after=12.0,
            ),
        ],
    )
    doc.sections.append(s1)

    # Section 2: Operative Clauses resolved from Clause Engine
    clauses = get_clause_engine().resolve_clauses_for_document("employment_contract", data)
    s2 = Section(
        title="TERMS AND CONDITIONS",
        elements=list(clauses),
    )
    doc.sections.append(s2)

    # Section 3: Execution and Signatures
    s3 = Section(
        title="SIGNATURES",
        elements=[
            Paragraph.from_text(
                "IN WITNESS WHEREOF, the parties hereto have executed this Employment Agreement "
                "as of the date first written above.",
                space_after=16.0,
            ),
            SignatureBlock(
                signers=[
                    Signer(
                        name=str(data.get("company_name")),
                        title="Authorized Officer",
                        organization=str(data.get("company_name")),
                        date=str(data.get("joining_date")),
                    ),
                    Signer(
                        name=str(data.get("employee_name")),
                        title="Employee",
                        date=str(data.get("joining_date")),
                    ),
                ],
                layout="side_by_side",
            ),
        ],
    )
    doc.sections.append(s3)

    return doc


def compose_nda(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Compose Document IR for a Non-Disclosure Agreement."""
    doc = Document(
        metadata=DocumentMetadata(
            title=f"Non-Disclosure Agreement - {data.get('disclosing_party')} & {data.get('receiving_party')}",
            author=data.get("disclosing_party"),
            document_type="nda",
            template_name=template.name,
            version=template.version,
        ),
        header=Header(left_text="NON-DISCLOSURE AGREEMENT", right_text="CONFIDENTIAL"),
        footer=Footer(include_page_number=True, left_text="Strictly Confidential"),
    )

    s1 = Section(
        title="MUTUAL NON-DISCLOSURE AGREEMENT" if data.get("mutual") else "NON-DISCLOSURE AGREEMENT",
        elements=[
            Paragraph.from_text(
                f"This Non-Disclosure Agreement (the 'Agreement') is entered into on {data.get('effective_date')} "
                f"by and between {data.get('disclosing_party')} ('Disclosing Party') and "
                f"{data.get('receiving_party')} ('Receiving Party').",
                space_after=12.0,
            ),
            Paragraph.from_text(
                f"The parties wish to explore business discussions regarding: {data.get('purpose')}.",
                space_after=12.0,
            ),
        ],
    )
    doc.sections.append(s1)

    clauses = get_clause_engine().resolve_clauses_for_document("nda", data)
    s2 = Section(title="COVENANTS & PROVISIONS", elements=list(clauses))
    doc.sections.append(s2)

    s3 = Section(
        title="EXECUTION",
        elements=[
            SignatureBlock(
                signers=[
                    Signer(
                        name=str(data.get("disclosing_party")),
                        title="Disclosing Party",
                        date=str(data.get("effective_date")),
                    ),
                    Signer(
                        name=str(data.get("receiving_party")),
                        title="Receiving Party",
                        date=str(data.get("effective_date")),
                    ),
                ],
                layout="side_by_side",
            )
        ],
    )
    doc.sections.append(s3)

    return doc


def compose_service_agreement(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Compose Document IR for a Service Agreement."""
    doc = Document(
        metadata=DocumentMetadata(
            title=f"Service Agreement - {data.get('client_name')}",
            author=data.get("service_provider"),
            document_type="service_agreement",
            template_name=template.name,
        ),
        header=Header(left_text="SERVICE AGREEMENT", right_text=str(data.get("service_provider"))),
        footer=Footer(include_page_number=True),
    )

    elements: List[Any] = [
        Paragraph.from_text(
            f"This Master Services Agreement is entered into on {data.get('start_date')} "
            f"between {data.get('client_name')} ('Client') and {data.get('service_provider')} ('Service Provider').",
            space_after=12.0,
        ),
        Heading(text="1. Scope of Services", level=2),
        Paragraph.from_text(str(data.get("service_description")), space_after=10.0),
    ]

    if data.get("deliverables"):
        elements.append(Heading(text="Deliverables", level=3))
        items = [ListItem.from_text(str(d), prefix="•") for d in data["deliverables"]]
        elements.append(ListBlock(items=items))

    elements.extend(
        [
            Heading(text="2. Compensation and Payment Terms", level=2),
            Paragraph.from_text(
                f"Client agrees to pay Service Provider a fee of {data.get('fee_amount')} "
                f"payable under {data.get('payment_terms', 'Net 30')} terms.",
                space_after=12.0,
            ),
            Heading(text="3. Signatures", level=2),
            SignatureBlock(
                signers=[
                    Signer(
                        name=str(data.get("client_name")),
                        title="Client Representative",
                        date=str(data.get("start_date")),
                    ),
                    Signer(
                        name=str(data.get("service_provider")),
                        title="Service Provider",
                        date=str(data.get("start_date")),
                    ),
                ],
                layout="side_by_side",
            ),
        ]
    )

    doc.sections.append(Section(title="MASTER SERVICES AGREEMENT", elements=elements))
    return doc


def compose_invoice(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Compose Document IR for a Commercial Invoice."""
    currency = data.get("currency", "USD")
    doc = Document(
        metadata=DocumentMetadata(
            title=f"Invoice #{data.get('invoice_number')}",
            author=data.get("seller_name"),
            document_type="invoice",
            template_name=template.name,
        ),
        header=Header(
            left_text=str(data.get("seller_name")),
            right_text=f"INVOICE #{data.get('invoice_number')}",
        ),
        footer=Footer(center_text="Thank you for your business!", include_page_number=True),
    )

    # Info table: From and To details
    info_table = Table(
        bordered=False,
        has_header=False,
        col_widths=[0.5, 0.5],
        rows=[
            TableRow(
                cells=[
                    TableCell(
                        content=[
                            Paragraph.from_text("BILLED FROM:", bold=True),
                            Paragraph.from_text(str(data.get("seller_name"))),
                            Paragraph.from_text(str(data.get("seller_address") or "")),
                        ]
                    ),
                    TableCell(
                        content=[
                            Paragraph.from_text("BILLED TO:", bold=True),
                            Paragraph.from_text(str(data.get("buyer_name"))),
                            Paragraph.from_text(str(data.get("buyer_address") or "")),
                        ]
                    ),
                ]
            ),
            TableRow(
                cells=[
                    TableCell(content=f"Invoice Date: {data.get('issue_date')}"),
                    TableCell(content=f"Due Date: {data.get('due_date')}"),
                ]
            ),
        ],
    )

    # Line items table
    item_rows = [
        TableRow(
            is_header=True,
            cells=[
                TableCell(content="Description", bold=True, background_color="#F2F4F7"),
                TableCell(content="Quantity", bold=True, alignment=Alignment.RIGHT, background_color="#F2F4F7"),
                TableCell(content="Unit Price", bold=True, alignment=Alignment.RIGHT, background_color="#F2F4F7"),
                TableCell(content="Total", bold=True, alignment=Alignment.RIGHT, background_color="#F2F4F7"),
            ],
        )
    ]

    for item in data.get("items", []):
        desc = item.get("description", "Item")
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0.0)
        tot = item.get("total", round(qty * price, 2))
        item_rows.append(
            TableRow(
                cells=[
                    TableCell(content=str(desc)),
                    TableCell(content=str(qty), alignment=Alignment.RIGHT),
                    TableCell(content=f"{currency} {price:,.2f}", alignment=Alignment.RIGHT),
                    TableCell(content=f"{currency} {tot:,.2f}", alignment=Alignment.RIGHT),
                ]
            )
        )

    # Subtotal and Total summary rows
    subtotal = float(data.get("subtotal", 0.0))
    tax_amt = float(data.get("tax_amount", 0.0))
    total_amt = float(data.get("total_amount", subtotal + tax_amt))

    item_rows.append(
        TableRow(
            cells=[
                TableCell(content=""),
                TableCell(content=""),
                TableCell(content="Subtotal:", bold=True, alignment=Alignment.RIGHT),
                TableCell(content=f"{currency} {subtotal:,.2f}", bold=True, alignment=Alignment.RIGHT),
            ]
        )
    )
    if tax_amt > 0:
        item_rows.append(
            TableRow(
                cells=[
                    TableCell(content=""),
                    TableCell(content=""),
                    TableCell(content="Tax:", bold=True, alignment=Alignment.RIGHT),
                    TableCell(content=f"{currency} {tax_amt:,.2f}", alignment=Alignment.RIGHT),
                ]
            )
        )
    item_rows.append(
        TableRow(
            cells=[
                TableCell(content=""),
                TableCell(content=""),
                TableCell(content="Total Due:", bold=True, alignment=Alignment.RIGHT),
                TableCell(content=f"{currency} {total_amt:,.2f}", bold=True, alignment=Alignment.RIGHT),
            ]
        )
    )

    items_table = Table(
        bordered=True,
        has_header=True,
        col_widths=[0.45, 0.15, 0.20, 0.20],
        rows=item_rows,
    )

    elements: List[Any] = [
        info_table,
        Paragraph.from_text("", space_after=12.0),
        items_table,
    ]

    if data.get("payment_instructions"):
        elements.extend(
            [
                Heading(text="Payment Instructions", level=3, space_before=16.0),
                Paragraph.from_text(str(data.get("payment_instructions"))),
            ]
        )

    doc.sections.append(Section(title=f"INVOICE #{data.get('invoice_number')}", elements=elements))
    return doc


def compose_quotation(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Compose Document IR for a Price Quotation."""
    currency = data.get("currency", "USD")
    doc = Document(
        metadata=DocumentMetadata(
            title=f"Quotation #{data.get('quote_number')}",
            author=data.get("seller_name"),
            document_type="quotation",
            template_name=template.name,
        ),
        header=Header(left_text=str(data.get("seller_name")), right_text=f"QUOTE #{data.get('quote_number')}"),
        footer=Footer(include_page_number=True, left_text=f"Valid until: {data.get('valid_until')}"),
    )

    item_rows = [
        TableRow(
            is_header=True,
            cells=[
                TableCell(content="Item / Service", bold=True, background_color="#F2F4F7"),
                TableCell(content="Quantity", bold=True, alignment=Alignment.RIGHT, background_color="#F2F4F7"),
                TableCell(content="Unit Price", bold=True, alignment=Alignment.RIGHT, background_color="#F2F4F7"),
                TableCell(content="Total", bold=True, alignment=Alignment.RIGHT, background_color="#F2F4F7"),
            ],
        )
    ]

    for item in data.get("items", []):
        desc = item.get("description", "Item")
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0.0)
        tot = item.get("total", round(qty * price, 2))
        item_rows.append(
            TableRow(
                cells=[
                    TableCell(content=str(desc)),
                    TableCell(content=str(qty), alignment=Alignment.RIGHT),
                    TableCell(content=f"{currency} {price:,.2f}", alignment=Alignment.RIGHT),
                    TableCell(content=f"{currency} {tot:,.2f}", alignment=Alignment.RIGHT),
                ]
            )
        )

    total_amt = float(data.get("total_amount", 0.0))
    item_rows.append(
        TableRow(
            cells=[
                TableCell(content=""),
                TableCell(content=""),
                TableCell(content="Quoted Total:", bold=True, alignment=Alignment.RIGHT),
                TableCell(content=f"{currency} {total_amt:,.2f}", bold=True, alignment=Alignment.RIGHT),
            ]
        )
    )

    elements: List[Any] = [
        Paragraph.from_text(f"Prepared for: {data.get('client_name')}", bold=True),
        Paragraph.from_text(
            f"Date: {data.get('quote_date')} | Valid Until: {data.get('valid_until')}", space_after=12.0
        ),
        Table(bordered=True, has_header=True, col_widths=[0.45, 0.15, 0.20, 0.20], rows=item_rows),
    ]

    if data.get("terms_and_conditions"):
        elements.extend(
            [
                Heading(text="Terms & Conditions", level=3, space_before=14.0),
                Paragraph.from_text(str(data.get("terms_and_conditions"))),
            ]
        )

    doc.sections.append(Section(title=f"PRICE QUOTATION #{data.get('quote_number')}", elements=elements))
    return doc


def compose_business_report(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Compose Document IR for a Business Report."""
    doc = Document(
        metadata=DocumentMetadata(
            title=str(data.get("report_title")),
            author=str(data.get("prepared_by")),
            organization=str(data.get("organization")),
            document_type="business_report",
            template_name=template.name,
        ),
        header=Header(left_text=str(data.get("organization")), right_text=str(data.get("report_title"))),
        footer=Footer(include_page_number=True, center_text=str(data.get("organization"))),
    )

    elements: List[Any] = [
        Paragraph.from_text(
            f"Author: {data.get('prepared_by')} | Organization: {data.get('organization')} | Date: {data.get('report_date')}",
            space_after=16.0,
        ),
        Heading(text="Executive Summary", level=2),
        Paragraph.from_text(str(data.get("executive_summary")), space_after=14.0),
    ]

    if data.get("findings"):
        elements.append(Heading(text="Key Findings", level=2))
        items = [ListItem.from_text(str(f), prefix="•") for f in data["findings"]]
        elements.append(ListBlock(items=items))

    if data.get("recommendations"):
        elements.append(Heading(text="Recommendations", level=2, space_before=14.0))
        items = [ListItem.from_text(str(r), prefix=f"{i + 1}.") for i, r in enumerate(data["recommendations"])]
        elements.append(ListBlock(items=items, ordered=True))

    doc.sections.append(Section(title=str(data.get("report_title")), elements=elements))
    return doc


def compose_certificate(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Compose Document IR for a Certificate."""
    doc = Document(
        metadata=DocumentMetadata(
            title=str(data.get("certificate_title", "Certificate of Achievement")),
            author=str(data.get("issuer_name")),
            document_type="certificate",
            template_name=template.name,
        ),
    )

    elements: List[Any] = [
        Paragraph.from_text("THIS IS PROUDLY PRESENTED TO", alignment=Alignment.CENTER, space_after=18.0),
        Heading(text=str(data.get("recipient_name")), level=1, alignment=Alignment.CENTER, space_after=18.0),
        Paragraph.from_text(
            "in recognition of successfully completing and mastering the curriculum for:",
            alignment=Alignment.CENTER,
            space_after=12.0,
        ),
        Paragraph.from_text(
            str(data.get("course_or_achievement")), bold=True, alignment=Alignment.CENTER, space_after=24.0
        ),
        Paragraph.from_text(
            f"Date of Issuance: {data.get('issue_date')}", alignment=Alignment.CENTER, space_after=24.0
        ),
        SignatureBlock(
            signers=[
                Signer(
                    name=str(data.get("issuer_name")),
                    title=str(data.get("issuer_title", "Authorized Signatory")),
                    date=str(data.get("issue_date")),
                )
            ],
            layout="side_by_side",
            intro_text=None,
        ),
    ]

    if data.get("certificate_id"):
        elements.append(
            Paragraph.from_text(
                f"Certificate ID: {data.get('certificate_id')}", alignment=Alignment.CENTER, space_after=6.0
            )
        )

    doc.sections.append(
        Section(title=str(data.get("certificate_title", "Certificate of Achievement")), elements=elements)
    )
    return doc


def compose_generic_document(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Fallback generic document composer when no specialized composer is registered."""
    doc = Document(
        metadata=DocumentMetadata(
            title=str(data.get("title", template.name.replace("_", " ").title())),
            document_type=template.document_type,
            template_name=template.name,
        ),
        header=Header(left_text=template.name.title()),
        footer=Footer(include_page_number=True),
    )

    elements: List[Any] = []
    for key, value in data.items():
        label = key.replace("_", " ").title()
        if isinstance(value, list):
            elements.append(Heading(text=label, level=2))
            items = [ListItem.from_text(str(v), prefix="•") for v in value]
            elements.append(ListBlock(items=items))
        elif isinstance(value, dict):
            elements.append(Heading(text=label, level=2))
            for k, v in value.items():
                elements.append(Paragraph.from_text(f"{k}: {v}"))
        else:
            elements.append(Paragraph.from_text(f"{label}: {value}"))

    doc.sections.append(Section(title=template.name.replace("_", " ").title(), elements=elements))
    return doc


def compose_document(data: Dict[str, Any], template: TemplateDefinition) -> Document:
    """Master composer directing data and template definition to appropriate composer."""
    if template.composer:
        return template.composer(data, template)

    if template.file_path and str(template.file_path).endswith(".docx"):
        from pathlib import Path
        from docugen.templates.docx_parser import parse_and_merge_docx_template

        return parse_and_merge_docx_template(Path(template.file_path), data, template)

    # Built-in dispatch
    composers = {
        "employment_contract": compose_employment_contract,
        "nda": compose_nda,
        "service_agreement": compose_service_agreement,
        "invoice": compose_invoice,
        "quotation": compose_quotation,
        "business_report": compose_business_report,
        "certificate": compose_certificate,
    }

    composer_fn = composers.get(template.name.lower()) or composers.get(template.document_type.lower())
    if composer_fn:
        return composer_fn(data, template)

    return compose_generic_document(data, template)
