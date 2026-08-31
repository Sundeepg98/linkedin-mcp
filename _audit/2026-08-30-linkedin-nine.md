# The nine unmeasured LinkedIn surfaces -- rulings, measurements and refusals

Date: 2026-08-30. Repo `linkedin`, branch `master`, baseline `eb518c6`.

The standing ruling this executes: *"Whatever is technically possible, I want you
to achieve all those things."* Every gap ends in ONE of three buckets:

* **CAN** -- measured reachable, with the measurement.
* **IMPOSSIBLE** -- refused by the platform, WITH the measurement that
  establishes it. Never "probably can't".
* **UNMEASURED** -- honest, and a DEBT rather than a decision. Every entry here
  names the exact next probe that would settle it.

A fourth outcome appears below and it is not a bucket: **REFUSED AT THE GATE**.
That is a decision, it is fully evidenced, and it is a successful outcome rather
than a gap -- see the next section for what the gate is.

---

## 0. Headline

| what | outcome |
|---|---|
| new census surface keys added | ONE (`settings`), after a written ruling |
| new census surface keys REFUSED at the gate | TWO -- `/mynetwork/` and messaging, both on measured badge behaviour |
| candidate surfaces NOT added for a different reason | ONE -- a company page. Its gate ruling came back MARGINAL rather than failing, and what actually stopped it is that the live measurement could not be run. Kept distinct from the two above on purpose: a refusal and a deferral are not the same answer. |
| live census runs performed | **ZERO** -- the linkedin MCP server was never exposed to this session. See section 6. |
| defects found and fixed | TWO, both shown failing first: a name leak in the census shaper, and a forbidden-substring entry that matched nothing LinkedIn serves |
| capabilities that moved out of UNMEASURED | ONE (#5, endorsing) -- to IMPOSSIBLE-AS-SPECIFIED, on a measurement |
| full suite | **1730 passed, 0 failed.** Baseline is 1705, not the 1703 this wave was briefed with -- see section 9, where the two-test discrepancy turns out to be a mechanism rather than an error |

**Nothing was performed on the operator's account.** No write tool was called,
with or without a `confirm_token`. No page was loaded and no browser was launched
BY THIS WAVE, and `_state/session.json` is byte-identical.

The Chrome profile DIRECTORY did change during the window, and that is reported
rather than filed under "untouched": a Playwright chromium is live against it,
and process ancestry puts it under a second linkedin MCP server owned by a
DIFFERENT `claude.exe` session. Evidence, and the proof the profile was not
damaged, in section 9.

---

## 1. THE GATE, written down as a test

The precedent is already in the code and it is the whole standard. Notifications
is deliberately NOT a census surface, because loading `/notifications/` clears
LinkedIn's unread badge -- measured, irreversible, and documented on
`linkedin_notifications`, which is the tool that pays that cost knowingly because
reading the list is the point of it. A census would pay the same cost to learn
what controls a row carries. **A census is not worth a side effect.**

Generalised into something that can be applied one surface at a time:

* **Q1 -- CONSUMPTION.** Does the surface carry, or feed, an unseen / unread /
  pending counter that the load itself consumes?
* **Q2 -- EMISSION.** Does loading emit a signal another person or organisation
  can observe?
* **Q3 -- MUTATION.** Does the load change a value the account holds?

**A YES to any one refuses the key.** A key is admitted only on three NOs, each
with evidence.

### 1.1 Where the evidence can come from, given the gate runs BEFORE the load

This is the hard part of the gate and it is worth being explicit, because the
obvious way to answer Q1-Q3 is to load the page, and that is precisely the act
the gate exists to authorise. Four classes of pre-load evidence were used, in
descending strength:

* **E1 -- a MEASURED sibling.** This package has already measured two surfaces in
  the nav-badge family and both cost a badge. That is a fact about the family,
  not a guess about a page.
* **E2 -- the RECIPROCAL instrument.** Where this server can read the RECEIVING
  end of a signal, the signal is measured. `linkedin_who_viewed_me` is the case:
  it exists, it returns rows, and every row is somebody who loaded a profile and
  produced a durable record the profile's owner can read 365 days later. That
  measures profile-view emission from the far end, without emitting one.
* **E3 -- the product's own published surface.** LinkedIn Page admins are given
  visitor analytics. That a surface exists is a fact about what a load feeds.
* **E4 -- STRUCTURAL ABSENCE.** The surface has no counter for a load to consume.
  This is the weakest class -- an argument from absence -- and it is used ONCE
  below, for settings. It is stated as DERIVED, not verified, and it is written
  with its own falsifier: name the badge, and the ruling is wrong.

**The burden sits on the ADDITION, not on the refusal.** A derived risk is enough
to refuse a key; only evidence is enough to admit one. That asymmetry is why
three of the four candidates below are refused and the reasoning for each refusal
is shorter than the reasoning for the one admission.

---

## 2. THE FOUR SIDE-EFFECT RULINGS, one at a time

### 2.1 `/mypreferences/d/` -- the settings index. **ADMITTED.**

| | ruling | evidence |
|---|---|---|
| Q1 consumption | NO | E4. This surface carries no badge. Nothing in LinkedIn's chrome counts unseen settings, so there is no counter for a load to spend. FALSIFIER: name a settings badge and this ruling is void. |
| Q2 emission | NO | Settings is a private surface. It displays his own values to him; no other party is shown that he opened it. |
| Q3 mutation | NO | The index RENDERS a list of sections. Changing a setting requires a toggle, and the census clicks nothing -- that is asserted in `test_the_census_script_carries_no_mutating_token` and `test_the_script_never_scrolls`, which predate this wave. |

**The one real hazard, and it is already handled.** LinkedIn interposes a re-auth
challenge in front of parts of settings. When it does, the landed url carries
`/checkpoint/`, which is already in `config.AUTHWALL_MARKERS`, so
`assert_not_authwall` turns it into a reported failure rather than a silent
half-read. That is a safe failure mode, not a side effect.

**Evidence class: DERIVED, not VERIFIED-BY-INSTRUMENT.** Nobody has loaded this
page. The first live call IS the measurement, and if the Q1 ruling is wrong it is
wrong irreversibly. That is stated plainly rather than smoothed over, and it is
the reason the permission is anchored as narrowly as it is.

**What was admitted, exactly.** One anchored pattern,
`^https://www\.linkedin\.com/mypreferences/d/?$` -- the INDEX, no query string,
no sub-path. The toggles live on `/mypreferences/d/categories/<name>` and those
are refused twice: they miss the anchored pattern, and they now carry a forbidden
substring (section 5.2).

### 2.2 `/mynetwork/` -- connection invitations. **REFUSED.**

| | ruling | evidence |
|---|---|---|
| Q1 consumption | **YES** | E1. `/mynetwork/` carries the pending-invitation badge. This package has MEASURED two members of that badge family and both reset on load: notifications (`linkedin_notifications` -- "loading this page cleared LinkedIn's unread notification badge. Unavoidable -- LinkedIn marks the list seen when it serves the page") and messaging (`linkedin_open_messaging` -- the nav badge "counts new-since-last-visit and resets when the tab is opened"). |
| Q2 emission | **unmeasured, and the cost lands on someone else** | Whether an invitation marked seen is visible to its SENDER has never been measured. That uncertainty argues for refusing, not for proceeding: this repository's own test for the policy bucket is whether the cost lands on somebody who is not him. |
| Q3 mutation | not reached | Q1 already refuses it. |

**This is a DERIVED refusal and that is legitimate.** The badge-reset claim for
`/mynetwork/` specifically is inference from the family, not a load of that page.
Under the asymmetry in section 1.1 that is exactly enough: a third member of a
family whose other two members both cost a badge does not get admitted on the
hope that it is the exception.

Pinned as a test rather than left as a comment:
`test_the_three_surfaces_refused_on_a_side_effect_ruling_are_absent`.

### 2.3 Messaging. **REFUSED, and this is the strongest refusal of the four.**

None of it is inference. Every line is already measured and already in the code.

| | ruling | evidence |
|---|---|---|
| Q1 consumption | **YES** | The messaging nav badge "counts new-since-last-visit and resets when the tab is opened" -- stated on `linkedin_open_messaging`, and `linkedin_new_messages` is the tool that reads that badge. |
| Q2 emission | **YES, to a third party** | `/messaging/` DOES NOT STAY ON A LIST. LinkedIn redirects it into ONE SPECIFIC CONVERSATION of its own choosing -- measured twice, and the reason `readonly.py` carries the thread-url pattern at all. So a census of this key OPENS SOMEBODY'S THREAD. Whether that sends them a read receipt is recorded on that tool as an honest unknown, believed unmeasurable from outside after three attempts. |
| Q3 mutation | not reached | Q1 and Q2 both refuse it. |

**A measurement is not worth a stranger's read receipt.**

**And it does not need one.** The census docstring already names the escape hatch
for exactly this situation: *"If that surface ever has to be measured, do it by
censusing a page that is already being loaded for another reason, not by adding a
key here."* `linkedin_open_messaging` IS that page. It already loads messaging
for a purpose the operator chose, and it already counts the send surface it finds
there -- editable nodes, form elements, and controls whose names match the
vocabulary this server refuses. See #9 in section 3.

### 2.4 A company page (`/company/<slug>/`). **NOT ADDED. The gate came back MARGINAL, and that is not why.**

| | ruling | evidence |
|---|---|---|
| Q1 consumption | NO | A company page carries no unseen counter of his. |
| Q2 emission | **YES, but weak and NON-IDENTIFYING** | E3. LinkedIn Page admins are shown visitor analytics -- page views, unique visitors, aggregated visitor demographics. A load feeds that. It does NOT name him: unlike a member profile, a company Page does not report who viewed it. |
| Q3 mutation | NO | Nothing on his account changes. |

So the gate does not fail this surface. It does not cleanly pass it either, and
the honest word is MARGINAL.

**The reason it was not added is a different one, and it is worth stating
separately so it is not mistaken for a safety verdict.** The live measurement
could not be run this session (section 6). Adding an anchored pattern to a
deliberately frozen navigation allowlist, in a PUBLIC repository, and shipping it
having never once exercised it against the surface it was written for, is a
widening with nothing behind it. **A widened boundary with no measurement behind
it is worse than the debt.** The debt is filed in #8 with its exact next probe.

**What a company page would actually buy, for the record, because it is not
nothing.** `dom.unfollow_control_selector` addresses a followed Page by its
NUMERIC id, and finds the row by requiring a descendant
`a[href*="/company/<digits>/"]`. A job posting names its employer by SLUG. So the
missing piece for #8 is a slug-to-id resolution, and a company page is the
obvious place it would be found. That makes this the most valuable of the three
surfaces not added -- which is why it is filed as a debt with an address rather
than as a refusal.

---

## 3. THE NINE

### #1 -- publish a post. Surface `/feed/`. Bucket: **UNMEASURED.**

The census key `feed` EXISTS and is admitted; nothing blocked this but the
absence of a live run. The instrument named in the server's own
`not_yet_measured` is exactly right and unchanged: *enumerate the composer
controls on `/feed/`, which this server already loads as a corroborating auth
check and has never read for this purpose.*

**Next probe, exactly:** `linkedin_surface_census(surface="feed")`. Read
`counts.contenteditable`, `counts.forms` and `counts.file_inputs` first -- a
composer is a contenteditable node, and the offline pass in section 4 found
`contenteditable == 0` on all thirteen tracked fixtures, so any non-zero on the
live feed is the finding. Then read `control_shapes` for a shape matching
`/start a post|share|photo|video/i`.

### #2 -- comment on an item. Surface `/feed/`. Bucket: **UNMEASURED.**

Same surface, same single probe as #1, and settled by the same capture. Look for
a control whose shape names a comment box, and for a SECOND contenteditable
distinct from the composer.

Carried forward unchanged because it is the part that matters if this is ever
built: a comment is public and attributed to him, so the preview must show the
exact text before anything is posted.

### #3 -- react / like an item. Surface `/feed/`. Bucket: **UNMEASURED.**

Same capture again. This is the one the census shaper was BUILT around -- the
canonical leak case in `tests/test_surface_census.py` is `React Like to <member>'s
post` -- so the shape to look for is already known, and a repeated count of it is
the measurement.

Cheapest of the three to build, and the only one that is reversible.

### #4 -- edit a profile field. Surface `/in/me/`. Bucket: **UNMEASURED, but narrowed by an offline measurement.**

The census key `profile` EXISTS. What is new today is offline evidence about what
that census will find, from the tracked sanitised fixtures (section 4):

* `profile_topcard.html`: 13 buttons, 11 links, **0 contenteditable, 0 forms**,
  6 controls whose name matches `/(edit|add|update|change|manage)/i`.
* `profile_topcard_hydrated.html`: 14 buttons, 19 links, **0 contenteditable, 0
  forms**, 6 editor-ish controls.

So an editor on the profile page is a MODAL, not an inline form -- consistent
with the existing Open-To-Work finding (237 urls and 37 payload paths across five
profile captures, zero of which reach an editor). **That is not proof it cannot
be done; it is proof it is not reachable BY NAVIGATION.** Modals open by
clicking.

**Next probe, exactly:** `linkedin_surface_census(surface="profile")` on the LIVE
page, and for each control whose shape matches `/(edit|add)/i` record whether
`has_href` is true. `has_href == false` means modal-only, which is the answer that
decides whether this is a navigation problem or a click problem.

### #5 -- endorse a skill. Surface: another member's profile. Bucket: **IMPOSSIBLE AS SPECIFIED**, and this one MOVED today, on a measurement.

**The measurement.** All thirteen tracked fixtures were censused offline for any
control whose shaped name or href matches `/endorse/i`. Result: **0 hits, across
every fixture.** Critically, `profile_skills.html` -- HIS OWN skills surface, the
one page `/in/me/details/skills/` renders -- carries 7 controls, of which 0 are
buttons and 7 are links, and **not one names an endorsement**.

That zero is falsifiable rather than merely absent: the pass also measured
SHAPING BLINDNESS, counting cases where the RAW string matched `/endorse/i` but
the shaped string did not. Endorse blindness is **0 of 13**. Nothing was hidden by
the shaper. (For contrast, editor blindness was 9, which is why #4 above is
reported as narrowed rather than settled.)

**So the specification is self-defeating, and now with evidence.** You cannot
endorse yourself; `/in/me/` therefore cannot show the control; and it does not.
Measuring the control REQUIRES loading a third party's profile.

**And loading a third party's profile is a measured emission -- E2, from this
server's own instrument.** `linkedin_who_viewed_me` exists, returns rows, and
reaches back 365 days on his Premium Career account. Every row in it is somebody
who loaded a profile and left a durable record its owner can read most of a year
later. That is not a guess about what a profile view does; it is this package
reading the receiving end of exactly that signal.

**Ruling: refused at the gate.** Censusing a stranger's profile would put HIM in
that stranger's "who viewed your profile" list, for no reason except a
measurement, and the cost lands entirely on the third party. It is refused on the
same principle as notifications and for a stronger reason.

**What is NOT being claimed.** The platform does not refuse this. LinkedIn
endorsements exist and work. What is established is narrower and it is what the
bucket name says: **impossible as specified** -- impossible to measure from any
surface this server may read, with a written reason why the only surface that
would show it is one it should not load for this purpose.

**Next probe, if the operator ever wants it settled:** he loads one profile of a
person who has consented, in his own browser, and reads whether the endorse
control carries an href or opens a modal. That keeps the emission a thing he
chose, which is the only form in which it is his to spend. This server should not
be the one to spend it. Note also that the policy bucket was dissolved on
2026-08-25 with the ruling that "an endorsement is a gift to the person receiving
it, not an extraction from them" -- that ruling is about PERFORMING an
endorsement, and it is untouched here. This is about MEASURING one, which costs
the third party a profile view and gives them nothing.

### #6 -- read / change settings. Surface `/mypreferences/d/`. Bucket: **UNMEASURED, and the means of measuring it now exists.**

Two things were false before today and both are fixed:

1. The server's `not_yet_measured` said *"/settings/ is on the forbidden
   substring list and has never been loaded"*, which reads as "it is blocked".
   **It is not.** Measured against the real guard: `"/settings/"` matches
   NEITHER `/mypreferences/d/` NOR `/psettings/` -- the character before
   `settings/` in the latter is a `p`. Both were refused, but by the ALLOWLIST
   alone, with no second gate behind them. Full measurement in section 5.2.
2. There was no way to read it. There is now: `surface="settings"`.

**Next probe, exactly:** `linkedin_surface_census(surface="settings")`. Enumerate
the sections; for each, record whether it is url-addressed (`has_href == true`,
`href_shape` names the category) or modal-only. That is the answer to "which
settings are reachable at all", and it is the input to any decision about
whether reading a setting -- let alone changing one -- is worth building.

**Note what the census will NOT reach, by design:** the category pages carrying
the toggles. That is the ruling in 2.1, not an oversight.

### #7 -- connection invitations. Surface `/mynetwork/`. Bucket: **UNMEASURED, and it will stay that way.**

**Refused at the gate** -- the full ruling is section 2.2. The surface carries the
pending-invitation badge; this package has measured that badge family resetting
on load twice; and the residual cost lands on the people whose invitations would
be marked seen.

**Filing this as a debt would be dishonest**, because a debt implies somebody
should pay it, and the ruling is that nobody should. It is recorded here so the
next person meets a decision instead of a hole. If it is ever revisited, the
thing that would change the ruling is a MEASUREMENT that `/mynetwork/` does not
reset its badge -- and taking that measurement requires resetting the badge.
That circularity is the same one that closed out the notifications question, and
it resolved the same way.

**One thing worth knowing, since it is free:** `/mynetwork/invitation-manager/`
is refused by the forbidden substring `invitation`, and `/invite` and `/connect`
are on that list too. So even a loosened allowlist cannot reach the invitation
surfaces. That was already true and is not a change.

### #8 -- follow a company. Surface: a company page. Bucket: **UNMEASURED. The debt has an address.**

The follow CONTROL is already measured, on two surfaces this server may read:

* On a job posting -- `dom.FOLLOW_CONTROL` is
  `button[aria-label="Follow"], button[aria-label="Following"]`, and the offline
  pass finds 1 follow hit on `job_detail.html`, `job_detail_hydrated.html` and
  `job_detail_following_hydrated.html`.
* On Manage Pages -- `dom.FOLLOWED_PAGE_BUTTON` is
  `button[aria-label^="Click to stop following "]`, and the offline pass finds 10
  such rows on `manage_pages_following.html` and 19 on its hydrated sibling.

**The blocker is unchanged and is not the control.** It is the KEY. A posting
names the employer by SLUG; `dom.unfollow_control_selector` requires a NUMERIC
id and finds the row by a descendant `a[href*="/company/<digits>/"]`; nothing
measured resolves one to the other.

One refinement the offline pass adds, stated narrowly so it is not overread: on
Manage Pages the follow BUTTON ITSELF carries no key -- no href, no `data-*`
attribute holding a 5+ digit run. The numeric id is on the ROW's anchor, not on
the button, which is exactly why the selector is written to scope the button to
its row. Nothing here contradicts `linkedin_followed_companies`.

**Next probe, exactly.** Two options, in order of preference:

1. **Cheapest, and it stays inside the existing boundary:** call
   `linkedin_job_detail` on one posting and read whether the employer link on it
   carries a numeric `/company/<digits>/` href anywhere, rather than only the
   slug form. If it does, #8 is solved with no boundary change at all. This
   should be tried FIRST and it was not tried today only because it needs the
   MCP server.
2. If it does not: add `^https://www\.linkedin\.com/company/[A-Za-z0-9\-_%]+/?$`
   to the allowlist and census it, on the MARGINAL gate ruling in section 2.4 --
   and only after running it once, so the widening ships exercised.

### #9 -- send a message / InMail. Surface: messaging. Bucket: **UNMEASURED, and it should be measured WITHOUT a new key.**

**Refused as a census key** -- the full ruling is section 2.3, and it is the
strongest of the four because every element of it is already measured and already
written in this package.

**But the capability itself is NOT refused, and the route to measuring it already
exists.** `linkedin_open_messaging` loads that page for a reason the operator
chose, and its result already carries the send-surface counts: editable nodes,
form elements, and controls whose names match the vocabulary this server refuses.
That is the census, taken on a page already being loaded for another reason,
which is precisely what the census docstring prescribes for a surface too
expensive to hold a key.

**Next probe, exactly:** `linkedin_open_messaging()` -- with `include_names`
left at its default False, which it must be, since nothing about this question
needs a correspondent's name. Read the send-surface counts in the result. A
non-zero contenteditable count is the finding for "is a composer rendered". Then
`linkedin_open_messaging(message_filter="inmail")` for the InMail half, which
activates the one sanctioned pill and reports `active_filter`.

**Note the cost is real and is HIS to spend, not this session's:** every call to
that tool opens somebody's thread. The tool is honest about it in its own name.
It was not called today.

---

## 4. The offline instrument, and what it bought

Live measurement was unavailable, so the tracked, sanitised fixtures were
censused OFFLINE -- stdlib `html.parser` approximating
`dom.CENSUS_CONTROL_SELECTOR`, with every accessible name and href put through
the package's real `shape.census_shape` and `shape.census_href_identifies_entity`
before being written down. No raw name or href appears in the output. Nothing
launched a browser. Thirteen fixtures, 151 buttons and 234 links.

Report: `_audit/_scratch/slice-fixture-census.md` (quarantined, gitignored).

| fixture | buttons | links | contenteditable | forms | endorse | follow | editor | compose |
|---|---|---|---|---|---|---|---|---|
| `profile_skills.html` | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| `profile_topcard.html` | 13 | 11 | 0 | 0 | 0 | 0 | 6 | 0 |
| `profile_topcard_hydrated.html` | 14 | 19 | 0 | 0 | 0 | 0 | 6 | 0 |
| `manage_pages_following.html` | 10 | 20 | 0 | 0 | 0 | 10 | 0 | 0 |
| `manage_pages_following_hydrated.html` | 21 | 40 | 0 | 0 | 0 | 19 | 0 | 0 |
| `job_detail.html` | 10 | 16 | 0 | 0 | 0 | 1 | 0 | 0 |
| `job_detail_hydrated.html` | 10 | 16 | 0 | 0 | 0 | 1 | 0 | 0 |
| `job_detail_following.html` | 3 | 23 | 0 | 0 | 0 | 0 | 1 | 1 |
| `job_detail_following_hydrated.html` | 15 | 24 | 0 | 0 | 0 | 1 | 0 | 0 |
| `notifications.html` | 22 | 12 | 0 | 0 | 0 | 0 | 6 | 0 |
| `jobs_tracker_row.html` | 11 | 6 | 0 | 0 | 0 | 0 | 2 | 0 |
| `profile_views_analytics.html` | 11 | 20 | 0 | 0 | 0 | 0 | 0 | 2 |
| `profile_views_analytics_hydrated.html` | 11 | 20 | 0 | 0 | 0 | 0 | 0 | 2 |
| **TOTAL** | **151** | **234** | **0** | **0** | **0** | **32** | **21** | **5** |

Three things this bought, none of which needed a page load:

* **#5 is settled** -- 0 endorse controls anywhere, 0 shaping blindness on that
  hunt, and 0 on his own skills surface specifically.
* **#1/#2/#4 are narrowed** -- `contenteditable == 0` and `forms == 0` on every
  single fixture, so any non-zero on a live feed or profile is a real finding
  rather than noise.
* **A live privacy defect was found** -- section 5.1.

**One anomaly, recorded not smoothed:** `job_detail_following.html` contains the
substring "follow" ZERO times in its whole 38,788 bytes, against 3 in its own
`_hydrated` sibling and 3 in plain `job_detail.html`. Its 0 follow hits are not a
shaping artefact -- the markup is not there. Anything costing follow behaviour
against that file as "the following-state surface" is costing against a fixture
that does not carry the state. Not acted on; flagged for whoever owns those
fixtures.

---

## 5. Two defects found, both shown failing before being fixed

### 5.1 The census shaper leaked a name -- in the exact label this package pins a selector against

`census_redact_rare` blanks a run of TWO OR MORE capitalised words in a shape
seen once. The blind spot: a name is only caught when it sits BESIDE another
capital.

Reproduced against the shipped code before anything was changed:

```
LEAK | count=1 | 'Click to stop following Acme'  -> 'Click to stop following Acme'
LEAK | count=1 | 'Connect with Prince'           -> 'Connect with Prince'
ok   | count=1 | 'Follow Acme'                   -> '<redacted>'
ok   | count=1 | 'Message Madonna'               -> '<redacted>'
```

`Follow Acme` and `Message Madonna` are two ADJACENT capitals, so the run rule
always caught those -- and every example anybody had written by hand happened to
be one of them. `Click to stop following <name>` is not: its only other capital
is `Click`, four lowercase words away.

**That template is not hypothetical.** It is literally `dom.FOLLOWED_PAGE_BUTTON`
-- `button[aria-label^="Click to stop following "]` -- so it is the label this
package is most certain to meet. The offline pass confirms it on real markup: 10
rows on `manage_pages_following.html` published as `Click to stop following
<Name>` with the name INTACT wherever the name was a single word, while two-word
names in the same table correctly became `<redacted>`. (Those particular names
are sanitised placeholders, so nothing leaked here -- but the census runs on the
LIVE feed and profile, and it would have.)

**Fix:** `_CENSUS_CAPS_RUN` gains a second alternative -- a single capitalised
word preceded by whitespace. A capital at the START of a shape is the control's
VERB (`Follow`, `Following`, `Save`) and must survive, or the census loses the
one thing it exists to report. A capital arriving mid-string, after lowercase
words, is not a verb.

**Shown failing first**, against the pre-fix rule:

```
FAILED tests/test_surface_census.py::test_the_cap_removes_a_one_word_name_the_run_rule_cannot_see[Acme]
FAILED tests/test_surface_census.py::test_the_cap_removes_a_one_word_name_the_run_rule_cannot_see[Prince]
FAILED tests/test_surface_census.py::test_the_cap_removes_a_one_word_name_the_run_rule_cannot_see[Madonna]
E       AssertionError: 'Prince' survived as 'Connect with Prince'
E       AssertionError: 'Madonna' survived as 'Message from Madonna today'
3 failed, 2 passed
```

The 2 that passed are the CONTROL and the RESIDUAL, and both must pass in both
states -- see below.

**The residual gap, pinned as known rather than left to be rediscovered.** A
shape that is EXACTLY one capitalised word and nothing else still survives:
`census_redact_rare("Gridwell", 1) == "Gridwell"`. It has to. `Follow` is that
same shape and is the single most useful row a follow census returns, and nothing
about the STRING separates them. What covers it in practice is structure --
`census_href_identifies_entity` blanks any control linking to the entity it names
-- and the uncovered case is a bare one-word button with no href at all. Pinned
by `test_a_one_word_shape_with_no_href_is_a_KNOWN_residual`.

### 5.2 A forbidden substring that matched nothing LinkedIn serves

`"/settings/"` has been on `_FORBIDDEN_URL_SUBSTRINGS` since the beginning, and
the module documents that list as *"a second, independent gate"* and *"belt and
braces: a future pattern edited too loosely still cannot reach these"*.

Measured by importing the real guard and calling it (report:
`_audit/_scratch/slice-guard-probe.md`, 20 urls, 7 allowed, 13 refused):

| url | `is_read_url` | refused by |
|---|---|---|
| `https://www.linkedin.com/mypreferences/d/` | False | **the allowlist** |
| `https://www.linkedin.com/psettings/` | False | **the allowlist** |
| `https://www.linkedin.com/settings/` | False | forbidden substring `/settings/` |

LinkedIn's settings live at `/mypreferences/d/`; the legacy address is
`/psettings/`, which does not contain `/settings/` because the character before
`settings/` is a `p`. **The only address that entry ever caught is one LinkedIn
no longer serves.** The net refusal held throughout -- nothing was ever reachable
that should not have been -- but for the settings family there was no second gate
at all, and this wave has now deliberately loosened the allowlist, which is
exactly the situation a backstop exists for.

**Fix:** `/mypreferences/d/categories/` and `/psettings/` added to the forbidden
list. `/settings/` KEPT -- it costs nothing, and an address LinkedIn stopped
serving is one it can start serving again. Verified after the change:

```
ALLOW   https://www.linkedin.com/mypreferences/d/
REFUSE ALLOWLIST  https://www.linkedin.com/mypreferences/d/?x=1
REFUSE SUBSTRING  https://www.linkedin.com/mypreferences/d/categories/account
REFUSE SUBSTRING  https://www.linkedin.com/psettings/
REFUSE ALLOWLIST  https://www.linkedin.com/mynetwork/
REFUSE ALLOWLIST  https://www.linkedin.com/company/example-co/
```

### 5.3 Two new boundary checks, and the gap in the freeze they close

The AST digest freeze answers *"did the boundary change"*. It cannot answer
*"which way"*, and for a DENYLIST that is the only question worth asking: adding
a substring refuses more, deleting one makes an address reachable, and
re-baselining a digest is the identical edit in both cases. This wave re-baselines
that dict for the third time, which is itself the argument.

* `test_the_forbidden_list_has_only_ever_grown` -- a ROSTER of every substring
  ever on the list, asserted as a SUBSET of the live tuple. Growth needs no edit;
  a deletion cannot pass without one.
* `test_no_previously_forbidden_address_became_readable` -- nine real ADDRESSES,
  put through the real guard. This is the one that would have caught 5.2: a
  roster check on the STRING `/settings/` passed every day for the life of this
  repository while the surface it was named for had no second gate.

Both shown failing on the exact mutations they catch. Deleting `"/psettings/"`
from the boundary:

```
E  AssertionError: these substrings left the forbidden list: ['/psettings/'].
   Each one was a refusal somebody wrote deliberately. Removing one is a
   boundary change, not a tidy-up.
FAILED tests/test_readonly.py::test_the_forbidden_list_has_only_ever_grown
```

Widening the allowlist to admit the two surfaces this wave refused -- which is
precisely the edit a future agent would make:

```
E  AssertionError: https://www.linkedin.com/mynetwork/ became readable.
E  AssertionError: https://www.linkedin.com/company/example-co/ became readable.
FAILED tests/test_readonly.py::test_no_previously_forbidden_address_became_readable[https://www.linkedin.com/mynetwork/]
FAILED tests/test_readonly.py::test_no_previously_forbidden_address_became_readable[https://www.linkedin.com/company/example-co/]
```

They live in `tests/test_readonly.py`, not in the invariant file where they were
first written: that file freezes the boundary by reading `readonly.py` AS TEXT
and hashing its AST, deliberately, so the freeze does not depend on importing
what it polices. These two need the live tuple and the live function.

### 5.4 The digest re-freeze

Two structures moved, in OPPOSITE directions, which is the only reason they are
one change:

```
_ALLOWED_URL_PATTERNS      6542383b4619c935 -> 0edd01ead91a89ea   (WIDENED by one pattern)
_FORBIDDEN_URL_SUBSTRINGS  92b02ca73055330f -> fcb931b0eaee5b84   (NARROWED by two substrings)
_MUTATION_CALL_PATTERNS    23aece1483afdee9    unchanged
JS_MUTATION_TOKENS         d47e30b67c583c1b    unchanged
SANCTIONED_MUTATIONS       b84365077cba813b    unchanged
<functions>                199939f7998e8d48    unchanged
```

The four unchanged are the load-bearing half: **no mutation detector was removed,
no JS token dropped, and no new mutation sanctioned** while the url lists moved.
`SANCTIONED_MUTATIONS` is still the two entries it was -- this wave adds no click.

Computed under Python 3.13.14. The two that moved are VALUE digests, which the
invariant file's own `_literal` argument establishes as interpreter-independent;
`<functions>`, the one digest that has historically split along the interpreter
matrix, did not move at all, so the 3.10 CI cell has nothing new to disagree
about.

---

## 6. Why there is no live measurement in this document

**No `mcp__linkedin__*` tool was ever exposed to this session, and the failure is
in TOOL EXPOSURE rather than in the server.** That distinction is the actionable
part, so it is stated precisely:

* The server is CONFIGURED, at project scope in
  `D:\workspace\projects\job-hunting\.mcp.json`, with `LINKEDIN_ENABLE_WRITES=1`.
* The server is RUNNING. `python.exe` executing `linkedin.py` was found at pid
  **22188** -- note that `_state/chrome-profile.lock` still names **55992**, so
  the process has restarted since that pid was recorded, and any claim resting on
  55992 is stale.
* The server CONNECTED to this session partway through: its `instructions` block
  was delivered in full, which only happens on a completed handshake. A later
  `ToolSearch` also reported the remaining connecting server by name (`instahyre`)
  and did NOT list linkedin, i.e. linkedin had finished connecting.
* **Its tools still never resolved.** Ten `ToolSearch` calls across the session,
  including two direct
  `select:mcp__linkedin__linkedin_surface_census,...` lookups and four
  capability-keyword searches phrased from the tools' own docstrings, returned no
  linkedin tool. Instructions arrived; the tool schemas did not. Searching was
  stopped at that point rather than continued indefinitely -- the finding was
  established, and further retries were spending context to re-confirm it.

A session that DOES hold those tools -- the lead's own, most likely -- can run
every probe below. Note also the corollary that applies to whoever runs them:
**the process at pid 22188 was started before this commit, so it holds the OLD
code.** `surface="settings"` will come back `unknown_surface` with
`valid_surfaces: ["feed", "profile"]` until the MCP client restarts the server.
Confirm with `linkedin_server_info()` and compare `build.code.commit` against
`git rev-parse --short=12 HEAD`; that is what the field is for.

**The standing instruction was followed rather than worked around:** never launch
the Chrome profile from a script -- the profile carries a Chrome 151 version
stamp against an older Playwright chromium, Chrome runs a downgrade migration and
DISCARDS the profile, and that has already cost this project a day. So no
alternative route was taken. Everything measurable without the browser was
measured; everything else is a debt with an address.

**Every live probe named in section 3 is a single MCP call**, and none of them
writes:

```
linkedin_surface_census(surface="feed")       -> #1, #2, #3
linkedin_surface_census(surface="profile")    -> #4
linkedin_surface_census(surface="settings")   -> #6   (new this commit)
linkedin_job_detail(<one posting>)            -> #8, cheapest route first
linkedin_open_messaging()                     -> #9   (costs an opened thread)
```

Rate discipline applies: one page per call, 3s minimum between loads.

---

## 7. The nine, as a table

| # | capability | surface | bucket | what establishes it |
|---|---|---|---|---|
| 1 | publish a post | `/feed/` | UNMEASURED | key `feed` exists and is admitted; no live run this session. Probe: `census(feed)`. |
| 2 | comment on an item | `/feed/` | UNMEASURED | same capture as #1. |
| 3 | react / like an item | `/feed/` | UNMEASURED | same capture as #1. |
| 4 | edit a profile field | `/in/me/` | UNMEASURED, narrowed | offline: 0 contenteditable and 0 forms on both profile fixtures, 6 editor-ish controls each -> editors are MODALS. Probe: `census(profile)`, read `has_href` per hit. |
| 5 | endorse a skill | another member's profile | **IMPOSSIBLE AS SPECIFIED** | offline: 0 endorse controls on 13/13 fixtures, 0 shaping blindness, 0 on his own skills page. Measuring it needs a third party's profile, and `linkedin_who_viewed_me` measures that a profile load leaves them a durable record. Refused at the gate. |
| 6 | read / change settings | `/mypreferences/d/` | UNMEASURED, now reachable | gate PASSED (2.1). Key `settings` added, index only. Probe: `census(settings)`. |
| 7 | connection invitations | `/mynetwork/` | **REFUSED AT THE GATE** | pending-invitation badge; badge family measured to reset on load twice in this package (notifications, messaging). |
| 8 | follow a company | a company page | UNMEASURED | control already measured on two allowed surfaces; blocker is slug-to-id. Gate MARGINAL, not the reason. Probe: `linkedin_job_detail` first, company page only if that fails. |
| 9 | send a message / InMail | messaging | UNMEASURED | key REFUSED at the gate (redirects into a stranger's thread, measured twice). Probe without a key: `linkedin_open_messaging()`, whose result already carries the send-surface counts. |

---

## 8. Close-out

**Full suite:** see section 9 -- filled in from the run, not from the baseline.

**`_state/`: nothing in this wave read, wrote or opened it, and no browser was
launched by it.** `session.json` is byte-identical before and after. The Chrome
profile DIRECTORY did move, and it was another Claude session's server -- proved
by process ancestry, not asserted. **Full evidence in section 9**, which is where
the convenient version of this sentence was replaced by the true one.

**No `confirm_token` was passed to anything.** No write tool was called at all.
He has still never saved a job or applied through this server, and both firsts
remain his.

**The server `instructions` string was left as it stands, deliberately.** Its
closing sentence -- *"There is no message, no connection request, no InMail, no
profile edit, and no post -- do not look for them or suggest they exist"* -- is
still true in every clause, because nothing in this wave BUILDS any of them.
Adding a census key measures a surface; it does not add a capability, and
loosening that sentence on the strength of a census would be exactly the error it
was written to prevent. What DID become false is a different sentence, inside
`not_yet_measured`, and it was corrected in the same commit (section 5.2).

## 9. Run record

**Full suite: 1730 passed, 0 failed**, with everything staged -- which is the
number that will be true of the commit. `venv\Scripts\python.exe -m pytest -q`,
Python 3.13.14.

**THE BASELINE IS 1705, NOT THE 1703 THIS WAVE WAS BRIEFED WITH**, and the two
missing tests are not a rounding error -- they are a mechanism worth knowing
about. Measured by collecting in a throwaway worktree at each commit:

```
8f5795e   1699 collected
5e5fe7e   1703 collected      <- the number the previous audit reports, correctly
eb518c6   1705 collected      <- HEAD, and eb518c6 is a DOCS-ONLY commit
```

`eb518c6` added exactly one file, `_audit/2026-08-26-session-store-ttl.md`, and
the collected count rose by two. The cause is that some checks parametrise over
`git ls-files` -- `test_no_committed_credential.py` scans every TRACKED file for
a session credential, one case per file -- so **adding a tracked file adds test
cases**. The previous audit's 1703 was accurate for its own commit and went
stale the moment its own audit file was committed.

**The same thing happens here, and it was measured rather than discovered
afterwards.** With the six code and test files modified but this document still
untracked, the suite collects and passes **1728**. Staging this document takes it
to **1730**. Both of the added cases were run against this file specifically and
pass. So:

```
1705  baseline at eb518c6
 +23  tests this wave writes           -> 1728  (measured, green, twice)
  +2  cases this AUDIT FILE creates by existing  -> 1730  (measured, green)
```

The 23, by what they certify:

| count | file | what |
|---|---|---|
| 3 | `test_surface_census.py` | the one-word name leak, parametrised over three labels -- shown failing on the pre-fix rule |
| 1 | `test_surface_census.py` | the CONTROL for those three: at any count but 1 the cap does not fire and every planted name survives |
| 1 | `test_surface_census.py` | the residual one-word shape, pinned as KNOWN |
| 6 | `test_surface_census.py` | the three gate-refused surfaces absent from the table, parametrised over six spellings |
| 1 | `test_surface_census.py` | the settings key reaches the index and not the toggles, asserted on BOTH gates |
| 1 | `test_readonly.py` | the forbidden list has only ever grown (roster, subset) |
| 1 | `test_readonly.py` | that roster check shown able to fail on a deletion |
| 9 | `test_readonly.py` | nine real addresses that must stay unreadable, one test each |
| **23** | | **total, and it reconciles exactly against the measured 1728** |

Two more tests were RENAMED rather than added, so they do not appear above:
`..._the_surface_table_is_a_closed_set_of_two` -> `..._of_three`, and
`test_every_surface_is_ALREADY_a_permitted_read_url` ->
`test_every_surface_is_a_permitted_read_url` -- the second because its docstring
asserted "the tool adds no url that readonly.py did not already allow, which is
why building it needed no edit to the navigation allowlist", and this wave made
that false. It was rewritten to say so rather than deleted: a stale claim sitting
in the one place a reader would check is worse than no claim.

**THE SUITE WAS RUN THREE TIMES, and the last is the one that counts.** After
the first green run, a byte count found `linkedin_server/readonly.py` had been
silently converted from LF to CRLF by the editing tools -- 918 line endings
flipped against what `HEAD` stores. This is the same class of defect the
2026-08-30 predecessor commit `eb518c6` records in the opposite direction, and
its lesson was followed rather than rediscovered: a Git Bash `grep` for a
carriage return is not evidence, a byte count is. The file was restored to LF,
all six touched files were re-checked against `HEAD`'s convention, and the full
suite was re-run on the restored bytes. Nothing about the AST digest depended on
it -- Python's universal newlines translate CRLF on read -- but that is a reason
the check passed, not a reason to skip it.

```
run 1   1728 passed in 415.28s   before the line-ending restore
run 2   1728 passed in 383.25s   on the restored LF bytes
run 3   1730 passed              with all seven files STAGED, so the two cases
                                 this document creates are included
```

Run 3 is the state of the commit. The first two are kept because dropping them
would hide that the bytes changed between a green run and the commit, which is
the whole reason the predecessor wave wrote its line-endings note.

### `_state/` -- the session file is byte-identical; the PROFILE DIRECTORY MOVED, and it was not this wave

**The cookie jar is untouched, verified by hash rather than by intent:**

```
_state/session.json   BEFORE  size=7813  mtime=2026-08-26 00:41:24.087578800 +0530
                              sha256(first 32)=f0892e35688868faef6a3525e54b93e4
_state/session.json   AFTER   size=7813  mtime=2026-08-26 00:41:24.087578800 +0530
                              sha256(first 32)=f0892e35688868faef6a3525e54b93e4
```

**`_state/chrome-profile` is a different answer and it would have been easy to
report the convenient one.** Its mtime moved during the wave, from
`2026-08-26 19:26:17` to `2026-08-30 10:49:06`, and
`_state/chrome-profile.lock` was rewritten from pid 55992 to pid 18468. A
Playwright chromium was live against the operator's real profile while this
document was being written.

**It was not this wave, and the attribution is process ancestry rather than an
alibi:**

```
9100   chrome.exe        --user-data-dir=...\linkedin\_state\chrome-profile   (10:48:48)
 <-  21928  node.exe     playwright/driver/node.exe
 <-  18468  python.exe   linkedin.py        <- a SECOND linkedin MCP server, started 10:46:49
 <-  11188  python.exe   linkedin.py
 <-  13924  claude.exe --continue           <- ANOTHER Claude session
```

So there are **two** linkedin server processes running, not one: 22188 (started
10:09:25) and 18468 (started 10:46:49). The browser hangs off 18468, whose
ancestry terminates in a different `claude.exe` session, and 18468 is the pid the
cross-process profile lock now names -- the lock working exactly as designed,
with one holder.

This wave launched no browser, called no MCP tool, and has no process anywhere in
that chain. **The correction to my own earlier reading is worth stating:** the
observation in section 6 that "the process has restarted since pid 55992 was
recorded" was right about the fact and incomplete about the cause -- what
actually happened is that a second server was started by another session, at
almost exactly the moment this session first received the linkedin server's
`instructions` block.

**The profile was not damaged by it.** `Last Version` still reads
`151.0.7922.34` and there is no `.CHROME_DELETE` marker, so the downgrade
migration that has already cost this project a day did not fire. Nothing was
killed and nothing was cleaned up: it is another session's live browser on the
operator's own account, and it is not this wave's to touch.

**A practical consequence for whoever picks up the probes in section 6:** that
other session HAS the linkedin server live and is driving the profile right now.
It is the session that can run them.

**No write was performed and no `confirm_token` was passed to anything.** No
write tool was called at all. He has still never saved a job nor applied through
this server; both firsts remain his.

**Working notes**, quarantined under the gitignored `_audit/_scratch/` and not
committed: `slice-guard-probe.md` (the 20-url guard probe),
`slice-fixture-census.md` (the 13-fixture offline census), plus both probe
scripts and the three suite logs.

### Commits

Split in two, following this repository's own convention -- `eb518c6` is a
docs-only commit recording `5e5fe7e`. It also resolves a problem this document
otherwise cannot solve: a file cannot name the sha of the commit that contains
it.

```
42e90e3   feat(census): a settings surface, on a written side-effect ruling
          -- and the two defects that ruling turned up
          6 files, +507 -22. The boundary, the shaper fix, the settings key,
          the digest re-freeze and 23 tests.
          Tree collects and passes 1728 (this document still untracked).
          Verified on the commit: no Co-Authored-By or session trailer, and
          every committed blob is LF and pure ASCII.

<this document's own commit follows immediately>
          Tree collects and passes 1730 -- the +2 being the two file-scan
          cases this document creates by being tracked, per section 9.
```

Neither is pushed. This repository is PUBLIC and the push is the lead's, after a
PII scan.

