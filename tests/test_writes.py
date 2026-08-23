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
door, a gate that DOES render.

WHAT CHANGED ON 2026-08-23, and why most of this file now drives a browser.
The gate used to take the target's ``facts`` and its measured ``state`` as
ARGUMENTS, so every test here could hand it a job that does not exist and a
direction nobody had read -- which is precisely what a caller could do too.
The gate now performs the read ITSELF, so a test cannot describe a page; it has
to serve one. Every gate test below runs the real reader over a FROZEN
CAPTURE in a local headless Chromium, and asserts which urls the gate asked
for. Nothing here reaches the network or an account.

THREE CHECKS IN THIS FILE USED TO BE INCAPABLE OF FAILING, all three found by
a cold review on 2026-08-23 and each proven by a mutation that left the suite
green:

* the ``unknown`` refusal was asserted with ``"unknown" in message``, which the
  WRONG refusal also satisfies because it interpolates the state -- deleting
  the entire unknown branch left every test passing;
* ``assert "this server" in by_server`` passes on its own inverse, since
  ``"NOT this server"`` contains ``"this server"`` -- ``save_job`` could be
  rewritten to claim the exact opposite with nothing going red;
* ``reversibility_class`` was asserted against the set of values that EXIST,
  so all four specs could be flipped to IRREVERSIBLE, silently contradicting
  the sentence printed beside them, with nothing going red.

All three are repaired below and each now carries the mutation that used to
survive it, written down as the thing being prevented rather than as history.
"""

from __future__ import annotations

import ast
import inspect
import time
from pathlib import Path

import pytest

from linkedin_server import readonly, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import (
    GRANT_TTL_SECONDS,
    OBSERVATION_TTL_SECONDS,
    PERMANENTLY_FORBIDDEN,
    SANCTIONED_WRITES,
    WRITES_FLAG,
    assert_write_url,
    consume,
    mint,
    preview,
    spec_for_action,
)
from tests.test_server_surface import FORBIDDEN_TOOLS

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: A posting id that is NOT in any frozen saved list.
JOB = "4600000042"
#: The id of the one job row ``jobs_tracker_row.html`` actually renders.
SAVED_JOB = "4011223344"


def markup(name: str) -> str:
    return (FIXTURE_DIR / f"{name}.html").read_text(encoding="ascii")


#: THE ONE PIECE OF MARKUP HERE THAT LINKEDIN DID NOT SERVE, and it is derived
#: rather than captured for a reason worth stating: a self-consistent NON-EMPTY
#: saved list cannot be photographed on this account, because he has nothing
#: saved. That is the same reason the save control's ON state has never been
#: seen. So the frozen tracker capture is taken and LinkedIn's own Saved count
#: is edited from 0 to 1 -- one field, so that the single row the page really
#: does render is reconciled by a count that agrees with it.
#:
#: It therefore exercises THE READER'S LOGIC and measures nothing about
#: LinkedIn. Every state it produces is labelled DERIVED below. The frozen
#: capture itself, count 0 beside one rendered row, is a genuine disagreement
#: and is used as one.
_TRACKER_RAW = markup("jobs_tracker_row")
SAVED_LIST_OF_ONE = _TRACKER_RAW.replace("Saved &#183; 0", "Saved &#183; 1")
SAVED_LIST_PARTIAL = _TRACKER_RAW.replace("Saved &#183; 0", "Saved &#183; 9")


class FixtureNavigator:
    """Serves frozen captures where LinkedIn would be, and RECORDS the asks.

    The recording is the point. A gate that reads for itself has to be shown
    actually opening pages, and shown opening the RIGHT ones -- the assertion
    that a follow costs one load and a save costs two is only meaningful
    against something that counted.
    """

    def __init__(self, pages: dict[str, str]):
        self.pages = dict(pages)
        self.gotos: list[str] = []

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        html = self.pages.get(url)
        if html is None:
            raise AssertionError(
                f"the gate asked for {url!r}, which this test did not freeze. "
                f"It froze {sorted(self.pages)}."
            )
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return url


def _pages(*, target, posting=None, saved=None, profile=None) -> dict[str, str]:
    out: dict[str, str] = {}
    if posting is not None:
        out[f"https://www.linkedin.com/jobs/view/{target}/"] = markup(posting)
    if saved is not None:
        out[writes.SAVED_LIST_URL] = (
            saved if saved.lstrip().startswith("<") else markup(saved)
        )
    if profile is not None:
        out[writes.PROFILE_URL] = markup(profile)
    return out


@pytest.fixture
async def browser_page():
    """ONE local headless Chromium for the whole test, reused across gate calls.

    Measured 2026-08-23 on this machine: a cold launch-and-close costs 1.35s
    while five ``set_content`` loads on an already-running browser cost 0.89s
    between them. Practically the entire price is the launch, so a browser per
    GATE CALL rather than per test was paying it about sixty-five times to run
    ninety-odd page loads. Nothing crosses between tests: the content is
    replaced on every load and the grant registries are cleared by the autouse
    fixture below.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            yield await browser.new_page()
        finally:
            await browser.close()


