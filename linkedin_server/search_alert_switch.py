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
:func:`query_for` composes ``keywords=<k>``, urlencoded -- the key
``linkedin_search_jobs`` writes first -- and that query string is the grant's
target. The page may VETO it (:func:`landed_on_search`, the landing must be
the same search) and never supplies one (``PAGE-MAY-VETO-NEVER-SUPPLY``).
Filters are not carried: the alert is set on the search the keywords name.

**THE ADDRESS IS THE AI SEARCH'S OWN SINCE LANE JOBS7 (2026-11-27).** The
classic ``/jobs/search/`` no longer serves: live session 12's load 3 asked
for it and was redirected to ``/jobs/search-results/`` with no classic list,
no deprecation banner and no classic toggle (``C-SRCH-1``, the decision
load). So :data:`URL_TEMPLATE` is the AI route's, and the AI page's own
switch is the ARM this pair presses (:data:`AI_ARM`). A PLACE IS REFUSED
before any load (:data:`PLACE_UNMEASURED`): the AI route addresses a place by
``geoId`` and ``distance``, and what it does with a text ``location`` is
unmeasured (capture ``C-SRCH-2``) -- an alert accepted for "these keywords
in that place" and set on the keywords alone would be the wrong alert, set
silently.

## THE TWO ARMS, AND WHICH ONE IS READ

The reader reads WHICHEVER arm the page draws, and refuses a page drawing
both or neither:

* :data:`AI_ARM` -- MEASURED on live session 11's raw page (search26, its
  section 3.1) and on BOTH of session 12's AI loads by keyed shape (lane
  jobs7's record, section 2.1; ``tests/fixtures/live12/c_srch_1_words.html``
  and ``c_srch_0b_words.html``): the page's ONE ``input[role=switch]
  [type=checkbox]``, nested inside a component keyed
  ``JobSearchAlertToggleRef_<query words>_<8 digits>_<1 digit>`` that
  occurs twice, nested; named by one ``label[for]`` holding no text;
  captioned :data:`CAPTION`, which its fifth ancestor first contains; drawn
  with NO ``checked`` attribute and NO ``aria-checked``. Off is that shape;
  ON is DERIVED -- the checked property true, still with no ``aria-checked``
  -- until the first supervised set measures it (``C-SRCH-6``).
* :data:`CLASSIC_ARM` -- MEASURED on live session 2's classic job search
  (2026-09-28; ``tests/fixtures/live2/j107_search_alert.html``, the tracked
  copy with the toggle's word written by keyed shape,
  ``scripts/_build_search_alert_skeleton.py``): ONE ``div`` wearing
  LinkedIn's class :data:`TOGGLE_CLASS`, a ``span.artdeco-toggle__text``
  reading :data:`WORD`, ONE ``input[role=switch]`` in it drawing
  ``aria-checked`` as the string for off. Kept because a landing on the
  classic page is still ACCEPTED (:data:`SEARCH_PATHS`): should LinkedIn
  serve it again at the AI address, its own switch is read there, the same
  search by the same keywords.

NOT MEASURED, on either arm: WHETHER A CLICK REACHES THE SWITCH. The press
aims the input itself; NO TRIAL PRESS IS TAKEN -- a trial click is a mutating
call the read boundary must declare, and its one declared trial click is
``job_alert_switch.trial_press``'s, for ``J 161``'s toggle alone. This
module does not widen that list. A press that cannot reach the switch throws
inside ``writes.perform``'s own click, the receipt says so, and the fresh
render says what LinkedIn stored.

## WHAT NEVER LEAVES THIS MODULE

