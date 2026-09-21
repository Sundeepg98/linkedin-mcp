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

import ast
import inspect
import pathlib
from unittest import mock

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
    """Includes ``off_state`` because /feed/ declares it SENSITIVE.

    A reading that omits the declared counter is refused: a basis naming a
    counter nobody read prices nothing.
    """
    return {
        "invitations": values[0],
        "messaging": values[1],
        "off_state": 3,
    }


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


def test_his_own_profile_is_admitted_and_a_third_party_is_not():
    """The self/third-party split, with both sides asserted.

    The third-party case is refused twice over -- the allowlist does not admit
    it either -- and that is defence in depth rather than redundancy: the
    address check would stop enforcing this the day somebody admits a
    third-party read.

    **RE-AIMED 2026-09-21, AND THE RENAME IS THE POINT.** This test used to
    assert ``evaluate(...).get("permitted_to_attempt") is True`` for
    ``/in/me/``, which was never a fact about the self/third-party split: the
    split lives entirely in :func:`press.check_address`, and the pre-press
    permit was reading True only because the gate did not yet consult the
    basis table. ``/in/me/`` declares no sensitivity basis, so it is ADMITTED
    (condition 1 passes on its own merits) and NOT PERMITTED TO PRESS (condition
    3 has no way to be satisfied there yet). Both halves are asserted below, so
    this is a narrower claim than the old one rather than a weaker one -- and
    the refusal is NOT-YET, with the remedy named in the verdict.
    See `_audit/2026-09-21-refuse-before-the-click.md` section 2.
    """
    assert press.check_address(f"{BASE}/in/me/").get("admitted") is True, (
        "his own profile must still pass condition 1 -- the third-party "
        "branch must not be catching /in/me/."
    )
    mine = press.evaluate(url=f"{BASE}/in/me/", shape="[aria-haspopup]")
    assert mine["refused"] == "no_sensitivity_basis", mine
    assert mine["reachable_by_this_route"] is True, (
        "declaring a basis for his own profile is an available ruling, so "
        "this must not read as NEVER."
    )
    assert "SENSITIVITY_BASES" in mine["why"], (
        "a NOT-YET refusal must name what would unblock it, or it consumes a "
        "future wave working out what to do with it."
    )
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
    """Aimed straight at ``check_address`` with the allowlist STIPULATED.

    Without this, the previous test passes on the allowlist alone and the
    third-party branch is never the thing standing -- the mutation-survives
    lesson this repository has recorded three times.

    **AND IT WAS STILL PASSING ON THE ALLOWLIST ALONE UNTIL 2026-09-21.** This
    test asserted ``refused in {address_not_admitted, third_party_surface}``,
    a SET satisfied by the first of the two, and then asserted a CONSTANT
    (``"me" in _SELF_SEGMENTS``) rather than the branch. Measured: every
    third-party profile spelling tried is refused by ``is_read_url`` first, so
    **the third-party branch could not be reached by any real url and had never
    been shown failing.** The allowlist is stipulated below -- which is what
    "on its own merits" was always supposed to mean -- so the branch is now the
    only thing standing.
    """
    verdict = press.check_address(f"{BASE}/in/someone/detail/")
    assert verdict["refused"] in {"address_not_admitted", "third_party_surface"}

    with mock.patch.object(press.readonly, "is_read_url", lambda _url: True):
        # The allowlist now admits everything, so nothing but the third-party
        # branch can refuse this.
        theirs = press.check_address(f"{BASE}/in/another-person/detail/")
        mine = press.check_address(f"{BASE}/in/me/")
    assert theirs["refused"] == "third_party_surface", theirs
    assert theirs["reachable_by_this_route"] is False
    assert mine.get("admitted") is True, (
        "with the allowlist stipulated, HIS OWN profile must still pass -- "
        "otherwise the branch refuses on the /in/ segment rather than on who "
        "the member is, and the positive half proves nothing."
    )


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


def test_a_merely_readable_counter_no_longer_prices_anything():
    """RULED 2026-09-19. READABILITY IS NOT ENOUGH, and this is the change.

    ``check_counters`` used to PASS on any counter read at both ends and name
    those in ``priced_by``. So condition 3 could be shown passing and could
    never be shown capable of failing -- this repository's own definition of a
    check that certifies nothing.

    With no declared basis for the surface, unchanged readable counters are now
    a REFUSAL, and ``reachable_by_this_route`` is True because declaring a
    basis is an available next step rather than an impossibility.
    """
    verdict = press.check_counters(
        {"invitations": 0}, {"invitations": 0}, basis=None
    )
    assert verdict["refused"] == "no_sensitivity_basis"
    assert verdict["reachable_by_this_route"] is True
    assert "READABLE" in verdict["why"]


