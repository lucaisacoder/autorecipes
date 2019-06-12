"""A generic Conan recipe for Python projects.

I considered using ``Pyproject`` in the names instead of ``Python``,
but once it has become a certified standard, no one will tell the difference.
"""

import os
from pathlib import Path
import typing as t

from conans import ConanFile  # type: ignore

from conan_cmake.descriptors import classproperty


class PythonAttributes:
    """A descriptor that lazily loads attributes from ``pyproject.toml``."""

    def __init__(self):
        self.attrs = None

    def __get__(self, obj: object, typ: type = None) -> t.Mapping[str, t.Any]:
        if self.attrs is None:
            # TODO: There is no avoiding this import...
            import toml

            source_dir = Path(os.getcwd())
            pyproject = toml.load(open(source_dir / 'pyproject.toml', 'r'))
            self.attrs = pyproject['tool']['poetry']
        return self.attrs

    def desc(self, key):  # pylint: disable=no-self-use
        """Create a descriptor that lazily returns one attribute."""

        @classproperty
        def f(cls):
            # We are assuming that the :class:`CMakeAttributes` descriptor
            # will be named ``attrs``.
            return cls.attrs[key]

        f.__name__ = key
        return f


class PythonExportsDescriptor:
    """A descriptor that lazily computes exported sources."""

    def __get__(self, obj: object, typ: type = None) -> t.Iterable[str]:
        yield 'pyproject.toml'
        for package in obj.attrs.get('packages', []):
            if 'include' in package:
                yield f"{package['include']}/**.py"


class PythonConanFile(ConanFile):
    """A base class for Conan recipes for Python projects."""
    attrs = PythonAttributes()

    name = attrs.desc('name')
    version = attrs.desc('version')
    description = attrs.desc('description')
    license = attrs.desc('license')
    url = attrs.desc('repository')
    exports = PythonExportsDescriptor()
