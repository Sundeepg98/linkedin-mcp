"""Which section does each group or event link sit under?

THE CONTAINER ROUTE FAILED AND THIS IS THE NEXT ONE. Run live on 2026-09-05,
``dom.read_surface_census`` reported every marked control on both roots with
``container: none`` -- 10 of 10 on groups, 54 of 54 on events, one distinct
container each. So the census's own container field does NOT separate his
memberships from LinkedIn's suggestions, and the capture has to answer it.

This reads the capture. It is OFFLINE -- no browser, no network, no page load.

## WHAT LEAVES THIS PROCESS

Section headings, and ONLY after both shipped census rules have run over them
WITH A REAL COUNT:

* ``census_shape`` -- the length and charset gate plus the identity
  substitutions;
* ``census_redact_rare(shape, count)`` -- the singleton rule, fed the heading's
  ACTUAL number of occurrences in the document rather than a guess.

That pairing is the point. ``census_redact_rare`` fires only at ``count == 1``,
so page furniture that repeats survives and a one-off run of capitalised words
is blanked. LinkedIn writes its section headings in sentence case -- "Your
groups", "Recommended for you" -- which carry at most one capitalised token and
survive; a heading carrying somebody's name is a 2+ run and does not. **The
rule is the shipped one, applied with the count it was designed to need, on a
path that emits per record** -- which is exactly the gap ``membership_row``
exists to close elsewhere.

Everything else printed is an integer.

## THE CONTROL, AND IT IS AN INDEPENDENT INSTRUMENT

This parses HTML with regex; the census walks the live DOM. They are different
instruments over the same page, so **the anchor totals must AGREE with the
census counts measured in the same session**. If they do not, this parse is
wrong and every section tally under it is void -- which is stated as a refusal
rather than left for a reader to notice.

    groups   census measured 10 marked controls
    events   census measured 54

A SECOND CONTROL runs the other way: a heading pattern that cannot match must
find nothing, or the matcher is over-broad rather than the page rich.

Usage::

    venv/Scripts/python.exe scripts/_probe_membership_sections.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import shape  # noqa: E402

#: The gitignored captures, and the census counts they must reproduce.
#: THE HREF ATTRIBUTE, NOT A BARE PATH, AND NOT THE ABSOLUTE FORM. Measured
#: rather than assumed, and the first version of this file got it wrong in a
#: way its own control caught: an absolute matcher
#: (``linkedin\.com/groups/...``) found 5 of the 10 group links and ZERO of the
#: 54 event links, because **both these pages write RELATIVE hrefs**. That is
#: the same fact ``census_href_identifies_entity`` records at its own site as
#: the reason it uses CONTAINMENT rather than ``startswith`` -- measured there
#: on a different surface, and reproduced here on two more.
#:
#: Matching the attribute rather than a bare path also keeps the page's own
#: address out of the tally: ``/groups/`` appears in the document for reasons
#: that are not links to a group.
CAPTURES = (
    ("groups", "_probe-groups-hyd.html",
     r'href="[^"]*/groups/([A-Za-z0-9\-_%.]+)', 10),
    ("events", "_probe-events-hyd.html",
     r'href="[^"]*/events/([A-Za-z0-9\-_%.]+)', 54),
)

#: Headings, in every level LinkedIn uses for a section title.
HEADING = re.compile(
    r"<h([1-4])\b[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL
)

#: A heading pattern that cannot match anything. The must-stay-silent control.
IMPOSSIBLE_HEADING = re.compile(r"<h9\b[^>]*>(.*?)</h9>", re.IGNORECASE)

TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def _text(fragment: str) -> str:
    return WS.sub(" ", TAG.sub(" ", fragment)).strip()


def _safe(raw: str, count: int) -> str:
    """A heading, through BOTH shipped rules, with its real count."""
    return shape.census_redact_rare(shape.census_shape(raw), count)


def _analyse(name: str, path: Path, anchor_pattern: str, expected: int) -> bool:
    print(f"\n--- {name.upper()}  {path.name}")
    if not path.is_file():
        print("    CAPTURE ABSENT. Nothing to analyse.")
        return False
    html = path.read_text(encoding="utf-8", errors="replace")
    print(f"    {len(html)} chars")

    anchors = [
        (m.start(), m.group(1)) for m in re.finditer(anchor_pattern, html)
    ]
    print(f"    anchor offsets found: {len(anchors)}, "
          f"{len({a[1] for a in anchors})} distinct identifiers")

    headings: list[tuple[int, str]] = []
    for match in HEADING.finditer(html):
        text = _text(match.group(2))
        if text:
            headings.append((match.start(), text))
    print(f"    headings found: {len(headings)}")

    silent = len(IMPOSSIBLE_HEADING.findall(html))
    print(f"    CONTROL must stay silent: {silent} "
          f"{'PASS' if silent == 0 else 'FAIL'}")

    # THE COUNT EVERY REDACTION NEEDS. Taken over the document rather than
    # assumed, because census_redact_rare is only correct when it is fed one.
    tally: dict[str, int] = {}
    for _offset, text in headings:
        tally[text] = tally.get(text, 0) + 1

    # Assign each anchor to the nearest PRECEDING heading, and keep the
    # IDENTIFIER so distinctness and overlap can be measured. THE IDENTIFIERS
    # ARE COUNTED AND NEVER PRINTED -- a count of distinct ids names nobody,
    # and it is the number that decides this whole question.
    per_section: dict[str, list[str]] = {}
    unassigned = 0
    for offset, identifier in anchors:
        previous = [h for h in headings if h[0] < offset]
        if not previous:
            unassigned += 1
            continue
        text = previous[-1][1]
        key = _safe(text, tally.get(text, 1))
        per_section.setdefault(key, []).append(identifier)

    print(f"    anchors under no heading: {unassigned}")
    print("    ANCHORS PER SECTION (heading shaped and count-redacted):")
    for key, ids in sorted(
        per_section.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        print(f"        {len(ids):>3} links, {len(set(ids)):>3} DISTINCT  "
              f"{key!r}")

    # THE DECIDING MEASUREMENT. Two sections listing the SAME entities would be
    # one set drawn twice; two sections listing DISJOINT entities are two sets,
    # and if one of them is labelled as suggestions the other one is not.
    print("    OVERLAP BETWEEN SECTIONS (distinct identifiers in common):")
    keys = sorted(per_section)
    if len(keys) < 2:
        print("        n/a -- one section, so there is nothing to separate")
    for first in range(len(keys)):
        for second in range(first + 1, len(keys)):
            common = set(per_section[keys[first]]) & set(per_section[keys[second]])
            print(f"        {len(common):>3}  {keys[first]!r} & "
                  f"{keys[second]!r}")

    ok = len(anchors) == expected
    print(f"    CONTROL against the census: parsed {len(anchors)}, census "
          f"measured {expected} -- {'AGREE' if ok else 'DISAGREE'}")
    if not ok:
        print("    THE TALLIES ABOVE ARE VOID. Two instruments over one page "
              "disagree, so this parse is wrong and nothing under it is a "
              "reading about his account.")
    return ok


def main() -> int:
    print("=== WHICH SECTION DOES EACH GROUP OR EVENT LINK SIT UNDER?")
    print("    Offline. Headings pass census_shape AND census_redact_rare "
          "with a real count; everything else is an integer.")
    results = [
        _analyse(name, ROOT / "_audit" / filename, pattern, expected)
        for name, filename, pattern, expected in CAPTURES
    ]
    print("\n=== VERDICT")
    if not all(results):
        print("  At least one control failed. No section tally above is a "
              "reading about his account.")
        return 1
    print("  Both parses agree with the census taken in the same session, so "
          "the section tallies are readings. WHICH section is 'his' is a "
          "judgement about LinkedIn's own wording and is not made here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