def test_the_sensitive_path_names_only_the_sensitive_counter():
    """PATH (a). The worked example is the feed's ``off_state``.

    ``priced_by`` now means shown-sensitive AND read at both ends. The merely
    readable counters are still reported -- under a different name, because
    they are a weaker fact and used to be published as the stronger one.
    """
    basis = press.sensitivity_basis("https://www.linkedin.com/feed/")
    assert basis["kind"] == "sensitive"
    verdict = press.check_counters(
        {"off_state": 3, "invitations": 0},
        {"off_state": 3, "invitations": 0},
        basis=basis,
    )
    assert verdict["counters_ok"] is True
    assert verdict["basis"] == "sensitive"
    assert verdict["priced_by"] == ["off_state"], (
        "priced_by must name the SENSITIVE counter only -- invitations was "
        "read at both ends and prices nothing."
    )
    assert verdict["read_at_both_ends"] == ["invitations", "off_state"]


def test_a_basis_naming_a_counter_nobody_read_prices_nothing():
    """The basis is not a password. It has to be satisfied by a real reading."""
    basis = press.sensitivity_basis("https://www.linkedin.com/feed/")
    verdict = press.check_counters(
        {"invitations": 0}, {"invitations": 0}, basis=basis
    )
    assert verdict["refused"] == "sensitive_counter_not_read"
    assert verdict["reachable_by_this_route"] is True


def test_the_structural_path_prices_by_argument_and_names_no_counter():
    """PATH (b). An explicit argument that no outward effect is possible.

    It reports ``priced_by: []`` deliberately -- the surface is not priced by a
    counter at all, and claiming one would be the same over-claim in the other
    direction.
    """
    basis = press.sensitivity_basis(
        "https://www.linkedin.com/analytics/profile-views/"
    )
    assert basis["kind"] == "structural"
    verdict = press.check_counters(
        {"invitations": 0}, {"invitations": 0}, basis=basis
    )
    assert verdict["counters_ok"] is True
    assert verdict["condition_3_route"] == "structural_argument"
    assert verdict["priced_by"] == []
    assert verdict["sensitivity_established"] is False, (
        "route (b) is an ARGUMENT, not a measurement, and the field that "
        "says so is what stops it being cited later as the stronger thing."
    )
    assert "argument, not a measurement" in verdict["weaker_than_route_a"]
    assert verdict["bound"] and verdict["refuters"]


def test_a_bare_assertion_is_not_a_structural_argument():
    """A ROUTE (b) ENTRY MUST CARRY ITS BOUND AND ITS REFUTERS.

    An argument nobody can attack is the shape this package refuses
    everywhere else, and the first structural argument on the record is
    exactly the one most likely to be cited later as though it were a
    measurement. So the SHAPE is enforced rather than trusted.
    """
    verdict = press.check_counters(
        {"invitations": 0},
        {"invitations": 0},
        basis={"kind": "structural", "why": "no third party on this surface"},
    )
    assert verdict["refused"] == "structural_argument_incomplete"
    assert "bound" in verdict["why"] and "refuters" in verdict["why"]
    assert verdict["reachable_by_this_route"] is True


def test_every_declared_structural_basis_carries_the_full_shape():
    """The table cannot acquire a bare assertion later without this going red."""
    for marker, basis in press.SENSITIVITY_BASES:
        if basis.get("kind") != "structural":
            continue
        for field in press._STRUCTURAL_REQUIRED:
            assert basis.get(field), f"{marker} is missing {field}"
        assert isinstance(basis["refuters"], tuple) and basis["refuters"], marker


def test_the_route_field_distinguishes_all_three_outcomes():
    """ESTABLISHED BY MEASUREMENT, ESTABLISHED BY ARGUMENT, OR NEITHER.

    The third is a refusal, and the first two must be tellable apart at the
    call site -- a verdict that said only "condition 3 passed" would collapse
    a derivation and an argument into one word.
    """
    feed = press.check_counters(
        {"off_state": 3}, {"off_state": 3},
        basis=press.sensitivity_basis("https://www.linkedin.com/feed/"),
    )
    analytics = press.check_counters(
        {"invitations": 0}, {"invitations": 0},
        basis=press.sensitivity_basis(
            "https://www.linkedin.com/analytics/profile-views/"
        ),
    )
    neither = press.check_counters(
        {"invitations": 0}, {"invitations": 0}, basis=None
    )

    assert feed["condition_3_route"] == "sensitive_counter"
    assert feed["sensitivity_established"] is True
    assert analytics["condition_3_route"] == "structural_argument"
    assert analytics["sensitivity_established"] is False
    assert neither.get("condition_3_route") is None
    assert neither["refused"] == "no_sensitivity_basis"


