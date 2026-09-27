"""Turn a captured PEOPLE-SEARCH results page into a skeleton fixture: its STRUCTURE, peopled with declared synthetic people.

Kept as the PROVENANCE of ``tests/fixtures/synthetic/people_search_results.html``:
the exact record of what was taken from the capture and what was put in its
place, which a privacy review needs and cannot get from the output alone.

WHAT IS KEPT. The first ``--results`` results of the page's result list, each
from the list's child down: every element's TAG and its NESTING, including the
one thing a hand-written fixture would never draw -- the whole result is ONE
LINK to the member, holding a SECOND link to the same member (the name) inside
it. An anchor inside an anchor is legal for a page built with DOM calls and
impossible for HTML's parser, so the fixture is written as well-formed XHTML
and the tests load it through an XML parser; ``tests/test_people_search_names.py``
says how, and shows the HTML parser losing the shape.

WHAT IS REPLACED, EVERY TIME. Every text node and every attribute value:

    the result's name (in its name link, and wherever else the same text
      sits in the result)                  -> a declared synthetic person
    a mutual connection's name              -> another declared synthetic person
    a member href                           -> that synthetic person's declared
                                               slug, in the SAME form (absolute
                                               or relative, and any depth below
                                               the slug) the capture wrote
    the headline (first link-free line
      beside the title)                     -> an invented headline
    the location (second such line)         -> an invented place
    any other href                          -> its closed route words only, the
                                               rest a placeholder segment
    an aria-label of a known template       -> the template, refilled with the
                                               synthetic person
    img src, class, id, style, data-*, and
      every other attribute                 -> DROPPED
    an svg's drawing                        -> dropped; an empty svg stays

WHAT IS KEPT VERBATIM, because it is interface text and never a person: the
degree ("<bullet> 2nd"), "Connect", a comma, an ampersand, and "<n> other
mutual connection(s)" with its number replaced. Any text node matching none of
the roles above is written as "Example text" and COUNTED, and the count is
printed: a skeleton with a nonzero count is one whose page drew something this
builder did not understand.

THE SYNTHETIC PEOPLE are taken from the declared tables --
``tests/test_fixtures_hold_only_synthetic_people.SYNTHETIC_PEOPLE`` and
``tests/test_no_committed_identity.SYNTHETIC_SLUGS``, the pairs invented
together for ``connections_list.html`` and the profile-views fixtures -- so no
declaration is added for this fixture.

The raw capture is gitignored and is NEVER committed: it holds real people.
Re-run this only against a fresh capture:

    python scripts/_build_people_search_skeleton.py --capture <path to the capture>

IT PRINTS COUNTS ONLY. It never prints a name, a headline, a place, a slug or
an id, and it writes no file but the fixture.
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "tests" / "fixtures" / "synthetic" / "people_search_results.html"

#: Declared synthetic people, in the order they are handed out: results
#: first, then the people the results name as mutual connections.
SYNTHETIC_PEOPLE = (
    ("Farhan Qureshi", "farhan-qureshi-2b8e77c4"),
    ("Anita Krishnan", "anita-krishnan-9d2f4a11"),
    ("Daniel Okonkwo", "daniel-okonkwo-77bd9f02"),
    ("Lakshmi Menon", "lakshmi-menon-51ac0e39"),
    ("Sunita Rao", "sunita-rao-3ef1a6d8"),
    ("Arun Balakrishnan", "arun-balakrishnan-4c19d833"),
    ("Rohan Desai", "rohan-desai-71f2e004"),
    ("Priya Sharma", "priya-sharma-8a41b207"),
)

#: Invented headlines, one per kept result, shaped like the capture's (a '|'
#: or the word 'at'). The employers are the fixtures' invented ones.
SYNTHETIC_HEADLINES = (
    "Principal Engineer at Umbrella Systems | Distributed Systems",
    "Engineering Manager at Umbrella Systems",
    "Staff Software Engineer | Payments | Example Labs",
)

#: An invented place, shaped like the capture's location lines (three words,
#: two commas).
SYNTHETIC_PLACE = "Fixtureton, Sampleshire, Exampleland"

#: The number written into "<n> other mutual connections".
SYNTHETIC_OTHERS = 3

PLACEHOLDER_TEXT = "Example text"
PLACEHOLDER_SEGMENT = "example"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
DROP_SUBTREE = {"script", "style", "template", "noscript", "path", "g", "defs"}

MEMBER = re.compile(r"^(https?://(?:www\.)?linkedin\.com)?/in/([A-Za-z0-9%_-]+)(/.*)?$")
DEGREE = re.compile(r"^[\u2022\u00b7]?\s*(1st|2nd|3rd\+?)$")
OTHERS = re.compile(r"^(\d+) other mutual connections?$")
INTERFACE_TEXT = {"Connect", ",", "&", "and", "Message", "Follow", "Pending"}

#: Route words kept verbatim in a non-member href; any other segment becomes
#: the placeholder.
ROUTE_WORDS = {"search", "results", "people", "preload", "in", "company",
               "school", "groups", "events", "overlay", "mynetwork", "feed",
               "messaging", "compose"}

#: aria-label templates refilled with the synthetic person; a label matching
#: none is dropped.
LABEL_TEMPLATES = (
    (re.compile(r"^Invite .+ to connect$"), "Invite {} to connect"),
    (re.compile(r"^View .+['\u2019]s profile$"), "View {}\u2019s profile"),
    (re.compile(r"^Follow .+$"), "Follow {}"),
    (re.compile(r"^Send a message to .+$"), "Send a message to {}"),
)
LABEL_VERBATIM = {"Verified"}

KEPT_ATTRIBUTES = {"role", "aria-hidden", "type"}
ATTRIBUTE_VALUE = re.compile(r"^[A-Za-z0-9 _-]{0,24}$")


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag, attrs, parent, text=None):
        self.tag, self.attrs, self.parent, self.text = tag, attrs, parent, text
        self.children = []


class Tree(HTMLParser):
    """The capture as it was SERIALISED -- nested anchors stay nested, which
    is what ``page.content()`` of the live page wrote."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        walker = self.cur
        while walker is not None and walker.tag != tag:
            walker = walker.parent
        if walker is not None and walker.parent is not None:
            self.cur = walker.parent

    def handle_data(self, data):
        if data.strip():
            self.cur.children.append(Node("#text", [], self.cur, data))


