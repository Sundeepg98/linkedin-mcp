"""Does LinkedIn HONOUR the job-search url filter parameters that
``linkedin_search_jobs`` is about to gain, or does it DISCARD them in silence?

THEIR SPELLINGS ARE BELIEVED, NOT MEASURED, and this repository does not ship
believed values. Five parameters are about to be appended to
``https://www.linkedin.com/jobs/search/`` by a shipped read tool::

    f_AL=true      Easy Apply only
    f_JT=F         job type, F = full-time
    f_EA=true      under ten applicants
    f_JIYN=true    in your network
    f_FCE=true     fair chance employer

**A PARAMETER LINKEDIN DOES NOT KNOW IS NOT AN ERROR.** It is dropped without
a word: the page still renders, the pills still draw, the cards still come
back. So a tool that appends a misspelled one reports a filter the member
never got, and nothing anywhere says otherwise. The question here is therefore
not "does the address load" -- every address below is already allowed by
``readonly._ALLOWED_URL_PATTERNS``, and all thirteen were confirmed ALLOWED
against ``readonly.is_read_url`` before this file was written -- but "does the
page COME BACK DIFFERENT".

THIS FILE RUNS TWO SEPARATE PASSES, in one browser session, with
``asyncio.sleep`` between every pair of loads in both.

=============================================================================
PASS ONE -- the five candidates, seven loads
=============================================================================

    1    BASELINE            ?keywords=<K> and nothing else
    2    NEGATIVE CONTROL    ?keywords=<K>&f_ZZQQX=true
    3-7  the five candidates, one per load

**THE NEGATIVE CONTROL IS THE CALIBRATION, NOT DECORATION.** ``f_ZZQQX`` is a
parameter LinkedIn has never had, so whatever it does to the page is exactly
what BEING IGNORED looks like on this surface. If it comes back identical to
BASELINE, then "identical to BASELINE" is a reading that MEANS ignored, and a
candidate that also comes back identical is ignored too. If it comes back
DIFFERENT, the page varies between loads on its own -- LinkedIn re-ranks, the
rendered card set moves -- and pass one cannot discriminate anything.

**THAT IS A FINDING, NOT A FAILURE, AND PASS ONE STOPS THERE.** It does not go
on to take five more readings and present them as evidence; it reports WHICH
channel disagreed and by how much. PASS TWO STILL RUNS -- it is a separate
instrument with its own controls and does not inherit pass one's verdict.

=============================================================================
PASS TWO -- settling ``f_JT`` on its own, six loads
=============================================================================

WHY A SECOND PASS EXISTS. Pass one's first live run returned, for ``f_JT=F``,
a zero on both channels it consults (card delta 0, differing pills 0) while
two channels it does NOT consult said the page had changed: the parameter
SURVIVED into the landed url where the negative control's was STRIPPED, and
the page carried 76 buttons against 71 for both baseline and the negative
control. A verdict of IGNORED on a silent channel is not a measurement, it is
an instrument reporting its own blind spot.

THE HYPOTHESIS UNDER TEST, and it is here to be REFUTED rather than confirmed:
the four boolean filters each render their own named checkbox, which is why
the pill channel sees them; job type renders as a DROPDOWN whose control name
stays "Job type" whatever value is chosen, so the pill channel is
STRUCTURALLY BLIND to it rather than reporting a true negative.

    1  BASELINE            ?keywords=<K>
    2  NEGATIVE CONTROL    ?keywords=<K>&f_ZZQQX=true   RE-TAKEN, not reused
    3  f_JT=F              full-time
    4  f_JT=C              contract
    5  f_JT=F,C            two values comma-joined
    6  f_JT=ZZ             A VALUE-LEVEL NEGATIVE CONTROL

**LOAD 6 IS THE ONE THAT DECIDES.** The survival channel that pass one turned
up is only worth promoting if it is measuring the PARAMETER. If ``f_JT=ZZ`` --
a value the job-type filter has never had -- is kept and looks identical to
``f_JT=F``, then LinkedIn keeps any ``f_``-prefixed pair whatever it says, the
channel is measuring the PREFIX, and it proves nothing about ``f_JT``. If
``f_JT=ZZ`` behaves differently from ``f_JT=F`` in some channel while the name
survives, ``f_JT`` is honoured. Anything else is CANNOT TELL, said plainly
rather than split down the middle.

ONE FIXED KEYWORD for all thirteen loads, never varied, because a changed
keyword changes the result set for reasons that have nothing to do with a
filter.

## What is measured, per load

* **CARD COUNT.** ``dom.harvest_linked_cards`` with ``dom.JOB_HREF``, the
  shipped harvest with the shipped pattern. THE COUNT ONLY.
* **PILL STATE.** Every ``<button>`` on the page, read through
  ``page.locator`` and ``get_attribute``, reported as an accessible name
  beside its ``aria-pressed`` / ``aria-checked`` / ``aria-expanded``.
* **PARAMETER SURVIVAL** into the landed url, verbatim, value included.
* **THE LANDED QUERY**, rendered through :func:`_redact` -- see below.
* **PASS TWO ALSO:** every control whose name contains "job type",
  "full-time", "contract" or "employment", case-insensitively, together with
  the inventory of names that were SEARCHED, so a zero says what it looked at.
* **PASS TWO BASELINE ALSO:** the ``dom.JOB_HREF`` diagnosis -- that pattern
  printed beside the count of anchors whose href contains ``/jobs/view/`` --
  because pass one's card channel returned exactly 7 on all seven loads
  including baseline, which is an inert channel and worth one line of
  diagnosis. Taken on a page that is being loaded anyway.

## Bounds

**EVERY ADDRESS IS A MODULE-LEVEL CONSTANT.** The thirteen urls are literals
in :data:`LOADS` and :data:`PASS2_LOADS`; nothing is built from a landed url
or from anything the page said. ``tests/test_navigation_is_never_derived.py``
scans this file like any other, and a probe that measured url parameters by
deriving a url from the page would be the joke version of itself.

**THE LANDED QUERY IS PRINTED THROUGH A SANITISER, AND THE NAME IS THE
CONTRACT.** That same test guards a second sink -- ``print`` -- because a
landed url reached a transcript three separate ways on 2026-09-03, and it
stops descending only at a call to a function named in its ``_SANITISERS``
set. :func:`_redact` below carries that name deliberately and implements the
contract the name asserts. **NOTHING OUTSIDE THIS FILE VERIFIES IT.** That is
the exact defect ``_SANITISERS``' own comment records -- an entry admitted on
the strength of a name, while the function had no slug rule at all -- so the
implementation here is built the one way that does not depend on being
audited: **AN ALLOWLIST, NOT A BLOCKLIST.** A query pair prints its value
verbatim only if its KEY is in :data:`QUERY_KEYS_PRINTABLE`, a module-level
literal set; every other key prints its name and a character count and never
its value. A blocklist fails open on the identifier nobody thought of --
``currentJobId``, ``geoId``, a tracking token -- and an allowlist fails
closed. Every emitted value additionally passes through
``shape.census_shape``.

**IT IS THIRTEEN GETS AND NOTHING ELSE.** No click, no fill, no scroll, no
``set_input_files``, and ``asyncio.sleep`` between every pair of loads. One
``BROWSER.session()`` for all thirteen.

**NO NEW ``page.evaluate``.** The button walk is ``page.locator("button")``
plus ``get_attribute`` / ``inner_text``. ``dom.read_surface_census`` was read
first and REJECTED for this question on two measured grounds: it does not read
``aria-pressed`` at all (grep ``aria-pressed`` across ``linkedin_server/`` and
every hit is a comment -- no reader consults it), and it puts every accessible
name through ``shape.census_shape`` INSIDE itself, so a filter pill would come
back as a shape rather than as the LinkedIn furniture the answer needs to
name. No other reader in ``dom.py`` returns names beside aria state.

**REDACTION, AND IT IS NOT THE ONE THE QUESTION ASSUMED.** Job cards carry
EMPLOYER names and JOB TITLES -- third parties -- so no card text, no title,
no company and no job id is printed. Counts only. Filter pill names ARE
printed verbatim, because they are LinkedIn's own furniture. But **the two
sets share one enumeration**: a job card's own controls are ``<button>``
elements on the same page, and LinkedIn writes titles and employers into their
accessible names. Three gates separate them, in this order:

    1. ARIA-STATE GATE. A button enters the printed inventory only if it
       carries at least one of the three aria attributes. One that carries
       none is COUNTED and never named. This costs the question nothing --
       aria state is the thing being measured -- and it is the structural
       proxy for "this control is filter chrome".
    2. ``shape.census_shape``, so a urn, a member path, a company path, a
       possessive or a long digit run cannot survive inside a printed name.
    3. LENGTH. Names of 60 characters or more are dropped, which is also
       ``shape.CENSUS_NAME_LIMIT``.

**THE NEEDLE SEARCH IN PASS TWO IS THE ONE PLACE THAT LOOKS OUTSIDE GATE 1**,
because a job-type control that carries no aria state is precisely the thing
the hypothesis predicts, and a search that could not see it would confirm the
hypothesis by construction. It gets its own gate instead: a needle match
prints only if it CARRIES AN ARIA STATE or is under
:data:`NEEDLE_NAME_LIMIT` characters. "Job type", "Full-time" and "Contract"
are all short; "Save <a title> at <an employer>" is not, and is withheld with
a count. Gates 2 and 3 still apply on top.

**THE RESIDUAL, NAMED RATHER THAN IMPLIED:** a card control that carries an
aria state AND a job title in its accessible name would be printed. Gate 1 is
a proxy, not a proof. Every gate reports how many names it dropped, so the
size of what is not being shown is on the page rather than assumed.

Run:  venv/Scripts/python.exe scripts/_probe_job_search_filter_params.py
Writes: ``_audit/_scratch/_probe-jobsearch-params.txt`` (that directory is
unconditionally gitignored) and the same text to stdout.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: THE ONE KEYWORD, FIXED FOR ALL THIRTEEN LOADS. Printed in the report so the
#: reader can see it never varied; the urls below carry it percent-encoded.
KEYWORD_TEXT = "node.js developer"

#: **PASS ONE'S SEVEN ADDRESSES, AS MODULE-LEVEL LITERALS.** Written out in
#: full, one per row, rather than assembled -- there is nothing here for a
#: landed url to reach into, which is the property
#: ``tests/test_navigation_is_never_derived`` exists to enforce and the
#: property this probe's own subject matter makes most tempting to break.
#:
#: Each row is ``(label, parameter, url)``. The parameter is ALSO the needle
#: used to ask whether LinkedIn kept the pair in the address it finished on,
#: so it is a literal here and not a slice of anything.
LOADS: tuple[tuple[str, str, str], ...] = (
    (
        "BASELINE",
        "",
        "https://www.linkedin.com/jobs/search/?keywords=node.js%20developer",
    ),
    (
        "NEGATIVE CONTROL",
        "f_ZZQQX=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_ZZQQX=true",
    ),
    (
        "Easy Apply only",
        "f_AL=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_AL=true",
    ),
    (
        "job type full-time",
        "f_JT=F",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=F",
    ),
    (
        "under ten applicants",
        "f_EA=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_EA=true",
    ),
    (
        "in your network",
        "f_JIYN=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JIYN=true",
    ),
    (
        "fair chance employer",
        "f_FCE=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_FCE=true",
    ),
)

#: **PASS TWO'S SIX ADDRESSES.** Same rule, same literal form. Rows 1 and 2
#: are RE-TAKEN rather than carried over from pass one: a baseline measured
#: minutes and six loads earlier is a reading with a timestamp, and the whole
#: point of a control is that it was taken beside the thing it controls.
PASS2_LOADS: tuple[tuple[str, str, str], ...] = (
    (
        "BASELINE",
        "",
        "https://www.linkedin.com/jobs/search/?keywords=node.js%20developer",
    ),
    (
        "NEGATIVE CONTROL",
        "f_ZZQQX=true",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_ZZQQX=true",
    ),
    (
        "f_JT full-time",
        "f_JT=F",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=F",
    ),
    (
        "f_JT contract",
        "f_JT=C",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=C",
    ),
    (
        "f_JT two values",
        "f_JT=F,C",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=F,C",
    ),
    (
        "f_JT VALUE CONTROL",
        "f_JT=ZZ",
        "https://www.linkedin.com/jobs/search/"
        "?keywords=node.js%20developer&f_JT=ZZ",
    ),
)

#: Index of the two loads every pass rests on.
BASELINE_INDEX = 0
NEGATIVE_INDEX = 1

#: The three attributes a filter pill can carry its state in. A button wearing
#: none of them is counted and never named -- gate 1 in the docstring.
ARIA_STATE_ATTRS: tuple[str, ...] = ("aria-pressed", "aria-checked", "aria-expanded")

#: Ceiling on buttons walked per load, so a page that draws hundreds cannot
#: turn one read into thousands of round trips. Reported as truncated rather
#: than silently cut, the way ``dom.CENSUS_MAX_CONTROLS`` is.
MAX_BUTTONS = 400

#: Gate 3. Same number as ``shape.CENSUS_NAME_LIMIT``, and deliberately so.
NAME_LIMIT = 60

#: The needle gate for pass two's job-type search -- the one search that looks
#: outside the aria-state gate, and so the one that needs a length rule of its
#: own. A match longer than this prints only if it carries an aria state.
NEEDLE_NAME_LIMIT = 30

#: WHAT PASS TWO HUNTS FOR, lowercased and matched as substrings. "employment"
#: is here because LinkedIn labels this filter "Job type" on some surfaces and
#: "Employment type" on others, and a search that knew only one spelling would
#: report a confident zero.
JT_NEEDLES: tuple[str, ...] = ("job type", "full-time", "contract", "employment")

#: Between every pair of loads. Not a settle wait -- ``BROWSER.goto`` already
#: does that and enforces its own navigation interval on top.
SLEEP_BETWEEN_LOADS_S = 3

#: Substrings that mean the browser was bounced off the surface entirely.
WALL_MARKERS: tuple[str, ...] = ("/login", "/checkpoint", "/authwall", "/uas/login")

#: The path every one of the thirteen addresses asks for.
JOBS_SEARCH_PATH = "/jobs/search"

#: **THE ALLOWLIST :func:`_redact` RENDERS A LANDED QUERY THROUGH.** A pair
#: whose key is here prints its value verbatim; every other pair prints its
#: key and a character count and NEVER its value.
#:
#: THE DIRECTION MATTERS AND IS THE WHOLE ARGUMENT. A blocklist of known-bad
#: keys fails OPEN on the identifier nobody thought of, and a jobs-search url
#: grows them without warning -- ``currentJobId`` is a job id, ``geoId`` is a
#: location id, and LinkedIn appends tracking pairs at will. An allowlist fails
#: CLOSED: an unforeseen key cannot print its value, because printing requires
#: membership rather than absence.
#:
#: Every key here is either one this repository put in the url itself or a
#: LinkedIn search-shape parameter that carries no identity. ``keywords`` is
#: here because it is the constant this probe supplies and holds nothing else.
QUERY_KEYS_PRINTABLE: frozenset[str] = frozenset(
    {
        "keywords",
        "f_AL",
        "f_JT",
        "f_EA",
        "f_JIYN",
        "f_FCE",
        "f_ZZQQX",
        "f_E",
        "f_TPR",
        "f_WT",
        "f_SB2",
        "sortBy",
        "origin",
        "refresh",
        "position",
        "pageNum",
        "start",
        "distance",
    }
)

#: The anchor shape the ``dom.JOB_HREF`` diagnosis counts.
JOB_VIEW_ANCHOR = 'a[href*="/jobs/view/"]'

#: Where the findings land. The directory is gitignored unconditionally
#: (``.gitignore``: ``_audit/_scratch/``), which is why a live reading may be
#: written there at all.
OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "_audit"
    / "_scratch"
    / "_probe-jobsearch-params.txt"
)

#: How many differing pill names one table cell will name before it stops.
MAX_NAMED_IN_CELL = 6


def _redact(url: str) -> str:
    """The LANDED QUERY, rendered so it can identify nobody. AN ALLOWLIST.

    **THIS FUNCTION'S NAME IS A CONTRACT, NOT A LABEL.**
    ``tests/test_navigation_is_never_derived.py`` stops its taint walk at a
    call to a function named ``_redact`` or ``_shape_of``, matched by NAME
    across every module it scans. So naming a function this makes a promise to
    every other check in this package -- "the result carries none of its
    input" -- and that file's own comment records what happens when the
    promise is made on the strength of a name: an entry sat in ``_SANITISERS``
    while the function it vouched for had no slug rule at all.

    NOTHING OUTSIDE THIS FILE VERIFIES THIS ONE. It is therefore built the one
    way that does not need an auditor: **membership, not absence.** A pair
    prints its value only if its key is in :data:`QUERY_KEYS_PRINTABLE`. A key
    nobody anticipated -- a job id, a geo id, a tracking blob -- cannot print
    its value by being unrecognised, which is exactly how a blocklist leaks.

    Returns the QUERY ONLY. No scheme, no host, no path: the path is reported
    separately as a relation, and it is the one part of a LinkedIn url that
    can be a member path.
    """
    query = urlsplit(str(url or "")).query
    if not query:
        return "(no query)"
    rendered: list[str] = []
    for pair in query.split("&"):
        if not pair:
            continue
        key, sep, value = pair.partition("=")
        if not sep:
            key, value = pair, ""
        if key in QUERY_KEYS_PRINTABLE:
            # Shaped even so. The allowlist says the KEY is safe to read a
            # value out of; the shaper is the second layer, and two layers is
            # what this package does with a string it is about to publish.
            rendered.append("%s=%s" % (key, shape.census_shape(value)))
        else:
            rendered.append(
                "%s=<withheld %d chars>"
                % (shape.census_shape(key) or "<key>", len(value))
            )
    return "&".join(rendered)


def _state_text(values: list) -> str:
    """One button's aria state, as a fixed-width reading.

    ``-`` means the attribute is ABSENT, which is a different fact from an
    attribute present and reading ``false``. Collapsing them would delete the
    vocabulary this whole probe needs: a pill that GAINS ``aria-pressed`` when
    a parameter is honoured is exactly an absent-to-present transition.
    """
    parts = []
    for attribute, value in zip(ARIA_STATE_ATTRS, values):
        short = attribute.replace("aria-", "")
        parts.append("%s=%s" % (short, "-" if value is None else str(value)))
    return " ".join(parts)


async def _read_buttons(page) -> dict:
    """Names and aria state for every ``<button>``, plus the needle search.

    Returns the name-to-state mapping (gate 1: aria-carrying only), the
    job-type needle hits (which deliberately look OUTSIDE gate 1, under a
    length gate of their own), and the counts that say how much of the page is
    NOT being shown.

    THOSE COUNTS ARE NOT BOOKKEEPING. A mapping of six pills means one thing
    if four hundred buttons were skipped and another if two were, and a reader
    who cannot tell which is looking at a number with no denominator.
    """
    result = {
        "total": 0,
        "walked": 0,
        "truncated": False,
        "no_aria_state": 0,
        "nameless": 0,
        "too_long": 0,
        "unread": 0,
        "named": 0,
        "states": {},
        "needle_hits": [],
        "needle_withheld": 0,
        "failed": "",
    }
    buttons = page.locator("button")
    try:
        result["total"] = int(await buttons.count())
    except Exception as exc:
        result["failed"] = type(exc).__name__
        return result

    limit = min(result["total"], MAX_BUTTONS)
    result["truncated"] = result["total"] > MAX_BUTTONS
    states: dict[str, set] = {}
    hits: dict[str, set] = {}
    for index in range(limit):
        control = buttons.nth(index)
        try:
            values = []
            for attribute in ARIA_STATE_ATTRS:
                values.append(await control.get_attribute(attribute))
            raw = await control.get_attribute("aria-label")
            if not raw:
                raw = await control.inner_text()
        except Exception:
            result["unread"] += 1
            continue
        result["walked"] += 1
        has_state = not all(one is None for one in values)
        name = " ".join(str(raw or "").split())
        if not name:
            result["nameless"] += 1
            if not has_state:
                result["no_aria_state"] += 1
            continue
        if len(name) >= NAME_LIMIT:
            result["too_long"] += 1
            continue
        # GATE 2. The repository's own shaper, so a urn, a member path, a
        # company path or a long digit run cannot ride through inside a name
        # that passed the gates above.
        safe = shape.census_shape(name)
        if not safe:
            result["nameless"] += 1
            continue
        result["named"] += 1
        state = _state_text(values)

        # THE NEEDLE SEARCH LOOKS OUTSIDE GATE 1 DELIBERATELY. A job-type
        # control carrying no aria state is exactly what the hypothesis
        # predicts, so a search confined to aria-carrying controls would
        # confirm that hypothesis by construction rather than test it.
        lowered = safe.lower()
        if any(needle in lowered for needle in JT_NEEDLES):
            if has_state or len(safe) < NEEDLE_NAME_LIMIT:
                hits.setdefault(safe, set()).add(state)
            else:
                result["needle_withheld"] += 1

        if not has_state:
            result["no_aria_state"] += 1
            continue
        states.setdefault(safe, set()).add(state)

    result["states"] = {key: frozenset(value) for key, value in states.items()}
    result["needle_hits"] = sorted(
        (key, sorted(value)) for key, value in hits.items()
    )
    return result


def _differing_names(baseline: dict, other: dict) -> list[str]:
    """Names whose aria state is not the same in the two loads.

    A name PRESENT in one and ABSENT in the other counts as differing, which
    is the case a set-of-pairs difference would report twice and a
    key-intersection would miss entirely: a pill that changes its accessible
    name when a filter applies leaves one key and arrives as another.
    """
    left = baseline.get("states") or {}
    right = other.get("states") or {}
    names = set(left) | set(right)
    return sorted(name for name in names if left.get(name) != right.get(name))


def _cell(names: list[str]) -> str:
    """The differing-pill column, bounded so one row cannot become a page."""
    if not names:
        return "(none)"
    shown = names[:MAX_NAMED_IN_CELL]
    text = "; ".join(shown)
    if len(names) > len(shown):
        text += "; ... (%d more)" % (len(names) - len(shown))
    return text


def _verdict(row: dict, negative_matches: bool) -> str:
    """The PASS ONE reading for one candidate.

    **THIS RULE CONSULTS TWO CHANNELS AND THE RUN PRODUCES FOUR.** It is left
    deliberately narrow rather than widened in place, because widening it on
    the strength of one surprising run is how an instrument gets tuned until
    it agrees with whoever is holding it. Pass two is the widening, done as a
    separate measurement with its own controls -- so a zero here now says
    "silent on these two channels" instead of claiming IGNORED.
    """
    if not negative_matches:
        return "CANNOT TELL (negative control disagreed with baseline)"
    if row.get("failed"):
        return "CANNOT TELL (the load did not complete)"
    if row["cards_delta"] != 0 or row["differing"]:
        return "HONOURED (on the two channels this rule reads)"
    return "NO CHANGE on the two channels this rule reads -- see pass two"


async def _one_load(page, emit, label, parameter, url, index) -> dict:
    """Load one address and take every reading. Shared by both passes."""
    row = {
        "label": label,
        "parameter": parameter or "(none)",
        "cards": -1,
        "cards_delta": 0,
        "buttons_delta": 0,
        "differing": [],
        "survived": None,
        "failed": "",
        "buttons": None,
        "walled": False,
    }
    emit("--- LOAD %d  %s  [%s]" % (index + 1, label, row["parameter"]))
    try:
        landed_url = await BROWSER.goto(page, url)
    except Exception as exc:
        row["failed"] = type(exc).__name__
        emit("    NAVIGATION FAILED: %s" % type(exc).__name__)
        emit("    (the message is withheld -- BrowserUnavailableError")
        emit("     interpolates the url it could not reach)")
        return row

    # EVERY READING OFF THE LANDED ADDRESS IS EITHER A COMPARISON AGAINST A
    # CONSTANT THIS REPOSITORY AUTHORED, OR A CALL TO _redact. A boolean about
    # a url, or an allowlisted rendering of its query -- never the url.
    served_exactly = landed_url == url
    walled = any(marker in landed_url for marker in WALL_MARKERS)
    on_surface = JOBS_SEARCH_PATH in landed_url
    survived = bool(parameter) and (parameter in landed_url)
    landed_query = _redact(landed_url)

    row["walled"] = walled
    if parameter:
        row["survived"] = survived

    emit("    landed at the exact address asked for: %s"
         % ("YES" if served_exactly else "NO"))
    emit("    still on %s: %s" % (JOBS_SEARCH_PATH, "YES" if on_surface else "NO"))
    emit("    auth wall: %s" % ("YES" if walled else "no"))
    if parameter:
        emit("    %r survived into the landed url verbatim: %s"
             % (parameter, "YES" if survived else "NO"))
    emit("    landed query: %s" % landed_query)

    if walled:
        row["failed"] = "auth wall"
        emit("    AUTH WALL. Not signed in, so nothing was measured here.")
        return row

    try:
        records = await dom.harvest_linked_cards(
            page,
            href_pattern=dom.JOB_HREF,
            max_items=100,
            max_chars=200,
        )
        row["cards"] = len(records)
    except Exception as exc:
        row["failed"] = type(exc).__name__
        emit("    HARVEST FAILED: %s (message withheld -- it can carry a url)"
             % type(exc).__name__)

    buttons = await _read_buttons(page)
    row["buttons"] = buttons

    emit("    job cards harvested: %s"
         % ("n/a" if row["cards"] < 0 else row["cards"]))
    emit("    buttons on the page: %d (walked %d%s)"
         % (buttons["total"], buttons["walked"],
            ", TRUNCATED" if buttons["truncated"] else ""))
    emit("    of those, carrying an aria state and named: %d"
         % len(buttons["states"]))
    emit("    dropped: %d carried no aria state, %d nameless, "
         "%d name >= %d chars, %d unreadable"
         % (buttons["no_aria_state"], buttons["nameless"],
            buttons["too_long"], NAME_LIMIT, buttons["unread"]))
    if buttons["failed"]:
        emit("    BUTTON WALK FAILED: %s" % buttons["failed"])
    return row


def _compare_to_baseline(rows: list[dict], row: dict, emit) -> None:
    """Fill in the deltas against this pass's own baseline, and print them."""
    base = rows[BASELINE_INDEX]
    if base["cards"] >= 0 and row["cards"] >= 0:
        row["cards_delta"] = row["cards"] - base["cards"]
    if base["buttons"] and row["buttons"]:
        row["buttons_delta"] = row["buttons"]["total"] - base["buttons"]["total"]
    row["differing"] = _differing_names(base["buttons"] or {}, row["buttons"] or {})
    emit("    card delta vs BASELINE: %+d" % row["cards_delta"])
    emit("    button delta vs BASELINE: %+d" % row["buttons_delta"])
    emit("    pills whose aria state differs from BASELINE: %d"
         % len(row["differing"]))
    for name in row["differing"][:MAX_NAMED_IN_CELL]:
        left = sorted((base["buttons"] or {}).get("states", {}).get(name, ()))
        right = sorted((row["buttons"] or {}).get("states", {}).get(name, ()))
        emit("        %-40s baseline=%s  here=%s"
             % (name, left or "ABSENT", right or "ABSENT"))


