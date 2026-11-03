"""How commands talk to the player: plans, confirmation, progress and Ctrl+C."""

import signal
from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from types import FrameType

import typer
from modsmith.instances import Changes
from modsmith.progress import CancelToken, Progress, ProgressCallback
from rich.progress import (
    BarColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.progress import Progress as Bars
from rich.text import Text

from .context import AppContext
from .core.errors import AppError

# How many paths of each kind a plan lists before summing up the rest.
SHOWN_PER_KIND = 12
TASK_NAMES = {
    "files": "Downloading files",
    "overrides": "Writing pack files",
    "minecraft": "Downloading Minecraft",
    "libraries": "Downloading libraries",
    "java": "Downloading Java",
    "identify": "Reading files",
    "fetch": "Downloading",
    "download": "Downloading",
    "processors": "Running installer steps",
}


@dataclass(frozen=True)
class PlanRow:
    """One kind of change in a plan, as shown to the player."""

    symbol: str
    style: str
    label: str
    paths: tuple[str, ...]


def _size(total: int) -> str:
    """Format a byte count, such as 12.3 MB."""
    size = float(total)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1000 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1000
    return f"{size:.1f} GB"


def show_plan(
    app: AppContext,
    changes: Changes,
    sizes: Mapping[str, int | None] | None = None,
    *,
    title: str | None = None,
    notes: Sequence[Text] = (),
) -> bool:
    """Print what a change would do. Returns False if it would change nothing.

    Args:
        app: The run.
        changes: The changes, from a library diff or plan.
        sizes: The download size of each path, where known.
        title: A heading for the plan.
        notes: Lines to print after the changes and before the summary.
    """
    rows = [
        PlanRow("+", "green", "add", changes.added),
        PlanRow("~", "cyan", "update", changes.updated),
        PlanRow("-", "red", "remove", changes.removed),
        PlanRow("!", "yellow", "keep your version of", changes.conflicts),
        PlanRow("!", "yellow", "keep, though no longer needed,", changes.orphaned),
    ]
    if title:
        app.out.print(Text(title, style="bold"))
    for row in rows:
        listed = row.paths if app.verbose else row.paths[:SHOWN_PER_KIND]
        for path in listed:
            app.out.print(Text.assemble((f"  {row.symbol} ", row.style), path))
        hidden = len(row.paths) - len(listed)
        if hidden:
            app.out.print(Text(f"  {row.symbol} and {hidden} more", style=row.style))
    for path in changes.superseded:
        app.out.print(Text.assemble(("  = ", "dim"), f"{path} is now part of the pack"))
    for note in notes:
        app.out.print(note)
    counts = [f"{len(row.paths)} to {row.label}" for row in rows[:3] if row.paths]
    kept = len(changes.conflicts) + len(changes.orphaned)
    if kept:
        counts.append(f"{kept} of your changes kept")
    if not counts:
        app.out.print("Nothing to change.")
        return False
    pending = [*changes.added, *changes.updated]
    total = sum((sizes or {}).get(path) or 0 for path in pending)
    summary = ", ".join(counts)
    if total:
        summary += f"; {_size(total)} to download"
    app.out.print(Text(summary + ".", style="bold"))
    return True


def confirm(app: AppContext, question: str, *, yes: bool) -> None:
    """Ask before changing files, unless ``--yes`` was given.

    Raises:
        AppError: There is no terminal to ask in, so ``--yes`` is needed.
        typer.Exit: The player said no.
    """
    if yes:
        return
    if not app.services.interactive():
        raise AppError(
            "This command changes files and there is no terminal to confirm in.",
            hint="Run it again with --yes.",
        )
    if not typer.confirm(question, default=True):
        app.err.print("Nothing was changed.")
        raise typer.Exit(0)


def confirm_name(app: AppContext, name: str, *, yes: bool, force: bool) -> None:
    """Ask the player to type a name before something that cannot be undone.

    Raises:
        AppError: ``--yes`` was given without ``--force``, or there is no
            terminal.
        typer.Exit: The player typed something else.
    """
    if yes:
        if not force:
            raise AppError(
                "This cannot be undone, so --yes alone is not enough.",
                hint="Add --force as well.",
            )
        return
    if not app.services.interactive():
        raise AppError(
            "This command cannot be undone and there is no terminal to confirm in.",
            hint="Run it again with --yes --force.",
        )
    typed = typer.prompt(f"Type {name} to confirm", default="", show_default=False)
    if typed != name:
        app.err.print("Nothing was changed.")
        raise typer.Exit(0)


@contextmanager
def progress(app: AppContext) -> Generator[ProgressCallback]:
    """Show the library's progress updates as bars, when standard error is a terminal."""
    if not app.err.is_terminal:
        yield lambda update: None
        return
    columns = (
        TextColumn("{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    )
    with Bars(*columns, console=app.err, transient=True) as bars:
        tasks: dict[tuple[str, str], TaskID] = {}

        def update(item: Progress) -> None:
            key = (item.task, item.unit)
            if key not in tasks:
                label = TASK_NAMES.get(item.task, item.task.capitalize())
                tasks[key] = bars.add_task(label, total=item.total)
            bars.update(tasks[key], completed=item.current, total=item.total)

        yield update


@contextmanager
def cancellable() -> Generator[CancelToken]:
    """Turn the first Ctrl+C into a clean stop, through a `CancelToken`.

    The library then stops at a safe point and raises `Cancelled`. A second
    Ctrl+C stops at once.
    """
    token = CancelToken()
    previous = signal.getsignal(signal.SIGINT)

    def stop(signum: int, frame: FrameType | None) -> None:
        if token.cancelled:
            raise KeyboardInterrupt
        token.cancel()

    try:
        signal.signal(signal.SIGINT, stop)
    except ValueError:
        # Signal handlers can only be set from the main thread.
        yield token
        return
    try:
        yield token
    finally:
        signal.signal(signal.SIGINT, previous)


def show_changelog(app: AppContext, title: str, text: str, *, lines: int) -> None:
    """Print a changelog under a heading, cut to its first lines unless verbose."""
    kept = [line.rstrip() for line in text.strip().splitlines()]
    if not kept:
        return
    app.out.print(Text(title, style="bold"))
    shown = kept if app.verbose else kept[:lines]
    app.out.print(Text("\n".join(shown)))
    if len(shown) < len(kept):
        app.out.print(Text("... (-v shows all of it)", style="dim"))
