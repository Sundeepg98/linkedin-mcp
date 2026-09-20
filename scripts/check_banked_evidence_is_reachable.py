"""Can a reader who CLONES this repository reach the evidence under a banked row?

THE DEFECT CLASS, and it is not a broken link. A census row in a banked state
-- COVERED-PROVEN, COVERED-CANNOT-DELIVER, MEASURED-ABSENT -- is a claim that
something was measured. The row states the numbers. If the artifact those
numbers came from is somewhere a clone cannot reach, the numbers are still
there, still stated with full confidence, and **checkable nowhere**. Nothing
looks wrong. An over-stated figure survives until somebody opens a machine that
still has the file, and that machine is one laptop.

FOUND BY HAND FIRST, on five rows. `_audit/2026-09-20-the-five-under-banked.md`
section 8 traced `jobs.md` rows 9, 11, 12, 13 and 14 to
`_audit/_scratch/_progress-job-search-params.md`. `.gitignore:156` quarantines
`_audit/_scratch/` unconditionally; `git ls-files _audit/_scratch/` returns
nothing. Worse, the raw probe output those numbers came from had been
overwritten twice, forty minutes before the document quoting them was written.
Five banked rows, an evidence chain ending outside the repository, and a guard
that passed them -- correctly, because they CITE rather than DEFER and the
existing `test_no_committed_document_defers_to_an_ignored_path` asks a
different question.

This file asks the reachability question directly, over the whole corpus.

============================================================================
IT MEASURES. IT DOES NOT DEMOTE.
============================================================================

Moving a row out of a banked state is a RULING and it belongs to whoever owns
the census. This instrument produces a count and a per-row list naming the
specific artifact a reader cannot reach. It never edits a census, never
proposes a state, and its exit status means "the measurement ran", not "these
rows are wrong".

============================================================================
WHY IT CANNOT PASS VACUOUSLY
============================================================================

An hour before this was written, `sweep_blobs_for_identity.py --help` accepted
`--help` as a git range, swept 0 blobs and printed *"PASS: 0 hits across 0
blobs"*. A garbage argument produced a green from a safety tool. Every stage
here refuses instead:

    a named census slice is missing                 -> exit 2
    a slice parses to zero table rows               -> exit 2
    zero rows in a banked state anywhere            -> exit 2
    zero artifacts extracted from any banked row    -> exit 2
    an argument that is not a known slice           -> exit 2, naming it
    --help / -h                                     -> usage, exit 0

and **an empty finding set is only a PASS when the denominators above are all
non-zero**, which is printed on every run above the verdict.

============================================================================
WHAT COUNTS AS UNREACHABLE
============================================================================

Reachable means: the artifact is TRACKED IN GIT. That is the whole test, and
it is the only one that describes what a clone contains. Everything else is a
named class of unreachable:

    GITIGNORED        the path is tracked by nobody and `.gitignore` excludes
                      it -- `_audit/_scratch/`, `_state/`, `*.html` captures
    ABSENT            not tracked and not on this disk either; the citation
                      names a file that does not exist anywhere reachable
    UNTRACKED-LOCAL   present on THIS box and tracked by nobody, so it reaches
                      this machine and no other -- the session-local capture
    ABSOLUTE-PATH     an absolute filesystem path; it is also an identifier,
                      so it is reported by SHAPE and never by value
    NOT-IN-REPO       a bare filename with an extension that matches no
                      tracked file at all

and one row-level class, reported separately because it is weaker evidence:

    NO-RERUNNABLE-SCRIPT   the cell describes a live run -- loads, a session,
                      "fired live" -- and cites no tracked script that could
                      take the reading again. The run is a story, not a method.

**AMBIGUOUS is not a finding and is never counted as one.** A bare filename
matching several tracked files, or a token this extractor cannot classify, is
printed in its own section with its count, because a refusal that names only
what it did NOT match is half a measurement.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import NamedTuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

#: THE STATE VOCABULARY IS IMPORTED, NOT REBUILT. `count_census_states` already
#: owns this problem and owns it better: it holds `ER`, `CCD` and
#: `CANNOT-DELIVER` as well as the long forms, each admitted with a receipt, and
#: `tests/test_state_cell_dialects_refuse_loudly.py` guards it. A hand-rolled
#: vocabulary here would have been the THIRD in this repository, and the repo's
#: own scar on that -- *"I wrote two broken versions of a check this repo
#: already ships"* -- is explicit.
#:
#: MEASURED BEFORE AND AFTER THE SWITCH, because importing an instrument is a
#: change to the measurement and not a tidy-up: the banked-row count and the
#: finding count are both printed on every run, and the switch moved neither.
#: What it buys is the dialects, and a LOUD report if a slice ever invents a new
#: one instead of that row silently not being banked.
from count_census_states import STATES as SHIPPED_STATES  # noqa: E402
from count_census_states import cells as shipped_cells  # noqa: E402
from count_census_states import classify as shipped_classify  # noqa: E402

#: The four capability census slices. NAMED, not globbed: `mcp-inventory.md`
#: lives in the same directory and is the INWARD half of the census, with a
#: different schema entirely (`PROVEN-LIVE` / `TESTED-ONLY` / `UNKNOWN`) and no
#: `state` column of this vocabulary. A glob would silently pull it in and its
#: rows would parse to nothing, which reads as a clean slice.
SLICES = (
    "_audit/_census/jobs.md",
    "_audit/_census/messaging-and-content.md",
    "_audit/_census/network.md",
    "_audit/_census/profile.md",
)

#: A state is BANKED when the row asserts the capability was established.
#: `jobs.md` declares abbreviations in its own legend (:172) -- *"`state`
#: values: **CP** = COVERED-PROVEN, **CU** = COVERED-UNFIRED, **XR** =
#: EXCLUDED-RULED"* -- and uses both spellings in the same table: 19 rows say
#: `CP` and 9 say `COVERED-PROVEN`. A matcher that knows only the long form
#: reads 9 where the answer is 28, and it fails in the direction that looks
#: like a clean corpus.
#: `CANNOT-DELIVER` is `messaging-and-content.md`'s own first spelling of
#: COVERED-CANNOT-DELIVER and cost two rows their census membership for eleven
#: commits; it is in the shipped vocabulary under its own key and is banked
#: here for the same reason the long form is.
BANKED = frozenset({
    "COVERED-PROVEN", "CP",
    "COVERED-CANNOT-DELIVER", "CCD", "CANNOT-DELIVER",
    "MEASURED-ABSENT",
})

#: Every state spelling these slices use, taken from the shipped vocabulary
#: rather than re-enumerated. `SKILL` is added because `jobs.md` writes
#: ``GAP `SKILL``` and ``MEASURED-ABSENT `SKILL``` -- a marker beside a state,
#: not a state -- and the first token rule already strips it.
KNOWN_STATES = frozenset(SHIPPED_STATES) | frozenset({"SKILL"})

#: ANY BANKED SPELLING THE SHIPPED VOCABULARY DOES NOT HOLD would be silently
#: un-banked, so it is asserted at import rather than discovered in a count.
_UNSHIPPED = set(BANKED) - set(SHIPPED_STATES)
if _UNSHIPPED:
    raise SystemExit(
        "REFUSING TO LOAD: these banked spellings are not in the shipped "
        "vocabulary of scripts/count_census_states.py: " + repr(sorted(_UNSHIPPED))
        + "\n  Rows spelled that way would not be banked here and nothing "
          "would say so. Teach the shipped vocabulary first."
    )

#: File extensions this corpus cites as evidence.
EXTENSIONS = (".py", ".md", ".json", ".tsv", ".txt", ".html", ".yml",
              ".yaml", ".log", ".csv", ".jsonl")

#: Vocabulary that means "a live reading was taken". Measured against the
#: corpus rather than invented: each phrase below appears in a banked cell.
RUN_WORDS = ("loads,", " loads ", "one session", "fired live", "live-fire",
             "measured live", "read live", "re-run", "rerun", "capture",
             "this session", "live reading")


class Artifact(NamedTuple):
    raw: str
    path: str
    verdict: str          # TRACKED / GITIGNORED / ABSENT / UNTRACKED-LOCAL /
    #                       ABSOLUTE-PATH / NOT-IN-REPO / AMBIGUOUS

    @property
    def reachable(self) -> bool:
        return self.verdict == "TRACKED"

    @property
    def counts_as_finding(self) -> bool:
        return self.verdict not in ("TRACKED", "AMBIGUOUS")

    def display(self) -> str:
        # An absolute path is an identifier. Report its SHAPE, never its value.
        if self.verdict == "ABSOLUTE-PATH":
            return "<absolute local path, " + str(len(self.path)) + " chars>"
        return self.path


class Row(NamedTuple):
    slice_name: str
    line: int
    row_id: str
    state: str
    evidence: str
    artifacts: tuple[Artifact, ...]

    @property
    def unreachable(self) -> tuple[Artifact, ...]:
        return tuple(a for a in self.artifacts if a.counts_as_finding)

    @property
    def reachable(self) -> tuple[Artifact, ...]:
        return tuple(a for a in self.artifacts if a.reachable)


def _git(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], input=stdin,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def tracked_files() -> set[str]:
    out = _git("ls-files")
    if out.returncode != 0:
        raise SystemExit("REFUSING: `git ls-files` failed: " + out.stderr.strip())
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def _split_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_absolute(tok: str) -> bool:
    if len(tok) > 2 and tok[1] == ":" and (tok[2] == "\\" or tok[2] == "/"):
        return True            # a drive-letter path
    return tok.startswith("~/") or tok.startswith("/c/") or tok.startswith("/d/")


def _clean(tok: str) -> str:
    """Trim a citation down to the path it names.

    Plain string work on purpose. Python's `\\b` treats `_` as a word
    character, and that single fact minted eleven phantom citations for a
    sibling wave this week; this corpus is full of `_leading_underscore`
    filenames, so a regex boundary here would be wrong in exactly the places
    that matter.
    """
    tok = tok.strip().strip("*")
    for lead in ("(", "[", "<", '"', "'"):
        while tok.startswith(lead):
            tok = tok[1:]
    for trail in (")", "]", ">", '"', "'", ".", ",", ";", ":", "!", "?"):
        while tok.endswith(trail):
            tok = tok[:-1]
    # `_audit/x.md:49` and `_audit/x.md:49-52` name a LINE, not a file.
    if ":" in tok:
        head, _, tail = tok.rpartition(":")
        if head and tail and tail.replace("-", "").isdigit():
            tok = head
    return tok


def _candidate_tokens(cell: str) -> list[str]:
    """Every token in a cell that could name a file.

    Backticked spans first, because that is how this corpus cites an artifact;
    then bare whitespace-separated tokens, so a citation somebody forgot to
    quote is not invisible.
    """
    out: list[str] = []
    parts = cell.split("`")
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part)
        else:
            out.extend(part.split())
    return [t for t in (_clean(x) for x in out) if t]


def classify(tok: str, tracked: set[str], ignored: set[str]) -> str:
    if _is_absolute(tok):
        return "ABSOLUTE-PATH"
    if tok in tracked:
        return "TRACKED"
    if "/" in tok:
        # A directory citation is reachable when anything under it is tracked.
        prefix = tok if tok.endswith("/") else tok + "/"
        if any(f.startswith(prefix) for f in tracked):
            return "TRACKED"
        if tok in ignored or any(tok.startswith(i) for i in ignored):
            return "GITIGNORED"
        return "ABSENT" if not (ROOT / tok).exists() else "UNTRACKED-LOCAL"
    # A bare filename: does exactly one tracked file end with it?
    hits = [f for f in tracked if f.rsplit("/", 1)[-1] == tok]
    if len(hits) == 1:
        return "TRACKED"
    if len(hits) > 1:
        return "AMBIGUOUS"
    return "NOT-IN-REPO"


#: Top-level directories of THIS repository. A citation like `_audit/_scratch/`
#: names a directory rather than a file and must still be classified, so a
#: token is admitted on a known first segment as well as on an extension.
REPO_DIRS = ("_audit/", "scripts/", "tests/", "linkedin_server/", "_state/",
             ".github/", "docs/", "fixtures/")

#: Characters no path in this repository contains, and every one of them
#: appears in this corpus inside something that is NOT a file.
_NOT_IN_A_PATH = "<>?*|\"' \t"


def _looks_like_a_path(tok: str) -> bool:
    """Is this token naming a FILE IN THIS REPOSITORY?

    **A LEADING `/` IN THIS CORPUS IS A LINKEDIN ROUTE, NOT A PATH.** These
    slices are full of `/jobs/collections/recommended/`, `/in/me/details/
    skills/` and `/feed/update/<urn>/`; they are addresses on a website and a
    filesystem check has nothing to say about them. The first version of this
    function admitted them, and the very first run died inside
    `git check-ignore` on a token that had been cleaned down to `/`. That is
    the good failure -- it was LOUD. Had `check-ignore` merely shrugged, every
    route would have been classified ABSENT and this instrument would have
    reported hundreds of unreachable artifacts, all of them wrong, and the
    real five would have been invisible inside the noise.
    """
    if _is_absolute(tok):
        return True
    if not tok or any(c in tok for c in _NOT_IN_A_PATH):
        return False
    if tok.startswith("/"):
        return False
    if tok.strip("/.") == "":
        return False
    if tok.lower().endswith(EXTENSIONS):
        return True
    return tok.endswith("/") and tok.startswith(REPO_DIRS)


def check_ignored(paths: list[str]) -> set[str]:
    """Which of these does `.gitignore` exclude? One batched call.

    **`-z`, AND IT IS NOT A TIDINESS CHOICE.** The newline form of this call
    is wrong on Windows and wrong SILENTLY. `subprocess` with `text=True`
    translates the `\\n` separators to `\\r\\n` on write, git takes the `\\r`
    as part of the path, finds the rule matches anyway, and echoes the path
    back C-quoted with the carriage return still in it::

        {'"_audit/_scratch/_progress-job-search-params.md\\\\r"'}

    Nothing fails. The set is non-empty, the exit code is 0, and every
    membership test against it misses -- so every gitignored artifact in the
    corpus was classified ABSENT instead of GITIGNORED. Both are findings, so
    the headline count did not move; the CLASS did, on all 13 of them, and the
    class is what tells a reader whether a file was deliberately excluded or
    was never there. Found by probing one known-ignored path rather than by
    reading the code, and pinned by
    `test_a_gitignored_artifact_is_classified_gitignored`.

    NUL-separated in both directions: no translation, no quoting, no escape.
    """
    if not paths:
        return set()
    out = _git("check-ignore", "--stdin", "-z", stdin="\0".join(paths) + "\0")
    # exit 0 = some ignored, 1 = none ignored, >1 = error.
    if out.returncode > 1:
        raise SystemExit("REFUSING: `git check-ignore` failed: " + out.stderr.strip())
    return {p for p in out.stdout.split("\0") if p}


def normalise_state(cell: str) -> str:
    """The state a cell names, stripped of everything a wave wrote beside it.

    MEASURED, AND IT WAS WORTH FOUR ROWS. A first version took the cell whole
    and compared it to the vocabulary. The corpus writes the state with things
    attached:

        `**CP 2026-09-19**`               jobs.md:237, row 44 -- BANKED
        `**COVERED-PROVEN 2026-09-05**`   profile.md:335, row G7 -- BANKED
        `**COVERED-PROVEN 2026-09-19**`   profile.md:462, row N2 -- BANKED
        `MEASURED-ABSENT `SKILL``         network.md -- BANKED
        `GAP `SKILL``                     jobs.md:225-228 -- not banked
        `EXCLUDED-RULED (R3)`             network.md -- not banked

    Four banked rows were being read as unknown states and dropped. They were
    only visible because this file PRINTS every state spelling it does not
    know instead of silently treating it as not-banked -- a refusal that names
    only what it did not match is half a measurement, and here the other half
    was 4 rows of the answer.
    """
    cell = cell.strip().strip("*").strip()
    cell = cell.replace("`", " ").replace("*", " ")
    cell = cell.split(" (")[0]
    parts = cell.split()
    return parts[0].strip() if parts else ""


def parse_slice(rel: str, blob: str) -> tuple[list[tuple[int, str, str, str]], dict, list[str]]:
    """(banked rows, counters, unknown state spellings).

    THE STATE CELL IS FOUND BY VALUE, WITH THE HEADER AS THE TIEBREAK, and
    both halves were forced by a measurement rather than chosen.

    By header alone: these slices put `state` in different columns --
    `network.md` and `profile.md` read `| # | capability | R/W | state | note |`
    while `messaging-and-content.md` reads
    `| # | capability | Help Center | state | R/W | REV | evidence |`. Fine so
    far. But a header index also SURVIVES INTO THE NEXT TABLE: `network.md`
    carries a summary table headed `| family | rows | read/write | reversible |
    shape |` whose fourth column holds `REV`, and the capability header from
    400 lines earlier was still in force, so five summary rows were read as
    rows with a state of `REV`. And requiring the row's cell count to match the
    header's silently discarded **121 rows** across the four slices, some of
    them malformed capability rows -- `network.md:319` is a real row whose
    state cell swallowed its note.

    By value alone: a row is a capability row when exactly one of its cells
    NAMES A STATE. The summary table names none and is skipped, malformed rows
    are still read, and nothing depends on a count matching.

    The header still wins when it agrees, because it is the author's own
    declaration; value-matching is the fallback, and a row where several cells
    name a state is reported as AMBIGUOUS rather than guessed at.
    """
    banked: list[tuple[int, str, str, str]] = []
    counters = {"table_lines": 0, "with_state": 0, "no_state": 0, "ambiguous": 0,
                "legend_rows": 0, "dialects": 0}
    unknown: list[str] = []
    header_idx: int | None = None
    for lineno, line in enumerate(blob.splitlines(), 1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = shipped_cells(stripped)
        lowered = [c.lower() for c in cells]
        if "state" in lowered:
            header_idx = lowered.index("state")
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue                       # the |---|---| separator
        counters["table_lines"] += 1

        # THE SHIPPED CLASSIFIER DECIDES THE STATE. It skips cell 0 (so a
        # state-legend row -- `| COVERED-PROVEN | 21 | 14.0% | 21 |` -- is not
        # a capability row, which cost this file 10 rows of denominator before
        # the switch), it takes the first token of a cell (so `**CP
        # 2026-09-19**` reads as `CP`, worth 4 banked rows), and it reports a
        # MISSPELLED state separately instead of letting the row vanish.
        state, dialects = shipped_classify(cells)
        # SCOPED TO CAPABILITY-SHAPED ROWS, and the scope was measured. Over
        # the whole of these four slices the shipped `dialect_of` reports
        # exactly two hits, both on `network.md` lines 171-172:
        #     | `/in/<member>/recent-activity/` | ABSENT |
        # a two-column table about page ADDRESSES, where `ABSENT` means the
        # page is not drawn. It is a shouted word built only from the state
        # vocabulary's own atoms, so the heuristic cannot help but see it. A
        # capability row in these slices has at least four cells; reporting
        # those two as misspelled states would be crying wolf in the one place
        # this instrument most needs to be believed.
        if dialects and len(cells) >= 4:
            counters["dialects"] += 1
            unknown.extend(dialects)
        named = [i for i, c in enumerate(cells)
                 if i != 0 and normalise_state(c) in KNOWN_STATES]
        legend_only = bool(state) is False and any(
            normalise_state(c) in KNOWN_STATES for c in cells[:1])
        if legend_only and not named:
            counters["legend_rows"] += 1
            continue
        if not named:
            counters["no_state"] += 1
            # REPORT ONLY THE CELL WHERE A STATE SHOULD HAVE BEEN. Scanning
            # every cell for an unrecognised spelling buries the signal: the
            # first run printed 32 spellings, almost all of them the first word
            # of a summary table's prose. The informative case is narrow -- a
            # row under a header that declares a `state` column, whose state
            # cell this file does not recognise.
            if (header_idx is not None and len(cells) > header_idx
                    and len(cells[0]) <= 8):
                # A capability row's id is short -- `9`, `M44`, `C40`, `L2b`.
                # A summary table's first cell is a phrase, and a `state`
                # header from an earlier table is still in force when one is
                # reached, so without this the report fills with the first
                # word of unrelated prose.
                cell = cells[header_idx]
                s = normalise_state(cell)
                if s and len(cell) < 60 and s not in KNOWN_STATES:
                    unknown.append(s)
            continue
        if header_idx is not None and header_idx in named:
            idx = header_idx
        elif len(named) == 1:
            idx = named[0]
        else:
            counters["ambiguous"] += 1
            continue
        counters["with_state"] += 1
        here = normalise_state(cells[idx])
        # THE SHIPPED CLASSIFIER AND THE HEADER COLUMN MUST AGREE, and a
        # disagreement is printed rather than resolved by preference: it means
        # one of them is reading a different cell from the author's, which is
        # the masking case `count_census_states.classify` was built to surface.
        if state and here and state != here:
            counters["ambiguous"] += 1
            unknown.append(state + "!=" + here)
            continue
        if here in BANKED:
            evidence = cells[-1] if idx != len(cells) - 1 else cells[idx]
            banked.append((lineno, cells[0].strip().strip("*` "), here, evidence))
    return banked, counters, unknown


def measure(repo_blobs: dict[str, str] | None = None) -> tuple[list[Row], dict[str, int], list[str]]:
    tracked = tracked_files()
    blobs: dict[str, str] = {}
    if repo_blobs is not None:
        blobs = dict(repo_blobs)
    else:
        for rel in SLICES:
            path = ROOT / rel
            if not path.exists():
                raise SystemExit(
                    "REFUSING: census slice not found: " + rel + "\n"
                    "  A missing slice would be measured as zero banked rows, "
                    "which reads as a clean slice."
                )
            blobs[rel] = path.read_text(encoding="utf-8", errors="replace")

    stats = {"table_rows": 0, "banked_rows": 0, "artifacts": 0, "slices": len(blobs),
             "rows_with_a_state": 0, "rows_with_no_state": 0, "rows_ambiguous": 0,
             "legend_rows": 0, "dialects": 0}
    unknown_states: list[str] = []
    staged: list[tuple[str, int, str, str, str, list[str]]] = []
    every_token: list[str] = []

    for rel in sorted(blobs):
        parsed, counters, unknown = parse_slice(rel, blobs[rel])
        seen = counters["with_state"]
        stats["table_rows"] += counters["table_lines"]
        stats["rows_with_a_state"] += counters["with_state"]
        stats["rows_with_no_state"] += counters["no_state"]
        stats["rows_ambiguous"] += counters["ambiguous"]
        stats["legend_rows"] += counters["legend_rows"]
        stats["dialects"] += counters["dialects"]
        unknown_states.extend(unknown)
        if repo_blobs is None and seen == 0:
            raise SystemExit(
                "REFUSING: " + rel + " parsed to ZERO table rows.\n"
                "  The header-row parser found no `state` column, so every row "
                "in this slice was skipped. That is a broken parser reporting a "
                "spotless census."
            )
        for lineno, row_id, state, evidence in parsed:
            stats["banked_rows"] += 1
            toks = [t for t in _candidate_tokens(evidence) if _looks_like_a_path(t)]
            every_token.extend(toks)
            staged.append((rel, lineno, row_id, state, evidence, toks))

    ignored = check_ignored(sorted({t for t in every_token if not _is_absolute(t)}))

    rows: list[Row] = []
    for rel, lineno, row_id, state, evidence, toks in staged:
        arts = tuple(
            Artifact(t, t, classify(t, tracked, ignored)) for t in dict.fromkeys(toks)
        )
        stats["artifacts"] += len(arts)
        rows.append(Row(rel, lineno, row_id, state, evidence, arts))

    return rows, stats, unknown_states


def names_a_run_with_no_script(row: Row, tracked: set[str]) -> bool:
    low = row.evidence.lower()
    if not any(w in low for w in RUN_WORDS):
        return False
    return not any(
        a.verdict == "TRACKED" and a.path.startswith("scripts/") for a in row.artifacts
    )


USAGE = """usage: check_banked_evidence_is_reachable.py [-v] [--rows] [SLICE ...]

