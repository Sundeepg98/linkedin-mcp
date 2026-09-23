"""Tests for linkedin_server.share_link -- the "Copy link to post" module.

OFFLINE, END TO END. Every browser-driven test here launches a LOCAL
headless Chromium and intercepts every single request with
``page.route("**/*", ...)``. All but one are aborted outright. The one
exception is the fixture's own navigation: it is FULFILLED from a string
already on this machine, never fetched, so Chromium never opens a socket
for it -- but ``page.url`` afterwards reads as a real
``https://www.linkedin.com/...`` address, which is what lets
``share_link.copy_own_post_link``'s own pre-press checks (``press``'s
``check_address``, ``check_shape``, ``check_scope`` and ``check_basis``,
called explicitly) run their real, unmodified logic rather than a stand-in.
Measured before this file was written (both directions, see the wave
report): a fully-aborted ``goto`` to that same address raises and leaves
``page.url`` at ``about:blank``; a locally-fulfilled one lands exactly on
the address requested. No test in this file ever contacts a real network
address, live or otherwise, and none loads a page from ``linkedin.com``.
"""
from __future__ import annotations

import ast
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

import pytest

from linkedin_server import share_link

REPO = Path(__file__).resolve().parent.parent
FIXTURE_PATH = REPO / "tests" / "fixtures" / "synthetic" / "own_post_menu.html"

#: The one address every "happy" test in this file navigates to -- a real
#: shape on the read allowlist (``readonly._ALLOWED_URL_PATTERNS``'s
#: ``/feed/update/urn:li:<type>:<digits>/`` entry), never actually fetched.
FIXTURE_URL = "https://www.linkedin.com/feed/update/urn:li:activity:1234/"

#: An address of the SAME shape but not on the allowlist, for the one test
#: that exercises the pre-press gate's own refusal.
NOT_ADMITTED_URL = "https://www.linkedin.com/some/unadmitted/path/"

#: The synthetic post id the fixture builds its "copied" link from. Four
#: digits, on purpose -- see the fixture's own top-of-file comment.
ACTIVITY_DIGITS = "1234"


# ---------------------------------------------------------------------------
# Fixture loading: string-splice the config in, then fulfil one navigation
# locally and abort everything else.
# ---------------------------------------------------------------------------


def _fixture_html(config: Optional[dict] = None) -> str:
    """The fixture text, with ``window.__fixtureConfig`` spliced in.

    NOT ``page.add_init_script`` -- measured before this file was written
    that an init script does not reliably run ahead of an inline
    ``<script>`` inside content handed to ``page.set_content``/navigated via
    a fulfilled route, so the config has to arrive as markup, ahead of the
    fixture's own behaviour script in DOCUMENT ORDER.
    """
    base = FIXTURE_PATH.read_text(encoding="ascii")
    assert "<!--FIXTURE_CONFIG-->" in base, "fixture marker comment is missing"
    if not config:
        return base
    snippet = "<script>window.__fixtureConfig = %s;</script>" % json.dumps(config)
    return base.replace("<!--FIXTURE_CONFIG-->", snippet)


@asynccontextmanager
async def _open_fixture(config: Optional[dict] = None, *, url: str = FIXTURE_URL):
    """A local headless Chromium tab, on ``url``, loaded from memory only.

    Every request is intercepted. The ONE exception is ``url`` itself,
    fulfilled from a string already on this machine -- Playwright never
    opens a socket for a fulfilled route. Anything else this page might ask
    for (a stray fetch, an image) is aborted outright.
    """
    playwright = pytest.importorskip("playwright.async_api")
    html = _fixture_html(config)

    async def handler(route):
        if route.request.url == url:
            await route.fulfill(status=200, content_type="text/html", body=html)
        else:
            await route.abort()

    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.route("**/*", handler)
            await page.goto(url, timeout=10_000)
            yield page
        finally:
            await browser.close()


# ---------------------------------------------------------------------------
# read_counters stand-ins
# ---------------------------------------------------------------------------


def _steady_counters(mapping: Optional[dict]):
    """Returns the SAME mapping every call (or None, every call).

    A steady ``{"off_state": N}`` is what the ``/feed/`` surface's declared
    sensitivity basis needs to see UNMOVED for a press to be permitted --
    see ``press.SENSITIVITY_BASES``.
    """

    async def _read():
        return dict(mapping) if mapping is not None else None

    return _read


