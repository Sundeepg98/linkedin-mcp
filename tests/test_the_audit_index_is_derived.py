"""`_audit/INDEX.md` must stay DERIVED, and the derivation must be able to fail.

WHY THIS EXISTS. `_audit/` held 195 tracked documents and 5.4 MB of prose with
no index of any kind, and `scripts/` contained nothing that made one. The only
ways in were grep and somebody's memory. That is not a housekeeping complaint:
the same day it was measured produced four count-drifts between a machine-
checked constant and the prose beside it, a section asserting a 22-pattern
allowlist that had held 42 for a fortnight, and a `CORRECTED BY:` marker that
was itself stale. **A corpus nobody can navigate is a corpus nobody re-reads.**

AND AN INDEX IS THE EASIEST THING IN THIS REPOSITORY TO GET WRONG IN EXACTLY
THAT WAY. A hand-written one over 195 documents would be the fifth count-drift
of the day inside a week. So `scripts/build_audit_index.py` derives every cell
from the corpus, and this file re-derives it and compares. Add a document, add
a marker, change a title, and the committed index no longer matches what the
corpus produces -- red, with the first differing line printed.

## SHOWN FAILING -- an instrument that has only ever been green certifies nothing

Every red proof below runs over a SYNTHETIC corpus in `tmp_path`. That is not
squeamishness: `_audit/` is written continuously by concurrent waves, and the
register's own preamble records a wave that proved three gates by mutating a
file another agent was holding uncommitted work in. `render()` is pure over an
explicit document list precisely so that the proof needs no live mutation.

    a document added to the corpus            -> drift, named
    a document removed from the corpus        -> drift, named
    a title edited                            -> drift, named
    one character flipped in the index        -> drift, named
    a marker pair declared in the corpus      -> drift, named
    an empty corpus                           -> vacuity, not a green pass
    prose that MENTIONS a marker              -> must NOT become an edge
    a marker inside a fenced code block       -> counted and reported, not silent
    a blockquoted marker naming a document    -> reported as HIDDEN, not folded in
    a pipe in a title                         -> escaped, column arity held
    a pair declared twice                     -> BOTH reasons survive
    a reason after a backticked symbol        -> printed in full, not truncated
    a backticked link                         -> the citation comes straight back

`scripts/_check_audit_index_guard_can_fail.py` is the other half, and it makes
the claim these controls cannot: it copies the tree, plants SEVEN defects and
runs THE REAL PYTEST SELECTOR against each one, asserting it goes red for the
right reason and green again after every restore. The controls here prove the
generator is sensitive; that file proves the assertion which gates a commit has
actually failed.

**IT ALSO FOUND THE DEFECT NOBODY WOULD HAVE READ FOR.** On its first run the
copy was not green before any mutation, because `_audit/INDEX.md` had become
tracked and therefore part of its own corpus -- section 3 quotes four
marker-shaped lines verbatim, so the count read 4, then 8, then 12, and no
fixpoint existed. A harness whose only job was to prove the guard could fail
found a bug in the thing under proof, before the first commit.

THE LAST FOUR ARE NOT HYPOTHETICAL AND THAT IS WHY THEY ARE HERE. Each was
found by running the generator over the real corpus:

* **A pair declared twice.** 68 `CORRECTS:` lines and 68 `CORRECTED BY:` lines
  resolve to 65 distinct pairs. The shipped correction guard stores them in
  `dict[(source, target)]`, so three declarations overwrite three others and
  three reasons are unreadable through it.
* **A truncated reason.** `test_a_correction_is_findable_from_the_claim._reason_on`
  takes everything after the LAST backtick on the line; its docstring says
  *whatever a marker line says after the document it names*. Those differ on
  **65 of 136** marker lines in this corpus. The worst returns 29 characters of
  a 767-character reason. The guard stays green on every one, because it only
  asks whether the fragment is 20 characters long, and a fragment can be.
* **A lopsided edge.** Two pairs are declared twice in one direction and once
  in the other. The guard's both-directions test is over distinct pairs, so two
  corrected claims under one back-pointer read to it as one clean pair.
* **A backticked link.** 490 resolvable citations and 153 candidate pairs, from
  link text alone, in a file that makes no claims about anything.

## WHAT THIS FILE DOES NOT ASSERT

It does not assert a TOTAL. `_audit/` grows by dozens of documents a day, and a
pinned count would be a guaranteed false red by tomorrow. What it asserts is an
IDENTITY that survives the corpus moving: the committed index IS what the
current corpus derives. A wave that adds a document turns this red, which is
the design working -- regenerate and commit.

Nothing here reaches LinkedIn, an account, or a browser. It reads committed
markdown and nothing else.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_audit_index as bai  # noqa: E402
import test_a_correction_is_findable_from_the_claim as guard  # noqa: E402


# --------------------------------------------------------------------------
# A synthetic corpus, so a red proof never touches a tree other waves write
# --------------------------------------------------------------------------

def _corpus(tmp_path, files: dict):
    """Write `{basename: text}` into `tmp_path/_audit/` and return (docs, root).

    The returned list is what `render` consumes, so a test can add, remove or
    edit a document by editing this dictionary -- no git, no live tree.
    """
    audit = tmp_path / "_audit"
    audit.mkdir(exist_ok=True)
    docs = []
    for name, text in files.items():
        path = audit / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        docs.append(path)
    return sorted(docs), tmp_path


#: A joined correction pair, spelled the way the corpus spells one.
PAIR = {
    "2026-01-01-the-claim.md": (
        "# The claim\n"
        "\n"
        "Skill endorsement counts are the smallest win left, at zero cost.\n"
        "\n"
        "**CORRECTED BY:** `_audit/2026-01-02-the-measurement.md` -- measured "
        "the next day, and the committed capture carries zero counts.\n"
    ),
    "2026-01-02-the-measurement.md": (
        "# The measurement\n"
        "\n"
        "**CORRECTS:** `_audit/2026-01-01-the-claim.md` -- its zero-cost "
        "ranking was never opened; the real cost is a fresh live load.\n"
    ),
}


# --------------------------------------------------------------------------
# The assertion this file was built for
# --------------------------------------------------------------------------

def test_the_committed_index_is_what_the_corpus_derives():
    """THE DRIFT CHECK. Somebody added a document and did not regenerate.

    Repaired with, from the repository root::

        python scripts/build_audit_index.py --write

    Line endings are normalised before comparing. `core.autocrlf` is true on
    the machine this corpus is written on and false on CI, so the SAME
    committed bytes arrive as CRLF here and LF there -- a byte comparison would
    pass on one and fail on the other, which is the local-passes/clone-fails
    shape this repository has already paid for once.
    """
    committed = bai.committed(ROOT)
    assert committed, (
        "_audit/INDEX.md does not exist. Run: "
        "python scripts/build_audit_index.py --write"
    )
    derived = bai.build(ROOT)
    if committed == derived:
        return

    mine = derived.splitlines()
    theirs = committed.splitlines()
    for number, (one, two) in enumerate(zip(theirs, mine), 1):
        if one != two:
            pytest.fail(
                "_audit/INDEX.md drifted from the corpus at line %d.\n"
                "  committed: %s\n"
                "  derived  : %s\n"
                "Run: python scripts/build_audit_index.py --write"
                % (number, one[:200], two[:200])
            )
    pytest.fail(
        "_audit/INDEX.md has %d lines; the corpus derives %d. "
        "Run: python scripts/build_audit_index.py --write"
        % (len(theirs), len(mine))
    )


def test_there_is_a_corpus_and_the_index_covers_all_of_it():
    """A sweep over nothing passes forever.

    Not a pinned total -- the corpus grows daily -- but a floor plus the
    identity that matters: EVERY tracked document has a row, and every row
    names a tracked document. An index missing a document is the failure this
    whole wave exists to fix, wearing a green tick.
    """
    docs = bai.tracked_documents(ROOT)
    assert len(docs) > 50, len(docs)

    names = [doc.name for doc in docs]
    assert len(names) == len(set(names)), sorted(
        name for name in names if names.count(name) > 1
    )

    text = bai.committed(ROOT)
    assert text, "run: python scripts/build_audit_index.py --write"

    table = [line for line in text.splitlines() if line.startswith("| 2")
             or line.startswith("| %s |" % bai.UNDATED)]
    assert len(table) == len(docs), (len(table), len(docs))

    for doc in docs:
        inside = doc.relative_to(ROOT / "_audit").as_posix()
        assert "(%s)" % inside in text, inside


def test_the_edge_set_agrees_with_the_shipped_correction_guard():
    """The composite is reimplemented here; assert it equals the shipped one.

    `build_audit_index` imports the correction guard's PATTERNS and extractors
    and reimplements only the `for document, for line` loop, because a pure
    function over an explicit document list is what makes the red proofs above
    possible. **That reimplementation is exactly where a fourth broken parser
    would come from**, so it is not trusted: both composites run over the live
    corpus and their key sets must be identical.

    Only the KEYS. The VALUES deliberately differ -- this index keeps every
    declaration of a pair where the guard keeps the last, and prints the whole
    reason where the guard's extractor stops at the last backtick.
    """
    docs = bai.tracked_documents(ROOT)
    mine_corrects, mine_back, mine_malformed, _ = bai.read_markers(docs, ROOT)
    their_corrects, their_back, their_malformed = guard._declarations()

    assert set(mine_corrects) == set(their_corrects), sorted(
        set(mine_corrects) ^ set(their_corrects)
    )
    assert set(mine_back) == set(their_back), sorted(
        set(mine_back) ^ set(their_back)
    )
    assert len(mine_malformed) == len(their_malformed), (
        mine_malformed, their_malformed
    )


# --------------------------------------------------------------------------
# The preconditions that keep an inherited blind spot harmless
# --------------------------------------------------------------------------

def test_no_marker_hides_inside_a_fenced_code_block():
    """The blind spot this index INHERITS, guarded rather than discovered later.

    The shipped `MARKER` matches a line-opening declaration wherever it sits,
    including inside a fenced code block -- so a document showing an EXAMPLE
    marker in a fence would be read as declaring one. Today there are none, so
    importing the fence-blind pattern costs nothing. This asserts that
    precondition, so the day an example is written into a fence somebody
    adjudicates it instead of the index silently gaining an edge.

    **Prose about a mechanism is indistinguishable from the mechanism to a
    matcher that only reads shape, and it always fails quiet.** That is this
    repository's own recurring defect; the correction guard was itself
    convicted of it.
    """
    offenders = []
    for doc in bai.tracked_documents(ROOT):
        lines = doc.read_text(encoding="utf-8").splitlines()
        offenders.extend(bai.fenced_marker_lines(doc, lines))
    assert offenders == [], offenders


#: Committed titles carrying a codepoint above 127, in a repository whose
#: standing rule is strict ASCII. THIS IS AN ALLOWLIST AND IT IS ITSELF
#: CHECKED, the discipline `NOT_A_CORRECTION` and `UNREACHABLE_BY_DESIGN`
#: already keep here: an entry claims *this document's title really does carry
#: this codepoint*, and a STALE entry fails as loudly as a missing one. A list
#: nobody re-checks is a silencer.
NON_ASCII_TITLES = {
    "2026-08-30-nine-live-census.md": ["U+2014"],
    "2026-09-05-census-hygiene.md": ["U+2014"],
    "2026-09-19-duplicate-register.md": ["U+2014"],
    "2026-09-19-feasibility-self-controlling-zero-guard.md": ["U+2014"],
    "2026-09-19-scope-jobs-rw-column.md": ["U+2014"],
}


def test_a_non_ascii_title_is_declared_and_reported():
    """This repository is strict-ASCII, and a title is quoted verbatim.

    `_ascii` spells any other codepoint as `<U+XXXX>` rather than dropping it,
    because silently stripping a character turns a title into a subtly
    different title that still LOOKS fine -- the exact failure mode this corpus
    keeps producing. So the index prints the escape AND names the document in
    its own section 5, which is the loud channel.

    Found by this test on its first run, not by reading. The wave lead had
    grepped one date's files by hand, found ONE em dash and written a
    one-entry allowlist; the test convicted it immediately and named five. A
    hand count of a corpus is the defect this whole wave is about, committed
    inside the fix for it.
    """
    found = {}
    for doc in bai.tracked_documents(ROOT):
        title = bai.title_of(doc.read_text(encoding="utf-8").splitlines())
        if bai._ascii(title) != title:
            found[doc.name] = sorted(
                {"U+%04X" % ord(char) for char in title if ord(char) > 127}
            )
    assert found == NON_ASCII_TITLES, found

    text = bai.committed(ROOT)
    for name in found:
        assert "NON-ASCII TITLE" in text
        assert name in text


def test_the_whole_index_is_ascii():
    """Belt and braces on the file itself, not only on the titles feeding it.

    Titles are not the only quoted text -- 65 correction reasons are quoted
    verbatim too, and nothing had ever checked those for a stray codepoint.
    This asserts the OUTPUT, so a channel nobody thought of is covered by the
    same line.
    """
    text = bai.committed(ROOT)
    assert text, "run: python scripts/build_audit_index.py --write"
    bad = sorted({char for char in text if ord(char) > 127})
    assert bad == [], ["U+%04X" % ord(char) for char in bad]


# --------------------------------------------------------------------------
# SHOWN FAILING -- the drift check
# --------------------------------------------------------------------------

def test_control_a_new_document_makes_the_index_stale(tmp_path):
    """Add a document without regenerating: the derivation must move."""
    docs, root = _corpus(tmp_path, PAIR)
    before = bai.render(docs, root)

    more = dict(PAIR)
    more["2026-01-03-a-later-note.md"] = "# A later note\n\nNothing yet.\n"
    docs_after, _ = _corpus(tmp_path, more)
    after = bai.render(docs_after, root)

    assert before != after
    assert "2026-01-03-a-later-note.md" not in before
    assert "2026-01-03-a-later-note.md" in after


def test_control_a_removed_document_makes_the_index_stale(tmp_path):
    """And the other direction, which a growth-only check would miss."""
    docs, root = _corpus(tmp_path, PAIR)
    full = bai.render(docs, root)
    fewer = bai.render([d for d in docs if "measurement" not in d.name], root)
    assert full != fewer
    assert "2026-01-02-the-measurement.md" in full


def test_control_an_edited_title_makes_the_index_stale(tmp_path):
    """A title is a cell. Editing one must move the derivation."""
    docs, root = _corpus(tmp_path, PAIR)
    before = bai.render(docs, root)

    edited = dict(PAIR)
    edited["2026-01-01-the-claim.md"] = edited[
        "2026-01-01-the-claim.md"].replace("# The claim", "# The claim, redone")
    docs_after, _ = _corpus(tmp_path, edited)
    after = bai.render(docs_after, root)

    assert before != after
    assert "The claim, redone" in after


def test_control_one_flipped_character_is_caught(tmp_path):
    """The comparison is exact, not a fuzzy match on section headings."""
    docs, root = _corpus(tmp_path, PAIR)
    derived = bai.render(docs, root)
    mutated = derived.replace("| audit documents git tracks under `_audit` | 2 |",
                              "| audit documents git tracks under `_audit` | 3 |")
    assert mutated != derived, "the mutation did not apply; the proof is vacuous"
    assert mutated.splitlines() != derived.splitlines()


def test_control_a_new_marker_pair_makes_the_index_stale(tmp_path):
    """The correction graph is the point of the file, so it must move too."""
    docs, root = _corpus(tmp_path, {
        "2026-01-01-the-claim.md": "# The claim\n\nA claim nobody corrected.\n",
        "2026-01-02-the-measurement.md": "# The measurement\n\nNothing yet.\n",
    })
    before = bai.render(docs, root)
    assert "| distinct declared correction edges | 0 |" in before
    assert "_No document in this corpus carries a `CORRECTED BY:` marker._" \
        in before

    docs_after, _ = _corpus(tmp_path, PAIR)
    after = bai.render(docs_after, root)
    assert "**CORRECTED x1**" in after
    assert "corrects x1" in after
    assert before != after


def test_control_an_empty_corpus_is_loud_rather_than_green(tmp_path):
    """An assertion satisfied by an empty result cannot fail.

    The generator must SAY the corpus is empty rather than emit a tidy index of
    nothing that the drift check would then happily certify.
    """
    root = tmp_path
    (root / "_audit").mkdir()
    text = bai.render([], root)
    assert "| audit documents git tracks under `_audit` | 0 |" in text
    assert "_No document in this corpus carries a `CORRECTED BY:` marker._" in text
    assert "_No document in this corpus carries a `CORRECTS:` marker._" in text


# --------------------------------------------------------------------------
# SHOWN FAILING -- the traps this corpus has already paid for
# --------------------------------------------------------------------------

def test_control_prose_that_mentions_a_marker_does_not_become_an_edge(tmp_path):
    """THE TRAP, planted. A document DESCRIBING the mechanism is not using it.

    Three shapes in one file, every one of which a matcher that reads only
    shape would eat: the keyword mid-sentence, the keyword inside inline code,
    and a line whose keyword carries no colon. The corpus is full of documents
    that discuss markers -- `INSTRUMENTS.md` among them, and this file too --
    so this is the live case, not a contrived one.

    **The keyword is written with a leading space below on purpose.** Writing
    it at column 0 in this source would make THIS FILE a declaration to any
    scan of the repository, which is the same joke one level up and not a funny
    one twice.
    """
    docs, root = _corpus(tmp_path, {
        "2026-01-01-the-claim.md": "# The claim\n\nA claim.\n",
        "2026-01-02-the-explainer.md": (
            "# The explainer\n"
            "\n"
            "A corrector writes a CORRECTS: marker naming "
            "`_audit/2026-01-01-the-claim.md`, and the target must then carry "
            "a matching CORRECTED BY: line pointing back at it.\n"
            "\n"
            "Spelled `**CORRECTS:**` inline, it names "
            "`_audit/2026-01-01-the-claim.md` and is still only a sentence.\n"
            "\n"
            "CORRECTS `_audit/2026-01-01-the-claim.md` with no colon at all, "
            "which is prose however it is punctuated.\n"
        ),
    })
    joined, malformed, half_joined, lopsided, truncated = bai.edges(docs, root)

    assert joined == {}, sorted(joined)
    assert malformed == [], malformed

    text = bai.render(docs, root)
    assert "| distinct declared correction edges | 0 |" in text
    assert "| marker-shaped lines inside a fenced code block | 0 |" in text


def test_control_a_fenced_example_marker_is_reported_never_silent(tmp_path):
    """THE INHERITED BLIND SPOT, planted and shown doing the wrong thing.

    The shipped `MARKER` anchors at line start and knows nothing about fences,
    so an EXAMPLE marker inside a code block reads to it as a declaration. This
    index inherits that deliberately -- diverging would make it advertise edges
    the correction guard does not enforce, or hide edges it does, and a reader
    cannot be expected to hold two different definitions of the same marker.

    **SO THE DEFECT IS NOT SUPPRESSED, IT IS PAIRED WITH A PRECONDITION.** This
    control asserts the wrong thing really does happen, and that when it does
    the index says so out loud in its own section 5;
    `test_no_marker_hides_inside_a_fenced_code_block` asserts the live corpus
    contains none, so the day somebody writes one, two instruments fire
    together instead of an edge appearing that nobody declared.

    Asserting the FALSE edge is the point. A control that asserted the fence
    was ignored would be asserting behaviour this file does not have, and would
    go green forever while telling a reader the opposite.
    """
    docs, root = _corpus(tmp_path, {
        "2026-01-01-the-claim.md": "# The claim\n\nA claim.\n",
        "2026-01-02-the-explainer.md": (
            "# The explainer\n"
            "\n"
            "```\n"
            "**CORRECTS:** `_audit/2026-01-01-the-claim.md` -- an example "
            "inside a fence, written to show a reader what one looks like.\n"
            "```\n"
        ),
    })
    joined, malformed, half_joined, lopsided, truncated = bai.edges(docs, root)

    assert list(joined) == [
        ("2026-01-02-the-explainer.md", "2026-01-01-the-claim.md")
    ], sorted(joined)
    assert half_joined == list(joined), half_joined

    text = bai.render(docs, root)
    assert "| marker-shaped lines inside a fenced code block | 1 |" in text
    assert "MARKER INSIDE A FENCE" in text
    assert "HALF-JOINED EDGE" in text


def test_control_a_pipe_in_a_title_cannot_shift_a_column(tmp_path):
    """Markdown has no arity check, so an unescaped pipe silently shifts a row.

    Planted, because this is not visible by reading: the table still renders,
    every later cell is simply one column to the left. `count_census_states`
    burned a wave on the same class of thing, where the escape is content.
    """
    docs, root = _corpus(tmp_path, {
        "2026-01-01-a-piped-title.md": "# One | two | three\n\nBody.\n",
    })
    text = bai.render(docs, root)

    row = [line for line in text.splitlines()
           if line.startswith("| 2026-01-01 |")]
    assert len(row) == 1, row
    assert "One \\| two \\| three" in row[0]
    # Four columns means five pipes, and the escaped ones must not count.
    unescaped = row[0].replace("\\|", "")
    assert unescaped.count("|") == 5, row[0]


def test_control_a_pair_declared_twice_keeps_both_reasons(tmp_path):
    """MEASURED, NOT IMAGINED: three pairs in the live corpus are declared twice.

    A `dict[(source, target)]` cannot hold two declarations of one pair -- the
    second overwrites the first, with no error. The shipped correction guard
    has that shape, correctly, because it only ever asks whether the pair
    exists. An index inheriting it would print one reason and drop the other,
    which is the precise failure this wave was built against.
    """
    docs, root = _corpus(tmp_path, {
        "2026-01-01-the-claim.md": (
            "# The claim\n"
            "\n"
            "**CORRECTED BY:** `_audit/2026-01-02-the-measurement.md` -- the "
            "first claim was overtaken, and here is why that happened.\n"
            "\n"
            "**CORRECTED BY:** `_audit/2026-01-02-the-measurement.md` -- the "
            "SECOND claim was also overtaken, for an unrelated reason.\n"
        ),
        "2026-01-02-the-measurement.md": (
            "# The measurement\n"
            "\n"
            "**CORRECTS:** `_audit/2026-01-01-the-claim.md` -- both of the "
            "claims above are corrected by this one measurement.\n"
        ),
    })
    joined, _, half_joined, lopsided, _ = bai.edges(docs, root)

    edge = joined[("2026-01-02-the-measurement.md", "2026-01-01-the-claim.md")]
    assert len(edge.corrected_by) == 2, edge.corrected_by
    assert half_joined == [], half_joined
    assert lopsided == [
        ("2026-01-02-the-measurement.md", "2026-01-01-the-claim.md")
    ], lopsided

    text = bai.render(docs, root)
    assert "the first claim was overtaken" in text
    assert "SECOND claim was also overtaken" in text
    assert "LOPSIDED EDGE" in text


def test_control_a_reason_after_a_backticked_symbol_is_printed_in_full(tmp_path):
    """MEASURED: the shipped extractor cuts 65 of 136 reasons in this corpus.

    `guard._reason_on` reads everything after the LAST backtick on the line.
    Plant a marker whose reason quotes a symbol AFTER naming its target -- the
    shape every SHA-citing correction in this corpus has -- and the shipped
    function returns the tail. It is still over 20 characters, so the guard is
    GREEN on it; only a reader notices, and only if they go and look.

    This asserts BOTH halves: that the shipped function really does truncate
    (or this control is proving nothing), and that the index does not.
    """
    line = ("**CORRECTS:** `_audit/2026-01-01-the-claim.md` -- the whole of "
            "this clause sits between the citation and the next backtick, "
            "which is where the shipped extractor loses it; the pinned commit "
            "`b2f5d16` is an ancestor of origin/master after all.")
    docs, root = _corpus(tmp_path, {
        "2026-01-01-the-claim.md": (
            "# The claim\n"
            "\n"
            "**CORRECTED BY:** `_audit/2026-01-02-the-measurement.md` -- "
            "re-measured against a freshly fetched remote on a later day.\n"
        ),
        "2026-01-02-the-measurement.md": "# The measurement\n\n%s\n" % line,
    })

    shipped = guard._reason_on(line)
    mine = bai.reason_on(line)
    assert shipped != mine, "the shipped extractor did not truncate; vacuous"
    assert len(shipped) >= 20, "the guard would have rejected it; vacuous"
    assert mine.endswith(shipped), (mine, shipped)
    assert len(mine) > 2 * len(shipped), (len(mine), len(shipped))

    text = bai.render(docs, root)
    assert "the whole of this clause" in text, "the index printed the fragment"
    assert "TRUNCATED REASON" in text
    assert "| reasons the shipped `_reason_on` cuts short" in text


def test_the_index_is_excluded_from_its_own_corpus():
    """A view of a set placed inside that set makes the scan read its output.

    MEASURED, by the red proof, before the first commit: section 3 quotes the
    four intra-document marker lines VERBATIM, those quoted lines are
    themselves marker-shaped, and with the index in its own corpus the count
    went 4 -> 8 -> 12 on successive regenerations. There is no fixpoint, so
    `--check` could never pass after `--write`. Nothing about reading the code
    suggested it; the harness that copies the tree and runs the real selector
    found it on its first run.
    """
    docs = bai.tracked_documents(ROOT)
    assert bai.INDEX not in docs
    assert all(doc.name != "INDEX.md" for doc in docs), [
        doc.name for doc in docs if doc.name == "INDEX.md"
    ]

    once = bai.build(ROOT)
    twice = bai.build(ROOT)
    assert once == twice, "the generator is not a fixpoint over its own output"


def test_the_generated_index_is_not_read_as_an_audit_document():
    """A DERIVED VIEW OF A CORPUS MUST NOT BE AN INPUT TO INSTRUMENTS THAT
    MEASURE THAT CORPUS -- the law this wave cost two other guards to learn.

    `_audit/INDEX.md` is tracked, so every instrument that sweeps tracked `.md`
    under `_audit` picks it up. It holds every document's title and 65
    correction reasons quoted verbatim, which breaks two different kinds of
    instrument for two different reasons. Both were found by the full suite,
    not by reading, and both are fixed at the instrument's single corpus
    entry point:

    **A RANKER GETS DILUTED.** `find_blocker_reason` ranks documents by how
    well they ARGUE a blocker. The index mentions every blocker-shaped word in
    the repository, so GROUPS-SURFACE's real argument fell from rank 1 to rank
    17 and the recall floor went red.

    **A QUOTE DOES NOT CARRY THE QUOTED DOCUMENT'S MARKS.** One reason quoted
    here says a cell names `linkedin_applied_jobs` "and no such tool exists
    anywhere". The document that wrote that clears the name with a doc-scoped
    mark; the quote leaves the mark behind, so `check_asserted_names_resolve`
    read the index as ASSERTING a tool the corpus was explicitly denying.
    **The index makes no claims; it reports that others did.**

    This asserts both exclusions rather than trusting the comments beside them,
    because a filter with a long comment is exactly what a later cleanup
    deletes.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_asserted_names_resolve as names  # noqa: E402
    import find_blocker_reason as locator  # noqa: E402

    ranked = [rel for rel, _ in locator.corpus()]
    assert "_audit/INDEX.md" not in ranked, (
        "the generated index is being ranked as a document that argues a "
        "blocker; see find_blocker_reason.corpus"
    )
    assert len(ranked) > 50, len(ranked)

    scanned = names.load_corpus(ROOT)
    assert "_audit/INDEX.md" not in scanned, (
        "the generated index is being scanned for asserted names; it quotes "
        "other documents' claims without their marks"
    )
    assert len(scanned) > 50, len(scanned)


