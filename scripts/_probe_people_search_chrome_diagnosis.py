"""WHY DID THIRTEEN OF THE FOURTEEN FILTER TERMS READ ZERO ON THE LIVE PAGE?

``_probe_people_search_shape_live.py`` fired the shipped shaper at
``/search/results/people/`` and got a stable, discriminating answer: of the
fourteen vocabulary terms that serve census rows ``N 80``-``N 93``, exactly two
read nonzero and twelve read zero, while the same reader on the feed read
fourteen zeros out of 72-203 controls.

**A ZERO IS NOT A FINDING UNTIL YOU KNOW WHICH KIND OF ZERO IT IS.** There are
three, and they carry completely different weight for a census row:

    ABSENT        the page does not draw that control at all.
    UNDRAWN       the page draws no search chrome, so the question was never
                  really asked.
    MISSED        the control is there and the matcher did not recognise its
                  label -- ``search_results`` limit 3 predicts exactly this for
                  a decorated single-word label, and names ``N 93`` as the case.

Banking a row on the wrong one of those is the over-claim this campaign cannot
afford, so this probe separates them.

## IT READS LABELS THE ONLY WAY THIS SURFACE PERMITS: IT DOES NOT

The obvious way to tell the three apart is to print the 79 unmatched labels and
look. **That is forbidden here and not as a formality.** A filter label on this
page can BE a person -- the ``Connections of`` control renders as
``Connections of <a person>`` once set -- and a result card's accessible name
carries an employer. The repository already records the operator's own slug
reaching a transcript three times.

So this probe never extracts a label. It drives the SHIPPED in-page classifier
(``dom.read_search_filters``) through its SHIPPED ``phrases`` parameter, handing
it a different vocabulary and reading back the same integer counts. **No new
JavaScript is injected and no string leaves the page** -- the only thing that
changes is which words this process shipped IN.

## THE VOCABULARY IT SHIPS IN, AND WHAT EACH WORD IS FOR

The shipped matcher is asymmetric, and the asymmetry is the whole instrument
here (``FILTER_PANEL_JS.matchPhrase``):

    one word   -> the label's ENTIRE normalised word list must equal it
    many words -> the words must appear as a contiguous run ANYWHERE in it

That asymmetry is what makes the three zeros separable without reading anything:

* **POSITIVE CONTROLS FOR THE EQUALITY PATH** (``next``, ``reset``, ``search``,
  ``home``, ``jobs``, ``messaging``) -- ordinary page chrome whose labels are a
  single word. If none of these match on a live LinkedIn page, the single-word
  path is not working at all, and every single-word zero is MISSED rather than
  ABSENT. **This is the control the banking of ``N 83`` depends on**, because
  ``locations`` is a single-word term and rides that exact path.
* **A NEGATIVE CONTROL** (``school anise``) -- ``menus.py``'s scar shape, a
  phrase this page cannot contain. A nonzero here means the matcher is
  saluting and nothing may be banked off any count.
* **CHROME PRESENCE** (``all filters``, ``show results``) -- multi-word, so
  containment finds them inside a decorated label. LinkedIn keeps most people
  filters behind an **All filters** button. If that control is drawn, the twelve
  zeros are ABSENT-BEHIND-A-PRESS, which this wave may not resolve because
  pressing it is a press. If it is NOT drawn, the page has no search chrome and
  the zeros are UNDRAWN.
* **A CONSISTENCY CHECK** (``locations filter``) -- ``locations`` matched by
  whole-label equality, so no control's label can also be ``locations filter``.
  A nonzero here would mean a SECOND control and would undercut the reading.
* **THE SUSPECT RE-MEASURED** (``actively hiring``) -- it read 2 on a people
  page, it is multi-word so it matches by containment anywhere in the document,
  and it is a jobs-side phrase. Carried so its count is on the record next to
  the controls rather than alone.

## THE HIDDEN-TEXT HAZARD, AND WHY THE ASYMMETRY BOUNDS IT

``label = getAttribute("aria-label") || textContent``, and ``textContent`` is
unconditional -- it ignores ``aria-hidden``, ``display:none`` and clip-styling.
So hidden text CAN join a label. Nothing but integers crosses the boundary, so
this is a correctness hazard and not a disclosure one.

**IT INFLATES CONTAINMENT MATCHES AND CANNOT INFLATE EQUALITY MATCHES.** Hidden
text only ever ADDS words; adding a word to a label breaks ``words.length === 1``
and makes a single-word term stop matching. So the hazard pushes multi-word
counts UP and single-word counts DOWN -- it can manufacture a false ``actively
hiring``, and it cannot manufacture a false ``locations``. That is why the row
this wave banks is a single-word one, and it is measured below rather than
assumed: if the equality controls fire, the path is live.

## BOUNDS

Reads only. One navigation per load to a literal module constant, the shipped
reader, nothing pressed, nothing typed, no scroll, no new script. Attach mode
only. Integers out; no label, no address, no exception text.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import config, dom, search_results  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: ``(phrase, what it is for)``. Order is this probe's own; the index handed to
#: the page is the position here. Every phrase is normalised already --
#: lowercase, single-spaced, a-z0-9 -- as the shipped matcher requires.
#:
#: NONE OF THESE IS A PERSON, an employer, a school or a place. They are UI
#: chrome words and the repo's own synthetic scar phrase.
PROBE_PHRASES: tuple[tuple[str, str], ...] = (
    ("next", "equality positive control -- ordinary chrome"),
    ("reset", "equality positive control -- ordinary chrome"),
    ("search", "equality positive control -- ordinary chrome"),
    ("home", "equality positive control -- ordinary chrome"),
    ("jobs", "equality positive control -- ordinary chrome"),
    ("messaging", "equality positive control -- ordinary chrome"),
    ("school anise", "NEGATIVE control -- must read 0"),
    ("all filters", "chrome presence -- the modal holding the other twelve"),
    ("show results", "chrome presence -- the filter panel's submit"),
    ("locations filter", "consistency check against the equality match"),
    ("actively hiring", "the suspect, re-measured"),
    ("locations", "the candidate for banking, re-measured"),
)


def say(line: str = "") -> None:
    print(line, flush=True)


async def one_load(page, url: str, surface: str) -> dict:
    """Navigate once and ask the SHIPPED reader a different question."""
    landed = await BROWSER.goto(page, url)
    raw = await dom.read_search_filters(
        page,
        phrases=[[phrase, index] for index, (phrase, _why) in enumerate(PROBE_PHRASES)],
        term_count=len(PROBE_PHRASES),
        html="",
    )
    source = raw if isinstance(raw, dict) else {}
    counts = source.get("counts")
    counts = list(counts) if isinstance(counts, (list, tuple)) else []
    # Integers only, the way the shipped readers do it -- never int(), which
    # would put a refused string into its own exception message.
    safe = []
    refused = 0
    for value in counts:
        number = search_results._as_int(value)
        if number is None:
            refused += 1
            number = 0
        safe.append(number)
    return {
        "surface": surface,
        "landed_where_it_was_sent": landed.rstrip("/") == url.rstrip("/"),
        "counts": safe,
        "values_refused": refused,
        "controls_seen": search_results._as_int(source.get("controls")) or 0,
        "matched_controls": search_results._as_int(source.get("matched_controls")) or 0,
        "unmatched_controls": search_results._as_int(source.get("unmatched_controls")) or 0,
        "empty_labels": search_results._as_int(source.get("empty_labels")) or 0,
    }


def _report(reading: dict) -> None:
    say(f"  landed where sent : {reading['landed_where_it_was_sent']}")
    say(
        "  controls=%d matched=%d unmatched=%d empty=%d refused=%d"
        % (
            reading["controls_seen"],
            reading["matched_controls"],
            reading["unmatched_controls"],
            reading["empty_labels"],
            reading["values_refused"],
        )
    )
    counts = reading["counts"]
    for index, (phrase, why) in enumerate(PROBE_PHRASES):
        count = counts[index] if index < len(counts) else -1
        words = len(phrase.split())
        path = "equality " if words == 1 else "contain  "
        say(f"    {count:>3}  {path} {phrase:<18} {why}")


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--loads", type=int, default=2)
    parser.add_argument(
        "--out", default=str(REPO / "_state" / "people-search-chrome-diagnosis.json")
    )
    args = parser.parse_args()

    if not config.CDP_ATTACH:
        say("REFUSING: LINKEDIN_CDP_ATTACH is not set. This probe attaches only.")
        return 2

    record = {"taken_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "readings": [],
              "phrases": [list(p) for p in PROBE_PHRASES]}
    try:
        await BROWSER.start()
    except Exception as exc:  # noqa: BLE001 - type only
        say(f"COULD NOT ATTACH: {type(exc).__name__}")
        return 2

    # OUR tab, held so the finally can close it. **THE PAGE, NEVER THE
    # CONTEXT** -- in attach mode the context is the operator's signed-in
    # Chrome. A probe that leaves its tab behind adds a target every later
    # attach must enumerate.
    tab = None
    try:
        async with BROWSER.session() as page:
            tab = page
            for trial in range(1, args.loads + 1):
                say(f"LOAD {trial} -- people search, probe vocabulary")
                reading = await one_load(
                    page, search_results.PEOPLE_SEARCH_URL, "people_search"
                )
                reading["trial"] = trial
                record["readings"].append(reading)
                _report(reading)
                say()
            say("CONTROL -- the feed, same probe vocabulary")
            control = await one_load(page, config.FEED_URL, "feed")
            control["trial"] = 0
            record["readings"].append(control)
            _report(control)
            say()
    except Exception as exc:  # noqa: BLE001 - type only
        say(f"PROBE FAILED: {type(exc).__name__}")
        record["error_type"] = type(exc).__name__
        return 1
    finally:
        if tab is not None and not tab.is_closed():
            await tab.close()
        await BROWSER.stop()

    path = pathlib.Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    say(f"raw reading written under {path.parent.name}/ (gitignored)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
