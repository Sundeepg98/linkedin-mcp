"""No TOOL's FAILURE ENVELOPE may carry a page string. Driven, not read.

## THE GAP THIS EXISTS FOR, MEASURED BEFORE IT WAS WRITTEN

``tests/test_readers_emit_no_page_string.py`` holds the same property and is
the instrument this one is modelled on. Its subject set is DISCOVERED as
*every module-level* ``async def`` *with a* ``page`` *parameter*, which is
**119 of the 591 module-level functions in this package**. The remainder is
not a rounding error, and one part of it is the part that matters:

    server.py module-level functions            86
      async with a `page` parameter              6   <- the reader guard's
      async WITHOUT a `page` parameter          52
      plain `def`                               28
    of those 52, decorated with `mcp.tool`      49
    of those 49, calling `_error(`              48

**THE 48 TOOL BODIES THAT FUNNEL INTO** ``server._error`` **ARE OUTSIDE THAT
GUARD AND ALWAYS WILL BE**, because it only ever discovers ``async def``
functions that take a page -- and ``_error`` itself is a plain ``def``,
doubly outside. The reader guard's own docstring names ``server._error`` as
the place a laundered exception reaches a caller. Nothing was driving it.

So this file drives the OTHER end of the same pipe: the tool, from its
arguments to its returned envelope, with a page that answers in strings.

## WHY THE ENVELOPE AND NOT THE RAISE

``server._error`` receives an ``Exception`` and can read exactly two things
from it -- ``type(exc)`` and ``str(exc)``. Whether the text it quotes came
from a page is NOT among them: ``int("<a label from the page>")`` raises a
STDLIB ``ValueError``, indistinguishable at the envelope from
``int(None)``. The provenance question is answerable at the RAISE and
unanswerable at the envelope, which is why this guard is driven from the
outside and asks what came OUT, rather than asking ``_error`` to classify
what went in.

    A POLICY AT THE ENVELOPE IS UNIFORM ACROSS EVERY PROVENANCE CLASS,
    BECAUSE THE ENVELOPE CANNOT SEE PROVENANCE.

## THE FOUR VERDICTS, AND THE ASYMMETRY THAT MAKES THEM HONEST

``clean``        driven, the page answered in plants, no plant came out.
``returns_text`` the plant came back on a SUCCESS payload only. A SEPARATE
                 FINDING AND DELIBERATELY NOT A FAILURE -- a tool whose
                 contract is to return what a page says is doing its job, and
                 whether that string may be published is the SHAPERS'
                 question (``shape.py``, ``menus.py``, the redaction tests).
``leaks``        the plant reached a FAILURE envelope -- one carrying an
                 ``error`` key -- or any string in the payload carries a
                 coercion-failure signature. **UNCONDITIONAL FAILURE.**
``not_driven``   the tool never read the page, or the harness could not build
                 its call. **NEVER A PASS**, and counted so that a shrinking
                 driven set is visible rather than silent.

The asymmetry is the reader guard's, restated for the envelope:

    RETURNING PAGE TEXT CAN BE A CONTRACT.
    PUTTING PAGE TEXT IN A FAILURE MESSAGE IS NOBODY'S CONTRACT.

## HOW "DRIVEN" IS PROVEN RATHER THAN ASSUMED

A tool that dies on its first line returns a tidy envelope with no plant in
it, which looks exactly like a pass. So the page counts its own
page-controlled reads, and a drive with ZERO of them is ``not_driven`` with
that reason. A guard may not claim more than it ran.

## WHAT THIS DOES NOT COVER, SAID OUT LOUD

* It drives each tool with its REQUIRED arguments only, by type. A tool whose
  leak needs a particular optional argument is not reached.
* ``PlantedPage`` has no ``context`` and no ``request``, so every tool that
  begins with a cookie read or a voyager call is ``not_driven``. That is the
  honest verdict and not a pass.
* It hunts ONE plant. A page string this harness does not emit is invisible.
* It says nothing about what a THIRD PARTY puts in its own exception text.
  That channel is real, is measured in
  ``_audit/2026-09-21-what-the-browser-said.md``, and is a different subject:
  no needle this package controls travels it.

Shown failing by ``scripts/_check_the_tool_envelope_guard_can_fail.py``, on
the coercion that actually shipped.
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Callable, Optional

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import cdp_bridge as cdp_bridge_module
from linkedin_server import server as server_module
from tests.plantedpage import (
    COERCION_FAILURE_SIGNATURES,
    PLANT,
    SYNTHETIC_ARGUMENT,
    NavigationAttempted,
    PlantedPage,
    carries_the_plant_outside_records,
    text_paths_a_baseline_may_not_record,
    text_ratchet,
)

REPO = Path(__file__).resolve().parents[1]
SERVER_SOURCE = REPO / "linkedin_server" / "server.py"

#: The committed verdict for every discovered tool. See the docstring: this is
#: the half that makes a shrinking driven set visible.
BASELINE_PATH = REPO / "tests" / "tool_envelope_baseline.json"

#: Long enough for a tool doing real work, short enough to stay inside an
#: ordinary run. A tool that exceeds it is NOT-DRIVEN with that reason.
DRIVE_TIMEOUT_S = 10.0

CLEAN = "clean"
LEAKS = "leaks"
RETURNS_TEXT = "returns_text"
NOT_DRIVEN = "not_driven"
#: THE DECLARED CHANNEL (2026-09-24, NAMES-AT-RUNTIME applied by
#: PEOPLE-DATA-MITIGATIONS): the plant reached a SUCCESS payload and ONLY
#: inside ``linkedin_server.people_data`` records. ``returns_text`` is since
#: then a legacy inventory that may shrink and may not grow (the ratchet in
#: ``test_the_driven_set_has_not_silently_shrunk``); ``leaks`` is unchanged and
#: walks records too -- a record in an ``_error`` envelope is a leak.
RETURNS_RECORDS = "returns_records"

#: A landing this package already navigates to, carrying no identifier. The
#: fake ``goto`` answers with the target it was handed, so a tool's own
#: authwall gate sees the address the tool asked for.
SAFE_LANDING = "https://www.linkedin.com/feed/"

#: THE ONE DOOR INTO THE TEXT INVENTORY, AND IT IS NARROW (2026-11-26, the
#: orchestrator's ruling HIS-OWN-TEXT-AT-RUNTIME, answering lane
#: readers-jobs26's question 2): a tool may return text HE authored or uploaded
#: on his OWN account -- his stored resume file names, his job alerts' query
#: words -- to his own session at runtime. Fixtures carry synthetic stand-ins;
#: tracked files, tests, CI and console never hold the real values.
#:
#: NARROW IN THREE WAYS, each held by a test below: a tool enters only BY NAME,
#: with the page it reads and the fields it returns; its one reason is
#: :data:`HIS_OWN_AUTHORED`, so an aggregate or a third party's words cannot be
#: filed here; and no tool in ``people_data.PEOPLE_TOOLS`` -- the tools whose
#: answer is OTHER members' words -- may hold the door, so third-party text keeps
#: its one channel, the record.
HIS_OWN_AUTHORED = "text he authored or uploaded on his own account"
ADMITTED_OWN_TEXT: dict[str, tuple[str, str]] = {
    "linkedin_application_settings": (
        HIS_OWN_AUTHORED,
        "/jobs/application-settings/: each stored resume's file name, which he uploaded",
    ),
    # 2026-11-26, lane build-jobs2 (census J 37): the ruling's second example,
    # "his job-alert keywords".
    "linkedin_job_alerts": (
        HIS_OWN_AUTHORED,
        "/jobs/jam/: each job alert's search_keywords, the query he typed",
    ),
    # 2026-11-26 (lane build-net2, census N 95, SEARCH-BOX-TYPEAHEAD-DISCLOSURE,
    # which names this ruling): his own search box's recent searches.
    "linkedin_recent_searches": (
        HIS_OWN_AUTHORED,
        "/feed/, its search box's recent-searches group: each recent search's keywords, which he typed",
    ),
}


def _error_kinds() -> frozenset[str]:
    """Every value ``server._error`` can put in ``error``. Discovered, not listed.

    ``_error`` writes ``exc.kind`` for a package error and the literal
    ``unexpected`` for anything else, so the vocabulary is the ``kind``
    attribute of every :class:`LinkedInReaderError` subclass. Walking the
    subclasses means an exception class added tomorrow is recognised here with
    no edit, which is the same discipline as discovering the subject set.
    """
    from linkedin_server.errors import LinkedInReaderError

    kinds = {"unexpected", LinkedInReaderError.kind}
    pending = [LinkedInReaderError]
    while pending:
        cls = pending.pop()
        for sub in cls.__subclasses__():
            kinds.add(getattr(sub, "kind", "error"))
            pending.append(sub)
    return frozenset(kinds)


#: WHY THIS IS NARROWER THAN "AN ENVELOPE WITH AN ``error`` KEY", AND THE
#: NARROWING IS A CORRECTION AGAINST THIS FILE'S FIRST DRAFT.
#:
#: The first version called any envelope carrying ``error`` a failure envelope,
#: and convicted ``linkedin_newsletter_subscriptions`` for publishing
#: ``badge_before.saw.shaped_label`` in a refusal. That is not this class. A
#: refusal built by ``_badge_refusal`` is a RETURN VALUE that deliberately says
#: what it saw -- the standing rule that a refusal naming only what it did NOT
#: match is half a measurement -- and the SAME field is published on the
#: success path of ``linkedin_connections``. Convicting it would convict the
#: repository's own contract, which is the reflexive wrap the standing
#: fourteen-row ruling forbids.
#:
#:     A REFUSAL THAT NAMES WHAT IT SAW IS A CONTRACT.
#:     AN EXCEPTION'S TEXT REACHING A CALLER IS NOBODY'S CONTRACT.
#:
#: So the strict class is text that arrived through ``server._error``, whose
#: envelope is identifiable by a CLOSED VOCABULARY rather than by one key.
ERROR_KINDS = _error_kinds()


# ---------------------------------------------------------------------------
# 1. Discovery -- a tool added tomorrow is in the subject set
# ---------------------------------------------------------------------------


def discover_tools() -> list[tuple[str, Callable[..., Any]]]:
    """Every ``mcp.tool``-decorated coroutine in ``linkedin_server.server``.

    Discovered from the SOURCE rather than from the FastMCP registry, for the
    same reason the reader guard walks the package: a registry can be swapped,
    renamed or wrapped, and the question this guard asks is about the functions
    this module declares as tools.
    """
    tree = ast.parse(SERVER_SOURCE.read_text(encoding="utf-8"))
    found: list[tuple[str, Callable[..., Any]]] = []
    for node in tree.body:
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        decorated = any(
            "mcp.tool" in ast.unparse(dec) for dec in node.decorator_list
        )
        if not decorated:
            continue
        fn = getattr(server_module, node.name, None)
        if fn is None or not callable(fn):
            continue
        found.append((node.name, fn))
    return sorted(found, key=lambda row: row[0])


# ---------------------------------------------------------------------------
# 2. The page, counting its own reads
# ---------------------------------------------------------------------------


class CountingPlantedPage(PlantedPage):
    """``PlantedPage``, plus a tally of how often the page was actually read.

    Zero reads is the difference between "this tool published nothing" and
    "this tool never got as far as the page", and only the second is a reason
    to withhold a verdict.
    """

    def __init__(self) -> None:
        super().__init__()
        self.page_reads = 0

    def _count(self) -> None:
        self.page_reads += 1

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any):
        self._count()
        return await super().evaluate(script, arg, **kwargs)

    async def evaluate_handle(self, script: Any, arg: Any = None):
        self._count()
        return await super().evaluate_handle(script, arg)

    async def eval_on_selector(self, *args: Any, **kwargs: Any):
        self._count()
        return await super().eval_on_selector(*args, **kwargs)

    async def eval_on_selector_all(self, *args: Any, **kwargs: Any):
        self._count()
        return await super().eval_on_selector_all(*args, **kwargs)

    async def content(self):
        self._count()
        return await super().content()

    async def title(self):
        self._count()
        return await super().title()

    async def inner_text(self, *args: Any, **kwargs: Any):
        self._count()
        return await super().inner_text(*args, **kwargs)

    async def text_content(self, *args: Any, **kwargs: Any):
        self._count()
        return await super().text_content(*args, **kwargs)

    def locator(self, *args: Any, **kwargs: Any):
        self._count()
        return super().locator(*args, **kwargs)

    def get_by_role(self, *args: Any, **kwargs: Any):
        self._count()
        return super().get_by_role(*args, **kwargs)

    def get_by_text(self, *args: Any, **kwargs: Any):
        self._count()
        return super().get_by_text(*args, **kwargs)


# ---------------------------------------------------------------------------
# 3. Building a call -- required parameters only, by type
# ---------------------------------------------------------------------------


def build_call(fn: Callable[..., Any]) -> Optional[dict[str, Any]]:
    """Arguments for a tool's REQUIRED parameters, or None if it cannot be built.

    THE PLANT IS NEVER THE ARGUMENT. Every value here is
    :data:`SYNTHETIC_ARGUMENT` or a number, and neither equals :data:`PLANT` --
    hunting a value this harness supplied would convict every echoing tool and
    prove nothing.
    """
    try:
        signature = inspect.signature(fn)
    except (TypeError, ValueError):
        return None
    kwargs: dict[str, Any] = {}
    for name, param in signature.parameters.items():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.default is not param.empty:
            continue
        annotation = param.annotation
        text = ast.unparse(annotation) if isinstance(annotation, ast.AST) else str(annotation)
        if "int" in text and "str" not in text:
            kwargs[name] = 1
        elif "bool" in text:
            kwargs[name] = False
        elif "str" in text or annotation is param.empty:
            kwargs[name] = SYNTHETIC_ARGUMENT
        else:
            return None
    return kwargs


# ---------------------------------------------------------------------------
# 4. The hunt -- positions, never values
# ---------------------------------------------------------------------------


#: What a path segment is spelled as when the KEY ITSELF is a page string.
#: FOUND BY RUNNING THIS GUARD, NOT BY REVIEWING IT: `linkedin_search_appearances`
#: returns `view_name_counts` keyed BY THE NAME, so the plant arrived inside a
#: JSON PATH -- and a path is the one thing this file prints. An instrument that
#: reports positions must not smuggle the value out through the position.
PAGE_CHOSEN_KEY = "<key the page chose>"


def _segment(key: Any) -> str:
    text = str(key)
    return PAGE_CHOSEN_KEY if PLANT in text else text


def _walk(obj: Any, path: str = "$"):
    yield path, obj
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _walk(value, "%s.%s" % (path, _segment(key)))
    elif isinstance(obj, (list, tuple)):
        for index, value in enumerate(obj):
            yield from _walk(value, "%s[%d]" % (path, index))
    elif isinstance(obj, (set, frozenset)):
        # A SET IS PUBLISHED AS A LIST, so it is walked as one -- in a stable
        # order, so a position names the same member on every run. It was not
        # walked at all until lane G's cold verification (2026-09-27) put a
        # plant in one and this guard called an _error envelope clean.
        for index, value in enumerate(sorted(obj, key=repr)):
            yield from _walk(value, "%s[%d]" % (path, index))


def plant_positions(obj: Any) -> list[str]:
    """Where the plant sits, as JSON paths. Closed vocabulary; no values.

    A PLANT CAN ARRIVE AS A KEY AND NOT AS A VALUE, which a value-only hunt
    cannot see -- a dict keyed by what the page said carries the page string
    with every value in it untouched. Both are searched.
    """
    hits = set()
    for path, value in _walk(obj):
        if isinstance(value, str) and PLANT in value:
            hits.add(path)
        elif not isinstance(value, _WALKED_OR_INERT) and PLANT in repr(value):
            # AN OBJECT IS PUBLISHED BY ITS FIELDS, so its repr is searched:
            # a people record INSTANCE -- published without its marker --
            # was invisible here until lane G's cold verification (2026-09-27).
            hits.add(path + "(repr)")
        if isinstance(value, dict):
            for key in value:
                if isinstance(key, str) and PLANT in key:
                    hits.add("%s.%s" % (path, PAGE_CHOSEN_KEY))
    return sorted(hits)


#: What ``_walk`` descends into, and leaves that cannot hold page text.
_WALKED_OR_INERT = (dict, list, tuple, set, frozenset, str, bytes, int, float, bool, type(None))


def coercion_signatures(obj: Any) -> list[str]:
    """Where a FAILED COERCION's own wording sits. Its presence is the leak."""
    return sorted(
        path
        for path, value in _walk(obj)
        if isinstance(value, str)
        and any(sig in value for sig in COERCION_FAILURE_SIGNATURES)
    )


