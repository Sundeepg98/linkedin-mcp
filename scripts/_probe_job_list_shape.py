"""What a LinkedIn job-list surface is made of, measured from two live captures.

Nobody has ever opened /jobs/collections/top-applicant or
/jobs/collections/top-choice -- there is no capture of either, and this file
does not create one. What it measures instead is the DOM shape of the two
job-list surfaces that HAVE been captured live: /jobs/collections/recommended/
and /jobs/search/. Their structure is the only honest basis for a synthetic
fixture for the two uncaptured pages, so this file turns that structure into
numbers.

THE HEADLINE FINDING THIS FILE EXISTS TO REPORT: a LinkedIn job list is
TWO-TIERED, not one repeating card. Every job posting gets a LIST SLOT
(`<li data-occludable-job-id="...">`, one per posting LinkedIn knows about in
the current window); only a subset of slots are HYDRATED with an actual
content card (`<div class="job-card-container" data-job-id="...">`, nested two
levels inside the slot). The rest are empty placeholder `<li>` elements
carrying LinkedIn's own class `jobs-search-results__job-card-search--generic-
occludable-area` -- a name that says what it is. A fixture or reader built
against only the hydrated-card shape will silently miss two-thirds of the
list slots on both captures measured here. This was found by chasing a
discrepancy the first version of this file's own selector table surfaced
(`data-occludable-job-id` doc-wide count did not match the hydrated-card
count), not assumed going in.

THE CAPTURES ARE A LIVE CAPTURE OF A REAL PERSON'S ACCOUNT. They embed his
name, his connections' names, his employer, his campus, his member id and
profile slugs, plus a member urn inside a trackingInfo blob. Nothing derived
from them may carry a name. This file imports shape_path() and visible_text()
from the sibling _probe_premium_surfaces_shape.py rather than reimplementing
them -- that file's docstring records that a hand-rolled reducer LEAKED a real
slug on its first version, found by reading the leak off stdout, not the code.
Route shapes below go through that one function, unmodified.

A NEEDLE IN THE SOURCE IS NOT A NEEDLE ON THE PAGE. Every text-derived count
below is reported raw (over the byte/char source) and rendered (over the
script/style/code/template/noscript-stripped text) side by side, using the
same visible_text() the sibling probe uses and validates.

AN ABSENT CAPTURE IS NOT A ZERO. If either file is missing this exits 2 and
tallies nothing.

Card structure is measured with a small stack-based tree builder on top of
the stdlib html.parser (no lxml/bs4 in this venv, and none added). Void
elements (img, br, input, ...) are never pushed onto the open-element stack,
because browser-serialized markup (what page.content() returns) never gives
them a matching close tag.

Run it as (from a linked worktree, where _state/ is not present locally so
the main checkout's copy must be named explicitly; the path itself belongs in
a run instruction, never hardcoded into source or spelled out as a literal
here -- see --state's own default, derived, just above)::

    ../../../venv/Scripts/python.exe scripts/_probe_job_list_shape.py --state ../../../_state
    ../../../venv/Scripts/python.exe scripts/_probe_job_list_shape.py --control
    ../../../venv/Scripts/python.exe scripts/_probe_job_list_shape.py --control --break-extractor

Run from the main checkout itself, --state needs no override (the derived
default already resolves there).
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import re
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _probe_premium_surfaces_shape import shape_path, visible_text  # noqa: E402

#: Derived, never hardcoded: an absolute literal here would embed the
#: operator's account path and trip this repository's identity guard on any
#: change set that includes this file, even untracked. Resolves to THIS
#: script's own parent-of-scripts/ directory -- the main checkout's _state/
#: when run there, or this worktree's (gitignored, absent) when run here.
#: Override with --state when the two differ, e.g. from a linked worktree:
#:     <python> scripts/_probe_job_list_shape.py --state ../../../_state
ROOT = Path(__file__).resolve().parents[1]
MAIN_STATE_DEFAULT = ROOT / "_state"

CAPTURES = (
    ("recommended", "cap-jobs-recommended.html"),
    ("search", "cap-jobs-search.html"),
)

VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

LANDMARK_TAGS = frozenset(
    {"main", "nav", "header", "footer", "aside", "section", "form"})
HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})

#: TIER 1 -- the element present once per job posting LinkedIn knows about in
#: the current list window, hydrated or not. Found by chasing why this
#: attribute's doc-wide grep count (24-25) did not match the tier-2 card
#: count (7): it lives on <li>, not on the card div.
SLOT_ATTR = "data-occludable-job-id"

#: TIER 2 -- the element present only for a job posting whose content has
#: actually been rendered. Class token verified as an EXACT token match
#: (not a substring: BEM element/modifier suffixes like
#: job-card-container__title are separate tokens and do not match this).
CARD_CLASS_TOKEN = "job-card-container"

#: LinkedIn's own name for an un-hydrated slot. Self-documenting: this is a
#: semantic class name (safe per this file's brief), not a hashed one.
PLACEHOLDER_CLASS_TOKEN = "jobs-search-results__job-card-search--generic-occludable-area"

#: Attribute names checked, in order, when asking whether a CARD (tier 2)
#: exposes its id directly on its own subtree. Order matters only as a
#: search sequence, not a ranking.
SELECTOR_CANDIDATES = ("data-job-id", "data-occludable-job-id")

EMPTY_NEEDLES = (
    "no results", "nothing here", "try again", "not available", "no longer",
    "sorry", "page not found", "coming soon", "check back", "we could not",
    "something went wrong", "no jobs",
)

HASHED_TOKEN_RE = re.compile(r"^_?[0-9a-f]{6,10}$")
DIGIT_RUN_RE = re.compile(r"\d{4,}")
EMBER_ID_RE = re.compile(r"^ember\d+$")


# ---------------------------------------------------------------------------
# A tree, built with the one HTML parser this venv ships without adding a
# dependency. Void elements are never pushed (browser-serialized markup, the
# format page.content() returns, never gives them a matching close tag);
# every other element is pushed and popped by handle_endtag. A stray end tag
# with no open match on the stack is ignored rather than corrupting it.
# ---------------------------------------------------------------------------

class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = attrs
        self.children = []
        self.parent = parent

    def class_tokens(self):
        c = self.attrs.get("class") or ""
        return c.split()

    def iter_subtree(self):
        yield self
        for ch in self.children:
            yield from ch.iter_subtree()

    def ancestors(self):
        n = self.parent
        while n is not None:
            yield n
            n = n.parent


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#document", {}, None)
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.stack[-1])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
        # stray close tag, no open match on the stack: ignored, not fatal.


def parse_tree(raw_html):
    tb = TreeBuilder()
    tb.feed(raw_html)
    tb.close()
    return tb.root


def all_nodes(root):
    for ch in root.children:
        yield from ch.iter_subtree()


def is_inside(node, tag):
    return any(a.tag == tag for a in node.ancestors())


def digit_len(s):
    m = DIGIT_RUN_RE.search(s or "")
    return len(m.group(0)) if m else None


def find_cards_by_token(root, token):
    return [n for n in all_nodes(root) if token in n.class_tokens()]


def find_cards(root):
    """Tier 2: hydrated content wrappers."""
    return find_cards_by_token(root, CARD_CLASS_TOKEN)


def find_slots(root):
    """Tier 1: one element per job posting, hydrated or not."""
    return [n for n in all_nodes(root) if SLOT_ATTR in n.attrs]


def slot_hydrated_card(slot, card_id_set):
    """The tier-2 card nested in this slot, or None."""
    for d in slot.iter_subtree():
        if id(d) in card_id_set:
            return d
    return None


def route_shapes_in(node):
    shapes = []
    for n in node.iter_subtree():
        if n.tag != "a":
            continue
        href = n.attrs.get("href")
        if not href:
            continue
        if href.startswith("#") or href.startswith("mailto") or href.startswith("javascript"):
            continue
        if href.startswith("http") and "linkedin.com" not in href:
            continue
        shapes.append(shape_path(href))
    return shapes


def card_id_signal(card):
    """(mechanism, digit_len) for the first id-bearing signal a card exposes,
    searched over the whole card subtree. Never returns the id itself."""
    for attr in SELECTOR_CANDIDATES:
        for n in card.iter_subtree():
            v = n.attrs.get(attr)
            if v:
                dl = digit_len(v)
                if dl:
                    return attr, dl
    for n in card.iter_subtree():
        if n.tag == "a":
            m = re.search(r"/jobs/view/(\d{4,})", n.attrs.get("href") or "")
            if m:
                return "href:/jobs/view/<digits>", len(m.group(1))
    return None, None


def class_token_report(tok):
    """Print form for a class token -- verbatim if it reads as ordinary CSS
    vocabulary, shape-only (length, char class) if it reads as a generated
    hash, per this file's safety brief."""
    if HASHED_TOKEN_RE.match(tok):
        return "<hashed len=%d hex>" % len(tok)
    if len(tok) > 20 and tok.isalnum() and not tok.islower():
        return "<shared-token len=%d mixed-alnum, identical across both captures>" % len(tok)
    return tok


