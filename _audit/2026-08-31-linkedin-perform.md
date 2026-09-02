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
| 2 `comment_on_item` | no surface, no control, unaimable | **must TYPE**, and -- found on 2026-09-01, after this line was written -- **no comment total exists to verify against.** Three closed, a FOURTH found. See Part Four. |
| 3 `react_to_item` | unaimable, no permalink, ON label, which reaction | **which reaction it applies, and the ON label.** Two closed, both remaining are one supervised act of his. |
| 9 `send_message` | surface forbidden, cost unknown | **must TYPE**, and the balance unread. The redirect cost turned out not to exist. |

**THREE OF THE FOUR NOW REFUSE ON ONE MEASURED THING: typing is not a
sanctioned mutation anywhere in this package.** That is the finding Part One
opened with, arriving where it was predicted to.

> **AMENDED 2026-09-01, and the amendment matters more than the sentence it
> qualifies.** Typing turned out NOT to be the last blocker for any of the
> three. Each also lacks a surface that could verify what it did, and that was
> established only by going to look -- the `comment_on_item` row above says
> "All three closed" because the count had not been checked yet. Had the
> typing ruling been spent on the strength of this section, the result would
> have been three writes that could only ever report `unknown`. Part Four
> carries the measurements.

## 24. RECEIPTS, PART THREE

    117a5a9  docs(refusals)  four captures land, three blockers close

    suite                 2340 passed, 0 failed
    badge before / after  0 / 0
    threads opened        0 -- /messaging/compose/ does not redirect
    SANCTIONED_MUTATIONS  2, unchanged all wave
    confirm_tokens used   0
    writes performed      0

Nothing was pushed.

---

# PART FOUR -- THE CLOSE (2026-09-01)

## 25. THE BUILD STAMP, FIRST, AS ALWAYS

    build.code.commit      c2090d373027   == git rev-parse HEAD
    build.code.dirty       false
    process.pid            19840
    process.started_at     2026-09-01T03:04:41Z  (08:34:41 IST)

The process is younger than the commit it reports, so the capture below was
taken against the code on disk. This is the second consecutive reconnect where
that held; of the four announced before it, three did not.

## 26. `feed_item_commented` -- THE CAPTURE THAT SETTLED THE QUESTION

One call, two page loads: the activity rail to resolve an item, then the item.

    surface        feed_item_commented
    source_url     /feed/update/urn:li:activity:<id>/   (redacted here --
                   test_no_committed_identity caught the raw id in this
                   very file, on a public repo under his real name)
    rule           most_anchors (8 items available, 4 anchors on the chosen one)
    controls_read  91
    forms 1   buttons 43   links 44   contenteditable 1   dialogs 2
    authorship     established -- isSelfProfile=true, one author string,
                   unanimous, owner_source=document-title

### Two of the three blockers are gone, and that is worth stating before the refusal

**The target opens.** The permalink loaded under the boundary ruling, no
redirect. Until 2026-08-31 `/feed/update` was on `_FORBIDDEN_URL_SUBSTRINGS`.

**The comment box exists and is now measured.** `contenteditable: 1` -- a
`div[role=textbox]` whose aria-label is `Text editor for creating comment`,
beside a text-named `Comment` button. The feed census of 2026-08-30 read
**0 contenteditable across 286 controls**, and that zero was the whole of the
"no control" half of this refusal for as long as it existed. This is the first
comment editor ever observed on this account.

### What stops it is the third thing, and it is measured rather than argued

**There is no comment total on the page.** The complete numeric inventory of
all 91 controls:

| shape | tag | count | what it is |
|---|---|---|---|
| `0` | `div[role=button]` | 4 | one per rendered comment row, paired 1:1 with four `Reply` buttons -- per-comment, not a post total |
| `33 reactions 33` | `a` -> `/feed/update/<urn>/` | 1 | the reactions total |
| `1,287 impressions ... analytics` | `a` | 1 | this post's analytics link |
| `Post impressions 58` | `a` | 1 | the Me-panel sidebar, a different post |
| `Profile viewers 31` | `a` | 1 | the Me-panel sidebar |
| `..., N new notification(s)` | `a` / `button` | 5 | nav badges |

Nothing counts comments.

### The instrument has its own control on that same reading

This is why the absence is a fact about the page and not about my reader.
`33 reactions 33` is lowercase, numeric and seen **exactly once** -- precisely
the shape `shape.census_redact_rare` blanks when it blanks anything -- and it
came through **intact**. A comment total of the form `2 comments` would have
survived the same pipeline for the same reason. The control was in the reading
itself; it did not have to be assumed.

### The fallback fails on the same capture

The tempting substitute is to count rendered comment controls: four `Reply`
buttons become five. That is not a total, and the page says so. The comment
list sits under a **`Most relevant`** control (`div[role=button]`,
`aria-expanded=false`), so the list is relevance-ordered, and the census reads
first render without scrolling. A comment posted seconds ago with no
engagement has no guaranteed place in a relevance-ordered first page. Counting
what rendered would be sampling a sorted, paginated list and calling it a
count.

### Holding the prediction

The expectation was on the record before the page was opened: **count
plausible, attribution expected to FAIL.** Half right, and the optimistic half
is the half that was wrong -- the count is not plausible, it is absent, and
attribution never got its turn because there is no total to attribute. No
comment appeared during this reading, so the upgrade-a-count-into-an-
attribution temptation was never available to resist; that is reported rather
than claimed as restraint.

## 27. THE RULING

**`comment_on_item` REFUSES ON VERIFICATION.** Not on target, not on anchor --
both were closed by this wave. On verification alone.

By the rule accepted before the capture was taken:

| action | verification surface | verdict |
|---|---|---|
| `publish_post` | the activity rail, measured at 233 controls once and 67 another time in the same session | **REFUSES** -- a check that answers nothing on some readings |
| `send_message` | none. No countable total on the composer, none on `/premium/my-premium/` | **REFUSES** -- could only ever report `unknown` |
| `comment_on_item` | none. No comment total among 91 controls | **REFUSES** |

**None of the three ships. The typing ruling stays unspent.**
`readonly.SANCTIONED_MUTATIONS` ends this wave at **2 entries**, exactly where
it started. No `fill` entry was landed, standalone or with a call site.

> **OVERTAKEN THE SAME DAY, 2026-09-01, and left standing because the reasoning
> is what changed rather than the measurements.** The operator lifted the
> VERIFICATION STANDARD within the hour of this being written: an unverifiable
> outcome became a shippable outcome provided the gate says so. Every
> measurement above survives that ruling intact -- there is still no comment
> total, the rail still renders intermittently, the composer still carries no
> countable balance. What changed is that those findings became the
> DISCLOSURE the gate prints instead of the reason it refuses.
>
> All three ship now, and `SANCTIONED_MUTATIONS` ends the day at **3**. See
> Part Five. Note what did NOT move: `send_message` still refuses, because its
> recipient control was never measured -- and a ruling cannot photograph a
> control.

The server still cannot type. What changed is that all three refusals now name
a measured ground instead of an inherited assumption.

## 28. THE BALANCE, IN ITS NARROW FORM

**There is no countable InMail balance on either surface this server MAY
READ.** That sentence is deliberately narrower than the one it is tempting to
write, and the narrowness is the finding.

* **The messaging composer** carries no balance. The control named `InMail` on
  that surface is a FILTER PILL, sibling to `Focused`, `Unread`, `Starred` and
  `Connections`.
* **`/premium/my-premium/`** was read twice, and the two readings **disagree**:
  **73 controls today, 80 on 2026-08-31.** So this surface has no settled
  count and neither reading is a measurement of the whole page. What survives
  both readings is that no control on either carried a credit balance. The
  numeric shapes present today are marketing offers (`Redeem 3 months free`,
  `Claim 1 year free`, `Redeem 4 months free`, `Redeem 3 months on us`),
  carousel pagination (`Page 1..3`, `Next`) and nav badges.

**The unadmitted addresses that could still hold it**, named rather than
gestured at, all measured on today's reading and none on the read allowlist:

| address | links to it | reached from |
|---|---|---|
| `/premium/sb/explore/` | 9 | `See all features`, `Get hired faster`, `Work smarter`, `Network like a pro`, `Enhance profile` |
| `/premium/premium-perks/` | 5 | the four redeem/claim offers |
| `/premium/switcher/` | 1 | `Change plan` |
| `<opaque>` href | 2 | `Manage subscription`, `Edit payment method` |

An earlier note to the lead said "two unadmitted links"; today's reading
enumerates four distinct destinations, so the earlier count is corrected here
rather than repeated. **None of them was opened** -- each would need its own
ruling, and there is nothing to consume the answer while `send_message`
refuses for a separate reason.

## 29. THE THIRTEEN-ROW LEDGER

`writes.SANCTIONED_WRITES` holds thirteen actions. Twelve have a registered
tool; `set_open_to_work` has none.

| # | action | state | the ground, as measured |
|---|---|---|---|
| 1 | `save_job` | **PERFORMS** | anchor `Save the job`, verified against the Saved tab |
| 2 | `unsave_job` | **PERFORMS** | anchor measured 2026-08-30 across two independent routes; refuses from any state it does not recognise |
| 3 | `follow_company` | **PERFORMS** | verified by re-reading the followed list |
| 4 | `unfollow_company` | **PERFORMS** | addressed by NUMERIC id; refuses when the Page is not among the rendered rows |
| 5 | `apply_job` | **PERFORMS**, irreversible | two defects fixed this wave: verification pointed at the Saved tab and now reads the Applied tab; the five-condition submit gate named none of its conditions and now returns a `refused_condition` code |
| 6 | `update_setting` | **PERFORMS** (new this wave) | dark mode is a three-state radio group read off `/mypreferences/d/dark-mode`; role read via `dom.aria_role_of`, refused if not a known input role; verified by reload and re-read |
| 7 | `publish_post` | refuses | surface and anchor MEASURED (`/preload/sharebox/`, contenteditable==2, control `Post`). Stops on TYPING and on a verification surface that renders intermittently |
| 8 | `comment_on_item` | refuses | surface and anchor MEASURED (permalink, contenteditable==1, `Text editor for creating comment`). Stops on TYPING and on **no comment total among 91 controls** |
| 9 | `react_to_item` | refuses | OFF anchor measured on three surfaces; permalink readable; post toggle unique. Stops on which reaction the toggle applies, and on the ON label never having been seen |
| 10 | `send_invitation` | refuses | nine controls on his own profile, costing no badge. Stops because the label IS the other person's name, which this server will not read, so the suffix selects all nine. `/invite`, `invitation`, `/connect` are on the forbidden list |
| 11 | `send_message` | refuses | composer OBSERVED under an exact-url exemption. Stops on TYPING and on nothing being able to verify a send |
| 12 | `update_profile_field` | refuses | `/edit/` is on the forbidden list (verified against the live tuple). No field inside any editor has been observed |
| 13 | `set_open_to_work` | refuses, **and has no tool** | 237 urls and 37 payload paths across five profile captures reach no audience editor; it opens as a modal, and the first click that would show it is the first that could change it |

Rows 7-12 are the six refusals a caller can reach through a tool. Row 13 is
refused inside `_refuse_unperformable` with no tool registered, which is why
thirteen actions present as twelve write-shaped tools.

## 30. THREE DRIFTS FOUND WHILE CLOSING, AND THE GUARD THAT NOW CATCHES THEM

None of these was the wave's subject. All three were found by reading what the
server tells a caller, immediately after measuring what the server does.

**One. `linkedin_server_info` carried a SECOND refusal table
(`server._WHY_NOT_PERFORMED`) that was stale against the boundary work.** It
told callers that `/feed/update/<urn>/` was forbidden -- removed 2026-08-31,
the first removal this package has ever made -- that `/article/new/` and
`/preload/sharebox/` were not on the allowlist (both added), and that no
messaging composer had ever been observed (one had). The comment above that
table shows the earlier mitigation: keep the duplicate to one line each *"and
two long copies of one argument drift apart"*. **Shortening a duplicate does
not stop it duplicating.** Five entries rewritten.

**Two. The module docstring claimed its own numbers were checked, and nothing
checked them.** It read *"THE NUMBERS ABOVE ARE DERIVED, not counted by
hand"*, named two pins, and both pins were real -- one pinned `len(tools)` to
the literal 33, the other pinned the INSTRUCTIONS string. Neither read the
docstring. So when `update_setting` shipped on 2026-08-31 the instructions
correctly said SIX and the docstring went on saying FIVE for a day and a half,
under a sentence asserting it could not. Seventh rot of that paragraph; the
first six were counted in it already.

**Three. The census parameter description named the wrong set.** It said *"one
of these five"* while eight keys existed, was corrected to a NINE that listed
`feed_item` while omitting `feed_item_commented` and `premium`. **The count was
right and the membership was wrong**, which is the version nobody catches: a
reader counting nine names against a stated nine finds nothing to doubt.

