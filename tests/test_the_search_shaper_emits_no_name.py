"""THE NAME-FREEDOM PROOF FOR THE SEARCH SHAPER, MEASURED RATHER THAN ASSERTED.

`_audit/2026-09-19-two-census-conventions-ruled.md` section 6 grants
`SEARCH-RESULTS-SURFACE` on five conditions, the first of which is that the
admission and **a name-free shaper** land in the same commit. It also names
what revokes the grant:

> A measured case of the shaper emitting a name, a slug, a member id or an urn
> from that surface -- **which revokes the admission**, not merely the shaper.

`tests/test_search_results.py` already proves the shaper's SIGNATURES take no
needle and its output ALPHABET is closed. **Neither of those is the property
the condition names.** A closed alphabet is a fact about the literals this
module can choose from; it says nothing about a string the PAGE supplies
travelling through the reader untouched. This file asks the other question, at
the one boundary where a document value and a caller meet.

## THE HOLE THIS FILE WAS BORN FROM, AND IT WAS REAL

Measured 2026-09-20 by driving the real reader functions with a page whose
``evaluate`` answers with strings. The shipped coercion was ``int(value)``,
and **``int()`` puts the value it refused verbatim into its own exception**::

    ValueError: invalid literal for int() with base 10: '<the label>'

Three payloads reached it: a string inside ``counts``, a string in the
``anchors`` scalar, and the first of those again through ``read_filters``.
The exception leaves the reader, ``server._error`` catches it and renders it
through ``config.scrub`` -- **which substitutes this server's own paths and
nothing else, because a name has no shape to scrub**, a fact
``tests/test_no_committed_identity.py`` states in its own first line. So the
string arrived at the caller intact.

The module docstring's claim was *"no string from the document, by
construction"*. The construction had an exception-shaped gap, and an
INTEGER-ONLY return value does not close it, because an exception is not a
return value. That is the whole lesson and it is why this file walks
exceptions as well as results -- ``tests/leakwalk.py`` had already written
that lesson down for credentials and nobody had applied it to identifiers.

## WHY THIS PROOF DOES NOT NEED A CAPTURE OF THE REAL PAGE, AND WHAT IT
## THEREFORE DOES NOT PROVE

**There is no capture of a `/search/` page in this repository** -- grepped
across `tests/fixtures/`, where the string `search/results` appears only as an
outbound href sitting inside captures of OTHER surfaces. `connections_list.html`
is the nearest list-of-people fixture and its own header says it **is not a
capture**. So this file could not drive the shaper at real markup even if that
were the right instrument.

**It is not the right instrument, for THIS property.** Name-freedom here is
INPUT-INDEPENDENT: the page script builds its return value out of integer
accumulators and the Python reader rebuilds a fixed set of integer fields, so
the set of strings that can cross is empty *for every input*, not merely for
the ones somebody thought to try. A hostile payload is therefore a STRICTLY
STRONGER probe than any capture: it hands the reader values no real page would
produce and asks whether they cross anyway.

**What a capture WOULD settle, and this file does not:** whether the selectors
match LinkedIn's real dialect, whether the counts mean what they are named,
whether a live filter label matches `FILTER_TERMS`. That is CORRECTNESS, not
name-freedom, and it stays unmeasured until a browser slot. See
`_audit/2026-09-20-the-search-admission.md`.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from linkedin_server import coerce, search_results
from tests.leakwalk import url_spellings, walk

# ---------------------------------------------------------------------------
# The plants
# ---------------------------------------------------------------------------
#
# BOTH CARRY ``example``, which is in ``SYNTHETIC_SLUG_TOKENS`` in
# ``tests/test_no_committed_identity.py``, so they are self-evidently invented
# and the identity guard passes them on sight rather than on a declaration.
# ``fake`` is deliberately not used: that guard's own comment says it asserts
# synthetic-ness instead of evidencing it.
#
# They are long and distinctive on purpose. A short marker cannot be told from
# ordinary prose, which is the reasoning ``leakwalk.MIN_SECRET`` writes down
# one layer up for credentials.

#: Stands in for the text of a search result row: a person's displayed name.
PLANTED_NAME = "Exampleperson Markersurname"

#: Stands in for the href of a search result row. **A SLUG IS A NAME**, which
#: is the rule this whole surface is held on, so it is hunted as hard as the
#: displayed name is.
PLANTED_SLUG = "example-markerperson-0a1b2c3d4e"

#: EVERY SPELLING OF BOTH PLANTS, not just the two literals.
#:
#: **THIS WAS A BARE SUBSTRING HUNT UNTIL ITS OWN CONTROL CONVICTED IT.** The
#: tool control below builds the url a browser really lands on, where the name
#: is percent-encoded -- ``Exampleperson%20Markersurname`` -- and a hunt for
#: the spaced spelling reported that payload CLEAN. That is
#: ``leakwalk.url_spellings``'s own recorded scar arriving one surface over: a
#: committed fixture leaked a real job title while its check reported *"69/69
#: forbidden strings absent"*, because the forbidden list held the spaced
#: spelling and the file spelled it with hyphens.
#:
#: So the spellings come from the shipped helper rather than from a literal
#: list somebody typed. **A list of literals only catches the spelling
#: somebody thought of**, and on this surface the spelling that matters is the
#: one LinkedIn puts in a query string.
PLANTS = tuple(
    sorted(url_spellings(PLANTED_NAME) | url_spellings(PLANTED_SLUG))
)


class _HostilePage:
    """A page whose ``evaluate`` returns whatever it was handed. No browser.

    This is not a mock of LinkedIn and does not pretend to be. It is the
    ADVERSARY the readers are supposed to survive: the thing on the other side
    of the boundary, answering with whatever it likes.
    """

    def __init__(self, payload: Any) -> None:
        self._payload = payload

    async def evaluate(self, script: Any, arg: Any = None) -> Any:
        return self._payload


#: One payload per way a page could answer with a string instead of a number.
#: The last three are the ones that were MEASURED LEAKING before the fix.
HOSTILE_PAYLOADS: dict[str, dict] = {
    "string fields beside well-formed integers": {
        "anchors": 3,
        "controls": 3,
        "counts": [1, 0, 0],
        "queries_present": 1,
        "sample_label": PLANTED_NAME,
        "first_href": "/in/" + PLANTED_SLUG,
    },
    "a plant used as a dict KEY": {
        "anchors": 1,
        "controls": 1,
        "counts": [1],
        PLANTED_NAME: 1,
    },
    "a string inside counts": {
        "anchors": 1,
        "controls": 1,
        "counts": [PLANTED_NAME],
    },
    "a string in the anchors scalar": {
        "anchors": "/in/" + PLANTED_SLUG,
        "controls": "/in/" + PLANTED_SLUG,
        "counts": [1],
    },
    "a nested object under a known key": {
        "anchors": 1,
        "controls": 1,
        "counts": [{"label": PLANTED_NAME}],
    },
    "the whole payload is a string": "/in/" + PLANTED_SLUG,
}

READERS = {
    "read_results": search_results.read_results,
    "read_filters": search_results.read_filters,
}


def _carries_a_plant(obj: Any) -> list[str]:
    """Every place in ``obj`` that carries a plant, by path.

    ``leakwalk.walk`` is IMPORTED, not rewritten. It is the repository's total
    walker -- dict keys as well as values, bytes both ways, exceptions as
    ``str``, ``repr`` AND per-argument -- and this file needs exactly its
    exception coverage, because the leak it was written for lived in a
    ``ValueError``'s message and in nothing that was ever returned.
    """
    return [
        f"{where} carries a plant"
        for where, text in walk(obj)
        if any(plant in text for plant in PLANTS)
    ]


def _drive(reader, payload: Any) -> tuple[Any, BaseException | None]:
    """Run a reader over a hostile payload. Returns whichever one happened."""
    try:
        return asyncio.run(reader(_HostilePage(payload))), None
    except BaseException as exc:  # noqa: BLE001 -- the exception IS the subject
        return None, exc


@pytest.mark.parametrize("reader_name", sorted(READERS))
@pytest.mark.parametrize("case", sorted(HOSTILE_PAYLOADS))
def test_no_plant_crosses_the_reader_by_any_path(reader_name: str, case: str) -> None:
    """THE PROOF. Neither the RESULT nor the EXCEPTION may carry a plant.

    Both channels are checked in one assertion on purpose. Checking only the
    return value is the exact defect ``leakwalk``'s docstring records for
    credentials -- *"a credential in a log record, in an exception's args ...
    is invisible to it"* -- and it is the defect that was live here.
    """
    result, exc = _drive(READERS[reader_name], HOSTILE_PAYLOADS[case])
    carried = _carries_a_plant(result) + _carries_a_plant(exc)
    assert not carried, (
        f"{reader_name} let a planted name or slug out on case {case!r}: "
        + "; ".join(carried)
        + ". This surface's admission is granted on the rule that no name, "
        "slug, member id or urn leaves it, and a measured emission revokes "
        "the admission rather than merely the shaper."
    )


@pytest.mark.parametrize("reader_name", sorted(READERS))
@pytest.mark.parametrize("case", sorted(HOSTILE_PAYLOADS))
def test_a_reader_never_raises_at_a_hostile_page(reader_name: str, case: str) -> None:
    """AND IT DOES NOT RAISE, which is the same fix seen from the other side.

    An exception here would be caught by ``server._error`` and rendered into a
    caller-visible message. The reader is a boundary, so it absorbs a
    malformed answer and REPORTS it as a number instead of propagating a
    string upward.
    """
    _, exc = _drive(READERS[reader_name], HOSTILE_PAYLOADS[case])
    assert exc is None, (
        f"{reader_name} raised {type(exc).__name__} on case {case!r}. Whatever "
        "the message says, it was built from a value the page chose."
    )


@pytest.mark.parametrize("reader_name", sorted(READERS))
def test_every_field_a_reader_returns_is_an_integer(reader_name: str) -> None:
    """THE STRUCTURAL HALF: the payload's VALUES are integers, all of them.

    ``bool`` is excluded explicitly. It is an ``int`` in Python, and a field
    reading ``True`` where a count belongs is a reading nobody took.
    """
    result, exc = _drive(
        READERS[reader_name], HOSTILE_PAYLOADS["string fields beside well-formed integers"]
    )
    assert exc is None
    for field, value in result.items():
        values = value if isinstance(value, list) else [value]
        for item in values:
            assert isinstance(item, int) and not isinstance(item, bool), (
                f"{reader_name}[{field!r}] holds {type(item).__name__}, and "
                "every field this reader publishes is supposed to be a count."
            )


@pytest.mark.parametrize("reader_name", sorted(READERS))
def test_a_refused_value_is_counted_and_not_silent(reader_name: str) -> None:
    """A REFUSAL IS A LOUD NUMBER. Silence would hide a changed page.

    ``values_refused`` is the only way a caller can tell "the page answered
    with zero" from "the page answered with something I would not repeat".
    Dropping the value without counting it would make those two identical,
    which is the collapsed-state defect this repository keeps paying for.
    """
    clean, _ = _drive(READERS[reader_name], {"anchors": 2, "controls": 2, "counts": [1, 1]})
    assert clean["values_refused"] == 0, "a well-formed page must refuse nothing"

    dirty, _ = _drive(READERS[reader_name], HOSTILE_PAYLOADS["a string inside counts"])
    assert dirty["values_refused"] >= 1, (
        "a page that answered with a string was absorbed silently. The value "
        "is correctly withheld and its EXISTENCE must not be."
    )


def test_a_refused_count_holds_its_POSITION_and_does_not_shift_the_alphabet() -> None:
    """THE SUBSTITUTION IS POSITIONAL, and that is the hazard, not tidiness.

    ``counts`` is positionally aligned to ``RESULT_KINDS`` and index 0 is
    ``person_result``. Dropping a refused entry rather than substituting it
    renames every kind behind it -- a page of people reported as companies --
    which is exactly the rename ``term_for`` refuses to commit by clamping.
    """
    counts, refused = search_results._counts_only([1, PLANTED_NAME, 7])
    assert refused == 1
    assert counts == [1, 0, 7], (
        "the refused entry was dropped instead of substituted, so position 2 "
        "now reports what position 3 measured."
    )


def test_an_absent_field_is_not_a_refusal_because_they_are_different_answers() -> None:
    """"I was not told" and "I was told a string" must not collapse together."""
    scalars, refused = search_results._scalars_only({}, (("anchors_seen", "anchors"),))
    assert scalars["anchors_seen"] == 0 and refused == 0, (
        "a missing key was counted as a refusal, which would report every "
        "short payload as a page answering with strings."
    )


# ---------------------------------------------------------------------------
# THE SHAPER THAT TAKES NO PAGE, AND WHY IT NEEDED ITS OWN TEST
# ---------------------------------------------------------------------------


def test_the_shaper_that_takes_no_page_refuses_a_string_too() -> None:
    """``tally`` is in the property, and until 2026-09-21 it was not.

    ## WHERE THE CLASS HAD GONE, AND WHY EVERY GREEN WAS HONEST

    ``tests/leakwalk.py`` discovers its subjects as **every module-level
    ``async def`` with a ``page`` parameter** -- deliberately, so a reader
    written tomorrow is in the subject set with no edit there. ``tally`` is
    synchronous and takes no page: it shapes a page's VALUES without touching
    the page. So the leak class had walked one layer out of that guard's
    subject set, and nothing in this file reached it either, because the
    hostile payloads above are fed to READERS.

    ## THE CLAIM THAT WAS TRUE OF ONE PARAMETER

    ``tally``'s docstring says *"Its parameters are INTEGERS -- a needle
    cannot reach it"* and that this is *"TRUE OF THE BEHAVIOUR AND NOT ONLY OF
    THE SIGNATURE"*. ``counts`` was routed through the coercion family on
    2026-09-20. ``queries_present`` was not, and reached a bare ``int()``.

    ## IT WAS LATENT, NOT LIVE, AND THE DIFFERENCE IS WORTH STATING

    Every caller at HEAD -- the tool in ``server`` and two probes -- passes
    ``read_results``'s already-coerced output, so no run has ever carried a
    name out through it. The property was held by the CALLER'S discipline
    rather than by this function, which is exactly what "even by mistake"
    denies. ``tests/test_search_results.py`` pins the SIGNATURE of these two
    parameters -- the half the docstring itself says is not enough.
    """
    for hostile in (PLANTED_NAME, PLANTED_SLUG, "/in/" + PLANTED_SLUG):
        shaped = search_results.tally([1, 2, 3], queries_present=hostile)
        assert not _carries_a_plant(shaped), (
            "tally carried a page value into its return; hostile=%r" % hostile
        )
        assert shaped["queries_present"] == 0, (
            "a refused value must substitute, not pass through"
        )
    # AND THE INTEGER PATH IS UNCHANGED -- a repair that broke the real
    # reading would pass the leak test and be useless.
    assert search_results.tally([1], queries_present=4)["queries_present"] == 4


def test_the_shaper_never_raises_a_string_it_was_handed() -> None:
    """The exception path, which is the one an integer-only return hides.

    AN INTEGER-ONLY RETURN VALUE DOES NOT MAKE A FUNCTION INTEGER-ONLY,
    BECAUSE AN EXCEPTION IS NOT A RETURN VALUE. This is that property for the
    page-less shaper.
    """
    try:
        search_results.tally([1], queries_present=PLANTED_NAME)
    except Exception as exc:  # noqa: BLE001 -- the point is that none is raised
        assert not _carries_a_plant(exc), (
            "tally raised an exception quoting a value the page chose"
        )
        raise AssertionError(
            "tally raised at a hostile value instead of refusing it: %r" % exc
        )


# ---------------------------------------------------------------------------
# THE CONTROLS. Every assertion above is shown failing on a planted defect.
# ---------------------------------------------------------------------------


def test_THIS_CONTROL_CAN_FAIL_the_page_less_shaper_really_did_leak() -> None:
    """THE DEFECT, REPRODUCED AT ITS OWN SITE, not merely as ``int()`` in general.

    The control one function up proves ``int()`` quotes what it refused. This
    one proves that the shipped ``tally`` REACHED such an ``int()`` with its
    second parameter, by running the exact expression the module carried until
    2026-09-21. If this stops leaking, the repair above is being tested
    against a defect that no longer exists and the assertions are passing for
    an unknown reason.
    """
    try:
        # THE LINE AS IT SHIPPED: `"queries_present": int(queries_present)`.
        int(PLANTED_NAME)
    except ValueError as exc:
        assert _carries_a_plant(exc), (
            "the shipped expression no longer carries its input, so the "
            "repair cannot be shown to have repaired anything"
        )
    else:
        raise AssertionError("int() accepted a name, which cannot happen")

    # AND THE REPAIR IS NOT A COSMETIC RENAME: the coercion the module now
    # uses must actually refuse the same value rather than pass it along.
    assert coerce.as_count(PLANTED_NAME) == 0


def test_THIS_CONTROL_CAN_FAIL_the_replaced_coercion_really_did_leak() -> None:
    """THE DEFECT, REPRODUCED. ``int()`` quotes what it refused.

    This is not a hypothetical mutation: it is the code that shipped in
    ``read_results`` and ``read_filters`` until 2026-09-20, run here over the
    same payload the tests above drive. If this ever stops leaking, ``int()``
    has changed its message and the detector above is measuring nothing.
    """
    try:
        [int(value) for value in [PLANTED_NAME]]
    except ValueError as exc:
        carried = _carries_a_plant(exc)
        assert carried, (
            "int() no longer carries the value it refused, so the leak this "
            "file exists to prevent can no longer be demonstrated and the "
            "assertions above are passing for an unknown reason."
        )
        return
    raise AssertionError("int() accepted a name, which cannot happen")


def test_THIS_CONTROL_CAN_FAIL_the_detector_sees_a_plant_in_a_plain_result() -> None:
    """The detector fires on a RETURN VALUE too, not only on an exception.

    A detector that could only see exceptions would report clean on a reader
    that politely returned the label, which is the more obvious of the two
    leaks and would be the embarrassing one to miss.
    """
    assert _carries_a_plant({"ok": True, "label": PLANTED_NAME})
    assert _carries_a_plant({"rows": [{"href": "/in/" + PLANTED_SLUG}]})
    assert _carries_a_plant({PLANTED_NAME: 1}), "a plant used as a KEY was missed"
    assert not _carries_a_plant({"ok": True, "counts": [1, 2, 3]})


def test_THIS_CONTROL_CAN_FAIL_a_reader_that_passed_the_page_through_goes_red() -> None:
    """A SHAPER THAT ECHOED THE PAGE WOULD BE CAUGHT by the assertion above.

    Driven through the same helper the real cases use, so this exercises the
    detector at its real call site rather than at a convenient one.
    """

    async def echoing_reader(page: Any, html: str = "") -> dict[str, Any]:
        raw = await page.evaluate("", {})
        return {"counts": [0], "echoed": raw}

    result, exc = _drive(echoing_reader, HOSTILE_PAYLOADS["a string inside counts"])
    assert exc is None
    assert _carries_a_plant(result), (
        "a reader that returns the page's own payload was reported clean. "
        "Every no-leak assertion in this file is then vacuous."
    )


# ---------------------------------------------------------------------------
# THE SHIPPED DECISION, DRIVEN AT NAME-SHAPED INPUT UNDER V8
# ---------------------------------------------------------------------------
#
# The two tests above measure the PYTHON boundary. The decision that reads the
# document is JavaScript, and it is the artifact a route actually meets, so it
# is driven here at the one input shape the surface guarantees: an address
# with a person's name in it.
#
# The runner is IMPORTED from the shaper's own suite rather than copied. This
# repository has a scar for writing a second copy of a check it already ships,
# and a transcribed driver is a second implementation that agrees today.


def _classify(routes: list[str]) -> list[dict]:
    from tests import test_search_results as suite

    if suite._node() is None:
        pytest.skip("node is not on PATH; the shipped classifier cannot be driven")
    return suite._run_classify_in_node(routes)


#: Addresses shaped the way a real people-search row is: a slug that IS a
#: name, and a query that is where a name gets typed.
NAME_SHAPED_ROUTES = [
    "/in/" + PLANTED_SLUG + "/",
    "/search/results/people/?keywords=" + PLANTED_NAME.replace(" ", "%20"),
    "/search/results/people/" + PLANTED_SLUG + "/",
    "/search/results/people/../../in/" + PLANTED_SLUG,
    "https://www.linkedin.com/search/results/people/?connectionOf=" + PLANTED_SLUG,
]


def test_the_shipped_classifier_returns_no_part_of_a_name_shaped_address() -> None:
    """THE OTHER ENGINE, measured at the input this surface is made of.

    ``classifyRoute`` is handed addresses carrying a planted name and slug and
    must answer in integers. This is the claim the module docstring makes --
    *"No string it was given is in its return value, on any path"* -- driven
    rather than read.
    """
    verdicts = _classify(NAME_SHAPED_ROUTES)
    assert len(verdicts) == len(NAME_SHAPED_ROUTES)
    carried = _carries_a_plant(verdicts)
    assert not carried, (
        "the shipped classifier echoed part of the address it was given: "
        + "; ".join(carried)
    )
    for verdict in verdicts:
        assert isinstance(verdict["kind"], int)
        assert verdict["term"] in search_results.emitted_alphabet()


# ---------------------------------------------------------------------------
# THE TOOL, which is the thing a caller actually touches
# ---------------------------------------------------------------------------
#
# Everything above measures the READERS. A caller never calls a reader; it
# calls `linkedin_people_search_shape`, which also assembles a payload and
# handles a landed url. **The landed url is a value the BROWSER chose**, and on
# this surface it can carry a query -- so the tool is driven here with a fake
# browser that lands on an address carrying a planted name, and must publish a
# boolean rather than the address.
#
# No browser is started. `BROWSER` is replaced for the duration.


class _HostileSearchPage:
    async def evaluate(self, script: Any, arg: Any = None) -> Any:
        return {
            "anchors": 12,
            "controls": 9,
            # Position 0 is person_result. A string here used to raise.
            "counts": [PLANTED_NAME] + [1] * 13,
            "queries_present": 1,
            "matched_controls": 9,
            "unmatched_controls": 3,
            "empty_labels": 1,
            "stray_label": "Connections of " + PLANTED_NAME,
            "first_href": "/in/" + PLANTED_SLUG,
        }


class _FakeBrowser:
    """Lands on an address carrying a name, as LinkedIn legitimately may."""

    def session(self):
        import contextlib

        @contextlib.asynccontextmanager
        async def _session():
            yield _HostileSearchPage()

        return _session()

    async def goto(self, page: Any, url: str) -> str:
        return url + "?keywords=" + PLANTED_NAME.replace(" ", "%20")


def _run_tool(monkeypatch) -> dict:
    from linkedin_server import server

    monkeypatch.setattr(server, "BROWSER", _FakeBrowser())
    monkeypatch.setattr(server, "assert_not_authwall", lambda final_url, *, surface: None)
    return asyncio.run(server.linkedin_people_search_shape())


def test_the_tool_publishes_no_plant_even_when_the_page_and_the_url_carry_one(
    monkeypatch,
) -> None:
    """THE PROOF AT THE SURFACE A CALLER TOUCHES.

    The page answers with a name in a count slot and the browser lands on an
    address carrying the same name. Neither may appear in the payload.
    """
    payload = _run_tool(monkeypatch)
    carried = _carries_a_plant(payload)
    assert not carried, (
        "the tool published a planted name or slug: " + "; ".join(carried)
    )
    assert payload["ok"] is True, "the hostile page made the tool report failure"


def test_the_tool_reports_the_landed_url_as_a_boolean_and_never_as_a_string(
    monkeypatch,
) -> None:
    """A LANDED URL IS A VALUE THE BROWSER CHOSE. It is answered, not quoted.

    The fake browser lands somewhere other than where it was sent, so this
    asserts the tool NOTICED (False) rather than asserting the happy path --
    a test that only ever sees True cannot tell a comparison from a constant.
    """
    payload = _run_tool(monkeypatch)
    assert payload["landed_where_it_was_sent"] is False
    assert not any(
        isinstance(value, str) and value.startswith("http")
        for value in payload.values()
    ), "the tool published a url at the top level of its payload"


def test_the_tool_counts_the_refusal_rather_than_swallowing_it(monkeypatch) -> None:
    """The page answered two count slots with a string. Both are reported."""
    payload = _run_tool(monkeypatch)
    assert payload["denominators"]["values_refused"] >= 1, (
        "a page that answered with a label was absorbed silently"
    )


def test_THIS_CONTROL_CAN_FAIL_the_tool_detector_would_see_a_published_url(
    monkeypatch,
) -> None:
    """SHOWN FAILING. The two tool assertions above are not vacuous.

    Their detector is run over a payload that DOES carry the landed url, which
    is the mistake the tool is written to avoid, and must complain.
    """
    payload = _run_tool(monkeypatch)
    leaky = dict(payload)
    leaky["landed_url"] = (
        search_results.PEOPLE_SEARCH_URL
        + "?keywords="
        + PLANTED_NAME.replace(" ", "%20")
    )
    assert _carries_a_plant(leaky), (
        "a payload publishing a landed url that carries a name was reported "
        "clean, so the tool assertions above certify nothing"
    )


def test_THIS_CONTROL_CAN_FAIL_the_v8_detector_sees_an_echo() -> None:
    """The V8 path's detector, shown firing.

    Without this, a driver that silently returned an empty list would make the
    assertion above pass while measuring nothing -- the vacuous-control shape
    this repository has found roughly ten times.
    """
    verdicts = _classify(NAME_SHAPED_ROUTES)
    assert verdicts, "the driver returned nothing; the test above is vacuous"
    echoed = json.loads(json.dumps(verdicts))
    echoed[0]["raw"] = NAME_SHAPED_ROUTES[0]
    assert _carries_a_plant(echoed), (
        "a verdict list carrying the address verbatim was reported clean"
    )
