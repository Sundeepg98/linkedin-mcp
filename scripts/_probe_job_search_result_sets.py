"""Do the job-search filter parameters change WHAT COMES BACK, or only what
the page draws?

**THIS IS THE CHANNEL THE PRIOR PASS COULD NOT RUN, AND IT IS THE ONLY ONE
THAT DECIDES A SHORTLIST.** ``scripts/_probe_job_search_filter_params.py``
established, with a negative control and then a value-level control, that
LinkedIn RECOGNISES ``f_AL``, ``f_EA``, ``f_JIYN``, ``f_FCE`` and ``f_JT``:
it draws a checked pill for each, and it strips an invented ``f_ZZQQX`` out of
the address it lands on while keeping these. Both readings are sound.

Neither is a reading about what ``linkedin_search_jobs`` RETURNS. That tool
returns a harvest of the rendered cards, and the prior probe recorded its own
blindness in ``server.py``'s ``_JOB_TYPE`` docstring: the harvest gave 7 on all
six loads including baseline, so "the channel that would separate them --
comparing the RESULT SETS -- is unavailable".

**A COUNT THAT DOES NOT MOVE IS NOT A RESULT SET THAT DOES NOT MOVE.** Seven
before and seven after is equally consistent with a filter working perfectly on
a page holding seven matches and with a reader returning the same seven rows
whatever it was asked. Those are opposite conclusions and the count cannot
separate them. This file compares the SETS.

=============================================================================
THE THREE CONTROLS, AND THE PROBE IS WORTHLESS WITHOUT THEM
=============================================================================

A result-set channel that reports "identical to baseline" is unreadable on its
own: it means the filter is inert, or it means the reader is blind. Three loads
exist to tell those apart, and each answers a different way of being wrong.

1. **POSITIVE CONTROL -- a keyword from another profession entirely, same
   location.** Its set MUST differ from baseline. If it does not, this
   instrument cannot see a change of any size and NO verdict about any filter
   may be drawn from this run. That is the finding, and it is a finding about
   the reader.

2. **NEGATIVE CONTROL -- baseline plus a parameter LinkedIn has never had.**
   Its set should MATCH baseline. It calibrates what being ignored looks like
   on this channel, and it is the same ``f_ZZQQX`` the prior probe measured
   LinkedIn stripping, so the two runs are comparable.

3. **STABILITY CONTROL -- baseline again, last, after every other load.**
   LinkedIn ranks; ranking drifts; a set difference between two loads seconds
   apart may be nothing but that drift. Without this, every difference below
   would be evidence and some of it would be noise. **This is the control that
   sets the threshold**, and it is taken LAST so that it spans the whole
   session rather than a friendly two-second window.

The negative and the stability control ask nearly the same question from
opposite directions, and both are kept: the first says an unknown parameter
changes nothing, the second says nothing changes on its own.

=============================================================================
THE SECOND MEASUREMENT, TAKEN ON PAGES BEING LOADED ANYWAY
=============================================================================

``server._read_cards`` navigates and harvests with NO readiness wait::

    final_url = await BROWSER.goto(page, url)
    assert_not_authwall(final_url, surface=surface)
    records = await dom.harvest_linked_cards(...)

Its sibling ``_read_tracker`` does the opposite and says why in a comment:
``dom.wait_for_tracker_list`` runs FIRST, because waiting after the harvest
"changes nothing about what was read". Job search gets ``browser.goto``'s
settle and nothing else, and the prior probe saw a page carrying **25 anchors
of any kind**, which is not a rendered LinkedIn page.

So every load here is read TWICE -- once the instant ``goto`` returns, which is
exactly where the shipped tool reads, and once after a further flat wait. No
extra navigation, no scroll, no press. If the second reading is larger, the
shipped reader is reading too early and every filter verdict above it is a
verdict about a page that had not finished arriving.

=============================================================================
WHAT IS PRINTED, AND WHAT CANNOT BE
=============================================================================

Set SIZES and OVERLAPS. Never an id, never a title, never an employer, never a
url. A job id in a search result is not an identity and this file could print
one; it prints none, because the question is entirely answered by
``|A|``, ``|B|``, ``|A and B|``, ``|A minus B|`` and ``|B minus A|``, and a
reading that needs no identifier should carry none.

Everything taken off the landed address is a COMPARISON AGAINST A LITERAL THIS
FILE AUTHORED, which yields a boolean whatever it compared. No sanitiser is
defined here and none is needed: nothing derived from a navigation is ever
interpolated. ``tests/test_navigation_is_never_derived.py`` is the check.

Run::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        ./venv/Scripts/python.exe scripts/_probe_job_search_result_sets.py

Writes ``_audit/_scratch/_probe-jobsearch-result-sets.txt`` (that directory is
unconditionally gitignored) and the same text to stdout.
"""
from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote_plus, urlencode, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: The query this whole run is about: the stack he is actually hunting.
KEYWORD_TEXT = "node.js developer"

