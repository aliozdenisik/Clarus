"""
Citation Sanitizer for LLM Output Normalization

Normalizes all LLM citation output to prevent double-bracket and malformed citation issues.
Handles bracket normalization, whitespace trimming, and comma spacing.

All transformations are idempotent (applying twice yields same result).
"""

import re
from typing import Any, Dict


def sanitize_citations(text: str) -> str:
    """
    Normalize citation brackets and formatting in text.

    Handles:
    - Double brackets: [[X]] → [X]
    - Triple+ brackets: [[[X]]] → [X]
    - Nested lists: [[X], [Y]] → [X], [Y]
    - Whitespace inside brackets: [ X ] → [X]
    - Comma spacing: [X,Y] → [X, Y]
    - Preserves valid single-bracket citations: [X] → [X]

    All transformations are idempotent.

    Args:
        text: Input text potentially containing malformed citations

    Returns:
        Text with normalized citations

    Example:
        >>> sanitize_citations("[[Bakara:45]]")
        "[Bakara:45]"
        >>> sanitize_citations("[ John 3:16 ]")
        "[John 3:16]"
        >>> sanitize_citations("[X,Y]")
        "[X, Y]"
        >>> sanitize_citations("[[X], [Y]]")
        "[X], [Y]"
    """
    if not text:
        return text

    result = text

    # Pattern 1: Remove double brackets (and triple+)
    # Match [[ ... ]] and replace with [ ... ]
    # Repeat until no more double brackets exist (handles triple+)
    max_iterations = 10  # Safety limit to prevent infinite loops
    iteration = 0
    while "[[" in result and iteration < max_iterations:
        result = re.sub(r"\[\[([^\[\]]*)\]\]", r"[\1]", result)
        iteration += 1

    # Pattern 2: Flatten nested lists like [[X], [Y]] → [X], [Y]
    # This handles cases where brackets contain comma-separated bracketed items
    result = re.sub(r"\[\[([^\[\]]+)\],\s*\[([^\[\]]+)\]\]", r"[\1], [\2]", result)

    # Pattern 3: Trim whitespace inside brackets: [ X ] → [X]
    result = re.sub(r"\[\s+", "[", result)
    result = re.sub(r"\s+\]", "]", result)

    # Pattern 4: Normalize comma spacing inside brackets: [X,Y] → [X, Y]
    # Match [content] and normalize commas inside
    def normalize_commas_in_brackets(match: re.Match) -> str:
        content = match.group(1)
        # Replace comma without space with comma + space
        normalized = re.sub(r",(?!\s)", ", ", content)
        return f"[{normalized}]"

    result = re.sub(r"\[([^\[\]]+)\]", normalize_commas_in_brackets, result)

    return result


def sanitize_agent_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply citation sanitizer to agent result dictionary.

    Sanitizes:
    - result["commentary"] if present (string)
    - result["essay"] if present (string)
    - Each string in result["citations"] if present (list of strings)

    Returns new dictionary without mutating input.

    Args:
        result: Agent result dict with optional "commentary", "essay", "citations" keys

    Returns:
        New dict with sanitized citation text

    Example:
        >>> result = {
        ...     "commentary": "See [[Bakara:45]]",
        ...     "citations": ["[Genesis 1:1]", "[[John 3:16]]"],
        ...     "confidence": 0.95
        ... }
        >>> sanitized = sanitize_agent_result(result)
        >>> sanitized["commentary"]
        "See [Bakara:45]"
        >>> sanitized["citations"]
        ["[Genesis 1:1]", "[John 3:16]"]
    """
    # Create shallow copy to avoid mutating input
    sanitized = dict(result)

    # Sanitize commentary if present
    if "commentary" in sanitized and isinstance(sanitized["commentary"], str):
        sanitized["commentary"] = sanitize_citations(sanitized["commentary"])

    # Sanitize essay if present
    if "essay" in sanitized and isinstance(sanitized["essay"], str):
        sanitized["essay"] = sanitize_citations(sanitized["essay"])

    # Sanitize citations list if present
    if "citations" in sanitized and isinstance(sanitized["citations"], list):
        sanitized["citations"] = [
            sanitize_citations(citation) if isinstance(citation, str) else citation
            for citation in sanitized["citations"]
        ]

    return sanitized
