"""No reader in this package may carry a page string out, BY ANY PATH.

## THE PROPERTY, AND WHY THE OBVIOUS CHECK MISSES IT

``int()`` writes the value it refused verbatim into its own ``ValueError``::

    ValueError: invalid literal for int() with base 10: '<a label from the page>'

That exception leaves the reader, ``server._error`` catches it, and
``config.scrub`` substitutes THIS SERVER'S OWN PATHS and nothing else -- a
person's name has no shape to scrub, so it passes straight through into the
tool's error output.

    AN INTEGER-ONLY RETURN VALUE DOES NOT MAKE A FUNCTION INTEGER-ONLY,
    BECAUSE AN EXCEPTION IS NOT A RETURN VALUE.

Checking the return type is therefore not a check. This file drives the REAL
readers with a page that answers in strings and hunts the plant in the return
value **and in anything raised**.

## WHY THIS GUARD DISCOVERS ITS SUBJECTS INSTEAD OF LISTING THEM

This class has now been repaired three times at three sites -- ``search_results``
on 2026-09-20, then ``anchors`` and ``collections_page``. A guard that names the
readers it knows about catches the third instance and not the fourth, which is
the shape of every repair this repository keeps re-making.

So :func:`discover_readers` walks ``linkedin_server`` and takes every
module-level ``async def`` with a ``page`` parameter. **A reader added tomorrow
is in the subject set the moment it is written**, with no edit here.

## AND A GUARD MAY NOT CLAIM MORE THAN IT RAN

Not every reader can be driven offline: some navigate, some need an object this
harness cannot build. Those are **NOT-DRIVEN**, which is a third verdict and
never a pass. :data:`BASELINE_PATH` records the verdict for every discovered
reader, and :func:`test_the_driven_set_has_not_silently_shrunk` fails when a
reader that used to be driven stops being driven, when a new reader appears
unclassified, or when a known one vanishes.

**THAT FILE IS THE HALF NO DIFF-SCOPED GATE WOULD SELECT.** A change to
``dom.py`` that makes a reader start raising ``NavigationAttempted`` shrinks
this guard's coverage silently, and nothing in the diff says so; the committed
baseline is what turns that into a red.

## THE PLANT IS NEVER THE ARGUMENT

Readers that take a needle legally echo it back. The harness passes
``plantedpage.SYNTHETIC_ARGUMENT`` for required parameters and hunts
``plantedpage.PLANT``, and the two are never equal -- hunting a value the
harness itself supplied would convict every echoing reader and prove nothing.

Shown failing by ``scripts/_check_the_coercion_family_guard_can_fail.py``, on
the coercion that actually shipped, which is this repository's condition for a
check entering the register at all.
"""

from __future__ import annotations

import asyncio
import functools
import importlib
import inspect
import json
import logging
import pkgutil
import shutil
from pathlib import Path
from typing import Any, Callable, Optional

import pytest

import linkedin_server
from tests import shipped_drives
from tests.plantedpage import (
    PLANT,
    RAISED_PLANT,
    SYNTHETIC_ARGUMENT,
    NavigationAttempted,
    PlantedLibraryError,
    PlantedPage,
    RaisingLocator,
    RaisingPage,
    carries_a_laundered_exception,
    carries_the_plant,
    carries_the_plant_outside_records,
    carries_the_raised_plant,
    text_paths_a_baseline_may_not_record,
    text_ratchet,
)

REPO = Path(__file__).resolve().parents[1]

#: The committed verdict for every discovered reader. See the docstring: this
#: is the half that makes a shrinking driven-set visible.
BASELINE_PATH = REPO / "tests" / "reader_leak_baseline.json"

#: Long enough that a reader doing real work finishes, short enough that the
#: whole family stays inside an ordinary test run. A reader that exceeds it is
#: NOT-DRIVEN with that reason, never a pass.
DRIVE_TIMEOUT_S = 5.0

#: Verdicts. ``LEAKS`` is the only one that fails an individual reader.
#:
#: ``RETURNS_TEXT`` is a SEPARATE FINDING AND DELIBERATELY NOT A FAILURE.
#: ``dom.read_main_text`` returning the page's main text is its entire job, and
#: ``read_save_control`` returning a control's label is the reading a caller
#: asked for. Whether those strings may be published is the SHAPERS' question,
#: governed by ``shape.py``, ``menus.py`` and the redaction tests -- a different
#: subject with its own guards. Folding them in here would paint 22 readers red
#: for working correctly, and the response to a wall of red is to weaken the
#: guard, which is how this one would die.
#:
#: ``LEAKS`` needs no such judgement, and that asymmetry is the point:
#:
#:     RETURNING PAGE TEXT CAN BE A CONTRACT. RAISING A ``ValueError``
#:     THAT QUOTES PAGE TEXT IS NOBODY'S CONTRACT.
#:
#: So an exception carrying the plant is a leak unconditionally, with no
#: exemption list to be argued into -- and an exemption list is exactly how the
#: previous three instances of this class stayed open.
#:
#: **THE INVARIANT WAS REDESIGNED ON 2026-09-24 (NAMES-AT-RUNTIME, applied by
#: PEOPLE-DATA-MITIGATIONS; lane G's foundation), AND NOTHING ABOVE WAS
#: WEAKENED.** It was "no page string leaves, except by a contract the shapers
#: govern". It is now: A PAGE STRING LEAVES ONLY THROUGH A DECLARED PEOPLE
#: RECORD (``linkedin_server.people_data``), and NEVER through an exception, an
#: error field, a log record, a receipt, a cache or a fixture. So:
#:
#: * ``RETURNS_RECORDS`` -- the plant came back, and ONLY inside people
#:   records: the declared channel. Nothing else in the value carries it.
#: * ``RETURNS_TEXT`` -- the plant came back OUTSIDE a record. A LEGACY
#:   INVENTORY FROM THIS DATE: every reader recorded so in the baseline may
#:   stay so until it is converted, and none may join it --
#:   :func:`text_ratchet` refuses a new one, a stale one, and a record reader
#:   that fell back to text, and the baseline writer refuses to record one.
#: * ``LEAKS`` is untouched, and it is checked on the PLAIN walk: a record in
#:   an exception is a leak like any other page string in one. The failing-
#:   page family and the log capture below also walk records.
CLEAN = "clean"
LEAKS = "leaks"
RETURNS_TEXT = "returns_text"
RETURNS_RECORDS = "returns_records"

#: CLEAN IS EARNED, NOT DEFAULTED (2026-09-27, the orchestrator's order). A
#: drive that carried nothing out was recorded ``clean`` whether or not the
#: reader ever reached the code that reads a page: group_leave's five readers
#: refused their argument on the first line, ``named_profile``'s namer took
#: an early return, and both were ``clean`` having read nothing. Measured
#: that day over the 109 readers the baseline called clean: 13 returned
#: without one read of the page, and 10 more read it and returned only an
#: empty shape. So a clean drive must now show its success path ran -- the
#: page was READ (``PlantedPage.reads``) and something that is not an empty
#: shape came back (:func:`empty_shape`). A plant in the result already shows
#: both, so ``returns_records`` and ``returns_text`` need no more. Either
#: failure is a NOT-DRIVEN reason, never a pass, and the reader's other
#: variants still decide its verdict (:func:`_worst`).
#:
#: WHY NOT A NON-EMPTY RESULT ALONE: an early return is often a refusal with
#: a sentence in it. Ten of the thirteen no-read readers returned exactly that
#: -- ``{"refused": ..., "why": ...}`` -- which is not empty and read nothing.
NO_PAGE_READ = "not_driven:returned without reading the page"
EMPTY_RESULT = "not_driven:read the page and returned only an empty shape"

#: AND A PEOPLE READER'S SUCCESS PATH IS ITS RECORDS. Found at lane G's
#: merge of master 5354d42, on the reader the order named: lane S's
#: ``people_results.read_result_people`` read the planted page, skipped its one
#: card for want of a member link, and returned its denominators -- a read,
#: and a result that is not empty -- having built NO record. A reader whose
#: code reaches a people-record builder (:func:`record_readers`, the
#: bounded-reader guard's own derivation) has one success path, and on the
#: planted page it puts the plant inside a record; a drive of such a reader
#: that comes back clean did not take it.
NO_RECORD = "not_driven:reaches a people-record builder and built no record"

#: AND A REFUSAL IS NOT A SUCCESS PATH, EVEN AFTER A READ (2026-09-28, found
#: while triaging the readers the rule above left not driven). "A read and a
#: result that is not empty" let a reader through that read the planted page,
#: judged it wrong, and returned its refusal: measured that day, four readers
#: were recorded clean that way and no other way -- ``read_compose_fields``,
#: ``read_self_owned_editor_fields`` and ``_values``, ``read_premium_badge``
#: -- and every press reader driven as far as its click came back clean on
#: the ``press_failed`` its own handler made of the harness's refusal (that
#: refusal can no longer be caught: see ``plantedpage.NavigationAttempted``).
#:
#: WHAT IS READ IS THE FIELD, NOT THE WORD: a top-level ``refused`` that is
#: truthy and is not a TALLY (a mapping or a sequence of per-item counts, as
#: ``item_addresses`` and six other readers keep under that name). So
#: ``press_failed`` -- whose own sentence says a failure is not a refusal --
#: is caught with the refusals: it is under the same field, and it is not a
#: success either.
REFUSED_AFTER_READ = "not_driven:read the page and returned a refusal"

#: NOR IS A FAILURE (2026-09-28, the same triage). Three readers were recorded
#: clean on ``{"error": "AttributeError", ...}``: the planted locator lacked
#: Playwright's ``and_``/``or_``/``filter``, each reader's own handler caught
#: the ``AttributeError``, and what came back was a failure envelope with
#: counts in it -- read, not empty, not a refusal. The locator now answers
#: those three, and all three reach their readings; this rule is what makes
#: the next missing method a not-driven verdict instead of a clean one. The
#: same shape as the refusal rule: a top-level ``error`` that is truthy and
#: is not a tally.
ERRORED_AFTER_READ = "not_driven:read the page and returned an error"

#: The not-driven verdicts of a drive that DID read the page. When a reader's
#: variants are all not driven, one of these names the reader: it is the
#: variant that got furthest (:func:`_worst`).
READ_BUT_NOT_DRIVEN = (EMPTY_RESULT, NO_RECORD, REFUSED_AFTER_READ, ERRORED_AFTER_READ)

#: The prefix of a drive that reached an action the planted page refuses
#: (:class:`plantedpage.NavigationAttempted`): ``navigates (<which>)``.
NAVIGATES = "not_driven:navigates"


@functools.lru_cache(maxsize=1)
def record_readers() -> frozenset[str]:
    """Readers, as ``module:function``, whose code reaches a people-record
    builder -- derived by ``tests/test_a_people_reader_reads_one_page.py``'s
    own closure, stopped at the write door as it stops there."""
    from tests import test_a_people_reader_reads_one_page as bounded

    modules = bounded.package_modules()
    functions = bounded.module_functions(modules)
    edges = {key: bounded.references(fn) for key, fn in functions.items()}
    reach = bounded.closure(
        edges, bounded.record_builders(modules), stop=frozenset({bounded.WRITE_DOOR})
    )
    return frozenset(f"{module}:{name}" for module, name in reach)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _modules() -> list[Any]:
    out = []
    for info in pkgutil.iter_modules(linkedin_server.__path__):
        if info.name.startswith("__"):
            continue
        try:
            out.append(importlib.import_module(f"linkedin_server.{info.name}"))
        except Exception:  # noqa: BLE001 -- an unimportable module is its own bug
            continue
    return out


def discover_readers() -> list[tuple[str, Callable[..., Any]]]:
    """Every module-level ``async def`` in the package that takes a ``page``.

    Keyed ``module:function`` so the baseline is stable under reordering and a
    complaint names something a person can open. Sorted, so a diff of the
    baseline reads as a list of readers rather than a reshuffle.
    """
    found: dict[str, Callable[..., Any]] = {}
    for module in _modules():
        for name, fn in vars(module).items():
            if not inspect.iscoroutinefunction(fn):
                continue
            if getattr(fn, "__module__", None) != module.__name__:
                continue  # re-exported from elsewhere; measured at its home
            params = inspect.signature(fn).parameters
            if "page" not in params:
                continue
            found[f"{module.__name__.split('.')[-1]}:{name}"] = fn
    return sorted(found.items())


# ---------------------------------------------------------------------------
# Driving
# ---------------------------------------------------------------------------


