"""The one reader that publishes a real identifier, and what buys it the right.

``linkedin_surface_census`` substitutes every ``urn:li:...`` out before it
counts -- that is what makes it safe to point at a page made of other members,
and it is also why nothing in this package could AIM. ``linkedin_my_activity_items``
publishes item urns, from ONE page, after establishing per call that the items
are the operator's own. This file is where that difference is held to being
exactly as narrow as it claims.

WHAT THIS FILE IS ORGANISED AROUND. Every check below is shown FAILING under a
named mutation of the code it guards, and the mutations are recorded in
``_audit/_slice-activity-items.md`` with the assertion text each one produced. A
reader that publishes identifiers, certified by checks nobody demonstrated
failing, would be the worst possible thing in this repository to take on trust.

The eleven requirements this file answers, in the order they appear:

* A1  a rail with TWO authors publishes NOTHING, and the other member's urn is
      in no part of the answer. THE ONE THAT MATTERS.
* A2  an all-his rail yields exactly his urns, deduped.
* A3  no ``isSelfProfile=true`` -- refuse, and read nothing else at all.
* A4  an ``h1`` naming somebody else -- refuse. C1 and C2 both hold here and
      only C3 catches it.
* A5  no ``h1`` -- refuse. A5b: two of them -- refuse rather than take the first.
* A6  zero overflow controls -- refuse. An empty rail is not an authorship claim.
* A7  the prefix rule, in both directions, and the case it must still reject.
* A8  a permalink whose segment is not urn-shaped is counted, never emitted.
* A9  a urn paired to no item root with an overflow control is counted, never
      emitted.
* A10 no author string, ``h1`` text or member segment anywhere in the answer, on
      the success path AND on every refusal path.
* A11 ``item_root_source`` reports which route found each item root, and the
      route's own attribute VALUE is never what gets published.

Structural guards follow them: the third copy of the name chain is held to
agreeing with the census's, the injected script is scanned a second time, the
measured strings are pinned to what the census read, the refusal codes are
shown to be the enumeration they claim to be, and the deliberate absence of
shaping on the urns is pinned against ``shape.census_substitute``.

EVERY IDENTIFIER-SHAPED LITERAL HERE IS INVENTED and is drawn from the families
``tests/test_no_committed_identity.py`` already sanctions in ``SYNTHETIC_IDS``
and ``SYNTHETIC_SLUGS``, so this file needs no entry in ``DECLARED_PLANTS`` --
which is the right outcome: a declared plant is a hole in that guard for the
whole file, and it should be earned, not spent on fixtures that had a
sanctioned form available.

Nothing here reaches LinkedIn or an account. It launches a LOCAL headless
Chromium over invented markup, because containment lives in the injected script
and only a laid-out document can answer what it asks -- ``closest()``,
``parentElement`` and ``innerText`` are browser behaviour, and a fake page
cannot stand in for any of them.
"""

from __future__ import annotations

import inspect
import json
from contextlib import asynccontextmanager
from typing import Any

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import dom, readonly, shape
from linkedin_server.server import (
    CENSUS_SURFACES,
    SELF_PROFILE_URL,
    linkedin_my_activity_items,
)
from tests.test_surface_census import ACTIVITY_ID, MEMBER_SLUG

ACTIVITY_VIEWPORT = {"width": 1280, "height": 720}

#: The landed url shape MEASURED on 2026-08-31: ``/in/me/`` lands slugged, with
#: LinkedIn's own self-assertion riding behind it. Built from the slug
#: ``tests/test_surface_census.py`` already commits so this file adds no new
#: invented identity of its own.
LANDED_PROFILE = f"https://www.linkedin.com/in/{MEMBER_SLUG}/?isSelfProfile=true"

#: The same landing with LinkedIn's assertion missing, and identical in every
#: other respect, so A3 isolates the one thing it is about.
LANDED_NO_ASSERTION = f"https://www.linkedin.com/in/{MEMBER_SLUG}/"

#: Invented item urns. The digits are drawn from the ``SYNTHETIC_IDS`` family
#: ``tests/test_no_committed_identity.py`` sanctions -- the same nineteen-digit
#: 74/749 shapes already committed in ``tests/fixtures/notifications.html`` and
#: ``tests/test_sdui_surfaces_fixture.py`` -- so the identifier sweep passes
#: over this file without an allowlist entry.
HIS_ITEM_ONE = "urn:li:activity:" + ACTIVITY_ID
HIS_ITEM_TWO = "urn:li:activity:7400000000000000002"
OTHER_ITEM = "urn:li:activity:7400000000000000003"
STRAY_ITEM = "urn:li:activity:7490000000000000001"

#: A permalink segment that is not urn-shaped at all.
NON_URN_SEGMENT = "not-a-urn-at-all"

#: THE REALISTIC NEAR MISS, and the one this design deliberately refuses. The
#: measured ``href_shape`` on his profile was the LITERAL urn spelling; the
#: percent-encoded form has never been observed in this position, and a shape
#: nobody has seen is not a shape to admit. It is counted ``unrecognised``,
#: exactly like the junk above, and A8 asserts both.
ENCODED_SEGMENT = "urn%3Ali%3Aactivity%3A" + ACTIVITY_ID

#: THE NAMES. Invented, obviously so, and chosen to make the prefix rule's
#: three cases visible: LinkedIn writes a SHORTENED form into the overflow
#: label while the ``h1`` carries the full one, which is the measured asymmetry
#: the rule exists for.
AUTHOR_SHORT = "Ada L"
OWNER_FULL = "Ada Lovelace"
OTHER_AUTHOR = "Grace Hopper"
NEAR_MISS_AUTHOR = "Adam Lovelace"

#: Built from the constants under test rather than retyped, so a fixture cannot
#: drift from the reader. That would be circular on its own -- if the constant
#: changed, every fixture would follow and every test would still pass -- so
#: ``test_the_measured_strings_are_the_ones_the_census_read`` pins the two
#: constants to the literals the census actually read, and that test is what
#: anchors all of this.
OVERFLOW_PREFIX = dom.ACTIVITY_OVERFLOW_PREFIX
PERMALINK_BASE = "https://www.linkedin.com" + dom.ACTIVITY_PERMALINK_MARKER


# ---------------------------------------------------------------------------
# Invented markup. NOT in tests/fixtures/, for the reason the editor slice's
# markup is not: nothing here was ever served by LinkedIn, and invented markup
# filed beside real captures is how invented markup starts being read as
# evidence.
# ---------------------------------------------------------------------------


def overflow(author: str) -> str:
    """One item overflow control, in the shape the census measured it.

    ``button``, ``aria-label``, ``aria-expanded="false"`` -- count 8 on his own
    profile and count 8 on the feed, 2026-08-31.
    """
    return (
        f'<button aria-label="{OVERFLOW_PREFIX}{author}" '
        'aria-expanded="false"></button>'
    )


def permalink(urn: str, text: str) -> str:
    """One item permalink, in the ``href_shape`` the census measured."""
    return f'<a href="{PERMALINK_BASE}{urn}/">{text}</a>'


def item(author: str, urn: str, *, root_attr: str = "", extra: str = "") -> str:
    """One activity-rail item: the overflow control, the reaction control, the
    permalink and the repost control -- the four shapes the census counted at 8
    apiece on his profile."""
    return (
        f'<div class="item"{root_attr}>'
        + overflow(author)
        + '<button aria-label="Reaction button state: no reaction"></button>'
        + permalink(urn, "Comment")
        + extra
        + "<button>Repost</button>"
        + "</div>"
    )


def page(*, heading: str, rail: str, loose: str = "") -> str:
    """A rail inside ``main``, with anything ``loose`` OUTSIDE it.

    THE ``main`` WRAPPER IS LOAD-BEARING for A9. A stray permalink placed
    directly in ``body`` beside the items would climb one hop to ``body`` --
    which contains every overflow control on the page -- and a reader without
    the document-level stop would happily pair it there. Putting the rail in
    ``main`` and the stray outside it means the stray's ONLY overflow-bearing
    ancestor is ``body``, which is exactly the case the stop exists for.
    """
    return (
        "<!doctype html><html><body>"
        + heading
        + "<main>"
        + rail
        + "</main>"
        + loose
        + "</body></html>"
    )


H1_OWNER = f"<h1>{OWNER_FULL}</h1>"

#: TWO items, THREE permalink anchors. The second anchor on item one is the
#: timestamp permalink LinkedIn draws beside the Comment link, and it is here so
#: A2 tests DEDUPING rather than merely counting -- a reader that returned one
#: entry per anchor would pass a fixture where every urn appeared once.
HIS_RAIL_HTML = page(
    heading=H1_OWNER,
    rail=(
        item(
            AUTHOR_SHORT,
            HIS_ITEM_ONE,
            extra=permalink(HIS_ITEM_ONE, "2w"),
        )
        + item(AUTHOR_SHORT, HIS_ITEM_TWO)
    ),
)

