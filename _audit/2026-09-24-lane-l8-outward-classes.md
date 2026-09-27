claude-opus-5-5[1m]

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

Status: IN PROGRESS. This record is written as the lane goes.

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

Commit `efa3d8f`. `writes.PERMANENTLY_FORBIDDEN` now holds exactly the six
the ruling names:

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
    delete_or_withdraw_anything   79f0867297b22471

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

## 3. The five `reversible_by` claims that leaned on the destruction entry

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
| `send_message` | NOBODY: a delivered message cannot be recalled | delivery itself: it arrives as an email and a notification; LinkedIn's 60-minute delete (census `M M12`) removes it from a thread, never from an inbox, and is unbuilt | none |
| `send_reply` (lane L5) | not on this base | -- | see below |

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
| `leave_group` | BUILT (section 6) | the only act of the three classes whose pressed controls are in a capture file: his own `/groups/` page (2026-09-20) holds the row-scoped disclosure and the `Leave this group` item, and the 2026-09-05 probes measured the menus live; the address is admitted | `M C63`, `N 64` |
| `repost_item` | NEEDS-CAPTURE | the Repost control is captured CLOSED four times and its menu never; the items the menu offers are what the act presses | `M C20` |
| `repost_item_with_thoughts` | NEEDS-CAPTURE | the same menu, and the composer its second item opens | `M C21` |
| `endorse_skill` | NEEDS-CAPTURE | no endorse control anywhere on disk (re-taken: 0 in 25 captures and 29 fixtures); it lives on a third party's profile, loadable only inside his named act, and no code path loads `/in/<slug>/` yet | `P E4`, `N 111`, `N 112` |
| `request_recommendation` | NEEDS-CAPTURE | the named member's profile `More` menu and the form it opens; the own-profile route aims by a name typeahead, measured dead and forbidden as an aim | `P F2`, `N 119` |
| `give_recommendation` | NEEDS-CAPTURE | as above, the `Recommend` item and its form | `P F3`, `N 120` |
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
  (`endorse_skill`), each NEEDS-CAPTURE inside his named act, behind the
  missing route that loads `/in/<slug>/` there.
* **OUTSIDE THE THREE CLASSES -- a decision point for the orchestrator, not
  decided here:** `N 29` (remove a connection -- a relationship with another
  member, not his item), `N 141` (block a member -- the ruling that lets a
  named member's profile load names connect, message and the note, not
  blocking), `N A14` (remove another member from his event), `P N27` (merge or
  close a duplicate account -- an account is not an item). Each is GAP because
  the key that held it is gone and no other written ground reaches it; each
  names as its blocker that the three classes do not include it, plus what else
  stands (a capture, an admission, an organiser precondition).

The GAP rows whose blockers NAMED a retired key keep their state and restate
the blocker: the repost pair `M C20` / `M C21` (the Repost menu capture), the
recommendation rows `P F2`-`F9` and `N 119`-`128` (the named member's profile
for request, give and revise; his own recommendations section --
`/in/me/details/recommendations/`, refused by allowlist silence on
2026-09-24 -- for the rows about recommendations he received or gave), and the
compound rows whose "delete half stays refused by delete_or_withdraw_anything"
(the delete half now waits on the same capture as the rest of its row; it is
unbuilt, not refused).

**`M C63` and `N 64` (leave a group) move GAP -> COVERED-UNFIRED** on the
build in section 6. Their class-table lines cite `GROUPS-ADDRESS-BUYS-NO-WRITE`
("each needs its own url, its own write sanction and its own ruling"): the
build pays all three -- the url is the admitted `/groups/` root, the sanction
is the WriteSpec behind the grant, the ruling is
OUTWARD-CLASSES-BUILT-BEHIND-GRANTS.

(5.2 the edits and 5.3 the pin moves are filled in as the census lands.)

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
  the build and the census land -- the BUILT record for `leave_group` has no
  performable spec yet, and nine governed rows still read EXCLUDED-RULED or GAP
  where their records say otherwise. That test is the instrument that proves
  the records and the census agree, shown failing on the real data first.
- `scripts/impact_gate.py --against 1902fcb --plan-only`: the impact set is 181
  of 244 test files (74%), so the gate WIDENS TO THE FULL SUITE -- touching
  `writes.py` couples almost everything. **Not run locally, by order; CI
  certifies at merge.**

## Live queue

One act of the three classes is built, so one proof is queued. Nothing in this
lane fired it, previewed it against a real group, or minted a grant outside
the offline fixture tests.

| proof | HE NAMES | calls | page loads | presses | what it settles |
|---|---|---|---|---|---|
| L1 `linkedin_leave_group` | a group he belongs to and is willing to leave, by its NUMERIC id -- and NOT his last membership (with none left, the fresh render cannot tell "no memberships" from "not drawn yet", and the verification answers unknown by construction) | two, in a process started with `LINKEDIN_ENABLE_WRITES=1`: the preview (returns the counts, the state `member`, a token), then the same call with `confirm_token` within 120 s | 3 loads of `/groups/` -- preview, perform, verification | 2 -- the row's disclosure, then 'Leave this group' only if exactly one visible leave item sits in that row | EITHER the leave lands with no further step (verified `not_member` on the fresh render: performed True), OR a confirmation opens, nothing in it is pressed, the fresh render still reads `member` (performed False) and the receipt reports the dialog and its button count. In that case the next session is capture C9 on the same named group, and the confirm step is built from it |

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
| C2 | `repost_item_with_thoughts` (`M C21`) | the same page, same session | the menu open and its 'Repost with your thoughts' item pressed | the composer it opens: editor, post control, whether post is disabled while empty | a composer publishes nothing until its own post control is pressed; nothing is typed; it is closed with Escape (a discard prompt answered discard) | 0 (C1's load) |
| C3 | `endorse_skill` (`P E4`, `N 111`, `N 112`), and `P E5` / `N 113` | `/in/<slug>/` of a 1st-degree connection HE NAMES, inside the endorsement he orders (THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET) | as first rendered, Skills section drawn | the per-skill endorse controls and the label an endorsed skill wears | loading and reading press nothing; the one cost, a profile view that member can read, is part of the act he ordered toward that same person -- never a measurement (the surviving forbidden entry). PREREQUISITE: a code path that loads `/in/<slug>/` inside a named act (the N 1 / M M1 builds) | 1 profile view |
| C4 | `request_recommendation` (`P F2`, `N 119`) | the same named profile, inside the request he orders | its `More` disclosure opened, the request item pressed, the form open and EMPTY | the item, the form (relationship, position, message box) and its send control | a disclosure and a form; nothing typed; send never pressed; the form dismissed | 0 if taken with C3 on the same person, else 1 |
| C5 | `give_recommendation` (`P F3`, `N 120`; revise `P F4` / `N 124`) | the same named profile, inside the recommendation he orders | `More` opened, the recommend item pressed, the form open and EMPTY | the item, the form and its send control | as C4 | as C4 |
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
until admitted), and the settings-family rows `J 87`, `N 96`, `P M3`, `P N27`
(admission by name first).
