"""Generate `_audit/RULINGS.md`: one entry per RULING, not per document.

THE GAP THIS ANSWERS, measured 2026-09-21. `_audit/INDEX.md` indexes
DOCUMENTS. It answers *"what did wave X report"* and *"what overtook this
claim"*, and it answers both well. It cannot answer **"what has been ruled
about X"**, and that question is the one the corpus keeps failing.

THE RECEIPT IS FOUR PAYMENTS FOR ONE ANSWER. *"Does a forbidden substring
alone count as a ruling?"* was answered on 2026-09-05
(`2026-09-05-decide-retire-rulings.md` section 2) and ruled again in terms on
2026-09-19 (`2026-09-19-two-census-conventions-ruled.md` section 3, *"RULED:
NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY."*). Two waves then
escalated it to the lead as undecided, and the lead re-derived it a third time
at 08:40 on 2026-09-21. The correction that caught this --
`2026-09-21-the-open-queue.md` section 5.4a -- **found the 2026-09-05 answer
and missed the 2026-09-19 one**, which is the defect convicting itself: the
document written to diagnose unfindability was also searching by memory.

## What is DERIVED and what is JUDGED, stated first because it is the honest limit

**A ruling's one-line claim cannot be extracted mechanically and this file does
not pretend otherwise.** Measured over the 208 tracked audit documents: a
`RULED:` grep finds 11 files; a heading mentioning a ruling finds 97, of which
only 10 also carry `RULED:`; 157 files match at least one of fourteen ruling
signals. The 2026-09-05 answer above is phrased as a QUOTED LEDGER RULE inside
a section titled *"THE BOUNDARY IS NOT A REASON"* and matches none of the
declaration markers. There is no regex over this corpus whose hits are rulings.

So the register is a HYBRID, and each half is labelled:

  JUDGED (hand-authored, in `REGISTER` below)
    id       the canonical id, per the 2026-09-19 ruling that every ruling has
             exactly one and that citations resolve to a SYMBOL
    claim    one line a stranger can match against a question
    binds    the capability class, address family, census state or verb
    aliases  the other names this same ruling wears, KEPT not deleted --
             2026-09-19 section 1: *"they are how existing readers find the
             rule, and deleting them would strand every document that uses
             one. They are mapped, and the map is the artifact."*
    anchor   an exact substring of the ruling's OWN WORDS

  DERIVED (computed from the corpus at the SHA this runs against)
    where    the document, and THE SECTION HEADING the anchor sits under
    when     the `YYYY-MM-DD` the document's basename opens with
    resolves whether the anchor is present EXACTLY ONCE

**THE ANCHOR IS THE LOAD-BEARING PART.** It is what makes a hand-authored
register non-rotting: an entry whose ruling was edited away, moved to another
document, or reworded stops resolving and `--check` goes red. A register
without that is `_audit/INSTRUMENTS.md`, which is hand-maintained, excellent,
9,000 lines long, and has no way at all to tell you an entry has gone stale.

**NO LINE NUMBERS ARE PRINTED, AND THAT IS A RULING THIS FILE OBEYS RATHER
THAN A STYLE CHOICE.** `2026-09-19-two-census-conventions-ruled.md` section 1:
*"every citation of it resolves to the SYMBOL, never to a line number and
never to a re-derived phrase"*, because this repo measured six retirements
citing a `server.py` line range that had since become a different function --
*"a reader who opens it finds a plausible unrelated answer rather than an
error."* The section heading is the symbol here.

## The discovery half, and WHY IT IS DELIBERATELY NARROW

A register nobody adds to is a register that silently stops being true. So
`--check` also SCANS the corpus for ruling DECLARATIONS and requires each one
to be either claimed by an entry or triaged onto `NOT_A_RULING` with a written
reason. A new ruling landing in the corpus then fails this check until
somebody files it.

**The scan is `RULED:` and nothing else.** Measured: 25 hit lines, 24 of them
genuine ruling declarations -- the highest precision of the fourteen signals
tried, and the only one whose full hit set can be closed by hand today. It is
the corpus's own emerging marker.

**IT HAS LOW RECALL AND THIS FILE SAYS SO OUT LOUD, EVERY RUN.** Scoping a
gate to a name and letting it imply completeness is the half-truth this repo
has already ruled against: a scoped gate *"may not claim more than it ran"*.
So `render()` prints an UNSCANNED table with the count of every signal the
discovery half does NOT read, and `--check` repeats it. A ruling written in
another dialect -- and the one that triggered this wave is exactly that -- will
NOT be caught by the scan. It has to be entered by hand, and the register is
where the judgment lives regardless.

## Why a sibling script rather than an extension of `build_audit_index.py`

Three reasons, and the first is the index's own stated constraint.

1. `build_audit_index.py` says *"Nothing here restates a number it did not
   derive -- that rule is the whole reason the file can be trusted a month
   from now."* This register is half hand-authored by necessity. Putting a
   judged half inside a file whose trust rests on having no judged half would
   spend the index's guarantee to buy this one.
2. **The two go red for different reasons.** `INDEX.md` drifts when a DOCUMENT
   is added; `RULINGS.md` drifts when a RULING is added, moved or reworded.
   Coupling them makes every new document touch the rulings check and every
   new ruling touch the document check, and a check that fires for reasons
   unrelated to its subject gets regenerated without being read.
3. `tests/test_the_audit_index_is_derived.py` re-derives `INDEX.md` line for
   line. That assertion is only meaningful over fully derived content.

**What IS shared is shared.** `tracked_documents`, `date_of`, `_unfenced`,
`_cell` and `_ascii` are IMPORTED from `build_audit_index`, not reimplemented.
Each of those paid for a defect -- the git-tracked corpus (a gitignored
`_scratch/` made a check pass locally and fail in a clone), the fence skip (a
`#` inside a fence is an example of a heading, not one), the pipe escape (a
pipe in a cell shifts every later column silently), the codepoint spell-out (a
silently stripped character makes a subtly different line that still looks
fine). Rewriting any of them here is how two waves shipped broken parsers in
one day.

Nothing here reaches LinkedIn, an account, or a browser. It reads committed
markdown and nothing else.
"""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_audit_index as bai  # noqa: E402

ROOT = bai.ROOT
RULINGS = ROOT / "_audit" / "RULINGS.md"

#: The declaration marker, with the two exclusions its own subject matter
#: forced. Position is NOT constrained: this corpus writes a declaration as
#: `**RULED:**`, as `## RULED:`, as `### 5.4 RULED:` and as `> RULED:`, and
#: anchoring at line start -- the rule the correction guard uses -- drops four
#: of the twenty-four genuine ones. So the keyword carries the precision, and
#: two things are subtracted from the line before it is applied.
#:
#: **(1) INLINE CODE SPANS.** `CORRECTS:` taught this repository that a
#: sentence DESCRIBING a marker is not one, and the correction guard solved it
#: with a line-start anchor. That solution is unavailable here, and the
#: problem is identical -- **measured on this wave's own report, which
#: mentions `RULED:` eighteen times while declaring nothing**. Every one of
#: those is written inside backticks, because prose about a marker quotes it
#: and a declaration does not. Subtracting code spans drops 17 of the 18 and
#: **loses none of the 24 genuine declarations**.
#:
#: **(2) THE STATE NAME `EXCLUDED-RULED`.** A census reason cell can end a
#: sentence with the state and a colon, and the keyword falls inside the
#: state's own name. That is the single false positive in the raw scan --
#: `_audit/_census/profile.md` row `P A25` -- and a lookbehind removes it
#: exactly, without a triage entry standing in for a parser bug.
#:
#: Measured over the tracked corpus: raw 25 hits / 11 files, of which 1 is a
#: false positive; this rule 24 / 10, of which 0 are.
DECLARATION = re.compile(r"(?<!EXCLUDED-)RULED:")

#: An inline code span. Subtracted before `DECLARATION` is applied -- see (1).
INLINE_CODE = re.compile(r"`[^`\n]*`")


def declares(line: str) -> bool:
    """Does this line DECLARE a ruling, as opposed to mentioning one."""
    return DECLARATION.search(INLINE_CODE.sub(" ", line)) is not None

#: An ATX heading OUTSIDE a fence. `(preamble)` covers hits above the first.
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
PREAMBLE = "(preamble)"

#: A leading blockquote marker is MARKUP, not content, and is stripped before
#: an anchor is matched -- the same call the fence skip makes about ``` .
#: **THIS IS NOT COSMETIC.** Rulings in this corpus are very often QUOTED,
#: out of a code comment or a sibling document, and a quoted ruling wraps
#: with a `>` opening each continuation line. Left in, the flattened text
#: reads `... all need > their own url ...` and every anchor spanning a wrap
#: inside a quote silently fails to resolve -- which would look exactly like
#: the ruling having been removed. Measured: it defeated
#: `GROUPS-ADDRESS-BUYS-NO-WRITE` on the second run of this generator.
BLOCKQUOTE = re.compile(r"^\s*(?:>\s?)+")


@dataclasses.dataclass(frozen=True)
class Ruling:
    """One ruling. `claim`, `binds` and `aliases` are JUDGED; the rest resolves."""

    id: str
    claim: str
    binds: str
    document: str
    anchor: str
    aliases: tuple = ()
    status: str = "STANDING"
    note: str = ""
    #: Only for a document whose basename carries no `YYYY-MM-DD` prefix --
    #: the census slices, which are living files rather than dated reports.
    #: JUDGED, not derived, and marked `~` wherever it is printed so no
    #: reader mistakes it for the filename's own date. Where the filename
    #: DOES carry a date and this disagrees with it, `resolve()` reports a
    #: failure rather than silently preferring either: two dates for one
    #: ruling is the supersession question wearing a typo.
    ruled_on: str = ""


# --------------------------------------------------------------------------
# THE REGISTER -- hand-authored. Every `claim` is a paraphrase written to be
# MATCHED AGAINST A QUESTION; the `anchor` is the ruling's own words and is
# what the check resolves. Where a ruling's own sentence is already short and
# quotable the two coincide, which is the best case.
# --------------------------------------------------------------------------

