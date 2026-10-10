"""Turn the live lane's capture of AUDIENCE ANALYTICS into a tracked skeleton fixture.

Kept as the PROVENANCE of ``tests/fixtures/live1/audience.html`` (census row
``P L1``): the exact record of what was carried over from the capture and what
was invented, which is what a privacy review needs and cannot get from the
output.

THE CAPTURE. The live lane's session 1 loaded
``https://www.linkedin.com/analytics/creator/audience/`` once on 2026-09-23 and
kept the page RAW in its gitignored ``_state/`` (``_audit/2026-09-23-live-lane-
session-1.md``, Entry 5). The page is follower DEMOGRAPHICS: aggregated other
people. It also draws his profile card in an ``aside``. The raw is read here and
never copied into the tree.

HOW IT IS REDUCED. ``skeleton_of`` and ``tracked_copy`` are IMPORTED from
``scripts/_probe_live_lane_session_2.py``, not copied, so this file keeps every
one of their rules: tags, attribute names, classes, roles and closed ARIA states
kept; every other text node and attribute value replaced by a keyed shape, then
by ONE ``x``; ids kept as ``k`` and their keyed hash so a label still finds its
control; scripts, styles and templates dropped. The key is SECRET and stays on
the box that built the file (``--key``); it is never committed.

WHAT IS CARRIED OVER BEYOND THE SKELETON, AND EACH ONE IS VERIFIED. Only the UI
words the reader ``linkedin_server.audience_analytics`` aims at, each restored
at a text node whose keyed shape EQUALS the keyed shape of the word (an HMAC
comparison under the build key; no other text is ever compared or restored):

* ``Total followers`` -- the label beside the follower count;
* ``All`` -- the demographics nav's current button (``aria-current="true"``);
* ``Job title``, ``Location``, ``Seniority``, ``Company``, ``Industry``,
  ``Company size`` -- the six dimension buttons in that nav, and the dimension
  word above each entry the panel draws.

WHAT IS INVENTED, AND IT IS EVERY VALUE. The capture's follower count becomes
``1,250``; each drawn entry's label and share become a DECLARED SYNTHETIC pair
(:data:`SYNTHETIC_ENTRIES`), placed by STRUCTURE: the entry is the nearest
``div`` above a ``role="progressbar"`` that holds a direct ``p`` (its dimension
word), and of the two ``p`` beneath its inner ``div`` the SHARE is the one whose
keyed shape equals the shape of some ``N%`` with N in 0..100, the label the
other. One entry, the ``Company`` one, is planted RARE on purpose: a
capitalised run in a label drawn once, so ``census_redact_rare`` fires on the
fixture itself. Both ``aside`` elements -- his profile card and the right rail
-- are dropped whole and replaced by an empty ``<aside></aside>``, so nothing of
the card reaches the file even as a shape.

MEASURED ON THE CAPTURE when this was written (2026-10-10, counts only): one
``nav`` of four holds the dimension buttons (six of its seven buttons; the
seventh is ``All``, the only one with ``aria-current``); six progressbars, one
per dimension, each entry pairing exactly one share-shaped ``p`` with one label
``p``; the ``Total followers`` label's parent holds exactly one other text, an
integer.

Run::

    python scripts/_build_audience_fixture.py --capture <raw> --key <keyfile>
    python scripts/_build_audience_fixture.py --capture <raw> --key <keyfile> --check

It prints counts only -- never a text, an id or a key. ``--check`` re-derives
the fixture from the capture and the key ON THIS BOX and compares it byte for
byte with the tracked file, exiting non-zero on any difference or refusal.
"""
from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _probe_live_lane_session_2 import (  # noqa: E402  -- imported, never copied
    skeleton_of,
    tracked_copy,
    value_shape,
)

DEFAULT_OUT = ROOT / "tests" / "fixtures" / "live1" / "audience.html"

#: The six demographic dimensions, in LinkedIn's own words.
DIMENSIONS = ("Job title", "Location", "Seniority", "Company", "Industry", "Company size")

#: The nav's view word, drawn on the button ``aria-current`` marks.
VIEW_ALL = "All"

#: The label beside the follower count.
TOTAL_LABEL = "Total followers"

#: DECLARED SYNTHETIC values, keyed by the dimension word above each entry.
#: ``Company`` is the planted RARE entry: a capitalised run, drawn once.
SYNTHETIC_ENTRIES: dict[str, tuple[str, str]] = {
    "Industry": ("Example industry", "31%"),
    "Seniority": ("Example seniority", "24%"),
    "Job title": ("Example title", "9%"),
    "Location": ("Example location", "40%"),
    "Company size": ("Example size band", "18%"),
    "Company": ("Example Company Two", "3%"),
}