def test_the_basis_table_is_closed_and_not_caller_supplied():
    """``disclose`` resolves the basis from the SURFACE, never from a caller.

    A basis a caller can assert is a basis a caller can invent, and "no
    outward effect is possible here" is exactly the claim somebody in a hurry
    would make about a surface they had not read.
    """
    signature = inspect.signature(press.disclose)
    assert "basis" not in signature.parameters
    assert "sensitivity" not in signature.parameters
    assert press.sensitivity_basis("https://www.linkedin.com/in/me/") is None


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

#: THE ROWS OF THE ORDERING TEST, one per CONDITION rather than one per
#: address, with the condition written down so a gap is visible on the page.
#:
#: **THE ROW SET USED TO BE FOUR ADDRESSES AND IT COVERED TWO CONDITIONS.**
#: Two of them refused at condition 1 and two at condition 2 -- both evaluated
#: before anything is touched -- so the test passed for a gate that acted first
#: on every OTHER branch, and `_audit/2026-09-21-the-all-filters-press.md`
#: section 3 measured exactly that happening on a surface listing other people.
#: A guard whose cases all take the same branch is a guard for that branch.
#:
#: Condition 4 is absent from this list ON PURPOSE and it is not an oversight:
#: **it has no pre-press-derivable refusal by construction.** `closure_verified`
#: is a statement about the state AFTER the press, so there is nothing about it
#: a gate could know in advance. The refusals that are genuinely measurements
#: are covered by :data:`WHEN_KNOWABLE` below, which requires each of them to
#: return a PERMIT from the pre-press verdict -- the mechanical form of "this
#: one really could not have been hoisted".
_REFUSED_BEFORE_ANY_CONTACT = (
    # condition 1 -- the address
    ("condition 1", f"{BASE}/pulse/drafts/", "[aria-expanded]",
     {"address_not_admitted"}),
    ("condition 1", f"{BASE}/article/new/", "[aria-expanded]",
     {"composer_or_editor"}),
    ("condition 1", f"{BASE}/in/another-person/", "[aria-expanded]",
     {"address_not_admitted", "third_party_surface"}),
    ("condition 1", None, "[aria-expanded]", {"no_address"}),
    # condition 2 -- the shape
    ("condition 2", f"{BASE}/feed/", 'button:has-text("All filters")',
     {"shape_not_sanctioned"}),
    ("condition 2", f"{BASE}/feed/", "button", {"shape_not_sanctioned"}),
    # condition 3 -- THE HALF THAT IS A PURE FUNCTION OF THE URL. These two
    # rows are the defect this file's ordering test used to miss entirely.
    ("condition 3", f"{BASE}/search/results/people/", "[aria-expanded]",
     {"no_sensitivity_basis"}),
    ("condition 3", f"{BASE}/in/me/", "[aria-haspopup]",
     {"no_sensitivity_basis"}),
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "condition,url,shape,expected",
    _REFUSED_BEFORE_ANY_CONTACT,
    ids=[
        f"{row[0]}-{sorted(row[3])[0]}" for row in _REFUSED_BEFORE_ANY_CONTACT
    ],
)
async def test_a_refused_press_never_touches_the_page(condition, url, shape, expected):
    """THE DIFFERENCE BETWEEN A GUARD AND A REPORT.

    Every refusal below is checked against a page that would have recorded a
    click. A gate that refuses AFTER acting is not a gate.

    **WIDENED 2026-09-21 TO COVER CONDITION 3.** The two condition-3 rows are a
    surface that lists other people and his own profile, and both were CLICKED
    and then refused by the shipped gate. See
    `_audit/2026-09-21-refuse-before-the-click.md`.
    """
    page = FakePage(url)
    verdict = await press.disclose(page, shape=shape, read_counters=_counters)
    assert verdict["pressed"] is False
    assert verdict["refused"] in expected, (condition, url, shape, verdict)
    assert page.clicks == [], (condition, url, shape, page.clicks)
    assert page.keys == [], (condition, url, shape, page.keys)
    assert page.selectors == [], (
        f"a refused press ({condition}, {verdict.get('refused')}) asked the "
        "page for a locator. The gate must return before touching anything."
    )


