"""FIRE the eight lane-L1 admitted-read keys and report their SHAPE, never their text.

A closed, ordered table of KEYS. Each names its census row, its address, and
its reader -- see :func:`_url_for` and :func:`_read_for` for the exact
mapping, and the docstrings of the modules those readers call
(``linkedin_server.anchors``, ``linkedin_server.chart_labels``,
``linkedin_server.creator_analytics``) for what each reading actually is.

    per_post      P G6   linkedin_creator_analytics() -- no navigation of its
                         own; the tool opens and closes its own page.
    contact       P A25  /in/me/overlay/contact-info/
    audience      P L1   /analytics/creator/audience/
    overview      P L8   /dashboard/
    articles      M C48  /in/me/recent-activity/articles/
    post_summary  M C38  /analytics/post-summary/urn:li:activity:<ID>/
                         (only with --post-id)
    followers     P L2b  /mynetwork/network-manager/people-follow/followers/
    event         N 184  /events/<ID>/ (only with --event-id)

**FOLLOWERS AND EVENT ARE ADMITTED ONLY BY THEIR OWN ``REVIEW:`` COMMITS.**
On a tree without them, ``followers`` trips the ``/follow`` forbidden
substring and ``event`` has no id-shaped pattern (only the bare ``/events/``
root). Both stay in the default selection either way: the ``is_read_url``
PRE-CHECK decides at run time, so a key the gate refuses is skipped with a
fixed line at zero page loads, and a key it admits runs. This file needs no
edit in either case.

## SELECTION IS DECIDED BEFORE THE BROWSER IS TOUCHED

:func:`_selected` is pure and takes only ``argv``. A bad ``--only``, a
``--post-id``/``--event-id`` that is not 1-20 ASCII digits, or ``--only
post_summary``/``--only event`` without its id all refuse via ``SystemExit``
at zero page loads.

## EVERY ADDRESS IS BUILT, NEVER READ OFF A PAGE

:func:`_url_for` builds every navigating key's address from a MODULE-LEVEL
CONSTANT template plus a validated digit string. Nothing here ever feeds a
landed url, an href or any other page-derived value back into a navigation.

## WHAT LEAVES THIS PROCESS

Per key: whether the shipped gate admitted it, the ``_relation`` between the
address asked for and the one landed on (a closed literal or an integer
depth -- see ``_probe_groups_events_live._relation``), and a small set of
INTEGERS and BOOLEANS from the reader named above. For ``audience``,
``overview`` and ``post_summary`` the reading also carries ``metrics``, a
list whose every member is checked against
``chart_labels.KNOWN_METRICS`` before it is printed -- anything outside
that closed vocabulary is counted in ``metrics_refused`` and never shown.
No url, no landed path, no page text, no page-drawn label and no exception
MESSAGE is ever printed -- only exception TYPE names, integers, booleans,
the closed metric words, and strings this file authored.

THE BRACKET: the CONTROL page (the jobs search the sibling probes use) is
loaded before the first key and after the last. If it does not serve, the
run is VOID and stops -- before any key, or with every reading above voided.
The invitation badge is read ON that page each time (it lives in the nav,
which a blank tab does not draw), and the consumption line compares the two.

## CAPTURES

When capture is on (the default), each navigating key's ``page.content()``
is written to the gitignored ``_state/l1-<key>.html`` -- never committed,
never printed. ``per_post`` is never captured: it opens no page of its own
to capture, and ``linkedin_creator_analytics`` already carries its own
capture discipline if one is ever wanted for that surface.

## THE ANOMALY RULE

An exception or an error envelope from ANY key stops every further page
load, the same rule ``_probe_unfired_job_detail_insights.FireAnomaly``
established for the sibling wave. The raw readings collected so far are
still written to ``_state/l1-admitted-reads-raw.json`` (gitignored), so a
stopped run can still be diagnosed from disk.

## COST

One page load per selected navigating key (``per_post`` costs the load
already inside ``linkedin_creator_analytics``, never a second one; a
GATE-REFUSED key costs zero), plus the control page twice, and nothing
pressed, typed, clicked or submitted.

Run it as::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_l1_admitted_reads_live.py \\
        [--only KEY] [--post-id DIGITS] [--event-id DIGITS] [--no-capture]
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Optional

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import anchors, chart_labels, creator_analytics, dom, readonly, server  # noqa: E402
from linkedin_server.auth import assert_not_authwall  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

# THE SHIPPED SANITISER, IMPORTED RATHER THAN COPIED. Its `main()` sits
# behind `if __name__ == "__main__":`, so importing it runs only its
# constants and defs -- the same lift `_probe_landed_address_sweep.py`
# already makes from this exact module.
from _probe_groups_events_live import _relation  # noqa: E402

# ---------------------------------------------------------------------------
# Addresses. MODULE-LEVEL CONSTANTS AND TEMPLATES ONLY -- see the module
# docstring. Every one is copied from the pattern `readonly.py` admits it
# under, not retyped from memory.
# ---------------------------------------------------------------------------

#: THE CONTROL PAGE, and the invitation badge is read ON it. Added by the lead
#: at review: the first draft read the badge on a freshly opened tab, which
#: draws no nav at all, so both readings would have been UNREADABLE and the
#: consumption line would have said UNKNOWN on every run -- a bracket that
#: cannot fail to be blind. This is the sibling probes' own control address
#: (``_probe_unfired_job_detail_insights.CONTROL_URL``), admitted, and a page
#: that serves draws the nav the badge lives in.
CONTROL_URL = "https://www.linkedin.com/jobs/search/?keywords=node.js"

CONTACT_URL = "https://www.linkedin.com/in/me/overlay/contact-info/"
AUDIENCE_URL = "https://www.linkedin.com/analytics/creator/audience/"
OVERVIEW_URL = "https://www.linkedin.com/dashboard/"
ARTICLES_URL = "https://www.linkedin.com/in/me/recent-activity/articles/"
POST_SUMMARY_URL_TEMPLATE = (
    "https://www.linkedin.com/analytics/post-summary/urn:li:activity:{}/"
)
FOLLOWERS_URL = (
    "https://www.linkedin.com/mynetwork/network-manager/people-follow/followers/"
)
EVENT_URL_TEMPLATE = "https://www.linkedin.com/events/{}/"

#: The closed set of keys this script knows. Used for --only's validation
#: and its refusal message.
KEYS: tuple[str, ...] = (
    "per_post", "contact", "audience", "overview", "articles",
    "post_summary", "followers", "event",
)

# ---------------------------------------------------------------------------
# Digit validation. groups.py's fix, restated here: str.isdigit() is True of
# Arabic-Indic, Extended Arabic-Indic and superscript digits too -- measured
# there, three scripts, all True, and int() cannot even parse the
# superscript form. The ten ASCII digits are named explicitly instead.
# ---------------------------------------------------------------------------

_ASCII_DIGITS = frozenset("0123456789")

#: groups.py's `_MAX_IDENTIFIER_DIGITS`, restated rather than imported --
#: that name is private to its own module -- and the same bound the two
#: allowlist lines this file fills (`[0-9]{1,20}`) carry. The activity and
#: event ids measured on the captures on disk are nineteen digits, so twenty
#: is one digit of headroom, not a generous margin. (The first draft of this
#: comment said "more than twice the longest id"; corrected at review.)
MAX_ID_DIGITS = 20


def _digits_or_none(value: str) -> Optional[str]:
    """``value`` if it is 1-20 ASCII digits, else ``None``. Never raises."""
    if not isinstance(value, str) or not value:
        return None
    if not set(value) <= _ASCII_DIGITS:
        return None
    if len(value) > MAX_ID_DIGITS:
        return None
    return value


def _arg_value(argv: list, flag: str) -> Optional[str]:
    """The value right after ``flag`` in argv, or ``None`` if absent.

    ``SystemExit`` if the flag is present with nothing after it -- a caller
    who typed the flag and forgot the value should not silently get "not
    given".
    """
    if flag not in argv:
        return None
    at = argv.index(flag)
    if at + 1 >= len(argv):
        raise SystemExit(flag + " needs a value")
    return argv[at + 1]


def _validated_id(argv: list, flag: str) -> Optional[str]:
    """The digit string after ``flag``, or ``None`` if the flag is absent.

    ``SystemExit`` on anything present but not 1-20 ASCII digits. THE
    MESSAGE NEVER ECHOES THE VALUE: whatever was typed there might be a
    slug, a pasted url or anything else, and a refusal is not a print.
    """
    raw = _arg_value(argv, flag)
    if raw is None:
        return None
    if _digits_or_none(raw) is None:
        raise SystemExit(flag + ": not 1-20 ASCII digits")
    return raw


def _selected(argv: list) -> tuple:
    """Which keys to read, in order. PURE -- testable without a browser.

    Decided before the browser is touched, so a bad flag refuses at zero
    page loads. Default order: per_post, contact, audience, overview,
    articles, followers, then post_summary if --post-id was given, then
    event if --event-id was given. ``--only KEY`` fires exactly that key;
    an unknown key, or --only post_summary/event without its id, refuses.
    """
    post_id = _validated_id(argv, "--post-id")
    event_id = _validated_id(argv, "--event-id")

    if "--only" in argv:
        at = argv.index("--only")
        want = argv[at + 1] if at + 1 < len(argv) else ""
        if want not in KEYS:
            raise SystemExit("--only takes exactly one of: " + ", ".join(KEYS))
        if want == "post_summary" and post_id is None:
            raise SystemExit("--only post_summary needs --post-id")
        if want == "event" and event_id is None:
            raise SystemExit("--only event needs --event-id")
        return (want,)

    rows = ["per_post", "contact", "audience", "overview", "articles", "followers"]
    if post_id is not None:
        rows.append("post_summary")
    if event_id is not None:
        rows.append("event")
    return tuple(rows)


def _url_for(key: str, post_id: Optional[str], event_id: Optional[str]) -> str:
    """The address for one NAVIGATING key. Never called for ``per_post``.

    Built from a module-level constant or template plus a validated digit
    string only -- never from anything read off a page. See
    ``tests/test_navigation_is_never_derived.py``.
    """
    if key == "contact":
        return CONTACT_URL
    if key == "audience":
        return AUDIENCE_URL
    if key == "overview":
        return OVERVIEW_URL
    if key == "articles":
        return ARTICLES_URL
    if key == "post_summary":
        if post_id is None:
            raise ValueError("post_summary needs a validated post id")
        return POST_SUMMARY_URL_TEMPLATE.format(post_id)
    if key == "followers":
        return FOLLOWERS_URL
    if key == "event":
        if event_id is None:
            raise ValueError("event needs a validated event id")
        return EVENT_URL_TEMPLATE.format(event_id)
    raise ValueError("no address for key " + key)


def _gate_check(key: str, url: str) -> Optional[str]:
    """``None`` when the shipped gate admits ``url``; else the skip line.

    Pre-checked so a refused address is never handed to ``BROWSER.goto`` --
    that call raises on a refusal, and this script treats today's two known
    refusals (followers, event) as routine rather than as an anomaly.
    """
    if readonly.is_read_url(url):
        return None
    return "REFUSED AT THE GATE -- pending its REVIEW commit"


# ---------------------------------------------------------------------------
# The invitation badge, read as this run's control. Copied idiom from
# scripts/_probe_unfired_self_reads.py rather than imported: these three are
# small, self-contained, and every session-opening script in this package
# defines its own badge helpers rather than sharing one.
# ---------------------------------------------------------------------------


async def _badge(page: Any) -> dict:
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


async def _control_serves(page: Any) -> bool:
    """Load the control page and say whether it served. The sibling's rule."""
    await BROWSER.goto(page, CONTROL_URL)
    return await page.locator("div.job-card-container").count() > 0


