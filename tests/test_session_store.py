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

from linkedin_server.session_store import (
    MAX_AGE_S,
    REARM_AFTER_S,
    SESSION_COOKIE,
    SessionStore,
)


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
    """A jar shaped the way Playwright actually returns one.

    DOMAIN AND PATH ARE NOT DECORATION HERE. ``add_cookies`` requires them, so
    a cookie without them cannot be restored -- and the first version of this
    module stored such cookies happily. See
    ``test_a_cookie_that_cannot_be_restored_is_never_stored``.
    """
    return [
        {"name": n, "value": f"value-of-{n}", "domain": ".linkedin.com", "path": "/"}
        for n in names
    ]


def age_the_jar(store, seconds):
    """Rewrite the stored timestamp so the jar reads as ``seconds`` old.

    The same move ``test_restore_refuses_a_stale_jar`` used to make inline. It
    is a helper now because the jar's AGE is load-bearing on BOTH sides -- the
    restore refusal and the re-arm -- and two tests that age a jar by two
    different routes stop being about the same clock.
    """
    data = json.loads(store.path.read_text(encoding="utf-8"))
    data["saved_at"] = data["saved_at"] - seconds
    store.path.write_text(json.dumps(data), encoding="utf-8")


# -- THE CASE THE MODULE EXISTS FOR ----------------------------------------


async def test_an_emptied_profile_plus_a_populated_store_is_a_session(store):
    """THE ROUND TRIP. Harvest, lose the profile, restore, signed in again.

    Every other test here checks a rule. This checks the PURPOSE: that the
    store can actually put a session back into a context Chrome has emptied.

    It is written deliberately because the restore path only ever runs in the
    rare case -- a profile that still has its session is left alone, which is
    correct -- so without a test built for it, the one path that justifies the
    whole module would never execute in the suite at all.
    """
    signed_in = FakeContext(jar(SESSION_COOKIE, "JSESSIONID", "bcookie"))
    assert (await store.save_from_context(signed_in, method="login"))["saved"] is True

    # What Chrome leaves behind after its downgrade migration.
    wiped = FakeContext([])
    assert SESSION_COOKIE not in {c["name"] for c in await wiped.cookies()}

    out = await store.restore_into_context(wiped)

    assert out["restored"] is True
    names = {c["name"] for c in await wiped.cookies()}
    assert SESSION_COOKIE in names, "the session did not come back"
    assert names == {SESSION_COOKIE, "JSESSIONID", "bcookie"}

    # And what came back is USABLE -- full value, domain and path, not a stub.
    restored = {c["name"]: c for c in wiped.added}
    assert restored[SESSION_COOKIE]["domain"] == ".linkedin.com"
    assert restored[SESSION_COOKIE]["path"] == "/"
    assert restored[SESSION_COOKIE]["value"]


async def test_a_live_auth_check_arms_an_empty_store(monkeypatch, tmp_path):
    """THE NET MUST NOT NEED THE DISASTER IN ORDER TO EXIST.

    The harvest originally lived only in ``login_via_browser``, so the store
    could be filled ONLY by the interactive sign-in -- which is the event it
    exists to spare him. If Chrome discarded the profile, the store would be
    empty, he would sign in, and only THEN would it fill: it protected the
    second failure and never the first.

    It was invisible for the same reason the previous defect was. A working
    profile never signs in, so the store simply stayed empty and empty looks
    exactly like not-yet-needed. Measured: three restarts on correct code,
    store empty throughout.

    So a confirmed live session now arms it, and this asserts that -- because
    like the restore path, this fires only in a condition the suite will never
    wander into on its own.
    """
    from linkedin_server import auth as auth_module
    from linkedin_server import browser as browser_module

    store = SessionStore(tmp_path / "armed.json")
    monkeypatch.setattr(browser_module, "SESSION_STORE", store, raising=False)
    assert not store.path.exists()

    page = type("P", (), {"context": FakeContext(jar(SESSION_COOKIE, "bcookie"))})()
    await auth_module._arm_session_store(page)

    assert store.path.exists(), "a live session did not arm the store"
    info = store.describe()
    assert info["has_session_cookie"] is True
    assert info["method"] == "check_auth"


