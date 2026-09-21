"""`_audit/RULINGS.md` is derived, and a ruling that leaves the corpus is LOUD.

`_audit/INDEX.md` indexes DOCUMENTS and cannot answer *"what has been ruled
about X"*. `scripts/build_rulings_index.py` answers that, and it is a HYBRID:
the claim and the binding are hand-authored judgment, the location and the
date are derived, and the ANCHOR -- an exact substring of the ruling's own
words -- is what ties the two together.

**THE ANCHOR IS THE ONLY THING STANDING BETWEEN THIS REGISTER AND
`_audit/INSTRUMENTS.md`.** That file is hand-maintained, 9,000 lines, genuinely
excellent, and has no way at all to tell a reader that an entry has gone
stale. This file is the difference. Every control below plants a defect that a
register without an anchor would swallow silently:

  a registered ruling DELETED from the corpus        -> red
  a registered ruling REWORDED                       -> red
  an anchor that matches TWICE                       -> red
  a NEW `RULED:` declaration nobody filed            -> red
  a `NOT_A_RULING` entry that has gone stale         -> red
  an ALIAS that resolves to two rulings              -> red
  the committed file drifting from the derivation    -> red

**AND ONE CONTROL ON THE CONTROLS.** `test_control_the_clean_corpus_is_green`
runs the same harness over a corpus with no defect planted and asserts it
passes. Without it, every red above is satisfied by a checker that always
fails, which is the failure class `_audit/INSTRUMENTS.md` section 50.1 names:
*"a control that has never executed is not a check that cannot fail. It is
worse."*

**NO DEFECT IS PLANTED IN THE LIVE TREE.** Every control builds a synthetic
corpus in `tmp_path`, which is the harness
`tests/test_the_audit_index_is_derived.py` already uses and the discipline
`_audit/INSTRUMENTS.md` states in its preamble -- having also recorded, in the
same file, the day that rule was violated by mutating a module another agent
held uncommitted work in.

Nothing here reaches LinkedIn, an account, or a browser.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_rulings_index as bri  # noqa: E402


# --------------------------------------------------------------------------
# A synthetic corpus, so a red proof never touches a tree other waves write
# --------------------------------------------------------------------------

def _corpus(tmp_path, files: dict):
    """Write `{basename: text}` into `tmp_path/_audit/`, return (docs, root)."""
    audit = tmp_path / "_audit"
    audit.mkdir(exist_ok=True)
    docs = []
    for name, text in files.items():
        path = audit / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        docs.append(path)
    return sorted(docs), tmp_path


#: One document carrying one ruling, spelled the way this corpus spells one --
#: a `RULED:` heading, the ruling hard-wrapped across two lines, and a
#: blockquote, because all three defeated the first version of the resolver.
DOC = "2026-01-01-the-convention.md"
FILES = {
    DOC: (
        "# A convention, ruled\n"
        "\n"
        "## 1. The question\n"
        "\n"
        "Whether a filter written for a class decides the capability.\n"
        "\n"
        "## 2. RULED: NO, and the blocker is named\n"
        "\n"
        "> A denylist substring written to stop a class of addresses is a\n"
        "> general mechanism that happens to catch this one, and the row\n"
        "> stays GAP with its blocker named precisely.\n"
    ),
}

ENTRY = bri.Ruling(
    id="SYNTHETIC-CLASS-FILTER",
    claim="A class filter that catches an address incidentally is a blocker.",
    binds="census state -- boundary-blocked rows",
    document="_audit/" + DOC,
    anchor="general mechanism that happens to catch this one",
    aliases=("the synthetic convention",),
)
REGISTER = (ENTRY,)


def _problems(tmp_path, files, register=REGISTER, triage=None):
    docs, root = _corpus(tmp_path, files)
    return bri.problems_over(register, docs, root, {} if triage is None
                             else triage)


# --------------------------------------------------------------------------
# The control on the controls
# --------------------------------------------------------------------------

def test_control_a_clean_synthetic_corpus_reports_nothing(tmp_path):
    """A checker that always fails satisfies every red proof below.

    This asserts the harness CAN pass, which is the only thing that makes the
    reds mean anything. It is the cheapest test in the file and the one whose
    absence would void all of them.
    """
    assert _problems(tmp_path, FILES) == []


# --------------------------------------------------------------------------
# THE CONTROL THE BRIEF NAMED: a ruling leaves the corpus
# --------------------------------------------------------------------------

def test_control_a_ruling_removed_from_the_corpus_goes_red(tmp_path):
    """Delete the ruling's own words. The register must refuse to stay green.

    This is the whole point of the anchor. A hand-maintained register loses
    this silently: the entry still reads well, still names a document that
    still exists, and says something that is no longer there.
    """
    gutted = {DOC: FILES[DOC].replace(
        "> general mechanism that happens to catch this one, and the row\n", "")}
    found = _problems(tmp_path, gutted)
    assert found, "a deleted ruling produced no complaint"
    assert any("anchor not found" in line for line in found), found
    assert any("SYNTHETIC-CLASS-FILTER" in line for line in found), found


def test_control_a_reworded_ruling_goes_red(tmp_path):
    """Not deleted -- REWORDED. The likelier case, and the quieter one."""
    reworded = {DOC: FILES[DOC].replace("happens to catch this one",
                                        "incidentally catches this one")}
    found = _problems(tmp_path, reworded)
    assert any("anchor not found" in line for line in found), found


def test_control_a_whole_document_vanishing_goes_red(tmp_path):
    """The document is gone, not just the sentence."""
    found = _problems(tmp_path, {"2026-01-02-unrelated.md": "# Unrelated\n"})
    assert any("does not exist" in line for line in found), found


def test_control_an_anchor_matching_twice_goes_red(tmp_path):
    """Two matches means the section it resolves to is a coin toss."""
    doubled = {DOC: FILES[DOC] + (
        "\n## 3. Restated\n\n"
        "It is a general mechanism that happens to catch this one.\n")}
    found = _problems(tmp_path, doubled)
    assert any("matches 2 lines" in line for line in found), found


# --------------------------------------------------------------------------
# The discovery half: a ruling ARRIVING is as important as one leaving
# --------------------------------------------------------------------------

def test_control_a_new_declaration_nobody_filed_goes_red(tmp_path):
    """Somebody rules something and does not register it.

    Without this half the register is a snapshot that silently stops being
    true, which is the failure mode of every hand-maintained list here.
    """
    more = dict(FILES)
    more["2026-01-03-a-later-ruling.md"] = (
        "# A later ruling\n"
        "\n"
        "## 1. The fork\n"
        "\n"
        "**RULED:** the press is permitted and the counter must not move.\n"
    )
    found = _problems(tmp_path, more)
    assert any("UNCLAIMED declaration" in line for line in found), found
    assert any("2026-01-03-a-later-ruling.md" in line for line in found), found


def test_a_declaration_inside_the_registered_section_is_claimed(tmp_path):
    """The positive half: a `RULED:` line the register already covers."""
    assert _problems(tmp_path, FILES) == []
    docs, root = _corpus(tmp_path, FILES)
    ok, _ = bri.resolve(REGISTER, root)
    claimed, _, unclaimed, _ = bri.triage(docs, ok, root, {})
    assert unclaimed == []
    assert [c[3] for c in claimed] == ["SYNTHETIC-CLASS-FILTER"]


def test_control_a_fenced_declaration_is_not_a_declaration(tmp_path):
    """A `RULED:` inside a code fence is an EXAMPLE of one, not one.

    This corpus quotes markdown at itself constantly. `build_audit_index`
    records reading a fenced `# ` as a title as a real defect, and the same
    trap is live for every marker this repository scans for.
    """
    more = dict(FILES)
    more["2026-01-04-an-example.md"] = (
        "# How a ruling is written\n"
        "\n"
        "## 1. The shape\n"
        "\n"
        "Write it like this::\n"
        "\n"
        "```\n"
        "**RULED:** the thing is permitted.\n"
        "```\n"
        "\n"
        "and register it.\n"
    )
    assert _problems(tmp_path, more) == [], \
        "a fenced example was read as a live declaration"


def test_control_prose_ABOUT_the_marker_does_not_become_a_declaration(tmp_path):
    """A document that DISCUSSES rulings must not read as one declaring them.

    **THIS WAVE'S OWN REPORT IS THE WITNESS.** It mentions `RULED:` eighteen
    times and declares nothing, and under the first version of this scan all
    eighteen came back as unfiled rulings. `CORRECTS:` taught this repository
    the same lesson and the correction guard solved it with a line-start
    anchor; that is unavailable here, because a declaration is written
    `## RULED:` and `### 5.4 RULED:` as often as `**RULED:**`.

    The discriminator measured instead: **prose about a marker quotes it, and
    a declaration does not.** Subtracting inline code spans dropped 17 of this
    report's 18 and lost none of the corpus's 24 genuine declarations.
    """
    more = dict(FILES)
    more["2026-01-07-a-discussion.md"] = (
        "# How this corpus writes a ruling\n"
        "\n"
        "## 1. The marker\n"
        "\n"
        "A wave that decides something writes `RULED:` and the verdict on\n"
        "one line. A grep for `RULED:` finds eleven files, and the phrase\n"
        "`**RULED:** the composer` is the commonest shape.\n"
    )
    assert _problems(tmp_path, more) == [], \
        "prose quoting the marker was read as declaring a ruling"


def test_control_the_state_name_is_not_a_declaration(tmp_path):
    """`EXCLUDED-RULED:` ends with the keyword and declares nothing.

    The one false positive in the raw 25 was a census reason cell doing
    exactly this. It was fixed in the PARSER rather than silenced with a
    triage entry, because an entry would hide the class while reading as a
    judgment about that row.
    """
    more = dict(FILES)
    more["2026-01-08-a-census-cell.md"] = (
        "# A slice\n"
        "\n"
        "## 1. Rows\n"
        "\n"
        "| id | capability | state | why |\n"
        "|---|---|---|---|\n"
        "| A25 | Contact info panel | EXCLUDED-RULED: the act is named |\n"
    )
    assert _problems(tmp_path, more) == [], \
        "the state name EXCLUDED-RULED was read as a declaration"


def test_control_the_state_name_guard_is_not_a_blanket_mute(tmp_path):
    """And it must not swallow a real declaration that mentions the state.

    A narrowing that quietly widened would be worse than the false positive
    it removed: this is the half that proves the lookbehind is scoped to the
    hyphenated token and not to the word.
    """
    more = dict(FILES)
    more["2026-01-09-a-real-one.md"] = (
        "# A verdict\n"
        "\n"
        "## 1. The fork\n"
        "\n"
        "**RULED:** the row moves to EXCLUDED-RULED on the act, not the url.\n"
    )
    found = _problems(tmp_path, more)
    assert any("UNCLAIMED declaration" in line for line in found), found


def test_control_a_stale_triage_entry_goes_red(tmp_path):
    """An allowlist nobody re-checks is a silencer.

    The entry claims the scan produces a hit. When it stops producing it, the
    entry is a standing permission for something that is not there, and it
    must fail as loudly as a missing one.
    """
    triage = {("2026-01-09-gone.md", "**RULED:** something"): "a reason"}
    found = _problems(tmp_path, FILES, triage=triage)
    assert any("STALE NOT_A_RULING" in line for line in found), found


def test_control_a_triage_entry_silences_exactly_its_own_hit(tmp_path):
    """And the positive half, so the triage path is not merely untested."""
    more = dict(FILES)
    more["2026-01-05-a-quotation.md"] = (
        "# A quotation\n"
        "\n"
        "## 1. Quoting a ruling made elsewhere\n"
        "\n"
        "> RULED: NO, and the blocker is named -- quoted from the convention.\n"
    )
    triage = {("2026-01-05-a-quotation.md", "quoted from the convention"):
              "A QUOTATION of a ruling registered elsewhere."}
    assert _problems(tmp_path, more, triage=triage) == []
    assert _problems(tmp_path, more) != []


# --------------------------------------------------------------------------
# The register enforces `CANONICAL-RULING-ID` on itself
# --------------------------------------------------------------------------

def test_control_an_alias_resolving_to_two_rulings_goes_red(tmp_path):
    """`CANONICAL-RULING-ID`: a citation resolves to ONE ruling.

    Found for real on this generator's first write -- `section 2` was entered
    as an alias of two different rulings, and because the alias table is built
    from a SET the rows swapped order between runs, so `--write` then
    `--check` disagreed.
    """
    files = dict(FILES)
    files["2026-01-06-another.md"] = (
        "# Another\n\n## 1. Ruled\n\n"
        "The second convention is that a reopener is always named.\n")
    twin = bri.Ruling(
        id="SYNTHETIC-SECOND",
        claim="A reopener is always named.",
        binds="census state -- reopeners",
        document="_audit/2026-01-06-another.md",
        anchor="a reopener is always named",
        aliases=("the synthetic convention",),
    )
    found = _problems(tmp_path, files, register=(ENTRY, twin))
    assert any("AMBIGUOUS ALIAS" in line for line in found), found


def test_control_a_ruled_on_disagreeing_with_the_filename_goes_red(tmp_path):
    """Two dates for one ruling is the supersession question wearing a typo."""
    wrong = bri.Ruling(
        id="SYNTHETIC-CLASS-FILTER",
        claim=ENTRY.claim, binds=ENTRY.binds, document=ENTRY.document,
        anchor=ENTRY.anchor, ruled_on="2025-12-25",
    )
    found = _problems(tmp_path, FILES, register=(wrong,))
    assert any("disagrees with the document's own date" in line
               for line in found), found


# --------------------------------------------------------------------------
# The live corpus
# --------------------------------------------------------------------------

def test_the_committed_register_is_what_the_corpus_derives():
    """THE DRIFT CHECK. Somebody moved a ruling and did not regenerate.

    Repaired with, from the repository root::

        venv/Scripts/python.exe scripts/build_rulings_index.py --write
    """
    committed = bri.committed(bri.ROOT)
    assert committed, "_audit/RULINGS.md does not exist; run --write"
    assert committed == bri.render(bri.ROOT), (
        "_audit/RULINGS.md is stale; regenerate it with --write")


def test_every_registered_ruling_still_resolves_in_the_corpus():
    """The register's whole promise, asserted over the real tree."""
    ok, broken = bri.resolve(bri.REGISTER, bri.ROOT)
    assert broken == [], broken
    assert len(ok) == len(bri.REGISTER)


