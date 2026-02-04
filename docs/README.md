# Documentation

This folder contains project documentation, organized for easy navigation.

## Folder Structure

```
docs/
├── README.md                           # This file
├── architecture/                       # System architecture & design docs
│   └── CONFIDENCE_SCORING.md           # Confidence scoring system design
├── guides/                             # Setup and usage guides
│   ├── ATTRIBUTION.md                  # Attribution & licensing info
│   └── google-oauth-setup.md           # Google OAuth configuration guide
├── research/                           # Research documents & findings
│   ├── biblical-resources-research.md  # Bible text sources research
│   └── GREEK_TRANSLITERATION_RESEARCH.md # Greek transliteration study
├── issues/                             # Bug reports and improvements
│   ├── README.md                       # Issue tracker index
│   ├── 001-new-testament-citation-formatting.md
│   ├── 002-compare-stats-zeroed-out.md
│   ├── 003-inconsistent-search-navigation.md
│   ├── 004-missing-apocrypha-book-count.md
│   ├── 005-align-compare-page-ui.md
│   ├── 006-replace-quran-data-with-tanzil-source.md
│   ├── 007-compare-citation-hover-missing.md
│   └── 024-fix-raw-markdown-headers-visible-in-comparative-analysis-ui.md
├── proposals/                          # Feature proposals and RFCs
│   ├── 001-history-rerun-search.md           # (Implemented)
│   ├── 002-history-result-snapshots.md       # (Implemented)
│   ├── 003-multilingual-query-translation.md
│   ├── 004-realistic-confidence-scoring.md
│   ├── 005-save-and-share-results.md
│   ├── 006-quran-keyword-search.md           # (Implemented)
│   ├── 007-quran-keyword-search-frontend.md  # (Implemented)
│   ├── 008-bible-keyword-search-expansion.md
│   └── 009-tanzil-net-verified-turkish-quran-source.md
├── security/                           # Security audits and documentation
│   └── SECURITY_AUDIT_2026-02-03.md    # Security audit report
└── archive/                            # Archived/obsolete files
    └── OPEN_ISSUES.md.archived         # Old issue tracking file
```

## Quick Links

### For Bug Reports and Improvements
👉 **[View All Issues](issues/README.md)**

Current open issues: **8**
- Issues are numbered sequentially with 3-digit prefixes (001, 002, etc.)

### For Feature Proposals
👉 **[View All Proposals](proposals/)**

Recent proposals:
- [RFC-001: History Page Re-run Search](proposals/001-history-rerun-search.md) ✅ Implemented
- [RFC-002: History Result Snapshots](proposals/002-history-result-snapshots.md) ✅ Implemented
- [RFC-006: Quran Keyword Search](proposals/006-quran-keyword-search.md) ✅ Implemented
- [RFC-009: Tanzil.net Verified Turkish Quran Source](proposals/009-tanzil-net-verified-turkish-quran-source.md) 📝 Draft

### For Setup Guides
- [Google OAuth Setup Guide](guides/google-oauth-setup.md)
- [Attribution & Licensing](guides/ATTRIBUTION.md)

### For Architecture & Research
- [Confidence Scoring System](architecture/CONFIDENCE_SCORING.md)
- [Biblical Resources Research](research/biblical-resources-research.md)
- [Greek Transliteration Research](research/GREEK_TRANSLITERATION_RESEARCH.md)

## Terminology

| Term | Definition | Example |
|------|------------|---------|
| **Issue** | A bug, UX problem, or technical debt item | "Stats showing 0 on compare page" |
| **Proposal** | A design document for a new feature or major change | "Add history re-run functionality" |
| **RFC** | Request for Comments (another name for proposal) | Same as proposal |
| **Architecture** | System design and technical specifications | Confidence scoring algorithms |
| **Research** | Investigative documents and findings | Bible source comparison |

## How to Use This Documentation

### I Found a Bug
1. Check [issues/README.md](issues/README.md) to see if it's already reported
2. If not, create a new issue file in `issues/` using the template
3. Use the next sequential number (e.g., `008-my-issue.md`)
4. Update `issues/README.md` with your new issue

### I Have a Feature Idea
1. Create a new proposal in `proposals/` using the RFC template from existing files
2. Number it sequentially (e.g., `010-my-feature.md`)
3. Share it with the team for feedback

### I Need Setup Help
- Check the existing guides in `guides/`
- If missing, create a new guide in `guides/`

### I'm Working on Architecture
- Review existing architecture docs in `architecture/`
- Add new design documents here for system-level changes

## Contributing

When adding documentation:
- Use clear, descriptive filenames (e.g., `001-fix-citation-bug.md` not `bug1.md`)
- Keep each file focused on one topic
- Update the relevant README when adding new files
- Archive old/obsolete files in `archive/` instead of deleting them
- Use 3-digit sequential numbering for issues and proposals

---

**Last Updated:** 2026-02-04
