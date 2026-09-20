"""Every commit SHA a tracked `_audit/` document CITES must resolve in a clone.

THE DEFECT CLASS. A short SHA in an audit document is a promise a reader can
check. When the promise is broken the reader does not get an error, because
nobody re-runs a citation: they get a sentence that still reads authoritatively
and names nothing. `2026-08-24-perform-save-unsave.md` said *"All at `5a69147`
unless stated"* for ten days after `5a69147` stopped existing, and every
measurement under that heading became uncheckable without one word of the
document changing.

THE PREDICATE, and it is the whole instrument::

    git merge-base --is-ancestor <sha> master     # read by EXIT CODE only

NEVER ``git cat-file -t`` / ``-e``. Those answer "is this object in THIS object
store", which is a different question and the wrong one: this repository keeps
a `pre-purge-restore` tag and 80+ `worktree-agent-*` branches alive, so an
object unreachable from any published ref still answers "commit" locally. A
guard built on ``cat-file`` passes green on a citation no clone can resolve --
measured: all six SHAs the 2026-09-20 repair handled answered "commit" to
``cat-file`` and exit 1 to ``--is-ancestor``.

============================================================================
KIND BEFORE RESOLUTION
============================================================================

**A resolver's zero means "not of this kind, OR absent", and it cannot tell
those apart.** So this guard decides what a token IS before it asks git about
it. Asking first is how a sibling census reported 325 dangling citations when
the real number was two figures lower: 280 of them were LinkedIn Help Center
article ids, shaped `a` + 6-8 digits, sitting correctly in a census column
headed `source`.

At least seven vocabularies in this corpus share the 7-8 lowercase-hex shape:

    abbreviated commit SHAs          `5a69147`
    LinkedIn Help Center article ids `a540461`, `a10376002`
    obfuscated CSS class fragments   `bb9bff38 _7917aabf ...`
    UUID first segments              `componentkey="e205ae22-..."`
    DOM component keys               `jobs.ApplyInterceptModal#4e38fb36`
    truncated sha256 digests         `959cb67f...469ad3`
    allowlist-set digests            `_ALLOWED_URL_PATTERNS 6542383b4619c935`

and two more that are pure decimal and therefore also valid hex: CI run ids
(11 digits, 32-35 billion) and LinkedIn job ids (10 digits).

SHAPE CANNOT SEPARATE THESE AND NEITHER CAN A RESOLVER. Two measurements say
so, and they point in OPPOSITE directions, which is why no single filter works:

* `a540461` and `a604394` are shaped exactly like help-article ids and are
  REAL COMMITS -- so the ``^a[0-9]{6,8}$`` pre-filter that fixes the 280
  ALSO DELETES TWO GENUINE CITATIONS, one of which does not resolve and is a
  real finding.
* `5480246`, `5581950` and `9580360` are all-digit and are REAL COMMIT SHAs --
  `9580360` is a live twin inside an existing mapping table, and `5581950` is
  one of the six a previous repair handled. Every "not all digits" pre-filter
  in use today drops all three silently.

**So the SLOT decides, not the shape.** A token is a commit citation because
this corpus's grammar put it in a position reserved for one. Only then is git
asked. The slot phrases in :data:`SLOTS` were MEASURED over the corpus, not
guessed, and one was measured and DROPPED -- see :data:`DROPPED_SLOTS`.

============================================================================
THE HALF THAT MAKES IT USABLE: A DEAD SHA CAN BE CORRECTLY RECORDED
============================================================================

**A repaired citation and an unrepaired one have the SAME TOKEN SHAPE.** This
is the finding that makes a shape-only census unusable here, and it is the
reason this guard has suppressors at all.

When a rewrite killed 24 SHAs across two documents in August, the repair did
not delete them. It could not: the dead hash is the KEY a reader arrives with.
It put each one in the left column of a mapping table beside the surviving
commit SUBJECT and the new hash, and it put a note at the very top of each
document saying every SHA below is dead. That is the correct repair, and it
leaves 24 unresolvable tokens in the tree on purpose.

A guard that fires on them is a guard that punishes the repair and gets
switched off. So a citation is suppressed when its own document has already
discharged the burden -- and, exactly as the sibling `check_asserted_names_resolve`
guard found for names, THIS CORPUS ALREADY MARKS THESE, in the author's own
words. Every suppressor below quotes the corpus rather than inventing wording.

============================================================================
WHAT THIS GUARD DOES NOT DO
============================================================================

It does not resolve SHAs belonging to OTHER repositories. `jobcore` and
`ats-jobs` commits are cited correctly in documents named for those
repositories, and asking this repo about them is the same error as asking
`cat-file` about a help-article id. They are suppressed by
:data:`CROSS_REPO_DOCS` and the containing document is the evidence.

It does not check that a resolvable SHA says what the document claims it says.
A citation can resolve and still be wrong about its own content; that is a
different and much more expensive instrument.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
from typing import Iterable, NamedTuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS_DIR = "_audit"
BASELINE_REF = "master"

#: Any run of 7-40 lowercase hex standing as a word. Decimals are NOT excluded:
#: see the module docstring -- three genuine SHAs in this corpus are all-digit.
#: The left boundary rejects `_`, `.`, `/` and `-` so that UUID tails, file
#: extensions, URL path segments and the `_<hash>` CSS-class spelling are not
#: re-cut into fresh tokens. That boundary choice is worth 11 distinct phantom
#: tokens: a census using a plain `\b` reported 732 where this reports 721, and
#: all 11 of the difference were CSS class fragments glued to a leading `_`.
HEX = r"[0-9a-f]{7,40}"
_TOKEN_OK = re.compile(r"^[0-9a-f]{7,40}$")

#: THE ONE SHAPE RULE, and it is a MEASURED bound rather than a guess.
#:
#: This corpus's 64-bit content digests are written as 16 lowercase hex, in the
#: same grammar a commit citation uses -- *"`<functions>` is byte-identical at
#: `eb16cd07f5cf369d`"*, *"PRE-EXISTING entry lands on `1d679b9ca1004849`"* --
#: so the slot alone cannot separate them.
#:
#: MEASURED OVER EVERY TOKEN THIS GUARD'S OWN SLOTS SELECT, and printed as what
#: was SEEN at each length rather than as a verdict::
#:
#:     length   ANCESTOR  LOCAL-ONLY  ABSENT
#:          7        186          29      22
#:          8          1           0       0
#:         12         10           2       0     <- `build.code.commit` field width
#:         16          0           0       3
#:
#: Commit citations here are 7, 8 or 12 characters -- 12 because
#: `linkedin_server_info` reports `build.code.commit` at that width. **Not one
#: resolving citation is 16 characters, and all three 16-character tokens in a
#: commit slot are digests.** Corroborated corpus-wide: of 47 distinct 16-hex
#: tokens anywhere in `_audit/`, zero resolve as a commit object.
#:
#: The bound excludes 16 ALONE. It deliberately does NOT exclude 32, 40 or 64:
#: a full 40-character SHA is a legitimate citation and excluding it to be tidy
#: would trade a measured rule for a symmetrical-looking one.
DIGEST_LENGTHS = frozenset({16})


class Slot(NamedTuple):
    name: str
    pattern: re.Pattern[str]


#: Positions this corpus reserves for a commit reference. EACH WAS MEASURED
#: over the tracked corpus before adoption -- occurrences selected, and how
#: many of those were of a known OTHER kind. A phrase that selected another
#: vocabulary at any material rate was dropped rather than tuned.
SLOTS: tuple[Slot, ...] = (
    Slot("at-backtick", re.compile(r"\bat\s+`(" + HEX + r")`")),
    Slot("at-bare", re.compile(r"\bat\s+(" + HEX + r")\b")),
    Slot("commit", re.compile(r"\bcommit\s+`?(" + HEX + r")`?")),
    Slot("committed", re.compile(r"\bcommitted\s+(?:at\s+)?`(" + HEX + r")`")),
    Slot("landed-on", re.compile(r"\bland(?:ed|s)\s+on\s+`(" + HEX + r")`")),
    Slot("landed-after", re.compile(r"`(" + HEX + r")`\s+land(?:ed|s)\b")),
    Slot("range-lhs", re.compile(r"`(" + HEX + r")\.\." + HEX + r"`")),
    Slot("range-rhs", re.compile(r"`" + HEX + r"\.\.(" + HEX + r")`")),
    Slot("applied", re.compile(r"\bapplied\s+.{0,20}?`(" + HEX + r")`")),
    Slot("show-path", re.compile(r"`(" + HEX + r"):[A-Za-z_./]")),
    Slot("introduced-at", re.compile(r"\bintroduced\s+at\s+`(" + HEX + r")`")),
    Slot("baseline", re.compile(r"\bbaseline\s+`(" + HEX + r")`")),
    Slot("pinned-commit", re.compile(r"\bpinned\s+commit\s+`?(" + HEX + r")`?")),
)

#: MEASURED AND REJECTED, kept here because a refusal that names only what it
#: did NOT match is half a measurement. A bare ``in `X` `` selects 44
#: occurrences in this corpus and **8 of them are LinkedIn help-article ids** --
#: including `2026-09-05-decide-retire-rulings.md`'s own
#: *"found in `a1341821`, an article neither..."*, where the document names the
#: kind in the same clause. Adding it would buy 31 more resolvable citations
#: this guard does not need and one leak class it cannot afford.
DROPPED_SLOTS = {
    "bare-in": (
        r"\bin\s+`(" + HEX + r")`",
        "44 occurrences selected, 8 of them help-article ids "
        "(a1341821, a540461, a540837, a550169, a564064 among them)",
    ),
}

#: DOCUMENT-SCOPED SUPPRESSOR 1 -- the document declares its own SHAs dead, at
#: the top, where a reader meets it before any citation. Quoted from the corpus:
#:
#:   "**EVERY SHORT SHA IN THIS FILE IS DEAD.** Added 2026-09-03."
#:       _audit/2026-08-24-perform-save-unsave.md:3
#:   "**EVERY SHORT SHA IN THIS FILE IS DEAD, and the subjects above replace
#:    the two that were in the title.** Added 2026-09-03."
#:       _audit/2026-08-24-out-of-scope-wave.md:3
#:
#: The damage model is "a reader is stopped". A reader of either document meets
#: this sentence first and is not stopped.
_DECLARED_DEAD_DOC = re.compile(
    r"EVERY\s+SHORT\s+SHA\s+IN\s+THIS\s+FILE\s+IS\s+DEAD", re.IGNORECASE
)

#: HOW FAR INTO A DOCUMENT THE DECLARATION MAY SIT, and this bound is not
#: cosmetic -- without it the suppressor is defeated by any document that
#: QUOTES the declaration.
#:
#: **MEASURED ON THIS GUARD'S OWN FIRST POST-COMMIT RUN.** The audit document
#: written to report this wave quotes the phrase twice, once in prose and once
#: in a table of suppressors. Both are discussion, neither is a declaration --
#: and the unbounded pattern read them AS one, silently clearing every citation
#: in the reporting document. `MARKED-DEAD-DOC` jumped 2 -> 9 and the guard got
#: quieter, which is the worst direction for a defect to move.
#:
#: This repository has now hit the identical shape three times: a
#: correction-marker guard read a sentence ABOUT markers as a marker; the
#: instrument register quoted a planted citation into a live commit slot; and
#: this. **PROSE ABOUT A MECHANISM IS INDISTINGUISHABLE FROM THE MECHANISM TO A
#: MATCHER THAT ONLY LOOKS AT SHAPE.** The correction guard's fix was to anchor
#: at line start, on the reasoning that a declaration is a LINE and not a
#: phrase. The same reasoning applies here with position as well as anchoring:
#: a declaration is something a reader meets BEFORE the citations it covers, so
#: one at line 242 protects nothing at line 20 and is not a declaration at all.
#:
#: 40 lines, against a measured 3 and 3 for the two real declarations. Wide
#: enough for a longer preamble, far short of any document's body.
_DECLARATION_WINDOW = 40

#: DOCUMENT-SCOPED SUPPRESSOR 2 -- a mapping table exists. Its heading is the
#: corpus's own: "## Dead hashes, recovered". Rows are
#: ``| dead | subject | live | confidence |``. The dead hash in column 0 is the
#: KEY a reader arrives with and MUST NOT be rewritten; that is what makes the
#: repair a repair. Suppression is per-token, not per-document: a document with
#: a mapping table is not thereby excused for citing some OTHER dead SHA.
_MAPPING_HEADING = re.compile(r"^#+\s*Dead hashes,\s*recovered\s*$", re.IGNORECASE | re.MULTILINE)

#: SUPPRESSOR 3 -- the document DISCLOSES that this particular SHA does not
#: resolve. Token-specific and document-scoped, and both halves are
#: load-bearing. Token-specific, so a document that honestly discloses one dead
#: SHA is not thereby excused for citing a different live-looking one.
#: Document-scoped, because the damage model is "a reader is stopped", and a
#: reader of this document is not stopped.
#:
#: THE WORDING WAS READ OFF THE CORPUS, NOT INVENTED. Every phrase below is
#: something a wave already wrote when it found one of these:
#:
#:   "`86b8ed5` and `5581950` (READINGS table, above) do not resolve on `master`."
#:       _audit/2026-09-19-routing-the-unassigned.md:289
#:   "and no clone can reach `5a69147`, so **no reader can check the measurement**"
#:       _audit/2026-09-20-names-that-do-not-exist.md:701
#:   "`git show b2f5d16:...` cannot resolve in a clone of the remote"
#:       _audit/2026-08-31-jobcore-paths.md:34
#:
#: THIS SUPPRESSOR WAS ADDED BECAUSE THE GUARD'S FIRST RUN CONVICTED THE THREE
#: DOCUMENTS THAT HAD DONE THE RIGHT THING. A guard that fires on the repair is
#: a guard that gets switched off, and the first version of this one fired on
#: the sentence *"no clone can reach `5a69147`"* -- a document being correct
#: out loud, in the exact words this docstring recommends.
_DISCLOSURE = re.compile(
    r"do(?:es)?\s+not\s+resolve"
    r"|cannot\s+resolve"
    r"|can(?:not|'t)\s+reach"
    r"|no\s+clone\s+can\s+(?:reach|resolve)"
    r"|resolves?\s+nowhere"
    r"|resolves?\s+to\s+nothing"
    r"|unresolvable"
    r"|is\s+dead\b|are\s+dead\b"
    # "became a commit on a backup branch and nowhere on `master`"
    #     _audit/2026-09-03-typeahead-name-matching-is-dead.md:323
    r"|nowhere\s+on\b",
    re.IGNORECASE,
)

#: Markdown emphasis markers, stripped before the disclosure search so that
#: "does **not** resolve" reads the same as "does not resolve". Backticks are
#: NOT stripped, because a disclosure names its SHA in backticks and removing
#: them would run the token into the surrounding words.
_EMPHASIS = re.compile(r"\*+|(?<=\w)_(?=\w)")

#: How far a disclosure may sit from the token it discloses. 2 lines, matching
#: the corpus's own re-wrapping: `routing-the-unassigned.md` names both tokens
#: on :289 and carries "do not resolve" on the same line, but
#: `search-shaper.md` splits the same sentence across :19-:20 at a narrower
#: column. Wider than 2 and a disclosure about one SHA would start clearing an
#: unrelated one in the next paragraph.
_DISCLOSURE_WINDOW = 2

#: SUPPRESSOR 4 -- the citation names another repository. The containing
#: document is the slot that decides WHICH registry a token is drawn from, and
#: these documents say so in their own titles and prose:
#:
#:   "# The leak was upstream: jobcore's first sweep, and the pin that could
#:    not move"                      _audit/2026-08-31-jobcore-paths.md:1
#:   "compares its body against jobcore at the pinned commit `6acc7e6`"
#:                                   _audit/2026-08-31-jobcore-paths.md:58
#:   "`origin/master`** (`fe21292`, remote `Sundeepg98/ats-jobs-mcp`)"
#:                                   _audit/2026-08-31-jobcore-paths.md:44
#:
#: All five were resolved in their own repositories on 2026-09-20 and all five
#: are ancestors of a freshly-fetched `origin/master` there, so they are
#: CORRECT citations that this repository is simply the wrong place to ask.
CROSS_REPO_TOKENS: dict[str, str] = {
    "5480246": "jobcore",
    "6acc7e6": "jobcore",
    "b2f5d16": "jobcore",
    "fff1438": "jobcore",
    "fe21292": "ats-jobs",
}

#: Where a cross-repo token may appear. Naming the DOCUMENTS as well as the
#: tokens keeps the suppressor from silencing the same hex anywhere in the
#: corpus: a jobcore SHA cited in a linkedin wave's own measurement section
#: would still be a finding.
CROSS_REPO_DOCS = (
    "_audit/2026-08-31-jobcore-paths.md",
    "_audit/2026-08-31-linkedin-lift.md",
)


class Site(NamedTuple):
    token: str
    doc: str
    line: int
    slot: str
    verdict: str
    text: str

    def __str__(self) -> str:
        return f"{self.doc}:{self.line}  {self.token}  [{self.slot}/{self.verdict}]"


def _git(repo: pathlib.Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


#: `_audit/INDEX.md` is GENERATED -- a derived view of this corpus, not a
#: member of it. It quotes correction reasons VERBATIM, and A QUOTE DOES NOT
#: CARRY THE QUOTED DOCUMENT'S MARKS. `1349fe6` is cited by four documents,
#: each of which opens with a SHA NOTE declaring it branch-only; the quote
#: carries the hash and leaves the note behind, so the index convicted for a
#: promise it never made. **The index makes no claims; it reports that others
#: did.** Third instrument to need this exclusion on 2026-09-20 -- see
#: INSTRUMENTS.md section 45.9, and the same line in
#: `scripts/check_asserted_names_resolve.py` and
#: `scripts/find_blocker_reason.py`.
GENERATED_VIEWS = frozenset({"_audit/INDEX.md"})


def tracked_docs(repo: pathlib.Path) -> list[str]:
    out = _git(repo, "ls-files", CORPUS_DIR).stdout
    return sorted(p for p in out.splitlines()
                  if p.endswith(".md") and p not in GENERATED_VIEWS)


def load_corpus(repo: pathlib.Path) -> dict[str, str]:
    blobs: dict[str, str] = {}
    for rel in tracked_docs(repo):
        path = repo / rel
        try:
            blobs[rel] = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return blobs


#: A mapping row is allowed to have NO live hash, but only when it SAYS SO.
#:
#: MEASURED, AND IT CONVICTED THE CORRECT REPAIR ON ITS FIRST RUN. The live-hash
#: check below was written without this exemption and immediately red-flagged
#: `94600de` and `db99276` in `2026-08-24-perform-save-unsave.md`. Those two
#: rows read ``| `94600de` | **UNMAPPED** -- see below | -- | UNMAPPED |`` and
#: the document spends two paragraphs explaining that the evidence CONFLICTS --
#: every positional candidate is already claimed on better evidence by a
#: different dead hash. The 2026-09-20 sixty-dangling wave ruled on exactly
#: this: *"'UNMAPPED' is not a shortfall. A guessed hash has no twin to find.
#: Recording the gap IS the repair."*
#:
#: So a declared no-twin row is a legitimate, ruled state and is counted and
#: printed rather than convicted. A row that is merely SILENT about its missing
#: live hash is still a finding: the difference between the two is the whole
#: point, and it is the difference between an author who looked and an author
#: who did not.
#:
#: `NEVER-LANDED` is admitted beside `UNMAPPED` for the neighbouring case a
#: sibling measurement found the same day -- 22 commits on eight unmerged local
#: branches whose subjects appear nowhere on `master`. For those the honest
#: annotation is not a twin hash at all; it is that the work never arrived.
_DECLARED_NO_TWIN = ("unmapped", "never-landed", "never landed")


class Remap(NamedTuple):
    """One row of a `## Dead hashes, recovered` table, as the document claims it."""
    doc: str
    line: int
    dead: str
    subject: str
    live: str
    confidence: str

    @property
    def declares_no_twin(self) -> bool:
        cell = _EMPHASIS.sub("", self.confidence).strip().casefold()
        return any(cell.startswith(w) for w in _DECLARED_NO_TWIN)

    def __str__(self) -> str:
        return f"{self.doc}:{self.line}  {self.dead} -> {self.live or '(no live hash)'}"


def mapping_rows(blob: str) -> list[tuple[int, str, str, str, str]]:
    """(lineno, dead, subject-cell, live) for every row of the mapping table.

    Only a row UNDER the mapping heading counts, and only column 0 supplies a
    dead hash. A SHA in the subject or live column is a different claim and is
    not suppressed by being nearby.
    """
    m = _MAPPING_HEADING.search(blob)
    if not m:
        return []
    offset = blob[: m.end()].count("\n")
    rows: list[tuple[int, str, str, str, str]] = []
    for i, line in enumerate(blob[m.end():].splitlines(), start=offset + 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            # A later heading of the same or higher level ends the section.
            if not stripped.lstrip("#").strip().lower().startswith("the "):
                break
        if not stripped.startswith("|"):
            continue
        cells = [c.strip().strip("`* ") for c in stripped.strip("|").split("|")]
        if cells and _TOKEN_OK.match(cells[0]):
            subject = cells[1].strip() if len(cells) > 1 else ""
            live = cells[2].strip().strip("`* ") if len(cells) > 2 else ""
            confidence = cells[3].strip() if len(cells) > 3 else ""
            rows.append((i, cells[0], subject,
                         live if _TOKEN_OK.match(live) else "", confidence))
    return rows


def mapped_tokens(blob: str) -> set[str]:
    """Dead hashes this document's own mapping table claims to have recovered."""
    return {dead for _, dead, _, _, _ in mapping_rows(blob)}


