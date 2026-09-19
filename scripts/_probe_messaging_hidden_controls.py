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


async def _run(page) -> None:
    print("\n1. BEFORE THE SPEND -- both badges, off the feed")
    landed = await BROWSER.goto(page, FEED_URL)
    if "/login" in landed or "/checkpoint" in landed:
        print("    AUTH WALL. Nothing measured, nothing spent.")
        return

    markup = await page.content()
    messaging = shape.messaging_badge(markup)
    invitation = shape.invitation_badge(await dom.read_invitation_badge(page))
    msg_count = messaging.get("new_since_last_visit")
    msg_state = messaging.get("state")
    inv_state = invitation.get("state")
    print("      messaging  new_since_last_visit=%r state=%r"
          % (msg_count, msg_state))
    print("      invitation pending=%r state=%r"
          % (invitation.get("pending"), inv_state))

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
    counts = await page.evaluate(_JS, [[n, s] for n, s in _PROBES])
    control_ok = True
    for name, _selector in _PROBES:
        record = counts.get(name) or {}
        total = record.get("total")
        hidden = record.get("hidden")
        flag = "  READER FAILED" if record.get("failed") else ""
        if name.startswith("CONTROL") and not total:
            control_ok = False
        print("    %-24s %7r %7r%s" % (name, total, hidden, flag))

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
