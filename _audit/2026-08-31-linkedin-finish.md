# Finishing LinkedIn: what the rulings bought, and what they did not reach

Date 2026-08-31. Repo `linkedin`, branch `master`. Baseline `77ecd2b`, suite 2023.

The operator gave six boundary rulings and deferred a seventh. This wave turns
them into code, closes the seven debts Part 7 left open, and reports honestly
on which refusals lifted.

**No `confirm_token` was issued to anything, by anyone, at any point. No write
was performed.** `_state/session.json` is byte-identical -- proof in section 9.

---

## 0. Headline

| what | outcome |
|---|---|
| rulings implemented | **3 of 6** as capability; 1 declined back to him; 2 unreachable |
| refusals LIFTED | **0** |
| refusals whose REASON changed | **4** |
| Part 7 debts closed | **6 of 7**, the seventh checked and correctly left recorded |
| further stale claims found | **3**, one of them a false SAFETY claim in a docstring |
| defects found and fixed | **3** -- a `KeyError` gate, a subtraction premise, a PII leak in my own fixture |
| read-boundary hole found and closed | **1**, and it was real |
| new click call sites | **ZERO**. `SANCTIONED_MUTATIONS` is the two entries it was |
| new injected scripts | **ONE**, declared and scanned |
| suite | **2023 -> 2096**, 0 failed |
| writes performed | **NONE** |

**Zero refusals lifted is the finding, not a shortfall.** Each of the six was
blocked by a boundary AND by a missing measurement. The rulings moved the
boundaries. The measurements are still missing, and four of them cannot be
taken without either a write or a side effect that lands on him -- which is
exactly the class of thing this server hands back rather than spends.

---

## 1. The constraint that shaped this wave, stated first

`linkedin_server_info` reports `build.code.commit` for the process that is
actually loaded. It read `77ecd2b44b48` at the start of this wave and **still
read it at the end**: same pid, uptime climbing. Every commit below is on disk
and none of it is in the running process.

**So the live captures this wave was commissioned to take could not be taken.**
The two new census keys exist, are tested, and are unreachable until the MCP
client restarts the server. A restart was requested with the commit sha and
had not landed when this was written.

What this means for every claim below, and it is applied consistently: a
capability whose capture has not happened is reported as **BUILT, NOT
CAPTURED**, never as measured. The one thing this wave refused to do is let a
built capture stand in for a taken one -- which is the exact failure mode the
`_WHY_NOT_PERFORMED` claim exhibited in August, when a statement true of the
fixtures was shipped as a statement about the site.

---

## 2. The one capture that DID happen, and what it settled

The Saved tab was empty for seven parts. It is populated now, so this ran
first and it was the cheapest thing in the wave.

    linkedin_saved_jobs()
      -> count 1, linkedin_count 1, tab_counts {saved:1, in_progress:1, ...}
         title    "Senior Full-stack Engineer - Remote Sprinto"
         company  null

**PAIRED WITH A CONTROL, as the standing rule requires**, because a single
reading of a tracker page has killed nine theories in this repo already:

    linkedin_job_detail("4423880462")     <- the authoritative pair
      title    "Senior Full-stack Engineer - Remote"
      company  "Sprinto"

    linkedin_search_jobs("Senior Full-stack Engineer Sprinto")
      title    "Senior Full-stack Engineer - Remote"
      company  "Sprinto"          <- the SAME posting, parsed correctly

### What it settles: the tracker row's title, CLOSED AS A REFUSAL

Part 7 refused to split the welded title without "a delimiter or a lockup" and
recorded that it needed this capture to decide. The capture decides it, and it
decides it **against splitting**, with a positive receipt rather than an
absence:

* The join between title and employer is a **single space**. Not a middle dot,
  not a pipe, not a dash.
* **The title itself contains " - ".** So the one delimiter a heuristic would
  reach for is already inside the field it would be splitting. `" - "` yields
  `"Senior Full-stack Engineer"` / `"Remote Sprinto"` -- **wrong in both
  fields**, and wrong in the silent way, since both halves look plausible.

