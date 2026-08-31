# Lifting the six: the instruments the rulings asked for, and what they measured

Date 2026-08-31. Repo `linkedin`, branch `master`. Baseline `4f45781`, suite
2132.

The lead ruled on five of the six remaining refusals and asked for an
instrument behind each. This document reports, per capability, THE INSTRUMENT
BUILT, THE MEASUREMENT IT PRODUCED, and whether the refusal LIFTED -- and
where it did not, the exact remaining blocker.

**No `confirm_token` was issued to anything, by anyone, at any point. No write
was performed. No third party's profile was loaded. No badge was spent.**

---

## 0. The state the process was in, checked before anything was read

The previous wave spent most of a day unable to take captures because the
loaded process was nine commits behind the tree. This one was not:

    linkedin_server_info()
      build.code.commit  4f4578188317      <- the tree's own HEAD
      dirty              false
      pid 7248, started 2026-08-31T07:53:46Z, uptime 304s

So every capture below was taken against the code on disk, and the commit was
verified BEFORE anything was interpreted.

---

## 0b. THREE WRITE-SHAPED TOOLS ARE REFUSED BY THE HARNESS, and it shapes what
## this wave could demonstrate

Not by this server. By the Claude Code permission classifier, which sits
outside it:

    linkedin_send_invitation   refused 2026-08-31 (previous wave)
    linkedin_send_message      refused 2026-08-31 (this wave)
    linkedin_update_setting    refused 2026-08-31 (this wave)

**None was routed around.** A tool whose name carries a write verb is exactly
what a permission layer should stop, and the correct response to a denial is
to stop rather than to find another door to the same act.

**WHAT IT COSTS THIS WAVE, STATED PLAINLY.** All three of those tools are
GATED PREVIEWS: called without a `confirm_token` they mint nothing, perform
nothing, and return a warning block. So the thing being refused is a read --
but it is refused on the NAME, which is the correct place for a permission
layer to work and is not something this server should try to be clever about.

The consequence for #6 is specific and is not hidden: **the lift can be shown
in the instrument and in the test suite, and it cannot be shown by calling the
tool.** What a live run establishes is the READING -- which of the three
radios is checked -- and that comes from `linkedin_surface_census`, which is
not refused. What the wiring then does with that reading is proved by test.
Both halves are reported separately below rather than blended into a claim
that the gate was seen rendering.

---

## 1. #1 publish_post -- THE DETECTION WAS ENGINEERED, AND IT SAYS DO NOT OPEN

**The ruling.** Build a CONTENT-DRAFT READER FIRST. With one, opening the
composer stops being an unmeasurable risk: read drafts, open, capture, read
drafts again, report the difference. **If no content-draft surface is
reachable, do NOT open the composer** -- come back and say so, and #1 stays
refusing with that as its reason.

**No content-draft surface is reachable. The composer was not opened.**

That conclusion rests on two independent measurements, and the second is the
one that carries it, because it does not depend on the first being complete.

### 1a. Enumeration -- zero draft-shaped addresses on either readable surface

`linkedin_surface_census` returns `href_shapes`, a counted map of every href
on the controls it reads. Both surfaces this server may read were censused
today:

| surface | controls read | distinct href shapes |
|---|---|---|
| `/feed/` | 297 | 25 |
| `/in/me/` | 232 | 28 |

**Not one of the 53 is a content-draft surface.** The four that come closest,
and why each is not one:

    /article/new/                       the article COMPOSER. Not a draft list.
    /preload/sharebox/                  the post COMPOSER. Not a draft list.
    /my-items/saved-posts/              posts HE SAVED -- other people's items.
    /analytics/creator/content/         analytics over PUBLISHED posts.

**THE LIMIT OF THIS ENUMERATION, STATED RATHER THAN GLOSSED.** 39 hrefs on the
feed and 51 on the profile shape to `<opaque>` -- they failed the census's
length or character gate, which is what LinkedIn's tracking-parameter urls do.
A draft surface could be among them and this enumeration could not see it. On
its own, therefore, section 1a is NOT sufficient, and it is not what the
verdict rests on.

### 1b. The boundary -- 17 candidate addresses, 17 refused

Run against `readonly.is_read_url` and `readonly.assert_read_url` directly, so
the answer is the boundary's own rather than a reading of it:

    REFUSE  /post/new/                        forbidden substring '/post/'
    REFUSE  /post/edit/<id>/                  forbidden substring '/post/'
    REFUSE  /article/edit/<id>/               forbidden substring '/edit/'
    REFUSE  /feed/update/<urn>/               forbidden substring '/feed/update'
    REFUSE  /article/new/                     not on the allowlist
    REFUSE  /my-items/                        not on the allowlist
    REFUSE  /my-items/drafts/                 not on the allowlist
    REFUSE  /my-items/saved-posts/            not on the allowlist
    REFUSE  /my-items/posts/                  not on the allowlist
    REFUSE  /in/me/recent-activity/all/       not on the allowlist
    REFUSE  /in/me/recent-activity/shares/    not on the allowlist
    REFUSE  /preload/sharebox/                not on the allowlist
    REFUSE  /pulse/drafts/                    not on the allowlist
    REFUSE  /drafts/                          not on the allowlist
    REFUSE  /content/drafts/                  not on the allowlist
    REFUSE  /analytics/creator/content/       not on the allowlist
    REFUSE  /dashboard/                       not on the allowlist

**This is what makes 1a's incompleteness irrelevant.** Even a draft surface the
enumeration failed to see could not be OPENED: four of these families are
refused by a forbidden substring checked before the allowlist, and the
remaining thirteen match no anchored pattern. A content-draft reader cannot be
built without a read-boundary widening, and no such widening was ruled.

### 1c. The verdict

**#1 STAYS REFUSING, and its reason is now measured rather than argued.** The
previous wave's objection was that opening the composer might leave a draft
this server cannot see or clean up. That objection has now been converted from
a worry into a measurement: **there is no reachable surface on which such a
draft could be detected, so the cost of opening the composer would still be
unmeasurable after opening it.** The lead's own stop condition is met exactly,
and the composer was not opened.

**WHAT WOULD LIFT IT** is unchanged in kind and now specific in content: a
ruling admitting ONE named draft-listing address to the read allowlist, so
that the before/after difference the ruling described can actually be taken.
Nothing on the two readable surfaces names such an address, so the ruling
would have to be made on an address found by him rather than by this server.

---

## 2. #9 send_message -- THE MARGINAL-COST ARGUMENT CHECKED, AND ONE THING IT MISSED

**The ruling.** One messaging open is permitted for the capture, on the ground
that `linkedin_new_messages` and `linkedin_open_messaging` already perform
exactly that operation and are already sanctioned -- so the capture spends
nothing the operator has not already accepted. **Verify that before relying on
it. Check the MESSAGING badge specifically before opening, and if it is
non-zero, stop and report.**

### 2a. The badge -- ZERO, measured twice on two surfaces

`dom.read_messaging_badge` reads `a[href*="/messaging/"]`'s `aria-label`
through `shape.census_shape`. That is the same element, the same attribute and
the same shaper the surface census reads, so a census row IS that measurement.
Both of today's censuses carry it:

    /in/me/    shape "Messaging, 0 new notifications"   count 1   aria-label
    /feed/     shape "Messaging, 0 new notifications"   count 1   aria-label

**The messaging badge is ZERO**, on two different surfaces in one session. So
the lead's stop condition -- stop if it is non-zero -- is NOT triggered.

