"""Hybrid document classification resolver."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from docugen.classification.ml import MLDocumentClassifier
from docugen.classification.rules import rule_based_classify
from docugen.core.models import ClassificationResult
from docugen.core.schema_registry import get_schema, list_document_types

_OPTIONAL_ML_CLASSIFIER = MLDocumentClassifier()


def classify_document(
    data: Dict[str, Any],
    explicit_type: Optional[str] = None,
    ml_classifier: Optional[MLDocumentClassifier] = None,
) -> ClassificationResult:
    """Classify input data to determine its most probable document type.

    Classification Priority:
        1. Explicitly provided template or document_type
        2. Exact schema match (satisfies 100% of required fields)
        3. Rule-based heuristic scoring
        4. Optional ML classifier
        5. Ambiguous resolution with ranked candidates

    Args:
        data: Input data dictionary.
        explicit_type: Explicitly requested document type if known.
        ml_classifier: Optional pre-trained ML classifier instance.

    Returns:
        ClassificationResult: Structured resolution result.
    """
    # 1. Explicit document type
    if explicit_type:
        return ClassificationResult(
            document_type=explicit_type.strip().lower(),
            confidence=1.0,
            method="explicit",
            ambiguous=False,
            candidates=[{"document_type": explicit_type, "score": 1.0}],
        )

    # 2. Schema required-fields matching
    schema_matches: List[Dict[str, Any]] = []
    keys = {k.strip().lower() for k in data.keys()}

    for doc_type in list_document_types():
        try:
            schema = get_schema(doc_type)
            req_fields = schema.get_required_field_names()
            if not req_fields:
                continue

            # Check aliases as well
            alias_map = schema.get_field_aliases_map()
            effective_keys = set(keys)
            for k in keys:
                if k in alias_map:
                    effective_keys.add(alias_map[k])

            matched = [f for f in req_fields if f in effective_keys]
            ratio = len(matched) / len(req_fields)
            if ratio == 1.0:
                schema_matches.append({"document_type": doc_type, "score": 1.0, "method": "schema_match"})
            elif ratio >= 0.6:
                schema_matches.append(
                    {"document_type": doc_type, "score": round(ratio * 0.9, 2), "method": "schema_match"}
                )
        except Exception:
            continue

    # If single exact schema match (ratio == 1.0)
    exact_matches = [m for m in schema_matches if m["score"] == 1.0]
    if len(exact_matches) == 1:
        return ClassificationResult(
            document_type=exact_matches[0]["document_type"],
            confidence=0.98,
            method="schema_match",
            ambiguous=False,
            candidates=schema_matches,
        )

    # 3. Rule-based heuristic scoring
    rule_scores = rule_based_classify(data)
    candidates: List[Dict[str, Any]] = []

    for dt, score in rule_scores:
        candidates.append({"document_type": dt, "score": score, "method": "rule_based"})

    # Combine schema and rule candidates
    for sm in schema_matches:
        if not any(c["document_type"] == sm["document_type"] for c in candidates):
            candidates.append(sm)

    candidates.sort(key=lambda x: x["score"], reverse=True)

    # 4. Optional ML Classifier
    clf = ml_classifier or _OPTIONAL_ML_CLASSIFIER
    if clf.is_trained:
        ml_pred = clf.predict(data)
        if ml_pred:
            ml_type, ml_conf = ml_pred
            if ml_conf >= 0.75:
                return ClassificationResult(
                    document_type=ml_type,
                    confidence=ml_conf,
                    method="ml",
                    ambiguous=False,
                    candidates=[{"document_type": ml_type, "score": ml_conf, "method": "ml"}],
                )

    if not candidates:
        return ClassificationResult(
            document_type=None,
            confidence=0.0,
            method="ambiguous",
            ambiguous=True,
            candidates=[],
        )

    top_candidate = candidates[0]

    # Check for ambiguity (second candidate within 0.1 score of top candidate)
    if len(candidates) > 1 and (candidates[0]["score"] - candidates[1]["score"]) < 0.15:
        return ClassificationResult(
            document_type=top_candidate["document_type"],
            confidence=top_candidate["score"],
            method="ambiguous",
            ambiguous=True,
            candidates=candidates,
        )

    if top_candidate["score"] >= 0.6:
        return ClassificationResult(
            document_type=top_candidate["document_type"],
            confidence=top_candidate["score"],
            method=top_candidate.get("method", "rule_based"),
            ambiguous=False,
            candidates=candidates,
        )

    return ClassificationResult(
        document_type=None,
        confidence=top_candidate["score"],
        method="ambiguous",
        ambiguous=True,
        candidates=candidates,
    )
