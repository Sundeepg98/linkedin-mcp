"""Choosing from a typeahead is not typing into one, and the click aims by NAME.

WHAT THIS GATE IS FOR, AND THE MEASUREMENT THAT CREATED IT. On 2026-09-03 a
supervised run typed a correct, first-degree name into a genuinely empty
composer and ``_recipient_gate`` came back ``1_no_recipient_committed`` with
all four chip selectors reading ZERO and zero clicks made. That settles the
question ``send_message`` shipped in order to ask: **a bare fill does not
commit a recipient.** The missing step is selecting from the suggestions, and
``writes._typeahead_gate`` is the selecting.

## Why this click is a new class, and what holds it

Every other click in this package targets UI furniture -- ``Save the job``,
``Send``, a filter pill. **A typeahead row exists because LinkedIn matched a
PERSON**, so the control being pressed is drawn from somebody's name. The
design has to hold that rather than route around it, and two properties do:

* **Exactly one, or refuse.** Zero refuses, several refuse, and a row whose
  name does not carry his needle refuses. It never falls back to the first row.
  A dropdown of three people who all match is exactly the ``aim_invitation``
  failure, on the action with the least recoverable audience in the package.
* **The comparison runs in the page.** Playwright's ``name=`` matches the
  accessible name inside the browser and returns a COUNT. No suggestion's
  label, id or urn enters the process, so there is nothing for a traceback or
  a log line to publish.

## And the click is not its own evidence

The gate says a uniquely-named suggestion exists and may be pressed. It does
NOT say a recipient was committed. ``_recipient_gate`` still runs afterwards,
unchanged, and remains the only thing that lets his words be typed. A gate that
both performed an act and certified it would be reading its own homework --
the defect ``apply_job`` spent months inside.

## THE HONESTY REQUIREMENT, same shape as the recipient gate's

**``dom.TYPEAHEAD_OPTION_SELECTORS`` HAS NEVER MATCHED ANYTHING ON A REAL
LINKEDIN PAGE**, because nobody has typed into that combobox through this
server. The markup below draws a ``role="listbox"`` of ``role="option"`` rows,
which is candidate #1 and nothing more than a candidate. A test whose fixture
is built from the same guess as the code under test cannot validate the guess.

Every green result here means exactly this and no more:

    GIVEN a page that draws suggestions the way this fixture draws them, the
    gate's logic is correct -- it refuses an absent listbox, refuses zero
    options, refuses a wrong name, refuses several matches, and proceeds on
    exactly one carrying his needle, aiming by name rather than by position.

It means NOTHING about how LinkedIn draws a typeahead. That has one answer and
it is not in this repository: type a name into the live composer and read the
per-selector counts the gate's own refusal returns. The gate is BUILT to
produce that measurement -- it fails closed, so a first live run that refuses
hands back counts nobody could obtain another way.

**A REAL BROWSER IS REQUIRED AND THAT IS NOT INCIDENTAL.** The gate aims with
``role=option[name="..."i]``, which is Playwright's own selector engine
resolving an ACCESSIBLE NAME. A hand-rolled page double cannot evaluate it, so
a double would be testing a string rather than a match -- and the accessible
name is the entire safety property.
"""

from __future__ import annotations

import pytest

from linkedin_server import dom, writes
from linkedin_server.writes import spec_for_action

from tests.test_apply_modal_fixture import VIEWPORT, over  # noqa: F401
from tests.test_writes import _bare_grant  # noqa: F401

#: His own needle. Invented, and it is HIS input rather than a third party's --
#: the one string this gate is allowed to hold.
NEEDLE = "Thornwick M"
TARGET = NEEDLE + writes.TARGET_JOIN + "a message body that is never typed here"

#: A DIFFERENT PERSON, invented, shape-valid. Present so "the listbox drew
#: somebody" and "the listbox drew HIM" stay distinguishable -- a fixture whose
#: only row is the right one cannot tell those apart.
OTHER = "Priya Raghunathan"


def _listbox(*names: str) -> str:
    """A composer whose typeahead has drawn these suggestions, in this order."""
    rows = "".join(
        '<div role="option" tabindex="-1">'
        f"<span>{name}</span><span>1st</span>"
        "</div>"
        for name in names
    )
    return (
        "<html><body>"
        '<div role="combobox" aria-label="Enter message recipients"></div>'
        f'<div role="listbox" aria-label="Suggestions">{rows}</div>'
        "</body></html>"
    )


