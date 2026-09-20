"""What does LinkedIn actually DRAW at the events root, control by control?

THE ABSENCE IS ALREADY ESTABLISHED AND THIS FILE DOES NOT RE-ESTABLISH IT.
``_audit/2026-09-05-groups-events-precondition.md`` s8 records, from a live
read with a control firing at both ends of the session, that **no "events you
are registered for" surface exists**: eighteen distinct events across two
sections, fifteen of them recommendations by LinkedIn's own heading and three
under a curated heading the singleton rule redacted. Not one is his
attendance.

That answers what the page is NOT. This asks what it IS, because eleven of
``EVENTS-SURFACE``'s eighteen census rows are WRITES and every one of them
needs a control to aim at. **A row whose control is not drawn on any address
this server may open is not a row waiting for a WriteSpec; it is a row waiting
for an address, and the two are costed differently.**

This reads the gitignored capture. It is OFFLINE -- no browser, no network,
no page load, and therefore no counter of anybody's is spent.

## THE FOUR QUESTIONS, AND WHY EACH IS WORTH A PASS

**Q1 -- WHAT ADDRESSES DOES THE ROOT ITSELF OFFER?** Every ``/events/`` href in
the document, reduced to its path SHAPE. This decides what the ledger's
"allowlist +1" actually has to buy: if LinkedIn links only to one sub-route
from the one address already admitted, then the boundary question is a single
pattern rather than a family, and the argument can be made about that one page
instead of about "events" in the abstract.

**Q2 -- WHAT CONTROLS SIT ON AN EVENT ROW?** Accessible names within a window
of each anchor, shaped and count-redacted. An attend control, a share control
or an overflow menu drawn HERE would mean rows ``N 182``, ``N 185`` and
``N 193`` have a route on an address that is already open. **Their absence
means the opposite, and it is the more likely answer**: this page is a
recommendation strip, and a recommendation strip is not an RSVP surface.

**Q3 -- IS THERE A DROPDOWN IN THE DOCUMENT ALREADY?** LinkedIn ships some
overflow menus into the DOM collapsed rather than building them on press. If
these are there, the menu contents are readable with no press at all, and the
groups wave's deliberately-declined press becomes unnecessary for events. If
they are not, that is the finding, and pressing is the only route -- which is
a separate decision with a separate cost.

**Q4 -- DOES ANY LINK LEAVE THIS PAGE TOWARDS A SELF-SCOPED EVENTS SURFACE?**
The absence in s8 was measured by reading the page's CONTENT. This asks the
NAVIGATION the other way: if LinkedIn drew a "your events" or "manage" route
anywhere, it would be an href, and an href is not a matter of interpretation.
Two instruments answering the same question by different means is the standard
this document set holds itself to.

## WHAT LEAVES THIS PROCESS

Integers, path shapes, and text that has passed BOTH shipped census rules with
a REAL count -- ``census_shape`` then ``census_redact_rare(shape, count)``,
where the count is the term's actual number of occurrences in the document and
never a guess. ``census_redact_rare`` fires at ``count == 1``, so page
furniture that repeats survives and a one-off capitalised run is blanked.

Path shapes are built by SEGMENT REPLACEMENT, not by substring editing: the
segment after ``events`` becomes ``<id>`` whatever it contains, so no
identifier can survive by being shaped like something else.

## THE CONTROLS

**MUST FIRE:** the anchor total must equal 54, the count
``dom.read_surface_census`` measured live on this same page in the same
session. This parses HTML with a regular expression; the census walks a live
DOM. They are different instruments, so agreement is evidence and disagreement
voids every tally below it. The sibling probe's first version failed exactly
this control -- an absolute-href matcher found ZERO of the 54, because this
page writes RELATIVE hrefs -- and printed nothing plausible in the meantime.

**MUST STAY SILENT:** an attribute that cannot exist must be found zero times.
A matcher that finds things everywhere is measuring itself.

**MUST FIRE, SECOND ONE:** ``Q4_MUST_FIRE_NEEDLE`` must be found in at least
one href. This is NOT redundant with the anchor control, and the reason is
measurable rather than argued: ``EVENT_HREF`` is unbounded while ``ANY_HREF``
stops at 400 characters, so an href longer than that is counted by the first
and invisible to the second. Padding the captured hrefs past that bound leaves
the anchor control agreeing at 54 while this needle reports zero.

**AND ALL THREE BRANCH.** Two of them did not until 2026-09-20: their results
were computed, printed with the word FAIL, and then ignored, so the probe
announced its own invalidity and published the tally anyway. They were found by
driving each control into its failing state, which is the only way to find
this -- the code reads correctly, and that is exactly the problem with it.

Usage::

    venv/Scripts/python.exe scripts/_probe_events_surface_shape.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import shape  # noqa: E402

#: The gitignored capture and the live census count it must reproduce.
#: ``.gitignore:140`` matches ``*_probe-*.html``.
CAPTURE = ROOT / "_audit" / "_probe-events-hyd.html"
CENSUS_MEASURED_ANCHORS = 54

#: RELATIVE hrefs, matched by CONTAINMENT. Measured on this very page, not
#: assumed: an absolute matcher finds zero here.
EVENT_HREF = re.compile(r'href="([^"]*/events/[^"]*)"')

#: Every href, for Q4. Bounded so a malformed attribute cannot swallow markup.
ANY_HREF = re.compile(r'href="([^"]{1,400})"')

#: Accessible names. Bounded for the same reason.
LABEL = re.compile(r'aria-label="([^"]{1,120})"')

#: Headings, at every level LinkedIn uses for a section title.
HEADING = re.compile(r"<h([1-4])\b[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)

#: The must-stay-silent control: an attribute no document carries.
IMPOSSIBLE = re.compile(r'aria-nonexistent-attribute="([^"]*)"')

#: Markers for a collapsed menu that is already in the document.
DROPDOWN_MARKERS = (
    "artdeco-dropdown",
    "aria-expanded",
    "aria-haspopup",
    'role="menu"',
    'role="dialog"',
    'role="button"',
    "<button",
)

#: How far after an anchor a control still counts as belonging to its row.
#: Two windows are run and BOTH are printed: a split that moves with the
#: window is an artefact of the window.
LABEL_WINDOWS = (1500, 3000)

#: The must-fire half of Q4's own control. ``/events/`` is on this page by
#: construction, so a needle sweep that reports zero for it is broken rather
#: than informative. NAMED rather than written twice: it was a bare literal in
#: two places, and a control whose needle can drift out of agreement with the
#: table it guards is one rename away from being silently disarmed.
Q4_MUST_FIRE_NEEDLE = "/events/"

#: Route needles for Q4 -- an href that would betray a self-scoped events
#: surface if LinkedIn drew one.
SELF_SCOPED_NEEDLES = (
    Q4_MUST_FIRE_NEEDLE,
    "my-items",
    "myitems",
    "/events/manage",
    "/events/my",
    "registered",
    "attending",
    "network-manager",
)

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def _text(fragment: str) -> str:
    return WS.sub(" ", TAG.sub(" ", fragment)).strip()


def _safe(raw: str, count: int) -> str:
    """Text through BOTH shipped census rules, with its real count."""
    return shape.census_redact_rare(shape.census_shape(raw), count)


def _path_shape(href: str) -> str:
    """The path shape of an href, by SEGMENT REPLACEMENT.

    The segment following ``events`` is replaced wholesale, so nothing of an
    identifier can survive by resembling something else. Query and fragment
    are dropped and reported separately as a count.
    """
    path = href.split("?")[0].split("#")[0]
    segments = [segment for segment in path.split("/") if segment]
    if "events" in segments:
        index = segments.index("events")
        if len(segments) > index + 1:
            segments = segments[: index + 1] + ["<id>"] + segments[index + 2:]
    trailing = "/" if path.endswith("/") else ""
    return "/" + "/".join(segments) + trailing


def main() -> int:
    print("=== THE EVENTS ROOT, CONTROL BY CONTROL. Offline over the capture.")
    if not CAPTURE.is_file():
        print(f"    CAPTURE ABSENT ({CAPTURE.name}). Nothing to analyse, and")
        print("    nothing below this line is a reading.")
        return 2
    html = CAPTURE.read_text(encoding="utf-8", errors="replace")
    print(f"    {len(html)} chars")

    # ---------------------------------------------------------- THE CONTROLS
    # EVERY ONE OF THESE BRANCHES, and that is the whole point of this block.
    # Until 2026-09-20 two of the three were COMPUTED, PRINTED and then
    # IGNORED: this probe would print the word FAIL and certify its tally in
    # the same breath. A result that nothing branches on is not a control, it
    # is a sentence. Both were found by driving them into their failing states,
    # not by reading the code -- reading it is how they survived review.
    silent = len(IMPOSSIBLE.findall(html))
    print(f"\n--- CONTROL, must stay silent: {silent} "
          f"{'PASS' if silent == 0 else 'FAIL'}")
    if silent:
        print("    VOID. An attribute that cannot exist was found, so this")
        print("    matcher is matching itself, and every tally below it would")
        print("    be a reading of the instrument rather than of the page.")
        return 1

    anchors = [(m.start(), m.group(1)) for m in EVENT_HREF.finditer(html)]
    agree = len(anchors) == CENSUS_MEASURED_ANCHORS
    print(f"--- CONTROL, must fire: {len(anchors)} anchors, census measured "
          f"{CENSUS_MEASURED_ANCHORS} -- {'AGREE' if agree else 'DISAGREE'}")
    if not agree:
        print("    VOID. This parse does not see what the census saw, so no")
        print("    tally below it is a reading. Fix the matcher, not the page.")
        return 1

    # Q4's needle sweep reads a DIFFERENT population from the anchor control
    # above: ``ANY_HREF`` is bounded to 400 characters and ``EVENT_HREF`` is
    # not. So the two CAN disagree, and the disagreement is not hypothetical --
    # padding every event href past that bound leaves the anchor control
    # AGREEING at 54 while this needle reports ZERO, measured 2026-09-20. The
    # controls are therefore not redundant, which is why this one is hoisted
    # here and branched on, where its own text always said it belonged: "a
    # zero here voids this whole sweep". It never did.
    hrefs = [m.group(1) for m in ANY_HREF.finditer(html)]
    must_fire = sum(1 for href in hrefs if Q4_MUST_FIRE_NEEDLE in href)
    print(f"--- CONTROL, must fire: {must_fire} of {len(hrefs)} hrefs carry "
          f"{Q4_MUST_FIRE_NEEDLE!r} -- "
          f"{'FIRES' if must_fire else 'SILENT'}")
    if not must_fire:
        print("    VOID. The needle sweep cannot see the one address this page")
        print("    is built out of, so a zero against any OTHER needle below")
        print("    would be a fact about the matcher, not about LinkedIn.")
        return 1

    # ---------------------------------------------------------------- Q1
    print("\n=== Q1  WHAT ADDRESSES DOES THE ROOT OFFER?")
    shapes: dict[str, int] = {}
    queried = 0
    for _offset, href in anchors:
        if "?" in href or "#" in href:
            queried += 1
        key = _path_shape(href)
        shapes[key] = shapes.get(key, 0) + 1
    for key, count in sorted(shapes.items(), key=lambda item: (-item[1], item[0])):
        print(f"    {count:>4}  {key}")
    print(f"    distinct path shapes: {len(shapes)}")
    print(f"    hrefs carrying a query or fragment: {queried}")

    identifiers = {
        _path_shape(href) + "|" + href.split("?")[0].split("#")[0]
        for _offset, href in anchors
    }
    print(f"    DISTINCT EVENT ADDRESSES: {len(identifiers)} "
          "(counted, never printed)")

    # ---------------------------------------------------------------- Q2
    print("\n=== Q2  WHAT CONTROLS SIT ON AN EVENT ROW?")
    labels = [(m.start(), m.group(1)) for m in LABEL.finditer(html)]
    print(f"    aria-labels in the whole document: {len(labels)}")
    label_tally: dict[str, int] = {}
    for _offset, text in labels:
        label_tally[text] = label_tally.get(text, 0) + 1

    for window in LABEL_WINDOWS:
        near: dict[str, int] = {}
        rows_with_any = 0
        for offset, _href in anchors:
            found = [
                text for position, text in labels
                if offset <= position < offset + window
            ]
            if found:
                rows_with_any += 1
            for text in found:
                key = _safe(text, label_tally.get(text, 1))
                near[key] = near.get(key, 0) + 1
        print(f"    WINDOW {window}: {rows_with_any} of {len(anchors)} anchors "
              f"have a labelled control after them")
        for key, count in sorted(near.items(), key=lambda item: (-item[1], item[0])):
            print(f"        {count:>4}  {key!r}")
        if not near:
            print("        NONE. No labelled control follows any event anchor")
            print("        within this window -- so no attend, share or")
            print("        overflow control is drawn per row on this page.")

    # ---------------------------------------------------------------- Q3
    print("\n=== Q3  IS A COLLAPSED MENU ALREADY IN THE DOCUMENT?")
    for marker in DROPDOWN_MARKERS:
        print(f"    {html.count(marker):>5}  {marker}")

    # ---------------------------------------------------------------- Q4
    print("\n=== Q4  DOES ANY HREF LEAVE TOWARDS A SELF-SCOPED EVENTS SURFACE?")
    # ``hrefs`` and the must-fire tally were computed with the controls above,
    # because a control that runs after the thing it guards has already been
    # printed can only ever annotate a reading it failed to prevent.
    print(f"    hrefs in the document: {len(hrefs)}")
    for needle in SELF_SCOPED_NEEDLES:
        hits = sum(1 for href in hrefs if needle in href)
        note = ""
        if needle == Q4_MUST_FIRE_NEEDLE:
            note = "  <- the must-fire control, checked and branched on above"
        print(f"    {hits:>5}  {needle}{note}")

    # ---------------------------------------------------------------- headings
    print("\n=== SECTION HEADINGS (shaped, count-redacted)")
    headings = [
        (m.start(), _text(m.group(2))) for m in HEADING.finditer(html)
    ]
    headings = [(offset, text) for offset, text in headings if text]
    heading_tally: dict[str, int] = {}
    for _offset, text in headings:
        heading_tally[text] = heading_tally.get(text, 0) + 1
    for offset, text in headings:
        print(f"    at {offset:>8}  "
              f"{_safe(text, heading_tally.get(text, 1))!r}")
    print(f"    headings: {len(headings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
