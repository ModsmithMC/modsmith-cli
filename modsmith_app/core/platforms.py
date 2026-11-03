"""Open the platforms that projects come from."""

from collections.abc import Callable, Collection, Generator
from contextlib import contextmanager

from modsmith.errors import NetworkError, PlatformError
from modsmith.platforms import CurseForge, Modrinth, Platform

from .. import __version__
from .config import Config
from .errors import AppError

USER_AGENT = f"modsmith-cli/{__version__} (+https://github.com/ModsmithMC/modsmith)"
CURSEFORGE_CONSOLE = "https://console.curseforge.com"
# CurseForge answers these when the key is wrong.
REJECTED = (401, 403)
NOT_FOUND = 404
TITLES = {"modrinth": "Modrinth", "curseforge": "CurseForge"}

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


def platform_title(name: str) -> str:
    """Return a platform's name as people write it, such as ``CurseForge``."""
    return TITLES.get(name, name)


@contextmanager
def explained(name: str, wanted: Collection[str] = ()) -> Generator[None]:
    """Turn a platform's refusal into an `AppError` that says what to fix.

    Args:
        name: The platform in use.
        wanted: The projects asked for, to name the one the platform lacks.

    Raises:
        AppError: CurseForge rejected the API key, or the platform has no
            project by one of the wanted names.
    """
    try:
        yield
    except NetworkError as e:
        if name == "curseforge" and e.status in REJECTED:
            raise AppError(
                "CurseForge rejected the API key.",
                hint=(
                    "Set it again: modsmith config set curseforge_api_key '<key>'. "
                    "In PowerShell, use single quotes, because $ starts a "
                    "variable inside double quotes."
                ),
            ) from e
        if e.status == NOT_FOUND and wanted:
            raise _unknown(name, wanted, str(e)) from e
        raise
    except PlatformError as e:
        # CurseForge finds slugs by searching, and says so when none matches.
        if any(item in str(e) for item in wanted):
            raise _unknown(name, wanted, str(e)) from e
        raise


def _unknown(name: str, wanted: Collection[str], message: str) -> AppError:
    """Say which of the wanted projects a platform does not have."""
    unknown = [item for item in wanted if item in message] or list(wanted)
    names = " or ".join(repr(item) for item in unknown)
    return AppError(
        f"{platform_title(name)} has no project called {names}.",
        hint=f"Look for it with: modsmith search {unknown[0]} --platform {name}",
    )
