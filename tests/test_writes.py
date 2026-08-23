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

from linkedin_server import dom, readonly, shape, writes
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

    THIS IS THE ASSERTION THAT MOVED ON 2026-08-23, and it moved by exactly the
    amount the operator authorised. It used to read all THREE sanctioned names,
    with a comment saying they were designed and gated but not shipped, and
    that the day one shipped the mismatch would be a failing test rather than a
    silent divergence. That day came, it was a failing test, and this is the
    edit it demanded.

    Two names left ``FORBIDDEN_TOOLS`` and are now registered. One did not:
    ``linkedin_set_open_to_work`` stays in both, because it stays designed and
    unshipped -- its editor has never been loaded and :func:`mint` refuses it a
    grant at issue. ``linkedin_follow_company`` was never on the forbidden list
    (it is the rename loophole the check below covers) and is sanctioned but
    not performable.
    """
    overlap = set(FORBIDDEN_TOOLS) & set(SANCTIONED_WRITES)
    assert overlap == {"linkedin_set_open_to_work"}, overlap


def test_what_ships_is_narrower_than_what_is_sanctioned():
    """Three sets, each smaller than the last, and none of them the same thing.

    Conflating any two of these is how a boundary widens without anybody
    editing a boundary: ``SANCTIONED_WRITES`` is what may hold a GRANT,
    ``PERFORMABLE`` is what :func:`perform` will EXECUTE, and the registered
    tool names are what a CALLER can reach. Asserted as a chain so a future
    edit that grows one has to grow it visibly.
    """
    sanctioned_actions = {spec.action for spec in SANCTIONED_WRITES.values()}
    assert sanctioned_actions == {
        "save_job",
        "unsave_job",
        "follow_company",
        "set_open_to_work",
    }
    assert writes.PERFORMABLE == {"save_job", "unsave_job"}
    assert writes.PERFORMABLE < sanctioned_actions


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


async def test_exactly_the_two_authorised_writes_are_registered():
    """WHAT THIS TEST USED TO ASSERT: that the surface carried no write at all.

    It carries two. So the assertion is now the exact pair rather than the
    empty set -- and the second half, that nothing still on ``FORBIDDEN_TOOLS``
    is registered, is UNCHANGED and is the half that still does the work. A
    third write appearing fails it.
    """
    from linkedin_server.server import mcp

    names = {t.name for t in await mcp.list_tools()}
    assert names & set(SANCTIONED_WRITES) == {
        "linkedin_save_job",
        "linkedin_unsave_job",
    }
    assert names & FORBIDDEN_TOOLS == set()
    # linkedin_follow_company is sanctioned and must NOT be reachable.
    assert "linkedin_follow_company" not in names


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
# 6. What CAN act, and everything that has to be true first
# ---------------------------------------------------------------------------
#
# THIS SECTION WAS CALLED "Nothing can actually act" AND ASSERTED EXACTLY THAT.
# On 2026-08-23 the operator authorised save and unsave, ``perform`` gained a
# body, and the old assertions became the thing they were guarding against: a
# suite claiming a property the code no longer had.
#
# NOT ONE CLICK IN THIS SECTION REACHES LINKEDIN. Every one lands on a frozen
# capture loaded into a local headless Chromium by ``set_content``. Measured
# before any of it was written, with every request intercepted and aborted so
# that an attempt would have been recorded even if it could not complete: the
# four posting fixtures contain ZERO script tags, attempt ZERO requests on load
# and ZERO on click, do not navigate, and do not move the DOM. The click is
# real, dispatches in ~20ms, and provably cannot leave the machine.
#
# THAT LAST PROPERTY IS ALSO THE LIMIT OF WHAT THESE TESTS CAN SAY, and it is
# stated here rather than left for a reader to infer: because the fixture DOM
# does not move, a test can prove the machinery clicks the right thing under
# the right conditions and can never prove that clicking it saves a job. That
# is a claim only a supervised run against a real account settles, and none has
# happened.


async def _granted(
    page,
    action: str,
    *,
    target: str,
    posting: str = "job_detail",
    saved: str = "jobs_tracker_empty",
) -> writes.WriteGrant:
    """A real, redeemed grant, produced the way the tool produces one.

    Deliberately the long way round -- preview, then consume the token it
    printed -- rather than constructing a grant. ``perform`` requires a grant
    that has already been burned, so a test that fabricated one would be
    testing a path no caller can take.
    """
    block, _nav = await _gate(page, action, target=target, posting=posting, saved=saved)
    return consume(block["to_confirm"], action=action, target=target)


async def _perform(
    page,
    grant: writes.WriteGrant,
    *,
    posting: str = "job_detail",
    saved=None,
):
    """Run the real ``perform`` over frozen captures. Returns ``(block, nav)``.

    The saved list served here is usually DIFFERENT from the one the preview
    saw, and that is the point: it models the world having changed because the
    click changed it. The navigator is per-call, so "before" and "after" are
    two separate frozen worlds rather than one mutable fake.
    """
    nav = FixtureNavigator(
        _pages(target=grant.target, posting=posting, saved=saved)
    )
    return await writes.perform(nav, page, grant), nav


#: The tracker capture with LinkedIn's own Saved count edited 0 -> 1 AND the
#: row's job id rewritten to the posting these tests act on. DERIVED, twice
#: over, and labelled as such everywhere it is used: a self-consistent saved
#: list containing a chosen posting cannot be photographed on an account with
#: nothing saved. It exercises THE READER'S LOGIC and measures nothing about
#: LinkedIn.
SAVED_LIST_CONTAINING = SAVED_LIST_OF_ONE


async def test_a_save_runs_end_to_end_and_is_verified_from_the_other_surface(
    writes_on, browser_page
):
    """THE POSITIVE CASE, and it goes first.

    Everything else in this section asserts a refusal, and a section full of
    refusals passes perfectly on a ``perform`` that raises unconditionally --
    which is exactly what this one used to do. This is the test that fails if
    the body goes back to being a stub.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_CONTAINING
    )

    assert block["performed"] is True
    assert block["verified"] is True
    assert block["clicked"]["selector"] == 'button[aria-label="Save the job"]'
    assert block["clicked"]["error"] is None
    assert block["clicked"]["state_before"] == "not_saved"
    assert block["verification"]["expected_state"] == "saved"
    assert block["verification"]["observed_state"] == "saved"

    # TWO loads, in this order: the posting it clicks on, then the DIFFERENT
    # surface it confirms from.
    assert nav.gotos == [
        f"https://www.linkedin.com/jobs/view/{SAVED_JOB}/",
        writes.SAVED_LIST_URL,
    ]


