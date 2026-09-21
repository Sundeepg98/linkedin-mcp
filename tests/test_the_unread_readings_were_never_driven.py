"""Three readings this package computes, DRIVEN -- two of which nothing reads.

`_audit/2026-09-21-described-never-built.md` section 4 swept `dom.py` for
readings that are measured and never consumed, reported three by name, and
fixed none of them: *"`hrefs_error`, `metrics_seen` and `pill_label` were not
fixed"*. Reporting a field as unread answers who CONSUMES it. It does not
answer what it CARRIES, and for two of the three those are different
questions with different answers.

This file drives them.

## WHY DRIVING WAS NEEDED, AND WHY NEITHER SHIPPED GUARD DID IT

Two instruments already hunt page strings in this package, and **both are
structurally unable to reach `dom.activate_messaging_filter`**. That is not a
bug in either; it is two safety properties meeting, and the gap between them
is where the only page-chosen value in this file's subject set lives.

* `tests/test_readers_emit_no_page_string.py` supplies
  `plantedpage.SYNTHETIC_ARGUMENT` for a reader's own parameters. That value
  is not in `dom.MESSAGING_FILTERS`, so `assert_permitted_filter` refuses it
  **before any locator exists**. The committed verdict in
  `tests/reader_leak_baseline.json` records the consequence honestly:
  `"dom:activate_messaging_filter": "not_driven:raises ValueError"`.
* `tests/test_tool_envelopes_emit_no_page_string.py` drives the TOOL. Its
  `build_call` skips every parameter that has a default (`if param.default is
  not param.empty: continue`), and `linkedin_open_messaging`'s signature is
  `include_names: bool = False, message_filter: str = ''` -- **both
  defaulted**. So the tool is driven with `message_filter=''`, the `if
  wanted:` branch is never entered, and `activate_messaging_filter` is never
  called at all.

The second verdict is the one worth stating plainly, because unlike the first
it ASSERTS something: `tests/tool_envelope_baseline.json` records
`"linkedin_open_messaging": "clean"`. **A tool driven down the branch on
which the field cannot exist was recorded clean.** That is the same shape
`plantedpage`'s own docstring records one level down -- *"The reader was never
driven, and 'not driven' printed as 'clean'."*

And supplying the argument does not fix it either, which is the half that
stops this being a one-line repair: `PlantedLocator.click` raises
`NavigationAttempted` by design, so a driven filter click returns an ERROR
ENVELOPE carrying no page string, and the verdict stays `clean`. The click is
`readonly.SANCTIONED_MUTATIONS[1]`, the only sanctioned click in `dom.py`.
**A reader behind a sanctioned click is unreachable by a harness whose safety
property is that it never clicks.**

So the double below allows the click as a NO-OP and changes nothing else --
every PAGE-CONTROLLED answer is still `plantedpage`'s, and `count()` still
answers Playwright's integer. Allowing the click is the whole modification,
and it is what makes this the first drive of that function's return.

## WHAT THE DRIVE SHOWED, IN ONE LINE EACH

* `hrefs_error` -- **its docstring's claim is TRUE, and now it is driven.**
  A page-chosen value in the raising exception's ARGUMENTS does NOT reach the
  field, because it stores `type(exc).__name__` and not `str(exc)`. The
  sibling `error` on the SAME function stores `f"{type(exc).__name__}: {exc}"`
  and DOES carry it -- which is this file's positive control, and the reason
  the check can fail.
* `pill_label` -- **raw page text, unshaped, published.** It reaches
  `linkedin_open_messaging`'s JSON at `active_filter.pill_label` through
  `{"requested": ..., **applied}`. Nothing redacts it, and it sits directly
  beside the two fields that WERE redacted after a real conversation
  identifier reached a transcript on 2026-09-03 (see
  `tests/test_a_thread_id_never_leaves_the_module.py`). That file guards the
  THREAD-ID class and passes correctly; a pill label is not a url, so it is
  outside the class that file checks.
* `shape.census_shape` -- **does not redact a name.** It is a character and
  length gate, which `dom.py` says twice in its own comments, and which makes
  one sentence in `dom.read_invitation_badge`'s docstring false. Pinned here
  so the sentence cannot be repaired by assertion.

## WHAT THIS FILE DOES NOT DO

It does not change a payload. `pill_label` is still published raw after this
file lands; what changes is that the SET of fields carrying page text is now
pinned, so a fourth raw field fails here instead of shipping -- which is the
class-not-instance discipline `test_a_thread_id_never_leaves_the_module.py`
states and which that file could not extend to this class without a drive.
"""