def _argument_for(param: inspect.Parameter) -> tuple[bool, Any]:
    """A value for one required parameter, or ``(False, reason)``.

    Only the shapes this package's readers actually take. An unrecognised
    annotation is REFUSED rather than guessed: a guessed object that half-works
    sends the reader down an unusual branch, and the verdict would then be
    about that branch rather than about the reader.

    Annotations arrive as STRINGS here -- every module in this package carries
    ``from __future__ import annotations`` -- so this matches on text. A
    version of this function that matched on types silently refused every
    parameter in the package.
    """
    text = param.annotation
    if not isinstance(text, str):
        text = getattr(text, "__name__", str(text))
    text = text.strip()
    inner = text
    for wrapper in ("Optional[", "typing.Optional["):
        if inner.startswith(wrapper) and inner.endswith("]"):
            inner = inner[len(wrapper):-1].strip()
    base = inner.split("[", 1)[0].strip()

    if param.name == "page":
        return True, PlantedPage()
    # BEFORE the ``str`` branch below, and the order is the whole point. An
    # anchor is a CONTROL LABEL that ``perform`` derives with
    # ``anchor_label_for(spec, grant.target)``; there is no other source for
    # one. Measured: handing ``_live_control`` the generic synthetic string
    # instead leaves ``save_job`` and ``unsave_job`` raising
    # ``ExtractionFailedError`` before their readings -- two of thirteen
    # branches unmeasured, reported as driven because eleven others ran.
    if param.name == "anchor":
        return True, _Paired("anchor")
    # AND BEFORE ``str`` FOR THE SAME REASON. A ``url`` in this package is an
    # ALLOWLISTED READ ADDRESS: ``writes._load`` hands it to
    # ``readonly.assert_read_url`` as its first statement, which refuses the
    # generic synthetic string and raises ``WriteAttemptError``. The baseline
    # then recorded ``not_driven:raises WriteAttemptError`` against a reader
    # that had never run a line of its own -- a reason describing the HARNESS
    # while reading as though the write module had refused. With the server's
    # own feed constant the true reason appears: it navigates, which is an
    # offline harness's honest ceiling. Blast radius is one reader; ``_load``
    # is the only discovered reader with a ``url`` parameter.
    if param.name == "url":
        from linkedin_server import writes

        return True, writes.FEED_URL
    # AND BEFORE ``Any`` FOR THE SAME REASON (2026-09-27, lane G's merge of
    # master 7986ae3). ``identifier`` is lane L8's GROUP ID, the only reader
    # parameter by that name (group_leave's five), annotated ``Any``: the
    # harness handed it a page double, ``group_leave.disclosure_selector``
    # refused it as not 1 to 20 digits on the FIRST line of every try block,
    # and the five were recorded ``clean`` having read nothing. A five-digit id
    # -- under the identity guard's six-digit line -- reaches the page reads.
    if param.name == "identifier":
        return True, _GROUP_ID
    if param.annotation is inspect.Parameter.empty:
        # Unannotated. Every such parameter in this package is a selector or a
        # needle, and a string is the only thing that could be passed anyway.
        return True, SYNTHETIC_ARGUMENT
    if base in {"str", "AnyStr"}:
        return True, SYNTHETIC_ARGUMENT
    if base in {"int", "float"}:
        return True, 1000
    if base in {"bool"}:
        return True, False
    if base in {"list", "List", "Sequence", "Iterable", "tuple", "Tuple"}:
        return True, []
    if base in {"dict", "Dict", "Mapping"}:
        return True, {}
    if base in {"Callable"}:
        return True, None
    if base in {"Any", "typing.Any"}:
        return True, PlantedPage()
    if base in DOMAIN_OBJECTS:
        return True, _VARY  # expanded by _build_call into one call per value
    if base in PAIRED_OBJECTS:
        return True, _Paired(base)  # built from this variant's own WriteSpec
    return False, f"needs {param.name}: {text}"


#: A sentinel meaning "this parameter has several faithful values; run them
#: all". See :func:`_domain_values`.
_VARY = object()

#: The group id group_leave's readers are driven with: numeric, as
#: ``group_leave.checked_group_id`` requires, and five digits, under the
#: six-digit run ``tests/test_no_committed_identity.py`` refuses.
_GROUP_ID = "12345"


class _Paired:
    """A placeholder for a value DERIVED FROM THE VARIANT'S OWN ``WriteSpec``.

    Not a member of :data:`DOMAIN_OBJECTS`, because those are varied
    INDEPENDENTLY and these may not be. A ``WriteGrant`` is permission for ONE
    action: pairing ``save_job``'s grant with ``follow_company``'s spec is a
    state the server cannot be in, so a verdict taken there would be about a
    branch nobody wrote. It is also the difference between 13 variants and
    13 x 13 x 13 -- ``_verify_after`` takes a spec, a grant AND an
    observation.

    See :func:`_pair_with_spec` for the resolution, and ``tests/refusinggrant.py``
    for what each kind resolves to and why none of it authorises a write.
    """

    __slots__ = ("kind",)

    def __init__(self, kind: str) -> None:
        self.kind = kind


class _PairedObservation:
    """A paired ``Observation`` whose facts need the PAGE, so it waits.

    ``observe`` builds an Observation's facts by running a reader over a page.
    Reproducing that faithfully is an ``await``, and :func:`_build_call` is
    synchronous -- so this marker carries the spec out to :func:`_drive_once`,
    which resolves it inside the event loop it already owns.
    """

    __slots__ = ("spec",)

    def __init__(self, spec: Any) -> None:
        self.spec = spec


#: THE TYPES THIS HARNESS SUPPLIES FROM THE VARIANT'S SPEC, and it supplies
#: them because REFUSING THEM WAS MEASURING THE HARNESS'S OWN PLUMBING.
#:
#: This slot held ``GRANT_REFUSAL`` until 2026-09-21: five readers recorded
#: ``not_driven`` on the grounds that minting a grant is "policy, not
#: capability". Three measurements retired it, all in
#: ``_audit/2026-09-21-the-ungrantable-readers.md``:
#:
#: * ``_live_control``, ``_verify_after``, ``_typeahead_gate`` and
#:   ``_recipient_gate`` contain NO page action and NO grant door -- an AST
#:   walk finds zero ``click``/``fill``/``goto`` and zero
#:   ``consume``/``mint``/``assert_write_url``/``writes_enabled``. They read a
#:   page and return a verdict. The grant reaches them as two strings.
#: * ``tests/test_writes.py::_bare_grant`` has built one all along, with a
#:   docstring explaining why that is not a way round ``mint``.
#: * ``writes.Observation``'s own docstring says an Observation built by hand
#:   is INERT, because ``_record`` is the only writer of ``_OBSERVED``.
#:
#: WHAT THE REFUSAL WAS COSTING, counted with the repository's own census:
#: 22 of the 52 unguarded page-derived coercion sites
#: (``scripts/_census_page_coercions.py``) live inside those five readers, and
#: that census closes by naming THIS file as the thing that settles which of
#: them leak. It could not. One of them did.
#:
#: ``perform`` is still NOT-DRIVEN and its reason is now the true one: the
#: process-wide ``writes_enabled()`` door, which nothing here touches.
PAIRED_OBJECTS: frozenset[str] = frozenset({"WriteGrant", "Observation"})


def _domain_values(text: str) -> list[Any]:
    """Every SHIPPED value of a domain type, never a fabricated one.

    ALL of them, not one, and the reason is the false negative this whole file
    was written around. ``scripts/_check_the_shaper_leak_guard_can_fail.py``
    drove ``collections_page`` with a payload missing the one key that reader
    reads, and printed ``clean``. Picking a single ``WriteSpec`` would repeat
    that exactly: a reader whose surface does not match the chosen action
    returns early, never reaches its coercions, and reports clean for the same
    reason -- it was never driven.
    """
    from linkedin_server import writes

    if text == "WriteSpec":
        return [writes.SANCTIONED_WRITES[k] for k in sorted(writes.SANCTIONED_WRITES)]
    if text == "_TrackerStage":
        return [writes.SAVED_STAGE, writes.APPLIED_STAGE]
    return []


#: Domain types this harness supplies, and it supplies only values the SERVER
#: ITSELF ships. A fabricated spec would drive a branch nobody wrote.
DOMAIN_OBJECTS: frozenset[str] = frozenset({"WriteSpec", "_TrackerStage"})


def _build_call(
    fn: Callable[..., Any]
) -> tuple[Optional[list[tuple[list[Any], dict[str, Any]]]], str]:
    """Positional args and kwargs for one reader, or a refusal.

    KEYWORD-ONLY PARAMETERS GO IN KWARGS, and getting that wrong is not a
    cosmetic bug: passing ``harvest_census(page, href_pattern, max_items)``
    positionally raises ``TypeError: takes 1 positional argument but 3 were
    given``, which this harness would have recorded as NOT-DRIVEN. Five readers
    read as un-measurable for that reason alone on the first run, and a harness
    that quietly drops readers is the failure this guard exists to prevent one
    level down.
    """
    variants: list[tuple[list[Any], dict[str, Any]]] = [([], {})]
    optional: list[inspect.Parameter] = []
    for param in inspect.signature(fn).parameters.values():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.default is not inspect.Parameter.empty:
            optional.append(param)
            continue
        ok, value = _argument_for(param)
        if not ok:
            return None, str(value)
        text = param.annotation if isinstance(param.annotation, str) else ""
        choices = _domain_values(text.strip()) if value is _VARY else [value]
        if not choices:
            return None, f"no shipped value for {param.name}: {text}"
        grown: list[tuple[list[Any], dict[str, Any]]] = []
        for args, kwargs in variants:
            for choice in choices:
                if param.kind is param.KEYWORD_ONLY:
                    grown.append((list(args), {**kwargs, param.name: choice}))
                else:
                    grown.append(([*args, choice], dict(kwargs)))
        variants = grown
    return _pair_with_spec(variants + _with_optionals(variants, optional)), ""


