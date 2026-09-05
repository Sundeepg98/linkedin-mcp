"""Does he subscribe to any newsletter, and does that page serve at all?

ONE PAGE LOAD, AND IT SETTLES FOUR THINGS. The address
``/mynetwork/network-manager/newsletters/`` was admitted to the read allowlist
on 2026-09-05 and has NEVER BEEN OPENED. Until it is, this repository holds a
door rather than a room:

  1. does LinkedIn SERVE it, or redirect it the way it redirects
     ``/in/me/details/interests/`` -- which is admitted, was admitted for this
     exact precondition, and does not serve;
  2. does he subscribe to any newsletter at all. **If zero, five of
     ``NEWSLETTER-SURFACE``'s rows are unreachable in principle for this
     account** and a twelve-row blocker is a one-row blocker;
  3. does the page also list newsletters he AUTHORS, which is the separate
     precondition under five more rows and which no measurement supports today;
  4. is an unsubscribe control drawn HERE, which would take census ``N 56``
     from two blockers to one.

## THE OBLIGATION, AND IT IS NOT OPTIONAL

``/mynetwork/`` is refused because opening it is BELIEVED to consume the
pending-invitation badge. This is a sub-page of it. ``linkedin_connections``
does not rely on the belief -- it reads the badge before and after and REFUSES
when it cannot -- and ``dom.read_invitation_badge`` costs no page load, because
the nav renders on every signed-in page. So this probe reads the badge
immediately BEFORE and immediately AFTER the load, and:

  * an UNREADABLE before means the load does not happen at all. An unreadable
    reading cannot anchor an after, and treating a failure as a zero is the
    defect this package has now met five times;
  * an UNREADABLE after, or a badge that MOVED, means the rows are NOT
    PUBLISHED. The page was opened, so whatever it costs has been spent, and
    the honest report is that this run cannot say what that was.

## THE ZERO CASE IS DIFFERENT HERE THAN IT IS NEXT DOOR, AND THE DIFFERENCE IS
## THE QUESTION RATHER THAN THE READING

``_probe_connections_badge_cost.py`` STOPS on a zero before, and is right to:
its question is *what does this address cost*, and a zero cannot decrement, so
an "unchanged" would agree with a story it had no power to refute.

**This probe's question is not that one.** It asks whether THIS read spent
something it passed. A badge reading zero before the load says there was
nothing pending to spend, which discharges that obligation by absence rather
than by comparison. It leaves the OTHER question -- is this address free for a
future load, when something IS pending -- exactly as unmeasured as it found it.

So a zero here does not stop the run, and this file does NOT record a cost off
it. Both halves are printed in one place so a later reader cannot take the
first for the second::

    SAFETY   discharged -- nothing pending was consumed, because nothing was
                           pending
    COST     UNMEASURED -- and it stays unmeasured until a day the badge is
                           not zero

## WHAT LEAVES THIS PROCESS

COUNTS, RELATIONS, MARKERS AND BOOLEANS. Never a newsletter title, never a
slug, never a url, never a nav label.

**A NEWSLETTER TITLE IS THE DANGEROUS FIELD ON THIS SURFACE**, measured rather
than feared: a newsletter is authored BY A PERSON, and both its title and its
slug routinely carry that person's name
(``scripts/_probe_interests_entity_shaping.py``, 2026-09-04). So every row this
probe sees goes through :func:`shape.subscription_row`, which redacts the title
unconditionally -- and this file prints that function's RELATION rather than
its payload: published / refused, whether the redactor changed the string, how
long it is, and whether an authorship join survives. **The shape, never the
instance.**

The nav labels are handled the same way and for the same reason recorded in
``_probe_connections_badge_cost.py``: the Me control's accessible name is HIS
NAME, so a badge sweep prints the family taken off the href and never the
label.

## ATTACH MODE ONLY

Chrome runs externally on the operator's real profile and this attaches rather
than launching. A launch-mode session opens a SECOND Chrome on that profile and
downgrades it from 152 to playwright's 151 -- the 2026-08-25 failure that cost
the signed-in session. Asserted below; this script refuses without it.

Usage::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_newsletter_subscriptions_live.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config, dom, newsletters, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL  # noqa: E402

#: THE ADDRESS UNDER TEST. Built from the module constant, never from anything
#: the page chose, which is what makes it navigable under
#: ``tests/test_navigation_is_never_derived.py``.
NEWSLETTERS_URL = f"{BASE_URL}/mynetwork/network-manager/newsletters/"

#: The gitignored capture path. ``.gitignore:140`` matches ``*_probe-*.html``,
#: verified with ``git check-ignore -v`` before this file was written rather
#: than read off the pattern. A capture of this page is made of other people's
#: publications and must never be committable.
CAPTURE = ROOT / "_audit" / "_probe-newsletters-hyd.html"

#: The newsletter marker this package writes into a shaped href. It is a
#: PLACEHOLDER this repository authors, not a string LinkedIn serves, so
#: counting it names nobody.
NEWSLETTER_MARKER = "/newsletters/<newsletter>"

#: Which nav control a badge belongs to, decided by its HREF rather than by its
#: words -- the label's leading word is redacted in this repo's own audit and
#: the Me control's label is his name.
#:
#: ONE COLUMN, AND THE LABEL IS DERIVED RATHER THAN TYPED BESIDE THE PATH. The
#: sibling probe this was copied from writes ``("feed-or-home", "/feed/")``
#: pairs, and MEASURED, that shape trips
#: ``test_no_tracked_file_pairs_fixture_content_with_anything_else`` -- the
#: pre-image detector, whose rule is *one string in a committed fixture and
#: another not*. It counted three rows here and NAMED THEM: ``notifications``
#: present with ``/notifications/`` absent, ``/feed/`` present with
#: ``feed-or-home`` absent, ``learning`` present with ``/learning`` absent.
#:
#: **IT IS A FALSE POSITIVE AND IT WAS STILL FIXED RATHER THAN DECLARED.** Both
#: halves of every row are LinkedIn furniture and neither is a pre-image of
#: anything. But a declaration permanently widens what that guard tolerates for
#: this file, and the obvious alternative -- rewording the labels until each row
#: is both-present or both-absent -- ROTS: the detector's own note records that
#: ADDING A FIXTURE lights up tables nobody touched, so a fix tuned to today's
#: fixture blob is a fix with an expiry date. Deleting the second column removes
#: the shape permanently, because a row with one meaningful string is not a pair
#: at any blob.
#:
#: AND IT IS A BETTER TABLE FOR A REASON THAT HAS NOTHING TO DO WITH THE GUARD:
#: with two columns a label can silently disagree with its path and nothing
#: checks it. Derived, it cannot. That is ``shape.CENSUS_KEY_FIELDS``'s argument
#: one surface over -- the names and the order cannot disagree by construction.
#:
#: ``/in/`` derives to the label ``in``, which is his own profile control. The
#: label is terser than the ``self-profile`` it replaces and carries exactly the
#: same information: a family name, never the href, because the Me control's
#: href is ``/in/<his slug>``.
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


def _relation(landed: str, asked: str) -> str:
    """Did the address serve, or did LinkedIn send us somewhere else?

    THE INTERESTS LESSON, applied. ``/in/me/details/interests/`` is on the
    allowlist and REDIRECTS to the profile, so an admitted address is not a
    served one -- and a probe that does not compare the landed url to the
    requested one cannot tell those apart.

    RETURNS A RELATION AND NEVER A URL. Every branch below yields a literal or
    an integer depth; no part of either input survives into the result. The
    depths are taken with ``len`` rather than a helper, because counting a
    thing is the discipline this package uses INSTEAD of printing it, and
    ``tests/test_navigation_is_never_derived.py`` recognises that form.

    ITS LOCALS ARE NAMED FOR THIS FUNCTION, and that is not cosmetic. The
    consent guard tracks tainted names ACROSS A WHOLE MODULE, not per scope,
    so a local called ``before`` here made every ``before`` in this file read
    as navigation-derived -- including three in the cost report, which are
    tallies of shaped control names and touch no url at all. Three of that
    guard's four findings against this file were that collision.
    """
    if str(landed) == str(asked):
        return "SERVED, exact"
    asked_depth = len([seg for seg in urlsplit(str(asked)).path.split("/") if seg])
    landed_depth = len([seg for seg in urlsplit(str(landed)).path.split("/") if seg])
    if asked_depth != landed_depth:
        return f"REDIRECTED, path depth {asked_depth} -> {landed_depth}"
    return "SERVED, same depth, different url"


def _family_of(href: str | None) -> str:
    """The nav family a badge belongs to, DERIVED from its own path.

    The label cannot disagree with the path it came from, because it is made
    out of it. See :data:`_FAMILY_PATHS` for why that matters twice over.
    """
    if href is None:
        return "no-href (button)"
    for needle in _FAMILY_PATHS:
        if needle in href:
            return needle.strip("/")
    return "other"


async def _all_nav_badges(page) -> list[tuple[str, int | None, str]]:
    """``(family, count, state)`` for every nav control carrying a count.

    THE SECOND OBSERVABLE. The obligation names one badge; reading them all
    costs no extra navigation and buys two things this run cannot do without:
    a LIVE CONTROL (a non-zero badge anywhere on this nav proves the reader
    resolves real values on this render rather than returning a default zero),
    and a cost this experiment was not looking for -- if the load moves a
    DIFFERENT badge, a probe watching only one would report the page free.

    THE LABEL NEVER LEAVES THIS FUNCTION. Only the number parsed out of it and
    the family taken off the href.
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


