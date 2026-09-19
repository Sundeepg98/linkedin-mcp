"""Close `P D25` -- press the add-a-section control and enumerate the menu.

THIS ROW WAS MOVED TO MEASURED-ABSENT THIS MORNING AND RETRACTED AN HOUR
LATER, by the wave that moved it. The needle came from LinkedIn's help article
(`a540837`, "Add profile section"); the page uses something else. Measured in
`_audit/_scratch/_probe-small-measures-followup-v2.txt`::

    a:has-text("Add section")                 3      three rendered links
    button:has-text("Add section")            0
    [aria-label*="Add section" i]             0
    [aria-label*="Add profile section" i]     0      the spelling that failed

So the control is on the page and the MENU CONTENTS are still unread. That is
the whole remaining gap, and this file is the read that closes it.

=============================================================================
THE HAZARD THIS FILE EXISTS TO HANDLE, AND IT IS NOT THE MENU
=============================================================================

**THE CONTROL IS AN ANCHOR, AND CLICKING AN ANCHOR CAN NAVIGATE.**

Every other navigation in this package goes through ``BROWSER.goto``, which
checks ``readonly.is_read_url`` first. **A click does not.** If those three
anchors carry a real href, pressing one moves the operator's own signed-in
browser to an address NOTHING CHECKED -- the read boundary bypassed, not by a
widened pattern, but by a route that never consults it.

So this file does NOT press first and look afterwards.

    1. READ what the three anchors ARE -- href RELATION (never the value),
       aria-haspopup, aria-expanded, aria-controls, role.
    2. DECIDE from that reading whether any of them is EVIDENCED as a
       disclosure control rather than a link to somewhere.
    3. PRESS ONLY THEN, and press only that one.

**A control that is not evidenced as a disclosure control is NOT PRESSED, and
the run reports that as its result.** An unpressed menu is a smaller loss than
an unchecked navigation on his live session.

This is the discriminator `_probe_match_details_control.py` established and it
is reused rather than reinvented: ARIA requires a control that expands a
region already in the document to say so -- ``aria-expanded``, and
``aria-controls`` naming the region. A link to something generated has
neither, because there is no region.

=============================================================================
CONTROLS
=============================================================================

**DETECTOR CONTROL on owned markup, runnable via ``--control`` BEFORE the CDP
gate**, so it can be shown failing without a browser. It aims the same
classifier at four anchors whose correct verdicts are known in both
directions: a fragment-href disclosure control, a real-path link, an
aria-haspopup control, and one that must be classified as NOT pressable.

**PAGE CONTROL on the live profile:** `edit`, `open_to`, `hiring` -- the top
card's own furniture, in the same region as the target.

=============================================================================
WHAT IS PRINTED
=============================================================================

**NO HREF VALUE, EVER.** Hrefs are reduced to a RELATION computed here --
fragment-only / same-path / in-product-path / off-product. A profile href
carries his member segment; printing one is the exact leak this repository
has a taint guard for.

**NO ACCESSIBLE NAME, EVER.** Not raw and not through ``census_shape`` --
that function is a STRUCTURAL shaper (urns, paths, possessives, digit runs)
plus a character gate, and a bare personal name passes it unchanged. That
mistake was made in this wave and put the operator's own name on stdout.
Menu items are reported as: a count, ``shape.describe_name_shaped`` structure
(name-free by construction), and BOOLEANS for which of the nineteen
help-article section names are present -- the nineteen are LinkedIn's product
vocabulary, carried as constants here, and a boolean about a constant reveals
nothing about him.

Run::

    ./venv/Scripts/python.exe scripts/_probe_add_section_menu.py --control
    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        ./venv/Scripts/python.exe scripts/_probe_add_section_menu.py

Writes NOTHING. Prints to stdout.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

PROFILE_URL = f"{BASE_URL}/in/me/"

#: LinkedIn's own product vocabulary for the nineteen sections `a540837`
#: lists. Constants, not readings. Presence of each is reported as a BOOLEAN.
HELP_ARTICLE_SECTIONS: tuple[str, ...] = (
    "About", "Education", "Position", "Services", "Career break", "Skills",
    "Featured", "Licenses and certifications", "Projects", "Courses",
    "Recommendations", "Volunteer experience", "Publications", "Patents",
    "Honors and awards", "Test scores", "Languages", "Organizations", "Causes",
)

PAGE_CONTROL_NEEDLES: tuple[str, ...] = ("Edit", "Open to", "Add")


def href_relation(href: str | None, page_url: str) -> str:
    """Reduce an href to a RELATION. The value is never returned.

    A profile href carries a member segment. This function is the only thing
    in this file that touches one, and nothing it returns contains any part
    of it.
    """
    if href is None:
        return "no-href-attribute"
    raw = href.strip()
    if raw == "":
        return "empty-href"
    if raw.startswith("javascript:"):
        return "javascript-href"
    if raw.startswith("#"):
        return "fragment-only"
    parsed = urlsplit(raw)
    here = urlsplit(page_url)
    if not parsed.netloc:
        if parsed.path in ("", here.path):
            return "same-path"
        return "in-product-path"
    if parsed.netloc == here.netloc:
        return "same-host-path"
    return "off-product"


#: EVERY VALUE ``href_relation`` CAN RETURN -- eight literals, every one of
#: them written in this file.
#:
#: THE ANCHOR LINE BELOW PRINTS THE ONE THAT MATCHES RATHER THAN PRINTING
#: ``rel``, and that is what clears the output guard without a declaration.
#: ``rel`` is navigation-derived -- ``here`` is a ``goto`` return -- so the
#: engine taints it correctly and a print of it is a true positive. Comparing
#: it against this tuple emits a token THIS FILE OWNS: even a bug in
#: ``href_relation`` that let a raw href through would render as
#: ``UNKNOWN-RELATION`` here rather than leaking it. That is strictly stronger
#: than trusting the function, which is the point -- see the note on the
#: anchor print.
#:
#: A NINTH RELATION ADDED WITHOUT ADDING IT HERE FAILS LOUD AND LEAKS NOTHING:
#: the line prints ``UNKNOWN-RELATION``. The control below asserts the classes
#: it exercises are all present, which is four of the eight; the other four are
#: covered by that fallback rather than by a claim.
RELATIONS: tuple[str, ...] = (
    "no-href-attribute", "empty-href", "javascript-href", "fragment-only",
    "same-path", "in-product-path", "same-host-path", "off-product",
)


def is_disclosure_control(rel: str, haspopup: str | None,
                          expanded: str | None) -> bool:
    """Evidenced as opening something already here, rather than going away.

    DELIBERATELY CONSERVATIVE. An href that goes anywhere disqualifies the
    control no matter what ARIA says, because the cost of being wrong is a
    navigation nothing checked on his live session, and the cost of being
    over-cautious is an unpressed menu.
    """
    goes_nowhere = rel in ("fragment-only", "empty-href", "no-href-attribute",
                           "javascript-href", "same-path")
    says_it_opens = bool(haspopup) or expanded in ("true", "false")
    return goes_nowhere and says_it_opens


# --------------------------------------------------------------------------
# DETECTOR CONTROL -- four cases, correct answers known in both directions
# --------------------------------------------------------------------------

CONTROL_CASES: tuple[tuple[str, str | None, str | None, str | None, str,
                           bool], ...] = (
    # label,            href,               haspopup, expanded, rel, press?
    ("fragment + popup", "#",               "true",  "false", "fragment-only",
     True),
    ("real path + popup", "/in/someone/",   "true",  "false", "in-product-path",
     False),
    ("fragment, no aria", "#",              None,    None,    "fragment-only",
     False),
    ("no href + popup",  None,              "menu",  None,    "no-href-attribute",
     True),
    ("off-product",      "https://example.com/x", "true", "false", "off-product",
     False),
)


async def run_detector_control() -> bool:
    print("=" * 70)
    print("DETECTOR CONTROL -- classifier aimed at known answers, both ways")
    print("=" * 70)
    ok = True
    page_url = f"{BASE_URL}/in/me/"
    for label, href, haspopup, expanded, want_rel, want_press in CONTROL_CASES:
        got_rel = href_relation(href, page_url)
        got_press = is_disclosure_control(got_rel, haspopup, expanded)
        rel_ok = got_rel == want_rel
        press_ok = got_press == want_press
        if not (rel_ok and press_ok):
            ok = False
        print(f"  {label:20s} rel={got_rel:20s} "
              f"{'PASS' if rel_ok else 'FAIL'}   "
              f"press={str(got_press):5s} want={str(want_press):5s} "
              f"{'PASS' if press_ok else 'FAIL'}")
    # AND THE ALPHABET IS CHECKED, because the anchor print now renders a
    # relation by matching against RELATIONS: a class that classifier can
    # return and this tuple does not name would print as UNKNOWN-RELATION and
    # teach a reader nothing.
    unnamed = sorted(
        {want for _l, _h, _hp, _ex, want, _w in CONTROL_CASES}
        - set(RELATIONS)
    )
    print()
    print(f"  every control relation is named in RELATIONS: "
          f"{'PASS' if not unnamed else 'FAIL -- ' + str(unnamed)}")
    if unnamed:
        ok = False

    # A classifier that says PRESS to everything is the failure that matters.
    presses = sum(
        1 for _l, h, hp, ex, _r, _w in CONTROL_CASES
        if is_disclosure_control(href_relation(h, page_url), hp, ex)
    )
    says_no = presses < len(CONTROL_CASES)
    print(f"\n  it refuses at least one case: {presses} of "
          f"{len(CONTROL_CASES)} pressable -- "
          f"{'PASS' if says_no else 'FAIL -- a gate that never refuses is not a gate'}")
    if not says_no:
        ok = False
    print(f"\n  DETECTOR USABLE: {ok}")
    return ok


async def main() -> int:
    if "--control" in sys.argv:
        return 0 if await run_detector_control() else 1

    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print(f"    Re-run with LINKEDIN_CDP_ATTACH=1 "
              f"LINKEDIN_CDP_PORT={config.CDP_PORT}")
        return 2
    if not await run_detector_control():
        print("\nDETECTOR BROKEN. Nothing live is loaded.")
        return 1
    if not readonly.is_read_url(PROFILE_URL):
        print("REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return 2

    page = None
    try:
        async with BROWSER.session() as opened:
            page = opened
            landed = await BROWSER.goto(page, PROFILE_URL)
            if "/login" in str(landed) or "/checkpoint" in str(landed):
                print("AUTH WALL. Nothing here is a reading.")
                return 1
            try:
                await page.wait_for_load_state("networkidle", timeout=15_000)
            except Exception as error:  # noqa: BLE001
                print(f"settle wait did not complete: {type(error).__name__}")

            html = await page.content()
            main_text = ""
            try:
                main_text = await page.inner_text("main")
            except Exception:  # noqa: BLE001
                pass
            print("\n    PAGE CONTROL -- must be non-zero:")
            page_ok = False
            for needle in PAGE_CONTROL_NEEDLES:
                count = main_text.count(needle)
                if count:
                    page_ok = True
                print(f"      {needle:12s} main={count:4d}  "
                      f"html={html.count(needle):5d}")
            print(f"      PAGE CONTROL: {'PASS' if page_ok else 'FAIL'}")
            if not page_ok:
                print("      SUSPECT -- nothing below is a reading.")
                return 1

            here = str(landed)
            anchors = page.locator('a:has-text("Add section")')
            total = await anchors.count()
            print(f"\n    anchors matching 'Add section': {total}")
            print("    NO HREF VALUE AND NO NAME IS PRINTED -- relation only.\n")

            candidate = None
            for index in range(total):
                node = anchors.nth(index)
                try:
                    href = await node.get_attribute("href")
                except Exception:  # noqa: BLE001
                    href = None
                haspopup = expanded = controls = role = None
                for attr, target in (("aria-haspopup", "haspopup"),
                                     ("aria-expanded", "expanded"),
                                     ("aria-controls", "controls"),
                                     ("role", "role")):
                    try:
                        value = await node.get_attribute(attr)
                    except Exception:  # noqa: BLE001
                        value = None
                    if target == "haspopup":
                        haspopup = value
                    elif target == "expanded":
                        expanded = value
                    elif target == "controls":
                        controls = value
                    else:
                        role = value
                rel = href_relation(href, here)
                pressable = is_disclosure_control(rel, haspopup, expanded)
                # THE RELATION IS MATCHED, NOT PRINTED, and the verdict is
                # printed as a comparison. Both are the output guard's own
                # sanctioned shapes, and neither adds an entry to
                # KNOWN_TAINTED_OUTPUT.
                #
                # ``href_relation`` does return a closed alphabet and its
                # docstring says so. IT IS STILL NOT TRUSTED BY NAME, because
                # the sibling probe already paid for that: while its own
                # classifier wore the name ``_relation`` the engine trusted the
                # call BY SPELLING and stopped examining everything downstream
                # of it. A guard silenced by a name does not merely stop
                # checking that function.
                #
                # ``rel`` and ``pressable`` STAY TAINTED deliberately. The fix
                # is at the sink, not at the binding, so a future print of
                # either one goes red again instead of inheriting this
                # exemption.
                shown = "/".join(
                    name for name in RELATIONS if rel == name
                ) or "UNKNOWN-RELATION"
                print(f"      anchor {index}: rel={shown:20s} "
                      f"haspopup={str(haspopup):6s} expanded={str(expanded):6s} "
                      f"controls={'yes' if controls else 'no':3s} "
                      f"role={str(role):8s} "
                      f"EVIDENCED-DISCLOSURE={pressable is True}")
                # WOULD THE BOUNDARY ADMIT IT? A BOOLEAN ABOUT THE ADDRESS,
                # NEVER THE ADDRESS. This turns "somebody should check the
                # href" into an answer, and it is the only question that
                # decides whether the supported route -- read the address,
                # put it through the boundary, THEN goto -- is even open.
                if href:
                    target = urljoin(here, href.strip())
                    admitted = readonly.is_read_url(target)
                    depth = len(
                        [s for s in urlsplit(target).path.split("/") if s]
                    )
                    # Which forbidden CLASS it trips, by name of the class and
                    # never by the matched text.
                    trips = [
                        token for token in ("/edit/", "/add", "/new",
                                            "/create", "/delete", "/psettings",
                                            "/settings")
                        if token in target
                    ]
                    # A COMPARISON, for the same reason and with the same
                    # restraint: ``is_read_url`` returns a literal True/False,
                    # so this prints the identical text it printed before. The
                    # engine flagged it because it tracks the NAME ``admitted``
                    # and cannot see what the call returns -- which is the
                    # engine being right, not over-strict, since the name is
                    # bound from a tainted ``target``.
                    print(f"                 boundary: "
                          f"is_read_url={admitted is True}  "
                          f"path_depth={depth}  "
                          f"forbidden_tokens_present={trips}")
                if pressable and candidate is None:
                    candidate = node

            if candidate is None:
                print("\n    NOT PRESSED, AND THIS IS THE RESULT RATHER THAN A")
                print("    FAILURE. None of those anchors is evidenced as a")
                print("    disclosure control: each would NAVIGATE, and a click")
                print("    does not consult readonly.is_read_url the way")
                print("    BROWSER.goto does. Pressing one would move his live")
                print("    session to an address nothing checked.")
                print("    NEXT ARTIFACT: a ruling on whether a click-driven")
                print("    navigation may be taken at all, or a goto to the")
                print("    href's own address once that address is read off")
                print("    the page and put through the boundary FIRST --")
                print("    which is the shape every other nav in this package")
                print("    already uses.")
                return 0

            async def structure(when: str) -> None:
                print(f"    {when:7s} "
                      f"menus={await page.locator('[role=\"menu\"]').count()}  "
                      f"items={await page.locator('[role=\"menuitem\"]').count()}  "
                      f"dialogs={await page.locator('[role=\"dialog\"]').count()}")

            print("\n    ABSOLUTE COUNTS on both sides of the press:")
            await structure("BEFORE")
            await candidate.click(timeout=8_000)
            await page.wait_for_timeout(1_500)
            await structure("AFTER")

            items = page.locator('[role="menuitem"], [role="dialog"] li')
            count = await items.count()
            print(f"\n    menu items found: {count}")
            for index in range(min(count, 40)):
                label = ""
                try:
                    label = (await items.nth(index).inner_text(
                        timeout=2_000) or "").strip()
                except Exception:  # noqa: BLE001
                    label = ""
                described = shape.describe_name_shaped(label)
                tail = described.get("tail")
                print(f"      item {index:2d}: len={len(label):3d} "
                      f"runs={described.get('runs')} "
                      f"tail={'<no-run>' if tail is None else repr(tail)}")

            opened_text = await page.inner_text("body")
            print("\n    WHICH OF THE NINETEEN HELP-ARTICLE SECTIONS ARE DRAWN")
            print("    (booleans about LinkedIn's own product vocabulary):")
            present = 0
            for section in HELP_ARTICLE_SECTIONS:
                hit = section in opened_text
                if hit:
                    present += 1
                print(f"      {section:30s} {hit}")
            print(f"\n    {present} of {len(HELP_ARTICLE_SECTIONS)} present")

            try:
                await page.keyboard.press("Escape")
                print("    Escape pressed.")
            except Exception as error:  # noqa: BLE001
                print(f"    Escape failed: {type(error).__name__}")
    finally:
        if page is not None:
            try:
                await page.close()
                print("\n    page closed.")
            except Exception as error:  # noqa: BLE001
                print(f"\n    page close failed: {type(error).__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
