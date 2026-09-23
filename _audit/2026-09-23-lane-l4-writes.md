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
exactly ONE row has left since, `M C85`, whose direction cell was repaired `W` -> `R+W` under
`COMPOUND-ROW-SPLITS-ONLY-ON-STATE`. It is one of the three `R+W` above, and it is a row this lane
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
attribution in any message):

* `b35ed54` -- the classification: the table, its checker, 20 tests, register 61.1-61.4.
* the build commit that follows this section -- `N 47` built, the second-use guard, the coercion
  and label repairs, the R2 build-ready columns, register 61 completed, this record.

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
   the answer.
2. **Ten functions in `writes.py` still coerce page values with `int()`** -- named in section 4.6.
   None was touched here, so none was repaired.
3. **The 18:15 ruling is not registered** -- section 5. Until it is, R2's label rests on a relay.
4. **The asserted-name guard reads one line at a time, so a slot phrase wrapped across a line break
   is invisible to it.** MEASURED on this record: section 1 wraps "under" at a line end with a
   ruling id opening the next line, and `scripts/check_asserted_names_resolve.py --all` lists no
   candidate site there, while the unwrapped instance in section 4 was convicted. Harmless here --
   that id resolves in `_audit/RULINGS.md` -- but an unresolvable BLOCKER name wrapped the same way
   would pass.