def _is_error_envelope(obj: Any) -> bool:
    """Did ``server._error`` build this? Answered on its closed vocabulary."""
    return (
        isinstance(obj, dict)
        and obj.get("error") in ERROR_KINDS
        and "message" in obj
    )


# ---------------------------------------------------------------------------
# 5. The drive
# ---------------------------------------------------------------------------


def drive_tool(name: str, fn: Callable[..., Any]) -> dict[str, Any]:
    """One tool, one planted page, one verdict. Never raises."""
    kwargs = build_call(fn)
    if kwargs is None:
        return {
            "tool": name,
            "verdict": NOT_DRIVEN,
            "reason": "the harness could not build a call",
            "at": [],
        }

    page = CountingPlantedPage()
    navigations: list[str] = []

    @asynccontextmanager
    async def fake_session(*args: Any, **more: Any):
        yield page

    async def fake_goto(target_page: Any, url: str, **more: Any) -> str:
        # NEVER ``page.goto`` -- PlantedPage refuses it loudly, and this
        # harness is not measuring whether a tool navigates.
        navigations.append(url)
        return url

    def closed_cdp_port() -> str:
        # NEVER THE CDP PORT. ``linkedin_cdp_status`` probes
        # http://127.0.0.1:<CDP_PORT>/json/version with urllib, where the live
        # lane's Chrome listens, and this harness drove it live: one connection
        # per run, measured 2026-09-28 (lane S). The probe answers here as a
        # closed port does. ``tests/cdp_port_guard.py`` refuses the next one.
        raise ConnectionRefusedError("the envelope harness does not probe the CDP port")

    original_session = browser_module.BROWSER.session
    original_goto = browser_module.BROWSER.goto
    original_read_version = cdp_bridge_module._read_version
    browser_module.BROWSER.session = fake_session
    browser_module.BROWSER.goto = fake_goto
    cdp_bridge_module._read_version = closed_cdp_port
    try:
        out = asyncio.run(asyncio.wait_for(fn(**kwargs), DRIVE_TIMEOUT_S))
        raised = None
    except NavigationAttempted as exc:
        out, raised = None, "NavigationAttempted: %s" % exc
    except asyncio.TimeoutError:
        out, raised = None, "timed out after %.0fs" % DRIVE_TIMEOUT_S
    except Exception as exc:  # noqa: BLE001
        # A tool that lets an exception escape is a finding of its own, but it
        # is not THIS guard's finding: nothing was published.
        out, raised = None, type(exc).__name__
    finally:
        browser_module.BROWSER.session = original_session
        browser_module.BROWSER.goto = original_goto
        cdp_bridge_module._read_version = original_read_version

    if raised is not None:
        return {
            "tool": name,
            "verdict": NOT_DRIVEN,
            "reason": "did not return an envelope (%s)" % raised,
            "at": [],
            "page_reads": page.page_reads,
        }
    if page.page_reads == 0:
        return {
            "tool": name,
            "verdict": NOT_DRIVEN,
            "reason": "never read the page",
            "at": [],
            "page_reads": 0,
        }

    verdict, reason, positions = classify_envelope(out)
    return {
        "tool": name,
        "verdict": verdict,
        "reason": reason,
        "at": positions,
        "page_reads": page.page_reads,
        "navigations": len(navigations),
    }


