# `leave_group` -- the WriteSpec, every field, measured or marked UNKNOWN

**Rows:** `N 64` ("leave a LinkedIn group") and `M C63` ("leave a group") --
one capability counted twice by two census slices.

Wave: groups-surface. Date: 2026-09-05. **This is a SPECIFICATION, not a
build.** No entry was added to `writes.py`, `SANCTIONED_MUTATIONS` or the tool
surface, and section 6 says why.

---

## 0. WHY THIS ROW AND NOT ONE OF THE OTHER NINETEEN

`GROUPS-SURFACE` carries twenty write rows. Nineteen of them need a boundary
change, a page nobody has opened, or both. **This one needs neither**: the
control is drawn on `/groups/`, which is already on the allowlist, and it was
read there today.

    _probe_groups_menu.py, four runs, control 20 -> 20 at both ends
        5  'Leave this group'      one per membership row

That is the whole of its cheapness, and it is also the whole of its danger:
the thing standing between this server and an irreversible act on his account
is a gate that does not exist yet, rather than an address it cannot reach.

## 1. THE FIELDS

| field | value | how it is known |
|---|---|---|
| `action` | `leave_group` | -- |
| `tool_name` | `linkedin_leave_group` | -- |
| `url_template` | `https://www.linkedin.com/groups/` | **the surface HAS been loaded**, six times today |
| `url_pattern` | the existing anchored root pattern in `readonly.py` | already on the allowlist; no widening |
| `exempt_substring` | **None** | measured: `/groups/` matches ZERO of the 33 forbidden substrings |
| `summary` | leave one LinkedIn group he is a member of | -- |
| `from_state` | `member` | the row draws `Leave this group`; a non-member row does not |
| `to_state` | `not_member` | UNVERIFIED -- nobody has watched the transition |
| `direction_source` | the row-scoped disclosure menu on `/groups/` | measured |
| `target_kind` | `group_id` -- a bounded run of digits | measured: 10 of 10 group segments on his page are pure digits at lengths 5-8, zero non-numeric, zero queries |
| `state_from` | the page the action acts on -- the `posting_page` shape, not the `saved_list` shape | measured: the state and the control are on one page, so one load yields both |
| `reversibility` | see section 3 | **NOT MEASURED** |
| `reversibility_measured` | `False` | -- |
| `reversibility_class` | `STILL-UNKNOWN`, and section 3 argues it is worse | -- |
| `wrong_state_note` | must be its own sentence, NOT the toggle sentence | see section 4 |

## 2. AIMING, AND IT IS THE HARD PART

**THE SURFACE HOLDS TEN GROUPS AND HE IS A MEMBER OF FIVE.** A write aimed by
position would eventually leave the wrong one, and this repository has already
ruled that choosing by position is refused for a write everywhere -- the rule
`_resolve_own_item_permalink` states and `_probe_comment_overflow_menu` was
careful to stay inside.

The aim is the numeric group identifier, matched INSIDE THE PAGE against each
row's own anchor href, and the rule is `send_message`'s:

> **EXACTLY ONE ROW CARRIES THE TARGET IDENTIFIER, OR IT REFUSES.** Zero
> refuses. Two or more refuses rather than shortlisting.

Three properties make that safe here and each was measured today rather than
assumed:

1. **The identifier is numeric**, so the needle cannot be a name. A slug aim
   would be a person's name whenever a group is named after a person, which is
   the defect the whole of `linkedin_server/groups.py` exists to close.
2. **The row is found from the CONTROL, not from the anchor.** The two
   directions are not interchangeable: run 1 of
   `_probe_membership_tally_live.py` walked from the anchor and resolved ZERO
   rows against five from the button-up walk on the same page in the same
   hour. A containment rule is not symmetric, and an aim built on the wrong
   direction fails closed here and could fail open elsewhere.
3. **A membership row and a suggestion row are structurally distinguishable**
   without reading a heading: five rows carry a row-scoped disclosure and five
   do not, and the split falls exactly on the section boundary.