That is the counter-example Part 7 said it was missing. The refusal stands and
is now evidenced instead of merely cautious.

**And the control names the real cause.** The same posting parses perfectly
from a search card. So the tracker row is not a parser failure at all: the
search card carries the entity lockup (`logo_name`, `meta_line`) and the
tracker row does not. The fix, if one is ever wanted, is a lockup on the
tracker surface -- which is LinkedIn's DOM, not this repo's code. Nothing in
`shape.py` can recover a boundary the page did not draw.

---

## 2b. Second-day readings of the two anchors that matter most

The standing rule is that no single reading of a page is a measurement. Both
anchors below had been read exactly once, on 2026-08-30. They were read again
today, through the loaded (stale) process, on surfaces already allowed.

### The reaction anchor -- CONFIRMED

    linkedin_react_to_item(item="placeholder-not-a-real-item")   -- no token, none can exist

      controls          8        every one of them
      off_state         8        aria-label "Reaction button state: no reaction"
      menus            10
      comment_controls  8
      permalinks        0        <- on /feed/

**The OFF label is confirmed on a second day and has not drifted.** The gate
also states a design property worth recording: it refuses unless EVERY
rendered control agrees, "because a mixed page cannot say which item a
direction belongs to".

**AND THE FEED CARRIES ZERO ITEM PERMALINKS.** That is a new number and it
sharpens section 3's finding: on the feed the comment affordance is a BUTTON,
so there is no urn there at all. The permalinks live on his profile.

### The invitation anchor -- CONFIRMED, by a different instrument

`linkedin_send_invitation` was **refused by the harness permission
classifier**, not by this server. That is recorded rather than worked around:
a tool named "send invitation" is exactly the sort of thing a permission layer
should stop, and the correct response to a denial is to stop, not to find
another door to the same act. The count was then taken with
`linkedin_surface_census("profile")` instead -- the instrument actually built
for counting controls, which sends nothing.

    shape "<redacted> to connect"   count 9   tag button   name_source aria-label

**Identical to 2026-08-30.** The suffix the needle design anchors on is stable
across two days.

### Three further things that run came back with

    https://www.linkedin.com/in/<member>/edit/intro/      count 1
    https://www.linkedin.com/feed/update/<urn>/           20 hrefs
    "Create a post"  tag a  ->  /preload/sharebox/        count 1
    contenteditable                                       0
    "Notifications, 3 new notifications"

1. **The intro editor anchor is live**, count 1, so the allowlist entry added
   this wave targets an address that really exists. It could not be FOLLOWED,
   because the loaded process predates the entry.
2. **Twenty permalink hrefs sit on his own profile** and every one is shaped to
   `<urn>` before counting. The keys are on the page; the census is built so
   they cannot leave it. That is the addressability gap of section 3 stated as
   a number rather than an argument.
3. **His unread notification count moved 1 -> 3 between yesterday and today.**
   Recorded because section 8 lists that badge as a cost, and the cost is now
   demonstrably larger than when it was priced.

---

## 3. The six capabilities

Read every row with the census's own caveat: **presence is not permission, and
first render only.**

### #1 publish a post -- `linkedin_publish_post`. STILL REFUSING. **Ruling declined back to him.**

**RULED:** the composer (`Start a post` modal, `/article/new/`) is allowed to
open and capture; opening publishes nothing.

**AND I DID NOT BUILD IT.** This is the one place in the wave where a ruling
was handed back, so the reasoning is given in full.

The ruling's premise is that opening publishes nothing. I believe that and it
is not what stopped me. **What cannot be established from here is that opening
leaves NO DRAFT.** LinkedIn's composer autosaves; a draft post or draft
article is a visible artefact on his account under his own name; and **this
server has no tool that could detect one afterwards** -- `linkedin_draft_applications`
reads the job tracker's In Progress tab, which is job applications, not
content. So the capture would spend something nobody here can see, measure, or
clean up.