def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)


def attr(node, name):
    for key, value in node.attrs:
        if key == name:
            return value
    return None


def member_key(node):
    """The member segment of a member link, or None. In memory only."""
    if node.tag != "a":
        return None
    found = MEMBER.match((attr(node, "href") or "").strip())
    if not found or found.group(2) == "me":
        return None
    return found.group(2)


def text_of(node):
    return " ".join(" ".join(n.text for n in walk(node) if n.tag == "#text").split())


def result_cards(root):
    """An outer member link holding a link to the same member: the reader's rule."""
    cards = []
    for node in walk(root):
        key = member_key(node)
        if key and any(member_key(d) == key for d in walk(node) if d is not node):
            cards.append(node)
    return cards


def list_of(cards):
    """The nearest common ancestor of every card, and each card's child of it."""
    chains = []
    for card in cards:
        chain, walker = [], card
        while walker is not None:
            chain.append(walker)
            walker = walker.parent
        chains.append(chain)
    common = next(c for c in chains[0] if all(c in chain for chain in chains))
    items = []
    for chain in chains:
        items.append(chain[chain.index(common) - 1])
    return common, items


class Skeleton:
    def __init__(self, results):
        self.results = results
        self.people = {}          # real member key -> (name, slug); memory only
        self.pool = list(SYNTHETIC_PEOPLE)
        self.unclassified = 0
        self.dropped_labels = 0

    def person(self, key):
        if key not in self.people:
            if not self.pool:
                sys.exit("refused: more distinct people than declared synthetic ones")
            self.people[key] = self.pool.pop(0)
        return self.people[key]

    def href(self, value):
        value = (value or "").strip()
        found = MEMBER.match(value)
        if found:
            prefix, key, tail = found.group(1) or "", found.group(2), found.group(3) or ""
            below = [s for s in tail.split("/") if s]
            rest = "".join(
                "/" + (s if s in ROUTE_WORDS else PLACEHOLDER_SEGMENT) for s in below
            )
            slash = "/" if tail.endswith("/") or not below else ""
            return f"{prefix}/in/{self.person(key)[1]}{rest}{slash}"
        prefix = re.match(r"^https?://[^/]+", value)
        path = re.sub(r"[?#].*$", "", value[prefix.end():] if prefix else value)
        segments = [s if s in ROUTE_WORDS else PLACEHOLDER_SEGMENT
                    for s in path.split("/") if s]
        return (prefix.group(0) if prefix else "") + "/" + "/".join(segments) + (
            "/" if segments else "")

    def label(self, value, key):
        value = (value or "").strip()
        if value in LABEL_VERBATIM:
            return value
        for pattern, template in LABEL_TEMPLATES:
            if pattern.match(value) and key is not None:
                return template.format(self.person(key)[0])
        self.dropped_labels += 1
        return None

    def attributes(self, node, key):
        out = []
        for name, value in node.attrs:
            if node.tag == "a" and name == "href":
                out.append(("href", self.href(value)))
            elif name == "aria-label":
                kept = self.label(value, key)
                if kept is not None:
                    out.append(("aria-label", kept))
            elif name in KEPT_ATTRIBUTES and ATTRIBUTE_VALUE.match(value or ""):
                out.append((name, value or ""))
            elif node.tag == "img" and name == "alt":
                out.append(("alt", ""))
        return out

    def text(self, node, roles):
        raw = " ".join(node.text.split())
        if node in roles:
            return roles[node]
        if DEGREE.match(raw) or raw in INTERFACE_TEXT:
            return raw
        found = OTHERS.match(raw)
        if found:
            plural = "s" if SYNTHETIC_OTHERS != 1 else ""
            return f"{SYNTHETIC_OTHERS} other mutual connection{plural}"
        self.unclassified += 1
        return PLACEHOLDER_TEXT

    def roles_for(self, item, index):
        """Which text node is which, for one result: decided in memory from
        the structure, never printed."""
        roles = {}
        card = next(c for c in result_cards(item))
        own = member_key(card)
        name, _slug = self.person(own)
        real_name = None
        for node in walk(card):
            if node is not card and member_key(node) == own:
                real_name = text_of(node)
                for text in (n for n in walk(node) if n.tag == "#text"):
                    roles[text] = name
                title_p = next(p for p in parents(node) if p.tag == "p")
                column = title_p.parent
                lines = [p for p in walk(column) if p.tag == "p" and p is not title_p
                         and not any(n.tag == "a" for n in walk(p))]
                if len(lines) == 2:
                    for text in (n for n in walk(lines[0]) if n.tag == "#text"):
                        roles[text] = SYNTHETIC_HEADLINES[index % len(SYNTHETIC_HEADLINES)]
                    for text in (n for n in walk(lines[1]) if n.tag == "#text"):
                        roles[text] = SYNTHETIC_PLACE
                break
        for node in walk(item):
            key = member_key(node)
            if key and key != own:
                other = self.person(key)[0]
                for text in (n for n in walk(node) if n.tag == "#text"):
                    roles[text] = other
            elif node.tag == "#text" and real_name and " ".join(node.text.split()) == real_name:
                roles[node] = name
        return roles, own

    def emit(self, node, roles, key, out):
        if node.tag == "#text":
            out.append(escape(self.text(node, roles)))
            return
        if node.tag in DROP_SUBTREE:
            return
        attrs = self.attributes(node, key)
        rendered = "".join(f" {name}={quoteattr(value)}" for name, value in attrs)
        if node.tag == "svg":
            out.append(f"<svg{rendered}></svg>")
            return
        if node.tag in VOID:
            out.append(f"<{node.tag}{rendered} />")
            return
        out.append(f"<{node.tag}{rendered}>")
        for child in node.children:
            self.emit(child, roles, key, out)
        out.append(f"</{node.tag}>")