#: NO LISTBOX AT ALL -- the combobox is there and nothing opened under it.
NO_LISTBOX = (
    "<html><body>"
    '<div role="combobox" aria-label="Enter message recipients"></div>'
    "</body></html>"
)


def _grant(target: str = TARGET):
    return _bare_grant(action="send_message", target=target)


async def _gate(over, html: str, target: str = TARGET):  # noqa: F811
    """``_typeahead_gate`` over one page. Returns the verdict dict."""

    async def work(page):
        return await writes._typeahead_gate(page, _grant(target))

    return await over(html, work)


@pytest.fixture(autouse=True)
def _fast_timeout(monkeypatch):
    """A SHORT WAIT, so the absent-listbox case does not cost five seconds.

    Patched rather than lowered in the module: the production value is a
    judgement about a real network and this file has no business changing it.
    The absent-listbox test asserts the REFUSAL, not the duration, so the
    number it waits is irrelevant to what is being proved.
    """
    monkeypatch.setattr(dom, "TYPEAHEAD_TIMEOUT_MS", 400)


# ---------------------------------------------------------------------------
# It must ANSWER -- a gate that only ever refuses certifies nothing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_exactly_one_suggestion_carrying_the_needle_proceeds(over):  # noqa: F811
    found = await _gate(over, _listbox(NEEDLE, OTHER))
    assert found["proceed"] is True, found
    assert found["refused_condition"] is None
    assert found["observed"]["total"] == 2
    assert found["observed"]["matches"] == 1
    assert found["selector"] == dom.typeahead_option_selector(NEEDLE)


@pytest.mark.asyncio
async def test_the_aim_is_the_name_and_not_the_position(over):  # noqa: F811
    """THE PROPERTY THE WHOLE GATE EXISTS FOR.

    His row is drawn SECOND. A reader that took the first suggestion would
    press a stranger; one that aims by accessible name presses him. Asserted
    by resolving the gate's own selector and finding it matches exactly one
    node -- the same locator the click will use, not a re-derivation of it.
    """
    found = await _gate(over, _listbox(OTHER, NEEDLE))
    assert found["proceed"] is True, found
    assert found["observed"]["total"] == 2
    assert found["observed"]["matches"] == 1

    async def resolves_to_one(page):
        return await page.locator(found["selector"]).count()

    assert await over(_listbox(OTHER, NEEDLE), resolves_to_one) == 1


# ---------------------------------------------------------------------------
# The four refusals, each shown independently
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_listbox_that_never_appears_refuses_about_the_reader(over):  # noqa: F811
    """"It never opened" is not "he is not reachable", and the text says so."""
    found = await _gate(over, NO_LISTBOX)
    assert found["proceed"] is False
    assert found["refused_condition"] == "1_no_listbox"
    assert found["observed"]["appeared"] is False
    assert "not a statement that the person you named is not reachable" in found["why"]


@pytest.mark.asyncio
async def test_an_empty_listbox_refuses_separately_from_an_absent_one(over):  # noqa: F811
    """THE TWO ZEROES ARE DIFFERENT FACTS and collapsing them removes a test.

    An absent listbox is a fact about this reader and the page together; an
    empty one is a fact about the name he supplied. Asserted as a PAIR, since
    the whole point is that they do not share a condition code.
    """
    empty = await _gate(over, _listbox())
    assert empty["refused_condition"] == "2_no_options"
    assert empty["observed"]["appeared"] is False
    absent = await _gate(over, NO_LISTBOX)
    assert absent["refused_condition"] == "1_no_listbox"
    assert empty["refused_condition"] != absent["refused_condition"]


@pytest.mark.asyncio
async def test_suggestions_that_do_not_carry_the_needle_refuse(over):  # noqa: F811
    """A drawn dropdown of the wrong people is a refusal, not a fallback."""
    found = await _gate(over, _listbox(OTHER))
    assert found["proceed"] is False
    assert found["refused_condition"] == "3_no_option_carries_the_needle"
    assert found["observed"]["total"] == 1
    assert found["observed"]["matches"] == 0