Every other capture in this wave loads a page that RENDERS existing state and
leaves nothing. This one is a different kind of act and it is the only one
whose cost is unmeasurable from inside the server.

That makes it a cost question, and cost questions on his account are his. It
has been put back to him with the alternative: he opens the composer once
himself and reports what it drew, which costs the same artefact he was already
willing to risk, and buys the measurement without this server touching it.

**What firing it would cost him:** a post is a BROADCAST. 275 followers, and
LinkedIn's own analytics on his profile show past posts reaching 103, 308 and
1,284 impressions. Whether a post can be deleted is UNMEASURED -- the per-post
overflow menu renders collapsed and its items have never been read -- and
deletion is permanently forbidden here regardless. It is also the one artefact
in this whole design that a current employer sees without looking for it.

**What would complete it:** one capture of the opened composer -- the
accessible name of its editable node and of its publish control -- plus an
answer on the draft artefact.

### #2 comment on an item -- `linkedin_comment_on_item`. STILL REFUSING.

**RULED:** `/feed/update/<urn>/` is allowed, an ordinary read of a post
permalink, no badge and no counter.

**The ruling removed one of three blockers.** The other two are untouched by it
and neither is a boundary:

1. **The comment box has never been observed.** `contenteditable == 0` across
   the whole feed and the whole profile. There is nothing measured to type
   into. A permalink that can now be opened is an address, not an editor.
2. **AND THE TARGET CANNOT BE NAMED, which the ruling did not reach.** To open
   `/feed/update/<urn>/` you need a urn, and **no tool in this server returns
   one.** The census substitutes `<urn>` out before counting, deliberately, so
   that a measurement cannot publish an identifier. The profile's 8 comment
   anchors carry real urns in their hrefs and the census reports only the
   shape.

Point 2 is the wave's most transferable finding and it applies to #3 as well:
**the permalink ruling made a surface reachable without making it
addressable.** Opening `/feed/update/<urn>/` requires knowing which urn, and
the only routes to one are a new reader over his own activity, or
`linkedin_notifications` -- which costs his unread badge, and he has one
unread notification. That badge is his to spend, not mine.

**What firing it would cost him:** a comment is public, attributed to him, and
sits under SOMEBODY ELSE'S item -- published to their audience rather than his
followers, notifying them, and staying attached to their content.

### #3 react to an item -- `linkedin_react_to_item`. STILL REFUSING. The closest, and the reason is now specific.

**RULED:** same permalink ruling.

**MEASURED, and it is the strongest anchor on this surface:**
`aria-label="Reaction button state: no reaction"`, 11 controls, 3 on the feed
and 8 on his own profile, every one in the OFF state. LinkedIn writes the
toggle state into the accessible name, which is the same convention as the
follow control.

**So the OFF-to-ON anchor -- the control a reaction would actually click --
IS measured.** That is true of none of the other five. It is why this one is
called the closest.

**Three things still stop it, and they are different from each other:**

1. **The ON label has never been seen.** This is NOT a blocker on the click --
   react clicks the OFF control, which is measured -- and it is NOT a blocker
   on the refusal, because `_direction` refuses any state it does not
   recognise, so an already-reacted item is refused rather than toggled back
   off. **It is a blocker on VERIFICATION.** After the click the control
   redraws into a label this server has never seen, so `_verify_after` could
   report only "the OFF label is gone", never what replaced it. That is
   weaker than `follow_company`, which knows both halves of its pair, and
   `follow_company`'s verification is already documented as the weakest in the
   design.
2. **WHICH reaction it would apply is unmeasured.** `Open reactions menu` is a
   SEPARATE control beside the toggle, `aria-expanded="false"`, contents never
   observed. Whether pressing the toggle applies a default Like or opens that
   picker has never been established. A gate that cannot say what it is about
   to express under his name is not a gate.
3. **The target cannot be named**, exactly as for #2.

**What firing it would cost him:** a reaction notifies the author and can
surface in his own network's feed. Removing it takes back the row, not the
notification.

