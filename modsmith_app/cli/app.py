"""The ``modsmith`` command and its global options."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.logging import RichHandler

from .. import __version__
from ..core.paths import AppPaths
from .config_cmd import config_app
from .context import AppContext, Services
from .errors import reported
from .list_cmd import list_command
from .search_cmd import search_command

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
    context = AppContext(paths, services, overrides)
    if verbose:
        level = logging.INFO if verbose == 1 else logging.DEBUG
        handler = RichHandler(console=context.err, show_path=False)
        logging.basicConfig(level=level, handlers=[handler], force=True)
    ctx.obj = context


app.command("list")(reported(list_command))
app.command("search")(reported(search_command))
app.add_typer(config_app, name="config")


def main() -> None:
    """Run the command line."""
    app()