def _row_relation(verdict: dict) -> str:
    """One :func:`shape.subscription_row` result, reduced to a RELATION.

    THE PAYLOAD IS THE THING THIS PROBE MUST NOT PRINT. That function's own
    floor is a CAPITALISED-RUN rule and not a name detector -- ``notes by
    alex`` survives it, asserted in its tests -- so printing its ``name`` would
    put this probe's output one lowercase title away from carrying an author.

    Everything the run actually needs is answerable without the string: did
    the gate publish, did the redactor fire, how long is what came back, and
    does an authorship join survive it (which is the property that makes
    ``<redacted> by <redacted>`` worth keeping over a bare count).
    """
    if not verdict.get("published"):
        return "REFUSED %s saw=%r" % (verdict.get("refused"), verdict.get("saw"))
    name = str(verdict.get("name") or "")
    return "published redacted=%-5r chars=%-3d joins=%r opaque=%r" % (
        bool(verdict.get("name_redacted")),
        len(name),
        " by " in name,
        shape.CENSUS_OPAQUE in name,
    )


async def _subscription_rows(page) -> list[dict]:
    """Every newsletter-marked anchor on the page, through the shipped gate.

    THE FIRST TIME :func:`shape.subscription_row` MEETS A REAL PAGE. It was
    built and red-proofed against synthetic input on 2026-09-05 by a wave that
    deliberately declined to build a reader, on the grounds that an aim written
    against a page nobody had opened fails CLOSED and reads as *he subscribes
    to nothing* -- the exact answer this surface exists to produce.

    This is not that reader and does not pretend to be. It is the widest
    possible aim -- every anchor whose href mentions the product -- so that a
    zero here is a fact about the PAGE rather than about a selector somebody
    guessed. A narrow aim is the next step and it needs the capture.
    """
    out: list[dict] = []
    anchors = page.locator('a[href*="/newsletters/"]')
    total = int(await anchors.count())
    for index in range(min(total, 60)):
        item = anchors.nth(index)
        href = await item.get_attribute("href")
        # THE ACCESSIBLE NAME, read and NEVER printed. It goes straight into
        # the gate, which is the only thing in this package allowed to decide
        # what may be said about it.
        try:
            name = await item.inner_text(timeout=2000)
        except Exception:  # noqa: BLE001
            name = ""
        out.append(shape.subscription_row(href, name))
    return out


