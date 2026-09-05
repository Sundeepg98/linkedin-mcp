"""Put every newsletter route through the read gate at HEAD, before designing one.

THE QUESTION, and it is deliberately not the census's question. The census asks
where LinkedIn DRAWS a newsletter control, and for eleven of the thirteen
newsletter rows the answer is "on a page nobody here has opened". This asks
instead: **what address SERVES the capability, and does
``readonly.assert_read_url`` admit it today** -- the shape that moved fourteen
rows in ``_audit/2026-09-05-routes-already-admitted.md``.

IT MATTERS HERE MORE THAN IT DID THERE, because this blocker's rows have been
filed against two surfaces that are both dead ends and neither of them is where
the data lives:

* the profile Interests tab draws a **Newsletters** category as a
  ``div role="radio"`` with no href, and a category's rows are not in the
  document until its tab is pressed;
* ``/in/me/details/interests/`` is on the allowlist AND LINKEDIN REDIRECTS IT
  to the profile -- measured, with two same-run siblings as the control
  (``readonly.py:405-419``).

Meanwhile ``dom.py:7239-7256`` records, from a live nav read taken on
2026-09-04 while hunting the invitation badge, that the feed draws
``.../mynetwork/network-manager/newsletters/`` -- an address whose SIBLING
``/mynetwork/network-manager/company/`` this server has opened since
2026-08-23. That href is not a guess and it is not this file's find; it is a
constant this repository already measured and then walked past, and the whole
purpose of running the gate over it is to say what the boundary does with it
rather than to assume.

CONTROLS FIRST, BOTH DIRECTIONS, and one refusal by substring rather than by
pattern -- a gate that admits everything and a gate that refuses everything
both draw a clean-looking table.

Read-only. No browser, no session, no page load, no ``mcp__linkedin__*`` call.
Every address is a repo constant, a shape this package already builds, or a
path the census quotes. No member name, no member id, no newsletter this
account subscribes to.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from linkedin_server import readonly  # noqa: E402

BASE = "https://www.linkedin.com"

#: A NEWSLETTER SLUG SHAPE, NOT A NEWSLETTER, and both halves are constrained.
#:
#: The literal spelling is lifted from ``tests/test_membership_row.py``, which
#: is tracked and has passed ``test_no_committed_identity`` since 2026-09-04 --
#: so it is a value this repository's identity guard has already looked at and
#: admitted, rather than a fresh string that has to argue for itself.
#:
#: SIX DIGITS, deliberately. That is the minimum ``_CENSUS_LONG_DIGITS``
#: reduces, so the probe exercises the digit rule while wearing no real
#: identifier's shape. An earlier probe in this package had a ten-digit id
#: opening with a 7 refused for wearing a mobile number's shape.
NEWSLETTER_SLUG = "weekly-123456"

#: A SECOND SLUG, CARRYING NO DIGITS AT ALL, because the two newsletter
#: addresses differ in more than length: LinkedIn builds a newsletter's slug
#: out of its TITLE, and a title is routinely its author's name. A route table
#: that only ever tested the digit form would not have exercised the shape the
#: page actually writes.
NEWSLETTER_SLUG_WORDS = "a-made-up-letter"

MUST_ALLOW: tuple[tuple[str, str], ...] = (
    ("the feed", f"{BASE}/feed/"),
    ("his own profile", f"{BASE}/in/me/"),
    # THE ONE THAT CARRIES THE ARGUMENT. If this ever stops being ALLOWED the
    # whole route claim below collapses, because it is the precedent the
    # newsletters sibling is asked for on.
    ("the Pages he follows -- the network-manager sibling",
     f"{BASE}/mynetwork/network-manager/company/"),
)
MUST_REFUSE: tuple[tuple[str, str], ...] = (
    ("My Network itself -- the badge-consuming parent",
     f"{BASE}/mynetwork/"),
    ("a company Page", f"{BASE}/company/example-co/"),
    ("a third party's interests tab",
     f"{BASE}/in/someone-else/details/interests/"),
    # REFUSED BY SUBSTRING RATHER THAN BY PATTERN. Without this the table
    # cannot show that the two gates are distinguishable at all.
    ("the people he follows -- substring, not pattern",
     f"{BASE}/mynetwork/network-manager/people-follow/following/"),
)

#: (census row(s), what the row asks for, the address that would serve it)
CANDIDATES: tuple[tuple[str, str, str], ...] = (
    # --- the read half -------------------------------------------------
    ("N 57", "the newsletters he subscribes to, as the LIVE NAV addresses it",
     f"{BASE}/mynetwork/network-manager/newsletters/"),
    ("N 57", "the same, without the trailing slash the nav actually writes",
     f"{BASE}/mynetwork/network-manager/newsletters"),
    ("N 57", "the same list as the census imagines it -- a product root",
     f"{BASE}/newsletters/"),
    ("N 57", "the same list on the profile tab that DRAWS the control",
     f"{BASE}/in/me/details/interests/"),
    # --- one newsletter, which is where the reader-side writes are drawn -
    ("M C80 N 55 N 56 M C82", "one newsletter's own page, digit-form slug",
     f"{BASE}/newsletters/{NEWSLETTER_SLUG}/"),
    ("M C80 N 55 N 56 M C82", "one newsletter's own page, word-form slug",
     f"{BASE}/newsletters/{NEWSLETTER_SLUG_WORDS}/"),
    # --- the author half -----------------------------------------------
    ("M C50 P L3", "the create-a-newsletter route off the article editor",
     f"{BASE}/article/new/?isNewsletter=true"),
    ("M C51 M C84 P L3", "manage the newsletters he authors",
     f"{BASE}/newsletters/manage/"),
    ("M C81", "create a Newsletter Page",
     f"{BASE}/newsletters/create/"),
    # --- analytics, filed here by name and costed elsewhere -------------
    ("M C83 P L4", "newsletter analytics, the creator-hub form",
     f"{BASE}/analytics/newsletter/"),
    ("M C83 P L4", "newsletter analytics, the per-newsletter form",
     f"{BASE}/newsletters/{NEWSLETTER_SLUG}/analytics/"),
    # --- the email half of N 58, which is not a linkedin.com address ----
    ("N 58", "unsubscribe from the EMAILS while staying subscribed on the feed",
     f"{BASE}/mypreferences/d/categories/notifications"),
)


def verdict(url: str) -> str:
    """ALLOWED, or a refusal that names WHICH gate fired and whether the other would.

    The gate's message reports, on a substring refusal, whether a read pattern
    would have admitted the address anyway -- and the two are different
    findings. Three readers of this package have taken a substring refusal for
    the wall when it was merely the first gate.
    """
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
    print(
        "\nALLOWED IS NOT SERVED. /in/me/details/interests/ is on the allowlist "
        "and LinkedIn redirects it; nothing here claims a page exists."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
