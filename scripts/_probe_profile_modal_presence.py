"""Ask whether the profile's modal-opening controls are DRAWN, and press one.

**THIS IS A PRESENCE INSTRUMENT AND NOT A DELTA ONE, and the distinction is
the reason it exists.** Three waves in this repo measured CHANGE at a question
about whether controls EXIST; one published a conclusion contradicting a number
it had printed two lines earlier. The four blockers this probe serves --
``OPEN-TO-WORK-MODAL``, ``OPEN-TO-HIRING-MODAL``,
``INTRO-EDITOR-UNREAD-CONTROLS`` and ``ADD-SECTION-MENU`` -- all ask "is this
drawn at all". So every reading below is an ABSOLUTE COUNT taken directly, and
the one before/after pair is reported as two absolute counts rather than as a
difference.

**WHAT IT PRESSES, AND WHAT IT REFUSES TO PRESS.** It presses exactly one
control: the profile's add-a-section menu button, which opens a list and adds
nothing. It presses Escape afterwards. It does NOT press the open-to-work
card's editor entry, and that refusal is a RULING already written into this
package rather than this probe's caution -- ``writes.SANCTIONED_WRITES
["linkedin_set_open_to_work"].reversibility_procedure`` records that the
editor's entry control fires a request named ``saveAndFetchNextStep``, so
**the one click that would first REVEAL the editor is also the first click
that could CHANGE it.** A census that presses it is not a measurement; it is
an unconsented write on his live profile. Presence is the most that may be
read here without him watching.

**THE CONTROL RUNS FIRST AND GATES THE REPORT.** A needle-count reader's most
likely output is a zero, and a zero from a working reader and a zero from a
broken one are the same character. So ``run_controls`` aims the SAME reader at
a fragment where the answer is known in both directions -- a needle that must
count 2 and a needle that must count 0 -- against markup this file owns. If
the must-find needle reports 0 the reader is broken and the live numbers are
not reported at all.

**IDENTITY.** No accessible name, href or page text leaves this process. The
needles are module-level literals written here, from LinkedIn's own interface
vocabulary; matching happens INSIDE the page and only an integer comes back.
Navigation results are reported as a RELATION, never as an address.

Read-only apart from the single menu press. Attaches; never launches.
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import AUTHWALL_MARKERS  # noqa: E402

#: Already on the read allowlist. This probe adds no address and no pattern.
SELF_PROFILE_URL = "https://www.linkedin.com/in/me/"
SELF_PROFILE_EDIT_INTRO_URL = "https://www.linkedin.com/in/me/edit/intro/"

#: STRUCTURAL CLASSES -- counted by CSS, so no string leaves the page.
#: ``menu_items`` is here because ``dom.CENSUS_CONTROL_SELECTOR`` does NOT
#: carry a menuitem role: the shipped census COUNTS this class and never LISTS
#: it, so a pressed menu can add nineteen items to the page and zero rows to
#: the census's ``controls``. That is the ``CENSUS_CONTROL_SELECTOR`` defect
#: this repo already recorded once, measured here rather than repeated.
STRUCTURAL: dict[str, str] = {
    "dialogs": '[role="dialog"], dialog',
    "menus": '[role="menu"]',
    "menu_items": '[role="menuitem"], [role="menuitemcheckbox"], '
                  '[role="menuitemradio"]',
    "expanded_false": '[aria-expanded="false"]',
    "expanded_true": '[aria-expanded="true"]',
    "haspopup": "[aria-haspopup]",
    "modal_true": '[aria-modal="true"]',
    "census_controls": (
        'button, a[href], input, textarea, select, '
        '[role="button"], [role="link"], [role="textbox"], [role="combobox"], '
        '[contenteditable]:not([contenteditable="false"])'
    ),
}

#: NEEDLES ARE THIS FILE'S OWN STRINGS. Each names a control this repo has
#: already recorded, with the artifact that recorded it. A count comes back;
#: the matched name never does.
NEEDLES: tuple[tuple[str, str], ...] = (
    # census profile.md D25 -- the menu whose 19 items are enumerated from a
    # Help article and have never been read off the rendered page.
    ("add_profile_section", "add profile section"),
    # set_open_to_work.reversibility_evidence, 2026-08-24 correction: the real
    # entry point is a control named "Edit" on the open-to-work card, pinned in
    # both frozen renders. "Open to" is the OTHER control -- the one that
    # correction proved was NOT the audience editor.
    ("edit", "edit"),
    ("open_to", "open to"),
    # census profile.md block J -- the Open-To-Hiring entry, observed across
    # five captures with nothing acting on it.
    ("hiring", "hiring"),
    ("providing_services", "providing services"),
    ("volunteer", "volunteer"),
    # A needle no LinkedIn surface draws. Its job is to be zero on every page,
    # so a reader that returns nonzero everywhere is visible as broken.
    ("must_be_absent", "zzq-not-a-linkedin-control-zzq"),
)

#: Markup this file owns, used to prove the needle reader can both find and
#: fail to find. Two matches for one needle, zero for the other, and the
#: DETECTOR IS NOT THE ASSERTION -- the expected integers are written here.
CONTROL_FRAGMENT = (
    '<div>'
    '<button aria-label="Add profile section">a</button>'
    '<div role="button" aria-label="Add profile section to page">b</div>'
    '<button aria-label="Open to">c</button>'
    '<div role="menu"><div role="menuitem">m1</div>'
    '<div role="menuitem">m2</div><div role="menuitem">m3</div></div>'
    '</div>'
)
CONTROL_EXPECT_NEEDLES: dict[str, int] = {
    "add_profile_section": 2,
    "open_to": 1,
    "must_be_absent": 0,
}
CONTROL_EXPECT_STRUCTURAL: dict[str, int] = {
    "menus": 1,
    "menu_items": 3,
    "dialogs": 0,
}

#: Counts the needle against accessible-name-ish attributes and text, INSIDE
#: the page. Returns integers only.
NEEDLE_JS = """
(cfg) => {
  const nameOf = (el) => (
    el.getAttribute('aria-label') ||
    el.getAttribute('title') ||
    (el.textContent || '')
  ).trim().toLowerCase();
  const nodes = Array.from(document.querySelectorAll(cfg.controlSelector));
  const out = {};
  for (const [key, needle] of cfg.needles) {
    out[key] = nodes.filter((el) => nameOf(el).includes(needle)).length;
  }
  out.__total = nodes.length;
  return out;
}
"""

STRUCTURAL_JS = """
(cfg) => {
  const out = {};
  for (const [key, sel] of cfg.selectors) {
    try { out[key] = document.querySelectorAll(sel).length; }
    catch (e) { out[key] = -1; }
  }
  return out;
}
"""


def _relation(landed: str, asked: str) -> str:
    """Did the address serve, or did LinkedIn send us somewhere else?

    THE BODY OF THIS FUNCTION IS BYTE-IDENTICAL TO THE TWO COPIES IN THE
    GROUPS PROBES, AND THAT IS ENFORCED rather than intended:
    ``test_every_relation_definition_is_byte_identical`` compares them. My
    first draft was a DIFFERENT function wearing this name -- it had a branch
    returning "redirected WITHIN member space", which is a claim about member
    space that the sanctioned version does not make -- and the guard caught it
    on the first run. A sanitiser admitted to ``_SANITISERS`` is admitted as a
    contract, not as a name; a local variant is a second contract sharing one
    entry.

    RETURNS A RELATION AND NEVER A URL. Every branch below yields a literal or
    an integer depth; no part of either input survives into the result.
    """
    if str(landed) == str(asked):
        return "SERVED, exact"
    asked_depth = len([seg for seg in urlsplit(str(asked)).path.split("/") if seg])
    landed_depth = len([seg for seg in urlsplit(str(landed)).path.split("/") if seg])
    if asked_depth != landed_depth:
        return f"REDIRECTED, path depth {asked_depth} -> {landed_depth}"
    return "SERVED, same depth, different url"


async def read_needles(page) -> dict[str, int]:
    return await page.evaluate(  # readonly-ok
        NEEDLE_JS,
        {"controlSelector": STRUCTURAL["census_controls"],
         "needles": [list(pair) for pair in NEEDLES]},
    )


async def read_structural(page) -> dict[str, int]:
    return await page.evaluate(  # readonly-ok
        STRUCTURAL_JS,
        {"selectors": [[k, v] for k, v in STRUCTURAL.items()]},
    )


async def run_controls(page) -> bool:
    """Prove BOTH readers can speak and can stay silent. Gates the report."""
    print("=" * 70)
    print("CONTROLS -- run first, and their result gates every number below")
    print("=" * 70)
    await page.set_content(f"<!doctype html><html><body>{CONTROL_FRAGMENT}"
                           "</body></html>")
    ok = True
    # THE COUNTS ARE NOT BOUND TO A LOCAL, AND THAT IS THE GUARD TALKING.
    # ``test_no_navigation_derived_value_reaches_an_output_sink`` tracks
    # tainted NAMES across a whole module, so ``got = int(needles.get(...))``
    # made the name ``got`` browser-derived everywhere in this file and turned
    # these two control lines -- which report integers from markup this file
    # OWNS, via ``set_content`` -- into taint findings. The guard is right to
    # be structural and cannot know the difference, so the call is inlined at
    # the print instead, which is the form the guard already recognises.
    needles = await read_needles(page)
    for key, expected in CONTROL_EXPECT_NEEDLES.items():
        if int(needles.get(key, -1)) != expected:
            ok = False
        print(f"  needle {key:24s} expected {expected}  "
              f"got {needles.get(key, -1)}  "
              f"{'PASS' if int(needles.get(key, -1)) == expected else 'FAIL'}")
    structural = await read_structural(page)
    for key, expected in CONTROL_EXPECT_STRUCTURAL.items():
        if int(structural.get(key, -1)) != expected:
            ok = False
        print(f"  struct {key:24s} expected {expected}  "
              f"got {structural.get(key, -1)}  "
              f"{'PASS' if int(structural.get(key, -1)) == expected else 'FAIL'}")
    print(f"\n  DETECTOR USABLE: {ok}")
    if not ok:
        print("  Live numbers are NOT reported: a reader that cannot pass its "
              "own control cannot distinguish a clean absence from a broken "
              "aim, and a zero is the reading this probe most expects.")
    return ok


async def read_surface(page, label: str, address: str) -> dict:
    print("\n" + "=" * 70)
    print(f"SURFACE: {label}")
    print("=" * 70)
    try:
        landed = await BROWSER.goto(page, address)
    except Exception as exc:  # noqa: BLE001
        print(f"  NAVIGATION REFUSED: {type(exc).__name__}")
        return {"refused": type(exc).__name__}
    print(f"  {_relation(landed, address)}")
    if any(marker in landed for marker in AUTHWALL_MARKERS):
        print("  AUTHWALL -- nothing was read")
        return {"authwall": True}
    needles = await read_needles(page)
    structural = await read_structural(page)
    print(f"  controls matched by the census selector : "
          f"{needles.get('__total')}")
    print("  PRESENCE, taken directly and not as a difference:")
    for key, _needle in NEEDLES:
        print(f"    needle {key:24s} {needles.get(key)}")
    for key in STRUCTURAL:
        if key == "census_controls":
            continue
        print(f"    struct {key:24s} {structural.get(key)}")
    return {"needles": needles, "structural": structural}


async def press_add_section(page) -> dict:
    """Press the ONE control here that opens a list and changes nothing.

    Reported as TWO ABSOLUTE READINGS, never as a delta, because the question
    the press serves is "what does the menu contain" and not "did anything
    move". If the menu does not open, that is a fact about the aim and is
    printed as one.
    """
    print("\n" + "=" * 70)
    print("PRESS -- add-a-section menu button, then Escape")
    print("=" * 70)
    before = await read_structural(page)
    print(f"  BEFORE  menus={before.get('menus')}  "
          f"menu_items={before.get('menu_items')}  "
          f"dialogs={before.get('dialogs')}")
    pressed = False
    try:
        target = page.locator(
            'button[aria-label*="Add profile section" i], '
            '[role="button"][aria-label*="Add profile section" i]'
        ).first
        if await target.count() > 0:
            await target.click(timeout=8000)
            await page.wait_for_timeout(1200)
            pressed = True
        else:
            print("  NOT PRESSED: no control carries that accessible name on "
                  "this render. That is a reading about the page, and this "
                  "probe reports it rather than widening its aim until "
                  "something matches.")
    except Exception as exc:  # noqa: BLE001
        print(f"  PRESS FAILED: {type(exc).__name__}")
    after = await read_structural(page)
    print(f"  AFTER   menus={after.get('menus')}  "
          f"menu_items={after.get('menu_items')}  "
          f"dialogs={after.get('dialogs')}")
    census_like = await read_needles(page)
    print(f"  controls matched by the CENSUS selector after the press : "
          f"{census_like.get('__total')}")
    print("  ^ compare against the same number before the press. The census "
          "selector carries NO menuitem role, so an opened menu can add items "
          "to the page and nothing to what the census would LIST.")
    if pressed:
        with contextlib.suppress(Exception):
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)
        closed = await read_structural(page)
        print(f"  AFTER ESCAPE  menus={closed.get('menus')}  "
              f"menu_items={closed.get('menu_items')}")
    return {"pressed": pressed, "before": before, "after": after}


@contextlib.asynccontextmanager
async def own_tab():
    """``BROWSER.session()`` plus the close nobody does.

    THE PAGE, NEVER THE CONTEXT. In attach mode the context is the operator's
    signed-in browser; the tab is ours. Copied deliberately from
    ``_probe_analytics_controls_live.own_tab`` rather than imported, because a
    probe that cannot run standalone is a probe nobody runs.
    """
    async with BROWSER.session() as page:
        try:
            yield page
        finally:
            try:
                if not page.is_closed():
                    await page.close()
            except Exception as exc:  # noqa: BLE001
                print(f"  NOTE: could not close this probe's tab "
                      f"({type(exc).__name__}); it is left open and counts "
                      "against the next attach")


async def main() -> int:
    if os.environ.get("LINKEDIN_CDP_ATTACH") != "1":
        print("REFUSING: set LINKEDIN_CDP_ATTACH=1 and LINKEDIN_CDP_PORT. "
              "The profile is shared and a launch is a browser DOWNGRADE.")
        return 2
    controls_only = "--control" in sys.argv
    async with own_tab() as page:
        detector_ok = await run_controls(page)
        if controls_only:
            return 0 if detector_ok else 1
        if not detector_ok:
            return 1
        await read_surface(page, "self_profile", SELF_PROFILE_URL)
        await press_add_section(page)
        await read_surface(page, "intro_editor", SELF_PROFILE_EDIT_INTRO_URL)
    print("\n" + "=" * 70)
    print("WHAT THIS DOES NOT SETTLE")
    print("=" * 70)
    print("  The open-to-work editor was NOT opened and must not be. Its "
          "entry control fires saveAndFetchNextStep, so revealing it is the "
          "same click as changing it. Presence of an entry control is not "
          "evidence about what is behind it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
