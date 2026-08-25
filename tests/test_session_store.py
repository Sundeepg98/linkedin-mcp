"""The session store: a net beneath the profile, never a new way to fail.

WHY IT EXISTS. Measured 2026-08-25: the LinkedIn Chrome profile carries a
NEWER Chrome's version stamp (151.0.7922.34, from the operator's own browser)
than playwright's chromium, so Chrome runs its downgrade migration on launch,
moves the profile aside and starts clean -- taking the session with it. That
is why he had to sign in again and again while naukri, whose profile carries
playwright's own stamp, held a session for days.

WHAT THESE TESTS HOLD, and each one is a rule that could quietly stop being
true:

* the store is ADDITIVE -- it never writes to or deletes the profile;
* restore is CONDITIONAL -- never over a live session, only into an emptied
  one, because injecting an older jar over a working one would make this a
  way to resurrect a stale session rather than a net;
* every failure DOWNGRADES to today's behaviour and none of them raises;
* the write is ATOMIC, because a truncated file that still parses is the
  worst outcome available here -- a store that reads as a session and is not;
* cookie VALUES never appear in anything reported.
"""
from __future__ import annotations

import json

import pytest

from linkedin_server.session_store import MAX_AGE_S, SESSION_COOKIE, SessionStore


class FakeContext:
    """A Playwright context, reduced to the two calls the store makes."""

    def __init__(self, cookies=None, add_raises=False, read_raises=False):
        self._cookies = list(cookies or [])
        self.added = None
        self._add_raises = add_raises
        self._read_raises = read_raises

    async def cookies(self):
        if self._read_raises:
            raise RuntimeError("context is gone")
        return list(self._cookies)

    async def add_cookies(self, cookies):
        if self._add_raises:
            raise RuntimeError("injection refused")
        self.added = list(cookies)
        self._cookies.extend(cookies)


def jar(*names):
    return [
        {"name": n, "value": f"value-of-{n}", "domain": ".linkedin.com", "path": "/"}
        for n in names
    ]


@pytest.fixture
def store(tmp_path):
    return SessionStore(tmp_path / "session.json")


# -- saving ----------------------------------------------------------------


async def test_a_live_jar_is_saved_and_the_file_is_owner_only(store):
    ctx = FakeContext(jar(SESSION_COOKIE, "JSESSIONID", "bcookie"))
    out = await store.save_from_context(ctx, method="test")
    assert out["saved"] is True
    assert out["cookie_count"] == 3
    assert store.path.exists()


async def test_a_signed_out_jar_never_overwrites_a_good_one(store):
    """The failure mode that would make this LOSE the session it protects."""
    good = FakeContext(jar(SESSION_COOKIE, "bcookie"))
    assert (await store.save_from_context(good, method="first"))["saved"] is True
    before = store.path.read_text(encoding="utf-8")

    empty = FakeContext(jar("bcookie"))  # no session cookie
    out = await store.save_from_context(empty, method="second")

    assert out["saved"] is False
    assert SESSION_COOKIE in out["why"]
    assert store.path.read_text(encoding="utf-8") == before, "the good jar was clobbered"


async def test_an_unreadable_context_does_not_raise(store):
    out = await store.save_from_context(FakeContext(read_raises=True), method="test")
    assert out["saved"] is False
    assert not store.path.exists()


async def test_the_write_leaves_no_temp_file_behind(store):
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE)), method="test")
    leftovers = list(store.path.parent.glob("*.tmp"))
    assert leftovers == [], leftovers


# -- restoring -------------------------------------------------------------


async def test_restore_puts_the_jar_back_into_an_emptied_profile(store):
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE, "bcookie")), method="t")

    emptied = FakeContext([])  # what Chrome leaves after a downgrade migration
    out = await store.restore_into_context(emptied)

    assert out["restored"] is True
    assert out["cookie_count"] == 2
    assert {c["name"] for c in emptied.added} == {SESSION_COOKIE, "bcookie"}


async def test_restore_refuses_over_a_live_session(store):
    """THE CONDITION THAT MAKES THIS A NET RATHER THAN A RESURRECTION.

    A profile that still holds a session is the FRESHER source. Injecting an
    older stored jar over it would silently swap a working session for a
    stale one, which is a worse failure than the one this module fixes.
    """
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE)), method="t")

    live = FakeContext(jar(SESSION_COOKIE, "bcookie"))
    out = await store.restore_into_context(live)

    assert out["restored"] is False
    assert live.added is None, "it injected over a working session"


async def test_restore_refuses_a_stale_jar(store):
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE)), method="t")
    data = json.loads(store.path.read_text(encoding="utf-8"))
    data["saved_at"] = data["saved_at"] - (MAX_AGE_S + 1)
    store.path.write_text(json.dumps(data), encoding="utf-8")

    out = await store.restore_into_context(FakeContext([]))
    assert out["restored"] is False
    assert "old" in out["why"] or "stale" in out["why"].lower()


@pytest.mark.parametrize(
    "content",
    ["", "{", "null", "[]", '{"cookies": []}'],
    ids=["empty", "truncated", "null", "wrong type", "no cookies"],
)
async def test_every_broken_file_downgrades_and_none_of_them_raises(store, content):
    """A missing or corrupt store must behave exactly like no store at all.

    This is the whole safety argument for shipping it: the worst it can do is
    leave the server behaving as it did before the module existed.
    """
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text(content, encoding="utf-8")

    out = await store.restore_into_context(FakeContext([]))
    assert out["restored"] is False
    assert out["why"]


async def test_a_failed_injection_is_reported_not_raised(store):
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE)), method="t")
    out = await store.restore_into_context(FakeContext([], add_raises=True))
    assert out["restored"] is False


# -- disclosure ------------------------------------------------------------


async def test_nothing_reported_ever_contains_a_cookie_value(store):
    """Names and counts. The sibling server's rule, and this one's already."""
    ctx = FakeContext(jar(SESSION_COOKIE, "bcookie"))
    saved = await store.save_from_context(ctx, method="test")
    described = store.describe()
    restored = await store.restore_into_context(FakeContext([]))

    blob = json.dumps([saved, described, restored])
    for cookie in ctx._cookies:
        assert cookie["value"] not in blob, "a cookie value escaped into a report"

    assert described["has_session_cookie"] is True
    assert SESSION_COOKIE in described["cookie_names"]


async def test_the_store_never_touches_the_profile():
    """ADDITIVE, asserted over the AST rather than over the text.

    The first version of this test grepped the SOURCE for "CHROME_DELETE" and
    failed -- on the module docstring, which names that directory to explain
    the bug being fixed. A check that fires on an explanation of a hazard,
    rather than on the hazard, is the defect this repo keeps finding in its
    own guards: it makes documenting a danger cost you a red test, which is
    exactly backwards.

    So this walks the parsed tree and looks at CALLS. Prose is invisible to
    it, and a destructive call cannot hide in a comment.
    """
    import ast
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[1]
        / "linkedin_server"
        / "session_store.py"
    ).read_text(encoding="utf-8")

    destructive = {"rmtree", "move", "remove", "rmdir"}
    called: list[str] = []
    unlink_calls = 0
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        name = None
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
        elif isinstance(node.func, ast.Name):
            name = node.func.id
        if name in destructive:
            called.append(name)
        if name == "unlink":
            unlink_calls += 1

    assert called == [], f"destructive call(s) in the session store: {called}"
    # unlink is allowed EXACTLY once: cleaning up the store's own temp file
    # after a failed write. Pinned by count so a second one has to argue for
    # itself in review rather than arriving quietly.
    assert unlink_calls == 1, unlink_calls
