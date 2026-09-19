"""The gate that will not type his words until it knows WHO is in the box.

``send_message`` shipped on 2026-09-02 as the twelfth performable write, and
it is the only one of the twelve whose target is a NAMED HUMAN BEING. An
apply reaches a company's process; a post reaches an audience; a message
reaches one person, arrives in their inbox as an email as well as a
notification, and is usually read within a day. That is why the flow in
``writes.perform`` is not the obvious one, and this file exists to make the
reason legible in a place a future editor cannot skip.

THE GATE THAT WOULD HAVE BEEN WRONG
-----------------------------------
``publish_post``'s gate is: fill the composer, then check that the submit went
from DISABLED to ENABLED. That is a real observable transition and it is the
right gate for a post. **It cannot carry this action.**

"Send became enabled" answers ONE question -- does LinkedIn think this is
sendable -- and the question that matters here is a different one: is the
recipient in that box the person he named? The two come apart in exactly the
case that hurts. If the recipient typeahead commits SOMETHING on the blur that
the second fill causes, then Send goes enabled, the publish-shaped gate sees
its own evidence satisfied, and the message goes to whoever LinkedIn happened
to draw first. The gate would be right about its own claim and the message
would still reach a stranger.

So the shipped flow interposes a second gate, and its ORDERING is the safety
property rather than its existence:

  1. ``writes._live_control`` requires an EMPTY composer -- no committed
     recipient, exactly two dispatch radios with one checked, exactly one
     ``div[role=textbox]``, exactly one control named ``Send`` drawn DISABLED
     -- and hands back ``dom.compose_recipient_selector()`` as the FIRST fill
     target.
  2. Fill one: the recipient combobox gets ``_subject_component_of``.
  3. ``writes._recipient_gate`` requires EXACTLY ONE committed recipient WHOSE
     ACCESSIBLE NAME CARRIES HIS NEEDLE, compared inside the page, integers
     only coming back. It appends the body fill to ``fill_plan`` ONLY on
     proceed.
  4. Fill two: the body, addressed by role alone.
  5. ``writes._send_gate`` requires the disabled-to-enabled transition, then
     appends the click.

**His words are never typed until a recipient has been confirmed against his
needle.** A refusal at step 3 costs him a typed name sitting in a composer.
The other ordering costs him his message in a composer, or sent.

THE HONESTY REQUIREMENT -- READ THIS BEFORE TRUSTING ANYTHING BELOW
-------------------------------------------------------------------
**``dom.RECIPIENT_CHIP_SELECTORS`` HAS NEVER MATCHED ANYTHING ON A REAL
LINKEDIN PAGE.** Not one of its four candidate strings. ``dom`` says so at
length where they are defined -- "NOT ONE OF THESE HAS EVER MATCHED ANYTHING"
-- and ``test_the_production_caveat_about_the_chip_selectors_still_stands``
below pins that sentence so this file cannot quietly outlive it.

``COMPOSER_MARKUP`` and its variants are therefore drawn to match one of those
GUESSES: the committed-recipient chip here is a ``<button>`` wearing an
``aria-label`` that starts with ``Remove``, which is candidate #1 and nothing
more than a candidate. **A test whose fixture is built from the same guess as
the code under test cannot validate the guess.** Every green result below
means exactly this and no more:

    GIVEN a page that draws a committed recipient the way this fixture draws
    one, the gate's logic is correct -- it refuses zero, refuses two, refuses
    a wrong name, and proceeds on exactly one carrying his needle.

It means NOTHING about whether LinkedIn draws a committed recipient that way.
That question has exactly one answer and it is not in this repository: type a
name into the live composer and read the per-selector counts the gate's own
refusal returns. The gate is BUILT to produce that measurement -- it fails
closed, so the first live run is expected to refuse with
``1_no_recipient_committed`` and hand back four counts nobody could obtain any
other way. This file covers the logic that will consume those counts once
somebody has them. It does not stand in for them.

WHY THE FIXTURE IS EXPORTED
---------------------------
``COMPOSER_MARKUP`` is module-level and public because a second file needs an
empty composer: ``tests/test_preview_state_and_click_state.py`` drives
``_live_control`` to its success path for every action in
``writes.PERFORMABLE`` and imports each page from the module that committed it,
exactly as it imports ``SHAREBOX_MARKUP`` from
``tests/test_result_verification_block.py``. One document, one owner, no second
copy to keep in step with ``dom``'s constants.

EVERY LABEL IS READ FROM A ``dom`` CONSTANT AND NEVER TYPED TWICE, which is
``tests/test_selectors_resolve.py``'s standing convention: a renamed constant
must fail this file rather than silently produce a fixture that no longer
matches what the code aims at.

THE NAMES IN HERE ARE INVENTED, AND DELIBERATELY ODD
----------------------------------------------------
Four of them, all constructed compounds that belong to nobody. They are odd on
purpose: ``test_no_third_party_name_reaches_any_gate_result`` asserts that not
one of their eight component words appears anywhere in a JSON dump of a gate
result, and a name like ``Alex R`` would make that assertion pass by
coincidence rather than by the gate behaving. A distinctive token is what makes
a substring search evidence.

NOTHING HERE REACHES LINKEDIN OR AN ACCOUNT. Every reading is taken over frozen
markup in a local headless Chromium through
``tests/test_apply_modal_fixture.py``'s ``over`` fixture -- one browser per
test, a FRESH ISOLATED CONTEXT per reading, and ``window.innerWidth`` asserted
on every measurement so no answer is taken at an unrecorded width.
"""

