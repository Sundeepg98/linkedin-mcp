"""Turn the live lane's session-7 skeleton of ONE named profile into a committed fixture that keeps what the session-2 fixture drops: the topcard's own people-search links and the Activity section's item keys.

Kept as the PROVENANCE of ``tests/fixtures/synthetic/named_profile_activity.html``,
the fixture lane NP's reader of the named profile's HANDLES
(``named_handles.read_handles`` over ``dom.read_named_profile_handles``) is
built over, 2026-10-10. It is a SUBCLASS of
``scripts/_build_named_profile_skeleton.py`` and keeps every rule that builder
states -- read its docstring first: the input is already a skeleton (every text
and attribute value a shape, ``{L<letters>D<digits>n<length>:<8-hex keyed
hash>}``), no name, slug or id reaches this script, and every value it writes is
a declared synthetic one or LinkedIn's own words.

WHY A SECOND FIXTURE, AND NOT AN EDIT OF THE FIRST. The session-2 builder drops
the query of every address but the composer's, and writes any shaped path
segment as ``example``: so its fixture holds no ``connectionOf`` value and no
activity key, which are exactly the two handles this lane returns. That builder
is pinned to its own fixed point and its structure digest by
``tests/test_named_profile_live_skeleton.py``; this one leaves it untouched and
adds, ONLY here:

    /feed/update/urn:li:activity:<shape>/   -> the same path, the activity id a
                                               DECLARED synthetic one
                                               (tests/test_no_committed_identity
                                               .SYNTHETIC_IDS), one per distinct
                                               shape, in order of first appearance
    /search/results/people/?origin=..&connectionOf=..&network=..
                                            -> the same keys IN THE SAME ORDER;
                                               origin "example"; connectionOf the
                                               OWNER's synthetic member id in a JSON
                                               list, raw or percent-encoded as the
                                               shape's length says; network
                                               ["F","S"] raw or ["F"] encoded, as
                                               its shape says (DERIVED from shapes,
                                               as lane L5 derived them on 2026-09-28)
    an aria-label whose shape is the item
      overflow prefix plus the owner's
      name's shape                          -> "Open control menu for post by
                                               <OWNER>"   (DERIVED: the measured
                                               prefix, dom.ACTIVITY_OVERFLOW_PREFIX,
                                               24 letters and 30 characters, plus a
                                               name of the topcard heading's shape)
    the reaction toggle's two state shapes  -> dom.REACTION_OFF_LABEL and
                                               "Reaction button state: Like"
                                               (DERIVED from their shapes; both
                                               strings are measured elsewhere)
    the reactions-menu shape                -> "Open reactions menu"   (DERIVED)

WHAT THE SESSION-7 CAPTURE SHOWS, counted by this script and printed (counts
only, never a hash): the topcard's container id is the 80-character shape the
session-2 builder derives the Topcard id from; the topcard draws two composer
links naming one member, and three people-search links carrying connectionOf;
the Activity section draws two items, five permalinks between them, and each
item's actor links are the topcard's own member link.

    python scripts/_build_named_profile_activity_skeleton.py --skeleton <path> [--out <path>]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _build_named_profile_skeleton as base  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "tests" / "fixtures" / "synthetic" / "named_profile_activity.html"

#: Declared synthetic activity ids (tests/test_no_committed_identity.SYNTHETIC_IDS),
#: handed out in order of first appearance.
ACTIVITY_IDS = ("7400000000000000001", "7400000000000000002", "7400000000000000003")
OVERFLOW_PREFIX = "Open control menu for post by "
REACTION_OFF = "Reaction button state: no reaction"
REACTION_ON = "Reaction button state: Like"
REACTIONS_MENU = "Open reactions menu"
ORIGIN_PLACEHOLDER = "example"

_ACTIVITY_PATH = re.compile(
    r"^/feed/update/urn:li:activity:(\{L\d+D\d+n\d+:[0-9a-f]{8}\}|[0-9]{1,25})/$"
)


def _letters(text):
    return sum(ch.isalpha() for ch in text)


def _digits(text):
    return sum(ch.isdigit() for ch in text)


class ActivityBuilder(base.Builder):
    """The session-2 builder, keeping the two handles' addresses and labels."""

    def __init__(self, tree):
        super().__init__(tree)
        self.activities = {}
        self.counts.update({"activity keys": 0, "people-search queries": 0,
                            "overflow labels": 0, "reaction labels": 0})

    def locate(self):
        super().locate()
        found = base.WHOLE_SHAPE.match(self.name_value)
        if found:
            letters, digits, length = (int(g) for g in found.groups())
        else:
            letters, digits, length = (
                _letters(self.name_value), _digits(self.name_value), len(self.name_value))
        self.overflow_shape = (
            _letters(OVERFLOW_PREFIX) + letters, digits, len(OVERFLOW_PREFIX) + length)
        self.member_length = len(base.OWNER_MEMBER_ID)

    # -- the activity keys ---------------------------------------------------

    def activity_id_for(self, key):
        if key in ACTIVITY_IDS:
            return key
        if key not in self.activities:
            self.activities[key] = ACTIVITY_IDS[len(self.activities) % len(ACTIVITY_IDS)]
        return self.activities[key]

    # -- the people-search query ---------------------------------------------

    def _member_list(self, value):
        """``connectionOf``'s value: the owner's synthetic id in a JSON list,
        raw or encoded as the shape (or the value already written) says."""
        encoded = '%5B%22' + base.OWNER_MEMBER_ID + '%22%5D'
        raw = '["' + base.OWNER_MEMBER_ID + '"]'
        if value in (encoded, raw):
            return value
        found = base.WHOLE_SHAPE.match(unquote(value))
        length = int(found.group(3)) if found else len(value)
        return encoded if length == self.member_length + 12 else raw

    @staticmethod
    def _degree_list(value):
        """``network``'s value as its shape says: ``["F","S"]`` raw (9
        characters, 2 letters) or ``["F"]`` encoded (13, 3 letters)."""
        if value in ('["F","S"]', '%5B%22F%22%5D'):
            return value
        found = base.WHOLE_SHAPE.match(unquote(value))
        length = int(found.group(3)) if found else len(value)
        return '%5B%22F%22%5D' if length == 13 else '["F","S"]'

    def address_for(self, node, href):
        parts = urlsplit(href)
        if parts.netloc and parts.netloc != "www.linkedin.com":
            return super().address_for(node, href)
        prefix = "https://www.linkedin.com" if parts.netloc else ""
        found = _ACTIVITY_PATH.match(parts.path)
        if found:
            self.counts["addresses rebuilt"] += 1
            self.counts["activity keys"] += 1
            return (prefix + "/feed/update/urn:li:activity:"
                    + self.activity_id_for(found.group(1)) + "/")
        if parts.path == "/search/results/people/" and "connectionOf=" in parts.query:
            self.counts["addresses rebuilt"] += 1
            self.counts["people-search queries"] += 1
            query = []
            for pair in parts.query.split("&"):
                name, _eq, value = pair.partition("=")
                if name == "origin":
                    query.append("origin=" + ORIGIN_PLACEHOLDER)
                elif name == "connectionOf":
                    query.append("connectionOf=" + self._member_list(value))
                elif name == "network":
                    query.append("network=" + self._degree_list(value))
            return prefix + parts.path + "?" + "&".join(query)
        return super().address_for(node, href)

    # -- the item labels -------------------------------------------------------

    def label_for(self, node, value):
        overflow = OVERFLOW_PREFIX + base.OWNER
        if value in (overflow, REACTION_OFF, REACTION_ON, REACTIONS_MENU):
            return value
        found = base.WHOLE_SHAPE.match(value)
        if found and node.tag == "button":
            shape = tuple(int(g) for g in found.groups())
            if shape == self.overflow_shape:
                self.counts["overflow labels"] += 1
                return overflow
            for label in (REACTION_OFF, REACTION_ON, REACTIONS_MENU):
                if shape == (_letters(label), _digits(label), len(label)):
                    self.counts["reaction labels"] += 1
                    return label
        return super().label_for(node, value)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--skeleton", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    tree = base.Tree()
    tree.feed(args.skeleton.read_text(encoding="utf-8"))
    tree.close()
    builder = ActivityBuilder(tree)
    text = builder.render()
    text = text.replace(
        "<!doctype html>\n<!--\n",
        "<!doctype html>\n<!--\n  LANE NP, 2026-10-10: built by "
        "scripts/_build_named_profile_activity_skeleton.py from the live lane's\n"
        "  SESSION-7 skeleton of one first-degree profile the operator named; it keeps\n"
        "  the topcard's people-search queries and the Activity section's item keys,\n"
        "  as declared synthetic values. Everything below is the session-2 builder's.\n\n",
        1,
    )
    assert all(ord(ch) < 128 for ch in text)
    args.out.write_text(text, encoding="ascii", newline="\n")
    body = next(n for n in base.walk(tree.root) if n.tag == "body")
    print("elements written   %d" % builder.written)
    print("topcard container  id shape %s" % builder.container_shape)
    print("action rows        %d, the second hidden" % builder.rows)
    for key in sorted(builder.counts):
        print("%-22s %d" % (key, builder.counts[key]))
    print("activity items     %d distinct" % len(builder.activities))
    print("other people       %d synthetic slugs" % len(builder.slugs))
    print("structure digest %s" % base.structure_digest(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
