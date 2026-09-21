"""FIRE THE SHIPPED PEOPLE-SEARCH SHAPER AT THE LIVE SURFACE, AND ASK WHETHER
ITS ANSWER DISCRIMINATES.

`linkedin_people_search_shape` landed 2026-09-20 with its address and its
shaper, and its own docstring says the part that matters here:

    **Not that it has seen a live people-search page.** No capture of this
    surface exists in this repository and this tool has never been run
    against one [...] its FIT to LinkedIn's real dialect is unmeasured.

Fourteen census rows (`N 80`-`N 93`, named in
:data:`search_results.FILTER_TERM_ROWS`) sit on that unmeasured fit. This
probe is the firing. It builds nothing and changes nothing; it runs the two
shipped readers against the real page and writes down what they say.

## THE QUESTION IS NOT "DOES A FIELD COME BACK". IT IS "DOES IT DISCRIMINATE"

A reader that answers the same thing for everything looks exactly like a
working one when you only look at the row you hoped for. Two measured scars in
this repository say so: a field that read ``4 true / 0 false`` at n=4 and
``9 / 2`` at n=11, and a filter probe where **every** value returned exactly
seven rows, so no count could have refuted anything.

So a count from this probe is worthless on its own, and it ships with three
controls that cost one extra page load between them:

**CONTROL 1 -- WITHIN THE PAGE.** If some vocabulary terms read 0 while others
read nonzero on the SAME reading, the matcher is selecting rather than
saluting. A reading where all fourteen are nonzero is NOT evidence of fourteen
filters; it is the shape a broken matcher also makes, and this probe says so.

**CONTROL 2 -- ACROSS PAGES.** The same two readers are run against
``config.FEED_URL``, an ordinary admitted read that is not a search page and
has no people-search filter panel. Same code, same call, different page. If
the filter counts do not collapse there, the number is about the reader and
not about the page, and NOTHING may be banked off it.

**CONTROL 3 -- ACROSS TIME, TWICE OVER.** Search pages on this platform are
shells that fill in afterwards -- ``_probe_search_render_timeline.py`` measured
a results page holding 25 hrefs in total. So each load is read TWICE, seconds
apart, and a count that is still rising is reported as a reading of a
half-drawn page rather than as a property of the surface. The whole load is
then repeated, because a control proves an instrument CAN speak while only
repetition proves that what it said was stable.

There is a fourth control this probe did not have to build, because the module
already carries it as a PRE-REGISTERED PREDICTION. ``search_results`` limit 3:

    a control labelled ``Keywords (first name, last name)`` does NOT match the
    term ``keywords``, because a single-word phrase must be the whole label.
    The census's own wording for ``N 93`` is exactly that decorated form.

That is a named term predicted IN ADVANCE to miss on the live page. If it
misses while its neighbours match, the vocabulary is discriminating on real
labels, and the prediction cost nothing to make.

## WHAT THIS PROBE MAY EMIT, AND WHY THAT IS ENFORCED RATHER THAN INTENDED

Every row of a people search is a third party. The shaper is name-free by
construction -- integers rebuilt through ``coerce.as_int``, strings only from
shipped vocabulary -- and the point of a live firing is to CHECK that
construction rather than to trust it.

So :func:`_gate` re-derives the shipped alphabets
(``search_results.emitted_alphabet()`` and ``filter_alphabet()``) and refuses
to write or print any string outside them plus this probe's own key names. A
string that is not in the alphabet is not tidied away: the probe stops, names
the FIELD it appeared in, and prints nothing of the value.

**NO ADDRESS IS EVER PRINTED.** Not the one navigated to, not the one landed
on. ``scripts/cdp_targets.py`` exists because this repo has already put the
operator's own profile slug into a transcript three times, and a landed search
url can carry a query. What this prints is the BOOLEAN of whether the landing
matched the request.

**NO EXCEPTION MESSAGE IS EVER PRINTED**, only its type. That is the same scar
one layer out: ``int()`` puts the value it refused verbatim into its own
``ValueError``, which is how a name left this process on 2026-09-20. An
arbitrary exception from a page interaction has no such guarantee either way,
so the text is never rendered.

## BOUNDS

**READS ONLY, AND NOTHING IS PRESSED.** Two shipped readers, both of which only
evaluate the package's own committed classifier, neither of which takes a
confirm token. Nothing is clicked, filled, scrolled or submitted. The "All
filters" panel is NOT opened -- opening it is a press, and this surface's
admitting ruling (condition 5) is that nothing is fired here. A filter that
lives only behind that button therefore reads 0, and that is an honest 0 about
what the page OFFERS WITHOUT INTERACTION, which is what the probe reports.

**ATTACH ONLY.** It refuses to run unless ``LINKEDIN_CDP_ATTACH`` is set, so it
can never launch a second Chrome against the persistent profile. Attach mode
opens a tab of its own and never navigates one the operator is using.

**RAW OUTPUT IS GITIGNORED.** ``--out`` defaults under ``_state/``. A capture of
this surface holds other people; only the derived integers are fit to commit.

USAGE::

    set LINKEDIN_CDP_ATTACH=1
    ./venv/Scripts/python.exe scripts/_probe_people_search_shape_live.py
    ./venv/Scripts/python.exe scripts/_probe_people_search_shape_live.py --loads 3
    ./venv/Scripts/python.exe scripts/_probe_people_search_shape_live.py --fire-tool

``--fire-tool`` additionally runs ``linkedin_people_search_shape`` ITSELF rather
than only its two readers, so the reading also passes through
``assert_not_authwall`` and the published envelope. **That is what a census row
means when it says a tool fired**, and the difference between "the readers ran"
and "the tool ran" is small enough to be worth closing rather than arguing
about. The envelope's one free-text field is checked for provenance rather than
whitelisted -- see :func:`_shipped_literals`.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import config, search_results  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: Between the two readings of one load. Long enough that a shell that is
#: still filling will have moved, short enough to keep a load cheap.
SETTLE_GAP_S = 6.0

#: Keys this probe itself introduces. Everything else a payload may carry has
#: to come out of the shipped alphabets.
_OWN_KEYS: frozenset[str] = frozenset(
    {
        "trial",
        "surface",
        "reading",
        "results",
        "filters",
        "by_kind",
        "by_term",
        "by_value_class",
        "kinds_not_reported",
        "terms_not_reported",
        "positions_beyond_the_alphabet",
        "positions_beyond_the_vocabulary",
        "total_classified",
        "person_results",
        "traversals_refused",
        "queries_present",
        "filters_offered",
        "person_valued_filters",
        "needle_valued_filters",
        "anchors_seen",
        "counts",
        "numeric_entity",
        "non_numeric_entity",
        "values_refused",
        "controls_seen",
        "matched_controls",
        "unmatched_controls",
        "empty_labels",
        "landed_where_it_was_sent",
        "people_search",
        "feed",
        "provenance",
        "head",
        "sha256_search_results",
        "sha256_dom",
        "mode",
        "loads",
        "settle_gap_s",
        "taken_at",
        "trials",
        "error_type",
        # --fire-tool: the SHIPPED TOOL's envelope keys, which the readers
        # above do not have. `not_claimed` is handled separately -- see
        # `_shipped_literals`.
        "ok",
        "pages_loaded",
        "denominators",
        "entity_segments_numeric",
        "entity_segments_non_numeric",
        "tool_payload",
        "not_claimed_are_shipped_literals",
        "tool_firings_that_saw_a_filter",
    }
)


def say(line: str = "") -> None:
    print(line, flush=True)


def _alphabet() -> frozenset[str]:
    """Every string a gated payload may contain. Re-derived, never listed."""
    return (
        search_results.emitted_alphabet()
        | search_results.filter_alphabet()
        | _OWN_KEYS
    )


def _gate(payload: object, allowed: frozenset[str], where: str = "") -> None:
    """Refuse any string outside the shipped alphabets. NEVER PRINTS THE VALUE.

    The whole claim under test is that no string from the document can leave
    the shaper. This is that claim, executed against what the live page
    actually produced, rather than read off the module docstring.

    On a violation it raises naming the FIELD PATH only. The offending string
    is not printed, not logged and not written -- on this surface the string a
    reader was not expecting is a person's name until shown otherwise, and
    "show me what leaked" is how it leaks a second time.
    """
    if isinstance(payload, dict):
        for key, value in payload.items():
            if not isinstance(key, str) or key not in allowed:
                raise ValueError(f"UNVOCABULARY KEY at {where or '<root>'}")
            _gate(value, allowed, f"{where}.{key}" if where else key)
        return
    if isinstance(payload, (list, tuple)):
        for position, value in enumerate(payload):
            _gate(value, allowed, f"{where}[{position}]")
        return
    if isinstance(payload, str):
        if payload not in allowed:
            raise ValueError(f"UNVOCABULARY STRING at {where or '<root>'}")
        return
    if isinstance(payload, (int, float, bool)) or payload is None:
        return
    raise ValueError(f"UNEXPECTED TYPE {type(payload).__name__} at {where}")


def _sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _head() -> str:
    """The commit this code is, or a LOUD marker naming why it is unknown.

    **IT NEVER RETURNS AN EMPTY STRING, AND THAT IS THE WHOLE POINT.** This
    value is the provenance line of a firing that a census row will cite. An
    empty string for "git did not run" is the same value a reader would get
    for "no head", and the two are different findings -- one is an outage and
    one is a fact about the tree. Returning a falsy datum out of an exception
    handler is how an outage gets filed as an absence, and
    `tests/test_an_outage_is_never_filed_as_an_absence.py` refuses it.

    So a failure comes back as a non-falsy string that says so and names the
    exception TYPE. It cannot be mistaken for a commit id and it cannot be
    mistaken for nothing.
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"UNKNOWN -- git did not run ({type(exc).__name__})"
    if out.returncode != 0:
        return f"UNKNOWN -- git rev-parse exited {out.returncode}"
    return out.stdout.strip() or "UNKNOWN -- git printed nothing"


