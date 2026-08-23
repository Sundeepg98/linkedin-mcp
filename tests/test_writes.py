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
    assert overlap == {"linkedin_save_job", "linkedin_unsave_job"}, overlap


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
    preview = render_preview(spec, target=JOB, facts=FACTS, token=grant.token)

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
            render_preview(spec, target=JOB, facts=facts, token="t")
        assert "live re-read" in str(excinfo.value)


def test_the_gate_will_not_print_an_unmeasured_reversibility_claim(writes_on):
    """THE RULE, ratified 2026-08-23, enforced rather than documented.

    All three specs are unmeasured today, so all three must print UNMEASURED
    and name what would settle it -- not a confident sentence nobody checked.
    """
    for spec in SANCTIONED_WRITES.values():
        preview = render_preview(spec, target=JOB, facts=FACTS, token="t")
        assert spec.reversibility_measured is False
        assert preview["reversibility_measured"] is False
        assert preview["reversibility"].startswith("UNMEASURED")
        assert spec.reversibility_procedure in preview["reversibility"]
        # And the confident version must NOT appear.
        assert not preview["reversibility"].startswith("reversible")


def test_the_gate_does_print_the_claim_once_it_is_measured(writes_on):
    """The control, and the reason the rule is a rule rather than a ban.

    A measured claim IS printed. Without this the assertion above would pass on
    a renderer that had simply lost the ability to say anything.
    """
    spec = spec_for_action("save_job")
    measured = writes.WriteSpec(**{**spec.__dict__, "reversibility_measured": True})
    preview = render_preview(measured, target=JOB, facts=FACTS, token="t")
    assert preview["reversibility"] == spec.reversibility
    assert preview["reversibility_measured"] is True
    assert "UNMEASURED" not in preview["reversibility"]


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


def test_the_toggle_problem_is_recorded_where_it_will_be_hit():
    """The blocker found while pinning those anchors: both are TOGGLES and the
    captures only ever show the OFF state, so nothing here can yet tell 'Save'
    from 'Unsave'. Recorded in the module so it cannot be rediscovered the
    expensive way."""
    doc = writes.perform.__doc__ or ""
    assert "TOGGLES" in doc
    assert "linkedin_saved_jobs" in doc
