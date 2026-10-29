"""Build validation on a copy of the smoke fixture (plan test group F).

Each test changes one lesson of a temporary copy and runs scripts/build.py on it.
The expected outcomes come from the content rules in the pilot plan (Task 5) and
the controller rulings R3 and R4: a TeX error, a semicolon in prose and a missing
generated number each fail the build, a semicolon in code or math does not.
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tomllib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from buildlib.cite import fingerprint  # noqa: E402

SMOKE = ROOT / "tests" / "fixtures" / "smoke"


@pytest.fixture
def content(tmp_path):
    target = tmp_path / "content"
    shutil.copytree(SMOKE, target)
    return target


def build(content, preview=False, dist=None):
    dist = dist or content.parent / ("preview" if preview else "dist")
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build.py"), "--content", str(content), "--dist", str(dist),
         *(["--preview"] if preview else [])],
        capture_output=True, text=True, cwd=ROOT,
    )


def mutate(path, old, new):
    """Replace the first `old` with `new` in a file, after asserting that `old` is there."""
    body = path.read_text()
    assert old in body, f"{old!r} not found in {path.name}: the mutation would do nothing"
    path.write_text(body.replace(old, new, 1))


def add_to_lesson(content, text):
    """Insert a block of Markdown at the top of the ## Engine features section of 01-alpha.md."""
    mutate(content / "01-alpha.md", "## Engine features\n\n", f"## Engine features\n\n{text}\n\n")


def block(path, title):
    """The text of the '## title' block, from its heading up to the next '## ' heading."""
    body = path.read_text()
    m = re.search(rf"(?ms)^## {re.escape(title)}\n.*?(?=^## |\Z)", body)
    assert m, f"no '## {title}' block in {path.name}"
    return m.group(0)


def move_block_before(path, title, before):
    text = block(path, title)
    mutate(path, text, "")
    mutate(path, f"## {before}\n", text + f"## {before}\n")


def remove_block(path, title):
    mutate(path, block(path, title), "")


def append_to_block(path, title, text):
    old = block(path, title)
    mutate(path, old, old.rstrip("\n") + f"\n\n{text}\n\n")


def add_section(path, title):
    mutate(path, "## A second section\n", f"## {title}\n\nAn added section.\n\n## A second section\n")


def add_subheading(path, title):
    mutate(path, "## A second section\n", f"### {title}\n\nUnder a repeated subheading.\n\n## A second section\n")


def review(content, *args):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "review.py"), *args, "--content", str(content)],
                          capture_output=True, text=True, cwd=ROOT)


def record_lesson(content, lesson_id):
    """Approve the current text of a lesson, the way a reviewer does: read its fingerprint, then record it."""
    shown = review(content, "show", "--lesson", lesson_id)
    m = re.search(r"^fingerprint: ([0-9a-f]{16})", shown.stdout, re.M)
    assert m, shown.stdout + shown.stderr
    done = review(content, "record", "--lesson", lesson_id, "--fingerprint", m.group(1), "--by", "test reviewer")
    assert done.returncode == 0, done.stdout + done.stderr


def edit_source(content, key, **changes):
    """Change fields of one entry of _sources.toml. A value of None removes the field."""
    path = content / "_sources.toml"
    data = tomllib.loads(path.read_text())
    assert key in data
    for name, value in changes.items():
        if value is None:
            data[key].pop(name, None)
        else:
            data[key][name] = value
    out = []
    for k, fields in data.items():
        out.append(f"[{k}]")
        out += [f"{name} = {json.dumps(value, ensure_ascii=False)}" for name, value in fields.items()]
        out.append("")
    path.write_text("\n".join(out))


def page(content, lesson_id):
    return (content.parent / "dist" / lesson_id / "index.html").read_text()


def test_smoke_fixture_builds(content):
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr


def test_invalid_tex_fails_and_names_the_lesson(content):
    add_to_lesson(content, r"Broken math $\frac{$ here.")
    result = build(content)
    assert result.returncode == 1
    assert "01-alpha.md" in result.stdout + result.stderr


