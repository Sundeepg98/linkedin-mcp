"""Is the account entitled to Premium -- and which states does that NOT settle?

ONE PAGE LOAD ON AN ADDRESS ALREADY ADMITTED. ``/premium/my-premium/`` is on
the read allowlist and has never been opened, so this repository holds a door
rather than a room -- the same shape ``A boundary opened with nothing behind
it`` names, and the reason row 56 (``PREMIUM-READER-NOT-BUILT``) exists.

## THE THREE-STATE PROBLEM THIS EXISTS TO NARROW, AND IT WILL NOT CLOSE IT

Census rows ``J 25``, ``J 29`` and ``J 30`` were retired on a measurement: the
control *Show match details / Show Premium Insights / How you match* reproduces
1/1/0 on four committed captures and twice live, so the match-insight panel is
**not drawn for this account**. Against that sits an understanding that the
account carries a Premium subscription. One reading, three states:

    A  not entitled
    B  entitled, and the panel is simply not drawn on those postings
    C  entitled, the panel IS drawn, and the reader could not see it

**THIS LOAD SEPARATES A FROM {B, C} AND DOES NOTHING ABOUT B VERSUS C.** Said
plainly and up front because a number that silently picks one state is worse
than no number. Entitlement lives on this page; whether a panel renders on a
JOB POSTING is a fact about a different surface, and no reading here can reach
it. Distinguishing B from C needs a posting load with the control firing, which
is a separate run and is not attempted.

## WHAT THIS PROBE MAY SAY, AND IT IS NOT PAGE TEXT

COUNTS AND RELATIONS ONLY. No accessible name, no label, no url, no plan name,
no price, no date leaves this process. A subscription page is dense with values
that are his, and ``tests/test_page_text_is_never_printed.py`` is the guard that
exists because a reader once believed otherwise. Every observable below is the
NUMBER OF CONTROLS whose accessible name matches a needle this repository
authors -- never the name that matched.

## THE MEASUREMENT THAT CONDITIONS THE LOAD

Every nav badge is read BEFORE and AFTER, and the run reports whether any moved.
An unmeasured cost is precisely what ``/mynetwork/`` is refused for, and a first
load of any surface owes that reading. An UNREADABLE badge at either end refuses
rather than guessing: treating a failure as a zero is the defect this package
has met repeatedly.

**A zero BEFORE does not stop this run**, and the reason is the question rather
than the reading -- the same split ``_probe_newsletter_subscriptions_live.py``
draws. This asks whether THIS load spent something it passed; a zero before says
there was nothing pending to spend, which discharges that by absence. It leaves
the other question -- is this address free on a day something IS pending --
exactly as unmeasured as it found it, and the report says so in both places so
neither can be read as the other.

## ATTACH MODE ONLY

Chrome runs externally on the operator's real profile. A launch-mode session
opens a SECOND Chrome on that profile and downgrades it from 152 to
playwright's 151 -- the 2026-08-25 failure that cost the signed-in session.

Usage::

    LINKEDIN_CDP_ATTACH_TIMEOUT_MS=120000 LINKEDIN_CDP_ATTACH=1 \\
        LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_premium_entitlement.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config, dom, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL  # noqa: E402

#: THE ADDRESS UNDER TEST, built from the module constant and never from
#: anything the page chose -- the form ``test_navigation_is_never_derived.py``
#: recognises.
PREMIUM_URL = f"{BASE_URL}/premium/my-premium/"

#: Nav families, DERIVED from the href rather than typed beside it. The Me
#: control's accessible name is HIS NAME, so a badge sweep prints the family
#: taken off the path and never the label.
_FAMILY_PATHS = (
    "/mynetwork/",
    "/messaging/",
    "/notifications/",
    "/jobs",
    "/feed/",
    "/in/",
    "/groups/",
    "/learning",
)

#: Needles THIS REPOSITORY AUTHORS, matched case-folded against accessible
#: names. Counting them names nobody, because the count is of our own strings.
#:
#: TWO FAMILIES, AND THE PAIRING IS THE INSTRUMENT. A page offering to SELL a
#: subscription and a page offering to MANAGE one are different pages wearing
#: the same address. Either family alone is ambiguous -- an upsell can appear
#: beside a live subscription, and a "manage" verb can appear on a marketing
#: page -- so the verdict below reads the PAIR and refuses to collapse a tie.
_ENTITLED_NEEDLES = (
    "cancel subscription",
    "cancel premium",
    "manage subscription",
    "manage plan",
    "your plan",
    "billing",
    "next payment",
    "subscription details",
)
_UNENTITLED_NEEDLES = (
    "start free trial",
    "start your free trial",
    "try premium",
    "retry premium",
    "reactivate",
    "choose plan",
    "select plan",
    "upgrade to premium",
)


def _relation(landed: str, asked: str) -> str:
    """Did the address serve, or did LinkedIn send us elsewhere?

    ``/in/me/details/interests/`` is admitted and REDIRECTS, so an admitted
    address is not a served one and a probe that does not compare landed to
    requested cannot tell those apart.

    RETURNS A RELATION, NEVER A URL. Every branch yields a literal or an
    integer depth; no part of either input survives into the result.
    """
    if str(landed) == str(asked):
        return "SERVED, exact"
    asked_depth = len([seg for seg in urlsplit(str(asked)).path.split("/") if seg])
    landed_depth = len([seg for seg in urlsplit(str(landed)).path.split("/") if seg])
    if asked_depth != landed_depth:
        return f"REDIRECTED, path depth {asked_depth} -> {landed_depth}"
    return "SERVED, same depth, different url"


def _family_of(href: str | None) -> str:
    """The nav family a badge belongs to, derived from its own path."""
    if href is None:
        return "no-href (button)"
    for needle in _FAMILY_PATHS:
        if needle in href:
            return needle.strip("/")
    return "other"


async def _all_nav_badges(page) -> list[tuple[str, int | None, str]]:
    """``(family, count, state)`` for every nav control carrying a count.

    Reading them ALL costs no extra navigation and buys two things: a LIVE
    CONTROL (a non-zero badge anywhere proves the reader resolves real values
    on this render rather than returning a default zero), and a cost this
    experiment was not looking for -- a load that moves a DIFFERENT badge would
    be reported free by a probe watching only one.

    THE LABEL NEVER LEAVES THIS FUNCTION. Only the parsed number and the family.
    """
    out: list[tuple[str, int | None, str]] = []
    badges = page.locator('[aria-label*="%s"]' % dom.INVITATION_BADGE_TAIL)
    total = int(await badges.count())
    for index in range(total):
        item = badges.nth(index)
        href = await item.get_attribute("href") or ""
        label = await item.get_attribute("aria-label")
        verdict = shape.invitation_badge(
            {
                "links": 1,
                "badge_links": 1,
                "label": shape.census_shape(str(label or "").strip()) or None,
                "error": None,
            }
        )
        out.append((_family_of(href), verdict["pending"], verdict["state"]))
    return out


def _show_badges(title: str, rows: list[tuple[str, int | None, str]]) -> None:
    print("    %s -- %d nav control(s) carrying a count" % (title, len(rows)))
    for family, pending, state in sorted(rows):
        print("        %-16s pending=%-5r state=%s" % (family, pending, state))


async def _count_needles(page, needles: tuple[str, ...]) -> dict[str, int]:
    """How many controls carry each needle. NEVER which control, never its name.

    Factored OUT of the verdict that consumes it so it has a handle and can be
    aimed at a known-bad sample; logic inside the verdict could never be.

    It reads accessible names into a LOCAL and emits only integers. That local
    is the one place page text exists in this process and it does not escape
    the function.
    """
    tally = {needle: 0 for needle in needles}
    controls = page.locator("a, button")
    total = int(await controls.count())
    for index in range(min(total, 400)):
        try:
            name = (await controls.nth(index).inner_text(timeout=1000)) or ""
        except Exception:  # noqa: BLE001
            continue
        folded = name.strip().lower()
        if not folded:
            continue
        for needle in needles:
            if needle in folded:
                tally[needle] += 1
    return tally


def _entitlement_verdict(entitled_hits: int, unentitled_hits: int) -> str:
    """Name the STATE, and refuse to collapse a tie.

    THE VERDICT IS DELIBERATELY ABLE TO SAY 'CANNOT TELL'. A reading that cannot
    separate states must say so -- this whole probe exists because one reading
    was being asked to settle three states at once.
    """
    if entitled_hits and not unentitled_hits:
        return "ENTITLED -- management verbs present, no sales verbs"
    if unentitled_hits and not entitled_hits:
        return "NOT ENTITLED -- sales verbs present, no management verbs"
    if entitled_hits and unentitled_hits:
        return (
            "AMBIGUOUS -- both families present. An upsell can sit beside a "
            "live subscription; this does not resolve and does not guess"
        )
    return (
        "NEITHER FAMILY MATCHED -- a reading about this INSTRUMENT, not about "
        "the account. Either the page draws neither vocabulary or the aim is "
        "wrong, and a zero from an aim nobody has validated is not evidence"
    )


async def main() -> int:
    """Run the probe and ALWAYS give the tab back.

    ``BROWSER.session()`` in attach mode opens a tab of its own and caches it;
    its ``finally`` does not close it. Leaked tabs accumulate on a browser
    nobody restarts and the bill arrives at the HANDSHAKE -- ``connect_over_cdp``
    enumerates every target, so at 120 targets attach takes 13-17s against a
    15s ceiling and becomes a coin flip.

    ``BROWSER.stop()`` closes the PAGE and drops the CDP connection, and in
    attach mode explicitly does NOT close the context, because the context is
    his own browser session. It never raises, so it is safe here even on the
    path where the attach gate refuses before anything started.
    """
    try:
        return await _run()
    finally:
        await BROWSER.stop()


async def _run() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print("    A launch-mode session opens a SECOND Chrome on the "
              "operator's profile and downgrades it.")
        return 2

    print("=" * 74)
    print("PREMIUM ENTITLEMENT -- the first load of an admitted address")
    print("=" * 74)

    admitted = readonly.is_read_url(PREMIUM_URL)
    print("\n0. THE BOUNDARY -- asked before the browser is touched")
    print("    the address under test is admitted: %r" % admitted)
    print("    NO ALLOWLIST CHANGE IS MADE BY THIS RUN.")
    if not admitted:
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    async with BROWSER.session() as page:
        try:
            print("\n1. PRE -- badges read off the feed's nav")
            feed_landed = await BROWSER.goto(page, FEED_URL)
            if "/login" in str(feed_landed) or "/checkpoint" in str(feed_landed):
                print("    AUTH WALL on the feed. Nothing loaded, nothing spent.")
                return 1
            print("    feed relation: %s" % _relation(feed_landed, FEED_URL))

            reading_pre = await dom.read_invitation_badge(page)
            badge_pre = shape.invitation_badge(reading_pre)
            print("    mynetwork badge: pending=%r state=%r"
                  % (badge_pre["pending"], badge_pre["state"]))
            nav_pre = await _all_nav_badges(page)
            _show_badges("all nav badges", nav_pre)
            live = [row for row in nav_pre if (row[1] or 0) > 0]
            print("    instrument control: %d of %d badges read NON-ZERO%s"
                  % (len(live), len(nav_pre),
                     "" if live else "   <-- nothing here could show a drop"))

            if badge_pre["state"] != "read":
                print("\nSTOPPED: the pending-invitation badge is UNREADABLE.")
                print("    Nothing loaded beyond the feed, so nothing was spent. "
                      "An unreadable pre cannot anchor a post.")
                return 1

            print("\n2. THE LOAD UNDER TEST")
            landed = await BROWSER.goto(page, PREMIUM_URL)
            relation = _relation(landed, PREMIUM_URL)
            walled = "/login" in str(landed) or "/checkpoint" in str(landed)
            print("    relation: %s" % relation)
            print("    authwall: %r" % walled)
            served = relation.startswith("SERVED") and not walled

            print("\n3. POST -- badges read off the loaded page's own nav")
            reading_post = await dom.read_invitation_badge(page)
            badge_post = shape.invitation_badge(reading_post)
            print("    mynetwork badge: pending=%r state=%r"
                  % (badge_post["pending"], badge_post["state"]))
            nav_post = await _all_nav_badges(page)
            _show_badges("all nav badges", nav_post)

            print("\n4. DID ANYTHING MOVE?")
            if badge_post["state"] != "read":
                print("    UNREADABLE POST. The page was opened, so whatever it "
                      "costs has been spent, and this run CANNOT say what that "
                      "was. Reported rather than guessed.")
            moved = {}
            pre_map = {family: count for family, count, _ in nav_pre}
            post_map = {family: count for family, count, _ in nav_post}
            for family in sorted(set(pre_map) | set(post_map)):
                if pre_map.get(family) != post_map.get(family):
                    moved[family] = (pre_map.get(family), post_map.get(family))
            print("    nav families that MOVED: %d" % len(moved))
            for family, (was, now) in sorted(moved.items()):
                print("        %-16s %r -> %r" % (family, was, now))
            print("    mynetwork pending: %r -> %r"
                  % (badge_pre["pending"], badge_post["pending"]))
            if badge_pre["pending"] == 0:
                print("    SAFETY  discharged by ABSENCE -- nothing pending "
                      "was consumed, because nothing was pending.")
                print("    COST    UNMEASURED -- and it stays unmeasured until a "
                      "day the badge is not zero. These are two claims and this "
                      "run makes only the first.")

            if not served:
                print("\n5. NOT SERVED. No entitlement reading is taken, because a "
                      "vocabulary count on a page that did not serve measures the "
                      "redirect target.")
                return 1

            print("\n5. ENTITLEMENT -- counts of OUR OWN needles, never a label")
            entitled = await _count_needles(page, _ENTITLED_NEEDLES)
            unentitled = await _count_needles(page, _UNENTITLED_NEEDLES)
            entitled_hits = sum(entitled.values())
            unentitled_hits = sum(unentitled.values())
            print("    management-verb matches: %d across %d needles"
                  % (entitled_hits, len([k for k, v in entitled.items() if v])))
            print("    sales-verb matches:      %d across %d needles"
                  % (unentitled_hits, len([k for k, v in unentitled.items() if v])))
            # WHICH NEEDLE FIRED, and this is safe to print where a label is not:
            # these strings are AUTHORED IN THIS FILE. Naming them describes our
            # own instrument, not the page. A verdict resting on ONE match is thin,
            # and a reader cannot weigh it without knowing which one -- "billing"
            # matching once and "cancel subscription" matching once are very
            # different pieces of evidence for the same integer.
            print("    needles that fired: %r"
                  % sorted(k for k, v in {**entitled, **unentitled}.items() if v))
            print("    VERDICT: %s" % _entitlement_verdict(entitled_hits,
                                                           unentitled_hits))
            if entitled_hits + unentitled_hits <= 1:
                print("    STRENGTH: THIN -- a single match. Reported as such "
                      "rather than rounded up to a settled reading.")

            print("\n6. WHAT THIS SETTLES, AND WHAT IT LEAVES OPEN")
            print("    SETTLES   state A (not entitled) versus {B, C}, and only "
                  "to the strength of the verdict above.")
            print("    LEAVES OPEN   B versus C -- entitled-but-not-drawn versus "
                  "drawn-but-unread on a JOB POSTING. That is a different "
                  "surface and NO reading taken here can reach it.")
            print("    A posting load with the 1/1/0 control firing is the next "
                  "step and is NOT attempted by this run.")

            return 0
        finally:
            # CLOSE THE TAB THIS RUN OPENED, on every path out of this block.
            # BELT AND SUSPENDERS beside BROWSER.stop() in main(): that call
            # also closes this same page (tolerantly, if already closed), but
            # it does so inside browser.py -- the static ratchet in
            # tests/test_a_probe_closes_its_own_tab.py can only see a receiver
            # named page/tab/_own_page in THIS file. THE PAGE, NEVER THE
            # CONTEXT.
            if not page.is_closed():
                await page.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
