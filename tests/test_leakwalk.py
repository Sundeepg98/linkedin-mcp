"""Controls for the leak walker itself.

``tests/leakwalk.py`` is the instrument every "no credential leaves this
process" assertion in the package now runs on. An instrument nobody has driven
at the thing it is supposed to catch certifies nothing -- this repo has the
receipts, twice, in the fixture privacy guard's own comments -- so every
detector in that module is driven here in BOTH directions:

* at a payload carrying the credential, where it must complain;
* at a payload carrying none, where it must stay silent.

The parametrised cases below mean the coverage is not a claim about a list
somebody remembered to update: the transform cases iterate
``credential_echo_control.TRANSFORMS`` and the rendering cases iterate
``leakwalk.renderings()``, so adding a spelling to either module adds its
control here automatically, and a spelling with no control cannot exist.
"""

from __future__ import annotations

import base64
import json
import logging
import sys
from pathlib import Path

import pytest

from tests import leakwalk
from tests.leakwalk import (
    PLANTED_JSESSIONID,
    PLANTED_LI_AT,
    assert_no_leak,
    find_credential_shaped,
    find_leaks,
    renderings,
    walk,
)

# The control plugin lives in scripts/, which is not on the path pytest.ini
# sets up (that is `.`). Importing it here rather than copying its transform
# list is the whole point: one list, two users, no drift.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from credential_echo_control import TRANSFORMS, inject  # noqa: E402

SECRET = PLANTED_LI_AT


# ---------------------------------------------------------------------------
# 0. The plant is credential-shaped, and stays that way
# ---------------------------------------------------------------------------


def test_the_planted_token_looks_like_the_thing_it_stands_in_for():
    """The defect this module was written for was the MARKER, not the hunt.

    A guard hunting ``"live"`` cannot catch a redaction bug that only fires on
    long high-entropy values, because it never presents one. So the plant has
    to keep looking like a real credential, and this is what stops it drifting
    back to a four-letter word.
    """
    assert leakwalk.LI_AT_SHAPE.fullmatch(PLANTED_LI_AT), PLANTED_LI_AT[:20]
    assert len(PLANTED_LI_AT) > 150
    assert len(PLANTED_LI_AT) >= leakwalk.MIN_SECRET
    assert leakwalk.JSESSIONID_SHAPE.search(PLANTED_JSESSIONID)


def test_a_marker_too_short_to_hunt_is_refused_rather_than_hunted_badly():
    """The failure mode of a run detector aimed at a short marker.

    ``"live"`` would fire on ``live_check``, which is a field name. Rather
    than quietly lowering the run length to fit, the hunt refuses.
    """
    with pytest.raises(AssertionError) as excinfo:
        find_leaks({"live_check": {"completed": False}}, "live")
    assert "too short to hunt" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 1. Every transform the leaking build can apply is caught
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("transform", TRANSFORMS)
def test_every_leaking_transform_is_caught(transform, caplog):
    """The control that gives the whole suite's leak assertions their teeth.

    One case per row of ``scripts/leak_matrix.py``. On the build this module
    replaced, five of these transforms produced no complaint at all.
    """
    payload = {"credential": {"present": True, "expires_in_days": 300}}
    with caplog.at_level(logging.DEBUG):
        leaked = inject(payload, SECRET, transform)

    extra = [caplog.text] + [r.getMessage() for r in caplog.records]
    assert find_leaks(leaked, SECRET, extra=extra), transform


@pytest.mark.parametrize("transform", TRANSFORMS)
def test_assert_no_leak_raises_on_every_leaking_transform(transform, caplog):
    """The same grid, through the assertion the tests actually call."""
    payload = {"credential": {"present": True}}
    with caplog.at_level(logging.DEBUG):
        leaked = inject(payload, SECRET, transform)
        with pytest.raises(AssertionError):
            assert_no_leak(leaked, SECRET, caplog=caplog)


@pytest.mark.parametrize("name", sorted(renderings(SECRET)))
def test_every_rendering_is_caught_on_its_own(name):
    """One case per spelling the walker knows, driven straight at that spelling.

    The transform grid above tests the LEAK; this tests the DETECTOR. They
    overlap deliberately -- a rendering with no leaking transform behind it
    would otherwise be untested.
    """
    rendered = renderings(SECRET)[name]
    leaks = find_leaks({"note": f"debug blob: {rendered}"}, SECRET)
    assert leaks, name


