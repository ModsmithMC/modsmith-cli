import pytest

from modsmith_app.core.errors import AppError
from modsmith_app.core.refs import LocalPack, ProjectRef, parse_pack, parse_project


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("sodium", ProjectRef("modrinth", "sodium")),
        ("  sodium ", ProjectRef("modrinth", "sodium")),
        ("curseforge:238222", ProjectRef("curseforge", "238222")),
        ("CurseForge:jei", ProjectRef("curseforge", "jei")),
        ("modrinth:iris", ProjectRef("modrinth", "iris")),
        ("https://modrinth.com/mod/sodium", ProjectRef("modrinth", "sodium")),
        ("https://modrinth.com/shader/glow?x=1", ProjectRef("modrinth", "glow")),
        (
            "https://www.curseforge.com/minecraft/mc-mods/jei/files",
            ProjectRef("curseforge", "jei"),
        ),
    ],
)
def test_projects(text, expected):
    assert parse_project(text, "modrinth") == expected


def test_default_platform_applies_to_bare_names():
    assert parse_project("jei", "curseforge") == ProjectRef("curseforge", "jei")
    assert str(ProjectRef("curseforge", "jei")) == "curseforge:jei"


@pytest.mark.parametrize("text", ["planet:sodium", "modrinth:", ""])
def test_bad_projects(text):
    with pytest.raises(AppError):
        parse_project(text, "modrinth")


def test_packs(tmp_path):
    pack = tmp_path / "Pack.MRPACK"
    pack.write_bytes(b"")
    assert parse_pack(str(pack), "modrinth") == LocalPack(pack)
    assert parse_pack("fabulously-optimized", "modrinth") == ProjectRef(
        "modrinth", "fabulously-optimized"
    )
    with pytest.raises(AppError, match="does not exist"):
        parse_pack(str(tmp_path / "missing.zip"), "modrinth")
