"""What the app remembers about each instance, next to the library's own state."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .errors import AppError

RECORD_FILE = ".modsmith/app.json"


@dataclass(frozen=True)
class PackSource:
    """Where an instance's pack came from, so it can be updated.

    Attributes:
        platform: The platform's name, or None for a local file.
        project_id: The pack's project id on that platform.
        release_id: The installed release's id on that platform.
        file: The local pack file, or None for a platform pack.
    """

    platform: str | None = None
    project_id: str | None = None
    release_id: str | None = None
    file: str | None = None


@dataclass(frozen=True)
class Record:
    """What the app remembers about one instance.

    Attributes:
        source: Where its pack came from, or None if it has no pack.
        profile: The key of its official launcher profile, or None.
        optional: The optional pack files the player chose.
    """

    source: PackSource | None = None
    profile: str | None = None
    optional: tuple[str, ...] = field(default_factory=tuple[str, ...])


def read_record(instance: Path) -> Record:
    """Read an instance's record, or an empty one if it has none.

    Raises:
        AppError: The record is corrupt.
    """
    path = instance / RECORD_FILE
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return Record()
    except ValueError as e:
        raise AppError(f"{path} is corrupt: {e}") from e
    try:
        source = data.get("source")
        return Record(
            source=PackSource(**source) if source else None,
            profile=data.get("profile"),
            optional=tuple(data.get("optional", ())),
        )
    except TypeError as e:
        raise AppError(f"{path} is corrupt: {e}") from e


def write_record(instance: Path, record: Record) -> None:
    """Save an instance's record."""
    path = instance / RECORD_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")
