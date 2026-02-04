# RFC-004: Realistic Confidence Scoring

**Status**: Proposed
**Created**: 2026-01-29
**Effort**: Medium

---

## Summary

Replace the current LLM self-reported confidence score with a realistic, data-grounded confidence metric that reflects actual retrieval quality, citation coverage, and source agreement.

## Motivation

The confidence percentage displayed in the analysis results bar (e.g. "95% confidence") is currently whatever the LLM decides to self-report. The system prompt asks the model to output a confidence number, and the few-shot examples hardcode `0.95` — so the model almost always echoes back a high value. This gives users a false sense of precision.

LLMs are notoriously unreliable at self-assessing confidence. A user seeing "95% confidence" expects that number to mean something measurable. Today it does not. This undermines trust, especially for a tool designed around scholarly accuracy.

## Proposal

The confidence score should be computed from objective, measurable signals that the system already has access to — not from the LLM's opinion of itself.

The score should reflect how well the system actually performed on a given query, considering factors such as:

- **Did the search find strong matches?** If the vector similarity scores from Qdrant are high, the system found genuinely relevant verses. If they're low or scattered, the system is less sure.
- **Did multiple sources agree?** A query that finds relevant content in both Quran and Bible collections is more robustly answered than one where only a single collection had anything to say.
- **Were citations actually used?** If the generated answer makes many claims but cites few verses, confidence should be lower. If every claim is backed by a citation, confidence should be higher.
- **How many verses were available?** A response synthesized from 80 relevant verses is more grounded than one working from 3.
- **Did the search scores cluster well?** A clear separation between relevant and irrelevant results (high top scores, steep drop-off) indicates a focused, confident retrieval. A flat distribution of mediocre scores indicates uncertainty.

The final confidence number shown to the user should be a weighted combination of these real signals. The LLM's own confidence assessment may be included as one small input, but it should not dominate the score.

The display in the UI (the green/yellow/red colored percentage) does not need to change — only the number feeding into it.

## Expected Outcome

- The confidence score reflects actual retrieval and citation quality, not LLM self-assessment.
- Queries with strong multi-source agreement and high similarity scores produce high confidence (80-95%).
- Queries with weak retrieval, sparse citations, or single-source answers produce lower confidence (40-70%).
- Users can trust the number as a meaningful quality indicator.
- The few-shot prompt examples no longer hardcode a confidence value for the LLM to parrot back.

## Open Questions

- Should the individual signal weights be tunable via configuration, or fixed after initial calibration?
- Should the old LLM-reported confidence be retained as a secondary "model confidence" field for debugging/comparison?
- What is the minimum acceptable confidence threshold below which the system should warn the user that results may be unreliable?
