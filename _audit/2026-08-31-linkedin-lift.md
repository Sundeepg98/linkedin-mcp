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
