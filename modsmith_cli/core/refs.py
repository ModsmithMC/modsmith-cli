"""Read how a player names a project or a pack.

``sodium`` uses the default platform, ``curseforge:238222`` or ``modrinth:iris``
names one, a project page's address works too, and a path to a ``.mrpack`` or
``.zip`` file means a local pack.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from .config import PLATFORMS
from .errors import AppError

PACK_SUFFIXES = (".mrpack", ".zip")
ADDRESSES = [
    ("modrinth", re.compile(r"^https?://(?:www\.)?modrinth\.com/[a-z]+/([^/?#]+)")),
    (
        "curseforge",
        re.compile(r"^https?://(?:www\.)?curseforge\.com/minecraft/[a-z-]+/([^/?#]+)"),
    ),
]


@dataclass(frozen=True)
class ProjectRef:
    """A project on a platform.

    Attributes:
        platform: The platform's name.
        name: The project's id or slug.
    """

    platform: str
    name: str

    def __str__(self) -> str:
        return f"{self.platform}:{self.name}"


@dataclass(frozen=True)
class LocalPack:
    """A pack file on this computer.

    Attributes:
        path: The file.
    """

    path: Path


def parse_project(text: str, default_platform: str) -> ProjectRef:
    """Read a project name, a ``platform:name`` pair or a project's address.

    Args:
        text: What the player typed.
        default_platform: The platform for a bare name.

    Returns:
        The project.

    Raises:
        AppError: The text is empty or names an unknown platform.
    """
    text = text.strip()
    for platform, pattern in ADDRESSES:
        match = pattern.match(text)
        if match:
            return ProjectRef(platform, match[1])
    platform, separator, name = text.partition(":")
    if not separator:
        platform, name = default_platform, text
    platform = platform.lower()
    if platform not in PLATFORMS:
        raise AppError(
            f"{platform!r} is not a platform.",
            hint="Write modrinth:<name> or curseforge:<name>.",
        )
    if not name:
        raise AppError("A project needs a name.")
    return ProjectRef(platform, name)


def parse_pack(text: str, default_platform: str) -> ProjectRef | LocalPack:
    """Read a pack: a local file, or a project as `parse_project` reads it.

    Raises:
        AppError: The text names a pack file that does not exist, or is not a
            project.
    """
    path = Path(text).expanduser()
    if path.suffix.lower() in PACK_SUFFIXES:
        if not path.is_file():
            raise AppError(f"{path} does not exist.")
        return LocalPack(path)
    return parse_project(text, default_platform)
