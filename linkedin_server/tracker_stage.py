"""Moving one tracked job to another stage -- census row ``J 54``. PURE.

THE ACTION IS BUILT TO REFUSE, and this module holds its closed vocabulary.
``writes`` holds the spec (``set_tracker_stage``, sanctioned and NOT
performable) and its preview read; ``server`` holds the tool
(``linkedin_set_tracker_stage``). Nothing here opens a page or presses
anything.

## WHAT IS MEASURED, AND WHAT IS NOT

MEASURED on the one populated tracker capture the repository holds,
``tests/fixtures/jobs_tracker_row.html`` (one row, its tab strip, its two
row copies): the tab strip draws five stages, by these words --
``Saved``, ``Draft``, ``Applied``, ``Interview``, ``Archived``
(:data:`TRACKER_TAB_WORDS`). Each row copy draws one control named
``Overflow menu``, ``aria-expanded="false"``, followed by an EMPTY slot:
the menu's items are not in the document while it is closed.

NOT MEASURED, and it is the whole reason the action refuses: what that menu
holds when it is open -- whether it offers a move to another stage at all,
under what name, and what pressing it does. No capture of an OPENED row menu
exists (census ``J 54``'s own note: the stage change is a row-level control
behind an overflow menu, and needs a capture the repository has never had).
A press at a control nobody has photographed is the one guess this server
does not make.

## THE DESTINATION IS VALIDATED BEFORE ANY PAGE LOADS

A destination outside :data:`TRACKER_STAGES` is refused by the tool before
the browser is touched, and the refusal reports a SHAPE, never the word it
was given. The vocabulary is the tab strip's own words, lower-cased; whether
a row's menu offers a move to each of them is unmeasured and the preview
says so.
"""
from __future__ import annotations

from typing import Any, Optional

#: The stage words the tracker's tab strip draws, as captured.
TRACKER_TAB_WORDS: tuple[str, ...] = ("Saved", "Draft", "Applied", "Interview", "Archived")

#: The closed set a destination is checked against: the tab words, folded.
TRACKER_STAGES: tuple[str, ...] = tuple(word.casefold() for word in TRACKER_TAB_WORDS)

#: The stage this action starts FROM. The brief and the spec agree: the act
#: is the stage control on a SAVED job, and the preview reads the Saved tab.
FROM_STAGE: str = "saved"

#: The longest destination word worth comparing. Anything longer is refused
#: by length alone, so an arbitrary string never reaches a comparison.
MAX_STAGE_CHARS: int = 32


def checked_stage(candidate: Any) -> tuple[Optional[str], str]:
    """``(stage, "")`` for a destination in the closed set, else
    ``(None, why)``. PURE, and the why never repeats the candidate.

    The destination may not be the stage the act starts from: moving a saved
    job to Saved changes nothing, and a preview of a no-op is a gate that
    describes nothing.
    """
    text = str(candidate if candidate is not None else "")
    if len(text) > MAX_STAGE_CHARS:
        return None, (
            f"the destination stage is {len(text)} characters long; the "
            f"tracker's stage words are at most {MAX_STAGE_CHARS}. It is not "
            "repeated here."
        )
    word = text.strip().casefold()
    if word == FROM_STAGE:
        return None, (
            "the destination is the stage this act starts from (Saved), so "
            "there is nothing to move."
        )
    if word in TRACKER_STAGES:
        return word, ""
    return None, (
        "the destination is not one of the stages the tracker's tab strip "
        f"draws ({[w for w in TRACKER_STAGES if w != FROM_STAGE]}, measured on "
        "the one populated tracker capture). It is not repeated here."
    )