def remap_claims(blobs: dict[str, str]) -> list[Remap]:
    """Every mapping-table row in the corpus, with NO resolver consulted."""
    out: list[Remap] = []
    for doc in sorted(blobs):
        for line, dead, subject, live, confidence in mapping_rows(blobs[doc]):
            out.append(Remap(doc, line, dead, subject, live, confidence))
    return out


def broken_remaps(repo: pathlib.Path, claims: Iterable[Remap]) -> list[tuple[Remap, str]]:
    """Mapping rows whose own repair does not hold up. THE POINT OF THIS CHECK.

    `MARKED-MAPPED` is the strongest suppressor this guard has: it silences a
    dead hash at every one of its sites in a document. Until now it fired on
    the mere PRESENCE of the hash in column 0 -- so a row could name any live
    hash at all, or none, and still switch the guard off for that token. A
    repair nobody can check is the defect this guard exists to find, wearing
    the guard's own uniform.

    So the suppressor now pays for itself. Each row must satisfy, and each
    failure is reported with what was SEEN rather than only that it failed:

      * the row names a live hash at all;
      * that live hash resolves as an ancestor of `master` -- a reader of a
        clone can reach it;
      * the subject cell byte-matches that commit's actual subject, because
        the subject is the durable reference the whole repair rests on and a
        row that quotes the wrong one has mapped the wrong commit;
      * the dead hash is not the live hash.

    **A silently wrong hash is not a repair.** This is the check that says so.
    """
    cache: dict[str, bool] = {}
    subjects: dict[str, str] = {}
    bad: list[tuple[Remap, str]] = []
    for c in claims:
        if c.declares_no_twin:
            # A row that SAYS it has no twin has discharged the burden. See
            # `_DECLARED_NO_TWIN` -- this exemption exists because the check
            # convicted the corpus's own correct repair on its first run.
            continue
        if not c.live:
            bad.append((c, "the row names no live hash in column 2, and its "
                           "confidence cell does not declare the hash UNMAPPED "
                           "or NEVER-LANDED either -- so it is silent rather "
                           "than honest"))
            continue
        if c.live == c.dead:
            bad.append((c, "the row maps the hash to itself"))
            continue
        if c.live not in cache:
            cache[c.live] = resolves(repo, c.live)
            subjects[c.live] = _git(
                repo, "log", "-1", "--format=%s", c.live
            ).stdout.rstrip("\n") if cache[c.live] else ""
        if not cache[c.live]:
            bad.append((c, f"the live hash `{c.live}` does not resolve on {BASELINE_REF} "
                           f"either -- this repair points at nothing"))
            continue
        actual = subjects[c.live]
        if c.subject and actual and c.subject != actual:
            bad.append((c, "the subject cell does not match the live commit.\n"
                           f"          table says: {c.subject}\n"
                           f"          commit says: {actual}"))
    return bad