REGISTER: tuple = (

    # ---------------------------------------------------------------- census
    Ruling(
        id="EXCLUDED-RULED-ADMISSION",
        claim="A row is EXCLUDED-RULED only on one of FOUR written grounds: a "
              "forbidden-substring entry, a writes.PERMANENTLY_FORBIDDEN key, "
              "a WriteSpec refusing in its own words, or an audit passage "
              "measuring the capability unreachable. Anything a general "
              "mechanism merely happens to block is GAP with a NAMED BLOCKER.",
        binds="census state -- the bar for EXCLUDED-RULED on every slice",
        document="_audit/_census/network.md",
        anchor="Everything a general mechanism merely happens to block",
        # `THE BOUNDARY IS NOT A REASON` was here too, and the register's own
        # ambiguity check refused it: that phrase is the SECTION TITLE of the
        # 2026-09-05 document, which is a distinct, later ruling APPLYING this
        # one. Two rulings cannot share a name. It belongs to the applier.
        aliases=("the ledger's own rule", "L118-123",
                 "the census's own rule", "a GAP with a NAMED BLOCKER"),
        # The slice's own first line reads *"Written 2026-09-03"*, and its
        # first commit is the same day (`61d3816`). Taken from the document
        # rather than from git, because git records when a file LANDED and
        # this is a claim about when the rule was WRITTEN.
        ruled_on="2026-09-03",
        note="Written twice, once per slice, in near-identical words; "
             "`_audit/_census/profile.md` carries the twin. This is the "
             "ORIGIN of the forbidden-substring question and it already "
             "answers it: a substring entry counts only when it is one of the "
             "four WRITTEN grounds, i.e. when it was aimed at the capability.",
    ),
    Ruling(
        id="INCIDENTAL-CAPTURE-IS-NOT-A-RULING",
        claim="A denylist substring written for a CLASS of addresses that "
              "catches this capability incidentally is a BLOCKER, not a "
              "decision. Those rows stay GAP with the blocker named. A rule "
              "naming the ACT is EXCLUDED-RULED; a filter catching the "
              "ADDRESS is GAP; an address measured UNREACHABLE is neither.",
        binds="census state -- every boundary-blocked row on all four slices",
        document="_audit/2026-09-19-two-census-conventions-ruled.md",
        anchor="RULED: NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY.",
        aliases=("incidental capture", "FORBIDDEN-CLASS-FIX-LANDED",
                 "the class-filter convention",
                 "two-census-conventions section 3"),
        note="THIS IS THE ANSWER TWO WAVES ESCALATED AS UNDECIDED AND A THIRD "
             "RE-DERIVED. It carries the three-way GENERAL FORM table that "
             "the 2026-09-21 re-derivation reconstructed from measurement. "
             "Its own citation is the 2026-09-03 ledger passage, so the chain "
             "is: census rule -> ledger asks -> 09-05 applies -> 09-19 RULES "
             "-> 09-21 re-derives.",
    ),
    Ruling(
        id="BOUNDARY-IS-NOT-A-REASON",
        claim="A capability's address being refused today is nearly worthless "
              "as evidence for retiring it; eleven of twelve retirement "
              "families meet only the default-closed allowlist, which decided "
              "nothing about them in particular, so no ruling may cite a "
              "no-pattern refusal as its reason.",
        binds="verb -- what may be cited as the ground of a retirement",
        document="_audit/2026-09-05-decide-retire-rulings.md",
        anchor="No ruling below cites a NO-PATTERN refusal as its reason.",
        aliases=("decide-retire-rulings section 2",
                 "THE BOUNDARY IS NOT A REASON"),
        note="The application of EXCLUDED-RULED-ADMISSION that section 5.4a "
             "found. It quotes the census rule rather than restating it.",
    ),
    Ruling(
        id="CANONICAL-RULING-ID",
        claim="Every ruling has ONE canonical id and every citation resolves "
              "to a SYMBOL, never to a line number and never to a re-derived "
              "phrase. Aliases are mapped, not deleted. A bare prose reason "
              "is not a citation and may not carry a verdict alone.",
        binds="verb -- how any ruling is cited anywhere in this corpus",
        document="_audit/2026-09-19-two-census-conventions-ruled.md",
        anchor="Every ruling has ONE canonical id, and every citation of it "
               "resolves to the",
        aliases=("two-census-conventions section 1", "one canonical id"),
        note="THIS FILE IS THAT RULING'S ARTIFACT. It is why the register "
             "prints a section heading and never a line number, and why the "
             "aliases column exists at all.",
    ),
    Ruling(
        id="CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE",
        claim="A container's exclusion reaches a control ON it only when the "
              "container was excluded as UNREACHABLE. An exclusion of the "
              "container's own ACT does not propagate to reading its "
              "contents. Either way the content row must CITE the container "
              "row, so a reopener on the container reaches the content.",
        binds="census state -- inherited exclusions, container to content",
        document="_audit/2026-09-19-two-census-conventions-ruled.md",
        anchor="Unreachable propagates. Unwanted does not.",
        aliases=("two-census-conventions section 2", "P I12 -> J99",
                 "container and content"),
        note="Built ON `P I12` as a SOUND exclusion: *zero of 237 urls reach "
             "one* is ground four of EXCLUDED-RULED-ADMISSION. Two later "
             "documents call `P I12` a miscategorisation; see the register's "
             "DISPUTED note in the report for this wave.",
    ),
    Ruling(
        id="DUPLICATE-ROW-IS-MARKED-NEVER-DELETED",
        claim="When two census rows describe one capability the duplicate "
              "STAYS in the file, marked as a duplicate and naming the row it "
              "duplicates. It is not removed and its id is never reused.",
        binds="census state -- every cross-slice re-file and de-duplication",
        document="_audit/2026-09-20-the-deduplication-ruling.md",
        anchor="the duplicate **stays in the file**",
        aliases=("the deduplication ruling",
                 "OWNED-BY-A-SIBLING-SLICE"),
    ),
    Ruling(
        id="COMPOUND-ROW-SPLITS-ONLY-ON-STATE",
        claim="When ONE census row describes TWO capabilities it is SPLIT "
              "only if the halves require different STATES. A DIRECTION "
              "divergence is repaired in the cell as `R+W`, never by a "
              "split. Two verbs, two surfaces, two addresses and mere "
              "verbosity are not grounds. A row whose halves share a state "
              "today but would not once a pending ruling is applied carries "
              "a written TRIGGER instead of being split now.",
        binds="census state -- every row whose capability names two acts",
        document="_audit/2026-09-21-the-compound-rows.md",
        anchor="SPLIT a compound row if and only if its halves require "
               "DIFFERENT STATES.",
        aliases=("the compound rows", "split or leave whole",
                 "P L2 -> L2 + L2b", "two capabilities one row",
                 "the write-partition's section 4.4.2 question"),
        note="THE EXACT COMPLEMENT OF `DUPLICATE-ROW-IS-MARKED-NEVER-DELETED` "
             "above -- that one governs two rows describing one capability, "
             "this one governs one row describing two. They were filed "
             "together for that reason. The asymmetry it rests on is "
             "MEASURED rather than argued: `reader_closable_blockers."
             "DIRECTIONS` normalises four spellings of a both-DIRECTION onto "
             "`R+W`, while `count_census_states.classify` answers a "
             "two-STATE cell by silently taking the first by textual order "
             "or by dropping the row out of the census, raising no dialect "
             "either way. Direction can be told the truth in the cell; state "
             "cannot. The corpus had already decided this eight times "
             "without naming it -- seven non-splits (`P M6` `P M9` `P M11` "
             "`M M28` `M C47` `N 125`, plus `J 71` declining in writing) and "
             "the one split, `P L2` -> `L2` + `L2b`, whose halves are BOTH "
             "reads and which therefore refutes a direction-based rule.",
    ),

    # ----------------------------------------------------------- write scope
    Ruling(
        id="NO-IRREVERSIBLE-WRITE-IS-FIRED",
        status="AMENDED",
        claim="AMENDED 2026-09-23 by WRITE-CLASS-B: irreversible writes MAY "
              "now be fired, but ONLY at a target the operator names -- the "
              "consent-per-act half below still binds. Original: "
              "No irreversible write is fired at a real target -- not an "
              "application, a post, an invitation, a message or a comment. "
              "Permission to BUILD a capability is not consent to perform a "
              "specific act against a specific person. Writes may be "
              "designed, gated, tested against fixtures and left ready.",
        binds="capability class -- every write in the server, standing",
        document="_audit/2026-09-05-lead-rulings-round-two.md",
        anchor="No irreversible write is fired at a real target.",
        aliases=("the line I did not cross", "the standing order",
                 "the operator gate"),
        note="The single widest write ruling in the corpus. It separates "
             "BUILD from FIRE, which is the distinction most re-escalations "
             "about writes collapse.",
    ),
    Ruling(
        id="STANDING-SHAPE-OF-A-WRITE-RULING",
        claim="Every new write gets the SAME bar the twelve shipped writes "
              "meet: design, WriteSpec, gate, consent text, tests against "
              "fixtures and synthetic targets, two calls behind a single-use "
              "action-bound target-bound token with a 120s TTL. Do not invent "
              "a stricter bar for a new capability, and do not weaken it.",
        binds="capability class -- the admission shape for any new write",
        document="_audit/2026-09-05-lead-rulings-round-two.md",
        anchor="Do not invent a bar stricter than that for a new capability.",
        aliases=("lead-rulings-round-two section 8", "the standing shape",
                 "safety is a property of the code"),
    ),
    Ruling(
        id="GROUPS-ADDRESS-BUYS-NO-WRITE",
        claim="Admitting a group address buys nothing for joining, leaving, "
              "posting, commenting or inviting. Each needs its own url, its "
              "own write sanction and its own ruling, so those rows stay GAP "
              "and no boundary change moves them. The price is three things "
              "and an admission pays one.",
        binds="capability class -- groups writes, and any address widening",
        document="_audit/2026-09-19-groups-admission.md",
        anchor="NO WRITE IS BOUGHT BY THIS. Joining, leaving, posting and "
               "inviting all need",
        aliases=("N 163 re-cost", "DECIDE not MEASURE",
                 "the groups eight"),
        note="Stated in `readonly.py`'s own comment and quoted here. The "
             "companion rule that a widening is reported by what it BANKS "
             "rather than by what it UNBLOCKS sits in the same section.",
    ),
    Ruling(
        id="SCROLL-NOT-SANCTIONED",
        claim="Infinite scroll is NOT sanctioned. Correct paging already "
              "reaches what it would buy, so the objection is SUFFICIENCY "
              "rather than safety. Three named conditions reopen it.",
        binds="verb -- scrolling as a page-interaction technique",
        document="_audit/2026-09-05-the-scroll-ruling.md",
        anchor="The ruling: NO, and revisit only on evidence",
        aliases=("SCROLL", "section 7 of lead-rulings-round-two"),
    ),
    Ruling(
        id="DISCLOSING-PRESS-PERMITTED",
        claim="Pressing a control that DISCLOSES content on a page already "
              "admitted is PERMITTED, under four conditions that must all "
              "hold: the page is admitted, the control matches an enumerated "
              "disclosure shape by attribute, the press is shown not to move "
              "an outward counter, and it is closed with the closure "
              "verified.",
        binds="verb -- pressing a control, disclosure only",
        document="_audit/2026-09-19-the-disclosing-press-ruling.md",
        anchor="RULED: PERMITTED, under four conditions that must ALL hold",
        aliases=("the disclosing press", "press.disclose",
                 "ANALYTICS-CONTROLS-UNPRESSED", "MATCH-DETAILS-COLLAPSED"),
    ),
    Ruling(
        id="MENTION-COMPOSITION-RULING",
        claim="Build the mention MECHANISM, forbid the SOURCE: composing a "
              "mention is permitted as a mechanism, and harvesting the "
              "candidate list it would mention from is not.",
        binds="capability class -- mentions in posts and comments",
        document="_audit/2026-09-05-lead-rulings-round-two.md",
        anchor="`MENTION-COMPOSITION-RULING` -- BUILD THE MECHANISM, FORBID "
               "THE SOURCE",
        aliases=("blocker 16", "M C10", "M C28"),
    ),
    Ruling(
        id="FEED-CONTENT-READ-RULING",
        claim="AMENDED 2026-09-24 by NAMES-AT-RUNTIME for what a read RETURNS "
              "at runtime (what is STORED is unchanged). Feed content may be "
              "read as COUNTS AND RELATIONS ONLY, never text or names.",
        binds="capability class -- reads of feed and post content",
        document="_audit/2026-09-05-lead-rulings-round-two.md",
        anchor="`FEED-CONTENT-READ-RULING` -- COUNTS AND RELATIONS ONLY",
        aliases=("blocker 49", "M C43", "M C74", "counts and relations only"),
        note="The ground `M C85`'s read half would rest on if that row were "
             "ever split -- see OPEN-QUESTIONS.",
    ),
    Ruling(
        id="MESSAGING-SETTINGS-CAPABILITY-LEVEL",
        claim="The settings-family ruling is CAPABILITY-level, not "
              "path-level: a setting is admitted BY NAME or not at all, which "
              "excludes every page below the settings index whatever its URL "
              "spelling. It says 'a setting', not 'a profile setting'.",
        binds="capability class -- every persisted account preference",
        document="_audit/2026-09-05-decide-retire-rulings.md",
        anchor="The settings-family ruling is capability-level, not "
               "path-level.",
        aliases=("R11", "MESSAGING-SETTINGS", "3.10", "settings family",
                 "server.py::linkedin_update_setting"),
        note="The ruling CANONICAL-RULING-ID was written about: one sentence "
             "wearing three names across three slices. Its census twin is "
             "`_audit/_census/profile.md`.",
    ),

    # --------------------------------------------------- boundary and probes
    Ruling(
        id="SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS",
        claim="The search-results admission is APPROVED IN PRINCIPLE under "
              "five binding conditions, one of which is that nothing is FIRED "
              "from that surface. Condition 1's name-free shaper AMENDED "
              "2026-09-24 by NAMES-AT-RUNTIME for runtime returns.",
        binds="address family -- /search/results/",
        document="_audit/2026-09-19-two-census-conventions-ruled.md",
        anchor="RULED: APPROVED IN PRINCIPLE. FIVE CONDITIONS, ALL BINDING.",
        aliases=("the search admission", "condition 5"),
        note="Condition 2 was AMENDED the same day -- see "
             "SEARCH-CONDITION-2-CLOSED. The ruling bars FIRING, not READING; "
             "conflating the two cost a later wave a decision it did not "
             "need.",
    ),
    Ruling(
        id="SEARCH-CONDITION-2-CLOSED",
        claim="Condition 2 of the search admission demands CLOSED PATH "
              "SEGMENTS, not a NARROW ANCHORED pattern. Anchoring was "
              "measured to do none of the work assigned to it.",
        binds="address family -- the shape of any allowlist pattern",
        document="_audit/2026-09-19-search-admission-condition-2-amended.md",
        anchor="CONDITION 2 IS AMENDED: **CLOSED**, NOT **ANCHORED**",
        aliases=("condition 2 amended",),
        status="AMENDS SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS",
    ),
    Ruling(
        id="MUST-STAY-REFUSED-ENTRIES-COME-OUT",
        claim="`MUST_STAY_REFUSED` listing `groups` and `events` is wrong and "
              "must come out, or move to a class the admission does not "
              "reach.",
        binds="address family -- the guard's must-stay-refused table",
        document="_audit/2026-09-19-search-admission-condition-2-amended.md",
        anchor="RULED: those entries come out",
        aliases=("the guard contradiction",),
    ),
    Ruling(
        id="PROBE-MUST-NOT-TRY-REFUSED-VALUES",
        claim="The check stands and the probe must not try refused values.",
        binds="verb -- what a probe may submit while measuring a boundary",
        document="_audit/2026-09-19-two-census-conventions-ruled.md",
        anchor="RULED: THE CHECK STANDS. THE PROBE MUST NOT TRY REFUSED "
               "VALUES.",
        aliases=(),
    ),
    Ruling(
        id="GATE-IS-SAFE-AND-BLIND",
        claim="The gate is SAFE and BLIND, and those are different "
              "properties: condition 4 cannot witness disclosure.",
        binds="capability class -- the disclosure witness on a press gate",
        document="_audit/2026-09-19-two-census-conventions-ruled.md",
        anchor="RULED: the gate is SAFE and BLIND, and those are different "
               "properties.",
        aliases=("DEFECT ONE",),
    ),
    Ruling(
        id="GRAIN-FOLLOWS-WHAT-THE-PLATFORM-DRAWS",
        claim="The grain of an enumeration follows what the PLATFORM draws, "
              "not what a reader finds convenient to count.",
        binds="census state -- how capabilities are enumerated",
        document="_audit/2026-09-19-two-census-conventions-ruled.md",
        anchor="RULED: THE GRAIN FOLLOWS WHAT THE PLATFORM DRAWS",
        aliases=(),
    ),
    Ruling(
        id="REDACTION-FORK-CLOSED-VOCABULARY",
        claim="The redaction fork is ruled: a CLOSED VOCABULARY.",
        binds="verb -- how a redacted value is spelled anywhere in output",
        document="_audit/2026-09-03-linkedin-gap-blockers.md",
        anchor="THE REDACTION FORK IS RULED: A CLOSED VOCABULARY",
        aliases=("A9",),
    ),
    Ruling(
        id="CENSUS-OUTRANKS-LEDGER",
        claim="Where the census and the ledger disagree the CENSUS is right; "
              "the ledger's `1R` is the error.",
        binds="census state -- precedence between the census and the ledger",
        document="_audit/2026-09-19-the-three-ruling-requests-ruled.md",
        anchor="RULED: THE CENSUS IS RIGHT. THE LEDGER'S `1R` IS THE ERROR.",
        aliases=("request 4",),
    ),
    Ruling(
        id="POSITIONAL-DIALECT-SHIP-THE-DETECTOR",
        claim="Ship the detector; do not rewrite the 69 cells.",
        binds="census state -- the positional-dialect cells",
        document="_audit/2026-09-20-the-pointer-graph.md",
        anchor="RULED: ship the detector. Do not rewrite the 69 cells.",
        aliases=("the positional dialect",),
    ),

    # ------------------------------------------- the 2026-08-31 write bench
    Ruling(
        id="COMPOSER-IS-THE-REFUSAL-NOT-THE-ADDRESS",
        claim="For publishing a post the composer is the wall, not the "
              "address.",
        binds="capability class -- publish a post",
        document="_audit/2026-08-31-linkedin-finish.md",
        anchor="**RULED:** the composer",
        aliases=("#1 publish a post", "linkedin_publish_post"),
    ),
    Ruling(
        id="PERMALINK-READ-IS-ALLOWED",
        claim="`/feed/update/<urn>/` is allowed and an ordinary read of a "
              "post at its permalink is permitted; reacting rests on the same "
              "permalink ruling.",
        binds="address family -- /feed/update/<urn>/",
        document="_audit/2026-08-31-linkedin-finish.md",
        anchor="**RULED:** `/feed/update/<urn>/` is allowed",
        aliases=("#2 comment on an item", "#3 react to an item",
                 "the permalink ruling"),
        note="`M C42` records that this ruling DID NOT REACH naming the "
             "target -- which is why that row cannot rest on it. See the "
             "DISPUTED section of `_audit/2026-09-21-what-was-ruled.md`.",
    ),
    Ruling(
        id="PROFILE-EDITOR-ADDRESSES-ALLOWED",
        claim="`/in/<member>/edit/` and the profile editors are allowed.",
        binds="address family -- the profile editor surfaces",
        document="_audit/2026-08-31-linkedin-finish.md",
        anchor="**RULED:** `/in/<member>/edit/`",
        aliases=("#4 edit a profile field",),
    ),
    Ruling(
        id="ONE-NAMED-SETTINGS-PAGE-AT-A-TIME",
        claim="ONE NAMED settings page below `/mypreferences/d/` is admitted, "
              "one at a time.",
        binds="address family -- /mypreferences/d/",
        document="_audit/2026-08-31-linkedin-finish.md",
        anchor="**RULED:** ONE NAMED settings page",
        aliases=("#6 change a setting", "dark mode"),
    ),
    Ruling(
        id="INVITATION-TARGETING-IS-CALL-TIME",
        claim="Targeting an invitation is allowed as a CALL-TIME "
              "responsibility.",
        binds="capability class -- send a connection invitation",
        document="_audit/2026-08-31-linkedin-finish.md",
        anchor="**RULED:** targeting is allowed as a CALL-TI",
        aliases=("#7 send a connection invitation",),
    ),
    Ruling(
        id="DO-NOT-OPEN-MESSAGING",
        status="SUPERSEDED",
        claim="SUPERSEDED 2026-09-23 by WRITE-CLASS-B: the operator ruled that "
              "messaging MAY be opened. Original: "
              "Do not open messaging. Opening it opens a surface whose cost "
              "lands on other people, and the row is DEFERRED BY RULING.",
        binds="address family -- /messaging/",
        document="_audit/2026-08-31-linkedin-finish.md",
        anchor="**RULED: do not open messaging.**",
        aliases=("#9 send a message / InMail", "R9", "linkedin_send_message"),
    ),

    # ------------------------------------------------- the five requests set
    Ruling(
        id="MAP-CONVENTION-AT-HEAD-MEMBERSHIP",
        claim="The blocker map records at-HEAD membership, plus a `RE_FILED` "
              "marker.",
        binds="census state -- what the blocker map means by membership",
        document="_audit/2026-09-19-the-five-requests-ruled.md",
        anchor="RULED: at-HEAD membership, plus `RE_FILED`",
        aliases=("request A",),
    ),
    Ruling(
        id="N61-REMOVED-FROM-HASHTAG-EXISTENCE",
        claim="`N 61` is removed from `HASHTAG-EXISTENCE`.",
        binds="census state -- one row's blocker assignment",
        document="_audit/2026-09-19-the-five-requests-ruled.md",
        anchor="RULED: removed",
        aliases=("request B",),
    ),
    Ruling(
        id="CONVERSATION-OVERFLOW-BOTH-WAVES-RIGHT",
        claim="On `CONVERSATION-OVERFLOW-MENU` both waves are right, about "
              "different things -- eight rows are forced and the chosen set "
              "stays empty.",
        binds="census state -- CONVERSATION-OVERFLOW-MENU",
        document="_audit/2026-09-19-the-five-requests-ruled.md",
        anchor="RULED: both waves are right, about different things",
        aliases=("request C", "request 1"),
    ),
    Ruling(
        id="PUBLISHED-SPLIT-REPORT-NOW-GATE-LATER",
        claim="The published-split check REPORTS now and GATES once the "
              "deliberate over-runs are declared.",
        binds="verb -- when a reporting check becomes a blocking gate",
        document="_audit/2026-09-19-the-five-requests-ruled.md",
        anchor="RULED: report now, gate once the deliberate over-runs are "
               "declared",
        aliases=("request D",),
    ),
    Ruling(
        id="CREATOR-HUB-AND-POST-COMMENT-LEDGER-OVERCOUNTS",
        claim="For `CREATOR-HUB-SURFACE` and `POST-COMMENT-CONTROLS` the "
              "LEDGER OVER-COUNTS.",
        binds="census state -- two blocker row counts",
        document="_audit/2026-09-19-the-five-requests-ruled.md",
        anchor="RULED: LEDGER OVER-COUNTS",
        aliases=("request E",),
    ),
    # REGISTERED BY THE WAVE THAT MADE IT, and that is why the entry exists
    # rather than the code comments citing a document title. Twenty sites fed
    # `ExtractionFailedError.url`, `server._error` publishes it with no
    # scrubber, and the question a later reader will ask is "what has been
    # ruled about that field" -- which is the one question `_audit/INDEX.md`
    # cannot answer and this register was written for.
    Ruling(
        id="ERROR-URL-ASKED-FOR-OR-NOTHING",
        claim="The error envelope's url field carries the address this server "
              "ASKED FOR, or nothing at all. A landing is never published "
              "there; where a requested address exists in scope publishing it "
              "is REQUIRED rather than merely permitted, and where none "
              "exists the key is omitted and the landing is DESCRIBED in the "
              "hint. A descriptor never goes into the url field.",
        binds="verb -- what ExtractionFailedError.url may carry, per site",
        document="_audit/2026-09-21-the-field-beside-the-message.md",
        anchor="carries the address this server ASKED FOR, or it carries "
               "nothing at all",
        aliases=("the field beside the message", "the twenty sites",
                 "ERROR-URL-PER-SITE"),
        note="THE FAILURE-PATH COUNTERPART OF THE `source_url` SPLIT RULING "
             "in `tests/test_the_source_url_split_was_never_ruled.py`, which "
             "is NOT registered here because it lives as a test rather than "
             "as an audit passage. Same kind of value -- the address a read "
             "landed on -- in several of the SAME functions, and the two were "
             "ruled by different files that did not know about each other: "
             "`linkedin_my_profile` was declared SHAPED on its success path "
             "and published its landing raw on its failure path, in one "
             "function, for weeks. That ruling supplied the METHOD used here "
             "(a per-site declaration with a written reason, a count per "
             "site, a relay pinned as a relay, and drift failing in BOTH "
             "directions) and its prohibition is what stopped this wave "
             "wrapping all twenty: *wrapping a deliberate publication is as "
             "much a defect as leaking an accidental one.* The count each "
             "way is 12 withheld, 7 published, 1 relay.",
    ),
    # THE FIELD ITSELF, RULED THE DAY AFTER THE FIELD BESIDE IT. Registered
    # next to its sibling on purpose: a reader who arrives asking about the
    # error envelope wants both, and they answer different halves.
    Ruling(
        id="ERROR-MESSAGE-RULED-AT-THE-RAISE",
        claim="What the error envelope's message may carry is decided WHERE "
              "THE VALUE ENTERS THE EXCEPTION, never where it leaves. The "
              "provenance classes are not classes of exception -- a page "
              "value inside a stdlib ValueError is indistinguishable at "
              "server._error from one that is not -- so no per-class policy "
              "may live at the envelope. The package's own exception text and "
              "a library's own exception text are PUBLISHABLE; a value the "
              "PAGE chose is FORBIDDEN inside any exception, whoever authored "
              "the class.",
        binds="verb -- what server._error may publish in $.message, and where "
              "that is decided",
        document="_audit/2026-09-21-what-the-browser-said.md",
        anchor="decided WHERE THE\nVALUE ENTERS THE EXCEPTION, never where it "
               "leaves",
        aliases=("what the browser said", "$.message", "the 89 sub-expressions",
                 "third-party exception text", "ERROR-MESSAGE-PROVENANCE"),
        note="THE SIBLING OF `ERROR-URL-ASKED-FOR-OR-NOTHING`, and it goes the "
             "OTHER WAY for a stated reason rather than by temperament. The "
             "url field could be ruled PER SITE because every value feeding it "
             "is an address this package composed or read; `$.message` cannot, "
             "because `_error` holds only `type(exc)` and `str(exc)` and the "
             "provenance of what that text QUOTES is not among them. So the "
             "ruling moves the decision to the raise, which is where the "
             "corpus had already put it three times without naming it: "
             "`coerce.py`, `press.disclose` and `landing.py`. It also DECLINES "
             "the sibling's own recommendation to make the twelve `dom.py` "
             "messages type-only -- all twelve are inside "
             "`tests/test_readers_emit_no_page_string.py`'s driven subject set "
             "and green (4 clean, 8 returns_text, 0 not_driven), so the "
             "payload class is already closed for them and type-only would "
             "delete twelve diagnoses to close a channel no needle travels. "
             "What it SHIPPED is the other end of the pipe: "
             "`tests/test_tool_envelopes_emit_no_page_string.py`, because the "
             "reader guard discovers only `async def` functions taking a "
             "`page` and the 48 tool bodies that funnel into `_error` are "
             "therefore outside it, permanently.",
    ),

    # ------------------------------ 2026-09-23: write class (b), live budget,
    # and the calls the operator delegated to the orchestrator
    Ruling(
        id="LIVE-BUDGET-40-LOADS",
        claim="A live session may use up to 40 LinkedIn page loads, serial, "
              "at least 20 seconds apart -- a ceiling, not a target; one "
              "browser driver at a time.",
        binds="live lanes -- page loads per session",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor='verbatim "go, 40 loads is fine")',
        note="Operator's words: \"go, 40 loads is fine\". Raised from 15 per "
             "wave, to feed one live lane from several offline build lanes.",
    ),
    Ruling(
        id="OUTWARD-ACTS-NEED-THE-OPERATOR",
        claim="Only acts toward other people, or irreversible ones, need the "
              "operator. Every other call -- search keywords, self-only "
              "presses, his own notification state, allowlist and press-gate "
              "defaults -- is the orchestrator's, on evidence, recorded here "
              "and overridable.",
        binds="decision routing -- what is escalated to the operator",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (operator, 2026-09-23 18:13) Only actions that act as "
               "the operator",
    ),
    Ruling(
        id="WRITE-CLASS-B",
        claim="The package may CONNECT, MESSAGE, APPLY, POST and OPEN "
              "MESSAGING on the operator's account, behind the single-use "
              "grant model and off by default. Lifts the read-only rule, the "
              "apply/connect/InMail cut and DO-NOT-OPEN-MESSAGING.",
        binds="capability class -- outward writes and opening messaging",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor='RULED: (operator, 2026-09-23 18:15, verbatim "b") The package '
               'may CONNECT,',
        aliases=("ruling (b)", "the write class (b)"),
        note="Operator's word: \"b\". Supersedes DO-NOT-OPEN-MESSAGING and "
             "amends NO-IRREVERSIBLE-WRITE-IS-FIRED; its target condition is "
             "OPERATOR-NAMES-THE-TARGET.",
    ),
    Ruling(
        id="OPERATOR-NAMES-THE-TARGET",
        claim="A live proof of an outward act fires ONLY at a target the "
              "operator names -- whom to connect with or message, which job to "
              "apply to, what to post. Never a real person or job chosen by "
              "the package or an agent.",
        binds="live proofs -- every outward write",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (operator, 2026-09-23 18:15, same ruling) A live proof "
               "of an outward",
    ),
    Ruling(
        id="VIEW-SWITCH-PRESS-RESTORED",
        claim="A press that changes which rows a view shows is permitted if "
              "the view is RESTORED afterwards and a before/after reading "
              "proves it.",
        binds="press gate -- sort and filter controls",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-23, delegated) VIEW-SWITCH "
               "PRESSES are",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable.",
    ),
    Ruling(
        id="D1-SEARCH-AS-READS",
        claim="Search keywords and LinkedIn-written facets are permitted as "
              "reads: values from tool arguments only, never an identifying "
              "value of the operator, at most 5 test searches per session.",
        binds="read boundary -- search keywords and facets",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-23, delegated) D1, SEARCH "
               "KEYWORDS AND",
        aliases=("D1",),
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable.",
    ),
    Ruling(
        id="NOTIFICATIONS-UNREAD-SPEND",
        claim="Loading /notifications/ is PERMITTED: it only clears the "
              "operator's own unread badge. Answers the question N 20 and "
              "N 45 were held on.",
        binds="address family -- /notifications/",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-23, delegated) Loading "
               "/notifications/ is",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Registered under the id the census holds used "
             "for the open question, so the holds resolve to the answer.",
    ),
    Ruling(
        id="OWN-INBOX-READS-COVERED-BY-B",
        claim="Reading the operator's own inbox, including opening threads, "
              "is covered by ruling (b) with no per-fire go-ahead; proofs "
              "prefer threads already read so no new read receipt is sent.",
        binds="live proofs -- /messaging/ reads",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-23, applying (b)) Reading the "
               "operator",
    ),
    Ruling(
        id="IN-ME-NO-BLANKET-BAR",
        claim="/in/me/ presses get no blanket sensitivity-basis bar; each "
              "control is judged on evidence like any other press.",
        binds="press gate -- /in/me/ controls",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-23, delegated) /in/me/ presses "
               "get NO blanket",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable.",
    ),
    Ruling(
        id="SELF-PROFILE-EDITS-NOT-OUTWARD",
        claim="Edits to the operator's own profile fields are not outward "
              "acts: no other person is targeted and each edit reverses. "
              "Live proofs are permitted with notify-network off, the field "
              "restored in-session and proven by a before/after reading, and "
              "never a field that broadcasts by nature.",
        binds="live proofs -- edits to the operator's own profile fields",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-23, delegated) EDITS TO THE "
               "OPERATOR'S OWN",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Narrows OPERATOR-NAMES-THE-TARGET to writes that "
             "target other people.",
    ),
    Ruling(
        id="OTHER-MEMBER-IDS-AS-READS",
        claim="Another member's id in a search facet (e.g. connectionOf) is "
              "permitted as a read when it comes from the tool's arguments, "
              "never from page content, and is never stored in a tracked "
              "file.",
        binds="read boundary -- search facets carrying another member's id",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-23, delegated) OTHER MEMBERS' "
               "IDS IN SEARCH",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Answers the other-members question N 172 was "
             "held on.",
    ),
    Ruling(
        id="D4-NO-OWN-BROWSER-CONTEXT",
        claim="The package does not create its own browser context; it "
              "attaches to the operator's signed-in browser. P C8's download "
              "transport goes through DevTools download behaviour on the "
              "attached browser, which creates no context.",
        binds="session model -- browser contexts",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) D4 IS ANSWERED NO",
        aliases=("D4",),
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Question: _audit/2026-09-21-the-read-triage.md D4.",
    ),
    Ruling(
        id="D6-CAPABILITY-OVER-AFFORDANCE",
        claim="A row named for an affordance is discharged when the package "
              "delivers the same capability payload by its own sanctioned "
              "routes; the row names them and rests on their proofs (PROVEN "
              "if live-proven, else UNFIRED).",
        binds="census convention -- rows named for a control or surface",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) D6 IS ANSWERED YES",
        aliases=("D6",),
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Question: _audit/2026-09-21-the-read-triage.md D6. "
             "Governs N 132 and J 107.",
    ),
    Ruling(
        id="REVEAL-BUTTON-IS-A-DISCLOSURE",
        claim="A plain button that only reveals content (e.g. 'Show more "
              "analytics') is pressed as a disclosure, with before/after "
              "readings proving it revealed content and changed no state.",
        binds="press gate -- reveal-only buttons",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) A PLAIN BUTTON "
               "THAT ONLY",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable.",
    ),
    Ruling(
        id="SHARE-AND-POLL-PROOFS-OWN-POSTS",
        claim="Share-link proofs use the operator's own posts only (M C72); a "
              "poll post's address (M C85) comes from tool arguments only -- "
              "his own poll post, or NEEDS-TARGET.",
        binds="live proofs -- share links and poll results",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) SHARE-LINK PROOFS "
               "USE THE",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable.",
    ),
    Ruling(
        id="CREDENTIAL-SETTINGS-NEED-THE-OPERATOR",
        claim="Credential, recovery and session settings -- the seven "
              "credential/recovery controls and P N10 (sign out of sessions, "
              "which ends this server's own session) -- are never live-proven "
              "unless the operator names them.",
        binds="live proofs -- account security settings",
        document="_audit/2026-09-23-rulings-write-class-and-delegated-calls.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) CREDENTIAL, "
               "RECOVERY AND SESSION",
        note="The cannot-be-undone arm of OUTWARD-ACTS-NEED-THE-OPERATOR.",
    ),
    Ruling(
        id="D2-SEARCH-VERTICALS-WIDENED",
        claim="The search admission widens from people to four CLOSED "
              "segments, /search/results/(people|companies|groups|events)/, "
              "under D1-SEARCH-AS-READS's three conditions; serves N 104, "
              "N 161, M C70 and N 179.",
        binds="read boundary -- search result verticals",
        document="_audit/2026-09-24-rulings-search-verticals-rosters-passive-"
                 "costs.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) D2 IS ANSWERED YES",
        aliases=("D2",),
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Question: _audit/2026-09-21-the-read-triage.md D2.",
    ),
    Ruling(
        id="D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING",
        claim="A refusal written only into an allowlist comment is not a "
              "ruling: it makes no row EXCLUDED-RULED or CANNOT-DELIVER, and "
              "a row resting on one is GAP, blocked on the decision the "
              "refusal asks for, until that decision is registered.",
        binds="census convention -- refusals recorded only beside an "
              "allowlist entry",
        document="_audit/2026-09-24-rulings-search-verticals-rosters-passive-"
                 "costs.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) D3 IS ANSWERED NO",
        aliases=("D3",),
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Question: _audit/2026-09-21-the-read-triage.md D3. "
             "Governs N 99, N 177 and N 178.",
    ),
    Ruling(
        id="MEMBER-ROSTERS-AS-BOUNDED-READS",
        claim="A roster the operator can open himself (a group's members, an "
              "event's attendees, a company's or school's People tab) is "
              "admitted as a bounded read: one page per call, the id from "
              "tool arguments only, no automatic pagination, no member name "
              "or id in a tracked file, inside the live budget.",
        binds="read boundary -- member rosters",
        document="_audit/2026-09-24-rulings-search-verticals-rosters-passive-"
                 "costs.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) MEMBER ROSTERS "
               "ARE ADMITTED AS",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Decides the roster question the 2026-09-05 "
             "refusal recorded in readonly.py and census cells but never "
             "registered (D3). Rows it held: N 165, N 188, N 189, J 108, "
             "N 102, N 99, N 177.",
    ),
    Ruling(
        id="D5-PASSIVE-COST-IS-NOT-A-ROW",
        claim="A consequence of an act with no control of its own is recorded "
              "on the act's row, and its own row is EXCLUDED-RULED as "
              "NOT-AN-ACT (N 171). A preference he sets is an act, a setting, "
              "and stays a GAP write row (N 183).",
        binds="census convention -- passive costs",
        document="_audit/2026-09-24-rulings-search-verticals-rosters-passive-"
                 "costs.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) D5 IS ANSWERED",
        aliases=("D5",),
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Question: _audit/2026-09-21-the-read-triage.md D5.",
    ),
    Ruling(
        id="SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED",
        claim="Amends condition 1 of SELF-PROFILE-EDITS-NOT-OUTWARD: where the "
              "edit dialog draws no notify control, his account-level 'Share "
              "profile updates with your network' setting read OFF before the "
              "edit satisfies it; an unnamed switch blocks until a capture "
              "names it; neither established -> NEEDS-OPERATOR.",
        binds="live proofs -- edits to the operator's own profile fields",
        document="_audit/2026-09-24-rulings-notify-veto-and-who-which.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) CONDITION 1 OF",
        status="AMENDS SELF-PROFILE-EDITS-NOT-OUTWARD",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Measured cause: the intro editor draws no named "
             "notify control (live lane session 1, lane L7).",
    ),
    Ruling(
        id="PAGE-MAY-VETO-NEVER-SUPPLY",
        claim="Every navigation address is composed from tool arguments; page "
              "content may only REFUSE a navigation (e.g. a caller-supplied id "
              "that is not his own), never provide the address.",
        binds="navigation -- addresses and page content",
        document="_audit/2026-09-24-rulings-notify-veto-and-who-which.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) A PAGE MAY VETO A "
               "NAVIGATION,",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Reconciles the navigation guard with ownership "
             "checks; first applied to linkedin_surface_census feed_item.",
    ),
    Ruling(
        id="THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET",
        claim="A third party's profile (/in/<slug>/) may be loaded only inside "
              "an outward act whose target the operator names in that call: "
              "slug from tool arguments only, never for a measurement, the "
              "shaper name-free. Search-admission condition 5 stands.",
        binds="read boundary -- third-party profiles inside outward acts",
        document="_audit/2026-09-24-rulings-notify-veto-and-who-which.md",
        anchor="RULED: (orchestrator, 2026-09-24, applying (b)) A THIRD PARTY'S "
               "PROFILE",
        note="The orchestrator applying WRITE-CLASS-B and "
             "OPERATOR-NAMES-THE-TARGET; overridable. Unblocks N 1, N 4, N 5, "
             "M M1 and M M6 as builds.",
    ),
    Ruling(
        id="WHO-WHICH-COUNTS-ARE-NOT-DELIVERY",
        claim="A row whose payload is WHO (people) or WHICH (items of other "
              "people's content) is not delivered by a count-only reader: GAP. "
              "Filters and aggregates are delivered by counts. The operator "
              "answered the names-and-titles question 2026-09-24 "
              "(NAMES-AT-RUNTIME): such rows now wait on a name-returning "
              "reader, not on the doctrine.",
        binds="census convention -- count-only readers",
        document="_audit/2026-09-24-rulings-notify-veto-and-who-which.md",
        anchor="RULED: (orchestrator, 2026-09-24, delegated) A ROW WHOSE PAYLOAD "
               "IS WHO (a",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Precedent: N 162 and N 180.",
    ),
    Ruling(
        id="NAMES-AT-RUNTIME",
        claim="A read whose capability is people, or which items of other "
              "people's content, RETURNS them as its result -- names, and "
              "group and event titles -- with the risks mitigated at runtime. "
              "What is stored is unchanged: no third party's name in a "
              "tracked file.",
        binds="read results -- people, groups and events",
        document="_audit/2026-09-24-rulings-names-at-runtime.md",
        anchor="RULED: (operator, 2026-09-24 08:11, verbatim) \"It's not about "
               "returning",
        aliases=("names at runtime",),
        note="The operator's ruling, verbatim in its document. Amends the "
             "2026-09-05 name-free doctrine for runtime returns; answers "
             "WHO-WHICH-COUNTS-ARE-NOT-DELIVERY's question.",
    ),
    Ruling(
        id="PEOPLE-DATA-MITIGATIONS",
        claim="People data is returned under six mitigations, each enforced by "
              "code and a test: declared fields only; sanitised and marked "
              "untrusted; never stored; bounded to one page per call; visible "
              "only (no de-anonymising); never a target by itself.",
        binds="read results -- people, groups and events",
        document="_audit/2026-09-24-rulings-names-at-runtime.md",
        anchor="RULED: (orchestrator, 2026-09-24, applying NAMES-AT-RUNTIME) "
               "PEOPLE DATA IS",
        note="Orchestrator's call applying the operator's ruling; overridable.",
    ),
    Ruling(
        id="OUTWARD-CLASSES-BUILT-BEHIND-GRANTS",
        claim="Repost or share, endorse or recommend, and delete or withdraw "
              "one of his own items are BUILT behind the single-use grant, off "
              "by default, fired only at a target he names. PERMANENTLY_"
              "FORBIDDEN keeps only entries whose grounds are mitigations.",
        binds="writes -- the classes ruling (b) did not name",
        document="_audit/2026-09-24-rulings-names-at-runtime.md",
        anchor="RULED: (orchestrator, 2026-09-24, applying the operator's 08:11 "
               "principle)",
        note="Orchestrator's call applying the operator's 08:11 principle and "
             "OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.",
    ),
)