def classify_envelope(out: Any) -> tuple[str, str, list[str]]:
    """``(verdict, reason, positions)`` for one returned envelope.

    A pure function of the envelope, so the controls drive the code the guard
    runs. POSITIONS COME FROM THE PLAIN WALK, records included: a person record
    in a failure envelope is a leak like any page string in one. Only a SUCCESS
    payload asks where the plant sits relative to the records, and it asks for
    a COUNT, never a path -- a record-aware path could spell a key the page
    chose, and positions are the one thing this file prints.
    """
    positions = plant_positions(out)
    signatures = coercion_signatures(out)
    if signatures:
        return (
            LEAKS,
            "a coercion-failure message reached the output",
            sorted(set(positions) | set(signatures)),
        )
    if positions and _is_error_envelope(out):
        return LEAKS, "the plant reached the _error envelope", positions
    if positions:
        outside, records = carries_the_plant_outside_records(out)
        if not outside:
            return (
                RETURNS_RECORDS,
                "the plant reached a published payload only inside %d people record(s)"
                % records,
                positions,
            )
        return RETURNS_TEXT, "the plant reached a published payload", positions
    return CLEAN, "", positions


def sandbox_session_store(directory: Any) -> None:
    """Point the session store at a throwaway path. CALLED OUTSIDE PYTEST ONLY.

    Under pytest, ``conftest._never_write_the_real_session_store`` already does
    this for every test, autouse, because it ALREADY HAPPENED ONCE: the suite
    wrote a seven-character fake credential into the operator's live state
    directory. This module also runs standalone -- ``--report``,
    ``--write-baseline``, and the can-fail control -- where no fixture applies,
    and it drives ``linkedin_login``, whose ``login_via_browser`` harvests
    cookies into that very store.

    It is unreachable today because ``PlantedPage.context`` is ``None`` and the
    harvest dies first. THAT IS AN ACCIDENT OF THE DOUBLE, NOT A GUARANTEE, and
    a safety property held by an accident is the shape this repository keeps
    paying for. So it is redirected rather than reasoned about, both bindings,
    exactly as the fixture does.
    """
    from linkedin_server import browser as module_browser
    from linkedin_server import session_store as module_store

    sandbox = Path(directory) / "session.json"
    module_store.SESSION_PATH = sandbox
    try:
        module_browser.SESSION_STORE.path = sandbox
    except AttributeError:  # pragma: no cover - shape changed, say so loudly
        raise SystemExit(
            "SESSION_STORE has no .path -- refusing to drive tools with the "
            "real session store reachable"
        )


