"""Open the platforms that projects come from."""

from collections.abc import Callable

from modsmith.platforms import CurseForge, Modrinth, Platform

from .. import __version__
from .config import Config
from .errors import AppError

USER_AGENT = f"modsmith-app/{__version__} (+https://github.com/PaPa-jun/Modsmith-App)"
CURSEFORGE_CONSOLE = "https://console.curseforge.com"

# Opens a platform by name. Tests pass one that serves a catalogue from memory.
PlatformOpener = Callable[[str, Config], Platform]


def open_platform(name: str, config: Config) -> Platform:
    """Open a platform. Close it when done, or use it as a context manager.

    Args:
        name: ``modrinth`` or ``curseforge``.
        config: The settings, which hold the CurseForge key.

    Returns:
        The platform.

    Raises:
        AppError: CurseForge has no key, or the name is unknown.
    """
    if name == "modrinth":
        return Modrinth(USER_AGENT)
    if name == "curseforge":
        if not config.curseforge_api_key:
            raise AppError(
                "CurseForge needs an API key.",
                hint=(
                    f"Get one at {CURSEFORGE_CONSOLE}, then run: "
                    "modsmith config set curseforge_api_key <key>"
                ),
            )
        return CurseForge(config.curseforge_api_key)
    raise AppError(f"{name!r} is not a platform.", hint="Use modrinth or curseforge.")
