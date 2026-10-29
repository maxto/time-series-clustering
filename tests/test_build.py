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

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SMOKE = ROOT / "tests" / "fixtures" / "smoke"


@pytest.fixture
def content(tmp_path):
    target = tmp_path / "content"
    shutil.copytree(SMOKE, target)
    return target


def build(content):
    dist = content.parent / "dist"
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build.py"), "--content", str(content), "--dist", str(dist)],
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
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr


def test_heading_slug_equal_to_block_id_is_rejected(content):
    add_section(content / "01-alpha.md", "Measure card!")  # slug "measure-card"
    out = build(content).stdout
    assert "measure-card" in out and "block id" in out


def test_repeated_heading_gets_suffix(content):
    add_subheading(content / "01-alpha.md", "A subheading")
    result = build(content)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'id="a-subheading-2"' in page(content, "alpha")


def test_unknown_code_language_is_rejected(content):
    mutate(content / "01-alpha.md", "```r", "```julia")
    assert "julia" in build(content).stdout
