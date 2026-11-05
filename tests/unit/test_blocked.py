from modsmith.packs import FileRef, PackEntry

from modsmith_cli.core.blocked import CURSEFORGE_CDN, cdn_url, from_cdn


def test_cdn_address():
    assert (
        cdn_url(CURSEFORGE_CDN, 5101366, "Sodium 1.0+mc.jar")
        == "https://edge.forgecdn.net/files/5101/366/Sodium%201.0%2Bmc.jar"
    )
    assert cdn_url("https://cdn.test/files/", 999, "a.jar").endswith(
        "/files/0/999/a.jar"
    )


def test_only_curseforge_files_with_no_link_change():
    blocked = PackEntry(
        path="mods/a.jar", ref=FileRef("curseforge", "1", "4000017"), manual_url="x"
    )
    assert from_cdn(blocked, CURSEFORGE_CDN).urls == (
        "https://edge.forgecdn.net/files/4000/17/a.jar",
    )
    unchanged = [
        PackEntry(path="mods/b.jar", urls=("https://x/b.jar",), ref=blocked.ref),
        PackEntry(path="mods/c.jar", ref=FileRef("modrinth", "c", "123")),
        PackEntry(ref=FileRef("curseforge", "1", "7")),  # no longer listed
        PackEntry(path="mods/d.jar"),
    ]
    for entry in unchanged:
        assert from_cdn(entry, CURSEFORGE_CDN) is entry
