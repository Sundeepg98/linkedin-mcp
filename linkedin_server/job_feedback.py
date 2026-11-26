"""The feedback pair under his recommended jobs: address it, read it, aim it -- census row ``J 163``.

*Tell LinkedIn whether its job recommendations are finding what you're looking
for.* Ruled ``J-163-RECEIPT-ONLY-WRITE`` (the orchestrator, 2026-11-25): "a
RECEIPT-ONLY WRITE behind the grant, fired only on his order (no inverse
exists, so the round-trip rule cannot apply); proven by that press". One write
acts through this module, ``send_recommendations_feedback``; ``writes``
delegates to it, as it does to ``search_alert_switch`` for ``J 31``.

## WHAT IS MEASURED

Live session 8's recommended jobs (``/jobs/collections/recommended/``), tracked
as ``tests/fixtures/live8/recommended.html`` and, with LinkedIn's words written
by keyed shape, as ``tests/fixtures/live8/recommended_words.html``
(``scripts/_build_jobs2_word_skeletons.py``): after the job list, ONE
``div[data-view-name="jobs-search-list-feedback"]`` holding an ``h2`` reading
:data:`HEADING`, a paragraph reading :data:`SENTENCE`, and exactly TWO
buttons, each an icon and one text span -- :data:`ANSWERS` ``"no"``, then
``"yes"`` (LinkedIn's curly apostrophe; the straight one matches nothing).

## WHAT IS NOT MEASURED, AND HOW THE WRITE SAYS SO

What a press leaves: no capture shows the block after an answer, and no
control that withdraws one is drawn. So the outcome is DECLARED UNVERIFIABLE
on the spec (``writes.Unverifiable``) -- there is no reader that could return
an "answered" state, and none is pretended -- and the receipt records what the
page draws right after the press, counts and booleans only
(:func:`read_block` again): the record the ruling calls the row's proof.

## THE ADDRESS, AND WHO SUPPLIES IT

A constant, :data:`PAGE_URL`. The ANSWER -- ``yes`` or ``no`` -- is the grant's
target, from his own argument, and the press is chosen by it from the closed
:data:`ANSWERS`; the page may veto (the landing must keep the collection's
path, and the block must draw the pair exactly once each), never supply.

## WHAT NEVER LEAVES

No page text: the readings are counts and booleans, compared here against the
module's own words.
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import coerce

#: The action this module serves, and its tool.
ACTION = "send_recommendations_feedback"
TOOL_NAME = "linkedin_send_recommendations_feedback"

#: His recommended jobs: the read boundary's admitted address, exactly.
PAGE_URL = "https://www.linkedin.com/jobs/collections/recommended/"
PAGE_PATH = "/jobs/collections/recommended"

#: The write door's pattern: that one address and nothing beside it.
URL_PATTERN = re.compile(r"^https://www\.linkedin\.com/jobs/collections/recommended/$")

#: The block, by LinkedIn's own view name.
BLOCK = 'div[data-view-name="jobs-search-list-feedback"]'

#: LinkedIn's words, each MEASURED by keyed shape (session 8). The apostrophe
#: is U+2019, written as an escape so this file stays ASCII.
HEADING = "Are these results helpful?"
SENTENCE = "Your feedback helps us improve job recommendations."
QUESTION = "Are you finding what you’re looking for?"
ANSWERS: dict[str, str] = {
    "no": QUESTION + " No",
    "yes": QUESTION + " Yes",
}

#: The state the preview and the click read: the block drawn once, its
#: heading, its sentence and its two buttons each exactly once.
ASKED = "asked"
#: The state the act would leave. No reader returns it: the spec declares the
#: outcome unverifiable, and this name exists for the spec's ``to_state``.
ANSWERED = "answered"
UNKNOWN = "unknown"

#: The most buttons read inside the block. The capture draws two.
MAX_BUTTONS = 12


def canonical_answer(value: Any) -> tuple[Optional[str], str]:
    """``("yes"|"no", "")``, or ``(None, why)``. PURE; the why never repeats the value."""
    text = str(value if value is not None else "").strip().casefold()
    if text in ANSWERS:
        return text, ""
    return None, (
        f"the answer must be one of {sorted(ANSWERS)}: the two buttons the "
        "block draws. It is not repeated here."
    )


def landed_on_page(landed: Any) -> bool:
    """Did the one load keep the recommended collection's own path? A yes or a no."""
    if not isinstance(landed, str):
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and parts.netloc.lower() == "www.linkedin.com"
        and parts.path.rstrip("/") == PAGE_PATH
    )


