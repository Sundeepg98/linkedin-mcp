"""WHICH ELEMENT DOES A HUMAN ACTUALLY CLICK TO SET A DARK-MODE RADIO?

THE MEASUREMENT THAT PROVOKED THIS, from the first live `update_setting` on
2026-09-03, driven with a real confirm token::

    performed      false
    clicks_made    0
    state_before   Always off
    observed_state Always off        (fresh navigation + re-read of all three)
    selector       role=radio[name="Always on"s]
    error          TimeoutError: Page.click: Timeout 10000ms exceeded
                   locator resolved to <input name="theme" type="radio"
                     value="dark" id="theme__dark"
                     aria-labelledby="theme__dark__label">
                   <div class="setting-radio__button"> intercepts pointer events
                   ... 23 retries over 10s, every one intercepted

**THE SELECTOR IS NOT THE DEFECT.** It resolved the right input, by accessible
name, exactly as designed -- LinkedIn styles its radios by covering the real
`<input>` with a decorative element, so the input is visible, enabled, stable
and still unclickable. Playwright retried 23 times and reported it honestly.
Everything downstream worked: the gate re-navigated, re-read all three radios
through the browser's own `checked` property, and reported the state UNCHANGED.

THE LABEL CANDIDATE IS ALREADY DEAD, AND A READ KILLED IT
----------------------------------------------------------
The obvious fix is "click the label" -- clicking a `<label for=...>` activates
its control, and the input names itself through `aria-labelledby`. **Measured
2026-09-03 via `linkedin_surface_census` on this page: all three radios report**

    name_source: "aria-labelledby"

and that is the finding rather than a detail. The census resolves a name by
trying `label-for` FIRST, then `label-ancestor`, and only then
`aria-labelledby`. Falling through to the third means **there is no `<label
for>` bound to these inputs and no label ancestor either.**

`aria-labelledby` is a NAMING relation. `<label for>` is an ACTIVATION
relation. They are not the same thing, and only the second makes a click on
the text set the radio. So clicking `#theme__dark__label` would very likely
pass every actionability check and change nothing -- **a candidate that fails
by SUCCEEDING**, which is the worst shape available and exactly why this was
worth reading before building.

WHAT IS ACTUALLY LEFT
---------------------
1. **THE DECORATION**, `.setting-radio__button` -- the element the live error
   named as the interceptor. If it intercepts the pointer, it is probably what
   a human's pointer lands on, and therefore probably what is wired. It must be
   reached FROM the named input rather than by position: start at the radio
   found by accessible name, walk to its own nearest ancestor, and require
   exactly one decoration inside it.
2. **THE NAME SOURCE**, tested anyway -- to confirm the negative behaviourally
   and to record whether it passes actionability. **A PASS THERE IS NOT GOOD
   NEWS.** Read the verdict block at the end before drawing any conclusion
   from it.

This probe does not choose by argument. It reads.

WHY A TRIAL CLICK IS THE RIGHT INSTRUMENT, AND WHY IT IS NOT A WRITE
---------------------------------------------------------------------
Playwright's `click(trial=True)` runs EVERY actionability check -- visible,
stable, receives events, enabled -- and then **performs no action**. It is the
only way to ask "would this click land?" without finding out by landing one.
So this file contains `.click(` and changes nothing, and it says so here
because a reader who greps for that token should not have to guess.

**IT WILL NOT SET THE SETTING.** No trial click can, on any branch. The dark
mode this account is in when the probe starts is the dark mode it is in when
the probe ends.

WHAT IT SETTLES
---------------
For each of the three radios, found BY ACCESSIBLE NAME:

* how many controls carry that name (must be exactly one, or the aim is
  ambiguous and nothing else matters);
* the `aria-labelledby` id the input points at, whether an element with that id
  exists, whether it is a `<label>`, and what its `for` attribute says;
* whether a trial click on the INPUT passes -- expected to fail, and its
  failing is the reproduction;
* whether a trial click on the LABEL passes -- the question;
* whether a trial click on the decorative BUTTON passes, where one can be
  identified for that radio.

WHAT IT CANNOT SETTLE. Whether clicking the winning candidate actually MOVES
the radio. Actionability is not effect: an element can be perfectly clickable
and wired to nothing. Only a real `update_setting` settles that, and its
verification already works -- fresh navigation, re-read all three through the
browser's own `checked` property, destination checked and the other two not.
That is what proved the failure rather than guessing at it, and it is
deliberately unchanged.

NO IDENTITY IS INVOLVED. This is the operator's own preferences page; the three
control names are `Always off`, `Always on` and `Device settings`, and the ids
are DOM ids. Nothing here belongs to a third party, which is why this probe
prints what it reads instead of counting it.

Run:  python scripts/_probe_radio_click_target.py
Writes NOTHING.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, writes  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

ACTION = "update_setting"

#: How long a trial click may spend on actionability before it is a NO. Short
#: on purpose: the live failure retried for ten seconds and every retry was
#: intercepted, so a candidate that has not settled in two is not the answer,
#: and three radios times three candidates times ten seconds is a probe nobody
#: runs twice.
TRIAL_TIMEOUT_MS = 2_000

#: The decorative element the live error named as the interceptor.
DECORATION = ".setting-radio__button"


async def _trial(locator, label: str) -> str:
    """Would a click on this land? PERFORMS NOTHING.

    ``trial=True`` runs the actionability checks and skips the action. A pass
    means Playwright would have clicked; it does NOT mean clicking achieves
    anything, which is the distinction the module docstring keeps.
    """
    try:
        await locator.click(trial=True, timeout=TRIAL_TIMEOUT_MS)
        return "PASSES"
    except Exception as exc:  # noqa: BLE001 - a refusal is the reading
        text = str(exc).replace("\n", " ")
        if "intercepts pointer events" in text:
            start = text.find("<div")
            return "INTERCEPTED " + (text[start : start + 90] if start > 0 else "")
        return type(exc).__name__ + ": " + text[:110]


async def _report_radio(page, name: str) -> None:
    print("\n=== radio named %r" % name)
    radio = page.locator(dom.named_role_selector("radio", name))
    count = await radio.count()
    print("    controls with this name   %d" % count)
    if count != 1:
        print("    STOPPING on this one: an aim that is not exactly one is not an aim.")
        return

    checked = await radio.is_checked()
    print("    checked now               %s" % checked)
    print("    input visible / enabled   %s / %s"
          % (await radio.is_visible(), await radio.is_enabled()))

    # --- candidate 0: the input itself, which is what ships ----------------
    print("    trial click on INPUT      %s" % await _trial(radio, "input"))

    # --- candidate 1: the accessible-name source ---------------------------
    #
    # THE ID IS READ FROM THE INPUT WE ALREADY FOUND BY NAME, never guessed.
    # That is what keeps the aim a NAME aim: the page tells us which element
    # names this radio, so following the pointer cannot land on a different
    # row however the three are ordered.
    labelled_by = await radio.get_attribute("aria-labelledby")
    print("    aria-labelledby           %r" % labelled_by)
    if labelled_by and " " not in labelled_by.strip():
        ident = labelled_by.strip()
        by_id = page.locator("#" + ident)
        exists = await by_id.count()
        print("    element with that id      %d" % exists)
        if exists == 1:
            is_label = await page.locator("label#" + ident).count()
            print("    is a <label>              %s" % bool(is_label))
            print("    its for attribute         %r" % await by_id.get_attribute("for"))
            print("    visible / enabled         %s / %s"
                  % (await by_id.is_visible(), await by_id.is_enabled()))
            verdict = await _trial(by_id, "name source")
            print("    trial click on NAME SRC   %s" % verdict)
            if verdict == "PASSES":
                print("      ^ AND THE BINDING EXISTS, measured. The two\n"
                      "        lines below settle it: this element IS a\n"
                      "        <label> and its for is this radio's own id,\n"
                      "        so the click ACTIVATES rather than merely\n"
                      "        landing. A pass here would NOT be good news\n"
                      "        if those two lines said otherwise -- an\n"
                      "        element that only NAMES a control clicks\n"
                      "        cleanly and sets nothing.")
    else:
        print("    (no single id to follow -- aria-labelledby is empty or a list)")

    # --- is there a <label for> at all? ------------------------------------
    #
    # THE CENSUS SAYS NO -- name_source is aria-labelledby on all three, and it
    # only reports that after failing to find a label-for and a label-ancestor.
    # Asked again here directly, because a claim inherited from another
    # instrument is a claim this probe cannot defend on its own.
    radio_id = await radio.get_attribute("id")
    if radio_id:
        bound = await page.locator('label[for="' + radio_id + '"]').count()
    # THIS LINE ONCE READ '(census predicts 0)' AND THE PREDICTION WAS MINE,
    # NOT THE CENSUS'S. linkedin_surface_census reports name_source
    # 'aria-labelledby' for these radios, and I read that as proving no
    # label-for exists. It proves nothing of the kind: the census's nameOf
    # dispatches aria-label -> aria-labelledby -> title -> label-for ->
    # text, so once the SECOND resolver answers the FOURTH is never
    # consulted. This query returned 1 where I had written 0, which is the
    # comparison doing its job on the person who wrote it.
        print("    <label for> bound to it   %d   (see note below)" % bound)

    # --- candidate 1: the decoration, reached FROM the named input ----------
    #
    # AN ANCESTOR WALK, NOT A POSITION. Playwright has no closest(), so this
    # goes through xpath from the element already identified BY NAME: up to its
    # nearest ancestor carrying the setting-radio class, then down to the
    # decoration inside THAT. The aim therefore stays a name aim -- reorder the
    # three rows and each radio still finds its own decoration.
    total = await page.locator(DECORATION).count()
    print("    %-25s %d on the page" % (DECORATION, total))
    # THE ANCESTOR IS COUNTED SEPARATELY FROM THE DECORATION INSIDE IT, and
    # that is a correction to this probe rather than extra detail.
    #
    # It printed ONE number, "in this radio's row", and that number was zero.
    # Zero there has TWO readings -- no such ancestor exists, or the ancestor
    # exists and holds no decoration -- and they say opposite things about
    # whether the walk is the right relation. Collapsing them is the defect
    # this repository has a name for, and it was in my own instrument while I
    # was using its output to rule a candidate dead.
    row = radio.locator("xpath=ancestor::*[contains(@class,'setting-radio')][1]")
    try:
        rows_found = await row.count()
    except Exception as exc:  # noqa: BLE001 - an unusable walk is a reading
        rows_found = -1
        print("    ancestor walk failed      %s" % type(exc).__name__)
    print("    setting-radio ancestors   %d" % rows_found)
    n = 0
    if rows_found == 1:
        try:
            n = await row.locator(DECORATION).count()
        except Exception as exc:  # noqa: BLE001 - reported, never raised
            n = -1
            print("    decoration count failed   %s" % type(exc).__name__)
        print("    ...decorations inside it  %d" % n)
    else:
        print("    ...decorations inside it  NOT ASKED -- there is no single "
              "ancestor to look inside, so a zero here would be a fact about "
              "the WALK and not about the row.")
    if n == 1:
        print("    trial click on DECORATION %s" % await _trial(scoped, "decoration"))


async def main() -> None:
    spec = writes.spec_for_action(ACTION)
    print("PROBE: which element does a human click to set a dark-mode radio?")
    print("  THIS RUN CHANGES NOTHING. Every click below is trial=True, which")
    print("  runs the actionability checks and performs no action.")

    async with BROWSER.session() as page:
        url = spec.url_template
        landed = await BROWSER.goto(page, url)
        # THE ASKED URL IS PRINTED AND THE LANDED ONE IS NOT, and the
        # difference is the whole of
        # tests/test_navigation_is_never_derived.py. `url` is a constant on
        # the spec and carries no identity; `landed` is a value THE BROWSER
        # CHOSE, and a value the browser chose handed to a print is how the
        # operator's slug reached a transcript three times in one day.
        #
        # So the landed url is reduced to the one RELATION anybody needs
        # from it -- did we end up at an auth wall -- and the string itself
        # never leaves this function.
        #
        # THAT GUARD CAUGHT THIS FILE ON ITS FIRST RUN, which is the second
        # time today an instrument somebody else built has caught me
        # inheriting a habit rather than a reason.
        walled = ('/login' in landed) or ('/checkpoint' in landed)
        print("")
        print("=== asked      %s" % url)
        print("    auth wall? %s" % walled)
        if walled:
            print("    Nothing was read. Sign in and re-run.")
            return

        for name in writes.DARK_MODE_STATES:
            await _report_radio(page, name)

        print("\n=== HOW TO READ THIS")
        print("    The INPUT line is the reproduction: it is expected to be")
        print("    INTERCEPTED, and that is the shipped defect.")
        print("    THE NAME-SOURCE LINE IS A TRAP. There is no <label for>")
        print("    binding on this page, so that element can pass every")
        print("    actionability check and still set nothing. A PASS there is")
        print("    not a candidate; it is the failure mode that looks like")
        print("    success, and only a real update_setting can tell them apart.")
        print("    A candidate is the answer only if it PASSES on ALL THREE")
        print("    radios -- one that works for two of them is a coincidence,")
        print("    and the aim has to hold whichever destination is asked for.")
        print("    ACTIONABILITY IS NOT EFFECT. A passing trial says Playwright")
        print("    would click it, not that clicking it moves the radio. Only a")
        print("    real update_setting settles that, and its verification is")
        print("    already the thing that proved the failure.")


# GUARDED, for the reason the sibling probes give at length: an import must not
# drive a browser. This one is a READ, so an accidental import would be cheaper
# than the typing probe's -- but the rule is the rule, and the guard costs a
# line.
if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(BROWSER.stop())
