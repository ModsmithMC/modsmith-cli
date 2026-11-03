"""``modsmith search``: find projects on Modrinth and CurseForge."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

import typer
from modsmith.errors import ModsmithError
from modsmith.platforms import ProjectType, SearchResults, SearchSort
from rich.table import Table
from rich.text import Text

from ..context import AppContext, get
from ..core.config import PLATFORMS
from ..core.errors import AppError
from ..core.platforms import explained, platform_title
from ..errors import report


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
    sort: SearchSort
    limit: int


# Narrower than this, the summary is left out.
MIN_SUMMARY = 12


class Order(StrEnum):
    """How to order search results."""

    RELEVANCE = "relevance"
    DOWNLOADS = "downloads"
    POPULARITY = "popularity"
    NEWEST = "newest"
    UPDATED = "updated"


ORDERS: dict[Order, SearchSort] = {
    Order.RELEVANCE: "relevance",
    Order.DOWNLOADS: "downloads",
    Order.POPULARITY: "popularity",
    Order.NEWEST: "newest",
    Order.UPDATED: "updated",
}


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


def _table(results: SearchResults, title: str | None, width: int) -> Table | None:
    """Lay out results so the name to copy fits, and the summary takes the rest.

    Returns None if the terminal is too narrow for the columns that must fit.
    """
    rows = [
        (
            project.name,
            f"{project.platform}:{project.slug}",
            _count(project.downloads),
            _one_line(project.summary),
        )
        for project in results.projects
    ]
    headers = ("Name", "Use as", "Downloads")
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    # Rich squeezes every column to fit a long line, so the summary gets a cap.
    room = width - sum(widths) - 2 * len(widths)
    if room < 0:
        return None
    table = Table(title=title, title_justify="left", box=None, pad_edge=False)
    table.add_column("Name", no_wrap=True)
    table.add_column("Use as", no_wrap=True)
    table.add_column("Downloads", justify="right", no_wrap=True)
    if room >= MIN_SUMMARY:
        table.add_column("Summary", no_wrap=True, overflow="ellipsis", max_width=room)
    for row in rows:
        table.add_row(*row[: len(table.columns)])
    return table


def _one_line(text: str) -> str:
    """Join a text's lines, because some summaries hold line breaks."""
    return " ".join(text.split())


def _lines(results: SearchResults, title: str | None) -> Text:
    """List results one per pair of lines, for narrow terminals."""
    text = Text()
    if title:
        text.append(f"{title}\n", style="italic")
    for project in results.projects:
        text.append(project.name, style="bold")
        text.append(f"  {_count(project.downloads)} downloads\n", style="dim")
        text.append(f"  {project.platform}:{project.slug}\n")
    text.rstrip()
    return text


def _search_one(app: AppContext, name: str, query: Query, title: str | None) -> None:
    with explained(name), app.platform(name) as platform:
        results = platform.search(
            query.text,
            project_type=query.kind,
            game_version=query.minecraft,
            loader=query.loader,
            sort=query.sort,
            limit=query.limit,
        )
    if results.projects:
        table = _table(results, title, app.out.width)
        if table is None:
            app.out.print(_lines(results, title), soft_wrap=True)
        else:
            app.out.print(table)
        shown = len(results.projects)
        if results.total > shown:
            app.err.print(f"Showing {shown} of {results.total}.", style="dim")
    else:
        app.out.print(Text(f"Nothing found on {platform_title(name)}.", style="dim"))


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
    sort: Annotated[
        Order, typer.Option("--sort", "-s", help="How to order the results.")
    ] = Order.RELEVANCE,
    limit: Annotated[int, typer.Option("--limit", "-n", min=1, max=100)] = 10,
) -> None:
    """Search for mods, modpacks, resource packs or shaders."""
    app = get(ctx)
    search = Query(query, KINDS[kind], minecraft, loader, ORDERS[sort], limit)
    names = (
        list(PLATFORMS)
        if where == Where.ALL
        else [(where or app.config.default_platform)]
    )
    failed = 0
    for name in names:
        heading = platform_title(name) if len(names) > 1 else None
        try:
            _search_one(app, str(name), search, heading)
        except (AppError, ModsmithError) as e:
            if len(names) == 1:
                raise
            failed += 1
            report(e, app.err, prefix=f"Skipped {name}: ")
    if failed == len(names):
        raise typer.Exit(1)