from __future__ import annotations

import ast
import json
import time
from pathlib import Path

import pytest

from linkedin_server import dom, writes
from linkedin_server.writes import TARGET_JOIN, UNKNOWN, spec_for_action

# THE HARNESS, from the file that already owns it -- imported the same way
# ``tests/test_preview_state_and_click_state.py`` imports it, so there is one
# browser harness in this suite rather than three.
from tests.test_apply_modal_fixture import VIEWPORT, over  # noqa: F401
from tests.test_writes import _bare_grant, writes_on  # noqa: F401

WRITES_PY = Path(writes.__file__)
DOM_PY = Path(dom.__file__)


# ---------------------------------------------------------------------------
# The four invented people
# ---------------------------------------------------------------------------
#
# NONE OF THESE IS ANYBODY. They are constructed compounds, and the oddness is
# load-bearing rather than decorative -- see the module docstring.

#: HIM, as the composer's dispatch radios name him. On the live surface the
#: checked default reads ``<him> will send message``, which is why that reader
#: shapes labels IN THE PAGE and returns no label at all.
OPERATOR_STANDIN = "Loamwright Fennelbrace"

#: The second name in the second dispatch label, which on the live surface
#: reads ``<him> to <somebody> will send message``.
#:
#: DELIBERATELY NOT THE RECIPIENT'S NAME, even though the live label's second
#: run probably is one. The composer this fixture draws is EMPTY -- nobody is
#: committed in it -- so a mode label naming the person the grant names would
#: put the needle into the document by a route the gate never reads, and the
#: leak assertion below would no longer be able to say which route a leaked
#: token came from. Faithful in SHAPE, unambiguous in ATTRIBUTION.
MODE_LABEL_SECOND_NAME = "Bramblecourt Hollowdene"

#: WHO HE NAMED. This is the needle: ``_subject_component_of`` splits it out
#: of the canonical target and ``_recipient_gate`` hands it to the page.
NAMED_RECIPIENT = "Quillfeather Nimblewick"

#: WHO LINKEDIN DREW INSTEAD -- the whole point of the gate. A composer holding
#: this person is a composer that a count-only gate would have called ready.
SOMEBODY_ELSE = "Thistlequince Barrowmede"

#: The body. Never typed by any test here -- the recipient gate runs BEFORE the
#: body fill, which is the ordering under test -- but it has to exist, because
#: a canonical ``member_and_text`` target has two halves and
#: ``_subject_component_of`` refuses anything that is not the two-part form.
MESSAGE_BODY = "Are you hiring on the platform team this quarter?"

#: The canonical target a real grant for this action would carry.
TARGET = NAMED_RECIPIENT + TARGET_JOIN + MESSAGE_BODY

#: Every component word of every invented name, which is what the leak
#: assertion actually searches for. Split rather than matched whole because a
#: partial leak is still a leak: a gate that reported ``Quillfeather`` alone
#: would pass a whole-string check and have published a person.
INVENTED_WORDS = tuple(
    word
    for name in (
        OPERATOR_STANDIN,
        MODE_LABEL_SECOND_NAME,
        NAMED_RECIPIENT,
        SOMEBODY_ELSE,
    )
    for word in name.split()
)


# ---------------------------------------------------------------------------
# The fixture
# ---------------------------------------------------------------------------
#
# THE DISPATCH LABELS, SHAPED THE WAY THE MEASUREMENT SAYS THEY SHAPE.
#
# ``dom.COMPOSE_MODES_JS`` never returns a label. It returns how many
# capitalised runs the label carries, whether the first and last are joined by
# "to", and the name-free TAIL that survives the last run. The two live labels
# were measured to shape as:
#
#     {"runs": 1, "joined_by_to": False, "tail": "will send message"}   CHECKED
#     {"runs": 2, "joined_by_to": True,  "tail": "will send message"}
#
# -- recorded in ``tests/test_compose_fields.py`` as ``MEASURED_MODES``, which
# is where those numbers come from. The two labels below are built to shape
# into exactly that pair, and ``test_the_fixture_shapes_into_the_measured_two``
# asserts it rather than assuming it: a fixture whose radios shaped some other
# way would drive ``_live_control`` down a refusal branch while looking like it
# had reached the success one.
#
# The run rule is ``shape._NAME_SHAPE_RUN``, handed to the page as source so
# one predicate serves both engines. "Loamwright Fennelbrace" is ONE run of two
# capitalised words; the lowercase tail scores nothing; "to" between two runs is
# what sets ``joined_by_to``.
MODE_LABEL_CHECKED = OPERATOR_STANDIN + " will send message"
MODE_LABEL_UNCHECKED = (
    OPERATOR_STANDIN + " to " + MODE_LABEL_SECOND_NAME + " will send message"
)

#: THE CHIP RAIL, EMPTY. The anchor every variant below is derived from, and
#: an empty rail rather than no rail because that is what an empty composer
#: would draw -- a container with nothing committed in it, which is the state
#: whose per-selector counts are all zero.
CHIP_RAIL_EMPTY = '<div id="chip-rail"></div>'


