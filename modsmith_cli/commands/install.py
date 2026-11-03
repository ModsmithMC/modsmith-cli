"""``modsmith install`` and ``modsmith create``: new instances, ready to play."""

from pathlib import Path
from typing import Annotated

import typer
from modsmith.errors import InstanceError, UnresolvedEntriesError, UnsupportedError
from modsmith.instances import Instance
from modsmith.loaders import Loader, create, recommended
from modsmith.minecraft import GameDir, install_version, list_versions
from modsmith.packs import Modpack

from ..context import AppContext, get
from ..core.config import Config
from ..core.errors import AppError
from ..core.install import (
    check_launcher,
    download_sizes,
    fetch_pack,
    match_optional,
    optional_entries,
    profile_key,
    profile_name,
    project_icon,
    with_optional,
)
from ..core.names import check_name, name_from
from ..core.platforms import explained
from ..core.records import Record, write_record
from ..core.refs import ProjectRef, parse_pack
from ..errors import report as report_error
from ..target import DryRun, Yes
from ..ui import cancellable, confirm, progress, show_plan

LOADER_NAMES = {
    "forge": "Forge",
    "neoforge": "NeoForge",
    "fabric": "Fabric",
    "quilt": "Quilt",
}


def loader_label(kind: str | None, version: str | None) -> str:
    """Name a loader for people, such as ``Fabric 0.16.10``."""
    if not kind:
        return "no mod loader"
    name = LOADER_NAMES.get(kind.lower(), kind)
    return f"{name} {version}" if version else name


def free_folder(name: str, config: Config) -> Path:
    """Return the folder for a new instance.

    Raises:
        AppError: An instance or other files are already there.
    """
    path = config.instances_dir / check_name(name)
    try:
        taken = Instance(path).state is not None
    except InstanceError:
        taken = True
    if taken:
        raise AppError(
            f"There is already an instance called {name!r}.",
            hint=f"Update it with: modsmith update {name}. Or choose another "
            "name with --name.",
        )
    if path.exists() and any(path.iterdir()):
        raise AppError(
            f"{path} already holds other files.",
            hint="Choose another name with --name.",
        )
    return path


def _ask_optional(app: AppContext, pack: Modpack) -> list[str]:
    """Let the player pick optional files by number."""
    options = [entry.path for entry in optional_entries(pack) if entry.path]
    app.out.print("This pack has optional files:")
    for index, path in enumerate(options, 1):
        app.out.print(f"  {index}. {path}")
    answer = typer.prompt(
        "Which do you want? Numbers separated by spaces, all, or Enter for none",
        default="",
        show_default=False,
    ).strip()
    if answer.lower() == "all":
        return options
    try:
        picked = [int(word) for word in answer.replace(",", " ").split()]
    except ValueError:
        raise AppError(f"{answer!r} is not a list of numbers.") from None
    if any(number < 1 or number > len(options) for number in picked):
        raise AppError(f"Choose numbers from 1 to {len(options)}.")
    return [options[number - 1] for number in dict.fromkeys(picked)]


def choose_optional(
    app: AppContext, pack: Modpack, patterns: list[str], everything: bool, yes: bool
) -> list[str]:
    """Decide which optional files to install, asking if nobody said."""
    options = optional_entries(pack)
    if everything:
        return [entry.path for entry in options if entry.path]
    if patterns:
        return match_optional(pack, patterns)
    if not options:
        return []
    if yes or not app.services.interactive():
        app.err.print(
            f"Left out {len(options)} optional files. "
            "Choose them with --optional or --all-optional.",
            style="dim",
        )
        return []
    return _ask_optional(app, pack)


Optional = Annotated[
    list[str] | None,
    typer.Option(
        "--optional",
        help="Install the optional files whose names contain this. Repeat for more.",
        show_default=False,
    ),
]
AllOptional = Annotated[
    bool, typer.Option("--all-optional", help="Install every optional file.")
]
From = Annotated[
    list[Path] | None,
    typer.Option(
        "--from",
        help="A folder with files you downloaded by hand. Repeat for more.",
        show_default=False,
    ),
]
Overwrite = Annotated[
    bool,
    typer.Option(
        "--overwrite", help="Replace files you changed, instead of keeping them."
    ),
]


