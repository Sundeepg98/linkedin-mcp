# Lane L8: the outward classes built behind the grant

Base: `1902fcb` (master, "rulings: names at runtime (the operator's), their six
mitigations, and the classes built behind the grant"), measured with
`git log -1` at lane start, 2026-09-24 08:35.

Rulings this lane builds under, all registered in `_audit/RULINGS.md`:
- `OUTWARD-CLASSES-BUILT-BEHIND-GRANTS` (`_audit/2026-09-24-rulings-names-at-runtime.md`):
  repost or share, endorse or recommend, and delete or withdraw one of HIS OWN
  items are BUILT behind the single-use grant, off by default, fired only at a
  target he names; `PERMANENTLY_FORBIDDEN` keeps only the entries whose
  grounds are mitigations.
- `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET` and `PAGE-MAY-VETO-NEVER-SUPPLY`
  (`_audit/2026-09-24-rulings-notify-veto-and-who-which.md`).
- `WRITE-CLASS-B`, `OPERATOR-NAMES-THE-TARGET`, `PEOPLE-DATA-MITIGATIONS`
  item 6 (a target is a link or an id the caller supplies, never a name), and
  `MENTION-COMPOSITION-RULING` (stands).

Status: DONE OFFLINE, 2026-09-27. Master merged into the lane once, at the end.
Nothing fired: no grant was minted outside the offline fixture tests, and no
LinkedIn page was loaded. The live and capture queues at the foot of this
record are what remains, each aimed at a target HE NAMES.

**THE LANE RAN IN TWO SESSIONS.** The first (2026-09-24, 08:35 to about 10:30)
stopped at a usage-limit restart with two children in flight; the second
resumed on the orchestrator's order on 2026-09-27 at 13:20, sampled the disk
first, and salvaged what the first left (section 8). Dates in this record are
the dates things happened: the forbidden set was narrowed on 2026-09-24; the
build was salvaged and the census moved on 2026-09-27.

## 1. What was on disk before anything moved

**The forbidden set held nine entries.** Three of them are this lane's:
`repost_or_share` (narrowed 2026-08-30 to "a repost republishes SOMEBODY
ELSE'S item"; its measurement: the Repost control is a button with
`aria-expanded='false'`, 3 on the feed and 8 on his profile, menu never
opened), `endorse_or_recommend` (reason replaced 2026-08-30 by a
MEASUREMENT: zero endorse controls on every surface this package may load, so
only a third party's profile carries one), and `delete_or_withdraw_anything`
("destruction is not a write this design covers", with the note that FIVE
specs cite it in `reversible_by`).

**What the ruling left standing is exactly six:** anti-detection, loops /
sweeps / scheduled writes, auto-accept or auto-reply, de-anonymising a viewer,
loading a third party's profile FOR A MEASUREMENT, and marking notifications
read.

**The census footprint of the three keys, measured with the shipped walk**
(`scripts/check_write_classes.walk` joined to `exclusion-basis.tsv`):
- 30 rows EXCLUDED-RULED whose exclusion family (in
  `scripts/check_exclusion_basis.py`) is one of those keys' two live families:
  27 in the destruction family, alone or first, and 3 in the family that pairs
  the third-party-profile rule with the endorsement key. The repost family
  was already EMPTIED by lane R (`M C20`, `M C21` returned 2026-09-23).
- About 35 GAP rows whose cells cite one of the keys: the recommendation rows
  (`P F2`-`F9`, `N 119`-`128`) whose blocker NAMED `endorse_or_recommend`, the
  two repost rows whose blocker named `repost_or_share`, and a family of
  compound rows ("its delete half stays refused by
  delete_or_withdraw_anything").

**What has been captured, counted offline over the 25 `cap-*.html` files in
the main checkout's `_state/` (all dated 2026-09-20) and the 29 tracked HTML
fixtures -- counts and shapes only, no text or id left the reading:**

    his own /groups/ page (cap-rc-groups)   5 row-scoped 'More options for <group>'
                                            disclosures (aria-expanded=false); 5
                                            'Leave this group' items PRESENT in the
                                            DOM inside aria-hidden menu containers;
                                            each row holds exactly one group id; no
                                            dialog, no role=menu
    the Repost control                      drawn CLOSED in four captures (8, 5, 1, 1
                                            text nodes); no capture holds its menu open
    endorse controls                        0 in all 25 captures and all 29 tracked
                                            fixtures -- a re-take of the 2026-08-30
                                            zero, on a larger corpus (29 fixtures, not
                                            13), and still no third party's profile
                                            anywhere on disk
    his own post's control menu             not a capture file; MEASURED LIVE by the
                                            live lane 2026-09-23/24 and encoded in
                                            linkedin_server/share_link.py and
                                            tests/fixtures/synthetic/own_post_menu.html:
                                            'delete post' and 'edit post' drawn on his
                                            own post, absent on another member's
    a comment's own overflow menu           measured 2026-09-04 (_audit/INSTRUMENTS.md):
                                            'Copy link to comment', 'Edit', 'Delete'
    the draft-application discard           tests/fixtures/jobs_tracker_row.html: a
                                            'Delete' control and the prompt 'Discard
                                            draft application and remove this job?'
                                            with Yes / No -- the one act of the class
                                            captured end to end (census J 69)
    the Sent Invitations manager            never loaded; /mynetwork/invitation-manager/
                                            sent/ is REFUSED by the read gate on
                                            'invitation' (measured 2026-09-24)
    his recommendations section             never loaded; /in/me/details/recommendations/
                                            is REFUSED by allowlist silence (measured
                                            2026-09-24)

## 2. The forbidden set, narrowed

Commit `efa3d8f` (on this lane's branch, which master holds only once the lane
merges; before that it does not resolve on `master`). `writes.PERMANENTLY_FORBIDDEN`
now holds exactly the six the ruling names:

    any_anti_detection_technique
    any_loop_sweep_or_scheduled_write
    auto_accept_or_auto_reply
    deanonymise_a_viewer
    load_a_third_partys_profile_to_measure_a_control
    mark_notifications_read

**The three retired entries were not deleted.** They moved BYTE-FOR-BYTE into
`linkedin_server/outward_classes.py` :: `RETIRED_PERMANENT_REFUSALS`, as dict
entries of the same form, so the census families filed under them still
resolve their citation (`"delete_or_withdraw_anything": (` occurs there). The
equality was checked against the live dict before removal, and the texts are
pinned by digest (`tests/test_outward_classes.py`):

    repost_or_share               7c1655c3ac2b725c
    endorse_or_recommend          27dac326eead5ec9
    delete_or_withdraw_anything   79f0867297b22471 -> 1cff9e239b05cb35

The third digest moved ONCE, at the merge of master (section 9). Lane L5 had
rewritten that entry on master to count SIX specs, `send_reply` the sixth. The
text the retirement removes from master is that one, so it is the one kept. It
was compared equal to master's dict value before the swap.

**Their facts were carried, not thrown away.** Each measured fact sits in the
record that needs it (`OUTWARD_CLASS_SPECS[...].carried_facts`): the Repost
disclosure counts in `repost_item`; the zero-endorse-control counts (13
fixtures, 222 live controls) and "only a THIRD PARTY'S PROFILE carries one" in
`endorse_skill`, where they now say WHERE the control is rather than that it
is out of reach. `tests/test_writes_nine.py` pins both carries.

One surviving entry was touched, line-locally: `load_a_third_partys_profile_
to_measure_a_control` opened "it is the rule the endorsement ruling above
rests on", and nothing stands above it now; it reads "the endorsement ruling
that stood above it until 2026-09-24 rested on". Its dict key -- the anchor
the census family `NO-THIRD-PARTY-PROFILE-LOAD` cites -- is unchanged.

**Tests that pinned the forbidden set, re-derived from the evidence:**
- `tests/test_writes.py::test_every_permanent_refusal_carries_its_reason`
  asserted `len(PERMANENTLY_FORBIDDEN) >= 8`. A floor goes red for the right
  change and green for a wrong one, so it now asserts the set BY NAME against
  `outward_classes.SURVIVING_PERMANENT_REFUSALS` and the three retired names
  absent.
- `tests/test_writes_nine.py` section 7: the "three surviving refusals" test
  now asserts two of the three RETIRED (and kept verbatim) and the third
  standing; the endorsement and repost tests read the retired texts where they
  now live and pin the carried facts; the "FIVE specs" test is rewritten --
  see section 3.

## 3. The `reversible_by` claims that leaned on the destruction entry: five on the base, six at the merge

The retired note said "Shortening it would silently make five reversibility
claims wrong at once." The answer is to restate the five, each by name, not to
keep the entry. Each now quotes what it used to say (the house convention for
a retraction), names the ruling, and names the record in `outward_classes`
that governs its undo with that record's real status:

| spec | restated `reversible_by` opens | ground now | record, status |
|---|---|---|---|
| `apply_job` | NOBODY | LinkedIn's own Help Center a512388: "You cannot edit or withdraw an application once submitted through LinkedIn" (quoted in `_audit/_census/jobs.md`) | `withdraw_application`, BLOCKED -- not a LinkedIn capability |
| `publish_post` | NOT YET through this server; by hand, he can | his own post's menu draws 'delete post' (live lane, 2026-09-23/24); what it draws when pressed is uncaptured | `delete_own_post`, NEEDS-CAPTURE |
| `comment_on_item` | NOT YET through this server; by hand, he can | a comment's own menu draws 'Delete' (2026-09-04); what it draws is uncaptured; one-page aim by id | `delete_own_comment`, NEEDS-CAPTURE |
| `send_invitation` | NOT YET through this server; by hand, he can | LinkedIn offers the withdraw (Help Center, network.md s8.5); the Sent manager is refused on 'invitation' | `withdraw_invitation`, BLOCKED |
| `send_message` | NOBODY: a delivered message cannot be recalled | delivery itself: it arrives as an email and a notification. LinkedIn documents a 60-minute delete (census `M M12`, a550661); what it removes, and from whom, is unestablished here, and it is unbuilt (hedged at the verification, section 9.5) | none |
| `send_reply` (lane L5) | NOBODY: a delivered reply cannot be recalled -- restated at this lane's merge of master (section 9) | as `send_message` | none |

**The sixth arrived with the merge.** What follows was written before it, and
it is exactly what the merge did (section 9). The one addition:
`reversibility_procedure`, which ended "Deleting stays forbidden here whatever
the menu offers", is restated the same way.

**`send_reply` is not on this lane's base** (`1902fcb` has no such spec; lane
L5 is integrating it). Read off L5's own commit `5eadfe7` (*messaging: a
receipt-safe inbox and a reply that confirms itself*), its two printed fields
lean on the retired entry:

    reversibility_evidence  "... and deletion is permanently forbidden in this
                            design whatever LinkedIn offers."
    reversible_by           "NOBODY, through this server. Deletion is permanently
                            forbidden here at any confirm level
                            (delete_or_withdraw_anything), so an un-send does not
                            exist in this design."

**THE RESTATEMENT FOR WHOEVER MERGES L5 AND L8** -- the verdict is unchanged,
its ground is `send_message`'s:

    reversible_by  "NOBODY: a delivered reply cannot be recalled. This field used
                   to say \"Deletion is permanently forbidden here at any confirm
                   level (delete_or_withdraw_anything)\"; that refusal was retired
                   2026-09-24 (OUTWARD-CLASSES-BUILT-BEHIND-GRANTS), so the ground
                   is the reply's own nature: it is delivered to a person and
                   arrives as an email and a notification too. LinkedIn's
                   60-minute delete (census M M12) removes it from a thread,
                   never from an inbox, and is unbuilt here."
    reversibility_evidence  keep its first sentence; replace the retired clause
                   with "This field used to add \"deletion is permanently forbidden
                   in this design whatever LinkedIn offers\"; that refusal was
                   retired 2026-09-24, and the 60-minute delete is unbuilt (census
                   M M12, the per-message menu never opened)."

(Applied at the merge as drafted. The clause on what the 60-minute delete
removes was then hedged, at the cold verification. Nothing in the repository
quotes a550661 beyond its title -- see section 9.5, D-C.)

and add `"send_reply": (None, "NOBODY")` to the `restated` table in
`tests/test_writes_nine.py::test_the_claims_that_depend_on_the_destruction_refusal_are_the_measured_ones`,
which names the five it checks and cannot see a sixth until it is added. The
merge will also conflict on `PERMANENTLY_FORBIDDEN` itself (L5 carries the
nine-entry dict): take this lane's six.

Two evidence fields were stale by the time this lane read them, and were
corrected in the same commit because the gate prints them beside
`reversible_by`: `publish_post.reversibility_evidence` said the post menu's
"ITEMS have never been read" (the live lane read them), and
`comment_on_item.reversibility_evidence` said "no comment's own overflow menu
has been read" (one was read 2026-09-04). Both quote the old sentence.
`reversibility_class` stays STILL-UNKNOWN on all five -- the affordances are
drawn, and no deletion has ever been observed.

`tests/test_a_spec_may_not_assert_what_the_code_denies.py` (the guard on the
prose the confirm block prints) passed over the restated text, with the rest
of `tests/test_writes_nine.py`: 167 passed.

## 4. The specs

`linkedin_server/outward_classes.py` :: `OUTWARD_CLASS_SPECS` records every act
the lane was asked to build, with the status the evidence supports. A record
may not claim a build that `writes.PERFORMABLE` does not hold, and a build may
not sit behind a record that says it waits (`tests/test_outward_classes.py`,
both directions, each rule shown failing on a planted copy). Every target is
a link or an id the caller supplies (`item_urn`, `profile_link_and_skill`,
`group_id`, ...); the closed list has no name-shaped kind, and a planted
`member_name` kind is shown failing.

**THE RULE THE LANE WAS GIVEN, APPLIED ACT BY ACT: build only against a DOM
that has been captured.** Where the control an act would PRESS has never been
captured, the record says NEEDS-CAPTURE and carries the capture: the page,
the state, the element, and why taking it cannot fire the act.

| act | status | why | census rows |
|---|---|---|---|
| `withdraw_from_group` | BUILT (section 6) | the only act of the three classes whose pressed controls are in a capture file: his own `/groups/` page (2026-09-20) holds the row-scoped disclosure and the `Leave this group` item, and the 2026-09-05 probes measured the menus live; the address is admitted | `M C63`, `N 64` |
| `repost_item` | NEEDS-CAPTURE | the Repost control is captured CLOSED four times and its menu never; the items the menu offers are what the act presses | `M C20` |
| `repost_item_with_thoughts` | NEEDS-CAPTURE | the same menu, and the composer its second item opens | `M C21` |
| `endorse_skill` | BLOCKED (NEEDS-CAPTURE until the verification, section 9.5, F-4) | no endorse control anywhere on disk (re-taken: 0 in 25 captures and 29 fixtures); it lives on a third party's profile, loadable only inside his named act -- and `/in/<slug>/` is refused by the read boundary, with no code path loading it yet, so that route comes before the capture | `P E4`, `N 111`, `N 112` |
| `request_recommendation` | BLOCKED (as above) | the named member's profile `More` menu and the form it opens, behind the same refused route; the own-profile route aims by a name typeahead, measured dead and forbidden as an aim | `P F2`, `N 119` |
| `give_recommendation` | BLOCKED (as above) | as above, the `Recommend` item and its form | `P F3`, `N 120` |
| `delete_own_post` | NEEDS-CAPTURE | the menu is measured live ('delete post' drawn on his own post); what pressing it draws is not, and it may itself be the act -- so the capture is taken only on a post he names for deletion | `M C19` |
| `delete_own_comment` | NEEDS-CAPTURE | the comment menu is measured ('Delete'); what it draws is not; aiming by comment id is measured on one page only | `M C31` |
| `withdraw_invitation` | BLOCKED | the Sent Invitations manager is refused by the read gate ('invitation'), and its /mynetwork/ badge cost is unmeasured; an exact-url admission comes before any capture | `N 10`, `N 12` |
| `withdraw_application` | BLOCKED | NOT A LINKEDIN CAPABILITY for a LinkedIn-submitted application (Help Center a512388); no census row (the jobs census excluded it from the denominator) | -- |

**THE CHEAPEST NEXT BUILD IN THE CLASS IS NOT ON THE BRIEF'S LIST, AND IT IS
NAMED RATHER THAN BUILT.** Discarding a DRAFT application (census `J 69`) is
deleting one of his own items, and it is the one act of the three classes
captured end to end: `tests/fixtures/jobs_tracker_row.html` carries the draft
row's `Delete` control and the prompt 'Discard draft application and remove
this job?' with `Yes` / `No`, on `/jobs-tracker/?stage=draft`, which the read
gate admits. It is not built here because the lane's list names the acts to
build, and because the fixture holds TWO prompts and TWO overflow controls for
one row -- which control opens which prompt is a reading the build would have
to make first. Its row names that as its blocker.

## 5. The census

**THE RULE APPLIED.** `EXCLUDED-RULED-ADMISSION` admits an exclusion on one of
four written grounds, one of which is "a writes.PERMANENTLY_FORBIDDEN key". A
row whose only written ground was one of the three retired keys has no ground
left, so it returns to GAP with its blocker NAMED in its own cell; a row with a
second written ground stays on that ground alone. Nothing here re-pins a count
(section 5.3 lists the moves).

### 5.1 The decisions, row by row

Of the 30 EXCLUDED-RULED rows whose exclusion family rests on a retired key
(27 in the destruction family, alone or first; 3 in the family pairing the
third-party-profile rule with the endorsement key), **29 return to GAP and one
stays**:

* **`P N28` (close the account) STAYS EXCLUDED-RULED on ground one alone** --
  `/close-accounts` entered the forbidden tuple on 2026-08-31 aimed at exactly
  this capability (family `ACCOUNT-END-SUBSTRINGS`, measured refusing
  `/mypreferences/d/close-accounts/` on 2026-09-24). Ground two left with the key.
* **In the classes the ruling built -- his own items -- and blocked on a
  capture or an address:** `J 69` (discard a draft application -- captured,
  unbuilt: the cheapest next build, section 4), `J 87`, `P E5`, `P F5`, `P I11`,
  `P K7`, `P M3`, `M M12`, `M M26`, `M C17`, `M C19` (`delete_own_post`),
  `M C22`, `M C31` (`delete_own_comment`), `M C62`, `M C77`, `N 10` and `N 12`
  (`withdraw_invitation`), `N 96`, `N 110`, `N 113`, `N 125`, `N A15`.
* **Endorsing, through the named member's profile:** `P E4`, `N 111`, `N 112`
  (`endorse_skill`), each BLOCKED on the missing route that loads
  `/in/<slug>/` inside his named act (the read boundary refuses that address
  today), then a capture there. They read "NEEDS-CAPTURE inside his named act"
  until the verification (section 9.5, F-4).
* **OUTSIDE THE THREE CLASSES -- a decision point for the orchestrator, not
  decided here:** `N 29` (remove a connection -- a relationship with another
  member, not his item), `N 141` (block a member -- the ruling that lets a
  named member's profile load names connect, message and the note, not
  blocking), `N A14` (remove another member from his event), `P N27` (merge or
  close a duplicate account -- an account is not an item). Each is GAP because
  the key that held it is gone and no other written ground reaches it; each
  names as its blocker that the three classes do not include it, plus what else
  stands (a capture, an admission, an organiser precondition). Master's `P P2`
  (delete his account data) joined this list at the merge (section 9.2). The
  orchestrator decided all five on 2026-09-27; section 10 applies both
  rulings.

The GAP rows whose blockers NAMED a retired key keep their state and restate
the blocker: the repost pair `M C20` / `M C21` (the Repost menu capture), the
recommendation rows `P F2`-`F9` and `N 119`-`128` (the named member's profile
for request, give and revise; his own recommendations section --
`/in/me/details/recommendations/`, refused by allowlist silence on
2026-09-24 -- for the rows about recommendations he received or gave), and the
compound rows whose "delete half stays refused by delete_or_withdraw_anything"
(the delete half now waits on the same blocker as the rest of its row, which
its cell names; it is unbuilt, not refused -- the cells said "the same capture"
until the verification, section 9.5, F-9).

**`M C63` and `N 64` (leave a group) move GAP -> COVERED-UNFIRED** on the
build in section 6. Their class-table lines cite `GROUPS-ADDRESS-BUYS-NO-WRITE`
("each needs its own url, its own write sanction and its own ruling"): the
build pays all three -- the url is the admitted `/groups/` root, the sanction
is the WriteSpec behind the grant, the ruling is
OUTWARD-CLASSES-BUILT-BEHIND-GRANTS.

### 5.2 The edits

This lane's census child applied the edits from the decisions above, and the
lead reviewed them. Two lane commits carry them: "census: the rows the three
retired keys held ..." and its follow-up "census: P A23 split ...". Every
marker is dated the day the move landed, 2026-09-27. The retirement it cites
is dated 2026-09-24, the day the key left the dict.

- **29 rows to GAP.** Each carries the marker `RETURNED TO GAP 2026-09-27 BY
  LANE L8 (... s5)` and `BLOCKER, NAMED:` in its own cell, with the old text
  kept. Every row was re-parsed by the shipped `count_census_states.classify`
  after the edit.
- **`P N28` re-grounded** in place, on `/close-accounts` alone.
- **About 45 cells restated**, state unchanged:
  - the delete halves of compound rows ("unbuilt, not refused");
  - the repost pair;
  - the recommendation rows (the named-profile route, or his own
    recommendations section);
  - `P E6` and `N 114` (the `/endorse` substring still blocks);
  - `M C35`, `M C82` and `N 193`;
  - `P D27`, `M C67` and `P L3`, the rows whose written TRIGGER named the
    destruction key.
- **`M C63`, `N 64`**: COVERED-UNFIRED, `built:withdraw_from_group`.
- **Side tables:**
  - `write-classes.tsv`: 26 lines added under three new acts (`endorse`,
    `delete-or-withdraw-own`, `outside-the-classes`, all R3), 22 re-queued,
    and the two built.
  - `exclusion-basis.tsv`: 29 lines removed. The three families are
    re-pointed to `outward_classes.RETIRED_PERMANENT_REFUSALS` and declared
    EMPTIED.
  - `jobs-directions.tsv`: `J 69` and `J 87` added.
- **Instruments.** `classify_writeoff_reasons`'s fallback names the six
  survivors. Its live-key test used to assert a floor of nine and went red on
  the narrowing, for the right reason; it now asserts the six by name.
- **The follow-up**, from what the child found beyond the decisions:
  - **`N 125`.** Its R/W cell `W (also R5)` read as direction `unknown`,
    which kept the row out of the write population. The note moved into the
    state cell, as lane R's convention for section K has it. The row then
    gained its class line, and the R5 control still counts 9.
  - **`M M32` re-grounded.** The loop key alone refuses all three thirds.
  - **`P A23` SPLIT under COMPOUND-ROW-SPLITS-ONLY-ON-STATE.** Its only other
    ground, the destruction key, is retired. The desktop delete of his own
    recording is in a class the ruling built, while recording and editing
    stay mobile-app only (ground four). The halves now need different states,
    so there is a new row `A23b`, GAP, with its blocker named, following the
    `L2 -> L2b` precedent.
    - This split exposed a real parser gap: the write-classes self-row
      citation did not admit a split suffix. It now does, with a test shown
      failing on the old regex (register section 80.4).
    - Unlike L2, `A23` kept its capability text, and section A's heading
      still says `(29)` over 30 rows.
  - **`mcp-inventory.md`.** The reversibility-table rows for `apply_job`,
    `publish_post` and `comment_on_item`, and four sentences of its
    Deliverable Three, are restated to the grounds section 3 gives.

**Left as they stand, on purpose:**
- The network.md headings `B` ("all EXCLUDED-RULED") and `D` ("10
  EXCLUDED-RULED, 1 GAP") were already stale after lane R, which left them.
- Heading `K` is also a control in `classify_writeoff_reasons`.
- The census COUNTS sections are recounts, not claims to patch.
- `mcp-inventory.md`'s COUNTS line "the undo is permanently forbidden here,
  or no selector for it exists | 6".

### 5.3 The pin moves -- measured on the merged tree, NOT re-pinned

The brief said not to re-pin. Each figure below is master's pin at `2eb90ad`
against the tree after this lane's merge of master (section 9), measured by
the instrument named. Every move is this lane's own work, except the one
master row the merge returned (`P P2`).

| instrument | pinned on master | measured on the merge | what moved it |
|---|---|---|---|
| census row population: `tests/census_row_pin.json` (`pin_census_rows.py --write`); `PINNED_ROW_TOTAL`, `PINNED_SLICE_ROWS` | 769, P 235 | 770, P 236 | `P A23b`, the split |
| `test_a_census_locator_names_its_row` literal | 769 | 770 | the same row |
| `census_completion.PINNED` | stated_rows 769, capabilities 783, achievable 698, capabilities_achievable 712, gap 564, gap_write 353, gap_unknown 107, out_of_scope 71, adjudicated 205, delivered_broad 115, unfired 36, b1_standing 13, jobs_gap 107, jobs_dir_w 58 | 770, 784, 729, 743, 593, 380, 109, 41, 177, 117, 38, 15, 109, 60 | 30 rows out of scope back to GAP (this lane's 29 and master's `P P2`); `M C63` / `N 64` COVERED-UNFIRED; `A23b` added; `N 125` read as W; `J 69` / `J 87` gaining a direction |
| `census_completion.PINNED_B1_ROWS` | -- | + `M C63`, `N 64`, held by OPERATOR-NAMES-THE-TARGET | the build |
| write-classes split (`test_write_classes`) | (16, 36, 306) | (16, 36, 335) | 29 new R3 lines: section 5.2's 26, `N 125`, `P A23b`, `P P2` |
| messaging triage headline (`test_triage_instrument`) | 124 {R 17, W 103, R+W 4} | 131 {R 17, W 110, R+W 4} | seven M rows back to GAP (`C17`, `C19`, `C22`, `C31`, `C77`, `M12`, `M26`), less `C63` |
| GAP rows on refused addresses (`EXPECTED_GAP_ROWS`) | 73 | 78 | `M C62` ('/withdraw'), `N A15` ('/invite', '/withdraw'), `P F5`, `P K7`, `P M3` ('/delete') |
| pointer graph (`measure_pointer_graph.py --pin`) | 66 | 65, 4 moved | `P B3 -> P B2` and `P E5 -> P E4`: the donor verdicts read ACCOUNT-FACT beside US-RULING now; `P F4 -> P F3`: US-BOUNDARY joined US-RULING when the F-4 fix named the refused profile (section 9.5), as it did for `P E4`; `M C63`'s `same` was struck when it was built, so its pointer is gone |

The census as a whole (`count_census_states`, unpinned), on the merge: 770
stated rows; GAP 593, EXCLUDED-RULED 29, COVERED-UNFIRED 35, XR 2.

## 6. The build: leaving a group, census `M C63` and `N 64`

**`linkedin_withdraw_from_group(group_id, confirm_token)`** -- spec
`withdraw_from_group` in `writes.SANCTIONED_WRITES` (right after
`mark_company_interest`), performable, grant-gated, off by default, one action,
one caller-supplied numeric id, consumed once. Readers and verdicts in
`linkedin_server/group_leave.py`; tests in `tests/test_leave_group.py` over the
synthetic `tests/fixtures/synthetic/groups_leave_menu.html`. Built by this
lane's child in its own worktree on 2026-09-24; the session stopped before the
child committed, and on 2026-09-27 the lead salvaged its uncommitted work
whole, reviewed every hunk, and merged it onto this branch. The merge was
proven both ways -- applying the child's hunks onto the lane, and the lane's
hunks onto the child's file, produce the same `writes.py` -- and the child's
last run of its own file was green (23 passed), as was the lead's on the
merged tree.

**WHY IT IS NOT CALLED `leave_group`, as the 2026-09-05 spec proposed and the
child first built it.** The naming law
(`tests/test_writes.py::test_a_sanctioned_write_cannot_evade_the_law_by_being_renamed`)
requires a sanctioned write's tool name to carry a word from
`readonly.WRITE_VERBS`, and "leave" is not one. Adding it was MEASURED and
refused: of the 54 registered tool descriptions, 8 contain the whole word, six
of them READ tools, which the docstring check would then read as write claims.
"withdraw" is on the list and is the ruling's own verb for this class. The
tool's docstring says it withdraws his MEMBERSHIP and is not the separate,
unbuilt act of withdrawing a pending request to join (`M C62`). The first name
had also discharged the asserted-name guard's spec-document mark's only
example; that mark, briefly deleted, is restored, because the spec's name
stays unbuilt (register section 80.3).

### 6.1 What it rests on, measured

- **The address.** `/groups/`, the admitted Groups root, is the ONE address
  this action loads -- a CONSTANT, so the id never enters a navigation
  (PAGE-MAY-VETO-NEVER-SUPPLY by construction). The page can only refuse an
  id; it cannot supply one.
- **The controls, from the capture** (`cap-rc-groups.html`, 2026-09-20, read by
  the child offline with JavaScript off and no network, counts only): 10
  disclosures (`button[aria-expanded]`), 5 of them row-scoped by the walk below;
  10 numeric group anchors, one per group; 5 `Leave this group` items in the
  DOM, all under an `aria-hidden=true` container and none pressable while
  closed; per id, exactly 1 disclosure, 1 row and 1 leave item for the 5
  memberships and 0 for the 5 suggestions; an id with its last digit dropped
  matches 0 (exact-id matching holds on the real hrefs). With one menu opened
  in memory, exactly one item became pressable, and the in-row gate proceeded
  for that row's id and refused the other nine.
- **The rule, from the 2026-09-05 probes.** The row is found FROM THE CONTROL:
  the nearest ancestor of an `aria-expanded` button that holds a numeric group
  anchor, qualifying only if it holds anchors of exactly one id. The
  disclosure's own label carries the group's NAME and is read nowhere.

### 6.2 The act, two presses through the one click site

1. The preview loads `/groups/` and requires exactly one row-scoped disclosure
   whose row carries the id he named (`member`); anything else is `unknown` or
   `not_member` and mints nothing. The block prints the id and the counts, and
   says in words that the group's name is not read.
2. At confirm, the same reading is taken fresh; click 1 is that row's
   disclosure.
3. A gate re-reads the page (briefly polled) and appends `Leave this group` to
   the SAME click queue only if exactly one VISIBLE leave item is on the whole
   page and it sits inside the target row (`MENU_ITEM_ACTIONS`, kept separate
   from apply's pinned `TWO_CLICK_ACTIONS`). Otherwise nothing more is pressed
   and the receipt says which condition refused.
4. After click 2, the page is COUNTED before anything navigates: visible
   dialogs and the buttons in them. **A dialog there is a further step that
   opened and was NOT taken** -- the receipt says so in those words.
5. The verification is a FRESH render of `/groups/`: a row still carrying the
   id is `member` (performed false); the page drawing other membership rows and
   none with the id is `not_member` (performed true); no membership row drawn
   at all is `unknown`.

`readonly.SANCTIONED_MUTATIONS` is unchanged: both presses drain `perform`'s
one literal click. A click error for this action carries its exception TYPE
only, because a Playwright message can print the element it resolved and this
element's label is the group's name.

### 6.3 What is not measured, and which way each gap fails

- **What pressing `Leave this group` draws.** Fails closed: a confirmation is
  counted and never answered; the fresh render then reads `member`, performed
  false. The first supervised press is the measurement (live queue L1).
- **Whether the menu opens in place.** A menu drawn outside the row is refused
  by the in-row condition (a planted portal menu is shown failing).
- **Whether a group left can be rejoined.** `reversible_by`: NOT through this
  server -- no join write is built (census `M C61`), an approval-gated group
  needs a manager, an unlisted group may not be findable again. Treated as
  irreversible; `reversibility_class` STILL-UNKNOWN.
- **His last group.** With no other membership row, the fresh render cannot
  tell a finished leave from an undrawn page and answers `unknown` by
  construction.

### 6.4 The controls (`tests/test_leave_group.py`)

The three grant controls with zero navigations on every refusal (no grant /
forged / unredeemed / not a grant; a grant for another group or another verb;
a second use of the token and of the grant object, the latter shown failing
without its flag); the aim refusals at the verdict and at the preview with no
grant minted (id absent, id on a suggestion row, id on two rows, no row-scoped
disclosure, a name given as the id -- refused and not repeated); the exact-id
rule shown failing as a prefix match; the menu gate refusing and pressing
nothing further (item never visible, two items in the row, every row opening),
with the in-row condition shown failing on a portal menu; a dialog after the
leave press counted and never answered; the end-to-end leave verified off a
fresh render; a click error carrying its type and never the element; and no
synthetic group name in any refusal, block or receipt.

## 7. Gates

**On `7e370ac` (the narrowing, before any census move or build):**
- `tests/test_writes.py`, `test_writes_nine.py`, `test_unverifiable_outcomes.py`,
  `test_preview_state_and_click_state.py`, `test_receipt_names_its_own_action.py`,
  `test_server_surface.py`, `test_tools.py`: **560 passed** in 476.7 s (`-n 4`).
- `tests/test_writes_nine.py`, `test_a_spec_may_not_assert_what_the_code_denies.py`
  and the edited `test_writes.py` test: 167 passed.
- `tests/test_no_committed_identity.py`, `test_the_package_compiles_on_its_oldest_python.py`,
  `test_readonly.py`, `test_recommendation_tally.py`: 1240 passed.
- `tests/test_prose_that_makes_a_claim.py`, `test_the_stated_guarantee_matches_the_sanctioned_list.py`,
  `test_the_other_two_count_claims_are_pinned_too.py`, `test_page_text_is_never_printed.py`,
  `test_readers_outside_dom_are_a_pinned_inventory.py`: 71 passed.
- `tests/test_outward_classes.py`: 20 passed, **2 failed as designed** until
  the build and the census land -- the BUILT record for the leave-a-group act had no
  performable spec yet, and nine governed rows still read EXCLUDED-RULED or GAP
  where their records say otherwise. That test is the instrument that proves
  the records and the census agree, shown failing on the real data first.
- `scripts/impact_gate.py --against 1902fcb --plan-only`: the impact set is 181
  of 244 test files (74%), so the gate WIDENS TO THE FULL SUITE -- touching
  `writes.py` couples almost everything. **Not run locally, by order; CI
  certifies at merge.**

**On the salvaged build, 2026-09-27, before the master merge:**
- The write-path, tool-surface and page-string batch (22 files, `-n 6`): **49
  failed, 1451 passed** on the first run. 46 of the 49 were ONE defect, and
  not a pin: the reader-leak harness (`tests/refusinggrant.py`) and the reach
  test had no synthetic value for the new `group_id` target kind, and the
  KeyError stopped every `writes` reader taking a grant from being driven for
  ANY spec. Both tables gained `"10001"`. The naming law refused the tool name
  (section 6); the readers inventory gained `group_leave.read_menu` as wired
  one hop away; the orphan-module ruling gained `outward_classes` as a record,
  not a capability. Re-run: **16 failed, 1507 passed** -- all 16 are the
  tool-surface pins and the two driven-set baselines, which move again at the
  master merge and are re-derived there, once.
- `tests/test_an_asserted_name_resolves.py` and
  `tests/test_a_correction_is_findable_from_the_claim.py`: 24 passed (after the
  rename; before it, the spec-document mark lost its only example -- register
  section 80.3).
- `tests/test_leave_group.py` + `tests/test_outward_classes.py`, serially,
  junit, NOT a quiet box (a census child running beside it): 41 tests, 1
  failed as designed (the census agreement, until the census lands). Priced by
  `ci_shard.seconds_per_file`: `tests/test_leave_group.py` **48.465 s**,
  `tests/test_outward_classes.py` **0.436 s** -- written into
  `scripts/ci_shard_timings.json` after the master merge.

**On the census commits, 2026-09-27, before the master merge.** These are
the census child's runs, reviewed by the lead.
- Every census table checker is green.
- The census and audit test set gave 13 failed and 1483 passed. Every red is
  one of three things:
  - a pin move (section 5.3);
  - the lane record's own index row, which the merge regenerated;
  - the server docstring's tool count, which the merge moved.
- One real defect was found and fixed on the way: the write-classes self-row
  regex did not admit `A23b` (register section 80.4).

**On the merged tree:** section 9.4.

## 8. The restart, and what was salvaged

The first session stopped on 2026-09-24 at about 10:30 with two children in
flight. On 2026-09-27 13:20 the lead resumed on the orchestrator's order and
SAMPLED FIRST, as the order asked:

- this worktree at `7e370ac` (a lane-branch commit that does not resolve on
  `master` until the lane merges, like every commit this section names),
  three commits past the base, the lane record untracked and coherent --
  pinned at once (`a002ff4`);
- the build child's branch had NO commits: its work -- five modified files and
  three new ones -- sat uncommitted in its own worktree, and its last run of its
  own test file had been green (23 passed). Salvaged by diffing each file
  against the base blob, applying the hunks here only where their context was
  unique, and proving the merge both ways (section 6). Nothing of it was
  rewritten except the name the naming law refused;
- the census child had made NO edit; its baseline of every census checker,
  taken at `efa3d8f` (the narrowing -- a lane-branch commit that does not
  resolve on `master` until the lane merges), survived in scratch and its
  successor reused it rather than re-taking it;
- master had moved from `1902fcb` to `96c1165` (lane L5, with `send_reply`)
  and kept moving while the lead worked. The order was to integrate it ONCE,
  at the end; section 9 records that merge.

## 9. The merge of master, once, at the end

Master was merged into the lane ONCE, as ordered, at the end: master's head
`2eb90ad` ("merge lane L7's last item: P B9 ..."), in the lane's merge commit
"merge master 2eb90ad into lane L8 ...". Master had moved under the lane from
the base: lane L5 (messaging, `send_reply`), lane L7's follow-ups and P B9,
lane S, lane D, lane Y2's itemized P-R block, and the live lane.

### 9.1 The conflicts: eleven files, each resolved by what each side changed

- **`writes.py`, six hunks.**
  - The forbidden dict keeps this lane's six. Master had rewritten
    `delete_or_withdraw_anything` to count SIX specs, and that entry is
    retired here.
  - `PERFORMABLE`, `_WRITE_SURFACE_FOR_ACTION`, `_VERIFIED_FROM`, `perform`'s
    locals and its click loop keep both sides: `send_reply` and the Premium
    badge's switch from master, `withdraw_from_group` from here. They are
    disjoint branches of one `elif` chain, and both drain the one click site.
- **Four test files.** Both sides' rows are kept, and the counts moved on the
  merged tree: 15 -> 16 performable, 16 -> 17 sanctioned. One duplicate dict
  key that the union produced was removed: `"LinkedIn messages"` appeared
  twice, the later one without `send_reply`. Left in, it would have silently
  stripped lane L5's second owner of that phrase.
- **`scripts/check_write_classes.py`.** Both acts vocabularies are kept:
  master's `data-rights-request` and this lane's three.
- **Five census tables** (exclusion-basis.tsv, messaging-and-content.md,
  network.md, profile.md, write-classes.tsv). These were resolved ROW BY ROW,
  by a keyed three-way merge over the base, taking whichever side changed each
  row. The nine hunks held 98 rows, some of them unchanged context. Measured
  afterwards from the three blobs, across the five whole tables: 288 rows had
  changed on one side only (156 on the lane, 132 on master), and none on both.
  So no row needed a judgement.

### 9.2 What the merge made untrue, restated in the merge commit

- **`send_reply`** (lane L5) was the sixth spec leaning on the retired entry.
  Its `reversible_by` now opens "NOBODY: a delivered reply cannot be
  recalled" and quotes what it used to say. Its `reversibility_evidence` and
  `reversibility_procedure` quote their retired clauses the same way.
  `tests/test_writes_nine.py` names it the sixth. A NEW RULE there reads every
  sanctioned spec's printed reversibility fields: a retired key, or
  "permanently forbidden", may appear only as a quoted retraction. The rule is
  shown failing on the exact text `send_reply` arrived with (register
  section 80.6).
- **The retired destruction text** is now master's SIX version, re-pinned by
  digest (section 2).
- **`P P2`** (lane Y2, "Delete his data") was itemized on master after this
  lane's base and filed EXCLUDED-RULED on the retired key alone. It is now
  RETURNED TO GAP with its blocker named:
  - Y2's own distinction stands: his account data is not an item he made, so
    this is none of the three classes, and Y2's reopener is now its blocker.
  - Like P3-P5, it awaits admission by name.
  - Its exclusion line left the table, it gained a class line
    (`outside-the-classes`), and the emptied family's note says so.
  Neither needed a judgement at the conflict level. `send_reply` merged
  cleanly, and so did the `P P2` census cell. `P P2`'s exclusion line did sit
  in a conflict hunk, but as a master-only row, which a keyed merge takes as it
  stands. Both were found by reading master's added lines for the retired key
  names before merging. The exclusion checker convicts a re-planted `P P2`
  line four ways, measured on a copy of the table.
- **`M M25`** (lane L5's cell) is restated. The key it was "adjacent to" is
  retired, and its blocker is now named: the conversation's own menu has
  never been opened.
- **The tool surface:** 57 tools, 41 read, 16 write. The count moved at every
  site that states it, all in the merge commit:
  - the tool-surface pin (57 tools, 89 parameters);
  - `test_server_surface.py`, whose test was renamed
    `..._fifty_seven_tools`, with its irreversible list typed by hand to
    SEVEN;
  - `test_every_tool_is_on_the_surface.py`;
  - `server.py`'s docstring and instructions;
  - the package docstring;
  - the README headline and layout.
  The two page-string baselines were regenerated: `group_leave`'s six readers
  are clean, and the tool is not driven, like every write. The two new test
  files were priced into `scripts/ci_shard_timings.json`.
- Master's `test_server_surface.py` also said "deletion is permanently
  forbidden here" of a reply, and there is no endorsement tool "because ...
  that is permanently refused". Both are restated to what now holds.

### 9.3 The commits

These are on the lane branch `worktree-agent-af690b71921f8cd52`, first parent
first, oldest last. Each resolves on `master` once the lane merges. Until
then only the branch holds them, and the SUBJECT is the key that survives.

| commit | date | subject |
|---|---|---|
| `511ed7f` | 09-27 | lane L8: what the cold verification found, fixed -- the retired refusal in two tool descriptions, six stale apply claims, a leave verdict a half-drawn page could fool |
| `ac46138` | 09-27 | lane L8 closes: the instructions test counts to sixteen, and the record gets its commits and the gates on the merged tree |
| `dda3f61` | 09-27 | merge master 2eb90ad into lane L8: the outward classes meet lanes L5, L7, S, D, Y2 and the live lane, once, at the end |
| `30e7651` | 09-27 | census: P A23 split (its delete half is his own item now), N 125 admitted as a write, M M32 re-grounded, the inventory's undo grounds restated |
| `c7fd61f` | 09-27 | census: the rows the three retired keys held -- 29 back to GAP with blockers named, M C63 / N 64 built, the side tables and instruments re-pointed |
| `dedfaee` | 09-27 | lane L8 record: the two sessions, the salvage, and the gates before the master merge |
| `3199b2f` | 09-27 | orphan modules: outward_classes is a record, not a capability -- ruled, not wired |
| `9681c5d` | 09-27 | outward_classes: the leave record's live proof counts three /groups/ loads and warns off his last membership |
| `73ea0b7` | 09-27 | readers inventory: group_leave.read_menu is wired one hop away, through the menu gate perform calls -- the read_filters shape |
| `544363e` | 09-27 | writes: the leave-a-group write is withdraw_from_group -- the naming law refused "leave" (it also restored the asserted-name guard's mark, which the commit below had removed) |
| `db480bb` | 09-27 | asserted-name guard: the spec-document mark lost its only example when leave_group was built, so it goes (reverted by the commit above) |
| `4a93ac2` | 09-27 | writes: leave one group he names by numeric id (M C63 / N 64), built behind the grant, ready and unfired |
| `a002ff4` | 09-27 | lane L8 record: pin the work in progress at the restart -- sections 1-4, the census decisions, the queues |
| `7e370ac` | 09-24 | outward_classes, send_invitation: cite the Help Center page the network census fetched for the withdraw (a568295), and its three-week wait |
| `e3a8eed` | 09-24 | outward_classes: name its constants for what they hold, so a test naming them couples to this module and nothing else |
| `efa3d8f` | 09-24 | writes: narrow PERMANENTLY_FORBIDDEN to the six mitigations; the three retired entries kept verbatim in outward_classes |

The count-map repair the merged tree's gate asked for is in `ac46138`
(section 9.4), and the verification's fixes are in `511ed7f` (section 9.5).
One more commit sits on top: this record's last edit. No lane commit carries
an AI co-author, session or generated-by line; that was checked over
`git log --first-parent --format=%B` for the range.

### 9.4 Gates on the merged tree, run and NOT run

Everything below ran on the merge commit, `-n 6 --dist loadfile` or `-n 4`,
and NOT on a quiet box: other lanes' test runs shared the machine.

**The write path, the tool surface and the page-string guards: 34 files,
3 failed, 2737 passed in 646.8 s.** The files:
- the two new files: `test_outward_classes`, `test_leave_group`;
- the write path: `test_writes`, `test_writes_nine`,
  `test_preview_state_and_click_state`, `test_receipt_names_its_own_action`,
  `test_unverifiable_outcomes`, `test_tools`, `test_send_reply`,
  `test_send_message_gate`, `test_a_spec_may_not_assert_what_the_code_denies`,
  `test_a_performable_action_can_reach_its_control`;
- the tool surface: `test_server_surface`,
  `test_the_tool_surface_is_pinned_so_a_row_must_move`,
  `test_every_tool_is_on_the_surface`,
  `test_the_other_two_count_claims_are_pinned_too`,
  `test_prose_that_makes_a_claim`,
  `test_the_stated_guarantee_matches_the_sanctioned_list`,
  `test_a_named_cost_names_a_tool_that_can_incur_it`;
- the page-string guards: `test_page_text_is_never_printed`,
  `test_tool_envelopes_emit_no_page_string`,
  `test_readers_emit_no_page_string`,
  `test_readers_outside_dom_are_a_pinned_inventory`;
- the orphan, identity and boundary guards: `test_every_orphan_module_is_ruled`,
  `test_no_committed_identity`, `test_readonly`, `test_group_page`;
- the three the order named: `test_the_package_compiles_on_its_oldest_python`,
  `test_gap_rows_on_refused_addresses`, `test_ci_shard`;
- and `test_write_classes`, `test_an_asserted_name_resolves`,
  `test_a_cited_sha_resolves`, `test_a_correction_is_findable_from_the_claim`.

Of the three reds, two are pins this lane was told not to move: the
write-classes split and the refused-address count (section 5.3). The third
was REAL: `test_the_server_instructions_name_every_write_that_ships`. Its
map from a write count to the word the instructions must say stopped at
fifteen, and it raised `KeyError: 16` -- the failure it was written to give.
The map gained sixteen in the closing commit, and `test_server_surface.py`
re-ran green: 52 passed. Before the merge commit, the five write-path files
had also run on the resolved tree: 249 passed.

**The census instruments, every script, with no pin or write flag:**
- Green: `check_write_classes` (387 lines), `check_exclusion_basis` (41/41,
  0 structural), `check_jobs_directions` (109/109), `check_read_addresses`,
  `classify_writeoff_reasons --check`, both triage scripts,
  `check_census_locators_resolve`, `check_contingent_writeoffs_carry_a_reopener`,
  `check_gap_rows_on_refused_addresses`, `check_cited_shas_resolve`, and
  `--check` on the blocker map, the rulings register and the audit index.
  The generated files were regenerated to a fixed point.
- Red only on pins:
  - `census_completion --check` refuses to report while the row pin reads
    769 against a live 770. Its figures were computed read-only with that
    one control set aside, and every other control passed (section 5.3).
  - `measure_pointer_graph --check`: the three moved pointers.
- `check_asserted_names_resolve` reports the same eight ASSERTED-ABSENT
  sites its test pins, none of them this lane's.

**The census and audit test files: 26 files, 8 failed, 522 passed in
224.7 s.** These are the census child's set plus the register, rulings and
blocker-map guards. All eight reds are the pins in section 5.3:
- bucket one;
- the row-label literal;
- the row total (two tests);
- the pointer graph (three tests);
- the messaging triage headline.

**NOT run:**
- The full suite, by order. `scripts/impact_gate.py` widens to it for any
  change touching `writes.py`; CI certifies at the orchestrator's merge.
- `tests/test_surface_census.py` and `tests/test_tracker_harvest_census.py`,
  which launch Chromium.
- Anything live.

### 9.5 The cold verification, and what it changed

The brief allowed one cold pass, and it went to a general-purpose child. The
child started from `git diff 2eb90ad HEAD`, not from this record, and made
mutations of its own, each restored. Its full report is the lane's scratch
file `verifier-report.md`. Its verdicts, and what each finding changed:

- **Q1, the forbidden set: HOLDS.** The six are exact. The three retired texts
  are byte-identical to what each last carried on master, compared with
  `ast`.
- **Q2, the restated undo claims: DEFECT.** The six `reversible_by` fields held
  against their sources; the text printed AROUND them did not. All three
  classes of defect are fixed:
  - **D-A.** Two tool descriptions still stated the retired refusal live:
    - `linkedin_comment_on_item`, "forbids deletion permanently", present on
      the base;
    - `linkedin_send_reply`, "Deletion is forbidden in this design", which
      arrived with lane L5.
    The whole-set rule read only spec fields, and its needles matched neither
    phrasing. Both descriptions now quote the old sentence as a retraction.
    The rule now also reads every sanctioned write's tool DESCRIPTION, against
    the phrasings measured on the tree, and it was run red on the two real
    descriptions before they were fixed (register section 80.4).
  - **D-B.** Printed text contradicted a restated ground, in the same spec or
    the same tool:
    - apply's "NOBODY HAS ESTABLISHED THAT LINKEDIN OFFERS A WITHDRAW AT ALL
      ... It might" stood in six places: its procedure, its tool description,
      the server instructions, two server_info notes, and a `not_yet_measured`
      entry calling a withdraw "a real LinkedIn feature". All six now rest on
      a512388.
    - send_invitation's `reversibility`, its evidence and its description rest
      on a568295.
    - publish_post's description and procedure, and comment_on_item's
      procedure, say the menus were read and what capture remains.
    Each quotes what it used to say.
  - **D-C.** "Removes it from a thread, never from an inbox" had no source,
    since a550661 is cited by title only. It is hedged, in both specs, the
    census `M M12` cell and class line, the inventory row, and section 3.
- **Q3, `withdraw_from_group`: HOLDS on all four sub-questions.** It is gated,
  aimed at one numeric id, and consumed once. It makes two presses at most,
  leaks no name, and fails closed after the press. The verifier's mutations
  M1 (dropping the in-row rule) and M2 (accepting two rows) were killed.
  Three LOW findings, all fixed:
  - **F-6.** The verification's `not_member` needed only one other row drawn,
    which a half-drawn page satisfies. It now requires EXACTLY one row fewer
    than the preview counted (`group_leave.verification_verdict`). The new
    test kills the old rule, run as a mutant.
  - **F-7.** The fixture's page-side press counters were never read. The test
    navigator now reads them off the clicked document before the
    verification replaces it.
  - **F-8.** The verifier's mutant M3 SURVIVED: deleting the verification's
    landing check left every test green. A new test drives a re-read that
    lands elsewhere, and it kills M3.
- **Q4, the records: DEFECT.** Every target is a link or an id. Two findings,
  both fixed:
  - **F-4.** `endorse_skill`, `request_recommendation` and
    `give_recommendation` read NEEDS-CAPTURE though their capture page,
    `/in/<slug>/`, is refused by the read boundary. That is BLOCKED by the
    module's own definition, the status `withdraw_invitation` got for the same
    kind of refusal. They are BLOCKED now, on one named route, keeping the
    capture that follows. The census blockers of `P E4`, `P E5`, `P F2`-`F4`,
    `N 111`, `N 119`, `N 120` and `N 124` say so.
  - **F-5.** The captures of "repost with your thoughts" and of the two
    recommendation forms pressed an item in a menu never read. Each now reads
    the menu first and aims by an exact whole name, never a prefix or a
    position: the Repost menu's expected sibling 'Repost' is a one-press
    repost and a PREFIX of the target item.
- **Q5, the census: HOLDS on states.** Eight moved rows were drawn at random.
  `P N28`'s remaining ground exists, the `A23` / `A23b` split is what the
  ruling requires, and `P P2`'s return is right. **F-9**: the compound rows'
  "waits on the same capture as the rest of the row" is now "the same
  blocker", because the rest often waits on an admission. `M C77` names its
  refused `/pulse/` address.
- **Q6, hygiene: HOLDS.** No real name, id, slug or path appears in the
  lane's added lines, and no AI attribution appears in the 15 lane commits
  that existed when it looked.
- **INFO, left as they stand:**
  - `A23` kept its whole-capability title, and section A's heading still says
    `(29)` over 30 rows. Both were disclosed in section 5.2.
  - The one clause edited in a surviving forbidden entry.
  - This record's first line is the model id, by the brief's own order. It is
    a convention every lane record here shares; whether it belongs in a
    public repository is the operator's call.

The fixes were re-checked by instruments, not by a second pass:
- the new rule, run red first;
- the mutants for F-6 and F-8, each killed by its new test;
- the census checkers, green but for the pins;
- the same 34-file batch as section 9.4, on `511ed7f`: 2 failed and 2742
  passed in 265.4 s. The two reds are the pins section 5.3 lists, the
  write-classes split and the refused-address count.

The census pins are unmoved by the fixes, with one exception: the pointer
graph now shows 4 moved pointers where it showed 3 (section 5.3). The census
and audit batch was re-run on this record's last edit: 8 failed and 522
passed in 85.2 s -- the same eight pins as section 9.4.

## 10. The rulings on the five rows, applied, and every pin re-derived (2026-09-27)

The orchestrator ordered this at about 16:35, after it had sampled the branch at
`965a13c` over master `2eb90ad`. Disk agreed with the order before anything
moved: HEAD `965a13c`; master still `2eb90ad` and an ancestor of HEAD; the five
rows read as section 5.1 describes. The orchestrator merges nothing else until
this branch lands, so this tree IS the merged tree, and the pin moves section
5.3 listed are this lane's to apply -- each re-derived here, by the instrument
that owns it, on the final tree.

### 10.1 The two rulings

The document `_audit/2026-09-27-rulings-relation-removals-and-account-destruction.md`
was copied byte-identical from the main tree (compared with `cmp`). Both
rulings are registered in `scripts/build_rulings_index.py`, after
OUTWARD-CLASSES-BUILT-BEHIND-GRANTS, with the ids, claims, binds, anchors
and notes the order gave:
- RELATION-REMOVALS-BUILT-BEHIND-GRANTS -- removing a 1st-degree
  connection, blocking a member, removing an attendee from his event: BUILT
  behind the grant, fired only at the one member he names.
- ACCOUNT-DESTRUCTION-STAYS-MANUAL -- merging or closing his account, and
  deleting the data LinkedIn holds about him: NOT built, EXCLUDED-RULED,
  with the ruling's reopener.

No document guard objected, so NO WORD of either entry or of the document
changed. The register resolves both anchors and claims both declarations:
66 rulings, 255 documents. The asserted-name check stays at its pinned 8
sites, and every cited SHA resolves. The correction and reopener scans are
in section 10.4.

### 10.2 The six rows

- **`N 29`, `N 141`, `N A14` stay GAP.** Each gains a RESTATED marker under
  RELATION-REMOVALS-BUILT-BEHIND-GRANTS. The class is ruled, so each
  "BLOCKER, NAMED:" is the build plus what the row itself still needs:
  - `N 29`: the connections list's row menu has never been opened or
    captured.
  - `N 141`: its control sits on the named member's profile, so it needs the
    named-profile route, then a capture inside his named act. Lane L5 is
    building that route on its own branch; none of it is on master, so none
    of it is cited.
  - `N A14`: he organizes no event (the N A admin precondition), and the
    attendee control has never been captured.
  The NOT-REV notes are kept.
- **`P N27` and `P P2`: GAP to EXCLUDED-RULED** on
  ACCOUNT-DESTRUCTION-STAYS-MANUAL, with the ruling's REOPENER in each cell.
  The old text is kept.
- **`P N28`: state unchanged.** The ruling is added as its capability-level
  ground, beside the forbidden-tuple entry that holds the address, with the
  REOPENER.
- **Side tables and instruments:**
  - `write-classes.tsv`: the three relation rows move to a new act,
    `remove-relation` (R3). Each gets a queue of its own
    (CONNECTION-ROW-MENU-CAPTURE, NAMED-PROFILE-ROUTE,
    EVENT-ORGANIZER-PRECONDITION) and cites both rulings. `P N27` and `P P2`
    leave the table, since they are no longer write-direction GAP rows. The
    act `outside-the-classes` no longer holds a line, so it leaves the
    closed vocabulary in `scripts/check_write_classes.py`, which says why.
  - `exclusion-basis.tsv`: `P N27` and `P P2` are filed under a new family,
    ACCOUNT-DESTRUCTION-STAYS-MANUAL. It is registered in
    `scripts/check_exclusion_basis.py` as made by the ORCHESTRATOR with
    op=NO -- the D5-PASSIVE-COST-IS-NOT-A-ROW precedent -- and anchored on
    the ruling's own two lines. `P N28` is filed under
    ACCOUNT-END-SUBSTRINGS+ACCOUNT-DESTRUCTION-STAYS-MANUAL, and the ruling's
    line is added as a source.
  - The blocker map, the rulings index and the audit index are regenerated
    by their generators.

### 10.3 The pins, re-derived on the final tree (before, then after)

| pin | owner | before | after | what moved it |
|---|---|---|---|---|
| census row population | `pin_census_rows.py --write` into `tests/census_row_pin.json`; `PINNED_ROW_TOTAL`, `PINNED_SLICE_ROWS` | 769; P 235 | 770; P 236 | `P A23b`, the split |
| stated labels | `test_a_census_locator_names_its_row` literal | 769 | 770 | `P A23b` |
| `census_completion.PINNED` | `census_completion.py --check` | (below) | (below) | each key carries its own dated cause |
| bucket one, row by row | `PINNED_B1_ROWS` | -- | + `M C63`, `N 64`, OPERATOR-NAMES-THE-TARGET | the build |
| write-classes split | `test_write_classes` | (16, 36, 306) | (16, 36, 333) | 358 + 29 - 2 = 385 lines |
| messaging triage headline | `test_triage_instrument`, new `AFTER_LANE_L8` | 124 {R 17, W 103, R+W 4} | 131 {R 17, W 110, R+W 4} | eight M rows returned, `C63` built |
| GAP rows on refused addresses | `EXPECTED_GAP_ROWS` | 73 | 78 | `M C62`, `N A15`, `P F5`, `P K7`, `P M3` entered GAP |
| pointer graph | `measure_pointer_graph.py --pin`; the selftest's G5 literal; the guard's docstring | 66 | 65 | `M C63`'s pointer gone; `P B3`, `P E5`, `P F4` re-pinned on their donors' new verdicts |

`census_completion.PINNED`, the 14 figures that moved:

| figure | before | after |
|---|---|---|
| stated_rows | 769 | 770 |
| capabilities | 783 | 784 |
| capabilities_achievable | 712 | 741 |
| out_of_scope | 71 | 43 |
| achievable | 698 | 727 |
| adjudicated | 205 | 179 |
| delivered_broad | 115 | 117 |
| unfired | 36 | 38 |
| gap | 564 | 591 |
| gap_write | 353 | 378 |
| gap_unknown | 107 | 109 |
| jobs_gap | 107 | 109 |
| jobs_dir_w | 58 | 60 |
| b1_standing | 13 | 15 |

The rulings' own share of these moves: `P N27` and `P P2` leaving GAP for
EXCLUDED-RULED move out_of_scope +2, gap -2, gap_write -2, achievable -2
and adjudicated +2. The three relation rows stay GAP, and move no figure.

After every edit to a pinned dict, an ast duplicate-key check ran over all
33 Python files the lane has touched: 465 dict literals and 0 duplicate
keys. It also checked the two registries built without a literal: the rulings
register, 66 ids, and the exclusion families, 32 calls, both with no
duplicates. The check was run red first, on a planted duplicate key. The
write count did not move in this step. The earlier prose-ordinal sweep still
holds: nothing in the package still counts fifteen writes except as history.

### 10.4 Gates on the final tree

- **The derived files.** The blocker map, the rulings index and the audit
  index were regenerated in a loop until their hashes stopped changing. That
  took two passes. `--check` then passed on each.
- **The census instruments**, with no pin or write flag -- all green:
  - `census_completion --check`: every headline figure matches its pin.
  - `check_read_addresses`: 104 of 104.
  - `check_write_classes`: 385 lines, 16 / 36 / 333.
  - `check_exclusion_basis`: population 43, table 43, 0 structural.
  - `check_jobs_directions`: 109 of 109.
  - `ruling_holds`: 1 standing hold, 3 lifted, 1 release, all resolving.
  - `pin_census_rows`: 770, matching.
  - `check_gap_rows_on_refused_addresses`: 78, MATCH, PASS.
  - Also green: `measure_pointer_graph --check` (65),
    `classify_writeoff_reasons --check`, both triage scripts,
    `check_census_locators_resolve`,
    `check_contingent_writeoffs_carry_a_reopener` (PASS), and
    `check_cited_shas_resolve`.
  - `check_asserted_names_resolve` reports its pinned 8 sites, none new.
- **The tests.** The impact set comes from `scripts/impact_gate.py`: 22 staged
  paths selected 139 test files, the 20 corpus-wide guards among them. The
  order's extras were added: `test_readonly.py`,
  `test_readonly_boundary_invariant.py`, `test_writes.py`, the tool-surface
  pin, and the correction, cited-SHA, reopener and asserted-name guards. Only
  the reopener test was not already selected, so the run is 140 files, with
  `-n 6 --dist loadfile`: 7554 passed, 8 skipped and 1 xfailed, none failed,
  in 2910 s (exit 0; all 140 files are in its junit record).
- **The final text.** This section was written after that run, and one list
  in the capture queue lost `P N27`, which now queues nothing. The derived
  files were then regenerated the same way, to a fixed point, and 29 files
  ran on the final text: the analyser's 20 corpus-wide guards (the
  correction and asserted-name guards among them), the cited-SHA and
  reopener guards, the three derived-file guards, and the locator,
  prose-claim, settled-count and path-hygiene tests: 3197 passed, none
  failed (exit 0).
- **NOT run:**
  - The full suite. The analyser itself recommends widening to it, because
    139 of 253 files is past its 45% line. It was not run, by the standing
    order against a local full suite; CI certifies when the orchestrator
    pushes.
  - Anything live, and no browser but the local headless Chromium that the
    fixture tests drive over committed markup.
  - `scripts/build_read_map.py`: the observed read map the analyser leans on
    was recorded at `5c910e4`. It can only add files to a plan, never trim
    one.
  - The rest of the analyser's set for this section's own edit. Asked about
    this record and the audit index alone, it names 117 files. All of them
    ran in the 140-file run, on the tree before this text; the text adds no
    ruling declaration, no census row and no code, and the guards that read
    prose ran on it again, as above.

## Live queue

One act of the three classes is built, so one proof is queued. Nothing in this
lane fired it, previewed it against a real group, or minted a grant outside
the offline fixture tests.

| proof | HE NAMES | calls | page loads | presses | what it settles |
|---|---|---|---|---|---|
| L1 `linkedin_withdraw_from_group` | a group he belongs to and is willing to leave, by its NUMERIC id -- and NOT his last membership (with none left, the fresh render cannot tell "no memberships" from "not drawn yet", and the verification answers unknown by construction) | two, in a process started with `LINKEDIN_ENABLE_WRITES=1`: the preview (returns the counts, the state `member`, a token), then the same call with `confirm_token` within 120 s | 3 loads of `/groups/` -- preview, perform, verification | 2 -- the row's disclosure, then 'Leave this group' only if exactly one visible leave item sits in that row | EITHER the leave lands with no further step (verified `not_member` on the fresh render: performed True), OR a confirmation opens, nothing in it is pressed, the fresh render still reads `member` (performed False) and the receipt reports the dialog and its button count. In that case the next session is capture C9 on the same named group, and the confirm step is built from it |

C9, queued only if L1 stops at a confirmation: `/groups/`, the same group HE
NAMED, the row's menu opened and 'Leave this group' pressed, the confirmation
captured whole, then cancelled -- taking it cannot fire an act he did not
order, because the group is the one he already named for leaving.

The CAPTURES below each need a target he names too; the page loads are
counted with them.

## Capture queue

Each capture is counts-and-structure only on the way out (the DOM stays under
the main checkout's gitignored `_state/`; a fixture is built from it by a
builder, synthetic, never a copy). The spec each one lifts is in
`outward_classes.OUTWARD_CLASS_SPECS`. "HE NAMES" means the target is his,
chosen by him, in that session.

| # | lifts | page (composed from what HE NAMES) | state when captured | element the capture must hold | why taking it cannot fire the act | loads |
|---|---|---|---|---|---|---|
| C1 | `repost_item` (`M C20`) | `/feed/update/<urn>/` of an item HE NAMES | the item's `Repost` control (declares `aria-expanded='false'`) pressed once through the shipped disclosing press | the menu it discloses: its items, their role and container | the control is a DISCLOSURE; nothing inside the menu is pressed; Escape closes it; the press is priced by the item's own reaction toggle at both ends, as share_link's is | 1 |
| C2 | `repost_item_with_thoughts` (`M C21`) | the same page, same session, AFTER C1 has read the menu | the menu open and the item whose whole name is exactly 'Repost with your thoughts' pressed -- only if exactly one visible item carries that name | the composer it opens: editor, post control, whether post is disabled while empty | a composer publishes nothing until its own post control is pressed; nothing is typed; it is closed with Escape (a discard prompt answered discard). The misaim is the risk: the sibling 'Repost' may republish in one press and is a prefix of the target, so the aim is the exact whole name C1 read, never a prefix or a position (F-5, section 9.5) | 0 (C1's load) |
| C3 | `endorse_skill` (`P E4`, `N 111`, `N 112`), and `P E5` / `N 113` | `/in/<slug>/` of a 1st-degree connection HE NAMES, inside the endorsement he orders (THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET) | as first rendered, Skills section drawn | the per-skill endorse controls and the label an endorsed skill wears | loading and reading press nothing; the one cost, a profile view that member can read, is part of the act he ordered toward that same person -- never a measurement (the surviving forbidden entry). PREREQUISITE: a code path that loads `/in/<slug>/` inside a named act (the N 1 / M M1 builds) | 1 profile view |
| C4 | `request_recommendation` (`P F2`, `N 119`) | the same named profile, inside the request he orders; the same PREREQUISITE as C3 | its `More` disclosure opened and its items READ, none pressed; then the request item, by its exact whole name from that read and only if exactly one visible item carries it, pressed, the form open and EMPTY | the menu's items, the request item, the form (relationship, position, message box) and its send control | a disclosure and a form; nothing typed; send never pressed; the form dismissed. The menu has never been read and may carry one-press acts beside the request (UNVERIFIED), so nothing in it is pressed before it is read (F-5) | 0 if taken with C3 on the same person, else 1 |
| C5 | `give_recommendation` (`P F3`, `N 120`; revise `P F4` / `N 124`) | the same named profile, inside the recommendation he orders; the same PREREQUISITE | `More` opened and read first; then the recommend item, by exact whole name, pressed, the form open and EMPTY | the menu's items, the item, the form and its send control | as C4 | as C4 |
| C6 | `delete_own_post` (`M C19`) | `/feed/update/<urn>/` of HIS OWN post, one HE NAMES FOR DELETION | the control menu opened through the shipped disclosing press (as share_link opens it) and 'delete post' pressed | whatever that press draws -- expected a confirmation with confirm and cancel | the menu open is a disclosure; 'delete post' MAY itself delete if no confirmation is drawn, which is why the post must be one he names for deletion -- then either outcome is the act he ordered; a drawn confirmation is cancelled | 1 |
| C7 | `delete_own_comment` (`M C31`) | the permalink carrying HIS OWN comment, one HE NAMES FOR DELETION | the comment's own menu opened, aimed by the comment's id, and 'Delete' pressed | the comment id on its element; whatever 'Delete' draws | as C6 | 1 |
| C8 | `withdraw_invitation` (`N 10`, `N 12`) | `/mynetwork/invitation-manager/sent/` -- REFUSED today; an exact-url admission with its badge cost measured comes FIRST | the sent list, with a pending invitation HE NAMES for withdrawal | the row's withdraw control and whatever pressing it draws | the admission and the list read press nothing; the withdraw press may be the act, so it is taken only on an invitation he names for withdrawal, and a drawn confirmation is cancelled | 1, priced by the badge gate |

Rows of the class whose capture is further off, each named in its own census
cell: `M C17` (the scheduled-posts modal), `M C22` (a repost's own menu -- a
repost must exist first), `M C62` (a pending group request must exist),
`M C77` (his article's menu), `M M12` / `M M26` (the per-message and
per-thread menus, lane L5's surface), `P I11` (the Open To Work editor, never
loaded), `P K7` (the verification surface), `P F5` / `N 125` and the received-
recommendation rows (his recommendations section, refused by allowlist silence
until admitted), the settings-family rows `J 87`, `N 96` and `P M3`
(admission by name first), and `P A23b` (a name-pronunciation recording must
first exist, and only the mobile app can make one).

Since section 10, three more rows sit in a ruled class,
RELATION-REMOVALS-BUILT-BEHIND-GRANTS, and each names a capture of its own.
Each is taken only at a member HE NAMES:
- `N 29`: the row menu of one connection he names, on the admitted
  connections list.
- `N 141`: the block control on the named member's profile, once the
  named-profile route exists.
- `N A14`: the attendee control of an event he organizes, once there is one.

`P P2`, `P N27` and `P N28` queue nothing: ACCOUNT-DESTRUCTION-STAYS-MANUAL
keeps them manual.
