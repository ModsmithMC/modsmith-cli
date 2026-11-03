import pytest
from modsmith.instances import Instance
from modsmith.platforms import Dependency

from tests.lib.builders import served_file, write_zip
from tests.lib.catalog import Catalog, project, release


@pytest.fixture
def survival(run, game, config):
    """An instance with the test loader, and nothing in it yet."""
    result = run("create", "survival", "-m", "1.21.1", "-l", "test-loader", "-y")
    assert result.exit_code == 0, result.output
    return Instance(config.instances_dir / "survival")


@pytest.fixture
def mods(server, catalogs):
    """Sodium, Iris that needs Sodium, and a library that Iris needs too."""

    def mod(slug, version="1", *deps, loader="test-loader", **options):
        data = f"{slug} {version}".encode()
        jar = served_file(server, f"{slug}-{version}.jar", data)
        return release(slug, version, *deps, loader=loader, files=(jar,), **options)

    needs = [Dependency("required", "sodium"), Dependency("required", "library")]
    catalog = Catalog(
        project("sodium", downloads=50),
        project("iris", downloads=40),
        project("library"),
        project("other"),
        releases=[
            mod("sodium"),
            mod("iris", "1", *needs),
            mod("library"),
            mod("other", loader="fabric"),
        ],
        changelogs={"sodium-1": "Faster chunks.\nFewer crashes."},
    )
    catalogs["modrinth"] = catalog
    catalog.mod = mod  # type: ignore[attr-defined]
    return catalog


def test_add_installs_dependencies(run, survival, mods):
    result = run("add", "survival", "iris", "-y")

    assert result.exit_code == 0, result.output
    assert "  + mods/iris-1.jar" in result.stdout
    assert "Sodium comes too, because a mod needs it" in result.stdout
    assert "Added to survival." in result.stdout
    assert (survival.path / "mods" / "sodium-1.jar").read_bytes() == b"sodium 1"
    assert {item.slug for item in survival.additions} == {"iris", "sodium", "library"}


def test_add_needs_the_instance_only_with_several(run, survival, mods):
    result = run("add", "sodium", "-y")
    assert result.exit_code == 0, result.output
    assert (survival.path / "mods" / "sodium-1.jar").exists()

    run("create", "second", "-m", "1.21.1", "-l", "test-loader", "-y")
    result = run("add", "iris", "-y")
    assert result.exit_code == 1
    assert "Name the instance to use." in result.stderr
    assert "survival" in result.stderr


def test_add_dry_run_and_unavailable(run, survival, mods):
    result = run("add", "survival", "sodium", "other", "--dry-run")
    assert result.exit_code == 0, result.output
    assert "  + mods/sodium-1.jar" in result.stdout
    assert "? other has no release for this instance" in result.stdout
    assert not (survival.path / "mods").exists() or not any(
        (survival.path / "mods").iterdir()
    )


def test_add_asks_first(run, survival, mods):
    result = run("add", "survival", "sodium")
    assert result.exit_code == 1
    assert "Run it again with --yes." in result.stderr

    result = run("add", "survival", "sodium", interactive=True, input="n\n")
    assert result.exit_code == 0
    assert "Nothing was changed." in result.stderr
    assert survival.additions == ()


def test_show_lists_where_files_came_from(run, survival, mods):
    run("add", "survival", "sodium", "-y")
    write_zip(
        survival.path / "mods" / "mine.jar",
        {"fabric.mod.json": '{"id": "mine", "name": "My Mod", "version": "3.0"}'},
    )
    run("disable", "survival", "mine.jar")

    result = run("show", "survival")

    assert result.exit_code == 0, result.output
    assert "survival: Minecraft 1.21.1 with test-loader 2" in result.stdout
    lines = result.stdout.splitlines()
    sodium = next(line for line in lines if "sodium-1.jar" in line)
    assert sodium.split()[:3] == ["Sodium", "added", "mods/sodium-1.jar"]
    mine = next(line for line in lines if "mine.jar" in line)
    assert mine.split() == [
        "My",
        "Mod",
        "3.0",
        "yours",
        "off",
        "mods/mine.jar.disabled",
    ]


def test_show_an_empty_instance(run, survival):
    result = run("show")
    assert result.exit_code == 0, result.output
    assert "It holds no mods" in result.stdout


def test_remove_takes_unneeded_dependencies(run, survival, mods):
    run("add", "survival", "iris", "sodium", "-y")

    result = run("remove", "survival", "iris", "--dry-run")
    assert result.exit_code == 0, result.output
    assert "  - mods/iris-1.jar" in result.stdout
    assert "  - mods/library-1.jar" in result.stdout
    assert "sodium" not in result.stdout
    assert len(survival.additions) == 3

    result = run("remove", "survival", "iris", "-y")
    assert result.exit_code == 0, result.output
    assert {item.slug for item in survival.additions} == {"sodium"}
    assert not (survival.path / "mods" / "library-1.jar").exists()


def test_remove_keeps_dependencies_and_changed_files(run, survival, mods):
    run("add", "survival", "iris", "-y")
    (survival.path / "mods" / "iris-1.jar").write_bytes(b"changed")

    result = run("remove", "survival", "iris", "--keep-deps", "-y")

    assert result.exit_code == 0, result.output
    assert "  ! mods/iris-1.jar" in result.stdout
    assert "1 of your changes kept." in result.stdout
    assert {item.slug for item in survival.additions} == {"sodium", "library"}


def test_remove_only_additions(run, survival, mods):
    result = run("remove", "survival", "sodium", "-y")
    assert result.exit_code == 1
    assert "Not added on its own: sodium." in result.stderr
    assert "modsmith disable" in result.stderr