def _moving_counters():
    """A different reading each call -- the counter-moved case."""
    calls = {"n": 0}

    async def _read():
        calls["n"] += 1
        return {"off_state": calls["n"]}

    return _read


class _NeverTouchedPage:
    """Raises on ANY attribute access. Proves zero page contact.

    Not "tolerates the calls the fixture happens to expect" -- literally no
    attribute of this object may be read before activity_digits is
    validated.
    """

    def __getattr__(self, name: str) -> Any:
        raise AssertionError(
            f"copy_own_post_link touched page.{name} before validating "
            "activity_digits"
        )


async def _os_clipboard_writes(page) -> int:
    return int(await page.evaluate("() => window.__osClipboardWrites || 0"))


async def _escape_keydowns(page) -> int:
    return int(await page.evaluate("() => window.__escapeKeydowns || 0"))


async def _clipboard_box(page):
    """None if CLIPBOARD_JS was never installed on this page, else its texts."""
    return await page.evaluate(
        "() => window.__lqClip ? window.__lqClip.texts.slice() : null"
    )


def _shorten_the_read_wait(monkeypatch, wait_ms: int = 300) -> None:
    """For a test whose copy NEVER arrives, so the read's bound is the wait.

    The bound lives in the script as a literal (see
    :func:`test_the_read_wait_in_the_script_is_the_pinned_constant`), so the
    script is patched, not the constant -- still a real, bounded wait.
    """
    literal = str(share_link.READ_WAIT_MS)
    assert share_link.CLIPBOARD_JS.count(literal) == 1
    monkeypatch.setattr(
        share_link, "CLIPBOARD_JS",
        share_link.CLIPBOARD_JS.replace(literal, str(wait_ms)),
    )


async def _trigger_expanded(page, trigger_id: str = "trigger-1") -> Optional[str]:
    return await page.locator("#" + trigger_id).get_attribute("aria-expanded")


# ---------------------------------------------------------------------------
# copy_own_post_link -- happy path
# ---------------------------------------------------------------------------


async def test_happy_path_copies_the_link_without_touching_the_os_clipboard():
    async with _open_fixture() as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict["permitted"] is True, verdict
        assert verdict["copied"] is True, verdict
        assert verdict["shape"] is not None, verdict
        assert verdict["shape"]["carries_activity_id"] is True, verdict
        assert verdict["owner_item_present"] is True, verdict
        assert verdict["link"], verdict
        assert verdict["captures"] == 1, verdict
        assert await _os_clipboard_writes(page) == 0, (
            "the OS clipboard must never be written to"
        )
        # The menu is left as it was found -- by the one Escape, which this
        # fixture's menu needs (its items do not close it). The count is the
        # positive control for the itemClickCloses test's zero.
        assert await _trigger_expanded(page) == "false"
        assert await _escape_keydowns(page) == 1


