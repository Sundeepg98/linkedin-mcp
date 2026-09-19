# BUILT-BUT-UNFIRED: THE WRITE ROWS WERE ALREADY BANKED. ZERO GAP ROWS MOVED.

Measured 2026-09-19, 14:05-14:15 by the box, at HEAD `744a1f4`.

**CORRECTS:** `_audit/_census/jobs.md` -- rows 103 and 104 were banked
COVERED-PROVEN on a PERFORMABILITY verdict quoted as though it were a live-fire
receipt; both move to COVERED-UNFIRED, and the slice's count block gains a delta
rather than a rewrite. Section 4 below holds the four readings.

**THE HEADLINE IS A NULL RESULT IN THE DIRECTION I WAS SENT, AND A DEFECT IN THE
OPPOSITE ONE.** I was sent to bank `COVERED-UNFIRED` on GAP write rows served by
the twelve shipped performable actions. **Every one of the twelve already has its
capability banked by an earlier wave.** No GAP row in the census is served by any
of them. **0 rows banked out of GAP; all 296 GAP rows left where they are.**

What I found instead, looking at the same twelve actions from the coverage side:
**two rows banked COVERED-PROVEN on evidence that does not say what the rows say
it says.** Both are corrected here, and both corrections move the campaign's
number DOWN.

---

## 1. THE PREMISE I WAS GIVEN, RE-MEASURED

| claim in the brief | measured | verdict |
|---|---|---|
| `writes.PERFORMABLE` holds 12 actions | 12, by import at 14:12 | CONFIRMED |
| `writes._NINE_REFUSALS` is empty | `len() == 0` | CONFIRMED |
| all 12 are wired as tools | 12 of 12 `def linkedin_<action>` in `server.py`; `set_open_to_work` 0, as expected | CONFIRMED |
| `set_open_to_work` is NOT performable | not in `PERFORMABLE`, `url_template is None`, no tool | CONFIRMED |
| "nobody banked it" | **FALSE.** 13 W rows COVERED-UNFIRED, 6 W rows COVERED-CANNOT-DELIVER, plus the jobs slice's own CP/CU rows | **REFUTED** |

Instrument: `venv/Scripts/python.exe` importing `linkedin_server.writes` and
enumerating `SANCTIONED_WRITES`; `grep -c "def linkedin_<action>"` over
`linkedin_server/server.py`. `tests/test_writes.py` holds 130 tests.

### The row-count denominators I could and could not reproduce

The brief states **181 W rows and 15 R+W rows at GAP**. I could not reproduce
either number and I am recording that rather than quoting one I did not take.

    GAP rows in the five census slices, measured 14:08   296
      jobs.md                  61     (its own frozen count block says 99)
      messaging-and-content    84
      network.md               88
      profile.md               63
      mcp-inventory.md          0     (a TOOL inventory; carries no capability rows)

    of the 296, W-marked                               159
    R+W / R/W marked                                     2
    carrying no R/W column at all (jobs.md)             61

    blocker-map.tsv, a FROZEN spine of 409 rows,
    state_today == GAP                                 310

    2026-09-03-linkedin-gap-blockers.md, summing the
    R/W cells of its 86 ranked blockers            R 125 / W 222

**Three sources, three different W counts, and none of them is 181.** The
denominators disagree because they are different sets: the
census `.md` files are today's rows, `blocker-map.tsv` is the 2026-09-03 frozen
set carrying today's state, and jobs.md's count block is a frozen block its own
slice deliberately does not rewrite.

**WHAT I ACTUALLY EXAMINED, stated exactly rather than generously:** all **222**
GAP rows that are W-marked, R+W-marked or carry no R/W column, one at a time,
listed by id and capability; plus a verb sweep over all **296** GAP rows for the
twelve action verbs (save, bookmark, apply, follow, connect, invite, message,
InMail, post, publish, comment, react, setting, profile, edit). The 74 R-marked
GAP rows were covered only by that sweep, which is correct for a write pass and
is the limit of this reading.

---

## 2. WHERE EACH OF THE TWELVE IS ALREADY BANKED

One row per action, with the slice and the state it is already in. This is the
table the brief's premise needs and that nothing in the repository held.

