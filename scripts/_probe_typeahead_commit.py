"""DOES CLICKING A TYPEAHEAD SUGGESTION COMMIT A RECIPIENT? Nobody knows.

That sentence is the whole reason this file exists, and it is not rhetorical.
On 2026-09-03 a supervised ``linkedin_send_message`` run typed a correct,
first-degree name into an empty composer and ``writes._recipient_gate``
returned ``1_no_recipient_committed`` with all four chip selectors reading
ZERO. **A bare fill commits nobody.** That was the finding, and it settled one
question while opening the next one: typing into a typeahead is not choosing
from it, so something has to do the choosing -- and whether the choosing
commits anybody has never been observed either.

**THIS PROBE TAKES THAT MEASUREMENT AND STOPS.** It types a name, presses at
most one suggestion, reads the composer, and ends. It never types a message
body and never presses a send control, so there is no path through it that
dispatches anything.

WHY IT CANNOT BE A TEST
-----------------------
Every gate below is already covered over frozen markup in
``tests/test_typeahead_gate.py`` and ``tests/test_send_message_gate.py``, and
those tests are honest about what they prove: GIVEN a page that draws a
typeahead the way the fixture draws one, the logic is right. They cannot say
whether LinkedIn draws one that way, because the fixture and the code under
test were built from the same guess. **A fixture built from a guess cannot
validate the guess.** The only instrument that can is a live composer, and the
only way to read a committed recipient is to commit one.

THE FIRST MUTATING PROBE IN THIS REPOSITORY, AND THE ARGUMENT FOR IT
--------------------------------------------------------------------
The five sibling probes read. This one FILLS a combobox and CLICKS a row, so
it does not get waved through on the family's reputation.

* **Neither act dispatches anything.** A name in a combobox is a name in a
  combobox. Pressing a suggestion addresses a message that does not exist yet.
  The act that reaches another human being is the send click, and this file
  contains no send click -- asserted below by
  :func:`tests.test_typeahead_probe.test_the_probe_presses_no_send_control`
  rather than promised here.
* **It is strictly safer than the alternative instrument.** The other way to
  learn this is to run ``writes.perform`` on a real grant, and perform is
  BUILT to continue: on a proceeding recipient gate it types his message and
  presses Send. This stops at the exact line perform carries on from.
* **It refuses to start on a composer it did not find empty.** The
  precondition is ``writes._live_control``'s own -- no recipient committed,
  two dispatch radios with one checked, one ``div[role=textbox]``, one control
  named Send drawn DISABLED. So it can never type over a draft of his.
* **The residue is named out loud.** If it commits somebody, a name is left in
  a composer on his screen, and the closing block says so and tells him to
  clear it. This server does not type again to undo a write, which is the
  standing ruling, and a probe does not get a private exemption from it.

THE NEEDLE IS AN ARGUMENT, AND THERE IS NO DEFAULT
--------------------------------------------------
It names a real person, so it is not in this file and it never will be. It
arrives on the command line or in ``LINKEDIN_TYPEAHEAD_NEEDLE``, and **this
probe never prints it** -- every line below reports its LENGTH and its counts.
A CI log, a terminal scrollback and an agent transcript are all publication
channels, and the repository's rule is that a third party's name does not
enter one to explain a measurement.

WHAT A RUN SETTLES, AND WHAT IT CANNOT
--------------------------------------
SETTLES, whichever way it comes out:

* which of ``dom.TYPEAHEAD_OPTION_SELECTORS`` matches a live LinkedIn
  typeahead, per selector, as counts;
* whether the dropdown opens at all for a filled combobox;
* whether pressing the one row that carries the needle commits a recipient --
  read afterwards through ``dom.RECIPIENT_CHIP_SELECTORS``, whose four
  candidates have never matched anything on any page either, so a zero here
  still has two readings and the per-selector counts are how they are told
  apart;
* whether ``Send`` goes from disabled to enabled, which is an INDEPENDENT
  corroboration of the chip reading from a control that is not a chip.

CANNOT SETTLE:

* whether a message would send. Nothing here sends, and the only surface that
  could confirm a send is the thread, which is forbidden and costs a real
  person a read receipt.
* whether a mode is an InMail and what it would cost. Five readings put InMail
  as a filter pill and no balance exists in 77 controls. Unmeasured, and
  printed as unmeasured.

Run:  python scripts/_probe_typeahead_commit.py "<needle>"
      LINKEDIN_TYPEAHEAD_NEEDLE="<needle>" python scripts/_probe_typeahead_commit.py

Writes NOTHING. A composer holding a committed recipient holds a third party,
and a capture of one is a file somebody has to remember to destroy.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, writes  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import SETTLE_MS  # noqa: E402

#: The environment variable the needle may arrive in instead of argv.
NEEDLE_ENV = "LINKEDIN_TYPEAHEAD_NEEDLE"

#: The action this probe drives the gates of. Named once.
ACTION = "send_message"

#: A body that is never typed. It exists only because a canonical
#: ``member_and_text`` target has two halves and ``_subject_component_of``
#: refuses anything that is not the two-part form -- so the grant below has to
#: carry one to be splittable at all. **NOTHING IN THIS FILE FILLS IT.** The
#: run ends before the body fill, which is the point of the whole exercise.
UNSENT_BODY = "this probe stops before the body is typed and never types it"


def _needle() -> str:
    """The name to type, from argv or the environment. NO DEFAULT, EVER.

    A default would be a real person's name committed to this repository, and
    ``tests/test_no_committed_identity.py`` says out loud that its checks
    cannot detect one -- names have no shape. So the absence of a default is
    the guard, and it is enforced by this function refusing rather than by
    anybody remembering.
    """
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    from_env = os.environ.get(NEEDLE_ENV, "").strip()
    if from_env:
        return from_env
    raise SystemExit(
        "refusing to run: no needle was given. Pass the name to type as the "
        f"first argument, or set {NEEDLE_ENV}. This file carries no default "
        "because a default would be a real person's name in a tracked file."
    )


def _grant_for(needle: str) -> writes.WriteGrant:
    """A grant object built directly, NOT minted, and it cannot redeem itself.

    ``_live_control``, ``_typeahead_gate`` and ``_recipient_gate`` each read
    exactly one thing off a grant -- its ``target`` -- and driving the real
    preview/mint/consume chain to settle a question about a dropdown would put
    a row of unrelated gates between the question and the answer. The same
    narrowing ``tests/test_writes.py::_bare_grant`` makes, and it is not a way
    round the write door: ``perform`` refuses any grant ``consume`` has not
    burned, and this probe never calls ``perform``.
    """
    return writes.WriteGrant(
        action=ACTION,
        target=needle + writes.TARGET_JOIN + UNSENT_BODY,
        token="not-a-minted-token",
        minted_at=time.monotonic(),
    )


def _report(title: str, rows: dict) -> None:
    """Print a block of counts. NEVER a name."""
    print(f"\n=== {title}")
    for key, value in rows.items():
        print(f"    {key:<26} {value}")


async def _open_composer(page) -> str:
    """Navigate to the composer. THE URL IS THE SPEC'S CONSTANT, not a landed one.

    The team lead's 2026-09-03 ruling on ``BROWSER.goto`` is that its argument
    may be a module-level constant or an allowlist template and never a value
    derived from a prior navigation. ``spec.url_template`` for this action is a
    CONSTANT rather than a template -- the target is a member and a text, not a
    page -- so it is passed whole and nothing that came back from the browser
    is fed into a navigation.
    """
    url = writes.spec_for_action(ACTION).url_template
    await BROWSER.wait_for_rate_slot()
    await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    BROWSER._last_navigation_at = time.monotonic()
    try:
        await page.wait_for_load_state("networkidle", timeout=SETTLE_MS)
    except Exception:  # noqa: BLE001 - settling is best-effort, never a gate
        await page.wait_for_timeout(SETTLE_MS)
    return url


async def main() -> None:
    needle = _needle()
    grant = _grant_for(needle)
    spec = writes.spec_for_action(ACTION)

    print("PROBE: does clicking a typeahead suggestion commit a recipient?")
    print(f"  needle length            {len(needle)} chars (never printed)")
    print("  this run types NO message body and presses NO send control.")

    async with BROWSER.session() as page:
        url = await _open_composer(page)
        print(f"\n=== composer: asked {url}")
        landed = page.url
        walled = "/login" in landed or "/checkpoint" in landed
        print(f"    auth-wall?             {walled}")
        if walled:
            print("    STOPPING. Nothing was typed. Sign in and re-run.")
            return

        # --- 1. the precondition, and it is the shipped gate's own -----------
        state, why, selector, *_rest = await writes._live_control(
            page, spec, grant, ""
        )
        _report(
            "1. is this composer in the state the action acts from?",
            {"state": state, "fill target": selector or "(none)"},
        )
        print(f"    why: {why}")
        if state != "composer_empty" or not selector:
            print(
                "\n    STOPPING, AND NOTHING WAS TYPED. This is the shipped "
                "precondition refusing, not the probe failing -- the composer "
                "was not empty, or was not the shape this action is measured "
                "to act from. Anything typed from here would be typed over "
                "something this server cannot read back."
            )
            return

        # --- 2. THE FILL. Mutation one of two, and it dispatches nothing -----
        await page.fill(selector, needle, timeout=writes.CLICK_TIMEOUT_MS)
        print("\n=== 2. the needle is in the combobox. Nothing has been sent.")

        # --- 3. what the dropdown drew --------------------------------------
        reading = await dom.read_typeahead_options(page, needle)
        _report(
            "3. THE MEASUREMENT NOBODY COULD TAKE ANY OTHER WAY",
            {
                "listbox appeared": reading.get("appeared"),
                "options (total)": reading.get("total"),
                "carrying the needle": reading.get("matches"),
                "selector error": reading.get("error"),
            },
        )
        print("    per candidate selector:")
        for candidate, count in (reading.get("per_selector") or {}).items():
            print(f"      {count:>4}  {candidate}")
        # THE PATTERN CENSUS, AND ON THE LIVE SURFACE IT IS THE POINT OF THE
        # RUN. The first live reading returned ten options and ten matches,
        # because the shipped matcher is a SUBSTRING and a typeahead returns a
        # row BECAUSE it matched what was typed -- so that predicate counts
        # LinkedIn's result set instead of discriminating inside it. These
        # counts say which candidate could, and they say it without any
        # accessible name entering this process.
        print("    per candidate MATCHER (would-match counts, nothing pressed):")
        for label, count in (reading.get("pattern_census") or {}).items():
            print(f"      {count:>4}  {label}")
        print(
            "    READ THE CENSUS AS A DIAGNOSTIC, not a scoreboard. "
            "'prefix' at zero says the rows do not start with the name. "
            "'prefix_boundary' at zero while 'prefix_then_nonletter' is "
            "non-zero says the degree suffix is run onto the name with no "
            "separator, which is the case a word boundary cannot see."
        )
        print(
            "    A ZERO FROM EVERY CANDIDATE HAS TWO READINGS and this probe "
            "cannot choose between them: the dropdown did not open, or none "
            "of these is how LinkedIn draws one. A human looking at the "
            "screen tells those apart in a second."
        )

        # --- 4. the gate's verdict, unmodified ------------------------------
        gate = await writes._typeahead_gate(page, grant)
        _report(
            "4. what the shipped typeahead gate decides",
            {
                "proceed": gate.get("proceed"),
                "refused_condition": gate.get("refused_condition"),
            },
        )
        print(f"    why: {gate.get('why')}")

        if not gate.get("proceed"):
            print(
                "\n    STOPPING AT THE GATE. Nothing was clicked and no body "
                "was typed. THE NEEDLE IS STILL IN HIS COMPOSER -- go and "
                "clear it if you do not want it there; this server will not "
                "type again to undo a write."
            )
            return

        # --- 5. THE CLICK. Mutation two of two, and it dispatches nothing ----
        await page.click(gate["selector"], timeout=writes.CLICK_TIMEOUT_MS)
        print("\n=== 5. one suggestion was pressed. Still nothing has been sent.")

        # --- 6. THE ANSWER, read by the gate that was already shipped -------
        #
        # AND THE CLICK IS NOT ITS OWN EVIDENCE. Step 5 says a row was pressed.
        # Only this step says whether anybody is now committed, and it is the
        # same reader ``perform`` uses, called the same way. If these two
        # disagree -- a successful click and a zero chip count -- that IS the
        # finding, and it means clicking a suggestion is not what commits a
        # recipient either.
        chips = await dom.read_selected_recipients(page, needle)
        _report(
            "6. DID THE CLICK COMMIT ANYBODY?",
            {
                "committed recipients": chips.get("total"),
                "carrying the needle": chips.get("matches"),
            },
        )
        print("    per candidate chip selector:")
        for candidate, count in (chips.get("per_selector") or {}).items():
            print(f"      {count:>4}  {candidate}")

        verdict = await writes._recipient_gate(page, grant)
        _report(
            "7. what the shipped recipient gate decides",
            {
                "proceed": verdict.get("proceed"),
                "refused_condition": verdict.get("refused_condition"),
            },
        )
        print(f"    why: {verdict.get('why')}")

        # --- 8. the independent corroboration -------------------------------
        #
        # A DIFFERENT CONTROL ANSWERING THE SAME QUESTION. ``Send`` is measured
        # DISABLED on an empty composer. If it is ENABLED now, LinkedIn thinks
        # this composer is addressed -- which is not the same claim as "the
        # chip selectors found somebody", and that is exactly why it is worth
        # reading: two readers agreeing is evidence, and two disagreeing tells
        # us which one is wrong.
        send = await dom.read_compose_send_state(page)
        _report(
            "8. corroboration from a control that is not a chip",
            {
                "controls named Send": send.get("controls"),
                "enabled": send.get("enabled"),
                "body textboxes": send.get("textboxes"),
                "error": send.get("error"),
            },
        )

        print("\n=== WHAT THIS RUN DID AND DID NOT SETTLE")
        if int(chips.get("total") or 0) > 0:
            print("    A CLICK ON A SUGGESTION COMMITS A RECIPIENT. That is new.")
        else:
            print(
                "    A CLICK ON A SUGGESTION DID NOT PRODUCE A CHIP any of the "
                "four candidates can see. Either it commits nobody, or none of "
                "those four is how a committed recipient is drawn. Both counts "
                "above are needed to tell them apart, and so is the Send state."
            )
        print(
            "    NOTHING WAS SENT. No body was typed and no send control was "
            "pressed, on any branch of this file."
        )
        print(
            "    THE INMAIL COST REMAINS UNMEASURED. Five readings put InMail "
            "as a filter pill and no balance appears in 77 controls; this "
            "probe reads no balance and does not pretend to."
        )
        print(
            "\n    ON HIS SCREEN NOW: a name in the composer, and possibly a "
            "committed recipient. GO AND CLEAR IT. This server will not type "
            "again to undo a write and is telling you rather than deciding "
            "for you."
        )


# GUARDED, AND FOR THE REASON ``_probe_messaging.py`` SPELLS OUT AT LENGTH.
# ``tests/test_scripts_are_import_safe.py`` accepts an ATTRIBUTE call at module
# scope, and ``asyncio.run(...)`` is one -- so a probe ending in a bare
# ``asyncio.run(main())`` passes that guard while launching a browser on
# import. For a reading probe that is a real hole. For this one it would mean
# an import TYPING INTO HIS COMPOSER, which is the accident this file exists
# to avoid causing rather than to demonstrate.
if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(BROWSER.stop())