def provenance() -> dict:
    """WHICH CODE RAN. A stale server process holds the code it started with,
    so a firing that cannot name its own bytes has not proven anything."""
    pkg = pathlib.Path(search_results.__file__).resolve().parent
    return {
        "head": _head(),
        "sha256_search_results": _sha(pkg / "search_results.py"),
        "sha256_dom": _sha(pkg / "dom.py"),
        "mode": BROWSER.mode if hasattr(BROWSER, "mode") else "",
    }


async def _read_both(page) -> dict:
    """One reading: both shipped readers, tallied the way the tool tallies."""
    results = await search_results.read_results(page)
    filters = await search_results.read_filters(page)
    return {
        "results": {
            **search_results.tally(
                results["counts"], results.get("queries_present", 0)
            ),
            "anchors_seen": results["anchors_seen"],
            "numeric_entity": results["numeric_entity"],
            "non_numeric_entity": results["non_numeric_entity"],
            "values_refused": results["values_refused"],
        },
        "filters": {
            **search_results.tally_filters(filters["counts"]),
            "controls_seen": filters["controls_seen"],
            "matched_controls": filters["matched_controls"],
            "unmatched_controls": filters["unmatched_controls"],
            "empty_labels": filters["empty_labels"],
            "values_refused": filters["values_refused"],
        },
    }