def _pair_with_spec(
    variants: list[tuple[list[Any], dict[str, Any]]]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Resolve every :class:`_Paired` against the WriteSpec beside it.

    A variant that already holds a spec uses THAT ONE -- so a grant, an anchor
    and an observation in the same call all describe the same action, which is
    the only combination ``perform`` can ever assemble.

    A variant with no spec (``_typeahead_gate(page, grant)``,
    ``_recipient_gate(page, grant)``, ``perform(navigator, page, grant)``) is
    EXPANDED, one per sanctioned action, for the reason :func:`_domain_values`
    gives: a single chosen action would drive the branch that action takes and
    report the reader measured. Four of the thirteen reach
    ``_recipient_gate``'s coercions and nine return early -- and the four are
    the whole finding.
    """
    from linkedin_server import writes

    from tests import refusinggrant

    shipped = [writes.SANCTIONED_WRITES[k] for k in sorted(writes.SANCTIONED_WRITES)]
    out: list[tuple[list[Any], dict[str, Any]]] = []
    for args, kwargs in variants:
        supplied = [*args, *kwargs.values()]
        if not any(isinstance(value, _Paired) for value in supplied):
            out.append((args, kwargs))
            continue
        own = [v for v in supplied if isinstance(v, writes.WriteSpec)]
        for spec in own[:1] or shipped:
            resolved = {
                "WriteGrant": lambda s=spec: refusinggrant.grant_for(s),
                "anchor": lambda s=spec: refusinggrant.anchor_for(s),
                "Observation": lambda s=spec: _PairedObservation(s),
            }
            out.append(
                (
                    [
                        resolved[v.kind]() if isinstance(v, _Paired) else v
                        for v in args
                    ],
                    {
                        name: resolved[v.kind]() if isinstance(v, _Paired) else v
                        for name, v in kwargs.items()
                    },
                )
            )
    return out


async def resolve_paired_observations(
    args: list[Any], kwargs: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    """Turn every :class:`_PairedObservation` into a real, INERT Observation.

    Separate and public because it is the one resolution that needs a running
    loop and the page, and because ``scripts/_probe_dom_error_url_field.py``
    consumes :func:`_build_call`'s variants directly -- a caller that drives a
    reader taking an ``Observation`` has to run this first or it hands the
    reader a marker.
    """
    from tests import refusinggrant

    supplied = [*args, *kwargs.values()]
    pages = [v for v in supplied if isinstance(v, PlantedPage)]
    page = pages[0] if pages else PlantedPage()

    async def _one(value: Any) -> Any:
        if isinstance(value, _PairedObservation):
            return await refusinggrant.observation_for(page, value.spec)
        return value

    return (
        [await _one(v) for v in args],
        {name: await _one(v) for name, v in kwargs.items()},
    )


def _with_optionals(
    variants: list[tuple[list[Any], dict[str, Any]]],
    optional: list[inspect.Parameter],
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Extra call variants that SUPPLY the parameters that have defaults.

    ## THE FALSE CLEAN THIS EXISTS FOR, AND IT WAS IN THIS HARNESS

    ``dom.read_invitation_surface(page, needle=None, ...)`` opens with::

        wanted = "" if needle is None else str(needle).strip()
        if not wanted:
            out["controls"] = int(await page.locator(INVITE_CONTROL).count())
            return out

    Driven with defaults only, it takes that early return and **never reaches
    the three coercions below it**. It reported ``clean``. It was not measured.

    > **A DEFAULT IS A BRANCH, AND AN UNTAKEN BRANCH IS NOT A CLEAN ONE.**

    Same disease as the payload key nobody supplied and the ``dict()`` that
    copied past an override -- third instance in one wave, which is itself the
    argument for the discovery-based design: a harness that only exercises what
    its author remembered to exercise is a list of what its author remembered.

    ## LINEAR, NOT COMBINATORIAL

    One extra variant per base variant with EVERY supportable optional supplied,
    rather than the power set. A reader with four optionals would otherwise be
    sixteen variants, times thirteen ``WriteSpec``s. The all-supplied variant is
    what reaches the far side of an ``if not <optional>`` guard, which is the
    branch this is for; a reader whose coercions sit behind some other
    combination is a gap this names rather than closes.

    ``html`` is included deliberately. It is the documented CONTROL PATH of the
    shaped readers, so supplying it runs the real classifier against a detached
    container -- another live path, measured rather than assumed dead.
    """
    supplied: dict[str, Any] = {}
    for param in optional:
        ok, value = _argument_for(param)
        if ok and value is not _VARY:
            supplied[param.name] = value
    if not supplied:
        return []
    out: list[tuple[list[Any], dict[str, Any]]] = []
    for args, kwargs in variants:
        out.append((list(args), {**kwargs, **supplied}))
    return out


class _ConfirmsTheNamedProfile:
    """The planted page, read as the profile of ONE named person.

    ``dom.NAMED_PROFILE_JS`` answers a CONFIRMED identity -- a profile title,
    one topcard, its first heading matching the title, first degree -- and
    ``dom.READ_PROFILE_JS`` answers a title and a topcard whose name and
    headline ARE the plant. Every other read is the planted page's own, so a
    string the namer reads anywhere else is still the plant.

    ADDED AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27, the
    orchestrator's order). Driven by signature alone,
    ``named_profile.name_the_profile_target`` was handed an observation built
    off the planted page, whose identity reading is page strings and never a
    confirmed identity -- so it took its first-line early return, named
    nobody, and was recorded ``clean`` having read nothing: the false clean
    lane G found in group_leave's five readers, in one more reader.
    """

    def __init__(self, page: Any) -> None:
        self._page = page

    def __getattr__(self, name: str) -> Any:
        return getattr(self._page, name)

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> Any:
        from linkedin_server import dom

        if script == dom.NAMED_PROFILE_JS:
            return {
                "title_shape": "profile",
                "topcards": 1,
                "topcard_headings": 1,
                "heading_matches_title": True,
                "degree": "1st",
                "degree_tokens": 1,
            }
        if script == dom.READ_PROFILE_JS:
            return {
                "title": PLANT + " | LinkedIn",
                "sections": [
                    {
                        "heading": PLANT,
                        "lines": [PLANT, "Headline of " + PLANT],
                    }
                ],
            }
        return await self._page.evaluate(script, arg, **kwargs)


async def _name_the_profile_target_as_shipped(page: Any) -> Any:
    """The namer as a named act's preview calls it: on the page the preview
    confirmed, with the facts ``writes.observe`` records there --
    ``named_profile.profile_facts`` of that page's own reading, and the
    landing flag -- for a named act's spec and a segment of the caller's."""
    from linkedin_server import dom, named_profile, writes

    confirming = _ConfirmsTheNamedProfile(page)
    facts = named_profile.profile_facts(await dom.read_named_profile(confirming))
    facts["landed_on_the_named_profile"] = True
    spec = writes.spec_for_action("connect_from_profile")
    observation = writes.Observation(
        target=SYNTHETIC_ARGUMENT,
        target_kind=spec.target_kind,
        facts=facts,
        facts_url="",
        state=named_profile.CONNECT_FROM,
        state_why="",
        state_url="",
        same_page_as_action=True,
        receipt="",
        observed_at=float("-inf"),
    )
    return await named_profile.name_the_profile_target(
        confirming, spec, observation, {}, segment=SYNTHETIC_ARGUMENT
    )


async def _read_the_confirmed_profile_as_shipped(page: Any) -> Any:
    """The read he names (ruling NAMED-PROFILE-READ-BEHIND-A-GRANT,
    2026-09-28) as ``linkedin_read_named_profile`` calls it after its one
    load: on the page the load landed on, the landing being the address the
    server composed from the caller's segment -- so the landing veto passes
    and the reader reaches its identity reading, its record and its hint."""
    from linkedin_server import named_profile, readonly

    return await named_profile.read_the_confirmed_profile(
        _ConfirmsTheNamedProfile(page),
        segment=SYNTHETIC_ARGUMENT,
        landed=readonly.named_profile_url(SYNTHETIC_ARGUMENT),
    )


async def _read_the_confirmed_details_as_shipped(page: Any) -> Any:
    """One detail page of the profile he names (lane NP, ruling
    NAMED-PROFILE-DETAIL-PAGES, 2026-10-10) as ``linkedin_read_named_profile``
    calls it after its one load: a section of the closed vocabulary and the
    landing the server composed, so the landing veto passes and the reader
    reaches its counts."""
    from linkedin_server import named_details, readonly

    return await named_details.read_the_confirmed_details(
        page,
        segment=SYNTHETIC_ARGUMENT,
        section="interests",
        landed=readonly.named_profile_details_url(SYNTHETIC_ARGUMENT, "interests"),
    )


def _inert_observation(
    spec: Any, facts: dict[str, Any], target: Any = SYNTHETIC_ARGUMENT
) -> Any:
    """An Observation built by hand, which ``writes.Observation`` documents as
    INERT: only ``writes._record`` writes the observation store. ``target``
    is the argument by default; a namer that parses its observation's target
    (the invitation's, since 2026-09-27) is handed the canonical target the
    server would have observed instead."""
    from linkedin_server import writes

    return writes.Observation(
        target=target,
        target_kind=spec.target_kind,
        facts=facts,
        facts_url="",
        state="",
        state_why="",
        state_url="",
        same_page_as_action=True,
        receipt="",
        observed_at=float("-inf"),
    )


class _OneToOneConversation:
    """The planted page, read as a conversation with ONE other member: its
    active row carries no group marker. Every other read is the page's own."""

    def __init__(self, page: Any) -> None:
        self._page = page

    def __getattr__(self, name: str) -> Any:
        return getattr(self._page, name)

    def locator(self, selector: Any, *args: Any, **kwargs: Any) -> Any:
        from linkedin_server import threads

        from tests.plantedpage import MAX_DEPTH, PlantedLocator

        if selector == threads.ACTIVE_GROUP_SELECTOR:
            return PlantedLocator(MAX_DEPTH)  # counts zero
        return self._page.locator(selector, *args, **kwargs)


async def _name_the_reply_recipient_as_shipped(page: Any) -> Any:
    """The reply preview's namer as ``writes.preview`` calls it for a
    ``send_reply``: after an observation that landed on the named thread and
    counted its messages -- once on a page that reads as a GROUP (the planted
    page counts every marker) and once as a conversation with ONE member."""
    from linkedin_server import threads, writes

    spec = writes.spec_for_action("send_reply")
    facts = {"landed_on_the_named_thread": True, "events": 1}
    group = await threads.name_the_reply_recipient(
        page, spec, _inert_observation(spec, facts), {}
    )
    one = await threads.name_the_reply_recipient(
        _OneToOneConversation(page), spec, _inert_observation(spec, facts), {}
    )
    return {"group": group, "one_to_one": one}


class _AnswersTheInvitationRail:
    """The planted page, whose invitation rail holds ONE card linking to the
    observed profile -- its one control labelled, as LinkedIn labels it, with
    the plant's name.

    THE LINK AIM, SINCE LANE L5'S MERGE OF MASTER 64afa6c (2026-09-27). This
    answered ``dom.INVITE_NEEDLE_JS`` until that script left with the needle:
    the rail is read now by two LOCATOR COUNTS -- the controls, and the cards
    linking to the profile -- and the label off the one control. So this
    answers each count with one and the label with the plant, and every read
    goes through the planted page first, so it is still counted."""

    def __init__(self, page: Any) -> None:
        self._page = page

    def __getattr__(self, name: str) -> Any:
        return getattr(self._page, name)

    def locator(self, *args: Any, **kwargs: Any) -> Any:
        return _OneCardOnTheRail(self._page.locator(*args, **kwargs))


class _OneCardOnTheRail:
    """A located set the rail reader counts as ONE, labelled with the plant."""

    def __init__(self, located: Any) -> None:
        self._located = located

    def __getattr__(self, name: str) -> Any:
        return getattr(self._located, name)

    async def count(self) -> int:
        await self._located.count()  # the read, counted
        return 1

    @property
    def first(self) -> Any:
        return _OneCardOnTheRail(self._located.first)

    async def get_attribute(self, name: str, **kwargs: Any) -> Any:
        from linkedin_server import dom

        await self._located.get_attribute(name, **kwargs)  # the read, counted
        return "Invite " + PLANT + dom.INVITE_CONTROL_SUFFIX


async def _name_the_invitation_recipient_as_shipped(page: Any) -> Any:
    """The invitation preview's namer as ``writes.preview`` calls it: after an
    observation of the rail that counted one control, whose target is the
    profile LINK the server canonicalised (since 2026-09-27)."""
    from linkedin_server import writes
    from tests import refusinggrant

    spec = writes.spec_for_action("send_invitation")
    observation = _inert_observation(
        spec, {"controls": 1}, target=refusinggrant.synthetic_target(spec)
    )
    return await writes._name_the_invitation_recipient(
        _AnswersTheInvitationRail(page), spec, observation, {}
    )


#: READERS THE SIGNATURE PLUMBING CAN ONLY DRIVE INTO AN EARLY RETURN, each
#: with one more variant that reaches its page reads the way it ships. The
#: generic variants still run and the worst verdict of all of them is the
#: reader's, so this can only ADD a finding, never hide one.
#:
#: The two PREVIEW NAMERS joined 2026-09-27, when a clean verdict began to
#: need a read: driven by signature they took their first-line returns --
#: another action's spec, or no landing -- and were recorded clean having
#: named nobody, the class this file now refuses.
#:
#: THE REST JOINED 2026-09-28, from ``tests/shipped_drives.py``: the readers
#: that rule left not driven, each triaged -- driven to its success path over
#: a tracked fixture (``DRIVES``), or as far as a press the planted page
#: refuses (``TO_THE_PRESS``, recorded not driven, run so the reads before
#: the press are hunted). The four whose success path returns page text
#: outside a record were held until the orchestrator's ruling of 04:25 the
#: same day, and are driven now under :data:`ADMITTED_TEXT`.
AS_SHIPPED: dict[str, Callable[..., Any]] = {
    "named_profile:name_the_profile_target": _name_the_profile_target_as_shipped,
    # THE READ HE NAMES, 2026-09-28 (lane L5): driven by signature it is
    # handed a landing that is not the named profile, vetoes on its first
    # line and reads nothing -- so it is driven as the tool calls it.
    "named_profile:read_the_confirmed_profile": _read_the_confirmed_profile_as_shipped,
    # ONE DETAIL PAGE OF IT, 2026-10-10 (lane NP): driven by signature it is
    # handed a section off the vocabulary and raises before any read.
    "named_details:read_the_confirmed_details": _read_the_confirmed_details_as_shipped,
    "threads:name_the_reply_recipient": _name_the_reply_recipient_as_shipped,
    "writes:_name_the_invitation_recipient": _name_the_invitation_recipient_as_shipped,
    **shipped_drives.DRIVES,
    **shipped_drives.TO_THE_PRESS,
}

#: THE RULING, VERBATIM IN SUBSTANCE (the orchestrator, 2026-09-28 04:25):
#: PEOPLE-DATA-MITIGATIONS binds OTHER members' data; his own data is not
#: people data in that sense. So his own text is ADMITTED to the text
#: inventory, anything identifying another member leaves only as a people
#: record (the reader is converted), and an aggregate that identifies no one
#: is admitted. "Read each one's success-path output on its drive; do not
#: decide from the name."
HIS_OWN = "his own profile's data, not another member's"
AGGREGATE = "an aggregate that identifies no one"

#: READERS ADMITTED TO THE TEXT INVENTORY BY THAT RULING, each with its
#: reason, after its drive's output was read FIELD BY FIELD:
#:
#: * ``dom:read_profile_detail_entries`` -- ``entries`` (his skills, roles,
#:   schools: the first line of each of HIS cards), ``evidence`` (the lines
#:   under them: where he used a skill, his employers, his dates),
#:   ``endorsements`` (a bare count), ``observed`` and ``why`` (counts and
#:   this package's sentences). The one field that could name ANOTHER member
#:   -- an endorsement line, "Endorsed by <a member>" -- was CONVERTED the same
#:   day: such a line is counted and published nowhere
#:   (``dom._ENDORSEMENT_COUNT``; ``tests/test_sdui_surfaces_fixture.py::
#:   test_an_endorsement_line_that_names_a_member_leaves_as_a_count_only``).
#: * ``dom:read_self_owned_editor_fields`` -- ``container`` (kind, the anchor
#:   word, a count) and ``fields``: each control's accessible NAME in his own
#:   editor (its label) and its type, role and states. His own editor's
#:   labels. (Driven with the default projection; the write path's
#:   ``include_dom_id=True`` adds the element's id, an attribute of his own
#:   editor, used by ``writes._live_control`` and never printed.)
#: * ``dom:read_self_owned_editor_values`` -- the same ``container``, and each
#:   field's label and VALUE, verbatim: what he typed into his own profile.
#: * ``profile_views_more:read_profile_views_more_insights`` --
#:   ``sections_found`` (two closed words), ``highlights`` (the top location,
#:   industry and company of his viewers: one value each, over all of them),
#:   ``details`` (a sub-heading and company names, each with a share), and
#:   ``unparsed_lines`` (a count). No field is a viewer: a value is taken
#:   only from the line before a closed label, an entry only from a line
#:   ending in a percentage, and a line that is neither is counted, never
#:   returned.
#: * ``server:_profile_views_more_analytics`` (driven the same day, over the
#:   profile-views skeletons, past the reveal's press by ruling (2)) --
#:   ``reveal`` (the gate's measurements: counts, verdicts, this package's
#:   words), ``insights_after`` (``dom.read_profile_views_insights`` on HIS
#:   OWN analytics page: the headline count and its label, the chart's
#:   description, the filter labels -- it reads no viewer row), and
#:   ``revealed_insights`` (the aggregates above). No field is a viewer.
ADMITTED_TEXT: dict[str, tuple[str, ...]] = {
    "dom:read_profile_detail_entries": (HIS_OWN,),
    "dom:read_self_owned_editor_fields": (HIS_OWN,),
    "dom:read_self_owned_editor_values": (HIS_OWN,),
    # The select path's before-and-after reading (2026-09-28): the values
    # reader above, returned whole, its exception turned into a typed refusal.
    "writes:_editor_values_or_refusal": (HIS_OWN,),
    "profile_views_more:read_profile_views_more_insights": (AGGREGATE,),
    "server:_profile_views_more_analytics": (HIS_OWN, AGGREGATE),
}

#: READERS NOTHING TRACKED CAN DRIVE TO THEIR SUCCESS PATH, each with WHAT
#: WOULD (2026-09-28, the orchestrator's order: "name the capture that would
#: make it drivable"). Every reader a drive leaves not driven after reading
#: nothing, reading only empties, refusing, or building no record is here or
#: has a drive; the test below holds that both ways.
#:
#: Each entry opens with its KIND, because a capture is not always the answer:
#:
#: * ``CAPTURE`` -- a page state nothing tracked draws. Capturing it (and
#:   committing a skeleton of it) is what is missing.
#: * ``ACTION`` -- its success path presses, types or loads a page, which the
#:   planted page refuses by design. A capture of the page after the action
#:   is needed AND a stand-in for the action, which is a ruling on this
#:   harness, not a fixture.
#: * ``NOT A PAGE READER`` -- it takes ``page`` but its success path reads no
#:   page content at all (a cookie jar, a disk write, an address), so no
#:   capture can make this guard's read count move.
#: * ``RULING`` -- a tracked fixture drives it, and what its success path
#:   returns is page text outside a record, which the text inventory may not
#:   admit without one. (None is left: the four held on 2026-09-28 were ruled
#:   on the same day -- :data:`ADMITTED_TEXT`.)
#:
#: FIVE OF THE 22 THE ORDER NAMED LEFT THIS SET THE SAME DAY, recorded
#: ``navigates`` -- a reason that already says what would drive them: a
#: stand-in for the action. Two had returned "without reading" because their
#: own ``except Exception`` swallowed the harness's refusal of a page load,
#: which ``plantedpage.NavigationAttempted`` no longer allows:
#: ``auth:_warm_session_cookies`` (loads the feed to be issued a cookie, then
#: reads the cookie jar) and ``writes:_read_account_share_updates`` (loads
#: the settings page; its page half,
#: ``profile_editor:read_account_share_updates``, is driven clean). Three are
#: driven to their click by ``shipped_drives.TO_THE_PRESS``: ``press:disclose``,
#: ``reveal:reveal``, ``share_link:copy_own_post_link``.
#:
#: AND SEVEN MORE LEFT IT LATER THE SAME DAY, by the orchestrator's rulings of
#: 04:25: the four ``view_switch`` readers are driven over the committed
#: profile-views skeletons (ruling 3); ``reveal:reveal`` and
#: ``server:_profile_views_more_analytics`` are driven past the reveal's press,
#: stood in for by the capture of the page after it (ruling 2); and
#: ``view_switch:apply_and_restore`` and ``server:_profile_views_switch`` are
#: driven past the pill's press to the option's, which no capture shows --
#: recorded ``navigates``, the transition named in
#: ``shipped_drives.TRANSITIONS``.
WHAT_WOULD_DRIVE_IT: dict[str, str] = {
    "auth:_arm_session_store": (
        "NOT A PAGE READER: it touches only page.context, returns None on "
        "every path, and its success path writes the session store "
        "(SESSION_STORE.save_from_context); no capture moves a page read."
    ),
    "auth:_maybe_corroborate": (
        "NOT A PAGE READER: with corroborate on it either loads the feed "
        "(BROWSER.goto, refused offline) or works from the address it is "
        "handed, reading no page content either way."
    ),
    #: ADDED 2026-09-28, fix 1 of the live lane's session 2: the one function
    #: that closes a tab of ours, never the browser's last. Discovered here
    #: because it takes a ``page``; it reads nothing ON the page.
    "browser:close_tab_keeping_the_window": (
        "NOT A PAGE READER: it reads no page content -- it asks whether the "
        "tab is closed, counts the open pages of the tab's context, may open "
        "a blank keeper tab, closes the tab, and returns one of the TAB_* "
        "constants on every path. Its behaviour is held over fake contexts by "
        "tests/test_the_last_tab_is_never_closed.py."
    ),
    #: ADDED 2026-09-28 (lane L5, the first-contact path of
    #: message_from_profile): the one overlay bubble holding a composer, read
    #: through the piercing engine. Its success path is a bubble a Message
    #: press opened, which a planted page never draws.
    "named_profile:holding_bubble": (
        "ACTION: a Message press on a named profile, which opens the overlay "
        "bubble inside a shadow root -- the live lane's tracked copy of the one "
        "session 3 drew is tests/fixtures/live3/m1_composer_bubble.html, and "
        "tests/test_first_contact_message.py drives this reader over the page "
        "built from it, in a shadow root, after that press. The harness presses "
        "nothing, so no bubble holds a composer and every field reads None."
    ),
    #: ADDED 2026-09-28 (lane L5, the orchestrator's call of 19:48): where his
    #: words are after a Message from a profile, read in place as the verdict
    #: is written. Its success path is a composer holding his words.
    "named_profile:words_in_the_box": (
        "ACTION: a Message from a profile whose words went into the composer -- "
        "typed, or already there as a draft. tests/test_first_contact_message.py "
        "drives this reader after the act, over the bubble built from the live "
        "lane's copy, in a shadow root, and reads it True and False. The harness "
        "types nothing, so no composer holds anybody's words."
    ),
    #: ADDED 2026-09-28 (lane L5, the orchestrator's order of 21:08): the same
    #: question of a reply's box, read after the verdict's fresh load -- did
    #: LinkedIn keep his words. Its success path is a reply box holding them.
    "threads:words_in_the_box": (
        "ACTION: a reply whose words went into the box, typed or already there "
        "as a draft. tests/test_reply_send_wait_and_draft.py drives this reader "
        "after the act, over the reply fixture's fresh load, and reads it True "
        "and False. The harness types nothing, so no reply box holds anybody's "
        "words."
    ),
    "dom:read_compose_fields": (
        "CAPTURE: /messaging/compose/ as loaded -- an empty composer, nothing "
        "clicked or typed -- drawing its two send-mode radios as "
        "_audit/2026-08-31-linkedin-perform.md records them (both named by "
        "label-for, one checked), sanitised into a synthetic skeleton; the "
        "tracked compose fixture draws no radio. A committed script reading "
        "exists (tests/test_compose_fields.py MEASURED_MODES), but no page."
    ),
}

#: The verdicts that mean a drive never reached its success path.
VACUOUS = (NO_PAGE_READ, *READ_BUT_NOT_DRIVEN)

#: The kinds an entry above may open with.
WHAT_WOULD_DRIVE_IT_KINDS = ("CAPTURE: ", "ACTION: ", "NOT A PAGE READER: ", "RULING: ")


def _reader_key(fn: Callable[..., Any]) -> str:
    return f"{getattr(fn, '__module__', '').split('.')[-1]}:{getattr(fn, '__name__', '')}"


def drive(fn: Callable[..., Any]) -> tuple[str, str]:
    """Run one reader against the planted page. ``(verdict, detail)``.

    The exception path is the SUBJECT, not an accident, so every ``BaseException``
    is caught and walked. A reader that raises is not thereby clean: the whole
    finding is that an exception carries values a return value would not.
    """
    variants, refusal = _build_call(fn)
    builds = _reader_key(fn) in record_readers()
    verdicts = (
        []
        if variants is None
        else [_drive_once(fn, args, kwargs, builds_records=builds) for args, kwargs in variants]
    )
    shipped = AS_SHIPPED.get(_reader_key(fn))
    if shipped is not None:
        verdicts.append(_drive_once(shipped, [PlantedPage()], {}, builds_records=builds))
    if not verdicts:
        return f"not_driven:{refusal}", refusal
    return _worst(verdicts)


def _drive_once(
    fn: Callable[..., Any],
    args: list[Any],
    kwargs: dict[str, Any],
    *,
    builds_records: bool = False,
) -> tuple[str, str]:
    pages = [v for v in (*args, *kwargs.values()) if isinstance(v, PlantedPage)]
    counted = {"reads": 0}

    async def _run() -> Any:
        call_args, call_kwargs = await resolve_paired_observations(args, kwargs)
        # THE READER'S OWN READS: a paired Observation is built by reading
        # the page first, and those reads are the harness's, not the reader's.
        before = sum(page.reads for page in pages)
        try:
            return await asyncio.wait_for(
                fn(*call_args, **call_kwargs), timeout=DRIVE_TIMEOUT_S
            )
        finally:
            counted["reads"] = sum(page.reads for page in pages) - before

    try:
        result = asyncio.run(_run())
    except NavigationAttempted as exc:
        return f"not_driven:navigates ({exc})", str(exc)
    except asyncio.TimeoutError:
        return f"not_driven:timed out after {DRIVE_TIMEOUT_S}s", ""
    except BaseException as exc:  # noqa: BLE001 -- the exception is the subject
        hits = carries_the_plant(exc)
        if hits:
            return LEAKS, f"{type(exc).__name__} carries it at {hits[0]}"
        return f"not_driven:raises {type(exc).__name__}", str(exc)[:120]
    return classify_drive(result, counted["reads"], builds_records=builds_records)


def empty_shape(value: Any, depth: int = 0) -> bool:
    """Is ``value`` an EMPTY SHAPE -- ``None``, ``False``, zero, ``""``, or a
    container holding only those, however nested? What an early return hands
    back; a success path on the planted page, where every count is 1 and every
    string the plant, hands back something else."""
    if depth > 16:
        return False
    if value is None or value is False:
        return True
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, str):
        return value == ""
    if isinstance(value, dict):
        return all(empty_shape(item, depth + 1) for item in value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return all(empty_shape(item, depth + 1) for item in value)
    return False


def _whole_call(result: Any, field: str) -> Any:
    """``result``'s top-level ``field`` when it is truthy and not a tally (a
    mapping or a sequence of per-item counts); otherwise ``None``."""
    if not isinstance(result, dict):
        return None
    value = result.get(field)
    if not value or isinstance(value, (dict, list, tuple, set, frozenset)):
        return None
    return value


def whole_call_refusal(result: Any) -> Any:
    """The refusal ``result`` IS, or ``None``. See :data:`REFUSED_AFTER_READ`."""
    return _whole_call(result, "refused")


def whole_call_error(result: Any) -> Any:
    """The failure ``result`` IS, or ``None``. See :data:`ERRORED_AFTER_READ`."""
    return _whole_call(result, "error")


def classify_drive(result: Any, reads: int, *, builds_records: bool = False) -> tuple[str, str]:
    """The verdict on one DRIVE: what came back, and whether the success path
    ran to produce it -- for a people reader, its records; for any other, a
    read and a result that is neither empty nor a refusal. Pure, so the
    controls drive the code the guard runs."""
    verdict, detail = classify_returned(result)
    if verdict != CLEAN:
        return verdict, detail
    if reads == 0:
        return NO_PAGE_READ, "the reader returned before any read of the page"
    if builds_records:
        return NO_RECORD, f"{reads} read(s), and no people record came back"
    refusal = whole_call_refusal(result)
    if refusal is not None:
        return REFUSED_AFTER_READ, f"{reads} read(s), and it refused: {str(refusal)[:60]}"
    failure = whole_call_error(result)
    if failure is not None:
        return ERRORED_AFTER_READ, f"{reads} read(s), and it failed: {str(failure)[:60]}"
    if empty_shape(result):
        return EMPTY_RESULT, f"{reads} read(s), and every value that came back was empty"
    return CLEAN, f"{reads} read(s)"


def classify_returned(result: Any) -> tuple[str, str]:
    """The verdict on what a reader RETURNED. ``(verdict, detail)``.

    A pure function of the value, so the controls below drive the same code the
    guard does rather than a copy of it.
    """
    # CHECKED BEFORE ``returns_text``, because it IS a leak wearing its costume.
    # A caught coercion failure put into an output field has carried the value
    # out just as surely as a raise would have -- see
    # ``plantedpage.carries_a_laundered_exception``. A record does not excuse
    # it: this walk is plain.
    laundered = carries_a_laundered_exception(result)
    if laundered:
        return LEAKS, f"a caught coercion failure was returned at {laundered[0]}"

    hits = carries_the_plant(result)
    if not hits:
        return CLEAN, ""
    outside, records = carries_the_plant_outside_records(result)
    if not outside:
        return RETURNS_RECORDS, f"page text only inside {records} people record(s)"
    return RETURNS_TEXT, f"returns page text at {outside[0]}"


def _worst(verdicts: list[tuple[str, str]]) -> tuple[str, str]:
    """The most serious verdict across a reader's call variants.

    ONE VARIANT LEAKING IS THE READER LEAKING. A reader driven with thirteen
    shipped ``WriteSpec``s that carries a name out under one of them has the
    defect; the twelve that returned early prove only that they returned early.
    Ranking clean ABOVE not-driven is deliberate for the same reason in reverse
    -- if any variant actually ran and came back clean, the reader WAS measured,
    and reporting it as un-measurable would understate the coverage.

    AND AMONG THE NOT-DRIVEN, THE VARIANT THAT GOT FURTHEST NAMES THE READER
    (2026-09-28): one that read the page and stopped short of success, then
    one that reached an action the harness refuses, then the rest -- refused
    or raised before either. Measured on the tree before that day's drives:
    the read rank alone moved no recorded verdict. With the drives, the
    action rank moved four, each to the truer reason: the three press
    readers, driven to their click, and ``writes:_load_named_profile``, one
    of whose variants reaches its page load past another's raise.
    """
    order = {LEAKS: 4, RETURNS_TEXT: 3, RETURNS_RECORDS: 2, CLEAN: 1}

    def rank(verdict: tuple[str, str]) -> float:
        if verdict[0] in order:
            return order[verdict[0]]
        if verdict[0] in READ_BUT_NOT_DRIVEN:
            return 0.5
        return 0.25 if verdict[0].startswith(NAVIGATES) else 0

    return max(verdicts, key=rank)


def measure() -> dict[str, tuple[str, str]]:
    return {name: drive(fn) for name, fn in discover_readers()}


# ---------------------------------------------------------------------------
# The guard
# ---------------------------------------------------------------------------


def _baseline() -> dict[str, str]:
    if not BASELINE_PATH.exists():
        return {}
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["readers"]


@pytest.mark.parametrize("name", [n for n, _ in discover_readers()])
def test_no_reader_carries_a_page_string_out(name: str) -> None:
    """One reader, driven by a page that answers in strings.

    A failure here means a name reached a caller. The plant is synthetic; the
    path it travelled is not.
    """
    fn = dict(discover_readers())[name]
    verdict, detail = drive(fn)
    assert verdict != LEAKS, (
        f"{name} carried the planted page string out of the process: {detail}. "
        f"An exception is not a return value -- coerce through a helper that "
        f"never raises and never quotes its input: "
        f"linkedin_server.coerce.as_count / as_int / counts_only."
    )


def test_the_driven_set_has_not_silently_shrunk() -> None:
    """Coverage is compared against a COMMITTED baseline, not asserted.

    Three ways this fails, and each one is a real event rather than a chore:

    * a reader stopped being drivable -- the guard now certifies less than it
      did and the diff does not say so;
    * a reader appeared and nobody classified it -- the fourth instance of the
      class, arriving unmeasured;
    * a reader vanished -- a rename that would otherwise take its coverage with
      it, silently.
    """
    baseline = _baseline()
    assert baseline, (
        f"{BASELINE_PATH.name} is missing or empty. It is the record of what "
        f"this guard covers; without it the guard cannot report shrinkage."
    )
    live = {name: verdict for name, (verdict, _) in measure().items()}

    appeared = sorted(set(live) - set(baseline))
    vanished = sorted(set(baseline) - set(live))
    regressed = sorted(
        name
        for name in set(live) & set(baseline)
        if baseline[name] == CLEAN and live[name] != CLEAN
    )

    assert not appeared, (
        "new page reader(s) with no recorded verdict: "
        + ", ".join(appeared)
        + f". Run scripts/_check_the_coercion_family_guard_can_fail.py and "
        f"commit the refreshed {BASELINE_PATH.name}."
    )
    assert not vanished, (
        "reader(s) in the baseline no longer exist: "
        + ", ".join(vanished)
        + ". A rename takes its coverage with it unless the baseline moves too."
    )
    assert not regressed, (
        "reader(s) that this guard used to DRIVE can no longer be driven: "
        + ", ".join(f"{n} -> {live[n]}" for n in regressed)
        + ". The guard now certifies less than the baseline says it does."
    )
    # THE LEGACY TEXT INVENTORY MAY SHRINK AND MAY NOT GROW (2026-09-24).
    ratchet = text_ratchet(baseline, live, ADMITTED_TEXT)
    assert not ratchet, (
        "the page-text inventory moved: " + "; ".join(ratchet) + ". A page "
        "string leaves only through a people_data record: a NEW text path must "
        "return records instead; a STALE entry means a reader stopped returning "
        f"text and {BASELINE_PATH.name} must be regenerated so the inventory "
        "shrinks; LOST RECORDS means a converted reader fell back."
    )


def test_the_named_profile_namer_is_driven_through_a_real_read() -> None:
    """``name_the_profile_target`` READS THE PAGE AND RETURNS A RECORD, here.

    Its as-shipped variant reaches both page reads and names the plant inside
    a people record -- the declared channel -- while its signature variants
    alone take the early return and read nothing. So its verdict in the
    baseline is the shipped variant's work, and a namer that stopped reading
    the page, or printed the plant outside the record, fails here by name.
    """
    from linkedin_server import named_profile

    fn = named_profile.name_the_profile_target
    shipped = _drive_once(AS_SHIPPED[_reader_key(fn)], [PlantedPage()], {})
    assert shipped[0] == RETURNS_RECORDS, shipped
    variants, _refusal = _build_call(fn)
    generic = [_drive_once(fn, args, kwargs) for args, kwargs in variants or []]
    # SAID OUT LOUD SINCE 2026-09-27: these read nothing, and are not clean.
    assert generic and all(verdict == NO_PAGE_READ for verdict, _ in generic), generic
    assert drive(fn)[0] == RETURNS_RECORDS
    block = asyncio.run(_name_the_profile_target_as_shipped(PlantedPage()))
    assert block["whom_this_resolves_to"]["name"] == PLANT, block


@pytest.mark.parametrize(
    "fn_key, records",
    [("threads:name_the_reply_recipient", 2), ("writes:_name_the_invitation_recipient", 1)],
)
def test_the_preview_namers_are_driven_to_the_records_they_build(fn_key, records) -> None:
    """THE TWO PREVIEW NAMERS (PREVIEW-NAMES-THE-RESOLVED-TARGET) read a page
    and return people records, here -- a group conversation's title record and
    a one-member conversation's person, and the invitation's person. Driven by
    signature alone they returned before reading and were recorded clean."""
    fn = dict(discover_readers())[fn_key]
    variants, _refusal = _build_call(fn)
    generic = [_drive_once(fn, args, kwargs)[0] for args, kwargs in variants or []]
    assert generic and CLEAN not in generic, generic
    verdict, detail = _drive_once(AS_SHIPPED[fn_key], [PlantedPage()], {})
    assert verdict == RETURNS_RECORDS, (verdict, detail)
    assert detail == f"page text only inside {records} people record(s)", detail


class _TheLabelDoesNotRead(_OneCardOnTheRail):
    """The rail reads as the observation recorded it; the control's label
    fails to read, as a live page's can."""

    @property
    def first(self) -> Any:
        return _TheLabelDoesNotRead(self._located.first)

    async def get_attribute(self, name: str, **kwargs: Any) -> Any:
        raise RuntimeError("the label did not read")


class _AFailingLabelOnTheRail(_AnswersTheInvitationRail):
    def locator(self, *args: Any, **kwargs: Any) -> Any:
        return _TheLabelDoesNotRead(self._page.locator(*args, **kwargs))


def test_the_invitation_namer_survives_a_label_that_does_not_read() -> None:
    """A FAILED READ IS LOGGED BY ITS TYPE AND THE BLOCK COMES BACK
    (2026-09-28, found by lane G item 4's census). The namer's handler logged
    through a ``logger`` that ``writes.py`` never defined, so the branch its
    own comment calls "never raised" raised ``NameError`` -- and no drive had
    reached it: the signature variants return first, the as-shipped drive's
    label reads."""
    from linkedin_server import writes

    from tests import refusinggrant

    spec = writes.spec_for_action("send_invitation")
    observation = _inert_observation(
        spec, {"controls": 1}, target=refusinggrant.synthetic_target(spec)
    )
    block = {"marker": "the preview block, untouched"}
    out = asyncio.run(
        writes._name_the_invitation_recipient(
            _AFailingLabelOnTheRail(PlantedPage()), spec, observation, dict(block)
        )
    )
    assert out == block, out


# ---------------------------------------------------------------------------
# A clean verdict is earned: the success path ran
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "result, reads, verdict",
    [
        ({"count": 1}, 2, CLEAN),
        ({"refused": "unknown_section", "why": "a sentence"}, 0, NO_PAGE_READ),
        ({"count": 1}, 0, NO_PAGE_READ),
        ({"rows": [], "count": 0, "error": None}, 3, EMPTY_RESULT),
        (None, 1, EMPTY_RESULT),
        ([False, "", {}], 1, EMPTY_RESULT),
        ({"present": True}, 1, CLEAN),
        (PLANT, 0, RETURNS_TEXT),
        ({"refused": "no_anchor", "why": "a sentence"}, 1, REFUSED_AFTER_READ),
        ({"pressed": False, "refused": "press_failed", "why": "a sentence"}, 13, REFUSED_AFTER_READ),
        ({"refused": True, "reason": "a sentence"}, 2, REFUSED_AFTER_READ),
        ({"recognised": 1, "refused": {"no_href": 1}}, 1, CLEAN),
        ({"rows": [1], "refused": ["one item"]}, 1, CLEAN),
        ({"count": 1, "refused": None}, 1, CLEAN),
        ({"count": 1, "refused": False}, 1, CLEAN),
        ({"recognised": 0, "containers": 1, "error": "AttributeError"}, 3, ERRORED_AFTER_READ),
        ({"reading": "on", "named": 1, "error": None}, 2, CLEAN),
        ({"rows": [1], "error": {"TimeoutError": 1}}, 1, CLEAN),
    ],
    ids=[
        "read and returned", "a refusal that read nothing", "a value that read nothing",
        "read and returned empty", "read and returned None", "nested empties",
        "a True is not empty", "a plant needs no proof",
        "a refusal after a read", "a press the harness refused", "a refusal spelled True",
        "a tally is not a refusal", "a list is not a refusal",
        "no refusal, None", "no refusal, False",
        "a failure after a read", "no failure, None", "a failure tally is not a failure",
    ],
)
def test_a_clean_drive_needs_a_read_and_something_back(result, reads, verdict) -> None:
    assert classify_drive(result, reads)[0] == verdict