def test_the_index_raises_no_candidate_pair_in_the_correction_guard():
    """THE PROPERTY THAT LET THIS WAVE SHIP WITHOUT EDITING THAT GUARD.

    `_audit/INDEX.md` is tracked, so the correction guard's `_documents()`
    scans it like any other document. That guard raises a CANDIDATE PAIR
    whenever its correction vocabulary sits within two lines of a backticked
    `*.md` that resolves -- and this file is nothing but document names beside
    the words CORRECTED and corrects.

    Measured with the links backticked, which was the obvious way to write
    them: **490 resolvable citations, 153 candidate pairs.** Every one would
    have needed a declaration or a hand-written triage entry, in a guard three
    other waves edited the same day, to excuse pairs raised by a file that
    makes no claims at all. An index of a corpus is not a claim about it.

    The remedy was entirely local: link text is not backticked (`_link`), and
    the one quoted title that carried a resolving spelling is defused
    (`defuse`). This asserts the OUTPUT, not the two mechanisms, so a third
    channel nobody thought of is covered by the same line.
    """
    docs = bai.tracked_documents(ROOT)
    text = bai.committed(ROOT)
    assert text, "run: python scripts/build_audit_index.py --write"
    assert bai.resolvable_citations(text, docs, ROOT) == [], (
        "the generated index carries a citation the correction guard resolves;"
        " it will raise candidate pairs against that guard"
    )


