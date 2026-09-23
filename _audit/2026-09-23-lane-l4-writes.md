claude-opus-5-5[1m]

# Lane L4 -- WRITES: classify the write-direction GAP rows, build the reversible first round to ready-to-fire

Written as the lane runs. Worktree branch `worktree-agent-a6aa0720780262d33`, cut from `master` at `b0d3ab8`.
Nothing in this lane touched LinkedIn: no browser was attached, no grant was issued, and
`writes_enabled()` stayed False in every process this lane started. Fixture tests drive a local
headless Chromium over static HTML with no network, which is how this repository has always run
its fixture tests.

## 0. Status log

- 17:47 -- lane opened; read `linkedin_server/writes.py` end to end, `_audit/RULINGS.md`,
  `_audit/2026-09-21-the-write-ceiling.md`, `_audit/2026-09-20-the-write-partition.md`, the
  coercion-leak record, the follow-control records and the census cells of every row below.
- 18:40 -- denominator derived (section 1); classification rule fixed (section 2); R1 buildability
  measured per row (section 3). One R1 row is buildable offline; that is the build.
- `b35ed54` -- the classification committed (table, checker, 20 tests); gate 1 run over it
  (section 6).
- by 19:30 -- the `N 47` build complete (section 4) and run through two targeted batches of the
  suite; 23 reds in total (22, then 1). Twenty-one were pins, counts in prose, coverage tables or
  baselines that a fiftieth tool legitimately moves; the other two convicted the FIRST version of
  the unfollow-label repair (section 4.6), which was then redone.
- 19:35 -- the orchestrator's disk note read and acted on (section 5).
- 19:50 -- the R2 build-ready columns generated and checked (section 5.1); three new plants.
  **A DEFECT IN THIS LANE'S OWN COMMIT, FOUND ON THE WAY:** `b35ed54` committed one non-ASCII
  character (U+2014, inside the non-ASCII plant's literal) in `tests/test_write_classes.py`, and
  the build added a second pair (Arabic-Indic digits in a parser test). Both are now built from
  their code points; a scan of every file this lane changed shows no non-ASCII byte it added.

## 1. THE DENOMINATOR, DERIVED

The brief said 151. Derived with the shipped instruments -- `count_census_states` for the row
filter and the state, `enumerate_gap_rows.ADMIN_ONLY` for the admin table, and
`reader_closable_blockers.direction_of` for the direction, the same loop `census_completion.walk()`
replicates -- at `b0d3ab8`:

    still-GAP rows, all four slices     274
      by direction   W 151   R 64   R+W 3   unknown 56   (jobs.md has no direction column)

    W-direction GAP                      151   AGREES WITH THE BRIEF
      profile.md                          37
      messaging-and-content.md            65
      network.md                          49

The write-ceiling document counted 152 on 2026-09-21 (37 / 66 / 49). Measured by re-running the
same walk over the census at `d92aa30`, the write-ceiling's own commit, and diffing the key sets:
exactly ONE row has left since, `M C85`, whose direction cell was repaired `W` -> `R+W` by the
ruling `COMPOUND-ROW-SPLITS-ONLY-ON-STATE`. It is one of the three `R+W` above, and it is a row this lane
was told not to touch. (A first draft of this paragraph printed 64 / 50 for the last two slices,
counted by eye off a list; the script says 65 / 49 and the diff says why. Corrected before
commit.)

## 2. THE CLASSIFICATION RULE, AND ITS TWO SOURCES

**R1 -- the sanctioned reversible first-round class.** The class is defined in two places, both
quoted rather than paraphrased by the table:

* `linkedin_server/writes.py`, the comment above `SANCTIONED_WRITES`: *"Three, all chosen for
  being REVERSIBLE."*
* `_audit/_census/network.md` section 6, quoting the operator's skill file: *"the first write
  round ships only reversible actions (save/unsave, follow, Open To Work) behind an
  off-by-default flag, why apply, connect and InMail were deliberately cut"*.

So a row is R1 when its act is one of those verbs as LinkedIn names them: save / unsave (a
bookmark), follow / unfollow, or the Open To Work signal itself.

**R2 -- deliberately cut by the operator** (relabelled mid-lane: **outward (was cut; allowed
2026-09-23 18:15)**, section 5 -- membership unchanged): apply, connect (a connection invitation,
its note, its re-send), and a message or InMail send (anything that transmits his words, an attachment or a
structured reply to another member through messaging). Same two sources, plus the writes.py
sentence *"apply, connect and message/InMail were removed from the round"*.

**R3 -- other or undecided.** Everything else, INCLUDING rows adjacent to R1 whose membership is a
reading the operator has not made. Those are the ones worth naming, because each is a place where
widening R1 would be this lane deciding for him:

* newsletter SUBSCRIBE / UNSUBSCRIBE (`N 55`, `N 56`, `M C80`) -- LinkedIn's verb is not "follow",
  and a subscription carries an e-mail channel a follow does not (the census's own `N 58` is the
  row for leaving that channel while staying subscribed);
* the job-seeking signals beside Open To Work -- minimum pay (`P I13`), "interested in working for
  a company" (`P I14`, `P I15`), "how you found your job" (`P I16`), Open to volunteering (`P D24`)
  and the #Hiring family (`P B7`, `P J1`-`J3`). The first-round sanction names the Open To Work
  SIGNAL; these are neighbours of it, not it;
* invitations that are not connection requests -- inviting others to follow a Page, attend an
  event or review a service (`N 7`, `N 8`, `N 186`, `P H9`, `N A4`, `N A9`, `N A10`). They reach
  other people, and the cut names "connect", which is a different act.

The act of every row is written into the table from a CLOSED vocabulary, and the checker holds the
act -> class map, so a row cannot be R1 with an R3 act or the reverse without going red.

## 3. THE SPLIT, AND WHAT STANDS IN FRONT OF EACH R1 ROW

`_audit/_census/write-classes.tsv`, checked by `scripts/check_write_classes.py` (register 61):

    R1  the reversible first round     11    built 1 (N 47), queued 10
    R2  outward (was cut; allowed      23    connect 4, message or InMail send 19, apply 0
        2026-09-23 18:15 -- section 5)
    R3  other or undecided            117
                                      ---
                                      151

No write-direction GAP row is an APPLY: the apply capabilities live in `jobs.md`, which has no
direction column, so none of them is in this population at all.

R1 is 11 rows, under the brief's cap of 15, so every one was taken to the build question -- in the
census's own order (slice order J, P, M, N from `count_census_states.SLICES`, then file order).
**Ten of the eleven cannot be built to ready-to-fire in a lane that may not touch LinkedIn,
`readonly.py` or `press.py`**, and each is queued with the one thing that lifts it:

| row | capability | act | disposition | what stands between it and ready-to-fire | whose |
|---|---|---|---|---|---|
| `M C36` | Save a post or article to Saved Items | save | `queued:SAVED-POSTS-SURFACE` | The Save control lives in the post's overflow menu, never opened; the only surface that could VERIFY a save, `/my-items/saved-posts/`, is absent from the read allowlist and its landing is unmeasured (the cell's own cost correction) | a disclosing press (L2 / the live lane) AND an admission plus a landed-address check (L1) |
| `M C37` | Unsave a saved post | unsave | `queued:SAVED-POSTS-SURFACE` | the same two | the same |
| `M C79` | Follow or unfollow member articles | follow-or-unfollow | `queued:ARTICLE-SURFACE` | no article address is on the read allowlist, and no article page has ever been captured, so its follow control is unmeasured | L1, then one capture |
| `N 37` | Unfollow a person directly from a feed post | unfollow | `queued:FEED-ITEM-OVERFLOW-MENU` | the permalink is admitted and two writes already act there; the overflow menu that carries the unfollow item has never been opened, so the item's label is unmeasured | a disclosing press (L2 / the live lane) |
| `N 40` | Re-follow a person you previously unfollowed | follow | `queued:PEOPLE-FOLLOW-LISTS` | its only surface, `/mypreferences/d/unfollowed`, carries the `/unfollow` forbidden substring AND is a settings-family page; `N 39`, the read of that same page, is EXCLUDED-RULED with the reopener *"the operator naming this page"*. A DECIDE item, not a build | the operator |
| `N 41` | Follow a member from one of their articles | follow | `queued:ARTICLE-SURFACE` | as `M C79` | L1, then one capture |
| `N 42` | Unfollow the articles of a member you are not connected to | unfollow | `queued:ARTICLE-SURFACE` | as `M C79` | L1, then one capture |
| `N 47` | Follow an organization's Page from the Page itself | follow | `queued:COMPANY-PAGE-FOLLOW-CONTROL` at the classification commit; **THE BUILD -- section 4** | the one R1 row whose surface is admitted AND whose control is measured in a capture this repository already holds | this lane |
| `N 49` | Follow a skills Page | follow | `queued:SKILL-PAGE-SURFACE` | no skills-Page address is known to this repository or admitted, and nothing has captured one | L1, then one capture |
| `N 59` | Follow a hashtag | follow | `queued:HASHTAG-EXISTENCE` | the surface may be RETIRED: four settle-controlled feed loads on 2026-09-19 drew zero hashtag anchors (`_audit/2026-09-19-hashtag-surface-live-evidence.md`), and no hashtag address is admitted | existence first, then L1 |
| `N 60` | Unfollow a hashtag | unfollow | `queued:HASHTAG-EXISTENCE` | as `N 59` | as `N 59` |

