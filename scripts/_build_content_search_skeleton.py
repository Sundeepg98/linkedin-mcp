"""Build the CONTENT SEARCH's result cards into a committed fixture: the live lane's session-11 skeleton of one content search, with its measured LinkedIn words kept and its people and their words synthetic.

Kept as the PROVENANCE of ``tests/fixtures/live11/search_content_posts.html``,
the fixture ``linkedin_server.content_search`` (census row ``M C93``) is built
over, 2026-11-26 (lane readers-msg26).

THE INPUT is the gitignored KEYED skeleton the live lane wrote on 2026-11-26
(``_state/live11/search_content.skeleton.html`` of lane live-s11, every text
and attribute value a keyed shape ``{L<letters>D<digits>n<length>:<8-hex
hash>}``) and that session's key (``_state/live11/shape.key``). Both are read,
neither is written anywhere, and nothing here prints a hash or the key. The
committed copy ``tests/fixtures/live11/search_content.html`` is
``tracked_copy`` of the same skeleton; this script recomputes that copy and
REFUSES unless it is identical to the committed one, so the input is shown to
be the capture the repository already holds.

WHAT IT CHANGES. A CARD is an element with ``role="listitem"``; the capture
draws three. Each is required to hold exactly one ``h2``, exactly one words
box and exactly one member link holding paragraphs; anything else refuses.

    MEASURED -- written ONLY after ``value_shape(word, key)`` equals the keyed
    shape at that place:

    the screen          data-sdui-screen   SCREEN (once on the page)
    each card's h2      its one text       "Feed post"
    each words box      data-testid        "expandable-text-box"
    each more control   data-testid        "expandable-text-button"
                        its two texts      the ellipsis, then "more"
    each author line    its degree text    the bullet and "3rd+"

    SYNTHETIC -- declared here, written over a keyed shape of the same kind:

    each card's author  the first text of the member link that holds
                        paragraphs         one of AUTHORS (declared people,
                                           tests/test_fixtures_hold_only_
                                           synthetic_people.py)
    each member link    its slug           SLUGS[card] (the token "example")
    each words box      each text line     "Example post words <card>.<line>"
                        each hashtag       "#exampletopic<k>"

Everything else is the committed copy's: every other text and value ``x``,
id references ``k`` plus their hash, LinkedIn's furniture and path words kept.

    python scripts/_build_content_search_skeleton.py --skeleton <keyed skeleton> --key <shape.key> [--out <path>]

Prints counts and a sha256 digest of what it wrote, never a value it read.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _probe_live_lane_session_2 as s2  # noqa: E402  value_shape, tracked_copy

DEFAULT_OUT = REPO / "tests" / "fixtures" / "live11" / "search_content_posts.html"
BASE_COPY = REPO / "tests" / "fixtures" / "live11" / "search_content.html"

#: MEASURED 2026-11-26 by hashing these candidate words with session 11's key
#: against the keyed skeleton (lane readers-msg26's record, section 2).
SCREEN = "com.linkedin.sdui.flagshipnav.search.SearchResultsContent"
HEADING = "Feed post"
WORDS_BOX = "expandable-text-box"
MORE_CONTROL = "expandable-text-button"
MORE_TEXTS = ("…", "more")
DEGREE_LINE = "• 3rd+"

#: Declared synthetic people (``SYNTHETIC_PEOPLE`` in
#: ``tests/test_fixtures_hold_only_synthetic_people.py``), one per card.
AUTHORS = ("Kai Example", "Juno Fixture", "Lea Sample")
SLUGS = ("kai-example-a1", "juno-example-b2", "lea-example-c3")

HEADER = (
    "<!doctype html>\n<!--\n"
    "  LANE READERS-MSG26 (census row M C93), 2026-11-26: built by\n"
    "  scripts/_build_content_search_skeleton.py from the live lane's\n"
    "  SESSION-11 keyed skeleton of one content search, the same skeleton\n"
    "  tests/fixtures/live11/search_content.html is the tracked copy of.\n"
    "  Identical to that copy except inside the screen marker and the three\n"
    "  result cards: the screen's name, each card's heading, its words box's\n"
    "  and more control's test hooks, the more control's two texts and the\n"
    "  degree line are LinkedIn's own words, each written only after its keyed\n"
    "  shape matched; each author's name and profile slug and every line of\n"
    "  each post's words are declared synthetic values. EVERY PERSON HERE IS\n"
    "  INVENTED. Every other text is x, as in that copy.\n"
    "-->\n"
)

_SHAPE = re.compile(r"^\{L(\d+)D(\d+)n(\d+):[0-9a-f]{8}\}$")
_SHAPE_ANYWHERE = re.compile(r"\{L\d+D\d+n\d+:[0-9a-f]{8}\}")
_MEMBER_HREF = re.compile(r"^https://www\.linkedin\.com/in/(\{L\d+D\d+n\d+:[0-9a-f]{8}\})/$")
_VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                   "link", "meta", "param", "source", "track", "wbr"})


class _Node:
    def __init__(self, tag: str, attrs: dict, line: int, parent: Optional["_Node"]) -> None:
        self.tag, self.attrs, self.line, self.parent = tag, attrs, line, parent
        self.children: list = []


class _Text:
    def __init__(self, text: str, line: int, parent: "_Node") -> None:
        self.text, self.line, self.parent = text, line, parent


class _Tree(HTMLParser):
    """The skeleton writes one token per line, so a token's line IS its place."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", {}, 0, None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, dict(attrs), self.getpos()[0], self.cur)
        self.cur.children.append(node)
        if tag not in _VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(_Node(tag, dict(attrs), self.getpos()[0], self.cur))

    def handle_endtag(self, tag):
        walker = self.cur
        while walker is not None and walker.tag != tag:
            walker = walker.parent
        if walker is not None and walker.parent is not None:
            self.cur = walker.parent

    def handle_data(self, data):
        if data.strip():
            lead = data[: len(data) - len(data.lstrip())].count("\n")
            self.cur.children.append(_Text(data.strip(), self.getpos()[0] + lead, self.cur))