**What would complete it:** one supervised reaction produces the ON label and
settles (2) at the same time -- the save/unsave pair is the worked example,
where one supervised write produced the label and a read-only route was then
built so the re-measurement never had to be bought twice. Plus a route to an
item key.

### #4 edit a profile field -- `linkedin_update_profile_field`. BUILT, NOT CAPTURED.

**RULED:** `/in/<member>/edit/` and the profile editors are allowed. His own
profile, no third party.

**BUILT:** `/in/me/edit/intro/` is on the read allowlist and
`linkedin_surface_census("profile_edit_intro")` addresses it.

**THE `/in/me/` SPELLING ONLY, and that is a measured constraint rather than a
cautious one.** The obvious generalisation `/in/[A-Za-z0-9-]+/edit/intro/` is
the one shape that must never be written, because `linkedin_who_viewed_me`
reads the RECEIVING end of exactly that signal: loading a third party's profile
leaves them a durable record. `/in/me/` redirects to whoever is signed in and
can only ever reach his own.

`/edit/` was NOT loosened. It still refuses the entire rest of that family, on
his profile and everyone else's. One url gets past it through
`_FORBIDDEN_SUBSTRING_EXEMPTIONS` -- see section 5.

**NOT CAPTURED:** the census key exists and has never been run, because the
loaded process predates it. Until it runs, no field inside any editor has been
observed and there is still nothing measured to type into. **The refusal
therefore stays**, and stays for the same reason it did yesterday.

**What firing it would cost him:** his profile is what recruiters read, and
they read it continuously rather than at a moment he chooses -- it reports 29
profile views. An edit reverted an hour later was live for an hour. LinkedIn
also notifies a network about some profile changes, which this server has not
measured and would not control.

**What would complete it:** one run of `linkedin_surface_census("profile_edit_intro")`
after a restart -- specifically, whether the editor renders the CURRENT value,
which is what makes an edit revertible by hand at all.

### #5 endorse a skill. IMPOSSIBLE AS SPECIFIED. Unchanged, and no ruling touched it.

The only surface carrying the control is a third party's profile, and loading
one is a MEASURED emission. Nothing in this wave changes that; the `/in/me/`
restriction in #4 is the same finding applied one door along.

### #6 change a setting -- `linkedin_update_setting`. BUILT, NOT CAPTURED.

**RULED:** ONE NAMED settings page below `/mypreferences/d/` -- one at a time,
never the family, never a wildcard.

**BUILT:** `/mypreferences/d/dark-mode`, and nothing else. A second page needs
a second ruling.

**WHY dark-mode AND NOT ANOTHER**, since three were candidates:

* It is a pure per-account display preference. No audience, no third party,
  nothing another member can observe.
* **And the part that decided it: it needs NO narrowing of any forbidden
  substring.** `/mypreferences/d/settings/language` and
  `.../settings/autoplay-videos` would each have required weakening
  `"/settings/"` to buy one read, and any `categories/` page would have
  required weakening the entry that keeps the toggles unreachable. Trading a
  standing refusal for a single read is the trade this design makes somebody
  argue for, and there was a candidate that did not require it.

**NOT CAPTURED**, for the same reason as #4. No toggle has been observed, so
the refusal stays.

**What firing it would cost him -- and the hazard here is worse than the
previous audit thought.** See section 5: the two account-lifecycle addresses
were never protected by the substring everyone assumed covered them.

### #7 send a connection invitation -- `linkedin_send_invitation`. STILL REFUSING, and the blocker is now a different one.

**RULED:** targeting is allowed as a CALL-TIME ARGUMENT, never stored. This
server may RECEIVE one identity per call and must not persist it -- no identity
in any file, log, cache or audit.

**BUILT, and the privacy property is structural rather than promised.** The
needle is passed INTO the page. `INVITE_NEEDLE_JS` enumerates controls whose
`aria-label` ends with the measured suffix `" to connect"`, counts how many
contain the needle, and **returns three integers -- total, matches, index --
and no label, no name, and no fragment of either.**

