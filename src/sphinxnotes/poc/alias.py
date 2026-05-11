from __future__ import annotations
from typing import TYPE_CHECKING

from docutils.parsers.rst import directives, roles

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config


def _config_inited(app: Sphinx, cfg: Config) -> None:
    for name, alias in cfg.alias_directives:
        directive = directives._directives[name]  # type: ignore[attr-defined]
        app.add_directive(alias, directive)

    for name, alias in cfg.alias_roles:
        directive = roles._roles[name]  # type: ignore[attr-defined]
        app.add_directive(alias, directive)


def setup(app: Sphinx):
    app.add_config_value('alias_directives', [], 'env', types=list[str])
    app.add_config_value('alias_roles', [], 'env', types=list[str])

    # Should have priority below any other "config-inited" callback.
    app.connect('config-inited', _config_inited, priority=999)
