"""The write boundary, driven in both directions.

``linkedin_server/writes.py`` is a cage built before the animal: the grant
machinery, the narrowed url door, the confirm gate and the sanctioned set are
all real and all exercised here, while the action itself does not exist yet
because the operator's permission classifier still refuses LinkedIn writes and
an unexercised write against his only account is the worst available outcome.

So these tests carry an unusual obligation. Most of them prove a write CANNOT
happen -- and a suite full of "it refused" is exactly the shape that passes
forever on a module that does nothing at all. Every refusal below is therefore
paired with the positive case that would fire if the machinery were inert: a
grant that DOES mint, a token that DOES redeem, a url that DOES pass its own
door. If the whole module were deleted and replaced with a function that raises
unconditionally, the paired tests go red.
"""

from __future__ import annotations

import ast
import time
from pathlib import Path

import pytest

from linkedin_server import readonly, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import (
    GRANT_TTL_SECONDS,
    PERMANENTLY_FORBIDDEN,
    SANCTIONED_WRITES,
    WRITES_FLAG,
    assert_write_url,
    consume,
    mint,
    render_preview,
    spec_for_action,
)
from tests.test_server_surface import FORBIDDEN_TOOLS

JOB = "4600000042"
FACTS = {"title": "Senior Node Engineer", "company": "Northwind"}


@pytest.fixture
def writes_on(monkeypatch):
    """Turn writes on for one test, and drop every grant afterwards."""
    monkeypatch.setenv(WRITES_FLAG, "1")
    yield
    writes.discard_all()


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


# ---------------------------------------------------------------------------
# 1. Off by default
# ---------------------------------------------------------------------------


def test_writes_are_off_unless_deliberately_enabled(monkeypatch):
    """A fresh clone, and this repo today, cannot mint a grant at all."""
    monkeypatch.delenv(WRITES_FLAG, raising=False)
    assert writes.writes_enabled() is False
    with pytest.raises(WriteAttemptError) as excinfo:
        mint("save_job", JOB, {})
    assert "writes are disabled" in str(excinfo.value)


@pytest.mark.parametrize("value", ["", "0", "no", "off", "false", "maybe"])
def test_only_an_explicit_yes_turns_writes_on(monkeypatch, value):
    monkeypatch.setenv(WRITES_FLAG, value)
    assert writes.writes_enabled() is False


@pytest.mark.parametrize("value", ["1", "true", "yes", "on", "ON", " True "])
def test_the_flag_does_turn_on(monkeypatch, value):
    """The control for every "it refused" above. Without it, a
    ``writes_enabled`` that returned False unconditionally would pass the lot."""
    monkeypatch.setenv(WRITES_FLAG, value)
    assert writes.writes_enabled() is True


# ---------------------------------------------------------------------------
# 2. The grant is single-use, action-bound, target-bound and short-lived
# ---------------------------------------------------------------------------


def test_a_grant_redeems_once(writes_on):
    """The positive case first: the machinery genuinely works."""
    grant = mint("save_job", JOB, {})
    redeemed = consume(grant.token, action="save_job", target=JOB)
    assert redeemed.action == "save_job"
    assert redeemed.target == JOB
    assert redeemed.consumed is True


def test_a_grant_cannot_be_redeemed_twice(writes_on):
    grant = mint("save_job", JOB, {})
    consume(grant.token, action="save_job", target=JOB)
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="save_job", target=JOB)
    assert "already" in str(excinfo.value)


def test_a_token_minted_for_one_job_will_not_act_on_another(writes_on):
    """The confirm gate named a posting. This is what makes that binding real."""
    grant = mint("save_job", JOB, {})
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="save_job", target="9999999")
    assert "target" in str(excinfo.value)


def test_a_token_minted_for_one_verb_will_not_perform_another(writes_on):
    grant = mint("save_job", JOB, {})
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="unsave_job", target=JOB)
    assert "minted for" in str(excinfo.value)


