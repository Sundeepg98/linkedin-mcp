"""Can a comment be DELETED? Open one overflow menu and read it. Press nothing.

THE QUESTION, AND WHY IT IS ASKED BEFORE A COMMENT EXISTS. ``comment_on_item``
is authorised and previews cleanly. Its reversibility class is STILL-UNKNOWN
because nobody has established that LinkedIn offers a delete at all -- and the
usual way to find out is to publish one and go looking, which is buying the
answer with the permanent act it was supposed to inform.

``comment_on_item``'s own preview names the cheap path instead: open the
overflow menu on one of HIS OWN EXISTING comments and read its items. That
settles whether a delete affordance exists without publishing anything.

**ONE MENU OPEN AGAINST A PERMANENT ACT.** That is the trade this file makes.

## The standing doctrine this probe is deliberately the first to test

This repository has always used the unopened overflow menu to REFUSE -- "an
unopened menu is not evidence about what is inside it" appears wherever a
capability was costed off one. Correct, and it cuts both ways: the same
sentence says the menu is the place the evidence actually lives. This is the
first time it is opened as a TASK rather than cited as a limit.

## Aiming, and why it is done inside the page

The comment overflow control's accessible name CARRIES THE COMMENTER'S NAME --
``View more options for <member>'s comment.`` is measured on this surface and
is quoted in ``dom.read_comment_surface``. A comment menu sits beside other
people's names, and this must open HIS OWN comment and no one else's.

So the whole selection happens in the document, exactly as
:data:`dom.INVITE_NEEDLE_JS` does it, and what crosses back is arithmetic:

1. The POST's own overflow control names the page owner --
   :data:`dom.ACTIVITY_OVERFLOW_PREFIX` is ``"Open control menu for post by "``
   and the remainder is the author. Read in the page, never returned.
2. Comment overflow controls are those whose name starts with
   ``"View more options for "``.
3. A comment is HIS if its label carries the owner string from step 1.
4. **EXACTLY ONE MATCH IS THE ONLY AIMABLE ANSWER.** Zero refuses. Two or more
   refuses rather than shortlisting -- the same rule ``aim_invitation`` keeps,
   for the same reason.

Only ``owner_found``, the counts, and an INDEX ever leave the page.

## Reading the menu without reading names

The menu is enumerated with :func:`dom.read_surface_census`, the house
instrument that is the only caller of ``CENSUS_JS`` and the one place a raw
accessible name is discarded. A census is taken BEFORE the click and again
AFTER, and the ARRIVED names -- present after, absent before -- are the menu.
That is the same delta instrument ``comment_on_item`` already uses to identify
its submit control, pointed at a different question.

Every string printed has been through ``shape.census_shape``.

## What it will not do

* It presses NOTHING inside the menu. Not delete, not edit, not report.
* It closes the menu with Escape and asserts nothing about having done so.
* It never opens a menu on a comment it could not prove was his.
* It loads no third party's profile and follows no link.

## Bounds

TWO navigations: his own profile, then one of his own item permalinks. One
click, on one overflow control, whose identity was established in the page.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, dom, shape, writes  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.writes import PROFILE_URL  # noqa: E402

#: The permalink address, COMPOSED HERE FROM THE SAME TWO CONSTANTS
#: ``server.ITEM_PERMALINK_URL`` composes it from, rather than imported from
#: ``server``. Importing that module would pull the whole tool surface in for
#: one string, and it is being edited by another agent tonight -- a probe that
#: cannot run because somebody else's file is mid-save is a probe that fails
#: for a reason having nothing to do with its question.
ITEM_PERMALINK_URL = config.BASE_URL + dom.ACTIVITY_PERMALINK_MARKER + "{urn}/"

#: The measured comment overflow control. Quoted in dom.read_comment_surface
#: as ``View more options for <member>'s comment.`` -- the prefix is the whole
#: of what may be anchored on, because everything after it is somebody's name.
COMMENT_OVERFLOW_PREFIX = "View more options for "

#: Words that would make a menu item a DELETE affordance. Matched
#: case-insensitively against SHAPED names, and reported rather than acted on.
#: A shaped name is a control KIND, so this is a question about the menu's
#: vocabulary and not about anybody on it.
DELETE_WORDS = ("delete", "remove")

AIM_JS = """
(cfg) => {
  const posts = Array.from(
    document.querySelectorAll('button[aria-label], a[aria-label]')
  ).map((n) => n.getAttribute('aria-label') || '');

  // 1. THE OWNER, from the POST's own overflow control. Read here, never
  //    returned -- only whether it was found and what it matched.
  const ownerLabels = posts.filter((v) => v.startsWith(cfg.postPrefix));
  const owners = new Set(
    ownerLabels.map((v) => v.slice(cfg.postPrefix.length).trim())
  );
  const owner = owners.size === 1 ? [...owners][0] : null;

  // 2. THE COMMENT OVERFLOW CONTROLS, as live nodes so an index means
  //    something to a locator using the same selector.
  const nodes = Array.from(
    document.querySelectorAll('button[aria-label]')
  ).filter((n) =>
    (n.getAttribute('aria-label') || '').startsWith(cfg.commentPrefix)
  );

  let matches = 0;
  let index = null;
  let first_index = null;
  if (owner) {
    for (let i = 0; i < nodes.length; i += 1) {
      const label = nodes[i].getAttribute('aria-label') || '';
      if (label.indexOf(owner) !== -1) {
        matches += 1;
        // ``index`` KEEPS THE WRITE RULE: a second match erases the aim
        // rather than keeping the first, which is what aim_invitation does
        // and what any write here must do.
        index = (matches === 1) ? i : null;
        // ``first_index`` IS THE MEASUREMENT RULE, and the two are returned
        // separately so the caller has to say WHICH it is using.
        if (first_index === null) first_index = i;
      }
    }
  }

  return {
    post_overflow_controls: ownerLabels.length,
    owner_found: owner !== null,
    owner_unanimous: owners.size === 1,
    distinct_owner_strings: owners.size,
    comment_overflow_controls: nodes.length,
    matches: matches,
    index: index,
    first_index: first_index,
  };
}
"""


#: THE MENU ITSELF, which the surface census CANNOT SEE.
#: ``dom.CENSUS_CONTROL_SELECTOR`` is ``button, a[href], input, textarea,
#: select, [role=button|link|textbox|combobox], [contenteditable]`` -- and
#: carries no menu role at all. So an overflow menu rendered the ordinary way,
#: as ``[role=menuitem]`` inside ``[role=menu]``, is INVISIBLE to a census
#: delta. The first run of this probe read the delta alone, saw one arrival
#: that was a comment editor, and would have reported "the menu drew and
#: offers no delete" on evidence that could not have shown a menu item if one
#: existed.
#:
#: This reads the menu roles directly, and reads ``aria-expanded`` on the
#: control that was pressed so that "the menu did not open" and "the menu
#: opened and was not seen" stop being the same answer.
MENU_JS = """
(cfg) => {
  const sel = '[role="menu"], [role="menuitem"], [role="menuitemcheckbox"], '
            + '[role="menuitemradio"]';
  const nodes = Array.from(document.querySelectorAll(sel));
  const items = nodes.filter(
    (n) => (n.getAttribute('role') || '') !== 'menu'
  );
  const controls = Array.from(
    document.querySelectorAll('button[aria-label]')
  ).filter((n) =>
    (n.getAttribute('aria-label') || '').startsWith(cfg.commentPrefix)
  );
  const expanded = controls.filter(
    (n) => (n.getAttribute('aria-expanded') || '') === 'true'
  ).length;

  return {
    menus: nodes.length - items.length,
    items: items.length,
    expanded_comment_controls: expanded,
    // RAW LABELS, shaped in python at the boundary the house shaper defines.
    // Menu verbs carry no name, but this is a comment menu and it sits beside
    // people's names, so nothing here is printed unshaped.
    labels: items.map(
      (n) => (n.getAttribute('aria-label') || n.textContent || '').trim()
    ),
    dialogs: document.querySelectorAll('[role="dialog"], dialog').length,
  };
}
"""


def _names(census: dict) -> dict[str, int]:
    """Shaped control name -> how many controls wear it.

    THE KEY IS ``controls``, NOT ``control_shapes``. The first run of this
    probe read ``control_shapes`` -- which is what the MCP TOOL
    ``linkedin_surface_census`` emits after its own aggregation pass -- and got
    an empty dict from BOTH censuses, before and after the click. It reported
    "nothing arrived", which would have read as a finding about the menu and
    was a finding about this function. The zero before the click is what gave
    it away: a page with no controls at all had not been clicked on.

    ``dom.read_surface_census`` returns ONE RECORD PER CONTROL under
    ``controls``, each already carrying a shaped ``shape`` and no count, so the
    counting happens here.

    AN UNNAMED CONTROL IS COUNTED, not dropped. ``census_shape`` returns "" for
    an empty accessible name, and a menu item that shaped to "" would vanish
    into exactly the false zero described above.
    """
    counts: dict[str, int] = {}
    for row in census.get("controls", []) or []:
        name = str(row.get("shape") or "") or "<unnamed>"
        counts[name] = counts.get(name, 0) + 1
    return counts


async def main() -> None:
    print("PROBE: does a comment overflow menu offer a DELETE?")
    print(f"  comment prefix anchored on: {COMMENT_OVERFLOW_PREFIX!r}")
    print(f"  owner read from:            {dom.ACTIVITY_OVERFLOW_PREFIX!r}")
    print("  presses NOTHING inside the menu. emits counts and SHAPES.\n")

    async with BROWSER.session() as page:
        landed = await BROWSER.goto(page, PROFILE_URL)
        print(f"  profile landed on /in/: {'/in/' in landed}")
        print(f"  self-assertion rode:    {'isSelfProfile=true' in landed}")

        rail = await dom.read_own_activity_items(page)
        if rail.get("refused") or not rail.get("items"):
            print(f"\n  REFUSED at the rail: {rail.get('refused')}")
            print(f"  {rail.get('reason')}")
            await BROWSER.stop()
            return

        items = list(rail["items"])
        anchors = dict(rail.get("anchors_per_item") or {})
        # RICHEST FIRST, by permalink anchors -- a heuristic for the item most
        # likely to carry comments, and the same rule the census's
        # ``feed_item_commented`` surface uses. Ties keep document order.
        #
        # AND THEN THE REST, because the first run of this probe found the
        # richest item carrying FOUR comment menus and NONE of them his. That
        # is a real answer about that item and says nothing about the others,
        # so walking the rail is the difference between "he has not commented
        # here" and "he has not commented at all". Every item is his own, so
        # each load costs a page and nobody else anything.
        order = sorted(
            items, key=lambda urn: (-anchors.get(urn, 0), items.index(urn))
        )
        print(f"  his items: {len(items)}; walking all of them, richest first")
        print("  (no urn is printed -- they are real identifiers)")

        aim = None
        print("\n=== 1. AIMING, decided inside the page, one item at a time")
        print(f"    {'item':>6}  {'anchors':>7}  {'owner':>5}  "
              f"{'comment menus':>13}  {'HIS':>3}")
        for position, urn in enumerate(order, start=1):
            await page.wait_for_timeout(3_000)
            await BROWSER.goto(page, ITEM_PERMALINK_URL.format(urn=urn))
            reading = await page.evaluate(
                AIM_JS,
                {
                    "postPrefix": dom.ACTIVITY_OVERFLOW_PREFIX,
                    "commentPrefix": COMMENT_OVERFLOW_PREFIX,
                },
            )
            print(
                f"    {position:>6}  {anchors.get(urn, 0):>7}  "
                f"{str(bool(reading.get('owner_found'))):>5}  "
                f"{int(reading.get('comment_overflow_controls') or 0):>13}  "
                f"{int(reading.get('matches') or 0):>3}"
            )
            if int(reading.get("matches") or 0) >= 1:
                aim = reading
                break

        if aim is None:
            print("\n    NO ITEM ON HIS RAIL CARRIES A COMMENT OF HIS OWN.")
            print("    Every one was checked and every one returned zero")
            print("    matches. Nothing was clicked on any of them.")
            print("    THIS IS NOT 'no delete exists' -- it is a missing")
            print("    SUBJECT. The menu that would answer the question is on")
            print("    a comment, and there is no comment of his to open one")
            print("    on. His comments, if any, are on OTHER members' items,")
            print("    which this rail does not return and no reader here can")
            print("    reach.")
            await BROWSER.stop()
            return

        print("\n    aim settled on the item above:")
        for key in (
            "post_overflow_controls",
            "owner_found",
            "owner_unanimous",
            "distinct_owner_strings",
            "comment_overflow_controls",
            "matches",
            "index",
        ):
            print(f"    {key:28s} {aim.get(key)}")

        if not aim.get("owner_found"):
            print("\n    STOPPING. The page owner could not be established")
            print("    from the post overflow control, so no comment can be")
            print("    proved to be his. Nothing was clicked.")
            await BROWSER.stop()
            return
        if int(aim.get("comment_overflow_controls") or 0) == 0:
            print("\n    STOPPING. No comment overflow control rendered at")
            print("    all. That is UNKNOWN, not 'comments cannot be")
            print("    deleted' -- the comment section may not have drawn.")
            await BROWSER.stop()
            return
        if int(aim.get("matches") or 0) < 1 or aim.get("first_index") is None:
            print(f"\n    STOPPING. {aim.get('matches')} comment(s) matched the")
            print("    page owner, so there is nothing of his to open a menu")
            print("    on here. Nothing was clicked.")
            await BROWSER.stop()
            return

        # THE FIRST OF HIS OWN, IN DOCUMENT ORDER, AND THE ANSWER SAYS SO.
        #
        # A WRITE MAY NOT DO THIS and this file is not a write. The rule is
        # already drawn in this repository, at ``_resolve_own_item_permalink``,
        # in these words: "THE FIRST ITEM IN DOCUMENT ORDER, and the answer
        # says so. For a WRITE that would be choosing by position and is
        # refused everywhere in this package; for a MEASUREMENT OF THE SURFACE
        # it is fine, because the question is what a permalink page draws and
        # any of his items answers it."
        #
        # The identical argument holds one level down. The question here is
        # what LinkedIn puts in the overflow menu of a comment THE VIEWER
        # WROTE, and any comment he wrote answers it. Both candidates cleared
        # the owner match inside the page, so position selects between two
        # comments of his own and can reach nobody else -- which is the
        # property that made the strict rule necessary in the first place.
        #
        # ``aim["index"]`` still carries the WRITE answer and is None here.
        # The two are kept apart so that using the looser one is a visible
        # decision rather than a silently relaxed gate.
        index = int(aim["first_index"])
        if int(aim.get("matches") or 0) > 1:
            print(f"\n    {aim.get('matches')} of his own comments are on this "
                  "item. Opening the FIRST in document order.")
            print("    A write would REFUSE here -- aim['index'] is None, as "
                  "it should be.")
            print("    This is a measurement, both candidates are his, and "
                  "position cannot reach a third party.")
        selector = (
            'button[aria-label^="' + COMMENT_OVERFLOW_PREFIX + '"]'
            " >> nth=" + str(index)
        )

        print("\n=== 2. CENSUS BEFORE THE CLICK")
        before = _names(await dom.read_surface_census(page))
        print(f"    distinct shaped control names: {len(before)}")

        print("\n=== 3. OPENING THE MENU. One click, on his own comment.")
        await page.click(selector, timeout=writes.CLICK_TIMEOUT_MS)
        await page.wait_for_timeout(1_500)
        print("    clicked. NOTHING inside the menu will be pressed.")

        print("\n=== 4. CENSUS AFTER -- the ARRIVED names are the menu")
        after = _names(await dom.read_surface_census(page))
        arrived = {n: c for n, c in after.items() if n not in before}
        grew = {
            n: (before[n], after[n])
            for n in after
            if n in before and after[n] > before[n]
        }

        print(f"    distinct shaped control names: {len(after)}")
        print(f"    ARRIVED (absent before, present after): {len(arrived)}")
        for name in sorted(arrived):
            print(f"      {arrived[name]:>3d}  {name!r}")
        if grew:
            print(f"    GREW (already present, count rose): {len(grew)}")
            for name in sorted(grew):
                was, now = grew[name]
                print(f"      {was} -> {now}  {name!r}")

        print("\n=== 4b. THE MENU ITSELF, read by role")
        menu = await page.evaluate(
            MENU_JS, {"commentPrefix": COMMENT_OVERFLOW_PREFIX}
        )
        for key in ("menus", "items", "expanded_comment_controls", "dialogs"):
            print(f"    {key:28s} {menu.get(key)}")

        menu_labels = [
            shape.census_shape(str(text or "").strip())
            for text in (menu.get("labels") or [])
        ]
        menu_labels = [text for text in menu_labels if text]
        print(f"    menu item labels ({len(menu_labels)}, shaped):")
        for text in menu_labels:
            print(f"      {text!r}")

        deletes = [
            text for text in menu_labels
            if any(word in text.lower() for word in DELETE_WORDS)
        ]

        print("\n=== 5. CLOSING THE MENU")
        await page.keyboard.press("Escape")
        print("    Escape pressed. Nothing in the menu was activated.")

        items = int(menu.get("items") or 0)
        expanded = int(menu.get("expanded_comment_controls") or 0)

        print("\n=== THE ANSWER")
        print(f"    menu items read by role:  {items}")
        print(f"    controls reading expanded: {expanded}")
        print(f"    delete-shaped items:      {len(deletes)}")
        for text in deletes:
            print(f"      {text!r}")

        if items == 0 and expanded == 0:
            print("    THE MENU DID NOT OPEN. No menu role rendered and no")
            print("    comment control reports aria-expanded=true, so the")
            print("    click did not do what this probe assumed. That is a")
            print("    fact about the CLICK and says NOTHING about whether a")
            print("    delete exists. Do not record a reversibility class off")
            print("    this run.")
        elif items == 0:
            print("    A CONTROL EXPANDED AND NO MENU ITEM RENDERED. The menu")
            print("    is drawn with markup this probe does not recognise --")
            print("    still UNKNOWN, and still not evidence of absence.")
        elif deletes:
            print("    A DELETE AFFORDANCE EXISTS on his own comment. That")
            print("    settles the reversibility class the spec calls")
            print("    STILL-UNKNOWN -- by reading, not by publishing.")
        else:
            print("    THE MENU OPENED AND CARRIES NO DELETE-SHAPED ITEM.")
            print("    The labels above are its whole vocabulary. That is the")
            print("    stronger finding, and it is what would make publishing")
            print("    a comment an act with no route back through this menu.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    asyncio.run(main())
