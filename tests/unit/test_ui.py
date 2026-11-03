import io
import signal

import pytest
from modsmith.instances import Changes
from rich.console import Console

from modsmith_app.cli.context import AppContext, Services
from modsmith_app.cli.ui import cancellable, confirm, confirm_name, show_plan
from modsmith_app.core.errors import AppError


def make_app(paths, *, interactive=False, verbose=0) -> tuple[AppContext, io.StringIO]:
    app = AppContext(paths, Services(interactive=lambda: interactive), verbose=verbose)
    out = io.StringIO()
    app.out = Console(file=out, width=120, no_color=True)
    return app, out


def test_plan_lists_each_kind_and_sums_up(paths):
    app, out = make_app(paths)
    changes = Changes(
        added=("mods/a.jar", "mods/b.jar"),
        updated=("mods/c.jar",),
        removed=("mods/old.jar",),
        conflicts=("config/x.toml",),
        superseded=("mods/d.jar",),
    )
    sizes = {"mods/a.jar": 1_500_000, "mods/b.jar": 500_000, "mods/c.jar": None}
    assert show_plan(app, changes, sizes, title="Plan for survival")
    text = out.getvalue()
    assert text.splitlines() == [
        "Plan for survival",
        "  + mods/a.jar",
        "  + mods/b.jar",
        "  ~ mods/c.jar",
        "  - mods/old.jar",
        "  ! config/x.toml",
        "  = mods/d.jar is now part of the pack",
        "2 to add, 1 to update, 1 to remove, 1 of your changes kept; 2.0 MB to download.",
    ]


def test_long_plans_are_shortened_unless_verbose(paths):
    changes = Changes(added=tuple(f"mods/{index}.jar" for index in range(30)))
    app, out = make_app(paths)
    show_plan(app, changes)
    assert "  + and 18 more" in out.getvalue()
    app, out = make_app(paths, verbose=1)
    show_plan(app, changes)
    assert "and 18 more" not in out.getvalue()
    assert "  + mods/29.jar" in out.getvalue()


def test_empty_plan(paths):
    app, out = make_app(paths)
    assert not show_plan(app, Changes(unchanged=("mods/a.jar",)))
    assert out.getvalue() == "Nothing to change.\n"


def test_confirmation_needs_a_terminal_or_yes(paths):
    app, _ = make_app(paths)
    confirm(app, "Go?", yes=True)
    with pytest.raises(AppError, match="no terminal") as caught:
        confirm(app, "Go?", yes=False)
    assert caught.value.hint == "Run it again with --yes."


def test_irreversible_actions_need_force_with_yes(paths):
    app, _ = make_app(paths)
    confirm_name(app, "survival", yes=True, force=True)
    with pytest.raises(AppError, match="--yes alone"):
        confirm_name(app, "survival", yes=True, force=False)
    with pytest.raises(AppError, match="cannot be undone") as caught:
        confirm_name(app, "survival", yes=False, force=False)
    assert caught.value.hint == "Run it again with --yes --force."


def test_first_ctrl_c_cancels_and_the_second_stops():
    before = signal.getsignal(signal.SIGINT)
    with cancellable() as token:
        handler = signal.getsignal(signal.SIGINT)
        assert callable(handler)
        handler(signal.SIGINT, None)
        assert token.cancelled
        with pytest.raises(KeyboardInterrupt):
            handler(signal.SIGINT, None)
    assert signal.getsignal(signal.SIGINT) is before