def _collapsed(text: Any) -> str:
    return " ".join(text.split()) if isinstance(text, str) else ""


async def _text(locator: Any) -> str:
    try:
        return _collapsed(await locator.text_content(timeout=2000))
    except Exception:  # noqa: BLE001 -- a part that cannot be read is not counted
        return ""


async def read_block(page: Any) -> dict[str, Any]:
    """The feedback block as the page draws it now, in counts. READ ONLY.

    Never raises: a failure is its exception's TYPE NAME. The block is found by
    its view name; inside it the heading by the ``h2``'s words, the sentence by
    a paragraph's, and each button by its own words -- by structure, never by
    position.
    """
    out: dict[str, Any] = {
        "blocks": 0,
        "heading": 0,
        "sentence": 0,
        "buttons": 0,
        "answers": {answer: 0 for answer in ANSWERS},
        "error": None,
    }
    try:
        blocks = page.locator(BLOCK)
        out["blocks"] = coerce.as_count(await blocks.count())
        if out["blocks"] != 1:
            return out
        block = blocks.nth(0)
        headings = block.locator("h2")
        for index in range(min(coerce.as_count(await headings.count()), 5)):
            if await _text(headings.nth(index)) == HEADING:
                out["heading"] += 1
        paragraphs = block.locator("p")
        for index in range(min(coerce.as_count(await paragraphs.count()), 5)):
            if await _text(paragraphs.nth(index)) == SENTENCE:
                out["sentence"] += 1
        buttons = block.locator("button")
        out["buttons"] = coerce.as_count(await buttons.count())
        for index in range(min(out["buttons"], MAX_BUTTONS)):
            words = await _text(buttons.nth(index))
            for answer, expected in ANSWERS.items():
                if words == expected:
                    out["answers"][answer] += 1
    except Exception as exc:  # noqa: BLE001 -- the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def state_of(reading: dict[str, Any]) -> tuple[str, str]:
    """``(state, why)`` off a :func:`read_block` reading. PURE."""
    if reading.get("error"):
        return UNKNOWN, f"the recommended jobs could not be read ({reading['error']})."
    blocks = coerce.as_count(reading.get("blocks"))
    if blocks != 1:
        return UNKNOWN, (
            f"{blocks} feedback block(s) are drawn, where exactly one is required."
        )
    answers = reading.get("answers") or {}
    counts = {answer: coerce.as_count(answers.get(answer)) for answer in ANSWERS}
    if (
        coerce.as_count(reading.get("heading")) != 1
        or coerce.as_count(reading.get("sentence")) != 1
        or coerce.as_count(reading.get("buttons")) != 2
        or any(n != 1 for n in counts.values())
    ):
        return UNKNOWN, (
            "the block does not draw what its capture drew -- its heading and its "
            "sentence once each, and exactly two buttons, one per answer, each "
            f"once (read: {coerce.as_count(reading.get('heading'))} heading(s), "
            f"{coerce.as_count(reading.get('sentence'))} sentence(s), "
            f"{coerce.as_count(reading.get('buttons'))} button(s), answers {counts})."
        )
    return ASKED, (
        "one feedback block, its heading and its sentence, and its two buttons "
        "once each: the question is drawn and unanswered on this render."
    )


def press_selector(answer: str) -> str:
    """The one button the press is aimed at: the answer's own words, inside the
    one block. Strict at the press, so a second match throws."""
    words = ANSWERS[answer]
    return f'{BLOCK} >> role=button[name="{words}"s]'


def after_press(reading: dict[str, Any]) -> dict[str, Any]:
    """What the receipt records of the page right after the press: the same
    counts, and whether the question is still drawn as it was. PURE."""
    answers = reading.get("answers") or {}
    return {
        "blocks": coerce.as_count(reading.get("blocks")),
        "heading": coerce.as_count(reading.get("heading")),
        "sentence": coerce.as_count(reading.get("sentence")),
        "buttons": coerce.as_count(reading.get("buttons")),
        "answers": {answer: coerce.as_count(answers.get(answer)) for answer in ANSWERS},
        "question_still_drawn": state_of(reading)[0] == ASKED,
        "error": reading.get("error"),
    }