def test_semicolon_in_prose_fails(content):
    add_to_lesson(content, "One clause; another clause.")
    result = build(content)
    assert result.returncode == 1
    out = result.stdout + result.stderr
    assert "01-alpha.md" in out and "semicolon" in out


def test_semicolon_in_code_and_math_passes(content):
    add_to_lesson(content, "Code `a; b` and math $a; b$ inline.\n\n```python\nx = 1; y = 2\n```\n\n$$\na; b\n$$")
    record_lesson(content, "alpha")
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr


def test_number_without_numbers_file_fails(content):
    add_to_lesson(content, "The distance is {{n:missing}}.")
    result = build(content)
    assert result.returncode == 1
    out = result.stdout + result.stderr
    assert "numbers.json" in out and "missing" in out


def test_number_with_missing_key_fails(content):
    (content / "figures" / "numbers.json").write_text(json.dumps({"present": 1.23}))
    add_to_lesson(content, "The distance is {{n:missing}}.")
    result = build(content)
    assert result.returncode == 1
    out = result.stdout + result.stderr
    assert "numbers.json" in out and "missing" in out


def test_number_is_substituted_from_numbers_file(content):
    (content / "figures" / "numbers.json").write_text(json.dumps({"present": 1.23}))
    add_to_lesson(content, "The distance is {{n:present}}.")
    record_lesson(content, "alpha")
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr
    page = (content.parent / "dist" / "alpha" / "index.html").read_text()
    assert "The distance is 1.23." in page and "{{n:" not in page


def test_fragment_link_without_heading_fails(content):
    add_to_lesson(content, "See [the missing part](#no-such-heading).")
    result = build(content)
    assert result.returncode == 1
    out = result.stdout + result.stderr
    assert "01-alpha.md" in out and "no-such-heading" in out


def test_v2_smoke_builds(content):
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr


def test_old_lesson_section_is_rejected(content):
    mutate(content / "01-alpha.md", "## Engine features", "## Lesson")
    assert "'## Lesson' was replaced by content sections" in build(content).stdout


def test_check_section_is_rejected(content):
    mutate(content / "03-gamma.md", "## Validity example", "## Check")
    assert "'## Check' is not used in the first phase" in build(content).stdout


def test_reserved_name_in_other_case_is_rejected(content):
    mutate(content / "01-alpha.md", "## A second section", "## code")
    assert "reserved block name" in build(content).stdout


def test_block_order_is_enforced(content):
    move_block_before(content / "01-alpha.md", "Common mistake", "Code")
    assert "out of order" in build(content).stdout


def test_lesson_needs_a_content_section(content):
    remove_block(content / "03-gamma.md", "Back to alpha")
    remove_block(content / "03-gamma.md", "Validity example")
    assert "at least one content section" in build(content).stdout


def test_unknown_sector_is_rejected(content):
    mutate(content / "01-alpha.md", "sector: energy", "sector: banking")
    assert "sector 'banking'" in build(content).stdout


def test_figure_in_finance_block_builds(content):
    append_to_block(content / "01-alpha.md", "In finance", "![Caption](figures/overview.svg)")
    record_lesson(content, "alpha")
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr


def test_heading_slug_equal_to_block_id_is_rejected(content):
    add_section(content / "01-alpha.md", "Measure card!")  # slug "measure-card"
    out = build(content).stdout
    assert "measure-card" in out and "block id" in out


def test_repeated_heading_gets_suffix(content):
    add_subheading(content / "01-alpha.md", "A subheading")
    record_lesson(content, "alpha")
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'id="a-subheading-2"' in page(content, "alpha")


def test_unknown_code_language_is_rejected(content):
    mutate(content / "01-alpha.md", "```r", "```julia")
    assert "julia" in build(content).stdout


def test_fingerprint_of_a_literal_text():  # expected value from: printf 'a b c' | sha256sum | cut -c1-16
    assert fingerprint("  a \n b\tc ") == "0e9f64031fcb2bc7"


def test_citation_renders_label_and_source_entry(content):
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr
    out = page(content, "alpha")
    assert '<a class="cite" href="#src-sakoe78" data-ref="sakoe78">Sakoe and Chiba (1978)</a>' in out
    assert 'id="src-sakoe78"' in out and "Hiroaki Sakoe and Seibi Chiba" in out


