"""Turn the live lane's skeletons of a GROUPS and an EVENTS search results page into committed fixtures: their STRUCTURE, with declared synthetic values only.

Kept as the PROVENANCE of ``tests/fixtures/synthetic/search_groups_live.html``
and ``tests/fixtures/synthetic/search_events_live.html``, the fixtures the
search-vertical readers (``linkedin_server/search_vertical_results.py``) are
built over: the exact record of what was taken from each capture and what was
put in its place.

THE INPUT IS ALREADY A SKELETON. The live lane loaded one groups search
(session 2, census row N 161) and one events search (session 3, census row
N 179), pressed nothing, and wrote each page with
``_probe_live_lane_session_2.skeleton_of``: tags, classes, roles and closed
ARIA states kept; LinkedIn's own words kept; EVERY OTHER TEXT NODE AND
ATTRIBUTE VALUE REPLACED BY ITS SHAPE, ``{L<letters>D<digits>n<length>:<keyed
hash>}``. So no title, id or address reaches this script -- only shapes, and
equal shapes for equal strings.

THE LIVE-TRUE SOURCE, AND WHY THIS SCRIPT DOES NOT READ IT. The live lane
committed each capture as a TRACKED copy, ``tests/fixtures/live2/n161.html``
and ``tests/fixtures/live3/n179.html``: every keyed text one ``x``, every
address segment that was a value one ``x``, ids kept as their hash. Those
copies are the live-true sources, and ``tests/test_search_vertical_fixtures.py``
holds this script's output to them: the STRUCTURE DIGEST this script prints
from a skeleton is the digest of the tracked copy's body. A tracked copy cannot
be this script's INPUT because it reduces exactly what a results reader needs
told apart -- WHICH result each of the two links in an event card names (the
copy writes every event id as one ``x``), and how long each id is.

THIS EXTENDS ``scripts/_build_named_profile_skeleton.py`` and reuses its
parser, walker, shape reduction, escaping, kept-attribute vocabularies and
structure digest by IMPORT, so the two builders cannot drift on what "reduced
to shape" or "the structure" means.

WHAT IS KEPT. Every element inside ``<body>``, with its tag and its nesting
(an ``<svg>`` stays, EMPTY: its drawing is dropped); the closed attribute
vocabularies the named-profile builder keeps (role, type, tabindex, dir,
target, hidden, disabled, checked and the aria states), each held to its
closed values; LinkedIn's own words, verbatim, from :data:`KEPT_WORDS`.

WHAT IS REPLACED, EVERY TIME:

    a RESULT's id -- the digits after
      /groups/ or /events/              -> a DECLARED SYNTHETIC DIGIT RUN OF THE
                                           SAME LENGTH: "1", then the result's
                                           number in order of first appearance,
                                           zero-padded (10001, 1000003,
                                           1000000000000000001). Two links that
                                           named one result still name one.
    every other address segment that is
      not one of LinkedIn's path words  -> "example"; the query and fragment
                                           dropped; an address on any other host
                                           DROPPED
    every id, and every attribute naming
      one (for, aria-labelledby,
      aria-describedby, aria-controls)  -> example-id-<n>, one per shape
    a shaped text with a letter or a
      digit -- every title, line, count
      and description                   -> REDUCED TO SHAPE: X and x for letters,
                                           9 for digits, spaces for the rest
                                           (the convention
                                           tests/test_fixtures_hold_only_synthetic_people.py
                                           accepts as nobody)
    a shaped text with neither          -> that many middle dots
    a shaped aria-label                 -> "Example label" (counted)
    a text or label that is NOT a shape,
      not one of LinkedIn's words kept
      and not a value this script writes-> "Example text" / "Example label",
                                           COUNTED: a hand edit does not survive
    class, style, componentkey, data-*,
      src, srcset, alt, value, title,
      xmlns and every other attribute    -> DROPPED

WELL-FORMED XHTML, ON PURPOSE. An event result is a link HOLDING a link to the
same event, which the live page builds with DOM calls and HTML's parser can
never produce (it closes the outer link at the inner one). So both fixtures are
written as XHTML -- void elements self-closed, a valueless boolean attribute
written as its own name -- and the tests load them through an XML parser, as
``tests/test_people_search_names.py`` loads the people-search fixture. The
groups page holds no nested link and is written the same way, so the two load
alike.

It PRINTS COUNTS ONLY -- never a shape's hash -- and writes no file but the
fixture. Run over its own output it reproduces it byte for byte (a FIXED POINT:
every value it writes is one it keeps), and it prints a STRUCTURE DIGEST --
tags and nesting only, the named-profile builder's own function -- which
``tests/test_search_vertical_fixtures.py`` pins.

    python scripts/_build_search_vertical_fixtures.py --vertical groups --skeleton <path> [--out <path>]
    python scripts/_build_search_vertical_fixtures.py --vertical events --skeleton <path> [--out <path>]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _build_named_profile_skeleton as named  # noqa: E402 -- the builder this one extends

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "tests" / "fixtures" / "synthetic"

#: The two verticals, each with its default output, the path word its result
#: links carry, the census row it serves and the live-true tracked copy.
VERTICALS = {
    "groups": {
        "out": FIXTURES / "search_groups_live.html",
        "word": "groups",
        "row": "N 161",
        "source": "tests/fixtures/live2/n161.html",
        "session": "session 2, 2026-09-28",
    },
    "events": {
        "out": FIXTURES / "search_events_live.html",
        "word": "events",
        "row": "N 179",
        "source": "tests/fixtures/live3/n179.html",
        "session": "session 3, 2026-09-28",
    },
}

#: LINKEDIN'S OWN WORDS THESE PAGES DRAW, kept verbatim: the words the live
#: lane's skeletons of the two pages kept, measured, every one on its closed
#: list (``_probe_live_lane_session_2.FURNITURE``, which the fixture test holds
#: this set to). A text node that is neither a shape, one of these, nor a value
#: this script writes becomes "Example text" and is COUNTED.
KEPT_WORDS = frozenset({
    "Home", "My Network", "Jobs", "Messaging", "Notifications", "Me", "For Business",
    "Learning", "Groups", "Events", "Join", "Previous", "Next", "About", "More",
})
#: And the labels they keep verbatim, on the same terms.
KEPT_LABELS = frozenset({"Dismiss", "For Business"})

PLACEHOLDER_TEXT = named.PLACEHOLDER_TEXT
PLACEHOLDER_LABEL = named.PLACEHOLDER_LABEL
PLACEHOLDER_SEGMENT = named.PLACEHOLDER_SEGMENT
DIGITS = re.compile(r"^[0-9]{1,25}$")
LINKEDIN_HOST = "www.linkedin.com"

HEADER = """<!DOCTYPE html>
<!--
  SKELETON OF A LIVE CAPTURE, WITH DECLARED SYNTHETIC VALUES ONLY. NOT A
  CAPTURE: no title, id or address here is anybody's.

  A LinkedIn {word} search results page, census row {row}, as LinkedIn drew it
  on the live lane's {session}: one search loaded, nothing pressed, the page
  written as a skeleton; scripts/_build_search_vertical_fixtures.py turned that
  skeleton into this file and says line by line what it kept and what it put
  in place.

  THE LIVE-TRUE SOURCE IS THE LIVE LANE'S TRACKED COPY of the same capture,
  {source}: every keyed text one x, ids kept as their hash. A test holds the
  two to one structure digest.

  KEPT: every element and its nesting; roles, types, tabindex and the closed
  ARIA states; LinkedIn's own words. REPLACED: each result's id by a declared
  synthetic digit run of the same length, in order of first appearance; every
  title, line, count and description REDUCED TO SHAPE (X, x, 9); every other
  address segment "example", queries dropped; ids example-id-n; shaped labels
  "Example label". DROPPED: classes, styles, component keys, data attributes,
  image sources and every other attribute.

  WELL-FORMED XHTML ON PURPOSE: an event result is a link holding a link, which
  only an XML parser keeps; the tests load both pages that way.