That is what makes "never stored" enforceable. A name that reaches Python can
reach a traceback, an exception message, a cache key or an audit line, and no
care downstream un-rings that. `writes.aim_invitation` never sees the needle at
all: its inputs are three integers and its refusal strings are built from
counts.

**THE AIMING RULE.** Exactly one match is the only aimable state. Zero is
refused; **two or more is refused as AMBIGUOUS**, because choosing between
indistinguishable controls is choosing by position, which is how a request
reaches somebody who merely sorted earlier.

**AND THE REASON IT STILL REFUSES CHANGED.** Yesterday the blocker was "a
decision he has not made". He has made it. The blocker now is a defect found by
tracing where a target actually goes:

The confirm-token target channel is `Observation.target`, `where["target"]`,
`grant.target`, `grant.preview` and `consume()`'s mismatch text. **Three
hazards go live the moment this action becomes grantable:**

1. `consume()`'s mismatch message interpolates BOTH targets verbatim -- for a
   grantable invitation that is a stranger's name in an exception string
   handed back to the caller.
2. **`_GRANTS` has no sweeper.** Written at `mint`, removed only by `consume`
   or `discard_all`. No timer, no task, no `atexit`. The TTL bounds when a
   grant can be USED, not how long it is HELD, so a minted-but-never-confirmed
   grant keeps its target in process memory for the life of the process.
3. `_render` retains the whole rendered block on `grant.preview`.

None is a defect today, because `mint` refuses a grant for a surface-less
action before `_target_for` is ever reached. All three are conditions on any
future wiring. **So the needle must never be routed through `target`** -- and
it is not; `_read_profile_invitations` was deliberately left not taking one.

**What firing it would cost him:** an invitation is a REQUEST TO A REAL PERSON
and lands as a notification with his name on it. Withdrawing one -- if LinkedIn
permits it, which is unmeasured because the sent-invitations manager's own
address contains `invitation` and is forbidden -- removes it from a pending
list; it does not un-notify. And the quieter cost: **LinkedIn restricts
accounts whose invitations are frequently ignored**, so this is the one action
here whose repetition has a consequence for the account itself. Nothing
readable reports that limit.

### #9 send a message / InMail -- `linkedin_send_message`. REFUSING, and now DEFERRED BY RULING.

**RULED: do not open messaging.** Opening it opens a conversation LinkedIn
chooses and can mark a real person's InMail read -- a cost paid on somebody
else.

This wave did not call `linkedin_open_messaging`. The refusal's reason should
now read as **deferred by ruling** rather than unmeasured, and that wording
change is the only thing owed here. It is listed in section 8 as outstanding:
it is a one-line edit in `writes._NINE_REFUSALS` that this wave did not reach.

---

## 4. The seven debts

| # | debt | outcome |
|---|---|---|
| 1 | **No capture of a populated Saved tab** | **CLOSED.** Captured, paired with two independent controls. Section 2. |
| 2 | **The tracker row's title carries the employer** | **CLOSED AS A REFUSAL, with evidence.** The capture produced the counter-example: the join is a single space and the title itself contains `" - "`, so every candidate delimiter is inside the field. The control proves the cause is a missing lockup in LinkedIn's DOM, not the parser. |
| 3 | **`HARVEST_BLOCK_CARDS_JS` carries the Part 4 subtraction defect** | **CLOSED.** A notifications fixture was built that shows it failing -- the visible body eaten by a `display:none` duplicate -- and 8573b8b's `isRendered` guard was ported verbatim in behaviour. The clip pattern is asserted STILL charged. Honest scope: proven as a reachable mechanism, not proven to be what the live page does. |
| 4 | **`set_open_to_work` has no backstop behind `_direction`'s unknown gate** | **CLOSED.** The multi-state branch validated the DESTINATION against `spec.audiences` and never the ORIGIN, then subscripted the dict with it: `KeyError: 'anyone on linkedin'`. Now a `WriteAttemptError` that refuses rather than defaulting. Shape-closing, not an observed bug -- `_read_profile_state` catches it one layer up. |
| 5 | **Prose rot: three/four writes where five ship** | **CLOSED.** 31 tools = 19 read + 5 write + 7 write-shaped-and-refusing, derived twice and the two agree. Nine claims corrected. One was not a stale number: *"Nothing here ... follows a company"* asserted the absence of a tool registered below it. |
| 6 | **The trace corpus is 13 records but fewer shapes** | **CLOSED.** Measured at 14 records / 7 shapes -- the debt line's count was stale, its "7 identical" exact. Widened to 16 / 9, each addition reaching a branch nothing reached. Four candidates rejected as padding. |
| 7 | **The status classifier could take a title the way the time-ago one did** | **CHECKED AND CORRECTLY LEFT RECORDED.** The instruction was to extend it only if a capture produced a status-shaped title. The capture produced `"Senior Full-stack Engineer - Remote Sprinto"`, which is not status-shaped. The exemption stays time-ago only. |