def _chip(name: str) -> str:
    """One committed recipient, drawn AS A GUESS. Read the caveat first.

    This matches ``dom.RECIPIENT_CHIP_SELECTORS[0]`` --
    ``button[aria-label^="Remove"]`` -- and it matches it because that is the
    string this fixture was written against, NOT because LinkedIn has ever been
    observed drawing one. It has not. Not one of the four candidates has ever
    matched anything on a real page, on either branch of any test.

    The aria-label carries the name because that is the half of the guess that
    the gate's NAME MATCH depends on: ``dom.SELECTED_RECIPIENT_JS`` concatenates
    ``aria-label`` and ``textContent`` and searches the result for the needle.
    A chip that matched a selector but carried no name would exercise the count
    and not the property.

    THE INDEX IS READ FROM THE CONSTANT, never spelled here, so a reordering of
    the candidate tuple fails this file instead of leaving it aimed at whatever
    moved into position zero.
    """
    assert dom.RECIPIENT_CHIP_SELECTORS[0] == 'button[aria-label^="Remove"]', (
        "the candidate this fixture is drawn against has moved or been "
        "rewritten. This chip is a GUESS shaped to one specific string; if "
        "that string changed, the guess is now aimed at nothing and every "
        "committed-recipient case below would silently become the empty case."
    )
    return '<button aria-label="Remove ' + name + '">Remove</button>'


#: THE EMPTY COMPOSER. Public, because a second test module needs it -- see
#: the module docstring.
#:
#: WHAT ``_live_control``'s ``send_message`` arm REQUIRES OF THIS PAGE, and
#: every clause is a measured shape rather than a convenience:
#:
#:   1. ZERO committed recipients. ``dom.read_compose_fields`` refuses outright
#:      if any are present -- a composer holding a stranger is not a composer
#:      this server may read the labels of, let alone type into.
#:   2. EXACTLY TWO ``input[type=radio]``, EXACTLY ONE checked. Measured at two
#:      across 77 controls, twice. A third means the page is not the page this
#:      was built against.
#:   3. EXACTLY ONE ``div[role=textbox]``. The body carries no label this
#:      server may use, so the COUNT is its whole identification -- at any
#:      other number a fill would be aiming by document order.
#:   4. EXACTLY ONE control named ``dom.MESSAGE_SEND_NAME``, drawn DISABLED.
#:      That is what empty looks like on this surface, and an ENABLED one means
#:      something is already in the box that this server did not put there.
#:
#: THE RECIPIENT COMBOBOX IS NAMED THROUGH LABEL-FOR, not through an
#: aria-label, and that is not a stylistic choice: it is how the live surface
#: names it -- measured -- and it is the reason
#: ``dom.compose_recipient_selector`` uses the role engine at all. An
#: aria-label here would make this fixture prove the selector against a naming
#: route the real page does not use.
#:
#: THE BODY CARRIES NO LABEL OF ANY KIND -- no aria-label, no aria-labelledby,
#: no ``<label for>``, no wrapping label -- which is the point. It is addressed
#: by role alone. ``dom.read_compose_modes`` reports its ``body_name_source``
#: as ``'none'`` here, and that is asserted below rather than assumed.
COMPOSER_MARKUP = (
    "<!doctype html><html><body><main>"
    '<label for="msg-recipients">' + dom.MESSAGE_RECIPIENT_LABEL + "</label>"
    '<input id="msg-recipients" type="text" role="combobox">'
    + CHIP_RAIL_EMPTY
    + '<label for="msg-mode-a">' + MODE_LABEL_CHECKED + "</label>"
    '<input type="radio" id="msg-mode-a" name="msg-mode" checked>'
    '<label for="msg-mode-b">' + MODE_LABEL_UNCHECKED + "</label>"
    '<input type="radio" id="msg-mode-b" name="msg-mode">'
    '<div role="textbox" contenteditable="true"></div>'
    "<button disabled>" + dom.MESSAGE_SEND_NAME + "</button>"
    "</main></body></html>"
)


def _with_chips(*names: str) -> str:
    """``COMPOSER_MARKUP`` with committed recipients in its rail. DERIVED.

    THE ASSERTION IS THE POINT, and this suite has already paid for the lesson:
    a derivation anchored on a literal that stopped matching becomes a silent
    no-op, and the test built on it goes on passing while testing the base
    fixture under another name. So a derivation that cannot prove it changed
    something is refused here rather than returned.
    """
    filled = CHIP_RAIL_EMPTY.replace(
        "></div>", ">" + "".join(_chip(name) for name in names) + "</div>"
    )
    out = COMPOSER_MARKUP.replace(CHIP_RAIL_EMPTY, filled, 1)
    assert out != COMPOSER_MARKUP, (
        "the chip rail anchor changed nothing, so this variant is the empty "
        "composer wearing another name. Repoint CHIP_RAIL_EMPTY, and do NOT "
        "delete this assertion -- it is the only thing keeping every "
        "committed-recipient case below from silently becoming the empty case."
    )
    return out


#: EXACTLY ONE COMMITTED RECIPIENT, CARRYING HIS NEEDLE. The only state the
#: gate proceeds from.
COMPOSER_ONE_RIGHT = _with_chips(NAMED_RECIPIENT)

#: EXACTLY ONE COMMITTED RECIPIENT, AND IT IS SOMEBODY ELSE. **The
#: load-bearing case.** A count of one is satisfied here and the property is
#: not, which is precisely the state a publish-shaped gate would have sent
#: from.
COMPOSER_ONE_WRONG = _with_chips(SOMEBODY_ELSE)

#: TWO COMMITTED RECIPIENTS, one of them the right person -- which is the
#: realistic shape of the failure, a typeahead that committed an extra rather
#: than two strangers. The gate refuses on the count before it ever reaches the
#: name, and that ordering is asserted rather than inferred.
COMPOSER_TWO = _with_chips(NAMED_RECIPIENT, SOMEBODY_ELSE)

