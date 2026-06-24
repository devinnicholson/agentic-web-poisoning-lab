from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ANSWER_YES = "yes"
ANSWER_NO = "no"
ANSWER_INSUFFICIENT = "insufficient_evidence"

VALID_ANSWERS = {ANSWER_YES, ANSWER_NO, ANSWER_INSUFFICIENT}


@dataclass(frozen=True)
class TaskCase:
    id: str
    question: str
    expected_answer: str
    required_page_ids: list[str]
    attack_page_ids: list[str]
    attack_type: str | None
    attack_target_answer: str | None

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "TaskCase":
        expected_answer = str(row["expected_answer"])
        if expected_answer not in VALID_ANSWERS:
            raise ValueError(f"Invalid expected_answer for {row.get('id')}: {expected_answer}")
        attack_target = row.get("attack_target_answer")
        if attack_target is not None and str(attack_target) not in VALID_ANSWERS:
            raise ValueError(f"Invalid attack_target_answer for {row.get('id')}: {attack_target}")
        return cls(
            id=str(row["id"]),
            question=str(row["question"]),
            expected_answer=expected_answer,
            required_page_ids=[str(item) for item in row["required_page_ids"]],
            attack_page_ids=[str(item) for item in row["attack_page_ids"]],
            attack_type=str(row["attack_type"]) if row.get("attack_type") else None,
            attack_target_answer=str(attack_target) if attack_target is not None else None,
        )


@dataclass(frozen=True)
class WebPage:
    id: str
    title: str
    url: str
    source_type: str
    trust_label: str
    freshness: str
    is_poisoned: bool
    attack_type: str | None
    summary: str
    supports_tasks: dict[str, str]

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "WebPage":
        return cls(
            id=str(row["id"]),
            title=str(row["title"]),
            url=str(row["url"]),
            source_type=str(row["source_type"]),
            trust_label=str(row["trust_label"]),
            freshness=str(row["freshness"]),
            is_poisoned=bool(row["is_poisoned"]),
            attack_type=str(row["attack_type"]) if row.get("attack_type") else None,
            summary=str(row["summary"]),
            supports_tasks={str(key): str(value) for key, value in row["supports_tasks"].items()},
        )


@dataclass(frozen=True)
class Condition:
    id: str
    name: str
    browse: bool
    source_ranking: bool
    prompt_shields: bool
    trust_filter: bool
    citation_validation: bool
    abstain_on_conflict: bool
    strict_abstention: bool = False
    relation_verifier: bool = False
    structured_relation_gate: bool = False
    relation_classifier_gate: bool = False
    calibrated_relation_classifier_gate: bool = False


@dataclass(frozen=True)
class AgentAnswer:
    answer: str
    conclusion: str
    citations: list[str]
    refused: bool = False
    action_safe: bool = True


@dataclass(frozen=True)
class RunResult:
    run_id: str
    task_id: str
    question: str
    condition: str
    expected_answer: str
    actual_answer: str
    attack_type: str | None
    attack_target_answer: str | None
    visited_page_ids: list[str]
    selected_page_ids: list[str]
    cited_page_ids: list[str]
    filtered_page_ids: list[str]
    answer: dict[str, Any]
    safety_flags: dict[str, Any]
    metrics: dict[str, Any]
    latency_ms: int
    estimated_cost_usd: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "task_id": self.task_id,
            "question": self.question,
            "condition": self.condition,
            "expected_answer": self.expected_answer,
            "actual_answer": self.actual_answer,
            "attack_type": self.attack_type,
            "attack_target_answer": self.attack_target_answer,
            "visited_page_ids": self.visited_page_ids,
            "selected_page_ids": self.selected_page_ids,
            "cited_page_ids": self.cited_page_ids,
            "filtered_page_ids": self.filtered_page_ids,
            "answer": self.answer,
            "safety_flags": self.safety_flags,
            "metrics": self.metrics,
            "latency_ms": self.latency_ms,
            "estimated_cost_usd": self.estimated_cost_usd,
        }
