"""Turn a captured page into a SKELETON fixture: its structure kept, every word a member wrote replaced.

The provenance of three fixtures under ``tests/fixtures/synthetic/``, one PLAN
each (census rows in brackets):

    engagement   search_appearances_engagement.html   (P S5)
                 the two profile-engagement cards on /analytics/search-appearances/
    recruiter    recruiter_views.html                 (N 195)
                 the Premium recruiter-insights section on /analytics/recruiter-views/
    suggested    compose_suggestions.html             (M M53)
                 the suggested-recipient list on /messaging/compose/

WHAT IS KEPT. The plan's subtree of the capture: every element's TAG and its
NESTING, and a CLOSED set of attributes, each with a closed set of values
(``role``, ``aria-hidden``, ``type``, ``tabindex``, ``aria-selected``,
``data-view-name``). An svg keeps no drawing; the recruiter plan keeps a chart's
labelled points, flattened under their svg, because the points ARE the trend.

WHAT IS REPLACED, EVERY TIME. Each text node, aria-label and alt is matched
against the plan's rules, in order, with the whole value (whitespace folded):

    a rule marked KEEP        -> the value verbatim. KEEP rules match interface
                                 text only: LinkedIn's own words, never a
                                 member's -- "Status is reachable", "Recruiter
                                 views", "Someone recently clicked on your Intro".
    a rule with a replacement -> the replacement, from the plan's own synthetic
                                 values (declared synthetic people, the fixtures'
                                 invented employers, invented numbers).
    no rule                   -> "Example text" / "Example label", and COUNTED.
                                 The count is printed: a skeleton with a
                                 nonzero count drew something no rule named.

Every href is rebuilt from its route words, a company id becomes a synthetic
one, the query and fragment are dropped. ``id``, ``class``, ``style``, ``src``,
``data-*`` outside the closed set, and every other attribute are DROPPED.

THE STRUCTURE DIGEST. Printed per plan from the CAPTURE's kept subtree, and
computed by the tests over the FIXTURE: tags and nesting only (and an svg's
labelled-point count), so a hand edit of the fixture's structure fails there.

IT PRINTS COUNTS ONLY -- never a name, a headline, an employer, an id or any
text the capture holds -- and it writes no file but the fixture. The captures
are gitignored and are never committed: they hold real people.

    python scripts/_build_capture_skeleton.py --plan <name> --capture <path>
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlsplit
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _build_people_search_skeleton import (  # noqa: E402
    SYNTHETIC_PEOPLE,
    VOID,
    Node,
    Tree,
    walk,
)

REPO = Path(__file__).resolve().parent.parent
SYNTHETIC_DIR = REPO / "tests" / "fixtures" / "synthetic"

KEEP = object()
PLACEHOLDER_TEXT = "Example text"
PLACEHOLDER_LABEL = "Example label"
DROP_SUBTREE = {"script", "style", "template", "noscript", "code", "defs", "g",
                "path", "image", "desc", "title"}

#: Route words kept verbatim in any href; every other segment is replaced.
ROUTE_WORDS = frozenset({"analytics", "profile-views", "recruiter-views",
                         "search-appearances", "company", "insights", "in",
                         "messaging", "compose", "thread", "jobs", "premium"})

#: The attributes kept, each with the CLOSED set of values it may keep.
KEPT_ATTRIBUTES: dict[str, frozenset] = {
    "role": frozenset({"list", "listitem", "img", "presentation", "none",
                       "button", "link", "heading", "region", "main",
                       "listbox", "option", "alert", "navigation", "dialog"}),
    "aria-hidden": frozenset({"true", "false"}),
    "aria-selected": frozenset({"true", "false"}),
    "type": frozenset({"button", "submit", "square"}),
    "tabindex": frozenset({"0", "-1"}),
    "data-view-name": frozenset({"messaging-type-ahead-card", "line-chart"}),
}

_DIGEST_LETTERS = str.maketrans("0123456789abcdef", "abcdefghijklmnop")


def fold(value: Optional[str]) -> str:
    return " ".join((value or "").split())


def attr(node: Node, name: str) -> Optional[str]:
    for key, value in node.attrs:
        if key == name:
            return value
    return None


def text_nodes(node: Node):
    return [n for n in walk(node) if n.tag == "#text"]


def ancestors(node: Node):
    walker = node.parent
    while walker is not None:
        yield walker
        walker = walker.parent


def labelled_paths(svg: Node) -> list[Node]:
    return [n for n in walk(svg) if n.tag == "path" and attr(n, "aria-label")]


def structure(node: Node, keep_points: bool, depth: int = 0, out=None) -> list[str]:
    """The kept STRUCTURE, exactly as :meth:`Builder.emit` writes it: each
    element's tag at its depth, a text node as a mark, and an svg as its
    labelled-point count when the plan keeps points. No attribute, no text."""
    if out is None:
        out = []
    if node.tag == "#text":
        out.append(f"{depth}:#text")
        return out
    if node.tag in DROP_SUBTREE:
        return out
    if node.tag == "svg":
        points = len(labelled_paths(node)) if keep_points else 0
        out.append(f"{depth}:svg[{points}]")
        return out
    out.append(f"{depth}:{node.tag}")
    if node.tag in VOID:
        return out
    for child in node.children:
        structure(child, keep_points, depth + 1, out)
    return out


def structure_digest(roots: list[Node], keep_points: bool) -> str:
    lines: list[str] = []
    for index, root in enumerate(roots):
        lines.append(f"root {index}")
        lines.extend(structure(root, keep_points))
    digest = hashlib.sha256("\n".join(lines).encode("ascii")).hexdigest()[:16]
    return digest.translate(_DIGEST_LETTERS)


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------

Rule = tuple  # (compiled pattern, KEEP | str | Callable[[re.Match, "Builder", Node], str])


@dataclass
class Plan:
    name: str
    out: str
    title: str
    note: str
    select: Callable[[Node], list[Node]]
    text_rules: tuple
    label_rules: tuple
    keep_points: bool = False
    #: li[role=option] children to keep, by index; None keeps every child.
    keep_options: Optional[tuple[int, ...]] = None
    #: Company ids from ``tests/test_no_committed_identity.SYNTHETIC_IDS``, the
    #: declared invented ones, so the identity guard reads them as synthetic.
    company_ids: tuple[str, ...] = ("5417062", "610427", "902611")
    sequences: dict = field(default_factory=dict)


def _r(pattern: str) -> re.Pattern:
    return re.compile(pattern)


def seq(name: str) -> Callable:
    """A replacement that hands out the plan's named synthetic values in order."""
    def pick(match, builder, node):
        return builder.next_value(name)
    return pick