# --------------------------------------------------------------------------
# Triage for declaration hits that are NOT a ruling being made here.
#
# AN ENTRY HERE IS A CLAIM AND IS ITSELF CHECKED, the discipline
# `NOT_A_CORRECTION` already keeps: it asserts that the scan DOES produce this
# hit and that, having read the line, it is something other than a ruling
# declaration. A STALE ENTRY -- one for a hit the scan no longer produces --
# FAILS AS LOUDLY AS A MISSING ONE, because an allowlist nobody re-checks is a
# silencer and this file would then be the thing it exists to catch.
#
# The key is (document basename, a distinctive ASCII-folded substring of the
# line). Not a line number: a line number is exactly the citation form
# CANONICAL-RULING-ID rules out, and it would rot on any edit above it.
# --------------------------------------------------------------------------

NOT_A_RULING: dict = {

    # `_audit/_census/profile.md` row `P A25` WAS an entry here -- the one
    # false positive in the raw 25, where a reason cell ends a clause with the
    # STATE NAME `EXCLUDED-RULED` and a colon. It was REMOVED when
    # `DECLARATION` grew its lookbehind. **A triage entry standing in for a
    # parser bug is the wrong artifact**: it silences one instance and leaves
    # the class live for every future cell written the same way, while
    # reading, forever after, as a considered judgment about that row.

    ("2026-09-19-the-four-absent-blockers.md", "> RULED: THE CENSUS IS RIGHT"): (
        "A QUOTATION OF A RULING MADE ELSEWHERE, marked as one by its "
        "blockquote. The ruling is CENSUS-OUTRANKS-LEDGER, declared in "
        "`_audit/2026-09-19-the-three-ruling-requests-ruled.md` and registered "
        "under that id. Registering the quotation too would give one ruling "
        "two entries, which is precisely what CANONICAL-RULING-ID forbids."
    ),

    ("2026-08-31-linkedin-finish.md", "**RULED:** same permalink ruling."): (
        "THE SAME RULING APPLIED TO A SECOND ROW, and the line says so in "
        "those words. `#3 react to an item` is decided by the permalink "
        "ruling declared two rows earlier under `#2 comment on an item`, "
        "registered as `PERMALINK-READ-IS-ALLOWED`. Giving it its own entry "
        "would put one ruling in the register twice under two ids, which is "
        "what `CANONICAL-RULING-ID` exists to stop. **This is the shape a "
        "register must get right or it manufactures rulings**: an APPLICATION "
        "of a ruling to a new row looks identical to a new ruling, and only "
        "reading the line separates them."
    ),

    ("2026-09-21-what-was-ruled.md",
     "RULED: NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY."): (
        "TWO QUOTATIONS OF `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` IN THE REPORT "
        "THAT BUILT THIS REGISTER -- once as a blockquote of the ruling under "
        "question Q1, once inside sample `--find` output. Neither decides "
        "anything. **Recorded rather than reworded, because this pair is the "
        "discovery half's only live demonstration**: the document was "
        "untracked while the register was being built, `--check` was green, "
        "and the instant it was staged the scan refused to stay green until "
        "somebody accounted for it. That is the whole mechanism, on a real "
        "document, and deleting the evidence to tidy the register would spend "
        "it."
    ),

    ("2026-09-21-the-open-queue.md", "RULED: NO. THEY STAY"): (
        "A THIRD QUOTATION OF `INCIDENTAL-CAPTURE-IS-NOT-A-RULING`, in section "
        "5.4b -- the correction that exists BECAUSE that ruling was missed. "
        "The lead's 5.4a claimed the question had been re-derived three times "
        "and named only the 2026-09-03 origin; 5.4b cites the 2026-09-19 "
        "ruling it had overlooked, which is the one that says `RULED:` in a "
        "file named `...-ruled.md`. Registering the citation would put that "
        "ruling in the register a second time, which `CANONICAL-RULING-ID` "
        "forbids. **The entry is worth reading for what it records rather "
        "than what it silences**: this register was merged and, within "
        "minutes, refused the very document written to explain why the "
        "corpus could not be searched -- the instrument convicting its own "
        "commissioner on its first working day."
    ),

    ("2026-09-21-the-open-queue.md", "RULED: incidental capture is not a ruling"): (
        "A RE-DERIVATION, NOT A NEW RULING, and its own document says so. "
        "Section 5.4a: *'5.4 below presents itself as a new ruling. It is not "
        "one ... The ruling stands; the attribution in 5.4 is wrong.'* The "
        "ruling is INCIDENTAL-CAPTURE-IS-NOT-A-RULING, declared 2026-09-19. "
        "Filing 5.4 as an entry would record a fourth payment as a fourth "
        "ruling, which is the defect this register was built to end. The "
        "MEASUREMENTS in 5.4 -- the three-way discriminator and the "
        "anchor-termination finding -- are new and are good; they are "
        "evidence under the existing ruling, not a new one."
    ),
}