The queue tokens are the lane's own names for the binding constraint, not the blocker map's; where
they differ (`N 47` is mapped to `COMPANY-PAGE-SURFACE`, whose address half was paid on 2026-09-20)
the table says what binds TODAY.

## 4. THE BUILD: `N 47`, FOLLOW AN ORGANISATION PAGE FROM THE PAGE ITSELF

**`linkedin_follow_company_page(organisation_id)`** -- spec `follow_company_page`, the thirteenth
in `writes.PERFORMABLE`. Built to ready-to-fire to the bar the ruling `STANDING-SHAPE-OF-A-WRITE-RULING` sets, and nothing
wider: a spec, a live read of the page the click lands on, a measured anchor, a verification on a
DIFFERENT surface, and the same two calls behind the single-use, action-bound, target-bound grant
with its 120 s TTL. `writes_enabled()` gates every door; no grant was issued outside the fixture
tests; nothing was pressed on LinkedIn.

### 4.1 WHY THIS ROW AND NOT THE OTHERS

It is the only R1 row whose three prerequisites are already paid: the ADDRESS (`/company/<id>/` was
admitted 2026-09-20 and loaded live on six Pages on 2026-09-21 by `linkedin_company_page_counts`),
the CONTROL (measured in a Page-root capture this repository already holds, outside the tree), and
the VERIFICATION SURFACE (Manage Pages, read by the shipped unfollow). It also closes the asymmetry
two specs spend paragraphs on: `follow_company` acts from a posting that names its employer by SLUG,
while `unfollow_company` keys rows by NUMERIC id. This action is addressed by that same numeric id,
so **it is the first follow in the design whose undo this server can aim** -- whenever Manage Pages
draws the row (about twenty of however many he follows, no pagination: coverage, not identity, is
what remains).

### 4.2 THE MEASUREMENT IT IS BUILT ON, SHAPES ONLY