def drive_all() -> list[dict[str, Any]]:
    return [drive_tool(name, fn) for name, fn in discover_tools()]


# ---------------------------------------------------------------------------
# 6. The guard
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def verdicts() -> list[dict[str, Any]]:
    return drive_all()


def test_no_tool_publishes_a_page_string_in_a_failure_envelope(verdicts):
    """The property. A leak is unconditional and has no exemption list."""
    leaking = [row for row in verdicts if row["verdict"] == LEAKS]
    assert not leaking, "\n".join(
        "%s -- %s at %s" % (row["tool"], row["reason"], ",".join(row["at"]))
        for row in leaking
    )


def test_the_driven_set_has_not_silently_shrunk(verdicts):
    """A tool that stops being driven is a coverage loss, and it must be loud."""
    if not BASELINE_PATH.exists():
        pytest.skip("no baseline yet -- write one with --write-baseline")
    committed = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["tools"]
    # THE STORED VALUE IS "verdict:reason", SO IT IS SPLIT RATHER THAN
    # COMPARED WHOLE. Found by this assertion firing on its own first baseline
    # and naming 27 tools as regressions on a tree nothing had changed -- a
    # guard whose first red is its own bug is the cheapest kind to find, and
    # `tests/reader_leak_baseline.json` splits on the first colon for the same
    # reason.
    recorded = {k: v.split(":", 1)[0].strip() for k, v in committed.items()}
    live = {row["tool"]: row["verdict"] for row in verdicts}

    appeared = sorted(set(live) - set(recorded))
    vanished = sorted(set(recorded) - set(live))
    assert not appeared, "new tools, unclassified: %s" % ", ".join(appeared)
    assert not vanished, "tools that vanished: %s" % ", ".join(vanished)

    regressed = sorted(
        name
        for name, verdict in live.items()
        if verdict == NOT_DRIVEN and recorded[name] != NOT_DRIVEN
    )
    assert not regressed, "these stopped being driven: %s" % ", ".join(regressed)
    # THE LEGACY TEXT INVENTORY MAY SHRINK AND MAY NOT GROW (2026-09-24).
    ratchet = text_ratchet(recorded, live, ADMITTED_OWN_TEXT)
    assert not ratchet, (
        "the page-text inventory moved: %s. A page string leaves only through a "
        "people_data record: a NEW text path must return records instead; a "
        "STALE entry means a tool stopped returning text and the baseline must "
        "be regenerated so the inventory shrinks; LOST RECORDS means a "
        "converted tool fell back." % "; ".join(ratchet)
    )