#: **THE CITIES ARE NOT WRITTEN INTO THIS FILE, AND THE SHIPPED IDENTITY SWEEP
#: IS WHY.** `scripts/sweep_tracked_for_identity.py` refused an earlier draft
#: of these probes -- three hits across three files, class
#: `operator_own_denied_terms`. It matches a gitignored wordlist of values
#: known to be HIS, so that is a real string in a tracked file and not the
#: usual undeclared-versus-real ambiguity: the city he lives in identifies him
#: whether or not it looks like an identifier.
#:
#: **THE REMEDY IS NOT A DECLARATION.** Every declaration permanently widens
#: what the guard tolerates; this widens nothing. The city comes from the
#: environment, the default is a whole country and identifies nobody, and NOT
#: ONE question this file asks is about which city it is -- pass one holds the
#: location fixed across every load, and pass two only needs two places that
#: differ from each other::
#:
#:     LINKEDIN_PROBE_CITY_A=<city> LINKEDIN_PROBE_CITY_B=<other city>
#:     LINKEDIN_CDP_ATTACH=1 ./venv/Scripts/python.exe scripts/<probe>.py
CITY_A = os.environ.get("LINKEDIN_PROBE_CITY_A", "India")
CITY_B = os.environ.get("LINKEDIN_PROBE_CITY_B", "Singapore")

#: The positive control's keyword. Chosen to share NO vocabulary with the
#: baseline: if a set difference cannot be produced by swapping software
#: engineering for clinical nursing in the same city, nothing smaller will
#: produce one either.
POSITIVE_CONTROL_TEXT = "cardiac nurse"

#: Flat wait between the early reading and the late one, ON TOP of the settle
#: ``browser.goto`` already spends (``config.SETTLE_MS`` is 3500, and on
#: /jobs/search the networkidle branch resolved early in 0 of 10 recorded
#: loads, so the flat branch always runs and the page has already had ~7s).
LATE_READ_WAIT_MS = 6_000

#: Between every pair of loads, on top of the browser's own rate slot.
SLEEP_BETWEEN_LOADS_S = 3

#: Substrings that mean the browser was bounced off the surface entirely.
WALL_MARKERS: tuple[str, ...] = ("/login", "/checkpoint", "/authwall", "/uas/login")

#: The path every address below asks for.
JOBS_SEARCH_PATH = "/jobs/search"

#: The anchor shape the render diagnosis counts.
JOB_VIEW_ANCHOR = 'a[href*="/jobs/view/"]'

#: How many cards a harvest may return. Deliberately far above a page's worth,
#: so a ceiling can never be mistaken for a filter.
HARVEST_MAX = 100

#: **THE SMALLEST MINORITY SHARE THIS INSTRUMENT WILL CALL A RESULT.** One
#: posting inside a seven-posting window is not evidence that a second filter
#: value applied: at that size "it applied" and "its postings rank below the
#: window" are indistinguishable. Set from a measurement, not from taste --
#: two runs of pass three returned the identical ``from_c == 1`` and disagreed
#: on the verdict because the drift floor moved by two. See _job_type_lines.
MIN_RESOLVABLE_SHARE = 1

#: **THE ADDRESSES, AS MODULE-LEVEL LITERALS, ONE PER ROW.** Written out in
#: full rather than assembled: there is nothing here for a landed url to reach
#: into, which is the property ``tests/test_navigation_is_never_derived``
#: enforces and the one this subject matter makes most tempting to break.
#:
#: Each row is ``(label, parameter, url)``. The parameter is ALSO the needle
#: asked about the landed address, so it is a literal here and not a slice.
BASELINE_INDEX = 0
POSITIVE_INDEX = 1
NEGATIVE_INDEX = 2


def _search_url(keywords: str = "", location: str = "", **extra) -> str:
    """One jobs-search address, built from this file and the environment.

    **NOT ASSEMBLED FROM A LANDED URL.** That is the property
    ``tests/test_navigation_is_never_derived.py`` enforces, and the property
    this subject matter makes most tempting to break. An environment variable
    and a constant defined here are neither a page nor a navigation, so
    building from them keeps the rule while keeping the city out of the file.

    The earlier draft wrote every address out as a full literal, for exactly
    that rule. It satisfied the navigation guard and failed the identity
    sweep, because a literal address had to contain the city. **The two guards
    wanted opposite things and only one of them was being listened to** --
    this helper is what satisfies both.
    """
    query = {"keywords": keywords or KEYWORD_TEXT, "location": location or CITY_A}
    query.update(extra)
    return "https://www.linkedin.com/jobs/search/?" + urlencode(query)