#: A1's fixture. ONE item his, ONE another member's, each with its own urn --
#: which is what an activity rail really carries, because a reshare and a
#: colleague's item both render there. Plus a STRAY permalink outside the rail,
#: which is what makes the second A1 mutation visible: with unanimity intact the
#: refusal hides the urns, and ``counts.unpaired`` is the field that still says
#: the pairing rule ran.
#:
#: HIS ITEM IS FIRST ON PURPOSE. The first A1 mutation relaxes unanimity to "at
#: least one author", which then takes ``distinct[0]`` as the sole author -- and
#: if the other member's item were first, that mutation would fail C3 by
#: accident and the test would go green for the wrong reason.
MIXED_RAIL_HTML = page(
    heading=H1_OWNER,
    rail=item(AUTHOR_SHORT, HIS_ITEM_ONE) + item(OTHER_AUTHOR, OTHER_ITEM),
    loose=f'<footer>{permalink(STRAY_ITEM, "Show all posts")}</footer>',
)

#: A9's fixture: all his, plus the same stray outside the rail.
HIS_RAIL_WITH_STRAY_HTML = page(
    heading=H1_OWNER,
    rail=(
        item(AUTHOR_SHORT, HIS_ITEM_ONE, extra=permalink(HIS_ITEM_ONE, "2w"))
        + item(AUTHOR_SHORT, HIS_ITEM_TWO)
    ),
    loose=f'<footer>{permalink(STRAY_ITEM, "Show all posts")}</footer>',
)

#: A8's fixture: all his, with two permalinks whose segments are not urn-shaped
#: sitting INSIDE item one -- so the shape check is the only thing keeping them
#: out. A junk anchor placed outside a rooted item would be rejected by the
#: pairing rule instead and A8 would be testing A9.
HIS_RAIL_WITH_JUNK_HTML = page(
    heading=H1_OWNER,
    rail=(
        item(
            AUTHOR_SHORT,
            HIS_ITEM_ONE,
            extra=(
                permalink(HIS_ITEM_ONE, "2w")
                + permalink(NON_URN_SEGMENT, "junk")
                + permalink(ENCODED_SEGMENT, "encoded")
            ),
        )
        + item(AUTHOR_SHORT, HIS_ITEM_TWO)
    ),
)

#: A11's fixtures. THE ``data-urn`` VALUES ARE SWAPPED against the hrefs, which
#: is what makes the "the attribute is a MARKER, its value is never read" claim
#: testable: a reader that published the attribute would return the two urns in
#: the other order, which is a different list rather than an unfalsifiable
#: coincidence.
DATA_URN_RAIL_HTML = page(
    heading=H1_OWNER,
    rail=(
        item(
            AUTHOR_SHORT,
            HIS_ITEM_ONE,
            root_attr=f' data-urn="{HIS_ITEM_TWO}"',
            extra=permalink(HIS_ITEM_ONE, "2w"),
        )
        + item(
            AUTHOR_SHORT, HIS_ITEM_TWO, root_attr=f' data-urn="{HIS_ITEM_ONE}"'
        )
    ),
)

DATA_ID_RAIL_HTML = page(
    heading=H1_OWNER,
    rail=(
        item(
            AUTHOR_SHORT,
            HIS_ITEM_ONE,
            root_attr=' data-id="item-one"',
            extra=permalink(HIS_ITEM_ONE, "2w"),
        )
        + item(AUTHOR_SHORT, HIS_ITEM_TWO, root_attr=' data-id="item-two"')
    ),
)

#: A4: C1 and C2 both hold, and only C3 catches it.
WRONG_OWNER_HTML = HIS_RAIL_HTML.replace(H1_OWNER, f"<h1>{OTHER_AUTHOR}</h1>")

#: A5: no heading at all.
NO_HEADING_HTML = HIS_RAIL_HTML.replace(H1_OWNER, "")

#: A5b: two headings, THE FIRST OF WHICH IS HIS. A fixture whose second heading
#: was his would let a take-the-first implementation refuse by accident, and the
#: check would certify nothing.
TWO_HEADING_HTML = HIS_RAIL_HTML.replace(
    H1_OWNER, H1_OWNER + f"<h1>{OTHER_AUTHOR}</h1>"
)

#: A6: permalinks and a heading, and not one control naming an author. The rail
#: LinkedIn draws for a member who has posted nothing has no overflow controls
#: in it either, so "absent" here is the realistic shape and not a contrivance.
EMPTY_RAIL_HTML = page(
    heading=H1_OWNER,
    rail=(
        '<div class="item">'
        + permalink(HIS_ITEM_ONE, "Comment")
        + "</div>"
        + '<div class="item">'
        + permalink(HIS_ITEM_TWO, "Comment")
        + "</div>"
    ),
)


def prefix_case(author: str, heading: str) -> str:
    """One item, one heading, and nothing else to get in the way. A7's fixture
    family, built rather than listed so the three rows differ in exactly the two
    strings the rule compares."""
    return page(
        heading=f"<h1>{heading}</h1>",
        rail=item(author, HIS_ITEM_ONE),
    )


# ---------------------------------------------------------------------------
# The harness
# ---------------------------------------------------------------------------


