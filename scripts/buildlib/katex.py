"""Render every math token of the build in one call to scripts/katex.mjs."""

import json
import subprocess


def render_math(lessons, root, errors):
    """Set token.meta["html"] on every math token. A TeX error is reported against its lesson file."""
    items = [(lesson, tok) for lesson in lessons for tok in lesson.math]
    if not items:
        return
    payload = [{"tex": tok.content.strip(), "display": tok.type != "math_inline"} for _, tok in items]
    try:
        run = subprocess.run(["node", str(root / "scripts" / "katex.mjs")], input=json.dumps(payload),
                             capture_output=True, text=True, cwd=root)
    except FileNotFoundError:
        errors.append("node not found: math needs Node.js and `npm install` (KaTeX)")
        return
    if run.returncode != 0:
        try:
            failed = json.loads(run.stderr)
        except json.JSONDecodeError:
            errors.append(f"scripts/katex.mjs failed: {run.stderr.strip()}")
            return
        for f in failed:
            lesson = items[f["index"]][0]
            errors.add(lesson.path, f"TeX error in ${f['tex']}$: {f['message']}")
        return
    for (_, tok), html in zip(items, json.loads(run.stdout)):
        tok.meta = {**(tok.meta or {}), "html": html}
