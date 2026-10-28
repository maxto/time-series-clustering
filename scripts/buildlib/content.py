"""Read and validate the course content: _course.md, lesson files, sections, prose rules.

Every problem is collected as one line "<file>: <message>" in an Errors list, so one
build run reports all of them.
"""

import html
import json
import pathlib
import re
from dataclasses import dataclass, field

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.dollarmath import dollarmath_plugin

LESSON_KEYS = ("id", "module", "title", "kicker", "lede", "ignores", "keeps", "python", "r")
LIST_KEYS = ("ignores", "keeps", "python", "r")
PROSE_KEYS = ("title", "kicker", "lede", "ignores", "keeps")
SECTIONS = ("One line", "Lesson", "Common mistake", "In finance", "Measure card", "Check")
REQUIRED = ("One line", "Lesson", "Common mistake")
ONE_PARAGRAPH = ("One line", "Common mistake")
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


def markdown():
    md = MarkdownIt("commonmark", {"html": False})
    md.use(dollarmath_plugin, allow_labels=False, double_inline=True)
    return md


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
class Lesson:
    entry: Entry
    path: pathlib.Path
    meta: dict
    sections: dict  # section name -> tokens
    math: list = field(default_factory=list)  # math tokens, rendered in one batch later
    fragments: list = field(default_factory=list)  # "#id" link targets, checked against heading ids


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


def load_lessons(content, course, md, errors):
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
        lessons.append(load_lesson(path, entry, md, numbers, published, content, errors))
    for e in course.published():
        if e.id not in files:
            errors.add(content / "_course.md", f"published lesson {e.id!r} has no file {e.number:02d}-{e.id}.md")
    return [lesson for lesson in lessons if lesson]


def load_lesson(path, entry, md, numbers, published, content, errors):
    meta, body = split_front(path.read_text(), path, errors)
    for key in LESSON_KEYS:
        if key not in meta:
            errors.add(path, f"missing front matter key {key!r}")
        elif key not in LIST_KEYS and not meta[key]:
            errors.add(path, f"empty front matter key {key!r}")
    for key in sorted(set(meta) - set(LESSON_KEYS)):
        errors.add(path, f"unknown front matter key {key!r}")
    if meta.get("id", entry.id) != entry.id:
        errors.add(path, f"id {meta['id']!r} does not match the file name ({entry.id!r})")
    if meta.get("module", entry.module) != entry.module:
        errors.add(path, f"module {meta['module']!r} but _course.md lists {entry.id!r} under module {entry.module}")
    for key in LIST_KEYS:
        meta[key] = [v.strip() for v in meta.get(key, "").split(",") if v.strip()]
    for key in PROSE_KEYS:
        value = meta.get(key, "")
        check_prose(", ".join(value) if isinstance(value, list) else value, path, errors, key)

    body = NUMBER.sub(lambda m: numbers.get(m.group(1), path, errors), body)
    tokens = md.parse(body)
    sections = split_sections(tokens, path, errors)
    lesson = Lesson(entry, path, meta, sections)
    for name, toks in sections.items():
        check_tokens(toks, name, lesson, published, content, errors)
    ids = heading_ids(sections)
    for frag in lesson.fragments:
        if frag not in ids:
            errors.add(path, f"link '#{frag}': no heading with that id in this lesson"
                             f" (ids: {', '.join(sorted(ids)) or 'none'})")
    return lesson


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"


def heading_ids(sections):
    """Give every rendered heading a deterministic, unique id (slug of its text, then -2, -3...)."""
    ids = set()
    for name in SECTIONS:
        toks = sections.get(name, [])
        for i, tok in enumerate(toks):
            if tok.type != "heading_open":
                continue
            text = "".join(c.content for c in walk_inline(toks[i + 1].children) if c.type in ("text", "code_inline"))
            base, n = slug(text), 1
            hid = base
            while hid in ids:
                n += 1
                hid = f"{base}-{n}"
            ids.add(hid)
            tok.attrSet("id", hid)
    return ids


def split_sections(tokens, path, errors):
    """Top-level '## Name' headings split the body. A '##' inside a code block is a fence token."""
    sections, order, current = {}, [], None
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == "heading_open" and tok.tag == "h2" and tok.level == 0:
            name = tokens[i + 1].content.strip()
            if name not in SECTIONS:
                errors.add(path, f"unknown section '## {name}' (allowed: {', '.join(SECTIONS)})")
            elif name in sections:
                errors.add(path, f"section '## {name}' appears twice")
            current = name
            sections.setdefault(name, [])
            order.append(name)
            i += 3
            continue
        if tok.type == "heading_open" and tok.tag == "h1":
            errors.add(path, "'# ' headings are not allowed in a lesson (the title comes from the front matter)")
        if current is None:
            errors.add(path, "text before the first '## ' section")
            current = "_before"
            sections["_before"] = []
        sections[current].append(tok)
        i += 1
    sections.pop("_before", None)
    known = [n for n in order if n in SECTIONS]
    if known != sorted(known, key=SECTIONS.index):
        errors.add(path, f"sections out of order: {', '.join(known)} (expected order: {', '.join(SECTIONS)})")
    for name in REQUIRED:
        if name not in sections:
            errors.add(path, f"missing section '## {name}'")
    for name in ONE_PARAGRAPH:
        toks = sections.get(name)
        if toks is not None and [t.type for t in toks] != ["paragraph_open", "inline", "paragraph_close"]:
            errors.add(path, f"section '## {name}' must be exactly one paragraph")
    return {n: t for n, t in sections.items() if n in SECTIONS}


def check_tokens(tokens, section, lesson, published, content, errors):
    """Prose rules, math collection, links and figures for the tokens of one section."""
    path = lesson.path
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type in MATH:
            lesson.math.append(tok)
        if tok.type == "inline":
            images = [c for c in walk_inline(tok.children) if c.type == "image"]
            alone = (len(tok.children) == 1 and images and i > 0 and tokens[i - 1].type == "paragraph_open"
                     and tokens[i - 1].level == 0)
            if images and not (alone and section == "Lesson"):
                errors.add(path, "an image must be a figure: alone in its own paragraph inside '## Lesson'")
            for c in walk_inline(tok.children):
                if c.type == "text":
                    check_prose(c.content, path, errors, f"section {section}")
                elif c.type in MATH:
                    lesson.math.append(c)
                elif c.type == "link_open":
                    check_link(c, lesson, published, errors)
            if images and alone and section == "Lesson":
                figure_token(tokens, i, images[0], path, content, errors)
        i += 1


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