async def _pass_one(page, emit, first_overall) -> tuple:
    emit()
    emit("=============================================================")
    emit("=== PASS ONE -- THE FIVE CANDIDATES, SEVEN LOADS")
    emit("=============================================================")
    rows: list[dict] = []
    stopped = ""
    negative_matches = False

    for index, (label, parameter, url) in enumerate(LOADS):
        if index or not first_overall:
            await asyncio.sleep(SLEEP_BETWEEN_LOADS_S)
        row = await _one_load(page, emit, label, parameter, url, index)
        rows.append(row)

        if row["walled"]:
            stopped = "an auth wall interrupted pass one"
            break
        if row["failed"] and index == BASELINE_INDEX:
            stopped = "pass one's baseline load failed"
            break
        if index == BASELINE_INDEX:
            emit("    (this is the baseline every later load is read against)")
            continue

        _compare_to_baseline(rows, row, emit)

        if index == NEGATIVE_INDEX:
            same_cards = row["cards_delta"] == 0 and row["cards"] >= 0
            same_pills = not row["differing"]
            negative_matches = same_cards and same_pills
            emit()
            emit("=== PASS ONE NEGATIVE CONTROL'S VERDICT")
            emit("    card count identical to baseline: %s"
                 % ("YES" if same_cards else "NO"))
            emit("    pill states identical to baseline: %s"
                 % ("YES" if same_pills else "NO"))
            if negative_matches:
                emit("    THE INSTRUMENT DISCRIMINATES. A parameter LinkedIn")
                emit("    has never had changed nothing, so 'identical to")
                emit("    baseline' now MEANS ignored.")
            else:
                emit("    PASS ONE CANNOT DISCRIMINATE. A parameter LinkedIn")
                emit("    has never had came back DIFFERENT from baseline, so")
                emit("    the page varies between loads on its own. STOPPING")
                emit("    pass one rather than calling five more readings")
                emit("    evidence. PASS TWO STILL RUNS -- separate controls.")
                stopped = "pass one's negative control disagreed with baseline"
                break
            emit()

    return rows, negative_matches, stopped


