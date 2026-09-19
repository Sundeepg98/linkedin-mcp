"""Classify a page's anchors by ROUTE SHAPE. No href crosses the boundary.

Three surfaces in the read tail need the same thing and none of them can have
it from the shipped census: job collections, school pages, premium job
surfaces. ``_audit/2026-09-19-read-tail.md`` section 8 measured why.

## WHY ``read_surface_census`` CANNOT SERVE, and why that is correct

It carries ``has_href`` and ``href_shape`` and **never hands out a raw href by
construction.** Asked for ``href`` it returns a value indistinguishable from
absence -- measured, ``(no href)`` on **147 of 147** controls of a page made
entirely of links, which presented as a clean zero rather than as an error.
Shaping is precisely what makes it unusable as a parser, and that is the shaper
doing its job.

## AND THE THING A NAIVE ANCHOR READER WOULD DO IS THE ONE THING FORBIDDEN

**An anchor reader that can see hrefs can see ``/in/<slug>``, and a slug is a
name.** So this module does not see them either.

The mechanism is ``menus.py``'s, applied to routes instead of labels: the
vocabulary is shipped INTO the page, the page answers with an **integer index
into a table defined in this file**, and the mapping back happens in Python.
**No raw href is shaped, redacted, or present in this process.**

## THE OUTPUT ALPHABET IS CLOSED, AND IT ANSWERS "WHICH SHAPE", NEVER "WHICH"

Every string this module can emit is a literal in :data:`ROUTE_CLASSES`. The
question it answers is *which shape is this anchor*, from an enumerated set --
never *what is this anchor*. A member profile is COUNTED and never described,
which is ``groups.py``'s rule arriving one level up.

## THE SEGMENT RULE, AND IT IS ``menus.py``'S SCAR GENERALISED

``menus.py`` shipped a matcher where ``classify("Star Anise")`` returned
``star``, because containment was applied at every phrase length and **the
hazard had been treated as a property of one WORD instead of a property of
every single-word term.** Its fix: a single-word phrase must be the WHOLE
label, because A NAME ADDS TOKENS.

**The same hole exists here one level over, and the MEASURED harm was worse
than the one predicted.** A route term tested by CONTAINMENT matches inside any
segment::

    /company/star-anise-school/   -> school_page     (WRONG)

**AND THE PREDICTION THAT PRODUCED THIS RULE WAS ITSELF REFUTED, which is why
the number is written down.** The expectation was that containment would move a
name-bearing anchor OUT of ``member_profile``. Run against
:func:`control_fixture` in a page on 2026-09-19 it did the opposite:

    member_profile   1 -> 4      help_article  1 -> 0
                                 messaging     1 -> 0
                                 school_page   1 -> 0

because the route term ``in`` is a substring of ``linkedin``, ``messaging`` and
``institute``. A help article, a messaging thread and a school page were all
reclassified as member profiles.

**Over-reporting the hazard class is not the safe direction.** It makes the one
count a caller must never publish per-record wrong by 4x, and tells a caller a
page is full of people when it holds one. So:

    A ROUTE TERM MUST BE A WHOLE PATH SEGMENT AT A FIXED POSITION.
    Never a substring of one, and never at a floating position.

That closes the class rather than the instance, exactly as requiring whole-label
equality did for ``menus.py``.

## NO HREF, SLUG OR ID IS A PARAMETER OR A RETURN VALUE OF ANY FUNCTION HERE

Asserted on ``inspect.signature`` in ``tests/test_anchors.py``, the way
``groups.py`` does it. :func:`read_anchors` is the only function that touches a
page and returns indices and integers; :func:`tally` -- the function a caller
publishes -- takes INDICES and cannot be handed an address even by mistake.

## WHAT IT DOES NOT CLAIM

* **Not that it saw every anchor.** It reports what the document held at one
  moment, and these surfaces move: the collections page's control count went
  75 -> 93 across five minutes on 2026-09-19. Design against the SHAPE, and
  treat any count as a reading with a timestamp.
* **Not that an anchor behind a disclosure exists or does not.** Nothing here
  presses anything. An anchor that only renders after a disclosing press is
  invisible to this module and that is a stated limit, not a measurement.
"""

from __future__ import annotations

from typing import Any, Iterable

#: THE CLOSED OUTPUT ALPHABET. Order is the contract: the page returns a
#: POSITION in this tuple, so reordering silently renames every reading ever
#: taken. ``tests/test_anchors.py`` pins it.
#:
#: ``member_profile`` IS THE HAZARD CLASS and it is first on purpose -- it is
#: the one whose entity segment is a NAME, so it is counted and never
#: described, and anything that would misclassify INTO or OUT OF it is the
#: defect this module's segment rule exists to prevent.
ROUTE_CLASSES: tuple[str, ...] = (
    "member_profile",
    "company_page",
    "school_page",
    "job_posting",
    "job_collection",
    "job_search",
    "premium_surface",
    "feed_update",
    "messaging",
    "help_article",
    "other_internal",
    "external",
    "no_href",
)