def test_an_expired_token_performs_nothing(writes_on, monkeypatch):
    """The TTL is what makes an unattended write structurally impossible."""
    grant = mint("save_job", JOB, {})
    real = time.monotonic
    monkeypatch.setattr(
        writes.time, "monotonic", lambda: real() + GRANT_TTL_SECONDS + 1
    )
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="save_job", target=JOB)
    assert "expired" in str(excinfo.value)


def test_the_ttl_has_not_quietly_become_an_hour():
    """A scheduler that wakes hourly must never be able to hold a live token."""
    assert 30 <= GRANT_TTL_SECONDS <= 300


@pytest.mark.parametrize("bogus", ["", None, 1, True, "not-a-real-token"])
def test_nothing_that_is_not_a_token_will_do(writes_on, bogus):
    """Specifically: a boolean will not do. `confirm=True` is a flag a caller
    can set without ever having seen a preview; a token is not."""
    with pytest.raises(WriteAttemptError):
        consume(bogus, action="save_job", target=JOB)


def test_a_grant_cannot_be_minted_for_an_unsanctioned_action(writes_on):
    for action in ("apply", "connect", "send_inmail", "post", "endorse"):
        with pytest.raises(WriteAttemptError) as excinfo:
            mint(action, JOB, {})
        assert "not a sanctioned write" in str(excinfo.value)


def test_a_target_that_is_not_an_integer_is_refused(writes_on):
    """The url is BUILT from this. A string here is a string in a url, which is
    the thing an allowlist exists to prevent."""
    for target in ("", "abc", "123/../456", "4600000042?apply=1", "-1"):
        with pytest.raises(WriteAttemptError):
            mint("save_job", target, {})


def test_grants_are_never_written_to_disk(writes_on, tmp_path):
    """A grant that outlived the process is a grant a scheduler could pick up."""
    mint("save_job", JOB, {})
    source = Path(writes.__file__).read_text(encoding="utf-8")
    for persisted in ("open(", "json.dump", "write_text", "pickle", "sqlite"):
        assert persisted not in source, persisted


# ---------------------------------------------------------------------------
# 3. The narrowed door -- and the read door untouched beside it
# ---------------------------------------------------------------------------


def test_the_write_url_is_rebuilt_from_the_grant_not_taken_from_a_caller(writes_on):
    grant = mint("save_job", JOB, {})
    good = f"https://www.linkedin.com/jobs/view/{JOB}/"
    assert assert_write_url(good, grant) == good


@pytest.mark.parametrize(
    "hostile",
    [
        "https://www.linkedin.com/jobs/view/4600000042/?apply=1",
        "https://www.linkedin.com/jobs/view/9999999/",
        "https://www.linkedin.com/jobs/application/4600000042/",
        "https://www.linkedin.com/messaging/thread/4600000042/",
        "https://evil.example.com/jobs/view/4600000042/",
        "https://www.linkedin.com/jobs/view/4600000042/\n",
    ],
)
def test_no_other_url_gets_through_a_save_grant(writes_on, hostile):
    grant = mint("save_job", JOB, {})
    with pytest.raises(WriteAttemptError):
        assert_write_url(hostile, grant)


def test_the_forbidden_list_is_not_shortened_for_writes():
    """Each action exempts at most ONE entry, by ``==``, never by shape.

    Today all three exempt NOTHING, which is the strongest version of this: a
    save grant is refused every forbidden substring without exception.
    """
    for spec in SANCTIONED_WRITES.values():
        assert spec.exempt_substring is None or (
            spec.exempt_substring in readonly._FORBIDDEN_URL_SUBSTRINGS
        ), spec.action


def test_the_read_door_is_untouched_by_any_of_this():
    """The read-only guarantee is the thing that made this server safe to point
    at his live account. A write module that quietly widened it would be the
    whole failure this design exists to avoid."""
    for url in (
        "https://www.linkedin.com/jobs/application/123/",
        "https://www.linkedin.com/messaging/thread/1/",
        "https://www.linkedin.com/in/someone/edit/",
    ):
        assert readonly.is_read_url(url) is False
    assert readonly.is_read_url("https://www.linkedin.com/feed/") is True