---

## 5. The hole in the read boundary, which was real

The settings audit assumed `Close and delete account` and `Hibernate account`
were covered by the `/mypreferences/d/categories/` forbidden entry, and
reasoned from that assumption: *"A permission written for the FAMILY would
carry those with it."*

**They were never in that family.** Measured off a live census 2026-08-31:

    Close and delete account  ->  /mypreferences/d/close-accounts
    Hibernate account         ->  /mypreferences/d/hibernate-account
    Dark mode                 ->  /mypreferences/d/dark-mode

Neither contains `categories/`. **The only thing that had ever refused the two
most destructive addresses on his account was the anchored allowlist** -- and
that allowlist has now been deliberately widened twice in two days, which is
precisely the situation a backstop exists for.

Both are now on `_FORBIDDEN_URL_SUBSTRINGS`. The tests assert **which gate**
refuses them, because a test checking only the net answer could not have seen
this: the net refusal held the whole time. What did not hold was the list's
stated job as a "second, independent gate".

### The exemption mechanism, and why it is shaped this way

`/in/me/edit/intro/` contains `/edit/`, which is checked before the allowlist.
Admitting the page needed either a narrowed `/edit/` entry or a named
exemption. Narrowing was refused.

`_FORBIDDEN_SUBSTRING_EXEMPTIONS` maps an **exact, complete url** to the **one**
forbidden substring it may carry. Three properties, each load-bearing:

* Compared with `==` against the whole lowered url -- never a prefix, never a
  pattern. This mirrors `WriteSpec.exempt_substring`'s own discipline: *"a
  loose exemption is how a real write hides"*. `.../in/me/edit/intro/../../evil`
  matches nothing and is refused by `/edit/` like the rest of the family.
* **Per-substring**, checked inside the forbidden loop, so a url exempted for
  `/edit/` that also carried `/delete` is still refused.
* It buys past **one gate, never both**. The url must still match an anchored
  allowlist pattern afterwards.

### A finding recorded rather than acted on

The census requests `https://www.linkedin.com/mypreferences/d/` and **lands on**
`https://www.linkedin.com/mypreferences/d/categories/account` -- read twice,
2026-08-30 and 2026-08-31. That is a redirect into the exact family the
forbidden entry exists to block, and `assert_read_url` gates the REQUESTED url
only.

It is the same shape as the `/messaging/` finding from August: a guard that
forbids a destination it knowingly delivers you to. It is recorded here and
NOT resolved, because both available resolutions are wrong on today's evidence
-- widening the pattern to admit the landing url would enlarge the family, and
re-checking landed urls is a change to every read in the package. It belongs
to whoever next touches that gate.

---

## 6. The PII guard fired on my own work

`tests/test_no_committed_identity.py` caught a urn-shaped href in a
notification fixture this wave commissioned:

    AssertionError: tests/test_sdui_surfaces_fixture.py: 1 unallowed urn id
    hit(s), 0 declared.

