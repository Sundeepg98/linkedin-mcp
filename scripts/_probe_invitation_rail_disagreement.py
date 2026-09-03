"""Nine controls or zero? The census and the invitation gate disagree.

THE MEASUREMENT THAT PROMPTED THIS, taken 2026-09-03, minutes apart, on the
SAME url in the SAME server process:

  * ``linkedin_surface_census(surface="profile")`` reported a control shaped
    ``"Invite <member> to connect"``, tag button, name_source aria-label,
    **count 9**, on a reading its own settle check called consistent (233
    controls expected, 233 read).
  * ``linkedin_send_invitation`` refused twice with **zero**: "no control
    whose accessible name ends ' to connect' rendered on this page."

Both load ``https://www.linkedin.com/in/me/``. ``writes.PROFILE_URL`` and
``server.SELF_PROFILE_URL`` are the same string, so this is not two pages.
One of these two readers is wrong about the same DOM, and until somebody says
WHICH, ``send_invitation`` cannot be repaired without guessing.

THE REPAIR MUST NOT BE A GUESS. The obvious move -- loosen the selector until
it matches -- is exactly the move that is forbidden here: a widened selector on
a control that sends a stranger a connection request is how an invitation
reaches whoever was drawn first. So the cause is measured first, and the fix
follows the cause.

## The hypotheses, cheapest first

**1. WHITESPACE. The label does not END with the suffix, it CONTAINS it.**
``dom.INVITE_CONTROL`` is ``button[aria-label$=" to connect"]`` and
``INVITE_NEEDLE_JS`` re-checks with ``endsWith``. Both are exact. The census
NORMALISES a name before it shapes it, so a label of ``"Invite X to connect "``
-- one trailing space, or a newline, or a non-breaking space -- shapes to
``"Invite <member> to connect"`` and is counted, while both of the gate's
predicates reject it. This would make the census right and the gate blind, and
it is the explanation that requires nothing exotic.

**2. LATE HYDRATION.** The rail arrives after the gate reads and before the
census does. Two readings, one wait between them, and "not yet" stops being the
same number as "not there". This is the same design as
``_probe_where_the_editor_lives``'s third hypothesis.

**3. NEITHER, AND THE COUNT IS REAL.** The rail genuinely was not drawn on the
gate's two loads and genuinely was on the census's one. Then every count below
is 9 on both readings, and the answer is that this surface is non-deterministic
and the gate needs a retry rather than a new selector.

Hypotheses 1 and 2 are distinguished by WHICH predicate moves; 1 and 3 by
whether the plain ``endsWith`` count is ever nonzero.

## What it emits, and the rule that bounds it

**INTEGERS. Only integers.** Every predicate below is evaluated INSIDE THE
PAGE and what crosses back is a count. No accessible name, no fragment of one,
and no length that could narrow one, ever enters this process -- these labels
carry OTHER PEOPLE'S NAMES, which is the whole reason ``INVITE_NEEDLE_JS``
compares in the page rather than in Python. A probe that printed one to a
transcript would be the exact leak this package's needle discipline exists to
prevent, and no field here can carry one.

## Bounds

ONE navigation, to a module constant. It clicks nothing, types nothing and
submits nothing. Reading a profile you already own emits no signal to anybody.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.writes import PROFILE_URL  # noqa: E402

#: How long before the second reading. Generous on purpose: the question is
#: whether the rail EVER arrives, not how quickly.
LATE_HYDRATION_WAIT_MS = 8_000

#: Every predicate, counted separately so the answer NAMES a cause instead of
#: reporting a total nobody can act on. Each returns a count and nothing else.
#:
#: The first two are what the gate actually runs today -- the CSS selector and
#: the JS ``endsWith`` that re-checks it. Everything after them is a candidate
#: explanation for a zero, ordered so that the first one to differ from
#: ``js_endswith`` names the defect.
COUNT_JS = """
(cfg) => {
  const suffix = cfg.suffix;
  const buttons = Array.from(document.querySelectorAll('button'));
  const labelled = buttons
    .map((n) => n.getAttribute('aria-label'))
    .filter((v) => v !== null && v !== undefined);

  // Normalisers, each isolating ONE way a label could fail an exact endsWith.
  const collapse = (s) => s.replace(/\\s+/g, ' ');
  const nbsp = (s) => s.replace(/\\u00a0/g, ' ');

  let trailing_ws = 0;
  let has_nbsp = 0;
  for (const v of labelled) {
    if (v !== v.trimEnd()) trailing_ws += 1;
    if (v.indexOf('\\u00a0') !== -1) has_nbsp += 1;
  }

  return {
    // LIVENESS FIRST. If these are near zero the page did not render and
    // every number below is meaningless.
    all_elements: document.querySelectorAll('*').length,
    all_buttons: buttons.length,
    buttons_with_aria_label: labelled.length,

    // WHAT THE GATE RUNS TODAY.
    css_suffix: document.querySelectorAll(cfg.selector).length,
    js_endswith: labelled.filter((v) => v.endsWith(suffix)).length,

    // CANDIDATE EXPLANATIONS FOR A ZERO.
    trimend_endswith: labelled.filter((v) => v.trimEnd().endsWith(suffix)).length,
    collapse_endswith: labelled.filter(
      (v) => collapse(nbsp(v)).trimEnd().endsWith(suffix)
    ).length,
    contains_suffix: labelled.filter((v) => v.indexOf(suffix) !== -1).length,
    contains_ci: labelled.filter(
      (v) => v.toLowerCase().indexOf(suffix.toLowerCase()) !== -1
    ).length,

    // SHAPE DIAGNOSTICS, still only counts.
    labels_with_trailing_whitespace: trailing_ws,
    labels_containing_nbsp: has_nbsp,
  };
}
"""

FIELDS = (
    "all_elements",
    "all_buttons",
    "buttons_with_aria_label",
    "css_suffix",
    "js_endswith",
    "trimend_endswith",
    "collapse_endswith",
    "contains_suffix",
    "contains_ci",
    "labels_with_trailing_whitespace",
    "labels_containing_nbsp",
)


async def _counts(page) -> dict[str, int]:
    """Every predicate, as integers. Raises nothing into the caller's lap."""
    cfg = {"selector": dom.INVITE_CONTROL, "suffix": dom.INVITE_CONTROL_SUFFIX}
    try:
        reading = await page.evaluate(COUNT_JS, cfg)
    except Exception as exc:  # pragma: no cover - defensive
        # THE EXCEPTION TYPE ONLY. Same rule read_invitation_surface keeps: a
        # driver that echoes its argument into an error message would publish
        # through this line.
        print(f"    UNREADABLE: {type(exc).__name__}")
        return {name: -1 for name in FIELDS}
    return {name: int(reading.get(name) or 0) for name in FIELDS}


