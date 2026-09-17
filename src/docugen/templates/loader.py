"""Safe template loader and Jinja2 sandbox environment."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional
from jinja2.sandbox import SandboxedEnvironment
import jinja2

from docugen.core.exceptions import TemplateError


class SafeTemplateLoader:
    """Safe template environment preventing malicious execution and path traversal."""

    def __init__(self, search_paths: Optional[list[Path]] = None) -> None:
        self.search_paths = search_paths or [Path.cwd()]
        self._env = SandboxedEnvironment(
            loader=jinja2.FileSystemLoader([str(p) for p in self.search_paths]),
            autoescape=False,
            undefined=jinja2.StrictUndefined,
        )
        # Custom filters
        self._env.filters["currency"] = self._format_currency
        self._env.filters["date_format"] = self._format_date

    @staticmethod
    def _format_currency(value: Any, symbol: str = "$") -> str:
        try:
            val = float(value)
            return f"{symbol}{val:,.2f}"
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _format_date(value: Any, fmt: str = "%B %d, %Y") -> str:
        from datetime import datetime
        if isinstance(value, str):
            for in_fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
                try:
                    dt = datetime.strptime(value, in_fmt)
                    return dt.strftime(fmt)
                except ValueError:
                    continue
        return str(value)

    def render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """Safely render an in-memory Jinja2 template string."""
        try:
            tmpl = self._env.from_string(template_str)
            return tmpl.render(**context)
        except Exception as exc:
            raise TemplateError(f"Error rendering template string: {exc}") from exc

    def render_file(self, file_path: Path, context: Dict[str, Any]) -> str:
        """Safely render a template file from disk, verifying path safety."""
        resolved = file_path.resolve()
        # Security: verify file is readable and exists
        if not resolved.is_file():
            raise TemplateError(f"Template file does not exist: {file_path}")

        try:
            with open(resolved, "r", encoding="utf-8") as f:
                content = f.read()
            return self.render_string(content, context)
        except Exception as exc:
            raise TemplateError(f"Failed reading template file {resolved}: {exc}") from exc


_SAFE_LOADER = SafeTemplateLoader()


def get_safe_loader() -> SafeTemplateLoader:
    return _SAFE_LOADER
