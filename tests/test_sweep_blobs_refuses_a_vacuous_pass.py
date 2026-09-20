"""How ``scripts/sweep_blobs_for_identity.py`` refuses rather than fake a sweep.

THE ORIGINAL DEFECT. That script sweeps git BLOBS (not the working tree) for
known real identity values before a push. Handed a garbage range argument --
observed with ``--help`` before this file's guard against ``--help``
existed -- it printed

    PASS: 0 hits across 0 blobs

and exited 0. The cause was ``_git()`` returning ``out.stdout`` alone and
throwing away ``returncode`` and ``stderr``. ``git rev-list <garbage>``
failed, ``_git()`` handed back whatever stdout it had (empty), ``commits``
came out ``[]``, the blob loop never ran, ``blobs`` stayed ``0``, and the
existing MUTE CHECK -- built for an empty NEEDLE set -- had no equivalent
check for an empty CORPUS. A garbage argument produced a green from a safety
instrument.

THIS FILE'S OWN HISTORY, recorded rather than silently overwritten, because
this exact question was gotten wrong twice in one day before it settled:

1. FIRST BUILD: unresolvable range -> refuse (exit 2). Resolvable range,
   zero commits -> ALSO refuse (exit 2). Same for commits > 0 but zero blobs
   after exemptions. Tested, shipped.
2. FIRST REVERSAL (withdrawn the same day): an argument was made that a
   resolvable-but-empty range (``origin/master..HEAD`` when nothing is
   unpushed) is the NORMAL state of a synced repo, and refusing there
   hard-fails the caller's own routine invocation -- so it should PASS,
   tagged ``PASS (NOTHING IN RANGE)`` / ``PASS (NOTHING SWEPT)`` to keep it
   out of the bare, undifferentiated form. Built, tested, shipped.
3. WITHDRAWN, SAME DAY: that argument attaches a MEASURED FACT (the range is
   empty right now) to a NORMATIVE CLAIM (therefore safe to pass) without
   separating them. An empty result is ambiguous between "genuinely nothing
   to check" and "this range was pointed at the wrong history" (a stale
   local ``origin/master``, a misconfigured upstream, a typo'd ref that
   happens to resolve) -- the tool cannot tell those apart, so PASS there is
   the same false assurance as the original ``--help`` bug, one layer up.
   Reverted to the first build's behaviour for both branches. See the
   SCRIPT's own module docstring for the full argument, including why the
   refusal is spelled neither ``PASS`` nor ``FAIL``.

WHAT THIS FILE PINS, grouped by what each group proves:

* :func:`test_a_garbage_range_is_refused_not_passed` is the literal RED PROOF
  -- the original failure mode, reproduced and asserted refused. Never in
  question through either reversal above.
* :func:`test_help_is_a_help_request_not_a_range` pins the companion fix:
  ``--help`` must never reach ``git rev-list`` as if it were a range.
* :func:`test_a_range_with_zero_commits_is_refused` and
  :func:`test_the_live_caller_shape_origin_master_dot_dot_head` pin the
  SETTLED behaviour end to end, as real subprocess invocations -- the second
  one against the caller's *actual* range rather than a stand-in.
* :func:`test_a_real_range_sweeps_and_never_silently_passes` is the positive
  control: a real, non-empty range must actually sweep and reach a real
  verdict.
* :func:`test_the_zero_commits_guard_fires_before_the_blob_loop_ever_runs`
  and :func:`test_the_zero_blobs_guard_fires_even_with_real_commits` are
  MUTATION CONTROLS: each isolates one of the two zero-cases in-process, by
  monkeypatching ``_git`` so the other case's trigger condition cannot also
  be true. That isolation is the reason they are in-process rather than more
  subprocess calls -- ``HEAD..HEAD`` alone cannot tell a reader whether the
  zero-COMMITS path or the zero-BLOBS path is what actually ran, because
  with zero commits the loop never runs and blobs is ALSO zero, so either
  path alone would make one subprocess test pass. Forcing ``commits``
  non-empty while ``ls-tree`` returns nothing (and asserting ``cat-file`` is
  never called) proves the blobs path specifically; forcing ``rev-list`` to
  return nothing while asserting ``ls-tree`` is never called proves the
  commits path specifically.
* :func:`test_a_failing_rev_list_is_reported_not_swallowed` is the in-process
  counterpart of the red proof.
* :func:`test_no_code_path_prints_the_bare_zero_zero_sentence` is a static
  control against reintroducing the original bug's exact sentence by a
  future edit that does not happen to go through any branch this file
  otherwise exercises -- kept through both reversals above without needing
  to change, since the sentence was never permitted in any build.

WHY SUBPROCESS FOR THE END-TO-END TESTS RATHER THAN IN-PROCESS THROUGHOUT:
this needs to run the script the way a caller actually runs it -- as a
subprocess, through the real interpreter -- so a bug that only exists at the
process boundary (exactly what the original one was: an exit code and
stderr thrown away by a function, not a Python-level exception) cannot hide
from the test the way it hid from the script's own author.

WHY THE INTERPRETER IS ``sys.executable``, AND WHY IT USED TO BE COMPUTED.

The original reasoning was right about the case it considered and wrong about
the one it did not. A linked worktree has no ``venv/`` of its own -- ``venv/``
is gitignored and git does not carry gitignored files into a worktree -- so
this resolved the interpreter through ``tests.repo_paths.main_checkout``,
reaching across to the main checkout exactly as
``tests/test_no_committed_identity.py`` does for the gitignored sanitisation
key.

**THAT PATH DOES NOT EXIST ON CI, WHERE THERE IS NO ``venv/`` AT ALL**, and the
precondition assert turned into a hard failure on all three platforms the
moment this was published -- ubuntu py3.10, ubuntu py3.13 and windows py3.13
alike, green on the box it was written on. Same shape as the ancestry control
that pinned a local-only branch, and as a wave citing a SHA on a branch that
never merged: **a test that assumes the shape of the repository it happens to
be standing in.**

``sys.executable`` is the interpreter ALREADY RUNNING these tests, so it is
correct in all three environments and solves the worktree problem more directly
than computing it -- in a worktree, the thing that invoked pytest IS the main
checkout's venv. It also needs no import of a helper to answer a question the
runtime already knows.
"""

