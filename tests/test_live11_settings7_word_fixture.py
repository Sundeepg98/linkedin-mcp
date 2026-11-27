"""Session 11's Account preferences capture IS its tracked copy, but for LinkedIn's own words put back by keyed shape.

``scripts/_build_live11_settings7_word_skeletons.py`` (lane settings7,
2026-11-27) wrote ``tests/fixtures/live11/sessions_surface_words.html`` from
session 11's KEYED skeleton of the page (gitignored, on the box that took the
capture), writing a word only where its keyed shape equals the skeleton's. It
is the evidence for the contact-syncing admission
(CONTACTS-PAGE-FROM-THE-SETTINGS-NAV): the settings nav's one contacts entry,
``Sync contacts`` under ``Syncing options``, a link to
``/mynetwork/settings/manage-syncing``.

The same three holds as ``tests/test_live12_settings_word_fixtures.py``, whose
token helpers this imports: the fixture equals its tracked copy token by token
except where the copy holds ``x`` and the fixture one of the builder's words;
it does differ somewhere; and another page's words do not explain it.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import _build_live11_settings7_word_skeletons as builder  # noqa: E402
import _build_live12_settings_word_skeletons as other_page  # noqa: E402
from tests.test_live12_settings_word_fixtures import (  # noqa: E402
    _as_committed,
    _assert_opens_with_its_provenance,
    _segments,
    _tokens,
)

LIVE11 = REPO / "tests" / "fixtures" / "live11"
STEM = "sessions_surface_words"


def _pair() -> tuple[str, str]:
    capture = builder.SPEC[STEM][0]
    return (
        (LIVE11 / (STEM + ".html")).read_text(encoding="ascii"),
        (LIVE11 / (capture + ".html")).read_text(encoding="ascii"),
    )


def _differences(words: tuple[str, ...]) -> list[str]:
    allowed = set(words)
    fixture, copy = (_tokens(t) for t in _pair())
    if len(fixture) != len(copy):
        return [f"{len(fixture)} tokens against {len(copy)}"]
    bad = []
    for index, (mine, theirs) in enumerate(zip(fixture, copy)):
        if mine == theirs:
            continue
        if mine[0] == "text" and theirs == ("text", "x") and mine[1] in allowed:
            continue
        if mine[0] == theirs[0] == "attr" and mine[1] == theirs[1]:
            if theirs[2] == "x" and mine[2] in allowed:
                continue
            ours, copied = _segments(mine[2] or ""), _segments(theirs[2] or "")
            if len(ours) == len(copied) and all(
                a == b or (b == "x" and a in allowed) for a, b in zip(ours, copied)
            ):
                continue
        bad.append(f"token {index}: {mine[:2]} against {theirs[:2]}")
    return bad


def test_the_fixture_is_its_tracked_copy_but_for_linkedins_words():
    assert _differences(builder.SPEC[STEM][2]) == []


def test_the_fixture_does_put_words_back():
    fixture, copy = _pair()
    assert fixture != copy


def test_another_pages_words_do_not_explain_it():
    """THE CHECK CAN FAIL: the verifications page's words leave its differences unexplained."""
    assert _differences(other_page.SPEC["verifications_words"][2]) != []


def test_the_contacts_entry_is_drawn_as_the_admitted_address_with_its_label():
    text = _pair()[0].split("\n-->\n", 1)[1]
    link = 'href="https://www.linkedin.com/mynetwork/settings/manage-syncing"'
    assert text.count(link) == 1
    after = text.split(link, 1)[1].split("</a>", 1)[0]
    assert "\nSync contacts\n" in after
    assert text.count("\nSyncing options\n") == 1


def test_the_fixture_opens_with_its_provenance_and_is_strict_ascii():
    raw = (LIVE11 / (STEM + ".html")).read_bytes()
    _assert_opens_with_its_provenance(_as_committed(raw), "scripts/_build_live11_settings7_word_skeletons.py")


def test_a_crlf_checkout_of_the_fixture_opens_the_same():
    """THE WINDOWS CELL'S CHECKOUT, ON ANY BOX: the committed LF bytes written as
    ``core.autocrlf`` writes them open with the same provenance."""
    committed = (LIVE11 / (STEM + ".html")).read_bytes().replace(b"\r\n", b"\n")
    assert b"\r" not in committed
    crlf = committed.replace(b"\n", b"\r\n")
    _assert_opens_with_its_provenance(_as_committed(crlf), "scripts/_build_live11_settings7_word_skeletons.py")
