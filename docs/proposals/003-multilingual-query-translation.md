# RFC-003: Multilingual Query Translation

**Status**: Implemented (Phase 1)
**Created**: 2026-01-29
**Effort**: High

## Problem

Right now, Clarus works in two languages:
- **Quran searches must be in Turkish** (because the Quran text is in Turkish)
- **Bible searches must be in English** (because the Bible text is in English KJVA)

This means users who speak Spanish, French, Italian, Portuguese, Arabic, or any other language have to manually translate their questions before using Clarus. This creates unnecessary friction.

## Proposed Solution

Add automatic translation so users can search in any language they want, and get answers back in that same language.

### How It Would Work

**Example 1: Spanish User Asking About the Bible**
1. User types: *"¿Qué es el amor según la Biblia?"* (Spanish)
2. System detects Spanish, translates to English: *"What is love according to the Bible?"*
3. System searches the English Bible and generates an answer in English
4. System translates the answer back to Spanish
5. User receives answer in Spanish

**Example 2: French User Asking About the Quran**
1. User types: *"Qu'est-ce que la patience en Islam?"* (French)
2. System detects French, translates to Turkish: *"İslam'da sabır nedir?"*
3. System searches the Turkish Quran and generates an answer in Turkish
4. System translates the answer back to French
5. User receives answer in French

### What Gets Translated

**Translated:**
- User's question
- The answer text
- Verse text in search results

**Not Translated (kept in original form):**
- Book names: "Genesis", "Al-Baqarah", "Matthew"
- Source names: "Quran", "Bible", "Old Testament", "New Testament"
- Verse references: `[Bakara:153]`, `[John:3:16]`

## Implementation Approach

### Three-Step Process

1. **Detect Language** — Figure out what language the user is typing in
2. **Translate Query** — Convert the question to the right language (Turkish for Quran, English for Bible)
3. **Translate Response** — Convert the answer back to the user's language

### Language Support (Initial)

- English (native for Bible)
- Turkish (native for Quran)
- Spanish
- French
- Italian
- Portuguese
- Arabic
- German

More languages can be added later based on demand.

### Optional Language Override

Users can manually select their preferred language in settings instead of relying on auto-detection. This is useful if:
- They want to force a specific language
- Auto-detection is incorrect
- They're typing in mixed languages

## Cost Impact

- **With translation:** Adds about 20% to the cost per query (~$0.003 extra)
- **Without translation:** No change (if user already types in Turkish/English)

Translation is only applied when needed, so users who already use Turkish/English won't see any cost increase.

## Alternatives Considered

### 1. Create Separate Collections for Each Language
**Why Not:** Would require storing 10 copies of all verses (one per language), increasing storage by 10x. Also, maintaining consistency across translations would be a nightmare.

### 2. Use Google Translate
**Why Not:** Google Translate performs poorly with religious terminology. It doesn't understand the nuanced vocabulary of sacred texts.

### 3. Do Nothing (Current State)
**Why Not:** Forces users to manually translate their questions, creating friction and limiting global accessibility.

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Automatic translation** (proposed) | Users can search in any language, no manual work | Adds ~20% cost, 200-500ms latency |
| **Separate collections** | No translation needed, instant | 10x storage cost, maintenance burden |
| **No translation** (current) | No cost, no latency | Limited to Turkish/English speakers |

## Success Metrics

- Translation accuracy: 95%+ quality
- Latency: Less than 500ms extra delay
- Cost: Less than 20% increase per query
- Adoption: At least 30% of users search in non-Turkish/English languages

## Recommendation

Implement this feature in phases:
1. **Phase 1:** Build the translation system behind the scenes (not visible to users yet)
2. **Phase 2:** Test with a small group of users across multiple languages
3. **Phase 3:** Add a language selector in the UI
4. **Phase 4:** Expand to 20+ languages based on demand

This allows us to validate quality before rolling out to everyone.

---

**Last Updated:** 2026-01-30
