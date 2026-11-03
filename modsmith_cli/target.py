"""Shared arguments and help for commands that act on an instance."""

from typing import Annotated

import typer

from .core.config import load_config
from .core.errors import AppError
from .core.paths import AppPaths
from .core.registry import list_instances

# Click rewraps help text, except a paragraph whose first line is this mark.
KEEP_LINES = "\b"


def complete_instances(incomplete: str) -> list[str]:
    """Offer instance names for shell completion."""
    try:
        paths = AppPaths.from_environment()
        entries = list_instances(load_config(paths), paths)
    except AppError:
        return []
    return [entry.name for entry in entries if entry.name.startswith(incomplete)]


def examples(*lines: str) -> str:
    """Format example commands for the end of a command's help."""
    listed = "\n".join(f"  {line}" for line in lines)
    return f"Examples:\n\n{KEEP_LINES}\n{listed}"


InstanceName = Annotated[
    str | None,
    typer.Argument(
        help="The instance. Can be left out when you have only one.",
        autocompletion=complete_instances,
        show_default=False,
    ),
]
Yes = Annotated[bool, typer.Option("--yes", "-y", help="Do it without asking.")]
DryRun = Annotated[
    bool, typer.Option("--dry-run", help="Show what would change, and change nothing.")
]
