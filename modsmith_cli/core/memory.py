"""How much memory to give the game."""

import ctypes
import os
import sys

MIB = 1024 * 1024
# The least the game gets, which is also what the official launcher gives.
FLOOR_MB = 2048
# Without a recommendation, a pack gets half the computer's memory, up to this.
DEFAULT_CEILING_MB = 6144
# What is left for the system and other programs, at the least.
SYSTEM_SHARE = 4
STEP_MB = 512


def total_memory_mb() -> int | None:
    """Return how much memory this computer has, in MiB, or None if unknown."""
    try:
        if sys.platform == "win32":
            return _windows_total() // MIB
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") // MIB
    except (AttributeError, OSError, ValueError):
        return None


if sys.platform == "win32":

    class _MemoryStatus(ctypes.Structure):
        """Windows' ``MEMORYSTATUSEX``."""

        _fields_ = [
            ("length", ctypes.c_ulong),
            ("load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("avail_phys", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("avail_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("avail_virtual", ctypes.c_ulonglong),
            ("avail_extended_virtual", ctypes.c_ulonglong),
        ]

    def _windows_total() -> int:
        """Return the physical memory in bytes, as Windows reports it."""
        status = _MemoryStatus()
        status.length = ctypes.sizeof(_MemoryStatus)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return int(status.total_phys)


def game_memory_mb(recommended: int | None, total: int | None) -> int:
    """Choose the game's maximum memory, in MiB.

    A pack's recommendation is followed, but never so far that the computer
    keeps less than a quarter of its memory. A pack that recommends nothing
    gets half the computer's memory, between 2 and 6 GiB.

    Args:
        recommended: What the pack recommends, or None.
        total: The computer's memory, or None if unknown.

    Returns:
        The memory, a multiple of 512 MiB and at least 2 GiB.
    """
    if total is None:
        wanted = recommended or FLOOR_MB
    else:
        most = total - total // SYSTEM_SHARE
        wanted = min(recommended or min(total // 2, DEFAULT_CEILING_MB), most)
    return max(FLOOR_MB, wanted // STEP_MB * STEP_MB)
