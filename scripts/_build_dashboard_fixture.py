"""Turn the captured ANALYTICS HUB (/dashboard/) into its tracked skeleton fixture.

Kept as the PROVENANCE of ``tests/fixtures/live1/overview.html`` (census row
``P L8``): the exact record of what was carried over from the live capture and
what was invented, which is what a privacy review needs and cannot get from
the output.

THE CAPTURE. The live lane's session 1 loaded ``/dashboard/`` on 2026-09-23
(``_audit/2026-09-23-live-lane-session-1.md``, Entry 5) and kept the page raw
under the gitignored ``_state/`` directory as ``l1-overview.html``. The raw is
never committed: it draws his profile card (name, headline) in an ``aside``
and his own analytics numbers in the cards.

HOW THE PAGE IS REDUCED. ``skeleton_of`` and ``tracked_copy`` are IMPORTED
from ``scripts/_probe_live_lane_session_2.py``, never copied, so this fixture
obeys every rule the session-2 skeletons obey: tags, classes, roles, ARIA
states and LinkedIn's own path words are kept; every text node and every
other attribute value becomes ONE ``x``; an id and every attribute naming it
become ``k`` plus an 8-hex keyed hash. The hashing key is SECRET: it is read
from ``--key``, kept on this box, and never committed, so an id hash in the
fixture cannot be tested against a list of names.

WHAT IS CARRIED OVER, beyond that structure. Restored by KEYED HASH -- each
word is put back only where its keyed shape is found, inside one metric card,
at the node the reader reads, and the build refuses if any expected node is
missing or holds anything else:

* the four card addresses' path words ``creator``, ``audience``,
  ``profile-views`` and ``search-appearances`` (``analytics`` and ``content``
  are already the skeleton's path words), so each card links to
  ``/analytics/creator/content/``, ``/analytics/creator/audience/``,
  ``/analytics/profile-views/`` and ``/analytics/search-appearances/``;
* three card labels, LinkedIn's words: ``Post impressions in 7 days``,
  ``Total followers``, ``Profile viewers in 90 days``;
* the comparison phrase ``vs. prior 7 days``, on the three cards that draw it;
* the delta icons' ids, LinkedIn's icon names: ``caret-small`` on the
  impressions card and ``caret-up-small`` on the followers and profile-viewers
  cards. The search-appearances card draws no icon, and none is added.

WHAT IS INVENTED, AND IT IS DECLARED. Every card's value and delta
(:data:`SYNTHETIC_VALUES`, :data:`SYNTHETIC_DELTAS`); and the
search-appearances card's dated label and comparison phrase, whose shapes were
measured on the capture -- ``Search appearances <Mon> <d><EN DASH><d>`` and
``vs. <Mon> <d><EN DASH><d>`` -- and whose dates are invented
(:data:`SYNTHETIC_DATED_LABEL`, :data:`SYNTHETIC_DATED_PERIOD`). No number of
his reaches the committed file, and no text of anyone's.

Re-run only after re-capturing the page:

    python scripts/_build_dashboard_fixture.py --capture <raw> --key <secret key file>
    python scripts/_build_dashboard_fixture.py --capture <raw> --key <secret key file> --check

It prints counts only -- never a text, an id, a value or a key. ``--check``
re-derives the fixture in memory and compares it byte for byte with the
tracked file; it can only run on a box that holds the raw and the key.
"""
from __future__ import annotations

import argparse
import html as html_escape
import pathlib
import re
import sys
from html.parser import HTMLParser
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _probe_live_lane_session_2 import (  # noqa: E402  (imported, never copied)
    skeleton_of,
    tracked_copy,
    value_shape,
)

DEFAULT_OUT = ROOT / "tests" / "fixtures" / "live1" / "overview.html"

#: Path words the reader needs, restored where their keyed shape stands.
RESTORED_PATH_WORDS = ("creator", "audience", "profile-views", "search-appearances")

#: The card addresses, by LinkedIn's path words: what each card must link to
#: once the words above are restored. Also the build's own check.
CARD_PATHS = {
    "/analytics/creator/content/": "post_impressions",
    "/analytics/creator/audience/": "followers",
    "/analytics/profile-views/": "profile_viewers",
    "/analytics/search-appearances/": "search_appearances",
}

