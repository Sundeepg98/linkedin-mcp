"""Turn a captured PROFILE-VIEWS page into a skeleton fixture: its STRUCTURE, with every member's text reduced to shape.

Kept as the PROVENANCE of the profile-views skeletons under
``tests/fixtures/synthetic/profile_views_*.html``: the exact record of what
was taken from a capture of ``/analytics/profile-views/`` and what was put in
its place. Modelled on ``scripts/_build_people_search_skeleton.py``, with one
difference in kind: that builder peoples its skeleton with declared synthetic
people, and this one invents nobody. A member's text is REDUCED TO SHAPE, so
the page keeps its lengths, its digits and its punctuation and loses every
letter.

WHAT IS KEPT. The ``<body>`` subtree (``<head>`` is dropped), every element's
TAG and NESTING, and these attributes, each with the rule for its value:

    class, role, type, tabindex   verbatim when the value is one the
                                  attribute's own vocabulary allows: class
                                  tokens of [A-Za-z0-9_-] (another token is
                                  dropped), a role made of WAI-ARIA roles
                                  (ROLE_TOKENS), a type that is one of HTML's
                                  keywords (TYPE_VALUES), an integer
                                  tabindex; any other value is DROPPED
    disabled, hidden              kept, as bare boolean attributes
                                  (hidden="until-found" stays as written)
    data-view-name                verbatim if it matches ^[a-z0-9-]+$, else
                                  dropped
    aria-*                        an id reference (ID_REFERENCES) is REDUCED TO
                                  SHAPE; a value made only of ARIA's own tokens
                                  (ARIA_TOKENS) or a number is kept verbatim;
                                  any other value follows the TEXT rule below
    href                          a member link (/in/<slug> anywhere in the
                                  href, as dom.PERSON_HREF finds it) becomes
                                  https://www.linkedin.com/in/<the slug reduced
                                  to shape: letters x, digits 0, - _ % kept>/ ;
                                  any other href -- the self alias /in/me/
                                  among them, which names nobody -- keeps a
                                  LinkedIn host, keeps the path segments in
                                  ROUTE_WORDS and writes "example" for every
                                  other one. Query strings and fragments are
                                  always dropped.

WHAT IS DROPPED. script, style, template, noscript, link and meta elements
with everything inside them; comments; an svg's children (the svg stays,
empty, with its kept attributes); and every attribute not listed above --
among them src, style, id, for, componentkey, alt, title, value, placeholder,
name, checked, popover, inert, and every data-* but data-view-name.

THE TEXT RULE -- text nodes, and aria values that are neither vocabulary nor
an id reference -- after collapsing each run of HTML whitespace (space, tab,
line feed, form feed, carriage return) to one space:

    kept VERBATIM     when it EQUALS a phrase of UI_ALLOWLIST, or matches one
                      of UI_TEMPLATES (whose only variable part is a number);
                      both compared by match_key, which ignores letter case
                      and reads typographic quotes, dashes and bullets as
                      their ASCII spellings, and admits nothing else that is
                      not ASCII -- or when it is purely NUMERIC (digits
                      , . % + and a leading bullet)
    REDUCED TO SHAPE  otherwise: every upper-case letter becomes X, every
                      other letter x; digits, whitespace and punctuation are
                      kept; any other character becomes ?

A text node that is only whitespace is KEPT, collapsed (a no-break space is
not HTML whitespace and stays as drawn): the page draws spans and paragraphs
holding a single space, and a paragraph of that kind sits between a number
and its label. One made of HTML whitespace holding a line break is
formatting, and is dropped -- which is what lets this builder write line
breaks of its own between block elements (BLOCK) and still read its output
back unchanged.

THE ALLOWLIST IS INTERFACE WORDS ONLY. Every phrase in it comes from a source
that cannot hold a person, named beside it: the phrases this package's
readers match, the vocabulary ``_audit/2026-09-23-live-lane-session-1.md``
wrote down (Entries 3, 7 and 8), and the chrome of the tracked, sanitised
``tests/fixtures/profile_views_analytics.html``. NOTHING IS ADDED BECAUSE A
CAPTURE SHOWED IT: text a capture draws that looks like interface text but is
not listed here is shaped like any other, and counted.

THE RAW CAPTURE IS NEVER COMMITTED -- it lists other members. Re-run this only
against a fresh capture:

    python scripts/_build_profile_views_skeleton.py --capture <path> --out <path>

IT PRINTS COUNTS ONLY, and a structure digest -- tags and nesting, sixteen
letters -- which is the same whether it runs over a capture or over the
skeleton it wrote. Run over its own output it reproduces it byte for byte. It
REFUSES a capture with no ``<main>``, printing why and no page text.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import string
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

# ---------------------------------------------------------------------------
# THE ALLOWLIST -- LinkedIn's own interface words, each with its source
# ---------------------------------------------------------------------------

_VIEW_SWITCH = "linkedin_server/view_switch.py VIEW_SWITCHES"
_APPLY = "linkedin_server/view_switch.py APPLY_PATTERN"
_REVEAL = "linkedin_server/reveal.py DECIDED_REVEALS"
_MORE = "linkedin_server/profile_views_more.py"
_READINGS = "linkedin_server/press.py OPEN_READINGS"
_DOM = "linkedin_server/dom.py, the profile-views insights block"
_AUDIT = "_audit/2026-09-23-live-lane-session-1.md Entries 3, 7, 8"
_FIXTURE = "tests/fixtures/profile_views_analytics.html (tracked, sanitised)"

#: EVERY PHRASE KEPT VERBATIM, and who vouches for it. Written as the source
#: spells it; compared through :func:`match_key`, so the readers' normalised
#: lower-case phrases cover the page's capitalised spelling of the same words.
UI_ALLOWLIST: dict[str, str] = {
    # The view switch: the pill it opens, its two options, its apply button.
    "interesting viewers": _VIEW_SWITCH + " pill_caption; " + _READINGS + "; " + _FIXTURE,
    "verified": _VIEW_SWITCH + " option; " + _AUDIT,
    "works at a company you follow": _VIEW_SWITCH + " option; " + _AUDIT,
    "show results": _APPLY + "; " + _READINGS + "; " + _AUDIT,
    # The decided reveal, and the two plain buttons its entry names beside it.
    "show more analytics": _REVEAL + " phrase; " + _READINGS + "; " + _FIXTURE,
    "all filters": _REVEAL + " why; " + _READINGS + "; " + _FIXTURE,
    "reset": _REVEAL + " why; " + _READINGS + "; " + _FIXTURE,
    # What the reveal draws: section headings, highlight labels, sub-heading.
    "highlights": _MORE + " SECTIONS; " + _AUDIT,
    "details": _MORE + " SECTIONS; " + _AUDIT,
    "top location": _MORE + " HIGHLIGHT_LABELS",
    "top industry": _MORE + " HIGHLIGHT_LABELS",
    "top company": _MORE + " HIGHLIGHT_LABELS",
    "companies": _MORE + " docstring, the Details sub-heading; " + _AUDIT,
    # The filter menu's reading: time ranges, viewer categories, controls.
    "past 7 days": _READINGS,
    "past 14 days": _READINGS,
    "past 28 days": _READINGS,
    "past 30 days": _READINGS,
    "past 90 days": _READINGS + "; " + _DOM + "; " + _FIXTURE,
    "past 365 days": _READINGS,
    "past year": _READINGS,
    "all viewers": _READINGS,
    "recruiters": _READINGS,
    "hiring managers": _READINGS,
    "your network": _READINGS,
    "people at your company": _READINGS,
    "senior leaders": _READINGS,
    "decision makers": _READINGS,
    "cancel": _READINGS,
    "apply": _READINGS,
    # The feed's share menu, the other OPEN_READINGS entry.
    "copy link to post": _READINGS,
    "copy link": _READINGS,
    "embed this post": _READINGS,
    "share via": _READINGS,
    # The profile-views insights reader's measured block.
    "Profile viewers": _DOM + "; " + _FIXTURE,
    "Company": _DOM + "; " + _FIXTURE,
    "Chart. Highcharts interactive chart.": _DOM + "; " + _FIXTURE,
    "Who's viewed your profile": "linkedin_server/dom.py harvest note; " + _FIXTURE,
    # The chrome of the sanitised fixture: headings, buttons, labels.
    "Chart": _FIXTURE,
    "End of interactive chart.": _FIXTURE,
    "Message": _FIXTURE,
    "Connect": _FIXTURE,
    "Follow": _FIXTURE,
    "Search": _FIXTURE,
    "Most recent": _FIXTURE,
    "Most relevant": _FIXTURE,
    "View all recruiters": _FIXTURE,
    "Primary content": _FIXTURE,
    "Filter by Past 90 days": _FIXTURE,
    "Filter by Interesting viewers": _FIXTURE,
    "Filter by Company": _FIXTURE,
    "more information about Who's viewed your profile": _FIXTURE,
}

#: Interface sentences whose ONLY variable part is a number, so no person can
#: sit in one. Patterns are matched in full against :func:`match_key`, which
#: is lower case and reads a bullet as ``*``.
UI_TEMPLATES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"show(?: [0-9][0-9,]*)? results?"), _APPLY),
    (re.compile(r"line chart with [0-9]+ data points?\."), _DOM + "; " + _FIXTURE),
    (re.compile(r"vs\. prior [0-9]+ days?"), _DOM + "; " + _FIXTURE),
    (re.compile(r"viewed [0-9]+(?:s|m|h|d|w|mo|y|yr)s? ago"), _FIXTURE),
    (re.compile(r"[0-9]+ (?:other )?mutual connections?"),
     _FIXTURE + "; scripts/_build_people_search_skeleton.py OTHERS"),
    (re.compile(r"[0-9]+ recruiters? viewed your profile"), _FIXTURE),
    (re.compile(r"(?:\* ?)?(?:1st|2nd|3rd\+?)"),
     _FIXTURE + "; scripts/_build_people_search_skeleton.py DEGREE"),
)

#: Typographic characters read as their ASCII spelling BY match_key ONLY --
#: what is written is still the page's own character. Built from code points
#: so this file stays ASCII.
_TYPOGRAPHIC = {
    0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"',
    0x2013: "-", 0x2014: "-", 0x2026: "...", 0x2022: "*", 0x00B7: "*",
}

_BULLETS = re.escape(chr(0x2022) + chr(0x00B7))
#: Purely numeric: digits , . % + and a leading bullet, at least one digit.
NUMERIC = re.compile("(?:[" + _BULLETS + "] ?)?[0-9.,%+]*[0-9][0-9.,%+]*")

# ---------------------------------------------------------------------------
# ATTRIBUTES
# ---------------------------------------------------------------------------

#: ARIA's own vocabulary. The first line is the brief's list; the rest are
#: the remaining enumerated tokens of WAI-ARIA 1.2 (aria-autocomplete,
#: -orientation, -sort, -relevant, -invalid, -dropeffect), none of which can
#: carry a person.
ARIA_TOKENS = frozenset({
    "true", "false", "mixed", "page", "step", "location", "date", "time",
    "menu", "listbox", "tree", "grid", "dialog", "polite", "assertive", "off", "on",
    "inline", "list", "both", "none", "horizontal", "vertical", "undefined",
    "ascending", "descending", "other", "additions", "all", "removals", "text",
    "grammar", "spelling", "copy", "execute", "link", "move", "popup",
})
ARIA_NUMBER = re.compile(r"-?[0-9]+(?:\.[0-9]+)?")
ARIA_NAME = re.compile(r"aria-[a-z]+")
#: ARIA attributes whose value names other elements by id. Ids are dropped, so
#: each reference dangles; it is reduced to shape and never allowlisted.
ID_REFERENCES = frozenset({
    "aria-controls", "aria-labelledby", "aria-describedby", "aria-owns",
    "aria-activedescendant", "aria-details", "aria-errormessage", "aria-flowto",
})

CLASS_TOKEN = re.compile(r"[A-Za-z0-9_-]+")
TABINDEX_VALUE = re.compile(r"-?[0-9]+")
VIEW_NAME_VALUE = re.compile(r"[a-z0-9-]+")
BOOLEAN_ATTRIBUTES = ("disabled", "hidden")

#: A role is kept only when every token of it is a WAI-ARIA 1.2 role (or a
#: graphics-* role). A closed set rather than a grammar: a grammar of lower-case
#: words would pass any word at all.
ROLE_TOKENS = frozenset({
    "alert", "alertdialog", "application", "article", "banner", "blockquote",
    "button", "caption", "cell", "checkbox", "code", "columnheader", "combobox",
    "command", "comment", "complementary", "composite", "contentinfo",
    "definition", "deletion", "dialog", "directory", "document", "emphasis",
    "feed", "figure", "form", "generic", "grid", "gridcell", "group", "heading",
    "img", "image", "input", "insertion", "landmark", "link", "list", "listbox",
    "listitem", "log", "main", "mark", "marquee", "math", "menu", "menubar",
    "menuitem", "menuitemcheckbox", "menuitemradio", "meter", "navigation",
    "none", "note", "option", "paragraph", "presentation", "progressbar",
    "radio", "radiogroup", "range", "region", "roletype", "row", "rowgroup",
    "rowheader", "scrollbar", "search", "searchbox", "section", "sectionhead",
    "select", "separator", "slider", "spinbutton", "status", "strong",
    "structure", "subscript", "suggestion", "superscript", "switch", "tab",
    "table", "tablist", "tabpanel", "term", "textbox", "time", "timer",
    "toolbar", "tooltip", "tree", "treegrid", "treeitem", "widget", "window",
    "graphics-document", "graphics-object", "graphics-symbol",
})
#: A type is kept only when it is one of HTML's own keywords for input and
#: button elements.
TYPE_VALUES = frozenset({
    "button", "checkbox", "color", "date", "datetime-local", "email", "file",
    "hidden", "image", "menu", "month", "number", "password", "radio", "range",
    "reset", "search", "submit", "tel", "text", "time", "url", "week",
})

#: dom.PERSON_HREF, copied rather than imported so this script needs nothing
#: from the package: a member link is ``/in/<slug>`` anywhere in the href.
PERSON_HREF = re.compile(r"/in/([A-Za-z0-9\-_%]{2,})")
MEMBER_BASE = "https://www.linkedin.com/in/"
#: LinkedIn's alias for the viewer's OWN profile. It names nobody, so a link to
#: it is not a member link: it is written like any other href, and since "in"
#: and "me" are route words it keeps its address. The same exception
#: scripts/_build_people_search_skeleton.py makes (member_key), and the one
#: tests/test_fixtures_hold_only_synthetic_people.py (SELF_ALIAS) and
#: tests/test_no_committed_identity.py (_slug_ok) make when they read one.
SELF_ALIAS = "me"

#: The literal path segments of ``linkedin_server/readonly.py``'s
#: _ALLOWED_URL_PATTERNS -- the package's admitted read addresses -- which
#: include every route word ``scripts/_build_people_search_skeleton.py`` keeps.
#: A segment of an href not in this set is written as PLACEHOLDER_SEGMENT.
ROUTE_WORDS = frozenset({
    "alerts", "all", "analytics", "article", "articles", "attendees", "audience",
    "collections", "company", "compose", "connections", "contact-info", "content",
    "creator", "dark-mode", "dashboard", "details", "discover", "edit", "events",
    "feed", "followers", "groups", "in", "interests", "intro", "invite-connect",
    "jam", "jobs", "jobs-tracker", "learning", "login", "me", "members",
    "messaging", "my-premium", "mynetwork", "mypreferences", "network-manager",
    "new", "newsletters", "notifications", "notify-network-for-updates",
    "overlay", "people", "people-follow", "post-summary", "preload", "premium",
    "profile-key-skills", "profile-views", "recent-activity", "recommended",
    "recruiter-views", "results", "role-play", "scenarios", "school", "search",
    "search-appearances", "settings", "sharebox", "thread", "top-applicant",
    "top-choice", "update", "view",
})
PLACEHOLDER_SEGMENT = "example"
LINKEDIN_HOSTS = frozenset({"www.linkedin.com", "linkedin.com"})
PLACEHOLDER_HOST = "https://example.invalid"

# ---------------------------------------------------------------------------
# ELEMENTS
# ---------------------------------------------------------------------------

VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                  "link", "meta", "param", "source", "track", "wbr"})
DROP_SUBTREE = frozenset({"script", "style", "template", "noscript", "link", "meta"})
#: Elements kept EMPTY: their children are drawing, not page.
FOREIGN = frozenset({"svg", "math"})
#: Elements a browser draws as blocks with no stylesheet. A line break between
#: two of them, siblings with nothing between, is never drawn -- so the builder
#: writes one there, and drops it when it reads its own output.
BLOCK = frozenset({
    "address", "article", "aside", "blockquote", "details", "dialog", "dd", "div",
    "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2",
    "h3", "h4", "h5", "h6", "header", "hgroup", "hr", "li", "main", "menu", "nav",
    "ol", "p", "section", "search", "summary", "table", "ul",
})
#: Parents inside which whitespace is drawn, so no line break is written.
KEEPS_WHITESPACE = frozenset({"pre", "textarea", "listing", "plaintext", "xmp"})

_PUNCTUATION = frozenset(string.punctuation)


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag, attrs, parent, text=None):
        self.tag, self.attrs, self.parent, self.text = tag, attrs, parent, text
        self.children = []


class Tree(HTMLParser):
    """The capture as it was SERIALISED. Adjacent text is one node, as the
    page's parser would make it; comments are not kept."""

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
        children = self.cur.children
        if children and children[-1].tag == "#text":
            children[-1].text += data
        else:
            children.append(Node("#text", [], self.cur, data))