#: THE POST-FILL STATE: ``Send`` ENABLED. Two different readers care about this
#: page and they read it in opposite directions, which is why one variant
#: serves both:
#:
#:   ``_live_control``   BEFORE anything is typed, an enabled Send means
#:                       content is already in the box -> REFUSE
#:   ``_verify_after``   AFTER the attempt, an enabled Send means the composer
#:                       is still holding its text -> NOTHING WAS DISPATCHED
COMPOSER_SEND_ENABLED = COMPOSER_MARKUP.replace(
    "<button disabled>", "<button>", 1
)
assert COMPOSER_SEND_ENABLED != COMPOSER_MARKUP, (
    "the disabled-Send anchor changed nothing, so the enabled variant is the "
    "empty composer and both readers that consume it are being handed the "
    "wrong page."
)


# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------


def _spec():
    return spec_for_action("send_message")


def _grant(target: str = TARGET):
    """A grant built directly rather than minted.

    The same narrowing ``tests/test_writes.py`` and
    ``tests/test_preview_state_and_click_state.py`` both make and both say:
    the readers under test here consume exactly one field off a grant -- its
    ``target`` -- and driving a full preview-mint-consume chain to settle a
    question about a gate's arithmetic would put a row of unrelated gates
    between the question and the answer, each already tested where it lives.
    """
    return _bare_grant(action="send_message", target=target)


def _observation():
    """An INERT observation, for the one parameter ``_verify_after`` requires.

    ``_verify_after``'s ``send_message`` branch reads the PAGE and nothing
    else; ``observation`` is consumed only by the follow branch, which is
    guarded by its own ``spec.action`` test. This exists to satisfy the
    signature honestly rather than by passing ``None`` and relying on a branch
    ordering nobody wrote down.

    It is inert by construction: an Observation is redeemable only while its
    receipt is live in ``writes._OBSERVED``, and the only function that puts
    one there is ``writes.observe``, which loads pages.
    """
    return writes.Observation(
        target=TARGET,
        target_kind=_spec().target_kind,
        facts={},
        facts_url="",
        state=str(_spec().from_state),
        state_why="built by a test, never observed",
        state_url="",
        same_page_as_action=False,
        receipt="not-a-live-receipt",
        observed_at=time.monotonic(),
    )


async def _live(over, html: str):
    """``_live_control`` over one page. Returns ``(state, why, selector)``."""

    async def work(page):
        return await writes._live_control(page, _spec(), _grant(), "")

    # A STAR, because one arm of ``_live_control`` returns a fourth element
    # naming its mutation kind. Unpacking three positionally would break the
    # day a second arm has something to say.
    state, why, selector, *_rest = await over(html, work)
    return state, why, selector


async def _gate(over, html: str, target: str = TARGET):
    """``_recipient_gate`` over one page. Returns the verdict dict."""

    async def work(page):
        return await writes._recipient_gate(page, _grant(target))

    return await over(html, work)


async def _verify(over, html: str):
    """``_verify_after`` over one page. Returns ``(state, why, read_from)``."""

    async def work(page):
        return await writes._verify_after(
            None, page, _spec(), _grant(), _observation()
        )

    return await over(html, work)


# ---------------------------------------------------------------------------
# 0. The fixture is what it claims to be
# ---------------------------------------------------------------------------
#
# A fixture is the artefact most likely to be mistaken for evidence, so its
# claims are asserted here before anything is built on them. Every count below
# is one ``_live_control`` or one gate depends on.


async def test_the_empty_composer_draws_the_shape_every_reader_requires(over):
    """The four structural counts, plus the two selectors that must resolve.

    THIS IS THE RECEIPT FOR EVERY TEST BELOW. If the radios are miscounted or
    the recipient combobox does not resolve, ``_live_control`` takes a refusal
    branch and the success-path tests would be asserting the wrong thing while
    looking green -- which is the exact split this suite keeps finding.
    """

    async def work(page):
        return {
            "radios": int(await page.locator('input[type="radio"]').count()),
            "checked": int(
                await page.locator('input[type="radio"]:checked').count()
            ),
            "textboxes": int(
                await page.locator(dom.compose_body_selector()).count()
            ),
            "recipient": int(
                await page.locator(dom.compose_recipient_selector()).count()
            ),
            "send": int(
                await page.locator(dom.compose_send_selector()).count()
            ),
            "send_enabled": await page.locator(
                dom.compose_send_selector()
            ).first.is_enabled(),
        }

    counts = await over(COMPOSER_MARKUP, work)
    assert counts["radios"] == 2, counts
    assert counts["checked"] == 1, counts
    assert counts["textboxes"] == 1, counts
    # THE COMBOBOX RESOLVES THROUGH LABEL-FOR. A zero here means the role
    # engine did not follow the label association, and the whole
    # first-fill-target claim would be unfounded.
    assert counts["recipient"] == 1, counts
    assert counts["send"] == 1, counts
    assert counts["send_enabled"] is False, counts


async def test_the_empty_composer_holds_nothing_any_chip_candidate_can_see(over):
    """ZERO for EVERY candidate, not just for the one the fixture is drawn to.

    The gate's empty case is ``total == 0``, and ``total`` is the DE-DUPLICATED
    count across all four candidates. A stray node matching candidate three or
    four would make the empty composer read as populated, and every refusal
    below would be the wrong refusal.
    """

    async def work(page):
        return {
            selector: int(await page.locator(selector).count())
            for selector in dom.RECIPIENT_CHIP_SELECTORS
        }

    counts = await over(COMPOSER_MARKUP, work)
    assert set(counts) == set(dom.RECIPIENT_CHIP_SELECTORS)
    assert all(value == 0 for value in counts.values()), counts


