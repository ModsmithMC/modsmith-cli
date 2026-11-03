"""Turn errors into short messages with a hint, instead of tracebacks."""

import functools
from collections.abc import Callable

import typer
from modsmith.errors import LockedError, ModsmithError, NetworkError
from rich.console import Console
from rich.text import Text

from ..core.errors import AppError

HINTS: list[tuple[type[ModsmithError], str]] = [
    (
        LockedError,
        "Another Modsmith is changing these files. Try again when it is done.",
    ),
    (NetworkError, "Check your internet connection, then try again."),
]


def describe(error: AppError | ModsmithError) -> tuple[str, str | None]:
    """Return a message and a hint for an app or library error."""
    if isinstance(error, AppError):
        return error.message, error.hint
    hint = next((text for kind, text in HINTS if isinstance(error, kind)), None)
    return str(error), hint


def report(error: AppError | ModsmithError) -> None:
    """Print an error's message and hint to standard error."""
    message, hint = describe(error)
    console = Console(stderr=True, highlight=False)
    console.print(Text.assemble(("Error: ", "bold red"), message), soft_wrap=True)
    if hint:
        # Hints often hold a command, which must stay on one line to be copied.
        console.print(Text(hint, style="dim"), soft_wrap=True)


def reported[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    """Wrap a command so app and library errors are reported, then exit with 1."""

    @functools.wraps(command)
    def run(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return command(*args, **kwargs)
        except (AppError, ModsmithError) as e:
            report(e)
            raise typer.Exit(1) from e

    return run