# ---------------------------------------------------------------------------
# 4. The conservation law
# ---------------------------------------------------------------------------

#: The forbidden set as it stood before any write was sanctioned. Frozen here
#: so a future edit cannot shrink FORBIDDEN_TOOLS quietly -- a name may only
#: MOVE across the boundary, visibly, into SANCTIONED_WRITES.
_ORIGINAL_FORBIDDEN = frozenset(
    {
        "linkedin_apply",
        "linkedin_apply_job",
        "linkedin_easy_apply",
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_send_message",
        "linkedin_send_inmail",
        "linkedin_connect",
        "linkedin_invite",
        "linkedin_endorse",
        "linkedin_follow",
        "linkedin_post",
        "linkedin_update_profile",
        "linkedin_set_open_to_work",
        "linkedin_mark_notification_read",
        "linkedin_withdraw_application",
    }
)


def test_no_boundary_can_be_deleted_only_moved():
    """THE conservation law. Every originally-forbidden name is still accounted
    for: either still forbidden, or sanctioned with a spec that gates it."""
    accounted = set(FORBIDDEN_TOOLS) | set(SANCTIONED_WRITES)
    missing = _ORIGINAL_FORBIDDEN - accounted
    assert missing == set(), missing


def test_the_conservation_law_would_notice_a_quiet_deletion():
    """The control. Without it the assertion above passes on any superset."""
    pretend_forbidden = set(FORBIDDEN_TOOLS) - {"linkedin_post"}
    accounted = pretend_forbidden | set(SANCTIONED_WRITES)
    assert _ORIGINAL_FORBIDDEN - accounted == {"linkedin_post"}


def test_nothing_is_both_forbidden_and_sanctioned_by_accident():
    """A name in both lists is ambiguous, and ambiguity in a boundary is a hole.

    Today all three sanctioned names are STILL in FORBIDDEN_TOOLS, which is the
    correct state: they are designed and gated but NOT shipped, because the
    action cannot be exercised. This asserts that reading, so the day one ships
    the mismatch is a failing test rather than a silent divergence.
    """
    overlap = set(FORBIDDEN_TOOLS) & set(SANCTIONED_WRITES)
    assert overlap == {
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_set_open_to_work",
    }, overlap


def test_a_sanctioned_write_cannot_evade_the_law_by_being_renamed():
    """A LOOPHOLE IN MY OWN CONSERVATION LAW, found while reviewing it, closed.

    The law says a name leaves ``FORBIDDEN_TOOLS`` only by arriving in
    ``SANCTIONED_WRITES``. Nothing in it constrains a name that was NEVER on
    the forbidden list -- and ``linkedin_follow_company`` is exactly such a
    name. It sanctions a follow while ``linkedin_follow`` sits on the forbidden
    list looking untouched, which is the quiet widening the law exists to stop,
    achieved by renaming instead of by deleting.

    So a sanctioned name must additionally (a) announce itself as a write to
    the surface check, so it can never pass as a read, and (b) use a verb the
    original forbidden list already named, so a new verb cannot be smuggled in
    under a new noun.
    """
    original_verbs: set[str] = set()
    for forbidden in _ORIGINAL_FORBIDDEN:
        original_verbs |= set(readonly.iter_write_verbs_in(forbidden))

    for name in SANCTIONED_WRITES:
        # The shape check alone is enough now. Until readonly.py learned that
        # undoing a write is still a write, this needed an "or it is on the
        # forbidden list" fallback to pass at all, because linkedin_unsave_job
        # read as not-a-write. The fallback is gone because the hole is.
        assert readonly.name_implies_write(name), f"{name} does not read as a write"
        verbs = set(readonly.iter_write_verbs_in(name))
        assert verbs & original_verbs, (name, sorted(verbs))