### The guard, and the eight mutations it was shown failing at

New file `tests/test_prose_that_makes_a_claim.py`, five tests. Every one was
shown RED at a mutation before being accepted, and each failure names its
cause rather than printing two integers:

| mutation | caught by | the failure it prints |
|---|---|---|
| `headline-count-rots-by-one` | docstring numbers | `the headline says five write, writes.PERFORMABLE has 6` |
| `split-restates-the-pre-update_setting-shape` | docstring numbers | `docstring says FIVE write, writes.PERFORMABLE has 6` |
| `sum-adds-up-and-disagrees-with-the-registry` | docstring numbers | `the sum sentence adds up and disagrees with the registry` |
| `toolless-action-drops-out-of-the-prose` | toolless action | names `set_open_to_work` |
| `census-lists-the-wrong-eleven` | census enumeration | `answered to but not named: ['premium']` |
| `census-count-and-membership-disagree` | census enumeration | `the description says 'ten' and the instrument answers to 11` |
| `refusal-inherits-a-boundary-that-moved` | forbidden-path guard | names `/feed/update/` and the sentence |
| `collector-skips-the-inline-refusal` | corpus guard | `missing: ['set_open_to_work']` |

Two of those mutations found real weaknesses in the checks themselves, which
is the point of running them:

* **`census-lists-the-wrong-eleven` initially passed.** Swapping `premium` out
  of the enumeration left the test green, because a sentence added *in the
  same commit as the test* names `"premium"` in prose. Searching the whole
  paragraph tests whether a word appears somewhere; the check now scopes to
  the enumeration clause and compares the quoted set against
  `census_surface_keys()` in both directions.
* **The corpus guard exists because a loop over nothing passes.** The
  forbidden-path check iterates refusal texts; had the collector returned an
  empty dict it would have been green forever. The collector reaches refusals
  by CALLING `_refuse_unperformable`, not by reading `_NINE_REFUSALS`, so
  `set_open_to_work` -- which has no table entry -- is covered like the rest.
  A guard that read only the table would be blind to exactly the entry the
  table forgot.

### One more correction the capture forced

`react_to_item`'s refusal stated that `Open reactions menu` had **count 1 on
the permalink**. Today's permalink drew **five**, because every rendered
comment carries its own reaction menu. The earlier number came from a reading
that used the `first` rule and landed on an item with no comments. The post's
own toggle is still unique on both readings (`Reaction button state: no
reaction`, count 1), so the aim survives -- but reading a property off one item
and calling it a property of the surface is the same error as inheriting a
refusal from a neighbouring address, and the entry now says so.

## 31. FOUR FINDINGS THAT OUTLIVE THIS WORK

Carried verbatim, because each is shorter than the incident that produced it
and would lose its edge in paraphrase.

> *A refusal inherited from a neighbouring address is not a measurement of
> that address.*

`/messaging/compose/` was refused for as long as this server has existed, on
`/messaging/`'s behaviour, and neither the original author nor the wave lead
checked. The same shape then repeated inside this wave: three refusal texts
kept citing `/feed/update` as forbidden for a day and a half after it was
deliberately admitted. A refusal is the text nobody re-reads, which is exactly
why it rots without being noticed.

> *Typing without a verification surface reproduces the defect apply carried
> for months.*

A write that can only ever report `"unknown"`. `apply_job` compared its
`to_state` against a reader that could never return it. All three typing
candidates in this wave were tested against this rule before any mutation was
sanctioned, and all three failed it. The rule is what kept the ruling unspent.

> *A reading taken while the thing is still moving is not a measurement of it.*

One finding, two instruments. On the page: `settle`, born after
`profile_edit_intro` was read TWICE at 67 controls and twice at 256 -- two
agreeing readings, both of a page that had not arrived. On the repository:
`git status`, after three suite runs against a moving tree and a push gated on
one of them. `/premium/my-premium/` in this very close is a live instance --
73 controls today against 80 on 2026-08-31, so neither reading is settled and
the finding drawn from them had to be narrowed to what both agree on.

> *A check that could not pass is indistinguishable from one that has not
> passed yet.*

`apply_job`'s `to_state` was compared against a reader that could never return
it, and nothing caught it because nothing asserted the surface. The twin,
found while closing, is worse: a CLAIM of being checked is worth less than
nothing, because it is the thing that stops somebody checking. `server.py` said
its numbers were derived, and that sentence was the reason nobody derived them.

## 32. RECEIPTS, PART FOUR

    suite                      see the run recorded with the commit
    captures taken             2 -- feed_item_commented, premium (re-read)
    page loads                 3
    badge before / after       unchanged; no notification or mynetwork load
    threads opened             0
    comments posted            0
    SANCTIONED_MUTATIONS       2, unchanged all wave
    fill entries landed        0
    confirm_tokens minted      0
    confirm_tokens used        0
    writes performed           0
    _state/session.json        untouched
    phase 2                    untouched, as instructed

Nothing was fired. Nothing was pushed.

---

# PART FIVE -- THE OPERATOR LIFTED THE STANDARD, AND SEVEN CAPABILITIES WERE ANSWERED (2026-09-01)

Part Four closed with **none of the three shipping** and the typing ruling
unspent. That close was correct on its evidence and was overtaken within the
hour: the operator was shown exactly what he would be accepting -- a write that
fires and cannot tell him whether it worked, and that for an invitation he
would be checking after the fact, on a person -- and he took it.

## 33. THE THREE RULINGS, AND WHAT EACH ONE DID NOT LIFT

**RULING 1 -- an unverifiable outcome is a shippable outcome, PROVIDED IT SAYS
SO.** `performed: "unknown"` stops being a reason to refuse and becomes an
honest result, on condition that the gate names what surface would confirm the
act, why this server cannot read it, and **what he must do himself**.

**RULING 2** -- `update_profile_field` may overwrite without recording the
previous value, provided the preview says it cannot report what it overwrites.

**RULING 3** -- `react_to_item` may apply LinkedIn's default reaction, provided
the preview states that nobody has measured which one that is.

**WHAT NONE OF THEM LIFTED, and this is the line the whole wave turns on:**

> **A check that CANNOT PASS may never ship as though it might.**

That was `apply_job`'s defect. What is now permitted is the opposite: a write
that declares its outcome unverifiable up front. Never compare against a reader
that cannot return the value; if there is no surface, say there is none. The
difference between those two is the entire content of Ruling 1, and the guard
below is that sentence expressed as an assertion.

**AND A RULING CANNOT MEASURE A CONTROL.** Three of the seven were blocked on
MEASUREMENT rather than permission, and lifting a verification standard does
not photograph anything. That distinction did most of the work this wave.

## 34. `Unverifiable` -- THREE FIELDS, NOT A PARAGRAPH

Ruling 1's three disclosures are a structured field on `WriteSpec`, printed in
the preview **and repeated on the result**:

    surface_that_would_confirm   what WOULD settle it, named
    why_it_cannot                the MEASUREMENT, not a shrug
    what_he_must_do              the instruction he can act on

**A paragraph carrying all three is a paragraph that can lose one**, and the
field that goes missing is always the third -- the first two are about the
software and only the third is about him. It is repeated on the RESULT because
the sentence he needs after acting is the one telling him where to look.

`_verify_after` returns a declared-unverifiable action's answer **before any
navigation, read or comparison**. That order is the safety property rather than
an optimisation: a comparison that runs is a comparison somebody later reads as
evidence.

## 35. THE DEFECT FOUND WHILE BUILDING THE GUARD, AND IT WAS WORSE THAN THE ONE IT WAS FOR

`_verify_after` ended in:

    if spec.action != "unfollow_company":
        <read the SAVED tab>

**Every action that was not an unfollow silently adopted the save pair's
verifier.** That is the actual mechanism behind `apply_job` comparing
`"applied"` against a reader that could only ever say `saved` / `not_saved` /
`unknown` -- not a typo in one comparison but a DEFAULT that hands one action's
reader to every other. Falling through LOOKED like being handled.

`unfollow_company` itself was reached by falling PAST that negative test, which
made it invisible to any check asking *which actions are handled*. Both are
explicit positive branches now, and an action reaching the end RAISES rather
than borrowing somebody else's reader.

### The guard: `tests/test_unverifiable_outcomes.py`

* **EXACTLY ONE** of {a branch in `_verify_after`, a declared `unverifiable`}.
  Neither is the apply shape. Both is worse -- a declaration used as cover for
  a comparison that still runs.
* Where a branch exists, the reader it calls must be able to RETURN the value
  compared against. Derived by AST from the real `_TrackerStage` objects, not
  from a list kept beside them.
* A **behavioural** proof, because the other two are structural: `_verify_after`
  is handed a navigator and page that raise on ANY attribute access.
* The AST branch-reader has its own control -- a rename would otherwise empty
  the file silently, and an empty corpus passes everything.

Five mutations, all caught, including **`apply-verifies-against-the-saved-tab`,
which reintroduces the original defect verbatim.**

## 36. THE SEVEN, EACH ANSWERED

| # | capability | outcome | what settled it |
|---|---|---|---|
| 1 | `react_to_item` | **PERFORMS** | three blockers measured away 2026-08-31; the fourth (which reaction) became a Ruling 3 disclosure in `residue` |
| 2 | `send_invitation` | **PERFORMS** | the aim CLOSED by measurement (`aim_invitation` resolves his needle to exactly one, inside the page); the verification was declared under Ruling 1 |
| 3 | `publish_post` | **PERFORMS** | typing granted; verification declared -- the activity rail is unreliable, not absent |
| 4 | `comment_on_item` | **PERFORMS, expecting to refuse** | surface, editor and aim measured; the SUBMIT is not, so it is found by ARRIVAL and refuses with the observation |
| 5 | `update_profile_field` | refuses | **measurement**: no field inside any editor has been observed. Ruling 2 lifted the previous-value requirement and cannot photograph a field |
| 6 | `send_message` | refuses | **measurement**: `Send` is measured (disabled while empty) but the RECIPIENT control's name never reached disk |
| 7 | `set_open_to_work` | refuses | **measured, and the ruling was deliberately not stretched** -- see section 40 |

**Four shipped. Three refuse, and every one of the three refuses on a
MEASUREMENT gap rather than on a permission the operator withheld.**

## 37. THE SENTENCES THAT ARE NOW THE PRODUCT

For each write that cannot confirm itself, the gate prints -- verbatim -- what
he must do:

| action | what he must do himself |
|---|---|
| `send_invitation` | *"open My Network, then Manage, then Sent, and look for the person. That is the only way to know whether this landed"* |
| `publish_post` | *"open your profile and look at your recent activity. If the post is there it published; this server cannot tell you reliably either way"* |
| `comment_on_item` | *"open the post and look at the comments. Yours will be attributed to you. AND IF THIS REFUSES AFTER TYPING: a comment draft may be left in the box, and whether that draft is local to this browser or saved to your account is UNMEASURED..."* |

## 38. THE PACKAGE TYPES NOW, AND SAID IT DID NOT UNTIL TODAY

`readonly.SANCTIONED_MUTATIONS` went from two entries to **three**, and the
third is the first that is not a click:

    ("linkedin_server/writes.py", "perform", "click")
    ("linkedin_server/dom.py",    "activate_messaging_filter", "click")
    ("linkedin_server/writes.py", "perform", "fill")        <- 2026-09-01

**"It types nothing" was true, was printed in THREE places, and is now false.**
All three were corrected in the commit that made them false -- `readonly.py`'s
module docstring, `shape.py`'s composer disclosure, and the tool docstring. A
reader who remembers the old guarantee meets the change where the guarantee
was.

**ONE FILL, ONE DRAIN POINT**, mirroring the click queue, because the scanner
counts CALL SITES and one drain point is what keeps the allowlist readable.

### What the boundary digests say this cost

Re-frozen a third time, and **only `SANCTIONED_MUTATIONS` moved**.
`<functions>` is byte-identical at `eb16cd07f5cf369d` -- `assert_read_url` and
every gate function unchanged -- and all four denylists are unchanged.
**Permitting a fill widened the allowlist DATA by one tuple and touched no
gate, no url pattern, no mutation pattern.** That is a measurement, not a
claim: a change that had loosened any of those on the way past would have moved
a second digest.

### The byte-identity test found its own weakness

The operator's third typing condition -- *the exact text verbatim in the
preview* -- is a promise about a string, so it is the one that could rot while
everything still looked right. The first version of the check compared
UNPARSED SOURCE against a substring, and this mutation **passed it**:

    _text_component_of(spec, grant.target) + " #hiring"

The substring is still in there. That mutation is precisely the "this server
composes what it types" failure the condition forbids. The check is on the AST
NODE TYPE now -- a BinOp, an f-string, a slice or any wrapper is a different
node. Four mutations caught: appending, truncating, wrapping, typing a literal.

