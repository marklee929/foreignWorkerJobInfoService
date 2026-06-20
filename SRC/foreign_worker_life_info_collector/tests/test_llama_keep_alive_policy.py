from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from foreign_worker_life_info_collector.social.news.duplicate_guard.llama_duplicate_checker import LlamaDuplicateChecker
from foreign_worker_life_info_collector.social.news.models import NewsCandidate
from foreign_worker_life_info_collector.social.news.summarizer.news_summarizer import NewsSummarizer
from foreign_worker_life_info_collector.utils.content_card_payload_generator import request_llama_payload


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def candidate(**overrides) -> NewsCandidate:
    base = {
        "title": "Korea updates visa support for foreign workers",
        "source_url": "https://example.com/visa",
        "source_type": "test",
        "publisher_name": "Example News",
        "summary": "Korea announced practical visa support for foreign workers.",
        "content": "Foreign workers should check official visa support notices and deadlines.",
    }
    base.update(overrides)
    return NewsCandidate(**base)


def request_payload(mock_urlopen) -> dict:
    request = mock_urlopen.call_args.args[0]
    return json.loads(request.data.decode("utf-8"))


class LlamaKeepAlivePolicyTest(unittest.TestCase):
    def test_summary_keep_alive_uses_low_memory_default_when_global_keep_alive_is_set(self) -> None:
        response = {
            "response": json.dumps(
                {
                    "generated_title": "Visa Support Update",
                    "summary_bullets": ["Visa support changed.", "Workers should check deadlines.", "Official notices matter."],
                    "why_it_matters": ["Visa timing may affect job plans.", "Workers should verify eligibility."],
                    "risk_notes": "Verify details with the official source.",
                }
            )
        }
        with patch.dict(
            "os.environ",
            {"LOCAL_LLAMA_ENDPOINT": "http://localhost:11434", "OLLAMA_KEEP_ALIVE": "10m"},
            clear=False,
        ):
            with patch(
                "foreign_worker_life_info_collector.social.news.summarizer.news_summarizer.urlopen",
                return_value=FakeResponse(response),
            ) as mock_urlopen:
                summary = NewsSummarizer(timeout=1).summarize(candidate())

        self.assertEqual(summary.generated_title, "Visa Support Update")
        self.assertEqual(request_payload(mock_urlopen)["keep_alive"], "30s")

    def test_summary_keep_alive_uses_task_specific_env(self) -> None:
        response = {
            "response": json.dumps(
                {
                    "generated_title": "Visa Support Update",
                    "summary_bullets": ["Visa support changed.", "Workers should check deadlines.", "Official notices matter."],
                    "why_it_matters": ["Visa timing may affect job plans.", "Workers should verify eligibility."],
                    "risk_notes": "Verify details with the official source.",
                }
            )
        }
        with patch.dict(
            "os.environ",
            {
                "LOCAL_LLAMA_ENDPOINT": "http://localhost:11434",
                "OLLAMA_KEEP_ALIVE": "10m",
                "OLLAMA_SUMMARY_KEEP_ALIVE": "15s",
            },
            clear=False,
        ):
            with patch(
                "foreign_worker_life_info_collector.social.news.summarizer.news_summarizer.urlopen",
                return_value=FakeResponse(response),
            ) as mock_urlopen:
                NewsSummarizer(timeout=1).summarize(candidate())

        self.assertEqual(request_payload(mock_urlopen)["keep_alive"], "15s")

    def test_duplicate_keep_alive_uses_low_memory_default_when_global_keep_alive_is_set(self) -> None:
        with patch.dict(
            "os.environ",
            {"LOCAL_LLAMA_ENDPOINT": "http://localhost:11434/api/generate", "OLLAMA_KEEP_ALIVE": "10m"},
            clear=False,
        ):
            with patch(
                "foreign_worker_life_info_collector.social.news.duplicate_guard.llama_duplicate_checker.urlopen",
                return_value=FakeResponse({"response": json.dumps({"duplicate": False, "confidence": 0.1, "reason": "distinct"})}),
            ) as mock_urlopen:
                result = LlamaDuplicateChecker(timeout=1).check(candidate(), [candidate(title="Recent distinct item")])

        self.assertFalse(result[0])
        self.assertEqual(request_payload(mock_urlopen)["keep_alive"], "30s")

    def test_duplicate_keep_alive_uses_task_specific_env(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "LOCAL_LLAMA_ENDPOINT": "http://localhost:11434/api/generate",
                "OLLAMA_KEEP_ALIVE": "10m",
                "OLLAMA_DUPLICATE_KEEP_ALIVE": "12s",
            },
            clear=False,
        ):
            with patch(
                "foreign_worker_life_info_collector.social.news.duplicate_guard.llama_duplicate_checker.urlopen",
                return_value=FakeResponse({"response": json.dumps({"duplicate": False, "confidence": 0.1, "reason": "distinct"})}),
            ) as mock_urlopen:
                LlamaDuplicateChecker(timeout=1).check(candidate(), [candidate(title="Recent distinct item")])

        self.assertEqual(request_payload(mock_urlopen)["keep_alive"], "12s")

    def test_card_payload_keep_alive_uses_low_memory_default_when_global_keep_alive_is_set(self) -> None:
        with patch.dict(
            "os.environ",
            {"LOCAL_LLAMA_ENABLED": "true", "OLLAMA_KEEP_ALIVE": "10m"},
            clear=False,
        ):
            with patch(
                "foreign_worker_life_info_collector.utils.content_card_payload_generator.urlopen",
                return_value=FakeResponse({"response": "{\"ok\": true}"}),
            ) as mock_urlopen:
                raw = request_llama_payload("prompt", endpoint="http://localhost:11434", model="test-model", timeout_seconds=1)

        self.assertEqual(raw, "{\"ok\": true}")
        self.assertEqual(request_payload(mock_urlopen)["keep_alive"], "30s")

    def test_card_payload_keep_alive_uses_task_specific_env(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "LOCAL_LLAMA_ENABLED": "true",
                "OLLAMA_KEEP_ALIVE": "10m",
                "OLLAMA_CARD_PAYLOAD_KEEP_ALIVE": "20s",
            },
            clear=False,
        ):
            with patch(
                "foreign_worker_life_info_collector.utils.content_card_payload_generator.urlopen",
                return_value=FakeResponse({"response": "{\"ok\": true}"}),
            ) as mock_urlopen:
                request_llama_payload("prompt", endpoint="http://localhost:11434", model="test-model", timeout_seconds=1)

        self.assertEqual(request_payload(mock_urlopen)["keep_alive"], "20s")


if __name__ == "__main__":
    unittest.main()
