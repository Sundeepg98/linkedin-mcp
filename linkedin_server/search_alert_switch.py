"""The job-alert switch at the head of one job search's results: address it, read it, aim it, verify it.

Census row ``J 31`` -- *create a job alert from a search*. Two writes act
through it, each the other's inverse, built in one change
(``HIS-OWN-CURATION-NOT-OUTWARD``: a job alert is his own saved query; nobody
else sees it): ``set_search_job_alert`` (off -> on) and
``unset_search_job_alert`` (on -> off). The address, the selectors, the
readings and the verdicts live here; ``writes`` delegates to them, as it does
to ``job_alert_switch`` for the posting's similar-jobs alert (``J 161``).

## THE ADDRESS, AND WHO SUPPLIES IT

The search is named by the CALLER'S OWN ARGUMENTS and nothing else:
:func:`query_for` composes ``keywords=<k>`` and, when one is given,
``&location=<l>`` -- urlencoded, the same two keys, in the same order,
``linkedin_search_jobs`` writes first -- and that query string is the grant's
target. The page may VETO it (:func:`landed_on_search`, the landing must be
the same search) and never supplies one (``PAGE-MAY-VETO-NEVER-SUPPLY``).
Filters are not carried: the alert is set on the search these two keys name.

## WHAT IS MEASURED, AND WHAT IS NOT

MEASURED on live session 2's classic job search (2026-09-28, ``/jobs/search/``;
the tracked copy is ``tests/fixtures/live2/j107.html``, and
``tests/fixtures/live2/j107_search_alert.html`` is the same copy with the
toggle's one word written by keyed shape,
``scripts/_build_search_alert_skeleton.py``): in the results list's header,
ONE ``div`` wearing LinkedIn's class :data:`TOGGLE_CLASS`; inside it a
``span.artdeco-toggle__text`` whose text is exactly :data:`WORD`, a ``label``
pointing at the switch (its hidden text, 27 letters in 33 characters, matched
by no candidate and NEVER READ here), and ONE ``input[role=switch]
[type=checkbox]`` drawing ``aria-checked`` as the string for off, with no
``checked`` attribute. The page draws no other ``input[role=switch]``.

NOT MEASURED (DERIVED, and every verdict that rests on it says so): the ON
state -- ``aria-checked`` reading ``true`` beside a checked property, under the
same word. If LinkedIn changes the word when the alert is on, the On reading
is ``unknown`` and the unset refuses; the first supervised set measures it.

NOT MEASURED EITHER: WHETHER A CLICK REACHES THE SWITCH. On this artdeco toggle
the input IS the drawn switch (``artdeco-toggle__button``), so the press aims
the input itself. NO TRIAL PRESS IS TAKEN: a trial click is a mutating call
the read boundary must declare, and its one declared trial click is
``job_alert_switch.trial_press``'s, for ``J 161``'s toggle alone (the sixteenth
entry of ``readonly.SANCTIONED_MUTATIONS``, on the coordinator's order). This
module does not widen that list. A press that cannot reach the switch throws
inside ``writes.perform``'s own click, the receipt says so, and the fresh
render says what LinkedIn stored.

THE PAGE IS LINKEDIN'S CLASSIC JOB SEARCH, and the same capture draws a
deprecation banner (``section.jobs-search-cjs-deprecation-banner``). A landing
anywhere else -- the AI job search, ``/jobs/search-results/`` -- is not the
search these arguments name, and is refused.

## WHAT NEVER LEAVES THIS MODULE

The toggle's hidden label is not read at all; the readings are counts, two
closed words (the toggle's word, ``aria-checked``) and one boolean. The query
leaves only as the caller's own two values.
"""
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit

from linkedin_server import coerce

#: The two actions that act through this switch.
SET: str = "set_search_job_alert"
UNSET: str = "unset_search_job_alert"
ACTIONS: tuple[str, str] = (SET, UNSET)

#: The page the switch is drawn on, and the grant's address template.
SEARCH_PATH = "/jobs/search/"
URL_TEMPLATE = "https://www.linkedin.com/jobs/search/?{target}"

#: LinkedIn's class for the toggle, and the toggle's visible word, MEASURED on
#: session 2's capture (the word by keyed shape).
TOGGLE_CLASS = "jobs-search-create-alert__artdeco-toggle"
WORD = "Set alert"

#: The toggle container; the switch inside it (THE PRESS TARGET); every switch
#: on the page; the toggle's own word.
TOGGLE = f"div.{TOGGLE_CLASS}"
SWITCH = f"{TOGGLE} input[role='switch']"
SWITCHES_ON_PAGE = "input[role='switch']"
TOGGLE_WORD = f"{TOGGLE} > span.artdeco-toggle__text"

