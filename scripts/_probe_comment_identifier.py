"""Does a COMMENT have an address this server can already name? Read, do not press.

THE KEYSTONE QUESTION. ``COMMENT-IDENTIFIER`` is filed BLOCKED and four write
rows wait behind it. The stated reason is that a comment has no address this
server can name, so nothing about a SPECIFIC comment can be gated: a write
needs a target, and a target needs a name.

That claim has never been measured. It was inferred from the absence of a
comment reader, which is a fact about this package and not about LinkedIn's
DOM. This probe settles it on the cheapest surface available -- ONE OF HIS OWN
ITEMS, at an address this server already opens for ``feed_item_commented``.

## TWO CANDIDATE ROUTES, and they cost very differently

* **ROUTE A -- an attribute already in the document.** If a comment node
  carries its own identifier as a DOM attribute, then a comment is addressable
  with a PARSER on a page already loaded: no new address, no new capture, no
  press, no clipboard. That is the cheapest possible outcome and it would
  re-cost the row from BLOCKED to a parser.
* **ROUTE B -- ``Copy link to comment``.** Measured in a comment's own overflow
  menu on 2026-09-04 and quoted in ``writes.py`` beside ``Edit`` and
  ``Delete``. It is an affordance, not a reader: it targets the CLIPBOARD,
  which is a permission-gated surface this package has never touched, and it
  costs a press per comment. Route B proves an address EXISTS; only route A
  makes it READABLE here.

Route A is therefore asked FIRST and route B is asked as corroboration, since
two instruments that do not share a defect disagreeing is the cheapest signal
available -- and two that DO share one agreeing is worth nothing.

## THE CONTROL, and why this probe would be worthless without it

A reader that finds nothing reports the same empty output whether the thing is
absent or the reader is blind. This repository has shipped that mistake: a
census aimed at a menu role that did not exist certified nothing while looking
green, and a tabbed surface read zero because nobody pressed the tab.

So the identifier reader runs FIRST on a page where comments are KNOWN ABSENT
-- his own profile, which draws no comment nodes -- and a non-zero reading
there means the reader is matching something other than a comment and its
answer on the item page cannot be trusted. **The control must read zero and the
item must read non-zero, or this probe has measured its own instrument.**

## WHAT CROSSES BACK, and why the masking is done in the page

A comment identifier is a REAL IDENTIFIER. Depending on its shape it can carry
the activity it hangs from and the member who wrote it, and the item is full of
other people's comments. So nothing is masked in python: the skeleton is built
INSIDE the document and only the skeleton is returned, exactly as
``dom.INVITE_NEEDLE_JS`` keeps its comparison in the page.

What leaves the page is: counts, distinct counts, attribute NAMES (which are
LinkedIn's schema and carry nobody), a boolean for whether a value carries the
literal marker ``urn:li:comment`` (a schema constant), and a SKELETON in which
every alphanumeric run is replaced by its class and LENGTH. No identifier, no
fragment of one, and no accessible name.

## Bounds

TWO navigations, both to his own pages. Route A presses NOTHING. Route B
presses ONE overflow control and closes the menu with Escape. The page this
probe opens is closed in a ``finally`` -- the PAGE, never the context, which is
his own signed-in browser session.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.writes import PROFILE_URL  # noqa: E402

#: Composed from the same two constants ``server.ITEM_PERMALINK_URL`` uses,
#: rather than imported from ``server`` -- that module is being edited by other
#: waves tonight and a probe that cannot run because a neighbour is mid-save
#: has failed for a reason unrelated to its question.
ITEM_PERMALINK_URL = config.BASE_URL + dom.ACTIVITY_PERMALINK_MARKER + "{urn}/"

#: The schema marker a comment identifier carries. This is LinkedIn's own
#: vocabulary, not anybody's identifier, so it is safe to hold and to print.
COMMENT_URN_MARKER = "urn:li:comment"

#: The measured comment overflow control prefix. Everything AFTER it is a
#: member's name, so the prefix is the whole of what may be anchored on.
COMMENT_OVERFLOW_PREFIX = "View more options for "

#: ROUTE A. Scans every element for any attribute whose value carries the
#: comment marker, and returns ONLY structure.
#:
#: ``skeleton`` replaces each maximal run of digits with ``d<len>`` and each
#: maximal run of letters with ``a<len>``, keeping punctuation. So two comment
#: identifiers of the same family collapse to one skeleton and neither is
#: recoverable from it -- the point is to show the SHAPE of the address a
#: WriteSpec would have to accept, without ever holding one.
IDENT_JS = """
(cfg) => {
  const mask = (v) => v
    .replace(/[0-9]+/g, (m) => 'd' + m.length)
    .replace(/[A-Za-z]+/g, (m) => 'a' + m.length);

  // THE ATTRIBUTE NAME IS ASKED ABOUT BY NAME, never echoed. An attribute
  // name is LinkedIn's schema and carries nobody -- but the guard cannot
  // know that, and the guard is right to refuse a page-chosen string at a
  // print. So the answer is which of OUR OWN constants matched.
  const matchedAttrs = new Set();
  let attrsNotInVocab = 0;
  const values = new Set();
  let nodes = 0;
  let maxDigitRun = 0;
  let carriesParenPair = false;
  let carriesComma = false;
  let segments = 0;

  for (const el of document.querySelectorAll('*')) {
    let hit = false;
    for (const attr of el.attributes) {
      const v = attr.value || '';
      if (v.indexOf(cfg.marker) === -1) continue;
      hit = true;
      const known = cfg.attrVocab.find((w) => attr.name === w);
      if (known) { matchedAttrs.add(known); } else { attrsNotInVocab += 1; }
      values.add(v);
      // STRUCTURE ONLY. Integers and booleans, computed here, so what a
      // WriteSpec would have to accept is describable without holding one.
      for (const run of (v.match(/[0-9]+/g) || [])) {
        if (run.length > maxDigitRun) maxDigitRun = run.length;
      }
      if (v.indexOf('(') !== -1 && v.indexOf(')') !== -1) carriesParenPair = true;
      if (v.indexOf(',') !== -1) carriesComma = true;
      const segs = v.split(':').length;
      if (segs > segments) segments = segs;
      // mask() is retained and exercised so the structural claims above are
      // taken from the same string the skeleton would describe; the skeleton
      // itself never leaves the page.
      mask(v);
    }
    if (hit) nodes += 1;
  }

  // The comment overflow controls, counted only. Their labels carry names.
  const overflow = Array.from(
    document.querySelectorAll('button[aria-label]')
  ).filter((n) =>
    (n.getAttribute('aria-label') || '').startsWith(cfg.commentPrefix)
  ).length;

  return {
    nodes_carrying_identifier: nodes,
    distinct_values: values.size,
    attr_vocab_matched: [...matchedAttrs].sort(),
    attrs_not_in_vocab: attrsNotInVocab,
    max_digit_run: maxDigitRun,
    colon_segments: segments,
    carries_paren_pair: carriesParenPair,
    carries_comma: carriesComma,
    comment_overflow_controls: overflow,
    // A denominator, so "zero identifiers" can be told apart from "zero
    // elements" -- an empty page and an unaddressable one look identical
    // without it.
    elements_total: document.querySelectorAll('*').length,
  };
}
"""

#: ROUTE B. The menu roles the surface census cannot see. ``CENSUS_CONTROL_SELECTOR``
#: carries no menu role at all, so a menu rendered the ordinary way is invisible
#: to a census delta -- this reads the roles directly and reads ``aria-expanded``
#: on the pressed control, so "the menu did not open" and "the menu opened and
#: was not seen" stop being one answer.
MENU_JS = """
(cfg) => {
  const sel = '[role="menu"], [role="menuitem"], [role="menuitemcheckbox"], '
            + '[role="menuitemradio"]';
  const all = Array.from(document.querySelectorAll(sel));
  const items = all.filter((n) => (n.getAttribute('role') || '') !== 'menu');
  const controls = Array.from(
    document.querySelectorAll('button[aria-label]')
  ).filter((n) =>
    (n.getAttribute('aria-label') || '').startsWith(cfg.commentPrefix)
  );
  const expanded = controls.filter(
    (n) => (n.getAttribute('aria-expanded') || '') === 'true'
  ).length;

  // A menu item's VERB is a control kind and carries nobody. But this menu
  // sits beside people's names, so each label is reduced to whether it
  // matches one of a CLOSED vocabulary asked about by name. Anything not on
  // that list is counted and never spelled.
  const vocab = cfg.vocab;
  const matched = [];
  let unmatched = 0;
  for (const n of items) {
    const raw = ((n.getAttribute('aria-label') || n.textContent) || '')
      .trim().toLowerCase();
    const hit = vocab.find((w) => raw.indexOf(w) !== -1);
    if (hit) { matched.push(hit); } else { unmatched += 1; }
  }

  return {
    menus: all.length - items.length,
    items: items.length,
    expanded_comment_controls: expanded,
    vocab_matched: matched.sort(),
    items_not_in_vocab: unmatched,
    dialogs: document.querySelectorAll('[role="dialog"], dialog').length,
  };
}
"""

#: The CLOSED vocabulary route B is allowed to name. Asked about by name so a
#: label is never echoed: the answer is which of these words the menu carries,
#: never what the menu says. ``copy link`` is the affordance the whole route-B
#: question is about.
MENU_VOCAB = ["copy link", "edit", "delete", "report", "share"]


#: The CLOSED vocabulary of attribute names route A is allowed to name. Asked
#: about by name, so a page-chosen string is never echoed: what prints is one
#: of THESE constants plus a boolean. Anything outside the list is counted.
IDENT_ATTR_VOCAB = (
    "id", "componentkey", "data-id", "data-urn", "data-entity-urn",
    "data-test-id", "href", "data-finite-scroll-hotkey-item",
)


def _cfg() -> dict:
    return {
        "marker": COMMENT_URN_MARKER,
        "commentPrefix": COMMENT_OVERFLOW_PREFIX,
        "vocab": MENU_VOCAB,
        "attrVocab": list(IDENT_ATTR_VOCAB),
    }


def _report(where: str, reading: dict) -> None:
    """Print COUNTS, and BOOLEANS keyed by constants this file owns.

    Nothing LinkedIn chose is printed. The attribute names below come from
    :data:`IDENT_ATTR_VOCAB`, which is written here; only the truth value
    beside each one came from the page.
    """
    print(f"    {where}")
    print(f"      elements on page ............ {reading['elements_total']}")
    print(f"      nodes carrying identifier ... {reading['nodes_carrying_identifier']}")
    print(f"      distinct identifier values .. {reading['distinct_values']}")
    print(f"      comment overflow controls ... {reading['comment_overflow_controls']}")
    matched = reading.get("attr_vocab_matched") or []
    for name in IDENT_ATTR_VOCAB:
        if name in matched:
            print(f"      carried on attribute ........ {name}")
    print(f"      attributes outside vocab .... {reading['attrs_not_in_vocab']}")
    print(f"      longest digit run ........... {reading['max_digit_run']}")
    print(f"      colon-delimited segments .... {reading['colon_segments']}")
    print(f"      parenthesised ............... {reading['carries_paren_pair']}")
    print(f"      comma-separated pair ........ {reading['carries_comma']}")


async def main() -> None:
    print("PROBE: is a COMMENT addressable off a page this server already opens?")
    print(f"  marker asked for: {COMMENT_URN_MARKER!r} (LinkedIn schema, not an id)")
    print("  route A reads attributes and presses NOTHING.")
    print("  every value is masked INSIDE the page; only structure returns.\n")

    async with BROWSER.session() as page:
      try:
        # === CONTROL FIRST. A reader that has not been shown failing is not
        # an instrument, and a zero from a blind reader is indistinguishable
        # from a zero from an empty page.
        print("=== 0. CONTROL -- a page where comment nodes are KNOWN ABSENT")
        await BROWSER.goto(page, PROFILE_URL)
        control = await page.evaluate(IDENT_JS, _cfg())
        _report("his own profile", control)
        control_clean = int(control["nodes_carrying_identifier"]) == 0
        print(f"      CONTROL PASSES (reads zero): {control_clean}")
        if not control_clean:
            print("\n      CONTROL FAILED. The reader matches something that is")
            print("      not a comment, so its reading on the item page would")
            print("      be a fact about the reader. STOPPING -- an instrument")
            print("      that cannot report absence cannot report presence.")
            return
        if int(control["elements_total"]) == 0:
            print("\n      The control page drew ZERO elements, so its zero is")
            print("      about the load and not about the reader. STOPPING.")
            return

        # === THE RAIL. Same resolver the census's feed_item surfaces use.
        rail = await dom.read_own_activity_items(page)
        if rail.get("refused") or not rail.get("items"):
            print(f"\n  REFUSED at the rail: {rail.get('refused')}")
            print(f"  {rail.get('reason')}")
            return
        items = list(rail["items"])
        anchors = dict(rail.get("anchors_per_item") or {})
        order = sorted(items, key=lambda u: (-anchors.get(u, 0), items.index(u)))
        print(f"\n  his items on the rail: {len(items)} (no urn is printed)")

        # === ROUTE A, walking richest-first until something carries comments.
        print("\n=== 1. ROUTE A -- an identifier already in the document")
        found = None
        for position, urn in enumerate(order, start=1):
            await page.wait_for_timeout(2_000)
            await BROWSER.goto(page, ITEM_PERMALINK_URL.format(urn=urn))
            reading = await page.evaluate(IDENT_JS, _cfg())
            _report(f"item {position} of {len(order)} "
                    f"(anchors {anchors.get(urn, 0)})", reading)
            if int(reading["nodes_carrying_identifier"]) > 0:
                found = reading
                break
            if int(reading["comment_overflow_controls"]) > 0 and found is None:
                # A page WITH comments and WITHOUT identifiers is the decisive
                # negative, and it is a different answer from a page with no
                # comments at all. Keep it and keep walking.
                found = reading

        print("\n=== 2. VERDICT ON ROUTE A")
        if found is None:
            print("    NO ITEM ON HIS RAIL DREW A COMMENT AT ALL.")
            print("    That is a missing SUBJECT, not an absent identifier.")
            print("    Route A is UNMEASURED, not refuted.")
        elif int(found["nodes_carrying_identifier"]) > 0:
            print("    A COMMENT CARRIES AN IDENTIFIER IN THE DOCUMENT.")
            print(f"    {found['nodes_carrying_identifier']} node(s), "
                  f"{found['distinct_values']} distinct; the attributes are")
            print("    named above, each one a constant this file owns.")
            print("    A comment is therefore addressable with a PARSER on a")
            print("    page this server already opens. No new address, no")
            print("    press, no clipboard.")
        else:
            print("    COMMENTS RENDER AND CARRY NO IDENTIFIER ATTRIBUTE.")
            print(f"    {found['comment_overflow_controls']} comment overflow")
            print("    control(s) and zero identifier-bearing attributes.")
            print("    Route A is REFUTED on this page and route B is the")
            print("    only remaining address.")

        # === ROUTE B. One press, on one control, to corroborate.
        print("\n=== 3. ROUTE B -- the overflow menu, pressed once")
        if found is None or int(found["comment_overflow_controls"]) < 1:
            print("    NOT ATTEMPTED: no comment overflow control on the page")
            print("    that was landed on. Nothing was pressed.")
            return

        before = await page.evaluate(MENU_JS, _cfg())
        print(f"    before press: menus={before['menus']} "
              f"items={before['items']} expanded={before['expanded_comment_controls']}")
        control_loc = page.locator(
            f'button[aria-label^="{COMMENT_OVERFLOW_PREFIX}"]'
        ).first
        await control_loc.click()
        await page.wait_for_timeout(1_500)
        after = await page.evaluate(MENU_JS, _cfg())
        print(f"    after press:  menus={after['menus']} "
              f"items={after['items']} expanded={after['expanded_comment_controls']}")
        matched = after.get("vocab_matched") or []
        for word in MENU_VOCAB:
            print(f"    menu carries {word:>10s}: {word in matched}")
        print(f"    items not in the asked vocabulary: {after['items_not_in_vocab']}")
        opened = int(after["items"]) > int(before["items"])
        print(f"    MENU ACTUALLY OPENED (item count grew): {opened}")
        await page.keyboard.press("Escape")
        print("    Escape sent. Nothing inside the menu was pressed.")
      finally:
        # THE PAGE, never the context. The context is his signed-in browser and
        # closing it would end the session every wave is sharing. A page count
        # cannot prove a tab closed -- a dozen waves share this Chrome -- so
        # ``is_closed()`` is read, which is the presence reading.
        try:
            await page.close()
            print(f"\n  page closed: {page.is_closed()}")
        except Exception as exc:  # pragma: no cover - cleanup only
            print(f"\n  page close failed: {type(exc).__name__}")


if __name__ == "__main__":
    asyncio.run(main())