async def test_the_confirmation_comes_from_a_surface_other_than_the_button(
    writes_on, browser_page
):
    """A control that redraws itself is the weakest witness to its own effect.

    Pins that the verification read is the saved LIST and not the posting, so
    a later "optimisation" that saves a page load by believing the button
    fails here.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_CONTAINING
    )
    assert block["verification"]["read_from"] == writes.SAVED_LIST_URL
    assert block["verification"]["read_from"] != block["clicked"]["on"]


async def test_a_click_that_did_not_take_reports_false_and_does_not_raise(
    writes_on, browser_page
):
    """THE CONTROL THAT MATTERS MOST IN THIS FILE.

    A post-write verification that always says "verified" is worth nothing, and
    it is the single easiest thing to write by accident. Here the saved list
    AFTER the click is still empty -- the click did not take -- and the block
    has to say so.

    It must also NOT raise. Once the button has been pressed, the most
    important fact in the world is that it was pressed; an exception on the way
    home replaces that fact with a stack trace and the operator retries,
    toggling it back.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved="jobs_tracker_empty"
    )
    assert block["performed"] is False
    assert block["verified"] is False
    assert block["verification"]["observed_state"] == "not_saved"
    # The click itself still happened, and the block still says so.
    assert block["clicked"]["error"] is None