async def _gate(
    page,
    action: str,
    *,
    target: str = JOB,
    posting: str = "job_detail",
    saved: str = "jobs_tracker_empty",
    profile: str = "profile_topcard",
    to_state=None,
):
    """Run the real gate over frozen captures. Returns ``(block, navigator)``."""
    spec = spec_for_action(action)
    nav = FixtureNavigator(
        _pages(target=target, posting=posting, saved=saved, profile=profile)
    )

    block = await preview(
        spec, target=target, navigator=nav, page=page, to_state=to_state
    )
    return block, nav


async def _observe(
    page,
    action: str,
    *,
    target: str = JOB,
    posting: str = "job_detail",
    saved: str = "jobs_tracker_empty",
    profile: str = "profile_topcard",
):
    """One live reading, receipt still live. The only way to reach ``mint``."""
    spec = spec_for_action(action)
    nav = FixtureNavigator(
        _pages(target=target, posting=posting, saved=saved, profile=profile)
    )

    return await writes.observe(nav, page, spec, target)


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


def _bare_grant(action: str = "save_job", target: str = JOB) -> writes.WriteGrant:
    """A grant object built directly, for the tests about the URL DOOR and the
    refusal in ``perform`` rather than about minting.

    Deliberately not a way round :func:`mint`. ``assert_write_url`` reads only
    the grant's action and target, and HOW a grant comes to exist is the whole
    subject of section 11, which drives the real path. Building one here keeps
    six parametrised url cases from launching six browsers to settle a question
    about a string.
    """
    return writes.WriteGrant(
        action=action,
        target=target,
        token="not-a-minted-token",
        minted_at=time.monotonic(),
    )


def _functions_assigning_into(source: str, name: str) -> set[str]:
    """Every function in ``source`` that assigns into ``name[...]``.

    Attributed to the INNERMOST enclosing function: a nested helper is counted
    as itself rather than as its parent, so hiding a second writer one scope
    down does not make it disappear.
    """
    tree = ast.parse(source)
    found: set[str] = set()
    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        stack = list(func.body)
        while stack:
            node = stack.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            targets: list = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                targets = [node.target]
            for target in targets:
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == name
                ):
                    found.add(func.name)
            stack.extend(ast.iter_child_nodes(node))
    return found



# ---------------------------------------------------------------------------
# 1. Off by default
# ---------------------------------------------------------------------------


def test_writes_are_off_unless_deliberately_enabled(monkeypatch):
    monkeypatch.delenv(WRITES_FLAG, raising=False)
    assert writes.writes_enabled() is False
    with pytest.raises(WriteAttemptError) as excinfo:
        mint("save_job", JOB, receipt="anything")
    assert "disabled" in str(excinfo.value)