async def test_the_fixture_shapes_into_the_measured_two(over):
    """The radios shape into the pair the live surface was MEASURED to produce.

    ONE capitalised run without "to", against TWO joined by it, both before the
    same name-free tail -- the numbers are ``MEASURED_MODES`` in
    ``tests/test_compose_fields.py``, which is where the live measurement is
    recorded. They are restated here rather than imported so that this file
    holds its own fixture contract; the citation is the point, not the copy.

    AND THE READER RETURNS NO LABEL, which is asserted directly: none of the
    four invented words in these two labels may appear anywhere in what
    ``read_compose_fields`` hands back. That is the property the whole in-page
    shaping design exists for, and this fixture is the one document in the
    suite whose radio labels are shaped like names on purpose.
    """
    reading = await over(COMPOSER_MARKUP, dom.read_compose_fields)
    assert "refused" not in reading, reading
    assert reading["recipients_selected"] == 0, reading

    modes = reading["modes"]
    assert len(modes) == 2, modes
    assert (modes[0]["runs"], modes[0]["joined_by_to"]) == (1, False), modes
    assert (modes[1]["runs"], modes[1]["joined_by_to"]) == (2, True), modes
    assert modes[0]["tail"] == modes[1]["tail"] == "will send message", modes
    assert [m["checked"] for m in modes] == [True, False], modes

    # THE BODY: presence and KIND, and the kind is 'none' because it carries no
    # label at all. That is what "addressed by role alone" means, made a
    # measurement instead of a claim in a comment.
    assert reading["body"]["present"] is True, reading
    assert reading["body"]["is_editable"] is True, reading
    assert reading["body"]["name_source"] == "none", reading

    dumped = json.dumps(reading)
    for word in (OPERATOR_STANDIN.split() + MODE_LABEL_SECOND_NAME.split()):
        assert word not in dumped, (
            f"{word!r} came back out of read_compose_fields. The dispatch "
            "labels are shaped IN THE PAGE precisely so that no part of them "
            "crosses into this process."
        )


# ---------------------------------------------------------------------------
# 1. The first gate: an empty composer, and the recipient as the first fill
# ---------------------------------------------------------------------------


async def test_live_control_names_the_recipient_as_the_first_fill_target(over):
    """The success path, and the field that makes it reachable.

    ``_live_control`` hands back ``composer_empty`` and the RECIPIENT selector
    -- not the body's. That is the ordering the whole design rests on: the
    first thing typed is a name, and the body's selector does not enter
    ``fill_plan`` at all until ``_recipient_gate`` has confirmed who is in the
    box.

    AND THE STATE GOES THROUGH ``click_from_state``, NOT ``from_state``, which
    is asserted in BOTH directions because that field's whole reason for
    existing is this action. ``from_state`` is ``composer_unmeasured`` and it
    is CORRECT: it describes what the PREVIEW's gate has seen, and that gate
    deliberately does not open messaging, because loading messaging redirects
    into one conversation of LinkedIn's choosing and spends a stranger's
    thread. By click time ``perform`` has navigated to the composer, so the
    click-time reading is a real reading of a real page and cannot honestly be
    called unmeasured.

    ONE FIELD CANNOT BE BOTH. Before ``click_from_state`` existed,
    ``valid_from`` compared the click-time reading against ``from_state`` --
    so this action would have refused EVERY reading it could ever take, with a
    wrong-state error. That is a gate that cannot pass rather than a gate
    refusing something, and it is the failure ``update_setting`` already had
    one field along. Asserting only that the right state passes would leave
    that regression undetectable, so the wrong one is asserted to fail too.
    """
    spec = _spec()
    state, why, selector = await _live(over, COMPOSER_MARKUP)

    assert state == "composer_empty", why
    assert selector == dom.compose_recipient_selector(), selector
    assert selector != dom.compose_body_selector(), (
        "the first fill target is the BODY, which inverts the whole design: "
        "his words would be typed before anybody confirmed who receives them."
    )

    # THE TWO FIELDS ARE GENUINELY DIFFERENT, so the assertions below are not
    # tautologies over one string.
    assert spec.click_from_state == "composer_empty", spec.click_from_state
    assert spec.from_state == "composer_unmeasured", spec.from_state
    assert spec.click_from_state != spec.from_state

    ok, refusal = writes.valid_from(spec, state, TARGET)
    assert ok is True, refusal

    # AND THE PREVIEW'S STATE IS REFUSED AT CLICK TIME, which is what proves
    # the reader consulted ``click_from_state`` rather than defaulting.
    ok, refusal = writes.valid_from(spec, str(spec.from_state), TARGET)
    assert ok is False
    assert spec.click_from_state in refusal, refusal


async def test_live_control_refuses_a_composer_whose_send_is_already_enabled(
    over,
):
    """AN ENABLED SEND ON AN UNTYPED COMPOSER MEANS SOMETHING IS IN THE BOX.

    ``Send`` is measured DISABLED while the composer is empty, so an enabled
    one is content this server did not put there and cannot read back -- most
    likely a draft LinkedIn restored, most likely his. A fill REPLACES, and
    replacing a draft he wrote is a side effect he did not ask for.

    THE SELECTOR MUST BE EMPTY, and that is the half worth asserting. A refusal
    that still handed back a fill target would be a refusal in the ``why`` and
    a permission in the return value, and ``perform`` consumes the return
    value.
    """
    state, why, selector = await _live(over, COMPOSER_SEND_ENABLED)
    assert state == UNKNOWN, (state, why)
    assert selector == "", selector
    assert "already ENABLED" in why, why


