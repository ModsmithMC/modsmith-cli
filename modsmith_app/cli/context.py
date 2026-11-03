"""What every command needs: settings, folders, platforms and output."""

import dataclasses
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import cached_property
from typing import cast

import typer
from modsmith.platforms import Platform
from rich.console import Console

from ..core.config import Config, load_config
from ..core.paths import AppPaths
from ..core.platforms import PlatformOpener, open_platform


@dataclass(frozen=True)
class Services:
    """What the command line gets from the outside world.

    Tests pass their own as the click context's ``obj``.

    Attributes:
        open_platform: Opens a platform by name.
        environ: The environment variables, or None for the real ones.
    """

    open_platform: PlatformOpener = open_platform
    environ: Mapping[str, str] | None = None


@dataclass
class AppContext:
    """The state of one command-line run.

    Attributes:
        paths: The app's folders.
        services: The outside world.
        overrides: Settings given as command-line options.
        out: Where results go.
        err: Where errors, warnings and progress go.
    """

    paths: AppPaths
    services: Services
    overrides: dict[str, object] = field(default_factory=dict[str, object])
    out: Console = field(default_factory=Console)
    err: Console = field(default_factory=lambda: Console(stderr=True))

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
