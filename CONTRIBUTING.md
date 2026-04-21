# Contributing to Launchpad AI

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/shawmillerman/launchpad_ai.git
cd launchpad_ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
```

## Development Guidelines

- **Configuration over code** — prefer YAML/JSON config changes over hardcoded logic
- **Keep it generic** — Launchpad AI is application-agnostic; domain logic belongs in your app layer
- **Test your changes** — add tests under `tests/` for any new modules
- **Document decisions** — add an entry to `docs/DECISIONS.md` for architectural choices

## Pull Request Process

1. Fork the repo and create a feature branch (`git checkout -b feature/my-feature`)
2. Make your changes with clear, descriptive commits
3. Ensure existing tests pass (`pytest`)
4. Open a pull request with a description of what you changed and why

## Reporting Issues

Open a GitHub issue with:
- A clear title and description
- Steps to reproduce (if a bug)
- Expected vs actual behavior

## Code Style

- Python: follow PEP 8
- Docstrings on all public functions and classes
- Type hints encouraged
