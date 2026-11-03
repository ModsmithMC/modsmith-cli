"""Find the player's instances by name or by path.

An instance is a folder under the instances folder, named after the instance,
or a folder elsewhere that the app was told about.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from modsmith.errors import InstanceError
from modsmith.instances import Instance, InstanceState

from .config import Config
from .errors import AppError
from .paths import AppPaths


@dataclass(frozen=True)
class Entry:
    """One instance the app knows.

    Attributes:
        name: Its folder's name.
        path: Its folder.
        state: What it holds, or None if that could not be read.
        external: Whether it is outside the instances folder.
        problem: Why its state could not be read, or None.
    """

    name: str
    path: Path
    state: InstanceState | None
    external: bool = False
    problem: str | None = None


def _looks_like_path(text: str) -> bool:
    return any(mark in text for mark in ("/", "\\")) or text.startswith((".", "~"))


def locate(text: str, config: Config) -> Path:
    """Return the folder that a name or a path refers to. It may not exist yet.

    A name is looked up in the instances folder. Anything with a slash, or
    starting with ``.`` or ``~``, is a path.
    """
    if _looks_like_path(text) or Path(text).is_absolute():
        return Path(text).expanduser().resolve()
    return config.instances_dir / text


def _state(instance: Instance) -> InstanceState | None:
    """Read an instance's state, reporting corruption as an `AppError`."""
    try:
        return instance.state
    except InstanceError as e:
        raise AppError(str(e)) from e


def open_instance(
    text: str, config: Config, paths: AppPaths | None = None
) -> tuple[Instance, InstanceState]:
    """Open an existing instance by name or path.

    A name is looked up in the instances folder, then among the instances kept
    elsewhere.

    Raises:
        AppError: There is no instance there, or its state is corrupt.
    """
    instance = Instance(locate(text, config))
    state = _state(instance)
    if state is None and paths is not None and not _looks_like_path(text):
        for path in external_paths(paths):
            if path.name == text:
                instance = Instance(path)
                state = _state(instance)
                break
    if state is None:
        raise AppError(
            f"There is no instance called {text!r}.",
            hint="Run modsmith list to see your instances.",
        )
    return instance, state


def resolve_instance(
    text: str | None, config: Config, paths: AppPaths
) -> tuple[Instance, InstanceState]:
    """Open the instance a command names, or the only one if it names none.

    Raises:
        AppError: There is no such instance, there are none, or there are
            several and none was named.
    """
    if text is not None:
        return open_instance(text, config, paths)
    usable = [
        entry for entry in list_instances(config, paths) if entry.state is not None
    ]
    if len(usable) == 1:
        return open_instance(str(usable[0].path), config, paths)
    if not usable:
        raise AppError(
            "There are no instances yet.",
            hint="Install a pack with modsmith install, or start one with modsmith create.",
        )
    names = ", ".join(entry.name for entry in usable)
    raise AppError("Name the instance to use.", hint=f"Your instances: {names}.")


def split_target(
    words: list[str], config: Config, paths: AppPaths
) -> tuple[Instance, InstanceState, list[str]]:
    """Separate an instance name from the items a command acts on.

    The first word names the instance if one has that name. Otherwise, when
    there is only one instance, every word is an item.

    Raises:
        AppError: No instance is named and there is not exactly one.
    """
    if words:
        try:
            instance, state = open_instance(words[0], config, paths)
        except AppError:
            pass
        else:
            return instance, state, words[1:]
    instance, state = resolve_instance(None, config, paths)
    return instance, state, words


def external_paths(paths: AppPaths) -> list[Path]:
    """Return the instances kept outside the instances folder."""
    try:
        data = json.loads(paths.external_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except ValueError as e:
        raise AppError(f"{paths.external_file} is corrupt: {e}") from e
    return [Path(item) for item in data if isinstance(item, str)]


def remember_external(paths: AppPaths, path: Path, keep: bool = True) -> None:
    """Add an instance outside the instances folder to the list, or remove it."""
    known = [item for item in external_paths(paths) if item != path]
    if keep:
        known.append(path)
    paths.external_file.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps([str(item) for item in known], indent=2)
    paths.external_file.write_text(text, encoding="utf-8")


def _entry(path: Path, external: bool) -> Entry | None:
    """Describe a folder, or return None if it is not an instance."""
    try:
        state = Instance(path).state
    except InstanceError as e:
        return Entry(path.name, path, None, external, str(e))
    if state is None:
        return None
    return Entry(path.name, path, state, external)


def list_instances(config: Config, paths: AppPaths) -> list[Entry]:
    """List every instance the app knows, sorted by name.

    Folders in the instances folder that are not instances are skipped, and so
    are remembered folders that are no longer instances.
    """
    found: list[Entry] = []
    if config.instances_dir.is_dir():
        for path in sorted(config.instances_dir.iterdir()):
            entry = _entry(path, external=False) if path.is_dir() else None
            if entry is not None:
                found.append(entry)
    for path in external_paths(paths):
        entry = _entry(path, external=True)
        if entry is not None:
            found.append(entry)
    return sorted(found, key=lambda item: item.name.lower())
