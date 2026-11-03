import dataclasses

import pytest
from modsmith.instances import Instance

from modsmith_cli.core.errors import AppError
from modsmith_cli.core.registry import (
    external_paths,
    list_instances,
    locate,
    open_instance,
    remember_external,
    resolve_instance,
    split_target,
)


def test_names_and_paths(config, tmp_path):
    assert locate("pack", config) == config.instances_dir / "pack"
    assert locate(str(tmp_path / "x"), config) == tmp_path / "x"
    assert locate("./x", config).name == "x"
    assert locate("~/x", config).name == "x"


def test_list_finds_instances_and_skips_other_folders(config, paths, tmp_path):
    Instance.create(config.instances_dir / "zeta", minecraft="1.21.1", loader="fabric")
    Instance.create(config.instances_dir / "Alpha", minecraft="1.20.1")
    (config.instances_dir / "not-an-instance").mkdir()
    (config.instances_dir / "file.txt").write_text("x")
    elsewhere = tmp_path / "elsewhere"
    Instance.create(elsewhere, minecraft="1.12.2")
    remember_external(paths, elsewhere)
    remember_external(paths, tmp_path / "gone")

    found = list_instances(config, paths)

    assert [entry.name for entry in found] == ["Alpha", "elsewhere", "zeta"]
    assert [entry.external for entry in found] == [False, True, False]
    assert found[2].state.loader_kind == "fabric"


def test_corrupt_instances_are_listed_with_the_problem(config, paths):
    broken = config.instances_dir / "broken" / ".modsmith"
    broken.mkdir(parents=True)
    (broken / "instance.json").write_text("{")
    (entry,) = list_instances(config, paths)
    assert entry.state is None
    assert "Corrupt" in entry.problem


def test_missing_instances_folder(config, paths, tmp_path):
    moved = dataclasses.replace(config, instances_dir=tmp_path / "nowhere")
    assert list_instances(moved, paths) == []


def test_open_instance(config):
    Instance.create(config.instances_dir / "pack", minecraft="1.21.1")
    instance, state = open_instance("pack", config)
    assert instance.path == config.instances_dir / "pack"
    assert state.minecraft == "1.21.1"
    with pytest.raises(AppError, match="no instance called 'other'"):
        open_instance("other", config)


def test_open_corrupt_instance(config):
    broken = config.instances_dir / "broken" / ".modsmith"
    broken.mkdir(parents=True)
    (broken / "instance.json").write_text("{")
    with pytest.raises(AppError, match="Corrupt"):
        open_instance("broken", config)


def test_external_list(paths, tmp_path):
    assert external_paths(paths) == []
    remember_external(paths, tmp_path / "a")
    remember_external(paths, tmp_path / "b")
    remember_external(paths, tmp_path / "a")
    assert external_paths(paths) == [tmp_path / "b", tmp_path / "a"]
    remember_external(paths, tmp_path / "b", keep=False)
    assert external_paths(paths) == [tmp_path / "a"]
    paths.external_file.write_text("[")
    with pytest.raises(AppError, match="corrupt"):
        external_paths(paths)


def test_resolve_uses_the_only_instance(config, paths):
    with pytest.raises(AppError, match="no instances yet"):
        resolve_instance(None, config, paths)
    Instance.create(config.instances_dir / "solo", minecraft="1.21.1")
    instance, _ = resolve_instance(None, config, paths)
    assert instance.path.name == "solo"
    Instance.create(config.instances_dir / "other", minecraft="1.21.1")
    with pytest.raises(AppError, match="Name the instance") as caught:
        resolve_instance(None, config, paths)
    assert caught.value.hint == "Your instances: other, solo."


def test_external_instances_are_found_by_name(config, paths, tmp_path):
    Instance.create(tmp_path / "far-away", minecraft="1.21.1")
    remember_external(paths, tmp_path / "far-away")
    instance, _ = resolve_instance("far-away", config, paths)
    assert instance.path == tmp_path / "far-away"


def test_split_target(config, paths):
    Instance.create(config.instances_dir / "solo", minecraft="1.21.1")
    instance, _, items = split_target(["solo", "sodium", "iris"], config, paths)
    assert (instance.path.name, items) == ("solo", ["sodium", "iris"])
    instance, _, items = split_target(["sodium", "iris"], config, paths)
    assert (instance.path.name, items) == ("solo", ["sodium", "iris"])
    Instance.create(config.instances_dir / "other", minecraft="1.21.1")
    with pytest.raises(AppError, match="Name the instance"):
        split_target(["sodium"], config, paths)
