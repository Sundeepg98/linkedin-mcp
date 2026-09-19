"""Whether the notifications page's cost can be measured TODAY, and by whom.

WHAT THIS MODULE IS FOR, stated as the blocker it retires.

``linkedin_notifications`` carries a measured side effect in its own
docstring: loading the notifications page CLEARS the unread badge, measured
2026-08-21 as a badge going from 1 to 0 and not coming back. The blocker
``NOTIFY-COST-UNMEASURED`` sits on that same surface and says the cost is
unmeasured. Both statements are true, and the reason they are both true is
the thing this module exists to make legible:

    THE 2026-08-21 READING WAS TAKEN BY HAND. This package holds a reader for
    the messaging badge and a reader for the invitation badge, and NONE for
    the notifications badge. So the server can state the cost and cannot
    RE-TAKE it -- on any day, by any caller, for any reason.

THE SECOND HALF, AND IT IS THE ONE THAT MAKES A ZERO DANGEROUS. This
repository already wrote the argument down, for the sibling badge, at
``shape.invitation_badge``:

    "the reason the cost it guards has never been measured is that a badge
    sitting at zero cannot distinguish 'the page consumed nothing' from
    'there was nothing to consume'."

That is the same trap one surface over. A before/after pair reading ``0 -> 0``
is not evidence that opening the page is free; it is evidence that nothing was
available to spend. A wave that ran the pair on a quiet account and reported
"no cost observed" would be publishing a fact about the DAY as a fact about
the PLATFORM -- which is the existence-question error this project has now
made in three separate places.

SO THE UNIT OF WORK HERE IS NOT A MEASUREMENT. IT IS A PRECONDITION.
:func:`measurability` answers one question -- *is today a day on which this
cost could be measured at all* -- and it answers it from a reading that costs
ZERO page loads, because the nav renders on every signed-in page. That is the
same property ``dom.read_messaging_badge`` and ``dom.read_invitation_badge``
already rely on and it is measured, not assumed: the invitation badge was read
on ``/feed/`` and on ``/in/me/`` alike.

WHY A NEW MODULE RATHER THAN A THIRD FUNCTION IN ``dom.py``. Cohesion argues
for putting it beside its two siblings and was overruled by contention: this
was written while ten other waves held the tree, and ``dom.py`` and
``server.py`` were the two files being written all afternoon. A reader who
later wants the three badge readers in one place should move this one INTO
``dom.py`` -- the split is a concurrency artefact and is recorded as one
rather than defended as a design.

WHAT THIS MODULE DOES NOT DO, and the omission is deliberate. It does not open
the notifications page, and it contains no code that could. Taking the AFTER
reading spends the operator's unread state, and this wave was briefed to
design and gate rather than to fire. The pair is therefore CONSTRUCTIBLE here
and TAKEN elsewhere, by whoever is legitimately calling
``linkedin_notifications`` anyway -- at which point the cost is recorded in
band, for free, on a call that was going to happen regardless.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from . import shape

#: The notifications nav control, aimed the way ``dom.read_invitation_badge``
#: aims and NOT the way ``dom.read_messaging_badge`` does.
#:
#: The difference between those two shipped readers is a decision, recorded in
#: ``dom.py``: the messaging reader takes ``.first`` of its href match, the
#: invitation reader refuses unless exactly one control carries a count,
#: because a page may draw several links to the same surface and ``.first``
#: would be a choice by POSITION between controls that are not
#: interchangeable.
#:
#: This follows the invitation reader. The notifications surface is linked
#: from the nav AND, on some pages, from in-page controls -- so the count is
#: the thing that identifies WHICH control is the badge, and requiring exactly
#: one is what stops this reader answering confidently about the wrong
#: element.
NOTIFICATIONS_BADGE_HREF = "/notifications"

#: The tail that makes a control a badge. Deliberately the SAME shape the
#: invitation badge is aimed with, and for the same reason: the label's
#: LEADING word is not available to aim with -- this repository's own audit
#: redacts it -- so the aim is the conjunction of the href and the count tail,
#: and the leading word is never matched, never stored and never needed.
BADGE_TAIL = re.compile(r",\s*([\d,]+)\s+new notification", re.I)


def notifications_badge_selector() -> str:
    """The conjunction of the two halves of the aim, as one selector."""
    return (
        'a[href*="'
        + NOTIFICATIONS_BADGE_HREF
        + '"][aria-label*="new notification" i]'
    )


async def read_notifications_badge(page: Any) -> dict[str, Any]:
    """The notifications nav badge, read WITHOUT opening notifications.

    COSTS NO PAGE LOAD. It reads the nav of a page that is already open, which
    is the whole point: the surface whose cost is in question is never
    touched, so taking the BEFORE reading cannot itself spend the thing being
    measured.

    DEFAULTS THAT REFUSE. Every early return leaves ``label`` at ``None``, so
    a reader that could not run never looks like a badge sitting at zero.
    That distinction is the entire content of this module and it has to be
    built into the failure mode, not asserted about it afterwards.

    THE REFUSAL REPORTS WHAT IT SAW, never only what it failed to match --
    this package has been told twice that a bare "zero matched" says nothing.
    So ``links`` (every notifications link on the page) travels beside
    ``badge_links`` (those that also carry the count tail), and a reader of
    the refusal can tell "the nav did not hydrate" from "the label changed
    shape" without opening a browser.

    THE LABEL IS SHAPED ON THE WAY OUT, before this function returns and
    before anything parses it, the same ordering ``dom.read_invitation_badge``
    uses. It is a nav label today and nothing guarantees it stays one.
    """
    out: dict[str, Any] = {
        "links": None,
        "badge_links": None,
        "label": None,
        "error": None,
    }
    try:
        out["links"] = int(
            await page.locator(
                'a[href*="' + NOTIFICATIONS_BADGE_HREF + '"]'
            ).count()
        )
        badges = page.locator(notifications_badge_selector())
        out["badge_links"] = int(await badges.count())
    except Exception as exc:  # noqa: BLE001 - reported, never raised
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out
    if out["badge_links"] != 1:
        return out
    try:
        label = await badges.first.get_attribute("aria-label")
    except Exception as exc:  # noqa: BLE001 - reported, never raised
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out
    out["label"] = shape.census_shape(str(label or "").strip()) or None
    return out


def notifications_badge(reading: Optional[dict[str, Any]]) -> dict[str, Any]:
    """How many unread notifications the nav badge says are waiting.

    Takes the WHOLE reading rather than a bare label, for the reason
    ``shape.invitation_badge`` gives: the interesting failures are not in the
    label. "The nav drew no notifications link at all" and "it drew three and
    only one should carry a count" are different repairs, and a function
    handed just the string could not tell them apart.

    ZERO IS A REAL ANSWER AND IS NOT THE SAME AS UNREADABLE. Here that
    contract is load-bearing in a way it is not for its siblings: a zero read
    from this badge is exactly the reading that makes the cost UNMEASURABLE
    today, and a zero mistaken for an unreadable -- or the reverse -- inverts
    the answer :func:`measurability` gives.
    """
    seen = dict(reading or {})
    links = seen.get("links")
    badge_links = seen.get("badge_links")
    label = seen.get("label")
    error = seen.get("error")

    def _unreadable(why: str) -> dict[str, Any]:
        return {
            "unread": None,
            "state": "unreadable",
            "why": why,
            "saw": {
                "notifications_links": links,
                "links_carrying_a_count": badge_links,
                "shaped_label": label,
                "error": error,
            },
        }

    if error:
        return _unreadable(
            "the badge could not be read from the page at all: %s" % error
        )
    if not badge_links:
        return _unreadable(
            "no notifications nav control carried the measured badge tail "
            "%r. That is NOT zero unread notifications: the nav may not have "
            "hydrated, or LinkedIn may have restyled the label."
            % BADGE_TAIL.pattern
        )
    if badge_links != 1:
        return _unreadable(
            "%d notifications controls carry a count, and this reader will "
            "not choose between them by position. One of them is the nav "
            "badge and the others are something nobody here has seen."
            % int(badge_links)
        )
    match = BADGE_TAIL.search(str(label or ""))
    if not match:
        return _unreadable(
            "the control resolved and its shaped label does not carry a "
            "count. The aim matched on the raw attribute and the parse runs "
            "on the shaped one, so a label the census shaper made opaque "
            "lands here."
        )
    raw = match.group(1).replace(",", "")
    try:
        count = int(raw)
    except ValueError:  # pragma: no cover - defensive
        return _unreadable("the badge read %r, which is not a number." % raw)
    return {
        "unread": count,
        "state": "read",
        "why": (
            "LinkedIn's own notifications nav badge reads %d new. Read off "
            "the nav of a page that was already open, which opens the "
            "notifications surface not at all." % count
        ),
        "saw": {
            "notifications_links": links,
            "links_carrying_a_count": badge_links,
            "shaped_label": label,
            "error": None,
        },
    }


def measurability(before: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Is TODAY a day on which the notifications cost could be measured?

    THIS IS THE FUNCTION THE BLOCKER WAS ACTUALLY WAITING ON. Not a
    measurement -- a precondition, answerable for free, that says whether
    spending the AFTER reading would produce evidence or produce nothing.

    THE THREE ANSWERS, and the middle one is the whole point:

    * ``unreadable`` -- the badge could not be read, so nothing can be said in
      either direction. The BEFORE half of a before/after pair is missing and
      a pair with a missing half is not a pair.
    * ``not_today`` -- the badge reads ZERO. The cost cannot be measured on
      this account today, and this is NOT a finding about LinkedIn. A
      ``0 -> 0`` pair cannot distinguish "the page consumed nothing" from
      "there was nothing to consume", so running it would produce a reading
      that looks like evidence of no cost and is evidence of nothing at all.
      It is reversible: it becomes measurable the moment one notification
      arrives.
    * ``measurable`` -- the badge reads above zero. A before/after pair taken
      around a legitimate ``linkedin_notifications`` call would carry a real
      answer, because there is something available to be consumed and the
      count says how much.

    WHAT IT DELIBERATELY WILL NOT DO. It does not recommend taking the
    reading, and it does not open anything. Whether to spend the operator's
    unread state is his call and not this module's, and a precondition that
    quietly became an instruction would be the thing this project keeps
    catching: a conclusion travelling without the artifact that produced it.
    """
    parsed = notifications_badge(before)
    unread = parsed.get("unread")
    if parsed.get("state") != "read":
        return {
            "state": "unreadable",
            "measurable": None,
            "unread_before": None,
            "why": (
                "the BEFORE half could not be read, so no before/after pair "
                "is constructible: " + str(parsed.get("why"))
            ),
            "reversible": None,
            "reading": parsed,
        }
    if unread == 0:
        return {
            "state": "not_today",
            "measurable": False,
            "unread_before": 0,
            "why": (
                "the badge reads zero, so a before/after pair around the "
                "notifications page would read 0 -> 0 and could not "
                "distinguish 'the page consumed nothing' from 'there was "
                "nothing to consume'. This is a fact about THIS ACCOUNT "
                "TODAY and not about the platform: it says nothing about "
                "whether opening the page costs anything, only that today "
                "cannot answer it."
            ),
            # THE FIELD THAT STOPS THIS BEING READ AS A PERMANENT REFUSAL.
            # A zero here is reversible by one arriving notification, and a
            # caller that cannot see that distinction will file the row as
            # closed.
            "reversible": True,
            "reading": parsed,
        }
    return {
        "state": "measurable",
        "measurable": True,
        "unread_before": unread,
        "why": (
            "the badge reads %d, so there is something available to be "
            "consumed and a before/after pair around a legitimate "
            "notifications call would carry a real answer. Taking it spends "
            "that unread state, which is the operator's to spend." % unread
        ),
        "reversible": None,
        "reading": parsed,
    }


