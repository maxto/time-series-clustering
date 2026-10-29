"""The search index: assets/search-index.js, a plain script that sets window.TSC_SEARCH.

One entry per lesson block (title, section, plain text), per map item and per planned lesson.
href is relative to the site root. Code, math source, figures and citations are not indexed.
A plain script (not fetched JSON) so it loads from file://.
"""

import json

from .content import MATH, deep_title

SKIP_INLINE = ("code_inline", "image", "tsc_cite", *MATH)
BLOCK_TITLES = {"oneline": "One line", "finance": "In finance", "measure": "Measure card", "mistake": "Common mistake"}


def inline_words(children, out):
    for c in children or []:
        if c.type in SKIP_INLINE:  # the whole subtree: an image's alt text is a caption, not prose
            continue
        if c.type == "text":
            out.append(c.content)
        elif c.type in ("softbreak", "hardbreak"):
            out.append(" ")
        inline_words(c.children, out)


def block_text(tokens):
    """The prose of a block's tokens: inline text only, no code blocks, math, figures or citations."""
    parts = []
    for tok in tokens:
        if tok.type == "container_deep_open":
            parts.append(" ".join(deep_title(tok).split()))
        elif tok.type == "inline":
            words = []
            inline_words(tok.children, words)
            parts.append(" ".join("".join(words).split()))
    return " ".join(p for p in parts if p)


def build_index(course, lessons, atlas):
    entries = []
    for lesson in lessons:
        e, meta = lesson.entry, lesson.meta
        entries.append({"kind": "lesson", "title": meta["title"], "section": "", "href": f"{e.id}/index.html",
                        "text": " ".join(meta["lede"].split()), "draft": False})
        for b in lesson.blocks:
            if b.kind == "code":
                continue
            section = BLOCK_TITLES.get(b.kind) or b.title
            entries.append({"kind": "lesson", "title": meta["title"], "section": section, "href": f"{e.id}/index.html#{b.id}",
                            "text": block_text(b.tokens), "draft": False})
    if atlas:
        for branch in atlas.branches:
            for fam in branch.families:
                for it in fam.items:
                    entries.append({"kind": "map", "title": it.name, "section": f"{branch.name}, {fam.name}",
                                    "href": f"index.html#item-{it.id}", "text": it.does, "draft": not it.reviewed})
    for e in course.entries:
        if e.status == "planned":
            entries.append({"kind": "planned", "title": e.title, "section": "Coming", "href": f"index.html#lesson-{e.id}",
                            "text": "", "draft": False})
    return entries


def index_script(entries):
    text = json.dumps(entries, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return f"window.TSC_SEARCH={text};\n"