def test_that_loophole_check_would_catch_a_smuggled_verb():
    """The control, at the shape it is written to reject: a plausible-looking
    tool name whose verb the original list never sanctioned."""
    original_verbs: set[str] = set()
    for forbidden in _ORIGINAL_FORBIDDEN:
        original_verbs |= set(readonly.iter_write_verbs_in(forbidden))

    smuggled = "linkedin_boost_profile"
    assert set(readonly.iter_write_verbs_in(smuggled)) & original_verbs == set()


async def test_no_write_tool_is_registered_on_the_surface_today():
    """The claim the whole pass rests on: the MCP surface is unchanged."""
    from linkedin_server.server import mcp

    names = {t.name for t in await mcp.list_tools()}
    assert names & set(SANCTIONED_WRITES) == set()
    assert names & FORBIDDEN_TOOLS == set()


# ---------------------------------------------------------------------------
# 5. The gate a human reads
# ---------------------------------------------------------------------------


def test_the_gate_names_the_target_in_words_a_person_can_check(writes_on):
    spec = spec_for_action("save_job")
    grant = mint("save_job", JOB, {})
    preview = render_preview(
        spec, target=JOB, facts=FACTS, token=grant.token, state="not_saved"
    )

    assert preview["performed"] is False
    assert preview["where"]["title"] == "Senior Node Engineer"
    assert preview["where"]["company"] == "Northwind"
    assert preview["to_confirm"] == grant.token
    assert "NOTHING has been done" in preview["what_happens_next"]


def test_the_gate_refuses_to_render_without_a_live_reread(writes_on):
    """An id is not something a human can check. A gate naming only an id asks
    him to confirm something he cannot verify, so it is refused outright."""
    spec = spec_for_action("save_job")
    for facts in ({}, {"title": "x"}, {"company": "y"}, {"title": "", "company": ""}):
        with pytest.raises(WriteAttemptError) as excinfo:
            render_preview(
                spec, target=JOB, facts=facts, token="t", state="not_saved"
            )
        assert "live re-read" in str(excinfo.value)


def test_the_gate_prints_every_measured_verdict_with_its_evidence(writes_on):
    """THE RULE, ratified 2026-08-23, and what happened to it.

    When it landed, all three specs printed UNMEASURED, and the rule was
    described as "biting its own author". The measurement was then performed --
    on 2026-08-23, entirely through READS -- so all four now print a verdict.
    That is the rule being satisfied, not relaxed, and this test is the half
    that says so: a verdict must arrive with its EVIDENCE, its OWNER and its
    RESIDUE, because a bare "reversible" is the confident string the rule
    exists to stop whether or not somebody has since done the measuring.
    """
    states = {
        "save_job": ("not_saved", None),
        "unsave_job": ("saved", None),
        "follow_company": ("not_following", None),
        "set_open_to_work": ("Recruiters only", "All LinkedIn members"),
    }
    assert set(states) == {spec.action for spec in SANCTIONED_WRITES.values()}

    for spec in SANCTIONED_WRITES.values():
        state, to_state = states[spec.action]
        preview = render_preview(
            spec,
            target=JOB,
            facts=FACTS,
            token="t",
            state=state,
            to_state=to_state,
        )
        assert spec.reversibility_measured is True, spec.action
        assert preview["reversibility_measured"] is True
        assert "UNMEASURED" not in preview["reversibility"]
        assert preview["reversibility_class"] in {
            "REVERSIBLE",
            "IRREVERSIBLE",
            "STILL-UNKNOWN",
        }
        # A verdict with no evidence line is the thing this rule forbids.
        assert "MEASURED 2026-08-23" in preview["reversibility_evidence"], spec.action
        assert len(preview["reversible_by"]) > 40, spec.action
        assert len(preview["what_it_cannot_undo"]) > 40, spec.action