from __future__ import annotations

from typing import Any

import pytest

from linkedin_server import dom, shape
from tests.plantedpage import (
    PLANT,
    PlantedLocator,
    PlantedPage,
    carries_the_plant,
)

# ---------------------------------------------------------------------------
# 1. The doubles. One allows a click; one raises where a real page can raise.
# ---------------------------------------------------------------------------

#: The selector `read_company_about_card` harvests links with. Matching on the
#: SELECTOR rather than on a depth count is deliberate: a depth is a position,
#: and this repository has already paid for choosing by position between
#: controls that are not interchangeable.
LINK_SELECTOR = "a[href]"


class _ClickableLocator(PlantedLocator):
    """`plantedpage`'s locator with the click allowed as a NO-OP.

    NOTHING ELSE CHANGES. `get_attribute` and `inner_text` still answer
    :data:`PLANT` because the document chooses them; `count` still answers
    Playwright's integer because the document cannot.
    """

    def locator(self, *args: Any, **kwargs: Any) -> "_ClickableLocator":
        return _ClickableLocator(self._depth + 1)

    def get_by_role(self, *args: Any, **kwargs: Any) -> "_ClickableLocator":
        return _ClickableLocator(self._depth + 1)

    def nth(self, index: int) -> "_ClickableLocator":
        return _ClickableLocator(self._depth + 1)

    @property
    def first(self) -> "_ClickableLocator":
        return _ClickableLocator(self._depth + 1)

    async def click(self, **kwargs: Any) -> None:
        return None


class _ClickablePage(PlantedPage):
    """A page whose controls can be clicked. See the module docstring."""

    def locator(self, *args: Any, **kwargs: Any) -> _ClickableLocator:
        return _ClickableLocator()

    def get_by_role(self, *args: Any, **kwargs: Any) -> _ClickableLocator:
        return _ClickableLocator()

    async def wait_for_timeout(self, timeout: Any = 0) -> None:
        return None


class _RaisingLocator(PlantedLocator):
    """A locator that raises where a real Playwright locator can.

    THE EXCEPTION CARRIES A PAGE-CHOSEN VALUE IN ITS ARGUMENTS, which is the
    discriminator `ERROR-MESSAGE-RULED-AT-THE-RAISE` names: whether a page
    value entered the exception's arguments is knowable at the raise and
    unknowable at the envelope. A real Playwright timeout quotes the selector
    it was resolving, and a selector can carry page content.
    """

    def __init__(self, depth: int = 0, mode: str = "links", is_link: bool = False):
        super().__init__(depth)
        self._mode = mode
        self._is_link = is_link

    def locator(self, selector: str = "", *args: Any, **kwargs: Any):
        return _RaisingLocator(
            self._depth + 1, self._mode, is_link=(selector == LINK_SELECTOR)
        )

    def nth(self, index: int) -> "_RaisingLocator":
        return _RaisingLocator(self._depth + 1, self._mode, self._is_link)

    @property
    def first(self) -> "_RaisingLocator":
        return _RaisingLocator(self._depth + 1, self._mode, self._is_link)

    async def get_attribute(self, name: str, **kwargs: Any):
        if self._is_link and self._mode == "links":
            raise ValueError("Timeout 30000ms resolving selector %r" % PLANT)
        return await super().get_attribute(name, **kwargs)

    async def inner_text(self, **kwargs: Any):
        if self._mode == "text":
            raise ValueError("Timeout 30000ms reading %r" % PLANT)
        return await super().inner_text(**kwargs)