| # | action | already banked at | state |
|---|---|---|---|
| 1 | `save_job` | `jobs.md` row 43 | CP -- and it genuinely landed, see s5 |
| 2 | `unsave_job` | `jobs.md` row 44 | CU |
| 3 | `follow_company` | `network.md` row 46 / `jobs.md` row 103 | **CU / CP -- CONTRADICTORY, see s4** |
| 4 | `unfollow_company` | `network.md` row 48 / `jobs.md` row 104 | **CU / CP -- CONTRADICTORY, see s4** |
| 5 | `apply_job` | `jobs.md` row 59 | CP (fired live, did not submit) |
| 6 | `update_setting` | `profile.md` N2 | CU |
| 7 | `publish_post` | `messaging-and-content.md` C1 | CU |
| 8 | `comment_on_item` | `messaging-and-content.md` C25 | CU |
| 9 | `react_to_item` | `messaging-and-content.md` C32 | CU |
| 10 | `update_profile_field` | `profile.md` A8, A11, A13, A17, A19, A21 | CU (six fields) |
| | | `profile.md` A2, A4, A6 | COVERED-CANNOT-DELIVER |
| 11 | `send_invitation` | `network.md` row 1 | CU |
| 12 | `send_message` | `messaging-and-content.md` M1, M2; `network.md` row 155 | COVERED-CANNOT-DELIVER |

**Twelve of twelve.** The finding "built and nobody banked it" was true of the
LEDGER's narrative and false of the CENSUS's rows.

---

## 3. THE 222 WRITE-SIDE ROWS I DID NOT BANK, AND WHY

Every GAP row fails at least one of three tests. **The discriminator is not my
invention -- it is the census's own**, set by `network.md` rows 46 and 47:
*"Follow the company attached to a job posting"* is banked and *"Follow an
organization's Page from the Page itself"* stays GAP, on the stated ground
*"no `/company/` pattern"*. The same act at a different address is a different
row. I applied that uniformly.

### 3.1 WRONG OBJECT -- the action addresses a different kind of thing

| row | what it asks | the action people would reach for | why it fails |
|---|---|---|---|
| `M C36` / `M C37` | save / unsave a POST | `save_job` / `unsave_job` | `target_kind='job_id'`, `url_pattern ^.../jobs/view/\d{6,}/$`. A post is not a job |
| `M C26` | reply to a COMMENT | `comment_on_item` | gate requires exactly one `Text editor for creating comment` on the item permalink; a reply box is a different control, and no comment identifier is read anywhere |
| `M C34` | react to a COMMENT | `react_to_item` | gate requires exactly ONE reaction control on the permalink; the one drawn is the post's |
| `M M48` | react to a MESSAGE | `react_to_item` | `url_pattern` is `/feed/update/urn:li:<type>:<digits>/`; a message is not a feed item |
| `N 37`, `N 40`, `N 41`, `N 42` | follow / unfollow a PERSON | `follow_company` / `unfollow_company` | `target_kind` is `job_id` and `company_id`; a member is neither |

### 3.2 WRONG ADDRESS -- the capability exists, the route is not the shipped one

| rows | the address they need | the shipped pattern |
|---|---|---|
| `N 4`, `N 6`, `N 166` | a people-search result, the Sent manager, a group roster | `send_invitation`: `^https://www\.linkedin\.com/in/me/$` |
| `N 47`, `N 49` | `/company/<slug>/`, a skills Page | `follow_company`: `^.../jobs/view/\d{6,}/$` |
| `M M10`, `M M11`, `M M13` | `/messaging/thread/...` | `send_message`: `^.../messaging/compose/$` |
| `P A26`-`A29` | `/in/me/overlay/contact-info/` | `update_profile_field`: `^.../in/me/edit/intro/$` |
| `P B4`, `P C2`-`C6` | `/public-profile/settings` | see s6 -- ruled by the operator, not mine |
| `M M35`, `M M36`, `N 176`, `P N12` | other settings pages | `update_setting`: `^.../mypreferences/d/dark-mode/?$`, ONE address |
| `M C61`-`C68`, `C91`, `N 63`, `N 64`, `N 163`-`N 176` | `/groups/...` | not admitted; a live ruling elsewhere today |
| `M C57`, `C58`, `C92`, `N 181`-`N 193` | `/events/...` | not admitted |

