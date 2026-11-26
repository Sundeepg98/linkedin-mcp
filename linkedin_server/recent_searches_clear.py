"""Clearing his recent job searches on the jobs home -- census row ``J 19``. BUILT TO REFUSE.

Ruled ``J-19-BUILT-BEHIND-THE-GRANT`` (the orchestrator, 2026-11-25): "BUILD
behind the grant, REFUSING until its confirm dialog is captured; it fires only
on his order". ``writes`` holds the spec (``set_recent_job_searches_cleared``,
sanctioned and NOT performable) and its preview read; ``server`` holds the
tool (``linkedin_set_recent_job_searches_cleared``). Nothing here opens a page or
presses anything.

## WHAT IS MEASURED

On the live lane's session-2 capture of the jobs home (``/jobs/jam/``, the
address ``job_home.HOME_URL`` reads ``J 18`` from), tracked as
``tests/fixtures/live2/j18.html`` and, with LinkedIn's words written by keyed
shape, as ``tests/fixtures/live2/j18_words.html``
(``scripts/_build_jobs2_word_skeletons.py``): inside ``main``, ONE ``section``
whose ``h2`` reads :data:`HEADING`; in that section ONE ``button`` whose own
text span reads :data:`CLEAR_WORD` (its ``aria-label`` matched no candidate
and is never read), and ONE ``ul`` whose ``aria-label`` is the heading again,
holding his searches as ``li`` items (six on the capture).

## WHAT IS NOT MEASURED, AND IT IS THE WHOLE REASON THE ACTION REFUSES

What the press opens: a confirmation dialog, or nothing -- and so what
confirms the clear, and under what name. A press at a control whose outcome
nobody has photographed is the one guess this server does not make, and the
act has no inverse: a cleared history is restored by no control drawn. The
refusal names the capture that lifts it: the press, made once AT HIS ORDER,
with whatever it opens read and closed, nothing confirmed.

## WHAT LEAVES

Counts and one boolean. No search's words: those are the recent-searches
read's to return (census ``J 18``), on its own reading of the same page.
"""
from __future__ import annotations

from typing import Any

from linkedin_server import coerce, job_home

#: The jobs home, the one page this action would act on: ``J 18``'s address.
HOME_URL = job_home.HOME_URL

#: The card's heading, MEASURED by keyed shape (session 2) as the ``h2`` and as
#: its list's ``aria-label`` -- the same words ``job_home`` checks its list by.
HEADING = job_home.RECENT_LIST_LABEL

#: The button's own words, MEASURED by keyed shape (session 2).
CLEAR_WORD = "Clear"

#: The state the preview reads: the card, its one Clear button, and at least
#: one search listed. Anything else is ``unknown`` -- an empty card has never
#: been captured, so "nothing to clear" is not a reading this server can take.
SEARCHES_LISTED = "searches_listed"
UNKNOWN = "unknown"

#: The most sections, buttons and list items looked at. A cost ceiling, not a
#: measured LinkedIn limit; the capture draws far fewer.
MAX_PARTS = 60

_SECTIONS = "main section"


def _collapsed(text: Any) -> str:
    return " ".join(text.split()) if isinstance(text, str) else ""


async def _text(locator: Any) -> str:
    try:
        return _collapsed(await locator.text_content(timeout=2000))
    except Exception:  # noqa: BLE001 -- a part that cannot be read is not counted
        return ""


async def read_clear_control(page: Any) -> dict[str, Any]:
    """What the jobs home draws around the Clear control, in counts.

    READ ONLY, and never raises: a failure is its exception's TYPE NAME. The
    card is found by its heading's words, the button by its own text span,
    the list by its ``aria-label`` -- each by structure inside the card, none
    by position.
    """
    out: dict[str, Any] = {
        "cards": 0,
        "clear_buttons": 0,
        "lists": 0,
        "searches_listed": 0,
        "confirm_dialog_read": False,
        "error": None,
    }
    try:
        sections = page.locator(_SECTIONS)
        total = min(coerce.as_count(await sections.count()), MAX_PARTS)
        cards = []
        for index in range(total):
            section = sections.nth(index)
            headings = section.locator("h2")
            texts = [await _text(headings.nth(i))
                     for i in range(min(coerce.as_count(await headings.count()), 5))]
            if texts.count(HEADING) == 1:
                cards.append(section)
        out["cards"] = len(cards)
        if len(cards) != 1:
            return out
        card = cards[0]
        buttons = card.locator("button")
        for index in range(min(coerce.as_count(await buttons.count()), MAX_PARTS)):
            words = await _text(buttons.nth(index).locator("span.artdeco-button__text"))
            if words == CLEAR_WORD:
                out["clear_buttons"] += 1
        lists = card.locator(f'ul[aria-label="{HEADING}"]')
        out["lists"] = coerce.as_count(await lists.count())
        if out["lists"] == 1:
            out["searches_listed"] = min(
                coerce.as_count(await lists.locator("li").count()), MAX_PARTS)
    except Exception as exc:  # noqa: BLE001 -- the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def state_of(reading: dict[str, Any]) -> tuple[str, str]:
    """``(state, why)`` off a :func:`read_clear_control` reading. PURE."""
    if reading.get("error"):
        return UNKNOWN, f"the jobs home could not be read ({reading['error']})."
    cards = coerce.as_count(reading.get("cards"))
    buttons = coerce.as_count(reading.get("clear_buttons"))
    listed = coerce.as_count(reading.get("searches_listed"))
    if cards != 1:
        return UNKNOWN, (
            f"{cards} card(s) on the jobs home are headed {HEADING!r}, where "
            "exactly one is required."
        )
    if buttons != 1:
        return UNKNOWN, (
            f"the {HEADING!r} card draws {buttons} button(s) reading "
            f"{CLEAR_WORD!r}, where exactly one is required."
        )
    if listed < 1:
        return UNKNOWN, (
            "the card lists no search: an empty card has never been captured, "
            "so this is not read as nothing to clear."
        )
    return SEARCHES_LISTED, (
        f"one {HEADING!r} card, its one {CLEAR_WORD!r} button, and {listed} "
        "search(es) listed under it."
    )
