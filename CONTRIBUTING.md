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

```bash
uv run sphinx-build -W -n -b dirhtml docs docs/_build/html
```

The documentation in `docs/` is published at
<https://modsmith.meneither.site/modsmith/> from `main`. Its command and
settings reference is generated from the code on every build, so a new option
only needs good help text.

Tests do not use mocks. Platforms are real `Platform` subclasses that serve a
catalogue from memory (`tests/lib/catalog.py`), and settings are isolated
through environment variables.

## Branches

`main` holds released work and new versions are developed on `develop`. Build
each feature on its own branch cut from `develop`, and merge it back through a
pull request.

## Releasing

Releases are published on GitHub, built from a tag.

1. Make sure the `modsmith` version the app needs is on PyPI. If
   `[tool.uv.sources]` names `modsmith`, remove that line and run `uv lock`, so
   the app is built and tested against the published library.
2. Set `version` in `pyproject.toml` and move the `Unreleased` notes in
   `CHANGELOG.md` under the new version.
3. Merge `develop` into `main`.
4. Push a tag such as `v0.1.0`. The tag must match the project version, and the
   release notes come from that version's section of `CHANGELOG.md`.