Recorded beside it, because the lead flagged the notification badge as having
moved 1 -> 4 and today it reads differently again:

    Home, 1 new notification            (both surfaces)
    Notifications, 0 new notifications  (both surfaces)
    <redacted>, 0 new notifications     (mynetwork, both surfaces)

The two nav controls disagree -- `Home` says 1, `Notifications` says 0 -- and
this server has no reading that resolves which is the unread count LinkedIn
would consume. **That is a disagreement between two labels on one page, not a
number**, and it is recorded as such rather than reported as "the badge is 1"
or "the badge is 0".

### 2b. The capture was NOT taken, and the reason is a permission denial

`linkedin_send_message` was **refused by the harness permission classifier**,
not by this server. It is recorded rather than worked around, exactly as
`linkedin_send_invitation` was on 2026-08-31: a tool named "send message" is
precisely what a permission layer should stop, and the correct response to a
denial is to stop rather than to find another door to the same act.

The badge reading above was NOT obtained by routing around that denial. It came
from a census of a page loaded for a different purpose -- which is the route
this server's own design already names as the way to measure a surface without
paying for it, and which reaches the identical string by the identical code
path.

### 2c. THE MARGINAL-COST ARGUMENT DOES NOT HOLD, and this is the finding

The lead asked for the argument to be checked rather than taken. Checked, it
fails -- and it fails on the composer, not on the badge.

`linkedin_open_messaging` and `linkedin_new_messages` load `/messaging/`.
LinkedIn is MEASURED TWICE to redirect that address into one conversation of
its own choosing. So those two tools pay: one badge, and one thread opened.

**A composer capture needs something neither of them touches.**
`/messaging/compose` is on `_FORBIDDEN_URL_SUBSTRINGS` -- it is the entry that
SURVIVED when the blanket `/messaging` ban was narrowed on 2026-08-26, and it
was kept for exactly this. The two sanctioned tools reach a THREAD; the send
composer is a different address, and it is forbidden.

So the operation is not the same operation:

| | the two sanctioned tools | a composer capture |
|---|---|---|
| address | `/messaging/` -> a thread | `/messaging/compose` |
| on the allowlist | yes, both spellings | **no** |
| on the forbidden list | no | **yes** |
| what it costs | the badge, one thread opened | the above, plus a surface nobody has ruled on |

**The marginal-cost argument is sound about the BADGE and unsound about the
COMPOSER.** Opening messaging costs nothing new; it also does not reach the
thing #9 needs measured. Reaching that needs a forbidden substring narrowed,
which is a boundary change and is not a marginal cost at all.

### 2d. The verdict

**#9 STAYS REFUSING.** Not on the deferral the lead lifted -- that deferral is
correctly lifted, and the badge check it was conditioned on passes at zero.
It stays on a different and firmer ground: **the composer address is on the
forbidden list, and opening messaging does not reach it.** The refusal's reason
changes from "deferred by ruling" to "the surface the capture needs is refused
by the read boundary, and the tool that would take it is refused by the
harness."

**WHAT WOULD LIFT IT:** a ruling narrowing `/messaging/compose`, which is the
single entry that has been kept through every other messaging relaxation. That
is a larger question than the one the lead lifted, and it is named here rather
than assumed.

---

## 3. #6 update_setting -- THE MISSING MEASUREMENT IS TAKEN

**The ruling.** Pure instrument, no ruling needed. The refusal stands only
because the census reports `disabled` and not `checked`, so `_direction` cannot
read a current state. **Build a `checked` reader. This is the whole blocker.**

### 3a. The instrument -- `08e846a`

`CENSUS_JS` gained `checkedOf`, and two fields ride each control record:
`checked` and `checked_source`. Both are plumbed through
`dom.read_surface_census` and into `shape.census_aggregate`'s merge key, which
went from eight fields to ten.

**THE TYPE GATE IS THE FIELD, and it was shown failing.**
`HTMLInputElement.checked` is defined for EVERY input type and reads `false` on
a text box, so an ungated read reports a control that is not checkable as one
that is checkable and off -- the same conflation `name_source: "none"` carried
for weeks. The mutation that removes the gate produces:

    assert False is None

on a text field named `Headline`. Measured over the 19 committed fixtures, the
ungated read gives 37 non-null readings against the gated 29, and **the eight
it wrongly claims are all text inputs.**

`null` means NOT CHECKABLE. `false` means CHECKABLE AND OFF. They are different
answers and the instrument keeps them apart.

`checked` and `checked_source` went INTO the merge key on an axis rule that is
worth carrying: `checked` is a control STATE, the same axis as `disabled` and
`aria_expanded`, and both of those were already in the key. `container` is a
PLACE and stays out. Without the key change, three same-shaped radios of which
one is on merge into a single row -- destroying the only thing the field was
added to report. Sweep over all 19 fixtures: 537 controls unchanged, no
pre-existing field moved, two fixtures gain one row each, and **no readable
shape anywhere became `<redacted>`.**

### 3b. The reading -- TAKEN LIVE, and it is the answer

Restart landed on `3940f72`, commit verified before reading.

    linkedin_surface_census("settings_dark_mode")
    source_url  https://www.linkedin.com/mypreferences/d/dark-mode   <- NO REDIRECT
    counts      forms 0   buttons 1   links 16   contenteditable 0   dialogs 0
    controls_read  20

    shape "Always off"        input  aria-labelledby  checked TRUE   native
    shape "Always on"         input  aria-labelledby  checked false  native
    shape "Device settings"   input  aria-labelledby  checked false  native

    the other 17 controls        checked null   checked_source "none"

**THE CURRENT SETTING IS `Always off`.** Exactly one of three is checked, read
off the very control a change would move, through the native branch.

**THE PRECONDITION WAS CHECKED BEFORE THE READING WAS INTERPRETED**, which is
the rule `profile_edit_intro` earned the hard way. This is the FOURTH reading
of this surface -- two on 2026-08-31 in the previous wave, one earlier today on
the pre-`checked` build, and this one -- and all four agree on every count: 20
controls, `forms: 0`, `buttons: 1`, `links: 16`, `dialogs: 0`, no redirect. It
is not a half-render.

**And the 17 nulls are the type gate working on a live page rather than on a
fixture.** Sixteen anchors and one button, every one reported as NOT CHECKABLE.
Under the ungated derivation none of them would have changed -- they are not
inputs -- so the live page does not by itself exercise the gate; the fixture
sweep is what does, and it is reported above rather than blended in here.

### 3c. What is now true, and what is not

**THE NAMED BLOCKER IS CLOSED.** `_direction`'s first two refusals -- no state,
and state `unknown` -- were the whole of why this gate would not render, and
the state they were missing is now measurable in one call.

**THE REFUSAL DOES NOT LIFT YET, and the remaining gap is wiring rather than
measurement.** `linkedin_update_setting`'s spec still declares
`state_from="settings_index"` and `from_state="setting_addressed"`, so the gate
still reads the INDEX -- a page that hands out addresses and switches nothing
-- rather than the page carrying the value. Moving it onto the multi-state
branch needs four things, none of which is a measurement:

1. a reader that turns the census rows above into a state, which
   `dom.read_surface_census` already supplies -- **no new script and no new
   `evaluate` waiver**; proved offline against a page built to the measured
   shape, where one-checked yields a single state and both none-checked and
   two-checked yield a set the reader must refuse;
2. `_SURFACE_READS` gaining the dark-mode page;
3. the spec moving to `from_state=None` with the three measured destinations;
4. `to_state` plumbed through `_write_tool`, which does not pass one today --
   so `_direction`'s multi-state branch is currently unreachable in production
   for every action, including `set_open_to_work`.

