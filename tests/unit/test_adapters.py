"""Tests for input adapters."""

import json
from dataclasses import dataclass
from pathlib import Path
import pytest
from pydantic import BaseModel

from docugen.core.exceptions import AdapterError
from docugen.input.adapters import adapt_input


class PydanticPerson(BaseModel):
    name: str
    age: int


@dataclass
class DataclassPerson:
    name: str
    age: int


def test_adapt_dict():
    data = {"name": "Alice", "role": "Engineer"}
    result = adapt_input(data)
    assert result == data
    assert result is not data  # returns copy


def test_adapt_pydantic():
    model = PydanticPerson(name="Bob", age=30)
    result = adapt_input(model)
    assert result == {"name": "Bob", "age": 30}


def test_adapt_dataclass():
    dc = DataclassPerson(name="Charlie", age=28)
    result = adapt_input(dc)
    assert result == {"name": "Charlie", "age": 28}


def test_adapt_json_string():
    json_str = '{"company": "Apex Inc", "employees": 50}'
    result = adapt_input(json_str)
    assert result == {"company": "Apex Inc", "employees": 50}


def test_adapt_json_file(tmp_path: Path):
    file_path = tmp_path / "data.json"
    file_path.write_text(json.dumps({"project": "DocuGen", "version": "0.1.0"}), encoding="utf-8")

    result = adapt_input(file_path)
    assert result == {"project": "DocuGen", "version": "0.1.0"}

    # Also test passing str of file path
    result_str = adapt_input(str(file_path))
    assert result_str == {"project": "DocuGen", "version": "0.1.0"}


def test_adapt_invalid_input():
    with pytest.raises(AdapterError):
        adapt_input(None)

    with pytest.raises(AdapterError):
        adapt_input(12345)

    with pytest.raises(AdapterError):
        adapt_input("non_existent_file_and_not_json.txt")
