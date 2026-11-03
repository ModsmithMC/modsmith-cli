from modsmith.instances import Instance

from modsmith_app import __version__
from modsmith_app.core.registry import remember_external
from tests.lib.catalog import Catalog, project


def test_version(run):
    result = run("--version")
    assert result.exit_code == 0
    assert result.stdout.strip() == f"modsmith {__version__}"


def test_no_arguments_shows_help(run):
    result = run()
    assert "Usage: modsmith" in result.output
    for command in ("list", "search", "config"):
        assert command in result.output


def test_list_with_no_instances(run):
    result = run("list")
    assert result.exit_code == 0
    assert "No instances yet." in result.stdout


def test_list_shows_versions_loaders_and_packs(run, config, paths, tmp_path):
    Instance.create(
        config.instances_dir / "survival",
        minecraft="1.21.1",
        loader="fabric",
        loader_version="0.16.10",
    )
    Instance.create(config.instances_dir / "plain", minecraft="1.20.1")
    elsewhere = tmp_path / "old-world"
    Instance.create(elsewhere, minecraft="1.12.2", loader="forge")
    remember_external(paths, elsewhere)

    result = run("list")

    assert result.exit_code == 0
    lines = result.stdout.splitlines()
    survival = next(line for line in lines if line.startswith("survival"))
    assert "1.21.1" in survival
    assert "fabric 0.16.10" in survival
    plain = next(line for line in lines if line.startswith("plain"))
    assert "vanilla" in plain
    assert "old-world" in result.stdout


def test_list_uses_the_instances_folder_option(run, tmp_path):
    Instance.create(tmp_path / "other" / "solo", minecraft="1.21.1")
    result = run("--instances-dir", str(tmp_path / "other"), "list")
    assert "solo" in result.stdout


def test_config_show_set_get_and_unset(run, paths):
    result = run("config")
    assert result.exit_code == 0
    assert "default_platform" in result.stdout
    assert "default" in result.stdout

    assert run("config", "set", "default_platform", "curseforge").exit_code == 0
    assert run("config", "get", "default_platform").stdout.strip() == "curseforge"
    row = next(line for line in run("config").stdout.splitlines() if "platform" in line)
    assert row.split()[-2:] == ["config", "file"]

    assert run("config", "unset", "default_platform").exit_code == 0
    assert run("config", "get", "default_platform").stdout.strip() == "modrinth"


def test_config_hides_the_api_key(run):
    run("config", "set", "curseforge_api_key", "very-secret")
    assert "very-secret" not in run("config").stdout
    assert run("config", "get", "curseforge_api_key").stdout.strip() == "set (hidden)"


def test_config_reports_command_line_and_environment(run, monkeypatch, tmp_path):
    result = run("--game-dir", str(tmp_path / "mc"), "config")
    assert "command line" in result.stdout

    monkeypatch.setenv("MODSMITH_INSTANCES_DIR", str(tmp_path / "env"))
    result = run("config", "set", "instances_dir", str(tmp_path / "file"))
    assert result.exit_code == 0
    assert "MODSMITH_INSTANCES_DIR is set" in result.stderr


def test_config_errors_are_short(run):
    result = run("config", "set", "allow_prereleases", "maybe")
    assert result.exit_code == 1
    assert "Error: 'maybe' is not true or false." in result.stderr
    assert "Traceback" not in result.stderr

    result = run("config", "get", "colour")
    assert result.exit_code == 1
    assert "Settings: instances_dir" in result.stderr


def test_config_path_works_with_a_broken_file(run, paths):
    paths.config_file.parent.mkdir(parents=True)
    paths.config_file.write_text("broken = = toml")
    result = run("config", "path")
    assert result.exit_code == 0
    assert result.stdout.strip() == str(paths.config_file)
    assert run("list").exit_code == 1


def test_search_uses_the_default_platform(run, catalogs):
    catalogs["modrinth"] = Catalog(
        project("sodium", downloads=12_345_678),
        project("sodium-extra", downloads=950),
        project("sodium-pack", kind="modpack"),
    )
    result = run("search", "sodium")
    assert result.exit_code == 0
    assert "modrinth:sodium " in result.stdout
    assert "12.3M" in result.stdout
    assert "950" in result.stdout
    assert "sodium-pack" not in result.stdout

    result = run("search", "sodium", "--type", "modpack")
    assert "modrinth:sodium-pack" in result.stdout


def test_search_says_when_there_is_more(run, catalogs):
    catalogs["modrinth"] = Catalog(*(project(f"mod-{index}") for index in range(5)))
    result = run("search", "mod", "--limit", "2")
    assert result.stdout.count("modrinth:mod-") == 2
    assert "Showing 2 of 5." in result.stderr


def test_search_with_no_results(run):
    result = run("search", "nothing")
    assert result.exit_code == 0
    assert "Nothing found on modrinth." in result.stdout


def test_curseforge_needs_a_key(run):
    result = run("search", "jei", "--platform", "curseforge")
    assert result.exit_code == 1
    assert "CurseForge needs an API key." in result.stderr
    assert "modsmith config set curseforge_api_key" in result.stderr


def test_searching_everywhere_skips_platforms_it_cannot_use(run, catalogs):
    catalogs["modrinth"] = Catalog(project("jei"))
    result = run("search", "jei", "--platform", "all")
    assert result.exit_code == 0
    assert "Modrinth" in result.stdout
    assert "modrinth:jei" in result.stdout
    assert "Skipped curseforge" in result.stderr


def test_searching_both_platforms(run, catalogs, monkeypatch):
    monkeypatch.setenv("CURSEFORGE_API_KEY", "test-key")
    catalogs["modrinth"] = Catalog(project("jei"))
    catalogs["curseforge"] = Catalog(project("jei", platform="curseforge"))
    result = run("search", "jei", "-p", "all")
    assert "modrinth:jei" in result.stdout
    assert "curseforge:jei" in result.stdout
