"""The write boundary on a LIST surface: the unfollow, its verification, and
two defensive branches.

SPLIT OUT OF ``tests/test_writes.py`` ON 2026-11-27 (lane ci8). That file took
about 137 s alone, over the two-minute cap on a local gate, so it was split
by concern into six files, each well under it. This one holds its
sections 9 (the click, on the LIST surface) and 9b (two defensive
branches), moved
verbatim, with their banners and their prose. The fixtures, the navigator,
the frozen captures and the helpers stay in ``tests/test_writes.py``, which
69 test files already import them from; its module docstring is the account
of the whole write boundary these files test, and it still applies here.
"""

from __future__ import annotations

import pytest

from linkedin_server import dom, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import (
    spec_for_action,
)
from tests.test_writes import (  # noqa: F401 -- fixtures are used by injection
    _no_grants_survive_a_test,
    browser_page,
    writes_on,
    FOLLOWED_COMPANY,
    FOLLOWED_COMPANY_NAME,
    _bare_grant,
    _granted,
    _manage_pages,
)


# ---------------------------------------------------------------------------
# 9. The click, on the LIST surface
# ---------------------------------------------------------------------------
#
# WHY THIS SECTION EXISTS SEPARATELY FROM THE SAVE ONE. Everything above tests
# perform() against a POSTING: one id in a url, a control whose state is a
# label, and a confirmation read from a genuinely different surface. The
# unfollow is none of those. It lands on a LIST whose url carries no target at
# all, its control is found by a row predicate rather than by a name, and its
# confirmation has nowhere else to come from. Three branches in perform() turn
# on that difference and none of them was exercised by a save test.




