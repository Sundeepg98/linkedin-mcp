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
import importlib
import inspect
import json
import pkgutil
from pathlib import Path
from typing import Any, Callable, Optional

import pytest

import linkedin_server
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
    carries_the_raised_plant,
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
CLEAN = "clean"
LEAKS = "leaks"
RETURNS_TEXT = "returns_text"


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


def drive(fn: Callable[..., Any]) -> tuple[str, str]:
    """Run one reader against the planted page. ``(verdict, detail)``.

    The exception path is the SUBJECT, not an accident, so every ``BaseException``
    is caught and walked. A reader that raises is not thereby clean: the whole
    finding is that an exception carries values a return value would not.
    """
    variants, refusal = _build_call(fn)
    if variants is None:
        return f"not_driven:{refusal}", refusal

    verdicts = [_drive_once(fn, args, kwargs) for args, kwargs in variants]
    return _worst(verdicts)


def _drive_once(
    fn: Callable[..., Any], args: list[Any], kwargs: dict[str, Any]
) -> tuple[str, str]:
    async def _run() -> Any:
        call_args, call_kwargs = await resolve_paired_observations(args, kwargs)
        return await asyncio.wait_for(
            fn(*call_args, **call_kwargs), timeout=DRIVE_TIMEOUT_S
        )

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

    # CHECKED BEFORE ``returns_text``, because it IS a leak wearing its costume.
    # A caught coercion failure put into an output field has carried the value
    # out just as surely as a raise would have -- see
    # ``plantedpage.carries_a_laundered_exception``.
    laundered = carries_a_laundered_exception(result)
    if laundered:
        return LEAKS, f"a caught coercion failure was returned at {laundered[0]}"

    hits = carries_the_plant(result)
    if hits:
        return RETURNS_TEXT, f"returns page text at {hits[0]}"
    return CLEAN, ""


def _worst(verdicts: list[tuple[str, str]]) -> tuple[str, str]:
    """The most serious verdict across a reader's call variants.

    ONE VARIANT LEAKING IS THE READER LEAKING. A reader driven with thirteen
    shipped ``WriteSpec``s that carries a name out under one of them has the
    defect; the twelve that returned early prove only that they returned early.
    Ranking clean ABOVE not-driven is deliberate for the same reason in reverse
    -- if any variant actually ran and came back clean, the reader WAS measured,
    and reporting it as un-measurable would understate the coverage.
    """
    order = {LEAKS: 3, RETURNS_TEXT: 2, CLEAN: 1}
    best = max(verdicts, key=lambda v: order.get(v[0], 0))
    return best


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

    with caplog.at_level(logging.WARNING, logger="linkedin"):
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

#: READERS STILL LAUNDERING, DECLARED RATHER THAN WAIVED, and every entry is
#: in a module lane G does not own. Asserted EXACTLY in both directions, so a
#: new launderer fails naming itself and a repaired one fails until its entry
#: goes -- the mechanism ``KNOWN_DERIVED_NAVIGATIONS`` uses. Each is one
#: ``except Exception as exc`` writing ``f"{type(exc).__name__}: {exc}"`` into
#: a returned ``error`` field; the repair is the one ``dom.py`` took on
#: 2026-09-24, the exception's TYPE and nothing else.
#:
#: MEASURED 2026-09-24 on the lane-G branch: 24 readers laundered before the
#: ``dom.py`` repair -- ten in ``dom.py``, eight in ``writes.py`` and one in
#: ``server.py`` that only CARRY a ``dom.py`` field onward (the four write
#: gates among them), plus these five. After it, these five and no others.
KNOWN_LAUNDERERS: dict[str, str] = {
    "events:read_events_home": "events.read_events_home, its returned `error`",
    "job_collections:read_job_collection": (
        "job_collections.read_job_collection, its returned `error`"
    ),
    "newsletters:read_newsletter_subscriptions": (
        "newsletters.read_newsletter_subscriptions, its returned `error`"
    ),
    "notify_cost:read_notifications_badge": (
        "notify_cost.read_notifications_badge, its returned `error`, two handlers"
    ),
    "premium:read_premium_surface": "premium.read_premium_surface, its returned `error`",
}

#: THE FAILING PAGE MUST REACH HANDLERS, or every verdict above is vacuous: a
#: reader that raises before its handler is ``raises``, not ``clean``. The
#: number of readers that RETURNED under it, measured 2026-09-24 after the
#: repair -- 78 of 126 (clean 73, launders 5; raises 47, not driven 1); a
#: floor, so it may rise freely and may fall only with a reason.
FAILING_PAGE_RETURNED_FLOOR = 78


def _with_the_failing_page(values: list[Any]) -> list[Any]:
    return [RaisingPage() if type(v) is PlantedPage else v for v in values]


def _drive_failing_once(
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


def failing_verdicts() -> dict[str, tuple[str, str]]:
    """Every discovered reader's verdict on the failing page, measured once."""
    if not _FAILING_VERDICTS:
        for name, fn in discover_readers():
            _FAILING_VERDICTS[name] = drive_failing(fn)
    return _FAILING_VERDICTS


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

    payload = {
        "_comment": (
            "Verdict per page reader, from tests/plantedpage.py. Regenerate "
            "with: python -m tests.test_readers_emit_no_page_string "
            "--write-baseline. 'clean' means the reader was DRIVEN and carried "
            "nothing out; 'returns_text' means it returns page text by "
            "contract, which the shapers govern; 'not_driven:<reason>' means "
            "this offline harness could not reach it, which is never a pass."
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


if __name__ == "__main__":
    import sys as _sys

    if "--write-baseline" in _sys.argv:
        raise SystemExit(write_baseline())
    raise SystemExit(
        "usage: python -m tests.test_readers_emit_no_page_string --write-baseline"
    )
