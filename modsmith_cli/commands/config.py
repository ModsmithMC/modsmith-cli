"""``modsmith config``: show and change settings."""

from typing import Annotated

import typer
from rich.table import Table

from ..context import get
from ..core import config as settings
from ..errors import reported

config_app = typer.Typer(
    help="Show and change settings. With no command, show them all.",
    invoke_without_command=True,
)

Key = Annotated[str, typer.Argument(help="The setting's name.", show_default=False)]


@config_app.callback()
@reported
def show_all(ctx: typer.Context) -> None:
    """Show every setting, its value and where the value comes from."""
    if ctx.invoked_subcommand is not None:
        return
    app = get(ctx)
    values = app.config.__dict__
    origins = settings.sources(app.paths, app.environ)
    table = Table(box=None, pad_edge=False)
    table.add_column("Setting", no_wrap=True)
    # Paths fold rather than shorten, so they can always be copied whole.
    table.add_column("Value", overflow="fold")
    table.add_column("From", overflow="fold")
    for key in settings.SETTINGS:
        origin = "command line" if key in app.overrides else origins[key]
        table.add_row(key, settings.shown(key, values[key]), origin)
    app.out.print(table)


@config_app.command("get")
@reported
def get_value(ctx: typer.Context, key: Key) -> None:
    """Print one setting's value."""
    app = get(ctx)
    settings.setting(key)
    app.out.print(settings.shown(key, app.config.__dict__[key]), highlight=False)


@config_app.command("set")
@reported
def set_value(
    ctx: typer.Context,
    key: Key,
    value: Annotated[str, typer.Argument(help="The new value.", show_default=False)],
) -> None:
    """Save a setting to the configuration file."""
    app = get(ctx)
    settings.save_setting(app.paths, key, value)
    app.out.print(f"Saved {key}.")
    variable = settings.SETTINGS[key].variable
    if variable and app.environ.get(variable):
        app.err.print(
            f"${variable} is set, so it still takes precedence.", style="yellow"
        )


@config_app.command("unset")
@reported
def unset_value(ctx: typer.Context, key: Key) -> None:
    """Remove a setting from the configuration file, so its default applies."""
    app = get(ctx)
    settings.save_setting(app.paths, key, None)
    app.out.print(f"Removed {key}.")


@config_app.command("path")
@reported
def show_path(ctx: typer.Context) -> None:
    """Print where the configuration file is."""
    app = get(ctx)
    app.out.print(str(app.paths.config_file), highlight=False, soft_wrap=True)