def cost_delta(
    before: Optional[dict[str, Any]], after: Optional[dict[str, Any]]
) -> dict[str, Any]:
    """What the notifications page actually cost, from a pair of readings.

    REFUSES ON THREE SEPARATE GROUNDS and reports which one fired, because
    they want different repairs: an unreadable BEFORE (retake it), an
    unreadable AFTER (the pair is broken and the cost was still paid), and a
    BEFORE of zero (the pair is intact and says nothing).

    THE ZERO REFUSAL IS THE ONE THAT MATTERS AND IT FIRES ON A PAIR THAT LOOKS
    PERFECTLY GOOD. Both halves readable, both zero, no error anywhere -- and
    the honest answer is still "this measured nothing". A function that
    returned ``delta: 0`` there would be handing back a number that reads as
    "no cost" and means "no experiment".
    """
    b = notifications_badge(before)
    a = notifications_badge(after)
    if b.get("state") != "read":
        return {
            "state": "refused",
            "refused_on": "before_unreadable",
            "delta": None,
            "why": "the BEFORE reading is unreadable: " + str(b.get("why")),
            "before": b,
            "after": a,
        }
    if a.get("state") != "read":
        return {
            "state": "refused",
            "refused_on": "after_unreadable",
            "delta": None,
            "why": (
                "the AFTER reading is unreadable, so the cost was paid and "
                "not recorded: " + str(a.get("why"))
            ),
            "before": b,
            "after": a,
        }
    if b.get("unread") == 0:
        return {
            "state": "refused",
            "refused_on": "nothing_to_consume",
            "delta": None,
            "why": (
                "both halves read cleanly and the BEFORE was zero, so this "
                "pair cannot say whether the page consumed anything. A delta "
                "of zero over a before of zero is not a measurement of no "
                "cost; it is the absence of an experiment."
            ),
            "before": b,
            "after": a,
        }
    return {
        "state": "measured",
        "refused_on": None,
        "delta": int(b["unread"]) - int(a["unread"]),
        "why": (
            "the badge moved from %d to %d across the call."
            % (int(b["unread"]), int(a["unread"]))
        ),
        "before": b,
        "after": a,
    }