@pytest.mark.parametrize("value", ["", "0", "false", "no", "off", "maybe"])
def test_only_an_explicit_yes_turns_writes_on(monkeypatch, value):
    monkeypatch.setenv(WRITES_FLAG, value)
    assert writes.writes_enabled() is False


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on"])
def test_the_flag_does_turn_on(monkeypatch, value):
    """THE CONTROL. Without it the four refusals above pass on a reader that
    always says no."""
    monkeypatch.setenv(WRITES_FLAG, value)
    assert writes.writes_enabled() is True


# ---------------------------------------------------------------------------
# 2. The grant is single-use, action-bound, target-bound and short-lived
# ---------------------------------------------------------------------------


async def test_a_grant_redeems_once(writes_on, browser_page):
    """The positive case first: the machinery genuinely works."""
    observation = await _observe(browser_page, "save_job")
    grant = mint("save_job", JOB, receipt=observation.receipt)
    redeemed = consume(grant.token, action="save_job", target=JOB)
    assert redeemed.action == "save_job"
    assert redeemed.target == JOB
    assert redeemed.consumed is True
    # And the grant carries the reading it was minted from, which is the only
    # durable evidence that a preview looked before it offered.
    assert redeemed.observation is observation


async def test_a_grant_cannot_be_redeemed_twice(writes_on, browser_page):
    observation = await _observe(browser_page, "save_job")
    grant = mint("save_job", JOB, receipt=observation.receipt)
    consume(grant.token, action="save_job", target=JOB)
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="save_job", target=JOB)
    assert "already" in str(excinfo.value)


async def test_a_token_minted_for_one_job_will_not_act_on_another(
    writes_on,
    browser_page,
):
    """The confirm gate named a posting. This is what makes that binding real."""
    observation = await _observe(browser_page, "save_job")
    grant = mint("save_job", JOB, receipt=observation.receipt)
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="save_job", target="9999999")
    assert "target" in str(excinfo.value)


async def test_a_token_minted_for_one_verb_will_not_perform_another(
    writes_on,
    browser_page,
):
    observation = await _observe(browser_page, "save_job")
    grant = mint("save_job", JOB, receipt=observation.receipt)
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="unsave_job", target=JOB)
    assert "minted for" in str(excinfo.value)


async def test_an_expired_token_performs_nothing(writes_on, monkeypatch, browser_page):
    """The TTL is what makes an unattended write structurally impossible."""
    observation = await _observe(browser_page, "save_job")
    grant = mint("save_job", JOB, receipt=observation.receipt)
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


def test_a_reading_dies_sooner_than_the_confirmation_built_on_it():
    """Two clocks, and the shorter one is the reading. That ordering is the
    claim: a grant is a HUMAN holding a confirmation and may be two minutes
    old; a reading is a measurement of LinkedIn and is stale the moment
    anything else touches the account."""
    assert OBSERVATION_TTL_SECONDS < GRANT_TTL_SECONDS
    assert 10 <= OBSERVATION_TTL_SECONDS <= 60


@pytest.mark.parametrize("bogus", ["", None, 1, True, "not-a-real-token"])
def test_nothing_that_is_not_a_token_will_do(writes_on, bogus):
    """Specifically: a boolean will not do. `confirm=True` is a flag a caller
    can set without ever having seen a preview; a token is not."""
    with pytest.raises(WriteAttemptError):
        consume(bogus, action="save_job", target=JOB)


def test_a_grant_cannot_be_minted_for_an_unsanctioned_action(writes_on):
    for action in ("apply", "connect", "send_inmail", "post", "endorse"):
        with pytest.raises(WriteAttemptError) as excinfo:
            mint(action, JOB, receipt="anything")
        assert "not a sanctioned write" in str(excinfo.value)


def test_a_target_that_is_not_an_integer_is_refused(writes_on):
    """The url is BUILT from this. A string here is a string in a url, which is
    the thing an allowlist exists to prevent."""
    for target in ("", "abc", "123/../456", "4600000042?apply=1", "-1"):
        with pytest.raises(WriteAttemptError):
            mint("save_job", target, receipt="anything")