@pytest.mark.asyncio
async def test_a_malformed_structural_basis_is_also_caught_before_the_press():
    """The SECOND url-derivable condition-3 refusal, and it needs a plant.

    ``structural_argument_incomplete`` fires when the table declares a route
    (b) entry without its BOUND or its REFUTERS. Like ``no_sensitivity_basis``
    it is a pure function of the url -- the table is closed and keyed by
    surface -- so it must be taken before the press for the same reason, and
    it was not.

    The malformed entry is PLANTED rather than found: the committed table has
    no such row and ``test_every_declared_structural_basis_carries_the_full_shape``
    exists to keep it that way, so the only honest way to reach this branch is
    to manufacture the fixture.
    """
    # ``/notifications/`` because it is ADMITTED by the read allowlist and
    # declares no basis today -- so the plant is the only thing that changed,
    # and the refusal cannot be an artefact of condition 1.
    surface = f"{BASE}/notifications/"
    assert press.check_address(surface).get("admitted") is True
    assert press.sensitivity_basis(surface) is None
    planted = (("/notifications/", {"kind": "structural", "why": "asserted"}),)
    with mock.patch.object(press, "SENSITIVITY_BASES", planted):
        assert press.sensitivity_basis(surface) is not None
        page = FakePage(surface)
        verdict = await press.disclose(
            page, shape="[aria-expanded]", read_counters=_counters
        )
    assert verdict["refused"] == "structural_argument_incomplete", verdict
    assert verdict["reachable_by_this_route"] is True
    assert page.clicks == [] and page.keys == [] and page.selectors == [], (
        "a basis the table itself declares incomplete was pressed anyway."
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
        # ``off_state`` is the feed's declared SENSITIVE counter, so condition
        # 3 is genuinely satisfied here rather than stepped over -- which is
        # what makes the closure the only thing left standing.
        before={"off_state": 3},
        after={"off_state": 3},
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


# ---------------------------------------------------------------------------
# THE HOLE IN THE ORDERING TEST ABOVE, NOW CLOSED. See
# `_audit/2026-09-21-the-all-filters-press.md` section 3 for the measurement
# and `_audit/2026-09-21-refuse-before-the-click.md` for the repair.
# ---------------------------------------------------------------------------

async def test_a_surface_with_no_declared_basis_is_refused_before_it_is_pressed():
    """THE ZERO-CLICKS CONTROL. Inverted 2026-09-21 from a characterisation
    test that pinned the opposite -- ``...is_pressed_before_it_is_refused`` --
    exactly as that test's own docstring instructed.

    ``test_a_refused_press_never_touches_the_page`` asserts the difference
    between a guard and a report, and until 2026-09-21 **every case it checked
    refused at condition 1 or condition 2**, both evaluated before anything is
    touched. No case exercised a surface that PASSES 1 and 2 and fails
    condition 3 because :data:`press.SENSITIVITY_BASES` declares no basis for
    it. On that path the click had already happened when the refusal was
    computed, so for those surfaces the gate was a report.

    **THIS WAS NOT ACADEMIC.** A wave was briefed on 2026-09-21 to press the
    ``All filters`` control on ``/search/results/people/`` and to let the gate
    decide. Had it called :func:`press.disclose`, a live page listing other
    people would have received a real click and a real ``Escape`` before the
    gate said no.

    **WHAT CHANGED:** the pre-press branch of :func:`press.evaluate` now
    consults :func:`press.sensitivity_basis`, which is a PURE FUNCTION OF THE
    URL, so a surface that can only ever end in ``no_sensitivity_basis`` is
    refused with the page untouched. The refusal is NOT-YET rather than NEVER,
    and its ``why`` names the remedy: declare a basis for the surface.
    """
    for surface, shape in (
        (f"{BASE}/search/results/people/", "[aria-expanded]"),
        (f"{BASE}/in/me/", "[aria-haspopup]"),
    ):
        # Condition 1 passes on its own merits, which is what makes the rest
        # mean something: this is not an artefact of an unadmitted address.
        assert readonly.is_read_url(surface) is True
        assert press.check_address(surface).get("admitted") is True
        # Condition 2 passes for a caller naming a sanctioned shape.
        assert press.check_shape(shape).get("shape_ok") is True
        # And no basis is declared for this surface, so condition 3 cannot pass.
        assert press.sensitivity_basis(surface) is None

        # control_count=8 is the count measured on the live people-search page
        # (`_audit/2026-09-21-the-all-filters-press.md` section 5). The control
        # IS present: the refusal is not shape_absent_on_this_page wearing
        # another name.
        page = FakePage(surface, control_count=8)

        async def _one_counter():
            return {"invitations": 0}

        verdict = await press.disclose(
            page, shape=shape, read_counters=_one_counter
        )
        # THE CONTROL, AND IT IS ASSERTED FIRST ON PURPOSE. Everything else
        # here is a statement about a verdict; this is the statement about the
        # PAGE, and it is the one that was false.
        assert page.clicks == [], (
            f"the gate clicked {surface.rsplit('/', 2)[-2]!r} and refused "
            f"afterwards: clicks={page.clicks}. The refusal is a pure "
            "function of the url and was available before any contact."
        )
        assert page.keys == [], (surface, page.keys)
        assert page.selectors == [], (surface, page.selectors)

        assert verdict["pressed"] is False
        assert verdict["refused"] == "no_sensitivity_basis", verdict
        assert verdict["reachable_by_this_route"] is True

        pre = press.evaluate(url=surface, shape=shape)
        assert pre.get("permitted_to_attempt") is not True, (
            "the pre-press verdict still permits a surface whose only possible "
            "outcome is no_sensitivity_basis."
        )
        assert pre["refused"] == "no_sensitivity_basis", pre
        assert pre["reachable_by_this_route"] is True, (
            "declaring a basis for this surface is an available next step, so "
            "the refusal must not read as terminal."
        )


#: WHEN EACH REFUSAL BECOMES KNOWABLE. Three values, and the middle one is not
#: padding: a gate may READ a page without pressing it, and reading is not what
#: the ordering rule forbids. What it forbids is ACTING -- a click or a key --
#: on a refusal that was already derivable.
#:
#: * ``before_any_contact`` -- derivable from the url, the shape and the
#:   caller's own arguments. The page is never even asked for a locator.
#: * ``after_a_read``       -- needs a fact about the page, obtained by reading
#:   it. Nothing is clicked and nothing is typed.
#: * ``after_the_press``    -- a MEASUREMENT of what the press did. It cannot
#:   be hoisted, and :func:`test_every_refusal_is_classified_by_when_it_is_knowable`
#:   proves that per row by requiring the PRE-PRESS verdict on the same input
#:   to be a permit.
#:
#: **THIS TABLE IS THE FIX TO THE BLIND SPOT, not the two rows added to the
#: ordering test.** The ordering test could only ever cover the inputs somebody
#: thought to write down; ``no_sensitivity_basis`` shipped because nobody did.
#: This dict is checked for EXACT completeness against the ``_refuse()`` calls
#: in :mod:`linkedin_server.press`, so a new refusal cannot be added without
#: somebody stating when it becomes knowable.
WHEN_KNOWABLE: dict[str, str] = {
    # condition 1 -- the address, and the caller's own arguments
    "no_address": "before_any_contact",
    "address_not_admitted": "before_any_contact",
    "composer_or_editor": "before_any_contact",
    "third_party_surface": "before_any_contact",
    # condition 2 -- the shape key
    "shape_not_sanctioned": "before_any_contact",
    # condition 3, the url-derivable half. BOTH OF THESE USED TO BE
    # after_the_press, and that was the defect.
    "no_sensitivity_basis": "before_any_contact",
    "structural_argument_incomplete": "before_any_contact",
    "no_counter_reader_supplied": "before_any_contact",
    # the page is read but never pressed
    "shape_absent_on_this_page": "after_a_read",
    # condition 3, the measured half -- these are facts about what the press
    # did and there is nothing about them a gate could know in advance
    "no_counter_reading": "after_the_press",
    "counter_unreadable": "after_the_press",
    "no_counter_prices_this_press": "after_the_press",
    "counter_moved": "after_the_press",
    "sensitive_counter_not_read": "after_the_press",
    # condition 4 -- a statement about the state AFTER the press, so it has no
    # pre-press-derivable form at all
    "closure_unverifiable": "after_the_press",
    "not_restored": "after_the_press",
    # the press itself raising
    "press_failed": "after_the_press",
}


def _refusal_reasons_in_source() -> set[str]:
    """Every reason string ``press.py`` hands to ``_refuse``, read by AST.

    Not by grep: a reason is the FIRST POSITIONAL ARGUMENT of a call, and a
    line-oriented scan cannot tell that from the same word in prose -- this
    repository has recorded exactly that failure in
    ``test_a_correction_is_findable_from_the_claim``.
    """
    tree = ast.parse(pathlib.Path(press.__file__).read_text(encoding="utf-8"))
    reasons: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name != "_refuse" or not node.args:
            continue
        first = node.args[0]
        assert isinstance(first, ast.Constant) and isinstance(first.value, str), (
            "a _refuse() reason is not a literal string. A COMPUTED REASON CAN "
            "CARRY PAGE TEXT, and it also makes this inventory unreadable."
        )
        reasons.add(first.value)
    return reasons


def test_the_refusal_inventory_is_exactly_what_the_module_can_emit():
    """A REFUSAL NOBODY CLASSIFIED IS THE DEFECT THAT SHIPPED.

    Both directions. A reason in the source and not in :data:`WHEN_KNOWABLE`
    is an unclassified branch; an entry for a reason the source no longer
    emits is a stale allowlist, which this repository treats as loudly as a
    missing one -- an allowlist nobody re-checks is a silencer.
    """
    in_source = _refusal_reasons_in_source()
    declared = set(WHEN_KNOWABLE)
    assert in_source - declared == set(), (
        f"unclassified refusals: {sorted(in_source - declared)}. Say when each "
        "becomes knowable -- if the answer is before_any_contact, the gate has "
        "to take it before the press."
    )
    assert declared - in_source == set(), (
        f"stale entries for refusals the module no longer emits: "
        f"{sorted(declared - in_source)}"
    )
    assert set(WHEN_KNOWABLE.values()) <= {
        "before_any_contact", "after_a_read", "after_the_press"
    }


#: The one refusal NOT in :data:`_REACHES`, because reaching it needs a PLANT
#: rather than an input -- the committed basis table has no malformed entry and
#: another test exists to keep it that way. It is exercised by
#: ``test_a_malformed_structural_basis_is_also_caught_before_the_press``.
_REACHED_BY_A_PLANT = {"structural_argument_incomplete"}


def test_every_classified_refusal_is_actually_exercised_somewhere():
    """A CLASSIFICATION NOBODY DRIVES IS A CLAIM, NOT A CHECK.

    :data:`WHEN_KNOWABLE` would otherwise let a refusal be declared
    ``before_any_contact`` with nothing ever proving it. Every reason must be
    reached by a real input in :data:`_REACHES` or by the one named plant, and
    the two sets must not overlap or drift.
    """
    exercised = set(_REACHES) | _REACHED_BY_A_PLANT
    assert exercised == set(WHEN_KNOWABLE), (
        f"classified but never driven: {sorted(set(WHEN_KNOWABLE) - exercised)}; "
        f"driven but not classified: {sorted(exercised - set(WHEN_KNOWABLE))}"
    )
    assert not (set(_REACHES) & _REACHED_BY_A_PLANT), (
        "a reason listed as needing a plant also has a plain input; one of the "
        "two is stale."
    )


#: ONE INPUT PER REFUSAL, so the classification above is exercised rather than
#: asserted. ``kwargs`` are handed to :func:`press.disclose`.
_REACHES: dict[str, dict] = {
    "no_address": {"url": None, "shape": "[aria-expanded]"},
    "address_not_admitted": {
        "url": f"{BASE}/pulse/drafts/", "shape": "[aria-expanded]"},
    "composer_or_editor": {
        "url": f"{BASE}/article/new/", "shape": "[aria-expanded]"},
    # THE ONLY ROW THAT NEEDS A PLANT, and the plant IS the finding. Measured
    # 2026-09-21: `readonly.is_read_url` refuses EVERY third-party profile
    # spelling tried -- `/in/another-person/`, `/in/another-person/detail/`,
    # `/in/another-person/recent-activity/all/` -- so `check_address` returns
    # `address_not_admitted` and the third-party branch is never the thing
    # standing. It is real defence in depth and it is ALSO a branch that had
    # never been shown failing; `test_the_third_party_refusal_fires_on_its_own_merits`
    # asserts a SET containing both reasons, so it is satisfied by the
    # allowlist alone. Admitting the address is the only honest way to make
    # the branch the only thing left.
    "third_party_surface": {
        "url": f"{BASE}/in/another-person/detail/", "shape": "[aria-expanded]",
        "admit_all": True},
    "shape_not_sanctioned": {"url": f"{BASE}/feed/", "shape": "button"},
    "no_sensitivity_basis": {
        "url": f"{BASE}/search/results/people/", "shape": "[aria-expanded]"},
    "no_counter_reader_supplied": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]", "reader": None},
    "shape_absent_on_this_page": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]", "control_count": 0},
    "counter_moved": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]", "reader": "moving"},
    "counter_unreadable": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]", "reader": "unreadable"},
    "no_counter_prices_this_press": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]", "reader": "disjoint"},
    "sensitive_counter_not_read": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]", "reader": "no_off_state"},
    "no_counter_reading": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]", "reader": "none"},
    "not_restored": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]",
        "expanded": ("false", "true", "true")},
    "closure_unverifiable": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]",
        "expanded": ("false", "true", None)},
    "press_failed": {
        "url": f"{BASE}/feed/", "shape": "[aria-expanded]", "raises": True},
}


