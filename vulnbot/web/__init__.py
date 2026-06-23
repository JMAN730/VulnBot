"""Web UI backend package for VulnBot."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("vulnbot")
except PackageNotFoundError:
    __version__ = "0.3.1"
