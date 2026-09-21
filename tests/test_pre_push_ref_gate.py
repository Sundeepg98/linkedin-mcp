"""The pre-push ref gate refuses anything but master, and can be shown doing it.

WHY THIS FILE IS SMALL AND RUNS ANYWHERE. The gate's decision is a pure
function of git's stdin lines, so the whole of it is testable without a repo, a
remote, a wordlist or a venv -- which matters because the identity gate beside
it CANNOT run on a runner (its wordlist is gitignored) and this one therefore
carries the CI half of the push protection on its own.

WHAT IT GUARDS, measured 2026-09-21 rather than assumed: `git push --all` in
this checkout offers 45 refs. Four non-ancestor branches were swept and every
one reads FAIL, 3 hits in 1 path -- the identity blobs that
`scripts/purge_denied_term.py` removed from the history master publishes. The
repository is public and publishing is not reversible.
"""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "pre_push_ref_gate", REPO / "scripts" / "pre_push_ref_gate.py")
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

A = "1" * 40
ZERO = "0" * 40


def _line(local: str, sha: str, remote: str) -> str:
    return f"{local} {sha} {remote} {A}"


def test_a_master_push_is_allowed():
    got = gate.verdicts([_line("refs/heads/master", A, "refs/heads/master")])
    assert [v for v, _r, _w in got] == ["ALLOW"], got


def test_a_non_master_ref_is_refused():
    got = gate.verdicts([_line("refs/heads/x", A, "refs/heads/integrate-1821")])
    assert [v for v, _r, _w in got] == ["REFUSE"], got


def test_the_refusal_is_on_the_REMOTE_ref_not_the_local_one():
    """`git push origin master:sneaky` -- the case a local-ref check misses.

    THE LOCAL SIDE MUST BE AN ALLOWED VALUE OR THIS TEST PROVES NOTHING. Its
    first version used `HEAD` as the local ref, and `HEAD` is not in the
    allowlist either -- so swapping the gate to read the LOCAL ref still
    refused, and the test passed for the wrong reason. A mutation run caught
    it: "check the local ref instead of the remote one" was survivable.
    Only a line whose local ref is literally `refs/heads/master`, while the ref
    that would become public is not, can tell the two implementations apart.
    """
    got = gate.verdicts([_line("refs/heads/master", A, "refs/heads/sneaky")])
    assert got[0][0] == "REFUSE", got
    assert got[0][1] == "refs/heads/sneaky", got


def test_a_delete_is_refused_and_named_as_one():
    got = gate.verdicts([_line("refs/heads/x", ZERO, "refs/heads/ci-offload")])
    assert got[0][0] == "REFUSE", got
    assert "DELETE" in got[0][2], got[0]


def test_an_unparsed_line_is_refused_rather_than_skipped():
    """An unknown line is an unknown push. Skipping it is the silent failure."""
    got = gate.verdicts(["garbage"])
    assert got[0][0] == "REFUSE", got
    assert "unparsed" in got[0][2], got[0]


def test_a_mixed_push_refuses_only_the_strays_and_counts_them():
    got = gate.verdicts([
        _line("refs/heads/master", A, "refs/heads/master"),
        _line("refs/heads/a", A, "refs/heads/a"),
        _line("refs/heads/b", A, "refs/heads/b"),
    ])
    assert [v for v, _r, _w in got] == ["ALLOW", "REFUSE", "REFUSE"], got


def test_blank_lines_are_not_verdicts():
    assert gate.verdicts(["", "   ", ""]) == []


def test_the_allowlist_is_exactly_master_and_nothing_adjacent():
    """A prefix or a tag must not slip in on a substring match.

    `refs/heads/master-wip` and `refs/tags/master` both contain the allowed
    string; membership is by equality and this is what says so.
    """
    for ref in ("refs/heads/master-wip", "refs/tags/master",
                "refs/heads/notmaster", "refs/remotes/origin/master"):
        got = gate.verdicts([_line("refs/heads/x", A, ref)])
        assert got[0][0] == "REFUSE", (ref, got)


def test_the_control_this_suite_needs_to_be_worth_anything():
    """THE POSITIVE CONTROL: the ALLOW path is reachable at all.

    Every other test here asserts a REFUSAL, and a `verdicts()` that returned
    REFUSE unconditionally -- the single likeliest way to break this file --
    would pass all of them. This is the one that would go red.
    """
    got = gate.verdicts([_line("refs/heads/master", A, "refs/heads/master")])
    assert got and got[0][0] == "ALLOW", (
        "verdicts() refuses even master, so every refusal test above is "
        "passing for the wrong reason")