def _reader_named(name):
    if name is None:
        return None
    if name == "none":
        async def read():
            return None
        return read
    if name == "unreadable":
        async def read():
            return {"off_state": None}
        return read
    if name == "moving":
        values = iter([{"off_state": 3}, {"off_state": 4}])

        async def read():
            return next(values)
        return read
    if name == "disjoint":
        values = iter([{"off_state": 3}, {"invitations": 0}])

        async def read():
            return next(values)
        return read
    if name == "no_off_state":
        async def read():
            return {"invitations": 0}
        return read
    raise AssertionError(name)


class RaisingPage(FakePage):
    """A page whose click raises, for the one refusal that needs it."""

    def locator(self, selector):
        locator = super().locator(selector)
        page = self

        async def click(**_kwargs):
            page.clicks.append(selector)
            raise TimeoutError("synthetic")

        locator.click = click
        return locator


@pytest.mark.asyncio
@pytest.mark.parametrize("reason", sorted(_REACHES))
async def test_every_refusal_is_classified_by_when_it_is_knowable(reason):
    """THE CLASSIFICATION, EXERCISED. Each refusal is reached, and what the
    page received is compared against what :data:`WHEN_KNOWABLE` claims.

    **THE LOAD-BEARING ASSERTION IS THE LAST ONE.** For every refusal claimed
    to be ``after_the_press``, the PRE-PRESS verdict on the same input must be
    a permit -- the mechanical form of "this one genuinely could not have been
    taken earlier". Reclassify ``no_sensitivity_basis`` back to
    ``after_the_press`` and that assertion is what fails, because the pre-press
    verdict now refuses it.
    """
    spec = dict(_REACHES[reason])
    url = spec.pop("url")
    shape = spec.pop("shape")
    reader_name = spec.pop("reader", "steady")
    factory = RaisingPage if spec.pop("raises", False) else FakePage
    admit_all = spec.pop("admit_all", False)
    page = factory(url, **spec)
    reader = _counters if reader_name == "steady" else _reader_named(reader_name)

    if admit_all:
        with mock.patch.object(press.readonly, "is_read_url", lambda _url: True):
            verdict = await press.disclose(page, shape=shape, read_counters=reader)
    else:
        verdict = await press.disclose(page, shape=shape, read_counters=reader)
    assert verdict.get("refused") == reason, verdict

    when = WHEN_KNOWABLE[reason]
    if when == "before_any_contact":
        assert page.selectors == [] and page.clicks == [] and page.keys == [], (
            f"{reason} is classified before_any_contact and the page was "
            f"touched: selectors={page.selectors} clicks={page.clicks}"
        )
    elif when == "after_a_read":
        assert page.selectors != [], f"{reason} claims a read that never happened"
        assert page.clicks == [] and page.keys == [], (
            f"{reason} is classified after_a_read and the page was PRESSED"
        )
    else:
        assert page.clicks != [], (
            f"{reason} is classified after_the_press and no press happened -- "
            "it is derivable earlier and must be taken earlier."
        )
        pre = press.evaluate(url=url, shape=shape)
        assert pre.get("permitted_to_attempt") is True, (
            f"{reason} is classified after_the_press, yet the pre-press "
            f"verdict on the same input already refuses it: {pre.get('refused')}"
        )