Point 4 is a finding in its own right and is recorded rather than fixed in
passing: **the multi-state branch that `dacf76d` hardened on 2026-08-31 has no
live caller.** Its `KeyError` fix was correct and shape-closing, and nothing
today can reach the code it protects.

### 3d. AND THE TOOL CANNOT BE CALLED TO SHOW IT

`linkedin_update_setting` is refused by the harness permission classifier (see
0b). So the end-to-end demonstration -- "the gate rendered a direction" -- is
not available to this wave by any route it should take. What IS available and
is reported above: the READING, live, and the wiring proved by test. Those two
are kept apart deliberately rather than blended into a claim that the gate was
seen working.

---

## 4. #4 update_profile_field -- THE INSTRUMENT IS BUILT AND CANNOT YET BE RUN

**The ruling.** A reader scoped to ONE container, measured to be self-owned,
may publish names the document-wide gate would redact. Constraints: scoped to a
single named container on a single self-owned surface; it must ESTABLISH
self-ownership rather than assume it; a SEPARATE entry point from
`linkedin_surface_census`; never reachable for `/feed/` or `/in/<other>/`.

### 4a. The instrument -- `linkedin_profile_editor_fields`, at `3940f72`

**Self-ownership is established per call, on an EXTERNAL assertion.** Load
`/in/me/` and require **LinkedIn's own `isSelfProfile=true`** on the landed
url. That is LinkedIn saying the profile is the viewer's, not this server
reasoning about what `/in/me/` ought to mean -- and the distinction is the
whole of why it is the anchor. Then load `/in/me/edit/intro/` and require the
same member segment. **Fail the first and the editor page is never fetched at
all.**

Neither segment is ever reported. It is compared and discarded, and the landed
paths are redacted TWICE -- once by `shape.census_substitute` and once by a
literal replacement of the segment that call captured, so a slug cannot escape
through whatever the first pass's character class does not cover.

**The container is identified STRUCTURALLY: the nearest dialog ancestor of the
one control named `Save`.** Not `dialog#0` -- that is document order, and
document order is LinkedIn's business. **Two `Save` controls anywhere on the
page is AMBIGUOUS and refuses**, document-wide rather than within the dialog,
because "the one inside the dialog" is itself a rule about position and
position is what this reader exists to refuse.

**What comes off is only the `<opaque>` gate and the singleton blanking.**
`census_substitute` was factored OUT of `census_shape` and is still run, so a
urn, a member path, a company path, a possessive or a long digit run in a label
is replaced whatever container it was read in. `census_shape`'s outputs are
pinned unchanged against the pre-move code.

**LABELS, NEVER VALUES.** A label is "First name"; a value is his first name.
Three layers were shown holding, and the middle one was found by mutation
rather than designed:

| layer | what it caught |
|---|---|
| the JS mutation scan | `el.value` in the script |
| **the field dict's NAMED KEYS** | a value read via `getAttribute` -- dropped silently because the dict enumerates its keys, the same discipline that once lost `container`, here working as a privacy backstop |
| a JSON sweep of the whole answer | the edit that adds the key too, which is what somebody would really write |

`linkedin_surface_census` and `shape.census_shape` are **unmodified in
behaviour**, so nothing already published changes meaning. **The read boundary
is untouched** -- no pattern added, no substring removed; both urls were
already admitted.

### 4b. THE CAPTURE HAS NOT BEEN TAKEN, and the blocker is not this server

The restart landed and the process reports `3940f7278055`, so the tool IS
loaded. **It is not reachable from the calling side:** the MCP tool LIST is
cached a layer above the server process, and a server restart refreshes the
CODE without refreshing the LIST. Confirmed by three separate `ToolSearch`
queries returning no such tool while `linkedin_surface_census` and
`linkedin_server_info` answer normally.

**A `/mcp` reconnect is required and has been requested.** Recorded as a
finding in its own right, because this wave has now hit the same class of
staleness at two layers: **a fix on disk is not a fix in the running process,
and a NEW TOOL in the running process is not a new tool in the client.** The
previous wave's census runs are recorded as having happened "after a `/mcp`
reconnect", which fits.

**No route around it was taken, and two were available and refused.** Driving
`dom.read_self_owned_editor_fields` from a script would mean launching the
Chrome profile from a script, which is forbidden outright -- Chrome 151 runs a
downgrade migration against the older Playwright chromium and DISCARDS the
profile. The CDP bridge needs a Chrome the operator starts himself. Neither is
this agent's to do.

### 4c. `<opaque>` VERSUS NOT-RENDERED -- why it was not "fixed"

The lead asked for this distinction to be fixed or for a reason. **It is
already distinguished, and the pair named is not where the residual conflation
lives.** Measured against `shape.census_shape` directly:

    a readable name          -> the name                  (a row exists)
    a name failing the gate  -> "<opaque>"                (a row exists)
    a control with no name   -> "" + name_source "none"   (a row exists)
    a control not rendered   -> NO ROW AT ALL

So `<opaque>` **implies a row implies the control rendered.** The three
absent-looking outcomes wear three different encodings and a caller can already
tell them apart.

What section 2g of the previous audit actually could not do was say WHICH FIELD
an `<opaque>` row is -- a naming problem, not an encoding one, and precisely
what 4a's reader closes inside the one container the ruling permits.

**The residual conflation, stated rather than left:** `<opaque>` is returned
for a name failing the LENGTH gate and for one failing the CHARACTER-CLASS
gate, and those are different facts. It is not fixed here because inside the
container the gate is off and the question does not arise, and outside it the
distinction would tell a caller that a label is long or is in another script
without naming it either way -- which moves no capability. Named so the next
reader finds a decision rather than an oversight.

### 4d. What the capture will and will not settle

**Will:** whether the intro editor's own fields are among the `<opaque>` set or
were simply not rendered -- the one thing section 2g said it could not
distinguish -- and, if they are named, what they are called and how they are
addressed.

**Will not, and this is unchanged by anything in this wave:** REVERSIBILITY.
Nothing here records a field's PREVIOUS VALUE, so an edit is still not
revertible by this server -- and the reader is built to read labels and
deliberately cannot read values, so it is not the thing that will close it.
**That is a second, independent blocker on #4 and it survives a successful
capture.** A gate that can name a field and cannot restore it is not a gate
this design would open.

---

## 5. #3's ON LABEL -- EXACTLY WHAT HE MUST DO, and one trap in the instrument

The lead's instruction: #3 additionally needs its ON label, which is one
supervised reaction on his own content -- his act, not mine. **Build up to that
point and say exactly what he must do.**

This is that instruction, and it carries a warning about the instrument that
would otherwise waste the act.

### 5a. Why it cannot be measured any other way

`aria-label="Reaction button state: no reaction"` is the OFF state, measured 11
times on 2026-08-30 and re-measured on two later days. LinkedIn writes toggle
state into the accessible name, so the ON label exists and simply has never
been rendered on this account -- nothing on either readable surface has been
reacted to. It is the identical position `unsave_job` was in until 2026-08-30,
and it takes the identical answer: **the missing half is not guessed.** How
unsave got out is the template rather than a precedent for guessing -- one
supervised write produced the label, then a READ-ONLY route re-measured it
three times before the row was written down.

### 5b. What he does

1. **In his own browser, not through this server.** Open his own LinkedIn
   profile and scroll to his activity.
2. **React to TWO of his own posts** -- see 5c for why two rather than one.
   His own posts, so no third party is notified by the act.
