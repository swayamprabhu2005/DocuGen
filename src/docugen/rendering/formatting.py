"""Centralized formatting and styling configuration for DocuGen AI."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class DocumentFormatting(BaseModel):
    """Visual style and layout specifications for document rendering."""

    page_size: Literal["A4", "LETTER", "LEGAL"] = "LETTER"
    orientation: Literal["portrait", "landscape"] = "portrait"

    # Margins in points (72 points = 1 inch)
    margin_top: float = 54.0     # 0.75 in
    margin_bottom: float = 54.0  # 0.75 in
    margin_left: float = 54.0    # 0.75 in
    margin_right: float = 54.0   # 0.75 in

    # Typography
    font_family: str = "Helvetica"
    heading_font_family: str = "Helvetica-Bold"
    primary_color: str = "#1E3A8A"     # Deep corporate blue
    secondary_color: str = "#4B5563"   # Slate gray
    text_color: str = "#1F2937"        # Charcoal
    light_bg: str = "#F9FAFB"          # Cool gray background

    # Sizes in points
    heading1_size: float = 20.0
    heading2_size: float = 14.0
    heading3_size: float = 12.0
    body_size: float = 10.0
    caption_size: float = 8.5
    line_spacing: float = 1.25

    # Tables
    table_header_bg: str = "#F3F4F6"
    table_header_color: str = "#111827"
    table_border_color: str = "#D1D5DB"
    table_stripe_bg: str = "#F9FAFB"


_DEFAULT_FORMATTING = DocumentFormatting()


def get_default_formatting() -> DocumentFormatting:
    return _DEFAULT_FORMATTING
