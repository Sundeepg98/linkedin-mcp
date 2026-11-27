"""The write boundary's state reads: the toggle direction, Open To Work, and
the read the gate performs for itself.

SPLIT OUT OF ``tests/test_writes.py`` ON 2026-11-27 (lane ci8). That file took
about 137 s alone, over the two-minute cap on a local gate, so it was split
by concern into six files, each well under it. This one holds its
sections 9 (the toggle-direction rule), 10 (Open To Work) and 11 (the
read the gate performs FOR ITSELF), moved
verbatim, with their banners and their prose. The fixtures, the navigator,
the frozen captures and the helpers stay in ``tests/test_writes.py``, which
69 test files already import them from; its module docstring is the account
of the whole write boundary these files test, and it still applies here.
"""

from __future__ import annotations

import inspect
import time
from pathlib import Path

import pytest

from linkedin_server import readonly, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import (
    OBSERVATION_TTL_SECONDS,
    assert_write_url,
    mint,
    preview,
    spec_for_action,
)
from tests.test_writes import (  # noqa: F401 -- fixtures are used by injection
    _no_grants_survive_a_test,
    browser_page,
    writes_on,
    FixtureNavigator,
    JOB,
    SAVED_JOB,
    SAVED_LIST_OF_ONE,
    SAVED_LIST_PARTIAL,
    _functions_assigning_into,
    _gate,
    _observe,
    markup,
)


# ---------------------------------------------------------------------------
# 9. The toggle-direction rule
# ---------------------------------------------------------------------------


async def test_the_gate_refuses_when_the_state_came_back_unknown(
    writes_on,
    browser_page,
):
    """``unknown`` is a real answer from the read and must stay one here.

    2a, REPAIRED. This assertion used to be ``"unknown" in str(excinfo.value)``,
    which the WRONG refusal also satisfies -- the wrong-state message
    interpolates the state, so it contains the word too. A cold review deleted
    the entire ``if state == UNKNOWN`` branch and every test in this file still
    passed. The assertion is now a phrase that exists in NO other refusal.

    The page driving it is the frozen tracker capture: one job row under a tab
    LinkedIn's own count says holds zero. A list that disagrees with itself
    cannot settle a direction in either direction, and answering anyway is how
    a gate offers to save something already saved.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "save_job", saved="jobs_tracker_row")
    message = str(excinfo.value)
    assert "refusal, not a delay" in message
    # ...and it says WHY it could not tell, which is the whole reason the read
    # layer returns a reason as well as a verdict.
    assert "More rows than the page claims" in message


async def test_absence_from_a_partial_list_is_not_absence(writes_on, browser_page):
    """The other way the saved read declines to answer, and the one a later
    edit is most likely to "helpfully" remove.

    The tracker loads one page and does not scroll. Nine saved jobs by
    LinkedIn's own count, one row rendered: a posting missing from the row that
    did draw is not a posting that is not saved. This is the Manage-Pages
    hazard on a second surface -- there it would have answered "you do not
    follow them" about thirty-eight companies it had simply not been shown.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "save_job", saved=SAVED_LIST_PARTIAL)
    message = str(excinfo.value)
    assert "refusal, not a delay" in message
    assert "below the fold" in message


async def test_the_unknown_refusal_is_a_different_refusal_from_the_wrong_state_one(
    writes_on,
    browser_page,
):
    """THE CONTROL for 2a, and the thing that makes the repair meaningful.

    The two refusals must be distinguishable by their messages, because the
    only reason the old assertion passed on a deleted branch was that they were
    not. Neither phrase may appear in the other's message.
    """
    with pytest.raises(WriteAttemptError) as unknown:
        await _gate(browser_page, "save_job", saved="jobs_tracker_row")
    with pytest.raises(WriteAttemptError) as wrong:
        await _gate(browser_page, 
            "save_job", target=SAVED_JOB, saved=SAVED_LIST_OF_ONE
        )
    assert "refusal, not a delay" in str(unknown.value)
    assert "refusal, not a delay" not in str(wrong.value)
    assert "OPPOSITE" in str(wrong.value)
    assert "OPPOSITE" not in str(unknown.value)