#: The states. ``alert_off`` is measured; ``alert_on`` is DERIVED.
ALERT_OFF: str = "alert_off"
ALERT_ON: str = "alert_on"
UNKNOWN: str = "unknown"

#: ``aria-checked``'s two values, closed, and the state each names.
ARIA_STATES: dict[str, str] = {"false": ALERT_OFF, "true": ALERT_ON}

#: The longest keywords and location this composes. LinkedIn's own search box
#: is the bound a person types into; these are generous above it and keep a
#: grant's target from being a document.
MAX_KEYWORDS = 200
MAX_LOCATION = 100


def _clean(value: Any, *, name: str, limit: int, required: bool) -> tuple[Optional[str], str]:
    """``(value, why)``: one argument stripped and checked, or ``(None, why)``.
    The why describes the SHAPE and never repeats the value."""
    if value is None:
        value = ""
    if not isinstance(value, str):
        return (None, f"{name} must be text.")
    text = value.strip()
    if not text:
        if required:
            return (None, f"{name} is required: an alert is set on a search with keywords.")
        return ("", "")
    if len(text) > limit:
        return (None, f"{name} is {len(text)} characters; at most {limit} are accepted.")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        return (None, f"{name} carries a control character, which no search box takes.")
    return (text, "")


def query_for(keywords: Any, location: Any = "") -> tuple[Optional[str], str]:
    """``(query, why)``: the canonical query string for one search, or
    ``(None, why)``. PURE. ``keywords`` first, ``location`` only when given,
    urlencoded -- one spelling, so a grant's target is one string."""
    words, why = _clean(keywords, name="keywords", limit=MAX_KEYWORDS, required=True)
    if words is None:
        return (None, why)
    place, why = _clean(location, name="location", limit=MAX_LOCATION, required=False)
    if place is None:
        return (None, why)
    pairs = [("keywords", words)] + ([("location", place)] if place else [])
    return (urlencode(pairs), "")


