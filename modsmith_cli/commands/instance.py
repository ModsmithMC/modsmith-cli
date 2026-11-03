"""Commands that bring in, move and delete whole instances."""

import shutil
from pathlib import Path
from typing import Annotated

import typer
from modsmith import loaders
from modsmith.errors import UnsupportedError
from modsmith.instances import Instance
from modsmith.launcher import Launcher, Profile
from modsmith.loaders import Loader
from modsmith.minecraft import GameDir

from ..context import AppContext, get
from ..core.config import Config
from ..core.errors import AppError
from ..core.install import check_launcher
from ..core.names import check_name
from ..core.records import Record, read_record, write_record
from ..core.registry import (
    list_instances,
    locate,
    remember_external,
    resolve_instance,
)
from ..target import DryRun, InstanceName, Yes
from ..ui import confirm, confirm_name
from .contents import adopt_files
from .install import loader_label


def _profile(launcher: Launcher, text: str) -> Profile:
    """Find a launcher installation by its key or, ignoring case, its name."""
    profiles = launcher.profiles()
    if text in profiles:
        return profiles[text]
    named = [item for item in profiles.values() if item.name.lower() == text.lower()]
    if len(named) == 1:
        return named[0]
    listed = ", ".join(sorted(item.name or item.key for item in profiles.values()))
    if named:
        raise AppError(
            f"Several installations are called {text!r}.",
            hint="Use the key of one instead: " + ", ".join(item.key for item in named),
        )
    raise AppError(
        f"The official launcher has no installation called {text!r}.",
        hint=f"Its installations: {listed}." if listed else None,
    )


def _versions(game: GameDir, version_id: str) -> tuple[str, Loader | None]:
    """Return the Minecraft version and the loader an installed version starts.

    Raises:
        AppError: The version, or one it inherits from, is not installed.
    """
    try:
        loader = loaders.detect(game, version_id)
        version = game.version(version_id)
    except UnsupportedError as e:
        raise AppError(
            f"{e}.", hint="Start it once in the official launcher, then try again."
        ) from e
    if loader is not None:
        return loader.minecraft, loader
    return version.inherits_from or version.id, None


def _inside(path: Path, folder: Path) -> bool:
    return path.resolve().is_relative_to(folder.resolve())


def _check_free_name(app: AppContext, path: Path, moving: Path | None = None) -> None:
    """Refuse a folder name that another instance already has."""
    others = {path.resolve(), moving.resolve() if moving else path.resolve()}
    taken = [
        entry
        for entry in list_instances(app.config, app.paths)
        if entry.name == path.name and entry.path.resolve() not in others
    ]
    if taken:
        raise AppError(
            f"An instance called {path.name} already exists.",
            hint="Rename one of the two folders first.",
        )


def import_command(
    ctx: typer.Context,
    installation: Annotated[
        str,
        typer.Argument(
            help="The installation's name in the official launcher.",
            show_default=False,
        ),
    ],
    yes: Yes = False,
    dry_run: DryRun = False,
) -> None:
    """Manage an installation you made in the official launcher as an instance."""
    app = get(ctx)
    game = GameDir(app.config.game_dir)
    profile = _profile(check_launcher(game, running=False), installation)
    if not profile.game_dir:
        raise AppError(
            f"{profile.name} uses the game directory itself.",
            hint="Give it its own game directory in the official launcher first.",
        )
    if not profile.version_id or profile.version_id.startswith("latest-"):
        raise AppError(
            f"{profile.name} starts the newest Minecraft, not one version.",
            hint="Choose a version for it in the official launcher first.",
        )
    path = Path(profile.game_dir).resolve()
    instance = Instance(path)
    if instance.state is not None:
        raise AppError(f"{path} is already an instance.")
    _check_free_name(app, path)
    minecraft, loader = _versions(game, profile.version_id)
    kind, version = (loader.kind, loader.version) if loader else (None, None)
    app.out.print(
        f"Import {profile.name} as {path.name}: Minecraft {minecraft} "
        f"with {loader_label(kind, version)}, in {path}."
    )
    if dry_run:
        return
    confirm(app, "Import it?", yes=yes)
    path.mkdir(parents=True, exist_ok=True)
    Instance.create(
        path,
        minecraft=minecraft,
        loader=kind,
        loader_version=version,
    )
    write_record(path, Record(profile=profile.key))
    if not _inside(path, app.config.instances_dir):
        remember_external(app.paths, path)
    platforms = ["modrinth"] + (["curseforge"] if app.config.curseforge_api_key else [])
    adopt_files(app, instance, platforms)
    app.out.print(f"{path.name} is now an instance.")


def _destination(text: str, config: Config, current: Path) -> Path:
    """Return where an instance moves to: a new name, or a folder path.

    A new name keeps the instance in the folder it is in now, so an imported
    instance is renamed in place rather than moved into the instances folder.
    """
    path = locate(text, config)
    if path.parent == config.instances_dir:
        path = current.parent / check_name(path.name)
    if path.exists():
        raise AppError(
            f"{path} already exists.",
            hint="Name a folder that does not exist yet.",
        )
    return path


def move_command(
    ctx: typer.Context,
    name: Annotated[
        str, typer.Argument(help="The instance to move.", show_default=False)
    ],
    destination: Annotated[
        str,
        typer.Argument(help="A new name, or a folder path.", show_default=False),
    ],
) -> None:
    """Rename an instance or move its folder, and update its launcher installation."""
    app = get(ctx)
    instance, _ = resolve_instance(name, app.config, app.paths)
    old = instance.path.resolve()
    new = _destination(destination, app.config, old)
    _check_free_name(app, new, moving=old)
    record = read_record(old)
    game = GameDir(app.config.game_dir)
    launcher = (
        check_launcher(game, app.services.launcher_running())
        if record.profile
        else None
    )
    new.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(old, new)
    remember_external(app.paths, old, keep=False)
    if not _inside(new, app.config.instances_dir):
        remember_external(app.paths, new)
    if launcher is not None and record.profile:
        profile = launcher.profiles().get(record.profile)
        if profile and profile.version_id:
            launcher.add_profile(
                profile.name, profile.version_id, new, key=record.profile
            )
    where = new.name if new.parent == old.parent else str(new)
    app.out.print(f"Moved {old.name} to {where}.")


def _worlds(path: Path) -> int:
    saves = path / "saves"
    if not saves.is_dir():
        return 0
    return sum(1 for item in saves.iterdir() if (item / "level.dat").is_file())


def delete_command(
    ctx: typer.Context,
    name: InstanceName = None,
    yes: Yes = False,
    force: Annotated[
        bool, typer.Option("--force", help="Allow --yes for this command.")
    ] = False,
) -> None:
    """Delete an instance's folder, worlds included, and its launcher installation."""
    app = get(ctx)
    instance, _ = resolve_instance(name, app.config, app.paths)
    path = instance.path.resolve()
    record = read_record(path)
    game = GameDir(app.config.game_dir)
    launcher = (
        check_launcher(game, app.services.launcher_running())
        if record.profile
        else None
    )
    worlds = _worlds(path)
    held = {0: "", 1: ", with its 1 world"}.get(worlds, f", with its {worlds} worlds")
    app.out.print(f"Delete {path} and everything in it{held}. This cannot be undone.")
    confirm_name(app, path.name, yes=yes, force=force)
    instance.delete()
    if launcher is not None and record.profile:
        launcher.remove_profile(record.profile)
    remember_external(app.paths, path, keep=False)
    app.out.print(f"Deleted {path.name}.")
