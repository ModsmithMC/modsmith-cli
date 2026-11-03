"""Work out which Minecraft and mod loader an installed version starts."""

from dataclasses import dataclass
from typing import Any, cast

from modsmith.errors import UnsupportedError
from modsmith.minecraft import GameDir, Version

from .errors import AppError

# Each loader puts itself on the class path under one of these names.
LIBRARIES = {
    "net.fabricmc:fabric-loader": "fabric",
    "org.quiltmc:quilt-loader": "quilt",
    "net.neoforged:neoforge": "neoforge",
    "net.neoforged:forge": "neoforge",
    "net.neoforged.fancymodloader:loader": "neoforge",
    "net.minecraftforge:forge": "forge",
    "net.minecraftforge:fmlloader": "forge",
}
# Forge and NeoForge name their own version in the game's arguments.
ARGUMENTS = {"--fml.forgeVersion": "forge", "--fml.neoForgeVersion": "neoforge"}
# Inheritance deeper than this means the version files loop.
MAX_DEPTH = 8


@dataclass(frozen=True)
class GameVersions:
    """The Minecraft and mod loader versions an installed version starts.

    Attributes:
        minecraft: The Minecraft version.
        loader: The loader's name, or None for vanilla.
        loader_version: The loader's version, or None.
    """

    minecraft: str
    loader: str | None = None
    loader_version: str | None = None


def _arguments(raw: dict[str, Any]) -> list[str]:
    arguments: dict[str, Any] = raw.get("arguments") or {}
    game: list[Any] = arguments.get("game") or []
    words = [item for item in game if isinstance(item, str)]
    legacy = raw.get("minecraftArguments")
    if isinstance(legacy, str):
        words.extend(legacy.split())
    return words


def _from_arguments(raw: dict[str, Any]) -> tuple[str, str] | None:
    words = _arguments(raw)
    for index, word in enumerate(words[:-1]):
        if word in ARGUMENTS:
            return ARGUMENTS[word], words[index + 1]
    return None


def _from_libraries(raw: dict[str, Any]) -> tuple[str, str] | None:
    libraries: list[Any] = raw.get("libraries") or []
    for library in libraries:
        entry = cast(dict[str, Any], library) if isinstance(library, dict) else {}
        name = entry.get("name")
        if not isinstance(name, str):
            continue
        group, _, rest = name.partition(":")
        artifact, _, version = rest.partition(":")
        kind = LIBRARIES.get(f"{group}:{artifact}")
        if kind and version:
            return kind, version.split(":")[0]
    return None


def _chain(game: GameDir, version_id: str) -> list[Version]:
    """Read a version and the versions it inherits from, child first."""
    chain: list[Version] = []
    current: str | None = version_id
    while current is not None and len(chain) < MAX_DEPTH:
        try:
            version = game.version(current)
        except (UnsupportedError, OSError, ValueError, KeyError) as e:
            raise AppError(
                f"Version {current} is not installed in {game.path}.",
                hint="Start it once in the official launcher, then try again.",
            ) from e
        chain.append(version)
        current = version.inherits_from
    return chain


def detect(game: GameDir, version_id: str) -> GameVersions:
    """Read an installed version's files to find what it starts.

    Raises:
        AppError: The version, or one it inherits from, is not installed.
    """
    chain = _chain(game, version_id)
    minecraft = chain[-1].id
    for version in chain:
        found = _from_arguments(version.raw) or _from_libraries(version.raw)
        if found:
            kind, loader_version = found
            return GameVersions(
                minecraft, kind, loader_version.removeprefix(f"{minecraft}-")
            )
    return GameVersions(minecraft)
