"""Which entity kinds can carry a name PAST the census shaper, and which cannot?

THE QUESTION IS A PRECONDITION FOR A BOUNDARY CHANGE, NOT A CURIOSITY.
`/in/me/details/interests/` is REFUSED-NO-PATTERN while its three siblings
`/in/me/details/(skills|experience|education)/` are ALLOWED -- measured
2026-09-04. Adding `interests` to that alternation is one word, and the ONLY
thing that makes it safe is that whatever a third party's name looks like on
that page, the shape layer refuses it. **That has to be established rather
than assumed**, and the reason is the disclosure lesson this repo learned
twice in one day: a privacy argument is scoped to a SET OF STRINGS, never to
a kind of field. "Companies are already published" is a true sentence about
companies and says nothing about the other four things that tab lists.

THE INTERESTS TAB ENUMERATES FIVE KINDS OF ENTITY, and they are not one
question:

    Top Voices    people          -> /in/<slug>
    Companies     organisations   -> /company/<slug>
    Groups        groups          -> /groups/<id>
    Newsletters   publications    -> /newsletters/<slug>
    Schools       institutions    -> /school/<slug>

Companies are SETTLED BY PRECEDENT -- `linkedin_followed_companies` ships and
publishes them. People are the case every guard in this module was built for.
The other three have never been asked about, and one of them is dangerous in a
way the other two are not: **a newsletter is authored BY A PERSON, and its
slug and its title routinely carry that person's name.**

## The two guards, and the exact gap between them

    census_redact_rare(shape, count)   blanks a capitalised run -- BUT ONLY
                                       when count == 1. It returns the shape
                                       UNCHANGED for count != 1, in its first
                                       line. That is deliberate and documented:
                                       furniture repeats and a member does not.

    census_href_identifies_entity()    refuses on the STRUCTURE of the control
                                       instead, and does not depend on the
                                       count premise -- which is exactly why it
                                       was added. Its marker set is
                                       `_CENSUS_ENTITY_HREFS`, and that tuple
                                       has TWO members: /in/<member> and
                                       /company/<company>.

**So an entity that appears TWICE on a surface escapes the count rule, and if
its href is not one of those two markers it escapes the structural rule too.**
Two escapes, one name. That is the hole this file measures.

COUNT == 2 IS NOT AN EXOTIC INPUT. `census_href_identifies_entity`'s own
docstring names it as the commonest control on a feed -- "a member who appears
twice, posts twice, or is linked from both a card header and a comment, merges
to count == 2, the singleton cap never fires, and the name ships verbatim.
Measured on this implementation, not imagined." This file asks whether the fix
for that measurement covers the entity kinds nobody has looked at.

## How to read the output

Every row is run at count == 1 AND count == 2, because the answer differs and a
table showing only one of them would publish a false all-clear. A row is RED
when the needle SURVIVES into the published shape.

TWO CONTROLS, AND THEY FAIL IN OPPOSITE DIRECTIONS:

    MUST-REDACT   a person behind /in/<slug>. If this survives, the guard is
                  broken and every other row is uninterpretable.
    MUST-SURVIVE  a furniture label with no href. If this is redacted, the
                  shaper is blanking its own vocabulary and a table of
                  redactions proves nothing -- a redactor that redacts
                  everything certifies nothing, exactly as a check that cannot
                  fail certifies nothing.

## Bounds

**PURE. NO BROWSER, NO PAGE LOAD, NO NETWORK, NO MCP CALL.** It imports
`linkedin_server.shape` and calls three functions.

**EVERY PERSON NAME AND SLUG HERE IS INVENTED AND ALREADY DECLARED** in
`tests/test_a_person_name_is_never_a_literal.py::INVENTED_NAMES`, held in the
constants that test names. Nothing new is introduced, so no new claim about a
name being invented is made by this file.

**NO OUTPUT PATH.** It writes nothing.

Run:  python scripts/_probe_interests_entity_shaping.py
      python scripts/_probe_interests_entity_shaping.py <candidate-package-root>
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import shape  # noqa: E402


def _use_candidate(root: str) -> None:
    """Rebind the module-global `shape` to a CANDIDATE package root.

    WHY A CANDIDATE ROOT EXISTS AT ALL. `linkedin_server/` is a shared tree
    with other waves writing in it, and the RED/GREEN pair this probe exists
    to produce must be taken against the SAME table with only the shaper
    differing. Pointing it at a patched COPY gets that pair without editing a
    file another wave is holding -- and it loads the real patched module
    rather than a model of it, which is the only version worth having. A probe
    that models the guard instead of calling it measures the model, and this
    file's author made exactly that mistake at a terminal the same hour.

    IT IS READ INSIDE `main` AND NOT AT MODULE LEVEL, deliberately. An earlier
    draft read `sys.argv[1]` where the imports are, which under pytest would
    have inserted a PYTEST ARGUMENT into `sys.path` on import --
    `tests/test_scripts_are_import_safe.py` asserts that importing a script
    does nothing, and reaching for argv at import time is doing something.
    """
    global shape
    import importlib

    # REFUSE A ROOT THAT IS NOT ONE, rather than falling back in silence.
    # An import that misses simply resolves to the repository's own package
    # and the run reports GREEN -- a probe measuring the wrong shaper and
    # saying nothing about it. Caught when a typo'd candidate path produced a
    # confident pass.
    candidate = Path(root) / "linkedin_server" / "shape.py"
    if not candidate.is_file():
        raise SystemExit(
            "candidate root %r holds no linkedin_server/shape.py -- refusing "
            "to run, because falling back to the repository's own shaper "
            "would report a pass for a file that was never loaded." % root
        )
    sys.path.insert(0, root)
    importlib.invalidate_caches()
    for name in [n for n in list(sys.modules) if n.startswith("linkedin_server")]:
        del sys.modules[name]
    shape = importlib.import_module("linkedin_server.shape")

#: THE NEEDLES. Invented, and every one already listed in
#: `tests/test_a_person_name_is_never_a_literal.py::INVENTED_NAMES`, held in
#: the constants that test names. This file adds no name to the repository and
#: makes no new claim that a name is invented.
MEMBER_NAME = "Grace Hopper"
OTHER_AUTHOR = "Savita Krishnan"
MEMBER_SLUG = "priya-sharma-12ab34"
OTHER_SLUG = "alex-r-12ab34"

#: THE ROWS, and every href is a COMPLETE LITERAL rather than a formatted one.
#:
#: BOTH OF THOSE PROPERTIES WERE FORCED BY THIS REPOSITORY'S OWN GUARDS, on
#: this file, and each caught a real defect rather than a style preference:
#:
#:   `test_scripts_are_import_safe` refused an earlier draft that built a slug
#:   with `.replace(" ", "-")` inside this tuple. That is a call executing at
#:   IMPORT time, and importing a script must do nothing.
#:
#:   `test_no_committed_identity` refused this file's first newsletter id: a
#:   TEN-DIGIT run opening with a 7, which is an Indian mobile number's shape.
#:   A synthetic constant wearing that shape is exactly what that guard exists
#:   to keep out of a tracked file -- and the number is not repeated here
#:   either, because the guard reads prose as well as code and it is right to.
#:   The id used below is SIX digits -- the minimum
#:   `_CENSUS_LONG_DIGITS` reduces -- so the probe still exercises the digit
#:   rule while wearing no real identifier's shape.
#:
#: Fields: (kind, accessible_name, href, name_needle, href_needle, expectation).
#: The two needles are separate because the two leak paths are separate: a
#: name can survive in the `shape` field, in the `href_shape` field, or in
#: both, and one needle asked of both fields cannot tell those apart.
ROWS: tuple[tuple[str, str, str, str, str, str], ...] = (
    (
        "top_voice",
        MEMBER_NAME,
        "/in/priya-sharma-12ab34/",
        MEMBER_NAME,
        MEMBER_SLUG,
        "CONTROL MUST-REDACT",
    ),
    (
        "company",
        "Show more about the company",
        "/company/an-organisation/",
        "an-organisation",
        "an-organisation",
        "settled by precedent -- followed_companies ships these",
    ),
    (
        "group",
        "A Professional Group",
        "/groups/123456/",
        "A Professional Group",
        "123456",
        "should redact",
    ),
    (
        # THE DANGEROUS ONE. A newsletter's title and its slug BOTH routinely
        # carry the author's name, and neither was a marker in
        # _CENSUS_ENTITY_HREFS before 2026-09-04.
        "newsletter",
        "Weekly Notes by Savita Krishnan",
        "/newsletters/weekly-notes-by-alex-r-12ab34-123456/",
        OTHER_AUTHOR,
        OTHER_SLUG,
        "should redact -- a newsletter is authored BY A PERSON",
    ),
    (
        "school",
        "An Institute Of Technology",
        "/school/an-institute/",
        "An Institute Of Technology",
        "an-institute",
        "should redact",
    ),
    (
        "furniture",
        "Show more",
        "",
        "Show more",
        "",
        "CONTROL MUST-SURVIVE",
    ),
)


def published_href_shape(href: str) -> str:
    """The `href_shape` field the census publishes for one control.

    A SECOND LEAK PATH, AND THE SIMPLER ONE. Every census record carries
    `href_shape` beside `shape`, so a slug that survives shaping is published
    whatever happens to the accessible name -- no count coincidence required,
    on every surface the census already reads. `_CENSUS_IN_PATH` and
    `_CENSUS_COMPANY_PATH` reduce two path families to placeholders; nothing
    reduces the others, so their slug ships as written. A newsletter slug is
    routinely its author's name.
    """
    return shape.census_shape(href)


def published_shape(name: str, href: str, count: int) -> str:
    """What the census actually publishes for one control, both guards applied.

    THE ORDER IS THE SHIPPED ORDER, copied from `dom.read_surface_census` and
    `shape.census_aggregate` rather than reasoned about here: the record-level
    structural refusal first, then the aggregate-level count rule. Reproducing
    it rather than approximating it is the whole point -- a probe that models
    the guard instead of calling it measures the model.
    """
    href_shape = shape.census_shape(href) or None
    name_shape = shape.census_shape(name)
    if shape.census_href_identifies_entity(href_shape):
        name_shape = shape.CENSUS_REDACTED
    return shape.census_redact_rare(name_shape, count)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1]:
        _use_candidate(sys.argv[1])
    print("=== CAN A NAME REACH THE PUBLISHED CENSUS THROUGH AN INTERESTS ENTRY?")
    print("    shaper under test: %s" % shape.__file__)
    print("    pure -- no browser, no page load, no network")
    print("    _CENSUS_ENTITY_HREFS has %d members: %s"
          % (len(shape._CENSUS_ENTITY_HREFS), list(shape._CENSUS_ENTITY_HREFS)))
    print()
    print("    %-11s %-6s %-9s %s" % ("kind", "count", "verdict", "expectation"))
    print("    " + "-" * 74)

    reds = 0
    control_failures = 0
    for kind, name, href, needle, href_needle, expectation in ROWS:
        for count in (1, 2):
            out = published_shape(name, href, count)
            survived = needle.lower() in out.lower()
            verdict = "RED" if survived else "redacted"
            if expectation == "CONTROL MUST-SURVIVE":
                verdict = "survives" if survived else "CONTROL-BROKEN"
                if not survived:
                    control_failures += 1
            elif expectation == "CONTROL MUST-REDACT":
                if survived:
                    verdict = "CONTROL-BROKEN"
                    control_failures += 1
            elif survived:
                reds += 1
            print("    %-11s %-6d %-9s %s" % (kind, count, verdict, expectation))
        print()

    print("=== THE SECOND LEAK PATH: `href_shape`, PUBLISHED ON EVERY RECORD")
    print("    no count is involved -- this ships whatever the name does.")
    href_reds = 0
    for kind, name, href, needle, href_needle, expectation in ROWS:
        if not href:
            continue
        hs = published_href_shape(href)
        leaks = bool(href_needle) and href_needle.lower() in hs.lower()
        if leaks and "CONTROL" not in expectation:
            href_reds += 1
        print("    %-11s %-8s %r" % (kind, "RED" if leaks else "shaped", hs))
    print("    href_shape leaking rows: %d" % href_reds)
    print()

    print("=== WHAT THE PUBLISHED SHAPE ACTUALLY IS, for the rows that leak")
    print("    printed because a verdict without the artefact is not a finding.")
    print("    These strings are INVENTED names, declared in INVENTED_NAMES.")
    for kind, name, href, needle, href_needle, expectation in ROWS:
        out = published_shape(name, href, 2)
        if needle.lower() in out.lower() and "CONTROL" not in expectation:
            print("    %-11s count=2 -> %r" % (kind, out))

    print()
    print("=== TALLY")
    print("    leaking rows (excluding controls): %d" % reds)
    print("    control failures:                  %d" % control_failures)
    if control_failures:
        print("    THE CONTROLS DID NOT BEHAVE. Every row above is uninterpretable.")
    elif reds:
        print("    RED. A name reaches the published census through these kinds.")
    else:
        print("    GREEN. No needle survived either guard on any kind.")


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    main()
