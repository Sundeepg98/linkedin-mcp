"""Three fixtures ARE the live lane's session-11 tracked copies, but for LinkedIn's own words put back by keyed shape.

``scripts/_build_live11_word_fixtures.py`` wrote
``tests/fixtures/synthetic/live11_invitations_words.html``,
``live11_invitations_sent_words.html`` and ``live11_ads_words.html`` from the
session's KEYED skeletons (gitignored, on the box that took the capture),
putting a word back only where its keyed shape equals the skeleton's. The
keyed skeletons are not here, so this file holds the OUTPUT to the tracked
copies it must equal everywhere else:

* TOKEN BY TOKEN. Both documents are parsed into the same stream of tags,
  attributes and text; a token may differ ONLY where the copy holds ``x`` and
  the fixture one of the builder's own words for that page -- in a text node,
  an attribute value, or one segment of an address. Anything else, and the
  fixture is not the capture.
* THE BUILDER, on a planted keyed skeleton: it puts back exactly the words it
  was given, at exactly the shapes that are theirs, never inside an id; and
  with no words it reproduces the tracked copy byte for byte (a fixed point,
  checked on the box: section 2 of lane readers-net26's record).
* NO ARGUMENT TAKES A WORD: the parser accepts a state directory and nothing
  else.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import _build_live11_word_fixtures as builder  # noqa: E402
import _probe_live_lane_session_2 as harness  # noqa: E402

PAIRS = {
    "invitations": ("synthetic/live11_invitations_words.html", "live11/invitations.html"),
    "invitations_sent": ("synthetic/live11_invitations_sent_words.html", "live11/invitations_sent.html"),
    "ads": ("synthetic/live11_ads_words.html", "live11/ads.html"),
}


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


def _tokens(path: Path) -> list[tuple]:
    parser = _Tokens()
    parser.feed(path.read_text(encoding="ascii"))
    parser.close()
    return parser.out


def _segments(value: str) -> list[str]:
    for sep in ("?", "&", "="):
        value = value.replace(sep, "/")
    return value.split("/")


def _differences(name: str) -> list[str]:
    """Every token where fixture and copy differ OTHER than by a word put back."""
    words = set(builder.WORDS[name])
    fixture_path, copy_path = (REPO / "tests" / "fixtures" / p for p in PAIRS[name])
    fixture, copy = _tokens(fixture_path), _tokens(copy_path)
    if len(fixture) != len(copy):
        return [f"{len(fixture)} tokens against {len(copy)}"]
    bad = []
    for index, (mine, theirs) in enumerate(zip(fixture, copy)):
        if mine == theirs:
            continue
        if mine[0] == "text" and theirs == ("text", "x") and mine[1] in words:
            continue
        if mine[0] == theirs[0] == "attr" and mine[1] == theirs[1]:
            if theirs[2] == "x" and mine[2] in words:
                continue
            ours, copied = _segments(mine[2] or ""), _segments(theirs[2] or "")
            if len(ours) == len(copied) and all(
                a == b or (b == "x" and a in words) for a, b in zip(ours, copied)
            ):
                continue
        bad.append(f"token {index}: {mine[:2]} against {theirs[:2]}")
    return bad


@pytest.mark.parametrize("name", sorted(PAIRS))
def test_each_fixture_is_its_tracked_copy_but_for_linkedins_words(name):
    assert _differences(name) == []


@pytest.mark.parametrize("name", sorted(PAIRS))
def test_each_fixture_does_put_words_back(name):
    """A fixture identical to its copy would pass the test above and serve no
    reader: each must differ from it somewhere."""
    fixture_path, copy_path = (REPO / "tests" / "fixtures" / p for p in PAIRS[name])
    assert fixture_path.read_text(encoding="ascii") != copy_path.read_text(encoding="ascii")


def test_a_word_from_the_other_page_does_not_explain_a_difference():
    """THE CHECK CAN FAIL: with the received page's words taken away, its
    fixture's differences are no longer explained."""
    saved = builder.WORDS["invitations"]
    try:
        builder.WORDS["invitations"] = ("Withdraw",)
        assert _differences("invitations") != []
    finally:
        builder.WORDS["invitations"] = saved


KEY = bytes(range(32))


def _keyed(text: str) -> str:
    return harness.value_shape(text, KEY)


def test_the_builder_puts_back_only_its_words_at_their_own_shapes():
    skeleton = "\n".join((
        "<!doctype html>",
        '<a id="%s" href="https://www.linkedin.com/mynetwork/%s/%s">' % (
            _keyed("Accept"), _keyed("invitation-manager"), _keyed("somebody-example")),
        "<span>", _keyed("Accept"), "</span>",
        "<span>", _keyed("Somebody Example"), "</span>",
        "</a>",
    ))
    fixture, counts = builder.restore(skeleton, KEY, ("Accept", "invitation-manager"))
    assert counts == {"Accept": 1, "invitation-manager": 1}
    assert ">\nAccept\n<" in fixture
    assert "/mynetwork/invitation-manager/x" in fixture
    assert "Somebody" not in fixture and "somebody" not in fixture
    assert 'id="k' in fixture and 'id="Accept"' not in fixture


def test_with_no_words_the_builder_writes_the_tracked_copy():
    skeleton = "<!doctype html>\n<p>\n%s\n</p>" % _keyed("Accept")
    fixture, counts = builder.restore(skeleton, KEY, ())
    assert counts == {} and fixture == harness.tracked_copy(skeleton)


def test_no_argument_takes_a_word():
    options = {
        option
        for action in builder.build_parser()._actions
        for option in action.option_strings
    }
    assert options == {"-h", "--help", "--state"}


def test_every_word_is_a_short_ascii_interface_string():
    for words in builder.WORDS.values():
        assert len(words) == len(set(words))
        for word in words:
            assert word.isascii() and word.strip() == word and 1 <= len(word) <= 40