FILTER_LOADS: tuple[tuple[str, str, str], ...] = (
    ("BASELINE", "", _search_url()),
    ("POSITIVE CONTROL", "", _search_url(keywords=POSITIVE_CONTROL_TEXT)),
    ("NEGATIVE CONTROL", "f_ZZQQX=true", _search_url(f_ZZQQX="true")),
    ("EASY APPLY", "f_AL=true", _search_url(f_AL="true")),
    ("UNDER TEN APPLICANTS", "f_EA=true", _search_url(f_EA="true")),
    ("IN YOUR NETWORK", "f_JIYN=true", _search_url(f_JIYN="true")),
    ("FAIR CHANCE", "f_FCE=true", _search_url(f_FCE="true")),
    ("JOB TYPE full-time", "f_JT=F", _search_url(f_JT="F")),
    ("STABILITY CONTROL", "", _search_url()),
)

#: **PASS TWO -- `J 151`, several locations at once, WHICH IS NOT SHIPPED AND
#: WHOSE SPELLING HAS NEVER BEEN MEASURED.** The tool's own docstring says so
#: and says why: a guessed encoding does not fail loudly, it silently searches
#: somewhere else.
#:
#: Two candidate spellings, each with its own single-location control, because
#: "the multi url returned rows" is worth nothing without knowing what each
#: place returns alone. The comparison that decides it is the multi set against
#: what each single one distinctively holds -- a spelling that works draws from
#: both, a spelling that is ignored draws from one.
#:
#: The repeated-key form cannot go through ``_search_url``: a dict cannot hold
#: one key twice, and that is the point of the row. It is appended by hand from
#: the same two constants, so the city still never appears here.
LOCATION_LOADS: tuple[tuple[str, str, str], ...] = (
    ("LOC A alone", "location=" + CITY_A, _search_url(location=CITY_A)),
    ("LOC B alone", "location=" + CITY_B, _search_url(location=CITY_B)),
    (
        "LOC A,B comma-joined",
        "location=" + CITY_A + ", " + CITY_B,
        _search_url(location=CITY_A + ", " + CITY_B),
    ),
    (
        "LOC A and B repeated key",
        "location=" + CITY_A,
        _search_url(location=CITY_A) + "&" + urlencode({"location": CITY_B}),
    ),
)

#: **PASS THREE -- THE ONE QUESTION THE PRIOR PASS NAMED AND COULD NOT ANSWER.**
#: ``server._JOB_TYPE``'s docstring closes on it, in its own words:
#:
#:     ONE THING IS STILL OPEN AND IT IS THE MULTI-VALUE FORM. ``f_JT=F,C``
#:     reached the page with its comma percent-encoded ... and the channel
#:     that would separate them -- comparing the RESULT SETS -- is unavailable
#:
#: It is available now, and this is the comparison it names. The single values
#: are re-taken in this pass rather than reused from pass one, so all four sets
#: come from one stretch of one session, and the single-F load is taken AGAIN
#: last as this pass's own drift control.
#:
#: **WHAT DECIDES IT.** If both values apply, the pair's set draws from
#: postings that ``f_JT=F`` alone and ``f_JT=C`` alone each return and the
#: other does not. If only one applies, the pair's set is that one's. The pill
#: channel could not tell those apart, which is why the question was left open
#: rather than guessed.
JOB_TYPE_LOADS: tuple[tuple[str, str, str], ...] = (
    ("JT single F", "f_JT=F", _search_url(f_JT="F")),
    ("JT single C", "f_JT=C", _search_url(f_JT="C")),
    ("JT pair F,C", "f_JT=F,C", _search_url(f_JT="F,C")),
    ("JT single F, RE-TAKEN", "f_JT=F", _search_url(f_JT="F")),
)

OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "_audit"
    / "_scratch"
    / "_probe-jobsearch-result-sets.txt"
)


def _ids_from_records(records: list) -> set:
    """The SET of job ids a harvest found, off the shipped pattern.

    ``dom.JOB_HREF`` is the pattern the shipped tool harvests on, so this set
    is the identity of what ``linkedin_search_jobs`` would have returned --
    not a second opinion about it.

    A CARD IS NOT A ROW AND THAT IS THE POINT OF SEPARATING THEM. This counts
    the ids the walk reached; ``shape.parse_job_card`` then refuses some of
    them, and the gap between the two numbers is how many postings the tool
    saw and did not report.
    """
    found = set()
    for record in records or []:
        match = re.search(dom.JOB_HREF, str(record.get("href") or ""))
        if match:
            found.add(match.group(1))
    return found