# ---------------------------------------------------------------------------
# Section builders -- each returns (report_lines, data_for_the_diff_table).
# ---------------------------------------------------------------------------

def sha_row(path):
    raw = path.read_bytes()
    return {
        "path": path.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "mtime": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                     .strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def measure_document_frame(name, raw_text, raw_bytes, root):
    vis = visible_text(raw_text)
    tag_counts = Counter(n.tag for n in all_nodes(root))
    main_nodes = [n for n in all_nodes(root) if n.tag == "main"]
    lines = []
    lines.append("### %s -- document frame" % name)
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---|")
    lines.append("| raw byte size (on disk) | %d |" % raw_bytes)
    lines.append("| raw char length (decoded) | %d |" % len(raw_text))
    lines.append("| rendered text length | %d |" % len(vis))
    lines.append("| rendered as pct of raw char length | %.2f |" %
                  (100.0 * len(vis) / max(1, len(raw_text))))
    lines.append("| `<main>` count | %d |" % len(main_nodes))
    if main_nodes:
        main_raw_blocks = re.findall(r"<main\b.*?</main>", raw_text, flags=re.S | re.I)
        main_vis = visible_text(" ".join(main_raw_blocks))
        lines.append("| rendered text inside `<main>` | %d |" % len(main_vis))
        lines.append("| that as pct of the page's rendered text | %.2f |" %
                      (100.0 * len(main_vis) / max(1, len(vis))))
    for t in ("nav", "header", "footer", "aside", "section"):
        lines.append("| `<%s>` count | %d |" % (t, tag_counts.get(t, 0)))
    lines.append("")
    return lines, {"tag_counts": tag_counts, "rendered_len": len(vis), "raw_len": len(raw_text)}


def measure_cards(name, root):
    slots = find_slots(root)
    cards = find_cards(root)
    card_id_set = set(id(c) for c in cards)

    lines = []
    lines.append("### %s -- the job-card container (TWO TIERS)" % name)
    lines.append("")
    lines.append("tier 1, list slot: any element carrying `%s` -- one per job posting "
                  "LinkedIn has placed in this list window, hydrated or not." % SLOT_ATTR)
    lines.append("tier 2, hydrated card: exact class token `%s` -- only for slots "
                  "actually rendered with content." % CARD_CLASS_TOKEN)
    lines.append("")

    if not slots:
        lines.append("NO LIST SLOT FOUND (`%s` absent). Falling back to tier-2 only." % SLOT_ATTR)
        if not cards:
            lines.append("NO HYDRATED CARD FOUND EITHER.")
            return lines, {"slots": [], "cards": []}
    hydrated = []
    placeholder = []
    neither = []
    for s in slots:
        c = slot_hydrated_card(s, card_id_set)
        if c is not None:
            hydrated.append((s, c))
        elif PLACEHOLDER_CLASS_TOKEN in s.class_tokens():
            placeholder.append(s)
        else:
            neither.append(s)

    lines.append("slots found (tier 1): %d" % len(slots))
    lines.append("  hydrated (has a nested tier-2 card): %d" % len(hydrated))
    lines.append("  placeholder (`%s`, zero children): %d" % (PLACEHOLDER_CLASS_TOKEN, len(placeholder)))
    lines.append("  neither hydrated nor recognized-placeholder: %d%s" %
                  (len(neither), "  <- UNCLASSIFIED, see below" if neither else ""))
    lines.append("hydrated cards found (tier 2, independent class-token search): %d" % len(cards))
    lines.append("  hydration cross-check: every tier-2 card sits inside a tier-1 slot? %s" %
                  ("yes (%d == %d)" % (len(hydrated), len(cards))
                   if len(hydrated) == len(cards)
                   else "NO -- %d tier-2 cards, %d slots classified hydrated" % (len(cards), len(hydrated))))
    lines.append("")

    # Requested explicitly, separate from BOTH the generic `class` attribute
    # row below (which counts any element with any class, not this token)
    # and from `data-job-id` (a different attribute on the same element):
    # does the EXACT class token `job-card-container` itself diverge between
    # doc-wide and inside-<main>, the way the generic `class` attribute does?
    card_doc_wide = len(cards)
    card_inside_main = sum(1 for c in cards if is_inside(c, "main"))
    lines.append("EXACT CLASS TOKEN `%s` -- doc-wide vs inside-`<main>` (reported "
                 "whichever way it comes out, not smoothed toward the tidier answer):" %
                 CARD_CLASS_TOKEN)
    lines.append("  doc-wide: %d" % card_doc_wide)
    lines.append("  inside-<main>: %d" % card_inside_main)
    lines.append("  equal: %s%s" %
                 (card_doc_wide == card_inside_main,
                  "" if card_doc_wide == card_inside_main
                  else "  -- %d instance(s) of this exact token exist outside <main>"
                       % (card_doc_wide - card_inside_main)))
    lines.append("")

    if neither:
        lines.append("unclassified slot sample (tag, class tokens, descendant count):")
        for s in neither[:5]:
            desc_n = sum(1 for _ in s.iter_subtree()) - 1
            lines.append("  - %s, %d descendants, classes: %s" %
                          (s.tag, desc_n, [class_token_report(t) for t in s.class_tokens()]))
        lines.append("")

    slot_tag_set = Counter(s.tag for s in slots)
    slot_parent_set = Counter(s.parent.tag if s.parent else "<none>" for s in slots)
    lines.append("tier-1 slot tag: %s" % ", ".join("%s x%d" % kv for kv in slot_tag_set.most_common()))
    lines.append("tier-1 list-parent tag: %s" %
                  ", ".join("%s x%d" % kv for kv in slot_parent_set.most_common()))
    if hydrated:
        mid = hydrated[0][1].parent
        lines.append("structural path from slot to hydrated card: <slot> > <%s (%d attrs)> > <card class=%s>"
                      % (mid.tag, len(mid.attrs), CARD_CLASS_TOKEN))
    lines.append("")

    attr_name_slots = Counter()
    for s in slots:
        for a in s.attrs:
            attr_name_slots[a] += 1
    lines.append("attribute names on the tier-1 slot (name only, never value):")
    lines.append("")
    lines.append("| attribute | slots carrying it | of %d |" % len(slots))
    lines.append("|---|---|---|")
    for a, n in attr_name_slots.most_common():
        lines.append("| `%s` | %d | %.0f |" % (a, n, 100.0 * n / len(slots)))

    lines.append("")
    lines.append("selector candidates at the slot tier (doc-wide = anywhere in the "
                  "document, any tag, not just slots):")
    lines.append("")
    lines.append("| attribute | on every slot | doc-wide count | inside-`<main>` count | doc-wide == inside-main |")
    lines.append("|---|---|---|---|---|")
    best = None
    for a in sorted(attr_name_slots):
        doc_wide_nodes = [n for n in all_nodes(root) if a in n.attrs]
        doc_wide = len(doc_wide_nodes)
        inside_main = sum(1 for n in doc_wide_nodes if is_inside(n, "main"))
        every_slot = attr_name_slots[a] == len(slots)
        equal = doc_wide == inside_main
        lines.append("| `%s` | %s | %d | %d | %s |" %
                      (a,
                       "yes" if every_slot else "no (%d of %d)" % (attr_name_slots[a], len(slots)),
                       doc_wide, inside_main,
                       "yes" if equal else "NO -- %d outside main" % (doc_wide - inside_main)))
        if every_slot and doc_wide == len(slots):
            if best is None:
                best = a
    lines.append("")
    if best:
        lines.append("chosen slot selector: `%s` -- on every slot (%d of %d) and doc-wide "
                      "count equals the slot count exactly (%d == %d)." %
                      (best, len(slots), len(slots), len(slots), len(slots)))
    else:
        lines.append("NO attribute is both on-every-slot AND doc-wide-exclusive.")

    # tier-2 attribute table, for the hydrated subset specifically
    attr_name_cards = Counter()
    for c in cards:
        for a in c.attrs:
            attr_name_cards[a] += 1
    lines.append("")
    lines.append("attribute names on the tier-2 hydrated card (name only, never value):")
    lines.append("")
    lines.append("| attribute | cards carrying it | of %d |" % len(cards) if cards else "| (no hydrated cards) | | |")
    if cards:
        lines.append("|---|---|---|")
        for a, n in attr_name_cards.most_common():
            lines.append("| `%s` | %d | %.0f |" % (a, n, 100.0 * n / len(cards)))

    # id equality cross-check between tiers
    eq, mismatch, card_missing = 0, 0, 0
    for s, c in hydrated:
        sv = s.attrs.get(SLOT_ATTR)
        cv = c.attrs.get("data-job-id")
        if cv is None:
            card_missing += 1
        elif sv == cv:
            eq += 1
        else:
            mismatch += 1
    lines.append("")
    lines.append("cross-tier id equality (slot's `%s` vs hydrated card's `data-job-id`, "
                 "values never printed): %d equal, %d mismatched, %d card-side attribute absent"
                 % (SLOT_ATTR, eq, mismatch, card_missing))

    sample_parent = slots[0].parent if slots else (cards[0].parent if cards else None)
    chain = list(sample_parent.ancestors()) if sample_parent else []
    chain.reverse()
    landmark_chain = []
    for n in chain:
        if n.tag in LANDMARK_TAGS or "role" in n.attrs:
            role = n.attrs.get("role")
            landmark_chain.append("%s%s" % (n.tag, ("[role=%s]" % role) if role else ""))
    lines.append("")
    lines.append("landmark stack enclosing the list (outermost first, sampled from "
                 "slot 1's parent chain): %s" %
                 (" > ".join(landmark_chain) if landmark_chain else "(none found)"))
    lines.append("")
    return lines, {
        "slots": slots, "cards": cards, "hydrated": hydrated, "placeholder": placeholder,
        "neither": neither, "selector": best or SLOT_ATTR,
        "card_token_doc_wide": card_doc_wide, "card_token_inside_main": card_inside_main,
    }


def measure_card_contents(name, cards):
    lines = []
    lines.append("### %s -- what one HYDRATED card contains" % name)
    lines.append("")
    lines.append("scope: the %d hydrated tier-2 cards only. A placeholder slot has zero "
                 "children by construction and would silently zero out these stats if "
                 "folded in, so it is not." % len(cards))
    lines.append("")
    if not cards:
        lines.append("(no hydrated cards -- nothing to measure)")
        return lines, {}

    per = {"a": [], "distinct_shapes": [], "img": [], "button": [], "heading": [],
           "span": [], "p": [], "aria": []}
    shape_card_counts = Counter()
    for c in cards:
        nodes = list(c.iter_subtree())
        per["a"].append(sum(1 for n in nodes if n.tag == "a"))
        card_shapes = set(route_shapes_in(c))
        per["distinct_shapes"].append(len(card_shapes))
        for sh in card_shapes:
            shape_card_counts[sh] += 1
        per["img"].append(sum(1 for n in nodes if n.tag == "img"))
        per["button"].append(sum(1 for n in nodes if n.tag == "button"))
        per["heading"].append(sum(1 for n in nodes if n.tag in HEADING_TAGS))
        per["span"].append(sum(1 for n in nodes if n.tag == "span"))
        per["p"].append(sum(1 for n in nodes if n.tag == "p"))
        per["aria"].append(sum(1 for n in nodes if "aria-label" in n.attrs))

    labels = {"a": "`<a>` anchors", "distinct_shapes": "distinct anchor route shapes",
              "img": "`<img>`", "button": "`<button>`", "heading": "heading elements (h1-h6)",
              "span": "`<span>`", "p": "`<p>`", "aria": "elements with `aria-label`"}
    lines.append("| element | min | median | max |")
    lines.append("|---|---|---|---|")
    stats = {}
    for k in ("a", "distinct_shapes", "img", "button", "heading", "span", "p", "aria"):
        vals = per[k]
        med = statistics.median(vals)
        med_s = ("%d" % med) if med == int(med) else ("%.1f" % med)
        lines.append("| %s | %d | %s | %d |" % (labels[k], min(vals), med_s, max(vals)))
        stats[k] = {"min": min(vals), "median": med, "max": max(vals)}
    lines.append("")
    lines.append("distinct anchor route shapes observed, aggregated across all %d hydrated "
                 "cards (via the shipped, control-tested shape_path() -- never a raw href):" % len(cards))
    lines.append("")
    lines.append("| route shape | cards linking to it | of %d |" % len(cards))
    lines.append("|---|---|---|")
    for sh, n in sorted(shape_card_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append("| `%s` | %d | %.0f |" % (sh, n, 100.0 * n / len(cards)))
    lines.append("")
    return lines, stats


def measure_job_id(name, slotinfo):
    slots = slotinfo.get("slots", [])
    hydrated = slotinfo.get("hydrated", [])
    lines = []
    lines.append("### %s -- the job id" % name)
    lines.append("")
    if not slots:
        lines.append("(no slots -- nothing to measure)")
        return lines, {}

    slot_digit_lens = [digit_len(s.attrs.get(SLOT_ATTR)) for s in slots]
    slot_digit_lens = [d for d in slot_digit_lens if d]
    lines.append("list slots exposing an id: %d of %d (via `%s`, which is what defines "
                 "slot membership -- not an independent finding, the discovery mechanism)"
                 % (len(slot_digit_lens), len(slots), SLOT_ATTR))
    if slot_digit_lens:
        lines.append("  slot-level id digit length: min %d, max %d" %
                     (min(slot_digit_lens), max(slot_digit_lens)))

    mechanisms = Counter()
    digit_lens = []
    exposed = 0
    for _s, c in hydrated:
        mech, dl = card_id_signal(c)
        if mech:
            exposed += 1
            mechanisms[mech] += 1
            digit_lens.append(dl)
    lines.append("")
    lines.append("of the hydrated subset, cards independently exposing an id via their "
                 "own tier-2 attributes/href: %d of %d" % (exposed, len(hydrated)))
    lines.append("")
    lines.append("| mechanism | cards |")
    lines.append("|---|---|")
    for m, n in mechanisms.most_common():
        lines.append("| `%s` | %d |" % (m, n))
    if digit_lens:
        lines.append("")
        lines.append("hydrated-card id digit length: min %d, max %d (id values themselves "
                     "are never printed)" % (min(digit_lens), max(digit_lens)))
    lines.append("")
    return lines, {"slot_exposed": len(slot_digit_lens), "exposed": exposed,
                    "mechanisms": mechanisms, "digit_lens": digit_lens,
                    "slot_digit_lens": slot_digit_lens}


def measure_empty_state(name, raw_text):
    vis = visible_text(raw_text).lower()
    raw_low = raw_text.lower()
    lines = []
    lines.append("### %s -- landmark/empty-state vocabulary" % name)
    lines.append("")
    lines.append("| needle | in source | rendered |")
    lines.append("|---|---|---|")
    any_hit = False
    hit_summary = {}
    for needle in EMPTY_NEEDLES:
        a, b = raw_low.count(needle), vis.count(needle)
        hit_summary[needle] = (a, b)
        if a or b:
            any_hit = True
        lines.append("| %s | %d | %d |" % (needle, a, b))
    lines.append("")
    if not any_hit:
        lines.append("all %d needles are 0/0 on this capture -- consistent with a page that "
                     "loaded results rather than an empty or error state; this is a zero that "
                     "was checked for, not assumed." % len(EMPTY_NEEDLES))
    else:
        lines.append("at least one needle hit -- see table above for which, and whether it "
                     "survived stripping (rendered) or was source-only.")
    lines.append("")
    return lines, hit_summary


# ---------------------------------------------------------------------------
# Control -- the synthetic document models BOTH tiers: hydrated slots, empty
# placeholder slots, and one decoy slot (hydrated) OUTSIDE <main> entirely.
# ---------------------------------------------------------------------------

SYNTHETIC_DOC = """<!DOCTYPE html>
<html><head><title>control fixture</title></head>
<body>
<header>site header, sibling of main, not an ancestor of the list</header>
<nav>site nav</nav>
<main>
  <section>
    <h1>Jobs</h1>
    <ul class="job-card-list">
      <li data-occludable-job-id="1001" id="ember10"><div><div class="job-card-container" data-job-id="1001">
        <a href="/jobs/view/1000000001/">t</a>
        <img src="x.png">
        <button>Save</button>
        <h3>Title</h3>
        <span>Company</span>
        <span aria-label="place">Loc</span>
      </div></div></li>
      <li data-occludable-job-id="1002" id="ember11"><div><div class="job-card-container" data-job-id="1002">
        <a href="/jobs/view/1000000002/">t</a>
        <img src="x.png">
        <button>Save</button>
        <h3>Title</h3>
        <span>Company</span>
      </div></div></li>
      <li data-occludable-job-id="1003" id="ember12"><div><div class="job-card-container" data-job-id="1003">
        <a href="/jobs/view/1000000003/">t</a>
        <a href="/company/example-org-slug/">c</a>
        <img src="x.png">
        <button>Save</button>
        <h3>Title</h3>
        <span>Company</span>
        <span>Loc</span>
        <p>desc</p>
      </div></div></li>
      <li data-occludable-job-id="1004" id="ember13"><div><div class="job-card-container" data-job-id="1004">
        <a href="/jobs/view/1000000004/">t</a>
        <img src="x.png">
        <h3>Title</h3>
      </div></div></li>
      <li data-occludable-job-id="1005" id="ember14"><div><div class="job-card-container" data-job-id="1005">
        <a href="/jobs/view/1000000005/">t</a>
        <img src="x.png">
        <button>Save</button>
        <button>More</button>
        <h3>Title</h3>
        <span>Company</span>
      </div></div></li>
      <li data-occludable-job-id="1006" id="ember15" class="jobs-search-results__job-card-search--generic-occludable-area"></li>
      <li data-occludable-job-id="1007" id="ember16" class="jobs-search-results__job-card-search--generic-occludable-area"></li>
      <li data-occludable-job-id="1008" id="ember17" class="jobs-search-results__job-card-search--generic-occludable-area"></li>
    </ul>
  </section>
</main>
<aside class="rail">
  <div data-occludable-job-id="9999" id="ember99"><div class="job-card-container" data-job-id="9999">
    <a href="/jobs/view/9999999999/">decoy, outside main entirely, still hydrated</a>
  </div></div>
</aside>
<footer>
  <script>var hidden = "something went wrong " + "x".repeat(5);</script>
  <p>Sorry, we could not load more jobs right now.</p>
</footer>
</body></html>"""


def control_good():
    root = parse_tree(SYNTHETIC_DOC)
    ok = True

    def check(label, got, want):
        nonlocal ok
        passed = got == want
        ok = ok and passed
        print("  %-58s got=%-8r want=%-8r %s" % (label, got, want, "PASS" if passed else "FAIL"))

    print("=== CONTROL (good path): known-ground-truth synthetic document ===")
    slots = find_slots(root)
    cards = find_cards(root)
    card_id_set = set(id(c) for c in cards)

    check("doc-wide slots (tier 1)", len(slots), 9)
    check("inside-<main> slots", sum(1 for s in slots if is_inside(s, "main")), 8)
    check("doc-wide hydrated cards (tier 2)", len(cards), 6)
    check("inside-<main> hydrated cards", sum(1 for c in cards if is_inside(c, "main")), 5)

    hydrated = [(s, slot_hydrated_card(s, card_id_set)) for s in slots]
    hydrated = [(s, c) for s, c in hydrated if c is not None]
    placeholder = [s for s in slots if slot_hydrated_card(s, card_id_set) is None
                   and PLACEHOLDER_CLASS_TOKEN in s.class_tokens()]
    check("hydrated slot count", len(hydrated), 6)
    check("placeholder slot count", len(placeholder), 3)
    check("hydrated + placeholder accounts for every slot",
          len(hydrated) + len(placeholder), len(slots))

    in_main_hydrated = [(s, c) for s, c in hydrated if is_inside(s, "main")]
    check("list-parent tag is <ul> for all in-main slots",
          all(s.parent.tag == "ul" for s, _ in in_main_hydrated), True)

    by_id = {c.attrs.get("data-job-id"): c for c in cards}
    check("card 1001 anchor count",
          sum(1 for n in by_id["1001"].iter_subtree() if n.tag == "a"), 1)
    check("card 1003 anchor count (job + company)",
          sum(1 for n in by_id["1003"].iter_subtree() if n.tag == "a"), 2)
    check("card 1003 distinct route shapes", len(set(route_shapes_in(by_id["1003"]))), 2)
    check("card 1005 button count",
          sum(1 for n in by_id["1005"].iter_subtree() if n.tag == "button"), 2)
    check("card 1001 aria-label element count",
          sum(1 for n in by_id["1001"].iter_subtree() if "aria-label" in n.attrs), 1)

    mech, dl = card_id_signal(by_id["1001"])
    check("card 1001 id mechanism", mech, "data-job-id")
    check("card 1001 id digit length", dl, 4)

    href_dl = None
    for n in by_id["1004"].iter_subtree():
        if n.tag == "a":
            m = re.search(r"/jobs/view/(\d{4,})", n.attrs.get("href") or "")
            if m:
                href_dl = len(m.group(1))
    check("card 1004 href digit-run length (cross-check)", href_dl, 10)

    eq = sum(1 for s, c in hydrated if s.attrs.get(SLOT_ATTR) == c.attrs.get("data-job-id"))
    check("cross-tier id equality holds for all hydrated slots", eq, len(hydrated))

    vis = visible_text(SYNTHETIC_DOC).lower()
    raw_low = SYNTHETIC_DOC.lower()
    check("'something went wrong' rendered count (inside <script>)",
          vis.count("something went wrong"), 0)
    check("'something went wrong' raw count (inside <script>)",
          raw_low.count("something went wrong"), 1)
    check("'we could not' rendered count (inside <p>)", vis.count("we could not"), 1)

    print()
    print("CONTROL (good path): %s" % ("ALL PASS" if ok else "AT LEAST ONE FAILURE -- VOID"))
    return 0 if ok else 1


def control_broken():
    root = parse_tree(SYNTHETIC_DOC)
    broken_token = "job-card-container-TYPO-DOES-NOT-EXIST"
    print("=== CONTROL (deliberately broken path): same document, wrong selector ===")
    found = find_cards_by_token(root, broken_token)
    print("  selector used: %r" % broken_token)
    print("  cards found: %d   (ground truth on this fixture is 6)" % len(found))
    if len(found) == 6:
        print("  UNEXPECTED: the broken selector still matched everything -- "
              "this would mean the real extractor's PASS is vacuous. VOID.")
        return 0
    print("  FAIL, as designed: a wrong selector returns the wrong count on a "
          "document with a KNOWN answer, so the good-path PASS above is not vacuous.")
    return 1


def run_control_capturing_stdout(fn):
    """Run a control function, capturing everything it printed, so BOTH the
    passing and the deliberately-failing transcript can be embedded in the
    markdown deliverable rather than only shown at the terminal. A control
    whose transcript never leaves the terminal is unfalsifiable to anyone who
    did not happen to be watching the run -- this is the fix for that, not a
    new control."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exit_code = fn()
    return exit_code, buf.getvalue().rstrip("\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="job-list DOM shape, two captures, offline")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--break-extractor", action="store_true",
                     help="with --control, deliberately mis-supply the card selector")
    ap.add_argument("--state", default=str(MAIN_STATE_DEFAULT))
    ap.add_argument("--out", default=None, help="markdown report path")
    args = ap.parse_args()

    if args.control:
        return control_broken() if args.break_extractor else control_good()

    state = Path(args.state)
    paths = {name: state / fname for name, fname in CAPTURES}
    missing = [name for name, p in paths.items() if not p.exists()]
    if missing:
        print("CAPTURES ABSENT (%d of %d): %s" % (len(missing), len(CAPTURES), ", ".join(missing)))
        print("An absence is not a zero. Tallying nothing.")
        return 2

    report = []
    report.append("# job-list DOM shape -- two captures, measured offline")
    report.append("")
    report.append("Slice: premium-four / jobshape. Generated by "
                   "scripts/_probe_job_list_shape.py, no dependency added "
                   "beyond the stdlib html.parser (lxml/bs4 not installed in this venv).")
    report.append("")
    report.append("HEADLINE: a LinkedIn job list is two-tiered. Every job posting gets a "
                   "list slot (`<li data-occludable-job-id>`); only some slots are hydrated "
                   "with an actual content card (`<div class=\"job-card-container\" "
                   "data-job-id>`, nested one bare <div> deeper). The rest are empty "
                   "placeholder `<li>` elements -- LinkedIn's own class name for them is "
                   "`jobs-search-results__job-card-search--generic-occludable-area`. See "
                   "section 2 per capture for the exact hydrated/placeholder split.")
    report.append("")
    report.append("## 0. Captures")
    report.append("")
    report.append("| capture | sha256 | bytes | mtime (UTC) |")
    report.append("|---|---|---|---|")
    docs = {}
    shas = {}
    for name, p in paths.items():
        row = sha_row(p)
        shas[name] = row
        report.append("| %s (%s) | %s | %d | %s |" %
                       (name, row["path"], row["sha256"], row["bytes"], row["mtime"]))
        docs[name] = p.read_text(encoding="utf-8", errors="replace")
    report.append("")

    report.append("## 1. Control -- the extractor, shown able to fail, before its readings are trusted")
    report.append("")
    report.append("A synthetic document with a known ground truth: 9 list slots (6 hydrated, "
                  "3 empty placeholders), one of the hydrated slots placed OUTSIDE `<main>` as "
                  "a decoy, landmark ancestors at known depths, and a needle planted inside a "
                  "`<script>` block to prove stripping. Both outcomes below are the literal, "
                  "unedited stdout of running scripts/_probe_job_list_shape.py --control "
                  "and --control --break-extractor, captured at report-generation time -- not "
                  "retyped, not summarized.")
    report.append("")
    good_code, good_txt = run_control_capturing_stdout(control_good)
    report.append("### 1a. good path -- extractor pointed at the real selectors")
    report.append("")
    report.append("```")
    report.extend(good_txt.split("\n"))
    report.append("```")
    report.append("")
    report.append("process exit code: %d" % good_code)
    report.append("")
    broken_code, broken_txt = run_control_capturing_stdout(control_broken)
    report.append("### 1b. deliberately broken path -- same document, wrong class token")
    report.append("")
    report.append("```")
    report.extend(broken_txt.split("\n"))
    report.append("```")
    report.append("")
    report.append("process exit code: %d" % broken_code)
    report.append("")
    if good_code != 0 or broken_code != 1:
        report.append("CONTROL DID NOT BEHAVE AS DESIGNED (want good=0, broken=1; got "
                      "good=%d, broken=%d). Every number below is UNFALSIFIED by this run "
                      "and should not be trusted until this is fixed." % (good_code, broken_code))
        report.append("")

    results = {}
    for name, _ in CAPTURES:
        raw = docs[name]
        root = parse_tree(raw)
        report.append("## %s" % name)
        report.append("")
        l1, frame = measure_document_frame(name, raw, shas[name]["bytes"], root)
        l2, slotinfo = measure_cards(name, root)
        l3, contentstats = measure_card_contents(name, slotinfo.get("cards", []))
        l4, idinfo = measure_job_id(name, slotinfo)
        l5, emptyinfo = measure_empty_state(name, raw)
        report += l1 + l2 + l3 + l4 + l5
        results[name] = {"frame": frame, "slots": slotinfo, "content": contentstats,
                          "id": idinfo, "empty": emptyinfo}

    report.append("## differences between the two surfaces")
    report.append("")
    names = [n for n, _ in CAPTURES]
    report.append("| metric | %s |" % " | ".join(names))
    report.append("|---|%s" % ("---|" * len(names)))

    def row(label, fn):
        vals = [fn(results[n]) for n in names]
        report.append("| %s | %s |" % (label, " | ".join(str(v) for v in vals)))

    row("list slots (tier 1)", lambda r: len(r["slots"].get("slots", [])))
    row("hydrated cards (tier 2)", lambda r: len(r["slots"].get("cards", [])))
    row("placeholder slots", lambda r: len(r["slots"].get("placeholder", [])))
    row("unclassified slots", lambda r: len(r["slots"].get("neither", [])))
    row("hydration ratio",
        lambda r: ("%d/%d" % (len(r["slots"].get("cards", [])), len(r["slots"].get("slots", []))))
        if r["slots"].get("slots") else "n/a")
    row("selector chosen (tier 1)", lambda r: r["slots"].get("selector"))
    row("`job-card-container` token: doc-wide", lambda r: r["slots"].get("card_token_doc_wide"))
    row("`job-card-container` token: inside-`<main>`", lambda r: r["slots"].get("card_token_inside_main"))
    row("`job-card-container` token: doc-wide == inside-main",
        lambda r: r["slots"].get("card_token_doc_wide") == r["slots"].get("card_token_inside_main"))
    row("`<main>` count", lambda r: r["frame"]["tag_counts"].get("main", 0))
    row("`<nav>` count", lambda r: r["frame"]["tag_counts"].get("nav", 0))
    row("`<section>` count", lambda r: r["frame"]["tag_counts"].get("section", 0))
    row("rendered text length", lambda r: r["frame"]["rendered_len"])
    row("hydrated cards exposing an id (tier 2)", lambda r: r["id"].get("exposed"))
    row("hydrated-card id digit length (min-max)",
        lambda r: ("%d-%d" % (min(r["id"]["digit_lens"]), max(r["id"]["digit_lens"])))
        if r["id"].get("digit_lens") else "n/a")
    row("anchors per hydrated card (median)", lambda r: r["content"].get("a", {}).get("median"))
    row("images per hydrated card (median)", lambda r: r["content"].get("img", {}).get("median"))

    n0slots = len(results[names[0]]["slots"].get("slots", []))
    n1slots = len(results[names[1]]["slots"].get("slots", []))
    n0cards = len(results[names[0]]["slots"].get("cards", []))
    n1cards = len(results[names[1]]["slots"].get("cards", []))
    same_shape = (n0slots > 0 and n1slots > 0 and n0cards > 0 and n1cards > 0
                  and results[names[0]]["slots"].get("selector") == results[names[1]]["slots"].get("selector"))
    report.append("")
    report.append("one slot shape AND one hydrated-card shape describes both surfaces: %s" %
                   ("YES" if same_shape else "NO -- see table above"))
    report.append("caveat: slot COUNT differs between the two surfaces (%d vs %d) even though "
                  "the SHAPE (attributes, nesting, placeholder class) is identical -- a fixture "
                  "should treat slot count as a per-surface parameter, not a constant." %
                  (n0slots, n1slots))
    report.append("")

    out_text = "\n".join(report) + "\n"
    assert out_text.isascii(), "non-ASCII content would be written -- refusing to write"

    out_path = Path(args.out) if args.out else (HERE.parent / "_audit" / "_slice-premium-four-jobshape.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text, encoding="ascii")

    print(out_text)
    print("WROTE: %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
