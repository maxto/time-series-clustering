"""Read and validate the course content: _course.md, lesson files, sections, prose rules.

Every problem is collected as one line "<file>: <message>" in an Errors list, so one
build run reports all of them.
"""

import html
import json
import math
import pathlib
import re
from dataclasses import dataclass, field

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin

from .cite import CITE, Citation, fingerprint, fingerprint_data

LESSON_KEYS = ("id", "module", "title", "kicker", "sector", "lede", "ignores", "keeps", "python", "r")
LIST_KEYS = ("ignores", "keeps", "python", "r")
PROSE_KEYS = ("title", "kicker", "lede", "ignores", "keeps")
SECTORS = ("energy", "finance", "weather", "retail", "industry", "health")
# Fixed blocks: name -> (kind, block id). Content sections (kind "section") sit between One line and In finance.
FIXED = {"One line": ("oneline", "one-line"), "In finance": ("finance", "in-finance"),
         "Measure card": ("measure", "measure-card"), "Code": ("code", "code"),
         "Common mistake": ("mistake", "common-mistake")}
KIND_ORDER = ("oneline", "section", "finance", "measure", "code", "mistake")
BLOCK_IDS = tuple(bid for _, bid in FIXED.values())
PICKS_MIN = 4  # a section with this many bold-led paragraphs lists options: it gets a chooser
ONE_PARAGRAPH = ("oneline", "mistake")
FIGURE_KINDS = ("section", "finance")
CODE_LANGUAGES = ("python", "r")
STATUSES = ("published", "planned")
MATH = ("math_inline", "math_inline_double", "math_block")
PROSE_BANNED = {";": "semicolon", "—": "em-dash"}
ID = r"[a-z0-9]+(?:-[a-z0-9]+)*"
NUMBER = re.compile(r"\{\{n:([^}]*)\}\}")
FIGURE = re.compile(r"figures/([a-z0-9-]+)\.svg")


class Errors(list):
    def add(self, path, msg):
        self.append(f"{show(path)}: {msg}")


def show(path):
    """A path as the reader typed it: relative to the working directory when inside it."""
    path = pathlib.Path(path)
    try:
        return str(path.resolve().relative_to(pathlib.Path.cwd()))
    except ValueError:
        return str(path)


def cite_rule(state, silent):
    """Inline rule for [@key, locator]. Runs only in prose: code spans and fences are skipped by the parser."""
    if state.src[state.pos:state.pos + 2] != "[@":
        return False
    m = CITE.match(state.src, state.pos)
    if not m:
        return False
    if not silent:
        tok = state.push("tsc_cite", "", 0)
        tok.meta = {"key": m.group(1), "locator": (m.group(2) or "").strip(), "label": m.group(1)}
    state.pos = m.end()
    return True


def markdown():
    md = MarkdownIt("commonmark", {"html": False})
    md.inline.ruler.before("link", "tsc_cite", cite_rule)
    md.use(dollarmath_plugin, allow_labels=False, double_inline=True)
    md.use(container_plugin, "deep", render=render_deep)
    return md


def deep_title(tok):
    """The plain-text title of a '::: deep <title>' opener token."""
    return tok.info.strip()[len("deep"):].strip()


def render_deep(self, tokens, idx, options, env):
    """A deep-dive is a native disclosure: closed by default, readable without JavaScript, no id."""
    if tokens[idx].nesting == 1:
        return f'<details class="deep"><summary>{html.escape(deep_title(tokens[idx]), quote=True)}</summary>\n'
    return "</details>\n"


DEEP_OPEN = re.compile(r" {0,3}:{3,}[ \t]*deep(?=[ \t]|$)[ \t]*(.*?)[ \t]*$")
DEEP_CLOSE = re.compile(r" {0,3}:{3,}[ \t]*$")
DEEP_OTHER = re.compile(r" {0,3}:{3,}[ \t]*\S")
FENCE_OPEN = re.compile(r" {0,3}(`{3,}|~{3,})")
H2_LINE = re.compile(r"## +(.*?) *#*$")
ANY_HEADING = re.compile(r" {0,3}#{1,6}(?:[ \t]|$)")
TITLE_MARKUP = re.compile(r"\$|\[@|\]\(|\[[^\]]*\]")