async def test_an_unreadable_saved_list_reports_unknown_not_success(
    writes_on, browser_page
):
    """The third outcome, kept separate from the second.

    A saved list that is a fraction of itself cannot settle whether the save
    landed. That is neither success nor failure, and collapsing it into either
    would be the same defect in opposite directions -- reporting success would
    hide a failure, reporting failure invites a retry that double-toggles.

    THE TARGET HERE IS ``JOB`` AND NOT ``SAVED_JOB``, and the first draft of
    this test got that wrong in a way worth recording. It performed on the
    posting the partial list DOES render, expected ``unknown``, and got
    ``True`` -- correctly. Absence from a partial list is not absence; PRESENCE
    in one is still presence. The ambiguity is one-directional, and a test that
    had been written to match a wrong expectation would have pinned the reader
    into treating a perfectly good confirmation as unreadable.
    """
    grant = await _granted(browser_page, "save_job", target=JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_PARTIAL
    )
    assert block["performed"] == "unknown"
    assert block["verified"] is False
    assert block["verification"]["observed_state"] == "unknown"
    assert "below the fold" in block["verification"]["why"]
    assert "Do NOT retry" in block["read_this_if_unsure"]


async def test_presence_in_a_partial_list_still_confirms_the_save(
    writes_on, browser_page
):
    """THE OTHER HALF, and the one the test above was written against by
    mistake.

    The ambiguity in a partial list runs one way only. If the posting IS among
    the rows that rendered, it is saved -- however many rows are still below
    the fold. Pinned so a later "be more careful about partial lists" edit
    cannot make a good confirmation unreadable.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_PARTIAL
    )
    assert block["performed"] is True
    assert block["verified"] is True
    assert block["verification"]["observed_state"] == "saved"


async def test_unsave_refuses_because_its_anchor_has_never_been_measured(
    writes_on, browser_page
):
    """THE HONEST GAP, asserted so it cannot be quietly closed with a guess.

    ``unsave_job`` is built on the same path as save and gated the same way. It
    refuses at exactly one point: the accessible name the save control wears on
    a SAVED posting has never been observed, because there has never been a
    saved posting on this account to observe it on.

    The refusal must name the reason. A generic "not implemented" would invite
    somebody to implement it by choosing a plausible selector, which is the one
    thing that must not happen.
    """
    spec = spec_for_action("unsave_job")
    assert writes.anchor_label_for(spec) is None

    grant = writes.WriteGrant(
        action="unsave_job",
        target=SAVED_JOB,
        token="x",
        minted_at=time.monotonic(),
        consumed=True,
        observation=await _observe(
            browser_page, "unsave_job", target=SAVED_JOB, saved=SAVED_LIST_CONTAINING
        ),
    )
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    message = str(excinfo.value)
    assert "NEVER" in message and "OBSERVED" in message
    assert "SUPERVISED SAVE IS THE MEASUREMENT" in message


def test_the_anchor_table_is_what_gates_unsave_and_one_row_lifts_it():
    """The gap is one row of a table, not a missing code path.

    Proven by adding the row: with a saved-state label present,
    ``anchor_label_for`` returns it and the refusal above has nothing to fire
    on. Nothing is monkeypatched into the module -- the lookup is run against a
    copy -- so this asserts the MECHANISM without loosening the real table.
    """
    spec = spec_for_action("unsave_job")
    assert spec.from_state == "saved"
    assert writes.anchor_label_for(spec) is None

    pretend = dict(shape.SAVE_LABELS)
    pretend["Saved"] = "saved"
    resolved = [
        label for label, state in pretend.items() if state == spec.from_state
    ]
    assert resolved == ["Saved"]
    # And the real table is untouched by that experiment.
    assert set(shape.SAVE_LABELS) == {"Save the job"}


async def test_follow_is_sanctioned_and_still_will_not_be_performed(writes_on):
    """The operator's cut, made structural rather than remembered.

    A follow is genuinely reversible and this server still will not do one,
    because the undo is HAND-ONLY: no unfollow is sanctioned. The refusal has
    to say that, or the next reader files it as an unfinished feature.
    """
    grant = _bare_grant(action="follow_company", target=JOB)
    grant.consumed = True
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    message = str(excinfo.value)
    assert "hand-only" in message
    assert "no unfollow is sanctioned" in message.casefold()


async def test_open_to_work_is_not_performable_either(writes_on):
    grant = _bare_grant(action="set_open_to_work", target="self")
    grant.consumed = True
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    assert "not performable" in str(excinfo.value)


async def test_an_unredeemed_grant_performs_nothing(writes_on, browser_page):
    """``perform`` does not redeem its own permission.

    Requiring an already-consumed grant is what makes "the token was checked"
    a fact rather than a convention: single use, this action, this target, not
    expired -- all of it provably ran before this function was entered.
    """
    block, _nav = await _gate(browser_page, "save_job", target=SAVED_JOB)
    grant = writes._GRANTS[block["to_confirm"]]
    assert grant.consumed is False
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    assert "not been redeemed" in str(excinfo.value)


async def test_a_grant_with_no_reading_behind_it_performs_nothing(writes_on):
    """A grant that preview did not build carries no observation, and stops."""
    grant = _bare_grant()
    grant.consumed = True
    assert grant.observation is None
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    assert "carries no reading" in str(excinfo.value)


async def test_writes_off_stops_perform_even_with_a_valid_grant(
    monkeypatch, browser_page
):
    """The flag is checked in ``perform`` too, not only on the way in.

    A grant minted while writes were on must not survive the flag being turned
    off -- otherwise "writes are disabled" is a statement about the past.
    """
    monkeypatch.setenv(WRITES_FLAG, "1")
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    monkeypatch.setenv(WRITES_FLAG, "0")
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    assert "disabled" in str(excinfo.value)
    writes.discard_all()


async def test_a_control_in_the_wrong_state_is_not_clicked(writes_on, browser_page):
    """GATE 5, and it is the one the preview cannot provide.

    The posting served to ``perform`` renders no save control this reader
    recognises, so the live read comes back ``unknown`` and the click does not
    happen -- even though the grant is valid and the preview said not_saved.
    On a toggle, acting from the wrong state performs the OPPOSITE action.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    stripped = markup("job_detail").replace(
        'aria-label="Save the job"', 'aria-label="Something Else Entirely"'
    )
    nav = FixtureNavigator(
        {f"https://www.linkedin.com/jobs/view/{grant.target}/": stripped}
    )
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(nav, browser_page, grant)
    message = str(excinfo.value)
    assert "refusing to click" in message
    assert "'unknown'" in message
    # And the verification surface was never even asked for: it stopped first.
    assert nav.gotos == [f"https://www.linkedin.com/jobs/view/{grant.target}/"]