@pytest.fixture
async def run_tool(monkeypatch):
    """Drive the real tool over frozen markup. One browser, a context per read.

    ``window.innerWidth`` is asserted on EVERY measurement, not once at setup.
    Containment does not depend on layout but ``innerText`` does -- the ``h1``
    text this reader compares IS rendered text -- so a reading taken at an
    unrecorded width is a reading whose conditions were not recorded.

    IT RECORDS WHICH SCRIPTS THE TOOL RAN, through a proxy in front of the
    page. A3 has to certify that a failed C1 reads NOTHING, and "the answer
    carried no counts" is weaker than that: it would also hold for a reader that
    injected the script and threw the result away. The proxy sees the injection
    itself. The harness's own ``window.innerWidth`` measurement goes to the real
    page and is deliberately not recorded, so the list holds only what the tool
    under test executed.

    THE TOOL IS DRIVEN, NOT THE READER. Every requirement here is about what a
    CALLER receives -- the refusals, the absent ``items`` key, the navigation
    count, the absence of every name. Testing ``dom.read_own_activity_items``
    directly would answer none of those, because C1 lives in the tool and the
    reader deliberately cannot see a url's query string.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        async def _run(
            html: str, *, landed: str = LANDED_PROFILE
        ) -> tuple[dict[str, Any], list[str], list[str]]:
            context = await browser.new_context(
                viewport=dict(ACTIVITY_VIEWPORT)
            )
            navigations: list[str] = []
            scripts: list[str] = []
            try:
                page_obj = await context.new_page()

                async def render(markup: str) -> None:
                    await page_obj.set_content(
                        markup, wait_until="domcontentloaded", timeout=60_000
                    )
                    width = await page_obj.evaluate("window.innerWidth")
                    assert width == ACTIVITY_VIEWPORT["width"], (
                        f"the page laid out at {width}px, not "
                        f"{ACTIVITY_VIEWPORT['width']}px. Every reading below "
                        "came off a document whose conditions were not "
                        "recorded."
                    )

                class Recorder:
                    """Forwards to the page and records what was injected."""

                    def __init__(self, inner):
                        self._inner = inner

                    @property
                    def url(self):
                        return self._inner.url

                    async def evaluate(self, script, *args, **kwargs):
                        scripts.append(script)
                        return await self._inner.evaluate(
                            script, *args, **kwargs
                        )

                recorder = Recorder(page_obj)

                @asynccontextmanager
                async def fake_session():
                    yield recorder

                async def fake_goto(target_page, url, **kwargs):
                    navigations.append(url)
                    await render(html)
                    return landed

                monkeypatch.setattr(
                    browser_module.BROWSER, "session", fake_session
                )
                monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
                return await linkedin_my_activity_items(), navigations, scripts
            finally:
                await context.close()

        try:
            yield _run
        finally:
            await browser.close()


#: ``.get("refused")`` rather than ``result["refused"]`` in every refusal check
#: below, and that is about the FAILURE TEXT rather than about strictness. A
#: subscript on a result that stopped refusing raises ``KeyError: 'refused'``,
#: which says nothing about what the tool returned instead; ``.get`` with the
#: whole result as the assertion message prints the answer a caller would have
#: received. Each is paired with an assertion that ``"items"`` is absent, which
#: is the half that would actually be dangerous.
def serialised(result: dict[str, Any]) -> str:
    """The whole answer as one string, which is how a leak is hunted here.

    Field-by-field assertions would miss a value that arrived in a key, in a
    nested reason, or in a field nobody thought to name -- and this reader's
    whole permission rests on which strings do and do not cross the boundary.
    """
    return json.dumps(result, sort_keys=True)


# ---------------------------------------------------------------------------
# A1. THE ONE THAT MATTERS
# ---------------------------------------------------------------------------


async def test_a_rail_with_two_authors_publishes_no_item_key_at_all(run_tool):
    """AN ACTIVITY RAIL CARRIES OTHER PEOPLE'S ITEMS. That is the whole reason
    this tool establishes authorship instead of trusting the address it was
    pointed at, and it is the measured shape of ``/feed/``: eight overflow
    controls carrying EIGHT DIFFERENT author strings, where the same eight on
    his profile carried ONE.

    THREE THINGS ARE ASSERTED AND THEY FAIL UNDER DIFFERENT MUTATIONS, which is
    why they are in one test rather than three:

    * no ``items`` key -- fails if unanimity stops being required;
    * no urn ANYWHERE in the serialised answer, his included -- fails the same
      way, and catches a urn arriving in a key or a reason rather than in the
      list;
    * ``counts.unpaired`` is still 1 -- fails if the pairing rule stops
      requiring an overflow control, which the refusal above would otherwise
      hide completely.
    """
    result, _navigations, _scripts = await run_tool(MIXED_RAIL_HTML)

    assert result.get("refused") == "mixed_authors", result
    assert "items" not in result, sorted(result)
    assert "anchors_per_item" not in result, sorted(result)

    rendered = serialised(result)
    for urn in (OTHER_ITEM, HIS_ITEM_ONE, STRAY_ITEM):
        assert urn not in rendered, (urn, rendered)

    assert result["authorship"]["established"] is False
    assert result["authorship"]["self_assertion_present"] is True
    assert result["authorship"]["unanimous"] is False
    assert result["authorship"]["authors_found"] == 2
    # NOT COMPARED, and not False: there was no single author to compare.
    assert result["authorship"]["matches_page_owner"] is None

    assert result["counts"]["overflow_controls"] == 2
    assert result["counts"]["permalink_anchors"] == 3
    assert result["counts"]["distinct_urns"] == 2
    assert result["counts"]["unpaired"] == 1, result["counts"]


def test_the_mixed_rail_really_carries_two_authors_and_three_urns():
    """THE CONTROL for A1. Without it the assertions above would pass just as
    well against markup that had nothing to refuse -- and a check that cannot
    fail certifies nothing.

    Four properties of the fixture are asserted, not assumed: both author
    strings are in it, all three urns are in it, and his item is FIRST, which is
    what makes the first A1 mutation land where it is supposed to.
    """
    assert OVERFLOW_PREFIX + AUTHOR_SHORT in MIXED_RAIL_HTML
    assert OVERFLOW_PREFIX + OTHER_AUTHOR in MIXED_RAIL_HTML
    for urn in (HIS_ITEM_ONE, OTHER_ITEM, STRAY_ITEM):
        assert urn in MIXED_RAIL_HTML, urn
    assert MIXED_RAIL_HTML.index(AUTHOR_SHORT) < MIXED_RAIL_HTML.index(
        OTHER_AUTHOR
    ), "his item must be first, or the unanimity mutation cannot land"


# ---------------------------------------------------------------------------
# A2. An all-his rail
# ---------------------------------------------------------------------------


async def test_an_all_his_rail_yields_exactly_his_item_keys_deduped(run_tool):
    """THE POSITIVE CASE, asserted as an EXACT list rather than by membership.

    A membership check would pass against a reader that also returned three
    other things, and the whole question here is which urns come out. The
    counts are asserted as a whole dict for the same reason: a reader that
    quietly stopped counting something would otherwise go unnoticed.

    ``anchors_per_item`` is what makes this a dedupe test. Item one carries TWO
    anchors -- the Comment link and the timestamp permalink LinkedIn draws
    beside it -- so a reader returning one entry per anchor gives three items
    here and two on a fixture where every urn appeared once.
    """
    result, navigations, _scripts = await run_tool(HIS_RAIL_HTML)

    assert result.get("refused") is None, result
    assert result["authorship"]["established"] is True
    assert result["authorship"]["unanimous"] is True
    assert result["authorship"]["authors_found"] == 1
    assert result["authorship"]["matches_page_owner"] is True

    assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]
    assert result["anchors_per_item"] == {HIS_ITEM_ONE: 2, HIS_ITEM_TWO: 1}
    assert result["counts"] == {
        "overflow_controls": 2,
        "owner_headings": 1,
        # BOTH ROUTES, and on this fixture they agree because its h1 is
        # plainly rendered. The pair is what makes the disagreement visible on
        # a page where it happens, and the fixture below is that page.
        "owner_headings_rendered": 1,
        "owner_headings_contained": 1,
        # ZERO because the harness serves a fragment with no <title>. That is
        # the fixture's shape and not a claim about LinkedIn -- and it is the
        # right shape here, because a page WITH a heading must be judged on
        # the heading whatever its title says.
        "owner_title_present": 0,
        "permalink_anchors": 3,
        "distinct_urns": 2,
        "unrecognised": 0,
        "unpaired": 0,
    }
    # AND THE ROUTE IS NAMED. On a rendered heading it must be the innerText
    # one: the fallback exists for a heading innerText cannot see, and a
    # reader that took the fallback here would be taking it always.
    assert result["authorship"]["owner_source"] == "h1-innertext"
    assert result["pages_loaded"] == 1
    assert navigations == [SELF_PROFILE_URL], navigations


#: THE LIVE REFUSAL, REPRODUCED -- and the construction was MEASURED rather
#: than reached for, because the obvious one does not work.
#:
#: Nine constructions were run through a real Chromium on 2026-08-31, reading
#: ``innerText`` and ``textContent`` off the same ``h1``. Only THREE produce
#: the live symptom (rendered empty, contained non-empty):
#:
#:     h1 style="visibility:hidden"          ''            'Owner Name'
#:     h1 > span style="display:none"        ''            'Owner Name'
#:     h1 > span style="visibility:hidden"   ''            'Owner Name'
#:
#: and SIX do not, including the two a reader would reach for first:
#:
#:     h1 style="display:none"               'Owner Name'  'Owner Name'
#:     h1 clip/absolute visually-hidden      'Owner Name'  'Owner Name'
#:     h1 aria-hidden="true"                 'Owner Name'  'Owner Name'
#:     h1 width:0;height:0;overflow:hidden   'Owner Name'  'Owner Name'
#:     h1 plain                              'Owner Name'  'Owner Name'
#:     h1 empty                              ''            ''
#:
#: ``display:none`` FAILS TO REPRODUCE IT because the spec says ``innerText``
#: on an element that is NOT BEING RENDERED returns ``textContent`` -- the
#: fallback is the whole point of that clause. The element has to be rendered
#: and its TEXT not, which is what ``visibility:hidden`` and a hidden child
#: do. And the clip-and-absolute pattern -- the standard "visually hidden"
#: recipe, and the one LinkedIn is most likely to use -- reads NORMALLY, which
#: is why this fixture is a reproduction of the CLASS and NOT evidence about
#: what the live page does. What the live page does is unmeasured; the two
#: counts this reader now reports are what will say.
HIDDEN_H1_HTML = HIS_RAIL_HTML.replace(
    H1_OWNER, f'<h1 style="visibility:hidden">{OWNER_FULL}</h1>'
)


async def test_a_heading_out_of_layout_used_to_refuse_and_now_names_the_owner(
    run_tool,
):
    """THE DEFECT THIS ROUTE WAS ADDED FOR, reproduced rather than described.

    On 2026-08-31 the live profile answered ``no_page_owner_heading`` TWICE,
    identically, while the two conditions that do the real work both held --
    LinkedIn's own ``isSelfProfile=true``, and one author across all eight
    overflow controls. The census measured 233 controls on the same page in
    the same session, so it was not a half-render: the reading was stable and
    the reader still would not aim.

    ``innerText`` IS A RENDERED-TEXT READING and C3 is not a question about
    rendering. It asks whether LinkedIn's own markup names this page's owner
    -- a claim about the DOCUMENT -- so making it depend on CSS was the
    defect, and it is the same shape as ``name_source: "none"`` meaning "this
    instrument cannot read one" while reading as "the control has none".

    THE CONTROL THAT MAKES THIS A REPRODUCTION rather than an assertion about
    the new code is the second half: the fixture is shown carrying the
    heading, and the rendered route is shown answering zero on it. Without
    that, a fixture with no h1 at all would pass this test.
    """
    assert OWNER_FULL in HIDDEN_H1_HTML
    result, _navigations, _scripts = await run_tool(HIDDEN_H1_HTML)

    # The rendered route sees NOTHING, which is the live symptom exactly.
    assert result["counts"]["owner_headings_rendered"] == 0
    # And the document says the owner is there.
    assert result["counts"]["owner_headings_contained"] == 1

    assert result.get("refused") is None, result
    assert result["authorship"]["established"] is True
    assert result["authorship"]["owner_source"] == "h1-textcontent"
    assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]


async def test_the_fallback_route_does_not_relax_the_wrong_owner_refusal(
    run_tool,
):
    """THE FALLBACK IS A SECOND ROUTE TO THE TEXT, NOT A WEAKER RULE.

    The obvious way to get past a refusing C3 is to stop requiring the
    comparison, and that is what this refuses to have done. A hidden heading
    naming SOMEBODY ELSE must still refuse: the route changed where the string
    is read from, and nothing about what is done with it.
    """
    wrong = WRONG_OWNER_HTML.replace(
        f"<h1>{OTHER_AUTHOR}</h1>",
        f'<h1 style="visibility:hidden">{OTHER_AUTHOR}</h1>',
    )
    assert OTHER_AUTHOR in wrong
    result, _navigations, _scripts = await run_tool(wrong)

    assert result["counts"]["owner_headings_rendered"] == 0
    assert result["counts"]["owner_headings_contained"] == 1
    assert result["refused"] == "author_is_not_the_page_owner", result
    assert "items" not in result
    # The refusal names the route it compared through, so a reader can tell a
    # rendered mismatch from a contained one.
    assert "h1-textcontent" in result["reason"]


async def test_two_hidden_headings_are_ambiguous_rather_than_resolved(run_tool):
    """AMBIGUITY SURVIVES THE FALLBACK. Two headings is two headings whichever
    route reads them, and picking one would be picking by document order --
    the rule this reader exists to keep. Written because a fallback that
    silently took the first of two would look identical from the outside on
    every page that has one."""
    two = TWO_HEADING_HTML.replace("<h1>", '<h1 style="visibility:hidden">')
    result, _navigations, _scripts = await run_tool(two)

    assert result["counts"]["owner_headings_rendered"] == 0
    assert result["counts"]["owner_headings_contained"] == 2
    assert result["refused"] == "ambiguous_page_owner_heading", result
    assert "items" not in result


async def test_no_heading_at_all_still_refuses_and_says_both_routes_saw_zero(
    run_tool,
):
    """AND THE REFUSAL THAT SURVIVES, now meaning something stronger.

    Before the second route, ``no_page_owner_heading`` could mean either "no
    heading" or "a heading this instrument cannot read". It now means only the
    first, and the reason prints both counts so the claim is checkable from
    the answer rather than from the source.
    """
    result, _navigations, _scripts = await run_tool(
        HIS_RAIL_HTML.replace(H1_OWNER, "")
    )
    assert result["refused"] == "no_page_owner_heading", result
    assert result["counts"]["owner_headings_rendered"] == 0
    assert result["counts"]["owner_headings_contained"] == 0
    assert "rendered (0)" in result["reason"]
    assert "contained (0)" in result["reason"]
    assert "items" not in result


def test_the_his_rail_fixture_really_repeats_one_urn():
    """THE CONTROL for the dedupe half of A2: the fixture is shown carrying
    item one's urn twice and item two's once."""
    assert HIS_RAIL_HTML.count(PERMALINK_BASE + HIS_ITEM_ONE + "/") == 2
    assert HIS_RAIL_HTML.count(PERMALINK_BASE + HIS_ITEM_TWO + "/") == 1


# ---------------------------------------------------------------------------
# A3. C1, and the page that is never read
# ---------------------------------------------------------------------------


async def test_without_the_self_assertion_nothing_at_all_is_read(run_tool):
    """LINKEDIN'S OWN CLAIM COMES FIRST, and the markup is IDENTICAL to A2's.

    That is what makes this test about C1 and nothing else: the same document
    that yields two item keys one line above yields no key at all here, and the
    only thing that changed is the query string on the landed url.

    ``scripts == []`` is the strong half. "The answer carried no counts" would
    also hold for a reader that injected the script and discarded the result;
    the proxy in the harness sees the injection itself, so this asserts that
    nothing was read rather than that nothing was reported.
    """
    result, navigations, scripts = await run_tool(
        HIS_RAIL_HTML, landed=LANDED_NO_ASSERTION
    )

    assert result.get("refused") == "no_self_assertion", result
    assert "items" not in result, sorted(result)
    assert "counts" not in result, sorted(result)
    assert "item_root_source" not in result, sorted(result)
    assert scripts == [], scripts
    assert navigations == [SELF_PROFILE_URL], navigations

    assert result["authorship"]["established"] is False
    assert result["authorship"]["self_assertion_present"] is False
    assert result["authorship"]["authors_found"] is None
    assert result["authorship"]["unanimous"] is None
    assert result["authorship"]["matches_page_owner"] is None
    assert result["pages_loaded"] == 1


async def test_the_same_markup_reads_when_the_assertion_is_there(run_tool):
    """THE CONTROL for A3: the identical document, with the assertion, does
    inject the script -- so ``scripts == []`` above is a fact about C1 and not
    about the fixture."""
    _result, _navigations, scripts = await run_tool(HIS_RAIL_HTML)
    assert scripts == [dom.ACTIVITY_ITEMS_JS], len(scripts)


# ---------------------------------------------------------------------------
# A4 and A5. C3, in its three failing shapes
# ---------------------------------------------------------------------------


async def test_an_h1_naming_somebody_else_refuses(run_tool):
    """THE CASE ONLY C3 CATCHES. C1 holds -- the url carries the assertion. C2
    holds -- every overflow control on the page names one person. And the page
    is somebody else's, which is what a hijacked redirect or a mis-served
    render looks like, and the only thing that says so is the heading.
    """
    result, _navigations, _scripts = await run_tool(WRONG_OWNER_HTML)

    assert result.get("refused") == "author_is_not_the_page_owner", result
    assert "items" not in result, sorted(result)
    assert result["authorship"]["self_assertion_present"] is True
    assert result["authorship"]["unanimous"] is True
    # COMPARED, and different. Not None -- the comparison did happen here, and
    # that is the difference between this refusal and the two below it.
    assert result["authorship"]["matches_page_owner"] is False
    assert result["counts"]["owner_headings"] == 1


async def test_no_h1_at_all_refuses(run_tool):
    """NO HEADING IS NOT A PASS. The tempting shape of this bug is a fallback --
    "there is no heading, so compare the author against itself" -- which would
    make C3 unconditionally true on any page LinkedIn renders without one.
    """
    result, _navigations, _scripts = await run_tool(NO_HEADING_HTML)

    assert result.get("refused") == "no_page_owner_heading", result
    assert "items" not in result, sorted(result)
    assert result["authorship"]["unanimous"] is True
    assert result["authorship"]["matches_page_owner"] is None
    assert result["counts"]["owner_headings"] == 0


async def test_two_h1_elements_refuse_rather_than_take_the_first(run_tool):
    """TWO HEADINGS IS NOT A TIE TO BREAK. Choosing one of them would be
    choosing by document order, which is the defect this package refuses
    everywhere else -- the editor's container is found by its anchor for the
    same reason.

    HIS HEADING IS FIRST in the fixture, so a take-the-first implementation
    would ESTABLISH here rather than refuse. That is what makes this test able
    to fail.
    """
    result, _navigations, _scripts = await run_tool(TWO_HEADING_HTML)

    assert result.get("refused") == "ambiguous_page_owner_heading", result
    assert "items" not in result, sorted(result)
    assert result["counts"]["owner_headings"] == 2
    assert result["authorship"]["matches_page_owner"] is None


def test_the_heading_fixtures_differ_only_in_the_heading():
    """THE CONTROL for A4 and A5: all three are derived from A2's markup by
    substituting the heading, so the rail underneath is identical and the tests
    above isolate C3."""
    assert WRONG_OWNER_HTML != HIS_RAIL_HTML
    assert NO_HEADING_HTML != HIS_RAIL_HTML
    assert TWO_HEADING_HTML != HIS_RAIL_HTML
    for markup in (WRONG_OWNER_HTML, NO_HEADING_HTML, TWO_HEADING_HTML):
        assert markup.count(OVERFLOW_PREFIX + AUTHOR_SHORT) == 2, markup[:80]
    assert TWO_HEADING_HTML.index(OWNER_FULL) < TWO_HEADING_HTML.index(
        f"<h1>{OTHER_AUTHOR}</h1>"
    ), "his heading must be first, or a take-the-first reader would refuse"


# ---------------------------------------------------------------------------
# A6. An empty rail is not an authorship claim
# ---------------------------------------------------------------------------


async def test_zero_overflow_controls_refuses(run_tool):
    """NOBODY DISAGREED IS NOT AGREEMENT. Unanimity over an empty set is
    vacuously true, and a reader that took it that way would publish every urn
    on any page carrying no overflow controls at all.

    The counts still come back, and that is the point of reporting them on a
    refusal: two permalink anchors were seen and both are unpaired, so a caller
    can tell "this page has nothing on it" from "this page could not be read".
    """
    result, _navigations, _scripts = await run_tool(EMPTY_RAIL_HTML)

    assert result.get("refused") == "no_overflow_controls", result
    assert "items" not in result, sorted(result)
    assert result["counts"]["overflow_controls"] == 0
    assert result["counts"]["permalink_anchors"] == 2
    assert result["counts"]["unpaired"] == 2
    assert result["counts"]["distinct_urns"] == 0
    assert result["authorship"]["authors_found"] == 0
    assert result["authorship"]["unanimous"] is False


# ---------------------------------------------------------------------------
# A7. The prefix rule, in both directions
# ---------------------------------------------------------------------------

PREFIX_CASES = [
    (
        "overflow shortened, h1 full -- the MEASURED asymmetry",
        AUTHOR_SHORT,
        OWNER_FULL,
        True,
    ),
    ("the other direction, which the rule also admits", OWNER_FULL, AUTHOR_SHORT, True),
    ("a different name that merely starts alike", NEAR_MISS_AUTHOR, OWNER_FULL, False),
]


@pytest.mark.parametrize(
    "label,author,heading,expected",
    PREFIX_CASES,
    ids=[row[0] for row in PREFIX_CASES],
)
async def test_the_prefix_rule_in_both_directions(
    run_tool, label, author, heading, expected
):
    """WHY NOT EQUALITY, AND WHAT IT COSTS.

    LinkedIn is measured to write a SHORTENED form of his name into the overflow
    label while the ``h1`` carries the full one, so exact equality would refuse a
    page that is entirely his -- row one. The rule is symmetric because nothing
    measured says which side is the short one, and asserting a direction nobody
    measured is how a guess gets written down as a fact -- row two.

    THE THIRD ROW IS THE COST, PINNED. ``Adam Lovelace`` and ``Ada Lovelace``
    share five characters and neither is a prefix of the other, so the rule
    rejects. What it would NOT reject is a member whose display name really is a
    prefix of the owner's -- the residue recorded in ``dom.py`` above the
    script. C1 and C2 are what make that residue unreachable, which is why all
    three conditions are required rather than any two.
    """
    result, _navigations, _scripts = await run_tool(
        prefix_case(author, heading)
    )

    if expected:
        assert result.get("refused") is None, result
        assert result["items"] == [HIS_ITEM_ONE], result
        assert result["authorship"]["matches_page_owner"] is True
    else:
        assert result.get("refused") == "author_is_not_the_page_owner", result
        assert "items" not in result, sorted(result)
        assert result["authorship"]["matches_page_owner"] is False


def test_the_near_miss_really_is_a_near_miss():
    """THE CONTROL for row three: the two names are shown sharing a prefix and
    standing in no prefix relation, so the row tests the rule rather than two
    unrelated strings."""
    assert NEAR_MISS_AUTHOR[:3] == OWNER_FULL[:3]
    assert not NEAR_MISS_AUTHOR.startswith(OWNER_FULL)
    assert not OWNER_FULL.startswith(NEAR_MISS_AUTHOR)


# ---------------------------------------------------------------------------
# A8. The anchored shape
# ---------------------------------------------------------------------------


async def test_a_permalink_that_is_not_urn_shaped_is_counted_never_emitted(
    run_tool,
):
    """A MALFORMED HREF MUST NOT BE ABLE TO SMUGGLE A STRING OUT.

    Both junk anchors sit INSIDE a properly rooted item, so the pairing rule
    admits them and the anchored shape is the only thing keeping them out -- if
    they were loose, this test would be a second copy of A9.

    THE SECOND ONE IS THE REALISTIC NEAR MISS. The percent-encoded urn spelling
    has never been observed in this position; the measured ``href_shape`` on his
    profile carried the literal one. Admitting a spelling nobody has seen is how
    a reader starts accepting shapes it was never shown, so it is counted
    unrecognised exactly like the junk.
    """
    result, _navigations, _scripts = await run_tool(HIS_RAIL_WITH_JUNK_HTML)

    assert result.get("refused") is None, result
    assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]
    assert result["counts"]["unrecognised"] == 2, result["counts"]
    assert result["counts"]["permalink_anchors"] == 5, result["counts"]

    rendered = serialised(result)
    assert NON_URN_SEGMENT not in rendered, rendered
    assert ENCODED_SEGMENT not in rendered, rendered


def test_the_junk_fixture_really_carries_both_malformed_segments():
    """THE CONTROL for A8."""
    assert PERMALINK_BASE + NON_URN_SEGMENT + "/" in HIS_RAIL_WITH_JUNK_HTML
    assert PERMALINK_BASE + ENCODED_SEGMENT + "/" in HIS_RAIL_WITH_JUNK_HTML


# ---------------------------------------------------------------------------
# A9. The pairing rule
# ---------------------------------------------------------------------------


async def test_a_urn_in_no_item_root_is_counted_never_emitted(run_tool):
    """A URN ON THE PAGE IS NOT A URN OF AN ITEM ON THE PAGE.

    The stray anchor here is the "Show all posts" link a rail draws in its
    footer, and its only overflow-bearing ancestor is ``body``. A reader whose
    climb stopped at the document would pair it to the whole render and publish
    it, which is the failure the document-level stop exists for -- and the hop
    ceiling does not close it, because this document reaches ``body`` in two
    hops.
    """
    result, _navigations, _scripts = await run_tool(HIS_RAIL_WITH_STRAY_HTML)

    assert result.get("refused") is None, result
    assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]
    assert result["counts"]["unpaired"] == 1, result["counts"]
    assert result["counts"]["permalink_anchors"] == 4, result["counts"]
    assert STRAY_ITEM not in serialised(result), serialised(result)


def test_the_stray_really_sits_outside_the_rail():
    """THE CONTROL for A9: the stray urn is in the fixture, and it is after the
    closing ``</main>`` -- so it genuinely has no item ancestor and the test is
    not passing because the anchor was never drawn."""
    assert STRAY_ITEM in HIS_RAIL_WITH_STRAY_HTML
    assert HIS_RAIL_WITH_STRAY_HTML.index(
        "</main>"
    ) < HIS_RAIL_WITH_STRAY_HTML.index(STRAY_ITEM)


# ---------------------------------------------------------------------------
# A10. No name leaves the page. On EVERY path.
# ---------------------------------------------------------------------------

#: Every path the tool has, success and refusal alike, as (label, markup,
#: landed url). Enumerated rather than sampled: the leak this guards against is
#: most likely on a path somebody forgot, and a success-only sweep would have
#: missed the refusal reasons entirely.
EVERY_PATH = [
    ("established", HIS_RAIL_HTML, LANDED_PROFILE),
    ("no_self_assertion", HIS_RAIL_HTML, LANDED_NO_ASSERTION),
    ("mixed_authors", MIXED_RAIL_HTML, LANDED_PROFILE),
    ("no_overflow_controls", EMPTY_RAIL_HTML, LANDED_PROFILE),
    ("no_page_owner_heading", NO_HEADING_HTML, LANDED_PROFILE),
    ("ambiguous_page_owner_heading", TWO_HEADING_HTML, LANDED_PROFILE),
    ("author_is_not_the_page_owner", WRONG_OWNER_HTML, LANDED_PROFILE),
]


@pytest.mark.parametrize(
    "label,markup,landed", EVERY_PATH, ids=[row[0] for row in EVERY_PATH]
)
async def test_no_name_or_member_segment_is_anywhere_in_the_answer(
    run_tool, label, markup, landed
):
    """THE PRIVACY PROPERTY, SWEPT OVER THE WHOLE SERIALISED ANSWER.

    The author string and the ``h1`` text are read, compared and discarded
    INSIDE the document; only booleans and counts come back. That is a
    structural guarantee rather than a shaping one -- there is nothing on this
    side to redact -- and this is where it is measured rather than described.

    The member slug is hunted too. It is in the landed url on every one of these
    paths and in the answer on none of them, which is the same discipline
    ``linkedin_profile_editor_fields`` keeps when it compares a segment and
    reports only that the two agreed.
    """
    result, _navigations, _scripts = await run_tool(markup, landed=landed)
    rendered = serialised(result)

    for secret in (AUTHOR_SHORT, OWNER_FULL, OTHER_AUTHOR, MEMBER_SLUG):
        assert secret not in rendered, (label, secret, rendered)


def test_every_one_of_those_names_really_is_in_its_markup():
    """THE CONTROL for A10. Without it the sweep would pass against fixtures
    that never carried the names -- and a leak test over markup with nothing to
    leak certifies nothing.

    The slug is checked separately because it lives in the landed URL rather
    than in the document, which is exactly why it is the one a
    document-oriented reader would forget.
    """
    assert AUTHOR_SHORT in HIS_RAIL_HTML
    assert OWNER_FULL in HIS_RAIL_HTML
    assert OTHER_AUTHOR in MIXED_RAIL_HTML
    assert OTHER_AUTHOR in WRONG_OWNER_HTML
    assert MEMBER_SLUG in LANDED_PROFILE
    assert MEMBER_SLUG in LANDED_NO_ASSERTION


# ---------------------------------------------------------------------------
# A11. Which route found the item root, and what it did NOT read
# ---------------------------------------------------------------------------

ROUTE_CASES = [
    ("data-urn", DATA_URN_RAIL_HTML, {"data-urn": 3, "data-id": 0, "climb": 0}),
    ("data-id", DATA_ID_RAIL_HTML, {"data-urn": 0, "data-id": 3, "climb": 0}),
    ("climb", HIS_RAIL_HTML, {"data-urn": 0, "data-id": 0, "climb": 3}),
]


@pytest.mark.parametrize(
    "label,markup,expected", ROUTE_CASES, ids=[row[0] for row in ROUTE_CASES]
)
async def test_the_route_that_found_each_item_root_is_reported(
    run_tool, label, markup, expected
):
    """"LINKEDIN LABELLED THE BOUNDARY" AND "I CLIMBED UNTIL I FOUND ONE" ARE
    DIFFERENT ANSWERS, and a caller has to be able to tell them apart -- the
    same ``name_source`` discipline the rest of this package keeps.

    All three rows publish the SAME two urns, which is the half that makes the
    route a report rather than a behaviour change: the route decides where the
    item boundary is, never what gets published.

    THE THIRD ROW IS ALSO A CONTROL. Without it, a reader that had quietly lost
    the climb would still pass the first two rows, and the climb is the route
    that fires on a page LinkedIn has not labelled.
    """
    result, _navigations, _scripts = await run_tool(markup)

    assert result.get("refused") is None, result
    assert result["item_root_source"] == expected, result["item_root_source"]
    assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]


async def test_the_root_marker_value_is_never_what_gets_published(run_tool):
    """``[data-urn]`` IS A MARKER OF A BOUNDARY, NOT A SOURCE OF A URN.

    The fixture's two item roots carry each OTHER'S urn in ``data-urn``, so a
    reader that published the attribute would return the same two urns in the
    opposite order. Asserting the order is what makes that detectable; asserting
    the SET would pass against exactly the bug being guarded.
    """
    result, _navigations, _scripts = await run_tool(DATA_URN_RAIL_HTML)

    assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]
    assert result["anchors_per_item"] == {HIS_ITEM_ONE: 2, HIS_ITEM_TWO: 1}


def test_the_data_urn_fixture_really_has_its_attributes_swapped():
    """THE CONTROL for the test above: the attribute values are shown to be the
    other item's, so "the href won" is a measurement rather than a tautology."""
    assert f'data-urn="{HIS_ITEM_TWO}"' in DATA_URN_RAIL_HTML
    assert f'data-urn="{HIS_ITEM_ONE}"' in DATA_URN_RAIL_HTML
    first_root = DATA_URN_RAIL_HTML.index(f'data-urn="{HIS_ITEM_TWO}"')
    first_href = DATA_URN_RAIL_HTML.index(PERMALINK_BASE + HIS_ITEM_ONE + "/")
    assert first_root < first_href, "the first root must carry the other urn"