def test_control_a_backticked_link_would_raise_candidate_pairs(tmp_path):
    """Planted: prove the defused property is not vacuously true.

    A test asserting "zero citations" over a file that could never contain one
    proves nothing. This re-backticks a link the way it was first written and
    asserts the citation comes straight back, so the zero above is a property
    that was won rather than one that was never at risk.
    """
    docs, root = _corpus(tmp_path, PAIR)
    text = bai.render(docs, root)
    assert bai.resolvable_citations(text, docs, root) == []

    backticked = text.replace("[2026-01-01-the-claim.md](",
                              "[`2026-01-01-the-claim.md`](")
    assert backticked != text, "the substitution did not apply; vacuous"
    assert bai.resolvable_citations(backticked, docs, root) == [
        "2026-01-01-the-claim.md"
    ]


def test_control_defusing_removes_backticks_and_nothing_else(tmp_path):
    """The quoted text must still say what the document says.

    A silent rewrite of quoted prose is the one thing this index cannot do, so
    the transformation is asserted character by character: the output is the
    input with exactly the backticks around a RESOLVING spelling gone, and a
    NON-resolving backticked path is left completely alone.
    """
    docs, root = _corpus(tmp_path, PAIR)
    title = ("the price of giving `2026-01-01-the-claim.md` the column it "
             "does not have, unlike `some-other-repo/notes.md`")
    clean, spellings = bai.defuse(title, docs, root)

    assert spellings == ["2026-01-01-the-claim.md"]
    assert clean == (
        "the price of giving 2026-01-01-the-claim.md the column it "
        "does not have, unlike `some-other-repo/notes.md`"
    )
    assert clean.replace("`", "") == title.replace("`", ""), (
        "defusing changed a character that was not a backtick"
    )


