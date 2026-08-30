# The remaining LinkedIn writes -- built, gated, and mostly refusing

Date: 2026-08-30. Repo `linkedin`, branch `master`. Baseline `000e87f`.

The standing ruling this executes, verbatim: *"Whatever is technically possible,
I want you to achieve all those things."* Shown the gap list and asked, the
operator said **"do all"**. The POLICY bucket is dissolved: a refusal survives
only if the thing is IMPOSSIBLE with a measurement behind it, or if performing
it is HIS decision and the gate is what defers it to him.

---

## 0. Headline

| what | outcome |
|---|---|
| new tools registered | **EIGHT** |
| of those, able to act | **ONE** -- `linkedin_follow_company` |
| built, gated, and REFUSING | **SEVEN**, each with a live read and a named next measurement |
| capabilities with no tool at all | ONE -- endorsing, re-examined and still IMPOSSIBLE AS SPECIFIED |
| read-boundary patterns added | **ZERO**. All six frozen AST digests unchanged |
| forbidden substrings removed | **ZERO** |
| new click call sites | **ZERO**. `SANCTIONED_MUTATIONS` is the two entries it was |
| live census runs performed | **THREE** (`feed`, `profile`, `settings`), plus one search and one job read |
| defects found and fixed | **THREE** -- the job-card parser, a wrong enumeration in a refusal, a name that under-declared a write |
| full suite | **1920 passed, 0 failed** |
| writes performed | **NONE.** No `confirm_token` was passed to anything, by anyone, at any point |

**`_state/session.json` is byte-identical.** Proof in section 8.

---

## 1. What the live measurement bought, and why it came first

`linkedin-nine` reported ZERO live runs because `mcp__linkedin__*` never
resolved for it. Those tools DID resolve for this wave, so the whole shape of
the answer changed: **every selector below is a string read off the operator's
own account on 2026-08-30, not one inferred from a sibling or a convention.**

Three census calls, one search, one job read. Nothing clicked. Rate discipline
held throughout (the server enforces 3s between loads).

The single most useful finding is one the offline wave predicted and could not
confirm: **LinkedIn writes toggle state into the accessible name.**
`Reaction button state: no reaction` appeared 3 times on `/feed/` and 8 times on
`/in/me/` -- eleven controls, every one in the OFF state. That is the same
convention as `Follow`/`Following` and `Click to stop following <Page>`, and it
is what makes reacting the closest of the seven to being performable.

---

## 2. THE NINE, one at a time

Each entry says: what was MEASURED, what was NOT, the reversibility finding with
its evidence class, and what firing it would cost him.

### #1 publish a post -- `linkedin_publish_post`. **BUILT, REFUSING.**

**Measured, live on `/feed/`:** one composer control, accessible name
`Start a post`, drawn as `div[role=button]` with **no href** -- so the composer
is a MODAL and is not reachable by navigation. Two publish routes ARE
url-addressed and both are real anchors: `Write article` -> `/article/new/` on
the feed, and `Create a post` -> `/preload/sharebox/` on his profile.

**Not measured:** `contenteditable == 0` across the whole page. **The editor
itself has never been observed**, and neither has whatever control publishes.
This server does not click a control it has not seen. Separately, neither
publish address is on the read allowlist.

**Reversibility: STILL-UNKNOWN, evidence class UNVERIFIED.** Each post draws an
overflow control -- `Open control menu for post by <him>`, measured 8 times --
and it renders `aria-expanded="false"`. **Its items have never been read**, so
whether LinkedIn offers Delete on a post is not established here. The
notifications precedent is that an unopened overflow menu is not evidence about
what is inside it. Deleting is permanently forbidden in this server regardless.

**What firing it would cost him:** a post is a BROADCAST. His profile reports
275 followers, and LinkedIn's own analytics on that page show past posts
reaching 103, 308 and 1,284 impressions. Deleting one -- if it can be deleted --
removes a row; it does not un-read what several hundred people have read, and it
does not recall the notification. **It is also the one artefact here a current
employer sees without looking for it.**

