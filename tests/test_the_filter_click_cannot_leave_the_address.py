"""A gate that was DESCRIBED and never built, and the naive build is wrong.

``dom.activate_messaging_filter``'s docstring writes a consequence:

    *"If activating a pill turns out to move the page, that is a finding
    rather than a detail: it would mean the control does more than filter,
    and the read classification that permits this click would no longer
    hold."*

It measured exactly that, as ``navigated``, and **nothing anywhere read it**.
Found by the act-then-decide sweep in
``_audit/2026-09-21-refuse-before-the-click.md`` section 8, reported not fixed.

## THE PART THAT MAKES "RAISE ON navigated" THE WRONG FIX

``navigated`` is not dead. It is TRUE on the only live reading this repository
has ever recorded of this path. From the 2026-09-03 leak record, in
``_audit/2026-08-31-linkedin-perform.md`` section 106 and in the docstring of
``tests/test_a_thread_id_never_leaves_the_module.py``:

    thread_opened.landed_url   ".../messaging/thread/<THREAD-ID>/"   safe
    active_filter.url_before   the whole id                          RAW
    active_filter.url_after    the whole id, plus ?filter=inmail     RAW

``url_after`` is ``url_before`` with a query appended, so ``page.url !=
before`` was True. **A gate that raised on ``navigated`` would have refused
the only run that ever worked** -- its sole known firing would be a false
positive, which is the same defect wearing the opposite costume to the one
the sweep found. ``test_the_naive_gate_refuses_the_only_live_reading`` holds
that, so nobody re-derives the naive fix.

## WHAT THE PERMISSION ACTUALLY RESTS ON

``readonly.SANCTIONED_MUTATIONS``, on this entry, verbatim: *"A pill SENDS
NOTHING and CHANGES NOTHING on LinkedIn's servers; it alters which rows are
displayed. Counted by EFFECT rather than by verb ... a view filter is a
read."*

A query parameter appended to the SAME address is LinkedIn recording which
rows are displayed. That is the permitted effect, spelled in the url bar. It
does not touch the classification.

What does touch it is the browser ending up at a DIFFERENT ADDRESS: then the
control did more than filter the view in front of it, and the server is about
to read (``page.content()``) and return a page whose address the read
boundary never admitted -- ``readonly.py``'s own allowlist comment names that
gap, *"the landed url is never re-checked"*. So the class that is enforced is
PATH-OR-HOST movement, not string inequality.

## WHEN IT BECOMES KNOWABLE, STATED AND NOT HIDDEN

``after_the_act``. Where a pill takes the browser cannot be derived before
pressing it -- the pills carry no href (measured; that is why the click
exists at all). So this refusal CANNOT be hoisted to a zero-contact gate the
way ``press.py``'s condition-3 pair was, and these tests assert that one click
happened rather than pretending none did.

**It still gates something real.** The raise lands BEFORE the caller reads the
page: ``server.py``'s messaging tool calls this and only then reaches
``page.content()``, so a refusal here means the reading of an unadmitted page
is never taken and never returned. It refuses the READ, not the click; the
click is already spent and this file says so out loud.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from linkedin_server import dom, readonly
from linkedin_server.errors import WriteAttemptError

#: Fabricated, and shaped like the real thing for the same reason the sibling
#: file's is: a thread id starts with a digit, which is what the read
#: allowlist keys on. Nothing here is derived from a page.
FAKE_THREAD_ID = "2-INVENTEDTHREADIDzzz=="
FAKE_OTHER_THREAD_ID = "2-ADIFFERENTINVENTEDIDzz=="

THREAD_URL = f"https://www.linkedin.com/messaging/thread/{FAKE_THREAD_ID}/"
OTHER_THREAD_URL = (
    f"https://www.linkedin.com/messaging/thread/{FAKE_OTHER_THREAD_ID}/"
)

#: THE MEASURED LIVE SHAPE, 2026-09-03. The one reading that exists.
FILTERED_URL = THREAD_URL + "?filter=inmail"

#: A compose surface WITH A QUERY, which the read boundary refuses.
#:
#: THE BARE ROOT NEXT TO IT IS ADMITTED, and that is not a typo -- it is an
#: exact-equality exemption in ``readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS``,
#: added so the composer surface can be READ. Both facts are asserted below,
#: because together they are the argument for classifying movement instead of
#: re-checking the allowlist: **a pill that landed the browser on the composer
#: root would pass an allowlist re-check.** Only the movement class catches it.
COMPOSE_URL = "https://www.linkedin.com/messaging/compose/?context=pill"
COMPOSE_ROOT = "https://www.linkedin.com/messaging/compose/"

#: Where the refusal sits in the ``press.py`` vocabulary. Two permitted
#: classes and one refusing class, and the refusing one is honest about
#: costing a click.
WHEN_KNOWABLE: dict[str, str] = {
    "none": "not_a_refusal",
    "filter_state": "not_a_refusal",
    "left_the_address": "after_the_act",
}


class _Pills:
    """One pill. Clicking it moves the page's url, which is the whole point."""

    def __init__(self, page: "_Page", count: int = 1) -> None:
        self._page = page
        self._count = count

    async def count(self) -> int:
        return self._count

    @property
    def first(self):
        return self

    async def get_attribute(self, _name: str, timeout=None, **_kwargs) -> str:
        return "InMail"

    async def inner_text(self) -> str:
        return "InMail"

    async def click(self, **_kw) -> None:
        self._page.clicks += 1
        if self._page.url_after_click is not None:
            self._page.url = self._page.url_after_click