#: LinkedIn's label words, each restored only on the card whose address
#: names the same metric.
RESTORED_LABELS = {
    "Post impressions in 7 days": "post_impressions",
    "Total followers": "followers",
    "Profile viewers in 90 days": "profile_viewers",
}
RESTORED_PERIOD = "vs. prior 7 days"
RESTORED_ICONS = ("caret-small", "caret-up-small")

EN_DASH = chr(0x2013)
_MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
#: The two dated shapes measured on the search-appearances card.
DATED_LABEL = re.compile(r"^Search appearances " + _MONTH + r" [0-9]{1,2}" + EN_DASH + r"[0-9]{1,2}$")
DATED_PERIOD = re.compile(r"^vs\. " + _MONTH + r" [0-9]{1,2}" + EN_DASH + r"[0-9]{1,2}$")

#: DECLARED SYNTHETIC. Invented values, one per card, by metric.
SYNTHETIC_VALUES = {
    "post_impressions": "41",
    "followers": "512",
    "profile_viewers": "63",
    "search_appearances": "27",
}
#: DECLARED SYNTHETIC. Invented delta magnitudes, LinkedIn's "<n>%" shape.
#: The search-appearances card draws no direction icon, so its delta is 0.
SYNTHETIC_DELTAS = {
    "post_impressions": "12%",
    "followers": "3%",
    "profile_viewers": "50%",
    "search_appearances": "0%",
}
SYNTHETIC_DATED_LABEL = "Search appearances Jan 12" + EN_DASH + "18"
SYNTHETIC_DATED_PERIOD = "vs. Jan 5" + EN_DASH + "11"

_VALUE = re.compile(r"^[0-9]{1,3}(?:,[0-9]{3})*$")
_DELTA = re.compile(r"^[0-9]{1,4}%$")
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
         "param", "source", "track", "wbr"}
_DROPPED = {"script", "style", "noscript", "code", "template"}

HEADER = (
    "<!-- SKELETON: built by scripts/_build_dashboard_fixture.py from the live lane's\n"
    "     session-1 capture of /dashboard/ (census row P L8). Structure only; every text\n"
    "     is x except the UI words restored by keyed hash, and every value, delta and\n"
    "     date is DECLARED SYNTHETIC (see the builder's docstring). -->\n"
)


class _Node:
    def __init__(self, tag: str, attrs: dict, parent: Optional["_Node"]) -> None:
        self.tag, self.attrs, self.parent = tag, attrs, parent
        self.children: list = []

    def kids(self) -> list["_Node"]:
        return [c for c in self.children if isinstance(c, _Node)]