**What would complete it:** open the composer once and record the accessible
name of its editable node and of its publish control. The click that first SHOWS
the composer publishes nothing; only the second one does. So this is measurable
with him watching -- unlike endorsing -- and simply has not been measured.

### #2 comment on an item -- `linkedin_comment_on_item`. **BUILT, REFUSING.**

**Measured, in BOTH of its shapes, which are not the same control:**

| surface | shape | count |
|---|---|---|
| `/feed/` | `Comment`, `tag: button`, `name_source: text`, no href | 3 |
| `/in/me/` | `Comment`, `tag: a`, href shape `.../feed/update/<urn>/` | 8 |

The second is the only place a target key for a feed item has ever been seen.

**Not measured, and there are three:** the permalink family `/feed/update` is on
`_FORBIDDEN_URL_SUBSTRINGS`, checked before the allowlist and NOT shortened for
a write; `contenteditable == 0`, so the comment box has never been observed; and
the exact form of a feed urn is unknown, because the census substitutes `<urn>`
out before counting so that a measurement cannot publish an identifier.

**Reversibility: STILL-UNKNOWN, UNVERIFIED.** No comment has been opened and no
comment overflow menu read.

**What firing it would cost him:** a comment is public, attributed to him, and
sits under SOMEBODY ELSE'S item -- published to their audience rather than his
followers, notifying them, and staying attached to their content.

**What would complete it:** a boundary ruling on `/feed/update/<urn>/`, and a
capture of the opened comment box. The cheap half first: open the overflow menu
on one of his OWN existing comments and read whether a delete exists.

### #3 react to an item -- `linkedin_react_to_item`. **BUILT, REFUSING. The closest.**

**Measured:** `aria-label="Reaction button state: no reaction"`, count 3 on the
feed and 8 on his profile. LinkedIn writes the toggle state into the name, so
**the OFF-to-ON anchor is measured** and the direction can be read off the very
button a reaction would move. `Open reactions menu` sits beside it,
`aria-expanded="false"`, contents never observed.

**Not measured:** the ON-state label. All eleven controls read `no reaction`,
because nothing on either surface had been reacted to. **This is the identical
position `unsave_job` has been in since August, and it takes the identical
answer: the missing half is not guessed.** `Reaction button state: like` and
`... liked` are both plausible and neither has been seen. Separately the target
cannot be aimed: the permalink is forbidden, and the feed renders several items
at once, so choosing one there would be choosing by position.

**Reversibility: STILL-UNKNOWN, UNVERIFIED -- and this is the one most tempting
to call reversible.** A control whose accessible name reports a STATE is almost
certainly a toggle. Almost certainly is not a measurement.

**What firing it would cost him:** a reaction notifies the author and can
surface in his own network's feed. Removing it takes back the row, not the
notification.

**What would complete it:** a boundary ruling on the item permalink. The anchor
is already in hand, which is true of none of the other six. The ON label is
settled by the first supervised reaction -- and 8 of the 11 measured controls
are on his own posts, so he can take that measurement on his own content.

### #4 edit a profile field -- `linkedin_update_profile_field`. **BUILT, REFUSING.**

**Measured, live, and it REFUTES a claim this server was shipping.** Profile
editors ARE addressed by url. Three are ordinary `<a href>` anchors on his own
profile, each count 1:

- `https://www.linkedin.com/in/<member>/edit/intro/`
- `https://www.linkedin.com/in/<member>/edit/forms/summary/new/`
- `https://www.linkedin.com/in/<member>/overlay/contact-info/`

and the live page carries **2 forms** where every tracked profile fixture
carries **0**. A fourth route, `/profile/edit-basic-info`, is anchored from the
settings surface.

**Not measured:** `/edit/` is on the forbidden list, so two of those addresses
are refused twice over; and `contenteditable == 0`, so no field inside any
editor has ever been observed. Even given the address there is nothing measured
to type into.

**Reversibility: STILL-UNKNOWN, UNVERIFIED.** The editors have never been
opened, so no field, no save control and no previous-value affordance is known.
An address is not an undo, and nothing here records the previous value.