def test_the_own_text_door_admits_by_name_and_for_his_own_text_only():
    """HIS-OWN-TEXT-AT-RUNTIME's door, held narrow: each entry's reason is the
    one own-text reason and names the page and the fields; no people tool --
    whose answer is other members' words -- holds it."""
    from linkedin_server import people_data

    for tool, (reason, scope) in ADMITTED_OWN_TEXT.items():
        assert reason == HIS_OWN_AUTHORED, tool
        assert scope.startswith("/") and ": " in scope, tool
    assert not set(ADMITTED_OWN_TEXT) & set(people_data.PEOPLE_TOOLS)


def test_the_own_text_door_opens_for_its_tool_and_no_other():
    """RED FIRST, the door's control: the same new text path is refused for a
    tool the door does not name -- a third party's text arriving through any
    other tool stays a new text path -- and admitted for the one it names."""
    was = {"linkedin_application_settings": CLEAN, "linkedin_planted_third_party": CLEAN}
    now = {"linkedin_application_settings": RETURNS_TEXT, "linkedin_planted_third_party": RETURNS_TEXT}
    shut = text_ratchet(was, now)
    assert sorted(shut) == [
        "new text path: linkedin_application_settings (clean -> returns_text)",
        "new text path: linkedin_planted_third_party (clean -> returns_text)",
    ]
    opened = text_ratchet(was, now, ADMITTED_OWN_TEXT)
    assert opened == ["new text path: linkedin_planted_third_party (clean -> returns_text)"]
    assert text_paths_a_baseline_may_not_record(was, now, ADMITTED_OWN_TEXT) == [
        "linkedin_planted_third_party"
    ]