#: ``(class token, first segment, required second segment or "")``. Matching is
#: SEGMENT EQUALITY at these FIXED POSITIONS -- see the module docstring for the
#: scar this closes. A route needing a third segment would need a deliberate
#: edit here, which is the point.
ROUTE_TABLE: tuple[tuple[str, str, str], ...] = (
    ("member_profile", "in", ""),
    ("company_page", "company", ""),
    ("school_page", "school", ""),
    ("job_posting", "jobs", "view"),
    ("job_collection", "jobs", "collections"),
    ("job_search", "jobs", "search"),
    ("premium_surface", "premium", ""),
    ("feed_update", "feed", "update"),
    ("messaging", "messaging", ""),
    ("help_article", "help", ""),
)

#: A refusal, and a literal like everything else here.
UNCLASSIFIED = "other_internal"

_HOST = "www.linkedin.com"

#: The in-page classifier. **THE ROUTE TABLE IS AN ARGUMENT**, so this function
#: is the entire boundary crossing and its return type is the safety property:
#: integers and booleans, never a string from the document.
_CLASSIFY_IN_PAGE = """
(args) => {
  const table = args.table || [];
  const host = args.host || "";
  const html = args.html || "";
  const classCount = args.classCount || 0;
  const indexOfClass = (token) => {
    for (let i = 0; i < args.classes.length; i += 1) {
      if (args.classes[i] === token) return i;
    }
    return -1;
  };
  // THE CONTROL PATH. When html is supplied the SAME classifier runs against a
  // DETACHED container, so the demonstration that it CAN classify -- and that
  // it refuses the adversarial cases -- costs no navigation. A classifier that
  // returns one class for everything is indistinguishable from a broken one.
  let root = document;
  if (html) {
    root = document.createElement("div");
    root.innerHTML = html;
  }
  const anchors = Array.from(root.querySelectorAll("a"));
  const counts = new Array(classCount).fill(0);
  let numericEntity = 0;
  let nonNumericEntity = 0;
  for (const node of anchors) {
    const raw = node.getAttribute("href");
    if (!raw) { counts[indexOfClass("no_href")] += 1; continue; }
    let path = raw;
    let isExternal = false;
    if (raw.indexOf("//") !== -1) {
      // A protocol-relative or absolute url. Anything not on the LinkedIn host
      // is EXTERNAL and is counted without being looked at further.
      const afterScheme = raw.slice(raw.indexOf("//") + 2);
      const slash = afterScheme.indexOf("/");
      const hostPart = slash === -1 ? afterScheme : afterScheme.slice(0, slash);
      if (hostPart !== host) isExternal = true;
      path = slash === -1 ? "/" : afterScheme.slice(slash);
    }
    if (isExternal) { counts[indexOfClass("external")] += 1; continue; }
    // SEGMENTS, and the query and fragment are DROPPED BEFORE ANYTHING IS
    // READ -- groups.py's rule: a part that is never read cannot carry
    // anything. /groups/123/?invitedBy=<token> survives shaping with the
    // token intact, and this is the same escape one level over.
    const q = path.indexOf("?"); if (q !== -1) path = path.slice(0, q);
    const h = path.indexOf("#"); if (h !== -1) path = path.slice(0, h);
    const segments = path.split("/").filter((s) => s.length > 0);
    let matched = -1;
    for (const row of table) {
      const token = row[0], first = row[1], second = row[2];
      // SEGMENT EQUALITY AT A FIXED POSITION. Never a substring, never
      // floating -- see this module's docstring for the scar.
      if (segments.length < 1 || segments[0] !== first) continue;
      if (second) {
        if (segments.length < 2 || segments[1] !== second) continue;
      }
      matched = indexOfClass(token);
      break;
    }
    if (matched === -1) { counts[indexOfClass("other_internal")] += 1; continue; }
    counts[matched] += 1;
    // THE ENTITY SEGMENT'S SHAPE, never its value. groups.py's numeric rule:
    // a non-numeric segment is a slug, and a slug is a name.
    const entityAt = table.find((r) => indexOfClass(r[0]) === matched);
    const position = entityAt && entityAt[2] ? 2 : 1;
    if (segments.length > position) {
      if (/^[0-9]+$/.test(segments[position])) numericEntity += 1;
      else nonNumericEntity += 1;
    }
  }
  // INTEGERS ONLY. Every field below is a number, by construction.
  return {
    anchors: anchors.length,
    counts: counts,
    numeric_entity: numericEntity,
    non_numeric_entity: nonNumericEntity,
  };
}
"""


