"""A ``_SANITISERS`` ENTRY IS A CLAIM. THIS IS THE MEASUREMENT BEHIND IT.

``tests/test_navigation_is_never_derived.py`` stops its taint walk at a call
to a function whose NAME is in ``_SANITISERS``. That is the entire test::

    if isinstance(func, ast.Name):
        return func.id in _SANITISERS

**SO THE GUARD TRUSTS AN IDENTIFIER, NOT A CONTRACT**, and this file is the
half that was missing. It was written after a cold verifier measured, by
mutation, what that costs.

## What was measured, 2026-09-04

The verifier took the real source of ``scripts/_probe_job_search_filter_params``
and ran seven versions of it through the guard's own ``output_violations``:

    1  real source, unmodified                             GREEN
    2  the sanitiser's body gutted to ``return url``        GREEN
    3  the sanitiser renamed, body intact                   GREEN
    4  a synthetic module with its own no-op ``_redact``    GREEN
    5  a synthetic module with no sanitiser at all          RED
    6  the sanitiser call DELETED, value emitted anyway     GREEN
    7  arm 6, with that one ``emit(...)`` made ``print(...)``  RED

Arm 2 is why this file exists: **a body that returns its input verbatim passed
the same check that arm 5 failed.** Arm 4 is why the enrolment half exists: any
module may define a function with the name and inherit the trust.

## And the drift was already real when this was written

``test_a_sanitiser_entry_is_a_claim_about_a_contract`` justifies the ``_redact``
entry with "``_redact`` has its own both-directions test file". At that moment
SIX functions across six files claimed a ``_SANITISERS`` name and exactly ONE
of them -- ``scripts/_probe_messaging.py`` -- had that test file. The sentence
was true of one function and false of five. **One function's earned trust was
being spent by five others that merely shared its spelling.**

## The two halves, and neither works alone

* **ENROLMENT.** Every function in the scanned tree whose name is in
  ``_SANITISERS`` must appear in :data:`ENROLLED`. A new claimant fails until
  somebody writes down what it promises. This is what makes the name
  NON-TRANSFERABLE.
* **DEMONSTRATION.** Every enrolled function is run against an adversarial
  table and must change every needle -- and must still DISCRIMINATE, so a
  redactor that returns a constant fails too. Over-redaction is not a pass.

## It is shown failing, which is the register's condition of entry

``test_the_table_would_catch_a_do_nothing_sanitiser`` and
``test_the_table_would_catch_a_constant_returning_sanitiser`` run the SAME
tables through an identity function and a constant function. A check that
cannot fail certifies nothing, and this package has already shipped one of
those.

NO REAL IDENTITY APPEARS HERE. Every needle is invented for its SHAPE and every
one is already sanctioned by ``tests/test_no_committed_identity.py`` -- either
listed in its ``SYNTHETIC_SLUGS`` or carrying one of its ``SYNTHETIC_SLUG_TOKENS``
-- so this file moves no allowlist to exist.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tests.test_navigation_is_never_derived import (  # noqa: E402
    _SANITISERS,
    _python_files,
)

#: How a claimant is CALLED. The two shapes in this package take different
#: arities, and guessing from the signature would be the kind of cleverness
#: that silently calls the wrong thing.
ONE_ARG = "one_arg"
TWO_ARG = "two_arg"

#: **THE ENROLMENT.** ``(filename, function name) -> arity``.
#:
#: A function whose name is in ``_SANITISERS`` and which is NOT here fails
#: :func:`test_every_claimant_of_a_sanitiser_name_is_enrolled`. That is the
#: point: the guard matches by name, so the name has to cost something.
#: THE SEVENTH ENTRY WAS FOUND BY THIS FILE'S FIRST RUN. It did not exist when
#: the list above it was written twenty minutes earlier: another agent added
#: ``_probe_search_render_timeline.py`` with its own ``_redact``, which
#: inherited the guard's trust the moment it was typed. That is the exact event
#: this test was built for, and it happened before the test was committed.
ENROLLED: dict[tuple[str, str], str] = {
    ("_probe_endorse_and_follow_lines.py", "_shape_of"): TWO_ARG,
    ("_probe_free_reads_shapes.py", "_shape_of"): TWO_ARG,
    ("_probe_job_search_filter_params.py", "_shape_of"): TWO_ARG,
    ("_probe_self_details_url.py", "_shape_of"): TWO_ARG,
    ("_probe_unmeasured_surfaces_live.py", "_shape_of"): TWO_ARG,
    ("_probe_messaging.py", "_redact"): ONE_ARG,
    ("_probe_search_render_timeline.py", "_redact"): ONE_ARG,
}

#: The address a two-argument claimant is told was ASKED FOR. A constant this
#: repository authored, which is the only kind of url any of these may hold.
REQUESTED = "https://www.linkedin.com/in/me/details/skills/"

#: **INPUTS THAT MUST BE CHANGED, and the needle that must not survive.**
#:
#: Every value is invented and shape-valid. ``some-real-slug-99`` is listed in
#: ``SYNTHETIC_SLUGS``; ``example-placeholder-88`` carries two of the
#: ``SYNTHETIC_SLUG_TOKENS``; the thread blob and the bare name are the shapes
#: ``tests/test_probe_redaction.py`` already committed. A PLACEHOLDER WOULD
#: BREAK THIS -- ``/in/<SLUG>/`` matches no slug rule, so the table would pass
#: against a sanitiser that had lost the rule entirely.
NEEDLED = [
    (
        "https://www.linkedin.com/in/some-real-slug-99/details/skills/",
        "some-real-slug-99",
        "a vanity slug in a member path",
    ),
    (
        "https://www.linkedin.com/in/example-placeholder-88/",
        "example-placeholder-88",
        "a second slug, so one hard-coded string cannot pass this",
    ),
    (
        "https://www.linkedin.com/messaging/thread/2-QUJDREVGSElKS0xNTk9Q==/",
        "QUJDREVGSElKS0xNTk9Q",
        "a base64-padded thread id",
    ),
    (
        "https://www.linkedin.com/in/some-real-slug-99/?trk=Jane%20Q%20Public",
        "some-real-slug-99",
        "a slug beside a query, so the query is not the only thing read",
    ),
]

#: **PAIRS THAT MUST NOT COME BACK THE SAME.** A sanitiser that returns a
#: constant passes every leak test above while reporting nothing, which is the
#: failure mode the messaging redactor was measured making twice while it was
#: being written.
#: MORE THAN ONE PAIR, BECAUSE THE CLAIMANTS ANSWER DIFFERENT QUESTIONS. The
#: four path-relation ``_shape_of``s report what happened to an ADDRESS; the
#: job-search one reports what happened to a QUERY and returns "(no query)" for
#: both halves of a path-only pair. Requiring every claimant to discriminate on
#: every pair would be asserting that they all answer the same question, which
#: they do not. AT LEAST ONE is the real contract: the output varies with the
#: input, so something is being reported.
MUST_DISCRIMINATE = [
    (
        REQUESTED,
        "https://www.linkedin.com/feed/",
        "two different paths",
    ),
    (
        "https://www.linkedin.com/jobs/search/?keywords=node&f_JT=F",
        "https://www.linkedin.com/jobs/search/?keywords=node",
        "the same path with and without a filter key",
    ),
]


_MODULES: dict[str, object] = {}


def _module(filename: str):
    """Load one scanned file by PATH, as ``tests/test_probe_redaction.py`` does.

    Cached, because the enrolment cross-product would otherwise re-import every
    probe once per adversary and each import pulls in ``linkedin_server``.
    """
    if filename not in _MODULES:
        path = REPO / "scripts" / filename
        spec = importlib.util.spec_from_file_location(path.stem, path)
        assert spec and spec.loader, filename
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[filename] = module
    return _MODULES[filename]


def _call(function, arity: str, landed: str, requested: str = REQUESTED) -> str:
    if arity == ONE_ARG:
        return function(landed)
    return function(landed, requested)


def _claimants() -> set[tuple[str, str]]:
    """Every ``(file, function)`` in the scanned tree claiming a guarded name.

    PARSED, not grepped. A grep for ``def _redact`` would miss a rebinding and
    would match one inside a string; this repository has a standing note about
    checking a claim by structure rather than by line text.
    """
    found: set[tuple[str, str]] = set()
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in _SANITISERS:
                    found.add((path.name, node.name))
    return found


def _tracked_names() -> set[str]:
    """Basenames of the files GIT HAS, in the two scanned directories.

    Shelled out the way ``tests/test_no_committed_credential.py`` does it, and
    a non-zero return is a FAILURE rather than a skip: a check that goes quiet
    when its instrument is missing is the shape this whole file exists to
    refuse.
    """
    proc = subprocess.run(
        ["git", "ls-files", "--", "scripts", "linkedin_server"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    assert proc.returncode == 0, "git ls-files failed: %s" % proc.stderr
    return {
        line.rsplit("/", 1)[-1]
        for line in proc.stdout.splitlines()
        if line.strip()
    }


def _untracked_enrolments(table) -> set[str]:
    """Filenames in an enrolment table that git has never heard of.

    A FUNCTION rather than an inline expression, so the control below can hand
    it a table it should reject. A predicate only exercised on data that
    passes has never been shown to reject anything.
    """
    tracked = _tracked_names()
    return {filename for filename, _fn in table if filename not in tracked}


def test_every_enrolled_file_is_tracked_by_git():
    """**AN ENROLMENT NAMING AN UNTRACKED PATH IS A CLAIM ABOUT A WORKING COPY.**

    THIS IS THE DEFECT THIS TEST WAS BORN FROM, and it was reproduced rather
    than reasoned about. The seventh entry -- the one this file caught on its
    first run and was rightly proud of -- named
    ``scripts/_probe_search_render_timeline.py``, which at that moment had ZERO
    COMMITS. It existed on one working copy and in no clone anywhere.

    **CI CLONES.** The lead moved the file aside and re-ran this suite: 5
    failed, 34 passed -- the four needle rows plus the discrimination row, and
    exactly the five the full-suite gate had reported. They had been written
    off as "already fixed at the present tree". They were not fixed; they were
    INVISIBLE from the shared tree, and the first push would have gone red on
    a defect nobody could reproduce locally. A suite that passes on your
    machine and fails in CI is among the worst things a repository can hand
    somebody.

    **THE FILE HAS SINCE BEEN COMMITTED BY ITS AUTHOR (5bb70d4) AND THAT CLOSES
    NOTHING.** It was resolved by somebody else's unrelated commit, not by
    anything structural. Without this assertion the next untracked claimant
    does it again, silently, the same way.

    It is the same defect class as everything else this week, one layer down:
    a claim about the REPOSITORY, verified against the WORKING COPY.
    """
    untracked = sorted(_untracked_enrolments(ENROLLED))
    assert not untracked, (
        "these files are enrolled and git has never heard of them: %s. They "
        "exist on this working copy and in no clone, so this suite passes "
        "here and fails in CI. COMMIT the file, then enrol it -- never the "
        "other way round." % untracked
    )


def test_the_check_would_notice_an_untracked_enrolment():
    """THE CONTROL, and it is the only reason the green above means anything.

    Shown failing against a path that cannot exist, because the real table is
    green now and a predicate exercised only on passing data has never been
    shown to reject anything.
    """
    invented = "_probe_a_file_git_has_never_heard_of.py"
    assert invented not in _tracked_names(), "pick a name that is really absent"
    assert _untracked_enrolments({(invented, "_redact"): ONE_ARG}) == {invented}
    # And the real table, through the same predicate, in the same call shape.
    assert _untracked_enrolments(ENROLLED) == set()


def test_every_claimant_of_a_sanitiser_name_is_enrolled():
    """THE NAME IS NOT TRANSFERABLE.

    ``_is_sanitiser_call`` matches ``func.id in _SANITISERS``, so defining a
    function with one of those names anywhere in ``scripts/`` or
    ``linkedin_server/`` silences the output rule at every call to it. This is
    what makes that cost something: a new claimant fails here until it is
    written down and given a table.
    """
    claimants = _claimants()
    enrolled = set(ENROLLED)
    unenrolled = claimants - enrolled
    assert not unenrolled, (
        "these functions claim a _SANITISERS name and are not enrolled: %s. "
        "The guard trusts them BY NAME already. Add each to ENROLLED with its "
        "arity, and it will be measured against the adversarial table below."
        % sorted(unenrolled)
    )
    # THE STALENESS CHECK IS SCOPED TO FILES THAT ARE STILL HERE, deliberately.
    # An enrolment whose FILE is absent -- an untracked probe that was never
    # committed, or one deleted outright -- grants no trust to anything, so
    # firing on it would put a landmine in the suite for a file nobody has.
    # An enrolment whose file EXISTS while its function is gone is the real
    # staleness case, and this repository's standing rule is that the
    # documentation of a thing must not outlive the thing.
    present = {path.name for path in _python_files()}
    vanished = {
        entry for entry in enrolled - claimants if entry[0] in present
    }
    assert not vanished, (
        "these are enrolled, their file is still here, and the function is "
        "gone: %s. An enrolment for a function that does not exist is a "
        "comment pretending to be a check -- delete it." % sorted(vanished)
    )


@pytest.mark.parametrize("claimant", sorted(ENROLLED), ids=lambda c: "%s::%s" % c)
@pytest.mark.parametrize("landed, needle, why", NEEDLED, ids=[w for _u, _n, w in NEEDLED])
def test_each_enrolled_sanitiser_is_shown_holding_the_needle(
    claimant, landed, needle, why
):
    """EVERY CLAIMANT, EVERY NEEDLE. The half arm 2 would have failed."""
    filename, function_name = claimant
    function = getattr(_module(filename), function_name)
    out = _call(function, ENROLLED[claimant], landed)
    assert needle not in out, (
        "%s::%s returned its input's identity (%s) -- %s. It is in "
        "_SANITISERS, which tells every other check in this package that its "
        "result carries none of its input."
        % (filename, function_name, why, needle)
    )


@pytest.mark.parametrize("claimant", sorted(ENROLLED), ids=lambda c: "%s::%s" % c)
def test_each_enrolled_sanitiser_still_discriminates(claimant):
    """THE OTHER DIRECTION, and it is what stops the fix being ``return ''``.

    A sanitiser that collapses everything to one string passes every needle
    test perfectly while reporting nothing -- the failure the messaging
    redactor was measured making twice while it was being written
    (``Conversation List`` flattened to ``<NAME>``).

    AT LEAST ONE PAIR, for the reason argued at :data:`MUST_DISCRIMINATE`.
    """
    filename, function_name = claimant
    function = getattr(_module(filename), function_name)
    arity = ENROLLED[claimant]
    separated = [
        why for left, right, why in MUST_DISCRIMINATE
        if _call(function, arity, left) != _call(function, arity, right)
    ]
    assert separated, (
        "%s::%s returned the SAME string for both halves of every pair in "
        "MUST_DISCRIMINATE, so it is not reporting anything. A redactor that "
        "flattens every input passes a leak-only test while destroying the "
        "reading it exists for." % (filename, function_name)
    )


def test_the_table_would_catch_a_do_nothing_sanitiser():
    """THE CONTROL. Without it the greens above mean nothing.

    This is arm 2 of the mutation study, run as a check rather than described
    in a comment: a body that returns its input, against the same table.
    """
    def gutted(url, requested=None):
        return url

    caught = [
        why for landed, needle, why in NEEDLED
        if needle in gutted(landed)
    ]
    assert len(caught) == len(NEEDLED), (
        "the needle table caught only %d of %d rows against a sanitiser that "
        "does nothing. The rows it missed are rows this file cannot see, and "
        "their greens above are vacuous: %s"
        % (len(caught), len(NEEDLED),
           sorted({w for _u, _n, w in NEEDLED} - set(caught)))
    )


def test_the_table_would_catch_a_constant_returning_sanitiser():
    """THE SECOND CONTROL. Over-redaction has to fail too, or the fix is ''."""
    def constant(url, requested=None):
        return "SERVED"

    separated = [
        why for left, right, why in MUST_DISCRIMINATE
        if constant(left) != constant(right)
    ]
    assert not separated, (
        "the discrimination table thinks a CONSTANT function reports "
        "something (%s), so it would not notice a redactor that reports "
        "nothing." % separated
    )


def test_the_guarded_names_are_the_ones_this_file_thinks_they_are():
    """PINNED AGAINST DRIFT IN THE OTHER FILE.

    This file's whole premise is the contents of ``_SANITISERS``. If a name is
    added there and not considered here, the enrolment above stops covering the
    set it claims to cover -- silently, because a new name simply matches
    nothing.
    """
    assert _SANITISERS == frozenset({"_shape_of", "_redact"}), _SANITISERS
    assert {name for _f, name in ENROLLED} == set(_SANITISERS), (
        "every guarded name must have at least one enrolled claimant, or this "
        "file is asserting over a name nobody uses: %s vs %s"
        % (sorted({n for _f, n in ENROLLED}), sorted(_SANITISERS))
    )