def test_the_gate_still_refuses_to_print_an_unmeasured_claim(writes_on):
    """THE CONTROL, and it matters more now than when it was written.

    Every real spec is measured today, so the assertion above would pass on a
    renderer that had lost the ability to say UNMEASURED at all -- which is
    precisely how a rule dies: not repealed, just never exercised again. So the
    refusal is driven against a spec that is unmeasured by construction.
    """
    unmeasured = writes.WriteSpec(
        **{
            **spec_for_action("save_job").__dict__,
            "reversibility_measured": False,
        }
    )
    preview = render_preview(
        unmeasured, target=JOB, facts=FACTS, token="t", state="not_saved"
    )
    assert preview["reversibility_measured"] is False
    assert preview["reversibility"].startswith("UNMEASURED")
    assert unmeasured.reversibility_procedure in preview["reversibility"]
    assert not preview["reversibility"].startswith("reversible")


def test_a_follow_says_plainly_that_this_server_cannot_take_it_back(writes_on):
    """The field most likely to mislead, asserted rather than trusted.

    "Reversible" reads as "this tool can undo it". For ``follow_company`` that
    is FALSE -- no unfollow is sanctioned, so a follow performed here is one
    only he can reverse, by hand. Two of the four are undoable by this server
    and two are not, and the gate has to say which it is holding.
    """
    by_server = spec_for_action("save_job").reversible_by
    assert "this server" in by_server

    for action in ("follow_company", "set_open_to_work"):
        by_hand = spec_for_action(action).reversible_by
        assert "NOT this server" in by_hand or "Not this server" in by_hand, action


def test_every_sanctioned_spec_carries_a_procedure_that_would_settle_it():
    """An unmeasured claim must name its own fix, or it is just a caveat."""
    for spec in SANCTIONED_WRITES.values():
        assert len(spec.reversibility_procedure) > 60, spec.action


# ---------------------------------------------------------------------------
# 6. Nothing can actually act
# ---------------------------------------------------------------------------


async def test_the_one_function_that_could_act_refuses(writes_on):
    grant = mint("save_job", JOB, {})
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), grant)
    assert "no write is implemented" in str(excinfo.value)


