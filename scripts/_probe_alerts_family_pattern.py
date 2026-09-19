"""What a FAMILY pattern under ``/jobs/alerts/`` would open, measured.

WHY THIS PROBE EXISTS. The standing boundary trap in this repository is that
``close-account`` is refused by NO PATTERN MATCHING rather than by a denylist
entry, so a settings-FAMILY pattern would admit account-ending spellings that
nothing else defends. The job-alerts surface has the same shape and nobody had
measured it: the alerts manage page needs an allowlist entry, and the lazy way
to write one is ``/jobs/alerts/.*``.

So this probe answers, for a list of candidate spellings under that root, three
questions that are usually collapsed into one:

    a. does a FORBIDDEN SUBSTRING bite?  (checked BEFORE the allowlist, and
       never shortened for a write)
    b. does any allowlist pattern admit it TODAY?
    c. would a family pattern admit it?

An address answering "no" to (a) and "no" to (b) is DEFENDED BY NOTHING BUT THE
ABSENCE OF A RULE -- exactly the close-account shape -- and it is the set a
family pattern opens.

IT OPENS NOTHING AND LOADS NOTHING. Every address below is a literal typed into
this file. No browser is started, no page is fetched, no LinkedIn session is
touched. The only thing called is the shipped predicate.

NO ADDRESS IS PRINTED. Output is a LABEL plus a RELATION plus, where a
substring bites, the substring itself -- because a refusal that names only what
it did NOT match is half a measurement. The urls stay in the source.

CONTROLS RUN FIRST AND THE PROBE REFUSES TO MEASURE IF EITHER FAILS. One
known-ALLOW and one known-REFUSE address are put through the predicate before
anything else, because an instrument that cannot say ALLOW will report the
whole boundary as closed and look authoritative doing it. That is not
hypothetical here: the sibling probe this one is modelled on failed its own
control on its first run.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import readonly  # noqa: E402


#: The family pattern this probe exists to argue against. It is NEVER added to
#: ``readonly._ALLOWED_URL_PATTERNS`` -- it is compiled here, applied to a COPY
#: of the roster, and thrown away.
_FAMILY = re.compile(r"^https://www\.linkedin\.com/jobs/alerts/.*$")

#: The narrow anchored candidate: the manage page and nothing else. No query,
#: no sub-path, no id.
_NARROW = re.compile(r"^https://www\.linkedin\.com/jobs/alerts/?$")


#: (label, url). Labels carry the census row where there is one.
_CANDIDATES: tuple[tuple[str, str], ...] = (
    ("J37 the manage page, trailing slash",
     "https://www.linkedin.com/jobs/alerts/"),
    ("J37 the manage page, no trailing slash",
     "https://www.linkedin.com/jobs/alerts"),
    ("J31 an alert create verb",
     "https://www.linkedin.com/jobs/alerts/create"),
    ("J34 an alert delete verb on an id",
     "https://www.linkedin.com/jobs/alerts/delete/1234567890"),
    ("J35 J36 alert frequency and channel",
     "https://www.linkedin.com/jobs/alerts/settings/"),
    ("an alert DETAIL page, one id deep",
     "https://www.linkedin.com/jobs/alerts/1234567890/"),
    ("an alert EDIT sub-path",
     "https://www.linkedin.com/jobs/alerts/edit/1234567890"),
    ("the manage page carrying a query",
     "https://www.linkedin.com/jobs/alerts/?origin=JOB_ALERT_EMAIL"),
    ("a manage-alerts spelling nobody has confirmed",
     "https://www.linkedin.com/jobs/alerts/manage/"),
    ("an alert PAUSE verb, which is a write nobody has named",
     "https://www.linkedin.com/jobs/alerts/pause/1234567890"),
    ("a dotted escape out of the alerts root",
     "https://www.linkedin.com/jobs/alerts/../mypreferences/d/categories/"),
)

_CONTROL_ALLOW = (
    "control-allow: the job search surface this server reads today",
    "https://www.linkedin.com/jobs/search/?keywords=node.js",
)
_CONTROL_REFUSE = (
    "control-refuse: another member's profile, the sharpest refusal there is",
    "https://www.linkedin.com/in/another-person/",
)


def _biting_substrings(url: str) -> tuple[str, ...]:
    """Which forbidden substrings are IN this url. Names what it saw."""
    return tuple(bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in url)


def _matches(url: str, roster: tuple[re.Pattern[str], ...]) -> bool:
    return any(pattern.match(url) for pattern in roster)


def _predicate_says_allow(url: str) -> tuple[bool, str]:
    """ALLOW/REFUSE from the SHIPPED predicate, plus its reason class."""
    try:
        readonly.assert_read_url(url)
    except Exception as exc:  # noqa: BLE001 - the class is the measurement
        return False, type(exc).__name__
    return True, ""


def _run_controls() -> bool:
    ok = True
    label, url = _CONTROL_ALLOW
    allowed, why = _predicate_says_allow(url)
    if not allowed:
        print(f"CONTROL FAILED: {label}")
        print(f"  expected ALLOW, predicate said REFUSE ({why})")
        ok = False
    label, url = _CONTROL_REFUSE
    allowed, _ = _predicate_says_allow(url)
    if allowed:
        print(f"CONTROL FAILED: {label}")
        print("  expected REFUSE, predicate said ALLOW")
        ok = False
    return ok


def main() -> int:
    if not _run_controls():
        print()
        print("NO MEASUREMENT TAKEN. An instrument that fails its own control")
        print("reports the boundary, not the addresses.")
        return 1

    roster = tuple(readonly._ALLOWED_URL_PATTERNS)
    print(f"allowlist patterns   {len(roster)}")
    print(f"forbidden substrings {len(readonly._FORBIDDEN_URL_SUBSTRINGS)}")
    print()

    undefended = 0
    narrow_admits = 0
    family_admits = 0
    family_only = 0

    for label, url in _CANDIDATES:
        bites = _biting_substrings(url)
        today = _matches(url, roster)
        by_narrow = bool(_NARROW.match(url))
        by_family = bool(_FAMILY.match(url))

        if by_narrow:
            narrow_admits += 1
        if by_family:
            family_admits += 1
        if by_family and not by_narrow and not bites:
            family_only += 1
        if not bites and not today:
            undefended += 1

        gate = "SUBSTRING BITES" if bites else "no substring"
        print(f"{label}")
        print(f"    {gate}"
              + (f": {', '.join(repr(b) for b in bites)}" if bites else ""))
        print(f"    admitted today   {'YES' if today else 'no'}")
        print(f"    narrow candidate {'YES' if by_narrow else 'no'}")
        print(f"    FAMILY pattern   {'YES' if by_family else 'no'}")

    print()
    print(f"candidates                                    {len(_CANDIDATES)}")
    print(f"  the NARROW anchored candidate admits        {narrow_admits}")
    print(f"  the FAMILY pattern admits                   {family_admits}")
    print(f"  admitted by FAMILY ONLY, no substring bites {family_only}")
    print(f"  defended today by NO RULE AT ALL            {undefended}")
    print()
    print("The last two lines are the argument. An address the family pattern")
    print("admits, that no forbidden substring bites, is defended today by")
    print("nothing but the absence of a rule -- and a family pattern is how")
    print("that absence stops defending it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
