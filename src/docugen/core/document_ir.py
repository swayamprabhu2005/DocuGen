"""Document Intermediate Representation (Document IR).

Provides an abstract, typed, format-agnostic internal tree structure
representing a document's semantic and visual components. Renderers
(DOCX, PDF, etc.) consume this structure without embedding business logic.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class TextRun(BaseModel):
    """An inline run of text with optional styling."""

    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: Optional[str] = None  # Hex or named color
    font_size: Optional[float] = None
    link_url: Optional[str] = None


class Paragraph(BaseModel):
    """A block paragraph composed of text runs and formatting options."""

    runs: List[TextRun] = Field(default_factory=list)
    alignment: Alignment = Alignment.LEFT
    space_before: float = 0.0
    space_after: float = 6.0
    line_spacing: float = 1.15
    indent: float = 0.0

    @classmethod
    def from_text(
        cls,
        text: str,
        bold: bool = False,
        italic: bool = False,
        alignment: Alignment = Alignment.LEFT,
        space_after: float = 6.0,
        space_before: float = 0.0,
    ) -> "Paragraph":
        return cls(
            runs=[TextRun(text=text, bold=bold, italic=italic)],
            alignment=alignment,
            space_after=space_after,
            space_before=space_before,
        )

    @property
    def plain_text(self) -> str:
        return "".join(run.text for run in self.runs)


class Heading(BaseModel):
    """A heading element (level 1 to 6)."""

    text: str
    level: int = Field(default=1, ge=1, le=6)
    number: Optional[str] = None  # e.g., "1.0", "2.1"
    alignment: Alignment = Alignment.LEFT
    space_before: float = 12.0
    space_after: float = 6.0


class ListItem(BaseModel):
    """An individual item in an ordered or unordered list."""

    runs: List[TextRun] = Field(default_factory=list)
    prefix: Optional[str] = None  # e.g. "1.", "a)", "•"

    @classmethod
    def from_text(cls, text: str, prefix: Optional[str] = None) -> "ListItem":
        return cls(runs=[TextRun(text=text)], prefix=prefix)

    @property
    def plain_text(self) -> str:
        return "".join(run.text for run in self.runs)


class ListBlock(BaseModel):
    """An ordered or unordered list of items."""

    items: List[ListItem] = Field(default_factory=list)
    ordered: bool = False
    bullet_style: Optional[str] = None  # e.g. "bullet", "circle", "decimal"


class TableCell(BaseModel):
    """A cell within a table row."""

    content: Union[str, List[Paragraph]] = ""
    col_span: int = 1
    row_span: int = 1
    alignment: Alignment = Alignment.LEFT
    bold: bool = False
    background_color: Optional[str] = None
    width: Optional[float] = None

    @property
    def plain_text(self) -> str:
        if isinstance(self.content, str):
            return self.content
        return " ".join(p.plain_text for p in self.content)


class TableRow(BaseModel):
    """A row in a table."""

    cells: List[TableCell] = Field(default_factory=list)
    is_header: bool = False


class Table(BaseModel):
    """A structured table element."""

    rows: List[TableRow] = Field(default_factory=list)
    columns: Optional[List[str]] = None  # Column header labels
    col_widths: Optional[List[float]] = None  # Fractional or point widths
    has_header: bool = True
    bordered: bool = True
    striped: bool = False
    caption: Optional[str] = None
    alignment: Alignment = Alignment.CENTER


class Image(BaseModel):
    """An embedded image element."""

    path: str
    width: Optional[float] = None
    height: Optional[float] = None
    caption: Optional[str] = None
    alignment: Alignment = Alignment.CENTER


class Signer(BaseModel):
    """Signer information in a signature block."""

    name: str
    title: Optional[str] = None
    organization: Optional[str] = None
    date: Optional[str] = None
    signature_line: bool = True


class SignatureBlock(BaseModel):
    """A formal signature block with one or more signers."""

    signers: List[Signer] = Field(default_factory=list)
    layout: Literal["stacked", "side_by_side"] = "side_by_side"
    intro_text: Optional[str] = "IN WITNESS WHEREOF, the parties hereto have executed this document."


class PageBreak(BaseModel):
    """Explicit page break."""

    pass


class Header(BaseModel):
    """Document header."""

    left_text: Optional[str] = None
    center_text: Optional[str] = None
    right_text: Optional[str] = None
    include_page_number: bool = False
    logo_path: Optional[str] = None


class Footer(BaseModel):
    """Document footer."""

    left_text: Optional[str] = None
    center_text: Optional[str] = None
    right_text: Optional[str] = None
    include_page_number: bool = True
    include_date: bool = False


class Watermark(BaseModel):
    """Diagonal background or status watermark supporting text, status labels, or images."""

    text: Optional[str] = "CONFIDENTIAL"
    status: Optional[str] = None  # e.g., "PAID", "DRAFT", "VOID", "CONFIDENTIAL", "APPROVED"
    image_path: Optional[str] = None  # Path to background logo or crest image
    color: str = "#E0E0E0"
    opacity: float = 0.3
    font_size: float = 54.0
    rotation: float = 45.0


class QRCodeElement(BaseModel):
    """A dynamic QR code block element."""

    data: str
    size: float = 80.0
    caption: Optional[str] = None
    alignment: Alignment = Alignment.CENTER


class BarcodeElement(BaseModel):
    """A standard 1D barcode block element (e.g. Code128, Standard39, EAN13)."""

    data: str
    barcode_type: str = "Code128"
    width: float = 160.0
    height: float = 40.0
    caption: Optional[str] = None
    alignment: Alignment = Alignment.CENTER


class FieldValue(BaseModel):
    """A key-value metadata field representation."""

    key: str
    label: str
    value: Any


class ClauseIR(BaseModel):
    """A legal or business clause embedded in a document."""

    clause_id: str
    title: str
    body: List[Paragraph] = Field(default_factory=list)
    number: Optional[str] = None
    category: Optional[str] = None
    optional: bool = False


# Union of all block elements that can appear inside a Section
BlockElement = Union[
    Paragraph,
    Heading,
    ListBlock,
    Table,
    Image,
    SignatureBlock,
    PageBreak,
    ClauseIR,
    QRCodeElement,
    BarcodeElement,
]


class Subsection(BaseModel):
    """A subsection within a document section."""

    title: Optional[str] = None
    number: Optional[str] = None
    elements: List[BlockElement] = Field(default_factory=list)


class Section(BaseModel):
    """A major logical section of a document."""

    title: Optional[str] = None
    number: Optional[str] = None
    elements: List[BlockElement] = Field(default_factory=list)
    subsections: List[Subsection] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    """Descriptive metadata for the document."""

    title: str = "Untitled Document"
    subject: Optional[str] = None
    author: Optional[str] = None
    organization: Optional[str] = None
    document_type: str = "general"
    template_name: Optional[str] = None
    version: str = "1.0.0"
    created_at: Optional[str] = None
    generator_version: str = "0.1.0"
    custom: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """Root container of the Document Intermediate Representation."""

    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    header: Optional[Header] = None
    footer: Optional[Footer] = None
    watermark: Optional[Watermark] = None
    sections: List[Section] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Document IR to a python dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Deserialize Document IR from a python dictionary."""
        return cls.model_validate(data)

    def to_json(self, indent: int = 2) -> str:
        """Serialize Document IR to a JSON string."""
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "Document":
        """Deserialize Document IR from a JSON string."""
        return cls.model_validate_json(json_str)

    def get_all_paragraphs(self) -> List[Paragraph]:
        """Extract all paragraphs recursively across sections and subsections."""
        paragraphs: List[Paragraph] = []
        for section in self.sections:
            for elem in section.elements:
                if isinstance(elem, Paragraph):
                    paragraphs.append(elem)
                elif isinstance(elem, ClauseIR):
                    paragraphs.extend(elem.body)
            for sub in section.subsections:
                for elem in sub.elements:
                    if isinstance(elem, Paragraph):
                        paragraphs.append(elem)
                    elif isinstance(elem, ClauseIR):
                        paragraphs.extend(elem.body)
        return paragraphs

    def get_plain_text(self) -> str:
        """Extract plain text of the entire document."""
        chunks: List[str] = [self.metadata.title]
        for section in self.sections:
            if section.title:
                chunks.append(section.title)
            for elem in section.elements:
                if isinstance(elem, Paragraph):
                    chunks.append(elem.plain_text)
                elif isinstance(elem, Heading):
                    chunks.append(elem.text)
                elif isinstance(elem, ListBlock):
                    chunks.extend(item.plain_text for item in elem.items)
                elif isinstance(elem, Table):
                    for row in elem.rows:
                        chunks.append(" | ".join(c.plain_text for c in row.cells))
                elif isinstance(elem, ClauseIR):
                    chunks.append(elem.title)
                    chunks.extend(p.plain_text for p in elem.body)
            for sub in section.subsections:
                if sub.title:
                    chunks.append(sub.title)
                for elem in sub.elements:
                    if isinstance(elem, Paragraph):
                        chunks.append(elem.plain_text)
                    elif isinstance(elem, Heading):
                        chunks.append(elem.text)
                    elif isinstance(elem, ClauseIR):
                        chunks.append(elem.title)
                        chunks.extend(p.plain_text for p in elem.body)
        return "\n".join(chunks)