3. **Press the reaction control itself, NOT the `Open reactions menu` control
   beside it.** These are two different controls: the toggle carries
   `Reaction button state: ...` and the menu carries `Open reactions menu` with
   `aria-expanded="false"`.
4. **Report which of these two things happened**, because it is the second
   unmeasured thing and one press settles it: did the press apply a reaction
   IMMEDIATELY, or did a picker open first? That is blocker (2) on #3 -- what
   the toggle actually applies -- and a gate that cannot say what it is about
   to express under his name is not a gate.
5. **Leave both reactions in place** until this server has re-read the page.
   After that they can go; the label will already be recorded.

### 5c. THE TRAP, and it is in this server's own instrument

**Two posts rather than one, because a reaction on exactly one post may be
BLANKED by the census before it can be read.**

`shape.census_redact_rare` blanks any run of two or more capitalised words in a
shape seen EXACTLY ONCE. React to one post and the ON label appears exactly
once, `count == 1`, and the rule fires. Whether it blanks anything depends on
capitalisation nobody can know in advance: `Reaction button state: like` would
survive, and something like `Liked Reaction Applied` would come back
`<redacted>` -- and the act would have been spent for nothing.

**Reacting to two posts puts the label at `count == 2`, past the singleton
trigger entirely.** It costs one extra reaction on his own content and it
removes the only way this measurement can fail.

There is a second route that does not have this problem, recorded because it
may be cheaper: `dom.read_reaction_surface` collects labels through
`shape.census_shape` and **not** through `census_redact_rare`, so the reader
behind `linkedin_react_to_item` would report the ON label at count 1. But that
tool's name carries a write verb and this wave has had three such tools refused
by the harness permission classifier, so it should not be relied on. **The
two-post route works through `linkedin_surface_census`, which is not refused.**

### 5d. What this server then does, and what it still will not do

Re-read `linkedin_surface_census("profile")` MORE THAN ONCE and record the ON
label. That is a read-only route and is the `unsave_job` template exactly: the
supervised act is paid once, and the re-measurement is bought with reads.

**It does not lift #3 on its own.** Even with the ON label and the toggle's
behaviour settled, #3 still needs an item key to aim at, which is section 6's
reader. Both are required and neither substitutes for the other. And nothing in
this wave will fire the capability: no `confirm_token` is issued for it, by
anyone, under any circumstances.

---

## 6. #6 RULED, on my own readings

The lead ran the dark-mode census once to verify the process had reloaded, and
said so explicitly: *"I am telling you the instrument is live, not what it
says."* These are my own readings, taken twice, with the settle precondition
checked before either was interpreted.

**Both readings are IDENTICAL, and they agree with the four that preceded
them.**

| reading | when | build | controls | forms | buttons | links | dialogs | redirect |
|---|---|---|---|---|---|---|---|---|
| 1-2 | 2026-08-31, previous wave | `b9d739c` | 20 | 0 | 1 | 16 | 0 | none |
| 3 | today, pre-`checked` | `4f45781` | 20 | 0 | 1 | 16 | 0 | none |
| 4 | today, post-restart | `3940f72` | 20 | 0 | 1 | 16 | 0 | none |
| **5-6** | **today, mine, post-restart** | **`3940f72`** | **20** | **0** | **1** | **16** | **0** | **none** |

**SIX READINGS ACROSS TWO DAYS AND THREE BUILDS, agreeing on every count.**
This is the surface `profile_edit_intro` was not: there is no half-render here
and no reading that had to be thrown away.

    "Always off"        input  aria-labelledby  checked TRUE   source native
    "Always on"         input  aria-labelledby  checked false  source native
    "Device settings"   input  aria-labelledby  checked false  source native
    the other 17                                checked null   source "none"

### THE RULING

**The current dark-mode setting is `Always off`.** Exactly one of three is
checked, read through the native branch off the very control a change would
move.

**#6's NAMED BLOCKER IS CLOSED.** `_direction`'s first two refusals -- no
state, and state `unknown` -- were the whole of why this gate would not render,
and the state is now measurable in one call.

**THE CAPABILITY DOES NOT LIFT, and the reason is structural rather than
missing evidence.** `linkedin_update_setting` holds `url_template=None`, and
`writes.mint` refuses at ISSUE for any such action:

> *"no grant is minted for {action}: its surface has never been loaded by this
> server, so there is no page for a grant to be permission to act on. Refused
> at ISSUE rather than only at use, because an invariant a future click has to
> remember to check is not an invariant."*

So **no `confirm_token` can exist for this action**, whoever calls it. Making
it performable would need a measured write surface and a new entry in
`SANCTIONED_MUTATIONS` -- a new click call site, which this wave was forbidden
to add and which nobody has ruled on.

**The honest close: the gate goes from CANNOT DESCRIBE to CAN DESCRIBE, and the
action stays unperformable.** That is a smaller claim than "the refusal
lifted", and it is the true one.

---

## 7. #9 -- REFUSED BY RULING, with the reason measured

The lead ruled after reading section 2: **`/messaging/compose` is not being
narrowed.** The ruling's own ground, recorded because it is stronger than the
deferral it replaces:

**#9 lands on the identical stop condition set for #1.** A compose surface
autosaves. A message draft lives inside the conversation it belongs to, so
detecting one requires opening a thread -- which is exactly the cost the
deferral existed to avoid. **No draft-detection route, no opening.** Narrowing
`/messaging/compose` would mean lifting a boundary while blind to what passing
through it leaves behind, on a surface that writes to another person.

And the lead's closing argument, which is the transferable part: **that
`/messaging/compose` was the ONE entry kept when the blanket `/messaging` ban
was narrowed on 2026-08-26 is the strongest argument against lifting it now.**
Somebody looked at this exact question with the same evidence and kept it.

So #9's refusal now reads: the badge check PASSED (zero, twice, two surfaces),
the deferral is lifted, and the action is refused on three measured grounds --
the composer address is on the forbidden list; the two sanctioned messaging
tools reach a THREAD and not the composer; and no draft-detection route exists
on any reachable surface.

---

## 8. THE NOTIFICATION BADGE STAYS A DISAGREEMENT

The lead had told the operator the badge moved 1 -> 4, and has corrected that
to him after seeing this wave's reading. Recorded here in the form the lead
asked for -- **as a disagreement, not resolved by picking the larger:**

    Home, 1 new notification              both surfaces, both readings
    Notifications, 0 new notifications    both surfaces, both readings

Two nav controls on one page disagree, consistently. **This server has no
reading that resolves which is the count LinkedIn would consume**, and the only
instrument that would -- loading `/notifications/` -- destroys the very thing
it would measure. So the honest record is two labels and no number.

---

## 9. THE IDENTITY GUARD: a gap, a live leak, and a near-miss of my own

The lead asked me to port the naukri sibling's drive-root rule into this
repo's `tests/test_no_committed_identity.py`, on the premise that **this repo
is clean and the port is therefore cheap insurance.**

**The premise is false. The leak is live here, in tracked and pushed files.**

### 9a. What is actually in the corpus

Measured over all 151 tracked files:

| rule | hits | files | segment |
|---|---|---|---|
| drive root (non-generic) | **31** | **13** | one distinct, 7 chars -- his GIVEN NAME |
| Windows user path | **18** | **9** | one distinct, 4 chars -- the Windows account name |
| POSIX home path | 0 | 0 | -- |

