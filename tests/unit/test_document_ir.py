"""Tests for Document Intermediate Representation (IR)."""

from docugen.core.document_ir import (
    Alignment,
    ClauseIR,
    Document,
    DocumentMetadata,
    Heading,
    ListBlock,
    ListItem,
    Paragraph,
    Section,
    Table,
    TableCell,
    TableRow,
    TextRun,
    Watermark,
)


def test_document_ir_construction_and_plain_text():
    doc = Document(
        metadata=DocumentMetadata(
            title="Sample Agreement",
            author="DocuGen Test",
            document_type="test_doc",
        ),
        watermark=Watermark(text="SAMPLE"),
        sections=[
            Section(
                title="Section 1: Introduction",
                elements=[
                    Paragraph.from_text("This is an introductory paragraph.", bold=True),
                    Heading(text="Scope of Work", level=2),
                    ListBlock(
                        items=[
                            ListItem.from_text("Deliverable 1"),
                            ListItem.from_text("Deliverable 2"),
                        ]
                    ),
                    Table(
                        rows=[
                            TableRow(
                                is_header=True,
                                cells=[
                                    TableCell(content="Header 1"),
                                    TableCell(content="Header 2"),
                                ],
                            ),
                            TableRow(
                                cells=[
                                    TableCell(content="Data 1"),
                                    TableCell(content="Data 2"),
                                ]
                            ),
                        ]
                    ),
                ],
            )
        ],
    )

    plain_text = doc.get_plain_text()
    assert "Sample Agreement" in plain_text
    assert "Section 1: Introduction" in plain_text
    assert "This is an introductory paragraph." in plain_text
    assert "Deliverable 1" in plain_text
    assert "Header 1 | Header 2" in plain_text


def test_document_ir_serialization():
    doc = Document(
        metadata=DocumentMetadata(title="Test Doc"),
        sections=[
            Section(
                title="S1",
                elements=[
                    Paragraph(
                        runs=[TextRun(text="Hello ", bold=True), TextRun(text="World", italic=True)],
                        alignment=Alignment.CENTER,
                    )
                ],
            )
        ],
    )

    doc_dict = doc.to_dict()
    assert doc_dict["metadata"]["title"] == "Test Doc"
    assert len(doc_dict["sections"]) == 1

    # Roundtrip from dict
    restored = Document.from_dict(doc_dict)
    assert restored.metadata.title == "Test Doc"
    assert restored.sections[0].title == "S1"
    assert restored.sections[0].elements[0].runs[0].text == "Hello "

    # Roundtrip JSON
    json_str = doc.to_json()
    from_json = Document.from_json(json_str)
    assert from_json.metadata.title == "Test Doc"