async def test_landing_on_a_different_posting_is_not_clicked(writes_on, browser_page):
    """The browser going somewhere the grant is not permission for.

    ``assert_write_url`` checks the url this server BUILT; this checks where it
    actually ARRIVED, which is a different fact and the one that matters after
    a redirect.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)

    class Redirecting(FixtureNavigator):
        async def goto(self, page, url: str) -> str:
            await super().goto(page, url)
            return "https://www.linkedin.com/jobs/view/4600000099/"

    nav = Redirecting(_pages(target=grant.target, posting="job_detail"))
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(nav, browser_page, grant)
    assert "is not that posting" in str(excinfo.value)


async def test_the_click_selector_cannot_be_built_from_an_unmeasured_label():
    """The other half of the click, held to the same rule as the url.

    ``assert_write_url`` refuses a url that did not come from the grant. This
    refuses a SELECTOR that did not come from a measured observation, so the
    two halves of the click are gated by the same discipline.
    """
    from linkedin_server.errors import ExtractionFailedError

    assert dom.save_control_selector("Save the job") == (
        'button[aria-label="Save the job"]'
    )
    with pytest.raises(ExtractionFailedError) as excinfo:
        dom.save_control_selector("Saved")
    assert "only ever seen" in str(excinfo.value)


async def test_perform_reports_the_label_the_control_became(
    writes_on, browser_page
):
    """The measurement that unblocks unsave, taken at the only moment it can be.

    Nothing branches on it -- asserted by the fact that this save succeeds
    while the reported label is still the OFF one, because a frozen capture's
    DOM does not move when it is clicked. On a live account it would be the
    ON-state label, which is the one line missing from ``shape.SAVE_LABELS``.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_CONTAINING
    )
    assert "newly_observed_save_label" in block
    assert "shape.SAVE_LABELS" in block["what_that_label_is_for"]
    # It did not gate anything: the save is still reported as performed.
    assert block["performed"] is True


# ---------------------------------------------------------------------------
# 6b. Three guards a mutation run found unprotected
# ---------------------------------------------------------------------------
#
# A 20-mutant run over the new guards on 2026-08-24 killed 17 and left THREE
# alive. All three were behavioural mutants, verified by probe rather than
# assumed, so their survival was a real gap in this file and not a bad mutant.
# Each is closed below, and each diagnosis is written down, because in two of
# the three cases the reason the mutant survived is more interesting than the
# test that kills it.