The drive-root hits are not confined to audit prose. They are in `README.md`,
in `linkedin_server/paths.py` and `linkedin_server/buildinfo.py` (vendoring
provenance comments), and three times in `tests/test_path_hygiene.py` -- the
file whose entire job is keeping absolute paths out of this server's output,
and which was using his REAL path as its "a real path looks like this" datum.

### 9b. HOW BOTH OF US MEASURED IT CLEAN, and it is a transport bug

**A shell heredoc collapses the doubled backslash.** Written as `[\/]` and
passed through one, the character class reaches Python as `[\/]` -- an escaped
slash, matching the SLASH ONLY. The check then runs, finds the forward-slash
paths, reports the backslash ones as absent, and exits clean.

The one-line proof, run under that transport:

    re.match(r'[\/]', chr(92))   ->   False

**AND IT ALMOST TOOK ME WITH IT.** My first measurement was a Python FILE, where
the backslashes survive, and it reported 31/13 correctly. I then "corrected" it
twice using shell heredocs and got ZERO both times. **Two agreeing readings, both
wrong, and they looked exactly like a clean result** -- I was one step from
reporting the lead's premise back to them as confirmed.

What stopped it was not a third reading. It was that the two runs DISAGREED with
the first and I refused to report either until I knew which was broken.

> **This is the `profile_edit_intro` limit again, one layer down.** That surface
> produced two agreeing readings that were both wrong because the PAGE had not
> settled. This produced two agreeing readings that were both wrong because the
> TRANSPORT ate an escape. Repetition catches variance; it does not catch a
> stable wrong state, and the stable wrong state can live in the instrument's
> delivery rather than in the thing measured.

**THE RULE THAT FOLLOWS, and it is cheap: a guard whose regex can silently match
nothing must assert that it matches something.** Every rule landed here carries a
CONTROL that fails loudly if the class stops matching a backslash. A PII guard
reporting zero is indistinguishable from a PII guard that is broken, and this one
was broken three times in twenty minutes.

### 9c. SEVERITY -- real, and bounded. Stated both ways

**The given name is already public in this repo by construction.** The GitHub
account is the given name plus digits, it is in the repository URL, and it is the
author name on every commit. The committer email is the GitHub `noreply` form, so
no personal address is exposed.

**So what the path leak ADDS is the local directory layout, not the identity.**
That is operational detail, and it is a materially smaller thing than this shape
was in the sibling repo. It is still worth fixing -- the next absolute path
committed may root at something the handle does not already publish -- but
reporting it as a fresh disclosure of his name would be wrong.

### 9d. The split: what a tree fix does and does not reach

**Cleaning the working tree is mechanical and changes no behaviour.** All six
non-audit sites are inert -- two provenance comments, one `cd` example, three test
data literals whose meaning survives a synthetic name exactly. 49 replacements
across 20 files, each anchored to the PATH SHAPE rather than to the bare name, so
the GitHub handle in urls is untouched: rewriting that would break real links and
would be pretending to fix something that is not a leak.

**It does not reach pushed history, and that is not mine.** This project's own
record is explicit: a force-push makes history unreachable but not unserved,
retained objects stay resolvable by SHA, and **only delete-and-recreate was
measured to remove them.** That is an operator-level decision and it is named here
rather than attempted.

---

## 10. #2 and #3 -- THE ITEM-KEY GAP IS CLOSED

**The ruling.** These are unaimable: the feed carries 0 item permalinks and the
census shapes every urn out, so no tool can hand him an item key. **Build a
reader over his own activity that returns item keys for HIS OWN items only.**
Establish authorship, do not infer it from placement. Never return another
member's item urn, and that must be a test.

### 10a. The reader -- `linkedin_my_activity_items`

**It reads `/in/me/` and NOTHING ELSE, so the read boundary is untouched.** The
ruling named `/in/<member>/recent-activity/all/`, which is measured present as
an href -- but it is NOT on the allowlist, and admitting it would be a
boundary widening to buy a surface his own profile already carries. The profile
renders 8 activity items and 20 item permalinks and is already loaded by three
other tools. **Zero widening, and the recent-activity page stays a separate
ruling nobody needs to make yet.**

**Authorship is established by THREE conjunctive conditions**, all computed
inside the page, all reported, and all required:

1. **LinkedIn's own `isSelfProfile=true`** on the landed url.
2. **UNANIMITY.** Every control whose name starts `Open control menu for post
   by ` carries the SAME author, and there is at least one. This is the rule
   `_read_feed_item` already applies to reaction state -- *a mixed page cannot
   say which item a direction belongs to* -- and it is what makes the pairing
   safe: **if every overflow control on the page names one author, no pairing
   can attribute an item to the wrong person.**
3. **That author is the page owner**, by a stated prefix relation against the
   `h1`, because LinkedIn writes a SHORTENED form of his name into the overflow
   label while the heading carries the full one. The weakness of a prefix rule
   is written into the code rather than hidden: it would also accept a member
   whose name is a prefix of his, which cannot arise once (1) and (2) hold.

**No author string, heading text or member segment ever leaves the page.**

**THE MEASUREMENT THIS RESTS ON is the asymmetry between the two surfaces**, and
it was already in the record without being read as evidence:

    /in/me/   "Open control menu for post by <his name>"  count 8   readable
    /feed/    "Open control menu for post by <redacted>"  count 8   redacted

The profile row came back READABLE at count 8 because eight controls carried
ONE author string; the feed row came back `<redacted>` at the same count
because eight controls carried EIGHT DIFFERENT ones, each blanked as a
singleton and then re-merged. **The profile rail is unanimous and the feed is
not**, and that is measured rather than assumed.

### 10b. The test the ruling demanded, and its failure text

A rail with two authors -- one item his, one another member's, each with its
own urn -- yields **no `items` key at all**. The mutation that removes the
unanimity check in BOTH gates produces a failure whose text carries the other
member's key, which is the whole point:

    E  AssertionError: {'authorship': {'established': True, ..., 'authors_found': 2, ...},
       'items': ['urn:li:activity:...001', 'urn:li:activity:...003'], ...}
    E  assert None == 'mixed_authors'

`...003` is the OTHER member's item. Unmutated it is in no part of the answer.

Two further mutations were run and are worth more than the first:

* **Relaxing unanimity in the SCRIPT ONLY did not produce emission** -- the
  reader's own Python check caught it. Defence in depth that was designed in
  and then demonstrated, rather than claimed.
* **Dropping the requirement that a urn be paired to an item root carrying an
  overflow control** leaves the refusal intact and publishes nothing, but
  `distinct_urns` goes 2 -> 3 as a stray rail-footer permalink is swept in.
  The test asserts the pairing COUNTS as well as the absence, because without
  them a refusal would hide the fact that the pairing rule had stopped running.

### 10c. AND NEITHER #2 NOR #3 LIFTS -- see section 12

The item-key gap is closed and it turns out not to have been the binding
constraint. Both actions hold `url_template=None`, so no token can exist for
either. #2 additionally has never had its comment box observed
(`contenteditable == 0` on both surfaces); #3 additionally has never seen its
ON label, and the supervised act that would produce it is the operator's to
choose and is **not scheduled**.

---

## 11. #4 -- CLOSED, and the blocker is the plumbing

The instrument is built, committed, and LOADED in the server process. **It is
unreachable from this agent, and a `/mcp` reconnect did not change that.**

The operator ran `/mcp`. Afterwards the harness delivered a fresh enumeration
of every available tool: **it lists 31 `linkedin` tools, and both tools added
this wave are absent from it**, while `linkedin_surface_census` and
`linkedin_react_to_item` resolve normally. Six `ToolSearch` queries across the
wave, none resolving.