def test_the_write_module_contains_no_mutating_call_at_all():
    """The reason readonly.py and test_readonly.py keep their zero-line diffs.

    This module could have been the package's first exception to the source
    scanner. It is not one: the scanner still reports zero for every file,
    including this one, because the click does not exist yet.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    assert readonly.scan_source_for_mutations(source) == []


def test_the_scanner_would_have_caught_it_if_it_did():
    """The control for the assertion above, at the exact code that will one day
    be written -- so the check is known to be capable of seeing it."""
    future = (
        "async def perform(page, grant):\n"
        "    await page.click('button[aria-label=\"Save the job\"]')\n"
    )
    kinds = {kind for _, kind, _ in readonly.scan_source_for_mutations(future)}
    assert "click" in kinds


# ---------------------------------------------------------------------------
# 7. The check that will police the click when it arrives
# ---------------------------------------------------------------------------


def _mutating_calls_outside_granted_functions(source: str) -> list[str]:
    """Every mutating call in ``source`` NOT inside a function taking a grant.

    This is the confinement rule, written now and driven at synthetic code,
    so that the day ``perform`` gains a body the rule is already load-bearing
    rather than something somebody remembers to add.
    """
    tree = ast.parse(source)
    offences: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = {a.arg for a in node.args.args + node.args.kwonlyargs}
        takes_grant = "grant" in args
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            func = inner.func
            if not isinstance(func, ast.Attribute):
                continue
            if readonly.scan_source_for_mutations(f"x.{func.attr}()"):
                if not takes_grant:
                    offences.append(f"{node.name} calls .{func.attr}() without a grant")
    return offences


def test_the_confinement_rule_accepts_a_granted_write():
    granted = (
        "async def perform(page, grant):\n"
        "    await page.click('button')\n"
    )
    assert _mutating_calls_outside_granted_functions(granted) == []


def test_the_confinement_rule_rejects_an_ungranted_write():
    """The one that matters: a click that nobody confirmed."""
    ungranted = (
        "async def helper(page):\n"
        "    await page.click('button')\n"
    )
    offences = _mutating_calls_outside_granted_functions(ungranted)
    assert offences and "without a grant" in offences[0]


def test_the_write_module_passes_its_own_confinement_rule():
    source = Path(writes.__file__).read_text(encoding="utf-8")
    assert _mutating_calls_outside_granted_functions(source) == []


# ---------------------------------------------------------------------------
# 8. The permanent refusals say why
# ---------------------------------------------------------------------------


def test_every_permanent_refusal_carries_its_reason():
    """An omission that does not explain itself reads as an oversight, and the
    next agent 'fixes' it."""
    assert len(PERMANENTLY_FORBIDDEN) >= 8
    for name, reason in PERMANENTLY_FORBIDDEN.items():
        assert len(reason) > 40, name


@pytest.mark.parametrize(
    "cut", ["apply", "connect", "send_inmail", "post", "endorse", "mark_read"]
)
def test_the_cut_actions_are_not_reachable_by_any_route(writes_on, cut):
    """apply, connect and InMail were cut by the operator on 2026-08-23. This is
    that decision made structural rather than remembered."""
    assert cut not in {s.action for s in SANCTIONED_WRITES.values()}
    with pytest.raises(WriteAttemptError):
        mint(cut, JOB, {})
    with pytest.raises(WriteAttemptError):
        spec_for_action(cut)


def test_the_anchors_the_future_click_will_use_are_frozen_at_both_renders():
    """The click does not exist, but its anchor is already pinned.

    Both are anchored on the ACCESSIBLE NAME, which is present in both frozen
    renders -- unlike ``data-view-name`` (absent pre-hydration) and unlike a
    class (a build hash). Freezing this now means the day the body is written,
    the selector is not a guess.
    """
    fixtures = Path(__file__).parent / "fixtures"
    for name in ("job_detail.html", "job_detail_hydrated.html"):
        html = (fixtures / name).read_text(encoding="ascii")
        assert 'aria-label="Save the job"' in html, name
        assert 'aria-label="Follow"' in html, name
        # And the anchor that must NOT be relied on, proving the asymmetry.
        if name == "job_detail.html":
            assert 'data-view-name="job-save-button"' not in html


def test_the_instrumentation_that_must_not_be_relied_on_did_in_fact_vanish():
    """The ban on ``data-view-name`` was a rule; on 2026-08-23 it became a
    measurement.

    ``job_detail_hydrated.html`` was captured on 2026-08-22 carrying fifteen
    ``data-view-name`` attributes. A posting loaded live the NEXT DAY carried
    ZERO -- and the fixtures frozen from that capture carry zero, which is what
    this asserts. Same surface, same account, one day, the whole instrumenting
    layer gone. A reader anchored there would have returned nothing that
    morning with every test still green.

    It is surface-specific rather than a platform-wide removal: Manage Pages,
    loaded minutes later, carried thirty-one. That is the honest form of the
    claim and it is why the fixtures are asserted rather than LinkedIn's
    behaviour.
    """
    fixtures = Path(__file__).parent / "fixtures"
    yesterday = (fixtures / "job_detail_hydrated.html").read_text(encoding="ascii")
    today = (fixtures / "job_detail_following_hydrated.html").read_text(
        encoding="ascii"
    )
    assert yesterday.count("data-view-name") > 0
    assert today.count("data-view-name") == 0
    # The accessible names survived the change in both. That is the point.
    assert 'aria-label="Save the job"' in yesterday
    assert 'aria-label="Save the job"' in today


def test_the_toggle_problem_is_solved_and_the_solution_is_recorded():
    """WHAT THIS TEST USED TO SAY, and why it now says the opposite.

    It used to pin a blocker: both anchors are TOGGLES, the captures only ever
    showed the OFF state, so nothing could tell Save from Unsave, and a gate
    that cannot say which way it moves a toggle is not a gate. All true. The
    inference drawn from it was wrong -- that the write had to come first.

    Measuring a toggle's ON state is a READ. It cost one page load on a posting
    from a company he already follows. So the module now records the measured
    labels rather than the blocker, and the direction rule is enforced in
    ``_direction`` rather than described in prose.

    The one honestly unmeasured half stays named: the SAVE control's ON state
    has never been seen, because there is no saved posting on the account to
    see it on, so save takes its direction from the list read instead.
    """
    doc = writes.perform.__doc__ or ""
    assert "IS SOLVED" in doc
    assert 'aria-label="Following"' in doc
    assert "linkedin_saved_jobs" in doc
    # And it must not have quietly dropped the half that is still open.
    assert "has NOT been observed" in doc

    # The measured pair is what the reader actually uses, so assert THAT
    # rather than the docstring alone -- a docstring cannot be wrong in a way
    # a caller notices.
    from linkedin_server import shape

    assert shape.FOLLOW_LABELS == {
        "Follow": "not_following",
        "Following": "following",
    }


# ---------------------------------------------------------------------------
# 9. The toggle-direction rule
# ---------------------------------------------------------------------------


def test_the_gate_refuses_to_render_without_the_targets_measured_state(writes_on):
    """"A gate that cannot say which way it moves a toggle is not a gate."

    This was recorded as a blocker on the write and it was not one: it was a
    READ nobody had performed. Now that both directions are measured, the gate
    REFUSES rather than defaulting, because a default here is a guess wearing a
    measurement's clothes.
    """
    for action in ("save_job", "unsave_job", "follow_company"):
        with pytest.raises(WriteAttemptError) as excinfo:
            render_preview(
                spec_for_action(action), target=JOB, facts=FACTS, token="t"
            )
        assert "TOGGLES" in str(excinfo.value), action


def test_the_gate_refuses_when_the_state_came_back_unknown(writes_on):
    """``unknown`` is a real answer from the read and must stay one here.

    ``dom.read_follow_control`` returns it when the control had not rendered,
    when several rendered, or when LinkedIn labelled it something never seen.
    Proceeding on any of those is proceeding on a guess.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        render_preview(
            spec_for_action("follow_company"),
            target=JOB,
            facts=FACTS,
            token="t",
            state="unknown",
        )
    assert "unknown" in str(excinfo.value)


