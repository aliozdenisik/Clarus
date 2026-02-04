# Issue #001: New Testament Citation Formatting in Compare Mode

**Status:** Closed  
**Date Closed:** 2026-01-29  
**Priority:** Medium  
**Date Reported:** 2026-01-29  
**Component:** Backend / Multi-Agent Answer Generator (NewTestamentAgent)

---

## Problem Description

The New Testament (Yeni Ahit) section in the multi-agent comparison results ("Compare" page) is generating citations with incorrect formatting, specifically using double brackets (e.g., `[[Revelation 5:1]]`) or nested lists of citations.

## Observed Behavior

- Citations appear as `[[Reference]]` instead of `[Reference]`.
- Multiple citations appear nested like `[[Ref 1], [Ref 2]]`.

## Expected Behavior

Citations should use single brackets: `[Book Chapter:Verse]`

## Context

This seems to be isolated to the New Testament agent's output. The other agents (Quran, Old Testament, Apocrypha) appear to be formatting citations correctly.

## Root Cause Analysis

- **Codebase:** The system prompts in `backend/src/multi_agent_answer_generator.py` correctly request single brackets: `[Kitap Bölüm:Ayet]`. The issue is a model adherence failure, not a prompt error.
- **Git History:** The frontend citation parser (`frontend/lib/utils/parse-citations.ts`) has required multiple updates (e.g., commits `c876560`, `4a76d8f`) to handle evolving citation formats like comma-separated lists and ranges. This indicates a long-standing instability in LLM citation output consistency.
- **Model Bias:** The `google/gemini-3-flash-preview` model may have a bias towards "Wiki-style" or "Obsidian-style" double-bracket links for the New Testament corpus specifically.

## Affected Files

- `backend/src/multi_agent_answer_generator.py` (NewTestamentAgent prompt)
- `frontend/lib/utils/parse-citations.ts` (citation parser)

## Proposed Solutions

1. **Strengthen prompt:** Add explicit examples in the system prompt showing correct vs. incorrect formatting
2. **Post-processing:** Add a cleanup step in the backend to normalize double brackets to single brackets
3. **Model switch:** Test alternative models for the NT agent that show better instruction adherence

## Related Issues

- None

## Notes

- This issue has existed across multiple git commits, suggesting it's a persistent model behavior issue rather than a recent regression.