The switches' labels are not read at all; the readings are counts, two
closed words (the classic toggle's word, ``aria-checked``), the caption's
counts and one boolean. The query leaves only as the caller's own value.
"""
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit

from linkedin_server import coerce

#: The two actions that act through this switch.
SET: str = "set_search_job_alert"
UNSET: str = "unset_search_job_alert"
ACTIONS: tuple[str, str] = (SET, UNSET)

#: THE AI SEARCH'S OWN PAGE, and the grant's address template (lane jobs7):
#: the classic page's address redirected here on live session 12's load 3.
SEARCH_PATH = "/jobs/search-results/"
URL_TEMPLATE = "https://www.linkedin.com/jobs/search-results/?{target}"
#: The classic page's path, ACCEPTED as a landing and never asked for.
CLASSIC_SEARCH_PATH = "/jobs/search/"
SEARCH_PATHS: tuple[str, str] = (SEARCH_PATH, CLASSIC_SEARCH_PATH)

#: The arm a reading was taken from: closed, declared here.
AI_ARM = "ai_toggle"
CLASSIC_ARM = "classic_toggle"

# -- the AI arm (sessions 11 and 12) ---------------------------------------

#: The prefix LinkedIn writes on the alert switch's component key; the rest
#: of the key is the query's own words and two digit runs, never read here.
AI_TOGGLE_KEY_PREFIX = "JobSearchAlertToggleRef_"
#: Every element keyed with that prefix (two, nested, on every capture).
AI_TOGGLE = f"[componentkey^='{AI_TOGGLE_KEY_PREFIX}']"
#: THE PRESS TARGET on the AI arm: the input switch inside the keyed toggle.
AI_SWITCH = f"{AI_TOGGLE} input[role='switch']"
#: The switch's caption, LinkedIn's own words, MEASURED by string equality on
#: session 11's raw page and by keyed shape on both of session 12's AI loads.
CAPTION = "Get job alerts for this search"
#: An element whose OWN text is exactly the caption.
CAPTION_ELEMENT = f"xpath=//*[normalize-space(text())='{CAPTION}']"
#: How far above the switch the caption may sit: its fifth ancestor first
#: contains it on both of session 12's loads; one more level of slack, and
#: never the whole page.
CAPTION_LEVELS = 6
CAPTION_NEAR_SWITCH = (
    f"xpath=ancestor::*[{CAPTION_LEVELS}]//*[normalize-space(text())='{CAPTION}']"
)

# -- the classic arm (session 2) ---------------------------------------------

#: LinkedIn's class for the toggle, and the toggle's visible word, MEASURED on
#: session 2's capture (the word by keyed shape).
TOGGLE_CLASS = "jobs-search-create-alert__artdeco-toggle"
WORD = "Set alert"

#: The toggle container; the switch inside it (THE PRESS TARGET on the classic
#: arm); every switch on the page; the toggle's own word.
TOGGLE = f"div.{TOGGLE_CLASS}"
SWITCH = f"{TOGGLE} input[role='switch']"
SWITCHES_ON_PAGE = "input[role='switch']"
TOGGLE_WORD = f"{TOGGLE} > span.artdeco-toggle__text"

#: The states. ``alert_off`` is measured on both arms; ``alert_on`` is DERIVED.
ALERT_OFF: str = "alert_off"
ALERT_ON: str = "alert_on"
UNKNOWN: str = "unknown"

#: ``aria-checked``'s two values, closed, and the state each names (the
#: classic arm's; the AI switch draws none).
ARIA_STATES: dict[str, str] = {"false": ALERT_OFF, "true": ALERT_ON}

#: The longest keywords and location this composes. LinkedIn's own search box
#: is the bound a person types into; these are generous above it and keep a
#: grant's target from being a document.
MAX_KEYWORDS = 200
MAX_LOCATION = 100

#: Why a place is refused, before any load (lane jobs7).
PLACE_UNMEASURED = (
    "a place is not taken yet: the alert is set on LinkedIn's AI job search, "
    "which addresses a place by geoId and distance, and what it does with a "
    "text location is unmeasured (capture C-SRCH-2), so an alert for these "
    "keywords in that place could silently be set on the keywords alone. "
    "Call again with keywords only."
)


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
    ``(None, why)``. PURE. ``keywords`` alone, urlencoded -- one spelling, so a
    grant's target is one string. A ``location`` is checked as before and then
    REFUSED (:data:`PLACE_UNMEASURED`): the AI route's place is unmeasured."""
    words, why = _clean(keywords, name="keywords", limit=MAX_KEYWORDS, required=True)
    if words is None:
        return (None, why)
    place, why = _clean(location, name="location", limit=MAX_LOCATION, required=False)
    if place is None:
        return (None, why)
    if place:
        return (None, PLACE_UNMEASURED)
    return (urlencode([("keywords", words)]), "")


def canonical(target: Any) -> tuple[Optional[str], str]:
    """``(query, why)``: ``target`` back in the one spelling :func:`query_for`
    writes, or ``(None, why)``. A target is accepted only if it IS that
    spelling: exactly ``keywords``, once, re-composing to itself. A target
    carrying a ``location`` is refused as :func:`query_for` refuses one."""
    raw = str(target if target is not None else "").strip()
    try:
        pairs = parse_qsl(raw, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        return (None, "the search is not a query string of keywords.")
    keys = [key for key, _value in pairs]
    if keys not in (["keywords"], ["keywords", "location"]):
        return (None, "the search must carry keywords and nothing else.")
    values = dict(pairs)
    query, why = query_for(values.get("keywords"), values.get("location", ""))
    if query is None:
        return (None, why)
    if query != raw:
        return (None, "the search is not in its one canonical spelling: compose it "
                      "from keywords, never by hand.")
    return (query, "")


def describe(target: str) -> dict[str, str]:
    """The caller's own values, for the block he confirms."""
    values = dict(parse_qsl(str(target or ""), keep_blank_values=True))
    return {"keywords": values.get("keywords", ""), "location": values.get("location", "")}


def landed_on_search(landed: Any, target: str) -> bool:
    """Whether the browser is on the job search this target names. PURE.

    The host must be LinkedIn's and the path the AI search's or, should
    LinkedIn serve it again, the classic search's (:data:`SEARCH_PATHS`);
    ``keywords`` must read the caller's value once, and ``location`` too when
    a target carries one. LinkedIn's own additions to the query (a geo id, an
    origin) do not re-address the search, so they are not compared."""
    try:
        parts = urlsplit(str(landed or ""))
    except ValueError:
        return False
    if parts.scheme != "https" or parts.netloc != "www.linkedin.com":
        return False
    if parts.path.rstrip("/") + "/" not in SEARCH_PATHS:
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

    Both arms' counts are taken; the state is read only on the ONE arm the
    page draws. Never raises; ``error`` is an exception TYPE name, never its
    message."""
    out: dict[str, Any] = {
        "arm": None,
        "toggles": 0,
        "switches_in_toggle": 0,
        "switches_on_page": 0,
        "word": None,
        "ai_toggles": 0,
        "ai_switches": 0,
        "captions": 0,
        "captions_near_switch": 0,
        "aria_checked": None,
        "checked": None,
        "error": None,
    }
    try:
        out["switches_on_page"] = coerce.as_count(await page.locator(SWITCHES_ON_PAGE).count())
        out["toggles"] = coerce.as_count(await page.locator(TOGGLE).count())
        out["switches_in_toggle"] = coerce.as_count(await page.locator(SWITCH).count())
        out["ai_toggles"] = coerce.as_count(await page.locator(AI_TOGGLE).count())
        out["ai_switches"] = coerce.as_count(await page.locator(AI_SWITCH).count())
        if out["toggles"] == 1 and out["switches_in_toggle"] == 1 and not out["ai_toggles"]:
            out["arm"] = CLASSIC_ARM
            words = page.locator(TOGGLE_WORD)
            if coerce.as_count(await words.count()) == 1:
                word = " ".join(str(await words.first.inner_text()).split())
                # A CLOSED WORD OR NOTHING: anything else is recorded as its
                # absence, never as text.
                out["word"] = word if word == WORD else "other"
            switch = page.locator(SWITCH).first
        elif out["ai_toggles"] and out["ai_switches"] == 1 and not out["toggles"]:
            out["arm"] = AI_ARM
            out["captions"] = coerce.as_count(await page.locator(CAPTION_ELEMENT).count())
            switch = page.locator(AI_SWITCH).first
            out["captions_near_switch"] = coerce.as_count(
                await switch.locator(CAPTION_NEAR_SWITCH).count()
            )
        else:
            return out
        aria = await switch.get_attribute("aria-checked")
        out["aria_checked"] = aria if aria in ARIA_STATES else ("other" if aria else None)
        out["checked"] = bool(await switch.is_checked())
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def _ai_verdict(facts: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    """The AI arm's verdict, off counts already coerced. PURE."""
    if facts["ai_switches"] != 1:
        return (facts, UNKNOWN, f"the AI search's alert toggle draws {facts['ai_switches']} "
                "input switch(es), where exactly one is required.")
    if facts["switches_on_page"] != 1:
        return (facts, UNKNOWN, f"{facts['switches_on_page']} input switches on the page; "
                "a second one makes the aim ambiguous.")
    if facts["captions"] != 1 or facts["captions_near_switch"] != 1:
        return (facts, UNKNOWN, "the switch is not captioned with its measured words exactly "
                "once, beside it, so it is not taken to be the alert switch.")
    if facts["aria_checked"] is not None:
        return (facts, UNKNOWN, "the AI search's switch draws an aria-checked, which no capture "
                "of it has drawn: its shape changed, so its state is not read off the page.")
    if facts["checked"] is False:
        return (facts, ALERT_OFF, "exactly one job-alert switch on LinkedIn's AI job search, "
                "captioned 'Get job alerts for this search', its checked property false and no "
                "aria-checked drawn -- the shape MEASURED on live sessions 11 and 12.")
    if facts["checked"] is True:
        return (facts, ALERT_ON, "exactly one job-alert switch on LinkedIn's AI job search, "
                "captioned 'Get job alerts for this search', its checked property true. The ON "
                "shape is DERIVED: no capture holds this switch on.")
    return (facts, UNKNOWN, "the AI search's switch's checked property was not read.")


def switch_verdict(reading: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    """``(facts, state, why)`` for the search's alert switch. PURE.

    On the AI arm (:func:`_ai_verdict`): ``alert_off`` is the MEASURED shape,
    ``alert_on`` the property true -- DERIVED. On the classic arm:

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
        "arm": reading.get("arm") if reading.get("arm") in (AI_ARM, CLASSIC_ARM) else None,
        "toggles": coerce.as_count(reading.get("toggles")),
        "switches_in_toggle": coerce.as_count(reading.get("switches_in_toggle")),
        "switches_on_page": coerce.as_count(reading.get("switches_on_page")),
        "word": reading.get("word"),
        "ai_toggles": coerce.as_count(reading.get("ai_toggles")),
        "ai_switches": coerce.as_count(reading.get("ai_switches")),
        "captions": coerce.as_count(reading.get("captions")),
        "captions_near_switch": coerce.as_count(reading.get("captions_near_switch")),
        "aria_checked": reading.get("aria_checked"),
        "checked": reading.get("checked"),
    }
    if reading.get("error"):
        return (facts, UNKNOWN, "the alert switch could not be read "
                f"({str(reading.get('error'))[:64]}); refused rather than guessed.")
    if facts["toggles"] and facts["ai_toggles"]:
        return (facts, UNKNOWN, "the page draws both the classic alert toggle and the AI "
                "search's, so which switch is his alert for this search is ambiguous.")
    if facts["ai_toggles"]:
        return _ai_verdict(facts)
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


def switch_for(facts: dict[str, Any]) -> str:
    """The press target for the arm a verdict was read on: a CONSTANT selector."""
    return AI_SWITCH if (facts or {}).get("arm") == AI_ARM else SWITCH


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