async def one_load(page, url: str, surface: str, trial: int) -> dict:
    """Navigate once, read TWICE. The pair is control 3's within-load half."""
    landed = await BROWSER.goto(page, url)
    matched = landed.rstrip("/") == url.rstrip("/")
    first = await _read_both(page)
    await asyncio.sleep(SETTLE_GAP_S)
    second = await _read_both(page)
    return {
        "trial": trial,
        "surface": surface,
        "landed_where_it_was_sent": matched,
        "reading": [first, second],
    }


def _print_reading(label: str, reading: dict) -> None:
    res, filt = reading["results"], reading["filters"]
    say(f"    {label}")
    say(
        "      results : anchors=%d classified=%d person=%d traversals=%d "
        "queries=%d refused=%d"
        % (
            res["anchors_seen"],
            res["total_classified"],
            res["person_results"],
            res["traversals_refused"],
            res["queries_present"],
            res["values_refused"],
        )
    )
    say(
        "      filters : controls=%d matched=%d unmatched=%d empty=%d "
        "offered=%d refused=%d"
        % (
            filt["controls_seen"],
            filt["matched_controls"],
            filt["unmatched_controls"],
            filt["empty_labels"],
            filt["filters_offered"],
            filt["values_refused"],
        )
    )
    hits = [t for t, n in sorted(filt["by_term"].items()) if n]
    miss = [t for t, n in sorted(filt["by_term"].items()) if not n]
    say(f"      terms nonzero ({len(hits)}): {', '.join(hits) or '-'}")
    say(f"      terms zero    ({len(miss)}): {', '.join(miss) or '-'}")
    kinds = [f"{k}={n}" for k, n in sorted(res["by_kind"].items()) if n]
    say(f"      kinds nonzero : {', '.join(kinds) or '-'}")