# ---------------------------------------------------------------------------
# Readers. Each returns integers, booleans and (for the chart reader)
# closed-vocabulary metric words only -- the guarantee the underlying
# modules already carry, re-checked here rather than merely trusted.
# ---------------------------------------------------------------------------


async def _anchors_reading(page: Any) -> dict[str, Any]:
    raw = await anchors.read_anchors(page)
    tallied = anchors.tally(raw.get("counts") or [])
    return {
        "anchors_seen": raw.get("anchors_seen"),
        "values_refused": raw.get("values_refused"),
        "total_classified": tallied.get("total_classified"),
        "member_profile_anchors": tallied.get("member_profile_anchors"),
        "classes_not_reported": tallied.get("classes_not_reported"),
    }


async def _chart_reading(page: Any) -> dict[str, Any]:
    labels = await creator_analytics.collect_labels(page)
    series = chart_labels.series(labels)
    metrics = series.get("metrics") or []
    safe_metrics = sorted(
        m for m in metrics if isinstance(m, str) and m in chart_labels.KNOWN_METRICS
    )
    return {
        "points_found": series.get("points_found"),
        "labels_seen": series.get("labels_seen"),
        "nav_labels_excluded": series.get("nav_labels_excluded"),
        "unrecognised_labels": series.get("unrecognised_labels"),
        "metrics": safe_metrics,
        "metrics_refused": max(0, len(metrics) - len(safe_metrics)),
    }