-->
"""


class Builder:
    """One skeleton (or this script's own output) in, one fixture out."""

    def __init__(self, tree: named.Tree, vertical: str) -> None:
        self.tree = tree
        self.vertical = vertical
        self.word = VERTICALS[vertical]["word"]
        self.counts = {
            "reduced text": 0, "dotted text": 0, "placeholder labels": 0,
            "ids mapped": 0, "result ids": 0, "addresses rebuilt": 0,
            "addresses dropped": 0, "unclassified text": 0,
            "unclassified labels": 0, "unclassified attributes": 0,
        }
        self.ids: dict[str, str] = {}
        self.result_ids: dict[str, str] = {}
        self.written = 0

    # -- values ----------------------------------------------------------------

    def text_for(self, value: str) -> str:
        """What a text node writes."""
        found = named.WHOLE_SHAPE.match(value)
        if not found:
            if (
                value in KEPT_WORDS
                or value == PLACEHOLDER_TEXT
                or named.REDUCED.match(value)
                or named.DOTS.match(value)
            ):
                return value
            self.counts["unclassified text"] += 1
            return PLACEHOLDER_TEXT
        letters, digits, length = (int(g) for g in found.groups())
        if letters == 0 and digits == 0:
            self.counts["dotted text"] += 1
            return chr(0x00B7) * max(1, length)
        self.counts["reduced text"] += 1
        return named.reduced(letters, digits, length)

    def id_for(self, value: str) -> str:
        if named.EXAMPLE_ID.match(value):
            return value
        if value not in self.ids:
            self.ids[value] = "example-id-%d" % (len(self.ids) + 1)
            self.counts["ids mapped"] += 1
        return self.ids[value]

    def result_id_for(self, segment: str) -> str:
        """A result's id: the declared synthetic run of the same length, by
        order of first appearance -- for a digits-only shape on a skeleton, or
        a digit run on this script's own output. Anything else is "example"."""
        found = named.WHOLE_SHAPE.match(segment)
        if found:
            letters, digits, length = (int(g) for g in found.groups())
            if letters or digits != length:
                return PLACEHOLDER_SEGMENT
        elif DIGITS.match(segment):
            length = len(segment)
        else:
            return PLACEHOLDER_SEGMENT
        if segment not in self.result_ids:
            number = str(len(self.result_ids) + 1)
            if len(number) >= length:
                return PLACEHOLDER_SEGMENT
            self.result_ids[segment] = "1" + number.zfill(length - 1)
            self.counts["result ids"] += 1
        return self.result_ids[segment]

    def address_for(self, href: str):
        """The address rebuilt, or ``None`` for one off LinkedIn's own host."""
        parts = urlsplit(href)
        if parts.netloc and parts.netloc != LINKEDIN_HOST:
            self.counts["addresses dropped"] += 1
            return None
        self.counts["addresses rebuilt"] += 1
        segments = parts.path.split("/")
        out = []
        for index, segment in enumerate(segments):
            if segment == "":
                out.append("")
            elif index == 2 and segments[1] == self.word:
                # /<word>/<id>/ -- a result's own address, as the capture
                # draws it, relative or on LinkedIn's host.
                out.append(self.result_id_for(segment))
            elif segment in named.PATH_WORDS:
                out.append(segment)
            else:
                out.append(PLACEHOLDER_SEGMENT)
        prefix = "https://" + LINKEDIN_HOST if parts.netloc else ""
        return prefix + "/".join(out)

    def label_for(self, value: str) -> str:
        if named.WHOLE_SHAPE.match(value):
            self.counts["placeholder labels"] += 1
            return PLACEHOLDER_LABEL
        if value in KEPT_LABELS or value == PLACEHOLDER_LABEL:
            return value
        self.counts["unclassified labels"] += 1
        return PLACEHOLDER_LABEL

    # -- writing ---------------------------------------------------------------

    def render(self) -> str:
        body = next(n for n in named.walk(self.tree.root) if n.tag == "body")
        config = VERTICALS[self.vertical]
        out = [
            HEADER.format(
                word=self.word, row=config["row"], session=config["session"],
                source=config["source"],
            ),
            '<html xmlns="http://www.w3.org/1999/xhtml" lang="en">\n'
            '<head><meta charset="utf-8" /><title>',
            named.escape("%s search results (synthetic skeleton)" % self.word.capitalize()),
            "</title></head>\n",
        ]
        self._write(body, out)
        out.append("\n</html>\n")
        return "".join(out)

    def _write(self, node, out) -> None:
        if isinstance(node, named.Text):
            out.append(named.escape(self.text_for(node.text)))
            return
        attrs = []
        for key, value in node.attrs:
            if key in named.KEPT:
                if value is None and key in named.BOOLEAN_KEPT:
                    attrs.append((key, key))
                elif value is not None and named.kept_value(key, value):
                    attrs.append((key, key if key in named.BOOLEAN_KEPT else value))
                else:
                    self.counts["unclassified attributes"] += 1
            elif value is None:
                continue
            elif key == "id":
                attrs.append((key, self.id_for(value)))
            elif key in named.ID_REFS:
                attrs.append((key, " ".join(self.id_for(v) for v in value.split())))
            elif key == "href" and node.tag == "a":
                address = self.address_for(value)
                if address is not None:
                    attrs.append((key, address))
            elif key == "aria-label":
                attrs.append((key, self.label_for(value)))
        self.written += 1
        rendered = "".join(
            ' %s="%s"' % (key, named.escape(value, quote=True)) for key, value in attrs
        )
        if node.tag in named.VOID:
            out.append("<%s%s />" % (node.tag, rendered))
            return
        out.append("<%s%s>" % (node.tag, rendered))
        if node.tag != "svg":
            for child in node.children:
                self._write(child, out)
        out.append("</%s>" % node.tag)


def result_links(tree: named.Tree, word: str) -> list:
    """Every ``<a>`` whose path is ``/<word>/<one segment>/`` -- a result's own
    address, as the capture draws it -- in document order."""
    found = []
    for node in named.walk(tree.root):
        if isinstance(node, named.Node) and node.tag == "a":
            parts = [p for p in urlsplit(node.get("href") or "").path.split("/") if p]
            if len(parts) == 2 and parts[0] == word:
                found.append(node)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--vertical", required=True, choices=sorted(VERTICALS))
    parser.add_argument("--skeleton", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    out_path = args.out or VERTICALS[args.vertical]["out"]
    tree = named.Tree()
    tree.feed(args.skeleton.read_text(encoding="utf-8"))
    tree.close()
    builder = Builder(tree, args.vertical)
    text = builder.render()
    assert all(ord(ch) < 128 for ch in text)
    out_path.write_text(text, encoding="ascii", newline="\n")
    body = next(n for n in named.walk(tree.root) if n.tag == "body")
    links = result_links(tree, builder.word)
    print("vertical           %s" % args.vertical)
    print("elements written   %d" % builder.written)
    print("result links       %d" % len(links))
    print("distinct results   %d" % len(builder.result_ids))
    for key in sorted(builder.counts):
        print("%-18s %d" % (key, builder.counts[key]))
    print("structure digest %s" % named.structure_digest(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
