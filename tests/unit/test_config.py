import sys

import pytest

from modsmith_app.core import config as settings
from modsmith_app.core.config import load_config, save_setting, sources
from modsmith_app.core.errors import AppError


def test_defaults(paths, tmp_path):
    config = load_config(paths)
    user = tmp_path / "user"
    # The official launcher's own folder on each system.
    launcher = (
        user / "Library" / "Application Support" / "minecraft"
        if sys.platform == "darwin"
        else user / ".minecraft"
    )
    assert config.instances_dir == paths.default_instances_dir
    assert config.game_dir == launcher.resolve()
    assert config.curseforge_api_key is None
    assert config.default_platform == "modrinth"
    assert config.allow_prereleases is False


def test_file_and_environment_override_defaults(paths, tmp_path):
    save_setting(paths, "default_platform", "CurseForge")
    save_setting(paths, "allow_prereleases", "yes")
    save_setting(paths, "instances_dir", str(tmp_path / "from-file"))
    environ = {"MODSMITH_INSTANCES_DIR": str(tmp_path / "from-env")}

    config = load_config(paths, environ)

    assert config.default_platform == "curseforge"
    assert config.allow_prereleases is True
    assert config.instances_dir == tmp_path / "from-env"
    found = sources(paths, environ)
    assert found["instances_dir"] == "$MODSMITH_INSTANCES_DIR"
    assert found["default_platform"] == "config file"
    assert found["game_dir"] == "default"


def test_saved_booleans_are_real_toml_booleans(paths):
    save_setting(paths, "allow_prereleases", "on")
    assert "allow_prereleases = true" in paths.config_file.read_text()
    save_setting(paths, "allow_prereleases", None)
    assert load_config(paths).allow_prereleases is False


def test_bad_values_say_where_they_came_from(paths):
    paths.config_file.parent.mkdir(parents=True)
    paths.config_file.write_text('default_platform = "planet"\n')
    with pytest.raises(AppError, match=r"default_platform in .*config\.toml"):
        load_config(paths)
    paths.config_file.unlink()
    with pytest.raises(AppError, match=r"\$CURSEFORGE_API_KEY"):
        load_config(paths, {"CURSEFORGE_API_KEY": "   "})


def test_unknown_keys_in_the_file_are_ignored(paths):
    paths.config_file.parent.mkdir(parents=True)
    paths.config_file.write_text("added_later = 1\n")
    assert load_config(paths).default_platform == "modrinth"


def test_invalid_toml(paths):
    paths.config_file.parent.mkdir(parents=True)
    paths.config_file.write_text("this is = = not toml")
    with pytest.raises(AppError, match="not valid TOML"):
        load_config(paths)


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("nothing", "x"),
        ("allow_prereleases", "maybe"),
        ("default_platform", "planet"),
        ("instances_dir", " "),
        ("curseforge_api_key", ""),
    ],
)
def test_save_rejects_bad_settings(paths, key, value):
    with pytest.raises(AppError):
        save_setting(paths, key, value)


def test_shown_values():
    assert settings.shown("curseforge_api_key", "secret") == "set (hidden)"
    assert settings.shown("curseforge_api_key", None) == "not set"
    assert settings.shown("allow_prereleases", True) == "true"