# ---------------------------------------------------------------------------
# 2. The recipient gate -- the reason this action's flow is not the obvious one
# ---------------------------------------------------------------------------


async def test_the_gate_refuses_when_nothing_is_committed_and_the_counts_are_the_answer(
    over,
):
    """THE EXPECTED FIRST RESULT ON A LIVE RUN, and it is an INSTRUMENT.

    Nobody has ever typed into that combobox through this server, so nobody
    knows whether a bare fill commits a recipient at all -- and the four
    candidate selectors that would find a committed one have never matched
    anything anywhere. This refusal is how that gets measured: it reports a
    count PER CANDIDATE, so a human reading the block can tell "there is nobody
    here" from "none of my selectors is how LinkedIn draws one". On this
    surface those two answers are the difference between refusing and sending.

    THE PER-SELECTOR SHAPE IS ASSERTED AS A SET, not by index. A refusal that
    reported three of four counts would look identical in a passing test that
    only checked the first, and the missing one might be the candidate that
    would have matched.
    """
    verdict = await _gate(over, COMPOSER_MARKUP)

    assert verdict["proceed"] is False
    assert verdict["refused_condition"] == "1_no_recipient_committed", verdict

    observed = verdict["observed"]
    assert set(observed["per_selector"]) == set(dom.RECIPIENT_CHIP_SELECTORS), (
        "a candidate went uncounted. The counts ARE the measurement this "
        "refusal exists to produce, and a partial set of them is a partial "
        "measurement presented as a whole one."
    )
    assert all(int(v) == 0 for v in observed["per_selector"].values()), observed
    assert observed["total"] == 0, observed
    assert observed["matches"] == 0, observed
    assert list(observed["selectors_tried"]) == list(
        dom.RECIPIENT_CHIP_SELECTORS
    ), observed

    # THE WHY SAYS THE COUNTS ARE THE MEASUREMENT. Pinned because a refusal
    # that reported numbers without saying what they are for would be read as
    # a malfunction and the one measurement nobody can otherwise take would be
    # thrown away by whoever read it.
    why = verdict["why"]
    assert "IT IS THE MEASUREMENT" in why, why
    assert "per-selector counts" in why, why


async def test_the_gate_refuses_one_committed_recipient_who_is_not_the_person_named(
    over,
):
    """**THE LOAD-BEARING CASE. A COUNT OF ONE IS NOT THE PROPERTY.**

    This is the state a ``publish_post``-shaped gate would have SENT from:
    exactly one recipient committed, Send would go enabled, everything looks
    ready -- and the person in the box is not the person he named. The
    typeahead committed whoever LinkedIn drew first, on the blur that the
    second fill would have caused, and the gate's own evidence would have been
    satisfied by exactly the thing that is wrong.

    The refusal is on the NAME, and the comparison ran inside the page. What
    comes back is ``matches: 0`` against ``total: 1`` -- two integers that say
    "somebody is here and it is not who you meant" without either process ever
    holding the stranger's name.
    """
    verdict = await _gate(over, COMPOSER_ONE_WRONG)

    assert verdict["proceed"] is False
    assert verdict["refused_condition"] == "3_needle_does_not_match", verdict
    observed = verdict["observed"]
    assert observed["total"] == 1, observed
    assert observed["matches"] == 0, observed
    # THE CHIP WAS SEEN. Without this the case is indistinguishable from a
    # fixture whose chip matched nothing, which would make this test pass for
    # the wrong reason -- the one failure mode a guessed selector guarantees.
    assert observed["per_selector"][dom.RECIPIENT_CHIP_SELECTORS[0]] == 1, observed

    why = verdict["why"]
    assert "THE COUNT IS NOT THE PROPERTY" in why, why


async def test_the_gate_refuses_two_committed_recipients_before_it_looks_at_names(
    over,
):
    """Several recipients is not a state this gate acts from.

    THE ORDERING IS ASSERTED, not just the refusal. One of the two chips here
    DOES carry his needle -- which is the realistic shape of the failure, a
    typeahead that committed an extra rather than two strangers -- so a gate
    that checked the name first would find its match and proceed, sending to
    both. The count check has to run first, and the way to show it did is that
    ``matches`` is 1 while the verdict is the several-recipients refusal.
    """
    verdict = await _gate(over, COMPOSER_TWO)

    assert verdict["proceed"] is False
    assert verdict["refused_condition"] == "2_several_recipients", verdict
    observed = verdict["observed"]
    assert observed["total"] == 2, observed
    assert observed["matches"] == 1, (
        "the fixture's two chips no longer include the named recipient, so "
        "this case has stopped testing the ordering it was written for: it "
        "would now be refused by the name check as well and the two checks "
        "would be indistinguishable."
    )


async def test_the_gate_proceeds_on_exactly_one_chip_carrying_his_needle(over):
    """THE ONLY WAY THROUGH, and it is narrow by construction.

    A chip that exists but carries the wrong name reads zero matches and
    refuses. A selector that matches nothing reads zero total and refuses. The
    only state that proceeds is one committed recipient whose accessible name
    carries the needle -- and even here, what the gate has established is
    ADDRESSING, not sendability. Sendability is the next gate's claim.

    AND THIS IS WHERE THE MODULE'S CAVEAT BITES HARDEST. This test says the
    gate's logic is right GIVEN a chip drawn the way this fixture draws one. It
    does not say LinkedIn draws one that way. Nothing in this repository can
    say that.
    """
    verdict = await _gate(over, COMPOSER_ONE_RIGHT)

    assert verdict["proceed"] is True, verdict
    assert verdict["refused_condition"] is None, verdict
    observed = verdict["observed"]
    assert observed["total"] == 1, observed
    assert observed["matches"] == 1, observed

    why = verdict["why"]
    assert "compared INSIDE the page" in why, why
    assert "The body may now be typed." in why, why