> **THE FINDING, and it is worth more than the capture would have been: a tool
> registered AFTER a subagent spawns is unreachable to that subagent,
> regardless of client reconnects.** The tool registry is snapshotted at spawn.
> A server restart refreshes the CODE; a client reconnect refreshes the
> PARENT's registry; neither reaches a subagent already running.

That is a real constraint on how this project runs waves: **an agent cannot
exercise an instrument it builds during the same wave.** Building the
instrument and capturing with it have to be different agents, or the capture
belongs to whoever spawned the builder.

**#4 therefore refuses, and the reason is neither measurement nor ruling.** It
is that the instrument cannot be delivered to the process that would run it.
And the second blocker recorded in section 4d survives regardless: nothing
records a field's PREVIOUS VALUE, so an edit is still not revertible by this
server.

---

## 12. THE STRUCTURAL FINDING: no token can exist for ANY of the seven

Measured across `SANCTIONED_WRITES`, and it reframes this whole wave:

| | actions |
|---|---|
| holds a `url_template` -- CAN mint | `apply_job`, `follow_company`, `save_job`, `unfollow_company`, `unsave_job` |
| `url_template is None` -- CANNOT mint | **all seven refusing capabilities**, plus `set_open_to_work` |

`writes.mint` refuses at ISSUE for any action with no `url_template`:

> *"no grant is minted for {action}: its surface has never been loaded by this
> server, so there is no page for a grant to be permission to act on. Refused
> at ISSUE rather than only at use, because an invariant a future click has to
> remember to check is not an invariant."*

**So no `confirm_token` can exist for any of the six capabilities this wave was
sent to lift -- for me, for the lead, or for the operator.** Not one of them
could have been made performable by any measurement or any ruling reachable
from here, because performing requires a WRITE SURFACE THAT HAS BEEN LOADED,
and none has been. Making one performable needs a new entry in
`SANCTIONED_MUTATIONS` -- a new click call site -- which this wave was
forbidden to add and which nobody has ruled on.

**THE NEVER-FIRE RULE WAS NEVER THE BINDING CONSTRAINT ON ANY OF THEM.** That
is not an argument for relaxing it; it is the observation that the architecture
had already made these actions unperformable, and the rule and the architecture
agreed. What the rulings and instruments could change is **what the gate can
SAY** -- and on that measure the wave moved four of the six.

---

## 13. THE GUARD PORT, AND THE RULE-SET DIFF

### 13a. What landed

Three rules, in `tests/test_no_committed_identity.py`: **drive root**,
**Windows user path**, **POSIX home path**. Semantics ported from the naukri
sibling rather than reinvented, because two guards sharing a filename and
differing in coverage is how the asymmetry arose in the first place.

Two predicates, and their asymmetry is deliberate:

* `_drive_root_ok` allows a first segment that is a GENERIC PLACE -- `users`,
  `windows`, `workspace`, `dev-cache`, `temp`, `repo` -- or a placeholder.
* `_account_path_ok` has **no generic list at all**. The segment after
  `Users/` or `/home/` is an ACCOUNT NAME by construction, so there is no
  benign vocabulary for it and only a visible placeholder may sit there.

### 13b. The corpus was cleaned first, because the guard could not land otherwise

**49 replacements across 20 files**, each anchored to the PATH SHAPE rather
than to the bare name, so the GitHub handle in urls is untouched -- rewriting
that would break real links and would be pretending to fix something that is
not a leak.

Re-measured afterwards with the controlled instrument: **drive root 0 hits,
Windows user path 0 hits.**

The six non-audit sites were inert: two vendoring-provenance comments, one
`cd` example in the README, and three literals in `tests/test_path_hygiene.py`.
**That last one is the sharpest instance in the whole finding** -- the file
whose entire job is keeping absolute paths out of this server's output was
proving it detects real paths BY CARRYING ONE. A synthetic name does that job
strictly better: a hygiene test that demonstrates itself with the thing it
forbids is the same self-refuting shape as a guard that cannot match a
backslash.

### 13c. THE CONTROL, and it is worth more than the rules

`test_the_path_rules_can_match_a_backslash_at_all` asserts, from `chr(92)`
rather than from an escape, that each rule matches the thing it exists to
match -- **before** the sweep is allowed to certify that it matched nothing.

It earned its place three times over in one afternoon. Every one of these
reported this repository CLEAN and every one was broken:

| broken check | how |
|---|---|
| a `git grep` | the pattern never reached the engine intact |
| a rewrite of it | a backslash before `+` made the plus a literal, matching nothing |
| a correct pattern, run twice through a shell heredoc | `[\/]` collapsed to `[\/]` -- the SLASH only |

**And the guard then caught the test that proves the guard works.** The
slash-spelling assertion was first written as a literal and the file's own
sweep failed on it: *"1 unallowed drive root hit(s), 0 declared"*. That is the
most direct demonstration available that these rules are not inert.

Shown failing at the mutation they catch -- the `SHAPES` entry removed:

    FAILED test_every_shape_can_actually_fail[drive root-<the composed plant>]
    FAILED test_the_drive_root_rule_catches_what_the_user_path_rule_cannot

### 13d. `DECLARED_PLANTS` IS UNTOUCHED, and how

Every other plant in that file is a literal with a declared count. The path
plants are **composed from `chr(92)` and string concatenation**, so no
drive-root or home-path shape exists in the file's TEXT and no new entry is
needed.

That deviates from the file's own stated preference -- it argues against
assembling shapes at runtime -- so the reason is written in beside it and is
specific to this shape: **hiding a plant of mine does not blind the sweep to a
REAL path pasted into this file later**, which is the property the urn entries
were protecting; and a backslash does not survive transport reliably, so
composing from the code point is the only way to write a backslash-bearing
test value that is certainly the value intended. The composition buys
correctness and the absent allowlist entry is a consequence rather than the
goal.

### 13e. THE DIFF: ten classes naukri catches that this repo did not

| class | hits here | disposition |
|---|---|---|
| drive root | **31 / 13 files** | **PORTED** -- the live leak |
| user path (Windows) | **18 / 9 files** | **PORTED** -- same class |
| user path (POSIX) | 0 | **PORTED** -- free, and completes the family |
| hex32 id | 5 / 4 files | **DELIBERATELY NOT PORTED -- see below** |
| hex64 id | 2 / 1 file | not ported, same reason |
| account id `key=value` | 2 / 2 files | named, not taken |
| credential assign | 2 / 2 files | named; both hits are in the guards' own test files |
| AWS key | 0 | named, cheap, worth a later wave |
| GitHub token | 0 | named, cheap, worth a later wave |
| PEM private key block | 0 | named, cheap, worth a later wave |

**SOME OF THE ASYMMETRY IS FIT, NOT GAP, and hex32 is the case that proves
it.** Naukri's rule would fire on this repo's deliberate `sha256(first 32)`
convention -- adopted here precisely so the identity guard would STOP firing
on full hashes, and now present in four audit files. Porting it would break a
convention that exists for a reason. **Two guards sharing a filename are not
supposed to converge to one rule set**; they are supposed to cover their own
corpus, and flattening them would have been the wrong move dressed as
consistency.

This repo also carries five classes naukri lacks -- LinkedIn slug, company id,
`ACoAA` member token, urn id, cookie shape -- all correctly platform-specific.

---

## 14. #6 UPDATED: the wiring landed, and section 3c is superseded

Section 3c said the refusal did not lift **yet** and named four wiring steps.
All four are done, so that paragraph is superseded rather than deleted:

1. `_read_dark_mode` -- calls `dom.read_surface_census`, so **no new script and
   no new `evaluate` waiver**. Exactly one checked is the only readable state;
   zero and two-or-more are both refused, the second because choosing between
   them would be choosing by position.
2. `_SURFACE_READS` gained `setting_dark_mode` **and lost `settings_index`**.
   The swap is the point: the old entry pointed at a page that hands out
   ADDRESSES and switches nothing, so the only state it could report was how
   many settings exist. `_read_settings_index` went with it -- this spec was
   its only caller.
3. The spec moved to `from_state=None` with the three measured destinations.
4. **`to_state` is plumbed through `_write_tool`**, which closes the finding
   section 3c raised: `_direction`'s multi-state branch had NO LIVE CALLER for
   any action. The `KeyError` fix `dacf76d` landed on it that morning guarded
   code nothing could reach. It is reachable and exercised now.

**A GUARD AT THE TOOL, because the reader cannot have one.** `writes.observe`
picks its surface from the SPEC's `state_from` and never from an argument --
that is the property stopping a caller aiming this server at a page of its
choosing, and its consequence is that the reader opens the dark-mode page
whatever setting was asked about. Without a check at the tool, a question about
"language" would come back describing dark mode's state under the label of the
setting asked for: **a gate confidently reporting a measurement of the wrong
thing, which is worse than one that refuses.** `linkedin_update_setting` now
refuses any other setting and **loads nothing at all** doing it.

**AND THE `audiences` DOCSTRING WAS CORRECTED, because it was false in a way
that mattered.** It read *"For a setting with an audience: who can see each
destination"* -- while `_direction` validates BOTH the destination AND the
measured origin against `sorted(spec.audiences)` and refuses anything absent
from it. **The keys ARE the enumeration of legal states.** A reader taking the
old sentence literally would leave it empty for an action with no audience,
which makes `_direction` refuse every destination there is. Dark mode's three
values say "NOBODY" in words rather than being blank, because a blank is
indistinguishable from nobody having filled it in.

### #6's final position

**The refusal STANDS, and it stands on section 12's structural ground rather
than on a missing measurement.** `update_setting` holds no `url_template`, so
`mint` refuses it a grant at issue and no `confirm_token` can exist for it.
What changed is real and is smaller than "lifted": **the gate went from
refusing to render at all, to rendering a true current state and a named
direction with no token attached.** Its refusal text now says so, and names
what would lift it -- a measured write surface and a deliberate
`SANCTIONED_MUTATIONS` entry, which is a decision about this account rather
than a measurement.

---

## 15. THE TRANSPORT TRAP CAUGHT ME A THIRD TIME, in the fix for it

Recorded because it is the same lesson and because leaving it out would make
section 9b read as a problem I had solved.

After the guard landed, its sweep failed on **this document** -- I had pasted
a mutation's failure text carrying a drive-rooted plant. I wrote a redaction
for it, ran it, and it reported success. **It had changed nothing:** my
replacement string was written with DOUBLED backslashes and the file contained
single ones, so the match never fired and the assertion that would have caught
it was the one I had just written to skip. The guard failed again on the next
run, in the same place.

Three lessons, and the third is the one worth carrying:

* The fix for an escaping bug is itself written in the language that has the
  escaping bug.
* **A replacement that reports "done" without asserting it changed something
  is the same defect as a guard that reports zero without asserting it can
  match** -- and I had just written a whole section about the second while
  committing the first.
* What caught it both times was not care. It was **an instrument that fails
  loudly on the file it is pointed at**, running in a suite I could not talk
  past. The audit and the guard were written by the same process; only one of
  them was checkable, and that is the one that found the error.

---

# 16. THE CLOSE

## 16.1 The ledger

| # | capability | outcome |
|---|---|---|
| 1 | publish a post | **REFUSES.** No content-draft surface is reachable -- 17 of 17 candidate addresses refused by the read boundary, which makes the href enumeration's incompleteness irrelevant. **The composer was NOT opened**, per the ruling's own stop condition. |
| 2 | comment on an item | **REFUSES.** The item-key gap is CLOSED. Still no comment box observed on either surface, and no token can exist. |
| 3 | react to an item | **REFUSES.** The item-key gap is CLOSED. The ON label is still unmeasured; the supervised act is the operator's, and it is not scheduled. No token can exist. |
| 4 | edit a profile field | **REFUSES.** The instrument is built, tested and LOADED -- and undeliverable to the process that would run it. Reversibility remains unmeasured independently. |
| 5 | endorse a skill | **IMPOSSIBLE.** Unchanged: the control lives only on a third party's profile and loading one is a measured emission. |
| 6 | change a setting | **REFUSES.** The reading was TAKEN -- `Always off`, six agreeing readings across two days and three builds. The gate now renders a true direction. No token can exist. |
| 7 | send an invitation | **REFUSES.** Untouched this wave, and refused by the harness classifier as well. |
| 9 | send a message | **REFUSED BY RULING.** The badge check PASSED at zero; the lead declined to narrow `/messaging/compose` on the stop condition #1 established. |

**ZERO REFUSALS LIFTED, and section 12 is why that was never available.** All
seven hold `url_template=None`, so `writes.mint` refuses a grant at issue and
**no `confirm_token` can exist for any of them, for anyone**. Not one could
have been made performable by a measurement or by any ruling reachable from
here. **The never-fire rule was never the binding constraint** -- the
architecture had already made these unperformable, and the rule and the
architecture agreed.

**FIVE REFUSALS CHANGED THEIR REASON**, which is the axis that was available:

| # | from | to |
|---|---|---|
| 1 | "opening might leave a draft we cannot see" -- an objection | 17 addresses refused, measured |
| 2, 3 | "unaimable; no route to an item key" | a route exists and is tested |
| 6 | "the census reports disabled, not checked" | `Always off`, and a rendering gate |
| 9 | "deferred by ruling" | the composer address is forbidden, and opening messaging does not reach it |

## 16.2 What was delivered

* **Four instruments**: a `checked` reading on the census; a self-owned
  container reader publishing names the document-wide gate withholds; an
  own-activity reader returning item keys for his items only; and three path
  rules in the identity guard.
* **A live PII leak found, measured and cleaned** -- 49 absolute paths across
  20 tracked, pushed files, including in the test whose job is preventing
  exactly that.
* **Two false claims corrected in code**: `audiences`' docstring, which
  under-described the field `_direction` validates against; and
  `_direction`'s multi-state branch, which had no live caller at all.

## 16.3 What was NOT done, deliberately

**No `confirm_token` was issued to anything, by anyone, at any point. No write
was performed. No third party's profile was loaded. No badge was spent** --
messaging read zero at the start and at the end. **The composer was not
opened. `_state/` was not touched.**

**THE READ BOUNDARY IS BYTE-IDENTICAL.** `linkedin_server/readonly.py` is
UNCHANGED across the entire wave: 17 allowlist patterns, 24 forbidden
substrings, one exemption, none added and none removed. `SANCTIONED_MUTATIONS`
is the 2 entries it was; `PERFORMABLE` is the same 5. **Zero new click call
sites.** Three capabilities were closed out without widening anything, and the
one instrument that could have justified a widening -- the activity reader --
was deliberately built on a surface already admitted.

    _state/session.json
      sha256(first 32)  f0892e35688868faef6a3525e54b93e4
      bytes             7813
      mtime             2026-08-26 00:41:24
      -- identical to the value recorded at the end of the previous wave.

    baseline   4f45781   suite 2132
    final      9a9d65c   suite 2267 passed, 0 failed
    34 files changed