# --------------------------------------------------------------------------
# Corpus mechanics
# --------------------------------------------------------------------------

def fold(text: str) -> str:
    """ASCII-fold, so a pure-ASCII anchor matches a corpus em dash or quote.

    This corpus is strict-ASCII by rule and NOT by fact: `build_audit_index`
    ships a `TRANSLITERATE` table precisely because committed titles type an
    em dash where the house spelling is `--`. An anchor written in the house
    spelling must still match the document it names, so both sides are folded
    through the SHIPPED table rather than a second one written here.
    """
    return bai._ascii(text)


def flatten(lines):
    """`(flat_text, line_of)` -- the document ASCII-folded onto ONE line.

    **AN ANCHOR MUST BE ALLOWED TO WRAP, BECAUSE EVERY RULING IN THIS CORPUS
    DOES.** The prose hard-wraps at about 78 columns, so a ruling's own
    sentence is almost never on one physical line. A single-line matcher
    forces anchors short enough to fit inside a wrap -- which makes them less
    distinctive exactly when distinctiveness is what stops an entry pointing
    at the wrong passage. Measured on the first run of this generator: 3 of 34
    anchors failed for this reason alone and NONE of the three rulings had
    changed.

    `line_of[i]` is the 1-based source line that character `i` came from, so a
    match over the flattened text still resolves to a section. Lines are
    joined with a single space, which is what `paragraph_at` already does
    upstream and what `test_joining_a_paragraph_changes_no_word` asserts
    changes no word.
    """
    parts, line_of = [], []
    for number, line in enumerate(lines, 1):
        piece = " ".join(fold(BLOCKQUOTE.sub("", line)).split())
        if parts:
            parts.append(" ")
            line_of.append(number)
        parts.append(piece)
        line_of.extend([number] * len(piece))
    return "".join(parts), line_of