@pytest.mark.parametrize(
    "variants, reason",
    [
        ([(NO_PAGE_READ, ""), (REFUSED_AFTER_READ, "13 read(s)")], REFUSED_AFTER_READ),
        ([("not_driven:raises ValueError", ""), (EMPTY_RESULT, "1 read(s)")], EMPTY_RESULT),
        ([(EMPTY_RESULT, ""), (CLEAN, "2 read(s)")], CLEAN),
        ([(NO_PAGE_READ, ""), ("not_driven:raises ValueError", "")], NO_PAGE_READ),
        ([(NO_PAGE_READ, ""), ("not_driven:navigates (locator.click)", "")],
         "not_driven:navigates (locator.click)"),
        ([("not_driven:navigates (page.goto)", ""), (EMPTY_RESULT, "1 read(s)")], EMPTY_RESULT),
    ],
    ids=["the drive that read names it", "a read outranks a raise", "clean outranks both",
         "neither read: the first stands", "an action outranks a refusal before it",
         "a read outranks an action"],
)
def test_the_variant_that_got_furthest_names_a_reader_not_driven(variants, reason) -> None:
    assert _worst(variants)[0] == reason


@pytest.mark.parametrize(
    "result, reads, verdict",
    [
        ({"people": [], "people_denominators": {"result_cards_seen": 1}}, 1, NO_RECORD),
        ({"count": 1}, 3, NO_RECORD),
        ({"count": 1}, 0, NO_PAGE_READ),
    ],
    ids=["lane S's reader, as it came back", "counts and no record", "no read at all"],
)
def test_a_people_readers_success_path_is_its_records(result, reads, verdict) -> None:
    """A PEOPLE READER'S CLEAN IS EARNED ONLY BY RECORDS: counts and a non-empty
    result are not its success path, and a records verdict is untouched."""
    assert classify_drive(result, reads, builds_records=True)[0] == verdict
    from linkedin_server import people_data

    record = {"person": people_data.Person.from_page(name=PLANT).envelope()}
    assert classify_drive(record, reads, builds_records=True)[0] == RETURNS_RECORDS


