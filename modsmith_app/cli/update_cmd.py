"""``modsmith update``: bring an instance's pack and additions up to date."""

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Annotated

import typer
from modsmith.errors import DependencyError, UnresolvedEntriesError, UnsupportedError
from modsmith.instances import Changes, Instance, InstanceState, Plan
from modsmith.minecraft import GameDir
from modsmith.packs import Modpack
from rich.text import Text

from ..core.install import (
    FetchedPack,
    check_launcher,
    download_pack,
    download_sizes,
    fetch_pack,
    latest_pack,
    optional_entries,
    with_optional,
)
from ..core.platforms import explained
from ..core.records import Record, read_record, write_record
from ..core.refs import LocalPack
from ..core.registry import resolve_instance
from .context import AppContext, get
from .errors import report as report_error
from .install_cmd import (
    AllOptional,
    From,
    Optional,
    Overwrite,
    choose_optional,
    loader_label,
)
from .target import DryRun, InstanceName, Yes
from .ui import cancellable, confirm, progress, show_changelog, show_plan

CHANGELOG_LINES = 6


@dataclass(frozen=True)
class Choices:
    """What the player asked ``update`` to do."""

    file: Path | None
    optional: list[str]
    all_optional: bool
    prereleases: bool
    yes: bool

    @property
    def reselect(self) -> bool:
        """Whether the player chose optional files again."""
        return bool(self.optional) or self.all_optional


@dataclass(frozen=True)
class PackUpdate:
    """A newer pack, ready to sync into an instance."""

    fetched: FetchedPack
    pack: Modpack
    chosen: tuple[str, ...]
    new_game: bool


def _game(pack: Modpack | InstanceState) -> str:
    return f"Minecraft {pack.minecraft} with " + loader_label(
        pack.loader_kind, pack.loader_version
    )


def _newer_pack(
    app: AppContext, record: Record, choices: Choices
) -> tuple[FetchedPack | None, str]:
    """Fetch the pack to update to, or explain why there is none."""
    source = record.source
    if choices.file is not None:
        ref = LocalPack(choices.file)
        fetched = fetch_pack(
            ref, app.platform, cache_dir=app.paths.cache_dir, allow_prereleases=False
        )
        return fetched, ""
    if source is None:
        return None, "It has no pack."
    if source.platform is None or source.project_id is None:
        return None, "Its pack came from a file. Update it with --file <newer pack>."
    with (
        explained(source.platform),
        app.platform(source.platform) as platform,
        cancellable() as token,
        progress(app) as report,
    ):
        project, release = latest_pack(
            platform, source.project_id, allow_prereleases=choices.prereleases
        )
        if release.id == source.release_id and not choices.reselect:
            return None, f"{project.name} is up to date."
        fetched = download_pack(
            platform,
            project,
            release,
            app.platform,
            cache_dir=app.paths.cache_dir,
            progress=report,
            cancel=token,
        )
        try:
            changelog = platform.changelog(release)
        except UnsupportedError:
            changelog = ""
    show_changelog(
        app, f"What changed in {release.name}", changelog, lines=CHANGELOG_LINES
    )
    return fetched, ""


def _kept_choice(app: AppContext, pack: Modpack, record: Record) -> tuple[str, ...]:
    """Keep the optional files chosen before, where the new pack still has them."""
    offered = {entry.path for entry in optional_entries(pack)}
    kept = tuple(path for path in record.optional if path in offered)
    gone = len(record.optional) - len(kept)
    if gone:
        app.err.print(
            (
                "1 optional file you chose is"
                if gone == 1
                else f"{gone} optional files you chose are"
            )
            + " not in this release. "
            "Choose again with --optional.",
            style="yellow",
        )
    return kept


def _pack_update(
    app: AppContext, instance: Instance, state: InstanceState, choices: Choices
) -> PackUpdate | None:
    """Show what updating the pack would change, if there is a newer one."""
    record = read_record(instance.path)
    fetched, reason = _newer_pack(app, record, choices)
    if fetched is None:
        app.out.print(Text(reason, style="dim"))
        return None
    if choices.reselect:
        chosen = tuple(
            choose_optional(
                app, fetched.pack, choices.optional, choices.all_optional, choices.yes
            )
        )
    else:
        chosen = _kept_choice(app, fetched.pack, record)
    pack = with_optional(fetched.pack, chosen)
    title = f"Update {state.pack_name or 'the pack'} {state.pack_version or ''}"
    title = f"{title.rstrip()} to {pack.name} {pack.version}"
    pending = show_plan(app, instance.diff(pack), download_sizes(pack), title=title)
    new_game = _game(pack) != _game(state)
    if new_game:
        app.out.print(f"It moves from {_game(state)} to {_game(pack)}.")
    if not (pending or new_game):
        return None
    return PackUpdate(fetched, pack, chosen, new_game)