from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from tests.repo_paths import describe_key_path, sanitisation_key_path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "sweep_blobs_for_identity.py"
PYTHON = Path(sys.executable)

#: The gitignored de-anonymisation wordlist the sweep needs in order to sweep
#: ANYTHING. Resolved through the shipped helper rather than joined by hand,
#: because a linked worktree has no key of its own and the helper is what
#: answers "the local one, else the main checkout's, else say where I looked".
#: Absent on every CI runner by design -- see the positive control below.
KEY_PATH = sanitisation_key_path(REPO)

#: Generous but bounded. The positive control below does a real sweep of one
#: commit's worth of blobs (low hundreds -- 610 the last time this was
#: measured), one ``git cat-file`` subprocess per blob. In a quiet worktree
#: that finishes in a couple of seconds; in THIS repository's actual working
#: conditions -- a shared worktree with a measured concurrent writer, see the
#: module docstring's history -- the identical command was clocked at 136s
#: standalone, no test framework involved. 120 was measured too tight here
#: and produced a TimeoutExpired on a run that was working correctly, just
#: slowly; this keeps enough headroom for that contention while still
#: catching a genuinely hung subprocess.
_TIMEOUT_SECONDS = 300


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the real script through the real interpreter, as a caller would."""
    # `sys.executable` is documented as possibly EMPTY -- an embedded or frozen
    # interpreter can leave it unset -- and an empty string here would run the
    # script through the shell's idea of "" rather than failing. That is the
    # only way this precondition can still bite, and it is worth one line.
    # It deliberately does NOT re-assert `PYTHON.exists()`: for the interpreter
    # currently executing this function that is true by construction, and a
    # precondition that cannot fail is the defect this whole module is about.
    assert str(PYTHON), (
        "sys.executable is empty, so there is no interpreter to run the script "
        "under and every result below would be about the shell, not the sweep"
    )
    return subprocess.run(
        [str(PYTHON), str(SCRIPT), *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SECONDS,
    )


def _load_script():
    """Load the script AS A MODULE, the way ``tests/test_identity_gate.py``
    loads ``scripts/identity_gate.py`` -- by file location, not by mutating
    ``sys.path`` and doing a plain import, so this test's own import does not
    leave a stray ``sweep_blobs_for_identity`` entry in ``sys.modules`` for
    whatever runs after it in the same session.
    """
    spec = importlib.util.spec_from_file_location(
        "_sweep_blobs_for_identity_under_test", SCRIPT
    )
    assert spec is not None and spec.loader is not None, SCRIPT
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Subprocess tests: the script as a caller actually invokes it.
# ---------------------------------------------------------------------------


def test_help_is_a_help_request_not_a_range():
    """``--help`` must print usage and exit 0 -- and, critically, must never
    be handed to ``git rev-list`` as if it were a range. Before the guard
    this test pins, that misinterpretation was exactly how the vacuous PASS
    below was first found.

    Does NOT assert "PASS"/"FAIL" are absent: the usage text legitimately
    documents both words as part of the exit-status contract (including why
    the refusal is spelled as neither), so they appear in real usage output
    on purpose. What must be absent is anything that only a REAL run prints
    -- the ``needles:``/``range  :`` scaffolding lines that always lead a
    real sweep's output and never appear in the docstring.
    """
    result = _run("--help")
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert "USAGE" in result.stdout
    assert "sweep_blobs_for_identity.py" in result.stdout
    assert "needles:" not in result.stdout
    assert "range  :" not in result.stdout


def test_a_garbage_range_is_refused_not_passed():
    """THE RED PROOF. A range git itself cannot resolve must exit 2 and must
    never print PASS -- reproducing, and pinning shut, the exact defect this
    file exists for. ``not-a-real-ref-zzz`` is used instead of the original
    ``--help`` repro because ``--help`` is now legitimately intercepted
    before it ever reaches ``git rev-list`` (see
    :func:`test_help_is_a_help_request_not_a_range`); this needs a garbage
    argument that still reaches the range-resolution code path.

    Never touched by this file's later back-and-forth (see the module
    docstring): an unresolvable range was never the case in question, only
    the resolvable-but-empty one was.
    """
    result = _run("not-a-real-ref-zzz")
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "PASS" not in result.stdout, result.stdout
    # Exit 1 is reserved for "hits found" (see the module docstring); a
    # failed git call must never land there by accident.
    assert result.returncode != 1


def test_a_range_with_zero_commits_is_refused():
    """SETTLED BEHAVIOUR, pinned end to end. ``HEAD..HEAD`` is always empty
    (a ref compared with itself) but always RESOLVABLE -- git succeeds,
    there is simply nothing there. That must ALSO exit 2, not 0: an empty
    result cannot be told apart from a misaimed range (see the script's own
    module docstring for the full argument), so it is refused the same as
    an unresolvable one, with a message that still says which of the two
    happened.
    """
    result = _run("HEAD..HEAD")
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "PASS" not in result.stdout, result.stdout
    assert "resolved to" in result.stdout and "ZERO commits" in result.stdout, (
        "must name that the range RESOLVED and was empty, distinguishably "
        f"from the unresolvable-range refusal:\n{result.stdout}"
    )
    assert result.returncode != 1


def test_the_live_caller_shape_origin_master_dot_dot_head():
    """Pins ``scripts/purge_denied_term.py:179``'s ACTUAL invocation, not a
    stand-in for it -- this is the range that the withdrawn PASS-on-empty
    behaviour was built to protect, and that this script's settled position
    refuses anyway, because a routine invocation that inspected nothing
    still inspected nothing.

    Never skipped, and never assumes which branch it will take: this
    repository's worktrees have measured concurrent writers (not
    theoretical -- caught directly during the investigation that produced
    this settled ruling; ``origin/master..HEAD`` was observed to go from 0
    commits ahead to 1 while the ruling was still being argued), so this
    reads the real state first with its own ``git rev-list`` call and
    asserts whichever outcome that state implies, naming the branch taken in
    every assertion message so a failure here never reads as ambiguous about
    which case it was checking.
    """
    ahead = subprocess.run(
        ["git", "rev-list", "origin/master..HEAD"],
        cwd=str(REPO), capture_output=True, text=True, timeout=30,
    )
    assert ahead.returncode == 0, (
        "origin/master..HEAD did not even resolve in this checkout; this "
        f"test needs a resolvable ref to test against: {ahead.stderr}"
    )
    commit_count = len(ahead.stdout.split())

    result = _run("origin/master..HEAD")

    if commit_count == 0:
        assert result.returncode == 2, (
            f"branch taken: EMPTY (0 commits ahead of origin/master) -- "
            f"expected exit 2 (refused, resolvable-but-empty):\n"
            f"{result.stdout}\n{result.stderr}"
        )
        assert "resolved to" in result.stdout and "ZERO commits" in result.stdout, (
            f"branch taken: EMPTY -- expected the resolved-but-empty "
            f"refusal:\n{result.stdout}"
        )
    else:
        assert result.returncode in (0, 1), (
            f"branch taken: NON-EMPTY ({commit_count} commit(s) ahead) -- "
            f"expected exit 0 or 1, never 2:\n{result.stdout}\n{result.stderr}"
        )
        assert "resolved to" not in result.stdout, (
            f"branch taken: NON-EMPTY ({commit_count} commit(s) ahead) -- "
            f"must not claim the range resolved to zero commits:\n"
            f"{result.stdout}"
        )
    assert "0 hits across 0 blobs" not in result.stdout, result.stdout


def test_a_real_range_sweeps_and_never_silently_passes():
    """POSITIVE CONTROL. ``HEAD~1..HEAD`` is one real commit in this
    repository's own history -- the sweep must actually run, find at least
    one blob, and reach a real verdict; an instrument that refuses
    EVERYTHING is as useless as one that never refuses. Untouched by this
    file's later back-and-forth: a non-empty range was never in question.

    Never skipped. If the wordlist genuinely holds no needles (the pre-
    existing MUTE CHECK this file's three broken predecessors were caught
    by), that is a real, assertable outcome in its own right -- exit 2 with
    the empty-needle-set message -- and this asserts exactly that rather
    than skipping around it. Any OTHER non-(0,1) outcome (in particular exit
    1 with empty stdout, which is what ``load_wordlist()`` produces if the
    gitignored key is entirely absent rather than merely empty) is left to
    fail the assertions below loudly, which is the correct outcome for an
    environment this test cannot silently paper over.

    THAT STANCE IS ANSWERED, NOT DELETED, 2026-09-20. It was right about a
    developer box and wrong about CI, and the difference is whether the
    absence is TEMPORARY. On a machine that ought to have the key, a loud
    failure is correct: somebody can go and fix it. **On CI the key is absent
    BY DESIGN and permanently** -- it is the de-anonymisation wordlist for the
    committed fixtures and it is gitignored on purpose, so it will never be
    there. A test that fails on every CI run forever is not failing loudly; it
    is training every reader to scroll past a red run, which costs more than
    the check was ever worth.

    So this now takes the SAME route this repository already chose for the
    identical situation in
    ``test_no_committed_identity.py::test_the_exact_value_sweep_actually_runs``:
    skip, with **a sentence rather than a dot**, so "did not run" is SAID in
    the summary of every run instead of being indistinguishable from "ran and
    found nothing". The original stance survives everywhere it was right --
    an EMPTY wordlist still fails loudly below, because that is a machine that
    has a key and the key is broken.
    """
    if not KEY_PATH.exists():
        pytest.skip(
            "THE POSITIVE CONTROL DID NOT RUN, so nothing in this session "
            "proved this sweep can actually sweep. The wordlist %s is absent "
            "-- gitignored on purpose, and never present on CI. The REFUSAL "
            "cases above all ran and need no key: they are validated before "
            "the wordlist is loaded, deliberately. What is unproven here is "
            "only the positive direction."
            % describe_key_path(REPO, KEY_PATH)
        )

    result = _run("HEAD~1..HEAD")
    if result.returncode == 2:
        assert "the needle set is EMPTY" in result.stdout, (
            "exit 2 on a real, populated range must mean the pre-existing "
            f"mute check fired, not a masked failure:\n{result.stdout}\n"
            f"{result.stderr}"
        )
        return

    assert result.returncode in (0, 1), (result.stdout, result.stderr)
    lines = result.stdout.splitlines()
    swept_lines = [line for line in lines if line.startswith("swept  :")]
    assert swept_lines, result.stdout
    blob_count = int(swept_lines[0].split(":", 1)[1].split()[0])
    assert blob_count > 0, swept_lines[0]

    if result.returncode == 0:
        assert "PASS:" in result.stdout
        assert f"across {blob_count} blobs" in result.stdout
    else:
        assert "FAIL:" in result.stdout


# ---------------------------------------------------------------------------
# Mutation controls: each isolates ONE zero-case in-process.
# ---------------------------------------------------------------------------


def test_the_zero_commits_guard_fires_before_the_blob_loop_ever_runs(
    monkeypatch, capsys
):
    """Force ``git rev-list`` to succeed with NOTHING, in-process, so this
    is isolated from the zero-blobs guard below: ``ls-tree`` must never even
    be called, which this proves by making the fake raise if it is.
    """
    module = _load_script()
    monkeypatch.setattr(module, "load_wordlist", lambda: {"cls": {"needle"}})

    def fake_git(*args: str, **kwargs: object) -> str:
        if args[0] == "rev-list":
            return ""  # git succeeded; there is simply nothing there
        raise AssertionError(
            f"the zero-commits guard should have returned before calling "
            f"git {args!r}"
        )

    monkeypatch.setattr(module, "_git", fake_git)

    code = module.main(["prog", "fake-range"])
    out = capsys.readouterr().out

    assert code == 2
    assert "resolved to" in out and "ZERO commits" in out
    assert "PASS" not in out


def test_the_zero_blobs_guard_fires_even_with_real_commits(monkeypatch, capsys):
    """Force ``git rev-list`` to succeed with ONE commit (so the zero-
    commits guard above does NOT fire) but that commit's tree is empty, in-
    process, so this is isolated from the zero-commits guard: ``cat-file``
    must never even be called, which this proves by making the fake raise if
    it is.
    """
    module = _load_script()
    monkeypatch.setattr(module, "load_wordlist", lambda: {"cls": {"needle"}})

    def fake_git(*args: str, **kwargs: object) -> str:
        if args[0] == "rev-list":
            return "0123456789abcdef0123456789abcdef01234567\n"
        if args[0] == "ls-tree":
            return ""  # that one commit's tree has nothing in it
        raise AssertionError(
            f"the zero-blobs guard should have returned before calling "
            f"git {args!r}"
        )

    monkeypatch.setattr(module, "_git", fake_git)

    code = module.main(["prog", "fake-range"])
    out = capsys.readouterr().out

    assert code == 2
    assert "range  : fake-range -> 1 commit(s)" in out
    assert "ZERO blobs to inspect" in out
    assert "PASS" not in out


def test_a_failing_rev_list_is_reported_not_swallowed(monkeypatch, capsys):
    """The in-process counterpart of :func:`test_a_garbage_range_is_refused
    _not_passed`: forces ``_git`` to raise ``GitError`` the way a real
    failed ``git rev-list`` now does, and checks the message names the
    range and quotes git's stderr rather than just returning a bare 2.
    Untouched by this file's later back-and-forth -- this is the case that
    was always meant to refuse.
    """
    module = _load_script()
    monkeypatch.setattr(module, "load_wordlist", lambda: {"cls": {"needle"}})

    def fake_git(*args: str, **kwargs: object) -> str:
        if args[0] == "rev-list":
            raise module.GitError(args, 128, "fatal: bad revision 'fake-range'\n")
        raise AssertionError(f"should not reach git {args!r} after a rev-list failure")

    monkeypatch.setattr(module, "_git", fake_git)

    code = module.main(["prog", "fake-range"])
    out = capsys.readouterr().out

    assert code == 2
    assert "fake-range" in out
    assert "FAILED" in out
    assert "bad revision" in out
    assert "PASS" not in out


def test_no_code_path_prints_the_bare_zero_zero_sentence():
    """THE CONTROL AGAINST RE-INTRODUCING THE ORIGINAL SENTENCE. The bug this
    whole file exists for had exactly one visible symptom:
    ``PASS: 0 hits across 0 blobs`` (see the module docstring). Every zero
    case now refuses rather than prints any PASS form at all, but this is
    pinned a SECOND way, statically on the source text rather than only at
    runtime, because a future edit could reintroduce the bare sentence as a
    hardcoded literal somewhere this file does not happen to exercise (a new
    print site, say) -- a runtime test aimed at today's branches would not
    catch that, and a grep can't be dodged by a code path it does not
    exercise. Unaffected by, and kept unchanged through, this file's
    back-and-forth: the sentence was never permitted in any build.

    Checked over STRING-LITERAL AST NODES, not raw text, and this went
    through two wrong drafts before landing here, both worth recording:
    a whole-file text search tripped on the module docstring's own
    explanation of the invariant, which has to name the exact sentence to
    explain what must never be printed again; splitting the docstring off by
    line number and text-searching the remainder then tripped on two CODE
    COMMENTS that name the same sentence for the same reason, one beside
    each zero-case branch. A text scan cannot tell "explains the sentence"
    from "prints the sentence" -- an AST walk restricted to string constants
    can, because a comment is never a node at all and every docstring is a
    specific, identifiable node this excludes by identity. What remains is
    exactly the set of literals that could ever reach stdout.
    """
    source = SCRIPT.read_text(encoding="ascii")
    tree = ast.parse(source)

    # Every docstring in the file (module, class or function), by node
    # identity -- not just the module's. Generalised past what this script
    # currently needs (only its module docstring names the sentence) so a
    # future function docstring that ALSO has to explain the invariant does
    # not reopen the same false positive a third time.
    docstrings = set()
    for owner in ast.walk(tree):
        if isinstance(owner, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = owner.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstrings.add(body[0].value)
    assert docstrings, "expected at least the module docstring to be found"

    offending = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node not in docstrings
        and "0 hits across 0 blobs" in node.value
    ]
    assert not offending, (
        f"found the literal phrase in a live string constant at line(s) "
        f"{offending} -- no zero-case may ever print any PASS form"
    )
