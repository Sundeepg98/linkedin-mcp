"""Turn the live lane's tracked copy of a FIRST-CONTACT Message press's composer into a committed fixture: its STRUCTURE, peopled only with declared synthetic values.

Kept as the PROVENANCE of ``tests/fixtures/synthetic/first_contact_bubble.html``,
the new-message bubble ``linkedin_message_from_profile``'s first-contact path is
built over since 2026-09-28 (lane L5, the orchestrator's addendums of 13:03 and
14:20).

WHAT THE SOURCE IS. The live lane's session 3 (2026-09-28) ran
``linkedin_message_from_profile`` on a first-degree profile the operator named,
with NO conversation between them. The Message press opened, in about two
seconds and still on the profile, a NEW-MESSAGE bubble in LinkedIn's messaging
overlay -- INSIDE AN OPEN SHADOW ROOT, where ``page.content()`` and
``document.querySelectorAll`` do not reach and Playwright's piercing locators
do. The act refused, by design (its gate wanted a conversation headed by the
name), and nothing was typed. The lane saved the bubble's markup through the
piercing locator as a skeleton, and committed it as a TRACKED COPY:
``tests/fixtures/live3/m1_composer_bubble.html`` -- every text and attribute
value a person could be in reduced to one ``x``, ids to ``k`` and a hash,
LinkedIn's classes, roles, closed ARIA states and own words kept. THAT COPY IS
THIS SCRIPT'S INPUT (``--source``, its default): no name, slug or id reaches it.

THE SECOND SOURCE, ``--kind filled`` (2026-09-28, the orchestrator's order of
17:37): the live lane's session 4 ran the first-contact path on the same
person. Every link of the chain held and his words went in, 65 of 65, and the
last-moment check refused because Send read DISABLED straight after the fill.
About a second later the lane saved the same bubble through the piercing
locator as a skeleton, gitignored in its own state: the words in the editor,
and Send drawn WITHOUT ``disabled``. Built from that skeleton, the fixture is
``tests/fixtures/synthetic/first_contact_bubble_filled.html``. Its structure
differs from the empty bubble's only where the fill changed it: the editor's
paragraph holds the words where it held a line break, two classes moved, and
Send lost ``disabled``.

WHAT THE BUBBLE DRAWS (the structure this file keeps): a header whose one title
reads "New message" and whose two controls carry their labels as TEXT; a
recipient box with ONE committed recipient, a dismissible pill (its label, and
its text the name), and an empty search field; a card for that recipient,
linking to their profile; the message form -- an empty editor, Send DISABLED,
attach, GIF, emoji and a send-mode toggle.

MEASURED ON THE GITIGNORED SKELETON THE COPY WAS MADE FROM, BY KEYED HASH (the
same session's key on the profile's skeleton; the values were never read): the
pill's text and the card's name are EXACTLY the profile's topcard name, and the
card's two links name the same ``/in/`` segment as the topcard's own links. And
the SHAPES there (letters, digits, length) are what the DERIVED values below
were chosen to fit.

WHAT IS REPLACED, BY THE ELEMENT A VALUE STANDS IN:

    the pill's text, the card's name     -> the declared synthetic OWNER
    the pill's aria-label                 -> "Remove " + OWNER  (DERIVED: its
                                             shape was 6 letters, a space and
                                             the name's length)
    the card's /in/<x>/ links             -> /in/<OWNER_SLUG>/
    the card's degree                     -> "&#183; 1st"
    its a11y text                         -> "1st degree connection" (DERIVED,
                                             fitting its shape exactly)
    the presence text                     -> "Status is offline" (DERIVED,
                                             fitting its shape exactly)
    the header's CLOSE control's text
      (the control that is not the expand
      button)                             -> "Close your draft conversation"
                                             (DERIVED from its shape, 26
                                             letters in four words, and the
                                             form's own "... for your draft
                                             conversation" labels). THE ONE
                                             TEXT THE CLOSE STEP READS -- and it
                                             reads only its first word
    the editor's words (the filled
      bubble only)                        -> TYPED_WORDS, declared synthetic,
                                             fitted to the capture's shape: 65
                                             characters, 53 letters, no digit
    contenteditable, aria-multiline       -> "true" (their shape was four
                                             letters, and "true" is the one
                                             four-letter value either admits)
    every id, and every attribute naming
      one                                 -> example-id-<n>
    any other reduced text                -> "Example text"
    any other reduced aria-label          -> "Example label"

WHAT IS DROPPED: class tokens that are LinkedIn's hashed names (no hyphen, no
underscore, mixed case); image and icon addresses; hidden inputs' names and
values; ``data-*`` attributes but ``data-view-name``; every svg's drawing (the
``<svg>`` stays, empty); presentation attributes.

THE SHADOW ROOT IS NOT IN THIS FILE. The file is the bubble's markup alone; the
tests put it back inside an open shadow root, as the live page draws it.

It PRINTS COUNTS ONLY and writes no file but the fixture. Run over its own
output it reproduces it byte for byte (a FIXED POINT), and it prints a
STRUCTURE DIGEST -- tags and nesting only -- which
``tests/test_first_contact_message.py`` pins, and which the gitignored skeleton
gives too.

    python scripts/_build_first_contact_bubble.py [--source <path>] [--out <path>]
        [--kind empty|filled]
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _build_named_profile_skeleton import (  # noqa: E402
    OWNER,
    OWNER_SLUG,
    VOID,
    Text,
    Tree,
    ancestors,
    escape,
)

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO / "tests" / "fixtures" / "live3" / "m1_composer_bubble.html"
DEFAULT_OUT = REPO / "tests" / "fixtures" / "synthetic" / "first_contact_bubble.html"

#: A VALUE THE SOURCE REDUCED: one ``x`` (the tracked copy), or a keyed shape
#: (the gitignored skeleton it was made from, which this script also reads).
REDUCED = re.compile(r"^(?:x|\{L\d+D\d+n\d+:[0-9a-f]{8}\})$")
#: An id the source wrote: ``k`` and a hash (the copy), or a keyed shape.
SOURCE_ID = re.compile(r"^(?:k[0-9a-f]{8}|\{L\d+D\d+n\d+:[0-9a-f]{8}\})$")
EXAMPLE_ID = re.compile(r"^example-id-\d+$")
#: A member address the source wrote, its one segment reduced.
REDUCED_MEMBER_HREF = re.compile(r"^/in/(?:x|\{L\d+D\d+n\d+:[0-9a-f]{8}\})/$")
DOT = chr(0x00B7)

#: THE VALUES THIS SCRIPT WRITES, so that its own output is a fixed point.
PILL_LABEL = "Remove " + OWNER
DEGREE = DOT + " 1st"
DEGREE_A11Y = "1st degree connection"
PRESENCE = "Status is offline"
CLOSE_TEXT = "Close your draft conversation"
#: THE WORDS IN THE EDITOR of the filled bubble: declared, synthetic, and
#: the same shape as the words the capture reduced (65 characters, 53
#: letters, no digit). A test grants exactly these words to model a draft.
TYPED_WORDS = "Example words typed into the box and nothing else as they landed."
PLACEHOLDER_TEXT = "Example text"
PLACEHOLDER_LABEL = "Example label"
OWNER_HREF = "/in/" + OWNER_SLUG + "/"

#: LINKEDIN'S OWN WORDS THIS BUBBLE DRAWS, kept verbatim: the ones the live
#: lane's copy kept (its closed list), and nothing else.
KEPT_WORDS = frozenset({
    "New message", "Attach an image for your draft conversation",
    "Attach a file for your draft conversation", "Open GIF Keyboard",
    "Open Emoji Keyboard", "Send", "Open send options",
})
#: And the labels it keeps verbatim, on the same terms.
KEPT_LABELS = frozenset({
    "Messaging", "Write a message" + chr(0x2026),
    "Attach an image for your draft conversation",
    "Attach a file for your draft conversation", "Open GIF Keyboard",
    "Open Emoji Keyboard",
})
WRITTEN_TEXTS = frozenset({
    OWNER, DEGREE, DEGREE_A11Y, PRESENCE, CLOSE_TEXT, PLACEHOLDER_TEXT, TYPED_WORDS,
})
WRITTEN_LABELS = frozenset({PILL_LABEL, PLACEHOLDER_LABEL})

#: Attributes kept VERBATIM, each with the closed vocabulary it may hold; a
#: value outside it is DROPPED and counted, so a hand edit breaks the fixed
#: point.
ARIA_STATES = frozenset({"true", "false"})
KEPT_VALUES = {
    "role": frozenset({"none", "dialog", "combobox", "textbox", "button", "presentation"}),
    "type": frozenset({"button", "hidden", "file", "text", "submit", "circle",
                       "cancel-icon", "emoji-face-icon"}),
    "tabindex": frozenset({"-1", "0"}),
    "aria-expanded": ARIA_STATES,
    "aria-hidden": ARIA_STATES,
    "autocomplete": frozenset({"off"}),
    "dir": frozenset({"auto", "ltr", "rtl"}),
    "loading": frozenset({"lazy"}),
    "data-view-name": frozenset({"message-overlay-conversation-bubble-item"}),
    "contenteditable": frozenset({"true"}),
    "aria-multiline": frozenset({"true"}),
}
BOOLEAN_KEPT = ("disabled",)
#: The two attributes whose reduced value was, in the skeleton, four letters:
#: "true".
REDUCED_TO_TRUE = ("contenteditable", "aria-multiline")
#: Attributes that NAME an id.
ID_REFS = ("for", "aria-labelledby", "aria-describedby", "aria-controls", "aria-owns")
#: A class token LinkedIn hashes: letters only, mixed case, no separator.
HASHED_CLASS = re.compile(r"^[A-Za-z]{12,}$")


def keep_class_token(token: str) -> bool:
    if "-" in token or "_" in token:
        return True
    return not (HASHED_CLASS.match(token) and token != token.lower())


def classes(node) -> list[str]:
    return (node.get("class") or "").split()


def has_class(node, name: str) -> bool:
    return name in classes(node)


class Builder:
    def __init__(self, tree):
        self.tree = tree
        self.ids: dict[str, str] = {}
        self.written = 0
        self.counts = {
            "texts to the owner": 0, "texts to the words": 0, "derived texts": 0,
            "placeholder texts": 0,
            "unclassified texts": 0, "ids mapped": 0, "labels templated": 0,
            "placeholder labels": 0, "unclassified labels": 0,
            "hashed classes dropped": 0, "addresses rebuilt": 0, "addresses dropped": 0,
            "unclassified attributes": 0,
        }
        self.roots = [c for c in tree.root.children if not isinstance(c, Text)]

    # -- values -----------------------------------------------------------

    def id_for(self, value: str) -> str:
        if EXAMPLE_ID.match(value):
            self.ids.setdefault(value, value)
            return value
        if not SOURCE_ID.match(value):
            self.counts["unclassified attributes"] += 1
        if value not in self.ids:
            self.ids[value] = "example-id-%d" % (len(self.ids) + 1)
            self.counts["ids mapped"] += 1
        return self.ids[value]

    @staticmethod
    def _in(node, cls: str) -> bool:
        return any(has_class(a, cls) for a in [node] + list(ancestors(node)) if hasattr(a, "attrs"))

    def text_for(self, text_node) -> str:
        value = text_node.text
        parent = text_node.parent
        if value in KEPT_WORDS or value in WRITTEN_TEXTS:
            return value
        if not REDUCED.match(value):
            self.counts["unclassified texts"] += 1
            return PLACEHOLDER_TEXT
        if self._in(parent, "artdeco-pill__text") or (
            has_class(parent, "truncate") and self._in(parent, "profile-card-one-to-one__profile-link")
        ):
            self.counts["texts to the owner"] += 1
            return OWNER
        if self._in(parent, "msg-form__contenteditable"):
            self.counts["texts to the words"] += 1
            return TYPED_WORDS
        if has_class(parent, "artdeco-entity-lockup__degree"):
            self.counts["derived texts"] += 1
            return DEGREE
        if has_class(parent, "a11y-text") and self._in(parent, "artdeco-entity-lockup__badge"):
            self.counts["derived texts"] += 1
            return DEGREE_A11Y
        if self._in(parent, "presence-entity__indicator"):
            self.counts["derived texts"] += 1
            return PRESENCE
        control = next((a for a in ancestors(text_node) if hasattr(a, "attrs")
                        and has_class(a, "msg-overlay-bubble-header__control")), None)
        if control is not None and not has_class(control, "msg-overlay-conversation-bubble__expand-btn"):
            self.counts["derived texts"] += 1
            return CLOSE_TEXT
        self.counts["placeholder texts"] += 1
        return PLACEHOLDER_TEXT

    def label_for(self, node, value: str):
        if value in KEPT_LABELS or value in WRITTEN_LABELS:
            return value
        if not REDUCED.match(value):
            self.counts["unclassified labels"] += 1
            return PLACEHOLDER_LABEL
        if has_class(node, "artdeco-pill--dismiss"):
            self.counts["labels templated"] += 1
            return PILL_LABEL
        self.counts["placeholder labels"] += 1
        return PLACEHOLDER_LABEL

    def href_for(self, node, value: str):
        if value == OWNER_HREF:
            return value
        if node.tag == "a" and REDUCED_MEMBER_HREF.match(value):
            self.counts["addresses rebuilt"] += 1
            return OWNER_HREF
        self.counts["addresses dropped"] += 1
        return None

    # -- output -----------------------------------------------------------

    def render(self, header: str) -> str:
        out = [header]
        for root in self.roots:
            self._write(root, out)
        out.append("\n")
        return "".join(out)

    def _write(self, node, out) -> None:
        if isinstance(node, Text):
            out.append(escape(self.text_for(node)))
            return
        attrs = []
        for key, value in node.attrs:
            if key in BOOLEAN_KEPT:
                if value in (None, "", key):
                    attrs.append((key, None))
                else:
                    self.counts["unclassified attributes"] += 1
                continue
            if value is None:
                continue
            if key == "class":
                kept = []
                for token in value.split():
                    if keep_class_token(token):
                        kept.append(token)
                    else:
                        self.counts["hashed classes dropped"] += 1
                if kept:
                    attrs.append((key, " ".join(kept)))
            elif key in REDUCED_TO_TRUE and REDUCED.match(value):
                attrs.append((key, "true"))
            elif key in KEPT_VALUES:
                if value in KEPT_VALUES[key]:
                    attrs.append((key, value))
                else:
                    self.counts["unclassified attributes"] += 1
            elif key == "id":
                attrs.append((key, self.id_for(value)))
            elif key in ID_REFS:
                attrs.append((key, " ".join(self.id_for(v) for v in value.split())))
            elif key == "aria-label":
                attrs.append((key, self.label_for(node, value)))
            elif key == "title":
                if value in KEPT_LABELS:
                    attrs.append((key, value))
            elif key == "href" and node.tag == "a":
                href = self.href_for(node, value)
                if href is not None:
                    attrs.append((key, href))
            # every other attribute is DROPPED: data-*, sizes, addresses of
            # images and icons, hidden inputs' names and values.
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


HEADER = """<!--
  BUILT FROM A LIVE CAPTURE'S TRACKED COPY, PEOPLED WITH DECLARED SYNTHETIC
  VALUES. NOT A CAPTURE: nobody here is anybody.

  The NEW-MESSAGE bubble a Message press on a first-degree profile opens when
  there is no conversation yet -- LinkedIn's messaging overlay, drawn inside an
  OPEN SHADOW ROOT, as the live lane's session 3 captured it on 2026-09-28. The
  ONE LIVE-TRUE SOURCE is that lane's tracked copy,
  tests/fixtures/live3/m1_composer_bubble.html; scripts/_build_first_contact_bubble.py
  turned it into this file, and says line by line what it kept and what it put
  in place. The shadow root is not in this file: the tests put the bubble back
  inside one.

  MEASURED (the structure is the capture's): one title, "New message"; two
  header controls whose labels are their text; a recipient box holding ONE
  committed recipient -- a dismissible pill whose text is the recipient's name
  -- and an empty search field; a card for that recipient linking to their
  profile; the form, its editor empty and Send DISABLED. On the capture the
  pill's text and the card's name were exactly the profile's topcard name, and
  the card linked the topcard's own profile (compared by keyed hash).

  DERIVED, and the builder's docstring argues each: the pill's label
  ("Remove " and the name), the degree's words, the presence words, and the
  close control's text -- only its first word is ever read.
-->
"""

HEADER_FILLED = """<!--
  BUILT FROM A LIVE CAPTURE'S SKELETON, PEOPLED WITH DECLARED SYNTHETIC
  VALUES. NOT A CAPTURE: nobody here is anybody.

  The NEW-MESSAGE bubble of a first contact AFTER HIS WORDS WENT IN -- the
  live lane's session 4, 2026-09-28, about a second after the fill, saved
  through the piercing locator as a gitignored skeleton in that lane's own
  state. scripts/_build_first_contact_bubble.py --kind filled turned it into
  this file, and says line by line what it kept and what it put in place.
  The shadow root is not in this file: the tests put the bubble back inside
  one.

  MEASURED (the structure is the capture's): the empty bubble's structure,
  except where the fill changed it -- the editor's paragraph holds the words,
  and Send is drawn WITHOUT disabled. Straight after the fill the gate read
  that same Send as disabled: LinkedIn turns it on after the words land.

  DERIVED, as in the empty bubble; and the words are declared synthetic,
  fitted to the shape of the words the capture reduced.
-->
"""
HEADERS = {"empty": HEADER, "filled": HEADER_FILLED}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--kind", choices=sorted(HEADERS), default="empty")
    args = parser.parse_args(argv)
    tree = Tree()
    tree.feed(args.source.read_text(encoding="utf-8"))
    tree.close()
    builder = Builder(tree)
    text = builder.render(HEADERS[args.kind])
    assert all(ord(ch) < 128 for ch in text)
    args.out.write_text(text, encoding="ascii", newline="\n")
    print("roots              %d" % len(builder.roots))
    print("elements written   %d" % builder.written)
    for key in sorted(builder.counts):
        print("%-18s %d" % (key, builder.counts[key]))
    print("structure digest %s" % fragment_digest(builder.roots))
    return 0


def fragment_digest(roots) -> str:
    """The profile builder's digest (tags and nesting, an svg counted and not
    entered, sixteen letters), over a fragment: each root in turn."""
    lines: list[str] = []
    for root in roots:
        _lines(root, 0, lines)
    digest = hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()[:16]
    return digest.translate(str.maketrans("0123456789abcdef", "abcdefghijklmnop"))


def _lines(node, depth, lines) -> None:
    if isinstance(node, Text):
        lines.append("%d:#text" % depth)
        return
    lines.append("%d:%s" % (depth, node.tag))
    if node.tag != "svg" and node.tag not in VOID:
        for child in node.children:
            _lines(child, depth + 1, lines)


if __name__ == "__main__":
    sys.exit(main())
