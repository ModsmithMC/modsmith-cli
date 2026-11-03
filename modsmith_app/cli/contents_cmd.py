"""Commands that look at and change what an instance holds."""

from collections.abc import Sequence
from enum import StrEnum
from typing import Annotated

import typer
from modsmith import metadata
from modsmith.errors import DependencyError, InstanceError, ModsmithError
from modsmith.instances import Changes, Instance, Plan
from modsmith.platforms import ProjectType
from rich.table import Table
from rich.text import Text

from ..core.config import PLATFORMS
from ..core.contents import find_contents
from ..core.errors import AppError
from ..core.platforms import explained
from ..core.refs import parse_project
from ..core.registry import resolve_instance, split_target
from .context import AppContext, get
from .errors import report
from .install_cmd import From, Overwrite, loader_label
from .target import DryRun, InstanceName, Yes
from .ui import cancellable, confirm, progress, show_plan

SOURCES = {"pack": "pack", "addition": "added", "user": "yours"}


class AddedKind(StrEnum):
    """The kinds of projects that can be added to an instance."""

    MOD = "mod"
    RESOURCEPACK = "resourcepack"
    SHADER = "shader"


ADDED_KINDS: dict[AddedKind, ProjectType] = {
    AddedKind.MOD: "mod",
    AddedKind.RESOURCEPACK: "resourcepack",
    AddedKind.SHADER: "shader",
}

Items = Annotated[
    list[str],
    typer.Argument(
        help="The instance, then what to act on. Leave the instance out if you "
        "have only one.",
        show_default=False,
    ),
]


def _heading(name: str, instance: Instance) -> str:
    state = instance.state
    if state is None:
        return name
    loader = loader_label(state.loader_kind, state.loader_version)
    pack = f", from {state.pack_name} {state.pack_version}" if state.pack_name else ""
    return f"{name}: Minecraft {state.minecraft} with {loader}{pack}"


def show_command(ctx: typer.Context, name: InstanceName = None) -> None:
    """List the mods, resource packs and shaders in an instance."""
    app = get(ctx)
    instance, _ = resolve_instance(name, app.config, app.paths)
    app.out.print(Text(_heading(instance.path.name, instance), style="bold"))
    contents = instance.contents()
    if not contents:
        app.out.print("It holds no mods, resource packs or shaders yet.")
        return
    table = Table(box=None, pad_edge=False)
    for column in ("Name", "Version", "From", "State"):
        table.add_column(column, no_wrap=column != "Name")
    table.add_column("File", overflow="fold")
    for item in contents:
        try:
            info = metadata.read(instance.path / item.location)
        except OSError:
            info = None
        label = (item.addition.name if item.addition else None) or (
            info.name if info else item.path.rsplit("/", 1)[-1]
        )
        flags = [] if item.enabled else ["off"]
        if item.addition and item.addition.pinned:
            flags.append("pinned")
        table.add_row(
            label,
            (info.version if info else None) or "",
            SOURCES[item.source],
            ", ".join(flags),
            item.location,
        )
    app.out.print(table)


def _notes(app: AppContext, plan: Plan) -> None:
    """Say what a plan leaves out and why."""
    for item in plan.skipped:
        app.out.print(Text(f"  = {item.name} is already in the pack", style="dim"))
    for name in plan.unavailable:
        app.out.print(
            Text(f"  ? {name} has no release for this instance", style="yellow")
        )
    for item in plan.additions:
        if not item.requested:
            app.out.print(
                Text(f"    {item.path} is needed by another mod", style="dim")
            )


def add_command(
    ctx: typer.Context,
    items: Items,
    kind: Annotated[
        AddedKind, typer.Option("--type", "-t", help="The kind of project.")
    ] = AddedKind.MOD,
    optional: Annotated[
        bool, typer.Option("--optional", help="Also add optional dependencies.")
    ] = False,
    pre: Annotated[
        bool, typer.Option("--pre", help="Allow alpha and beta releases.")
    ] = False,
    overwrite: Overwrite = False,
    from_folders: From = None,
    yes: Yes = False,
    dry_run: DryRun = False,
) -> None:
    """Add mods, resource packs or shaders to an instance, with what they need."""
    app = get(ctx)
    instance, _, names = split_target(items, app.config, app.paths)
    if not names:
        raise AppError("Name at least one project to add.")
    refs = [parse_project(name, app.config.default_platform) for name in names]
    release_only = not (pre or app.config.allow_prereleases)
    plans: list[tuple[str, Plan]] = []
    for platform_name in PLATFORMS:
        wanted = [ref.name for ref in refs if ref.platform == platform_name]
        if not wanted:
            continue
        with explained(platform_name), app.platform(platform_name) as platform:
            plan = instance.plan(
                platform,
                wanted,
                project_type=ADDED_KINDS[kind],
                include_optional=optional,
                release_only=release_only,
            )
        plans.append((platform_name, plan))

    title = f"Add to {instance.path.name}"
    changes = Changes(
        added=tuple(path for _, plan in plans for path in plan.changes.added),
        updated=tuple(path for _, plan in plans for path in plan.changes.updated),
        removed=tuple(path for _, plan in plans for path in plan.changes.removed),
        conflicts=tuple(path for _, plan in plans for path in plan.changes.conflicts),
    )
    sizes = {item.path: item.entry.size for _, plan in plans for item in plan.additions}
    pending = show_plan(app, changes, sizes, title=title)
    for _, plan in plans:
        _notes(app, plan)
    for _, plan in plans:
        if not plan.ok:
            raise DependencyError(plan)
    if not pending or dry_run:
        return
    confirm(app, "Add them?", yes=yes)
    with cancellable() as token, progress(app) as update:
        for _, plan in plans:
            instance.add(
                plan,
                overwrite=overwrite,
                adopt_from=from_folders or (),
                progress=update,
                cancel=token,
            )
    app.out.print(f"Added to {instance.path.name}.")