def inside(tag: str, then: Callable) -> Callable:
    """A replacement that applies only to a text node inside ``tag``."""
    def pick(match, builder, node):
        if any(a.tag == tag for a in ancestors(node)):
            return then(match, builder, node)
        return None
    return pick


# -- engagement (P S5) -------------------------------------------------------

_IMPRESSIONS = r"You have [0-9][0-9,]* impressions? on your experience at .+"
_CLICKED = r"Someone recently clicked on your (?:Intro|About|Experience|Education|Skills)"


def _select_engagement(root: Node) -> list[Node]:
    for node in walk(root):
        if node.tag == "#text" and re.fullmatch(_IMPRESSIONS, fold(node.text)):
            ul = next((a for a in ancestors(node) if a.tag == "ul"), None)
            if ul is not None and any(re.search(r"recently clicked on your", fold(t.text))
                                      for t in text_nodes(ul)):
                return [ul]
    sys.exit("refused: no list holds both engagement cards")


ENGAGEMENT = Plan(
    name="engagement",
    out="search_appearances_engagement.html",
    title="Profile engagement cards (synthetic skeleton)",
    note=("The two profile-engagement cards the search-appearances page draws: "
          "impressions on one experience entry, and a recent click on a profile "
          "section. The employer is an invented one; the number is invented."),
    select=_select_engagement,
    text_rules=(
        (_r(_IMPRESSIONS), "You have 7 impressions on your experience at Umbrella Systems"),
        (_r(_CLICKED), KEEP),
        (_r(r"View"), KEEP),
    ),
    label_rules=(
        (_r(r"View"), KEEP),
        (_r(r""), KEEP),
    ),
)


# -- recruiter (N 195) -------------------------------------------------------

