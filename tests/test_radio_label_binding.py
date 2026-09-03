"""A LABEL THAT NAMES A RADIO IS NOT A LABEL THAT SETS ONE.

``update_setting`` aims at a ``<label>`` matched by its text, because the real
``<input>`` is covered by a decorative div and cannot be clicked -- measured on
2026-09-03, when the first end-to-end write came back ``clicks_made: 0`` after
23 intercepted retries.

**MATCHING A LABEL BY TEXT IS A NAMING RELATION.** What makes a click on a
label move a radio is a ``<label for=X>`` binding to the control with id ``X``,
which is an ACTIVATION relation. The two look identical on a page and only one
of them does anything.

THIS FILE EXISTS BECAUSE CONFUSING THEM COST A ROUND, AND THE CONFUSION WENT
THE OTHER WAY FIRST. ``linkedin_surface_census`` reports
``name_source: "aria-labelledby"`` for these radios. That was read as proving
no ``label-for`` binding exists -- and a direct ``label[for=...]`` query counts
ONE. The census's ``nameOf`` checks ``aria-labelledby`` BEFORE it checks
``label-for``, so once the first resolves the second is never consulted:
**``name_source`` reports which resolver produced the name, not which relations
exist in the DOM.** The inference was about the instrument and was stated as a
fact about the page.

So ``dom.read_radio_label_binding`` reads the relation instead of inferring it,
and the tests below are its controls. The one that matters is
``test_a_label_that_names_but_does_not_activate_is_refused``: that page passes
every actionability check and sets nothing, which is the failure that looks
like success.

NOTHING HERE REACHES LINKEDIN. Hand-written markup in a local headless
Chromium, and the settings page carries no third party -- the three control
names are ``Always off``, ``Always on`` and ``Device settings``.
"""

from __future__ import annotations

from linkedin_server import dom

from tests.test_apply_modal_fixture import VIEWPORT, over  # noqa: F401

NAME = "Always on"
OTHER = "Always off"


def _row(
    *,
    input_id: str = "theme__dark",
    label_for: str | None = "theme__dark",
    text: str = NAME,
    covered: bool = True,
) -> str:
    """One settings radio, drawn the way the live page draws it.

    THE COVERING DIV IS IN BY DEFAULT. Without it the fixture does not carry
    the defect the label aim exists to route around, and a page that cannot
    reproduce the bug cannot demonstrate the fix.

    ``label_for=None`` draws the trap: a label that NAMES the control and is
    bound to nothing.
    """
    binding = "" if label_for is None else ' for="' + label_for + '"'
    cover = '<div class="setting-radio__button"></div>' if covered else ""
    return (
        '<div class="setting-radio">'
        '<input name="theme" type="radio" id="' + input_id + '"'
        ' aria-labelledby="' + input_id + '__label">'
        + cover
        + "<label" + binding + ' id="' + input_id + '__label">' + text + "</label>"
        "</div>"
    )


#: THE STYLE THAT MAKES THE COVER A COVER.
#:
#: WITHOUT IT THIS FILE PROVES NOTHING, and the first version did not have it.
#: A bare ``<div>`` after an ``<input>`` sits BELOW it in the layout and
#: intercepts nothing, so the input stayed perfectly clickable and
#: ``test_the_input_really_is_unclickable_on_this_fixture`` reported CLICKABLE
#: -- which is the control doing its job on my own fixture. Interception is a
#: LAYOUT fact, not a markup fact, so reproducing it needs the positioning that
#: creates the overlap.
COVER_STYLE = (
    "<style>"
    ".setting-radio{position:relative;display:block;width:220px;height:32px}"
    ".setting-radio input{position:absolute;left:0;top:0;width:24px;height:24px}"
    ".setting-radio__button{position:absolute;left:0;top:0;"
    "width:24px;height:24px;background:#ccc}"
    ".setting-radio label{position:absolute;left:32px;top:0}"
    "</style>"
)


def _page(*rows: str) -> str:
    return (
        "<!doctype html><html><body>"
        + COVER_STYLE
        + "<main>"
        + "".join(rows)
        + "</main></body></html>"
    )


async def _binding(over, html: str, name: str = NAME) -> dict:  # noqa: F811
    async def work(page):
        return await dom.read_radio_label_binding(page, "radio", name)

    return await over(html, work)


# ---------------------------------------------------------------------------
# The state the live page is in
# ---------------------------------------------------------------------------


async def test_a_properly_bound_label_verifies(over):  # noqa: F811
    """THE LIVE SHAPE. Measured on all three radios on 2026-09-03.

    This is the positive case and it goes first, because a file of refusals
    passes perfectly against a reader that refuses unconditionally.
    """
    found = await _binding(over, _page(_row()))
    assert found["bound"] is True, found
    assert found["observed"]["controls_named"] == 1
    assert found["observed"]["input_id"] == "theme__dark"
    assert found["observed"]["labels_matching"] == 1
    assert found["observed"]["label_for"] == "theme__dark"
    assert "ACTIVATION relation" in found["why"]


