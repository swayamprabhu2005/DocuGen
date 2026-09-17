"""CLI integration tests."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(*args, cwd=None):
    """Helper to run the docugen CLI and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, "-m", "docugen.cli.main", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )
    return result.returncode, result.stdout, result.stderr


def test_cli_help():
    code, out, err = run_cli("--help")
    assert code == 0
    assert "docugen" in out.lower() or "usage" in out.lower()


def test_cli_list_templates():
    code, out, err = run_cli("templates", "list")
    assert code == 0, f"CLI templates list failed:\n{err}"
    assert "employment_contract" in out
    assert "nda" in out
    assert "invoice" in out


def test_cli_list_document_types():
    code, out, err = run_cli("document-types", "list")
    assert code == 0, f"CLI document-types list failed:\n{err}"
    assert "employment_contract" in out


def test_cli_schemas_list():
    code, out, err = run_cli("schemas", "list")
    assert code == 0
    assert "employment_contract" in out


def test_cli_schemas_show():
    code, out, err = run_cli("schemas", "show", "employment_contract")
    assert code == 0, f"Schema show failed:\n{err}"
    assert "employee_name" in out or "fields" in out


def test_cli_validate(tmp_path):
    """CLI validate command with a valid data JSON file."""
    data_file = tmp_path / "emp_data.json"
    data_file.write_text(
        json.dumps(
            {
                "employee_name": "Alice Smith",
                "company_name": "TechCorp Ltd",
                "salary": 90000,
                "joining_date": "2026-10-01",
            }
        )
    )
    code, out, err = run_cli("validate", "--template", "employment_contract", "--data", str(data_file))
    assert code == 0, f"CLI validate failed:\n{err}\n{out}"
    assert "valid" in out.lower() or "pass" in out.lower() or "✓" in out or "OK" in out


def test_cli_generate_pdf(tmp_path):
    """CLI generate command produces a PDF file."""
    data_file = tmp_path / "emp_data.json"
    out_file = tmp_path / "contract.pdf"
    data_file.write_text(
        json.dumps(
            {
                "employee_name": "Charlie Brown",
                "company_name": "InnovateCo",
                "salary": 75000,
                "joining_date": "2026-11-01",
            }
        )
    )
    code, out, err = run_cli(
        "generate",
        "--template",
        "employment_contract",
        "--data",
        str(data_file),
        "--output",
        str(out_file),
        "--format",
        "pdf",
    )
    assert code == 0, f"CLI generate PDF failed:\n{err}\n{out}"
    assert out_file.exists(), f"PDF output not found at {out_file}"
    assert out_file.stat().st_size > 1000


def test_cli_generate_docx(tmp_path):
    """CLI generate command produces a DOCX file."""
    data_file = tmp_path / "emp_data.json"
    out_file = tmp_path / "contract.docx"
    data_file.write_text(
        json.dumps(
            {
                "employee_name": "Diana Prince",
                "company_name": "Atlas Global",
                "salary": 125000,
                "joining_date": "2026-12-01",
            }
        )
    )
    code, out, err = run_cli(
        "generate",
        "--template",
        "employment_contract",
        "--data",
        str(data_file),
        "--output",
        str(out_file),
        "--format",
        "docx",
    )
    assert code == 0, f"CLI generate DOCX failed:\n{err}\n{out}"
    assert out_file.exists()
    assert out_file.stat().st_size > 5000


def test_cli_validate_invalid_data(tmp_path):
    """CLI validate should exit non-zero for invalid data."""
    data_file = tmp_path / "bad_data.json"
    data_file.write_text(json.dumps({"salary": "not_a_number"}))
    code, out, err = run_cli("validate", "--template", "employment_contract", "--data", str(data_file))
    assert code != 0, "Expected non-zero exit code for invalid data"


def test_cli_generate_invalid_format(tmp_path):
    """CLI generate should error on unsupported format."""
    data_file = tmp_path / "emp.json"
    data_file.write_text(
        json.dumps({"employee_name": "X", "company_name": "Y", "salary": 1, "joining_date": "2026-01-01"})
    )
    code, out, err = run_cli(
        "generate",
        "--template",
        "employment_contract",
        "--data",
        str(data_file),
        "--output",
        str(tmp_path / "out.html"),
        "--format",
        "html",
    )
    assert code != 0