def test_enable_and_disable(run, survival, mods):
    run("add", "survival", "sodium", "-y")
    jar = survival.path / "mods" / "sodium-1.jar"

    result = run("disable", "survival", "sodium")
    assert result.exit_code == 0, result.output
    assert "Turned off mods/sodium-1.jar." in result.stdout
    assert not jar.exists()
    assert jar.with_name("sodium-1.jar.disabled").exists()

    result = run("enable", "survival", "sodium-1.jar.disabled")
    assert result.exit_code == 0, result.output
    assert jar.exists()

    result = run("enable", "survival", "missing")
    assert result.exit_code == 1
    assert "Nothing in survival is called 'missing'." in result.stderr


def test_pin_and_unpin(run, survival, mods):
    run("add", "survival", "sodium", "-y")

    result = run("pin", "survival", "sodium")
    assert result.exit_code == 0, result.output
    assert "Sodium stays at its release." in result.stdout
    assert survival.additions[0].pinned

    result = run("unpin", "survival", "sodium")
    assert "Sodium follows updates again." in result.stdout
    assert not survival.additions[0].pinned

    result = run("pin", "survival", "nothing")
    assert result.exit_code == 1
    assert "cannot be pinned" in result.stderr


def test_adopt_recognises_files(run, survival, mods, catalogs):
    folder = survival.path / "mods"
    folder.mkdir()
    (folder / "sodium-1.jar").write_bytes(b"sodium 1")
    (folder / "unknown.jar").write_bytes(b"who knows")

    result = run("adopt", "survival", "-p", "modrinth")

    assert result.exit_code == 0, result.output
    assert "Sodium: mods/sodium-1.jar" in result.stdout
    assert "1 file can now be updated" in result.stdout
    assert [item.slug for item in survival.additions] == ["sodium"]

    result = run("adopt", "survival")
    assert result.exit_code == 0, result.output
    assert "Skipped curseforge:" in result.stderr
    assert "No unrecognised files" in result.stdout


def test_info_of_an_unknown_project(run, mods):
    result = run("info", "nothing-like-it")
    assert result.exit_code == 1
    assert "Modrinth has no project called 'nothing-like-it'." in result.stderr


def test_info(run, mods):
    result = run("info", "sodium")

    assert result.exit_code == 0, result.output
    assert "Sodium" in result.stdout
    assert "About sodium" in result.stdout
    assert "Downloads  50" in result.stdout
    assert "What changed in Sodium 1" in result.stdout
    assert "Fewer crashes." in result.stdout

    result = run("info", "sodium", "--minecraft", "1.7.10")
    assert "No releases match." in result.stdout


def test_loaders(run):
    result = run("loaders", "test-loader", "1.21.1")
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert "test-loader for Minecraft 1.21.1" in lines[0]
    assert lines[2].split() == ["2", "recommended"]
    assert "older versions" not in result.stdout

    assert "has no versions" in run("loaders", "test-loader", "0.30").stdout

    result = run("loaders", "optifine", "1.21.1")
    assert result.exit_code == 1
    assert "Modsmith cannot install 'optifine'." in result.stderr
    assert "fabric, quilt, forge or neoforge" in result.stderr


def test_loaders_lists_the_newest_unless_asked(run):
    result = run("loaders", "many-loader", "1.21.1")
    assert result.exit_code == 0, result.output
    assert "15 older versions; see them with --all." in result.stdout
    assert " 16 " not in f" {result.stdout} "

    result = run("loaders", "many-loader", "1.21.1", "--all")
    assert "older versions" not in result.stdout
    assert result.stdout.splitlines()[-1].split()[0] == "1"
    assert "beta" in result.stdout


def test_files_can_be_named_by_the_id_they_declare(run, survival):
    write_zip(
        survival.path / "mods" / "iris-fabric-1.11.4+mc1.21.1.jar",
        {"fabric.mod.json": '{"id": "iris", "name": "Iris Shaders", "version": "1"}'},
    )

    result = run("disable", "survival", "iris")
    assert result.exit_code == 0, result.output
    assert "Turned off mods/iris-fabric-1.11.4+mc1.21.1.jar." in result.stdout
    result = run("enable", "survival", "iris shaders")
    assert result.exit_code == 0, result.output


def test_add_says_what_is_there_already(run, survival, mods):
    run("add", "survival", "iris", "-y")

    result = run("add", "survival", "iris", "sodium")

    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert "  = Iris is already added" in lines
    assert "  = Sodium is already added" in lines
    assert lines[-1] == "Nothing to change."


def test_add_an_unknown_project(run, survival, mods):
    result = run("add", "survival", "sodium", "nothing-like-it")
    assert result.exit_code == 1
    assert "Modrinth has no project called 'nothing-like-it'." in result.stderr
    assert "modsmith search nothing-like-it --platform modrinth" in result.stderr
    assert "404" not in result.stderr


def test_add_an_unknown_curseforge_project(run, survival, catalogs):
    catalogs["curseforge"] = Catalog(name="curseforge")
    result = run("add", "survival", "curseforge:nothing-like-it")
    assert result.exit_code == 1
    assert "CurseForge has no project called 'nothing-like-it'." in result.stderr


def test_add_names_a_dependency_with_no_release(run, survival, mods):
    mods.projects.append(project("ghost", name="Ghost Lib"))
    mods.publish(mods.mod("ghost", loader="fabric"))
    mods.publish(mods.mod("haunted", "1", Dependency("required", "ghost")))
    mods.projects.append(project("haunted"))

    result = run("add", "survival", "haunted", "--dry-run")

    assert result.exit_code == 1
    assert "This cannot be installed, because of these problems." in result.stderr
    assert "Haunted 1 needs Ghost Lib, which has no release" in result.stderr
    assert "+ mods/haunted" not in result.stdout
