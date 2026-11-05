"""Download CurseForge files whose authors turned off downloads through the API.

CurseForge's API gives no download link for these files, but they are still
served from its CDN, at an address made of the file's id and name. Modsmith
downloads them from there and checks them against the hashes CurseForge lists,
so a pack installs in one go, as it would in CurseForge's own app.
"""

import dataclasses
from urllib.parse import quote

from modsmith.instances import Plan
from modsmith.packs import Modpack, PackEntry

CURSEFORGE_CDN = "https://edge.forgecdn.net/files"
# CurseForge's CDN splits a file id into a folder of thousands and the rest.
SPLIT = 1000


def cdn_url(base: str, file_id: int, file_name: str) -> str:
    """Return where CurseForge's CDN serves a file.

    Args:
        base: The CDN's files address, such as `CURSEFORGE_CDN`.
        file_id: The file's id.
        file_name: The file's name, as CurseForge lists it.

    Returns:
        The address, such as ``.../files/5101/366/sodium.jar`` for file 5101366.
    """
    folder, rest = divmod(file_id, SPLIT)
    return f"{base.rstrip('/')}/{folder}/{rest}/{quote(file_name)}"


def from_cdn(entry: PackEntry, base: str) -> PackEntry:
    """Give a CurseForge file with no download link its address on the CDN.

    Entries that already have a download, come from elsewhere, or whose file
    CurseForge no longer lists are returned unchanged.
    """
    ref = entry.ref
    if entry.urls or entry.path is None or ref is None or ref.platform != "curseforge":
        return entry
    if not ref.file_id.isdigit():
        return entry
    name = entry.path.rsplit("/", 1)[-1]
    return dataclasses.replace(entry, urls=(cdn_url(base, int(ref.file_id), name),))


def pack_from_cdn(pack: Modpack, base: str) -> Modpack:
    """Return the pack with its CurseForge files all downloadable."""
    return pack.with_entries(tuple(from_cdn(entry, base) for entry in pack.entries))


def plan_from_cdn(plan: Plan, base: str) -> Plan:
    """Return the plan with its CurseForge files all downloadable."""
    additions = tuple(
        dataclasses.replace(item, entry=from_cdn(item.entry, base))
        for item in plan.additions
    )
    return dataclasses.replace(plan, additions=additions)