class _RaisingAboutPage(PlantedPage):
    def __init__(self, mode: str) -> None:
        super().__init__()
        self._mode = mode

    def locator(self, *args: Any, **kwargs: Any) -> _RaisingLocator:
        return _RaisingLocator(0, self._mode)


# ---------------------------------------------------------------------------
# 2. `hrefs_error` -- the claim is true, and the sibling proves the check works
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hrefs_error_is_null_when_the_links_were_actually_read():
    """The assertion `tests/test_job_detail_wiring.py`'s docstring CLAIMS.

    That docstring says the healthy path is *"asserted on ... links were read
    AND the error field is null"*. Its test body asserts neither -- it checks
    `company_page.hrefs` and an extraction-failed envelope. The claim was
    true of the code and false of the suite; this is the missing assertion.
    """
    out = await dom.read_company_about_card(PlantedPage())
    assert out["container"] is True, out
    assert out["hrefs"], "the healthy path must actually read links"
    assert out["hrefs_error"] is None, out
    assert out["error"] is None, out


@pytest.mark.asyncio
async def test_a_page_value_in_the_raise_does_not_reach_hrefs_error():
    """THE RAISE PATH. A returned dict is not the only way a string leaves.

    The link harvest raises with :data:`PLANT` inside the exception's own
    arguments. `hrefs_error` stores `type(exc).__name__`, so the field
    records THAT a read failed without recording WHAT the page said.
    """
    out = await dom.read_company_about_card(_RaisingAboutPage("links"))

    assert out["hrefs_error"] == "ValueError", out["hrefs_error"]
    assert out["hrefs"] == [], out["hrefs"]
    assert carries_the_plant(out["hrefs_error"]) == [], out["hrefs_error"]
    # AND THE THREE-WAY DISTINCTION THE FIELD EXISTS FOR STILL HOLDS: an
    # empty list beside a non-null marker is a FAILED read, not an empty card.
    assert out["container"] is True, out


@pytest.mark.asyncio
async def test_the_sibling_error_field_does_carry_the_page_value():
    """THE POSITIVE CONTROL, and it is why the test above can fail.

    `error` is built `f"{type(exc).__name__}: {exc}"` six lines above
    `hrefs_error`'s `type(exc).__name__`, in the same function, and the
    comment between them calls that *"a deliberate difference"*. If this
    assertion ever stops holding, the instrument above has gone blind and its
    green means nothing -- a check that cannot fail certifies nothing.
    """
    out = await dom.read_company_about_card(_RaisingAboutPage("text"))

    assert out["error"] is not None, out
    assert carries_the_plant(out["error"]) != [], out["error"]
    # The two fields are genuinely different, not two spellings of one thing.
    assert out["hrefs_error"] is None, out


# ---------------------------------------------------------------------------
# 3. `pill_label` -- driven for the first time
# ---------------------------------------------------------------------------

#: WHICH RETURNED FIELDS CARRY PAGE TEXT, as `carries_the_plant` paths. The
#: SET is pinned, not the one member: pinning `pill_label` by name would
#: protect the one field already known and none of the next one, which is the
#: exact mistake `test_a_thread_id_never_leaves_the_module.py` was written
#: about. An eighth field added raw fails here.
PAGE_TEXT_FIELDS: tuple[str, ...] = ("$.pill_label",)


@pytest.mark.asyncio
@pytest.mark.parametrize("name", dom.MESSAGING_FILTERS)
async def test_exactly_one_returned_field_carries_page_text(name: str) -> None:
    """Every permitted filter name, not one. The closed tuple is the subject.

    Driving all seven costs nothing and answers a question one would not:
    whether the carrying field depends on WHICH filter was asked for. It does
    not -- the label is read off whatever control matched, so the filter name
    selects the pill and the PAGE chooses the string.
    """
    result = await dom.activate_messaging_filter(_ClickablePage(), name)

    assert result["activated"] is True, result
    assert sorted(carries_the_plant(result)) == sorted(PAGE_TEXT_FIELDS), result