def _set_relation(baseline: set, other: set) -> dict:
    """Two sets, as five integers. No member of either is returned."""
    return {
        "left": len(baseline),
        "right": len(other),
        "both": len(baseline & other),
        "only_left": len(baseline - other),
        "only_right": len(other - baseline),
    }


def _relation_text(reading: dict) -> str:
    return (
        "baseline %d, this %d, shared %d, baseline-only %d, this-only %d"
        % (reading["left"], reading["right"], reading["both"],
           reading["only_left"], reading["only_right"])
    )


def _differs(reading: dict) -> bool:
    return bool(reading["only_left"] or reading["only_right"])


async def _count_anchors(page, selector: str) -> int:
    try:
        return int(await page.locator(selector).count())
    except Exception:
        return -1


async def _read_once(page) -> dict:
    """One harvest plus the two anchor counts. No navigation, no press."""
    reading = {"cards": -1, "ids": set(), "rows": -1, "dropped": -1,
               "job_anchors": -1, "all_anchors": -1, "failed": ""}
    try:
        records = await dom.harvest_linked_cards(
            page,
            href_pattern=dom.JOB_HREF,
            max_items=HARVEST_MAX,
            max_chars=200,
        )
        reading["cards"] = len(records)
        reading["ids"] = _ids_from_records(records)
        rows, dropped = dom.parse_all(records, shape.parse_job_card)
        reading["rows"] = len(rows)
        reading["dropped"] = int(dropped or 0)
    except Exception as exc:
        reading["failed"] = type(exc).__name__
    reading["job_anchors"] = await _count_anchors(page, JOB_VIEW_ANCHOR)
    reading["all_anchors"] = await _count_anchors(page, "a[href]")
    return reading


async def _one_load(page, emit, label, parameter, url, index) -> dict:
    """Load one address, read it early, wait, read it again."""
    row = {
        "label": label,
        "parameter": parameter or "(none)",
        "early": None,
        "late": None,
        "key_kept": None,
        "walled": False,
        "failed": "",
        "served_exactly": None,
        "on_surface": None,
    }
    emit("--- LOAD %d  %s  [%s]" % (index + 1, label, row["parameter"]))
    try:
        landed_url = await BROWSER.goto(page, url)
    except Exception as exc:
        row["failed"] = type(exc).__name__
        emit("    NAVIGATION FAILED: %s" % type(exc).__name__)
        emit("    (message withheld -- BrowserUnavailableError interpolates")
        emit("     the url it could not reach)")
        return row

    # EVERY READING OFF THE LANDED ADDRESS IS A COMPARISON AGAINST A LITERAL
    # THIS FILE AUTHORED. A comparison yields a boolean whatever it compared,
    # which is the shape the taint engine in
    # tests/test_navigation_is_never_derived.py exempts by design -- and the
    # booleans are the whole of what this file wants from that address.
    row["served_exactly"] = landed_url == url
    row["walled"] = any(marker in landed_url for marker in WALL_MARKERS)
    row["on_surface"] = JOBS_SEARCH_PATH in landed_url
    if parameter:
        # KEY KEPT, DECODED ON BOTH SIDES. The raw substring test reported
        # `f_JT=F,C` as dropped for one reason only: LinkedIn returns the
        # comma as %2C. Only the boolean leaves this scope.
        row["key_kept"] = parameter in unquote_plus(urlsplit(landed_url).query)

    emit("    landed at the exact address asked for: %s"
         % ("YES" if row["served_exactly"] else "NO"))
    emit("    still on %s: %s" % (JOBS_SEARCH_PATH, "YES" if row["on_surface"] else "NO"))
    emit("    auth wall: %s" % ("YES" if row["walled"] else "no"))
    if parameter:
        emit("    LinkedIn KEPT the pair this file asked for: %s"
             % ("YES" if row["key_kept"] else "NO -- STRIPPED"))
        emit("      (KEPT means RECOGNISED, never HONOURED -- the prior probe")
        emit("       measured f_JT=ZZ, a value the filter has never had, kept")
        emit("       verbatim and inert on every other channel)")

    if row["walled"]:
        row["failed"] = "auth wall"
        emit("    AUTH WALL. Not signed in, so nothing was measured here.")
        return row

    row["early"] = await _read_once(page)
    emit("    EARLY reading -- taken where server._read_cards reads:")
    emit("        cards %d, ids %d, rows %d, dropped %d, /jobs/view/ anchors "
         "%d, anchors of any kind %d"
         % (row["early"]["cards"], len(row["early"]["ids"]),
            row["early"]["rows"], row["early"]["dropped"],
            row["early"]["job_anchors"], row["early"]["all_anchors"]))
    if row["early"]["failed"]:
        emit("        HARVEST FAILED: %s (message withheld -- it can carry a url)"
             % row["early"]["failed"])

    await asyncio.sleep(LATE_READ_WAIT_MS / 1000)
    row["late"] = await _read_once(page)
    emit("    LATE reading -- same page, %d ms later, nothing pressed:"
         % LATE_READ_WAIT_MS)
    emit("        cards %d, ids %d, rows %d, dropped %d, /jobs/view/ anchors "
         "%d, anchors of any kind %d"
         % (row["late"]["cards"], len(row["late"]["ids"]),
            row["late"]["rows"], row["late"]["dropped"],
            row["late"]["job_anchors"], row["late"]["all_anchors"]))

    gained = len(row["late"]["ids"] - row["early"]["ids"])
    lost = len(row["early"]["ids"] - row["late"]["ids"])
    emit("        LATE minus EARLY: %d id(s) gained, %d lost" % (gained, lost))
    return row