async def _read_for(key: str, page: Any) -> dict[str, Any]:
    """The reader for one NAVIGATING key. Never called for ``per_post``."""
    if key == "contact":
        reading = await _anchors_reading(page)
        reading["dialog_count"] = int(await page.locator('[role="dialog"]').count())
        return reading
    if key in ("audience", "overview", "post_summary"):
        reading = await _chart_reading(page)
        reading["anchors"] = await _anchors_reading(page)
        return reading
    if key == "articles":
        reading = await _anchors_reading(page)
        reading["pulse_link_count"] = int(
            await page.locator('main a[href*="/pulse/"]').count()
        )
        return reading
    if key == "followers":
        full = await _anchors_reading(page)
        # THE ONE FIELD THIS KEY REPORTS, ON THE BRIEF'S OWN INSTRUCTION: an
        # INTEGER only, never the rest of the tally.
        return {"member_profile_anchors": full.get("member_profile_anchors")}
    if key == "event":
        return await _anchors_reading(page)
    raise ValueError("no reader for key " + key)


def _print_value(label: str, value: Any) -> None:
    """Print one field. Integers, booleans and closed metric words only.

    Anything else is reported by TYPE and LENGTH -- never by content -- the
    same discipline ``_probe_unfired_self_reads.py``'s ``_report`` uses.
    """
    if isinstance(value, bool):
        print("    " + label + " = " + str(value))
    elif isinstance(value, int):
        print("    " + label + " = " + str(value))
    elif value is None:
        print("    " + label + " = None")
    elif isinstance(value, (list, tuple)) and all(
        isinstance(item, str) and item in chart_labels.KNOWN_METRICS
        for item in value
    ):
        print("    " + label + " = " + str(sorted(value)))
    else:
        print("    " + label + ": " + type(value).__name__ + ", length "
              + str(len(str(value))))