def test_every_declaration_is_claimed_or_triaged():
    assert bri.problems(bri.ROOT) == []


def test_the_register_is_ascii():
    """Strict ASCII, like every other generated file here."""
    text = bri.committed(bri.ROOT)
    bad = [(n, line) for n, line in enumerate(text.splitlines(), 1)
           if any(ord(c) > 127 for c in line)]
    assert bad == [], bad[:5]


def test_the_register_is_excluded_from_its_own_corpus():
    """A generated view of a set must not sit inside that set.

    Section 5 QUOTES every declaration it found, so an unfiltered scan would
    read its own quotations as fresh declarations and demand they be
    registered -- with no fixpoint, exactly as `build_audit_index` measured
    for the correction markers.
    """
    assert bri.RULINGS.resolve() not in {d.resolve()
                                         for d in bri.corpus(bri.ROOT)}


def test_the_question_that_caused_this_register_is_findable():
    """THE POSITIVE CONTROL, and it is the reason the wave existed.

    *"Does a forbidden substring alone count as a ruling?"* was answered on
    2026-09-05 and RULED in terms on 2026-09-19, and was then escalated as
    undecided by two waves and re-derived by a third. Asking the register in
    the words those waves used must return the ruling that answers it.
    """
    hits = bri.find("does a forbidden substring alone count as a ruling",
                    bri.ROOT)
    ids = [h.ruling.id for h in hits]
    assert "INCIDENTAL-CAPTURE-IS-NOT-A-RULING" in ids, ids
    assert "EXCLUDED-RULED-ADMISSION" in ids, ids
    assert ids[:2] == ["EXCLUDED-RULED-ADMISSION",
                       "INCIDENTAL-CAPTURE-IS-NOT-A-RULING"], (
        "the two rulings that answer the question must rank first; got %s"
        % ids[:4])
