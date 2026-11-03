"""Commands that look a project or a loader up, without changing anything."""

from itertools import islice
from typing import Annotated

import typer
from modsmith import loaders
from modsmith.errors import UnsupportedError
from rich.table import Table
from rich.text import Text

from ..core.errors import AppError
from ..core.platforms import explained
from ..core.refs import parse_project
from .context import get
from .install_cmd import LOADER_HINT, LOADER_NAMES
from .search_cmd import KINDS, Kind
from .ui import show_changelog

RELEASES_SHOWN = 5
LOADERS_SHOWN = 15
CHANGELOG_LINES = 12


def _count(number: int) -> str:
    return f"{number:,}"


def info_command(
    ctx: typer.Context,
    project: Annotated[
        str,
        typer.Argument(
            help="A name, platform:name, or the project's address.",
            show_default=False,
        ),
    ],
    kind: Annotated[
        Kind, typer.Option("--type", "-t", help="The kind of project.")
    ] = Kind.MOD,
    minecraft: Annotated[
        str | None,
        typer.Option("--minecraft", "-m", help="Only releases for this version."),
    ] = None,
    loader: Annotated[
        str | None,
        typer.Option("--loader", "-l", help="Only releases for this loader."),
    ] = None,
) -> None:
    """Show a project's details, its newest releases and what changed last."""
    app = get(ctx)
    ref = parse_project(project, app.config.default_platform)
    with explained(ref.platform, [ref.name]), app.platform(ref.platform) as platform:
        found = platform.get_project(ref.name, project_type=KINDS[kind])
        authors = platform.authors(found)
        releases = list(
            islice(
                platform.iter_releases(found, game_version=minecraft, loader=loader),
                RELEASES_SHOWN,
            )
        )
        try:
            changelog = platform.changelog(releases[0]) if releases else ""
        except UnsupportedError:
            changelog = ""

    app.out.print(
        Text(found.name, style="bold"), Text(f"({ref.platform}:{found.slug})")
    )
    if found.summary:
        app.out.print(found.summary)
    facts = [
        ("By", ", ".join(authors)),
        ("Downloads", _count(found.downloads)),
        ("Categories", ", ".join(found.categories)),
        ("Minecraft", ", ".join(found.game_versions[:8])),
        ("Updated", found.updated[:10]),
        ("Page", found.url),
    ]
    table = Table.grid(padding=(0, 2))
    for label, value in facts:
        if value:
            table.add_row(Text(label, style="dim"), value)
    app.out.print(table)

    app.out.print()
    if not releases:
        app.out.print("No releases match.")
        return
    listed = Table(box=None, pad_edge=False, title_justify="left")
    for column in ("Release", "Type", "Minecraft", "Loaders", "Published"):
        listed.add_column(column, no_wrap=column != "Minecraft")
    for release in releases:
        listed.add_row(
            release.version or release.name,
            release.release_type,
            ", ".join(release.game_versions[:4]),
            ", ".join(release.loaders),
            release.published[:10],
        )
    app.out.print(listed)
    if changelog:
        app.out.print()
        show_changelog(
            app,
            f"What changed in {releases[0].name}",
            changelog,
            lines=CHANGELOG_LINES,
        )


def loaders_command(
    ctx: typer.Context,
    kind: Annotated[
        str,
        typer.Argument(help="fabric, quilt, forge or neoforge.", show_default=False),
    ],
    minecraft: Annotated[
        str, typer.Argument(help="The Minecraft version.", show_default=False)
    ],
    everything: Annotated[
        bool, typer.Option("--all", help="List every version, not only the newest.")
    ] = False,
) -> None:
    """List a mod loader's versions for a Minecraft version."""
    app = get(ctx)
    try:
        found = loaders.versions(kind.lower(), minecraft)
    except UnsupportedError as e:
        raise AppError(f"Modsmith cannot install {kind!r}.", hint=LOADER_HINT) from e
    name = LOADER_NAMES.get(kind.lower(), kind)
    if not found:
        app.out.print(f"{name} has no versions for Minecraft {minecraft}.")
        return
    shown = found if everything else found[:LOADERS_SHOWN]
    table = Table(box=None, pad_edge=False)
    table.add_column("Version", no_wrap=True)
    table.add_column("")
    for item in shown:
        notes = ["recommended"] if item.recommended else []
        if not item.stable:
            notes.append("beta")
        table.add_row(item.version, ", ".join(notes))
    app.out.print(Text(f"{name} for Minecraft {minecraft}", style="bold"))
    app.out.print(table)
    if len(shown) < len(found):
        app.out.print(
            Text(
                f"{len(found) - len(shown)} older versions; see them with --all.",
                style="dim",
            )
        )