def test_acting_from_the_wrong_state_would_perform_the_opposite_and_is_refused(
    writes_on,
):
    """The refusal most likely to be argued with, and the one that earns most.

    Confirming a save on an ALREADY-SAVED posting does not do nothing. On a
    toggle it UNSAVES it -- the opposite of what the gate said. So the mismatch
    is refused rather than treated as a harmless no-op.
    """
    cases = {
        "save_job": "saved",
        "unsave_job": "not_saved",
        "follow_company": "following",
    }
    for action, wrong in cases.items():
        with pytest.raises(WriteAttemptError) as excinfo:
            render_preview(
                spec_for_action(action),
                target=JOB,
                facts=FACTS,
                token="t",
                state=wrong,
            )
        assert "OPPOSITE" in str(excinfo.value), action


def test_the_right_state_does_render_and_names_both_ends(writes_on):
    """THE CONTROL for the three refusals above.

    Without it they all pass on a ``_direction`` that raises unconditionally,
    which is the same shape of dead gate this whole module is arranged against.
    """
    pairs = {
        "save_job": ("not_saved", "saved"),
        "unsave_job": ("saved", "not_saved"),
        "follow_company": ("not_following", "following"),
    }
    for action, (before, after) in pairs.items():
        preview = render_preview(
            spec_for_action(action),
            target=JOB,
            facts=FACTS,
            token="t",
            state=before,
        )
        assert preview["direction"]["currently"] == before, action
        assert preview["direction"]["after"] == after, action
        # And it names the TOOL the reading came from, so he can run it
        # himself rather than taking the gate's word for the state.
        assert "linkedin_" in preview["direction"]["read_from"], action


