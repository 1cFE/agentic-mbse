# Python Environment Rules

## Why uv?

This project uses `uv` for Python package management and script execution. All Python commands must use the `uv run` prefix to ensure the correct virtual environment and dependencies are used.

## Correct Usage

```bash
# Running Python scripts
uv run python script.py

# Running modules
uv run python -m pytest

# Installing packages
uv add package_name

# Running syside (SysML parser)
uv run syside check models/path/to/file.sysml

# Running agentic-mbse CLI
uv run agentic-mbse validate models/
uv run agentic-mbse --help
```

## Incorrect Usage

```bash
python script.py        # WRONG - uses system Python
python3 script.py       # WRONG - uses system Python
pip install package     # WRONG - installs to wrong env
syside check file.sysml # WRONG - unless uv shell is active
```

## Rationale

- Ensures correct virtual environment is used
- Manages dependencies consistently
- Project has `pyproject.toml` configured for uv
- Local path dependencies (agentic-mbse, sysml-codegen, teax) require uv resolution