## 39. THE EMPTY-STATE ASYMMETRY -- ONE MEASURED BOOLEAN, TWO DIFFERENT INSTRUMENTS

This is the finding of the wave's second half and it is worth carrying alone,
because anyone re-deriving it from control NAMES gets it wrong the same way.

| surface | submit candidate | state while EMPTY | does a fill produce a signal? |
|---|---|---|---|
| `/preload/sharebox/` | `Post` | **disabled** | YES -- disabled to enabled |
| `/messaging/compose/` | `Send` | **disabled** | YES -- same shape |
| `/feed/update/<urn>/` | `Comment` | **ENABLED** | **NO** |

`Post` being disabled while empty **is itself the evidence it is the submit**,
and it is what makes a post-fill gate possible at all. The comment surface has
no transition to observe, so *"present, visible and enabled, named Comment"* is
satisfied BEFORE anything is typed -- a gate keyed on it presses the FOCUS
AFFORDANCE and returns something indistinguishable from success.

So `comment_on_item` identifies its submit by **ARRIVAL**: it did not exist
until there was something to submit. Names censused before the fill and after;
exactly one NEW NAME is aimable; a name whose COUNT merely grew means two
controls share one name and only position separates them, which is refused.

**It is expected to refuse on first use and its docstring leads with that.**
Measuring the submit requires the fill, and the fill is the act the gate
authorises -- so the refusal, carrying `arrived` and `grew`, IS the
measurement. The same shape `unsave_job` took when its ON label could not be
observed until one write produced it.

Container scoping was checked and **does not survive**: the editor, the
`Comment` control and all four `Reply` buttons report container `none`; the
only container-bearing controls on that permalink are two ad dialogs and the
ad-report form. The delta is whole-page with that noise named rather than
hidden.

## 40. `set_open_to_work` -- THE RULING ADMITTED THE DOOR AND NOT THE ROOM

The operator ruled that **a click measured to issue no `ServerRequest` is, by
effect, a READ** -- extending this package's own reasoning about the messaging
filter pills. That ruling admits opening a modal.

`_audit/_slice-otw-census.md` had already measured the procedure, statically,
over five captures. Nine steps, and the danger is concentrated in exactly one:

| step | control | action list | admitted? |
|---|---|---|---|
| 4 | `Show details` | **one `Navigate`, NO `ServerRequest`** | **YES** |
| 7 | `Edit` | `SetState` x2 then **`ServerRequest ...saveAndFetchNextStepRequest`** | **NO** |

And the audit's own two sentences, which settle it:

> **First step that shows the editor's controls: step 7. First step that could
> change state if mis-clicked: also step 7. The two are the same click.**

**So the editor is not reachable by a click measured to send nothing**, and the
ruling was not stretched to cover `Edit` -- whose request is named
`saveAndFetchNextStep` by LinkedIn, and which writes two `SetState` values
optimistically before the request leaves.

One question stays genuinely open and is recorded rather than closed: nothing
on disk says whether the AUDIENCE control lives in the step-5 detail modal or
one level deeper. Settling it would cost a **FOURTH** entry in
`SANCTIONED_MUTATIONS` -- a click on a read path -- to answer a question whose
likely answer is *still refuses*. That widening outlives the wave, and it was
surfaced as a decision rather than taken.

## 41. THE GUARD THAT COULD NOT SEE A NEW FILE

Found because it fired one commit late on a REAL activity id -- one of his own
posts, on a public repo under his real name.

> **THE CHECK A NEW FILE MOST NEEDS RAN ONLY AFTER THE FILE WAS PUBLISHED.**

Both guards swept `git ls-files`. The file sat in the working tree through a
full green suite; that run was green AND CORRECT, because the file was
invisible to the question. It became visible in the same commit that put the id
in history.

`committable_files()` = tracked + untracked-not-ignored. `.gitignore` still
keeps `_state/`, caches and build output out; what remains is exactly what a
`git add` would pick up. **The credential guard now sweeps a strict SUPERSET**,
asserted rather than argued -- nothing it measured before is unmeasured now.

Shown blind at the mutation, with an untracked fixture carrying both plants:

    widened sweep        credential RED    identity RED
    untracked half cut   credential GREEN  identity GREEN   <- blind

**The durable test is set-level and writes no plant**, which is a risk trade
rather than a weaker check: a standing end-to-end version would leave a
credential-shaped string in the working tree if pytest were killed mid-run,
manufacturing on a schedule the exact condition this repo suffered that
morning. The property is composed from two checks that each fail alone.

**It proved itself four hours later, unprompted:** `test_comment_delta_gate.py`
was untracked during a full suite run and was swept anyway.

## 42. AND MY OWN REPORT WAS WRONG WHERE THE INSTRUMENT WAS RIGHT

I reported that urn as already fixed. It was -- **in the other file.** Two
files had the identical defect, one fix went in, and the report generalised
from one instance to the class.

> **I reported a fix by its class, not by its instances.**

The guard disagreed with the summary and the guard was right, which is the
whole argument for checks that fail loudly over reports that read well.

## 43. THE THIRTEEN-ROW LEDGER

| # | action | state | the ground, as measured |
|---|---|---|---|
| 1 | `save_job` | **PERFORMS** | anchor `Save the job`, verified against the Saved tab |
| 2 | `unsave_job` | **PERFORMS** | anchor measured across two independent routes |
| 3 | `follow_company` | **PERFORMS** | verified by re-reading the followed list |
| 4 | `unfollow_company` | **PERFORMS** | numeric id; refuses when the Page is not among rendered rows |
| 5 | `apply_job` | **PERFORMS**, irreversible | verification now reads the Applied tab; the submit gate names which of five conditions refused |
| 6 | `update_setting` | **PERFORMS** | three-state radio group; role read off the row; verified by reload and re-read |
| 7 | `react_to_item` | **PERFORMS** | OFF anchor on three surfaces; permalink draws exactly one control; verification returns `to_state`, and declines to say WHICH reaction |
| 8 | `send_invitation` | **PERFORMS**, irreversible | needle resolved to exactly one control inside the page; outcome DECLARED unverifiable |
| 9 | `publish_post` | **PERFORMS**, irreversible | `Post` disabled-while-empty gives a real post-fill gate; refuses to type over a restored draft; outcome declared unverifiable |
| 10 | `comment_on_item` | **PERFORMS**, irreversible | submit found by ARRIVAL; expects to refuse and reports what it saw |
| 11 | `send_message` | refuses | `Send` measured; the RECIPIENT control's name never reached disk. A measurement, not a permission |
| 12 | `update_profile_field` | refuses | `/edit/` forbidden with one exact-url exemption; no field inside any editor observed |
| 13 | `set_open_to_work` | refuses, **no tool** | the editor is behind a click that fires `ServerRequest saveAndFetchNextStep`; the no-`ServerRequest` ruling admits step 4 and not step 7 |

**Ten perform. Three refuse, all three on measurement.**
`performable_and_irreversible` is **four**: `apply_job`, `comment_on_item`,
`publish_post`, `send_invitation`.

## 44. THE FINDINGS THAT OUTLIVE THIS WORK

The four from Part Four stand unchanged and are not repeated here. This wave
added two.

> *The check a new file most needs runs only after the file is published.*

A guard against committing something must see what is ABOUT TO BE committed,
not only what already was -- otherwise its first true answer always arrives one
commit late, which is precisely too late for anything it protects. Its
green runs before that are not wrong; they are answers to a narrower question
than the one anybody was asking.

> *One measured boolean can separate a trivial gate from an impossible one.*

`Post` and `Send` are drawn DISABLED while empty; `Comment` is drawn ENABLED.
Two of those surfaces can be gated on a state transition and the third cannot
be gated that way at all -- and every one of the three carries a plausible,
well-named submit control. **A design derived from control names alone gets
this wrong**, confidently, and the resulting gate presses the wrong control
while looking exactly like success.

## 45. RECEIPTS, PART FIVE

    commits                   fd9f49e  the Unverifiable mechanism + the catch-all fix
                              d74178f  react_to_item performs
                              bc7447a  send_invitation performs
                              b6bf408  publish_post performs -- the package types
                              051c518  the urn out; seven skips converted
                              43a8d6b  the guards see untracked files
                              1fb3c15  comment_on_item performs

    suite                     2389 passed, 0 failed, 0 SKIPPED
    tree                      identical at both ends of every gating run
    SANCTIONED_MUTATIONS      3 (click, click, fill); both non-dom entries in perform
    PERFORMABLE               10
    irreversible+performable  4
    boundary digests          only SANCTIONED_MUTATIONS moved; <functions> unchanged
    confirm_tokens            0 minted, 0 used
    writes performed          0
    _state/session.json       untouched, f0892e35688868fa, 7813 bytes
    phase 2                   untouched

Nothing was fired. Nothing was pushed from this seat.

---

# PART SIX -- THE SEVENTH CAPABILITY, AND THE CLOSE (2026-09-01)

## 46. `set_open_to_work` -- THE RULING WAS ADMITTED AND ITS PRECONDITION WAS NOT

The operator ruled that **a click measured to issue no `ServerRequest` is, by
effect, a READ** -- extending this package's own reasoning about the messaging
filter pills, which send nothing and change nothing. That is a real route to a
modal, and it is the route this action needed.

The wave lead overrode a recommendation not to spend a fourth
`SANCTIONED_MUTATIONS` entry on it, and the override was right on two grounds
worth keeping:

* **declining the entry would have made the ruling unactionable.** A ruling
  whose implementation is refused exists on paper and nothing may act on it.
* **the entry would have been NARROWER than the three already there.**
  `perform`'s click and fill are STATIC permits -- authorised by the gate, not
  by any measurement of the control they land on. This one would have been
  authorised **per click, by a live reading of that control's own action
  list.** That is a stronger shape than anything on the list.

### The instrument, and the floor that made its answer trustworthy

`dom.read_sdui_actions` counts SDUI action tokens in the flight payload and
returns **integers only** -- the payload is ~1.09 MB of his profile, which is
why the tracked fixtures carry zero script characters.

Its `readable` flag is False unless the payload was present **AND** carried
recognisable action tokens. That floor is the reason the result below is a
finding rather than a shrug: **a parser that has stopped parsing returns zero
of everything, and a row of zeroes is the exact shape of permission.**

### The measurement -- one admitted read, no click

    settle    verdict CONSISTENT    expected 233    read 233

    sdui      script_blocks    2
              payload_chars    2,146
              needle_hits      0
              global           server_request 0, navigate 0, set_state 0, show_menu 0
              readable         FALSE
              error            null

    2026-08-24, pre-hydration    17 script blocks    1,091,238 payload chars
    2026-09-01, at load event     2 script blocks         2,146 payload chars

Three things make that decisive rather than inconclusive:

1. **The page had fully arrived.** `settle` says `consistent` at 233/233. An
   absence measured on a half-rendered page is worth nothing; this one is not.
2. **The reader ran.** `error: null`. It did not throw and did not fail to
   parse. It looked, and found 2,146 characters carrying not one action token.
3. **So the diagnosis is ABSENT PAYLOAD, not broken reader** -- two different
   `readable: false` verdicts, and this is the second.

### The refusal

**`set_open_to_work` refuses because the ruling's PRECONDITION cannot be
satisfied through this transport.** Not because of `Edit`, and not because the
reader is broken. The action lists the ruling turns on live in a React flight
payload that is gone by the time this server can look. The 2026-08-24 audit's
own post-hydration figure -- 3,686 characters -- matches today's 2,146, so this
is the documented behaviour of the surface rather than a surprise.

**The DOM controls are all still there** -- `Open to` with
`aria-expanded="false"`, `Edit` at count 1. What is gone is the EVIDENCE ABOUT
WHAT THEY DO, and the ruling turns on the evidence rather than on the controls.

**The negative control was never reachable.** `Edit` could not be shown
returning non-zero, because there is no payload to count in for EITHER control
-- so by the rule agreed before the reading, no click was authorised and none
happened.

### THE FOURTH ENTRY WAS NEVER SPENT

`readonly.SANCTIONED_MUTATIONS` is still **three**. The widening the lead
accepted the cost of turned out not to be needed: the question cost **one page
load of his own profile** -- no badge, no third party, no click, no new
permission. The right call was to ask, and the recommendation against asking
was wrong about the price.

### What would lift it, and why it may not be worth lifting

The payload exists **pre-hydration**. Reaching it means capturing the document
response before the page hydrates, which is **request interception** -- `route`
is on `readonly._MUTATION_CALL_PATTERNS`. That is a materially LARGER
capability than the click it would have authorised: it lets this server see raw
traffic rather than one measured control.

**And it may not be worth it even then.** Step 7's `Edit` still fires
`saveAndFetchNextStep`, so the editor stays behind a click that saves. The
payload would only settle whether the AUDIENCE control happens to sit one level
shallower, in the step-5 detail modal. Recorded as a decision belonging to the
operator, with a recommendation against.