async def test_acting_from_the_wrong_state_would_perform_the_opposite_and_is_refused(
    writes_on,
    browser_page,
):
    """The refusal most likely to be argued with, and the one that earns most.

    Confirming a save on an ALREADY-SAVED posting does not do nothing. On a
    toggle it UNSAVES it -- the opposite of what the gate said. So the mismatch
    is refused rather than treated as a harmless no-op.
    """
    with pytest.raises(WriteAttemptError) as save_wrong:
        await _gate(browser_page, "save_job", target=SAVED_JOB, saved=SAVED_LIST_OF_ONE)
    assert "OPPOSITE" in str(save_wrong.value)

    with pytest.raises(WriteAttemptError) as unsave_wrong:
        await _gate(browser_page, "unsave_job", saved="jobs_tracker_empty")
    assert "OPPOSITE" in str(unsave_wrong.value)

    with pytest.raises(WriteAttemptError) as follow_wrong:
        await _gate(browser_page, "follow_company", posting="job_detail_following_hydrated")
    assert "OPPOSITE" in str(follow_wrong.value)


async def test_the_right_state_does_render_and_names_both_ends(writes_on, browser_page):
    """THE CONTROL for the refusals above.

    Without it they all pass on a ``_direction`` that raises unconditionally,
    which is the same shape of dead gate this whole module is arranged against.
    """
    save, _ = await _gate(browser_page, "save_job", saved="jobs_tracker_empty")
    assert save["direction"]["currently"] == "not_saved"
    assert save["direction"]["after"] == "saved"

    unsave, _ = await _gate(browser_page, 
        "unsave_job", target=SAVED_JOB, saved=SAVED_LIST_OF_ONE
    )
    assert unsave["direction"]["currently"] == "saved"
    assert unsave["direction"]["after"] == "not_saved"

    follow, _ = await _gate(browser_page, "follow_company", posting="job_detail")
    assert follow["direction"]["currently"] == "not_following"
    assert follow["direction"]["after"] == "following"

    for block in (save, unsave, follow):
        # It names the TOOL the reading came from, so he can run it himself
        # rather than taking the gate's word for the state.
        assert "linkedin_" in block["direction"]["read_from"]


async def test_the_follow_direction_is_read_off_the_page_the_action_would_act_on(
    writes_on,
    browser_page,
):
    """The ideal shape, and the gate says it is the one it got.

    The state and the action share a rendering: one page load, and the control
    that reports the direction is the control the click would move. Nothing can
    drift between the reading and the acting because there is nothing between
    them.
    """
    block, nav = await _gate(browser_page, "follow_company", posting="job_detail")
    assert nav.gotos == [f"https://www.linkedin.com/jobs/view/{JOB}/"]
    assert block["read"]["page_loads"] == 1
    assert block["read"]["same_page_as_the_action"] is True
    assert block["direction"]["read_from_url"] == block["where"]["read_from_url"]


async def test_the_save_direction_comes_from_a_different_surface_and_says_so(
    writes_on,
    browser_page,
):
    """The other shape, kept visibly different rather than flattened into it.

    The direction comes from the LIST -- LinkedIn's own per-tab count with a
    distinguishable empty state. A different source, not a weaker one, and it
    costs a second page load. A gate that reported this as "read off the
    button" would be describing a measurement it did not make.

    THE ORIGINAL REASON FOR THE SPLIT IS GONE AND THE SPLIT IS NOT. This
    docstring used to justify it with "the save control's ON state has never
    been observed and cannot be: he has no saved posting to observe it on."
    That stopped being true on 2026-08-30. The list read stays because it
    answers the question a save actually changes -- MEMBERSHIP of the list --
    where the button answers what a click would do. So the page-load count
    below is unchanged, and it is now a design choice rather than a necessity.
    """
    block, nav = await _gate(browser_page, "save_job", saved="jobs_tracker_empty")
    assert nav.gotos == [
        f"https://www.linkedin.com/jobs/view/{JOB}/",
        writes.SAVED_LIST_URL,
    ]
    assert block["read"]["page_loads"] == 2
    assert block["read"]["same_page_as_the_action"] is False
    assert block["direction"]["read_from_url"] == writes.SAVED_LIST_URL
    assert block["where"]["read_from_url"] != block["direction"]["read_from_url"]
    assert "DIFFERENT surface" in block["direction"]["what_that_means"]


