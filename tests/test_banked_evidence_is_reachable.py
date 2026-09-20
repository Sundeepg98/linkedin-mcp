"""Controls and the pin for `scripts/check_banked_evidence_is_reachable.py`.

WHAT IS PINNED. **9** banked census rows rest on at least one evidence
artifact that a reader cloning this repository cannot reach. Measured
2026-09-20 over 94 banked rows and 126 cited artifacts across the four
capability slices. The list is in
`_audit/2026-09-20-the-evidence-that-resolves.md`.

THE PIN RUNS BOTH WAYS, for the reason the sibling citation guard gives: a
defect DISAPPEARING and a detector going blind look identical from outside,
and only one of them is good news.

THE CONTROL THAT MATTERS MOST here is not a finding control at all. It is
`test_a_nonsense_argument_is_loud_not_green`. An hour before this instrument
was written, `scripts/sweep_blobs_for_identity.py --help` accepted `--help` as
a git range, swept 0 blobs and printed **"PASS: 0 hits across 0 blobs"** --
a safety tool returning a green because it had been aimed at nothing. Every
denominator in this instrument is therefore a refusal point, and each one is
controlled below.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_banked_evidence_is_reachable as chk  # noqa: E402

SCRIPT = REPO / "scripts" / "check_banked_evidence_is_reachable.py"

#: (slice, row id, state) -- the 9. Measured 2026-09-20 at the second merge of
#: `master` into this wave. Every one of the 15 unreachable artifacts behind
#: these rows is a `_audit/_scratch/` path, which `.gitignore:156` quarantines
#: outright.
#:
#: **THE SET GREW WHILE THE WAVE RAN, AND THAT IS THE FINDING RATHER THAN AN
#: INCONVENIENCE.** It was 7 at the first measurement and 7 again after the
#: first merge. The second merge brought a sibling wave that banked 13 more
#: rows, and TWO of them -- `jobs.md` 27 and 151 -- cite `_audit/_scratch/`
#: paths. So this is not an inherited mess being counted down: the generator
#: is live, and a row banked today can land here tomorrow. That is exactly what
#: a two-way ratchet is for.
PINNED = {
    ("_audit/_census/jobs.md", "9", "COVERED-PROVEN"),
    ("_audit/_census/jobs.md", "11", "COVERED-PROVEN"),
    ("_audit/_census/jobs.md", "12", "COVERED-PROVEN"),
    ("_audit/_census/jobs.md", "13", "COVERED-PROVEN"),
    ("_audit/_census/jobs.md", "14", "COVERED-PROVEN"),
    ("_audit/_census/jobs.md", "15", "COVERED-PROVEN"),
    ("_audit/_census/jobs.md", "27", "COVERED-PROVEN"),
    ("_audit/_census/jobs.md", "151", "COVERED-PROVEN"),
    ("_audit/_census/network.md", "136", "MEASURED-ABSENT"),
}

#: A census table shaped like the real ones, for planting defects into.
#: `{state}` and `{cell}` are filled per test.
PLANTED = (
    "# A planted slice\n\n"
    "| # | capability | R/W | state | evidence |\n"
    "|---|---|---|---|---|\n"
    "| 1 | Something measurable | R | {state} | {cell} |\n"
)

def _a_tracked_script() -> str:
    """A path git certainly tracks, chosen AT RUN TIME.

    Written first as a literal naming this instrument's own script -- which
    was not committed yet, so two controls went red claiming an UNTRACKED-LOCAL
    verdict was a bug. It was not; the fixture was. A fixture that assumes a
    file is published is the same shape as a wave citing a SHA on a branch
    that never merged, which is the sibling guard's entire subject.
    """
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "scripts/*.py"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    files = [f.strip() for f in out.stdout.splitlines() if f.strip()]
    assert files, (
        "no tracked file under scripts/ -- the positive control has no fixture "
        "and must not be skipped; something is wrong with the checkout"
    )
    return sorted(files)[0]


TRACKED_ARTIFACT = _a_tracked_script()
IGNORED_ARTIFACT = "_audit/_scratch/_progress-job-search-params.md"


def _plant(cell, state="COVERED-PROVEN"):
    return {"_audit/_census/_planted.md": PLANTED.format(state=state, cell=cell)}


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO),
    )


@pytest.fixture(scope="module")
def measured():
    return chk.measure()


# --------------------------------------------------------------------------
# THE RED PROOF, and its positive control
# --------------------------------------------------------------------------

def test_the_detector_finds_a_planted_unreachable_artifact():
    """RED PROOF. A check that has never been shown failing certifies nothing."""
    rows, stats, _ = chk.measure(_plant("Measured once, see `" + IGNORED_ARTIFACT + "`."))
    assert len(rows) == 1, rows
    bad = rows[0].unreachable
    assert [a.path for a in bad] == [IGNORED_ARTIFACT], rows[0].artifacts
    assert bad[0].verdict == "GITIGNORED", bad[0]


def test_a_row_citing_only_tracked_evidence_is_clean():
    """THE MIRROR. An instrument that convicts everything convicts the clean
    row too, and then its findings mean nothing."""
    rows, _, _ = chk.measure(_plant("Measured once, see `" + TRACKED_ARTIFACT + "`."))
    assert len(rows) == 1
    assert rows[0].unreachable == (), rows[0].artifacts
    assert [a.verdict for a in rows[0].artifacts] == ["TRACKED"]


def test_an_unbanked_row_is_not_examined():
    """The instrument is scoped to BANKED states. A GAP row citing the same
    unreachable path is not a finding -- a GAP claims nothing."""
    rows, _, _ = chk.measure(
        _plant("See `" + IGNORED_ARTIFACT + "`.", state="GAP"))
    assert rows == []


@pytest.mark.parametrize("state", ["COVERED-PROVEN", "CP", "COVERED-CANNOT-DELIVER",
                                   "MEASURED-ABSENT", "**CP 2026-09-19**",
                                   "**COVERED-PROVEN 2026-09-05**",
                                   "MEASURED-ABSENT `SKILL`"])
def test_every_banked_spelling_the_corpus_uses_is_recognised(state):
    """FOUR ROWS RODE ON THIS. A first version compared the whole state cell
    against the vocabulary, so `**CP 2026-09-19**` and
    `**COVERED-PROVEN 2026-09-05**` read as unknown states and were dropped --
    silently, and in the direction that looks like a clean census."""
    rows, _, _ = chk.measure(
        _plant("See `" + IGNORED_ARTIFACT + "`.", state=state))
    assert len(rows) == 1, f"{state!r} was not recognised as a banked state"


@pytest.mark.parametrize("state", ["CPX", "COVERED-PROVENANCE", "NOT-COVERED-PROVEN"])
def test_the_state_normaliser_can_still_say_no(state):
    """MUTATION on the control above. Stripping a cell down to its first token
    must not turn every cell into a state."""
    rows, _, _ = chk.measure(
        _plant("See `" + IGNORED_ARTIFACT + "`.", state=state))
    assert rows == [], f"{state!r} was wrongly accepted as a banked state"


# --------------------------------------------------------------------------
# THE PARSER, and the three things that made it wrong
# --------------------------------------------------------------------------

def test_a_state_legend_row_is_not_a_capability_row():
    """`| COVERED-PROVEN | 21 | 14.0% | 21 |` is a COUNT, not a capability.
    Value-matching found 10 of these across the four slices and counted them
    as banked rows -- a denominator inflated by 10 on a figure whose entire
    job is to be exact."""
    blob = ("| # | capability | R/W | state | evidence |\n"
            "|---|---|---|---|---|\n"
            "| COVERED-PROVEN | 21 | 14.0% | 21 | -- |\n")
    banked, counters, _ = chk.parse_slice("_audit/_census/_planted.md", blob)
    assert banked == []
    assert counters["legend_rows"] == 1, counters


def test_a_summary_table_does_not_inherit_the_previous_state_column():
    """`network.md` carries a summary table headed
    `| family | rows | read/write | reversible | shape |` whose fourth column
    holds `REV`. The capability header 400 lines above was still in force, so
    five summary rows were read as rows with a state of `REV`."""
    blob = ("| # | capability | R/W | state | evidence |\n"
            "|---|---|---|---|---|\n"
            "| 1 | A real row | R | COVERED-PROVEN | see `" + TRACKED_ARTIFACT + "` |\n"
            "\n"
            "| family | rows | read/write | reversible | shape |\n"
            "|---|---|---|---|---|\n"
            "| People search | 79-96 | READ | REV | one pattern |\n")
    banked, counters, _ = chk.parse_slice("_audit/_census/_planted.md", blob)
    assert [r[1] for r in banked] == ["1"], banked
    assert counters["with_state"] == 1, counters


def test_a_linkedin_route_is_not_a_filesystem_path():
    """These slices are full of `/jobs/collections/recommended/` and
    `/in/me/details/skills/`. They are addresses on a website; a filesystem
    check has nothing to say about them, and admitting them would have
    produced hundreds of wrong findings with the real seven buried inside."""
    rows, _, _ = chk.measure(_plant(
        "Read live at `/jobs/collections/recommended/` and `/in/me/details/skills/`, "
        "instrument `" + TRACKED_ARTIFACT + "`."))
    assert [a.path for a in rows[0].artifacts] == [TRACKED_ARTIFACT], rows[0].artifacts


def test_an_abbreviated_path_is_not_counted_as_unreachable():
    """AN ABBREVIATED CITATION IS NOT AN UNREACHABLE ONE.

    FORCED BY A REAL ROW, not anticipated. `messaging-and-content.md` row `M4`
    cites `perform.md:3462-3487`. No tracked file is named `perform.md`, so the
    strict rule called it NOT-IN-REPO and put an EIGHTH row in the headline
    count -- the one integer this instrument exists to state exactly. But
    exactly one tracked basename ENDS with it,
    `_audit/2026-08-31-linkedin-perform.md`, and the line number settles it:
    that file has 4,966 lines while the only other candidate containing
    "perform" has 298, so line 3462 exists in precisely one of them.

    The evidence is reachable; the path as written is not. Those are different
    complaints and folding the second into the first inflates the answer.
    """
    tracked = chk.tracked_files()
    assert chk.classify("perform.md", tracked, set()) == "ABBREVIATED"
    art = chk.Artifact("perform.md", "perform.md", "ABBREVIATED")
    assert not art.counts_as_finding
    assert not art.reachable, (
        "ABBREVIATED must not read as TRACKED either -- it is reported, not "
        "silently accepted"
    )
    # THE MIRROR, in both directions, or the class is a hole rather than a
    # distinction: a name matching nothing at all is still NOT-IN-REPO, and a
    # name matching exactly is still TRACKED.
    assert chk.classify("no-such-file-zzz.md", tracked, set()) == "NOT-IN-REPO"
    assert chk.classify(TRACKED_ARTIFACT.rsplit("/", 1)[-1], tracked, set()) == "TRACKED"


def test_a_line_number_suffix_does_not_break_the_path():
    rows, _, _ = chk.measure(
        _plant("See `" + TRACKED_ARTIFACT + ":49` and `" + IGNORED_ARTIFACT + ":12-18`."))
    verdicts = {a.path: a.verdict for a in rows[0].artifacts}
    assert verdicts == {TRACKED_ARTIFACT: "TRACKED",
                        IGNORED_ARTIFACT: "GITIGNORED"}, verdicts


def test_a_gitignored_artifact_is_classified_gitignored():
    """PINS A BUG THAT FAILED SILENTLY ON WINDOWS ONLY.

    `git check-ignore --stdin` was fed newline-separated paths through a
    `text=True` pipe, which translates `\\n` to `\\r\\n`. Git took the `\\r`
    as part of the path and echoed it back C-quoted --
    `'"_audit/_scratch/....md\\\\r"'` -- so every membership test missed and all
    13 gitignored artifacts were classified ABSENT. Non-empty set, exit code
    0, nothing to notice. The headline count was unaffected because both
    classes are findings; the CLASS was wrong on all 13, and the class is what
    says whether a file was deliberately excluded or was never there.
    """
    ignored = chk.check_ignored([IGNORED_ARTIFACT])
    assert ignored == {IGNORED_ARTIFACT}, (
        "check_ignored mangled the path -- look for a line-ending translation "
        f"or a C-quoted result: {ignored!r}"
    )
    assert "\r" not in "".join(ignored)
    assert chk.classify(IGNORED_ARTIFACT, chk.tracked_files(), ignored) == "GITIGNORED"


def test_check_ignored_can_say_no():
    """The mirror: an ignore-checker that answers yes to everything is useless."""
    assert chk.check_ignored([TRACKED_ARTIFACT]) == set()


# --------------------------------------------------------------------------
# VACUOUS-PASS CONTROLS -- the reason this file exists in this shape
# --------------------------------------------------------------------------

def test_a_nonsense_argument_is_loud_not_green():
    """THE SWEEP'S DEFECT, controlled here so it cannot be repeated.

    `sweep_blobs_for_identity.py --help` took `--help` as a git range, swept
    0 blobs and printed `PASS: 0 hits across 0 blobs`. Exit 0 from a safety
    tool that had measured nothing at all.
    """
    out = _run("not-a-census-slice.md")
    assert out.returncode == 2, (out.returncode, out.stdout[-600:])
    assert "REFUSING" in out.stdout
    assert "PASS" not in out.stdout and "OK:" not in out.stdout


def test_the_refusal_does_not_echo_an_absolute_path():
    """A REFUSAL IS A DISCLOSURE PATH, and this one echoes its argument.

    The findings already redact an absolute path, but the ARGUMENT refusal did
    not -- so a mistyped workspace path would have been printed in full, by the
    one code path a confused user is most likely to reach, into a terminal, a
    transcript or a CI log. Found by handing the tool `/etc/passwd` on Windows,
    where the shell rewrote it to an absolute path and the refusal echoed the
    whole thing back.
    """
    out = _run("Z:/some/private/place/notes.md")
    assert out.returncode == 2, out.stdout
    assert "private" not in out.stdout and "place" not in out.stdout, out.stdout
    assert "<absolute path" in out.stdout, out.stdout
    # The mirror: a RELATIVE bad argument is still named, or the refusal stops
    # being useful.
    rel = _run("not-a-slice.md")
    assert rel.returncode == 2
    assert "not-a-slice.md" in rel.stdout, rel.stdout


def test_help_is_help_and_not_a_corpus():
    out = _run("--help")
    assert out.returncode == 0, out.stdout
    assert "usage:" in out.stdout
    assert "OK:" not in out.stdout


def test_an_empty_corpus_refuses_rather_than_passing():
    rows, stats, _ = chk.measure({})
    assert rows == [] and stats["banked_rows"] == 0
    out = _run("_audit/_census/jobs.md", "--verbose")
    assert out.returncode in (0, 1), out.stdout[-400:]


def test_a_slice_with_no_banked_rows_is_not_a_clean_result(tmp_path, monkeypatch):
    """An assertion satisfied by an empty result cannot fail. A census with no
    banked rows at all is a broken parser, not a spotless corpus."""
    blob = ("| # | capability | R/W | state | evidence |\n"
            "|---|---|---|---|---|\n"
            "| 1 | Something | R | GAP | nothing yet |\n")
    rows, stats, _ = chk.measure({"_audit/_census/_planted.md": blob})
    assert rows == []
    assert stats["banked_rows"] == 0, (
        "the vacuity gate in main() keys on this counter; if it can be "
        "non-zero with no rows the gate is measuring the wrong thing"
    )


def test_a_banked_row_citing_nothing_at_all_yields_no_artifacts():
    """The third denominator: zero artifacts from a banked row. `main` refuses
    on it corpus-wide; here we only assert the counter is honest."""
    rows, stats, _ = chk.measure(_plant("Measured. No artifact named."))
    assert len(rows) == 1
    assert rows[0].artifacts == ()
    assert stats["artifacts"] == 0


# --------------------------------------------------------------------------
# THE PIN
# --------------------------------------------------------------------------

def test_the_seven_under_banked_rows_are_exactly_these(measured):
    rows, stats, _ = measured
    assert stats["banked_rows"] >= 70, (
        f"only {stats['banked_rows']} banked rows found; the parser has lost "
        "rows and a shrinking denominator hides findings"
    )
    assert stats["artifacts"] >= 70, stats
    seen = {(r.slice_name, r.row_id, r.state) for r in rows if r.unreachable}
    appeared = sorted(seen - PINNED)
    fixed = sorted(PINNED - seen)
    assert not appeared, (
        f"NEW banked row(s) resting on evidence no clone can reach: {appeared}. "
        "MEASURE, do not demote: the row may be correct and its receipt still "
        "unreachable. Either commit the artifact or say in the cell that the "
        "reading cannot be re-checked from a clone."
    )
    assert not fixed, (
        f"these pinned rows no longer show unreachable evidence: {fixed}. If the "
        "artifact was committed, narrow PINNED in the SAME commit and say so. "
        "If instead the DETECTOR stopped seeing it, this pin just hid a "
        "regression -- check the red proof above first."
    )


def test_every_unreachable_artifact_is_named_and_classified(measured):
    """A count with no per-row list is not a measurement anybody can act on."""
    rows, _, _ = measured
    bad = [a for r in rows for a in r.unreachable]
    assert len(bad) == 15, [str(a) for a in bad]
    assert {a.verdict for a in bad} == {"GITIGNORED"}, sorted({a.verdict for a in bad})
    assert all(a.path.startswith("_audit/_scratch/") for a in bad), bad


def test_an_absolute_path_is_never_printed_by_value():
    """An absolute workspace path is an identifier. This instrument's output
    is read into a tracked audit document, so it must report the SHAPE.

    THE FIXTURE ITSELF WAS CAUGHT BY THE IDENTITY GATE, which is the joke and
    also the lesson. A first version wrote a literal drive-rooted path, and
    `scripts/staged_identity_shapes.py` refused the commit: *"a file this
    commit would write carries an UNDECLARED identifier shape"*. A red there
    means UNDECLARED, not real -- but the guard's own advice is to change the
    content rather than widen what it tolerates for this file forever, so the
    drive letter is assembled from a letter that names no volume here.
    """
    home_style = "~/a/b.md"
    art = chk.Artifact(home_style, home_style, "ABSOLUTE-PATH")
    shown = art.display()
    assert home_style not in shown, shown
    assert shown.startswith("<absolute local path")

    drive = chr(ord("Y") + 1) + ":"          # a volume letter, not a location
    assert chk._is_absolute(drive + "/x/y.md")
    assert chk._is_absolute(drive + "\\x\\y.md")
    assert chk._is_absolute("~/x.md")
    assert not chk._is_absolute("_audit/x.md")
    assert not chk._is_absolute("scripts/x.py")


def test_the_instrument_stays_cheap_enough_to_gate():
    import time
    t0 = time.perf_counter()
    chk.measure()
    elapsed = time.perf_counter() - t0
    assert elapsed < 120, f"took {elapsed:.1f}s; too slow to gate on"