**What firing it would cost him:** his profile is what recruiters read, and they
read it continuously -- it reports 29 profile views. An edit reverted an hour
later was live for an hour. LinkedIn also notifies a network about some profile
changes, which this server has not measured and would not control.

**What would complete it:** a boundary ruling on the `/in/<member>/edit/` family
and a census of one opened editor -- specifically whether it renders the CURRENT
value, which is what makes an edit revertible by hand at all.

### #5 endorse a skill. **IMPOSSIBLE AS SPECIFIED. Re-examined once, ruling unchanged.**

The instruction was to re-check that this was aimed right, under the privacy
constraint, without collecting third-party data. That re-check happened and it
was free: the `profile` census run for #4 read **222 controls on his own live
profile**, and **not one of them names an endorsement**. No `/endorse` href
appears anywhere in its 28 distinct href shapes. That is a LIVE measurement on
top of the offline one (0 endorse controls across 13 fixtures, 0 shaping
blindness, 0 on his own skills surface).

**The specific question asked -- is there a surface listing his own connections'
skills?** No such surface was found among anything this server may read. The
routes the two censuses surfaced are `/in/<member>/details/featured/`,
`/in/<member>/recent-activity/all/`, `/mypreferences/d/unfollowed`
("People you unfollowed") and `/feed/followers/`. None lists a connection's
skills. `/mynetwork/` is refused at the gate for the pending-invitation badge,
and its sub-surfaces are refused by the substrings `invitation` and `/connect`.

**So the ruling stands and its ground is now a measurement rather than a
policy.** You cannot endorse yourself; the only surface that would carry the
control is a third party's profile; and loading one is a MEASURED emission --
`linkedin_who_viewed_me` reads the receiving end of exactly that signal, 365
days back on his Premium Career account. **No third-party data was collected to
establish this.**

`PERMANENTLY_FORBIDDEN["endorse_or_recommend"]` previously read *"a statement
ABOUT ANOTHER PERSON, which is not his to automate"* -- which is POLICY, and was
already overtaken by the operator's own 2026-08-25 ruling that an endorsement is
a gift to its recipient. **That reason is replaced by the measurement**, and a
new entry, `load_a_third_partys_profile_to_measure_a_control`, states the rule
it rests on rather than restating it.

### #6 change a setting -- `linkedin_update_setting`. **BUILT, REFUSING.**

**Measured, live:** every individual setting IS its own address. 33 links, and
they include `/mypreferences/d/settings/language`,
`/mypreferences/d/settings/autoplay-videos`, `/mypreferences/d/dark-mode`,
`/mypreferences/d/categories/privacy`, `/profile/edit-basic-info`. The surface
that lists them carries **0 forms, 1 button, and 0 checkboxes, selects or
switches**: it hands out addresses and switches nothing.

**Not measured:** no page below the index has ever been loaded, so no toggle has
ever been observed. `/mypreferences/d/categories/` and `/settings/` are both
forbidden, which between them refuse every page carrying a value.

**Reversibility: STILL-UNKNOWN, UNVERIFIED -- and a single verdict for "a
setting" would be false whatever it said.** Those 33 addresses are not one kind
of thing.

**What firing it would cost him -- read this before any future ruling here.**
**Two of the 33 addresses are `Close and delete account` and `Hibernate
account`**, and they sit in the same url family as `Dark mode`. A permission
written for the FAMILY would carry those with it. **A setting must be admitted
BY NAME or not at all.**

### #7 connection invitation -- `linkedin_send_invitation`. **BUILT, REFUSING. Side effect AVOIDED.**

The brief asked whether a route exists that avoids the measured side effect.
**It does, and here is how that was established.** The obvious surface is
`/mynetwork/`, refused because loading it consumes the pending-invitation badge.
The `profile` census -- run for #4, at no extra cost -- reported **9 controls
whose shaped accessible name is `<redacted> to connect`**, `tag: button`,
`name_source: aria-label`, on `/in/me/`. That is a page this server already
loads and which carries no such counter.

**So this tool never touches `/mynetwork/`.** Its preview loads his own profile
and counts. The side effect is declared in the tool's own docstring, in
`writes._NINE_REFUSALS`, and in `linkedin_server_info`'s `known_side_effects` --
so it reaches a caller at call time rather than only in this document.

