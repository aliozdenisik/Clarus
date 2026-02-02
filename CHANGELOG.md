# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Professional repository structure (LICENSE, CONTRIBUTING, CODE_OF_CONDUCT)
- GitHub templates for Issues and Pull Requests
- CI/CD workflow for automated testing
- Dependabot configuration for dependency updates
- Security policy

### Changed
- Standardized project documentation
- Improved .gitignore configuration

## [0.2.0-alpha] - 2026-02-02

### Added
- Latin alphabet (Buckwalter) transliteration for Arabic roots and derived words (#29)
  - Backend: `root_buckwalter` and `word_transliterations` fields in API response
  - Frontend: Latin text displayed below Arabic in root card and derived word chips
- Interactive derived word selection updates charts and statistics in real-time (#28)
  - Clicking a derived word filters verses, recalculates surah distribution chart, and updates stats bar
  - Chart title reflects selected word filter

### Fixed
- In-verse word highlighting now works correctly (#30)
  - Backend returns `token_clean` (normalized) instead of raw `token` (with diacritics)
  - Removed redundant "Matched words" footer from verse cards
- Removed technical Buckwalter source badge from root card for cleaner UI (#31)

### Changed
- Keyword search navigation link added to main navigation bar

## [1.0.0] - 2024-01-27

### Added
- Initial release of Clarus
- Hybrid RAG search engine with Qdrant
- Multi-agent comparative analysis system
- FastAPI backend with JWT authentication
- Next.js frontend application
