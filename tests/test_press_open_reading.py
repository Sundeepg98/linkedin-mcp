"""THE OPEN-MOMENT READING AND THE SCOPE TABLE, tested without pressing anything.

Added 2026-09-23 with ``press.OPEN_READINGS`` and ``press.PRESS_SCOPES``
(`_audit/2026-09-23-readers-four-rows.md`). Until then the only instant at
which a press's disclosure exists -- between the click and the Escape -- was
spent on a closed count that says THAT something opened and never WHAT, so no
reader could read what the gate disclosed.

Every test runs against a FAKE page. The fake is stateful on purpose: the
shipped fakes hand out fixed readings, which cannot model "this phrase is on
the page only while the menu is open" -- the one fact this mechanism exists to
capture. It records every event in order, so the tests can assert WHEN the
reading was taken relative to the click and the dismissal, not merely that it
was taken.

The refusals the two new keys can produce are classified and driven by the
exhaustive inventory in ``tests/test_press.py`` (``WHEN_KNOWABLE`` and
``_REACHES``), not here, so there is one inventory and not two.
"""
from __future__ import annotations

import re

import pytest

from linkedin_server import company_root, dom, press, readonly

BASE = "https://www.linkedin.com"
FEED = f"{BASE}/feed/"
SHARE = "feed_item_share_menu"


def _phrases(key: str) -> list[str]:
    return [phrase for _term, phrase in press.open_reading(key)["phrases"]]


def _terms(key: str) -> set[str]:
    return {term for term, _phrase in press.open_reading(key)["phrases"]}


# ---------------------------------------------------------------------------
# A page that knows whether its menu is open
# ---------------------------------------------------------------------------


class Loc:
    def __init__(self, page, chain):
        self.page = page
        self.chain = tuple(chain)

    def locator(self, selector):
        self.page.events.append(("locator", self.chain + (selector,)))
        return Loc(self.page, self.chain + (selector,))

    def nth(self, _index):
        return self

    async def count(self):
        return self.page.count_for(self.chain)

    async def get_attribute(self, name):
        assert name == "aria-expanded", name
        return "true" if self.page.open else "false"

    async def click(self, **_kwargs):
        self.page.events.append(("click", self.chain))
        self.page.open = True


class Keyboard:
    def __init__(self, page):
        self.page = page

    async def press(self, key):
        self.page.events.append(("key", key))
        if key == "Escape":
            self.page.open = False


class Page:
    """``closed`` and ``opened`` are the COUNT_LINES answers for each state.

    Each is a list of ``(phrase_position, shape_position, value)`` triples, or
    the string ``"raise"`` to make the evaluate call fail in that state.
    """

    def __init__(
        self,
        url=FEED,
        *,
        closed=(),
        opened=(),
        scoped_count=1,
        page_count=1,
    ):
        self.url = url
        self.open = False
        self.closed = closed
        self.opened = opened
        self.scoped_count = scoped_count
        self.page_count = page_count
        self.events: list = []
        self.keyboard = Keyboard(self)

    def locator(self, selector):
        self.events.append(("locator", (selector,)))
        return Loc(self, (selector,))

    def count_for(self, chain):
        if len(chain) == 1 and chain[0] in dict(press.WITNESS_SELECTORS).values():
            return 1 if self.open else 0
        if len(chain) == 2:
            return self.scoped_count
        return self.page_count

    async def evaluate(self, script, arg=None):
        state = "open" if self.open else "closed"
        self.events.append(("evaluate", state))
        assert script == dom.COUNT_LINES_JS, "the reading ran some other script"
        answer = self.opened if self.open else self.closed
        if answer == "raise":
            raise RuntimeError("synthetic")
        return {
            "elements": 10,
            "chunks": 10,
            "chunks_capped": 0,
            "hidden_skipped": 2,
            "non_content_skipped": 0,
            "matches": [
                {"phrase": p, "shape": s, "value": v, "chars": 12}
                for p, s, v in answer
            ],
        }


async def _steady():
    return {"off_state": 3}


def _moving():
    values = iter([{"off_state": 3}, {"off_state": 4}])

    async def read():
        return next(values)

    return read


def _position(key: str, phrase: str) -> int:
    return _phrases(key).index(phrase)


# ---------------------------------------------------------------------------
# 1. THE TABLES ARE CLOSED, COMPLETE, AND STRUCTURAL
# ---------------------------------------------------------------------------


def test_every_reading_entry_carries_its_whole_shape():
    names = [name for name, _entry in press.OPEN_READINGS]
    assert len(names) == len(set(names)), names
    for name, entry in press.OPEN_READINGS:
        missing = [f for f in press._READING_REQUIRED if not entry.get(f)]
        assert not missing, (name, missing)
        assert re.fullmatch(r"[a-z][a-z0-9_]*", name), name