def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)


# ---------------------------------------------------------------------------
# TEXT
# ---------------------------------------------------------------------------


#: HTML's own whitespace -- space, tab, line feed, form feed, carriage return
#: -- the characters a browser collapses. A no-break space is not one of them
#: and is kept as the page drew it.
_HTML_SPACE_RUN = re.compile(r"[ \t\n\f\r]+")
_FORMATTING = re.compile(r"[ \t\n\f\r]*[\n\r][ \t\n\f\r]*")


def collapse(text):
    """Each run of HTML whitespace becomes one space; the ends are NOT
    stripped."""
    return _HTML_SPACE_RUN.sub(" ", text or "")


def match_key(text):
    """The spelling the allowlist is compared on: every whitespace run one
    space, the ends stripped, typographic punctuation read as ASCII, lower
    case. None if anything else in it is not ASCII -- so a letter outside
    ASCII can never ride along on an interface phrase."""
    key = re.sub(r"\s+", " ", text or "").strip().translate(_TYPOGRAPHIC).lower()
    return key if key.isascii() else None


_ALLOW_KEYS = frozenset(match_key(phrase) for phrase in UI_ALLOWLIST)


def allowlisted(text):
    """'phrase', 'template' or None. PURE."""
    key = match_key(text)
    if not key:
        return None
    if key in _ALLOW_KEYS:
        return "phrase"
    if any(pattern.fullmatch(key) for pattern, _source in UI_TEMPLATES):
        return "template"
    return None