async def test_a_menu_that_closes_itself_on_the_copy_press_is_sent_no_escape():
    """A real menu's item usually closes its menu. Then the closure holds
    with NO key pressed: Escape is for a menu still open, never a ritual."""
    async with _open_fixture({"itemClickCloses": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict["permitted"] is True, verdict
        assert verdict["copied"] is True, verdict
        assert verdict["closure"].get("closed") is True, verdict
        assert await _escape_keydowns(page) == 0


async def test_a_copy_made_after_the_click_returns_is_still_captured():
    """The page copies 400ms after its click handler returned -- as a page
    that awaits something of its own first does. A read taken at once would
    report a copy that happened as one that did not."""
    async with _open_fixture({"asyncCopier": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict["copied"] is True, verdict
        assert verdict["captures"] == 1, verdict
        assert verdict["shape"]["carries_activity_id"] is True, verdict
        assert await _os_clipboard_writes(page) == 0


async def test_a_clipboard_item_copier_is_captured_by_its_text_part():
    async with _open_fixture({"clipboardItemCopier": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict["copied"] is True, verdict
        assert verdict["shape"]["path_kind"] == "posts", verdict
        assert verdict["shape"]["carries_activity_id"] is True, verdict
        assert await _os_clipboard_writes(page) == 0


async def test_a_write_with_no_text_part_is_a_capture_and_never_a_link():
    """An item carrying no text/plain is kept as an EMPTY text: counted, so
    the write is visible, and never promoted to ``copied`` or a link."""
    async with _open_fixture(
        {"clipboardItemCopier": True, "htmlOnlyItem": True}
    ) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict["captures"] == 1, verdict
        assert verdict["copied"] is False, verdict
        assert verdict["link"] is None, verdict
        assert verdict["shape"] is None, verdict
        assert await _os_clipboard_writes(page) == 0


async def test_a_copier_holding_a_reference_taken_before_the_capture_reads_as_not_copied(
    monkeypatch,
):
    """THE NAMED GAP, PINNED AS AN ANSWER RATHER THAN HIDDEN.

    The page copies through a reference to writeText it took at LOAD, before
    the hook existed -- the one route share_link's capture cannot see (the
    async clipboard API fires no copy event). The module must say so the only
    way it can: ``copied`` False, no link, no shape. The fixture's own count
    records the write the module could not see; the module never claims one
    either way.
    """
    _shorten_the_read_wait(monkeypatch)
    async with _open_fixture({"capturedReference": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict["copied"] is False, verdict
        assert verdict["captures"] == 0, verdict
        assert verdict["link"] is None, verdict
        assert verdict["shape"] is None, verdict
        assert await _os_clipboard_writes(page) == 1


def test_the_read_wait_in_the_script_is_the_pinned_constant():
    """The script's one timer bound is READ_WAIT_MS, spelled as a literal
    because a script must be a module constant to be certified at all."""
    assert re.findall(r"\}, ([0-9]+)\);", share_link.CLIPBOARD_JS) == [
        str(share_link.READ_WAIT_MS)
    ]


async def test_a_startswith_lookalike_item_does_not_count_as_the_copy_item():
    """POSITIVE CONTROL for the exact-match requirement on COPY_PHRASE.

    The fixture also renders "Copy link to post to a group" -- normalised
    text that STARTS WITH the copy phrase and is not equal to it. A correct
    implementation still succeeds, aiming at the one EXACT match.
    """
    async with _open_fixture({"startsWithDecoy": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict["permitted"] is True, verdict
        assert verdict["copied"] is True, verdict


# ---------------------------------------------------------------------------
# not_his_post
# ---------------------------------------------------------------------------


async def test_non_owner_menu_refuses_not_his_post_without_clicking_copy():
    async with _open_fixture({"nonOwner": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict.get("refused") == "not_his_post", verdict
        # THE COPY ITEM WAS NEVER CLICKED: the clipboard hook, installed
        # only immediately before that click, was never installed either.
        assert await _clipboard_box(page) is None
        assert await _os_clipboard_writes(page) == 0
        assert await _trigger_expanded(page) == "false", "menu must close"
        # And the refusal SAYS it closed: the menu was opened before it.
        assert verdict["closure"].get("closed") is True, verdict


async def test_a_refusal_after_the_menu_opened_says_when_it_did_not_close():
    """The refusal's closure is a reading, not a formality: a menu that
    ignores Escape is reported as not restored even though the answer is a
    refusal."""
    async with _open_fixture({"nonOwner": True, "ignoreEscape": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict.get("refused") == "not_his_post", verdict
        assert verdict["closure"].get("refused") == "not_restored", verdict


# ---------------------------------------------------------------------------
# control_menu_not_unique
# ---------------------------------------------------------------------------


async def test_two_triggers_refuses_control_menu_not_unique_with_zero_clicks():
    async with _open_fixture({"twoTriggers": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict.get("refused") == "control_menu_not_unique", verdict
        assert verdict["trigger_matches"] == 2, verdict
        # ZERO CLICKS: neither trigger ever opened.
        assert await _trigger_expanded(page, "trigger-1") == "false"
        assert await _trigger_expanded(page, "trigger-2") == "false"
        assert await _clipboard_box(page) is None


# ---------------------------------------------------------------------------
# copy_item_absent
# ---------------------------------------------------------------------------


async def test_copy_item_missing_refuses_copy_item_absent_and_closes_the_menu(
    monkeypatch,
):
    # Shrunk from the real 5000ms bound: this scenario times out by design,
    # and a real 5s wait per run is a cost the suite should not pay for a
    # deliberately-absent item. Still bounded, still a real wait -- see the
    # module docstring: "using a Playwright locator wait, no sleep loop".
    monkeypatch.setattr(share_link, "OPEN_WAIT_MS", 700)
    async with _open_fixture({"missingCopyItem": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict.get("refused") == "copy_item_absent", verdict
        assert await _trigger_expanded(page) == "false", (
            "the menu must be closed after this refusal"
        )
        assert await _clipboard_box(page) is None


# ---------------------------------------------------------------------------
# copy_item_not_unique (bonus coverage -- not in the required list, cheap)
# ---------------------------------------------------------------------------


async def test_duplicate_copy_items_refuse_copy_item_not_unique():
    async with _open_fixture({"duplicateCopyItem": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict.get("refused") == "copy_item_not_unique", verdict
        assert await _trigger_expanded(page) == "false"
        assert await _clipboard_box(page) is None


# ---------------------------------------------------------------------------
# The execCommand copier
# ---------------------------------------------------------------------------


async def test_execcommand_copier_is_captured_and_permitted():
    async with _open_fixture({"execCommandCopier": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict["copied"] is True, verdict
        assert verdict["permitted"] is True, verdict
        # WHAT was kept is the link, not merely something: the selection the
        # copy command saw carries the post's id in the shareable form.
        assert verdict["shape"]["path_kind"] == "posts", verdict
        assert verdict["shape"]["carries_activity_id"] is True, verdict
        assert await _os_clipboard_writes(page) == 0


# ---------------------------------------------------------------------------
# Escape ignored -> closure refused
# ---------------------------------------------------------------------------


async def test_menu_that_ignores_escape_gives_closure_refused_not_restored():
    async with _open_fixture({"ignoreEscape": True}) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        # The copy itself still succeeded -- this is a CLOSURE failure, not
        # a copy failure, and the two must stay distinguishable.
        assert verdict.get("copied") is True, verdict
        assert verdict.get("permitted") is False, verdict
        assert verdict["closure"].get("refused") == "not_restored", verdict


# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------


async def test_counters_that_move_give_the_counter_check_refused():
    async with _open_fixture() as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_moving_counters(),
        )
        assert verdict.get("permitted") is False, verdict
        assert verdict["counters"].get("refused") == "counter_moved", verdict


async def test_unreadable_counters_refuse_before_any_click():
    async with _open_fixture() as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters(None),
        )
        assert verdict.get("refused") == "counters_unreadable", verdict
        assert await _trigger_expanded(page) == "false", (
            "no click may occur before counters are read"
        )


async def test_an_empty_counters_mapping_also_refuses_before_any_click():
    async with _open_fixture() as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({}),
        )
        assert verdict.get("refused") == "counters_unreadable", verdict
        assert await _trigger_expanded(page) == "false"


# ---------------------------------------------------------------------------
# The pre-press gate itself
# ---------------------------------------------------------------------------


async def test_page_not_on_the_read_allowlist_refuses_gate_refused():
    async with _open_fixture(url=NOT_ADMITTED_URL) as page:
        verdict = await share_link.copy_own_post_link(
            page,
            activity_digits=ACTIVITY_DIGITS,
            read_counters=_steady_counters({"off_state": 3}),
        )
        assert verdict.get("refused") == "gate_refused", verdict
        assert verdict["gate"].get("refused") == "address_not_admitted", verdict["gate"]
        # THE GATE REFUSES BEFORE ANY PAGE CONTACT BEYOND THE TRIGGER SCAN --
        # nothing was ever clicked.
        assert await _trigger_expanded(page) == "false"


# ---------------------------------------------------------------------------
# bad_activity_id -- zero page contact
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "12a45",
        "1" * 21,  # built at runtime: 21 ASCII digits, one over the cap
        None,
        1234,
        "-5",
        "12 34",
        # Arabic-Indic digit U+0664, x3: non-ASCII, must refuse. Built from
        # its code point rather than written as a literal character, so no
        # amount of quoting, copying or transport can turn it into
        # something else -- the same discipline
        # tests/test_no_committed_identity.py's own BACKSLASH constant uses.
        chr(0x0664) * 3,
    ],
    ids=[
        "empty", "letters", "twenty_one_digits", "none", "int",
        "leading_sign", "embedded_space", "unicode_digits",
    ],
)
async def test_bad_activity_id_refuses_before_any_page_contact(bad):
    verdict = await share_link.copy_own_post_link(
        _NeverTouchedPage(),
        activity_digits=bad,
        read_counters=_steady_counters({"off_state": 1}),
    )
    assert verdict.get("refused") == "bad_activity_id", verdict
    assert set(verdict) == {"refused", "why"}, verdict


async def test_bad_activity_id_message_is_a_fixed_string_never_the_value():
    outcomes = set()
    for bad in ("a-clearly-unique-marker-token", "9" * 25, "another-marker"):
        verdict = await share_link.copy_own_post_link(
            _NeverTouchedPage(),
            activity_digits=bad,
            read_counters=_steady_counters({"off_state": 1}),
        )
        assert str(bad) not in verdict["why"], verdict
        outcomes.add(verdict["why"])
    assert len(outcomes) == 1, (
        "the refusal sentence must be a fixed string, not built from the "
        f"input: {outcomes}"
    )


# ---------------------------------------------------------------------------
# validated_activity_digits -- pure, no page
# ---------------------------------------------------------------------------


def test_validated_activity_digits_accepts_one_digit():
    assert share_link.validated_activity_digits("7") == "7"


def test_validated_activity_digits_accepts_twenty_digits():
    value = "1" * 20
    assert share_link.validated_activity_digits(value) == value


def test_validated_activity_digits_refuses_twenty_one_digits():
    with pytest.raises(ValueError):
        share_link.validated_activity_digits("1" * 21)


@pytest.mark.parametrize(
    "bad",
    ["", "12a45", "-5", "12 34", None, 1234, 12.5, [], chr(0x0664) * 3],
    ids=[
        "empty", "letters", "leading_sign", "embedded_space", "none",
        "int", "float", "list", "unicode_digits",
    ],
)
def test_validated_activity_digits_refuses_bad_values(bad):
    with pytest.raises(ValueError):
        share_link.validated_activity_digits(bad)


def test_validated_activity_digits_message_never_includes_the_value():
    try:
        share_link.validated_activity_digits("a-totally-unique-token-9182")
    except ValueError as exc:
        message = str(exc)
    else:
        pytest.fail("expected a ValueError")
    assert "a-totally-unique-token-9182" not in message


# ---------------------------------------------------------------------------
# post_url -- pure, no page
# ---------------------------------------------------------------------------


def test_post_url_fills_the_template():
    assert share_link.post_url("1234") == (
        "https://www.linkedin.com/feed/update/urn:li:activity:1234/"
    )


def test_post_url_validates_before_filling():
    with pytest.raises(ValueError):
        share_link.post_url("not-digits")


# ---------------------------------------------------------------------------
# link_shape -- pure, no page
# ---------------------------------------------------------------------------


def test_link_shape_posts_kind_with_activity_id_and_query():
    link = (
        "https://www.linkedin.com/posts/someone_lq-activity-1234-xyz"
        "?utm_source=share"
    )
    shape = share_link.link_shape(link, "1234")
    assert shape == {
        "is_https": True,
        "host_is_linkedin": True,
        "path_kind": "posts",
        "carries_activity_id": True,
        "has_query": True,
        "length": len(link),
    }


def test_link_shape_feed_update_kind_no_query():
    link = "https://www.linkedin.com/feed/update/urn:li:activity:1234/"
    shape = share_link.link_shape(link, "1234")
    assert shape["path_kind"] == "feed_update"
    assert shape["has_query"] is False
    assert shape["carries_activity_id"] is True


def test_link_shape_other_kind_for_an_unrecognised_path():
    shape = share_link.link_shape(
        "https://www.linkedin.com/jobs/view/9999999/", "1234"
    )
    assert shape["path_kind"] == "other"


def test_link_shape_non_linkedin_host():
    shape = share_link.link_shape(
        "https://example.com/posts/x-activity-1234-y", "1234"
    )
    assert shape["host_is_linkedin"] is False


def test_link_shape_bare_linkedin_host_without_www_still_counts():
    shape = share_link.link_shape(
        "https://linkedin.com/posts/x-activity-1234-y", "1234"
    )
    assert shape["host_is_linkedin"] is True


def test_link_shape_not_https():
    shape = share_link.link_shape(
        "http://www.linkedin.com/posts/x-activity-1234-y", "1234"
    )
    assert shape["is_https"] is False


def test_link_shape_activity_id_must_be_a_whole_number_not_a_substring():
    # "1234" must not be reported as carried by a link whose number is
    # "51234" -- a substring match would be the wrong answer.
    shape = share_link.link_shape(
        "https://www.linkedin.com/posts/x-activity-51234-y", "1234"
    )
    assert shape["carries_activity_id"] is False


def test_link_shape_never_returns_a_substring_of_the_link():
    link = (
        "https://www.linkedin.com/posts/a-distinctive-marker-activity-1234-y"
        "?x=1"
    )
    shape = share_link.link_shape(link, "1234")
    for value in shape.values():
        if isinstance(value, str):
            assert "distinctive-marker" not in value
            assert link not in value


def test_link_shape_malformed_link_does_not_raise():
    shape = share_link.link_shape("not a url at all", "1234")
    assert shape["is_https"] is False
    assert shape["host_is_linkedin"] is False
    assert shape["path_kind"] == "other"
    assert shape["carries_activity_id"] is False
    assert shape["length"] == len("not a url at all")


# ---------------------------------------------------------------------------
# _normalise -- pure, no page
# ---------------------------------------------------------------------------


def test_normalise_lowercases_and_collapses_punctuation():
    assert (
        share_link._normalise("  Copy   Link!!  to Post ")
        == "copy link to post"
    )


def test_normalise_handles_none_and_empty():
    assert share_link._normalise(None) == ""
    assert share_link._normalise("") == ""


def test_normalise_matches_the_measured_live_trigger_label():
    assert (
        share_link._normalise("Open control menu for post")
        == "open control menu for post"
    )
    assert share_link._normalise("Open control menu for post").startswith(
        share_link.MENU_PREFIX
    )


# ---------------------------------------------------------------------------
# The two drain points -- _activate (the one click) and _clipboard (the one
# evaluate). readonly.SANCTIONED_MUTATIONS admits one call site per entry,
# "not a licence" (readonly.py's own words), so each of this module's two
# mutating kinds is reached from exactly one place, and both halves of that
# claim -- ONE literal call in the source, and ONE caller of the function
# that makes it -- are pinned here by AST, the same way
# tests/test_view_switch.py pins _activate for that module.
# ---------------------------------------------------------------------------


def _share_link_tree() -> ast.AST:
    return ast.parse(Path(share_link.__file__).read_text(encoding="utf-8"))


def _callers_of(tree: ast.AST, name: str) -> set[str]:
    """Every function whose body contains a bare-name call to ``name``."""
    callers: set[str] = set()
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == name:
                callers.add(fn.name)
    return callers


def test_activate_is_the_modules_only_click_and_its_only_caller_is_copy_own_post_link():
    tree = _share_link_tree()
    assert _callers_of(tree, "_activate") == {"copy_own_post_link"}
    clicks = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and n.attr == "click"
    ]
    assert len(clicks) == 1, clicks


def test_clipboard_is_the_modules_only_evaluate_and_its_only_caller_is_copy_own_post_link():
    tree = _share_link_tree()
    assert _callers_of(tree, "_clipboard") == {"copy_own_post_link"}
    evaluates = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and n.attr.startswith("evaluate")
    ]
    assert len(evaluates) == 1, evaluates


def test_escape_press_has_no_drain_point_and_stays_the_modules_only_press():
    """THE FOURTH REWORK POINT, PINNED: the Escape press is not routed
    through a third drain function -- it is one literal call, directly
    inside copy_own_post_link, exactly as before the rework."""
    tree = _share_link_tree()
    presses = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and n.attr == "press"
    ]
    assert len(presses) == 1, presses
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Attribute) and node.attr == "press":
                assert fn.name == "copy_own_post_link", fn.name


async def test_clipboard_refuses_an_unrecognised_mode_before_any_page_contact():
    with pytest.raises(ValueError):
        await share_link._clipboard(_NeverTouchedPage(), "delete")


async def test_clipboard_refuses_a_non_string_mode_before_any_page_contact():
    with pytest.raises(ValueError):
        await share_link._clipboard(_NeverTouchedPage(), None)


async def test_clipboard_install_and_read_are_the_only_two_modes_used(monkeypatch):
    """POSITIVE CONTROL for the two tests above: 'install' and 'read' must
    still work, or a validator that rejects everything would pass them
    trivially. Nothing is copied, so the read runs to its (shortened) bound
    and answers an empty list -- installed, nothing kept -- not None."""
    _shorten_the_read_wait(monkeypatch)
    async with _open_fixture() as page:
        result = await share_link._clipboard(page, "install")
        assert result is True
        texts = await share_link._clipboard(page, "read")
        assert texts == []


# ---------------------------------------------------------------------------
# THE TOOL, END TO END: linkedin_own_item_link on the fixture, offline.
#
# Everything above drives share_link directly with a stand-in counter
# reader. This drives the TOOL a caller calls -- its navigation, the landed-
# url check, the REAL counter reader (dom.read_reaction_surface) and the
# envelope it hands back -- against the same fixture, so a wiring defect is
# found here rather than by spending a live load on it. BROWSER is replaced
# by a stand-in whose goto navigates the local page by the fulfilled route:
# still no socket, still no linkedin.com.
# ---------------------------------------------------------------------------


class _FixtureBrowser:
    """BROWSER's two methods, over one local page; records every address."""

    def __init__(self, page: Any) -> None:
        self.page = page
        self.gotos: list[str] = []

    def session(self):
        @asynccontextmanager
        async def _session():
            yield self.page

        return _session()

    async def goto(self, page: Any, url: str) -> str:
        self.gotos.append(url)
        await page.goto(url, timeout=10_000)
        return page.url


async def _run_tool(monkeypatch, config: dict, **kwargs) -> tuple[dict, list[str]]:
    from linkedin_server import server

    async with _open_fixture(config) as page:
        browser = _FixtureBrowser(page)
        monkeypatch.setattr(server, "BROWSER", browser)
        payload = await server.linkedin_own_item_link(**kwargs)
        return payload, browser.gotos


async def test_the_tool_copies_on_one_load_and_withholds_the_link_by_default(
    monkeypatch,
):
    payload, gotos = await _run_tool(
        monkeypatch, {"reactionControl": True}, activity_id=ACTIVITY_DIGITS
    )
    assert gotos == [share_link.post_url(ACTIVITY_DIGITS)], gotos
    assert payload.get("permitted") is True, payload
    assert payload["copied"] is True, payload
    assert payload["shape"]["carries_activity_id"] is True, payload
    assert payload["pages_loaded"] == 1, payload
    # THE LINK IS NOT IN THE ENVELOPE unless asked for; its presence is.
    assert "link" not in payload, payload
    assert payload["link_withheld"] is True, payload
    # The price was a REAL reading: one reaction toggle, OFF, unmoved.
    assert payload["counters"].get("refused") is None, payload


async def test_the_tool_returns_the_link_only_when_asked(monkeypatch):
    payload, _ = await _run_tool(
        monkeypatch, {"reactionControl": True},
        activity_id=ACTIVITY_DIGITS, include_link=True,
    )
    assert payload["copied"] is True, payload
    assert share_link.link_shape(payload["link"], ACTIVITY_DIGITS)[
        "carries_activity_id"
    ] is True
    assert "link_withheld" not in payload, payload


async def test_the_tool_refuses_when_the_press_moves_the_reaction_counter(
    monkeypatch,
):
    """THE PRICE, SHOWN FAILING END TO END: the copy press also flips the
    item's reaction toggle, as an outward act would. The tool's own reader
    must see off_state move and the verdict must refuse -- whatever the
    clipboard captured."""
    payload, _ = await _run_tool(
        monkeypatch, {"reactionControl": True, "copyReacts": True},
        activity_id=ACTIVITY_DIGITS,
    )
    assert payload.get("permitted") is False, payload
    assert payload["counters"].get("refused") == "counter_moved", payload


async def test_the_tool_refuses_a_bad_id_with_no_load(monkeypatch):
    payload, gotos = await _run_tool(monkeypatch, {}, activity_id="12a45")
    assert payload.get("refused") == "bad_activity_id", payload
    assert payload["pages_loaded"] == 0, payload
    assert gotos == [], gotos