### The cheaper route was checked, and it is FORECLOSED

The obvious move is to skip the browser: a plain authenticated **HTTP GET of
the profile never hydrates**, so it would return the flight payload intact and
restore exactly the measurement this precondition needs, with no interception
at all.

**It is the LARGER of the two changes, not the smaller.** `route` stays inside
Playwright, which this server already is. An HTTP client is a **new data path
in a server whose defining property is not having one** -- and the packaging
says so in its own words:

    dependencies = ["fastmcp>=2.0,<4", "playwright>=1.40"]

> *"This server has no HTTP data path at all: every tool drives a real
> signed-in Chrome, so an install without playwright is an install that cannot
> answer a single call."*
> -- `pyproject.toml`, on why playwright is not an optional extra

Giving a browser-only server a raw HTTP path to fetch one payload is a louder
change than the interception it would replace. Written down here so the next
reader meets the reason rather than the idea.

### Why even the SAFE click is unreachable -- the cleanest statement of the stuckness

The wave lead announced he would spend the fourth entry on the census's step-4
`Show details` click, and then corrected it. The correction is the sharpest
form of this whole finding:

**The census rates steps 1-6 PROVABLY SAFE, and that proof is drawn from the
same flight payload that is absent from a live load.** So the safe first click
is blocked by the IDENTICAL missing evidence as the dangerous one -- not by
permission, and not by the ruling.

**There is nothing to click, because there is nothing to measure.**

That is why the fourth entry stays unspent. It was authorised, and the thing it
would have authorised cannot be authorised by anything.

## 47. THE THIRTEEN-ROW LEDGER, FINAL

| # | action | state | the ground, as measured |
|---|---|---|---|
| 1 | `save_job` | **PERFORMS** | anchor `Save the job`, verified against the Saved tab |
| 2 | `unsave_job` | **PERFORMS** | anchor measured across two independent routes |
| 3 | `follow_company` | **PERFORMS** | verified by re-reading the followed list |
| 4 | `unfollow_company` | **PERFORMS** | numeric id; refuses when the Page is not among rendered rows |
| 5 | `apply_job` | **PERFORMS**, irreversible | verification reads the Applied tab; the submit gate names which of five conditions refused |
| 6 | `update_setting` | **PERFORMS** | three-state radio group; role read off the row; verified by reload and re-read |
| 7 | `react_to_item` | **PERFORMS** | OFF anchor on three surfaces; permalink draws exactly one control; verification returns `to_state` and declines to say WHICH reaction |
| 8 | `send_invitation` | **PERFORMS**, irreversible | needle resolved to exactly one control inside the page; outcome DECLARED unverifiable |
| 9 | `publish_post` | **PERFORMS**, irreversible | `Post` disabled-while-empty gives a real post-fill gate; refuses to type over a restored draft; outcome declared unverifiable |
| 10 | `comment_on_item` | **PERFORMS**, irreversible | submit found by ARRIVAL; expects to refuse on first use and reports what it saw |
| 11 | `send_message` | refuses | `Send` measured disabled-while-empty; the RECIPIENT control's name never reached disk. A MEASUREMENT gap |
| 12 | `update_profile_field` | refuses | `/edit/` forbidden with one exact-url exemption; no field inside any editor observed. A MEASUREMENT gap |
| 13 | `set_open_to_work` | refuses, **no tool** | the ruling's precondition is unsatisfiable through this transport: the action lists are in a payload absent at load. A MEASUREMENT gap |

**Ten perform. Three refuse, and every one of the three refuses on a
MEASUREMENT gap rather than on a permission he withheld.** A ruling cannot
photograph a control, and that sentence is the shape of this whole wave.

`performable_and_irreversible` is **four**: `apply_job`, `comment_on_item`,
`publish_post`, `send_invitation`.

## 48. THE DISCLOSURE SENTENCES, VERBATIM

For each write that cannot confirm itself, what the gate prints -- the third
field, the one that is about him:

| action | what he must do himself |
|---|---|
| `send_invitation` | *"open My Network, then Manage, then Sent, and look for the person. That is the only way to know whether this landed"* |
| `publish_post` | *"open your profile and look at your recent activity. If the post is there it published; this server cannot tell you reliably either way"* |
| `comment_on_item` | *"open the post and look at the comments. Yours will be attributed to you. AND IF THIS REFUSES AFTER TYPING: a comment draft may be left in the box, and whether that draft is local to this browser or saved to your account is UNMEASURED..."* |

## 49. THE FINDINGS

The four from Part Four stand unchanged. Part Five added two. This part adds
two more, and one of them is the sentence the whole wave turned on.

> *A zero from a reader that has never been shown returning non-zero is not a
> measurement.*

Every instrument failure in this repository's last three days is one shape: an
instrument returning a clean answer to a question it could not actually ask. A
guard blind to a doubled backslash. A comparison with no passing case. A corpus
of nothing reading as a pass. A suite green over a file it could not see. A
parser that has stopped parsing reports zero of everything -- **and a row of
zeroes is the exact shape of permission.**

It is why `read_sdui_actions` carries its own floor rather than trusting a
caller to check one, and it is why `readable: false` from an absent payload is
a FINDING where a bare row of zeroes would have been an invitation.

> *The payload cannot be kept because of what is in it, so the measurement has
> to be retaken live. Those are the same fact, not bad luck.*

The two captures the OTW census worked from are gone, and the surviving
fixtures carry zero script characters DELIBERATELY -- because the flight
payload is where his identity lives. The safety property that protects him is
the same property that makes offline validation impossible. Treating the
absence as an obstacle would have missed that they are one fact.

## 50. RECEIPTS, PART SIX

    commits           034fb78  the SDUI reader and its floor
                      <this>   set_open_to_work's refusal, rewritten from the
                               live measurement, and this close

    suite             see the run recorded with the commit
    SANCTIONED_MUTATIONS   3 -- the fourth entry was authorised and NOT SPENT
    PERFORMABLE            10
    still refusing         send_message, update_profile_field, set_open_to_work
    live reads this part   1 (his own profile, settle-confirmed)
    clicks                 0
    confirm_tokens         0 minted, 0 used
    writes performed       0
    _state/session.json    untouched
    phase 2                untouched

Nothing was fired. Nothing was pushed from this seat.

---

# NEEDS-RECONNECT  --  the live validations queued behind ONE server reload

Written as it accumulates rather than reconstructed at the end, because this
list is the thing that makes ONE reconnect sufficient instead of six. The
loaded process holds the code it started with; a fix on disk is not a fix in
the session. Everything here is code-complete and gated, and needs only the
server to reload before it can be exercised against live LinkedIn.

| # | what to run | what it settles | expected outcome |
|---|---|---|---|
| 1 | `linkedin_profile_editor_fields` | the field names inside `/in/me/edit/intro/` | **DONE 2026-09-01 -- SUCCEEDED** |
| 2 | `dom.read_compose_fields` on `/messaging/compose/` | the two SEND-MODE radio labels, and whether either is an **InMail** | **BLOCKED -- not reachable from any tool** |
| 3 | the same reading | the message body's `aria-label`, which the census reduces to `<opaque>` | **BLOCKED -- same cause** |
| 4 | a third `premium` census | whether `/premium/my-premium/` has a settled control count at all | **DONE 2026-09-01 -- no baseline, and no balance** |

## Item 1 -- ANSWERED, and the answer refutes the premise the capability was re-adjudicated on

    self_ownership  established TRUE, same_member TRUE
    landed_paths    editor /in/<member>/edit/intro   (no <<member>mber>)
    container       dialog, anchor "Save", 23 controls

Both defects confirmed fixed against the live surface. Named controls:
`First name*`, `Last name*`, `Additional name`, `Industry*`, `City`,
`Country/Region*`, `School*`, `Month`, `Save`, and one `div[role=textbox]`
whose name comes back as `<content>`.

**`update_profile_field` now has exact-named controls and a readable previous
value for NONE of them without a guess:**

| what `linkedin_my_profile` returns | the editor's controls | the gap |
|---|---|---|
| `name` | `First name*` AND `Last name*` | one value, two controls -- splitting it is a guess |
| `location` | `City` AND `Country/Region*` | one value, two controls -- same |
| `headline` | `<content>` | readable value, **no named control** |
| (nothing) | `Industry*`, `Additional name` | named control, **no readable value** |

The re-adjudication held that recording the previous value was the FEATURE
rather than the blocker, and it was right about the reasoning. What it could
not know is that **this server has no value reader at all** -- "LABELS, NEVER
VALUES" is the editor reader's entire design. The restore path needs an
instrument that does not exist, and building it is a READ.

## Item 4 -- ANSWERED. Third reading, and NO baseline recorded

    73  (first)    80  (second)    80  (third)

Two agree at 80 and **that is not enough here, because the variance is
EXPLAINED**: the page carries a paginated carousel and drew `Page 1..6` at
counts 3,3,3,2,2,1. The control count moves with how much of the carousel
renders, so the surface has no single settled number and two agreeing readings
would be a coincidence rather than a measurement.

**And still no credit balance.** The complete numeric inventory is pagination
and marketing offers plus nav badges. Third independent reading, same absence.

## Items 2 and 3 -- BLOCKED ON ONE PIECE OF TOOL CODE, and that is my error

`dom.read_compose_fields` was built, unit-tested and mutation-tested, and
**never wired to a tool**. So neither item was answerable on the last
reconnect regardless of which build was loaded.

I should have checked REACHABILITY when writing this list. The list exists to
make one reconnect sufficient, and **an item on it that no caller can invoke
is the same defect as a check that cannot fail** -- it looks like coverage and
is not.

## A prediction on file for item 2, before it is run

**I expect `read_compose_fields` to REFUSE with `name_shaped_label_present`.**

The census reduced the two send-mode labels to `<redacted>` and `<redacted> to
<redacted>`. The most likely raw text is *"<his name> will send message"* and
*"<his name> to <someone> will send message"*  --  and the guard refuses any
label carrying a run of capitalised words.

**That refusal would be over-cautious, and the reason is worth stating before
the fact rather than after.** The guard cannot tell WHOSE name it is. In a
composer with no recipient selected, a name is almost certainly HIS OWN  --  and
his own name is not a third-party disclosure. The self-ownership argument this
whole reader rests on says the container is his.

I have **built it to the ruling as given** rather than quietly loosening it,
because a guard that publishes a name on the reasoning that it is *probably*
his is exactly the shape this package refuses. If it refuses on his own name,
that is a ruling to make with the evidence in hand, not a rule to soften in
advance.

### RESOLVED, and the reframe is better than the tension it dissolves

The risk was never that HE must not see his own name. **It is that a control
label becomes a COMMITTED CONSTANT** -- `MESSAGE_RECIPIENT_LABEL = "Enter
message recipients"` sits in this repository -- and a literal `"<his name>
will send message"` in source is a name committed, which
`test_no_committed_identity` would flag on the next run and would be right to.
**The guard protects the label table, not his eyes.**

So the string is not stored and the DISCRIMINATOR is. The two modes differ
structurally and the difference carries no name:

    one capitalised run, no " to "        ->  runs=1, joined_by_to=False
    two runs joined by " to "             ->  runs=2, joined_by_to=True

both before the same name-free tail, which IS storable. The guard refuses to
publish the labels; the reader still answers which mode is checked. **Nothing
was softened and the question is still answered.**

### AND THE LABELS MAY NOT SETTLE THE CREDIT QUESTION AT ALL

This is the part not to stretch. *"X will send message"* against *"X to Y will
send message"* most likely describes sending **as himself versus on behalf of
a Page** -- which says nothing whatever about metering. **If the shapes come
back like that, the InMail question is still open and must be reported as
open.**

What would actually settle it, none of which this server can currently read:

* a readable **credit balance** -- measured absent on `/premium/my-premium/`,
  twice, on readings of 73 and 80 controls that do not agree with each other;
* an explicit **InMail affordance** on the composer -- the control named
  `InMail` there is a conversation FILTER PILL carrying `aria-checked`, beside
  `Focused` / `Unread` / `Starred` / `Connections`, confirmed three times;
* some Premium surface naming an allowance, which nothing measured so far does.

**An unmetered assumption is exactly what the gate must not rest on.** If the
shapes do not answer it, `send_message` still refuses on that ground, and the
refusal names this list as what would lift it.

## What is NOT on this list, and why

`set_open_to_work` is not here. Its blocker is not a stale process: the SDUI
flight payload is absent from a live load, measured twice, so no reconnect
changes it. It refuses on measured ground and the fourth mutation entry stays
unspent.

# PART SEVEN -- THE VALUE READER, AND THE RESTORE PATH

Batch item 2 of four. Items 1, 3 and 4 landed in `f2d612b`; this is the last
one, and it is the one with an argument in it rather than a wiring.

## 51. WHAT WAS BUILT, AND THE RULING IT ANSWERS