def check_deep_blocks(body, offset, path, errors):
    """Source-aware pass over '::: deep' blocks, before the parser (which closes an open block silently).

    Fenced code is skipped. Line numbers are those of the file (offset = lines before the body)."""
    fixed = {n.lower() for n in FIXED}
    fence = None  # (char, length) while inside a fenced code block
    section = None  # None before the first '## ', else True for a content section
    opened = None  # line number of the open block
    for n, line in enumerate(body.split("\n"), start=offset + 1):
        if fence:
            m = re.fullmatch(r" {0,3}(" + re.escape(fence[0]) + r"{" + str(fence[1]) + r",})[ \t]*", line)
            if m:
                fence = None
            continue
        m = FENCE_OPEN.match(line)
        if m and not (m.group(1)[0] == "`" and "`" in line[m.end():]):
            fence = (m.group(1)[0], len(m.group(1)))
            continue
        h2 = H2_LINE.fullmatch(line)
        if h2:
            if opened:
                errors.add(path, f"line {opened}: deep-dive is not closed before the next '## ' heading (line {n})")
                opened = None
            section = h2.group(1).strip().lower() not in fixed and h2.group(1).strip() not in ("Lesson", "Check")
            continue
        op = DEEP_OPEN.fullmatch(line)
        if op:
            title = op.group(1)
            if opened:
                errors.add(path, f"line {n}: nested deep-dive (the one opened at line {opened} is still open)")
                continue
            if not title:
                errors.add(path, f"line {n}: opener '::: deep' without a title (write '::: deep <title>')")
            else:
                check_prose(title, path, errors, f"deep-dive title, line {n}")
                if TITLE_MARKUP.search(title):
                    errors.add(path, f"line {n}: deep-dive title '{title}' may not hold a citation, math, a link or markup in brackets: plain text only")
            if not section:
                errors.add(path, f"line {n}: deep-dive outside a content section (it belongs in a '## <title>' content section)")
            opened = n
            continue
        if DEEP_CLOSE.fullmatch(line):
            if opened:
                opened = None
            else:
                errors.add(path, f"line {n}: closer ':::' with no open deep-dive")
            continue
        if DEEP_OTHER.match(line):
            errors.add(path, f"line {n}: unknown ':::' block (only '::: deep <title>' exists)")
            continue
        if opened:
            if ANY_HEADING.match(line):
                errors.add(path, f"line {n}: heading inside a deep-dive (opened at line {opened})")
            elif "![" in line:
                errors.add(path, f"line {n}: figure inside a deep-dive (opened at line {opened})")
    if opened:
        errors.add(path, f"line {opened}: deep-dive is not closed before the end of the file")


@dataclass
class Entry:
    id: str
    status: str
    title: str
    number: int
    module: str
    module_title: str


@dataclass
class Course:
    title: str = ""
    tagline: str = ""
    modules: list = field(default_factory=list)  # [(letter, title, [Entry])]
    entries: list = field(default_factory=list)

    def published(self):
        return [e for e in self.entries if e.status == "published"]


@dataclass
class Block:
    kind: str  # oneline | section | finance | measure | code | mistake
    title: str
    id: str  # fixed blocks: one-line, in-finance, measure-card, code, common-mistake. Sections: heading slug
    tokens: list
    title_tok: object = None  # sections: the inline token of the '##' heading (rendered by the page, so math and links work)
    picks: list = field(default_factory=list)  # sections: (id, label) of the options the section lists, for its chooser


@dataclass
class Lesson:
    entry: Entry
    path: pathlib.Path
    meta: dict
    blocks: list  # [Block] in document order
    code: dict = field(default_factory=dict)  # "python" / "r" -> code text, only those present
    citations: list = field(default_factory=list)  # [Citation] in document order
    fingerprint: str = ""  # whole text after {{n:}} (line endings only normalised) plus the identity of every cited source
    math: list = field(default_factory=list)  # math tokens, rendered in one batch later
    fragments: list = field(default_factory=list)  # "#id" link targets, checked against heading ids
    draft: bool = False  # preview only: the text or a citation has no current review record


