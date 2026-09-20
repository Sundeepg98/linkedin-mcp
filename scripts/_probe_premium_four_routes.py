"""Anchor-level measurement of four premium route candidates, read OFFLINE.

The premium-four wave is deciding whether to admit four addresses to the read
allowlist:

    /analytics/recruiter-views
    /jobs/collections/top-applicant
    /jobs/collections/top-choice
    /premium/profile-key-skills

This re-reads the six captures already sitting in the main checkout's
``_state/`` (gitignored, absent from a linked worktree) -- no browser, no
session, no account touched -- and reports, per capture and in aggregate:
how many real ``<a href>`` elements resolve to each of the four route shapes,
the exact spelling of the href drawn (trailing slash, query param NAMES,
absolute vs root-relative), the enclosing landmark stack, the anchor's offset
in the rendered document, whether any DEEPER route is drawn under the same
prefix anywhere in the six captures, and -- the piece that decides the
allowlist argument -- every distinct route shape drawn under ``/analytics``,
``/jobs/collections`` and ``/premium``, with the shipped read predicate's
verdict on each shape today.

## WHY A REAL PARSER, NOT A BIGGER REGEX

A regex over ``href="..."`` cannot tell a ``<nav>`` anchor from a ``<main>``
one, cannot tell a genuine ``<a>`` from a ``<link>``/``<area>`` carrying the
same attribute name, and cannot be shown FAILING in a way that proves it was
ever looking at document structure at all. The extractor here is
``html.parser.HTMLParser`` with a tag stack, so landmark ancestry and anchor
offset are both real reads of DOM shape, not text proximity. The control
document below carries a ``<link rel="preload" href="...">`` and a
``<script>`` block that both spell the same href text as a real anchor, and
the report prints the raw-substring count alongside the real parsed count
so the gap is a measurement, not an assertion. Control 3 breaks the
extractor by renaming the attribute and the tag, and shows it correctly drop
to zero both times.

## THE SHIPPED REDUCER, IMPORTED, NOT REWRITTEN

``shape_path()`` and ``visible_text()`` come from
``scripts/_probe_premium_surfaces_shape.py`` by direct file load (no package
assumptions about ``scripts/``). That file's docstring records that a
hand-rolled reducer LEAKED a real slug on its first version -- the rule that
works replaces the segment AFTER a member-bearing prefix UNCONDITIONALLY.
None of this wave's three prefixes (``analytics``, ``jobs/collections``,
``premium``) are member-bearing, so no segment under them is ever
entity-redacted by that rule. A SECOND, stricter filter is layered on top
here for exactly that gap -- ``safe_shape()`` prints a literal path segment
only if it is a short lowercase/digit/hyphen token, and prints
``<seg:len=N>`` for anything else, including anything ``shape_path`` itself
would have passed through literally. This is additive, never a replacement.

## WHAT LEAVES THIS PROCESS

Integers, booleans, route shapes (member-bearing segments and any segment
that fails the extra literal-token filter both redacted), tag names,
landmark names, and words this file's author wrote (the synthetic control
document, which is 100% authored text). No href verbatim, no page text, no
accessible name, no member id ever reaches stdout from the real captures.

Run it as::

    ./venv/Scripts/python.exe scripts/_probe_premium_four_routes.py --control
    ./venv/Scripts/python.exe scripts/_probe_premium_four_routes.py
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server.readonly import is_read_url  # noqa: E402

# The shipped reducer is loaded by direct file path -- not `import scripts...`
# and not reimplemented -- so this works regardless of whether `scripts/` is
# a package, and so `shape_path`/`visible_text` are provably the same code
# object the sibling probe uses, not a fork of it.
_SHAPE_MOD_PATH = ROOT / "scripts" / "_probe_premium_surfaces_shape.py"
_spec = importlib.util.spec_from_file_location(
    "_probe_premium_surfaces_shape", _SHAPE_MOD_PATH)
_shape_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_shape_mod)
shape_path = _shape_mod.shape_path
visible_text = _shape_mod.visible_text

# Derived, never hardcoded: an absolute path to this checkout trips the
# repository's identity-shape guard (the operator's name is a `[drive root]`
# shape it refuses at commit time, whether or not anything is staged -- it
# scans the whole change set, untracked files included). ROOT (defined above,
# for the shape-module load) is THIS file's own checkout root, so
# DEFAULT_STATE resolves correctly when this script runs from the main
# checkout. Run from a linked worktree (which has no _state/ of its own --
# gitignored, confirmed empty here), pass the real one explicitly:
# --state ../../../_state
DEFAULT_STATE = ROOT / "_state"

SURFACES = ("jobs-recommended", "premium-hub", "newsletters",
            "profile-views", "search-appearances", "jobs-search")

TARGET_ROUTES = (
    "/analytics/recruiter-views",
    "/jobs/collections/top-applicant",
    "/jobs/collections/top-choice",
    "/premium/profile-key-skills",
)

SIBLING_PREFIXES = ("/analytics", "/jobs/collections", "/premium")

LANDMARK_TAGS = frozenset(
    {"nav", "main", "header", "footer", "aside", "section"})
VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})

#: Extra, STRICTER-than-shape_path defence. See module docstring. Applied
#: AFTER shape_path, never instead of it.
_SAFE_SEGMENT = re.compile(r"^[a-z][a-z0-9-]{0,23}$")
_SAFE_PARAM = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,31}$")


def safe_shape(shape):
    """shape_path()'s output, with any segment that is not a short
    lowercase/digit/hyphen token replaced by its length. Never prints a
    segment shape_path itself did not already agree to emit unredacted.
    """
    parts = shape.split("/")
    out = []
    for p in parts:
        if p in ("", "<entity>", "<opaque>"):
            out.append(p)
        elif _SAFE_SEGMENT.match(p):
            out.append(p)
        else:
            out.append("<seg:len=%d>" % len(p))
    return "/".join(out)


def safe_param_name(name):
    return name if _SAFE_PARAM.match(name) else ("<param:len=%d>" % len(name))


def path_segments(href):
    path = re.sub(r"^https?://[^/]+", "", href).split("?")[0].split("#")[0]
    return [s for s in path.split("/") if s]


def shape8_segments(shape8):
    return [seg for seg in shape8.split("/") if seg]


def shape_at(anchor, n):
    """This anchor's shape truncated to its first `n` path segments.

    Derived from the anchor's own depth-8 shape rather than re-deriving from
    the raw href (which the anchor dict does not carry). This is exact, not
    an approximation: shape_path()'s per-segment reduction depends only on
    that segment's own text and its immediate predecessor, never on the
    `depth` argument, so truncating an already-computed depth-8 shape to its
    first n segments is identical to having called shape_path(href, depth=n)
    directly. This matters because the four target routes are not all the
    same length (two are 2 segments, two are 3), so a single fixed-depth
    field would either truncate a 2-segment target's deeper draws into a
    3-segment shape that no longer matches it, or fail to notice a 2-segment
    target with a real sub-path -- both would be reported as false zeros.
    """
    segs = shape8_segments(anchor["shape8"])
    if not segs:
        return "/"
    return "/" + "/".join(segs[:n])


class AnchorWalker(HTMLParser):
    """Every real ``<a href>`` element: its landmark-ancestor stack (nav /
    main / header / footer / aside / section, outermost first) and its
    absolute character offset in the raw document. A tag stack, not a regex,
    because ancestry is a nesting question and nesting is not visible to a
    line-local pattern.
    """

    #: This class does NOT use HTMLParser.getpos()/updatepos() for offsets.
    #: Measured on the real search-appearances capture: a single <img> tag
    #: whose attribute values did not fit parse_starttag()'s quoting
    #: assumptions made check_for_whole_start_tag() return an end position
    #: 9 characters short of that tag's real end (confirmed by direct
    #: character-offset comparison, not inference) -- the tag was still
    #: recognised correctly (right name, right 3 attrs), only the position
    #: bookkeeping was wrong, and every getpos() call for the rest of the
    #: document then carried that shortfall forward, growing anchor by
    #: anchor (deltas of 2 to 54 observed across 29 anchors on that one
    #: capture, monotonically non-decreasing). Offsets are instead resolved
    #: after the fact by extract_anchors(), via an independent forward regex
    #: search that never touches HTMLParser's internal position state --
    #: see _independent_anchor_offsets().

    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.raw = raw
        self._tag_stack = []
        self._landmark_stack = []
        #: EVERY <a> open, with or without an href, in document order. Kept
        #: separate from "has an href" so this list's length can be cross-
        #: checked against the independent offset finder's count before
        #: either is trusted -- a mismatch means something about this
        #: document broke one of the two methods and neither should be used
        #: blind.
        self.all_a_opens = []  # dicts: href (or None), landmarks (tuple)

    def _record_a(self, attrs):
        href = dict(attrs).get("href")
        self.all_a_opens.append({
            "href": href,
            "landmarks": tuple(self._landmark_stack),
        })

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in LANDMARK_TAGS:
            self._landmark_stack.append(tag)
        if tag == "a":
            self._record_a(attrs)
        if tag not in VOID_TAGS:
            self._tag_stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        # Self-closed form, e.g. <a href="..." />. Counts as one anchor;
        # never pushed onto either stack since it never opens a scope.
        if tag.lower() == "a":
            self._record_a(attrs)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in LANDMARK_TAGS and tag in self._landmark_stack:
            for i in range(len(self._landmark_stack) - 1, -1, -1):
                if self._landmark_stack[i] == tag:
                    del self._landmark_stack[i]
                    break
        if tag in self._tag_stack:
            for i in range(len(self._tag_stack) - 1, -1, -1):
                if self._tag_stack[i] == tag:
                    del self._tag_stack[i:]
                    break


#: The same bundle tag set the shipped reducer strips, imported rather than
#: duplicated, so "what counts as a bundle" can never drift between the two
#: files.
_BUNDLE_TAGS = _shape_mod.STRIPPED_TAGS


def _blank_bundles(html):
    """`html` with every <script>/<style>/<code>/<template>/<noscript> block
    (open tag through close tag, inclusive) replaced by spaces of the SAME
    LENGTH. Every character OUTSIDE those blocks keeps its original offset
    exactly -- this is a position-preserving version of the shipped
    visible_text()'s stripping step, used only so a forward search for a
    literal tag-open can never land on text that only LOOKS like one inside
    a bundle. Nothing about this function's OUTPUT is ever printed; it
    exists purely to compute positions.
    """
    out = html
    for tag in _BUNDLE_TAGS:
        pat = re.compile(r"<%s\b.*?</%s>" % (tag, tag), re.S | re.I)
        out = pat.sub(lambda m: " " * len(m.group(0)), out)
    return out


#: '<a' followed by whitespace, '/', or '>' -- excludes <article>, <abbr>,
#: <aside>, <address> and similar, which also start with the two characters
#: '<a' but are not anchors.
_ANCHOR_OPEN = re.compile(r"<a(?=[\s/>])", re.I)


def _independent_anchor_offsets(raw):
    """Every real <a ...>/<a .../> tag-open's raw character offset, found by
    forward regex search over a bundle-blanked copy of `raw`.

    Deliberately independent of HTMLParser's getpos()/updatepos(): see the
    comment on AnchorWalker for the concrete case (a real capture) where
    that state was proven to desync from a malformed attribute on an
    unrelated tag. This function never calls feed()/getpos() and carries no
    parser state to desync -- it is a single pass of string search over a
    document that has already had every place such state could go wrong
    (script/style/code/template/noscript content) blanked out first.
    """
    blanked = _blank_bundles(raw)
    return [m.start() for m in _ANCHOR_OPEN.finditer(blanked)]


def raw_prefix_count(doc, path_prefix):
    """How many times `path_prefix` appears as the START of an href value,
    in EITHER root-relative (href="/x...) or absolute
    (href="https://www.linkedin.com/x... or href="https://linkedin.com/x...)
    spelling.

    Every relevant anchor measured on the six real captures for this wave
    turned out to be ABSOLUTE (is_absolute=True on all of them) -- a first
    version of this check only tried the root-relative spelling and reported
    raw=0 everywhere a real, parsed anchor existed, which is backwards for a
    check whose whole purpose is to show raw >= parsed. Deliberate raw
    substring counting, used ONLY for this comparison, per this repository's
    own discipline: `inmail` counts 16-21 raw and 0 rendered on this exact
    corpus, and a naive counter that cannot even find the routes it is
    trying to compare against proves nothing about that gap either way.
    """
    total = 0
    for spelling in ('href="' + path_prefix,
                      'href="https://www.linkedin.com' + path_prefix,
                      'href="https://linkedin.com' + path_prefix):
        total += doc.count(spelling)
    return total


def relevant(href):
    """Same admission filter the shipped reducer applies before shaping:
    drop fragments, mailto, and off-host absolutes. Kept as a predicate
    (not reimplemented differently) so both scripts agree on what counts as
    a LinkedIn route anchor at all.
    """
    if href.startswith("#") or href.startswith("mailto"):
        return False
    if href.startswith("http") and "linkedin.com" not in href:
        return False
    return True


def extract_anchors(raw):
    """Parse `raw` once. Return (anchors, stripped_total_len).

    Each anchor dict never carries the raw href -- only derived, safe
    fields: href_len, is_absolute, is_root_relative, has_trailing_slash,
    query_params (NAMES only, sorted tuple, each name itself passed through
    the same safe-token filter), landmarks, raw_offset, stripped_offset,
    shape (shape_path depth=3), shape8 (shape_path depth=8, unredacted --
    used only internally by shape_at() and by the sibling-inventory grouping
    key, never printed directly), safe_shape8 (the print-safe version of
    shape8), n_segments (total path segment count, for sub-path detection).

    Anchors that `relevant()` would drop (fragments, mailto, off-host
    absolutes) are still included here with their shape computed -- callers
    filter with relevant() on the SHAPE-lessness question they care about,
    since shape_path already reduces off-host absolutes to a bare path that
    would otherwise be indistinguishable from an on-host one. This function
    filters nothing; every caller below applies relevant() explicitly.

    raw_offset comes from _independent_anchor_offsets(), never from
    HTMLParser's own position tracking (see AnchorWalker's docstring for
    why). The two methods are cross-checked by COUNT before either is
    trusted: HTMLParser's tag/CDATA recognition decides WHETHER a given
    stretch of markup is a real <a> tag at all (that recognition was not
    the part found broken), and the independent regex decides WHERE each
    one sits in the raw text. Both methods independently exclude bundle
    content (HTMLParser via CDATA-mode parsing, the regex via a pre-pass
    that blanks the same tag set) so a matching count across the two is
    real evidence the pairing lines up, not a coincidence -- and a
    mismatched count raises rather than guessing, because at that point
    something has broken one of the two methods on this document and there
    is no third method here to arbitrate.

    stripped_offset is computed as len(visible_text(raw[:raw_offset])).
    This is exact, not approximate, given a correct raw_offset: raw_offset
    always points at the '<' of a genuine <a> tag (asserted below) and that
    position is never inside a <script>/<style>/<code>/<template>/
    <noscript> block (both methods agree on that), so cutting the raw
    document at that point and stripping the prefix never straddles an
    unclosed bundle tag.
    """
    walker = AnchorWalker(raw)
    walker.feed(raw)
    walker.close()
    stripped_total = len(visible_text(raw))

    independent_offsets = _independent_anchor_offsets(raw)
    if len(independent_offsets) != len(walker.all_a_opens):
        raise RuntimeError(
            "anchor cross-check failed: HTMLParser saw %d <a> tag-opens, "
            "the independent bundle-blanked regex search found %d. "
            "Refusing to pair them positionally -- something about this "
            "document broke one of the two methods and neither should be "
            "trusted blind." % (len(walker.all_a_opens), len(independent_offsets)))

    out = []
    for a, off in zip(walker.all_a_opens, independent_offsets):
        href = a["href"]
        if href is None:
            continue
        assert raw[off] == "<", (
            "offset invariant broken even after the independent search: "
            "raw[%d] = %r, expected '<'" % (off, raw[off]))
        if not relevant(href):
            shape3 = shape_path(href, depth=3)
            shape8 = shape_path(href, depth=8)
            out.append({
                "relevant": False,
                "href_len": len(href), "is_absolute": href.startswith("http"),
                "is_root_relative": href.startswith("/"),
                "has_trailing_slash": False, "query_params": (),
                "landmarks": a["landmarks"], "raw_offset": off,
                "stripped_offset": len(visible_text(raw[:off])),
                "shape": shape3, "shape8": shape8,
                "safe_shape8": safe_shape(shape8),
                "n_segments": len(path_segments(href)),
            })
            continue
        path_only = href.split("?")[0].split("#")[0]
        q = ()
        if "?" in href:
            qs = href.split("?", 1)[1].split("#")[0]
            names = [kv.split("=")[0] for kv in qs.split("&") if kv]
            q = tuple(sorted(set(safe_param_name(n) for n in names if n)))
        shape8 = shape_path(href, depth=8)
        out.append({
            "relevant": True,
            "href_len": len(href),
            "is_absolute": href.startswith("http"),
            "is_root_relative": href.startswith("/"),
            "has_trailing_slash": path_only.endswith("/") and path_only != "/",
            "query_params": q,
            "landmarks": a["landmarks"],
            "raw_offset": off,
            "stripped_offset": len(visible_text(raw[:off])),
            "shape": shape_path(href, depth=3),
            "shape8": shape8,
            "safe_shape8": safe_shape(shape8),
            "n_segments": len(path_segments(href)),
        })
    return out, stripped_total


# ---------------------------------------------------------------------------
# Control
# ---------------------------------------------------------------------------

def _build_synthetic_doc():
    """A document this file's author wrote in full. Every string in it is
    authored, not sampled -- safe to print verbatim in the deliverable.

    Deliberately carries THREE independent spellings of the same href text
    (a real <a>, a <link rel="preload">, and a <script>-embedded JS string)
    so the raw-substring-vs-parsed-anchor gap this file reports against the
    real captures is demonstrated here first, on a document with a known
    answer, rather than only asserted.
    """
    return """<html><head>
<link rel="preload" href="/analytics/recruiter-views" as="document">
</head><body>
<nav>
<a href="/analytics/recruiter-views">Recruiter views</a>
<a href="/premium/profile-key-skills?trk=nav">Key skills</a>
</nav>
<main>
<section>
<a href="/jobs/collections/top-applicant/">Top applicant jobs</a>
<a href="/jobs/collections/top-choice">Top choice jobs</a>
<a href="/jobs/collections/recommended">Recommended, not a target</a>
</section>
<aside>
<a href="/analytics/profile-views">Already-admitted sibling</a>
<a href="/jobs/collections/top-applicant/placeholder-slug">Deeper sub-path of a target</a>
</aside>
</main>
<footer>
<a href="/premium/my-premium/">Already-admitted premium sibling</a>
<a href="#section-anchor">Fragment, must be ignored</a>
<a href="mailto:test@example.com">Mailto, must be ignored</a>
<a href="https://other-domain-example.test/analytics/recruiter-views">Off-host, must be ignored</a>
</footer>
<script>
var fake = 'href="/analytics/recruiter-views"';
</script>
</body></html>"""


#: Expected (shape at the route's OWN depth -> count) for every RELEVANT
#: anchor in the synthetic doc.
_EXPECT_ROUTE_COUNTS = {
    "/analytics/recruiter-views": 1,
    "/premium/profile-key-skills": 1,
    "/jobs/collections/top-applicant": 2,   # the direct one + the deep one
    "/jobs/collections/top-choice": 1,
    "/jobs/collections/recommended": 1,
    "/analytics/profile-views": 1,
    "/premium/my-premium": 1,
}
_EXPECT_TOTAL_RELEVANT_ANCHORS = 8
_EXPECT_TOTAL_TAGS_A = 11  # 8 relevant + fragment + mailto + off-host
_EXPECT_LANDMARKS = {
    "/analytics/recruiter-views": [("nav",)],
    "/premium/profile-key-skills": [("nav",)],
    "/jobs/collections/top-choice": [("main", "section")],
    "/jobs/collections/recommended": [("main", "section")],
    "/analytics/profile-views": [("main", "aside")],
    "/premium/my-premium": [("footer",)],
}


def _control_extraction_accuracy():
    print("=== CONTROL 1  THE EXTRACTOR FINDS EXACTLY WHAT WAS AUTHORED")
    html = _build_synthetic_doc()
    ok = True

    total_a_tags = len(re.findall(r"<a\b", html, flags=re.I))
    print("    <a ...> tags in the synthetic doc (incl. ignored): %d "
          "(expected %d)" % (total_a_tags, _EXPECT_TOTAL_TAGS_A))
    ok = ok and total_a_tags == _EXPECT_TOTAL_TAGS_A

    anchors, stripped_total = extract_anchors(html)
    kept = [a for a in anchors if a["relevant"]]
    print("    <a href> elements the parser saw (all, pre-filter): %d"
          % len(anchors))
    print("    of those, relevant (drops #/mailto/off-host): %d "
          "(expected %d)" % (len(kept), _EXPECT_TOTAL_RELEVANT_ANCHORS))
    ok = ok and len(kept) == _EXPECT_TOTAL_RELEVANT_ANCHORS

    # Bucket every relevant anchor by each KNOWN route's OWN fixed depth --
    # the same thing main()'s real measurement does (route_segs computed
    # from the route string, never from the anchor's own natural length).
    # An earlier version of this loop bucketed by `len(shape8_segments(...))`
    # -- the ANCHOR's own full depth -- which put the deliberately-deeper
    # /jobs/collections/top-applicant/placeholder-slug anchor in its own
    # 4-segment bucket instead of folding it into the 3-segment parent, and
    # this control caught that on its first run (recorded here rather than
    # silently fixed, since a control that never printed the wrong number
    # first proves nothing about the version that replaced it).
    route_counts = {}
    landmarks_by_route = {}
    for route in _EXPECT_ROUTE_COUNTS:
        route_segs = [x for x in route.split("/") if x]
        n = len(route_segs)
        hits = [a for a in kept if shape_at(a, n) == route]
        route_counts[route] = len(hits)
        landmarks_by_route[route] = [h["landmarks"] for h in hits]

    print("    %-42s %8s %8s" % ("route (own depth)", "got", "want"))
    for route, want in sorted(_EXPECT_ROUTE_COUNTS.items()):
        got = route_counts.get(route, 0)
        flag = "" if got == want else "   <- MISMATCH"
        print("    %-42s %8d %8d%s" % (route, got, want, flag))
        ok = ok and got == want
    accounted = sum(route_counts.values())
    print("    relevant anchors accounted for across the 7 known routes: "
          "%d (of %d relevant total)" % (accounted, len(kept)))
    if accounted != len(kept):
        print("    VOID -- some relevant anchor fell outside every known "
              "route bucket, or was double-counted")
        ok = False

    for route, want_stacks in _EXPECT_LANDMARKS.items():
        got_stacks = landmarks_by_route.get(route, [])
        match = got_stacks == want_stacks
        print("    landmarks for %-32s got=%-22s want=%-22s%s"
              % (route, got_stacks, want_stacks,
                 "" if match else "   <- MISMATCH"))
        ok = ok and match

    # The specific target-route shaping bug this control exists to catch:
    # a fixed depth-3 field would truncate a 2-segment target the same as a
    # 3-segment one and mis-handle a deeper draw of it. Prove shape_at()
    # gives the route's OWN depth regardless of how many segments follow.
    deep_hits = [a for a in kept
                 if shape8_segments(a["shape8"])[:3] ==
                 ["jobs", "collections", "top-applicant"]
                 and len(shape8_segments(a["shape8"])) > 3]
    print("    jobs/collections/top-applicant anchors with a real 4th "
          "segment: %d (expected 1 -- the deliberately deeper one)"
          % len(deep_hits))
    ok = ok and len(deep_hits) == 1

    # The raw-substring-vs-parsed-anchor gap, demonstrated on THIS document.
    raw_hits = html.count('href="/analytics/recruiter-views"')
    parsed_hits = route_counts.get("/analytics/recruiter-views", 0)
    print("    raw substring count of href=\"/analytics/recruiter-views\": "
          "%d  (the <a>, the <link>, and the <script> string all spell it)"
          % raw_hits)
    print("    real <a>-tag parsed count for the same route: %d" % parsed_hits)
    if raw_hits <= parsed_hits:
        print("    VOID -- the synthetic doc failed to demonstrate a "
              "raw > parsed gap; the control's own premise did not hold")
        ok = False
    else:
        print("    gap confirmed on a document with a known answer: raw=%d, "
              "parsed=%d -- the <link> and the <script> string are both "
              "real, and both correctly excluded" % (raw_hits, parsed_hits))

    # Offset sanity: strictly increasing raw_offset in document order, every
    # stripped_offset within [0, stripped_total].
    raws = [a["raw_offset"] for a in anchors]
    strs = [a["stripped_offset"] for a in anchors]
    monotonic = raws == sorted(raws) and strs == sorted(strs)
    bounded = all(0 <= s <= stripped_total for s in strs)
    print("    raw_offset strictly increasing in doc order: %s" % monotonic)
    print("    every stripped_offset within [0, %d]: %s"
          % (stripped_total, bounded))
    ok = ok and monotonic and bounded

    print("    CONTROL 1 %s" % ("PASS" if ok else "VOID"))
    return ok


def _control_is_read_url_wiring():
    print("=== CONTROL 2  is_read_url() AGREES WITH THE SHIPPED ALLOWLIST "
          "ON CASES WITH A KNOWN ANSWER")
    # NONE of this wave's own four target routes appear in `cases` below,
    # deliberately: this shared worktree moved TWICE during this run (commits
    # a73ae10 at 12:06:52 admitted top-applicant/top-choice; fce0843 at
    # 12:31:39 admitted the remaining two, recruiter-views and
    # profile-key-skills -- so all four are now True). A hardcoded
    # expectation for any of the four would go stale the next time the
    # shared tree moves, and this control exists to catch a WIRING bug in
    # THIS script (does calling is_read_url actually reach the real,
    # current predicate), not to re-litigate a ruling that is this wave's
    # own subject and keeps landing while this script runs. Every case here
    # is either long-pre-existing (unrelated to this wave's decision) or
    # fabricated by this file's author to match no real LinkedIn surface, so
    # none of them can be moved by this wave's own commits.
    cases = (
        ("/analytics/profile-views", True),
        ("/premium/my-premium", True),
        ("/jobs/collections/recommended", True),
        ("/this-route-does-not-exist-anywhere", False),
    )
    ok = True
    for shape, want in cases:
        got = is_read_url("https://www.linkedin.com" + shape + "/")
        print("    %-34s admitted=%-5s want=%-5s%s"
              % (shape, got, want, "" if got == want else "   <- MISMATCH"))
        ok = ok and got == want
    print("    CONTROL 2 %s" % ("PASS" if ok else "VOID"))
    return ok


def _control_driven_failure():
    print("=== CONTROL 3  THE EXTRACTOR IS SHOWN ABLE TO FAIL "
          "(driven-failing, on purpose)")
    html = _build_synthetic_doc()
    ok = True

    blinded = html.replace('href="', 'data-blind-href="')
    anchors, _ = extract_anchors(blinded)
    print("    break A: rename href= -> data-blind-href= on the whole doc")
    print("      <a href> elements found: %d (expect 0)" % len(anchors))
    if len(anchors) != 0:
        print("      FAIL TO BREAK -- the extractor still found anchors "
              "after the attribute was renamed; this control cannot prove "
              "the extractor reads real structure rather than a fixed stub")
        ok = False
    else:
        print("      broke as expected -- the extractor's answer is a "
              "function of the actual attribute, not a fixed stub")

    retagged = re.sub(r"<a\b", "<b", html, flags=re.I)
    retagged = re.sub(r"</a>", "</b>", retagged, flags=re.I)
    anchors2, _ = extract_anchors(retagged)
    print("    break B: rename <a>/</a> -> <b>/</b>, href left intact")
    print("      <a href> elements found: %d (expect 0)" % len(anchors2))
    if len(anchors2) != 0:
        print("      FAIL TO BREAK -- an href on a non-<a> element was "
              "counted as an anchor")
        ok = False
    else:
        print("      broke as expected -- href alone is not sufficient; "
              "the tag must be <a>")

    print("    CONTROL 3 %s" % ("PASS" if ok else "VOID"))
    if ok:
        print("    both driven-failure cases behaved as a real parser "
              "should -- which is what makes CONTROL 1's PASS mean "
              "something rather than being a tautology")
    return ok


def _control_offset_cross_check_fires():
    print("=== CONTROL 4  THE OFFSET CROSS-CHECK FIRES ON A MANUFACTURED "
          "MISMATCH")
    print("    Context: on the real search-appearances capture, a single "
          "<img> tag's attributes did not fit HTMLParser's own "
          "check_for_whole_start_tag() quoting assumptions, so it returned "
          "an end position 9 characters short of that tag's real end -- "
          "confirmed by direct offset comparison against the raw bytes, "
          "not inferred. Every getpos() call for the rest of that document "
          "then carried the shortfall forward (29 of 29 anchors past that "
          "point were off by 2-54 characters). That is why raw_offset is "
          "computed by _independent_anchor_offsets() instead, cross-checked "
          "by count against HTMLParser's own tag recognition. This control "
          "proves the cross-check itself is wired to fire, by manufacturing "
          "exactly the disagreement it exists to catch.")
    html = _build_synthetic_doc()
    module = sys.modules[__name__]
    original = module._independent_anchor_offsets

    def _lying(raw):
        real = original(raw)
        return real[:-1] if real else real  # silently drop the last one

    module._independent_anchor_offsets = _lying
    ok = False
    try:
        extract_anchors(html)
        print("    FAIL TO BREAK -- extract_anchors() did not raise despite "
              "a manufactured count mismatch; the safety net is not wired")
    except RuntimeError as e:
        ok = "cross-check failed" in str(e)
        print("    raised RuntimeError as designed: %s"
              % ("PASS" if ok else "WRONG MESSAGE: %s" % e))
    finally:
        module._independent_anchor_offsets = original
    # Prove the restore worked and normal operation resumed. extract_anchors()
    # returns EVERY <a> (relevant and not, each tagged) -- filter to relevant
    # before comparing to _EXPECT_TOTAL_RELEVANT_ANCHORS, or this check would
    # compare 11 (all <a> tags) against a count that means something narrower.
    anchors_after, _ = extract_anchors(html)
    n_relevant_after = sum(1 for a in anchors_after if a["relevant"])
    restored = n_relevant_after == _EXPECT_TOTAL_RELEVANT_ANCHORS
    print("    restored correctly after the test (relevant anchors=%d, "
          "expected %d): %s"
          % (n_relevant_after, _EXPECT_TOTAL_RELEVANT_ANCHORS, restored))
    ok = ok and restored
    print("    CONTROL 4 %s" % ("PASS" if ok else "VOID"))
    return ok


def control():
    c1 = _control_extraction_accuracy()
    print()
    c2 = _control_is_read_url_wiring()
    print()
    c3 = _control_driven_failure()
    print()
    c4 = _control_offset_cross_check_fires()
    print()
    if not (c1 and c2 and c3 and c4):
        print("control: at least one control VOID -- do not trust a run "
              "against the real captures until this is fixed")
        return 1
    print("control: all controls passed -- a zero below is a measurement")
    return 0


# ---------------------------------------------------------------------------
# Real measurement
# ---------------------------------------------------------------------------

def load_capture_paths(state_dir):
    paths = {}
    missing = []
    for s in SURFACES:
        p = state_dir / ("cap-%s.html" % s)
        if p.exists():
            paths[s] = p
        else:
            missing.append(s)
    return paths, missing


def main():
    ap = argparse.ArgumentParser(
        description="four premium route candidates, anchor-level, offline")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    args = ap.parse_args()

    if args.control:
        return control()

    state = Path(args.state)
    paths, missing = load_capture_paths(state)
    if missing:
        print("CAPTURES ABSENT (%d of %d): %s"
              % (len(missing), len(SURFACES), ", ".join(missing)))
        print("An absence is not a zero. state dir tried: %s" % state)
        return 2

    t0 = time.time()
    docs = {}
    stats = {}
    for s, p in paths.items():
        data = p.read_bytes()
        stats[s] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
            "mtime": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(p.stat().st_mtime)),
        }
        docs[s] = data.decode("utf-8", errors="replace")

    print("=== 0  CAPTURE IDENTITY -- pinned to the exact bytes read")
    for s in SURFACES:
        st = stats[s]
        print("    %-20s sha256=%s size=%9d  mtime=%s"
              % (s, st["sha256"], st["size"], st["mtime"]))

    parsed = {}
    for s in SURFACES:
        parsed[s] = extract_anchors(docs[s])
    print("    parsed 6 captures in %.2fs" % (time.time() - t0))

    print()
    print("=== 1  FOUR TARGET ROUTES")
    headline = {}
    for route in TARGET_ROUTES:
        route_segs = [x for x in route.split("/") if x]
        n = len(route_segs)
        print()
        print("  -- %s" % route)
        total = 0
        deeper_shapes = {}
        #: The route's last path segment alone, e.g. "recruiter-views" for
        #: /analytics/recruiter-views -- a BARE word census, matching this
        #: repository's own "inmail" convention (16-21 raw, 0 rendered on
        #: this corpus) rather than requiring href="..." syntax. Reported
        #: alongside raw_href_prefix_count because the two answer different
        #: questions and a single real discrepancy was found reconciling
        #: them: this route's bare count and its href-wrapped count are NOT
        #: always equal (search-appearances carries "profile-key-skills" as
        #: a bare substring twice but as a real href once -- the second
        #: occurrence is bundle text, not a second anchor).
        bare_needle = route.rstrip("/").rsplit("/", 1)[-1]
        for s in SURFACES:
            anchors, stripped_total = parsed[s]
            kept = [a for a in anchors if a["relevant"]]
            hits = [a for a in kept if shape_at(a, n) == route]
            raw_c = raw_prefix_count(docs[s], route)
            bare_c = docs[s].count(bare_needle)
            flag = ("   <- bare > href-wrapped: %d occurrence(s) of %r "
                     "outside any href" % (bare_c - raw_c, bare_needle)
                     if bare_c > raw_c else "")
            print("    %-20s anchors=%-3d raw_href_prefix_count=%-4d "
                  "bare_substring(%r)=%-4d stripped_doc_len=%d%s"
                  % (s, len(hits), raw_c, bare_needle, bare_c,
                     stripped_total, flag))
            total += len(hits)
            for h in hits:
                print("        landmarks=%-30s trailing_slash=%-5s "
                      "absolute=%-5s root_relative=%-5s query_params=%s"
                      % (str(h["landmarks"]), h["has_trailing_slash"],
                         h["is_absolute"], h["is_root_relative"],
                         h["query_params"]))
                print("            raw_offset=%d  stripped_offset=%d  "
                      "of stripped_doc_len=%d"
                      % (h["raw_offset"], h["stripped_offset"],
                         stripped_total))
            if not hits:
                top_prefix_segs = route_segs[:1]
                siblings_here = sorted(set(
                    shape_at(a, len(shape8_segments(a["shape8"])))
                    for a in kept
                    if shape8_segments(a["shape8"])[:1] == top_prefix_segs
                ))
                safe_siblings = [safe_shape(x) for x in siblings_here]
                print("        0 anchors. Under /%s on this capture, "
                      "shapes actually drawn: %s"
                      % (top_prefix_segs[0],
                         safe_siblings if safe_siblings else "(none)"))
            # sub-paths: anchors matching this route's own segments with a
            # real, longer, tail.
            for a in kept:
                segs8 = shape8_segments(a["shape8"])
                if segs8[:n] == route_segs and a["n_segments"] > n:
                    deeper_shapes.setdefault(a["safe_shape8"], set()).add(s)
        print("    TOTAL anchors resolving to this shape, all 6 captures: %d"
              % total)
        if deeper_shapes:
            print("    DEEPER sub-paths of this route drawn somewhere:")
            for shp in sorted(deeper_shapes):
                print("        %-52s on %s"
                      % (shp, sorted(deeper_shapes[shp])))
        else:
            print("    DEEPER sub-paths of this route drawn somewhere: none")
        headline[route] = total

    print()
    print("=== 2  SIBLING INVENTORY -- every distinct shape under the "
          "three prefixes, and today's admission verdict")
    prefix_shape_totals = {}
    for prefix in SIBLING_PREFIXES:
        prefix_segs = [x for x in prefix.split("/") if x]
        print()
        print("  -- prefix %s" % prefix)
        shape_surfaces = {}   # safe_shape -> {surface: count}
        shape_true = {}       # safe_shape -> one true (unredacted) shape
        for s in SURFACES:
            anchors, _ = parsed[s]
            for a in anchors:
                if not a["relevant"]:
                    continue
                segs8 = shape8_segments(a["shape8"])
                if segs8[:len(prefix_segs)] != prefix_segs:
                    continue
                true_shape = shape_at(a, len(segs8))
                key = safe_shape(true_shape)
                shape_surfaces.setdefault(key, {}).setdefault(s, 0)
                shape_surfaces[key][s] += 1
                shape_true.setdefault(key, true_shape)
        if not shape_surfaces:
            print("    0 shapes drawn under %s across all 6 captures."
                  % prefix)
            prefix_shape_totals[prefix] = 0
            continue
        for key in sorted(shape_surfaces):
            true_shape = shape_true[key]
            admitted_bare = is_read_url("https://www.linkedin.com" + true_shape)
            admitted_slash = is_read_url(
                "https://www.linkedin.com" + true_shape + "/")
            per_surface = ", ".join(
                "%s:%d" % (s, c) for s, c in sorted(shape_surfaces[key].items()))
            total = sum(shape_surfaces[key].values())
            flag = ("   <- ADMISSION DIFFERS WITH/WITHOUT TRAILING SLASH"
                     if admitted_bare != admitted_slash else "")
            print("    %-46s total=%-3d admitted(bare)=%-5s "
                  "admitted(+slash)=%-5s  [%s]%s"
                  % (key, total, admitted_bare, admitted_slash, per_surface,
                     flag))
        print("    %d distinct shapes under %s" % (len(shape_surfaces), prefix))
        prefix_shape_totals[prefix] = len(shape_surfaces)

    print()
    print("=== 3  RAW-VS-RENDERED DISCIPLINE CHECK, PER PREFIX")
    for prefix in SIBLING_PREFIXES:
        prefix_segs = [x for x in prefix.split("/") if x]
        raw_total = parsed_total = 0
        for s in SURFACES:
            raw_c = raw_prefix_count(docs[s], prefix)
            anchors, _ = parsed[s]
            parsed_c = sum(
                1 for a in anchors
                if a["relevant"]
                and shape8_segments(a["shape8"])[:len(prefix_segs)]
                == prefix_segs)
            raw_total += raw_c
            parsed_total += parsed_c
            flag = "" if raw_c == parsed_c else "   <- GAP"
            print("    %-20s prefix=%-20s raw=%4d  parsed(<a> only)=%4d%s"
                  % (s, prefix, raw_c, parsed_c, flag))
        print("    %-20s TOTAL raw=%4d  parsed=%4d"
              % (prefix, raw_total, parsed_total))

    print()
    print("=== HEADLINE ===")
    for route in TARGET_ROUTES:
        print("    %-38s total_anchors=%d" % (route, headline[route]))
    for prefix in SIBLING_PREFIXES:
        print("    %-38s distinct_shapes=%d"
              % (prefix, prefix_shape_totals[prefix]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
