# RFC-009: Tanzil.net Verified Turkish Quran Translation Source

**Status**: Proposed
**Created**: 2026-02-02
**Effort**: Medium

---

## Summary

Replace the current Turkish Quran data source with verified, up-to-date Turkish translations downloaded directly from tanzil.net, the authoritative open-source Quran text repository.

## Motivation

The current `quran_tr.json` data file may contain unverified or outdated Turkish translations. Tanzil.net is a widely recognized, community-verified source for Quran texts that provides multiple scholarly Turkish translations (e.g., Diyanet İşleri, Elmalılı Hamdi Yazır, Süleyman Ateş). Using tanzil.net as the canonical data source ensures:

- **Accuracy**: Texts are verified against published scholarly translations.
- **Currency**: Updates and corrections from tanzil.net are reflected.
- **Provenance**: Clear attribution to specific translators/editions.
- **Trust**: Users can verify results against a well-known public source.

## Proposal

Download the current Turkish Quran translation(s) from tanzil.net and use them as the primary data source for the semantic search system. The existing `quran_tr` collection in the vector database should be rebuilt from this new source. The end result should be transparent to the user — search and Q&A features continue to work as before, but backed by verified tanzil.net data.

Users should notice improved accuracy and reliability of Turkish Quran text in search results and citations. The data pipeline should support future updates from tanzil.net without manual intervention.

## Expected Outcome

- Verified Turkish Quran translation(s) from tanzil.net are downloaded and stored locally.
- The existing `quran_tr.json` is replaced (or superseded) by the new data.
- The `quran_tr` Qdrant collection is re-indexed with the new source.
- All existing search, ask, and compare features work correctly with the new data.
- Data provenance (translator name, source URL) is preserved in metadata.
- A repeatable process exists to refresh data from tanzil.net in the future.

## Open Questions

- Which specific Turkish translation(s) should be included? (e.g., Diyanet only, or multiple?)
- Should multiple translations be stored as separate collections or merged into one?
- How should translator attribution appear in search results and citations?