async def test_the_two_shapes_are_not_described_with_the_same_sentence(
    writes_on,
    browser_page,
):
    """THE CONTROL for the pair above: a constant string would satisfy both."""
    follow, _ = await _gate(browser_page, "follow_company", posting="job_detail")
    save, _ = await _gate(browser_page, "save_job", saved="jobs_tracker_empty")
    assert (
        follow["direction"]["what_that_means"]
        != save["direction"]["what_that_means"]
    )
    assert (
        follow["read"]["same_page_as_the_action"]
        is not save["read"]["same_page_as_the_action"]
    )


async def test_the_saved_gate_renders_on_the_list_he_actually_has(
    writes_on,
    browser_page,
):
    """His saved list is EMPTY, and that is a corroborated emptiness rather
    than a failed read: LinkedIn's own count says zero and the page draws its
    empty state. So a save gate renders today and an UNSAVE gate cannot render
    at all -- there is nothing on the account in the state unsave is valid
    from. Recorded because it is the live shape, not a limitation of the
    fixtures.
    """
    block, _ = await _gate(browser_page, "save_job", saved="jobs_tracker_empty")
    assert block["direction"]["currently"] == "not_saved"
    assert "corroborated empty" in block["direction"]["why"]

    with pytest.raises(WriteAttemptError):
        await _gate(browser_page, "unsave_job", saved="jobs_tracker_empty")


# ---------------------------------------------------------------------------
# 10. Open To Work: three states, an audience, no surface -- and no grant
# ---------------------------------------------------------------------------


async def test_open_to_work_will_not_derive_a_destination_it_was_not_given(
    writes_on,
    browser_page,
):
    """It is not a binary toggle -- off, recruiters-only, all-members -- so
    there is no "the other one" to flip to, and inventing one would be the
    gate choosing his audience for him."""
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "set_open_to_work", target="self")
    assert "more than two states" in str(excinfo.value)


async def test_open_to_work_refuses_a_setting_it_has_never_seen_linkedin_render(
    writes_on,
    browser_page,
):
    """A gate that cannot say who can see a setting must not offer it."""
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "set_open_to_work", target="self", to_state="Only my dog")
    assert "ever seen LinkedIn render" in str(excinfo.value)


async def test_open_to_work_refuses_an_ORIGIN_it_could_not_read(
    writes_on,
    browser_page,
):
    """THE HOLE A COLD REVIEW FOUND ON THE DAY THE BRANCH SHIPPED.

    The three-state branch used to return BEFORE the ``unknown`` check ran, so
    for ``set_open_to_work`` -- the ONE action whose residue is IRREVERSIBLE IN
    AUDIENCE -- an unread current state rendered a gate anyway, describing the
    origin as "UNRECOGNISED" and offering to change it. Only the DESTINATION
    was ever validated. The refusals now run before the branch, so they belong
    to every action.

    Two ways the origin fails to read, both driven here against the frozen
    topcard with ONE field edited:

    * the audience is a string this server has never seen LinkedIn render --
      what a rename of the setting would look like;
    * no Open-to-work line at all, which is NOT the same as the setting being
      off. The off state has never been observed on this account, so nothing
      can tell "switched off" from "the card did not draw".
    """
    frozen = markup("profile_topcard")

    renamed = frozen.replace(
        "Open to work &#183; Recruiters only",
        "Open to work &#183; Selected partners",
    )
    absent = frozen.replace("Open to work &#183; Recruiters only", "Add profile section")

    for derived, expected in (
        (renamed, "not one of the settings this server has seen"),
        (absent, "no 'Open to work' line rendered"),
    ):
        spec = spec_for_action("set_open_to_work")
        nav = FixtureNavigator({writes.PROFILE_URL: derived})

        async def work(page, _nav=nav, _spec=spec):
            return await preview(
                _spec,
                target="self",
                navigator=_nav,
                page=page,
                to_state="All LinkedIn members",
            )

        with pytest.raises(WriteAttemptError) as excinfo:
            await work(browser_page)
        assert "refusal, not a delay" in str(excinfo.value)
        assert expected in str(excinfo.value)