async def test_arming_never_overwrites_a_store_that_already_has_a_session(
    monkeypatch, tmp_path
):
    """A populated store is left exactly alone.

    Refreshing it on every read would trade a known-good jar for a newer one
    on no evidence the newer one is better, and would multiply the chances of
    damaging the thing being protected.
    """
    from linkedin_server import auth as auth_module
    from linkedin_server import browser as browser_module

    store = SessionStore(tmp_path / "armed.json")
    monkeypatch.setattr(browser_module, "SESSION_STORE", store, raising=False)
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE)), method="login")
    before = store.path.read_text(encoding="utf-8")

    page = type("P", (), {"context": FakeContext(jar(SESSION_COOKIE, "extra"))})()
    await auth_module._arm_session_store(page)

    assert store.path.read_text(encoding="utf-8") == before


# -- THE DEADLOCK BETWEEN THE TWO AGE RULES --------------------------------


async def test_a_jar_too_old_to_restore_is_not_too_good_to_replace(
    monkeypatch, tmp_path
):
    """THE DEFECT. Two correct rules met on day 31 and killed the mechanism.

    ``restore_into_context`` refuses any jar older than ``MAX_AGE_S``, which
    is right -- a jar from a machine state nobody remembers should not be
    resurrected. ``_arm_session_store`` refuses to write over a store that is
    present and holds a session cookie, which is also right -- a known-good
    jar should not be traded for a newer one on no evidence.

    Neither rule looked at the other. Past thirty days a stored jar was
    SIMULTANEOUSLY too old to restore and too present to replace, so the store
    sat there inert and reported nothing wrong: ``describe`` said present,
    ``has_session_cookie`` said true, and the one thing it could never do
    again was the thing it exists for.

    Nothing was bricked -- ``login_via_browser`` harvests with no guard at
    all, so a sign-in still re-armed it. The cost was exactly one sign-in,
    which is the single event this whole module exists to spare him.
    """
    from linkedin_server import auth as auth_module
    from linkedin_server import browser as browser_module

    store = SessionStore(tmp_path / "armed.json")
    monkeypatch.setattr(browser_module, "SESSION_STORE", store, raising=False)
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE)), method="login")
    age_the_jar(store, MAX_AGE_S + 1)

    assert store.describe()["stale"] is True
    assert (await store.restore_into_context(FakeContext([])))["restored"] is False

    page = type("P", (), {"context": FakeContext(jar(SESSION_COOKIE, "bcookie"))})()
    await auth_module._arm_session_store(page)

    after = store.describe()
    assert after["stale"] is False, (
        "a live session did not replace a jar that had gone past the restore "
        "ceiling -- the store is inert and says nothing about it"
    )
    assert after["method"] == "check_auth"


async def test_a_jar_is_replaced_while_it_is_still_good_not_after_it_dies(
    monkeypatch, tmp_path
):
    """THE MARGIN. A re-arm that waits for expiry re-arms only corpses.

    If the re-arm threshold equalled ``MAX_AGE_S``, a jar would become
    eligible for replacement at the exact moment it stopped working -- and the
    replacement needs a LIVE session to harvest from, which is precisely what
    the disaster this store exists for takes away. A profile Chrome has
    emptied produces no 200, so no re-arm, so the jar is never refreshed in
    the one situation that matters.

    The jar is therefore refreshed while it is still restorable. This pins a
    jar at 80% of the ceiling -- comfortably alive, refusing nothing -- and
    requires that a live check replaces it anyway.
    """
    from linkedin_server import auth as auth_module
    from linkedin_server import browser as browser_module

    store = SessionStore(tmp_path / "armed.json")
    monkeypatch.setattr(browser_module, "SESSION_STORE", store, raising=False)
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE)), method="login")
    age_the_jar(store, int(MAX_AGE_S * 0.8))

    before = store.describe()
    assert before["stale"] is False, "the fixture must be a jar that still works"
    assert (await store.restore_into_context(FakeContext([])))["restored"] is True

    page = type("P", (), {"context": FakeContext(jar(SESSION_COOKIE, "bcookie"))})()
    await auth_module._arm_session_store(page)

    after = store.describe()
    assert after["age_seconds"] < before["age_seconds"], (
        "a jar four fifths of the way to the ceiling was not refreshed, so its "
        "remaining life is whatever is left rather than a full term"
    )
    assert after["method"] == "check_auth"

