"""Boundary evidence for the DECIDE-RETIRE rulings, both gates reported.

WHY BOTH GATES. ``readonly.assert_read_url`` runs the forbidden-substring loop
FIRST and raises on the first hit, so a refusal names a substring and stops --
and three readers have already taken that substring for the wall when it was
not. This probe asks the two questions separately and prints both answers, so a
ruling that leans on "the boundary refuses this" can say WHICH gate refused and
whether narrowing the other one would free anything.

It also prints, for every case, the CLASS of the refusal:

    FORBIDDEN  a substring somebody wrote down, with an argument behind it
    NO-PATTERN the default-closed allowlist, which decided nothing about this
               address in particular

That distinction is the whole point. This repo's own rule is that a general
mechanism which merely happens to block something is a GAP WITH A NAMED
BLOCKER, never a decision -- so a NO-PATTERN refusal may NOT be cited as the
reason a capability is retired. It is context. Only FORBIDDEN carries an
argument, and even then the argument is the one written beside the substring.

CONTROLS. Four must-allow and one must-refuse. A run whose controls do not
behave is discarded whole rather than read -- the same discipline the blockers
ledger applied when an earlier boundary run reported ``/feed/`` refused.

ADDRESSES ARE INVENTED WHERE THE CENSUS NAMES NONE, and every such case is
marked ASSUMED in the output. An assumed address proves what the boundary does
with a SHAPE; it cannot prove LinkedIn serves the capability at that shape.
That limit is stated in the ruling document rather than hidden here.

Run:
    ./venv/Scripts/python.exe scripts/_probe_retire_ruling_boundary.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import readonly  # noqa: E402
from linkedin_server.writes import WriteAttemptError  # noqa: E402

# (label, url, expectation, address_provenance)
#   expectation: "ALLOW" | "REFUSE" | None (report only)
#   provenance:  "CITED"   the census or a help article names this address
#                "ASSUMED" this probe invented it to test a shape
CASES: tuple[tuple[str, str, str | None, str], ...] = (
    ("CONTROL feed", "https://www.linkedin.com/feed/", "ALLOW", "CITED"),
    ("CONTROL job search", "https://www.linkedin.com/jobs/search/", "ALLOW", "CITED"),
    ("CONTROL messaging", "https://www.linkedin.com/messaging/", "ALLOW", "CITED"),
    (
        "CONTROL dark mode",
        "https://www.linkedin.com/mypreferences/d/dark-mode",
        "ALLOW",
        "CITED",
    ),
    ("CONTROL psettings root", "https://www.linkedin.com/psettings/", "REFUSE", "CITED"),
    # MESSAGING-SETTINGS -- the settings family below the index
    (
        "MSG-SET typing indicators",
        "https://www.linkedin.com/psettings/messaging-typing-indicators",
        "REFUSE",
        "ASSUMED",
    ),
    (
        "MSG-SET smart features",
        "https://www.linkedin.com/psettings/messaging-smart-features",
        "REFUSE",
        "ASSUMED",
    ),
    (
        "MSG-SET group members",
        "https://www.linkedin.com/psettings/allow-messages-from-group-members",
        "REFUSE",
        "ASSUMED",
    ),
    ("MSG-SET inmail opt-out", "https://www.linkedin.com/psettings/inmail", "REFUSE", "ASSUMED"),
    ("MSG-SET nudges", "https://www.linkedin.com/psettings/message-nudges", "REFUSE", "ASSUMED"),
    (
        "MSG-SET category index",
        "https://www.linkedin.com/mypreferences/d/categories/messaging",
        "REFUSE",
        "CITED",
    ),
    ("MSG-SET settings index", "https://www.linkedin.com/settings/", "REFUSE", "CITED"),
    # HELP-CENTER-FORM -- the two deceased-member forms are cited by slug
    (
        "HELP form ts-rmdmlp",
        "https://www.linkedin.com/help/linkedin/ask/ts-rmdmlp",
        None,
        "CITED",
    ),
    ("HELP index", "https://www.linkedin.com/help/linkedin", None, "CITED"),
    # OFF-PLATFORM-WIDGET -- a follow button on somebody else's domain
    ("OFF-DOMAIN employer site", "https://example.com/careers", None, "ASSUMED"),
    # LIVE-BROADCAST / PAID-BOOST / AI-INTERVIEW-PRODUCT
    ("LIVE video manager", "https://www.linkedin.com/video/live/", None, "ASSUMED"),
    ("BOOST campaign manager", "https://www.linkedin.com/campaignmanager/", None, "ASSUMED"),
    ("AI-INTERVIEW learning", "https://www.linkedin.com/learning/", None, "ASSUMED"),
    ("AI-INTERVIEW prep hub", "https://www.linkedin.com/interview-prep/", None, "ASSUMED"),
    # CONTACT-IMPORT / SIGNIN-INTERSTITIAL
    (
        "IMPORT contacts",
        "https://www.linkedin.com/mynetwork/import-contacts/",
        None,
        "ASSUMED",
    ),
    (
        "SIGNIN checkpoint",
        "https://www.linkedin.com/checkpoint/challenge/",
        None,
        "CITED",
    ),
)


def _substring_verdict(url: str) -> str | None:
    """The forbidden substring this url trips, or None."""
    lowered = url.lower()
    exact = readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS.get(lowered)
    exempted = frozenset({exact}) if exact is not None else frozenset()
    if not exempted:
        exempted = readonly._pattern_exempted_substrings(url)
    for bad in readonly._FORBIDDEN_URL_SUBSTRINGS:
        if bad in lowered and bad not in exempted:
            return bad
    return None


def _pattern_verdict(url: str) -> bool:
    """Whether any allowlist pattern admits this url, ignoring substrings."""
    return any(pattern.match(url) for pattern in readonly._ALLOWED_URL_PATTERNS)


def main() -> int:
    print(f"allowlist patterns: {len(readonly._ALLOWED_URL_PATTERNS)}")
    print(f"forbidden substrings: {len(readonly._FORBIDDEN_URL_SUBSTRINGS)}")
    print()
    header = f"{'case':28s} {'prov':8s} {'substring':22s} {'pattern':9s} {'verdict':10s}"
    print(header)
    print("-" * len(header))

    control_failures = 0
    for label, url, expectation, provenance in CASES:
        bad = _substring_verdict(url)
        admitted = _pattern_verdict(url)
        try:
            readonly.assert_read_url(url)
            verdict = "ALLOWED"
        except WriteAttemptError:
            verdict = "REFUSED"
        klass = "FORBIDDEN" if bad else ("--" if admitted else "NO-PATTERN")
        print(
            f"{label:28s} {provenance:8s} {(bad or '--'):22s} "
            f"{('admits' if admitted else 'none'):9s} {verdict:10s} {klass}"
        )
        if expectation == "ALLOW" and verdict != "ALLOWED":
            control_failures += 1
            print(f"  !! CONTROL FAILED: expected ALLOWED for {label}")
        if expectation == "REFUSE" and verdict != "REFUSED":
            control_failures += 1
            print(f"  !! CONTROL FAILED: expected REFUSED for {label}")

    print()
    if control_failures:
        print(f"CONTROL FAILURES: {control_failures}. DISCARD THIS RUN WHOLE.")
        return 1
    print("controls: 4 must-allow passed, 1 must-refuse fired, 0 failures.")
    print()
    print(
        "READ THE CLASS COLUMN. A NO-PATTERN refusal is the default-closed "
        "allowlist and decides nothing about the address in particular; it may "
        "not be cited as the reason a capability is retired."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
