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

SPLIT BY CONCERN ON 2026-11-27 (lane ci8). This file alone took about 137 s,
over the two-minute cap on a local gate. Its sections now live in six files,
each moved verbatim with its banner and prose, and each well under the cap:

    tests/test_writes.py               the fixtures and helpers below, and
                                       sections 1-3: off by default, the grant,
                                       the narrowed url door
    tests/test_writes_conservation.py  4 the conservation law, 7 the
                                       confinement check, 8 the permanent
                                       refusals, the 2026-09-02 url ruling
    tests/test_writes_gate.py          5 the gate a human reads
    tests/test_writes_perform.py       6 what CAN act, 6b three guards
    tests/test_writes_state.py         9 the toggle direction, 10 Open To Work,
                                       11 the read the gate performs itself
    tests/test_writes_list.py          9 the click on the LIST surface, 9b two
                                       defensive branches

The fixtures, the navigator, the frozen captures and every helper another
file imports stay HERE, because 69 test files import them from
``tests.test_writes``. The collected ids are the same 163, modulo the file.
The three checks named above are in tests/test_writes_gate.py and
tests/test_writes_state.py now.
"""

from __future__ import annotations

import ast
import inspect
import re
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

#: A company the frozen Manage-Pages capture shows him following, and the id
#: its row is keyed on. Both halves matter: the id is what the click is
#: anchored to and the name is what the gate prints for him to check, so a
#: test that used one without the other would not notice them drifting apart.
FOLLOWED_COMPANY = "902611"
FOLLOWED_COMPANY_NAME = "Gridwell"
#: A well-formed company id that is on no row of that capture.
UNFOLLOWED_COMPANY = "7777777"


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

#: DERIVED, and for the same reason the tracker markup above is: no capture in
#: this repo shows a SAVED posting, because every one predates the operator's
#: first save on 2026-08-30. The label itself is NOT derived -- it was measured
#: four times that evening, across two independent routes -- but a page wearing
#: it has to be built here.
#:
#: THE ASSERTION IS NOT DECORATION. A ``replace`` whose anchor has drifted is a
#: silent no-op, and a toggle-hazard test running against an UNSAVED posting
#: would pass while proving nothing at all.
_SAVE_ATTR = 'aria-label="Save the job"'
SAVED_POSTING = markup("job_detail").replace(
    _SAVE_ATTR, 'aria-label="Unsave the job"', 1
)
assert SAVED_POSTING != markup("job_detail"), (
    "the saved-posting derivation anchored on "
    f"{_SAVE_ATTR!r} and changed nothing, so every toggle-direction test below "
    "would run against an UNSAVED page. Repoint the anchor; do NOT delete this."
)

#: DERIVED: the control renamed off the measured vocabulary entirely. This is
#: what an unrecognised state looks like now that BOTH real states are known,
#: and it is the page that separates "unsave refuses always" -- which it did
#: until 2026-08-30 -- from "unsave refuses on a state it cannot read".
RENAMED_POSTING = markup("job_detail").replace(
    _SAVE_ATTR, 'aria-label="Bookmark this job"', 1
)
assert RENAMED_POSTING != markup("job_detail")


class FixtureNavigator:
    """Serves frozen captures where LinkedIn would be, and RECORDS the asks.

    The recording is the point. A gate that reads for itself has to be shown
    actually opening pages, and shown opening the RIGHT ones -- the assertion
    that a follow costs one load and a save costs two is only meaningful
    against something that counted.

    A URL MAY ALSO MAP TO A LIST, served one entry per visit in order (the
    last entry repeats once the list runs out). Every other action already
    verified from a DIFFERENT surface than the one it clicked, so one string
    per url was enough -- ``save_job``'s "before" and "after" are two
    different frozen worlds because they are two different urls.
    ``react_to_item`` is not that shape: its own verification re-navigates to
    the SAME item permalink its click's gate already read, because there is
    only one surface that carries this item's reaction state. A single
    static page cannot wear the OFF label a click needs to be valid FROM and
    the ON label its verification needs to see AFTER, so this is the second
    frozen world the same url needs, in visit order, rather than one page
    pretending to have moved.
    """

    #: THE ONE NAVIGATION A PRESS STARTS ON THESE CAPTURES, answered HERE.
    #: The job posting captures draw the apply control as an ANCHOR whose href
    #: is LinkedIn's (``/jobs/view/<id>/apply/?openSDUIApplyFlow=true&``); on
    #: LinkedIn its own script opens the apply flow in place, and on a frozen
    #: capture, with no script, pressing it starts a navigation. Until
    #: 2026-09-27 nothing answered it, and eleven tests sent a fresh Chromium
    #: to LinkedIn on every run; ``tests/network_guard.py`` now fails any test
    #: that lets a request leave. So the navigator that served the posting
    #: answers its apply anchor too, with a navigation that lands nowhere --
    #: the page stays on the capture, as it does on LinkedIn -- and every
    #: answer is recorded in ``answered``.
    #:
    #: THE ANSWER IS ``abort("aborted")`` SINCE 2026-11-24, AND WAS ``204 No
    #: Content`` BEFORE. Both land nowhere on playwright 1.63.0 and 1.65.2. On
    #: 1.64.1 -- which CI resolved on 2026-10-26, because requirements.txt
    #: leaves playwright unpinned -- a press whose navigation is answered 204
    #: does not resolve within its 10 s bound, and the stuck navigation holds
    #: the page's next waits to their full bounds: four tests red on every
    #: platform, master f339459.
    #: ``abort("failed")`` was measured too and is no answer: it replaces the
    #: page with Chromium's error page. ``tests/test_the_apply_answer_lands_
    #: nowhere.py`` holds the property; the fixes lane's record,
    #: ``_audit/2026-10-26-fixes.md`` section 3, holds the measurements.
    APPLY_NAVIGATION = re.compile(r"^https://www\.linkedin\.com/jobs/view/\d+/apply/")

    def __init__(self, pages: dict[str, "str | list[str]"]):
        self.pages = dict(pages)
        self.gotos: list[str] = []
        self.answered: list[str] = []
        self._visits: dict[str, int] = {}
        self._routed: set[int] = set()
        self.named: list[bool] = []

    async def goto(self, page, url: str, *, named_profile: bool = False) -> str:
        # ``named_profile`` (2026-11-24, lane builds-26): the refusing
        # endorsement previews load a named profile through the second door,
        # which asks the navigator for it by keyword; recorded, never routed.
        self.named.append(named_profile)
        self.gotos.append(url)
        entry = self.pages.get(url)
        if entry is None:
            raise AssertionError(
                f"the gate asked for {url!r}, which this test did not freeze. "
                f"It froze {sorted(self.pages)}."
            )
        if isinstance(entry, (list, tuple)):
            visit = self._visits.get(url, 0)
            self._visits[url] = visit + 1
            html = entry[min(visit, len(entry) - 1)]
        else:
            html = entry
        if id(page) not in self._routed and hasattr(page, "route"):
            # A page's route outranks the network guard's context route, and
            # the latest navigator's outranks an earlier one on the same page,
            # so the navigator driving the press is the one that records it.
            # A page double has no route and cannot reach a network.
            await page.route(self.APPLY_NAVIGATION, self._answer_locally)
            self._routed.add(id(page))
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return url

    async def _answer_locally(self, route) -> None:
        self.answered.append(route.request.url)
        await route.abort("aborted")


def _pages(
    *, target, posting=None, saved=None, applied=None, profile=None, followed=None
) -> dict[str, str]:
    out: dict[str, str] = {}
    if posting is not None:
        # RAW MARKUP IS ACCEPTED HERE, exactly as it already is for ``saved``
        # and ``followed``, and for the same reason: no fixture in this repo
        # shows a SAVED posting. Every capture predates the operator's first
        # save on 2026-08-30, so the ON state has to be DERIVED.
        out[f"https://www.linkedin.com/jobs/view/{target}/"] = (
            posting if posting.lstrip().startswith("<") else markup(posting)
        )
    if saved is not None:
        out[writes.SAVED_LIST_URL] = (
            saved if saved.lstrip().startswith("<") else markup(saved)
        )
    if applied is not None:
        # THE APPLIED TAB, added 2026-08-31 with apply's verification fix.
        # Raw markup accepted for the same reason ``saved`` accepts it: no
        # capture in this repo shows an APPLIED posting, because the Applied
        # tab has read zero on every reading anybody has taken.
        out[writes.APPLIED_LIST_URL] = (
            applied if applied.lstrip().startswith("<") else markup(applied)
        )
    if profile is not None:
        out[writes.PROFILE_URL] = markup(profile)
    if followed is not None:
        out[writes.FOLLOWED_PAGES_URL] = (
            followed if followed.lstrip().startswith("<") else markup(followed)
        )
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
    followed: str = "manage_pages_following_hydrated",
    to_state=None,
):
    """Run the real gate over frozen captures. Returns ``(block, navigator)``."""
    spec = spec_for_action(action)
    nav = FixtureNavigator(
        _pages(
            target=target,
            posting=posting,
            saved=saved,
            profile=profile,
            followed=followed,
        )
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
    followed: str = "manage_pages_following_hydrated",
):
    """One live reading, receipt still live. The only way to reach ``mint``."""
    spec = spec_for_action(action)
    nav = FixtureNavigator(
        _pages(
            target=target,
            posting=posting,
            saved=saved,
            profile=profile,
            followed=followed,
        )
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
# Shared with the other write files, and with the files that import them
# ---------------------------------------------------------------------------
#
# MOVED HERE 2026-11-27 (lane ci8), when this file was split by concern into
# itself and five more: test_writes_conservation.py, test_writes_gate.py,
# test_writes_perform.py, test_writes_state.py and test_writes_list.py. Each
# name below is imported from ``tests.test_writes`` by another test file, or
# used by two of the six, so it lives where those imports already point. Each
# moved with its own comment and nothing else; the sections they came from
# kept their banners and their prose.

#: THE SECOND CARVE-OUT, added 2026-08-30, and it is a different KIND from the
#: first. The ``un`` rule is derived -- it admits the inverse of something
#: already sanctioned, and nothing else. This one is not derivable from
#: anything: it is an ENUMERATED pair of verbs admitted by an operator ruling,
#: and each has to argue for itself here or it does not belong.
#:
#: WHY IT COULD NOT BE AVOIDED. ``linkedin_comment_on_item`` and
#: ``linkedin_react_to_item`` were registered on 2026-08-30, and neither
#: ``comment`` nor ``react`` is on the frozen baseline in
#: ``_ORIGINAL_FORBIDDEN``. Two of the four names in that wave were fixed by
#: RENAMING instead -- ``linkedin_change_setting`` became
#: ``linkedin_update_setting`` and ``linkedin_edit_profile_field`` became
#: ``linkedin_update_profile_field``, both onto ``update``, which the baseline
#: already knew and which announces the write that "change" concealed. That is
#: the preferred fix and it was taken wherever it did not distort the name.
#: For these two it would have: a comment is not an update and a reaction is
#: not a post, and a name that misdescribes what a tool does to satisfy a
#: verb list is worse than a list that grew visibly.
#:
#: WHAT THIS DOES NOT ADMIT, which is the whole reason it is a frozen set of
#: two rather than a rule. It does not admit ``un`` + either verb -- the
#: existing carve-out is checked against ``original_verbs`` alone, so
#: ``uncomment`` and ``unreact`` still fail. It does not admit a third verb.
#: And it does not admit a name mixing one of these with a verb that is
#: inadmissible on its own, because the test is a SUBSET test.
_VERBS_ADMITTED_BY_RULING = frozenset({"comment", "react"})
async def _granted(
    page,
    action: str,
    *,
    target: str,
    posting: str = "job_detail",
    saved: str = "jobs_tracker_empty",
    followed: str = "manage_pages_following_hydrated",
) -> writes.WriteGrant:
    """A real, redeemed grant, produced the way the tool produces one.

    Deliberately the long way round -- preview, then consume the token it
    printed -- rather than constructing a grant. ``perform`` requires a grant
    that has already been burned, so a test that fabricated one would be
    testing a path no caller can take.
    """
    block, _nav = await _gate(
        page, action, target=target, posting=posting, saved=saved, followed=followed
    )
    return consume(block["to_confirm"], action=action, target=target)
async def _perform(
    page,
    grant: writes.WriteGrant,
    *,
    posting: str = "job_detail",
    saved=None,
    applied=None,
):
    """Run the real ``perform`` over frozen captures. Returns ``(block, nav)``.

    The saved list served here is usually DIFFERENT from the one the preview
    saw, and that is the point: it models the world having changed because the
    click changed it. The navigator is per-call, so "before" and "after" are
    two separate frozen worlds rather than one mutable fake.
    """
    nav = FixtureNavigator(
        _pages(target=grant.target, posting=posting, saved=saved, applied=applied)
    )
    return await writes.perform(nav, page, grant), nav
#: The tracker capture with LinkedIn's own Saved count edited 0 -> 1 AND the
#: row's job id rewritten to the posting these tests act on. DERIVED, twice
#: over, and labelled as such everywhere it is used: a self-consistent saved
#: list containing a chosen posting cannot be photographed on an account with
#: nothing saved. It exercises THE READER'S LOGIC and measures nothing about
#: LinkedIn.
SAVED_LIST_CONTAINING = SAVED_LIST_OF_ONE
#: A LinkedIn-shaped activity urn matching ``WriteSpec.url_pattern`` for
#: react_to_item (``urn:li:[A-Za-z]+:[0-9]+``). NOT a real one -- this server
#: has never parsed one unshaped, the same reason ``ITEM`` in
#: tests/test_writes_nine.py is a placeholder string -- but this test needs a
#: target that actually PASSES the write door, which an opaque placeholder
#: would not.
#:
#: SUBSTITUTED 2026-09-04, and the reason is not that the old value was real.
#: It was nineteen digits drawn from THREE distinct characters -- invented, on
#: any reading of the entropy. It was also UNDECLARED, so
#: tests/test_no_committed_identity.py flagged it as an unallowed urn id and
#: went red, and it stayed red across eight commits because nothing between a
#: commit and the disk runs that guard.
#:
#: The replacement is the next member of the family already declared in that
#: guard's ``SYNTHETIC_IDS``. **A synthetic value that has to be argued for
#: costs more than one that argues for itself** -- the same finding the
#: connections fixture's member tokens were rewritten for the same day. Do not
#: replace this with a fresh hand-typed number; take the next one in the
#: series and declare it there.
REACTED_ITEM = "urn:li:activity:7400000000000000004"
#: THE SMALLEST MARKUP THAT SETTLES THE REACTION READER, following
#: ``FEED_MARKUP`` in tests/test_writes_nine.py: one control wearing the OFF
#: label this server has actually measured, and nothing else the read
#: branches on.
_REACTION_OFF_PAGE = (
    "<html><body>"
    '<button aria-label="' + dom.REACTION_OFF_LABEL + '"></button>'
    "</body></html>"
)
#: DERIVED from the page above by substituting the ON label for the OFF one.
#: THE LABEL ITSELF IS NOT DERIVED -- it was measured 2026-09-04, on the
#: operator's own profile rail, across 8 reaction controls (off_state 7, this
#: string on the eighth) -- what is derived here is a page that wears it,
#: because no capture in this repo shows a REACTED item: every one predates
#: the operator's first reaction.
_REACTION_ON_LABEL = "Reaction button state: Like"
_REACTION_ON_PAGE = _REACTION_OFF_PAGE.replace(
    dom.REACTION_OFF_LABEL, _REACTION_ON_LABEL, 1
)
assert _REACTION_ON_PAGE != _REACTION_OFF_PAGE, (
    "the reacted-item derivation anchored on "
    f"{dom.REACTION_OFF_LABEL!r} and changed nothing, so the verify branch "
    "below would read the OFF label twice and this test could never turn "
    "red. Repoint the anchor; do NOT delete this."
)
def _manage_pages(*, without=None, total: int = 58) -> str:
    """The Manage-Pages capture, with one row optionally cut and a new total.

    MODELS THE WORLD AFTER A CLICK, and the two knobs are independent ON
    PURPOSE. LinkedIn's rendered rows and LinkedIn's own stated total are two
    separate readings and the whole verification rests on them agreeing -- so a
    helper that could only move them together could not tell a real unfollow
    from a row that scrolled out of a partial list.

    ``without`` names the company whose entire ``<li>`` is removed, located
    from its button and bounded by COUNTING tags rather than by a regex over
    ``<li>.*?</li>``: these rows nest lists, and a lazy match would cut the
    wrong element and quietly hand every test below a shorter page than it
    asked for.
    """
    html = markup("manage_pages_following_hydrated")
    if without is not None:
        needle = 'aria-label="Click to stop following ' + without + '"'
        at = html.index(needle)
        start = html.rindex("<li", 0, at)
        depth, cursor = 0, start
        while True:
            nxt_open = html.find("<li", cursor + 1)
            nxt_close = html.find("</li>", cursor + 1)
            if nxt_close == -1:
                raise AssertionError("unterminated <li> in the fixture")
            if nxt_open != -1 and nxt_open < nxt_close:
                depth += 1
                cursor = nxt_open
                continue
            if depth == 0:
                html = html[:start] + html[nxt_close + len("</li>") :]
                break
            depth -= 1
            cursor = nxt_close
        assert needle not in html, without
    if total != 58:
        assert "58 Pages" in html
        html = html.replace("58 Pages", str(total) + " Pages", 1)
    return html



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
    whole failure this design exists to avoid.

    AMENDED 2026-08-26, and the distinction matters more than the edit. The
    messaging THREAD url left this list because the operator ruled that
    reading his own inbox is his to do -- a deliberate boundary change, made
    in its own commit, with the frozen digests re-verified under both
    interpreters. It did NOT leave because writes.py widened anything, which
    is what this test polices and what it still polices.

    ``/messaging/compose`` takes its place, and is the better probe for this
    test's actual question: it is the SENDING surface, so a write module that
    reached it would be exactly the failure named above.
    """
    for url in (
        "https://www.linkedin.com/jobs/application/123/",
        "https://www.linkedin.com/messaging/compose/?body=hi",
        "https://www.linkedin.com/in/someone/edit/",
    ):
        assert readonly.is_read_url(url) is False
    assert readonly.is_read_url("https://www.linkedin.com/feed/") is True