def test_the_exact_substring_hunt_this_replaced_calls_a_real_leak_clean():
    """The finding, written down as a test so it cannot be re-introduced.

    Both payloads below carry the operator's entire session cookie. The old
    one-line guard passes on both. This is the measurement behind the 34
    green cells in ``scripts/leak_matrix.py``'s first run.
    """
    b64 = base64.b64encode(SECRET.encode()).decode()
    half = len(SECRET) // 2
    for payload in (
        {"credential": {"fingerprint": b64}},
        {"credential": {"head": SECRET[:half], "tail": SECRET[half:]}},
    ):
        # The guard as it was written everywhere in this package.
        assert SECRET not in json.dumps(payload), "the old hunt saw it"
        # The guard as it is written now.
        assert find_leaks(payload, SECRET)


# ---------------------------------------------------------------------------
# 2. The walk reaches every hiding place
# ---------------------------------------------------------------------------


def test_the_walk_reaches_a_credential_used_as_a_dict_key():
    assert find_leaks({SECRET: "seen"}, SECRET)


def test_the_walk_reaches_bytes():
    """``json.dumps`` cannot even render these, so the old hunt never saw one."""
    assert find_leaks({"blob": SECRET.encode("utf-8")}, SECRET)


def test_the_walk_reaches_an_exceptions_arguments():
    """An exception is the single most common way a secret gets out."""
    assert find_leaks({"error": OSError(2, "failed", SECRET)}, SECRET)


def test_the_walk_reaches_an_object_of_a_type_it_does_not_know():
    """An unrecognised type falls through to repr rather than being skipped.

    Silence about a leaf is the one failure mode a leak walker may not have.
    """

    class Opaque:
        def __repr__(self) -> str:
            return f"<Opaque token={SECRET}>"

    assert find_leaks({"thing": Opaque()}, SECRET)


def test_the_walk_reaches_inside_nested_containers():
    nested = {"a": [{"b": ({"c": [SECRET]},)}], "d": {frozenset()}}
    assert find_leaks(nested, SECRET)


def test_the_walk_yields_nothing_for_none_and_booleans():
    """The quiet direction. A walker that yielded "None" and "False" as text
    would drown a real complaint in noise -- and ``False`` being an ``int``
    subclass is exactly how that happens by accident.

    The KEYS still come through, which is deliberate: a credential used as a
    dict key is a credential.
    """
    walked = list(walk({"a": None, "b": True, "c": False}))
    assert [text for where, text in walked] == ["a", "b", "c"]
    assert all(where.endswith("(key)") for where, _ in walked)


# ---------------------------------------------------------------------------
# 3. The quiet direction -- a clean result stays clean
# ---------------------------------------------------------------------------

#: The real shape ``linkedin_session_info`` returns, minus the credential. If
#: the walker complains about THIS, it is useless: every guarded test would be
#: red for a reason that has nothing to do with a leak.
CLEAN_RESULT = {
    "server": "linkedin",
    "authenticated": None,
    "checked_against": "https://www.linkedin.com/voyager/api/me",
    "live_check": {
        "attempted": True,
        "completed": False,
        "why_not": "no browser could be started",
    },
    "credential": {
        "name": "li_at",
        "present": True,
        "expires_at": "2027-08-21T17:12:37+00:00",
        "expires_in_days": 364,
        "expired": False,
        "expiry_source": "the profile's on-disk cookie jar",
    },
    "supporting": [{"name": "JSESSIONID", "present": True}],
    "renewal": {"session_lapses_at": "2027-08-21T17:12:37+00:00"},
    "job_url": "https://www.linkedin.com/jobs/view/4600000042",
}


def test_a_clean_result_produces_no_complaint():
    assert find_leaks(CLEAN_RESULT, SECRET) == []
    assert find_credential_shaped(CLEAN_RESULT) == []
    assert_no_leak(CLEAN_RESULT, SECRET)


def test_a_run_one_character_short_of_the_threshold_is_not_a_leak():
    """The boundary, both sides. Without this the run length is a guess."""
    short = SECRET[: leakwalk.MIN_RUN - 1]
    exact = SECRET[: leakwalk.MIN_RUN]
    assert find_leaks({"note": short}, SECRET) == []
    assert find_leaks({"note": exact}, SECRET)


def test_a_clean_result_stays_clean_with_an_empty_log(caplog):
    with caplog.at_level(logging.DEBUG):
        logging.getLogger("linkedin_server.auth").debug("no browser available")
    assert_no_leak(CLEAN_RESULT, SECRET, caplog=caplog)


# ---------------------------------------------------------------------------
# 4. The shape hunt -- for the credential nobody planted
# ---------------------------------------------------------------------------


def test_the_shape_hunt_catches_a_credential_no_test_planted():
    """The half of the guard a marker hunt cannot have.

    A marker hunt only knows the values it was told about, so a leak of the
    REAL li_at down a path no test plants into is invisible to it. This one
    is told nothing and still complains.
    """
    unknown = "AQEDAQ" + "kLmNoPqRsTuVwXyZ0123456789-_" * 4
    assert find_credential_shaped({"credential": {"raw": unknown}})