def records_outside_the_people_tools(rows: list[dict[str, Any]]) -> list[str]:
    """Tools called ``returns_records`` that are not declared people tools."""
    from linkedin_server import people_data

    return sorted(
        row["tool"]
        for row in rows
        if row["verdict"] == RETURNS_RECORDS and row["tool"] not in people_data.PEOPLE_TOOLS
    )


def test_only_a_declared_people_tool_returns_records(verdicts):
    """A RECORD IS THE DECLARED CHANNEL FOR THE DECLARED PEOPLE TOOLS AND NO ONE
    ELSE (lane G's cold verification, 2026-09-27). A dict shaped like an
    envelope passes ``as_record`` whoever built it, so any tool could wrap
    page text in one and be called ``returns_records``. Such a tool is refused
    here, and by the baseline writer, until it joins
    ``people_data.PEOPLE_TOOLS`` -- where the bounded-reader file, the
    instructions paragraph and the invariant drives then hold it."""
    strays = records_outside_the_people_tools(verdicts)
    assert not strays, (
        "returns people records without being a declared people tool: %s. "
        "Declare it in people_data.PEOPLE_TOOLS, or return no page text." % strays
    )


def test_that_people_tool_check_can_fail():
    rows = [
        {"tool": "linkedin_planted_roster", "verdict": RETURNS_RECORDS},
        {"tool": "linkedin_who_viewed_me", "verdict": RETURNS_RECORDS},
        {"tool": "linkedin_planted_clean", "verdict": CLEAN},
    ]
    assert records_outside_the_people_tools(rows) == ["linkedin_planted_roster"]