@pytest.mark.asyncio
async def test_a_counter_reader_returning_none_cannot_pass_for_a_pre_press_permit():
    """A SECOND INSTANCE OF THE SAME DEFECT, found by enumerating the branches.

    :func:`press.evaluate` decided it was being called BEFORE a press from the
    absence of counter readings -- ``before is None and after is None``. A
    ``read_counters`` that returns ``None`` produces exactly that shape AFTER a
    real click, so the gate clicked, pressed ``Escape``, skipped conditions 3
    and 4 entirely, and returned ``permitted_to_attempt: True`` with no
    ``refused`` key at all.

    **THAT IS WORSE THAN REFUSING LATE**, which is why it is pinned separately:
    a caller testing ``verdict.get("refused")`` sees ``None`` and banks a press
    that was never priced, on a verdict whose own witness says the press
    happened.

    The measured shape at ``4c8d0f1``::

        verdict : {"permitted_to_attempt": true, "pressed": false, ...}
        clicks  : ['[aria-expanded]']
        keys    : ['Escape']
    """
    page = FakePage(f"{BASE}/feed/")

    async def _none_reader():
        return None

    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_none_reader
    )
    assert verdict.get("permitted_to_attempt") is not True, (
        "a pre-press permit was returned for a press that already happened."
    )
    assert verdict["refused"] == "no_counter_reading", verdict
    assert page.clicks == ["[aria-expanded]"], (
        "the press DID happen here -- this refusal is a measurement, and the "
        "defect was never that the click occurred but that the verdict denied "
        "it had."
    )
    # AND THE WITNESS THAT RIDES ON THAT REFUSAL MAY NOT SPEAK FOR IT. See
    # test_the_witness_never_asserts_permission below.
    assert "permitted" not in verdict["witness"].get("why", ""), verdict["witness"]


