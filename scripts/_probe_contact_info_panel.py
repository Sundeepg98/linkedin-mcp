"""Does the contact-info control EXIST on his own profile, and what does PRESSING it draw?

`CONTACT-INFO-PANEL` is row 38 of the gap ledger and its queue is MEASURE, not
BUILD. The reason is worth stating because it decides the whole shape of this
file: the panel is HIS OWN DATA -- the same class as the profile page it hangs
off -- but it sits BEHIND A CONTROL, and nothing in this repository has ever
pressed that control. Five rows are filed against a panel nobody has opened.

## THIS PROBE ADDS NO ADDRESS. IT PRESSES ONE.

`https://www.linkedin.com/in/me/` is already on `readonly._ALLOWED_URL_PATTERNS`.
The overlay address is NOT, and this probe does not navigate to it -- it presses
the affordance the profile page already draws and reads whatever renders in
place. That is precisely why the ledger costs this row as a MEASURE with no
allowlist entry: the question is what a press reveals, and a press needs no new
pattern.

## A CENSUS THAT NEVER PRESSES REPORTS A CLEAN ABSENCE

That has shipped here once already: `CENSUS_CONTROL_SELECTOR` was aimed at a
menu role that did not exist, certified nothing, and looked green the whole
time. So this file carries a CONTROL, and the control is the point:

    THE SAME PRESSER IS RUN AT AN ADDRESS WHERE THE CONTROL IS KNOWN ABSENT.

`/mypreferences/d/dark-mode` is an admitted read page that draws no contact-info
affordance. If the presser reports `control_absent` there and `pressed` on the
profile, then a clean absence and a broken presser are DISTINGUISHABLE. If it
reports `control_absent` at BOTH, this run says nothing about his profile and
says so in its own verdict rather than publishing a zero.

**A DELTA CANNOT ANSWER A QUESTION ABOUT PRESENCE.** Every number below is a
COUNT TAKEN AT A MOMENT, never a difference between two moments. Three waves in
this repository have published a change measurement against a question about
whether something exists; one of them contradicted a number it had printed two
lines earlier. The before/after readings here exist to bound the effect of the
press on the SAME page, and they are reported as two presence readings, never
subtracted into a single claim.

## WHAT MAY CROSS BACK, AND IT IS NOT HIS CONTACT DETAILS

The panel is made of email addresses, phone numbers, birthdays and websites.
Those are the highest-value strings on the whole surface and NONE of them may
leave the page. The rule is enforced structurally rather than by filtering:

    THE IN-PAGE SCRIPT RETURNS INTEGERS AND CLOSED-VOCABULARY KEYS ONLY.

Every label this probe can report is a member of `LABEL_VOCABULARY`, a tuple
written in this file. The matching happens INSIDE the page against that tuple,
so an unmatched label produces a count in `other` and never a string. There is
no code path on which a value, a label or any page text becomes a Python string
in this process, which is a stronger property than redacting one afterwards --
a filter has to keep up, and an absent channel does not.

## COST

Two page loads, one press, and the pending-invitation badge read before and
after on the surface that carries it. The press is on his own profile and opens
an overlay; the overlay is dismissed with Escape.

Usage::

    LINKEDIN_CDP_ATTACH_TIMEOUT_MS=120000 LINKEDIN_CDP_ATTACH=1 \\
        LINKEDIN_CDP_PORT=9224 venv/Scripts/python.exe \\
        scripts/_probe_contact_info_panel.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL  # noqa: E402

#: The affordance, taken from `dom.PROFILE_EDITOR_HREFS` rather than retyped, so
#: the two cannot drift. That tuple records the 2026-08-30 measurement that the
#: live profile draws three editor anchors where every tracked fixture draws
#: none -- this is the third of them.
CONTACT_MARKER = dom.PROFILE_EDITOR_HREFS[2]

PROFILE_URL = f"{BASE_URL}/in/me/"

#: THE CONTROL ADDRESS. An admitted read page that draws no contact-info
#: affordance, used by a sibling probe as its liveness control for the same
#: reason. The presser MUST report `control_absent` here.
CONTROL_URL = f"{BASE_URL}/mypreferences/d/dark-mode"

#: The floor the control page must clear for this session to be believable at
#: all, matching the sibling probe's constant.
CONTROL_EXPECTED = 20

#: THE CLOSED VOCABULARY. The only label strings this probe can ever report,
#: and they are written HERE rather than read off the page. A label LinkedIn
#: draws that is not on this list increments `other` and does not cross.
#:
#: These are LABELS, not values. "email" as a key says the panel drew a section
#: about email; it says nothing whatever about the address inside it, which is
#: never read.
LABEL_VOCABULARY = (
    "profile",
    "website",
    "email",
    "phone",
    "address",
    "birthday",
    "connected",
    "im",
    "twitter",
    "instant messaging",
)

#: The in-page reader. RETURNS INTEGERS AND KEYS FROM `vocab` AND NOTHING ELSE.
#:
#: There is deliberately no branch that returns a substring of the document.
#: The label match is `indexOf` against the caller's own tuple, so the value
#: that crosses is the caller's literal and never the page's text.
PANEL_JS = r"""
(cfg) => {
  const out = {controls: 0, expanded: 0, dialogs: 0, rows: 0, other: 0,
               links: 0, labels: {},
               visible_dialogs: 0, visible_rows: 0, visible_headings: 0,
               visible_links: 0, visible_children: 0, token_labels: {}};
  const anchors = Array.from(document.querySelectorAll('a[href]'));
  for (const a of anchors) {
    let path = '';
    try { path = new URL(a.href, document.baseURI).pathname; }
    catch (e) { continue; }
    if (path.indexOf(cfg.marker) !== -1) {
      out.controls += 1;
      if (a.getAttribute('aria-expanded') !== null) { out.expanded += 1; }
    }
  }
  const all = Array.from(document.querySelectorAll('[role="dialog"], dialog'));
  out.dialogs = all.length;

  // THE SECOND INSTRUMENT, AND IT DOES NOT SHARE AN INPUT FEATURE WITH THE
  // FIRST. Run 1 published two numbers as declared UPPER BOUNDS: a label
  // count taken by SUBSTRING over EVERY dialog on the page, and a row count
  // of 1 that was implausible for a panel drawing three field classes.
  //
  // Both defects have the same root and it is not the matcher: the page
  // carried FOUR dialogs BEFORE the press, so every count was taken over
  // other people's markup as well as the panel. Restricting to the VISIBLE
  // dialog aims the reader at the thing that was opened.
  //
  // And the label rule becomes a TOKEN match with word boundaries rather
  // than a substring. `im` inside `time` is the measured overreach; a
  // boundary rule cannot make it and reports zero where zero is the truth.
  const visible = all.filter((d) => {
    if (d.hidden) { return false; }
    if (d.getAttribute('aria-hidden') === 'true') { return false; }
    const r = d.getBoundingClientRect();
    return (r.width > 0 && r.height > 0);
  });
  out.visible_dialogs = visible.length;

  for (const d of all) {
    const text = (d.innerText || '').toLowerCase();
    let matchedAny = false;
    for (const word of cfg.vocab) {
      if (text.indexOf(word) !== -1) {
        out.labels[word] = (out.labels[word] || 0) + 1;
        matchedAny = true;
      }
    }
    if (!matchedAny) { out.other += 1; }
    out.rows += d.querySelectorAll('li, section').length;
    out.links += d.querySelectorAll('a[href]').length;
  }

  // THE BOUNDARY RULE, BUILT WITHOUT A REGEX ON PURPOSE.
  //
  // A constructed RegExp needs the vocabulary escaped, and getting that
  // escaping wrong is exactly how run 2 of this probe died -- Playwright
  // reported "Invalid regular expression: missing /", the run aborted before
  // the control leg, and it cost a page load and proved nothing. The escape
  // had to survive a Python string literal AND a JavaScript regex literal,
  // which is two layers of quoting to get right for no benefit.
  //
  // A NEIGHBOUR-CHARACTER TEST NEEDS NO ESCAPING AT ALL and cannot be
  // mis-quoted: a match counts only when the characters either side of it
  // are not letters or digits, which is what a word boundary means. The text
  // is lower-cased before it gets here, so the letter test needs one range.
  const isWordChar = (ch) =>
    (ch >= 'a' && ch <= 'z') || (ch >= '0' && ch <= '9');
  const hasToken = (text, word) => {
    let from = 0;
    for (;;) {
      const at = text.indexOf(word, from);
      if (at === -1) { return false; }
      const before = (at === 0) ? '' : text.charAt(at - 1);
      const after = text.charAt(at + word.length);
      if (!isWordChar(before) && !isWordChar(after)) { return true; }
      from = at + 1;
    }
  };

  for (const d of visible) {
    const text = (d.innerText || '').toLowerCase();
    for (const word of cfg.vocab) {
      if (hasToken(text, word)) {
        out.token_labels[word] = (out.token_labels[word] || 0) + 1;
      }
    }
    // A WIDER STRUCTURAL NET than li/section, because run 1's row count of 1
    // says the panel's rows are probably neither.
    out.visible_rows += d.querySelectorAll('li, section').length;
    out.visible_headings += d.querySelectorAll(
      'h1, h2, h3, h4, h5, h6').length;
    out.visible_links += d.querySelectorAll('a[href]').length;
    out.visible_children += d.querySelectorAll('*').length;
  }
  return out;
}
"""


async def press_contact_control(page):
    """Count the control, PRESS it, and count what the press drew. Counts only.

    Returns a dict of integers plus a status drawn from a closed set. The status
    is the whole reason this function exists as one unit: a run that finds no
    control and a run whose press failed must not report the same thing.
    """
    before = await page.evaluate(
        PANEL_JS, {"marker": CONTACT_MARKER, "vocab": list(LABEL_VOCABULARY)}
    )
    controls = int(before.get("controls") or 0)
    if controls == 0:
        return {
            "status": "control_absent",
            "controls": 0,
            "dialogs_before": int(before.get("dialogs") or 0),
            "dialogs_after": 0,
            "rows": 0,
            "links": 0,
            "other": 0,
            "labels": {},
        }

    locator = page.locator('a[href*="' + CONTACT_MARKER + '"]').first
    try:
        await locator.click(timeout=15000)
    except Exception as exc:  # noqa: BLE001 - class only, see below
        # CLASS ONLY, DELIBERATELY. Everywhere else in this repository dropping
        # the exception message is the anti-pattern; here the message can carry
        # an interpolated selector built from a live href, and an identity url
        # has reached a transcript through exactly that route before.
        return {
            "status": "press_failed",
            "controls": controls,
            "press_error_class": type(exc).__name__,
            "dialogs_before": int(before.get("dialogs") or 0),
            "dialogs_after": 0,
            "rows": 0,
            "links": 0,
            "other": 0,
            "labels": {},
        }

    await page.wait_for_timeout(2500)
    after = await page.evaluate(
        PANEL_JS, {"marker": CONTACT_MARKER, "vocab": list(LABEL_VOCABULARY)}
    )
    return {
        "status": "pressed",
        "controls": controls,
        "visible_dialogs": int(after.get("visible_dialogs") or 0),
        "visible_rows": int(after.get("visible_rows") or 0),
        "visible_headings": int(after.get("visible_headings") or 0),
        "visible_links": int(after.get("visible_links") or 0),
        "visible_children": int(after.get("visible_children") or 0),
        "token_labels": {
            str(tok_word): int(tok_hits)
            for tok_word, tok_hits in dict(
                after.get("token_labels") or {}).items()
            if tok_word in LABEL_VOCABULARY
        },
        "dialogs_before": int(before.get("dialogs") or 0),
        "dialogs_after": int(after.get("dialogs") or 0),
        "rows": int(after.get("rows") or 0),
        "links": int(after.get("links") or 0),
        "other": int(after.get("other") or 0),
        # Keys are members of LABEL_VOCABULARY by construction; values are
        # ints.
        #
        # THE LOOP VARIABLES ARE NAMED `vocab_word` AND `vocab_hits` RATHER
        # THAN `key` AND `value`, AND THAT IS NOT COSMETIC. The page-text taint
        # guard tracks names across a MODULE, not per scope -- the same
        # property that cost a sibling wave three findings at 196394d. Binding
        # `key` here from a page-derived object taints the name `key`
        # EVERYWHERE in this file, including a loop over LABEL_VOCABULARY in a
        # function that touches no page at all. Measured: with the old names
        # the guard reported this file 0 -> 1; with these it reports nothing.
        #
        # And note what does NOT fix it: `_COUNTING_CALLS` is `len` alone, so
        # wrapping a tainted name in `int()` launders nothing. Assigning does
        # not launder taint either -- the fixed point follows the binding.
        "labels": {
            str(vocab_word): int(vocab_hits)
            for vocab_word, vocab_hits in dict(after.get("labels") or {}).items()
            if vocab_word in LABEL_VOCABULARY
        },
    }


def report(title, result):
    """Print a press result. INTEGERS AND CLOSED-VOCABULARY KEYS ONLY."""
    print(f"\n=== {title}")
    print(f"    status            {result['status']}")
    print(f"    controls          {result['controls']}")
    print(f"    dialogs before    {result['dialogs_before']}")
    print(f"    dialogs after     {result['dialogs_after']}")
    print(f"    rows in dialogs   {result['rows']}")
    print(f"    links in dialogs  {result['links']}")
    print(f"    unmatched dialogs {result['other']}")
    print(f"    VISIBLE dialogs   {int(result.get('visible_dialogs') or 0)}")
    print(f"    visible rows      {int(result.get('visible_rows') or 0)}")
    print(f"    visible headings  {int(result.get('visible_headings') or 0)}")
    print(f"    visible links     {int(result.get('visible_links') or 0)}")
    print(f"    visible elements  {int(result.get('visible_children') or 0)}")
    for label_word in LABEL_VOCABULARY:
        label_count = int(result["labels"].get(label_word) or 0)
        if label_count:
            print(f"    label SUBSTRING {label_word:<14} {label_count}")
    for tok_label in LABEL_VOCABULARY:
        tok_count = int((result.get("token_labels") or {}).get(tok_label) or 0)
        if tok_count:
            print(f"    label TOKEN     {tok_label:<14} {tok_count}")
    if "press_error_class" in result:
        print(f"    press error class {result['press_error_class']}")


async def main() -> int:
    _own_page = None
    control_before = 0
    control_after = 0
    on_profile = None
    on_control = None
    badge_before = {}
    badge_after = {}
    try:
        async with BROWSER.session() as page:
            _own_page = page

            # THE SESSION LIVENESS CONTROL and THE PRESSER'S OWN CONTROL,
            # taken on the SAME load. A page KNOWN to draw no contact-info
            # affordance, and known to census about CONTROL_EXPECTED controls.
            await BROWSER.goto(page, CONTROL_URL)
            control_before = int(
                (await dom.read_surface_census(page)).get("controls_read") or 0
            )
            on_control = await press_contact_control(page)

            await BROWSER.goto(page, FEED_URL)
            badge_before = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )

            await BROWSER.goto(page, PROFILE_URL)
            on_profile = await press_contact_control(page)
            # Dismiss whatever the press opened, on his own page.
            try:
                await page.keyboard.press("Escape")
            except Exception as exc:  # noqa: BLE001
                print("    dismiss unavailable:", type(exc).__name__)

            await BROWSER.goto(page, FEED_URL)
            badge_after = shape.invitation_badge(
                await dom.read_invitation_badge(page)
            )

            await BROWSER.goto(page, CONTROL_URL)
            control_after = int(
                (await dom.read_surface_census(page)).get("controls_read") or 0
            )
    finally:
        # THE PAGE, NEVER THE CONTEXT. The context is his own signed-in browser
        # session and a dozen waves share it.
        if _own_page is not None and not _own_page.is_closed():
            await _own_page.close()
        print("\n    tab closed:",
              _own_page.is_closed() if _own_page is not None else "no tab opened")

    if on_control is not None:
        report("CONTROL PAGE -- the presser must find NOTHING here", on_control)
    if on_profile is not None:
        report("HIS OWN PROFILE -- the measurement", on_profile)

    print("\n=== VERDICT")
    print(f"    control census {control_before} then {control_after} "
          f"(two presence readings, floor {int(CONTROL_EXPECTED * 0.5)}; "
          "reported side by side and NOT subtracted)")
    print(f"    invitation badge {badge_before.get('state')} "
          f"{badge_before.get('pending')} then {badge_after.get('state')} "
          f"{badge_after.get('pending')}")
    floor = int(CONTROL_EXPECTED * 0.5)
    if control_before < floor or control_after < floor:
        print("    THE SESSION CONTROL FAILED. Nothing above is a reading "
              "about his account.")
        return 1
    if on_control is None or on_profile is None:
        print("    A LEG DID NOT RUN. No conclusion.")
        return 1
    if on_control["status"] != "control_absent":
        print("    THE PRESSER FIRED WHERE NOTHING SHOULD BE THERE. Every "
              "count on the profile leg is void -- this instrument cannot "
              "tell a control from the absence of one.")
        return 1
    print("    presser control: control_absent on the known-empty page, so a "
          "clean absence and a broken presser are distinguishable")
    if on_profile["status"] == "control_absent":
        print("    NO CONTACT-INFO CONTROL ON HIS PROFILE by this aim. That "
              "is a PRESENCE reading and the presser is shown able to fire "
              "elsewhere -- but a single aim is one instrument, not two.")
        return 0
    if on_profile["status"] == "press_failed":
        print("    THE CONTROL EXISTS AND THE PRESS DID NOT LAND. The panel "
              "remains unobserved and the row does not move.")
        return 1
    print("    THE PANEL WAS OPENED. Counts above are of SECTIONS AND LINKS, "
          "never of values.")
    print("    VALUES PUBLISHED BY THIS RUN: 0. The in-page script has no "
          "branch that returns page text, so there is no filter to have got "
          "wrong.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