def test_no_blockquoted_marker_names_another_document():
    """THE PRECONDITION THAT MAKES LEAVING THE SHIPPED GUARD ALONE SAFE.

    The shipped anchor's `^\\s*` does not consume `> `, so a marker behind a
    blockquote is invisible to it. This corpus holds four such lines and
    **every one names "this section" or "this document"** -- an intra-document
    correction, a relation that guard has no model for. Widening the anchor
    would therefore gain no cross-document edge and would turn four
    well-intentioned annotations into four malformed reds, because that guard
    requires a marker to name exactly one RESOLVING document.

    So nothing in `tests/` is edited by this wave. What is asserted instead is
    the fact that makes that the right call: ZERO blockquoted markers name
    another document. The day one does, it IS an edge the guard cannot see,
    this goes red, and somebody adjudicates widening the anchor -- rather than
    a correction quietly existing that no reader can reach.
    """
    docs = bai.tracked_documents(ROOT)
    intra, hidden = bai.read_quoted_markers(docs, ROOT)
    assert hidden == [], hidden
    assert intra, (
        "zero blockquoted markers found; either the corpus changed or "
        "QUOTED_MARKER stopped matching -- an empty result here makes the "
        "assertion above vacuous"
    )


def test_every_intra_document_marker_reaches_the_index():
    """Identity, not a pinned count -- the corpus grows every day.

    A fifth self-correction written tomorrow must appear in the index, and
    this says so without going red merely because somebody wrote one.
    """
    docs = bai.tracked_documents(ROOT)
    intra, _ = bai.read_quoted_markers(docs, ROOT)
    text = bai.committed(ROOT)
    assert text, "run: python scripts/build_audit_index.py --write"
    for name, rows in intra.items():
        assert name in text, name
        for _, _, verbatim in rows:
            assert bai._ascii(verbatim) in text, (name, verbatim[:80])


