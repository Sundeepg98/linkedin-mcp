"""FIRE ``linkedin_group_page`` AND ``linkedin_company_page_counts`` LIVE.

Three census rows were built and merged on 2026-09-20 and all three sat
COVERED-UNFIRED, which in this repository means built, reviewed, tested and
never once run against the thing it is about:

    N 175   linkedin_group_page(group_id)              group_page.py
    N 33    linkedin_company_page_counts(org_id)       company_root.py
    N 54    the same tool, the same page load          company_root.py

## THE INPUTS ARE RE-DERIVED, NEVER TYPED, AND THAT IS THE EVIDENCE DESIGN

Nine rows were once found resting on gitignored scratch paths, so a fired proof
has to be re-derivable from tracked files or from a re-runnable script. A group
id and an organisation id are both identifiers of a real account's real
affiliations, so neither may be written into a tracked file -- which would
normally leave the evidence resting on a gitignored note again.

**SO THIS SCRIPT DERIVES ITS OWN INPUTS EVERY RUN.** The group ids come from
``linkedin_group_memberships`` and the organisation ids from
``linkedin_followed_companies``, both shipped tools, both called here through
the registry. Nothing is hardcoded, nothing is read from a scratch file, and
re-running this script reproduces the whole chain from the account itself.

**NO IDENTIFIER IS EVER PRINTED.** Not a group id, not an organisation id, not
a landed url. They are written to the gitignored ``_state/`` and what reaches a
terminal is counts, closed-alphabet verdicts and integers.

## ``N 33`` / ``N 54`` MEASURE LINKEDIN'S WORDING AS WELL AS ITS COUNT

``company_root.COUNT_PHRASES`` is an unmeasured guess -- ``company_page.py``
says nobody in this repository has ever opened a company Page -- and a phrase
that does not render reads ``phrase_not_drawn``, never a count of zero. So the
first fire answers two questions at once, and it is built to keep them apart:

* ``count_read``        the phrase was found AND a number sat beside it
* ``phrase_not_drawn``  the page rendered and no shipped phrase matched
* ``reader_blind``      the page did not render for this reader at all

**N GREATER THAN ONE, DELIBERATELY.** A firing wave last week nearly banked a
field reading 4-true / 0-false at n=4 which read 9/2 at n=11. One company Page
answering ``count_read`` proves the wording on one page; one answering
``phrase_not_drawn`` proves nothing on its own, because an account with no
connection at that employer draws no such line either. Only a SPREAD over
several Pages can separate "the words are wrong" from "the line is absent",
so this fires at up to :data:`DEFAULT_ORGS` of them and reports the
distribution.

## BOUNDS

**ATTACH ONLY** -- refuses without ``LINKEDIN_CDP_ATTACH``, so it can never
launch a second Chrome against the persistent profile.

**READS ONLY.** Four shipped read tools. Nothing is pressed, joined, followed,
saved or submitted; ``writes_enabled`` is untouched and no confirm token exists
anywhere in this file.

**RATE.** Every navigation goes through ``BROWSER.goto``, which holds the
shipped minimum interval between loads. The page count is bounded by the two
``--groups`` / ``--orgs`` caps and is printed.

USAGE::

    set LINKEDIN_CDP_ATTACH=1
    <python> scripts/_probe_the_three_fires.py
    <python> scripts/_probe_the_three_fires.py --groups 3 --orgs 8

Resolve ``<python>`` with the interpreter you are already running. Never
``REPO / "venv"``: ``venv/`` is gitignored and absent in every worktree.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import company_root, config, group_page  # noqa: E402
from linkedin_server.server import mcp  # noqa: E402

#: How many of each to fire at unless told otherwise. The organisation cap is
#: the larger one for the reason the module docstring gives: the wording
#: question is only answerable across a spread.
DEFAULT_GROUPS = 3
DEFAULT_ORGS = 6

EXERCISED = (
    "linkedin_server/group_page.py",
    "linkedin_server/company_root.py",
    "linkedin_server/company_page.py",
    "linkedin_server/groups.py",
    "linkedin_server/dom.py",
    "linkedin_server/server.py",
)


def provenance() -> dict[str, Any]:
    """This run's git head and the sha256 of every module it exercises."""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        head = "unavailable:" + type(exc).__name__
    shas: dict[str, str] = {}
    for relative in EXERCISED:
        try:
            shas[relative] = hashlib.sha256(
                (REPO / relative).read_bytes()
            ).hexdigest()
        except Exception as exc:  # noqa: BLE001
            shas[relative] = "unavailable:" + type(exc).__name__
    return {"git_head": head, "sha256": shas}