def test_grants_are_never_written_to_disk(writes_on):
    """A grant that outlived the process is a grant a scheduler could pick up.

    The same argument covers the readings: a receipt on disk is a grant waiting
    to be minted, so neither registry may ever be persisted.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    for persisted in ("open(", "json.dump", "write_text", "pickle", "sqlite"):
        assert persisted not in source, persisted


async def test_the_kill_switch_drops_the_readings_as_well_as_the_grants(
    writes_on,
    browser_page,
):
    """Half a teardown is not a teardown: a surviving receipt is permission to
    mint a grant after the switch was thrown."""
    observation = await _observe(browser_page, "save_job")
    assert writes._OBSERVED
    writes.discard_all()
    assert writes._OBSERVED == {} and writes._GRANTS == {}
    with pytest.raises(WriteAttemptError):
        mint("save_job", JOB, receipt=observation.receipt)


# ---------------------------------------------------------------------------
# 3. The narrowed door -- and the read door untouched beside it
# ---------------------------------------------------------------------------


def test_the_write_url_is_rebuilt_from_the_grant_not_taken_from_a_caller(writes_on):
    grant = _bare_grant()
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
    grant = _bare_grant()
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
# 5. The gate a human reads -- built from a read the gate performed itself
# ---------------------------------------------------------------------------

#: The verdict each action carries, PINNED PER ACTION. It used to be asserted
#: as ``in {"REVERSIBLE", "IRREVERSIBLE", "STILL-UNKNOWN"}`` -- the set of all
#: values that exist, one of which is the dataclass default -- so a cold review
#: flipped all four specs to IRREVERSIBLE and the whole suite stayed green
#: while the gate printed IRREVERSIBLE beside "reversible by unsaving the same
#: posting". A check that cannot distinguish a verdict from its opposite is
#: not checking the verdict.
REVERSIBILITY_CLASS = {
    "save_job": "REVERSIBLE",
    "unsave_job": "REVERSIBLE",
    "follow_company": "REVERSIBLE",
    "set_open_to_work": "REVERSIBLE",
}


async def test_the_gate_names_the_target_in_words_a_person_can_check(
    writes_on,
    browser_page,
):
    block, _nav = await _gate(browser_page, "save_job")
    assert block["performed"] is False
    assert block["where"]["job_id"] == JOB
    assert block["to_confirm"] in writes._GRANTS
    assert "NOTHING has been done" in block["what_happens_next"]
    # The title and employer came OFF THE PAGE. Asserted by finding them in
    # the frozen markup rather than by typing the invented company name into
    # this file, which is the convention the fixture suites already keep.
    posting = markup("job_detail")
    assert block["where"]["title"] and block["where"]["company"]
    assert block["where"]["company"] in posting


async def test_the_facts_track_the_page_and_not_the_request(writes_on, browser_page):
    """THE CONTROL for the assertion above, and the one that would have caught
    the old defect on its own: two identical requests over two different
    postings must not produce the same block."""
    one, _ = await _gate(browser_page, "save_job", posting="job_detail")
    two, _ = await _gate(browser_page, "save_job", posting="job_detail_following_hydrated")
    assert one["where"]["company"] != two["where"]["company"]
    assert one["where"]["title"] != two["where"]["title"]


async def test_the_gate_refuses_when_the_posting_did_not_render(
    writes_on,
    browser_page,
):
    """An id is not something a human can check, so a gate that could not read
    the posting names nothing he can verify and refuses.

    ``job_detail_following.html`` is the honest shape of this: a real capture,
    taken before the page settled, carrying LinkedIn's server-rendered document
    title and no posting behind it.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "save_job", posting="job_detail_following")
    assert "no posting could be read from it" in str(excinfo.value)