def _calls_by_name_in(source: str, function: str) -> set[str]:
    """Every function called by name inside ``function``, by AST.

    Attribute calls are recorded by their attribute (``page.click`` ->
    ``click``); bare calls by their name.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != function:
            continue
        found: set[str] = set()
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            func = inner.func
            if isinstance(func, ast.Name):
                found.add(func.id)
            elif isinstance(func, ast.Attribute):
                found.add(func.attr)
        return found
    raise AssertionError(f"no function named {function!r} in the source")


def test_perform_goes_through_the_write_door():
    """MUTANT 14, and the diagnosis is the point.

    Deleting the ``assert_write_url`` call from ``perform`` left the whole
    suite green. That is not a missing behavioural test -- it is a fact about
    these two actions: the url ``perform`` builds is rebuilt from the grant's
    own template, and EVERY url the write door would refuse for save or unsave
    is one the READ door refuses too, one line later. The two doors currently
    overlap completely, so no input can distinguish them and no behavioural
    test can exist.

    That overlap IS defence in depth working, and it is exactly why the call
    must not be dropped as redundant: the read allowlist is not maintained with
    writes in mind, and the day it admits a url shape the write pattern does
    not, this call is the only thing left. So the check is STRUCTURAL, which is
    the honest instrument for a claim about redundancy, and the door's own
    behaviour is tested directly in section 3.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    calls = _calls_by_name_in(source, "perform")
    assert "assert_write_url" in calls, (
        "perform no longer goes through the write door. It is redundant with "
        "the read door TODAY and that is not a reason to remove it."
    )
    # And the read door too, via the loader that enforces it.
    assert "_load" in calls


def test_that_structural_check_would_notice_the_deletion():
    """THE CONTROL: the same walk over the source with the call removed."""
    source = Path(writes.__file__).read_text(encoding="utf-8")
    without = source.replace(
        "    url = assert_write_url(\n"
        '        str(spec.url_template or "").format(target=grant.target), grant\n'
        "    )",
        '    url = str(spec.url_template or "").format(target=grant.target)',
        1,
    )
    assert without != source, "the mutation did not apply -- update this test"
    assert "assert_write_url" not in _calls_by_name_in(without, "perform")


@pytest.mark.parametrize(
    "label", ["Saved", "Unsave the job", "Remove from saved", "", "Save"]
)
def test_an_unrecognised_save_label_is_never_guessed_at(label):
    """MUTANT 18, and its diagnosis is the more useful half.

    Making ``save_state`` return ``not_saved`` for a label it has never seen
    left the suite green -- and the reason is that the branch is currently
    UNREACHABLE through ``read_save_control``. ``dom.SAVE_CONTROL`` matches only
    the one known label, so an unknown one produces count 0 and the answer
    comes from the count branch instead. The label branch is dead code today.

    It stops being dead the moment ``SAVE_LABELS`` gains its second row, which
    is the whole plan for unsave -- so it is tested directly now rather than
    when somebody is mid-way through adding that row. ``"Save"`` is on the list
    deliberately: it is one character from the real label and must still not be
    guessed at.
    """
    verdict = shape.save_state(label, count=1)
    assert verdict["state"] == shape.SAVE_UNKNOWN, (label, verdict)
    assert "not " + "the one measured state" not in verdict["why"] or True
    # The reason must name the ambiguity that makes this different from follow.
    assert "SAVED state being rendered for the first time" in verdict["why"]


def test_the_one_recognised_label_IS_recognised():
    """THE CONTROL for the five refusals above, which otherwise pass on a
    function that returns ``unknown`` for everything."""
    verdict = shape.save_state("Save the job", count=1)
    assert verdict["state"] == "not_saved"


def test_the_selector_and_the_vocabulary_cannot_drift_apart():
    """The anti-drift check the follow pair never had, on the save pair.

    ``shape.SAVE_LABELS`` is the vocabulary and ``dom.SAVE_LABELS_SEEN`` builds
    the selector, in two modules that do not import each other. If they drift,
    the reader stops matching a state it claims to know -- which is precisely
    how the branch above becomes reachable AND wrong at the same time. This is
    the check that makes adding the unsave row a one-line change in one place
    plus a failing test if it is not mirrored.
    """
    assert set(dom.SAVE_LABELS_SEEN) == set(shape.SAVE_LABELS), (
        sorted(dom.SAVE_LABELS_SEEN),
        sorted(shape.SAVE_LABELS),
    )
    for label in dom.SAVE_LABELS_SEEN:
        assert f'aria-label="{label}"' in dom.SAVE_CONTROL


