"""Turn the live lane's skeleton of ONE third party's profile into a committed fixture: its STRUCTURE, peopled only with declared synthetic values.

Kept as the PROVENANCE of ``tests/fixtures/synthetic/named_profile_live.html``,
the fixture the named-person reader (``dom.read_named_profile``) is built over
since 2026-09-28: the exact record of what was taken from the capture and what
was put in its place, which a privacy review needs and cannot get from the
output alone.

THE INPUT IS ALREADY A SKELETON. The live lane (session 2, 2026-09-28) loaded
one first-degree profile the operator named, through the named-person door,
pressed nothing, and wrote it with ``_probe_live_lane_session_2.skeleton_of``:
tags, classes, roles and closed ARIA states kept; LinkedIn's own words kept;
EVERY OTHER TEXT NODE AND ATTRIBUTE VALUE REPLACED BY ITS SHAPE,
``{L<letters>D<digits>n<length>:<8-hex keyed hash>}``. So no name, slug or id
reaches this script -- only shapes, and equal shapes for equal strings. What
it does is put SYNTHETIC values where the shapes stood, each by the ROLE the
structure gives it.

WHAT IS KEPT. Every element inside ``<body>``, with its tag and its nesting
(an ``<svg>`` stays, EMPTY: its drawing is dropped); the closed attribute
vocabularies the live lane kept verbatim (role, type, tabindex, dir, target,
hidden, disabled, checked and the aria states); LinkedIn's own words, verbatim.

WHAT IS REPLACED, EVERY TIME:

    the page title (one shape)          -> "<owner> | LinkedIn"
    the owner's name -- the shape of the
      topcard's first heading, wherever
      that shape stands                 -> the declared synthetic OWNER
    the TOPCARD CONTAINER's id -- the
      nearest ancestor of that heading
      carrying an id                    -> com.linkedin.sdui.profile.card.ref
                                           <OWNER_MEMBER_ID>Topcard   (DERIVED,
                                           below)
    every other id, and every attribute
      naming one (for, aria-labelledby,
      aria-describedby, aria-controls)  -> example-id-<n>, one per shape
    a member address /in/<shape>/...     -> the owner's synthetic slug for the
                                           topcard's own shape, another declared
                                           synthetic slug for each other shape;
                                           the path's own words kept, any other
                                           shaped segment "example", the query
                                           dropped
    /messaging/compose/?...              -> the same path, its query naming a
                                           declared synthetic member id: the
                                           owner's in the topcard
    any other address                    -> its kept path words, shaped segments
                                           "example", the query dropped
    the topcard's degree lines (L2D1n5) -> "&#183; 1st"   (DERIVED: the live lane
                                           says the profile is first-degree,
                                           and the shape is that line's)
    the topcard's first shaped line of
      ten or more letters under the name-> the synthetic HEADLINE
    the next such line, not in a link   -> the synthetic PLACE
    the topcard's contact link
      (/overlay/<12-character shape>/)  -> /overlay/contact-info/ and
                                           "Contact info"   (DERIVED from the
                                           shape and the path word)
    an aria-label on a control whose own
      text is Message, Connect or Follow-> "Message <p>", "Invite <p> to
                                           connect", "Follow <p>", <p> a name
                                           REDUCED TO SHAPE (below)
    any other shaped aria-label          -> DROPPED on a member link (a label
                                           there is a person slot), else
                                           "Example label"; both COUNTED
    any other shaped text with a letter  -> its shape spelled out REDUCED TO
                                           SHAPE: X and x for letters, 9 for
                                           digits, spaces for the rest -- the
                                           length of what stood there and none
                                           of it (the convention
                                           tests/test_fixtures_hold_only_synthetic_people.py
                                           accepts as nobody)
    a shaped text with no letter        -> that many &#183;
    a text or label that is NOT a shape,
      not one of LinkedIn's words kept
      (KEPT_WORDS, KEPT_LABELS) and not a
      value this script writes          -> "Example text" / "Example label",
                                           COUNTED: a hand edit does not survive
    class, style, componentkey, data-*,
      src, srcset, alt, value and every
      other attribute                    -> DROPPED

WHAT IS DERIVED, stated so a reader can weigh it:

* THE TOPCARD CONTAINER'S ID. The skeleton shapes ids, so it cannot say the id
  ENDS ``Topcard``. Its shape is 80 characters, 71 letters and 4 digits: the
  measured convention's 34-character prefix ``com.linkedin.sdui.profile.card.ref``
  (29 letters) and a 39-character member id, plus a 7-letter suffix -- and the
  six sibling card containers fit the same pattern with their own suffix
  lengths (5, 8, 8, 15, 16, 25). This script prints the shape it found; if the
  inference were wrong, the reader finds no topcard on the live page and
  REFUSES.
* WHICH OF THE TOPCARD'S TWO ACTION ROWS IS HIDDEN. The topcard draws Message
  and More TWICE, in two rows, and the live page showed ONE of each (the live
  lane, page-wide: Message 5 visible of 6, More 1 of 2). The capture keeps no
  stylesheet, so which row LinkedIn hides is not in it: the SECOND row is
  hidden here, with ``style="display:none"``, and the tests drive the first
  hidden instead.

THE ONE THING THE BROWSER CHANGES: the topcard's mutual-connections link holds
a second link, as the live page's script builds it; HTML's parser, loading
this fixture, un-nests it. No reader here reads that link.

It PRINTS COUNTS ONLY -- never a shape's hash -- and writes no file but the
fixture. Run over its own output it reproduces it byte for byte (a FIXED POINT:
every value it writes is one it keeps), and it prints a STRUCTURE DIGEST --
tags and nesting only -- which ``tests/test_named_profile_live_skeleton.py``
pins.

    python scripts/_build_named_profile_skeleton.py --skeleton <path> [--out <path>]
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "tests" / "fixtures" / "synthetic" / "named_profile_live.html"

#: The OWNER: the declared synthetic person the secondary fixture,
#: ``tests/fixtures/synthetic/named_profile.html``, already draws, so the two
#: fixtures are one person on two drawings.
OWNER = "Casey Example"
OWNER_SLUG = "casey-example-3f9a"
OWNER_MEMBER_ID = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"
HEADLINE = "Invented headline for a synthetic person"
PLACE = "Example City, Example Region"
TOPCARD_ID = "com.linkedin.sdui.profile.card.ref" + OWNER_MEMBER_ID + "Topcard"

#: Other people's addresses and member ids: declared synthetic tokens only
#: (``tests/test_no_committed_identity.SYNTHETIC_SLUG_TOKENS`` and
#: ``SYNTHETIC_MEMBER_TOKENS``), handed out in order of first appearance.
OTHER_SEGMENT_TEMPLATE = "someone-example-{n}"
OTHER_MEMBER_IDS = (
    "ACoAASYNTHETICSYNTHETICSYNTHETIC0000003",
    "ACoAASYNTHETICSYNTHETICSYNTHETIC0000004",
    "ACoAASYNTHETICSYNTHETICSYNTHETIC0000001",
)
PLACEHOLDER_LABEL = "Example label"
PLACEHOLDER_SEGMENT = "example"
DEGREE_LINE = chr(0x00B7) + " 1st"
CONTACT_TEXT = "Contact info"
CONTACT_SEGMENT = "contact-info"

SHAPE = re.compile(r"\{L(\d+)D(\d+)n(\d+):[0-9a-f]{8}\}")
WHOLE_SHAPE = re.compile(r"^\{L(\d+)D(\d+)n(\d+):[0-9a-f]{8}\}$")
REDUCED = re.compile(r"^[Xx9 ]+$")
DOTS = re.compile("^" + chr(0x00B7) + "+$")
EXAMPLE_ID = re.compile(r"^example-id-\d+$")
OTHER_SLUG_SHAPE = re.compile(r"^someone-example-\d+$")

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
#: Attributes kept VERBATIM: the closed vocabularies the live lane kept.
KEPT = ("role", "type", "tabindex", "dir", "target", "hidden", "disabled", "checked",
        "aria-hidden", "aria-expanded", "aria-haspopup", "aria-pressed", "aria-checked",
        "aria-selected", "aria-current", "aria-disabled", "aria-level", "aria-modal")
#: Attributes that NAME an id.
ID_REFS = ("for", "aria-labelledby", "aria-describedby", "aria-controls")
#: LinkedIn's own path words, which an address keeps (the live lane's list).
PATH_WORDS = frozenset({
    "https:", "www.linkedin.com", "in", "me", "company", "school", "groups", "events",
    "feed", "update", "messaging", "thread", "compose", "mynetwork", "search",
    "results", "people", "companies", "content", "all", "jobs", "view", "mypreferences",
    "d", "settings", "recent-activity", "posts", "members", "attendees", "analytics",
    "overlay", "edit", "details", "network-manager", "people-follow", "followers",
    "following", "invite-connect", "connections", "notifications", "about", "life",
    "verifications", "verification", "trust", "contact-info",
})
CONTROL_TEMPLATES = {"Message": "Message {p}", "Connect": "Invite {p} to connect",
                     "Follow": "Follow {p}"}

#: LINKEDIN'S OWN WORDS THIS PAGE DRAWS, kept verbatim -- the ones the live
#: lane's skeleton kept, every one of them on its closed list
#: (``_probe_live_lane_session_2.FURNITURE``, which
#: ``tests/test_named_profile_live_skeleton.py`` holds this set to). A text
#: node that is neither a shape, one of these, nor a value this script writes
#: becomes "Example text" and is COUNTED -- which is what makes a hand edit of
#: the fixture break its fixed point.
KEPT_WORDS = frozenset({
    "About", "Activity", "Comment", "Connect", "Follow", "For Business", "Home",
    "Jobs", "Learning", "Like", "Me", "Message", "Messaging", "More", "My Network",
    "Notifications", "People you may know", "Posts", "Repost", "Send", "Show all",
    "You might like",
})
#: And the labels it keeps verbatim, on the same terms.
KEPT_LABELS = frozenset({"Dismiss", "For Business", "More", "Premium"})
#: ("Verified", which the live lane kept as a label eight times, is not on
#: master's copy of that list, so it is written as the placeholder here.)
PLACEHOLDER_TEXT = "Example text"
#: A label this script wrote from a template: a control's word and a person
#: reduced to shape.
TEMPLATED = re.compile(r"^(?:Message [Xx9 ]+|Invite [Xx9 ]+ to connect|Follow [Xx9 ]+)$")

HEADER = """<!doctype html>
<!--
  SKELETON OF A LIVE CAPTURE, PEOPLED WITH DECLARED SYNTHETIC VALUES. NOT A
  CAPTURE: nobody here is anybody.

  A third party's profile at /in/<segment>/, first-degree, as LinkedIn drew it
  on 2026-09-28 -- the live lane's session 2 loaded one profile the operator
  named, through the named-person door, pressed nothing, and wrote its
  skeleton; scripts/_build_named_profile_skeleton.py turned that skeleton into
  this file, and says line by line what it kept and what it put in place.

  THIS IS THE LIVE-TRUE FIXTURE for dom.read_named_profile (lane L5, the
  orchestrator's addendum of 2026-09-28 08:43). tests/fixtures/synthetic/
  named_profile.html, the invented page the reader was first built over, is the
  SECONDARY case.

  MEASURED (the structure is the capture's): the topcard's container is the
  nearest ancestor of the owner's name heading (an h2) that carries an id; the
  topcard draws its two actions TWICE, in two rows -- Message as a link to the
  composer whose name is its own text, "Message", with no aria-label; More as a
  button, once by its text and once by an aria-label -- and the page's rails
  draw other people's Message, Connect and Follow controls, each labelled with
  that person's name; LinkedIn's class names are hashed, and dropped here.

  DERIVED, and the builder's docstring argues each: that the container's id
  ends "Topcard" (its shape fits com.linkedin.sdui.profile.card.ref<member
  id>Topcard, 80 characters); which of the two action rows is hidden (the
  second, here); the degree line's words; "Contact info". Everything else a
  member wrote is REDUCED TO SHAPE (X, x, 9), or is a declared synthetic value.
-->
"""


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = list(attrs)
        self.parent = parent
        self.children = []

    def get(self, name):
        for key, value in self.attrs:
            if key == name:
                return value
        return None


class Text:
    tag = "#text"

    def __init__(self, text, parent):
        self.text = text
        self.parent = parent
        self.children = []


class Tree(HTMLParser):
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
        text = " ".join(data.split())
        if text:
            self.cur.children.append(Text(text, self.cur))


def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)


def ancestors(node):
    walker = node.parent
    while walker is not None:
        yield walker
        walker = walker.parent


def own_text(node):
    return [c.text for c in node.children if isinstance(c, Text)]


def all_text(node):
    return [n.text for n in walk(node) if isinstance(n, Text)]


def reduced(letters, digits, length):
    """A shape spelled out: ``letters`` X/x in words, ``digits`` 9s, spaces."""
    others = max(0, length - letters - digits)
    words = max(1, others + 1) if letters else 0
    out = []
    if letters:
        base, extra = divmod(letters, words)
        for index in range(words):
            size = base + (1 if index < extra else 0)
            if size:
                out.append("X" + "x" * (size - 1))
    text = " ".join(out)
    if digits:
        text = (text + " " if text else "") + "9" * digits
    return text


class Builder:
    def __init__(self, tree):
        self.tree = tree
        self.counts = {"reduced text": 0, "dotted text": 0, "labels dropped": 0,
                       "placeholder labels": 0, "templated labels": 0,
                       "ids mapped": 0, "addresses rebuilt": 0, "addresses dropped": 0,
                       "unclassified text": 0, "unclassified labels": 0}
        self.ids = {}
        self.slugs = {}
        self.members = {}
        self.written = 0

    # -- finding the landmarks -------------------------------------------------

    def locate(self):
        body = next(n for n in walk(self.tree.root) if n.tag == "body")
        main = next(n for n in walk(body) if n.tag == "main")
        heading = next(n for n in walk(main) if n.tag in ("h1", "h2"))
        container = next(a for a in ancestors(heading) if a.get("id") is not None)
        self.body, self.main, self.heading, self.container = body, main, heading, container
        name = own_text(heading)
        assert len(name) == 1, "the topcard heading holds %d text nodes" % len(name)
        self.name_value = name[0]
        members = set()
        for node in walk(container):
            href = node.get("href") if isinstance(node, Node) else None
            segment = self._member_segment(href)
            if segment is not None:
                members.add(segment)
        assert len(members) == 1, "the topcard links %d members" % len(members)
        self.owner_segment = members.pop()
        titles = [n for n in walk(self.tree.root) if n.tag == "title"]
        values = {v for t in titles for v in own_text(t)}
        assert len(values) == 1, "%d distinct titles" % len(values)
        self.title_value = values.pop()
        found = WHOLE_SHAPE.match(container.get("id"))
        self.container_shape = (
            "L%sD%sn%s" % found.groups() if found else "literal, %d characters" % len(container.get("id"))
        )

    @staticmethod
    def _member_segment(href):
        if not href:
            return None
        path = urlsplit(href).path
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2 and parts[0] == "in" and parts[1] != "me":
            return parts[1]
        return None

    # -- values ----------------------------------------------------------------

    def text_for(self, node, value):
        """What a text node writes."""
        if value == self.name_value:
            return OWNER
        if value == self.title_value:
            return OWNER + " | LinkedIn"
        found = WHOLE_SHAPE.match(value)
        if not found:
            # LinkedIn's own words, or a value this script writes -- and
            # anything else is somebody's edit, which does not survive.
            if (
                value in KEPT_WORDS
                or value in (HEADLINE, PLACE, CONTACT_TEXT, DEGREE_LINE, PLACEHOLDER_TEXT)
                or REDUCED.match(value)
                or DOTS.match(value)
            ):
                return value
            self.counts["unclassified text"] += 1
            return PLACEHOLDER_TEXT
        letters, digits, length = (int(g) for g in found.groups())
        in_topcard = self.container in ancestors(node)
        if in_topcard and (letters, digits, length) == (2, 1, 5):
            return DEGREE_LINE
        if in_topcard and node is self.headline_node:
            return HEADLINE
        if in_topcard and node is self.place_node:
            return PLACE
        if in_topcard and node is self.contact_node:
            return CONTACT_TEXT
        if letters == 0 and digits == 0:
            self.counts["dotted text"] += 1
            return chr(0x00B7) * max(1, length)
        self.counts["reduced text"] += 1
        return reduced(letters, digits, length)

    def classify_topcard_lines(self):
        """The headline, the place and the contact text, by their place under
        the name heading: the topcard's text nodes in document order. On a
        skeleton they are shapes; on this script's own output they are the
        values it wrote, and each is recognised as itself."""
        self.headline_node = self.place_node = self.contact_node = None
        seen_heading = False
        for node in walk(self.container):
            if node is self.heading:
                seen_heading = True
                continue
            if not seen_heading or not isinstance(node, Text):
                continue
            link = next((a for a in ancestors(node) if a.tag == "a"), None)
            if link is not None:
                if "/overlay/" in (link.get("href") or "") and self.contact_node is None:
                    self.contact_node = node
                continue
            if self.contact_node is not None:
                continue
            found = WHOLE_SHAPE.match(node.text)
            letters = int(found.group(1)) if found else None
            if self.headline_node is None:
                if node.text == HEADLINE or (letters is not None and letters >= 10):
                    self.headline_node = node
            elif self.place_node is None:
                if node.text == PLACE or (letters is not None and letters >= 3):
                    self.place_node = node

    def id_for(self, value):
        if value == self.container.get("id") or value == TOPCARD_ID:
            return TOPCARD_ID
        if EXAMPLE_ID.match(value):
            return value
        if value not in self.ids:
            self.ids[value] = "example-id-%d" % (len(self.ids) + 1)
            self.counts["ids mapped"] += 1
        return self.ids[value]

    def slug_for(self, segment):
        if segment in (self.owner_segment, OWNER_SLUG):
            return OWNER_SLUG
        if OTHER_SLUG_SHAPE.match(segment):
            return segment
        if segment not in self.slugs:
            self.slugs[segment] = OTHER_SEGMENT_TEMPLATE.format(n=len(self.slugs) + 1)
        return self.slugs[segment]

    def member_id_for(self, node):
        if self.container in ancestors(node):
            return OWNER_MEMBER_ID
        key = id(node)
        if key not in self.members:
            self.members[key] = OTHER_MEMBER_IDS[len(self.members) % len(OTHER_MEMBER_IDS)]
        return self.members[key]

    def address_for(self, node, href):
        """The address rebuilt, or ``None`` for one off LinkedIn's own host."""
        parts = urlsplit(href)
        if parts.netloc and parts.netloc != "www.linkedin.com":
            self.counts["addresses dropped"] += 1
            return None
        self.counts["addresses rebuilt"] += 1
        absolute = bool(parts.netloc)
        segments = parts.path.split("/")
        out = []
        member_at = None
        for index, segment in enumerate(segments):
            if segment == "":
                out.append("")
                continue
            if index >= 1 and segments[index - 1] == "in" and segment != "me":
                out.append(self.slug_for(segment))
                member_at = index
                continue
            if member_at is not None and index >= 1 and segments[index - 1] == "overlay":
                out.append(CONTACT_SEGMENT)
                continue
            out.append(segment if segment in PATH_WORDS else PLACEHOLDER_SEGMENT)
        path = "/".join(out)
        prefix = "https://www.linkedin.com" if absolute else ""
        if path.startswith("/messaging/compose"):
            return prefix + path + "?profileUrn=urn%3Ali%3Afsd_profile%3A" + self.member_id_for(node)
        return prefix + path

    def label_for(self, node, value):
        """What an aria-label writes, or ``None`` to drop it."""
        found = WHOLE_SHAPE.match(value)
        if not found:
            if value in KEPT_LABELS or value == PLACEHOLDER_LABEL or TEMPLATED.match(value):
                return value
            self.counts["unclassified labels"] += 1
            return PLACEHOLDER_LABEL
        letters, digits, length = (int(g) for g in found.groups())
        words = [t for t in all_text(node) if not WHOLE_SHAPE.match(t)]
        kind = next((w for w in words if w in CONTROL_TEMPLATES), None)
        if kind is not None and node.tag in ("a", "button"):
            template = CONTROL_TEMPLATES[kind]
            fixed = template.format(p="")
            person = reduced(
                max(1, letters - sum(ch.isalpha() for ch in fixed)),
                max(0, digits - sum(ch.isdigit() for ch in fixed)),
                max(1, length - len(fixed)),
            )
            self.counts["templated labels"] += 1
            return template.format(p=person)
        if node.tag == "a" and self._member_segment(node.get("href")) is not None:
            self.counts["labels dropped"] += 1
            return None
        self.counts["placeholder labels"] += 1
        return PLACEHOLDER_LABEL

    # -- the hidden row --------------------------------------------------------

    def action_rows(self):
        """The topcard's action rows: for each composer link in the topcard,
        its nearest ancestor that also holds a More button."""
        rows = []
        for node in walk(self.container):
            if not (isinstance(node, Node) and node.tag == "a"):
                continue
            if "/messaging/compose" not in (node.get("href") or ""):
                continue
            for up in ancestors(node):
                more = any(
                    isinstance(x, Node) and x.tag == "button"
                    and ((x.get("aria-label") or "") == "More" or "More" in all_text(x))
                    for x in walk(up)
                )
                if more:
                    if up not in rows:
                        rows.append(up)
                    break
                if up is self.container:
                    break
        return rows

    # -- writing ---------------------------------------------------------------

    def render(self):
        self.locate()
        self.classify_topcard_lines()
        rows = self.action_rows()
        assert len(rows) == 2, "the topcard draws %d action rows, not 2" % len(rows)
        self.hidden_row = rows[1]
        self.rows = len(rows)
        out = [HEADER, "<html lang=\"en\">\n<head><meta charset=\"utf-8\"><title>",
               escape(OWNER + " | LinkedIn"), "</title></head>\n"]
        self._write(self.body, out)
        out.append("\n</html>\n")
        return "".join(out)

    def _write(self, node, out):
        if isinstance(node, Text):
            out.append(escape(self.text_for(node, node.text)))
            return
        attrs = []
        for key, value in node.attrs:
            if value is None:
                if key in KEPT:
                    attrs.append((key, None))
                continue
            if key in KEPT:
                attrs.append((key, value))
            elif key == "id":
                attrs.append((key, self.id_for(value)))
            elif key in ID_REFS:
                attrs.append((key, " ".join(self.id_for(v) for v in value.split())))
            elif key == "href" and node.tag == "a":
                address = self.address_for(node, value)
                if address is not None:
                    attrs.append((key, address))
            elif key == "aria-label":
                label = self.label_for(node, value)
                if label is not None:
                    attrs.append((key, label))
        if node is self.hidden_row:
            attrs.append(("style", "display:none"))
        self.written += 1
        rendered = "".join(
            " %s" % key if value is None else ' %s="%s"' % (key, escape(value, quote=True))
            for key, value in attrs
        )
        out.append("<%s%s>" % (node.tag, rendered))
        if node.tag in VOID:
            return
        if node.tag != "svg":
            for child in node.children:
                self._write(child, out)
        out.append("</%s>" % node.tag)


def escape(text, quote=False):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if quote:
        text = text.replace('"', "&quot;")
    return "".join(ch if ord(ch) < 128 else "&#%d;" % ord(ch) for ch in text)


def structure_digest(node, depth=0, lines=None):
    """Tags and nesting only, below ``<body>``, an svg counted and not
    entered: sixteen letters."""
    top = lines is None
    lines = [] if top else lines
    if isinstance(node, Text):
        lines.append("%d:#text" % depth)
    else:
        lines.append("%d:%s" % (depth, node.tag))
        if node.tag != "svg" and node.tag not in VOID:
            for child in node.children:
                structure_digest(child, depth + 1, lines)
    if top:
        digest = hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()[:16]
        return digest.translate(str.maketrans("0123456789abcdef", "abcdefghijklmnop"))
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--skeleton", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    tree = Tree()
    tree.feed(args.skeleton.read_text(encoding="utf-8"))
    tree.close()
    builder = Builder(tree)
    text = builder.render()
    assert all(ord(ch) < 128 for ch in text)
    args.out.write_text(text, encoding="ascii", newline="\n")
    body = next(n for n in walk(tree.root) if n.tag == "body")
    print("elements written   %d" % builder.written)
    print("topcard container  id shape %s" % builder.container_shape)
    print("topcard members    1 (the owner's own address)")
    print("action rows        %d, the second hidden" % builder.rows)
    for key in sorted(builder.counts):
        print("%-18s %d" % (key, builder.counts[key]))
    print("other people       %d synthetic slugs" % len(builder.slugs))
    print("structure digest %s" % structure_digest(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