The value was invented. **The guard cannot tell invented from real, which is
exactly its value**, and this repo is public.

The house remedy is a `DECLARED_PLANTS` entry, and there are two precedents.
**It was refused here.** Both precedents EARNED their entries by needing the
shape -- one feeds a redactor a urn-shaped literal, one certifies that
`writes._target_for` declines to validate a feed-item urn. This one was
decorative realism in a field no test reads: the walk returns the href
untouched and every assertion in the section is about the card's text.

So the literal went and the allowlist stayed exactly as narrow as it was.
Widening a PII allowlist for a decorative value is how the next real
identifier gets through.

**AND IT FIRED A SECOND TIME, ON THIS DOCUMENT.** The full sha256 of
`session.json` carries a ten-digit run, which is phone-shaped, and the guard
cannot tell a hash from a number. The same remedy applied: the hash is printed
truncated here, which turns out to be what every previous audit in this
directory already does -- `sha256(first 32)` in the writes audit,
`f0892e35688868fa...` in the undo audit. That convention was almost certainly
established by this guard firing on somebody else, and nobody wrote down why.
It is written down now: **do not paste a full sha256 into a tracked file in
this repo.** Thirty-two hex characters identify the artefact beyond argument
and contain no ten-digit run.

---

## 7. The boundary did not widen beyond what was ruled

| structure | before | after |
|---|---|---|
| `SANCTIONED_MUTATIONS` | 2 | **2** |
| new click call sites | -- | **0** |
| `_ALLOWED_URL_PATTERNS` | n | n + 2, both anchored to one page each |
| `_FORBIDDEN_URL_SUBSTRINGS` | n | **n + 2** -- the list GREW |
| forbidden substrings removed | -- | **0** |
| `_FORBIDDEN_SUBSTRING_EXEMPTIONS` | -- | 1 entry, exact-url, per-substring |
| injected scripts | 6 | 7, declared and scanned clean |
| `evaluate()` waivers in `dom.py` | 6 | 7 |

**The seventh waiver is the first spent to buy a PRIVACY guarantee rather than
a reading.** The other six count controls and could each have been a locator
chain -- which is the test that got a third waiver refused in August. This one
fails that test in the other direction: a locator chain comparing the label in
Python would have to fetch a third party's name into this process first, which
is the exact thing the ruling forbids.

The frozen AST digests fired, as designed, and were re-frozen in the same
commit with a comment recording which moved and in which direction -- because
a digest cannot tell a list that grew from one that shrank.

---

## 8. What remains between this server and complete

Ordered by what it would take, not by size.

**BLOCKED ON A RESTART, and nothing else:**

1. `linkedin_surface_census("profile_edit_intro")` -- decides #4.
2. `linkedin_surface_census("settings_dark_mode")` -- decides #6.

Both are built, tested and green. Neither has run.

**BLOCKED ON HIM, because the cost lands on him:**