`linkedin_update_profile_field` overwrites a field and cannot say what it
overwrote. That shipped, deliberately, with the preview saying so. The ruling
that produced this reader is the refinement of it:

> **The previous value is the FEATURE, not the blocker.** Code can make an
> action correct; it cannot make an irreversible outward-facing action
> undoable. Only the old value can, and only if somebody has it.

So this reads it, and nothing else. `linkedin_profile_editor_values` is a
READ: it loads two pages, clicks nothing, types nothing, mints no token and
does not touch the gate. It hands him the string he would need to type back.
The typing back is his own call through the ordinary two-step confirm.

**Nothing fired. No `confirm_token` for any of the ten.**

| what | where |
|---|---|
| `dom.EDITOR_VALUES_JS` | the injected script, 8.4 kB |
| `dom.EDITOR_VALUE_MAX_CHARS = 3000` | above About's 2,600 and headline's 220 |
| `dom.read_self_owned_editor_values` | the reader |
| `server._establish_self_owned_editor` | the shared ownership gate, NEW |
| `server.linkedin_profile_editor_values` | the tool, 35th, 23rd read |
| `tests/test_editor_values.py` | 28 tests, R1-R15 |

## 52. THE SAME BAR IS NOW A FACT ABOUT THE CODE, NOT A CLAIM ABOUT IT

The promise made about this tool is that it clears exactly the gate the label
tool clears. Two copies of that gate would make it a claim, and a claim that
drifts is precisely how the WIDER tool ends up with the WEAKER check --
somebody strengthens one and does not know there are two.

So the ~110 lines of ownership dance moved OUT of
`linkedin_profile_editor_fields` and into `_establish_self_owned_editor`, and
both tools call it. `test_neither_editor_tool_reimplements_the_ownership_gate`
reads the source and asserts that neither tool body contains
`_self_assertion_on`, `_member_segment_of`, `_ownership_block(` or
`SELF_PROFILE_URL` -- scoped to the two BODIES, because other tools in
`server.py` legitimately use those primitives.

The structural check alone would pass on two tools that called one helper and
then ignored what it said, so
`test_the_two_tools_refuse_the_same_way_on_the_same_page` drives BOTH over two
hostile landings and compares their refusal codes, page counts and navigation
lists **to each other** rather than to a literal. A literal would be a number
maintained in two places, which is the disease.

`pages_loaded` now comes from the helper, because the helper is what loads the
pages.

## 53. WHY A SECOND SCRIPT AND NOT A FLAG ON THE LABEL READER

The cheap design was `cfg.readValues` on `EDITOR_FIELDS_JS` -- one script, one
copy of the name chain, no new `# readonly-ok` waiver.

It was refused, and the reason is one assertion:

    assert ".value" not in dom.EDITOR_FIELDS_JS

That guard is **unconditional**. There is no code path, no argument and no
caller mistake that reaches a value through the label reader. A `cfg` flag
converts it into a claim about a branch, on the narrowest and most-scrutinised
reader in this package -- the one whose whole standing is that it cannot do
this. **A waiver is a cheaper thing to spend than that guard**, so the eleventh
evaluate waiver was spent instead.

The cost is a THIRD copy of the name chain, and it is paid rather than waved
at: `test_the_three_name_chains_agree` runs `CENSUS_JS`, `EDITOR_FIELDS_JS` and
`EDITOR_VALUES_JS` over one document and compares name AND `name_source`.
`test_the_label_readers_no_value_assertion_is_still_unconditional` re-asserts
the guard from the new file, so anyone merging the two scripts fails in the
file that would have benefited from the merge.

## 54. WHAT IS WITHHELD, AND WHERE

Withheld **inside the page**, for the reason `INVITE_NEEDLE_JS` does its
comparison there: a string that reaches this process can reach a traceback or
a log line, and no care downstream un-rings that.

| control | `value_source` | why |
|---|---|---|
| `input[type=file]` | `withheld_by_type` | its value is a path on his own disk |
| `input[type=password]` | `withheld_by_type` | a secret; no editor field is one, which is why it is structural rather than noticed-absent |
| checkbox / radio | `state_not_value` | the `value` attribute is a submission token, not the state. The state is `checked` and it is the LABEL tool's field |
| a `select` | `selected_option` | the OPTION TEXT, not `el.value` -- restoring by submission token is not something a human can do in the editor |

**A control whose name is its own content still comes back as `<content>`.**
The name half of this reader is the label reader's, unchanged, so the content
is disclosed EXACTLY ONCE, in the value slot where a reader knows what it is
looking at. `test_the_editable_content_arrives_as_a_value_and_not_as_a_name`
asserts the string appears exactly once in the serialised answer.

## 55. VALUES COME BACK VERBATIM, AND THAT IS THE ONE DELIBERATE UNSHAPING

`shape.census_substitute` is NOT called on a value. It is called on the name
in the same record.

A urn, a member path, a company path, a possessive and a long digit run are
all legal things to have in a headline. Substituting one produces a string
that LOOKS like his value and is not, and he would paste it back believing it
was. **The failure would be silent, and the tool would have caused exactly the
loss it exists to prevent.**

R8 and R9 are the same urn in two slots, with two opposite answers, and each
asserts the substitution WOULD have changed the string -- so neither is a
value that happens to survive.

A value is also **not trimmed**, unlike every name route. A name is read for a
human to recognise; a value is read for a human to put back.

## 56. TRUNCATION IS REPORTED, NEVER DISGUISED

3,000 characters, chosen against the surface rather than picked: LinkedIn's
headline caps at 220 and About at 2,600, so every profile field this reader
can meet comes back WHOLE. Past that, `value_truncated` is true and
`value_chars` carries the REAL length. **A truncated value is a broken restore,
not a shorter one**, and a prefix that looks complete is the dishonest failure.

`value_chars` is uncoerced: `None` means no value route applied at all, `0`
means the control held an empty string. Both are in one answer in
`test_an_empty_value_is_not_an_absent_one`, on the field where confusing them
would mean restoring an empty string over real content.

## 57. THE MUTATION TABLE -- 20 APPLIED, PLUS ONE PLANTED IN THE TEST

Twenty were applied to the tree one at a time, each file restored
byte-for-byte in a `finally` with the restore asserted. The last row is not
one of them: the click is planted INSIDE the test, which is how the scanner's
own control has always been written here. Assertion text as produced.

| mutation | test | what it printed |
|---|---|---|
| `editable-value-dropped` | R1 (x2) | `assert None == 'PLANTED-EDITABLE-CONTENT-NOT-A-LABEL'` |
| `ownership-gate-reimplemented` | R2 structural | `AssertionError: ('linkedin_profile_editor_values', '_self_assertion_on')` |
| `helper-refusal-ignored` | R2 behavioural (x2) | refusal dict compared against a success shape |
| `file-input-value-published` | R4 | `assert '' is None` |
| `password-value-published` | R5 | `assert 'PLANTED-SECRET-NOT-A-PROFILE-FIELD' is None` |
| `checkbox-token-published-as-a-value` | R6 | the record printed with a token in `value` |
| `value-substituted-like-a-name` | R8 | `assert 'I wrote <urn> about it' == 'I wrote urn:...about it'` |
| `name-left-unsubstituted` | R9 | the substituted label absent from the name list |
| `truncation-never-reported` | R10 | `assert False is True` |
| `truncation-always-reported` | R10 inverse | `assert True is False` |
| `value-chars-coerced-to-zero` | R10 / absent-is-not-zero | `assert 0 is None` |
| `index-off-by-one` | R12 | `assert [1, 2, 3, ...] == [0, 1, 2, ...]` |
| `name-chain-reordered-in-the-third-copy` | R15 | the name list resolving through `label-for` where `aria-label` should win |
| `content-marker-removed...` | R7 | `<content>` absent; the value published in the NAME slot |
| `one-of-the-ten-fields-dropped` | R11 | nine keys where ten were pinned |
| `refusal-carries-an-empty-field-list` (tool) | R3 (x3) | the refusal printed WITH `'fields': []` |
| `container-scope-widened-to-the-document` | containment | `assert 'PLANTED-OUT...HE-CONTAINER' not in ...` |
| `the-script-scrolls` | no-scroll | `assert 'scrollIntoView' not in ...` |
| `the-two-scripts-merged-behind-a-flag` | R14 / merge guard | `assert 'readValues' not in ...` |
| `the-census-reaches-the-value-reader` | census isolation | `assert 2 == 1` |
| `a-click-planted-in-the-script` | mutation scan | `.click(` returned by the scanner |

## 58. TWO CHECKS THAT COULD NOT FAIL, FOUND BY RUNNING THE MUTATIONS

Both passed under a mutation that should have killed them. Both are the same
class as the two found earlier this wave, and both are recorded because the
mutation run is the only thing that finds them.

**`index-counts-returned-rows-not-container-position` PASSED.** The mutation
swapped `index: i` for `index: out.controls.length`, and the test did not
notice -- because **the two are the same number under this loop**. Truncation
cuts the TAIL, so every row that IS pushed has the same container position as
row number. The comment beside the field claimed they "differ once maxControls
truncates", and that claim was FALSE. The comment is corrected in place, and
the mutation replaced with `index: i + 1`, which the test catches.

**`name-chain-reordered-in-the-third-copy` PASSED.** Moving the label routes
ahead of `aria-label` changed NO resolved name, because every control in the
first draft of the fixture named itself through exactly one route. The
three-way agreement test could not fail on that document. Fixed by adding one
control with `aria-label` AND a `label for=` -- two competing routes -- and by
asserting the fixture's precondition inside the test, so a future edit that
removes it fails there rather than silently going vacuous.

## 59. SIX GUARD HITS ON MY OWN WORK, AND TWICE THE COMMENT WAS THE HIT

| guard | what it caught | what changed |
|---|---|---|
| `readonly.scan_js_for_mutations` | `el.value == null` contains the mutation token for an assignment | bound the property first; the scanner is RIGHT to be crude and must not learn about equality |
| the same scanner, again | the COMMENT explaining that token quoted the token | reworded around the sequence |
| `test_no_committed_identity` | a drive-rooted Windows path as a file-input placeholder | replaced; it also proved nothing extra, since a browser will not accept a value on a file input from markup |
| `test_no_committed_identity` | an email shape -- a newline escape immediately before the tool decorator leaves a letter, an at-sign and a dotted word | built the markers from `chr(10)` |
| the same guard, again | the COMMENT explaining THAT shape quoted the shape | reworded around it |
| `test_no_committed_identity` | an invented activity urn | reused one already on `SYNTHETIC_IDS` rather than widening a privacy allowlist to buy nothing |

**Twice in one file, a comment explaining a guard tripped the guard it was
explaining.** That is not a coincidence: prose about a pattern contains the
pattern. The rule that falls out is small and general -- *when a comment must
name a forbidden shape, describe it, never quote it* -- and it is now written
beside both comments rather than only here.

Six hits across TWO guards -- the mutation scanner twice, the identity guard
four times. None was silenced. In every case the source changed, not the
guard, and the two allowlists this repo keeps (`SYNTHETIC_IDS`,
`DECLARED_PLANTS`) grew by nothing.

## 60. THE COUNTS THAT MOVED

| pin | from | to |
|---|---|---|
| `len(await mcp.list_tools())` | 34 | 35 |
| reads (`tools - SANCTIONED_WRITE_TOOLS`) | 22 | 23 |
| **writes (`writes.PERFORMABLE`)** | **10** | **10** |
| `dom.py` evaluate waivers | 10 | 11 |
| declared injected scripts | 10 | 11 |
| executed script call sites | 10 | 11 |
| suite | 2455 | 2485 |

The write count is the half that matters. **The tool that arrived is the UNDO
for a write, and it does that by reading.** A tool that made the write undoable
BY writing would move the other number and would fail the split.

## 61. WHAT THIS DOES NOT DO

* It does not restore anything. It reads. He types it back through the gate.
* It cannot pair itself with the label tool across two calls without pairing
  across two RENDERS -- `index` lines the two up, and a control that moved
  between the calls pairs wrongly. Nothing here can detect that; the tool says
  so rather than implying the pairing is free.
* It reads the FIRST RENDER and does not scroll, so a field it did not see is
  a field it cannot restore. Absent is UNKNOWN, not zero.
* It does not answer item 1's finding. The live surface says every field has
  either a value with no addressable control, a control with no readable
  value, or one value against two controls. **This reader gets the value; it
  does not conjure the control.** `update_profile_field` is still blocked on
  the aiming half, and the reconnect is what measures it.

# PART EIGHT -- THE DELETE, AND A FAILURE CLASS OF ITS OWN

## 62. `read_settings_surface` -- THE PRECONDITION, THEN THE DELETE

The wave lead ruled DELETE, conditioned on one check, and named the risk
precisely: **if `update_setting` turned out to have no settings reader at all,
that would be a much more serious finding than dead code and would change the
answer.**