def _show(title: str, counts: dict[str, int]) -> None:
    print(f"  {title}")
    for name in FIELDS:
        print(f"    {name:34s} {counts[name]:>6d}")


async def main() -> None:
    print("PROBE: the invitation rail, and which reader is wrong about it")
    print(f"  selector under test: {dom.INVITE_CONTROL}")
    print(f"  suffix under test:   {dom.INVITE_CONTROL_SUFFIX!r}")
    print("  emits COUNTS ONLY -- no accessible name crosses into python.\n")

    async with BROWSER.session() as page:
        landed = await BROWSER.goto(page, PROFILE_URL)
        # The landed url carries the member slug, so only its SHAPE is said.
        print(f"  navigated to the profile constant; landed on /in/: "
              f"{'/in/' in landed}")
        print(f"  self-assertion rode this load: "
              f"{'isSelfProfile=true' in landed}\n")

        print("=== READING ONE, immediately after the standard settle")
        first = await _counts(page)
        _show("counts:", first)

        print(f"\n=== READING TWO, after a further {LATE_HYDRATION_WAIT_MS}ms")
        print("    Same page, no navigation. A number that MOVES means the")
        print("    rail arrives late and the gate reads too early.")
        await page.wait_for_timeout(LATE_HYDRATION_WAIT_MS)
        second = await _counts(page)
        _show("counts:", second)

        print("\n=== WHAT MOVED BETWEEN THE READINGS")
        moved = [n for n in FIELDS if first[n] != second[n]]
        if not moved:
            print("    nothing. The page was settled on the first reading.")
        for name in moved:
            print(f"    {name:34s} {first[name]:>6d} -> {second[name]:>6d}")

        print("\n=== HOW TO READ THIS")
        print("    js_endswith 0 while collapse_endswith or trimend_endswith")
        print("      is 9 -> HYPOTHESIS 1. The label does not END with the")
        print("      suffix; it carries trailing or non-breaking whitespace.")
        print("      The census normalises before shaping and sees it; both of")
        print("      the gate's predicates are exact and do not. Fix is to")
        print("      normalise in the SAME place the census does, not to")
        print("      loosen the selector to a substring match.")
        print("    every count 0 on reading one and 9 on reading two ->")
        print("      HYPOTHESIS 2, late hydration. Fix is a settle, not a")
        print("      selector.")
        print("    css_suffix and js_endswith both 9 on both readings ->")
        print("      HYPOTHESIS 3. The reader is fine and the rail simply was")
        print("      not drawn on the gate's loads. Fix is a bounded retry")
        print("      that reports UNKNOWN, which is what it already does.")
        print("    contains_suffix 9 while every endswith form is 0 -> the")
        print("      suffix sits mid-label; the anchor itself is wrong and")
        print("      needs re-measuring, NOT widening.")
        print("    all_buttons near zero -> the page did not render. Nothing")
        print("      above means anything. Check this line first.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    asyncio.run(main())
