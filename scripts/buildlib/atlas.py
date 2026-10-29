"""The map of the field and the sector questions, with review state derived from records.

_map.toml holds branches, families and items, _sectors.toml holds sectors, their questions and
the fits of items to a question. There is no status field: an item or a fit is reviewed when
_reviews.toml holds a record for its current fingerprint, so editing it makes it a draft again.
A reviewed item also needs, for each factual field, a located source that is not a candidate.
"""

import math
import re
from dataclasses import dataclass, field

from .cite import fingerprint, read_toml
from .content import SECTORS, check_prose, slug

IGNORE_TAGS = ("level", "scale", "shift", "warp", "noise", "length")
NEED_TAGS = ("matrix", "similarity", "vectors", "series", "labels")
MARKS = ("good", "avoid")
BRANCHES = ("compare", "group", "validate")
BASE_SUPPORTS = ("does", "python", "r")


@dataclass
class Ref:
    key: str
    locator: str
    supports: str
    candidate: bool = False

    def line(self):
        return f"ref|{self.key}|{self.locator}|{self.supports}|{'candidate' if self.candidate else 'confirmed'}"


@dataclass
class Tag:
    tag: str
    cond: str = ""
    sources: list = field(default_factory=list)


@dataclass
class Item:
    id: str
    name: str
    does: str
    ignores: list = field(default_factory=list)
    needs: list = field(default_factory=list)
    cond: str = ""
    python: str = ""
    r: str = ""
    sources: list = field(default_factory=list)
    reviewed: bool = False
    branch: str = ""
    family: str = ""
    recorded: bool = False
    gaps: list = field(default_factory=list)

    def all_refs(self):
        return [*self.sources, *(r for t in (*self.ignores, *self.needs) for r in t.sources)]

    @property
    def fingerprint(self):
        lines = [self.name, self.does]
        for kind, tags in (("ignores", self.ignores), ("needs", self.needs)):
            for t in tags:
                lines.append(f"{kind}|{t.tag}|{t.cond}")
                lines += [r.line() for r in t.sources]
        lines += [self.cond, self.python, self.r, *(r.line() for r in self.sources)]
        return fingerprint("\n".join(lines))

    def required_support(self):
        out = ["does"]
        out += [f for f in ("python", "r") if getattr(self, f)]
        out += [f"ignores:{t.tag}" for t in self.ignores] + [f"needs:{t.tag}" for t in self.needs]
        return out


@dataclass
class Family:
    name: str
    lesson: str = None
    items: list = field(default_factory=list)


@dataclass
class Branch:
    id: str
    name: str
    sub: str
    families: list = field(default_factory=list)


@dataclass
class Fit:
    item: str
    mark: str
    reason: str
    cond: str = ""
    sources: list = field(default_factory=list)
    reviewed: bool = False
    question: str = ""
    recorded: bool = False
    gaps: list = field(default_factory=list)

    @property
    def fingerprint(self):
        lines = [self.question, self.item, self.mark, self.reason, self.cond, *(r.line() for r in self.sources)]
        return fingerprint("\n".join(lines))


@dataclass
class Question:
    id: str
    text: str
    starts: list = field(default_factory=list)
    fits: list = field(default_factory=list)


@dataclass
class Sector:
    id: str
    name: str
    about: str
    curve: list
    questions: list = field(default_factory=list)


@dataclass
class Atlas:
    branches: list
    sectors: list

    def items(self):
        return [it for b in self.branches for f in b.families for it in f.items]

    def fits(self):
        return [ft for s in self.sectors for q in s.questions for ft in q.fits]

    def draft_items(self):
        out = []
        for it in self.items():
            if not it.recorded:
                out.append(f"item '{it.name}' is draft: no review record for its current text"
                           f" (fingerprint {it.fingerprint}, see scripts/review.py show-map)")
            elif it.gaps:
                out.append(f"item '{it.name}' is draft: no located confirmed source for {', '.join(it.gaps)}")
        return out

    def draft_fits(self):
        out = []
        for ft in self.fits():
            if not ft.recorded:
                out.append(f"fit {ft.question} / '{ft.item}' is draft: no review record for its current text"
                           f" (fingerprint {ft.fingerprint}, see scripts/review.py show-map)")
            elif ft.gaps:
                out.append(f"fit {ft.question} / '{ft.item}' is draft: no located confirmed source for the fit")
        return out

    def drafts(self):
        return [*self.draft_items(), *self.draft_fits()]