async def _pass_two(page, emit) -> tuple:
    emit()
    emit("=============================================================")
    emit("=== PASS TWO -- SETTLING f_JT ON ITS OWN, SIX LOADS")
    emit("=============================================================")
    rows: list[dict] = []
    stopped = ""
    diagnosis: list[str] = []

    for index, (label, parameter, url) in enumerate(PASS2_LOADS):
        await asyncio.sleep(SLEEP_BETWEEN_LOADS_S)
        row = await _one_load(page, emit, label, parameter, url, index)
        rows.append(row)

        buttons = row["buttons"] or {}
        hits = buttons.get("needle_hits") or []
        emit("    controls whose name contains %s: %d"
             % (", ".join(repr(one) for one in JT_NEEDLES), len(hits)))
        for name, state_list in hits:
            emit("        MATCH  %-38s %s" % (name, state_list))
        if buttons.get("needle_withheld"):
            emit("        (%d further match(es) withheld: no aria state and a"
                 % buttons["needle_withheld"])
            emit("         name of %d+ chars, so possibly card text)"
                 % NEEDLE_NAME_LIMIT)
        emit("    THE SEARCHED INVENTORY (every aria-carrying named control):")
        inventory = sorted(buttons.get("states") or {})
        if inventory:
            for name in inventory:
                emit("        %-40s %s" % (name, sorted(buttons["states"][name])))
        else:
            emit("        (empty -- so a zero above says nothing was searched)")

        if row["walled"]:
            stopped = "an auth wall interrupted pass two"
            break

        if index == BASELINE_INDEX:
            # THE JOB_HREF DIAGNOSIS. One extra measurement on a page that is
            # being loaded anyway, because pass one's card channel returned 7
            # on every one of seven loads and an inert channel deserves a
            # cause rather than a shrug.
            emit()
            emit("=== dom.JOB_HREF DIAGNOSIS (pass two baseline page)")
            emit("    dom.JOB_HREF = %s" % dom.JOB_HREF)
            try:
                anchors = int(await page.locator(JOB_VIEW_ANCHOR).count())
            except Exception as exc:
                anchors = -1
                emit("    anchor count FAILED: %s" % type(exc).__name__)
            try:
                all_anchors = int(await page.locator("a[href]").count())
            except Exception:
                all_anchors = -1
            emit("    anchors matching %s: %d" % (JOB_VIEW_ANCHOR, anchors))
            emit("    anchors with any href on the page: %d" % all_anchors)
            emit("    harvest_linked_cards returned: %d" % row["cards"])
            if anchors >= 0 and row["cards"] >= 0:
                if anchors == row["cards"]:
                    diagnosis.append(
                        "THE PAGE DRAWS ONLY %d /jobs/view/ ANCHORS. The "
                        "harvest is not finding the wrong set -- it is finding "
                        "all there are, so the results list is not in the DOM "
                        "this read sees (virtualised, or behind a scroll this "
                        "probe does not perform)." % anchors)
                else:
                    diagnosis.append(
                        "THE HARVEST IS FINDING THE WRONG SET. %d anchors on "
                        "the page match /jobs/view/ but harvest_linked_cards "
                        "returned %d, so dom.JOB_HREF or the card walk is "
                        "dropping %d of them."
                        % (anchors, row["cards"], anchors - row["cards"]))
            emit("    %s" % (diagnosis[0] if diagnosis else "inconclusive"))
            emit()
            emit("    (this is pass two's own baseline, re-taken)")
            continue

        _compare_to_baseline(rows, row, emit)

    return rows, stopped, diagnosis