def _print_reading(reading: dict) -> None:
    for label in sorted(reading):
        value = reading[label]
        if isinstance(value, dict):
            for sub in sorted(value):
                _print_value(label + "." + sub, value[sub])
        else:
            _print_value(label, value)


# ---------------------------------------------------------------------------
# per_post -- the one key that fires no navigation of its own.
# ---------------------------------------------------------------------------


async def _do_per_post(outcomes: dict, raw: dict) -> None:
    """Fire ``linkedin_creator_analytics()`` and report its per_post fields.

    NO NAVIGATION OF ITS OWN: the tool opens and closes its own page
    session, so this must never run inside an ``async with
    BROWSER.session()`` block this script is already holding -- the session
    lock is not reentrant.
    """
    out = await server.linkedin_creator_analytics()
    if not isinstance(out, dict):
        raw["per_post"] = {"envelope_type": type(out).__name__}
        outcomes["per_post"] = "ERROR"
        raise _Anomaly("NotADict", "per_post")
    raw["per_post"] = out
    has_error = bool(out.get("error"))
    per_post = out.get("per_post")
    per_post = per_post if isinstance(per_post, dict) else {}
    print("\n--- per_post (via linkedin_creator_analytics; no navigation of "
          "its own)")
    _print_value("error_envelope", has_error)
    _print_value("points_found", out.get("points_found"))
    _print_value("readable", out.get("readable"))
    _print_value("per_post.items_read", per_post.get("items_read"))
    _print_value("per_post.readable", per_post.get("readable"))
    _print_value("per_post.unparsed", per_post.get("unparsed"))
    _print_value("per_post.not_activity_links", per_post.get("not_activity_links"))
    _print_value("per_post.duplicate_links", per_post.get("duplicate_links"))
    outcomes["per_post"] = "ERROR" if has_error else "RETURNED"
    if has_error:
        raise _Anomaly("error_envelope", "per_post")


# ---------------------------------------------------------------------------
# Captures and the raw-results file. gitignored _state/ and nowhere else.
# ---------------------------------------------------------------------------


def _capture(key: str, html: str) -> None:
    state = _ROOT / "_state"
    state.mkdir(exist_ok=True)
    (state / ("l1-" + key + ".html")).write_text(html, encoding="utf-8")


def _write_raw(raw: dict) -> None:
    state = _ROOT / "_state"
    state.mkdir(exist_ok=True)
    (state / "l1-admitted-reads-raw.json").write_text(
        json.dumps(raw, indent=2, default=str), encoding="utf-8")
    print("\n### RAW results written under _state/ (gitignored)")


