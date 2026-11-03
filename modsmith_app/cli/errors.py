"""Turn errors into short messages with a hint, instead of tracebacks."""

import functools
from collections.abc import Callable
from dataclasses import dataclass, field

import typer
from modsmith.errors import (
    Cancelled,
    DependencyError,
    DownloadError,
    LockedError,
    ModsmithError,
    NetworkError,
    UnresolvedEntriesError,
)
from rich.console import Console
from rich.text import Text

from ..core.errors import AppError

BUSY = 429
# The exit status of a command stopped with Ctrl+C, as shells expect.
INTERRUPTED = 130


@dataclass(frozen=True)
class Report:
    """What to tell the player about an error.

    Attributes:
        message: What went wrong.
        hint: What to do about it, or None.
        details: One line per item that failed, such as each file.
    """

    message: str
    hint: str | None = None
    details: list[str] = field(default_factory=list[str])


def _network_hint(error: NetworkError) -> str | None:
    """Say what to do about a failed request, going by its status."""
    if error.status is None:
        return "Check your internet connection, then try again."
    if error.status == BUSY or error.status >= 500:
        return "The service is busy or having trouble. Try again later."
    return None


def _unresolved(error: UnresolvedEntriesError) -> Report:
    details: list[str] = []
    for entry in error.entries:
        name = entry.path or (
            entry.ref and f"{entry.ref.platform} file {entry.ref.file_id}"
        )
        page = f"  download it from {entry.manual_url}" if entry.manual_url else ""
        details.append(f"{name}{page}")
    return Report(
        f"{len(error.entries)} files cannot be downloaded automatically.",
        "Download them by hand into one folder, then run the command again "
        "with --from <folder>.",
        details,
    )


def _dependencies(error: DependencyError) -> Report:
    resolution = error.plan.resolution
    details = [
        f"{item.release.name} cannot be used with {item.chosen.name}"
        for item in resolution.conflicts
    ]
    details += [
        f"{item.release.name} needs "
        f"{item.dependency.project_id or item.dependency.release_id}, "
        "which has no release for this instance"
        for item in resolution.missing
        if item.dependency.kind == "required"
    ]
    return Report("Nothing was installed, because of these problems.", None, details)


def describe(error: AppError | ModsmithError) -> Report:
    """Describe an app or library error for the player."""
    if isinstance(error, AppError):
        return Report(error.message, error.hint)
    if isinstance(error, Cancelled):
        return Report(
            "Cancelled.",
            "Nothing was changed. Run the command again to carry on where it stopped.",
        )
    if isinstance(error, LockedError):
        return Report(
            str(error),
            "Another Modsmith is changing these files. Try again when it is done.",
        )
    if isinstance(error, DownloadError):
        return Report(
            str(error),
            "Nothing was changed. Run the command again to retry.",
            list(error.failures),
        )
    if isinstance(error, UnresolvedEntriesError):
        return _unresolved(error)
    if isinstance(error, DependencyError):
        return _dependencies(error)
    if isinstance(error, NetworkError):
        return Report(str(error), _network_hint(error))
    return Report(str(error))


def report(
    error: AppError | ModsmithError, console: Console | None = None, prefix: str = ""
) -> None:
    """Print an error's message, details and hint to standard error.

    Args:
        error: The error.
        console: Where to print. Defaults to standard error.
        prefix: Shown instead of ``Error:``, for errors that did not stop the
            command.
    """
    found = describe(error)
    out = console or Console(stderr=True, highlight=False)
    label = (prefix, "yellow") if prefix else ("Error: ", "bold red")
    out.print(Text.assemble(label, found.message), soft_wrap=True)
    for line in found.details:
        out.print(Text(f"  {line}"), soft_wrap=True)
    if found.hint:
        # Hints often hold a command, which must stay on one line to be copied.
        out.print(Text(found.hint, style="dim"), soft_wrap=True)


def _console(kwargs: dict[str, object]) -> Console | None:
    """Find the run's error console through the command's context, if it has one."""
    ctx = kwargs.get("ctx")
    if isinstance(ctx, typer.Context):
        root = ctx.find_root().obj
        return getattr(root, "err", None)
    return None


def reported[**P, R](command: Callable[P, R]) -> Callable[P, R]:
    """Wrap a command so known errors are reported and end the command.

    Cancelled commands and Ctrl+C exit with 130, other errors with 1.
    """

    @functools.wraps(command)
    def run(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return command(*args, **kwargs)
        except Cancelled as e:
            report(e, _console(kwargs))
            raise typer.Exit(INTERRUPTED) from e
        except KeyboardInterrupt as e:
            report(Cancelled(), _console(kwargs))
            raise typer.Exit(INTERRUPTED) from e
        except (AppError, ModsmithError) as e:
            report(e, _console(kwargs))
            raise typer.Exit(1) from e

    return run
