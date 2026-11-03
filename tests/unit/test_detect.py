import pytest
from modsmith.minecraft import GameDir

from modsmith_app.core.detect import GameVersions, detect
from modsmith_app.core.errors import AppError


@pytest.fixture
def game(tmp_path) -> GameDir:
    folder = GameDir(tmp_path / ".minecraft")
    folder.write_version("1.20.1", {"id": "1.20.1"})
    return folder


def test_vanilla(game):
    assert detect(game, "1.20.1") == GameVersions("1.20.1")


def test_forge_from_its_arguments(game):
    game.write_version(
        "1.20.1-forge-47.3.0",
        {
            "id": "1.20.1-forge-47.3.0",
            "inheritsFrom": "1.20.1",
            "arguments": {
                "game": [
                    "--launchTarget",
                    "forgeclient",
                    "--fml.forgeVersion",
                    "47.3.0",
                ]
            },
        },
    )
    assert detect(game, "1.20.1-forge-47.3.0") == GameVersions(
        "1.20.1", "forge", "47.3.0"
    )


def test_neoforge_and_quilt_from_their_libraries(game):
    game.write_version(
        "neo",
        {
            "id": "neo",
            "inheritsFrom": "1.20.1",
            "libraries": [{"name": "net.neoforged:forge:1.20.1-47.1.106:universal"}],
        },
    )
    game.write_version(
        "quilt",
        {
            "id": "quilt",
            "inheritsFrom": "1.20.1",
            "libraries": [
                "odd",
                {"name": 3},
                {"name": "org.quiltmc:quilt-loader:0.26.4"},
            ],
        },
    )
    assert detect(game, "neo") == GameVersions("1.20.1", "neoforge", "47.1.106")
    assert detect(game, "quilt") == GameVersions("1.20.1", "quilt", "0.26.4")


def test_old_forge_from_legacy_arguments(game):
    game.write_version(
        "old",
        {
            "id": "old",
            "inheritsFrom": "1.20.1",
            "minecraftArguments": "--tweakClass x --fml.forgeVersion 14.23.5.2860",
        },
    )
    assert detect(game, "old").loader_version == "14.23.5.2860"


def test_a_missing_parent(game):
    game.write_version("child", {"id": "child", "inheritsFrom": "1.7.10"})
    with pytest.raises(AppError, match=r"Version 1.7.10 is not installed"):
        detect(game, "child")