def test_lane_s_people_reader_is_driven_to_its_records() -> None:
    """THE READER THE ORDER NAMED. Driven by its signature,
    ``people_results.read_result_people`` reaches a record builder, reads the
    planted page, skips its one card for want of a member link and returns its
    denominators: NO RECORD, never clean. Driven over the people-search
    skeleton (``tests/shipped_drives.py``), it returns ONE record, the plant
    inside it -- and that is the verdict the baseline records."""
    from linkedin_server import people_results

    key = "people_results:read_result_people"
    assert key in record_readers()
    variants, _refusal = _build_call(people_results.read_result_people)
    generic = [_drive_once(people_results.read_result_people, a, k, builds_records=True)
               for a, k in variants or []]
    assert generic and all(verdict == NO_RECORD for verdict, _ in generic), generic
    shipped = _drive_once(AS_SHIPPED[key], [PlantedPage()], {}, builds_records=True)
    assert shipped == (RETURNS_RECORDS, "page text only inside 1 people record(s)"), shipped
    assert drive(people_results.read_result_people)[0] == RETURNS_RECORDS
    assert _baseline()[key] == RETURNS_RECORDS


#: What each drive to the success path comes back as: clean, the people
#: reader's records, or -- for a reader the ruling admitted -- text.
DRIVEN_TO = {key: CLEAN for key in shipped_drives.DRIVES}
DRIVEN_TO["people_results:read_result_people"] = RETURNS_RECORDS
DRIVEN_TO.update({key: RETURNS_TEXT for key in ADMITTED_TEXT})
# LANE S'S TWO PEOPLE READERS (2026-09-28): each success path returns people
# records -- the composer's suggested people and the recruiter viewers -- so
# the plant comes back inside a record, where the rule says it may.
DRIVEN_TO["presence:read_suggested_presence"] = RETURNS_RECORDS
DRIVEN_TO["recruiter_views:read_recruiter_views"] = RETURNS_RECORDS


@pytest.mark.parametrize("key", sorted(shipped_drives.DRIVES))
def test_a_drive_from_a_tracked_fixture_earns_the_verdict(key: str) -> None:
    """EACH DRIVE IS WHAT EARNS ITS READER'S VERDICT: alone it comes back
    clean (or with records), the reader's signature variants alone do not,
    and the reader's recorded verdict is the drive's."""
    fn = dict(discover_readers())[key]
    builds = key in record_readers()
    verdict, detail = _drive_once(shipped_drives.DRIVES[key], [PlantedPage()], {},
                                  builds_records=builds)
    assert verdict == DRIVEN_TO[key], (verdict, detail)
    variants, _refusal = _build_call(fn)
    generic = [_drive_once(fn, a, k, builds_records=builds)[0] for a, k in variants or []]
    assert generic and all(v in VACUOUS for v in generic), generic
    assert drive(fn)[0] == DRIVEN_TO[key]
    assert _baseline()[key] == DRIVEN_TO[key]


@pytest.mark.parametrize("key", sorted(shipped_drives.TO_THE_PRESS))
def test_a_drive_to_the_press_reaches_the_press_and_no_further(key: str) -> None:
    """THE HARNESS'S REFUSAL OF THE CLICK IS THE PROOF THE PRESS WAS REACHED:
    it escapes the reader's own handler now, so the drive ends on it, after
    the reads before the press. A drive that fell short of the click comes
    back with the reader's refusal instead -- ``reveal_control_not_unique``,
    ``counters_unreadable_before_any_press`` -- and fails here. The reader's
    recorded verdict is that action: what would drive it further is a
    stand-in for the click."""
    verdict, detail = _drive_once(shipped_drives.TO_THE_PRESS[key], [PlantedPage()], {})
    assert verdict == "not_driven:navigates (locator.click)", (verdict, detail)
    fn = dict(discover_readers())[key]
    assert drive(fn)[0] == verdict
    assert _baseline()[key] == verdict
    assert key not in WHAT_WOULD_DRIVE_IT


@pytest.mark.parametrize("key", sorted(ADMITTED_TEXT))
def test_a_reader_joins_the_text_inventory_only_by_the_ruling(key: str) -> None:
    """ADMITTED, AND FOR A RULED REASON ONLY (2026-09-28). Each admitted
    reader is driven to its success path by a tracked fixture, comes back
    with page text outside a record, and is recorded so; its reason is one
    the ruling gave; and without its admission the ratchet and the baseline
    writer still refuse it as a new text path -- the door is this table."""
    assert key in shipped_drives.DRIVES, "an admission must be earned by a drive"
    assert set(ADMITTED_TEXT[key]) and set(ADMITTED_TEXT[key]) <= {HIS_OWN, AGGREGATE}
    fn = dict(discover_readers())[key]
    assert drive(fn)[0] == RETURNS_TEXT
    assert _baseline()[key] == RETURNS_TEXT
    was = {key: NO_PAGE_READ}
    now = {key: RETURNS_TEXT}
    assert text_ratchet(was, now) == [f"new text path: {key} (not_driven -> returns_text)"]
    assert text_ratchet(was, now, ADMITTED_TEXT) == []
    assert text_paths_a_baseline_may_not_record(was, now) == [key]
    assert text_paths_a_baseline_may_not_record(was, now, ADMITTED_TEXT) == []


