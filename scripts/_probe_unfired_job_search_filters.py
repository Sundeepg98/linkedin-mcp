"""FIRE the job-search filter rows the census carries as UNFIRED.

## THE ROWS, AND WHAT EACH ONE NEEDS BEFORE IT CAN BE BANKED

    J 2    boolean operators in the query (AND / OR / NOT / "phrase" / parens)
    J 4    Date posted            -> f_TPR, four values
    J 5    Workplace type         -> f_WT,  four values
    J 6    Experience level       -> f_E,   six values
    J 7    Sort by relevant/recent-> sortBy=DD
    J 10   Company filter         -> f_C
    J 151  MULTIPLE simultaneous locations, as a second-load fan-out

## THE DISCRIMINATION TEST, AND WHY A URL IS NOT EVIDENCE

Every one of these rows was banked UNFIRED on the strength of a CONSTANT: the
code holds `f_TPR` and four values, therefore the filter exists. That is a fact
about this repository and says nothing about LinkedIn.

**AND FIRING IT IS NOT ENOUGH EITHER.** A search that returns seven postings
proves the page loaded, not that the filter did anything: a parameter LinkedIn
ignores, or one this server appends to the wrong key, returns a perfectly
healthy result set that is simply the unfiltered one. That failure is silent,
it looks exactly like success, and it is the same disease as a check that
cannot fail.

**SO THE MEASURE IS DISCRIMINATION, NOT RESPONSE.** For each filter every
permitted value is fired against one fixed query, and the JOB ID SET that comes
back is recorded. The verdict is the number of DISTINCT id sets across the
values:

    DISCRIMINATES     two or more distinct id sets. The filter reaches
                      LinkedIn and changes what it serves. BANKABLE.
    NO-EFFECT         every value returned an identical id set. The filter is
                      either being dropped or has no effect on this query.
                      NOT BANKABLE, and it is a finding rather than a failure
                      to report.
    THIN              too few results came back to tell the two apart.

A NO-EFFECT verdict is NOT reported as a pass. That is the whole point of the
file.

## THE CONFOUND THIS PROBE DOES NOT PRETEND TO HAVE SOLVED

LinkedIn's result sets DRIFT between two identical requests seconds apart.
So a difference between two id sets is not proof by itself. The baseline query
is therefore fired TWICE, back to back, before any filter runs, and the
DRIFT FLOOR -- how much two identical requests already disagree -- is printed
beside every filter's result. A filter whose sets differ by less than the drift
floor has not been shown to do anything, and this file says so rather than
counting it.

## WHAT LEAVES THIS PROCESS

COUNTS, SET SIZES, OVERLAPS AND VERDICTS. No job title, no employer, no
location and no job id is printed. Job ids are compared inside the process and
never emitted; the raw sets go to `_state/`, which is gitignored.

The search terms are LITERALS IN THIS FILE and are deliberately generic, so
that nothing this probe searches for comes from the operator's own saved
searches -- one of his spellings is on this repository's denied-terms list.

## IT FIRES NO WRITE

It searches and it reads. Nothing is applied to, saved, followed or messaged.

Run it as::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_unfired_job_search_filters.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import dom, server  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

CONTROL_URL = "https://www.linkedin.com/jobs/search/?keywords=node.js"

#: The fixed query every filter is measured against. A literal, and generic.
BASE_KEYWORDS = "software engineer"

#: Two cities named as LITERALS here, for the multi-location fan-out only.
#:
#: **THEY ARE DELIBERATELY NOT HIS, AND THE FIRST VERSION OF THIS LINE WAS.**
#: It named the operator's own city and the identity gate REFUSED the commit on
#: an exact-value match against the de-anonymisation key. A probe testing a
#: fan-out MECHANISM needs two distinct places and nothing more, so the cities
#: it ships with must be ones that identify nobody -- his geography is one of
#: the things this repository is careful never to write down.
#:
#: Overridable, so a caller who wants their own places need not edit the file:
#:     LINKEDIN_PROBE_LOCATIONS="A;B"
LOCATIONS_TWO = os.environ.get(
    "LINKEDIN_PROBE_LOCATIONS", "Toronto;Berlin"
)

#: Boolean-operator queries for J 2. The point is not that each returns rows;
#: it is that the operators change WHICH rows, which is what proves they
#: reached LinkedIn rather than being swallowed.
BOOLEAN_QUERIES = (
    ("plain", "backend engineer"),
    ("OR", "backend OR frontend"),
    ("NOT", "backend NOT manager"),
    ("quoted phrase", '"backend engineer"'),
    ("parens + AND", '(backend AND engineer)'),
)


async def _badge(page) -> dict:
    try:
        reading = await dom.read_invitation_badge(page)
    except Exception as exc:  # noqa: BLE001
        return {"error": type(exc).__name__}
    return reading if isinstance(reading, dict) else {"error": "no reading"}


def _badge_state(reading: dict) -> str:
    if reading.get("error"):
        return "UNREADABLE (error)"
    if reading.get("badge_links") != 1:
        return "UNREADABLE (badge_links is not exactly 1)"
    if reading.get("label") is None:
        return "UNREADABLE (no label)"
    return "READABLE"


def _consumption(before: dict, after: dict) -> str:
    if _badge_state(before) != "READABLE" or _badge_state(after) != "READABLE":
        return ("UNKNOWN -- one end could not be read, so this says nothing "
                "rather than saying nothing was spent")
    if before.get("label") == after.get("label"):
        return "the badge did not move across this read"
    return "THE BADGE MOVED -- something was spent"


async def _control_serves(page) -> bool:
    await BROWSER.goto(page, CONTROL_URL)
    return await page.locator("div.job-card-container").count() > 0


async def _ids(**kwargs) -> frozenset:
    """Fire the SHIPPED search tool and return its job-id set.

    The ids are returned as a set for comparison and are never printed.

    A REFUSAL IS ANNOUNCED, NOT SILENTLY RETURNED AS AN EMPTY SET, and that is
    a repair of this probe's own first version. It returned `frozenset()` for
    every unhappy path alike, so a REFUSED CALL AND AN EMPTY RESULT SET WERE
    THE SAME VALUE. Measured here 2026-09-20: `sort_by="recent"` was fired at a
    tool whose permitted values are `relevance` and `date`, the tool correctly
    refused with `sort_by must be relevance or date`, and this function
    reported it as "rows=0" -- which read as LinkedIn serving nothing and was
    nearly written up as a defect in the server. The argument was wrong, the
    server was right, and the instrument could not say so.
    """
    try:
        result = await server.linkedin_search_jobs(**kwargs)
    except Exception as exc:  # noqa: BLE001
        print("        search RAISED " + type(exc).__name__)
        return frozenset()
    if isinstance(result, dict):
        # `ok: False`, an `error`, or a `message` without results is the tool
        # refusing the ARGUMENT. That is this probe's mistake, never a finding
        # about LinkedIn, and it must be impossible to mistake for one.
        if result.get("ok") is False or result.get("error"):
            print("        search REFUSED THE ARGUMENT -- this is a defect in"
                  " the probe's input, not a measurement of the filter")
            return frozenset()
    rows = result.get("results") or []
    return frozenset(str(r.get("job_id") or "") for r in rows if r.get("job_id"))


def _distinct(sets: list) -> int:
    return len(set(sets))


def _verdict(sets: list, drift: int) -> str:
    """DISCRIMINATES / NO-EFFECT / THIN, judged against the drift floor."""
    populated = [s for s in sets if s]
    if len(populated) < 2:
        return "THIN -- fewer than two values returned any rows"
    if _distinct(sets) == 1:
        return "NO-EFFECT -- every value returned an identical id set"
    # How far apart are the two most different sets?
    spread = 0
    for i, a in enumerate(sets):
        for b in sets[i + 1:]:
            spread = max(spread, len(a ^ b))
    if spread <= drift:
        return ("INDISTINGUISHABLE FROM DRIFT -- widest disagreement "
                + str(spread) + " is within the drift floor " + str(drift))
    return ("DISCRIMINATES -- " + str(_distinct(sets))
            + " distinct id sets, widest disagreement " + str(spread))


def _bankable(verdict: str) -> str:
    return "BANKABLE" if verdict.startswith("DISCRIMINATES") else (
        "NOT BANKABLE -- " + verdict.split(" -- ")[0])


async def _measure(label: str, cases: list, drift: int, raw: dict) -> str:
    """Fire every case of one filter and print its verdict."""
    print("\n### " + label)
    sets: list = []
    for name, kwargs in cases:
        got = await _ids(**kwargs)
        sets.append(got)
        print("    value " + name + ": rows=" + str(len(got)))
    verdict = _verdict(sets, drift)
    print("    VERDICT: " + verdict)
    print("    " + _bankable(verdict))
    raw[label] = [sorted(s) for s in sets]
    return verdict


async def main() -> int:
    raw: dict = {}
    verdicts: dict = {}
    try:
        print("### CONTROL, before anything")
        async with BROWSER.session() as page:
            first_control = await _control_serves(page)
            print("    control serves: " + str(first_control))
            badge_before = await _badge(page)
            print("### invitation badge BEFORE: " + _badge_state(badge_before))
        if not first_control:
            print("    THE CONTROL DID NOT SERVE. This run is VOID. Stopping.")
            return 1

        # THE DRIFT FLOOR. Two identical requests, back to back, before any
        # filter runs. Without this number a difference between two filtered
        # sets cannot be told from LinkedIn reshuffling its own results.
        print("\n### DRIFT FLOOR -- the same query fired twice, back to back")
        base_a = await _ids(keywords=BASE_KEYWORDS, limit=10)
        base_b = await _ids(keywords=BASE_KEYWORDS, limit=10)
        drift = len(base_a ^ base_b)
        print("    first  rows=" + str(len(base_a)))
        print("    second rows=" + str(len(base_b)))
        print("    DRIFT FLOOR (symmetric difference): " + str(drift))
        print("    Any filter disagreeing by <= this has NOT been shown to act.")
        raw["drift"] = {"a": sorted(base_a), "b": sorted(base_b)}

        verdicts["J 4 date_posted (f_TPR)"] = await _measure(
            "J 4 -- Date posted, f_TPR, four values",
            [(v, {"keywords": BASE_KEYWORDS, "date_posted": v, "limit": 10})
             for v in ("any", "past_24h", "past_week", "past_month")],
            drift, raw)

        verdicts["J 5 workplace (f_WT)"] = await _measure(
            "J 5 -- Workplace type, f_WT, four values",
            [(v, {"keywords": BASE_KEYWORDS, "remote": v, "limit": 10})
             for v in ("any", "on_site", "remote", "hybrid")],
            drift, raw)

        verdicts["J 6 experience (f_E)"] = await _measure(
            "J 6 -- Experience level, f_E, six values",
            [(v, {"keywords": BASE_KEYWORDS, "experience_level": v,
                  "limit": 10})
             for v in ("internship", "entry", "associate", "mid_senior",
                       "director", "executive")],
            drift, raw)

        # THE PERMITTED VALUES ARE `relevance` AND `date`, NOT `recent`.
        # The census row is worded in LinkedIn's UI labels -- "Most relevant /
        # Most recent" -- and this probe's first run passed `recent` straight
        # through to a tool that accepts `date`. It refused, correctly, and the
        # run reported THIN. The row is about the capability; the argument
        # spelling is this server's.
        verdicts["J 7 sort_by (sortBy=DD)"] = await _measure(
            "J 7 -- Sort by, relevance vs date (LinkedIn's 'Most recent')",
            [(v, {"keywords": BASE_KEYWORDS, "sort_by": v, "limit": 10})
             for v in ("relevance", "date")],
            drift, raw)

        verdicts["J 2 boolean operators"] = await _measure(
            "J 2 -- Boolean operators in the query",
            [(name, {"keywords": q, "limit": 10})
             for name, q in BOOLEAN_QUERIES],
            drift, raw)

        # J 10 -- the company filter needs a REAL company id, which is read off
        # a posting by the shipped tool rather than typed in here.
        print("\n### J 10 -- Company filter, f_C")
        company_id = ""
        for jid in sorted(base_a)[:4]:
            try:
                detail = await server.linkedin_job_detail(jid)
            except Exception as exc:  # noqa: BLE001
                print("    job_detail raised " + type(exc).__name__)
                continue
            verdict_cell = detail.get("company_id") or {}
            if str(verdict_cell.get("state")) == "resolved":
                company_id = str(verdict_cell.get("company_id") or "")
                if company_id:
                    break
        if not company_id:
            print("    NO COMPANY ID RESOLVED off any sampled posting, so the")
            print("    filter could not be aimed. NOT FIRED -- and that is a")
            print("    fact about the resolver, not about f_C.")
            verdicts["J 10 company (f_C)"] = "NOT FIRED -- no id resolved"
        else:
            print("    a company id resolved off a posting (value not printed)")
            filtered = await _ids(keywords=BASE_KEYWORDS,
                                  company_id=company_id, limit=10)
            print("    unfiltered rows=" + str(len(base_a)))
            print("    company-filtered rows=" + str(len(filtered)))
            overlap = len(filtered & base_a)
            print("    overlap with the unfiltered set: " + str(overlap))
            if not filtered:
                v = ("NO ROWS -- the filter returned nothing; it may be right "
                     "(that employer has no match for this query) or dropped")
            elif filtered == base_a:
                v = "NO-EFFECT -- identical to the unfiltered set"
            elif len(filtered ^ base_a) <= drift:
                v = "INDISTINGUISHABLE FROM DRIFT"
            else:
                v = ("DISCRIMINATES -- the filtered set differs from the "
                     "unfiltered set by " + str(len(filtered ^ base_a)))
            print("    VERDICT: " + v)
            print("    " + _bankable(v))
            verdicts["J 10 company (f_C)"] = v
            raw["J10"] = {"filtered": sorted(filtered)}

        # J 151 -- the multi-location fan-out. Its own claim is structural:
        # one load PER PLACE, merged, with `found_in` on every row.
        print("\n### J 151 -- MULTIPLE simultaneous locations (second-load fan-out)")
        try:
            multi = await server.linkedin_search_jobs(
                keywords=BASE_KEYWORDS, locations=LOCATIONS_TWO, limit=12)
        except Exception as exc:  # noqa: BLE001
            print("    raised " + type(exc).__name__)
            multi = {}
        rows = multi.get("results") or []
        searches = multi.get("searches") or []
        found_in_present = sum(1 for r in rows if r.get("found_in"))
        distinct_found_in = len({str(r.get("found_in")) for r in rows
                                 if r.get("found_in")})
        print("    rows returned: " + str(len(rows)))
        print("    searches reported: " + str(len(searches)))
        print("    rows carrying found_in: " + str(found_in_present))
        print("    distinct found_in values: " + str(distinct_found_in))
        ids_multi = frozenset(str(r.get("job_id") or "") for r in rows
                              if r.get("job_id"))
        print("    distinct job ids: " + str(len(ids_multi)))
        if len(searches) >= 2 and distinct_found_in >= 2:
            v = ("DISCRIMINATES -- " + str(len(searches)) + " searches "
                 "reported and rows attributed to " + str(distinct_found_in)
                 + " distinct places")
        elif len(searches) >= 2:
            v = ("PARTIAL -- " + str(len(searches)) + " searches ran but rows "
                 "are attributed to " + str(distinct_found_in) + " place(s)")
        else:
            v = "NO FAN-OUT -- fewer than two searches were reported"
        print("    VERDICT: " + v)
        print("    " + _bankable(v))
        verdicts["J 151 locations"] = v
        raw["J151"] = {"searches": len(searches), "ids": sorted(ids_multi)}

        async with BROWSER.session() as page:
            badge_after = await _badge(page)
            print("\n### invitation badge AFTER: " + _badge_state(badge_after))
            print("    CONSUMPTION: " + _consumption(badge_before, badge_after))
            print("\n### CONTROL AGAIN, at the end")
            last_control = await _control_serves(page)
            print("    control serves: " + str(last_control))
        if not last_control:
            print("    THE CONTROL STOPPED SERVING. Treat every reading above")
            print("    as VOID rather than as data.")
            return 1
    except Exception as error:  # noqa: BLE001
        print("\nRUN ABORTED: " + type(error).__name__)
        print("    " + str(error)[:300])
        return 1
    finally:
        # CLOSE OUR TAB, THEN DROP THE CDP CONNECTION.
        #
        # `BROWSER.stop()` alone would already close it -- its teardown closes
        # the tab this process opened and leaves the operator's Chrome
        # serving. The page is closed EXPLICITLY FIRST anyway, for two
        # reasons. It is the idiom the rest of this package uses and the one
        # `tests/test_a_probe_closes_its_own_tab.py` recognises, and that test
        # is a RATCHET: 39 of 43 session-opening scripts leak a tab per run,
        # the count may only go down, and a probe that cleans up by a route
        # the detector cannot see would have pushed the pin UP while actually
        # being clean. Leaking is not untidiness here -- `connect_over_cdp`
        # enumerates every target on attach, and this wave's own attach took
        # 93 seconds against 56 targets and failed outright at the 15s default.
        #
        # THE PAGE, NEVER THE CONTEXT. In attach mode the context is his
        # signed-in browser; closing it closes his window.
        try:
            own = getattr(BROWSER, "_own_page", None)
            if own is not None and not own.is_closed():
                page = own
                await page.close()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    closing our tab raised " + type(exc).__name__)
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    cleanup raised " + type(exc).__name__)

    print("\n" + "=" * 68)
    print("### VERDICT SUMMARY")
    for k in sorted(verdicts):
        print("    " + k + ": " + verdicts[k])

    state = _ROOT / "_state"
    state.mkdir(exist_ok=True)
    (state / "unfired-job-search-filters-raw.json").write_text(
        json.dumps(raw, indent=2, default=str), encoding="utf-8")
    print("\n### RAW id sets written under _state/ (gitignored)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
