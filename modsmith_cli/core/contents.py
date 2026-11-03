"""Find the files an instance holds by the names players use for them."""

from collections.abc import Iterable

from modsmith import metadata
from modsmith.instances import ContentFile, Instance

from .errors import AppError

DISABLED = ".disabled"


def _file_name(path: str) -> str:
    return path.rsplit("/", 1)[-1].lower()


def _declared(instance: Instance, item: ContentFile) -> set[str]:
    """Return the id and name a file declares about itself, in lower case."""
    try:
        info = metadata.read(instance.path / item.location)
    except OSError:
        return set()
    if info is None:
        return set()
    return {text.lower() for text in (info.id, info.name) if text}


def _matches(
    instance: Instance, contents: Iterable[ContentFile], name: str
) -> list[ContentFile]:
    """Return the files a name means, trying cheap matches before reading files."""
    wanted = name.lower().removesuffix(DISABLED)
    hits = [
        item
        for item in contents
        if (item.addition is not None and item.addition.matches(name))
        or item.path.lower() == wanted
        or _file_name(item.path) == wanted
    ]
    if hits:
        return hits
    return [item for item in contents if wanted in _declared(instance, item)]


def find_contents(instance: Instance, names: Iterable[str]) -> list[ContentFile]:
    """Match each name to one mod, resource pack or shader pack in the instance.

    A name can be an added project's id or slug, a path such as
    ``mods/sodium.jar``, a file name with or without ``.disabled``, or the id
    or name a mod declares about itself, such as ``iris``.

    Raises:
        AppError: A name matches nothing, or more than one file.
    """
    contents = instance.contents()
    found: list[ContentFile] = []
    for name in names:
        hits = _matches(instance, contents, name)
        if not hits:
            raise AppError(
                f"Nothing in {instance.path.name} is called {name!r}.",
                hint=f"See what it holds with: modsmith show {instance.path.name}",
            )
        if len(hits) > 1:
            listed = ", ".join(item.path for item in hits)
            raise AppError(f"{name!r} could mean {listed}.", hint="Use the full path.")
        found.append(hits[0])
    return list(dict.fromkeys(found))