def resolves(repo: pathlib.Path, token: str, ref: str = BASELINE_REF) -> bool:
    """True iff a clone of `ref` can resolve `token`.

    Two calls, in this order, because `merge-base` on a nonexistent object is
    a fatal error rather than exit 1 and the two must not be conflated.
    """
    if _git(repo, "cat-file", "-e", token + "^{commit}").returncode != 0:
        return False
    return _git(repo, "merge-base", "--is-ancestor", token, ref).returncode == 0


def disclosed_tokens(blob: str) -> set[str]:
    """SHAs this document says, in its own words, do not resolve.

    A token counts as disclosed when disclosure vocabulary sits within
    :data:`_DISCLOSURE_WINDOW` lines of an occurrence of that token -- anywhere
    in the document, not only at its citation site, because the corpus's own
    form is a note at the foot referring back to a table above.
    """
    lines = blob.splitlines()
    # Markdown emphasis INSIDE the phrase defeats a plain word-boundary match:
    # this corpus writes "does **not** resolve on `master`" as often as it
    # writes the unadorned form, and the first version of this suppressor
    # missed every emphasised one. Found on the guard's own audit document,
    # which used the emphasised spelling and was convicted for it.
    plain = [_EMPHASIS.sub("", line) for line in lines]
    disclosing = [i for i, line in enumerate(plain) if _DISCLOSURE.search(line)]
    if not disclosing:
        return set()
    found: set[str] = set()
    for i in disclosing:
        lo = max(0, i - _DISCLOSURE_WINDOW)
        hi = min(len(lines), i + _DISCLOSURE_WINDOW + 1)
        for line in lines[lo:hi]:
            for m in re.finditer(r"(?<![0-9a-zA-Z_./-])(" + HEX + r")(?![0-9a-zA-Z_])", line):
                found.add(m.group(1))
    return found


