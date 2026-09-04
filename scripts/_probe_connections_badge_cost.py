"""Does opening his connections list spend his pending-invitation badge?

THE QUESTION HAS BLOCKED A SHIPPED TOOL INDEFINITELY. ``linkedin_connections``
refuses because ``server.CONNECTIONS_BADGE_COST`` is ``None`` -- nobody has
measured whether loading ``/mynetwork/invite-connect/connections/`` consumes
the badge. That is a TECHNICAL unknown and not a permission question, and the
defect is that nobody engineered the measurement. This is the measurement.

## THE ASSUMPTION UNDER TEST, NAMED SO IT CANNOT BE SMUGGLED IN

``/mynetwork/`` is refused on the argument that it consumes the badge. **The
connections list is a DIFFERENT ADDRESS.** Whether the documented cost of the
parent transfers to the sub-page IS THE HYPOTHESIS, so the existing sentence
about ``/mynetwork/`` may not stand in for a reading of this one. Nothing in
this script consults it.

## THE GATE THAT CAN END THE RUN BEFORE ANYTHING IS SPENT

**A BADGE THAT ALREADY READS ZERO CANNOT SHOW A DECREMENT.** If the before
reading is zero, this run could only ever report "unchanged" -- which would be
a result that could not have come out any other way, agreeing with a plausible
story it had no power to refute. That is the uninterpretable zero this
repository has now met four times in one day, and it is worse than no reading
because it looks like one.

So: **if the pending-invitation badge is unreadable OR zero, this STOPS and
loads nothing.** Unmeasurable-today is a real answer. A manufactured
no-change is not.

## WHAT IT READS THAT THE PRESCRIPTION DID NOT ASK FOR, AND WHY

**EVERY nav badge, not just the one under test.** The prescription is a
before/after on the mynetwork badge. Read alone, that reading cannot say what
the run was CAPABLE of detecting -- and "say what you DID see" is the rule this
repo wrote after two wrong diagnoses came out of "zero matched".

Reading all of them costs nothing (same page, same locator family, no extra
navigation) and buys two things:

  * a LIVE CONTROL. A non-zero badge elsewhere on the same nav proves the
    reader is resolving real values on this render rather than returning a
    cached or default zero. On 2026-08-31 ``Home`` read 1 while three others
    read 0, so this is not hypothetical.
  * a SECOND OBSERVABLE. If the mynetwork badge is measurable and the load
    turns out to move a DIFFERENT badge, that is a cost this experiment would
    otherwise have missed entirely while reporting the page free.

## WHAT IT PRINTS

COUNTS, BADGE VALUES AND FAMILY NAMES. No member name, no member id, no slug,
no url carrying either. A badge label's leading word is NOT printed: the audit
redacts it (``_audit/2026-08-31-linkedin-lift.md:174``), so it is not a string
this repository holds, and the family is named off the HREF instead.

Run:  venv/Scripts/python.exe scripts/_probe_connections_badge_cost.py
Presses nothing. Types nothing. Sends nothing. Two navigations at most, both
to module constants.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, server, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import FEED_URL  # noqa: E402
from linkedin_server.auth import assert_not_authwall  # noqa: E402

#: Which nav control a badge belongs to, decided by its HREF rather than by its
#: words. The href is the stable half -- the label's leading word is redacted
#: in this repo's own audit and is therefore unavailable to match on, which is
#: the same reason `dom.invitation_badge_selector` aims the way it does.
_FAMILIES = (
    ("mynetwork", "/mynetwork/"),
    ("messaging", "/messaging/"),
    ("notifications", "/notifications/"),
    ("jobs", "/jobs"),
    ("feed-or-home", "/feed/"),
    # HIS OWN PROFILE, named as a family so its href is never PRINTED. The Me
    # control's href is /in/<his slug>, and an "other" bucket that prints the
    # href to be useful would print exactly that.
    ("self-profile", "/in/"),
    ("interests-groups", "/groups/"),
    ("learning", "/learning"),
)


def _family_of(href: str | None) -> str:
    if href is None:
        return "no-href (button)"
    for name, needle in _FAMILIES:
        if needle in href:
            return name
    return "other"


#: The one string this probe compares a nav label against, and it is the
#: measured tail rather than any word before it.
_TAIL = dom.INVITATION_BADGE_TAIL


def _label_relation(label: str | None) -> str:
    """A nav label reduced to a RELATION. Never the label.

    The Me control's accessible name is HIS NAME, so this probe cannot print
    nav labels -- and the question it needs answered is structural anyway:
    does this control carry a COUNT, and if not, what does it carry instead?
    Words, characters, whether any digit appears, and whether the measured
    tail appears are all answerable without the string.
    """
    text = (label or "").strip()
    if not text:
        return "no aria-label"
    return "words=%d chars=%d has_digit=%s has_tail=%s" % (
        len(text.split()),
        len(text),
        any(ch.isdigit() for ch in text),
        _TAIL in text.lower(),
    )


async def _all_nav_badges(page) -> list[tuple[str, int | None, str]]:
    """(family, count, state) for every nav control carrying a count.

    One locator over the measured tail, then one attribute read per hit. No
    evaluate, no waiver, and the LABEL ITSELF NEVER LEAVES THIS FUNCTION -- only
    the number parsed out of it and the family name taken off the href.
    """
    out: list[tuple[str, int | None, str]] = []
    # ANY TAG, NOT JUST AN ANCHOR. The audit that measured this label records
    # the shape on ``a`` / ``button`` -- so a sweep restricted to anchors is
    # blind to half of what it was told about, and would report a badge drawn
    # on a button as absent.
    badges = page.locator('[aria-label*="%s"]' % dom.INVITATION_BADGE_TAIL)
    count = int(await badges.count())
    for index in range(count):
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


def _show(title: str, rows: list[tuple[str, int | None, str]]) -> None:
    print("  %s -- %d nav control(s) carrying a count" % (title, len(rows)))
    for family, pending, state in sorted(rows):
        print("      %-16s pending=%-5r state=%s" % (family, pending, state))


async def main() -> None:
    print("=" * 72)
    print("CONNECTIONS BADGE COST -- before/after on the address itself")
    print("=" * 72)

    async with BROWSER.session() as page:
        # ------------------------------------------------------------------
        # 1. BEFORE, off a page this server already loads for other reasons.
        # ------------------------------------------------------------------
        landed = await BROWSER.goto(page, FEED_URL)
        assert_not_authwall(landed, surface="feed")
        print("\n1. BEFORE, read off the feed's nav")

        reading = await dom.read_invitation_badge(page)
        before = shape.invitation_badge(reading)
        print("   mynetwork badge: pending=%r state=%r"
              % (before["pending"], before["state"]))
        print("   why: %s" % before["why"])
        print("   saw: mynetwork_links=%r links_carrying_a_count=%r"
              % (reading["links"], reading["badge_links"]))

        before_all = await _all_nav_badges(page)
        _show("all nav badges", before_all)

        # WHAT THE MYNETWORK CONTROL CARRIES INSTEAD, because "it has no
        # count" and "my selector cannot see its count" are different facts
        # and only one of them is a defect in this reader. Reported as a
        # RELATION: that control sits beside one whose label is his name.
        print()
        print("   the network controls, by relation (no label printed):")
        anywhere = page.locator('[href*="/mynetwork"], [aria-label*="etwork"]')
        total = int(await anywhere.count())
        for index in range(min(total, 12)):
            item = anywhere.nth(index)
            href = await item.get_attribute("href")
            label = await item.get_attribute("aria-label")
            # THE HREF IS PRINTED HERE AND THE LABEL IS NOT, and the asymmetry
            # is the whole privacy rule of this probe. A nav destination is
            # FURNITURE -- /mynetwork, /jobs, /feed -- and knowing which
            # spelling LinkedIn uses is the entire question. A nav LABEL is
            # not furniture: the control beside these carries his name. The
            # href still goes through census_substitute, because the Me
            # control's href is /in/<slug> and a sweep that widened by one
            # selector would otherwise print it.
            print("      tag=%-8s %s" % (
                (await item.evaluate("el => el.tagName")).lower(),  # readonly-ok
                _label_relation(label),
            ))
            print("               href=%r" % (shape.census_substitute(href or ""),))
        print("      (%d control(s) matched)" % total)

        # THE CONTROL, stated as a number rather than assumed. A non-zero badge
        # anywhere on this nav proves the reader resolves real values on this
        # render; all-zero means the instrument is unproven on this run and the
        # report has to say so.
        live = [row for row in before_all if (row[1] or 0) > 0]
        print("   instrument control: %d of %d badges read NON-ZERO%s"
              % (len(live), len(before_all),
                 "" if live else "  <-- nothing on this nav could show a drop"))

        # ------------------------------------------------------------------
        # 2. THE GATE. A zero cannot decrement.
        # ------------------------------------------------------------------
        if before["state"] != "read":
            print("\nSTOPPED: the pending-invitation badge is UNREADABLE.")
            print("Nothing was loaded beyond the feed. An unreadable before")
            print("cannot anchor an after, and this refuses rather than")
            print("treating the failure as a zero.")
            await BROWSER.stop()
            return

        if before["pending"] == 0:
            print("\nSTOPPED: UNMEASURABLE TODAY. The badge reads ZERO.")
            print("The connections page was NOT opened, so nothing was spent.")
            print()
            print("WHY THIS IS A RESULT AND NOT A FAILURE. A zero before and a")
            print("zero after cannot distinguish 'the page consumed nothing'")
            print("from 'there was nothing to consume'. Running the load anyway")
            print("would produce an 'unchanged' that could not have come out")
            print("any other way -- a check that cannot fail, arriving inside")
            print("the measurement ruled to settle a cost.")
            print()
            print("WHAT WOULD MAKE IT MEASURABLE: one pending invitation he")
            print("has not yet looked at. That is not arrangeable on demand --")
            print("somebody else has to send it -- so this waits for a day when")
            print("the number above is not zero, and the run costs one feed")
            print("load to find out.")
            await BROWSER.stop()
            return

        # ------------------------------------------------------------------
        # 3. THE LOAD UNDER TEST. Reached only with a non-zero before.
        # ------------------------------------------------------------------
        print("\n2. THE LOAD UNDER TEST -- %s" % server.CONNECTIONS_URL)
        landed = await BROWSER.goto(page, server.CONNECTIONS_URL)
        assert_not_authwall(landed, surface="connections")
        print("   landed on the admitted address: %r"
              % (shape.census_substitute(landed) == server.CONNECTIONS_URL))

        # ------------------------------------------------------------------
        # 4. AFTER, off the connections page's OWN nav. No third navigation.
        # ------------------------------------------------------------------
        print("\n3. AFTER, read off the connections page's own nav")
        reading_after = await dom.read_invitation_badge(page)
        after = shape.invitation_badge(reading_after)
        print("   mynetwork badge: pending=%r state=%r"
              % (after["pending"], after["state"]))
        after_all = await _all_nav_badges(page)
        _show("all nav badges", after_all)

        # ------------------------------------------------------------------
        # 5. THE VERDICT.
        # ------------------------------------------------------------------
        print("\n4. VERDICT")
        if after["state"] != "read":
            print("   INCONCLUSIVE: the after reading failed. The page WAS")
            print("   opened, so whatever it costs has been spent, and this")
            print("   cannot say what that was. Stated rather than hidden.")
        elif after["pending"] == before["pending"]:
            print("   UNCHANGED: %d -> %d. Opening this address consumed no"
                  % (before["pending"], after["pending"]))
            print("   pending invitation, measured against a badge that COULD")
            print("   have fallen. Record in server.CONNECTIONS_BADGE_COST:")
            print("     {\"before\": %d, \"after\": %d, \"measured\": \"<date>\"}"
                  % (before["pending"], after["pending"]))
        elif after["pending"] < before["pending"]:
            print("   CONSUMED: %d -> %d. Opening this address SPENT %d."
                  % (before["pending"], after["pending"],
                     before["pending"] - after["pending"]))
            print("   The documented cost of /mynetwork/ transfers to the")
            print("   sub-page. That is the answer, learned by paying it once.")
        else:
            print("   ROSE: %d -> %d. An invitation arrived mid-read, so this"
                  % (before["pending"], after["pending"]))
            print("   run cannot separate 'consumed nothing' from 'consumed")
            print("   some and more arrived'. Re-run rather than record it.")

        # The other badges, compared as a set, because a cost this experiment
        # was not looking for is still a cost.
        moved = [
            (fam, b, a)
            for (fam, b, _sb), (fam2, a, _sa) in zip(sorted(before_all), sorted(after_all))
            if fam == fam2 and b != a
        ]
        print("\n   other nav badges that moved across the load: %d" % len(moved))
        for fam, b, a in moved:
            print("      %-16s %r -> %r" % (fam, b, a))

        # ------------------------------------------------------------------
        # 6. AND THE READER, since the page is open and reading is free now.
        # ------------------------------------------------------------------
        rows, census = await server._read_connection_rows(page, limit=25)
        print("\n5. THE READER, on the real page (COUNTS ONLY)")
        print("   rows parsed:        %r" % census["rows_parsed"])
        print("   rows unparsed:      %r" % census["rows_unparsed"])
        print("   person anchors:     %r" % census["anchors_keyed"])
        print("   message buttons:    %r" % census["message_buttons"])
        print("   with recipient_id:  %r" % census["with_recipient_id"])
        print("   unattributable ids: %r" % census["ids_unattributable"])
        print("   named off the link: %r" % census["named_by_link"])
        print("   named off the row:  %r" % census["named_by_row"])
        print("   headline present:   %d of %d"
              % (sum(1 for r in rows if r.get("headline")), len(rows)))

    await BROWSER.stop()


if __name__ == "__main__":
    asyncio.run(main())