async def test_the_gate_prints_every_measured_verdict_with_its_evidence(
    writes_on,
    browser_page,
):
    """THE RULE, ratified 2026-08-23, and what happened to it.

    When it landed, all four specs printed UNMEASURED, and the rule was
    described as "biting its own author". The measurement was then performed --
    entirely through READS -- so all four now print a verdict. That is the rule
    being satisfied, not relaxed, and this test is the half that says so: a
    verdict must arrive with its EVIDENCE, its OWNER and its RESIDUE, because a
    bare "reversible" is the confident string the rule exists to stop whether
    or not somebody has since done the measuring.
    """
    cases = {
        "save_job": {},
        "unsave_job": {"target": SAVED_JOB, "saved": SAVED_LIST_OF_ONE},
        "follow_company": {},
        "set_open_to_work": {
            "target": "self",
            "to_state": "All LinkedIn members",
        },
    }
    assert set(cases) == {spec.action for spec in SANCTIONED_WRITES.values()}

    for action, kwargs in cases.items():
        spec = spec_for_action(action)
        block, _nav = await _gate(browser_page, action, **kwargs)
        assert spec.reversibility_measured is True, action
        assert block["reversibility_measured"] is True
        assert "UNMEASURED" not in block["reversibility"]
        assert block["reversibility_class"] == REVERSIBILITY_CLASS[action], action
        # A verdict with no evidence line is the thing this rule forbids.
        assert "MEASURED 2026-08-23" in block["reversibility_evidence"], action
        assert len(block["reversible_by"]) > 40, action
        assert len(block["what_it_cannot_undo"]) > 40, action


def test_every_verdict_is_pinned_to_ITS_ACTION_not_to_the_set_of_verdicts():
    """2c, repaired at the spec.

    The mutation that used to survive: set every ``reversibility_class`` to
    IRREVERSIBLE. Under the old assertion all four still passed, because
    IRREVERSIBLE is a member of the set of values that exist. Pinning per
    action is what makes the headline claim of the wave -- all four REVERSIBLE
    -- an assertion rather than a sentence in a commit message.
    """
    assert set(REVERSIBILITY_CLASS) == {s.action for s in SANCTIONED_WRITES.values()}
    for spec in SANCTIONED_WRITES.values():
        assert spec.reversibility_class == REVERSIBILITY_CLASS[spec.action], spec.action


async def test_a_verdict_that_contradicts_its_own_sentence_will_not_render(
    writes_on,
    monkeypatch,
    browser_page,
):
    """2c, repaired as a MECHANISM rather than only as an assertion.

    Pinning the class per action stops THIS repo drifting. It does not stop the
    two fields disagreeing -- a future spec could carry IRREVERSIBLE beside
    "reversible by unsaving the same posting" and the pin would simply be
    updated to match. So the gate now refuses to render a block whose one-word
    verdict contradicts the sentence printed beside it: two fields in
    disagreement tell the reader less than one field saying nothing, because he
    cannot tell which half to believe.
    """
    save = spec_for_action("save_job")
    flipped = writes.WriteSpec(
        **{**save.__dict__, "reversibility_class": "IRREVERSIBLE"}
    )
    monkeypatch.setitem(writes.SANCTIONED_WRITES, "linkedin_save_job", flipped)
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "save_job")
    assert "IRREVERSIBLE while the sentence beside it" in str(excinfo.value)


async def test_that_refusal_does_not_fire_on_the_specs_as_they_stand(
    writes_on,
    browser_page,
):
    """THE CONTROL. Without it the refusal above passes on a renderer that has
    started refusing everything."""
    for spec in SANCTIONED_WRITES.values():
        assert writes._reversibility_disagreement(spec) is None, spec.action
    block, _ = await _gate(browser_page, "save_job")
    assert block["reversibility_class"] == "REVERSIBLE"