Nothing was pushed. The push and its PII scan are the lead's -- and this wave
is the reason to run the repository's own committed guard rather than a
hand-rolled scan, because a hand-rolled scan is exactly what missed this.

## 16.4 The three findings worth carrying past this repo

1. **Repetition through one broken channel is not repetition.** Two agreeing
   readings were wrong twice in one day -- once because a PAGE had not
   settled, once because a TRANSPORT ate an escape. The at-least-twice rule
   catches variance and cannot catch a stable wrong state, and the stable
   wrong state can live in the instrument's delivery rather than in the thing
   measured.
2. **A guard that can silently match nothing must assert that it matches
   something.** Reporting zero and being broken are indistinguishable from
   the outside. Three checks reported this repository clean in ten minutes and
   all three were broken.
3. **An agent cannot exercise an instrument it builds in the same wave.** A
   tool registered after a subagent spawns is unreachable to it regardless of
   server restarts or client reconnects. Building and capturing have to be
   different agents -- or the capture belongs to whoever spawned the builder.

## 17. CORRECTION: "0 and 0" WAS WRONG, and the guard was blind to the doubled spelling

**Section 13b's re-measurement, and section 16.3's clean bill, were both taken
with an instrument that could not see what it was looking for.** The lead
caught it. Three given-name drive roots survived in tracked files, and the
guard I had just landed passed over all three.

### 17a. The defect

`DRIVE_ROOT_PATH` was `[A-Za-z]:[\/]([A-Za-z0-9_.-]{2,})`. **`[\/]` matches
exactly ONE separator character.** Against a doubled separator, the class
consumes the first backslash and the capture group must then start on the
second -- which is not in `[A-Za-z0-9_.-]`. No match.

Measured against the shipped rule, importing the compiled pattern rather than
retyping it:

    single separator    D:\<name>     matched, WOULD FAIL      (rule works)
    DOUBLE separator    D:\<name>    no match -- BLIND

**The doubled spelling is not an edge case.** It is how a Windows path is
written inside JSON, inside a Python string literal, and inside any prose
quoting either. So the cleanup removed the 46 occurrences the rule could see
and left exactly the 3 it could not, and the re-measurement that reported zero
shared the blindness.

`_drive_root_ok` was correct throughout -- the segment is not generic and
carries no placeholder, so it would have failed the file if the pattern had
ever reached it. **The predicate was right and the pattern never got there.**

### 17b. The three survivors, and what two of them were

| file | what it was |
|---|---|
| `README.md` | a JSON config example, where `\` is CORRECT JSON |
| `linkedin_server/paths.py` | a COMMENT describing the 2026-08-20 sweep |
| `tests/test_path_hygiene.py` | a COMMENT describing the same sweep |

**Two of the three were documentation of this very leak** -- prose explaining
that a sweep found this path shape inside MCP configs, which quoted the real
path in order to say so. That is the identical self-refuting shape as
`test_path_hygiene.py:151` proving it detects real paths by carrying one: the
instance I had already fixed, in prose, two files over, and I did not look for
its siblings.

The README case was fixed by **replacing the VALUE and not the escaping** -- a
reader copying that config needs a real path there, and the doubled backslash
is correct JSON.

### 17c. The fix, and the generalisation that outranks it

Every separator run in all three rules is now `+`. Shown failing by narrowing
it back:

    E  AssertionError: DRIVE_ROOT_PATH is blind to a separator run of 2;
       that is how three of these sat at HEAD
    FAILED test_every_shape_can_actually_fail[drive root-"args": [...]]
    FAILED test_the_path_rules_can_match_a_backslash_at_all

**That mutation is a REAL HISTORICAL DEFECT rather than a synthetic one**, and
the doubled form is now a permanent plant in the can-fail table.

> **THE GENERALISATION, and it is worth more than the quantifier: a control
> must cover every spelling the value can be WRITTEN in, not just the one the
> author had in mind.** Section 13c said a guard reporting zero without
> asserting it can match is indistinguishable from a broken one. Mine asserted
> it could match ONE spelling -- which is the same defect one level down, and I
> committed it in the same breath as writing the rule against it.

### 17d. The count

**This was the FIFTH instance of the escaping trap in one day, and the first
one committed and load-bearing:** a `git grep` that reported clean; a rewrite
whose backslash escaped a `+`; two heredoc "corrections" that agreed with each
other and were both wrong; a redaction that reported success and changed
nothing; and now a shipped PII rule blind to half the spellings of the thing it
exists to catch. **A sixth occurred while writing this section** -- the mutation
script's anchor was collapsed by a heredoc and refused to apply, which it
caught only because it asserts its replacement count before writing.

Every instance has one shape: **the fix for an escaping bug is written in the
language that has the escaping bug.** The two things that actually caught them
were never care. They were an instrument that fails loudly on the file it is
pointed at, and a second reader measuring independently.

Re-measured after the fix, with the widened pattern and the control asserting
both spellings: **survivors 0.** Stated with less confidence than last time,
because last time was wrong.

---

## 18. THE THIRD SURVIVOR CANNOT BE FIXED FROM THIS REPO -- and the wave ends one test red

`linkedin_server/paths.py` is a **VENDORED COPY**. Its own header says
`DO NOT EDIT THIS FILE`, and `tests/test_vendored_buildinfo.py` enforces that
by comparing its body against **jobcore at the pinned commit `6acc7e6`** --
not against jobcore's working tree.

**So the leak in that file is upstream, and the two guards are in direct
conflict:**

| action | vendoring pin | identity guard |
|---|---|---|
| fix the vendored copy | **FAILS** -- body diverges from the pinned commit | passes |
| leave it | passes | **FAILS** -- a real given name in a tracked file |

Both states were measured, not reasoned about. There is no third state
reachable from inside this repository.

**I edited jobcore's source to test the theory and REVERTED IT.** The edit
proved the leak is at `jobcore/src/jobcore/paths.py` line 3 and that a
working-tree fix there does not satisfy the pin, because the pin reads a
COMMIT. jobcore is a separate repository with its own remote and its own
history question; committing to it and then bumping this repo's vendor pin is a
two-repo change with push implications, and it is not mine to make. **jobcore
is left exactly as found: clean.**

**THE WAVE THEREFORE CLOSES WITH ONE TEST RED, and it is red for the right
reason.** `test_no_tracked_file_carries_a_real_identifier[linkedin_server/paths.py]`
is not a broken test; it is the instrument reporting a leak that exists. Every
other test passes.

### What would close it, in order

1. Fix the docstring in `jobcore/src/jobcore/paths.py` -- one comment line,
   zero behaviour -- and commit it there.
2. Bump `linkedin_server/paths.py`'s vendor header to the new jobcore commit
   and re-vendor the body.
3. Re-run both guards; the conflict dissolves because the copy and its source
   agree again.

**And a question worth asking before step 1:** jobcore is a pushed repository
that nobody has swept. Its `paths.py` carries this shape at line 3 -- found
incidentally, by following this one file. **Nothing here establishes that it is
the only instance in that repo**, and the same guard does not exist there.

### The alternative I did NOT take

`DECLARED_PLANTS` would silence it. **It stays untouched.** The lead's ruling
was that the fix is removing the real value rather than declaring it, and while
this case is genuinely different -- the value cannot be removed from this repo
at all -- that difference is an argument for a ruling, not for me assuming one.
Declaring a real identifier to make a suite green is the exact trade this
guard exists to refuse, and it should be somebody's explicit decision if it is
made.
