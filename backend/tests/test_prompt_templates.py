"""
Tests for prompt template system (backend/src/prompts/).

Verifies locale-parameterized prompt retrieval and multi-agent section headers.
"""

import pytest

from src.multi_agent_answer_generator import MultiAgentAnswer
from src.prompts import PromptManager


class TestPromptManager:
    """Test PromptManager basic functionality"""

    def test_init(self):
        """PromptManager initializes with all modules"""
        pm = PromptManager()
        assert pm._templates is not None
        assert "answer_generator" in pm._templates
        assert "query_enhancer" in pm._templates
        assert "multi_agent" in pm._templates
        assert "comparative" in pm._templates

    def test_get_prompt_unknown_module(self):
        """Unknown module raises KeyError with helpful message"""
        pm = PromptManager()
        with pytest.raises(KeyError, match="Unknown module 'nonexistent'"):
            pm.get_prompt("nonexistent", "quran_system", "tr")

    def test_get_prompt_unknown_key(self):
        """Unknown key raises KeyError with helpful message"""
        pm = PromptManager()
        with pytest.raises(KeyError, match="Unknown key 'nonexistent'"):
            pm.get_prompt("answer_generator", "nonexistent", "tr")

    def test_get_prompt_unsupported_locale(self):
        """Unsupported locale raises ValueError"""
        pm = PromptManager()
        with pytest.raises(ValueError, match="Locale 'fr' not available"):
            pm.get_prompt("answer_generator", "quran_system", "fr")


class TestAnswerGeneratorPrompts:
    """Test answer_generator module prompts"""

    def test_quran_system_prompt_turkish(self):
        """Quran system prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("answer_generator", "quran_system", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir İslam Alimi" in prompt
        assert "Türkçe" in prompt

    def test_quran_system_prompt_english(self):
        """Quran system prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("answer_generator", "quran_system", "en")
        assert isinstance(prompt, str)
        assert "You are an expert Islamic Scholar" in prompt
        assert "English" in prompt

    def test_bible_system_prompt_turkish(self):
        """Bible system prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("answer_generator", "bible_system", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir İncil Alimi" in prompt
        assert "Türkçe" in prompt

    def test_bible_system_prompt_english(self):
        """Bible system prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("answer_generator", "bible_system", "en")
        assert isinstance(prompt, str)
        assert "You are an expert Biblical Scholar" in prompt
        assert "English" in prompt

    def test_quran_few_shot_examples(self):
        """Quran few-shot examples are locale-independent"""
        pm = PromptManager()
        examples = pm.get_prompt("answer_generator", "quran_few_shot")
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert all("role" in ex and "content" in ex for ex in examples)

    def test_bible_few_shot_examples(self):
        """Bible few-shot examples are locale-independent"""
        pm = PromptManager()
        examples = pm.get_prompt("answer_generator", "bible_few_shot")
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert all("role" in ex and "content" in ex for ex in examples)


class TestQueryEnhancerPrompts:
    """Test query_enhancer module prompts"""

    def test_quran_system_prompt_turkish(self):
        """Quran enhancement prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("query_enhancer", "quran_system", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir İslam Alimi" in prompt
        assert "TÜRKÇE" in prompt

    def test_quran_system_prompt_english(self):
        """Quran enhancement prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("query_enhancer", "quran_system", "en")
        assert isinstance(prompt, str)
        assert "You are an expert Islamic Scholar" in prompt
        assert "ENGLISH" in prompt

    def test_bible_system_prompt_turkish(self):
        """Bible enhancement prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("query_enhancer", "bible_system", "tr")
        assert isinstance(prompt, str)
        assert "Sen King James Version" in prompt
        assert "Türkçe" in prompt or "İngilizce" in prompt

    def test_bible_system_prompt_english(self):
        """Bible enhancement prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("query_enhancer", "bible_system", "en")
        assert isinstance(prompt, str)
        assert "You are an expert Biblical Scholar" in prompt
        assert "King James Version" in prompt


class TestMultiAgentPrompts:
    """Test multi_agent module prompts (5 agents + section headers)"""

    def test_old_testament_agent_turkish(self):
        """OT agent prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "old_testament", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir Eski Ahit" in prompt
        assert "Türkçe" in prompt

    def test_old_testament_agent_english(self):
        """OT agent prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "old_testament", "en")
        assert isinstance(prompt, str)
        assert "You are an expert Old Testament" in prompt
        assert "English" in prompt

    def test_new_testament_agent_turkish(self):
        """NT agent prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "new_testament", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir Yeni Ahit" in prompt
        assert "Türkçe" in prompt

    def test_new_testament_agent_english(self):
        """NT agent prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "new_testament", "en")
        assert isinstance(prompt, str)
        assert "You are an expert New Testament" in prompt
        assert "English" in prompt

    def test_apocrypha_agent_turkish(self):
        """Apocrypha agent prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "apocrypha", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir Apokrifa" in prompt
        assert "Türkçe" in prompt

    def test_apocrypha_agent_english(self):
        """Apocrypha agent prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "apocrypha", "en")
        assert isinstance(prompt, str)
        assert "You are an expert Apocrypha" in prompt
        assert "English" in prompt

    def test_quran_agent_turkish(self):
        """Quran agent prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "quran", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir İslam Alimi" in prompt
        assert "Türkçe" in prompt

    def test_quran_agent_english(self):
        """Quran agent prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "quran", "en")
        assert isinstance(prompt, str)
        assert "You are an expert Islamic Scholar" in prompt
        assert "English" in prompt

    def test_summary_agent_turkish(self):
        """Summary agent prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "summary", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir karşılaştırmalı" in prompt
        assert "Türkçe" in prompt

    def test_summary_agent_english(self):
        """Summary agent prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("multi_agent", "summary", "en")
        assert isinstance(prompt, str)
        assert "You are an expert comparative" in prompt
        assert "English" in prompt

    def test_section_headers_turkish(self):
        """Section headers return Turkish version"""
        pm = PromptManager()
        headers = pm.get_section_headers("tr")
        assert isinstance(headers, dict)
        assert headers["old_testament"] == "## Eski Ahit (Old Testament)"
        assert headers["new_testament"] == "## Yeni Ahit (New Testament)"
        assert headers["apocrypha"] == "## Apokrifa (Apocrypha)"
        assert headers["quran"] == "## Kuran-ı Kerim"
        assert headers["synthesis"] == "## Karşılaştırmalı Değerlendirme"

    def test_section_headers_english(self):
        """Section headers return English version"""
        pm = PromptManager()
        headers = pm.get_section_headers("en")
        assert isinstance(headers, dict)
        assert headers["old_testament"] == "## Old Testament"
        assert headers["new_testament"] == "## New Testament"
        assert headers["apocrypha"] == "## Apocrypha"
        assert headers["quran"] == "## Quran"
        assert headers["synthesis"] == "## Comparative Analysis"


