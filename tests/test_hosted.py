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
    parse_hosted_answer,
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
