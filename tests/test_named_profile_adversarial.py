"""The named-person gate against the pages the cold check built (2026-09-28).

WHAT WAS FOUND. A cold verification of the rebuilt reader built adversarial
pages from the two named-profile fixtures and pressed nothing -- it asked
Playwright, with a trial click, what the strict press WOULD reach. On the
reader of commit cee979c the gate passed, and the press would have reached a
control that is not the owner's, on these pages:

* a stranger's card drawn INSIDE the owner's topcard, with an unlabelled
  "Message" link of its own, the owner's visible link gone -- an unlabelled
  "Message" was taken for the owner's wherever it sat in the topcard;
* the same, named by ``aria-labelledby`` rather than ``aria-label``;
* the owner's control ``visibility:collapse`` and a stranger's in an open
  SHADOW ROOT inside the topcard -- the page's own ``visible()`` called the
  collapsed control visible, the page's ``querySelectorAll`` never entered the
  shadow root, and Playwright's engine, which the press uses, did the
  opposite of both;
* a same-name stranger's card inside the topcard with ITS Connect;
* a composer link on ANOTHER HOST -- the old destination token read the path
  of any host.

And on four more the gate and the press simply disagreed -- ``display:contents``,
``visibility:collapse``, ``content-visibility:hidden``, a closed ``<details>``
-- so a gate that passed was followed by a press that found nothing.

WHAT HOLDS IT NOW, and what this file asserts, page by page:

1. THE GATE COUNTS WHAT THE PRESS RESOLVES: for every page below, the visible
   count the reading returns equals the count of the press selector in
   Playwright's engine -- one engine answers both.
2. Every page that put a stranger's control within the press's reach is
   REFUSED -- the topcard must be one person's card (one heading, at most one
   member linked), a control inside a shadow root is not in the topcard, a
   composer link must name the topcard's own member, and must be on
   LinkedIn's own host.
3. And where the gate passes, the ONE element the press resolves is the
   owner's.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium, ``set_content``, and
a script of this file's run in the page to build each world.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom, named_profile
from tests.test_writes import browser_page  # noqa: F401 -- a fixture

REPO = Path(__file__).resolve().parent.parent
LIVE = (REPO / "tests" / "fixtures" / "synthetic" / "named_profile_live.html").read_text(encoding="ascii")
INVENTED = (REPO / "tests" / "fixtures" / "synthetic" / "named_profile.html").read_text(encoding="utf-8")

STRANGER_MEMBER = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000003"
STRANGER_COMPOSE = (
    "/messaging/compose/?profileUrn=urn%3Ali%3Afsd_profile%3A" + STRANGER_MEMBER
    + "&recipient=" + STRANGER_MEMBER
)

#: Marks the owner's controls, so a press can be asked whose control it
#: reached: the topcard's composer links (both rows) and its Connect.
_TAG_OWNER = """
() => {
  const card = document.querySelector('[id$="Topcard"]');
  for (const el of card.querySelectorAll('a[href*="/messaging/compose/"], button[aria-label$=" to connect"]')) {
    el.setAttribute('data-who', 'owner');
  }
}
"""

#: The owner's VISIBLE composer link in the topcard, for a world to edit.
_OWNER_VISIBLE = (
    """Array.from(document.querySelector('[id$="Topcard"]').querySelectorAll("""
    """'a[href*="/messaging/compose/"]')).find((a) => a.getBoundingClientRect().width > 0)"""
)

#: Each world: the fixture, and a script run in the page after it loads.
WORLDS = {
    "live as committed": (LIVE, "() => {}"),
    "a stranger's card nested in the topcard, its unlabelled Message, the owner's gone": (
        LIVE,
        "() => { const owner = " + _OWNER_VISIBLE + "; const card = document.createElement('div');"
        " card.innerHTML = '<h3>Morgan Example</h3><a data-who=\"stranger\" href=\"" + STRANGER_COMPOSE
        + "\"><span>Message</span></a>'; owner.replaceWith(card); }",
    ),
    "a stranger's unlabelled Message in the topcard, no card around it, the owner's gone": (
        LIVE,
        "() => { const owner = " + _OWNER_VISIBLE + "; const a = document.createElement('a');"
        " a.setAttribute('data-who', 'stranger'); a.setAttribute('href', '" + STRANGER_COMPOSE + "');"
        " a.innerHTML = '<span>Message</span>'; owner.replaceWith(a); }",
    ),
    "a stranger's Message named by aria-labelledby, the owner's gone": (
        LIVE,
        "() => { const owner = " + _OWNER_VISIBLE + "; const box = document.createElement('span');"
        " box.innerHTML = '<span id=\"lbl-stranger\" style=\"position:absolute;left:-9999px\">Message"
        " Morgan Example</span><a data-who=\"stranger\" aria-labelledby=\"lbl-stranger\" href=\""
        + STRANGER_COMPOSE + "\"><span>Message</span></a>'; owner.replaceWith(box); }",
    ),
    "the owner's Message collapsed, a stranger's labelled Message in a shadow root": (
        LIVE,
        "() => { const owner = " + _OWNER_VISIBLE + "; owner.style.visibility = 'collapse';"
        " const host = document.createElement('div'); owner.parentElement.appendChild(host);"
        " host.attachShadow({mode: 'open'}).innerHTML = '<a data-who=\"stranger\" aria-label=\"Message"
        " Morgan Example\" href=\"" + STRANGER_COMPOSE + "\">Message</a>'; }",
    ),
    "the owner's Message pointing at a composer path on another host": (
        LIVE,
        "() => { const owner = " + _OWNER_VISIBLE + "; owner.setAttribute('href',"
        " 'https://other-host.example/messaging/compose/?recipient=ACoAASYNTHETICSYNTHETICSYNTHETIC0000002');"
        " owner.setAttribute('data-who', 'elsewhere'); }",
    ),
    "the owner's Message display:contents": (
        LIVE, "() => { " + _OWNER_VISIBLE + ".style.display = 'contents'; }",
    ),
    "the owner's Message visibility:collapse": (
        LIVE, "() => { " + _OWNER_VISIBLE + ".style.visibility = 'collapse'; }",
    ),
    "the owner's Message in a content-visibility:hidden box": (
        LIVE,
        "() => { const owner = " + _OWNER_VISIBLE + "; const box = document.createElement('div');"
        " box.style.contentVisibility = 'hidden'; owner.replaceWith(box); box.appendChild(owner); }",
    ),
    "the owner's Message in a closed details": (
        LIVE,
        "() => { const owner = " + _OWNER_VISIBLE + "; const box = document.createElement('details');"
        " box.innerHTML = '<summary>x</summary>'; owner.replaceWith(box); box.appendChild(owner); }",
    ),
    "invented as committed": (INVENTED, "() => {}"),
    "the owner's Connect collapsed, a stranger's Connect in a shadow root": (
        INVENTED,
        "() => { const owner = document.getElementById('topcard-connect');"
        " owner.style.visibility = 'collapse'; const host = document.createElement('div');"
        " owner.parentElement.appendChild(host); host.attachShadow({mode: 'open'}).innerHTML ="
        " '<button type=\"button\" data-who=\"stranger\" aria-label=\"Invite Morgan Example to"
        " connect\">Connect</button>'; }",
    ),
    "a same-name stranger's card nested in the topcard with its Connect, the owner's gone": (
        INVENTED,
        "() => { const owner = document.getElementById('topcard-connect');"
        " const card = document.createElement('div'); card.innerHTML = '<h3>Casey Example</h3>"
        "<button type=\"button\" data-who=\"stranger\" aria-label=\"Invite Casey Example to connect\">"
        "Connect</button>'; owner.replaceWith(card); }",
    ),
}

#: The worlds whose press, on commit cee979c's reader, reached a control that
#: is not the owner's, or would have followed a link off LinkedIn.
MUST_REFUSE = {
    "a stranger's card nested in the topcard, its unlabelled Message, the owner's gone": "message",
    "a stranger's unlabelled Message in the topcard, no card around it, the owner's gone": "message",
    "a stranger's Message named by aria-labelledby, the owner's gone": "message",
    "the owner's Message collapsed, a stranger's labelled Message in a shadow root": "message",
    "the owner's Message pointing at a composer path on another host": "message",
    "the owner's Connect collapsed, a stranger's Connect in a shadow root": "invite",
    "a same-name stranger's card nested in the topcard with its Connect, the owner's gone": "invite",
}

_STATE = {"message": named_profile.message_state, "invite": named_profile.connect_state}
_PRESS = {"message": dom.topcard_message_control_selector, "invite": dom.topcard_invite_control_selector}
_DRAWN = {"message": named_profile.MESSAGE_FROM, "invite": named_profile.CONNECT_FROM}


async def _world(page, name):
    html, script = WORLDS[name]
    await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    await page.evaluate(_TAG_OWNER)
    await page.evaluate(script)
    return await dom.read_named_profile(page)


@pytest.mark.parametrize("name", sorted(WORLDS))
async def test_the_gate_counts_what_the_press_resolves(browser_page, name):
    """ONE ENGINE ANSWERS BOTH: the visible count the gate reads is the count
    of the selector the strict press is handed, for each kind."""
    reading = await _world(browser_page, name)
    assert reading["error"] is None, reading["error"]
    for kind in ("message", "invite"):
        pressed = await browser_page.locator(_PRESS[kind]()).count()
        assert reading[kind + "_visible_in_topcard"] == pressed, (kind, reading, pressed)


@pytest.mark.parametrize("name", sorted(MUST_REFUSE))
async def test_a_page_that_puts_a_strangers_control_in_reach_is_refused(browser_page, name):
    kind = MUST_REFUSE[name]
    reading = await _world(browser_page, name)
    state, why = _STATE[kind](reading)
    assert state == named_profile.UNKNOWN, (name, why)


@pytest.mark.parametrize("name", sorted(WORLDS))
async def test_where_the_gate_passes_the_press_reaches_the_owner_and_nothing_else(browser_page, name):
    reading = await _world(browser_page, name)
    for kind in ("message", "invite"):
        state, _why = _STATE[kind](reading)
        if state != _DRAWN[kind]:
            continue
        who = await browser_page.locator(_PRESS[kind]()).evaluate_all(
            "els => els.map((e) => e.getAttribute('data-who'))"
        )
        assert who == ["owner"], (name, kind, who)


async def test_the_committed_pages_still_pass(browser_page):
    """The controls: the live page's Message and the invented page's Connect
    and Message pass, so the refusals above are not a gate refusing
    everything."""
    live = await _world(browser_page, "live as committed")
    assert named_profile.message_state(live)[0] == named_profile.MESSAGE_FROM
    assert live["topcard_all_headings"] == 1 and live["topcard_members"] == 1
    assert live["topcard_member_id"] is True
    invented = await _world(browser_page, "invented as committed")
    assert named_profile.message_state(invented)[0] == named_profile.MESSAGE_FROM
    assert named_profile.connect_state(invented)[0] == named_profile.CONNECT_FROM