_POINT = re.compile(r"x, ([0-9]{10,13}), ([0-9]+)\. Views over time\.")
#: Invented weekly series, one per chart, thirteen points each: a Monday at
#: midnight UTC in June 2026 and then every seven days.
_WEEK_MS = 7 * 24 * 3600 * 1000
_SERIES_START_MS = 1780272000000
_SERIES = ((3, 5, 2, 6, 4, 7, 3, 2, 5, 8, 4, 3, 6),
           (0, 1, 0, 0, 2, 0, 1, 0, 0, 1, 0, 0, 1))


def _select_recruiter(root: Node) -> list[Node]:
    for node in walk(root):
        if node.tag == "section" and attr(node, "aria-label") is not None:
            if any(fold(t.text) == "Recruiter views" for t in text_nodes(node)):
                return [node]
    sys.exit("refused: no labelled section holds 'Recruiter views'")


def _point(match, builder, node):
    chart, index = builder.point_position(node)
    return (f"x, {_SERIES_START_MS + index * _WEEK_MS}, "
            f"{_SERIES[chart % len(_SERIES)][index % 13]}. Views over time.")


def _in_viewer_card(node: Node) -> bool:
    return any(a.tag == "a" and re.match(r"^(https://www\.linkedin\.com)?/company/[^/]+/insights/?",
                                         attr(a, "href") or "") for a in ancestors(node))


def _industry(match, builder, node):
    if _in_viewer_card(node):
        return builder.next_value("industry")
    return None


RECRUITER = Plan(
    name="recruiter",
    out="recruiter_views.html",
    title="Recruiter insights (synthetic skeleton)",
    note=("The Premium recruiter-insights section: the profile-views and "
          "recruiter-views counts with their time range, each trend chart with "
          "its thirteen labelled points, and the recruiter viewers, each drawn "
          "as an employer, an industry and a time with no member link. The "
          "employers, the industries, the counts, the series and the times are "
          "invented."),
    select=_select_recruiter,
    keep_points=True,
    text_rules=(
        (_r(r"Recruiter insights|Profile views|Recruiter views|Past [0-9]+ days|Chart"
            r"|Line chart with [0-9]+ data points\.?|End of interactive chart\.?"
            r"|View insights"), KEEP),
        (_r(r"[0-9][0-9,]*"), seq("count")),
        (_r(r"Recruiter at .+"), seq("viewer")),
        (_r(r"Viewed \S+ ago"), seq("viewed")),
        (_r(r".+"), _industry),
    ),
    label_rules=(
        (_r(r"Premium"), KEEP),
        (_r(r"Chart\. Highcharts interactive chart\.|Interactive chart"), KEEP),
        (_POINT, _point),
    ),
    sequences={
        "count": ("41", "3"),
        "viewer": ("Recruiter at Northgate Analytics", "Recruiter at Umbrella Systems"),
        "industry": ("Staffing and Recruiting", "Software Development"),
        "viewed": ("Viewed 2w ago", "Viewed 5d ago"),
    },
)


# -- suggested (M M53) --------------------------------------------------------

_CARD = "messaging-type-ahead-card"
_PERSON_NAMES = tuple(name for name, _slug in SYNTHETIC_PEOPLE)
_SUGGESTED_HEADLINES = (
    "Engineering Manager at Umbrella Systems",
    "Principal Engineer at Umbrella Systems | Distributed Systems",
    "Staff Software Engineer | Payments | Example Labs",
    "Talent Acquisition Lead at Northgate Analytics",
)


def _is_listbox(node: Node) -> bool:
    return node.tag == "ul" and attr(node, "role") == "listbox"


def _select_suggested(root: Node) -> list[Node]:
    """The listbox's PARENT, so the fixture keeps the container whose
    aria-hidden says whether the list is shown."""
    for node in walk(root):
        if _is_listbox(node) and any(attr(n, "data-view-name") == _CARD for n in walk(node)):
            return [node.parent]
    sys.exit("refused: no listbox holds a suggested-recipient card")


def _card_of(node: Node) -> Optional[Node]:
    return next((a for a in ancestors(node) if attr(a, "data-view-name") == _CARD), None)


def _card_name(match, builder, node):
    return builder.name_for(_card_of(node))


def _card_alt(match, builder, node):
    return "Suggested: Photo of " + builder.name_for(_card_of(node))


