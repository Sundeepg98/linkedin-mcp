"""What is INSIDE a group row's overflow menu? Open all of them. Press nothing.

THE MEASUREMENT THE PRECONDITION AUDIT NAMED AND DID NOT TAKE.
``_audit/2026-09-05-groups-events-precondition.md`` section 7 says it in one
line: *"WHAT WOULD SETTLE IT ABSOLUTELY: the label text inside one of those
overflow menus, which needs a PRESS. Not taken."* This is that press.

It answers three things one page load cannot otherwise reach:

1. **IS ``Groups listing`` LINKEDIN'S WORD FOR MEMBERSHIP?** That reading is
   the one thing in the precondition audit filed as READ rather than MEASURED.
   A menu offering to LEAVE something is a structural answer to it that does
   not depend on reading LinkedIn's copy.
2. **WHICH WRITES EXIST ON AN ADDRESS THIS SERVER MAY ALREADY OPEN.**
   ``GROUPS-SURFACE`` carries twenty write rows and every one of them was
   costed off a page nobody had opened. A menu is an enumeration of the
   affordances LinkedIn actually draws there.
3. **A THIRD INDEPENDENT COUNT OF HIS MEMBERSHIPS.** The heading said five and
   the per-row control said five. This qualifies the controls STRUCTURALLY --
   by what contains them, not by their labels and not by their section -- so
   a third five is a third instrument agreeing rather than the same one twice.

## THE COST OBLIGATION, AND IT IS NOT OPTIONAL

``/mynetwork/`` is refused outright because opening it is believed to consume
the pending-invitation badge. **A tool that cannot measure its own cost must
refuse rather than guess**, so both nav badges are read BEFORE the groups load
and again AFTER every press, and the run reports whether either moved. The nav
renders on every signed-in page, so this costs no extra page load -- the same
property ``linkedin_connections`` relies on.

A badge that moves is not automatically this probe's doing. It is reported as
a MOVEMENT with both readings, and the interpretation is left to a reader who
knows what else was live.

## HOW A CONTROL IS CHOSEN, AND WHY NOT BY ITS NAME

The per-row control's measured labels are ``More`` five times over and
``More options for <redacted>`` once, so **a name-based rule would aim at four
rows out of five or at a string carrying a group's name.** Neither is a rule.

The rule here is structural and it is about WHERE A SEARCH STOPS, not how far
it goes -- the distinction this project paid for once already, when a walk
capped at eight hops attributed a stranger's identifier after two:

    From each button declaring aria-expanded, walk up. At each ancestor count
    the group anchors inside it. The FIRST ancestor holding at least one is
    the candidate row, and the control qualifies only if that count is
    EXACTLY ONE. An ancestor reached holding more than one before any holding
    exactly one disqualifies the control -- that button belongs to the list,
    not to a row.

No budget, no depth limit, and no label. A button that is not row-scoped
cannot qualify by walking further.

## WHY ALL FIVE MENUS RATHER THAN ONE

Because the count rule is the only thing that separates a menu verb from a
group's name, and **one menu has no tally.** Opened across five rows, a verb
LinkedIn draws on every row appears five times and survives
``census_redact_rare``; a label carrying one group's own name appears once and
is redacted by the same rule with no special case. That is
``census_aggregate``'s premise -- furniture repeats and a name does not --
applied at the only window where it is available.

Pressing one menu would have produced a payload in which every capitalised
label is redacted, which is the degenerate answer this wave was warned about
in its own surface.

## WHAT IT WILL NOT DO

* It presses NOTHING inside a menu. Not leave, not report, not settings.
* It closes each menu with Escape and CHECKS that the control collapsed,
  because "the menu did not open" and "the menu opened and was not seen" are
  different findings and a probe that cannot tell them apart has measured
  neither.
* It asserts the address did not change across the whole press sequence. If it
  did, every count after that point is void and the run says so.
* It never opens a menu on a row it could not qualify structurally.

## NO URL IS PRINTED, AND NOT VIA A SANITISER

``_relation`` exists in two sibling probes and is admitted to
``tests/test_navigation_is_never_derived.py::_SANITISERS`` on a proof. This
file needs neither: every navigation fact it reports is a BOOLEAN off a
comparison, and a comparison yields a boolean whatever it compared -- which is
the one exit the taint engine grants by construction rather than by promise.
That is a smaller claim than a sanitiser and it needs no entry anywhere.

## ATTACH MODE ONLY

Chrome runs externally on the operator's real profile and this script REFUSES
without ``LINKEDIN_CDP_ATTACH=1``. A launch-mode session opens a second Chrome
on that profile; the profile is stamped 152 against playwright's 151, so a
launch is a DOWNGRADE and it cost the signed-in session once already.

Usage::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        venv/Scripts/python.exe scripts/_probe_groups_menu.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config, dom, readonly, shape, writes  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL  # noqa: E402

#: The gitignored capture directory. ``.gitignore:140`` matches
#: ``*_probe-*.html``.
OUT = ROOT / "_audit"

GROUPS_URL = f"{BASE_URL}/groups/"

#: The control, and it is the SAME one the two sibling groups probes used, on
#: purpose: 20 controls across six readings on two days. A shared control is
#: what makes today's run comparable to theirs.
CONTROL_URL = f"{BASE_URL}/mypreferences/d/dark-mode"
CONTROL_EXPECTED = 20

#: The selector the press is aimed with. A REPO LITERAL. Only an integer
#: crosses back from the page, and the integer is an index into exactly this
#: list -- so the string that reaches ``page.click`` is authored here and the
#: page contributes a position and nothing else.
DISCLOSURE_SELECTOR = "button[aria-expanded]"

#: A ceiling on presses, stated rather than implied. Five rows were measured;
#: eight leaves room for the answer to have changed without letting a runaway
#: page turn this into an interaction session.
MAX_PRESSES = 8

#: THE ROW QUALIFIER. Returns COUNTS and INDICES. No label, no href and no
#: fragment of either ever crosses back.
#:
#: ``groupAnchors`` counts anchors whose href PATH contains the group marker.
#: The path, not the whole href -- a query string can carry an identifier that
#: has nothing to do with where the anchor points, which is the same reason
#: ``shape.membership_row`` publishes a literal instead of a shaped href.
AIM_JS = """
(cfg) => {
  const groupAnchors = (root) => {
    const out = [];
    for (const a of Array.from(root.querySelectorAll('a[href]'))) {
      let path = '';
      try { path = new URL(a.href, document.baseURI).pathname; }
      catch (e) { path = ''; }
      if (path.indexOf(cfg.marker) !== -1) out.push(a);
    }
    return out;
  };

  const buttons = Array.from(document.querySelectorAll(cfg.selector));
  const qualified = [];
  const disqualified = { list_scoped: 0, no_group_ancestor: 0 };
  // HOW WIDE THE STOPPING ANCESTOR WAS, tallied. A button stopped at a
  // container holding two anchors and one stopped at the whole ten-anchor
  // list are different findings, and "list_scoped" alone flattens them into
  // one word. Counts only -- a width is an integer and names nobody.
  const widths = {};

  buttons.forEach((button, index) => {
    let node = button.parentElement;
    let verdict = 'no_group_ancestor';
    let width = 0;
    while (node) {
      const found = groupAnchors(node).length;
      if (found === 1) { verdict = 'row'; width = 1; break; }
      if (found > 1) { verdict = 'list_scoped'; width = found; break; }
      node = node.parentElement;
    }
    if (verdict === 'row') qualified.push(index);
    else {
      disqualified[verdict] += 1;
      widths[String(width)] = (widths[String(width)] || 0) + 1;
    }
  });

  return {
    buttons: buttons.length,
    qualified: qualified,
    disqualified_list_scoped: disqualified.list_scoped,
    disqualified_no_group_ancestor: disqualified.no_group_ancestor,
    disqualified_stopping_widths: widths,
    group_anchors_in_document: groupAnchors(document).length,
  };
}
"""

#: THE MENU, WHICH A SURFACE CENSUS CANNOT SEE. ``CENSUS_CONTROL_SELECTOR``
#: carries no menu role at all, so an overflow menu drawn the ordinary way as
#: ``[role=menuitem]`` inside ``[role=menu]`` is invisible to a census delta.
#: Lifted in shape from ``scripts/_probe_comment_overflow_menu.py``, which
#: found that out the expensive way -- it read a delta alone and would have
#: reported "no delete exists" on evidence that could not have shown one.
#:
#: RAW LABELS CROSS AND ARE SHAPED IN PYTHON, at the tally, because the tally
#: is the only place the count rule can run.
MENU_JS = """
(cfg) => {
  const sel = '[role="menu"], [role="menuitem"], [role="menuitemcheckbox"], '
            + '[role="menuitemradio"]';
  const nodes = Array.from(document.querySelectorAll(sel));
  const items = nodes.filter(
    (n) => (n.getAttribute('role') || '') !== 'menu'
  );
  const expanded = Array.from(
    document.querySelectorAll(cfg.selector)
  ).filter(
    (n) => (n.getAttribute('aria-expanded') || '') === 'true'
  ).length;
  return {
    menus: nodes.length - items.length,
    items: items.length,
    expanded_controls: expanded,
    labels: items.map(
      (n) => (n.getAttribute('aria-label') || n.textContent || '').trim()
    ),
    dialogs: document.querySelectorAll('[role="dialog"], dialog').length,
  };
}
"""


async def _read_badge(page) -> str:
    """The pending-invitation badge as ONE SHORT STRING, through the shipper.

    ONE BADGE, NOT TWO, and the choice is measured rather than tidy.
    ``shape.messaging_badge`` takes an HTML STRING and answers a different
    question -- messages arrived since he last opened messaging -- through a
    pipeline this probe does not run. Reading it here would mean building a
    second path to a second answer nobody asked for. The pending-invitation
    badge is the one this repository already gates a page load on, and it is
    the one the obligation names.

    ``state != "read"`` is reported as ``unreadable`` rather than as a number,
    because a badge whose value is unknown cannot answer "did this page
    consume one" in EITHER direction -- which is the whole reason the reading
    is taken twice.

    **AND AN UNREADABLE BADGE REPORTS WHAT IT DID SEE.** The first run of this
    probe printed the bare word ``unreadable`` and that is half a measurement
    -- this repository has lost three rounds to a refusal that reported only
    what it did NOT match. A nav that never drew a mynetwork link
    (``mynetwork_links: 0``) and a nav that drew three of which none carried a
    count want completely different repairs, and ``shape.invitation_badge``
    already separates them. Printing only the verdict threw that away.
    """
    verdict = shape.invitation_badge(await dom.read_invitation_badge(page))
    saw = dict(verdict.get("saw") or {})
    seen = (
        f"[mynetwork links {saw.get('mynetwork_links')}, carrying a count "
        f"{saw.get('links_carrying_a_count')}]"
    )
    # THE COUNTS ARE PRINTED ON BOTH BRANCHES, not only the failing one. Run 3
    # printed them only when the badge was unreadable, and the comparison that
    # matters is between the two PAGES: a page drawing a count element and a
    # page drawing none are different navs, and that cannot be seen from one
    # side of the pair. A diagnostic available only on failure cannot support
    # a diagnosis that needs both readings.
    if verdict.get("state") != "read":
        return f"unreadable {seen}"
    return f"{verdict.get('pending')} {seen}"


async def _census_controls(page) -> int:
    census = await dom.read_surface_census(page)
    return int(census.get("controls_read") or 0)


def _names(census: dict) -> dict[str, int]:
    """Shaped control name -> how many controls wear it.

    ``controls``, NOT ``control_shapes``. The second key is what the MCP TOOL
    emits after its own aggregation pass and is empty here; a sibling probe
    read it and got an empty dict from both censuses, then reported "nothing
    arrived" -- a finding about the function wearing a finding about the page.

    AN UNNAMED CONTROL IS COUNTED rather than dropped, because a menu item
    that shaped to the empty string would vanish into exactly that false zero.
    """
    counts: dict[str, int] = {}
    for row in (census.get("controls") or []):
        name = str(row.get("shape") or "") or "<unnamed>"
        counts[name] = counts.get(name, 0) + 1
    return counts


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print("    Chrome runs externally on the operator's own profile and "
              "this script attaches to it. A launch-mode session would open a "
              "SECOND Chrome on that profile and DOWNGRADE it.")
        print(f"    Re-run with LINKEDIN_CDP_ATTACH=1 "
              f"LINKEDIN_CDP_PORT={config.CDP_PORT}")
        return 2

    print("=== WHAT IS INSIDE A GROUP ROW'S OVERFLOW MENU?")
    print(f"    attach mode, port {config.CDP_PORT}.")
    print("    presses NOTHING inside any menu. Emits counts and SHAPES.")

    if not readonly.is_read_url(GROUPS_URL):
        print("\nREFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    label_tally: dict[str, int] = {}
    arrived_tally: dict[str, int] = {}
    per_menu: list[dict] = []

    try:
        async with BROWSER.session() as page:
            print("\n=== 1. CONTROL AND COST, BEFORE")
            await BROWSER.goto(page, CONTROL_URL)
            control_before = await _census_controls(page)
            print(f"    control census: {control_before} controls, expected "
                  f"about {CONTROL_EXPECTED}")
            # THE BADGE IS READ ON THE FEED, NOT ON THE CONTROL PAGE, and the
            # reason is structural: a settings page draws a settings nav and
            # is not known to carry the mynetwork link the badge hangs off.
            # ``linkedin_connections`` spends a navigation on the feed for
            # exactly this reading; this probe pays the same price rather than
            # assuming a page it never measured carries the instrument.
            await BROWSER.goto(page, FEED_URL)
            inv_before = await _read_badge(page)
            print(f"    invitation badge, read on the feed: {inv_before}")

            print("\n=== 2. THE GROUPS ROOT")
            landed = await BROWSER.goto(page, GROUPS_URL)
            # A COMPARISON, so the boolean carries nothing of either url. This
            # is the exit the taint engine grants by construction; no
            # sanitiser is claimed and none is needed.
            served = str(landed).rstrip("/") == GROUPS_URL.rstrip("/")
            walled = "/login" in str(landed) or "/checkpoint" in str(landed)
            print(f"    served the address asked for: {served}")
            if walled:
                print("    AUTH WALL. Nothing else measured.")
                return 1
            groups_controls = await _census_controls(page)
            print(f"    census: {groups_controls} controls")

            print("\n=== 3. QUALIFYING THE ROW CONTROLS, STRUCTURALLY")
            aim = await page.evaluate(
                AIM_JS,
                {"selector": DISCLOSURE_SELECTOR, "marker": "/groups/"},
            )
            qualified = [int(i) for i in (aim.get("qualified") or [])]
            print(f"    buttons declaring aria-expanded: {aim.get('buttons')}")
            print(f"    group anchors in the document:   "
                  f"{aim.get('group_anchors_in_document')}")
            print(f"    QUALIFIED as row-scoped:         {len(qualified)}")
            print(f"    disqualified, list-scoped:       "
                  f"{aim.get('disqualified_list_scoped')}")
            print(f"    disqualified, no group ancestor: "
                  f"{aim.get('disqualified_no_group_ancestor')}")
            print(f"    stopping ancestor widths, disqualified only: "
                  f"{dict(aim.get('disqualified_stopping_widths') or {})}")

            if not qualified:
                print("\n    ZERO QUALIFIED. That is a finding about this "
                      "rule or about the page, and it is NOT a finding that "
                      "he belongs to no group -- two earlier instruments "
                      "measured five. Nothing was pressed.")
                return 1

            # THE ADDRESS AS IT STANDS BEFORE ANY PRESS. Never printed, never
            # navigated to; used only in comparisons, which yield booleans.
            before_url = page.url

            # THE BASELINE FOR THE DELTA. Taken once, before any press.
            baseline = _names(await dom.read_surface_census(page))
            print(f"\n    baseline: {len(baseline)} distinct shaped control "
                  "names before any press")

            print(f"\n=== 4. OPENING {min(len(qualified), MAX_PRESSES)} MENUS, "
                  "ONE AT A TIME")
            for order, index in enumerate(qualified[:MAX_PRESSES], start=1):
                selector = f"{DISCLOSURE_SELECTOR} >> nth={index}"
                await page.click(selector, timeout=writes.CLICK_TIMEOUT_MS)
                await page.wait_for_timeout(900)
                reading = await page.evaluate(
                    MENU_JS, {"selector": DISCLOSURE_SELECTOR}
                )
                labels = [str(text) for text in (reading.get("labels") or [])]
                for text in labels:
                    label_tally[text] = label_tally.get(text, 0) + 1
                # THE SECOND READER, AND THE FIRST RUN PROVED IT IS NOT
                # OPTIONAL. Run 1 read menu ROLES alone: every control went to
                # aria-expanded=true and ZERO menus, items or dialogs
                # appeared. So this surface draws its overflow content without
                # a single menu role, and a role-only reader is blind to it.
                #
                # THE SIBLING PROBE LEARNED THE EXACT OPPOSITE on the comment
                # surface -- there the census delta was blind and the roles
                # were visible. Two surfaces, two readers, opposite blind
                # spots. WHICH READER IS BLIND IS A PROPERTY OF THE SURFACE,
                # not of the reader, so neither one alone can be trusted to
                # report an empty menu.
                arrived = {
                    name: count
                    for name, count in _names(
                        await dom.read_surface_census(page)
                    ).items()
                    if name not in baseline
                }
                # A SEPARATE TALLY, AND THE FIRST RUN PROVED WHY. These names
                # have ALREADY been through ``census_shape`` inside
                # ``read_surface_census``. Run 2 dropped them into the raw
                # tally, where the report shaped them a SECOND time -- and
                # since the key carried a bracketed prefix, the second pass
                # opaqued every one of them. Three distinct arrivals printed
                # as three identical ``<opaque>`` strings.
                #
                # **A DOUBLE-SHAPED STRING IS INDISTINGUISHABLE FROM A
                # REDACTED ONE**, so a reader could not tell "LinkedIn's label
                # is unshapeable" from "this probe shaped it twice". Only the
                # count rule is applied to these, at the report, with their
                # real tally.
                for name, count in arrived.items():
                    arrived_tally[name] = arrived_tally.get(name, 0) + count
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(400)
                closed = await page.evaluate(
                    MENU_JS, {"selector": DISCLOSURE_SELECTOR}
                )
                moved = str(page.url) != str(before_url)
                per_menu.append(
                    {
                        "order": order,
                        "menus": int(reading.get("menus") or 0),
                        "items": int(reading.get("items") or 0),
                        "expanded": int(reading.get("expanded_controls") or 0),
                        "dialogs": int(reading.get("dialogs") or 0),
                        "labels": len(labels),
                        "arrived": len(arrived),
                        "expanded_after_escape": int(
                            closed.get("expanded_controls") or 0
                        ),
                        "navigated": bool(moved),
                    }
                )
                print(f"    menu {order}: menus={reading.get('menus')} "
                      f"items={reading.get('items')} "
                      f"arrived_controls={len(arrived)} "
                      f"expanded={reading.get('expanded_controls')} "
                      f"dialogs={reading.get('dialogs')} "
                      f"-> after Escape expanded="
                      f"{closed.get('expanded_controls')} "
                      f"navigated={moved}")

            print("\n=== 5. COST AND CONTROL, AFTER")
            # ON THE GROUPS PAGE ITSELF. The nav renders on every signed-in
            # page, so the AFTER reading costs no navigation -- the same
            # property linkedin_connections relies on.
            inv_after = await _read_badge(page)
            print(f"    invitation badge: {inv_before} -> {inv_after}    "
                  f"{'UNMOVED' if inv_after == inv_before else 'MOVED'}")

            html = await page.content()
            target = OUT / "_probe-groups-menu-hyd.html"
            target.write_text(html, encoding="utf-8")
            print(f"    captured {len(html)} chars -> {target.name} "
                  "(gitignored, not read back here)")

            await BROWSER.goto(page, CONTROL_URL)
            control_after = await _census_controls(page)
            print(f"    control census at the END: {control_after}")
    except Exception as error:  # noqa: BLE001
        print(f"\nRUN ABORTED: {type(error).__name__}: {error}")
        return 1

    print("\n=== 6. THE MENU, SHAPED AND COUNT-REDACTED")
    print("    Every label passes census_shape AND census_redact_rare with "
          "its REAL tally across the menus opened. A verb LinkedIn draws on "
          "every row survives; a label carrying one group's name is a "
          "singleton and is redacted by the same rule, with no special case.")
    print("    A. MENU-ROLE LABELS, raw from the page, shaped here:")
    if not label_tally:
        print("        NONE. This surface draws no [role=menu] content.")
    for text, count in sorted(
        label_tally.items(), key=lambda item: (-item[1], item[0])
    ):
        safe = shape.census_redact_rare(shape.census_shape(text), count)
        print(f"        {count:>3}  {safe!r}")
    print("    B. ARRIVED CONTROLS, already shaped by the census; only the "
          "count rule is applied here:")
    if not arrived_tally:
        print("        NONE.")
    for text, count in sorted(
        arrived_tally.items(), key=lambda item: (-item[1], item[0])
    ):
        print(f"        {count:>3}  "
              f"{shape.census_redact_rare(text, count)!r}")

    print("\n=== 7. VERDICT")
    floor = int(CONTROL_EXPECTED * 0.5)
    control_ok = control_before >= floor and control_after >= floor
    print(f"    control {control_before} -> {control_after}, floor {floor} -- "
          f"{'PASS at both ends' if control_ok else 'FAIL'}")
    if not control_ok:
        print("    FAILED, so nothing above is a reading about his account.")
        return 1
    navigated = any(row["navigated"] for row in per_menu)
    stuck = [row for row in per_menu if row["expanded_after_escape"] > 0]
    drew = [
        row for row in per_menu if row["items"] > 0 or row["arrived"] > 0
    ]
    opened = [row for row in per_menu if row["expanded"] > 0]
    print(f"    controls that reported themselves EXPANDED: {len(opened)} "
          f"of {len(per_menu)}")
    print(f"    menus opened: {len(per_menu)}, of which {len(drew)} drew "
          "content EITHER reader could see")
    print(f"    any navigation during the presses: {navigated}")
    print(f"    menus still expanded after Escape:  {len(stuck)}")
    if navigated:
        print("    THE ADDRESS CHANGED DURING A PRESS. Every count above is "
              "void: a press that navigates was not a menu open.")
        return 1
    if not drew:
        if opened:
            print("    THE CONTROLS OPENED AND NEITHER READER SAW CONTENT. "
                  "aria-expanded went true on every press, so this is NOT "
                  "'the menu did not open' -- it is a blind spot in both "
                  "readers at once, and that is a finding about the surface.")
        else:
            print("    NOTHING OPENED. aria-expanded never went true, so the "
                  "press did not reach a disclosure and the labels above "
                  "would be about some other part of the page.")
        return 1
    print(f"    distinct menu-role labels: {len(label_tally)}, distinct "
          f"arrived controls: {len(arrived_tally)}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