async def test_the_wrong_person_page_proceeds_for_the_needle_it_does_carry(over):
    """THE CONTROL FOR THE LOAD-BEARING CASE. Same page, the other needle.

    Without this, the refusal above is ambiguous in the one way that matters
    for a guessed selector: ``matches: 0`` is what a page with the wrong person
    in it returns, and it is ALSO what a page whose chip no candidate could see
    would return. One of those is the gate working and the other is the fixture
    being invisible, and ``total: 1`` is the only thing separating them.

    So the same document is driven again with the needle that IS in it, and it
    proceeds. That makes the pair a genuine discrimination: the page is
    readable, the chip is seen, and the ONLY variable between refusing and
    proceeding is whether the committed name is the one he supplied. Which is
    the property, stated as an experiment rather than as an assertion about one
    reading.
    """
    verdict = await _gate(
        over, COMPOSER_ONE_WRONG, target=SOMEBODY_ELSE + TARGET_JOIN + MESSAGE_BODY
    )
    assert verdict["proceed"] is True, verdict
    assert verdict["observed"]["total"] == 1, verdict
    assert verdict["observed"]["matches"] == 1, verdict


# ---------------------------------------------------------------------------
# 3. No name leaks, on any branch
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "label,html",
    [
        ("empty", COMPOSER_MARKUP),
        ("one right", COMPOSER_ONE_RIGHT),
        ("one wrong", COMPOSER_ONE_WRONG),
        ("two", COMPOSER_TWO),
    ],
)
async def test_no_third_party_name_reaches_any_gate_result(over, label, html):
    """INTEGERS COME OUT. NAMES DO NOT -- on the proceeding branch too.

    A committed recipient IS a third party by definition, so any label read in
    that composer names somebody who is not him. A name that reaches Python can
    reach a traceback, a log line, a cache key or an audit file, and no care
    downstream un-rings that. So the needle goes IN and only counts come back.

    THE REFUSING BRANCHES MATTER MOST. A refusal that quotes what it refused is
    the leak wearing an apology, and it is the single most tempting thing to
    write when a gate has to explain itself -- "exactly one recipient is
    committed and it is X, not Y" is a better error message and a disclosure.
    The shipped ``why`` says so in as many words and reports nothing.

    THE PROCEEDING BRANCH IS INCLUDED DELIBERATELY. It is the one case where
    the gate has confirmed the name matches, which is exactly when echoing it
    back would feel harmless.

    SEARCHED BY COMPONENT WORD, both cased and lowercased. A whole-name check
    would pass on a result that leaked half of one, and the in-page comparison
    lowercases its inputs, so a leak arriving from that path would arrive in
    lower case.
    """
    verdict = await _gate(over, html)
    dumped = json.dumps(verdict)
    lowered = dumped.lower()
    for word in INVENTED_WORDS:
        assert word not in dumped, (
            f"[{label}] {word!r} appears in the gate's own verdict. That is a "
            "third party's name in a structure that gets returned, logged and "
            "written into a receipt."
        )
        assert word.lower() not in lowered, (
            f"[{label}] {word!r} appears lowercased in the gate's verdict, "
            "which is the shape the in-page comparison works in -- so this is "
            "a leak arriving straight off the match path."
        )
    # AND THE BODY OF HIS MESSAGE IS NOT IN THERE EITHER. It is never typed on
    # a refusing branch, but it IS on the grant this gate is handed, one field
    # away from the needle it does read.
    assert MESSAGE_BODY not in dumped, dumped


# ---------------------------------------------------------------------------
# 4. Verification: the negative is provable, the positive is not
# ---------------------------------------------------------------------------


async def test_verify_after_reports_the_composer_still_holding_its_text(over):
    """THE STRONGEST STATEMENT THIS ACTION CAN MAKE, AND IT IS A NEGATIVE ONE.

    ``send_message`` cannot prove it happened. There is no surface that could:
    the composer carries no countable total, and the only thing that could
    confirm a send is the thread -- which is forbidden here AND costs a read
    receipt on a real person.

    But proving it did NOT happen was never blocked by that. ``perform``
    compares the verified state against ``expected_after`` for True and against
    ``not_performed_state`` for False, falling to UNKNOWN between them. A
    composer still on screen with Send still ENABLED is what a composer holding
    its content looks like, and reading that turns the worst answer into the
    second best.

    AND WHAT MAKES IT ADMISSIBLE is what disqualified the alternative,
    inverted. A "composer cleared means sent" rule could only be validated BY
    SENDING, and a verification you can only validate by performing the
    irreversible thing is not a verification. The negative direction needs no
    such thing: fill the composer, do not send, and observe what UNCHANGED
    looks like. That is a read, and it is this one.
    """
    spec = _spec()
    state, why, read_from = await _verify(over, COMPOSER_SEND_ENABLED)

    assert state == "composer_holds_text", (state, why)
    assert state == spec.not_performed_state, (state, spec.not_performed_state)
    assert "NOTHING WAS DISPATCHED" in why, why
    # NO SECOND SURFACE WAS READ, and the empty string says so. This branch
    # re-reads the page already in front of it; a url here would be claiming a
    # navigation that did not happen.
    assert read_from == "", read_from