def test_open_to_work_refuses_an_ORIGIN_IT_CANNOT_NAME_AN_AUDIENCE_FOR():
    """THE BACKSTOP BEHIND THE UNKNOWN GATE, and it is a SHAPE-CLOSER rather
    than a bug anybody has hit.

    Everything the multi-state branch validates, it validates about the
    DESTINATION: that a ``to_state`` was named, that it is one of the three
    audiences, and that it is not the state already in force. The ORIGIN gets
    two checks and both are about emptiness -- truthy, and not ``unknown``.
    Then the block is built, and building it subscripts
    ``spec.audiences[state.strip().casefold()]``.

    So a state string the spec has never seen -- a relabelled audience, a
    translated one, a fourth setting -- came out of that subscript as a raw
    ``KeyError``. Not a refusal: an unhandled crash, saying nothing about what
    was read, on the one action this module documents as IRREVERSIBLE IN
    AUDIENCE. Every other refusal in ``_direction`` is a sentence the operator
    reads. The binary-toggle path below has exactly this backstop
    (``if state != spec.from_state``) and returns before the multi-state
    branch can reach it, which is the whole reason the gap existed.

    NO REAL LINKEDIN STRING IS KNOWN TO REACH IT, and that is stated rather
    than implied. ``_read_profile_state`` already casefold-checks the audience
    against ``spec.audiences`` and returns ``UNKNOWN`` when it misses, so
    through :func:`preview` an unrecognised audience is caught one layer up --
    which is what ``test_open_to_work_refuses_an_ORIGIN_it_could_not_read``
    pins. This test therefore drives ``_direction`` DIRECTLY, which is the
    only way in, and the guard it demands is the same species as refusal 1 in
    that function's own docstring: unreachable today, kept because it is what
    would catch a future edit routing round the read.

    SHOWN FAILING by deleting the guard from the multi-state branch::

        E       KeyError: 'anyone on linkedin'
    """
    spec = spec_for_action("set_open_to_work")
    # A string LinkedIn could genuinely render -- it is their own audience
    # wording elsewhere in the product -- rather than obvious garbage. The
    # failure this guards is a RENAME, not a corruption.
    observation = writes.Observation(
        target="self",
        target_kind="self",
        facts={"name": "Sundeep", "headline": ""},
        facts_url=writes.PROFILE_URL,
        state="Anyone on LinkedIn",
        state_why="the topcard printed it verbatim beside the label",
        state_url=writes.PROFILE_URL,
        same_page_as_action=False,
        receipt="not-redeemable",
        observed_at=time.monotonic(),
    )

    with pytest.raises(WriteAttemptError) as excinfo:
        writes._direction(spec, observation, "off")
    message = str(excinfo.value)
    # It names WHAT WAS READ, so the reader can go and look at the same card.
    assert "Anyone on LinkedIn" in message, message
    # ...and the permitted set, so the rename is legible as a rename.
    assert "recruiters only" in message, message
    # It must be the ORIGIN being refused, not the destination: the
    # destination refusal already exists and passing on its message would
    # leave this branch untested.
    assert "ever seen LinkedIn render" not in message, message


async def test_open_to_work_names_the_audience_of_the_destination_in_the_gate(
    writes_on,
    browser_page,
):
    """THE POINT OF SPECCING IT AT ALL, and THE CONTROL for the two refusals
    above.

    SOMEONE job-hunting WHILE EMPLOYED faces a setting an employer can read --
    the single one in the whole design -- so the gate does not repeat LinkedIn's four
    words back at him -- it says who will be able to see the change, and says
    it about the DESTINATION rather than the current state.
    """
    block, nav = await _gate(browser_page, 
        "set_open_to_work", target="self", to_state="All LinkedIn members"
    )
    assert nav.gotos == [writes.PROFILE_URL]
    seen = block["who_can_see_it"]
    assert "PUBLIC" in seen
    assert "EMPLOYER" in seen.upper()
    assert block["direction"]["currently"] == "Recruiters only"
    assert block["direction"]["after"] == "All LinkedIn members"
    # ...and the quieter setting must NOT be described as public.
    quiet = block["direction"]["who_can_see_it_now"]
    assert "PUBLIC" not in quiet
    assert "does not see it" in quiet.casefold()


async def test_open_to_work_shows_him_whose_profile_it_is_not_a_job_id(
    writes_on,
    browser_page,
):
    """It used to print a ``job_id`` for a profile setting, because the
    freshness check demanded a title and a company and a profile setting has
    neither -- so the only way to render this gate at all was to hand it two
    fields that do not exist for it. The target is now ``self``, and the facts
    are his own name off his own topcard."""
    block, _ = await _gate(browser_page, 
        "set_open_to_work", target="self", to_state="All LinkedIn members"
    )
    assert "job_id" not in block["where"]
    assert block["where"]["whose"] == "your own LinkedIn profile"
    assert block["where"]["name"] in markup("profile_topcard")

    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "set_open_to_work", target=JOB, to_state="off")
    assert "takes no id" in str(excinfo.value)