def candidates(blobs: dict[str, str]) -> list[Site]:
    """Every token sitting in a commit slot. NO resolver is consulted here."""
    sites: list[Site] = []
    for doc in sorted(blobs):
        blob = blobs[doc]
        preamble = "\n".join(blob.splitlines()[:_DECLARATION_WINDOW])
        declared_dead = bool(_DECLARED_DEAD_DOC.search(preamble))
        mapped = mapped_tokens(blob)
        disclosed = disclosed_tokens(blob)
        for lineno, line in enumerate(blob.splitlines(), 1):
            seen_on_line: set[tuple[str, int]] = set()
            for slot in SLOTS:
                for m in slot.pattern.finditer(line):
                    token = m.group(1)
                    if len(token) in DIGEST_LENGTHS:
                        continue
                    key = (token, m.start(1))
                    if key in seen_on_line:
                        continue
                    seen_on_line.add(key)
                    verdict = "CANDIDATE"
                    if token in mapped:
                        verdict = "MARKED-MAPPED"
                    elif declared_dead:
                        verdict = "MARKED-DEAD-DOC"
                    elif token in CROSS_REPO_TOKENS and doc in CROSS_REPO_DOCS:
                        verdict = "MARKED-CROSS-REPO"
                    elif token in disclosed:
                        verdict = "MARKED-DISCLOSED"
                    sites.append(Site(token, doc, lineno, slot.name, verdict, line.strip()))
    return sites


