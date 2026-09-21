"""CAN ``group_page.reachability`` EVER REACH ITS POSITIVE BRANCH? MEASURE IT.

``linkedin_group_page`` fired for the first time on 2026-09-21 against THREE
groups this account is a MEMBER of, and returned ``ambiguous`` on all three:

    fire 0   anchors 86   feed 0   member 16   other 57   same_group True
    fire 1   anchors 35   feed 0   member  3   other 26   same_group True
    fire 2   anchors 47   feed 0   member  9   other 28   same_group True

``ambiguous`` is that module's honest branch and it is documented as such --
*a membership gate, an empty group and a restyle that moved the permalink all
draw a page with no post anchors, and nothing in this process can separate
them*. But three of three, on groups the account BELONGS to, on pages drawing
86, 35 and 47 anchors, is a different shape of result from an occasional
ambiguity. It is what a verdict looks like when its positive branch cannot be
reached at all.

**THE POSITIVE BRANCH IS GATED ON ONE ROUTE CLASS.** ``feed_drawn`` requires
``anchors.ROUTE_CLASSES``'s ``feed_update``, which is the fixed-segment rule
over ``/feed/update/``. If LinkedIn's group feed permalinks do not wear that
route, then ``feed_drawn`` is unreachable on every group forever, gated or
not -- and a reader whose positive verdict cannot occur is not reporting an
ambiguity, it is failing to a branch that happens to be worded honestly.

**A CHECK THAT CANNOT FAIL AND A VERDICT THAT CANNOT FIRE ARE THE SAME
DEFECT SEEN FROM TWO SIDES**, and this repository has been counting the first
for two days.

## WHAT THIS DOES

One navigation per group, to an address the read allowlist already admits and
``linkedin_group_page`` already opens. It captures the page to the gitignored
``_state/`` and then censuses the HREFS OFFLINE by leading path segment, so
the answer is a distribution over route shapes rather than a list of links.

**NO HREF IS EVER PRINTED.** What reaches a terminal is the leading segment of
each route and a count -- ``/feed/`` 0, ``/in/`` 16, and so on. A leading
segment is a route name this package already ships in
``anchors.ROUTE_CLASSES``; the entity segment after it is the part that can be
a name, and it is never rendered.

USAGE::

    set LINKEDIN_CDP_ATTACH=1
    <python> scripts/_probe_group_feed_permalinks.py --groups 3
    <python> scripts/_probe_group_feed_permalinks.py --from-raw
"""

from __future__ import annotations

import argparse
import asyncio
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import anchors, config, group_page  # noqa: E402
from linkedin_server.server import mcp  # noqa: E402

_HREF = re.compile(r'href="([^"]*)"', re.IGNORECASE)

#: THE HOSTS THAT ARE THIS PLATFORM. An absolute href to one of them is an
#: INTERNAL route and must be resolved to its path before it is classified.
#:
#: **THE FIRST VERSION OF THIS PROBE DID NOT DO THAT AND ITS HEADLINE WAS
#: THEREFORE UNSOUND.** It bucketed every absolute href as
#: ``(external-or-absolute)`` -- 108, 58 and 70 of them on the three pages --
#: and then concluded from the remainder that NO anchor wears a ``/feed``
#: route. An absolute ``https://www.linkedin.com/feed/update/...`` would have
#: sat inside the bucket it never looked in, so the measurement could not have
#: refuted its own conclusion. That is the same defect this wave is auditing,
#: committed by the instrument auditing it.
_LINKEDIN_HOSTS = ("linkedin.com", "www.linkedin.com", "lnkd.in")

#: THE SECOND SEGMENT IS RENDERED ONLY IF IT IS ONE OF THESE WORDS. Everything
#: else becomes ``<entity>``.
#:
#: **THE FIRST VERSION RENDERED IT UNCONDITIONALLY AT DEPTH 2, AND THE
#: DOCSTRING SAYING IT NEVER WOULD WAS SIMPLY FALSE.** ``/in/<slug>/`` is two
#: segments, so a depth-2 route printed a member's vanity slug -- a NAME -- for
#: the account's own profile and for three third parties, into a terminal, on
#: the first run. A blocklist could not have stopped that; only deciding which
#: words are ALLOWED can, which is the same shape as the readers' own
#: ship-a-vocabulary-in rule and as the fix the wording probe needed an hour
#: earlier for the same class of mistake.
#: THE FIRST SEGMENT'S ALLOWLIST. A route word this package already knows, or
#: the segment is rendered ``<root>``. See :func:`route_of` for why segment one
#: needs one at all.
ROOT_WORDS = frozenset(
    {
        "in",
        "company",
        "school",
        "groups",
        "jobs",
        "feed",
        "messaging",
        "help",
        "premium",
        "mynetwork",
        "notifications",
        "learning",
        "events",
        "posts",
        "pulse",
        "newsletters",
        "search",
        "psettings",
        "settings",
        "accessibility",
        "legal",
        "ad",
        "checkpoint",
        "uas",
        "login",
        "signup",
        "my-items",
        "analytics",
        "services",
        "showcase",
        "talent",
        "sales",
        "business",
        "interstitial",
        "redir",
        "comm",
        "e",
    }
)