def _jt_reading(rows: list[dict]) -> list[str]:
    """THE f_JT VERDICT, in the vocabulary that was asked for and no other.

    The decision rests on ONE comparison, and it is not ``f_JT=F`` against
    baseline. It is ``f_JT=ZZ`` -- a value the filter has never had -- against
    ``f_JT=F``. Survival alone cannot separate "LinkedIn understood f_JT" from
    "LinkedIn keeps anything spelled f_something", and only a value-level
    control can.
    """
    out: list[str] = []
    by_parameter = {row["parameter"]: row for row in rows}
    full = by_parameter.get("f_JT=F")
    control = by_parameter.get("f_JT=ZZ")
    if not full or not control:
        return ["CANNOT TELL -- f_JT=F and/or f_JT=ZZ were never loaded."]
    if full.get("failed") or control.get("failed"):
        return ["CANNOT TELL -- one of the two decisive loads did not complete."]

    kept_full = bool(full.get("survived"))
    kept_control = bool(control.get("survived"))
    same_cards = full["cards_delta"] == control["cards_delta"]
    same_buttons = full["buttons_delta"] == control["buttons_delta"]
    same_pills = sorted(full["differing"]) == sorted(control["differing"])
    identical = same_cards and same_buttons and same_pills

    out.append("f_JT=F  survived verbatim: %s" % ("YES" if kept_full else "NO"))
    out.append("f_JT=ZZ survived verbatim: %s" % ("YES" if kept_control else "NO"))
    out.append("f_JT=ZZ vs f_JT=F -- cards same: %s, buttons same: %s, "
               "pills same: %s" % (same_cards, same_buttons, same_pills))

    if kept_full and not identical:
        out.append("VERDICT: HONOURED. The name survives AND the value-level")
        out.append("control behaves differently from a real value, so the")
        out.append("survival channel is reading the PARAMETER, not the prefix.")
    elif kept_control and identical:
        out.append("VERDICT: DISBELIEVED. f_JT=ZZ is kept and looks identical")
        out.append("to f_JT=F, so LinkedIn keeps any f_-prefixed pair and the")
        out.append("survival channel is measuring the PREFIX. It proves")
        out.append("nothing about f_JT.")
    else:
        out.append("VERDICT: CANNOT TELL. Neither pattern was produced --")
        out.append("see the three readings above for which half is missing.")
    return out