def sections(lines) -> list:
    """`(heading, start, end)` for every ATX heading, 1-based, fence-aware.

    A heading inside a fenced block is an EXAMPLE of a heading, not one --
    this corpus quotes markdown at itself constantly, and `build_audit_index`
    records that reading a fenced `# ` as a title was a real defect. The
    fence state is tracked over the raw lines rather than filtered out,
    because the line NUMBERS have to survive for the containment test below.
    """
    out = []
    inside = False
    opened = 1
    label = PREAMBLE
    for number, line in enumerate(lines, 1):
        if bai.FENCE.match(line.strip()):
            inside = not inside
            continue
        if inside:
            continue
        found = HEADING.match(line.rstrip("\n"))
        if found:
            out.append((label, opened, number - 1))
            label = found.group(2).strip()
            opened = number
    out.append((label, opened, len(lines)))
    return out


def section_of(secs, number: int) -> str:
    for label, start, end in secs:
        if start <= number <= end:
            return label
    return PREAMBLE


@dataclasses.dataclass(frozen=True)
class Resolved:
    ruling: Ruling
    date: str
    section: str
    start: int
    end: int
    hits: int


def resolve(register, root: pathlib.Path):
    """Resolve every entry's anchor against the corpus. Returns (ok, broken).

    `broken` carries a SENTENCE per failure rather than a code, because the
    caller prints it to somebody who has to fix it. Three failure kinds are
    distinguished and they need different fixes: a missing document (the
    ruling moved or the path is wrong), a missing anchor (the ruling was
    reworded or deleted -- THE CASE THIS REGISTER EXISTS TO CATCH), and an
    ambiguous anchor (it matches twice, so the section it resolves to is a
    coin toss and the entry has to be made more specific).
    """
    ok, broken = [], []
    for entry in register:
        path = root / entry.document
        if not path.is_file():
            broken.append("%s: document %s does not exist"
                          % (entry.id, entry.document))
            continue
        lines = path.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines()
        flat, line_of = flatten(lines)
        needle = " ".join(fold(entry.anchor).split())
        found, at = [], flat.find(needle)
        while at != -1:
            found.append(line_of[at])
            at = flat.find(needle, at + 1)
        if not found:
            broken.append(
                "%s: anchor not found in %s -- the ruling was reworded, moved "
                "or removed. Anchor: %r"
                % (entry.id, entry.document, entry.anchor[:80]))
            continue
        if len(found) > 1:
            broken.append(
                "%s: anchor matches %d lines in %s; it must identify ONE. "
                "Anchor: %r"
                % (entry.id, len(found), entry.document, entry.anchor[:80]))
            continue
        secs = sections(lines)
        label = section_of(secs, found[0])
        start, end = next((s, e) for lb, s, e in secs
                          if s <= found[0] <= e and lb == label)
        date = bai.date_of(path)
        if date == bai.UNDATED and entry.ruled_on:
            date = "~" + entry.ruled_on
        elif date != bai.UNDATED and entry.ruled_on and entry.ruled_on != date:
            broken.append(
                "%s: ruled_on %s disagrees with the document's own date %s "
                "-- one ruling cannot have two dates; drop ruled_on or fix it"
                % (entry.id, entry.ruled_on, date))
            continue
        ok.append(Resolved(entry, date, label, start, end, 1))
    return ok, broken