ROUTE_WORDS = frozenset(
    {
        "update",
        "search",
        "results",
        "view",
        "collections",
        "recommended",
        "thread",
        "my-premium",
        "my-items",
        "discover-hub",
        "discovery-see-all",
        "invite-connect",
        "network-manager",
        "group",
        "answer",
        "posts",
        "people",
        "about",
        "jobs",
        "feed",
        "new",
        "all",
        "me",
    }
)

EXERCISED = (
    "linkedin_server/group_page.py",
    "linkedin_server/anchors.py",
    "linkedin_server/dom.py",
)


def provenance() -> dict[str, Any]:
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
    shas = {}
    for relative in EXERCISED:
        try:
            shas[relative] = hashlib.sha256(
                (REPO / relative).read_bytes()
            ).hexdigest()
        except Exception as exc:  # noqa: BLE001
            shas[relative] = "unavailable:" + type(exc).__name__
    return {"git_head": head, "sha256": shas}


def route_of(href: str) -> str:
    """A route SHAPE. Segment one verbatim; segment two only if it is a word.

    THE ENTITY SEGMENT IS REPLACED, NOT DROPPED LATER. A slug is a name and a
    feed urn identifies an author, so neither may be rendered -- and an
    absolute href to this platform is resolved to its path FIRST, or the
    census cannot see the very routes it is looking for. See
    :data:`ROUTE_WORDS` and :data:`_LINKEDIN_HOSTS` for the two defects that
    wording repairs.
    """
    text = str(href or "").strip()
    if not text:
        return "(empty)"
    if text.startswith("#"):
        return "(fragment)"

    if "//" in text:
        remainder = text.split("//", 1)[1]
        host = remainder.split("/", 1)[0].split("@")[-1].split(":")[0].lower()
        if host not in _LINKEDIN_HOSTS:
            return "(external)"
        text = "/" + (remainder.split("/", 1)[1] if "/" in remainder else "")
    elif not text.startswith("/"):
        return "(relative)"

    segments = [s for s in text.split("?")[0].split("#")[0].split("/") if s]
    if not segments:
        return "/"
    # SEGMENT ONE IS ALLOWLISTED TOO, AND THAT IS THE THIRD REPAIR OF THIS ONE
    # CLASS IN ONE WAVE. Resolving absolutes fixed the blindness and
    # allowlisting segment two fixed ``/in/<slug>/``, and a root-level route
    # was STILL rendered verbatim -- so a bare ``/<something>/`` printed
    # whatever LinkedIn put there. Closing the class means EVERY rendered
    # segment comes from a word this file wrote down; nothing is rendered
    # because it merely looked harmless.
    first = segments[0].lower()
    head = first if first in ROOT_WORDS else "<root>"
    if len(segments) == 1:
        return "/" + head + "/"
    second = segments[1].lower()
    rendered = second if second in ROUTE_WORDS else "<entity>"
    return "/" + head + "/" + rendered + "/"


def leaks(route: str) -> bool:
    """Would this rendered route carry a free-form segment? THE SELF-CHECK.

    Run over every route the census produces, so the probe convicts itself
    rather than relying on the reasoning above having been right. It is the
    control the first version did not have and needed.
    """
    if not route.startswith("/"):
        return False
    parts = [p for p in route.split("/") if p]
    if not parts:
        return False
    if parts[0] != "<root>" and parts[0] not in ROOT_WORDS:
        return True
    if len(parts) < 2:
        return False
    return parts[1] != "<entity>" and parts[1] not in ROUTE_WORDS


def census(html: str) -> dict[str, int]:
    counter: collections.Counter[str] = collections.Counter()
    for href in _HREF.findall(html):
        counter[route_of(href)] += 1
    # THE SELF-CHECK RUNS BEFORE THE RESULT IS RETURNED, not after it is
    # printed. A route that would carry a free-form segment stops this probe
    # rather than being tidied, because a tidied leak is still a leak that
    # nobody has to explain.
    offenders = [route for route in counter if leaks(route)]
    if offenders:
        raise SystemExit(
            "REFUSING TO PUBLISH: %d rendered route(s) carry a free-form "
            "segment. The segment is not printed here. Widen ROUTE_WORDS only "
            "for words that are ROUTES, never for values." % len(offenders)
        )
    return dict(counter)


def digits_only(values: Any) -> list[str]:
    out = []
    for value in list(values or []):
        text = str(value).strip()
        if text and set(text) <= set("0123456789") and len(text) <= 20:
            out.append(text)
    return out


