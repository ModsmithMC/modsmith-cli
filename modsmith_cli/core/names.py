"""Instance names: what is allowed, and a default made from a pack's name."""

import re

from .errors import AppError

NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,63}$")


def check_name(name: str) -> str:
    """Return a valid instance name unchanged.

    Raises:
        AppError: The name could not be a folder name on every system.
    """
    if not NAME.match(name) or name.endswith((" ", ".")):
        raise AppError(
            f"{name!r} cannot be an instance name.",
            hint=(
                "Use up to 64 letters, digits, spaces, dots, dashes and "
                "underscores, starting with a letter or digit."
            ),
        )
    return name


def name_from(text: str) -> str:
    """Make an instance name from a pack's name, such as ``fabulously-optimized``."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:64].strip("-")
    return slug or "instance"
