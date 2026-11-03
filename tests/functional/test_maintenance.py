import json

import pytest
from modsmith.instances import Instance

from modsmith_app.core.records import read_record
from tests.lib.builders import pack_file, served_file, write_mrpack
from tests.lib.catalog import project, release

OPTIONAL = {"client": "optional", "server": "optional"}


def profiles(game) -> dict:
    data = json.loads(
        (game.path / "launcher_profiles.json").read_text(encoding="utf-8")
    )
    return data["profiles"]


def add_profile(game, key, **fields) -> None:
    path = game.path / "launcher_profiles.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["profiles"][key] = {"type": "custom", **fields}
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def packs(server, catalogs, tmp_path):
    """Publish releases of a modpack called Pack on the test catalogue."""
    catalog = catalogs["modrinth"]
    catalog.projects.append(project("pack", "modpack"))

    def publish(version, mods, *, minecraft="1.21.1", loader="1"):
        files = [pack_file(server, name, data, env) for name, data, env in mods]
        path = write_mrpack(
            tmp_path / "published" / f"pack-{version}.mrpack",
            files,
            name="Pack",
            version=version,
            loader={"test-loader": loader},
            minecraft=minecraft,
        )
        item = served_file(server, path.name, path.read_bytes())
        catalog.publish(release("pack", version, loader="test-loader", files=(item,)))
        catalog.changelogs[f"pack-{version}"] = f"Notes for {version}.\nMore."
        return path

    return publish


@pytest.fixture
def mods(server, catalogs):
    """Publish releases of mods for the test loader."""
    catalog = catalogs["modrinth"]

    def publish(slug, version="1"):
        if not any(item.id == slug for item in catalog.projects):
            catalog.projects.append(project(slug))
        jar = served_file(server, f"{slug}-{version}.jar", f"{slug} {version}".encode())
        catalog.publish(release(slug, version, loader="test-loader", files=(jar,)))
        catalog.changelogs[f"{slug}-{version}"] = f"{slug} {version} is faster."

    return publish


@pytest.fixture
def survival(run, game, config):
    result = run("create", "survival", "-m", "1.21.1", "-l", "test-loader", "-y")
    assert result.exit_code == 0, result.output
    return Instance(config.instances_dir / "survival")


def test_update_the_pack(run, game, config, packs):
    packs("1", [("a.jar", b"a1", None)])
    assert run("install", "pack", "-y").exit_code == 0
    folder = config.instances_dir / "pack"
    packs("2", [("b.jar", b"b2", None)])

    result = run("update", "pack", "-y")

    assert result.exit_code == 0, result.output
    assert "What changed in Pack 2" in result.stdout
    assert "Notes for 2." in result.stdout
    assert "Update Pack 1 to Pack 2" in result.stdout
    assert "  + mods/b.jar" in result.stdout
    assert "  - mods/a.jar" in result.stdout
    assert "Updated pack." in result.stdout
    assert (folder / "mods" / "b.jar").read_bytes() == b"b2"
    assert not (folder / "mods" / "a.jar").exists()
    assert read_record(folder).source.release_id == "pack-2"

    result = run("update", "pack", "-y")
    assert result.exit_code == 0, result.output
    assert "Pack is up to date." in result.stdout
    assert "Everything in pack is up to date." in result.stdout


def test_update_keeps_optional_choices(run, config, game, packs):
    mods = [("a.jar", b"a", None), ("extra.jar", b"x", OPTIONAL)]
    packs("1", mods)
    assert run("install", "pack", "--optional", "extra", "-y").exit_code == 0
    folder = config.instances_dir / "pack"
    packs("2", [*mods, ("new.jar", b"n", None)])

    result = run("update", "-y")

    assert result.exit_code == 0, result.output
    assert (folder / "mods" / "extra.jar").exists()
    assert (folder / "mods" / "new.jar").exists()
    assert read_record(folder).optional == ("mods/extra.jar",)

    result = run("update", "--all-optional", "-y")
    assert result.exit_code == 0, result.output
    packs("3", [("a.jar", b"a", None), ("other.jar", b"o", OPTIONAL)])
    result = run("update", "-y")
    assert result.exit_code == 0, result.output
    assert "1 optional file you chose is not in this release." in result.stderr
    assert not (folder / "mods" / "other.jar").exists()