def canonical(target: Any) -> tuple[Optional[str], str]:
    """``(query, why)``: ``target`` back in the one spelling :func:`query_for`
    writes, or ``(None, why)``. A target is accepted only if it IS that
    spelling: exactly ``keywords`` and an optional ``location``, in that order,
    each once, re-composing to itself."""
    raw = str(target if target is not None else "").strip()
    try:
        pairs = parse_qsl(raw, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        return (None, "the search is not a query string of keywords and an optional location.")
    keys = [key for key, _value in pairs]
    if keys not in (["keywords"], ["keywords", "location"]):
        return (None, "the search must carry keywords and, optionally, a location, "
                      "and nothing else.")
    values = dict(pairs)
    query, why = query_for(values.get("keywords"), values.get("location", ""))
    if query is None:
        return (None, why)
    if query != raw:
        return (None, "the search is not in its one canonical spelling: compose it "
                      "from keywords and a location, never by hand.")
    return (query, "")


def describe(target: str) -> dict[str, str]:
    """The caller's own two values, for the block he confirms."""
    values = dict(parse_qsl(str(target or ""), keep_blank_values=True))
    return {"keywords": values.get("keywords", ""), "location": values.get("location", "")}


def landed_on_search(landed: Any, target: str) -> bool:
    """Whether the browser is on the classic job search this target names.
    PURE. The host and path must be the search's; ``keywords`` must read the
    caller's value once, and ``location`` too when he gave one. LinkedIn's own
    additions to the query (a geo id, a view flag) do not re-address the
    search, so they are not compared."""
    try:
        parts = urlsplit(str(landed or ""))
    except ValueError:
        return False
    if parts.scheme != "https" or parts.netloc != "www.linkedin.com":
        return False
    if parts.path.rstrip("/") + "/" != SEARCH_PATH:
        return False
    wanted = describe(target)
    if not wanted["keywords"]:
        return False
    got = parse_qs(parts.query, keep_blank_values=True)
    if got.get("keywords") != [wanted["keywords"]]:
        return False
    if wanted["location"] and got.get("location") != [wanted["location"]]:
        return False
    return True


async def read_switch(page: Any) -> dict[str, Any]:
    """COUNTS, TWO CLOSED WORDS AND ONE BOOLEAN, off the search already open.
    Never raises; ``error`` is an exception TYPE name, never its message."""
    out: dict[str, Any] = {
        "toggles": 0,
        "switches_in_toggle": 0,
        "switches_on_page": 0,
        "word": None,
        "aria_checked": None,
        "checked": None,
        "error": None,
    }
    try:
        out["toggles"] = coerce.as_count(await page.locator(TOGGLE).count())
        out["switches_in_toggle"] = coerce.as_count(await page.locator(SWITCH).count())
        out["switches_on_page"] = coerce.as_count(await page.locator(SWITCHES_ON_PAGE).count())
        if out["toggles"] == 1 and out["switches_in_toggle"] == 1:
            words = page.locator(TOGGLE_WORD)
            if coerce.as_count(await words.count()) == 1:
                word = " ".join(str(await words.first.inner_text()).split())
                # A CLOSED WORD OR NOTHING: anything else is recorded as its
                # absence, never as text.
                out["word"] = word if word == WORD else "other"
            switch = page.locator(SWITCH).first
            aria = await switch.get_attribute("aria-checked")
            out["aria_checked"] = aria if aria in ARIA_STATES else ("other" if aria else None)
            out["checked"] = bool(await switch.is_checked())
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def switch_verdict(reading: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    """``(facts, state, why)`` for the search's alert switch. PURE.

    ``alert_off``  exactly one toggle wearing LinkedIn's class, exactly one
                   switch in it and on the page, the toggle's word ``Set
                   alert``, ``aria-checked`` off and the checked property
                   false -- the MEASURED shape
    ``alert_on``   the same, with ``aria-checked`` on and the property true --
                   DERIVED
    ``unknown``    everything else, and the why says which, in counts
    """
    reading = dict(reading or {})
    facts: dict[str, Any] = {
        "toggles": coerce.as_count(reading.get("toggles")),
        "switches_in_toggle": coerce.as_count(reading.get("switches_in_toggle")),
        "switches_on_page": coerce.as_count(reading.get("switches_on_page")),
        "word": reading.get("word"),
        "aria_checked": reading.get("aria_checked"),
        "checked": reading.get("checked"),
    }
    if reading.get("error"):
        return (facts, UNKNOWN, "the alert switch could not be read "
                f"({str(reading.get('error'))[:64]}); refused rather than guessed.")
    if facts["toggles"] != 1:
        return (facts, UNKNOWN, f"{facts['toggles']} alert toggles on the search, where "
                "exactly one is required.")
    if facts["switches_in_toggle"] != 1:
        return (facts, UNKNOWN, f"the toggle draws {facts['switches_in_toggle']} input "
                "switch(es), where exactly one is required.")
    if facts["switches_on_page"] != 1:
        return (facts, UNKNOWN, f"{facts['switches_on_page']} input switches on the page; "
                "a second one makes the aim ambiguous.")
    if facts["word"] != WORD:
        return (facts, UNKNOWN, "the toggle does not draw its measured word beside the "
                "switch, so it is not taken to be the alert toggle.")
    state = ARIA_STATES.get(str(facts["aria_checked"]))
    if state is None:
        return (facts, UNKNOWN, "the switch draws no closed aria-checked value, so its "
                "state is not read off the page.")
    if (state == ALERT_ON) is not (facts["checked"] is True):
        return (facts, UNKNOWN, f"the switch's aria-checked names {state} and its checked "
                f"property reads {facts['checked']!r}: they disagree, so neither is believed.")
    if state == ALERT_OFF:
        return (facts, ALERT_OFF, "exactly one job-alert switch at the head of the search, "
                "its word Set alert, reading off on both its aria-checked and its checked "
                "property -- the shape MEASURED on live session 2.")
    return (facts, ALERT_ON, "exactly one job-alert switch at the head of the search, its "
            "word Set alert, reading on on both its aria-checked and its checked property. "
            "The ON shape is DERIVED: no capture holds this switch on.")


async def read_state(page: Any) -> tuple[dict[str, Any], str, str]:
    """The preview's and the click's reading, off the search already open."""
    return switch_verdict(await read_switch(page))


def verification_verdict(reading: dict[str, Any], wanted: str) -> tuple[str, str]:
    """``(state, why)`` off a FRESH render of the search, after the press.

    The switch carries both states on one control, so the answer is strong in
    both directions: the state it reads is the state LinkedIn stored. ``wanted``
    is the destination; the verdict is the state read, and the caller compares.
    """
    _facts, state, why = switch_verdict(reading)
    if state == wanted:
        return (state, "on a fresh render of the search the switch reads "
                f"{state}: the change was stored. " + why)
    return (state, f"on a fresh render of the search the switch reads {state}, not "
            f"{wanted}. " + why)