def is_numeric(text):
    return NUMERIC.fullmatch(collapse(text).strip()) is not None


def shape(text):
    """Letters to X or x; digits, spaces and punctuation kept; anything else
    ``?``. The same length as its input, and its own fixed point."""
    out = []
    for character in text:
        if character == " " or "0" <= character <= "9":
            out.append(character)
        elif character.isascii():
            if character.isalpha():
                out.append("X" if character.isupper() else "x")
            elif character in _PUNCTUATION:
                out.append(character)
            elif character.isspace():
                out.append(" ")
            else:
                out.append("?")
        else:
            category = unicodedata.category(character)
            if category[0] in "LM":
                out.append("X" if category in ("Lu", "Lt") else "x")
            elif category[0] in "PZ" or category == "Nd":
                out.append(character)
            else:
                out.append("?")
    return "".join(out)


def is_formatting(text):
    """HTML whitespace holding a line break, and nothing else: layout, not
    page."""
    return _FORMATTING.fullmatch(text) is not None


def classify(text):
    """(kind, what is written) for one text value, by THE TEXT RULE. PURE."""
    collapsed = collapse(text)
    if not collapsed.strip():
        return "space", collapsed
    found = allowlisted(collapsed)
    if found:
        return "verbatim-" + found, collapsed
    if is_numeric(collapsed):
        return "numeric", collapsed
    return "shaped", shape(collapsed)


