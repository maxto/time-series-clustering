"""Sources, citations and review records.

_sources.toml is the registry of cited works, _reviews.toml records who reviewed which text.
A review record names the exact text it approved by fingerprint, so any edit reopens it.
"""

import datetime
import hashlib
import json
import re
import tomllib
from dataclasses import dataclass, field

TOPICS = ("survey", "compare", "group", "validate", "finance", "software")
KEY = r"[a-z0-9-]+"
CITE = re.compile(rf"\[@({KEY})(?:,\s*([^\]]+))?\]")


FP_VERSION = "tsc-fp-v2"


def normalise(text):
    """Line endings only: every other character, whitespace included, is part of the approved text."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def fingerprint(text):
    """sha256 of the version tag, a newline and the text. Changing the rule means a new tag, which reopens every record."""
    return hashlib.sha256(f"{FP_VERSION}\n{normalise(text)}".encode("utf-8")).hexdigest()[:16]


def fingerprint_data(obj):
    """Fingerprint of a structured value: canonical JSON, so field boundaries cannot collide."""
    return fingerprint(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


@dataclass
class Source:
    key: str
    authors: list
    year: int
    title: str
    venue: str
    topics: list
    doi: str = None
    arxiv: str = None
    ssrn: str = None
    url: str = None

    @property
    def label(self):
        names = [a.split(",")[0].strip() for a in self.authors]
        if len(names) == 1:
            who = names[0]
        elif len(names) == 2:
            who = f"{names[0]} and {names[1]}"
        else:
            who = f"{names[0]} et al."
        return f"{who} ({self.year})"

    @property
    def full_authors(self):
        names = []
        for a in self.authors:
            family, sep, given = a.partition(",")
            names.append(f"{given.strip()} {family.strip()}" if sep else family.strip())
        if len(names) <= 2:
            return " and ".join(names)
        return ", ".join(names[:-1]) + f", and {names[-1]}"

    @property
    def links(self):
        out = []
        if self.doi:
            out.append(("Publisher", f"https://doi.org/{self.doi}"))
        if self.arxiv:
            out.append(("arXiv", f"https://arxiv.org/abs/{self.arxiv}"))
        if self.ssrn:
            out.append(("SSRN", f"https://papers.ssrn.com/sol3/papers.cfm?abstract_id={self.ssrn}"))
        if self.url:
            out.append(("Authors' page", self.url))
        return out

    @property
    def identity(self):
        return fingerprint_data({"doi": self.doi, "arxiv": self.arxiv, "ssrn": self.ssrn, "url": self.url,
                                 "title": self.title, "year": self.year, "authors": self.authors, "venue": self.venue})


@dataclass
class Citation:
    key: str
    locator: str
    paragraph: str  # fingerprint of the paragraph text that holds the citation
    text: str = ""  # that paragraph's source text, kept for review.py show (a caption paragraph is gone from the tokens)


@dataclass
class Reviews:
    lessons: dict = field(default_factory=dict)  # lesson id -> {fingerprint}
    citations: set = field(default_factory=set)  # (lesson, key, locator, paragraph, identity)
    items: dict = field(default_factory=dict)  # name -> {fingerprint}
    fits: dict = field(default_factory=dict)  # (question, item) -> {fingerprint}
    questions: dict = field(default_factory=dict)  # public question id -> {fingerprint}
    sectors: dict = field(default_factory=dict)  # sector id -> {fingerprint}
    branches: dict = field(default_factory=dict)  # branch id -> {fingerprint}


def read_toml(path, errors):
    if not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        errors.add(path, f"invalid TOML: {e}")
        return {}


def load_sources(content, errors):
    path = content / "_sources.toml"
    sources = {}
    for key, raw in read_toml(path, errors).items():
        if not re.fullmatch(KEY, key) or not isinstance(raw, dict):
            errors.add(path, f"bad source key {key!r} (lowercase letters, digits, hyphens, one table per source)")
            continue
        known = {"authors", "year", "title", "venue", "topics", "doi", "arxiv", "ssrn", "url", "manual"}
        for name in sorted(set(raw) - known):
            errors.add(path, f"source {key!r}: unknown field {name!r}")
        ok = True
        for name, kind in (("authors", list), ("year", int), ("title", str), ("venue", str), ("topics", list)):
            value = raw.get(name)
            if not isinstance(value, kind) or isinstance(value, bool) or not value:
                errors.add(path, f"source {key!r}: missing or invalid {name!r}")
                ok = False
        if not ok:
            continue
        if not all(isinstance(a, str) and a.strip() for a in raw["authors"]):
            errors.add(path, f"source {key!r}: authors are non-empty strings")
        for topic in raw["topics"]:
            if topic not in TOPICS:
                errors.add(path, f"source {key!r}: unknown topic {topic!r} (one of: {', '.join(TOPICS)})")
        links = {n: raw.get(n) for n in ("doi", "arxiv", "ssrn", "url")}
        for name, value in links.items():
            if value is not None and not (isinstance(value, str) and value.strip()):
                errors.add(path, f"source {key!r}: {name!r} must be a non-empty string")
                links[name] = None
        if not any(links.values()):
            errors.add(path, f"source {key!r} has no link (doi, arxiv, ssrn or url)")
        if "manual" in raw:
            m = raw["manual"]
            if not isinstance(m, dict):
                errors.add(path, f"source {key!r}: manual must be a table with date, by, what")
            else:
                for name in sorted(set(m) - {"date", "by", "what"}):
                    errors.add(path, f"source {key!r}: unknown manual field {name!r}")
                if not isinstance(m.get("date"), datetime.date) or isinstance(m.get("date"), datetime.datetime):
                    errors.add(path, f"source {key!r}: manual.date must be a TOML date (YYYY-MM-DD)")
                for name in ("by", "what"):
                    if not isinstance(m.get(name), str) or not m[name].strip():
                        errors.add(path, f"source {key!r}: manual.{name} must be a non-empty string")
        if links["url"] and not links["url"].startswith("https://"):
            errors.add(path, f"source {key!r}: url must start with https://")
        sources[key] = Source(key, raw["authors"], raw["year"], raw["title"], raw["venue"], raw["topics"], **links)
    return sources


def load_reviews(content, errors):
    path = content / "_reviews.toml"
    data = read_toml(path, errors)
    reviews = Reviews()
    shapes = {"lesson": ("id", "fingerprint"), "citation": ("lesson", "key", "locator", "paragraph", "identity"),
              "item": ("name", "fingerprint"), "fit": ("question", "item", "fingerprint"),
              "question": ("id", "fingerprint"), "sector": ("id", "fingerprint"), "branch": ("id", "fingerprint")}
    for table in sorted(set(data) - set(shapes)):
        errors.add(path, f"unknown table [[{table}]]")
    for table, fields in shapes.items():
        for rec in data.get(table, []):
            missing = [f for f in (*fields, "by", "date") if f not in rec]
            if missing:
                errors.add(path, f"[[{table}]] record without {', '.join(missing)}: {rec}")
                continue
            if table == "lesson":
                reviews.lessons.setdefault(rec["id"], set()).add(rec["fingerprint"])
            elif table == "citation":
                reviews.citations.add(tuple(rec[f] for f in fields))
            elif table == "item":
                reviews.items.setdefault(rec["name"], set()).add(rec["fingerprint"])
            elif table == "question":
                reviews.questions.setdefault(rec["id"], set()).add(rec["fingerprint"])
            elif table == "sector":
                reviews.sectors.setdefault(rec["id"], set()).add(rec["fingerprint"])
            elif table == "branch":
                reviews.branches.setdefault(rec["id"], set()).add(rec["fingerprint"])
            else:
                reviews.fits.setdefault((rec["question"], rec["item"]), set()).add(rec["fingerprint"])
    return reviews


def citation_text(c):
    return f"[@{c.key}, {c.locator}]"


def check_reviews(lessons, sources, reviews, errors, allow_drafts=False):
    """The review gate: a record for the lesson text and one for every citation. A release build
    rejects a missing record. A preview (allow_drafts) marks the lesson as a draft instead."""
    for lesson in lessons:
        lid = lesson.entry.id
        missing = []
        if lesson.fingerprint not in reviews.lessons.get(lid, set()):
            missing.append(f"lesson {lid!r} has no review for its current text"
                           f" (fingerprint {lesson.fingerprint}, see scripts/review.py)")
        for c in lesson.citations:
            if c.key in sources and (lid, c.key, c.locator, c.paragraph, sources[c.key].identity) not in reviews.citations:
                missing.append(f"citation {citation_text(c)} has no review record"
                               f" (paragraph {c.paragraph}, see scripts/review.py)")
        if missing and allow_drafts:
            lesson.draft = True
        for line in [] if allow_drafts else missing:
            errors.add(lesson.path, line)


def cited_sources(lessons):
    """Source key -> ids of the lessons citing it, in the order of the lessons given."""
    out = {}
    for lesson in lessons:
        for c in lesson.citations:
            ids = out.setdefault(c.key, [])
            if lesson.entry.id not in ids:
                ids.append(lesson.entry.id)
    return out
