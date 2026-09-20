"""Generate `_audit/INDEX.md`: a way into 195 audit documents that is not grep.

THE GAP THIS ANSWERS, measured 2026-09-20. `_audit/` holds 195 git-tracked
markdown documents and 5.4 MB of prose. 59 of them were written on 2026-09-19
and 32 on 2026-09-20. There was no index of any kind, and nothing in `scripts/`
produced one. The only ways in were grep and somebody's memory.

THAT IS NOT A HOUSEKEEPING COMPLAINT. A corpus nobody can navigate is a corpus
nobody RE-READS, and the same day this was measured produced four separate
count-drifts between a machine-checked constant and the prose beside it, a
section asserting a 22-pattern allowlist that had held 42 for a fortnight, and
a `CORRECTED BY:` marker that was itself stale. Every one of those is the same
defect: a claim was overtaken and the reader arriving at it could not tell.

WHAT FAILED WAS NEVER *FINDING A FILE*. It was KNOWING A DOCUMENT HAD BEEN
OVERTAKEN. So the index is built around that, not around filenames.

## The hard constraint: DERIVED, NOT WRITTEN

A hand-written index over 195 documents would be the fifth count-drift of the
day inside a week. Every cell below is computed from the corpus at the SHA it
runs against, and `tests/test_the_audit_index_is_derived.py` re-derives it and
compares line for line. Add a document without regenerating and the suite goes
red. **Nothing here restates a number it did not derive** -- that rule is the
whole reason the file can be trusted a month from now.

## Where the correction graph comes from: IMPORTED, NOT RE-DERIVED

The marker vocabulary (`CORRECTS:` / `CORRECTED BY:`), its line-anchored
pattern, the citation pattern, the three spellings the corpus uses for the same
target, and the rule for where a marker's reason starts ALL come from
`tests/test_a_correction_is_findable_from_the_claim.py`. They are imported.

That file paid for each of them. Its `MARKER` is anchored at line start because
an unanchored version read a SENTENCE DESCRIBING the mechanism as a marker. Its
`_reason_on` starts after the LAST backtick on the line. Its `_documents` asks
git rather than walking the disk, because `_audit/_scratch/` is gitignored and
37 working notes made a check pass locally and fail in a clone at the same SHA.
Re-deriving any of that is how two separate waves shipped broken parsers in one
day.

WHAT IS *NOT* IMPORTED is the iteration -- `for document, for line` -- because
that loop has no blind spot to inherit, and a pure function over an EXPLICIT
document list is what lets the guard plant defects in a temporary directory
instead of mutating a corpus four other waves are writing. The composite is
then asserted equal to the shipped composite over the live corpus, in
`test_the_edge_set_agrees_with_the_shipped_correction_guard`. Reuse where reuse
is load-bearing; reimplement the trivial half; assert the two agree.

## What the index surfaces, and why each earns its place

  DATE          from the `YYYY-MM-DD-` filename prefix. Documents without one
                are printed as undated rather than given a date from git --
                see NOT DERIVED below. How many of each is DERIVED into the
                counts table and deliberately not restated here: a count
                written into prose beside a count the machine maintains is the
                exact drift this corpus produced four times in one day.
  TITLE         the first level-1 ATX heading. Table stakes.
  CORRECTED BY  the documents that declare a correction of this one, with the
                reason this document itself gives for the correction. THIS IS
                THE POINT OF THE FILE. A reader who lands on a claim sees,
                without grep, that something later overtook it.
  CORRECTS      the other direction, so a corrector's reach is visible too.
  SELF-CORRECTED a DIFFERENT RELATION, kept separate: a later section of a
                document correcting an earlier one in the same file. Four such
                markers exist and the shipped guard cannot see any of them --
                they sit behind a blockquote, which its line-start anchor does
                not reach. Flattening them into the graph above would claim a
                cross-document correction nobody declared.

## Two things this file had to survive, both found by its own red proof

**IT MUST NOT INDEX ITSELF.** `_audit/INDEX.md` is a derived VIEW of the
corpus, and a view of a set placed inside that set makes the scan read its own
output: section 3 quotes four marker-shaped lines verbatim, so the count went
4 -> 8 -> 12 on successive regenerations and no fixpoint exists. See
`tracked_documents`.

**IT MUST NOT SPEAK TO THE CORRECTION GUARD.** That guard raises a candidate
pair whenever its correction vocabulary sits within two lines of a backticked
`*.md` that resolves, and this file is nothing but document names beside the
words CORRECTED and corrects. Written the obvious way, with backticked link
text, it produced 490 resolvable citations and **153 candidate pairs** -- each
demanding a declaration or a hand-written triage entry in a guard three other
waves edited the same day, to excuse pairs raised by a file that makes no
claims at all. See `_link` and `defuse`. The remedy was entirely local and no
test file was edited by this wave.

## NOT DERIVED, and left out rather than guessed

  A GIT-DERIVED DATE for the documents whose filename carries none (the
  counts table derives how many). `git log --diff-filter=A` would supply one,
  and it is rejected on a receipt: this repository lost 14
  days to red CI caused by `actions/checkout` `fetch-depth: 1`. `git ls-files`
  works in a shallow clone; history does not. An index that cannot be
  regenerated on CI is an index whose guard gets disabled.

  A LAST-TOUCHED DATE, for the same reason plus a worse one: it would make the
  committed index a function of history, so every commit touching any audit
  document turns the guard red until somebody regenerates. A guard that is red
  for reasons nobody can act on is the one people learn to bypass.

  WHETHER A DOCUMENT IS STILL TRUE. Only a marker somebody wrote can say that,
  and inferring it from prose was MEASURED not to work: the lexical scan in the
  correction guard produced 24 candidate pairs over an earlier corpus and
  exactly 1 was a genuine correction. No threshold separates them. The index
  reports declarations and says nothing about the rest.

  A SUMMARY OF ANY DOCUMENT'S CONTENT. The title and the correction reasons are
  quoted verbatim from tracked, swept lines. Nothing else is excerpted, because
  an excerpt chosen by a script is a place an identifier could reach a file that
  did not have one before.

## The blind spot this inherits, stated rather than discovered later

`MARKER` matches a line-opening declaration wherever it sits, INCLUDING inside
a fenced code block -- so a document that shows an EXAMPLE marker in a fence
would be read as declaring one. The corpus carries zero such lines today, and
`test_no_marker_hides_inside_a_fenced_code_block` asserts that precondition, so
the day one appears somebody has to look rather than silently gaining an edge.
Prose about a mechanism is indistinguishable from the mechanism to a matcher
that only reads shape, and it always fails quiet.

    python scripts/build_audit_index.py --write
    python scripts/build_audit_index.py --check
    python scripts/build_audit_index.py            # counts, to stdout
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT = ROOT / "_audit"
INDEX = AUDIT / "INDEX.md"

sys.path.insert(0, str(ROOT / "tests"))

#: The correction guard, imported for its PARSE and nothing else. A rename
#: there breaks this import loudly, which is the intended failure: a generator
#: that silently fell back to its own pattern would be the defect this whole
#: file is written against.
import test_a_correction_is_findable_from_the_claim as guard  # noqa: E402

CITATION = guard.CITATION
MARKER = guard.MARKER

#: `2026-09-20-the-audit-index.md` -> `2026-09-20`. Anchored at the start of the
#: BASENAME, so a date appearing anywhere else in the name cannot be mistaken
#: for the document's date.
DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})-")

#: A marker sitting BEHIND A BLOCKQUOTE, which the shipped anchor cannot see:
#: its `^\s*` never consumes `> `. Verified directly rather than reasoned
#: about -- `> **CORRECTED BY:** x` does not match the shipped pattern,
#: `**CORRECTED BY:** x` and `   CORRECTS: y` both do -- so the two patterns
#: are DISJOINT by construction and a line cannot be counted twice.
#:
#: **THE FOUR IN THIS CORPUS ARE NOT MERELY INVISIBLE MARKERS, THEY ARE A KIND
#: THE GUARD HAS NO MODEL FOR.** Every one names "this section" or "this
#: document" -- a LATER SECTION correcting an EARLIER ONE IN THE SAME FILE.
#: They name no other document, so widening the shipped anchor would not gain
#: a single cross-document edge; it would turn four well-intentioned
#: annotations into four malformed reds, because that guard requires a marker
#: to name exactly one RESOLVING document and "this section" resolves to none.
#:
#: So the guard is left alone and this index records them as WHAT THEY ARE: a
#: different relation, kept separate rather than flattened into the
#: cross-document graph. `test_no_blockquoted_marker_names_another_document`
#: holds the precondition that makes leaving the guard alone safe.
QUOTED_MARKER = re.compile(r"^\s*>[\s>]*(?:\*\*)?(CORRECTS|CORRECTED BY):")

#: How much of a blockquoted marker line to strip before quoting it. Only the
#: blockquote furniture -- the rest is printed VERBATIM, because these lines
#: carry no citation for `reason_on` to measure from and inventing a boundary
#: in prose is how a reason becomes a fragment.
QUOTE_PREFIX = re.compile(r"^\s*>[\s>]*")

#: A markdown fence, which opens or closes on three or more backticks or
#: tildes at the start of a stripped line.
FENCE = re.compile(r"^(?:`{3,}|~{3,})")

#: A level-1 ATX heading with at least one non-space character after it.
#: `#Foo` is not a heading in CommonMark and is not treated as one here.
H1 = re.compile(r"^#[ \t]+(\S.*)$")

UNDATED = "(undated)"
NO_TITLE = "(no level-1 heading)"


# --------------------------------------------------------------------------
# The corpus
# --------------------------------------------------------------------------

def tracked_documents(root: pathlib.Path) -> list[pathlib.Path]:
    """Every `.md` document under `_audit` THAT GIT TRACKS, sorted.

    Deliberately the same domain as the correction guard's `_documents`, and
    for the same reason: `_audit/_scratch/` is gitignored, holds working notes
    no clone has, and a check whose verdict depends on which tree it runs in is
    not checking the repository.

    A non-zero git exit RAISES. It is not skipped and not defaulted to a disk
    walk. A generator that goes quiet when its instrument is missing would emit
    an index of nothing and the drift check would then demand that nothing be
    committed.

    `git ls-files` prints a conflicted path ONCE PER MERGE STAGE, so mid-merge
    this list can carry duplicates. They are collapsed rather than allowed to
    double a row: a spurious red during a merge is an artifact, and an artifact
    that looks like a real finding costs somebody an hour.

    **`_audit/INDEX.md` IS EXCLUDED FROM ITS OWN CORPUS, AND THAT IS NOT
    TIDINESS.** It is a derived VIEW of the corpus, and a view of a set placed
    inside that set makes the scan read its own output. Measured, on the run
    that found it: with the index tracked and included, section 3 quotes four
    intra-document marker lines VERBATIM, those four quoted lines are
    themselves marker-shaped, and the count went 4 -> 8 -> 12 on successive
    regenerations. There is no fixpoint, so `--check` could never pass after
    `--write`. The red proof caught this before the first commit; nothing about
    reading the code suggested it.
    """
    proc = subprocess.run(
        ["git", "ls-files", "--", "_audit"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError("git ls-files failed: %s" % proc.stderr.strip())
    generated = (root / "_audit" / "INDEX.md").resolve()
    seen = {
        root / line.strip()
        for line in proc.stdout.splitlines()
        if line.strip().endswith(".md")
    }
    return sorted(doc for doc in seen if doc.resolve() != generated)


def resolver(documents, root: pathlib.Path) -> dict:
    """The three spellings the corpus uses for one target, mapped to files.

    Mirrors the correction guard's `_resolver` over an EXPLICIT document list
    so a synthetic corpus can be scanned. Basenames are unique across `_audit`
    (asserted by the guard and again here), so the bare-name form is
    unambiguous. Anything not in this map resolves to nothing and is ignored.
    """
    audit = root / "_audit"
    index: dict = {}
    for doc in documents:
        index[doc.relative_to(root).as_posix()] = doc
        index[doc.relative_to(audit).as_posix()] = doc
        index[doc.name] = doc
    return index


# --------------------------------------------------------------------------
# Per-document facts
# --------------------------------------------------------------------------

def date_of(doc: pathlib.Path) -> str:
    """The `YYYY-MM-DD` the BASENAME opens with, or `(undated)`."""
    found = DATE_PREFIX.match(doc.name)
    return found.group(1) if found else UNDATED


def title_of(lines) -> str:
    """The first level-1 ATX heading, or `(no level-1 heading)`.

    A heading inside a fenced code block is NOT a title. That is not a
    hypothetical nicety: this corpus quotes markdown at itself constantly, and
    a `# ` line inside a fence is an example of a heading rather than one.
    """
    for line in _unfenced(lines):
        found = H1.match(line.strip())
        if found:
            return found.group(1).strip()
    return NO_TITLE


def _unfenced(lines):
    """Yield only the lines that sit outside a fenced code block."""
    inside = False
    for line in lines:
        if FENCE.match(line.strip()):
            inside = not inside
            continue
        if not inside:
            yield line


def reason_on(line: str) -> str:
    """Whatever a marker line says after the document it names.

    **THAT SENTENCE IS THE SHIPPED `_reason_on`'s OWN DOCSTRING, AND THE
    SHIPPED IMPLEMENTATION IS NOT IT.** It takes everything after the LAST
    backtick on the line, which equals "after the document it names" only when
    no backtick follows the cited path. Marker reasons in this corpus quote
    SHAs, symbols and branch names constantly, so the two part company often:

        65 of 136 marker lines disagree, measured 2026-09-20
        every one of the 65 is a strict SUFFIX -- text is lost, never invented
        13 are cut below 60 characters
        the worst loses 738 characters of a 767-character reason

    One reads, in full, `. The dated note sits at that block.` Its real reason
    is a four-clause re-measurement against a freshly fetched remote. **The
    guard is still GREEN on it**, because its only check is that the fragment
    is 20 characters long, and a fragment can be.

    So this takes the text from the END OF THE CITATION MATCH, which is the
    stated intent implemented. THE SHIPPED FUNCTION IS STILL WHAT ADMITS A
    MARKER -- see `read_markers` -- so the edge set here is provably the edge
    set the guard enforces, and the only thing that changes is how much of the
    reason a reader gets to see. Nothing in `tests/` is edited by this wave.
    """
    found = CITATION.search(line)
    if found is None:
        return ""
    return line[found.end():].strip().lstrip("-*: ").strip()


def truncated_by_the_shipped_extractor(line: str) -> bool:
    """True when `guard._reason_on` drops text that `reason_on` keeps."""
    mine = reason_on(line)
    theirs = guard._reason_on(line)
    return bool(mine) and mine != theirs and mine.endswith(theirs)


def fenced_marker_lines(doc: pathlib.Path, lines) -> list:
    """Marker-shaped lines that sit INSIDE a fence -- examples, not declarations.

    The precondition of this whole file: today there are none, so importing the
    correction guard's fence-blind `MARKER` costs nothing. `--check` and the
    guard both assert that, so the day an example marker is written into a
    fence, somebody adjudicates it instead of the index silently gaining an
    edge that nobody declared.
    """
    out = []
    inside = False
    for number, line in enumerate(lines, 1):
        if FENCE.match(line.strip()):
            inside = not inside
            continue
        if inside and MARKER.search(line):
            out.append((doc.name, number, line.strip()))
    return out


# --------------------------------------------------------------------------
# The correction graph
# --------------------------------------------------------------------------

class Edge:
    """One declared correction, as the corpus spells it in BOTH directions.

    Each direction holds a LIST of `(line_no, reason)` rather than one, because
    a document may declare a correction of the same target more than once, for
    two different claims. See `read_markers`.
    """

    __slots__ = ("corrector", "target", "corrects", "corrected_by")

    def __init__(self, corrector, target):
        self.corrector = corrector
        self.target = target
        self.corrects: list = []
        self.corrected_by: list = []


def read_markers(documents, root: pathlib.Path):
    """Every well-formed marker in `documents`, plus everything rejected.

    Returns `(corrects, corrected_by, malformed, truncated)`:

      corrects        `(corrector_name, target_name) -> [(line_no, reason)]`
      corrected_by    `(target_name, corrector_name) -> [(line_no, reason)]`
      malformed       marker lines naming other than exactly one resolving
                      document, or carrying under 20 characters of reason
      truncated       admitted lines whose reason the SHIPPED extractor cuts
                      short -- see `reason_on`

    THE REJECTION RULES ARE THE CORRECTION GUARD'S, TO THE CHARACTER, because
    the two must agree about what a marker is or the index would advertise
    edges the guard does not enforce. `_is_marker`, `_citations` and
    `_reason_on` are called directly rather than reimplemented.

    **THE VALUE IS A LIST FOR A MEASURED REASON.** The shipped guard stores
    `dict[(source, target)] = (line, reason)`, and this corpus contains 68
    `CORRECTS:` lines against 65 distinct pairs. THREE PAIRS ARE DECLARED
    TWICE, for two different claims each, and in a pair-keyed dict the second
    declaration OVERWRITES the first with no error -- so three correction
    reasons are invisible to anything reading that dict. The guard is not
    wrong to do it; it only ever asks whether the pair exists. An index that
    inherited the same shape would print one reason and silently drop the
    other, which is the precise failure this whole file was built against.
    """
    index = resolver(documents, root)
    corrects: dict = {}
    corrected_by: dict = {}
    malformed: list = []
    truncated: list = []

    for doc in documents:
        lines = doc.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, 1):
            kind = guard._is_marker(line)
            if kind is None:
                continue
            named = guard._citations(line, index)
            if len(named) != 1:
                malformed.append((doc.name, number, line.strip(),
                                  "names %d documents that resolve" % len(named)))
                continue
            # ADMISSION uses the shipped extractor, on purpose: the set of
            # edges this index advertises must be the set that guard enforces,
            # and it is the length of ITS output that guard tests. Only the
            # TEXT comes from `reason_on`.
            if len(guard._reason_on(line)) < 20:
                malformed.append((doc.name, number, line.strip(),
                                  "carries no reason after the citation"))
                continue
            if truncated_by_the_shipped_extractor(line):
                truncated.append((doc.name, number,
                                  len(reason_on(line)),
                                  len(guard._reason_on(line))))
            where = corrects if kind == "CORRECTS" else corrected_by
            where.setdefault((doc.name, named[0].name), []).append(
                (number, reason_on(line)))
    return corrects, corrected_by, malformed, sorted(truncated)


def read_quoted_markers(documents, root: pathlib.Path):
    """Markers behind a blockquote, split into the two things they can be.

    Returns `(intra_document, hidden)`:

      intra_document  `doc_name -> [(line_no, kind, verbatim_line)]` -- a
                      marker naming NO other document, i.e. a later section
                      correcting an earlier one in the same file
      hidden          `[(doc_name, line_no, target_name, verbatim_line)]` -- a
                      marker that DOES name another document, and is therefore
                      a real cross-document correction the shipped guard is
                      structurally unable to see

    **THE SPLIT IS THE WHOLE POINT.** `hidden` is a defect and `intra_document`
    is a legitimate annotation in a form nobody formalised, and a single count
    covering both would say nothing useful about either. This corpus holds 4
    of the second and 0 of the first, measured -- so the shipped guard is
    missing no edge today, which is exactly why leaving it alone is safe and
    not merely convenient.
    """
    index = resolver(documents, root)
    intra: dict = {}
    hidden: list = []

    for doc in documents:
        for number, line in enumerate(
                doc.read_text(encoding="utf-8").splitlines(), 1):
            if MARKER.search(line) or not QUOTED_MARKER.match(line):
                continue
            kind = QUOTED_MARKER.match(line).group(1)
            named = [p for p in guard._citations(line, index) if p != doc]
            verbatim = QUOTE_PREFIX.sub("", line).strip()
            if named:
                for target in named:
                    hidden.append((doc.name, number, target.name, verbatim))
            else:
                intra.setdefault(doc.name, []).append((number, kind, verbatim))
    return intra, sorted(hidden)


def edges(documents, root: pathlib.Path):
    """The declared correction graph, joined across both directions.

    A `CORRECTS:` in the corrector and the matching `CORRECTED BY:` in the
    target are ONE edge. The correction guard asserts both halves exist for
    every pair, so a half-joined edge here means that guard is red; this file
    does not re-assert it, it CARRIES it -- `half_joined` comes back so the
    index can print what it saw rather than quietly dropping it.

    `lopsided` is the asymmetry that guard cannot see: a pair declared TWICE in
    one direction and ONCE in the other. Its both-directions test works on
    distinct pairs, so two claims corrected under one back-pointer reads to it
    as a clean joined pair. It is a thing for a person to look at, not a thing
    for this script to rule on, so it is reported and nothing more.
    """
    corrects, corrected_by, malformed, truncated = read_markers(documents, root)

    joined: dict = {}
    for (corrector, target), rows in corrects.items():
        edge = joined.setdefault((corrector, target), Edge(corrector, target))
        edge.corrects = sorted(rows)
    for (target, corrector), rows in corrected_by.items():
        edge = joined.setdefault((corrector, target), Edge(corrector, target))
        edge.corrected_by = sorted(rows)

    half_joined = sorted(
        key for key, edge in joined.items()
        if not edge.corrects or not edge.corrected_by
    )
    lopsided = sorted(
        key for key, edge in joined.items()
        if edge.corrects and edge.corrected_by
        and len(edge.corrects) != len(edge.corrected_by)
    )
    return joined, malformed, half_joined, lopsided, truncated


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def _cell(text: str) -> str:
    """Make `text` safe inside one markdown table cell.

    A pipe in a title splits the row and shifts every later cell one column
    left -- silently, because markdown has no arity check. The corpus already
    burned a wave on exactly this class of thing in `count_census_states`,
    where the escape `\\|` is content and a naive split ate it.
    """
    return text.replace("\\", "\\\\").replace("|", "\\|").strip()


#: The only codepoints that are TRANSLITERATED rather than escaped, and the
#: reason each one is: this corpus's own house spelling for the character.
#: Five committed titles type an em dash where every other line in the
#: repository writes `--`. Rendering those five as `<U+2014>` would be correct
#: and unreadable, and an index nobody can read is the thing this wave exists
#: to fix. THE SUBSTITUTION IS NOT SILENT: every affected document is named in
#: the index's own section 5 with its codepoint, so a reader knows the title is
#: transliterated rather than quoted.
TRANSLITERATE = {
    chr(0x2014): "--",    # em dash
    chr(0x2013): "--",    # en dash
    chr(0x2018): "'",     # left single quote
    chr(0x2019): "'",     # right single quote
    chr(0x201c): '"',     # left double quote
    chr(0x201d): '"',     # right double quote
    chr(0x2026): "...",   # ellipsis
    chr(0x00a0): " ",     # non-breaking space
}


def _ascii(text: str) -> str:
    """ASCII, with any unmapped codepoint SPELLED OUT rather than dropped.

    This repository is strict-ASCII. Silently stripping a character would
    change a title into a subtly different title that still LOOKS fine, which
    is this corpus's signature failure. Naming the codepoint keeps the row
    honest and tells whoever reads it what to fix.
    """
    out = []
    for char in text:
        if ord(char) < 128:
            out.append(char)
        elif char in TRANSLITERATE:
            out.append(TRANSLITERATE[char])
        else:
            out.append("<U+%04X>" % ord(char))
    return "".join(out)


def defuse(text: str, documents, root: pathlib.Path):
    """Strip the backticks from any `*.md` spelling the guard would RESOLVE.

    Returns `(defused_text, spellings)`.

    THE MINIMUM CHANGE THAT KEEPS THIS INDEX FROM SPEAKING. `_link` explains
    the mechanism; this is the same problem arriving through the one channel
    this wave does not control -- the titles and reasons it quotes verbatim.
    One title in this corpus reads *"the price of giving `jobs.md` the R/W
    column it does not have"*, and that backticked spelling resolves, so the
    generated index would raise one candidate pair against `_census/jobs.md`
    and turn `test_every_candidate_pair_is_declared_or_triaged` red on a pair
    that means nothing.

    Only the BACKTICKS go. Not a character of the text changes, so the title
    still says what the document says; it simply stops being a citation. The
    alternative -- adding a triage entry to a guard three waves edited today,
    to excuse a pair generated by a file that makes no claims -- would put a
    permanent apology in that guard for a defect in this one.

    Every defusal is reported in the index's own section 6. A silent rewrite of
    quoted text is exactly the thing this corpus cannot afford.
    """
    index = resolver(documents, root)
    spellings = []

    def swap(hit):
        if index.get(hit.group(1)) is None:
            return hit.group(0)
        spellings.append(hit.group(1))
        return hit.group(0).strip("`")

    return CITATION.sub(swap, text), spellings


def resolvable_citations(text: str, documents, root: pathlib.Path) -> list:
    """Backticked `*.md` spellings in `text` that the correction guard resolves.

    THE ONE PROPERTY THAT KEEPS THIS INDEX INERT TO THAT GUARD. `_link`
    explains why it matters and what it cost when it was false. This is the
    measurement, run over whatever is passed in -- the generated index itself,
    or the individual titles and reasons that feed it, which are the only
    strings here nobody in this wave wrote.
    """
    index = resolver(documents, root)
    return sorted(
        {hit.group(1) for hit in CITATION.finditer(text)
         if index.get(hit.group(1)) is not None}
    )


def _plural(count: int, noun: str) -> str:
    """`1 correction` / `2 corrections`. A generated sentence that reads as
    broken English is a generated sentence readers stop reading."""
    return "%d %s%s" % (count, noun, "" if count == 1 else "s")


def _link(doc: pathlib.Path, root: pathlib.Path) -> str:
    """A relative link from `_audit/INDEX.md` to `doc`, as markdown.

    **THE LINK TEXT IS NOT BACKTICKED, AND THAT IS LOAD-BEARING RATHER THAN A
    STYLE CHOICE.** The shipped correction guard's `CITATION` pattern is a
    BACKTICKED path ending in `.md`, and its lexical scan raises a candidate
    pair whenever correction vocabulary sits within two lines of one. This file
    is nothing but document names next to the words CORRECTED and corrects.

    Measured before this was changed: backticking the link text gave 490
    resolvable citations in the generated index and **153 candidate pairs**,
    every one of which `test_every_candidate_pair_is_declared_or_triaged`
    would demand a declaration or a written triage entry for. The correction
    guard would have gone red the moment this index was committed, on 153
    pairs that mean nothing -- an index of a corpus is not a claim about it.

    Dropping the backticks takes that to zero, and it is the whole remedy: all
    490 came from link text, and ZERO came from the reasons quoted verbatim in
    sections 2, 3 and 4. So no guard was edited, no triage list was written,
    and `test_the_index_raises_no_candidate_pair_in_the_correction_guard`
    holds the property that made that possible.
    """
    inside = doc.relative_to(root / "_audit").as_posix()
    return "[%s](%s)" % (inside, inside)


def _name_link(name: str, by_name: dict, root: pathlib.Path) -> str:
    doc = by_name.get(name)
    return _link(doc, root) if doc is not None else name


def render(documents, root: pathlib.Path) -> str:
    """The whole of `_audit/INDEX.md`, as one string with LF line endings.

    Pure over `documents`, which is what makes the red proof possible without
    touching a corpus that four other waves are writing into.
    """
    documents = sorted(documents)
    by_name = {doc.name: doc for doc in documents}

    facts = {}
    fenced = []
    non_ascii = []
    for doc in documents:
        lines = doc.read_text(encoding="utf-8").splitlines()
        title = title_of(lines)
        facts[doc.name] = (date_of(doc), title)
        fenced.extend(fenced_marker_lines(doc, lines))
        if _ascii(title) != title:
            non_ascii.append((doc.name, sorted(
                {"U+%04X" % ord(c) for c in title if ord(c) > 127})))

    joined, malformed, half_joined, lopsided, truncated = edges(documents, root)
    intra, hidden = read_quoted_markers(documents, root)

    #: Titles and quoted reasons are the only strings in this file that this
    #: wave did not write. If one of them carries a backticked `*.md` that
    #: resolves, the correction guard gains a candidate pair FROM THE INDEX and
    #: goes red for a reason nobody will connect to this file. Zero today;
    #: named here so the red arrives with its own explanation attached.
    quoting: list = []

    def quote(text: str, owner: str, where: str) -> str:
        clean, spellings = defuse(text, documents, root)
        for spelling in spellings:
            quoting.append((owner, where, spelling))
        return _ascii(clean)

    for name in list(facts):
        date, title = facts[name]
        facts[name] = (date, quote(title, name, "title"))
    for edge in joined.values():
        edge.corrects = [(number, quote(reason, edge.corrector, "CORRECTS: reason"))
                         for number, reason in edge.corrects]
        edge.corrected_by = [
            (number, quote(reason, edge.target, "CORRECTED BY: reason"))
            for number, reason in edge.corrected_by]
    for name, rows in intra.items():
        intra[name] = [
            (number, kind, quote(verbatim, name, "intra-document marker"))
            for number, kind, verbatim in rows]
    quoting = sorted(set(quoting))

    corrected = {}
    corrects_out = {}
    for (corrector, target), edge in joined.items():
        corrected.setdefault(target, []).append(edge)
        corrects_out.setdefault(corrector, []).append(edge)

    on_an_edge = set(corrected) | set(corrects_out)
    touched = on_an_edge | set(intra)
    dated = [name for name in by_name if facts[name][0] != UNDATED]
    corrects_lines = sum(len(edge.corrects) for edge in joined.values())
    back_lines = sum(len(edge.corrected_by) for edge in joined.values())

    out = []
    w = out.append

    w("# The audit index")
    w("")
    w("**GENERATED. Do not edit this file by hand.** Every row is derived from")
    w("the corpus by `scripts/build_audit_index.py`;")
    w("`tests/test_the_audit_index_is_derived.py` re-derives it and fails on any")
    w("drift, so an edit here is a change that will be reverted by the next")
    w("regeneration rather than a change to the record.")
    w("")
    w("    python scripts/build_audit_index.py --write")
    w("")
    w("**THE DOMAIN IS WHAT GIT TRACKS UNDER `_audit`**, not what is on disk.")
    w("`_audit/_scratch/` is gitignored, so a disk walk would index documents no")
    w("clone has -- the exact divergence that made the correction guard pass")
    w("locally and fail in a clone at the same SHA.")
    w("")
    w("**WHAT THIS FILE CANNOT TELL YOU.** Whether a document is still true. Only")
    w("a `CORRECTS:` / `CORRECTED BY:` marker somebody wrote can say that, and")
    w("section 2 below is exactly those markers and nothing inferred. A document")
    w("absent from section 2 is a document nobody has declared a correction of --")
    w("which is not the same as one nobody has overtaken.")
    w("")
    w("Dates come from the `YYYY-MM-DD-` filename prefix. Documents without one")
    w("are listed as `%s`; no date is taken from git history, because" % UNDATED)
    w("`git ls-files` works in a shallow clone and `git log` does not.")
    w("")

    w("## 1. The counts")
    w("")
    w("| what | count |")
    w("| --- | --- |")
    w("| audit documents git tracks under `_audit` | %d |" % len(documents))
    w("| of those, carrying a `YYYY-MM-DD-` date prefix | %d |" % len(dated))
    w("| distinct dates | %d |" % len({facts[n][0] for n in dated}))
    w("| documents with no level-1 heading | %d |"
      % sum(1 for name in by_name if facts[name][1] == NO_TITLE))
    w("| `CORRECTS:` marker lines | %d |" % corrects_lines)
    w("| `CORRECTED BY:` marker lines | %d |" % back_lines)
    w("| distinct declared correction edges | %d |" % len(joined))
    w("| documents something later corrects | %d |" % len(corrected))
    w("| documents that correct something | %d |" % len(corrects_out))
    w("| documents at either end of a cross-document edge | %d |"
      % len(on_an_edge))
    w("| intra-document correction markers | %d |"
      % sum(len(rows) for rows in intra.values()))
    w("| documents that correct themselves later on | %d |" % len(intra))
    w("| documents no correction marker touches at all | %d |"
      % (len(documents) - len(touched)))
    w("| blockquoted markers naming ANOTHER document | %d |" % len(hidden))
    w("| edges missing one of their two markers | %d |" % len(half_joined))
    w("| edges declared a different number of times in each direction | %d |"
      % len(lopsided))
    w("| marker lines rejected as malformed | %d |" % len(malformed))
    w("| marker-shaped lines inside a fenced code block | %d |" % len(fenced))
    w("| reasons the shipped `_reason_on` cuts short (printed in full below) | %d |"
      % len(truncated))
    w("| titles carrying a non-ASCII character | %d |" % len(non_ascii))
    w("| quoted strings whose backticked citation had to be defused | %d |"
      % len(quoting))
    w("")
    if corrects_lines != len(joined) or back_lines != len(joined):
        w("**THE MARKER LINES OUTNUMBER THE EDGES**, because some pairs are")
        w("declared more than once, for two different claims. Every reason is")
        w("printed below; a pair-keyed dictionary keeps only the last of each,")
        w("which is how those reasons went unread.")
        w("")

    w("## 2. What a later document corrected")
    w("")
    w("**A reader who arrives at a claim should be able to see here, without")
    w("grep, that something later overtook it.** Each entry is the corrected")
    w("document, then the correctors it names, then the reason THAT DOCUMENT")
    w("ITSELF gives -- quoted from its own `CORRECTED BY:` line, not summarised.")
    w("")
    w("A correction is of a CLAIM, never of a whole document. Nothing here says a")
    w("document is dead; it says one thing in it was overtaken and names what.")
    w("")
    if not corrected:
        w("_No document in this corpus carries a `CORRECTED BY:` marker._")
        w("")
    for target in sorted(corrected):
        w("### %s" % _name_link(target, by_name, root))
        w("")
        w("%s &middot; %s" % (facts[target][0], _ascii(facts[target][1])))
        w("")
        for edge in sorted(corrected[target], key=lambda e: e.corrector):
            w("- CORRECTED BY %s" % _name_link(edge.corrector, by_name, root))
            w("")
            for _, reason in (edge.corrected_by or edge.corrects):
                w("  > %s" % _ascii(reason))
                w("")

    w("## 3. What a document corrected in itself")
    w("")
    w("**A DIFFERENT RELATION, KEPT SEPARATE ON PURPOSE.** These markers sit")
    w("behind a blockquote, where the shipped correction guard's line-start")
    w("anchor cannot reach them, and every one names *this section* or *this")
    w("document* rather than another file -- a later section correcting an")
    w("earlier one in the same document.")
    w("")
    w("They are NOT edges in the graph above and are not counted as such.")
    w("Flattening the two would claim a cross-document correction that nobody")
    w("declared. The line is printed verbatim, blockquote furniture removed,")
    w("because it carries no citation to measure a reason from and inventing a")
    w("boundary in prose is how a reason becomes a fragment.")
    w("")
    if not intra:
        w("_No document in this corpus carries an intra-document correction"
          " marker._")
        w("")
    for name in sorted(intra):
        w("### %s" % _name_link(name, by_name, root))
        w("")
        w("%s &middot; %s" % (facts[name][0], _ascii(facts[name][1])))
        w("")
        for number, kind, verbatim in intra[name]:
            w("- line %d, `%s:`" % (number, kind))
            w("")
            w("  > %s" % _ascii(verbatim))
            w("")

    w("## 4. What each document corrects")
    w("")
    w("The same cross-document edges from the other end, so a corrector's")
    w("reach is visible. The quoted reason here is the CORRECTOR's own")
    w("`CORRECTS:` line.")
    w("")
    if not corrects_out:
        w("_No document in this corpus carries a `CORRECTS:` marker._")
        w("")
    for corrector in sorted(corrects_out):
        w("### %s" % _name_link(corrector, by_name, root))
        w("")
        w("%s &middot; %s" % (facts[corrector][0], _ascii(facts[corrector][1])))
        w("")
        for edge in sorted(corrects_out[corrector], key=lambda e: e.target):
            w("- CORRECTS %s" % _name_link(edge.target, by_name, root))
            w("")
            for _, reason in (edge.corrects or edge.corrected_by):
                w("  > %s" % _ascii(reason))
                w("")

    w("## 5. Every document, by date")
    w("")
    w("`CORRECTED` means at least one later document declares a correction of")
    w("something in this one -- go to section 2 for what. `corrects` means this")
    w("document declares a correction of another. `self-corrected` means a")
    w("later section of the document corrects an earlier one -- section 3. A")
    w("blank cell means no marker names this document in any of the three")
    w("ways, which is a fact about markers and not a verdict on the document.")
    w("")
    w("| date | document | title | markers |")
    w("| --- | --- | --- | --- |")
    for doc in sorted(documents, key=lambda d: (facts[d.name][0], d.name)):
        name = doc.name
        date, title = facts[name]
        flags = []
        if name in corrected:
            flags.append("**CORRECTED x%d**" % len(corrected[name]))
        if name in corrects_out:
            flags.append("corrects x%d" % len(corrects_out[name]))
        if name in intra:
            flags.append("self-corrected x%d" % len(intra[name]))
        w("| %s | %s | %s | %s |" % (
            date,
            _link(doc, root),
            _cell(_ascii(title)),
            " ".join(flags),
        ))
    w("")

    if (malformed or half_joined or lopsided or fenced or truncated
            or non_ascii or hidden or quoting):
        w("## 6. What the scan rejected, could not join, or had to repair")
        w("")
        w("**An empty section here would be a claim, so it is printed only when")
        w("there is something in it.** Everything below is a thing somebody")
        w("should look at; none of it is absorbed silently.")
        w("")
        if truncated:
            w("`tests/test_a_correction_is_findable_from_the_claim.py::_reason_on`")
            w("returns everything after the LAST backtick on a marker line. Its")
            w("docstring says *whatever a marker line says after the document it")
            w("names*, which is the same thing only when no backtick follows the")
            w("cited path. The lines below are the ones where it is not. Every")
            w("case is a strict SUFFIX -- text is lost, never invented -- and the")
            w("guard stays green on all of them, because it only asks whether the")
            w("fragment is 20 characters long. **Sections 2 and 3 above print the")
            w("full reason**, taken from the end of the citation match.")
            w("")
            for name, number, full, short in truncated:
                w("- TRUNCATED REASON %s line %d -- the shipped extractor returns"
                  " %d of %d characters."
                  % (_name_link(name, by_name, root), number, short, full))
            w("")
        for name, number, line, why in sorted(malformed):
            w("- MALFORMED MARKER %s line %d -- %s"
              % (_name_link(name, by_name, root), number, why))
        for corrector, target in half_joined:
            w("- HALF-JOINED EDGE %s -> %s -- one of the two markers is missing;"
              " the correction guard fails on this."
              % (_name_link(corrector, by_name, root),
                 _name_link(target, by_name, root)))
        for corrector, target in lopsided:
            edge = joined[(corrector, target)]
            w("- LOPSIDED EDGE %s declares %s of %s, which carries %s to it."
              " Two claims under one back-pointer read to the correction guard"
              " as one clean pair, because its test is over distinct pairs."
              % (_name_link(corrector, by_name, root),
                 _plural(len(edge.corrects), "correction"),
                 _name_link(target, by_name, root),
                 _plural(len(edge.corrected_by), "back-pointer")))
        for name, number, target, verbatim in hidden:
            w("- HIDDEN CROSS-DOCUMENT CORRECTION %s line %d names %s from"
              " behind a blockquote. The shipped anchor's `^\\s*` does not"
              " consume `> `, so the correction guard cannot see this line and"
              " will not demand the matching back-pointer. **This is a real"
              " edge missing from section 2** -- unlike the intra-document"
              " markers in section 3, which name no other document."
              % (_name_link(name, by_name, root), number,
                 _name_link(target, by_name, root)))
        for name, number, line in sorted(fenced):
            w("- MARKER INSIDE A FENCE %s line %d -- read as a declaration by"
              " the shipped pattern, which is fence-blind."
              % (_name_link(name, by_name, root), number))
        for name, where, spelling in quoting:
            w("- DEFUSED CITATION %s -- its %s quotes the spelling %s in"
              " backticks, which the correction guard's `CITATION` pattern"
              " RESOLVES. That guard raises a candidate pair whenever"
              " correction vocabulary sits within two lines of a resolving"
              " citation, and this file is nothing but document names beside"
              " the words CORRECTED and corrects, so the quoted string would"
              " make this index raise a pair it means nothing by. **The"
              " backticks are removed here and not one character of the text"
              " is**; the quoted string still says exactly what the document"
              " says, it simply stops being a citation."
              % (_name_link(name, by_name, root), where, spelling))
        for name, points in sorted(non_ascii):
            w("- NON-ASCII TITLE %s carries %s, so its title above is"
              " transliterated rather than quoted. This repository is"
              " strict-ASCII and writes an em dash as `--` everywhere else;"
              " a codepoint with no house spelling is printed as `<U+XXXX>`"
              " rather than dropped, because silently stripping it would leave"
              " a title that still looks fine and is not the one in the"
              " document."
              % (_name_link(name, by_name, root), ", ".join(points)))
        w("")

    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------

def build(root: pathlib.Path = ROOT) -> str:
    return render(tracked_documents(root), root)


def committed(root: pathlib.Path = ROOT) -> str:
    """The index as checked out, with line endings normalised.

    `core.autocrlf` is true on the machine this corpus is written on and false
    on CI, so the SAME committed bytes arrive as CRLF here and LF there. A
    byte comparison would therefore pass on one and fail on the other -- which
    is precisely the local-passes/clone-fails shape this repository has already
    paid for once.
    """
    path = root / "_audit" / "INDEX.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true",
                        help="regenerate _audit/INDEX.md")
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed index is not what this "
                             "generator produces from the current corpus")
    args = parser.parse_args(argv)

    documents = tracked_documents(ROOT)
    text = render(documents, ROOT)

    if args.write:
        INDEX.write_text(text, encoding="utf-8", newline="\n")
        print("wrote %s over %d tracked documents"
              % (INDEX.relative_to(ROOT).as_posix(), len(documents)))
        return 0

    if args.check:
        have = committed(ROOT)
        if not have:
            print("FAIL _audit/INDEX.md does not exist; run --write")
            return 1
        if have != text:
            mine = text.splitlines()
            theirs = have.splitlines()
            for number, (one, two) in enumerate(zip(theirs, mine), 1):
                if one != two:
                    print("FAIL _audit/INDEX.md drifted at line %d" % number)
                    print("  committed: %s" % one[:160])
                    print("  derived  : %s" % two[:160])
                    break
            else:
                print("FAIL _audit/INDEX.md has %d lines, the corpus derives %d"
                      % (len(theirs), len(mine)))
            return 1
        print("ok _audit/INDEX.md matches the corpus (%d documents)"
              % len(documents))
        return 0

    joined, malformed, half_joined, lopsided, truncated = edges(documents, ROOT)
    corrected = {target for _, target in joined}
    print("documents             %d" % len(documents))
    print("CORRECTS lines        %d"
          % sum(len(edge.corrects) for edge in joined.values()))
    print("CORRECTED BY lines    %d"
          % sum(len(edge.corrected_by) for edge in joined.values()))
    print("distinct edges        %d" % len(joined))
    print("corrected documents   %d" % len(corrected))
    print("malformed markers     %d" % len(malformed))
    print("half-joined edges     %d" % len(half_joined))
    print("lopsided edges        %d" % len(lopsided))
    print("truncated reasons     %d" % len(truncated))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