async def fire(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = await mcp.call_tool(name, arguments)
    payload = getattr(result, "structured_content", None) or result
    if isinstance(payload, dict) and "result" in payload:
        payload = payload["result"]
    return payload if isinstance(payload, dict) else {"ok": False}


async def run(wanted: int) -> dict[str, Any]:
    from linkedin_server.browser import BROWSER

    if not config.CDP_ATTACH:
        raise SystemExit("REFUSING TO RUN. Set LINKEDIN_CDP_ATTACH=1 first.")

    # THE TAB IS GIVEN BACK AT THE END -- see
    # ``_probe_control_paths_live.run`` for what an abandoned one costs the
    # next probe's attach.
    try:
        return await _census_groups(BROWSER, wanted)
    finally:
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - teardown noise, never fatal
            print("teardown raised " + type(exc).__name__)


async def _census_groups(BROWSER: Any, wanted: int) -> dict[str, Any]:
    memberships = await fire("linkedin_group_memberships", {})
    ids = digits_only(
        dict(memberships.get("memberships") or {}).get("identifiers")
    )[:wanted]

    raw_dir = REPO / "_state" / "group-feed-permalinks"
    raw_dir.mkdir(parents=True, exist_ok=True)

    pages: list[dict[str, Any]] = []
    for position, identifier in enumerate(ids):
        address = group_page.group_page_url(identifier)
        if not address.get("built"):
            continue
        async with BROWSER.session() as page:
            try:
                landed = await BROWSER.goto(page, address["url"])
                reading = await group_page.read_group_page(page)
                html = await page.content()
            finally:
                # CLOSE THE PAGE, NEVER THE CONTEXT -- see
                # ``_probe_company_root_wording`` for the measurement behind
                # this. The tab is ours; the context is his.
                if not page.is_closed():
                    await page.close()
        (raw_dir / ("group-%02d.html" % position)).write_text(
            html, encoding="utf-8"
        )
        pages.append(
            {
                "index": position,
                "landed_on_the_same_group": group_page.landed_on_the_same_group(
                    landed, address["identifier"]
                ),
                "reader": {
                    "anchors_seen": reading["anchors_seen"],
                    "feed_update_anchors": reading["feed_update_anchors"],
                    "member_profile_anchors": reading["member_profile_anchors"],
                    "other_internal_anchors": reading["other_internal_anchors"],
                },
                "verdict": group_page.reachability(reading, True)["state"],
                "route_census": census(html),
            }
        )
    return {"provenance": provenance(), "pages": pages}


def from_raw() -> dict[str, Any]:
    raw_dir = REPO / "_state" / "group-feed-permalinks"
    pages = []
    for index, path in enumerate(sorted(raw_dir.glob("group-*.html"))):
        html = path.read_text(encoding="utf-8", errors="replace")
        pages.append(
            {
                "index": index,
                "landed_on_the_same_group": None,
                "reader": None,
                "verdict": None,
                "route_census": census(html),
            }
        )
    return {"provenance": provenance(), "pages": pages}


def summarise(result: dict[str, Any]) -> int:
    print("")
    print("CAN feed_drawn EVER FIRE? ROUTE CENSUS OF A GROUP PAGE")
    print("=" * 78)
    total: collections.Counter[str] = collections.Counter()
    for page in result["pages"]:
        print("")
        print("group %02d   verdict=%s   reader=%s"
              % (page["index"], page["verdict"], json.dumps(page["reader"] or {})))
        rows = sorted(
            page["route_census"].items(), key=lambda pair: (-pair[1], pair[0])
        )
        for route, count in rows[:14]:
            print("    %-34s %4d" % (route, count))
        if len(rows) > 14:
            print("    ... %d more route(s)" % (len(rows) - 14))
        for route, count in page["route_census"].items():
            total[route] += count

    print("")
    print("THE ONE QUESTION")
    print("-" * 78)
    feed_routes = {
        route: count for route, count in total.items() if route.startswith("/feed")
    }
    print("  anchors.ROUTE_CLASSES gates feed_drawn on the /feed/update/ route.")
    print("  routes under /feed seen across all pages: " + (json.dumps(feed_routes) or "{}"))
    if not feed_routes:
        print("")
        print("  ZERO. No anchor on any group page wears a /feed route, so")
        print("  group_page.reachability's feed_drawn branch DID NOT FIRE")
        print("  because it COULD NOT. ambiguous is not an ambiguity here.")
    print("=" * 78)
    print("")
    print("ROUTE CLASSES THIS PACKAGE SHIPS: " + ", ".join(anchors.ROUTE_CLASSES))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--groups", type=int, default=3)
    parser.add_argument("--from-raw", action="store_true")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    result = from_raw() if args.from_raw else asyncio.run(run(args.groups))
    destination = Path(
        args.out or (REPO / "_state" / "group-feed-permalinks.json")
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    code = summarise(result)
    print("git head: " + str(result["provenance"]["git_head"]))
    print("raw json: " + destination.name + " (gitignored _state/)")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