class SequencedNavigator:
    """Serves a DIFFERENT page each time the SAME url is asked for.

    ``FixtureNavigator`` maps one url to one frozen page, which is exactly
    right for the save pair: it clicks on a posting and confirms from the saved
    list, two urls, so "before" and "after" are two separate frozen worlds by
    construction.

    An unfollow loads ONE url TWICE -- the page it clicks on, then the reload
    that confirms the click -- across a world the click just changed. A
    one-page-per-url fake cannot represent that at all: it either serves the
    before-world to the verification (which then always reports failure) or the
    after-world to the click (which then always refuses at gate 5, because the
    row it was about to press is not there). Both were observed while writing
    these tests, and both look like a code defect rather than a fixture that
    cannot express the situation.

    So this pops from a per-url queue and RECORDS every ask. The last entry
    repeats if the queue runs dry, which keeps a test that loads once from
    having to describe a second load it does not make.
    """

    def __init__(self, pages: dict):
        self.pages = {url: list(seq) for url, seq in pages.items()}
        self.gotos: list[str] = []

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        queue = self.pages.get(url)
        if not queue:
            raise AssertionError(
                f"the write asked for {url!r}, which this test did not freeze. "
                f"It froze {sorted(self.pages)}."
            )
        html = queue.pop(0) if len(queue) > 1 else queue[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return url


async def _unfollow(page, grant, *, before: str, after: str):
    """Perform an unfollow across a world that changed between the two loads.

    ``before`` is what the click lands on and ``after`` is what the
    verification reload sees. Naming them separately is the point: the
    verification is a claim about the SECOND reading, and a test that could
    only supply one page would be asserting that a page equals itself.
    """
    nav = SequencedNavigator({writes.FOLLOWED_PAGES_URL: [before, after]})
    return await writes.perform(nav, page, grant), nav


async def test_the_after_world_helper_actually_removes_the_row_it_names():
    """THE CONTROL FOR THE HELPER, before anything is concluded from it.

    Every unfollow test below distinguishes its outcome by what this function
    produced. If the cut silently failed -- and a lazy regex over nested lists
    is exactly how it would -- then the "row is gone" world and the "row is
    still there" world would be the same string, three tests would agree with
    each other, and all three would be measuring nothing.
    """
    before = _manage_pages()
    after = _manage_pages(without=FOLLOWED_COMPANY_NAME, total=57)

    assert "Click to stop following " + FOLLOWED_COMPANY_NAME in before
    assert "Click to stop following " + FOLLOWED_COMPANY_NAME not in after
    assert "58 Pages" in before
    assert "57 Pages" in after
    # Exactly ONE row left, and every other row untouched.
    assert before.count("Click to stop following ") == 20
    assert after.count("Click to stop following ") == 19
    assert "/company/" + FOLLOWED_COMPANY + "/" not in after


async def test_an_unfollow_that_took_reports_true_and_names_both_totals(
    writes_on, browser_page
):
    """The happy path, end to end, on the surface nothing else here tests.

    Pins the three things that differ from a save: the click is aimed by the
    ID-KEYED selector rather than by a label, the landing check compares the
    whole list url rather than a job id, and the verdict is carried by
    LinkedIn's own count.
    """
    grant = await _granted(
        browser_page, "unfollow_company", target=FOLLOWED_COMPANY
    )
    block, nav = await _unfollow(
        browser_page,
        grant,
        before=_manage_pages(),
        after=_manage_pages(without=FOLLOWED_COMPANY_NAME, total=57),
    )

    assert block["performed"] is True
    assert block["verified"] is True
    assert block["clicked"]["error"] is None
    assert block["clicked"]["state_before"] == "following"
    assert block["verification"]["expected_state"] == "not_following"
    assert block["verification"]["observed_state"] == "not_following"
    # The count is the evidence, and the block SHOWS both readings rather than
    # printing the conclusion and keeping the arithmetic to itself.
    assert "58" in block["verification"]["why"]
    assert "57" in block["verification"]["why"]

    # Aimed by id, not by label. A label-only selector would match all twenty.
    assert block["clicked"]["selector"] == dom.unfollow_control_selector(
        FOLLOWED_COMPANY
    )
    assert FOLLOWED_COMPANY in block["clicked"]["selector"]

    # The company he can CHECK is named; the id he cannot check is beside it.
    # THE NAME TRAVELS AS A RECORD since 2026-10-10 (the orchestrator's
    # ruling): the organisation record, marked as LinkedIn's text, its link
    # the Page's canonical address.
    from linkedin_server import people_data

    company = people_data.as_record(block["target"]["company"])
    assert isinstance(company, people_data.Organisation), block["target"]["company"]
    assert company.name == FOLLOWED_COMPANY_NAME
    assert block["target"]["company_id"] == FOLLOWED_COMPANY
    assert "job_id" not in block["target"]

    # TWO loads of the SAME url -- the page it clicks on, then the reload that
    # confirms it. Asserted because it is the honest weakness of this action:
    # a later "optimisation" that believed the redrawn button instead would
    # show up here as one load.
    assert nav.gotos == [writes.FOLLOWED_PAGES_URL, writes.FOLLOWED_PAGES_URL]
    assert block["verification"]["read_from"] == writes.FOLLOWED_PAGES_URL
    assert "RELOADED" in block["verification"]["surface"]


async def test_an_unfollow_that_did_not_take_reports_false_and_does_not_raise(
    writes_on, browser_page
):
    """The row is still there afterwards. That is a real outcome, not an error.

    Nothing may raise after the click: once the button has been pressed, THAT
    is the most important fact there is, and an exception on the way home
    replaces it with a stack trace the operator answers by retrying -- which on
    a toggle performs the opposite action.
    """
    grant = await _granted(
        browser_page, "unfollow_company", target=FOLLOWED_COMPANY
    )
    block, _nav = await _unfollow(
        browser_page, grant, before=_manage_pages(), after=_manage_pages()
    )

    assert block["performed"] is False
    assert block["verified"] is False
    assert block["verification"]["observed_state"] == "following"
    assert "still on the page" in block["verification"]["why"]


async def test_a_vanished_row_with_an_unchanged_total_is_unknown_not_success(
    writes_on, browser_page
):
    """THE TEST THAT MAKES THE OTHER TWO MEAN SOMETHING.

    This surface renders about twenty rows of fifty-eight and offers no way to
    page through the rest, so a row being absent from the rows that drew is the
    NORMAL condition for most of the list -- it is not evidence of anything. A
    verification that concluded "gone, therefore unfollowed" would pass the
    happy-path test above AND the failure test above it, and would report
    success every time the list merely reordered.

    So the verdict rests on LinkedIn's own stated total moving by exactly one.
    Here the row is gone and the total held: the honest answer is that nobody
    knows, and the block says to go and look.
    """
    grant = await _granted(
        browser_page, "unfollow_company", target=FOLLOWED_COMPANY
    )
    block, _nav = await _unfollow(
        browser_page,
        grant,
        before=_manage_pages(),
        after=_manage_pages(without=FOLLOWED_COMPANY_NAME, total=58),
    )

    assert block["performed"] == "unknown"
    assert block["verified"] is False
    assert block["verification"]["observed_state"] == "unknown"
    assert "does not corroborate" in block["verification"]["why"]
    assert "look" in block["verification"]["why"]
    # And it does not tell him to retry, which on a toggle is the one
    # instruction that could make it worse -- nor send him to the wrong page
    # to check, which is what it did until this assertion was written: an
    # unknown UNFOLLOW pointed him at his saved jobs.
    advice = block["read_this_if_unsure"]
    assert "Do NOT retry" in advice
    assert "followed companies" in advice
    assert "saved jobs" not in advice


async def test_perform_refuses_when_the_row_is_not_on_the_page_it_landed_on(
    writes_on, browser_page
):
    """GATE 5 on the list surface: the row must be there at CLICK time.

    The preview saw the row; between preview and confirm the list may have
    reordered it out of the rendered window. Absence is not "already
    unfollowed" -- it is "cannot tell" -- so this refuses BEFORE clicking,
    rather than clicking at something that is not there or concluding the work
    was already done.
    """
    grant = await _granted(
        browser_page, "unfollow_company", target=FOLLOWED_COMPANY
    )
    with pytest.raises(WriteAttemptError) as excinfo:
        await _unfollow(
            browser_page,
            grant,
            before=_manage_pages(without=FOLLOWED_COMPANY_NAME),
            after=_manage_pages(),
        )
    message = str(excinfo.value)
    assert "refusing to click" in message
    assert "NOT evidence" in message
    assert "no pagination control" in message


async def test_a_list_write_refuses_a_landing_that_is_not_its_own_list(
    writes_on, browser_page
):
    """The landing check, on the branch a job id cannot exercise.

    A posting is identified by the id inside its url; a list has one address
    and no id, so the url is compared whole. Without a separate branch the
    check would be vacuous for every list write -- ``dom.JOB_HREF`` finds no
    job id in a network-manager url, so the POSTING branch would refuse every
    unfollow outright, and the tempting fix at that point is to skip the check
    for lists entirely.
    """
    grant = await _granted(
        browser_page, "unfollow_company", target=FOLLOWED_COMPANY
    )

    class Elsewhere:
        """Serves the right page and reports a url that is not its own."""

        def __init__(self):
            self.gotos = []

        async def goto(self, page, url):
            self.gotos.append(url)
            await page.set_content(
                _manage_pages(), wait_until="domcontentloaded"
            )
            return "https://www.linkedin.com/feed/"

    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(Elsewhere(), browser_page, grant)
    message = str(excinfo.value)
    assert "refusing to click" in message
    assert "anchored to a row on one page" in message


async def test_the_unfollow_reads_back_no_label_and_says_why(
    writes_on, browser_page
):
    """The post-click sweep is SAVE-ONLY, and the block says so rather than
    reporting null and leaving a reader to guess which it meant.

    An unfollow removes its own row, so there is no control left to read back;
    sweeping for one would report whichever neighbouring row redrew first,
    which is the "choosing by position" failure this package refuses
    everywhere else.
    """
    grant = await _granted(
        browser_page, "unfollow_company", target=FOLLOWED_COMPANY
    )
    block, _nav = await _unfollow(
        browser_page,
        grant,
        before=_manage_pages(),
        after=_manage_pages(without=FOLLOWED_COMPANY_NAME, total=57),
    )
    assert block["newly_observed_save_label"] is None
    assert "not applicable" in block["what_that_label_is_for"]


# ---------------------------------------------------------------------------
# 9b. Two defensive branches, and an honest account of whether they can fire
# ---------------------------------------------------------------------------
#
# THE PATTERN THIS SECTION EXISTS FOR was recorded on 2026-08-23, when a
# mutation survived because ``save_state`` guessing a state for an unseen label
# sat behind a branch that answers first -- dead code that looked live, tested
# by nothing, and green either way. ``_live_control``'s unfollow arm has two
# branches with the same smell, and rather than leaving a reader to work out
# which are real, they are exercised DIRECTLY and their reachability through
# the real selector is stated.


class _StubLocator:
    """Answers the two questions ``read_unfollow_control`` asks, and no more."""

    def __init__(self, count: int, label):
        self._count = count
        self._label = label

    async def count(self) -> int:
        return self._count

    @property
    def first(self):
        return self

    async def get_attribute(self, name: str, timeout=None, **_kwargs):
        assert name == "aria-label"
        return self._label


class _StubPage:
    def __init__(self, count: int, label):
        self._loc = _StubLocator(count, label)
        self.asked: list[str] = []

    def locator(self, selector: str):
        self.asked.append(selector)
        return self._loc


async def _live(count: int, label):
    """Run gate 5's unfollow arm against a stubbed page."""
    spec = spec_for_action("unfollow_company")
    grant = _bare_grant(action="unfollow_company", target=FOLLOWED_COMPANY)
    page = _StubPage(count, label)
    state, why, selector = await writes._live_control(
        page, spec, grant, writes.UNFOLLOW_ANCHOR_PREFIX
    )
    return state, why, selector, page


async def test_two_rows_for_one_company_id_is_unknown_rather_than_a_guess(
    writes_on,
):
    """REACHABLE IN PRINCIPLE, and the reason it is worth guarding.

    The selector keys on a ``/company/<id>/`` link, and nothing stops LinkedIn
    rendering two rows that both carry one -- a duplicate, or a row nested
    inside another it did not expect. Two matches means the id did not select a
    row, and clicking either would be clicking by position, which is the one
    thing this package refuses everywhere.
    """
    state, why, selector, _page = await _live(2, "Click to stop following X")
    assert state == writes.UNKNOWN
    assert selector == ""
    assert "exactly one row" in why
    assert "position" in why


async def test_an_unrecognised_label_is_unknown_and_the_branch_is_a_race_guard(
    writes_on,
):
    """UNREACHABLE THROUGH THE REAL SELECTOR TODAY, and said so rather than
    left looking load-bearing.

    ``dom.unfollow_control_selector`` matches on ``starts-with(@aria-label,
    'Click to stop following ')``, so any button it finds already wears the
    prefix -- the check below cannot fail from a mismatched selector. What it
    CAN catch is a race: the count and the attribute are two separate reads
    over the wire, and LinkedIn may relabel the control between them. That is a
    narrow window and a cheap guard, and the honest description of it is
    "defence against a race", not "validation".

    Exercised directly here BECAUSE it is unreachable the normal way. A branch
    that no test can enter through the front door is one a future refactor
    deletes as dead, and this one stops being dead the moment somebody widens
    the selector.
    """
    state, why, selector, _page = await _live(1, "Following")
    assert state == writes.UNKNOWN
    assert selector == ""
    assert "'Following'" in why
    assert "prefix" in why


async def test_the_selector_itself_is_why_that_branch_cannot_fire_normally(
    writes_on,
):
    """THE CONTROL for the claim in the docstring above.

    Asserts the property rather than restating it: the selector the live read
    uses CONTAINS the prefix it then checks for. If somebody widens the
    selector -- matching on the row alone, say -- this fails, which is exactly
    when the branch above stops being a race guard and starts being a real
    validation.
    """
    selector = dom.unfollow_control_selector(FOLLOWED_COMPANY)
    assert writes.UNFOLLOW_ANCHOR_PREFIX in selector
    assert "starts-with(@aria-label" in selector


async def test_the_happy_arm_of_that_same_function_still_answers(writes_on):
    """Without this, the three above pass on a ``_live_control`` that returns
    unknown for everything -- which would refuse every unfollow forever and
    look, from the tests, like a very careful gate."""
    state, why, selector, page = await _live(
        1, "Click to stop following " + FOLLOWED_COMPANY_NAME
    )
    assert state == "following"
    assert selector == dom.unfollow_control_selector(FOLLOWED_COMPANY)
    assert FOLLOWED_COMPANY_NAME in why
    # And it asked the page for the id-keyed selector, not a label-only one.
    assert page.asked == [dom.unfollow_control_selector(FOLLOWED_COMPANY)]
