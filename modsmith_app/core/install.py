"""Getting a pack ready to install, and adding it to the official launcher."""

import dataclasses
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from modsmith.errors import LauncherError, ModsmithError
from modsmith.launcher import Launcher, icon_data_uri
from modsmith.minecraft import GameDir
from modsmith.net import Session
from modsmith.packs import Modpack, PackEntry, load
from modsmith.platforms import Platform, Project, Release
from modsmith.progress import CancelToken, ProgressCallback

from .errors import AppError
from .names import name_from
from .records import PackSource
from .refs import LocalPack, ProjectRef

PROFILE_PREFIX = "modsmith-"
# The launcher shows PNG and JPEG icons; other formats are left out.
ICON_TYPES = ("image/png", "image/jpeg")


@dataclass(frozen=True)
class FetchedPack:
    """A pack read and ready to install.

    Attributes:
        pack: The pack, with downloads looked up where its format needs it.
        source: Where it came from.
        project: Its project on a platform, or None for a local file.
    """

    pack: Modpack
    source: PackSource
    project: Project | None = None


def _resolved(pack: Modpack, open_platform: Callable[[str], Platform]) -> Modpack:
    """Look up downloads for a CurseForge pack, whose files are named by id."""
    if pack.format != "curseforge":
        return pack
    with open_platform("curseforge") as platform:
        return platform.resolve(pack)


def latest_pack(
    platform: Platform, name: str, *, allow_prereleases: bool
) -> tuple[Project, Release]:
    """Find a modpack project and its newest release.

    Raises:
        AppError: The project is not a modpack, or has no release.
        NetworkError: The platform could not be reached.
    """
    project = platform.get_project(name, project_type="modpack")
    if project.project_type != "modpack":
        raise AppError(
            f"{project.name} is a {project.project_type}, not a modpack.",
            hint=f"Add it to an instance with: modsmith add <instance> "
            f"{platform.name}:{name}",
        )
    release = platform.latest_release(project, release_only=not allow_prereleases)
    if release is None:
        raise AppError(
            f"{project.name} has no release to install.",
            hint="Alpha and beta releases count if you run: "
            "modsmith config set allow_prereleases true",
        )
    return project, release


def download_pack(
    platform: Platform,
    project: Project,
    release: Release,
    open_platform: Callable[[str], Platform],
    *,
    cache_dir: Path,
    progress: ProgressCallback | None = None,
    cancel: CancelToken | None = None,
) -> FetchedPack:
    """Download a pack release into the cache and read it.

    Raises:
        PackError: The file is not a valid pack.
        NetworkError: A platform could not be reached.
    """
    folder = cache_dir / "packs" / platform.name
    path = platform.fetch(release, folder, progress=progress, cancel=cancel)
    pack = _resolved(load(path), open_platform)
    return FetchedPack(pack, PackSource(platform.name, project.id, release.id), project)


def fetch_pack(
    ref: ProjectRef | LocalPack,
    open_platform: Callable[[str], Platform],
    *,
    cache_dir: Path,
    allow_prereleases: bool,
    progress: ProgressCallback | None = None,
    cancel: CancelToken | None = None,
) -> FetchedPack:
    """Read a local pack, or download a platform pack's newest release.

    Args:
        ref: The pack.
        open_platform: Opens a platform by name.
        cache_dir: Where downloaded packs are kept.
        allow_prereleases: Whether an alpha or beta release may be chosen.
        progress: Receives download updates.
        cancel: Stops the download.

    Returns:
        The pack.

    Raises:
        AppError: The project is not a modpack, or has no release.
        PackError: The file is not a valid pack.
        NetworkError: A platform could not be reached.
    """
    if isinstance(ref, LocalPack):
        pack = load(ref.path)
        source = PackSource(file=str(ref.path.resolve()))
        return FetchedPack(_resolved(pack, open_platform), source)
    with open_platform(ref.platform) as platform:
        project, release = latest_pack(
            platform, ref.name, allow_prereleases=allow_prereleases
        )
        return download_pack(
            platform,
            project,
            release,
            open_platform,
            cache_dir=cache_dir,
            progress=progress,
            cancel=cancel,
        )


def optional_entries(pack: Modpack) -> list[PackEntry]:
    """Return the files a pack lets the player choose to install."""
    return [
        entry
        for entry in pack.entries
        if entry.path and entry.support("client") == "optional"
    ]


def match_optional(pack: Modpack, patterns: Iterable[str]) -> list[str]:
    """Find the optional files whose paths contain each pattern.

    Raises:
        AppError: A pattern matches no optional file.
    """
    options = [entry.path for entry in optional_entries(pack) if entry.path]
    chosen: list[str] = []
    for pattern in patterns:
        hits = [path for path in options if pattern.lower() in path.lower()]
        if not hits:
            listed = ", ".join(options) or "none"
            raise AppError(
                f"No optional file matches {pattern!r}.",
                hint=f"The optional files are: {listed}.",
            )
        chosen.extend(hits)
    return list(dict.fromkeys(chosen))


def with_optional(pack: Modpack, chosen: Iterable[str]) -> Modpack:
    """Return the pack with the chosen optional files made part of the install."""
    wanted = set(chosen)
    entries = tuple(
        dataclasses.replace(entry, client="required")
        if entry.path in wanted and entry.support("client") == "optional"
        else entry
        for entry in pack.entries
    )
    return pack.with_entries(entries)


def download_sizes(pack: Modpack) -> dict[str, int | None]:
    """Return each file's download size, for a plan's summary."""
    return {entry.path: entry.size for entry in pack.entries if entry.path}


def check_launcher(game: GameDir, running: bool) -> Launcher:
    """Make sure the official launcher's profiles can be changed now.

    Raises:
        AppError: The launcher is open, or has never run with this game
            directory.
    """
    if running:
        raise AppError(
            "Close the official launcher first.",
            hint="It saves its own list of installations when it closes, "
            "which would undo this change.",
        )
    launcher = Launcher(game)
    try:
        launcher.profiles()
    except LauncherError as e:
        raise AppError(
            f"The official launcher has not been set up in {game.path}.",
            hint="Start the official launcher once and close it, then try again. "
            "If you use another game directory, set it with: "
            "modsmith config set game_dir <folder>",
        ) from e
    return launcher


def profile_key(name: str) -> str:
    """Return the launcher profile key for an instance."""
    return PROFILE_PREFIX + name_from(name)


def project_icon(project: Project | None) -> str | None:
    """Download a project's icon as a data URI, or return None if there is none."""
    if project is None or not project.icon_url:
        return None
    try:
        with Session() as session:
            response = session.request("GET", project.icon_url)
    except ModsmithError:
        return None
    kind = response.headers.get("Content-Type", "").split(";")[0].strip()
    if kind not in ICON_TYPES:
        return None
    return icon_data_uri(response.content, kind)