async def test_open_to_work_has_no_measured_surface_and_issues_no_token(
    writes_on,
    browser_page,
):
    """A GATE MAY NOT NAME A TARGET SURFACE NOBODY HAS OPENED -- and it may not
    hand out permission to act on one either.

    The state is read off the profile topcard, which is allowlisted. The
    EDITOR is a modal nothing has ever loaded, so there is no url, no anchor
    and no capture. A grant WAS mintable and consumable for it, with
    ``assert_write_url`` the single thing standing between it and a navigation
    -- an invariant enforced only at the point of use is one a future click has
    to remember. It is now refused at issue: no surface, no grant, and the
    block says plainly that what he is reading is the warning rather than an
    offer.
    """
    spec = spec_for_action("set_open_to_work")
    assert spec.url_template is None and spec.url_pattern is None

    block, _ = await _gate(browser_page, 
        "set_open_to_work", target="self", to_state="All LinkedIn members"
    )
    assert block["where"]["url"].startswith("UNMEASURED")
    assert block["to_confirm"] is None
    assert "NO CONFIRM TOKEN IS ISSUED" in block["what_happens_next"]
    assert writes._GRANTS == {}

    with pytest.raises(WriteAttemptError) as excinfo:
        mint("set_open_to_work", "self", receipt="anything")
    assert "no grant is minted" in str(excinfo.value)


async def test_the_measured_surfaces_still_pass_their_own_door(writes_on, browser_page):
    """THE CONTROL. Without it the refusals above pass on a door that has
    stopped letting anything through at all, and on a gate that has stopped
    issuing tokens for everything."""
    block, _ = await _gate(browser_page, "save_job")
    grant = writes._GRANTS[block["to_confirm"]]
    url = f"https://www.linkedin.com/jobs/view/{JOB}/"
    assert assert_write_url(url, grant) == url


# ---------------------------------------------------------------------------
# 11. The read the gate performs FOR ITSELF
# ---------------------------------------------------------------------------
#
# The section this wave exists for. Everything above rests on the gate having
# looked at the target; until 2026-08-23 nothing made it look.


def test_there_is_no_parameter_through_which_a_caller_can_supply_a_state():
    """WHAT A CALLER CAN NO LONGER DO, asserted at the signature.

    The old renderer took ``facts`` and ``state``. Its docstring said both
    "must come from a LIVE re-read of the target" -- a comment, and the whole
    guarantee rested on a not-yet-written caller honouring it. Measured at
    oldsha14: a made-up title, a made-up employer and a direction nobody read
    produced a confident gate. The fix is that there is nowhere left to put
    them.
    """
    parameters = inspect.signature(preview).parameters
    assert "facts" not in parameters
    assert "state" not in parameters
    assert not hasattr(writes, "render_preview")
    # THE CONTROL: the one thing a caller does still choose, so this is not
    # passing merely because every name was removed.
    assert "to_state" in parameters
    assert "target" in parameters


async def test_a_grant_cannot_be_minted_from_a_receipt_nobody_read(writes_on):
    """The receipt is the mechanism, and this is it failing.

    A state string can be typed by a caller that never performed a read -- the
    same argument that made the confirmation a token rather than a boolean,
    one level down. So the state now arrives inside a receipt, and a receipt
    exists only because a page was loaded.
    """
    for invented in ("", None, 1, True, "plausible-looking-receipt"):
        with pytest.raises(WriteAttemptError):
            mint("save_job", JOB, receipt=invented)


async def test_a_receipt_from_an_actual_read_does_mint(writes_on, browser_page):
    """THE CONTROL. Without it the refusal above passes on a mint that refuses
    everything, which is the dead-gate shape this module is arranged against."""
    observation = await _observe(browser_page, "save_job")
    grant = mint("save_job", JOB, receipt=observation.receipt)
    assert grant.token in writes._GRANTS
    assert grant.observation is observation


