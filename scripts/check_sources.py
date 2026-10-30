"""Check the identifiers of content/_sources.toml against Crossref and arXiv.

Network script, never called by the build. Writes content/_sources-check.json and prints one
line per source. A DOI is checked through Crossref, an arXiv id through the arXiv API: the
normalised title and the year are compared. A year difference between a preprint and its
publication is reported as a mismatch with both values for a person to judge, never fixed by
editing the registry. Outcomes: matched, mismatch, unavailable, manual-needed. SSRN ids and author
URLs are manual-needed, and a source with a valid `manual` record (date, by, what) is listed as
manually checked in the summary, not given a fifth outcome. A Crossref 404 and any network or
parse failure are unavailable. Exit 1 only on a mismatch. The JSON file is an audit trail.

Usage: uv run python scripts/check_sources.py [--content DIR]
"""

import argparse
import datetime
import http.client
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
UA = "time-series-clustering-source-check (https://github.com/maxto/time-series-clustering)"
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
        parts = (msg.get("issued") or {}).get("date-parts") or [[None]]
        return compare(src, (msg.get("title") or [""])[0], parts[0][0])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "unavailable", "not found on Crossref (DOI may be registered with another agency)"
        return "unavailable", f"HTTP {e.code}"
    except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError, IndexError, AttributeError) as e:
        return "unavailable", f"{type(e).__name__}: {e}"


def check_arxiv(src):
    try:
        root = ET.fromstring(fetch(f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(src.arxiv)}"))
        entry = root.find(f"{ATOM}entry")
        title = " ".join((entry.findtext(f"{ATOM}title") or "").split()) if entry is not None else ""
        if entry is None or not title or "/api/errors" in (entry.findtext(f"{ATOM}id") or ""):
            return "mismatch", "arXiv returned no entry for this id"
        return compare(src, title, int(entry.findtext(f"{ATOM}published")[:4]))
    except (OSError, http.client.HTTPException, ET.ParseError, ValueError, TypeError, AttributeError) as e:
        return "unavailable", f"{type(e).__name__}: {e}"


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
        manual = raw[key].get("manual")
        for name, value in (("ssrn", src.ssrn), ("url", src.url)):
            if value:
                entry[name] = "manual-needed"
                notes.append(f"{name} {value}: manual-needed")
                if not manual:
                    rest.append(f"{key} {name}: manual-needed")
        if manual:
            entry["manual"] = {k: str(v) for k, v in manual.items()}
            notes.append(f"manual check {manual['date']} by {manual['by']}: {manual['what']}")
        result[key] = entry
        print(f"{key}: " + " | ".join(notes))
    (args.content / "_sources-check.json").write_text(
        json.dumps({"run": datetime.date.today().isoformat(), "sources": result}, indent=2, ensure_ascii=False) + "\n")
    outcomes = [e[k] for e in result.values() for k in ("doi", "arxiv") if k in e]
    if outcomes and all(o == "unavailable" for o in outcomes):
        print("\nEverything was unavailable: no identifier was checked (network or service problem).")
    if rest:
        print("\nNot matched:")
        print("\n".join(f"  {r}" for r in rest))
    return 1 if mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
