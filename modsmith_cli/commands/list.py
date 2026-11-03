"""``modsmith list``: list the player's instances."""

import typer
from modsmith.instances import InstanceState
from rich.table import Table
from rich.text import Text

from ..context import get
from ..core.registry import list_instances
from .install import loader_label


def _loader(state: InstanceState) -> str:
    if not state.loader_kind:
        return "vanilla"
    return loader_label(state.loader_kind, state.loader_version)


def _pack(state: InstanceState) -> str:
    if not state.pack_name:
        return "-"
    return " ".join(part for part in (state.pack_name, state.pack_version) if part)


def list_command(ctx: typer.Context) -> None:
    """List your instances."""
    app = get(ctx)
    entries = list_instances(app.config, app.paths)
    if not entries:
        app.out.print("No instances yet.")
        app.out.print(
            "Install a pack with modsmith install, or start one with modsmith create.",
            style="dim",
        )
        return
    table = Table(box=None, pad_edge=False)
    for column in ("Name", "Minecraft", "Loader", "Pack"):
        table.add_column(column)
    table.add_column("Folder", overflow="fold")
    for entry in entries:
        folder = str(entry.path) if entry.external else ""
        if entry.state is None:
            problem = Text(entry.problem or "", style="red")
            table.add_row(entry.name, "", "", problem, folder)
            continue
        state = entry.state
        table.add_row(entry.name, state.minecraft, _loader(state), _pack(state), folder)
    app.out.print(table)
