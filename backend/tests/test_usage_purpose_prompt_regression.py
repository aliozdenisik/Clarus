import json
from unittest.mock import patch

from src.answer_generator import AnswerGenerator
from src.comparative_answer_generator import ComparativeAnswerGenerator
from src.multi_agent_answer_generator import OldTestamentAgent


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_answer_generator_uses_usage_purpose_for_template_selection() -> None:
    generator = AnswerGenerator(api_key="test-key", locale="tr")
    fake_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "answer": "ok",
                            "cited_references": ["Bakara:45"],
                            "confidence": 0.0,
                        }
                    )
                }
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }

    with (
        patch("src.answer_generator.get_prompt_template", return_value="STYLE") as mock_template,
        patch("src.answer_generator.llm_with_breaker", return_value=_FakeResponse(fake_payload)),
    ):
        result = generator._call_llm(
            query="sabir nedir",
            context="[1] Bakara:45 - ...",
            source="quran_tr_diyanet",
            usage_purpose="academic",
            language="en",
        )

    assert result["answer"] == "ok"
    mock_template.assert_called_once_with("academic", "en")


def test_comparative_generator_uses_usage_purpose_for_template_selection() -> None:
    generator = ComparativeAnswerGenerator(api_key="test-key", locale="tr")
    fake_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "essay": "comparative answer",
                            "quran_citations": ["Bakara:45"],
                            "bible_citations": ["John 3:16"],
                            "all_references_ordered": ["Bakara:45", "John 3:16"],
                            "confidence": 0.0,
                        }
                    )
                }
            }
        ]
    }

    with (
        patch("src.comparative_answer_generator.get_prompt_template", return_value="STYLE") as mock_template,
        patch("src.comparative_answer_generator.llm_with_breaker", return_value=_FakeResponse(fake_payload)),
    ):
        result = generator._call_llm(
            query="patience",
            context="context",
            usage_purpose="textual",
            language="en",
        )

    assert result["essay"] == "comparative answer"
    mock_template.assert_called_once_with("textual", "en")


def test_multi_agent_base_prompt_uses_usage_purpose_for_template_selection() -> None:
    agent = OldTestamentAgent(api_key="test-key", locale="tr")

    with patch("src.multi_agent_answer_generator.get_prompt_template", return_value="STYLE") as mock_template:
        system_prompt = agent._build_system_prompt(
            prompt_key="old_testament",
            usage_purpose="preaching",
            language="en",
        )

    mock_template.assert_called_once_with("preaching", "en")
    assert system_prompt.startswith("STYLE\n\n")