def _walk(node):
    yield node
    for child in getattr(node, "children", []):
        yield from _walk(child)


def _elements(node, tag=None):
    return [n for n in _walk(node) if isinstance(n, _Node) and (tag is None or n.tag == tag)]


def _texts(node):
    return [n for n in _walk(node) if isinstance(n, _Text)]


def _inside(node, ancestor) -> bool:
    walker = node.parent
    while walker is not None:
        if walker is ancestor:
            return True
        walker = walker.parent
    return False


def build(skeleton: str, key: bytes) -> tuple[str, dict[str, int]]:
    lines = skeleton.split("\n")
    tree = _Tree()
    tree.feed(skeleton)
    tree.close()

    def measured(value: str, word: str, what: str) -> str:
        if value == word:
            return word  # kept verbatim by the session's own FURNITURE list
        if s2.value_shape(word, key) != value:
            raise SystemExit(f"the {what} did not match its measured word; refusing to write it")
        return word

    def set_line(line: int, old: str, new: str) -> None:
        current = lines[line - 1]
        if current.count(old) != 1:
            raise SystemExit("a line did not hold exactly one value to replace")
        lines[line - 1] = current.replace(old, new)

    def set_attribute(node: _Node, name: str, word: str, what: str) -> None:
        value = node.attrs.get(name)
        if value is None:
            raise SystemExit(f"the {what} has no {name}")
        set_line(node.line, name + '="' + value + '"',
                 name + '="' + measured(value, word, what) + '"')

    def synthetic(text: _Text, word: str, what: str) -> None:
        if not _SHAPE.match(text.text):
            raise SystemExit(f"the {what} is not a keyed shape where one was expected")
        set_line(text.line, text.text, word)

    counts = {"screens": 0, "cards": 0, "headings kept": 0, "words boxes kept": 0,
              "more controls kept": 0, "degree lines kept": 0, "synthetic authors": 0,
              "synthetic slugs": 0, "synthetic word lines": 0, "synthetic hashtags": 0}

    screens = [n for n in _elements(tree.root) if "data-sdui-screen" in n.attrs]
    if len(screens) != 1:
        raise SystemExit(f"{len(screens)} screen markers, where one is required")
    set_attribute(screens[0], "data-sdui-screen", SCREEN, "screen marker")
    counts["screens"] = 1

    cards = [n for n in _elements(tree.root) if n.attrs.get("role") == "listitem"]
    if len(cards) != len(AUTHORS):
        raise SystemExit(f"{len(cards)} cards, where {len(AUTHORS)} were measured")
    counts["cards"] = len(cards)
    hashtag = 0
    for index, card in enumerate(cards):
        h2s = _elements(card, "h2")
        if len(h2s) != 1 or len(_texts(h2s[0])) != 1:
            raise SystemExit("a card without exactly one one-line h2")
        text = _texts(h2s[0])[0]
        set_line(text.line, text.text, measured(text.text, HEADING, "card heading"))
        counts["headings kept"] += 1

        boxes = [n for n in _elements(card) if "data-testid" in n.attrs
                 and s2.value_shape(WORDS_BOX, key) == n.attrs["data-testid"]]
        if len(boxes) != 1:
            raise SystemExit("a card without exactly one words box")
        box = boxes[0]
        set_attribute(box, "data-testid", WORDS_BOX, "words box")
        counts["words boxes kept"] += 1

        mores = [n for n in _elements(card) if "data-testid" in n.attrs
                 and s2.value_shape(MORE_CONTROL, key) == n.attrs["data-testid"]]
        if len(mores) != 1:
            raise SystemExit("a card without exactly one more control")
        more = mores[0]
        set_attribute(more, "data-testid", MORE_CONTROL, "more control")
        more_texts = [t for t in _texts(more)
                      if not any(isinstance(a, _Node) and a.tag == "button" and a is not more
                                 and _inside(t, a) for a in _elements(more))]
        if len(more_texts) < len(MORE_TEXTS):
            raise SystemExit("the more control does not hold its two texts")
        for text, word in zip(more_texts[: len(MORE_TEXTS)], MORE_TEXTS):
            set_line(text.line, text.text, measured(text.text, word, "more control text"))
        counts["more controls kept"] += 1

        # THE AUTHOR: the one member link holding paragraphs, outside the box.
        members = [a for a in _elements(card, "a")
                   if _MEMBER_HREF.match(a.attrs.get("href") or "") and not _inside(a, box)]
        slugs = {_MEMBER_HREF.match(a.attrs["href"]).group(1) for a in members}
        if len(slugs) != 1:
            raise SystemExit("a card's member links do not name exactly one profile")
        named = [a for a in members if _elements(a, "p")]
        if len(named) != 1:
            raise SystemExit("a card without exactly one member link holding paragraphs")
        paragraphs = _elements(named[0], "p")
        if len(paragraphs) != 2 or any(len(_texts(p)) != 1 for p in paragraphs):
            raise SystemExit("the author link does not hold exactly two one-line paragraphs")
        synthetic(_texts(paragraphs[0])[0], AUTHORS[index], "author name")
        counts["synthetic authors"] += 1
        degree = _texts(paragraphs[1])[0]
        set_line(degree.line, degree.text, measured(degree.text, DEGREE_LINE, "degree line"))
        counts["degree lines kept"] += 1
        slug = next(iter(slugs))
        for link in members:
            set_line(link.line, slug, SLUGS[index])
            counts["synthetic slugs"] += 1

        # THE WORDS: every text inside the box but the more control's.
        for number, text in enumerate(
            [t for t in _texts(box) if not _inside(t, more)], start=1
        ):
            if text.parent.tag == "strong":
                hashtag += 1
                synthetic(text, f"#exampletopic{hashtag}", "hashtag")
                counts["synthetic hashtags"] += 1
            else:
                synthetic(text, f"Example post words {index + 1}.{number}", "word line")
                counts["synthetic word lines"] += 1

    copy = s2.tracked_copy("\n".join(lines))
    if not copy.startswith("<!doctype html>\n"):
        raise SystemExit("the skeleton does not open with its doctype line")
    if _SHAPE_ANYWHERE.search(copy):
        raise SystemExit("a keyed shape survived the tracked copy; refusing to write")
    return HEADER + copy[len("<!doctype html>\n"):], counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--skeleton", required=True, type=Path)
    parser.add_argument("--key", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    skeleton = args.skeleton.read_text(encoding="utf-8")
    key = bytes.fromhex(args.key.read_text(encoding="utf-8").strip())

    base = s2.tracked_copy(skeleton)
    if BASE_COPY.read_text(encoding="ascii") != base:
        raise SystemExit("this skeleton's tracked copy is not tests/fixtures/live11/search_content.html")

    text, counts = build(skeleton, key)
    assert all(ord(ch) < 128 for ch in text)
    args.out.write_text(text, encoding="ascii", newline="\n")
    print("base copy identical to the committed capture: True")
    for name in sorted(counts):
        print("%-22s %d" % (name, counts[name]))
    body = text.split("\n")[len(HEADER.split("\n")) - 1:]
    print("lines differing from the base copy: %d" % sum(
        1 for a, b in zip(base.split("\n")[1:], body) if a != b))
    print("sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest()[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
