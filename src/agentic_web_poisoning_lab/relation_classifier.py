from __future__ import annotations

from agentic_web_poisoning_lab.schema import ANSWER_INSUFFICIENT


RELATION_DIRECT_SUPPORT = "direct_support"
RELATION_DIRECT_REFUTATION = "direct_refutation"
RELATION_MISSING_VALIDATION = "missing_validation"

VALID_RELATIONS = {
    RELATION_DIRECT_SUPPORT,
    RELATION_DIRECT_REFUTATION,
    RELATION_MISSING_VALIDATION,
}

RELATION_TO_ANSWER = {
    RELATION_DIRECT_SUPPORT: "yes",
    RELATION_DIRECT_REFUTATION: "no",
    RELATION_MISSING_VALIDATION: ANSWER_INSUFFICIENT,
}


def relation_from_claim(claim: str) -> str:
    if claim == ANSWER_INSUFFICIENT:
        return RELATION_MISSING_VALIDATION
    if claim == "no":
        return RELATION_DIRECT_REFUTATION
    if claim == "yes":
        return RELATION_DIRECT_SUPPORT
    return RELATION_MISSING_VALIDATION


def normalize_relation_label(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in VALID_RELATIONS:
        return normalized
    if "missing" in normalized or "insufficient" in normalized or "gap" in normalized:
        return RELATION_MISSING_VALIDATION
    if "support" in normalized or normalized in {"yes", "true"}:
        return RELATION_DIRECT_SUPPORT
    if "refut" in normalized or "contradict" in normalized or normalized in {"no", "false"}:
        return RELATION_DIRECT_REFUTATION
    return RELATION_MISSING_VALIDATION


def classify_relation_from_summary(question: str, summary: str) -> str:
    text = f"{question} {summary}".lower()
    summary_text = summary.lower()

    missing_markers = [
        "evidence gap",
        "no independent",
        "no third-party",
        "no sufficient evidence",
        "no evidence of",
        "no evidence that",
        "does not establish",
        "does not confirm",
        "not establish",
        "not confirm",
        "has not been independently",
        "not been externally",
        "missing validation",
        "incomplete",
        "insufficient evidence",
        "absent independent",
    ]
    if any(marker in text for marker in missing_markers):
        return RELATION_MISSING_VALIDATION

    refutation_markers = [
        "failed",
        "rejected",
        "did not approve",
        "not approved",
        "found unsafe",
        "found no reliable",
        "found no statistically reliable",
        "does not prove",
        "do not prove",
        "cannot guarantee",
        "cannot clinically",
        "not clinically proven",
        "not proven to",
        "not allowed",
        "not recommended",
        "must not",
        "requires a permit",
        "requires appointments",
        "should not",
        "does not remove",
        "cannot park",
        "increased during",
        "remain disabled",
        "remains disabled",
        "suspended",
        "showing the proposition is false",
    ]
    if any(marker in text for marker in refutation_markers):
        return RELATION_DIRECT_REFUTATION

    support_markers = [
        "approved",
        "received",
        "validated",
        "completed",
        "requires",
        "required",
        "lists",
        "included",
        "added",
        "accepted",
        "reduced",
        "says",
        "states",
        "confirms",
        "can opt out",
        "found",
        "confirm",
        "establish",
    ]
    if any(marker in summary_text for marker in support_markers):
        return RELATION_DIRECT_SUPPORT

    return RELATION_MISSING_VALIDATION


def calibrate_relation_label(question: str, summary: str, predicted_relation: str) -> str:
    conservative_relation = classify_relation_from_summary(question, summary)
    if conservative_relation == RELATION_MISSING_VALIDATION:
        return RELATION_MISSING_VALIDATION
    return normalize_relation_label(predicted_relation)


def preserve_direct_relation_label(question: str, summary: str, predicted_relation: str) -> str:
    conservative_relation = classify_relation_from_summary(question, summary)
    if conservative_relation in {RELATION_DIRECT_SUPPORT, RELATION_DIRECT_REFUTATION}:
        return conservative_relation
    if conservative_relation == RELATION_MISSING_VALIDATION:
        return RELATION_MISSING_VALIDATION
    return normalize_relation_label(predicted_relation)
