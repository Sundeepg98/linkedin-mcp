"""His own Verifications settings page: which verifications he holds, and each one's switch and controls (census ``P K1``).

ONE ADMITTED ADDRESS, :data:`VERIFICATIONS_URL`. ``readonly.py`` admits it by
its exact address plus a per-address exemption for ``verification`` (lane
admit5-26, VERIFICATIONS-PAGE-ADMITTED: "read-only, zero presses";
two-step verification stays refused). This module never navigates and
presses nothing.

MEASURED on the live lane's session-12 capture (load 15, served exact; the raw
page withheld by the people gate, the keyed skeleton kept; tracked copy
``tests/fixtures/live12/verifications.html`` and, with LinkedIn's words
written where their keyed shapes matched,
``tests/fixtures/live12/verifications_words.html``, written by
``scripts/_build_live12_settings_word_skeletons.py``). The page is Ember
markup whose class names and ``data-test-*`` hooks the skeleton keeps:

* one ``main``; in it the banner's ``h1`` (``data-test-header-title``)
  reading LinkedIn's ``Verifications``, beside a ``Back`` link to
  ``/mypreferences/d/categories/account``;
* ONE entry container, ``[data-test-verifications-evidences-container]``,
  holding three parts:
  - the entry itself, ``[data-test-verifications-evidences]``: an ``h3``
    reading ``Workplace`` and THREE detail lines in
    ``.verifications-evidences__innerContent`` -- his data (an employer may be
    among them), never read here;
  - a work-email consent section,
    ``[data-test-verifications-evidences-work-email-consent-toggle]``, holding
    ONE ``input[role=switch][type=checkbox]`` and an ``aria-hidden`` span
    drawing LinkedIn's state word ``On`` (the live DOM read the input checked:
    session 12's reading of the load); its label and helper lines are long
    copy no candidate matched, and are never read;
  - a delete section, ``[data-test-verifications-delete-evidence]``, holding
    one button whose text reads ``Delete``;
* under it, a line linking his email settings,
  ``/mypreferences/d/manage-email-addresses``, which the boundary refuses and
  this module never opens.

WHAT COMES BACK: CLOSED WORDS AND INTEGERS ONLY. A kind is its heading
compared exactly against :data:`KINDS` and returned as that literal; any other
heading is ``other``, COUNTED (``unknown_kinds``) and never named. The switch
state is LinkedIn's own word, ``On`` or ``Off``, compared exactly (``Off`` is
the switch's other word, DERIVED: the capture drew ``On``); ``unknown`` when
the word is neither or the section draws more than one switch, ``None`` when
the entry draws no consent section. ``delete_drawn`` is whether the delete
section draws a button reading exactly ``Delete`` -- read, never pressed:
removing a verification is census ``P K7``, a write this module does not
build.

ONE ENTRY PER CONTAINER IS WHAT WAS MEASURED. A container holding more than
one entry would make pairing a switch and a Delete to its verification a
guess, so it is WITHHELD and counted.

THE ZERO RULE: a page whose heading is not drawn, or on which no entry is
read, raises -- no empty state of this page has been captured, so no read
here can say "you hold none".
"""
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import urlsplit

from .config import BASE_URL
from .errors import ExtractionFailedError

#: THE ONE ADDRESS, admitted in ``readonly.py``, in the spelling session 12
#: loaded and was served exactly (load 15).
VERIFICATIONS_URL = f"{BASE_URL}/mypreferences/d/verifications"

_HOST = "www.linkedin.com"
_PATH = "/mypreferences/d/verifications"

#: The page's heading, as LinkedIn draws it (kept verbatim by the skeleton).
PAGE_HEADING = "Verifications"

#: Each verification kind, by its heading, MEASURED, and the literal it is
#: returned as.
KINDS: dict[str, str] = {"Workplace": "workplace"}

#: The switch's state words, compared exactly.
_STATE_WORDS: dict[str, str] = {"On": "on", "Off": "off"}

#: The delete section's button word, compared exactly.
DELETE_WORD = "Delete"

#: Why a whole read refuses. Closed.
REFUSALS = ("main_unreadable", "landed_elsewhere")

#: Milliseconds any one read may wait, and the most parts read on a page.
READ_TIMEOUT_MS = 2000
MAX_PARTS = 20

SCOPE = (
    "His Verifications settings page: which verifications he holds, each by "
    "its kind as a closed word, the state of its work-email consent switch and "
    "whether its Delete button is drawn. One page, nothing pressed. Detail "
    "lines are counted, never read; a kind this server has not measured is "
    "counted, never named. No entry read raises."
)