@pytest.mark.asyncio
async def test_several_matching_suggestions_refuse_rather_than_choosing(over):  # noqa: F811
    """THE aim_invitation FAILURE, REFUSED.

    Two rows both carry the needle. Picking either would be choosing by
    position, on the action whose audience is the least recoverable here.
    """
    found = await _gate(over, _listbox(NEEDLE + " Iyer", NEEDLE + " Menon"))
    assert found["proceed"] is False
    assert found["refused_condition"] == "4_several_options_match"
    assert found["observed"]["matches"] == 2
    assert found["selector"] is None


# ---------------------------------------------------------------------------
# Nothing about anybody else leaves the gate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_other_persons_name_appears_anywhere_in_the_verdict(over):  # noqa: F811
    """THE LEAK CHECK, over the WHOLE verdict rather than a chosen field.

    The gate holds his needle -- his own input -- and must hold nothing else.
    Serialising the entire dict and searching it for the other row's name is
    the only form of this check that survives somebody adding a field.
    """
    for html in (_listbox(OTHER), _listbox(NEEDLE, OTHER), _listbox()):
        found = await _gate(over, html)
        blob = repr(found)
        assert OTHER not in blob, blob
        for part in OTHER.split():
            assert part not in blob, (part, blob)


@pytest.mark.asyncio
async def test_a_needle_that_would_break_the_selector_refuses(over):  # noqa: F811
    """REFUSED RATHER THAN ESCAPED.

    A quote in the needle would end the selector's own quoting and could aim
    the click at a different row. This server would rather not send than send
    accurately-quoted to somebody else.
    """
    found = await _gate(over, _listbox(NEEDLE), target='He said "hi"' + writes.TARGET_JOIN + "body")
    assert found["proceed"] is False
    assert found["refused_condition"] == "0_selector_unbuildable"
    assert found["selector"] is None


def test_the_selector_builder_refuses_a_quote_and_a_backslash():
    """Both characters, and the control that it accepts an ordinary name.

    Without the control this passes against a builder that refuses
    everything -- which would be a gate that can never aim at anybody.
    """
    from linkedin_server.errors import ExtractionFailedError

    for bad in ('a"b', "a" + chr(92) + "b"):
        with pytest.raises(ExtractionFailedError):
            dom.typeahead_option_selector(bad)
    assert dom.typeahead_option_selector(NEEDLE) == (
        'role=option[name="' + NEEDLE + '"i]'
    )


# ---------------------------------------------------------------------------
# The click is not its own evidence
# ---------------------------------------------------------------------------


def test_the_recipient_gate_is_still_the_authority():
    """THE ORDERING PROPERTY, asserted on the SOURCE of ``perform``.

    A proceeding typeahead gate appends a CLICK. Only the recipient gate
    appends the BODY FILL. If a future edit ever let the typeahead gate queue
    his message directly, the click would have become its own evidence and
    this file's whole argument would be gone -- so the two appends are pinned
    where they live rather than described in prose.
    """
    import inspect

    source = inspect.getsource(writes.perform)
    assert 'typeahead_gate["proceed"]' in source
    assert 'click_plan.append(typeahead_gate["selector"])' in source
    # The body fill is appended by the RECIPIENT gate and by nothing else.
    assert 'recipient_gate["proceed"]' in source
    body_append = "dom.compose_body_selector()"
    assert source.count(body_append) == 1, source.count(body_append)
    before = source.index('recipient_gate = await _recipient_gate')
    assert source.index(body_append) > before, (
        "the body fill is queued before the recipient gate has spoken"
    )


def test_the_production_caveat_about_the_option_selectors_still_stands():
    """PIN THE SENTENCE, so this file cannot quietly outlive it.

    The moment ``TYPEAHEAD_OPTION_SELECTORS`` is validated against a real
    LinkedIn typeahead, that sentence has to change -- and when it does, this
    fails and forces the docstrings above to be re-read rather than left
    asserting something that stopped being true.
    """
    import inspect

    source = inspect.getsource(dom)
    marker = "NONE OF THESE HAS EVER MATCHED ANYTHING"
    assert marker in source, (
        "the caveat has been edited or removed. If the selectors have now been "
        "validated live, update this test AND the honesty section at the top "
        "of this file -- do not delete the assertion."
    )
