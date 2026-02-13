"""
PromptManager system for locale-parameterized LLM prompt templates.

Centralizes all hardcoded prompts from backend modules into locale-aware templates.
Supports Turkish (tr) and English (en) variants for all prompts.
"""

from typing import Any

from . import answer_generator, comparative, multi_agent, query_enhancer


class PromptManager:
    """
    Centralized prompt template manager with locale support.

    Retrieves prompts from module-specific template files based on:
    - module: Target module (answer_generator, query_enhancer, multi_agent, comparative)
    - key: Specific prompt identifier
    - locale: Language code ("tr" or "en")
    """

    def __init__(self):
        self._templates = {
            "answer_generator": answer_generator.PROMPTS,
            "query_enhancer": query_enhancer.PROMPTS,
            "multi_agent": multi_agent.PROMPTS,
            "comparative": comparative.PROMPTS,
        }

    def get_prompt(self, module: str, key: str, locale: str = "tr") -> Any:
        """
        Retrieve a prompt template.

        Args:
            module: Module name (answer_generator, query_enhancer, multi_agent, comparative)
            key: Prompt key (e.g., "quran_system", "bible_few_shot", "section_headers")
            locale: Language code ("tr" or "en", default: "tr")

        Returns:
            Prompt string, dict, or list depending on the key type

        Raises:
            KeyError: If module or key doesn't exist
            ValueError: If locale not supported for the given key

        Examples:
            >>> pm = PromptManager()
            >>> pm.get_prompt("answer_generator", "quran_system", "tr")
            'Sen uzman bir İslam Alimi...'
            >>> pm.get_prompt("multi_agent", "section_headers", "en")
            {'old_testament': '## Old Testament', ...}
        """
        if module not in self._templates:
            raise KeyError(f"Unknown module '{module}'. Available: {list(self._templates.keys())}")

        module_prompts = self._templates[module]

        if key not in module_prompts:
            raise KeyError(f"Unknown key '{key}' in module '{module}'. Available: {list(module_prompts.keys())}")

        prompt_data = module_prompts[key]

        if isinstance(prompt_data, dict) and locale in prompt_data:
            return prompt_data[locale]

        if isinstance(prompt_data, dict) and locale not in prompt_data:
            if "tr" in prompt_data or "en" in prompt_data:
                raise ValueError(
                    f"Locale '{locale}' not available for '{module}.{key}'. "
                    f"Available locales: {list(prompt_data.keys())}"
                )
            return prompt_data

        return prompt_data

    def get_few_shot(self, module: str, source: str) -> list[dict[str, str]]:
        """
        Retrieve few-shot examples (locale-independent).

        Args:
            module: Module name
            source: Source type ("quran" or "bible")

        Returns:
            List of few-shot examples

        Examples:
            >>> pm.get_prompt("answer_generator", "quran_few_shot")
            [{"role": "user", "content": "..."}, ...]
        """
        key = f"{source}_few_shot"
        return self.get_prompt(module, key)

    def get_section_headers(self, locale: str = "tr") -> dict[str, str]:
        """
        Retrieve essay section headers for multi-agent system.

        Args:
            locale: Language code ("tr" or "en", default: "tr")

        Returns:
            Dictionary of section headers

        Examples:
            >>> pm.get_section_headers("tr")
            {'old_testament': '## Eski Ahit (Old Testament)', ...}
        """
        return self.get_prompt("multi_agent", "section_headers", locale)