def test_the_rearm_margin_is_derived_and_leaves_real_headroom():
    """The two controls on the margin, stated as relationships not literals.

    Pinning ``REARM_AFTER_S == 1296000`` would pass for the wrong reasons and
    would have to be edited by anyone re-ruling the number, which makes it a
    speed bump rather than a check. What must hold is:

    * STRICTLY SHORTER than the restore ceiling. Equality is the defect --
      a jar would become replaceable only once it had stopped working, and a
      re-arm needs the live session the disaster removes.
    * A re-arm at least DOUBLES the remaining restorable life. This is the
      evidence that justifies overwriting a store the module otherwise calls
      good: not "newer", but a jar of identical provenance with strictly more
      term than the one it replaces. It also forbids the other failure --
      a margin so close to the ceiling that the doubling argument is gone.
    """
    assert 0 < REARM_AFTER_S < MAX_AGE_S
    assert MAX_AGE_S - REARM_AFTER_S >= REARM_AFTER_S


async def test_a_jar_well_inside_the_margin_is_still_left_exactly_alone(
    monkeypatch, tmp_path
):
    """The guard must have gained a threshold, not lost a rule.

    The sibling test uses a jar written moments ago, which would survive even a
    margin of one second -- so it cannot tell a real margin from a collapsed
    guard. This one is a quarter of the way to the ceiling: old enough that
    "always re-arm" would rewrite it, young enough that it must not be.
    """
    from linkedin_server import auth as auth_module
    from linkedin_server import browser as browser_module

    store = SessionStore(tmp_path / "armed.json")
    monkeypatch.setattr(browser_module, "SESSION_STORE", store, raising=False)
    await store.save_from_context(FakeContext(jar(SESSION_COOKIE)), method="login")
    age_the_jar(store, int(MAX_AGE_S * 0.25))
    before = store.path.read_text(encoding="utf-8")

    page = type("P", (), {"context": FakeContext(jar(SESSION_COOKIE, "extra"))})()
    await auth_module._arm_session_store(page)

    assert store.path.read_text(encoding="utf-8") == before


async def test_arming_never_breaks_the_auth_answer(monkeypatch, tmp_path):
    """A harvest is an errand during a read and may never fail the read.

    If a broken store could turn a working auth_status into an error, the
    safety net would have become a new way to lose access -- the exact
    inversion this module must not perform.
    """
    from linkedin_server import auth as auth_module
    from linkedin_server import browser as browser_module

    class Exploding:
        path = tmp_path / "boom.json"

        def describe(self):
            raise RuntimeError("store is on fire")

    monkeypatch.setattr(browser_module, "SESSION_STORE", Exploding(), raising=False)
    page = type("P", (), {"context": FakeContext(jar(SESSION_COOKIE))})()

    await auth_module._arm_session_store(page)  # must not raise


#: A jar shaped like the real one that shipped: LinkedIn rows mixed with the
#: whole rest of the browser, because ``context.cookies()`` returns everything.
FOREIGN = [
    {"name": "SID", "value": "x" * 70, "domain": ".google.com", "path": "/"},
    {"name": "LSID", "value": "x" * 70, "domain": "accounts.google.com", "path": "/"},
    {"name": "__Secure-1PSID", "value": "x" * 70, "domain": ".google.com", "path": "/"},
    {"name": "fr", "value": "x" * 30, "domain": ".facebook.com", "path": "/"},
    {"name": "MUID", "value": "x" * 30, "domain": ".bing.com", "path": "/"},
    {"name": "uuid2", "value": "x" * 30, "domain": ".adnxs.com", "path": "/"},
]


