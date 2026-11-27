"""Lane net7's word fixtures ARE live session 12's tracked copies, but for LinkedIn's own words put back by keyed shape.

``scripts/_build_live12_net7_word_skeletons.py`` wrote each fixture of its
``SPEC`` from the session's KEYED skeleton, through
``scripts/_build_live11_word_skeletons.build`` -- a word only where its keyed
shape equals the skeleton's, a declared word that matches nowhere refused:

* ``tests/fixtures/synthetic/live12_people_panel_words.html`` -- the people
  search with All filters' panel open (load 6; ``N 82``, ``N 86``, ``N 88``,
  ``N 89``, and the form ``N 90`` to ``N 93`` are re-aimed by);
* ``tests/fixtures/synthetic/live12_first_degree_panel_words.html`` -- his
  first degree's search, the panel open (load 32; ``N 26b``);
* ``tests/fixtures/synthetic/live12_premium_matches_words.html`` -- his Premium
  networking matches (load 26; ``N 199``);
* ``tests/fixtures/synthetic/live12_invitation_pills_words.html`` -- his
  received invitations' three filter pills (load 28; ``N 14``);
* ``tests/fixtures/synthetic/live12_connections_words.html`` -- his
  connections page's toolbar (load 14; ``N 27``, ``N 24``), added in the
  lane's round 2.

The keyed skeletons are not here, so this file holds each OUTPUT to the tracked
copy it must equal everywhere else, TOKEN BY TOKEN: a token may differ ONLY
where the copy holds ``x`` and the fixture one of the builder's own words --
in a text node, or as one segment of an attribute.
``tests/test_live11_word_fixtures.py``'s tokenizer and rule, imported, as
``tests/test_live11_net2_word_fixtures.py`` imports them.
"""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import _build_live12_net7_word_skeletons as builder  # noqa: E402
from tests.test_live11_word_fixtures import _segments, _tokens  # noqa: E402

SYNTHETIC = REPO / "tests" / "fixtures" / "synthetic"
LIVE12 = REPO / "tests" / "fixtures" / "live12"

#: stem -> the one word whose absence from the list must leave a difference
#: nothing explains: the control that shows the check can fail.
CONTROL_WORD = {
    "live12_people_panel_words": "Schools",
    "live12_first_degree_panel_words": "Industries",
    "live12_premium_matches_words": "Hiring for",
    "live12_invitation_pills_words": "Focused 3",
    # Round 2 (2026-11-27): his connections page (load 14), for N 27 and N 24.
    "live12_connections_words": "Locations",
}


def _paths(stem: str) -> tuple[Path, Path]:
    _skeleton, capture, _words = builder.SPEC[stem]
    return SYNTHETIC / (stem + ".html"), LIVE12 / (capture + ".html")


def _differences(stem: str, words: set[str]) -> list[str]:
    fixture_path, copy_path = _paths(stem)
    fixture, copy = _tokens(fixture_path), _tokens(copy_path)
    # The fixture opens with its provenance comment, which the copy lacks;
    # HTMLParser drops comments, so the two streams align from the doctype.
    if len(fixture) != len(copy):
        return [f"{len(fixture)} tokens against {len(copy)}"]
    bad = []
    for index, (mine, theirs) in enumerate(zip(fixture, copy)):
        if mine == theirs:
            continue
        if mine[0] == "text" and theirs == ("text", "x") and mine[1] in words:
            continue
        if mine[0] == theirs[0] == "attr" and mine[1] == theirs[1]:
            ours, copied = _segments(mine[2] or ""), _segments(theirs[2] or "")
            if len(ours) == len(copied) and all(
                a == b or (b == "x" and a in words) for a, b in zip(ours, copied)
            ):
                continue
        bad.append(f"token {index}: {mine[:2]} against {theirs[:2]}")
    return bad


def _words(stem: str) -> set[str]:
    return set(builder.SPEC[stem][2])


def _drawn(text: str, word: str) -> bool:
    """The word stands where the builder writes one: a whole text line, a
    whole attribute value, a path segment, or a query value."""
    escaped = re.escape(word.replace("&", "&amp;"))
    return bool(
        re.search(r">\n" + escaped + r"\n<", text)
        or re.search(r'="' + escaped + r'"', text)
        or re.search(r"/" + escaped + r'(?:/|")', text)
        or re.search(r"=" + escaped + r'(?:&|")', text)
    )


def test_every_fixture_of_the_builder_has_a_control_word():
    assert set(CONTROL_WORD) == set(builder.SPEC)
    for stem, word in CONTROL_WORD.items():
        assert word in _words(stem), stem


@pytest.mark.parametrize("stem", sorted(builder.SPEC))
def test_the_fixture_is_its_tracked_copy_but_for_linkedins_words(stem):
    assert _differences(stem, _words(stem)) == []


@pytest.mark.parametrize("stem", sorted(builder.SPEC))
def test_the_fixture_does_put_every_declared_word_back(stem):
    fixture_path, copy_path = _paths(stem)
    text = fixture_path.read_text(encoding="ascii")
    assert text != copy_path.read_text(encoding="ascii")
    missing = [word for word in _words(stem) if not _drawn(text, word)]
    assert missing == [], missing


@pytest.mark.parametrize("stem", sorted(builder.SPEC))
def test_a_word_not_on_the_list_does_not_explain_a_difference(stem):
    """THE CHECK CAN FAIL: without its control word on the list, the
    fixture's places holding it are differences nothing explains."""
    assert _differences(stem, _words(stem) - {CONTROL_WORD[stem]}) != []


def test_no_argument_takes_a_word():
    assert set(inspect.signature(builder.main).parameters) == {"argv"}
    assert set(inspect.signature(builder.render).parameters) == {"session_dir", "stem"}
    source = (REPO / "scripts" / "_build_live12_net7_word_skeletons.py").read_text(encoding="utf-8")
    added = re.findall(r'add_argument\("(--[a-z-]+)"', source)
    assert added == ["--session-dir", "--check"], added