def test_every_reading_surface_is_admitted_and_pressable():
    """A reading on a surface no press may happen on is a reading nobody takes.

    Each surface must be ADMITTED by the read boundary and must carry a
    SENSITIVITY BASIS, or the gate refuses every press there before the reading
    could ever run -- and an entry that can never run is a claim, not a check.
    """
    for name, entry in press.OPEN_READINGS:
        for path in entry["surfaces"]:
            url = BASE + path
            assert readonly.is_read_url(url), (name, path)
            assert press.check_basis(url).get("refused") is None, (name, path)


def test_every_phrase_is_already_in_the_form_the_page_compares():
    """A phrase that is not normalised can never match, and would sit in the
    table looking like a measurement. Checked with the shipped normaliser the
    count-line reader's own tests use for the same purpose."""
    for name, entry in press.OPEN_READINGS:
        for term, phrase in entry["phrases"]:
            assert re.fullmatch(r"[a-z][a-z0-9_]*", term), (name, term)
            assert company_root.normalised(phrase) == phrase, (name, phrase)


def test_every_scope_is_structural_and_never_a_label():
    """CONDITION 2'S RULE, one level up: a scope may not read text or a name."""
    names = [name for name, _entry in press.PRESS_SCOPES]
    assert len(names) == len(set(names)), names
    forbidden = ("aria-label", "text=", "has-text", ":text", "title", "alt=", '"')
    for name, entry in press.PRESS_SCOPES:
        missing = [f for f in press._SCOPE_REQUIRED if not entry.get(f)]
        assert not missing, (name, missing)
        selector = entry["selector"]
        for token in forbidden:
            assert token not in selector, (name, selector, token)


def test_an_unknown_key_is_refused_by_every_entry_point():
    assert press.check_reading(FEED, "nope")["refused"] == "reading_not_sanctioned"
    assert press.check_scope("nope")["refused"] == "scope_not_sanctioned"
    for refusal in (press.check_reading(FEED, "nope"), press.check_scope("nope")):
        assert refusal["reachable_by_this_route"] is False, refusal
    # And the absence of a key is the gate as it was, not a refusal.
    assert press.check_reading(FEED, None).get("refused") is None
    assert press.check_scope(None).get("refused") is None


def test_a_reading_surface_is_matched_exactly_not_by_prefix():
    """The feed entry must not travel onto a permalink page because the path
    happens to start with ``/feed/``: its phrases were chosen for one page."""
    permalink = f"{BASE}/feed/update/urn:li:activity:12345/"
    assert readonly.is_read_url(permalink)
    verdict = press.check_reading(permalink, SHARE)
    assert verdict["refused"] == "reading_not_for_this_surface", verdict


# ---------------------------------------------------------------------------
# 2. THE READING IS TAKEN AT THE OPEN MOMENT, AND ONLY THE PRESS IS CREDITED
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_reading_is_taken_before_the_click_and_again_before_the_escape():
    embed = _position(SHARE, "embed this post")
    page = Page(opened=[(embed, 0, 0)])
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_steady, reading=SHARE
    )
    order = [e for e in page.events if e[0] in ("evaluate", "click", "key")]
    assert order == [
        ("evaluate", "closed"),
        ("click", ("[aria-expanded]",)),
        ("evaluate", "open"),
        ("key", "Escape"),
    ], order
    assert verdict["reading"]["appeared"] == ["embed"], verdict["reading"]


@pytest.mark.asyncio
async def test_a_phrase_already_on_the_page_is_not_credited_to_the_press():
    """A feed post's own text can say anything. What was there before the click
    HELD; only what arrived with the press APPEARED."""
    link = _position(SHARE, "copy link")
    embed = _position(SHARE, "embed this post")
    page = Page(closed=[(link, 0, 0)], opened=[(link, 0, 0), (embed, 0, 0)])
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_steady, reading=SHARE
    )
    reading = verdict["reading"]
    assert reading["appeared"] == ["embed"], reading
    assert reading["held"] == ["copy_link"], reading
    assert reading["gone"] == [], reading


@pytest.mark.asyncio
async def test_an_unread_moment_is_undetermined_and_still_closes_the_press():
    """A reading that did not happen is not a reading that found nothing -- and
    a reading that FAILED between the click and the Escape must not skip the
    Escape."""
    page = Page(opened="raise")
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_steady, reading=SHARE
    )
    assert ("key", "Escape") in page.events, page.events
    reading = verdict["reading"]
    assert reading["appeared"] is None and reading["held"] is None, reading
    assert reading["open"] == {"read": False, "unreadable": "RuntimeError"}, reading
    # And the verdict is still decided on safety, exactly as without a reading.
    assert verdict.get("permitted") is True, verdict


