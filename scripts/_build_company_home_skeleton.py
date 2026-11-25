"""Build the TRACKED skeletons of an organisation Page root that the Home-view prose reader (``linkedin_server/company_home.py``, census row J 110) is aimed at.

Kept as the PROVENANCE of two committed fixtures, 2026-10-10 (lane B4):

    tests/fixtures/live1/company_root_home_view.html    --kind home
        from a RAW capture of a Page root taken 2026-09-23 by the live lane
        (session 1), on which the root drew its HOME view: the tab nav's
        current anchor is the Home tab, and the main column draws the
        Overview card and the Page posts section.
    tests/fixtures/live9/company_root_posts_view.html   --kind posts
        from the live lane's session-9 KEYED skeleton of a Page root,
        2026-10-10, on which the SAME admitted root address drew the POSTS
        view: the current anchor is the Posts tab, there is no Overview card,
        and the main column is a feed of posts.

Both inputs are gitignored and stay on the box. The script reads one, and
writes a document that keeps the STRUCTURE and nothing anybody wrote:

WHAT IS KEPT
    * every element inside ``<body>``, with its tag and nesting (an ``<svg>``
      stays, EMPTY: its drawing is dropped);
    * the closed attribute vocabularies, each value checked against its
      vocabulary (role, aria-hidden, aria-current, aria-expanded,
      aria-disabled, type, tabindex, dir, hidden, disabled);
    * ``data-testid`` ONLY when its value is one of :data:`KEPT_TESTIDS`,
      the hooks the reader is built on, each MEASURED on the captures;
    * ``componentkey``'s PRESENCE, with one constant value -- the reader finds
      a card as the nearest ancestor carrying the attribute, never by value;
    * a text node EQUAL to one of :data:`KEPT_WORDS`, LinkedIn's own words,
      each MEASURED drawn on at least one of the captures (on a keyed
      skeleton, a word counts as drawn when its keyed shape equals the node).

WHAT IS REPLACED, EVERY TIME
    * the text of the ONE text box inside the Overview card -> the declared
      synthetic sentences :data:`SYNTHETIC_PROSE`, one per text run, so the
      reader under test has organisation prose to read that nobody wrote;
    * every other text node -> ``x`` (the reduced-to-shape alphabet both of
      the repository's people guards admit; it says only that text was there);
    * ``id`` and every attribute naming one -> ``example-id-<n>``, in order of
      first appearance;
    * an address on www.linkedin.com -> its path with LinkedIn's own path
      words kept (:data:`PATH_WORDS`) and every other segment ``x``, each query
      value ``x``; a relative address the same; any other host ->
      ``https://example.invalid/``;
    * every other attribute -> DROPPED (class, style, src, srcset, alt,
      aria-label, title, value, data-* and the rest).

It reads no name, slug or id into its output by construction: every value it
writes is a kept word, a closed-vocabulary value, ``x``, or a constant here.
It PRINTS COUNTS ONLY. Run in ``--raw`` mode over its own output it reproduces
that output byte for byte (a FIXED POINT), which
``tests/test_company_home.py`` asserts for both fixtures, and it prints a
STRUCTURE DIGEST (tags and nesting only) that the same test pins.

    python scripts/_build_company_home_skeleton.py --kind home  --raw <capture> [--out <path>]
    python scripts/_build_company_home_skeleton.py --kind posts --skeleton <keyed skeleton> --key <key file> [--out <path>]
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = {
    "home": REPO / "tests" / "fixtures" / "live1" / "company_root_home_view.html",
    "posts": REPO / "tests" / "fixtures" / "live9" / "company_root_posts_view.html",
}

#: LinkedIn's own words a fixture keeps, each MEASURED drawn on at least one of
#: the two captures (scratch measurements of 2026-10-10, recorded in lane B4's
#: report): the Page's tab labels; the Home view's Overview heading, its
#: "Show all" link and the "Page posts" heading; the accessible heading
#: LinkedIn draws over each feed item, "Feed post"; the Page's top-card
#: controls; and a feed item's action bar.
KEPT_WORDS = frozenset({
    "Home", "About", "Posts", "Jobs", "People", "Insights", "Life", "Products",
    "Overview", "Show all", "Page posts", "Feed post",
    "Follow", "Following", "Message",
    "Like", "Comment", "Repost", "Send", "more", "Sort by:", "Top",
})

#: The ``data-testid`` values kept, each MEASURED: ``expandable-text-box`` holds
#: the Overview card's description on the three September Home-view captures
#: and each post's words on the session-9 Posts view (13); its expander,
#: ``expandable-text-button`` (12 on session 9); ``lazy-column``, the Home
#: view's column (1 on each September capture).
KEPT_TESTIDS = frozenset({"expandable-text-box", "expandable-text-button", "lazy-column"})

#: The heading that names the Overview card, and how far up the card is.
OVERVIEW_HEADING = "Overview"
CARD_HOPS = 4

#: What the Overview card's text box holds in a fixture: invented sentences,
#: one per text run of the capture's box, in order, cycling.
SYNTHETIC_PROSE = (
    "Example overview sentence one, written for this fixture and naming nobody.",
    "Example overview sentence two.",
)

PLACEHOLDER_TEXT = "x"
COMPONENT_VALUE = "example-component"
OTHER_HOST = "https://example.invalid/"

#: LinkedIn's own path words, which a rebuilt address keeps.
PATH_WORDS = frozenset({
    "company", "school", "in", "feed", "update", "search", "results", "people",
    "companies", "content", "all", "jobs", "view", "posts", "about", "home",
    "insights", "life", "products", "services", "events", "videos", "groups",
    "mynetwork", "messaging", "notifications", "learning", "premium", "help",
    "legal", "accessibility", "talent", "ad", "sales", "mobile", "my-items",
})

VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                  "link", "meta", "param", "source", "track", "wbr"})
DROPPED = frozenset({"script", "style", "noscript", "template", "code", "head", "title"})

ARIA_STATES = frozenset({"true", "false", "mixed", "page", "step", "location", "date", "time"})
ROLES = frozenset({
    "alert", "article", "banner", "button", "checkbox", "complementary", "contentinfo",
    "dialog", "feed", "figure", "group", "heading", "img", "link", "list", "listbox",
    "listitem", "main", "menu", "menubar", "menuitem", "menuitemcheckbox",
    "menuitemradio", "navigation", "none", "option", "presentation", "progressbar",
    "radio", "region", "search", "separator", "status", "switch", "tab", "tablist",
    "tabpanel", "textbox", "toolbar", "tooltip",
})
TYPES = frozenset({"button", "submit", "reset", "checkbox", "radio", "text", "search"})
DIRS = frozenset({"ltr", "rtl", "auto"})
CLOSED = {
    "role": ROLES,
    "aria-hidden": ARIA_STATES,
    "aria-current": ARIA_STATES,
    "aria-expanded": ARIA_STATES,
    "aria-disabled": ARIA_STATES,
    "type": TYPES,
    "dir": DIRS,
}
TABINDEX = re.compile(r"^-?[0-9]{1,2}$")
BOOLEAN_ATTRIBUTES = ("hidden", "disabled")
ID_REFS = ("for", "aria-labelledby", "aria-describedby", "aria-controls", "aria-owns")
KEEP_ORDER = ("role", "type", "tabindex", "dir", "aria-current", "aria-expanded",
              "aria-disabled", "aria-hidden", "hidden", "disabled", "id", "for",
              "aria-labelledby", "aria-describedby", "aria-controls", "aria-owns",
              "data-testid", "componentkey", "href")

HEADER = {
    "home": (
        "LANE B4, 2026-10-10 (census row J 110): built by\n"
        "  scripts/_build_company_home_skeleton.py --kind home from a RAW capture of an\n"
        "  organisation Page root taken 2026-09-23, on which the root drew its HOME view.\n"
        "  Structure only: every text is x, a kept LinkedIn word, or the declared synthetic\n"
        "  prose in the Overview card's text box. Nobody's words are here."
    ),
    "posts": (
        "LANE B4, 2026-10-10 (census row J 110): built by\n"
        "  scripts/_build_company_home_skeleton.py --kind posts from the live lane's\n"
        "  session-9 KEYED skeleton of an organisation Page root (2026-10-10), on which\n"
        "  the same admitted root address drew the POSTS view. Structure only: every text\n"
        "  is x or a kept LinkedIn word. Nobody's words are here."
    ),
}


def value_shape(text: str, key: bytes) -> str:
    """The live lane's keyed shape (``_probe_live_lane_session_2.value_shape``),
    used ONLY to ask whether a skeleton's node equals a kept word."""
    letters = sum(1 for ch in text if ch.isalpha())
    digits = sum(1 for ch in text if ch.isdigit())
    mark = hmac.new(key, text.encode("utf-8"), hashlib.sha256).hexdigest()[:8]
    return "{L" + str(letters) + "D" + str(digits) + "n" + str(len(text)) + ":" + mark + "}"


