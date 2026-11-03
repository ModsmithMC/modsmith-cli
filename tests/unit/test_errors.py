import pytest
from modsmith.errors import LockedError, NetworkError, PlatformError

from modsmith_app.cli.errors import describe
from modsmith_app.core.errors import AppError


@pytest.mark.parametrize(
    ("error", "hint"),
    [
        (NetworkError("GET x failed: timed out"), "internet connection"),
        (NetworkError("GET x returned 503", 503), "busy"),
        (NetworkError("GET x returned 429", 429), "busy"),
        (LockedError("locked"), "Another Modsmith"),
    ],
)
def test_hints(error, hint):
    assert hint in describe(error)[1]


def test_errors_without_a_hint():
    assert describe(NetworkError("GET x returned 404", 404)) == (
        "GET x returned 404",
        None,
    )
    assert describe(PlatformError("no such project"))[1] is None
    assert describe(AppError("bad", hint="fix it")) == ("bad", "fix it")
