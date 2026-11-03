import pytest
from modsmith.errors import (
    Cancelled,
    DownloadError,
    LockedError,
    NetworkError,
    PlatformError,
    UnresolvedEntriesError,
)
from modsmith.packs import FileRef, PackEntry

from modsmith_cli.core.errors import AppError
from modsmith_cli.errors import describe


@pytest.mark.parametrize(
    ("error", "hint"),
    [
        (NetworkError("GET x failed: timed out"), "internet connection"),
        (NetworkError("GET x returned 503", 503), "busy"),
        (NetworkError("GET x returned 429", 429), "busy"),
        (LockedError("locked"), "Another Modsmith"),
        (Cancelled(), "Nothing was changed"),
    ],
)
def test_hints(error, hint):
    assert hint in describe(error).hint


def test_errors_without_a_hint():
    found = describe(NetworkError("GET x returned 404", 404))
    assert (found.message, found.hint) == ("GET x returned 404", None)
    assert describe(PlatformError("no such project")).hint is None
    found = describe(AppError("bad", hint="fix it"))
    assert (found.message, found.hint) == ("bad", "fix it")


def test_failed_downloads_name_every_file():
    error = DownloadError(
        "2 of 9 downloads failed",
        [
            "Failed to download sodium.jar: 404",
            "Failed to download iris.jar: timed out",
        ],
    )
    found = describe(error)
    assert found.message == "2 of 9 downloads failed"
    assert found.details == [
        "Failed to download sodium.jar: 404",
        "Failed to download iris.jar: timed out",
    ]


def test_files_to_download_by_hand_show_where_to_get_them():
    entries = [
        PackEntry(path="mods/a.jar", manual_url="https://example.invalid/a"),
        PackEntry(ref=FileRef("curseforge", "1", "2")),
    ]
    found = describe(UnresolvedEntriesError(entries))
    assert found.details == [
        "mods/a.jar  download it from https://example.invalid/a",
        "curseforge file 2",
    ]
    assert "--from" in found.hint