# ---------------------------------------------------------------------------
# 10. Open To Work: three states, an audience, and no surface
# ---------------------------------------------------------------------------


def test_open_to_work_will_not_derive_a_destination_it_was_not_given(writes_on):
    """It is not a binary toggle -- off, recruiters-only, all-members -- so
    there is no "the other one" to flip to, and inventing one would be the
    gate choosing his audience for him."""
    with pytest.raises(WriteAttemptError) as excinfo:
        render_preview(
            spec_for_action("set_open_to_work"),
            target=JOB,
            facts=FACTS,
            token="t",
            state="Recruiters only",
        )
    assert "more than two states" in str(excinfo.value)


def test_open_to_work_refuses_a_setting_it_has_never_seen_linkedin_render(writes_on):
    """A gate that cannot say who can see a setting must not offer it."""
    with pytest.raises(WriteAttemptError) as excinfo:
        render_preview(
            spec_for_action("set_open_to_work"),
            target=JOB,
            facts=FACTS,
            token="t",
            state="Recruiters only",
            to_state="Only my dog",
        )
    assert "ever seen LinkedIn render" in str(excinfo.value)


def test_open_to_work_names_the_audience_of_the_destination_in_the_gate(writes_on):
    """THE POINT OF SPECCING IT AT ALL.

    Someone job-hunting while employed. This is the single setting in the whole
    design a current employer can read, so the gate does not repeat LinkedIn's four
    words back at him -- it says who will be able to see the change, and says
    it about the DESTINATION rather than the current state.
    """
    preview = render_preview(
        spec_for_action("set_open_to_work"),
        target=JOB,
        facts=FACTS,
        token="t",
        state="Recruiters only",
        to_state="All LinkedIn members",
    )
    seen = preview["who_can_see_it"]
    assert "PUBLIC" in seen
    assert "EMPLOYER" in seen.upper()
    assert preview["direction"]["currently"] == "Recruiters only"
    assert preview["direction"]["after"] == "All LinkedIn members"
    # ...and the quieter setting must NOT be described as public.
    quiet = preview["direction"]["who_can_see_it_now"]
    assert "PUBLIC" not in quiet
    assert "does not see it" in quiet.casefold()


def test_open_to_work_has_no_measured_surface_and_the_door_says_so(writes_on):
    """A GATE MAY NOT NAME A TARGET SURFACE NOBODY HAS OPENED.

    The state is read off the profile topcard, which is allowlisted. The
    EDITOR is a modal nothing has ever loaded, so there is no url, no anchor
    and no capture -- and the honest response is a refusal, not a plausible
    path. Inventing one would be the same failure as printing an unmeasured
    reversibility claim, one field over.
    """
    spec = spec_for_action("set_open_to_work")
    assert spec.url_template is None and spec.url_pattern is None

    grant = mint("set_open_to_work", JOB, {})
    with pytest.raises(WriteAttemptError) as excinfo:
        assert_write_url("https://www.linkedin.com/in/me/", grant)
    assert "no measured surface" in str(excinfo.value)

    preview = render_preview(
        spec,
        target=JOB,
        facts=FACTS,
        token="t",
        state="Recruiters only",
        to_state="off",
    )
    assert preview["where"]["url"].startswith("UNMEASURED")


def test_the_measured_surfaces_still_pass_their_own_door(writes_on):
    """THE CONTROL. Without it the refusal above passes on a door that has
    stopped letting anything through at all."""
    grant = mint("save_job", JOB, {})
    url = f"https://www.linkedin.com/jobs/view/{JOB}/"
    assert assert_write_url(url, grant) == url