class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = attrs
        self.children = []
        self.parent = parent


class Tree(HTMLParser):
    """The document as nested nodes; text whitespace-normalised; comments,
    scripts, styles, templates and the head dropped while parsing."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root
        self.dropping = 0

    def handle_starttag(self, tag, attrs):
        if tag in DROPPED:
            if tag not in VOID:
                self.dropping += 1
            return
        if self.dropping:
            return
        node = Node(tag, list(attrs), self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and tag not in DROPPED and not self.dropping:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in DROPPED:
            if tag not in VOID:
                self.dropping = max(0, self.dropping - 1)
            return
        if self.dropping or tag in VOID:
            return
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        # ADJACENT TEXT IS ONE TEXT, as a browser draws it. A capture splits a
        # run with comments (React writes ``<!-- -->`` between interpolations)
        # and those are dropped here, so the run is joined BEFORE it is judged
        # -- otherwise two reduced halves would write ``xx``, which reads back
        # as one node, and the output would not be its own fixed point.
        if self.dropping:
            return
        if self.cur.children and isinstance(self.cur.children[-1], str):
            self.cur.children[-1] += data
        else:
            self.cur.children.append(data)


def texts_of(node):
    """``node``'s own text runs, whitespace-normalised, empties dropped."""
    out = []
    for child in node.children:
        if isinstance(child, str):
            text = " ".join(child.split())
            if text:
                out.append(text)
    return out


