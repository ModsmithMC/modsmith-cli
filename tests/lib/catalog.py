"""A real `Platform` subclass that serves a catalogue from memory."""

import hashlib
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import ClassVar

from modsmith.errors import NetworkError, PlatformError
from modsmith.platforms import (
    Dependency,
    Platform,
    Project,
    Release,
    ReleaseFile,
    SearchResults,
)


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


def release(
    project_id: str,
    version: str = "1",
    *dependencies: Dependency,
    game: str = "1.21.1",
    loader: str = "fabric",
    files: tuple[ReleaseFile, ...] = (),
    platform: str = "modrinth",
    release_type: str = "release",
) -> Release:
    """Build a release whose id is ``project-version``."""
    return Release(
        platform=platform,
        id=f"{project_id}-{version}",
        project_id=project_id,
        name=f"{project_id.title()} {version}",
        release_type=release_type,  # type: ignore[arg-type]
        game_versions=(game,),
        loaders=(loader,),
        files=files,
        dependencies=dependencies,
        version=version,
    )


class Catalog(Platform):
    """A platform that serves the projects and releases it is given.

    Args:
        *projects: The projects.
        releases: Their releases, newest first.
        name: The platform's name.
        refuse: Makes every search fail with this HTTP status.
        changelogs: Changelogs by release id.
    """

    name: ClassVar[str] = "modrinth"

    def __init__(
        self,
        *projects: Project,
        releases: Iterable[Release] = (),
        name: str = "",
        refuse: int | None = None,
        changelogs: dict[str, str] | None = None,
    ) -> None:
        super().__init__()
        self.projects = list(projects)
        self.releases = list(releases)
        self.refuse = refuse
        self.changelogs = dict(changelogs or {})
        if name:
            self.name = name

    def copy(self) -> "Catalog":
        """Return a fresh platform with the same catalogue."""
        return Catalog(
            *self.projects,
            releases=self.releases,
            name=self.name,
            refuse=self.refuse,
            changelogs=self.changelogs,
        )

    def publish(self, item: Release) -> None:
        """Add a release, newer than the others of its project."""
        self.releases.insert(0, item)

    def search(
        self,
        query,
        *,
        project_type="modpack",
        game_version=None,
        loader=None,
        sort="relevance",
        offset=0,
        limit=20,
    ) -> SearchResults:
        if self.refuse is not None:
            raise NetworkError(
                f"GET https://{self.name}.invalid/search returned {self.refuse}",
                self.refuse,
            )
        found = [
            item
            for item in self.projects
            if item.project_type == project_type
            and query.lower() in (item.name + item.slug).lower()
        ]
        if sort == "downloads":
            found.sort(key=lambda item: item.downloads, reverse=True)
        elif sort == "popularity":
            found.sort(key=lambda item: item.follows or 0, reverse=True)
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

    def get_release(self, release_id: str) -> Release:
        for item in self.releases:
            if item.id == release_id:
                return item
        raise PlatformError(f"Unknown release {release_id}")

    def changelog(self, release: Release) -> str:
        return self.changelogs.get(release.id, "")

    def identify(
        self, paths: Iterable[Path | str], *, progress=None, cancel=None
    ) -> dict[Path, Release]:
        found: dict[Path, Release] = {}
        for path in map(Path, paths):
            digest = hashlib.sha1(path.read_bytes()).hexdigest()
            for item in self.releases:
                if any(file.hashes.get("sha1") == digest for file in item.files):
                    found[path] = item
                    break
        return found