It has one. Measured, both halves:

| half | what reads settings | through |
|---|---|---|
| preview / BEFORE | `writes._read_dark_mode`, reached via `_SURFACE_READS["setting_dark_mode"]` off the spec's own `state_from` | `dom.read_surface_census` on `/mypreferences/d/dark-mode` |
| `_verify_after` / AFTER | an explicit `if spec.action == "update_setting"` branch: fresh navigation to the same url, then `_read_dark_mode` again | the same census |

Neither reaches `dom.read_settings_surface`, and `_read_dark_mode`'s own
docstring says why: *"This calls `dom.read_surface_census`... A purpose-built
reader here would have been a second implementation of a chain that already
exists, declared and scanned."* No test called the old reader either -- the
only mentions anywhere were its definition, the comment in `writes.py`, and
the allowlist entry.

**Deleted:** the reader (21 lines) and `SETTINGS_LINK_PREFIX`, which had
exactly one user and died with it. Uncalled since 2026-08-31, removed
2026-09-02, recoverable from history and named in the commit.

## 63. THE FAILURE CLASS, AND IT IS NOT THE ONE THE OTHER FOUR BELONG TO

The four instances before it were **instruments failing silently** -- a reader
nothing called, a tool never run, a check that could not fire. This one is
different and the wave lead named it exactly:

> **The fact was observed and the rule was stated and the two were never
> connected, one sentence apart.**

`writes.py` said, in one paragraph:

    "a reader kept for a state nobody consults is a reader that goes stale
     unread"
    ...
    "dom.read_settings_surface remains available and is now uncalled from
     this module"

Nothing was hidden. No check failed to fire. **The premise and the rule were
both written down, by the same hand, in the same breath, and the conclusion
was not drawn.** That is a class no guard in this package was watching for,
because every guard here is built to catch something being INVISIBLE.

What caught it was a **call graph**, which cannot be talked out of a
conclusion the way a reader of that paragraph was. The corrected comment now
carries the whole story in place, so the next reader meets the failure rather
than a tidied-up module.

## 64. THE ALLOWLIST IS NOW EMPTY, AND EMPTY IS THE TARGET STATE

`UNREACHABLE_BY_DESIGN` held one entry for one day. The length pin tightened
from `<= 1` to `== 0`: **a bound with room in it is a bound nothing has to
argue with**, and zero means the next unreachable reader cannot be parked
there without somebody deliberately widening the line.

**Emptying it created the defect this file is about.** The three-rule entry
validation and the allowlisted branch of the reachability parametrisation
both became loops over nothing -- passing forever, certifying nothing. So
`test_the_entry_validation_can_still_fail` re-runs all three rules against
fabricated entries. The treatment for an empty list is not that nobody checks
the rules any more.

Three mutations, each shown failing:

| mutation | what it printed |
|---|---|
| a dead reader reinstated in `dom.py` | `read_a_reader_nothing_calls is defined in dom.py and NOTHING calls it...` |
| a REACHABLE reader put on the allowlist | `read_surface_census is on UNREACHABLE_BY_DESIGN but IS reachable -- the entry is stale` |
| one genuinely-unreachable entry added | `AssertionError: ['read_job_identity']` -- the length pin |

The first is the one that matters: it proves the deletion is **enforced going
forward**, not merely done once.

## 65. PUSH STATE, MEASURED BY `git fetch` RATHER THAN BY EITHER OF US

The wave lead's fifth correction said the remote was at `c830b91` with
`f2d612b` unpushed, and told me to use their count over mine. **A real
`git fetch origin` says the remote is at `f2d612b`.** Their push landed and
the message predates it.

Recorded because the instruction was to trust a number over an instrument,
and the instrument is cheap: `git fetch` costs nothing and settles it. Both
of our counts were built from snapshots; only one of us could re-measure
without asking, so I did.

**AND THE WAVE LEAD'S DIAGNOSIS IS BETTER THAN THE FINDING.** Their numbers
were not wrong when taken -- each was a live `git ls-remote` at the moment of
sending. **A RELAYED COUNT IS STALE BY CONSTRUCTION**, and theirs simply had
the shorter half-life. Telling me five times to prefer theirs was fixing the
wrong thing; the right instruction was *neither of us should be relaying
this.* In their words: **a count is an instrument reading with a timestamp,
and the timestamp gets dropped when the reading agrees with you.**

THE PROTOCOL, agreed 2026-09-02 and standing: **neither agent states a push
count to the other. Each fetches.** A disagreement then cannot happen,
because there is nothing to disagree about -- both parties are reading the
same remote rather than each other's memory of it.

It generalises past git. Any number one agent hands another is a reading
somebody took at a time, and the receiving agent cannot see the timestamp.
Where the measurement is cheap to retake, RETAKE IT; relay only what cannot
be re-measured.

# PART NINE -- THE AIMING PROBLEM DISSOLVES, AND WHAT IS ACTUALLY LEFT

## 66. THE WAVE LEAD IS RIGHT, AND THE PROOF WAS ALREADY ON DISK

I closed Part Seven with *"this gets the value; it does not conjure the
control -- `update_profile_field` is still blocked on the aiming half."*
**That sentence was wrong**, and the wave lead's correction is exact:

> The mismatch only exists **if `update_profile_field` is aimed by
> `my_profile`'s field names.** It does not have to be. Aim it at the control.

The four-row gap table in section "Item 1" measured `my_profile`'s
AGGREGATED fields against the editor's controls. Two of its four rows -- one
value against two controls -- are **artefacts of the mapping and vanish when
there is no mapping.** Nothing needs splitting because nothing is being split:
the caller names `First name`, and `First name` is a control.

**AND NO RECONNECT WAS NEEDED TO SETTLE THE REST.** The per-control reading
was already recorded in section 5 of this file, taken live on 2026-08-31:

    First name*        input  text  label-for  REQUIRED
    Last name*         input  text  label-for  REQUIRED
    Additional name    input  text  label-for
    Industry*          input  text  aria-label
    City               input  text  aria-label
    Country/Region*    input  text  aria-label
    School*            select       label-for  REQUIRED
    Month              select       aria-label
    Save               button       text       enabled

**Every one of the eight is an `input type=text` or a `select`, and the value
reader covers both natively** -- `el.value` for the inputs, the selected
option's TEXT for the selects. There is no `[role="combobox"]` div anywhere in
that container, which was the one shape that could have returned
`value_source: "none"` and left a control with no readable previous value.

I had that as an open worry before reading this table. It is closed by
measurement, not by optimism, and the measurement cost nothing because
somebody had already written it down. **The reload list does not grow.**

**The `select` decision turns out to be load-bearing.** Returning the OPTION
TEXT rather than `el.value` was argued from restore fidelity -- a human
re-picks what the option SAYS. Two of the eight fields are selects, so that
choice is the difference between a restore path existing for `School` and
`Month` and not existing.

**`headline` is the genuine casualty and the lead's reason is better than
mine.** Its control is named `<content>` -- named BY ITS OWN CONTENT -- so
**the anchor moves every time the value does.** An anchor that changes when
you change the thing it anchors is not an anchor. That is a narrow, permanent,
measured refusal, and it is a far better answer than "blocked on the aiming
half."

## 67. WHAT IS ACTUALLY LEFT, AND ONE ITEM IS NEW

The aiming half is closed. Three things stand between here and a performable
`update_profile_field`, and the third was not on anybody's list:

1. **IT MUST TYPE, and the mechanism exists.** `SANCTIONED_MUTATIONS` holds a
   `click` and, since 2026-09-01, a `fill` draining a `fill_plan` at a single
   call site. Six of the eight fields are `input type=text` and are reachable
   by that mechanism. This is design work, not a measurement.

2. **THE RESTORE IS A SECOND GATED WRITE, not an automatic undo.** The value
   is read at PREVIEW time; the restore is another two-call confirm carrying
   the old string. "Undoable" means HE HOLDS THE STRING and can issue a second
   approved call -- it does not mean this server can put it back on its own,
   and the preview must not imply otherwise.

3. **TWO OF THE EIGHT NEED A MUTATION KIND THAT DOES NOT EXIST.** `School*`
   and `Month` are `<select>`. **`page.fill` does not work on a select** --
   Playwright needs `select_option`, which is a THIRD entry in
   `SANCTIONED_MUTATIONS` and therefore a third thing a reviewer has to read
   and approve. So the eight split six/two, and a design that quietly assumed
   one typing mechanism covers all of them would fail on exactly the two
   fields whose previous value the reader works hardest to get right.

**AND A REQUIRED-FIELD RULE FALLS OUT OF THE SAME TABLE.** Five of the eight
are REQUIRED. A restore puts a value back, so it is safe; but a caller can
pass an empty string, and a gate that fills `""` into a required field is
asking LinkedIn to refuse a form the human already approved. The refusal
belongs at the gate, from the `required` field the LABEL reader already
returns.

## 68. THE DIAGNOSTICS, CHECKED RATHER THAN ASSUMED

The wave lead sent three and said explicitly not to conclude "probably
benign", because that reasoning has been wrong five times this week.

**`FILE_PATH_VALUE` is not undefined -- it does not exist.** `grep` returns
zero hits for the name and three for `FILE_PLACEHOLDER`, which replaced it
when `test_no_committed_identity` flagged the drive-rooted path it held. Both
of its sites execute under the suite, so an undefined name there would raise
rather than lint. The diagnostic is a stale snapshot from before the rename.

**The unresolved imports are the known Pyright `pythonpath` gap**, unchanged.

**The two unused names were fake-method parameters**, renamed `_page` and
`**_kwargs`. Renamed **in both fixtures rather than only the new one**:
`test_editor_fields.py` carries the byte-identical helper, and fixing one of
two deliberately parallel files is how they stop being parallel.

## 69. A STANDING RULE, PROMOTED OUT OF TWO COMMENTS

> **Prose about a pattern contains the pattern. When a comment must name a
> forbidden shape, DESCRIBE it -- never quote it.**

Both instances were in this wave and both were comments explaining the very
guard they tripped: one quoted the mutation-scanner's assignment token while
explaining why the code avoids it; the other quoted the address shape while
explaining why the markers are built from `chr(10)`. Neither was silenced --
the prose was reworded both times.

It belongs here rather than only beside those two comments, because the next
instance will be in a file neither of them is in.

# PART TEN -- THREE OF THE TEN COULD NOT CLICK

## 70. THE DEFECT, FOUND WHILE BUILDING SOMETHING ELSE

Three of `dom.py`'s selector builders emitted a string Playwright rejects:

    role=radio[name="Always on"][exact=true]

    Locator.count: Error: Unknown attribute "exact", must be one of
    "checked", "disabled", "expanded", "include-hidden", "level", "name",
    "pressed", "selected"

`exact` is not an attribute the role engine has. Handed to any page, it
raises.

| builder | capability | what could not happen |
|---|---|---|
| `named_role_selector` | `update_setting` | its ONLY click. Nothing at all. |
| `post_submit_selector` | `publish_post` | the submit AFTER the fill |
| `comment_submit_selector` | `comment_on_item` | the submit AFTER the fill |

**The two typing actions are the worse half.** The fill lands, the submit
raises, `perform` catches it into `click_error` -- so the text sits in his
composer with nothing posted, and the gate reports a failure. It fails SAFE.
It also cannot succeed, which is the `apply_job` class the operator ruled
against on 2026-09-01: *a check that cannot pass may never ship as though it
might.*

All nine selector builders were resolved against a real headless page. The
other six -- `save_control_selector`, `post_editor_selector`,
`comment_editor_selector`, `reaction_control_selector`,
`invite_control_selector`, `tracker_list_selector` -- are CSS or xpath and
each matched exactly one control.

## 71. WHY NOTHING CAUGHT IT, WHICH IS THE PART THAT GENERALISES

Every test compared the selector as a **string literal**:

    assert dom.named_role_selector("radio", "Always on") == 'role=radio[name="Always on"][exact=true]'

and `test_writes_nine.py`'s fake page records `page.clicks` as whatever string
it is handed, so it accepts a selector no browser would.

**NO TEST IN THIS SUITE HAD EVER GIVEN A ROLE SELECTOR TO A BROWSER.** A
selector test that never resolves the selector is a check that cannot fail on
the one thing a selector is for. Nothing had ever fired, which is exactly why
it survived.

`tests/test_selectors_resolve.py` closes it, and the half that keeps working
after today is that the list is **derived by AST**: every `*_selector`
function in `dom.py` must be resolved below or carry a checked reason on
`NOT_RESOLVED_HERE`. Fixing three selectors is worth one commit; making the
fourth impossible to add untested is worth the file.

## 72. AND THE CLAUSE'S STATED REASON WAS ALSO WRONG

The comment justified `[exact=true]` like this:

> *a substring match would let `Always on` select a control named `Always on,
> recommended`, and on a radio group the two would be different destinations*