def shape_slug(slug):
    """A member slug's shape: letters x, digits 0, every other character kept."""
    return "".join(
        "x" if c.isascii() and c.isalpha() else "0" if c.isascii() and c.isdigit() else c
        for c in slug
    )


# ---------------------------------------------------------------------------
# THE SKELETON
# ---------------------------------------------------------------------------


def kept_children(node):
    """A node's children as written: dropped elements skipped, and the text on
    either side of one merged, as the page's parser would merge it."""
    items = []
    for child in node.children:
        if child.tag in DROP_SUBTREE:
            continue
        if child.tag == "#text":
            if items and isinstance(items[-1], str):
                items[-1] += child.text
            else:
                items.append(child.text)
        else:
            items.append(child)
    return items


def _escape_text(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _escape_attribute(value):
    return (value.replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


class Skeleton:
    def __init__(self):
        self.counts = {}

    def count(self, key, by=1):
        self.counts[key] = self.counts.get(key, 0) + by

    def text(self, value):
        kind, written = classify(value)
        self.count("text " + kind)
        return written

    def aria(self, name, value):
        collapsed = collapse(value or "")
        tokens = collapsed.split()
        if name in ID_REFERENCES:
            kind, written = "id reference", shape(collapsed.strip(" "))
        elif tokens and all(token in ARIA_TOKENS for token in tokens):
            kind, written = "vocabulary", " ".join(tokens)
        elif ARIA_NUMBER.fullmatch(collapsed.strip(" ")):
            kind, written = "number", collapsed.strip(" ")
        elif not collapsed.strip(" "):
            kind, written = "empty", ""
        else:
            kind, written = classify(collapsed)
        self.count("aria %s" % kind)
        if name == "aria-label":
            self.count("aria-label %s" % ("shaped" if kind == "shaped" else "kept"))
        return written

    def href(self, value):
        value = (value or "").strip()
        found = PERSON_HREF.search(value)
        if found and found.group(1) != SELF_ALIAS:
            self.count("member hrefs")
            return MEMBER_BASE + shape_slug(found.group(1)) + "/"
        if found:
            self.count("other hrefs: the self alias")
        self.count("other hrefs")
        parts = urlsplit(value)
        if parts.query:
            self.count("other hrefs: queries dropped")
        if parts.fragment:
            self.count("other hrefs: fragments dropped")
        host = (parts.hostname or "").lower()
        if parts.netloc and host in LINKEDIN_HOSTS:
            base = "https://" + host
        elif parts.netloc:
            self.count("other hrefs: placeholder hosts")
            base = PLACEHOLDER_HOST
        else:
            base = ""
        mapped = []
        for segment in (s for s in parts.path.split("/") if s):
            if segment in ROUTE_WORDS:
                self.count("other hrefs: route words kept")
                mapped.append(segment)
            else:
                self.count("other hrefs: segments replaced")
                mapped.append(PLACEHOLDER_SEGMENT)
        return base + "/" + "/".join(mapped) + ("/" if mapped else "")

    def attributes(self, node):
        out, seen = [], set()
        for name, value in node.attrs:
            if name in seen:
                self.count("attributes dropped: duplicates")
                continue
            seen.add(name)
            value = value if value is not None else ""
            if name == "href":
                out.append(("href", self.href(value)))
            elif name == "class":
                tokens = value.split()
                good = [t for t in tokens if CLASS_TOKEN.fullmatch(t)]
                if len(good) != len(tokens):
                    self.count("class tokens dropped: off-grammar", len(tokens) - len(good))
                if good:
                    out.append(("class", " ".join(good)))
            elif name in ("role", "type", "tabindex", "data-view-name"):
                if name == "role":
                    good = bool(value.split()) and all(t in ROLE_TOKENS for t in value.split())
                elif name == "type":
                    good = value in TYPE_VALUES
                elif name == "tabindex":
                    good = TABINDEX_VALUE.fullmatch(value) is not None
                else:
                    good = VIEW_NAME_VALUE.fullmatch(value) is not None
                if good:
                    out.append((name, " ".join(value.split()) if name == "role" else value))
                else:
                    self.count("attribute values dropped: off-grammar %s" % name)
            elif name in BOOLEAN_ATTRIBUTES:
                out.append((name, "until-found" if (name, value) == ("hidden", "until-found") else None))
            elif name.startswith("aria-"):
                if ARIA_NAME.fullmatch(name):
                    out.append((name, self.aria(name, value)))
                else:
                    self.count("attributes dropped: off-grammar aria name")
            else:
                self.count("attributes dropped")
        return out

    def emit(self, node, out):
        self.count("elements kept")
        rendered = "".join(
            " %s" % name if value is None else ' %s="%s"' % (name, _escape_attribute(value))
            for name, value in self.attributes(node)
        )
        tag = node.tag
        if tag in FOREIGN:
            self.count("elements dropped: inside svg or math",
                       sum(1 for d in walk(node) if d is not node and not d.tag.startswith("#")))
            out.append("<%s%s></%s>" % (tag, rendered, tag))
            return
        out.append("<%s%s>" % (tag, rendered))
        if tag in VOID:
            return
        previous = None
        for item in kept_children(node):
            if isinstance(item, str):
                if is_formatting(item):
                    self.count("text formatting dropped")
                    continue
                out.append(_escape_text(self.text(item)))
                previous = None
                continue
            if (previous is not None and previous.tag in BLOCK and item.tag in BLOCK
                    and tag not in KEEPS_WHITESPACE):
                out.append("\n")
            self.emit(item, out)
            previous = item
        out.append("</%s>" % tag)


def structure(node, depth=0, out=None):
    """The kept STRUCTURE, exactly as :meth:`Skeleton.emit` writes it: each
    element's tag at its depth and each text node as a mark -- no attribute,
    no text. Pure; the same on a capture and on the skeleton it produced."""
    if out is None:
        out = []
    out.append("%d:%s" % (depth, node.tag))
    if node.tag in FOREIGN or node.tag in VOID:
        return out
    for item in kept_children(node):
        if isinstance(item, str):
            if not is_formatting(item):
                out.append("%d:#text" % (depth + 1))
        else:
            structure(item, depth + 1, out)
    return out


#: The digest's alphabet: hex digits spelled as letters, as the people-search
#: builder spells its own.
_DIGEST_LETTERS = str.maketrans("0123456789abcdef", "abcdefghijklmnop")


def structure_digest(body):
    """A digest of the kept body's structure, sixteen letters."""
    digest = hashlib.sha256("\n".join(structure(body)).encode("utf-8")).hexdigest()[:16]
    return digest.translate(_DIGEST_LETTERS)


def kept_elements(node):
    """Every element the skeleton writes, in document order."""
    yield node
    if node.tag in FOREIGN or node.tag in VOID:
        return
    for item in kept_children(node):
        if not isinstance(item, str):
            yield from kept_elements(item)


HEADER = """<!DOCTYPE html>
<!-- A SKELETON of LinkedIn's profile-views analytics page, written by
     scripts/_build_profile_views_skeleton.py from a raw capture that is never
     committed, because it lists other members. KEPT: the body's elements,
     their tags and nesting, and the attributes class, role, type, disabled,
     hidden, tabindex, data-view-name and aria-*. EVERY MEMBER'S TEXT IS
     REDUCED TO SHAPE BY THE BUILDER: an upper-case letter became X, any other
     letter x, and digits, spaces and punctuation stayed. Only LinkedIn's own
     interface words from the builder's declared allowlist, and plain numbers,
     are written as the page drew them. A member link keeps only the shape of
     its slug; any other link keeps its route words and reads "example"
     elsewhere. Scripts, styles, ids, sources and every other attribute are
     gone. The line breaks sit between block elements and are not the page's. -->
<html lang="en">
<head><meta charset="utf-8"><title>Profile views (skeleton)</title></head>
"""
FOOTER = "\n</html>\n"


def build(source_text):
    """(document text, counts, digest), or raise SystemExit with a reason
    that quotes nothing from the page."""
    tree = Tree()
    tree.feed(source_text)
    tree.close()
    bodies = [n for n in walk(tree.root) if n.tag == "body"]
    if not bodies:
        raise SystemExit("refused: the capture has no <body> element")
    body = bodies[0]
    mains = [n for n in kept_elements(body) if n.tag == "main"]
    if not mains:
        raise SystemExit("refused: the capture has no <main> element -- "
                         "not a profile-views page as this builder knows it")
    skeleton = Skeleton()
    everything = [n for n in walk(body) if not n.tag.startswith("#")]
    in_dropped = sum(
        1 for n in everything
        if n.tag in DROP_SUBTREE or any(a.tag in DROP_SUBTREE for a in _ancestors(n, body))
    )
    skeleton.count("elements in the body", len(everything))
    skeleton.count("elements dropped: script, style, template, noscript, link, meta", in_dropped)
    head_elements = sum(1 for h in walk(tree.root) if h.tag == "head"
                        for n in walk(h) if not n.tag.startswith("#"))
    skeleton.count("elements dropped: head", head_elements)
    skeleton.count("main elements", len(mains))
    skeleton.count("elements under main", sum(
        sum(1 for _ in kept_elements(main)) - 1 for main in mains))
    out = []
    skeleton.emit(body, out)
    text = HEADER + "".join(out) + FOOTER
    # THE FILE IS ASCII: anything else travels as a numeric character
    # reference, which every HTML parser decodes.
    text = text.encode("ascii", "xmlcharrefreplace").decode("ascii")
    return text, skeleton.counts, structure_digest(body)


def _ancestors(node, stop):
    walker = node.parent
    while walker is not None and walker is not stop:
        yield walker
        walker = walker.parent


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--capture", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    source, target = Path(args.capture), Path(args.out)
    if source.resolve() == target.resolve():
        raise SystemExit("refused: --out is the capture itself")
    text, counts, digest = build(source.read_bytes().decode("utf-8", errors="replace"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(text.encode("ascii"))
    get = counts.get
    in_body = get("elements in the body", 0)
    print("elements: in body", in_body, "| kept", get("elements kept", 0),
          "| dropped", in_body - get("elements kept", 0),
          "(script/style/template/noscript/link/meta subtrees %d, inside svg/math %d)"
          % (get("elements dropped: script, style, template, noscript, link, meta", 0),
             get("elements dropped: inside svg or math", 0)),
          "| head dropped", get("elements dropped: head", 0),
          "| main", get("main elements", 0), "| under main", get("elements under main", 0))
    print("text nodes: verbatim", get("text verbatim-phrase", 0) + get("text verbatim-template", 0),
          "(phrase %d, template %d)" % (get("text verbatim-phrase", 0), get("text verbatim-template", 0)),
          "| numeric", get("text numeric", 0), "| shaped", get("text shaped", 0),
          "| whitespace kept", get("text space", 0),
          "| formatting dropped", get("text formatting dropped", 0))
    print("aria-labels: kept", get("aria-label kept", 0), "| shaped", get("aria-label shaped", 0),
          "| all aria values: vocabulary", get("aria vocabulary", 0),
          "| numbers", get("aria number", 0), "| empty", get("aria empty", 0),
          "| id references shaped", get("aria id reference", 0),
          "| text verbatim", get("aria verbatim-phrase", 0) + get("aria verbatim-template", 0),
          "| text numeric", get("aria numeric", 0), "| text shaped", get("aria shaped", 0))
    print("hrefs: member", get("member hrefs", 0), "| other", get("other hrefs", 0),
          "(the self alias %d)" % get("other hrefs: the self alias", 0),
          "| route words kept", get("other hrefs: route words kept", 0),
          "| segments replaced", get("other hrefs: segments replaced", 0),
          "| placeholder hosts", get("other hrefs: placeholder hosts", 0),
          "| queries dropped", get("other hrefs: queries dropped", 0),
          "| fragments dropped", get("other hrefs: fragments dropped", 0))
    off_grammar = sum(v for k, v in counts.items() if "off-grammar" in k)
    print("attributes dropped", get("attributes dropped", 0),
          "| off-grammar values dropped", off_grammar,
          "| duplicates dropped", get("attributes dropped: duplicates", 0),
          "| bytes", len(text))
    # THE STRUCTURE THIS SKELETON CARRIES, as a digest of tags and nesting
    # only: printed from the capture at build time, and the same from the
    # skeleton, so a test can pin it and a structural hand edit fails there.
    print("structure digest", digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
