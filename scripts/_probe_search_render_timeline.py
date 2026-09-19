"""WHAT DOES THE JOB-SEARCH PAGE NEED BEFORE ITS RESULTS ARE IN THE DOM?

ONE QUESTION, ONE PAGE LOAD, WATCHED OVER TIME.

``scripts/_probe_job_search_filter_params.py`` measured
``/jobs/search/?keywords=<K>`` seven times and got EXACTLY SEVEN job cards on
every load -- baseline, negative control, and five loads whose filters must
have moved the result set if LinkedIn honoured them. A number that does not
move under an input that should move it is a number about the INSTRUMENT.

Two facts were then established on that same surface:

     9   anchors on the page match ``/jobs/view/``
     7   records ``dom.harvest_linked_cards`` returns with ``dom.JOB_HREF``
    25   HREFS IN THE WHOLE DOCUMENT

**THE 25 IS THE FINDING, NOT THE 9-VERSUS-7.** A LinkedIn search results page
carrying twenty-five links in total has not finished drawing, and every count
taken off it inherits that. Tuning the regex against a page in that state
would fit a pattern to a shell.

So this does not tune anything. It takes ONE load and watches it.

## The four hypotheses it exists to separate

    1  READ TOO EARLY      ``BROWSER.goto`` returns before the client finishes.
                           Would show as href count RISING with time.
    2  IFRAME              the results live in a child frame, so a main-frame
                           read cannot see them at all. Would show as a frame
                           whose own href count exceeds the main frame's.
    3  VIRTUALISED / LAZY  the list needs a scroll or an intersection before
                           it is mounted.
    4  SHELL PLUS FETCH    the served document is a shell and the rows arrive
                           on a fetch the page makes afterwards.

**HYPOTHESIS 3 IS NOT TESTED HERE AND THAT IS DELIBERATE.** This package's
readers do not scroll, and a scroll is a DIFFERENT PERMISSION from a read --
it is an interaction with a surface that counts impressions. This probe reports
whether the evidence points that way and stops there. Saying CANNOT TELL and
naming the measurement that would settle it is the honest end of a read-only
instrument; performing the interaction to get a nicer verdict is not.

## Bounds

**ONE ADDRESS, A MODULE-LEVEL CONSTANT** (:data:`SEARCH_URL`), navigated ONCE.
A second navigation would answer a different question -- the whole point is
watching a SINGLE load age. ``tests/test_navigation_is_never_derived.py``
scans this file like any other, on both of its sinks.

**READS ONLY.** One ``goto``, then locator counts, ``page.content()``,
``dom.read_main_text`` and the two shipped harvests. Nothing clicked, nothing
filled, nothing scrolled, no new ``page.evaluate`` -- the two harvest calls run
the package's own committed script, which is not the same thing as this file
injecting one.

**IT PRINTS NO CARD TEXT.** A job card names an EMPLOYER and a TITLE, and both
are third parties who did not agree to appear in a transcript. Counts, lengths,
a redacted frame path and the ``dom.JOB_HREF`` pattern. No title, no company,
no job id, no href. See :func:`_redact`, which is an allowlist for exactly the
reason its sibling in ``_probe_job_search_filter_params.py`` is one.

Run:  venv/Scripts/python.exe scripts/_probe_search_render_timeline.py
Writes: ``_audit/_scratch/_probe-search-render.txt`` (that directory is
gitignored unconditionally -- ``.gitignore``: ``_audit/_scratch/``).
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: THE ONE ADDRESS. A module-level literal, written out in full: there is
#: nothing here for a landed url to reach into. This is the exact spelling the
#: seven-load probe measured, so this timeline and that finding are about the
#: same page.
SEARCH_URL = "https://www.linkedin.com/jobs/search/?keywords=node.js+developer"

#: Where the findings land.
OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "_audit"
    / "_scratch"
    / "_probe-search-render.txt"
)

#: Path fragments that mean LinkedIn bounced the visit. Matched against the
#: landed url inside a comparison, which is the one thing a probe may do with
#: a navigation-derived value.
WALL_MARKERS = ("/login", "/checkpoint", "/authwall", "/uas/login")

#: THE TIMELINE. Seconds to sleep BEFORE each sample, so the cumulative marks
#: are t=0, +2, +5, +10 from the moment ``goto`` returned.
SAMPLE_SLEEPS_S: tuple[float, ...] = (0.0, 2.0, 3.0, 5.0)

#: The bounded ``networkidle`` wait taken after the timeline. Bounded because
#: an unbounded one turns "did it settle" into "how long did you wait".
NETWORKIDLE_TIMEOUT_MS = 10_000

#: The anchor shape the ``dom.JOB_HREF`` diagnosis counts.
JOB_VIEW_ANCHOR = 'a[href*="/jobs/view/"]'

#: Every anchor with an address at all.
ANY_ANCHOR = "a[href]"

#: PLAUSIBLE RESULTS-LIST CONTAINERS AND ROW MARKERS, counted and never read.
#: Roles and simple CSS only. The point of the list is that a page can hold its
#: rows in something that is not an ``<a href>`` -- a clickable div carrying
#: ``data-job-id`` is a row an href census cannot see, and a total of 25 hrefs
#: beside a large ``[data-job-id]`` count would mean something completely
#: different from 25 hrefs beside a zero.
CONTAINER_SELECTORS: tuple[tuple[str, str], ...] = (
    ("main", "main"),
    ("role=list", '[role="list"]'),
    ("role=listitem", '[role="listitem"]'),
    ("ul", "ul"),
    ("li", "li"),
    ("[data-job-id]", "[data-job-id]"),
    ("[data-occludable-job-id]", "[data-occludable-job-id]"),
    ("[data-view-name]", "[data-view-name]"),
    ("[data-sdui-component]", "[data-sdui-component]"),
    (".scaffold-layout__list", ".scaffold-layout__list"),
    (".jobs-search-results-list", ".jobs-search-results-list"),
    (".job-card-container", ".job-card-container"),
    ("iframe", "iframe"),
    ("button", "button"),
)

#: PATH SEGMENTS THIS FILE WILL PRINT VERBATIM. **A MEMBERSHIP LIST, NOT A
#: BLOCKLIST**, which is the whole of :func:`_redact`'s argument: a segment
#: nobody anticipated cannot print itself by being unrecognised. No entry here
#: contains a digit, so no digit run can reach the report through it, and no
#: entry is a member slug, so no identity can.
PATH_WORDS_PRINTABLE: frozenset[str] = frozenset(
    {
        "jobs", "search", "search-results", "collections", "view", "feed",
        "in", "company", "school", "help", "legal", "login", "checkpoint",
        "uas", "authwall", "psettings", "mynetwork", "messaging",
        "notifications", "blank", "srp", "static", "sw", "csp", "recaptcha",
        "anchor", "aframe", "bframe", "api", "html", "container", "frame",
        "iframe", "embed", "widget", "widgets", "pixel", "beacon", "sync",
        "silent", "auth", "oauth", "px", "ads", "ad", "pagead", "seo",
        "cse", "bin", "counter", "js", "css", "images", "media", "li",
        "voyager", "lite", "cap", "wp", "sc", "cdn", "share", "dst",
    }
)

#: Schemes safe to print. Same rule: membership.
SCHEMES_PRINTABLE: frozenset[str] = frozenset(
    {"", "http", "https", "about", "blob", "data", "chrome-extension",
     "javascript", "file"}
)

#: Every line the report carries, printed and written.
LINES: list[str] = []


def _redact(url: str) -> str:
    """A frame's SCHEME AND PATH, rendered so it can identify nobody.

    **THIS FUNCTION'S NAME IS A CONTRACT, NOT A LABEL.**
    ``tests/test_navigation_is_never_derived.py`` stops its taint walk at a
    call to a function named ``_redact`` or ``_shape_of``, matched by NAME
    across every module it scans. Naming a function this makes a promise to
    every other check in this package -- "the result carries none of its
    input" -- and that file records what happens when the promise is made on
    the strength of a name and nothing verifies it: an entry sat in
    ``_SANITISERS`` for a day while the function it vouched for had no slug
    rule at all, and a member's public identity was printed by the code
    standing between a probe and a leak.

    NOTHING OUTSIDE THIS FILE VERIFIES THIS ONE, exactly as in
    ``_probe_job_search_filter_params.py``. It is therefore built the one way
    that does not need an auditor: **membership, not absence.** A segment
    prints itself only if it is in :data:`PATH_WORDS_PRINTABLE`; a scheme only
    if it is in :data:`SCHEMES_PRINTABLE`. A job id, a geo id, a tracking blob
    or a vanity slug cannot print by being unrecognised, which is precisely
    how a blocklist leaks.

    **NO HOST AND NO QUERY, EVER.** The question this probe asks about a frame
    is answered by its path shape and by whether it is same-origin with the
    main frame, and the second of those is reported as a BOOLEAN taken inside
    a comparison rather than as two strings placed side by side.
    """
    parts = urlsplit(str(url or ""))
    scheme = parts.scheme if parts.scheme in SCHEMES_PRINTABLE else "<scheme>"
    segments = [seg for seg in str(parts.path or "").split("/") if seg]
    if not segments:
        return "%s:/" % scheme
    rendered = [
        seg if seg in PATH_WORDS_PRINTABLE else "<withheld %d chars>" % len(seg)
        for seg in segments
    ]
    return "%s:/%s" % (scheme, "/".join(rendered))


def say(line: str) -> None:
    """One line, to stdout and to the report. Never handed a tainted value."""
    LINES.append(line)
    print(line)


async def _count(owner, selector: str) -> int:
    """``count()`` on a locator, or -1 if the frame would not answer.

    A DETACHED OR CROSS-ORIGIN FRAME RAISES, and a probe that dies on an ad
    iframe would report nothing about the page it came for. -1 is printed as
    ``n/a`` and is never mistaken for a zero.
    """
    try:
        return int(await owner.locator(selector).count())
    except Exception:
        return -1


def _num(value: int) -> str:
    return "n/a" if value < 0 else str(value)


async def _sample(page, label: str, elapsed_s: float) -> dict:
    """One row of the timeline. COUNTS AND LENGTHS ONLY."""
    total_hrefs = await _count(page, ANY_ANCHOR)
    job_hrefs = await _count(page, JOB_VIEW_ANCHOR)
    main_text = await dom.read_main_text(page)
    html = await page.content()

    frames = list(page.frames)
    others = [frame for frame in frames if frame is not page.main_frame]
    frame_rows: list[tuple[str, int, bool]] = []
    for frame in others:
        frame_hrefs = await _count(frame, ANY_ANCHOR)
        same_origin = urlsplit(str(frame.url)).netloc == urlsplit(str(page.url)).netloc
        frame_rows.append((_redact(frame.url), frame_hrefs, same_origin))

    return {
        "label": label,
        "elapsed_s": round(elapsed_s, 1),
        "total_hrefs": total_hrefs,
        "job_hrefs": job_hrefs,
        "main_text_len": len(main_text),
        "content_len": len(html),
        "frames": len(frames),
        "frame_rows": frame_rows,
    }


def _report_timeline(samples: list) -> None:
    say("")
    say("=== TIMELINE OVER ONE LOAD")
    say("    every row is the SAME page, read again N seconds later.")
    say("")
    header = "%-24s %7s %8s %11s %10s %12s %7s" % (
        "sample", "t (s)", "a[href]", "/jobs/view/", "len(main)",
        "len(content)", "frames",
    )
    say("    " + header)
    say("    " + "-" * len(header))
    for row in samples:
        say(
            "    %-24s %7s %8s %11s %10s %12s %7s"
            % (
                row["label"],
                row["elapsed_s"],
                _num(int(row["total_hrefs"])),
                _num(int(row["job_hrefs"])),
                row["main_text_len"],
                row["content_len"],
                row["frames"],
            )
        )


def _report_frames(samples: list) -> int:
    """Non-main frames of the LAST sample. Returns the largest href count."""
    say("")
    say("=== FRAMES AT THE LAST SAMPLE")
    last = samples[-1]
    rows = list(last["frame_rows"])
    main_hrefs = int(last["total_hrefs"])
    if not rows:
        say("    ZERO non-main frames. The main frame is the whole document.")
        return -1
    say("    %-46s %8s %12s" % ("path (scheme + allowlisted segments)",
                                "a[href]", "same-origin"))
    say("    " + "-" * 68)
    best = -1
    for path, hrefs, same_origin in rows:
        say("    %-46s %8s %12s"
            % (path, _num(hrefs), "yes" if same_origin else "no"))
        best = max(best, hrefs)
    say("")
    say("    largest non-main frame href count: %s" % _num(best))
    say("    main frame href count:             %s" % _num(main_hrefs))
    say(
        "    a frame carries MORE than the main frame: %s"
        % ("YES" if best > main_hrefs else "no")
    )
    return best


async def _report_channels(page) -> tuple:
    """The two harvest channels side by side. Returns the four numbers."""
    say("")
    say("=== THE TWO CHANNELS, ON THE PAGE AS IT NOW STANDS")
    say("    dom.JOB_HREF = %r" % dom.JOB_HREF)
    anchors = await _count(page, JOB_VIEW_ANCHOR)
    census = await dom.harvest_census(page, href_pattern=dom.JOB_HREF, max_items=200)
    records = await dom.harvest_linked_cards(
        page, href_pattern=dom.JOB_HREF, max_items=200, max_chars=300
    )
    keyed = census.get("anchors_keyed")
    dropped = census.get("dropped_empty_text")
    keyed_n = -1 if keyed is None else int(keyed)
    dropped_n = -1 if dropped is None else int(dropped)
    say("")
    say("    DOM channel     a[href*=/jobs/view/] elements : %s" % _num(anchors))
    say("    walk channel    distinct keyed anchors seen   : %s" % _num(keyed_n))
    say("    walk channel    rows refused for empty text   : %s" % _num(dropped_n))
    say("    harvest         records returned              : %d" % len(records))
    say("")
    if anchors >= 0:
        say("    drop across the two channels: %d anchors -> %d records"
            % (anchors, len(records)))
    else:
        say("    drop across the two channels: DOM channel did not answer")
    return anchors, keyed_n, dropped_n, len(records)


async def _report_containers(page) -> dict:
    say("")
    say("=== PLAUSIBLE RESULTS CONTAINERS AND ROW MARKERS (counts only)")
    counts: dict = {}
    for label, selector in CONTAINER_SELECTORS:
        found = await _count(page, selector)
        counts[label] = found
        say("    %-28s %s" % (label, _num(found)))
    return counts


def _verdicts(
    samples: list,
    idle_reached: bool,
    best_frame_hrefs: int,
    anchors: int,
    records: int,
    counts: dict,
) -> None:
    first = int(samples[0]["total_hrefs"])
    last = int(samples[-1]["total_hrefs"])
    span = float(samples[-1]["elapsed_s"])
    main_hrefs = last
    rows_marked = max(
        counts.get("[data-job-id]", -1),
        counts.get("[data-occludable-job-id]", -1),
        counts.get(".job-card-container", -1),
        counts.get("role=listitem", -1),
        counts.get("li", -1),
    )
    say("")
    say("=== WHAT MAKES IT RENDER")
    say("")

    # -- 1 -----------------------------------------------------------------
    if last > first:
        say(
            "    1 READ TOO EARLY .............. SUPPORTED. Total hrefs rose "
            "%d -> %d over %.1f s on one load." % (first, last, span)
        )
    else:
        say(
            "    1 READ TOO EARLY .............. REFUTED. Total hrefs were %d "
            "at t=0 and %d at t=%.1f s -- no growth, and goto had already "
            "spent its own settle before t=0." % (first, last, span)
        )
    say(
        "                                    networkidle within %d ms: %s"
        % (NETWORKIDLE_TIMEOUT_MS, "REACHED" if idle_reached else "TIMED OUT")
    )

    # -- 2 -----------------------------------------------------------------
    if best_frame_hrefs > main_hrefs:
        say(
            "    2 IFRAME ...................... SUPPORTED. A non-main frame "
            "carries %d hrefs against the main frame's %d."
            % (best_frame_hrefs, main_hrefs)
        )
    elif best_frame_hrefs < 0:
        say(
            "    2 IFRAME ...................... REFUTED. Zero non-main "
            "frames at the last sample; %d frames total."
            % int(samples[-1]["frames"])
        )
    else:
        say(
            "    2 IFRAME ...................... REFUTED. The largest "
            "non-main frame carries %d hrefs against the main frame's %d."
            % (best_frame_hrefs, main_hrefs)
        )

    # -- 3 -----------------------------------------------------------------
    say(
        "    3 VIRTUALISED / LAZY .......... CANNOT TELL BY CONSTRUCTION. "
        "This probe does not scroll, and a scroll is a different permission "
        "from a read."
    )
    say(
        "                                    Directional evidence: row "
        "markers present = %s against a[href*=/jobs/view/] = %s. THE "
        "MEASUREMENT THAT WOULD SETTLE IT: one scroll of the results column, "
        "or one IntersectionObserver trigger, with these same counts retaken "
        "-- and it needs a permission this slice does not hold."
        % (_num(rows_marked), _num(anchors))
    )

    # -- 4 -----------------------------------------------------------------
    if last > first:
        say(
            "    4 SHELL PLUS FETCH ............ SUPPORTED. The document grew "
            "after load (hrefs %d -> %d), which is a later fetch filling it."
            % (first, last)
        )
    elif rows_marked > records and rows_marked > 0:
        say(
            "    4 SHELL PLUS FETCH ............ REFUTED for the observed "
            "window. Rows ARE mounted -- %s row markers against %d harvested "
            "records -- so the content arrived; it is the href census that "
            "cannot see it." % (_num(rows_marked), records)
        )
    else:
        say(
            "    4 SHELL PLUS FETCH ............ CANNOT TELL. The document "
            "did not grow (hrefs flat at %d over %.1f s) and carries %s row "
            "markers, so nothing here distinguishes 'the fetch already landed "
            "before t=0' from 'the fetch never happened'. THE MEASUREMENT "
            "THAT WOULD SETTLE IT: a response listener over the same single "
            "load, counting job-bearing XHR responses and their arrival times "
            "against these sample marks -- a read, and buildable without any "
            "new permission." % (last, span, _num(rows_marked))
        )


def _flush() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(LINES) + "\n", encoding="ascii")
    print("")
    print("    written to _audit/_scratch/%s" % OUT_PATH.name)


async def main() -> None:
    say("=== WHAT MAKES THE JOB SEARCH RESULTS ACTUALLY RENDER?")
    say("    ONE load of /jobs/search/?keywords=<K>, read repeatedly.")
    say("    counts, lengths and redacted frame paths -- no card text.")

    try:
        await BROWSER.start()
    except Exception as exc:
        say("")
        say("    COULD NOT START THE BROWSER: %s" % type(exc).__name__)
        say("    If that is ProfileLockedError, another process holds the")
        say("    cross-process profile lock. THAT IS THE RESULT. Not retried.")
        _flush()
        return

    try:
        async with BROWSER.session() as page:
            started = time.monotonic()
            landed = await BROWSER.goto(page, SEARCH_URL)
            walled = any(marker in landed for marker in WALL_MARKERS)
            settle = BROWSER.last_settle
            say("")
            say(
                "    goto settle branch: %s after %s ms (configured %s ms)"
                % (
                    settle.get("branch"),
                    settle.get("settled_ms"),
                    settle.get("settle_ms_configured"),
                )
            )
            if walled:
                say("")
                say("    AUTH WALL. LinkedIn bounced the visit, so NOTHING about")
                say("    the results list was measured. Session expired or signed")
                say("    out. That is the result; no retry.")
                return

            samples: list = []
            marks = ("t=0 (goto returned)", "t=+2s", "t=+5s", "t=+10s")
            for sleep_s, label in zip(SAMPLE_SLEEPS_S, marks):
                if sleep_s:
                    await asyncio.sleep(sleep_s)
                samples.append(await _sample(page, label, time.monotonic() - started))

            try:
                await page.wait_for_load_state(
                    "networkidle", timeout=NETWORKIDLE_TIMEOUT_MS
                )
                idle_reached = True
            except Exception:
                idle_reached = False
            samples.append(
                await _sample(
                    page,
                    "networkidle %s" % ("reached" if idle_reached else "timed out"),
                    time.monotonic() - started,
                )
            )

            _report_timeline(samples)
            best_frame = _report_frames(samples)
            anchors, _keyed, _dropped, records = await _report_channels(page)
            counts = await _report_containers(page)
            _verdicts(samples, idle_reached, best_frame, anchors, records, counts)
    except Exception as exc:
        say("")
        say("    THE RUN STOPPED: %s" % type(exc).__name__)
        say("    Nothing beyond this line was measured.")
    finally:
        await BROWSER.stop()
        _flush()


# GUARDED: importing a script must not DO anything.
# ``tests/test_scripts_are_import_safe.py`` asserts that for every script here.
if __name__ == "__main__":
    asyncio.run(main())