def test_update_a_pack_that_moves_to_a_new_game(run, game, config, packs, mods):
    packs("1", [("a.jar", b"a", None)])
    run("install", "pack", "-y")
    mods("sodium")
    run("add", "pack", "sodium", "-y")
    packs("2", [("a.jar", b"a", None)], minecraft="1.21.4", loader="2")
    mods("sodium", "2")

    result = run("update", "pack", "--dry-run")
    assert result.exit_code == 0, result.output
    assert (
        "It moves from Minecraft 1.21.1 with test-loader 1 to "
        "Minecraft 1.21.4 with test-loader 2." in result.stdout
    )
    assert "the next time you run modsmith update" in result.stdout
    assert profiles(game)["modsmith-pack"]["lastVersionId"] == "test-loader-1-1.21.1"

    assert run("update", "pack", "-y", launcher_open=True).exit_code == 1
    result = run("update", "pack", "-y")
    assert result.exit_code == 0, result.output
    assert profiles(game)["modsmith-pack"]["lastVersionId"] == "test-loader-2-1.21.4"
    assert Instance(config.instances_dir / "pack").state.minecraft == "1.21.4"


def test_update_a_pack_from_a_file(run, config, game, server, tmp_path):
    first = write_mrpack(tmp_path / "one.mrpack", [pack_file(server, "a.jar", b"a")])
    run("install", str(first), "-y")

    result = run("update", "test-pack", "--pack-only")
    assert result.exit_code == 0, result.output
    assert "Its pack came from a file. Update it with --file" in result.stdout

    second = write_mrpack(
        tmp_path / "two.mrpack", [pack_file(server, "b.jar", b"b")], version="2.0"
    )
    result = run("update", "test-pack", "--file", str(second), "-y")
    assert result.exit_code == 0, result.output
    assert (config.instances_dir / "test-pack" / "mods" / "b.jar").exists()
    assert read_record(config.instances_dir / "test-pack").source.file == str(
        second.resolve()
    )


def test_update_additions(run, survival, mods):
    mods("sodium")
    mods("lithium")
    run("add", "survival", "sodium", "lithium", "-y")
    run("pin", "survival", "lithium")
    mods("sodium", "2")
    mods("lithium", "2")

    result = run("update", "survival", "--dry-run")
    assert result.exit_code == 0, result.output
    assert "It has no pack." in result.stdout
    assert "What changed in Sodium 2" in result.stdout
    assert "sodium 2 is faster." in result.stdout
    assert "lithium-2" not in result.stdout
    assert "Lithium 2" not in result.stdout
    assert "  + mods/sodium-2.jar" in result.stdout
    assert (survival.path / "mods" / "sodium-1.jar").exists()

    result = run("update", "survival", "-y")
    assert result.exit_code == 0, result.output
    assert (survival.path / "mods" / "sodium-2.jar").exists()
    assert not (survival.path / "mods" / "sodium-1.jar").exists()
    assert (survival.path / "mods" / "lithium-1.jar").exists()

    result = run("update", "survival")
    assert "Everything in survival is up to date." in result.stdout


def test_update_only_the_pack_or_the_additions(run, config, game, packs, mods):
    packs("1", [("a.jar", b"a", None)])
    run("install", "pack", "-y")
    mods("sodium")
    run("add", "pack", "sodium", "-y")
    packs("2", [("b.jar", b"b", None)])
    mods("sodium", "2")

    result = run("update", "pack", "--additions-only", "--dry-run")
    assert "mods/b.jar" not in result.stdout
    assert "mods/sodium-2.jar" in result.stdout

    result = run("update", "pack", "--pack-only", "--dry-run")
    assert "mods/b.jar" in result.stdout
    assert "mods/sodium-2.jar" not in result.stdout


def fabric_install(game, folder, name="My Fabric", key="abc123"):
    """Set up an installation the way the official launcher leaves one."""
    game.write_version("1.21.1", {"id": "1.21.1"})
    loader_id = "fabric-loader-0.16.10-1.21.1"
    game.write_version(
        loader_id,
        {
            "id": loader_id,
            "inheritsFrom": "1.21.1",
            "libraries": [
                {"name": "org.ow2.asm:asm:9.7"},
                {"name": "net.fabricmc:fabric-loader:0.16.10"},
            ],
        },
    )
    add_profile(game, key, name=name, lastVersionId=loader_id, gameDir=str(folder))


