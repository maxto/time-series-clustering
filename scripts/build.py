"""Build the course site from content/ into dist/.

Usage: uv run python scripts/build.py [--content DIR] [--dist DIR] [--previews]

Reads DIR/_course.md (modules and lessons, published or planned) and one NN-<id>.md per
published lesson, validates everything (schema, sections, prose rules, figures, TeX) and
reports every problem as one line "<file>: <message>", exit 1. When all is valid it writes:
  DIST/index.html            home: overview graphic and module list, planned lessons "coming"
  DIST/<id>/index.html       one page per published lesson
  DIST/assets/               theme.css, theme.js, Geist fonts, KaTeX css and fonts
  DIR/figures/<name>.preview.svg   light preview of each figure for GitHub (default content/
                             only, or with --previews)
All links are relative, so the site works from file:// and under the Pages subpath.
"""

import argparse
import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from buildlib import svg  # noqa: E402
from buildlib.content import Errors, esc, load_course, load_lessons, markdown, show  # noqa: E402
from buildlib.katex import render_math  # noqa: E402

SITE_URL = "https://maxto.github.io/time-series-clustering/"

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
NODE = ROOT / "node_modules"
MARKER = ".tsc-build"


def fill(template, values):
    """Replace {{key}} in one pass, so inserted content is never re-scanned."""
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template)


def head_meta(title, description, url, og_type, site):
    tags = [("name", "description", description), ("property", "og:type", og_type), ("property", "og:site_name", site),
            ("property", "og:title", title), ("property", "og:description", description), ("property", "og:url", url),
            ("property", "og:locale", "en_US"), ("name", "twitter:card", "summary")]
    return "\n".join([f"<title>{esc(title)}</title>", f'<link rel="canonical" href="{esc(url)}">',
                      *(f'<meta {k}="{v}" content="{esc(c)}">' for k, v, c in tags)])


def setup_markdown(figures):
    md = markdown()

    def math_inline(self, tokens, idx, options, env):
        return tokens[idx].meta["html"]

    def math_block(self, tokens, idx, options, env):
        return f'<div class="math">{tokens[idx].meta["html"]}</div>\n'

    def figure(self, tokens, idx, options, env):
        meta = tokens[idx].meta
        caption = self.renderInline(meta["caption"], options, env)
        return f'<figure>{figures[meta["name"]]}<figcaption>{caption}</figcaption></figure>\n'

    md.add_render_rule("math_inline", math_inline)
    md.add_render_rule("math_inline_double", math_inline)
    md.add_render_rule("math_block", math_block)
    md.add_render_rule("tsc_figure", figure)
    md.add_render_rule("tsc_skip", lambda self, tokens, idx, options, env: "")
    return md


def render(md, tokens):
    return md.renderer.render(tokens, md.options, {})


def notes(lesson, md):
    meta, out = lesson.meta, []
    if meta["ignores"] or meta["keeps"]:
        chips = "".join(f'<span class="y">{esc(v)}</span>' for v in meta["ignores"])
        chips += "".join(f"<span>{esc(v)}</span>" for v in meta["keeps"])
        out.append(f'<div class="note ignores"><b>What it ignores</b><div class="chips">{chips}</div>'
                   '<div class="legend">Highlighted: ignored. Grey: kept.</div></div>')
    if "In finance" in lesson.sections:
        out.append(f'<div class="note finance"><b>In finance</b>{render(md, lesson.sections["In finance"])}</div>')
    code = [f"{lang} · {esc(', '.join(meta[key]))}" for lang, key in (("Python", "python"), ("R", "r")) if meta[key]]
    if code:
        out.append(f'<div class="note code"><b>Code</b><span class="mono">{"<br>".join(code)}</span></div>')
    return "\n".join(out)


def pager(prev, nxt):
    out = []
    for cls, label, e in (("prev", "← Previous", prev), ("next", "Next →", nxt)):
        if e:
            out.append(f'<a class="{cls}" href="../{e.id}/index.html"><span>{label}</span>{e.number} · {esc(e.title)}</a>')
    return "".join(out)


def lesson_page(lesson, course, md, template, prev, nxt, position):
    e, meta, sec = lesson.entry, lesson.meta, lesson.sections
    specimens = "".join(f'<div class="card {cls}"><b class="lbl">{name}</b>{render(md, sec[name])}</div>\n'
                        for name, cls in (("Measure card", "measure"), ("Check", "check")) if name in sec)
    mistake = render(md, sec["Common mistake"]).replace("<p>", "<p><b>Common mistake.</b> ", 1)
    total = len(course.published())
    return fill(template, {
        "meta": head_meta(f"{meta['title']} · {course.title}", meta["lede"], f"{SITE_URL}{e.id}/", "article", course.title),
        "root": "../", "site": esc(course.title.lower()), "module": esc(f"{e.module} · {e.module_title}"),
        "position": f"{position} / {total}", "progress": f"{round(100 * position / total)}",
        "kicker": esc(f"Lesson {e.number} · {meta['kicker']}"), "title": esc(meta["title"]), "lede": esc(meta["lede"]),
        "oneline": render(md, sec["One line"]), "body": render(md, sec["Lesson"]), "specimens": specimens,
        "mistake": mistake, "pager": pager(prev, nxt), "notes": notes(lesson, md),
    })


