"""Build the People tab's INSIGHT CAROUSEL into a committed fixture: the live lane's session-2 skeleton of one organisation's People tab, with the carousel's measured LinkedIn words kept and its rows' labels and counts synthetic.

Kept as the PROVENANCE of ``tests/fixtures/live2/company_people_insights.html``,
the fixture ``linkedin_server.company_people_insights`` (census row ``J 108``)
is built over, 2026-10-10 (lane B4, child b4-j108).

THE INPUT is the gitignored KEYED skeleton the live lane wrote on 2026-09-28
(``_state/live2/company_people.skeleton.html``, every text and attribute value
a keyed shape ``{L<letters>D<digits>n<length>:<8-hex hash>}``) and that
session's key (``_state/live2/shape.key``). Both are read, neither is written
anywhere, and nothing here prints a hash or the key. The committed copy
``tests/fixtures/live2/company_people.html`` is ``tracked_copy`` of the same
skeleton; this script recomputes that copy and REFUSES unless it is identical
to the committed one, so the input is shown to be the capture the repository
already holds.

WHAT IT CHANGES, and only inside the carousel. A card is the nearest ``li``
around a row; a row is an ``a[role="checkbox"]`` whose address is a People tab
with one ``facet...`` parameter. Per card, by the facet parameter its rows
carry (all of a card's rows must carry the same one, or this refuses):

    the card's h3 heading            -> LinkedIn's heading for that facet
    the filter toggle's label text    -> LinkedIn's toggle word
    the toggle's inner aria-label     -> "Filter by <toggle word>"
    the connection card's row labels  -> the degree word, one of 1st/2nd/3rd+

each written ONLY after ``value_shape(word, key)`` equals the keyed shape at
that place -- a MEASURED word, never an assumed one -- and

    every other card's row label      -> "Example <kind> <n>"        (synthetic)
    every row's count                 -> "<k>,000"-style, the measured digit
                                         count and thousands separator kept,
                                         largest first                (synthetic)

after checking the label's shape has letters and the count's has digits only.
Everything else is the committed copy's: every other text and value ``x``, id
references ``k`` plus their hash, LinkedIn's words and path words kept.

    python scripts/_build_company_people_insights_skeleton.py --skeleton <keyed skeleton> --key <shape.key> [--out <path>]

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
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _probe_live_lane_session_2 as s2  # noqa: E402  value_shape, tracked_copy

DEFAULT_OUT = REPO / "tests" / "fixtures" / "live2" / "company_people_insights.html"
BASE_COPY = REPO / "tests" / "fixtures" / "live2" / "company_people.html"

#: Per facet parameter: (heading, toggle label, toggle aria-label, synthetic
#: label stem). MEASURED 2026-10-10 by hashing these candidate words with the
#: session key against the keyed skeleton (b4-j108's report, section 1).
#: ``None`` stem: that card's labels are LinkedIn's degree words, kept.
CARDS: dict[str, tuple[str, str, str, Optional[str]]] = {
    "facetGeoRegion": ("Where they live", "Locations", "Filter by Locations", "Example place"),
    "facetSchool": ("Where they studied", "Schools", "Filter by Schools", "Example school"),
    "facetCurrentFunction": ("What they do", "Job title", "Filter by Job title", "Example title"),
    "facetSkills": ("What they are skilled at", "Skills", "Filter by Skills", "Example skill"),
    "facetEducation": ("What they studied", "Studied", "Filter by Studied", "Example field"),
    "facetConnection": ("How you are connected", "Connections", "Filter by Connections", None),
}

#: The connection degrees LinkedIn draws (``people_data.DEGREES``'s words).
DEGREES = ("1st", "2nd", "3rd+")

HEADER = (
    "<!doctype html>\n<!--\n"
    "  LANE B4 (census row J 108), 2026-10-10: built by\n"
    "  scripts/_build_company_people_insights_skeleton.py from the live lane's\n"
    "  SESSION-2 keyed skeleton of one organisation's People tab, the same\n"
    "  skeleton tests/fixtures/live2/company_people.html is the tracked copy of.\n"
    "  Identical to that copy except inside the insight carousel: each card's\n"
    "  heading, its filter toggle's label and aria-label, and the connection\n"
    "  card's degree words are LinkedIn's own words, each written only after its\n"
    "  keyed shape matched; each other row's label and every row's count is a\n"
    "  declared synthetic value. Every other text is x, as in that copy.\n"
    "-->\n"
)

_SHAPE = re.compile(r"^\{L(\d+)D(\d+)n(\d+):[0-9a-f]{8}\}$")
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
            # The data starts with the newline that ends the previous token's
            # line, so its own line is that many lines further on.
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


def _shape(text: str) -> tuple[int, int, int]:
    found = _SHAPE.match(text)
    if not found:
        raise SystemExit("a carousel text is not a keyed shape where one was expected")
    return tuple(int(g) for g in found.groups())  # type: ignore[return-value]


def _facet_of(href: str) -> Optional[str]:
    parts = urlsplit(href)
    if not re.fullmatch(r"/(company|school)/[^/]+/people/", parts.path):
        return None
    names = [pair.partition("=")[0] for pair in parts.query.split("&") if pair]
    facets = [name for name in names if name.startswith("facet")]
    return facets[0] if len(names) == 1 and len(facets) == 1 else None


def _synthetic_count(digits: int, length: int, rank: int) -> str:
    """``<k>`` followed by zeros, ``digits`` long, grouped when the measured
    length says a separator was drawn; ``k`` counts down by rank from 9."""
    lead = max(1, 9 - rank)
    value = lead * 10 ** (digits - 1)
    grouped = length == digits + (digits - 1) // 3
    if length != digits and not grouped:
        raise SystemExit("a count's shape is neither plain digits nor grouped digits")
    return f"{value:,}" if grouped and digits > 3 else str(value)


def build(skeleton: str, key: bytes) -> tuple[str, dict[str, int]]:
    lines = skeleton.split("\n")
    tree = _Tree()
    tree.feed(skeleton)
    tree.close()

    def measured(text: str, word: str, what: str) -> str:
        if text == word:
            return word  # kept verbatim by the session's own FURNITURE list
        if s2.value_shape(word, key) != text:
            raise SystemExit(f"the {what} did not match its measured word; refusing to write it")
        return word

    def set_line(line: int, old: str, new: str) -> None:
        current = lines[line - 1]
        if current.count(old) != 1:
            raise SystemExit("a carousel line did not hold exactly one value to replace")
        lines[line - 1] = current.replace(old, new)

    rows = [a for a in _elements(tree.root, "a")
            if a.attrs.get("role") == "checkbox" and _facet_of(a.attrs.get("href") or "")]
    cards: list[_Node] = []
    for row in rows:
        walker = row.parent
        while walker is not None and walker.tag != "li":
            walker = walker.parent
        if walker is None:
            raise SystemExit("a facet row outside any li")
        if walker not in cards:
            cards.append(walker)

    counts = {"cards": len(cards), "rows": len(rows), "headings kept": 0, "toggle labels kept": 0,
              "toggle aria-labels kept": 0, "degree words kept": 0, "synthetic labels": 0,
              "synthetic counts": 0}
    for card in cards:
        card_rows = [r for r in rows if card in _ancestors(r)]
        facets = {_facet_of(r.attrs["href"]) for r in card_rows}
        if len(facets) != 1 or next(iter(facets)) not in CARDS:
            raise SystemExit("a card's rows do not carry one known facet parameter")
        heading, toggle, toggle_label, stem = CARDS[next(iter(facets))]

        h3s = _elements(card, "h3")
        if len(h3s) != 1 or len(_texts(h3s[0])) != 1:
            raise SystemExit("a card without exactly one one-line h3")
        text = _texts(h3s[0])[0]
        set_line(text.line, text.text, measured(text.text, heading, "heading"))
        counts["headings kept"] += 1

        labels = _elements(card, "label")
        if len(labels) != 1 or len(_texts(labels[0])) != 1:
            raise SystemExit("a card without exactly one one-line toggle label")
        text = _texts(labels[0])[0]
        if text.text != toggle:
            set_line(text.line, text.text, measured(text.text, toggle, "toggle label"))
        counts["toggle labels kept"] += 1

        named = [n for n in _elements(card) if "aria-label" in n.attrs
                 and any(a.attrs.get("role") == "button" for a in _ancestors(n))]
        if len(named) != 1:
            raise SystemExit("a card's toggle without exactly one aria-label inside it")
        value = named[0].attrs["aria-label"]
        set_line(named[0].line, 'aria-label="' + value + '"',
                 'aria-label="' + measured(value, toggle_label, "toggle aria-label") + '"')
        counts["toggle aria-labels kept"] += 1

        ranks: dict[int, int] = {}
        for index, row in enumerate(card_rows):
            paragraphs = _elements(row, "p")
            if len(paragraphs) != 2 or any(len(_texts(p)) != 1 for p in paragraphs):
                raise SystemExit("a row without exactly two one-line paragraphs")
            label, count = _texts(paragraphs[0])[0], _texts(paragraphs[1])[0]
            letters, digits, _length = _shape(label.text)
            c_letters, c_digits, c_length = _shape(count.text)
            if c_letters or not c_digits:
                raise SystemExit("a row's second paragraph is not digits-only")
            if stem is None:
                word = next((d for d in DEGREES if s2.value_shape(d, key) == label.text), None)
                if word is None:
                    raise SystemExit("a connection row's label is not a degree word; refusing")
                set_line(label.line, label.text, word)
                counts["degree words kept"] += 1
            else:
                if not letters or digits:
                    raise SystemExit("a row's first paragraph is not letters-only")
                set_line(label.line, label.text, f"{stem} {index + 1}")
                counts["synthetic labels"] += 1
            rank = ranks.get(c_digits, 0)
            ranks[c_digits] = rank + 1
            set_line(count.line, count.text, _synthetic_count(c_digits, c_length, rank))
            counts["synthetic counts"] += 1

    text = s2.tracked_copy("\n".join(lines))
    if not text.startswith("<!doctype html>\n"):
        raise SystemExit("the skeleton does not open with its doctype line")
    return HEADER + text[len("<!doctype html>\n"):], counts


def _ancestors(node):
    walker = node.parent
    while walker is not None:
        yield walker
        walker = walker.parent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--skeleton", required=True, type=Path)
    parser.add_argument("--key", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    skeleton = args.skeleton.read_text(encoding="utf-8")
    key = bytes.fromhex(args.key.read_text(encoding="utf-8").strip())

    base = s2.tracked_copy(skeleton)
    if BASE_COPY.exists() and BASE_COPY.read_text(encoding="ascii") != base:
        raise SystemExit("this skeleton's tracked copy is not tests/fixtures/live2/company_people.html")

    text, counts = build(skeleton, key)
    assert all(ord(ch) < 128 for ch in text)
    args.out.write_text(text, encoding="ascii", newline="\n")
    print("base copy identical to the committed capture: %s" % BASE_COPY.exists())
    for name in sorted(counts):
        print("%-24s %d" % (name, counts[name]))
    print("lines differing from the base copy: %d" % sum(
        1 for a, b in zip(base.split("\n")[1:], text.split("\n")[len(HEADER.split("\n")) - 1:]) if a != b))
    print("sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
