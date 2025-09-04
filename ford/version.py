from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ford")
except PackageNotFoundError:
    try:
        from setuptools_scm import get_version  # type: ignore[import]
        __version__ = get_version(root="..", relative_to=__file__)
    except Exception:
        __version__ = "dev"
