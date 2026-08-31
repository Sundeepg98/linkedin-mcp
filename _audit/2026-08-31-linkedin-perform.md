# Making the capabilities performable: what a surface bought, and what a
# mutation class still refuses

Date 2026-08-31. Repo `linkedin`, branch `master`. Baseline `fbe2aef`, suite
2267 passed / 1 failed. Final `64e655c`, suite **2306 passed, 0 failed**.

**No `confirm_token` was used, by anyone, at any point. No write was
performed. No third party's profile was loaded. The messaging badge was not
spent -- it read `Messaging, 0 new notifications` at the start, immediately
before the composer work, and no messaging surface was ever opened.
`_state/session.json` is byte-identical.**

---

## 0. THE FINDING THAT REFRAMES THE WHOLE LEDGER, and it is a correction to
## this repository rather than to LinkedIn

The previous wave closed with *"ZERO REFUSALS LIFTED, and section 12 is why
that was never available"* -- the argument being that every one of the seven
holds `url_template=None`, so `mint` refuses at issue, and that **making one
performable "needs a new entry in `SANCTIONED_MUTATIONS` -- a new click call
site -- which this wave was forbidden to add and which nobody has ruled on."**

**The first half of that is true. The second half is false, and it is why the
conclusion was wrong.**

`readonly.SANCTIONED_MUTATIONS` is keyed by `(path, function, kind)` and its
first entry is:

    ("linkedin_server/writes.py", "perform", "click")

That is not permission to perform ONE ACTION. It is permission for ONE
FUNCTION to make one KIND of call. **`perform` may click any control it can
NAME.** What the list refuses is a click somewhere ELSE in the package, or a
mutation of another KIND inside `perform`. The sentence read a permission
scoped to a CALL SITE as though it were scoped to an action, and a whole
wave's conclusion rested on it.

