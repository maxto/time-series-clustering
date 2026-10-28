"""Build validation on a copy of the smoke fixture (plan test group F).

Each test changes one lesson of a temporary copy and runs scripts/build.py on it.
The expected outcomes come from the content rules in the pilot plan (Task 5) and
the controller rulings R3 and R4: a TeX error, a semicolon in prose and a missing
generated number each fail the build, a semicolon in code or math does not.
"""

import json
import pathlib
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


def add_to_lesson(content, text):
    """Insert a block of Markdown at the top of the ## Lesson section of 01-alpha.md."""
    lesson = content / "01-alpha.md"
    body = lesson.read_text()
    assert "## Lesson\n\n" in body
    lesson.write_text(body.replace("## Lesson\n\n", f"## Lesson\n\n{text}\n\n", 1))


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
