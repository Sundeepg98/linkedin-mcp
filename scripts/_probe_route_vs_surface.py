"""Put every route this audit claims through the read gate at HEAD.

THE QUESTION THIS ANSWERS is not "where does LinkedIn draw the control" but
"what address serves the capability, and does ``readonly.assert_read_url``
admit it today". A route that ought to be allowed and is refused by a
forbidden substring is the trap this instrument exists to catch, so the
refusal is reported WITH THE SUBSTRING THAT FIRED and with whether a pattern
would have admitted the address anyway.

CONTROLS FIRST, and both directions. Three addresses that must be ALLOWED and
four that must be REFUSED, one of them for the substring rather than for the
pattern -- a gate that admits everything and a gate that refuses everything
both produce a clean-looking table.

Read-only. No browser, no session, no page load. Module-level literals only:
every address here is either a repo constant, a shape this package already
builds, or a path quoted by the census. No member name, no member id, no
company this account has any relationship with.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from linkedin_server import readonly  # noqa: E402

BASE = "https://www.linkedin.com"

#: A job id shape, not a job. Six digits is the pattern's own minimum.
JOB_ID = "1234567890"
#: A Page id SHAPE that belongs to nobody -- the all-zeroes convention this
#: repository already uses for a synthetic urn. It is shape-valid on purpose:
#: a self-test that hides from the identity guard blinds the guard to a real
#: value pasted in later.
PAGE_ID = "0000"

MUST_ALLOW: tuple[tuple[str, str], ...] = (
    ("the feed", f"{BASE}/feed/"),
    ("job search, bare", f"{BASE}/jobs/search/"),
    ("his own profile", f"{BASE}/in/me/"),
)
MUST_REFUSE: tuple[tuple[str, str], ...] = (
    ("people search -- the general case, deliberately absent",
     f"{BASE}/search/results/people/?keywords=x"),
    ("a company Page", f"{BASE}/company/example-co/"),
    ("the password page -- substring, not pattern",
     f"{BASE}/mypreferences/d/change-password"),
    ("a third party's details page", f"{BASE}/in/someone-else/details/skills/"),
)

#: (census row(s), what the row asks for, the address that would serve it)
CANDIDATES: tuple[tuple[str, str, str], ...] = (
    # --- the job-search endpoint as a filter language -------------------
    ("J 10", "filter a job search by company",
     f"{BASE}/jobs/search/?keywords=engineer&f_C={PAGE_ID}"),
    ("J 107", "see all jobs at this company",
     f"{BASE}/jobs/search/?f_C={PAGE_ID}"),
    ("J 151", "several locations in one search",
     f"{BASE}/jobs/search/?keywords=engineer&f_PP=106164952%2C102713980"),
    ("J 37 J 38", "re-run the search an alert was built from",
     f"{BASE}/jobs/search/?keywords=Senior+Software+Engineer&f_TPR=r86400"),
    ("J 15 J 16", "the All-filters panel and the suggested-filter chips",
     f"{BASE}/jobs/search/?keywords=engineer"),
    # --- addresses LinkedIn ITSELF hands over, and the boundary refuses --
    ("J 37 J 38", "the address LinkedIn's own alert notification links to",
     f"{BASE}/jobs/search-results/?keywords=Senior+Software+Engineer"),
    ("J 38", "the address LinkedIn's own alert EMAIL links to",
     f"{BASE}/comm/jobs/search-results/?keywords=Senior+Software+Engineer"),
    ("--", "a job posting as LinkedIn's own email addresses it",
     f"{BASE}/comm/jobs/view/{JOB_ID}/"),
    ("--", "a job posting as this server addresses it",
     f"{BASE}/jobs/view/{JOB_ID}/"),
    # --- pages already open, rows filed against the control's surface ----
    ("P J4", "the #Hiring line on his own topcard", f"{BASE}/in/me/"),
    ("P E6 P E7 N 114", "endorsements he RECEIVED, on his own skills page",
     f"{BASE}/in/me/details/skills/"),
    ("P A25-A29", "the contact-info panel, reached from the intro editor",
     f"{BASE}/in/me/edit/intro/"),
    ("P O3 N 133 N 134 N 136", "the profile-views page with a filter in the url",
     f"{BASE}/analytics/profile-views/?timeRange=past_90_days"),
    ("P G7 N 132", "search appearances", f"{BASE}/analytics/search-appearances/"),
    ("J 127", "the InMail credit balance", f"{BASE}/premium/my-premium/"),
    ("N 169 N 187", "a filtered read over his own connections",
     f"{BASE}/mynetwork/invite-connect/connections/"),
    ("M C60 N 173 N 174", "his own groups", f"{BASE}/groups/"),
    ("N 180", "his own events", f"{BASE}/events/"),
    ("M C43 M C34 N 148", "one post, by permalink",
     f"{BASE}/feed/update/urn:li:activity:0000000000000000000/"),
    ("M C74", "the feed itself", f"{BASE}/feed/"),
    ("M M47 M M10", "one conversation", f"{BASE}/messaging/thread/2-ABCdef123/"),
    ("P N12", "the sign-in form, as the census names it", f"{BASE}/uas/login"),
    ("P N12", "the sign-in form, as this server opens it", f"{BASE}/login"),
    # --- routes that read like reads and are refused by write words -----
    ("N 39 N 40", "the list of people he previously unfollowed",
     f"{BASE}/mypreferences/d/unfollowed"),
    ("N 38", "the list of people he follows",
     f"{BASE}/mynetwork/network-manager/people-follow/following/"),
    ("N 44 P L2b", "his own follower list",
     f"{BASE}/mynetwork/network-manager/people-follow/followers/"),
    ("J 33 J 34", "the job-alerts page", f"{BASE}/jobs/alerts/"),
    ("J 18 J 19", "recent job searches", f"{BASE}/jobs/search-history/"),
    ("J 42 J 125", "a job collection", f"{BASE}/jobs/collections/top-applicant/"),
    ("M C36 M C37", "saved posts", f"{BASE}/my-items/saved-posts/"),
    ("J 106 J 108-J 111", "a company Page, whose SLUG carries a forbidden word",
     f"{BASE}/company/connectwise/"),
    ("J 112 N 99 N 100", "a school's alumni tab",
     f"{BASE}/school/example-university/people/"),
)


def verdict(url: str) -> str:
    try:
        readonly.assert_read_url(url)
    except Exception as exc:  # noqa: BLE001 - the gate raises exactly one type
        message = str(exc)
        hit = re.search(r"contains '([^']+)'", message)
        if hit:
            both = "AND NO READ PATTERN" in message
            return (
                f"REFUSED-FORBIDDEN[{hit.group(1)}]"
                + ("-AND-NO-PATTERN" if both else "-PATTERN-WOULD-ADMIT")
            )
        return "REFUSED-NO-PATTERN"
    return "ALLOWED"


def main() -> int:
    failures = 0
    print("CONTROLS")
    for why, url in MUST_ALLOW:
        got = verdict(url)
        ok = got == "ALLOWED"
        failures += 0 if ok else 1
        print(f"  must-allow   {'ok ' if ok else 'FAIL'}  {got:44s} {why}")
    for why, url in MUST_REFUSE:
        got = verdict(url)
        ok = got != "ALLOWED"
        failures += 0 if ok else 1
        print(f"  must-refuse  {'ok ' if ok else 'FAIL'}  {got:44s} {why}")
    print(f"\ncontrol failures: {failures}")
    if failures:
        print("CONTROLS FAILED. The table below is not a reading.")
        return 1

    print(f"\nallowlist patterns at HEAD: {len(readonly._ALLOWED_URL_PATTERNS)}")
    print(f"forbidden substrings at HEAD: {len(readonly._FORBIDDEN_URL_SUBSTRINGS)}")

    allowed = 0
    print("\nROUTES")
    for rows, what, url in CANDIDATES:
        got = verdict(url)
        allowed += got == "ALLOWED"
        print(f"  {got:44s} {rows:22s} {what}")
        print(f"  {'':44s} {url}")
    print(f"\n{allowed} of {len(CANDIDATES)} candidate routes ALLOWED at HEAD.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