class _Tree(HTMLParser):
    """The raw page as a tree, with the skeleton's own text normalisation and
    its dropped elements, so a node here and a shape there are the same text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", {}, None)
        self.cur = self.root
        self.dropping = 0

    def handle_starttag(self, tag, attrs):
        if tag in _DROPPED:
            self.dropping += 1
            return
        if self.dropping:
            return
        node = _Node(tag, dict(attrs), self.cur)
        self.cur.children.append(node)
        if tag not in _VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        if tag in _DROPPED or self.dropping:
            return
        self.cur.children.append(_Node(tag, dict(attrs), self.cur))

    def handle_endtag(self, tag):
        if tag in _DROPPED:
            self.dropping = max(0, self.dropping - 1)
            return
        if self.dropping:
            return
        node = self.cur
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.parent is not None:
            self.cur = node.parent

    def handle_data(self, data):
        if self.dropping:
            return
        text = " ".join(data.split())
        if text:
            self.cur.children.append(text)


def _walk(node: _Node):
    yield node
    for kid in node.kids():
        yield from _walk(kid)


def _texts(node: _Node):
    for child in node.children:
        if isinstance(child, str):
            yield child
        else:
            yield from _texts(child)


def _refuse(reason: str) -> None:
    raise SystemExit("REFUSED: " + reason)


def _raw_cards(raw: str) -> list[dict]:
    """Each metric card of the raw page, in document order: its p texts with
    their role, and its icon ids. Nothing here is printed."""
    tree = _Tree()
    tree.feed(raw)
    tree.close()
    mains = [n for n in _walk(tree.root) if n.tag == "main"]
    if len(mains) != 1:
        _refuse(f"{len(mains)} main elements, where one is required")
    sections = [n for n in _walk(mains[0]) if n.tag == "section"]
    if len(sections) != 1:
        _refuse(f"{len(sections)} section elements inside main, where one is required")
    cards = []
    for link in _walk(sections[0]):
        if link.tag != "a" or "/analytics/" not in (link.attrs.get("href") or ""):
            continue
        roles = []
        for p in [n for n in _walk(link) if n.tag == "p"]:
            text = " ".join(_texts(p))
            roles.append((_role_of(text), text))
        loose = sum(1 for n in _walk(link) if n.tag != "p" and any(isinstance(c, str) for c in n.children)
                    and not any(a.tag == "p" for a in _ancestors(n)))
        if loose:
            _refuse(f"a card holds {loose} text outside its p elements")
        icons = [n.attrs.get("id") or "" for n in _walk(link) if n.tag == "svg"]
        cards.append({"roles": roles, "icons": icons})
    if len(cards) != len(CARD_PATHS):
        _refuse(f"{len(cards)} analytics links in the section, where {len(CARD_PATHS)} are required")
    return cards


def _ancestors(node: _Node):
    node = node.parent
    while node is not None:
        yield node
        node = node.parent


def _role_of(text: str) -> str:
    if _VALUE.match(text):
        return "value"
    if _DELTA.match(text):
        return "delta"
    if text in RESTORED_LABELS or DATED_LABEL.match(text):
        return "label"
    if text == RESTORED_PERIOD or DATED_PERIOD.match(text):
        return "period"
    return "unknown"


_TAG_A = re.compile(r"<a\b[^>]*>")
_HREF = re.compile(r' href="([^"]*)"')
#: A text node as ``skeleton_of`` writes one: its own line between two tags
#: (the skeleton joins its pieces with newlines, and a text holds none).
_TEXT = re.compile(r">\n([^<\n]+)\n<")
_SVG_ID = re.compile(r'(<svg\b[^>]*? id=")([^"]*)(")')


def build(raw: str, key: bytes) -> tuple[str, dict[str, int]]:
    cards = _raw_cards(raw)
    skel = skeleton_of(raw, key)
    if skel.count("<main") != 1:
        _refuse("the skeleton does not draw exactly one main")
    main_start = skel.index("<main")
    main_end = skel.index("</main>", main_start)
    if skel.count("<section", main_start, main_end) != 1:
        _refuse("the skeleton does not draw exactly one section inside main")
    start = skel.index("<section", main_start, main_end)
    end = skel.index("</section>", start)
    section = skel[start:end]
    counts = {"cards": 0, "path_words": 0, "labels_restored": 0, "periods_restored": 0,
              "icons_restored": 0, "values_planted": 0, "deltas_planted": 0, "dated_planted": 0}

    out: list[str] = []
    cursor = 0
    card_index = 0
    for match in _TAG_A.finditer(section):
        href_m = _HREF.search(match.group(0))
        if href_m is None or "/analytics/" not in href_m.group(1):
            continue
        if card_index >= len(cards):
            _refuse("the skeleton draws more analytics links than the raw")
        close = section.index("</a>", match.end())
        out.append(section[cursor:match.start()])
        card_html, metric = _rebuild_card(section[match.start():close], cards[card_index], key, counts)
        out.append(card_html)
        cursor = close
        card_index += 1
        counts["cards"] += 1
    out.append(section[cursor:])
    if card_index != len(cards):
        _refuse("the skeleton and the raw disagree on the card count")
    rebuilt = skel[:start] + "".join(out) + skel[end:]
    copy = tracked_copy(rebuilt)
    doctype = "<!doctype html>\n"
    if not copy.startswith(doctype):
        _refuse("the tracked copy does not open with the skeleton's doctype")
    copy = doctype + HEADER + copy[len(doctype):] + "\n"
    counts["x_texts"] = copy.count(">\nx\n<")
    counts["bytes"] = len(copy)
    return copy, counts


def _rebuild_card(card: str, raw_card: dict, key: bytes, counts: dict[str, int]) -> tuple[str, str]:
    # 1. The address: its path words, by keyed hash, then the whole path checked.
    href_m = _HREF.search(card)
    href = href_m.group(1)
    for word in RESTORED_PATH_WORDS:
        shape = value_shape(word, key)
        if shape in href:
            href = href.replace(shape, word)
            counts["path_words"] += 1
    path = re.sub(r"^https://www\.linkedin\.com", "", html_escape.unescape(href))
    metric = CARD_PATHS.get(path)
    if metric is None:
        _refuse("a card links to an analytics address outside the four the reader names")
    card = card[:href_m.start(1)] + href + card[href_m.end(1):]

    # 2. The icon ids, by keyed hash.
    def icon(m: "re.Match[str]") -> str:
        for word in RESTORED_ICONS:
            if m.group(2) == value_shape(word, key):
                counts["icons_restored"] += 1
                return m.group(1) + word + m.group(3)
        _refuse("a card's icon id is not one of the icon names the reader reads")
        return ""

    card = _SVG_ID.sub(icon, card)
    if len(raw_card["icons"]) != sum(1 for _ in _SVG_ID.finditer(card)):
        _refuse("the raw card and its skeleton disagree on the icon count")

    # 3. The texts: each skeleton text chunk must be the keyed shape of the raw
    #    node at the same place, and is replaced by the planned text.
    chunks = list(_TEXT.finditer(card))
    roles = raw_card["roles"]
    if len(chunks) != len(roles) or sorted(r for r, _ in roles) != ["delta", "label", "period", "value"]:
        _refuse("a card does not hold exactly one value, label, delta and period")
    pieces, cursor = [], 0
    for chunk, (role, text) in zip(chunks, roles):
        if chunk.group(1) != html_escape.escape(value_shape(text, key), quote=False):
            _refuse("a card's text is not the keyed shape of the raw node at its place")
        planned = _planned(role, text, metric, counts)
        pieces.append(card[cursor:chunk.start(1)])
        pieces.append(html_escape.escape(planned, quote=False))
        cursor = chunk.end(1)
    pieces.append(card[cursor:])
    return "".join(pieces), metric


def _planned(role: str, text: str, metric: str, counts: dict[str, int]) -> str:
    if role == "value":
        counts["values_planted"] += 1
        return SYNTHETIC_VALUES[metric]
    if role == "delta":
        counts["deltas_planted"] += 1
        return SYNTHETIC_DELTAS[metric]
    if role == "label":
        if RESTORED_LABELS.get(text) == metric:
            counts["labels_restored"] += 1
            return text
        if DATED_LABEL.match(text) and metric == "search_appearances":
            counts["dated_planted"] += 1
            return SYNTHETIC_DATED_LABEL
        _refuse("a card's label names a different metric than its address")
    if role == "period":
        if text == RESTORED_PERIOD:
            counts["periods_restored"] += 1
            return text
        if DATED_PERIOD.match(text):
            counts["dated_planted"] += 1
            return SYNTHETIC_DATED_PERIOD
    _refuse("a card holds a text of no role")
    return ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capture", type=pathlib.Path, required=True, help="the raw /dashboard/ capture")
    ap.add_argument("--key", type=pathlib.Path, required=True, help="the SECRET hashing key file (hex)")
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true", help="re-derive and compare with --out")
    args = ap.parse_args(argv)
    key = bytes.fromhex(args.key.read_text(encoding="utf-8").strip())
    copy, counts = build(args.capture.read_text(encoding="utf-8"), key)
    print("counts: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    if args.check:
        same = args.out.exists() and args.out.read_text(encoding="ascii") == copy
        print(f"{args.out.name}: " + ("IDENTICAL to the re-derivation" if same else "DIFFERS from the re-derivation"))
        return 0 if same else 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(copy, encoding="ascii", newline="\n")
    print(f"wrote {args.out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
