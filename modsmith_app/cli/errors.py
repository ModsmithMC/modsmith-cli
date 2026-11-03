"""Turn errors into short messages with a hint, instead of tracebacks."""

import functools
from collections.abc import Callable

import typer
from modsmith.errors import LockedError, ModsmithError, NetworkError
from rich.console import Console
from rich.text import Text

from ..core.errors import AppError

BUSY = 429


def _network_hint(error: NetworkError) -> str | None:
    """Say what to do about a failed request, going by its status."""
    if error.status is None:
        return "Check your internet connection, then try again."
    if error.status == BUSY or error.status >= 500:
        return "The service is busy or having trouble. Try again later."
    return None


def describe(error: AppError | ModsmithError) -> tuple[str, str | None]:
    """Return a message and a hint for an app or library error."""
    if isinstance(error, AppError):
        return error.message, error.hint
    if isinstance(error, LockedError):
        return str(
            error
        ), "Another Modsmith is changing these files. Try again when it is done."
    if isinstance(error, NetworkError):
        return str(error), _network_hint(error)
    return str(error), None


def report(error: AppError | ModsmithError, prefix: str = "") -> None:
    """Print an error's message and hint to standard error.

    Args:
        error: The error.
        prefix: Shown instead of ``Error:``, for errors that did not stop the
            command.
    """
    message, hint = describe(error)
    console = Console(stderr=True, highlight=False)
    label = (prefix, "yellow") if prefix else ("Error: ", "bold red")
    console.print(Text.assemble(label, message), soft_wrap=True)
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