class Reader:
    """Typed access to TOML tables that reports every problem against one file."""

    def __init__(self, path, errors):
        self.path, self.errors = path, errors

    def err(self, msg):
        self.errors.add(self.path, msg)

    def table(self, raw, where, allowed, required=()):
        if not isinstance(raw, dict):
            self.err(f"{where}: expected a table")
            return None
        for name in sorted(set(raw) - set(allowed)):
            self.err(f"{where}: unknown field {name!r}")
        missing = [n for n in required if n not in raw]
        for name in missing:
            self.err(f"{where}: missing field {name!r}")
        return None if missing else raw

    def text(self, raw, name, where, required=False):
        value = raw.get(name, "")
        if not isinstance(value, str):
            self.err(f"{where}: {name!r} must be a string")
            return ""
        if required and not value.strip():
            self.err(f"{where}: {name!r} must not be empty")
        check_prose(value, self.path, self.errors, f"{where} {name}")
        return value

    def refs(self, raw, where, sources, valid, fixed=None):
        out = []
        data = raw.get("sources", [])
        if not isinstance(data, list):
            self.err(f"{where}: 'sources' must be a list")
            return out
        for i, r in enumerate(data):
            w = f"{where} source {i + 1}"
            r = self.table(r, w, ("key", "locator", "supports", "candidate"), ("key",))
            if r is None:
                continue
            key = r["key"]
            if not isinstance(key, str) or key not in sources:
                self.err(f"{w}: key {key!r} is not in _sources.toml")
            supports = fixed or r.get("supports", "")
            if not isinstance(supports, str) or supports not in valid:
                self.err(f"{w}: supports {supports!r} is not one of: {', '.join(valid)}")
            candidate = r.get("candidate", False)
            if not isinstance(candidate, bool):
                self.err(f"{w}: 'candidate' must be true or false")
                candidate = False
            out.append(Ref(str(key), self.text(r, "locator", w), str(supports), candidate))
        return out


def has_support(refs, supports):
    return any(r.supports == supports and not r.candidate and r.locator.strip() for r in refs)


def load_tags(rd, raw, kind, vocabulary, where, sources):
    tags = []
    data = raw.get(kind, [])
    if not isinstance(data, list):
        rd.err(f"{where}: {kind!r} must be a list")
        return tags
    for t in data:
        t = rd.table(t, f"{where} {kind}", ("tag", "cond", "sources"), ("tag",))
        if t is None:
            continue
        name = t["tag"]
        if name not in vocabulary:
            rd.err(f"{where}: unknown tag {name!r} in {kind} (one of: {', '.join(vocabulary)})")
        w = f"{where} {kind} {name}"
        cond = rd.text(t, "cond", w)
        tags.append(Tag(str(name), cond, rd.refs(t, w, sources, (f"{kind}:{name}",), f"{kind}:{name}")))
    return tags


def load_map(content, sources, course, errors):
    path = content / "_map.toml"
    rd = Reader(path, errors)
    data = read_toml(path, errors)
    rd.table(data, "file", ("branch",))
    branches, names, ids = [], {}, {}
    for b in data.get("branch", []):
        b = rd.table(b, "branch", ("id", "name", "sub", "family"), ("id", "name"))
        if b is None:
            continue
        if b["id"] not in BRANCHES:
            rd.err(f"branch id {b['id']!r} is not one of: {', '.join(BRANCHES)}")
        if any(x.id == b["id"] for x in branches):
            rd.err(f"branch {b['id']!r} appears twice")
        branch = Branch(str(b["id"]), rd.text(b, "name", f"branch {b['id']}", True), rd.text(b, "sub", f"branch {b['id']}"))
        branches.append(branch)
        for f in b.get("family", []):
            f = rd.table(f, f"branch {branch.id} family", ("name", "lesson", "item"), ("name",))
            if f is None:
                continue
            fw = f"family {f['name']!r}"
            lesson = f.get("lesson") or None
            if lesson is not None and lesson not in [e.id for e in course.entries]:
                rd.err(f"{fw}: lesson {lesson!r} is not listed in _course.md")
            family = Family(rd.text(f, "name", fw, True), lesson)
            branch.families.append(family)
            for raw in f.get("item", []):
                raw = rd.table(raw, f"{fw} item", ("name", "does", "ignores", "needs", "cond", "python", "r", "sources"),
                               ("name", "does"))
                if raw is None:
                    continue
                name = str(raw["name"])
                w = f"item {name!r}"
                if branch.id == "compare" and "needs" in raw:
                    rd.err(f"{w}: 'needs' is for group and validate items, not the compare branch")
                if branch.id != "compare" and "ignores" in raw:
                    rd.err(f"{w}: 'ignores' is for the compare branch only")
                ignores = load_tags(rd, raw, "ignores", IGNORE_TAGS, w, sources)
                needs = load_tags(rd, raw, "needs", NEED_TAGS, w, sources)
                valid = (*BASE_SUPPORTS, *(f"ignores:{t.tag}" for t in ignores), *(f"needs:{t.tag}" for t in needs))
                item = Item(slug(name), rd.text(raw, "name", w, True), rd.text(raw, "does", w, True), ignores, needs,
                            rd.text(raw, "cond", w), rd.text(raw, "python", w), rd.text(raw, "r", w),
                            rd.refs(raw, w, sources, valid), branch=branch.id, family=family.name)
                if item.name in names:
                    rd.err(f"item '{item.name}' appears twice")
                elif item.id in ids:
                    rd.err(f"item '{item.name}' has the same id as '{ids[item.id]}'")
                names[item.name], ids[item.id] = item, item.name
                family.items.append(item)
    return branches, names


