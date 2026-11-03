"""Modsmith: modpacks, mods and packs for the official Minecraft launcher."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("modsmith-cli")
except PackageNotFoundError:
    __version__ = "0.0.0"