# ---------------------------------------------------------------------------
# The structural guards
# ---------------------------------------------------------------------------


async def test_the_activity_chain_resolves_the_same_names_as_the_census():
    """THE THIRD COPY OF THE NAME CHAIN, HELD TO AGREEING.

    ``ACTIVITY_ITEMS_JS`` carries its own copy of ``CENSUS_JS``'s
    name-resolution chain, and the duplication is forced for the reason recorded
    above ``EDITOR_FIELDS_JS``: the census script is document-wide and returns
    raw names for the whole page, which is the thing being avoided, and a script
    assembled from a shared fragment cannot be certified by
    ``tests/test_readonly.py``'s call-site resolver.

    A copy nothing compares is a copy that goes stale, so ``nameOf`` is exposed
    from this script for the same document and compared against the census's,
    name AND ``name_source`` -- the source being the half that says which route
    won.

    IT COMPARES THE CHAIN, NOT THE MATCHER. The matcher runs over the UNION of
    the five routes on purpose, which is a deliberate difference from the census
    rather than drift, and it is measured in the test below this one.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport=dict(ACTIVITY_VIEWPORT))
        try:
            page_obj = await context.new_page()
            await page_obj.set_content(
                HIS_RAIL_HTML, wait_until="domcontentloaded", timeout=60_000
            )
            width = await page_obj.evaluate("window.innerWidth")
            assert width == ACTIVITY_VIEWPORT["width"], width

            census = await page_obj.evaluate(
                dom.CENSUS_JS,
                {
                    "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
                    "maxControls": dom.CENSUS_MAX_CONTROLS,
                    "maxChars": 300,
                },
            )
            # The activity script's own chain, called on every control the
            # census saw. The probe reuses the script's text so it cannot drift
            # from what the reader runs -- it appends one expression that calls
            # the chain and nothing else.
            probe = dom.ACTIVITY_ITEMS_JS.replace(
                "  const out = {\n",
                "  if (cfg.probeNames) {\n"
                "    const probed = [];\n"
                "    for (const el of all) {\n"
                "      const named = nameOf(el);\n"
                "      probed.push([named.name, named.source]);\n"
                "    }\n"
                "    return { probed: probed };\n"
                "  }\n"
                "  const out = {\n",
                1,
            )
            assert probe != dom.ACTIVITY_ITEMS_JS, "the probe did not attach"
            probed = await page_obj.evaluate(
                probe,
                {
                    "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
                    "overflowPrefix": dom.ACTIVITY_OVERFLOW_PREFIX,
                    "permalinkMarker": dom.ACTIVITY_PERMALINK_MARKER,
                    "maxAnchors": dom.ACTIVITY_MAX_ANCHORS,
                    "maxHops": dom.ACTIVITY_MAX_HOPS,
                    "maxChars": 300,
                    "probeNames": True,
                },
            )
        finally:
            await context.close()
            await browser.close()

    from_activity = [
        (row[0], row[1]) for row in probed["probed"] if row[0]
    ]
    from_census = {
        (row["name"], row["name_source"])
        for row in census["controls"]
        if row["name"]
    }
    assert from_activity, from_activity
    for pair in from_activity:
        assert pair in from_census, (pair, sorted(from_census))


async def test_the_matcher_sees_an_author_the_chain_would_miss():
    """THE UNION, MEASURED, AND WHY IT IS THE SAFETY DIRECTION.

    ``CENSUS_JS`` resolves ONE name per control -- the first route that answers.
    A control whose ``aria-label`` is generic while its ``title`` names an
    author is therefore invisible to the chain, and an author the matcher cannot
    see is an author C2 cannot count: unanimity would hold over a page that is
    not unanimous, which is precisely the A1 failure.

    So the matcher runs over the union of the five routes, and this is where
    that is shown to make a difference rather than asserted to. The fixture is
    A2's rail with ONE extra control that hides an author behind ``title``, and
    the tool refuses it as mixed.
    """
    hidden = page(
        heading=H1_OWNER,
        rail=(
            item(AUTHOR_SHORT, HIS_ITEM_ONE)
            + '<div class="item">'
            + '<button aria-label="More" '
            + f'title="{OVERFLOW_PREFIX}{OTHER_AUTHOR}"></button>'
            + permalink(OTHER_ITEM, "Comment")
            + "</div>"
        ),
    )
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport=dict(ACTIVITY_VIEWPORT))
        try:
            page_obj = await context.new_page()
            await page_obj.set_content(
                hidden, wait_until="domcontentloaded", timeout=60_000
            )
            width = await page_obj.evaluate("window.innerWidth")
            assert width == ACTIVITY_VIEWPORT["width"], width
            reading = await page_obj.evaluate(
                dom.ACTIVITY_ITEMS_JS,
                {
                    "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
                    "overflowPrefix": dom.ACTIVITY_OVERFLOW_PREFIX,
                    "permalinkMarker": dom.ACTIVITY_PERMALINK_MARKER,
                    "maxAnchors": dom.ACTIVITY_MAX_ANCHORS,
                    "maxHops": dom.ACTIVITY_MAX_HOPS,
                    "maxChars": 300,
                },
            )
            census = await page_obj.evaluate(
                dom.CENSUS_JS,
                {
                    "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
                    "maxControls": dom.CENSUS_MAX_CONTROLS,
                    "maxChars": 300,
                },
            )
        finally:
            await context.close()
            await browser.close()

    # THE CONTROL, in the same test, and it is the half that makes this a
    # measurement. The census's chain resolves the hidden control to its
    # aria-label -- "More" -- so the SECOND author is nowhere in the census's
    # answer: exactly ONE control reports a prefixed name, item one's, and
    # OTHER_AUTHOR appears in none of them. That is the blind spot the matcher
    # has to see past, shown rather than argued.
    census_names = [str(row["name"]) for row in census["controls"]]
    assert "More" in census_names, census_names
    prefixed = [
        name for name in census_names if name.startswith(OVERFLOW_PREFIX)
    ]
    assert prefixed == [OVERFLOW_PREFIX + AUTHOR_SHORT], prefixed
    assert not any(OTHER_AUTHOR in name for name in census_names), census_names

    assert reading["overflow_controls"] == 2, reading
    assert reading["authors_found"] == 2, reading
    assert reading["established"] is False, reading
    assert "items" not in reading, sorted(reading)


def test_the_measured_strings_are_the_ones_the_census_read():
    """THE ANCHOR FOR EVERY FIXTURE IN THIS FILE.

    The markup above is BUILT from ``dom.ACTIVITY_OVERFLOW_PREFIX`` and
    ``dom.ACTIVITY_PERMALINK_MARKER`` rather than retyped, so a fixture cannot
    drift from the reader -- but on its own that is circular: change the
    constant and every fixture follows and every test still passes. This is the
    one place the constants are held to the literals the 2026-08-31 census
    actually read, which is what makes the rest of the file mean something.

    THE TRAILING SPACE ON THE PREFIX IS ASSERTED SEPARATELY. Without it the
    prefix would match a control named ``...for post byline`` and hand back
    ``line`` as an author, so it is a property of the string rather than a
    typo somebody might tidy away.
    """
    assert dom.ACTIVITY_OVERFLOW_PREFIX == "Open control menu for post by "
    assert dom.ACTIVITY_OVERFLOW_PREFIX.endswith(" ")
    assert dom.ACTIVITY_PERMALINK_MARKER == "/feed/update/"


def test_the_tool_reads_one_page_and_takes_no_argument():
    """NO ARGUMENT SELECTS A SURFACE, which is what stops a caller aiming this
    at a page full of other members. The address is a literal, and it is the
    same one the census reaches under ``profile`` -- pinning the pair equal is
    what stops the two tools drifting onto different pages while claiming one
    measurement.

    THE READ BOUNDARY IS UNCHANGED and that is asserted rather than promised:
    ``/in/me/`` was already admitted and is already loaded by several tools, so
    this slice needed no widening of ``readonly``'s allowlist and did none.
    """
    signature = inspect.signature(linkedin_my_activity_items)
    assert list(signature.parameters) == [], signature

    assert SELF_PROFILE_URL == CENSUS_SURFACES["profile"]
    assert readonly.is_read_url(SELF_PROFILE_URL) is True


async def test_the_refusal_codes_are_the_enumeration_they_claim_to_be(run_tool):
    """A COMPLETENESS CLAIM, MADE CHECKABLE.

    ``dom.ACTIVITY_REFUSALS`` says the reader has five refusals and the tool
    adds a sixth of its own. A tuple nothing exercises is a list of hopes, so
    every code in it is produced here by a real fixture, and every code produced
    is shown to be in it -- both directions, because one of them alone would
    pass against a tuple with a spare entry nobody can reach.
    """
    produced = set()
    for _label, markup, landed in EVERY_PATH:
        result, _navigations, _scripts = await run_tool(markup, landed=landed)
        code = result.get("refused")
        if code is not None:
            produced.add(code)

    assert produced == set(dom.ACTIVITY_REFUSALS) | {"no_self_assertion"}, (
        sorted(produced),
        sorted(dom.ACTIVITY_REFUSALS),
    )


async def test_the_urns_are_published_unshaped_and_that_is_the_capability(
    run_tool,
):
    """THE ONE THING THIS READER DOES THAT NOTHING ELSE HERE DOES.

    Every other reader in ``dom.py`` hands its output to ``census_shape`` or at
    least to ``census_substitute``. Run either over one of these urns and the
    answer is ``<urn>`` -- which is exactly the useless answer this tool exists
    to replace, and why a shaped urn would be a silent regression rather than a
    visible one.
    """
    assert shape.census_substitute(HIS_ITEM_ONE) == "<urn>"
    assert shape.census_shape(HIS_ITEM_ONE) == "<urn>"

    result, _navigations, _scripts = await run_tool(HIS_RAIL_HTML)
    assert result["items"][0] == HIS_ITEM_ONE
    assert "<urn>" not in serialised(result)


def test_the_injected_script_only_reads():
    """The same scan ``test_readonly.py`` runs, asserted here too because this
    is the script that publishes an identifier -- if any script in this package
    deserves a second reader, it is this one and the editor's."""
    assert readonly.scan_js_for_mutations(dom.ACTIVITY_ITEMS_JS) == []