#: EACH DRIVE'S PREMISE, BROKEN (2026-09-28). For every drive in
#: ``tests/shipped_drives.py``, ONE needle of the shape it rests on, and what
#: it is broken into in a scratch copy of the fixtures. The drive must then
#: RAISE -- recorded not driven -- and never come back with its verdict on a
#: page the fixture no longer draws. Found by this control the day the drives
#: were written: the disclose drive checked its headline inside a double,
#: i.e. inside the counter reader's own ``except Exception``, which swallowed
#: the check, and the drive went on to its click on the broken fixture.
FIXTURE_BREAKS: dict[str, dict[str, str]] = {
    "dom:read_any_save_control_label": {
        "fixture": "job_detail_hydrated.html",
        "needle": 'aria-label="Save the job"', "into": 'aria-label="Keep the job"',
    },
    "dom:read_profile_detail_entries": {
        "fixture": "profile_skills.html",
        "needle": "/details/skills/edit/forms/", "into": "/details/skills/",
    },
    "dom:read_self_owned_editor_fields": {
        "fixture": "synthetic/intro_editor_switches.html",
        "needle": "<p>Placeholder setting A</p>", "into": "<p>Placeholder setting Z</p>",
    },
    "dom:read_self_owned_editor_values": {
        "fixture": "synthetic/intro_editor_switches.html",
        "needle": "<p>Placeholder setting A</p>", "into": "<p>Placeholder setting Z</p>",
    },
    "writes:_editor_values_or_refusal": {
        "fixture": "synthetic/intro_editor_switches.html",
        "needle": "<p>Placeholder setting A</p>", "into": "<p>Placeholder setting Z</p>",
    },
    "named_profile:composer_holds": {
        "fixture": "synthetic/named_profile.html",
        "needle": "data-dispatches", "into": "data-other",
    },
    "people_results:read_result_people": {
        "fixture": "synthetic/people_search_results.html",
        "needle": "&#8226; 2nd", "into": "2nd",
    },
    "presence:read_suggested_presence": {
        "fixture": "synthetic/compose_suggestions.html",
        "needle": "<span>Status is reachable</span>", "into": "<span>Status is away</span>",
    },
    "recruiter_views:read_recruiter_views": {
        "fixture": "synthetic/recruiter_views.html",
        "needle": "<p>Viewed 2w ago</p>", "into": "<p>Seen 2w ago</p>",
    },
    "press:disclose": {
        "fixture": "profile_views_analytics.html",
        "needle": "<p>Profile viewers</p>", "into": "<p>Viewers</p>",
    },
    "profile_editor:read_premium_badge": {
        "fixture": "synthetic/intro_editor_switches.html",
        "needle": "<p>Placeholder setting A</p>", "into": "<p>Placeholder setting Z</p>",
    },
    "reveal:reveal": {
        "fixture": "synthetic/profile_views_verify.html",
        "needle": ">Show more analytics<", "into": ">Xxxx xxxx xxxxxxxxx<",
    },
    "profile_views_more:read_profile_views_more_insights": {
        "fixture": "synthetic/profile_views_revealed.html",
        "needle": ">Highlights<", "into": ">Xxxxxxxxxx<",
    },
    "server:_profile_views_more_analytics": {
        "fixture": "synthetic/profile_views_revealed.html",
        "needle": ">Details<", "into": ">Xxxxxxx<",
    },
    "server:_profile_views_switch": {
        "fixture": "synthetic/profile_views_closed.html",
        "needle": "Interesting viewers", "into": "Xxxxxxxxxxx xxxxxxx",
    },
    "view_switch:_apply_positions": {
        "fixture": "synthetic/profile_views_pill_open.html",
        "needle": ">Show results<", "into": ">Xxxx xxxxxxx<",
    },
    "view_switch:_option_positions": {
        "fixture": "synthetic/profile_views_pill_open.html",
        "needle": 'aria-label="Works at a company you follow"',
        "into": 'aria-label="Xxxxx xx x xxxxxxx xxx xxxxxx"',
    },
    "view_switch:_pill_positions": {
        "fixture": "synthetic/profile_views_closed.html",
        "needle": "Interesting viewers", "into": "Xxxxxxxxxxx xxxxxxx",
    },
    "view_switch:_wait_for_option": {
        "fixture": "synthetic/profile_views_pill_open.html",
        "needle": 'aria-expanded="true"', "into": 'aria-expanded="false"',
    },
    "view_switch:apply_and_restore": {
        "fixture": "synthetic/profile_views_closed.html",
        "needle": 'aria-expanded="false"', "into": 'aria-expanded="mixed"',
    },
    "server:_attach_recipient_ids": {
        "fixture": "profile_views_analytics.html",
        "needle": "recipient=", "into": "other=",
    },
    "server:_profile_views_press_counters": {
        "fixture": "profile_views_analytics.html",
        "needle": "<p>Profile viewers</p>", "into": "<p>Viewers</p>",
    },
    "share_link:copy_own_post_link": {
        "fixture": "synthetic/own_post_menu.html",
        "needle": 'id="decoy-toggle"', "into": 'id="decoy-other"',
    },
    "threads:composer_holds": {
        "fixture": "synthetic/messaging_thread.html",
        "needle": 'id="reply-editor"', "into": 'id="reply-other"',
    },
}

ALL_DRIVES = {**shipped_drives.DRIVES, **shipped_drives.TO_THE_PRESS}


def test_every_drive_has_its_premise_broken_below() -> None:
    assert set(FIXTURE_BREAKS) == set(ALL_DRIVES), sorted(set(ALL_DRIVES) ^ set(FIXTURE_BREAKS))


@pytest.mark.parametrize("key", sorted(ALL_DRIVES))
def test_a_drive_on_a_fixture_that_stopped_drawing_its_shape_raises(
    key: str, tmp_path: Any, monkeypatch: Any
) -> None:
    """A DRIVE IS ONLY AS GOOD AS ITS FIXTURE STILL BEING WHAT IT CITES:
    each drive re-reads its fixture before the reader runs, and a broken
    needle makes it raise -- not driven -- rather than measure a page nobody
    draws. The needle is checked present first, so a control that breaks
    nothing fails here instead of passing."""
    broken = FIXTURE_BREAKS[key]
    copy = tmp_path / "fixtures"
    shutil.copytree(shipped_drives.FIXTURES, copy)
    target = copy / broken["fixture"]
    text = target.read_text(encoding="utf-8")
    assert broken["needle"] in text, (key, broken["needle"])
    target.write_text(text.replace(broken["needle"], broken["into"]), encoding="utf-8")
    monkeypatch.setattr(shipped_drives, "FIXTURES", copy)
    verdict, detail = _drive_once(
        ALL_DRIVES[key], [PlantedPage()], {}, builds_records=key in record_readers()
    )
    assert verdict == "not_driven:raises AssertionError", (verdict, detail)



@pytest.mark.parametrize("press, before, after", shipped_drives.TRANSITIONS)
def test_each_stood_in_press_names_the_capture_that_shows_the_page_after_it(
    press: str, before: str, after: Any
) -> None:
    """RULING (2), APPLIED (2026-09-28): a press the guard's double stands in
    for moves it to the skeleton of the capture taken after that press, and
    each such transition names its source; a press no capture shows (``after``
    None) is refused, as the planted page refuses every press, and the drive
    ends there -- never a state the double invented."""
    assert before in shipped_drives.VIEWS_SOURCES, before
    if after is not None:
        assert after in shipped_drives.VIEWS_SOURCES and after != before, after


def _run_until_refused(drive: Callable[..., Any], at: Any) -> Any:
    """``drive(at)`` to its end; the harness's refusal of a press, if any,
    returned rather than raised, so a test can read what the double did."""
    try:
        return asyncio.run(drive(at))
    except NavigationAttempted as refused:
        return refused


def test_the_stand_in_carries_the_reveal_past_its_press_and_nothing_else() -> None:
    """THE STAND-IN, SHOWN DOING THE WORK. With the double's stand-in taken
    away, the reveal ends at its click, as a ``TO_THE_PRESS`` drive does; with
    it, the one press is the decided one, the reveal is PERMITTED, and
    ``main`` grew from the fresh load's elements to the revealed page's."""
    from linkedin_server import reveal, server

    async def the_reveal(at: Any) -> Any:
        counters = await server._profile_views_press_counters(at)
        return await reveal.reveal(
            at, key=shipped_drives.REVEAL_KEY, read_counters=counters,
            reading=server.PROFILE_VIEWS_MENU_READING,
        )

    bare = shipped_drives._views_page(PlantedPage(), shipped_drives.VIEWS_VERIFY)
    bare._on_click = None
    assert isinstance(_run_until_refused(the_reveal, bare), NavigationAttempted)

    at = shipped_drives._views_page(PlantedPage(), shipped_drives.VIEWS_VERIFY)
    value = _run_until_refused(the_reveal, at)
    assert at._on_click.presses == ["Show more analytics"], at._on_click.presses
    assert value["pressed"] is True and value["permitted"] is True, value
    assert value["main_elements"]["after"] > value["main_elements"]["before"], value
    assert at.unmodelled == [], at.unmodelled


def test_the_switch_is_driven_to_the_one_press_no_capture_shows() -> None:
    """THE OPTION'S PRESS HAS NO CAPTURE, so the switch stays NOT DRIVEN
    there -- and it is THAT press it stops at: the pill's press is stood in
    for (the popover the capture drew), the option is found and read
    unchecked, and only then is a press refused."""
    from linkedin_server import server

    async def the_switch(at: Any) -> Any:
        return await server._profile_views_switch(
            at, shipped_drives.SWITCH_KEY, server.DEFAULT_LIMIT
        )

    at = shipped_drives._views_page(PlantedPage(), shipped_drives.VIEWS_CLOSED)
    assert isinstance(_run_until_refused(the_switch, at), NavigationAttempted)
    assert at._on_click.presses == ["the Interesting viewers pill", "refused"], (
        at._on_click.presses
    )
    assert at.document is not None and at.unmodelled == [], at.unmodelled
    refused = [row for row in shipped_drives.TRANSITIONS if row[2] is None]
    assert [row[1] for row in refused] == [shipped_drives.VIEWS_PILL_OPEN], refused

def test_every_vacuous_reader_is_driven_or_names_what_would_drive_it() -> None:
    """NO READER IS LEFT NOT DRIVEN WITHOUT SAYING WHAT WOULD DRIVE IT
    (2026-09-28). Every reader whose drives read nothing, read only empties,
    refused, or built no record is in :data:`WHAT_WOULD_DRIVE_IT`, under a
    declared kind, and the committed baseline records it so; an entry whose
    reader is driven now, or gone, is stale."""
    live = {name: verdict for name, (verdict, _) in measure().items()}
    vacuous = sorted(name for name, verdict in live.items() if verdict in VACUOUS)
    untriaged = [name for name in vacuous if name not in WHAT_WOULD_DRIVE_IT]
    assert untriaged == [], (
        "reader(s) never reaching their success path, and not triaged: %s. "
        "Give each a drive in tests/shipped_drives.py from a tracked fixture, "
        "or say in WHAT_WOULD_DRIVE_IT what would drive it." % untriaged
    )
    stale = sorted(name for name in WHAT_WOULD_DRIVE_IT if live.get(name) not in VACUOUS)
    assert stale == [], (
        "WHAT_WOULD_DRIVE_IT names reader(s) that are driven now, or gone: %s. "
        "Remove them." % stale
    )
    baseline = _baseline()
    unrecorded = sorted(name for name in WHAT_WOULD_DRIVE_IT if baseline.get(name) != live[name])
    assert unrecorded == [], (
        "the committed baseline does not record these as the harness finds "
        "them: %s. Regenerate it." % unrecorded
    )
    kindless = sorted(
        name for name, why in WHAT_WOULD_DRIVE_IT.items()
        if not why.startswith(WHAT_WOULD_DRIVE_IT_KINDS)
    )
    assert kindless == [], kindless


def test_the_harness_refusal_of_an_action_cannot_be_swallowed() -> None:
    """A READER'S ``except Exception`` CANNOT TURN THE HARNESS'S REFUSAL INTO
    A CLEAN (2026-09-28). ``NavigationAttempted`` was a ``RuntimeError``: a
    reader that read the page, pressed inside a broad handler and returned
    what it had came back clean, the click swallowed. Measured that day: no
    reader was recorded clean that way, and five not-driven readers' reasons
    were wrong -- two of them among the 22 the order named, which returned
    "without reading" because they had swallowed a page load."""

    async def reads_then_swallows_a_click(page: Any) -> dict[str, Any]:
        count = await page.locator("main").count()
        try:
            await page.locator("button").click()
        except Exception:  # noqa: BLE001 -- the shape under test
            pass
        return {"controls": count}

    verdict, detail = _drive_once(reads_then_swallows_a_click, [PlantedPage()], {})
    assert verdict == "not_driven:navigates (locator.click)", (verdict, detail)
    assert not issubclass(NavigationAttempted, Exception)


@pytest.mark.parametrize(
    "key",
    [
        "named_profile:read_opened_conversation",
        "profile_editor:read_account_share_updates",
        "profile_editor:recognise_intro_editor_switches",
    ],
)
def test_a_reader_that_narrows_a_locator_reaches_its_reading(key: str) -> None:
    """THE THREE READERS RECORDED CLEAN ON A FAILURE (2026-09-28). Each
    narrows a locator with Playwright's ``and_``/``or_``/``filter``; the
    planted locator lacked them, so each returned ``{"error":
    "AttributeError"}`` and read as clean. Every variant now reaches a
    reading with no error in it, and the reader's clean is that reading's."""
    fn = dict(discover_readers())[key]
    variants, _refusal = _build_call(fn)
    assert variants
    for args, kwargs in variants:

        async def run(args: list[Any] = args, kwargs: dict[str, Any] = kwargs) -> Any:
            call_args, call_kwargs = await resolve_paired_observations(args, kwargs)
            return await fn(*call_args, **call_kwargs)

        value = asyncio.run(run())
        assert isinstance(value, dict) and whole_call_error(value) is None, value
    assert drive(fn)[0] == CLEAN