def load_sectors(content, sources, items, errors):
    path = content / "_sectors.toml"
    rd = Reader(path, errors)
    data = read_toml(path, errors)
    rd.table(data, "file", ("sector",))
    sectors, fit_keys = [], set()
    for s in data.get("sector", []):
        s = rd.table(s, "sector", ("id", "name", "about", "curve", "question"), ("id", "name", "curve"))
        if s is None:
            continue
        sid = str(s["id"])
        if sid not in SECTORS:
            rd.err(f"sector id {sid!r} is not one of: {', '.join(SECTORS)}")
        if any(x.id == sid for x in sectors):
            rd.err(f"sector {sid!r} appears twice")
        curve = s["curve"]
        if not (isinstance(curve, list) and curve and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                                           and math.isfinite(v) for v in curve)):
            rd.err(f"sector {sid!r}: 'curve' must be a non-empty list of finite numbers")
            curve = []
        sector = Sector(sid, rd.text(s, "name", f"sector {sid}", True), rd.text(s, "about", f"sector {sid}"),
                        [float(v) for v in curve])
        sectors.append(sector)
        for q in s.get("question", []):
            q = rd.table(q, f"sector {sid} question", ("id", "text", "starts", "fit"), ("id", "text"))
            if q is None:
                continue
            qid = f"{sid}/{q['id']}"
            if not re.fullmatch(r"[a-z0-9-]+", str(q["id"])):
                rd.err(f"question {qid!r}: the id is lowercase letters, digits and hyphens")
            if any(x.id == qid for x in sector.questions):
                rd.err(f"question {qid!r} appears twice")
            starts = q.get("starts", [])
            if not isinstance(starts, list) or not all(isinstance(x, str) for x in starts):
                rd.err(f"question {qid!r}: 'starts' must be a list of item names")
                starts = []
            for name in starts:
                if name not in items:
                    rd.err(f"question {qid!r}: unknown item {name!r} in starts")
            question = Question(qid, rd.text(q, "text", f"question {qid}", True), list(starts))
            sector.questions.append(question)
            for f in q.get("fit", []):
                f = rd.table(f, f"question {qid} fit", ("item", "mark", "reason", "cond", "sources"), ("item", "mark", "reason"))
                if f is None:
                    continue
                w = f"fit {qid} / {f['item']!r}"
                if f["item"] not in items:
                    rd.err(f"{w}: unknown item {f['item']!r}")
                if f["mark"] not in MARKS:
                    rd.err(f"{w}: unknown mark {f['mark']!r} (one of: {', '.join(MARKS)})")
                if (qid, f["item"]) in fit_keys:
                    rd.err(f"{w}: appears twice")
                fit_keys.add((qid, f["item"]))
                fit = Fit(str(f["item"]), str(f["mark"]), rd.text(f, "reason", w, True), rd.text(f, "cond", w),
                          rd.refs(f, w, sources, ("fit",), "fit"), question=qid)
                question.fits.append(fit)
    return sectors


def load_atlas(content, sources, reviews, course, errors):
    """The atlas with review state derived from reviews, or None when there is no _map.toml."""
    if not (content / "_map.toml").exists():
        if (content / "_sectors.toml").exists():
            errors.add(content / "_sectors.toml", "sectors without a _map.toml")
        return None
    branches, items = load_map(content, sources, course, errors)
    sectors = load_sectors(content, sources, items, errors)
    atlas = Atlas(branches, sectors)
    for it in atlas.items():
        it.recorded = it.fingerprint in reviews.items.get(it.name, set())
        it.gaps = [s for s in it.required_support() if not has_support(it.all_refs(), s)]
        it.reviewed = it.recorded and not it.gaps
    for ft in atlas.fits():
        ft.recorded = ft.fingerprint in reviews.fits.get((ft.question, ft.item), set())
        ft.gaps = [] if has_support(ft.sources, "fit") else ["fit"]
        ft.reviewed = ft.recorded and not ft.gaps
    return atlas