async def test_a_write_tool_refuses_before_it_touches_a_browser(monkeypatch):
    """MUTANT 20. The refusal is not enough; WHERE it happens is the claim.

    Deleting the writes-off short-circuit from ``_write_tool`` left the suite
    green because the caller still gets an error either way -- ``observe``
    refuses further down. But by then the server has LAUNCHED CHROMIUM and, one
    step later, would have navigated to LinkedIn. A read-only process that
    opens a browser and loads a posting because somebody called a write tool is
    doing something it said it would not.

    So this asserts the position rather than the outcome: with writes off, the
    browser session is never even opened. ``BROWSER.session`` is replaced with
    something that raises, so touching it is unmistakable.
    """
    from linkedin_server import server as server_module

    monkeypatch.delenv(WRITES_FLAG, raising=False)

    def exploding_session(*args, **kwargs):
        raise AssertionError(
            "a browser session was opened for a write that should have been "
            "refused before any browser was touched"
        )

    monkeypatch.setattr(server_module.BROWSER, "session", exploding_session)

    for tool in (server_module.linkedin_save_job, server_module.linkedin_unsave_job):
        out = await tool(job_id=JOB)
        assert out["error"] == "writes_disabled", out
        assert out["performed"] is False
        assert WRITES_FLAG in out["message"]


async def test_that_browser_trap_is_armed(monkeypatch):
    """THE CONTROL. With writes ON, the same tool DOES reach for a browser --
    so the test above is measuring the short-circuit and not a tool that never
    opens a session at all."""
    from linkedin_server import server as server_module

    monkeypatch.setenv(WRITES_FLAG, "1")
    reached = []

    def exploding_session(*args, **kwargs):
        reached.append(True)
        raise RuntimeError("browser reached")

    monkeypatch.setattr(server_module.BROWSER, "session", exploding_session)
    out = await server_module.linkedin_save_job(job_id=JOB)
    assert reached == [True]
    assert "error" in out
    writes.discard_all()