class TestComparativePrompts:
    """Test comparative module prompts"""

    def test_system_prompt_turkish(self):
        """Comparative system prompt returns Turkish version"""
        pm = PromptManager()
        prompt = pm.get_prompt("comparative", "system", "tr")
        assert isinstance(prompt, str)
        assert "Sen uzman bir karşılaştırmalı teolog" in prompt
        assert "TÜRKÇE" in prompt

    def test_system_prompt_english(self):
        """Comparative system prompt returns English version"""
        pm = PromptManager()
        prompt = pm.get_prompt("comparative", "system", "en")
        assert isinstance(prompt, str)
        assert "You are an expert comparative theologian" in prompt
        assert "ENGLISH" in prompt

    def test_few_shot_examples(self):
        """Comparative few-shot examples are locale-independent"""
        pm = PromptManager()
        examples = pm.get_prompt("comparative", "few_shot")
        assert isinstance(examples, list)
        assert len(examples) > 0
        assert all("role" in ex and "content" in ex for ex in examples)


class TestMultiAgentAnswerToEssay:
    """Test MultiAgentAnswer.to_essay() locale-aware section headers"""

    def test_to_essay_turkish_headers(self):
        """to_essay() returns Turkish section headers for locale=tr"""
        answer = MultiAgentAnswer(
            old_testament_commentary="OT content",
            new_testament_commentary="NT content",
            apocrypha_commentary="Apoc content",
            quran_commentary="Quran content",
            synthesis="Summary content",
            locale="tr",
        )
        essay = answer.to_essay()
        assert "## Eski Ahit (Old Testament)" in essay
        assert "## Yeni Ahit (New Testament)" in essay
        assert "## Apokrifa (Apocrypha)" in essay
        assert "## Kuran-ı Kerim" in essay
        assert "## Karşılaştırmalı Değerlendirme" in essay

    def test_to_essay_english_headers(self):
        """to_essay() returns English section headers for locale=en"""
        answer = MultiAgentAnswer(
            old_testament_commentary="OT content",
            new_testament_commentary="NT content",
            apocrypha_commentary="Apoc content",
            quran_commentary="Quran content",
            synthesis="Summary content",
            locale="en",
        )
        essay = answer.to_essay()
        assert "## Old Testament" in essay
        assert "## New Testament" in essay
        assert "## Apocrypha" in essay
        assert "## Quran" in essay
        assert "## Comparative Analysis" in essay

    def test_to_essay_default_locale_is_turkish(self):
        """to_essay() defaults to Turkish headers when locale not specified"""
        answer = MultiAgentAnswer(
            old_testament_commentary="OT content",
            new_testament_commentary="NT content",
            apocrypha_commentary="Apoc content",
            quran_commentary="Quran content",
            synthesis="Summary content",
        )
        essay = answer.to_essay()
        assert "## Eski Ahit (Old Testament)" in essay
        assert "## Kuran-ı Kerim" in essay


class TestPromptContentPreservation:
    """Verify original prompt content is preserved"""

    def test_quran_prompt_has_critical_rules(self):
        """Quran prompts contain critical rules section"""
        pm = PromptManager()
        prompt_tr = pm.get_prompt("answer_generator", "quran_system", "tr")
        prompt_en = pm.get_prompt("answer_generator", "quran_system", "en")
        assert "KRİTİK KURALLAR" in prompt_tr or "CRITICAL RULES" in prompt_tr
        assert "CRITICAL RULES" in prompt_en

    def test_bible_prompt_has_kjv_reference(self):
        """Bible prompts reference KJV or KJVA"""
        pm = PromptManager()
        prompt_en = pm.get_prompt("query_enhancer", "bible_system", "en")
        assert "King James Version" in prompt_en or "KJV" in prompt_en

    def test_multi_agent_prompts_have_json_format(self):
        """All multi-agent prompts specify JSON output format"""
        pm = PromptManager()
        for agent in ["old_testament", "new_testament", "apocrypha", "quran", "summary"]:
            prompt_tr = pm.get_prompt("multi_agent", agent, "tr")
            prompt_en = pm.get_prompt("multi_agent", agent, "en")
            assert "JSON" in prompt_tr
            assert "JSON" in prompt_en
