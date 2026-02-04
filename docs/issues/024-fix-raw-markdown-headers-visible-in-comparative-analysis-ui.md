---
number: 24
title: "Fix raw Markdown headers visible in Comparative Analysis UI"
labels: [bug]
date: 2026-02-01
url: https://github.com/aliozdenisik/Clarus/issues/24
status: open
---

# Fix raw Markdown headers visible in Comparative Analysis UI

## Description
In the Comparative Analysis (Compare) mode, the UI displays raw Markdown header syntax (e.g., `## Title`) instead of rendering it as a formatted header or hiding it. This occurs in the "Comparative Analysis" section and potentially others like "Old Testament" or "New Testament" within the comparison view.

## Steps to Reproduce
1. Navigate to the Compare page.
2. Enter a search term (e.g., "livre").
3. Wait for the analysis to complete.
4. Observe the "Karşılaştırılmalı Değerlendirme" (Comparative Analysis) card.
5. Note that the text begins with `## Karşılaştırılmalı Değerlendirme` or similar raw Markdown.

## Context
- User reports this issue **only** occurs in Compare mode, not in Normal Search.
- Screenshots show `## Eski Ahit`, `## Yeni Ahit`, and `## Karşılaştırılmalı Değerlendirme` visible as plain text.
- This suggests the frontend component rendering the agent response is not stripping or parsing the markdown headers correctly, or the backend is including them redundantly.
