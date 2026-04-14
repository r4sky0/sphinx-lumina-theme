"""Custom Sphinx directives for the Lumina theme."""

from docutils import nodes
from sphinx.util import logging

from sphinx_design.cards import CardDirective
from sphinx_design.grids import GridItemCardDirective
from sphinx_design.shared import create_component

from ._icon_utils import get_icon_svg

logger = logging.getLogger(__name__)


def _inject_icon(card_node, icon_name, icon_style):
    """Inject an icon SVG into a card node's body.

    Finds the card-body and card-title components inside the card node
    and injects the icon according to the chosen style.
    """
    svg = get_icon_svg(icon_name, size=20, css_class="lumina-icon")
    if not svg:
        logger.warning("Unknown Lucide icon: %s", icon_name)
        return

    # Find the card-body container
    body = None
    for child in card_node.findall(nodes.container):
        if child.get("design_component") == "card-body":
            body = child
            break

    if body is None:
        return

    # Find the card-title container inside the body
    title = None
    for child in body.findall(nodes.container):
        if child.get("design_component") == "card-title":
            title = child
            break

    icon_raw = nodes.raw("", str(svg), format="html")

    if icon_style == "featured":
        # Create a featured icon pill above the title
        pill = create_component("card-icon-featured", ["sd-card-icon-featured"])
        pill.append(icon_raw)
        body.insert(0, pill)
    else:
        # Inline: add icon to title and apply flex class
        if title is not None:
            title["classes"].append("sd-card-icon-inline")
            title.insert(0, icon_raw)


class LuminaCardDirective(CardDirective):
    """Card directive with Lucide icon support."""

    option_spec = {
        **CardDirective.option_spec,
        "icon": lambda x: x.strip() if x else "",
        "icon-style": lambda x: (
            x.strip() if x and x.strip() in ("inline", "featured") else "inline"
        ),
    }

    def run_with_defaults(self):
        result = super().run_with_defaults()
        icon = self.options.get("icon", "")
        if icon:
            icon_style = self.options.get("icon-style", "inline")
            _inject_icon(result[0], icon, icon_style)
        return result


class LuminaGridItemCardDirective(GridItemCardDirective):
    """Grid-item-card directive with Lucide icon support."""

    option_spec = {
        **GridItemCardDirective.option_spec,
        "icon": lambda x: x.strip() if x else "",
        "icon-style": lambda x: (
            x.strip() if x and x.strip() in ("inline", "featured") else "inline"
        ),
    }

    def run_with_defaults(self):
        result = super().run_with_defaults()
        icon = self.options.get("icon", "")
        if icon:
            icon_style = self.options.get("icon-style", "inline")
            # GridItemCard wraps the card in a grid-item container
            # Find the actual card node inside
            for child in result[0].findall(nodes.container):
                if child.get("design_component") == "card":
                    _inject_icon(child, icon, icon_style)
                    break
        return result