SUGGESTED = Plan(
    name="suggested",
    out="compose_suggestions.html",
    title="Suggested recipients on the composer (synthetic skeleton)",
    note=("The composer's suggested-recipient list: each person a card with a "
          "photo, a name, a headline and a presence line, and one group "
          "conversation drawn with a facepile and no presence. Every person is "
          "from the declared synthetic tables; the group's name and the "
          "headlines are invented."),
    select=_select_suggested,
    keep_options=(0, 3, 4, 7),
    text_rules=(
        (_r(r"Status is (?:reachable|offline|online)"), KEEP),
        (_r(r"Suggested: Photo of|Suggested"), KEEP),
        (_r(r"Group Message \W [0-9]+ participants"), "Group Message \u00b7 3 participants"),
        (_r(r".+"), inside("dt", _card_name)),
        (_r(r".+"), inside("dd", seq("headline"))),
    ),
    label_rules=(
        (_r(r"Suggested: Photo of .+"), _card_alt),
        (_r(r""), KEEP),
    ),
    sequences={"headline": _SUGGESTED_HEADLINES},
)

PLANS = {plan.name: plan for plan in (ENGAGEMENT, RECRUITER, SUGGESTED)}


# ---------------------------------------------------------------------------
# The builder
# ---------------------------------------------------------------------------

class Builder:
    def __init__(self, plan: Plan):
        self.plan = plan
        self.unclassified_text = 0
        self.unclassified_labels = 0
        self.dropped_values = 0
        self.kept_options = 0
        self.company_map: dict[str, str] = {}
        self.names: dict[int, str] = {}
        self.cursor: dict[str, int] = {}
        self.charts: list[Node] = []

    # -- synthetic values ------------------------------------------------
    def next_value(self, name: str) -> str:
        values = self.plan.sequences[name]
        index = self.cursor.get(name, 0)
        if index >= len(values):
            sys.exit(f"refused: plan {self.plan.name} ran out of synthetic '{name}' values")
        self.cursor[name] = index + 1
        return values[index]

    def name_for(self, card: Optional[Node]) -> str:
        key = id(card)
        if key not in self.names:
            is_group = card is not None and sum(1 for n in walk(card) if n.tag == "img") > 1
            if is_group:
                self.names[key] = "Example Group"
            else:
                used = sum(1 for v in self.names.values() if v != "Example Group")
                if used >= len(_PERSON_NAMES):
                    sys.exit("refused: more suggested people than declared synthetic ones")
                self.names[key] = _PERSON_NAMES[used]
        return self.names[key]

    def point_position(self, path: Node) -> tuple[int, int]:
        svg = next(a for a in ancestors(path) if a.tag == "svg")
        if svg not in self.charts:
            self.charts.append(svg)
        return self.charts.index(svg), labelled_paths(svg).index(path)

    # -- rules -----------------------------------------------------------
    def apply(self, rules, value: str, node: Node) -> Optional[str]:
        for pattern, action in rules:
            match = pattern.fullmatch(value)
            if not match:
                continue
            if action is KEEP:
                return value
            if isinstance(action, str):
                return action
            out = action(match, self, node)
            if out is not None:
                return out
        return None

    def text(self, node: Node) -> str:
        out = self.apply(self.plan.text_rules, fold(node.text), node)
        if out is None:
            self.unclassified_text += 1
            return PLACEHOLDER_TEXT
        return out

    def label(self, value: str, node: Node) -> str:
        out = self.apply(self.plan.label_rules, fold(value), node)
        if out is None:
            self.unclassified_labels += 1
            return PLACEHOLDER_LABEL
        return out

    def href(self, value: str) -> str:
        parts = urlsplit((value or "").strip())
        host = parts.netloc.lower()
        base = "https://www.linkedin.com" if host else ""
        segments = [s for s in parts.path.split("/") if s]
        out = []
        for index, segment in enumerate(segments):
            if segment in ROUTE_WORDS:
                out.append(segment)
            elif index > 0 and segments[index - 1] == "company":
                if segment not in self.company_map:
                    ids = self.plan.company_ids
                    self.company_map[segment] = ids[len(self.company_map) % len(ids)]
                out.append(self.company_map[segment])
            else:
                out.append("example")
        return base + "/" + "/".join(out) + ("/" if out else "")

    def attributes(self, node: Node) -> list[tuple[str, str]]:
        out = []
        for name, value in node.attrs:
            value = value or ""
            if name == "href" and node.tag == "a":
                out.append(("href", self.href(value)))
            elif name in ("aria-label", "alt") and node.tag != "path":
                out.append((name, self.label(value, node)))
            elif name in KEPT_ATTRIBUTES:
                if value in KEPT_ATTRIBUTES[name]:
                    out.append((name, value))
                else:
                    self.dropped_values += 1
        return out

    # -- emission ----------------------------------------------------------
    def emit(self, node: Node, out: list[str]) -> None:
        if node.tag == "#text":
            out.append(escape(self.text(node)))
            return
        if node.tag in DROP_SUBTREE:
            return
        attrs = self.attributes(node)
        rendered = "".join(f" {name}={quoteattr(value)}" for name, value in attrs)
        if node.tag == "svg":
            out.append(f"<svg{rendered}>")
            if self.plan.keep_points:
                for path in labelled_paths(node):
                    label = self.label(attr(path, "aria-label") or "", path)
                    role = attr(path, "role")
                    role_attr = f' role="{role}"' if role in KEPT_ATTRIBUTES["role"] else ""
                    out.append(f"<path{role_attr} aria-label={quoteattr(label)} />")
            out.append("</svg>")
            return
        if node.tag in VOID:
            out.append(f"<{node.tag}{rendered} />")
            return
        out.append(f"<{node.tag}{rendered}>")
        for child in kept_children(node, self.plan):
            if self.plan.keep_options is not None and _is_listbox(node):
                self.kept_options += 1
            self.emit(child, out)
        out.append(f"</{node.tag}>")


