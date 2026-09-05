"""A census that never presses a control reports a clean absence.

WHAT THIS IS FOR. ``ANALYTICS-CONTROLS-UNPRESSED`` (blocker 23, four reads:
filter the viewer data, notable viewers, the weekly trend graph, and top
locations / industries / companies). All four are said to be reachable by
pressing something on a page ``linkedin_who_viewed_me`` ALREADY OPENS. Nobody
has pressed anything there, so "the panel is not on the page" and "the panel is
behind a control this reader cannot see" are the same reading today.

THE SAME DEFECT HAS ALREADY FIRED HERE, TWICE, WHICH IS WHY THIS IS STRUCTURAL
RATHER THAN A HUNT:

* ``CENSUS_CONTROL_SELECTOR`` carries no menu role, so a census pointed at an
  open menu saw nothing and reported a clean absence (2026-09-04). The fix was
  a COUNT -- ``counts.menus`` and ``counts.menu_items`` -- not a wider
  selector, so the census can now say "I am blind here" instead of "empty".
* A tabbed category's rows are not in the document until its tab is pressed:
  the Companies category holds at least 20 rows in the tracked fixtures and
  renders ZERO on an unpressed capture.

## HOW A CONTROL THAT HIDES SOMETHING IS FOUND, AND WHY NOT BY ITS NAME

By ``aria-expanded="false"``, which the census ALREADY RETURNS on every record
and which nothing in this repository has ever read. That is the accessibility
contract for "this control discloses content that is not currently rendered" --
a property of the DOM rather than of a word somebody guessed would be on the
button. A name-matching press list ("Show more", "See all") is a probe set
chosen from the author's model of the risk, which is the failure this project
has now caught three times; ``aria-expanded`` is chosen from the branch
structure of the thing under test.

The vocabulary match is kept as a SECOND, weaker signal and reported beside the
first, never instead of it -- so a page that discloses without the attribute is
visible as a disagreement between two counts rather than invisible.

## WHAT PRESSING COSTS, MEASURED RATHER THAN ARGUED

Every press is on HIS OWN analytics page and every one is a DISCLOSURE: the
element says, in the DOM, that it expands content already fetched or about to
be. That is an argument, and this probe does not rest on it:

* ``dom.read_invitation_badge`` is read BEFORE the first press and AFTER the
  last, and the two are compared. That is this repository's standing way of
  proving a read did not spend a counter it walked past.
* The page's own control count is censused before and after, so a press that
  navigated away instead of expanding shows up as a collapse in the count
  rather than as a silent wrong reading.
* A press is REFUSED unless the element still reports ``aria-expanded="false"``
  at the moment of pressing. The census index is a position, and this package
  refuses to aim a press by position: the confirmation is re-read in the page,
  immediately before the press, off the element about to be pressed.

## WHAT MAY NOT BE PRESSED, AND IT IS ENFORCED INSIDE THE PAGE

A denylist of act words is applied to the element's own text IN THE PAGE, and
only an index and a boolean cross back. No accessible name leaves the browser
through this file. The denylist wins over both positive signals: a control that
is a disclosure AND carries an act word is not pressed, because a disclosure
that also sends something is exactly the case a structural rule gets wrong.

## WHAT LEAVES THIS PROCESS

Counts, relations, booleans and shaped control names that have been through
``dom.read_surface_census`` (which runs ``shape.census_shape`` and blanks the
name of any control pointing at a person). Plus analytics-tree PATH SHAPES,
gated in the page by a pattern that admits product route names and nothing
else; anything failing the gate is emitted as a marker and counted, never
printed. NO url is printed by this file, and nothing derived from a navigation
reaches a ``goto``.

## WHAT THIS PROBE CANNOT SETTLE

It cannot establish that a panel LinkedIn does not draw for this account is
absent for everybody, and it does not try. A zero here is a reading of one
Premium Career account on one day. What it CAN do is separate "not on the page"
from "behind a control", which is the only question ``ANALYTICS-CONTROLS-
UNPRESSED`` is filed against.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import AUTHWALL_MARKERS  # noqa: E402

#: MODULE-LEVEL LITERALS, which is what makes them navigable. Both addresses
#: are already on the read allowlist; this probe adds nothing to it and opens
#: nothing else.
PROFILE_VIEWS_URL = "https://www.linkedin.com/analytics/profile-views/"
SELF_PROFILE_URL = "https://www.linkedin.com/in/me/"
FEED_URL = "https://www.linkedin.com/feed/"
#: HIS OWN CONTENT ANALYTICS. Admitted to the read allowlist on 2026-09-05 on
#: the strength of the route discovery this same probe took: LinkedIn draws
#: this address twice on his profile and once on the feed, both of which this
#: server already opens. It is read TWICE here, because the entry that admits
#: it claims a badge measurement and a claim ahead of its evidence is what the
#: allowlist's own prose forbids.
CREATOR_CONTENT_URL = "https://www.linkedin.com/analytics/creator/content/"

#: Ceiling on presses per page. A cap is not a rule about WHICH controls may be
#: pressed -- that is the gate below -- it is a bound on how long a probe may
#: hold a browser several waves are sharing.
MAX_PRESSES = 12

#: Selection and refusal, run INSIDE the page so that no accessible name
#: crosses back. Returns one record per candidate: its index against the census
#: selector, which signals matched, and nothing else. The denylist is applied
#: to the element's own text and wins over both positive signals.
SELECT_JS = """
(cfg) => {
  const nodes = Array.from(document.querySelectorAll(cfg.controlSelector));
  const deny = cfg.deny;
  const vocab = cfg.vocab;
  const out = [];
  let denied = 0;
  let expandedAlready = 0;
  nodes.forEach((el, index) => {
    const expanded = el.getAttribute('aria-expanded');
    const raw = (el.getAttribute('aria-label') || el.textContent || '')
      .replace(/\\s+/g, ' ').trim().toLowerCase();
    const hitDeny = deny.some((word) => raw.indexOf(word) !== -1);
    const hitVocab = vocab.some((word) => raw.indexOf(word) !== -1);
    if (expanded === 'true') { expandedAlready += 1; }
    const isDisclosure = expanded === 'false';
    if (!isDisclosure && !hitVocab) { return; }
    if (hitDeny) { denied += 1; return; }
    out.push({
      index: index,
      disclosure: isDisclosure,
      vocab: hitVocab,
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute('role') || '',
      disabled: !!(el.disabled || el.getAttribute('aria-disabled') === 'true')
    });
  });
  return {
    total: nodes.length,
    denied: denied,
    expanded_already: expandedAlready,
    candidates: out
  };
}
"""

#: Confirm, at the moment of the press, that the element at this index is still
#: the disclosure the census said it was. Returns a boolean and nothing else.
#: THE INDEX IS A POSITION AND A POSITION IS NOT AN AIM -- this is what turns
#: one into the other, and it is re-read rather than remembered.
CONFIRM_JS = """
(cfg) => {
  const nodes = Array.from(document.querySelectorAll(cfg.controlSelector));
  const el = nodes[cfg.index];
  if (!el) { return {present: false}; }
  const raw = (el.getAttribute('aria-label') || el.textContent || '')
    .replace(/\\s+/g, ' ').trim().toLowerCase();
  return {
    present: true,
    expanded: el.getAttribute('aria-expanded'),
    denied: cfg.deny.some((word) => raw.indexOf(word) !== -1),
    tag: el.tagName.toLowerCase()
  };
}
"""

#: The analytics-tree route names LinkedIn itself links to, discovered rather
#: than guessed -- this is how ``CONTENT-ANALYTICS-SURFACE`` and
#: ``CREATOR-HUB-SURFACE`` get an address that was READ off the product instead
#: of one spelled from a help article. THE GATE IS THE POINT: a path is emitted
#: only if it is entirely lowercase route words, and anything else is counted
#: under a marker so the refusal keeps its evidence.
ANALYTICS_LINKS_JS = """
(cfg) => {
  const ok = /^\\/[a-z][a-z-]*(\\/[a-z][a-z-]*)*\\/?$/;
  const shapes = {};
  let withheld = 0;
  let offtree = 0;
  Array.from(document.querySelectorAll('a[href]')).forEach((a) => {
    let path = '';
    try { path = new URL(a.href, document.baseURI).pathname; } catch (e) { return; }
    if (!cfg.trees.some((t) => path.indexOf(t) === 0)) { offtree += 1; return; }
    if (!ok.test(path)) { withheld += 1; return; }
    shapes[path] = (shapes[path] || 0) + 1;
  });
  return {shapes: shapes, withheld: withheld, offtree: offtree};
}
"""

#: Act words. A control carrying one of these is never pressed, whatever its
#: ``aria-expanded`` says. Written as a module literal so the list is reviewable
#: in a diff rather than assembled at runtime.
DENY_WORDS = [
    "message", "invite", "connect", "follow", "unfollow", "apply", "save",
    "download", "export", "delete", "remove", "send", "post", "share",
    "report", "block", "withdraw", "subscribe", "unsubscribe", "buy",
    "upgrade", "pay", "purchase", "cancel", "endorse", "recommend", "react",
    "like", "comment", "sign out", "log out", "settings", "edit", "add",
]

#: The weaker, name-based signal, kept BESIDE the structural one and never
#: instead of it. A page that discloses without ``aria-expanded`` shows up as a
#: disagreement between two counts rather than as a clean absence -- which is
#: the entire failure this probe is named for.
VOCAB_WORDS = [
    "show more", "show all", "see more", "see all", "view more", "view all",
    "expand", "more analytics", "show less",
]


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


def _summarise(census: dict) -> dict:
    """The numbers a press is supposed to move, and NOTHING INVENTED.

    A KEY THIS CENSUS DOES NOT PUBLISH RAISES RATHER THAN READING AS ZERO, and
    that is not defensive style -- this function had ``main_chars`` in it on
    its first run and reported ``0`` on two pages that were both drawing
    thousands of characters. ``CENSUS_JS``'s ``counts`` block has no such key;
    ``main_chars`` belongs to ``read_search_appearances``'s own reader, and a
    ``.get(key) or 0`` turned "this instrument cannot see that" into "the page
    has none of it".

    That is the defect ``census_aggregate``'s own docstring records against
    ``container`` -- a field dropped in silence because nothing enumerated it
    -- reproduced inside the probe written to hunt for it. A zero that means
    "absent field" and a zero that means "measured none" are the same integer
    and only one of them is a reading.
    """
    counts = dict(census.get("counts") or {})
    wanted = ("menus", "menu_items", "dialogs", "links", "buttons", "forms")
    missing = [key for key in wanted if key not in counts]
    if missing:
        raise KeyError(
            f"the census published no {missing} -- reporting 0 for a key the "
            "instrument does not have is how an absence becomes a measurement"
        )
    controls = list(census.get("controls") or [])
    out = {
        "controls_read": int(census.get("controls_read") or 0),
        "disclosures_closed": len(
            [c for c in controls if c.get("aria_expanded") == "false"]
        ),
        "disclosures_open": len(
            [c for c in controls if c.get("aria_expanded") == "true"]
        ),
    }
    for key in wanted:
        out[key] = int(counts[key] or 0)
    return out


def _shape_tally(census: dict) -> dict:
    """How many times each control shape occurs, THROUGH ``census_aggregate``.

    ``read_surface_census`` does NOT apply ``census_redact_rare`` and says so
    in its own docstring: that rule needs a COUNT, and its records are not yet
    counted. A caller that tallies them itself and prints the keys has skipped
    the only step that separates ``Start A Post`` from a member's name.

    This function counted them by hand on its first run. It got away with it
    because the names that surfaced were product chrome -- which is luck, not
    a property, and the next page is the one with a person on it.
    """
    control_shapes, _href_shapes = shape.census_aggregate(
        list(census.get("controls") or [])
    )
    tally: dict[str, int] = {}
    for row in control_shapes:
        name = str(row.get("shape") or "")
        if not name:
            continue
        tally[name] = tally.get(name, 0) + int(row.get("count") or 0)
    return tally


async def _census(page) -> dict:
    return await dom.read_surface_census(page)


async def _badge(page, when: str) -> dict:
    """The pending-invitation nav badge. THE COST INSTRUMENT, not a garnish."""
    try:
        reading = await dom.read_invitation_badge(page)
    except Exception as exc:  # noqa: BLE001 -- a refusal is a result
        print(f"  badge {when}: UNREADABLE -- {type(exc).__name__}: {exc}")
        return {"unreadable": type(exc).__name__}
    print(f"  badge {when}: {json.dumps(reading, sort_keys=True)}")
    return reading


async def press_pass(page, label: str) -> dict:
    """Census TWICE, select, press, re-census. The delta IS the finding.

    THE SECOND UNPRESSED CENSUS IS NOT A RETRY. Neither of these surfaces has
    a ``CENSUS_SETTLED_CONTROLS`` entry, so the settle report answers
    ``unknown`` -- which is NOT a pass, and a delta taken against a
    half-rendered baseline measures the render rather than the press. Two
    unpressed readings that agree are what make the third number mean
    anything; two that disagree say the page had not settled and the delta
    below is void. Either way the probe says which.
    """
    print(f"\n--- {label}: unpressed census, reading 1 ---")
    first_census = await _census(page)
    first = _summarise(first_census)
    print(json.dumps(first, indent=2, sort_keys=True))

    await page.wait_for_timeout(1500)
    print(f"\n--- {label}: unpressed census, reading 2 (the baseline test) ---")
    unpressed_census = await _census(page)
    before = _summarise(unpressed_census)
    print(json.dumps(before, indent=2, sort_keys=True))
    settled = (first["controls_read"] == before["controls_read"])
    print(f"  BASELINE AGREES: {settled}  "
          f"({first['controls_read']} then {before['controls_read']})")
    if not settled:
        print("  THE TWO UNPRESSED READINGS DISAGREE. The delta below is a "
              "reading of the render, not of the press, and must not be "
              "quoted as one.")

    selection = await page.evaluate(  # readonly-ok
        SELECT_JS,
        {
            "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
            "deny": DENY_WORDS,
            "vocab": VOCAB_WORDS,
        },
    )
    candidates = list(selection.get("candidates") or [])
    structural = [c for c in candidates if c.get("disclosure")]
    vocab_only = [c for c in candidates if not c.get("disclosure")]
    print(f"\n  selector total      : {selection.get('total')}")
    print(f"  refused on act word : {selection.get('denied')}")
    print(f"  already expanded    : {selection.get('expanded_already')}")
    print(f"  closed disclosures  : {len(structural)}")
    print(f"  vocab-only matches  : {len(vocab_only)}")
    print("  THE TWO SIGNALS DISAGREEING IS ITSELF THE READING: a vocab-only "
          "match is a control that hides something without saying so in the "
          "DOM, and a closed disclosure with no vocab hit is one this "
          "repository would never have guessed by name.")

    pressed = 0
    refused_at_press = 0
    vanished = 0
    # BOTH LISTS ARE PRESSED, structural first. Pressing only the structural
    # ones and REPORTING a vocab-only count is this file's own headline defect
    # committed inside the file that names it: a candidate counted and never
    # pressed is an absence reported clean. The vocab-only ones carry no
    # ``aria-expanded``, so the confirmation gate below cannot demand one of
    # them -- it demands the ABSENCE of an act word instead, and the two
    # requirements are stated per list rather than merged into one rule that
    # would be wrong for both.
    for candidate in (structural + vocab_only)[:MAX_PRESSES]:
        index = int(candidate["index"])
        if candidate.get("disabled"):
            continue
        wants_disclosure = bool(candidate.get("disclosure"))
        check = await page.evaluate(  # readonly-ok
            CONFIRM_JS,
            {
                "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
                "index": index,
                "deny": DENY_WORDS,
            },
        )
        if not check.get("present"):
            vanished += 1
            continue
        if check.get("denied"):
            refused_at_press += 1
            continue
        if wants_disclosure and check.get("expanded") != "false":
            refused_at_press += 1
            continue
        locator = page.locator(dom.CENSUS_CONTROL_SELECTOR).nth(index)
        try:
            await locator.click(timeout=4000)
            pressed += 1
        except Exception as exc:  # noqa: BLE001 -- a failed press is a result
            print(f"  press {index}: FAILED {type(exc).__name__}")
        await page.wait_for_timeout(400)

    print(f"\n  pressed             : {pressed}")
    print(f"  refused at press    : {refused_at_press}")
    print(f"  vanished before press: {vanished}")

    print(f"\n--- {label}: pressed census ---")
    pressed_census = await _census(page)
    after = _summarise(pressed_census)
    print(json.dumps(after, indent=2, sort_keys=True))

    delta = {key: after[key] - before[key] for key in before}
    print(f"\n  DELTA: {json.dumps(delta, sort_keys=True)}")

    tally_unpressed = _shape_tally(unpressed_census)
    tally_pressed = _shape_tally(pressed_census)
    appeared = sorted(set(tally_pressed) - set(tally_unpressed))
    disappeared = sorted(set(tally_unpressed) - set(tally_pressed))
    print(f"  shaped names that APPEARED   ({len(appeared)}): "
          f"{json.dumps(appeared[:40])}")
    print(f"  shaped names that DISAPPEARED ({len(disappeared)}): "
          f"{json.dumps(disappeared[:40])}")

    return {
        "before": before,
        "after": after,
        "delta": delta,
        "pressed": pressed,
        "refused_at_press": refused_at_press,
        "closed_disclosures": len(structural),
        "vocab_only": len(vocab_only),
        "baseline_agrees": settled,
        "denied": int(selection.get("denied") or 0),
        "appeared": appeared,
        "disappeared": disappeared,
    }


#: THE TREES SEARCHED FOR AN ADDRESS. Discovery, not a guess: ``CONTENT-
#: ANALYTICS-SURFACE`` and ``CREATOR-HUB-SURFACE`` each want "allowlist +1",
#: and an allowlist should permit what LinkedIn DRAWS rather than what a help
#: article spells. The creator trees are here because the analytics tree alone
#: answered neither on the first run.
#:
#: ``/newsletters/`` AND ``/posts/`` ARE DELIBERATELY ABSENT, and the reason is
#: the gate rather than the tree. The gate admits an all-lowercase, digit-free
#: path -- which is a route name AND is also the shape of a newsletter slug. A
#: publication titled ``<name> by <author>`` slugs to exactly that, so those two
#: trees are the ones where the emission stops being a route and becomes a
#: title. Every tree below is LinkedIn's own product vocabulary with no member-
#: authored segment in it, which is what makes the gate sufficient here and
#: insufficient there. The newsletter routes are already read and owned
#: elsewhere; this probe does not need them.
LINK_TREES = ["/analytics/", "/creator/", "/dashboard/",
              "/mynetwork/network-manager/"]


async def analytics_routes(page) -> dict:
    """What these trees link to, read off LinkedIn rather than guessed."""
    found = await page.evaluate(  # readonly-ok
        ANALYTICS_LINKS_JS, {"trees": LINK_TREES}
    )
    shapes = dict(found.get("shapes") or {})
    print("\n  ANALYTICS ROUTES LINKED FROM THIS PAGE, path shapes only:")
    for path in sorted(shapes):
        print(f"    {path}   x{shapes[path]}")
    print(f"    withheld by the shape gate: {found.get('withheld')}")
    print(f"    links outside the searched trees: {found.get('offtree')}")
    return found


async def main() -> int:
    if os.environ.get("LINKEDIN_CDP_ATTACH") != "1":
        print("REFUSING: set LINKEDIN_CDP_ATTACH=1 and LINKEDIN_CDP_PORT. "
              "This probe must attach to the running Chrome rather than "
              "launching one -- the profile is shared and a launch is a "
              "browser DOWNGRADE.")
        return 2

    print(f"port : {os.environ.get('LINKEDIN_CDP_PORT')}")
    out: dict = {}

    async with BROWSER.session() as page:
        # PRESSING IS SCOPED TO THE ANALYTICS TREE. The last two are opened
        # for ROUTE DISCOVERY ONLY and nothing on them is pressed: they are
        # here to answer "what address does LinkedIn itself draw for the
        # creator surfaces", which is a different question from "what is
        # behind a control", and pressing the feed's chrome would answer
        # neither while spending a page several waves share.
        for label, address, press in (
            ("profile_views", PROFILE_VIEWS_URL, True),
            ("search_appearances", dom.SEARCH_APPEARANCES_URL, True),
            ("creator_content", CREATOR_CONTENT_URL, True),
            ("creator_content_again", CREATOR_CONTENT_URL, True),
            ("self_profile", SELF_PROFILE_URL, False),
            ("feed", FEED_URL, False),
        ):
            print("\n" + "=" * 70)
            print(f"SURFACE: {label}")
            print("=" * 70)
            try:
                landed = await BROWSER.goto(page, address)
            except Exception as exc:  # noqa: BLE001
                print(f"  NAVIGATION REFUSED: {type(exc).__name__}")
                out[label] = {"refused": type(exc).__name__}
                continue
            print(f"  {_relation(landed, address)}")
            if any(marker in landed for marker in AUTHWALL_MARKERS):
                print("  AUTHWALL -- nothing was read")
                out[label] = {"authwall": True}
                continue

            badge_a = await _badge(page, "before")
            routes = await analytics_routes(page)
            if not press:
                out[label] = {"routes": routes, "discovery_only": True}
                continue
            result = await press_pass(page, label)
            badge_b = await _badge(page, "after")

            first_count = badge_a.get("count")
            second_count = badge_b.get("count")
            moved = (first_count != second_count)
            print(f"\n  BADGE MOVED: {moved}  ({first_count} -> {second_count})")
            result["badge_moved"] = moved
            result["routes"] = routes
            out[label] = result

    print("\n" + "=" * 70)
    print("WHAT THIS SETTLES")
    print("=" * 70)
    for label, result in out.items():
        if result.get("discovery_only"):
            print(f"\n  {label}: opened for ROUTE DISCOVERY ONLY, nothing "
                  "pressed. See the route list above.")
            continue
        if not result.get("delta"):
            print(f"\n  {label}: NOT READ -- {json.dumps(result, sort_keys=True)}")
            continue
        delta = result["delta"]
        if result["closed_disclosures"] == 0 and result["vocab_only"] == 0:
            print(f"\n  {label}: NO CONTROL ON THIS PAGE HIDES ANYTHING that "
                  "either signal can see. That is a reading about the page AND "
                  "about the two detectors, and it is only worth what the "
                  "detectors are worth -- the menu count is the third signal "
                  "and it is reported above.")
            continue
        if result["pressed"] == 0:
            print(f"\n  {label}: {result['closed_disclosures']} closed "
                  "disclosures and NONE was pressed. The absence behind them "
                  "is UNKNOWN, not clean.")
            continue
        # ``main_chars`` USED TO BE PRINTED HERE AND THE CENSUS NEVER HAD IT.
        # Removing it from ``_summarise`` and leaving it in this line is the
        # HALF-APPLIED FIX this repository has now recorded twice -- the fix
        # landed in the producer and not in the consumer, and the consumer is
        # where it was read. It raised rather than printing a wrong number,
        # which is the only reason it was cheap.
        print(f"\n  {label}: pressed {result['pressed']}; controls "
              f"{delta['controls_read']:+d}, links {delta['links']:+d}, "
              f"buttons {delta['buttons']:+d}, menus {delta['menus']:+d}, "
              f"menu_items {delta['menu_items']:+d}, dialogs "
              f"{delta['dialogs']:+d}")
        if delta["controls_read"] <= 0 and delta["links"] <= 0:
            print("    NOTHING AROSE. A press that moves no count is evidence "
                  "the disclosure held no unrendered content -- or that this "
                  "reader cannot see what arrived. The menu counts separate "
                  "those two and are printed above.")
        else:
            print(f"    CONTENT AROSE THAT AN UNPRESSED CENSUS CANNOT SEE. "
                  f"{len(result['appeared'])} shaped names appeared that were "
                  "not in the document before.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
