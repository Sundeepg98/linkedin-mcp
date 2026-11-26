"""His own resumes-and-application-data page, read: the two switches and the resume list.

Census rows ``P M2`` (*Saved resumes list (4 most recent)*) and, by their
reading, the state the switch rows ``J 74`` / ``P M8`` and ``J 76`` / ``P M7``
would change. Lane readers-jobs26, 2026-11-26, over the live lane's session-11
capture of ``/jobs/application-settings/`` (load 11), tracked as
``tests/fixtures/live11/application_settings.html`` and, with LinkedIn's words
measured by keyed shape, as ``application_settings_words.html``
(``scripts/_build_live11_word_skeletons.py``).

## WHAT WAS MEASURED (session 11)

The page's main region (``role="main"``) draws one ``h1`` reading ``Resumes
and application data``, and two sections, each an ``h2`` and one switch:

* ``Save resumes and application data`` -- its switch an
  ``input[role=switch][type=checkbox]`` labelled ``Allow LinkedIn to save your
  resumes and answers``, beside LinkedIn's sentence that answers may change
  "with each application";
* ``Share resume data with hirers`` -- its switch labelled ``Allow recruiters
  to view your resumes``.

Both read ``aria-checked="true"`` on the capture. Under the second section,
FOUR resume cards: each an ``h3`` holding the file's NAME (his data), a
paragraph reading ``Last used on <M/D/YYYY>`` or ``Uploaded on <M/D/YYYY>``,
and an options button whose label is ``Show options for <the file's name>``
-- its menu EMPTY while closed. Then a ``label[role=button]`` reading ``Upload
resume`` bound by ``for`` to one ``input[type=file]``, and the rule ``DOC,
DOCX, PDF (5MB)``. No Save button: the page stores each switch on its own.

## WHAT LEAVES, AND WHAT NEVER DOES

* Each switch: its KEY (this module's), and ``on``, ``off`` or ``unknown``,
  read off the input its own label names (``for``), never by position.
* Each resume: its file TYPE (``pdf``, ``docx`` or ``doc``, the name's own
  suffix, compared in this process), WHICH date the card shows (``last_used``
  or ``uploaded``) and that date as an ISO date. THE FILE'S NAME NEVER
  LEAVES: it is his, but no declared channel carries his own document names
  (``people_data`` records are other members' words, and the tool-envelope
  inventory of page text may not grow), so the name is read only to take its
  suffix. The options button's label, which repeats the name, is never read.
* The upload control: whether one is drawn, and the types and size its rule
  names, parsed into a closed list and an integer.

## THE ZERO RULE

No resume card read, on a page whose heading and upload control drew, is not
"you have none": no empty state has been captured, so it raises.

## IT PRESSES NOTHING

No switch, no options button, no upload control is touched. Every read is a
locator read in the skeleton grammar.
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import dom
from linkedin_server.errors import ExtractionFailedError

#: The page's one address: the read boundary's admitted line for it, exactly.
PAGE_URL = "https://www.linkedin.com/jobs/application-settings/"

#: The page's heading, MEASURED.
PAGE_HEADING = "Resumes and application data"

#: Each switch, by the label LinkedIn binds to it, MEASURED, with the key it
#: is returned as and the census rows that would change it.
SWITCHES: dict[str, str] = {
    "Allow LinkedIn to save your resumes and answers": "save_resumes_and_answers",
    "Allow recruiters to view your resumes": "share_resume_data_with_hirers",
}

#: The upload control's word, MEASURED.
UPLOAD_LABEL = "Upload resume"

#: The file types a resume's own suffix is read as. Closed: any other suffix
#: is ``other``, and the name itself never leaves.
RESUME_TYPES: tuple[str, ...] = ("pdf", "docx", "doc")

#: The card's date line, MEASURED in two forms: ``Last used on 9/2/2025`` and
#: ``Uploaded on 10/14/2025`` (digits shown here are invented).
_DATE_LINE = re.compile(r"(Last used on|Uploaded on) ([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})")
_DATE_KINDS = {"Last used on": "last_used", "Uploaded on": "uploaded"}

#: The upload rule, MEASURED as ``DOC, DOCX, PDF (5MB)``.
_RULE = re.compile(r"((?:[A-Z]{3,4}, ){0,6}[A-Z]{3,4}) \(([0-9]{1,3}) ?MB\)")

#: Milliseconds any one read may wait.
READ_TIMEOUT_MS = 2000

#: The most cards, labels and paragraphs read on one page.
MAX_PARTS = 60

MAIN = 'div[role="main"]'


def collapsed(text: Any) -> str:
    """White space collapsed and the ends trimmed; ``""`` for a non-string."""
    return " ".join(text.split()) if isinstance(text, str) else ""


def landed_on_the_page(landed: Any) -> bool:
    """Whether the one load kept this page's own path. A yes or a no."""
    if not isinstance(landed, str):
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and parts.netloc.lower() == "www.linkedin.com"
        and parts.path.rstrip("/") == "/jobs/application-settings"
    )


async def _count(locator: Any, failed: list[int]) -> int:
    try:
        value = await locator.count()
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return 0
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