def _shipped_literals(strings: list) -> bool:
    """Are these sentences LITERALS IN `server.py`, or did they come off a page?

    The shipped tool's envelope carries a ``not_claimed`` list of English
    sentences. They are module literals -- but *"they are literals"* is exactly
    the kind of claim this wave exists to stop taking on trust, and the gate
    above cannot help: free English is outside every shipped alphabet by
    construction, so whitelisting it would mean whitelisting arbitrary text on
    the one surface where arbitrary text is a name.

    So it is CHECKED rather than excused: each sentence must appear in
    `linkedin_server/server.py`'s own source. A sentence that came from the
    document cannot be in the file that was written before the page loaded.

    **THE NAIVE FORM OF THIS CHECK IS WRONG AND SAID SO ON ITS FIRST RUN.** A
    plain ``s in source`` returned False for all three sentences, which looks
    exactly like a finding and is not one: the literals are written as IMPLICIT
    CONCATENATION across source lines, so the runtime string is a splice of
    fragments separated in the file by a quote, a newline and an indent. The
    reconstruction below splices those junctions back and collapses whitespace
    before comparing. *A provenance check that cannot see the shape its own
    codebase writes strings in manufactures a leak report.*
    """
    if not strings:
        return False
    source = (REPO / "linkedin_server" / "server.py").read_text(encoding="utf-8")
    spliced = re.sub(r'"\s*"', "", source)
    spliced = re.sub(r"\s+", " ", spliced)
    for sentence in strings:
        if not isinstance(sentence, str):
            return False
        if re.sub(r"\s+", " ", sentence).strip() not in spliced:
            return False
    return True