**Not measured, and both halves are real.** First, **the label IS the other
person's name.** LinkedIn writes it into the aria-label; the census blanks a
name before counting it; reading the full label to aim a click would mean
collecting a stranger's identity to populate a confirm block. The suffix is the
whole of what may be known without paying that, and a suffix selects all nine
controls, not one. The reader is written to match:
`dom.read_invitation_surface` returns a COUNT and never reads the label -- not
read-then-shaped, not read-then-dropped. Second, `/invite`, `invitation` and
`/connect` are all forbidden urls.

**Reversibility: STILL-UNKNOWN, UNVERIFIED, and unmeasurable from here.** The
sent-invitations manager's address contains `invitation` and is forbidden, so
this server has never seen it and holds no evidence either way.

**What firing it would cost him:** an invitation is a REQUEST TO A REAL PERSON
and lands as a notification with his name on it. Withdrawing one -- if LinkedIn
permits it -- removes it from a pending list; it does not un-notify. And a
quieter cost: **LinkedIn restricts accounts whose invitations are frequently
ignored**, so this is the one action here whose repetition has a consequence for
the account itself. Nothing readable reports that limit.

**What would complete it:** not a measurement -- a decision. Whether this server
may hold ONE named person's identity long enough to show it to him and aim one
click. That is about him and a stranger, and it is his to answer.

### #8 follow a company -- `linkedin_follow_company`. **PERFORMED.**

The only one of the eight that can act, and the change is one of AUTHORITY
rather than of measurement.

**Measured:** the control is `button[aria-label="Follow"]` when not following
and `"Following"` when following -- measured on a live posting in August, class
attributes byte-identical between the two states and `aria-pressed` absent, so
the accessible name is the whole of the signal. The surface is the posting page,
**already on the read allowlist**, so no boundary moved.

**The blocker, re-measured today and still true.** `linkedin_job_detail` on job
`4447654264` returned `company_url: https://www.linkedin.com/company/onarrival-travel/`
-- **a SLUG, not a numeric id.** That settles the cheaper of the two routes the
previous audit named, and it fails. `linkedin_unfollow_company` addresses rows by
NUMERIC company id, so this server cannot aim its own unfollow at what a follow
creates. Manage Pages also renders about 20 rows of a stated 58 with no
pagination.

**Why it now ships anyway.** "The undo cannot be aimed" is a REVERSIBILITY fact,
and this design has a place for one: `reversible_by`, which the gate prints in
full before he confirms. Holding the action back AS WELL is deciding for him on
a ground he can read for himself. Reversibility class **REVERSIBLE**, evidence
class **VERIFIED-BY-INSTRUMENT** -- LinkedIn writes the inverse action into the
control's own name on three surfaces -- with `reversible_by` saying plainly:
*him, by hand, in LinkedIn's own interface; NOT this server.*

**The prerequisite, which is why this was not a one-line change.** Adding an
action to `PERFORMABLE` alone would have been a defect. `_live_control` had no
branch for follow, so gate 5 would have fallen through to the SAVE family's --
re-reading the save button and calling that a corroboration of the follow
control. **That is the identical bug apply carried until 2026-08-26**, and it is
invisible from outside because the fall-through returns a plausible answer about
the wrong element. A branch was written first, plus a guarded
`dom.follow_control_selector` that refuses any label
`shape.FOLLOW_LABELS` has not seen, plus a `_verify_after` branch.

**Verification is the weakest in this design and says so.** The control redraws
in place and is re-read there. The stronger shape is unavailable for a specific
reason: an unfollow's preview reads Manage Pages and therefore holds a BEFORE
count; a follow's preview reads the POSTING -- one page load, state and action
sharing a rendering -- so no before-count exists, and an absent row on a partial
list is not evidence.

**What firing it would cost him:** a follow can surface in his network's feed.
The data is restorable and the impression is not. And the undo is his to perform
by hand.

### #9 send a message / InMail -- `linkedin_send_message`. **BUILT, REFUSING. Side effect NOT PAID.**