def write_baseline() -> dict[str, Any]:
    """Regenerate the committed verdicts.

    REFUSES to write a file containing a leak. A baseline that can record a
    permitted leak becomes a list of permitted leaks within one commit of
    somebody being in a hurry -- the reasoning ``tests/reader_leak_baseline.json``
    already carries, applied to a third class.
    """
    rows = drive_all()
    leaking = [row["tool"] for row in rows if row["verdict"] == LEAKS]
    if leaking:
        raise SystemExit(
            "refusing to write a baseline recording a leak: %s"
            % ", ".join(leaking)
        )
    committed: dict[str, str] = {}
    if BASELINE_PATH.exists():
        committed = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["tools"]
    new_text = text_paths_a_baseline_may_not_record(
        committed, {row["tool"]: row["verdict"] for row in rows}, ADMITTED_OWN_TEXT
    )
    if new_text:
        raise SystemExit(
            "refusing to write a baseline recording a NEW page-text path: %s. "
            "A page string leaves only through a linkedin_server.people_data "
            "record (2026-09-24)." % ", ".join(new_text)
        )
    strays = records_outside_the_people_tools(rows)
    if strays:
        raise SystemExit(
            "refusing to write a baseline recording people records from a tool "
            "that is not in people_data.PEOPLE_TOOLS: %s" % ", ".join(strays)
        )
    tools: dict[str, str] = {}
    for row in rows:
        tools[row["tool"]] = (
            row["verdict"]
            if not row.get("reason")
            else "%s:%s" % (row["verdict"], row["reason"])
        )
    out: dict[str, Any] = {
        "_comment": (
            "Verdict per mcp.tool in linkedin_server/server.py, driven against "
            "tests/plantedpage.py. 'clean' means the tool was DRIVEN and "
            "published nothing the page chose; 'returns_records' means a page "
            "string reached a published payload ONLY inside "
            "linkedin_server.people_data records, the declared channel; "
            "'returns_text' means a page string reached a published payload "
            "outside a record -- a legacy inventory since 2026-09-24 that may "
            "shrink and may not grow; 'not_driven:<reason>' means this offline "
            "harness could not reach it, which is never a pass. There is no "
            "verdict meaning 'this leaks' -- a baseline that could record one "
            "would become a list of permitted leaks. Regenerate with: "
            "python -m tests.test_tool_envelopes_emit_no_page_string --write-baseline"
        ),
        "tools": tools,
    }
    BASELINE_PATH.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return out


def _report() -> None:
    rows = drive_all()
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    print("tools discovered: %d" % len(rows))
    for verdict in (CLEAN, RETURNS_RECORDS, RETURNS_TEXT, LEAKS, NOT_DRIVEN):
        print("   %-14s %3d" % (verdict, counts.get(verdict, 0)))
    print()
    for row in sorted(rows, key=lambda r: (r["verdict"], r["tool"])):
        print(
            "%-12s %-42s %-46s %s"
            % (
                row["verdict"],
                row["tool"],
                row.get("reason", "")[:46],
                ",".join(row["at"]),
            )
        )


if __name__ == "__main__":  # pragma: no cover
    import sys
    import tempfile

    with tempfile.TemporaryDirectory() as _scratch:
        sandbox_session_store(_scratch)
        if "--write-baseline" in sys.argv:
            write_baseline()
            print("wrote %s" % BASELINE_PATH.name)
        else:
            _report()