async def main() -> int:
    """Run the probe and ALWAYS give the tab back.

    THIS WRAPPER IS A BUG FIX AND NOT A TIDY-UP, and the cost was measured on
    the whole fleet rather than on this file. ``BROWSER.session()`` in attach
    mode opens a tab of its own -- correctly, because navigating one of HIS
    tabs would yank a page out from under him -- and caches it. Its ``finally``
    touches the idle timer and does NOT close that tab. So every probe process
    that attaches leaves one behind, this one included: it ran twice today and
    leaked two.

    They accumulate on a browser nobody restarts, and the bill arrives
    somewhere else entirely: ``connect_over_cdp`` enumerates every target
    during the handshake, so at 120 targets the attach itself takes 13 to 17
    seconds against a 15-second ceiling. **Attach became a coin flip, and the
    refusal it produced blamed "Chrome not running" -- a refusal naming what it
    did NOT find instead of what it SAW, on a browser that was healthy
    throughout.**

    ``BROWSER.stop()`` closes the tab and drops the CDP connection, and in
    attach mode it explicitly does NOT close the context, because the context
    is his own browser session. It never raises, so it is safe in a ``finally``
    even on the path where the attach gate refuses before anything started.

    IN A ``finally``, so a probe that raises still gives the tab back. A
    cleanup that only runs on the success path is the one that never runs when
    it matters.
    """
    try:
        return await _run()
    finally:
        await BROWSER.stop()