@pytest.mark.asyncio
async def test_the_pill_label_is_not_drawn_from_the_closed_tuple():
    """It is the PAGE's string, not the caller's argument.

    The locator matches `name=wanted, exact=False`, so the control's
    accessible name need only CONTAIN the permitted word -- and the label is
    then read back whole with `get_attribute`/`inner_text`. What comes back
    is the control's entire text, which is not bounded by
    `dom.MESSAGING_FILTERS` in either length or content.
    """
    result = await dom.activate_messaging_filter(_ClickablePage(), "inmail")

    assert result["filter"] == "inmail", result
    assert result["pill_label"] == PLANT, result
    assert result["pill_label"] not in dom.MESSAGING_FILTERS, result


@pytest.mark.asyncio
async def test_the_two_redacted_url_fields_are_still_redacted_beside_it():
    """THE FIELD BESIDE IT WAS FIXED AND THIS ONE WAS NOT.

    Asserted together on purpose: the point is not that `pill_label` carries
    text, it is that it carries text WHILE its neighbours are redacted at the
    source. Reading either fact alone loses the finding.
    """
    result = await dom.activate_messaging_filter(_ClickablePage(), "inmail")

    assert carries_the_plant(result["url_before"]) == [], result
    assert carries_the_plant(result["url_after"]) == [], result
    assert carries_the_plant(result["pill_label"]) != [], result


def test_the_reader_guard_cannot_supply_a_permitted_filter_name():
    """WHY THE BASELINE SAYS `not_driven`, asserted rather than narrated.

    If `SYNTHETIC_ARGUMENT` ever became a permitted filter name this would
    fail, and the baseline's `not_driven` verdict would be stale -- which is
    a thing worth being told about rather than discovering later.
    """
    from tests.plantedpage import SYNTHETIC_ARGUMENT

    assert SYNTHETIC_ARGUMENT not in dom.MESSAGING_FILTERS
    with pytest.raises(ValueError):
        dom.assert_permitted_filter(SYNTHETIC_ARGUMENT)


# ---------------------------------------------------------------------------
# 4. The premise `shape.invitation_badge` rests on
# ---------------------------------------------------------------------------


def test_census_shape_does_not_redact_a_name_shaped_string():
    """THE SENTENCE THIS REFUTES, and it is load-bearing.

    `dom.read_invitation_badge`'s docstring says the label is shaped on the
    way out *"so a nav label that one day carries a name carries it no
    further than the page."* `census_shape` is a CHARACTER AND LENGTH gate --
    `dom.py` says so twice in its own comments -- and a short plain name
    passes both gates unchanged.

    BOTH DIRECTIONS, so this is not a shaper-does-nothing test: something
    that fails the gate must still come back opaque, or a mutation that
    disabled the shaper entirely would pass.
    """
    assert shape.census_shape(PLANT) == PLANT
    # The gate is real -- it just does not catch a name.
    assert shape.census_shape("x" * 400) == shape.CENSUS_OPAQUE
    assert shape.census_shape("") == ""


def test_the_shaped_label_is_published_on_both_branches():
    """Where the unredacted label actually goes.

    `saw.shaped_label` is published by `shape.invitation_badge` on the
    success branch AND on the refusal branches, and the refusal contract
    depends on it -- `_unreadable` exists to say WHAT IT SAW, so a nav that
    did not hydrate can be told from a label whose shape changed. That is why
    the honest repair is a fork rather than a deletion.
    """
    label = shape.census_shape("%s, 3 new notifications" % PLANT)

    read = shape.invitation_badge(
        {"links": 1, "badge_links": 1, "label": label, "error": None}
    )
    assert read["state"] == "read", read
    assert read["pending"] == 3, read
    assert carries_the_plant(read) == ["$.saw.shaped_label"], read

    refused = shape.invitation_badge(
        {"links": 3, "badge_links": 0, "label": shape.census_shape(PLANT), "error": None}
    )
    assert refused["state"] == "unreadable", refused
    assert carries_the_plant(refused) == ["$.saw.shaped_label"], refused