async def test_the_gate_still_refuses_to_print_an_unmeasured_claim(
    writes_on,
    monkeypatch,
    browser_page,
):
    """THE CONTROL for the measured-reversibility rule, and it matters more now
    than when it was written.

    Every real spec is measured today, so the assertions above would pass on a
    renderer that had lost the ability to say UNMEASURED at all -- which is
    precisely how a rule dies: not repealed, just never exercised again. So the
    refusal is driven against a spec that is unmeasured by construction.
    """
    unmeasured = writes.WriteSpec(
        **{
            **spec_for_action("save_job").__dict__,
            "reversibility_measured": False,
            "reversibility_class": "STILL-UNKNOWN",
        }
    )
    monkeypatch.setitem(writes.SANCTIONED_WRITES, "linkedin_save_job", unmeasured)
    block, _ = await _gate(browser_page, "save_job")
    assert block["reversibility_measured"] is False
    assert block["reversibility"].startswith("UNMEASURED")
    assert unmeasured.reversibility_procedure in block["reversibility"]
    assert not block["reversibility"].startswith("reversible")


async def test_an_unmeasured_claim_may_not_wear_a_measured_verdict(
    writes_on,
    monkeypatch,
    browser_page,
):
    """The half of the rule the class field was quietly outside of: printing
    UNMEASURED prose beside ``reversibility_class: REVERSIBLE`` is the
    confident string with an extra step."""
    half = writes.WriteSpec(
        **{
            **spec_for_action("save_job").__dict__,
            "reversibility_measured": False,
        }
    )
    monkeypatch.setitem(writes.SANCTIONED_WRITES, "linkedin_save_job", half)
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "save_job")
    assert "UNMEASURED" in str(excinfo.value)


async def test_a_follow_says_plainly_that_this_server_cannot_take_it_back(
    writes_on,
    browser_page,
):
    """The field most likely to mislead, and 2b: it was NOT being asserted.

    "Reversible" reads as "this tool can undo it". For ``follow_company`` that
    is FALSE -- no unfollow is sanctioned, so a follow performed here is one
    only he can reverse, by hand. Two of the four are undoable by this server
    and two are not, and the gate has to say which it is holding.

    THE MUTATION THAT USED TO SURVIVE: rewrite ``save_job.reversible_by`` to
    "HIM, by hand. NOT this server..." -- the exact inversion -- and the old
    ``assert "this server" in by_server`` still passed, because "NOT this
    server" CONTAINS "this server". The positive half was a substring of the
    negative half. It is now asserted in both directions.
    """
    by_server = spec_for_action("save_job").reversible_by
    assert "this server" in by_server
    assert "NOT this server" not in by_server
    assert "Not this server" not in by_server

    for action in ("follow_company", "set_open_to_work"):
        by_hand = spec_for_action(action).reversible_by
        assert "NOT this server" in by_hand or "Not this server" in by_hand, action

    # And the distinction survives into the block he actually reads, which is
    # the only place it can do him any good.
    save_block, _ = await _gate(browser_page, "save_job")
    follow_block, _ = await _gate(browser_page, "follow_company")
    assert save_block["reversible_by"] != follow_block["reversible_by"]
    assert "NOT this server" in follow_block["reversible_by"]
    assert "NOT this server" not in save_block["reversible_by"]


def test_every_sanctioned_spec_carries_a_procedure_that_would_settle_it():
    """An unmeasured claim must name its own fix, or it is just a caveat."""
    for spec in SANCTIONED_WRITES.values():
        assert len(spec.reversibility_procedure) > 60, spec.action


# ---------------------------------------------------------------------------
# 6. Nothing can actually act
# ---------------------------------------------------------------------------


async def test_the_one_function_that_could_act_refuses(writes_on):
    grant = _bare_grant()
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
        mint(cut, JOB, receipt="anything")
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

    The save control's ON state has never been observed and cannot be: he has
    no saved posting to observe it on. So the direction comes from the LIST --
    LinkedIn's own per-tab count with a distinguishable empty state. A
    different source, not a weaker one, and it costs a second page load. A gate
    that reported this as "read off the button" would be describing a
    measurement it did not make.
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


async def test_open_to_work_names_the_audience_of_the_destination_in_the_gate(
    writes_on,
    browser_page,
):
    """THE POINT OF SPECCING IT AT ALL, and THE CONTROL for the two refusals
    above.

    Someone job-hunting while employed. This is the single setting in the whole
    design a current employer can read, so the gate does not repeat LinkedIn's four
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
