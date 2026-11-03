"""What every command needs: settings, folders, platforms and output."""

import dataclasses
import os
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from functools import cached_property
from typing import cast

import typer
from modsmith.launcher import is_running
from modsmith.platforms import Platform
from rich.console import Console

from ..core.config import Config, load_config
from ..core.paths import AppPaths
from ..core.platforms import PlatformOpener, open_platform


class ColorMode(StrEnum):
    """When to use colour."""

    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"


def _interactive() -> bool:
    """Return whether a person can answer questions on this terminal."""
    return sys.stdin.isatty() and sys.stdout.isatty()


@dataclass(frozen=True)
class Services:
    """What the command line gets from the outside world.

    Tests pass their own as the click context's ``obj``.

    Attributes:
        open_platform: Opens a platform by name.
        environ: The environment variables, or None for the real ones.
        interactive: Whether a person can answer questions.
        launcher_running: Whether the official launcher is open.
    """

    open_platform: PlatformOpener = open_platform
    environ: Mapping[str, str] | None = None
    interactive: Callable[[], bool] = _interactive
    launcher_running: Callable[[], bool] = is_running


def _console(color: ColorMode, *, stderr: bool) -> Console:
    """Make a console that follows the colour choice and ``NO_COLOR``."""
    if color == ColorMode.ALWAYS:
        return Console(stderr=stderr, force_terminal=True)
    if color == ColorMode.NEVER:
        return Console(stderr=stderr, no_color=True, color_system=None)
    return Console(stderr=stderr)


@dataclass
class AppContext:
    """The state of one command-line run.

    Attributes:
        paths: The app's folders.
        services: The outside world.
        overrides: Settings given as command-line options.
        verbose: How much detail to show, from ``-v``.
        color: When to use colour.
        out: Where results go.
        err: Where errors, warnings and progress go.
    """

    paths: AppPaths
    services: Services
    overrides: dict[str, object] = field(default_factory=dict[str, object])
    verbose: int = 0
    color: ColorMode = ColorMode.AUTO
    out: Console = field(init=False)
    err: Console = field(init=False)

    def __post_init__(self) -> None:
        self.out = _console(self.color, stderr=False)
        self.err = _console(self.color, stderr=True)

    @property
    def environ(self) -> Mapping[str, str]:
        """The environment variables."""
        return (
            self.services.environ if self.services.environ is not None else os.environ
        )

    @cached_property
    def config(self) -> Config:
        """The settings in effect. Read on first use, so ``config`` can fix bad ones.

        Raises:
            AppError: A setting is invalid.
        """
        config = load_config(self.paths, self.environ)
        return dataclasses.replace(config, **self.overrides)

    def platform(self, name: str) -> Platform:
        """Open a platform by name.

        Raises:
            AppError: The platform needs a key that is not set.
        """
        return self.services.open_platform(name, self.config)


def get(ctx: typer.Context) -> AppContext:
    """Return the run's state from any command's context."""
    return cast(AppContext, ctx.find_root().obj)
