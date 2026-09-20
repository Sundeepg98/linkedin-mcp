"""The frame of two analytics surfaces, and the profile-views scope defect,
read OFFLINE from captures nobody has re-opened since they were taken.

NOBODY HAS EVER OPENED /analytics/recruiter-views or
/premium/profile-key-skills. There is no capture of either. The only honest
basis for a fixture is the DOM shape of a SIBLING surface that HAS been
captured: cap-profile-views.html and cap-search-appearances.html stand in for
the two, and cap-premium-hub.html stands in a second time for the Premium
route inventory in part 4.

## THE REDUCER IS IMPORTED, NOT REWRITTEN

``shape_path()`` and ``visible_text()`` come from
``_probe_premium_surfaces_shape`` unchanged. That file's docstring records
that its first version LEAKED a real profile slug, because it replaced a path
segment only when the segment was long or digit-bearing, and a slug is
neither -- the working rule replaces the segment AFTER a member-bearing
prefix UNCONDITIONALLY. Writing a second reducer here would risk the same
leak a second time for no reason; this file has exactly one path-shaping
function and it is somebody else's, proven.

## THE ROW-FINDING ALGORITHM IS ALSO IMPORTED, IN SPIRIT

``linkedin_server/dom.py``'s ``HARVEST_LINKED_CARDS_JS`` already runs this walk
against a LIVE DOM: climb from a matching anchor to the LARGEST ancestor that
still speaks for exactly one target, stopping at a container (more than one
distinct target underneath), at an LI/ARTICLE, or at an element already
carrying ``data-view-name``. ``row_of()`` below is that same three-stop rule,
ported to the parsed tree because there is no live page here to call
``page.evaluate`` against -- only a saved capture. ``max_hops=8`` is that
module's own default for ``harvest_linked_cards``, carried over rather than
re-guessed.

That module's docstring also records the fact that makes part 3 below
necessary rather than decorative: LinkedIn draws privacy-limited viewers
("Someone at Acme") with NO link at all, so a harvest anchored only on
anchors under-counts the row list. Six of ten were invisible this way when it
was live-measured. So "rows" and "rows with a member anchor" are counted as
TWO different numbers throughout this file, never conflated into one.

## WHAT LEAVES THIS PROCESS

Integers, booleans, tag names, attribute NAMES, landmark labels, and route
shapes already redacted by the imported ``shape_path()``. No href verbatim,
no accessible name, no person's name, no employer, no campus, no aria-label
VALUE. Where a value must be inspected to make a decision (is there a digit
in this aria-label; is this class repeated on a sibling), the script reads it
in memory and prints only the count or the boolean, never the value. If ever
unsure whether a string names a person, this file prints its length, not the
string.

## THE CAPTURES ARE GITIGNORED AND THEIR ABSENCE IS NOT A ZERO

``_state/`` carries no files in a linked worktree. A run that cannot find a
capture it needs exits 2 for that capture's sections and tallies nothing for
them; it does not report a zero standing in for "did not look."

Run it as::

    ../../../venv/Scripts/python.exe scripts/_probe_analytics_list_shape.py
    ../../../venv/Scripts/python.exe scripts/_probe_analytics_list_shape.py --control
    ../../../venv/Scripts/python.exe scripts/_probe_analytics_list_shape.py --break-demo
"""

from __future__ import annotations

import argparse
import hashlib
import re
import statistics
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _probe_premium_surfaces_shape import shape_path, visible_text  # noqa: E402

# The main checkout's _state/, reached from a worktree at
# <linkedin>/.claude/worktrees/<agent>/. Overridable; this default is a
# convenience, never load-bearing for correctness.
DEFAULT_STATE = ROOT.parent.parent.parent / "_state"

CAPTURES = {
    "profile-views": "cap-profile-views.html",
    "search-appearances": "cap-search-appearances.html",
    "premium-hub": "cap-premium-hub.html",
}

VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})

STRIP_TAGS = frozenset({"script", "style", "code", "template", "noscript"})

HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")

LANDMARK_TAGS = frozenset({"main", "nav", "header", "footer", "aside", "section", "form"})
LANDMARK_ROLES = frozenset({
    "main", "navigation", "banner", "contentinfo", "complementary",
    "region", "form", "search", "article",
})

#: linkedin_server.dom.harvest_linked_cards' own default -- carried over
#: rather than re-guessed. See module docstring.
MAX_HOPS = 8

#: Generic empty-state / error vocabulary, authored for this file. Not one of
#: these is copied from a capture.
EMPTY_STATE_NEEDLES = (
    "no results", "nothing to show", "nothing here", "no data available",
    "something went wrong", "try again", "we could not", "unable to load",
    "not found", "no activity yet", "no viewers yet", "temporarily unavailable",
    "please refresh", "no matches found", "isn't available", "an error occurred",
)


# ---------------------------------------------------------------------------
# A DOM-shape tree, built once per document and never printed
# ---------------------------------------------------------------------------

class ElementNode:
    __slots__ = ("tag", "attrs", "parent", "children")

    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []


class TextNode:
    __slots__ = ("data", "parent")

    def __init__(self, data, parent):
        self.data = data
        self.parent = parent


class TreeBuilder(HTMLParser):
    """A defensive shape tree. Captures here are ``page.content()`` output --
    a browser's own serialization, always well-formed -- so a mismatched end
    tag is the exception. On one, this pops to the nearest matching ancestor
    instead of corrupting the stack, rather than assuming it cannot happen.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = ElementNode("#root", {}, None)
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = ElementNode(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(ElementNode(tag, attrs, self.stack[-1]))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
        # Unmatched on well-formed serialized DOM: ignore rather than corrupt.

    def handle_data(self, data):
        if data:
            self.stack[-1].children.append(TextNode(data, self.stack[-1]))


def parse(html):
    b = TreeBuilder()
    b.feed(html)
    return b.root


def walk(node):
    """Document-order walk, node itself first, ElementNode only."""
    if isinstance(node, ElementNode):
        yield node
        for c in node.children:
            yield from walk(c)


def find_all(root, tag):
    return [n for n in walk(root) if n.tag == tag]


def ancestors(node):
    """Innermost first, node itself excluded."""
    p = node.parent
    while p is not None:
        yield p
        p = p.parent


def contains(ancestor, node):
    return any(a is ancestor for a in ancestors(node))


def has_ancestor_tag(node, tag):
    return any(a.tag == tag for a in ancestors(node))


def rendered_text(node):
    """Text-node concatenation under node, STRIP_TAGS subtrees excluded,
    whitespace-collapsed. Same rule as the imported ``visible_text()``
    (strip bundle tags, collapse whitespace) but run over the parsed tree so
    it can be scoped to any subtree -- a <main>, a row, a panel -- where
    ``visible_text()`` only ever sees a whole raw string.
    """
    parts = []

    def _walk(n):
        if isinstance(n, TextNode):
            parts.append(n.data)
            return
        if n.tag in STRIP_TAGS:
            return
        for c in n.children:
            _walk(c)

    _walk(node)
    # Joined with a space, not "": visible_text() replaces EVERY tag with a
    # space before collapsing, so two text runs separated by a tag boundary
    # (however many tags deep) always end up with whitespace between them
    # there. html.parser (convert_charrefs=True) fires handle_data once per
    # contiguous non-tag run, so "one text node per gap" already holds; the
    # explicit separator is what makes an adjacent-inline-tag case like
    # ``<b>foo</b><i>bar</i>`` read "foo bar" here the same way it does
    # there, instead of gluing to "foobar".
    return re.sub(r"\s+", " ", " ".join(parts))


def landmark_stack(node):
    """Outermost-first landmark labels enclosing node.

    A landmark is a tag in LANDMARK_TAGS, or any element carrying an ARIA
    role in LANDMARK_ROLES. SIMPLIFICATION, stated rather than hidden: a bare
    ``<section>``/``<form>`` with no accessible name is not a landmark under
    strict ARIA; this file counts every section/form as one regardless, to
    keep the stack a simple structural trail rather than a name-dependent
    one. Where a role differs from the tag's own, both are shown:
    ``section[role=region]``.
    """
    out = []
    for a in ancestors(node):
        role = (a.attrs.get("role") or "").strip().lower()
        if a.tag in LANDMARK_TAGS:
            out.append("%s[role=%s]" % (a.tag, role) if (role and role != a.tag and role in LANDMARK_ROLES)
                        else a.tag)
        elif role in LANDMARK_ROLES:
            out.append("%s[role=%s]" % (a.tag, role))
    out.reverse()
    return out


def is_member_route(href):
    """True iff the shipped reducer would draw this as /in/<entity> -- the
    ONLY test used to decide "does this anchor address a person", so the
    classification and the redaction are the same code path.

    THE try/except AROUND ``shape_path`` WAS REMOVED 2026-09-20 BY THE WAVE
    LEAD, and it is a safety fix rather than a style one.
    ``tests/test_an_outage_is_never_filed_as_an_absence.py`` flagged it, and
    the guard is right in the direction that matters here: a swallowed
    exception returned ``False``, which this function's callers read as **"this
    anchor does not address a person"**. So a reducer that raised would have
    silently reclassified a MEMBER anchor as a non-member one -- the unsafe
    direction, on the one classification this file exists to get right, and
    indistinguishable from an honest negative.

    ``shape_path`` takes a string and does not raise on one. If it ever does,
    that is a defect that must stop the run, not be filed as an absence.
    """
    if not href:
        return False
    return shape_path(href, depth=2) == "/in/<entity>"


def member_anchors_in(node):
    """Every descendant <a href> (node itself included) addressing a member."""
    out = []
    for n in walk(node):
        if n.tag == "a" and is_member_route(n.attrs.get("href")):
            out.append(n)
    return out


def _href_fingerprint(href):
    """A per-TARGET distinctness key that is safe to hold and never printed.

    NOT shape_path(): shape_path() collapses EVERY ``/in/<anything>`` to the
    identical literal ``/in/<entity>`` by design (that is what makes it safe
    to print) -- which also means using it as a set key can never tell two
    DIFFERENT people's rows apart. A set built from shape_path() output can
    never exceed size 1, which silently disables the "this container spans
    more than one target" stop that row_of() depends on. Measured while
    building this file's control: real captures elsewhere in this wave
    stopped correctly only because a SECOND, independent check (raw anchor
    count once text exists) happened to cover for it -- true in this file's
    fixture but not guaranteed on a differently-shaped page.

    A SHA-1 of the raw href is distinct per real target, reveals nothing
    about it, and is never printed -- only len() of a set of these ever
    reaches output.
    """
    return hashlib.sha1(href.encode("utf-8", "surrogatepass")).hexdigest()


def _keys_within(node):
    """Distinct member-route TARGETS strictly under node (descendants only,
    node itself excluded) -- ported from HARVEST_LINKED_CARDS_JS's
    keysWithin(), which queries node.querySelectorAll and so never matches
    node itself. Values are opaque fingerprints (see _href_fingerprint);
    never printed, only counted via len().
    """
    keys = set()
    for c in node.children:
        for n in walk(c):
            if n.tag == "a":
                href = n.attrs.get("href")
                if is_member_route(href):
                    keys.add(_href_fingerprint(href))
    return keys


def _links_within(node):
    """Count of ALL matching anchors strictly under node, non-deduped --
    ported from HARVEST_LINKED_CARDS_JS's linksWithin().
    """
    count = 0
    for c in node.children:
        for n in walk(c):
            if n.tag == "a" and is_member_route(n.attrs.get("href")):
                count += 1
    return count


def row_of(anchor, max_hops=MAX_HOPS, _break=False):
    """Port of HARVEST_LINKED_CARDS_JS's rowOf(). Climbs from a member-route
    anchor to the largest ancestor that still speaks for exactly one target,
    stopping at a container, an LI/ARTICLE, or a data-view-name element.

    _break=True disables the container stop -- a DELIBERATE, obviously-wrong
    variant that exists only for the control's driven-failure demonstration.
    It must never be passed True on real data; the CLI never does.
    """
    node = anchor
    row = anchor
    hops = 0
    while node is not None and hops < max_hops:
        if not _break and len(_keys_within(node)) > 1:
            break
        if not _break and rendered_text(row) and _links_within(node) > 1:
            break
        row = node
        if node.tag in ("li", "article"):
            break
        if "data-view-name" in node.attrs:
            break
        node = node.parent
        hops += 1
    return row


def find_row_list(root, _break_scope=False):
    """Resolve the viewer-row list: the (parent, tag) signature that the
    member-route anchors' resolved rows agree on, plus every row of that
    signature under that parent (so a linkless, privacy-limited viewer row
    is counted too, per the harvest_linked_cards ``sibling_rows`` mode this
    mirrors).

    Returns a dict: parent, tag, rows (all, by signature), anchor_rows
    (the subset each holding >=1 member anchor), orderly (bool -- does every
    row in the full set carry AT MOST one distinct member key, matching the
    live harvester's own orderliness check), signatures (how many distinct
    (parent,tag) groups the anchors' rows fell into, for disagreement
    reporting).

    _break_scope is accepted and ignored here; the scope break lives in the
    caller (it governs the inside-main predicate, not row-finding).
    """
    anchors = member_anchors_in(root)
    groups = {}
    for a in anchors:
        row = row_of(a)
        if row.parent is None:
            continue
        sig = (id(row.parent), row.tag)
        groups.setdefault(sig, {"parent": row.parent, "tag": row.tag, "rows": set()})
        groups[sig]["rows"].add(id(row))
    if not groups:
        return None
    # The dominant signature: the one whose rows cover the most anchors.
    best_sig = max(groups, key=lambda s: len(groups[s]["rows"]))
    best = groups[best_sig]
    parent, tag = best["parent"], best["tag"]
    all_rows = [c for c in parent.children if isinstance(c, ElementNode) and c.tag == tag]
    anchor_row_ids = best["rows"]
    anchor_rows = [r for r in all_rows if id(r) in anchor_row_ids]
    orderly = all(len(_keys_within(r) | ({_href_fingerprint(r.attrs.get("href"))}
                                          if r.tag == "a" and is_member_route(r.attrs.get("href"))
                                          else set())) <= 1
                  for r in all_rows)
    return {
        "parent": parent,
        "tag": tag,
        "rows": all_rows,
        "anchor_rows": anchor_rows,
        "orderly": orderly,
        "signature_count": len(groups),
    }


def count_data_view_name(root, _scope_break=False):
    """(document-wide, inside-main) counts of elements carrying
    data-view-name. _scope_break=True makes the "inside main" predicate
    always True regardless of ancestry -- the control's second, INDEPENDENT
    break, modelling the exact historical defect (a reader that looks in the
    wrong box) rather than a generic bug.
    """
    doc_wide = 0
    inside_main = 0
    for n in walk(root):
        if "data-view-name" in n.attrs:
            doc_wide += 1
            if _scope_break or has_ancestor_tag(n, "main"):
                inside_main += 1
    return doc_wide, inside_main


def count_text_nodes(node):
    n = 0

    def _walk(x):
        nonlocal n
        if isinstance(x, TextNode):
            if x.data.strip():
                n += 1
            return
        if x.tag in STRIP_TAGS:
            return
        for c in x.children:
            _walk(c)

    _walk(node)
    return n


def count_aria_label_bearing(node):
    return sum(1 for n in walk(node) if (n.attrs.get("aria-label") or "").strip())


def distinct_anchor_shapes(node, depth=3):
    shapes = set()
    for n in walk(node):
        if n.tag == "a":
            href = n.attrs.get("href")
            if href and not href.startswith("#") and not href.startswith("mailto"):
                if href.startswith("http") and "linkedin.com" not in href:
                    continue
                shapes.add(shape_path(href, depth=depth))
    return shapes


def row_shape_counts(row):
    return {
        "a": len(find_all(row, "a")),
        "distinct_a_shapes": len(distinct_anchor_shapes(row)),
        "img": len(find_all(row, "img")),
        "button": len(find_all(row, "button")),
        "headings": sum(len(find_all(row, h)) for h in HEADING_TAGS),
        "text_nodes": count_text_nodes(row),
        "aria_label": count_aria_label_bearing(row),
    }


def _mmm(values):
    """min/median/max, formatted, tolerant of an empty list."""
    if not values:
        return "n/a (0 rows)"
    return "min=%s median=%s max=%s" % (
        min(values), statistics.median(values), max(values))


# ---------------------------------------------------------------------------
# File manifest
# ---------------------------------------------------------------------------

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest(paths):
    print("=== 0  CAPTURE MANIFEST")
    print("    %-28s %10s %-19s %s" % ("file", "bytes", "mtime (UTC)", "sha256"))
    for name, p in paths.items():
        if not p.exists():
            print("    %-28s %10s %-19s %s" % (name, "ABSENT", "-", "-"))
            continue
        st = p.stat()
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(st.st_mtime))
        print("    %-28s %10d %-19s %s" % (name, st.st_size, mtime, sha256_of(p)))


# ---------------------------------------------------------------------------
# Part 1
# ---------------------------------------------------------------------------

def part1(name, raw):
    print("  -- %s" % name)
    root = parse(raw)
    vis_shipped = visible_text(raw)
    vis_tree = rendered_text(root)
    print("    raw=%d  rendered(shipped visible_text)=%d  (%.1f%% of raw)"
          % (len(raw), len(vis_shipped), 100.0 * len(vis_shipped) / max(1, len(raw))))
    print("    rendered(tree-walk, same rule, whole doc)=%d  (parity check vs shipped: %s)"
          % (len(vis_tree), "MATCH" if abs(len(vis_tree) - len(vis_shipped)) <= 2 else
             "DIFFERS by %d" % (len(vis_tree) - len(vis_shipped))))

    mains = find_all(root, "main")
    print("    <main> elements: %d" % len(mains))
    if len(mains) == 1:
        main_text = rendered_text(mains[0])
        pct = 100.0 * len(main_text) / max(1, len(vis_shipped))
        print("    main_chars=%d  (%.1f%% of the page's rendered text)" % (len(main_text), pct))
    elif len(mains) > 1:
        for i, m in enumerate(mains):
            mt = rendered_text(m)
            print("    main[%d]_chars=%d  (%.1f%% of page)" % (i, len(mt), 100.0 * len(mt) / max(1, len(vis_shipped))))
    else:
        print("    main_chars=n/a (no <main> on this capture)")

    for tag in ("nav", "header", "footer", "aside", "section"):
        print("    <%s> count: %d" % (tag, len(find_all(root, tag))))
    heading_total = sum(len(find_all(root, h)) for h in HEADING_TAGS)
    per_heading = ", ".join("%s=%d" % (h, len(find_all(root, h))) for h in HEADING_TAGS)
    print("    headings total: %d  (%s)" % (heading_total, per_heading))

    if mains:
        target = mains[0]
        method = "<main> element, document order 0 (n=%d found)" % len(mains)
    else:
        # Fallback: the largest-rendered-text direct child of <body>.
        bodies = find_all(root, "body")
        candidates = []
        if bodies:
            candidates = [c for c in bodies[0].children if isinstance(c, ElementNode)]
        target = max(candidates, key=lambda c: len(rendered_text(c))) if candidates else None
        method = ("no <main>; fallback = largest-rendered-text direct child of <body> (<%s>)"
                  % target.tag if target is not None else "no <main>, no <body> children; undetermined")
    if target is not None:
        # landmark_stack() reports ANCESTORS only; the target's own tag is
        # appended last so the printed stack ends at the region itself.
        stack_full = landmark_stack(target) + [target.tag]
        print("    primary-content landmark stack (outermost first): %s" % " > ".join(stack_full))
        print("    identified via: %s" % method)
    else:
        print("    primary-content landmark stack: UNDETERMINED (%s)" % method)
    return root, vis_shipped


# ---------------------------------------------------------------------------
# Part 2 + 3 (profile-views)
# ---------------------------------------------------------------------------

def part2_3(root, vis_shipped):
    print("=== 2  THE SCOPE DEFECT, MEASURED OFFLINE")
    doc_wide, inside_main = count_data_view_name(root)
    print("    data-view-name elements, document-wide: %d" % doc_wide)
    print("    data-view-name elements, inside <main>: %d" % inside_main)

    rl = find_row_list(root)
    mains = find_all(root, "main")
    if rl is None:
        print("    viewer rows found (any anchor-driven signature): 0")
        print("    NO member-route anchor resolved to any row at all -- see below for what WAS seen.")
        row_count_doc = row_count_main = 0
        all_rows = []
    else:
        all_rows = rl["rows"]
        row_count_doc = len(all_rows)
        row_count_main = sum(1 for r in all_rows if has_ancestor_tag(r, "main"))
        print("    row-list resolved: <%s> repeated under one parent (%d row(s))"
              % (rl["tag"], row_count_doc))
        print("    distinct (parent,tag) signatures the anchors' rows fell into: %d%s"
              % (rl["signature_count"], "" if rl["signature_count"] == 1 else
                 "   <- DISAGREEMENT: not every member anchor climbed to the same row group"))
        print("    row list orderliness (every row carries <=1 distinct member key): %s"
              % ("yes" if rl["orderly"] else "NO -- at least one row holds >1 distinct member target"))
    print("    viewer rows, document-wide: %d" % row_count_doc)
    print("    viewer rows, inside <main>: %d" % row_count_main)

    if mains:
        main_text = rendered_text(mains[0])
        print("    main_chars on this capture: %d  (prior live measurement on "
              "/analytics/profile-views/: 1835)" % len(main_text))
    else:
        print("    main_chars on this capture: n/a (no <main>)")

    print("    ---")
    if row_count_doc == 0:
        print("    VERDICT: cannot evaluate the defect -- no viewer row was located at all on this "
              "capture (see part 3 note on WHAT WAS SEEN instead). This is itself a finding, not "
              "forced into either a reproduction or a clean miss.")
    elif row_count_main == 0 and row_count_doc > 0:
        print("    VERDICT: capture REPRODUCES the defect's shape -- %d row(s) exist document-wide "
              "and 0 are inside <main>." % row_count_doc)
    else:
        print("    VERDICT: capture DOES NOT reproduce the defect -- of %d row(s) document-wide, "
              "%d are inside <main> (nonzero). What was seen instead: the row list sits INSIDE "
              "<main> on this capture, contradicting the live document-wide/main-scoped gap quoted "
              "in the brief. Stated straight, not reconciled by adjusting the row-finder."
              % (row_count_doc, row_count_main))

    if rl is not None:
        list_stack = landmark_stack(rl["parent"]) + [rl["parent"].tag]
        rel = ("inside <main>" if has_ancestor_tag(rl["parent"], "main") else
               "sibling of <main>" if (mains and rl["parent"].parent is mains[0].parent) else
               "in a container <main> does not reach")
        print("    viewer-row list container landmark stack (outermost first): %s"
              % " > ".join(list_stack))
        print("    relative to <main>: %s" % rel)

    print()
    print("=== 3  PER-ROW STRUCTURE OF THE PEOPLE-BEARING LIST")
    if not all_rows:
        print("    NO ROWS -- nothing to structure. What WAS seen: %d member-route anchor(s) "
              "document-wide, %d landmark-bearing candidate container(s) examined."
              % (len(member_anchors_in(root)), 0))
        return

    per = [row_shape_counts(r) for r in all_rows]
    for key, label in (("a", "<a> anchors"), ("distinct_a_shapes", "distinct anchor route shapes"),
                        ("img", "<img>"), ("button", "<button>"), ("headings", "headings"),
                        ("text_nodes", "text nodes"), ("aria_label", "aria-label-bearing elements")):
        vals = [p[key] for p in per]
        print("    %-30s %s" % (label, _mmm(vals)))

    with_member = sum(1 for r in all_rows if member_anchors_in(r))
    print("    rows carrying a member-route (/in/<entity>) anchor: %d of %d" % (with_member, len(all_rows)))

    main_node = mains[0] if mains else None
    panel = find_panel(root, main_node, all_rows)
    if panel is None:
        print("    insights/trend/summary panel distinct from the row list: NOT FOUND")
    else:
        counts = {t: len(find_all(panel, t)) for t in
                  ("a", "img", "button") + HEADING_TAGS}
        print("    insights/trend/summary panel distinct from the row list: FOUND (<%s>)" % panel.tag)
        print("      element counts: %s" % ", ".join("%s=%d" % (k, v) for k, v in counts.items() if v))
        print("      landmark stack (outermost first): %s" % " > ".join(landmark_stack(panel) + [panel.tag]))
        print("      inside <main>: %s" % ("yes" if has_ancestor_tag(panel, "main") else "no"))


def find_panel(root, main_node, rows):
    """A direct child of <main> that does not contain any row and carries
    enough rendered text or a heading to be panel-like. Heuristic, stated as
    one: reported alongside its own counts so the lead can judge it, not
    hidden behind a bare "found".
    """
    if main_node is None:
        return None
    row_ids = {id(r) for r in rows}
    best = None
    best_len = -1
    for child in main_node.children:
        if not isinstance(child, ElementNode):
            continue
        if any(id(n) in row_ids for n in walk(child)):
            continue
        text = rendered_text(child)
        has_heading = any(find_all(child, h) for h in HEADING_TAGS)
        if len(text) >= 20 or has_heading:
            if len(text) > best_len:
                best, best_len = child, len(text)
    return best


# ---------------------------------------------------------------------------
# Part 4 (premium-hub, search-appearances)
# ---------------------------------------------------------------------------

CONTROL_TAGS = ("button",)


def control_texts(root):
    """Rendered subtree text of <button>/<a>/role=button|link|tab elements --
    OPERATIONAL DEFINITION, stated because "control text" is not self-evident.

    FIRST VERSION OF THIS FUNCTION USED DIRECT TEXT-NODE CHILDREN ONLY, ON
    THE THEORY THAT A BUTTON WRAPPING AN ICON PLUS A NESTED BADGE SHOULD NOT
    BE DOUBLE-COUNTED. It returned 0 on cap-premium-hub.html despite 45
    anchors and 23 buttons existing on the page -- measured by walking the
    parsed tree and checking child tag names (never printing them), which
    showed every single one of the first six wraps its label in nested
    <span>/<div> children and carries no direct text at all. That is a
    structural fact about this page (component-per-label styling), not a
    property of "control text" in general, so direct-only was the wrong
    definition rather than a stricter one. This version reads the CONTROL'S
    OWN SUBTREE (excluding nested <button>/<a>/role=... descendants, so a
    link-within-a-button or a badge-within-a-link is not counted twice
    through both the outer and the inner element).
    """
    out = []
    for n in walk(root):
        role = (n.attrs.get("role") or "").strip().lower()
        if n.tag not in ("button", "a") and role not in ("button", "link", "tab", "menuitem"):
            continue
        if any(a.tag in ("button", "a") for a in ancestors(n)):
            continue  # nested inside an outer control; counted there instead
        text = rendered_text(n).strip()
        if text:
            out.append(text)
    return out


def part4(name, raw):
    print("  -- %s" % name)
    root = parse(raw)
    ctrl_texts = control_texts(root)
    digit_controls = sum(1 for t in ctrl_texts if any(ch.isdigit() for ch in t))
    print("    control texts examined (<button>/<a>/role=button|link|tab): %d" % len(ctrl_texts))
    print("    digit-bearing rendered control texts: %d" % digit_controls)

    aria_vals = [n.attrs.get("aria-label") for n in walk(root) if (n.attrs.get("aria-label") or "").strip()]
    digit_aria = sum(1 for v in aria_vals if any(ch.isdigit() for ch in v))
    print("    aria-label-bearing elements: %d" % len(aria_vals))
    print("    digit-bearing aria-labels: %d" % digit_aria)
    if name == "premium-hub":
        print("    prior wave (premium hub, live): 7 control / 13 aria-label -- "
              "control %s, aria-label %s"
              % ("MATCHES" if digit_controls == 7 else "DIFFERS (%d)" % digit_controls,
                 "MATCHES" if digit_aria == 13 else "DIFFERS (%d)" % digit_aria))

    shapes = {}
    for n in walk(root):
        if n.tag != "a":
            continue
        href = n.attrs.get("href")
        if not href or href.startswith("#") or href.startswith("mailto"):
            continue
        if href.startswith("http") and "linkedin.com" not in href:
            continue
        shape = shape_path(href, depth=4)
        if shape.startswith("/premium"):
            shapes.setdefault(shape, []).append(n)
    if not shapes:
        print("    /premium/... route shapes drawn: 0")
    else:
        print("    /premium/... route shapes drawn: %d" % len(shapes))
        for shape in sorted(shapes):
            nodes = shapes[shape]
            stacks = {" > ".join(landmark_stack(n) + [n.tag]) for n in nodes}
            print("      %-40s anchors=%d  landmark stack(s): %s"
                  % (shape, len(nodes), "; ".join(sorted(stacks))))

    vis = visible_text(raw)
    print("    rendered length: unstripped=%d  stripped=%d" % (len(vis), len(vis.strip())))
    if name == "premium-hub":
        print("    prior wave (premium hub, live): 3346 unstripped / 3344 stripped -- "
              "unstripped %s, stripped %s"
              % ("MATCHES" if len(vis) == 3346 else "DIFFERS (%d)" % len(vis),
                 "MATCHES" if len(vis.strip()) == 3344 else "DIFFERS (%d)" % len(vis.strip())))

    low_raw, low_vis = raw.lower(), vis.lower()
    print("    empty-state / error needle census (%d needles, author's own):" % len(EMPTY_STATE_NEEDLES))
    print("      %-24s %9s %9s" % ("needle", "raw", "rendered"))
    for needle in EMPTY_STATE_NEEDLES:
        a, b = low_raw.count(needle), low_vis.count(needle)
        flag = "   <- SOURCE ONLY" if a and not b else ""
        print("      %-24s %9d %9d%s" % (needle, a, b, flag))


# ---------------------------------------------------------------------------
# Control
# ---------------------------------------------------------------------------

def _build_control_doc():
    """A synthetic document, authored, with a known shape:

      * <main> holds a <section> holding a <ul> of 3 <li> rows, each carrying
        data-view-name. Two carry a member-route anchor; the third is a
        privacy-limited row with none (mirrors the live "Someone at Acme"
        case dom.py's own docstring records).
      * <aside> inside <main> is a distinct panel (a heading + prose),
        structurally separate from the row list.
      * <footer>, OUTSIDE <main>, holds ONE decoy row: a <div> carrying its
        own data-view-name AND a member-route anchor, but not part of the
        <li> sibling group -- it must be counted document-wide and excluded
        from both the main-scoped tally and the row list.

    Every slug re-uses the THREE TOKENS already committed and passing in
    ``scripts/_probe_premium_surfaces_shape.py``'s own CONTROL 3
    (``placeholder-slug``, ``example-org-slug``, ``example-campus-slug``),
    rather than inventing new ones. That file's control explains why a fresh
    short/hyphenated/digit-free slug is not a safe way to author a synthetic
    one: it is exactly what a naive length-or-digit redaction rule would wave
    through, so this repository's identity guard treats ANY undeclared
    slug-shaped string as suspect on sight -- including a freshly-invented
    "obviously synthetic" one -- and only recognises these three because they
    are already declared safe. Re-using them costs nothing here: the row
    logic below only needs three anchors to be MUTUALLY DISTINCT targets,
    never that their slugs mean anything.
    """
    html = """
<html><body>
<header><nav><a href="/feed/">Home</a></nav></header>
<main>
<h1>Who viewed your profile</h1>
<section aria-label="viewer list">
<ul>
<li data-view-name="profile-viewer-row"><a href="/in/placeholder-slug">Row One</a><span>Engineer</span></li>
<li data-view-name="profile-viewer-row"><a href="/in/example-org-slug">Row Two</a><img alt="x"><button aria-label="More actions row two">More</button></li>
<li data-view-name="profile-viewer-row"><span>Someone at a company</span><span>Recruiter</span></li>
</ul>
</section>
<aside aria-label="trend"><h2>Your views this week</h2><p>Some prose that is not a row at all.</p></aside>
</main>
<footer>
<div data-view-name="decoy-outside-main"><a href="/in/example-campus-slug">Decoy</a></div>
</footer>
</body></html>
"""
    expected = {
        "data_view_name_doc": 4,
        "data_view_name_main": 3,
        "rows_doc": 3,
        "rows_main": 3,
        "rows_with_member_anchor": 2,
    }
    return html, expected


def _run_control_pass(html, expected, *, break_rows=False, break_scope=False):
    root = parse(html)
    dvn_doc, dvn_main = count_data_view_name(root, _scope_break=break_scope)

    if break_rows:
        # Deliberately corrupt row-finding: disable the container stop so
        # the climb overshoots past the intended <li> boundary.
        anchors = member_anchors_in(root)
        rows = set()
        for a in anchors:
            r = row_of(a, _break=True)
            rows.add(id(r))
        rows_doc = len(rows)
        rows_main = sum(1 for a in anchors if has_ancestor_tag(row_of(a, _break=True), "main"))
        with_member = None  # not meaningfully defined once rows have collapsed
    else:
        rl = find_row_list(root)
        rows_doc = len(rl["rows"]) if rl else 0
        rows_main = sum(1 for r in rl["rows"] if has_ancestor_tag(r, "main")) if rl else 0
        with_member = len(rl["anchor_rows"]) if rl else 0

    ok = (dvn_doc == expected["data_view_name_doc"]
          and dvn_main == expected["data_view_name_main"]
          and rows_doc == expected["rows_doc"]
          and rows_main == expected["rows_main"]
          and (with_member == expected["rows_with_member_anchor"] if with_member is not None else True))

    print("    data-view-name doc-wide:   got=%d expected=%d" % (dvn_doc, expected["data_view_name_doc"]))
    print("    data-view-name in <main>:  got=%d expected=%d" % (dvn_main, expected["data_view_name_main"]))
    print("    rows doc-wide:             got=%d expected=%d" % (rows_doc, expected["rows_doc"]))
    print("    rows in <main>:            got=%d expected=%d" % (rows_main, expected["rows_main"]))
    if with_member is not None:
        print("    rows with member anchor:  got=%d expected=%d" % (with_member, expected["rows_with_member_anchor"]))
    else:
        print("    rows with member anchor:  UNDEFINED (rows collapsed by the induced break)")
    return ok


def control():
    """Every control, each capable of voiding the run."""
    html, expected = _build_control_doc()

    print("=== CONTROL 1  THE EXTRACTOR IS RIGHT ON A KNOWN DOCUMENT")
    ok = _run_control_pass(html, expected)
    if not ok:
        print("    VOID -- the extractor is wrong on a document whose answer is known by construction")
        return 1
    print("    all five counts matched their authored truth.  PASS")

    print("=== CONTROL 2  THE REDUCER STILL REDACTS ON THESE SYNTHETIC SLUGS")
    cases = ("/in/placeholder-slug", "/in/example-org-slug", "/in/example-campus-slug")
    leaked = [c for c in cases if c.split("/")[-1] in shape_path(c)]
    for c in cases:
        print("    %-24s -> %s" % (c, shape_path(c)))
    if leaked:
        print("    VOID -- %d synthetic slug(s) survived shape_path()" % len(leaked))
        return 1
    print("    0 of %d survived.  PASS" % len(cases))

    print("=== CONTROL 3  THE STRIPPER USED FOR rendered_text() MATCHES visible_text()")
    doc_vis = visible_text(html)
    doc_tree = rendered_text(parse(html))
    if abs(len(doc_vis) - len(doc_tree)) > 2:
        print("    VOID -- whole-document tree-walk (%d) disagrees with the shipped reducer (%d)"
              % (len(doc_tree), len(doc_vis)))
        return 1
    print("    shipped visible_text()=%d  tree-walk rendered_text()=%d  (within tolerance).  PASS"
          % (len(doc_vis), len(doc_tree)))

    print()
    print("control: all three passed -- a zero in the real run is a measurement")
    return 0


def break_demo():
    """Run the SAME assertions with the extractor deliberately corrupted, in
    two independent ways, and show them fail loudly. A non-zero exit here is
    the CORRECT outcome of this demonstration, not a defect in this script.
    """
    html, expected = _build_control_doc()
    overall_ok = True

    print("=== BREAK 1  ROW-FINDING WITH THE CONTAINER STOP DISABLED")
    print("    (mirrors: a row-walk that never learns it has left one row and entered the next)")
    ok = _run_control_pass(html, expected, break_rows=True)
    print("    -> %s" % ("PASSED (unexpected -- the break had no effect; investigate)" if ok
                          else "FAILED as expected: the corrupted extractor's counts do not match "
                               "the authored truth"))
    overall_ok = overall_ok and not ok  # we EXPECT failure; "ok" here would be the anomaly

    print("=== BREAK 2  data-view-name SCOPE PREDICATE FORCED TRUE (THE HISTORICAL DEFECT ITSELF)")
    print("    (mirrors: a reader that reports every row as 'inside main' regardless of where it is)")
    ok = _run_control_pass(html, expected, break_scope=True)
    print("    -> %s" % ("PASSED (unexpected -- the break had no effect; investigate)" if ok
                          else "FAILED as expected: forcing the scope predicate true produced a "
                               "main-count that no longer matches the authored truth"))
    overall_ok = overall_ok and not ok

    print()
    if overall_ok:
        print("break-demo: both induced breaks were caught (both mismatched truth as they should).")
        print("exiting 1 -- non-zero on purpose, to prove a broken extractor cannot exit clean.")
        return 1
    print("break-demo: AT LEAST ONE INDUCED BREAK DID NOT CHANGE THE RESULT -- the control is "
          "weaker than assumed. This is reported, not smoothed over.")
    return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="analytics-list DOM shape, offline")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--break-demo", action="store_true")
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    args = ap.parse_args()

    if args.break_demo:
        return break_demo()
    if args.control:
        return control()

    state = Path(args.state)
    paths = dict((s, state / fname) for s, fname in CAPTURES.items())
    manifest(paths)

    needed = ("profile-views", "search-appearances", "premium-hub")
    missing = [s for s in needed if not paths[s].exists()]
    if missing:
        print()
        print("CAPTURES ABSENT (%d of %d needed): %s" % (len(missing), len(needed), ", ".join(missing)))
        print("An absence is not a zero. _state/ carries no files in a linked worktree; "
              "pass --state to point at the main checkout, or run this from there.")
        return 2

    docs = dict((s, p.read_text(encoding="utf-8", errors="replace")) for s, p in paths.items())

    print()
    print("=== 1  ANALYTICS PAGE FRAME, PER CAPTURE")
    root_pv, vis_pv = part1("profile-views", docs["profile-views"])
    root_sa, vis_sa = part1("search-appearances", docs["search-appearances"])

    print()
    part2_3(root_pv, vis_pv)

    print()
    print("=== 4  THE /premium/profile-key-skills BASIS")
    part4("premium-hub", docs["premium-hub"])
    part4("search-appearances", docs["search-appearances"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
