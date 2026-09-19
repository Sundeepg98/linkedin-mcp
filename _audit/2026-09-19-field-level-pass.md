# The field-level pass -- 1 row, and the separation is the judgement it rests on

> **THIS IS THE PASS, NOT THE MAP, AND THE DISTINCTION IS DELIBERATE.**
> `scripts/reader_field_inventory.py` reads the AST and **makes no claim about
> any census row** -- it cannot be wrong about one because it never mentions
> one. **This document DOES make claims about rows**, so it carries its own
> evidence per row and does not inherit the map's cleanliness. A worklist that
> is sound and a conclusion drawn from it are different artifacts.

## 1. THE SEPARATION, STATED FIRST BECAUSE THE PASS RESTS ON IT

227 fields reach a caller. **Most are not capabilities.** The criterion, and it
is a judgement rather than a rule:

> **Does the field name a thing LINKEDIN RENDERS that a member would
> recognise, or does it describe THE READ ITSELF?**

    DIAGNOSTIC   main_chars  main_present  scan_complete  settle_why  observed
                 truncated  anchors_seen  heading_count  controls_read
                 rows_total  selector  pattern_census  why  refused  reason
                 -- these describe the instrument's own operation

    CAPABILITY   applicant_insights  company_insights  promoted  verified_job
                 responses_managed_off_linkedin  trend  memberships
                 registered_events  endorsements  off_state  badge_links
                 entitled_hits  authorship_facts  more_behind_a_control
                 -- these name something the product draws

**Nine of the fourteen capability-bearing fields were already banked** by this
wave today -- five of them from one dict. That is the expected shape: the
inventory's value was never a large yield, it was making the minority findable.

## 2. THE ONE ROW, WITH ITS EVIDENCE

**`P E7` "Endorsements received" -> MEASURED-ABSENT.**

Reached by following the field `endorsements`, which the separation above kept.

**Its stated blocker was inherited from a row it does not apply to.** The cell
read *"same blocker, same absence of a reason"*, pointing at `E6`, where
`/endorse` is a forbidden substring. **That substring is about the endorse
ACTION.** `E7` is a READ of endorsements already received on his own profile,
and the page that would show them is ADMITTED:
`is_read_url("https://www.linkedin.com/in/me/details/skills/")` returns True,
verified at this tree. **No boundary blocks it.**

**The capability is measured absent, not unbuilt:**

    dom.py:8772          read_profile_detail_entries emits "endorsements"
                         carrying drawn, lines, looked_at
    server.py:4221-4227  linkedin_my_profile lifts it into its payload
    that comment         "Not a parser this tool is missing -- a line
                          LinkedIn does not draw"
    network.md N 118     THE SAME CAPABILITY, another slice, already
                         MEASURED-ABSENT on a live 2026-09-04 reading:
                         20 skill cards, no endorsement line among them

**What the instrument DID see travels with the zero** -- the field reports its
own denominator, so a no is distinguishable from a page that never loaded.

`E6` and `N 114` stay GAP: both are WRITES (hide/show an endorsement), and a
read banks neither.

## 3. TWO CORRECTIONS THE PASS MADE TO ITSELF

### 3.1 I read a window too narrow and nearly reported the opposite

Looking at `server.py:4190-4215` I found the caller lifting `entries`, `count`
and `observed` and **concluded `endorsements` was computed and dropped.** The
lift is at `:4221`, six lines past where I stopped.

Had I reported it, the finding would have been "a reached reader whose
capability field no caller takes" -- a clean, wrong, and quite interesting
claim. **The window was the error, not the reading**, which is the same shape
as the nav-badge counter earlier today: accurate about what it covered and
silent about what decided the question.

### 3.2 `reached` IS READER GRANULARITY, NOT FIELD GRANULARITY

The map marks a READER reached when a tool can call it. **It does not follow
whether each FIELD survives the caller.** Measured on the very reader this
pass used:

    read_profile_detail_entries emits 5 fields
      lifted by the caller:  endorsements, reason, refused, why
      COMPUTED AND DROPPED:  section

So a field can sit inside a REACHED reader and reach nobody. **That is a real
limit on the map and it is recorded here rather than in the map**, because it
is a caveat on how the map is USED and the map's own contract is exactly what
it says: it reports what the code contains.

## 4. WHY THE YIELD IS ONE, AND WHY THAT IS THE RIGHT NUMBER

The hand cross-reference of 42 TOOLS yielded one row; the unit was too coarse.
The field-level pass yielded one row **on top of the nine capability-bearing
fields already banked today by other routes** -- six from a single dict through
`CLOSED-SINCE-CENSUS`, one through a COVERED twin, two through the groups tool.

**So the field unit found what the tool unit could not: it just found most of
it a few hours earlier, by other means.** The honest statement of this
instrument's worth is not "it banks rows" but "it is the first artifact that
would have found all seven fields of that one dict in a single pass" -- and
that claim is now checkable, because the map exists and the dict is in it.

## 5. WHAT REMAINS IN THE CAPABILITY-BEARING SET

    off_state              the counter that prices a feed press (M C72),
                           already recorded on that row
    badge_links            invitation and notification badges; both readers
                           are cost instruments, not capability surfaces
    entitled_hits          premium entitlement, read by premium.py
    authorship_facts       own-activity authorship
    more_behind_a_control  the collapsed-panel marker behind
                           MATCH-DETAILS-COLLAPSED, which is queued DECIDE

**None of these is an unbanked capability row.** Each is either already
recorded against its row, or is an instrument field rather than a product
surface. The capability-bearing set is now accounted for end to end.
