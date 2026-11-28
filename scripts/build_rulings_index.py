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
             "wave, to feed one live lane from several offline build lanes. "
             "Read strictly by BUDGET-ONE-ACCOUNT-40 (2026-11-26): the 40 are "
             "his account's, per trailing 12 hours, shared with the job "
             "pipeline.",
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
        note="Amended 2026-11-26 for JOB APPLICATIONS only by "
             "RATIFIED-POLICY-NAMES-APPLICATION-TARGETS: a policy he ratified "
             "names those targets by rule. Every other outward act is "
             "unchanged.",
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
    Ruling(
        id="RELATION-REMOVALS-BUILT-BEHIND-GRANTS",
        claim="Removing a relation with a member he names -- removing a "
              "1st-degree connection, blocking a member, removing an attendee "
              "from an event he organises -- is BUILT behind the single-use "
              "grant, off by default, fired only at the one member he names in "
              "the call, with the resolved identity reported before the act.",
        binds="writes -- his relations with another member",
        document="_audit/2026-09-27-rulings-relation-removals-and-account-"
                 "destruction.md",
        anchor="RULED: (orchestrator, 2026-09-27, applying the operator's 08:11 "
               "principle) REMOVING A RELATION",
        note="Orchestrator's call applying the operator's 08:11 principle and "
             "OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Decides N 29, N 141 "
             "and N A14, which lane L8 left outside the three classes.",
    ),
    Ruling(
        id="ACCOUNT-DESTRUCTION-STAYS-MANUAL",
        claim="Merging or closing his account, and deleting the data LinkedIn "
              "holds about him, are NOT built: EXCLUDED-RULED, reopened only "
              "when he asks for one by name in the call that would make it.",
        binds="writes -- his account and its data",
        document="_audit/2026-09-27-rulings-relation-removals-and-account-"
                 "destruction.md",
        anchor="RULED: (orchestrator, 2026-09-27, applying the operator's 08:11 "
               "principle) ACCOUNT-LEVEL",
        note="Orchestrator's call applying the operator's 08:11 principle; "
             "overridable. Decides P N27 and P P2, and adds a capability-level "
             "ground to P N28.",
    ),
    Ruling(
        id="PREVIEW-NAMES-THE-RESOLVED-TARGET",
        claim="A preview names whom the tool resolved -- the page-read name and "
              "headline, sanitised, marked untrusted, inside a people record -- "
              "and is returned at runtime, never written; a receipt (anything "
              "persisted after a write fires) carries only the caller-supplied "
              "target.",
        binds="writes -- previews and receipts",
        document="_audit/2026-09-27-rulings-previews-and-receipts.md",
        anchor="RULED: (orchestrator, 2026-09-27, applying NAMES-AT-RUNTIME) A "
               "PREVIEW NAMES WHOM",
        note="Orchestrator's call applying NAMES-AT-RUNTIME and "
             "PEOPLE-DATA-MITIGATIONS; overridable. Answers lane G's preview "
             "question.",
    ),
    # THE AMENDED RULING IS A FAMILY OF THE EXCLUSION REGISTER, NOT AN ENTRY
    # OF THIS ONE (lane L5, 2026-09-28). His 2026-09-04 removal of the
    # third-party profile pattern was never filed here: it is registered in
    # ``scripts/check_exclusion_basis.py`` as the family
    # NO-THIRD-PARTY-PROFILE-LOAD (op=YES, made by the OPERATOR), anchored on
    # the removal's own comment in ``linkedin_server/readonly.py``. That id is
    # the one this status names.
    Ruling(
        id="NAMED-PROFILE-READ-BEHIND-A-GRANT",
        claim="A read of a member's profile he names in the call -- by link "
              "or member id, never a name read off a page -- is built behind "
              "the single-use grant, its preview stating that LinkedIn may "
              "show the member the view; declared fields leave as people "
              "records; never for a measurement.",
        binds="read boundary -- a third-party profile he names",
        document="_audit/2026-09-28-rulings-named-profile-read.md",
        anchor="RULED: (operator, 2026-09-28 08:01, verbatim) \"Yes, I'm "
               "giving you permission.\"",
        status="AMENDS NO-THIRD-PARTY-PROFILE-LOAD",
        note="The operator's ruling, verbatim in its document; mitigations as "
             "the question put them.",
    ),
    # THE FIVE CLASS RULINGS OF 2026-09-28 (registered by lane K, 2026-10-10,
    # from the orchestrator's paused-lanes copy, byte-identical). Lanes A, U
    # and S copy the same document; these five entries are the register's
    # half of it.
    Ruling(
        id="EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS",
        claim="Every act toward other people -- publishing his own content and "
              "its modes, invitations that are not connection requests, RSVPs "
              "and group membership requests, reports about another member's "
              "content and their undo -- is BUILT behind the single-use grant, "
              "off by default, fired only at a target he names. It does not "
              "reach measured permanent refusals, the destruction rulings or "
              "purchases.",
        binds="writes -- every act toward other people",
        document="_audit/2026-09-28-rulings-build-classes.md",
        anchor="RULED: (orchestrator, 2026-09-28, applying WRITE-CLASS-B and "
               "the operator's 08:11 principle) "
               "EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS",
        note="Orchestrator's call applying WRITE-CLASS-B and the operator's "
             "08:11 principle; overridable. Extends "
             "OUTWARD-CLASSES-BUILT-BEHIND-GRANTS to every outward class.",
    ),
    Ruling(
        id="HIS-OWN-SETTINGS-NOT-OUTWARD",
        claim="A setting of his own account is not an outward act: built behind "
              "the grant, live-proven one setting at a time by read, benign "
              "write, read back, exact restore, read back; a failed restore is "
              "STOP-ALL. Credential settings, settings that cannot be put back "
              "exactly and sensitive self-identification are built and never "
              "live-proven unless he names them.",
        binds="writes -- settings of his own account",
        document="_audit/2026-09-28-rulings-build-classes.md",
        anchor="RULED: (orchestrator, 2026-09-28, applying "
               "OUTWARD-ACTS-NEED-THE-OPERATOR) HIS-OWN-SETTINGS-NOT-OUTWARD",
        note="Orchestrator's call applying OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Settings pages are still admitted one by name.",
    ),
    Ruling(
        id="HIS-OWN-CURATION-NOT-OUTWARD",
        claim="Curating his own feed and items -- mute, hide, not interested, "
              "follow or unfollow from a feed item, save, a post's "
              "notification switch, the per-post controls on his own items -- "
              "is not an outward act: built behind the grant and proven with "
              "its inverse in the same session, read back.",
        binds="writes -- curation of his own feed and items",
        document="_audit/2026-09-28-rulings-build-classes.md",
        anchor="RULED: (orchestrator, 2026-09-28, applying "
               "OUTWARD-ACTS-NEED-THE-OPERATOR) HIS-OWN-CURATION-NOT-OUTWARD",
        note="Orchestrator's call applying OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. An undo drawn only once proves the act only "
             "through that undo.",
    ),
    Ruling(
        id="PURCHASES-STAY-MANUAL",
        claim="A purchase -- Premium, InMail credits, ads, boosts, any paid "
              "upgrade -- is NOT built: its row is EXCLUDED-RULED, reopened "
              "when he names a purchase to automate.",
        binds="writes -- purchases",
        document="_audit/2026-09-28-rulings-build-classes.md",
        anchor="RULED: (orchestrator, 2026-09-28, applying COST-AWARE "
               "STAKES-GATING) PURCHASES-STAY-MANUAL",
        note="Orchestrator's call applying the operator's COST-AWARE "
             "STAKES-GATING rule; overridable.",
    ),
    Ruling(
        id="READ-PAST-AN-ACT-SUBSTRING",
        claim="A refused substring whose recorded ground is an ACT -- sending, "
              "following, applying -- does not bar the READ of his own page "
              "that carries it: one exact anchored pattern, a control shown "
              "failing, the press gate still refusing every control. Not for "
              "a GET that changes state, a credential, recovery, session or "
              "security surface, a sign-in challenge, or a refusal grounded "
              "in an operator's ruling.",
        binds="read boundary -- substrings written to stop an act",
        document="_audit/2026-09-28-rulings-build-classes.md",
        anchor="RULED: (orchestrator, 2026-09-28, applying "
               "OUTWARD-ACTS-NEED-THE-OPERATOR and "
               "D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING) "
               "READ-PAST-AN-ACT-SUBSTRING",
        note="Orchestrator's call applying OUTWARD-ACTS-NEED-THE-OPERATOR and "
             "D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING; overridable. A page the "
             "allowlist refuses by its silence is admitted the same way.",
    ),
    # THE LEDGER'S QUESTIONS, RULED 2026-10-10 (registered by lane K from the
    # orchestrator's copy, byte-identical). Fifteen rulings; the document's
    # sixth section points at lane NP's route and its thirteenth relays a
    # question to the operator, so neither declares a ruling here.
    Ruling(
        id="CAPTURE-PRESS-UNDER-PROBE-RULE",
        claim="A live-lane CAPTURE may press a disclosure control (a menu, a "
              "folder, a filter panel, a list) or type into a SEARCH box, "
              "never a composer or an editor, on a surface the press gate "
              "refuses, when nothing is committed: no save, send, submit, "
              "apply or confirm, and Escape closes what was opened. A shipped "
              "tool still needs its own per-surface basis entry.",
        binds="captures -- presses and typing on a surface the gate refuses",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) CAPTURE-PRESS-UNDER-PROBE-RULE",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. The capture is the evidence a tool's basis entry "
             "is built from.",
    ),
    Ruling(
        id="ARTICLE-COMPOSER-CAPTURE",
        claim="One capture load of the article composer is permitted, with "
              "nothing typed and nothing published; an empty draft it may "
              "leave is his, private and deletable, and the capture records "
              "whether one appeared.",
        binds="captures -- the article composer",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) ARTICLE-COMPOSER-CAPTURE",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable.",
    ),
    Ruling(
        id="NO-INDEX-PINNED-JUDGEMENTS",
        claim="A control is judged by its own accessible name and role, never "
              "by its position; controls on his own profile go to capture "
              "first, and label-based basis entries follow from it.",
        binds="press gate -- how a control is judged",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) NO-INDEX-PINNED-JUDGEMENTS",
        note="Orchestrator's call; overridable. Session 7 saw LinkedIn move "
             "structure under a recorded position.",
    ),
    Ruling(
        id="CALLER-COMPOSITION-UNDER-D6",
        claim="A row is discharged under D6-CAPABILITY-OVER-AFFORDANCE when "
              "the caller can compose SHIPPED tools to deliver its payload, "
              "with no server-side derived navigation; the row's cell names "
              "the tools and their arguments, and its state is the weakest "
              "of its parts.",
        binds="census state -- rows a composition of shipped tools delivers",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) CALLER-COMPOSITION-UNDER-D6",
        note="Orchestrator's call applying D6-CAPABILITY-OVER-AFFORDANCE; "
             "overridable.",
    ),
    Ruling(
        id="CONTACT-IMPORT-STAYS-MANUAL",
        claim="An address-book import or sync is not built: it uploads other "
              "people's contact data and completes on another domain's "
              "consent screen. EXCLUDED-RULED, reopened when he asks to "
              "import or sync his address book.",
        binds="writes -- importing or syncing his address book",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) CONTACT-IMPORT-STAYS-MANUAL",
        note="Orchestrator's call; overridable. Decides N 106, N 108 and "
             "P N21.",
    ),
    Ruling(
        id="SESSION-SURFACE",
        claim="Reading the active-sessions list stays GAP, admissible only as "
              "ONE named settings page after a capture proves the address is "
              "the current settings page and that loading it changes nothing; "
              "never through the legacy path. Signing out of sessions is "
              "EXCLUDED-RULED, reopened when he names it.",
        binds="reads and writes -- the active-sessions surface",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) SESSION-SURFACE",
        note="Orchestrator's call applying CREDENTIAL-SETTINGS-NEED-THE-OPERATOR; "
             "overridable. Decides P N9 and P N10.",
    ),
    Ruling(
        id="SIGN-IN-CHALLENGES-ARE-HIS",
        claim="This server never answers a sign-in or account-recovery "
              "challenge; password and second-factor entry are the operator's "
              "own gate. EXCLUDED-RULED, reopened never by this server -- he "
              "completes them himself.",
        binds="reads and writes -- sign-in and recovery challenges",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) SIGN-IN-CHALLENGES-ARE-HIS",
        note="Orchestrator's call; overridable. Decides P N13 and P N14.",
    ),
    Ruling(
        id="APPLY-FLOW-IS-THE-APPLICATION",
        claim="Opening the Easy Apply flow is the first step of an "
              "application, so its read stays refused; the daily-limit row "
              "waits on the limit being reached.",
        binds="read boundary -- the Easy Apply flow",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) APPLY-FLOW-IS-THE-APPLICATION",
        note="Orchestrator's call; overridable. Decides J 82.",
    ),
    Ruling(
        id="THIRD-PARTY-TEXT-AT-RUNTIME",
        claim="A post's own text and an organisation Page's prose are returned "
              "at runtime as untrusted third-party text -- sanitised, bounded "
              "in length, never stored -- under PEOPLE-DATA-MITIGATIONS; the "
              "feed-content ruling still governs what is stored.",
        binds="reads -- other people's text, returned at runtime",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10, applying the operator's "
               "NAMES-AT-RUNTIME) THIRD-PARTY-TEXT-AT-RUNTIME",
        note="Orchestrator's call applying NAMES-AT-RUNTIME; overridable. "
             "Decides M C43 and J 110.",
    ),
    Ruling(
        id="DOM-WAIVER-25-J110",
        claim="dom.py may hold a 25th waived page evaluate, solely J 110's "
              "page-root reader read (COMPANY_HOME_JS, moved verbatim from "
              "its branch), read-only and argued under "
              "THIRD-PARTY-TEXT-AT-RUNTIME; a 26th still needs its own ruling.",
        binds="reads -- the dom.py waived-evaluate budget in "
              "tests/test_readonly.py, and its copy in "
              "tests/test_the_search_shape_reading.py",
        document="_audit/2026-10-26-integration-2.md",
        anchor="RULED: (orchestrator, 2026-11-25) DOM-WAIVER-25-J110",
        note="Orchestrator's call, answering integration 2's question about "
             "the budget move its J 110 fix made by commit (24 -> 25). "
             "Applies THIRD-PARTY-TEXT-AT-RUNTIME.",
    ),
    # ---- integration 3 (2026-11-26): the orchestrator's rulings of 2026-11-25
    # from 22:30 IST, registered from _audit/2026-11-25-rulings-end-of-wave.md
    Ruling(
        id="L1-D1-RIDERS-RIDE",
        claim="Live plan L1, D-1: both riders take their hosts' loads (C-B3-2 on the own-post-reactions load, C-B5-4 on C-B5-3's).",
        binds="the live plan -- session 11's riders",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) L1-D1-RIDERS-RIDE",
        note="Orchestrator's call on the live plan's question D-1. Reopener: none stated. Moves no row: it governs session 11's loads.",
    ),
    Ruling(
        id="L1-D2-GROUPS-FROM-HIS-MEMBERSHIPS",
        claim="Live plan L1, D-2 (b): the groups come from his memberships plus one groups search, which fires N 161.",
        binds="the live plan -- which groups session 11 opens",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) L1-D2-GROUPS-FROM-HIS-MEMBERSHIPS",
        note="Orchestrator's call on D-2. Reopener: none stated. Moves no row by itself; session 11's search fire is N 161's.",
    ),
    Ruling(
        id="L1-D3-MEDIA-CHOOSER-INTERCEPTED",
        claim="Live plan L1, D-3: a composer's media control may be pressed with the file chooser intercepted and never answered, then Escape.",
        binds="the live plan -- composer media presses",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) L1-D3-MEDIA-CHOOSER-INTERCEPTED",
        note="Orchestrator's call on D-3. Reopener: none stated. Moves no row: it governs session 11's presses.",
    ),
    Ruling(
        id="L1-D4-NEUTRAL-READ-VALUES",
        claim="Live plan L1, D-4: read values are neutral -- session 2's organisation if recorded, else a large Page verified at runtime as not his employer, and generic keywords.",
        binds="the live plan -- the values a session reads with",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) L1-D4-NEUTRAL-READ-VALUES",
        note="Orchestrator's call on D-4. Reopener: none stated. Moves no row.",
    ),
    Ruling(
        id="MEASURED-ABSENT-OR-PRECONDITION",
        claim="MEASURED-ABSENT means LinkedIn does not offer the capability to this account at all; PRECONDITION means it is offered but needs an account state he lacks, with a named reopener.",
        binds="census state -- MEASURED-ABSENT against a GAP row waiting on a PRECONDITION",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) MEASURED-ABSENT-OR-PRECONDITION",
        aliases=("the absence convention",),
        note="Orchestrator's convention; overridable. Names N 118, P E7 and P K8 for reconciliation. Reopener: none stated.",
    ),
    Ruling(
        id="P-O23-D5-ON-ITS-OWN-WORDS",
        claim="P O23 takes D5's NOT-AN-ACT only if D5's own words cover it, and the registering lane checks and quotes them.",
        binds="census row P O23",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) P-O23-D5-ON-ITS-OWN-WORDS",
        note="Orchestrator's call. Applied at integration 3: D5 covers a consequence with no control of its own, and O23's consequence has one (P O17's switch), so O23 stays GAP. Reopener: a change to D5's words.",
    ),
    Ruling(
        id="ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC",
        claim="An organisation's name may return at runtime as third-party text, and its link only when the link is numeric; N 104's bar is still unmet, so it stays GAP.",
        binds="reads -- organisation identity returned at runtime",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC",
        aliases=("Q-ORG-IDENTITY",),
        note="Orchestrator's answer of 2026-10-10 19:22, registered at integration 3. Applies THIRD-PARTY-TEXT-AT-RUNTIME. Reopener: N 104 meeting its own bar.",
    ),
    Ruling(
        id="B5-RAIL-JOIN-DOES-NOT-DISCHARGE",
        claim="A Join button drawn in a page's side rail does not discharge N 63 or M C61: the target would come from the page.",
        binds="census rows N 63, M C61",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) B5-RAIL-JOIN-DOES-NOT-DISCHARGE",
        note="Lane B5's first answer, recorded 2026-10-10 19:18, registered at integration 3. Applies PAGE-MAY-VETO-NEVER-SUPPLY. Reopener: none stated.",
    ),
    Ruling(
        id="B5-GROUP-COMPOSER-OPENS-EMPTY",
        claim="A capture may open a group's composer with nothing typed (capture C-B5-4), as ARTICLE-COMPOSER-CAPTURE allows for articles.",
        binds="captures -- a group composer opened empty",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) B5-GROUP-COMPOSER-OPENS-EMPTY",
        note="Lane B5's second answer, registered at integration 3. Applies ARTICLE-COMPOSER-CAPTURE. Reopener: none stated.",
    ),
    Ruling(
        id="B5-INVITE-DIALOG-IS-A-LIST",
        claim="A group's invite dialog is a list and its filter is a search box (capture C-B5-3): reading them sends nothing.",
        binds="captures -- a group's invite dialog",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) B5-INVITE-DIALOG-IS-A-LIST",
        note="Lane B5's third answer, registered at integration 3. Reopener: none stated.",
    ),
    Ruling(
        id="M-C18-EDITOR-OPENS-UNSAVED",
        claim="His answer for C-B5-4 covers opening his post editor unsaved, so M C18 becomes a cheap capture.",
        binds="census row M C18",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) M-C18-EDITOR-OPENS-UNSAVED",
        note="Orchestrator's call, applying B5-GROUP-COMPOSER-OPENS-EMPTY. Reopener: none stated.",
    ),
    Ruling(
        id="M-C97-LINK-KEYED-DELETE",
        claim="M C97's delete is keyed by the notification's link and refuses a link that matches more than one card; building it needs a live uniqueness capture first.",
        binds="census row M C97 -- a notification delete",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) M-C97-LINK-KEYED-DELETE",
        aliases=("Q-NOTIFICATION-KEY",),
        note="Orchestrator's design call; answers the ledger's Q-NOTIFICATION-KEY. Reopener: the live uniqueness capture.",
    ),
    Ruling(
        id="M-C29-DESIGN-FIRST",
        claim="M C29 is designed first and queued for the next build wave.",
        binds="census row M C29",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) M-C29-DESIGN-FIRST",
        note="Orchestrator's call. Reopener: the next build wave.",
    ),
    Ruling(
        id="APPLY-DRY-WALK-FIRES-THE-STEP-ROWS",
        claim="A dry walk of the apply flow on a named posting, every step read back and the draft discarded and verified, fires the step rows J 61 to J 65; the submission row still needs a real send.",
        binds="census rows J 61-J 65 -- the apply flow's steps",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) APPLY-DRY-WALK-FIRES-THE-STEP-ROWS",
        note="Orchestrator's call on lane apply-26. Applies APPLY-FLOW-IS-THE-APPLICATION. Moves no row until the walk is fired. Reopener: none stated.",
    ),
    Ruling(
        id="SCREENING-QUESTION-RECORD",
        claim="An application's screening question is returned as a new people_data record type, ScreeningQuestion, under THIRD-PARTY-TEXT-AT-RUNTIME.",
        binds="reads -- screening questions as third-party text",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) SCREENING-QUESTION-RECORD",
        note="Orchestrator's call on lane apply-26. Applies THIRD-PARTY-TEXT-AT-RUNTIME. Reopener: none stated.",
    ),
    Ruling(
        id="REFUSED-APPLY-DISCARDS-ITS-DRAFT",
        claim="When linkedin_apply_job refuses mid-flow, it dismisses the flow, presses Discard and verifies the Draft tab holds nothing it left.",
        binds="writes -- the apply flow's refusal path",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) REFUSED-APPLY-DISCARDS-ITS-DRAFT",
        note="Orchestrator's call on lane apply-26. Reopener: none stated.",
    ),
    Ruling(
        id="L3-OPENS-WITH-A-DRAFT-RESIDUE-READ",
        claim="Live session L3 opens with one read of the Draft tab, for any residue an earlier apply walk left.",
        binds="the live plan -- session L3's first load",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) L3-OPENS-WITH-A-DRAFT-RESIDUE-READ",
        note="Orchestrator's call on lane apply-26. Reopener: none stated. Moves no row.",
    ),
    Ruling(
        id="C-J68-IDS-KEPT",
        claim="The capture lines C-J68-1 to C-J68-3 keep their ids, in the census family J 60 to J 69.",
        binds="the capture queue -- the apply-flow captures",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) C-J68-IDS-KEPT",
        note="Orchestrator's call on lane apply-26. Applied at integration 3: the ids kept, the ranks renumbered on merge. Reopener: none stated.",
    ),
    Ruling(
        id="JOBHUNT-HOME-KEEPS-ITS-MEANING",
        claim="JOBHUNT_HOME keeps jobcore's meaning, the directory holding jobhunt.json.",
        binds="configuration -- the JOBHUNT_HOME variable",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) JOBHUNT-HOME-KEEPS-ITS-MEANING",
        note="Orchestrator's call on lane apply-26. Reopener: none stated.",
    ),
    Ruling(
        id="JOBHUNT-ROOT-RESOLUTION-ORDER",
        claim="The answer bank resolves JOBHUNT_ANSWER_BANK, then JOBHUNT_ROOT, then the .jobhunt-root walk-up (six parents, as jobcore); JOBHUNT_HOME is never read.",
        binds="configuration -- how the apply walker finds its answer bank",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) JOBHUNT-ROOT-RESOLUTION-ORDER",
        note="Orchestrator's call on lane apply-26, refined on its final head. Reopener: none stated.",
    ),
    Ruling(
        id="EDITOR-TYPEAHEAD-SANCTIONED",
        claim="A capture may type a benign value from tool arguments into his own editor's autocomplete field, dismiss it with Cancel or Escape and re-read to prove nothing changed; any autosave sign stops everything.",
        binds="captures -- his own editor's typeahead fields (P A11, P A13, P A17)",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) EDITOR-TYPEAHEAD-SANCTIONED",
        aliases=("Q-EDITOR-TYPEAHEAD",),
        note="Orchestrator's call on lane build-p26. Moves P A11, P A13, P A17 to CAPTURE on C-B1a. Reopener: any autosave sign.",
    ),
    Ruling(
        id="ABSENT-ON-HIS-ACCOUNT-PER-ROW",
        claim="Per row, under the absence convention: a drawn and corroborated empty state answers a READ; a surface not offered to his account is MEASURED-ABSENT; a write needing data he lacks is PRECONDITION with a reopener.",
        binds="census rows P A14, P A15, P K8",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) ABSENT-ON-HIS-ACCOUNT-PER-ROW",
        aliases=("Q-ABSENT-ON-HIS-ACCOUNT",),
        note="Orchestrator's call on lane build-p26, applying MEASURED-ABSENT-OR-PRECONDITION. Applied at integration 3: P A14 and P A15 to MEASURED-ABSENT (not drawn for his account), P K8 waiting on a PRECONDITION (a badge he lacks). Reopener: per row, the one the row names.",
    ),
    Ruling(
        id="OWN-PROFILE-SCROLL-SANCTIONED",
        claim="One scroll pass of his own profile per load is permitted, reading what renders and pressing nothing.",
        binds="captures -- a scroll of his own profile (P D26)",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) OWN-PROFILE-SCROLL-SANCTIONED",
        aliases=("Q-OWN-PROFILE-SCROLL",),
        note="Orchestrator's call on lane build-p26. Reopener: none stated.",
    ),
    Ruling(
        id="LINKS-ARE-NOT-DISCLOSURES",
        claim="A link on his own profile is not a disclosure: the in-me-profile link presses for P D25 and P A25 are vetoed, and both rows go to a ruling on whether the self-profile query variant is admissible.",
        binds="captures -- link presses on his own profile (P D25, P A25)",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) LINKS-ARE-NOT-DISCLOSURES",
        note="Orchestrator's call on lane build-p26, applying PAGE-MAY-VETO-NEVER-SUPPLY. Reopener: the ruling on the self-profile query variant.",
    ),
    Ruling(
        id="RECOMMENDATIONS-DETAIL-PAGE-ADMITTED",
        claim="The named /in/me/details/recommendations/ address is admitted (the interests-page precedent); its capture records where it lands.",
        binds="reads -- his recommendations detail page",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) RECOMMENDATIONS-DETAIL-PAGE-ADMITTED",
        aliases=("Q-RECOMMENDATIONS-DETAIL-PAGE",),
        note="Orchestrator's call on lane admit26. Moves its 13 rows to ADMIT. Reopener: none stated.",
    ),
    Ruling(
        id="OPEN-TO-WORK-EDITOR-ATTENDED-ONLY",
        claim="A capture may press his Open-to-Work Edit only in a session he attends: read the modal, close it, choose nothing, and round-trip read the card before and after; any change to the card stops everything.",
        binds="captures -- his Open-to-Work editor",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) OPEN-TO-WORK-EDITOR-ATTENDED-ONLY",
        aliases=("Q-OPEN-TO-WORK-EDITOR",),
        note="Orchestrator's call on lane admit26. Moves its 11 rows to CAPTURE. Reopener: the card changing.",
    ),
    Ruling(
        id="VOLUNTEERING-BARE-SPELLING-FIRST",
        claim="His volunteering-education page is tried in its bare spelling first, the capture recording where it lands; if it does not land, his own profileId comes from tool arguments at runtime and is never stored.",
        binds="reads -- his volunteering-education page (P D24)",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) VOLUNTEERING-BARE-SPELLING-FIRST",
        aliases=("Q-VOLUNTEERING-PROFILE-ID",),
        note="Orchestrator's call on lane admit26. Its reopener was met in live session 12 (load 22: the bare spelling redirected to his root); VOLUNTEERING-FALLBACK-BOUNDARY (integration 7) is the fallback, built by lane prof7. Reopener: the bare spelling not landing.",
    ),
    Ruling(
        id="VERIFICATIONS-PAGE-ADMITTED",
        claim="The exact /mypreferences/d/verifications address is admitted read-only, with zero presses and a per-address exemption for 'verification'; two-step verification stays refused.",
        binds="reads -- his verifications page",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) VERIFICATIONS-PAGE-ADMITTED",
        aliases=("Q-VERIFICATIONS-PAGE",),
        note="Orchestrator's call on lane admit26. Moves P K1 and P K7 to ADMIT. P K1 is COVERED-UNFIRED on linkedin_my_verifications (lane settings7, merged in integration 7); P K7 is held by VERIFICATION-DELETE-HELD. Reopener: none stated.",
    ),
    Ruling(
        id="NAME-BEARING-ADDRESS-REDACTION-SCOPE",
        claim="The redaction of a name-bearing address reaches every tracked or CI- or console-printed record, while gitignored raw state may hold the address; the newsletter page is admitted now on its drawn slug shape, and the article page after a capture spells it.",
        binds="reads -- newsletter and article pages, and what records may hold their addresses",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) NAME-BEARING-ADDRESS-REDACTION-SCOPE",
        aliases=("Q-NAME-BEARING-ADDRESS-REDACTION",),
        note="Orchestrator's call on lane admit26. Moves the five newsletter rows to ADMIT. Reopener: for the article page, a capture that spells its address.",
    ),
    Ruling(
        id="AI-GENERATION-IS-A-NON-OUTWARD-WRITE",
        claim="A load that starts an AI generation on his own account, toward no person, is a non-outward write: allowed behind the grant, one capture per feature, with its quota effect recorded on the row.",
        binds="writes -- AI generation loads on his own account",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) AI-GENERATION-IS-A-NON-OUTWARD-WRITE",
        aliases=("Q-AI-GENERATING-LOADS",),
        note="Orchestrator's call on lane admit26. Its 8 rows are left at their ruling step at integration 3: the read boundary still refuses their addresses, and the ledger has no capture class for a write behind the grant. Reopener: none stated.",
    ),
    Ruling(
        id="AI-COACH-OUTSIDE-PURPOSE",
        claim="Asking LinkedIn Learning's AI coach is EXCLUDED-RULED by OUTSIDE-THE-PRODUCT-PURPOSE.",
        binds="census row J 155",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) AI-COACH-OUTSIDE-PURPOSE",
        aliases=("Q-AI-COACH-QUESTION",),
        note="Orchestrator's call on lane admit26, applying OUTSIDE-THE-PRODUCT-PURPOSE. Reopener: he asks.",
    ),
    Ruling(
        id="COURSE-VIDEO-OUTSIDE-PURPOSE",
        claim="Watching a LinkedIn Learning course or video is EXCLUDED-RULED by OUTSIDE-THE-PRODUCT-PURPOSE.",
        binds="census row J 153",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) COURSE-VIDEO-OUTSIDE-PURPOSE",
        aliases=("Q-COURSE-VIDEO-PROGRESS",),
        note="Orchestrator's call on lane admit26, applying OUTSIDE-THE-PRODUCT-PURPOSE. Reopener: he asks.",
    ),
    Ruling(
        id="AD-LIBRARY-OUTSIDE-PURPOSE",
        claim="Searching LinkedIn's Ad Library is EXCLUDED-RULED by OUTSIDE-THE-PRODUCT-PURPOSE.",
        binds="census row J 159",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) AD-LIBRARY-OUTSIDE-PURPOSE",
        aliases=("Q-AD-LIBRARY-PURPOSE",),
        note="Orchestrator's call on lane admit26, applying OUTSIDE-THE-PRODUCT-PURPOSE. Reopener: he asks.",
    ),
    Ruling(
        id="RESUME-BUILDER-UNDER-ARTICLE-COMPOSER-CAPTURE",
        claim="ARTICLE-COMPOSER-CAPTURE extends to LinkedIn's resume builder, since it serves the job search: one load, nothing typed, once a capture finds where LinkedIn draws it.",
        binds="captures -- the resume builder (P M11)",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) RESUME-BUILDER-UNDER-ARTICLE-COMPOSER-CAPTURE",
        aliases=("Q-RESUME-BUILDER",),
        note="Orchestrator's call on lane admit26, applying ARTICLE-COMPOSER-CAPTURE. Reopener: a capture that finds where LinkedIn draws it.",
    ),
    Ruling(
        id="N-102-MOVES-WITH-J-108",
        claim="N 102 moves with J 108 as its sibling: there is no distinct capability (precedent N 173 / M C60).",
        binds="census rows N 102 and J 108",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) N-102-MOVES-WITH-J-108",
        note="Orchestrator's call on lane build-jmn26. Integration 2's section 6 had kept N 102 GAP; this ruling moves it, and that record carries the back-pointer. Reopener: none stated.",
    ),
    Ruling(
        id="J-19-BUILT-BEHIND-THE-GRANT",
        claim="J 19 is built behind the grant and refuses until its confirm dialog is captured; it fires only on his order.",
        binds="census row J 19 -- clearing his recent job searches",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) J-19-BUILT-BEHIND-THE-GRANT",
        note="Orchestrator's call on lane build-jmn26, applying OUTWARD-CLASSES-BUILT-BEHIND-GRANTS. Reopener: the confirm dialog's capture.",
    ),
    Ruling(
        id="J-110-SPLITS-HOME-AND-POSTS",
        claim="J 110 splits under COMPOUND-ROW-SPLITS-ONLY-ON-STATE: the Home half goes to COVERED-UNFIRED, and the Posts half is built on the live9 capture.",
        binds="census row J 110 and its Posts half",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) J-110-SPLITS-HOME-AND-POSTS",
        note="Orchestrator's call on lane build-jmn26, applying COMPOUND-ROW-SPLITS-ONLY-ON-STATE. Reopener: none stated.",
    ),
    Ruling(
        id="J-163-RECEIPT-ONLY-WRITE",
        claim="J 163 is a receipt-only write behind the grant, fired only on his order: no inverse exists, so the round-trip rule cannot apply, and the press itself is the proof.",
        binds="census row J 163 -- a one-shot recommendation feedback",
        document="_audit/2026-11-25-rulings-end-of-wave.md",
        anchor="RULED: (orchestrator, 2026-11-25) J-163-RECEIPT-ONLY-WRITE",
        aliases=("Q-ONE-SHOT-FEEDBACK",),
        note="Orchestrator's call on lane build-jmn26; answers the ledger's Q-ONE-SHOT-FEEDBACK. Reopener: his order.",
    ),
    Ruling(
        id="SEARCH-ROUTE-CLASSIC-PRIMARY",
        claim="The classic job search is the primary route while it serves; the AI search page is the fallback, and it refuses every filter not measured on it.",
        binds="reads -- the job search's route, classic or AI",
        document="_audit/2026-11-26-rulings-search-route.md",
        anchor="RULED: (orchestrator, 2026-11-26) SEARCH-ROUTE-CLASSIC-PRIMARY",
        aliases=("Q-SEARCH-ROUTE-POLICY",),
        note="Orchestrator's call on the classic search's retirement (01:20 entry). Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="FILTER-REQUERY-COUNTS-AS-A-SEARCH",
        claim="A re-query that a filter triggers counts as a search against the 5-per-session search cap.",
        binds="live loads -- the per-session search cap",
        document="_audit/2026-11-26-rulings-search-route.md",
        anchor="RULED: (orchestrator, 2026-11-26) FILTER-REQUERY-COUNTS-AS-A-SEARCH",
        aliases=("Q-FILTER-FIRES-SEARCH-CAP",),
        note="Orchestrator's call, applying D1-SEARCH-AS-READS's cap of 5 test searches per session. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE",
        claim="Rows proven on the classic job search stay COVERED-PROVEN while it serves; once a capture shows it no longer serves, each returns to GAP with its next step on the AI route and a reopener.",
        binds="census rows proven on the classic job search",
        document="_audit/2026-11-26-rulings-search-route.md",
        anchor="RULED: (orchestrator, 2026-11-26) RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE",
        aliases=("Q-RETIRED-ROUTE-ROWS",),
        note="Orchestrator's call on the classic search's retirement. Its trigger was met in live session 12: load 3, C-SRCH-1, was redirected to the AI route. Applied at integration 6 to the 22 rows of search26's report, section 4.5 (J 1 to J 15, J 17, J 18, J 20, J 40, J 107, J 151, and J 31, built on the classic switch), each to GAP with its next step on the AI route and a reopener. Four of them are COVERED-UNFIRED again, built on the AI route by lane jobs7 and merged in integration 7 (J 1, J 20, J 40, and J 31's AI arm); REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE refuses the classic arguments before any load. Reopener: none stated.",
    ),
    Ruling(
        id="SELF-PROFILE-QUERY-VARIANT-ADMITTED",
        claim="His own profile address carrying exactly one query parameter, isSelfProfile=true, is a read address in its own right: his own profile path only, that one parameter, composed by the server and never from a page, and refused unless the landing proves his own profile.",
        binds="reads -- his own profile's self-profile spelling (P D25, P A25)",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) SELF-PROFILE-QUERY-VARIANT-ADMITTED",
        aliases=("Q-SELF-PROFILE-QUERY-VARIANT",),
        note="Orchestrator's call on the lane-K ledger's question, raised by LINKS-ARE-NOT-DISCLOSURES. Applied by lane admit5-26 (the readonly.py line, red first, the /in/me/ form only); anchor (4) rests on lane selfprofile26's self-profile recognition. Reopener: a capture showing the variant draws nothing the bare profile does not.",
    ),
    Ruling(
        id="AI-EASY-APPLY-POST-FILTER",
        claim="On the AI job-search fallback, easy_apply may be honoured as a local post-filter on each card's own measured Easy Apply mark, from the one load with no re-query, named as such with counts before and after and never presented as LinkedIn's filter; the AI page's own toggle stays refused.",
        binds="reads -- the job search's AI fallback, one filter",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) AI-EASY-APPLY-POST-FILTER",
        note="Orchestrator's call on lane search-fix26's Q1; built in its second round. Moves no row. Reopener: for the page's own toggle, a capture that measures its effect.",
    ),
    Ruling(
        id="NO-RESULTS-STATE-CAPTURES",
        claim="Each job-search route's no-results state is captured (C-SRCH-0a classic, C-SRCH-0b AI; one load and one search each, a keyword chosen to draw nothing); until then every zero refuses on both routes.",
        binds="captures -- the job search's two no-results states",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) NO-RESULTS-STATE-CAPTURES",
        note="Orchestrator's call on lane search-fix26's Q2; the two capture lines are in the queue. Moves no row. Reopener: the two captures.",
    ),
    Ruling(
        id="READ-CARDS-DELETION",
        claim="After integration 4, the first lane touching server.py deletes server._read_cards if an AST caller census shows no caller.",
        binds="code -- server._read_cards",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) READ-CARDS-DELETION",
        note="Orchestrator's call on lane search-fix26's Q3. Executed by lane infra26 on an AST caller census that found no caller (717 tracked files and the 12 live-runner files), merged in integration 5. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="RATIFIED-POLICY-NAMES-APPLICATION-TARGETS",
        claim="For JOB APPLICATIONS only, a policy he ratified at his own console names the targets by rule, and that satisfies OPERATOR-NAMES-THE-TARGET; APPLY-FLOW-IS-THE-APPLICATION still holds, and every other outward act (messages, connects, posts, InMail) still needs a target he names.",
        binds="live proofs and automated runs -- job applications under a ratified policy",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) RATIFIED-POLICY-NAMES-APPLICATION-TARGETS",
        note="Orchestrator's lead ruling L1 (12:22) on the operator's 'yes, automate max' (11:39, 2026-11-26). Amends OPERATOR-NAMES-THE-TARGET for job applications only. Moves no row today: no policy for LinkedIn applications has been ratified. Reopener: none stated.",
    ),
    Ruling(
        id="J-114-SPLITS",
        claim="J 114 splits under COMPOUND-ROW-SPLITS-ONLY-ON-STATE on the J 110 -> J 168 precedent: the built facet stays J 114, and the unbuilt facets take the next free numeric id, GAP, next step C-RJ26-1.",
        binds="census row J 114 and its unbuilt facets (J 169)",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) J-114-SPLITS",
        note="Orchestrator's call on lane readers-jobs26's Q1; applied in its second round (J 114 COVERED-UNFIRED, J 169 entered GAP). Reopener: none stated.",
    ),
    Ruling(
        id="HIS-OWN-TEXT-AT-RUNTIME",
        claim="A tool may return text he authored or uploaded on his own account (his resume file names, his job-alert keywords) to his own session at runtime; fixtures synthetic, never in tracked files, tests, CI or console logs; one narrow door in the tool-envelope ratchet, with a control that third-party text stays refused.",
        binds="tool results -- his own text, at runtime",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) HIS-OWN-TEXT-AT-RUNTIME",
        note="Orchestrator's call on lane readers-jobs26's Q2; applied in its second round as the ADMITTED_OWN_TEXT door. Reopener: none stated.",
    ),
    Ruling(
        id="APPLICATION-SETTINGS-WRITE",
        claim="The two switches on his application settings page are admitted in principle as his own settings, a reversible on/off pair behind the grant, proven by a live round trip; the build is deferred to the first build lane after integration 4.",
        binds="writes -- his application settings switches",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) APPLICATION-SETTINGS-WRITE",
        note="Orchestrator's call on lane readers-jobs26's Q3. Built by lane build-jobs2 (J 74, J 76, P M7, P M8 COVERED-UNFIRED; the write door's excusal on the spec, WRITE-DOOR-EXCUSAL-ON-THE-SPEC) and merged in integration 6. Reopener: none stated.",
    ),
    Ruling(
        id="UNFOLLOWED-RAW-DELETED",
        claim="The kept raw capture of his unfollowed page, which held 44 members' names, is deleted by the orchestrator in both its copies; the skeletons are kept.",
        binds="live-lane state -- a raw capture holding people",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) UNFOLLOWED-RAW-DELETED",
        note="Orchestrator's call on lane readers-net26's section 9, question 1. An action on gitignored state; moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="PEOPLE-GATE-COUNTS-NAME-SLOTS",
        claim="The live lane's people gate, in its next version, counts name slots as well as profile links before a raw capture is kept.",
        binds="live captures -- the people gate on raw pages",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) PEOPLE-GATE-COUNTS-NAME-SLOTS",
        note="Orchestrator's call on lane readers-net26's section 9. Specified at 14:05 as six rules (people gate v2), before session 12. Built by lane infra26 as scripts/people_gate.py (rule N1, with the six rules as R1 to R6), merged in integration 5; the live lane wires it into its runner. Reopener: none stated.",
    ),
    Ruling(
        id="RECEIVED-BADGE-IS-THE-READS-COST",
        claim="Reading his received invitations clears the pending-invitation badge; that is recorded as the read's passive cost and stated in the tool's docstring, while the sent tab and the following list keep withholding on a badge drop.",
        binds="reads -- his received invitations, and the badge",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) RECEIVED-BADGE-IS-THE-READS-COST",
        aliases=("RECEIVED-BADGE-IS-THE-READ'S-COST",),
        note="Orchestrator's call on lane readers-net26's section 9, question 2 (the linkedin_notifications precedent). The orchestrator's own spelling carries an apostrophe and is kept as the alias. Applied by the lane. Reopener: none stated.",
    ),
    Ruling(
        id="REINVITE-BY-CALLER-COMPOSITION",
        claim="N 6 is discharged by CALLER-COMPOSITION-UNDER-D6 on linkedin_sent_invitations and linkedin_connect_from_profile, COVERED-UNFIRED; LinkedIn's re-invite cooldown is honoured because Connect is pressed only where drawn, and Connect stays outward, at named targets only.",
        binds="census row N 6 -- a re-invitation",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) REINVITE-BY-CALLER-COMPOSITION",
        aliases=("Q-REINVITE-COMPOSITION",),
        note="Orchestrator's call on the lane-K ledger's question; applied by lane readers-net26's second round. Reopener: none stated.",
    ),
    Ruling(
        id="REFOLLOW-FROM-HIS-NAMED-PROFILE",
        claim="A re-follow is built from the member's own profile he names by link (N 34's route); the unfollowed list is a read and a veto only, never a target source.",
        binds="census rows N 40, M C52 -- following a member again",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) REFOLLOW-FROM-HIS-NAMED-PROFILE",
        aliases=("Q-REFOLLOW-AIM",),
        note="Orchestrator's call on the lane-K ledger's question; applied by lane readers-net26's second round (both rows read SIBLING N 34). Reopener: none stated.",
    ),
    Ruling(
        id="AD-HIDE-AT-HIS-NAMED-AD",
        claim="Hiding an ad is allowed under HIS-OWN-CURATION-NOT-OUTWARD for an ad he names (an urn a reader returned to him that he hands back); the tool never picks an ad, the undo is captured on the first supervised fire, and Report ad stays outward.",
        binds="census row N 200 -- hiding an ad",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) AD-HIDE-AT-HIS-NAMED-AD",
        aliases=("Q-AD-HIDE-TARGET",),
        note="Orchestrator's call on the lane-K ledger's question; applied by lane readers-net26's second round (N 200 BUILD behind the grant). Its aim is held by AD-HIDE-AIM-HELD (17:10): no reader returns an ad urn without pressing ads he did not name. Reopener: none stated.",
    ),
    Ruling(
        id="AD-DATA-GRAIN",
        claim="The five grouped Advertising data rows (P P10 to P P14) are kept; they split per setting only when their pages are admitted and their states diverge (COMPOUND-ROW-SPLITS-ONLY-ON-STATE).",
        binds="census rows P P10 to P P14 -- their grain",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) AD-DATA-GRAIN",
        note="Orchestrator's call on lane readers-net26's section 9, question 4, applying GRAIN-FOLLOWS-WHAT-THE-PLATFORM-DRAWS. No cell changed. Reopener: a row's pages admitted and its settings' states diverging.",
    ),
    Ruling(
        id="PRESS-GATE-MAY-READ-TO-DECIDE-SELF",
        claim="Where the URL alone no longer decides self or other (a member profile root with no marker), the press gate may make its own read-only count of edit links before any press; a caller-supplied reading stays refused, and where the URL decides, the gate still refuses before touching the page.",
        binds="press gate -- deciding his own profile",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) PRESS-GATE-MAY-READ-TO-DECIDE-SELF",
        note="Orchestrator's call on lane selfprofile26's question 1; the one narrowed row of test_a_refused_press_never_touches_the_page stands under it. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="MESSAGE-SEARCH-CAPTURE-FIRST",
        claim="A capture first measures whether his inbox search lands on an address of its own; if it does, the search is composed under D1-SEARCH-AS-READS with no typing; only if not, a new sanctioned shape SEARCH-BOX-TYPING, anchored to a labelled search input and refusing if focus reaches a composer or a send control enables.",
        binds="census row M M34 -- searching his inbox",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) MESSAGE-SEARCH-CAPTURE-FIRST",
        aliases=("Q-MESSAGE-SEARCH-TYPING",),
        note="Orchestrator's call on the lane-K ledger's question; applied by lane readers-msg26's second round as a next step. Reopener: none stated.",
    ),
    Ruling(
        id="SCHEDULED-LIST-AS-A-SHIPPED-READ",
        claim="His scheduled posts list is a shipped read: the post composer opened empty, Schedule post, then View all scheduled posts; the list read (zero only on a drawn empty headline), closed with nothing typed or scheduled, no draft verified, and a stop on any autosave sign.",
        binds="census row M C14 -- his scheduled posts",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) SCHEDULED-LIST-AS-A-SHIPPED-READ",
        aliases=("Q-SCHEDULED-LIST-PRESS",),
        note="Orchestrator's call on the lane-K ledger's question; applied by lane readers-msg26's second round (BUILD on its session-11 capture). Built by lane build-msg2 (M C14, linkedin_scheduled_posts) and merged in integration 6. Reopener: none stated.",
    ),
    Ruling(
        id="ARTICLE-COMPOSER-ONE-CAPTURE",
        claim="The article composer's closed controls are read in ONE capture with nothing typed: onboarding dismissed, then the author toggle, Manage, the embed control and Next, each read and closed; never Publish or Schedule; a draft's appearance recorded (its next step is deleting it), and a stop on any publishing control.",
        binds="captures -- the article composer's disclosures (M C44, M C46, M C50, M C78, M C81, P L3)",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) ARTICLE-COMPOSER-ONE-CAPTURE",
        aliases=("Q-ARTICLE-COMPOSER-DISCLOSURES",),
        note="Orchestrator's call on the lane-K ledger's question, applying ARTICLE-COMPOSER-CAPTURE; applied by lane readers-msg26's second round as capture C-MSG26-4. Reopener: none stated.",
    ),
    Ruling(
        id="CONVERSATION-MENU-PREVIEW-PRESS",
        claim="A sanctioned preview press opens the one options menu bound to the named conversation, reads the item's word, presses nothing inside and closes on Escape; the confirmed press re-reads and refuses on the inverse; Delete conversation, which has no inverse, is receipt-only behind the grant, on his explicit order for a named conversation.",
        binds="census rows M M26, M M27, M M29, M M31 -- a conversation's menu acts",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) CONVERSATION-MENU-PREVIEW-PRESS",
        aliases=("Q-CONVERSATION-MENU-STATE",),
        note="Orchestrator's call on the lane-K ledger's question (the similar-jobs trial-press precedent; the J 163 class for delete); applied by lane readers-msg26's second round (BUILD on its session-11 capture). Built by lane build-msg2 (M M26, M M27, M M29, M M31 COVERED-UNFIRED) and merged in integration 6. Reopener: none stated.",
    ),
    Ruling(
        id="NAVIGATION-CEILING-MADE-TRUE",
        status="AMENDED",
        claim="AMENDED 2026-11-26 by NAVIGATION-CEILING-PER-TOOL-CALL: the measured maximum is 5, not 3, reached by the job search's place fan-out alone, so that one tool declares an allowance capped at 5 and every other tool call keeps the ceiling of 3, enforced in goto, refusing a 4th. Original: MAX_NAVIGATIONS_PER_CALL is raised to the measured maximum, 3, and enforced in BrowserManager.goto by a per-call counter refusing a 4th; the README's 'One page load per tool call' is put right.",
        binds="code -- page loads per tool call",
        document="_audit/2026-11-26-rulings-integration-4.md",
        anchor="RULED: (orchestrator, 2026-11-26) NAVIGATION-CEILING-MADE-TRUE",
        note="Orchestrator's call on lane pace20's question 1. Built as amended by lane infra26 and merged in integration 5: three loads per tool call, enforced in LinkedInBrowser.goto, and the README's two statements put right. Moves no row. Reopener: none stated.",
    ),
    # INTEGRATION 5 (2026-11-26): the orchestrator's rulings of 16:45 to
    # 18:18, from its merge notes, quoted in their own document.
    Ruling(
        id="NAVIGATION-CEILING-PER-TOOL-CALL",
        claim="At most 3 page loads per MCP tool call: a fastmcp middleware arms a budget for each tools/call, goto counts only while one is armed and refuses the 4th load before making it, and code outside a tool call (the live runner, probes, direct test calls) is untouched; linkedin_search_jobs alone declares a fan-out allowance, one load per place, capped at MAX_LOCATIONS 5 and AST-pinned to its one call site; the people readers' loop bound is its own constant, 2.",
        binds="code -- page loads per tool call",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) NAVIGATION-CEILING-PER-TOOL-CALL",
        aliases=("NAVIGATION-CEILING-PER-CALL-WITH-ONE-DECLARED-FAN-OUT",),
        status="AMENDS NAVIGATION-CEILING-MADE-TRUE",
        note="Orchestrator's call on lane infra26's item 2: named NAVIGATION-CEILING-PER-CALL-WITH-ONE-DECLARED-FAN-OUT at 16:45 (the alias), final form at 17:12. Lane infra26's record calls it option (C). Built by that lane in two heads, both merged in integration 5, and held there in full: the middleware, the refused 4th load, the capped fan-out with its one-caller pin and a planted-second-caller control, a test that every registered tool passes through the middleware, and the people bound. The lead's four asks under it are orders, not rulings. It amends NAVIGATION-CEILING-MADE-TRUE, whose 'raise it to 3' rested on a measured maximum of 3 where infra26 measured 5. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="SEARCH-BOX-TYPEAHEAD-DISCLOSURE",
        claim="The search box's typeahead is a sanctioned disclosure shape over [role=search] input[aria-autocomplete] on an admitted page, refused at runtime unless exactly one is drawn; nothing is typed, only the recent-searches group is read (HIS-OWN-TEXT-AT-RUNTIME), people options are never read, and Escape closes it with the listbox verified gone.",
        binds="presses -- the search box's recent searches (N 95)",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) SEARCH-BOX-TYPEAHEAD-DISCLOSURE",
        note="Orchestrator's call for lane build-net2 (17:10), registered at integration 5. Measured by the orchestrator: exactly one such input on 62 of 175 fixtures, none on 113, never two. Built by that lane (N 95, linkedin_recent_searches) and merged in integration 6; its one entry is one shape (ONE-ENTRY-IS-ONE-SHAPE). Reopener: none stated.",
    ),
    Ruling(
        id="AD-HIDE-AIM-HELD",
        claim="N 200 stays GAP: no reader returns an ad urn without pressing ads he did not name, and pressing un-named ads' menus to search for one is declined.",
        binds="census row N 200 -- where a hidden ad's urn comes from",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) AD-HIDE-AIM-HELD",
        note="Orchestrator's call for lane build-net2 (17:10), registered at integration 5; option (b) declined. N 200 held at GAP by that lane, merged in integration 6. AD-HIDE-AT-HIS-NAMED-AD still stands: a hide fires only at an ad he names. The row's cells are build-net2's. Reopener: a measured disclosure shape for the ad control-menu trigger.",
    ),
    Ruling(
        id="FIFTH-SEARCH-TO-PEOPLE-LABELS",
        claim="Session 12's fifth search goes to the search-people-labels capture, whose All-filters button is drawn outside main.",
        binds="captures -- session 12's fifth search",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) FIFTH-SEARCH-TO-PEOPLE-LABELS",
        note="Orchestrator's answer to lane s12-prep's second call (17:45); applied in its round 2. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="MESSAGING-LINE-TO-SESSION-13-STANDBY",
        claim="The one queue line that carries M M34 (the inbox-search capture-first) and M M28 behind one receipt guard moves whole to session 13's standby, so session 12 needs no inbox read.",
        binds="captures -- the guarded messaging line, M M34 and M M28",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) MESSAGING-LINE-TO-SESSION-13-STANDBY",
        note="Orchestrator's answer to lane s12-prep's second call (17:45), and its acceptance of that lane's reading of it (18:18); X-0 is dropped with it. Applied in the lane's round 2. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="EDITOR-TYPEAHEAD-ONLY-ATTENDED",
        claim="C-B1a, the editor's typeahead, is captured only in a session he attends, so it stays out of an unattended session.",
        binds="captures -- the editor typeahead line, C-B1a",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) EDITOR-TYPEAHEAD-ONLY-ATTENDED",
        note="Orchestrator's answer to lane s12-prep's third call, as that lane's plan records it; the merge-notes entries do not carry it in words. The capture itself is EDITOR-TYPEAHEAD-SANCTIONED's (P A11, P A13, P A17 on C-B1a); this adds only when it runs. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS",
        claim="The newsletter page session 12 captures is one the lane picks at runtime from his own subscriptions, published by LinkedIn or an organisation and never by a person.",
        binds="captures -- the newsletter page's target",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS",
        note="Orchestrator's answer to lane s12-prep's fourth call (17:45); applied in queue line 32's plan cell. In session 12 NEWSLETTER-PUBLISHER-UNPROVEN held it: no kept reading proved a non-person publisher. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="MSG-THREAD-FOOTER-TO-L2",
        claim="The msg-thread-footer capture needs a conversation he names, so it runs in an L2 session once he names it.",
        binds="captures -- msg-thread-footer",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) MSG-THREAD-FOOTER-TO-L2",
        note="Orchestrator's answer to lane s12-prep's fifth call (17:45); applied in the line's session cell. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="BUDGET-ONE-ACCOUNT-40",
        claim="His account has ONE budget of 40 page loads per trailing 12 hours, shared by the live lane and the job pipeline; the live runner records every load in the pipeline's one pinned ledger before making it, with no copy and no second ledger, and a session starts only with 40 free, or shrinks its plan from the bottom of the rank.",
        binds="live lanes and the job pipeline -- page loads on his account",
        document="_audit/2026-11-26-rulings-integration-5.md",
        anchor="RULED: (orchestrator, 2026-11-26) BUDGET-ONE-ACCOUNT-40",
        note="Orchestrator's call (17:52), overridable by him; it closes the 15:36 open question and is the stricter reading of LIVE-BUDGET-40-LOADS. Two separate budgets only on his word. Folded into the session-12 plan by lane s12-prep; at 18:40 the orchestrator confirmed that the harness's own session file holds session rules, not an account count, so it is not a second ledger. Moves no row. Reopener: his word.",
    ),
    # INTEGRATION 6 (2026-11-26): the orchestrator's rulings of 19:25 to
    # 23:05, from its merge notes, quoted in their own document.
    Ruling(
        id="J-37-SPLITS",
        claim="J 37 splits on state: the list half stays J 37, COVERED-UNFIRED on linkedin_job_alerts; the manage half is a new row, J 170, at GAP with its next step BUILD.",
        binds="census rows J 37 and J 170 -- the job-alert manager",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) J-37-SPLITS",
        aliases=("Q-J37-SPLITS",),
        note="Orchestrator's answer to lane build-jobs2's question 1 (19:25), on COMPOUND-ROW-SPLITS-ONLY-ON-STATE and the J 114 / J 169 precedent; applied by that lane's round 2 and merged in integration 6. The population moved 775 -> 776 on its branch. Reopener: none stated.",
    ),
    Ruling(
        id="RECEIPT-RISK-IS-HIS",
        claim="The save switch's live round trip on his application settings may delete his stored resumes and answers, which is unmeasured, so it is never scheduled without his explicit order naming the direction.",
        binds="live proofs -- J 76 and P M7, the save switch",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) RECEIPT-RISK-IS-HIS",
        note="Orchestrator's answer to lane build-jobs2's question 2 (19:25). The rows stay COVERED-UNFIRED; the switch's preview prints the risk and reads his stored resumes before the press and after the restore. Reopener: his explicit order naming the direction.",
    ),
    Ruling(
        id="WRITE-DOOR-EXCUSAL-ON-THE-SPEC",
        claim="The write door's excusal for his application settings page is keyed by its address on the WriteSpec (exempt_substrings_at), and readonly.py and its boundary freeze stay untouched.",
        binds="code -- the write door's per-address excusal",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) WRITE-DOOR-EXCUSAL-ON-THE-SPEC",
        note="Orchestrator's answer to lane build-jobs2's question 3 (19:25), which gave it no id: \"The WriteSpec excusal is ACCEPTED, with readonly.py untouched.\" Merged in integration 6. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="J-160-RAW-ONLY-IF-THE-PEOPLE-GATE-KEEPS-IT",
        claim="J 160's capture of his career insights keeps a raw page only if PEOPLE-GATE v2 keeps it; otherwise the skeleton and the heading words by key.",
        binds="captures -- the career-insights page (J 160)",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) J-160-RAW-ONLY-IF-THE-PEOPLE-GATE-KEEPS-IT",
        note="Orchestrator's answer to lane build-jobs2's question 4 (19:25), which gave it no id; written into the career-insights line's save cell by that lane's round 2. J 160 stays GAP. Reopener: none stated.",
    ),
    Ruling(
        id="READER-LEAK-WRITER-UNDER-THE-PACE-QUEUED",
        claim="The reader-leak baseline's writer, which under the 20 s pace drives four server helpers into a 5 s timeout and regenerates truly only with the pace at zero, is queued for the guard's next owner.",
        binds="tooling -- the reader-leak baseline's writer",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) READER-LEAK-WRITER-UNDER-THE-PACE-QUEUED",
        note="Orchestrator's answer to lane build-jobs2's question 5 (19:25), which gave it no id. Nothing is built; integration 6 ran the baseline writers with LINKEDIN_MIN_INTERVAL_S=0. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="LIVE-FLAG-DENIES-LINKEDIN-MCP",
        claim="While the live-session flag is up, the user-scope guard denies every non-exempt LinkedIn MCP tool in every session (only server_info, cdp_status, logout and page_plugin_snippet pass), and the live lane drives LinkedIn through its runner only.",
        binds="live lanes -- LinkedIn MCP tools while a live session runs",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) LIVE-FLAG-DENIES-LINKEDIN-MCP",
        note="The 15:36 rule for the next live lane's brief, registered on the orchestrator's 20:36 answer to integration 5's first question. The guard is the job pipeline's, at user scope outside this repository. Session 12 drove LinkedIn through its runner. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="PLAN-PEOPLE-GATE-LINES-ARE-THE-LIVE-LINES",
        claim="For session 12 the live lane applies the people-gate lines of the session plan's section 6, which judge every page, and not lane infra26's generic one-line hand-off.",
        binds="live lanes -- the runner's people-gate lines",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) PLAN-PEOPLE-GATE-LINES-ARE-THE-LIVE-LINES",
        note="Orchestrator's answer (20:36) to integration 5's second question, which gave it no id. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="ONE-ENTRY-IS-ONE-SHAPE",
        claim="SEARCH-BOX-TYPEAHEAD-DISCLOSURE's one sanctioned-mutation entry is one sanctioned SHAPE, not one line: one drain function with exactly two call sites, the click that opens and the Escape that closes, so readonly.SANCTIONED_MUTATIONS holds two lines for it; every other key and every fill refused.",
        binds="presses -- the search box's typeahead (N 95)",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) ONE-ENTRY-IS-ONE-SHAPE",
        note="Orchestrator's answer to lane build-net2's question (about 20:00), recorded at 20:36, 21:46 and 21:55 and written in full in that lane's record; built and merged in integration 6. Reopener: none stated.",
    ),
    Ruling(
        id="NEWSLETTER-PUBLISHER-UNPROVEN",
        claim="No newsletter page is loaded until a reading proves its publisher an organisation or LinkedIn: of session 12's five kept readings three were person-published and two showed no publisher, so E12 was skipped and its load went to standby.",
        binds="captures -- the newsletter page's target",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) NEWSLETTER-PUBLISHER-UNPROVEN",
        note="Orchestrator's call in session 12 (22:02); it holds NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS to its own 'never a person'. Moves no row. Reopener: he names a newsletter (L2), or a reading proves an organisation or LinkedIn publisher.",
    ),
    Ruling(
        id="M-M28-SPLITS",
        claim="M M28 splits on state: the view half stays M M28, COVERED-UNFIRED on linkedin_archived_conversations; the restore half is a new row, M M54, at GAP with its next step a CAPTURE, its control never captured.",
        binds="census rows M M28 and M M54 -- archived conversations",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) M-M28-SPLITS",
        note="Orchestrator's answer to lane build-msg2's question 1 (22:33), on COMPOUND-ROW-SPLITS-ONLY-ON-STATE; applied by that lane's round 2 and merged in integration 6. Reopener: none stated.",
    ),
    Ruling(
        id="MEDIA-POST-SAME-REFUSAL",
        claim="linkedin_publish_post's audience refusal applies to a media post on the same composer, whose audience is unread, and perform's drain rule stands, so there is no upload after a press: M C3 and M C4, with M C6 and M C7, stay GAP and cite this ruling.",
        binds="census rows M C3, M C4, M C6, M C7 -- a post with media",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) MEDIA-POST-SAME-REFUSAL",
        aliases=("Q-MEDIA-POST-AUDIENCE",),
        note="Orchestrator's answer to lane build-msg2's question 2 (22:33). The lane-K ledger carries the question as Q-MEDIA-POST-AUDIENCE from integration 6, so the two rows' next step can cite it. Reopener: an audience the server can read.",
    ),
    Ruling(
        id="GROUP-POST-AUDIENCE-FROM-ITS-TRIGGER",
        claim="M C64's audience is read off the group page's own trigger, \"Start a public post\", on two conditions: the preview shows that label verbatim before the grant, and the act fires only on his explicit order for a group he names.",
        binds="writes -- a post in one group (M C64)",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) GROUP-POST-AUDIENCE-FROM-ITS-TRIGGER",
        note="Orchestrator's answer to lane build-msg2's question 3 (22:33); M C64 is COVERED-UNFIRED, receipt-only, merged in integration 6. Reopener: none stated.",
    ),
    Ruling(
        id="M-M31-READ-BY-COMPOSITION",
        claim="M M31's read half is the composition linkedin_open_thread(thread_id, allow_unread=True) under CALLER-COMPOSITION-UNDER-D6: it opens only a conversation he names, and opening marks it read, which is the read's cost.",
        binds="census row M M31 -- marking a conversation read",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) M-M31-READ-BY-COMPOSITION",
        note="Orchestrator's ratification (22:33) of lane build-msg2's question 4, which gave it no id. Reopener: none stated.",
    ),
    Ruling(
        id="READER-INVENTORY-BY-QUALIFIED-NAME",
        claim="The pinned inventory of readers outside dom.py matches a call to module.function, never to a bare name, so a same-named reader in another module cannot pass as wired.",
        binds="guards -- the readers-outside-dom inventory",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) READER-INVENTORY-BY-QUALIFIED-NAME",
        note="Orchestrator's answer to lane build-msg2's question 5 (22:33); built red first in that lane's round 2 (2 of 12 failed on the bare-name detector) and merged in integration 6. Reopener: none stated.",
    ),
    Ruling(
        id="FAILED-REPROOF-DEMOTES",
        claim="A COVERED-PROVEN row whose scheduled live re-proof fails moves to COVERED-UNFIRED, citing the failed load, until a fire re-proves it.",
        binds="census state -- rows whose re-proof fails",
        document="_audit/2026-11-26-rulings-integration-6.md",
        anchor="RULED: (orchestrator, 2026-11-26) FAILED-REPROOF-DEMOTES",
        note="Orchestrator's call (23:05), for M C41, in the shape of Q-RETIRED-ROUTE-ROWS; applied at integration 6 to M C41, whose re-proof, session 12's E1, refused at loads 1 and 2. CAPTURE-SHOWS-READER-BLIND-DEMOTES (integration 7) applies its shape to M C75, whose shipped reader read nothing on a live capture. Reopener: a fire that re-proves the row.",
    ),
    # INTEGRATION 7 (2026-11-27): the orchestrator's rulings of 12:35 to
    # 17:50 for the five wave-7 lanes and the live lane, from its merge
    # notes and the lanes' disk notes, quoted in their own document.
    Ruling(
        id="ADMIT-NOW-LANDING-IN-SESSION-14",
        claim="A wave-7 admission is made now, one anchored line in ONE commit with its census lines, red first; each admitted address gets one read-only landing-and-capture load in session 14, the first live session on a master carrying it; a failed landing check means the next integration reverts that admission; no row moves on an admission alone.",
        binds="admissions -- wave 7's landing checks (/my-items/saved-posts/, /learning/me/my-library/saved/)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) ADMIT-NOW-LANDING-IN-SESSION-14",
        note="Orchestrator's answer to lane msg7's question 1 (12:35). Its scope includes lane jobs7's J 175 admission, the Learning saved list (queue line C-LRN-3). The hashtag address was held by HASHTAG-ADMISSION-WAITS-FOR-A-REFUSING-BASIS. Reopener: a landing check that fails (the admission is reverted).",
    ),
    Ruling(
        id="SAVE-POST-UNDER-OWN-CURATION",
        claim="linkedin_save_post saves one feed item he names, behind the grant, in mark_not_interested's shape under HIS-OWN-CURATION-NOT-OUTWARD; the item is the caller's named target, never the page's; M C37 rides M C36's first live fire in session 14 (save, read the drawn Unsave, unsave), attended.",
        binds="writes -- saving a feed item he names (M C36, M C37)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) SAVE-POST-UNDER-OWN-CURATION",
        note="Orchestrator's answer to lane msg7's question 2 (12:35); built by that lane (M C36 COVERED-UNFIRED) and merged in integration 7. Reopener: none stated.",
    ),
    Ruling(
        id="FEED-UNFOLLOW-ROUTES-UNDER-D6",
        claim="N 37's unfollow is held on the feed (no press on the menu of an item he did not name, AD-HIDE-AIM-HELD's ground) and routed under D6: SIBLING to a shipped route for unfollowing a member he names if one exists, else a CAPTURE on his following list, network's surface, wave 8.",
        binds="census row N 37 -- unfollowing from the feed",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) FEED-UNFOLLOW-ROUTES-UNDER-D6",
        aliases=("Q-FEED-UNFOLLOW-AIM",),
        note="Orchestrator's answer to lane msg7's question 3 (12:35). Lane msg7 checked: no such route ships, so the step is the following-list capture. Reopener: none stated.",
    ),
    Ruling(
        id="CAPTURE-SHOWS-READER-BLIND-DEMOTES",
        claim="A COVERED-PROVEN row whose shipped reader reads nothing on a live capture of its own surface moves to COVERED-UNFIRED, citing the capture, until a fire re-proves it (FAILED-REPROOF-DEMOTES' shape); its new read is built red first with the old page kept as a control.",
        binds="census state -- rows whose reader is blind on a new capture (M C75, N 20, N 45)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) CAPTURE-SHOWS-READER-BLIND-DEMOTES",
        note="Orchestrator's answer to lane msg7's question 4 (12:35): M C75 demoted on session 12's server-driven /notifications/ capture (the shipped harvest read 0); N 20 and N 45 kept COVERED-UNFIRED with the evidence; the server-driven read built by that lane, session 5's 9 of 9 the control. Reopener: a fire that re-proves the rows (session 14).",
    ),
    Ruling(
        id="ARTICLE-EDITOR-PRESSES",
        claim="Three article-editor presses are session-14 capture specs: (a) Drafts in Manage, a read of his own lists; (b) Create newsletter, its form read with nothing typed and closed unsubmitted; (c) ATTENDED ONLY, a fixed placeholder title, Next, the publish settings read and closed without Publish, the draft deleted and verified absent; no Publish press is ever in the runner's closed list, and an unverifiable deletion is STOP-ALL.",
        binds="captures -- the article editor (M C44, M C46, M C47, M C50)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) ARTICLE-EDITOR-PRESSES",
        aliases=("Q-ARTICLE-MANAGE-DRAFTS", "Q-NEWSLETTER-CREATE-FORM", "Q-ARTICLE-NEXT-NEEDS-A-TITLE"),
        note="Orchestrator's answer to lane msg7's question 5 (12:35). M C46 rides M C44. Reopener: none stated.",
    ),
    Ruling(
        id="GROUP-SEARCH-MEASURED-ABSENT",
        claim="M C70, a search inside groups, is MEASURED-ABSENT on the two surfaces measured: the content search's All filters panel draws no group facet, and a group's own page draws no group-scoped search control.",
        binds="census row M C70 -- searching inside groups",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) GROUP-SEARCH-MEASURED-ABSENT",
        aliases=("Q-GROUP-CONTENT-SEARCH-ABSENT",),
        note="Orchestrator's answer to lane msg7's question 6 (12:35), under MEASURED-ABSENT-OR-PRECONDITION; applied by that lane. Reopener: a capture that draws a group facet or a group-scoped search control.",
    ),
    Ruling(
        id="COMMENTS-METRIC-NOT-ABSENT-ON-ONE-DROPDOWN",
        claim="M C39 is not MEASURED-ABSENT: one metric dropdown on one surface does not measure a capability; under D6 it is re-aimed to a post's own analytics, a CAPTURE, and stays GAP.",
        binds="census row M C39 -- comment analytics",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) COMMENTS-METRIC-NOT-ABSENT-ON-ONE-DROPDOWN",
        aliases=("Q-COMMENT-ANALYTICS-METRIC",),
        note="Orchestrator's answer to lane msg7's question 6, first half (12:35), which gave it no id; the id is integration 7's. CREATOR-IDEAS-NOT-ABSENT-ON-ONE-SURFACE rests on it. Reopener: none stated.",
    ),
    Ruling(
        id="HASHTAG-ADMISSION-WAITS-FOR-A-REFUSING-BASIS",
        claim="The hashtag page /feed/hashtag/ is not admitted: READ-PAST-AN-ACT-SUBSTRING's condition, the press gate still refusing every control, is unmet because SENSITIVITY_BASES matches /feed/ by containment and gives the page the feed's press basis; N 59 and N 60 keep their ADMIT step, and containment matching is a wave-8 design item.",
        binds="admissions -- the hashtag page (N 59, N 60)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) HASHTAG-ADMISSION-WAITS-FOR-A-REFUSING-BASIS",
        note="Orchestrator's answer (13:30) to lane msg7's hold on the hashtag admission's press-gate premise. Reopener: a refusing press basis for the page (wave 8's SENSITIVITY_BASES design item).",
    ),
    Ruling(
        id="SAVE-RECEIPT-NEEDS-A-CHANGE",
        claim="linkedin_save_post's receipt reads a change, never a presence: a baseline is read before the press, and saved is reported only on more saved regions than the baseline or on the menu flipping to Unsave; otherwise not_pressed, not_landed or unverified.",
        binds="receipts -- saving a feed item (M C36)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) SAVE-RECEIPT-NEEDS-A-CHANGE",
        note="Orchestrator's fix-round order (17:20) on the cold verifier's finding (a saved region drawn before the press read as performed); fixed red first by lane msg7 (7e9f61b) before the first live fire and merged in integration 7. FEED-CURATION-RECEIPT-NEEDS-A-CHANGE is its shape for N 154. Reopener: none stated.",
    ),
    Ruling(
        id="P-N22-SPLITS",
        claim="P N22 splits on state: the subscription half stays P N22, COVERED-UNFIRED on the closed-words read of his Manage Premium account page; the payments half is a new P id at GAP, its step ADMIT of a static named purchases address, never the page-drawn id.",
        binds="census rows P N22 and P N32 -- his Premium subscription and payments",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) P-N22-SPLITS",
        aliases=("Q-P-N22-SPLITS",),
        note="Orchestrator's answer to lane settings7's question 1 (12:55), option (a), under COMPOUND-ROW-SPLITS-ONLY-ON-STATE; applied by that lane: P N32 entered at GAP, its step ADMIT of /manage/purchases-payments/purchases/ under NAMED-SETTINGS-PAGES-RATIFIED. Reopener: none stated.",
    ),
    Ruling(
        id="VERIFICATION-DELETE-HELD",
        claim="P K7, deleting a verification, stays at RULING: the act has no inverse, is visible to others, and its first press may be the act itself. If the captured Delete declares a popup, an attended capture (press, read, Cancel) and then a build in J-19's refuse-until-captured shape; if not, it stays his.",
        binds="census row P K7 -- deleting a verification",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) VERIFICATION-DELETE-HELD",
        aliases=("Q-VERIFICATION-DELETE",),
        note="Orchestrator's answer to lane settings7's question 2 (12:55), option (b). Measured offline by that lane: the captured Delete declares no popup and no controlled dialog, so the row stays his. Reopener: his word, or a Delete that declares a popup.",
    ),
    Ruling(
        id="SELF-LOADER-WAITS-FOR-THE-REWRITE",
        claim="The self-profile loader and the press gate wait, bounded, for LinkedIn's client-side rewrite of /in/me/ to his member path (polling the address only), then run the edit-link structure check; red first on a fake page whose address changes after a delay.",
        binds="code -- loading his own profile at /in/me/",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) SELF-LOADER-WAITS-FOR-THE-REWRITE",
        note="Orchestrator's build order of 2026-11-26 22:21, after session 12's E1 refusal; not registered at integration 6 (an order answering no question), registered here because session 14's self-anchored lines wait on it. Built first by lane prof7 (self_profile.await_rewrite) and merged in integration 7. Reopener: none stated.",
    ),
    Ruling(
        id="SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH",
        claim="A link drawn on his own profile root is pressed, attended only, only when its target is EXACTLY the address the read boundary admits, including any constant query the admission carries, with the proven landed member read as me; any other query, parameter or fragment vetoes; a navigating press is a load; nothing typed or saved; closed and verified gone; the root read before and after.",
        binds="presses -- links on his own profile root (session 14)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH",
        aliases=("Q-SELF-ROOT-FORM-LINKS",),
        note="Orchestrator's answer to lane prof7 (13:00), amended at 13:10 to include an admitted constant query (\"My 'no query' meant no query the PAGE adds\"). Every such press goes through the one matcher EXACT-MATCH-REFUSES-ANY-WHITESPACE names. Reopener: none stated.",
    ),
    Ruling(
        id="KEY-SKILLS-ADD-HELD",
        claim="P S8's key-skill add is not built: the skills list draws no Show all and no control on its six items, so the add has no drawn inverse; the row is held at GAP with a session-14 attended capture of the skills section's own edit view, nothing saved.",
        binds="census row P S8 -- adding a key skill",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) KEY-SKILLS-ADD-HELD",
        note="Orchestrator's answer to lane prof7 on rank 102 (13:00). Reopener: none stated.",
    ),
    Ruling(
        id="CREATOR-IDEAS-NOT-ABSENT-ON-ONE-SURFACE",
        claim="P L7's post ideas are not MEASURED-ABSENT because one landing draws them 0 times: one surface is not a measurement of the capability (the M C39 ground, under D6); P L7 is re-aimed to a capture of the creator hub's own navigation, or a RULING if it shows the feature retired.",
        binds="census row P L7 -- creator post ideas",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) CREATOR-IDEAS-NOT-ABSENT-ON-ONE-SURFACE",
        note="Orchestrator's answer to lane prof7 on rank 111 (13:00). Reopener: none stated.",
    ),
    Ruling(
        id="VOLUNTEERING-FALLBACK-BOUNDARY",
        claim="His volunteering page's profileId comes only from his runtime argument, validated by shape and never stored or logged; the card link is pressed only on an exact match with the address formed from it, and the page never supplies the id.",
        binds="admissions and presses -- his volunteering page (P D24)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) VOLUNTEERING-FALLBACK-BOUNDARY",
        aliases=("Q-VOLUNTEERING-ID-FROM-HIS-ARGUMENTS",),
        note="Orchestrator's answer to lane prof7 (13:10); built now, red first, by that lane (volunteering_route.py and one anchored allowlist line) and merged in integration 7. It is VOLUNTEERING-BARE-SPELLING-FIRST's fallback. Reopener: none stated.",
    ),
    Ruling(
        id="EXACT-MATCH-REFUSES-ANY-WHITESPACE",
        claim="The exact match is ONE matcher (volunteering_route.exact_link_verdict) that never normalises its target: any character outside the printable ASCII range refuses, unsafe percent escapes refuse, the comparison is raw exact equality with no case fold, and only an admitted /in/me/ address counts; every session-14 root press imports it.",
        binds="code -- the exact match for a press from his profile root",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) EXACT-MATCH-REFUSES-ANY-WHITESPACE",
        note="Orchestrator's fix-round order (17:20) on the cold verifier's MAJOR (str.strip dropped the Unicode whitespace the URL parser keeps); fixed red first by lane prof7 (4f84353) and merged in integration 7. live-s13's session-14 reviewer re-checks it where the runner imports it. Reopener: none stated.",
    ),
    Ruling(
        id="KEYWORD-FIELDS-MEASURED-ABSENT",
        claim="N 93, the people search's keyword fields, is MEASURED-ABSENT: both open All-filters panels draw no text input, with a D6 note to the shipped keyword search rows and the facets.",
        binds="census row N 93 -- people-search keyword fields",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) KEYWORD-FIELDS-MEASURED-ABSENT",
        note="Orchestrator's answer to lane net7 (13:25); applied by that lane. Reopener: none stated.",
    ),
    Ruling(
        id="GROW-SUGGESTIONS-BY-ADMISSION-NOT-SCROLL",
        claim="His full People You May Know lists are reached by admitting /mynetwork/discovery-see-all/, its landing in session 14, never by a scroll: SCROLL-NOT-SANCTIONED stands.",
        binds="admissions -- the discovery see-all lists (N 62, N 97, N 98)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) GROW-SUGGESTIONS-BY-ADMISSION-NOT-SCROLL",
        note="Orchestrator's answer to lane net7 (13:25); the address admitted by that lane on one anchored line and merged in integration 7. Reopener: none stated.",
    ),
    Ruling(
        id="CONTACTS-PAGE-FROM-THE-SETTINGS-NAV",
        claim="N 32 and N 110 are re-aimed to his contact-syncing settings page, named by the settings navigation's own entry; lane settings7 admits it only if drawn and only if READ-PAST-AN-ACT-SUBSTRING's condition holds, the press gate refusing every control there.",
        binds="admissions -- his contact-syncing page (N 32, N 110)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) CONTACTS-PAGE-FROM-THE-SETTINGS-NAV",
        note="Orchestrator's answer to lane net7 (13:25), with the 13:21 condition and the 14:12 order to measure it; settings7 admitted /mynetwork/settings/manage-syncing with one exemption and measured no press basis there (14:32); net7 re-aimed both rows onto settings7's queue line. Reopener: none stated.",
    ),
    Ruling(
        id="CONNECTIONS-CONTROLS-MEASURED-ABSENT",
        claim="N 27 is MEASURED-ABSENT on three surfaces; N 24 moves the same way only if its spellings include the sort's value labels and the page draws no dropdown trigger.",
        binds="census rows N 24 and N 27 -- his connections list's controls",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) CONNECTIONS-CONTROLS-MEASURED-ABSENT",
        note="Orchestrator's answer to lane net7 (13:25). N 27 applied; N 24 stays GAP, its second condition failing (13 aria-expanded triggers in main), with a session-14 capture of its two pills. Reopener: none stated.",
    ),
    Ruling(
        id="RECEIVED-LEAF-ADMITTED-WITH-ITS-READER",
        claim="N 13's received-tab leaf, /mynetwork/invitation-manager/received/, is admitted together with its reader's landing check by the lane that owns the reader, red first: one reader is never split across two lanes.",
        binds="admissions -- the invitation manager's received leaf (N 13)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) RECEIVED-LEAF-ADMITTED-WITH-ITS-READER",
        note="Orchestrator's answer 6 to lane net7 (13:25), which gave it no id; the id is integration 7's. One anchored line, one pattern exemption excusing exactly invitation, and invitation_manager._RECEIVED_PATHS accepting the leaf. RECEIVED-LEAF-SERVES-THE-INVITATION-WRITES accepts the same tuple's widening onto N 15 and N 16. Reopener: none stated.",
    ),
    Ruling(
        id="RECEIVED-LEAF-SERVES-THE-INVITATION-WRITES",
        claim="The shared invitation_manager._RECEIVED_PATHS is accepted as built: the accept and ignore writes (N 15, N 16) proceed on /mynetwork/invitation-manager/received/, where LinkedIn now lands; the target stays the one the operator names, the grant and press gates are unchanged, and the widening is confined to the invitation manager.",
        binds="writes -- the invitation acts' landing veto (N 15, N 16)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) RECEIVED-LEAF-SERVES-THE-INVITATION-WRITES",
        note="Orchestrator's ruling (17:20) on the cold verifier's MAJOR on lane net7 (the write veto widened beyond answer 6's text); without it those writes could never fire. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="FEED-CURATION-RECEIPT-NEEDS-A-CHANGE",
        claim="linkedin_mark_not_interested's receipt reads a change, never a presence (SAVE-RECEIPT-NEEDS-A-CHANGE's shape): an Undo drawn anywhere on the page before the press does not read as the item hidden.",
        binds="receipts -- marking a feed item not interested (N 154)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) FEED-CURATION-RECEIPT-NEEDS-A-CHANGE",
        note="Orchestrator's order to lane net7 (17:50), red first, before N 154's first live fire, on lane msg7's finding of the same flaw in feed_curation.verification_verdict (17:47). Reopener: none stated.",
    ),
    Ruling(
        id="REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE",
        claim="A job search setting any argument the AI route refuses (a place, a filter, an offset or an employer) is refused before any load and any D1 search, naming the arguments and the retired classic route; the plain keyword search runs on the AI route.",
        binds="code -- linkedin_search_jobs' arguments on the retired classic route",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE",
        note="Orchestrator's answer to lane jobs7's question 4 (13:45); built red first (job_search_route.CLASSIC_ROUTE_RETIRED) and merged in integration 7. The job pipeline's located LinkedIn searches now refuse at once. Reopener: a capture showing the classic route serving again.",
    ),
    Ruling(
        id="JOB-ALERT-ROW-CONTROL-ATTENDED",
        claim="J 170's alert-row control is captured in session 14, attended: one row's control pressed once and read only, nothing typed or chosen, closed and verified gone, the alert manager read before and after with no change.",
        binds="captures -- one job alert's own control (J 170)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) JOB-ALERT-ROW-CONTROL-ATTENDED",
        aliases=("Q-J170-ROW-CONTROL",),
        note="Orchestrator's answer to lane jobs7's question 2 (13:45); queue line C-J170-1. Reopener: none stated.",
    ),
    Ruling(
        id="LEARNING-ROWS-SPLIT",
        claim="J 152, J 154 and J 156 each split on state where their halves are different capabilities: the captured half keeps the id and builds, the other half takes a new id with a CAPTURE step or, for J 154's saved list, an ADMIT of /learning/me/my-library/saved/ with its landing in session 14.",
        binds="census rows J 152, J 154, J 156, J 171, J 172, J 175 -- LinkedIn Learning",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) LEARNING-ROWS-SPLIT",
        aliases=("Q-LEARNING-SPLITS",),
        note="Orchestrator's answer to lane jobs7's question 3 (13:45), re-ruled at 14:05 for J 154 on the lane's hold (load 25 landed on the in-progress tab), under COMPOUND-ROW-SPLITS-ONLY-ON-STATE; applied by that lane and merged in integration 7. Reopener: none stated.",
    ),
    Ruling(
        id="J169-SPLITS-SENIORITY-REAIMED-UNDER-D6",
        status="AMENDED",
        claim="AMENDED 2026-11-27 by J169-BY-ITS-OWN-WORDS: J 169 keeps its own words' first two halves, and its seniority half is the new row, re-aimed under D6. Original: J 169's function half builds; its seniority half takes a new id at GAP, its step a CAPTURE of the AI job search's experience-level facet; it is not absent on one view.",
        binds="census rows J 169 and J 173 -- Premium Page Insights by seniority",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) J169-SPLITS-SENIORITY-REAIMED-UNDER-D6",
        aliases=("Q-J169-SENIORITY",),
        note="Orchestrator's answer to lane jobs7's question 1 (13:45); held by that lane (J 169 names no function half) and corrected at 14:05. Its D6 re-aim stands: J 173's step is the experience-level facet (C-J173-1). Reopener: none stated.",
    ),
    Ruling(
        id="J169-BY-ITS-OWN-WORDS",
        status="AMENDS J169-SPLITS-SENIORITY-REAIMED-UNDER-D6",
        claim="J 169 is headcount over time, notable alumni and openings by seniority, by its own words; it splits only if load 20 makes the first two buildable, the seniority half then a new row.",
        binds="census rows J 169 and J 173",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) J169-BY-ITS-OWN-WORDS",
        note="Orchestrator's corrected ruling (14:05) on lane jobs7's hold. Load 20 draws both: J 169 kept them (built, COVERED-UNFIRED) and J 173 entered at GAP. Reopener: none stated.",
    ),
    Ruling(
        id="JOB-OPENINGS-BY-FUNCTION-ADDED",
        claim="Job openings by function is a capability the census did not hold: a new J row, on load 20's Insights tab, distinct from J 114's headcount by function.",
        binds="census row J 174 -- job openings by function",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) JOB-OPENINGS-BY-FUNCTION-ADDED",
        note="Orchestrator's corrected ruling (14:05) on lane jobs7's hold; J 174 entered and moved to COVERED-UNFIRED on its own field by that lane. Reopener: none stated.",
    ),
    Ruling(
        id="J114-READS-ITS-OWN-TABLE",
        claim="The company Insights reader selects each table by its summary, never by its header words: Headcount growth by function feeds J 114, re-based on load 20, and Total job openings feeds J 174; red first on both pages.",
        binds="code -- the company Insights tab's function tables (J 114, J 174)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) J114-READS-ITS-OWN-TABLE",
        note="Orchestrator's ruling (14:30) on lane jobs7's finding that the shipped reader read the job-openings table as headcount; applied by that lane (J 114 stays COVERED-UNFIRED, re-based, with a CORRECTS / CORRECTED BY pair) and merged in integration 7. Reopener: none stated.",
    ),
    Ruling(
        id="J175-ADMISSION-PASSES-NO-ACT-SUBSTRING",
        claim="J 175's admission of /learning/me/my-library/saved/ stands only if the address passes no act substring of the write guard or the press gate (save the one to check); measured: none of the 33 forbidden substrings, none of the press gate's markers, and no press basis, so both sanctioned shapes are refused there.",
        binds="admissions -- his Learning saved list (J 175)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) J175-ADMISSION-PASSES-NO-ACT-SUBSTRING",
        note="Orchestrator's check (14:30), which gave it no id; the id is integration 7's. Measured by lane jobs7 on the shipped guards and held by tests/test_the_learning_saved_list_presses_nothing.py. Reopener: an act substring found in the address (the admission is reverted).",
    ),
    Ruling(
        id="J111-SPLITS-PRODUCTS-FROM-SERVICES",
        claim="J 111 splits on state: the Products half, built (linkedin_company_page_tab, tab=products), keeps J 111 at COVERED-UNFIRED; the Services half takes the next free J id at GAP, its step CAPTURE C-J111-1.",
        binds="census rows J 111 and J 176 -- a company Page's Products and Services tabs",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) J111-SPLITS-PRODUCTS-FROM-SERVICES",
        note="Orchestrator's ruling (15:51) for integration 7 to apply, under COMPOUND-ROW-SPLITS-ONLY-ON-STATE, so lane jobs7 was not reopened; applied at integration 7: J 176 entered (the Services tab). Reopener: none stated.",
    ),
    Ruling(
        id="INBOX-SEARCH-IS-NOT-A-D1-SEARCH",
        claim="M M34's typed inbox search is not a D1 search: it is a load if it navigates, typed under SEARCH-BOX-TYPING, people-gated; it returns to session 13 only if already built, else session 14.",
        binds="live lanes -- the inbox search (M M34)",
        document="_audit/2026-11-27-rulings-integration-7.md",
        anchor="RULED: (orchestrator, 2026-11-27) INBOX-SEARCH-IS-NOT-A-D1-SEARCH",
        note="Orchestrator's ruling for the live lane (13:35). SEARCH-BOX-TYPING is the shape MESSAGE-SEARCH-CAPTURE-FIRST contemplates. Moves no row. Reopener: none stated.",
    ),
    Ruling(
        id="FIXED-UI-LABEL-MATCH",
        claim="The people search's Actively-hiring filter is matched by its "
              "exact LinkedIn UI label, a fixed product string, with a control "
              "showing a near-miss label is refused.",
        binds="reads -- one search filter matched by its product label",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) FIXED-UI-LABEL-MATCH",
        note="Orchestrator's call; overridable. Decides N 82.",
    ),
    Ruling(
        id="GEOLOCATION-BY-D6",
        claim="No browser geolocation permission is granted; searching jobs "
              "near him moves under D6 on the shipped location-parameter "
              "search, by the row's own bar.",
        binds="census state -- searching from his current location",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) GEOLOCATION-BY-D6",
        note="Orchestrator's call applying D6-CAPABILITY-OVER-AFFORDANCE; "
             "overridable. Decides J 17.",
    ),
    Ruling(
        id="P-A9-CANNOT-DELIVER",
        claim="The additional name's visibility is COVERED-CANNOT-DELIVER on "
              "the P A2 / P A4 precedent: its two switches carry the same "
              "label, so no route can aim one; reopened when LinkedIn draws a "
              "distinguishing name.",
        binds="census state -- P A9",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) P-A9-CANNOT-DELIVER",
        note="Orchestrator's call; overridable. Measured on session 7's "
             "editor skeleton.",
    ),
    Ruling(
        id="P-D29-BUILT-BEHIND-THE-GRANT",
        claim="Adding a LinkedIn Learning certificate to his profile is built "
              "behind the grant under EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS "
              "and never live-proven unless he names a certificate to add.",
        binds="writes -- P D29",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) P-D29-BUILT-BEHIND-THE-GRANT",
        note="Orchestrator's call; overridable.",
    ),
    Ruling(
        id="SAFETY-REPORTS-STAY-MANUAL",
        claim="A harassment or safety report, an accusation filed through an "
              "off-product Help Center form, is not built: EXCLUDED-RULED, "
              "reopened when an in-product structured report exists or he "
              "names one.",
        binds="writes -- safety reports",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) SAFETY-REPORTS-STAY-MANUAL",
        note="Orchestrator's call; overridable. Decides N 152.",
    ),
    Ruling(
        id="OUTSIDE-THE-PRODUCT-PURPOSE",
        claim="A row whose capability serves neither his job search nor his "
              "professional presence is EXCLUDED-RULED, reopened when he asks "
              "for it -- unless its own cell shows it tunes his job "
              "recommendations or his search.",
        binds="census state -- rows outside the product's purpose",
        document="_audit/2026-10-10-rulings-ledger-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10, applying the operator's rule "
               "that every feature must serve the product's core purpose) "
               "OUTSIDE-THE-PRODUCT-PURPOSE",
        note="Orchestrator's call applying the operator's rule that every "
             "feature must serve the product's core purpose; overridable.",
    ),

    # LANE NP, 2026-10-10: the orchestrator's APPLICATION of the ruling above
    # to that same profile's own detail pages -- one address shape, for the
    # named segment only, behind the same grant and warning. Registered in its
    # own document, as the order said.
    Ruling(
        id="NAMED-PROFILE-DETAIL-PAGES",
        claim="The read of a profile he names includes that same profile's own "
              "detail pages (/in/<the same slug>/details/<section>/), one load "
              "per call, behind the same single-use grant and the same preview "
              "warning; any other slug and any non-details path stay refused.",
        binds="read boundary -- a third-party profile he names",
        document="_audit/2026-10-10-rulings-named-profile-detail-pages.md",
        anchor="RULED: (orchestrator, 2026-10-10, applying the operator's 08:01 "
               "YES to reading profiles he names)",
        note="Orchestrator's application of NAMED-PROFILE-READ-BEHIND-A-GRANT; "
             "overridable. Admitted for the four detail sections measured on his "
             "own profile; N 178 and N 65 wait on the Interests page's capture.",
    ),

    # LANE A'S QUESTIONS, RULED 2026-10-10 (registered by lane A from the
    # orchestrator's copy, byte-identical). Five rulings, one entry per id,
    # each anchored on its own RULED: line; the document's closing answers
    # cite rulings already registered and declare none.
    Ruling(
        id="RECEIVED-INVITATIONS-READ-STAYS-ADMITTED",
        claim="His received-invitations tab (N 13, N 14, N 19) stays admitted. "
              "A change a read makes to an invitation's seen state is a "
              "passive cost, recorded on those rows as UNMEASURED and reopened "
              "when a capture shows the sender can see it.",
        binds="read boundary -- his received invitations",
        document="_audit/2026-10-10-rulings-lane-a-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) "
               "RECEIVED-INVITATIONS-READ-STAYS-ADMITTED",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR, applying "
             "D5-PASSIVE-COST-IS-NOT-A-ROW; overridable.",
    ),
    Ruling(
        id="NAMED-SETTINGS-PAGES-RATIFIED",
        claim="Each settings page lane A admitted by its exact address in its "
              "own commit -- N 39, P P15 and /jobs/application-settings/ -- is "
              "within ONE-NAMED-SETTINGS-PAGE-AT-A-TIME; this is the second "
              "decision that one asks for, with HIS-OWN-SETTINGS-NOT-OUTWARD, "
              "and no pattern widens.",
        binds="read boundary -- his named settings pages",
        document="_audit/2026-10-10-rulings-lane-a-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) NAMED-SETTINGS-PAGES-RATIFIED",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable.",
    ),
    Ruling(
        id="CREDENTIAL-ADJACENT-STAYS-REFUSED",
        claim="His stored applicant sign-ins for other sites (P M9, J 77) are "
              "treated as credential-adjacent and stay refused -- an inference, "
              "held on purpose to be conservative -- reopened when a capture "
              "shows the page holds no credential or secret.",
        binds="read boundary -- stored applicant sign-ins for other sites",
        document="_audit/2026-10-10-rulings-lane-a-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) CREDENTIAL-ADJACENT-STAYS-REFUSED",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable. Rests on inference, not measurement.",
    ),
    Ruling(
        id="NAMED-ADDRESS-NEEDS-LOG-REDACTION",
        claim="A page whose address carries a person's or a publication's name "
              "(M C101's newsletter page) is admitted only after every log line "
              "that records a page load writes that route's address as a shape, "
              "never the slug; until the redaction is built and shown failing "
              "first, the row is GAP on that blocker.",
        binds="read boundary -- addresses that carry a name",
        document="_audit/2026-10-10-rulings-lane-a-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) NAMED-ADDRESS-NEEDS-LOG-REDACTION",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR, applying "
             "PEOPLE-DATA-MITIGATIONS; overridable.",
    ),
    Ruling(
        id="CONTENT-VERTICAL-NOT-ALL-RESULTS",
        claim="D2-SEARCH-VERTICALS-WIDENED does not reach the mixed "
              "/search/results/all/ page. The hashtag row M C93 is served under "
              "D6 by the content vertical, /search/results/content/?keywords="
              "<hashtag>, admitted by its own exact pattern under "
              "D1-SEARCH-AS-READS's three conditions with /all/ shown still "
              "refused; M C70 shares it, and post text returns under "
              "THIRD-PARTY-TEXT-AT-RUNTIME.",
        binds="read boundary -- the content search vertical",
        document="_audit/2026-10-10-rulings-lane-a-questions.md",
        anchor="RULED: (orchestrator, 2026-10-10) CONTENT-VERTICAL-NOT-ALL-RESULTS",
        note="Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; "
             "overridable.",
    ),
    # THE OPERATOR'S UPLOAD DECISION, REGISTERED 2026-10-10 BY LANE U. It was
    # made 2026-09-04 and landed in 615a5c4, and until this entry the register
    # had no line for it. NO COMMITTED SOURCE RECORDS HIS WORDS: the commit
    # and the decides document both report the decision in their authors' own
    # words, so it is registered on that record and on nothing more. Its
    # anchor is the decides document's section 1 heading, which is why the
    # date column prints 2026-09-20 -- the record's date, not the decision's.
    Ruling(
        id="FILE-UPLOAD-OPENED",
        claim="This server may upload a file from this machine: the operator "
              "opened file upload on 2026-09-04, in full -- profile photo, "
              "post media and message attachments. The browser's upload verb "
              "joined SANCTIONED_MUTATIONS in 615a5c4. "
              "The FILE-UPLOAD-UNSANCTIONED blocker retires and its rows do "
              "not: each still needs a performable verb and a captured file "
              "input on its own surface. No extension allowlist -- one would "
              "narrow his decision.",
        binds="writes -- uploading a file from this machine",
        document="_audit/2026-09-20-the-decides.md",
        anchor="DECIDED, 2026-09-04, BY THE OPERATOR. THE BLOCKER RETIRES; "
               "THE 15 ROWS DO NOT.",
        aliases=("FILE-UPLOAD-UNSANCTIONED", "the upload sanction"),
        note="THE OPERATOR'S decision, made 2026-09-04. No committed source "
             "records his words: it is recorded by 615a5c4 and "
             "_audit/2026-09-20-the-decides.md section 1, and registered on "
             "that record. The date shown is the record's, 2026-09-20.",
    ),
    # REGISTERED 2026-11-28 BY LANE BUILD28, on the orchestrator's order (its
    # rulings file of 19:35: "register a ruling ... Register it in your record,
    # in the shape build_rulings_index reads, and cite it from both readonly
    # entries").
    Ruling(
        id="RESUME-MENU-DOWNLOAD-SANCTIONED",
        claim="A tool or capture may open his own stored resume's card menu and "
              "press its Download item. It fetches his own file through P C8's "
              "transport (D4-NO-OWN-BROWSER-CONTEXT) and changes nothing on his "
              "account. Any sign that the item does more than download (a "
              "dialog, a share sheet, a state change) stops the act and is "
              "recorded.",
        binds="presses -- his stored resumes' Download item (J 72, P M4)",
        document="_audit/2026-11-28-build28.md",
        anchor="RULED: (orchestrator, 2026-11-28) RESUME-MENU-DOWNLOAD-SANCTIONED",
        note="Orchestrator's answer to lane build28's question 1 (19:35). Cited "
             "by both readonly.SANCTIONED_MUTATIONS entries for "
             "resume_files._press; the download stops on any sign of more than "
             "a download. Reopener: a sign recorded on a live fire.",
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
