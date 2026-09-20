"""Classify the REASON behind every written-off census row by the KIND of fact it asserts.

WHY THIS EXISTS. A census cell that writes off a capability rests on a reason, and the
corpus spells several different kinds of thing exactly the same way. Only some of them
are stable:

  US-RULING     somebody here DECIDED this. Stale only when somebody re-rules it, and a
                re-ruling is a visible act. Durable.
  US-BOUNDARY   a fact about our own allowlist / denylist / forbidden substrings. Also
                ours -- but a ruling is a decision somebody defended and a BOUNDARY ENTRY
                IS A LINE SOMEBODY TYPED. It can be flatly wrong while looking settled.
  WORLD-FACT    a fact about what LinkedIn draws, offers, or has retired; about geography
                or policy; about another codebase or slice. Goes stale when LinkedIn
                ships, and nobody sends us a note.
  ACCOUNT-FACT  a fact about THIS operator's account -- what he holds, what it renders to
                him, what an action would spend. Goes stale when he changes something,
                and it is the kind most often mistaken for a capability limit.
  PROCESS-FACT  a refusal read off the LIVE MCP PROCESS rather than off the file. That
                measures a process, not a capability: a running server holds the
                allowlist it booted with, and this repo has caught one answering 58
                commits stale.

THE SPLIT THAT MATTERS is not four ways, it is two: US-RULING and US-BOUNDARY are OURS
and re-checkable by reading this tree, while WORLD-FACT, ACCOUNT-FACT and PROCESS-FACT
are CONTINGENT -- they depend on something outside the codebase, and NOTHING IN THE CELL
SAYS SO. `_audit/2026-09-20-the-contingent-writeoffs.md` names that class, measures that a
contingent write-off carrying a reopener is 15% still GAP against 91% for one carrying
none, and reports a conviction rate of 5 of 5: every contingent write-off yet found wrong
sat in the no-reopener set.

WHY US-BOUNDARY IS SPLIT OUT OF US-RULING, which is not a taxonomy preference but a
measured lesson: `_audit/2026-09-20-the-live-capture.md` s12.1 found `/jobs/alerts/`
ALLOWED by our own gate and redirecting away to an address sixteen enumerated guesses had
missed -- wrong for fifteen days while looking settled. Billing that as "decided" is
false. A boundary entry is cheap to re-check (read one file) and cheap to get wrong, which
is the worst combination to leave unmarked.

IT IMPORTS THE SHIPPED PARSE RATHER THAN REPARSING. `cells`, `classify`, `ROW`,
`HEADERS`, `SLICES` come from `count_census_states`; `slice_text` from
`enumerate_gap_rows`. Four waves reimplemented that parse on 2026-09-05 and three got a
broken one. The blind spots are inherited and stated rather than hidden: a row whose state
cell is prose is invisible here exactly as it is there, and `count_census_states
--unstated` remains the only way to see those.

=============================================================================
THE THING THAT MAKES THIS HARDER THAN A KEYWORD SWEEP, MEASURED BEFORE IT WAS DESIGNED
=============================================================================

127 of the 309 write-off reason cells -- 41% -- ARE NOT REASONS. They are POINTERS.
`network.md`'s median write-off reason cell is FOURTEEN CHARACTERS. Six dialects, all of
which must be RESOLVED before any word in the cell can be classified:

  1. BACKREFERENCE   `same`, `same gate`, `same ruling`, `same measurement`.  46 cells.
                     Resolves to the nearest PRECEDING row in the same table whose cell is
                     substantive, and the chain is TRANSITIVE: `P D17` -> `D16` -> `D15`
                     -> `D14`, which is where the argument finally is.
                     THIS IS THE MOST FRAGILE CONSTRUCT IN THE CORPUS. It resolves BY
                     POSITION, so a row inserted above it silently re-points it, and
                     nothing marks a cell as load-bearing for the rows beneath it.
  2. RULING CODE     `R4. NOT-REV`, `R1 + R2`, `R2`.  `network.md` only.
                     Resolves to that file's own `### R<n> -- ...` ruling section.
                     THE HEADING IS NOT ENOUGH and using it would have been wrong:
                     `### R3 -- endorse_or_recommend` reads as a fact about our own tool,
                     while R3's BODY argues LinkedIn draws no endorsement line for this
                     account -- an ACCOUNT-FACT. The body is what gets classified.
  3. RETIREMENT      `RETIRED 2026-09-05, `BLOCKER` (3.13)`. Carries its argument inline
                     and cites `decide-retire-rulings.md`, the one queue in this corpus
                     that gives every entry a REOPENER. No resolution needed.
  4. FAMILY RULING   `/edit/ family ruling`. Substantive as written.
  5. NAMED KEY       `delete_or_withdraw_anything`, `PERMANENTLY_FORBIDDEN["..."]`. A
                     complete reason to anybody who knows the codebase and invisible to a
                     keyword sweep. The key list is READ FROM `writes.py`, not hardcoded.
  6. SECTION HEADING `### K. Recommendations (10) -- all EXCLUDED-RULED under R3`, and
                     NOT ONE of `N 119`-`N 128` carries that attribution in any cell --
                     those rows have no note column to put it in. THE MOST INVISIBLE
                     DIALECT: a reader who lands on `N 126` from the blocker map sees a
                     capability, a state, and no argument at all. Scoped on a measured
                     fact rather than a guess -- exactly ONE heading in the whole census
                     cites an R-code without being a ruling heading itself, and `--check`
                     fails if that stops being true.

A cell classified without resolving these would put 127 rows in UNCLEAR and call 41% of
the corpus unclassifiable. That would be a fact about the instrument, not about the
census.

=============================================================================
FIVE DEFECTS THIS SCRIPT HAD, EVERY ONE CAUGHT BY MEASUREMENT AND NONE BY RE-READING IT
=============================================================================

Recorded because the standing law here is that every fresh instrument built in one session
had a bug on its first attempt. Two were found by a child's independent extraction and two
more by a cold mutation harness; the fifth is listed at the end of the rule section.

**0. A CONTROL THAT COULD NOT FAIL.** The per-file check's second half read
`unkinded = [r for r in sub if not r.kind]`, and `finalise` sets `r.kind = "UNCLEAR"` on an
empty kind set -- so `r.kind` is NEVER falsy and the branch was unreachable. It printed
"all 112 write-off rows carry a kind" and could never have said anything else. Replaced
with the invariant that actually broke: a row resolved through a pointer must carry at
least what it points at. Shown failing on 102 rows with inheritance disabled.

**0b. BACKREFERENCE INHERITANCE WAS SILENTLY DEAD.** The donor was recovered by re-parsing
the label `backref<-P D14` with a non-whitespace capture; every row key here contains a
space, so the capture stopped at `P` and the lookup missed. 46 rows never inherited a kind and simply
came out UNCLEAR, which is indistinguishable from a census that never wrote a reason.

**1. HEADING SCANNING MUST BE FENCE-AWARE.** `network.md` quotes OTHER documents' markdown
headings inside ``` fences: line 644 `### #7 -- connection invitations` sits inside R1's
quote block, and line 776 `### NOT RECOMMENDED ...` sits inside R9's. A scanner that does
not track fences ends R1's body at 644 and R9's at 776 -- TRUNCATING EACH RULING AT
EXACTLY THE QUOTE IT RESTS ON. The first draft did this. Both the R-ruling scan and the
section tracker are fence-aware now.

**2. 22 ROWS HAVE NO REASON CELL AT ALL, and "the last non-empty cell" silently returned
their STATE cell.** Two `network.md` tables ship four columns (`# | capability | R/W |
state`) with no note column: section G (`N 67`-`N 78`) and section K (`N 119`-`N 128`).
Taking the last cell uniformly made the reason of `N 120` the string `EXCLUDED-RULED`,
which classifies as nothing and would have been reported as an unreadable census rather
than as a row that CARRIES NO WRITTEN REASON. The reason cell is now identified as the
last non-empty cell AFTER the state cell, and a row with none is reported under its own
heading as NO-REASON-CELL -- which is a finding about the census, not a parse failure.

=============================================================================
THE RULE, STATED SO IT CAN BE ARGUED WITH
=============================================================================

Each signal below is a WORD-BOUNDARY regex tagged with the kind of fact it indicates.
Every pattern is tested against every row; there is deliberately NO first-match-wins,
because first-match-wins is how a corrected reason loses to a superseded one. The verdict
is the SET of kinds that fired, joined with `+`. An empty set is UNCLEAR.

A MULTI-KIND VERDICT IS A RESULT, NOT A FAILURE. `the-contingent-writeoffs.md` s3.6
measured four blockers carrying two reasons on DIFFERENT subjects, where a CODE reason had
later been corrected to an ACCOUNT or WORLD one and the name kept the superseded half. A
classifier that silently picks one of two subjects reproduces that bug at row scale. And
`WORLD-FACT+ACCOUNT-FACT` is a real and common shape -- a product that exists only in some
geographies, read by an account in one of them.

WHY A SUBSTRING SWEEP WAS REJECTED. The same document measured its own first pass matching
`"has no"` inside `"has none"` and `"not a"` inside `"not at all"`, one boilerplate
sentence contributing ~33 rows of pure artifact; word-boundary regexes removed 33 and added
0. Every pattern here is anchored, and every row reports WHICH signals fired, so the rule
can be convicted at the pattern rather than argued about at the verdict.

=============================================================================
DERIVED, WITH A PINNED HAND OVERLAY -- AND WHY NOT THE OTHER TWO DESIGNS
=============================================================================

  (a) A HAND-WRITTEN TABLE of 309 classifications. Rejected: stale the day after it is
      written, unauditable, and this corpus is already full of them -- s4.1 of the
      contingent-writeoffs document found four of six hand-written locators dead and one
      landing on a DIFFERENT row that read COVERED-PROVEN, so a reader checking a GAP found
      a covered row and stopped.

  (b) THE TAG IN THE CELL, so it moves with the row. Rejected on two grounds. Mechanically,
      it means editing 309 rows across four census files while sibling waves are writing
      those same files -- a guaranteed conflict, corrupting attribution for work that is not
      mine. But the real reason is that AN IN-CELL TAG IS STILL HAND-MAINTAINED: written
      once against the reason that was there that day. When a sibling rewrites the reason --
      which happens constantly; `M C52` carries the words "CORRECTED 2026-09-19 BY THE WAVE
      THAT GOT IT WRONG, SECOND TIME TODAY" -- the tag does not follow, and a WRONG tag that
      travels with the row is worse than no tag, because it looks maintained.

  (c) DERIVED + PINNED ADJUDICATION. Chosen. The rule re-runs over whatever the cells say
      today, so the mass tracks the text for free. Where the rule refuses, a committed
      adjudication supplies the kind BY ROW ID -- never by line number, because s4.1
      measured every one of six line-number locators drifting 48 to 51 lines -- and each
      adjudication carries a VERBATIM QUOTE from the cell it rules on.

      THE QUOTE IS THE WHOLE MECHANISM. `--check` fails if a pinned quote no longer occurs
      in that row's resolved text. When somebody rewrites a reason out from under a hand
      ruling, the ruling goes RED AND LOUD instead of silently mislabelling the row. That is
      the one property (a) and (b) cannot have: a hand judgement that INVALIDATES ITSELF
      when its evidence moves.

=============================================================================
THE RE-CHECK TRIGGER, WHICH IS THE POINT OF THE WHOLE EXERCISE
=============================================================================

A classification that only labels rows goes stale as silently as the reasons it labels. So
every CONTINGENT row is also reported with whether it carries a mechanical re-check
trigger -- a `REOPENER:` clause naming the condition that falsifies it. `has_reopener` x
`contingent` is the re-examination list: a write-off resting on a fact about him or the
world, with nothing that would ever tell anybody it had changed.

CONTROLS. `--check` asserts PER FILE, never over the union: a union assertion over a
redundant corpus cannot detect a lost source, and if `network.md` stopped being read the
union would still be satisfied by the other three slices. An EMPTY result is a LOUD event,
because an assertion satisfied by an empty result cannot fail.

    python scripts/classify_writeoff_reasons.py --check
    python scripts/classify_writeoff_reasons.py --tsv out.tsv
    python scripts/classify_writeoff_reasons.py --show UNCLEAR
    python scripts/classify_writeoff_reasons.py --contingent
    python scripts/classify_writeoff_reasons.py --explain "J 134"
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import count_census_states as ccs        # noqa: E402  (the shipped instrument)
import enumerate_gap_rows as egr         # noqa: E402  (its shipped enumerator)

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADJUDICATIONS = ROOT / "_audit" / "_census" / "reason-kind-adjudications.tsv"

#: The states this script calls a WRITE-OFF. Long and short spellings both, because the
#: shipped counter reports `XR` and `CANNOT-DELIVER` under their own keys precisely so a
#: downstream artifact cannot silently merge them. GAP is NOT here: a GAP row is not
#: closed, so it owes no reason and cannot carry a stale one.
WRITEOFF = frozenset({
    "EXCLUDED-RULED", "XR",
    "MEASURED-ABSENT",
    "COVERED-CANNOT-DELIVER", "CANNOT-DELIVER",
})

ADMIN_ONLY = re.compile(r"A\d+")
HEADING = re.compile(r"^(#{2,6})\s+(.*)$")
FENCE = re.compile(r"^\s*(```|~~~)")

OURS = ("US-RULING", "US-BOUNDARY")
CONTINGENT_KINDS = ("WORLD-FACT", "ACCOUNT-FACT", "PROCESS-FACT")
KINDS = OURS + CONTINGENT_KINDS

# --------------------------------------------------------------------------------------
# THE SIGNAL TABLE
# --------------------------------------------------------------------------------------
_SIGNALS_RAW: list[tuple[str, str, str]] = [
    # ---- US-BOUNDARY: a line somebody typed in our own allow/deny lists ---------------
    ("allowlist",            "US-BOUNDARY", r"(?i)\ballow[- ]?list\b|_ALLOWED_URL_PATTERNS"),
    ("denylist",             "US-BOUNDARY", r"(?i)\bdeny[- ]?list\b"),
    # The census writes this list three ways -- "forbidden substring", "forbidden
    # tuple", "forbidden-substring list". `P M1`/`M2`/`M4`-`M7` and `P N29` say "the FIRST
    # entry on the forbidden tuple" and read as UNCLEAR until the spelling was widened.
    ("forbidden-substring",  "US-BOUNDARY", r"(?i)forbidden[- ](?:substring|tuple|list)"
                                            r"|_FORBIDDEN_URL_SUBSTRINGS"),
    ("mutation-verb",        "US-BOUNDARY", r"(?i)mutation[- ]verb"),
    ("not-on-allowlist",     "US-BOUNDARY", r"(?i)not (?:on|admitted)\b.{0,24}\b(?:allow|admit)"),
    ("admitted-by-name",     "US-BOUNDARY", r"(?i)admitted by name|by name or not at all"),
    ("boundary",             "US-BOUNDARY", r"(?i)\bboundary\b"),
    # Addresses that ARE the boundary entry. `P D7` and `P E8` write the whole reason as
    # one of these and nothing else, which read as UNCLEAR until they were added.
    ("settings-family",      "US-BOUNDARY", r"(?i)settings[- ]family|/psettings/"
                                            r"|/mypreferences/d/categories/"),

    # ---- US-RULING: a decision somebody here defended ---------------------------------
    ("src:readonly.py",      "US-RULING",   r"readonly\.py"),
    ("src:writes.py",        "US-RULING",   r"writes\.py"),
    ("src:server.py",        "US-RULING",   r"server\.py"),
    ("src:shape/dom",        "US-RULING",   r"\b(?:shape|dom|perform)\.(?:py|md)\b"),
    ("src:package",          "US-RULING",   r"linkedin_server"),
    # The first draft spelled this `the .{0,18}ruling\b`, which fired 157 times and made
    # US-RULING the default verdict for anything that used the word. Narrowed to the
    # spellings that name a ruling as the REASON rather than mentioning one in passing.
    ("ruling",               "US-RULING",   r"(?i)\b(?:family|shipped|same|own|settings)"
                                            r"\s+(?:ruling|refusal)\b"
                                            r"|\bthis repo's own\b|\bruling at\b"
                                            # "on the NEVER-LOADED ruling" is the census's
                                            # commoner spelling than "under the".
                                            r"|\b(?:on|under) the .{0,28}ruling\b"
                                            r"|NEVER-LOADED"),
    # The `/edit/` family ruling is cited by bare address on 8 profile rows.
    ("edit-family",          "US-RULING",   r"/edit/"),
    ("operator-ruled",       "US-RULING",   r"(?i)operator ruling|he re-rules|the operator ruled"),
    ("no-tool",              "US-RULING",   r"(?i)\bno tool\b"),
    ("no-reader",            "US-RULING",   r"(?i)\bno (?:reader|parser|route|pattern)\b"),
    ("not-built",            "US-RULING",   r"(?i)\b(?:not|never) built\b|deliberately not built"),
    ("nothing-builds",       "US-RULING",   r"(?i)nothing builds"),
    ("structurally",         "US-RULING",   r"(?i)structurally (?:unable|out of shape)"),
    ("unaimable",            "US-RULING",   r"(?i)accessible name|no aria-label|unaimable"),
    ("this-server",          "US-RULING",   r"(?i)\bthis server\b"),
    ("writespec",            "US-RULING",   r"WriteSpec"),
    ("name-freedom",         "US-RULING",   r"(?i)name[- ]freedom"),
    ("cannot-verify-send",   "US-RULING",   r"(?i)cannot report \"?sent\"?"
                                            r"|nothing here can verify a send"),

    # ---- ACCOUNT-FACT: this operator's account, holdings, entitlements ----------------
    ("this-account",         "ACCOUNT-FACT", r"(?i)\b(?:this|his) account\b"),
    ("for-him",              "ACCOUNT-FACT", r"(?i)\bfor him\b|\bto him\b"),
    ("he-holds",             "ACCOUNT-FACT", r"(?i)\bhe (?:has|had|holds|owns|never|wants)\b"),
    ("his-thing",            "ACCOUNT-FACT", r"(?i)\bhis (?:profile|network|connections|own|name)\b"),
    ("never-actioned",       "ACCOUNT-FACT", r"(?i)NEVER ACTIONED|has never used"),
    ("not-drawn-for",        "ACCOUNT-FACT", r"(?i)not drawn for|draws no .{0,40}\bfor this\b"),
    ("spends-a-credit",      "ACCOUNT-FACT", r"(?i)\bcredits?\b"),
    ("entitlement",          "ACCOUNT-FACT", r"(?i)premium[- ]gated|premium subscriber"
                                             r"|\bsubscription\b|\bentitle"),
    ("unverifiable-account", "ACCOUNT-FACT", r"(?i)unverifiable on this account"),
    ("operator-must-act",    "ACCOUNT-FACT", r"(?i)\bthe operator (?:names|moving|wants)\b"),
    ("his-locale",           "ACCOUNT-FACT", r"(?i)\bhis locale\b"),

    # ---- WORLD-FACT: LinkedIn, geography, policy, third parties, other code ----------
    ("help-centre",          "WORLD-FACT",  r"(?i)help (?:cent(?:er|re)|article|index)"
                                            r"|\bHelp article\b"),
    ("linkedin-says",        "WORLD-FACT",  r"LinkedIn (?:does not|draws no|offers|no longer"
                                            r"|cannot|makes|DRAWS NO|retired|redesigns)"),
    ("linkedin-learning",    "WORLD-FACT",  r"LinkedIn Learning"),
    ("geography",            "WORLD-FACT",  r"(?i)\bUS[- ]only\b|United States|India[- ]only"),
    ("mobile-only",          "WORLD-FACT",  r"(?i)\bmobile\b|desktop only"),
    # `third-party` was WORLD-FACT on the first draft and that was WRONG, measured: it
    # fired 50 times, 41 of them inside R4's body -- and R4 is `loading a third party's
    # profile is permanently forbidden`, which is OUR prohibition, not a fact about the
    # world. In this corpus the phrase almost always appears inside a refusal we wrote.
    ("third-party",          "US-RULING",   r"(?i)third[- ]party|another party's domain"
                                            r"|off[- ]domain"),
    ("served-by-skill",      "WORLD-FACT",  r"(?i)served by the skill|the skill's|\bthe skill\b"),
    ("sibling-slice",        "WORLD-FACT",  r"(?i)\bsibling slice\b|owned by .{0,20}slice"
                                            r"|another slice"),
    # Was `separate product` and never fired: the corpus writes "opens as a separate
    # LinkedIn Learning product in its own tab", with two words in between. A needle that
    # never fires and a fact that is never true look identical in a count.
    ("separate-product",     "WORLD-FACT",  r"(?i)separate\s+\S+(?:\s+\S+)?\s+product"),
    ("http-404",             "WORLD-FACT",  r"\b404\b"),
    ("needs-hardware",       "WORLD-FACT",  r"(?i)camera and microphone|real-time SPOKEN"
                                            r"|live audio session"),
    ("not-on-the-page",      "WORLD-FACT",  r"(?i)carries no balance|is not on the (?:page|composer)"
                                            r"|no such panel is drawn"),

    # ---- PROCESS-FACT: measured off a running process, not off the file --------------
    # The needle set is deliberately narrow. This class was added on the coordinator's
    # report of `0a7836f` ("the server that answered section 3 was 58 commits stale"), and
    # a wide pattern here would manufacture a category rather than find one.
    ("live-process",         "PROCESS-FACT", r"(?i)the live (?:server|mcp|process)"
                                             r"|the running server|commits stale"
                                             r"|the server that answered|as booted"
                                             r"|stale (?:mcp|server) process"),
]

#: A FIFTH POINTER DIALECT, found by reading the UNCLEAR bucket rather than by design.
#: 78 rows came back UNCLEAR on the first tightened run and most were not unclear at all:
#: they point at a `PERMANENTLY_FORBIDDEN` KEY BY NAME -- `delete_or_withdraw_anything`,
#: `PERMANENTLY_FORBIDDEN["endorse_or_recommend"]`, `a settings-family toggle` -- which is
#: a complete reason to anybody who knows the codebase and invisible to a keyword sweep.
#: The key list is READ FROM THE PACKAGE rather than hardcoded, so a tenth entry is picked
#: up without editing this file.
_FORBIDDEN_FALLBACK = (
    "repost_or_share", "endorse_or_recommend", "deanonymise_a_viewer",
    "load_a_third_partys_profile_to_measure_a_control",
    "delete_or_withdraw_anything", "mark_notifications_read",
    "auto_accept_or_auto_reply", "any_loop_sweep_or_scheduled_write",
    "any_anti_detection_technique",
)


def forbidden_keys() -> tuple[list[str], str]:
    """(the PERMANENTLY_FORBIDDEN key names, how they were obtained).

    AN EMPTY LIST IS NEVER RETURNED, and that is a safety property rather than tidiness:
    `"|".join([])` inside an alternation yields a pattern that matches the empty string at
    every position, which would silently tag all 309 rows US-RULING. Every failure path
    falls back to the nine names measured at `cd08e05` AND SAYS SO in the run header.
    """
    path = ROOT / "linkedin_server" / "writes.py"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return list(_FORBIDDEN_FALLBACK), "FALLBACK -- writes.py unreadable"
    m = re.search(r"PERMANENTLY_FORBIDDEN[^=]*=\s*\{(.*?)\n\}", text, re.S)
    if not m:
        return list(_FORBIDDEN_FALLBACK), "FALLBACK -- no PERMANENTLY_FORBIDDEN block"
    keys = re.findall(r'^\s{4}"([a-z_]+)":', m.group(1), re.M)
    if not keys:
        return list(_FORBIDDEN_FALLBACK), "FALLBACK -- block parsed but held no keys"
    return keys, f"read from linkedin_server/writes.py"


_FKEYS, FKEYS_SOURCE = forbidden_keys()
_SIGNALS_RAW.append(
    ("forbidden-key", "US-RULING",
     r"\b(?:" + "|".join(re.escape(k) for k in _FKEYS) + r")\b"))

SIGNALS = [(label, kind, re.compile(pat)) for label, kind, pat in _SIGNALS_RAW]


# --------------------------------------------------------------------------------------
# Row walking -- guard order copied verbatim from `enumerate_gap_rows.rows()`
# --------------------------------------------------------------------------------------
class Row:
    __slots__ = ("letter", "rid", "state", "lineno", "capability", "reason",
                 "section", "table_key", "resolved", "resolution", "signals",
                 "kinds", "kind", "source", "has_reason_cell", "backref_donor",
                 "inherited_kinds")

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def key(self) -> str:
        return f"{self.letter} {self.rid}"

    @property
    def contingent(self) -> bool:
        return bool(self.kinds & set(CONTINGENT_KINDS))


def split_reason(c: list[str]) -> tuple[str, bool]:
    """(reason cell, whether the row HAS one).

    The reason is the last non-empty cell AFTER the state cell. Identifying it by
    position-from-the-end alone was the first draft's bug: two `network.md` tables ship
    four columns with no note column, so the last cell IS the state cell there, and 22
    rows silently got the string `EXCLUDED-RULED` as their reason. A row with no cell
    after its state carries NO WRITTEN REASON, which is a finding about the census.
    """
    state_at = -1
    for i, cell in enumerate(c):
        if i == 0:
            continue
        bare = cell.replace("`", "").replace("*", "").strip()
        if bare.split(" ")[0] in ccs.STATES:
            state_at = i
            break
    if state_at < 0:
        for cell in reversed(c):
            if cell.strip():
                return cell.strip(), True
        return "", False
    for cell in reversed(c[state_at + 1:]):
        if cell.strip():
            return cell.strip(), True
    return "", False


def walk(ref: str | None = None) -> tuple[list[Row], list[str], dict[str, int]]:
    """Every stated row in the four slices, with its enclosing heading.

    Uses `ccs.classify` rather than `ccs.state_of` so a dialect cell is COLLECTED and
    reported rather than raising -- this script must be able to report on a census that
    has a defect in it, which is the state such a census is usually in.
    """
    rows: list[Row] = []
    dialects: list[str] = []
    stated: dict[str, int] = {}
    for letter, name in ccs.SLICES.items():
        section = ""
        table_key = f"{letter}:0"
        stated[letter] = 0
        prev_was_row = False
        in_fence = False
        for lineno, line in enumerate(egr.slice_text(name, ref).splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING.match(line)
            if m:
                section = m.group(2).strip()
                prev_was_row = False
                continue
            if not line.startswith("|"):
                # Prose or a blank line ENDS a table. Backreference resolution must not
                # cross that boundary: `same` means the row above IN THIS TABLE.
                if line.strip() == "" and prev_was_row:
                    table_key = f"{letter}:{lineno}"
                    prev_was_row = False
                continue
            c = ccs.cells(line)
            if len(c) < 3:
                continue
            if c[0] and set(c[0]) <= set("-: "):
                continue
            if not ccs.ROW.match(line) or c[0].lower() in ccs.HEADERS:
                continue
            st, found = ccs.classify(c)
            for spelling in found:
                dialects.append(
                    f"{letter} {c[0]} ({name} line {lineno}) spells a state "
                    f"{spelling!r}, which the shipped vocabulary does not hold")
            if not st and letter == "N" and ADMIN_ONLY.fullmatch(c[0]):
                st = "GAP"
            if not st:
                continue
            prev_was_row = True
            stated[letter] += 1
            reason, has_reason = split_reason(c)
            rows.append(Row(letter=letter, rid=c[0], state=st, lineno=lineno,
                            capability=c[1] if len(c) > 1 else "",
                            reason=reason, has_reason_cell=has_reason,
                            section=section, table_key=table_key,
                            resolved="", resolution="own-cell",
                            signals=[], kinds=set(), kind="", source="",
                            backref_donor="", inherited_kinds=set()))
    return rows, dialects, stated


# --------------------------------------------------------------------------------------
# Resolution pass
# --------------------------------------------------------------------------------------
BACKREF = re.compile(r"^\**same\b", re.I)
RCODE = re.compile(r"\bR(\d{1,2})\b")
REOPENER = re.compile(r"REOPEN(?:ER|S)\b", re.I)

#: A cell is SUBSTANTIVE if, once the pointer furniture is stripped, something is left to
#: classify. The threshold is published rather than tuned in private, and `--explain`
#: prints the residue for any row so the judgement can be checked by hand.
_FURNITURE = re.compile(r"(?i)\b(?:NOT-REV|REV|R\d{1,2}|same)\b|[`*.,;:+()\-\s]")
SUBSTANTIVE_MIN = 15


def residue(text: str) -> str:
    return _FURNITURE.sub("", text)


def is_substantive(text: str) -> bool:
    return len(residue(text)) >= SUBSTANTIVE_MIN


def rcode_rulings(ref: str | None = None) -> dict[str, str]:
    """Every `R<n>` ruling section in `network.md`, code -> body text.

    FENCE-AWARE, and that is not cosmetic: `network.md` quotes other documents' markdown
    headings inside ``` fences (line 644 inside R1's quote block, line 776 inside R9's).
    A scanner that does not track fences ends those two bodies at exactly the quote the
    ruling rests on.

    A heading may name more than one code (`### R10 / R7 -- ...`), so every code in the
    heading maps to the same body. A heading that merely MENTIONS a code in passing
    ("all EXCLUDED-RULED under R3") is a table section, not a ruling, so the heading must
    LEAD with its code.
    """
    lines = egr.slice_text(ccs.SLICES["N"], ref).splitlines()
    real_heading: dict[int, tuple[int, list[str]]] = {}
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if m:
            real_heading[i] = (len(m.group(1)), m.group(2))
    starts = []
    for i, (depth, text) in sorted(real_heading.items()):
        if re.match(r"^\s*R\d{1,2}\b", text):
            starts.append((i, depth, re.findall(r"\bR(\d{1,2})\b", text)))
    out: dict[str, str] = {}
    for i, depth, codes in starts:
        end = len(lines)
        for j in sorted(real_heading):
            if j > i and real_heading[j][0] <= depth:
                end = j
                break
        body = "\n".join(lines[i:end])
        for code in codes:
            out[f"R{code}"] = body
    return out


def cited_codes(c_line_cells: list[str]) -> list[str]:
    """R-codes cited anywhere from the R/W column rightwards.

    NOT the row id and NOT the capability text: `network.md` row ids are numeric, but a
    code can appear in the R/W cell (`N 125` reads `W (also R5)`) or inside the STATE cell
    (`N 67`-`N 78` read `EXCLUDED-RULED (R11)`), because those tables have no note column
    to put it in. Scanning only the reason cell misses 22 rows outright.
    """
    return sorted(set(RCODE.findall(" ".join(c_line_cells))), key=int)


def resolve(rows: list[Row], rulings: dict[str, str],
            codes_by_key: dict[str, list[str]]) -> list[str]:
    """Fill `.resolved` and `.resolution` on every row. Returns unresolved complaints."""
    problems: list[str] = []
    by_table: dict[str, list[Row]] = collections.defaultdict(list)
    # Backreference resolution walks ALL stated rows, not only write-off rows, because
    # `same` points at the row physically above it whatever state that row is in. A filter
    # applied before resolution would break exactly those chains.
    for r in rows:
        by_table[r.table_key].append(r)

    for r in rows:
        parts: list[str] = []
        how: list[str] = []

        if BACKREF.match(r.reason):
            siblings = by_table[r.table_key]
            pos = siblings.index(r)
            inherited = donor = ""
            for prev in reversed(siblings[:pos]):
                if is_substantive(prev.reason) and not BACKREF.match(prev.reason):
                    inherited, donor = prev.reason, prev.key
                    break
            if not inherited:
                problems.append(
                    f"{r.key} ({ccs.SLICES[r.letter]} line {r.lineno}) is a BACKREFERENCE "
                    f"({r.reason[:40]!r}) with no substantive row above it in its table")
            else:
                parts.append(inherited)
                r.backref_donor = donor
                how.append(f"backref<-{donor}")

        if r.letter == "N":
            for code in codes_by_key.get(r.key, []):
                name = f"R{code}"
                body = rulings.get(name)
                if body is None:
                    problems.append(
                        f"{r.key} ({ccs.SLICES[r.letter]} line {r.lineno}) cites {name}, "
                        f"which has no ruling section in network.md")
                else:
                    parts.append(body)
                    how.append(f"ruling<-{name}")

        parts.append(r.reason)
        r.resolved = "\n".join(parts)
        r.resolution = "+".join(how) if how else "own-cell"
    return problems


#: What MECHANICALLY re-checks a write-off of each kind, and what it costs. Keyed by the
#: kind rather than written per row, because a per-row list of 309 triggers is the
#: hand-maintained table this whole script exists to avoid.
#:
#: A CLASSIFICATION THAT ONLY LABELS ROWS GOES STALE AS SILENTLY AS THE REASONS IT LABELS.
#: The label says a row depends on something outside the codebase; only the trigger says
#: what would tell anybody it had changed. Ordered cheapest first, which is also the order
#: the re-examination list is printed in.
RECHECK = {
    "US-BOUNDARY": (0, "read the allow/deny list in `linkedin_server/readonly.py` and "
                       "confirm the substring or pattern still does what the cell says. "
                       "Zero page loads. CHEAP TO CHECK AND CHEAP TO GET WRONG -- "
                       "/jobs/alerts/ was ALLOWED and redirecting away for fifteen days"),
    "PROCESS-FACT": (1, "restart the MCP server and re-ask. A running server holds the "
                        "allowlist it booted with, so the refusal measured a process"),
    "ACCOUNT-FACT": (2, "one read on his own session, or one question to him. The fact "
                        "flips when he acquires, spends, toggles or receives something"),
    "WORLD-FACT":   (3, "one page load or one help-article fetch. The fact flips when "
                        "LinkedIn ships, and nobody sends a note"),
    "US-RULING":    (9, "nothing -- re-read the ruling. It changes only when somebody "
                        "re-rules it, which is a visible act"),
}


def recheck_of(r: Row) -> tuple[int, str]:
    """(cost rank, what would mechanically re-check this row). Cheapest kind wins.

    A row carrying several kinds is ranked by its CHEAPEST contingent kind, because the
    cheapest check is the one somebody will actually run, and if it settles the row the
    dearer ones are never needed.
    """
    # RANKED OVER ALL ITS KINDS, NOT ONLY THE CONTINGENT ONES. The row is on the list
    # because something about it is contingent, but the cheapest way to make progress may
    # be the OTHER half: `M C52`, `N 10` and `P N20` each carry a US-BOUNDARY alongside a
    # WORLD-FACT, and reading one file to find out whether the boundary is the binding
    # half costs nothing and may settle the row outright. Ranking on the contingent kinds
    # alone filed all three under "one page load", which is the dearer answer to a
    # question that has a free one.
    if not r.kinds:
        return (99, "nothing derivable -- the cell does not say what it depends on")
    rank, text = min((RECHECK[k] for k in r.kinds if k in RECHECK),
                     default=(99, "unknown kind"))
    return rank, text


def classify_own_cell(r: Row) -> None:
    """Derive a kind from the row's OWN words only.

    THE FIRST DRAFT CLASSIFIED `r.resolved` AND THAT WAS THE WRONG UNIT. A row whose whole
    reason cell is `R2` was being keyword-matched against R2's 926-character argument,
    which mentions an allowlist, a forbidden substring, LinkedIn and "his connections
    list" -- so it came out ACCOUNT-FACT+US-BOUNDARY+US-RULING, a three-kind verdict
    carrying no information. Measured: 87 of 309 rows had ZERO signals in their own cell
    and were classified entirely by inherited text.

    The unit of reasoning for those rows is the RULING, not the cell. Eleven rulings cover
    72 rows, so they are adjudicated ONCE by hand in
    `_audit/_census/reason-kind-adjudications.tsv` and the rows INHERIT that judgement --
    which is what the census itself means when it writes `R2` in a cell.
    """
    fired, kinds = [], set()
    for label, kind, pat in SIGNALS:
        if pat.search(r.reason):
            fired.append(f"{kind.split('-')[0][0]}{kind.split('-')[1][0]}:{label}")
            kinds.add(kind)
    r.signals = fired
    r.kinds = kinds
    r.source = "rule" if kinds else "none"


def finalise(r: Row) -> None:
    r.kind = "+".join(sorted(r.kinds)) if r.kinds else "UNCLEAR"


# --------------------------------------------------------------------------------------
# The pinned hand overlay
# --------------------------------------------------------------------------------------
class Adjudication:
    __slots__ = ("key", "kind", "quote", "why")

    def __init__(self, key, kind, quote, why):
        self.key, self.kind, self.quote, self.why = key, kind, quote, why


def load_adjudications(path: pathlib.Path = ADJUDICATIONS) -> list[Adjudication]:
    """Read the committed adjudications, or [] if none exists yet.

    ABSENCE IS NOT AN ERROR but it is REPORTED, because a silently-missing overlay would
    turn every adjudicated row back into UNCLEAR and look like the census got worse.
    """
    if not path.exists():
        return []
    out = []
    valid = set(KINDS) | {"UNCLEAR"}
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if parts[0].strip().lower() in ("row", "row_id", "key"):
            continue
        if len(parts) < 4:
            raise ValueError(
                f"{path.name} line {lineno}: expected 4 tab-separated fields "
                f"(row, kind, pinned_quote, why), got {len(parts)}")
        key, kind, quote, why = (p.strip() for p in parts[:4])
        for atom in kind.split("+"):
            if atom not in valid:
                raise ValueError(
                    f"{path.name} line {lineno}: kind {atom!r} is not one of "
                    f"{sorted(valid)}")
        out.append(Adjudication(key, kind, quote, why))
    return out


def check_pin(a: Adjudication, haystack: str, what: str) -> str | None:
    """'' if the pinned quote still holds, else the complaint.

    THIS IS THE ANTI-STALENESS MECHANISM AND THE ONLY REASON THE HAND LAYER IS SAFE.
    A hand judgement written against text that has since been rewritten is exactly the
    failure this whole wave is about, one level up: a label that looks maintained and is
    not. Pinning the judgement to a verbatim substring makes it self-invalidating.
    """
    if not a.quote:
        return None
    if a.quote in haystack:
        return None
    return (f"ADJUDICATION for {a.key} pins the quote {a.quote[:64]!r}, which is NO "
            f"LONGER PRESENT in {what}. The evidence moved out from under the "
            f"judgement -- re-read it before trusting the kind")


def apply_ruling_adjudications(rulings: dict[str, str],
                               adj: list[Adjudication]) -> tuple[dict[str, set], list[str]]:
    """(code -> adjudicated kinds, complaints). Every ruling must be adjudicated."""
    problems: list[str] = []
    kinds: dict[str, set] = {}
    by_key = {a.key: a for a in adj if a.key.startswith("RULING ")}
    for code, body in rulings.items():
        a = by_key.get(f"RULING {code}")
        if a is None:
            problems.append(
                f"RULING {code} has no adjudication. {sum(1 for _ in [1])} -- every "
                f"ruling section in network.md must be classified by hand, because rows "
                f"pointing at it inherit its kind and a keyword sweep over its body was "
                f"measured to be meaningless")
            continue
        bad = check_pin(a, body, f"the {code} ruling body in network.md")
        if bad:
            problems.append(bad)
            continue
        kinds[code] = set(a.kind.split("+")) & set(KINDS)
    for a in by_key.values():
        code = a.key.split(" ", 1)[1]
        if code not in rulings:
            problems.append(
                f"ADJUDICATION {a.key!r} names a ruling section that network.md no "
                f"longer has -- it was renamed, renumbered or removed")
    return kinds, problems


def apply_row_adjudications(rows: list[Row], adj: list[Adjudication]) -> list[str]:
    """Overlay row-level hand rulings; return complaints that should fail `--check`."""
    problems: list[str] = []
    index = {r.key: r for r in rows}
    for a in adj:
        if a.key.startswith("RULING "):
            continue
        r = index.get(a.key)
        if r is None:
            problems.append(
                f"ADJUDICATION for {a.key!r} names a row that is not a write-off row at "
                f"this ref -- it was renamed, removed, mistyped, or has left a write-off "
                f"state, in which case the judgement is moot and should be retired")
            continue
        bad = check_pin(a, r.resolved, f"{a.key}'s resolved reason")
        if bad:
            problems.append(bad)
            continue
        r.kinds = set(a.kind.split("+")) & set(KINDS)
        r.source = "adjudicated"
    return problems


def build(ref: str | None = None):
    rows, dialects, stated = walk(ref)
    rulings = rcode_rulings(ref)
    codes_by_key: dict[str, list[str]] = {}
    for letter, name in ccs.SLICES.items():
        if letter != "N":
            continue
        in_fence = False
        for line in egr.slice_text(name, ref).splitlines():
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence or not line.startswith("|"):
                continue
            c = ccs.cells(line)
            if len(c) < 3:
                continue
            codes_by_key[f"{letter} {c[0]}"] = cited_codes(c[2:])
    problems = resolve(rows, rulings, codes_by_key)
    adj = load_adjudications()
    ruling_kinds, rp = apply_ruling_adjudications(rulings, adj)
    problems += rp

    # Every row gets its OWN-CELL signals first, including non-write-off rows, because a
    # backreference donor may be any state and the dependent inherits from it.
    for r in rows:
        classify_own_cell(r)

    # INHERITANCE, in table order so a donor is final before its dependents read it.
    by_key = {r.key: r for r in rows}
    for r in rows:
        for code in codes_by_key.get(r.key, []) if r.letter == "N" else []:
            want = ruling_kinds.get(f"R{code}", set())
            r.inherited_kinds |= want
            r.kinds |= want
            if want:
                r.source = "inherit-ruling" if r.source == "none" else r.source

        # A SIXTH POINTER DIALECT, AND THE MOST INVISIBLE ONE. `network.md` section K is
        # headed "### K. Recommendations (10) -- all EXCLUDED-RULED under R3", and NOT ONE
        # of `N 119`-`N 128` carries that attribution in any cell -- those rows ship four
        # columns with no note column, so there is nowhere to put it. A reader who lands
        # on `N 126` from the blocker map sees a capability, a state, and no argument.
        #
        # Confirmed from two directions before it was implemented: R3's own body declares
        # `Rows: 111, 112, 113, 119-128` (13), while a token scan over every cell of every
        # row finds 4. The difference is exactly those ten.
        #
        # SCOPED NARROWLY ON A MEASUREMENT, not on a guess: of all headings in all four
        # slices, exactly ONE cites an R-code without being a ruling heading itself. The
        # control below fails if that stops being true, because a heading that merely
        # mentions a code in passing would silently repaint every row beneath it.
        if r.letter == "N" and not re.match(r"^\s*R\d{1,2}\b", r.section):
            for code in sorted(set(RCODE.findall(r.section)), key=int):
                want = ruling_kinds.get(f"R{code}", set())
                if not want:
                    continue
                r.inherited_kinds |= want
                r.kinds |= want
                if r.source == "none":
                    r.source = "inherit-heading"
                if "heading" not in r.resolution:
                    r.resolution = (f"heading<-R{code}" if r.resolution == "own-cell"
                                    else f"{r.resolution}+heading<-R{code}")
        # READ THE SLOT, NEVER RE-PARSE THE LABEL. The first version of this matched
        # `backref<-(\S+)` out of `r.resolution` -- and every row key in this corpus
        # contains a space (`P D14`), so the capture stopped at `P`, `by_key.get("P")`
        # returned None, and BACKREFERENCE INHERITANCE SILENTLY NEVER RAN for any of the
        # 46 rows that need it. It produced no error and no warning; it just left every
        # `same` row UNCLEAR, which looked exactly like a census that had not written a
        # reason. Found by the mutation harness (M7), not by reading this code.
        if r.backref_donor:
            donor = by_key.get(r.backref_donor)
            if donor is not None:
                r.inherited_kinds |= donor.kinds
                r.kinds |= donor.kinds
                if r.source == "none":
                    r.source = "inherit-backref"

    wo = [r for r in rows if r.state in WRITEOFF]
    problems += apply_row_adjudications(wo, adj)
    for r in wo:
        finalise(r)
    return rows, wo, dialects, stated, rulings, problems, adj


def write_tsv(path: pathlib.Path, wo: list[Row]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", errors="replace", newline="\n") as fh:
        fh.write("row\tstate\tkind\tcontingent\thas_reopener\thas_reason_cell\tsource\t"
                 "resolution\tslice\tline\tsection\tcapability\tsignals\treason\n")
        for r in wo:
            fh.write("\t".join((
                r.key, r.state, r.kind,
                "1" if r.contingent else "0",
                "1" if REOPENER.search(r.resolved) else "0",
                "1" if r.has_reason_cell else "0",
                r.source, r.resolution, ccs.SLICES[r.letter], str(r.lineno),
                r.section.replace("\t", " "), r.capability.replace("\t", " "),
                ";".join(r.signals), r.reason.replace("\t", " "),
            )) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Classify write-off reasons by kind of fact")
    ap.add_argument("--ref", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tsv", default="")
    ap.add_argument("--show", default="", help="print every row whose kind contains this")
    ap.add_argument("--contingent", action="store_true",
                    help="print the re-examination list: contingent, no reopener")
    ap.add_argument("--explain", default="")
    args = ap.parse_args(argv)

    rows, wo, dialects, stated, rulings, problems, adj = build(args.ref)

    if args.explain:
        for r in wo:
            if r.key == args.explain.strip():
                print(f"{r.key}  state={r.state}  {ccs.SLICES[r.letter]} line {r.lineno}")
                print(f"  section     : {r.section}")
                print(f"  capability  : {r.capability}")
                print(f"  reason cell : {r.reason if r.has_reason_cell else '(NO REASON CELL)'}")
                print(f"  residue     : {residue(r.reason)!r} "
                      f"(substantive={is_substantive(r.reason)})")
                print(f"  resolution  : {r.resolution}")
                print(f"  signals     : {', '.join(r.signals) or '(none fired)'}")
                print(f"  verdict     : {r.kind}  [{r.source}]  "
                      f"contingent={r.contingent}  "
                      f"reopener={bool(REOPENER.search(r.resolved))}")
                if r.resolution != "own-cell":
                    print(f"  resolved text ({len(r.resolved)} chars), first 1500:")
                    print("    " + r.resolved[:1500].replace("\n", "\n    "))
                return 0
        print(f"no write-off row with key {args.explain!r}")
        return 1

    print("WRITE-OFF REASON KINDS -- derived from the cells at "
          f"{args.ref or 'the working tree'}")
    print("=" * 96)
    print(f"stated rows per slice        : "
          f"{', '.join(f'{k}={v}' for k, v in stated.items())}")
    print(f"R-code ruling sections found : {len(rulings)} "
          f"({', '.join(sorted(rulings, key=lambda s: int(s[1:])))})")
    print(f"adjudications loaded         : {len(adj)}"
          f"{'  (NONE ON DISK -- overlay absent)' if not adj else ''}")
    # THE DOCSTRING PROMISED THIS LINE AND THE CODE DID NOT PRINT IT. `FKEYS_SOURCE` was
    # assigned once and read nowhere, while `forbidden_keys()` claimed every failure path
    # "SAYS SO in the run header". A reader of a FALLBACK run could not tell it was one --
    # which is the same half-truth this wave is auditing the census for, in my own
    # instrument. Found by the mutation child, not by me.
    print(f"PERMANENTLY_FORBIDDEN keys   : {len(_FKEYS)}  [{FKEYS_SOURCE}]")
    noreason = [r for r in wo if not r.has_reason_cell]
    print(f"write-off rows with NO REASON CELL AT ALL: {len(noreason)}")
    if noreason:
        print("   " + ", ".join(r.key for r in noreason[:40])
              + (" ..." if len(noreason) > 40 else ""))
    print()

    # PER FILE, never over the union.
    hdr = ["OURS(rule)", "OURS(bound)", "WORLD", "ACCOUNT", "PROCESS"]
    print(f"{'slice':30s} {'write-offs':>10s} "
          + " ".join(f"{h:>11s}" for h in hdr)
          + f" {'CONTING':>8s} {'UNCLEAR':>8s}")
    for letter, name in ccs.SLICES.items():
        sub = [r for r in wo if r.letter == letter]
        cnt = [sum(1 for r in sub if k in r.kinds) for k in KINDS]
        print(f"{name:30s} {len(sub):>10d} "
              + " ".join(f"{n:>11d}" for n in cnt)
              + f" {sum(1 for r in sub if r.contingent):>8d}"
              + f" {sum(1 for r in sub if r.kind == 'UNCLEAR'):>8d}")
    print("-" * 96)
    cnt = [sum(1 for r in wo if k in r.kinds) for k in KINDS]
    print(f"{'TOTAL (kinds overlap)':30s} {len(wo):>10d} "
          + " ".join(f"{n:>11d}" for n in cnt)
          + f" {sum(1 for r in wo if r.contingent):>8d}"
          + f" {sum(1 for r in wo if r.kind == 'UNCLEAR'):>8d}")
    print()
    print("exact verdicts (a row is counted once):")
    for k, n in collections.Counter(r.kind for r in wo).most_common():
        print(f"  {k:46s} {n:4d}")
    print()
    res = collections.Counter(r.resolution.split("<-")[0].split("+")[0] for r in wo)
    print(f"reason cells that needed RESOLUTION (a pointer, not a reason): "
          f"{sum(v for k, v in res.items() if k != 'own-cell')} of {len(wo)}")
    for k, v in res.most_common():
        print(f"  {k:24s} {v:4d}")

    cont = [r for r in wo if r.contingent]
    noreop = [r for r in cont if not REOPENER.search(r.resolved)]
    print()
    print(f"CONTINGENT write-off rows            : {len(cont)}")
    print(f"  ... carrying a REOPENER            : {len(cont) - len(noreop)}")
    print(f"  ... carrying NONE (re-examine list): {len(noreop)}")

    if args.contingent:
        print("\n--- RE-EXAMINATION LIST: contingent, and nothing would ever say it "
              "changed ---")
        print("Grouped by WHAT WOULD MECHANICALLY RE-CHECK IT, cheapest first. A "
              "classification\nthat only labels rows goes stale as silently as the "
              "reasons it labels.\n")
        last = None
        for r in sorted(noreop, key=lambda r: (recheck_of(r)[0], r.letter, r.lineno)):
            rank, trigger = recheck_of(r)
            if rank != last:
                import textwrap
                print(f"\n=== TIER {rank}: " + textwrap.fill(
                    trigger, 84, subsequent_indent="    ") + "\n")
                last = rank
            print(f"  {r.key:9s} {r.kind:34s} {r.state:22s} {r.capability[:44]}")

    if args.show:
        want = args.show.strip().upper()
        print(f"\n--- every write-off row whose kind contains {want} ---")
        for r in wo:
            if want in r.kind:
                print(f"{r.key:9s} {r.kind:34s} {r.section[:30]:30s} {r.capability[:46]}")
                print(f"          signals: {', '.join(r.signals) or '(none)'}")

    if dialects:
        print(f"\nDIALECT STATE CELLS: {len(dialects)}")
        for d in dialects:
            print(f"  {d}")
    if problems:
        print(f"\nPROBLEMS -- {len(problems)}")
        for p in problems:
            print(f"  {p}")

    if args.tsv:
        write_tsv(pathlib.Path(args.tsv), wo)
        print(f"\nwrote {args.tsv}")

    if not args.check:
        return 0

    failed = False
    print("\nCONTROLS")
    if not wo:
        print("  FAIL  the corpus yielded ZERO write-off rows. An empty result is a loud "
              "event here, never a silent pass")
        return 1
    print(f"  ok    corpus is non-empty ({len(wo)} write-off rows)")

    for letter, name in ccs.SLICES.items():
        sub = [r for r in wo if r.letter == letter]
        if not sub:
            print(f"  FAIL  {name} contributed ZERO write-off rows -- a slice that stopped "
                  f"being read looks exactly like a slice with nothing to say")
            failed = True
            continue
        # WHAT USED TO BE HERE COULD NOT FAIL, and it took a second reader to see it:
        #   unkinded = [r for r in sub if not r.kind]
        # `finalise` sets `r.kind = "UNCLEAR"` whenever the kind set is empty, so
        # `r.kind` is never falsy and that branch was unreachable. It printed
        # "all N write-off rows carry a kind" over 309 rows and could never have said
        # anything else -- a control computed, printed, and structurally unable to fire,
        # which is the exact defect `scripts/detect_unbranched_probe_controls.py` was
        # built to find in 129 other places.
        #
        # REPLACED WITH THE INVARIANT THAT ACTUALLY BROKE. A row that resolved through a
        # pointer must end up carrying AT LEAST what it points at. When backreference
        # inheritance was silently dead, 46 rows had a donor and none of the donor's
        # kinds; this assertion fails loudly in that state, and the tautology did not.
        broken = [
            f"{r.key} resolved through {r.resolution} but is missing "
            f"{sorted(r.inherited_kinds - r.kinds)}"
            for r in sub if not r.inherited_kinds <= r.kinds
        ]
        if broken:
            print(f"  FAIL  {name}: {len(broken)} row(s) resolved through a pointer and "
                  f"did NOT inherit what it points at")
            for b in broken[:4]:
                print(f"          {b}")
            failed = True
        else:
            inherited = sum(1 for r in sub if r.resolution != "own-cell")
            print(f"  ok    {name}: {len(sub)} write-off rows, {inherited} resolved "
                  f"through a pointer, all inheriting what they point at")

    # The heading-inheritance rule is scoped on a measured fact: exactly ONE heading in
    # the whole census cites an R-code without being a ruling heading. If that stops being
    # true, the rule starts silently repainting rows under headings that merely mention a
    # code in passing, so it is asserted rather than assumed.
    cite_headings = []
    for letter, name in ccs.SLICES.items():
        in_fence = False
        for lineno, line in enumerate(egr.slice_text(name, args.ref).splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = HEADING.match(line)
            if m and RCODE.search(m.group(2)) and not re.match(r"^\s*R\d{1,2}\b",
                                                               m.group(2)):
                cite_headings.append(f"{name}:{lineno} {m.group(2)[:60]}")
    if len(cite_headings) == 1:
        print(f"  ok    exactly 1 non-ruling heading cites an R-code, as measured: "
              f"{cite_headings[0]}")
    else:
        print(f"  FAIL  {len(cite_headings)} non-ruling headings cite an R-code; the "
              f"heading-inheritance rule was scoped to exactly 1 and must be re-read")
        for h in cite_headings:
            print(f"          {h}")
        failed = True

    if dialects:
        print(f"  FAIL  {len(dialects)} dialect state cell(s)")
        failed = True
    if problems:
        print(f"  FAIL  {len(problems)} unresolved pointer(s) or stale adjudication(s)")
        failed = True
    if not problems and not dialects:
        print("  ok    every pointer resolved and every adjudication still pinned")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
