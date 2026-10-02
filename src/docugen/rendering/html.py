"""HTML document renderer for DocuGen AI."""

from __future__ import annotations

import base64
import html
import logging
from pathlib import Path
from typing import Any, List, Optional

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
    TextRun,
)
from docugen.core.models import RenderResult
from docugen.rendering.barcodes import generate_barcode_bytes, generate_qr_bytes
from docugen.rendering.base import Renderer
from docugen.rendering.formatting import DocumentFormatting, get_default_formatting

logger = logging.getLogger("docugen.rendering.html")


class HtmlRenderer(Renderer):
    """Renders Document IR to a styled, responsive, print-ready HTML document."""

    def __init__(self, formatting: Optional[DocumentFormatting] = None) -> None:
        self.formatting = formatting or get_default_formatting()

    def render(self, document: Document, destination: Path) -> RenderResult:
        """Render Document IR to HTML at destination path."""
        try:
            dest_file = Path(destination)
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            html_content = self._build_html(document)
            dest_file.write_text(html_content, encoding="utf-8")

            file_size = dest_file.stat().st_size if dest_file.exists() else 0
            return RenderResult(
                success=True,
                output_path=str(dest_file.resolve()),
                format="html",
                file_size_bytes=file_size,
            )
        except Exception as exc:
            logger.exception("Error during HTML rendering: %s", exc)
            return RenderResult(
                success=False,
                output_path=str(destination),
                format="html",
                error=str(exc),
            )

    def _build_html(self, doc: Document) -> str:
        fmt = self.formatting
        title = html.escape(doc.metadata.title or "Document")

        # Watermark styling
        wm_html = ""
        if doc.watermark:
            wm_text = (doc.watermark.status or doc.watermark.text or "").strip().upper()
            if wm_text:
                wm_html = (
                    f'<div class="watermark" style="color: {doc.watermark.color}; '
                    f'opacity: {doc.watermark.opacity}; transform: rotate(-{doc.watermark.rotation}deg);">'
                    f"{html.escape(wm_text)}</div>"
                )

        # Header
        header_html = ""
        if doc.header:
            parts = [html.escape(p) for p in (doc.header.left_text, doc.header.center_text, doc.header.right_text) if p]
            if parts:
                header_html = f'<div class="header"><span>{"</span> &bull; <span>".join(parts)}</span></div>'

        # Footer
        footer_html = ""
        if doc.footer:
            parts = [html.escape(p) for p in (doc.footer.left_text, doc.footer.center_text, doc.footer.right_text) if p]
            if parts:
                footer_html = f'<div class="footer"><span>{"</span> &bull; <span>".join(parts)}</span></div>'

        # Render sections
        body_parts = []
        for section in doc.sections:
            body_parts.append(self._render_section(section))

        content_body = "\n".join(body_parts)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    @page {{
      margin: {fmt.margin_top}pt {fmt.margin_right}pt {fmt.margin_bottom}pt {fmt.margin_left}pt;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: {fmt.primary_color};
      background: #f8fafc;
      margin: 0;
      padding: 24px;
      line-height: {fmt.line_spacing};
    }}
    .document-page {{
      position: relative;
      background: #ffffff;
      max-width: 820px;
      margin: 0 auto;
      padding: {fmt.margin_top}pt {fmt.margin_right}pt {fmt.margin_bottom}pt {fmt.margin_left}pt;
      box-shadow: 0 4px 14px rgba(0,0,0,0.08);
      border-radius: 4px;
      overflow: hidden;
    }}
    .watermark {{
      position: absolute;
      top: 45%;
      left: 15%;
      width: 70%;
      text-align: center;
      font-size: 54pt;
      font-weight: 900;
      pointer-events: none;
      user-select: none;
      z-index: 0;
    }}
    .content-layer {{
      position: relative;
      z-index: 1;
    }}
    .header {{
      border-bottom: 1px solid {fmt.table_border_color};
      padding-bottom: 8px;
      margin-bottom: 24px;
      font-size: 9pt;
      color: {fmt.secondary_color};
      display: flex;
      justify-content: space-between;
    }}
    .footer {{
      border-top: 1px solid {fmt.table_border_color};
      padding-top: 8px;
      margin-top: 32px;
      font-size: 9pt;
      color: {fmt.secondary_color};
      text-align: center;
    }}
    h1 {{
      font-size: {fmt.heading1_size}pt;
      color: {fmt.primary_color};
      border-bottom: 2px solid {fmt.primary_color};
      padding-bottom: 6px;
      margin-top: 24px;
      margin-bottom: 14px;
    }}
    h2 {{
      font-size: {fmt.heading2_size}pt;
      color: {fmt.primary_color};
      margin-top: 18px;
      margin-bottom: 8px;
    }}
    h3 {{
      font-size: {fmt.heading3_size}pt;
      color: {fmt.primary_color};
      margin-top: 14px;
      margin-bottom: 6px;
    }}
    p {{
      font-size: {fmt.body_size}pt;
      margin-top: 0;
      margin-bottom: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
      font-size: 9.5pt;
    }}
    th, td {{
      padding: 7px 10px;
      text-align: left;
      vertical-align: top;
    }}
    table.bordered th, table.bordered td {{
      border: 1px solid {fmt.table_border_color};
    }}
    th {{
      background: {fmt.table_header_bg};
      color: {fmt.table_header_color};
      font-weight: 600;
    }}
    .signature-block {{
      display: flex;
      justify-content: space-between;
      margin-top: 32px;
      gap: 20px;
    }}
    .signer-box {{
      flex: 1;
      border-top: 1px solid {fmt.primary_color};
      padding-top: 8px;
      margin-top: 40px;
    }}
    .qr-box, .barcode-box {{
      text-align: center;
      margin: 16px 0;
    }}
    .qr-box img, .barcode-box img {{
      display: inline-block;
      border: 1px solid #e2e8f0;
      padding: 4px;
      background: white;
      border-radius: 4px;
    }}
    .barcode-caption {{
      font-size: 8.5pt;
      color: {fmt.secondary_color};
      margin-top: 4px;
    }}
    @media print {{
      body {{ background: transparent; padding: 0; }}
      .document-page {{ box-shadow: none; border-radius: 0; max-width: 100%; padding: 0; }}
      .page-break {{ page-break-after: always; }}
    }}
  </style>
