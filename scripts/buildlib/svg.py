"""Figure rules and GitHub previews.

A figure is styled only through the classes in the figure block of site/theme.css:
no colour attributes, no inline style, no width/height on the root, role="img" and a
<title>. The class whitelist is read from that block, so the stylesheet is the one source.
"""

import re
import xml.etree.ElementTree as ET

from .content import show

ELEMENTS = {"svg", "g", "defs", "marker", "rect", "circle", "ellipse", "line", "polyline", "polygon", "path",
            "text", "tspan", "title", "desc"}
DRAWN = {"rect", "circle", "ellipse", "line", "polyline", "polygon", "path"}
ATTRS = {"xmlns", "viewBox", "role", "aria-label", "aria-hidden", "id", "class", "transform", "opacity",
         "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "width", "height", "d", "points", "dx", "dy",
         "text-anchor", "stroke-width", "stroke-dasharray", "stroke-linecap", "stroke-linejoin", "fill-opacity",
         "stroke-opacity", "marker-start", "marker-mid", "marker-end", "markerWidth", "markerHeight", "refX", "refY",
         "orient", "markerUnits", "preserveAspectRatio"}
COLOUR_ATTRS = {"fill", "stroke", "color", "stop-color", "flood-color", "lighting-color"}
BLOCK = re.compile(r"/\* figure-classes:start \*/(.*?)/\* figure-classes:end \*/", re.S)


def figure_block(theme_css):
    m = BLOCK.search(theme_css)
    if not m:
        raise SystemExit("site/theme.css: figure-classes:start/end markers not found")
    return m.group(1)


def allowed_classes(theme_css):
    return set(re.findall(r"figure svg \.([a-z][a-z0-9-]*)", figure_block(theme_css)))


def local(name):
    return name.split("}")[-1]


def check_svg(path, classes, errors):
    """Validate one figure file. Returns the markup to inline (no prolog, no comments) or None."""
    text = path.read_text()
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        errors.add(path, f"SVG is not well-formed XML: {e}")
        return None
    if local(root.tag) != "svg":
        errors.add(path, "root element is not <svg>")
        return None
    if len(root.get("viewBox", "").split()) != 4:
        errors.add(path, "root <svg> needs a viewBox of four numbers")
    if root.get("width") is not None or root.get("height") is not None:
        errors.add(path, "root <svg> must not have width or height (CSS sizes it)")
    if root.get("role") != "img":
        errors.add(path, 'root <svg> needs role="img"')
    titles = [c for c in root if local(c.tag) == "title"]
    if not titles or not (titles[0].text or "").strip():
        errors.add(path, "root <svg> needs a non-empty <title> child")
    for el in root.iter():
        tag = local(el.tag)
        if tag not in ELEMENTS:
            errors.add(path, f"element <{tag}> not allowed")
        for name, value in el.attrib.items():
            name = local(name)
            if name == "style":
                errors.add(path, f"inline style on <{tag}>: use a class from site/theme.css")
            elif name in COLOUR_ATTRS:
                if not (name in ("fill", "stroke") and value == "none"):
                    errors.add(path, f'colour attribute {name}="{value}" on <{tag}>: use a class from site/theme.css')
            elif name not in ATTRS:
                errors.add(path, f"attribute {name!r} on <{tag}> not allowed")
        used = set((el.get("class") or "").split())
        if used - classes:
            errors.add(path, f"classes {sorted(used - classes)} on <{tag}> are not figure classes of site/theme.css")
        if tag in DRAWN and not used:
            errors.add(path, f"<{tag}> has no class, so it has no theme colour")
    markup = re.sub(r"<\?xml.*?\?>|<!--.*?-->", "", text, flags=re.S).strip()
    return markup


def preview_css(theme_css):
    """The figure block with light values in place of every var(), without the 'figure svg ' prefix."""
    light = dict(re.findall(r"(--[a-z0-9-]+):\s*([^;]+);", theme_css.split(":root {", 1)[1].split("}", 1)[0]))

    def resolve(value, depth=0):
        if depth > 10:
            raise SystemExit(f"site/theme.css: var() loop in {value!r}")
        return re.sub(r"var\((--[a-z0-9-]+)\)", lambda m: resolve(light[m.group(1)], depth + 1), value)

    css = resolve(figure_block(theme_css))
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S).replace("figure svg ", "")
    return re.sub(r"\s*\n\s*", "", css), resolve("var(--fig-bg)")


def write_preview(path, markup, css, background):
    """<name>.preview.svg next to the figure: light theme, styles inlined, for the README on GitHub."""
    svg = markup if "xmlns=" in markup.split(">", 1)[0] else markup.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    svg = re.sub(r"(<svg[^>]*>)", lambda m: f'{m.group(1)}<style>{css}</style><rect width="100%" height="100%" fill="{background}"/>',
                 svg, count=1)
    out = path.with_name(path.stem + ".preview.svg")
    out.write_text(svg + "\n")
    return show(out)