def test_that_scan_can_fail_on_this_script():
    """THE CONTROL: the scanner is shown catching a mutation planted in this
    very script, so the assertion above is not vacuous."""
    planted = dom.ACTIVITY_ITEMS_JS.replace(
        "  const distinct = [];",
        "  const distinct = []; document.querySelector('button').click();",
    )
    assert ".click(" in readonly.scan_js_for_mutations(planted)


def test_the_script_never_scrolls_and_reads_no_control_value():
    """TWO PROMISES THE DOCSTRING MAKES, both read off the script rather than
    trusted.

    "Absent means UNKNOWN, not zero" is only honest while the script genuinely
    does not scroll -- an item below the fold is one this reader did not see,
    never one he did not write. And a label is not a value: nothing here reads
    what is IN a control, only what a control is called.
    """
    for token in ("scrollIntoView", "window.scrollTo", "scrollBy", "scrollTop"):
        assert token not in dom.ACTIVITY_ITEMS_JS, token
    assert ".value" not in dom.ACTIVITY_ITEMS_JS


def test_the_tool_warns_that_its_output_must_not_be_committed():
    """THE ONE WARNING THAT PROTECTS A GUARD RATHER THAN A PERSON.

    This tool returns real identifiers into a public repository's working
    session, and ``tests/test_no_committed_identity.py`` sweeps every tracked
    file for exactly that shape. The docstring is the only place a caller is
    told before they paste one into a fixture or a commit, so the warning is
    asserted present rather than left to survive an edit on goodwill.
    """
    text = (linkedin_my_activity_items.__doc__ or "").lower()
    assert "real identifier" in text
    assert "tracked file" in text
    assert "test_no_committed_identity" in text


