"""The ``modsmith`` command and its global options."""

import io
import logging
import sys
from pathlib import Path
from typing import Annotated, TextIO

import typer
from rich.logging import RichHandler

from . import __version__
from .commands.config import config_app
from .commands.contents import (
    add_command,
    adopt_command,
    disable_command,
    enable_command,
    pin_command,
    remove_command,
    show_command,
    unpin_command,
)
from .commands.discovery import info_command, loaders_command
from .commands.install import create_command, install_command
from .commands.instance import delete_command, import_command, move_command
from .commands.list import list_command
from .commands.search import search_command
from .commands.update import update_command
from .context import AppContext, ColorMode, Services
from .core.paths import AppPaths
from .errors import reported
from .target import examples

app = typer.Typer(
    help=(
        "Install Minecraft modpacks, mods, resource packs and shaders "
        "for the official launcher."
    ),
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    rich_markup_mode=None,
)


def _show_version(value: bool) -> None:
    if value:
        typer.echo(f"modsmith {__version__}")
        raise typer.Exit


@app.callback()
def root(
    ctx: typer.Context,
    instances_dir: Annotated[
        Path | None,
        typer.Option("--instances-dir", help="Use this instances folder for this run."),
    ] = None,
    game_dir: Annotated[
        Path | None,
        typer.Option("--game-dir", help="Use this game directory for this run."),
    ] = None,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose", "-v", count=True, help="Show more detail. Repeat for more."
        ),
    ] = 0,
    color: Annotated[
        ColorMode,
        typer.Option("--color", help="When to use colour. NO_COLOR also turns it off."),
    ] = ColorMode.AUTO,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_show_version,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Set up the run before any command."""
    services = ctx.obj if isinstance(ctx.obj, Services) else Services()
    environ = services.environ
    paths = (
        AppPaths.from_environment()
        if environ is None
        else AppPaths.from_environment(environ)
    )
    overrides: dict[str, object] = {}
    if instances_dir is not None:
        overrides["instances_dir"] = instances_dir.expanduser()
    if game_dir is not None:
        overrides["game_dir"] = game_dir.expanduser()
    context = AppContext(paths, services, overrides, verbose=verbose, color=color)
    if verbose:
        level = logging.INFO if verbose == 1 else logging.DEBUG
        handler = RichHandler(console=context.err, show_path=False)
        logging.basicConfig(level=level, handlers=[handler], force=True)
    ctx.obj = context


app.command(
    "install",
    epilog=examples(
        "modsmith install fabulously-optimized",
        "modsmith install curseforge:all-the-mods-9 --name atm9",
        "modsmith install Downloads/pack.mrpack --all-optional",
        "modsmith install curseforge:some-pack --from Downloads/manual",
    ),
)(reported(install_command))
app.command(
    "create",
    epilog=examples(
        "modsmith create vanilla --minecraft 1.21.1",
        "modsmith create modded --minecraft 1.21.1 --loader fabric",
        "modsmith create old --minecraft 1.20.1 --loader forge --loader-version 47.3.0",
    ),
)(reported(create_command))
app.command("list")(reported(list_command))
app.command(
    "search",
    epilog=examples(
        "modsmith search sodium",
        'modsmith search "fabulously optimized" --type modpack',
        "modsmith search shaders --type shader --sort downloads",
        "modsmith search jei --platform all --minecraft 1.20.1 --loader forge",
    ),
)(reported(search_command))
app.command("show", epilog=examples("modsmith show", "modsmith show survival"))(
    reported(show_command)
)
app.command(
    "add",
    epilog=examples(
        "modsmith add survival sodium lithium",
        "modsmith add survival curseforge:jei",
        "modsmith add survival complementary-reimagined --type shader",
    ),
)(reported(add_command))
app.command(
    "remove",
    epilog=examples(
        "modsmith remove survival sodium", "modsmith remove iris --keep-deps"
    ),
)(reported(remove_command))
app.command("enable", epilog=examples("modsmith enable survival sodium"))(
    reported(enable_command)
)
app.command(
    "disable",
    epilog=examples(
        "modsmith disable survival sodium",
        "modsmith disable survival mods/OptiFine.jar",
    ),
)(reported(disable_command))
app.command("pin", epilog=examples("modsmith pin survival sodium"))(
    reported(pin_command)
)
app.command("unpin", epilog=examples("modsmith unpin survival sodium"))(
    reported(unpin_command)
)
app.command(
    "adopt",
    epilog=examples("modsmith adopt survival", "modsmith adopt survival -p modrinth"),
)(reported(adopt_command))
app.command(
    "info",
    epilog=examples(
        "modsmith info sodium",
        "modsmith info curseforge:jei --minecraft 1.20.1 --loader forge",
        "modsmith info fabulously-optimized --type modpack",
    ),
)(reported(info_command))
app.command(
    "loaders",
    epilog=examples(
        "modsmith loaders fabric 1.21.1", "modsmith loaders forge 1.20.1 --all"
    ),
)(reported(loaders_command))
app.command(
    "update",
    epilog=examples(
        "modsmith update survival",
        "modsmith update survival --dry-run",
        "modsmith update survival --pack-only --optional shaders",
        "modsmith update atm9 --file Downloads/atm9-1.2.zip",
    ),
)(reported(update_command))
app.command(
    "import",
    epilog=examples(
        'modsmith import "My Fabric world"', "modsmith import old-pack --dry-run"
    ),
)(reported(import_command))
app.command(
    "move",
    epilog=examples(
        "modsmith move survival creative", "modsmith move survival D:/Games/survival"
    ),
)(reported(move_command))
app.command("delete", epilog=examples("modsmith delete survival"))(
    reported(delete_command)
)
app.add_typer(config_app, name="config")


def tolerate_unencodable(*streams: TextIO) -> None:
    """Write characters an output cannot encode as ``?`` instead of failing.

    Piped or redirected output uses the system code page, so that the shell
    reading it decodes it correctly. On Windows that code page often cannot
    hold the emoji found in project names and summaries.
    """
    for stream in streams:
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="replace")


def main() -> None:
    """Run the command line."""
    tolerate_unencodable(sys.stdout, sys.stderr)
    app()
