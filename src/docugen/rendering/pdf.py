"""PDF document renderer using ReportLab."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List, Optional
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak as FlowablePageBreak,
    Paragraph as PlatypusParagraph,
    SimpleDocTemplate,
    Spacer,
    Table as PlatypusTable,
    TableStyle,
)

from docugen.core.document_ir import (
    Alignment,
    BlockElement,
    ClauseIR,
    Document,
    Heading,
    ListBlock,
    PageBreak,
    Paragraph,
    Section,
    SignatureBlock,
    Table,
    Watermark,
)
from docugen.core.models import RenderResult
from docugen.rendering.base import Renderer
from docugen.rendering.formatting import DocumentFormatting, get_default_formatting

logger = logging.getLogger("docugen.rendering.pdf")


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas recording total pages to stamp 'Page X of Y', headers, footers, and watermarks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Any] = []
        self.docugen_doc: Optional[Document] = None
        self.docugen_formatting: Optional[DocumentFormatting] = None

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages: int) -> None:
        if not self.docugen_doc or not self.docugen_formatting:
            return

        fmt = self.docugen_formatting
        width, height = self._pagesize

        # 1. Draw Watermark if present
        wm = self.docugen_doc.watermark
        if wm and wm.text:
            self.saveState()
            self.setFont("Helvetica-Bold", wm.font_size)
            try:
                wm_color = colors.HexColor(wm.color)
            except Exception:
                wm_color = colors.lightgrey
            self.setFillColor(wm_color, alpha=wm.opacity)
            self.translate(width / 2.0, height / 2.0)
            self.rotate(45)
            self.drawCentredString(0, 0, wm.text.upper())
            self.restoreState()

        # 2. Draw Header
        if self.docugen_doc.header:
            hdr = self.docugen_doc.header
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor(fmt.secondary_color))
            y_pos = height - fmt.margin_top + 18
            if hdr.left_text:
                self.drawString(fmt.margin_left, y_pos, hdr.left_text)
            if hdr.center_text:
                self.drawCentredString(width / 2.0, y_pos, hdr.center_text)
            if hdr.right_text:
                self.drawRightString(width - fmt.margin_right, y_pos, hdr.right_text)
            # Thin rule under header
            self.setStrokeColor(colors.HexColor(fmt.table_border_color))
            self.setLineWidth(0.5)
            self.line(fmt.margin_left, y_pos - 4, width - fmt.margin_right, y_pos - 4)
            self.restoreState()

        # 3. Draw Footer
        if self.docugen_doc.footer:
            ftr = self.docugen_doc.footer
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor(fmt.secondary_color))
            y_pos = fmt.margin_bottom - 24
            # Thin rule above footer
            self.setStrokeColor(colors.HexColor(fmt.table_border_color))
            self.setLineWidth(0.5)
            self.line(fmt.margin_left, y_pos + 12, width - fmt.margin_right, y_pos + 12)

            if ftr.left_text:
                self.drawString(fmt.margin_left, y_pos, ftr.left_text)
            if ftr.center_text:
                self.drawCentredString(width / 2.0, y_pos, ftr.center_text)

            # Page numbering
            if ftr.include_page_number:
                page_str = f"Page {self._pageNumber} of {total_pages}"
                if ftr.right_text:
                    page_str = f"{ftr.right_text}  |  {page_str}"
                self.drawRightString(width - fmt.margin_right, y_pos, page_str)
            elif ftr.right_text:
                self.drawRightString(width - fmt.margin_right, y_pos, ftr.right_text)

            self.restoreState()


class PdfRenderer(Renderer):
    """Renders Document IR to a professional PDF using ReportLab Platypus."""

    def __init__(self, formatting: Optional[DocumentFormatting] = None) -> None:
        self.formatting = formatting or get_default_formatting()
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()

    def _init_custom_styles(self) -> None:
        fmt = self.formatting

        self.styles.add(
            ParagraphStyle(
                name="DocTitle",
                fontName="Helvetica-Bold",
                fontSize=fmt.heading1_size + 2,
                leading=fmt.heading1_size + 8,
                textColor=colors.HexColor(fmt.primary_color),
                alignment=TA_CENTER,
                spaceAfter=14,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="DocHeading1",
                fontName="Helvetica-Bold",
                fontSize=fmt.heading1_size - 4,
                leading=fmt.heading1_size + 2,
                textColor=colors.HexColor(fmt.primary_color),
                spaceBefore=14,
                spaceAfter=8,
                keepWithNext=True,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="DocHeading2",
                fontName="Helvetica-Bold",
                fontSize=fmt.heading2_size,
                leading=fmt.heading2_size + 4,
                textColor=colors.HexColor(fmt.text_color),
                spaceBefore=10,
                spaceAfter=6,
                keepWithNext=True,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="DocHeading3",
                fontName="Helvetica-Bold",
                fontSize=fmt.heading3_size,
                leading=fmt.heading3_size + 3,
                textColor=colors.HexColor(fmt.text_color),
                spaceBefore=8,
                spaceAfter=4,
                keepWithNext=True,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="DocBody",
                fontName="Helvetica",
                fontSize=fmt.body_size,
                leading=fmt.body_size * fmt.line_spacing + 1,
                textColor=colors.HexColor(fmt.text_color),
                spaceAfter=6,
            )
        )

    def render(self, document: Document, destination: Path) -> RenderResult:
        """Render Document IR to destination PDF file."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            doc_tpl = SimpleDocTemplate(
                str(destination),
                pagesize=letter,
                leftMargin=self.formatting.margin_left,
                rightMargin=self.formatting.margin_right,
                topMargin=self.formatting.margin_top,
                bottomMargin=self.formatting.margin_bottom,
            )

            story: List[Any] = []

            # Document Title Header
            if document.metadata.title:
                story.append(PlatypusParagraph(document.metadata.title, self.styles["DocTitle"]))
                story.append(Spacer(1, 10))

            # Sections
            for section in document.sections:
                self._render_section(story, section)

            # Factory function to link canvas with doc
            def make_canvas(*args: Any, **kwargs: Any) -> NumberedCanvas:
                c = NumberedCanvas(*args, **kwargs)
                c.docugen_doc = document
                c.docugen_formatting = self.formatting
                return c

            doc_tpl.build(story, canvasmaker=make_canvas)

            file_size = destination.stat().st_size if destination.exists() else 0
            return RenderResult(
                success=True,
                output_path=str(destination.resolve()),
                format="pdf",
                file_size_bytes=file_size,
            )
        except Exception as exc:
            logger.exception("Error during PDF rendering: %s", exc)
            return RenderResult(
                success=False,
                output_path=str(destination),
                format="pdf",
                error=str(exc),
            )

    def _render_section(self, story: List[Any], section: Section) -> None:
        if section.title:
            story.append(PlatypusParagraph(section.title, self.styles["DocHeading1"]))

        for elem in section.elements:
            self._render_element(story, elem)

        for sub in section.subsections:
            if sub.title:
                story.append(PlatypusParagraph(sub.title, self.styles["DocHeading2"]))
            for elem in sub.elements:
                self._render_element(story, elem)

    def _render_element(self, story: List[Any], elem: BlockElement) -> None:
        if isinstance(elem, Heading):
            style_name = "DocHeading1" if elem.level == 1 else ("DocHeading2" if elem.level == 2 else "DocHeading3")
            story.append(PlatypusParagraph(elem.text, self.styles[style_name]))

        elif isinstance(elem, Paragraph):
            story.append(self._build_platypus_paragraph(elem))

        elif isinstance(elem, ClauseIR):
            title = f"{elem.number or ''} {elem.title}".strip()
            story.append(PlatypusParagraph(title, self.styles["DocHeading2"]))
            for p in elem.body:
                story.append(self._build_platypus_paragraph(p))

        elif isinstance(elem, ListBlock):
            for item in elem.items:
                prefix = item.prefix or ("•" if not elem.ordered else "")
                xml_text = f"<b>{prefix}</b> " + self._runs_to_xml(item.runs)
                story.append(PlatypusParagraph(xml_text, self.styles["DocBody"]))

        elif isinstance(elem, Table):
            story.append(self._build_platypus_table(elem))
            story.append(Spacer(1, 8))

        elif isinstance(elem, SignatureBlock):
            sig_flowables = self._build_signature_flowables(elem)
            story.append(KeepTogether(sig_flowables))

        elif isinstance(elem, PageBreak):
            story.append(FlowablePageBreak())

    def _build_platypus_paragraph(self, para: Paragraph) -> PlatypusParagraph:
        xml_text = self._runs_to_xml(para.runs)
        style = ParagraphStyle("InlinePara", parent=self.styles["DocBody"])
        if para.alignment == Alignment.CENTER:
            style.alignment = TA_CENTER
        elif para.alignment == Alignment.RIGHT:
            style.alignment = TA_RIGHT
        elif para.alignment == Alignment.JUSTIFY:
            style.alignment = TA_JUSTIFY
        else:
            style.alignment = TA_LEFT
        style.spaceAfter = para.space_after
        return PlatypusParagraph(xml_text, style)

    def _runs_to_xml(self, runs: List[Any]) -> str:
        parts: List[str] = []
        for r in runs:
            escaped = r.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if r.bold:
                escaped = f"<b>{escaped}</b>"
            if r.italic:
                escaped = f"<i>{escaped}</i>"
            if r.underline:
                escaped = f"<u>{escaped}</u>"
            if r.color:
                escaped = f"<font color='{r.color}'>{escaped}</font>"
            parts.append(escaped)
        return "".join(parts) or "&nbsp;"

    def _build_platypus_table(self, tbl: Table) -> PlatypusTable:
        # Printable page width ~ 500 pt
        usable_width = 504.0

        table_data: List[List[Any]] = []
        for row in tbl.rows:
            row_data: List[Any] = []
            for cell in row.cells:
                if isinstance(cell.content, list):
                    cell_flowables = [self._build_platypus_paragraph(p) for p in cell.content]
                    row_data.append(cell_flowables)
                else:
                    align_val = TA_RIGHT if cell.alignment == Alignment.RIGHT else TA_LEFT
                    style = ParagraphStyle("CellP", parent=self.styles["DocBody"], alignment=align_val, spaceAfter=2)
                    bold_text = f"<b>{cell.plain_text}</b>" if cell.bold or row.is_header else cell.plain_text
                    row_data.append(PlatypusParagraph(bold_text, style))
            table_data.append(row_data)

        # Compute column widths
        col_count = max(len(r) for r in table_data) if table_data else 1
        col_widths = None
        if tbl.col_widths and len(tbl.col_widths) == col_count:
            # Check if fractional
            if sum(tbl.col_widths) <= 1.5:
                col_widths = [w * usable_width for w in tbl.col_widths]
            else:
                col_widths = tbl.col_widths
        else:
            col_widths = [usable_width / col_count] * col_count

        p_table = PlatypusTable(table_data, colWidths=col_widths)
        t_style = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
        ]

        if tbl.bordered:
            t_style.extend(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(self.formatting.table_border_color)),
                    ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor(self.formatting.table_border_color)),
                ]
            )

        if tbl.has_header and len(table_data) > 0:
            t_style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(self.formatting.table_header_bg)))

        p_table.setStyle(TableStyle(t_style))
        return p_table

    def _build_signature_flowables(self, sig_block: SignatureBlock) -> List[Any]:
        flowables: List[Any] = []
        if sig_block.intro_text:
            flowables.append(PlatypusParagraph(sig_block.intro_text, self.styles["DocBody"]))
            flowables.append(Spacer(1, 14))

        signers = sig_block.signers
        if not signers:
            return flowables

        # Side by side table
        cells: List[Any] = []
        for signer in signers:
            lines = [
                "_____________________________________<br/>",
                f"<b>Name:</b> {signer.name}<br/>",
            ]
            if signer.title:
                lines.append(f"<b>Title:</b> {signer.title}<br/>")
            if signer.organization:
                lines.append(f"<b>Company:</b> {signer.organization}<br/>")
            if signer.date:
                lines.append(f"<b>Date:</b> {signer.date}<br/>")
            cells.append(PlatypusParagraph("".join(lines), self.styles["DocBody"]))

        col_w = 504.0 / len(signers)
        sig_table = PlatypusTable([cells], colWidths=[col_w] * len(signers))
        sig_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        flowables.append(sig_table)
        flowables.append(Spacer(1, 12))
        return flowables