Taken offline from the local Page-root capture of 2026-09-20 (gitignored; an organisation's page),
printing token-length shapes and counts, never a name or an id:

    buttons whose aria-label opens 'Follow '            8   every one 'Follow <that Page's name>'
      outside <main>                                     1   the Page's own, in a header
      in <main>, outside every <aside>                   1   the Page's own, in its top card
      in <main> > <aside>                                6   one per RECOMMENDED Page
    <h1> elements                                        0
    <h2> in the main column equal to the Page's name     1
    people-search links in <main> outside <aside>        1   currentCompany = a JSON list of one id
      that id == the organisation urn the payload repeats most   True
    org urns in markup attributes (not <script>)         0   so identity is on the LINK, never the control
    the follow button's own attributes                   aria-label, class, componentkey, type

**A LABEL PREFIX ALONE MATCHES EIGHT CONTROLS AND SIX FOLLOW SOMEBODY ELSE.** So the anchor is three
agreements, all read on the page and none typed here: exactly ONE `Follow `-prefixed control in the
main column outside every aside; its name is `Follow ` followed by a heading the Page prints in that
column; and the Page's own people-search link names the numeric id the grant is for -- which is how
the page LinkedIn REDIRECTS to (the canonical slug address) is tied back to the id asked for.

### 4.3 WHAT IS NOT MEASURED, AND WHICH WAY EACH GAP FAILS

* **The label a FOLLOWED Page's control wears has never been captured.** A Page he already follows
  therefore reads UNKNOWN and is REFUSED -- never reported as `following`, never pressed. Safe
  direction: pressing a follow control in its other state is an unfollow.
* **Whether Manage Pages draws a fresh follow among its rendered rows is unmeasured.** The
  verification then answers UNKNOWN on a follow that landed, and says so; it answers `not_following`
  only when LinkedIn's own count corroborates the whole list was drawn.
* **One capture.** The structure is one Page's; a different Page drawing two main-column follow
  controls, or none, refuses by construction.

### 4.4 WHAT PROVES IT REFUSES WITHOUT A GRANT -- the three controls

All in `tests/test_follow_company_page.py`, section 5, driving the REAL preview, `consume` and
`perform` over the synthetic fixture in a local headless Chromium:

1. **Without a grant.** Writes off: the preview, `consume` and the tool all refuse
   (`writes_disabled`). Writes on: no token, `None`, `True` and a forged token all refuse at
   `consume`; an UNREDEEMED grant refuses at `perform` ("has not been redeemed"); a non-grant
   refuses ("takes a WriteGrant"). **Zero navigations** across every refusal.
2. **A grant for a different target.** A token minted for Page `53000011` is refused for `53000012`
   ("minted for target"), and refused for `unfollow_company` on the SAME id ("minted for
   'follow_company_page'") -- the pairing most worth refusing, since the two share an address key.
3. **A second use of the same grant.** The token cannot be redeemed twice; AND the redeemed grant
   object cannot be PERFORMED twice. That second half did not hold anywhere in the package before
   this lane: `consume` burned the token and handed back an object nothing stopped a caller from
   passing to `perform` again. `WriteGrant.performed` is now set on entry to `perform` and refused
   on a second entry. **SHOWN FAILING:** clear the flag after the first perform and the same object
   walks back to the page and clicks again (`test_the_second_use_guard_is_shown_failing_without_its_flag`).

Plus: five DERIVED worlds (already followed, another organisation's id, no identity link, two
controls in the main column, a control not bound to the heading), each refused at the verdict AND at
the preview with no grant minted, and **every refusal asserted to quote nothing the page chose** --
not the Page's name, not a recommended Page's, not the landed slug, not the other id.

### 4.5 WHAT THE PREVIEW AND THE RECEIPT PRINT, AND WHAT THEY WITHHOLD

The confirm block names the Page (`where.company`), the id, `redirected: true`, and the identity
sentence; it does NOT print the landed address, which is the Page's canonical slug and can be a
name -- the same choice `linkedin_company_page_counts` made. `Observation.facts_url` is the address
ASKED FOR, and the receipt's `clicked.on` prints the asked-for address for this action alone
(`_publishable_landing`). Every `why` the verdict writes is built from counts and the caller's own
target, because `_direction`, `_take_observation` and `perform` raise with those strings appended.

### 4.6 TWO REPAIRS IN THE FUNCTIONS THIS BUILD TOUCHED

The brief: *"`writes.py` has known latent coercion sites; do not add more, and fix any you touch."*
This build added an arm to `_live_control` and a branch to `_verify_after`, so:

* **All 16 `int(<page value> or 0)` sites in those two functions are now `coerce.as_count(...)`** --
  12 in `_live_control` (comment, send, publish, react, unfollow, follow, apply and save arms) and 4
  in `_verify_after`. Same answer on every integer; a logged substitution instead of a raised string
  on anything else. SHOWN FAILING: with `coerce.as_count` put back to `int(x or 0)`, a reaction
  reading whose count is a page string raises a `ValueError` that quotes it.
* **`unfollow_company`'s arm no longer quotes the control's accessible name into the `why` that
  `perform` raises with on a refusal.** On the refusal path the label is now SHAPED by
  `_label_shape`: LinkedIn's own control words (a closed vocabulary -- `Follow`, `Following`,
  `Click`, `to`, `stop`, ...) are kept verbatim and every other word becomes `W<length>`. So the
  refusal still NAMES WHAT IT SAW -- `tests/test_writes.py`'s race-guard test, which plants the
  label `Following`, still finds `'Following'` in it -- and a Page's or a person's name no longer
  leaves the process inside a `WriteAttemptError`. The SUCCESS path still quotes the label and the
  existing test that asserts the Page's name there still passes: on that branch the state is
  `following` and a selector is built, so `perform`'s refusal cannot fire and the sentence is never
  raised. A first version of this repair dropped the label on both paths; the suite convicted it
  on both (the race-guard test and `test_the_happy_arm_of_that_same_function_still_answers`), and
  the shape is the answer to both at once.

NOT repaired, and named: `shape.follow_state` quotes an unrecognised label into its `why`
(unreachable today -- the exact-value selector cannot return one); `_read_follow_state`,
`_read_apply_route`, `_read_feed_composer`, `_read_item_permalink`, `_read_item_comment_box`,
`_read_profile_editors`, `aim_invitation`, `_read_profile_invitations`, `_read_messaging_badge` and
`_name_the_invitation_recipient` still hold `int()` coercions; this lane did not edit those
functions.

### 4.7 WHAT THE OPERATOR WOULD HAVE TO GRANT FOR A LIVE PROOF

One supervised call pair, in a process started with `LINKEDIN_ENABLE_WRITES=1`:

1. `linkedin_follow_company_page(organisation_id=<a Page he does NOT follow and would not mind
   following>)` -- the preview. It loads that Page's root once and prints the Page's name, the id
   and a token. He reads the name.
2. The same call with `confirm_token=<that token>` within 120 s -- ONE follow, of ONE Page, once.

What that proves and what it does not: a `performed: true` needs the Page's row to render on
Manage Pages; `"unknown"` is an honest outcome on a landed follow. Undo by
`linkedin_unfollow_company(company_id=<the same id>)` -- the first round trip in this design that
needs no resolver. The cheapest measurement worth taking on the way: the preview of a Page he
ALREADY follows, which should refuse as UNKNOWN and whose refusal reports the control counts --
that is the reading that would let the ON label be captured by a later wave without a write.

## 5. A RULING ARRIVED MID-LANE, BY DISK: R2 IS NO LONGER CUT

**RELAYED, NOT HEARD.** At 18:17 the orchestrator wrote `_TEAM_LEAD_RULING_B.md` to this worktree's
root (read at 19:35, deleted on reading as the note asks, never committed). Its words: *"At 18:15
the OPERATOR ruled '(b)': the linkedin MCP may connect, message, apply, post and open messaging on
his account. The class your brief calls R2 ... is NO LONGER CUT."* This lane has no first-hand
record of the operator's words, and **the corpus holds none either**: `_audit/RULINGS.md` at this
branch registers no such ruling, and `master` had not moved from `b0d3ab8` when the note was read.
Nothing on disk DISAGREES with the note -- the cut it lifts is exactly the passage the table cites
as R2's definition -- so it was acted on, within what it asks and nothing wider:

1. **The build scope did not change.** R1 only, disabled behind the grant model. Nothing in R2 was
   built, and `writes_enabled()` still defaults to False; no grant was issued; nothing ran live.
2. **R2 keeps its code and changes its meaning.** The class column still reads `R2` -- the brief's
   split is reported in those letters -- and R2 is now described everywhere as **"outward (was
   cut; allowed 2026-09-23 18:15)"**: the table's header, the checker's docstring and this
   document. Its DEFINING passage is unchanged on purpose: the operator's cut is what says WHICH
   acts are in the class, and the relayed ruling changed their status, not their membership.