def test_the_two_moments_give_the_same_reason_for_the_same_surface():
    """THE ANTI-DRIFT CONTROL for a refusal computed at two moments.

    ``check_basis`` runs before the press and ``check_counters`` runs after it,
    and both decide the same two url-derivable refusals. Two copies of one
    refusal drift; the reasoning lives in ``press._basis_refusal`` and this
    asserts the two callers still agree -- same REASON and same terminality,
    on every surface the table knows about and on one it does not.

    The ``why`` texts differ DELIBERATELY and that is asserted too: after a
    press the refusal can also say what WAS read, which is evidence the
    pre-press form does not have. A difference of evidence, not of rule.
    """
    surfaces = (
        f"{BASE}/search/results/people/",   # no basis
        f"{BASE}/in/me/",                   # no basis
        f"{BASE}/notifications/",           # no basis, not in the table at all
    )
    for surface in surfaces:
        pre = press.check_basis(surface)
        post = press.check_counters(
            {"invitations": 0},
            {"invitations": 0},
            basis=press.sensitivity_basis(surface),
        )
        assert pre["refused"] == post["refused"] == "no_sensitivity_basis", (
            surface, pre, post
        )
        assert pre["reachable_by_this_route"] is post["reachable_by_this_route"]
        assert pre["why"] != post["why"], (
            "the post-press refusal must ALSO report what was read at both "
            "ends; if the two texts are identical that evidence was dropped."
        )
        assert "READABLE" in post["why"] and "READABLE" not in pre["why"]

    # And the surfaces that DO declare a basis are not refused at either moment.
    for surface, kind in (
        (f"{BASE}/feed/", "sensitive"),
        (f"{BASE}/analytics/profile-views/", "structural"),
    ):
        verdict = press.check_basis(surface)
        assert verdict.get("refused") is None, verdict
        assert verdict["basis"] == kind
    assert press.check_basis(f"{BASE}/feed/")["requires_counters"] == ["off_state"]
    assert press.check_basis(
        f"{BASE}/analytics/profile-views/"
    )["requires_counters"] == [], (
        "a structural basis prices by ARGUMENT and names no counter; saying it "
        "requires one would send a caller hunting for something that does not "
        "exist."
    )


