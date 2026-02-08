# Contributing to Clarus

First off, thank you for considering contributing to Clarus! It's people like you that make Clarus such a great tool for exploring sacred texts.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for Qdrant and PostgreSQL)
- Git

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/Clarus.git
   cd Clarus
   ```

2. **Set up the backend**

   ```bash
   # Install uv (if not present)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   cd backend
   uv sync

   # Copy environment file
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Set up the frontend**

   ```bash
   cd frontend
   npm install
   ```

4. **Start infrastructure**

   ```bash
   # From project root
   docker compose up -d
   ```

5. **Verify setup**

   ```bash
   # Backend
   cd backend
   python main.py info

   # Frontend
   cd frontend
   npm run dev
   ```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the behavior
- Expected behavior vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs or error messages

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) when opening an issue.

### Suggesting Features

Feature requests are welcome! Please use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- A clear use case for the feature
- Why existing functionality doesn't meet your needs
- Possible implementation approaches (optional)

### Your First Code Contribution

Looking for something to work on? Check out issues labeled:

- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `documentation` - Improvements to docs

### Pull Requests

1. **Create a branch**

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**

   - Write clear, commented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**

   ```bash
   # Backend linting
   cd backend
   ruff check .
   ruff format .

   # Frontend linting and tests
   cd frontend
   npm run lint
   npm test
   ```

4. **Commit your changes**

   Follow [Conventional Commits](https://www.conventionalcommits.org/):

   ```bash
   git commit -m "feat: add new search filter option"
   git commit -m "fix: resolve cache invalidation bug"
   git commit -m "docs: update API documentation"
   ```

5. **Push and create a PR**

   ```bash
   git push origin feature/your-feature-name
   ```

   Then open a Pull Request on GitHub.

## Pull Request Process

1. Fill out the PR template completely
2. Ensure all CI checks pass
3. Request review from maintainers
4. Address any feedback
5. Once approved, a maintainer will merge your PR

### PR Checklist

- [ ] I have read the contributing guidelines
- [ ] My code follows the project's style guidelines
- [ ] I have added tests that prove my fix/feature works
- [ ] I have updated the documentation accordingly
- [ ] All new and existing tests pass

## Style Guidelines

### Python (Backend)

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting
- Type hints are required for all function signatures
- Docstrings for public functions (Google style)

```python
def search_quran(query: str, top_k: int = 10) -> list[SearchResult]:
    """Search the Quran collection.

    Args:
        query: The search query string.
        top_k: Maximum number of results to return.

    Returns:
        List of SearchResult objects ordered by relevance.
    """
    pass
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Follow ESLint configuration
- Prefer functional components with explicit prop types
- Use `cn()` utility for conditional classNames

```typescript
interface SearchResultProps {
  result: SearchResult;
  onSelect: (id: string) => void;
}

export function SearchResult({ result, onSelect }: SearchResultProps) {
  return (
    <div className={cn("p-4", result.highlighted && "bg-yellow-50")}>
      {/* ... */}
    </div>
  );
}
```

### Commit Messages

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit first line to 72 characters
- Reference issues when applicable

### Documentation

- Keep README.md up to date
- Document new features in relevant docs
- Include code examples where helpful
- Use clear, concise language

## Project Structure

```
Clarus/
├── backend/           # Python FastAPI backend
│   ├── app/           # API routes and auth
│   ├── src/           # Core RAG pipeline
│   ├── data/          # Source JSON files
│   └── tests/         # Backend tests
├── frontend/          # Next.js frontend
│   ├── app/           # App Router pages
│   ├── components/    # React components
│   └── lib/           # Utilities and hooks
└── docs/              # Additional documentation
```

## Community

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

## Recognition

Contributors are recognized in our README and release notes. Thank you for helping make Clarus better!

---

If you have questions, feel free to open a Discussion or reach out to the maintainers.
