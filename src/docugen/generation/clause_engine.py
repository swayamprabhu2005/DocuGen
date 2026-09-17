"""Deterministic clause engine for DocuGen AI.

Provides modular, condition-driven clause selection and template expansion
without neural hallucination or uncontrolled text generation.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
import jinja2
from pydantic import BaseModel, Field

from docugen.core.document_ir import ClauseIR, Paragraph
from docugen.core.exceptions import ClauseError


class ClauseDefinition(BaseModel):
    """Declarative specification for a reusable document clause."""

    clause_id: str
    title: str
    category: str = "general"
    document_types: List[str] = Field(default_factory=list)
    condition_field: Optional[str] = None
    expected_value: Optional[Any] = None
    priority: int = 100  # Lower number = higher priority / earlier in document
    required: bool = False
    dependencies: List[str] = Field(default_factory=list)
    template_text: str
    version: str = "1.0.0"

    def is_applicable(self, data: Dict[str, Any]) -> bool:
        """Evaluate whether this clause applies to the given data."""
        if self.required:
            return True
        if self.condition_field is None:
            return True
        actual_value = data.get(self.condition_field)
        if self.expected_value is not None:
            return actual_value == self.expected_value
        return bool(actual_value)


class ClauseEngine:
    """Registry and resolver for document clauses."""

    def __init__(self) -> None:
        self._clauses: Dict[str, ClauseDefinition] = {}
        self._jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=False,
        )

    def register(self, clause: ClauseDefinition) -> None:
        """Register a new clause definition."""
        self._clauses[clause.clause_id] = clause

    def get(self, clause_id: str) -> Optional[ClauseDefinition]:
        """Retrieve clause definition by ID."""
        return self._clauses.get(clause_id)

    def list_clauses(self) -> List[str]:
        """List all registered clause IDs."""
        return sorted(list(self._clauses.keys()))

    def render_clause_text(self, clause_id: str, data: Dict[str, Any]) -> str:
        """Render a single clause template string using input data."""
        clause = self.get(clause_id)
        if not clause:
            raise ClauseError(f"Clause '{clause_id}' not found in registry.")
        try:
            tmpl = self._jinja_env.from_string(clause.template_text)
            return tmpl.render(**data).strip()
        except jinja2.TemplateError as exc:
            raise ClauseError(
                f"Failed to render clause '{clause_id}': {exc}"
            ) from exc

    def resolve_clauses_for_document(
        self, document_type: str, data: Dict[str, Any]
    ) -> List[ClauseIR]:
        """Resolve, sort, and render all applicable clauses for a document.

        Args:
            document_type: Document type name.
            data: Normalized document data.

        Returns:
            List[ClauseIR]: Ordered list of resolved Clause IR elements.
        """
        applicable_clauses: List[ClauseDefinition] = []

        for clause in self._clauses.values():
            if clause.document_types and document_type not in clause.document_types:
                continue
            if clause.is_applicable(data):
                applicable_clauses.append(clause)

        # Check dependencies
        selected_ids = {c.clause_id for c in applicable_clauses}
        for clause in applicable_clauses:
            for dep in clause.dependencies:
                if dep not in selected_ids:
                    raise ClauseError(
                        f"Clause '{clause.clause_id}' depends on '{dep}', which is not included."
                    )

        # Sort by priority then clause_id
        applicable_clauses.sort(key=lambda c: (c.priority, c.clause_id))

        results: List[ClauseIR] = []
        for idx, clause in enumerate(applicable_clauses, start=1):
            rendered_text = self.render_clause_text(clause.clause_id, data)
            # Break rendered text into paragraphs
            paragraphs = [
                Paragraph.from_text(p.strip())
                for p in rendered_text.split("\n\n")
                if p.strip()
            ]
            results.append(
                ClauseIR(
                    clause_id=clause.clause_id,
                    title=clause.title,
                    number=f"{idx}.0",
                    body=paragraphs,
                    category=clause.category,
                    optional=not clause.required,
                )
            )

        return results


_GLOBAL_CLAUSE_ENGINE = ClauseEngine()


def get_clause_engine() -> ClauseEngine:
    return _GLOBAL_CLAUSE_ENGINE


def _init_builtin_clauses() -> None:
    engine = _GLOBAL_CLAUSE_ENGINE

    # Employment clauses
    engine.register(
        ClauseDefinition(
            clause_id="employment_appointment",
            title="Appointment and Position",
            category="employment",
            document_types=["employment_contract"],
            priority=10,
            required=True,
            template_text=(
                "The Company hereby employs the Employee in the role of {{ job_title }}, "
                "and the Employee accepts employment upon the terms and conditions set forth herein. "
                "The Employee shall commence employment on {{ joining_date }} at {{ work_location }}."
            ),
        )
    )

    engine.register(
        ClauseDefinition(
            clause_id="employment_compensation",
            title="Compensation and Benefits",
            category="employment",
            document_types=["employment_contract"],
            priority=20,
            required=True,
            template_text=(
                "In consideration for the services rendered hereunder, the Company shall pay the Employee "
                "a base salary of {{ salary }} per {{ salary_period }}, payable in accordance with the Company's "
                "standard payroll schedule and subject to all applicable statutory deductions and tax withholdings."
            ),
        )
    )

    engine.register(
        ClauseDefinition(
            clause_id="employment_probation",
            title="Probationary Period",
            category="employment",
            document_types=["employment_contract"],
            priority=30,
            condition_field="probation_period_months",
            template_text=(
                "The Employee shall serve a probationary period of {{ probation_period_months }} month(s) from the joining date. "
                "During this probationary period, either party may terminate the employment with 7 days' written notice."
            ),
        )
    )

    engine.register(
        ClauseDefinition(
            clause_id="employment_remote_work",
            title="Remote Work Policy",
            category="employment",
            document_types=["employment_contract"],
            priority=40,
            condition_field="remote_work_allowed",
            expected_value=True,
            template_text=(
                "The Employee is permitted to perform work remotely from an approved location, provided the Employee "
                "maintains reliable internet connectivity, adheres to information security policies, and remains available "
                "during designated business hours."
            ),
        )
    )

    engine.register(
        ClauseDefinition(
            clause_id="employment_non_compete",
            title="Non-Competition Covenant",
            category="employment",
            document_types=["employment_contract"],
            priority=50,
            condition_field="non_compete",
            expected_value=True,
            template_text=(
                "During the term of employment and for a period of twelve (12) months following termination, "
                "the Employee shall not directly or indirectly engage in, perform services for, or establish any "
                "business enterprise that directly competes with the Company within the relevant geographic market."
            ),
        )
    )

    engine.register(
        ClauseDefinition(
            clause_id="employment_termination",
            title="Termination of Employment",
            category="employment",
            document_types=["employment_contract"],
            priority=60,
            required=True,
            template_text=(
                "Either party may terminate this Agreement by providing {{ notice_period_days }} days' prior written notice "
                "to the other party, or payment of base salary in lieu thereof. The Company reserves the right to terminate "
                "employment immediately for Cause without notice or severance."
            ),
        )
    )

    # NDA clauses
    engine.register(
        ClauseDefinition(
            clause_id="nda_confidentiality",
            title="Confidentiality Obligations",
            category="legal",
            document_types=["nda"],
            priority=10,
            required=True,
            template_text=(
                "The Receiving Party agrees to receive and hold all Confidential Information disclosed by the Disclosing Party "
                "in strict confidence, employing at least the same degree of care as it uses for its own confidential information, "
                "but no less than a reasonable degree of care, solely for the Purpose of {{ purpose }}."
            ),
        )
    )

    engine.register(
        ClauseDefinition(
            clause_id="nda_term",
            title="Term and Expiration",
            category="legal",
            document_types=["nda"],
            priority=20,
            required=True,
            template_text=(
                "This Agreement and the confidentiality obligations herein shall remain in effect for a period of "
                "{{ duration_years }} year(s) from the Effective Date ({{ effective_date }})."
            ),
        )
    )

    engine.register(
        ClauseDefinition(
            clause_id="nda_injunctive_relief",
            title="Injunctive Relief",
            category="legal",
            document_types=["nda"],
            priority=30,
            condition_field="remedies_injunctive_relief",
            expected_value=True,
            template_text=(
                "The Receiving Party acknowledges that unauthorized disclosure or use of Confidential Information will cause "
                "irreparable harm for which monetary damages alone would be inadequate. Accordingly, the Disclosing Party shall "
                "be entitled to seek injunctive and equitable relief without the necessity of posting bond."
            ),
        )
    )

    engine.register(
        ClauseDefinition(
            clause_id="nda_governing_law",
            title="Governing Law and Jurisdiction",
            category="legal",
            document_types=["nda", "service_agreement"],
            priority=90,
            required=True,
            template_text=(
                "This Agreement shall be governed by and construed in accordance with the laws of {{ jurisdiction }} "
                "without regard to its conflict of law principles."
            ),
        )
    )


# Initialize built-ins
_init_builtin_clauses()