class _Anomaly(Exception):
    """Raised to stop every further page load. Carries no page-derived text."""

    def __init__(self, kind: str, where: str) -> None:
        super().__init__(kind + " at " + where)
        self.kind = kind
        self.where = where


async def main() -> int:
    argv = sys.argv[1:]
    no_capture = "--no-capture" in argv
    # DECIDED BEFORE THE BROWSER IS TOUCHED: a bad flag refuses here, at
    # zero page loads.
    keys = _selected(argv)
    post_id = _validated_id(argv, "--post-id")
    event_id = _validated_id(argv, "--event-id")
    print("### keys selected: " + ", ".join(keys))

    outcomes: dict[str, str] = {}
    raw: dict[str, Any] = {}
    try:
        print("### CONTROL, before anything")
        async with BROWSER.session() as page:
            first_control = await _control_serves(page)
            print("    control serves: " + str(first_control))
            badge_before = await _badge(page)
        if not first_control:
            print("    THE CONTROL DID NOT SERVE. This run is VOID. Stopping "
                  "before any key.")
            _write_raw(raw)
            return 1
        before_state = _badge_state(badge_before)
        print("### invitation badge BEFORE: " + before_state)
        if before_state != "READABLE":
            # A BRANCH, NOT A DECORATION: the run goes on, because the badge is
            # a COST reading and not a self-check -- but it says now, before a
            # single key loads, that the consumption line at the end will be
            # UNKNOWN rather than letting a blind bracket read as a clean one.
            print("    the badge cannot be read on the control page, so this "
                  "run cannot price itself; consumption will read UNKNOWN")

        for key in keys:
            if key == "per_post":
                # ITS OWN SESSION, OPENED AND CLOSED INSIDE THE TOOL CALL --
                # never nested inside a session block this script holds.
                await _do_per_post(outcomes, raw)
                continue

            url = _url_for(key, post_id, event_id)
            skip = _gate_check(key, url)
            if skip is not None:
                print("\n--- " + key + ": " + skip)
                outcomes[key] = "GATE-REFUSED"
                continue

            html: Optional[str] = None
            try:
                async with BROWSER.session() as page:
                    landed = await BROWSER.goto(page, url)
                    relation = _relation(landed, url)
                    print("\n--- " + key)
                    print("    relation: " + relation)
                    assert_not_authwall(landed, surface=key)
                    reading = await _read_for(key, page)
                    if not no_capture:
                        html = await page.content()
            except Exception as exc:  # noqa: BLE001
                print("    RAISED " + type(exc).__name__)
                raise _Anomaly(type(exc).__name__, key) from exc

            _print_reading(reading)
            raw[key] = reading
            outcomes[key] = "RETURNED"
            if html is not None:
                _capture(key, html)

        print("\n### CONTROL AGAIN, at the end")
        async with BROWSER.session() as page:
            last_control = await _control_serves(page)
            print("    control serves: " + str(last_control))
            badge_after = await _badge(page)
        after_state = _badge_state(badge_after)
        consumption = _consumption(badge_before, badge_after)
        print("### invitation badge AFTER: " + after_state)
        print("    CONSUMPTION: " + consumption)
        raw["_bracket"] = {"before": before_state, "after": after_state,
                           "consumption": consumption}
        if not last_control:
            print("    THE CONTROL STOPPED SERVING. Readings above are VOID.")
            _write_raw(raw)
            return 1
    except _Anomaly as stop:
        # NO FURTHER PAGE LOAD, not even the closing badge read. The raw
        # results collected so far are still written so the anomaly can be
        # diagnosed from disk without another navigation.
        print("\n### ANOMALY: " + stop.kind + " at " + stop.where + ".")
        print("    EVERY FURTHER PAGE LOAD WAS STOPPED. This run is VOID.")
        _write_raw(raw)
        return 1
    except Exception as error:  # noqa: BLE001
        print("\nRUN ABORTED: " + type(error).__name__)
        _write_raw(raw)
        return 1
    finally:
        # CLOSE OUR TAB, THEN DROP THE CDP CONNECTION.
        #
        # The page is closed explicitly first: the idiom
        # tests/test_a_probe_closes_its_own_tab.py recognises, and the one
        # every other script in this wave uses. THE PAGE, NEVER THE
        # CONTEXT -- in attach mode the context is the operator's own
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
    print("### OUTCOMES")
    for k in sorted(outcomes):
        print("    " + k + ": " + outcomes[k])

    _write_raw(raw)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
