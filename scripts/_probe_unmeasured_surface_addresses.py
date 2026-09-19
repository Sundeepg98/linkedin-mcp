"""Which candidate LinkedIn addresses does this package's OWN read boundary
allow, and for the ones it refuses, which of the two independent gates fired?

``linkedin_server/readonly.py`` enforces the read-only invariant in two
layers, checked in a fixed order inside ``assert_read_url``:
:data:`readonly._FORBIDDEN_URL_SUBSTRINGS` (33 literal substrings, checked
FIRST -- measured, not assumed: ``len(readonly._FORBIDDEN_URL_SUBSTRINGS) ==
33``) and :data:`readonly._ALLOWED_URL_PATTERNS` (24 anchored regexes,
checked second and REQUIRED -- ``len(readonly._ALLOWED_URL_PATTERNS) == 24``).
Three families this package has never navigated to -- LinkedIn Groups,
LinkedIn Events, and the hashtag/content-search family -- have therefore
never had their outcome against that boundary MEASURED. This runs every
candidate address in each family through the real boundary function once and
reports, per address, exactly which of three things happened:

    ALLOWED               an allow pattern matched.
    REFUSED-FORBIDDEN     a forbidden substring fired. WHICH ONE is reported,
                           by re-scanning ``_FORBIDDEN_URL_SUBSTRINGS`` for
                           every entry the url's lowercased text contains --
                           there can be more than one.
    REFUSED-NO-PATTERN    no forbidden substring, and no allow pattern
                           matched either.

A REFUSAL THAT DOES NOT NAME ITS CAUSE IS USELESS HERE. "Refused" alone
answers nothing about whether Groups and Events are unreachable because
nobody has written a pattern for them yet, or because something about their
shape trips an existing forbidden word -- and those are different findings
with different next steps for whoever reads this probe's output.

## The seven controls

Seven addresses this package has ALREADY ruled on are run through the same
function and checked against a stated expectation, printed as PASS/FAIL.
The probe's findings above are not trustworthy unless these seven behave as
documented -- they are the calibration, not decoration, and a FAIL here means
stop and report rather than trust the rest of the run.

Six of the seven are a plain MUST-ALLOW / MUST-REFUSE-FORBIDDEN /
MUST-REFUSE-NO-PATTERN check. The seventh, ``/in/me/edit/intro/``, is
different in kind and is labelled ORDERING-PROBE rather than a plain
expectation: an ALLOW pattern exists for that exact address, and ``/edit/``
is ALSO one of the forbidden substrings, checked first. Whatever the real
function does with that url -- refuse, because the forbidden check runs
first and finds an unexempted hit, or allow, because
``_FORBIDDEN_SUBSTRING_EXEMPTIONS`` names that one exact url as exempt from
``/edit/`` specifically -- is a finding about the boundary's own ordering
and exemption table, not a bug in this probe. It PASSES either way; what
matters is that the printed line states which actually happened.

## Bounds

**NO BROWSER. NO PAGE LOAD. NO NETWORK. NO mcp__linkedin__* CALL.** This
imports ``linkedin_server.readonly`` and calls ``readonly.assert_read_url``,
the real public entry point whose decision logic sits at lines 917-945 of
that module -- nothing else in this package is imported, and nothing here
opens a page.

**IT DOES NOT RE-IMPLEMENT THE CHECK, AND IT DOES NOT TOUCH EITHER LIST.**
The ALLOWED / REFUSED decision for every address below comes from one call
to the real ``assert_read_url``, unmodified and uncopied. The only thing
this file adds on top of that call is a separate, honest RE-SCAN of
``_FORBIDDEN_URL_SUBSTRINGS`` -- run only after a refusal, only to name
which literal substring(s) the url's text contains -- and that re-scan is a
plain membership test, not a second copy of the gate. Neither
``_ALLOWED_URL_PATTERNS`` nor ``_FORBIDDEN_URL_SUBSTRINGS`` is written to
anywhere in this file.

THE RE-SCAN'S HONEST LIMIT, stated rather than implied: ``assert_read_url``
also consults two exemption tables (``_FORBIDDEN_SUBSTRING_EXEMPTIONS`` and
``_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS``) that can excuse ONE named url
from ONE named substring. The re-scan below does not consult them -- it
answers "does this literal text occur", not "would the real gate excuse
it" -- so a substring it lists beside a REFUSED url is always the true
cause (the real function refused, and refused because of an unexempted
hit), but the list is not, in general, a claim about what an ALLOWED url's
text happens to contain. CHECKED BY MEASUREMENT rather than assumed: every
one of the 26 candidates below was tested against both exemption tables
before this file was written, and exactly one -- the ordering-probe control
itself -- matches either of them. That one is called out by name above
rather than folded into the count silently.

**EVERY ADDRESS IS A LITERAL.** One module-level tuple, ``CANDIDATES``, and
every entry in it is copied verbatim from the brief -- none built from
anything read at runtime, matched off a page, or derived from another
address. The ``<id>`` placeholders (``12345678``, ``12345678901234567890``,
``example``) are shape probes and stay placeholders; ``4423880462`` on the
MUST-ALLOW job-posting control is the one posting id already sitting in this
package's own committed fixtures (``scripts/_probe_free_reads_shapes.py``'s
``JOB_ID``, filled in 2026-09-03 from ``linkedin_saved_jobs``) -- a posting
id, never a person's. No person's name, no company name, no member path, and
no real member or company id appears anywhere in this file.

**IT WRITES NOTHING.** No file, no output path, and nothing to LinkedIn --
there is no LinkedIn session anywhere in this process to write to.

Run:  venv/Scripts/python.exe scripts/_probe_unmeasured_surface_addresses.py
Writes NOTHING.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import readonly  # noqa: E402
from linkedin_server.errors import WriteAttemptError  # noqa: E402

#: The four expectation labels a CANDIDATES row can carry. ``None`` (the
#: fourth, implicit case) means "not a control -- no assertion, just a
#: measurement". The other three are plain equality checks against the
#: outcome; ORDERING_PROBE is deliberately not one -- see the docstring.
MUST_ALLOW = "MUST-ALLOW"
MUST_REFUSE_FORBIDDEN = "MUST-REFUSE-FORBIDDEN"
MUST_REFUSE_NO_PATTERN = "MUST-REFUSE-NO-PATTERN"
ORDERING_PROBE = "ORDERING-PROBE"

#: THE WHOLE ADDRESS LIST. One module-level tuple, as the brief asks for.
#: Every entry is ``(group, url, expectation)`` -- ``group`` is one of
#: "groups", "events", "hashtag" or "control"; ``expectation`` is ``None``
#: for the first three groups (this probe is measuring them, not asserting
#: on them) and one of the four labels above for every "control" row.
#:
#: EVERY URL IS A LITERAL, copied from the brief character for character.
#: Nothing here is built from a page, a previous call in this file, or
#: anything read at runtime -- the discipline
#: ``tests/test_navigation_is_never_derived.py`` exists to hold, even though
#: this file never calls ``.goto`` and so never trips it either way.
CANDIDATES: tuple[tuple[str, str, Optional[str]], ...] = (
    # -- GROUPS: never measured against this boundary before now. --------
    ("groups", "https://www.linkedin.com/groups/", None),
    ("groups", "https://www.linkedin.com/groups/12345678/", None),
    ("groups", "https://www.linkedin.com/groups/12345678/members/", None),
    ("groups", "https://www.linkedin.com/groups/12345678/requests/", None),
    ("groups", "https://www.linkedin.com/groups/12345678/about/", None),
    ("groups", "https://www.linkedin.com/groups/12345678/invite/", None),
    ("groups", "https://www.linkedin.com/groups/discover/", None),
    ("groups", "https://www.linkedin.com/mynetwork/groups/", None),
    (
        "groups",
        "https://www.linkedin.com/search/results/groups/?keywords=engineering",
        None,
    ),
    # -- EVENTS: same question, a different family. -----------------------
    ("events", "https://www.linkedin.com/events/", None),
    ("events", "https://www.linkedin.com/events/12345678901234567890/", None),
    (
        "events",
        "https://www.linkedin.com/events/12345678901234567890/about/",
        None,
    ),
    (
        "events",
        "https://www.linkedin.com/events/12345678901234567890/comments/",
        None,
    ),
    (
        "events",
        "https://www.linkedin.com/mynetwork/network-manager/events/",
        None,
    ),
    (
        "events",
        "https://www.linkedin.com/search/results/events/?keywords=hiring",
        None,
    ),
    # -- HASHTAG / content-search family. ---------------------------------
    ("hashtag", "https://www.linkedin.com/feed/hashtag/hiring/", None),
    ("hashtag", "https://www.linkedin.com/feed/hashtag/?keywords=hiring", None),
    (
        "hashtag",
        "https://www.linkedin.com/search/results/content/?keywords=%23hiring",
        None,
    ),
    ("hashtag", "https://www.linkedin.com/feed/follows/", None),
    # -- CONTROLS: already-ruled addresses, asserted rather than measured. -
    ("control", "https://www.linkedin.com/feed/", MUST_ALLOW),
    ("control", "https://www.linkedin.com/jobs/view/4423880462", MUST_ALLOW),
    ("control", "https://www.linkedin.com/messaging/", MUST_ALLOW),
    ("control", "https://www.linkedin.com/in/me/edit/intro/", ORDERING_PROBE),
    (
        "control",
        "https://www.linkedin.com/feed/?action=like",
        MUST_REFUSE_FORBIDDEN,
    ),
    (
        "control",
        "https://www.linkedin.com/psettings/messages/",
        MUST_REFUSE_FORBIDDEN,
    ),
    (
        "control",
        "https://www.linkedin.com/company/example/",
        MUST_REFUSE_NO_PATTERN,
    ),
)

#: The three possible outcomes, named once so every place that prints or
#: counts one spells it identically.
ALLOWED = "ALLOWED"
REFUSED_FORBIDDEN = "REFUSED-FORBIDDEN"
REFUSED_NO_PATTERN = "REFUSED-NO-PATTERN"


def _classify(url: str) -> tuple[str, list[str]]:
    """Run one url through the REAL read boundary and name what happened.

    Returns ``(outcome, substrings)``. ``outcome`` is one of
    :data:`ALLOWED`, :data:`REFUSED_FORBIDDEN` or :data:`REFUSED_NO_PATTERN`.
    ``substrings`` is the (possibly empty) list of every entry in
    ``readonly._FORBIDDEN_URL_SUBSTRINGS`` that this url's lowercased text
    contains -- always empty when ``outcome`` is not REFUSED_FORBIDDEN.

    THE GATE IS ``readonly.assert_read_url``, CALLED UNCHANGED. Whether this
    returns ALLOWED or a REFUSED-* outcome is decided entirely by whether
    that call raises -- nothing here second-guesses it. The substring list
    is a SEPARATE, ADDITIONAL re-scan, run only to name a refusal's cause
    once the real function has already decided there is one; see the
    "RE-SCAN'S HONEST LIMIT" section of the module docstring for exactly
    what that re-scan does and does not claim.
    """
    lowered = url.lower()
    try:
        readonly.assert_read_url(url)
    except WriteAttemptError:
        hits = [bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in lowered]
        return (REFUSED_FORBIDDEN if hits else REFUSED_NO_PATTERN, hits)
    return (ALLOWED, [])


def _verdict(expectation: Optional[str], outcome: str) -> Optional[str]:
    """PASS/FAIL for a control row, or ``None`` for a plain measurement row.

    ORDERING_PROBE always PASSES -- it is not a pass/fail gate, it is asking
    which of two real mechanisms fires first, and either answer is the
    finding. The other three expectations are a literal equality check
    against ``outcome``.
    """
    if expectation is None:
        return None
    if expectation == ORDERING_PROBE:
        return "PASS"
    if expectation == MUST_ALLOW:
        return "PASS" if outcome == ALLOWED else "FAIL"
    if expectation == MUST_REFUSE_FORBIDDEN:
        return "PASS" if outcome == REFUSED_FORBIDDEN else "FAIL"
    if expectation == MUST_REFUSE_NO_PATTERN:
        return "PASS" if outcome == REFUSED_NO_PATTERN else "FAIL"
    raise AssertionError("unreachable: unknown expectation %r" % (expectation,))


def main() -> None:
    print("=== WHICH UNMEASURED LINKEDIN ADDRESSES DOES THE READ BOUNDARY ALLOW?")
    print("    %d literal addresses, one call each to readonly.assert_read_url" % (
        len(CANDIDATES),
    ))
    print("    no browser, no page load, no network, no mcp call -- the")
    print("    boundary function only\n")

    # group -> outcome -> count
    group_counts: dict[str, dict[str, int]] = {}
    control_verdicts: list[str] = []
    forbidden_hits: list[tuple[str, list[str]]] = []

    current_group: Optional[str] = None
    for group, url, expectation in CANDIDATES:
        if group != current_group:
            shown = [g for g, _u, _e in CANDIDATES if g == group]
            print("--- %s (%d) ---" % (group, len(shown)))
            current_group = group

        outcome, hits = _classify(url)
        group_counts.setdefault(group, {ALLOWED: 0, REFUSED_FORBIDDEN: 0, REFUSED_NO_PATTERN: 0})
        group_counts[group][outcome] += 1
        if outcome == REFUSED_FORBIDDEN:
            forbidden_hits.append((url, hits))

        verdict = _verdict(expectation, outcome)
        if verdict is None:
            suffix = ("  substrings=%s" % hits) if hits else ""
            print("    %-19s %s%s" % (outcome, url, suffix))
        else:
            control_verdicts.append(verdict)
            suffix = ("  substrings=%s" % hits) if hits else ""
            print(
                "    %-4s expected=%-19s actual=%-19s %s%s"
                % (verdict, expectation, outcome, url, suffix)
            )

    print("\n=== COUNTS, BY GROUP")
    grand: dict[str, int] = {ALLOWED: 0, REFUSED_FORBIDDEN: 0, REFUSED_NO_PATTERN: 0}
    surface_only: dict[str, int] = {ALLOWED: 0, REFUSED_FORBIDDEN: 0, REFUSED_NO_PATTERN: 0}
    for group in ("groups", "events", "hashtag", "control"):
        counts = group_counts.get(group, {ALLOWED: 0, REFUSED_FORBIDDEN: 0, REFUSED_NO_PATTERN: 0})
        total = sum(counts.values())
        print(
            "    %-8s ALLOWED=%d  REFUSED-FORBIDDEN=%d  REFUSED-NO-PATTERN=%d  (%d total)"
            % (group, counts[ALLOWED], counts[REFUSED_FORBIDDEN], counts[REFUSED_NO_PATTERN], total)
        )
        for key in grand:
            grand[key] += counts[key]
            if group != "control":
                surface_only[key] += counts[key]

    grand_total = sum(grand.values())
    surface_total = sum(surface_only.values())
    print(
        "    %-8s ALLOWED=%d  REFUSED-FORBIDDEN=%d  REFUSED-NO-PATTERN=%d  (%d total)"
        % ("ALL 26", grand[ALLOWED], grand[REFUSED_FORBIDDEN], grand[REFUSED_NO_PATTERN], grand_total)
    )
    print(
        "    %-8s ALLOWED=%d  REFUSED-FORBIDDEN=%d  REFUSED-NO-PATTERN=%d  (%d total)"
        % (
            "SURFACE",
            surface_only[ALLOWED],
            surface_only[REFUSED_FORBIDDEN],
            surface_only[REFUSED_NO_PATTERN],
            surface_total,
        )
    )
    print("    (SURFACE = groups + events + hashtag only, the 19 addresses")
    print("    this probe exists to measure; ALL 26 also folds in the 7")
    print("    controls above.)")

    print("\n=== REFUSED-FORBIDDEN, WITH THE SUBSTRING THAT FIRED")
    if forbidden_hits:
        for url, hits in forbidden_hits:
            print("    %-70s %s" % (url, hits))
    else:
        print("    none")

    print("\n=== CONTROLS")
    if control_verdicts and all(v == "PASS" for v in control_verdicts):
        print("    ALL %d CONTROLS PASSED" % len(control_verdicts))
    else:
        failed = sum(1 for v in control_verdicts if v != "PASS")
        print(
            "    %d OF %d CONTROLS FAILED -- see the FAIL line(s) above. The"
            % (failed, len(control_verdicts))
        )
        print("    findings above this line are not trustworthy until that is understood.")


# GUARDED: importing a script must not DO anything.
# tests/test_scripts_are_import_safe.py asserts this for every file in scripts/.
if __name__ == "__main__":
    main()
