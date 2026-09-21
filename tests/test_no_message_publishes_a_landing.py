"""No message in this package may publish an address LinkedIn chose.

## THE CLASS THIS HOLDS CLOSED

``config.scrub`` cleans error text by substituting THIS SERVER'S OWN
FILESYSTEM PATHS and nothing else. It knows paths. It does not know urls. So a
message that interpolates an address -- a landed url, an href, a slug, a
redirect target -- carries that address to the caller intact, through an
exception or through a log record, and no amount of scrubbing touches it.

    A PATH-SHAPED SCRUBBER IS NOT A REDACTOR. IT IS A SUBSTITUTION LIST,
    AND A URL IS NOT ON IT.

The repair is ``linkedin_server/landing.py``: it turns an address into a line
built only from a closed vocabulary -- a marker from ``config.AUTHWALL_MARKERS``,
a route from a fixed table, and COUNTS. ``tests/test_landing.py`` proves that
module says nothing else. THIS file is the other half, and it answers the
question that one cannot: **are there any other sites?**

## IT DISCOVERS ITS SUBJECTS

A guard that NAMES the sites it knows about catches the third instance of a
class and not the fourth, which is the shape of every repair this repository
keeps re-making. So the subject set is DISCOVERED by walking the package's AST
through ``scripts/_census_message_interpolations.py`` -- imported, never
re-implemented here, because two copies of one walk drift and the drift is
invisible. A message written tomorrow that interpolates an address is in the
subject set the moment it is written.

## THE FIVE VERDICTS, AND WHY NONE OF THEM CAN MEAN "IT LEAKS"

* ``WITHHELD`` -- routed through ``landing.withheld`` / ``landing.render`` /
  ``landing.describe_landing``. No character the site chose survives. MEASURED
  from the call, not ruled.
* ``SERVER_CONSTRUCTED`` -- a module constant, or an address this package
  assembled from its own template (``LOGIN_URL``, ``BASE_URL``,
  ``http_url(chosen)``, ``spec.url_template.format(...)``). MEASURED.
* ``ASKED_FOR`` -- the value is the address this package REQUESTED, not one it
  landed on. ``assert_read_url(url)`` refusing the url it was handed is quoting
  the caller's own argument back. RULED, per function, below.
* ``PUBLISHED_BY_CONTRACT`` -- a field the tool publishes on its SUCCESS path
  too, so withholding it in the failure message would withhold nothing. RULED.
* ``NAMES_NO_ADDRESS`` -- the site matched the source-text rule on a token
  inside an identifier that is not an address at all (``dom.JOB_HREF`` is a
  regex pattern and contains ``href``). RULED.

There is deliberately **no verdict meaning "this publishes a landing"**, and
:func:`write_baseline` REFUSES to write a file containing an unruled site. A
baseline that can record a permitted leak becomes a list of permitted leaks
within one commit of somebody being in a hurry -- which is the reasoning
``tests/reader_leak_baseline.json`` already carries, applied to a second class.

A site that fits none of the five is ``UNRULED``, and ``UNRULED`` is a
FAILURE, not a bucket. A new address-naming message goes red on arrival.

## WHAT THIS GUARD DOES NOT COVER -- the honest half

It may not claim more than it ran, so:

**IT IS A SOURCE-TEXT RULE OVER EXPRESSION NAMES.** A site enters the subject
set when the source text of an interpolated sub-expression contains ``url``,
``landed``, ``final_url``, ``href``, ``slug`` or ``redirect``. Therefore:

* **A LANDING BOUND TO A NAME THAT SAYS NONE OF THOSE IS INVISIBLE TO IT.**
  ``raise Error(f"... {destination} ...")`` or ``{where_we_ended_up}`` or
  ``{target}`` holding a landed address is a real instance of this class and
  this guard will not see it. That is the limit, stated plainly rather than
  discovered later.
* It reads NAMES, not values. It cannot tell whether a variable called ``url``
  actually holds one.
* It does not run the code. Which of these sites is REACHABLE is a different
  question, settled by driving, not by reading -- the way
  ``tests/test_readers_emit_no_page_string.py`` settles its own.
* The census it imports does not count strings built into a ``dict`` literal,
  returned directly, or assembled across a function boundary by a helper.
  Those shapes are outside the subject set entirely.

Regenerate the baseline with::

    python -m tests.test_no_message_publishes_a_landing --write-baseline
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Optional

import pytest

REPO = Path(__file__).resolve().parents[1]

#: The committed verdict for every discovered site. The half that makes a
#: silently changing subject set visible.
BASELINE_PATH = REPO / "tests" / "landing_interpolation_baseline.json"

#: The walk. IMPORTED, not re-implemented -- see the module docstring.
CENSUS_PATH = REPO / "scripts" / "_census_message_interpolations.py"


# ---------------------------------------------------------------------------
# Verdicts
# ---------------------------------------------------------------------------

WITHHELD = "WITHHELD"
SERVER_CONSTRUCTED = "SERVER_CONSTRUCTED"
ASKED_FOR = "ASKED_FOR"
PUBLISHED_BY_CONTRACT = "PUBLISHED_BY_CONTRACT"
NAMES_NO_ADDRESS = "NAMES_NO_ADDRESS"

#: The failure state. It is NOT a verdict and it is NEVER written to the
#: baseline; see :func:`write_baseline`.
UNRULED = "UNRULED"

RECORDABLE: frozenset[str] = frozenset(
    {WITHHELD, SERVER_CONSTRUCTED, ASKED_FOR, PUBLISHED_BY_CONTRACT, NAMES_NO_ADDRESS}
)


# ---------------------------------------------------------------------------
# The two RULED tables. Keyed by ``module:function`` -- never by line, because
# a line number is the first thing an unrelated edit moves, and a ruling that
# expires on every reformat is a ruling nobody will maintain.
#
# THESE ARE ADJUDICATIONS, NOT MEASUREMENTS, and they are written down here
# with their reason so the next reader can disagree with the reason rather
# than guess at it.
# ---------------------------------------------------------------------------

ASKED_FOR_SITES: dict[str, str] = {
    "readonly.py:assert_read_url": (
        "the gate refuses the url it was HANDED. Quoting a caller's own "
        "argument back to that caller publishes nothing the caller did not "
        "already have, and naming the rejected address is the entire value of "
        "the refusal -- a gate that says 'some url was refused' cannot be "
        "acted on."
    ),
    "writes.py:assert_write_url": (
        "same shape as readonly.assert_read_url, on the write side. The "
        "subject is the REQUESTED address, checked before any navigation, so "
        "there is no landing here to withhold."
    ),
    "browser.py:goto": (
        "the navigation target this package asked for, reported when the "
        "navigation itself failed. No page was reached, so nothing LinkedIn "
        "chose exists at this point."
    ),
}

PUBLISHED_BY_CONTRACT_SITES: dict[str, str] = {
    "shape.py:parse_person_card": (
        "``out['profile']`` is a field this shaper publishes on its SUCCESS "
        "path. Withholding it in a message while returning it in the payload "
        "would withhold nothing. Whether that field may be published at all "
        "is the SHAPERS' question, governed by shape.py and the redaction "
        "tests -- a different subject with its own guards."
    ),
    "dom.py:read_job_identity": (
        "``out['company_url']`` is likewise a success-path field. Same "
        "reasoning, same owning guard."
    ),
}

#: Addresses this package ASSEMBLES, where the census cannot measure it.
#:
#: ``SERVER_CONSTRUCTED`` is decided from the code wherever that is possible --
#: a SHOUTED constant, a ``landing.*`` call. It is NOT decidable for a call to
#: an ordinary local function: ``http_url(chosen)`` could return anything as
#: far as a static walk knows, and teaching the walk to assume otherwise would
#: make its hazard bucket lie about every other local call in the package.
#:
#: So these two are RULED, and the ruling is the narrow one: not "calls in this
#: function are safe" but "THIS expression assembles an address out of parts
#: this server already held".
SERVER_ASSEMBLED_SITES: dict[str, str] = {
    "transport.py:_serve": (
        "``http_url(chosen)`` is this server's OWN loopback bind address, "
        "built from a port number it just selected. Nothing LinkedIn chose "
        "reaches it."
    ),
    "writes.py:_render": (
        "``spec.url_template.format(target=url_target_of(...))`` assembles an "
        "address from a template that is a literal in the module-level "
        "``SANCTIONED_WRITES`` table plus a grant target. It is the address "
        "this package INTENDS to visit, composed before any navigation -- the "
        "same class as ASKED_FOR, and never a landing."
    ),
}

#: Sites the SOURCE-TEXT rule caught on a token that is not an address.
#:
#: The subject rule matches ``url``/``landed``/``href``/``slug``/``redirect``
#: as substrings of an expression's source, which over-approximates on
#: purpose. This is where the over-approximation is paid off, and naming the
#: verdict rather than folding these into a safety class is the point: these
#: are not addresses that were judged safe, they are NOT ADDRESSES.
NAMES_NO_ADDRESS_SITES: dict[str, str] = {
    "server.py:_read_tracker": (
        "the interpolated value is ``shape.tracker_read_note(...)``, a note "
        "this package composes to explain why a read came back empty. It "
        "matches the address rule through exactly one substring -- the "
        "``href`` inside ``href_pattern=dom.JOB_HREF`` -- and ``JOB_HREF`` is "
        "a REGEX PATTERN, ``/jobs/view/(?:[^/?#]*-)?(\\d{6,})``, not an "
        "address. There is no landing at this site to withhold."
    ),
}


# ---------------------------------------------------------------------------
# The subject set
# ---------------------------------------------------------------------------


def _census() -> Any:
    """Load the census module by path.

    ``scripts/`` is not a package, so this is an explicit path load rather
    than an import. It is done once and cached on the module.
    """
    cached = globals().get("_CENSUS_MODULE")
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(
        "_census_message_interpolations", CENSUS_PATH
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError(f"could not load the census at {CENSUS_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    globals()["_CENSUS_MODULE"] = module
    return module


#: How much of an expression goes into its key. One site in this package is a
#: 700-character call whose source segment carries INLINE COMMENTS, and a key
#: holding those would turn this guard red every time somebody reworded a
#: comment deep inside an unrelated call -- a guard that cries wolf on prose
#: is one that gets deleted. 60 characters reaches past the callee name and
#: the first argument at every current site, and stops before any comment.
KEY_EXPR_LIMIT = 60


def _site_key(module: str, function: str, expr: str, seen: dict[str, int]) -> str:
    """``module:function:expression``, with ``#n`` only where it repeats.

    DELIBERATELY NOT ``module:line``. The lead of this wave edits these files
    continuously; a line-keyed baseline would churn on every unrelated edit
    and a baseline nobody can keep green is one somebody deletes.

    The ordinal is the cost of that choice and it is a real one: deleting the
    first of four identical sites renumbers the other three, so the guard
    reports one vanished and one appeared rather than one removed. That is
    LOUD and wrong-in-the-safe-direction, which is the trade taken here.
    """
    short = " ".join(expr.split())[:KEY_EXPR_LIMIT]
    base = f"{module}:{function}:{short}"
    seen[base] = seen.get(base, 0) + 1
    return base if seen[base] == 1 else f"{base}#{seen[base]}"


def subject_sites(sources: Optional[dict[str, str]] = None) -> list[dict[str, Any]]:
    """Every interpolated sub-expression whose SOURCE TEXT names an address.

    ``sources`` is an injection point for the controls at the bottom, which
    plant a synthetic module as a STRING. Nothing is ever written into
    ``linkedin_server/`` to test this guard.
    """
    census = _census()
    package_errors = census._package_error_names(census.PACKAGE)
    if sources is None:
        sources = census.read_package()
    rows = census.census_sources(sources, package_errors)

    seen: dict[str, int] = {}
    out: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda r: (r["module"], r["line"])):
        for field in row["fields"]:
            if not field.get("shortlist"):
                continue
            out.append(
                {
                    "key": _site_key(
                        row["module"], row["function"], field["expr"], seen
                    ),
                    "module": row["module"],
                    "function": row["function"],
                    "line": row["line"],
                    "kind": row["kind"],
                    "expr": field["expr"],
                    "bucket": field["bucket"],
                    "sanitiser": field.get("sanitiser", ""),
                }
            )
    return out


def verdict_for(site: dict[str, Any]) -> str:
    """One of the five verdicts, or ``UNRULED``.

    ORDER IS THE DESIGN. The two MEASURED verdicts are decided first, from the
    code itself, so a ruling can never quietly override what the source says.
    Only then are the RULED tables consulted.
    """
    if site["sanitiser"]:
        return WITHHELD
    if site["bucket"] == "SERVER_CONSTRUCTED":
        return SERVER_CONSTRUCTED

    where = f"{site['module']}:{site['function']}"
    if where in SERVER_ASSEMBLED_SITES:
        return SERVER_CONSTRUCTED
    if where in ASKED_FOR_SITES:
        return ASKED_FOR
    if where in PUBLISHED_BY_CONTRACT_SITES:
        return PUBLISHED_BY_CONTRACT
    if where in NAMES_NO_ADDRESS_SITES:
        return NAMES_NO_ADDRESS
    return UNRULED


#: The package walk, done ONCE. ``server.py`` alone is half a megabyte and the
#: walk covers 46 modules; without this, parametrising over the subject set
#: re-parsed the whole package once per case and the file took minutes instead
#: of seconds. Synthetic sources are never cached -- the controls mutate them
#: and a cache keyed on nothing would hand the second control the first one's
#: answer, which is a control that cannot fail.
_PACKAGE_SITES: Optional[list[dict[str, Any]]] = None


def package_sites() -> list[dict[str, Any]]:
    global _PACKAGE_SITES
    if _PACKAGE_SITES is None:
        _PACKAGE_SITES = subject_sites()
    return _PACKAGE_SITES


def measure(sources: Optional[dict[str, str]] = None) -> dict[str, str]:
    sites = package_sites() if sources is None else subject_sites(sources)
    return {site["key"]: verdict_for(site) for site in sites}


def compare(baseline: dict[str, str], live: dict[str, str]) -> dict[str, list]:
    """The THREE EVENTS, as data so the controls can assert on them.

    Factored out rather than inlined because a comparison that only ever runs
    on passing input has never been shown to detect anything.
    """
    return {
        "appeared": sorted(set(live) - set(baseline)),
        "vanished": sorted(set(baseline) - set(live)),
        "changed": sorted(
            f"{k}: {baseline[k]} -> {live[k]}"
            for k in set(live) & set(baseline)
            if baseline[k] != live[k]
        ),
    }


def _baseline() -> dict[str, str]:
    if not BASELINE_PATH.exists():
        return {}
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["sites"]


# ---------------------------------------------------------------------------
# The guard
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", sorted(measure()))
def test_every_address_naming_site_has_a_verdict(key: str) -> None:
    """No site may publish a landing, and no site may be unclassified.

    One case per site so a failure names the site rather than a count.
    """
    live = measure()
    verdict = live[key]
    assert verdict in RECORDABLE, (
        f"{key} interpolates an address and has no verdict. Either route it "
        f"through landing.withheld(), or record WHY it is safe in "
        f"ASKED_FOR_SITES / PUBLISHED_BY_CONTRACT_SITES / "
        f"NAMES_NO_ADDRESS_SITES in {Path(__file__).name}. There is no "
        f"verdict meaning 'this one is allowed to publish a landing'."
    )


def test_the_subject_set_has_not_silently_changed() -> None:
    """Coverage is compared against a COMMITTED baseline, not asserted.

    Three ways this fails, each a real event rather than a chore:

    * a site APPEARED that nobody classified -- the next instance of the
      class, arriving unmeasured;
    * a site VANISHED -- a rename or a refactor taking its coverage with it,
      silently;
    * a site's verdict CHANGED -- most importantly, a ``WITHHELD`` site that
      went back to naming the address.
    """
    baseline = _baseline()
    assert baseline, (
        f"{BASELINE_PATH.name} is missing or empty. It is the record of what "
        f"this guard covers; without it the guard cannot report a change. "
        f"Regenerate: python -m tests.{Path(__file__).stem} --write-baseline"
    )
    events = compare(baseline, measure())

    assert not events["appeared"], (
        "message site(s) interpolating an address with no recorded verdict: "
        + ", ".join(events["appeared"])
        + f". Classify them, then regenerate {BASELINE_PATH.name}."
    )
    assert not events["vanished"], (
        "site(s) in the baseline no longer exist: "
        + ", ".join(events["vanished"])
        + ". A rename takes its coverage with it unless the baseline moves too."
    )
    assert not events["changed"], (
        "site verdict(s) changed: "
        + "; ".join(events["changed"])
        + ". A WITHHELD site becoming anything else is this guard's whole point."
    )


def test_the_baseline_cannot_record_a_leak() -> None:
    """The file may hold only the five verdicts, none of which permits one.

    This is a property of the FILE, checked independently of how it was
    written. A hand-edited baseline carrying ``"PUBLISHES": "known issue"`` is
    exactly how a guard becomes a list of exceptions, and that edit would pass
    every other test here.
    """
    baseline = _baseline()
    unknown = sorted({v for v in baseline.values() if v not in RECORDABLE})
    assert not unknown, (
        f"{BASELINE_PATH.name} records verdict(s) this guard does not define: "
        + ", ".join(repr(v) for v in unknown)
        + ". A baseline is not where a leak is recorded."
    )


def test_every_declared_verdict_is_actually_used() -> None:
    """A verdict nobody has ever assigned is dead vocabulary -- and worse.

    This file's central claim is that there is NO verdict meaning "allowed to
    publish a landing". Every unexercised verdict weakens that claim, because
    an unused escape hatch is one nobody has checked the shape of. It is also
    how this guard was first written: ``NAMES_NO_ADDRESS`` was declared and
    then never assigned, because its one real site had been filed under
    ``PUBLISHED_BY_CONTRACT`` -- a less accurate verdict that happened to be
    reached first.

        A CATEGORY THAT NEVER FIRES HAS NOT BEEN TESTED, IT HAS BEEN ASSUMED.
    """
    used = set(measure().values())
    unused = sorted(RECORDABLE - used)
    assert not unused, (
        "verdict(s) declared but assigned to no site: "
        + ", ".join(unused)
        + ". Either some site belongs there and is currently filed under a "
        "less accurate verdict, or the category should be deleted."
    )


def test_the_guard_reports_what_it_examined() -> None:
    """It may not claim more than it ran.

    The count is asserted to be non-trivial, because a subject set that
    quietly became empty -- an import that failed, a rename in the census,
    a changed flag name -- would make every other test in this file pass by
    examining nothing. A guard satisfied by an empty result cannot fail.
    """
    sites = package_sites()
    by_verdict: dict[str, int] = {}
    for site in sites:
        by_verdict[verdict_for(site)] = by_verdict.get(verdict_for(site), 0) + 1

    print(f"\naddress-naming interpolations examined: {len(sites)}")
    for verdict in sorted(by_verdict):
        print(f"  {verdict:24s} {by_verdict[verdict]:3d}")
    print(
        "NOT covered: a landing bound to a name containing none of "
        "url/landed/final_url/href/slug/redirect is invisible to this rule."
    )

    assert len(sites) >= 10, (
        f"only {len(sites)} address-naming interpolation(s) found in "
        f"linkedin_server/. This guard covered 19 when it was written; a "
        f"collapse to near-zero means the census stopped finding them, not "
        f"that the package stopped doing it."
    )
    assert by_verdict.get(WITHHELD, 0) >= 1, (
        "no site is WITHHELD. landing.py exists precisely so that some are; "
        "if none is, either the repair was reverted or this guard stopped "
        "recognising it."
    )


# ---------------------------------------------------------------------------
# SHOWN FAILING
#
# A guard enters this repository only if it has been demonstrated going red on
# a planted defect. Both controls plant a SYNTHETIC MODULE SOURCE -- a string,
# parsed by the census, never written into ``linkedin_server/`` -- and assert
# the comparison convicts it.
#
# NO REAL IDENTITY IS HERE. The plants are Python identifiers and one
# ``example``-token address, which is sanctioned by
# ``tests/test_no_committed_identity.SYNTHETIC_SLUG_TOKENS``.
# ---------------------------------------------------------------------------

#: A module with ONE withheld site. The starting point both controls mutate.
_CLEAN_SUBJECT = '''
from linkedin_server import landing


class WriteAttemptError(Exception):
    pass


def _assert_landed_on_target(landed):
    if landed != "https://example.invalid/target":
        raise WriteAttemptError(
            "refusing to click: the browser landed elsewhere. THE LANDING IS "
            f"WITHHELD; what is safe to say about it -- {landing.withheld(landed)}."
        )
'''

#: The same module plus a NEW site that names the landing outright.
_SUBJECT_WITH_A_NEW_SITE = _CLEAN_SUBJECT + '''

def _a_gate_somebody_added_today(landed):
    raise WriteAttemptError(f"refusing to click: it landed on {landed}")
'''

#: The same module with the withheld call REVERTED to the bare value.
_SUBJECT_REVERTED = _CLEAN_SUBJECT.replace(
    "{landing.withheld(landed)}", "{landed}"
)


def _measure_subject(source: str) -> dict[str, str]:
    return measure({"subject.py": source})


def test_control_a_new_unruled_landing_site_is_reported_as_new() -> None:
    """PLANTED DEFECT 1: somebody adds a gate that names the landing.

    The guard must report it as APPEARED, and it must carry no verdict -- if
    an unruled site could quietly acquire one, the baseline would absorb the
    next instance of this class instead of refusing it.
    """
    baseline = _measure_subject(_CLEAN_SUBJECT)
    live = _measure_subject(_SUBJECT_WITH_A_NEW_SITE)

    assert baseline, "the control's own clean subject produced no sites"
    assert all(v == WITHHELD for v in baseline.values()), baseline

    events = compare(baseline, live)
    assert events["appeared"], (
        "CONTROL FAILED: a new raise naming the landing was not reported as "
        f"a new site. live={live}"
    )
    assert not events["vanished"], events
    for key in events["appeared"]:
        assert live[key] == UNRULED, (
            f"CONTROL FAILED: the planted site {key} was given the verdict "
            f"{live[key]!r} instead of {UNRULED}."
        )


def test_control_a_withheld_site_reverted_to_the_bare_value_is_reported_as_changed() -> None:
    """PLANTED DEFECT 2: the repair is backed out at an existing site.

    This is the regression the whole guard exists for, and it is the one a
    "no new sites" check would miss entirely -- the site count does not move.

    The key deliberately CHANGES with the expression, so the event surfaces as
    a vanished-plus-appeared pair rather than as a verdict change. That is the
    documented cost of keying on the expression instead of the line, and the
    control asserts the real behaviour rather than the behaviour the name
    suggests -- a control that asserts what its author hoped for is not one.
    """
    baseline = _measure_subject(_CLEAN_SUBJECT)
    live = _measure_subject(_SUBJECT_REVERTED)

    assert _SUBJECT_REVERTED != _CLEAN_SUBJECT, "the mutation did not apply"
    assert list(baseline.values()) == [WITHHELD], baseline

    events = compare(baseline, live)
    assert events["appeared"] or events["changed"], (
        "CONTROL FAILED: reverting landing.withheld() to the bare landed "
        f"value was not detected. baseline={baseline} live={live}"
    )
    assert not all(v == WITHHELD for v in live.values()), (
        f"CONTROL FAILED: the reverted site is still called {WITHHELD}. "
        f"live={live}"
    )
    assert UNRULED in live.values(), (
        f"CONTROL FAILED: the reverted site did not become {UNRULED}. "
        f"live={live}"
    )


def test_control_the_two_planted_subjects_really_differ() -> None:
    """Small, and it exists because the failure it prevents is invisible.

    If a plant ever stopped applying -- a renamed helper, a changed spelling
    -- both controls above would compare a subject against itself, find no
    events, and the assertions would report a guard that cannot fail as a
    guard that passes.
    """
    assert "landing.withheld" in _CLEAN_SUBJECT
    assert "landing.withheld" not in _SUBJECT_REVERTED
    assert len(_SUBJECT_WITH_A_NEW_SITE) > len(_CLEAN_SUBJECT)


# ---------------------------------------------------------------------------
# Regeneration
# ---------------------------------------------------------------------------


def write_baseline() -> int:
    """Write the baseline, REFUSING if any site is unruled."""
    sites = package_sites()
    rows = {site["key"]: verdict_for(site) for site in sites}

    unruled = sorted(k for k, v in rows.items() if v not in RECORDABLE)
    if unruled:
        print(f"REFUSED: {len(unruled)} site(s) interpolate an address with no")
        print("verdict. A baseline is not where a leak is recorded -- either")
        print("route them through landing.withheld() or rule them first:")
        for key in unruled:
            print(f"  {key}")
        return 1

    payload = {
        "_comment": (
            "Verdict per message site that interpolates an address, from "
            "scripts/_census_message_interpolations.py. Regenerate with: "
            "python -m tests.test_no_message_publishes_a_landing "
            "--write-baseline. WITHHELD and SERVER_CONSTRUCTED are MEASURED "
            "from the code; ASKED_FOR, PUBLISHED_BY_CONTRACT and "
            "NAMES_NO_ADDRESS are RULED, per function, with reasons in that "
            "file. There is no verdict meaning 'this publishes a landing' -- "
            "a baseline that could record one would become a list of "
            "permitted leaks."
        ),
        "sites": dict(sorted(rows.items())),
    }
    BASELINE_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )

    counts: dict[str, int] = {}
    for verdict in rows.values():
        counts[verdict] = counts.get(verdict, 0) + 1
    print(f"wrote {BASELINE_PATH} -- {len(rows)} sites")
    for verdict, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {verdict:24s} {count:4d}")
    return 0


if __name__ == "__main__":
    if "--write-baseline" in sys.argv:
        raise SystemExit(write_baseline())
    raise SystemExit(
        "usage: python -m tests.test_no_message_publishes_a_landing --write-baseline"
    )