async def read_anchors(page: Any, html: str = "") -> dict[str, Any]:
    """Classify the page's anchors. Returns COUNTS PER CLASS and integers.

    THE ONLY FUNCTION HERE THAT TOUCHES A PAGE. What crosses the boundary back
    is a list of counts positionally aligned to :data:`ROUTE_CLASSES`.

    ``html`` IS THE CONTROL PATH and is not a reading of anything -- it runs the
    same classifier against a detached container so :func:`control_fixture` can
    prove the classifier works and refuses the adversarial cases, at no page
    load. It is a parameter of the READER, never of :func:`tally`.
    """
    raw = await page.evaluate(
        _CLASSIFY_IN_PAGE,
        {
            "table": [list(row) for row in ROUTE_TABLE],
            "classes": list(ROUTE_CLASSES),
            "classCount": len(ROUTE_CLASSES),
            "host": _HOST,
            "html": html or "",
        },
    )
    counts = list((raw or {}).get("counts") or [])
    return {
        "anchors_seen": int((raw or {}).get("anchors") or 0),
        "counts": [int(value) for value in counts],
        "numeric_entity": int((raw or {}).get("numeric_entity") or 0),
        "non_numeric_entity": int((raw or {}).get("non_numeric_entity") or 0),
    }


def term_for(index: int) -> str:
    """One index -> one literal. Out of range REFUSES rather than clamping.

    A clamp would silently rename one route class to another -- and the class
    at index 0 is ``member_profile``, so a clamp could rename a name-bearing
    anchor into an organisation. Never clamped.
    """
    if 0 <= index < len(ROUTE_CLASSES):
        return ROUTE_CLASSES[index]
    return "index_out_of_range"


def tally(counts: Iterable[int]) -> dict[str, Any]:
    """COUNTS BY CLASS. Its parameter is INTEGERS -- an address cannot reach it.

    A short list is reported as such rather than padded, because a missing
    class and a zero-count class are different answers and collapsing them is
    how a reader says "none of those" when it means "I was not told".
    """
    values = [int(value) for value in counts]
    by_class = {
        ROUTE_CLASSES[position]: value
        for position, value in enumerate(values)
        if position < len(ROUTE_CLASSES)
    }
    overflow = max(0, len(values) - len(ROUTE_CLASSES))
    return {
        "by_class": dict(sorted(by_class.items())),
        "classes_not_reported": max(0, len(ROUTE_CLASSES) - len(values)),
        "positions_beyond_the_alphabet": overflow,
        "total_classified": sum(by_class.values()),
        # NAMED SEPARATELY because it is the number a caller must not publish
        # per-record. A count of member anchors is his own page's shape; the
        # anchors themselves are other people.
        "member_profile_anchors": by_class.get("member_profile", 0),
    }


def emitted_alphabet() -> frozenset[str]:
    """Every string this module can publish. Asserted over adversarial input."""
    return frozenset(ROUTE_CLASSES) | {"index_out_of_range"}


def control_fixture() -> str:
    """Anchors that MUST classify, including the ones that must NOT misclassify.

    **THE ADVERSARIAL CASES ARE THE POINT.** A classifier that returns one
    class for everything looks exactly like a working one on a page that
    happens to be uniform, so the fixture carries the two shapes that convicted
    the containment design:

    * ``/company/star-anise-school/`` -- a slug CONTAINING a route term, which
      a containment matcher calls ``school_page``. It is a company.
    * ``/in/<a slug containing 'company'>`` -- the same trick aimed at the
      hazard class, and the worse of the two: it would move a name-bearing
      anchor OUT of ``member_profile``.

    **THE SLUGS ARE SYNTHETIC AND DELIBERATELY NOT PEOPLE.** ``menus.py`` uses
    a spice for the same reason: a tracked file may not carry a third party's
    name even as an illustration, and the substitute demonstrates the same
    thing -- a route term sitting inside a segment that is not a route.
    """
    return (
        '<a href="/in/star-anise-company-ltd/">a</a>'
        '<a href="/company/star-anise-school/">b</a>'
        '<a href="/school/some-institute/">c</a>'
        '<a href="/jobs/view/1234567890/">d</a>'
        '<a href="/jobs/collections/recommended/">e</a>'
        '<a href="/jobs/search/?keywords=x">f</a>'
        '<a href="/premium/my-premium/">g</a>'
        '<a href="/feed/update/some-urn/">h</a>'
        '<a href="/messaging/thread/">i</a>'
        '<a href="/help/linkedin/answer/12345">j</a>'
        '<a href="/some/unknown/route/">k</a>'
        '<a href="https://example.invalid/elsewhere">l</a>'
        '<a>m</a>'
    )


#: What :func:`control_fixture` must produce. Written out so the control has an
#: EXPECTATION rather than only an output -- a control whose result nobody
#: predicted cannot fail.
CONTROL_EXPECTATION: dict[str, int] = {
    "member_profile": 1,
    "company_page": 1,
    "school_page": 1,
    "job_posting": 1,
    "job_collection": 1,
    "job_search": 1,
    "premium_surface": 1,
    "feed_update": 1,
    "messaging": 1,
    "help_article": 1,
    "other_internal": 1,
    "external": 1,
    "no_href": 1,
}
