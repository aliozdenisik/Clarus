---
number: 26
title: "Replace Quran data with Tanzil source, adapt pipeline, and add source attribution"
labels: [enhancement]
date: 2026-02-01
url: https://github.com/aliozdenisik/Clarus/issues/26
status: open
---

# Replace Quran data with Tanzil source, adapt pipeline, and add source attribution

## Description

The current `quran_tr.json` is sourced from a third-party CDN (`risan/quran-json`) which itself derives from Tanzil.net. This indirect sourcing creates attribution gaps and limits translation choice. The data should be sourced directly from Tanzil.net with an appropriate Turkish translation, the vector indexing pipeline should be adapted to the new format, and proper source attribution (with Tanzil link) must be displayed on the site.

## Current State

- **Data file**: `backend/data/quran_tr.json` (6,236 verses, 114 surahs)
- **Source**: `cdn.jsdelivr.net/npm/quran-json@3.1.2/dist/quran_tr.json` (derivative of Tanzil `tr.diyanet`)
- **Attribution**: Hardcoded as `"Diyanet Isleri Baskanligi"` in `backend/app/api/compare.py` (lines 112-127) and `compare_helpers.py`
- **Frontend display**: Small gray text under verse cards showing translation name — no link to Tanzil, no licensing info
- **JSON structure**: `{id, name, transliteration, translation, type, total_verses, verses: [{id, text, translation}]}`

## Requirements

### 1. Replace `quran_tr.json` with Tanzil-sourced data
- Download Turkish translation directly from Tanzil.net (e.g., `tr.diyanet`, `tr.yazir`, or another appropriate translation)
- Tanzil provides XML/TXT/SQL formats — a converter to the current JSON schema is needed
- Decision needed: which Turkish translation to use (see available options below)
- Preserve current JSON structure OR adapt `data_loader.py` to handle the new format

**Available Turkish translations on Tanzil:**

| Translator | Tanzil ID | Notes |
|---|---|---|
| Diyanet İşleri | `tr.diyanet` | Official state translation |
| Diyanet Vakfı | `tr.vakfi` | Religious foundation translation |
| Elmalılı Hamdi Yazır | `tr.yazir` | Classical scholarly, widely respected |
| Ali Bulaç | `tr.bulac` | Modern interpretation |
| Yaşar Nuri Öztürk | `tr.ozturk` | Modern scholarly |
| Süleyman Ateş | `tr.ates` | Academic |
| Suat Yıldırım | `tr.yildirim` | Contemporary |
| Edip Yüksel | `tr.yuksel` | Contemporary interpretation |
| Abdulbaki Gölpınarlı | `tr.golpinarli` | Classical |

### 2. Adapt vector indexing pipeline
- **`backend/src/data_loader.py`** (lines 118-151): `QuranChunk` dataclass and JSON parsing — update field mapping if structure changes
- **`backend/src/indexer.py`** (lines 150-159): Extracts `chunk.translation` for embedding — verify field name matches new data
- **Payload fields**: `id, surah_id, surah_name, surah_name_arabic, surah_transliteration, surah_type, verse_id, arabic_text, translation, translation_normalized, translation_lemma`
- Add a `translation_source` metadata field to payloads (e.g., `"Tanzil.net - Diyanet İşleri"`)
- Re-index `quran_tr` collection after data replacement (6,236 vectors, ~$0.50 embedding cost)

### 3. Display source attribution on the site
- **Backend**: Update hardcoded `"Diyanet Isleri Baskanligi"` in `compare.py` and `compare_helpers.py` to include Tanzil attribution
- **Frontend**: Add visible Tanzil.net attribution with link — required by CC-BY-3.0 license
  - `frontend/components/compare/source-reference-card.tsx` (line 95): Currently shows `verse.translation` as plain text
  - `frontend/components/compare/citation-hover-card.tsx` (line 72): Same
  - Consider adding a footer or info section: "Quran text courtesy of Tanzil.net" with hyperlink
  - `frontend/components/compare/source-badge.tsx`: Could add tooltip with source info

## Tanzil Licensing Requirements

- **Quran text**: CC-BY-3.0 — must attribute with link to tanzil.net
- **Translations**: Non-commercial use; must link to https://tanzil.net/trans/ if using >3 translations
- **Text integrity**: Quran text cannot be modified/changed

## Context

- Tanzil download page: https://tanzil.net/download/
- Tanzil translations: https://tanzil.net/trans/
- Current data CDN: https://cdn.jsdelivr.net/npm/quran-json@3.1.2/dist/quran_tr.json
- Related metadata: https://tanzil.net/docs/quran_metadata
