"""ONE detail page of a profile he names -- ruling NAMED-PROFILE-DETAIL-PAGES (lane NP, 2026-10-10).

THE RULING, verbatim in ``_audit/2026-10-10-rulings-named-profile-detail-pages.md``:
"the read of a profile he names includes that SAME profile's own detail pages
(/in/<the same slug>/details/<section>/), one load per call, behind the same
single-use grant and the same preview warning." It APPLIES
NAMED-PROFILE-READ-BEHIND-A-GRANT (the operator, 2026-09-28 08:01) and narrows
nothing in it.

WHY IT EXISTS. The live lane's session 7 read a first-degree profile the
operator named, once: its first render drew no Interests section and no group
link. Census rows ``N 178`` (which groups a member belongs to) and ``N 65`` (a
member's Interests) are about that section, which LinkedIn draws in full on the
profile's own detail page, ``/in/<slug>/details/interests/``. No door reached it.

WHAT IS BUILT, AND WHAT IS NOT. The preview (nothing loaded, the same warning,
a token bound to that one address), and the ONE confirmed load through the
third check (``readonly.assert_named_profile_details_url``, which takes the
segment he named). The load returns WHAT THE PAGE SHOWED as counts and nothing
else: NO capture of this page exists, so no reader of its entries is built -- a
reader built on synthetic markup moves no row, and failed live once already.
The capture spec and the reader design are in
``_audit/2026-10-10-lane-np-named-profile.md`` (D.2, D.3): the first confirmed
load of it, on a member he names, is what the next live session saves.

A LANDING ELSEWHERE VETOES THE READ: on his own account
``/in/me/details/interests/`` REDIRECTED to the profile (2026-09-04, the note at
its allowlist entry in ``readonly.py``), and a landing this server did not
compose names nobody it can vouch for (PAGE-MAY-VETO-NEVER-SUPPLY).
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from linkedin_server import coerce, named_profile, readonly
from linkedin_server.config import logger
from linkedin_server.errors import WriteAttemptError

#: The counts the confirmed load takes, each a locator count -- no script, no
#: string. Hints for the capture the next session saves; no field is built on
#: any of them.
HINT_SELECTORS: tuple[tuple[str, str], ...] = (
    ("group_links", 'a[href*="/groups/"]'),
    ("company_links", 'a[href*="/company/"]'),
    ("member_links", 'a[href*="/in/"]'),
    ("newsletter_links", 'a[href*="/newsletters/"]'),
    ("school_links", 'a[href*="/school/"]'),
    ("tabs", '[role="tab"]'),
    ("list_items", "li"),
    ("headings", "h1, h2, h3"),
)


def section_word(value: Any) -> str:
    """The detail page's section, one word of the closed vocabulary, or raise
    before anything is minted or loaded. The refusal lists the vocabulary and
    never quotes what was given."""
    text = str(value if value is not None else "").strip()
    if text not in readonly.NAMED_PROFILE_DETAIL_SECTIONS:
        raise WriteAttemptError(
            "section takes one of "
            + ", ".join(readonly.NAMED_PROFILE_DETAIL_SECTIONS)
            + " -- the detail pages measured on your own profile -- and nothing "
            "else. Nothing was loaded and no token was issued."
        )
    return text


def details_address(segment: str, section: str) -> str:
    """The ONE detail page the read may load, through the third check -- or a
    refusal that QUOTES NOTHING (an address can carry a person's name)."""
    try:
        return readonly.assert_named_profile_details_url(
            readonly.named_profile_details_url(segment, section), segment
        )
    except WriteAttemptError:
        raise WriteAttemptError(
            "the detail page you named is not one this server's navigation "
            "boundary admits for that profile (a refused word in the address, "
            "say), so it will not be loaded. Nothing was loaded and no token "
            "was issued."
        ) from None


def read_preview(segment: str, section: str) -> dict[str, Any]:
    """The first call for a detail page: NOTHING IS LOADED. The address, the
    same warning as the profile's, and a token bound to that address."""
    address = details_address(segment, section)
    grant = named_profile.mint_read_grant(segment, address=address)
    return {
        "action": named_profile.READ_ACTION,
        "loaded": False,
        "pages_loaded": 0,
        "page_this_loads": grant.target,
        "section": section,
        "whom_this_resolves_to": None,
        "whom_this_resolves_to_why": (
            "NOT READ, AND ON PURPOSE: loading the page IS the view this "
            "confirmation asks you for. The address above is composed from the "
            "link you gave and the section you named -- CHECK THE LINK: a link "
            "that names the wrong person is the one failure this preview cannot "
            "catch for you."
        ),
        "they_may_see_this_view": (
            "LinkedIn may show this member that you viewed their profile -- "
            "among the people who viewed it, in the way your own "
            "profile-viewing setting presents you -- and a view cannot be "
            "taken back. Confirming loads this one page of their profile ONCE; "
            "this preview loaded nothing."
        ),
        "on_confirm": {
            "pages_loaded": 1,
            "entries": (
                "ABSENT: no capture of this page exists, so its entries are not "
                "read (NEEDS-CAPTURE C-NP1); you get what the page showed, as "
                "counts, and whether LinkedIn served the page at all"
            ),
        },
        "confirm_token": grant.token,
        "expires_in_seconds": int(named_profile.READ_GRANT_TTL_SECONDS),
        "kept": (
            "nothing: what the confirmed read returns is in no grant, no log "
            "and no file of this server's"
        ),
    }


def check_token(token: Any, segment: str, section: str) -> None:
    """The token's refusal, if it would be refused, BEFORE a session opens."""
    named_profile.check_read_token(token, segment, address=details_address(segment, section))


async def load_the_confirmed_details(
    navigator: Any, page: Any, *, token: str, segment: str, section: str
) -> str:
    """The ONE load a confirmed details read makes. Returns the landing for the
    reader to COMPARE, never for anything to navigate by or print.

    The token is redeemed FIRST, for this very address, and the grant marked
    loaded BEFORE the navigation, as :func:`named_profile.load_the_confirmed_profile`
    does. The navigator checks the address with the THIRD check, handed the
    segment he named, so a detail page of anybody else is refused at the door.
    """
    from linkedin_server.auth import assert_not_authwall

    details_page = details_address(segment, section)
    grant = named_profile.consume_read_grant(token, segment, address=details_page)
    if grant.loaded:
        raise WriteAttemptError(
            "this grant has already loaded its page once. A read token buys one load."
        )
    grant.loaded = True
    # THE THIRD CHECK, ASKED HERE as well as by the navigator, against the
    # segment he named -- the navigation guard counts it only at this site.
    details_page = readonly.assert_named_profile_details_url(details_page, segment)
    details_landing = str(
        await navigator.goto(page, details_page, named_profile_details_of=segment) or ""
    )
    assert_not_authwall(details_landing, surface="profile")
    return details_landing


def landed_on_details(landed: Any, segment: str, section: str) -> bool:
    """Did the browser land on THIS detail page? A comparison, never an address:
    LinkedIn's host, ``/in/<segment>/details/<section>/`` (the slash optional),
    the segment compared as :func:`named_profile.same_segment` compares it, the
    section exactly. A query LinkedIn appends is not read."""
    try:
        parts = urlsplit(str(landed or ""))
    except ValueError:
        return False
    if parts.scheme != "https" or parts.netloc.lower() != "www.linkedin.com":
        return False
    pieces = [piece for piece in (parts.path or "").split("/") if piece]
    if len(pieces) != 4 or pieces[0] != "in" or pieces[2] != "details":
        return False
    return named_profile.same_segment(pieces[1], str(segment)) and pieces[3] == section


async def read_the_confirmed_details(
    page: Any, *, segment: str, section: str, landed: str
) -> dict[str, Any]:
    """The confirmed details read's answer: whether LinkedIn served the page,
    and what it showed, as COUNTS. Reads; never navigates, presses or scrolls.
    No entry is read: no capture of this page exists (NEEDS-CAPTURE C-NP1)."""
    out: dict[str, Any] = {
        "action": named_profile.READ_ACTION,
        "loaded": True,
        "pages_loaded": 1,
        "page_loaded": details_address(segment, section),
        "section": section,
        "landed_on_the_details_page": False,
        "entries": None,
        "entries_why": (
            "ABSENT: no capture of this page exists, so no reader of its "
            "entries is built (NEEDS-CAPTURE C-NP1 in lane NP's record) -- a "
            "reader built on invented markup moves no census row."
        ),
        "what_the_page_showed": {},
        "the_view": (
            "the page was loaded once: LinkedIn may show this member that you "
            "viewed their profile, and that cannot be undone."
        ),
        "kept": "nothing: this answer is in no grant, no log and no file.",
    }
    if not landed_on_details(landed, segment, section):
        out["landed_why"] = (
            "LinkedIn did not serve the detail page you named -- it sent the "
            "browser elsewhere (on your own account, the Interests detail page "
            "redirected to the profile, 2026-09-04) -- so nothing is read off "
            "that page. The landing is withheld."
        )
        return out
    out["landed_on_the_details_page"] = True
    showed: dict[str, Any] = {}
    for name, selector in HINT_SELECTORS:
        try:
            showed[name] = coerce.as_count(await page.locator(selector).count())
        except Exception as exc:  # noqa: BLE001 - a hint; a failure is its type
            logger.debug("details hint unreadable: %s", type(exc).__name__)
            showed[name] = None
    out["what_the_page_showed"] = showed
    return out
