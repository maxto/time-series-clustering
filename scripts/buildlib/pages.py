"""Page assembly: the shell shared by every page (top bar, contents) and the lesson page.

The DOM here is a contract for the home, the sources page and the behaviour script (design 4.1, 4.3):
ids, classes and attributes are listed in the Task 5 brief of the redesign plan. Everything is plain
HTML and reads without JavaScript. All links are relative to `root` ("" on the home, "../" below it).
"""

import re

from .content import CODE_LANGUAGES, esc

LANG_NAMES = {"python": "Python", "r": "R"}
FIXED_LABELS = {"finance": "In finance", "measure": "Measure card", "code": "Code", "mistake": "Common mistake"}
# Small inline icons, drawn with currentColor so both themes follow the text colour.
ICON_SEARCH = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
               '<circle cx="7" cy="7" r="5"/><path d="M11 11l3.5 3.5"/></svg>')
ICON_MENU = ('<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M2 4h14M2 9h14M2 14h9" '
             'stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>')
ICON_THEME = ('<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5a6.5 6.5 0 1 0 0 13z" '
              'fill="currentColor"/><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>')
ICON_GITHUB = ('<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 '
               '3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38v-1.49c-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13'
               '-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89'
               '-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 0 1 4 0c1.53-1.04 2.2-.82 '
               '2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48v2.2c0 .21.15'
               '.46.55.38A8 8 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>')


def fill(template, values):
    """Replace {{key}} in one pass, so inserted content is never re-scanned."""
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template)


def head_meta(title, description, url, og_type, site):
    tags = [("name", "description", description), ("property", "og:type", og_type), ("property", "og:site_name", site),
            ("property", "og:title", title), ("property", "og:description", description), ("property", "og:url", url),
            ("property", "og:locale", "en_US"), ("name", "twitter:card", "summary")]
    return "\n".join([f"<title>{esc(title)}</title>", f'<link rel="canonical" href="{esc(url)}">',
                      *(f'<meta {k}="{v}" content="{esc(c)}">' for k, v, c in tags)])


def render(md, tokens):
    return md.renderer.render(tokens, md.options, {})


def render_inline(md, tok):
    return md.renderer.renderInline(tok.children or [], md.options, {})


def plain_label(md, block):
    """A block title as inline HTML without links, for use inside a link."""
    html = render_inline(md, block.title_tok) if block.title_tok is not None else esc(block.title)
    return re.sub(r"</?a\b[^>]*>", "", html)


def top_bar(root, course_title, repo_url, progress):
    """header.top: menu button, logo, course name, search, reading progress (lessons only), theme, GitHub."""
    bar = '<div class="progress" aria-hidden="true"><i></i></div>' if progress else ""
    return (
        '<header class="top"><div class="in">'
        '<button class="menu" type="button" aria-controls="contents" aria-expanded="false">'
        f'{ICON_MENU}<span class="lbl">Contents</span></button>'
        f'<a class="logo" href="{root}index.html" aria-label="{esc(course_title)}, home">TS</a>'
        f'<a class="name" href="{root}index.html">{esc(course_title)}</a>'
        f'<form class="search" role="search" action="{root}index.html" method="get">{ICON_SEARCH}'
        '<input id="q" name="q" type="search" autocomplete="off" placeholder="Search the course" '
        'aria-label="Search the course"></form>'
        f'{bar}'
        f'<button class="theme" type="button" aria-label="Switch colour theme">{ICON_THEME}</button>'
        f'<a class="gh" href="{esc(repo_url)}" aria-label="GitHub repository">{ICON_GITHUB}</a>'
        "</div></header>")


def contents_nav(course, root, finance_ids, current=None, toc=""):
    """nav#contents: course links, then every module with its lessons. `toc` is the ol.toc under `current`."""
    links = [("Course home", f"{root}index.html", current == "home"), ("Map of the field", f"{root}index.html#map", False),
             ("Examples by sector", f"{root}index.html#sectors", False),
             ("Sources", f"{root}sources/index.html", current == "sources")]
    out = ['<nav id="contents" aria-label="Course contents">'
           '<div class="dh"><strong>Contents</strong><button class="close" type="button" aria-label="Close contents">×</button></div>']
    for label, href, here in links:
        mark = ' aria-current="page"' if here else ""
        out.append(f'<a class="pg" href="{href}"{mark}>{label}</a>')
    for letter, title, entries in course.modules:
        out.append(f'<h2>{letter} · {esc(title)}</h2><ol>')
        for e in entries:
            tag = '<span class="fin">Finance</span>' if e.id in finance_ids else ""
            label = f'<span class="n">{e.number}</span><span class="t">{esc(e.title)}</span>{tag}'
            if e.status == "planned":
                out.append(f'<li class="coming"><span class="ls">{label}<span class="soon">coming</span></span></li>')
            elif e.id == current:
                out.append(f'<li class="here"><a class="ls" href="{root}{e.id}/index.html" aria-current="page">{label}</a>{toc}</li>')
            else:
                out.append(f'<li><a class="ls" href="{root}{e.id}/index.html">{label}</a></li>')
        out.append("</ol>")
    out.append("</nav>")
    return "".join(out)


def pager(prev, nxt):
    out = []
    for cls, label, e in (("prev", "Previous lesson", prev), ("next", "Next lesson", nxt)):
        if e:
            out.append(f'<a class="{cls}" href="../{e.id}/index.html"><span>{label}</span>{esc(e.title)}</a>')
    return f'<nav class="pager" aria-label="Lessons">{"".join(out)}</nav>'