def test_unknown_citation_key_fails(content):
    add_to_lesson(content, "As shown by [@nobody99, p. 1].")
    assert "unknown source 'nobody99'" in build(content).stdout


def test_citation_without_locator_fails(content):
    add_to_lesson(content, "As shown by [@sakoe78].")
    assert "needs a locator" in build(content).stdout


def test_any_edit_reopens_the_lesson_review(content):
    mutate(content / "01-alpha.md", "A fixture lesson", "A fixture lesson,")  # front matter lede
    assert "lesson 'alpha' has no review for its current text" in build(content).stdout


def test_removed_citation_reopens_the_lesson_review(content):
    mutate(content / "01-alpha.md", "The band of [@sakoe78, sec. II] limited", "The band limited")
    assert "lesson 'alpha' has no review" in build(content).stdout


def test_citation_in_list_item_needs_its_record(content):
    add_to_lesson(content, "- a list item citing [@sakoe78, sec. II]")
    record_lesson(content, "alpha")  # lesson record only
    assert "citation [@sakoe78, sec. II] has no review record" in build(content).stdout


def test_citation_in_caption_needs_its_record(content):
    add_to_lesson(content, "![Band of [@sakoe78, sec. II]](figures/overview.svg)")
    record_lesson(content, "alpha")
    assert "has no review record" in build(content).stdout


def test_changed_source_identity_reopens(content):
    edit_source(content, "sakoe78", year=1979)
    assert "has no review" in build(content).stdout


def test_registry_rules(content):
    edit_source(content, "sakoe78", topics=["speech"])
    assert "unknown topic 'speech'" in build(content).stdout
    edit_source(content, "sakoe78", topics=["compare"], doi=None, arxiv=None, ssrn=None, url=None)
    assert "no link" in build(content).stdout


# --- map and sector data (Task 4) ---

def toml_value(v):
    if isinstance(v, list):
        return "[" + ", ".join(toml_value(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k} = {toml_value(x)}" for k, x in v.items()) + "}"
    return json.dumps(v, ensure_ascii=False)


def table_block(path, header, name_field, name):
    """The text of the [[header]] block whose name_field equals name, and its position."""
    body = path.read_text()
    for m in re.finditer(rf"(?ms)^\[\[{re.escape(header)}\]\]\n.*?(?=^\[\[|\Z)", body):
        if re.search(rf'^{name_field} = "{re.escape(name)}"$', m.group(0), re.M):
            return m.group(0)
    raise AssertionError(f"no [[{header}]] with {name_field} = {name!r} in {path.name}")


def set_fields(path, header, name_field, name, **fields):
    old = table_block(path, header, name_field, name)
    new = old
    for key, value in fields.items():
        line = f"{key} = {toml_value(value)}\n"
        if re.search(rf"^{key} = .*\n", new, re.M):
            new = re.sub(rf"^{key} = .*\n", lambda _: line, new, count=1, flags=re.M)
        else:
            new = re.sub(rf"^({name_field} = .*\n)", lambda m: m.group(1) + line, new, count=1, flags=re.M)
    mutate(path, old, new)


def edit_item(content, name, **fields):
    set_fields(content / "_map.toml", "branch.family.item", "name", name, **fields)


def edit_fit(content, question, **fields):
    sector, qid = question.split("/")
    path = content / "_sectors.toml"
    body = path.read_text()
    start = body.index(f'id = "{qid}"')
    m = re.search(r"(?ms)^\[\[sector\.question\.fit\]\]\n.*?(?=^\[\[|\Z)", body[start:])
    old = m.group(0)
    new = old
    for key, value in fields.items():
        new = re.sub(rf"^{key} = .*\n", lambda _: f"{key} = {toml_value(value)}\n", new, count=1, flags=re.M)
    assert new != old
    mutate(path, old, new)