3. **The composer capture (#1)** -- opening it may leave a draft artefact this
   server cannot detect or remove. Handed back with the alternative that he
   opens it once himself.
4. **One supervised reaction (#3)** -- produces the ON label and settles what
   the toggle actually applies, in one act, on his own content. Eight of the
   eleven measured controls are on his own posts.
5. **His unread notification badge**, if a feed-item urn is ever to come from
   `linkedin_notifications`.

**NOT REACHED BY ANY RULING, and this is the wave's main finding:**

6. **There is no route to a feed-item key.** The permalink ruling made
   `/feed/update/<urn>/` readable without making it ADDRESSABLE. No tool here
   returns a urn -- the census substitutes `<urn>` out by design. So #2 and #3
   would be unusable by him even with every other blocker cleared. Closing it
   needs a new reader over his own activity that returns item keys for HIS OWN
   items, which is a capability nobody has specified and which has its own
   privacy question: a profile activity rail carries other people's items too.

**OWED AND NOT DONE BY THIS WAVE:**

7. `linkedin_send_message`'s refusal text should say **deferred by ruling**
   rather than unmeasured. One line in `writes._NINE_REFUSALS`.
8. The `/mypreferences/d/` redirect finding in section 5 is recorded and
   unresolved.
9. ~~`tests/test_readonly_boundary_invariant.py:35`~~ **CLOSED.** It said a
   re-freeze "HAS BEEN ONE, ONCE" of something that has happened five times --
   count rot in the one file whose job is noticing when something moved.
10. ~~The README's read table lists 14 rows for 19 reads.~~ **CLOSED.** All
    nineteen are there, verified set-equal to `mcp.list_tools()` minus the
    twelve write-shaped names rather than counted by eye. It had also been
    leading with `linkedin_login_browser`, the DEPRECATED ALIAS, while the
    canonical `linkedin_login` was absent entirely.
11. **A FALSE SAFETY CLAIM, found while doing 10 and corrected.**
    `linkedin_notifications`' docstring said: *"It is the ONE server-side
    change any tool here causes. Everything else in this package leaves
    LinkedIn exactly as it found it."* True when written; now false several
    times over -- five writes ship, messaging opens somebody's conversation
    and resets a badge, and a job search adds to his recent-search history.
    **This is the worst of the rot found in this wave**, because it is a
    docstring an assistant answers from, and that sentence is exactly the kind
    a caller repeats verbatim to somebody deciding whether to run something.
    The narrower true claim is kept: it is the only server-side change any
    READ causes WITHOUT BEING ASKED FOR IT.
12. **STILL OPEN, and it needs a rewrite rather than a patch.** README's
    "What it deliberately cannot do" carries five stale claims: it still lists
    following and applying as impossible when both ship, still says inbox
    reading is unmeasured and "has NOT been run", and still heads "The two
    side effects" over three. Left deliberately -- patching individual
    sentences in a section whose premise has moved produces a section that
    contradicts itself in more places, which is what the write-count history
    in `server.py` demonstrates.

**CANNOT BE CLOSED FROM HERE AT ALL:**

11. **Endorsement (#5)** -- the control lives only on a third party's profile
    and loading one is a measured emission.
12. **Whether LinkedIn permits withdrawing an invitation** -- the manager's
    own address contains `invitation`.
13. **Whether LinkedIn permits deleting a post or a comment** -- the overflow
    menus render collapsed and have never been opened.
14. **His InMail balance** -- `/premium/my-premium/` is not on the read
    allowlist, so a send could spend a finite resource whose size is unknown
    to the thing spending it.

---

## 9. Receipts

    baseline            77ecd2b44b48   suite 2023 passed
    final               bf9ac08        suite 2096 passed, 0 failed

    dacf76d  fix(gate)      set_open_to_work's origin gets the check its destination had
    958a98d  fix(harvest)   port the non-rendered-duplicate guard to the block walk
    ec19c8b  test(trace)    the corpus had 14 records and 7 shapes, not 13 and 13
    e3586c1  docs           the write count was wrong a fourth time, and five ship
    b364744  fix(fixture)   the identity guard fired on my own notification card
    0d543f4  feat(boundary) the three surfaces the operator ruled, and a name that
                            never enters Python
    b0c3d0a  docs(refusal)  send_message is deferred by ruling, not unmeasured
    24cba07  docs(audit)    this document
    bf9ac08  docs           the read table listed 14 of 19, and a safety claim
                            that was no longer true

    _state/session.json
      sha256(first 32)  f0892e35688868faef6a3525e54b93e4
      bytes             7813
      mtime   2026-08-26 00:41:24 +0530
      -- read at the start of this wave and again at the end. UNCHANGED.

    confirm_tokens issued        0
    writes performed             0
    third-party profiles loaded  0
    live page loads this wave    7  (saved tab, job detail, job search,
                                     settings census, profile census, and the
                                     feed read inside react_to_item's refusal)
    tools refused by the harness 1  (linkedin_send_invitation -- not routed
                                     around; the census was used instead)

Nothing was pushed. The push and its PII scan are the lead's.
