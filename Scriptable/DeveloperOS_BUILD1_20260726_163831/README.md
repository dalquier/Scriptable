# DeveloperOS BUILD-1

BUILD-1 provides a small, deterministic Python 3.11+ kernel with typed configuration, a service container, aggregate health, safe diagnostics, structured logging and a command-line interface.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Use

```bash
developeros run
developeros health
developeros diagnostics
python scripts/run_demo.py
```

## Validate

```bash
python scripts/validate_build1.py
```

Configuration precedence is: built-in defaults, optional TOML file, `DEVELOPEROS_*` environment variables, explicit overrides. See `docs/` for the architecture and acceptance evidence.
