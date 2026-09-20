"""Every name a tracked `_audit/` document ASSERTS must resolve in the tree.

THE DEFECT CLASS. Four separate waves on 2026-09-20 tripped over the same thing
and none of them was looking for it: a document names a tool, a blocker, a file
or a census row that exists NOWHERE in this repository. `linkedin_applied_jobs`
is a tool name that appears only inside the document naming it.
`PROXIMITY-NOT-PARSED` is a blocker name that measures zero in the ledger, zero
in `blocker-map.tsv`, zero in `blocker-assignments.tsv`, and zero repo-wide
outside one document -- and it is why a committed test asserting `unknown == []`
fails.

WHY THIS NEEDS A GUARD RATHER THAN MORE CARE. A citation to something that does
not exist does not rot into an obviously dangling reference. **It rots into a
PLAUSIBLE WRONG ANSWER**, which stops the reader instead of sending them
looking. A tool name that reads like the other forty-five is believed. A blocker
name in the right shape is believed. Nothing in the text says "look elsewhere",
so the reader stops, and the next wave rediscovers it by stumbling.

============================================================================
THE HARD PART: A DOCUMENT MAY LEGITIMATELY NAME SOMETHING THAT DOES NOT EXIST
============================================================================

It may propose a tool, quote a rejected candidate, record a name it decided
against, argue that a blocker should be created, or narrate a defect in which
the name was wrong. A guard that cannot tell an ASSERTION from a PROPOSAL fires
constantly, gets suppressed, and certifies nothing -- which is this repository's
most expensive recurring failure.

**THE RULE, and it was read off the corpus rather than invented: THIS CORPUS
ALREADY MARKS ITS PROPOSALS.** Every document that mints a name says so, in the
author's own words, in one of a small number of ways:

    "**New blocker: `LINK-FOR-OFF-PLATFORM-USE` -- 2 rows, 2R, queue BUILD**"
        _audit/2026-09-05-decide-retire-rulings.md:478

    "| rows | n | successor blocker (proposed) | what it is blocked on |"
        _audit/2026-09-20-the-decides.md:187 -- and the same table writes
        "`PICKER-SURFACES` (exists)" for the two that DO exist

    "**Re-file as `COLLABORATIVE-POST` (3W, no boundary) and ...**"
        _audit/2026-09-05-article-publish.md:176

    "Proposed rename: `AI-ASSISTANT-OVERLAY` -- A PROPOSAL, NOT A RULING."
        _audit/2026-09-19-blocker-conflicts.md:70

    "**This is a SPECIFICATION, not a build.**"
        _audit/2026-09-05-leave-group-writespec.md:7 -- the document whose
        field table reads "| `tool_name` | `linkedin_leave_group` |"

    "So a tool named `linkedin_read_inbox` WOULD not return an inbox"
        _audit/2026-08-25-cannot-vs-will-not.md:234 -- a modal

    "`AI-INTERVIEW-RESULTS-NO-ADDRESS` exists only in
     `_audit/2026-09-05-decide-retire-rulings.md` lines 300-303"
        _audit/2026-09-20-the-decides.md:95 -- the document disclosing the
        absence itself, which is the document being RIGHT

So the guard does not try to infer intent. **It asks whether the author
discharged the burden of marking**, and the burden is the author's because they
are the only party who knows. A name written in a referential position with no
mark is an assertion, because a reader has nothing else to go on. That is not a
heuristic about English; it is a property of how this corpus is written, and
section "MEASURED" below gives the counts.

THE SECOND HALF, AND IT DOES MORE WORK THAN THE FIRST. For the blocker kind the
dominant error is not proposal-versus-assertion at all -- it is KIND. The
UPPER-KEBAB shape in this corpus is shared by at least seven closed
vocabularies: blocker names, census state cells (`EXCLUDED-RULED`,
`COVERED-CANNOT-DELIVER`), evidence classes (`LEDGER-EXPLICIT`, `RECON-DOC`),
refusal returns (`REFUSED-BY-SUBSTRING`, `ALLOWLIST-SILENCE`), map-close classes
(`EMPTY-CERTAIN`), build states (`PROVEN-LIVE`, `TESTED-ONLY`), and the
INSTRUMENTS register's own entry names (`A-SKIP-IS-NOT-A-RED`). Measured over
the corpus: **235 occurrences of a backticked UPPER-KEBAB token that is not one
of the ledger's 97.** Firing on all of them would be a guard with roughly 4%
precision, which is a guard nobody reads.

So a blocker candidate must sit in a SLOT -- a position this corpus's own
grammar reserves for a blocker reference. The slot phrases below were not
guessed; each was measured for how many ledger blockers versus other-vocabulary
tokens it selects (see MEASURED), and four candidate phrases that selected only
other vocabularies (`stays`, `is now`, `filed as`, `files this blocker as`) were
dropped on that evidence.

============================================================================
MEASURED, at 8b58dcb, over 166 tracked `_audit/` files / 78,656 lines
============================================================================

SLOT PHRASES -- selections, and how many named a real ledger blocker:

    phrase            selected   real   other-vocabulary
    `blocker`                9      4      5  (all 5 are findings, not noise)
    `under`                 23     21      2  (both are findings)
    `filed under`            4      4      0
    `belongs to`             3      3      0
    `behind`                 1      1      0
    `the blocker`            1      1      0
    ---------------- DROPPED on this evidence ----------------
    `stays`                  1      0      1  -> RULING-FORK, a queue verdict
    `is now`                 1      0      1  -> EMPTY-CERTAIN, a close class
    `filed as`               2      0      2  -> an INSTRUMENTS entry name
    `files this blocker as`  1      0      1  -> DECIDE-RETIRE, a queue verdict

TOOL NAMES -- the population is complete, not sampled. 72 distinct `linkedin_*`
tokens appear in the corpus; 68 resolve; the 4 that do not are the entire
decision space, at 5 occurrence sites, and every one is labelled below.

WHAT THIS GUARD DOES NOT DO. It does not reach names carried in prose with no
slot and no backticks -- `find_asserted_names` would have to guess which
vocabulary such a token is drawn from, and guessing is how the 4%-precision
version of this check gets built. It does not judge whether a RESOLVING citation
points at the right thing. It does not follow `path:line` locators into their
targets (a line number is not an anchor in a live tree; see INSTRUMENTS 3.5).

    ./venv/Scripts/python.exe scripts/check_asserted_names_resolve.py
    ./venv/Scripts/python.exe scripts/check_asserted_names_resolve.py --all
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import subprocess
import sys
from typing import Iterable, NamedTuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CORPUS_DIR = "_audit"
CODE_DIRS = ("linkedin_server", "scripts", "tests")


class Site(NamedTuple):
    """One occurrence of one candidate name, with the verdict it earned."""

    kind: str           # TOOL | BLOCKER
    name: str
    doc: str
    line: int
    verdict: str        # ASSERTED-ABSENT, or the marker that cleared it
    text: str

    def __str__(self) -> str:
        return f"{self.doc}:{self.line}  {self.kind} {self.name}  [{self.verdict}]"


# --------------------------------------------------------------------------
# The corpus, read ONCE.
#
# THE REASON THIS IS STATED RATHER THAN ASSUMED: two scripts in this repository
# re-scan the whole corpus once per item. `find_blocker_reason.py` takes over
# 120 seconds across 97 blockers, and two test modules do the same inside the
# suite. A guard that is slow gets excluded from the gate and then protects
# nothing, so the corpus is loaded once into memory and every later question is
# answered from the index.
# --------------------------------------------------------------------------
def tracked(repo: pathlib.Path, *paths: str) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=str(repo), capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {proc.stderr.strip()}")
    return [p for p in proc.stdout.splitlines() if p.strip()]


def load_corpus(repo: pathlib.Path) -> dict[str, list[str]]:
    """Every tracked `_audit/` file, as lines. One read each, no re-reads."""
    out: dict[str, list[str]] = {}
    for rel in tracked(repo, CORPUS_DIR):
        path = repo / rel
        if not path.is_file():
            continue
        out[rel] = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return out


def fenced(lines: Iterable[str]) -> set[int]:
    """1-based line numbers sitting inside a ``` fence.

    Quoted tool output is not a claim. `_audit/_slice-activity-items.md:537`
    holds a pytest assertion diff -- `{'linkedin_my...n_saved_jobs'}` -- whose
    ELIDED middle tokenises as a tool named `linkedin_my`. Nothing in that line
    is the document speaking.
    """
    inside: set[int] = set()
    open_fence = False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            open_fence = not open_fence
            inside.add(i)
            continue
        if open_fence:
            inside.add(i)
    return inside


# --------------------------------------------------------------------------
# The registries a name is resolved against.
# --------------------------------------------------------------------------
def tool_registry(repo: pathlib.Path) -> set[str]:
    """Every ``linkedin_*`` identifier that appears ANYWHERE in tracked code.

    DELIBERATELY WIDER THAN THE 45 REGISTERED TOOLS. The question this guard
    asks is "does this name exist in the tree at all", which is the defect
    class; a helper, a constant or a name mentioned only in a docstring all
    answer it. Resolving against the registered 45 instead would convict every
    document that discusses an internal function, which is a different and much
    noisier claim.
    """
    found: set[str] = set()
    pattern = re.compile(r"\blinkedin_[a-z0-9_]+")
    for rel in tracked(repo, *CODE_DIRS):
        if not rel.endswith(".py"):
            continue
        path = repo / rel
        if not path.is_file():
            continue
        found.update(pattern.findall(path.read_text(encoding="utf-8", errors="replace")))
    return found


def registered_tools(repo: pathlib.Path) -> set[str]:
    """The ``@mcp.tool()``-decorated names, by AST. Used as a CONTROL only."""
    tree = ast.parse((repo / "linkedin_server" / "server.py").read_text(
        encoding="utf-8", errors="replace"))
    out: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if (getattr(target, "attr", None) or getattr(target, "id", None)) == "tool":
                out.add(node.name)
    return out


def blocker_registry(repo: pathlib.Path) -> dict[str, int]:
    """The ledger's 97 blockers, via the SHIPPED parser.

    NOT REIMPLEMENTED. `build_blocker_map.ledger_counts()` locates the ledger's
    two tables by header row and is the same parse every other check in this
    repository resolves a blocker against. A second parse here could disagree
    with it, and then a name would be "absent" according to one instrument and
    present according to another -- which is the failure this guard exists to
    catch, reproduced inside the guard.
    """
    import build_blocker_map as bbm  # noqa: PLC0415  (import cost is the point)

    counts = bbm.ledger_counts()
    if len(counts) < 90:
        raise RuntimeError(
            f"the ledger parse returned {len(counts)} blockers, not ~97. A "
            "partial parse would make real blockers look absent and this guard "
            "would convict the corpus for the parser's failure. Refusing to run."
        )
    return counts


# --------------------------------------------------------------------------
# The marks. A candidate is ASSERTED unless the author marked it.
# --------------------------------------------------------------------------

#: SLOT FORM 1 -- a phrase immediately BEFORE the name. Measured per phrase;
#: the four that selected only other vocabularies were dropped.
_SLOT_BEFORE = re.compile(
    r"(?:^|[\s(*_>|,;:-])"
    r"(?:the\s+blocker|blocker|blocked\s+behind|behind|filed\s+under|under"
    r"|belongs\s+to)"
    r"\s*[:=]?\s*$",
    re.IGNORECASE,
)

#: SLOT FORM 2 -- the word AFTER the name: "a single `NO-ADDRESS` blocker".
#: Measured: 2 selections, 1 a ledger blocker, 1 cleared by its own modal.
#: Thin, and kept anyway: leaving it out would have hidden `NO-ADDRESS` behind
#: an ACCIDENT of the prefix rule rather than behind the marker that actually
#: excuses it, and a guard whose silences are accidents cannot be audited.
_SLOT_AFTER = re.compile(r"^\s*blockers?\b", re.IGNORECASE)

#: SLOT FORM 3 -- a markdown table cell under a column whose HEADER names
#: blockers, where the name IS the cell. This is where the corpus does most of
#: its blocker referencing and it is the strongest slot evidence there is:
#: measured over the corpus it selects 358 cells, 353 of which name a ledger
#: blocker, and the distinct names it selects are EXACTLY the ledger's 97 --
#: the slot reproduces the registry.
#:
#: "the name IS the cell" is load-bearing, not tidiness. `_census/profile.md`
#: heads its fifth column `evidence / blocker` and fills it with prose, so a
#: contains-test convicted a `STILL-UNKNOWN` sitting inside a reason sentence.
#: Requiring the whole cell drops that and keeps all 97.
_CELL_ASIDE = re.compile(r"\s*\([^)]*\)\s*$")   # "`PICKER-SURFACES` (exists)"

#: LINE-scoped: the author minting the name on the spot.
_MINTS = re.compile(
    r"new\s+blocker|proposed\s+rename|proposed\s+name|\bproposal\b|\bproposed\b"
    r"|re-?file\s+as|rename\s+to|should\s+be\s+(?:called|named)"
    r"|replaced\s+by|successor\b|becomes\s+a\b|call\s+it\b|name\s+it\b"
    r"|\bbuild\s+the\b|\bbuild\s+two\b",
    re.IGNORECASE,
)

#: LINE-scoped: the author speaking of something that is not the case.
_MODAL = re.compile(
    r"\bwould\b|\bcould\b|\bmight\b|\bwere\s+to\b|a\s+tool\s+named\b"
    r"|a\s+blocker\s+(?:named|called)\b|\bhypothetical\b|\bif\s+it\s+were\b",
    re.IGNORECASE,
)

#: DOCUMENT-scoped: the author disclosing the absence. One honest disclosure
#: anywhere in a document clears that document's citations of that name --
#: correctly, because a reader of the document can reach the disclosure. This is
#: the rule that keeps `_audit/2026-09-20-the-decides.md` innocent: it cites
#: `AI-INTERVIEW-RESULTS-NO-ADDRESS` six times AND states at line 95 that the
#: name "exists only in" one other document, which is the document being right.
_DISCLOSES = re.compile(
    r"exists?\s+only\s+in|do(?:es)?\s+not\s+exist|never\s+existed|no\s+such\b"
    r"|not\s+one\s+of\s+the\s+97|never\s+ruled|not\s+in\s+the\s+ledger"
    r"|is\s+not\s+a\s+blocker|appears?\s+nowhere|nowhere\s+in\s+the\s+repo",
    re.IGNORECASE,
)

#: DOCUMENT-scoped: the document declaring itself a spec for an unbuilt thing.
_SPEC_DOC = re.compile(
    r"this\s+is\s+a\s+specification,?\s+not\s+a\s+build"
    r"|a\s+SPECIFICATION,?\s+not\s+a\s+build",
    re.IGNORECASE,
)

#: TABLE-scoped: a markdown table whose header says its names are proposals.
#: `_audit/2026-09-20-the-decides.md:187` -- "successor blocker (proposed)".
_PROPOSAL_HEADER = re.compile(r"\|[^|]*\bproposed\b[^|]*\|", re.IGNORECASE)

_BACKTICK = re.compile(r"`([^`\n]+)`")
_TOOL_TOKEN = re.compile(r"\blinkedin_[a-z0-9_]+")
_KEBAB = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
#: The cheap prefilter: could this line hold an UPPER-KEBAB token at all?
_KEBAB_ANYWHERE = re.compile(r"[A-Z][A-Z0-9]*-[A-Z0-9]")
#: `I13-I16`, `L11-L27`, `J92-J98` are row/line RANGES wearing the same shape.
_RANGE = re.compile(r"^[A-Z]?[0-9]")


def _cells(line: str) -> list[str]:
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return raw.split("|")


def _bare_cell(cell: str) -> str:
    """A table cell stripped to the name it would carry, if it carries one."""
    text = _CELL_ASIDE.sub("", cell.strip())
    return text.strip().strip("*").strip("_").strip().strip("`").strip()


def table_headers(
    lines: list[str],
) -> tuple[list[str | None], list[list[int] | None]]:
    """Per 1-based line: its table's header row, and the blocker column indices.

    ONE FORWARD PASS, and the column indices are resolved ONCE PER TABLE rather
    than once per row. Walking upward per candidate, or re-splitting the header
    per row, would make this quadratic in table length -- the shape of the two
    120-second scripts this guard is written not to become.
    """
    heads: list[str | None] = [None] * (len(lines) + 1)
    cols: list[list[int] | None] = [None] * (len(lines) + 1)
    header: str | None = None
    header_cols: list[int] | None = None
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("|"):
            if header is None:
                header = line          # first row of a new table
                header_cols = [
                    j for j, c in enumerate(_cells(line)) if "blocker" in c.lower()
                ] or None
            else:
                heads[i] = header
                cols[i] = header_cols
        else:
            header = None
            header_cols = None
    return heads, cols


#: DOCUMENT-scoped and NAME-SPECIFIC: the document minting this exact name.
#: Name-specific rather than a blanket document flag, deliberately -- a document
#: that opens one blocker legitimately must not thereby be excused for citing a
#: DIFFERENT unregistered one. `_audit/2026-09-05-decide-retire-rulings.md`
#: opens two and cites both again in its own ruling table; a reader of that
#: document meets the mint, so those later cells are part of the same ruling.
_MINT_OF = (
    r"(?:new\s+blocker|proposed\s+rename|proposed\s+name|re-?file\s+as"
    r"|successor\s+blocker)\s*[:.]?\s*[`*\s]{{0,4}}{name}"
)
#: DOCUMENT-scoped and NAME-SPECIFIC: the document disclosing this name's
#: absence, which is the document being RIGHT.
_ABSENT_OF = (
    r"{name}`?[^\n]{{0,120}}?(?:exists?\s+only\s+in|does\s+not\s+exist"
    r"|not\s+one\s+of\s+the\s+97|never\s+ruled|appears?\s+nowhere)"
)


def _doc_marks(blob: str, name: str) -> str | None:
    """A document-scope verdict for `name`, or None."""
    esc = re.escape(name)
    if re.search(_MINT_OF.format(name=esc), blob, re.IGNORECASE):
        return "MARKED-PROPOSAL-DOC"
    if re.search(_ABSENT_OF.format(name=esc), blob, re.IGNORECASE):
        return "MARKED-ABSENT"
    return None


def _blocker_candidates(
    line: str, header_cols: list[int] | None
) -> list[tuple[str, str]]:
    """(name, slot-form) for every blocker-position name on this line.

    `header_cols` is the PRE-RESOLVED list of column indices whose header names
    blockers, computed once per table rather than per row -- re-splitting the
    header for all 78,656 corpus lines was measured at several seconds on its
    own, which is how a guard gets dropped from a gate.
    """
    out: list[tuple[str, str]] = []
    for m in _BACKTICK.finditer(line):
        name = m.group(1).strip()
        if not _KEBAB.match(name) or _RANGE.match(name):
            continue
        before = line[: m.start()].rstrip().rstrip("*_")
        if _SLOT_BEFORE.search(before):
            out.append((name, "phrase-before"))
        elif _SLOT_AFTER.match(line[m.end():]):
            out.append((name, "phrase-after"))

    if header_cols:
        cells = _cells(line)
        for i in header_cols:
            if i >= len(cells):
                continue
            name = _bare_cell(cells[i])
            if _KEBAB.match(name) and not _RANGE.match(name):
                out.append((name, "table-cell"))
    return out


def classify(
    corpus: dict[str, list[str]],
    tools: set[str],
    blockers: set[str],
) -> list[Site]:
    """Every candidate site in the corpus, with its verdict. ONE pass per file."""
    sites: list[Site] = []
    for doc, lines in corpus.items():
        inside_fence = fenced(lines)
        heads, cols = table_headers(lines)
        blob = "\n".join(lines)
        doc_is_spec = bool(_SPEC_DOC.search(blob))
        doc_cache: dict[str, str | None] = {}

        for n, line in enumerate(lines, 1):
            # THE PREFILTER, and it is the whole performance story. The marker
            # regexes and the table split are the expensive part, and 99.9% of
            # lines carry no candidate at all -- so nothing expensive runs
            # until a cheap substring test says a candidate is possible.
            may_tool = "linkedin_" in line
            may_blocker = _KEBAB_ANYWHERE.search(line) is not None
            if not (may_tool or may_blocker) or n in inside_fence:
                continue

            found: list[tuple[str, str]] = []
            if may_tool:
                found += [("TOOL", m.group(0)) for m in _TOOL_TOKEN.finditer(line)
                          if m.group(0) not in tools]
            if may_blocker:
                found += [("BLOCKER", nm)
                          for nm, _form in _blocker_candidates(line, cols[n])
                          if nm not in blockers]
            if not found:
                continue

            mints = bool(_MINTS.search(line))
            modal = bool(_MODAL.search(line))
            header = heads[n]
            proposal_table = bool(header and _PROPOSAL_HEADER.search(header))

            for kind, name in dict.fromkeys(found):
                if kind == "TOOL" and doc_is_spec:
                    verdict = "MARKED-SPEC-DOC"
                elif modal:
                    verdict = "MARKED-HYPOTHETICAL"
                elif mints:
                    verdict = "MARKED-PROPOSAL"
                elif proposal_table:
                    verdict = "MARKED-PROPOSAL-TABLE"
                else:
                    if name not in doc_cache:
                        doc_cache[name] = _doc_marks(blob, name)
                    verdict = doc_cache[name] or "ASSERTED-ABSENT"
                sites.append(Site(kind, name, doc, n, verdict, line.strip()))
    return sites


def findings(sites: Iterable[Site]) -> list[Site]:
    return sorted(
        (s for s in sites if s.verdict == "ASSERTED-ABSENT"),
        key=lambda s: (s.doc, s.line, s.name),
    )


def run(repo: pathlib.Path) -> tuple[list[Site], list[Site]]:
    corpus = load_corpus(repo)
    sites = classify(corpus, tool_registry(repo), set(blocker_registry(repo)))
    return sites, findings(sites)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true",
                    help="print every candidate site, not only the findings")
    args = ap.parse_args(argv)

    sites, bad = run(ROOT)

    if args.all:
        for s in sorted(sites, key=lambda x: (x.kind, x.name, x.doc, x.line)):
            print(s)
        print()

    # A guard must say what it did NOT check, every time, or its PASS is a
    # half-truth. These three lines are that statement.
    considered = len(sites)
    print(f"candidate sites considered : {considered}")
    print(f"cleared by an author mark  : {considered - len(bad)}")
    print(f"ASSERTED and ABSENT        : {len(bad)}")
    print("NOT checked: unbackticked UPPER-KEBAB outside a slot, prose names of "
          "no fixed vocabulary, whether a RESOLVING citation points at the "
          "right thing, and locator line numbers.")
    if not bad:
        print("\nno asserted name is absent.")
        return 0
    print()
    for s in bad:
        print(s)
        print(f"    {s.text[:160]}")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
