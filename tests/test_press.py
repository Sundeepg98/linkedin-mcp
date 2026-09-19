"""THE DISCLOSING-PRESS GATE, tested without pressing anything.

The ruling's own last line is that nobody presses anything until the mechanism
exists, *including to test it*. So every test here runs against a FIXTURE
STRING or a FAKE PAGE. No browser is opened, no live control is touched, and
the fake records what it was handed so the tests can assert that a refused
press touches NOTHING rather than merely returning a refusal afterwards.

That distinction is the whole difference between a guard and a report, and it
is asserted directly: :class:`FakePage` counts clicks.
"""
from __future__ import annotations

import inspect

import pytest

from linkedin_server import press, readonly

BASE = "https://www.linkedin.com"


class FakeLocator:
    def __init__(self, page, selector, expanded=("false", "false")):
        self.page = page
        self.selector = selector
        self._expanded = list(expanded)
        self._reads = 0

    def nth(self, _index):
        return self

    async def count(self):
        return self.page.control_count

    async def get_attribute(self, name):
        assert name == "aria-expanded", name
        value = self._expanded[min(self._reads, len(self._expanded) - 1)]
        self._reads += 1
        return value

    async def click(self, **_kwargs):
        self.page.clicks.append(self.selector)


class FakeKeyboard:
    def __init__(self, page):
        self.page = page

    async def press(self, key):
        self.page.keys.append(key)


class FakePage:
    """Records everything. The assertions that matter are about what it did NOT
    receive."""

    def __init__(self, url, control_count=1, expanded=("false", "false")):
        self.url = url
        self.control_count = control_count
        self.clicks: list[str] = []
        self.keys: list[str] = []
        self.selectors: list[str] = []
        self.keyboard = FakeKeyboard(self)
        self._expanded = expanded

    def locator(self, selector):
        self.selectors.append(selector)
        return FakeLocator(self, selector, self._expanded)


async def _counters(values=(0, 0)):
    return {"invitations": values[0], "messaging": values[1]}


# ---------------------------------------------------------------------------
# CONDITION 2 -- the enumerated shape list, SHOWN REFUSING off-list shapes
# ---------------------------------------------------------------------------

OFF_LIST_SHAPES = [
    "button",                                   # the family wildcard
    "a",
    "[role=button]",
    "[role=menuitem]",
    '[aria-label*="All filters" i]',            # a real probe's real selector
    'button:has-text("All filters")',           # ditto, text-based
    "text=Delete",
    "[onclick]",
    "[data-test-id]",
    ".artdeco-dropdown__trigger",
    "*",
    "",
    None,
]


@pytest.mark.parametrize("shape", OFF_LIST_SHAPES)
def test_every_off_list_shape_is_refused(shape):
    """SHOWN FAILING ON AN OFF-LIST SHAPE, which the ruling requires by name.

    The two label-based entries are not invented: they are the selectors a
    probe really used to press a live control today --
    ``button[aria-label*="All filters" i]`` and ``button:has-text(...)``. The
    wave that wrote them scored its own press against these conditions and
    reported one of four. This gate refuses that selection outright.
    """
    verdict = press.evaluate(url=f"{BASE}/feed/", shape=shape)
    assert verdict["refused"] == "shape_not_sanctioned", verdict
    assert verdict["reachable_by_this_route"] is False


def test_the_sanctioned_shapes_are_attributes_and_never_text():
    """Condition 2 is 'by attribute, never by label'. Asserted structurally.

    A shape that selected on text would let page text into a decision, which is
    the one route this server does not take.
    """
    assert press.SANCTIONED_SHAPES, "the shape list is empty"
    for shape in press.SANCTIONED_SHAPES:
        assert shape.startswith("[") and shape.endswith("]"), shape
        assert "aria-" in shape, shape
        for banned in ("has-text", "text=", ":text", "aria-label", "title"):
            assert banned not in shape, (
                f"{shape!r} selects on text. Condition 2 admits attributes "
                "that DECLARE a disclosure, never anything carrying a label."
            )


