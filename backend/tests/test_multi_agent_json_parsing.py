from unittest.mock import MagicMock, patch

from src.multi_agent_answer_generator import BaseSpecialistAgent


def test_call_llm_accepts_valid_json_with_trailing_text() -> None:
    response = MagicMock()
    response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        '{"commentary":"Valid commentary","citations":["Genesis 1:1"],"confidence":0.9}'
                        "\nUnexpected trailing explanation"
                    )
                }
            }
        ]
    }
    agent = BaseSpecialistAgent(api_key="test-key")

    with patch("src.multi_agent_answer_generator.llm_with_breaker", return_value=response):
        result = agent._call_llm([{"role": "user", "content": "test"}])

    assert result == {
        "commentary": "Valid commentary",
        "citations": ["Genesis 1:1"],
        "confidence": 0.9,
    }
    response.raise_for_status.assert_called_once_with()