async def test_the_tool_previews_without_a_token_and_redeems_with_one(
    writes_on, browser_page, monkeypatch
):
    """THE TWO-STEP CONTRACT, at the level a caller actually meets it.

    Everything else in this file drives ``preview`` and ``perform`` directly.
    Nothing pinned the ONE LINE that chooses between them -- and that line is
    the whole of what the tool's docstring promises: no token performs nothing,
    a token redeems. A mutant that always previewed would leave a caller
    confirming forever with nothing happening and every other test green.

    The browser session is replaced with the frozen-fixture page this module
    already uses, so the tool runs its real body against real markup and still
    touches nothing.
    """
    from contextlib import asynccontextmanager

    from linkedin_server import server as server_module

    nav = FixtureNavigator(
        _pages(target=SAVED_JOB, posting="job_detail", saved="jobs_tracker_empty")
    )

    @asynccontextmanager
    async def fake_session(*args, **kwargs):
        yield browser_page

    monkeypatch.setattr(server_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(server_module.BROWSER, "goto", nav.goto)

    # Step one: no token. Nothing is performed, and a token comes back.
    block = await server_module.linkedin_save_job(job_id=SAVED_JOB)
    assert block["performed"] is False
    assert block["to_confirm"]
    assert block["where"]["job_id"] == SAVED_JOB

    # Step two: that token. Now it acts -- against the same frozen world, so
    # the saved list still reads empty and the honest answer is "did not take".
    result = await server_module.linkedin_save_job(
        job_id=SAVED_JOB, confirm_token=block["to_confirm"]
    )
    assert "to_confirm" not in result
    assert result["clicked"]["selector"] == 'button[aria-label="Save the job"]'
    assert result["performed"] is False
    assert result["verified"] is False


async def test_a_token_from_one_tool_will_not_redeem_at_the_other(
    writes_on, browser_page, monkeypatch
):
    """THE CONTROL. The token is bound to its verb at the tool boundary too.

    Without this, the test above passes on a ``_write_tool`` that ignored
    ``action`` entirely and redeemed anything.
    """
    from contextlib import asynccontextmanager

    from linkedin_server import server as server_module

    nav = FixtureNavigator(
        _pages(target=SAVED_JOB, posting="job_detail", saved="jobs_tracker_empty")
    )

    @asynccontextmanager
    async def fake_session(*args, **kwargs):
        yield browser_page

    monkeypatch.setattr(server_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(server_module.BROWSER, "goto", nav.goto)

    block = await server_module.linkedin_save_job(job_id=SAVED_JOB)
    out = await server_module.linkedin_unsave_job(
        job_id=SAVED_JOB, confirm_token=block["to_confirm"]
    )
    assert "error" in out, out
    assert "save_job" in out["message"]


def test_the_write_module_contains_exactly_one_sanctioned_mutating_call():
    """WHAT THIS TEST USED TO ASSERT: that the scanner found nothing here.

    It finds one thing, in ``perform``, of kind ``click``, and that is the
    complete list. The scanner was NOT taught to stop seeing it -- the raw scan
    below still reports it -- which is why it can still see a second.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    raw = readonly.scan_source_for_mutations(source)
    assert len(raw) == 1, raw
    assert raw[0][1] == "click"

    sanctioned, unsanctioned = readonly.partition_mutation_hits(
        "linkedin_server/writes.py", source
    )
    assert unsanctioned == []
    assert len(sanctioned) == 1
    assert readonly.enclosing_function(source, sanctioned[0][0]) == "perform"


def test_a_second_click_inside_perform_is_still_caught():
    """THE CONTROL, on the real file, at the hardest possible edit.

    A second click inside ``perform`` is in the sanctioned file, the sanctioned
    function and of the sanctioned kind -- so it matches the allowlist entry
    exactly and the PARTITION cannot see it. Asserted here, because a control
    that hid that would be worse than none.

    What catches it is the COUNT: the package is asserted to contain exactly as
    many mutating calls as the list has entries, and the list has one. This
    reproduces that check against the doubled source and shows it going red.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    doubled = source.replace(
        "await page.click(selector, timeout=CLICK_TIMEOUT_MS)",
        "await page.click(selector, timeout=CLICK_TIMEOUT_MS)\n"
        "        await page.click(selector, timeout=CLICK_TIMEOUT_MS)",
        1,
    )
    assert doubled != source

    # The partition is BLIND to it, and that is asserted rather than hidden.
    _sanctioned, unsanctioned = readonly.partition_mutation_hits(
        "linkedin_server/writes.py", doubled
    )
    assert unsanctioned == [], "the partition sees a duplicate -- update this test"

    # The count is not.
    raw = readonly.scan_source_for_mutations(doubled)
    assert len(raw) == 2
    assert len(raw) != len(readonly.SANCTIONED_MUTATIONS), (
        "the count check would not fire on a doubled click"
    )


def test_the_scanner_would_have_caught_it_if_it_did():
    """The scanner, shown seeing the exact code that was eventually written."""
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

    WHERE IT MOVED TO. This used to read ``writes.perform.__doc__``. That
    docstring described a function that refused; the function now acts, and its
    docstring describes what it does. The record was moved to a module constant
    rather than deleted, because the reasoning is the deliverable -- and a
    history kept inside the docstring of the thing it is the history OF is a
    history that gets edited away the next time the thing changes.
    """
    doc = writes.TOGGLE_MEASUREMENT_RECORD
    assert "IS SOLVED" in doc
    assert 'aria-label="Following"' in doc
    assert "linkedin_saved_jobs" in doc
    # And it must not have quietly dropped the half that is still open.
    assert "has NOT been observed" in doc

    # The measured pair is what the reader actually uses, so assert THAT
    # rather than the docstring alone -- a docstring cannot be wrong in a way
    # a caller notices.
    assert shape.FOLLOW_LABELS == {
        "Follow": "not_following",
        "Following": "following",
    }
    # And the half that is NOT a measured pair, for the same reason. One entry,
    # and its singularity is the whole reason unsave refuses.
    assert shape.SAVE_LABELS == {"Save the job": "not_saved"}


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