def test_the_shape_list_is_exactly_the_two_the_ruling_named():
    """The list grows only by a further ruling. This is what makes a widening
    show up in a diff rather than in an incident."""
    assert set(press.SANCTIONED_SHAPES) == {"[aria-expanded]", "[aria-haspopup]"}


def test_a_listener_presence_matcher_is_not_in_the_list():
    """The wired-but-undeclared case is refused, DELIBERATELY.

    Measured by another wave: the contact-info control carries neither
    attribute but does carry a click listener. Matching on listener presence
    would admit nearly every interactive node on the page -- the family
    wildcard condition 2 exists to forbid.
    """
    for shape in press.SANCTIONED_SHAPES:
        assert "onclick" not in shape and "listener" not in shape


# ---------------------------------------------------------------------------
# CONDITION 1 -- the address, and the refusals that outrank it
# ---------------------------------------------------------------------------

def test_a_refused_address_refuses_every_control_on_it():
    verdict = press.evaluate(url=f"{BASE}/pulse/drafts/", shape="[aria-expanded]")
    assert verdict["refused"] == "address_not_admitted"
    assert verdict["reachable_by_this_route"] is False


def test_a_composer_is_refused_even_though_it_is_admitted_for_reading():
    """THE AUTOSAVE CLASS, and the point is the FIRST assertion.

    `/article/new/` passes ``is_read_url``. It is still refused for pressing,
    which is what makes the press allowlist a strict subset of the read
    allowlist rather than a synonym for it.
    """
    assert readonly.is_read_url(f"{BASE}/article/new/") is True
    verdict = press.evaluate(url=f"{BASE}/article/new/", shape="[aria-expanded]")
    assert verdict["refused"] == "composer_or_editor"
    assert verdict["reachable_by_this_route"] is False


def test_his_own_profile_is_permitted_and_a_third_party_is_not():
    """The self/third-party split, with both sides asserted.

    The third-party case is refused twice over -- the allowlist does not admit
    it either -- and that is defence in depth rather than redundancy: the
    address check would stop enforcing this the day somebody admits a
    third-party read.
    """
    mine = press.evaluate(url=f"{BASE}/in/me/", shape="[aria-haspopup]")
    assert mine.get("permitted_to_attempt") is True
    # ``another-person`` rather than an invented slug: it is a member of
    # ``test_no_committed_identity.SYNTHETIC_SLUG_TOKENS``, so ``_slug_ok``
    # passes it ON SIGHT. The first version read ``a-third-party`` -- equally
    # fictional, and the guard has no way to know that, so it correctly
    # refused a slug-shaped string it had never been told was fake.
    #
    # RENAMED RATHER THAN DECLARED, deliberately. A ``DECLARED_PLANTS`` entry
    # tolerates that shape in this file forever and is inherited by readers who
    # take the list to mean "known safe" rather than "known fake". A value that
    # argues for itself costs less than one that needs an argument.
    theirs = press.check_address(f"{BASE}/in/another-person/")
    assert theirs["refused"] in {"address_not_admitted", "third_party_surface"}
    assert theirs["reachable_by_this_route"] is False


def test_the_third_party_refusal_fires_on_its_own_merits():
    """Aimed straight at ``check_address`` with the allowlist stipulated.

    Without this, the previous test passes on the allowlist alone and the
    third-party branch is never the thing standing -- the mutation-survives
    lesson this repository has recorded three times.
    """
    verdict = press.check_address(f"{BASE}/in/someone/detail/")
    assert verdict["refused"] in {"address_not_admitted", "third_party_surface"}
    # And the branch itself, exercised directly on a path it alone refuses.
    assert "me" in press._SELF_SEGMENTS


# ---------------------------------------------------------------------------
# CONDITION 3 -- the counter, and UNMEASURABLE RESOLVES AGAINST THE PRESS
# ---------------------------------------------------------------------------

def test_a_press_with_no_counter_reading_is_refused():
    verdict = press.check_counters(None, None)
    assert verdict["refused"] == "no_counter_reading"