def walk(node):
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from walk(child)


class Builder:
    def __init__(self, tree: Tree, key: bytes | None):
        self.tree = tree
        self.key = key
        self.ids: dict[str, str] = {}
        self.counts = {
            "elements": 0, "texts kept": 0, "texts reduced": 0, "prose runs": 0,
            "testids kept": 0, "addresses rebuilt": 0, "overview headings": 0,
            "overview text boxes": 0,
        }
        self.kept_words = {word: word for word in KEPT_WORDS}
        self.kept_testids = {value: value for value in KEPT_TESTIDS}
        if key is not None:
            for word in KEPT_WORDS:
                self.kept_words[value_shape(word, key)] = word
            for value in KEPT_TESTIDS:
                self.kept_testids[value_shape(value, key)] = value
        self.prose_boxes = self._overview_boxes()

    def _word(self, text):
        return self.kept_words.get(text)

    def _overview_boxes(self):
        """The text box of each Overview card, found the way the reader finds it."""
        boxes = set()
        for node in walk(self.tree.root):
            if node.tag != "h2":
                continue
            own = texts_of(node)
            if not (len(own) == 1 and self._word(own[0]) == OVERVIEW_HEADING):
                continue
            self.counts["overview headings"] += 1
            card, hops = node.parent, 1
            while card is not None and card.tag != "#root" and hops <= CARD_HOPS:
                if any(name == "componentkey" for name, _ in card.attrs):
                    break
                card, hops = card.parent, hops + 1
            else:
                continue
            if card is None or card.tag == "#root":
                continue
            for inner in walk(card):
                testid = dict(inner.attrs).get("data-testid")
                if testid is not None and self.kept_testids.get(testid) == "expandable-text-box":
                    boxes.add(id(inner))
                    self.counts["overview text boxes"] += 1
        return boxes

    def id_for(self, value):
        if value not in self.ids:
            self.ids[value] = "example-id-%d" % (len(self.ids) + 1)
        return self.ids[value]

    def address_for(self, href):
        text = (href or "").strip()
        if not text or text.startswith("#") or text.lower().startswith("javascript:"):
            return "#"
        try:
            parts = urlsplit(text)
        except ValueError:
            return OTHER_HOST
        if parts.scheme not in ("", "https", "http"):
            return OTHER_HOST
        if parts.netloc and parts.netloc != "www.linkedin.com":
            return OTHER_HOST
        if not parts.netloc and parts.scheme:
            return OTHER_HOST
        self.counts["addresses rebuilt"] += 1
        segments = parts.path.split("/")
        path = "/".join(s if (s == "" or s in PATH_WORDS) else PLACEHOLDER_TEXT for s in segments)
        query = ""
        if parts.query:
            names = []
            for pair in parts.query.split("&"):
                name, eq, _value = pair.partition("=")
                shown = name if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,40}", name) else PLACEHOLDER_TEXT
                names.append(shown + ("=" + PLACEHOLDER_TEXT if eq else ""))
            query = "?" + "&".join(names)
        prefix = "https://www.linkedin.com" if parts.netloc else ""
        return prefix + path + query

    def attributes_for(self, node):
        source = {}
        for name, value in node.attrs:
            source.setdefault(name, value)
        out = []
        for name in KEEP_ORDER:
            if name not in source:
                continue
            value = source[name]
            if name in CLOSED:
                if value is not None and value in CLOSED[name]:
                    out.append((name, value))
            elif name == "tabindex":
                if value is not None and TABINDEX.match(value):
                    out.append((name, value))
            elif name in BOOLEAN_ATTRIBUTES:
                out.append((name, None))
            elif name == "id":
                if value:
                    out.append((name, self.id_for(value)))
            elif name in ID_REFS:
                if value:
                    out.append((name, " ".join(self.id_for(t) for t in value.split())))
            elif name == "data-testid":
                kept = self.kept_testids.get(value or "")
                if kept is not None:
                    self.counts["testids kept"] += 1
                    out.append((name, kept))
            elif name == "componentkey":
                out.append((name, COMPONENT_VALUE))
            elif name == "href":
                out.append((name, self.address_for(value)))
        return out

    def render(self, kind):
        body = next((n for n in walk(self.tree.root) if n.tag == "body"), None)
        if body is None:
            raise SystemExit("the input has no <body>")
        out = ["<!doctype html>\n<!--\n  " + HEADER[kind] + "\n-->\n<html>\n<head><meta charset=\"utf-8\"><title>x</title></head>\n"]
        self._write(body, out, in_box=False, run=[0])
        out.append("\n</html>\n")
        return "".join(out)

    def _write(self, node, out, *, in_box, run):
        self.counts["elements"] += 1
        parts = [node.tag]
        for name, value in self.attributes_for(node):
            parts.append(name if value is None else '%s="%s"' % (name, escape(value, quote=True)))
        out.append("<" + " ".join(parts) + ">")
        if node.tag in VOID:
            return
        if node.tag == "svg":
            out.append("</svg>")
            return
        box = in_box or id(node) in self.prose_boxes
        if id(node) in self.prose_boxes:
            run = [0]
        for child in node.children:
            if isinstance(child, Node):
                self._write(child, out, in_box=box, run=run)
                continue
            child = " ".join(child.split())
            if not child:
                continue
            if box:
                out.append(escape(SYNTHETIC_PROSE[run[0] % len(SYNTHETIC_PROSE)]))
                run[0] += 1
                self.counts["prose runs"] += 1
                continue
            word = self._word(child)
            if word is not None:
                self.counts["texts kept"] += 1
                out.append(escape(word))
            else:
                self.counts["texts reduced"] += 1
                out.append(PLACEHOLDER_TEXT)
        out.append("</" + node.tag + ">")


