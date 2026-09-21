"""FIRE the per-job network-proximity reader at the live job surfaces.

## THE ONE ROW THIS SETTLES, AND WHAT ITS OWN CELL ASKS FOR

Census row ``J 40`` -- *read per-job network proximity* -- was BUILT on
2026-09-21 by wave ``proximity-field`` and banked ``COVERED-UNFIRED``. Its cell
ends with the whole of this probe's brief:

    WHAT REMAINS FOR CP: one live fire.

The reader (:func:`shape.find_proximity`, riding along in
``shape.parse_job_card`` and ``shape.parse_job_detail``) was measured over
COMMITTED CAPTURES in a local headless Chromium, in both layouts. A fixture is
not a fire. This runs the SHIPPED TOOLS -- ``linkedin_search_jobs`` and
``linkedin_job_detail``, the same code path an MCP client reaches -- against
real postings and writes down what came back.

## WHAT WOULD MAKE THIS A BANK, STATED BEFORE THE RUN

A reading that cannot tell the row from its neighbours is not evidence, and a
field that is PRESENT is not a field that WORKS. A reader whose selector died
returns ``not_drawn`` for every posting on earth and is indistinguishable, over
a sample of jobs where the operator knows nobody, from a correct reader. So the
verdict is taken on DISCRIMINATION and the tally is printed three ways:

    DISCRIMINATES-WITHIN-SURFACE   some cards on one surface read a relation
                                   and others read not_drawn. The reader is
                                   SELECTING. This is the strong result.
    DISCRIMINATES-ACROSS-SURFACE   the same job id reads ``count_read`` on the
                                   search card and ``relation_only`` on the
                                   detail page. That asymmetry is a PREDICTION
                                   this reader's design makes -- the detail
                                   page draws the relation as a heading over a
                                   face pile and states no number -- so it is
                                   a falsifiable one and not a tautology.
    UNDISCRIMINATED                every reading is the same verdict. Reported
                                   as NOT BANKABLE, whichever verdict it is.

**``not_drawn`` IS NOT A COUNT OF ZERO** and this probe never reports it as
one. The shipped alphabet says why: a card that draws no insight, a card whose
wording moved, and an account with no connection to that employer are three
different worlds, and neither this reader nor this probe can separate the third
from the other two.

## WHAT LEAVES THIS PROCESS

**INTEGERS, POSITIONS AND VERDICTS.** The proximity reading is three integers
or ``None`` by construction -- ``state`` and ``relation`` are POSITIONS in
closed alphabets this package ships. No title, no employer, no location, no job
id, no url and no page string is printed on any path.

That is asserted rather than trusted. :func:`leak_gate` refuses any proximity
value that is not an ``int`` or ``None`` and reports only the offending value's
TYPE -- never the value. The scar one layer out is that ``int()`` puts the text
it refused verbatim into its own ``ValueError``, which is how a name left this
process on 2026-09-20, so nothing here calls ``int()`` on anything off a page
and no exception message is ever printed.

## THE OBLIGATIONS THIS REPOSITORY PUTS ON A LIVE READ

Lifted from ``_probe_unfired_job_detail_insights`` by IMPORT rather than by
copy -- the control, the invitation-badge reading and the consumption verdict
are that probe's, already shown working, and writing a second copy of a check
this repository ships is a scar it has paid for.

* A CONTROL read FIRST and again LAST. If it stops serving mid-run the
  readings are VOID, not data.
* The invitation badge immediately BEFORE and AFTER, which is how this repo
  proves a read did not consume a counter it passed.
* IT FIRES NO WRITE. It searches and it reads postings. Nothing is applied to,
  saved, followed, connected to or messaged.
* IT PRESSES NOTHING. No click, no fill, no keyboard, no scroll.
* IT CLOSES ITS OWN TAB, NEVER THE CONTEXT. In attach mode the context is the
  operator's signed-in browser and closing it closes his window.

Run it as::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_proximity_live.py [N]

``N`` is the number of postings to fire the detail tool at; default 8.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import shape, server  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

# THE SIBLING PROBE'S CONTROL APPARATUS, IMPORTED. Its `main()` is behind an
# `if __name__` guard, so importing it runs constants and defs only.
import _probe_unfired_job_detail_insights as sibling  # noqa: E402


def provenance() -> list[str]:
    """Which bytes ran. A firing that cannot name its own bytes proves nothing."""
    lines = []
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(_ROOT),
            capture_output=True, text=True, check=False).stdout.strip()
    except Exception:  # noqa: BLE001
        head = "(unavailable)"
    lines.append("    head                  " + (head or "(unavailable)"))
    for name in ("shape.py", "server.py"):
        path = _ROOT / "linkedin_server" / name
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception:  # noqa: BLE001
            digest = "(unavailable)"
        lines.append("    sha256_" + name.ljust(14) + digest)
    lines.append("    mode                  "
                 + ("attach" if os.environ.get("LINKEDIN_CDP_ATTACH") else "LAUNCH"))
    return lines


def leak_gate(reading: Any) -> Optional[str]:
    """None when the reading is safe to print, else a TYPE-ONLY complaint.

    THE VALUE IS NEVER QUOTED. A proximity reading is three integers or None by
    construction; anything else is a defect, and the one thing a defect on this
    path could be carrying is a string off a page.
    """
    if reading is None:
        return None
    if not isinstance(reading, dict):
        return "proximity is a " + type(reading).__name__ + ", not a dict"
    for key in ("state", "relation", "count"):
        if key not in reading:
            continue
        value = reading[key]
        if value is None or isinstance(value, int) and not isinstance(value, bool):
            continue
        return ("proximity[" + key + "] is a " + type(value).__name__
                + ", which is neither int nor None")
    extra = sorted(set(reading) - {"state", "relation", "count"})
    if extra:
        return "proximity carries unexpected keys: " + ",".join(extra)
    return None


def state_name(position: Any) -> str:
    """The shipped token for a state position, or a description of the miss."""
    if isinstance(position, int) and 0 <= position < len(shape.PROXIMITY_STATES):
        return shape.PROXIMITY_STATES[position]
    return "(out-of-alphabet position)"


def relation_name(position: Any) -> str:
    if position is None:
        return "(none)"
    if isinstance(position, int) and 0 <= position < len(shape.PROXIMITY_RELATIONS):
        return shape.PROXIMITY_RELATIONS[position]
    return "(out-of-alphabet position)"


def verdict(states: dict[str, int]) -> str:
    """The within-surface discrimination verdict over a tally of state names.

    **THE ABSENT CASE IS IN THE TALLY, AND THE FIRST RUN OF THIS PROBE PROVED
    IT HAS TO BE.** ``parse_job_card`` OMITS the ``proximity`` key entirely
    when the card drew no insight, so `(key absent)` is not a missing
    measurement here -- it is this reader's way of saying "nothing drawn". The
    first version of this function excluded it, and on a live run that read 3
    cards ``count_read`` and 18 absent it reported UNDISCRIMINATED over a
    denominator of 3. That is blind to the exact contrast that separates a live
    reader from a dead one: **a selector that died omits the key on EVERY card**,
    so absent-everywhere is the dead-reader signature and present-on-some is
    the discrimination. Excluding the class that carries the signal left the
    verdict measuring only the rows that already agreed.
    """
    seen = {name for name, n in states.items() if n}
    if not seen:
        return "NO-SAMPLE"
    if len(seen) > 1:
        return "DISCRIMINATES-WITHIN-SURFACE"
    only = next(iter(seen))
    if only == "(key absent)":
        return ("UNDISCRIMINATED (the key was absent on every card -- this is "
                "the DEAD-READER signature)")
    return "UNDISCRIMINATED (every reading " + only + ")"


def bankable(text: str) -> str:
    if text.startswith("DISCRIMINATES"):
        return "-> this is evidence the reader is SELECTING"
    if text.startswith("UNDISCRIMINATED"):
        return ("-> NOT BANKABLE on its own: a dead reader looks exactly like "
                "this over a sample with no relation to find")
    return "-> no reading was taken"


def tally_of(readings: list[dict]) -> tuple[dict[str, int], dict[str, int], list[int]]:
    """(state tally, relation tally, every count read). Names are shipped tokens."""
    states: dict[str, int] = {name: 0 for name in shape.PROXIMITY_STATES}
    states["(key absent)"] = 0
    relations: dict[str, int] = {name: 0 for name in shape.PROXIMITY_RELATIONS}
    relations["(none)"] = 0
    counts: list[int] = []
    for reading in readings:
        if reading is None:
            states["(key absent)"] += 1
            continue
        states[state_name(reading.get("state"))] = \
            states.get(state_name(reading.get("state")), 0) + 1
        relations[relation_name(reading.get("relation"))] = \
            relations.get(relation_name(reading.get("relation")), 0) + 1
        value = reading.get("count")
        if isinstance(value, int) and not isinstance(value, bool):
            counts.append(value)
    return states, relations, counts


def print_tally(label: str, readings: list[dict]) -> str:
    states, relations, counts = tally_of(readings)
    print("\n    " + label + "  (n=" + str(len(readings)) + ")")
    for name in list(shape.PROXIMITY_STATES) + ["(key absent)"]:
        if states.get(name):
            print("        state " + name.ljust(16) + str(states[name]))
    for name in list(shape.PROXIMITY_RELATIONS) + ["(none)"]:
        if relations.get(name):
            print("        relation " + name.ljust(13) + str(relations[name]))
    if counts:
        print("        counts read           " + str(sorted(counts))
              + "  distinct=" + str(len(set(counts))))
    drawn = {n: c for n, c in states.items()
             if n not in ("not_drawn", "(key absent)") and c}
    text = verdict(states)
    print("        VERDICT " + text)
    print("        " + bankable(text))
    if not drawn:
        print("        NOTE: not_drawn IS NOT A COUNT OF ZERO. It cannot be")
        print("        separated here from an account with no relation to")
        print("        these employers.")
    return text


async def main() -> int:
    wanted = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    if not os.environ.get("LINKEDIN_CDP_ATTACH"):
        print("REFUSING: LINKEDIN_CDP_ATTACH is not set. This probe attaches")
        print("to the browser already running on the persistent profile and")
        print("never launches one -- the profile is stamped newer than")
        print("Playwright's chromium and launching migrates it aside,")
        print("discarding the signed-in session.")
        return 1

    print("=" * 68)
    print("FIRE THE PROXIMITY READER -- census row J 40, COVERED-UNFIRED")
    print("=" * 68)
    print("\n### PROVENANCE")
    for line in provenance():
        print(line)

    own = None
    by_id: dict[str, dict] = {}
    card_readings: list[dict] = []
    detail_readings: list[dict] = []
    paired: list[tuple[str, str]] = []
    followers_tally = {"int": 0, "none": 0, "absent": 0}
    about_states: dict[str, int] = {}
    follower_values: list[int] = []
    leaks: list[str] = []
    errors: dict[str, int] = {}
    cards_seen = 0
    details_ok = 0

    try:
        # PHASE 1 -- our own session, for the control and the badge ONLY.
        # THE SESSION IS RELEASED BEFORE ANY SHIPPED TOOL IS CALLED.
        # `BROWSER.session()` holds a single-flight lock for the whole of its
        # body and every shipped tool opens a session of its own; calling one
        # from inside ours DEADLOCKS as a silent hang that looks exactly like
        # a slow page. Measured by the sibling probe, twice, 2026-09-20.
        print("\n### CONTROL, before anything")
        async with BROWSER.session() as page:
            own = page
            first_control = await sibling._control_serves(page)
            print("    control serves: " + str(first_control))
            badge_before = await sibling._badge(page)
            print("    invitation badge BEFORE: "
                  + sibling._badge_state(badge_before))
        own = None
        if not first_control:
            print("    THE CONTROL DID NOT SERVE. This run is VOID.")
            return 1

        # PHASE 2 -- the SEARCH surface. This is the path that carries a COUNT.
        print("\n### FIRE linkedin_search_jobs (the surface that draws a count)")
        for term in sibling.HARVEST_TERMS:
            try:
                result = await server.linkedin_search_jobs(keywords=term, limit=10)
            except Exception as exc:  # noqa: BLE001 - TYPE only, never the message
                errors[type(exc).__name__] = errors.get(type(exc).__name__, 0) + 1
                continue
            rows = result.get("results") or []
            print("    a search returned rows: " + str(len(rows)))
            for row in rows:
                cards_seen += 1
                reading = row.get("proximity")
                complaint = leak_gate(reading)
                if complaint:
                    leaks.append("search card: " + complaint)
                    continue
                card_readings.append(reading)
                jid = str(row.get("job_id") or "").strip()
                if jid and jid not in by_id:
                    by_id[jid] = reading

        # THE DENOMINATOR THAT MATTERS IS JOBS, NOT CARDS, AND THE FIRST TWO
        # RUNS OF THIS PROBE GOT IT WRONG. Three searches returned 21 cards
        # and the tally read `count_read 3` -- which reads like three postings
        # until you notice the detail phase found only ONE of them distinct.
        # A popular posting matching all three search terms is rendered three
        # times and drew three times, so counting CARDS reports one fact as
        # three. That is precisely the hazard `find_proximity` closes INSIDE a
        # card ("de-duplication is on the fact, not on the match"), reappearing
        # one layer up in the instrument that measures it.
        drew_ids = sorted(j for j, r in by_id.items() if r)
        print("    cards seen: " + str(cards_seen)
              + "   readings kept: " + str(len(card_readings)))
        # ZERO CARDS IS NOT A NEGATIVE READING, IT IS NO READING, AND EVERY
        # TALLY BELOW WOULD BE A COUNT OVER AN EMPTY SAMPLE. `cards_seen` is
        # the raw material this whole run is made of. If the search surface
        # returned nothing then `find_proximity` was never reached, and
        # nothing downstream is evidence about it in either direction.
        # FALLING THROUGH WAS THE DEFECT, and it is quiet rather than loud:
        # `verdict()` answers NO-SAMPLE over n=0, `strong` is then False, and
        # the banking question prints "EVERY READING WAS THE SAME VERDICT"
        # about zero readings. That sentence is false, and it is the one
        # shape this probe's own preamble forbids -- the ABSENCE of data
        # reported as data, in the exact words a real negative would use. It
        # exits 1 either way, so the whole difference lives in the log, which
        # is what makes it worth a branch instead of a footnote.
        if not cards_seen:
            print("    NO CARD WAS READ AT ALL. This run is VOID, not a")
            print("    negative: the SEARCH surface returned nothing, so the")
            print("    proximity reader was never reached and no tally below")
            print("    would be a measurement of it.")
            if errors:
                print("    searches that raised, by TYPE (messages"
                      " deliberately not printed): "
                      + ", ".join(name + "=" + str(errors[name])
                                  for name in sorted(errors)))
            else:
                print("    No search raised: each returned zero rows, which")
                print("    is the search surface's own answer and not this")
                print("    reader's.")
            return 1
        print("    DISTINCT job ids seen: " + str(len(by_id))
              + "   distinct ids that DREW: " + str(len(drew_ids)))
        if len(by_id) and len(drew_ids):
            print("    so the per-JOB rate is " + str(len(drew_ids)) + " of "
                  + str(len(by_id)) + ", not "
                  + str(len([r for r in card_readings if r])) + " of "
                  + str(len(card_readings)))

        # PHASE 3 -- the DETAIL surface. The reader's own design predicts
        # relation_only here: the detail page draws the relation as a heading
        # over a face pile and states no number.
        # WHICH POSTINGS GET THE DETAIL CALL, AND WHY IT IS NOT THE FIRST N.
        # The cross-surface question -- does ONE job read differently on two
        # renderings -- can only be ASKED where the search card drew
        # something, and the first run of this probe spent 7 of its 8 detail
        # calls on cards that drew nothing, leaving that comparison at n=1.
        # So the drawing cards go first and the rest fill the sample. This is
        # not a filter on the answer: every card that drew is included, none
        # is dropped for what it said, and the non-drawing fill is kept so the
        # detail surface's OWN discrimination is still measured against it.
        drew = [j for j, r in by_id.items() if r]
        rest = [j for j, r in by_id.items() if not r]
        ids = (drew + rest)[:wanted]
        print("\n### FIRE linkedin_job_detail on " + str(len(ids)) + " postings")
        print("    of which the search card drew a reading on: "
              + str(len([j for j in ids if by_id.get(j)])))
        for jid in ids:
            try:
                out = await server.linkedin_job_detail(jid)
            except Exception as exc:  # noqa: BLE001 - TYPE only
                errors[type(exc).__name__] = errors.get(type(exc).__name__, 0) + 1
                continue
            details_ok += 1
            reading = out.get("proximity")
            complaint = leak_gate(reading)
            if complaint:
                leaks.append("job detail: " + complaint)
            else:
                detail_readings.append(reading)
                paired.append((state_name((by_id[jid] or {}).get("state"))
                               if by_id[jid] else "(key absent)",
                               state_name((reading or {}).get("state"))
                               if reading else "(key absent)"))
            # N 53 rides along at zero extra page load: the follower count is
            # published under `company_about` off this same posting.
            about = out.get("company_about")
            # `state` IS READ ALONGSIDE `followers`, NOT INSTEAD OF IT.
            # `state == "read"` (every field parsed) is stronger evidence than
            # a non-null `followers` under any other state, because "partial
            # with followers present but something else missing" is itself
            # informative about which half of the card shape held. The four
            # values are shipped tokens from `shape.company_about_card`
            # (absent / read / unhydrated / unnamed), so printing them
            # discloses nothing off the page.
            if isinstance(about, dict):
                token = str(about.get("state") or "(no state key)")
                about_states[token] = about_states.get(token, 0) + 1
            value = (about or {}).get("followers") if isinstance(about, dict) else None
            if value is None:
                if isinstance(about, dict) and "followers" in about:
                    followers_tally["none"] += 1
                else:
                    followers_tally["absent"] += 1
            elif isinstance(value, int) and not isinstance(value, bool):
                followers_tally["int"] += 1
                follower_values.append(value)
            else:
                leaks.append("company_about.followers is a "
                             + type(value).__name__ + ", not int or None")

        # PHASE 4 -- the control again, and the badge.
        print("\n### CONTROL, after everything")
        async with BROWSER.session() as page:
            own = page
            last_control = await sibling._control_serves(page)
            print("    control serves: " + str(last_control))
            badge_after = await sibling._badge(page)
            print("    invitation badge AFTER: "
                  + sibling._badge_state(badge_after))
            print("    consumption: "
                  + sibling._consumption(badge_before, badge_after))
        own = None
        if not last_control:
            print("    THE CONTROL STOPPED SERVING. These readings are VOID.")
            return 1

    except Exception as exc:  # noqa: BLE001 - TYPE only, never the message
        print("\n    THE RUN RAISED " + type(exc).__name__
              + " -- message deliberately not printed")
        return 1
    finally:
        # CLOSE OUR TAB, THEN DROP THE CDP CONNECTION. THE PAGE, NEVER THE
        # CONTEXT: in attach mode the context is his signed-in browser.
        try:
            own = getattr(BROWSER, "_own_page", None)
            if own is not None and not own.is_closed():
                # BOUND TO `page` ON PURPOSE, exactly as the sibling probe
                # does. `tests/test_a_probe_closes_its_own_tab.py` recognises
                # a close by NAME -- `(page|tab|_own_page).close(` -- and it
                # is a RATCHET whose count may only go down. A probe that
                # cleans up by a route the detector cannot see pushes that pin
                # UP while actually being clean, which is worse than leaking:
                # it spends the budget AND teaches the instrument nothing.
                page = own
                await page.close()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    closing our tab raised " + type(exc).__name__)
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    cleanup raised " + type(exc).__name__)

    print("\n" + "=" * 68)
    print("### WHAT THE READER SAID")
    search_verdict = print_tally("SEARCH CARDS (per rendering)", card_readings)
    per_job = print_tally("SEARCH, PER DISTINCT JOB ID",
                          [r for _j, r in sorted(by_id.items())])
    detail_verdict = print_tally("JOB DETAIL", detail_readings)

    print("\n    CROSS-SURFACE, same job id read on both")
    pairs: dict[str, int] = {}
    for a, b in paired:
        key = a + " -> " + b
        pairs[key] = pairs.get(key, 0) + 1
    for key in sorted(pairs):
        print("        " + key.ljust(40) + str(pairs[key]))
    asymmetric = sum(n for k, n in pairs.items()
                     if k.split(" -> ")[0] != k.split(" -> ")[1])
    print("        pairs whose two surfaces DISAGREE: " + str(asymmetric))
    if asymmetric:
        print("        -> DISCRIMINATES-ACROSS-SURFACE. The reader answers")
        print("           differently to two renderings of the same job,")
        print("           which a defaulted field cannot do.")

    print("\n### N 53 RIDING ALONG -- company_about")
    print("    followers int=" + str(followers_tally["int"])
          + "  none=" + str(followers_tally["none"])
          + "  key absent=" + str(followers_tally["absent"]))
    print("    card state tally (shipped tokens): "
          + ", ".join(k + "=" + str(v) for k, v in sorted(about_states.items())))
    if follower_values:
        print("    distinct values: " + str(len(set(follower_values)))
              + " over " + str(len(follower_values)) + " postings")
        # MAGNITUDE SPREAD, NOT THE VALUES. A single large-number sample
        # cannot surface a magnitude-dependent wording change -- an
        # abbreviated "2K", a singular "1 follower", a zero-state. Digit
        # LENGTHS are printed; the numbers themselves are the employer's own
        # size and are not this probe's to publish.
        buckets: dict[int, int] = {}
        for v in follower_values:
            width = len(str(abs(v)))
            buckets[width] = buckets.get(width, 0) + 1
        print("    magnitude spread (digit length -> postings): "
              + ", ".join(str(k) + "->" + str(v) for k, v in sorted(buckets.items())))
        print("    distinct magnitudes: " + str(len(buckets)))
    print("    NOT CLOSED HERE: the OCCURRENCE COUNT of the follower line")
    print("    inside the card. `_ABOUT_FOLLOWERS` is fully anchored (^...$)")
    print("    so the N 54 suffix collision is structurally impossible, but")
    print("    'exactly one line matches' is a measurement nobody has taken.")

    if errors:
        print("\n### errors by TYPE (messages deliberately not printed)")
        for name in sorted(errors):
            print("    " + name + ": " + str(errors[name]))

    if leaks:
        print("\n### THE LEAK GATE FIRED -- " + str(len(leaks)) + " time(s)")
        for complaint in leaks[:20]:
            print("    " + complaint)
        print("    A value on this path that is neither int nor None is a")
        print("    DEFECT, and the one thing it could be carrying is a string")
        print("    off a page. Nothing is banked on this run.")
        return 1

    print("\n### THE BANKING QUESTION")
    strong = (per_job.startswith("DISCRIMINATES")
              or detail_verdict.startswith("DISCRIMINATES")
              or asymmetric > 0)
    if strong:
        print("    The reader DISCRIMINATED on live pages. J 40's remaining")
        print("    cost was 'one live fire' and this is it.")
        return 0
    print("    EVERY READING WAS THE SAME VERDICT. This run does not")
    print("    distinguish a working reader from a dead one, and J 40 does")
    print("    NOT bank on it. Reported as measured, not as a pass.")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
