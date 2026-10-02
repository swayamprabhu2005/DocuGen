"""DOCX document renderer using python-docx."""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional
import docx
from docugen.core.document_ir import (
    Alignment,
    BarcodeElement,
    BlockElement,
    ClauseIR,
    Document,
    Heading,
    Image,
    ListBlock,
    PageBreak,
    Paragraph,
    QRCodeElement,
    Section,
    SignatureBlock,
    Table,
)
from docugen.core.exceptions import RenderingError
from docugen.core.models import RenderResult
from docugen.rendering.barcodes import generate_barcode_bytes, generate_qr_bytes
from docugen.rendering.base import Renderer
from docugen.rendering.formatting import DocumentFormatting, get_default_formatting

logger = logging.getLogger("docugen.rendering.docx")


class DocxRenderer(Renderer):
    """Renders Document IR to a formatted Microsoft Word DOCX file."""

    def __init__(self, formatting: Optional[DocumentFormatting] = None) -> None:
        self.formatting = formatting or get_default_formatting()

    def render(self, document: Document, destination: Path) -> RenderResult:
        """Render Document IR to DOCX at destination path."""
        try:
            doc = docx.Document()
            self._apply_page_setup(doc, document)
            self._apply_metadata(doc, document)
            self._apply_headers_footers(doc, document)

            # Render title if present
            if document.metadata.title:
                h = doc.add_heading(document.metadata.title, level=0)
                h.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER

            # Render sections
            for section in document.sections:
                self._render_section(doc, section)

            # Ensure parent directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            doc.save(str(destination))

            file_size = destination.stat().st_size if destination.exists() else 0
            return RenderResult(
                success=True,
                output_path=str(destination.resolve()),
                format="docx",
                file_size_bytes=file_size,
            )
        except Exception as exc:
            logger.exception("Error during DOCX rendering: %s", exc)
            return RenderResult(
                success=False,
                output_path=str(destination),
                format="docx",
                error=str(exc),
            )

    def _apply_page_setup(self, doc: docx.Document, document: Document) -> None:
        """Configure page margins, orientation, and sizes."""
        section = doc.sections[0]
        section.top_margin = docx.shared.Pt(self.formatting.margin_top)
        section.bottom_margin = docx.shared.Pt(self.formatting.margin_bottom)
        section.left_margin = docx.shared.Pt(self.formatting.margin_left)
        section.right_margin = docx.shared.Pt(self.formatting.margin_right)

    def _apply_metadata(self, doc: docx.Document, document: Document) -> None:
        """Set DOCX core properties (author, title, subject)."""
        props = doc.core_properties
        if document.metadata.title:
            props.title = document.metadata.title
        if document.metadata.author:
            props.author = document.metadata.author
        if document.metadata.subject:
            props.subject = document.metadata.subject

    def _apply_headers_footers(self, doc: docx.Document, document: Document) -> None:
        """Configure header and footer text and watermark."""
        section = doc.sections[0]

        # Apply watermark in header if configured
        if document.watermark:
            wm_text = (document.watermark.status or document.watermark.text or "").strip().upper()
            if wm_text:
                p_wm = section.header.paragraphs[0]
                run_wm = p_wm.add_run(f"[{wm_text}]  ")
                run_wm.bold = True
                run_wm.font.size = docx.shared.Pt(11)
                run_wm.font.color.rgb = docx.shared.RGBColor(160, 160, 160)

        if document.header:
            header_text_parts = [
                t for t in (document.header.left_text, document.header.center_text, document.header.right_text) if t
            ]
            if header_text_parts:
                p = section.header.paragraphs[0]
                p.text = (p.text or "") + "   |   ".join(header_text_parts)
                p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.RIGHT

        if document.footer:
            footer_text_parts = [
                t for t in (document.footer.left_text, document.footer.center_text, document.footer.right_text) if t
            ]
            if footer_text_parts:
                p = section.footer.paragraphs[0]
                p.text = "   |   ".join(footer_text_parts)
                p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER

    def _render_section(self, doc: docx.Document, section: Section) -> None:
        """Render a single Document IR section into docx."""
        if section.title:
            doc.add_heading(section.title, level=1)

        for elem in section.elements:
            self._render_element(doc, elem)

        for sub in section.subsections:
            if sub.title:
                doc.add_heading(sub.title, level=2)
            for elem in sub.elements:
                self._render_element(doc, elem)

    def _render_element(self, doc: docx.Document, elem: BlockElement) -> None:
        """Render an individual block element."""
        if isinstance(elem, Heading):
            doc.add_heading(elem.text, level=min(elem.level, 4))

        elif isinstance(elem, Paragraph):
            self._render_paragraph(doc, elem)

        elif isinstance(elem, ClauseIR):
            h = doc.add_heading(f"{elem.number or ''} {elem.title}".strip(), level=2)
            for p in elem.body:
                self._render_paragraph(doc, p)

        elif isinstance(elem, ListBlock):
            style = "List Number" if elem.ordered else "List Bullet"
            for item in elem.items:
                p = doc.add_paragraph(style=style)
                for run in item.runs:
                    r = p.add_run(run.text)
                    r.bold = run.bold
                    r.italic = run.italic

        elif isinstance(elem, Table):
            self._render_table(doc, elem)

        elif isinstance(elem, SignatureBlock):
            self._render_signature_block(doc, elem)

        elif isinstance(elem, PageBreak):
            doc.add_page_break()

        elif isinstance(elem, QRCodeElement):
            p = doc.add_paragraph()
            p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
            qr_bytes = generate_qr_bytes(elem.data, size=int(elem.size * 2))
            p.add_run().add_picture(io.BytesIO(qr_bytes), width=docx.shared.Pt(elem.size))
            if elem.caption:
                cap_p = doc.add_paragraph(elem.caption)
                cap_p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                cap_p.runs[0].italic = True
                cap_p.runs[0].font.size = docx.shared.Pt(9)

        elif isinstance(elem, BarcodeElement):
            p = doc.add_paragraph()
            p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
            bc_bytes = generate_barcode_bytes(
                elem.data,
                barcode_type=elem.barcode_type,
                width=int(elem.width * 2),
                height=int(elem.height * 2),
            )
            p.add_run().add_picture(
                io.BytesIO(bc_bytes),
                width=docx.shared.Pt(elem.width),
                height=docx.shared.Pt(elem.height),
            )
            if elem.caption:
                cap_p = doc.add_paragraph(elem.caption)
                cap_p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
                cap_p.runs[0].italic = True
                cap_p.runs[0].font.size = docx.shared.Pt(9)

    def _render_paragraph(self, doc: docx.Document, para: Paragraph) -> None:
        """Render Paragraph IR with inline TextRuns."""
        p = doc.add_paragraph()
        if para.alignment == Alignment.CENTER:
            p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
        elif para.alignment == Alignment.RIGHT:
            p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.RIGHT
        elif para.alignment == Alignment.JUSTIFY:
            p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
        else:
            p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.LEFT

        p.paragraph_format.space_after = docx.shared.Pt(para.space_after)

        for run in para.runs:
            r = p.add_run(run.text)
            r.bold = run.bold
            r.italic = run.italic
            r.underline = run.underline
            if run.font_size:
                r.font.size = docx.shared.Pt(run.font_size)

    def _render_table(self, doc: docx.Document, tbl: Table) -> None:
        """Render Table IR into docx table."""
        if not tbl.rows:
            return

        col_count = max(len(row.cells) for row in tbl.rows)
        docx_tbl = doc.add_table(rows=len(tbl.rows), cols=col_count)
        docx_tbl.style = "Table Grid" if tbl.bordered else "Normal Table"

        for row_idx, row in enumerate(tbl.rows):
            docx_row = docx_tbl.rows[row_idx]
            for col_idx, cell in enumerate(row.cells):
                if col_idx >= col_count:
                    break
                docx_cell = docx_row.cells[col_idx]
                docx_cell.text = cell.plain_text
                # Make header bold
                if row.is_header or cell.bold:
                    for p in docx_cell.paragraphs:
                        for run in p.runs:
                            run.bold = True

        # Add small spacing after table
        doc.add_paragraph().paragraph_format.space_after = docx.shared.Pt(6)

    def _render_signature_block(self, doc: docx.Document, sig_block: SignatureBlock) -> None:
        """Render formal signature blocks with lines and signer details."""
        if sig_block.intro_text:
            doc.add_paragraph(sig_block.intro_text).paragraph_format.space_after = docx.shared.Pt(12)

        signers = sig_block.signers
        if not signers:
            return

        if sig_block.layout == "side_by_side" and len(signers) >= 2:
            tbl = doc.add_table(rows=1, cols=len(signers))
            tbl.style = "Normal Table"
            row = tbl.rows[0]
            for idx, signer in enumerate(signers):
                cell = row.cells[idx]
                p = cell.paragraphs[0]
                p.add_run("_____________________________________\n")
                name_run = p.add_run(f"Name: {signer.name}\n")
                name_run.bold = True
                if signer.title:
                    p.add_run(f"Title: {signer.title}\n")
                if signer.organization:
                    p.add_run(f"Company: {signer.organization}\n")
                if signer.date:
                    p.add_run(f"Date: {signer.date}\n")
        else:
            for signer in signers:
                p = doc.add_paragraph()
                p.add_run("_____________________________________\n")
                name_run = p.add_run(f"Name: {signer.name}\n")
                name_run.bold = True
                if signer.title:
                    p.add_run(f"Title: {signer.title}\n")
                if signer.organization:
                    p.add_run(f"Company: {signer.organization}\n")
                if signer.date:
                    p.add_run(f"Date: {signer.date}\n")
                p.paragraph_format.space_after = docx.shared.Pt(14)