def test_an_unreadable_counter_is_not_a_zero():
    verdict = press.check_counters({"invitations": None}, {"invitations": 0})
    assert verdict["refused"] == "counter_unreadable"


def test_no_shared_counter_means_nothing_prices_the_press():
    verdict = press.check_counters({"a": 1}, {"b": 1})
    assert verdict["refused"] == "no_counter_prices_this_press"


def test_a_moved_counter_makes_it_a_write_and_that_is_terminal():
    """A PRESS THAT MOVES AN OUTWARD COUNTER IS A WRITE, whatever it looked
    like. Terminal, because no retry makes it not a write."""
    verdict = press.check_counters({"invitations": 0}, {"invitations": 1})
    assert verdict["refused"] == "counter_moved"
    assert verdict["reachable_by_this_route"] is False


def test_unchanged_counters_pass_and_name_what_priced_it():
    verdict = press.check_counters({"invitations": 0}, {"invitations": 0})
    assert verdict.get("counters_ok") is True
    assert verdict["priced_by"] == ["invitations"]


def test_priced_by_means_READABLE_and_says_so_rather_than_implying_sensitive():
    """THE WEAK SENSE, LABELLED.

    ``priced_by`` names counters READ at both ends. It does NOT establish that
    any of them would have moved had the press done something, and the field
    name invites exactly that stronger reading -- so the weaker one is stated
    in the verdict rather than left to a reader's charity.

    The ruling's own language is the strong sense: *where no counter CAN price
    a press, unmeasurable resolves AGAINST the press.* This implementation
    reads "can price" as "was read at both ends". **That gap is real and is
    recorded rather than closed**, because closing it would require showing a
    counter SENSITIVE to a press class -- which, for an outward counter, is
    shown only by a press of that class moving it, which is the write the gate
    exists to prevent.

    So on a surface offering no safe sensitive counter, the strong reading can
    be shown passing and can never be shown capable of failing. Whether that
    resolves against the press is a boundary ruling, not a code change.
    """
    verdict = press.check_counters(
        {"invitations": 0, "notifications_unread": 6},
        {"invitations": 0, "notifications_unread": 6},
    )
    assert verdict["counters_ok"] is True
    assert verdict["priced_by"] == ["invitations", "notifications_unread"]
    assert verdict["sensitivity_established"] is False, (
        "a passing counter check must not claim its counters were sensitive "
        "to the press -- it only ever showed they were readable."
    )
    assert "SENSITIVE" in verdict["sensitivity_note"]


# ---------------------------------------------------------------------------
# CONDITION 4 -- closure
# ---------------------------------------------------------------------------

def test_an_unrestored_toggle_is_refused():
    verdict = press.check_closure("false", "true")
    assert verdict["refused"] == "not_restored"


def test_an_unverifiable_closure_is_treated_as_an_open_one():
    verdict = press.check_closure("false", None)
    assert verdict["refused"] == "closure_unverifiable"


# ---------------------------------------------------------------------------
# THE ORDERING -- a refused press must touch NOTHING
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_a_refused_press_never_touches_the_page():
    """THE DIFFERENCE BETWEEN A GUARD AND A REPORT.

    Every refusal below is checked against a page that would have recorded a
    click. A gate that refuses AFTER acting is not a gate.
    """
    for url, shape in (
        (f"{BASE}/article/new/", "[aria-expanded]"),
        (f"{BASE}/pulse/drafts/", "[aria-expanded]"),
        (f"{BASE}/feed/", 'button:has-text("All filters")'),
        (f"{BASE}/feed/", "button"),
    ):
        page = FakePage(url)
        verdict = await press.disclose(page, shape=shape, read_counters=_counters)
        assert verdict["pressed"] is False
        assert page.clicks == [], (url, shape, page.clicks)
        assert page.keys == []
        assert page.selectors == [], (
            "a refused press asked the page for a locator. The gate must "
            "return before touching anything."
        )


@pytest.mark.asyncio
async def test_a_press_with_no_counter_reader_touches_nothing():
    page = FakePage(f"{BASE}/feed/")
    verdict = await press.disclose(page, shape="[aria-expanded]", read_counters=None)
    assert verdict["refused"] == "no_counter_reader_supplied"
    assert page.clicks == [] and page.selectors == []