#: The follower count planted in place of the capture's.
SYNTHETIC_TOTAL = "1,250"

VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                  "link", "meta", "param", "source", "track", "wbr"})

HEADER = (
    "<!-- SYNTHETIC: built by scripts/_build_audience_fixture.py from one capture of\n"
    "     the audience-analytics page. The structure is the capture's; every text is\n"
    "     one x except the reader's UI words, each verified by keyed hash, and every\n"
    "     value is invented (see the builder's docstring). The asides are dropped. -->"
)


class Refused(Exception):
    """The capture does not hold the structure this builder records."""


class _Node:
    def __init__(self, tag: str, attrs: dict, parent: Optional["_Node"], line: int) -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.start = line
        self.end = line
        self.kids: list[_Node] = []
        self.texts: list[tuple[int, str]] = []


class _LineTree(HTMLParser):
    """The skeleton as a tree that remembers the LINE of every token. The
    skeleton writes one token per line, so a line names a text exactly."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", {}, None, 0)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, dict(attrs), self.cur, self.getpos()[0])
        self.cur.kids.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(_Node(tag, dict(attrs), self.cur, self.getpos()[0]))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            n.end = self.getpos()[0]
            self.cur = n.parent

    def handle_data(self, data):
        text = " ".join(data.split())
        if text:
            self.cur.texts.append((self.getpos()[0], text))


def _walk(node: _Node):
    yield node
    for kid in node.kids:
        yield from _walk(kid)


def _texts_under(node: _Node) -> list[tuple[int, str]]:
    out = list(node.texts)
    for kid in node.kids:
        out.extend(_texts_under(kid))
    return out


def _entry_of(bar: _Node) -> Optional[_Node]:
    """The nearest ``div`` above a progressbar that holds a direct ``p``."""
    node = bar.parent
    while node is not None:
        if node.tag == "div" and any(k.tag == "p" for k in node.kids):
            return node
        node = node.parent
    return None


def build(capture_text: str, key: bytes) -> tuple[str, dict[str, int]]:
    """The tracked fixture and the counts printed about it. PURE but for the key."""
    skeleton = skeleton_of(capture_text, key)
    lines = skeleton.split("\n")
    tree = _LineTree()
    tree.feed(skeleton)
    tree.close()
    nodes = list(_walk(tree.root))
    replace: dict[int, str] = {}
    counts: dict[str, int] = {"elements": len(nodes) - 1}

    def restore(line: int, token: str, word: str) -> bool:
        if token == value_shape(word, key):
            replace[line] = word
            return True
        return False

    # 1. The demographics nav: the one nav whose buttons carry dimension words.
    navs = []
    for nav in (n for n in nodes if n.tag == "nav"):
        buttons = [b for b in _walk(nav) if b.tag == "button"]
        tokens = [_texts_under(b) for b in buttons]
        if any(len(t) == 1 and t[0][1] in {value_shape(d, key) for d in DIMENSIONS} for t in tokens):
            navs.append((nav, buttons, tokens))
    if len(navs) != 1:
        raise Refused(f"{len(navs)} navs carry a dimension button, where exactly one is required")
    _, buttons, tokens = navs[0]
    counts["nav_buttons"] = len(buttons)
    current = [b for b in buttons if b.attrs.get("aria-current") == "true"]
    if len(current) != 1:
        raise Refused(f"{len(current)} nav buttons carry aria-current, where exactly one is required")
    restored_tabs = 0
    for button, toks in zip(buttons, tokens):
        if len(toks) != 1:
            raise Refused("a nav button does not hold exactly one text")
        line, token = toks[0]
        words = (VIEW_ALL,) if button is current[0] else DIMENSIONS
        if not any(restore(line, token, w) for w in words):
            raise Refused("a nav button's text is no word this builder restores")
        restored_tabs += 1
    counts["tab_words_restored"] = restored_tabs

    # 2. The drawn entries, one per progressbar.
    seen: dict[str, int] = {}
    shares = {value_shape(f"{n}%", key) for n in range(101)}
    bars = [n for n in nodes if n.attrs.get("role") == "progressbar"]
    counts["progressbars"] = len(bars)
    for bar in bars:
        entry = _entry_of(bar)
        if entry is None:
            raise Refused("a progressbar has no entry container")
        heads = [k for k in entry.kids if k.tag == "p"]
        if len(heads) != 1 or len(_texts_under(heads[0])) != 1:
            raise Refused("an entry does not hold exactly one dimension word")
        line, token = _texts_under(heads[0])[0]
        word = next((d for d in DIMENSIONS if restore(line, token, d)), None)
        if word is None:
            raise Refused("an entry's dimension word is no dimension this builder knows")
        seen[word] = seen.get(word, 0) + 1
        pair = [p for k in entry.kids if k.tag == "div" for p in k.kids if p.tag == "p"]
        pair_texts = [_texts_under(p) for p in pair]
        if len(pair) != 2 or any(len(t) != 1 for t in pair_texts):
            raise Refused("an entry does not pair exactly one label with one share")
        is_share = [t[0][1] in shares for t in pair_texts]
        if sum(is_share) != 1:
            raise Refused("an entry does not hold exactly one share-shaped text")
        label, share = SYNTHETIC_ENTRIES[word]
        for t, flag in zip(pair_texts, is_share):
            replace[t[0][0]] = share if flag else label
    if sorted(seen) != sorted(DIMENSIONS) or any(v != 1 for v in seen.values()):
        raise Refused("the entries do not draw each dimension exactly once")
    counts["entries_planted"] = len(bars)

    # 3. The follower count beside its label.
    labels = [(n, line) for n in nodes for line, tok in n.texts if tok == value_shape(TOTAL_LABEL, key)]
    if len(labels) != 1:
        raise Refused(f"{len(labels)} texts read {TOTAL_LABEL!r}, where exactly one is required")
    label_node, label_line = labels[0]
    replace[label_line] = TOTAL_LABEL
    others = [(ln, tok) for ln, tok in _texts_under(label_node.parent) if ln != label_line]
    if len(others) != 1:
        raise Refused("the follower label's parent does not hold exactly one other text")
    number_line, number_token = others[0]
    if not any(number_token in (value_shape(str(n), key), value_shape(f"{n:,}", key))
               for n in range(100000)):
        raise Refused("the text beside the follower label is not an integer under 100000")
    replace[number_line] = SYNTHETIC_TOTAL

    # 4. The asides: dropped whole. Only the OUTERMOST ones, each to the last
    # line any of its descendants reaches -- so an aside the parser never saw
    # closed cannot leave its children behind.
    def inside_aside(node: _Node) -> bool:
        up = node.parent
        while up is not None:
            if up.tag == "aside":
                return True
            up = up.parent
        return False

    asides = [n for n in nodes if n.tag == "aside" and not inside_aside(n)]
    dropped: set[int] = set()
    stubs: set[int] = set()
    for aside in asides:
        last = max([aside.end] + [d.end for d in _walk(aside)] + [ln for ln, _ in _texts_under(aside)])
        dropped.update(range(aside.start, last + 1))
        stubs.add(aside.start)
    counts["asides_dropped"] = len(asides)
    counts["aside_lines_dropped"] = len(dropped)

    out_lines = []
    for number, text in enumerate(lines, start=1):
        if number in stubs:
            out_lines.append("<aside></aside>")
        elif number in dropped:
            continue
        elif number in replace:
            out_lines.append(replace[number])
        else:
            out_lines.append(text)
    tracked = tracked_copy("\n".join(out_lines))
    head, _, body = tracked.partition("\n")
    html = head + "\n" + HEADER + "\n" + body + "\n"
    html.encode("ascii")  # strict ASCII, or this raises before anything is written
    counts["bytes"] = len(html)
    return html, counts


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capture", type=Path, required=True, help="the raw audience capture")
    ap.add_argument("--key", type=Path, required=True, help="the SECRET hex key file")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true", help="re-derive and compare, write nothing")
    args = ap.parse_args(argv)
    key = bytes.fromhex(args.key.read_text(encoding="utf-8").strip())
    try:
        html, counts = build(args.capture.read_text(encoding="utf-8", errors="replace"), key)
    except Refused as why:
        print(f"REFUSED: {why}")
        return 1
    print("counts:", counts)
    if args.check:
        same = args.out.exists() and args.out.read_bytes() == html.encode("ascii")
        print(f"{args.out.name}: {'MATCHES the re-derivation' if same else 'DIFFERS from the re-derivation'}")
        return 0 if same else 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(html.encode("ascii"))
    print(f"wrote {args.out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