def _compare(rows: list, row: dict, emit, baseline_index: int) -> None:
    """This load's late set against the baseline's late set."""
    if not rows or row.get("late") is None:
        return
    baseline = rows[baseline_index]
    if baseline.get("late") is None:
        return
    reading = _set_relation(baseline["late"]["ids"], row["late"]["ids"])
    row["vs_baseline"] = reading
    emit("    RESULT SET vs BASELINE (late readings): %s" % _relation_text(reading))
    emit("    DIFFERS FROM BASELINE: %s" % ("YES" if _differs(reading) else "NO"))


async def _run(page, emit, loads, baseline_index, first) -> list:
    rows: list = []
    for index, (label, parameter, url) in enumerate(loads):
        if not (first and index == 0):
            await asyncio.sleep(SLEEP_BETWEEN_LOADS_S)
        row = await _one_load(page, emit, label, parameter, url, index)
        rows.append(row)
        if index != baseline_index:
            _compare(rows, row, emit, baseline_index)
        emit()
        if row["walled"]:
            emit("    STOPPING: an auth wall ended this pass.")
            break
    return rows


def _verdict_lines(rows: list) -> list:
    """The verdict, and the ORDER OF THE QUESTIONS IS THE WHOLE DESIGN.

    The controls are read FIRST and they can void everything after them. A
    filter verdict is only printed once the instrument has been shown able to
    see a change at all.
    """
    out: list = []
    if len(rows) <= max(POSITIVE_INDEX, NEGATIVE_INDEX):
        return ["THE RUN DID NOT REACH ITS CONTROLS. No verdict."]

    positive = rows[POSITIVE_INDEX].get("vs_baseline")
    negative = rows[NEGATIVE_INDEX].get("vs_baseline")
    stability = rows[-1].get("vs_baseline") if rows[-1]["label"].startswith(
        "STABILITY") else None

    if not positive:
        return ["THE POSITIVE CONTROL DID NOT COMPLETE. No verdict."]

    out.append("POSITIVE CONTROL (another profession, same city): %s"
               % _relation_text(positive))
    if not _differs(positive):
        out.append("")
        out.append("    ***  THE INSTRUMENT IS BLIND. A different profession in")
        out.append("    ***  the same city returned THE SAME SET. Nothing below")
        out.append("    ***  this line is a reading about a filter; it is a")
        out.append("    ***  reading about the reader. NO FILTER VERDICT.")
        return out
    out.append("    the channel CAN see a change of query. Verdicts are readable.")
    out.append("")

    if negative is not None:
        out.append("NEGATIVE CONTROL (a parameter LinkedIn never had): %s"
                   % _relation_text(negative))
        out.append("    ignored looks like: %s"
                   % ("a set that MOVES -- so movement alone is not evidence"
                      if _differs(negative) else "a set that does NOT move"))
        out.append("")

    if stability is not None:
        out.append("STABILITY CONTROL (baseline again, last): %s"
                   % _relation_text(stability))
        out.append("    drift with NO change of query at all: %d id(s) differ"
                   % (stability["only_left"] + stability["only_right"]))
        out.append("    ANY difference at or below this size is INDISTINGUISHABLE")
        out.append("    FROM DRIFT and is reported as such, not as a filter.")
        out.append("")

    floor = 0
    if stability is not None:
        floor = stability["only_left"] + stability["only_right"]

    out.append("THE FIVE SHIPPED FILTERS, against the baseline's late set:")
    for row in rows:
        reading = row.get("vs_baseline")
        if reading is None or row["parameter"] in ("(none)", "f_ZZQQX=true"):
            continue
        moved = reading["only_left"] + reading["only_right"]
        if not _differs(reading):
            verdict = "CHANGED NOTHING"
        elif moved <= floor:
            verdict = "moved %d -- WITHIN DRIFT (%d), not evidence" % (moved, floor)
        else:
            verdict = "MOVED %d, above the %d-id drift floor" % (moved, floor)
        out.append("    %-22s %-14s %s"
                   % (row["label"], row["parameter"], verdict))
    out.append("")
    out.append("    AND ONE ROW IN THIS TABLE IS MEASURED AGAINST THE WRONG")
    out.append("    THING, WHICH IS A PROPERTY OF THE FILTER AND NOT A FAULT")
    out.append("    IN THE RUN. The four booleans are OFF by default, so")
    out.append("    baseline is genuinely their unfiltered case. f_JT is a")
    out.append("    dropdown whose default is ANY, and the baseline for a")
    out.append("    Node search in a tech city is already mostly full-time --")
    out.append("    so f_JT=F asks the corpus to narrow to what it already is.")
    out.append("    A small movement there is EXPECTED and says little either")
    out.append("    way. PASS THREE is f_JT's real measurement: F against C,")
    out.append("    two values of the same filter, where a filter that works")
    out.append("    must separate them.")
    return out