def declarations(documents, root: pathlib.Path) -> list:
    """Every `RULED:` line outside a fence, as `(document, lineno, text)`."""
    out = []
    for doc in documents:
        lines = doc.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines()
        inside = False
        for number, line in enumerate(lines, 1):
            if bai.FENCE.match(line.strip()):
                inside = not inside
                continue
            if inside:
                continue
            if declares(line):
                out.append((doc, number, line.strip()))
    return out


def triage(documents, resolved, root: pathlib.Path, not_a_ruling=None):
    """Split declaration hits into claimed / triaged / UNCLAIMED, + stale keys.

    A hit is CLAIMED when it falls inside the SECTION a register entry
    resolved to. Containment rather than a key, because a section is what a
    ruling actually occupies and it survives every edit that does not move the
    ruling out of its own section -- where a line-number key rots on any edit
    above it and a text key rots on any rewording, including a rewording that
    changes nothing.
    """
    table = NOT_A_RULING if not_a_ruling is None else not_a_ruling
    owned = {}
    for item in resolved:
        owned.setdefault(item.ruling.document, []).append(item)

    claimed, triaged, unclaimed = [], [], []
    used = set()
    for doc, number, text in declarations(documents, root):
        rel = doc.relative_to(root).as_posix()
        mine = [i for i in owned.get(rel, []) if i.start <= number <= i.end]
        if mine:
            claimed.append((rel, number, text, mine[0].ruling.id))
            continue
        key = next((k for k in table
                    if k[0] == doc.name and fold(k[1]) in fold(text)), None)
        if key is not None:
            used.add(key)
            triaged.append((rel, number, text, key))
            continue
        unclaimed.append((rel, number, text))
    stale = sorted(set(table) - used)
    return claimed, triaged, unclaimed, stale