**AND THE CLICK IS NOT ITS OWN EVIDENCE.** The menu must be opened first, so
the sequence is press-disclosure, then press `Leave this group` -- two clicks,
of which only the second is the write. The gate must re-establish AFTER opening
the menu that the menu it opened belongs to the row carrying the target
identifier, exactly as `send_message` re-checks who is in the box after
choosing from the typeahead. `linkedin_send_message` shipped on 2026-09-02
believing a fill committed a recipient; it did not, and the repair was to check
the state after the act rather than to trust the act.

## 3. REVERSIBILITY -- UNMEASURED, AND THE HONEST READING IS WORSE THAN THAT

The naive reading is that leaving is reversible because joining exists. **That
is not a measurement and it is probably wrong:**

* rejoining a group that requires approval needs a MANAGER to act, so the
  undo is not his to perform. An action whose reversal depends on a third
  party's decision is not reversible by this server in any useful sense;
* **nothing on the admitted root says which of the five are approval-gated.**
  The root draws the membership rows and their three menu items; it does not
  draw a privacy or entry-rule marker that this wave observed;
* an unlisted or private group may not be findable again at all -- census row
  `N 175` exists precisely because such a group is reached by a direct link,
  and a link he no longer has is not a route.

**REVERSIBILITY PROCEDURE, so the gap names its own fix rather than sitting as
a caveat:** determine, for the specific target group and BEFORE the act,
whether it is open or approval-gated. Nothing this server can currently read
answers that. `/groups/<id>/` would, and it is not admitted.

**THE RECOMMENDATION, and it is a recommendation and not a ruling:** treat
`leave_group` as IRREVERSIBLE until the entry rule of the specific target is
readable. That is the same posture `apply_job` holds, and for the same reason
-- the undo exists in principle and not in this server's hands.

## 4. THE WRONG-STATE SENTENCE MUST BE ITS OWN

The default toggle sentence is *"performing this from the other state performs
the opposite action"*. **It is FALSE here**, in the way `apply_job`'s docstring
already records for its own case: there is no opposite action drawn on a
suggestion row, and `Leave this group` is not the far end of a toggle whose
near end is a Join button on the same control. Acting from the wrong state does
not join a group -- it aims a leave at a row that has no leave, which either
refuses or, if the aim is loose, presses something else.

Proposed text: *"a row that is not one of his memberships draws no leave
control at all. Aiming this action at one does not join it; it aims at a
control that is not there."*

## 5. WHAT ELSE THE MENU BOUGHT, AND WHAT IT DID NOT

The same five menus draw `Update your settings` (twice per row) and `Copy link
to group`. Those are the surfaces behind census rows `N 170` (allow or prevent
group members messaging you) and `N 176` (prevent your network being updated).

**AND THERE IS A BOUNDARY TRAP WAITING THERE, worth knowing rather than
discovering:** `settings` and `/settings/` are BOTH on
`_FORBIDDEN_URL_SUBSTRINGS`, checked BEFORE the allowlist. So if that menu item
navigates to a per-group settings address, those two rows are DOUBLE-refused in
exactly the way `/groups/<id>/invite/` is -- and they would need a denylist
exemption, which is a heavier act than an allowlist addition.

**It may not navigate at all.** A menu item that opens a modal on the same page
would be reachable with no boundary change whatsoever. Nobody has pressed it.
That single press is the cheapest measurement left in this blocker and it
settles both rows plus the administrative inference behind `N A10`-`A12`.

## 6. WHY NOTHING WAS BUILT

* **`writes.py` holds another wave's uncommitted lines today**, and `--only`
  does not protect a neighbour's LINES inside a path you name -- measured on
  this project this morning, when a wave committed 214 lines of which 117 were
  somebody else's.
* **A spec is not the gate.** Wiring this needs a `SANCTIONED_MUTATIONS` entry,
  a tool, a confirm gate built from a live read, and a single-use grant. The
  mutation list has five entries and widening it is a test failure rather than
  a judgement call, which is the design.
* **The reversibility class is genuinely open and it is not this wave's to
  close.** Section 3 names what would settle it and states a recommendation
  rather than a verdict.
* **Nothing was fired at a real group.** No confirm token was minted, no write
  path was executed, and the probes that measured this pressed nothing inside
  any menu.