@pytest.mark.asyncio
async def test_the_witness_never_asserts_permission():
    """A SURFACE MAY NOT PRINT A CLAIM IT CANNOT DERIVE.

    :func:`press.witness_verdict` is handed two counts and, at most, the
    control's own ``aria-expanded``. It never sees the verdict. Its MISS text
    nevertheless read *"the press was permitted and safe"* -- and the module
    docstring is explicit that the witness is attached to REFUSALS TOO, so that
    sentence shipped on refusals, saying the opposite of the verdict it rode
    beside. Measured 2026-09-21 on a press refused for ``no_counter_reading``.

    The property asserted is about the FUNCTION, not about one call site: no
    reading this function can return may contain a permission word.
    """
    readings = (
        (None, None),
        ({}, {}),
        ({"menus": 1}, {"menus": 2}),
        ({"menus": 1}, {"menus": 1}),
        ({"menus": 1}, {"menus": 1}),
    )
    for index, (before, after) in enumerate(readings):
        control_open = "true" if index == 4 else None
        witness = press.witness_verdict(before, after, control_open=control_open)
        why = str(witness.get("why", "")).lower()
        for word in ("permitted", "permission", "safe", "refused", "unsafe"):
            assert word not in why, (
                f"the witness claimed {word!r} in {witness!r}. It is handed "
                "counts and nothing else -- it cannot know whether the press "
                "was permitted, and it is attached to refusals too."
            )