**MEASURED 2026-09-02, against a page drawing both controls:**

| selector | matches |
|---|---|
| `role=radio[name="Always on"]` | 1 |
| `role=radio[name="Always"]` | **0** |
| `role=radio[name="always on"]` | **0** |
| `role=radio[name="always on"i]` | 1 |

The role engine matches a name **WHOLE, never as a substring**, with or
without any suffix. The clause was defending against something the engine
does not do -- spelled in a way that made every selector it built unusable.

What the `s` suffix actually buys is **case sensitivity**, which is also this
version's default. So it is the behaviour WRITTEN DOWN rather than inherited,
and that is the honest size of the reason to keep it.

**MY FIRST TEST ASSERTED THE WRONG PROPERTY** -- it pinned substring
protection, because that is what the comment claimed -- and a mutation
dropping the suffix PASSED it. The test now pins case sensitivity, which is
what the suffix does.

## 73. THE MUTATIONS, INCLUDING THE ONE THAT IS A GENUINE NO-OP

| mutation | verdict |
|---|---|
| `[exact=true]` restored | **3 failed** -- `Unknown attribute "exact"` |
| the `s` suffix changed to `i` | **1 failed** -- a lowercase name matched 1 control |
| a new `*_selector` added to `dom.py` | **1 failed** -- covered-or-declared |
| **the suffix dropped entirely** | **13 passed, and that is CORRECT** |

The last row is recorded rather than hidden. Without a suffix the engine is
already case-sensitive and whole-name in this version, so dropping `s` changes
nothing observable and no test can fail on it. **A test cannot fail on a
no-op, and writing one that appeared to would be manufacturing a check** --
the disease this file has spent the whole wave naming. The suffix is kept for
explicitness, and its docstring says exactly that rather than claiming the
suffix is load-bearing.

**AND THAT MEANS THE TEST IS THE GUARD, NOT THE SUFFIX**, which is worth
stating because it changes what a future reader must not delete. Since
case-sensitivity is already the default, the thing standing between this
package and a future Playwright that flips it is
`tests/test_selectors_resolve.py` pinning `[name="always on"]` to ZERO -- not
the `s` being present. Both that file and `named_role_selector`'s docstring
now say so in terms, so nobody removes the assertion reasoning that the suffix
covers it. **The suffix would go on looking correct while silently doing
nothing -- which is exactly the state `[exact=true]` was in for a day and a
half.**

## 73a. THE SECOND WAY A COMMENT CORRUPTS WHAT IS BUILT FROM IT

Section 69 recorded the first: **prose about a pattern contains the pattern.**
Here is the second, and it is worse because the corruption runs into the
instrument rather than into a guard's input.

The `[exact=true]` clause carried a justification nobody had measured -- that
it prevented a substring match. When the test was written to defend the fixed
selector, **it pinned substring protection, because that is what the comment
said the thing was for.** The mutation dropping the suffix passed it. The
check inherited the error instead of catching it.

> **A TEST DERIVED FROM A COMMENT TESTS THE COMMENT.**

An unmeasured claim in prose becomes the specification for the check that was
supposed to verify the code, and the loop closes with nothing on either side
having touched the running system. The fix is not "read comments
sceptically"; it is that a check's premise has to come from a MEASUREMENT --
here, four selector strings resolved against a real page, which took one
command and refuted the sentence that had stood for a day and a half.

## 74. WHAT ELSE THE SAME PROBE SETTLED

**No twelfth `evaluate` waiver is needed for the option-presence check.** I
was about to write a script for it. A locator chain answers it and returns
INTEGERS, with no option text crossing into this process:

    page.locator(sel).get_by_role("option", name=wanted, exact=True).count()

Measured: `Beta College` -> 1, `Beta` -> 0. The exactness the operator's
condition requires is the engine's, not something this package has to
implement.

**The asterisk is unresolved and is not being guessed.** Section 5's table
renders the control as `First name*` AND carries a separate REQUIRED column,
so whether the `*` is part of the accessible name is unmeasured. The design
does not need to know: the caller names a field, the gate matches it against
the LIVE control list, and refuses -- naming the controls it did see -- unless
it matches exactly one.

## 75. WHAT THIS COSTS THE THREE CAPABILITIES

Nothing has been un-shipped. The fix restores what their specs already
claimed, and the previews were always honest about what they could not verify.
But three of the ten had never been exercisable, and no reconnect was needed
to discover it -- **a local headless page and nine strings were enough**. The
reload list is unchanged at two READ tools; this was never a live-surface
question.

## 76. FAILING SAFE IS NOT FAILING CLEANLY -- THE TEXT LEFT IN HIS COMPOSER

The operator ruled on 2026-09-02, after the broken selectors were found. Both
typing actions FILL and then CLICK. For a day and a half the click could not
resolve, so the sequence was: text lands in his composer, submit raises,
`perform` catches it into `click_error`, receipt reports a failure.

**It failed SAFE. It did not fail CLEANLY.** Nothing in the receipt said the
words were still on his screen, and a reader who saw an error would reasonably
conclude nothing had happened. **A draft sitting in his UI that he did not put
there is a side effect he did not consent to, even though nothing published.**

`writes.typed_text_residue` is now in every receipt for a typing action:

| field | says |
|---|---|
| `text_was_entered` | whether the fill landed |
| `submit_was_pressed` | whether a click followed -- NOT whether it posted |
| `left_in_the_composer` | the consequence, stated as a consequence |
| `what_to_do` | go and clear it yourself |

**IT IS NOT A CLEARING MUTATION AND MUST NOT BECOME ONE.** Clearing would be a
second write to undo a failed write -- more machinery pointed at his account,
on this server's own judgement, at exactly the moment it has just demonstrated
it cannot reliably press a button. The ruling was TELL HIM. A test asserts no
clearing verb appears in the block.

**PRESENT ON THE HAPPY PATH TOO**, because a block that appeared only on
failure would make "no text was left" and "nobody checked" the same answer.
Four mutations caught: the block omitted when the submit succeeded, the helper
unwired from the receipt, `left_in_the_composer` pinned false, and a clearing
verb offered instead of an instruction.

## 77. THE TWO "UNBLOCKED" ITEMS ARE MECHANICALLY COUPLED TO THE CAPABILITY

The wave lead separated the three rulings by argument -- the `select_option`
boundary entry and the required-empty refusal as structural, the capability as
dependent on a reader that has never run live. **The argument separates
cleanly and the mechanism does not.**

`test_every_sanctioned_entry_is_actually_present` asserts

    set(readonly.SANCTIONED_MUTATIONS) == found

where `found` is what the scanner finds in the source. **A strict set
equality.** So an entry with no call site fails exactly as loudly as a call
site with no entry -- which is the guard working, and it means the permission
and the `page.select_option` call are inseparable. That call is
`update_profile_field`'s.

The only way to land the entry alone is a `select_plan` queue gated on an
EMPTY action set. That was considered and refused:

* **A permission for a call nothing can make cannot be reviewed.** The entry
  exists so a reviewer can read how the capability is used; with no use there
  is nothing to read.
* **The emptiness becomes the only guard.** A later edit adding an action to
  that set inherits the permission WITHOUT anybody re-reading the entry --
  which inverts what the allowlist is for.

The required-empty refusal has the same shape one level down: built now it is
a validator nothing calls, which is the defect
`tests/test_reader_reachability.py` exists to end.

**So both land WITH the capability, after the value reader has returned real
values once.** Recorded here rather than settled silently, because declining
an approved item is the wave lead's call to reverse.

## 78. THE INSTRUMENT: PROVING A COMMIT IS PROSE-ONLY, AND THE RULE BEHIND IT

Filed on the wave lead's ruling, and the ruling itself is the useful
distinction: *"do not extend the audit" meant do not manufacture prose to fill
an idle gap. It did not mean drop a reusable instrument on the floor.* **An
instrument that exists only in a message thread is the amnesia pattern** --
the next person to need it will not read that thread, and will reach for the
weaker version because that is what is written down.

### The instrument

Claiming a commit is documentation-only, **structurally** rather than by
reading it:

    import ast, subprocess, sys

    def strip_docstrings(tree):
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Module, ast.FunctionDef,
                                     ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:]
        return tree

    def at(rev, path):
        return subprocess.run(["git", "show", f"{rev}:{path}"],
                              capture_output=True, text=True,
                              check=True).stdout

    path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
    a = ast.dump(strip_docstrings(ast.parse(at(old, path))))
    b = ast.dump(strip_docstrings(ast.parse(at(new, path))))
    print(a == b)

**RUN WITH ITS OWN NEGATIVE CONTROL before being written down here**, because
filing an unmeasured claim about an instrument is the failure section 73a
records:

    linkedin_server/dom.py  add5212~1..add5212   True    (the prose-only commit)
    linkedin_server/dom.py  866e34f~1..866e34f   False   (the selector fix)

What it asserts is **"the module compiles to the same tree"**, not "no line
that looked like code changed". The text heuristic it replaces -- filtering
the diff hunk for non-comment lines -- is fooled by a changed line that
happens to begin with `#`, by a docstring whose content is code-shaped, and by
a reindent that moves executable lines without changing their text.

**ITS FAILURE MODE, NAMED.** It proves the parsed trees match. It says nothing
about whether the docstring change was CORRECT -- a docstring can be rewritten
into something false and this still returns True, which is exactly what
happened to `named_role_selector` for a day and a half. It answers "did
anything executable move", and only that.

### The rule, and it is worth more than the three instruments together

> **READ THE STRUCTURE, NOT THE TEXT -- BECAUSE THE TEXT IS WHAT A MISTAKE
> LOOKS LIKE.**

Three different problems this week, and in every one the textual form was
plausible, cheap, and wrong:

| problem | textual form | structural form | what the textual form missed |
|---|---|---|---|
| is this reader reachable | grep for the name | call graph over `ast.Call` | passed a docstring mention; called a dom-internal caller dead |
| are all selectors tested | an enumerated list | builders derived by AST | would have gone stale on the tenth builder |
| is this commit prose-only | filter the hunk for non-comment lines | compare dumped ASTs | a `#`-prefixed change, a reindent, a code-shaped docstring |

Each textual version would have shipped looking correct. The first passed the
fifth dead reader while inventing a sixth; the second certifies exactly the
surface that existed the day it was written; the third proves only that
nothing *resembling* code changed.

**Three instances is a pattern rather than a coincidence**, which is why the
rule is filed and not just the three tools.

# PART ELEVEN -- THE READERS RAN, AND BOTH DESIGNS WERE BUILT ON A SURFACE THAT MOVED

Both readers ran live on 2026-09-02 for the first time. **Neither result
matches its design.** Diagnosed before anything was adapted, which is the
entire reason the build waited.

## 79. THE EDITOR: THE NAME CHAINS AGREE. LINKEDIN CHANGED THE PAGE.

Two hypotheses were open: the two readers' name chains disagree, or the page
changed. **One call separated them completely** --
`linkedin_profile_editor_fields` run against the same live page, minutes after
the value reader.

**THEY AGREE, CONTROL FOR CONTROL.** Same 17 controls, same order, same names,
same `name_source` on every one. `test_the_three_name_chains_agree` is not
passing on an inadequate fixture; the chains genuinely agree, on the live page,
including on the controls that come back unnamed.

So the 2026-08-31 reading is **stale rather than wrong**: 23 controls then, 17
now, and a different set.

| 2026-08-31 | 2026-09-02 |
|---|---|
| `First name*` label-for | **`""` -- no accessible name at all** |
| `Last name*` label-for | **`""` -- no accessible name at all** |
| `School*` select label-for | gone; `Education` select label-for |
| `Month` select aria-label | gone; `Pronouns` select label-for |
| `Industry*`, `City`, `Country/Region*`, `Additional name`, `Save`, `<content>` | unchanged, same sources |
| -- | new: `Dismiss`, `All LinkedIn members`, `Write with AI`, `Learn more`, `Edit contact info`, two unnamed switches |

### What this does to the re-aiming design

**The first-name and last-name inputs have NO ACCESSIBLE NAME AND ARE
`required: true`.** Their values read perfectly -- the value reader returned
both -- and they cannot be addressed by name. That is the exact inverse of the
problem the ruling was written to solve, and it lands on two of the fields the
ruling was written to reach.

**THE AIMABLE SET IS SIX, NOT EIGHT, AND IT IS A DIFFERENT SIX:**

| field | name source | tag | value read |
|---|---|---|---|
| `Additional name` | label-for | input text | empty string |
| `Country/Region` | aria-label | input text | yes |
| `City` | aria-label | input text | yes |
| `Industry` | aria-label | input text | yes |
| `Pronouns` | label-for | **select** | yes, option text |
| `Education` | label-for | **select** | yes, option text |

**UNAIMABLE, and now for two different reasons:** `headline` because its name
IS its content, and first/last name because they have no name at all.