async def fire_the_tool(allowed: frozenset) -> dict:
    """Run the SHIPPED TOOL, not just its readers. Returns the gated payload.

    **THE DIFFERENCE IS SMALL AND IT IS NOT NOTHING.** The trials above drive
    ``read_results`` and ``read_filters`` and tally them the way the tool does.
    This calls the tool body itself, so the reading also passes through
    ``assert_not_authwall`` and the published envelope -- which is what a
    census row means when it says a tool fired.

    **IT HOLDS NO SESSION WHILE IT DOES SO.** ``BROWSER.session()`` takes a
    single-flight lock for the whole of its body and the tool opens a session
    of its own; calling one from inside another DEADLOCKS, measured on this box
    twice as a silent hang that looks exactly like a slow page.
    """
    from linkedin_server import server  # imported here: it pulls the world in

    payload = await server.linkedin_people_search_shape()
    if not isinstance(payload, dict):
        raise ValueError("the tool returned something that is not a payload")
    rest = dict(payload)
    not_claimed = rest.pop("not_claimed", [])
    rest["not_claimed_are_shipped_literals"] = _shipped_literals(not_claimed)
    _gate(rest, allowed, "tool")
    return rest


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--loads", type=int, default=2)
    parser.add_argument(
        "--fire-tool",
        action="store_true",
        help="also run the SHIPPED TOOL end to end, not only its readers.",
    )
    parser.add_argument(
        "--fire-tool-times",
        type=int,
        default=1,
        help=(
            "how many times to fire the tool. MORE THAN ONE IS THE POINT when "
            "characterising the read-too-early race: a race is a RATIO, and one "
            "firing cannot tell a race from a verdict."
        ),
    )
    parser.add_argument("--out", default=str(REPO / "_state" / "people-search-shape-live.json"))
    parser.add_argument(
        "--skip-feed-control",
        action="store_true",
        help="run WITHOUT control 2. The output then cannot bank a row.",
    )
    args = parser.parse_args()

    if not config.CDP_ATTACH:
        say("REFUSING: LINKEDIN_CDP_ATTACH is not set.")
        say("This probe attaches to a Chrome that is already running. Launching")
        say("a second one against the persistent profile costs the signed-in")
        say("session, and only the operator can put it back.")
        return 2

    allowed = _alphabet()
    record = {
        "provenance": provenance(),
        "loads": args.loads,
        "settle_gap_s": SETTLE_GAP_S,
        "taken_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trials": [],
    }

    say("PROVENANCE -- which code actually ran")
    for key, value in record["provenance"].items():
        say(f"  {key:<24} {value}")
    say()

    try:
        await BROWSER.start()
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        say(f"COULD NOT ATTACH: {type(exc).__name__}")
        return 2

    # OUR tab, held so the finally can close it. **THE PAGE, NEVER THE
    # CONTEXT** -- in attach mode the context is the operator's own signed-in
    # Chrome and closing it takes his browser down; the tab is ours and every
    # probe process that leaves one behind adds a target that
    # `connect_over_cdp` must enumerate on the next attach.
    tab = None
    try:
        async with BROWSER.session() as page:
            tab = page
            for trial in range(1, args.loads + 1):
                say(f"LOAD {trial} -- people search")
                trial_record = await one_load(
                    page, search_results.PEOPLE_SEARCH_URL, "people_search", trial
                )
                _gate(trial_record, allowed, f"trial{trial}")
                record["trials"].append(trial_record)
                say(f"    landed where sent: {trial_record['landed_where_it_was_sent']}")
                _print_reading("reading 1 (immediately after settle)", trial_record["reading"][0])
                _print_reading(f"reading 2 (+{SETTLE_GAP_S:.0f}s)", trial_record["reading"][1])
                say()

            if not args.skip_feed_control:
                say("CONTROL 2 -- the same readers on the feed, which is not a search")
                control = await one_load(page, config.FEED_URL, "feed", 0)
                _gate(control, allowed, "control")
                record["trials"].append(control)
                say(f"    landed where sent: {control['landed_where_it_was_sent']}")
                _print_reading("reading 1", control["reading"][0])
                _print_reading(f"reading 2 (+{SETTLE_GAP_S:.0f}s)", control["reading"][1])
                say()

        # OUTSIDE the session block on purpose -- see fire_the_tool().
        if args.fire_tool:
            record["tool_payload"] = []
            saw_a_filter = 0
            for shot in range(1, max(1, args.fire_tool_times) + 1):
                say(f"THE SHIPPED TOOL ITSELF, firing {shot}, no session held")
                tool_payload = await fire_the_tool(allowed)
                # WHICH FIRING PRODUCED THIS PAYLOAD, carried in the record and
                # not only in the console. The race in section 4b of the
                # deliverable is a statement about a PARTICULAR firing, so a
                # reader opening the saved reading has to be able to tell them
                # apart. Set after the gate: it is our own integer.
                tool_payload["trial"] = shot
                record["tool_payload"].append(tool_payload)
                denominators = tool_payload.get("denominators", {})
                filters_by_term = tool_payload.get("filters", {}).get("by_term", {})
                hits = [t for t, n in sorted(filters_by_term.items()) if n]
                if hits:
                    saw_a_filter += 1
                say(f"    ok / landed / pages    : {tool_payload.get('ok')} / "
                    f"{tool_payload.get('landed_where_it_was_sent')} / "
                    f"{tool_payload.get('pages_loaded')}")
                say(f"    values_refused         : {denominators.get('values_refused')}")
                say(f"    not_claimed are shipped: "
                    f"{tool_payload.get('not_claimed_are_shipped_literals')}")
                # THE DENOMINATOR IS THE WHOLE STORY ON THIS SURFACE. A low
                # controls_seen is a page that had not finished drawing, and it
                # is what separates "no filters" from "read too early".
                say(f"    controls_seen          : {denominators.get('controls_seen')}"
                    f"   (unmatched {denominators.get('unmatched_controls')})")
                say(f"    anchors_seen           : {denominators.get('anchors_seen')}")
                say(f"    filters.by_term nonzero: {', '.join(hits) or '-'}")
                results_by_kind = tool_payload.get("results", {}).get("by_kind", {})
                kinds = [f"{k}={n}" for k, n in sorted(results_by_kind.items()) if n]
                say(f"    results.by_kind nonzero: {', '.join(kinds) or '-'}")
                say()
            record["tool_firings_that_saw_a_filter"] = saw_a_filter
            say(f"TOOL FIRINGS THAT SAW ANY FILTER: {saw_a_filter} of "
                f"{max(1, args.fire_tool_times)}")
            say()
    except ValueError as exc:
        # THE GATE'S OWN REFUSAL, and its message is safe to render where a
        # general exception's is not: it is built from FIELD PATHS only and
        # never from a value. `_check_the_probe_vocabulary_gate_can_fail.py`
        # case B3 asserts exactly that -- the message names the field the
        # string was found under and does not echo the string. Printing it is
        # what makes a refusal diagnosable instead of merely loud.
        say(f"PROBE REFUSED ITS OWN OUTPUT: {exc}")
        say("A string outside the shipped alphabets reached the payload. The")
        say("value is deliberately not printed. Treat this as a leak until")
        say("shown otherwise, and do not re-run to 'see what it was'.")
        record["error_type"] = "ValueError"
        _write(args.out, record)
        return 1
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        say(f"PROBE FAILED: {type(exc).__name__}")
        record["error_type"] = type(exc).__name__
        _write(args.out, record)
        return 1
    finally:
        if tab is not None and not tab.is_closed():
            await tab.close()
        await BROWSER.stop()

    _write(args.out, record)
    return 0


def _write(out: str, record: dict) -> None:
    path = pathlib.Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    say(f"raw reading written under {path.parent.name}/ (gitignored)")


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