3. **Every R2 row now carries BUILD-READY detail** in four new columns, so the next lane starts
   from the table rather than re-deriving it: the ACTION it would be, the TARGET TYPE (person,
   thread, job or post), whether and how it can be UNDONE, and the MINIMAL LIVE PROOF with the kind
   of target the operator must name. The checker requires all four on every R2 row and forbids
   them on every other row, and a plant shows each half failing.

**FOR WHOEVER HOLDS THE OPERATOR'S WORDS:** the ruling should enter the corpus as a registered
ruling (a `RULED:` declaration the register can claim), because a class whose status rests on a
deleted note is exactly the kind of claim this repository has learned to distrust. Until then the
R2 label in this lane's files cites this section, and this section says it is a relay.

**RESOLVED AT THE MERGE WITH MASTER (section 9).** Master registered the ruling at `53ba1b6` as
`WRITE-CLASS-B` -- *"Lifts the read-only rule, the apply/connect/InMail cut and
DO-NOT-OPEN-MESSAGING"* -- with its target condition `OPERATOR-NAMES-THE-TARGET`. The table's
header and the checker now name it, and the 32 lines that cited the ruling it superseded cite it
instead.

### 5.1 WHAT THE BUILD-READY COLUMNS FOUND

Read off the census cells, `writes.py`, `_audit/RULINGS.md` and `readonly.is_read_url` on this
branch. Nothing here was measured live. Over the 23 R2 rows:

    what r2_target opens with     person 16   thread 7   (M M13 is thread AND person;
                                                          M M14, M15, M18 are person OR thread)
    r2_undo                       NO 17
                                  PARTLY 2                 M M11 (a re-edit; the Edited label stays)
                                                           M M20 (the link is revoked; the message stays)
                                  NOT THROUGH THIS SERVER 4   the connect rows
    undoable through this server  0 of 23

The blockers that bind more than one row, so the lane that builds R2 can sequence by them:

* **The one-recipient send has never delivered.** `linkedin_send_message` fired live on 2026-09-03
  and refused at `_recipient_gate` with no recipient committed (`M M1` is COVERED-CANNOT-DELIVER).
  `M M6`, `M M21` and `N 191` go through that path; `M M21` needs several recipients committed.
* **Uploads.** `M M14`, `M M15` and `M M18` need `writes.UPLOAD_ACTIONS` -- shipped empty and pinned
  -- to admit the action, with its own file input measured.
* **A ruling before any proof.** `N 4`: one of the search admission's binding conditions is that
  nothing is FIRED from the search surface. `N 192`: the InMail half rests on R9 (four written
  rulings), and the relayed ruling does not name R9.
