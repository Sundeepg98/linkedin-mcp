"""Which of LinkedIn's FIXED labels a live lane's KEYED skeleton draws -- read offline, by keyed shape, from a closed vocabulary only.

## WHY THIS EXISTS

The live lane writes every capture as a skeleton
(``_probe_live_lane_session_2.skeleton_of``): tags, classes, roles and closed
ARIA states kept, a closed list of LinkedIn's own words kept verbatim
(``FURNITURE``), and EVERY OTHER text and attribute value replaced by its
keyed SHAPE, ``{L<letters>D<digits>n<length>:<8-hex HMAC>}``, under a key made
for that session and kept beside its captures. So a builder reading a
skeleton cannot see a menu entry or a filter label that is not on that list:
``Not interested`` and ``Actively hiring`` read as ``{L13D0n14:...}`` and
``{L14D0n15:...}``. With the session's key on this box, the shape of a
CANDIDATE string can be computed by the same function and compared: an equal
shape is the label, measured -- the 8-hex mark under a key, together with
equal letter, digit and length counts, makes an accidental equality
negligible.

Lane B2 (2026-10-10) read seventeen BUILD rows this way before building any
of them (``_audit/2026-10-10-lane-b2-network-build.md``, section 1), and
twelve of the captures turned out not to draw what their row needed.

## WHAT IT MAY TEST: ITS OWN CLOSED VOCABULARY, AND NOTHING A CALLER TYPES

``FIXED-UI-LABEL-MATCH`` (the orchestrator, 2026-10-10): a fixed product label
is not third-party text. The hazard is the opposite use of the same key: a
list of NAMES tested against a skeleton reverses exactly what the key exists
to protect. So the candidates are this file's literals, :data:`VOCABULARY`,
each one of LinkedIn's interface strings, and THERE IS NO ARGUMENT THAT TAKES
A LABEL -- ``tests/test_verify_fixed_labels.py`` asserts the parser's options.
A new label is an edit here, reviewed like any other.

## WHAT IT PRINTS, AND WHAT IT NEVER PRINTS

For each vocabulary label: how many text nodes and attribute values of the
skeleton equal it -- verbatim, where the skeleton kept LinkedIn's word, or by
keyed shape. Never a hash, never the key, never the shape of a value that
matched nothing, never any text of the page.

## WHAT IT CANNOT SAY

* An exact check. A decorated label (``School (3)``) neither matches
  ``School`` nor is excluded by its zero.
* A label outside the vocabulary is not tested at all; its absence from the
  output says nothing.
* A match says the string is on the page -- not which control carries it,
  nor whether that control is visible.
* The key must be the SKELETON'S OWN SESSION'S. A wrong key reads 0 for every
  shaped label and still counts the verbatim ones; the test file shows it.

    python scripts/verify_fixed_labels.py --skeleton <keyed skeleton> --key <that session's shape.key>
"""
from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_ROOT / "scripts"))

#: LinkedIn's fixed interface strings this instrument may test, by the
#: surface each was read on. Every entry is a label LinkedIn writes for every
#: member alike -- never a name, a title, a company or a post's words.
VOCABULARY: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("a feed item and its control menu", (
        "Feed post", "Save", "Unsave", "Copy link to post", "Embed this post",
        "Not interested", "Report post", "Unfollow", "Mute", "Hide post",
        "Hide this post",
    )),
    ("an ad's own flow in the feed", (
        "Why am I seeing this ad?", "Hide or report this ad", "Report this ad",
        "Hide this ad",
    )),
    ("the people search's filter bar", (
        "People", "All filters", "Actively hiring", "Current companies",
        "Past companies", "Current company", "Past company", "Locations",
        "Network", "1st", "2nd", "3rd+", "Connections", "School", "Schools",
        "Industry", "Industries", "Keywords", "First name", "Last name",
        "Title", "Company", "Show results", "Reset",
    )),
    ("a Page's People tab", (
        "Where they live", "Where they studied", "What they do",
        "What they are skilled at", "What they studied",
    )),
)

#: Every attribute a label can sit in: the label attributes the skeleton
#: knows, and the rest are counted too -- a label equal by keyed shape is the
#: label wherever it stands.
_VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                   "link", "meta", "param", "source", "track", "wbr"})


def labels() -> tuple[str, ...]:
    """The vocabulary, flattened, in order. PURE."""
    return tuple(label for _surface, group in VOCABULARY for label in group)


class _Values(HTMLParser):
    """Every text node (whitespace collapsed) and every attribute value."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        for _name, value in attrs:
            if value:
                self.values.append(" ".join(value.split()))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if text:
            self.values.append(text)


def count_labels(skeleton_text: str, key: bytes) -> dict[str, int]:
    """``{label: matches}`` for every vocabulary label. PURE.

    A value matches a label when it IS the label (the skeleton kept it
    verbatim) or when it is the label's keyed shape under ``key``, computed
    by the live lane's own :func:`value_shape` -- imported, never re-written.
    """
    from _probe_live_lane_session_2 import value_shape  # noqa: PLC0415

    parser = _Values()
    parser.feed(skeleton_text)
    parser.close()
    tally: dict[str, int] = {}
    for value in parser.values:
        tally[value] = tally.get(value, 0) + 1
    out: dict[str, int] = {}
    for label in labels():
        out[label] = tally.get(label, 0) + tally.get(value_shape(label, key), 0)
    return out


def read_key(path: Path) -> bytes:
    """A session key as the live lane writes it: hex, one line."""
    return bytes.fromhex(path.read_text(encoding="utf-8").strip())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--skeleton", required=True, type=Path,
                        help="a live lane's keyed skeleton (*.skeleton.html)")
    parser.add_argument("--key", required=True, type=Path,
                        help="that session's shape.key")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        key = read_key(args.key)
        text = args.skeleton.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print("refused: %s (%s)" % (type(exc).__name__, "the skeleton or the key is unreadable"))
        return 2
    counts = count_labels(text, key)
    for surface, group in VOCABULARY:
        print("== %s" % surface)
        for label in group:
            print("   %-28s %d" % (label, counts[label]))
    found = sum(1 for n in counts.values() if n)
    print("%d of %d vocabulary labels drawn" % (found, len(counts)))
    print("NOT SAID: a decorated label (an exact check neither matches nor excludes it);"
          " any label outside the vocabulary; which control carries a match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