def parents(node):
    walker = node.parent
    while walker is not None:
        yield walker
        walker = walker.parent


HEADER = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head><meta charset="utf-8" /><title>People search results (synthetic skeleton)</title></head>
<body>
<!-- EVERY PERSON HERE IS SYNTHETIC: names and slugs from the declared tables,
     headlines and the place invented. The STRUCTURE is a live people-search
     results page's, kept by scripts/_build_people_search_skeleton.py, which
     says what was kept and what replaced. WELL-FORMED XHTML ON PURPOSE: each
     result is a link holding a link, which only an XML parser keeps; the
     tests load it that way. Text is not indented, as the page drew none. -->
<main>
"""
FOOTER = """</main>
</body>
</html>
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--capture", required=True)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--results", type=int, default=3)
    args = parser.parse_args(argv)

    tree = Tree()
    tree.feed(Path(args.capture).read_bytes().decode("utf-8", errors="replace"))
    cards = result_cards(tree.root)
    if not cards:
        sys.exit("refused: the capture holds no result card (a member link holding one)")
    container, items = list_of(cards)
    kept = items[: args.results]
    skeleton = Skeleton(args.results)
    body = []
    for index, item in enumerate(kept):
        roles, own = skeleton.roles_for(item, index)
        body.append("")
        skeleton.emit(item, roles, own, body)
        body.append("\n")
    text = HEADER + '<div role="list">' + "".join(body) + "</div>\n" + FOOTER
    unexpected = {ch for ch in text if ord(ch) > 127} - {"\u2022", "\u2019"}
    if unexpected:
        sys.exit("refused: %d character(s) outside ASCII other than the bullet and "
                 "the apostrophe" % len(unexpected))
    # THE FILE IS ASCII: the bullet and the apostrophe travel as character
    # references, which the HTML parser and the XML parser both decode.
    text = text.encode("ascii", "xmlcharrefreplace").decode("ascii")
    Path(args.out).write_text(text, encoding="ascii", newline="\n")
    print("result cards in the capture", len(cards), "| list children", len(items),
          "| kept", len(kept), "| synthetic people used", len(skeleton.people),
          "| unclassified text nodes", skeleton.unclassified,
          "| aria-labels dropped", skeleton.dropped_labels,
          "| bytes", len(text.encode("utf-8")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
