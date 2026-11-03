"""The app's settings: defaults, then ``config.toml``, then environment variables.

Command-line options override all three, in the front end.
"""

import os
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

import tomli_w
from modsmith.minecraft import GameDir

from .errors import AppError
from .paths import AppPaths

PLATFORMS = ("modrinth", "curseforge")
TRUE = {"true", "yes", "on", "1"}
FALSE = {"false", "no", "off", "0"}


@dataclass(frozen=True)
class Config:
    """The settings in effect.

    Attributes:
        instances_dir: Where new instances are created.
        game_dir: The official launcher's game directory.
        curseforge_api_key: The key for the CurseForge API, or None.
        default_platform: Where to look when a project names no platform.
        allow_prereleases: Whether alpha and beta releases may be chosen.
    """

    instances_dir: Path
    game_dir: Path
    curseforge_api_key: str | None = None
    default_platform: str = "modrinth"
    allow_prereleases: bool = False


@dataclass(frozen=True)
class Setting:
    """How one setting is described, read and checked.

    Attributes:
        key: Its name in ``config.toml``.
        description: What it does.
        parse: Turns text into the setting's value, or raises `AppError`.
        variable: The environment variable that overrides it, or None.
        secret: Whether to hide its value when it is shown.
    """

    key: str
    description: str
    parse: Callable[[str], Any]
    variable: str | None = None
    secret: bool = False


def _path(text: str) -> Path:
    if not text.strip():
        raise AppError("A path cannot be empty.")
    return Path(text).expanduser()


def _boolean(text: str) -> bool:
    value = text.strip().lower()
    if value in TRUE:
        return True
    if value in FALSE:
        return False
    raise AppError(f"{text!r} is not true or false.")


def _platform(text: str) -> str:
    value = text.strip().lower()
    if value not in PLATFORMS:
        raise AppError(
            f"{text!r} is not a platform.", hint="Use modrinth or curseforge."
        )
    return value


def _secret(text: str) -> str:
    if not text.strip():
        raise AppError("The key cannot be empty.")
    return text.strip()


SETTINGS = {
    item.key: item
    for item in [
        Setting(
            "instances_dir",
            "Where new instances are created",
            _path,
            "MODSMITH_INSTANCES_DIR",
        ),
        Setting(
            "game_dir",
            "The official launcher's game directory",
            _path,
            "MODSMITH_GAME_DIR",
        ),
        Setting(
            "curseforge_api_key",
            "Your CurseForge API key",
            _secret,
            "CURSEFORGE_API_KEY",
            secret=True,
        ),
        Setting(
            "default_platform",
            "Where to look when a project names no platform",
            _platform,
        ),
        Setting(
            "allow_prereleases",
            "Whether alpha and beta releases may be chosen",
            _boolean,
        ),
    ]
}
assert set(SETTINGS) == {item.name for item in fields(Config)}


def setting(key: str) -> Setting:
    """Return a setting by name.

    Raises:
        AppError: There is no such setting.
    """
    try:
        return SETTINGS[key]
    except KeyError:
        known = ", ".join(SETTINGS)
        raise AppError(
            f"There is no setting called {key!r}.", hint=f"Settings: {known}."
        ) from None


def read_file(paths: AppPaths) -> dict[str, Any]:
    """Return the settings saved in ``config.toml``, as written.

    Raises:
        AppError: The file is not valid TOML.
    """
    try:
        with paths.config_file.open("rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        return {}
    except tomllib.TOMLDecodeError as e:
        raise AppError(
            f"{paths.config_file} is not valid TOML: {e}",
            hint="Fix or delete the file.",
        ) from e


def load_config(paths: AppPaths, environ: Mapping[str, str] = os.environ) -> Config:
    """Work out the settings in effect.

    Args:
        paths: The app's folders.
        environ: The environment variables.

    Returns:
        The settings.

    Raises:
        AppError: A saved or environment value is invalid.
    """
    values: dict[str, Any] = {
        "instances_dir": paths.default_instances_dir,
        "game_dir": GameDir.default().path,
    }
    for key, raw in read_file(paths).items():
        if key in SETTINGS:
            values[key] = _checked(
                key,
                str(raw).lower() if isinstance(raw, bool) else str(raw),
                f"{paths.config_file}",
            )
    for key, item in SETTINGS.items():
        raw = environ.get(item.variable) if item.variable else None
        if raw:
            values[key] = _checked(key, raw, f"${item.variable}")
    return Config(**values)


def _checked(key: str, raw: str, source: str) -> Any:
    """Parse a value, saying where a bad one came from."""
    try:
        return SETTINGS[key].parse(raw)
    except AppError as e:
        raise AppError(f"{key} in {source}: {e.message}", hint=e.hint) from e


def sources(paths: AppPaths, environ: Mapping[str, str] = os.environ) -> dict[str, str]:
    """Return where each setting's value comes from.

    Each is ``default``, ``config file`` or ``$VARIABLE``.
    """
    saved = read_file(paths)
    found: dict[str, str] = {}
    for key, item in SETTINGS.items():
        if item.variable and environ.get(item.variable):
            found[key] = f"${item.variable}"
        elif key in saved:
            found[key] = "config file"
        else:
            found[key] = "default"
    return found


def save_setting(paths: AppPaths, key: str, raw: str | None) -> None:
    """Save a setting to ``config.toml``, or remove it when ``raw`` is None.

    Raises:
        AppError: The setting does not exist or the value is invalid.
    """
    item = setting(key)
    saved = read_file(paths)
    if raw is None:
        saved.pop(key, None)
    else:
        value = item.parse(raw)
        saved[key] = str(value) if isinstance(value, Path) else value
    paths.config_file.parent.mkdir(parents=True, exist_ok=True)
    paths.config_file.write_text(tomli_w.dumps(saved), encoding="utf-8")


def shown(key: str, value: Any) -> str:
    """Format a setting's value for display, hiding secrets."""
    if value is None:
        return "not set"
    if SETTINGS[key].secret:
        return "set (hidden)"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
