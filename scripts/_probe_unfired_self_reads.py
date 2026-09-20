"""FIRE the two SELF-DIRECTED read tools the census carries as UNFIRED.

    M M45   Open a blank compose window      -> linkedin_compose_fields
    M C41   View your own activity feed      -> linkedin_my_activity_items

## WHY THESE TWO AND NOT THE OTHER FIVE MESSAGING ROWS

The messaging slice holds seven UNFIRED rows. Five of them are NOT fired by
this wave and the reason is the same one the census already gave itself:

* `M C1`, `M C25`, `M C32` publish a post, comment on a post and react to a
  post. They are WRITES against a real professional identity. Not fireable.
* `M M33` and `M M43` need `linkedin_open_messaging`, which by its own
  docstring opens a LinkedIn-chosen conversation thread and may reset the
  messaging badge. `_audit/2026-08-30-linkedin-writes.md` declined it in those
  words -- *"The cost lands on somebody who is not him, so it is his to
  spend."* That reasoning has not expired, and a second wave spending it
  quietly would be worse than the first one declining it loudly.

The same rule keeps `linkedin_notifications` out of this wave, and with it
`N 20` and `N 45`: loading `/notifications/` CLEARS THE UNREAD BADGE, which
that tool's own docstring calls *"the only server-side change any READ in this
package causes WITHOUT BEING ASKED FOR IT."* It is read-only by the write-gate
classification and it still destroys information the operator has. Not fired.

**THE TWO BELOW ARE DIFFERENT: both act on HIS OWN surfaces and neither
consumes a counter that belongs to anyone else.** `linkedin_compose_fields`
names the controls on an EMPTY composer and refuses if any recipient is
present; `linkedin_my_activity_items` loads `/in/me/` and clicks nothing.

## WHAT A FIRE PROVES HERE, AND WHAT IT DOES NOT

`M C41`'s census cell records that EVERY recorded live run of
`linkedin_my_activity_items` REFUSED -- `no_page_owner_heading`,
`owner_headings 0`, and on a later run `no_self_assertion` five calls running.
**It has never returned an item.** So the interesting outcome is not "did it
run" but WHICH of the two it does now, and a refusal is a result rather than a
failure of this probe. The refusal REASON is printed; nothing it read is.

`M M45`'s cell records a live fire on 2026-09-02 returning
`refused: name_shaped_label_present`, with the repaired build never re-run.
Same shape: the verdict is the finding.

## WHAT LEAVES THIS PROCESS

VERDICT STRINGS THIS FILE AUTHORS, COUNTS, AND REFUSAL REASON KEYS. No control
label, no message, no recipient, no activity item and no page text. A refusal
reason is a short machine token this server chose (`no_page_owner_heading`),
not something LinkedIn wrote, and it is the whole point of the reading.

## IT FIRES NO WRITE

Nothing is typed, dispatched, posted, reacted to or sent.

Run it as::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_unfired_self_reads.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import dom, server  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

CONTROL_URL = "https://www.linkedin.com/jobs/search/?keywords=node.js"

#: Keys whose VALUE is a verdict this server authored, safe to print. Anything
#: not on this list is reported by TYPE and LENGTH only.
VERDICT_KEYS = ("ok", "refused", "reason", "state", "error")


async def _badge(page) -> dict:
    try:
        reading = await dom.read_invitation_badge(page)
    except Exception as exc:  # noqa: BLE001
        return {"error": type(exc).__name__}
    return reading if isinstance(reading, dict) else {"error": "no reading"}


def _badge_state(reading: dict) -> str:
    if reading.get("error"):
        return "UNREADABLE (error)"
    if reading.get("badge_links") != 1:
        return "UNREADABLE (badge_links is not exactly 1)"
    if reading.get("label") is None:
        return "UNREADABLE (no label)"
    return "READABLE"


def _consumption(before: dict, after: dict) -> str:
    if _badge_state(before) != "READABLE" or _badge_state(after) != "READABLE":
        return ("UNKNOWN -- one end could not be read, so this says nothing "
                "rather than saying nothing was spent")
    if before.get("label") == after.get("label"):
        return "the badge did not move across this read"
    return "THE BADGE MOVED -- something was spent"


async def _control_serves(page) -> bool:
    await BROWSER.goto(page, CONTROL_URL)
    return await page.locator("div.job-card-container").count() > 0


def _report(label: str, out: dict) -> str:
    """Print the SHAPE of a tool result and return a one-word outcome."""
    print("\n### " + label)
    if not isinstance(out, dict):
        print("    the tool did not return a dict")
        return "NO-DICT"
    print("    top-level keys: " + str(len(out)))
    for key in sorted(out):
        value = out[key]
        if key in VERDICT_KEYS:
            # A verdict this server authored. Printed.
            print("    " + key + " = " + str(value)[:80])
        elif isinstance(value, (list, tuple)):
            print("    " + key + ": list of " + str(len(value)))
        elif isinstance(value, dict):
            print("    " + key + ": dict of " + str(len(value)) + " keys")
        elif value is None:
            print("    " + key + ": None")
        else:
            # LinkedIn may have written it. TYPE AND LENGTH ONLY.
            print("    " + key + ": " + type(value).__name__ + ", length "
                  + str(len(str(value))))
    if out.get("refused"):
        return "REFUSED"
    if out.get("error"):
        return "ERROR"
    return "RETURNED"


async def main() -> int:
    outcomes: dict = {}
    raw: dict = {}
    try:
        print("### CONTROL, before anything")
        async with BROWSER.session() as page:
            first_control = await _control_serves(page)
            print("    control serves: " + str(first_control))
            badge_before = await _badge(page)
            print("### invitation badge BEFORE: " + _badge_state(badge_before))
        if not first_control:
            print("    THE CONTROL DID NOT SERVE. This run is VOID. Stopping.")
            return 1

        # M M45 -- the blank composer.
        try:
            out = await server.linkedin_compose_fields()
        except Exception as exc:  # noqa: BLE001
            print("\n### M M45 -- linkedin_compose_fields RAISED "
                  + type(exc).__name__)
            out = {"error": type(exc).__name__}
        outcomes["M M45 compose_fields"] = _report(
            "M M45 -- linkedin_compose_fields (blank compose window)", out)
        raw["M45"] = out

        # M C41 -- his own activity feed.
        try:
            out2 = await server.linkedin_my_activity_items()
        except Exception as exc:  # noqa: BLE001
            print("\n### M C41 -- linkedin_my_activity_items RAISED "
                  + type(exc).__name__)
            out2 = {"error": type(exc).__name__}
        outcomes["M C41 my_activity_items"] = _report(
            "M C41 -- linkedin_my_activity_items (your own activity feed)",
            out2)
        raw["C41"] = out2

        async with BROWSER.session() as page:
            badge_after = await _badge(page)
            print("\n### invitation badge AFTER: " + _badge_state(badge_after))
            print("    CONSUMPTION: " + _consumption(badge_before, badge_after))
            print("\n### CONTROL AGAIN, at the end")
            last_control = await _control_serves(page)
            print("    control serves: " + str(last_control))
        if not last_control:
            print("    THE CONTROL STOPPED SERVING. Readings above are VOID.")
            return 1
    except Exception as error:  # noqa: BLE001
        print("\nRUN ABORTED: " + type(error).__name__)
        print("    " + str(error)[:300])
        return 1
    finally:
        # CLOSE OUR TAB, THEN DROP THE CDP CONNECTION.
        #
        # `BROWSER.stop()` alone would already close it -- its teardown closes
        # the tab this process opened and leaves the operator's Chrome
        # serving. The page is closed EXPLICITLY FIRST anyway, for two
        # reasons. It is the idiom the rest of this package uses and the one
        # `tests/test_a_probe_closes_its_own_tab.py` recognises, and that test
        # is a RATCHET: 39 of 43 session-opening scripts leak a tab per run,
        # the count may only go down, and a probe that cleans up by a route
        # the detector cannot see would have pushed the pin UP while actually
        # being clean. Leaking is not untidiness here -- `connect_over_cdp`
        # enumerates every target on attach, and this wave's own attach took
        # 93 seconds against 56 targets and failed outright at the 15s default.
        #
        # THE PAGE, NEVER THE CONTEXT. In attach mode the context is his
        # signed-in browser; closing it closes his window.
        try:
            own = getattr(BROWSER, "_own_page", None)
            if own is not None and not own.is_closed():
                page = own
                await page.close()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    closing our tab raised " + type(exc).__name__)
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    cleanup raised " + type(exc).__name__)

    print("\n" + "=" * 68)
    print("### OUTCOMES")
    for k in sorted(outcomes):
        print("    " + k + ": " + outcomes[k])
    print("")
    print("    A REFUSED outcome does NOT bank its row. It is a fresh")
    print("    measurement of a tool that ships expecting to refuse, and the")
    print("    row stays COVERED-UNFIRED carrying the reason above.")

    state = _ROOT / "_state"
    state.mkdir(exist_ok=True)
    (state / "unfired-self-reads-raw.json").write_text(
        json.dumps(raw, indent=2, default=str), encoding="utf-8")
    print("\n### RAW results written under _state/ (gitignored)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
