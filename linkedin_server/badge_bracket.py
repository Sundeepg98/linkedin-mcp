"""The pending-invitation badge, read before and after a ``/mynetwork/`` list loads -- and what the two readings decide.

WHY. ``readonly.py`` admits three ``/mynetwork/`` lists for lane A's rows --
the invitation manager's received tab (``N 13``) and sent tab (``N 9``), and
the people he follows (``N 38``) -- with one condition written beside them:
"the pending-invitation badge a load may clear is a passive cost
(D5-PASSIVE-COST-IS-NOT-A-ROW), bracketed by the reader as
``linkedin_connections`` brackets it". This module is that bracket's verdict.
It is PURE: the tool reads the badge (``dom.read_invitation_badge``, then
``shape.invitation_badge``) on ``/feed/`` before the list loads and on the
list's own navigation after, and hands the two readings here.

MEASURED on session 11's captures: the network control on every one of these
pages, and on the feed, carries LinkedIn's label ``Network, 0 new
notifications`` (by keyed shape), which the shipped badge parser reads as a
count -- so the AFTER reading is taken on the list itself and costs no third
load, as ``linkedin_connections`` takes it.

THE THREE OUTCOMES, by what the list's own page can cost:

* BEFORE UNREADABLE: refused, and the list is never loaded.
* THE SENT TAB AND THE FOLLOWING LIST: an unreadable AFTER, or a badge that
  MOVED, WITHHOLDS the list -- exactly ``linkedin_connections``' rule. Neither
  page shows the invitations the badge counts, so a move is not their cost and
  a tool cannot certify what it read.
* THE RECEIVED TAB: the page IS the invitations the badge counts, and
  RECEIVED-INVITATIONS-READ-STAYS-ADMITTED keeps the read admitted with
  whatever it changes in an invitation's seen state as a passive cost,
  recorded and unmeasured. So a badge that fell is THAT cost, MEASURED, and
  returned beside the list; it never withholds it. RULED by the orchestrator,
  2026-11-26, RECEIVED-BADGE-IS-THE-READ'S-COST: reading the received tab
  inherently clears the pending badge, on the ``linkedin_notifications``
  precedent; the sent tab and the following list keep withholding.

``cost.proven`` says which case a held badge is: a non-zero badge that held
is a measurement; a zero that held proves nothing about the page and cost
nothing either, the argument ``linkedin_connections`` gives in full.

WHAT LEAVES: integers, booleans and closed words. The badge's label -- which
the badge reader's own docstring says to read as name-bearing -- does not.
"""
from __future__ import annotations

from typing import Any, Optional

#: The surfaces a bracket judges, and whether a moved badge withholds the list.
WITHHOLDS_ON_MOVE: dict[str, bool] = {
    "received_invitations": False,
    "sent_invitations": True,
    "own_following_list": True,
}

#: What the bracket says, closed.
OUTCOMES = (
    "before_unreadable",
    "after_unreadable",
    "moved",
    "held",
)


def badge(reading: Optional[dict[str, Any]]) -> dict[str, Any]:
    """A ``shape.invitation_badge`` reading reduced to what may leave:
    ``{"state": "read" | "unreadable", "pending": int | None}``. PURE."""
    reading = reading or {}
    if reading.get("state") == "read" and isinstance(reading.get("pending"), int):
        return {"state": "read", "pending": int(reading["pending"])}
    return {"state": "unreadable", "pending": None}


def before_unreadable(first_reading: Optional[dict[str, Any]]) -> dict[str, Any]:
    """The refusal when the badge could not be read BEFORE: nothing loaded."""
    return {
        "refused": "badge_unreadable_before",
        "badge_before": badge(first_reading),
        "badge_after": None,
        "cost": {"outcome": "before_unreadable", "proven": False},
        "pages_loaded": 1,
        "why": (
            "the pending-invitation badge could not be read on the feed before "
            "the list, so the list was not opened: a /mynetwork/ load is made "
            "only between two readings of that badge. Nothing was spent."
        ),
    }


def judge(
    surface: str,
    reading: dict[str, Any],
    first_reading: Optional[dict[str, Any]],
    second_reading: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """The list's reading with the bracket beside it -- or withheld. PURE.

    ``reading`` is the list reader's answer; ``first_reading`` and
    ``second_reading`` are the two ``shape.invitation_badge`` readings, off the
    feed before the load and off the list's own nav after it. (Not named
    ``before`` and ``after``: those are paging words, and no function a people
    tool names takes one -- ``tests/test_a_people_reader_reads_one_page.py``.)
    Raises ``KeyError`` for a surface this module does not judge.
    """
    withholds = WITHHOLDS_ON_MOVE[surface]
    b, a = badge(first_reading), badge(second_reading)
    out = dict(reading)
    out["badge_before"] = b
    out["badge_after"] = a
    out["pages_loaded"] = 2
    if a["state"] != "read":
        out["cost"] = {"outcome": "after_unreadable", "proven": False}
    elif a["pending"] != b["pending"]:
        out["cost"] = {
            "outcome": "moved",
            "proven": True,
            "before": b["pending"],
            "after": a["pending"],
        }
    else:
        out["cost"] = {"outcome": "held", "proven": b["pending"] > 0}
    if withholds and out["cost"]["outcome"] in ("after_unreadable", "moved"):
        return _withheld(surface, reading, out)
    return out


def _withheld(surface: str, reading: dict[str, Any], judged: dict[str, Any]) -> dict[str, Any]:
    """The reading with every record and count withheld, the bracket kept."""
    kept = {
        key: judged[key]
        for key in ("surface", "badge_before", "badge_after", "cost", "pages_loaded", "scope")
        if key in judged
    }
    kept["refused"] = (
        "badge_unreadable_after" if judged["cost"]["outcome"] == "after_unreadable" else "badge_moved"
    )
    kept["readable"] = False
    kept["why"] = (
        "the list was opened, so whatever it cost is spent -- stated, not "
        "hidden; what was read is WITHHELD, because only an unchanged badge "
        "read at both ends certifies that this load consumed nothing, the "
        "rule linkedin_connections holds."
    )
    return kept
