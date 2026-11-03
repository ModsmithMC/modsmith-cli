"""Errors the app reports to the player."""


class AppError(Exception):
    """Something the player can fix, with a hint on how.

    Args:
        message: What went wrong.
        hint: What to do about it, or None.

    Attributes:
        message: What went wrong.
        hint: What to do about it, or None.
    """

    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