@pytest.mark.asyncio
async def test_a_permitted_press_clicks_exactly_the_sanctioned_shape():
    """THE POSITIVE CONTROL. Without it every refusal above could be a gate
    that refuses everything, which certifies nothing."""
    page = FakePage(f"{BASE}/feed/")
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_counters
    )
    assert verdict["pressed"] is True, verdict
    assert page.clicks == ["[aria-expanded]"]
    assert page.keys == ["Escape"], "condition 4 requires the closure"
    # EVERY SELECTOR THE PAGE IS HANDED COMES FROM A CLOSED SET IN THIS
    # PACKAGE -- the sanctioned shape, or a member of WITNESS_SELECTORS.
    #
    # This assertion used to read ``== {"[aria-expanded]"}``, and the witness
    # added on 2026-09-19 made that false BY DESIGN: seeing whether anything
    # opened requires reading the PAGE and not only the pressed control. The
    # property that actually mattered was never "exactly one selector" -- it
    # was that no selector is ever derived from page text or from a caller's
    # string, and that is what is asserted now.
    witness = {selector for _name, selector in press.WITNESS_SELECTORS}
    assert set(page.selectors) <= {"[aria-expanded]"} | witness, (
        "a selector was handed to the page that is neither the sanctioned "
        "shape nor a member of the closed witness set -- no label, no "
        "derived string, no caller input."
    )
    assert page.clicks == ["[aria-expanded]"], (
        "the witness must READ the page and never press it: exactly one "
        "control is clicked however many selectors are counted."
    )


@pytest.mark.asyncio
async def test_a_moved_counter_is_reported_after_a_real_press():
    """The empirical half of the ruling, end to end on the fake.

    Condition 3 catches the autosave class by MEASUREMENT rather than by
    enumeration, so it has to be shown working after the press and not only as
    a pure function.
    """
    page = FakePage(f"{BASE}/feed/")
    moved = iter([{"invitations": 0}, {"invitations": 1}])

    async def reader():
        return next(moved)

    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=reader
    )
    assert verdict["refused"] == "counter_moved"
    assert verdict["reachable_by_this_route"] is False
    assert page.clicks == ["[aria-expanded]"], (
        "the press did happen -- this refusal is a measurement of its effect, "
        "not a pre-press refusal, and the two must not be conflated."
    )


@pytest.mark.asyncio
async def test_an_absent_shape_is_a_fact_about_the_page_not_the_shape():
    page = FakePage(f"{BASE}/feed/", control_count=0)
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_counters
    )
    assert verdict["refused"] == "shape_absent_on_this_page"
    assert verdict["reachable_by_this_route"] is True, (
        "an absent control is NOT YET, not NEVER -- another page may draw one."
    )
    assert page.clicks == []


# ---------------------------------------------------------------------------
# NOT-YET versus NEVER-BY-THIS-ROUTE
# ---------------------------------------------------------------------------

def test_never_and_not_yet_are_distinguishable_at_the_call_site():
    """A DEFERRAL THAT WILL NEVER RESOLVE IS WORSE THAN A REFUSAL, because it
    consumes a future wave. So the two are different fields, not different
    prose."""
    never = press.evaluate(url=f"{BASE}/feed/", shape="button")
    not_yet = press.check_counters(None, None)
    assert never["reachable_by_this_route"] is False
    assert not_yet["reachable_by_this_route"] is True


def test_every_refusal_says_which_it_is():
    """No refusal may omit the field -- an absent flag reads as neither."""
    refusals = [
        press.check_address(None),
        press.check_address(f"{BASE}/pulse/drafts/"),
        press.check_address(f"{BASE}/article/new/"),
        press.check_shape("button"),
        press.check_counters(None, None),
        press.check_counters({"a": 0}, {"a": 1}),
        press.check_closure("false", "true"),
    ]
    for verdict in refusals:
        assert "reachable_by_this_route" in verdict, verdict
        assert isinstance(verdict["reachable_by_this_route"], bool)
        assert verdict.get("why"), "a refusal must say what it saw"