def unscanned(documents) -> list:
    """What the discovery half does NOT read, counted, for the printed table.

    A SCOPED CHECK MAY NOT CLAIM MORE THAN IT RAN. These counts are the
    register's own NOT CHECKED line: every one of them is a place a ruling can
    be written that `RULED:` will never see, and the ruling that caused this
    wave was written in the first of them.
    """
    wider = (
        ("a heading naming a ruling",
         re.compile(r"^#{1,6} .*\b(RULED|RULING|RULINGS|Ruled|Ruling|ruled|"
                    r"ruling|rulings)\b")),
        ("a bold line opening on RULING/RULED",
         re.compile(r"^\*\*.*\b(RULED|RULING|RULINGS)\b")),
        ("the phrase THE RULING", re.compile(r"\bTHE RULING\b")),
        ("a named -RULING id", re.compile(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+"
                                          r"-RULING\b")),
        ("the phrase standing ruling", re.compile(r"(?i)\bstanding ruling\b")),
        ("a lead or operator ruling in prose",
         re.compile(r"(?i)\b(the lead ruled|lead's ruling|the operator ruled|"
                    r"operator's ruling|the lead has ruled)\b")),
    )
    rows = []
    for label, pattern in wider:
        files, hits = set(), 0
        for doc in documents:
            text = doc.read_text(encoding="utf-8").replace("\r\n", "\n")
            found = sum(1 for line in bai._unfenced(text.splitlines())
                        if pattern.search(line))
            if found:
                files.add(doc)
                hits += found
        rows.append((label, len(files), hits))
    return rows


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def _link(document: str) -> str:
    return "[%s](%s)" % (document.replace("_audit/", ""),
                         document.replace("_audit/", ""))


def corpus(root: pathlib.Path = ROOT) -> list:
    """The tracked audit documents, MINUS this register's own output.

    **A GENERATED VIEW OF A SET MUST NOT SIT INSIDE THAT SET.**
    `build_audit_index` records measuring exactly this: with its own output in
    scope its marker count went 4 -> 8 -> 12 on successive regenerations and
    `--check` could never pass after `--write`. The same trap is live here and
    is worse, because section 5 of this register QUOTES every `RULED:` line it
    found -- so an unfiltered scan would read its own quotations as fresh
    declarations and demand they be registered, forever.
    """
    return [d for d in bai.tracked_documents(root)
            if d.resolve() != RULINGS.resolve()]


def render(root: pathlib.Path = ROOT) -> str:
    return render_over(REGISTER, corpus(root), root, NOT_A_RULING)


def render_over(register, documents, root: pathlib.Path,
                not_a_ruling=None) -> str:
    """The whole file, as a pure function of (register, corpus).

    Split out from `render` so a red proof can drive it over a SYNTHETIC
    corpus in a tmp dir -- no git, and no mutation of a tree other waves
    write. That is the harness `tests/test_the_audit_index_is_derived.py`
    already uses and the discipline `_audit/INSTRUMENTS.md` states in its
    preamble, having also recorded the day that rule was violated.
    """
    table = NOT_A_RULING if not_a_ruling is None else not_a_ruling
    ok, broken = resolve(register, root)
    claimed, triaged, unclaimed, stale = triage(documents, ok, root, table)

    out = []
    add = out.append
    add("# THE RULINGS REGISTER -- one entry per RULING, not per document")
    add("")
    add("**GENERATED. Do not hand-edit.** `scripts/build_rulings_index.py "
        "--write` rebuilds it; `--check` fails when it drifts, when a "
        "registered ruling stops resolving in the corpus, or when a `RULED:` "
        "declaration is neither claimed nor triaged.")
    add("")
    add("`_audit/INDEX.md` answers *what did wave X report* and *what "
        "overtook this claim*. It cannot answer **what has been ruled about "
        "X**, and this file is that key. The receipt for why it exists is "
        "four payments for one answer -- see "
        "`_audit/2026-09-21-what-was-ruled.md`.")
    add("")
    add("**WHERE and WHEN are DERIVED** from the corpus at the SHA this runs "
        "against; **CLAIM, BINDS and ALIASES are JUDGED** and hand-authored. "
        "Section headings are printed and line numbers are not, because "
        "`CANONICAL-RULING-ID` rules that a citation resolves to a symbol.")
    add("")
    add("**THIS REGISTER IS NOT THE CORPUS AND DOES NOT CLAIM TO BE "
        "COMPLETE.** Read section 4 before concluding a question is "
        "unruled: the scan that keeps it honest reads ONE marker, and the "
        "ruling that caused this file to be written does not carry it.")
    add("")
    add("    rulings registered       %d" % len(ok))
    add("    documents scanned        %d" % len(documents))
    add("    RULED: declarations      %d claimed, %d triaged, %d unclaimed"
        % (len(claimed), len(triaged), len(unclaimed)))
    add("")

    if broken:
        add("## 0. BROKEN -- A REGISTERED RULING NO LONGER RESOLVES")
        add("")
        add("**This is the failure this register exists to make loud.** An "
            "entry below names a ruling whose own words are no longer in the "
            "document that held them.")
        add("")
        for line in broken:
            add("* %s" % bai._ascii(line))
        add("")

    add("---")
    add("")
    add("## 1. THE REGISTER, BY WHAT IT BINDS")
    add("")
    add("Scan the CLAIM column against your question. Every claim is a "
        "paraphrase written to be matched; the ARGUMENT is in the document, "
        "under the section named.")
    add("")

    for family in sorted({item.ruling.binds.split(" -- ")[0] for item in ok}):
        add("### %s" % bai._ascii(family))
        add("")
        add("| id | what was ruled | binds | when | where (document / section) |")
        add("|---|---|---|---|---|")
        rows = [i for i in ok if i.ruling.binds.split(" -- ")[0] == family]
        for item in sorted(rows, key=lambda i: (i.date, i.ruling.id)):
            tail = item.ruling.binds.split(" -- ", 1)
            add("| `%s` | %s | %s | %s | %s<br>*%s* |" % (
                bai._cell(bai._ascii(item.ruling.id)),
                bai._cell(bai._ascii(item.ruling.claim)),
                bai._cell(bai._ascii(tail[1] if len(tail) > 1 else tail[0])),
                item.date,
                bai._cell(_link(item.ruling.document)),
                bai._cell(bai._ascii(item.section)),
            ))
        add("")

    add("---")
    add("")
    add("## 2. THE ALIAS MAP -- every other name a registered ruling wears")
    add("")
    add("`CANONICAL-RULING-ID` rules that aliases are KEPT, not deleted: "
        "*\"they are how existing readers find the rule, and deleting them "
        "would strand every document that uses one. They are mapped, and the "
        "map is the artifact.\"* **This table is that artifact.** If you "
        "arrived with a name from an old document, find it here.")
    add("")
    add("| you may have seen it called | canonical id |")
    add("|---|---|")
    pairs = sorted({(bai._ascii(a), item.ruling.id)
                    for item in ok for a in item.ruling.aliases},
                   key=lambda p: (p[0].lower(), p[1]))
    for alias, canonical in pairs:
        add("| %s | `%s` |" % (bai._cell(alias), bai._cell(canonical)))
    add("")

    notes = [i for i in ok if i.ruling.note]
    if notes:
        add("---")
        add("")
        add("## 3. NOTES ON INDIVIDUAL RULINGS")
        add("")
        for item in sorted(notes, key=lambda i: i.ruling.id):
            add("**`%s`** -- %s" % (bai._ascii(item.ruling.id),
                                    bai._ascii(item.ruling.note)))
            add("")

    add("---")
    add("")
    add("## 4. WHAT THIS REGISTER DID NOT SCAN")
    add("")
    add("**The discovery scan reads `RULED:` and nothing else.** It was "
        "chosen on precision -- 24 of 25 hits are genuine declarations, the "
        "best of fourteen signals measured -- and its recall is poor. The "
        "counts below are signals a ruling can be written under that this "
        "scan will NEVER see. They are printed every run so that a green "
        "check is not read as a complete one.")
    add("")
    add("| signal NOT scanned | files | lines |")
    add("|---|---|---|")
    for label, files, hits in unscanned(documents):
        add("| %s | %d | %d |" % (bai._cell(label), files, hits))
    add("")
    add("**The ruling that caused this register to be written is in the first "
        "row and not in the scan.** `BOUNDARY-IS-NOT-A-REASON` is phrased as "
        "a quoted ledger rule under a heading that carries no marker at all. "
        "It is registered because a person read it, and nothing here would "
        "have found it.")
    add("")

    add("---")
    add("")
    add("## 5. THE DECLARATIONS THE SCAN FOUND")
    add("")
    add("Every `RULED:` line in the corpus, and what became of it. An "
        "UNCLAIMED row fails `--check`.")
    add("")
    add("| document | section | claimed by |")
    add("|---|---|---|")
    seen = set()
    for rel, number, text, rid in sorted(claimed):
        key = (rel, rid)
        if key in seen:
            continue
        seen.add(key)
        add("| %s | %s | `%s` |" % (
            bai._cell(_link(rel)),
            bai._cell(bai._ascii(text[:90])),
            bai._cell(rid)))
    add("")
    if triaged:
        add("### 5.1 Triaged -- a declaration hit that is not a ruling made here")
        add("")
        for rel, number, text, key in sorted(triaged):
            add("**%s** -- `%s`" % (bai._cell(_link(rel)),
                                    bai._ascii(text[:100])))
            add("")
            add("> %s" % bai._ascii(table[key]))
            add("")
    if unclaimed:
        add("### 5.2 UNCLAIMED -- these fail `--check`")
        add("")
        for rel, number, text in sorted(unclaimed):
            add("* %s -- `%s`" % (bai._cell(_link(rel)),
                                  bai._ascii(text[:120])))
        add("")
    if stale:
        add("### 5.3 STALE TRIAGE -- these fail `--check`")
        add("")
        add("An entry on `NOT_A_RULING` for a hit the scan no longer "
            "produces. An allowlist nobody re-checks is a silencer.")
        add("")
        for key in stale:
            add("* `%s` -- `%s`" % (bai._cell(key[0]), bai._cell(key[1])))
        add("")

    return "\n".join(out) + "\n"


