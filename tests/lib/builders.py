"""Build real pack archives, releases and game files for tests."""

import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

from modsmith.minecraft import GameDir
from modsmith.platforms import ReleaseFile


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def write_zip(path: Path, files: dict[str, bytes | str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return path


def pack_file(
    server, name: str, data: bytes, env: dict[str, str] | None = None, folder="mods"
) -> dict[str, Any]:
    """Describe a file of an mrpack whose download the local server serves."""
    entry: dict[str, Any] = {
        "path": f"{folder}/{name}",
        "hashes": {"sha1": sha1(data)},
        "downloads": [server.add_body(f"/files/{name}", data)],
        "fileSize": len(data),
    }
    if env:
        entry["env"] = env
    return entry


def write_mrpack(
    path: Path,
    files: list[dict[str, Any]] | tuple[()] = (),
    overrides: dict[str, bytes | str] | None = None,
    *,
    name: str = "Test Pack",
    version: str = "1.0",
    loader: dict[str, str] | None = None,
) -> Path:
    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "name": name,
        "versionId": version,
        "files": list(files),
        "dependencies": {
            "minecraft": "1.21.1",
            **({"test-loader": "1"} if loader is None else loader),
        },
    }
    content: dict[str, bytes | str] = {"modrinth.index.json": json.dumps(index)}
    content.update(overrides or {})
    return write_zip(path, content)


def write_curseforge_pack(path: Path, files: list[tuple[int, int]]) -> Path:
    manifest = {
        "manifestType": "minecraftModpack",
        "name": "Curse Pack",
        "version": "2.0",
        "overrides": "overrides",
        "minecraft": {
            "version": "1.21.1",
            "modLoaders": [{"id": "test-loader-1", "primary": True}],
        },
        "files": [
            {"projectID": project, "fileID": file, "required": True}
            for project, file in files
        ],
    }
    return write_zip(path, {"manifest.json": json.dumps(manifest)})


def served_file(server, name: str, data: bytes) -> ReleaseFile:
    """A release file that the local server serves."""
    url = server.add_body(f"/files/{name}", data)
    return ReleaseFile(name, (url,), {"sha1": sha1(data)}, len(data))


def install_vanilla(server, game: GameDir, version: str = "1.21.1") -> None:
    """Put a vanilla version's JSON in place, with a client jar to download."""
    jar = b"client " + version.encode()
    game.write_version(
        version,
        {
            "id": version,
            "downloads": {
                "client": {
                    "url": server.add_body(f"/client-{version}.jar", jar),
                    "sha1": sha1(jar),
                    "size": len(jar),
                }
            },
        },
    )