class _Page:
    """A page that RECORDS the click and moves where the test says it moves."""

    def __init__(self, url: str, url_after_click: str | None = None) -> None:
        self.url = url
        self.url_after_click = url_after_click
        self.clicks = 0
        self.content_reads = 0
        self._pills = _Pills(self)

    def get_by_role(self, *_a, **_kw):
        return self._pills

    async def wait_for_timeout(self, _ms: int) -> None:
        return None

    async def content(self) -> str:  # pragma: no cover - asserted NOT called
        self.content_reads += 1
        return "<html></html>"


# ---------------------------------------------------------------------------
# 1. THE RED. Today's code returns a dict here and the caller reads on.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_pill_that_opens_another_conversation_is_refused():
    """THE CASE THE DOCSTRING DESCRIBES AND THE CODE DID NOT ENFORCE.

    A filter that auto-selects the first conversation in the filtered list
    lands on a DIFFERENT thread. That is not a view filter: it opens a second
    person's conversation, which this tool prices as its single unavoidable
    cost and does not price twice. The address is still on the read
    allowlist -- asserted below -- so an allowlist re-check alone would wave
    it straight through. The class being refused is MOVEMENT, not
    inadmissibility.
    """
    page = _Page(THREAD_URL, url_after_click=OTHER_THREAD_URL)
    with pytest.raises(WriteAttemptError) as caught:
        await dom.activate_messaging_filter(page, "inmail")
    message = str(caught.value)
    assert "left_the_address" in message, message
    # The other thread IS admitted. A boundary re-check would not have caught
    # this, and that is why the enforced class is movement.
    assert readonly.is_read_url(OTHER_THREAD_URL) is True
    # HONEST ABOUT THE COST: exactly one click happened, and the refusal is
    # after it. There is no pre-press form of this question.
    assert page.clicks == 1, page.clicks
    assert page.content_reads == 0, "the page was read after a refusal"


@pytest.mark.asyncio
async def test_a_pill_that_lands_on_a_compose_surface_is_refused():
    """The same class, at its worst: off the read boundary entirely.

    Two independent reasons hold here and the test states both, because a
    refusal that only says one of them is how three readers in this package
    took a substring for the wall.

    AND THE THIRD ASSERTION IS THE INTERESTING ONE. The composer ROOT, one
    query string away, is ADMITTED for reading -- so the tempting cheaper
    repair (re-check ``is_read_url`` after the click) would have permitted a
    pill that opened the composer. Movement is the class that catches it;
    admissibility is not.
    """
    page = _Page(THREAD_URL, url_after_click=COMPOSE_URL)
    with pytest.raises(WriteAttemptError) as caught:
        await dom.activate_messaging_filter(page, "inmail")
    assert "left_the_address" in str(caught.value)
    assert readonly.is_read_url(COMPOSE_URL) is False
    assert readonly.is_read_url(COMPOSE_ROOT) is True, (
        "the composer root is no longer admitted for reading. That changes "
        "the argument in this test's docstring -- re-derive it rather than "
        "deleting this line."
    )
    assert page.clicks == 1, page.clicks


