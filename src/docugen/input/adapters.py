"""Input adapters for DocuGen AI.

Normalizes diverse input formats (Python dictionaries, JSON strings, JSON files,
Pydantic models, dataclasses) into standard Python dictionaries.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any, Dict, Union

from docugen.core.exceptions import AdapterError


def adapt_input(data: Any) -> Dict[str, Any]:
    """Adapt any supported input format into a dictionary.

    Supported inputs:
    - dict
    - JSON string (e.g. '{"key": "value"}')
    - JSON file path (str or Path)
    - Pydantic BaseModel instance (v1 or v2)
    - dataclass instance

    Returns:
        Dict[str, Any]: Standardized Python dictionary.

    Raises:
        AdapterError: If input data cannot be adapted.
    """
    if data is None:
        raise AdapterError("Input data cannot be None.")

    # 1. Direct dictionary
    if isinstance(data, dict):
        return dict(data)

    # 2. Pydantic model (v2 model_dump or v1 dict)
    if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
        return data.model_dump()
    if hasattr(data, "dict") and callable(getattr(data, "dict")):
        return data.dict()

    # 3. Dataclass instance
    if dataclasses.is_dataclass(data) and not isinstance(data, type):
        return dataclasses.asdict(data)

    # 4. Path object pointing to a JSON file
    if isinstance(data, Path):
        if not data.exists():
            raise AdapterError(f"Input file path does not exist: {data}")
        try:
            with open(data, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if not isinstance(loaded, dict):
                    raise AdapterError(f"JSON file {data} did not contain a JSON object (dict).")
                return loaded
        except json.JSONDecodeError as exc:
            raise AdapterError(f"Failed to parse JSON file {data}: {exc}") from exc
        except Exception as exc:
            raise AdapterError(f"Failed to read input file {data}: {exc}") from exc

    # 5. String: could be file path or JSON string
    if isinstance(data, str):
        trimmed = data.strip()
        # Check if it looks like JSON string
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]")):
            try:
                loaded = json.loads(trimmed)
                if not isinstance(loaded, dict):
                    raise AdapterError("JSON string did not contain a JSON object.")
                return loaded
            except json.JSONDecodeError as exc:
                raise AdapterError(f"Invalid JSON string provided: {exc}") from exc

        # Check if it's an existing file path
        path_candidate = Path(trimmed)
        if path_candidate.is_file():
            return adapt_input(path_candidate)

        raise AdapterError("String input was neither a valid JSON string nor an existing file path.")

    raise AdapterError(
        f"Unsupported input type '{type(data).__name__}'. Expected dict, JSON string/file, Pydantic model, or dataclass."
    )
