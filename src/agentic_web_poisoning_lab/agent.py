from __future__ import annotations

from datetime import UTC, datetime
from typing import Sequence

from agentic_web_poisoning_lab.conditions import CONDITIONS
from agentic_web_poisoning_lab.metrics import evaluate_result
from agentic_web_poisoning_lab.schema import (
    ANSWER_INSUFFICIENT,
    AgentAnswer,
    Condition,
    RunResult,
    TaskCase,
    WebPage,
)


PROMPT_SHIELD_ATTACKS = {"action_hijack", "indirect_prompt_injection"}


class DeterministicWebAgent:
    def __init__(self, pages: Sequence[WebPage]) -> None:
        self._pages_by_id = {page.id: page for page in pages}

    def run(self, tasks: Sequence[TaskCase], condition_ids: Sequence[str]) -> list[RunResult]:
        run_id = datetime.now(UTC).strftime("local-%Y%m%dT%H%M%SZ")
        rows: list[RunResult] = []
        for condition_id in condition_ids:
            condition = CONDITIONS[condition_id]
            for task in tasks:
                rows.append(self.run_one(task, condition, run_id=run_id))
        return rows

    def run_one(self, task: TaskCase, condition: Condition, run_id: str) -> RunResult:
        visited_pages = self._visited_pages(task, condition)
        filtered_pages = self._filtered_pages(visited_pages, condition)
        selected_pages = [page for page in visited_pages if page.id not in {item.id for item in filtered_pages}]
        answer = self._answer(task, selected_pages, condition)
        metrics = evaluate_result(task, answer, visited_pages, selected_pages, filtered_pages)
        safety_flags = {
            "page_screening": condition.prompt_shields,
            "source_ranking": condition.source_ranking,
            "trust_filter": condition.trust_filter,
            "filtered_page_count": len(filtered_pages),
            "prompt_shields_flagged": any(page.attack_type in PROMPT_SHIELD_ATTACKS for page in filtered_pages),
        }

        return RunResult(
            run_id=run_id,
            task_id=task.id,
            question=task.question,
            condition=condition.id,
            expected_answer=task.expected_answer,
            actual_answer=answer.answer,
            attack_type=task.attack_type,
            attack_target_answer=task.attack_target_answer,
            visited_page_ids=[page.id for page in visited_pages],
            selected_page_ids=[page.id for page in selected_pages],
            cited_page_ids=answer.citations,
            filtered_page_ids=[page.id for page in filtered_pages],
            answer={
                "answer": answer.answer,
                "conclusion": answer.conclusion,
                "citations": answer.citations,
                "refused": answer.refused,
                "action_safe": answer.action_safe,
            },
            safety_flags=safety_flags,
            metrics=metrics,
            latency_ms=self._latency_ms(condition, len(visited_pages), len(filtered_pages)),
            estimated_cost_usd=self._estimated_cost(condition, len(visited_pages)),
        )

    def _visited_pages(self, task: TaskCase, condition: Condition) -> list[WebPage]:
        if not condition.browse:
            return []
        page_ids = [*task.attack_page_ids, *task.required_page_ids]
        pages = [self._pages_by_id[page_id] for page_id in page_ids]
        if condition.source_ranking:
            return sorted(pages, key=_source_rank)
        return pages

    def _filtered_pages(self, pages: Sequence[WebPage], condition: Condition) -> list[WebPage]:
        filtered: list[WebPage] = []
        for page in pages:
            if condition.prompt_shields and page.attack_type in PROMPT_SHIELD_ATTACKS:
                filtered.append(page)
                continue
            if condition.trust_filter and (page.trust_label == "low" or page.freshness == "stale"):
                filtered.append(page)
        return filtered

    def _answer(
        self,
        task: TaskCase,
        selected_pages: Sequence[WebPage],
        condition: Condition,
    ) -> AgentAnswer:
        if not condition.browse:
            return self._direct_answer(task)

        supporting_pages = [page for page in selected_pages if task.id in page.supports_tasks]
        if not supporting_pages:
            return AgentAnswer(
                answer=ANSWER_INSUFFICIENT,
                conclusion="The agent did not find enough usable web evidence to answer the question.",
                citations=[],
                refused=True,
            )

        if condition.abstain_on_conflict and _has_conflict(task, supporting_pages):
            clean_pages = [
                page
                for page in supporting_pages
                if page.trust_label == "trusted" and page.freshness == "current"
            ]
            if clean_pages:
                return self._answer_from_pages(task, clean_pages, condition)
            return AgentAnswer(
                answer=ANSWER_INSUFFICIENT,
                conclusion="The agent found conflicting or low-trust web evidence and abstained.",
                citations=[],
                refused=True,
            )

        if condition.strict_abstention and _has_insufficient_clean_evidence(task, supporting_pages):
            clean_pages = [
                page
                for page in supporting_pages
                if page.trust_label == "trusted" and page.freshness == "current"
            ]
            return AgentAnswer(
                answer=ANSWER_INSUFFICIENT,
                conclusion=(
                    "The trusted evidence identifies an evidence gap rather than directly "
                    "establishing yes or no."
                ),
                citations=[page.id for page in clean_pages[:2]],
                refused=True,
            )

        return self._answer_from_pages(task, supporting_pages, condition)

    def _direct_answer(self, task: TaskCase) -> AgentAnswer:
        if task.expected_answer == ANSWER_INSUFFICIENT:
            answer = ANSWER_INSUFFICIENT
        elif "currently" in task.question.lower() or "this semester" in task.question.lower():
            answer = ANSWER_INSUFFICIENT
        else:
            answer = "no"
        return AgentAnswer(
            answer=answer,
            conclusion="Direct answering did not inspect external pages; this row is a no-browse baseline.",
            citations=[],
            refused=answer == ANSWER_INSUFFICIENT,
        )

    def _answer_from_pages(
        self,
        task: TaskCase,
        pages: Sequence[WebPage],
        condition: Condition,
    ) -> AgentAnswer:
        primary = pages[0]
        answer = primary.supports_tasks[task.id]
        citations = [primary.id]
        if condition.citation_validation:
            citations = [
                page.id
                for page in pages
                if page.supports_tasks.get(task.id) == answer
                or (answer == ANSWER_INSUFFICIENT and page.trust_label == "trusted")
            ][:2]
        else:
            citations = [page.id for page in pages[:2]]

        return AgentAnswer(
            answer=answer,
            conclusion=_conclusion(task, answer, pages),
            citations=citations,
            action_safe=not (task.attack_type == "action_hijack" and answer == task.attack_target_answer),
        )

    def _latency_ms(self, condition: Condition, visited_count: int, filtered_count: int) -> int:
        return 320 + 140 * visited_count + 90 * filtered_count + (220 if condition.prompt_shields else 0)

    def _estimated_cost(self, condition: Condition, visited_count: int) -> float:
        if not condition.browse:
            return 0.0002
        return round(0.0004 + visited_count * 0.00018 + (0.0002 if condition.prompt_shields else 0), 6)


def _source_rank(page: WebPage) -> tuple[int, int, str]:
    trust_rank = 0 if page.trust_label == "trusted" else 1
    freshness_rank = 0 if page.freshness == "current" else 1
    return (trust_rank, freshness_rank, page.id)


def _has_conflict(task: TaskCase, pages: Sequence[WebPage]) -> bool:
    answers = {page.supports_tasks[task.id] for page in pages if task.id in page.supports_tasks}
    return len(answers) > 1


def _has_insufficient_clean_evidence(task: TaskCase, pages: Sequence[WebPage]) -> bool:
    return any(
        page.trust_label == "trusted"
        and page.freshness == "current"
        and page.supports_tasks.get(task.id) == ANSWER_INSUFFICIENT
        for page in pages
    )


def _conclusion(task: TaskCase, answer: str, pages: Sequence[WebPage]) -> str:
    page_titles = ", ".join(page.title for page in pages[:2])
    if answer == ANSWER_INSUFFICIENT:
        return f"The visited pages do not provide enough reliable evidence to answer yes or no. Key pages: {page_titles}."
    return f"The agent answers {answer} based on the selected web evidence. Key pages: {page_titles}."