# ---------------------------------------------------------------------------
# C3's THIRD ROUTE: the page's own title
# ---------------------------------------------------------------------------
#
# THE LIVE PROFILE HAS NO h1 CARRYING TEXT, by either route. Measured
# 2026-08-31 after the textContent route shipped: owner_headings_rendered 0
# AND owner_headings_contained 0, on a page the census measured at 233
# controls with isSelfProfile=true and one unanimous author. That REFUTED the
# CSS hypothesis the second route was built on, and reporting both counts is
# what settled it in one call rather than leaving it to be argued.
#
# So C3 consults a third thing, last: document.title, which is LinkedIn's own
# markup naming the page in the same sense isSelfProfile=true is LinkedIn's
# url naming it.


def titled(html: str, title: str) -> str:
    """The same markup with a ``<title>``. The harness serves fragments, so a
    title has to be put there deliberately -- which is the right default: a
    fixture that accidentally carried one would let the third route answer
    tests written about the first two."""
    assert "<title>" not in html
    return html.replace("<body>", f"<head><title>{title}</title></head><body>", 1)


#: HIS profile, no heading of any kind, titled the way a browser tab is --
#: an unread count in front and " | LinkedIn" behind. The decoration is the
#: whole reason this route compares by containment rather than by prefix.
TITLE_ONLY_HTML = titled(
    HIS_RAIL_HTML.replace(H1_OWNER, ""), f"(3) {OWNER_FULL} | LinkedIn"
)