def test_control_a_blockquoted_self_correction_is_surfaced(tmp_path):
    """Planted. The shipped anchor misses it; this index must not."""
    docs, root = _corpus(tmp_path, {
        "2026-01-01-the-claim.md": (
            "# The claim\n"
            "\n"
            "Section 3 reports the gate sweep RED.\n"
            "\n"
            "> **CORRECTED BY: this section.** It was red for an unrelated "
            "reason, and section 3 is not wrong about any row.\n"
        ),
    })
    assert not bai.MARKER.search(
        "> **CORRECTED BY: this section.** It was red"
    ), "the shipped anchor matched a blockquoted line; this control is vacuous"

    intra, hidden = bai.read_quoted_markers(docs, root)
    assert hidden == [], hidden
    assert list(intra) == ["2026-01-01-the-claim.md"], intra

    text = bai.render(docs, root)
    assert "| intra-document correction markers | 1 |" in text
    assert "| distinct declared correction edges | 0 |" in text
    assert "self-corrected x1" in text
    assert "It was red for an unrelated reason" in text


def test_control_a_blockquoted_marker_naming_a_document_is_reported_as_hidden(
        tmp_path):
    """THE DANGEROUS ONE, planted: a real edge the shipped guard cannot see.

    Same syntax as the four benign lines in the corpus, one word different --
    it names a FILE. The guard will never demand the back-pointer, so the
    correction exists, is machine-readable, and the reader who starts at the
    claim still cannot find it. That is the original defect, restored by a
    blockquote.

    It must NOT be folded into the cross-document graph either, because then
    the index would advertise an edge the guard does not enforce and the two
    would disagree silently. Reported, loudly, in its own class.
    """
    docs, root = _corpus(tmp_path, {
        "2026-01-01-the-claim.md": "# The claim\n\nA claim.\n",
        "2026-01-02-the-measurement.md": (
            "# The measurement\n"
            "\n"
            "> **CORRECTED BY:** `_audit/2026-01-01-the-claim.md` -- named "
            "from behind a blockquote, where the anchor cannot reach it.\n"
        ),
    })
    intra, hidden = bai.read_quoted_markers(docs, root)
    assert intra == {}, intra
    assert hidden == [(
        "2026-01-02-the-measurement.md", 3, "2026-01-01-the-claim.md",
        "**CORRECTED BY:** `_audit/2026-01-01-the-claim.md` -- named from "
        "behind a blockquote, where the anchor cannot reach it.",
    )], hidden

    joined, _, _, _, _ = bai.edges(docs, root)
    assert joined == {}, "a hidden marker must not become a graph edge"

    text = bai.render(docs, root)
    assert "| blockquoted markers naming ANOTHER document | 1 |" in text
    assert "HIDDEN CROSS-DOCUMENT CORRECTION" in text