async def test_verify_after_will_not_read_a_cleared_composer_as_sent(over):
    """A CLEARED COMPOSER AND ONE THAT NEVER GOT THE TEXT LOOK IDENTICAL.

    So the disabled-Send reading is UNKNOWN, not success. This is the branch
    where the temptation is largest and the evidence is weakest: the click has
    already happened, the composer looks empty, and calling that "sent" would
    be the single most useful-sounding sentence this server could print. It is
    also unfalsifiable from here.
    """
    state, why, read_from = await _verify(over, COMPOSER_MARKUP)

    assert state == UNKNOWN, (state, why)
    assert "will NOT read that as 'sent'" in why, why
    assert "Open your messages and look." in why, why
    assert read_from == "", read_from


async def test_verify_after_can_never_return_the_to_state(over):
    """``message_sent`` IS UNREACHABLE BY CONSTRUCTION, proven two ways.

    ``expected_after`` is ``to_state`` and ``verified_state`` initialises to
    UNKNOWN, so with no surface writing that state the True arm cannot be
    entered. This action can be shown NOT to have happened and cannot be shown
    to have happened, and that asymmetry is the design rather than a gap
    somebody will close later.

    TWO PROOFS, BECAUSE THE BEHAVIOURAL ONE ALONE IS WEAK. Driving both
    readings shows the two reachable answers are not ``to_state``; it cannot
    show a third reading does not exist. So the branch's own source is read:
    every string constant inside ``_verify_after``'s ``send_message`` arm is
    collected off the AST and ``to_state`` is asserted absent from it. A future
    edit that adds a "sent" return has to argue with this test.
    """
    spec = _spec()
    assert spec.to_state == "message_sent", spec.to_state

    for html in (COMPOSER_MARKUP, COMPOSER_SEND_ENABLED):
        state, why, _read_from = await _verify(over, html)
        assert state != spec.to_state, (state, why)

    literals = _string_constants_in_the_send_message_arm("_verify_after")
    assert literals, (
        "no string constants were found in _verify_after's send_message arm, "
        "which means the arm was not located -- this check is passing "
        "vacuously and proves nothing."
    )
    assert spec.to_state not in literals, (
        f"{spec.to_state!r} is now a literal inside _verify_after's "
        "send_message arm, so the True arm may have become reachable. That is "
        "a claim this action cannot support: nothing this server can read "
        "distinguishes a sent message from a composer that never received the "
        "text."
    )


def _string_constants_in_the_send_message_arm(function: str) -> set[str]:
    """Every string literal inside ``if spec.action == "send_message":``.

    Located by AST rather than by a text search, so a docstring elsewhere in
    the file mentioning the action cannot be mistaken for the branch, and so
    that reformatting the source cannot silently empty the result -- an empty
    result is asserted against by the caller for exactly that reason.
    """
    tree = ast.parse(WRITES_PY.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != function:
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.If):
                continue
            test = inner.test
            if not isinstance(test, ast.Compare) or len(test.comparators) != 1:
                continue
            right = test.comparators[0]
            if not isinstance(right, ast.Constant) or right.value != "send_message":
                continue
            for leaf in ast.walk(inner):
                if isinstance(leaf, ast.Constant) and isinstance(leaf.value, str):
                    found.add(leaf.value)
    return found


# ---------------------------------------------------------------------------
# 5. The caveat this whole file rests on, pinned
# ---------------------------------------------------------------------------


def test_the_production_caveat_about_the_chip_selectors_still_stands():
    """THE SENTENCE THAT MAKES EVERY GREEN RESULT ABOVE HONEST.

    ``dom`` states, where the candidates are defined, that not one of them has
    ever matched anything on a real page. Every committed-recipient test in
    this file draws a chip to match candidate #1, so if that sentence were ever
    softened -- by somebody who saw a suite full of passing chip tests and
    concluded the selectors were validated -- this file would become the
    evidence for a claim it cannot support.

    So the sentence is pinned. Softening it has to be a deliberate act that
    breaks a test, and the only thing that legitimately retires it is a LIVE
    reading in which one of those candidates counted something.
    """
    source = DOM_PY.read_text(encoding="utf-8")
    assert "NOT ONE OF THESE HAS EVER MATCHED ANYTHING" in source, (
        "linkedin_server/dom.py no longer states that the recipient-chip "
        "selectors have never matched anything. If a live reading retired "
        "that caveat, say so where the candidates are defined AND rewrite "
        "this module's docstring -- it currently tells the reader that every "
        "committed-recipient result in this file is conditional on a guess."
    )
    assert "RECIPIENT_CHIP_SELECTORS" in source


def test_this_module_says_out_loud_what_its_fixture_cannot_prove():
    """THE DOCSTRING IS PART OF THE INSTRUMENT, so it is asserted like one.

    A file that proves a gate's logic over a fixture built from the same guess
    as the code under test is worth having. A file that READS as though it had
    validated the guess is worse than nothing -- it manufactures confidence at
    exactly the point where none exists. The difference between the two is
    entirely in the prose, which is why the prose is pinned here rather than
    trusted to survive an edit.
    """
    doc = __doc__ or ""
    assert "NEVER MATCHED ANYTHING" in doc, doc
    assert "cannot validate the guess" in doc, doc
    assert "It means NOTHING about whether LinkedIn draws" in doc, doc
