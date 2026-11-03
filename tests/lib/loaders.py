"""A real loader, registered with the library, that installs without a network."""

from dataclasses import dataclass
from typing import ClassVar

from modsmith.loaders import Loader, LoaderVersion, register


@register
@dataclass(frozen=True)
class TestLoader(Loader):
    """Installs by writing a version JSON, and lists versions from a class list."""

    __test__ = False
    kind: ClassVar[str] = "test-loader"
    published: ClassVar[list[str]] = ["2", "1"]

    def version_id(self, *, session=None, cache_dir=None):
        return f"test-loader-{self.version}-{self.minecraft}"

    def expected_id(self):
        return self.version_id()

    def install(self, game, **options):
        game.write_version(
            self.version_id(), {"id": self.version_id(), "inheritsFrom": self.minecraft}
        )
        return self.version_id()

    @classmethod
    def available(cls, minecraft, *, session=None):
        return [
            LoaderVersion(cls.kind, version, minecraft, recommended=index == 0)
            for index, version in enumerate(cls.published)
        ]
