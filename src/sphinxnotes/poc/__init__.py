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
from math import pi, cos, sin, ceil
from urllib.parse import quote

from sphinx.util import logging
from sphinx.util.docutils import SphinxRole
from docutils.nodes import Node, system_message, image, literal, Text

from data_url import construct_data_url

if TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

# less -> more
DEFAULT_FG_COLORS = ['#aceebb', '#4ac26b', '#2da44e', '#116329']
DEFAULT_BG_COLOR = '#eff2f5'

def generate_pie_svg(pct: int, bg_color: str, fg_colors: list[str]) -> str:
    RADIUS = 50
    pct = max(0, min(100, pct))
    fg_color = fg_colors[ceil(len(fg_colors)*pct/100) -1]

    # Generate SVG frame.
    # https://developer.mozilla.org/zh-CN/docs/Web/SVG/Tutorials/SVG_from_scratch/Positions
    svg = [
        f'<svg viewBox="0 0 {RADIUS*2} {RADIUS*2}" xmlns="http://www.w3.org/2000/svg">',
        f'<circle cx="{RADIUS}" cy="{RADIUS}" r="{RADIUS}" fill="{bg_color}"/>'
    ]

    if pct == 100:
        svg.append(f'<circle cx="{RADIUS}" cy="{RADIUS}" r="{RADIUS}" fill="{fg_color}"/>')
    elif pct > 0:
        angle = - 2 * pi * (pct / 100) + pi / 2
        x = RADIUS + RADIUS * cos(angle)
        y = RADIUS - RADIUS * sin(angle)  # 注意Y轴方向
        large_arc = 1 if (pct > RADIUS) else 0

        # https://developer.mozilla.org/zh-CN/docs/Web/SVG/Tutorials/SVG_from_scratch/Paths
        path = [
            # [M]ove to center of circle.
            f'M {RADIUS} {RADIUS}',
            # Draw a [L]ine as sector edge, at 12 o'clock.
            f'L {RADIUS} 0',
            # Draw a [Arc] according the angle.
            # A rx ry x-axis-rotation large-arc-flag sweep-flag x y
            # sweep-flag=1: clockwise
            f'A {RADIUS} {RADIUS} 0 {large_arc} 1 {x} {y}',
            # [L]ine back to circle center to close(Z) the shape.
            f'L {RADIUS} {RADIUS} Z'
        ]

        svg.append(f'<path d="{' '.join(path)}" fill="{fg_color}" />')

    svg.append('</svg>')
    svg = ''.join(svg)
    return svg

class ProgressRole(SphinxRole):

    @staticmethod
    def text_to_pct(v: str) -> int:
        if v.endswith('%'):
            pct = float(v.rstrip('%'))
        elif v.startswith('0.'):
            pct = float(v)*100
        elif '/' in v:
            [num, den] = v.split('/', maxsplit=1)
            pct =  100*float(num)/float(den) if float(den) != 0 else 0
        else:
            pct = 0
        return round(pct)

    def run(self) -> tuple[list[Node], list[system_message]]:
        pct = self.text_to_pct(self.text)
        svg = quote(generate_pie_svg(pct,
                                     self.config.progress_bg_color,
                                     self.config.progress_fg_colors))
        nodes = []
        nodes.append(image(self.rawtext,
                           uri = construct_data_url('image/svg+xml', False, svg),
                           alt = f'Progress: {self.text}',
                           width = '1em',
                           CLASS = 'sphinxnotes-progress',
                           ))

        if self.config.progress_with_label:
            nodes.append(Text(' '))
            nodes.append(literal(self.text, self.text))

        return nodes, []

def setup(app: Sphinx):
    """Sphinx extension entrypoint."""

    app.add_config_value('progress_fg_colors', DEFAULT_FG_COLORS, 'env', types=list[str])
    app.add_config_value('progress_bg_color', DEFAULT_BG_COLOR, 'env', types=str)
    app.add_config_value('progress_with_label', True, 'env', types=bool)

    app.add_role('progress', ProgressRole())

    return {'version': version('sphinxnotes.poc')}