def test_the_failing_locator_narrows_to_a_failing_locator() -> None:
    """A FAILING PAGE STAYS FAILING THROUGH THE ALGEBRA: a locator narrowed
    with ``and_``/``or_``/``filter`` off the failing page is itself failing,
    so no reader escapes the failing family into a page that answers."""
    base = RaisingPage().locator("main")
    for narrowed in (base.and_(base), base.or_(base), base.filter(has_text="x")):
        assert type(narrowed) is RaisingLocator, type(narrowed)
    planted = PlantedPage().locator("main")
    for narrowed in (planted.and_(planted), planted.or_(planted), planted.filter()):
        assert type(narrowed).__name__ == "PlantedLocator", type(narrowed)


def _early_return(fn: Callable[..., Any], *, read_first: bool) -> Callable[..., Any]:
    """``fn`` STUBBED TO RETURN EARLY: a refusal with a sentence in it, after
    one read of the page or none -- dressed as ``fn`` so discovery takes it."""

    async def stub(page: Any, *args: Any, **kwargs: Any) -> Any:
        if read_first:
            page.locator("main")
            return {"rows": [], "count": 0, "error": None}
        return {"refused": "stubbed", "why": "returned before reading the page"}

    stub.__module__ = fn.__module__
    stub.__name__ = stub.__qualname__ = fn.__name__
    return stub


def test_a_reader_stubbed_to_return_early_is_not_counted_clean(monkeypatch) -> None:
    """THE CONTROL THE ORDER NAMED. ``anchors.read_anchors`` reads the page and
    returns what it read: clean. Stubbed to return a refusal before reading,
    or to read and hand back an empty shape, it is NOT clean -- and the
    coverage comparison against the committed baseline FAILS on it by name,
    the way a real reader that stopped reaching its success path would."""
    from linkedin_server import anchors

    real = anchors.read_anchors
    assert drive(real)[0] == CLEAN, drive(real)
    assert _baseline()["anchors:read_anchors"] == CLEAN

    assert drive(_early_return(real, read_first=False))[0] == NO_PAGE_READ
    assert drive(_early_return(real, read_first=True))[0] == EMPTY_RESULT

    monkeypatch.setattr(anchors, "read_anchors", _early_return(real, read_first=False))
    with pytest.raises(AssertionError) as shrunk:
        test_the_driven_set_has_not_silently_shrunk()
    assert "anchors:read_anchors -> " + NO_PAGE_READ in str(shrunk.value), shrunk.value


def test_the_harness_plant_is_never_the_harness_argument() -> None:
    """The two synthetic values must differ, or every echoing reader 'leaks'.

    Small, and it exists because the failure it prevents is invisible: if these
    two ever became the same string, this whole file would go red on readers
    that are doing exactly what they are supposed to, and the natural response
    to a wall of red is to weaken the guard.
    """
    assert PLANT != SYNTHETIC_ARGUMENT
    assert SYNTHETIC_ARGUMENT not in PLANT
    assert PLANT not in SYNTHETIC_ARGUMENT


# ---------------------------------------------------------------------------
# The helper's own contract
# ---------------------------------------------------------------------------
#
# The family guard above is an end-to-end measurement: it proves the readers do
# not leak TODAY, driven through the code they happen to contain. These prove
# the property of the helper they were all repaired onto, so a reader written
# tomorrow that uses it inherits a CHECKED guarantee rather than a habit.


@pytest.mark.parametrize(
    "value",
    [
        PLANT,
        PLANT.encode("utf-8"),
        [PLANT],
        {"k": PLANT},
        None,
        "",
        object(),
        float("nan"),
        True,
        False,
    ],
)
def test_as_int_never_raises_and_never_carries_its_input(value: object) -> None:
    """The two halves of the contract, over input designed to break each.

    ``int()`` raises on most of these and QUOTES several. The replacement may
    do neither, and the second half is checked by WALKING the result rather
    than by reading it -- a returned string, a container holding one, or an
    ``int`` subclass carrying a ``repr`` would all pass an eyeball.
    """
    from linkedin_server.coerce import as_int

    result = as_int(value)  # must not raise
    assert result is None or type(result) is int
    assert not carries_the_plant(result)


def test_as_int_refuses_bool_because_true_is_an_int() -> None:
    """``True`` is an ``int`` in Python, and a count of ``True`` is no reading."""
    from linkedin_server.coerce import as_int

    assert as_int(True) is None
    assert as_int(False) is None
    assert as_int(0) == 0
    assert as_int(1) == 1


def test_as_count_logs_the_type_and_never_the_value(caplog: Any) -> None:
    """A LOG RECORD IS ANOTHER WAY OUT OF THE PROCESS.

    Substituting silently is the green this repository distrusts most, so the
    refusal is announced -- and announcing it is exactly where the original
    defect would reappear if the message carried the value. This drives the
    real logger and reads ``caplog``, which is the channel
    ``leakwalk.assert_no_leak`` takes for the same reason.
    """
    import logging

    from linkedin_server.coerce import as_count

    # DEBUG, NOT WARNING: ``PLANT not in caplog.text`` below is a claim about
    # the whole log, and WARNING raised the package logger's own level from
    # INFO, dropping every INFO and DEBUG record before capture -- a line
    # quoting the value at either level passed it (measured 2026-09-28 with a
    # planted record, lane G item 4). INFO is the level the server runs at.
    with caplog.at_level(logging.DEBUG, logger="linkedin"):
        assert as_count(PLANT) == 0
        assert as_count(PLANT, 7) == 7

    assert caplog.records, "the substitution was silent, which is the other defect"
    assert PLANT not in caplog.text
    assert "str" in caplog.text


def test_counts_only_substitutes_in_place_and_never_drops() -> None:
    """POSITION IS A MEANING on every list this is used for.

    ``counts`` is positional against a closed alphabet whose index 0 is the
    hazard class, so dropping a refused entry renames every kind behind it.
    The length is the assertion.
    """
    from linkedin_server.coerce import counts_only

    values, refused = counts_only([1, PLANT, 3])
    assert values == [1, 0, 3]
    assert refused == 1
    assert len(values) == 3

    negative, _ = counts_only([PLANT], default=-1)
    assert negative == [-1]


def test_counts_only_treats_a_string_as_one_refusal_not_a_character_walk() -> None:
    """A string is Iterable, and iterating it would measure the wrong thing.

    Handed a name where a list belongs, a character walk yields one refusal per
    LETTER -- twenty-seven substituted zeros positionally aligned against an
    alphabet of thirteen. Refusing the whole value once says what happened.
    """
    from linkedin_server.coerce import counts_only

    values, refused = counts_only(PLANT)
    assert values == []
    assert refused == 1
    assert counts_only(None) == ([], 0)




def test_the_laundered_exception_detector_fires_and_discriminates() -> None:
    """It must catch a caught-and-returned coercion failure, and nothing else.

    BOTH DIRECTIONS, because a detector that fires on everything is as useless
    as one that fires on nothing. The negative case is a field holding ordinary
    page text -- which is `returns_text`, a contract, and must NOT be convicted
    here or 39 working readers go red.
    """
    real_message = ""
    try:
        int(PLANT)
    except ValueError as exc:
        real_message = f"{type(exc).__name__}: {exc}"

    assert real_message, "int() stopped raising; this whole guard is moot"

    # POSITIVE: the message a caught coercion produces, in an output field.
    assert carries_a_laundered_exception({"error": real_message})
    assert carries_a_laundered_exception({"rows": [{"why": real_message}]})

    # NEGATIVE: page text in a contract field is not a laundered exception.
    assert not carries_a_laundered_exception({"label": PLANT})
    assert not carries_a_laundered_exception({"shape": PLANT, "controls_read": 0})
    assert not carries_a_laundered_exception({})


def test_a_reader_that_launders_a_coercion_failure_is_called_a_leak() -> None:
    """End to end, through `drive`, on a reader written to have the defect.

    The detector being correct is not the same as the guard CONSULTING it, and
    a check wired in the wrong order is a check that does not run. This drives a
    synthetic reader with exactly the shape `dom.py` uses at 18 sites --
    `except Exception as exc: out["error"] = f"{type(exc).__name__}: {exc}"` --
    around a coercion of page data, and requires the verdict to be LEAKS rather
    than the `returns_text` it would otherwise earn.
    """

    async def laundering_reader(page: Any) -> dict[str, Any]:
        out: dict[str, Any] = {"count": 0, "error": None}
        try:
            raw = await page.evaluate("<script>")
            out["count"] = int(raw.get("total"))
        except Exception as exc:  # noqa: BLE001 - the defect, on purpose
            out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    verdict, detail = drive(laundering_reader)
    assert verdict == LEAKS, (
        f"the guard let a caught-and-returned coercion failure through as "
        f"{verdict!r} ({detail}). A name that leaves through a caught exception "
        f"has still left."
    )


# ---------------------------------------------------------------------------
# THE CHANNEL A FAILING LIBRARY OPENS -- an exception's text in a returned field
#
# Added 2026-09-24 (lane G). ``carries_a_laundered_exception`` above catches one
# shape of this: a COERCION's message, recognised by its wording. It could not
# see the rest, and lane L4 measured the rest: readers in ``dom.py`` writing
# ``f"{type(exc).__name__}: {exc}"`` into an ``error`` or ``why`` field, and
# four write gates printing that field in their refusal reasons. What a
# Playwright failure quotes -- a selector carrying his needle, a request, a
# JSON snippet of the page -- carries no signature to recognise.
#
# So this does not recognise anything. It drives every reader against
# ``plantedpage.RaisingPage``, where EVERY read fails quoting
# ``RAISED_PLANT``, and hunts that marker in what the reader RETURNS. No read
# can return it, so a return value carrying it carries an exception's text,
# whatever the syntax -- ``str(exc)``, ``repr(exc)``, ``exc.args``, ``%s``.
#
# THE RAISE IS NOT JUDGED HERE. A reader that lets the failure propagate is
# the ``$.message`` channel, ruled at the raise by
# ``ERROR-MESSAGE-RULED-AT-THE-RAISE``, and the twelve ``dom.py`` raise sites
# keep their messages by that ruling. ``raises`` is recorded, never failed.
# ---------------------------------------------------------------------------

#: A returned value carried what a failing library said. The only failure.
LAUNDERS = "launders"

#: Every variant let the failure propagate: the ruled channel, not this one.
RAISES = "raises"

#: READERS STILL LAUNDERING, DECLARED RATHER THAN WAIVED. Asserted EXACTLY in
#: both directions, so a new launderer fails naming itself and a repaired one
#: fails until its entry goes -- the mechanism ``KNOWN_DERIVED_NAVIGATIONS``
#: uses.
#:
#: **EMPTY SINCE THE LANE G FOLLOW-UP OF 2026-09-24.** Measured that day: 24
#: readers laundered before the ``dom.py`` repair -- ten in ``dom.py``, eight in
#: ``writes.py`` and one in ``server.py`` that only CARRY a ``dom.py`` field
#: onward (the four write gates among them), plus five in other modules, which
#: were declared here for one merge. Those five -- ``events.read_events_home``,
#: ``job_collections.read_job_collection``,
#: ``newsletters.read_newsletter_subscriptions``,
#: ``notify_cost.read_notifications_badge`` (two handlers) and
#: ``premium.read_premium_surface`` -- took the same repair the next morning:
#: the exception's TYPE and nothing else. Leave it empty; an entry added here
#: has to carry an argument that type-only is wrong for its site.
KNOWN_LAUNDERERS: dict[str, str] = {}

#: THE FAILING PAGE MUST REACH HANDLERS, or every verdict above is vacuous: a
#: reader that raises before its handler is ``raises``, not ``clean``. The
#: number of readers that RETURNED under it, measured 2026-09-24 after the
#: repair -- 78 of 126 (clean 73, launders 5; raises 47, not driven 1); a
#: floor, so it may rise freely and may fall only with a reason.
FAILING_PAGE_RETURNED_FLOOR = 78


def _with_the_failing_page(values: list[Any]) -> list[Any]:
    return [RaisingPage() if type(v) is PlantedPage else v for v in values]


#: EVERY LOG RECORD THE ``linkedin`` LOGGER EMITTED DURING THE CURRENT DRIVE,
#: captured at DEBUG. A LOG RECORD IS ANOTHER WAY OUT OF THE PROCESS: the
#: server's stderr is redirected to a file on disk by ``scripts/start_server.ps1``
#: and DEBUG is the level one sets to diagnose. Measured where they land before
#: this was added -- see ``tests/test_no_log_record_carries_a_library_message.py``.
_DRIVE_LOG: list[str] = []


class _CollectRecords(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            _DRIVE_LOG.append(record.getMessage())
        except Exception:  # noqa: BLE001 -- an unformattable record still counts
            _DRIVE_LOG.append(repr(record.msg) + repr(record.args))


#: THE PACKAGE'S LOGGERS: ``linkedin``, which ``config`` names and most modules
#: import, and the MODULE-NAMED ones under ``linkedin_server`` (``threads``
#: logs through ``getLogger(__name__)``). Each is heard at DEBUG while a reader
#: is driven -- the second was deaf until 2026-09-28: it inherits the root's
#: WARNING, so its DEBUG records never reached a handler.
PACKAGE_LOGGERS = ("linkedin", "linkedin_server")


def _drive_failing_once(
    fn: Callable[..., Any], args: list[Any], kwargs: dict[str, Any]
) -> tuple[str, str]:
    handler = _CollectRecords(level=logging.DEBUG)
    saved = []
    for name in PACKAGE_LOGGERS:
        log = logging.getLogger(name)
        saved.append((log, log.level))
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)
    try:
        return _drive_failing_once_logged(fn, args, kwargs)
    finally:
        for log, level in saved:
            log.removeHandler(handler)
            log.setLevel(level)


def _drive_failing_once_logged(
    fn: Callable[..., Any], args: list[Any], kwargs: dict[str, Any]
) -> tuple[str, str]:
    async def _run() -> Any:
        # OBSERVATIONS ARE RESOLVED ON THE ORDINARY PAGE FIRST, and then the
        # reader's own page is swapped. An Observation is a PRIOR reading; built
        # on the failing page it would raise before the reader ran a line.
        call_args, call_kwargs = await resolve_paired_observations(args, kwargs)
        call_args = _with_the_failing_page(call_args)
        call_kwargs = dict(
            zip(call_kwargs, _with_the_failing_page(list(call_kwargs.values())))
        )
        return await asyncio.wait_for(
            fn(*call_args, **call_kwargs), timeout=DRIVE_TIMEOUT_S
        )

    try:
        result = asyncio.run(_run())
    except NavigationAttempted as exc:
        return f"not_driven:navigates ({exc})", str(exc)
    except asyncio.TimeoutError:
        return f"not_driven:timed out after {DRIVE_TIMEOUT_S}s", ""
    except BaseException as exc:  # noqa: BLE001 -- the ruled channel, recorded
        return RAISES, type(exc).__name__
    hits = carries_the_raised_plant(result)
    if hits:
        return LAUNDERS, f"a failing library's message was returned at {hits[0]}"
    return CLEAN, ""


