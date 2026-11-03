from pathlib import Path

from modsmith_app.core.paths import AppPaths


def test_home_variable_puts_everything_in_one_folder(tmp_path):
    paths = AppPaths.from_environment({"MODSMITH_HOME": str(tmp_path)})
    assert paths.config_dir == paths.data_dir == tmp_path
    assert paths.cache_dir == tmp_path / "cache"
    assert paths.config_file == tmp_path / "config.toml"
    assert paths.default_instances_dir == tmp_path / "instances"
    assert paths.external_file == tmp_path / "external.json"


def test_system_folders_are_named_after_the_app():
    paths = AppPaths.from_environment({})
    for folder in (paths.config_dir, paths.data_dir):
        assert "modsmith" in [part.lower() for part in Path(folder).parts]
