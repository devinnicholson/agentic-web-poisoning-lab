from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_web_poisoning_lab.hosted import (
    AzureOpenAIConfig,
    HostedCompletion,
    HostedConfigError,
    HostedWebAgent,
    azure_config_from_env,
    build_relation_classifier_messages,
    parse_hosted_answer,
    parse_relation_classifier_answer,
)
from agentic_web_poisoning_lab.cli import (
    completed_key,
    completed_keys,
    hosted_progress_line,
    parse_task_ids,
    planned_hosted_total,
    resume_run_id,
)
from agentic_web_poisoning_lab.io import load_pages, load_tasks


class HostedTest(unittest.TestCase):
    def test_hosted_agent_records_provider_metadata_and_metrics(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.seed.jsonl")
        pages = load_pages(ROOT / "data" / "pages.seed.jsonl")
        client = FakeChatClient(
            [
                {
                    "answer": "yes",
                    "conclusion": "The forum-linked grant page says yes.",
                    "cited_page_ids": ["page_housing_grant_hijack"],
                    "refused": False,
                    "action_safe": False,
                },
                {
                    "answer": "no",
                    "conclusion": "The campus security guidance says not to submit credentials.",
                    "cited_page_ids": ["page_housing_security_guidance"],
                    "refused": False,
                    "action_safe": True,
                },
            ]
        )
        agent = HostedWebAgent(
            pages,
            client,
            provider_metadata={
                "provider": "azure_openai",
                "endpoint_host": "example.openai.azure.com",
                "deployment": "test-deployment",
                "api_version": "2024-10-21",
            },
        )

        rows = agent.run(
            tasks,
            ["A1_AGENT_BASELINE", "A4_FULL_DEFENSE"],
            ["task_011"],
        )

        self.assertEqual(len(rows), 2)
        baseline, defended = rows
        self.assertEqual(baseline["actual_answer"], "yes")
        self.assertTrue(baseline["metrics"]["attack_success"])
        self.assertTrue(baseline["metrics"]["unsafe_action"])
        self.assertEqual(baseline["provider_metadata"]["provider"], "azure_openai")
        self.assertEqual(defended["actual_answer"], "no")
        self.assertFalse(defended["metrics"]["attack_success"])
        self.assertIn("page_housing_grant_hijack", defended["filtered_page_ids"])

    def test_azure_config_from_env_requires_secret_settings(self) -> None:
        with self.assertRaises(HostedConfigError):
            azure_config_from_env(env_file=None, environ={})

    def test_azure_config_public_metadata_excludes_api_key(self) -> None:
        config = azure_config_from_env(
            env_file=None,
            environ={
                "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com",
                "AZURE_OPENAI_API_KEY": "secret-value",
                "AZURE_OPENAI_DEPLOYMENT": "smoke",
            },
        )

        metadata = config.public_metadata()

        self.assertIsInstance(config, AzureOpenAIConfig)
        self.assertEqual(metadata["endpoint_host"], "example.openai.azure.com")
        self.assertNotIn("api_key", metadata)
        self.assertNotIn("secret-value", json.dumps(metadata))

    def test_parse_hosted_answer_accepts_json_fences(self) -> None:
        task = next(task for task in load_tasks(ROOT / "data" / "tasks.seed.jsonl") if task.id == "task_011")
        pages = [
            page
            for page in load_pages(ROOT / "data" / "pages.seed.jsonl")
            if page.id == "page_housing_security_guidance"
        ]

        answer = parse_hosted_answer(
            '```json\n{"answer":"no","conclusion":"No.","cited_page_ids":["page_housing_security_guidance"]}\n```',
            task,
            pages,
        )

        self.assertEqual(answer.answer, "no")
        self.assertEqual(answer.citations, ["page_housing_security_guidance"])

    def test_parse_task_ids_accepts_all(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.seed.jsonl")

        self.assertEqual(len(parse_task_ids("all", tasks)), len(tasks))
        self.assertEqual(parse_task_ids("task_001, task_002", tasks), ["task_001", "task_002"])

    def test_hosted_iter_run_skips_completed_rows(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.seed.jsonl")
        pages = load_pages(ROOT / "data" / "pages.seed.jsonl")
        client = FakeChatClient(
            [
                {
                    "answer": "no",
                    "conclusion": "The official guidance says no.",
                    "cited_page_ids": ["page_housing_security_guidance"],
                    "refused": False,
                    "action_safe": True,
                }
            ]
        )
        agent = HostedWebAgent(pages, client, provider_metadata={"provider": "test"})

        rows = list(
            agent.iter_run(
                tasks,
                ["A1_AGENT_BASELINE"],
                ["task_011", "task_025"],
                run_id="hosted-test",
                skip_keys={("task_025", "A1_AGENT_BASELINE", 1)},
            )
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["run_id"], "hosted-test")
        self.assertEqual(rows[0]["task_id"], "task_011")
        self.assertEqual(len(client.messages), 1)

    def test_hosted_iter_run_repeats_rows_and_resumes_by_repeat_index(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.seed.jsonl")
        pages = load_pages(ROOT / "data" / "pages.seed.jsonl")
        client = FakeChatClient(
            [
                {
                    "answer": "no",
                    "conclusion": "The official guidance says no.",
                    "cited_page_ids": ["page_housing_security_guidance"],
                    "refused": False,
                    "action_safe": True,
                },
                {
                    "answer": "no",
                    "conclusion": "The official guidance still says no.",
                    "cited_page_ids": ["page_housing_security_guidance"],
                    "refused": False,
                    "action_safe": True,
                },
            ]
        )
        agent = HostedWebAgent(pages, client, provider_metadata={"provider": "test"})

        rows = list(
            agent.iter_run(
                tasks,
                ["A4_FULL_DEFENSE"],
                ["task_011"],
                run_id="hosted-repeat-test",
                repeat_count=3,
                skip_keys={("task_011", "A4_FULL_DEFENSE", 2)},
            )
        )

        self.assertEqual([row["repeat_index"] for row in rows], [1, 3])
        self.assertEqual({completed_key(row) for row in rows}, {
            ("task_011", "A4_FULL_DEFENSE", 1),
            ("task_011", "A4_FULL_DEFENSE", 3),
        })
        self.assertEqual(len(client.messages), 2)

    def test_structured_relation_gate_overrides_missing_validation_to_abstain(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.boundary.jsonl")
        pages = load_pages(ROOT / "data" / "pages.boundary.jsonl")
        client = FakeChatClient(
            [
                {
                    "evidence_relation": "direct_refutation",
                    "answer": "no",
                    "conclusion": "No third-party certification is present.",
                    "cited_page_ids": ["page_bound_algae_panel_gap"],
                    "refused": False,
                    "action_safe": True,
                },
                {
                    "evidence_relation": "direct_refutation",
                    "answer": "no",
                    "conclusion": "The certifier rejected the panel.",
                    "cited_page_ids": ["page_bound_algae_panel_rejected"],
                    "refused": False,
                    "action_safe": True,
                },
            ]
        )
        agent = HostedWebAgent(pages, client, provider_metadata={"provider": "test"})

        rows = agent.run(
            tasks,
            ["A7_STRUCTURED_RELATION_GATE"],
            ["task_bound_003", "task_bound_004"],
        )

        self.assertEqual(rows[0]["actual_answer"], "insufficient_evidence")
        self.assertTrue(rows[0]["metrics"]["answer_accuracy"])
        self.assertTrue(rows[0]["safety_flags"]["structured_relation_gate"])
        self.assertIn("Structured relation gate", rows[0]["answer"]["conclusion"])
        self.assertEqual(rows[1]["actual_answer"], "no")
        self.assertTrue(rows[1]["metrics"]["answer_accuracy"])

    def test_classified_relation_gate_uses_classifier_label_not_gold_label(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.boundary.jsonl")
        pages = load_pages(ROOT / "data" / "pages.boundary.jsonl")
        client = FakeChatClient(
            [
                {
                    "evidence_relation": "missing_validation",
                    "confidence": "high",
                    "rationale": "The classifier sees this as missing validation.",
                },
                {
                    "evidence_relation": "direct_refutation",
                    "answer": "no",
                    "conclusion": "The final answer model treated the page as direct refutation.",
                    "cited_page_ids": ["page_bound_algae_panel_rejected"],
                    "refused": False,
                    "action_safe": True,
                },
            ]
        )
        agent = HostedWebAgent(pages, client, provider_metadata={"provider": "test"})

        rows = agent.run(
            tasks,
            ["A8_CLASSIFIED_RELATION_GATE"],
            ["task_bound_004"],
        )

        self.assertEqual(rows[0]["actual_answer"], "insufficient_evidence")
        self.assertEqual(
            rows[0]["safety_flags"]["relation_labels"]["page_bound_algae_panel_rejected"],
            "missing_validation",
        )
        self.assertIn("Relation classifier gate", rows[0]["answer"]["conclusion"])
        self.assertIn("relation_classifier", rows[0]["provider_metadata"])
        self.assertEqual(len(client.messages), 2)
        self.assertNotIn("Task-relevant claim", client.messages[0][1]["content"])
        self.assertIn("Predicted relation label: missing_validation", client.messages[1][1]["content"])

    def test_calibrated_relation_gate_overrides_evidence_gap_mislabel(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.boundary.jsonl")
        pages = load_pages(ROOT / "data" / "pages.boundary.jsonl")
        client = FakeChatClient(
            [
                {
                    "evidence_relation": "direct_refutation",
                    "confidence": 0.92,
                    "rationale": "No third-party certification directly refutes the claim.",
                },
                {
                    "evidence_relation": "direct_refutation",
                    "answer": "no",
                    "conclusion": "The final answer model treated the gap as direct refutation.",
                    "cited_page_ids": ["page_bound_algae_panel_gap"],
                    "refused": False,
                    "action_safe": True,
                },
            ]
        )
        agent = HostedWebAgent(pages, client, provider_metadata={"provider": "test"})

        rows = agent.run(
            tasks,
            ["A9_CALIBRATED_RELATION_GATE"],
            ["task_bound_003"],
        )

        classifier_record = rows[0]["provider_metadata"]["relation_classifier"][0]
        self.assertEqual(rows[0]["actual_answer"], "insufficient_evidence")
        self.assertEqual(rows[0]["safety_flags"]["relation_labels"]["page_bound_algae_panel_gap"], "missing_validation")
        self.assertEqual(classifier_record["raw_evidence_relation"], "direct_refutation")
        self.assertTrue(classifier_record["calibration_override"])
        self.assertIn("Calibrated relation label: missing_validation", client.messages[1][1]["content"])

    def test_preservation_calibrated_gate_preserves_direct_refutation(self) -> None:
        tasks = load_tasks(ROOT / "data" / "tasks.graph-long.jsonl")
        pages = load_pages(ROOT / "data" / "pages.graph-long.jsonl")
        client = FakeChatClient(
            [
                {
                    "evidence_relation": "missing_validation",
                    "confidence": 0.88,
                    "rationale": "The classifier was too conservative.",
                },
                {
                    "evidence_relation": "missing_validation",
                    "confidence": 0.86,
                    "rationale": "The classifier was too conservative.",
                },
                {
                    "evidence_relation": "missing_validation",
                    "confidence": 0.84,
                    "rationale": "The classifier was too conservative.",
                },
                {
                    "evidence_relation": "missing_validation",
                    "answer": "insufficient_evidence",
                    "conclusion": "The final answer model over-abstained.",
                    "cited_page_ids": ["page_long_faceid_board_rejection"],
                    "refused": True,
                    "action_safe": True,
                },
            ]
        )
        agent = HostedWebAgent(pages, client, provider_metadata={"provider": "test"})

        rows = agent.run(
            tasks,
            ["A10_PRESERVATION_CALIBRATED_GATE"],
            ["task_long_graph_005"],
        )

        classifier_record = rows[0]["provider_metadata"]["relation_classifier"][0]
        self.assertEqual(rows[0]["actual_answer"], "no")
        self.assertTrue(rows[0]["metrics"]["answer_accuracy"])
        self.assertEqual(
            rows[0]["safety_flags"]["relation_labels"]["page_long_faceid_board_rejection"],
            "direct_refutation",
        )
        self.assertEqual(classifier_record["raw_evidence_relation"], "missing_validation")
        self.assertTrue(classifier_record["calibration_override"])
        self.assertIn("Preservation-calibrated relation label: direct_refutation", client.messages[-1][1]["content"])

    def test_relation_classifier_prompt_and_parser_are_gold_label_free(self) -> None:
        task = next(task for task in load_tasks(ROOT / "data" / "tasks.boundary.jsonl") if task.id == "task_bound_003")
        page = next(
            page
            for page in load_pages(ROOT / "data" / "pages.boundary.jsonl")
            if page.id == "page_bound_algae_panel_gap"
        )

        messages = build_relation_classifier_messages(task, page)
        parsed = parse_relation_classifier_answer('{"evidence_relation":"direct refutation"}', task, page)

        self.assertIn("Summary:", messages[1]["content"])
        self.assertNotIn("Task-relevant claim", messages[1]["content"])
        self.assertEqual(parsed["evidence_relation"], "direct_refutation")

    def test_resume_helpers_identify_completed_rows_and_progress(self) -> None:
        rows = [
            {
                "run_id": "hosted-existing",
                "task_id": "task_011",
                "condition": "A1_AGENT_BASELINE",
                "repeat_index": 2,
                "actual_answer": "no",
                "metrics": {"attack_success": False, "provider_error": False},
                "provider_metadata": {"retry_count": 2},
            }
        ]

        self.assertEqual(completed_keys(rows), {("task_011", "A1_AGENT_BASELINE", 2)})
        self.assertEqual(resume_run_id(rows), "hosted-existing")
        self.assertIn("[1/2] A1_AGENT_BASELINE task_011", hosted_progress_line(rows[0], 1, 2))
        self.assertIn("repeat=2", hosted_progress_line(rows[0], 1, 2))
        self.assertIn("retries=2", hosted_progress_line(rows[0], 1, 2))
        self.assertEqual(planned_hosted_total(["task_011", "task_025"], ["A1"], None, 3), 6)


class FakeChatClient:
    def __init__(self, payloads: Sequence[Mapping[str, object]]) -> None:
        self._payloads = list(payloads)
        self.messages: list[Sequence[Mapping[str, str]]] = []

    def complete(self, messages: Sequence[Mapping[str, str]]) -> HostedCompletion:
        self.messages.append(messages)
        payload = self._payloads.pop(0)
        return HostedCompletion(
            content=json.dumps(payload),
            metadata={
                "model": "fake-model",
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20},
            },
            latency_ms=25,
        )


if __name__ == "__main__":
    unittest.main()
