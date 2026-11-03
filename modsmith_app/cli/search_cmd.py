"""``modsmith search``: find projects on Modrinth and CurseForge."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

import typer
from modsmith.platforms import ProjectType, SearchResults
from rich.table import Table
from rich.text import Text

from ..core.config import PLATFORMS
from ..core.errors import AppError
from .context import AppContext, get


class Kind(StrEnum):
    """The kinds of projects to search for."""

    MOD = "mod"
    MODPACK = "modpack"
    RESOURCEPACK = "resourcepack"
    SHADER = "shader"


KINDS: dict[Kind, ProjectType] = {
    Kind.MOD: "mod",
    Kind.MODPACK: "modpack",
    Kind.RESOURCEPACK: "resourcepack",
    Kind.SHADER: "shader",
}


@dataclass(frozen=True)
class Query:
    """One search, as the player asked for it."""

    text: str
    kind: ProjectType
    minecraft: str | None
    loader: str | None
    limit: int


class Where(StrEnum):
    """The platforms to search."""

    MODRINTH = "modrinth"
    CURSEFORGE = "curseforge"
    ALL = "all"


def _count(value: int) -> str:
    """Shorten a download count, such as 1.2M."""
    for size, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if value >= size:
            return f"{value / size:.1f}".rstrip("0").rstrip(".") + suffix
    return str(value)


def _table(results: SearchResults, title: str | None) -> Table:
    table = Table(title=title, title_justify="left", box=None, pad_edge=False)
    table.add_column("Name", no_wrap=True)
    table.add_column("Use as", no_wrap=True)
    table.add_column("Downloads", justify="right")
    table.add_column("Summary", overflow="ellipsis", no_wrap=True, max_width=60)
    for project in results.projects:
        table.add_row(
            project.name,
            f"{project.platform}:{project.slug}",
            _count(project.downloads),
            project.summary,
        )
    return table


def _search_one(app: AppContext, name: str, query: Query, title: str | None) -> None:
    with app.platform(name) as platform:
        results = platform.search(
            query.text,
            project_type=query.kind,
            game_version=query.minecraft,
            loader=query.loader,
            limit=query.limit,
        )
    if results.projects:
        app.out.print(_table(results, title))
        shown = len(results.projects)
        if results.total > shown:
            app.err.print(f"Showing {shown} of {results.total}.", style="dim")
    else:
        app.out.print(Text(f"Nothing found on {name}.", style="dim"))


def search_command(
    ctx: typer.Context,
    query: Annotated[str, typer.Argument(help="What to look for.", show_default=False)],
    kind: Annotated[
        Kind, typer.Option("--type", "-t", help="The kind of project.")
    ] = Kind.MOD,
    where: Annotated[
        Where | None,
        typer.Option(
            "--platform", "-p", help="Where to search. Defaults to the setting."
        ),
    ] = None,
    minecraft: Annotated[
        str | None, typer.Option("--minecraft", "-m", help="Only this game version.")
    ] = None,
    loader: Annotated[
        str | None, typer.Option("--loader", "-l", help="Only this mod loader.")
    ] = None,
    limit: Annotated[int, typer.Option("--limit", "-n", min=1, max=50)] = 10,
) -> None:
    """Search for mods, modpacks, resource packs or shaders."""
    app = get(ctx)
    search = Query(query, KINDS[kind], minecraft, loader, limit)
    names = (
        list(PLATFORMS)
        if where == Where.ALL
        else [(where or app.config.default_platform)]
    )
    for name in names:
        title = name.capitalize() if len(names) > 1 else None
        try:
            _search_one(app, str(name), search, title)
        except AppError as e:
            if len(names) == 1:
                raise
            app.err.print(Text(f"Skipped {name}: {e.message}", style="yellow"))