def test_control_the_two_marker_patterns_are_disjoint(tmp_path):
    """A line counted by both would double every self-correction.

    Asserted on the patterns rather than argued from `^\\s*`, because that is
    the kind of reasoning that produced the bug in the first place.
    """
    quoted = "> **CORRECTED BY: this section.** with a reason long enough."
    plain = "**CORRECTED BY:** `x.md` -- with a reason long enough to pass."
    indented = "   CORRECTS: something, with a reason long enough to pass."

    assert bai.QUOTED_MARKER.match(quoted) and not bai.MARKER.search(quoted)
    assert bai.MARKER.search(plain) and not bai.QUOTED_MARKER.match(plain)
    assert bai.MARKER.search(indented)
    assert not bai.QUOTED_MARKER.match(indented)


def test_control_a_heading_inside_a_fence_is_not_a_title(tmp_path):
    """A corpus that quotes markdown at itself will do this sooner or later."""
    docs, root = _corpus(tmp_path, {
        "2026-01-01-fenced-heading.md": (
            "Some preamble before any heading.\n"
            "\n"
            "```\n"
            "# Not the title, an example of one\n"
            "```\n"
            "\n"
            "# The actual title\n"
        ),
    })
    text = bai.render(docs, root)
    assert "The actual title" in text
    assert "Not the title" not in text