def split_front(text, path, errors):
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        errors.add(path, "missing front matter (--- block at the top)")
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            errors.add(path, f"front matter line without a colon: {line!r}")
            continue
        meta[key.strip()] = value.strip()
    return meta, m.group(2)


def check_prose(text, path, errors, where):
    for char, name in PROSE_BANNED.items():
        if char in text:
            i = text.index(char)
            errors.add(path, f"{name} in prose ({where}): {text[max(0, i - 30):i + 30]!r}")


def load_course(content, errors):
    path = content / "_course.md"
    meta, body = split_front(path.read_text(), path, errors)
    course = Course(meta.get("title", ""), meta.get("tagline", ""))
    for key in ("title", "tagline"):
        if not meta.get(key):
            errors.add(path, f"missing front matter key {key!r}")
        check_prose(meta.get(key, ""), path, errors, key)
    for key in sorted(set(meta) - {"title", "tagline"}):
        errors.add(path, f"unknown front matter key {key!r}")
    seen = set()
    for line in body.splitlines():
        if not line.strip():
            continue
        if mm := re.fullmatch(r"## ([A-Z])\. (.+)", line):
            letter, title = mm.groups()
            if any(letter == m[0] for m in course.modules):
                errors.add(path, f"duplicate module {letter}")
            check_prose(title, path, errors, f"module {letter}")
            course.modules.append((letter, title.strip(), []))
        elif line.startswith("- "):
            parts = [p.strip() for p in line[2:].split("|")]
            if len(parts) != 3:
                errors.add(path, f"lesson line is not '- <id> | <status> | <title>': {line!r}")
                continue
            lid, status, title = parts
            if not course.modules:
                errors.add(path, f"lesson {lid!r} before any '## <Letter>. <Module>' heading")
                continue
            if not re.fullmatch(ID, lid):
                errors.add(path, f"bad lesson id {lid!r} (lowercase letters, digits, hyphens)")
            if lid in seen:
                errors.add(path, f"duplicate lesson id {lid!r}")
            if status not in STATUSES:
                errors.add(path, f"unknown status {status!r} for {lid!r} (published or planned)")
            if not title:
                errors.add(path, f"lesson {lid!r} has no title")
            check_prose(title, path, errors, f"title of {lid}")
            seen.add(lid)
            letter, mtitle, entries = course.modules[-1]
            entry = Entry(lid, status, title, len(course.entries) + 1, letter, mtitle)
            entries.append(entry)
            course.entries.append(entry)
        else:
            errors.add(path, f"unexpected line: {line!r}")
    for letter, _, entries in course.modules:
        if not entries:
            errors.add(path, f"module {letter} has no lessons")
    if not course.entries:
        errors.add(path, "no lessons listed")
    return course


class Numbers:
    """{{n:key}} values from figures/numbers.json, read only when a lesson asks for one."""

    def __init__(self, content):
        self.path = content / "figures" / "numbers.json"
        self.values = None

    def get(self, key, lesson_path, errors):
        if self.values is None:
            self.values = {}
            if self.path.exists():
                try:
                    self.values = json.loads(self.path.read_text())
                except json.JSONDecodeError as e:
                    errors.add(self.path, f"invalid JSON: {e}")
        if not self.path.exists():
            errors.add(lesson_path, f"{{{{n:{key}}}}} used but {show(self.path)} does not exist")
            return ""
        if key not in self.values:
            errors.add(lesson_path, f"{{{{n:{key}}}}}: no key {key!r} in {show(self.path)}")
            return ""
        value = self.values[key]
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            errors.add(self.path, f"value of {key!r} is not a string or a number")
            return ""
        return str(value)


def walk_inline(children):
    for tok in children or []:
        yield tok
        if tok.children:
            yield from walk_inline(tok.children)


