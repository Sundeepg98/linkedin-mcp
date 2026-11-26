"""THE SEARCH BOX'S TYPEAHEAD, DISCLOSED: his recent searches read, the box closed by Escape.

Census row ``N 95`` (*View and re-run a recent search*). Implements the
orchestrator's SEARCH-BOX-TYPEAHEAD-DISCLOSURE (2026-11-26, the answer to lane
build-net2's ``Q-SEARCH-BOX-PRESS-SHAPE``; integration 6 registers it), over
live session 11's capture of the feed with its search box open (load 28,
``tests/fixtures/live11/feed_search_box_open.html``).

## WHAT WAS MEASURED (session 11, load 28)

The global search box's ``input`` sits inside a ``role=search`` container and
carries ``aria-autocomplete`` -- and neither ``aria-expanded`` nor
``aria-haspopup``, so :data:`press.SANCTIONED_SHAPES` cannot reach it. ONE
click on it opened ONE popup (the live runner's reading: one new popup, no
dialog, the address unmoved) and ONE Escape closed it. While open, the
input's ``aria-owns`` names a ``role=listbox`` holding, in order:

* a heading, ``Recent`` (keyed shape), and a ``Clear all`` option (keyed
  shape) -- an option that would act, never pressed here;
* a ``role=group`` of four options, each ONE link to a member's profile
  (``/in/``): the people he viewed recently;
* a ``role=group`` with NO heading of its own, of two options, each ONE link
  to a search address -- ``/jobs/search-results/?keywords=...`` and
  ``/search/results/all/?keywords=...`` (the path word ``search-results``
  verified by keyed shape): HIS RECENT SEARCHES;
* a ``role=group`` under its own ``p`` heading, ``Try searching for`` (keyed
  shape): LinkedIn's suggestions.

Closed, the input owns nothing and the page draws no listbox (the feed's
other session-11 captures: 0 listboxes on each).

## WHAT IS PRESSED, AND WHAT IS NOT

The one entry of :data:`TYPEAHEADS` names one surface, one target and one
group. :func:`disclose_recent_searches`, in order, refusing at the first
failed step and touching nothing on the page after a refusal:

1. CONDITION 1: the address is admitted (``press.check_address``) and is the
   entry's surface -- decided before the page is asked for anything;
2. CONDITION 2: the target ``[role=search] input[aria-autocomplete]`` matches
   EXACTLY ONE element, visible -- by attribute, never a label. None, or two
   or more, refuses NAMING THE COUNT, with nothing pressed;
3. the box reads closed: no visible listbox, and the target owns none;
4. ONE click on the target (:func:`_press`, step ``open``);
5. the listbox the target owns, waited for (bounded), and in it the
   recent-searches group, located by its own structure and read -- ONLY it;
6. ONE Escape on the target (step ``close``), and CONDITION 4: the closure
   verified -- no visible listbox, the target owning none -- bounded;
7. CONDITION 3 is the structural argument the ruling accepted (below), and
   its refuters are read after the press: the address moved, or a dialog
   drawn, refuses.

NOTHING IS TYPED. :func:`_press` takes a STEP from :data:`STEPS` -- ``open``
is a click, ``close`` is the one key ``Escape`` -- and refuses anything else,
so no key that types, no Enter that would run a search, and no fill exist
here. No option is pressed: not a recent search, not a suggestion, not
``Clear all``.

## WHAT LEAVES

Each recent search: its ``keywords`` -- what he typed into his own search box,
returned to his own session at runtime under HIS-OWN-TEXT-AT-RUNTIME,
sanitised and bounded, never stored -- and its ``vertical``, from a closed
list keyed by the option's own address (``jobs``, ``all``; any other results
path is ``other``). Re-running one is the caller passing its keywords to a
search tool (D6); this module follows no address it read.

THE PEOPLE OPTIONS ARE NEVER READ OR RETURNED. The group of recently viewed
members is excluded by structure INSIDE THE PAGE -- its options' links are not
search addresses -- so nothing of it crosses: no name, no link, no count of
it. Neither do the suggestions, the heading or ``Clear all``.

## THE CALL SITES

``readonly.SANCTIONED_MUTATIONS`` holds two lines for this module, both in
:func:`_press`: the click that opens (``open``) and the Escape that closes
(``close``), one call site each -- the share-link module's precedent for a
disclosure closed by Escape.
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import parse_qsl, urlsplit

from linkedin_server import coerce, press, readonly
from linkedin_server.errors import ExtractionFailedError, WriteAttemptError

_refuse = press._refuse

#: The one page this module presses on: the feed, where the box was measured.
#: Admitted for reading; a press never extends reach (condition 1).
PAGE_URL = "https://www.linkedin.com/feed/"

#: THE TARGET, by attribute (condition 2): the one search input inside a
#: ``role=search`` container that carries ``aria-autocomplete``.
TARGET = '[role="search"] input[aria-autocomplete]'
TARGET_VISIBLE = TARGET + " >> visible=true"
#: Every ``aria-autocomplete`` input on the page, wherever it is: the
#: denominator a refusal names. Never a target.
AUTOCOMPLETE_INPUTS = "input[aria-autocomplete]"

_TARGET_X = "//*[@role='search']//input[@aria-autocomplete]"
#: The listbox THE TARGET OWNS: the element whose id the target's
#: ``aria-owns`` names. A listbox the target does not own is never read.
OWNED_LISTBOX = "xpath=//*[@role='listbox'][@id = " + _TARGET_X + "/@aria-owns]"
LISTBOXES_VISIBLE = '[role="listbox"] >> visible=true'
DIALOGS_VISIBLE = ":is([role=dialog], [role=alertdialog]) >> visible=true"

#: The two search addresses a recent search was measured to carry.
SEARCH_PREFIXES: tuple[str, ...] = (
    "https://www.linkedin.com/search/results/",
    "https://www.linkedin.com/jobs/search-results/",
)
_IS_SEARCH_LINK = " or ".join(f"starts-with(@href, '{prefix}')" for prefix in SEARCH_PREFIXES)

#: THE RECENT-SEARCHES GROUP, BY ITS OWN STRUCTURE: a ``role=group`` in the
#: owned listbox with no heading of its own, holding options, each option
#: holding exactly one link, and every one of those links a search address.
#: The people group fails the last (its links are profiles); the suggestions
#: group fails the first (its own ``p`` heading). XPath 1.0, evaluated by the
#: browser: nothing of a group that fails crosses back.
RECENT_GROUP = (
    OWNED_LISTBOX
    + "//*[@role='group']"
    + "[not(./p or ./h1 or ./h2 or ./h3 or ./h4 or ./*[@role='heading'])]"
    + "[.//*[@role='option']]"
    + "[not(.//*[@role='option'][count(.//a[@href]) != 1])]"
    + f"[not(.//*[@role='option']//a[@href][not({_IS_SEARCH_LINK})])]"
)
#: Each recent search's one link, inside that group only.
RECENT_LINKS = RECENT_GROUP + "//*[@role='option']//a[@href]"

#: A results path, to the closed word it is returned as. Measured: the two.
VERTICALS: dict[str, str] = {
    "/search/results/all/": "all",
    "/jobs/search-results/": "jobs",
}

#: THE STEPS, CLOSED. ``open`` is one click on the target; ``close`` is this
#: one key on it. There is no step that types.
STEPS: dict[str, str] = {"open": "click", "close": "Escape"}

#: The most recent searches returned, and the longest keywords kept.
MAX_RECENT = 10
KEYWORDS_CAP = 200
#: Bounded waits: the listbox opening, and closing.
POLLS = 12
POLL_MS = 250
CLICK_TIMEOUT_MS = press.CLICK_TIMEOUT_MS

_RULING = (
    "SEARCH-BOX-TYPEAHEAD-DISCLOSURE (orchestrator, 2026-11-26, answering "
    "Q-SEARCH-BOX-PRESS-SHAPE): the one [role=search] input[aria-autocomplete] "
    "on an admitted page, refused at runtime unless it matches exactly once; "
    "nothing typed; only the listbox's recent-searches group read, by its own "
    "structure, under HIS-OWN-TEXT-AT-RUNTIME, the people options never read "
    "or returned; closed by Escape and the closure verified; condition 3 the "
    "structural argument that a typeahead opening sends nothing outward."
)

_ENTRY_REQUIRED = ("surfaces", "target", "ruling", "condition_3", "why")

#: THE CLOSED TABLE: one entry, the whole of what this module may open.
TYPEAHEADS: tuple[tuple[str, dict[str, Any]], ...] = (
    (
        "recent_searches",
        {
            "surfaces": ("/feed/",),
            "target": TARGET,
            "ruling": _RULING,
            "condition_3": {
                "route": "structural_argument",
                "argument": (
                    "Opening his own search box's typeahead is a disclosure of "
                    "his own search history in his own browser: it sends no "
                    "message, notifies no member, saves nothing and runs no "
                    "search. Nothing is typed and no option is pressed."
                ),
                "bound": "one click on the target and one Escape on it, nothing between",
                "refuters": (
                    "the address moved after the click",
                    "a dialog drawn after the click",
                ),
            },
            "why": (
                "N 95. Measured on session 11's feed (load 28): one click opened "
                "one popup, the input's own listbox, and one Escape closed it."
            ),
        },
    ),
)

_SPACE = re.compile(r"\s+")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def typeahead(key: Optional[str]) -> Optional[dict[str, Any]]:
    """The table entry for a key, or None. PURE."""
    for name, entry in TYPEAHEADS:
        if name == key:
            return entry
    return None


def check_page(url: Optional[str], key: str = "recent_searches") -> dict[str, Any]:
    """CONDITION 1 and the surface, before the page is asked for anything. PURE."""
    entry = typeahead(key)
    if entry is None:
        return _refuse(
            "typeahead_not_ruled",
            "the key is not in search_typeahead.TYPEAHEADS; a caller names an "
            "entry and cannot supply one.",
            terminal=True,
        )
    missing = [field for field in _ENTRY_REQUIRED if not entry.get(field)]
    if missing:
        return _refuse(
            "typeahead_entry_incomplete",
            f"the table entry is missing {missing}; an entry with no ruling is "
            "not an admission.",
            terminal=True,
        )
    address = press.check_address(url)
    if address.get("refused"):
        return address
    if urlsplit(str(url).strip()).path not in entry["surfaces"]:
        return _refuse(
            "typeahead_not_for_this_surface",
            "the page is not the surface this typeahead was measured on, and a "
            "search box measured on one page says nothing about another.",
            terminal=True,
        )
    return {"pressed": False, "page_ok": True}


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def _read_box(page: Any) -> dict[str, Any]:
    """COUNTS ONLY: the target, every autocomplete input, the listboxes, the
    dialogs. Never raises; ``error`` is an exception TYPE name."""
    out: dict[str, Any] = {
        "targets": 0,
        "targets_visible": 0,
        "autocomplete_inputs": 0,
        "listboxes_visible": 0,
        "owned_listboxes": 0,
        "dialogs": 0,
        "error": None,
    }
    try:
        out["targets"] = await _count(page, TARGET)
        out["targets_visible"] = await _count(page, TARGET_VISIBLE)
        out["autocomplete_inputs"] = await _count(page, AUTOCOMPLETE_INPUTS)
        out["listboxes_visible"] = await _count(page, LISTBOXES_VISIBLE)
        out["owned_listboxes"] = await _count(page, OWNED_LISTBOX)
        out["dialogs"] = await _count(page, DIALOGS_VISIBLE)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def _facts(reading: Any) -> dict[str, int]:
    reading = reading if isinstance(reading, dict) else {}
    return {
        key: coerce.as_count(reading.get(key))
        for key in (
            "targets", "targets_visible", "autocomplete_inputs",
            "listboxes_visible", "owned_listboxes", "dialogs",
        )
    }


def target_verdict(reading: Any) -> dict[str, Any]:
    """CONDITION 2, and the closed state, before any press. PURE."""
    facts = _facts(reading)
    error = reading.get("error") if isinstance(reading, dict) else "unreadable"
    if error:
        refusal = _refuse(
            "unreadable",
            f"the page could not be counted ({error}); nothing was pressed.",
            terminal=False,
        )
        return {**refusal, "observed": facts}
    if facts["targets"] != 1 or facts["targets_visible"] != 1:
        refusal = _refuse(
            "target_count",
            f"the page draws {facts['targets']} input(s) of the shape {TARGET} "
            f"({facts['targets_visible']} visible), where exactly one is "
            f"required; {facts['autocomplete_inputs']} autocomplete input(s) on "
            "the page in all. Nothing was pressed: choosing among inputs is "
            "choosing by position.",
            terminal=False,
        )
        return {**refusal, "observed": facts}
    if facts["listboxes_visible"] or facts["owned_listboxes"]:
        refusal = _refuse(
            "already_open",
            f"{facts['listboxes_visible']} listbox(es) read visible and the "
            f"target owns {facts['owned_listboxes']} before any press, so the "
            "box is not in the closed state this press starts from and its "
            "closure could not be shown. Nothing was pressed.",
            terminal=False,
        )
        return {**refusal, "observed": facts}
    return {"pressed": False, "target_ok": True, "observed": facts}


def clean_keywords(value: Any) -> str:
    """His keywords as he typed them: control characters out, whitespace
    collapsed, bounded. PURE."""
    text = _CONTROL.sub(" ", str(value or ""))
    return _SPACE.sub(" ", text).strip()[:KEYWORDS_CAP]


def parse_search_address(href: Any) -> Optional[dict[str, str]]:
    """A recent search's ``keywords`` and ``vertical``, from its own address,
    or None. PURE: a closed list of hosts and paths decides the vertical."""
    parts = urlsplit(str(href or ""))
    if parts.scheme != "https" or parts.netloc != "www.linkedin.com":
        return None
    address = f"https://www.linkedin.com{parts.path}"
    if not address.startswith(SEARCH_PREFIXES):
        return None
    vertical = VERTICALS.get(parts.path, "other")
    keywords = ""
    for name, value in parse_qsl(parts.query, keep_blank_values=True):
        if name == "keywords":
            keywords = clean_keywords(value)
            break
    if not keywords:
        return None
    return {"keywords": keywords, "vertical": vertical}


async def _read_recent_searches(page: Any) -> dict[str, Any]:
    """THE ONE READING OF PAGE TEXT: the recent-searches group, and only it.

    The group must be EXACTLY ONE by its structure, and every link in it must
    parse as a search address with keywords, or this raises -- a group read
    wrong is never returned as his history. Raises
    :class:`ExtractionFailedError` with this module's own sentence only, its
    ``url`` the address this module ASKED FOR (:data:`PAGE_URL`, a constant),
    never the landing.
    """
    groups = await _count(page, RECENT_GROUP)
    if groups != 1:
        raise ExtractionFailedError(
            f"{groups} group(s) in the search box's own listbox have the "
            "recent-searches structure, where exactly one is required.",
            url=PAGE_URL,
        )
    links = page.locator(RECENT_LINKS)
    drawn = coerce.as_count(await links.count())
    if drawn < 1:
        raise ExtractionFailedError("the recent-searches group holds no link.", url=PAGE_URL)
    searches: list[dict[str, str]] = []
    for index in range(min(drawn, MAX_RECENT)):
        parsed = parse_search_address(await links.nth(index).get_attribute("href"))
        if parsed is None:
            raise ExtractionFailedError(
                "a link in the recent-searches group is not a search address "
                "carrying keywords, so the group is not read as his history.",
                url=PAGE_URL,
            )
        searches.append(parsed)
    return {
        "recent_searches": searches,
        "count": len(searches),
        "drawn": drawn,
        "capped": drawn > MAX_RECENT,
    }


async def _press(target: Any, step: str) -> None:
    """THE ONLY CALLS IN THIS MODULE THAT ACT ON THE PAGE: ``open``, one
    click on the target, and ``close``, one Escape on it. Any other step is
    refused before the page is touched -- there is no step that types."""
    if step == "open":
        await target.click(timeout=CLICK_TIMEOUT_MS)
        return
    if step == "close":
        await target.press(STEPS["close"], timeout=CLICK_TIMEOUT_MS)
        return
    raise WriteAttemptError(
        f"refusing step {step!r}: the search box's typeahead is opened with one "
        "click and closed with one Escape, and nothing is ever typed into it."
    )


async def _settle(page: Any, *, want_open: bool) -> dict[str, Any]:
    """Poll the box, bounded, until it reads open (owned listbox drawn) or
    closed (no visible listbox, none owned). Returns the last reading."""
    reading = await _read_box(page)
    for _ in range(POLLS):
        facts = _facts(reading)
        if reading.get("error"):
            break
        if want_open and facts["owned_listboxes"] >= 1:
            break
        if not want_open and not facts["listboxes_visible"] and not facts["owned_listboxes"]:
            break
        await page.wait_for_timeout(POLL_MS)
        reading = await _read_box(page)
    return reading


async def _settle_group(page: Any) -> int:
    """Poll, bounded, for the recent-searches group in the owned listbox."""
    groups = await _count(page, RECENT_GROUP)
    for _ in range(POLLS):
        if groups >= 1:
            break
        await page.wait_for_timeout(POLL_MS)
        groups = await _count(page, RECENT_GROUP)
    return groups


async def disclose_recent_searches(page: Any, landed: str) -> dict[str, Any]:
    """Open his search box's typeahead, read his recent searches, close it.

    ``page`` is already on ``landed``, the address the caller's one load
    landed on, checked here before the page is asked for anything; this module
    never navigates. Returns a refusal (``refused`` and ``why``) or the
    reading; never raises for a page problem.

    AFTER THE CLICK, A REFUTER STOPS EVERYTHING: the address moved, a dialog
    drawn, or no listbox of the target's own drawn -- each refuses with
    nothing more pressed, and in particular no Escape, because an Escape with
    nothing of ours open could close something else on the page.
    """
    pre = check_page(landed)
    if pre.get("refused"):
        return pre
    before = await _read_box(page)
    verdict = target_verdict(before)
    if verdict.get("refused"):
        return verdict
    target = page.locator(TARGET)
    address_before = str(page.url)
    pressed = {"clicks": 0, "escapes": 0}
    common: dict[str, Any] = {
        "pressed_steps": pressed,
        "condition_3_route": "structural_argument",
    }
    try:
        await _press(target, "open")
    except Exception as exc:  # noqa: BLE001 - a click that cannot be made is a reading
        refusal = _refuse(
            "not_pressed",
            f"the click on the search box could not be made ({type(exc).__name__}); "
            "nothing opened and nothing was pressed.",
            terminal=False,
        )
        return {**refusal, **common, "closed": None, "observed": {"before": _facts(before)}}
    pressed["clicks"] = 1
    opened = await _settle(page, want_open=True)
    observed: dict[str, Any] = {"before": _facts(before), "open": _facts(opened)}
    if str(page.url) != address_before:
        refusal = _refuse(
            "address_moved",
            "the address moved after the click, which the structural argument "
            "says a typeahead opening never does; nothing more was pressed or "
            "read.",
            terminal=False,
        )
        return {**refusal, **common, "closed": None, "observed": observed}
    if _facts(opened)["dialogs"] > _facts(before)["dialogs"]:
        refusal = _refuse(
            "dialog_drawn",
            "a dialog was drawn after the click, which the structural argument "
            "says a typeahead opening never draws; nothing more was pressed or "
            "read, and nothing in the dialog was touched.",
            terminal=False,
        )
        return {**refusal, **common, "closed": None, "observed": observed}
    if _facts(opened)["owned_listboxes"] < 1:
        refusal = _refuse(
            "did_not_open",
            "the click drew no listbox the search box owns, so there was nothing "
            "to read; nothing is Escaped, since an Escape with nothing of ours "
            "open could close something else.",
            terminal=False,
        )
        return {**refusal, **common, "closed": None, "observed": observed}
    reading: Optional[dict[str, Any]] = None
    unread: Optional[str] = None
    observed["recent_groups"] = await _settle_group(page)
    try:
        reading = await _read_recent_searches(page)
    except ExtractionFailedError as exc:
        unread = str(exc)
    except Exception as exc:  # noqa: BLE001 - the box is closed below whatever happened
        unread = f"the recent-searches group could not be read ({type(exc).__name__})."
    try:
        await _press(target, "close")
        pressed["escapes"] = 1
    except Exception as exc:  # noqa: BLE001 - reported, never smoothed
        unread = unread or f"the Escape could not be pressed ({type(exc).__name__})."
    after = await _settle(page, want_open=False)
    observed["after"] = _facts(after)
    closed = not observed["after"]["listboxes_visible"] and not observed["after"]["owned_listboxes"]
    common.update({"closed": closed, "observed": observed})
    if not closed:
        refusal = _refuse(
            "did_not_close",
            "the Escape did not close the search box's listbox, so the page is "
            "not shown as found; what was read is withheld. Look at the page.",
            terminal=False,
        )
        return {**refusal, **common}
    if reading is None:
        refusal = _refuse(
            "recent_group_unread",
            str(unread or "the recent-searches group was not read."),
            terminal=False,
        )
        return {**refusal, **common}
    return {**common, **reading, "pressed": True}