#: Words that carry no discrimination in a corpus where every document is
#: about rulings. Dropped from a `--find` query so that asking *"is a
#: forbidden substring a ruling"* is scored on `forbidden` and `substring`
#: rather than on `a`, `is` and `ruling` -- which between them match almost
#: every entry and would rank the right answer below the noise.
STOPWORDS = frozenset("""
a an and are as at be been but by can could does do for from has have if in
into is it its of on or that the their them then there these this to was were
what when where which who why will with would rule ruled ruling rulings
""".split())


def find(query: str, root: pathlib.Path = ROOT) -> list:
    """Entries whose judged text matches `query`, best first.

    **THIS IS THE FUNCTION THE WHOLE FILE EXISTS FOR.** A register that can
    only be read front to back is a document, and the corpus already has 207
    of those. The question this campaign keeps failing is asked in words --
    *does a forbidden substring count as a ruling* -- and it has to be
    answerable in words, against the CLAIM column, by somebody who does not
    know which file the answer is in. That is the exact case that failed four
    times.

    Scoring is deliberately dumb: count distinct query tokens present. A
    cleverer ranker would be a second thing to trust, and the register is
    small enough that recall beats precision -- a reader who is shown three
    candidates and picks the right one has still been saved the search.
    """
    tokens = {t for t in re.findall(r"[a-z0-9_]+", query.lower())
              if t not in STOPWORDS and len(t) > 1}
    ok, _ = resolve(REGISTER, root)
    scored = []
    for item in ok:
        hay = " ".join([
            item.ruling.id, item.ruling.claim, item.ruling.binds,
            item.ruling.note, " ".join(item.ruling.aliases),
        ]).lower()
        score = sum(1 for t in tokens if t in hay)
        if score:
            scored.append((score, item))
    return [i for _, i in sorted(scored, key=lambda p: (-p[0], p[1].ruling.id))]


def committed(root: pathlib.Path = ROOT) -> str:
    path = root / "_audit" / "RULINGS.md"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def problems(root: pathlib.Path = ROOT) -> list:
    return problems_over(REGISTER, corpus(root), root, NOT_A_RULING)


def problems_over(register, documents, root: pathlib.Path,
                  not_a_ruling=None) -> list:
    """Every condition that makes the register dishonest, as sentences."""
    ok, broken = resolve(register, root)
    _, _, unclaimed, stale = triage(documents, ok, root, not_a_ruling)
    out = list(broken)

    # THE REGISTER ENFORCES `CANONICAL-RULING-ID` ON ITSELF. That ruling says
    # a citation must resolve to ONE ruling; an alias pointing at two resolves
    # to neither, and a reader arriving with it is back where they started.
    # **This is not a hypothetical.** `section 2` was entered as an alias of
    # two different rulings on this register's first write, and because the
    # alias table is built from a SET the two rows swapped order between runs
    # -- so `--write` then `--check` disagreed and the drift check caught a
    # non-determinism that no amount of reading the code had suggested.
    owners: dict = {}
    for item in ok:
        for alias in item.ruling.aliases:
            owners.setdefault(alias.lower(), set()).add(item.ruling.id)
    for alias, ids in sorted(owners.items()):
        if len(ids) > 1:
            out.append(
                "AMBIGUOUS ALIAS %r resolves to %d rulings (%s) -- "
                "CANONICAL-RULING-ID requires one. Qualify it, or drop it."
                % (alias, len(ids), ", ".join(sorted(ids))))
    for item in ok:
        if item.ruling.id.lower() in owners and \
                owners[item.ruling.id.lower()] != {item.ruling.id}:
            out.append("ALIAS COLLIDES WITH A CANONICAL ID: %r"
                       % item.ruling.id)

    for rel, number, text in unclaimed:
        out.append("UNCLAIMED declaration in %s: %r -- register it, or triage "
                   "it onto NOT_A_RULING with a reason" % (rel, text[:100]))
    for key in stale:
        out.append("STALE NOT_A_RULING entry %r -- the scan no longer "
                   "produces this hit; remove it" % (key,))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true",
                        help="regenerate _audit/RULINGS.md")
    parser.add_argument("--check", action="store_true",
                        help="fail if the committed register is not what this "
                             "generator derives, or if any registered ruling "
                             "no longer resolves in the corpus")
    parser.add_argument("--find", metavar="WORDS", default=None,
                        help="ask what has been ruled about something, in "
                             "words: --find \"forbidden substring\"")
    args = parser.parse_args(argv)

    if args.find is not None:
        hits = find(args.find, ROOT)
        if not hits:
            print("NOTHING REGISTERED MATCHES %r." % args.find)
            print("")
            print("THAT IS NOT A FINDING THAT NOTHING WAS RULED. The register")
            print("holds %d rulings and its discovery scan reads `RULED:`"
                  % len(REGISTER))
            print("only -- section 4 of _audit/RULINGS.md lists the signals it")
            print("does not read. Search the corpus before concluding.")
            return 0
        print("%d registered ruling(s) match %r, best first:"
              % (len(hits), args.find))
        for rank, item in enumerate(hits, 1):
            print("")
            print("  %d. %s   [%s]"
                  % (rank, bai._ascii(item.ruling.id), item.date))
            print("     RULED  : %s" % bai._ascii(item.ruling.claim))
            print("     BINDS  : %s" % bai._ascii(item.ruling.binds))
            print("     WHERE  : %s" % bai._ascii(item.ruling.document))
            print("     SECTION: %s" % bai._ascii(item.section))
            if item.ruling.aliases:
                print("     ALIASES: %s"
                      % bai._ascii(", ".join(item.ruling.aliases)))
            if item.ruling.note:
                print("     NOTE   : %s" % bai._ascii(item.ruling.note))
        return 0

    text = render(ROOT)
    found = problems(ROOT)

    if args.write:
        RULINGS.write_text(text, encoding="utf-8", newline="\n")
        print("wrote %s -- %d rulings registered"
              % (RULINGS.relative_to(ROOT).as_posix(), len(REGISTER)))
        for line in found:
            print("  STILL BROKEN: %s" % line)
        return 1 if found else 0

    if args.check:
        failed = False
        for line in found:
            print("FAIL %s" % line)
            failed = True
        have = committed(ROOT)
        if not have:
            print("FAIL _audit/RULINGS.md does not exist; run --write")
            failed = True
        elif have != text:
            mine, theirs = text.splitlines(), have.splitlines()
            for number, (one, two) in enumerate(zip(theirs, mine), 1):
                if one != two:
                    print("FAIL _audit/RULINGS.md drifted at line %d" % number)
                    print("  committed: %s" % one[:150])
                    print("  derived  : %s" % two[:150])
                    break
            else:
                print("FAIL _audit/RULINGS.md has %d lines, the corpus "
                      "derives %d" % (len(theirs), len(mine)))
            failed = True
        if failed:
            return 1
        documents = corpus(ROOT)
        print("ok _audit/RULINGS.md matches: %d rulings, all anchors resolve, "
              "all declarations accounted for (%d documents)"
              % (len(REGISTER), len(documents)))
        print("   NOT SCANNED: the discovery half reads `RULED:` only. "
              "Section 4 of the register lists what it does not read.")
        return 0

    ok, _ = resolve(REGISTER, ROOT)
    documents = corpus(ROOT)
    claimed, triaged, unclaimed, stale = triage(documents, ok, ROOT)
    print("rulings registered    %d" % len(REGISTER))
    print("anchors resolving     %d" % len(ok))
    print("documents scanned     %d" % len(documents))
    print("declarations claimed  %d" % len(claimed))
    print("declarations triaged  %d" % len(triaged))
    print("declarations UNCLAIMED %d" % len(unclaimed))
    print("stale triage entries  %d" % len(stale))
    for line in problems(ROOT):
        print("  %s" % line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
