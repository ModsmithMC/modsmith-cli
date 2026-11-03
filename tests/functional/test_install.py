import json

from modsmith.instances import Instance

from modsmith_app.core.records import PackSource, read_record
from tests.lib.builders import (
    install_vanilla,
    pack_file,
    served_file,
    write_curseforge_pack,
    write_mrpack,
)
from tests.lib.catalog import Catalog, project, release
from tests.lib.loaders import TestLoader


def profiles(game) -> dict:
    data = json.loads(
        (game.path / "launcher_profiles.json").read_text(encoding="utf-8")
    )
    return data["profiles"]


def simple_pack(server, tmp_path, **options):
    files = [
        pack_file(server, "a.jar", b"mod a"),
        pack_file(
            server, "extra.jar", b"extra", {"client": "optional", "server": "optional"}
        ),
        pack_file(
            server, "shiny.jar", b"shiny", {"client": "optional", "server": "optional"}
        ),
    ]
    return write_mrpack(
        tmp_path / "packs" / "pack.mrpack",
        files,
        {"overrides/config/a.toml": "a=1"},
        **options,
    )


def test_install_a_local_pack(run, server, game, config, tmp_path):
    path = simple_pack(server, tmp_path)

    result = run("install", str(path), "--yes")

    assert result.exit_code == 0, result.output
    assert "Install Test Pack 1.0 as test-pack" in result.stdout
    assert "  + mods/a.jar" in result.stdout
    assert "Minecraft 1.21.1 with test-loader 1" in result.stdout
    folder = config.instances_dir / "test-pack"
    assert (folder / "mods" / "a.jar").read_bytes() == b"mod a"
    assert (folder / "config" / "a.toml").read_text() == "a=1"
    assert not (folder / "mods" / "extra.jar").exists()
    assert "Left out 2 optional files" in result.stderr
    profile = profiles(game)["modsmith-test-pack"]
    assert profile["name"] == "Test Pack"
    assert profile["lastVersionId"] == "test-loader-1-1.21.1"
    assert profile["gameDir"] == str(folder.resolve())
    record = read_record(folder)
    assert record.profile == "modsmith-test-pack"
    assert record.source == PackSource(file=str(path.resolve()))
    assert "Installed Test Pack as test-pack" in result.stdout


def test_dry_run_changes_nothing(run, server, game, config, tmp_path):
    result = run("install", str(simple_pack(server, tmp_path)), "--dry-run")
    assert result.exit_code == 0
    assert "  + mods/a.jar" in result.stdout
    assert not (config.instances_dir / "test-pack").exists()
    assert profiles(game) == {}


def test_confirmation(run, server, game, config, tmp_path):
    path = str(simple_pack(server, tmp_path))
    result = run("install", path)
    assert result.exit_code == 1
    assert "Run it again with --yes." in result.stderr

    result = run("install", path, interactive=True, input="\nn\n")
    assert result.exit_code == 0
    assert "Nothing was changed." in result.stderr
    assert not (config.instances_dir / "test-pack").exists()

    result = run("install", path, interactive=True, input="\ny\n")
    assert result.exit_code == 0, result.output
    assert (config.instances_dir / "test-pack" / "mods" / "a.jar").exists()


def test_the_launcher_must_be_closed_and_set_up(run, server, game, tmp_path):
    path = str(simple_pack(server, tmp_path))
    result = run("install", path, "--yes", launcher_open=True)
    assert result.exit_code == 1
    assert "Close the official launcher first." in result.stderr

    (game.path / "launcher_profiles.json").unlink()
    result = run("install", path, "--yes")
    assert result.exit_code == 1
    assert "has not been set up" in result.stderr


def test_names_must_be_free_and_valid(run, server, game, config, tmp_path):
    path = str(simple_pack(server, tmp_path))
    assert run("install", path, "--yes").exit_code == 0
    result = run("install", path, "--yes")
    assert result.exit_code == 1
    assert "already an instance called 'test-pack'" in result.stderr
    assert run("install", path, "--yes", "--name", "second").exit_code == 0
    result = run("install", path, "--yes", "--name", "bad/name")
    assert "cannot be an instance name" in result.stderr


def test_choosing_optional_files(run, server, game, config, tmp_path):
    path = str(simple_pack(server, tmp_path))
    result = run("install", path, "--yes", "--optional", "SHINY", "--name", "one")
    assert result.exit_code == 0, result.output
    folder = config.instances_dir / "one"
    assert (folder / "mods" / "shiny.jar").exists()
    assert not (folder / "mods" / "extra.jar").exists()
    assert read_record(folder).optional == ("mods/shiny.jar",)

    run("install", path, "--yes", "--all-optional", "--name", "two")
    assert (config.instances_dir / "two" / "mods" / "extra.jar").exists()

    result = run("install", path, "--name", "three", interactive=True, input="2\ny\n")
    assert result.exit_code == 0, result.output
    assert "  2. mods/shiny.jar" in result.stdout
    assert read_record(config.instances_dir / "three").optional == ("mods/shiny.jar",)

    result = run("install", path, "--yes", "--optional", "nothing", "--name", "four")
    assert result.exit_code == 1
    assert "The optional files are: mods/extra.jar, mods/shiny.jar." in result.stderr

    result = run("install", path, "--name", "five", interactive=True, input="9\n")
    assert "Choose numbers from 1 to 2." in result.stderr