**THE SELECT DECISION HOLDS AND SO DOES THE `select_option` NEED** -- two of
the six are selects, and both returned their option TEXT exactly as designed.
That is the one part of the design the live surface confirmed.

**AND THE REQUIRED-EMPTY REFUSAL WOULD CURRENTLY PROTECT NOTHING**, which is
worth saying rather than discovering later: the only two `required: true`
controls in the container are the two that cannot be aimed at. It is still the
right guard -- a page that moved once will move again -- but on today's surface
it guards an empty set.

## 80. THE GATE IS NON-DETERMINISTIC, AND IT PRODUCED A SECOND FALSE REFUSAL

The first call to `linkedin_profile_editor_fields` refused:

    refused: no_self_assertion
    "the landed profile url carries no isSelfProfile=true"
    pages_loaded: 1

**An immediate retry, same code, same page, seconds later, SUCCEEDED** with
`established: true, same_member: true`. And the wave lead's run of the value
reader minutes earlier had also succeeded.

So `isSelfProfile=true` does not reliably appear on the `/in/me/` redirect.
`server._establish_self_owned_editor` fails CLOSED, which is the right
direction -- but it hands back a confident, specific refusal that misdescribes
the world, and its text invites the reader to conclude the page was not his.

**THIS IS THE SECOND FALSE REFUSAL FROM THIS GATE.** The first was on
`linkedin_profile_editor_fields`'s first-ever live call. Both were confident,
both were specific, and both were wrong about the account. A gate whose anchor
is an external query parameter is only as deterministic as that parameter, and
nothing here had measured whether it is.

## 81. THE COMPOSER: THE PREDICTION LANDED AND ITS MECHANISM WAS WRONG

    refused: name_shaped_label_present    recipients_selected: 0
    label_shapes:  {runs: 1, joined_by_to: false, tail: "", checked: false}
                   {runs: 1, joined_by_to: false, tail: "", checked: false}

**The refusal code is exactly the one predicted. The reason given for the
prediction cannot be the cause.** Measured against the shipped predicate:

    'Firstname will send message'          runs 0  -- NOT name-shaped
    'Firstname to Acme will send message'  runs 1, tail 'will send message'

(The examples above read `Firstname` rather than his actual given name. The
first draft of this section used the real one, twice, and
`test_no_committed_identity` PASSED IT -- that guard looks for emails, phones,
slugs, urns, member tokens, company ids, credentials and drive roots, and **a
bare given name is none of those**. Caught by grepping the file for the values
the readers had just returned, which is a check no test performs. The rule is
*values reach the tool result and nothing else, never the audit*, and it needs
a human sweep because the automated one cannot see this class.)

The predicted single-name label **does not trip the guard at all**, because
`_CENSUS_CAPS_RUN` needs either two consecutive capitalised words or a
capitalised word with whitespace before it -- and a name at position 0 has
neither. **Right outcome, wrong mechanism**, recorded as such rather than
claimed as a clean hit.

### What the measured numbers actually correspond to

`runs: 1, tail: ""` means a label whose LAST word is a capitalised token
preceded by a space, with no other capitalised run:

    'Write with AI'      {runs: 1, joined_by_to: False, tail: ''}
    'Send as InMail'     {runs: 1, joined_by_to: False, tail: ''}
    'Send as Message'    {runs: 1, joined_by_to: False, tail: ''}

### AND THIS IS WHY THE DISCRIMINATOR CANNOT DISCRIMINATE

**The two shapes are identical because the shape deletes exactly the token
that distinguishes them.** If the two send modes differ in a single trailing
proper noun -- `...InMail` against `...Message` -- then `runs`,
`joined_by_to` and `tail` are identical BY CONSTRUCTION. Identical output is
not an anomaly to be tuned away; it is the specified behaviour of a shape
whose job is to delete capitalised words, applied to a pair that differs only
in one.

**NO ADJUSTMENT OF THE EXTRACTOR FIXES THIS.** The information needed to tell
the modes apart is precisely the information the guard exists to withhold.
That is a design contradiction, not a bug, and it was invisible until the
surface was read.

The design assumed the modes differed STRUCTURALLY -- one name against two
names joined by "to". They do not appear to.

**WHAT IS NOT ESTABLISHED, and must not be stretched:** whether these two
controls are the send-mode radios at all. `checked: false` on both, where the
census recorded one radio checked, is unexplained. They could be the radios in
a different render, or two other checkable controls entirely. **The shapes are
consistent with several readings and settle none of them.**

**THE INMAIL QUESTION IS STILL OPEN.** Nothing in this reading says whether
either mode spends a credit. It was made a precondition precisely so that it
would not be answered by inference, and it has not been answered.

## 82. THE ALL-OR-NOTHING REFUSAL, WHICH IS A REAL DESIGN QUESTION

Two name-shaped labels withheld **every** field, including the message body's
`aria-label` -- an unrelated control carrying nobody's name. So `send_message`
is blocked by a guard protecting something else.

**MY READING: the container-wide refusal is right and the PREDICATE is what is
wrong.** Per-label withholding would publish fifteen names from a container
that has just produced evidence this server misjudged it -- and "the labels I
could read look safe" is not a reason to trust the ones I could not.

The defect is upstream. `looks_name_shaped` fires on any label ending in a
capitalised word after a space, which on a real UI includes `Write with AI` --
a control this server has now READ, BY NAME, in the profile editor, on the
same account. **The predicate cannot tell a product feature from a person**,
and on a surface where LinkedIn brands things in title case that is not an
edge case.

Fixing the predicate is a change to a privacy gate and is the wave lead's to
rule. It is recorded here and NOT adjusted.

## 83. THE COMPOSER: THE DESIGN WAS RIGHT AND THE READER IS AIMED AT THE WRONG CONTAINER

The wave lead asked which controls the two shapes describe, before anything
touches the extractor. **The census answers it, and the answer inverts the
conclusion.**

`linkedin_surface_census(surface="messaging_compose")`, badge read ZERO first
through `linkedin_new_messages` off `/feed/`, settle verdict `consistent`,
77 controls expected and 77 read.

### The send-mode radios exist, and they are EXACTLY the shape the design predicted

    shape "<redacted> will send message"                 radio  label-for  checked TRUE
    shape "<redacted> to <redacted> will send message"   radio  label-for  checked false

**One name, versus two names joined by "to".** That is precisely the
structural difference `shape.describe_name_shaped` was built to detect. The
design's model of this surface was CORRECT and is confirmed by an instrument
that has never been able to publish those labels.

### And `read_compose_fields` cannot see either of them, by CONTAINMENT

    both radios          containers: {"none": 1}    -- no form ancestor
    dom.MESSAGE_SEND_NAME          'Send'
    dom.MESSAGE_CONTAINER_SELECTOR 'form'

The reader anchors on `Send` and scopes to that control's nearest `form`
ancestor -- `form#0`. **The radios are in no form at all.** They are outside
the container by construction, and no adjustment to the predicate, the
extractor or the shaping would ever bring them into view.

The two shapes it DID return therefore describe two OTHER controls inside
`form#0`. The census shows exactly two candidates there: a pair of buttons,
`name_source: aria-label`, `aria_expanded: false`, count 2, whose names the
census also redacts.

**So the reader is not mis-shaping the radios. It has never read them.**

### THE THIRD FINDING IS A PRIVACY DEFECT, AND IT MAKES THE FIX ORDER MATTER

    looks_name_shaped('Firstname will send message')             False
    looks_name_shaped('Firstname to Acmecorp will send message')  True

`_CENSUS_CAPS_RUN` matches either two consecutive capitalised words, or a
single capitalised word **preceded by whitespace**. A name at position 0 has
neither. So the guard **fails OPEN on the CHECKED mode** -- the default one,
the label most likely to carry his name and nothing else.

**RE-POINTING THE READER AT THE RIGHT CONTAINER WITHOUT FIXING THE PREDICATE
WOULD PUBLISH HIS NAME VERBATIM.** The container-scope bug is currently the
only thing preventing that, which is not a design and cannot be relied on.

The same defect corrupts the discriminator's other half: for that label
`describe_name_shaped` returns `runs: 0` and a "name-free tail" of **the whole
string, name included**. The tail is name-free only for the mode that happens
to trip the guard.

### What the discriminator would do if both halves were fixed

It would work. `runs: 0` against `runs: 1` separates the two modes cleanly,
and the checked flag says which is default. The mechanism is sound; it has
simply never been pointed at its subject, and one of its two outputs is
unsafe on the subject it was built for.

### THE INMAIL QUESTION IS STILL OPEN, and this reading narrows it without answering it

`InMail` on this page is a **button, `role=button`, `aria-checked=false`,
count 1, container `none`** -- sitting beside `Focused`, `Unread`, `Starred`,
`Connections` and `Jobs`, all with the same shape. **Third independent
corroboration that it is a conversation FILTER PILL and not a send affordance.**

No balance, allowance or credit count appears anywhere in 77 controls.

**One unopened door is named rather than guessed:** a button `Open send
options`, `aria_expanded: false`, inside `form#0`. It has never been opened
and its contents are unmeasured. That is where a send-mode or credit
affordance would plausibly live, and this server has not looked.

**And the composer has the disabled-when-empty signal** the comment surface
lacks: `Send` is `disabled: true` on an empty composer with no recipient. That
is the same measured transition `publish_post`'s submit gate uses, and it
would be available to a future `send_message` gate.

### One disclosure about how this reading was taken

My session's census schema is STALE -- it documents five surfaces where the
committed code carries nine -- so `messaging_compose` is a key my own tool
description does not list. The server process is current (`2be66b8`) and
accepts it; the surface is sanctioned in committed code and the wave lead had
loaded the same page minutes earlier; the badge precondition was read first
and was zero. **It went THROUGH the gate rather than around it**, which is the
distinction that separates this from the workaround refused in section 82 --
importing the module and launching the browser from a script.

## 84. RULING 1 BUILT: THE GATE NOW SEPARATES ABSENT FROM FALSE

The wave lead's ruling, and it is this week's own lesson turned on the gate
that produced two false refusals:

> `readable: false, error: null` again -- the distinction between *the reader
> ran and the answer is no* and *the reader could not ask*.

`_self_assertion_state` reads THREE states where `_self_assertion_on` reads
two. The boolean is UNCHANGED and keeps its two other callers; the three-way
reading sits beside it.

| state | meaning | what the gate does |
|---|---|---|
| `true` | LinkedIn asserts the profile is his | proceed |
| `false` | LinkedIn asserts it is NOT | **refuse at once**, `not_self_profile`, one page load, no retry |
| `absent` | the parameter did not ride at all | **retry once**, then `self_assertion_unreadable` |

**A STATEMENT IS NOT RETRIED AND AN UNREAD QUESTION IS.** Asking a settled
question twice is a page load spent on nothing; re-asking one that was never
answered is what a reader does. `_SELF_ASSERTION_ATTEMPTS = 2` is the
measurement rather than a preference -- on 2026-09-02 the first load came back
absent and the immediate second came back true -- and it is BOUNDED because an
unbounded retry turns a LinkedIn change into a page-load loop against his
account.

**The absent refusal now says what it does not know**, in terms: *THIS IS NOT
A STATEMENT THAT THE PROFILE IS NOT YOURS -- LinkedIn did not answer the
question, and this server will not turn an unread assertion into a claim about
your account.* The old text invited exactly the opposite conclusion, twice, on
the first live call of two different tools.

`pages_loaded` is now derived from the loads actually made rather than the
literal `1` and `2`, so a retried call reports two profile loads and a
refusal before the editor still reports that the editor was never fetched.

**Three mutations, each shown failing:** absent collapsed back into false (3
failed); the retry removed (`assert 1 == 2`); a settled `false` retried like an
absent one (`pages_loaded` 2 where 1 is the contract). And a new test the old
suite had no way to express -- `isSelfProfile=false`, LinkedIn answering NO --
which could not be written while both states shared one code.

## 85. WHAT IS NOT BUILT, AND WHY, SO THE LEDGER IS HONEST

Rulings 2, 3 and 4 arrived in the same message and are NOT in this commit.

* **RULING 2 -- narrow the composer read** to the dispatch radios by role and
  radio group, and the body textbox by role. Correct and not started. It is a
  reader rewrite whose subject sits OUTSIDE the container the current reader
  scopes to (section 83), so it is a new aiming design rather than an edit.
* **RULING 3 -- the gitignored identity-value file** with a loud skip. Correct
  and not started.
* **RULING 4 -- the required-empty refusal.** The coupling recorded in section
  77 still holds: built now it is a validator nothing calls, because its
  caller is the re-aimed capability. The wave lead's argument -- *"it is
  reachable, it is called on every write"* -- is true of the guard ONCE THE
  CAPABILITY EXISTS, and presupposes it. Flagged rather than built, for the
  second time, on the same mechanism.

Nothing fires. No `confirm_token`.