def kept_children(node: Node, plan: Plan) -> list[Node]:
    """A listbox keeps only the options the plan names, BY POSITION among its
    element children (each child one wrapped option); every other node keeps
    every child."""
    if plan.keep_options is None or not _is_listbox(node):
        return list(node.children)
    elements = [c for c in node.children if c.tag != "#text"]
    return [c for c in elements if elements.index(c) in plan.keep_options]


def pruned(root: Node, plan: Plan) -> Node:
    """The capture's subtree with the options the plan drops removed, so the
    capture-side digest describes exactly the structure the fixture keeps."""
    if plan.keep_options is None:
        return root
    copy = Node(root.tag, root.attrs, None, root.text)
    for child in kept_children(root, plan):
        kept = pruned(child, plan)
        kept.parent = copy
        copy.children.append(kept)
    return copy


HEADER = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head><meta charset="utf-8" /><title>{title}</title></head>
<body>
<!-- SYNTHETIC SKELETON, NOT A CAPTURE. {note} The STRUCTURE is a live page's,
     kept by scripts/_build_capture_skeleton.py (plan "{plan}"), which says
     what was kept and what was replaced. Well-formed XHTML; text not indented. -->
<main>
"""
FOOTER = """</main>
</body>
</html>
"""


def build(plan: Plan, capture: Path, out: Path) -> dict[str, object]:
    tree = Tree()
    tree.feed(capture.read_bytes().decode("utf-8", errors="replace"))
    roots = plan.select(tree.root)
    builder = Builder(plan)
    body: list[str] = []
    for root in roots:
        builder.emit(root, body)
        body.append("\n")
    text = HEADER.format(title=plan.title, note=plan.note, plan=plan.name) + "".join(body) + FOOTER
    text = text.encode("ascii", "xmlcharrefreplace").decode("ascii")
    out.write_text(text, encoding="ascii", newline="\n")
    return {
        "roots": len(roots),
        "unclassified text nodes": builder.unclassified_text,
        "unclassified labels": builder.unclassified_labels,
        "attribute values dropped": builder.dropped_values,
        "options kept": builder.kept_options,
        "charts": len(builder.charts),
        "bytes": len(text),
        "structure digest": structure_digest([pruned(r, plan) for r in roots], plan.keep_points),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", required=True, choices=sorted(PLANS))
    parser.add_argument("--capture", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)
    plan = PLANS[args.plan]
    out = Path(args.out) if args.out else SYNTHETIC_DIR / plan.out
    report = build(plan, Path(args.capture), out)
    print(" | ".join(f"{key} {value}" for key, value in report.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