@pytest.mark.asyncio
async def test_the_reading_never_decides_the_verdict():
    embed = _position(SHARE, "embed this post")
    # A press that MOVES the sensitive counter is a write, whatever it showed.
    page = Page(opened=[(embed, 0, 0)])
    moved = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_moving(), reading=SHARE
    )
    assert moved["refused"] == "counter_moved", moved
    assert moved["reading"]["appeared"] == ["embed"], (
        "the reading rides on a refusal too -- as evidence, never as a delivered read"
    )
    # And a safe press that brought nothing into view is still permitted.
    quiet = await press.disclose(
        Page(), shape="[aria-expanded]", read_counters=_steady, reading=SHARE
    )
    assert quiet.get("permitted") is True, quiet
    assert quiet["reading"]["appeared"] == [], quiet["reading"]


@pytest.mark.asyncio
async def test_the_reading_publishes_only_its_own_literals_and_integers():
    """THE CLOSED ALPHABET. Positions outside the phrase list are DROPPED, never
    clamped onto the first phrase, and every word that leaves is a term from
    the table or a shape word from ``company_root.NUMERAL_SHAPES``."""
    count = len(_phrases(SHARE))
    embed = _position(SHARE, "embed this post")
    page = Page(opened=[(count, 1, 7), (-1, 1, 9), (embed, 99, 5)])
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_steady, reading=SHARE
    )
    terms = verdict["reading"]["open"]["terms"]
    assert set(terms) <= _terms(SHARE), terms
    assert set(terms) == {"embed"}, (
        f"out-of-range positions must be dropped, not clamped: {terms}"
    )
    words = set(company_root.NUMERAL_SHAPES) | {"position_out_of_range"}
    for entry in terms.values():
        assert entry["numeral"] in words, entry
        assert entry["value"] is None or isinstance(entry["value"], int), entry


@pytest.mark.asyncio
async def test_a_value_rides_only_on_the_two_shapes_that_carry_one():
    embed = _position(SHARE, "embed this post")
    link = _position(SHARE, "copy link")
    percent = company_root.NUMERAL_SHAPES.index("percent_refused")
    plain = company_root.NUMERAL_SHAPES.index("plain_digits")
    page = Page(opened=[(embed, percent, 40), (link, plain, 3)])
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_steady, reading=SHARE
    )
    terms = verdict["reading"]["open"]["terms"]
    assert terms["embed"] == {"numeral": "percent_refused", "value": None}, terms
    assert terms["copy_link"] == {"numeral": "plain_digits", "value": 3}, terms


@pytest.mark.asyncio
async def test_no_reading_asked_for_is_the_gate_exactly_as_it_was():
    page = Page()
    verdict = await press.disclose(page, shape="[aria-expanded]", read_counters=_steady)
    assert "reading" not in verdict, verdict
    assert not [e for e in page.events if e[0] == "evaluate"], page.events
    pre = press.evaluate(url=FEED, shape="[aria-expanded]")
    assert "reading" not in pre and "scope" not in pre, pre


# ---------------------------------------------------------------------------
# 3. THE SCOPE NARROWS WHERE THE CONTROL IS LOOKED FOR, AND ONLY THAT
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_scope_looks_for_the_shape_only_inside_its_container():
    page = Page()
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_steady, scope="main"
    )
    clicks = [e for e in page.events if e[0] == "click"]
    selector = press.press_scope("main")["selector"]
    assert clicks == [("click", (selector, "[aria-expanded]"))], clicks
    assert verdict.get("permitted") is True, verdict


@pytest.mark.asyncio
async def test_a_scope_with_no_candidate_is_absent_and_nothing_is_pressed():
    page = Page(scoped_count=0, page_count=9)
    verdict = await press.disclose(
        page, shape="[aria-expanded]", read_counters=_steady, scope="main"
    )
    assert verdict["refused"] == "shape_absent_on_this_page", verdict
    assert not [e for e in page.events if e[0] in ("click", "key")], page.events


@pytest.mark.asyncio
async def test_the_scope_never_narrows_what_the_witness_counts():
    """The witness is PAGE-WIDE by design -- a dialog opened elsewhere on the
    page is still a disclosure -- and a scope must not quietly change that."""
    page = Page()
    await press.disclose(
        page, shape="[aria-expanded]", read_counters=_steady, scope="main"
    )
    witness_selectors = set(dict(press.WITNESS_SELECTORS).values())
    seen = {
        chain for kind, chain in page.events if kind == "locator" and len(chain) == 1
    }
    assert {(s,) for s in witness_selectors} <= seen, seen


def test_the_pre_press_permit_echoes_the_keys_it_was_asked_for():
    pre = press.evaluate(
        url=FEED, shape="[aria-expanded]", reading=SHARE, scope="main"
    )
    assert pre["permitted_to_attempt"] is True, pre
    assert pre["reading"] == SHARE and pre["scope"] == "main", pre
