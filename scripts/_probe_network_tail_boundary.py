"""Boundary reproduction for the ``network-tail`` wave's five blockers.

Offline. Opens no browser and loads no page. For every candidate address it
prints WHAT THE GATE SAW, never only what it failed to match -- the repo's
standing rule that a refusal reporting a bare count is half a measurement.

Three outcomes are distinguished, because they are three different findings:

    ALLOWED              already reachable; the row's blocker is not the boundary
    REFUSED-FORBIDDEN    a substring on ``_FORBIDDEN_URL_SUBSTRINGS`` matched,
                         and the matching substring is named
    REFUSED-NO-PATTERN   no forbidden substring matched; no allowlist pattern did

The distinction is the whole point of this probe. A row blocked by
NO-PATTERN needs an allowlist addition, which is additive. A row blocked by
FORBIDDEN needs a denylist NARROWING, which subtracts from something that
exists to stop an act -- the most dangerous edit in this repository.

Run:

    ./venv/Scripts/python.exe scripts/_probe_network_tail_boundary.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from linkedin_server import readonly  # noqa: E402

BASE = "https://www.linkedin.com"

#: ``(blocker, census rows, read-or-write, address)``. Addresses are route
#: SHAPES from LinkedIn's own navigation; none carries a member identifier.
CANDIDATES: tuple[tuple[str, str, str, str], ...] = (
    # --- 63 ENDORSE-SUBSTRING-OVERREACH -------------------------------
    ("ENDORSE", "P E7 / N 114", "R", f"{BASE}/in/me/details/skills/"),
    ("ENDORSE", "P E7", "R", f"{BASE}/in/me/details/skills/?detailScreenTabIndex=0"),
    ("ENDORSE", "P E6", "W", f"{BASE}/in/me/details/skills/endorsements/"),
    ("ENDORSE", "R3 the act itself", "W", f"{BASE}/in/me/endorse/"),
    ("ENDORSE", "R3 the act itself", "W", f"{BASE}/profile/endorse"),
    # --- 52 PEOPLE-FOLLOW-LISTS ---------------------------------------
    ("FOLLOW-LISTS", "N 38", "R", f"{BASE}/mynetwork/network-manager/people-follow/following/"),
    ("FOLLOW-LISTS", "N 44 / P L2b", "R", f"{BASE}/mynetwork/network-manager/people-follow/followers/"),
    ("FOLLOW-LISTS", "sibling, already admitted", "R", f"{BASE}/mynetwork/network-manager/company/"),
    ("FOLLOW-LISTS", "the act this denylist entry exists to stop", "W", f"{BASE}/in/me/follow/"),
    ("FOLLOW-LISTS", "the act this denylist entry exists to stop", "W", f"{BASE}/company/example/follow/"),
    ("FOLLOW-LISTS", "the act this denylist entry exists to stop", "W", f"{BASE}/company/example/unfollow/"),
    # --- 21 SERVICES-PAGE-SURFACE -------------------------------------
    ("SERVICES", "P H11", "R", f"{BASE}/services/page/"),
    ("SERVICES", "P H1", "W", f"{BASE}/services/page/create/"),
    ("SERVICES", "P H2", "W", f"{BASE}/services/page/edit/"),
    ("SERVICES", "P H10", "W", f"{BASE}/services/page/reviews/"),
    # --- 11 HASHTAG-EXISTENCE -----------------------------------------
    ("HASHTAG", "C 52", "R", f"{BASE}/feed/hashtag/hiring/"),
    ("HASHTAG", "C 52", "R", f"{BASE}/feed/follows/"),
    # --- 60 INVITE-NOTE-PARAM -----------------------------------------
    ("INVITE-NOTE", "the act, for the record", "W", f"{BASE}/mynetwork/invite-connect/connections/"),
)


def verdict(url: str) -> tuple[str, str]:
    """Return ``(outcome, what the gate saw)`` for one address."""
    lowered = url.lower()
    exempt = readonly._pattern_exempted_substrings(url)
    exact = readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS.get(lowered)
    matched = [
        bad
        for bad in readonly._FORBIDDEN_URL_SUBSTRINGS
        if bad in lowered and bad not in exempt and (exact is None or bad != exact)
    ]
    try:
        readonly.assert_read_url(url)
    except readonly.WriteAttemptError:
        if matched:
            return "REFUSED-FORBIDDEN", "matched " + ", ".join(repr(m) for m in matched)
        return "REFUSED-NO-PATTERN", "no forbidden substring; no allowlist pattern"
    return "ALLOWED", ("carried " + ", ".join(repr(m) for m in matched)) if matched else "clean"


#: Controls. The substring scan in :func:`verdict` is computed INDEPENDENTLY
#: of ``assert_read_url`` -- deliberately, so the two can disagree and the
#: disagreement is visible. An instrument whose detector is the thing it is
#: measuring cannot fail, and a check that cannot fail certifies nothing.
#:
#: ``(url, expected outcome, why this control exists)``
CONTROLS: tuple[tuple[str, str, str], ...] = (
    (
        f"{BASE}/feed/",
        "ALLOWED",
        "must-pass: a known-admitted address. If this reads REFUSED the "
        "probe is refusing everything and every finding below is void.",
    ),
    (
        f"{BASE}/company/example/follow/",
        "REFUSED-FORBIDDEN",
        "must-refuse: the act '/follow' exists to stop. If this reads "
        "ALLOWED the denylist is not being consulted at all.",
    ),
    (
        f"{BASE}/nothing/here/",
        "REFUSED-NO-PATTERN",
        "must-refuse-differently: proves the probe distinguishes its two "
        "refusal classes rather than collapsing them into one word.",
    ),
)


def run_controls() -> bool:
    """Print each control and whether it fired. Return True if all held."""
    ok = True
    print("CONTROLS -- an instrument that cannot fail certifies nothing")
    for url, expected, why in CONTROLS:
        outcome, seen = verdict(url)
        held = outcome == expected
        ok = ok and held
        print(f"  {'HELD' if held else 'BROKEN'}  {url[len(BASE):]:<28} "
              f"expected {expected:<19} read {outcome} ({seen})")
        print(f"          {why}")
    print()
    return ok


def main() -> int:
    print(f"allowlist patterns : {len(readonly._ALLOWED_URL_PATTERNS)}")
    print(f"forbidden substrings: {len(readonly._FORBIDDEN_URL_SUBSTRINGS)}")
    print()
    if not run_controls():
        print("A CONTROL DID NOT HOLD. The readings below are NOT evidence.")
        return 1
    width = max(len(u) for _, _, _, u in CANDIDATES) - len(BASE)
    current = None
    for blocker, rows, kind, url in CANDIDATES:
        if blocker != current:
            print(f"--- {blocker} " + "-" * (58 - len(blocker)))
            current = blocker
        outcome, seen = verdict(url)
        path = url[len(BASE):]
        print(f"  [{kind}] {path:<{width}}  {outcome:<19} {seen}")
        print(f"        rows: {rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
