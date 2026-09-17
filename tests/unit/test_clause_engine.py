"""Tests for Clause Engine."""

import pytest
from docugen.core.exceptions import ClauseError
from docugen.generation.clause_engine import (
    ClauseDefinition,
    ClauseEngine,
    get_clause_engine,
)


def test_clause_engine_condition_and_rendering():
    engine = ClauseEngine()

    engine.register(
        ClauseDefinition(
            clause_id="c_remote",
            title="Remote Work",
            document_types=["employment"],
            condition_field="remote_allowed",
            expected_value=True,
            priority=20,
            template_text="Employee {{ name }} is allowed to work remotely.",
        )
    )
    engine.register(
        ClauseDefinition(
            clause_id="c_base",
            title="Base Duty",
            document_types=["employment"],
            priority=10,
            required=True,
            template_text="Employee {{ name }} must perform assigned duties.",
        )
    )

    # 1. Test when remote_allowed is True
    data_remote = {"name": "Alice", "remote_allowed": True}
    clauses = engine.resolve_clauses_for_document("employment", data_remote)
    assert len(clauses) == 2
    # Check ordering by priority
    assert clauses[0].clause_id == "c_base"
    assert clauses[1].clause_id == "c_remote"
    assert "Alice" in clauses[0].body[0].plain_text

    # 2. Test when remote_allowed is False
    data_no_remote = {"name": "Bob", "remote_allowed": False}
    clauses_no_remote = engine.resolve_clauses_for_document("employment", data_no_remote)
    assert len(clauses_no_remote) == 1
    assert clauses_no_remote[0].clause_id == "c_base"


def test_clause_dependency():
    engine = ClauseEngine()
    engine.register(
        ClauseDefinition(
            clause_id="clause_a",
            title="Clause A",
            document_types=["doc_x"],
            priority=10,
            template_text="Text A",
        )
    )
    engine.register(
        ClauseDefinition(
            clause_id="clause_b",
            title="Clause B",
            document_types=["doc_x"],
            dependencies=["clause_a"],
            priority=20,
            template_text="Text B",
        )
    )

    # Both selected: valid
    res = engine.resolve_clauses_for_document("doc_x", {})
    assert len(res) == 2

    # Unmet dependency
    engine_unmet = ClauseEngine()
    engine_unmet.register(
        ClauseDefinition(
            clause_id="clause_dep_missing",
            title="B",
            dependencies=["non_existent_clause"],
            template_text="Text B",
        )
    )
    with pytest.raises(ClauseError):
        engine_unmet.resolve_clauses_for_document("any", {})