def _render_lines(rows: list) -> list:
    """Is the shipped reader reading too early? One number answers it."""
    out: list = []
    gains = []
    for row in rows:
        if row.get("early") is None or row.get("late") is None:
            continue
        gains.append((row["label"],
                      len(row["early"]["ids"]),
                      len(row["late"]["ids"]),
                      row["early"]["all_anchors"],
                      row["late"]["all_anchors"]))
    if not gains:
        return ["No load produced both readings. Nothing to say about timing."]

    out.append("    %-22s %6s %6s %9s %9s"
               % ("LOAD", "EARLY", "LATE", "ANCH-E", "ANCH-L"))
    for label, early, late, anchor_early, anchor_late in gains:
        out.append("    %-22s %6d %6d %9d %9d"
                   % (label, early, late, anchor_early, anchor_late))
    grew = sum(1 for _l, e, la, _ae, _al in gains if la > e)
    out.append("")
    out.append("    loads whose id set GREW between the two readings: %d of %d"
               % (grew, len(gains)))
    if grew:
        out.append("    ***  server._read_cards READS AT THE EARLY COLUMN. On %d"
                   % grew)
        out.append("    ***  of %d loads the page was still arriving, so the tool"
                   % len(gains))
        out.append("    ***  returns fewer postings than the search found.")
    else:
        out.append("    the page had finished arriving by the early reading on")
        out.append("    every load, so the missing readiness wait cost nothing")
        out.append("    HERE. It is still absent, and this run is one sample.")
    return out