@pytest.mark.asyncio
async def test_a_refusal_carries_no_address_at_all():
    """A refusal is a place a url leaks from. Closed vocabulary only.

    The class name, the filter name (from a closed tuple) and prose. No url
    before, no url after, no thread id -- not even the redacted form, which
    would still say which surface he was on.
    """
    page = _Page(THREAD_URL, url_after_click=OTHER_THREAD_URL)
    with pytest.raises(WriteAttemptError) as caught:
        await dom.activate_messaging_filter(page, "inmail")
    message = str(caught.value)
    for forbidden in (
        FAKE_THREAD_ID,
        FAKE_OTHER_THREAD_ID,
        "linkedin.com",
        "https://",
        "/messaging/",
    ):
        assert forbidden not in message, (forbidden, message)


# ---------------------------------------------------------------------------
# 2. THE CASE THE NAIVE FIX WOULD HAVE BROKEN
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_only_live_reading_is_still_permitted():
    """``?filter=inmail`` appended to the same thread. MEASURED 2026-09-03.

    Permitted, reported, and ``navigated`` stays True because it is an honest
    string comparison. What changed is that a second field now says WHAT KIND
    of change it was.
    """
    page = _Page(THREAD_URL, url_after_click=FILTERED_URL)
    result = await dom.activate_messaging_filter(page, "inmail")
    assert result["activated"] is True, result
    assert result["navigated"] is True, result
    assert result["url_movement"] == "filter_state", result
    assert page.clicks == 1


@pytest.mark.asyncio
async def test_the_naive_gate_refuses_the_only_live_reading():
    """THE CONTROL ON THE OBVIOUS FIX, and it is the reason for this file.

    ``raise if navigated`` is what the docstring reads like an instruction to
    build. Run it against the one reading that has ever come off his account
    and it refuses. A gate whose only known firing is a false positive is not
    a gate; it is the act-then-decide defect inverted.
    """
    page = _Page(THREAD_URL, url_after_click=FILTERED_URL)
    result = await dom.activate_messaging_filter(page, "inmail")

    def _naive_gate(reading: dict) -> bool:
        """The fix that was not made, applied to the live shape."""
        return bool(reading["navigated"])

    assert _naive_gate(result) is True, (
        "the naive gate no longer fires on the measured live shape, so this "
        "control certifies nothing -- re-read the leak record before "
        "trusting it"
    )
    # And the shipped classification does not refuse it.
    assert result["url_movement"] in ("none", "filter_state"), result
    assert WHEN_KNOWABLE[result["url_movement"]] == "not_a_refusal"


# ---------------------------------------------------------------------------
# 3. THE CLASSIFIER ITSELF
# ---------------------------------------------------------------------------


def test_every_declared_class_is_reachable():
    """A class nothing can produce is a branch that cannot fire.

    Each of the three is produced from a real pair of urls, and the set of
    what the function CAN produce is compared with what it DECLARES.
    """
    produced = {
        dom.classify_filter_movement(THREAD_URL, THREAD_URL),
        dom.classify_filter_movement(THREAD_URL, FILTERED_URL),
        dom.classify_filter_movement(THREAD_URL, OTHER_THREAD_URL),
    }
    assert produced == set(dom.FILTER_MOVEMENT_CLASSES), produced
    assert dom.classify_filter_movement(THREAD_URL, THREAD_URL) == "none"
    assert dom.classify_filter_movement(THREAD_URL, FILTERED_URL) == "filter_state"
    assert (
        dom.classify_filter_movement(THREAD_URL, OTHER_THREAD_URL)
        == "left_the_address"
    )


def test_a_trailing_slash_is_not_a_departure():
    """The same page, spelled two ways, is not the control moving the page."""
    assert (
        dom.classify_filter_movement(THREAD_URL, THREAD_URL.rstrip("/"))
        == "filter_state"
    )


def test_a_host_change_is_a_departure():
    """Movement is not only about the path.

    A same-path url on another host is the shape an interstitial or a locale
    redirect takes, and it is refused for the same reason.
    """
    elsewhere = THREAD_URL.replace("www.linkedin.com", "www.example.invalid")
    assert dom.classify_filter_movement(THREAD_URL, elsewhere) == "left_the_address"


def test_an_unreadable_url_resolves_against_the_click():
    """Unmeasurable resolves AGAINST, which is this package's standing rule.

    No special branch exists for it -- an empty string simply has no path in
    common with a real address -- so this is a property of the comparison
    rather than a case somebody remembered.
    """
    assert dom.classify_filter_movement("", THREAD_URL) == "left_the_address"
    assert dom.classify_filter_movement(THREAD_URL, "") == "left_the_address"


