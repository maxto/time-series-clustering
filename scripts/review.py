"""Show and record review decisions for lessons and citations.

Usage:
  uv run python scripts/review.py show   --content DIR --lesson ID
  uv run python scripts/review.py record --content DIR --lesson ID --fingerprint F --by TEXT [--note TEXT]
  uv run python scripts/review.py record --content DIR --lesson ID --cite KEY --locator L --paragraph P --by TEXT

`show` prints the fingerprint of the lesson text and, for each citation, its locator, its
paragraph and the paragraph fingerprint, with whether a record already matches.
`record` appends a record to DIR/_reviews.toml only if the fingerprint given equals the current
one, so the reviewer approves exactly what they read. It records a review done by a person or a
model and verifies nothing else: the second-model review must be done before a record is written.
"""

import argparse
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from buildlib.cite import fingerprint, load_reviews, load_sources  # noqa: E402
from buildlib.content import Errors, load_course, load_lessons, markdown, walk_inline  # noqa: E402


def load(content, lid):
    errors = Errors()
    course = load_course(content, errors)
    sources = load_sources(content, errors)
    reviews = load_reviews(content, errors)
    lessons = load_lessons(content, course, markdown(), sources, errors)
    lesson = next((x for x in lessons if x.entry.id == lid), None)
    if errors or lesson is None:
        print("\n".join(errors) or f"no published lesson {lid!r}", file=sys.stderr)
        sys.exit(1)
    return lesson, sources, reviews


def paragraph_texts(lesson):
    """Paragraph fingerprint -> text, for the paragraphs holding a citation."""
    out = {}
    for b in lesson.blocks:
        for tok in b.tokens:
            if tok.type == "inline" and any(c.type == "tsc_cite" for c in walk_inline(tok.children)):
                out[fingerprint(tok.content)] = tok.content
    return out


def show(args):
    lesson, sources, reviews = load(args.content, args.lesson)
    done = "recorded" if lesson.fingerprint in reviews.lessons.get(args.lesson, set()) else "not recorded"
    print(f"lesson {args.lesson}")
    print(f"fingerprint: {lesson.fingerprint} ({done})")
    texts = paragraph_texts(lesson)
    for c in lesson.citations:
        have = (args.lesson, c.key, c.locator, c.paragraph, sources[c.key].identity) in reviews.citations
        print(f"citation {c.key} | {c.locator} | {c.paragraph} | {'recorded' if have else 'not recorded'}")
        print(f"  paragraph: {texts.get(c.paragraph, '')}")


def toml_value(v):
    return json.dumps(v, ensure_ascii=False)


def append(content, table, fields, args):
    fields = {**fields, "by": args.by, "date": datetime.date.today().isoformat()}
    if args.note:
        fields["note"] = args.note
    lines = [f"[[{table}]]"] + [f"{k} = {v if k == 'date' else toml_value(v)}" for k, v in fields.items()]
    path = content / "_reviews.toml"
    old = path.read_text() if path.exists() else ""
    path.write_text(old + ("\n" if old and not old.endswith("\n\n") else "") + "\n".join(lines) + "\n")


def record(args):
    lesson, sources, _ = load(args.content, args.lesson)
    if args.cite:
        match = [c for c in lesson.citations if (c.key, c.locator, c.paragraph) == (args.cite, args.locator, args.paragraph)]
        if not match:
            print(f"no citation [@{args.cite}, {args.locator}] with paragraph {args.paragraph} in {args.lesson!r} now", file=sys.stderr)
            return 1
        append(args.content, "citation", {"lesson": args.lesson, "key": args.cite, "locator": args.locator,
                                          "paragraph": args.paragraph, "identity": sources[args.cite].identity}, args)
    else:
        if args.fingerprint != lesson.fingerprint:
            print(f"fingerprint {args.fingerprint} is not the current one ({lesson.fingerprint}): the text changed", file=sys.stderr)
            return 1
        append(args.content, "lesson", {"id": args.lesson, "fingerprint": lesson.fingerprint}, args)
    print("recorded")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("show", "record"):
        p = sub.add_parser(name)
        p.add_argument("--content", type=pathlib.Path, required=True)
        p.add_argument("--lesson", required=True)
    rec = sub.choices["record"]
    rec.add_argument("--fingerprint")
    rec.add_argument("--cite")
    rec.add_argument("--locator")
    rec.add_argument("--paragraph")
    rec.add_argument("--by", required=True)
    rec.add_argument("--note")
    args = ap.parse_args()
    args.content = args.content.resolve()
    if args.cmd == "show":
        show(args)
        return 0
    if args.cite and not (args.locator and args.paragraph) or not args.cite and not args.fingerprint:
        ap.error("record needs --fingerprint, or --cite with --locator and --paragraph")
    return record(args)


if __name__ == "__main__":
    sys.exit(main())
