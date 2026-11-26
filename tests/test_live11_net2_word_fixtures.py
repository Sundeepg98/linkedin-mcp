"""Lane build-net2's word fixture IS live session 11's tracked copy, but for LinkedIn's own words put back by keyed shape.

``scripts/_build_live11_net2_word_skeletons.py`` wrote
``tests/fixtures/synthetic/live11_permalink_menu_words.html`` from the
session's KEYED skeleton of a member's post's permalink with its control menu
open (load 29), through ``scripts/_build_live11_word_skeletons.build`` -- a
word only where its keyed shape equals the skeleton's, a declared word that
matches nowhere refused. The keyed skeleton is not here, so this file holds
the OUTPUT to the tracked copy it must equal everywhere else, TOKEN BY TOKEN:
a token may differ ONLY where the copy holds ``x`` and the fixture one of the
builder's own words. ``tests/test_live11_word_fixtures.py``'s tokenizer and
rule, imported.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import _build_live11_net2_word_skeletons as builder  # noqa: E402
from tests.test_live11_word_fixtures import _segments, _tokens  # noqa: E402

FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "live11_permalink_menu_words.html"
COPY = REPO / "tests" / "fixtures" / "live11" / "permalink_member_post_menu_open.html"


def _differences(words: set[str]) -> list[str]:
    fixture, copy = _tokens(FIXTURE), _tokens(COPY)
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


def _words() -> set[str]:
    return set(builder.SPEC["live11_permalink_menu_words"][2])


def test_the_fixture_is_its_tracked_copy_but_for_linkedins_words():
    assert _differences(_words()) == []


def test_the_fixture_does_put_words_back():
    assert FIXTURE.read_text(encoding="ascii") != COPY.read_text(encoding="ascii")
    text = FIXTURE.read_text(encoding="ascii")
    for word in _words():
        assert f">\n{word}\n<" in text, word


def test_a_word_not_on_the_list_does_not_explain_a_difference():
    """THE CHECK CAN FAIL: without 'Not interested' on the list, the fixture's
    one 'Not interested' is a difference nothing explains."""
    assert _differences(_words() - {"Not interested"}) != []


def test_no_argument_takes_a_word():
    parser_args = {a.dest for a in builder.argparse.ArgumentParser().parse_known_args([])[0].__dict__}
    assert parser_args == set()
    import inspect

    assert set(inspect.signature(builder.main).parameters) == {"argv"}
    assert set(inspect.signature(builder.render).parameters) == {"session_dir", "stem"}
