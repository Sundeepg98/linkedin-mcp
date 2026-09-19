"""The notifications-cost precondition, driven entirely from synthetic readings.

WHY THERE IS NO BROWSER IN THIS FILE. The reader half
(:func:`notify_cost.read_notifications_badge`) is the only part that needs a
page, and it is deliberately thin: it counts two locators and pulls one
attribute. Everything that DECIDES lives in the three pure functions below it,
which is what makes the decisions testable at all. So the detector is factored
out of its assertion here in the literal sense -- the tests hand the parser a
dict and read what it concluded, and none of them can be satisfied by a
browser behaving a particular way.

THE CASE THIS FILE EXISTS FOR is ``test_a_zero_before_refuses_even_when_the_pair_is_clean``.
Its input is a pair with nothing whatever wrong with it: both halves readable,
no error, no missing control, a well-formed count on each side. Every OTHER
refusal branch in ``cost_delta`` passes that input. The zero guard is the only
thing standing between it and a confident ``delta: 0`` -- which is exactly the
property the 2026-09-05 ruling asks for, and the reason the input is shaped
this way rather than being a generically broken pair.
"""

from __future__ import annotations

import pytest

from linkedin_server import notify_cost


def _reading(label: str | None, *, links: int = 3, badge_links: int = 1,
             error: str | None = None) -> dict[str, object]:
    """A synthetic badge reading, built the way the DOM half would return one.

    Kept as a helper rather than inlined so that the tests below state only
    what they are VARYING. A test whose fixture is 80% boilerplate hides which
    field it is actually about.
    """
    return {
        "links": links,
        "badge_links": badge_links,
        "label": label,
        "error": error,
    }


# --------------------------------------------------------------------------
# The parser: zero is a real answer and is not the same as unreadable
# --------------------------------------------------------------------------


def test_a_well_formed_badge_parses_to_its_count() -> None:
    parsed = notify_cost.notifications_badge(_reading("<opaque>, 7 new notifications"))
    assert parsed["state"] == "read"
    assert parsed["unread"] == 7


def test_a_badge_at_zero_is_read_and_not_unreadable() -> None:
    """The distinction the whole module rests on, asserted directly."""
    parsed = notify_cost.notifications_badge(_reading("<opaque>, 0 new notifications"))
    assert parsed["state"] == "read"
    assert parsed["unread"] == 0


def test_a_nav_that_drew_nothing_is_unreadable_and_not_zero() -> None:
    parsed = notify_cost.notifications_badge(
        _reading(None, links=0, badge_links=0)
    )
    assert parsed["state"] == "unreadable"
    assert parsed["unread"] is None


def test_the_refusal_reports_what_it_saw_not_only_what_it_missed() -> None:
    """A bare 'zero matched' is what stops anyone telling two repairs apart."""
    parsed = notify_cost.notifications_badge(
        _reading(None, links=3, badge_links=0)
    )
    assert parsed["state"] == "unreadable"
    saw = parsed["saw"]
    assert saw["notifications_links"] == 3
    assert saw["links_carrying_a_count"] == 0


def test_two_counted_controls_refuse_rather_than_choose_by_position() -> None:
    parsed = notify_cost.notifications_badge(
        _reading("<opaque>, 2 new notifications", badge_links=2)
    )
    assert parsed["state"] == "unreadable"
    assert "position" in parsed["why"]


def test_a_shaped_opaque_label_lands_in_the_parse_refusal() -> None:
    """The aim matches the RAW attribute; the parse runs on the SHAPED one."""
    parsed = notify_cost.notifications_badge(_reading("<opaque>"))
    assert parsed["state"] == "unreadable"
    assert parsed["unread"] is None


# --------------------------------------------------------------------------
# The precondition: is today a day this could be measured at all?
# --------------------------------------------------------------------------


def test_a_nonzero_badge_makes_the_cost_measurable_today() -> None:
    verdict = notify_cost.measurability(_reading("<opaque>, 4 new notifications"))
    assert verdict["state"] == "measurable"
    assert verdict["measurable"] is True
    assert verdict["unread_before"] == 4


def test_a_zero_badge_is_not_today_and_says_so_reversibly() -> None:
    """A zero here is a fact about the ACCOUNT, and must not read as permanent."""
    verdict = notify_cost.measurability(_reading("<opaque>, 0 new notifications"))
    assert verdict["state"] == "not_today"
    assert verdict["measurable"] is False
    # The field that stops a caller filing the row as permanently closed.
    assert verdict["reversible"] is True