def load_lessons(content, course, md, sources, errors):
    by_id = {e.id: e for e in course.entries}
    published = {e.id for e in course.published()}
    numbers = Numbers(content)
    lessons, files = [], {}
    for path in sorted(content.glob("*.md")):
        if path.name == "_course.md":
            continue
        mm = re.fullmatch(rf"(\d\d)-({ID})\.md", path.name)
        if not mm:
            errors.add(path, "not a lesson file name (NN-<id>.md)")
            continue
        number, lid = int(mm.group(1)), mm.group(2)
        entry = by_id.get(lid)
        if entry is None:
            errors.add(path, f"lesson file not listed in _course.md (id {lid!r})")
            continue
        if entry.status == "planned":
            errors.add(path, f"lesson {lid!r} is planned in _course.md, so it must not have a file")
            continue
        if lid in files:
            errors.add(path, f"second file for lesson {lid!r} (also {files[lid].name})")
            continue
        files[lid] = path
        if number != entry.number:
            errors.add(path, f"file number {number:02d} does not match position {entry.number} in _course.md")
        lessons.append(load_lesson(path, entry, md, numbers, published, content, sources, errors))
    for e in course.published():
        if e.id not in files:
            errors.add(content / "_course.md", f"published lesson {e.id!r} has no file {e.number:02d}-{e.id}.md")
    return [lesson for lesson in lessons if lesson]


def load_lesson(path, entry, md, numbers, published, content, sources, errors):
    text = NUMBER.sub(lambda m: numbers.get(m.group(1), path, errors), path.read_text())
    meta, body = split_front(text, path, errors)
    for key in LESSON_KEYS:
        if key not in meta:
            errors.add(path, f"missing front matter key {key!r}")
        elif key not in LIST_KEYS and not meta[key]:
            errors.add(path, f"empty front matter key {key!r}")
    for key in sorted(set(meta) - set(LESSON_KEYS)):
        errors.add(path, f"unknown front matter key {key!r}")
    if meta.get("sector") and meta["sector"] not in SECTORS:
        errors.add(path, f"sector {meta['sector']!r} is not one of: {', '.join(SECTORS)}")
    if meta.get("id", entry.id) != entry.id:
        errors.add(path, f"id {meta['id']!r} does not match the file name ({entry.id!r})")
    if meta.get("module", entry.module) != entry.module:
        errors.add(path, f"module {meta['module']!r} but _course.md lists {entry.id!r} under module {entry.module}")
    for key in LIST_KEYS:
        meta[key] = [v.strip() for v in meta.get(key, "").split(",") if v.strip()]
    for key in PROSE_KEYS:
        value = meta.get(key, "")
        check_prose(", ".join(value) if isinstance(value, list) else value, path, errors, key)

    check_deep_blocks(body, text[:len(text) - len(body)].count("\n"), path, errors)
    tokens = md.parse(body)
    blocks = split_blocks(tokens, path, errors)
    lesson = Lesson(entry, path, meta, blocks)
    for b in blocks:
        if b.title_tok is None:
            check_prose(b.title, path, errors, f"heading {b.title}")
        else:
            check_title(b, lesson, published, errors)
        check_tokens(b, lesson, published, content, sources, errors)
        if b.kind == "code":
            collect_code(b, lesson, errors)
    identities = sorted({sources[c.key].identity for c in lesson.citations if c.key in sources})
    lesson.fingerprint = fingerprint_data({"text": text, "sources": identities})
    ids = heading_ids(blocks, path, errors)
    # a link may also point at a fixed block the page renders: One line and Common mistake always, the others when present
    # ('code' only when a python or r block will render, as pages.lesson_main decides)
    targets = ids | {b.id for b in blocks if b.kind in ("oneline", "mistake", "finance", "measure")}
    if lesson.code:
        targets.add("code")
    for frag in lesson.fragments:
        if frag not in targets:
            errors.add(path, f"link '#{frag}': no heading or block with that id in this lesson"
                             f" (ids: {', '.join(sorted(targets)) or 'none'})")
    return lesson


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"


def inline_text(tok):
    """The plain text of an inline token (text and code, no math): what a heading id is made from."""
    return "".join(c.content for c in walk_inline(tok.children) if c.type in ("text", "code_inline"))


def heading_text(toks, i):
    return inline_text(toks[i + 1])