async def test_the_page_title_names_the_owner_when_no_heading_does(run_tool):
    """THE ROUTE THE LIVE PAGE REQUIRES, on markup shaped like it.

    No h1 at all, so both heading routes answer zero -- which is the live
    profile's measured shape, not a contrivance. The title carries the owner,
    the one author on the rail is inside it, and authorship is established
    through ``document-title``.
    """
    result, _navigations, _scripts = await run_tool(TITLE_ONLY_HTML)

    assert result["counts"]["owner_headings_rendered"] == 0
    assert result["counts"]["owner_headings_contained"] == 0
    assert result["counts"]["owner_title_present"] == 1
    assert result.get("refused") is None, result
    assert result["authorship"]["established"] is True
    assert result["authorship"]["owner_source"] == "document-title"
    # WHICH HEADING ROUTE WOULD HAVE ANSWERED, reported separately: None here,
    # beside a non-null owner_source. That pair IS the live page's shape and
    # reporting the two apart is what makes it visible rather than inferable.
    assert result["authorship"]["owner_heading_source"] is None
    assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]


async def test_a_heading_still_wins_over_the_title(run_tool):
    """THE ORDER, asserted rather than assumed.

    The title route is consulted LAST. A page WITH a heading is judged on the
    heading, so adding a title cannot change a verdict -- which matters
    because a title is the loosest of the three comparisons and would
    otherwise be able to rescue a page the strict rule refused.
    """
    result, _navigations, _scripts = await run_tool(
        titled(HIS_RAIL_HTML, f"(3) {OWNER_FULL} | LinkedIn")
    )
    assert result["authorship"]["owner_source"] == "h1-innertext"
    assert result["authorship"]["established"] is True

    # AND THE CASE THAT PROVES IT IS AN ORDER AND NOT A PREFERENCE: a heading
    # naming somebody else, beside a title naming him. The heading refuses and
    # the title does not get to overturn it.
    wrong = titled(WRONG_OWNER_HTML, f"(3) {OWNER_FULL} | LinkedIn")
    result, _navigations, _scripts = await run_tool(wrong)
    assert result["refused"] == "author_is_not_the_page_owner", result
    assert "items" not in result