def test_an_unreadable_badge_is_not_a_not_today() -> None:
    """Three-way, never two-way: 'could not look' is not 'looked and saw none'."""
    verdict = notify_cost.measurability(_reading(None, links=0, badge_links=0))
    assert verdict["state"] == "unreadable"
    assert verdict["measurable"] is None
    assert verdict["reversible"] is None


@pytest.mark.parametrize(
    "reading, expected",
    [
        (_reading("<opaque>, 0 new notifications"), "not_today"),
        (_reading("<opaque>, 1 new notifications"), "measurable"),
        (_reading(None, links=0, badge_links=0), "unreadable"),
        (_reading(None, error="TimeoutError: nav never hydrated"), "unreadable"),
    ],
)
def test_the_three_states_are_reachable_and_distinct(
    reading: dict[str, object], expected: str
) -> None:
    assert notify_cost.measurability(reading)["state"] == expected


# --------------------------------------------------------------------------
# The delta, and the one refusal that fires on a pair with nothing wrong
# --------------------------------------------------------------------------


def test_a_real_pair_measures_the_drop() -> None:
    out = notify_cost.cost_delta(
        _reading("<opaque>, 5 new notifications"),
        _reading("<opaque>, 0 new notifications"),
    )
    assert out["state"] == "measured"
    assert out["delta"] == 5


def test_a_zero_before_refuses_even_when_the_pair_is_clean() -> None:
    """THE MUTATION-SENSITIVE CASE. See this module's docstring.

    Both halves are readable, both carry a well-formed count, there is no
    error and no missing control. Every other refusal branch in ``cost_delta``
    passes this input. Delete the zero guard and this returns
    ``state: measured, delta: 0`` -- a number that reads as "no cost" and
    means "no experiment".

    So the assertion is on the REFUSAL REASON, not on the delta. Asserting
    ``delta != 5`` or ``delta is falsy`` would survive the mutation, which is
    the trap the 2026-09-05 ruling names: a test asserting the refusal SHAPE
    and nothing about the branch it is named for.
    """
    out = notify_cost.cost_delta(
        _reading("<opaque>, 0 new notifications"),
        _reading("<opaque>, 0 new notifications"),
    )
    assert out["state"] == "refused"
    assert out["refused_on"] == "nothing_to_consume"
    assert out["delta"] is None


def test_an_unreadable_after_says_the_cost_was_paid_and_not_recorded() -> None:
    out = notify_cost.cost_delta(
        _reading("<opaque>, 6 new notifications"),
        _reading(None, links=0, badge_links=0),
    )
    assert out["state"] == "refused"
    assert out["refused_on"] == "after_unreadable"
    # The half that matters: an unreadable AFTER does not mean nothing was
    # spent. It means the spend was not recorded.
    assert "paid" in out["why"]


def test_the_three_refusals_are_distinguishable_from_each_other() -> None:
    """They want different repairs, so a caller must be able to tell them apart."""
    reasons = {
        notify_cost.cost_delta(
            _reading(None, links=0, badge_links=0),
            _reading("<opaque>, 0 new notifications"),
        )["refused_on"],
        notify_cost.cost_delta(
            _reading("<opaque>, 6 new notifications"),
            _reading(None, links=0, badge_links=0),
        )["refused_on"],
        notify_cost.cost_delta(
            _reading("<opaque>, 0 new notifications"),
            _reading("<opaque>, 0 new notifications"),
        )["refused_on"],
    }
    assert reasons == {
        "before_unreadable",
        "after_unreadable",
        "nothing_to_consume",
    }


# --------------------------------------------------------------------------
# The aim, which is the half a browser would exercise
# --------------------------------------------------------------------------


def test_the_selector_is_the_conjunction_of_href_and_count_tail() -> None:
    """Neither half alone identifies the badge, and the aim must carry both."""
    sel = notify_cost.notifications_badge_selector()
    assert notify_cost.NOTIFICATIONS_BADGE_HREF in sel
    assert "new notification" in sel


def test_the_badge_tail_never_matches_a_label_without_a_count() -> None:
    assert notify_cost.BADGE_TAIL.search("Notifications") is None
    assert notify_cost.BADGE_TAIL.search("<opaque>, 12 new notifications")