async def _run() -> int:
    # ATTACH MODE IS A PRECONDITION, NOT A PREFERENCE.
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print("    Chrome runs externally on the operator's real profile and "
              "this script attaches to it. A launch-mode session opens a "
              "SECOND Chrome on that profile and downgrades it.")
        print("    Re-run with LINKEDIN_CDP_ATTACH=1 "
              "LINKEDIN_CDP_PORT=%d" % config.CDP_PORT)
        return 2

    print("=" * 74)
    print("NEWSLETTER SUBSCRIPTIONS -- the first load of an admitted address")
    print("=" * 74)
    print("attach mode, port %d. Report is SHAPED; the capture is raw and "
          "gitignored." % config.CDP_PORT)

    # THE BOUNDARY, ASKED BEFORE THE BROWSER IS TOUCHED. An address being on
    # the allowlist is this run's precondition and not its finding.
    admitted = readonly.is_read_url(NEWSLETTERS_URL)
    print("\n0. THE BOUNDARY")
    print("    the address under test is admitted: %r" % admitted)
    if not admitted:
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    async with BROWSER.session() as page:
        # --------------------------------------------------------------
        # 1. BEFORE, off the feed's nav. The feed is a page this server
        #    already loads for other reasons, so the anchor costs nothing
        #    that was not already being spent.
        # --------------------------------------------------------------
        print("\n1. BEFORE -- the badge, read off the feed's nav")
        feed_landed = await BROWSER.goto(page, FEED_URL)
        if "/login" in str(feed_landed) or "/checkpoint" in str(feed_landed):
            print("    AUTH WALL on the feed. Nothing else measured, nothing "
                  "captured, nothing loaded.")
            return 1
        print("    feed relation: %s" % _relation(feed_landed, FEED_URL))

        reading_pre = await dom.read_invitation_badge(page)
        badge_pre = shape.invitation_badge(reading_pre)
        print("    mynetwork badge: pending=%r state=%r"
              % (badge_pre["pending"], badge_pre["state"]))
        print("    why: %s" % badge_pre["why"])
        print("    saw: mynetwork_links=%r links_carrying_a_count=%r"
              % (reading_pre["links"], reading_pre["badge_links"]))
        nav_pre = await _all_nav_badges(page)
        _show_badges("all nav badges", nav_pre)

        live = [row for row in nav_pre if (row[1] or 0) > 0]
        print("    instrument control: %d of %d badges read NON-ZERO%s"
              % (len(live), len(nav_pre),
                 "" if live else "   <-- nothing on this nav could show a drop"))

        # THE GATE THAT CAN END THE RUN BEFORE ANYTHING IS SPENT.
        if badge_pre["state"] != "read":
            print("\nSTOPPED: the pending-invitation badge is UNREADABLE.")
            print("    Nothing was loaded beyond the feed, so nothing was "
                  "spent. An unreadable before cannot anchor an after, and "
                  "this refuses rather than treating the failure as a zero.")
            return 1

        # --------------------------------------------------------------
        # 2. THE LOAD UNDER TEST.
        # --------------------------------------------------------------
        print("\n2. THE LOAD UNDER TEST")
        landed = await BROWSER.goto(page, NEWSLETTERS_URL)
        relation = _relation(landed, NEWSLETTERS_URL)
        walled = "/login" in str(landed) or "/checkpoint" in str(landed)
        print("    relation: %s" % relation)
        served = relation.startswith("SERVED") and not walled
        print("    authwall: %r" % walled)

        # --------------------------------------------------------------
        # 3. AFTER, off whatever page we are now on. No third navigation.
        # --------------------------------------------------------------
        print("\n3. AFTER -- the badge, read off the loaded page's own nav")
        reading_post = await dom.read_invitation_badge(page)
        badge_post = shape.invitation_badge(reading_post)
        print("    mynetwork badge: pending=%r state=%r"
              % (badge_post["pending"], badge_post["state"]))
        print("    saw: mynetwork_links=%r links_carrying_a_count=%r"
              % (reading_post["links"], reading_post["badge_links"]))
        nav_post = await _all_nav_badges(page)
        _show_badges("all nav badges", nav_post)

        # --------------------------------------------------------------
        # 4. THE OBLIGATION'S VERDICT, DECIDED BEFORE ANY ROW IS READ.
        # --------------------------------------------------------------
        print("\n4. THE OBLIGATION")
        moved = [
            (fam_pre, count_pre, count_post)
            for (fam_pre, count_pre, _s1), (fam_post, count_post, _s2)
            in zip(sorted(nav_pre), sorted(nav_post))
            if fam_pre == fam_post and count_pre != count_post
        ]
        may_publish = True
        if badge_post["state"] != "read":
            print("    REFUSED: the AFTER reading failed. The page WAS opened, "
                  "so whatever it costs has been spent, and this run cannot "
                  "say what that was. No rows are published.")
            may_publish = False
        elif badge_post["pending"] != badge_pre["pending"]:
            print("    REFUSED: the badge MOVED, %r -> %r. No rows are "
                  "published." % (badge_pre["pending"], badge_post["pending"]))
            may_publish = False
        elif badge_pre["pending"] == 0:
            print("    SAFETY   discharged BY ABSENCE. The badge read 0 before "
                  "and 0 after: nothing pending was consumed because nothing "
                  "was pending.")
            print("    COST     UNMEASURED, and it stays that way. A zero "
                  "cannot decrement, so this run says nothing about what this "
                  "address costs on a day something IS pending. Do NOT read "
                  "the line above as 'this page is free'.")
        else:
            print("    SAFETY   discharged BY COMPARISON. %d -> %d against a "
                  "badge that COULD have fallen."
                  % (badge_pre["pending"], badge_post["pending"]))
            print("    COST     MEASURED ZERO on this reading. Record it "
                  "rather than re-deriving it.")
        print("    other nav badges that moved across the load: %d" % len(moved))
        for fam, count_pre, count_post in moved:
            print("        %-16s %r -> %r" % (fam, count_pre, count_post))
            may_publish = False
        if moved:
            print("    REFUSED: a badge this run was not watching for MOVED. "
                  "No rows are published.")

        if not served:
            print("\n5. THE ADDRESS DOES NOT SERVE.")
            print("    An admitted address is not a served one -- the same "
                  "result ``/in/me/details/interests/`` has, and the reason "
                  "that route is not the cheap answer either. Nothing is "
                  "captured and no rows are read.")
            return 0

        if not may_publish:
            print("\n5. ROWS WITHHELD by the obligation above. The page "
                  "served; what is on it is not published by this run.")
            return 1

        # --------------------------------------------------------------
        # 5. THE PAGE, entirely through the shaped census.
        # --------------------------------------------------------------
        print("\n5. THE PAGE, through dom.read_surface_census (SHAPED)")
        census = await dom.read_surface_census(page)
        controls = list(census.get("controls") or [])
        read_count = int(census.get("controls_read") or 0)
        marked = [
            row for row in controls
            if NEWSLETTER_MARKER in str(row.get("href_shape") or "")
        ]
        print("    controls_read=%d   newsletter-marked hrefs=%d"
              % (read_count, len(marked)))

        by_container: dict[str, int] = {}
        by_role: dict[str, int] = {}
        for row in marked:
            container = str(row.get("container") or "none")
            by_container[container] = by_container.get(container, 0) + 1
            role = "%s/%s" % (row.get("tag") or "?", row.get("role") or "none")
            by_role[role] = by_role.get(role, 0) + 1
        print("    CONTAINERS over the %d marked controls (%d distinct):"
              % (len(marked), len(by_container)))
        for container, count in sorted(
            by_container.items(), key=lambda item: (-item[1], item[0])
        ):
            print("        %3d  %s" % (count, container))
        print("    TAG/ROLE:")
        for role, count in sorted(
            by_role.items(), key=lambda item: (-item[1], item[0])
        ):
            print("        %3d  %s" % (count, role))

        # THE UNSUBSCRIBE QUESTION, asked of the shaped names rather than of a
        # guess. A control whose SHAPE carries the word is furniture-shaped and
        # names nobody; a control pointing at a newsletter has its name
        # redacted by the census itself, so this can only ever find the
        # generic ones -- which is exactly the ones the question is about.
        vocabulary = ("subscribe", "unsubscribe", "manage", "following",
                      "subscribed", "create", "write", "draft")
        found: dict[str, int] = {}
        for row in controls:
            text = str(row.get("shape") or "").lower()
            for word in vocabulary:
                if word in text:
                    found[word] = found.get(word, 0) + 1
        print("    CONTROL VOCABULARY over all %d shaped names:" % read_count)
        for word in vocabulary:
            print("        %-12s %d" % (word, found.get(word, 0)))

        # --------------------------------------------------------------
        # 6. THE SHIPPED GATE, against a real page for the first time.
        # --------------------------------------------------------------
        print("\n6. shape.subscription_row OVER EVERY NEWSLETTER-ISH ANCHOR")
        rows = await _subscription_rows(page)
        published = [row for row in rows if row.get("published")]
        refused = [row for row in rows if not row.get("published")]
        print("    anchors seen=%d   published=%d   refused=%d"
              % (len(rows), len(published), len(refused)))
        by_reason: dict[str, int] = {}
        for row in refused:
            reason = str(row.get("refused"))
            by_reason[reason] = by_reason.get(reason, 0) + 1
        for reason, count in sorted(by_reason.items()):
            print("        refused %-42s %d" % (reason, count))
        redacted = sum(1 for row in published if row.get("name_redacted"))
        print("    of the published rows, the redactor changed %d of %d"
              % (redacted, len(published)))
        for index, row in enumerate(published[:12]):
            print("        [%02d] %s" % (index, _row_relation(row)))
        if len(published) > 12:
            print("        ... %d more" % (len(published) - 12))

        # --------------------------------------------------------------
        # 6b. THE READER, against the page it was built from.
        #
        # THE ONLY PLACE IT MEETS THE LIVE DOM. Its suite runs it over a
        # SYNTHETIC fixture in a real headless page -- which exercises the
        # selector, the paragraph choice and the deduplication, and still
        # cannot say that LinkedIn's page is shaped the way the fixture claims.
        # These four numbers are that claim, checked.
        # --------------------------------------------------------------
        print("\n6b. newsletters.read_newsletter_subscriptions ON THE LIVE PAGE")
        reading = await newsletters.read_newsletter_subscriptions(page)
        print("    error=%r  heading_seen=%d  anchors=%d  without_text=%d"
              % (reading["error"], reading["heading_seen"], reading["anchors"],
                 reading["anchors_without_text"]))
        print("    distinct=%d  published=%d  titles_matching_slug=%d  "
              "unmatched=%d"
              % (reading["distinct"], reading["published"],
                 reading["titles_matching_slug"], reading["titles_unmatched"]))
        for index, row in enumerate(reading["rows"]):
            print("        [%02d] matches_slug=%-5r %s"
                  % (index, row.get("title_matches_slug"), _row_relation(row)))
        if reading["titles_unmatched"]:
            print("    THE AIMING CONTROL FIRED. At least one first paragraph "
                  "is not a prefix of its own slug, so the paragraph the "
                  "reader calls a title may not be one. Do not publish these "
                  "titles; re-read the capture.")
        elif reading["distinct"]:
            print("    the aiming control passed on every row: each title is a "
                  "prefix of the slug LinkedIn built from it.")

        # --------------------------------------------------------------
        # 7. THE CAPTURE. Written, never read back here, never printed from.
        # --------------------------------------------------------------
        html = await page.content()
        CAPTURE.write_text(html, encoding="utf-8")
        print("\n7. CAPTURE  %d chars -> %s (gitignored)"
              % (len(html), CAPTURE.name))

        # --------------------------------------------------------------
        # 8. WHAT THIS RUN SETTLES, stated as the four questions it was
        #    launched to answer, so no reader has to infer them.
        # --------------------------------------------------------------
        print("\n8. THE FOUR QUESTIONS")
        print("    (1) does it SERVE          : %s" % relation)
        print("    (2) newsletter-marked hrefs: %d" % len(marked))
        print("    (3) rows the gate PUBLISHES: %d" % len(published))
        print("    (4) unsubscribe vocabulary : %d occurrence(s)"
              % (found.get("unsubscribe", 0) + found.get("subscribed", 0)))
        if not marked and not published:
            print("    ZERO ROWS. That is either 'he subscribes to nothing' or "
                  "'this aim is wrong', and the two are NOT distinguished by "
                  "this run. The capture above is what distinguishes them, and "
                  "reading it is the next step rather than concluding here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