async def _text(locator: Any, failed: list[int]) -> Optional[str]:
    try:
        value = await locator.inner_text(timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return None
    return value if isinstance(value, str) else None


async def _attribute(locator: Any, name: str, failed: list[int]) -> Optional[str]:
    try:
        value = await locator.get_attribute(name, timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return None
    return value if isinstance(value, str) else None


def resume_type(name: Optional[str]) -> Optional[str]:
    """A file name's own suffix, as one of :data:`RESUME_TYPES`, ``other``, or
    ``None`` for no name. PURE: the name is compared here and never kept."""
    line = collapsed(name).lower()
    if not line:
        return None
    for suffix in RESUME_TYPES:
        if line.endswith("." + suffix):
            return suffix
    return "other"


def date_of(line: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """``(kind, ISO date)`` of a card's date line, or ``(None, None)``."""
    found = _DATE_LINE.fullmatch(collapsed(line))
    if not found:
        return None, None
    month, day, year = int(found.group(2)), int(found.group(3)), int(found.group(4))
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None, None
    return _DATE_KINDS[found.group(1)], "%04d-%02d-%02d" % (year, month, day)


def upload_rule(line: Optional[str]) -> Optional[dict[str, Any]]:
    """The upload rule's types and size, or ``None`` when the line is not one."""
    found = _RULE.fullmatch(collapsed(line))
    if not found:
        return None
    return {
        "types": [word.lower() for word in found.group(1).split(", ")],
        "max_megabytes": int(found.group(2)),
    }


async def read_application_settings(page: Any) -> dict[str, Any]:
    """His resumes-and-application-data page, as ``page`` already shows it.

    Raises ``ExtractionFailedError`` when the page's heading is not drawn, or
    when no resume card is read: no empty state has been captured, so a zero
    here is never reported as "you have none".
    """
    failed = [0]
    main = page.locator(MAIN)
    headings = [collapsed(await _text(main.locator("h1").nth(i), failed))
                for i in range(min(await _count(main.locator("h1"), failed), 5))]
    out: dict[str, Any] = {
        "page_heading_drawn": headings.count(PAGE_HEADING) == 1,
        "switches": {key: "unknown" for key in SWITCHES.values()},
        "switch_labels_unrecognised": 0,
        "resumes": [],
        "resume_cards_withheld": 0,
        "file_control": {"offered": False, "rule": None},
    }
    # THE SWITCHES: a label names its input by ``for``; the input's own
    # ``aria-checked`` is the state. Compared here, never built into a selector.
    inputs = main.locator('input[role="switch"]')
    states: dict[str, str] = {}
    for index in range(min(await _count(inputs, failed), MAX_PARTS)):
        ident = await _attribute(inputs.nth(index), "id", failed)
        checked = await _attribute(inputs.nth(index), "aria-checked", failed)
        if ident:
            states[ident] = {"true": "on", "false": "off"}.get(checked or "", "unknown")
    labels = main.locator("label")
    file_targets: list[str] = []
    for index in range(min(await _count(labels, failed), MAX_PARTS)):
        label = labels.nth(index)
        word = collapsed(await _text(label, failed))
        target = await _attribute(label, "for", failed) or ""
        if word == UPLOAD_LABEL:
            file_targets.append(target)
            continue
        key = SWITCHES.get(word)
        if key is None:
            if target in states:
                out["switch_labels_unrecognised"] += 1
            continue
        out["switches"][key] = states.get(target, "unknown")
    files = main.locator('input[type="file"]')
    file_ids = [await _attribute(files.nth(i), "id", failed) for i in range(min(await _count(files, failed), 5))]
    out["file_control"]["offered"] = any(t and t in file_ids for t in file_targets)
    for index in range(min(await _count(main.locator("p"), failed), MAX_PARTS)):
        rule = upload_rule(await _text(main.locator("p").nth(index), failed))
        if rule is not None:
            out["file_control"]["rule"] = rule
    # THE RESUMES: every h3 in the region is a card's file name (measured:
    # four, one per card); its parent holds the card's date line.
    names = main.locator("h3")
    for index in range(min(await _count(names, failed), MAX_PARTS)):
        name = names.nth(index)
        kind = resume_type(await _text(name, failed))
        card = name.locator("xpath=..")
        dated = [date_of(await _text(card.locator("p").nth(i), failed))
                 for i in range(min(await _count(card.locator("p"), failed), 4))]
        dated = [d for d in dated if d[0] is not None]
        if kind is None or len(dated) != 1:
            out["resume_cards_withheld"] += 1
            continue
        out["resumes"].append({"type": kind, "date_shown": dated[0][0], "date": dated[0][1]})
    out["resume_count"] = len(out["resumes"])
    out["reads_failed"] = failed[0]
    if not out["page_heading_drawn"]:
        raise ExtractionFailedError(
            "the resumes and application data page drew no heading this reader "
            "knows, so nothing on it is read.",
            hint=dom._landing_note(page),
        )
    if not out["resumes"]:
        raise ExtractionFailedError(
            "no resume card was read on the resumes and application data page, "
            "and no empty state for it has ever been captured; an empty list "
            "here would be indistinguishable from a broken read "
            f"({out['resume_cards_withheld']} card(s) seen and withheld).",
            hint=dom._landing_note(page),
        )
    return out
