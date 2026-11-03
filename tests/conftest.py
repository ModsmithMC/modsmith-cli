from collections.abc import Callable
from pathlib import Path

import pytest
import pytest_socket
from typer.testing import CliRunner, Result

from modsmith_app.cli import app
from modsmith_app.cli.context import Services
from modsmith_app.core.config import Config, load_config
from modsmith_app.core.paths import AppPaths
from tests.lib.catalog import Catalog

VARIABLES = (
    "MODSMITH_INSTANCES_DIR",
    "MODSMITH_GAME_DIR",
    "CURSEFORGE_API_KEY",
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
def catalogs() -> dict[str, Catalog]:
    """The platforms the command line sees, keyed by name. Tests fill them."""
    return {"modrinth": Catalog(name="modrinth")}


@pytest.fixture
def run(catalogs: dict[str, Catalog]) -> Callable[..., Result]:
    """Run the command line with the test catalogues as its platforms."""

    def open_platform(name: str, config: Config) -> Catalog:
        if name not in catalogs:
            from modsmith_app.core.platforms import open_platform as real

            real(name, config)
        source = catalogs[name]
        return Catalog(
            *source.projects,
            releases=tuple(source.releases),
            name=name,
            refuse=source.refuse,
        )

    def invoke(*args: str) -> Result:
        services = Services(open_platform=open_platform)
        return CliRunner().invoke(app, list(args), obj=services, prog_name="modsmith")

    return invoke