def test_the_shape_hunt_catches_a_csrf_token_and_an_opaque_run():
    assert find_credential_shaped({"csrf": PLANTED_JSESSIONID})
    assert find_credential_shaped({"tracking": "b" * 44})


def test_the_shape_hunt_reads_its_exemptions_exactly_not_loosely():
    """A loose exemption is how a real credential hides behind a guard.

    The permitted token passes; one character of drift from it does not.
    """
    token = "c" * 44
    assert find_credential_shaped({"t": token}, allowed=[token]) == []
    assert find_credential_shaped({"t": token + "d"}, allowed=[token])


def test_the_shape_hunt_does_not_fire_on_ordinary_result_prose():
    """The quiet control. Urls, dates, integers and sentences are not tokens."""
    assert find_credential_shaped(CLEAN_RESULT) == []
    assert find_credential_shaped(
        {
            "why": "the live identity call could not be made, so this is null",
            "url": "https://www.linkedin.com/in/some-person-a1b2c3/details/skills/",
            "posted": "2026-08-21T17:12:37+00:00",
            "applicants": 214,
        }
    ) == []


# ---------------------------------------------------------------------------
# 5. The guarded tests are still WIRED to the walker
# ---------------------------------------------------------------------------
#
# Everything above proves the INSTRUMENT works. None of it proves the six real
# assertions still USE it -- and that is a live decay path, because reverting
# one of them to `assert SECRET not in json.dumps(result)` leaves the whole
# suite green while putting the credential back at risk. The 0-of-54
# measurement would silently become historical.
#
# scripts/leak_matrix.py re-measures the property properly and is the right
# tool when the question is open. This is the cheap continuous version of the
# same question, so the decay cannot go unnoticed between runs of it.

GUARDED = {
    "tests/test_auth.py": (
        "test_no_cookie_value_ever_reaches_a_tool_result",
        "test_no_cookie_value_leaks_from_the_login_result",
        "test_session_info_never_returns_a_cookie_value",
    ),
    "tests/test_auth_lifecycle.py": (
        "test_the_offline_result_carries_no_cookie_value",
        "test_the_live_result_carries_no_cookie_value",
        "test_a_logout_result_carries_no_cookie_value",
    ),
}

REPO = Path(__file__).resolve().parent.parent


def calls_made_in(source: str, function: str) -> set[str]:
    """Every function name called inside one named function, via AST.

    AST rather than a substring search on purpose: a grep for
    "assert_no_leak" would be satisfied by the word appearing in a comment,
    which is precisely the kind of check that passes on a broken thing.
    """
    import ast

    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != function:
            continue
        names: set[str] = set()
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call):
                func = inner.func
                if isinstance(func, ast.Name):
                    names.add(func.id)
                elif isinstance(func, ast.Attribute):
                    names.add(func.attr)
        return names
    raise AssertionError(f"{function} not found -- was it renamed or deleted?")


@pytest.mark.parametrize(
    "relative,function",
    [(path, fn) for path, names in GUARDED.items() for fn in names],
    ids=lambda v: v if "/" not in str(v) else str(v).split("/")[-1],
)
def test_each_guarded_test_still_runs_through_the_walker(relative, function):
    source = (REPO / relative).read_text(encoding="utf-8")
    assert "assert_no_leak" in calls_made_in(source, function), (relative, function)


def test_the_wiring_check_can_tell_a_reverted_guard_from_a_wired_one():
    """The control. Both bodies below mention the credential; only one hunts it
    in a way that survives an encoding, and the check has to tell them apart."""
    reverted = (
        "def guard():\n"
        "    # assert_no_leak was here\n"
        "    assert SECRET not in json.dumps(result)\n"
    )
    wired = "def guard():\n    assert_no_leak(result, SECRET, caplog=caplog)\n"

    assert "assert_no_leak" not in calls_made_in(reverted, "guard")
    assert "assert_no_leak" in calls_made_in(wired, "guard")


def test_the_wiring_check_notices_a_guarded_test_that_vanished():
    """A renamed or deleted guard must be a failure, not a silent pass."""
    with pytest.raises(AssertionError) as excinfo:
        calls_made_in("def other(): pass\n", "test_that_is_not_here")
    assert "not found" in str(excinfo.value)


def test_assert_no_leak_reports_the_channel_and_the_encoding():
    """A complaint has to be actionable: WHERE it leaked and AS WHAT."""
    payload = {"credential": {"fingerprint": renderings(SECRET)["hex"]}}
    with pytest.raises(AssertionError) as excinfo:
        assert_no_leak(payload, SECRET)
    message = str(excinfo.value)
    assert "credential.fingerprint" in message
    assert "hex" in message