</head>
<body>
  <div class="document-page">
    {wm_html}
    <div class="content-layer">
      {header_html}
      {content_body}
      {footer_html}
    </div>
  </div>
</body>
</html>
"""

    def _render_section(self, section: Section) -> str:
        parts = []
        if section.title:
            parts.append(f"<h1>{html.escape(section.title)}</h1>")

        for elem in section.elements:
            parts.append(self._render_element(elem))

        for sub in section.subsections:
            if sub.title:
                parts.append(f"<h2>{html.escape(sub.title)}</h2>")
            for elem in sub.elements:
                parts.append(self._render_element(elem))

        return "\n".join(parts)

    def _render_element(self, elem: BlockElement) -> str:
        if isinstance(elem, Heading):
            tag = f"h{min(elem.level, 4)}"
            align = f" style='text-align: {elem.alignment.value};'" if elem.alignment != Alignment.LEFT else ""
            return f"<{tag}{align}>{html.escape(elem.text)}</{tag}>"

        elif isinstance(elem, Paragraph):
            return self._render_paragraph(elem)

        elif isinstance(elem, ClauseIR):
            title = f"{elem.number or ''} {elem.title}".strip()
            paras = "".join(self._render_paragraph(p) for p in elem.body)
            return f"<div class='clause'><h2>{html.escape(title)}</h2>{paras}</div>"

        elif isinstance(elem, ListBlock):
            tag = "ol" if elem.ordered else "ul"
            items_html = "".join(f"<li>{self._runs_to_html(it.runs)}</li>" for it in elem.items)
            return f"<{tag}>{items_html}</{tag}>"

        elif isinstance(elem, Table):
            return self._render_table(elem)

        elif isinstance(elem, SignatureBlock):
            return self._render_signature_block(elem)

        elif isinstance(elem, QRCodeElement):
            qr_bytes = generate_qr_bytes(elem.data, size=int(elem.size * 2))
            b64_qr = base64.b64encode(qr_bytes).decode("ascii")
            cap_html = f"<div class='barcode-caption'>{html.escape(elem.caption)}</div>" if elem.caption else ""
            return f"""<div class='qr-box'><img src="data:image/png;base64,{b64_qr}" width="{elem.size}" height="{elem.size}" alt="QR Code">{cap_html}</div>"""

        elif isinstance(elem, BarcodeElement):
            bc_bytes = generate_barcode_bytes(
                elem.data,
                barcode_type=elem.barcode_type,
                width=int(elem.width * 2),
                height=int(elem.height * 2),
            )
            b64_bc = base64.b64encode(bc_bytes).decode("ascii")
            cap_html = f"<div class='barcode-caption'>{html.escape(elem.caption)}</div>" if elem.caption else ""
            return f"""<div class='barcode-box'><img src="data:image/png;base64,{b64_bc}" width="{elem.width}" height="{elem.height}" alt="Barcode">{cap_html}</div>"""

        elif isinstance(elem, PageBreak):
            return '<div class="page-break" style="page-break-after: always; height: 1px;"></div>'

        return ""

    def _render_paragraph(self, para: Paragraph) -> str:
        align = f"text-align: {para.alignment.value};" if para.alignment != Alignment.LEFT else ""
        space = f"margin-bottom: {para.space_after}pt;"
        style_attr = f" style='{align} {space}'".strip()
        inner = self._runs_to_html(para.runs)
        return f"<p{style_attr}>{inner}</p>"

    def _runs_to_html(self, runs: List[TextRun]) -> str:
        parts = []
        for r in runs:
            text = html.escape(r.text)
            styles = []
            if r.bold:
                text = f"<strong>{text}</strong>"
            if r.italic:
                text = f"<em>{text}</em>"
            if r.underline:
                styles.append("text-decoration: underline;")
            if r.color:
                styles.append(f"color: {r.color};")
            if r.font_size:
                styles.append(f"font-size: {r.font_size}pt;")
            if styles:
                text = f"<span style='{' '.join(styles)}'>{text}</span>"
            parts.append(text)
        return "".join(parts) or "&nbsp;"

    def _render_table(self, tbl: Table) -> str:
        bordered = "bordered" if tbl.bordered else ""
        rows_html = []
        for r in tbl.rows:
            tag = "th" if r.is_header else "td"
            cell_strs = []
            for c in r.cells:
                bold_open = "<strong>" if c.bold else ""
                bold_close = "</strong>" if c.bold else ""
                align = f" style='text-align: {c.alignment.value};'" if c.alignment != Alignment.LEFT else ""
                content = html.escape(c.plain_text)
                cell_strs.append(f"<{tag}{align}>{bold_open}{content}{bold_close}</{tag}>")
            rows_html.append(f"<tr>{''.join(cell_strs)}</tr>")

        return f"<table class='{bordered}'>{''.join(rows_html)}</table>"

    def _render_signature_block(self, sig: SignatureBlock) -> str:
        intro = f"<p style='margin-bottom: 24px; font-weight: 500;'>{html.escape(sig.intro_text)}</p>" if sig.intro_text else ""
        boxes = []
        for s in sig.signers:
            name = html.escape(s.name)
            title = f"<br><span style='font-size: 9pt; color: #64748b;'>{html.escape(s.title)}</span>" if s.title else ""
            date = f"<br><span style='font-size: 8.5pt; color: #94a3b8;'>Date: {html.escape(s.date)}</span>" if s.date else ""
            boxes.append(f"<div class='signer-box'><strong>{name}</strong>{title}{date}</div>")

        return f"{intro}<div class='signature-block'>{''.join(boxes)}</div>"