async def fire(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call one shipped tool THROUGH THE REGISTRY and return its payload.

    Through the registry rather than as a python coroutine, because that is
    what a census row means when it says a tool fired: the registration, the
    argument coercion and the published envelope are all part of what is
    being proven.
    """
    result = await mcp.call_tool(name, arguments)
    payload = getattr(result, "structured_content", None) or result
    if isinstance(payload, dict) and "result" in payload:
        payload = payload["result"]
    if not isinstance(payload, dict):
        return {"ok": False, "error": "unexpected_payload_type"}
    return payload


def digits_only(values: Any) -> list[str]:
    """Keep only bounded ASCII-digit runs. A non-numeric segment is a SLUG.

    Filtering here rather than trusting the upstream tool is deliberate: this
    script is about to interpolate whatever comes back into an address, and a
    slug is a name.
    """
    out: list[str] = []
    for value in list(values or []):
        text = str(value).strip()
        if text and set(text) <= set("0123456789") and len(text) <= 20:
            out.append(text)
    return out


async def harvest_group_ids(limit: int) -> dict[str, Any]:
    """Group ids, from ``linkedin_group_memberships``. NEVER PRINTED."""
    payload = await fire("linkedin_group_memberships", {})
    memberships = dict(payload.get("memberships") or {})
    ids = digits_only(memberships.get("identifiers"))
    return {
        "ok": bool(payload.get("ok")),
        "error": payload.get("error"),
        "pages_loaded": payload.get("pages_loaded"),
        "distinct": memberships.get("distinct"),
        "usable": len(ids),
        "ids": ids[:limit],
    }


async def harvest_org_ids(limit: int) -> dict[str, Any]:
    """Numeric Page ids, from ``linkedin_followed_companies``. NEVER PRINTED."""
    payload = await fire("linkedin_followed_companies", {"limit": 50})
    rows = payload.get("pages")
    rows = list(rows) if isinstance(rows, (list, tuple)) else []
    candidates: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in ("company_id", "page_id", "id", "identifier"):
            found = digits_only([row.get(key)])
            if found:
                candidates.append(found[0])
                break
    # Order preserved, duplicates dropped: the same Page twice is one reading,
    # not two, and a denominator inflated by duplicates is the shape this
    # repository already convicted once.
    seen: set[str] = set()
    unique = [i for i in candidates if not (i in seen or seen.add(i))]
    return {
        "ok": bool(payload.get("ok")),
        "error": payload.get("error"),
        "rows_seen": len(rows),
        "usable": len(unique),
        "ids": unique[:limit],
    }


def group_row(payload: dict[str, Any]) -> dict[str, Any]:
    """One ``linkedin_group_page`` firing, reduced to integers and literals."""
    reach = dict(payload.get("reach") or {})
    state = reach.get("state")
    return {
        "ok": bool(payload.get("ok")),
        "error": payload.get("error"),
        "state": state if state in group_page.REACH_STATES else None,
        "reached": reach.get("reached"),
        "landed_on_the_same_group": payload.get("landed_on_the_same_group"),
        "anchors_seen": payload.get("anchors_seen"),
        "feed_update_anchors": payload.get("feed_update_anchors"),
        "member_profile_anchors": payload.get("member_profile_anchors"),
        "other_internal_anchors": payload.get("other_internal_anchors"),
        "values_refused": payload.get("values_refused"),
    }


def org_row(payload: dict[str, Any]) -> dict[str, Any]:
    """One ``linkedin_company_page_counts`` firing, reduced the same way."""
    counts = dict(payload.get("counts") or {})
    by_kind = dict(counts.get("by_kind") or {})
    out: dict[str, Any] = {
        "ok": bool(payload.get("ok")),
        "error": payload.get("error"),
        "redirected": payload.get("redirected"),
        "elements_walked": counts.get("elements_walked"),
        "chunks_considered": counts.get("chunks_considered"),
        "chunks_capped": counts.get("chunks_capped"),
        "hidden_subtrees_skipped": counts.get("hidden_subtrees_skipped"),
        "non_content_skipped": counts.get("non_content_skipped"),
        "matches_refused": counts.get("matches_refused"),
    }
    for kind in company_root.COUNT_KINDS:
        verdict = by_kind.get(kind)
        verdict = verdict if isinstance(verdict, dict) else {}
        state = verdict.get("state")
        numeral = verdict.get("numeral")
        out[kind] = {
            "state": state if state in company_root.READING_STATES else None,
            "value": verdict.get("value"),
            "numeral": numeral if numeral in company_root.NUMERAL_SHAPES else None,
        }
    return out


async def run(groups_wanted: int, orgs_wanted: int) -> dict[str, Any]:
    if not config.CDP_ATTACH:
        raise SystemExit(
            "REFUSING TO RUN. Set LINKEDIN_CDP_ATTACH=1 first. Without it this "
            "would LAUNCH a second Chrome on the persistent profile."
        )

    # THE TAB IS GIVEN BACK AT THE END. See
    # ``_probe_control_paths_live.run`` for the measurement: an abandoned tab
    # lengthens the NEXT probe's CDP handshake, and five of them on a loaded
    # box turned the sixth attach into eight ``browser_unavailable`` results
    # that looked exactly like a dead browser.
    from linkedin_server.browser import BROWSER

    try:
        return await _fire_everything(groups_wanted, orgs_wanted)
    finally:
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - teardown noise, never fatal
            print("teardown raised " + type(exc).__name__)


async def _fire_everything(
    groups_wanted: int, orgs_wanted: int
) -> dict[str, Any]:
    result: dict[str, Any] = {"provenance": provenance()}

    # -- N 175 -----------------------------------------------------------
    harvest = await harvest_group_ids(groups_wanted)
    result["group_harvest"] = {
        key: value for key, value in harvest.items() if key != "ids"
    }
    result["group_ids_count"] = len(harvest["ids"])
    group_fires: list[dict[str, Any]] = []
    for identifier in harvest["ids"]:
        payload = await fire("linkedin_group_page", {"group_id": identifier})
        group_fires.append(group_row(payload))
    result["group_fires"] = group_fires

    # -- N 33 / N 54 -----------------------------------------------------
    org_harvest = await harvest_org_ids(orgs_wanted)
    result["org_harvest"] = {
        key: value for key, value in org_harvest.items() if key != "ids"
    }
    result["org_ids_count"] = len(org_harvest["ids"])
    org_fires: list[dict[str, Any]] = []
    for identifier in org_harvest["ids"]:
        payload = await fire(
            "linkedin_company_page_counts", {"organisation_id": identifier}
        )
        org_fires.append(org_row(payload))
    result["org_fires"] = org_fires

    # THE IDS TRAVEL IN THE RAW FILE ONLY, which lands under the gitignored
    # _state/. They are affiliations of a real account and a tracked file may
    # not carry one.
    result["_ids"] = {
        "groups": harvest["ids"],
        "orgs": org_harvest["ids"],
    }
    return result


def distribution(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    """How many firings landed in each state. THE DENOMINATOR IS THE POINT."""
    out: dict[str, int] = {}
    for row in rows:
        token = row.get(key)
        if isinstance(token, dict):
            token = token.get("state")
        name = str(token)
        out[name] = out.get(name, 0) + 1
    return dict(sorted(out.items()))


def summarise(result: dict[str, Any]) -> int:
    print("")
    print("THE THREE FIRES")
    print("=" * 78)

    groups = result["group_fires"]
    print("")
    print("N 175  linkedin_group_page -- %d firing(s)" % len(groups))
    print("  harvest: " + json.dumps(result["group_harvest"], sort_keys=True))
    for index, row in enumerate(groups):
        print(
            "  fire %d: state=%-13s reached=%-5s same_group=%-5s "
            "anchors=%-4s feed=%-4s member=%-4s other=%-4s refused=%s"
            % (
                index,
                row["state"],
                row["reached"],
                row["landed_on_the_same_group"],
                row["anchors_seen"],
                row["feed_update_anchors"],
                row["member_profile_anchors"],
                row["other_internal_anchors"],
                row["values_refused"],
            )
        )
        if not row["ok"]:
            print("          NOT OK: " + str(row["error"]))
    print("  state distribution: " + json.dumps(distribution(groups, "state")))

    orgs = result["org_fires"]
    print("")
    print(
        "N 33 / N 54  linkedin_company_page_counts -- %d firing(s)" % len(orgs)
    )
    print("  harvest: " + json.dumps(result["org_harvest"], sort_keys=True))
    for index, row in enumerate(orgs):
        at_org = row.get("connections_at_organisation", {})
        following = row.get("connections_following_page", {})
        print(
            "  fire %d: redirected=%-5s elements=%-6s chunks=%-6s "
            "hidden_skipped=%-4s non_content=%s"
            % (
                index,
                row["redirected"],
                row["elements_walked"],
                row["chunks_considered"],
                row["hidden_subtrees_skipped"],
                row["non_content_skipped"],
            )
        )
        print(
            "          N 33 at_org:   state=%-17s value=%-8s numeral=%s"
            % (at_org.get("state"), at_org.get("value"), at_org.get("numeral"))
        )
        print(
            "          N 54 following: state=%-17s value=%-8s numeral=%s"
            % (
                following.get("state"),
                following.get("value"),
                following.get("numeral"),
            )
        )
        if not row["ok"]:
            print("          NOT OK: " + str(row["error"]))
    print(
        "  N 33 distribution: "
        + json.dumps(distribution(orgs, "connections_at_organisation"))
    )
    print(
        "  N 54 distribution: "
        + json.dumps(distribution(orgs, "connections_following_page"))
    )
    print("=" * 78)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--groups", type=int, default=DEFAULT_GROUPS)
    parser.add_argument("--orgs", type=int, default=DEFAULT_ORGS)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    destination = Path(
        args.out or (REPO / "_state" / "the-three-fires.json")
    )
    result = asyncio.run(run(args.groups, args.orgs))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    code = summarise(result)
    print("")
    print("git head: " + str(result["provenance"]["git_head"]))
    for relative, digest in sorted(result["provenance"]["sha256"].items()):
        print("  %-38s %s" % (relative, digest[:16]))
    print(
        "raw json: " + destination.name + " (gitignored _state/; it is the "
        "ONLY place the identifiers appear)"
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
