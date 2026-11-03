"""Where the app keeps its configuration, data and caches."""

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_cache_path, user_config_path, user_data_path

HOME_VARIABLE = "MODSMITH_HOME"


@dataclass(frozen=True)
class AppPaths:
    """The app's own folders.

    Attributes:
        config_dir: Holds ``config.toml``.
        data_dir: Holds instances and the list of instances kept elsewhere.
        cache_dir: Holds downloaded Java runtimes and loader installers.
    """

    config_dir: Path
    data_dir: Path
    cache_dir: Path

    @property
    def config_file(self) -> Path:
        """The configuration file."""
        return self.config_dir / "config.toml"

    @property
    def default_instances_dir(self) -> Path:
        """Where instances go unless the configuration says otherwise."""
        return self.data_dir / "instances"

    @property
    def external_file(self) -> Path:
        """The list of instances outside the instances folder."""
        return self.data_dir / "external.json"

    @classmethod
    def from_environment(cls, environ: Mapping[str, str] = os.environ) -> "AppPaths":
        """Use ``MODSMITH_HOME`` if it is set, and the system's usual folders if not.

        Args:
            environ: The environment variables.

        Returns:
            The folders.
        """
        home = environ.get(HOME_VARIABLE)
        if home:
            root = Path(home).expanduser()
            return cls(root, root, root / "cache")
        # Linux folders are lowercase by convention.
        name = "modsmith" if sys.platform.startswith("linux") else "Modsmith"
        return cls(
            user_config_path(name, appauthor=False, roaming=True),
            user_data_path(name, appauthor=False),
            user_cache_path(name, appauthor=False),
        )