async def test_the_input_really_is_unclickable_on_this_fixture(over):  # noqa: F811
    """THE DEFECT THE AIM ROUTES AROUND, reproduced.

    Without this the fixture would be proving the label aim against a page
    where the input was clickable all along, and the whole change would rest
    on a live error message nobody could re-run.

    A TRIAL CLICK PERFORMS NOTHING -- it runs the actionability checks and
    skips the action -- so this reproduces the interception without pressing
    anything.
    """

    async def work(page):
        radio = page.locator(dom.named_role_selector("radio", NAME))
        assert await radio.count() == 1
        try:
            await radio.click(trial=True, timeout=1_000)
            return "CLICKABLE"
        except Exception as exc:  # noqa: BLE001 - the refusal is the reading
            # THE WHOLE MESSAGE, NOT A SLICE. The first version cut it at
            # 200 characters and the interception line sits further down
            # Playwright's call log, so the test read 'TimeoutError' with
            # no reason and failed on its own truncation rather than on
            # the page. A control that cannot see the evidence it asserts
            # on reports the wrong thing.
            return type(exc).__name__ + "|" + str(exc).replace(chr(10), " ")

    verdict = await over(_page(_row()), work)
    assert verdict != "CLICKABLE", (
        "the covered input is clickable on this fixture, so this page does "
        "not carry the defect the label aim exists for and every other test "
        "in this file is proving something about a page LinkedIn does not draw"
    )
    assert "intercepts pointer events" in verdict, verdict[:400]
    assert "setting-radio__button" in verdict, verdict[:400]


# ---------------------------------------------------------------------------
# The controls. Each one is a page that would click cleanly and be wrong
# ---------------------------------------------------------------------------


async def test_a_label_that_names_but_does_not_activate_is_refused(over):  # noqa: F811
    """**THE FAILURE THAT LOOKS LIKE SUCCESS, AND THE REASON THIS READER
    EXISTS.**

    A label carrying the right text with NO ``for`` attribute. It is visible,
    enabled, stable and perfectly clickable -- a trial click passes -- and
    clicking it moves nothing, because naming a control is not activating one.

    Aiming by text alone cannot tell this page from the one above. That is the
    entire argument for reading the binding.
    """
    found = await _binding(over, _page(_row(label_for=None)))
    assert found["bound"] is False, found
    assert found["observed"]["labels_matching"] == 1
    assert found["observed"]["label_for"] is None
    assert "clicks cleanly and sets nothing" in found["why"], found["why"]


async def test_a_label_bound_to_a_different_control_is_refused(over):  # noqa: F811
    """WORSE THAN CLICKING NOTHING: clicking somebody else's radio.

    The label says ``Always on`` and its ``for`` points at the OTHER input. A
    text aim presses it and the wrong setting changes -- and the verification
    would then correctly report the destination unchanged, sending a reader
    hunting for a verification bug that does not exist.
    """
    html = _page(
        _row(input_id="theme__dark", label_for="theme__light"),
        _row(input_id="theme__light", label_for="theme__light", text=OTHER),
    )
    found = await _binding(over, html)
    assert found["bound"] is False, found
    assert found["observed"]["input_id"] == "theme__dark"
    assert found["observed"]["label_for"] == "theme__light"
    assert "sets somebody else's radio" in found["why"], found["why"]


async def test_two_labels_with_the_same_text_are_refused(over):  # noqa: F811
    """Two labels carrying the same text and pressing either is a coin toss.

    The builder's selector matches both. Choosing one would be choosing by
    document order, which is the thing this package refuses everywhere else.
    """
    # ONE control carrying the name, TWO labels carrying the text. The second
    # label is bare -- no input of its own -- so the reader reaches the label
    # count instead of refusing at the control count.
    #
    # THE FIRST VERSION OF THIS TEST DREW TWO FULL ROWS and refused at clause
    # 1 with controls_named 2, which is a correct refusal for the WRONG
    # reason: it proved the name check works and said nothing about the label
    # check. A control that fires on the clause before the one it is aimed at
    # is a control that has not been shown to work.
    html = _page(
        _row(input_id="theme__dark"),
        '<label for="theme__other">' + NAME + "</label>",
    )
    found = await _binding(over, html)
    assert found["bound"] is False, found
    assert found["observed"]["controls_named"] == 1, found["observed"]
    assert found["observed"]["labels_matching"] == 2, found["observed"]
    assert "picking by position" in found["why"], found["why"]


async def test_a_name_that_matches_no_control_is_refused(over):  # noqa: F811
    """Zero controls with that name is a page that had not arrived."""
    found = await _binding(over, _page(_row()), name="Device settings")
    assert found["bound"] is False, found
    assert found["observed"]["controls_named"] == 0, found["observed"]


async def test_a_control_with_no_id_is_refused(over):  # noqa: F811
    """No id means no ``for`` can point at it, so there is nothing to verify.

    Refused rather than waved through: a reader that returned True when it
    could not check would be worse than no reader, because its True would be
    read as a verified binding.
    """
    html = _page(
        '<div class="setting-radio">'
        '<input name="theme" type="radio" aria-label="' + NAME + '">'
        '<div class="setting-radio__button"></div>'
        "<label>" + NAME + "</label>"
        "</div>"
    )
    found = await _binding(over, html)
    assert found["bound"] is False, found
    assert found["observed"]["input_id"] in (None, "")
    assert "no id" in found["why"], found["why"]


# ---------------------------------------------------------------------------
# And the wiring
# ---------------------------------------------------------------------------


def test_the_aiming_arm_refuses_when_the_binding_does_not_verify():
    """THE READER IS CALLED, AND ITS ANSWER GATES THE SELECTOR.

    A reader that is correct and unreached is the defect this repository has
    spent the week removing, so the wiring is asserted rather than assumed --
    off the source of the function that does the aiming.
    """
    import inspect

    from linkedin_server import writes

    source = inspect.getsource(writes._live_control)
    assert "read_radio_label_binding" in source
    # The selector is returned only past the check: the refusal branch comes
    # first and returns an empty target.
    check = source.index("read_radio_label_binding")
    aim = source.index("settings_radio_label_selector(anchor)")
    assert check < aim, (
        "the selector is built before the binding is verified, so a page that "
        "fails the check would still hand back a click target"
    )