Measures whether a reader cloning this repository can reach the evidence
under every census row in a banked state. It MEASURES; it never demotes.

  -v, --verbose   print every artifact of every banked row, not only findings
  --rows          print the full per-row finding list (default)
  SLICE           limit to one or more of the four census slices, by path

exit 0  the measurement ran and every banked row's evidence is reachable
exit 1  the measurement ran and found unreachable evidence
exit 2  the measurement could not honestly run (see the message)
"""


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "-h" in argv or "--help" in argv:
        print(USAGE)
        return 0
    verbose = "-v" in argv or "--verbose" in argv
    wanted = [a for a in argv if not a.startswith("-")]
    unknown_args = [a for a in wanted if a.replace("\\", "/") not in SLICES]
    if unknown_args:
        # THE REFUSAL ECHOES WHAT IT WAS HANDED, AND THAT IS A DISCLOSURE PATH.
        # This output reaches terminals, transcripts and CI logs. An absolute
        # path is an identifier by this repository's own rule, and the
        # findings already redact one -- but the ARGUMENT refusal did not, so
        # a mistyped workspace path would have been printed in full by the one
        # code path a confused user is most likely to reach. Found by handing
        # the tool `/etc/passwd`, which the shell rewrote to an absolute path
        # and the refusal echoed back whole.
        shown = [
            "<absolute path, " + str(len(a)) + " chars>" if _is_absolute(a) else a
            for a in unknown_args
        ]
        print("REFUSING: not a census slice: " + ", ".join(shown))
        print("  Known slices:")
        for s in SLICES:
            print("    " + s)
        print("  An unrecognised argument would measure an empty corpus and "
              "print a clean result.")
        return 2

    blobs = None
    if wanted:
        blobs = {}
        for rel in wanted:
            rel = rel.replace("\\", "/")
            blobs[rel] = (ROOT / rel).read_text(encoding="utf-8", errors="replace")

    rows, stats, unknown_states = measure(blobs)
    tracked = tracked_files()

    print("census slices read      : " + str(stats["slices"]))
    print("table lines seen        : " + str(stats["table_rows"]))
    print("  rows naming a state   : " + str(stats["rows_with_a_state"]))
    print("  rows naming none      : " + str(stats["rows_with_no_state"])
          + "   (headers, summary tables, prose rows)")
    print("  rows naming several   : " + str(stats["rows_ambiguous"])
          + "   (NOT guessed at)")
    print("  state-legend rows     : " + str(stats["legend_rows"])
          + "   (the state IS the row id; not capabilities)")
    print("  MISSPELLED state cells: " + str(stats["dialects"])
          + "   (shipped dialect_of; a row here is in NO count until fixed)")
    print("rows in a BANKED state  : " + str(stats["banked_rows"]))
    print("evidence artifacts found: " + str(stats["artifacts"]))
    if unknown_states:
        import collections
        print("state spellings this file does not know (treated as NOT banked):")
        for s, n in collections.Counter(unknown_states).most_common():
            print("    " + repr(s) + "  x" + str(n))

    # ---- the vacuity gates, all of them LOUD -------------------------------
    if stats["table_rows"] == 0:
        print("\nZERO TABLE ROWS PARSED. That is a broken parser, not a clean "
              "census. Treating as FAIL.")
        return 2
    if stats["banked_rows"] == 0:
        print("\nZERO ROWS IN A BANKED STATE. Either the state vocabulary "
              "moved or the parser broke; a census with no banked rows at all "
              "is not a result. Treating as FAIL.")
        return 2
    if stats["artifacts"] == 0:
        print("\nZERO EVIDENCE ARTIFACTS EXTRACTED from " + str(stats["banked_rows"])
              + " banked rows. An extractor that finds nothing reports a "
                "spotless corpus. Treating as FAIL.")
        return 2

    bad = [r for r in rows if r.unreachable]
    stranded = [r for r in bad if not r.reachable]
    norun = [r for r in rows if names_a_run_with_no_script(r, tracked)]

    ambiguous = [(r, a) for r in rows for a in r.artifacts if a.verdict == "AMBIGUOUS"]

    print("")
    print("BANKED ROWS WITH AT LEAST ONE UNREACHABLE ARTIFACT : " + str(len(bad)))
    print("  of those, rows with NO reachable artifact at all  : " + str(len(stranded)))
    print("BANKED ROWS DESCRIBING A RUN WITH NO TRACKED SCRIPT : " + str(len(norun)))
    print("artifacts the extractor could not disambiguate      : "
          + str(len(ambiguous)) + "   (NOT counted as findings)")

    by_verdict: dict[str, int] = {}
    for r in rows:
        for a in r.artifacts:
            by_verdict[a.verdict] = by_verdict.get(a.verdict, 0) + 1
    print("")
    print("every artifact, by verdict:")
    for v in sorted(by_verdict):
        print("    {:<16} {}".format(v, by_verdict[v]))

    if verbose:
        print("")
        for r in rows:
            print("  {}:{}  row {}  [{}]".format(
                r.slice_name.split("/")[-1], r.line, r.row_id, r.state))
            for a in r.artifacts:
                print("      {:<16} {}".format(a.verdict, a.display()))

    if bad:
        print("")
        print("PER-ROW FINDINGS -- the specific artifact a clone cannot reach:")
        for r in sorted(bad, key=lambda x: (x.slice_name, x.line)):
            tag = "  [NO REACHABLE EVIDENCE AT ALL]" if not r.reachable else ""
            print("  {} row {} [{}] line {}{}".format(
                r.slice_name.split("/")[-1], r.row_id, r.state, r.line, tag))
            for a in r.unreachable:
                print("      {:<16} {}".format(a.verdict, a.display()))
            if r.reachable:
                print("      (also cites {} reachable artifact(s))".format(len(r.reachable)))

    if norun:
        print("")
        print("ROWS DESCRIBING A LIVE RUN WITH NO TRACKED SCRIPT TO RETAKE IT:")
        for r in sorted(norun, key=lambda x: (x.slice_name, x.line)):
            print("  {} row {} [{}] line {}".format(
                r.slice_name.split("/")[-1], r.row_id, r.state, r.line))

    if ambiguous:
        print("")
        print("AMBIGUOUS, reported because a refusal that names only what it "
              "did NOT match is half a measurement:")
        for r, a in ambiguous[:40]:
            print("  {} row {}  {!r}".format(
                r.slice_name.split("/")[-1], r.row_id, a.raw))

    print("")
    if not bad and not norun:
        print("OK: every banked row's cited evidence is tracked in git, across "
              + str(stats["banked_rows"]) + " banked rows and "
              + str(stats["artifacts"]) + " artifacts.")
        return 0
    print("THIS IS A MEASUREMENT, NOT A RULING. No row is demoted here and none "
          "should be\ndemoted on this output alone: a row can be right and its "
          "receipt still be\nunreachable. The remedy is to move the artifact "
          "into the repository, or to\nstate in the cell that the reading "
          "cannot be re-checked from a clone.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