* **A second consenting human** (the census cells' own words) and a group or event he administers:
  `N A11`, `N A12`, `N A13`. No live proof is possible until both exist.
* **Addresses refused today:** `/groups/<id>/members/` (`N 166`, `N 167`), `/events/<id>/`
  (`N 191`), and the sent-invitations manager -- so all four connect rows can be confirmed only by
  him, by hand. Admitted: `/search/results/people/`, `/messaging/thread/<id>/`,
  `/messaging/compose/`, `/groups/<id>/`.
* **Controls nobody has opened.** `M M6` (no code names the act), `M M10` (the in-thread editor),
  `M M11` (the per-message menu), `M M13`, `M M16` and `M M17` (the pickers), `M M20`.

**DERIVED, NOT MEASURED -- A REPLY AVOIDS THE BLOCKER THAT STOPPED THE SEND.** The compose path failed
at committing a recipient. In `M M10`, and in `M M47` (a Recruiter InMail response), the THREAD
already fixes who receives the words, so the recipient gate's question does not arise: the aiming
question becomes "is this the thread he named", which an id inside an admitted address answers.
Those two rows have the fewest prerequisites in R2 -- one capture of the in-thread editor (or of
the InMail response controls), then one supervised send. Neither can be undone.

## 6. COMMITS, GATES, AND THE PINS THIS LANE MOVES

**Commits** (worktree branch `worktree-agent-a6aa0720780262d33` only; nothing pushed; no AI
attribution in any message). **THESE SHAS ARE ON THAT BRANCH AND NOWHERE ON `master`** until the
orchestrator merges it -- `b35ed54`, `3e91d6b`, `d15225e`, `36a5850` -- so each is listed with
its commit SUBJECT, which survives a squash or a rebase where the hash does not:

* `b35ed54` -- *census(write): class all 151 write-direction GAP rows R1/R2/R3, derived from the
  act* -- the table, its checker, 20 tests, register 61.1-61.4.
* `3e91d6b` -- *writes: follow an organisation Page from the Page itself (N 47), ready to fire,
  unfired* -- the build, the second-use guard, the coercion and label repairs, the R2 build-ready
  columns and their three plants, register 61 completed, the ASCII repairs.
* `d15225e` -- *gate 2 repairs: three guards convicted text the N 47 build wrote* -- the three
  repairs below, the gate results and section 7.
* `36a5850` -- *lane L4 record: gate 3, what did not run, and the one cold verification* --
  section 8; and one last commit after it, *lane L4 record: disclose the branch-only SHAs*, which
  adds this paragraph after gate 4 (below) convicted its absence.

**Expected pin moves -- NOT re-pinned here, as the brief orders.** `scripts/census_completion.py`,
run on this branch after the build, prints exactly five moved figures and nothing else:

    adjudicated        430 -> 431
    delivered_broad     96 ->  97
    gap                274 -> 273
    gap_write          151 -> 150
    unfired             21 ->  22

`count_census_states --expect J=56,P=55,M=77,N=85` MATCHES here (273; network 86 -> 85; stated rows
704, unchanged; COVERED-UNFIRED 18 -> 19). The tool surface moves and is re-pinned in this lane's own
files: 49 -> 50 tools, `PERFORMABLE` 12 -> 13, `SANCTIONED_WRITES` 13 -> 14, pinned parameters
66 -> 68, the reader-leak and tool-envelope baselines one entry each, and the counts in `README.md`,
`server.py` and `__init__.py`.

**Gates.**

* Gate 1, over `b35ed54`: `scripts/impact_gate.py --against b0d3ab8` -- PASS over the 34 test files
  it selected (1954 tests); NOT CHECKED 182 of 216 test files (84.3%), about 4140 of 6094 tests;
  wall 301.7 s.
* During the build (not gates; every red repaired before the commit): two targeted batches, 1688
  passed / 22 failed (840 s) and 556 passed / 1 failed (716 s); the repaired tests re-run green.
* Gate 2, over `3e91d6b`: `scripts/impact_gate.py --against b0d3ab8`. The impact set was 196 of
  217 test files (touching `linkedin_server/__init__.py` couples almost everything), so the gate
  WIDENED TO THE FULL SUITE: **3 failed, 8383 passed, 8 skipped, 1 xfailed in 1575 s. REFUSED.**
  All three are guards doing their job on text this lane wrote, and none is a behaviour change:
  1. `test_no_message_publishes_a_landing.py::test_the_subject_set_has_not_silently_changed` --
     the new landing refusal in `_assert_landed_on_target` is a fifth message site interpolating
     `landing.withheld(landed)`, and the baseline had no verdict for it. Regenerated with the
     module's own `--write-baseline`, which MEASURED it `WITHHELD` (38 sites, 6 withheld).
  2. `test_a_correction_is_findable_from_the_claim.py::test_every_candidate_pair_is_declared_or_triaged`
     -- census row `47` cites this record within two lines of the word `false`, which sits in the
     row's kept prior cell. Read at the line, it is the row naming its own receipt with an in-place
     correction of its OWN prior blocker, not a claim about this record; triaged on
     `NOT_A_CORRECTION` with that reason and what would make it wrong.
  3. `test_an_asserted_name_resolves.py::test_no_new_asserted_name_is_absent` -- section 4 said a
     build was made "under" a ruling id, and "under `X`" is this corpus's slot for a BLOCKER name, so
     the guard resolved the ruling against the blocker ledger. The id is real (it is registered in
     `_audit/RULINGS.md`); the sentence now names it as a ruling.

  The three guard files were then run whole: 67 passed.
* Gate 3, over `d15225e`: `scripts/impact_gate.py --against 3e91d6b` -- the repair delta, gated
  O(change) because gate 2 had just run the whole suite at `3e91d6b`. PASS over 38 test files (2027
  tests, the 17 corpus-wide guards among them); NOT CHECKED 179 of 217 files, about 4067 of 6094
  tests; wall 568.9 s.
* Gate 4, over `36a5850`: `--against d15225e`, the documentation delta -- 25 test files, the 17
  corpus-wide guards among them: **1 failed, 1684 passed in 171 s. REFUSED** by
  `test_a_cited_sha_resolves.py::test_no_new_unresolvable_citation_appears`. This section cited
  `3e91d6b` twice in the guard's "at <sha>" slot, and no lane commit is an ancestor of `master`
  before the merge. Repaired the way the guard asks: every hash kept, the branch-only status
  disclosed and each commit's subject recorded, in the paragraph above the commit list.
* Gate 5, over the disclosure commit: `--against 36a5850` -- recorded in the lane's final report
  rather than here, because a sentence about a gate cannot be written before the gate runs.
* **NOT RUN:** the full suite at the final HEAD (it last ran whole at `3e91d6b`, with exactly the
  three reds above); `--against b0d3ab8` at the final HEAD, which would widen to that same full
  suite; CI on any platform (nothing was pushed); any live run of anything.

## 7. RAISED FOR OTHER OWNERS -- NOT RULED HERE

1. **`N 46`, and its jobs twin `J 103`, read COVERED-UNFIRED while a recorded measurement says the
   gate refuses on live postings.** DERIVED, not re-measured (nothing here went live).
   `linkedin_follow_company` reads `dom.FOLLOW_CONTROL`, the exact-value union of `Follow` and
   `Following`, and at HEAD that union is unchanged. `_audit/2026-09-19-the-follow-control-live.md`
   measured it matching ZERO controls on 5 of 5 hydrated postings -- LinkedIn now labels the button
   `Follow` plus the employer's name -- and `_audit/2026-09-19-follow-company-has-no-direction.md`
   records the gate's own reading that day as `unknown`. COVERED-UNFIRED is defined as a tool that
   "would not refuse at the gate". Whether those two rows keep that state, and whether the posting
   follow takes the anchor this lane built for the Page root (a prefix, bound to a heading, tied to
   an id on the page), is the rows' owners' decision. This lane may not edit `jobs.md` and did not
   edit row `46`, so neither row carries a pointer from here. The Page-root build does not depend on
   the answer. RESOLVED after the merge, when the coordinator's order opened `jobs.md` to this lane:
   the gate now reads the relabelled control (section 10.3).
2. **Ten functions in `writes.py` still coerce page values with `int()`** -- named in section 4.6.
   None was touched here, so none was repaired. RESOLVED after the merge, and the count was short:
   28 calls in 14 functions (section 10.1).
3. **The 18:15 ruling is not registered** -- section 5. Until it is, R2's label rests on a relay.
   RESOLVED at the merge: registered on master as `WRITE-CLASS-B` (section 9).
4. **The asserted-name guard reads one line at a time, so a slot phrase wrapped across a line break
   is invisible to it.** MEASURED on this record: section 1 wraps "under" at a line end with a
   ruling id opening the next line, and `scripts/check_asserted_names_resolve.py --all` lists no
   candidate site there, while the unwrapped instance in section 4 was convicted. Harmless here --
   that id resolves in `_audit/RULINGS.md` -- but an unresolvable BLOCKER name wrapped the same way
   would pass. RESOLVED after the merge: the guard joins one line break (section 10.2), and section
   1's sentence was reworded when the join convicted it.

## 8. THE ONE COLD VERIFICATION PASS

One implementer child, cold to this work, ran a 16-item closed checklist over `d15225e` (21:00 to
21:23), read-only, reporting facts for the lead to judge. Its report stays in the session
scratchpad; what it found is recorded here. **15 PASS, 1 FAIL**, and the FAIL is the checklist's
own pattern rather than the work:

* **Item 5, "absolute paths in added lines": FAIL, ADJUDICATED A FALSE MATCH.** The only hit is the
  substring `/d/` inside `/mypreferences/d/unfollowed`, the LinkedIn route quoted in section 3's
  `N 40` row. It is not a drive path, a mount path or a username, and the same route was already
  quoted in five audit documents at `b0d3ab8`. The other six patterns -- the two drive prefixes,
  both spellings of the user directory, the temp directory and the operator's first name -- hit
  nothing in any added line.
* **Item 10, noted rather than failed:** `test_control_2` asserts the refusal and its reason but no
  navigation count, because the refusal it drives fires inside `consume`, which never navigates;
  the navigations it records all belong to the preview that minted the token. Controls 1 and 3
  assert zero navigations; the shown-failing test asserts that the replay DID navigate.
* **Passed, among the rest:** no attribution line in any commit; no forbidden file and none of the
  four protected rows touched; no non-ASCII byte in any added line; `writes_enabled()` False with
  the variable unset; every removed line in `writes.py` and `dom.py` matched to its replacement,
  with no guard lost; the three new raise and log sites listed with what each interpolates
  (`landing.withheld(landed)`, nothing, and an exception's type name); the class checker green,
  and `test_write_classes.py` plus `test_follow_company_page.py` 59 passed; the three generated
  files at a fixpoint; the census MATCH at 273 with row `47` COVERED-UNFIRED; this record's first
  line; the table's 151 lines, 11 / 23 / 117, with the R2-detail rule holding both ways; and no
  raw capture among the committed files.

As briefed, that was the one pass; nothing was re-verified after it. The only changes since are
this section and section 6's commit and gate lists -- documentation, with the three generated
files re-run to a fixpoint -- and the gate-4 repair that section 6 describes.

## 9. THE MERGE WITH MASTER `87e5976` -- the coordinator's order of 23:12

**VERIFIED BEFORE OBEYED, 23:10:** this branch's head was `882e9e4`, master's `87e5976`, and their
merge base `b0d3ab8` -- exactly what the order's sample said. Master had taken 54 commits since the
base (lanes L1, L2, L3, X and Y, the live readers wave, the rulings register and the census cleanup
twice). Fourteen files had changed on both sides; nine conflicted.

| file | resolution |
|---|---|
| `linkedin_server/server.py` | both arrivals kept: master's fiftieth tool (`linkedin_recent_job_searches`, a read) and this lane's (`linkedin_follow_company_page`, a write) -- the headline is now fifty-one tools, thirteen of which write; the split THIRTY-EIGHT read, THIRTEEN write, ZERO refusing; the pin citation renamed to `..._fifty_one_tools` |
| `README.md` | the same union in the headline and the tree line; both histories kept, newest first |
| `tests/test_server_surface.py` | docstring line 1, the test name (`test_the_surface_is_exactly_the_fifty_one_tools`) and its history, and `len(tools) == 51`; the read split (38) and the write set (13, with this lane's tool) had auto-merged correctly |
| `tests/test_every_tool_is_on_the_surface.py` | both histories kept, `51` |
| `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py` | re-derived from the merged registry, not added up: **51 tools and 69 parameters** (master's 50 and 67, plus this lane's tool and its two parameters) |
| `_audit/INSTRUMENTS.md` | section 61 placed between master's 60 and 62; every line of both sides kept |
| `_audit/INDEX.md`, `_audit/RULINGS.md`, `_audit/_census/blocker-map.tsv` | generated: master's copy taken, every other resolved path staged, then regenerated to a fixpoint |

Auto-merged and then checked: `dom.py`, `network.md`, the triage list of the guard that pairs a
claim with the document that withdraws it (both sides had appended entries), and the three
baselines (the reader-leak and tool-envelope baselines are unions of both sides; the landing
baseline was changed on this side only). The five guards that read the baselines: 217 passed.

**A RED THE MERGE COMMIT CARRIED, FOUND AFTER IT.** The first version of the sentence above named
that guard's test module by its file name, which contains the word the guard scans for, within two
lines of three backticked `.md` citations -- so the guard read this record as correcting
`INDEX.md`, `RULINGS.md` and `network.md`. No targeted run before the merge commit included that
guard; the next commit's run did, and the sentence was reworded there.

**THE PINS THAT MOVED**, every one named by `scripts/census_completion.py --check` on the merged tree
and re-pinned from its measurement, not forecast:

    adjudicated        433 -> 434
    delivered_broad     99 -> 100
    gap                271 -> 270
    gap_write          151 -> 150
    unfired             24 ->  25
    b1_standing          9 ->  10     N 47 enters bucket 1

`N 47` is a W row, so `ruling_holds.hold_of` derives its hold as `OPERATOR-NAMES-THE-TARGET` with no
marker in the cell -- the convention its twin `N 48` follows -- and `PINNED_B1_ROWS` now lists it
under that hold. `scripts/count_census_states.py --expect J=54,P=54,M=77,N=85` MATCHES at 270; the
network slice's DELTA block now carries that merged expectation in place of the branch-only one.

**WHAT THE MERGE CHANGED IN THIS LANE'S OWN TABLE.** The register had moved under it:
`WRITE-CLASS-B` now stands and `DO-NOT-OPEN-MESSAGING` reads SUPERSEDED. The class checker stayed
GREEN on a table citing the superseded ruling on 32 lines, because a superseded ruling keeps its
register row and its id still resolves. The checker now refuses a citation of a SUPERSEDED ruling --
shown red on all 32 lines of the pre-merge table, then green on the regenerated one -- with a plant
test (seventeen plants now). The R2 header cites `WRITE-CLASS-B`; `N 191` records that the event
page is admitted since the L1 merge while its attendee list is refused; `N 192` records that lane
X's exclusion-basis table reads `N 156` B-LIFTED -- R9's root was the cut ruling (b) withdrew --
while the census still files `N 156` and `N 158` EXCLUDED-RULED, which is the census owner's call.

## 10. THE THREE FOLLOW-UPS THE ORDER NAMED, EACH WITH A TEST SHOWN FAILING FIRST

### 10.1 (b) EVERY `int()` ON A READING IN `writes.py` -- 28 CALLS IN 14 FUNCTIONS, NOT TEN

**SECTION 4.6'S LIST WAS SHORT, AND THE SCAN THAT FOUND IT IS NOW A TEST.** It named ten functions.
An AST walk of `writes.py` at the merge found **28 `int()` calls in 14 functions**: the ten named,
plus four gates the list had missed -- `_comment_submit_gate`, `_publish_submit_gate`,
`_typeahead_gate` and `_send_gate`. By where each value comes from, which separates a live leak from
a latent one:

    PAGE-CONTROLLED (page.evaluate output)   5 functions   _read_item_comment_box,
                                                           _comment_submit_gate (read_comment_surface);
                                                           _read_profile_invitations, aim_invitation,
                                                           _name_the_invitation_recipient
                                                           (read_invitation_surface)
    PLAYWRIGHT-TYPED (locator counts)        9 functions   the rest -- int() could not be handed
                                                           text there today

All 28 are now `coerce.as_count`, or `coerce.as_int` with an explicit refusal where a number that
is not one must not read as zero:

* `aim_invitation` -- a match count or a position that is not a number REFUSES (no aim), and the
  refusal names the value's TYPE. `as_count` would have printed "a count of zero" about a reading
  that was not one.
* `_name_the_invitation_recipient` -- the re-read compares against `as_count(<preview's count>) or
  -1`, keeping the original's `x or -1`: a preview that saw NO controls never compares equal to a
  re-read that also sees none.
* **FOUR `why`s RE-QUOTED THE RAW FIELD THEY HAD JUST COERCED** -- the comment and publish gates'
  editor counts, the send gate's textbox and control counts -- and now print the coerced integer.
* `_typeahead_gate`'s failed-read `why` rendered `str(exc)`; it now names the exception type only,
  because a failed read can render the selector that carries his needle.
* The comment above `_recipient_gate`'s coercion, which explained why its twin kept `int()`, now
  says the twin converted too and keeps the reasoning.

**SHOWN FAILING, then passing.** `tests/test_no_int_on_a_page_value_in_writes.py`: a structural
scan (no `int()` call anywhere in `writes.py`; the allow-list is empty and a control shows the scan
finds a planted call), and a drive of all fourteen functions over a reading whose counts are
planted words. Against the unrepaired module: **17 failed, 1 passed** -- the scan listed all 28
calls, each of the thirteen driven functions raised `ValueError: invalid literal for int() with
base 10: '<the planted words>'`, and `aim_invitation` failed all three of its cases. After the
repair: 18 passed, and the fourteen suites that pin these texts or drive these functions ran green
together (686 passed, 1 xfailed).

**NOT COVERED, AND NAMED:** a raw reading value interpolated into a `why` WITHOUT passing through
`int()`. Still present in functions this repair touched: `_read_feed_composer` quotes two route
counts, `_read_item_permalink` the control labels, `_read_messaging_badge` the badge label, and the
comment, publish and send gates interpolate `reading['error']`, which several dom readers fill with
`f"{type(exc).__name__}: {exc}"`. Those are page TEXT by design in some readers ("returns_text" in
the reader-leak baseline) and a message rendering in others; either is a different repair from
this one.

### 10.2 (c) THE ASSERTED-NAME GUARD NOW READS A NAME WRAPPED ONTO THE NEXT LINE

Built by one implementer child to a closed brief (its files only; it committed nothing), then
reviewed and extended here. `scripts/check_asserted_names_resolve.py` finds a slot phrase and a
backticked UPPER-KEBAB name on ONE line; hard-wrapped prose splits them, and section 7 item 4
measured this record doing exactly that. Both slot forms now also match ACROSS ONE line break --
the phrase ending the previous line and the name opening this one, or the name ending this line
and "blocker" opening the next -- only between two non-blank lines, never through a fence and
never into or out of a table row. The review added one thing: a name wrapped inside emphasis
(`**` before it) was still missed, because the same-line check strips `*` and `_` and the join did
not; it does now.

**SHOWN FAILING.** The child's control, `test_the_detector_finds_a_wrapped_assertion`, plants
both mirror shapes with names that resolve nowhere; against the unmodified guard it failed with
`found == set()` -- neither wrap seen. After the fix it passes, and the review's second control,
`test_a_wrap_is_joined_across_one_ordinary_line_break_and_no_further`, plants the emphasised
join (convicted) and a blank line, a fence, a table row and two line breaks (none joined). The
module: 11 passed; the guard stays well under its speed bound.

**WHAT THE JOIN FOUND ON ITS FIRST RUN: six sites, 59 -> 65 candidates, 3 -> 9 convictions.**
Each is "under" ending a line with a backticked id opening the next -- the shape this guard has
always convicted on one line, and whose MEASURED table counts other-vocabulary names as findings.
Five are registered RULING ids and one is a census STATE word; none is a blocker:

    _audit/2026-09-20-the-premium-block.md         EXCLUDED-RULED (a state)       pinned
    _audit/2026-09-21-the-auth-reason-leak.md      ERROR-URL-ASKED-FOR-OR-NOTHING pinned
    _audit/2026-09-23-bucket1-fires.md             NO-IRREVERSIBLE-WRITE-IS-FIRED pinned
    _audit/2026-09-23-census-cleanup.md            SELF-PROFILE-EDITS-NOT-OUTWARD pinned
    _audit/2026-09-23-lane-l1-refused-reads.md     ONE-NAMED-SETTINGS-PAGE-AT-A-TIME pinned
    this record, section 1                         COMPOUND-ROW-SPLITS-ONLY-ON-STATE reworded

The five in other lanes' records are PINNED in the test's ratchet with that reason, not edited:
the repair is a one-word rewording by each record's owner, and the ratchet then demands the pin
narrow. **A DESIGN QUESTION FOR THE GUARD'S OWNER, not ruled here:** the register now makes a
ruling id resolvable in the tree, and the guard still resolves only against the blocker ledger.
Resolving ruling ids too would clear four of the five and every future "under `<RULING>`"; it
would also stop the guard catching a ruling id asserted where a blocker belongs.

### 10.3 (a) THE POSTING'S FOLLOW CONTROL, READ THE WAY THE PAGE ROOT'S IS (`N 46`, `J 103`)

**THE DEFECT, as section 7 item 1 raised it.** LinkedIn relabelled the posting's company-follow
control on or before 2026-09-19: one button in the About-the-company card, visible text `Follow`,
accessible name `Follow <the employer's name>`. The exact-label union `dom.FOLLOW_CONTROL` matched
it on 0 of 5 live postings, `read_follow_control` answered "count 0", and `shape.follow_state`
turned that into "no follow control rendered ... the page had not hydrated yet" -- false on a card
that had drawn its follower line and its button. So `linkedin_follow_company` refused on every live
posting while `N 46` and `J 103` read COVERED-UNFIRED, and `linkedin_job_detail` reported the same
wrong reason on every posting it read.

**THE REPAIR, the Page root's anchor carried over.** `read_follow_control` still reads the bare
labels exactly as before, and now also the card: the ONE button inside
`div[componentkey^="JobDetails_AboutTheCompany"]` whose name opens `Follow ` (the space keeps
`Following ...` out), BOUND when the rest of its name is the employer name the card itself draws
in its own `/company/` link. It never returns that label: a bound control is reported by the
canonical word `Follow`. `shape.posting_follow_state` answers `not_following` from exactly one
bound control; UNKNOWN from an unbound one, from several, from a card drawing BOTH conventions, and
from a `Following ...` control -- the relabelled ON label, never measured -- with a reason that no
longer blames hydration. The bare-label answers are delegated unchanged to `follow_state`. The
click is aimed through the CONSTANT selector `dom.POSTING_FOLLOW_IN_CARD`, which the verdict
accepted as matching exactly one element and Playwright's strict mode holds to one. The three
`follow_company` readings (preview, click, verification) and `linkedin_job_detail`'s
`company_follow_state` all route through the new verdict, and every reason it gives is built from
counts. Failures are logged by exception TYPE; the page-text guard caught a first version that
logged a name this module had elsewhere bound to page text, and it was rewritten before commit.

**SHOWN FAILING, then passing.** `tests/test_posting_follow_relabelled.py`, every world one
asserted edit of `tests/fixtures/job_detail.html`. Against the unrepaired code: **5 failed, 5
passed** -- the relabelled OFF control read `unknown` with the hydration reason, no click selector
was built for it, the ON shape was blamed on hydration, a card drawing both conventions was read as
`not_following`, and the verdict did not exist. After: 10 passed, and the 22 suites that touch the
follow path, the page-text inventory and the surface ran green (1059 passed once the log line was
rewritten).

**THE CENSUS.** `J 103` (`jobs.md`) and `N 46` (`network.md`) keep COVERED-UNFIRED -- the tool has
still never fired -- and each cell now says the gate reads the relabelled control, since when, and
which test shows it. What only a live fire settles: the ON label, and whether every live posting
draws the card's name link the binding reads.