def landed_on_the_page(landed: Any) -> bool:
    """Did the load land on the Verifications page itself? PURE."""
    if not isinstance(landed, str) or not landed:
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return parts.scheme == "https" and parts.netloc == _HOST and parts.path.rstrip("/") == _PATH


def _reading() -> dict[str, Any]:
    """The answer's shape, every count at zero. Every key is fixed here."""
    return {
        "surface": "own_verifications",
        "refused": None,
        "page_heading_drawn": False,
        "verifications": [],
        "entries_seen": 0,
        "entries_withheld": 0,
        "unknown_kinds": 0,
        "reads_failed": 0,
        "readable": False,
        "scope": SCOPE,
    }


def landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not land on the page."""
    out = _reading()
    out["refused"] = "landed_elsewhere"
    return out


def _collapsed(text: Any) -> str:
    return " ".join(text.split()) if isinstance(text, str) else ""


async def _count(locator: Any, failed: list[int]) -> int:
    try:
        value = await locator.count()
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return 0
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


async def _text(locator: Any, failed: list[int]) -> str:
    try:
        value = await locator.inner_text(timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return ""
    return _collapsed(value)


async def _consent(container: Any, failed: list[int]) -> Optional[str]:
    """The entry's work-email consent switch, by LinkedIn's own state word."""
    sections = container.locator("[data-test-verifications-evidences-work-email-consent-toggle]")
    if await _count(sections, failed) != 1:
        return None
    section = sections.nth(0)
    if await _count(section.locator('input[role="switch"]'), failed) != 1:
        return "unknown"
    words = section.locator('span[aria-hidden="true"]')
    seen = [await _text(words.nth(i), failed) for i in range(min(await _count(words, failed), 4))]
    states = [_STATE_WORDS[word] for word in seen if word in _STATE_WORDS]
    return states[0] if len(states) == 1 else "unknown"


async def _delete_drawn(container: Any, failed: list[int]) -> bool:
    buttons = container.locator("[data-test-verifications-delete-evidence] button")
    words = [await _text(buttons.nth(i), failed) for i in range(min(await _count(buttons, failed), 4))]
    return words.count(DELETE_WORD) == 1


async def read_verifications(page: Any) -> dict[str, Any]:
    """His Verifications page, already open: each verification, closed words only.

    The page must already be at :data:`VERIFICATIONS_URL`. One read; no
    navigation, press or scroll. Raises when the heading is not drawn or no
    entry is read.
    """
    out = _reading()
    failed = [0]
    main = page.locator("main")
    if await _count(main, failed) != 1:
        out["refused"] = "main_unreadable"
        out["reads_failed"] = failed[0]
        return out
    region = main.nth(0)
    headings = region.locator("h1")
    titles = [await _text(headings.nth(i), failed) for i in range(min(await _count(headings, failed), 4))]
    out["page_heading_drawn"] = titles.count(PAGE_HEADING) == 1
    containers = region.locator("[data-test-verifications-evidences-container]")
    for index in range(min(await _count(containers, failed), MAX_PARTS)):
        container = containers.nth(index)
        out["entries_seen"] += 1
        entries = container.locator("[data-test-verifications-evidences]")
        if await _count(entries, failed) != 1:
            out["entries_withheld"] += 1
            continue
        entry = entries.nth(0)
        kinds = entry.locator("h3")
        heading = await _text(kinds.nth(0), failed) if await _count(kinds, failed) == 1 else ""
        kind = KINDS.get(heading)
        if kind is None:
            out["unknown_kinds"] += 1
            kind = "other"
        out["verifications"].append({
            "kind": kind,
            "detail_lines": await _count(
                entry.locator('[class*="verifications-evidences__innerContent"] p'), failed
            ),
            "work_email_consent": await _consent(container, failed),
            "delete_drawn": await _delete_drawn(container, failed),
        })
    out["reads_failed"] = failed[0]
    if not out["page_heading_drawn"]:
        raise ExtractionFailedError(
            "the Verifications page drew no heading this reader knows, so "
            "nothing on it is read.",
            url=VERIFICATIONS_URL,
        )
    if not out["verifications"]:
        raise ExtractionFailedError(
            "no verification entry was read on the Verifications page, and no "
            "empty state for it has ever been captured; an empty list here "
            "would be indistinguishable from a broken read "
            f"({out['entries_seen']} entry container(s) seen, "
            f"{out['entries_withheld']} withheld).",
            url=VERIFICATIONS_URL,
        )
    out["readable"] = True
    return out