def check_title(block, lesson, published, errors):
    """A '## ' section title is inline Markdown: prose rules on its text, math collected, links checked."""
    for c in walk_inline(block.title_tok.children):
        if c.type == "text":
            check_prose(c.content, lesson.path, errors, f"heading {block.title}")
        elif c.type in MATH:
            lesson.math.append(c)
        elif c.type == "link_open":
            check_link(c, lesson, published, errors)
        elif c.type == "tsc_cite":
            errors.add(lesson.path, f"heading {block.title!r}: a citation does not belong in a heading")


def heading_ids(blocks, path, errors):
    """Give every rendered heading a deterministic, unique id (slug of its text, then -2, -3...).

    A content section's id is the id of its own '##' heading. A slug equal to a fixed block id is an error."""
    ids = set()

    def unique(text):
        base, n = slug(text), 1
        if base in BLOCK_IDS:
            errors.add(path, f"heading {text!r} has the slug {base!r}, which is a block id")
        hid = base
        while hid in ids:
            n += 1
            hid = f"{base}-{n}"
        ids.add(hid)
        return hid

    for b in blocks:
        if b.kind == "section":
            b.id = unique(inline_text(b.title_tok))
        for i, tok in enumerate(b.tokens):
            if tok.type == "heading_open":
                tok.attrSet("id", unique(heading_text(b.tokens, i)))
        if b.kind == "section":
            leads = [(i, label) for i in range(len(b.tokens)) if (label := lead_label(b.tokens, i))]
            if len(leads) >= PICKS_MIN:
                for i, label in leads:
                    pid = unique(label)
                    b.tokens[i].attrSet("id", pid)
                    b.picks.append((pid, label))
    return ids


def lead_label(tokens, i):
    """The bold words opening the top-level paragraph at tokens[i], without their closing '.' or ':', or None."""
    if tokens[i].type != "paragraph_open" or tokens[i].level != 0:
        return None
    children = [c for c in tokens[i + 1].children or [] if c.type != "text" or c.content]  # the parser opens with an empty text
    if not children or children[0].type != "strong_open":
        return None
    words = []
    for c in children[1:]:
        if c.type == "strong_close":
            return "".join(words).strip().rstrip(".:")
        words.append(c.content if c.type in ("text", "code_inline") else "")
    return None


def split_blocks(tokens, path, errors):
    """Top-level '## Name' headings split the body. A '##' inside a code block is a fence token."""
    blocks = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == "heading_open" and tok.tag == "h2" and tok.level == 0:
            name = tokens[i + 1].content.strip()
            title_tok = tokens[i + 1]
            i += 3
            if name in FIXED:
                kind, bid = FIXED[name]
                if any(b.kind == kind for b in blocks):
                    errors.add(path, f"section '## {name}' appears twice")
                blocks.append(Block(kind, name, bid, []))
            elif name.lower() in {n.lower() for n in FIXED}:
                errors.add(path, f"'## {name}' is a reserved block name (use exactly "
                                 f"{', '.join(repr(n) for n in FIXED)}, or another title for a content section)")
                blocks.append(Block("_skip", name, "", []))
            elif name == "Lesson":
                errors.add(path, "'## Lesson' was replaced by content sections (design 4.3): "
                                 "give each part its own '## <title>' section")
                blocks.append(Block("_skip", name, "", []))
            elif name == "Check":
                errors.add(path, "'## Check' is not used in the first phase (design 1.1): "
                                 "a validity example is a content section with its own title")
                blocks.append(Block("_skip", name, "", []))
            else:
                blocks.append(Block("section", name, "", [], title_tok))
            continue
        if tok.type == "heading_open" and tok.tag == "h1":
            errors.add(path, "'# ' headings are not allowed in a lesson (the title comes from the front matter)")
        if not blocks:
            errors.add(path, "text before the first '## ' section")
            blocks.append(Block("_skip", "", "", []))
        blocks[-1].tokens.append(tok)
        i += 1
    kinds = [b.kind for b in blocks if b.kind != "_skip"]
    expected = "One line, content sections, In finance, Measure card, Code, Common mistake"
    if kinds != sorted(kinds, key=KIND_ORDER.index):
        shown = ", ".join(b.title for b in blocks if b.kind != "_skip")
        errors.add(path, f"sections out of order: {shown} (expected order: {expected})")
    for kind in ONE_PARAGRAPH:
        if kind not in kinds:
            errors.add(path, f"missing section '## {next(n for n, (k, _) in FIXED.items() if k == kind)}'")
    if "section" not in kinds and not any(b.kind == "_skip" for b in blocks):
        errors.add(path, "a lesson needs at least one content section (a '## <title>' section after '## One line')")
    for b in blocks:
        if b.kind in ONE_PARAGRAPH and [t.type for t in b.tokens] != ["paragraph_open", "inline", "paragraph_close"]:
            errors.add(path, f"section '## {b.title}' must be exactly one paragraph")
    return [b for b in blocks if b.kind != "_skip"]


