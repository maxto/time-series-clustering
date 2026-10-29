"""Build the course site from content/ into dist/.

Usage: uv run python scripts/build.py [--content DIR] [--dist DIR] [--previews] [--preview]

Reads DIR/_course.md (modules and lessons, published or planned) and one NN-<id>.md per
published lesson, validates everything (schema, sections, prose rules, figures, TeX) and
reports every problem as one line "<file>: <message>", exit 1. When all is valid it writes:
  DIST/index.html            home: hero, map of the field, sector cards, lesson index (planned lessons "coming")
  DIST/<id>/index.html       one page per published lesson
  DIST/sources/index.html    every registered source with its links and where it is cited
  DIST/assets/               theme.css, theme.js, course.js, map.js, search-index.js (generated), Geist fonts, KaTeX css and fonts
  DIR/figures/<name>.preview.svg   light preview of each figure for GitHub (default content/
                             only, or with --previews)
Two modes. The release build (default, DIST defaults to dist/) fails on every map item or sector fit
without a current review record (one line each). The preview build (--preview, DIST defaults to
preview/) allows them, marks the home with a draft banner and never writes into dist/. Every page
carries <html data-build="release|preview" data-root="...">.
All links are relative, so the site works from file:// and under the Pages subpath.
"""

import argparse
import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from buildlib import svg  # noqa: E402
from buildlib.atlas import load_atlas  # noqa: E402
from buildlib.cite import check_reviews, cited_sources, load_reviews, load_sources  # noqa: E402
from buildlib.content import Errors, esc, load_course, load_lessons, markdown, show  # noqa: E402
from buildlib.katex import render_math  # noqa: E402
from buildlib.search import build_index, index_script  # noqa: E402
from buildlib.pages import (contents_nav, fill, head_meta, lessons_section, lesson_page, map_section, sectors_section,  # noqa: E402
                            sources_page, top_bar)

SITE_URL = "https://maxto.github.io/time-series-clustering/"
REPO_URL = "https://github.com/maxto/Time-Series-Clustering"  # the repo is not renamed yet

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
NODE = ROOT / "node_modules"
MARKER = ".tsc-build"


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

    def cite(self, tokens, idx, options, env):
        meta = tokens[idx].meta
        return f'<a class="cite" href="#src-{meta["key"]}" data-ref="{meta["key"]}">{esc(meta["label"])}</a>'

    md.add_render_rule("math_inline", math_inline)
    md.add_render_rule("math_inline_double", math_inline)
    md.add_render_rule("math_block", math_block)
    md.add_render_rule("tsc_figure", figure)
    md.add_render_rule("tsc_cite", cite)
    md.add_render_rule("tsc_skip", lambda self, tokens, idx, options, env: "")
    return md


def home_page(course, template, overview, atlas, sources, finance_ids, build_mode="release"):
    published = course.published()
    by_id = {e.id: e for e in course.entries}
    cta = (f'<p class="cta"><a class="start" href="{published[0].id}/index.html">Start with lesson 1</a></p>' if published else "")
    n = len(course.entries)
    atlas_html = ""
    if atlas:
        atlas_html = (map_section(atlas, sources, by_id, "", build_mode == "preview", course.title) + sectors_section(atlas))
    return fill(template, {
        "meta": head_meta(course.title, course.tagline, SITE_URL, "website", course.title),
        "build": build_mode, "root": "",
        "top": top_bar("", course.title, REPO_URL, progress=False),
        "contents": contents_nav(course, "", finance_ids, current="home"),
        "count": f"{n} lessons · {len(published)} published", "title": esc(course.title),
        "tagline": esc(course.tagline), "cta": cta,
        "overview": f'<figure class="overview">{overview}</figure>' if overview else "",
        "atlas": atlas_html, "lessons": lessons_section(course, finance_ids),
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
    for name in ("theme.css", "theme.js", "course.js", "map.js", "favicon.svg"):
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
    ap.add_argument("--dist", type=pathlib.Path, help="output directory (default: dist/, or preview/ with --preview)")
    ap.add_argument("--preview", action="store_true", help="preview build: allow draft map items and fits, write to preview/")
    ap.add_argument("--previews", action="store_true", help="write figure previews also for a --content other than content/")
    args = ap.parse_args()
    content = (args.content or ROOT / "content").resolve()
    dist = (args.dist or ROOT / ("preview" if args.preview else "dist")).resolve()
    mode = "preview" if args.preview else "release"
    if args.preview and dist.is_relative_to(ROOT / "dist"):
        print(f"{show(dist)}: a preview never writes into dist/ (the release tree)")
        return 1
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
    sources = load_sources(content, errors)
    reviews = load_reviews(content, errors)
    lessons = load_lessons(content, course, md, sources, errors)
    check_reviews(lessons, sources, reviews, errors)
    atlas = load_atlas(content, sources, reviews, course, errors)
    if atlas and not args.preview:
        for line in atlas.draft_items():
            errors.add(content / "_map.toml", line)
        for line in atlas.draft_fits() + atlas.draft_sectors():
            errors.add(content / "_sectors.toml", line)

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
    finance_ids = {lesson.entry.id for lesson in lessons if any(b.kind == "finance" for b in lesson.blocks)}
    for i, lesson in enumerate(lessons):
        prev = published[i - 1] if i > 0 else None
        nxt = published[i + 1] if i + 1 < len(published) else None
        (dist / lesson.entry.id).mkdir()
        page = lesson_page(lesson, course, md, template, prev, nxt, sources, finance_ids, mode, SITE_URL, REPO_URL)
        (dist / lesson.entry.id / "index.html").write_text(page)
    (dist / "index.html").write_text(home_page(
        course, (SITE / "home.html").read_text(), figures.get("overview"), atlas, sources, finance_ids, mode))
    (dist / "assets" / "search-index.js").write_text(index_script(build_index(course, lessons, atlas)))
    (dist / "sources").mkdir()
    in_map = {r.key for it in atlas.items() for r in it.all_refs()} | {r.key for ft in atlas.fits() for r in ft.sources} if atlas else set()
    (dist / "sources" / "index.html").write_text(sources_page(
        course, (SITE / "sources.html").read_text(), sources, cited_sources(lessons), in_map, finance_ids, mode, SITE_URL, REPO_URL))

    written = []
    if previews and figures:
        css, background = svg.preview_css(theme_css)
        written = [svg.write_preview(content / "figures" / f"{name}.svg", markup, css, background)
                   for name, markup in figures.items()]
    print(f"build: {len(lessons)} lessons of {len(course.entries)}, {len(figures)} figures,"
          f" {len(written)} previews ({mode}) -> {show(dist)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