# ---------------------------------------------------------------------------
# THE REGRESSION CASE -- a real press, scored 1 of 4 by the wave that took it
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_the_all_filters_press_scores_one_of_four_and_is_refused():
    """THE SPECIFICATION IN ONE CASE, and it is not hypothetical.

    On 2026-09-19 a probe pressed the All-filters trigger on `/jobs/search/`.
    Its own wave then audited that press against these four conditions and
    scored it **1 of 4**:

        1. page already admitted        PASS  (/jobs/search/)
        2. matched by ATTRIBUTE         FAIL  matched by LABEL TEXT
        3. shown not to move a counter  FAIL  no counter reading taken at all
        4. closed, closure VERIFIED     FAIL  Escape pressed, never checked

    Its author's sentence is the specification: *"I can't show it was harmless,
    because I never measured the thing that would show it."*

    **A MECHANISM THAT WOULD HAVE ALLOWED THAT PRESS IS NOT THE MECHANISM THE
    RULING DESCRIBES**, so it is pinned here as a regression rather than left
    as a story. Each of the three failing conditions is asserted to refuse on
    its own, because a case that fails three ways can pass a gate that only
    catches one of them -- the mutation-survives lesson applied to a test
    input.
    """
    jobs = f"{BASE}/jobs/search/"

    # CONDITION 1 is the one it PASSED, and asserting that is what makes the
    # other three mean something: the refusals below are not an artefact of an
    # address that was never admitted.
    assert readonly.is_read_url(jobs) is True
    assert press.check_address(jobs).get("admitted") is True

    # CONDITION 2 -- the actual selector it used, refused for being a label.
    for real_selector in (
        'button[aria-label*="All filters" i]',
        'button:has-text("All filters")',
    ):
        verdict = press.check_shape(real_selector)
        assert verdict["refused"] == "shape_not_sanctioned"
        assert verdict["reachable_by_this_route"] is False

    # CONDITION 3 -- no reading taken at either end.
    assert press.check_counters(None, None)["refused"] == "no_counter_reading"

    # CONDITION 4 -- Escape pressed, closure never read back.
    assert press.check_closure("true", None)["refused"] == "closure_unverifiable"

    # AND END TO END: the gate refuses before the page is touched at all.
    page = FakePage(jobs)
    verdict = await press.disclose(
        page,
        shape='button[aria-label*="All filters" i]',
        read_counters=_counters,
    )
    assert verdict["pressed"] is False
    assert verdict["refused"] == "shape_not_sanctioned"
    assert page.clicks == [] and page.selectors == [], (
        "the regression press reached the page. This is the exact press the "
        "mechanism exists to have prevented."
    )


def test_a_press_that_skips_the_closure_check_cannot_report_success():
    """The fourth condition, isolated so it is the only thing standing.

    The regression case failed three conditions at once, so it would be
    refused by this gate even if condition 4 did nothing. This input passes 1,
    2 and 3 and fails only the closure, which is what makes the branch
    reachable and the test falsifiable.
    """
    verdict = press.evaluate(
        url=f"{BASE}/feed/",
        shape="[aria-expanded]",
        before={"invitations": 0},
        after={"invitations": 0},
        expanded_before="false",
        expanded_after="true",
    )
    assert verdict["refused"] == "not_restored"


def test_the_caller_cannot_hand_in_a_selector():
    """The signature is the safety property: ``shape`` is membership-checked
    against a closed tuple before it is ever used to build a locator."""
    signature = inspect.signature(press.disclose)
    assert "shape" in signature.parameters
    assert "selector" not in signature.parameters
    assert "label" not in signature.parameters
    for invented in ("[aria-expanded][data-x]", " [aria-expanded]", "[aria-expanded] "):
        assert press.check_shape(invented)["refused"] == "shape_not_sanctioned", (
            f"{invented!r} was admitted; membership must be EXACT, so a "
            "near-miss string cannot be smuggled past the list."
        )