def escape(text, quote=False):
    out = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if quote:
        out = out.replace('"', "&quot;")
    return out.encode("ascii", "xmlcharrefreplace").decode("ascii")


def structure_digest(text):
    """Tags and nesting of the body only, as a sha256 prefix."""
    tree = Tree()
    tree.feed(text)
    tree.close()
    body = next(n for n in walk(tree.root) if n.tag == "body")
    lines = []

    def rec(node, depth):
        lines.append("%d %s" % (depth, node.tag))
        for child in node.children:
            if isinstance(child, Node):
                rec(child, depth + 1)

    rec(body, 0)
    return hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()[:16]


def build(source_text, *, kind, key=None):
    """The fixture text for ``kind`` from an input document (raw page, keyed
    skeleton, or a fixture this script wrote). PURE."""
    tree = Tree()
    tree.feed(source_text)
    tree.close()
    builder = Builder(tree, key)
    text = builder.render(kind)
    assert all(ord(ch) < 128 for ch in text)
    return text, builder.counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--kind", required=True, choices=sorted(HEADER))
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--raw", type=Path)
    source.add_argument("--skeleton", type=Path)
    parser.add_argument("--key", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    key = None
    if args.skeleton is not None:
        if args.key is None:
            parser.error("--skeleton needs --key, the key it was shaped with")
        key = bytes.fromhex(args.key.read_text(encoding="utf-8").strip())
        source_text = args.skeleton.read_text(encoding="utf-8")
    else:
        source_text = args.raw.read_text(encoding="utf-8", errors="replace")
    text, counts = build(source_text, kind=args.kind, key=key)
    out = args.out or DEFAULT_OUT[args.kind]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="ascii", newline="\n")
    for name in sorted(counts):
        print("%-20s %d" % (name, counts[name]))
    print("bytes written        %d" % len(text))
    print("structure digest     %s" % structure_digest(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