**This preview does not open messaging, and that is the design rather than a
shortfall.** Loading `/messaging/` is measured TWICE to redirect into one
specific conversation of LinkedIn's own choosing -- so the load itself opens
somebody's thread -- and the nav badge counts new-since-last-visit and resets
when the tab is opened. **A gate that opened messaging in order to describe that
cost would have spent it, on a third party, to produce a sentence.**

So it reads the BADGE off a page already open -- that number IS the counter a
load would consume. Measured 2026-08-30: `Messaging, 0 new notifications`, on
both the feed and the profile. `dom.read_messaging_badge` shapes the label on
the way out.

**This wave did NOT call `linkedin_open_messaging`.** The cost lands on somebody
who is not him, so it is his to spend. That tool pays it knowingly and its own
name says so.

**Not measured:** any composer. `/messaging/compose` is on the forbidden list --
it is the entry that SURVIVED when the blanket messaging ban was narrowed in
August so he could read his own inbox, and it was kept for exactly this.

**Reversibility: STILL-UNKNOWN, UNVERIFIED.** No thread opened for this purpose,
no message control read.

**What firing it would cost him:** a message is read by a person, usually within
a day, and arrives as an email as well as a notification. **This is the most
irreversible-in-audience action in the whole design**, and unlike an application
it is addressed to a named individual rather than a company's process. It may
also **spend an InMail credit -- UNMEASURED rather than denied**: messaging
outside his network uses InMail, that allowance is finite on Premium Career, and
this server has never read his balance because `/premium/my-premium/` is not on
the read allowlist. A send could consume a finite resource whose size is unknown
to the thing spending it.

**What would complete it:** he calls `linkedin_open_messaging()`, whose result
already carries the send-surface counts, then
`linkedin_open_messaging(message_filter="inmail")`. Plus a boundary ruling on the
composer.

---

## 3. The shape all seven share, and why it is not a stub

Each of the seven is a full `WriteSpec` behind the **existing** two-call gate.
No second gate was invented. What makes them refuse is structural rather than
behavioural:

**None holds a `url_template`.** `writes.mint` refuses a grant at ISSUE for a
surface-less action, so **no confirm token for any of them exists anywhere in
the process.** That is stronger than "the tool declines to act": there is
nothing to confirm. The preview returns the WARNING block -- `to_confirm: None`,
`performed: False` -- exactly as `set_open_to_work` has since August.

**Each performs a REAL LIVE READ.** Six new `state_from` branches load a page
that was ALREADY on the read allowlist -- the feed, his own profile, the
settings index -- count what bears on the capability, and hand the gate a state
read seconds ago. The lazy build is a constant string saying "cannot"; the
failure mode of the lazy build is documented three times in this package, where
a stored refusal outlived its reason and was then read as current.

**Content is part of the target.** `_composite_target` canonicalises a comment
as `<item> :: <text>`, a post as its text, a setting as `<setting> = <value>`.
The existing `consume` compares the WHOLE target string, so a token is bound to
the exact words the preview showed -- with no new mechanism. Changing the text
between preview and confirmation produces *"token was minted for target X, not
Y"* for free. Four refusals protect it: an empty component, a component over
3000 characters, a component containing the separator, and a control character.

**A target this server has never read unshaped is not validated, and says so.**
`item_urn` and `member` are accepted as opaque strings. The census substitutes
`<urn>` and `<member>` out before counting, deliberately, so the exact form is
unmeasured -- and a normaliser enforcing `urn:li:activity:<digits>` would be
doing precisely what this package refuses to do with a selector: asserting a
shape nobody has seen.

---

## 4. The boundary did not move, and that is checkable

| frozen structure | before | after |
|---|---|---|
| `_ALLOWED_URL_PATTERNS` | `0edd01ead91a89ea` | unchanged |
| `_FORBIDDEN_URL_SUBSTRINGS` | `fcb931b0eaee5b84` | unchanged |
| `_MUTATION_CALL_PATTERNS` | `23aece1483afdee9` | unchanged |
| `JS_MUTATION_TOKENS` | `d47e30b67c583c1b` | unchanged |
| `SANCTIONED_MUTATIONS` | `b84365077cba813b` | unchanged |
| `<functions>` | `199939f7998e8d48` | unchanged |