def install_command(
    ctx: typer.Context,
    source: Annotated[
        str,
        typer.Argument(
            help="A pack file, a project such as fabulously-optimized or "
            "curseforge:<id>, or its web address.",
            show_default=False,
        ),
    ],
    name: Annotated[
        str | None,
        typer.Option("--name", help="The instance's name. Defaults to the pack's."),
    ] = None,
    optional: Optional = None,
    all_optional: AllOptional = False,
    from_folders: From = None,
    yes: Yes = False,
    dry_run: DryRun = False,
) -> None:
    """Install a modpack as a new instance in the official launcher."""
    app = get(ctx)
    config = app.config
    ref = parse_pack(source, config.default_platform)
    game = GameDir(config.game_dir)
    launcher = (
        None if dry_run else check_launcher(game, app.services.launcher_running())
    )
    platform, wanted = (
        (ref.platform, [ref.name]) if isinstance(ref, ProjectRef) else ("", [])
    )
    with cancellable() as token, progress(app) as report, explained(platform, wanted):
        fetched = fetch_pack(
            ref,
            app.platform,
            cache_dir=app.paths.cache_dir,
            allow_prereleases=config.allow_prereleases,
            progress=report,
            cancel=token,
        )
    path = free_folder(name or name_from(fetched.pack.name), config)
    chosen = choose_optional(app, fetched.pack, optional or [], all_optional, yes)
    pack = with_optional(fetched.pack, chosen)
    missing = [entry for entry in pack.unresolved if entry.wanted("client")]
    if missing and not from_folders and not dry_run:
        raise UnresolvedEntriesError(missing)

    instance = Instance(path)
    title = f"Install {pack.name} {pack.version} as {path.name}"
    show_plan(app, instance.diff(pack), download_sizes(pack), title=title)
    app.out.print(
        f"Minecraft {pack.minecraft} with "
        f"{loader_label(pack.loader_kind, pack.loader_version)}, "
        "and an installation in the official launcher."
    )
    if missing and not from_folders:
        report_error(
            UnresolvedEntriesError(missing), app.err, prefix="Before you install: "
        )
    if dry_run or launcher is None:
        return
    confirm(app, "Install it?", yes=yes)
    with cancellable() as token, progress(app) as report:
        version_id = pack.install_game(
            game, cache_dir=app.paths.cache_dir, progress=report, cancel=token
        )
        instance.sync(
            pack, adopt_from=from_folders or (), progress=report, cancel=token
        )
    key = profile_key(path.name)
    shown = profile_name(launcher, pack.name, key, path.name)
    key = launcher.add_profile(
        shown,
        version_id,
        instance.path,
        key=key,
        memory_mb=pack.memory_mb,
        icon=project_icon(fetched.project),
    )
    write_record(instance.path, Record(fetched.source, key, tuple(chosen)))
    app.out.print(
        f"Installed {pack.name} as {path.name}. In the official launcher, "
        f"choose the {shown} installation and play."
    )


LOADER_HINT = "Use fabric, quilt, forge or neoforge."


def _registered(kind: str, minecraft: str) -> bool:
    """Return whether the library knows a loader by this name."""
    try:
        create(kind, "0", minecraft)
    except UnsupportedError:
        return False
    return True


def _pick_loader(
    kind: str | None, version: str | None, minecraft: str
) -> Loader | None:
    """Return the loader to install, choosing a version if none was given.

    Raises:
        AppError: The loader is unknown, or has no version for this Minecraft.
    """
    if version and not kind:
        raise AppError("--loader-version needs --loader too.")
    if not kind:
        return None
    try:
        if version:
            return create(kind, version, minecraft)
        return recommended(kind, minecraft)
    except UnsupportedError as e:
        if not _registered(kind, minecraft):
            raise AppError(
                f"Modsmith cannot install {kind!r}.", hint=LOADER_HINT
            ) from e
        raise AppError(
            f"{loader_label(kind, None)} has no version for Minecraft {minecraft}.",
            hint="Check the Minecraft version, or choose another loader.",
        ) from e


def _check_minecraft(game: GameDir, minecraft: str) -> None:
    """Make sure a Minecraft version exists before planning around it.

    Raises:
        AppError: Mojang has no such version.
    """
    if game.has_version(minecraft):
        return
    if not any(item.id == minecraft for item in list_versions()):
        raise AppError(
            f"There is no Minecraft {minecraft}.",
            hint="Use a version such as 1.21.1. Snapshots work too.",
        )


def create_command(
    ctx: typer.Context,
    name: Annotated[
        str, typer.Argument(help="The new instance's name.", show_default=False)
    ],
    minecraft: Annotated[
        str,
        typer.Option(
            "--minecraft", "-m", help="The Minecraft version.", show_default=False
        ),
    ],
    loader: Annotated[
        str | None,
        typer.Option("--loader", "-l", help="fabric, quilt, forge or neoforge."),
    ] = None,
    loader_version: Annotated[
        str | None,
        typer.Option("--loader-version", help="Defaults to the recommended version."),
    ] = None,
    yes: Yes = False,
    dry_run: DryRun = False,
) -> None:
    """Create an empty instance, with or without a mod loader."""
    app = get(ctx)
    config = app.config
    path = free_folder(name, config)
    game = GameDir(config.game_dir)
    launcher = (
        None if dry_run else check_launcher(game, app.services.launcher_running())
    )
    chosen = _pick_loader(loader, loader_version, minecraft)
    if chosen is None:
        _check_minecraft(game, minecraft)
    label = loader_label(
        chosen.kind if chosen else None, chosen.version if chosen else None
    )
    app.out.print(
        f"Create {name}: Minecraft {minecraft} with {label}, "
        "and an installation in the official launcher."
    )
    if dry_run or launcher is None:
        return
    confirm(app, "Create it?", yes=yes)
    with cancellable() as token, progress(app) as report:
        if chosen is None:
            version_id = install_version(
                game, minecraft, progress=report, cancel=token
            ).id
        else:
            version_id = chosen.install(
                game, cache_dir=app.paths.cache_dir, progress=report, cancel=token
            )
    Instance.create(
        path,
        minecraft=minecraft,
        loader=chosen.kind if chosen else None,
        loader_version=chosen.version if chosen else None,
    )
    key = profile_key(name)
    key = launcher.add_profile(
        profile_name(launcher, name, key, name), version_id, path, key=key
    )
    write_record(path, Record(profile=key))
    app.out.print(
        f"Created {name}. In the official launcher, choose the {name} installation."
    )