async def test_a_reading_is_single_use(writes_on, browser_page):
    """A replayed reading mints nothing, for the same reason a replayed
    confirmation performs nothing."""
    observation = await _observe(browser_page, "save_job")
    mint("save_job", JOB, receipt=observation.receipt)
    with pytest.raises(WriteAttemptError) as excinfo:
        mint("save_job", JOB, receipt=observation.receipt)
    assert "already-redeemed" in str(excinfo.value)


async def test_a_reading_of_one_posting_will_not_mint_a_grant_for_another(
    writes_on,
    browser_page,
):
    """The binding the confirm gate's whole value rests on, one level earlier:
    the thing named in the block must be the thing that was read."""
    observation = await _observe(browser_page, "save_job", target=JOB)
    with pytest.raises(WriteAttemptError) as excinfo:
        mint("save_job", "9999999", receipt=observation.receipt)
    assert "this reading is of" in str(excinfo.value)


async def test_a_stale_reading_mints_nothing(writes_on, monkeypatch, browser_page):
    """A confirmation may be two minutes old because a human was reading it. A
    READING may not: anything else touching the account invalidates it."""
    observation = await _observe(browser_page, "save_job")
    real = time.monotonic
    monkeypatch.setattr(
        writes.time, "monotonic", lambda: real() + OBSERVATION_TTL_SECONDS + 1
    )
    with pytest.raises(WriteAttemptError) as excinfo:
        mint("save_job", JOB, receipt=observation.receipt)
    assert "older than" in str(excinfo.value)


async def test_no_reading_survives_the_call_that_made_it(writes_on, browser_page):
    """Whether it rendered or refused. A receipt left lying about is permission
    to mint a grant later, from a reading nobody is still looking at."""
    block, _ = await _gate(browser_page, "save_job")
    assert block["to_confirm"] in writes._GRANTS
    assert writes._OBSERVED == {}

    with pytest.raises(WriteAttemptError):
        await _gate(browser_page, "save_job", saved="jobs_tracker_row")
    assert writes._OBSERVED == {}


async def test_a_reading_that_did_not_settle_the_state_mints_nothing(
    writes_on,
    browser_page,
):
    """``unknown`` stops the grant as well as the gate. Belt and braces, and
    the braces are the ones that survive a future edit routing round
    ``_direction``."""
    observation = await _observe(browser_page, "save_job", saved="jobs_tracker_row")
    assert observation.state == writes.UNKNOWN
    with pytest.raises(WriteAttemptError) as excinfo:
        mint("save_job", JOB, receipt=observation.receipt)
    assert "did not settle the state" in str(excinfo.value)


async def test_the_gate_opens_the_pages_itself_and_only_allowlisted_ones(
    writes_on,
    browser_page,
):
    """The preview IS a read, so it goes through the READ door -- unrelaxed,
    still a zero-line diff, and checked in this module as well as in the
    navigator so that a navigator which skipped it could not point the gate
    anywhere new."""
    _block, follow_nav = await _gate(browser_page, "follow_company", posting="job_detail")
    _block, save_nav = await _gate(browser_page, "save_job")
    _block, profile_nav = await _gate(browser_page, 
        "set_open_to_work", target="self", to_state="All LinkedIn members"
    )

    every_url = follow_nav.gotos + save_nav.gotos + profile_nav.gotos
    assert every_url, "the gate opened nothing at all"
    for url in every_url:
        assert readonly.is_read_url(url), url


def test_only_one_function_in_the_module_records_a_reading():
    """The confinement rule for the receipt registry.

    A second writer of ``_OBSERVED`` would be a second way to mint a reading,
    and a reading is what a grant is made from. So the registry has exactly one
    writer, asserted by walking the module's own syntax tree rather than by
    grep -- an assignment inside a nested function is still an assignment.
    """
    writers = _functions_assigning_into(
        Path(writes.__file__).read_text(encoding="utf-8"), "_OBSERVED"
    )
    assert writers == {"_record"}, writers


def test_that_walk_would_notice_a_second_writer():
    """THE CONTROL, at the shape it exists to reject."""
    smuggled = (
        "def _record(x):\n"
        "    _OBSERVED[x] = 1\n"
        "\n"
        "def helpful_shortcut(x):\n"
        "    _OBSERVED[x] = 2\n"
    )
    assert _functions_assigning_into(smuggled, "_OBSERVED") == {
        "_record",
        "helpful_shortcut",
    }