`update_setting`'s own `residue` is why the settings family cannot be stretched:
*"TWO OF THE THIRTY-THREE ADDRESSES ARE ACCOUNT DESTRUCTION ... a setting has to
be admitted BY NAME or not at all."*

### 3.3 MISSING PARAMETER -- the right action, a thing its spec does not have

| row | asks for | the spec |
|---|---|---|
| `N 5` | a personalised note on an invitation | `linkedin_send_invitation(member, confirm_token)` takes no note parameter |
| `M C2` | choose the post's audience | `publish_post.audiences == {}` |
| `M C3`-`C9`, `C27`, `M M14`-`M M18` | photo, video, document, poll, GIF, files | `target_kind='post_text'` / `'item_and_text'`; no upload is sanctioned |
| `M C33` (already XR) | choose WHICH reaction | the toggle applies LinkedIn's unmeasured default |

These three are the `COVERED-CANNOT-DELIVER` SHAPE, not `COVERED-UNFIRED`. I did
not bank them, because my mandate was UNFIRED and because banking
CANNOT-DELIVER needs the refusal MEASURED, not inferred. **Flagged for whoever
owns those slices**: `PUBLISH-POST-AUDIENCE-PARAM` (1 row), `INVITE-NOTE-PARAM`
(1 row) and `MISSING-PARAM-MESSAGING` (1 row) are blocker names that already say
exactly this.

### 3.4 THE THREE I LOOKED AT HARDEST AND STILL LEFT GAP

**`P A14` (postal code), `P A15` (location display choice), `P A22` (primary
position).** These are intro-editor fields, and `update_profile_field` addresses
the intro editor. Six of their siblings (`A8`, `A11`, `A13`, `A17`, `A19`,
`A21`) are banked CU on the stated ground *"aimable by `label-for`"* /
*"aimable by `aria-label`"*; three others (`A2`, `A4`, `A6`) are
COVERED-CANNOT-DELIVER on a measurement that they are **unaimable**.

**THE MECHANISM, read at 14:28 rather than assumed.** `anchor_label_for` for
this action *"returns THE FIELD NAME, PER CALL"*, and `_live_control` checks
that name *"against THE LIVE CONTROL LIST, requiring exactly one match, on the
very page the write will act on"* -- and `perform` checks aiming FIRST, before
the write door, before the navigation, before any control is read. So for these
rows the question "would the gate refuse?" is decided entirely by whether the
field carries a matchable accessible name on that container.

`A14` and `A22` are **neither**. `linkedin_server.intro_fields.signature`
returns a TRI-STATE and both read `unknown`: no label matched, AND four controls
in that container have no accessible name at all, so the field may sit behind
one of them. The action's aiming branch *"refuses unless EXACTLY ONE control is
named as asked"* -- so whether it would refuse is **the thing that is not
known**. Banking CU would assert the gate would not refuse. **That assertion has
no measurement behind it, and it is exactly the inflation this wave was sent to
prevent. They stay GAP.** `A15` moved partly forward (`city` and
`country_region` read present) but those are `A13` and `A11`'s fields, already
banked; the display CHOICE control is still unidentified.

**A CORRECTION OWED TO THOSE THREE ROWS, REPORTED AND NOT EDITED** (they belong
to today's intro-editor pass, and rewriting another wave's cell is how
attribution is lost): all three end *"STILL A WRITE EITHER WAY -- it needs a
WriteSpec, a gate and a ruling."* **The WriteSpec and the gate exist.**
`update_profile_field` is in `PERFORMABLE`, holds
`url_template='https://www.linkedin.com/in/me/edit/intro/'`, an
`exempt_substring='/edit/'`, and ships. What those rows lack is a NAMEABLE
CONTROL, which is a narrower and more actionable blocker than the one written.
The state does not move; the reason should.

**`M M6` (send a message request).** `send_message` reaches the same compose
surface, and `M1` records it **fired live 2026-09-03 and refused at
`_recipient_gate`**. So `M6` is CANNOT-DELIVER-shaped, never UNFIRED. Its
assigned blocker is `MESSAGE-REQUESTS-SURFACE`, which names a surface while the
SEND half is already measured refusing. Reported, not moved.