def test_install_a_pack_from_a_platform(run, server, game, config, tmp_path, catalogs):
    archive = simple_pack(server, tmp_path, version="3.1").read_bytes()
    catalogs["modrinth"] = Catalog(
        project("test-pack", kind="modpack", icon_url=None),
        project("a-mod"),
        releases=[
            release(
                "test-pack", "3.1", files=(served_file(server, "pack.mrpack", archive),)
            ),
        ],
    )

    result = run("install", "test-pack", "--yes")

    assert result.exit_code == 0, result.output
    record = read_record(config.instances_dir / "test-pack")
    assert record.source == PackSource("modrinth", "test-pack", "test-pack-3.1")

    result = run("install", "a-mod", "--yes")
    assert result.exit_code == 1
    assert "is a mod, not a modpack" in result.stderr
    assert "modsmith add <instance> modrinth:a-mod" in result.stderr


def test_a_pack_with_no_release(run, game, catalogs):
    catalogs["modrinth"] = Catalog(project("empty", kind="modpack"))
    result = run("install", "empty", "--yes")
    assert result.exit_code == 1
    assert "has no release to install" in result.stderr


def test_curseforge_files_to_download_by_hand(run, game, tmp_path, catalogs):
    catalogs["curseforge"] = Catalog(name="curseforge")
    path = write_curseforge_pack(tmp_path / "cf.zip", [(10, 20)])
    result = run("install", str(path), "--yes")
    assert result.exit_code == 1
    assert "1 files cannot be downloaded automatically." in result.stderr
    assert "curseforge file 20" in result.stderr
    assert "--from <folder>" in result.stderr


def test_a_vanilla_pack_installs_plain_minecraft(run, server, game, config, tmp_path):
    install_vanilla(server, game)
    path = write_mrpack(
        tmp_path / "vanilla.mrpack",
        overrides={"overrides/resourcepacks/look.zip": "x"},
        loader={},
    )
    result = run("install", str(path), "--yes")
    assert result.exit_code == 0, result.output
    assert "with no mod loader" in result.stdout
    assert profiles(game)["modsmith-test-pack"]["lastVersionId"] == "1.21.1"
    assert Instance(config.instances_dir / "test-pack").state.loader_kind is None


def test_create_with_the_recommended_loader(run, game, config):
    result = run(
        "create", "modded", "--minecraft", "1.21.1", "--loader", "test-loader", "-y"
    )
    assert result.exit_code == 0, result.output
    assert "Minecraft 1.21.1 with test-loader 2" in result.stdout
    state = Instance(config.instances_dir / "modded").state
    assert (state.minecraft, state.loader_kind, state.loader_version) == (
        "1.21.1",
        "test-loader",
        TestLoader.published[0],
    )
    profile = profiles(game)["modsmith-modded"]
    assert (profile["name"], profile["lastVersionId"]) == (
        "modded",
        "test-loader-2-1.21.1",
    )
    assert read_record(config.instances_dir / "modded").profile == "modsmith-modded"


def test_create_with_a_chosen_loader_version_or_none(run, server, game, config):
    result = run(
        "create",
        "older",
        "-m",
        "1.21.1",
        "-l",
        "test-loader",
        "--loader-version",
        "1",
        "-y",
    )
    assert result.exit_code == 0, result.output
    assert Instance(config.instances_dir / "older").state.loader_version == "1"

    install_vanilla(server, game)
    result = run("create", "plain", "-m", "1.21.1", "-y")
    assert result.exit_code == 0, result.output
    assert profiles(game)["modsmith-plain"]["lastVersionId"] == "1.21.1"

    result = run("create", "odd", "-m", "1.21.1", "--loader-version", "1", "-y")
    assert "--loader-version needs --loader too." in result.stderr


def test_create_dry_run(run, game, config):
    result = run("create", "later", "-m", "1.21.1", "-l", "test-loader", "--dry-run")
    assert result.exit_code == 0
    assert "Create later" in result.stdout
    assert not (config.instances_dir / "later").exists()


def test_platform_packs_bring_their_icon(run, server, game, tmp_path, catalogs):
    from tests.lib.server import Reply

    png = b"\x89PNG\r\n\x1a\nicon"
    icon = server.add("/icon.png", Reply(png, headers={"Content-Type": "image/png"}))
    webp = server.add(
        "/icon.webp", Reply(b"RIFF", headers={"Content-Type": "image/webp"})
    )
    archive = simple_pack(server, tmp_path).read_bytes()
    catalogs["modrinth"] = Catalog(
        project("with-icon", kind="modpack", icon_url=icon),
        project("other-icon", kind="modpack", icon_url=webp),
        releases=[
            release("with-icon", files=(served_file(server, "one.mrpack", archive),)),
            release("other-icon", files=(served_file(server, "two.mrpack", archive),)),
        ],
    )
    assert run("install", "with-icon", "--yes", "--name", "one").exit_code == 0
    assert run("install", "other-icon", "--yes", "--name", "two").exit_code == 0
    saved = profiles(game)
    assert saved["modsmith-one"]["icon"].startswith("data:image/png;base64,")
    assert "icon" not in saved["modsmith-two"]