def findings(repo: pathlib.Path, sites: Iterable[Site]) -> list[Site]:
    """Candidates that no clone can resolve. Resolution runs LAST, by design."""
    cache: dict[str, bool] = {}
    out: list[Site] = []
    for s in sites:
        if s.verdict != "CANDIDATE":
            continue
        if s.token not in cache:
            cache[s.token] = resolves(repo, s.token)
        if not cache[s.token]:
            out.append(s._replace(verdict="UNRESOLVED"))
    return out


def run(repo: pathlib.Path = ROOT) -> tuple[list[Site], list[Site]]:
    sites = candidates(load_corpus(repo))
    return sites, findings(repo, sites)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    verbose = "-v" in argv or "--verbose" in argv
    blobs = load_corpus(ROOT)
    if not blobs:
        # An instrument handed an empty corpus must be LOUD, never green.
        print(f"EMPTY CORPUS -- `git ls-files {CORPUS_DIR}` returned no .md files.")
        print("That is a broken aim, not a clean repository. Treating as FAIL.")
        return 2
    sites = candidates(blobs)
    bad = findings(ROOT, sites)
    claims = remap_claims(blobs)
    broken = broken_remaps(ROOT, claims)

    if verbose:
        for s in sorted(sites, key=lambda x: (x.doc, x.line)):
            print(f"  {s}")

    # A refusal must say what it SAW, not only what it did not match.
    by_verdict: dict[str, int] = {}
    for s in sites:
        by_verdict[s.verdict] = by_verdict.get(s.verdict, 0) + 1
    print(f"commit-slot occurrences : {len(sites)}")
    for v in sorted(by_verdict):
        print(f"  {v:<20} {by_verdict[v]}")
    print(f"distinct tokens in slot : {len({s.token for s in sites})}")
    declared = [c for c in claims if c.declares_no_twin]
    print(f"remap rows checked      : {len(claims)}"
          f" in {len({c.doc for c in claims})} document(s)")
    print(f"  of those, rows that DECLARE no twin exists: {len(declared)}")
    for c in declared:
        print(f"      {c.doc}:{c.line}  {c.dead}  [{c.confidence}]")

    if not sites:
        # An assertion satisfied by an empty result cannot fail.
        print("EMPTY CANDIDATE SET -- the slot patterns matched nothing at all.")
        print("That is a broken extractor, not a clean corpus. Treating as FAIL.")
        return 2

    if broken:
        print(f"\n{len(broken)} mapping-table row(s) whose own repair does not hold:\n")
        for c, why in broken:
            print(f"  {c}")
            print(f"      {why}")
        print(
            "\nA `## Dead hashes, recovered` row SILENCES this guard for that hash at\n"
            "every one of its sites. A row that cannot be checked is a suppression\n"
            "wearing a repair's name. Fix the row or remove it -- an unrepaired\n"
            "citation that the guard still reports is better than a repaired-looking\n"
            "one nobody can follow."
        )
        return 1

    if not bad:
        print(f"OK: every cited SHA resolves as an ancestor of {BASELINE_REF}, and"
              f" all {len(claims)} remap row(s) check out.")
        return 0

    print(f"\n{len(bad)} citation(s), {len({s.token for s in bad})} distinct SHA(s), "
          f"that no clone can resolve:\n")
    for s in sorted(bad, key=lambda x: (x.doc, x.line)):
        print(f"  {s}")
        print(f"      {s.text[:160]}")
    print(
        "\nEach one is a promise a reader cannot check. The repair is NOT to delete\n"
        "the hash -- it is the key a reader arrives with. Record the commit SUBJECT,\n"
        "which survives a rewrite, and map the dead hash to it under a\n"
        "'## Dead hashes, recovered' heading, or declare the document's SHAs dead\n"
        "at the top. Where no honest twin exists, say so: an annotated dangling SHA\n"
        "is honest, and a plausible wrong remap cannot be caught afterwards."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