def home_page(course, template, overview):
    mods = []
    for letter, title, entries in course.modules:
        items = []
        for e in entries:
            if e.status == "published":
                items.append(f'<li><span class="n">{e.number}</span><a href="{e.id}/index.html">{esc(e.title)}</a></li>')
            else:
                items.append(f'<li class="planned"><span class="n">{e.number}</span><span>{esc(e.title)}</span>'
                             '<span class="coming">coming</span></li>')
        mods.append(f'<section class="module"><h2>{letter} · {esc(title)}</h2><ol>{"".join(items)}</ol></section>')
    n, p = len(course.entries), len(course.published())
    return fill(template, {
        "meta": head_meta(course.title, course.tagline, SITE_URL, "website", course.title),
        "site": esc(course.title.lower()), "count": f"{n} lessons · {p} published", "title": esc(course.title),
        "tagline": esc(course.tagline), "overview": f'<figure class="overview">{overview}</figure>' if overview else "",
        "modules": "\n".join(mods),
    })


def prepare_dist(dist, errors):
    """Replace a previous build output. Refuse to touch a non-empty directory the build did not write."""
    if dist.exists():
        if not (dist / MARKER).exists() and any(dist.iterdir()):
            errors.append(f"{show(dist)}: refusing to replace a non-empty directory without {MARKER} (not a build output)")
            return False
        shutil.rmtree(dist)
    dist.mkdir(parents=True)
    (dist / MARKER).write_text("written by scripts/build.py, replaced on every build\n")
    return True


def copy_assets(dist):
    assets = dist / "assets"
    (assets / "fonts").mkdir(parents=True)
    (assets / "katex" / "fonts").mkdir(parents=True)
    for name in ("theme.css", "theme.js", "favicon.svg"):
        shutil.copyfile(SITE / name, assets / name)
    geist = NODE / "geist" / "dist" / "fonts"
    shutil.copyfile(geist / "geist-sans" / "Geist-Variable.woff2", assets / "fonts" / "Geist-Variable.woff2")
    shutil.copyfile(geist / "geist-mono" / "GeistMono-Variable.woff2", assets / "fonts" / "GeistMono-Variable.woff2")
    shutil.copyfile(NODE / "geist" / "LICENSE.txt", assets / "fonts" / "Geist-LICENSE.txt")
    katex = NODE / "katex" / "dist"
    # Ship only the woff2 fonts: drop the woff and ttf fallbacks from the stylesheet.
    css = re.sub(r',url\(fonts/[^)]+\.(?:woff|ttf)\) format\("(?:woff|truetype)"\)', "", (katex / "katex.min.css").read_text())
    (assets / "katex" / "katex.min.css").write_text(css)
    for font in (katex / "fonts").glob("*.woff2"):
        shutil.copyfile(font, assets / "katex" / "fonts" / font.name)
    shutil.copyfile(NODE / "katex" / "LICENSE", assets / "katex" / "LICENSE.txt")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--content", type=pathlib.Path, help="content directory (default: content/)")
    ap.add_argument("--dist", type=pathlib.Path, default=ROOT / "dist", help="output directory (default: dist/)")
    ap.add_argument("--previews", action="store_true", help="write figure previews also for a --content other than content/")
    args = ap.parse_args()
    content = (args.content or ROOT / "content").resolve()
    dist = args.dist.resolve()
    previews = args.previews or content == (ROOT / "content").resolve()

    if not (content / "_course.md").exists():
        if args.content is None:
            print("build: no content/_course.md, nothing to build")
            return 0
        print(f"{show(content / '_course.md')}: missing")
        return 1
    if not (NODE / "katex").exists() or not (NODE / "geist").exists():
        print("build: node_modules/katex or node_modules/geist missing, run `npm install`")
        return 1

    errors = Errors()
    md = markdown()
    course = load_course(content, errors)
    lessons = load_lessons(content, course, md, errors)

    theme_css = (SITE / "theme.css").read_text()
    classes = svg.allowed_classes(theme_css)
    figures = {}
    for path in sorted((content / "figures").glob("*.svg")):
        if not path.name.endswith(".preview.svg"):
            figures[path.stem] = svg.check_svg(path, classes, errors)
    render_math(lessons, ROOT, errors)
    if errors:
        print("\n".join(errors))
        return 1

    md = setup_markdown(figures)
    if not prepare_dist(dist, errors):
        print("\n".join(errors))
        return 1
    copy_assets(dist)
    order = {e.id: i for i, e in enumerate(course.published())}
    lessons.sort(key=lambda lesson: order[lesson.entry.id])
    published = course.published()
    template = (SITE / "page.html").read_text()
    for i, lesson in enumerate(lessons):
        prev = published[i - 1] if i > 0 else None
        nxt = published[i + 1] if i + 1 < len(published) else None
        (dist / lesson.entry.id).mkdir()
        page = lesson_page(lesson, course, md, template, prev, nxt, i + 1)
        (dist / lesson.entry.id / "index.html").write_text(page)
    (dist / "index.html").write_text(home_page(course, (SITE / "home.html").read_text(), figures.get("overview")))

    written = []
    if previews and figures:
        css, background = svg.preview_css(theme_css)
        written = [svg.write_preview(content / "figures" / f"{name}.svg", markup, css, background)
                   for name, markup in figures.items()]
    print(f"build: {len(lessons)} lessons of {len(course.entries)}, {len(figures)} figures,"
          f" {len(written)} previews -> {show(dist)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
