"""Which file inputs does the MESSAGE COMPOSER draw? A LIVE READ, nothing else.

WHY THIS EXISTS. ``_audit/2026-09-04-file-input-survey.md`` records, in its
table row for the message composer (``/messaging/compose/``), "TWO, measured
live 2026-09-01" -- and that reading has never been reproduced by an
instrument. The only place the two file inputs' accessible names have ever
existed is as PROSE, in a test docstring and in that audit file. A name
recorded in prose is not a measurement a later wave can act on, and three
capability rows (attach photo / video / files to a message) are blocked on
turning that prose into something re-takeable.

``_probe_file_inputs_live.py`` did exactly this job for the post composer and
the feed, and is the template this script copies: same allowlist gate, same
ABSENT-vs-ZERO discipline, same refusal to aim at a name. This is the sibling
probe for the one surface that script did not cover.

WHAT IT DOES: takes the profile lock, opens the ONE allowlisted messaging
compose address through the same read door every read tool in this package
uses, and counts. WHAT IT DOES NOT DO: it does not click, fill, type, press,
select, submit or upload anything. There is no mutating call in this file,
and ``readonly.scan_source_for_mutations`` run over this file's own source is
what proves that, printed at the end rather than merely claimed.

ABSENT IS NOT ZERO, and the distinction decides the answer here just as it
did for the post composer. "The composer drew no file input" is a claim
about the composer. "The page did not render a composer" is a claim about
the page, and a file-input count of zero taken off it means nothing at all.
So the composer's OWN controls are read too, through
``dom.read_compose_fields``, which either names its two dispatch modes and
its body control structurally or REFUSES and says why -- and either answer
is reported alongside the file-input count rather than left implicit.

RUN IT (the env pair is MANDATORY -- it attaches to the operator's own
already-running, signed-in Chrome; without it this launches a SECOND Chrome
on the same profile, which has cost a signed-in session before):

LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 venv/Scripts/python.exe scripts/_probe_compose_file_inputs.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

# THE REPO ROOT ON THE PATH, the same way every other probe in this directory
# does it. A script run by filename gets its OWN directory on sys.path, not
# the checkout, so the package is not importable without this line.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, dom, profile_lock, readonly, server  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: THE ONE TARGET, read off the server's own surface table rather than typed
#: as a literal here, so this script cannot silently name an address the rest
#: of the package does not also recognise as the messaging compose surface.
TARGET_LABEL = "messaging compose"
TARGET_URL: str = server.CENSUS_SURFACES["messaging_compose"]


def _fmt_compose_fields(compose_fields: dict[str, Any]) -> str:
    """The ABSENT-vs-ZERO control. Counts and refusal reasons only -- never a
    label, a mode's text, or anything else this reader chose not to publish.
    """
    lines = ["    compose_fields (the composer's OWN controls, read separately):"]
    refused = compose_fields.get("refused")
    lines.append(f"      refused:             {refused!r}")
    if refused:
        lines.append(f"      why:                 {compose_fields.get('why')}")
        lines.append(
            f"      recipients_selected: {compose_fields.get('recipients_selected')}"
        )
        for key in ("radio_count", "checked_count", "textbox_count"):
            if key in compose_fields:
                lines.append(f"      {key}: {compose_fields.get(key)}")
    else:
        modes = list(compose_fields.get("modes") or [])
        body = compose_fields.get("body") or {}
        lines.append(
            f"      recipients_selected: {compose_fields.get('recipients_selected')}"
        )
        lines.append(f"      dispatch_modes_count: {len(modes)}")
        lines.append(f"      body.present:         {body.get('present')}")
        lines.append(f"      body.is_editable:     {body.get('is_editable')}")
        lines.append(f"      body.name_source:     {body.get('name_source')!r}")
    return "\n".join(lines)


def _fmt_file_inputs(reading: dict[str, Any]) -> str:
    lines = ["    file_inputs:"]
    lines.append(f"      count:        {reading['count']}")
    lines.append(f"      described:    {reading['described']}")
    lines.append(f"      ambiguous:    {reading['ambiguous']}")
    lines.append(f"      undercounted: {reading['undercounted']}")
    for record in reading["inputs"]:
        lines.append(
            f"      - shape={record.get('shape')!r} "
            f"container={record.get('container')} "
            f"disabled={record.get('disabled')} "
            f"name_source={record.get('name_source')}"
        )
    return "\n".join(lines)


def _verdict(reading: dict[str, Any], compose_fields: dict[str, Any]) -> str:
    """ZERO / ONE / TWO OR MORE / UNKNOWN, and nothing but one of those four.

    THE ABSENT-vs-ZERO CONTROL FIRES BEFORE THE COUNT IS EVEN CONSULTED. A
    truncated census cannot be aimed from at all, whatever it counted. Short
    of that, the composer's own controls (``compose_fields``) have to show
    the page actually rendered a composer -- either a clean structural
    reading of its two dispatch modes and its body, or the one refusal that
    is itself positive evidence of rendering (a recipient chip already
    sitting in an otherwise-fresh compose box). Every OTHER refusal from
    ``read_compose_fields`` means this surface's own controls did not come
    back in the shape that reader expects, which is the same "the page never
    arrived" signal ``_probe_file_inputs_live.py`` treats as UNKNOWN for the
    post composer's editors and publish controls.
    """
    if reading["undercounted"]:
        return "UNKNOWN (census truncated / composer did not render)"
    refused = compose_fields.get("refused")
    composer_confirmed_rendered = (not refused) or refused == "recipient_already_selected"
    if not composer_confirmed_rendered:
        return "UNKNOWN (census truncated / composer did not render)"
    if reading["count"] == 0:
        return "ZERO"
    if reading["count"] == 1:
        return "ONE (aimable by count)"
    return "TWO OR MORE (ambiguous - a count cannot aim)"


async def _measure(page: Any) -> dict[str, Any]:
    """One allowlisted navigation and three reads. No mutation anywhere."""
    readonly.assert_read_url(TARGET_URL)
    landed = await BROWSER.goto(page, TARGET_URL)
    census = await dom.read_surface_census(page)
    file_inputs = await dom.read_file_inputs(page, census=census)
    compose_fields = await dom.read_compose_fields(page)
    return {
        "landed": landed,
        "census": census,
        "file_inputs": file_inputs,
        "compose_fields": compose_fields,
    }


async def _run() -> int:
    # THE DOOR ANSWERS, not this script. If the address is not on the
    # allowlist this stops here, before the profile lock is touched and
    # before any browser session is opened.
    try:
        readonly.assert_read_url(TARGET_URL)
    except Exception as exc:
        print(f"REFUSED BY ALLOWLIST: {type(exc).__name__}: {exc}")
        print("Nothing was opened. Exiting without navigating.")
        return 3

    print(
        f"ALLOWLIST CHECK: PASS -- {TARGET_URL!r} is a permitted read "
        "surface (readonly.assert_read_url)."
    )
    print(
        f"CDP config: attach={config.CDP_ATTACH!r} port={config.CDP_PORT!r} "
        f"host={config.CDP_HOST!r}"
    )
    if not config.CDP_ATTACH:
        print(
            "REFUSING: LINKEDIN_CDP_ATTACH is not set (or not truthy). "
            "Proceeding would launch a second Chrome on the shared profile "
            "instead of attaching to the operator's own. Nothing was opened."
        )
        return 4

    holder = profile_lock.live_holder()
    if holder is not None:
        print(
            f"REFUSING: the Chrome profile is locked by pid {holder}. "
            "Nothing was opened."
        )
        return 2

    profile_lock.acquire()
    try:
        await BROWSER.start()
        async with BROWSER.session() as page:
            from linkedin_server.auth import assert_not_authwall

            out = await _measure(page)
            assert_not_authwall(out["landed"], surface=TARGET_LABEL)

            census = out["census"]
            reading = out["file_inputs"]
            compose_fields = out["compose_fields"]

            print(f"--- {TARGET_LABEL} ({TARGET_URL})")
            print(
                f"    served:        "
                f"{_relation(out['landed'], TARGET_URL)}"
            )
            print(f"    page counts:   {census['counts']}")
            print(
                f"    controls_read: {census['controls_read']} "
                f"truncated={census['truncated']}"
            )
            print(_fmt_compose_fields(compose_fields))
            print(_fmt_file_inputs(reading))
            verdict = _verdict(reading, compose_fields)
            print(f"    VERDICT: {verdict}")
        return 0
    finally:
        await BROWSER.stop()
        profile_lock.release()


def _print_mutation_scan() -> None:
    """Prove the zero-mutation claim rather than assert it, over THIS file."""
    source = Path(__file__).read_text(encoding="utf-8")
    hits = readonly.scan_source_for_mutations(source)
    print(f"scan_source_for_mutations(own source): {len(hits)} hit(s)")
    for lineno, kind, line in hits:
        print(f"  line {lineno} [{kind}]: {line}")


# THE ADDRESS IS NOT PRINTED, AND THE COPY IS DELIBERATE.
#
# `tests/test_navigation_is_never_derived.py` refuses a navigation-derived
# url reaching a print, because the operator's own slug reached a
# transcript three times. This probe originally printed `out['landed']`
# and the guard PASSED it -- measured 2026-09-05, and the pass is a
# property of the guard rather than of the line: the same value printed
# through the bare name `landed` is caught, and printed through a DICT
# SUBSCRIPT is not. Riding through that gap would have been shipping on
# an instrument's blind spot, so this takes the sanctioned route instead.
#
# BYTE-IDENTICAL TO THE COPY IN `_probe_groups_events_live.py`, which
# `test_every_relation_definition_is_byte_identical` requires and which is
# why it was EXTRACTED rather than retyped.
def _relation(landed: str, asked: str) -> str:
    """Did the address serve, or did LinkedIn send us somewhere else?

    THE INTERESTS LESSON, applied. ``/in/me/details/interests/`` is on the
    allowlist and REDIRECTS to the profile, so an admitted address is not a
    served one -- and a probe that does not compare the landed url to the
    requested one cannot tell those apart.

    RETURNS A RELATION AND NEVER A URL. Every branch below yields a literal or
    an integer depth; no part of either input survives into the result. The
    depths are taken with ``len`` rather than a helper, because counting a
    thing is the discipline this package uses INSTEAD of printing it, and
    ``tests/test_navigation_is_never_derived.py`` recognises that form.

    ITS LOCALS ARE NAMED FOR THIS FUNCTION, and that is not cosmetic. The
    consent guard tracks tainted names ACROSS A WHOLE MODULE, not per scope,
    so a local called ``before`` here made every ``before`` in this file read
    as navigation-derived -- including three in the cost report, which are
    tallies of shaped control names and touch no url at all. Three of that
    guard's four findings against this file were that collision.
    """
    if str(landed) == str(asked):
        return "SERVED, exact"
    asked_depth = len([seg for seg in urlsplit(str(asked)).path.split("/") if seg])
    landed_depth = len([seg for seg in urlsplit(str(landed)).path.split("/") if seg])
    if asked_depth != landed_depth:
        return f"REDIRECTED, path depth {asked_depth} -> {landed_depth}"
    return "SERVED, same depth, different url"


def main() -> int:
    try:
        code = asyncio.run(_run())
    except Exception as exc:
        print(f"READ FAILED: {type(exc).__name__}: {exc}")
        code = 1
    _print_mutation_scan()
    return code


if __name__ == "__main__":
    sys.exit(main())