---

## 4. THE DEFECT: TWO ROWS BANKED COVERED-PROVEN ON A PERFORMABILITY VERDICT

`_audit/_census/jobs.md` rows 103 and 104:

    | 103 | Follow a company   | CP | `linkedin_follow_company`;
    |     |   `2026-08-31-linkedin-perform.md:1318` -- "**PERFORMS** | verified
    |     |   by re-reading the followed list" |
    | 104 | Unfollow a company | CP | `linkedin_unfollow_company`; same table |

**`PERFORMS` in that document is a statement about the GATE, not about a fire.**
Four independent readings, all taken 14:18-14:22:

1. The table those rows quote is `## 29. THE THIRTEEN-ROW LEDGER`, whose stated
   subject is *"`writes.SANCTIONED_WRITES` holds thirteen actions"* and whose
   closing line is *"Rows 7-12 are the six refusals a caller can reach through a
   tool."* It is a refuses/performs ledger.
2. The same file's `## 10. THE LEDGER -- performable before, performable after`
   carries the identical verdicts under columns literally headed
   `before | after`.
3. **`apply_job` reads `PERFORMS` in that same ledger**, and `jobs.md` row 59
   records *"zero applications have ever landed."* So `PERFORMS` is
   demonstrably not a landing claim, by that slice's own row.
4. The receipts of the very document being cited, at `:1058-1059`, `:1462` and
   `:1794`: `confirm_tokens used 0`, `writes performed 0`, **"Nothing was
   fired."** A write cannot be performed without a confirm token.

There is no live-fire receipt for either action anywhere in `_audit/`. I
searched for one.

**AND `jobs.md` ALREADY KNEW THIS.** Its own section *"THE SECOND CORRECTION:
what 'live-fire' means for the three writes"* exists to separate a ledger
verdict from a fire, and applies it to three actions -- giving `unsave_job`
**NO. NEVER FIRED.** Rows 103 and 104 are the same error, two hundred rows later
in the same file, on the two actions that section did not cover.

**CORRECTED HERE: 103 and 104 move CP -> CU**, which is what the NETWORK census
slice has held all along in its rows 46 and 48. The two slices now agree.

    jobs.md state counts       CP 21 -> 19        CU 7 -> 9

Following `profile.md`'s convention, the frozen count block is **not
rewritten** -- a delta is recorded beneath it, because a count that silently
rewrites itself cannot be cited.

---

## 5. WHAT I DID NOT TOUCH, HAVING CHECKED IT

**`save_job` row 43, "the one write proven to land", STANDS.** The blanket
statements elsewhere in `_audit/` that no confirm token was ever used are scoped
to their own sessions: `_audit/2026-08-30-linkedin-undo.md:433` records a
redeemed save producing `newly_observed_save_label: "Unsave the job"` -- an ON
label that could only exist because a real save produced it. That is a landed
write and the row is right.

**`apply_job` row 59 STANDS.** It was fired live, end to end, and reported
honestly that it did not submit. Its row already carries the effect qualifier.

---

## 6. ONE FAMILY I REFUSED ON THE OPERATOR'S STANDING RULING

`P B4`, `P C2`, `P C3`, `P C4`, `P C5`, `P C6` and two siblings -- eight rows
under `FORBIDDEN-CLASS-FIX-LANDED` -- all sit at `/public-profile/settings`.
They are not mine and not cheap. `readonly.py` records the operator's ruling of
2026-08-31 at the `/mypreferences/d/dark-mode` entry: *"ONE NAMED PAGE AT A
TIME, NEVER THE FAMILY, NEVER A WILDCARD"*, and it names two pages deliberately
refused because admitting them *"would each have required `/settings/` to be
narrowed to buy one page, WHICH IS TRADING A STANDING REFUSAL FOR A SINGLE
READ."* `/public-profile/settings` contains `/settings`. **They stay GAP and
only he can revisit it.**

---

## 7. NOTHING WAS FIRED FROM THIS SEAT

    browser opened            0
    write tools called        0
    confirm_tokens minted     0
    grants minted             0
    writes flag               untouched
    page loads                0
    census rows moved out of GAP   0
    census rows corrected downward 2

---