def _addition_updates(
    app: AppContext, instance: Instance, state: InstanceState, prereleases: bool
) -> list[Plan]:
    """Plan updates for the projects added on their own, platform by platform."""
    plans: list[Plan] = []
    for name in sorted({item.platform for item in state.additions}):
        with explained(name), app.platform(name) as platform:
            plan = instance.plan_updates(platform, release_only=not prereleases)
            logs: list[tuple[str, str]] = []
            for item in plan.additions:
                try:
                    release = platform.get_release(item.release_id)
                    logs.append((release.name, platform.changelog(release)))
                except UnsupportedError:
                    continue
        if not plan.additions:
            continue
        plans.append(plan)
        for title, text in logs:
            show_changelog(app, f"What changed in {title}", text, lines=CHANGELOG_LINES)
    return plans


def _show_additions(app: AppContext, name: str, plans: list[Plan]) -> bool:
    changes = Changes(
        added=tuple(path for plan in plans for path in plan.changes.added),
        updated=tuple(path for plan in plans for path in plan.changes.updated),
        removed=tuple(path for plan in plans for path in plan.changes.removed),
        conflicts=tuple(path for plan in plans for path in plan.changes.conflicts),
    )
    sizes = {item.path: item.entry.size for plan in plans for item in plan.additions}
    pending = show_plan(app, changes, sizes, title=f"Update what you added to {name}")
    for plan in plans:
        if not plan.ok:
            raise DependencyError(plan)
    return pending


def _apply_pack(
    app: AppContext,
    instance: Instance,
    update: PackUpdate,
    *,
    overwrite: bool,
    from_folders: list[Path],
) -> None:
    record = read_record(instance.path)
    game = GameDir(app.config.game_dir)
    launcher = (
        check_launcher(game, app.services.launcher_running())
        if update.new_game and record.profile
        else None
    )
    with cancellable() as token, progress(app) as report:
        version_id = update.pack.install_game(
            game, cache_dir=app.paths.cache_dir, progress=report, cancel=token
        )
        instance.sync(
            update.pack,
            overwrite=overwrite,
            adopt_from=from_folders,
            progress=report,
            cancel=token,
        )
    if launcher is not None and record.profile:
        profile = launcher.profiles().get(record.profile)
        launcher.add_profile(
            profile.name if profile else update.pack.name,
            version_id,
            instance.path,
            key=record.profile,
        )
    write_record(
        instance.path,
        replace(record, source=update.fetched.source, optional=update.chosen),
    )


def update_command(
    ctx: typer.Context,
    name: InstanceName = None,
    pack_only: Annotated[
        bool, typer.Option("--pack-only", help="Update only the pack.")
    ] = False,
    additions_only: Annotated[
        bool,
        typer.Option("--additions-only", help="Update only what you added yourself."),
    ] = False,
    file: Annotated[
        Path | None,
        typer.Option("--file", help="Update the pack from this pack file."),
    ] = None,
    optional: Optional = None,
    all_optional: AllOptional = False,
    pre: Annotated[
        bool, typer.Option("--pre", help="Allow alpha and beta releases.")
    ] = False,
    overwrite: Overwrite = False,
    from_folders: From = None,
    yes: Yes = False,
    dry_run: DryRun = False,
) -> None:
    """Update an instance's pack, and the projects you added to it."""
    app = get(ctx)
    instance, state = resolve_instance(name, app.config, app.paths)
    choices = Choices(
        file, optional or [], all_optional, pre or app.config.allow_prereleases, yes
    )
    pack = None if additions_only else _pack_update(app, instance, state, choices)
    missing = (
        [entry for entry in pack.pack.unresolved if entry.wanted("client")]
        if pack is not None and not from_folders
        else []
    )
    if missing and not dry_run:
        raise UnresolvedEntriesError(missing)
    if missing:
        report_error(
            UnresolvedEntriesError(missing), app.err, prefix="Before you update: "
        )
    plans: list[Plan] = []
    if pack is not None and pack.new_game and state.additions:
        app.out.print(
            Text(
                "What you added is updated after the pack, the next time you run "
                "modsmith update.",
                style="dim",
            )
        )
    elif pack is None or not pack.new_game:
        plans = (
            _addition_updates(app, instance, state, choices.prereleases)
            if not pack_only and state.additions
            else []
        )
    pending = _show_additions(app, instance.path.name, plans) if plans else False
    if pack is None and not pending:
        app.out.print(f"Everything in {instance.path.name} is up to date.")
        return
    if dry_run:
        return
    confirm(app, "Update them?", yes=yes)
    if pack is not None:
        _apply_pack(
            app, instance, pack, overwrite=overwrite, from_folders=from_folders or []
        )
    with cancellable() as token, progress(app) as report:
        for plan in plans:
            instance.add(
                plan,
                overwrite=overwrite,
                adopt_from=from_folders or (),
                progress=report,
                cancel=token,
            )
    app.out.print(f"Updated {instance.path.name}.")