All six verified by `tests/test_readonly_boundary_invariant.py` passing
unmodified. `WRITE_VERBS` gained `react` -- it is not a frozen structure and no
function body changed, which is why `<functions>` did not move.

**No new click call site.** Every one of the seven is unperformable and
`follow_company` reuses the single existing `page.click` in `writes.perform`.

**No injected script.** All seven new readers use Playwright locator chains, so
`test_readonly.py`'s `INJECTED_SCRIPTS` needs no new entry and the JS mutation
scanner has nothing new to scan.

---

## 5. Three defects found, and a live boundary finding

### 5.1 The job-card parser put a location in the company field

**Observed live:** a `linkedin_search_jobs` row came back with
`"company": "Bengaluru, Karnataka, India (On-site)"` and `"location": null`.

**Mechanism.** `harvest_linked_cards` finds the entity lockup by an `img[alt]`
ending in `" logo"`, and reads `logo_name` AND `meta_line` only inside
`if (lockup)` -- so one missing alt costs BOTH anchors at once and the row
reverts to positional reading. With exactly one content line after the title,
company takes it and nothing is left for the location.

**Fix.** An anchor beats a position, and a positional company with nothing after
it is not a company. The refused line is routed to `location`, so a refusal
corrects one field instead of costing two.

**The regularity it rests on was COUNTED**: 42 parses across 21 distinct rows of
the three tracked search fixtures at both layouts, plus the tracker fixture and
11 hand-written card texts. Zero violations -- the guard refuses nothing that
currently works. Two of the five new tests are genuine reproductions and were
shown failing against the unchanged parser.

**Not fixed, recorded:** with `logo_name` present but `meta_line` absent on a
one-line card, `location` is null before and after. `harvest_linked_cards` never
produces that combination, so it is unreachable from the live surfaces.

### 5.2 A refusal named the wrong specs

`PERMANENTLY_FORBIDDEN["delete_or_withdraw_anything"]` gained a note saying five
specs depend on it -- and named *"a post, a comment, a reaction, an invitation
and a message"*. Measured: react_to_item does NOT cite it (its `reversible_by`
rests on the unmeasured ON-state label), and apply_job DOES. **The count was
right while both ends of the list were wrong**, which is exactly the error a
count cannot catch. Corrected, and the test that pins it is written by name
rather than by number.

### 5.3 A tool name that under-declared a write

