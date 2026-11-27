"""Four fixtures ARE the live lane's session-12 tracked copies, but for LinkedIn's own words put back by keyed shape.

``scripts/_build_live12_settings_word_skeletons.py`` (lane settings7,
2026-11-27) wrote ``tests/fixtures/live12/privacy_words.html``,
``verifications_words.html``, ``job_prefs_words.html`` and
``premium_manage_account_words.html`` from session 12's KEYED skeletons
(gitignored, on the box that took the capture), writing a word only where its
keyed shape equals the skeleton's. The keyed skeletons are not here, so this
file holds the OUTPUT to the tracked copies it must equal everywhere else:

* TOKEN BY TOKEN. Both documents are parsed into the same stream of tags,
  attributes and text; a token may differ ONLY where the copy holds ``x`` and
  the fixture one of the builder's own words for that page -- in a text node,
  an attribute value, or one segment of an address. Anything else, and the
  fixture is not the capture.
* WHAT MUST STAY ``x`` stays ``x``: the verification's three detail lines (his
  employer may be among them), his purchase id, the premium card's two
  description lines, and every job card on the page his preferences address
  served. Each is asserted by its own markup, not by a count of differences.
* THE CHECK CAN FAIL: another page's words do not explain a fixture.

Nothing here prints what a fixture draws beyond the builder's own words.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import _build_live12_settings_word_skeletons as builder  # noqa: E402

LIVE12 = REPO / "tests" / "fixtures" / "live12"


class _Tokens(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[tuple] = []

    def handle_starttag(self, tag, attrs):
        self.out.append(("start", tag, tuple(name for name, _ in attrs)))
        for name, value in attrs:
            self.out.append(("attr", name, value))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        self.out.append(("end", tag))

    def handle_data(self, data):
        text = " ".join(data.split())
        if text:
            self.out.append(("text", text))


def _tokens(text: str) -> list[tuple]:
    parser = _Tokens()
    parser.feed(text)
    parser.close()
    return parser.out


def _segments(value: str) -> list[str]:
    for sep in ("?", "&", "="):
        value = value.replace(sep, "/")
    return value.split("/")


def _pair(stem: str) -> tuple[str, str]:
    capture = builder.SPEC[stem][0]
    return (
        (LIVE12 / (stem + ".html")).read_text(encoding="ascii"),
        (LIVE12 / (capture + ".html")).read_text(encoding="ascii"),
    )


def _differences(stem: str, words: tuple[str, ...]) -> list[str]:
    """Every token where fixture and copy differ OTHER than by a word put back."""
    allowed = set(words)
    fixture, copy = (_tokens(t) for t in _pair(stem))
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


STEMS = sorted(builder.SPEC)


@pytest.mark.parametrize("stem", STEMS)
def test_each_fixture_is_its_tracked_copy_but_for_linkedins_words(stem):
    assert _differences(stem, builder.SPEC[stem][2]) == []


@pytest.mark.parametrize("stem", STEMS)
def test_each_fixture_does_put_words_back(stem):
    """A fixture identical to its copy would pass the test above and serve no
    reader: each must differ from it somewhere."""
    fixture, copy = _pair(stem)
    assert fixture != copy


def test_a_word_from_another_page_does_not_explain_a_difference():
    """THE CHECK CAN FAIL: with the premium page's words in place of the
    verifications page's, that fixture's differences are no longer explained."""
    assert _differences("verifications_words", builder.SPEC["premium_manage_account_words"][2]) != []


@pytest.mark.parametrize("stem", STEMS)
def test_each_fixture_opens_with_its_provenance_and_is_strict_ascii(stem):
    raw = (LIVE12 / (stem + ".html")).read_bytes()
    text = raw.decode("ascii")
    assert text.startswith("<!doctype html>\n<!--\n  LANE SETTINGS7, 2026-11-27: built by\n")
    assert "scripts/_build_live12_settings_word_skeletons.py" in text.split("-->", 1)[0]


def _body(stem: str) -> str:
    return (LIVE12 / (stem + ".html")).read_text(encoding="ascii").split("\n-->\n", 1)[1]


def test_the_verification_detail_lines_stay_x():
    """His employer may be on these lines: the builder writes none of them."""
    body = _body("verifications_words")
    inner = body.split('<div class="verifications-evidences__innerContent">', 1)[1].split("</div>", 1)[0]
    assert inner.count("<p ") == 3
    assert [line for line in inner.split("\n") if line and not line.startswith("<")] == ["x", "x", "x"]


def test_his_purchase_id_and_the_two_description_lines_stay_x():
    body = _body("premium_manage_account_words")
    assert "/manage/purchases-payments/purchases/x\"" in body
    description = body.split("premium-subscription-overview-settings-card__description", 1)[1].split("</div>", 1)[0]
    assert [line for line in description.split("\n") if line and not line.startswith("<") and "=" not in line] == ["x", "x"]


class _CardTexts(HTMLParser):
    """The texts inside each job card: an anchor whose address carries a
    ``currentJobId`` (the six cards the landing drew; ``Show all`` carries none)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.cards: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a" and not self.depth and "currentJobId=" in (dict(attrs).get("href") or ""):
            self.depth = 1
            self.cards.append([])
        elif self.depth and tag == "a":
            self.depth += 1

    def handle_endtag(self, tag):
        if self.depth and tag == "a":
            self.depth -= 1

    def handle_data(self, data):
        text = " ".join(data.split())
        if self.depth and text:
            self.cards[-1].append(text)


def _cards(text: str) -> list[list[str]]:
    parser = _CardTexts()
    parser.feed(text)
    return parser.cards


def test_the_job_cards_on_the_preferences_landing_are_the_tracked_copys():
    """Only the rail's anchors, the title and one module heading are words:
    every job card reads exactly as in the tracked copy, nothing written in it."""
    fixture, copy = _pair("job_prefs_words")
    cards = _cards(fixture)
    assert len(cards) == 6
    assert cards == _cards(copy)
    assert all(card and "x" in card for card in cards)


def test_every_word_is_an_ascii_interface_string_and_the_parser_takes_none():
    for capture, skeleton, words in builder.SPEC.values():
        assert len(words) == len(set(words))
        for word in words:
            assert word.isascii() and word.strip() == word and 1 <= len(word) <= 90
    options = {
        option
        for action in argparse_actions()
        for option in action.option_strings
    }
    assert options == {"-h", "--help", "--session-dir", "--only", "--check"}


def argparse_actions():
    """The builder's parser, rebuilt the way its main() builds it."""
    import argparse

    seen = []
    real = argparse.ArgumentParser.parse_args

    def capture(self, *args, **kwargs):
        seen.extend(self._actions)
        raise SystemExit(0)

    argparse.ArgumentParser.parse_args = capture
    try:
        with pytest.raises(SystemExit):
            builder.main([])
    finally:
        argparse.ArgumentParser.parse_args = real
    return seen