def edit_ref(content, name, supports, locator):
    path = content / "_map.toml"
    old = table_block(path, "branch.family.item", "name", name)
    pattern = rf'locator = "[^"]*", supports = "{re.escape(supports)}"'
    assert re.search(pattern, old), f"no ref supporting {supports!r} in {name!r}"
    mutate(path, old, re.sub(pattern, lambda _: f'locator = "{locator}", supports = "{supports}"', old, count=1))


def duplicate_item(content, name):
    path = content / "_map.toml"
    old = table_block(path, "branch.family.item", "name", name)
    mutate(path, old, old + old.rstrip("\n") + "\n\n")


def drop_record(content, header, name_field, name):
    path = content / "_reviews.toml"
    mutate(path, table_block(path, header, name_field, name), "")


def remove_item_record(content, name):
    drop_record(content, "item", "name", name)


def remove_fit_record(content, question):
    drop_record(content, "fit", "question", question)


def rerecord_item(content, name):
    drop_record(content, "item", "name", name)
    shown = review(content, "show-map").stdout
    m = re.search(rf"^item {re.escape(name)} \| ([0-9a-f]{{16}})", shown, re.M)
    assert m, shown
    done = review(content, "record-item", "--name", name, "--fingerprint", m.group(1), "--by", "test reviewer")
    assert done.returncode == 0, done.stdout + done.stderr


def test_smoke_map_builds_in_both_modes(content):
    assert build(content).returncode == 0
    assert build(content, preview=True).returncode == 0


def test_release_refuses_an_unreviewed_item(content):
    remove_item_record(content, "Euclidean")
    result = build(content)
    assert result.returncode == 1
    assert "item 'Euclidean' is draft" in result.stdout


def test_editing_a_reviewed_item_makes_it_draft(content):
    edit_item(content, "Euclidean", does="Compares the same time steps, now edited.")
    assert "item 'Euclidean' is draft" in build(content).stdout
    assert build(content, preview=True).returncode == 0


def test_release_refuses_an_unreviewed_fit(content):
    remove_fit_record(content, "finance/same-dates")
    out = build(content).stdout
    assert "fit finance/same-dates / 'Correlation' is draft" in out


def test_preview_allows_drafts_and_marks_them(content):
    remove_item_record(content, "Euclidean")
    assert build(content, preview=True).returncode == 0
    home = (content.parent / "preview" / "index.html").read_text()
    assert 'class="draft-banner"' in home and 'data-build="preview"' in home
    assert not (content.parent / "dist").exists()


def test_release_pages_carry_the_build_mode(content):
    assert build(content).returncode == 0
    assert 'data-build="release"' in (content.parent / "dist" / "index.html").read_text()
    assert 'data-build="release"' in page(content, "alpha")
    assert "draft-banner" not in (content.parent / "dist" / "index.html").read_text()


def test_preview_never_writes_into_the_release_tree(content):
    def snapshot(target):
        return None if not target.exists() else sorted((str(f), f.stat().st_mtime_ns) for f in [target, *target.rglob("*")])

    for target in (ROOT / "dist", ROOT / "dist" / "preview"):
        before = snapshot(target)
        result = build(content, preview=True, dist=target)
        assert result.returncode == 1
        assert "a preview never writes into dist/" in result.stdout
        assert snapshot(target) == before


def test_duplicate_item_name_fails(content):
    duplicate_item(content, "Euclidean")
    assert "item 'Euclidean' appears twice" in build(content, preview=True).stdout


def test_fit_on_unknown_item_fails(content):
    edit_fit(content, "finance/same-dates", item="Nonexistent")
    assert "unknown item 'Nonexistent'" in build(content, preview=True).stdout


def test_reviewed_item_needs_located_support_for_each_field(content):
    edit_ref(content, "Euclidean", supports="python", locator="")
    rerecord_item(content, "Euclidean")
    out = build(content).stdout
    assert "item 'Euclidean' is draft" in out and "python" in out
    assert build(content, preview=True).returncode == 0


def test_tag_vocabulary(content):
    edit_item(content, "Euclidean", ignores=[{"tag": "amplitude", "cond": ""}])
    assert "unknown tag 'amplitude'" in build(content, preview=True).stdout


