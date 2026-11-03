"""A real `Platform` subclass that serves a catalogue from memory."""

from collections.abc import Iterator
from typing import ClassVar

from modsmith.errors import PlatformError
from modsmith.platforms import Platform, Project, Release, SearchResults


def project(slug: str, kind: str = "mod", downloads: int = 0, **fields) -> Project:
    """Build a project whose id is its slug."""
    return Project(
        platform=fields.pop("platform", "modrinth"),
        id=slug,
        slug=slug,
        name=fields.pop("name", slug.title()),
        summary=fields.pop("summary", f"About {slug}"),
        project_type=kind,
        downloads=downloads,
        **fields,
    )


class Catalog(Platform):
    """A platform that serves the projects and releases it is given."""

    name: ClassVar[str] = "modrinth"

    def __init__(
        self, *projects: Project, releases: tuple[Release, ...] = (), name: str = ""
    ) -> None:
        super().__init__()
        self.projects = list(projects)
        self.releases = list(releases)
        if name:
            self.name = name

    def search(
        self,
        query,
        *,
        project_type="modpack",
        game_version=None,
        loader=None,
        offset=0,
        limit=20,
    ) -> SearchResults:
        found = [
            item
            for item in self.projects
            if item.project_type == project_type
            and query.lower() in (item.name + item.slug).lower()
        ]
        return SearchResults(tuple(found[offset : offset + limit]), len(found), offset)

    def get_project(self, ref, *, project_type="modpack") -> Project:
        for item in self.projects:
            if str(ref) in (item.id, item.slug):
                return item
        raise PlatformError(f"Unknown project {ref}")

    def iter_releases(
        self, project, *, game_version=None, loader=None, release_only=False
    ) -> Iterator[Release]:
        for item in self.releases:
            if (
                item.project_id == project.id
                and (game_version is None or game_version in item.game_versions)
                and (loader is None or loader in item.loaders)
                and (not release_only or item.release_type == "release")
            ):
                yield item
