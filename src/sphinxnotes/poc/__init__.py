"""
sphinxnotes.poc
~~~~~~~~~~~~~~~

Proof of concept of some ideas about extending Sphinx.

:copyright: Copyright 2025 Shengyu Zhang
:license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from importlib.metadata import version

if TYPE_CHECKING:
    from sphinx.application import Sphinx

def setup(app: Sphinx):
    """Sphinx extension entrypoint."""

    from . import progress
    progress.setup(app)

    return {'version': version('sphinxnotes.poc')}
