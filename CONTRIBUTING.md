# Contributing to CipherQuorum

CipherQuorum is designed to be approachable for contributors who want to work on
cryptography, networking, CLI tooling, or documentation.

## Development Setup

```powershell
uv run --extra dev pytest
uv run --extra dev ruff check .
```

If you prefer a traditional virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
pytest
ruff check .
```

## Good First Areas

- Add edge-case tests for Shamir reconstruction.
- Improve LAN timeout and retry behavior.
- Add structured logging or a `--verbose` mode.
- Add examples for multi-machine demos.
- Harden peer identity and trust prompts.

## Pull Request Expectations

- Keep changes focused.
- Add or update tests when behavior changes.
- Run the test and lint commands before opening a pull request.
- Document user-facing CLI changes in `README.md`.

## Security

Please do not open a public issue with a live secret, private key, API token, or
reproduction that exposes someone else's credentials. Use placeholders in examples.