def _job_type_lines(rows: list) -> list:
    """Does `f_JT=F,C` reach BOTH job types, or only one?

    THE DRIFT CONTROL IS READ FIRST AND IT SETS A THRESHOLD, NOT A GATE. The
    single-F load is re-taken last; whatever it moved is what movement means
    nothing. A pair-set differing from F's by less than that is not evidence.
    """
    out: list = []
    by_label = {row["label"]: row for row in rows}
    single_f = by_label.get("JT single F")
    single_c = by_label.get("JT single C")
    pair = by_label.get("JT pair F,C")
    retake = by_label.get("JT single F, RE-TAKEN")
    if not all(r is not None and r.get("late") is not None
               for r in (single_f, single_c, pair, retake)):
        return ["    a load did not complete. No verdict."]

    ids_f = single_f["late"]["ids"]
    ids_c = single_c["late"]["ids"]
    ids_pair = pair["late"]["ids"]
    floor = len(ids_f ^ retake["late"]["ids"])

    out.append("    DRIFT FLOOR: f_JT=F re-taken last differs from itself by "
               "%d id(s)." % floor)
    out.append("    F alone %d, C alone %d, shared %d"
               % (len(ids_f), len(ids_c), len(ids_f & ids_c)))
    only_f = ids_f - ids_c
    only_c = ids_c - ids_f
    if not only_f or not only_c:
        out.append("    ***  F AND C DO NOT SEPARATE on this query, so no pair")
        out.append("    ***  set can be told apart from either single. NO VERDICT.")
        return out

    from_f = len(ids_pair & only_f)
    from_c = len(ids_pair & only_c)
    out.append("    the pair F,C returned %d ids: %d of them are F-only "
               "postings, %d are C-only" % (len(ids_pair), from_f, from_c))
    out.append("    pair vs F alone: %d differ; pair vs C alone: %d differ"
               % (len(ids_pair ^ ids_f), len(ids_pair ^ ids_c)))

    #: **A RESOLUTION FLOOR AS WELL AS A DRIFT FLOOR, AND THE SECOND RUN IS
    #: WHY.** Two runs of this pass returned ``from_c == 1`` -- the identical
    #: number -- and the verdict FLIPPED between them, from "the pair's window
    #: is F's" to "both values apply", purely because the drift floor happened
    #: to be 2 in one run and 0 in the other. **A verdict that turns on which
    #: side of zero a single posting falls is not a verdict.**
    #:
    #: The repair is not a better floor. It is admitting that a window of
    #: seven cannot resolve a minority contribution of one: at that size the
    #: union hypothesis and the ranking hypothesis predict the same picture.
    #: So one posting is reported as UNRESOLVED however the drift lands, and
    #: the reproducibility of the 1 is reported as the finding it is.
    if from_f > floor and from_c > max(floor, MIN_RESOLVABLE_SHARE):
        out.append("    ***  BOTH VALUES APPLY. The pair reaches postings that")
        out.append("    ***  each single value returns and the other does not,")
        out.append("    ***  by more than the %d-id drift floor and by more than" % floor)
        out.append("    ***  the %d-posting resolution floor. Comma-joining is"
                   % MIN_RESOLVABLE_SHARE)
        out.append("    ***  HONOURED and the open question is closed YES.")
    elif from_f > floor and 0 < from_c <= MIN_RESOLVABLE_SHARE:
        out.append("    ***  UNRESOLVED, AND THAT IS THE HONEST ANSWER HERE.")
        out.append("    ***  The pair's window holds %d of the first value's" % from_f)
        out.append("    ***  distinctive postings and %d of the second's. One or"
                   % from_c)
        out.append("    ***  two postings out of seven cannot separate 'the")
        out.append("    ***  second value applies' from 'the second value's")
        out.append("    ***  postings rank below a seven-posting window' --")
        out.append("    ***  both hypotheses predict exactly this picture.")
        out.append("    ***  A WIDER WINDOW WOULD SETTLE IT AND NEEDS A SCROLL,")
        out.append("    ***  which is a boundary question and not this run's.")
        out.append("    ***  The prior reading -- 'a caller asking for two job")
        out.append("    ***  types has NOT been shown to get both' -- STANDS,")
        out.append("    ***  and now has a shape: at most %d of 7." % from_c)
    elif from_f > floor and from_c <= floor:
        out.append("    ***  THE PAIR'S WINDOW IS THE FIRST VALUE'S. %d of the"
                   % from_f)
        out.append("    ***  first value's distinctive postings are in it and %d"
                   % from_c)
        out.append("    ***  of the second's, on a floor of %d." % floor)
        out.append("        AND TWO MECHANISMS PRODUCE THAT, WHICH THIS RUN")
        out.append("        CANNOT SEPARATE -- SAY SO RATHER THAN PICK ONE:")
        out.append("        (a) LinkedIn drops the second value; or")
        out.append("        (b) LinkedIn returns the union and ranks the first")
        out.append("            value's postings above the seven-posting window,")
        out.append("            which a commoner job type would do on its own.")
        out.append("        Separating them needs a window wider than seven, and")
        out.append("        that needs a scroll, which is a boundary question.")
        out.append("    ***  WHAT IS TRUE UNDER BOTH: a caller asking for two job")
        out.append("    ***  types gets a window made of the first. The prior")
        out.append("    ***  reading -- 'has NOT been shown to get both' -- stands")
        out.append("    ***  and is now stronger, not overturned.")
    elif from_c > floor and from_f <= floor:
        out.append("    ***  THE PAIR'S WINDOW IS THE LAST VALUE'S. Same two")
        out.append("    ***  mechanisms as above, in the other order.")
    else:
        out.append("    ***  THE PAIR MATCHES NEITHER SINGLE'S DISTINCTIVE SET.")
        out.append("    ***  It is not the union and it is not either half --")
        out.append("    ***  which is a THIRD outcome nobody predicted, and it")
        out.append("    ***  is a reason to stop shipping the comma form.")
    return out