def drive_failing(fn: Callable[..., Any]) -> tuple[str, str]:
    """One reader against the failing page. ``(verdict, detail)``.

    The WORST variant decides, as in :func:`drive`: one variant returning the
    marker is the reader returning it. ``clean`` outranks ``raises`` because a
    variant that returned was measured, and one that raised was not.
    """
    variants, refusal = _build_call(fn)
    if variants is None:
        return f"not_driven:{refusal}", refusal
    order = {LAUNDERS: 3, CLEAN: 2, RAISES: 1}
    verdicts = [_drive_failing_once(fn, a, k) for a, k in variants]
    return max(verdicts, key=lambda v: order.get(v[0], 0))


_FAILING_VERDICTS: dict[str, tuple[str, str]] = {}

#: Per reader: how many log records emitted while it was driven carried what
#: the failing library said. A COUNT, so a red never prints a record.
_FAILING_LOG_HITS: dict[str, int] = {}


def failing_verdicts() -> dict[str, tuple[str, str]]:
    """Every discovered reader's verdict on the failing page, measured once.

    The same drive fills :data:`_FAILING_LOG_HITS`, so the log check costs no
    second pass over the readers.
    """
    if not _FAILING_VERDICTS:
        for name, fn in discover_readers():
            _DRIVE_LOG.clear()
            _FAILING_VERDICTS[name] = drive_failing(fn)
            _FAILING_LOG_HITS[name] = sum(RAISED_PLANT in m for m in _DRIVE_LOG)
    return _FAILING_VERDICTS


@pytest.mark.parametrize("name", [n for n, _ in discover_readers()])
def test_no_reader_logs_what_a_failing_library_said(name: str) -> None:
    """THE SAME DRIVE, READ FOR LOG RECORDS rather than for the return value."""
    failing_verdicts()
    hits = _FAILING_LOG_HITS[name]
    assert hits == 0, (
        f"{name} emitted {hits} log record(s) carrying what a failing library "
        "said, captured at DEBUG. Log type(exc).__name__ and name the step in "
        "the call's own words; a library's message can quote a selector, a "
        "request or an address, and stderr is a file on disk."
    )


def test_the_log_capture_sees_a_record_it_was_not_shown() -> None:
    """SHOWN FAILING: a reader that logs the message is counted, one that logs
    the type is not -- through the real capture, not a copy of it."""
    import logging as _logging

    log = _logging.getLogger("linkedin")

    async def logs_the_message(page: Any) -> dict[str, Any]:
        try:
            await page.locator("x").count()
        except Exception as exc:  # noqa: BLE001 - the defect, on purpose
            log.debug("read failed: %s: %s", type(exc).__name__, exc)
        return {}

    async def logs_the_type(page: Any) -> dict[str, Any]:
        try:
            await page.locator("x").count()
        except Exception as exc:  # noqa: BLE001
            log.debug("read failed: %s", type(exc).__name__)
        return {}

    _DRIVE_LOG.clear()
    drive_failing(logs_the_message)
    assert sum(RAISED_PLANT in m for m in _DRIVE_LOG) == 1, len(_DRIVE_LOG)
    _DRIVE_LOG.clear()
    drive_failing(logs_the_type)
    assert _DRIVE_LOG and sum(RAISED_PLANT in m for m in _DRIVE_LOG) == 0


def test_the_log_capture_hears_a_module_named_logger_too() -> None:
    """NOT ONLY ``linkedin`` (2026-09-28, lane G item 4's census). One module,
    ``threads``, logs through ``getLogger(__name__)`` -- ``linkedin_server.
    threads``, which is not under ``linkedin`` and sits at the root's level,
    WARNING, so its DEBUG records were dropped before any handler: a reader
    logging a failing library's message there was counted zero times.
    Measured: planted on ``linkedin`` it was counted once; on the module's
    logger, never."""
    import logging as _logging

    log = _logging.getLogger("linkedin_server.threads")

    async def logs_the_message_by_module(page: Any) -> dict[str, Any]:
        try:
            await page.locator("x").count()
        except Exception as exc:  # noqa: BLE001 - the defect, on purpose
            log.debug("read failed: %s: %s", type(exc).__name__, exc)
        return {}

    _DRIVE_LOG.clear()
    drive_failing(logs_the_message_by_module)
    assert sum(RAISED_PLANT in m for m in _DRIVE_LOG) == 1, len(_DRIVE_LOG)


@pytest.mark.parametrize("name", [n for n, _ in discover_readers()])
def test_no_reader_returns_what_a_failing_library_said(name: str) -> None:
    verdict, detail = failing_verdicts()[name]
    if name in KNOWN_LAUNDERERS:
        assert verdict == LAUNDERS, (
            f"{name} is declared in KNOWN_LAUNDERERS and no longer launders "
            f"({verdict}). If it was repaired, delete its entry -- the record "
            "of a defect may not outlive the defect."
        )
        return
    assert verdict != LAUNDERS, (
        f"{name} returned what a failing library said: {detail}. The field is "
        "decided where the value enters it (ERROR-MESSAGE-RULED-AT-THE-RAISE): "
        "write the exception's TYPE, or a reason this package composed, never "
        "str(exc). A write gate that prints the field prints whatever it holds."
    )


def test_the_failing_page_reached_the_handlers() -> None:
    returned = sorted(
        n for n, (v, _) in failing_verdicts().items() if v in {CLEAN, LAUNDERS}
    )
    assert len(returned) >= FAILING_PAGE_RETURNED_FLOOR, (
        f"only {len(returned)} readers returned under the failing page, below "
        f"the floor of {FAILING_PAGE_RETURNED_FLOOR}. A reader that raises "
        "before its handler is not measured by this rule, so a falling count "
        "is coverage leaving silently."
    )


def test_the_failing_page_fails_every_read_and_refuses_every_action() -> None:
    """THE DOUBLE, CONTROLLED. A read that quietly answers would let a reader
    reach a return without its handler ever running, and read as clean."""
    from tests import plantedpage

    async def _probe() -> None:
        for cls, instance in (
            (PlantedPage, RaisingPage()),
            (plantedpage.PlantedLocator, RaisingLocator()),
        ):
            reads = plantedpage._async_reads(cls)
            assert len(reads) >= 8, (cls.__name__, reads)
            for name in reads:
                with pytest.raises(PlantedLibraryError) as caught:
                    await getattr(instance, name)("x")
                assert RAISED_PLANT in str(caught.value), name
        with pytest.raises(NavigationAttempted):
            await RaisingPage().goto("x")
        with pytest.raises(NavigationAttempted):
            await RaisingLocator().click()
        assert await RaisingPage().wait_for_timeout(1) is None

    asyncio.run(_probe())
    assert RAISED_PLANT not in PLANT and PLANT not in RAISED_PLANT
    assert RAISED_PLANT not in SYNTHETIC_ARGUMENT
    assert SYNTHETIC_ARGUMENT not in RAISED_PLANT


@pytest.mark.parametrize(
    "render",
    [
        lambda exc: f"{type(exc).__name__}: {exc}",
        lambda exc: str(exc),
        lambda exc: repr(exc),
        lambda exc: exc.args[0],
        lambda exc: "failed (%s)" % (exc,),
    ],
    ids=["dom-shape", "str", "repr", "args", "percent"],
)
def test_a_reader_returning_a_libraries_message_is_convicted(render: Any) -> None:
    """SHOWN FAILING, and on the form rather than the spelling: all five."""

    async def laundering_reader(page: Any) -> dict[str, Any]:
        out: dict[str, Any] = {"count": 0, "error": None}
        try:
            out["count"] = await page.locator("x").count()
        except Exception as exc:  # noqa: BLE001 - the defect, on purpose
            out["error"] = render(exc)
        return out

    verdict, detail = drive_failing(laundering_reader)
    assert verdict == LAUNDERS, (verdict, detail)


def test_the_type_and_the_raise_are_not_convicted() -> None:
    """The other direction: the repair must stay writable, and the ruled
    channel must stay out of this rule's reach."""

    async def type_only(page: Any) -> dict[str, Any]:
        out: dict[str, Any] = {"count": 0, "error": None}
        try:
            out["count"] = await page.locator("x").count()
        except Exception as exc:  # noqa: BLE001
            out["error"] = type(exc).__name__
        return out

    async def raises_with_it(page: Any) -> dict[str, Any]:
        try:
            await page.evaluate("x")
        except Exception as exc:
            raise RuntimeError(f"could not read the page: {exc}") from exc
        return {}

    assert drive_failing(type_only)[0] == CLEAN
    assert drive_failing(raises_with_it)[0] == RAISES


def test_the_radio_binding_reader_is_driven_through_its_library_path() -> None:
    """ONE READER THE FAMILY CANNOT DISCRIMINATE, driven the way it ships.

    ``dom.read_radio_label_binding`` rendered the exception into its ``why``
    at two sites. In the family above it is ``clean`` for the wrong reason:
    the harness hands ``role`` the synthetic argument, ``named_role_selector``
    refuses that before any read, and the handler returns a message this
    package composed -- the library path never runs, before a repair or after.
    Its one shipped caller, ``writes._live_control``, passes ``"radio"`` and
    nothing else, so that is what this passes.
    """
    from linkedin_server import dom

    async def as_shipped(page: Any, name: str) -> dict[str, Any]:
        return await dom.read_radio_label_binding(page, "radio", name)

    verdict, detail = drive_failing(as_shipped)
    assert verdict == CLEAN, (verdict, detail)
    reading = asyncio.run(
        dom.read_radio_label_binding(RaisingPage(), "radio", SYNTHETIC_ARGUMENT)
    )
    assert "PlantedLibraryError" in reading["why"], (
        "the handler was not reached through a failing read, so the verdict "
        f"above measured nothing: {reading['why']!r}"
    )


# ---------------------------------------------------------------------------
# Refreshing the baseline
# ---------------------------------------------------------------------------


def write_baseline() -> int:
    """Rewrite :data:`BASELINE_PATH` from a live measurement. Prints the table.

    Run it deliberately, never from a test. A baseline a test refreshes on its
    own is a baseline that records whatever the tree currently does, which is
    the opposite of a baseline -- a reader that started leaking would rewrite
    the file that was supposed to notice.

        venv/Scripts/python -m tests.test_readers_emit_no_page_string --write-baseline

    NOTHING THAT LEAKS MAY BE WRITTEN INTO IT. A leak is a defect to repair,
    not a state to record, and a file holding ``"x": "leaks"`` would turn the
    guard into a list of permitted leaks within one commit of somebody being in
    a hurry. This refuses instead, and names them.
    """
    rows = measure()
    leaking = sorted(n for n, (v, _) in rows.items() if v == LEAKS)
    if leaking:
        print(f"REFUSED: {len(leaking)} reader(s) are leaking. A baseline is")
        print("not where a leak is recorded -- repair them first:")
        for name in leaking:
            print(f"  {name}  {rows[name][1]}")
        return 1
    # NOR IS IT WHERE A NEW PAGE-TEXT PATH IS RECORDED (2026-09-24). The text
    # inventory is the one committed before this rule, and it only shrinks.
    new_text = text_paths_a_baseline_may_not_record(
        _baseline(), {name: verdict for name, (verdict, _) in rows.items()}, ADMITTED_TEXT
    )
    if new_text:
        print(f"REFUSED: {len(new_text)} reader(s) return page text outside a")
        print("people record and the committed baseline does not already say so.")
        print("A page string leaves only through linkedin_server.people_data:")
        for name in new_text:
            print(f"  {name}")
        return 1

    payload = {
        "_comment": (
            "Verdict per page reader, from tests/plantedpage.py. Regenerate "
            "with: python -m tests.test_readers_emit_no_page_string "
            "--write-baseline. 'clean' means the reader was DRIVEN -- it read "
            "the page and returned something that is not an empty shape -- and "
            "carried nothing out; 'returns_records' means page text came back ONLY "
            "inside linkedin_server.people_data records, the declared channel; "
            "'returns_text' means page text came back outside a record -- a "
            "legacy inventory since 2026-09-24 that may shrink and may not "
            "grow; 'not_driven:<reason>' means this offline harness could not "
            "reach it, which is never a pass."
        ),
        "readers": {name: verdict for name, (verdict, _) in sorted(rows.items())},
    }
    BASELINE_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )

    counts: dict[str, int] = {}
    for verdict, _ in rows.values():
        key = verdict.split(":")[0]
        counts[key] = counts.get(key, 0) + 1
    print(f"wrote {BASELINE_PATH} -- {len(rows)} readers")
    for key, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {key:14s} {count:4d}")
    return 0


def _sandbox_the_session_store(directory: Any) -> None:
    """Point the session store at a throwaway path, as ``tests/conftest.py``
    does for every test. The baseline writer runs OUTSIDE pytest, where that
    fixture does not apply, and it drives ``auth._arm_session_store`` -- whose
    success path writes the store. Unreachable today only because the planted
    page's ``context`` is ``None``: redirected rather than relied on."""
    from linkedin_server import browser as browser_module
    from linkedin_server import session_store as store_module

    sandbox = Path(directory) / "session.json"
    store_module.SESSION_PATH = sandbox
    browser_module.SESSION_STORE.path = sandbox


if __name__ == "__main__":
    import sys as _sys
    import tempfile as _tempfile

    if "--write-baseline" in _sys.argv:
        with _tempfile.TemporaryDirectory() as _scratch:
            _sandbox_the_session_store(_scratch)
            _status = write_baseline()
        raise SystemExit(_status)
    raise SystemExit(
        "usage: python -m tests.test_readers_emit_no_page_string --write-baseline"
    )