def collect_code(block, lesson, errors):
    """'## Code': at most one python and one r fence, optional paragraphs, nothing else."""
    para = ("paragraph_open", "inline", "paragraph_close")
    for tok in block.tokens:
        if tok.type == "fence":
            lang = tok.info.strip()
            if lang not in CODE_LANGUAGES:
                errors.add(lesson.path, f"code block language {lang!r}: '## Code' takes {' and '.join(CODE_LANGUAGES)}")
            elif lang in lesson.code:
                errors.add(lesson.path, f"'## Code' has two {lang} blocks (at most one per language)")
            else:
                lesson.code[lang] = tok.content
        elif tok.type not in para and tok.level == 0:
            errors.add(lesson.path, f"'## Code' holds only paragraphs and fenced code, found {tok.type}")


def check_tokens(block, lesson, published, content, sources, errors):
    """Prose rules, math collection, links and figures for the tokens of one block."""
    path, tokens, section = lesson.path, block.tokens, block.title
    figures_ok = block.kind in FIGURE_KINDS
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type in MATH:
            lesson.math.append(tok)
        if tok.type == "inline":
            images = [c for c in walk_inline(tok.children) if c.type == "image"]
            alone = (len(tok.children) == 1 and images and i > 0 and tokens[i - 1].type == "paragraph_open"
                     and tokens[i - 1].level == 0)
            if images and not (alone and figures_ok):
                errors.add(path, "an image must be a figure: alone in its own paragraph inside a content section"
                                 " or '## In finance'")
            paragraph = fingerprint(tok.content)
            for c in walk_inline(tok.children):
                if c.type == "tsc_cite":
                    check_cite(c, paragraph, tok.content, lesson, sources, errors)
                elif c.type == "text":
                    check_prose(c.content, path, errors, f"section {section}")
                elif c.type in MATH:
                    lesson.math.append(c)
                elif c.type == "link_open":
                    check_link(c, lesson, published, errors)
            if images and alone and figures_ok:
                figure_token(tokens, i, images[0], path, content, errors)
        i += 1


def check_cite(tok, paragraph, text, lesson, sources, errors):
    key, locator = tok.meta["key"], tok.meta["locator"]
    if key not in sources:
        errors.add(lesson.path, f"citation [@{key}]: unknown source '{key}' (not in _sources.toml)")
        return
    if not locator:
        errors.add(lesson.path, f"citation [@{key}] needs a locator (page, section or theorem), as in [@{key}, p. 3]")
        return
    tok.meta["label"] = sources[key].label
    lesson.citations.append(Citation(key, locator, paragraph, text))


def check_link(tok, lesson, published, errors):
    path, href = lesson.path, tok.attrGet("href") or ""
    if href.startswith("lesson:"):
        lid = href[len("lesson:"):]
        if lid not in published:
            errors.add(path, f"link to {href!r}: no published lesson with that id")
        tok.attrSet("href", f"../{lid}/index.html")
    elif href.startswith("#"):
        lesson.fragments.append(href[1:])
    elif not href.startswith(("https://", "mailto:")):
        errors.add(path, f"link {href!r}: use lesson:<id>, #<heading-id>, https:// or mailto:")


