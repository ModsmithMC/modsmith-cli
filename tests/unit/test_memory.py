import pytest

from modsmith_cli.core.memory import game_memory_mb, total_memory_mb


@pytest.mark.parametrize(
    ("recommended", "total", "expected"),
    [
        (None, 16384, 6144),  # half, up to 6 GiB
        (None, 8192, 4096),
        (None, 4096, 2048),
        (None, 2048, 2048),  # never below what the launcher gives
        (8192, 32768, 8192),  # a pack's recommendation is followed
        (12288, 8192, 6144),  # but leaves a quarter for the computer
        (5000, 16384, 4608),  # in steps of 512 MiB
        (None, None, 2048),
        (6144, None, 6144),
    ],
)
def test_game_memory(recommended, total, expected):
    assert game_memory_mb(recommended, total) == expected


def test_this_computer_reports_its_memory():
    total = total_memory_mb()
    assert total is not None
    assert total > 0