## 8. A SHIPPED GUARD CAUGHT THREE DEFECTS IN THIS WAVE'S OWN COMMITS

`tests/test_a_correction_is_findable_from_the_claim.py` is the instrument and it
worked on the wave that thought it was being careful. Recorded because the
failures are more useful than the fix.

1. **The `CORRECTED BY:` back-pointer wrapped its reason onto the next line.**
   The guard's own design note says it: *"a DECLARATION is a line, not a
   phrase"*, and the reason must sit on the marker's own line. I wrote the
   marker correctly and then let the editor wrap it.
2. **The corrected rows cited their corrector by filename, in cells that also
   carry the word CORRECTED**, which mints a candidate pair in the REVERSE
   direction of the declared one. A declared pair runs corrector -> target; the
   corrected rows pointing back at their corrector is not a second correction.
   The cells now route through the DELTA note, which carries the declared
   citation, so a reader of row 103 is still one hop from the evidence.
3. **Two prose lines named another census slice by filename inside the
   two-line vocabulary window**, for a slice that was RIGHT all along and is
   being corroborated rather than corrected.

**THE HONEST LONG-TERM FIX FOR 2 AND 3 IS A `NOT_A_CORRECTION` ENTRY, AND IT IS
OWED RATHER THAN DONE.** That table lives in a `tests/` file. Staging one fires
`scripts/pre_commit_boundary_gate.py`, the hook refuses while the foreign reds
stand, and the standing ruling is that it is not bypassed -- one wave's finished
file is already held for exactly this reason. Rewording to avoid minting a FALSE
pair is not the same act as suppressing a real one: the real correction stays
declared, in both directions, by the marker pair the guard checks.

**GUARD STATE AFTER THIS WAVE: 4 untriaged candidate pairs and 1 marker without
a reason, every one of them in a file this wave never wrote** --
`2026-09-19-the-three-ruling-requests-ruled.md:4`, `jobs.md:201` (row 42, twice),
`network.md:436`, and `2026-09-19-search-admission-preconditions.md:184`.

---

## 9. THIS PASS IS THE CROSS-REFERENCE A FAILED INSTRUMENT ASKED FOR, AND THE
## DIRECTION OF THE JOIN IS WHY IT WORKED

`scripts/unbanked_row_sweep.py` is a **deliberately kept failed instrument** for
exactly this problem -- *"rows already built but still filed GAP"* -- and its
docstring records four designs, each convicted by its own control:

    1  cell-text signals      0 of 7   the census not knowing is the defect itself
    2  identifier matching    1 of 7   and that one was a FALSE match
    3  parameter matching     7 of 7   PASSING BY COINCIDENCE -- three job-search
                                       rows matched a MESSAGING tool on "filter"
    4  self-contradiction     9 candidates, 0 genuine

Its conclusion: *"The durable fix is not a detector, it is a discipline ... For
the backlog that already exists, the only method that has produced a correct
answer is a HUMAN cross-reference of the 42 tools against the GAP rows -- every
one of the ten instances above was found by a person reading the tree, none by a
machine."*

**THE WRITE HALF OF THAT CROSS-REFERENCE IS NOW DONE, AND SECTION 2 IS ITS
RESULT.** What made it tractable is the DIRECTION OF THE JOIN, and that is the
transferable part:

> **All four failed designs scanned the CENSUS -- 296 rows, no closed source to
> join against -- and tried to infer "this was built". This pass enumerated the
> CAPABILITY SOURCE instead: `writes.PERFORMABLE` is a CLOSED SET OF TWELVE,
> each with a spec, a `url_pattern` and a `target_kind`, and asked of each
> "where is this banked?" The denominator is twelve, not two hundred and
> ninety-six, and every one of the twelve resolves by hand.**

**IT DOES NOT GENERALISE TO READS AND THAT LIMIT IS THE POINT.** The join works
because the write side HAS a closed enumeration with addresses attached. There
is no `READABLE` frozenset; the read surface is an allowlist of patterns with no
one-to-one correspondence to capabilities, which is precisely why the four
census-scanning designs were tried in the first place.