def _location_lines(rows: list) -> list:
    """`J 151`: does either candidate spelling reach BOTH cities?"""
    out: list = []
    by_label = {row["label"]: row for row in rows}
    alone_a = by_label.get("LOC A alone")
    alone_b = by_label.get("LOC B alone")
    if not (alone_a and alone_b) or alone_a.get("late") is None or alone_b.get(
            "late") is None:
        return ["    the two single-location loads did not both complete."]

    ids_a = alone_a["late"]["ids"]
    ids_b = alone_b["late"]["ids"]
    out.append("    city A alone: %d ids; city B alone: %d ids; shared %d"
               % (len(ids_a), len(ids_b), len(ids_a & ids_b)))
    if not (ids_a - ids_b) or not (ids_b - ids_a):
        out.append("    ***  THE TWO CITIES DO NOT SEPARATE on this query, so")
        out.append("    ***  no multi-location spelling can be told apart from")
        out.append("    ***  either single one. NO VERDICT on J 151 from this run.")
        return out

    for label in ("LOC A,B comma-joined", "LOC A and B repeated key"):
        row = by_label.get(label)
        if row is None or row.get("late") is None:
            out.append("    %-26s did not complete" % label)
            continue
        ids = row["late"]["ids"]
        from_a = len(ids & (ids_a - ids_b))
        from_b = len(ids & (ids_b - ids_a))
        out.append("    %-26s %d ids: %d only-A, %d only-B, kept=%s"
                   % (label, len(ids), from_a, from_b,
                      "YES" if row.get("key_kept") else "NO"))
        if from_a and from_b:
            out.append("        BOTH CITIES ARE REPRESENTED -- this spelling reaches")
            out.append("        postings neither single search alone returns.")
        elif from_a and not from_b:
            out.append("        ONLY CITY A. The second location was discarded.")
        elif from_b and not from_a:
            out.append("        ONLY CITY B. The first location was discarded.")
        else:
            out.append("        NEITHER city's distinctive postings. Inconclusive.")
    return out


async def main() -> None:
    lines: list = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit("=== DO THE JOB-SEARCH FILTERS CHANGE WHAT COMES BACK?")
    emit("    the RESULT-SET channel, which the pill channel is not")
    emit("    keyword (fixed): %r   location (fixed): %r"
         % (KEYWORD_TEXT, CITY_A))
    emit("    positive control keyword: %r" % POSITIVE_CONTROL_TEXT)
    emit("    SET SIZES AND OVERLAPS ONLY -- no id, title, employer or url")
    emit("    every load read TWICE: at the shipped reader's moment, and")
    emit("    %d ms later, with no navigation and nothing pressed" % LATE_READ_WAIT_MS)
    emit()

    filter_rows: list = []
    location_rows: list = []
    job_type_rows: list = []

    try:
        await BROWSER.start()
    except Exception as exc:
        emit("    COULD NOT START THE BROWSER: %s: %s"
             % (type(exc).__name__, str(exc)[:300]))
        emit("    THAT IS THE RESULT. Nothing was measured.")
        _write(lines)
        return

    # ONE PASS AT A TIME IS AVAILABLE, AND THE REASON IS RATE DISCIPLINE
    # RATHER THAN CONVENIENCE. Re-running seventeen loads to replicate four of
    # them spends thirteen page loads on his account for nothing, and a
    # correction to one pass's WORDING should not have to buy a whole run.
    wanted = {"one", "two", "three"}
    for name in ("one", "two", "three"):
        if "--only-pass-%s" % name in sys.argv:
            wanted = {name}
            break

    try:
        async with BROWSER.session() as page:
            first = True
            if "one" in wanted:
                emit("=== PASS ONE -- the five shipped filters and three controls")
                emit()
                filter_rows = await _run(
                    page, emit, FILTER_LOADS, BASELINE_INDEX, first
                )
                first = False
                emit()
            if "two" in wanted:
                emit("=== PASS TWO -- J 151, several locations at once")
                emit()
                location_rows = await _run(page, emit, LOCATION_LOADS, 0, first)
                first = False
                emit()
            if "three" in wanted:
                emit("=== PASS THREE -- f_JT=F,C, the question _JOB_TYPE left open")
                emit()
                job_type_rows = await _run(page, emit, JOB_TYPE_LOADS, 0, first)
    except Exception as exc:
        emit("    THE RUN RAISED: %s (message withheld)" % type(exc).__name__)
    finally:
        await BROWSER.stop()

    emit()
    emit("=== VERDICT")
    for text in _verdict_lines(filter_rows):
        emit(text)
    emit()
    emit("=== IS THE SHIPPED READER READING TOO EARLY?")
    for text in _render_lines(filter_rows + location_rows + job_type_rows):
        emit(text)
    emit()
    emit("=== J 151 -- SEVERAL LOCATIONS AT ONCE")
    for text in _location_lines(location_rows):
        emit(text)
    emit()
    emit("=== f_JT=F,C -- DOES THE SECOND VALUE APPLY?")
    for text in _job_type_lines(job_type_rows):
        emit(text)
    emit()
    emit("=== WHAT THIS RUN CANNOT SAY")
    emit("    Nothing about whether a filter is CORRECT -- only whether it")
    emit("    changes the set. A parameter could filter to the wrong thing and")
    emit("    read as MOVED here.")
    emit("    Nothing about a second page: start= is never sent.")
    emit("    One session, one keyword, one city, one afternoon.")
    _write(lines)


def _write(lines: list) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print("written to _audit/_scratch/%s" % OUT_PATH.name)


if __name__ == "__main__":
    asyncio.run(main())