def remove_command(
    ctx: typer.Context,
    items: Items,
    keep_dependencies: Annotated[
        bool,
        typer.Option(
            "--keep-deps", help="Keep dependencies even if nothing needs them."
        ),
    ] = False,
    yes: Yes = False,
    dry_run: DryRun = False,
) -> None:
    """Remove projects you added, and the dependencies nothing else needs."""
    app = get(ctx)
    instance, _, names = split_target(items, app.config, app.paths)
    if not names:
        raise AppError("Name at least one project to remove.")
    try:
        preview = instance.remove(
            *names, keep_dependencies=keep_dependencies, dry_run=True
        )
    except InstanceError as e:
        raise AppError(
            str(e) + ".",
            hint="Files from the pack cannot be removed, but you can turn them off "
            "with: modsmith disable",
        ) from e
    show_plan(app, preview, title=f"Remove from {instance.path.name}")
    if dry_run:
        return
    confirm(app, "Remove them?", yes=yes)
    instance.remove(*names, keep_dependencies=keep_dependencies)
    app.out.print(f"Removed from {instance.path.name}.")


def _toggle(ctx: typer.Context, items: list[str], *, enabled: bool) -> None:
    app = get(ctx)
    instance, _, names = split_target(items, app.config, app.paths)
    if not names:
        raise AppError("Name at least one file or project.")
    targets = find_contents(instance, names)
    paths = [item.path for item in targets]
    if enabled:
        instance.enable(*paths)
    else:
        instance.disable(*paths)
    verb = "Turned on" if enabled else "Turned off"
    for path in paths:
        app.out.print(f"{verb} {path}.")


def enable_command(ctx: typer.Context, items: Items) -> None:
    """Turn mods, resource packs or shaders back on."""
    _toggle(ctx, items, enabled=True)


def disable_command(ctx: typer.Context, items: Items) -> None:
    """Turn mods, resource packs or shaders off, without removing them."""
    _toggle(ctx, items, enabled=False)


def _pin(ctx: typer.Context, items: list[str], *, pinned: bool) -> None:
    app = get(ctx)
    instance, _, names = split_target(items, app.config, app.paths)
    if not names:
        raise AppError("Name at least one project.")
    for name in names:
        try:
            addition = instance.pin(name, pinned)
        except ModsmithError as e:
            raise AppError(
                f"{name!r} was not added on its own, so it cannot be pinned.",
                hint="Pack files follow the pack's own updates.",
            ) from e
        state = "stays at its release" if pinned else "follows updates again"
        app.out.print(f"{addition.name} {state}.")


def pin_command(ctx: typer.Context, items: Items) -> None:
    """Keep projects you added at their current release."""
    _pin(ctx, items, pinned=True)


def unpin_command(ctx: typer.Context, items: Items) -> None:
    """Let pinned projects update again."""
    _pin(ctx, items, pinned=False)


class AdoptFrom(StrEnum):
    """Which platforms may recognise files."""

    MODRINTH = "modrinth"
    CURSEFORGE = "curseforge"
    ALL = "all"


def adopt_files(app: AppContext, instance: Instance, names: Sequence[str]) -> int:
    """Ask each platform to recognise the player's files, and say what it found.

    With several platforms, one that cannot be used is skipped with a note.

    Returns:
        How many files were recognised.
    """
    found = 0
    for platform_name in names:
        try:
            with (
                cancellable() as token,
                progress(app) as update,
                explained(platform_name),
                app.platform(platform_name) as platform,
            ):
                adopted = instance.adopt(platform, progress=update, cancel=token)
        except AppError as e:
            if len(names) == 1:
                raise
            report(e, app.err, prefix=f"Skipped {platform_name}: ")
            continue
        for item in adopted:
            app.out.print(f"  {item.name}: {item.path}")
        found += len(adopted)
    if found:
        files = "1 file" if found == 1 else f"{found} files"
        app.out.print(f"{files} can now be updated and removed like added ones.")
    else:
        app.out.print("No unrecognised files were found on these platforms.")
    return found


def adopt_command(
    ctx: typer.Context,
    name: InstanceName = None,
    where: Annotated[
        AdoptFrom,
        typer.Option("--platform", "-p", help="Which platforms may recognise files."),
    ] = AdoptFrom.ALL,
) -> None:
    """Recognise files you put in an instance, so they can be updated and removed."""
    app = get(ctx)
    instance, _ = resolve_instance(name, app.config, app.paths)
    names = list(PLATFORMS) if where == AdoptFrom.ALL else [where.value]
    adopt_files(app, instance, names)