async def main() -> None:
    lines: list[str] = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit("=== DOES LINKEDIN HONOUR THE JOB-SEARCH FILTER PARAMETERS?")
    emit("    two passes, one session, one fixed keyword, nothing pressed")
    emit("    keyword (fixed for all thirteen loads): %r" % KEYWORD_TEXT)
    emit("    card COUNTS only -- no title, no employer, no job id is printed")
    emit("    the landed query is rendered through an ALLOWLIST (_redact)")

    p1_rows: list[dict] = []
    p2_rows: list[dict] = []
    p1_negative = False
    p1_stopped = ""
    p2_stopped = ""
    diagnosis: list[str] = []

    try:
        await BROWSER.start()
    except Exception as exc:
        # The local profile lock and the launch failures both land here. The
        # message names a directory on this box, never a LinkedIn identity, so
        # it is printed -- a lock report that will not say what is locked is
        # the report nobody can act on.
        emit("    COULD NOT START THE BROWSER: %s: %s"
             % (type(exc).__name__, str(exc)[:300]))
        emit("    THAT IS THE RESULT. Nothing was measured. If this is the")
        emit("    cross-process profile lock, another process holds the")
        emit("    profile -- this probe does not retry and kills nothing.")
        _write(lines)
        return

    try:
        async with BROWSER.session() as page:
            p1_rows, p1_negative, p1_stopped = await _pass_one(page, emit, True)
            p2_rows, p2_stopped, diagnosis = await _pass_two(page, emit)
    except Exception as exc:
        emit("    THE RUN RAISED: %s (message withheld)" % type(exc).__name__)
        p2_stopped = p2_stopped or "the session raised %s" % type(exc).__name__
    finally:
        await BROWSER.stop()

    emit()
    emit("=== PASS ONE TABLE")
    emit("    %-22s %-14s %6s %7s  %s"
         % ("LOAD", "PARAMETER", "CARDS", "DELTA", "PILLS DIFFERING FROM BASELINE"))
    for index, row in enumerate(p1_rows):
        cards = (row["failed"] if (row["failed"] and row["cards"] < 0)
                 else str(row["cards"]))
        delta = "n/a" if index == BASELINE_INDEX else "%+d" % row["cards_delta"]
        emit("    %-22s %-14s %6s %7s  %s"
             % (row["label"][:22], row["parameter"][:14], cards, delta,
                "(baseline)" if index == BASELINE_INDEX else _cell(row["differing"])))
    if len(p1_rows) < len(LOADS):
        emit("    %d load(s) NOT TAKEN -- %s"
             % (len(LOADS) - len(p1_rows), p1_stopped or "stopped"))

    emit()
    emit("=== PASS ONE READING, ONE LINE PER CANDIDATE")
    for index, row in enumerate(p1_rows):
        if index in (BASELINE_INDEX, NEGATIVE_INDEX):
            continue
        emit("    %-22s %-14s %s"
             % (row["label"][:22], row["parameter"][:14],
                _verdict(row, p1_negative)))

    emit()
    emit("=== PASS TWO TABLE")
    emit("    %-22s %-12s %8s %8s %8s %6s  %s"
         % ("LOAD", "PARAMETER", "SURVIVED", "BUTTONS", "B-DELTA", "CARDS",
            "JT-MATCHED CONTROLS"))
    for index, row in enumerate(p2_rows):
        buttons = row["buttons"] or {}
        survived = ("n/a" if row["survived"] is None
                    else ("YES" if row["survived"] else "NO"))
        hits = buttons.get("needle_hits") or []
        emit("    %-22s %-12s %8s %8s %8s %6s  %s"
             % (row["label"][:22], row["parameter"][:12], survived,
                buttons.get("total", "n/a"),
                "n/a" if index == BASELINE_INDEX else "%+d" % row["buttons_delta"],
                row["cards"] if row["cards"] >= 0 else "n/a",
                "; ".join(name for name, _s in hits) or "(none)"))
    if len(p2_rows) < len(PASS2_LOADS):
        emit("    %d load(s) NOT TAKEN -- %s"
             % (len(PASS2_LOADS) - len(p2_rows), p2_stopped or "stopped"))

    emit()
    emit("=== f_JT READING")
    for text in _jt_reading(p2_rows):
        emit("    %s" % text)

    emit()
    emit("=== dom.JOB_HREF DIAGNOSIS")
    emit("    %s" % (diagnosis[0] if diagnosis else "not taken"))

    _write(lines)


def _write(lines: list[str]) -> None:
    """Put the report on disk, in the one directory that is always ignored."""
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="ascii")
    print("\n    findings written to %s" % OUT_PATH)


# GUARDED: importing a script must not DO anything.
# tests/test_scripts_are_import_safe.py asserts this for every file in scripts/.
if __name__ == "__main__":
    asyncio.run(main())