**AND A GUARD IS OWED THAT WOULD HAVE CAUGHT SECTION 4 AUTOMATICALLY.** No
shipped test distinguishes `COVERED-PROVEN` from `COVERED-UNFIRED`: rows 103 and
104 passed `test_a_covered_row_names_the_artifact_that_covers_it.py` for three
weeks because they DID name an artifact -- the state was the wrong one, not the
citation. The missing check is *a `COVERED-PROVEN` row must cite a live-fire
receipt, not a performability verdict*, **and its positive control already
exists**: those two rows in their pre-correction form, which the check must be
shown failing on before it is admitted anywhere. Not built here, for the same
reason the `NOT_A_CORRECTION` entry is not: it is a `tests/` file and the hook
refuses while the foreign reds stand.

---

## 10. THE GATE: WHAT I RAN, AND WHAT I DID NOT

**I did NOT run the tree.** Naming that first, because the standing finding of
the day is that every wave reported a subset as the gate.

**WHAT I RAN, 14:24:18-14:32:24 by the box, single command:** every test file in
`tests/` that READS the audit corpus at runtime, enumerated rather than chosen --
`grep -rln "_audit" tests/*.py` filtered to the files that actually open, glob or
`git ls-files` it. **37 files.**

    2155 passed   4 failed   4 skipped   486.19s

**ALL FOUR FAILURES ARE FOREIGN TO THIS WAVE**, and each is attributed rather
than asserted:

| failure | whose |
|---|---|
| `test_a_correction_is_findable_from_the_claim::test_every_marker_names_one_document_and_carries_a_reason` | `2026-09-19-search-admission-preconditions.md:184`, not written here |
| `...::test_every_candidate_pair_is_declared_or_triaged` | 4 pairs, in `2026-09-19-the-three-ruling-requests-ruled.md`, `jobs.md` row 42 (twice) and `network.md:436` -- none of them this wave's prose; see s8 for the three that WERE |
| `test_ci_shard::test_the_timings_table_still_prices_most_of_the_suite` | a timings pin last touched `7bcbcc6`, 2026-09-05; this wave added no test file |
| `test_no_committed_identity::test_no_tracked_file_carries_a_real_identifier[_RECOVER_groups_admission.patch]` | **see below -- it is a SAFETY guard and it is live** |

The 4 skips are environmental: 3 `test_uploads` symlink skips (`WinError 1314`,
privilege not held) and 1 reader that does not exist yet by design.

**A SUBSET IS STILL A SUBSET.** These 37 files are the ones that can SEE a change
to `_audit/`, which is the only thing this wave changed -- no code, no test, no
script. That is the argument for the scope, not a claim about the tree.

### THE SAFETY RED, ROUTED WITH ITS MEASUREMENT AND ITS LIMIT

    _RECOVER_groups_admission.patch: 4 unallowed email hit(s), 0 declared

**MEASURED, 14:33:** the file is **UNTRACKED** -- `git ls-files --error-unmatch`
returns *"did not match any file(s) known to git"* -- and its mtime is
**14:22:50 today**. It did not exist in this tree at 14:18. **Nothing is
committed and nothing is published.**

**THE GUARD IS DOING EXACTLY WHAT IT WAS WIDENED TO DO.** Its `sweepable()`
docstring: *"TRACKED plus UNTRACKED-NOT-IGNORED. WIDENED 2026-09-01 ... A guard
against committing an identity has to see what is ABOUT TO BE committed;
sweeping only what already was makes its first true answer arrive one commit
late."* A `_RECOVER_*.patch` is a file staged for `git apply` -- precisely the
"about to be committed" case.

**AND THE STANDING RULE APPLIES: A RED ON THIS GUARD MEANS UNDECLARED, NEVER
REAL.** Four hits, all rendered by the guard as the same 25-character redaction,
which is the shape of ONE token repeated -- consistent with a synthetic address,
and not established as one. The repair is a declaration or a rename, not alarm.

**I CANNOT MEASURE ITS AUTHOR AND I AM NOT GOING TO INFER ONE.** `git log -1 --
<path>` returns nothing, because the file is untracked -- so the one command the
lead's own routing rule prescribes has no answer here. The filename and the
timing point at the groups admission work; **that is exactly the
inference-from-a-name that was recorded twice today as a routing error**, so it
is offered as a lead to verify and not as an attribution. Whoever holds that
patch should declare or rename the token before applying it.
