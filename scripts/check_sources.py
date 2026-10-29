"""Check the identifiers of content/_sources.toml against Crossref and arXiv.

Network script, never called by the build. Writes content/_sources-check.json and prints one
line per source. A DOI is checked through Crossref, an arXiv id through the arXiv API: the
normalised title and the year are compared. A year difference between a preprint and its
publication is reported as a mismatch with both values for a person to judge, never fixed by
editing the registry. SSRN ids and author URLs are manual-needed unless the source carries a
`manual` record (date, by, what). Exit 1 on any mismatch.

Usage: uv run python scripts/check_sources.py [--content DIR]
"""

import argparse
import datetime
import json
import pathlib
import re
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from buildlib.cite import load_sources  # noqa: E402
from buildlib.content import Errors  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = "time-series-clustering-source-check (mailto:m.todaro@macroasset.it)"
ATOM = "{http://www.w3.org/2005/Atom}"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def title_key(text):
    return re.sub(r"[^a-z0-9]+", " ", re.sub(r"<[^>]+>", "", text).lower()).strip()


def compare(src, title, year):
    problems = []
    if title_key(title) != title_key(src.title):
        problems.append(f"title registry {src.title!r} vs remote {title!r}")
    if year != src.year:
        problems.append(f"year registry {src.year} vs remote {year}")
    return ("mismatch", "; ".join(problems)) if problems else ("matched", f"{title!r} {year}")


def check_doi(src):
    try:
        msg = json.loads(fetch(f"https://api.crossref.org/works/{urllib.parse.quote(src.doi)}"))["message"]
    except urllib.error.HTTPError as e:
        return ("mismatch", f"Crossref HTTP {e.code}") if e.code == 404 else ("unavailable", f"HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return "unavailable", str(e)
    parts = (msg.get("issued") or {}).get("date-parts") or [[None]]
    return compare(src, (msg.get("title") or [""])[0], parts[0][0])


def check_arxiv(src):
    try:
        root = ET.fromstring(fetch(f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(src.arxiv)}"))
    except (urllib.error.URLError, TimeoutError, ET.ParseError) as e:
        return "unavailable", str(e)
    entry = root.find(f"{ATOM}entry")
    if entry is None or entry.find(f"{ATOM}title") is None or not entry.find(f"{ATOM}title").text.strip() or "/api/errors" in (entry.findtext(f"{ATOM}id") or ""):
        return "mismatch", "arXiv returned no entry for this id"
    title = " ".join(entry.findtext(f"{ATOM}title").split())
    return compare(src, title, int(entry.findtext(f"{ATOM}published")[:4]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", type=pathlib.Path, default=ROOT / "content")
    args = ap.parse_args()
    errors = Errors()
    sources = load_sources(args.content, errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    raw = tomllib.loads((args.content / "_sources.toml").read_text()) if (args.content / "_sources.toml").exists() else {}
    result, rest, mismatch = {}, [], False
    for key, src in sources.items():
        entry, notes = {}, []
        for name, value, check in (("doi", src.doi, check_doi), ("arxiv", src.arxiv, check_arxiv)):
            if value:
                outcome, detail = check(src)
                entry[name] = outcome
                notes.append(f"{name} {value}: {outcome} ({detail})")
                if outcome == "mismatch":
                    mismatch = True
                if outcome != "matched":
                    rest.append(f"{key} {name}: {outcome} ({detail})")
        for name, value in (("ssrn", src.ssrn), ("url", src.url)):
            if value:
                manual = raw[key].get("manual")
                entry[name] = "matched-manual" if manual else "manual-needed"
                notes.append(f"{name} {value}: {entry[name]}")
                if not manual:
                    rest.append(f"{key} {name}: manual-needed")
        if manual_rec := raw[key].get("manual"):
            entry["manual"] = {k: str(v) for k, v in manual_rec.items()}
        result[key] = entry
        print(f"{key}: " + " | ".join(notes))
    (args.content / "_sources-check.json").write_text(
        json.dumps({"run": datetime.date.today().isoformat(), "sources": result}, indent=2, ensure_ascii=False) + "\n")
    if rest:
        print("\nNot matched:")
        print("\n".join(f"  {r}" for r in rest))
    return 1 if mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