def figure_token(tokens, i, image, path, content, errors):
    """Replace the paragraph holding a lone image with one 'tsc_figure' token."""
    src = image.attrGet("src") or ""
    mm = FIGURE.fullmatch(src)
    if not mm:
        errors.add(path, f"figure {src!r}: must be figures/<name>.svg")
        return
    if not (content / "figures" / f"{mm.group(1)}.svg").exists():
        errors.add(path, f"missing figure {show(content / 'figures' / (mm.group(1) + '.svg'))}")
    if not image.content.strip():
        errors.add(path, f"figure {src!r} has no caption (the image alt text)")
    fig = Token("tsc_figure", "", 0)
    fig.meta = {"name": mm.group(1), "caption": image.children or []}
    fig.block = True
    tokens[i - 1:i + 2] = [fig, Token("tsc_skip", "", 0), Token("tsc_skip", "", 0)]


def esc(text):
    return html.escape(text, quote=True)


LIVE_KEYS = {"component", "sample_minutes", "series", "pairs", "w", "initial"}
LIVE_SUFFIX = ".live.json"
LIVE_MAX_SAMPLES = 48  # budget: 48 by 48 = 2,304 cells


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def load_live(path, errors):
    """Read and validate the data file of a live figure. Returns the dict, or None after reporting every problem."""
    bad = len(errors)

    def err(field, msg):
        errors.add(path, f"{field}: {msg}")

    try:
        data = json.loads(path.read_text())
    except ValueError as e:
        err("json", f"not valid JSON ({e})")
        return None
    if not isinstance(data, dict):
        err("json", "must be an object")
        return None
    for k in sorted(set(data) - LIVE_KEYS):
        err("keys", f"unexpected key {k!r}")
    for k in sorted(LIVE_KEYS - set(data)):
        err("keys", f"missing key {k!r}")
    if len(errors) > bad:
        return None
    if data["component"] != "dtw":
        err("component", f"{data['component']!r} is not a known component (only 'dtw')")
    sm = data["sample_minutes"]
    if not _is_int(sm) or sm <= 0:
        err("sample_minutes", "must be a positive integer")
    series, n = data["series"], None
    if not isinstance(series, dict) or not series:
        err("series", "must be a non-empty object")
        series = {}
    for name, row in series.items():
        if not re.fullmatch(r"[a-z0-9]+", name):
            err("series", f"name {name!r} must match [a-z0-9]+")
        field = f"series.{name}"
        if not isinstance(row, list) or not row or not all(_is_number(v) for v in row):
            err(field, "must be a non-empty list of finite numbers")
            continue
        if len(row) > LIVE_MAX_SAMPLES:
            err(field, f"{len(row)} samples, at most {LIVE_MAX_SAMPLES}")
        if n is None:
            n = len(row)
        elif len(row) != n:
            err(field, f"{len(row)} samples, the other rows have {n}")
    pairs = data["pairs"]
    if not isinstance(pairs, list) or not pairs:
        err("pairs", "must be a non-empty list")
        pairs = []
    for k, pair in enumerate(pairs):
        if (not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, str) for x in pair)
                or pair[0] == pair[1]):
            err(f"pairs[{k}]", "must be two distinct series names")
        elif any(x not in series for x in pair):
            err(f"pairs[{k}]", f"names a series that does not exist: {pair}")
    w = data["w"]
    if not isinstance(w, dict) or set(w) != {"min", "max", "initial", "none"}:
        err("w", "must be an object with exactly min, max, initial, none")
    else:
        top = None if n is None else n - 1
        if not _is_int(w["min"]) or w["min"] < 0:
            err("w.min", "must be an integer >= 0")
        if not _is_int(w["max"]) or (_is_int(w["min"]) and w["max"] < w["min"]):
            err("w.max", "must be an integer >= w.min")
        elif top is not None and w["max"] > top:
            err("w.max", f"{w['max']} is above the series length - 1 = {top}")
        if not _is_int(w["initial"]) or not (_is_int(w["min"]) and _is_int(w["max"]) and w["min"] <= w["initial"] <= w["max"]):
            err("w.initial", "must be an integer in [w.min, w.max]")
        if not isinstance(w["none"], bool):
            err("w.none", "must be true or false")
    init = data["initial"]
    if not isinstance(init, dict) or set(init) != {"pair"}:
        err("initial", "must be an object with exactly pair")
    elif not _is_int(init["pair"]) or not 0 <= init["pair"] < len(pairs):
        err("initial.pair", f"must be an index into pairs (0 to {len(pairs) - 1})")
    return None if len(errors) > bad else data