async def test_another_sites_cookies_never_reach_the_disk(store):
    """THE CONTROL FOR THE WORST DEFECT THIS MODULE HAS HAD.

    ``context.cookies()`` returns the WHOLE browser jar. The first working
    harvest wrote 92 cookies of which 68 were foreign -- 17 ``.google.com``,
    8 ``accounts.google.com``, 11 ``.youtube.com``, plus facebook, bing and a
    dozen ad networks. The Google rows were ``SID``, ``LSID`` and the
    ``__Host-`` prefixed ones: live authentication for his Google account.

    Chrome keeps that jar encrypted under AES-256-GCM. This file is plaintext
    JSON. So the harvest took credentials Chrome deliberately seals and wrote
    them out in the clear.

    A rule in a comment would not have caught it. This goes red.
    """
    mixed = FakeContext(jar(SESSION_COOKIE, "JSESSIONID") + FOREIGN)
    out = await store.save_from_context(mixed, method="test")

    assert out["saved"] is True
    written = store.path.read_text(encoding="utf-8")

    # Not one foreign cookie, by name OR by domain, anywhere in the file.
    for cookie in FOREIGN:
        assert cookie["name"] not in written, cookie["name"]
        assert cookie["domain"] not in written, cookie["domain"]

    stored = json.loads(written)["cookies"]
    assert {c["name"] for c in stored} == {SESSION_COOKIE, "JSESSIONID"}
    assert all(c["domain"].endswith("linkedin.com") for c in stored)


@pytest.mark.parametrize(
    "domain,belongs",
    [
        (".linkedin.com", True),
        ("www.linkedin.com", True),
        (".www.linkedin.com", True),
        ("linkedin.com", True),
        (".google.com", False),
        ("accounts.google.com", False),
        # Lookalikes. A substring match on "linkedin.com" would admit both.
        ("evil-linkedin.com", False),
        ("linkedin.com.attacker.net", False),
        ("", False),
    ],
)
def test_the_domain_test_is_not_a_substring_match(domain, belongs):
    """Matching on the registrable domain, not on whether the text appears.

    ``linkedin.com.attacker.net`` contains ``linkedin.com``. A substring check
    would hand that site's cookies straight into the store.
    """
    from linkedin_server.session_store import is_linkedin_cookie

    assert is_linkedin_cookie({"domain": domain}) is belongs


async def test_restore_refuses_foreign_rows_from_an_older_file(store):
    """The belt. The write filter is the fix; this covers a file that predates
    it, or one edited by hand.

    Injecting somebody's Google session into a browser context is not
    something this server should be capable of even from a bad input.
    """
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text(
        json.dumps(
            {
                "saved_at": __import__("time").time(),
                "method": "old version",
                "cookies": jar(SESSION_COOKIE) + FOREIGN,
                "has_session": True,
            }
        ),
        encoding="utf-8",
    )

    ctx = FakeContext([])
    out = await store.restore_into_context(ctx)

    assert out["restored"] is True
    injected = {c["name"] for c in ctx.added}
    assert injected == {SESSION_COOKIE}
    for cookie in FOREIGN:
        assert cookie["name"] not in injected


async def test_a_cookie_that_cannot_be_restored_is_never_stored(store):
    """THE DEFECT THAT SHIPPED, pinned so it cannot ship twice.

    A test's FakePage returns cookies as ``{"li_at": "pending"}`` -- a name
    and a seven-character value, no domain, no path. The first version of this
    module stored that into the operator's REAL session file. It looked like a
    populated store and could never have restored anything, because
    ``add_cookies`` cannot use a cookie without a domain.

    WHY IT WENT UNNOTICED IS THE PART WORTH KEEPING. The degrade rules are
    good: every restore path returns ``restored: false`` with a reason. So a
    store that can NEVER work is indistinguishable from a store that is not
    needed yet -- and the day it is needed is the day the profile was
    discarded, which is the one day it matters. Graceful degradation hides a
    broken mechanism perfectly. The validation therefore lives at the WRITE.
    """
    stub = FakeContext([{"name": SESSION_COOKIE, "value": "pending"}])
    out = await store.save_from_context(stub, method="login_via_browser")

    assert out["saved"] is False
    assert not store.path.exists(), "an unrestorable jar reached the disk"

    # WHICH guard catches it changed on 2026-08-26 and the assertion is
    # written not to care. The fixture cookie has no domain, so the
    # linkedin-only filter now rejects it BEFORE the restorability check ever
    # runs -- it counts as foreign rather than as unrestorable. Both are
    # correct rejections, and pinning one counter would make this test fail
    # the next time a guard is added in front of it. What must hold is that it
    # is refused and that nothing reaches disk.
    assert out["dropped_foreign"] + out["rejected_unrestorable"] == 1


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
