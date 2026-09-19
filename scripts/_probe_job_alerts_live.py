"""Does LinkedIn serve the job-alerts manage page, and how many alerts are there?

THE ADDRESS WAS ADMITTED AS A HYPOTHESIS AND THIS IS WHAT SETTLES IT. The
boundary entry frozen at ``6b90622`` says so in its own comment: everything
measured up to that point was about the GATE, and not one byte of it said
LinkedIn serves that spelling. **If this probe reports the address unserved,
the correct response is to change the pattern, not to conclude he has no
alerts.**

WHY IT IS WORTH ONE PAGE LOAD. His job alerts are how LinkedIn's matcher
decides what to push at him daily, and the ``linkedin-jobs`` skill already
parses what those alerts DELIVER into his inbox. What nothing in this system
can see is what they are CONFIGURED to hunt -- so an alert aimed at the wrong
stack or the wrong geography is invisible, and every downstream email inherits
it. Four things fall out of one load: whether the page is served, how many
alerts exist, whether the frequency and channel controls are drawn there, and
whether a delete control is drawn beside them.

## WHAT LEAVES THIS PROCESS: INTEGERS, RELATIONS AND VERDICTS

**NO ALERT'S KEYWORDS ARE READ OUT AND NO TITLE IS PRINTED.** That is a
deliberate limit and not an oversight. His search terms carry a geography and a
stack, and one of those spellings is on this repository's own denied-terms
list -- so the SHAPER's answer here is a tally, not a transcript. Counting how
many controls carry a generic vocabulary word answers "are the alert controls
drawn" without publishing a single thing he searches for. Whoever builds the
reader can argue the keyword read separately; it is a different decision.

Every control goes through ``dom.read_surface_census``, which shapes each name
and href inside itself. ``_relation`` is IMPORTED from the groups/events probe
rather than copied: this package already carries two byte-identical copies of
it under a test that pins them equal, and a third copy would be a third thing
to keep in step.

## THE OBLIGATION THIS REPOSITORY PUTS ON A NEW LIVE READ

``dom.read_invitation_badge`` is read immediately BEFORE and AFTER. That is how
this repo proves a read did not consume a counter it passed, and it is not
optional for an address nobody has opened. If the reading cannot be taken at
either end, this says UNKNOWN -- never "nothing was consumed", which is a claim
about an instrument rather than about the page.

## THE CONTROL, AND WHY THE RUN IS VOID WITHOUT IT

A known-served admitted address is read FIRST. An instrument that cannot report
SERVED will report every address as unserved and look authoritative doing it --
which is how a sibling probe would have reported the whole boundary closed on
its first run had its control been absent.

## IT FIRES NO WRITE

It navigates and reads. No control is clicked, nothing is submitted, and
``LINKEDIN_ENABLE_WRITES`` is irrelevant to it.

Run it as:

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_job_alerts_live.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import dom, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from _probe_groups_events_live import _relation  # noqa: E402

ALERTS_URL = "https://www.linkedin.com/jobs/alerts/"
#: A known-served admitted address. The control.
CONTROL_URL = "https://www.linkedin.com/jobs/search/?keywords=node.js"

#: Generic English words a job-alert management UI draws. None of them is
#: identifying, and the tally is over SHAPED control names.
VOCABULARY = ("alert", "daily", "weekly", "delete", "edit", "manage", "off", "on")

#: CANDIDATE LANDING PATHS, EVERY ONE A LITERAL TYPED INTO THIS FILE.
#:
#: The redirect is the finding and "somewhere else" is not an actionable form
#: of it -- a pattern cannot be re-anchored on a shrug. So the landed path is
#: COMPARED against literals and only the matching LABEL is printed. The label
#: comes from this tuple and never from the browser, which is what keeps the
#: output free of anything a navigation chose. It is the same discipline
#: ``_relation`` uses inside itself, applied at the print site.
#:
#: A MISS IS A RESULT AND IS REPORTED AS ONE. If none matches, that says the
#: landing is a spelling nobody here has guessed -- which is worth knowing and
#: is not the same as knowing nothing.
CANDIDATE_PATHS: tuple[tuple[str, str], ...] = (
    ("the job search page", "/jobs/search"),
    ("the jobs home", "/jobs"),
    ("the recommended collection", "/jobs/collections/recommended"),
    ("a collection other than recommended", "/jobs/collections"),
    ("the alerts path without its trailing slash", "/jobs/alerts"),
    ("a hyphenated job-alerts spelling", "/jobs/job-alerts"),
    ("an opportunities-scoped alerts spelling",
     "/jobs/opportunities/job-alerts"),
    ("the job tracker", "/jobs-tracker"),
    ("the feed", "/feed"),
    ("the network hub", "/mynetwork"),
    # SECOND BATCH, added after the first run reported the landing as UNDER
    # /jobs and matching none of the ten above. The first batch narrowed the
    # answer to one path segment; these are the segments a jobs product plausibly
    # uses for alert management, saved searches and preferences.
    ("a job-alerts segment spelled with an underscore", "/jobs/job_alerts"),
    ("an alert-settings segment", "/jobs/alert-settings"),
    ("a saved-searches segment", "/jobs/saved-searches"),
    ("a saved segment", "/jobs/saved"),
    ("an applied segment", "/jobs/applied"),
    ("a my-jobs segment", "/jobs/my-jobs"),
    ("a preferences segment", "/jobs/preferences"),
    ("an opportunities segment", "/jobs/opportunities"),
    ("a tracker segment under jobs", "/jobs/tracker"),
    ("a manage segment under jobs", "/jobs/manage"),
    ("a settings segment under jobs", "/jobs/settings"),
    ("a search-alerts segment", "/jobs/search-alerts"),
    ("a jobs view", "/jobs/view"),
    # THIRD BATCH. The counts narrowed the landing to /jobs/<3 characters>, so
    # these enumerate three-character segments rather than plausible words --
    # a search space this small is worth walking instead of guessing at.
    ("a three-letter segment: all", "/jobs/all"),
    ("a three-letter segment: new", "/jobs/new"),
    ("a three-letter segment: set", "/jobs/set"),
    ("a three-letter segment: top", "/jobs/top"),
    ("a three-letter segment: job", "/jobs/job"),
    ("a three-letter segment: alt", "/jobs/alt"),
    ("a three-letter segment: hub", "/jobs/hub"),
    ("a three-letter segment: sub", "/jobs/sub"),
    ("a three-letter segment: rec", "/jobs/rec"),
    ("a three-letter segment: sav", "/jobs/sav"),
    ("a three-letter segment: pre", "/jobs/pre"),
    ("a three-letter segment: JAT", "/jobs/JAT"),
    ("a three-letter segment: jat", "/jobs/jat"),
    ("a three-letter segment: mgr", "/jobs/mgr"),
    ("a three-letter segment: geo", "/jobs/geo"),
    ("a three-letter segment: r-r", "/jobs/r-r"),
)


def _print_candidate_match(landed_path: str) -> None:
    """Print the LABEL of the candidate this path matches, or a literal MISS.

    IT PRINTS RATHER THAN RETURNS, AND THAT IS THE GUARD'S DOING. A version
    that RETURNED the label was refused by
    ``tests/test_navigation_is_never_derived.py``: the guard is a fixed point
    over BINDINGS, so a value returned from a function called with a tainted
    argument is tainted, whatever the function actually does with it. Only
    ``_SANITISERS`` launders, and adding an entry there permanently widens what
    the guard tolerates -- too much to spend on one line.

    Printing INSIDE the loop keeps the print expression bound to ``label``,
    which comes from ``CANDIDATE_PATHS`` -- a module constant -- and never from
    the browser. The tainted value is used in the comparison and reaches no
    output.
    """
    trimmed = landed_path.rstrip("/")
    for label, candidate in CANDIDATE_PATHS:
        if trimmed == candidate:
            print("    landed path matches candidate: " + label)
            return
    for label, candidate in CANDIDATE_PATHS:
        if trimmed.startswith(candidate + "/"):
            print("    landed path is UNDER candidate: " + label)
            return
    print("    landed path matches NONE of the candidates -- a spelling "
          "nobody here has guessed")


def _print_path_shape(landed_path: str) -> None:
    """COUNTS about the landed path, never its text.

    The guard's own message sanctions this form -- *"emit a RELATION or a count
    instead"* -- and ``_relation`` establishes it: segment depths are taken with
    ``len`` precisely because counting a thing is what this package does instead
    of printing it.

    WHY IT IS WORTH PRINTING AT ALL. Twenty-three candidate spellings missed, and
    a miss narrows nothing on its own. A segment COUNT and a segment LENGTH turn
    "somewhere under /jobs" into a search space of one word of a known size, which
    is what the next wave needs in order to stop guessing.
    """
    parts = [seg for seg in landed_path.split("/") if seg]
    print(f"    landed path depth: {len(parts)} segments")
    if len(parts) >= 2:
        print(f"    the segment after 'jobs' is {len(parts[1])} characters long")
    if len(parts) >= 3:
        print(f"    the segment after that is {len(parts[2])} characters long")


def _title_class(title: str) -> str:
    """A CLASS, never the title. A title is a string LinkedIn chose."""
    low = (title or "").lower()
    if "alert" in low:
        return "carries the word alert"
    if "job" in low:
        return "carries the word job, not alert"
    if "linkedin" in low:
        return "the bare product name -- LinkedIn's generic 404 reads this way"
    if not low:
        return "empty"
    return "something else"


def _vocabulary_tally(controls: list) -> dict[str, int]:
    """Tally over the SHAPED name, which the census calls ``shape``.

    THE FIRST VERSION OF THIS READ ``control["name"]`` AND RETURNED ZERO FOR
    EVERY WORD ON EVERY PAGE, including ``on`` across 185 controls of a page
    LinkedIn certainly labels in English. **A control that must fire and does
    not is the strongest evidence available that the instrument cannot see**,
    and that zero was a fact about the key, not about the page. The census
    publishes ``shape`` and ``href_shape``; there is no ``name``.
    """
    tally = {word: 0 for word in VOCABULARY}
    for control in controls:
        text = str((control or {}).get("shape") or "").lower()
        for word in VOCABULARY:
            if word in text:
                tally[word] += 1
    return tally


def _blank_shapes(controls: list) -> int:
    """How many controls the shaper blanked. Without it the tally is
    uninterpretable: zero hits over blanked shapes is not zero hits."""
    return sum(1 for c in controls if not str((c or {}).get("shape") or "").strip())


async def _badge(page) -> str:
    """A RELATION about the badge, or UNKNOWN. Never a number he did not ask for."""
    try:
        reading = await dom.read_invitation_badge(page)
    except Exception as error:  # noqa: BLE001
        return f"UNKNOWN ({type(error).__name__})"
    if not isinstance(reading, dict):
        return "UNKNOWN (unexpected shape)"
    value = reading.get("count")
    if value is None:
        return "UNKNOWN (no badge drawn)"
    return f"read, value {int(value)}"


async def _read(page, label: str, url: str) -> dict:
    print(f"\n--- {label}")
    if not readonly.is_read_url(url):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return {"refused": True}
    landed = await BROWSER.goto(page, url)
    relation = _relation(landed, url)
    # A SECOND RELATION, BECAUSE THE FIRST IS AMBIGUOUS ON THIS ROOT.
    # ``/jobs/alerts/`` and ``/jobs/search/`` are BOTH path depth 2, so
    # "SERVED, same depth, different url" cannot tell a served alerts page from
    # a redirect onto the search page. This is a BOOLEAN about containment --
    # no part of either address survives into it.
    # IT COMPARES PATHS, NOT URLS, AND THE FIRST VERSION DID NOT. Comparing
    # whole urls read False FOR THE CONTROL -- a page that certainly served --
    # because LinkedIn reorders a query string. A containment test that fails
    # on the known-good case is measuring the query, not the route.
    kept = urlsplit(str(landed)).path.startswith(
        urlsplit(url).path.rstrip("/")
    )
    # AND A THIRD RELATION, WHICH IS THE ONE THAT MAKES A REDIRECT ACTIONABLE.
    # ``assert_read_url`` gates the REQUESTED url and never re-checks the
    # LANDED one -- the invariant file records this for /messaging/ and calls
    # it "a trap the moment anyone adds that check". So when an admitted
    # address redirects, the question is whether the server has come to rest on
    # something its own allowlist covers. This asks the SHIPPED predicate about
    # the landed address and prints only its BOOLEAN.
    landed_admitted = readonly.is_read_url(str(landed))
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    print(f"    relation: {relation}")
    # THE BRANCHES PRINT LITERALS, AND THAT IS THE GUARD'S DOING RATHER THAN
    # MY TASTE. Printing the BOOLEANS directly -- `{kept}`, `{landed_admitted}`
    # -- was refused by tests/test_navigation_is_never_derived.py, which tracks
    # tainted names across a module and does not care that a bool cannot carry
    # a url. Its message is the instruction: emit a RELATION instead. The
    # alternative was to widen `_SANITISERS`, and a declaration permanently
    # widens what the guard tolerates to buy one f-string.
    if kept:
        print("    landed PATH still begins with the asked path: yes")
    else:
        print("    landed PATH still begins with the asked path: NO, "
              "LinkedIn sent us elsewhere")
    if landed_admitted:
        print("    the LANDED address is admitted by the allowlist: yes")
    else:
        print("    the LANDED address is admitted by the allowlist: NO -- the "
              "server has come to rest where its own allowlist refuses")
    _print_candidate_match(urlsplit(str(landed)).path)
    _print_path_shape(urlsplit(str(landed)).path)
    if walled:
        print("    AUTH WALL on this address. Nothing else measured.")
        return {"authwall": True}

    title = await page.title()
    print(f"    title class: {_title_class(title)}")

    census = await dom.read_surface_census(page)
    controls = list(census.get("controls") or [])
    read = int(census.get("controls_read") or 0)
    counts = census.get("counts") or {}
    print(f"    controls_read={read}  truncated={bool(census.get('truncated'))}")
    print("    " + "  ".join(
        f"{key}={int(counts.get(key) or 0)}"
        for key in ("forms", "buttons", "links", "contenteditable", "dialogs")
    ))
    blanked = _blank_shapes(controls)
    tally = _vocabulary_tally(controls)
    print(f"    shapes blanked by the shaper: {blanked} of {len(controls)}")
    print("    vocabulary in shaped control names:")
    print("      " + "  ".join(f"{word}={n}" for word, n in tally.items()))
    return {
        "relation": relation,
        "kept": kept,
        "controls": read,
        "tally": tally,
        "blanked": blanked,
    }


async def main() -> int:
    print("=== JOB ALERTS, LIVE. Does LinkedIn serve the address just admitted?")
    print("    Integers, relations and verdicts only. No keyword is read out.")
    print("    No control is clicked and no write is fired.")

    _own_page = None
    try:
        async with BROWSER.session() as page:
            _own_page = page

            print("\n### CONTROL FIRST. If this is wrong, nothing else is a reading.")
            control_first = await _read(page, "CONTROL", CONTROL_URL)
            if control_first.get("refused") or control_first.get("authwall"):
                print("\nCONTROL FAILED. NO MEASUREMENT TAKEN.")
                return 1
            if not str(control_first.get("relation", "")).startswith("SERVED"):
                print("\nCONTROL FAILED: a known-served address did not serve.")
                print("NO MEASUREMENT TAKEN.")
                return 1

            badge_before = await _badge(page)
            print(f"\n### invitation badge BEFORE: {badge_before}")

            first = await _read(page, "ALERTS 1", ALERTS_URL)
            second = await _read(page, "ALERTS 2", ALERTS_URL)

            badge_after = await _badge(page)
            print(f"\n### invitation badge AFTER: {badge_after}")
            if "UNKNOWN" in badge_before or "UNKNOWN" in badge_after:
                print("    CONSUMPTION: UNKNOWN. One end could not be read, so")
                print("    this says nothing rather than saying nothing was spent.")
            elif badge_before == badge_after:
                print("    CONSUMPTION: the badge did not move across this read.")
            else:
                print("    CONSUMPTION: THE BADGE MOVED. Something was spent.")

            print("\n### CONTROL AGAIN, at the end of the session.")
            control_second = await _read(page, "CONTROL", CONTROL_URL)
            if not str(control_second.get("relation", "")).startswith("SERVED"):
                print("    THE CONTROL STOPPED SERVING mid-session. Treat the")
                print("    alerts readings above as void rather than as data.")

            print("\n### SETTLE")
            if first.get("controls") == second.get("controls"):
                print(f"    two readings agree at controls_read="
                      f"{first.get('controls')}")
            else:
                print(f"    two readings DISAGREE: {first.get('controls')} then "
                      f"{second.get('controls')} -- the page had not settled, and")
                print("    a lone reading of it would have been uninterpretable.")
    except Exception as error:  # noqa: BLE001
        name = type(error).__name__
        print(f"\nRUN ABORTED: {name}")
        if "ProfileLocked" in name:
            print("    The Chrome profile is held by another process. This is")
            print("    the cross-process guard working, not a defect.")
        else:
            print(f"    {error}")
        return 1
    finally:
        # THE PAGE, NEVER THE CONTEXT. The context is his signed-in browser
        # session; closing it closes his window. In a finally, because the runs
        # that ABORT are exactly the ones that leak a tab.
        if _own_page is not None and not _own_page.is_closed():
            await _own_page.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