def lesson_sources(lesson, sources):
    """The sources the lesson cites, in order of first citation. Entry ids (src-<key>) are targets of a.cite."""
    keys = list(dict.fromkeys(c.key for c in lesson.citations))
    if not keys:
        return ""
    items = []
    for k in keys:
        s = sources[k]
        links = "".join(f'<a href="{esc(url)}">{esc(name)}</a>' for name, url in s.links)
        links = f' <span class="ln">{links}</span>' if links else ""
        items.append(f'<li class="ref" id="src-{k}"><span class="au">{esc(s.full_authors)} ({s.year}).</span> '
                     f'<cite class="ti">{esc(s.title)}</cite>. <span class="ve">{esc(s.venue)}.</span>{links}</li>')
    return f'<section class="lsrc"><h2>Sources cited in this lesson</h2>\n<ol class="refs">{"".join(items)}</ol></section>\n'


def trade_box(meta):
    def box(label, values, cls):
        return f'<div class="{cls}"><p class="lbl">{label}</p><p>{esc(", ".join(values)) if values else "Nothing in particular"}</p></div>'
    if not (meta["ignores"] or meta["keeps"]):
        return ""
    return f'<div class="trade">{box("It ignores", meta["ignores"], "ignores")}{box("It keeps", meta["keeps"], "keeps")}</div>\n'


def libs_line(meta):
    parts = [f"{' '.join(f'<code>{esc(v)}</code>' for v in meta[key])} in {LANG_NAMES[lang]}"
             for lang, key in (("python", "python"), ("r", "r")) if meta[key]]
    return f'<p class="libs">Related library functions: {", ".join(parts)}.</p>\n' if parts else ""


def code_section(block, lesson, md):
    langs = [lang for lang in CODE_LANGUAGES if lang in lesson.code]
    if not langs:
        return ""
    prose = render(md, [t for t in block.tokens if t.type != "fence"])
    tabs = ""
    if len(langs) > 1:
        buttons = "".join(f'<button type="button" role="tab" data-lang="{lang}" aria-selected="{"true" if i == 0 else "false"}">'
                          f'{LANG_NAMES[lang]}</button>' for i, lang in enumerate(langs))
        tabs = f'<div role="tablist" aria-label="Language">{buttons}</div>'
    pres = "".join(f'<pre data-lang="{lang}"><code>{esc(lesson.code[lang])}</code></pre>' for lang in langs)
    return (f'<section class="code" id="code"><h2>Code</h2>\n{prose}'
            f'<div class="codebox"><div class="bar">{tabs}<button class="copy" type="button">Copy</button></div>{pres}</div>\n'
            f'{libs_line(lesson.meta)}</section>\n')


def lesson_main(lesson, course, md, prev, nxt, sources):
    """The inside of main#main, and the (id, label, kind) of every block the contents and jump links point to."""
    e, meta = lesson.entry, lesson.meta
    by_kind = {b.kind: b for b in lesson.blocks if b.kind != "section"}
    parts = [f'<div class="hero"><div class="mod">Module {esc(e.module)}, {esc(e.module_title)}</div>'
             f'<h1>{esc(meta["title"])}</h1><p class="lede">{esc(meta["lede"])}</p></div>\n', trade_box(meta)]
    targets = []
    for b in lesson.blocks:
        if b.kind == "section":
            targets.append((b.id, plain_label(md, b), "section"))
        elif b.kind in FIXED_LABELS and (b.kind != "code" or lesson.code):
            targets.append((b.id, FIXED_LABELS[b.kind], b.kind))
    jump = "".join(f'<a{cls} href="#{bid}">{label}</a>' for bid, label, kind in targets if kind != "mistake"
                   for cls in [' class="f"' if kind == "finance" else ""])
    parts.append(f'<nav class="jump" aria-label="Sections of this lesson">{jump}</nav>\n')
    parts.append(f'<div class="oneline" id="one-line">{render(md, by_kind["oneline"].tokens)}</div>\n')
    for b in lesson.blocks:
        if b.kind == "section":
            parts.append(f'<section class="content" id="{b.id}"><h2>{render_inline(md, b.title_tok)}</h2>\n{render(md, b.tokens)}</section>\n')
        elif b.kind == "finance":
            parts.append(f'<section class="finance" id="in-finance"><h2>In finance</h2>\n{render(md, b.tokens)}</section>\n')
        elif b.kind == "measure":
            parts.append(f'<section class="measure" id="measure-card"><h2>Measure card</h2>\n{render(md, b.tokens)}</section>\n')
        elif b.kind == "code":
            parts.append(code_section(b, lesson, md))
    parts.append(f'<section class="mistake" id="common-mistake"><h2>Common mistake</h2>\n{render(md, by_kind["mistake"].tokens)}</section>\n')
    parts.append(lesson_sources(lesson, sources))
    parts.append(pager(prev, nxt))
    toc = "".join(f'<li><a href="#{bid}">{label}</a></li>' for bid, label, _ in targets)
    return "".join(parts), f'<ol class="toc">{toc}</ol>'


def lesson_page(lesson, course, md, template, prev, nxt, sources, finance_ids, build_mode, site_url, repo_url):
    e, meta = lesson.entry, lesson.meta
    main, toc = lesson_main(lesson, course, md, prev, nxt, sources)
    return fill(template, {
        "meta": head_meta(f"{meta['title']} · {course.title}", meta["lede"], f"{site_url}{e.id}/", "article", course.title),
        "build": build_mode, "root": "../",
        "top": top_bar("../", course.title, repo_url, progress=True),
        "contents": contents_nav(course, "../", finance_ids, current=e.id, toc=toc),
        "main": main,
    })
