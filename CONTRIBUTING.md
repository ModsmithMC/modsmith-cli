# Contributing

## Setup

You need [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

```bash
uv run pre-commit install
```

Until the next library release, the app follows the library's development
branch through `[tool.uv.sources]` in `pyproject.toml`. To work on both at once,
install your library checkout into this environment:

```bash
uv pip install -e ../CurseCraft
```

`uv sync` puts the pinned version back.

## Code layout

| Folder | Holds |
| :--- | :--- |
| `modsmith_app/core` | What the command line and the GUI share. It never prints or asks. |
| `modsmith_app/cli` | The `modsmith` command, built with Typer and Rich. |

The app uses only the library's public API.

## Checks

```bash
uv run ruff check .
```

```bash
uv run pyright
```

```bash
uv run pytest --cov
```

Tests do not use mocks. Platforms are real `Platform` subclasses that serve a
catalogue from memory (`tests/lib/catalog.py`), and settings are isolated
through environment variables.

## Branches

`main` holds released work and new versions are developed on `develop`. Build
each feature on its own branch cut from `develop`, and merge it back through a
pull request.