def test_semicolon_in_map_text_fails(content):
    edit_item(content, "Euclidean", does="One; two")
    assert "semicolon" in build(content, preview=True).stdout


def test_ref_key_must_be_in_the_registry(content):
    mutate(content / "_map.toml", 'key = "sakoe78", locator = "sec. II", supports = "does"}',
           'key = "nobody99", locator = "sec. II", supports = "does"}')
    assert "key 'nobody99' is not in _sources.toml" in build(content, preview=True).stdout


def test_family_lesson_must_be_in_the_course(content):
    mutate(content / "_map.toml", 'lesson = "alpha"', 'lesson = "nowhere"')
    assert "lesson 'nowhere' is not listed in _course.md" in build(content, preview=True).stdout


def test_ignores_belong_to_the_compare_branch(content):
    edit_item(content, "k-medoids", ignores=[{"tag": "level", "cond": ""}])
    assert "'ignores' is for the compare branch only" in build(content, preview=True).stdout


def edit_block(content, file, header, name_field, name, **fields):
    set_fields(content / file, header, name_field, name, **fields)


REOPENING_EDITS = [
    ("item cond", lambda c: edit_item(c, "DTW", cond="within a wider w"), "item 'DTW' is draft"),
    ("item python", lambda c: edit_item(c, "Euclidean", python="scipy sqeuclidean"), "item 'Euclidean' is draft"),
    ("item r", lambda c: edit_item(c, "Euclidean", r="dist(x)"), "item 'Euclidean' is draft"),
    ("tag cond", lambda c: edit_item(c, "DTW", ignores=[{"tag": "warp", "cond": "alignment within w, edited"}]),
     "item 'DTW' is draft"),
    ("ref locator", lambda c: edit_ref(c, "Correlation", "ignores:level", "sec. IX"), "item 'Correlation' is draft"),
    ("fit mark", lambda c: edit_fit(c, "finance/same-dates", mark="avoid"), "fit finance/same-dates / 'Correlation' is draft"),
    ("fit reason", lambda c: edit_fit(c, "finance/same-dates", reason="A different reason."),
     "fit finance/same-dates / 'Correlation' is draft"),
    ("question text", lambda c: edit_block(c, "_sectors.toml", "sector.question", "id", "same-hours", text="Another question?"),
     "question energy/same-hours is draft"),
    ("question starts", lambda c: edit_block(c, "_sectors.toml", "sector.question", "id", "same-hours", starts=["Euclidean"]),
     "question energy/same-hours is draft"),
    ("sector about", lambda c: edit_block(c, "_sectors.toml", "sector", "id", "energy", about="Another description."),
     "sector 'energy' is draft"),
    ("sector curve", lambda c: edit_block(c, "_sectors.toml", "sector", "id", "energy", curve=[0.0, 1.0]),
     "sector 'energy' is draft"),
]


@pytest.mark.parametrize("edit,expected", [(e, x) for _, e, x in REOPENING_EDITS], ids=[n for n, _, _ in REOPENING_EDITS])
def test_a_substantive_edit_reopens_review(content, edit, expected):
    edit(content)
    out = build(content).stdout
    assert expected in out
    assert build(content, preview=True).returncode == 0


def test_release_refuses_an_unreviewed_question_and_sector(content):
    drop_record(content, "question", "id", "energy/same-hours")
    drop_record(content, "sector", "id", "finance")
    out = build(content).stdout
    assert "question energy/same-hours is draft" in out and "sector 'finance' is draft" in out


def test_section_title_renders_inline_math_and_code_with_slug_id(content):
    mutate(content / "01-alpha.md", "## Engine features\n", "## Window $w$ and `dtw`\n")
    record_lesson(content, "alpha")
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr
    out = page(content, "alpha")
    # literal expected id: the text tokens "Window ", " and ", "dtw" without the math, as ### headings compute it
    m = re.search(r'<section class="content" id="window-and-dtw"><h2>(.*?)</h2>', out, re.S)
    assert m, "section id is not 'window-and-dtw'"
    assert 'class="katex"' in m.group(1) and "<code>dtw</code>" in m.group(1) and "$" not in m.group(1)
