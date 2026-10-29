"""Show and record review decisions for lessons, citations, map items and sector fits.

Usage:
  uv run python scripts/review.py show   --content DIR --lesson ID
  uv run python scripts/review.py record --content DIR --lesson ID --fingerprint F --by TEXT [--note TEXT]
  uv run python scripts/review.py record --content DIR --lesson ID --cite KEY --locator L --paragraph P --by TEXT
  uv run python scripts/review.py show-map    --content DIR
  uv run python scripts/review.py record-item --content DIR --name NAME --fingerprint F --by TEXT [--note TEXT]
  uv run python scripts/review.py record-question --content DIR --id SECTOR/QUESTION --fingerprint F --by TEXT [--note TEXT]
  uv run python scripts/review.py record-sector --content DIR --id SECTOR --fingerprint F --by TEXT [--note TEXT]
  uv run python scripts/review.py record-branch --content DIR --id BRANCH --fingerprint F --by TEXT [--note TEXT]
  uv run python scripts/review.py record-fit  --content DIR --question Q --item NAME --fingerprint F --by TEXT [--note TEXT]

`show` prints the fingerprint of the lesson text and, for each citation, its locator, its
paragraph and the paragraph fingerprint, with whether a record already matches.
`record` appends a record to DIR/_reviews.toml only if the fingerprint given equals the current
one, so the reviewer approves exactly what they read. It records a review done by a person or a
model and verifies nothing else: the second-model review must be done before a record is written.
`show-map` lists every map item and sector fit with its fingerprint and whether a record matches.
`record-item`, `record-fit`, `record-question`, `record-sector` and `record-branch` refuse a fingerprint that is not the current one, like `record`.
"""

import argparse
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from buildlib.atlas import load_atlas  # noqa: E402
from buildlib.cite import load_reviews, load_sources  # noqa: E402
from buildlib.content import Errors, load_course, load_lessons, markdown  # noqa: E402


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


def load_map(content):
    errors = Errors()
    course = load_course(content, errors)
    sources = load_sources(content, errors)
    reviews = load_reviews(content, errors)
    atlas = load_atlas(content, sources, reviews, course, errors)
    if errors or atlas is None:
        print("\n".join(errors) or "no _map.toml", file=sys.stderr)
        sys.exit(1)
    return atlas


def show(args):
    lesson, sources, reviews = load(args.content, args.lesson)
    done = "recorded" if lesson.fingerprint in reviews.lessons.get(args.lesson, set()) else "not recorded"
    print(f"lesson {args.lesson}")
    print(f"fingerprint: {lesson.fingerprint} ({done})")
    for c in lesson.citations:
        have = (args.lesson, c.key, c.locator, c.paragraph, sources[c.key].identity) in reviews.citations
        print(f"citation {c.key} | {c.locator} | {c.paragraph} | {'recorded' if have else 'not recorded'}")
        print(f"  paragraph: {c.text}")


def show_map(args):
    atlas = load_map(args.content)
    for it in atlas.items():
        state = "reviewed" if it.reviewed else ("recorded, source gaps: " + ", ".join(it.gaps) if it.recorded else "draft")
        print(f"item {it.name} | {it.fingerprint} | {state}")
    for ft in atlas.fits():
        state = "reviewed" if ft.reviewed else ("recorded, source gaps" if ft.recorded else "draft")
        print(f"fit {ft.question} | {ft.item} | {ft.fingerprint} | {state}")
    for b in atlas.branches:
        print(f"branch {b.id} | {b.fingerprint} | {'reviewed' if b.recorded else 'draft'}")
    for s in atlas.sectors:
        print(f"sector {s.id} | {s.fingerprint} | {'reviewed' if s.recorded else 'draft'}")
    for q in atlas.questions():
        print(f"question {q.id} | {q.fingerprint} | {'reviewed' if q.recorded else 'draft'}")


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


def record_map(args):
    atlas = load_map(args.content)
    if args.cmd == "record-item":
        found = next((it for it in atlas.items() if it.name == args.name), None)
        what, fields = f"item {args.name!r}", {"name": args.name}
    elif args.cmd == "record-question":
        found = next((q for q in atlas.questions() if q.id == args.id), None)
        what, fields = f"question {args.id!r}", {"id": args.id}
    elif args.cmd == "record-branch":
        found = next((b for b in atlas.branches if b.id == args.id), None)
        what, fields = f"branch {args.id!r}", {"id": args.id}
    elif args.cmd == "record-sector":
        found = next((s for s in atlas.sectors if s.id == args.id), None)
        what, fields = f"sector {args.id!r}", {"id": args.id}
    else:
        found = next((ft for ft in atlas.fits() if (ft.question, ft.item) == (args.question, args.item)), None)
        what, fields = f"fit {args.question} / {args.item!r}", {"question": args.question, "item": args.item}
    if found is None:
        print(f"no {what} in the map now", file=sys.stderr)
        return 1
    if args.fingerprint != found.fingerprint:
        print(f"fingerprint {args.fingerprint} is not the current one ({found.fingerprint}): the text changed", file=sys.stderr)
        return 1
    table = {"record-item": "item", "record-fit": "fit", "record-question": "question", "record-sector": "sector", "record-branch": "branch"}[args.cmd]
    append(args.content, table, {**fields, "fingerprint": found.fingerprint}, args)
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
    sm = sub.add_parser("show-map")
    sm.add_argument("--content", type=pathlib.Path, required=True)
    for name in ("record-item", "record-fit", "record-question", "record-sector", "record-branch"):
        p = sub.add_parser(name)
        p.add_argument("--content", type=pathlib.Path, required=True)
        p.add_argument("--fingerprint", required=True)
        p.add_argument("--by", required=True)
        p.add_argument("--note")
    sub.choices["record-item"].add_argument("--name", required=True)
    sub.choices["record-question"].add_argument("--id", required=True)
    sub.choices["record-sector"].add_argument("--id", required=True)
    sub.choices["record-branch"].add_argument("--id", required=True)
    sub.choices["record-fit"].add_argument("--question", required=True)
    sub.choices["record-fit"].add_argument("--item", required=True)
    args = ap.parse_args()
    args.content = args.content.resolve()
    if args.cmd == "show-map":
        show_map(args)
        return 0
    if args.cmd in ("record-item", "record-fit", "record-question", "record-sector", "record-branch"):
        return record_map(args)
    if args.cmd == "show":
        show(args)
        return 0
    if args.cite and not (args.locator and args.paragraph) or not args.cite and not args.fingerprint:
        ap.error("record needs --fingerprint, or --cite with --locator and --paragraph")
    return record(args)


if __name__ == "__main__":
    sys.exit(main())