def _returned_string_constants(function_name: str) -> set[str]:
    """Every string literal ``function_name`` can RETURN, read by AST.

    Not by grep. A class name is a returned constant, and a line-oriented
    scan cannot tell one from the same word in the prose above it -- the
    failure this repository already recorded in
    ``test_a_correction_is_findable_from_the_claim``.
    """
    tree = ast.parse(pathlib.Path(dom.__file__).read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != function_name:
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Return) or inner.value is None:
                continue
            value = inner.value
            assert isinstance(value, ast.Constant) and isinstance(value.value, str), (
                "a movement class is not a literal string. A COMPUTED CLASS "
                "CAN CARRY PAGE TEXT, and it also makes this inventory "
                "unreadable."
            )
            found.add(value.value)
    assert found, f"{function_name} was not found in dom.py"
    return found


def test_the_class_vocabulary_is_exactly_what_the_function_can_emit():
    """The mechanical half, so the tuple cannot drift from the code.

    A fourth class added in the function and not in the tuple fails here; so
    does a tuple entry nothing returns. Either one would leave a caller
    matching on a vocabulary that is not the real one.
    """
    emitted = _returned_string_constants("classify_filter_movement")
    assert emitted == set(dom.FILTER_MOVEMENT_CLASSES), {
        "emitted, not declared": sorted(emitted - set(dom.FILTER_MOVEMENT_CLASSES)),
        "declared, not emitted": sorted(set(dom.FILTER_MOVEMENT_CLASSES) - emitted),
    }


def test_every_class_is_classified_by_when_it_becomes_knowable():
    """A class nobody classified is the defect that shipped, one level up.

    The refusing class is ``after_the_act`` and is ALLOWED to be: where a
    pill lands is not derivable before pressing it, because the pills carry
    no href. That is a measured fact about the surface, not an excuse.
    """
    assert set(WHEN_KNOWABLE) == set(dom.FILTER_MOVEMENT_CLASSES), WHEN_KNOWABLE
    refusing = {
        name for name, when in WHEN_KNOWABLE.items() if when != "not_a_refusal"
    }
    assert refusing == {"left_the_address"}, refusing
    assert WHEN_KNOWABLE["left_the_address"] == "after_the_act"


# ---------------------------------------------------------------------------
# 4. THE CONSEQUENCE AT THE CALLER, ASSERTED STRUCTURALLY
# ---------------------------------------------------------------------------


def test_the_caller_reads_the_page_only_after_this_call():
    """WHY A POST-ACT RAISE IS STILL A GATE.

    The claim is that a refusal here means the unadmitted page is never read
    and never returned. That rests on ORDER in ``server.py``: the filter is
    activated, and only afterwards is ``page.content()`` taken. Asserted by
    AST over the caller rather than by a hand-written mirror of it -- a mirror
    drifts and then certifies nothing.

    ``server.py`` belongs to another wave; this test only READS it. If it
    goes red, the order changed and the enforcement claim in this file's
    docstring needs re-deriving rather than re-asserting.
    """
    tree = ast.parse(
        pathlib.Path(
            pathlib.Path(dom.__file__).parent / "server.py"
        ).read_text(encoding="utf-8")
    )
    callers = 0
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        activate_lines = [
            inner.lineno
            for inner in ast.walk(node)
            if isinstance(inner, ast.Call)
            and getattr(inner.func, "attr", None) == "activate_messaging_filter"
        ]
        if not activate_lines:
            continue
        callers += 1
        content_lines = [
            inner.lineno
            for inner in ast.walk(node)
            if isinstance(inner, ast.Call)
            and getattr(inner.func, "attr", None) == "content"
        ]
        assert content_lines, (
            f"{node.name} activates a filter and never reads the page. The "
            "enforcement argument assumed it did."
        )
        assert min(content_lines) > max(activate_lines), (
            f"{node.name} reads the page at line {min(content_lines)} before "
            f"the filter at line {max(activate_lines)}. A refusal from "
            "activate_messaging_filter no longer prevents the read."
        )
    assert callers == 1, (
        f"{callers} functions in server.py activate a messaging filter. This "
        "file's enforcement claim was derived for exactly one."
    )
