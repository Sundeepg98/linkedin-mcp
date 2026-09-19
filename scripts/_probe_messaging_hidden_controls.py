"""Is a control ABSENT, or merely INVISIBLE? Row 76 turns on the difference.

WHY THIS EXISTS AS A SECOND FILE. The sibling probe
``_probe_messaging_menu_enumeration.py`` measured ZERO elements matching
``[aria-label*="React"]`` on a live conversation, where the ``messaging-rows``
wave had measured TWELVE on 2026-09-05. A zero like that has three quite
different causes and they retire opposite sets of rows:

1. **THE SPELLING.** A CSS attribute substring match is CASE-SENSITIVE on its
   value. ``[aria-label*="React"]`` cannot see ``react``, ``Reaction`` is a
   different string again, and the predecessor recorded exactly this trap on
   this surface -- its own ``label contains reaction`` read 0 while
   ``label contains React`` read 12. **So a case-sensitive zero is a fact about
   the query.** Every label selector here carries the CSS ``i`` flag.
2. **VISIBILITY.** LinkedIn reveals per-message controls on HOVER. If the
   control is in the DOM and merely hidden, ``querySelectorAll`` still finds it
   and the count is non-zero. If it is INJECTED on hover, it is genuinely absent
   until a pointer arrives. **Those two are distinguishable without hovering**,
   by counting how many matching elements are non-displayed, and that is the
   measurement this file exists to take.
3. Or the control is really not drawn on this conversation.

**AND THAT IS WHY THIS IS A READ AND NOT A HOVER.** The sibling probe reports
that ``readonly._MUTATION_CALL_PATTERNS`` HAS NO ``hover`` CLASS -- verified by
running the shipped scanner over a source that hovers twice and getting ``[]``.
So a hover would pass the boundary check while routing around its intent. This
file deliberately takes the reading that a static query CAN take, and leaves the
hover to whoever rules on whether it belongs in that tuple.

WHAT CROSSES THE BOUNDARY: integers. No label, no href, no text, in any branch.
Every selector is written in this file.

Run:  LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
      ./venv/Scripts/python.exe scripts/_probe_messaging_hidden_controls.py

Writes NOTHING. Sends NOTHING. Presses NOTHING. Hovers over NOTHING.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import FEED_URL, MESSAGING_URL  # noqa: E402

#: CASE-INSENSITIVE label probes. The ``i`` flag is the whole point of the file
#: for half of these: the sibling's zeros were taken case-sensitively.
#:
#: THE FIRST TWO ARE THE FIRING CONTROL. A logged-in messaging page draws
#: buttons and draws its own nav. If those read zero the reader is dead and
#: every other zero here is void.
_PROBES: tuple[tuple[str, str], ...] = (
    ("CONTROL button", "button"),
    ("CONTROL a[href]", "a[href]"),
    ("label ~ react (i)", '[aria-label*="react" i]'),
    ("label ~ reaction (i)", '[aria-label*="reaction" i]'),
    ("label ~ emoji (i)", '[aria-label*="emoji" i]'),
    ("label ~ option (i)", '[aria-label*="option" i]'),
    ("label ~ more (i)", '[aria-label*="more" i]'),
    ("label ~ menu (i)", '[aria-label*="menu" i]'),
    ("label ~ delete (i)", '[aria-label*="delete" i]'),
    ("label ~ archive (i)", '[aria-label*="archive" i]'),
    ("label ~ report (i)", '[aria-label*="report" i]'),
    ("label ~ request (i)", '[aria-label*="request" i]'),
    ("aria-haspopup any", "[aria-haspopup]"),
    ("role=menu", '[role="menu"]'),
    ("role=menuitem", '[role="menuitem"]'),
    ("aria-expanded any", "[aria-expanded]"),
    ("aria-expanded=false", '[aria-expanded="false"]'),
    ("aria-expanded=true", '[aria-expanded="true"]'),
    ("hidden=true", '[aria-hidden="true"]'),
)

#: Counts each selector twice: TOTAL, and how many of those are NOT DISPLAYED.
#: ``offsetParent === null`` is the cheap display test; it is true for
#: ``display:none`` and for detached nodes, and NOT true for something merely
#: transparent -- which is stated because it bounds what the number means.
_JS = """
(probes) => {
  const out = {};
  for (const [name, selector] of probes) {
    let nodes = [];
    try { nodes = Array.from(document.querySelectorAll(selector)); }
    catch (e) { out[name] = { total: -1, hidden: -1, failed: true }; continue; }
    let hidden = 0;
    for (const el of nodes) {
      const undisplayed = (el.offsetParent === null);
      const style = window.getComputedStyle(el);
      if (undisplayed || style.visibility === 'hidden' || style.opacity === '0') {
        hidden += 1;
      }
    }
    out[name] = { total: nodes.length, hidden: hidden, failed: false };
  }
  return out;
}
"""

_SPENT: list[int] = []


async def _read_both_badges(page):
    """Both nav badges, REDUCED TO TWO PAIRS OF SCALARS AT THE BOUNDARY.

    Copied from ``_read_both_badges`` in the predecessor probe, including the
    reason: the shaped badge dicts carry ``why``, ``saw`` and ``shaped_label``
    -- fields that can hold text LinkedIn wrote -- so a printer handed the whole
    dict can reach them, and a later edit adding one more ``.get`` would be a
    real leak no guard could see. Handing back scalars closes that in the
    SIGNATURE rather than in a habit.

    ``page.content()`` is a text call, so the markup taints the shaped reading
    and everything unpacked from it. Terminating that here, behind a function
    whose return type is four primitives, is what keeps it out of ``_run``.
    """
    markup = await page.content()
    messaging = shape.messaging_badge(markup)
    invitation = shape.invitation_badge(await dom.read_invitation_badge(page))
    return (
        (messaging.get("new_since_last_visit"), messaging.get("state")),
        (invitation.get("pending"), invitation.get("state")),
    )


async def _census(page) -> list[tuple[str, int, int, bool]]:
    """The whole census, REDUCED TO PRIMITIVES AT THE BOUNDARY.

    Returns one ``(label, total, undisplayed, failed)`` tuple per probe, where
    ``label`` is a string from ``_PROBES`` -- written in this file -- and the
    rest are an int, an int and a bool. **No printer downstream ever touches
    the evaluate result object.**

    **WHY THIS IS A SEPARATE FUNCTION RATHER THAN A LOOP IN ``_run``, and it is
    not to clear a red by renaming.** The first version evaluated and printed
    in one scope, and ``test_page_text_is_never_printed`` refused this file on
    two sites the moment the commit made it tracked. The mechanism is the one
    ``196394d`` and ``_read_both_badges`` already document in this package:
    **the taint engine tracks a name ACROSS THE WHOLE MODULE, not per scope,
    and it follows the BINDING rather than the meaning.** ``page.evaluate`` is
    a text call, so its result taints whatever it is bound to, and everything
    unpacked out of it one line later, all the way into the prints -- even
    though not one of those sites ever held a label, because the JavaScript
    returns nothing but integers and booleans.

    A rename would have been the laundering this repository has a scar for. The
    honest fix is to stop handing a printer a page-derived object at all, which
    is what the return type above does: it closes the door in the SIGNATURE, so
    a future edit that wanted to print a label would have to change the type
    and show up in a diff.

    Note that the guard is RIGHT to refuse the original shape even though
    nothing leaked. It cannot know what the JavaScript returns, and it exists
    because the operator's own slug reached a transcript three times. A
    structural guard firing on a file with nothing to hide is the guard
    working, not a false positive to be waived.
    """
    measured = await page.evaluate(_JS, [[n, s] for n, s in _PROBES])
    out: list[tuple[str, int, int, bool]] = []
    for label, _selector in _PROBES:
        entry = (measured or {}).get(label) or {}
        out.append((
            label,
            int(entry.get("total") if entry.get("total") is not None else -1),
            int(entry.get("hidden") if entry.get("hidden") is not None else -1),
            bool(entry.get("failed")),
        ))
    return out


async def _run(page) -> None:
    print("\n1. BEFORE THE SPEND -- both badges, off the feed")
    landed = await BROWSER.goto(page, FEED_URL)
    if "/login" in landed or "/checkpoint" in landed:
        print("    AUTH WALL. Nothing measured, nothing spent.")
        return

    msg_pair, inv_pair = await _read_both_badges(page)
    msg_count, msg_state = msg_pair
    inv_state = inv_pair[1]
    print("      messaging  new_since_last_visit=%r state=%r" % msg_pair)
    print("      invitation pending=%r state=%r" % inv_pair)

    if msg_state != "read" or inv_state != "read":
        print("    REFUSED. An unreadable badge is not a zero, and a load whose")
        print("    cost cannot be certified at both ends does not get taken.")
        return
    if msg_count:
        print("    REFUSED. Something arrived since his last visit, so the")
        print("    conversation LinkedIn redirects into may be UNREAD. Opening")
        print("    it marks a real person's message read. Nothing was spent.")
        return

    print("\n2. THE SPEND -- one navigation to config.MESSAGING_URL")
    _SPENT.append(1)
    arrived = await BROWSER.goto(page, MESSAGING_URL)
    print("    redirected into a conversation: %r"
          % ("/messaging/thread/" in arrived))

    surface = await dom.read_thread_reply_surface(page)
    print("    elements on the page: %r" % surface.get("elements"))
    print("    settle verdict:       %r" % surface.get("settle"))
    if surface.get("settle") == "unrendered":
        print("    STOP. The page did not render; every count below is about")
        print("    that and not about LinkedIn.")
        return

    print("\n3. TOTAL vs NOT-DISPLAYED, per selector")
    print("    %-24s %7s %7s" % ("selector", "total", "hidden"))
    readings = await _census(page)
    control_ok = True
    for label, total, undisplayed, failed in readings:
        flag = "  READER FAILED" if failed else ""
        if label.startswith("CONTROL") and not total:
            control_ok = False
        print("    %-24s %7r %7r%s" % (label, total, undisplayed, flag))

    print()
    if not control_ok:
        print("    THE CONTROL DID NOT FIRE. Every zero above is void.")
        return
    print("    HOW TO READ THIS, and it is the whole point of the file:")
    print("      total 0            -> the control is NOT IN THE DOM. Either")
    print("                            LinkedIn injects it on hover, or it is")
    print("                            not drawn on this conversation. A static")
    print("                            read cannot separate those two.")
    print("      total>0, hidden>0  -> it IS in the DOM and merely not shown,")
    print("                            so it is reachable by a read and the")
    print("                            sibling's case-sensitive zero was about")
    print("                            the QUERY rather than about LinkedIn.")


async def main() -> None:
    print("=" * 72)
    print("MESSAGING HIDDEN-CONTROL CENSUS -- absent, or merely invisible?")
    print("=" * 72)
    async with BROWSER.session() as page:
        try:
            await _run(page)
        finally:
            try:
                await page.close()
                print("\n    page closed: %r" % page.is_closed())
            except Exception as exc:  # noqa: BLE001
                print("\n    page close failed: %s" % type(exc).__name__)
            print("    /messaging/ loads taken this run: %d" % len(_SPENT))
            print("    presses: 0   hovers: 0   sends: 0   types: 0")


if __name__ == "__main__":
    asyncio.run(main())