async def test_the_title_route_still_refuses_somebody_elses_rail(run_tool):
    """THE CASE C3 EXISTS FOR, and it must survive the widening.

    A rail of items by one OTHER member is UNANIMOUS -- it passes C2 -- and it
    is exactly what an activity rail full of reshares looks like. The title of
    HIS profile does not carry that member's name, so this refuses. If it did
    not, the third route would have turned C3 into a formality.
    """
    others = titled(
        HIS_RAIL_HTML.replace(H1_OWNER, "").replace(AUTHOR_SHORT, OTHER_AUTHOR),
        f"(3) {OWNER_FULL} | LinkedIn",
    )
    assert OTHER_AUTHOR in others
    result, _navigations, _scripts = await run_tool(others)
    assert result["counts"]["owner_title_present"] == 1
    assert result["refused"] == "author_is_not_the_page_owner", result
    assert "items" not in result
    # AND NO NAME LEAVES, on this path as on every other.
    blob = json.dumps(result)
    for secret in (OTHER_AUTHOR, OWNER_FULL, AUTHOR_SHORT):
        assert secret not in blob, secret


async def test_two_headings_do_not_fall_through_to_the_title(run_tool):
    """AMBIGUITY IS NOT RESOLVED BY CHANGING THE QUESTION.

    Two headings has no unambiguous owner and choosing one would be choosing
    by document order. Falling through to the title instead would answer a
    DIFFERENT question and call it the same one -- so the ambiguous refusal is
    asserted to survive a title that would have answered.
    """
    two = titled(TWO_HEADING_HTML, f"(3) {OWNER_FULL} | LinkedIn")
    result, _navigations, _scripts = await run_tool(two)
    assert result["refused"] == "ambiguous_page_owner_heading", result
    assert "items" not in result


async def test_a_page_naming_nobody_at_all_refuses_and_says_so(run_tool):
    """THE REFUSAL THAT SURVIVES ALL THREE ROUTES, and it now means something
    stronger than it did with one: nothing on this page names its owner by any
    route this reader consults. The reason prints all three counts, so the
    claim is checkable from the answer rather than from the source."""
    result, _navigations, _scripts = await run_tool(
        HIS_RAIL_HTML.replace(H1_OWNER, "")
    )
    assert result["refused"] == "no_page_owner_heading", result
    assert result["counts"]["owner_headings_rendered"] == 0
    assert result["counts"]["owner_headings_contained"] == 0
    assert result["counts"]["owner_title_present"] == 0
    assert result["authorship"]["owner_source"] is None
    assert "NAMES ITS OWNER" in result["reason"]
    assert "items" not in result


async def test_a_title_that_does_not_carry_the_author_refuses(run_tool):
    """A TITLE IS NOT A PASS. The page has one, it simply does not name the
    author -- which is what a mislabelled or non-profile page looks like, and
    it must read as a refusal rather than as an absence."""
    result, _navigations, _scripts = await run_tool(
        titled(HIS_RAIL_HTML.replace(H1_OWNER, ""), "Feed | LinkedIn")
    )
    assert result["counts"]["owner_title_present"] == 1
    assert result["refused"] == "author_is_not_the_page_owner", result
    assert "items" not in result


async def test_a_degenerate_author_is_too_short_to_compare_by_containment(
    run_tool,
):
    """THE BOUND ON THE LOOSER COMPARISON, shown doing something.

    Containment is looser than a prefix and the way it is loosest is a very
    short author string being a coincidental substring. ``ACTIVITY_MIN_AUTHOR_CHARS``
    stops the degenerate case from reading as an established authorship claim.
    It is a bound, not a fix, and it is asserted so that removing it fails
    here rather than passing quietly.

    ``"In"`` is inside ``"LinkedIn"``, which is in every one of these titles --
    so without the bound this page would establish authorship on a coincidence
    in LinkedIn's own suffix.
    """
    assert dom.ACTIVITY_MIN_AUTHOR_CHARS > len("In")
    short = titled(
        HIS_RAIL_HTML.replace(H1_OWNER, "").replace(AUTHOR_SHORT, "In"),
        f"(3) {OWNER_FULL} | LinkedIn",
    )
    result, _navigations, _scripts = await run_tool(short)
    assert result["counts"]["owner_title_present"] == 1
    assert result["refused"] == "no_page_owner_heading", result
    assert result["authorship"]["owner_source"] is None
    assert "items" not in result


# ---------------------------------------------------------------------------
# THE ENUMERATE-AND-DROP CLASS
# ---------------------------------------------------------------------------


async def test_every_authorship_fact_the_reader_produces_reaches_the_caller(
    run_tool, monkeypatch
):
    """THE DEFECT CLASS, GUARDED -- not its fourth instance.

    ``server._authorship_block`` builds its answer by NAMING keys. So does
    ``dom.read_own_activity_items``'s facts dict, and so did the census
    reader's row, and the census aggregate's merge key, and
    ``writes._read_dark_mode``'s projection. Every one of them has now dropped
    a field that the layer below it produced, SILENTLY, with no error and no
    test going red:

        ``container``          census reader -> aggregate, the day it was added
        the census row itself  built by INDEX, so a field renamed the columns
                               after it rather than going missing
        ``role``               _read_dark_mode's projection -> dom.aria_role_of,
                               which reads it FIRST
        ``owner_source``       this reader -> this block, 2026-08-31
        ``owner_heading_source``  the same pair, the same day, again

    Five instances of one shape. Each was found by a different accident and
    none by reading the code, which is what makes a per-field assertion the
    wrong instrument: it can only ever catch the field somebody thought of.

    SO THIS ASSERTS THE SET. Every key the reader puts in
    ``authorship_facts`` must appear in the block the tool returns. The block
    may carry MORE -- ``established`` and ``how`` are the tool's own -- but it
    may not carry LESS, and a sixth field added to the reader fails here
    without anybody adding a line.
    """
    seen: dict[str, object] = {}
    real = dom.read_own_activity_items

    async def spy(page, **kwargs):
        reading = await real(page, **kwargs)
        seen.update(reading.get("authorship_facts") or {})
        return reading

    monkeypatch.setattr(dom, "read_own_activity_items", spy)
    result, _navigations, _scripts = await run_tool(HIS_RAIL_HTML)

    assert seen, "the reader produced no authorship facts at all"
    missing = sorted(set(seen) - set(result["authorship"]))
    assert not missing, (
        f"the reader produced {missing} and the tool's block does not carry "
        "them. Both sides enumerate their keys, so a field added to one and "
        "not the other is dropped in silence -- five fields have gone that "
        "way in this package already."
    )
    # AND THE REFUSAL PATH TOO, which is the one a caller reads when it
    # matters most: a refusal is where the counts and the routes are the whole
    # of the answer, so a field dropped there is a field dropped exactly when
    # somebody is trying to work out why.
    seen.clear()
    refused, _navigations, _scripts = await run_tool(
        HIS_RAIL_HTML.replace(H1_OWNER, "")
    )
    assert refused.get("refused")
    missing = sorted(set(seen) - set(refused["authorship"]))
    assert not missing, missing