def test_import_an_installation(run, game, config, tmp_path, mods):
    mods("sodium")
    folder = tmp_path / "elsewhere" / "fabric-world"
    (folder / "mods").mkdir(parents=True)
    (folder / "mods" / "sodium-1.jar").write_bytes(b"sodium 1")
    (folder / "mods" / "mine.jar").write_bytes(b"mine")
    fabric_install(game, folder)

    result = run("import", "my fabric", "--dry-run")
    assert result.exit_code == 0, result.output
    assert "Minecraft 1.21.1 with Fabric 0.16.10" in result.stdout
    assert Instance(folder).state is None

    result = run("import", "My Fabric", "-y")

    assert result.exit_code == 0, result.output
    state = Instance(folder).state
    assert (state.minecraft, state.loader_kind, state.loader_version) == (
        "1.21.1",
        "fabric",
        "0.16.10",
    )
    assert [item.slug for item in state.additions] == ["sodium"]
    assert read_record(folder).profile == "abc123"
    assert "fabric-world is now an instance." in result.stdout
    listed = run("list").stdout
    assert "fabric-world" in listed
    assert run("show", "fabric-world").exit_code == 0

    result = run("import", "abc123", "-y")
    assert result.exit_code == 1
    assert "is already an instance" in result.stderr


def test_import_needs_its_own_folder_and_version(run, game, tmp_path):
    add_profile(game, "default", name="", lastVersionId="latest-release")
    add_profile(game, "plain", name="Plain", lastVersionId="1.21.1")
    add_profile(
        game, "nover", name="No Version", lastVersionId="1.20", gameDir=str(tmp_path)
    )
    add_profile(
        game, "latest", name="Latest", lastVersionId="latest-snapshot", gameDir="x"
    )

    result = run("import", "nothing")
    assert result.exit_code == 1
    assert "has no installation called 'nothing'" in result.stderr
    assert "Plain" in result.stderr

    assert "uses the game directory itself" in run("import", "plain").stderr
    assert "starts the newest Minecraft" in run("import", "latest").stderr
    assert "Version 1.20 is not installed" in run("import", "no version").stderr


def test_move_and_rename(run, game, config, survival, tmp_path):
    result = run("move", "survival", "creative")

    assert result.exit_code == 0, result.output
    renamed = config.instances_dir / "creative"
    assert not survival.path.exists()
    assert Instance(renamed).state is not None
    assert profiles(game)["modsmith-survival"]["gameDir"] == str(renamed.resolve())

    away = tmp_path / "games" / "creative"
    result = run("move", "creative", str(away))
    assert result.exit_code == 0, result.output
    assert profiles(game)["modsmith-survival"]["gameDir"] == str(away.resolve())
    assert "creative" in run("list").stdout
    assert run("show", "creative").exit_code == 0

    result = run("move", "creative", str(tmp_path))
    assert result.exit_code == 1
    assert "already exists" in result.stderr
    assert "cannot be an instance name" in run("move", "creative", "no?pe").stderr


def test_renaming_an_imported_instance_keeps_it_in_place(run, game, tmp_path):
    folder = tmp_path / "games" / "fabric-world"
    folder.mkdir(parents=True)
    fabric_install(game, folder)
    run("import", "My Fabric", "-y")

    result = run("move", "fabric-world", "renamed")

    assert result.exit_code == 0, result.output
    assert "Moved fabric-world to renamed." in result.stdout
    assert (tmp_path / "games" / "renamed" / ".modsmith").is_dir()
    assert profiles(game)["abc123"]["gameDir"] == str(tmp_path / "games" / "renamed")
    assert run("show", "renamed").exit_code == 0


def test_delete(run, game, config, survival):
    (survival.path / "saves" / "World").mkdir(parents=True)
    (survival.path / "saves" / "World" / "level.dat").write_bytes(b"")

    result = run("delete", "survival", "-y")
    assert result.exit_code == 1
    assert "Add --force as well." in result.stderr

    assert run("delete", "survival").exit_code == 1

    result = run("delete", "survival", interactive=True, input="nope\n")
    assert "with its 1 world" in result.stdout
    assert "Nothing was changed." in result.stderr
    assert survival.path.exists()

    result = run("delete", "survival", "-y", "--force", launcher_open=True)
    assert "Close the official launcher first." in result.stderr

    result = run("delete", "survival", interactive=True, input="survival\n")
    assert result.exit_code == 0, result.output
    assert not survival.path.exists()
    assert "modsmith-survival" not in profiles(game)
    assert "Deleted survival." in result.stdout


def test_delete_an_imported_instance(run, game, config, tmp_path):
    folder = tmp_path / "fabric-world"
    folder.mkdir()
    fabric_install(game, folder)
    run("import", "My Fabric", "-y")

    result = run("delete", "fabric-world", "-y", "--force")

    assert result.exit_code == 0, result.output
    assert not folder.exists()
    assert "abc123" not in profiles(game)
    assert "fabric-world" not in run("list").stdout
