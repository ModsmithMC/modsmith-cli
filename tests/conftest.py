import json
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
import pytest_socket
from modsmith.minecraft import GameDir
from typer.testing import CliRunner, Result

import tests.lib.loaders  # noqa: F401  Registers the test loader with the library.
from modsmith_app.cli import app
from modsmith_app.cli.context import Services
from modsmith_app.core.config import Config, load_config
from modsmith_app.core.paths import AppPaths
from modsmith_app.core.platforms import open_platform as real_open_platform
from tests.lib.catalog import Catalog
from tests.lib.server import LocalServer

VARIABLES = (
    "MODSMITH_INSTANCES_DIR",
    "MODSMITH_GAME_DIR",
    "CURSEFORGE_API_KEY",
    "NO_COLOR",
)


@pytest.fixture(autouse=True)
def _block_internet(request: pytest.FixtureRequest) -> None:
    """Only tests under tests/live may leave this machine."""
    if "live" not in request.path.parts:
        pytest_socket.socket_allow_hosts(["127.0.0.1"])


@pytest.fixture(autouse=True)
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Keep every test's settings, data and game directory inside tmp_path."""
    root = tmp_path / "home"
    monkeypatch.setenv("MODSMITH_HOME", str(root))
    for name in ("APPDATA", "HOME", "USERPROFILE"):
        monkeypatch.setenv(name, str(tmp_path / "user"))
    for name in VARIABLES:
        monkeypatch.delenv(name, raising=False)
    # A wide, fixed terminal keeps table rows on one line in assertions.
    monkeypatch.setenv("COLUMNS", "200")
    return root


@pytest.fixture
def paths() -> AppPaths:
    return AppPaths.from_environment()


@pytest.fixture
def config(paths: AppPaths) -> Config:
    return load_config(paths)


@pytest.fixture
def server() -> Iterator[LocalServer]:
    local = LocalServer()
    yield local
    local.close()


@pytest.fixture
def game(config: Config) -> GameDir:
    """The game directory, set up as the official launcher leaves it."""
    folder = GameDir(config.game_dir)
    folder.path.mkdir(parents=True, exist_ok=True)
    (folder.path / "launcher_profiles.json").write_text(
        json.dumps({"profiles": {}}), encoding="utf-8"
    )
    return folder


@pytest.fixture
def catalogs() -> dict[str, Catalog]:
    """The platforms the command line sees, keyed by name. Tests fill them."""
    return {"modrinth": Catalog(name="modrinth")}


@pytest.fixture
def run(catalogs: dict[str, Catalog]) -> Callable[..., Result]:
    """Run the command line with the test catalogues as its platforms.

    Pass ``input`` to answer prompts, ``interactive=True`` to act as if a person
    is at a terminal, and ``launcher_open=True`` to act as if the official
    launcher is running.
    """

    def open_platform(name: str, config: Config) -> Catalog:
        if name not in catalogs:
            real_open_platform(name, config)
        return catalogs[name].copy()

    def invoke(
        *args: str,
        input: str | None = None,
        interactive: bool = False,
        launcher_open: bool = False,
    ) -> Result:
        services = Services(
            open_platform=open_platform,
            interactive=lambda: interactive,
            launcher_running=lambda: launcher_open,
        )
        return CliRunner().invoke(
            app, list(args), obj=services, prog_name="modsmith", input=input
        )

    return invoke