**WHAT THE LIST DOES STILL REFUSE, and it is the real blocker for four of the
eight.** These are on `readonly._MUTATION_CALL_PATTERNS` and on **no entry of
`SANCTIONED_MUTATIONS`, for any function, anywhere in this package**:

    fill        .fill(
    type_text   .type(
    press       .press(
    keyboard    .keyboard

So the eight split on a line nobody had drawn:

| | actions | what stands in the way |
|---|---|---|
| **CLICK ONLY** | `update_setting`, `react_to_item`, `send_invitation` | a measured surface and a measured anchor. Nothing else. |
| **MUST TYPE** | `publish_post`, `comment_on_item`, `update_profile_field`, `send_message` | a MUTATION CLASS nobody has sanctioned. A url does not reach it. |
| **no url at all** | `set_open_to_work` | its editor is a modal with no href -- re-measured today |

**That is a measured structural split and it is the single most useful thing
in this document.** Four of the eight were never one ruling away from
performable, and no amount of surface admission would have changed that. The
other four were much closer than the previous wave concluded.

`SANCTIONED_MUTATIONS` **is unchanged across this entire wave** -- the two
entries it has held since 2026-08-26. Nothing was permitted in order to ship
anything.

---

## 1. #6 `update_setting` -- **PERFORMABLE**, and it is the first of the eight

### 1a. What it got, and what licensed each part

| | value | the measurement licensing it |
|---|---|---|
| `url_template` | `https://www.linkedin.com/mypreferences/d/dark-mode` | SIX readings across two days and three builds, every one landing on that exact url with no redirect and reporting 20 controls / 0 forms / 1 button / 16 links / 0 dialogs |
| `url_pattern` | `^https://www\.linkedin\.com/mypreferences/d/dark-mode/?$` | anchored to that one page; a second settings page needs a second deliberate edit |
| anchor | the radio named for the DESTINATION | three inputs named through `aria-labelledby`, exactly one `checked`, measured six times |
| selector | `role=<role>[name="<destination>"][exact=true]` | the ROLE is read off the row at click time -- see 1b |
| verification | a fresh navigation and a re-read of the whole group | the strongest in this package -- see 1c |

**NO `{target}` IN THE TEMPLATE, deliberately.** The target names a setting and
a value and NEITHER belongs in a url: the page is one fixed address and the
destination is chosen by which control is clicked on it. `.format()` over a
string with no placeholder returns it unchanged, so `assert_write_url`'s
rebuild-and-compare still runs -- there is simply nothing for a caller to
influence.

### 1b. THE ROLE IS READ, NOT ASSUMED, and this is what the census gained

Six readings establish three **checkable** inputs. **Not one of them
establishes which of the two checkable types they are** -- `checkedOf`'s type
gate admits `radio` and `checkbox` alike, and both come back
`checked_source: "native"`. An input's ARIA role is decided by its type, and
Playwright's accessible-name selector engine is addressed BY ROLE, so a
selector built on the wrong one matches nothing.

So `input_type` joined the census as its **eleventh merge-key field**, and
`_live_control` builds the selector from the role the page reports.

**CONFIRMED LIVE** on the feed census after the restart: `<input
type="radio">` rows report `"radio"`, every non-input reports `null`.

### 1c. The verification, and why it is the strongest here

The save pair is confirmed from a DIFFERENT surface, which is the ideal shape.
A setting has no second surface -- **the page that renders the value is the
page that sets it.** So this reloads and re-reads, and what it reads is not a
label the control chose to draw: it is the browser's own `checked` property
across a group of three, where exactly one being on is a structural fact
rather than a string. **A control that redrew wrongly would have to report
itself checked AND the other two report themselves unchecked to pass.**

The block says exactly that rather than borrowing the save pair's "a DIFFERENT
surface", which it did until this action shipped -- a false claim in the
block the operator reads, found and fixed.

### 1d. Reversibility -- STILL-UNKNOWN, deliberately

The inverse of this action **is** this action with a different destination
named. All three states are measured to exist, all readable, all reachable
from each other through the same three controls.

**And `reversibility_measured` stays `False`.** Nobody has performed a
dark-mode change and read it back, so the round trip is UNPERFORMED, and
`_reversibility_disagreement` enforces that an unmeasured claim may not wear a
measured class. The structural argument is strong and it is not a
measurement.

**One stale claim corrected:** `reversible_by` read *"NOT this server: the
pages carrying the values are unreachable in either direction."* True of every
settings page when written, false of this one now. Narrowed rather than
deleted -- the forbidden entries it cited still make every OTHER setting
unreachable both ways.

### 1e. What firing it would cost him

**The least of any write in this package.** Dark mode is a per-account DISPLAY
preference: no audience, no other member can observe it, broadcast nowhere,
appears in no feed and no notification, and the same tool sets it back. That
is precisely why it was the settings page admitted.

### 1f. It was NOT fired, and I did not call the tool at all

From the restart onward a **preview** of `update_setting` would MINT a live
token -- minting is what a preview does. The capability is proved by the suite
and by nine mutations; calling the tool would have put a live token in the
process and bought no measurement. So `linkedin_update_setting` was never
called.

---

## 2. #1 `publish_post` -- **THE CAPTURE THE OPERATOR CLEARED WAS TAKEN**, and
## it lifted one of the two blockers

`linkedin_surface_census("post_composer")`, live, after the restart:

    source_url   https://www.linkedin.com/preload/sharebox/    <- NO REDIRECT
    counts       forms 0  buttons 20  links 7  dialogs 1
                 contenteditable 2        <- THE FIRST NON-ZERO EVER MEASURED
    controls_read 31

The two controls #1 has been missing for four waves, both inside `dialog#0`:

    "Text editor for creating content"   div[role=textbox]  aria-label
    "Post"                               button  text       DISABLED

Also in the dialog: `Add media`, `Celebrate an occasion`, `Create an event`,
`Schedule post`, `More`, `Dismiss`, and an audience control.

**`contenteditable == 0` HAS BEEN THE STANDING MEASUREMENT ON EVERY SURFACE
THIS SERVER COULD READ**, and it was the whole of the "NO CONTROL" half of
#1's refusal. It is now 2, on a page reached by NAVIGATION -- no click, no
typing, nothing submitted.

**`Post` renders DISABLED on an empty composer.** That is a safety fact worth
having on its own: the publish control is not merely present, it is
inoperative until there is something to publish.

### 2a. WAS ANYTHING LEFT BEHIND? Reported by what exists, and not further

The lead's instruction was to report explicitly and not to claim what cannot
be seen. Three things were checked and one cannot be:

| probe | before | after | reading |
|---|---|---|---|
| his own activity rail, item count | 8 | **8** | no new item |
| the same rail, permalink anchors | 20 | **20** | unchanged |
| `Post` control state | -- | **disabled** | an empty composer cannot publish |
| **a saved DRAFT** | -- | -- | **NOT DETECTABLE. See below.** |

**NOTHING DETECTABLE WAS LEFT BEHIND, AND A DRAFT IS NOT DETECTABLE.** Those
are two statements and both belong in the record. The previous wave ran 17
candidate draft-listing addresses against this module's own read boundary and
**all 17 were refused**, so there is no reachable surface on which a draft
could be seen or removed. The activity-rail probe settles PUBLICATION, which
is the larger of the two costs and the only one with an instrument.

`Post impressions 61` was NOT re-read and the reason is that it is the weaker
probe, not that it was skipped: it is a rolling analytics figure and a
brand-new post with no impressions would not move it. The activity rail is
where a published post appears immediately, and it is flat.

### 2b. #1 STILL REFUSES, and now on ONE blocker instead of two

| blocker | before today | after |
|---|---|---|
| NO SURFACE -- `/preload/sharebox/` not on the allowlist | live | **CLOSED.** Admitted by name, captured, no redirect. |
| NO CONTROL -- the editor and the publish control never observed | live | **CLOSED.** Both named, both inside `dialog#0`. |
| **MUST TYPE** | not identified | **LIVE, and it is measured.** Publishing means entering text into `Text editor for creating content`. `fill`, `type`, `press` and `keyboard` are on `_MUTATION_CALL_PATTERNS` and on no entry of `SANCTIONED_MUTATIONS`. |

**What firing it would cost him, unchanged and re-measured:** a post is a
BROADCAST. His profile reports 274 followers today, and LinkedIn's own
analytics on it show past posts at 113, 318 and 1,287 impressions. Whether a
post can be deleted is still UNMEASURED -- the per-post overflow menu renders
collapsed and its items have never been read. It is the one artefact in this
design a current employer sees without looking for it.

**WHAT WOULD LIFT IT** is now exactly one thing and it is not a measurement:
a ruling sanctioning a text-entry mutation for `perform`. That is a new
mutation CLASS in this package's boundary, which is a larger decision than a
url, and it is named here rather than assumed.

---

## 3. #9 `send_message` and the ARTICLE COMPOSER -- **REFUSED BY THE HARNESS,
## not routed around**

`linkedin_surface_census("article_composer")` and
`linkedin_surface_census("messaging_compose")` were both **denied by the
Claude Code permission classifier**, which sits outside this server. The
`post_composer` key on the identical tool went through, so what was refused is
the ARGUMENT, not the tool.

**NEITHER WAS ROUTED AROUND, and two routes were available and declined.** A
different spelling of the key, or reaching the same page through another
tool, is exactly the "find another door to the same act" that this project has
refused three times already. A denial is recorded and stopped at.

**ONE CONSEQUENCE IS GOOD AND IS WORTH STATING: HIS MESSAGING BADGE WAS NOT
SPENT.** The operator's ruling was conditioned on that badge reading zero
first, which it did -- `Messaging, 0 new notifications`, count 1, on `/feed/`
and on his profile at the start of the wave and again immediately before the
composer work. The artefact he authorised remains unspent, because the capture
never happened.

**#9 therefore stays refusing on THREE grounds, and the order matters:**

1. **IT MUST TYPE.** Even a perfect capture could not lift it. This is the
   binding constraint and it is the one nobody had identified.
2. The composer surface is admitted now but was never loaded, so no anchor is
   measured.
3. The capture was refused outside this server.

The boundary change for `/messaging/compose/` is real and it is the narrowest
in this wave: an **exact-url exemption**, so `"/messaging/compose"` stays on
the forbidden tuple and every other spelling in that family refuses exactly as
before -- measured, in `tests/test_readonly.py`, on `?recipient=`, `new/` and
the pre-filled overlay.

**A NOTE ON WHETHER THAT WIDENING SHOULD STAND.** The lead's own withdrawn
ruling established that *a read-boundary widening with no consumer is strictly
negative*. This one HAS a consumer -- `linkedin_surface_census("messaging_compose")`
is a registered surface a caller can invoke -- so it is not the shape that
ruling condemned. But nobody has loaded it, and if the operator would rather
the entry come out until somebody can, that is a one-line revert and it is his
call. It is flagged rather than left to be noticed.

---

## 4. #3 `react_to_item` -- **REFUSES**, and the aiming reader refused the live
## page for a reason nobody had

This is the capability that consumed the most of this wave and it did not
lift. What happened is worth more than the outcome.

### 4a. The reader built last wave REFUSES THE LIVE PROFILE

`linkedin_my_activity_items`, run twice, identically:

    refused                   no_page_owner_heading
    self_assertion_present    true      <- C1 holds
    authors_found             1
    unanimous                 true      <- C2 holds
    overflow_controls         8
    permalink_anchors         20
    distinct_urns             8
    owner_headings            0         <- C3 has nothing to read

**Two of its three conditions hold and the third had nothing to compare
against.** The census measured 233 controls on the same page in the same
session, so this is not the half-render that produced a wrong answer for
`profile_edit_intro`. The reading is stable and the reader still would not
aim.

### 4b. A hypothesis, a fix, and the fix REFUTING the hypothesis

`innerText` is a RENDERED-text reading and returns `''` for text CSS has taken
out of layout, so the obvious explanation was a heading LinkedIn draws and
hides. That is **a real defect independent of the live page** -- C3 asks
whether LinkedIn's own markup names the owner, which is a question about the
DOCUMENT, and making it depend on CSS was wrong however the page behaved. So a
`textContent` route landed, **with both counts reported**.

**The live page then answered ZERO BY BOTH.**

    owner_headings_rendered   0
    owner_headings_contained  0

**The profile has no `h1` carrying text at all.** Reporting both counts is
what settled that in ONE call rather than leaving it to be argued -- and it is
the whole argument for reporting a measurement's two halves instead of its
verdict.

**THE FIXTURE WAS MEASURED BEFORE IT WAS WRITTEN, and the obvious one is
wrong.** Nine constructions were run through a real Chromium; only three
produce the symptom:

    h1 style="visibility:hidden"          ''            'Owner Name'   REPRODUCES
    h1 > span style="display:none"        ''            'Owner Name'   REPRODUCES
    h1 > span style="visibility:hidden"   ''            'Owner Name'   REPRODUCES
    h1 style="display:none"               'Owner Name'  'Owner Name'   does NOT
    h1 clip/absolute "visually hidden"    'Owner Name'  'Owner Name'   does NOT
    h1 aria-hidden="true"                 'Owner Name'  'Owner Name'   does NOT
    h1 width:0;height:0;overflow:hidden   'Owner Name'  'Owner Name'   does NOT

`display:none` on the element FAILS to reproduce it because the spec makes
`innerText` fall back to `textContent` for an element that is not rendered --
the fallback is the point of that clause. **And the clip-and-absolute recipe,
the standard "visually hidden" pattern and the one LinkedIn is most likely to
use, reads normally.** A fixture written from the obvious assumption would
have tested nothing.

### 4c. The third route, and what it still refuses

`7e7c728` adds `document.title`, consulted LAST -- LinkedIn's markup naming the
page in the same sense `isSelfProfile=true` is LinkedIn's url naming it.
Compared by **containment**, forced by the string rather than chosen: a browser
title carries an unread count in front and `" | LinkedIn"` behind, which no
prefix rule survives. Looser, so `ACTIVITY_MIN_AUTHOR_CHARS` bounds the
degenerate case -- `"In"` is inside `"LinkedIn"` and would otherwise establish
authorship on a coincidence in LinkedIn's own suffix.

**It still refuses, and each of these is a test:** a rail of reshares by one
OTHER member (unanimous, passes C2, not in the title of HIS profile); a title
naming nobody on the rail; TWO headings, which do NOT fall through to the
title, because resolving an ambiguity by changing the question is not
resolving it; and a heading naming somebody else beside a title naming him --
the heading wins, because the routes are an ORDER and not a preference.

**WHETHER IT ANSWERS ON THE LIVE PAGE IS UNMEASURED at the time of writing** --
it needs a second restart. If the title route also answers zero, **#3 stays
unaimable on that ground and I will say so rather than adding a fourth route.**
Three is already the point at which "find something that names the owner"
stops being a measurement and starts being a search.

### 4d. #3's other blocker is untouched and is the operator's

The ON label has still never been seen. The supervised act that would produce
it is his, is described in full in the previous audit (**two** reactions, not
one, because `census_redact_rare` blanks a shape seen exactly once), and **is
not scheduled**. Its consequence, stated precisely: `react_to_item` could be
made MINTABLE without it, and `_verify_after` would then be able to say only
"the OFF label is gone" and never what replaced it.

---

## 5. #2 `comment_on_item` and #4 `update_profile_field` -- **REFUSE**, and
## #4's stated condition was MET

### #4: the fields ARE nameable, measured today

`linkedin_profile_editor_fields` ran live and the lead's condition -- *"only if
a field can be named"* -- **is met**:

    First name*        input  text  label-for  REQUIRED
    Last name*         input  text  label-for  REQUIRED
    Additional name    input  text  label-for
    Industry*          input  text  aria-label
    City               input  text  aria-label
    Country/Region*    input  text  aria-label
    School*            select       label-for  REQUIRED
    Month              select       aria-label
    Save               button       text       enabled

Self-ownership established per call: `isSelfProfile=true` plus the same member
segment on both landed urls. Container `dialog`, anchored on `Save`, 23
controls inside.

**So #4's blocker is no longer "no field can be named". It is two things, and
both are measured:**

1. **IT MUST TYPE.** Same mutation class as #1 and #9.
2. **NOTHING RECORDS THE PREVIOUS VALUE**, so an edit is not revertible by
   this server. A gate that can name a field and cannot restore it is not a
   gate this design opens.

**AND ONE DEFECT FOUND IN THAT INSTRUMENT, FIXED IN `58f69ec`.** The tool
promises **"LABELS, NEVER VALUES"** and it published a VALUE: the headline
control is a `div[role=textbox]` with no aria-label, no label-for and no
title, so its accessible name resolved through the LAST route in the name
chain -- the element's own text. For a contenteditable that text IS the value,
and the answer carried his headline verbatim.

**WHY THREE LAYERS OF GUARD ALL PASSED, and it is the transferable half.**
Each was built against the PROPERTY route: a scan of the injected script for a
value read, the field dict's named keys, and a JSON sweep of the whole answer.
A control whose NAME IS ITS CONTENT is a fourth route none of them covers --
and **no fixture in that suite had a contenteditable in it**, so there was
nothing for any of the three to catch. The JSON sweep in particular could only
ever look for values it had itself planted.

The harm is nil -- his own headline, already public on his profile -- and the
CLAIM was false, which is the class of finding this repository keeps making
about its own docstrings.

**REFUSED IN THE PAGE, not shaped in Python**, for the reason
`INVITE_NEEDLE_JS` does its comparison there: a value that reaches this
process can reach a traceback or a log line. The control now returns
`<content>` with `name_source: "content"` -- a DIFFERENT answer from `none`,
which means no name was found; this one HAS a name and it is withheld.

**GATED ON EDITABLE, NOT ON THE `text` ROUTE**, and the control for that
shipped with it: a `<button>` is named by its own text too, and for a button
that text is a LABEL. Gating the route would have blanked every one of them
and taken the ANCHOR with it, since the container is found by the control
named `Save`. The over-gating mutation fails with `no_anchor`, which is that
exactly.

**THE CENSUS SHARES THAT NAME CHAIN AND WAS DELIBERATELY NOT CHANGED.** Its
contract is SHAPES rather than labels and its gate is ON, so an editable's
content there already meets `census_shape`. Changing it would move published
shapes without keeping a promise that was made.

**AND WHAT IT COSTS IS THE INTERESTING HALF:** a field's current value is
exactly what would make a change REVERTIBLE, which is one of the two things
still blocking #4. Withholding it keeps the promise and leaves that blocker
standing. Returning it would widen this tool's contract -- and this tool
exists BECAUSE the operator ruled one narrow widening, so a second is his.

### #2: the item-key gap and the comment box

The permalink is admitted and the anchors are measured. **It must TYPE**, so
it refuses on the same mutation class regardless of what a permalink capture
would find, and `contenteditable == 0` on both readable surfaces means the
comment box has still never been observed. The permalink capture is pending
the same restart as #3.

---

## 6. #7 `send_invitation` -- **REFUSES**, and I answered the question the lead
## asked

### 6a. THE IDENTITY DOES NOT GO THROUGH `target`. Which, and why

The lead's fork was: close the three hazards, or keep the identity out of
`target`. **Out of `target`**, on three grounds:

1. **THE PROPERTY ALREADY EXISTS AND WOULD BE DESTROYED.** `INVITE_NEEDLE_JS`
   hands the needle INTO the page and returns three integers precisely so no
   name enters Python. `_read_profile_invitations` was deliberately left not
   taking one.
2. **STRUCTURE BEATS HANDLING.** A target reaches `consume()`'s mismatch
   message, `_render`'s block and `grant.preview`. Not routing makes a leak
   IMPOSSIBLE; closing those three sites makes one LESS LIKELY. This repo's
   own words: a name that reaches Python can reach a traceback, an exception
   message, a cache key or an audit line, and no care downstream un-rings it.
3. A digest would have been the alternative binding, and a truncated digest of
   a short human name is not anonymisation against somebody holding a
   candidate list -- worth saying, since it is the design I considered and
   rejected rather than one I did not think of.

### 6b. AND THEN THE BLOCKER THAT IS BIGGER THAN THE PLUMBING

**THE CONFIRM BLOCK CANNOT NAME THE PERSON.** The aiming is safe *because* no
label enters this process, so the block can say "exactly one of nine controls
carries the word you gave, at position 3" and cannot say WHO.

Every other action here names its target in terms he can CHECK -- a job title
and an employer, a company name, his own name and headline. **This package has
already decided that question twice, both times the same way:** `unsave_job`
refused until the label on the control it would press had been photographed,
and `react_to_item` is refused partly because *"a gate that cannot say what it
is about to express under his name is not a gate."* An invitation is a request
to a real person, sent under his name, and it is less recoverable than either.

**The privacy design and the confirmability requirement are in direct
opposition** -- the same tension the census's gate has with #4 -- and here the
container is NOT self-owned: those nine names belong to nine other people.

**WHAT WOULD LIFT IT is now far narrower than the ruling he already gave.**
Not "may this server hold an identity", but: **may it read the accessible name
of THE ONE control his own needle has already uniquely selected, print it in
the block for him to check, and discard it.** One label, chosen by his word
rather than by this server, never stored and never returned to a caller. That
is the exact shape of the self-owned-container relaxation, one door along, and
it is his.

### 6c. The hazard that WAS closed, because it stopped being hypothetical

**`_GRANTS` had no sweeper.** The TTL bounded when a grant could be USED, not
how long it was HELD -- written at `mint`, removed only by `consume` or
`discard_all`, no timer, no task, no `atexit`. A minted-but-never-confirmed
grant kept its target in process memory for the life of the process.

**It stopped being theoretical the moment `update_setting` shipped:** a
PREVIEW mints, and previews are the common case while confirmations are the
rare one. Swept on mint and on consume -- paths that already run, because a
timer would be a background task and a background task holding write grants is
exactly what `GRANT_TTL_SECONDS` exists to make impossible.

**The placement in `consume` is a correction rather than a choice.** Sweeping
before the lookup was the obvious spot and it cost something real: an expired
token stopped getting *"this confirm token expired after 120s -- run the
preview again and read it before confirming"* and started getting *"unknown or
already-discarded confirm token"*. Both refuse; only one tells him what to do,
and the difference lands on somebody who has just taken too long over a block
this design asked him to read carefully.

Hazards 1 and 3 (the mismatch message, `_render`'s retention) are **NOT
closed and are NOT live**: no identity-carrying action is grantable, and none
is after this wave. They become preconditions again only if somebody revisits
6a.

---

## 7. #8 `set_open_to_work` -- REFUSES, and it was re-measured today

Today's profile census: `Open to` renders as a **`button` with
`aria_expanded="false"` and NO href**. Its editor is still a modal reached
only by a click on a read path, so it is not navigable, there is no url to
template, and the single click that would first SHOW the editor is also the
first click that could CHANGE it. Unchanged, and now re-measured rather than
inherited.

---

## 8. THE BOUNDARY: what moved, in which direction, and what it cost

| structure | before | after |
|---|---|---|
| `SANCTIONED_MUTATIONS` | 2 | **2** |
| new click call sites | -- | **0** |
| new injected scripts | 7 | **7** |
| `evaluate()` waivers in `dom.py` | 7 | **7** |
| `_ALLOWED_URL_PATTERNS` | n | n + 4, each anchored to one url or one url shape |
| `_FORBIDDEN_URL_SUBSTRINGS` | n | **n - 1** |
| `_FORBIDDEN_SUBSTRING_EXEMPTIONS` | 1 | 2, both exact-url |
| `assert_read_url`'s own code | -- | **BYTE-IDENTICAL** |
| `PERFORMABLE` | 5 | **6** |

**THE FORBIDDEN LIST SHRANK, AND THAT HAS NEVER HAPPENED BEFORE.** It has
grown at every previous re-freeze. `"/feed/update"` was removed to admit ONE
item permalink per call, and it **could not be kept** for a mechanical reason
rather than an appetite: this gate matches SUBSTRINGS and cannot say "the
permalink but nothing beneath it", while the exemption table is keyed on an
EXACT url and the urn varies per call. Neither mechanism can express the
ruling.

**WHAT DID NOT GO WITH IT is asserted rather than argued.**
`test_the_removed_substring_did_not_take_the_family_with_it` puts that
family's destructive members through the real guard and reads back WHICH
substring refused each -- `/edit/`, `/delete` and `action=`, all still there,
all still checked before the allowlist.

**AND THE REMOVAL IS RECORDED RATHER THAN DELETED.** It stays in
`FORBIDDEN_SUBSTRINGS_EVER` and is listed in a new
`FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED`, because a substring quietly
dropped from a roster is indistinguishable from one that was never on it. The
exception list has its own guard: an entry must name a substring the roster
remembers AND one that is really gone.

**`<functions>` DID NOT MOVE, and that is the load-bearing line.** Four
surfaces were admitted and `assert_read_url` is byte-identical: no gate was
taught an exception, no check reordered, no clause relaxed. The whole change
is DATA, which is the only shape of boundary change a reviewer can check by
reading a list.

**The contrast between the two composers is the reason each was handled as it
was:** `/messaging/compose/` is a CONSTANT, so an exact-url exemption holds it
and the substring stays. A url with a variable segment has no such option.

---

## 9. DEFECTS FOUND, and five of them are one shape

### 9a. THE ENUMERATE-AND-DROP CLASS -- five instances, now guarded as a class

| where | what was dropped |
|---|---|
| census reader -> `census_aggregate` | `container`, on the day it was added (previous wave) |
| the published census row itself | **built by INDEX**, so inserting a field RENAMED every column after it |
| `_read_dark_mode`'s row projection | `role` -- which `dom.aria_role_of` consults FIRST |
| the activity reader -> the tool's block | `owner_source` |
| the same pair, same day, again | `owner_heading_source` |

Three of those five were written **in this wave**, in code whose author had
just documented the defect. **Not one was found by reading; every one was
found by a mutation or a failing pin.**

The mislabel case is the worst of them and it is new: a row built by
subscripting the key stays WELL-FORMED when a field is inserted -- every value
is still a string or a `None` -- while `role` reports what `name_source`
measured. **A silent DROP leaves a hole; a silent MISLABEL leaves output that
looks complete.** The row is now built by zipping `shape.CENSUS_KEY_FIELDS`
against the key, so names and order cannot disagree by construction, and a
mutation reproduces exactly the historical shape.

**And the class is now guarded rather than its fifth instance:**
`test_every_authorship_fact_the_reader_produces_reaches_the_caller` asserts
the SET -- every key the reader emits must reach the tool's block, on the
success path AND on a refusal. A sixth field fails it without anybody adding a
line.

### 9b. A DEFECT THAT WOULD HAVE GONE LIVE WITH THE FIRST COMPOSITE ACTION

`consume()` compared `grant.target` against `str(target)`, **raw**, while
`mint` had stored a value normalised by `_target_for`. For a job id the two
agree because normalising one is a strip. **For a COMPOSITE target they never
can:** `mint` stores `"dark-mode :: Always on"` and the tool layer hands
`consume` a mapping, whose `str()` is its repr. **Every composite action's
token was unredeemable BY CONSTRUCTION** -- not refused for a reason, just
never equal -- and nothing caught it because no composite action could reach
`mint` either.

**And a second one behind it:** `_target_for` was not IDEMPOTENT. `preview`
mints with `observation.target`, which `observe` had already canonicalised, so
`mint` re-normalised its own output and raised. **The first composite action
to get a `url_template` could not be previewed at all.** A normaliser that
rejects its own output is broken; it now accepts the canonical spelling, with
exactly one separator required so the split cannot be ambiguous.

### 9c. TWO CHECKS THAT COULD NOT FAIL, both mine, both caught by mutation

* The owner-route branch chain had a **dead arm** -- the catch-all already did
  the fallback's job, so deleting the fallback changed nothing and the suite
  stayed green. *A check that cannot fail certifies nothing, and neither does
  the code shape that makes it unable to.*
* `test_the_role_is_read_off_the_row_and_never_assumed` exercises
  `dom.aria_role_of` directly, which a hardcoded `role = "radio"` in
  `_live_control` sails straight past -- MEASURED: that mutation left the file
  green. **A unit test of a helper cannot certify that the helper is the thing
  being called.** Fixed by serving the same three controls as CHECKBOXES and
  asserting the selector followed: on a radio fixture, an assumed role and a
  read one are the same string.

### 9d. Three false claims corrected in code

| where | what it claimed | what was true |
|---|---|---|
| `perform`'s verification block | *"a DIFFERENT surface from the one clicked... LinkedIn's own saved list"* | For a setting there IS no second surface. It now says so, and says why a reloaded group is still stronger than a control reporting on itself. |
| the census docstring | *"IT LOADS EXACTLY ONE PAGE"*, and that a census "is not worth a side effect" | `feed_item` loads two, and three surfaces may now cost something. The claim keeps its exception BY NAME, and every costly key returns a `cost` field ON THE ANSWER. |
| `update_setting`'s `reversible_by` | *"NOT this server: unreachable in either direction"* | False of this one page now. Narrowed, not deleted. |

### 9e. The escaping trap, twice more

Seventh and eighth instances, both in the mutation harness rather than in
shipped code, both caught by the harness's own assertion that a replacement
changed something. One was a Python string in a heredoc whose quoting could
not survive; the other was an anchor consumed by an earlier replacement in the
same script. **The rule that caught both is the one already written down: a
replacement that reports "done" without asserting it changed something is the
same defect as a guard that reports zero without asserting it can match.**

---

## 10. THE LEDGER -- performable before, performable after

| # | capability | before | after | why |
|---|---|---|---|---|
| -- | `save_job` | PERFORMS | PERFORMS | -- |
| -- | `unsave_job` | PERFORMS | PERFORMS | -- |
| -- | `follow_company` | PERFORMS | PERFORMS | -- |
| -- | `unfollow_company` | PERFORMS | PERFORMS | -- |
| -- | `apply_job` | PERFORMS | PERFORMS | -- |
| **6** | **`update_setting`** | refuses | **PERFORMS** | surface measured x6, anchor measured, role read not assumed, verified from a reload. **No new permission.** |
| 1 | `publish_post` | refuses | refuses | **MUST TYPE.** Surface and BOTH controls now measured -- two blockers to one. |
| 2 | `comment_on_item` | refuses | refuses | **MUST TYPE.** Permalink admitted; no comment box observed. |
| 3 | `react_to_item` | refuses | refuses | unaimable -- the live profile names its owner in nothing the reader could read. Third route added; **live answer pending a restart**. ON label still the operator's act. |
| 4 | `update_profile_field` | refuses | refuses | **MUST TYPE**, and no previous value is recorded. Fields ARE nameable -- the lead's condition is MET. |
| 5 | endorse a skill | IMPOSSIBLE | IMPOSSIBLE | the control lives only on a third party's profile. Unchanged, and correctly refused on his behalf. |
| 7 | `send_invitation` | refuses | refuses | **the confirm block cannot name the person.** Identity deliberately not routed through `target`. |
| 8 | `set_open_to_work` | refuses | refuses | no href, re-measured today. |
| 9 | `send_message` | refuses | refuses | **MUST TYPE.** Capture refused by the harness; badge NOT spent. |

**ONE OF EIGHT LIFTED. Seven refuse, and every one of them names a measured
blocker rather than a missing ruling.** Four of the seven are blocked by a
mutation class nobody has ruled on -- which no surface admission could ever
have reached, and which is the finding the previous wave's conclusion was
missing.

---

## 11. RECEIPTS

    baseline   fbe2aef   suite 2267 passed, 1 failed (theirs -- since fixed
                         by jobcore-paths at dcf0a68/76667d4/2367b83)
    3b78dd6    feat(writes): update_setting performs -- the first of the eight
                             to get a surface
    0729201    fix(grants): the TTL bounded use, not holding
    7e7c728    fix(activity): the live profile names its owner in the title,
                              and in nothing else
    58f69ec    fix(editor): "LABELS, NEVER VALUES" was false on the one
                            control it mattered on  (+ this audit)
    64e655c    docs(readme): the cannot-do list named four capabilities that
                              ship
    final      suite 2306 passed, 0 failed

    _state/session.json
      sha256(first 32)  f0892e35688868faef6a3525e54b93e4
      bytes             7813
      mtime             2026-08-26 00:41:24
      -- IDENTICAL to the value recorded at the end of each of the two
         previous waves. git status on _state/ is clean.

    confirm_tokens USED           0
    writes performed              0
    third-party profiles loaded   0
    messaging badge spent         NO -- 0 before, 0 immediately before the
                                  composer work, and no messaging surface
                                  was ever opened
    composer opened               ONE, /preload/sharebox/, by NAVIGATION.
                                  No click, no typing, nothing submitted.
    tools refused by the harness  2 (census article_composer,
                                  census messaging_compose) -- recorded,
                                  NOT routed around
    mutations run                 24, every new check shown failing at the
                                  one it catches. TWO of them failed to fail
                                  on the first attempt and both were MY code
                                  rather than my tests -- a dead branch arm,
                                  and a unit test of a helper the mutation
                                  bypassed. Both are in section 9c.

Nothing was pushed.

---

## 11b. WHAT IS STILL PENDING, and it is one restart

Two things were built and could not be run, and both wait on the SAME thing:
the loaded process is at `3b78dd6` and the work is at `64e655c`.

| pending | what it would settle |
|---|---|
| `linkedin_my_activity_items` on the new build | whether `document.title` names the owner LIVE. If it does, #3 becomes AIMABLE for the first time. If it does not, #3 stays unaimable and **I will say so rather than adding a fourth route** -- three is already where "find something that names the owner" stops being a measurement and becomes a search. |
| `linkedin_surface_census("feed_item")` | the permalink's own render: whether ONE reaction control is drawn there rather than the eight a rail draws, and whether a comment box exists on it. It needs the row above to succeed first, since the urn comes from that reader. |

**NEITHER IS BLOCKED BY A DECISION, A MEASUREMENT OR A RULING.** Both are
built, tested and committed, and they are waiting on a client reconnect. That
is worth separating from the seven refusals above, every one of which is
blocked by something real.

Two further captures were requested and **REFUSED BY THE HARNESS**
(`article_composer`, `messaging_compose`); neither was routed around. See
section 3.

---

## 12. THE THREE THINGS WORTH CARRYING PAST THIS REPO

1. **A PERMISSION SCOPED TO A CALL SITE IS NOT A PERMISSION SCOPED TO AN
   ACTION.** One sentence misreading `(path, function, kind)` as "this action
   may not be performed" produced a whole wave's conclusion that zero of seven
   capabilities could be lifted by anything reachable. Four of them were
   blocked by something else entirely, and three were one measured surface
   away.

2. **REPORT A MEASUREMENT'S TWO HALVES, NOT ITS VERDICT.** The activity
   reader was given a second route on a hypothesis, and made to report BOTH
   counts. The next live call refuted the hypothesis in one call. Had it
   reported only "the owner was not found", the wrong explanation would have
   survived and a third route would have been built on it.

3. **A UNIT TEST OF A HELPER CANNOT CERTIFY THAT THE HELPER IS CALLED.**
   Hardcoding the value the helper returns left the whole file green, because
   every fixture was one where the hardcoded answer was correct. The check
   that can fail is the one where the assumption is WRONG -- which had to be
   built, not found.


---

# PART TWO: the rulings that arrived after the first close

Four more rulings landed and one live apply was performed. This part records
what each bought. **Still no `confirm_token` used, no write performed by me,
`_state/` byte-identical.**

---

## 13. `apply_job` -- TWO DEFECTS, FOUND BY FIRING IT ONCE

The operator authorised his first apply; the lead performed it. **IT DID NOT
SUBMIT.** The gate held, on an irreversible action, on a real posting with a
real employer at the other end. Neither fix makes it more permissive.

### 13a. DEFECT 1 was not a wrong string. It was a check that could not pass

The verification read `/jobs-tracker/?stage=saved`. `apply_job`'s `to_state`
is `"applied"` and `_read_saved_state` returns `saved` / `not_saved` /
`unknown`, so **`verified_state == "applied"` was FALSE on every reading it
could ever take.** Every apply this server can perform was going to report
`performed: "unknown"`.

**AND NOTHING CAUGHT IT BECAUSE NOTHING ASSERTED THE SURFACE** -- changing it
broke no existing test. That absence is what let it ship, and it is now
asserted both ways: the Applied tab is visited and the Saved tab is not.

It reads `?stage=applied` through the **same reconciliation** rather than a
second copy -- `_TrackerStage` describes a tab, `_read_saved_state` is now a
thin wrapper. Two copies of "absence from a partial list is not absence" are
two things that can drift, and that rule matters MORE here: reporting an
unreconciled absence would tell him an irreversible act did not happen when
the row is merely below the fold.

**AND "IT DID NOT HAPPEN" IS NOW `False`, NOT `"unknown"`.** `perform` decided
between them against `from_state`, which works for a TOGGLE -- one that did
not move is still in the state it was valid from. Apply is not a toggle:
`from_state` is `"linkedin_apply"`, a claim about which ROUTE the control
takes, which a tracker read establishes nothing about. `WriteSpec.not_performed_state`
names the state that means it did not happen. `"unknown"` on this action is
the one answer a caller cannot resolve by retrying, because the docstring
forbids the retry.

### 13b. DEFECT 2 was not a missing reason. It was an unread one

`_apply_submit_gate` produces a specific sentence for whichever of its five
conditions refused. **`perform` assigned that dict to a local and never read
it again.** Same shape as three defects this repo has already fixed --
`save_job`'s refusal that would not say what it saw, `_read_tracker`
discarding its own counts, `parse_job_card`'s two indistinguishable `None`s.

The result carries `submit_gate` now: the condition as a **code** as well as
prose, and the reading behind it -- modal present, submit present and enabled,
its name, advance controls found, whether that scan COMPLETED, and the limit.
An unfinished scan is why "no advance controls" can mean UNKNOWN rather than
none. Condition 5 has two codes because it has two ways of failing.

It also says what it is **not**: one reading of a modal is not evidence a
posting cannot be applied to.

Six mutations, each shown failing. The first reproduces the live block
exactly: `expected_state "applied"`, `observed_state "unknown"`, `read_from
?stage=saved`.

---

## 14. #7 -- THE NEEDLE HAD NEVER RUN, AND NOW THE GATE CAN NAME WHO

### 14a. A mechanism that was never reachable

**`aim_invitation` had NO CALLER in `linkedin_server/`.** Only tests called
it. `observe` handed its surface readers no target, so
`_read_profile_invitations` counted controls and never saw a needle -- the
aiming this entire capability is built around had never run against a page.

Same shape as `_direction`'s multi-state branch, hardened in August against a
`KeyError` nothing could reach. **A mechanism can be built, tested, audited
and argued about at length while being unreachable from production, and the
only thing that shows it is following the value.**

### 14b. The label, ruled and implemented

The blocker this refusal carried was that the block could say a COUNT and a
POSITION and not WHO. The operator ruled that ONE label may be read -- the
control his own needle uniquely selected -- printed for him, discarded.

**The distinction the ruling turned on, now recorded in the code:** loading a
stranger's PROFILE stays refused because it EMITS, and `who_viewed_me` reads
the receiving end of exactly that signal. Reading one accessible name off a
page already rendered on HIS OWN profile notifies nobody and creates no
record. And he already knows the name -- he typed the needle -- so this
CONFIRMS his input rather than collecting somebody's identity.

**THREE GATES IN TWO LANGUAGES**, so no single edit opens them all: the script
requires the caller to have asked AND exactly one match; Python re-checks.

**THE PYTHON GATE COULD NOT FAIL** when first written -- measured, by the
mutation that deletes it, which left the suite green because the script's gate
meant no two-match reading ever carried a label. Rather than delete it, it is
now reached by simulating a script that stopped gating, which is what defence
in depth is for.

**IT REACHES THE BLOCK AND NOTHING ELSE, BY ORDER RATHER THAN BY SCRUBBING.**
The block is stored on the grant BEFORE the label exists and added to a NEW
dict after, so the retained object provably never held it. The reader feeding
the Observation does not read a label at all, because an Observation is
retained on a grant. The target stays HIS OWN NEEDLE.

**And the settle precondition here is on the RAIL, not the url.** The first
draft compared landed urls; a page can re-render at the same address, and what
matters is whether the control the name is read off is the control the aim was
taken on. It was also untestable through a fixture harness -- which is its own
argument that it checked the wrong thing.

### 14c. #7 still refuses, on a narrower and newly measured ground

**NOTHING CAN CONFIRM THE SEND.** No post-click state of that control has ever
been observed -- the identical gap `react_to_item` has for its ON label and
`unsave_job` had until 2026-08-30 -- and the sent-invitations manager is on the
forbidden list AND would consume the pending-invitation badge to read.

So a performed invitation could only ever report `"unknown"`. **That is the
shape just fixed in `apply_job`, and it will not ship again on an irreversible
act.** A higher bar than `follow_company` clears, deliberately: a follow is
reversible and observable by him; an invitation is a request to a real person
that LinkedIn will not let him take back and that counts against the account
if it is ignored.

**WHAT WOULD LIFT IT** is the `unsave_job` template: one invitation he sends
himself, then a read-only re-measurement. Nothing here will do that for him.

---

## 15. THE SETTLE FAILURE HAPPENED AGAIN, TO ME, HOURS AFTER I WROTE THE RULE

This is the most useful thing in Part Two.

### 15a. What happened

    BEFORE the composer captures -- four readings, 2026-08-31
      /in/me/ census      232 and 233 controls, source_url carries
                          ?isSelfProfile=true
      activity reader     C1 established, 8 overflow controls, 20 permalinks
      editor fields       self-ownership established, 23 controls in dialog

    TWO post-composer loads

    AFTER -- seven readings
      /in/me/ census      67 controls, TWICE, byte-identical.
                          source_url still /in/me/. NO REDIRECT.
      activity reader     no_self_assertion, five consecutive calls
      editor fields       no_self_assertion

**67 CONTROLS IS THE DOCUMENTED HALF-RENDER SIGNATURE**, and it is the same
number `profile_edit_intro` produced when it was read mid-flight. The
`isSelfProfile=true` the two self-owned readers require was absent **because
the redirect had not resolved** -- so both readers refused correctly, read
nothing, and the design worked.

**AND THE ONLY REASON IT WAS CAUGHT IS THAT I HAPPENED TO REMEMBER 233.** The
census reported 67 twice with no signal of any kind.

### 15b. What is measured, and what is not

**MEASURED:** the readings above, in that order.

**NOT MEASURED: causation.** A clean before/after with a single intervening
event is not a controlled test, and I am not claiming the composer load broke
the profile read. What it is, precisely: **the operator asked what the
composer capture left behind, and the honest answer includes this** -- not a
draft, but a correlated change in this server's ability to read his profile,
which I would not have seen had I not re-read afterwards.

### 15c. So the rule became an instrument

Every census answer now carries a `settle` block comparing what it read
against what the surface is MEASURED to draw. Three verdicts: `consistent`,
`looks_half_rendered`, and `unknown` for a surface nobody has read twice --
which is the ABSENCE of a check rather than one passing.

**IT DOES NOT REFUSE.** A census is a measurement instrument and a
half-rendered page is a true reading of something; what it must never do is
let that pass as a reading of the whole page.

**THE FLOOR IS CHOSEN AGAINST THE DATA.** Both observed half-renders came in
at roughly a QUARTER of the settled count -- 67 of 233, 67 of 255 -- while
honest variation between settled readings is a few per cent: 232 vs 233, 255
vs 256, 277 vs 287 vs 297. An order of magnitude apart, and the test asserts
THE GAP rather than the constant.

**AND THE REPORT SAYS REPEATING IT WILL NOT HELP.** The instinct on a suspect
reading is to take another one. Both observed instances were TWO AGREEING
READINGS.

---

## 16. `publish_post` -- NOT BUILT, AND THE REASON IS 15

The typing ruling removes its mutation-class blocker, and its capture was
already taken -- so it was the one capability that could have lifted on that
ruling alone. **It was not built, and the decision is measured rather than
cautious.**

**THE SETTLE PRECONDITION WAS APPLIED FIRST, as instructed, and the composer
passed it.** Two readings, identical on every count: 31 controls, `forms 0`,
`buttons 20`, `links 7`, `contenteditable 2`, `dialogs 1`, no redirect. `Text
editor for creating content` count 1 and `Post` count 1, both in `dialog#0`,
`Post` disabled on an empty composer. That surface is settled.

**WHAT IS NOT SETTLED IS THE VERIFICATION.** The only surface that could
confirm a post exists is his own activity rail -- and section 15 is that
surface failing to render, five readings running, immediately after the
composer loads this capability would perform. To ship it I would have to
assert that a new post appears on that rail, which **nobody has measured**,
using an instrument that is currently returning nothing.

**THAT IS THE EXACT DEFECT FIXED IN `apply_job` THIS MORNING** -- a
verification that could not pass, shipped because nothing had asserted its
surface. Shipping a second one hours later, on the most public action in the
design, on a BROADCAST that reaches up to 1,287 impressions and whose deletion
is unmeasured, would be the same mistake with a better excuse.

**AND THE MUTATION CLASS WAS NOT ADDED EITHER.** `fill` in
`SANCTIONED_MUTATIONS` with no call site is a permission with no consumer,
which is the shape the lead's own withdrawn ruling condemns. The ruling stands
and is unspent; it costs nothing to leave it so.

`SANCTIONED_MUTATIONS` is **unchanged across this entire wave** -- the two
entries it has held since 2026-08-26.

---

## 17. THE LEDGER, PART TWO

| # | capability | after Part One | after Part Two |
|---|---|---|---|
| -- | `apply_job` | PERFORMS, verified against the wrong tab | **PERFORMS, and can now say what happened and why it stopped** |
| 6 | `update_setting` | PERFORMS | PERFORMS |
| 1 | `publish_post` | refuses -- must type | refuses. Mutation class RULED IN; **verification unmeasured**, and its surface is currently unreadable |
| 2 | `comment_on_item` | refuses -- must type | refuses. Mutation class ruled in; no comment box observed, no capture taken |
| 3 | `react_to_item` | refuses -- unaimable | refuses. Third owner route committed, **live verdict still pending a reconnect** |
| 4 | `update_profile_field` | refuses | refuses. Fields nameable; **no previous value**, which the ruling explicitly does not lift |
| 5 | endorse | IMPOSSIBLE | IMPOSSIBLE |
| 7 | `send_invitation` | refuses -- cannot name who | **refuses -- cannot confirm the send.** The naming blocker is CLOSED and the aiming now runs |
| 8 | `set_open_to_work` | refuses | refuses |
| 9 | `send_message` | refuses -- must type | refuses. Mutation class ruled in; capture refused by the harness; InMail balance ruled readable and not yet read |

**ONE OF EIGHT PERFORMS, and `apply_job` -- which already performed -- can now
report honestly.** Every refusal names a measured blocker.

---

## 18. WHAT I DID NOT REACH, named rather than left

| not reached | why |
|---|---|
| `feed_item` capture, #3's live verdict | the loaded process never advanced past `3b78dd6`; five commits behind at close |
| `article_composer`, `messaging_compose` captures | REFUSED BY THE HARNESS classifier, not routed around |
| the InMail balance | `/premium/my-premium/` is ruled admitted; the boundary entry and reader are NOT built, because #9 cannot lift regardless and a widening with nothing to consume it is the shape the lead's own withdrawn ruling condemns |
| phase 2, all four items | not started. The slug/id gap, `set_open_to_work`'s `Show details` click, the profile-editor enumeration and the settings-section enumeration are all untouched |
| withdrawing an application | blocked on an EVENT rather than a measurement -- the Applied tab reads zero |

---

## 19. RECEIPTS, PART TWO

    eaf7f66  fix(apply)       the wrong tab, and a gate that named none
    82313a8  feat(invitation) the needle reaches a page; the gate names who
    2ad2ad8  feat(census)     the settle precondition, as an instrument

    suite            2306 -> 2340 passed, 0 failed
    mutations run    24 -> 41, every new check shown failing
    checks that could NOT fail, found and fixed   3
                     (a dead branch arm; a unit test the mutation bypassed;
                      the Python half of the label gate)

    _state/session.json  f0892e35688868faef6a3525e54b93e4, 7813 bytes,
                         mtime 2026-08-26 -- UNCHANGED
    SANCTIONED_MUTATIONS 2, unchanged all wave
    confirm_tokens used  0
    writes performed by me   0

Nothing was pushed.


---

# PART THREE: the four captures

The operator granted the two captures the harness had refused -- **surfaced to
him as a permission decision rather than routed around** -- and a genuinely
fresh reconnect (pid 8748, `82313a8`) made the fourth reachable. All four
taken. **Badge 0 before and 0 after. Nothing of anybody's was spent.**

## 20. What each capture settled

| capture | landed | the finding |
|---|---|---|
| `feed_item` | `/feed/update/<urn>/`, **no redirect** | ONE reaction control and ONE comment affordance, where the feed and profile draw eight. **`contenteditable: 1` and `Text editor for creating comment` NAMED** -- every previous census of every readable surface reported zero. |
| `post_composer` | `/preload/sharebox/`, no redirect, **twice identical** | `contenteditable: 2`, `Text editor for creating content` and `Post` (DISABLED while empty), both in `dialog#0`. |
| `article_composer` | `/article/new/`, no redirect | Editor and `Title` named; **the publish control comes back `<redacted>`** -- blanked as a singleton. **This route is WORSE measured than the sharebox one.** Two routes was never a requirement. |
| `messaging_compose` | `/messaging/compose/`, **NO REDIRECT** | **The cost this refusal was built around does not exist.** It stayed at the composer, 77 controls, ZERO dialogs, opened nobody's thread -- the opposite of `/messaging/`, measured twice to redirect into a conversation. Controls named; `Send` disabled while empty. |

**AND THE INMAIL BALANCE IS NOT ON THE COMPOSER.** The control named `InMail`
is a conversation-list FILTER PILL carrying `aria-checked=false`, beside
`Focused`, `Unread`, `Starred` and `Connections`. A balance needs
`/premium/my-premium/`, which is admitted and unread.

## 21. WHAT THE COMPOSERS LEFT BEHIND -- in the two sentences, uncollapsed

**WHAT I COULD SEE:** his activity rail was 8 items / 20 permalinks before and
after; `Post impressions` moved 61 to 62, which is analytics drift and not a
post; the messaging badge read 0 before and 0 after; and the messaging
composer did not redirect, so no thread was opened.

**WHAT I COULD NOT SEE:** whether any composer saved a DRAFT. 17 of 17
candidate draft-listing addresses are refused by this module's own read
boundary, so there is no reachable surface on which one could be detected or
removed. **"Nothing appears to have been left" is a statement about my
instruments, not about what happened.**

## 22. A CORRECTION TO PART TWO, AND IT IS MINE

Part Two reported the profile going dark after the composer loads, and my
message to the lead called it a "reproduced correlation" after it recurred
following the second batch of composer loads.

**ONE READING LATER IT DID NOT REPRODUCE.** The profile came back at 233
controls with `?isSelfProfile=true` present, same session, no restart.

So the honest finding is **simpler and weaker than the one I reported**:
`/in/me/` renders INTERMITTENTLY -- sometimes 233 controls with LinkedIn's
self-assertion, sometimes 67 with no redirect at all -- and the two
self-owned readers refuse correctly on the bad ones. The clustering after
composer loads is not established, and I am withdrawing that claim rather
than leaving it to be believed.

**It does not weaken the instrument built for it.** The settle report flags a
bad reading without needing a causal story, which is exactly why reporting the
comparison beats reporting a theory.

## 23. THE LEDGER AFTER THE CAPTURES

| # | blocker before | blocker after |
|---|---|---|
| 1 `publish_post` | no surface, no control | **must TYPE**, and its only verification surface renders intermittently |
| 2 `comment_on_item` | no surface, no control, unaimable | **must TYPE.** All three closed. |
| 3 `react_to_item` | unaimable, no permalink, ON label, which reaction | **which reaction it applies, and the ON label.** Two closed, both remaining are one supervised act of his. |
| 9 `send_message` | surface forbidden, cost unknown | **must TYPE**, and the balance unread. The redirect cost turned out not to exist. |

**THREE OF THE FOUR NOW REFUSE ON ONE MEASURED THING: typing is not a
sanctioned mutation anywhere in this package.** That is the finding Part One
opened with, arriving where it was predicted to.

## 24. RECEIPTS, PART THREE

    117a5a9  docs(refusals)  four captures land, three blockers close

    suite                 2340 passed, 0 failed
    badge before / after  0 / 0
    threads opened        0 -- /messaging/compose/ does not redirect
    SANCTIONED_MUTATIONS  2, unchanged all wave
    confirm_tokens used   0
    writes performed      0

Nothing was pushed.
