"""Build LinkedIn's AI job search into a committed fixture: the structure kept, every value replaced.

Kept as the PROVENANCE of ``tests/fixtures/jobs_search_ai.html``, the fixture
``linkedin_server.job_search_route`` reads (lane search-fix26, 2026-11-26).

THE INPUT is live session 11's RAW capture of ``/jobs/search-results/?keywords=``
(2026-11-26, relation SERVED, 25 result cards), kept gitignored in the main
checkout under ``_state/preserved/live11-2026-11-25/jobs_search_keywords.html``.
It is read and never written anywhere; nothing here prints a value it read.

WHAT IS KEPT, AND IT IS A WHITELIST, NOT A SCRUB. A scrub removes what it knows
is identifying and keeps the rest; this keeps what it knows is NOT and
replaces the rest, so a value nobody thought of cannot survive by default:

* every ELEMENT and its nesting -- the structure the reader binds to -- except
  undrawn ones (script, style, template, noscript, code, link, meta, iframe)
  and the contents of ``svg``;
* attribute VALUES only from LinkedIn's code vocabulary, each validated by
  shape: ``role``, ``type``, ``tabindex``, the ``aria-*`` states, ``checked``,
  ``data-display-contents``, ``data-testid`` and ``data-sdui-screen``;
* ``componentkey`` from a closed list of LinkedIn's own component names, or
  rewritten: a card's ``job-card-component-ref-<id>`` takes a SYNTHETIC id of
  the same ten-digit shape (the same id for the card's inner copy and for the
  page's ``currentJobId`` links), the alert toggle's key loses the query words
  and digit runs it carries, and every other key becomes ``k<n>``;
* ``id`` and ``for`` as ``id<n>``, one per distinct value, so every label still
  names its control;
* ``href`` as a bare LinkedIn path from a closed list, the search-results
  link with synthetic values, or ``#``; ``alt`` as empty;
* ``aria-label`` only when it is one of LinkedIn's filter names, or the
  ``Filter by <chip>`` / ``Dismiss <title> job`` grammar rewritten round a
  neutral value, otherwise ``x``;
* TEXT only when it is a LinkedIn UI word from :data:`UI_WORDS` (equality), or
  matches one of the closed grammars in :data:`GRAMMARS` (a time-ago, a posted
  line, a results total, an alumni count). A card's title, company and place
  become ``Role Title NN``, ``Company NN`` and ``Place NN`` -- the place keeps
  its ``(Remote)`` / ``(Hybrid)`` / ``(On-site)`` word, which is LinkedIn's
  vocabulary -- and the title's plain-span twin becomes ``Accessible Copy NN``,
  a NEEDLE: a reader that took the twin instead of the visible copy returns it.
  Every other text is ``x``.

AND IT CHECKS ITSELF, IN BOTH DIRECTIONS, BEFORE WRITING. :func:`verify` parses
the output and refuses unless EVERY text and EVERY attribute value is one of
the declared forms above -- a positive check, so a value nobody listed cannot
pass it. Then every input text of six characters or more that the vocabulary
does not keep is searched for in the output's texts, and one found refuses.
The output must be ASCII (the middle dot is written as an entity) and must
hold exactly the input's card count. ``tests/test_job_search_route.py`` runs
:func:`verify` over the committed fixture and shows it refusing a planted name.

    python scripts/_build_ai_job_search_skeleton.py --raw <raw capture> [--out <path>]

Prints counts and a sha256 digest of what it wrote, never a value it read.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qsl, urlsplit

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO / "tests" / "fixtures" / "jobs_search_ai.html"

#: Elements a browser does not draw, dropped whole.
DROPPED = frozenset({"script", "style", "template", "noscript", "code", "link",
                     "meta", "iframe", "head", "title", "base"})
VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                  "link", "meta", "param", "source", "track", "wbr"})

#: LinkedIn's UI words on this page, kept by EQUALITY. Every one is LinkedIn's
#: own label for a control, a chip or a state, and none is a value a person or
#: an employer chose. Measured on the capture by lane search26 (raw equality
#: and session 11's keyed shapes agreeing) or by this lane's anchor probe.
UI_WORDS = frozenset({
    "Easy Apply", "Actively reviewing applicants", "Be an early applicant",
    "Get job alerts for this search", "Jobs", "Date posted", "Company",
    "Workplace type", "Experience level", "Employment type", "In my network",
    "Verified", "All filters", "Next", "Previous", "Promoted", "Viewed",
    "Applied", "Are these results helpful?",
    "Your feedback helps us improve search results.", chr(0xB7),
})

#: Closed grammars, kept by FULL match. Digits here are ages and counts.
GRAMMARS = (
    re.compile(r"\d+ (?:second|minute|hour|day|week|month|year)s? ago"),
    re.compile(r"(?:Posted|Reposted) \d+ (?:second|minute|hour|day|week|month|year)s? ago"),
    re.compile(r"\d+\+? results?"),
    re.compile(r"\d+ (?:school|company) (?:alum|alums|alumni) works? here"),
    re.compile(r"\d+ connections? works? here"),
)

#: LinkedIn's own component names on this page, kept as they are.
COMPONENT_NAMES = frozenset({
    "JobsSearchFilters", "SearchResults_AllFiltersButton",
    "SearchResultsMainContent", "navBarJobTypeaheadComponentRef",
})
CARD_KEY = re.compile(r"^job-card-component-ref-(\d{6,})$")
ALERT_KEY = re.compile(r"^JobSearchAlertToggleRef_")
ALERT_KEY_SYNTHETIC = "JobSearchAlertToggleRef_synthetic_role_00000000_0"

#: The first synthetic posting id, and the ids count up from it.
SYNTHETIC_ID_BASE = 4000000100

#: Attribute -> the shape its value must have to be kept.
KEPT_ATTRS = {
    "role": re.compile(r"[a-z]+"),
    "type": re.compile(r"[a-z]+"),
    "tabindex": re.compile(r"-?\d"),
    "aria-hidden": re.compile(r"true|false"),
    "aria-expanded": re.compile(r"true|false"),
    "aria-current": re.compile(r"[a-z]+"),
    "aria-disabled": re.compile(r"true|false"),
    "aria-live": re.compile(r"[a-z]+"),
    "aria-atomic": re.compile(r"true|false"),
    "aria-haspopup": re.compile(r"[a-z]+"),
    "aria-autocomplete": re.compile(r"[a-z]+"),
    "data-display-contents": re.compile(r"true|false"),
    "data-testid": re.compile(r"[a-z][a-z0-9-]{0,60}"),
    "data-sdui-screen": re.compile(r"com\.linkedin\.sdui\.[A-Za-z.]{1,120}"),
}
#: Boolean attributes kept as bare names.
FLAG_ATTRS = frozenset({"checked"})

#: Bare LinkedIn paths an href may keep (query dropped).
KEPT_PATHS = frozenset({"/jobs/", "/messaging/", "/mynetwork", "/mynetwork/",
                        "/notifications/", "/feed/", "/help/linkedin/"})
SEARCH_RESULTS_PATH = "/jobs/search-results/"

#: LinkedIn's own filter names an ``aria-label`` may keep whole.
KEPT_LABELS = frozenset({
    "Filter by Easy Apply", "Filter by Jobs", "Filter by In my network",
    "Filter by Verified",
})
FILTER_LABEL = re.compile(r"^Filter by (.+)$")
DISMISS_LABEL = re.compile(r"^Dismiss .+ job$")

HEADER = (
    "<!doctype html>\n<!--\n"
    "  LANE SEARCH-FIX26, 2026-11-26: built by\n"
    "  scripts/_build_ai_job_search_skeleton.py from live session 11's raw capture\n"
    "  of LinkedIn's AI job search (/jobs/search-results/?keywords=, 25 cards).\n"
    "  The element structure is LinkedIn's. Every text is a LinkedIn UI word, a\n"
    "  closed time-ago / total / alumni grammar, or a neutral value written by the\n"
    "  builder; every attribute value is LinkedIn code vocabulary or a synthetic\n"
    "  stand-in. Posting ids are synthetic, of the real ten-digit shape.\n"
    "-->\n"
)


class _Node:
    def __init__(self, tag: str, attrs: list, parent: Optional["_Node"]) -> None:
        self.tag, self.attrs, self.parent = tag, attrs, parent
        self.children: list = []


class _Tree(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(_Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        walker = self.cur
        while walker is not None and walker.tag != tag:
            walker = walker.parent
        if walker is not None and walker.parent is not None:
            self.cur = walker.parent

    def handle_data(self, data):
        if data.strip():
            self.cur.children.append(" ".join(data.split()))


def _walk(node):
    yield node
    for child in node.children:
        if isinstance(child, _Node):
            yield from _walk(child)


def _attr(node: _Node, name: str) -> Optional[str]:
    for key, value in node.attrs:
        if key == name:
            return value
    return None


def _has(node: _Node, name: str) -> bool:
    return any(key == name for key, _value in node.attrs)


def _elements(node: _Node) -> list:
    return [c for c in node.children if isinstance(c, _Node)]


def _inside(node: _Node, ancestor: _Node) -> bool:
    up = node.parent
    while up is not None:
        if up is ancestor:
            return True
        up = up.parent
    return False


class Builder:
    """One build. Holds the synthetic maps so every relation survives."""

    def __init__(self) -> None:
        self.job_ids: dict[str, str] = {}
        self.ids: dict[str, str] = {}
        self.keys: dict[str, str] = {}
        self.topics: dict[str, str] = {}
        #: id(text-owner node) -> replacement text, for the card fields.
        self.planted: dict[tuple[int, int], str] = {}
        self.counts = {"cards": 0, "titles": 0, "companies": 0, "places": 0,
                       "twins": 0, "topics": 0, "texts kept": 0, "texts replaced": 0}

    # -- synthetic values -------------------------------------------------
    def job_id(self, real: str) -> str:
        if real not in self.job_ids:
            self.job_ids[real] = str(SYNTHETIC_ID_BASE + len(self.job_ids) + 1)
        return self.job_ids[real]

    def element_id(self, real: str) -> str:
        if real not in self.ids:
            self.ids[real] = "id%d" % (len(self.ids) + 1)
        return self.ids[real]

    def other_key(self, real: str) -> str:
        if real not in self.keys:
            self.keys[real] = "k%d" % (len(self.keys) + 1)
        return self.keys[real]

    def topic(self, real: str) -> str:
        if real not in self.topics:
            self.topics[real] = "Topic %d" % (len(self.topics) + 1)
            self.counts["topics"] += 1
        return self.topics[real]

    # -- the card fields, placed by structure ------------------------------
    def plan_cards(self, root: _Node) -> None:
        keyed = [n for n in _walk(root) if CARD_KEY.match(_attr(n, "componentkey") or "")]
        outer = [n for n in keyed if not any(_inside(n, o) for o in keyed if o is not n)]
        self.counts["cards"] = len(outer)
        for number, card in enumerate(outer, start=1):
            self.job_id(CARD_KEY.match(_attr(card, "componentkey")).group(1))
            displays = [n for n in _walk(card) if _has(n, "data-display-contents")]
            if len(displays) != 1:
                raise SystemExit("a card without exactly one title wrapper; refusing to guess")
            display = displays[0]
            for p in [n for n in _walk(display) if n.tag == "p"]:
                for span in _elements(p):
                    if span.tag != "span":
                        continue
                    hidden = (_attr(span, "aria-hidden") or "") == "true"
                    value = ("Role Title %02d" if hidden else "Accessible Copy %02d") % number
                    if self._plant_first_text(span, value):
                        self.counts["titles" if hidden else "twins"] += 1
            stack = display.parent
            for child in _elements(stack):
                if child is display:
                    continue
                if child.tag == "div":
                    for p in [n for n in _walk(child) if n.tag == "p"]:
                        if self._plant_first_text(p, "Company %02d" % number):
                            self.counts["companies"] += 1
                elif child.tag == "p":
                    real = " ".join(t for t in child.children if isinstance(t, str))
                    found = re.search(r"\((Remote|Hybrid|On-site)\)", real)
                    value = "Place %02d" % number + (" (%s)" % found.group(1) if found else "")
                    if self._plant_first_text(child, value):
                        self.counts["places"] += 1

    def _plant_first_text(self, node: _Node, value: str) -> bool:
        """Replace the first text under ``node`` with ``value``; blank the rest."""
        planted = False
        for owner in _walk(node):
            for index, child in enumerate(owner.children):
                if isinstance(child, str):
                    self.planted[(id(owner), index)] = "" if planted else value
                    planted = True
        return planted

    # -- the transform ------------------------------------------------------
    def text(self, owner: _Node, index: int, value: str) -> str:
        key = (id(owner), index)
        if key in self.planted:
            return self.planted[key]
        if value in UI_WORDS or any(g.fullmatch(value) for g in GRAMMARS):
            self.counts["texts kept"] += 1
            return value
        if value in self.topics:
            return self.topics[value]
        self.counts["texts replaced"] += 1
        return "x"

    def attrs(self, node: _Node) -> list[tuple[str, Optional[str]]]:
        out: list[tuple[str, Optional[str]]] = []
        for name, value in node.attrs:
            text = value or ""
            if name in KEPT_ATTRS:
                if KEPT_ATTRS[name].fullmatch(text):
                    out.append((name, text))
            elif name in FLAG_ATTRS:
                out.append((name, None))
            elif name == "componentkey":
                card = CARD_KEY.match(text)
                if card:
                    out.append((name, "job-card-component-ref-" + self.job_id(card.group(1))))
                elif ALERT_KEY.match(text):
                    out.append((name, ALERT_KEY_SYNTHETIC))
                elif text in COMPONENT_NAMES:
                    out.append((name, text))
                else:
                    out.append((name, self.other_key(text)))
            elif name in ("id", "for"):
                out.append((name, self.element_id(text)))
            elif name == "href":
                out.append((name, self.href(text)))
            elif name == "alt":
                out.append((name, ""))
            elif name == "aria-label":
                out.append((name, self.label(text)))
        return out

    def href(self, value: str) -> str:
        try:
            parts = urlsplit(value)
        except ValueError:
            return "#"
        if (parts.netloc or "www.linkedin.com") not in ("www.linkedin.com", "linkedin.com"):
            return "#"
        if parts.path == SEARCH_RESULTS_PATH:
            pairs = parse_qsl(parts.query)
            keep = []
            for key, val in pairs:
                if key == "currentJobId" and val in self.job_ids:
                    keep.append("currentJobId=" + self.job_ids[val])
                elif key == "keywords":
                    keep.append("keywords=synthetic+role")
            return "https://www.linkedin.com" + SEARCH_RESULTS_PATH + ("?" + "&".join(keep) if keep else "")
        if parts.path in KEPT_PATHS:
            return "https://www.linkedin.com" + parts.path
        return "#"

    def label(self, value: str) -> str:
        if value in KEPT_LABELS:
            return value
        if DISMISS_LABEL.match(value):
            return "Dismiss x job"
        chip = FILTER_LABEL.match(value)
        if chip:
            if chip.group(1) in UI_WORDS:
                return value
            return "Filter by " + self.topic(chip.group(1))
        return "x"

    def render(self, node: _Node, out: list[str], depth: int = 0) -> None:
        for index, child in enumerate(node.children):
            if isinstance(child, str):
                text = self.text(node, index, child)
                if text:
                    out.append(escape(text, quote=False))
                continue
            if child.tag in DROPPED:
                continue
            attrs = "".join(
                " %s" % name if value is None else ' %s="%s"' % (name, escape(value, quote=True))
                for name, value in self.attrs(child)
            )
            if child.tag == "svg":
                out.append("<svg%s></svg>" % attrs)
                continue
            if child.tag in VOID:
                out.append("<%s%s>" % (child.tag, attrs))
                continue
            out.append("<%s%s>" % (child.tag, attrs))
            self.render(child, out, depth + 1)
            out.append("</%s>" % child.tag)


#: The neutral values this builder writes, and nothing else it writes as text.
NEUTRAL_TEXT = re.compile(
    r"(?:Role Title|Accessible Copy|Company|Place) \d{2}"
    r"(?: \((?:Remote|Hybrid|On-site)\))?|Topic \d+|x"
)
SYNTHETIC_CARD_KEY = re.compile(r"job-card-component-ref-40000001\d\d")
SYNTHETIC_SEARCH_HREF = re.compile(
    r"https://www\.linkedin\.com/jobs/search-results/"
    r"(?:\?(?:currentJobId=40000001\d\d)?&?(?:keywords=synthetic\+role)?)?"
)


def _allowed_attr(name: str, value: Optional[str]) -> bool:
    """Is one OUTPUT attribute inside the closed alphabet this builder writes?"""
    text = value or ""
    if name in KEPT_ATTRS:
        return bool(KEPT_ATTRS[name].fullmatch(text))
    if name in FLAG_ATTRS:
        return value is None or text == ""
    if name == "componentkey":
        return bool(
            SYNTHETIC_CARD_KEY.fullmatch(text)
            or text == ALERT_KEY_SYNTHETIC
            or text in COMPONENT_NAMES
            or re.fullmatch(r"k\d+", text)
        )
    if name in ("id", "for"):
        return bool(re.fullmatch(r"id\d+", text))
    if name == "href":
        return (
            text == "#"
            or text in {"https://www.linkedin.com" + path for path in KEPT_PATHS}
            or bool(SYNTHETIC_SEARCH_HREF.fullmatch(text))
        )
    if name == "alt":
        return text == ""
    if name == "aria-label":
        return (
            text in KEPT_LABELS
            or text in {"Filter by " + word for word in UI_WORDS}
            or text in ("x", "Dismiss x job")
            or bool(re.fullmatch(r"Filter by Topic \d+", text))
        )
    if name == "charset":
        return text == "utf-8"
    return False


def verify(text: str) -> dict[str, int]:
    """Refuse unless EVERY text and attribute value written is in the closed alphabet.

    A POSITIVE check of the output, not a search for known-bad input: a value
    nobody listed cannot pass it, because passing means being one of the
    declared forms. Returns the counts it checked.
    """
    tree = _Tree()
    tree.feed(text)
    tree.close()
    texts = attrs = 0
    for node in _walk(tree.root):
        for child in node.children:
            if isinstance(child, str):
                texts += 1
                if not (child in UI_WORDS or any(g.fullmatch(child) for g in GRAMMARS)
                        or NEUTRAL_TEXT.fullmatch(child)):
                    raise SystemExit("an output text is outside the closed alphabet; refusing")
        for name, value in node.attrs:
            attrs += 1
            if not _allowed_attr(name, value):
                raise SystemExit("an output %s value is outside the closed alphabet; refusing" % name)
    return {"output texts checked": texts, "output attributes checked": attrs}


def _input_texts(root: _Node) -> set[str]:
    """Input texts of six characters or more that the vocabulary does not keep."""
    found: set[str] = set()
    for node in _walk(root):
        if node.tag in DROPPED:
            continue
        for child in node.children:
            if isinstance(child, str) and len(child) >= 6:
                if child not in UI_WORDS and not any(g.fullmatch(child) for g in GRAMMARS):
                    found.add(child)
    return found


def build(raw: str) -> tuple[str, dict[str, int]]:
    tree = _Tree()
    tree.feed(raw)
    tree.close()
    builder = Builder()
    builder.plan_cards(tree.root)
    if builder.counts["cards"] == 0:
        raise SystemExit("no AI job-search card in the input; this builder reads one page only")
    # The topic chips are named by their own toggles' labels, so read those first.
    for node in _walk(tree.root):
        label = _attr(node, "aria-label") or ""
        chip = FILTER_LABEL.match(label)
        if node.tag == "input" and chip and chip.group(1) not in UI_WORDS:
            builder.topic(chip.group(1))
    bodies = [n for n in _walk(tree.root) if n.tag == "body"]
    if len(bodies) != 1:
        raise SystemExit("the input does not hold exactly one body")
    out: list[str] = ["<html>", "<head><meta charset=\"utf-8\"><title>x</title></head>", "<body>"]
    builder.render(bodies[0], out, 1)
    out += ["</body>", "</html>"]
    text = HEADER + "\n".join(out) + "\n"

    if any(ord(ch) > 127 for ch in text.replace(chr(0xB7), "")):
        # The middle dot is LinkedIn's separator and the one non-ASCII UI word;
        # it is written as an entity below so the file itself stays ASCII.
        raise SystemExit("a non-ASCII character survived outside the separator; refusing")
    text = text.replace(chr(0xB7), "&middot;")

    checked = verify(text)

    # AND THE NEGATIVE HALF, over the output's own texts: no input text of six
    # characters or more that the vocabulary does not keep is in any of them.
    check = _Tree()
    check.feed(text)
    check.close()
    written_texts = "\n".join(
        child for node in _walk(check.root) for child in node.children if isinstance(child, str)
    )
    inputs = _input_texts(tree.root)
    if any(value in written_texts for value in inputs):
        raise SystemExit("an input text survived into the output; refusing to write")

    written = [n for n in _walk(check.root) if CARD_KEY.match(_attr(n, "componentkey") or "")]
    outer = [n for n in written if not any(_inside(n, o) for o in written if o is not n)]
    if len(outer) != builder.counts["cards"]:
        raise SystemExit("the output holds a different card count from the input; refusing")
    counts = dict(builder.counts)
    counts.update(checked)
    counts["synthetic ids"] = len(builder.job_ids)
    counts["input texts searched for"] = len(inputs)
    return text, counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    raw = args.raw.read_text(encoding="utf-8")
    text, counts = build(raw)
    args.out.write_text(text, encoding="ascii", newline="\n")
    for name in sorted(counts):
        print("%-22s %d" % (name, counts[name]))
    print("bytes %d" % len(text))
    print("sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest()[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
