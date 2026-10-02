"""Dynamic QR code and barcode image/SVG generation utilities for DocuGen AI."""

from __future__ import annotations

import io
from typing import Optional
from PIL import Image, ImageDraw
from reportlab.graphics.barcode import createBarcodeDrawing, qr


def generate_qr_image(data: str, size: int = 160) -> Image.Image:
    """Generate a clean PIL Image QR code from string data."""
    w = qr.QrCodeWidget(data)
    w.draw()
    modules = w.qr.modules
    count = len(modules)
    border = 4
    total_grid = count + border * 2
    cell_size = max(1, size // total_grid)
    actual_size = total_grid * cell_size

    img = Image.new("RGB", (actual_size, actual_size), "white")
    draw = ImageDraw.Draw(img)

    for r, row in enumerate(modules):
        for c, is_dark in enumerate(row):
            if is_dark:
                x0 = (c + border) * cell_size
                y0 = (r + border) * cell_size
                draw.rectangle([x0, y0, x0 + cell_size - 1, y0 + cell_size - 1], fill="black")

    return img


def generate_qr_bytes(data: str, size: int = 160, format: str = "PNG") -> bytes:
    """Generate QR code as bytes (PNG)."""
    img = generate_qr_image(data, size=size)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def generate_barcode_image(
    data: str,
    barcode_type: str = "Code128",
    width: int = 240,
    height: int = 60,
) -> Image.Image:
    """Generate a 1D barcode PIL Image."""
    try:
        drawing = createBarcodeDrawing(barcode_type, value=str(data))
        bc = drawing.getContents()[0]
        decomp = bc.decompose()
    except Exception:
        # Fallback to standard Code128
        drawing = createBarcodeDrawing("Code128", value=str(data))
        bc = drawing.getContents()[0]
        decomp = bc.decompose()

    char_widths = {
        "a": 1, "b": 2, "c": 3, "d": 4,
        "A": 1, "B": 2, "C": 3, "D": 4,
    }
    total_units = sum(char_widths.get(ch, 1) for ch in decomp)
    unit_px = max(1.0, float(width - 20) / max(total_units, 1))
    img_w = int(total_units * unit_px) + 20
    img = Image.new("RGB", (img_w, height), "white")
    draw = ImageDraw.Draw(img)

    x = 10.0
    for ch in decomp:
        w_units = char_widths.get(ch, 1)
        w_px = w_units * unit_px
        if ch.isupper():
            draw.rectangle([x, 4, x + w_px, height - 12], fill="black")
        x += w_px

    return img


def generate_barcode_bytes(
    data: str,
    barcode_type: str = "Code128",
    width: int = 240,
    height: int = 60,
    format: str = "PNG",
) -> bytes:
    """Generate barcode as bytes (PNG)."""
    img = generate_barcode_image(data, barcode_type=barcode_type, width=width, height=height)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()