`readonly.name_implies_write("linkedin_change_setting")` returned **False** for a
sanctioned write. Adding `"change"` to `WRITE_VERBS` was **measured before being
attempted**: across every registered tool description it appears as a whole word
in SIX, three of them READS using it to describe the boundary ("has no way to
change anything about the posting"). Arming the docstring check on three correct
tools is how a guard gets switched off.

**So the tool was renamed instead**, to `linkedin_update_setting` --
`update` is already a write verb AND on the frozen conservation baseline, and
the new name announces the write the old one concealed.
`linkedin_edit_profile_field` moved the same way for a different reason: `edit`
announces a write but is not on the baseline, so `test_a_sanctioned_write_cannot
_evade_the_law_by_being_renamed` refused it.

**Read the direction of these renames.** The loophole that test exists to close
is renaming until a write passes as a READ. This is the opposite: the guard
reported an under-declaring name and the name was corrected to declare more.
`"react"` WAS added to `WRITE_VERBS`, measured at exactly one occurrence -- zero
false positives.

### 5.4 A LIVE BOUNDARY FINDING: the second gate guards the request, not the landing

`linkedin_surface_census(surface="settings")` was asked for
`https://www.linkedin.com/mypreferences/d/` and came back with

```
"source_url": "https://www.linkedin.com/mypreferences/d/categories/account"
```

**LinkedIn redirects the settings index onto a category page -- and the category
family is precisely what was added to `_FORBIDDEN_URL_SUBSTRINGS` that same
morning, as the "second, independent gate" behind the newly widened allowlist.**

Nothing was breached: the page read is the settings index's own account section,
which is what the ruling intended to permit, and the census clicks nothing. What
is false is an inference a reader would reasonably draw -- that the forbidden
list keeps this server OFF those addresses. It keeps this server from ASKING for
them. `assert_read_url` gates the requested url and the landed url is never
re-checked.

**Pinned rather than fixed, deliberately.** Re-checking the landed url would
break two working tools BY DESIGN: `linkedin_open_messaging` is built to land on
a thread url, and this census is built to land wherever the settings index sends
it. Quietly widening the allowlist to admit the category page instead would undo
the ruling that put it on the denylist. So the honest artefact is
`test_the_settings_index_is_permitted_and_its_landing_page_is_not`, shown failing
on the mutation it catches.

---

## 6. The two corrections the brief named

### 6.1 `_WHY_NOT_PERFORMED["set_open_to_work"]` -- CORRECTED, narrowed, tested

It read: *"its editor is not addressed by a url at all -- 237 urls and 37 payload
paths measured across five profile captures, zero of which reach it."*

**Every number is still true of the captures and the conclusion is false of the
site.** The live profile carries three editor anchors and 2 forms where every
fixture carries none.

**Narrowed to what survives:** profile editors ARE url-addressed -- and none of
those anchors, nor any other href on the page, reaches the OPEN TO WORK audience
editor. That one remains modal-only, and the click that would first show it is
the first that could change it.

Pinned by `test_the_open_to_work_reason_no_longer_makes_the_claim_the_live_page
_refutes`, **shown failing against the restored original text**:

```
>       assert "not addressed by a url at all" not in lowered
E       AssertionError: assert 'not address...a url at all' not in 'its editor ...yer can see.'
E         'not addressed by a url at all' is contained here:
E           its editor is not addressed by a url at all -- 237 urls and 37 payload paths
E           measured across five profile captures, zero of which reach it. ...
FAILED tests/test_server_surface.py::test_the_open_to_work_reason_no_longer_makes_the_claim_the_live_page_refutes
```

### 6.2 `linkedin_search_jobs` parser -- REPRODUCED, FIXED, PINNED

Section 5.1. Commit `f57c184`.

### 6.3 The server `instructions` string

It ended: *"There is no message, no connection request, no InMail, no profile
edit, and no post -- do not look for them or suggest they exist."* Every clause
became false the moment those tools registered -- and worse than false, because
that paragraph is what an assistant answers FROM, so a stale denial there is
repeated to him as fact.

It now names all seven tools, states that **none of them can act**, carries the
two side-effect warnings (`send_message` does not open messaging;
`send_invitation` does not open `/mynetwork/`), states the follow asymmetry, and
states that endorsing is impossible as specified. The old sentence is QUOTED
inside its correction, which is this package's convention -- so the test asserts
the stronger property: it appears exactly once, inside a frame saying it is what
the paragraph used to say.

---

## 7. What was NOT done, and why

- **`linkedin_open_messaging` was not called.** Its cost lands on a third party.
  Named as the next measurement for #9 instead; it is his to spend.
- **No third party's profile was loaded**, for #5 or anything else.
- **`/mynetwork/` was not loaded.** The invitation control was found on a
  surface that costs no badge.
- **No boundary was widened.** Several capabilities are blocked by
  `_FORBIDDEN_URL_SUBSTRINGS`, and shortening a denylist is a ruling nobody has
  made. Each refusal names the exact address that would have to be admitted.
- **Reposting was not built.** It was not among the nine. Its former entry in
  `PERMANENTLY_FORBIDDEN` was narrowed to it alone, with its measurement
  (`Repost` is a button with `aria-expanded="false"`; its menu has never been
  opened) rather than the taste argument that covered four capabilities.
- **NO WRITE WAS PERFORMED.** No `confirm_token` was passed to anything.

---

## 8. Run record

**Full suite: 1920 passed, 0 failed.** `venv\Scripts\python.exe -m pytest -q`,
Python 3.13.14, with all code and test files committed.

Baseline at `000e87f` was **1766** (measured by collection, not carried). The
delta is +154, of which 10 are the job-card parser slice and 144 are the
capability wave -- 137 of those in the new `tests/test_writes_nine.py`.

Note the mechanism this repo already documented: some checks parametrise over
`git ls-files`, so **committing this document adds test cases**. The number
above is the tree before it; the docs commit's own count is recorded in section
9.

### `_state/` -- byte-identical

```
_state/session.json   size=7813
                      sha256(first 32)=f0892e35688868faef6a3525e54b93e4
                      mtime=2026-08-26 00:41:24.087579
```

Identical to the values the brief specified. **Nothing in this wave read, wrote
or opened `_state/`.**

**The Chrome profile directory DID move, and that is reported rather than filed
under "untouched".** Five MCP reads went through the running server -- three
censuses, one search, one job detail -- and the server launches the browser
against the persistent profile to serve them. That is the sanctioned path every
read tool uses; **no browser was launched from a script**, which is the standing
rule. The profile survived: `Last Version` still reads `151.0.7922.34` and there
is no `.CHROME_DELETE` marker, so the downgrade migration did not fire.

### Committed blobs

Every blob in both commits verified LF-only and pure ASCII after committing. No
`Co-Authored-By` and no session trailer on either.

---

## 9. The nine, plus the corrections, as a table

| # | capability | tool | state | what would complete it |
|---|---|---|---|---|
| 1 | publish a post | `linkedin_publish_post` | **DELIVERED AND REFUSING** | capture the opened composer: the editable node's name and the publish control's |
| 2 | comment on an item | `linkedin_comment_on_item` | **DELIVERED AND REFUSING** | a boundary ruling on `/feed/update/<urn>/`, plus a capture of the comment box |
| 3 | react to an item | `linkedin_react_to_item` | **DELIVERED AND REFUSING** -- anchor already measured | a boundary ruling on the item permalink; the ON label follows from one supervised reaction on his own post |
| 4 | edit a profile field | `linkedin_update_profile_field` | **DELIVERED AND REFUSING** | a boundary ruling on `/in/<member>/edit/`, plus a census of one opened editor |
| 5 | endorse a skill | none | **IMPOSSIBLE AS SPECIFIED**, re-examined | nothing this server may do. Only he can, on a profile he chooses to open |
| 6 | change a setting | `linkedin_update_setting` | **DELIVERED AND REFUSING** | a boundary ruling on ONE NAMED setting page -- never the family |
| 7 | connection invitation | `linkedin_send_invitation` | **DELIVERED AND REFUSING**, badge cost avoided | a decision, not a measurement: may this server hold one named person's identity to aim one click |
| 8 | follow a company | `linkedin_follow_company` | **PERFORMED** | nothing. The undo remains hand-only and the gate says so |
| 9 | send a message / InMail | `linkedin_send_message` | **DELIVERED AND REFUSING**, thread cost not paid | he calls `linkedin_open_messaging`, plus a boundary ruling on the composer |
| C1 | `_WHY_NOT_PERFORMED` false claim | -- | **CORRECTED AND NARROWED**, shown failing on the original text | -- |
| C2 | `linkedin_search_jobs` parser | -- | **REPRODUCED, FIXED, PINNED** | -- |
| C3 | server `instructions` | -- | **TRUE OF THE SHIPPED SERVER** | -- |

**Seven capabilities are delivered-and-refusing.** For six of them the single
missing measurement is a BOUNDARY RULING on a named address -- which is the
operator's to make, not a measurement anybody can take. For #1 it is a capture
he can authorise at no cost to anyone. For #3 the anchor is already in hand and
only the target is missing.

### Commits

```
f57c184   fix(job-card): a lone line after the title is a location, never a company
          2 files, shape.py + tests/test_job_search_fixture.py

050349f   feat(writes): the seven that refuse, and follow_company that does not
          8 files: dom.py, readonly.py, server.py, writes.py and four test files,
          including the new tests/test_writes_nine.py

<this document's own commit follows immediately>
```

**Neither is pushed.** This repository is PUBLIC and the push is the lead's,
after a PII scan.
