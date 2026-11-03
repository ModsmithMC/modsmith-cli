"""Find the files an instance holds by the names players use for them."""

from collections.abc import Iterable

from modsmith.instances import Addition, ContentFile, Instance, InstanceState

from .errors import AppError

DISABLED = ".disabled"


def _file_name(path: str) -> str:
    return path.rsplit("/", 1)[-1].lower()


def find_contents(instance: Instance, names: Iterable[str]) -> list[ContentFile]:
    """Match each name to one mod, resource pack or shader pack in the instance.

    A name can be an added project's id or slug, a path such as
    ``mods/sodium.jar``, or a file name with or without ``.disabled``.

    Raises:
        AppError: A name matches nothing, or more than one file.
    """
    contents = instance.contents()
    found: list[ContentFile] = []
    for name in names:
        wanted = name.lower().removesuffix(DISABLED)
        hits = [
            item
            for item in contents
            if (item.addition is not None and item.addition.matches(name))
            or item.path.lower() == wanted
            or _file_name(item.path) == wanted
        ]
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


def removal_preview(
    state: InstanceState, names: Iterable[str], *, keep_dependencies: bool
) -> list[Addition]:
    """Work out which additions removing these projects takes away.

    Dependencies that nothing else needs go too, unless they are kept.

    Raises:
        AppError: A name is not a project that was added on its own.
    """
    names = list(names)
    unknown = [
        name
        for name in names
        if not any(item.matches(name) for item in state.additions)
    ]
    if unknown:
        raise AppError(
            f"Not added on its own: {', '.join(unknown)}.",
            hint="Files from the pack cannot be removed, but you can turn them off "
            "with: modsmith disable",
        )
    staying = [
        item
        for item in state.additions
        if not any(item.matches(name) for name in names)
    ]
    while not keep_dependencies:
        needed = {project for item in staying for project in item.requires}
        kept = [item for item in staying if item.requested or item.project_id in needed]
        if len(kept) == len(staying):
            break
        staying = kept
    return [item for item in state.additions if item not in staying]
