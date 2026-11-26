"""Lane build-net2's word fixtures ARE live session 11's tracked copies, but for LinkedIn's own words put back by keyed shape.

``scripts/_build_live11_net2_word_skeletons.py`` wrote each fixture of its
``SPEC`` from the session's KEYED skeleton, through
``scripts/_build_live11_word_skeletons.build`` -- a word only where its keyed
shape equals the skeleton's, a declared word that matches nowhere refused:

* ``tests/fixtures/synthetic/live11_permalink_menu_words.html`` -- a member's
  post's permalink with its control menu open (load 29; ``N 154``);
* ``tests/fixtures/synthetic/live11_search_box_words.html`` -- the feed with
  its search box's typeahead open (load 28; ``N 95``), whose one ADDRESS word,
  ``search-results``, sits inside a link rather than in a text node.

The keyed skeletons are not here, so this file holds each OUTPUT to the tracked
copy it must equal everywhere else, TOKEN BY TOKEN: a token may differ ONLY
where the copy holds ``x`` and the fixture one of the builder's own words --
in a text node, or as one segment of an attribute.
``tests/test_live11_word_fixtures.py``'s tokenizer and rule, imported.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import _build_live11_net2_word_skeletons as builder  # noqa: E402
from tests.test_live11_word_fixtures import _segments, _tokens  # noqa: E402

SYNTHETIC = REPO / "tests" / "fixtures" / "synthetic"
LIVE11 = REPO / "tests" / "fixtures" / "live11"

#: stem -> the one word whose absence from the list must leave a difference
#: nothing explains: the control that shows the check can fail.
CONTROL_WORD = {
    "live11_permalink_menu_words": "Not interested",
    "live11_search_box_words": "search-results",
}


def _paths(stem: str) -> tuple[Path, Path]:
    _skeleton, capture, _words = builder.SPEC[stem]
    return SYNTHETIC / (stem + ".html"), LIVE11 / (capture + ".html")


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


def test_every_fixture_of_the_builder_has_a_control_word():
    assert set(CONTROL_WORD) == set(builder.SPEC)
    for stem, word in CONTROL_WORD.items():
        assert word in _words(stem), stem


@pytest.mark.parametrize("stem", sorted(builder.SPEC))
def test_the_fixture_is_its_tracked_copy_but_for_linkedins_words(stem):
    assert _differences(stem, _words(stem)) == []


@pytest.mark.parametrize("stem", sorted(builder.SPEC))
def test_the_fixture_does_put_words_back(stem):
    fixture_path, copy_path = _paths(stem)
    text = fixture_path.read_text(encoding="ascii")
    assert text != copy_path.read_text(encoding="ascii")
    for word in _words(stem):
        assert f">\n{word}\n<" in text or f"/{word}/" in text, word


@pytest.mark.parametrize("stem", sorted(builder.SPEC))
def test_a_word_not_on_the_list_does_not_explain_a_difference(stem):
    """THE CHECK CAN FAIL: without its control word on the list, the
    fixture's one place holding it is a difference nothing explains."""
    assert _differences(stem, _words(stem) - {CONTROL_WORD[stem]}) != []


def test_no_argument_takes_a_word():
    parser_args = {a.dest for a in builder.argparse.ArgumentParser().parse_known_args([])[0].__dict__}
    assert parser_args == set()
    import inspect

    assert set(inspect.signature(builder.main).parameters) == {"argv"}
    assert set(inspect.signature(builder.render).parameters) == {"session_dir", "stem"}
