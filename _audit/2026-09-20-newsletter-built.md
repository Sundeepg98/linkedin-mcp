# NEWSLETTER-SURFACE, built. One capability, no boundary change, and two
# addresses refused with the argument written down.

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- its ranked table publishes `NEWSLETTER-SURFACE` as 12 rows at `1R/11W`, and the corpus holds THIRTEEN newsletter-named frozen-GAP rows split `3R/10W`, so every 12-subset of them holds at least TWO reads and `1R` was unreachable from the census's own direction column on the day the table was written. Not a re-file and not the cross-slice duplication: the published cell was wrong when it was written. Section 6a below.

Wave `build-newsletter`, 2026-09-20, from master `bf275cf`.
Scope: the 12 filed rows of `NEWSLETTER-SURFACE`, verdict BUILD, 11 live GAP.
No write was fired. No browser session was opened. No LinkedIn page was
loaded. Every measurement below is offline, against a capture already on disk
and against committed fixtures.

---

## 0. THE HONEST LEDGER LINE, FIRST

    rows banked out of GAP        0
    rows inflated                 0
    capability shipped            1   M C50's READ HALF, tested, not a stub
    allowlist patterns added      0   and the refusal is argued, not deferred
    open questions closed         2   by measurement, permanently
    prose claims corrected        3
    census defects handed over    2
    inherited CI reds repaired    1   not this wave's, and it blocked everyone

**THIS BLOCKER IS NOT WHAT ITS VERDICT SAYS IT IS, and the number above is the
evidence rather than an excuse.** Nine of the eleven GAP rows are WRITES whose
controls are on pages nobody has opened, and the two READS are for an address
nobody has ever seen LinkedIn serve. A wave with no browser can move exactly
what moved here. What it CAN do, and what this one spent its time on, is make
sure the next wave with a browser spends one page load instead of four.

---

## 1. THE MEASUREMENT THAT DECIDED EVERYTHING BELOW

`scripts/_probe_newsletter_surface_shape.py`, offline over
`_audit/_probe-newsletters-hyd.html` -- the gitignored capture the 2026-09-05
live probe wrote and then walked away from.

**THAT PROBE PUT FOUR QUESTIONS IN ITS OWN HEADER, ANSWERED TWO, AND LEFT TWO
OPEN FOR FIFTEEN DAYS -- behind a page load that had already been paid for.**
Re-reading a capture costs nothing on his account. That is register entry 23's
subject and it is the most portable thing in this document.

    capture                 74234 chars
    hrefs                      28, 23 distinct
    newsletter anchors         10   agrees with the Playwright reader's 10
    aria-labels                24, 23 distinct
    buttons                    19
    forms                       1

### WHAT THE PAGE DRAWS

| shaped href | count | read gate |
|---|---:|---|
| `<seg>//<seg>/newsletters/<newsletter>/` | 10 | refused |
| `/in/<member>/` | 3 | relative, no verdict |
| `/article/newsletter/new/` | 1 | relative, no verdict |
| `<seg>//<seg>/messaging/` | 1 | ADMITTED |
| `<seg>//<seg>/notifications/` | 1 | ADMITTED |
| eleven more, all chrome | 12 | refused |

**THE THREE MEMBER PATHS ARE IN THE PRODUCT SECTION, NOT THE NAV**, measured
by the same landmark stack: `main>section>section`, alongside the rows. The
page NAMES MEMBERS. The shipped reader cannot reach them -- its anchor
selector is `a[href*="/newsletters/"]`, plural, and no member path matches it
-- but **whoever widens that selector, or adds an author join, inherits three
third-party names in one step.** Recorded here and in `readonly.py` so it is
met as a known obligation rather than as a surprise.

### WHAT THE PAGE DOES NOT DRAW, AND THESE THREE ZEROS ARE THE FINDING

```
the word "analytics"       0   in 74234 characters
the word "subscribe"       0   href, aria-label and text
the word "unsubscribe"     0
```

**A ZERO OUT OF A BROKEN MATCHER LOOKS EXACTLY LIKE A ZERO OUT OF A PAGE**, so
the probe carries `--control`: the identical census over a synthetic document
that DOES carry every one of those words, required to name each. It passes,
and the script prints the dependency in its own output -- *"A zero above is a
measurement ONLY if --control passes."*

### AND WHERE THE ONE AUTHOR-SIDE ROUTE SITS, WHICH IS THE WHOLE SIGNAL

```
product <h2> "Newsletters"          offset 27655   main>section>section
/article/newsletter/new             offset 27957   main>section>section
first subscription row              offset 29889   main>section>section
```

302 characters after the heading, 1932 before the first row, in the heading's
own container. **That is the section's header action, not global chrome** --
and the difference is the difference between a fact about THIS ACCOUNT and a
string every member is shown. LinkedIn gates newsletter authorship, so the
question *is the control offered to me* has a real answer.

Presence alone would have proved nothing. Every needle in the probe is
therefore reported with its enclosing LANDMARK STACK, which is tag names only
and names nobody.

---

## 2. WHAT SHIPPED

**`linkedin_newsletter_subscriptions` now returns `create_control` and
`create_control_outside_main`.**

The first counts create-a-newsletter anchors inside `main`; the second counts
the rest. Both are integers. **The hrefs are counted and never read**, so
nothing the page chose can reach a caller through the pair -- asserted over
the whole returned structure, not over the two fields, because a leak arrives
where nobody is watching.

**IT IS THE READ HALF OF A WRITE AND NOTHING MORE.** Creating a newsletter
mails subscribers -- `messaging-and-content.md` marks `M C50` **NOT**
reversible in those words. Nothing in this package creates one; the address is
on `press._COMPOSER_MARKERS`, so the sanctioned press mechanism refuses it
even if somebody later wants it pressed; and no tool here navigates to it.
Reporting that a control is on the page is not an offer to press it.

### WHY BOTH NUMBERS SHIP

A document-wide count reads the same today and becomes a DIFFERENT measurement
the day LinkedIn puts a create route in the nav, silently, with nothing saying
why. Publishing the two separately is the same discipline that makes `anchors`
ship beside `distinct` on this very tool: the illustration anchors are counted
and dropped rather than filtered in silence.

### THE CREDIT I TOOK AND THE FOUR I DID NOT

`M C50` gets a PARTIAL in this report and **stays GAP in the census**, because
the row is a write and the write is not built.

`M C51`, `M C81`, `M C84` and `P L3` get nothing, and the reason is measured
rather than modest: **the page draws no manage, edit or delete route at all.**
The word "manage" occurs twice in the document, once inside a subscription
row's own prose and once in the advertisement's "Manage this ad". Crediting
those rows off a create control would be the move the company-page wave
refused when it declined a PARTIAL built on a positional zero.

---

## 3. THE BOUNDARY: NOTHING WAS ADMITTED, AND THAT IS A RULING

`_ALLOWED_URL_PATTERNS` is **35 before and 35 after**. The AST digest
`6577a7bc8a32d7b8` is unmoved. Two candidate addresses were on the table and
both are refused with the argument recorded in `readonly.py` beside the entry,
not in this file where a future reader will not look.

### 3a. `/newsletters/<slug>/analytics/` -- REFUSED, because it is UNMEASURED

`readonly.py`'s refusal list has read `/newsletters/<slug>/analytics/ census
M C83, P L4` since 2026-09-05, in a voice that sounds like a measurement.
**It is not one.** Nobody in this repository has seen LinkedIn serve that
spelling. The page that lists his newsletters links no analytics address and
says the word zero times.

A second candidate exists and is no better off: `/analytics/creator/
newsletters/` appears only in `tests/test_analytics_creator_boundary.py` as a
MUST-REFUSE needle. Never observed either.

**THIS SURFACE'S OWN FOUNDING LESSON IS THAT AN ADMITTED ADDRESS IS NOT A
SERVED ONE.** `/in/me/details/interests/` was admitted for this blocker's
precondition and REDIRECTS. An entry written for a spelling nobody has seen
would be exactly the guessed address the newsletter entry's opening paragraph
declines to be -- *"THE ADDRESS WAS NOT GUESSED AND IT IS NOT THIS ENTRY'S
FIND."*

So `M C83` and `P L4` are **not one allowlist line away from anything.** They
are waiting on a LIVE READ that establishes which address serves. That is a
different cost from "allowlist +1" and the ledger's costing does not say so.

### 3b. `/newsletters/<slug>/` -- REFUSED TWICE, and the second reason is new

The existing reason stands: a newsletter slug is ROUTINELY ITS AUTHOR'S NAME,
measured, so the address itself carries a person and admitting it would put
one in every log line recording a page load. One of the five slugs in the
tracked fixture is a person's name with two words around it.

**But that reason alone invites the answer "then ship a name-free shaper with
it", which is precisely what the company-page admission did yesterday.** The
two cases are not the same, and the asymmetry is measurable:

| | company Page | newsletter |
|---|---|---|
| numeric spelling exists | YES, 21 of 28 corpus segments | **none known** |
| package can assemble the address | YES, `company_page_url`, numeric only | **no** |
| slug form admitted because | LinkedIn canonicalises numeric -> slug, so refusing the slug refuses the ARRIVAL | -- |

All ten captured anchors are slug forms. **There is no name-free spelling to
assemble**, so reaching this page would mean navigating to an href THE PAGE
CHOSE -- which `tests/test_navigation_is_never_derived.py` exists to refuse,
after `/in/me/` resolved to a decorated member path and a slug went into a
traceback.

The rule the company-page wave wrote still governs: *the list admits what the
product serves, and the package assembles only what names nobody.* **Here
those two sets do not overlap.** The door would open onto a room nothing may
walk into, and the room is made of other people's publications with the author
named in the address.

`M C51`, `M C80`, `M C84`, `N 55`, `N 56` and `P L3` all wait there, and they
wait on that rather than on a line. **A surface admitted and unusable is not a
partial win; it is a blast radius paid for nothing.**

---

## 4. EVERY GUARD SHIPS SHOWN FAILING

### The probe's five controls, each capable of voiding the run

| control | mechanism | state |
|---|---|---|
| the census can speak | `--control` over a synthetic doc carrying every finding word | all named |
| the reducer changes a name | a person-shaped slug READ OUT OF THE TRACKED FIXTURE, never pasted | `/newsletters/<newsletter>/` |
| cross-instrument agreement | regex count 10 vs the Playwright reader's 10 | AGREE |
| must stay silent | an attribute no document carries | 0 |
| an absent capture | worktree run | exit 2, no tally printed |

The last one is not hypothetical: **a linked worktree carries no gitignored
files**, so the default invocation from this wave's own tree finds nothing.
Reported as an absence, exit 2, with the line *"an absence is not a zero"*.
Had it returned zeros it would have said *the page draws no analytics* about a
file that was not there.

### The reader's mutation, planted and fired

`test_the_naive_document_wide_selector_is_shown_getting_it_wrong` monkeypatches
the shipped selector to the obvious wrong implementation -- count the whole
document, which is what every other reader in the module does -- and measures
it reporting **2 in main and 0 outside** against the shipped **1 and 1**.

That assertion is only real because the fixture carries a DECOY create route
outside `main`, which the live page does not draw. It is the same deliberate
divergence as the fixture's eleventh anchor, and
`test_the_fixture_draws_the_create_route_twice_and_only_one_is_in_main` pins
the decoy so nobody tidies it away and leaves the scoping assertion passing
while testing nothing.

### A DEFECT IN MY OWN TEST, CAUGHT BY ITSELF ON ITS FIRST RUN

That pinning test located `<main>` with a bare `find` over the fixture SOURCE.
The fixture's own header comment, amended in the same commit, NAMES the
`<main>` wrapper in prose -- so the locator hit the explanation at offset 1495,
put the decoy at 3092 on the wrong side of it, and the test went red with a
coordinate triple that made no sense until the comment was read.

**Any assertion that searches a fixture's source rather than its DOM is
searching its documentation too.** Fixed by stripping HTML comments before
locating, and the comment above the fix says so rather than quietly working.

### The reset nobody would have noticed

The create counts are taken inside the same `try` as everything else, so a
frame detaching after one of them would leave a number that looks measured
beside an error saying nothing was. They are reset in the handler with the
other three, and `test_a_detached_frame_resets_the_create_counts_rather_than_
keeping_them` asserts it.

---

## 5. THE 12 ROWS, ONE BY ONE

Legend: SHIPPED = reachable from a registered tool and tested. PARTIAL = a
named half delivered. GAP = still gap, with the measured earliest binding
constraint.

### Moved this wave

**`M C50` -- Create a newsletter.** GAP in the census, **READ HALF SHIPPED**.
`create_control` reports whether LinkedIn offers the create affordance in the
product section, which is an account-specific eligibility fact because
authorship is gated. Delivered by `newsletters.CREATE_ROUTE` /
`CREATE_SELECTOR`, surfaced by `linkedin_newsletter_subscriptions`, tested by
five tests in `tests/test_newsletter_reader.py`.
STILL MISSING, and it is three things rather than one: the address
`/article/newsletter/new/` is refused (ONE boundary change -- it carries no
`/create` substring, unlike `/newsletters/create/` which is refused twice), a
WriteSpec, and a ruling on the AUTOSAVE class. `/article/new/` is already
admitted for READING and is a composer; opening one may autosave a draft this
server has no surface to detect, which is why this wave did not admit the
second composer either.

### Already delivered before this wave

**`N 57` -- View the newsletters you subscribe to.** COVERED-CANNOT-DELIVER,
pre-existing and correctly filed. `linkedin_newsletter_subscriptions` returns
`distinct` -- a COUNT. The row asks WHICH. `shape.subscription_row` redacts
the title unconditionally and publishes a constant href shape, so the answer
says a subscription exists and never which one. **Nothing found uncredited.**

The company-page wave found seven rows already built and never credited. I
looked for the same here and **found none.** Every newsletter code path in the
package -- `newsletters.py`, `feed.py`'s kind map, `search_results.py`'s
`newsletter_result`, `shape.membership_row`, `shape.subscription_row`,
`recommendations.py`'s markers, `dom.py`'s nav record -- was checked against
the twelve rows. The feed and search paths CLASSIFY a newsletter link; no
census row asks for that, and crediting one would be manufacturing.

### Still GAP, with the measured constraint

**`M C83` and `P L4` -- newsletter analytics.** GAP. The only two READS in the
blocker, and they are **one capability filed twice** (see section 6). Blocked
on a LIVE READ, not on a line -- section 3a.

**`M C51` -- Manage a newsletter.** GAP. No manage route exists on the one
newsletter surface ever opened. Its control is on a newsletter's own page --
section 3b.

**`M C84` -- Manage multiple newsletters.** GAP, same address, same ruling.

**`P L3` -- Create / edit / delete a newsletter.** GAP. Its create third
shares `M C50`'s route; its edit and delete thirds are on a newsletter's own
page.

**`M C81` -- Create a Newsletter Page.** GAP. A Newsletter *Page* is an
organisation-shaped product and no measurement here reaches it. The create
route the page draws is `/article/newsletter/new`, which is a newsletter and
not a Page, and conflating them would be the cheapest error available.

**`M C80` -- Subscribe or unsubscribe to a newsletter.** GAP, **and it is
BUNDLED, not a clean row.** `_audit/2026-09-19-duplicate-register.md` records
it as spanning `N 55` and `N 56`: one row against two capabilities, so
subtracting it removes two capabilities and one row and the counts diverge.
No control drawn here -- measured zero.

**`N 55` -- Subscribe to a newsletter.** GAP. Measured zero on this surface.

**`N 56` -- Unsubscribe from a newsletter.** GAP, **and this wave answers the
question that was filed against it.** The 2026-09-05 live probe asked whether
an unsubscribe control is drawn here, noting it *"would take census N 56 from
two blockers to one"*. **It is not: zero occurrences in href, in aria-label
and in text.** The row does not shorten.

**`N 58` -- Unsubscribe from newsletter emails while staying subscribed on the
feed.** GAP, **and it is filed against the wrong blocker.** This is an email
SETTING. The captured newsletter page contains `email` 0 times, `frequency` 0,
`settings` 0 and `notify` 0, so the control is not drawn on this surface at
all.

**THE MEASURED HALF AND THE INFERRED HALF ARE KEPT APART.** MEASURED: the
control is not on the newsletter surface. INFERRED: its likeliest home is
Settings, under email frequency -- and if that is right the constraint is the
settings family, where `linkedin_update_setting` is scoped to **dark mode
alone** and its own WriteSpec residue says why widening is unavailable --
*"two of the thirty-three addresses are account destruction ... so a setting
has to be admitted BY NAME or not at all."* That route needs a named settings
address plus a second WriteSpec plus a live read of that page. A SECOND
POSSIBILITY is not excluded and would be worse: LinkedIn also carries an
unsubscribe link in the newsletter EMAIL itself, which is off-platform
entirely and outside this server's reach in any spelling. **Nobody has
looked**, and which of the two it is decides whether the row is expensive or
impossible.

Either way it is not a newsletter-surface problem. Handed over rather than
re-filed: this wave does not run `build_blocker_map.py --write`.

---

## 6. TWO CENSUS DEFECTS, HANDED OVER

### 6a. THE OVER-PUBLISHED R IS NOT A RE-FILE AND NOT THE DUPLICATION

`scripts/_check_published_split.py` reports this blocker **published R1/W11,
held R3/W9**, and the brief I was given attributes the surplus to the
`P L4` / `M C83` cross-slice duplication plus `N 57` as a third read. **I
checked the ruling rather than assuming it, and it does not carry the
arithmetic.**

The three held-R rows are `M C83`, `N 57` and `P L4`. Each is marked `R` in
its own slice table, and **each was already marked `R` at `aac33be`, the
ledger's own commit** -- verified by reading `profile.md`,
`messaging-and-content.md` and `network.md` at that tree.

The corpus holds **THIRTEEN** newsletter-named frozen-GAP rows, not twelve:
the twelve in the map plus `M C82`. Their split is **3R / 10W**. Every
12-subset of thirteen rows holding three reads holds at least TWO.

    published    12 rows    1R / 11W
    the 13       13 rows    3R / 10W
    the map's 12 12 rows    3R /  9W

**So `1R/11W` is unreachable from the census's own direction column, and was
unreachable on the day it was published.** It is not a re-file signature. It
reads like a hand-written summary -- *one read, the rest writes* -- rather
than a count.

The duplication ruling is real and does not rescue it either.
`_audit/2026-09-19-duplicate-register.md` entry 7 records `P L4` / `M C83` as
a pair, state GAP, and states in its own section 4 that it executes **no
subtraction, no state change, no census row edited**. Even executed, it
removes one row and one read: held R would be **2** against a published **1**.

**THE CONSEQUENCE FOR THE REPORT, which is the part that matters beyond this
blocker:** `_check_published_split.py`'s docstring frames a direction over-run
as distinguishing *a published row was LOST* from *a published row was RE-FILED
OUT*. There is a third cause, and this blocker is it -- **the published cell
was wrong when it was written**. Two blockers are currently reported OVER and
they should not both be read as the same thing.

### 6b. `M C82` IS A THIRTEENTH NEWSLETTER ROW AND IT IS UNASSIGNED

`M C82` "Share a Newsletter Page", W, GAP at the freeze and GAP today, is one
of the 19 UNASSIGNED frozen-GAP rows. By subject it is plainly this blocker's;
by what blocks it, its control is on a Newsletter Page, which is the address
section 3b refuses.

**It is unassigned because of the COUNT, not because of the evidence.**
Admitting it makes the map hold 13 against a published 12, which the shipped
builder's count assertion would flag. That is the count constraining the
evidence rather than checking it -- and it points the SAME WAY as 6a: the
published cell is short a row and short two reads, and over by one write.

Neither is fixed here. `build_blocker_map.py --write` was not run.

### 6c. AN OBSERVATION, NOT A ROW: the surface census does not know this page

`CENSUS_SURFACES` in `server.py` holds twelve keys -- `feed`, `profile`,
`profile_edit_intro`, `settings`, `settings_dark_mode`, `post_composer`,
`article_composer`, `messaging_compose`, `premium`, `search_appearances`,
`groups`, `events` -- and **none of them is a newsletter surface**, although
the newsletters root has been admitted since 2026-09-05 and has a dedicated
tool. `linkedin_surface_census` therefore cannot price a page this server
already opens.

The name `newsletter_composer`, which a grep finds in
`tests/test_every_census_surface_prices_itself.py`, is NOT evidence of a
shipped surface: it is a synthetic key unioned into the real set inside
`test_a_new_surface_without_a_cost_is_caught`, purely to show that guard
capable of failing. Recorded because the grep is misleading and the next
reader will run it.

No census row asks for a newsletter surface-census entry, so nothing was
built for this. It is handed over as a measured fact rather than a task.

---

## 7. WHAT THIS WAVE MADE FALSE ELSEWHERE

A measurement falsifies sentences the same way a boundary change does, and
**none of these would have failed a test.**

1. **`readonly.py`'s newsletter entry** said the author-side question was *"a
   question for the first live read, not an assumption for this entry."* The
   read had happened fifteen days earlier. The paragraph KEEPS ITS TEXT and
   gains the answer beneath it, labelled and dated -- the mechanism
   `_audit/2026-09-05-the-newsletter-create-route.md` used on register 9.1,
   because rewriting a correct measurement to remove a stale inference costs
   the reader the sequence.

2. **The same entry's refusal list** named the analytics address in a voice
   that sounds measured. It now says it is not -- section 3a.

3. **`scripts/_probe_newsletter_subscriptions_live.py`'s header** advertised
   four questions and had answered two. It keeps all four and gains the other
   two answers, with the generalisation attached: a live run's capture answers
   more than the run asked, and re-reading it is free.

**Swept and clean:** `tests/test_analytics_creator_boundary.py`'s
`test_the_address_this_reading_informs_is_still_refused` asserts
`/analytics/creator/newsletters/` MUST REFUSE, and it still must -- this wave
admitted nothing, so that control is unmoved rather than stale.
`test_the_admitted_analytics_pages_are_exactly_three` is unmoved at 4 patterns
over 3 pages.

---

## 8. FILES

Shipped:

- `scripts/_probe_newsletter_surface_shape.py` -- NEW instrument. Offline over
  the capture, five controls, `--control` inverts the word census.
- `linkedin_server/newsletters.py` -- `CREATE_ROUTE`, `CREATE_SELECTOR`,
  `CREATE_SELECTOR_ANYWHERE`, two returned fields and their reset. Plain
  Playwright `count()` calls: **no script is injected**, so `INJECTED_SCRIPTS`,
  the `EXECUTED_SCRIPTS` count and the `dom.py` waiver cap are all unmoved.
- `linkedin_server/server.py` -- the tool docstring only. Checked against
  `readonly.docstring_write_claims` before it was written: `[]`.
- `linkedin_server/readonly.py` -- COMMENTS ONLY. No pattern added, no pattern
  changed; the AST digest is unmoved and the boundary invariant is green.
- `_audit/INSTRUMENTS.md` -- register section 23.

Tests:

- `tests/test_newsletter_reader.py` -- 16 -> 21. The fixture self-description
  with the decoy pinned, the scoped pair, the naive selector shown getting it
  wrong, the zero-beside-a-live-control pairing, the detached-frame reset, and
  no href surviving into the reading.
- `tests/fixtures/synthetic/newsletter_subscriptions.html` -- a `<main>`
  wrapper the live page has and this file omitted, the create route where the
  capture draws it, and the decoy outside `main`. It deliberately still draws
  NO analytics route and NO subscribe control, because inventing an affordance
  LinkedIn does not offer lets a reader pass a test and find nothing.

Not shipped, deliberately: any allowlist entry, any WriteSpec, any press, any
navigation.

### The delegated slice, and what it is and is not

`_audit/_slice-newsletter-inventory.md` is a read-only inventory of every
newsletter-touching code path, produced by a delegated implementer and
REVIEWED before any of it entered this report. It is what establishes section
5's *"nothing found uncredited"* from the coverage side: exactly ONE
`@mcp.tool()` in `server.py` reads newsletter data, and the other two
mentions are a sibling tool's docstring and a line inside
`linkedin_server_info`'s self-audit payload.

**AND ONE DEFECT IN IT THAT THE REVIEW MISSED AND A GUARD CAUGHT**, recorded
because it is the argument for reviewing a slice at all. The inventory quoted,
verbatim, a synthetic plus-tagged EMAIL ADDRESS that
`tests/test_no_committed_identity.py` plants as a control in its own file. The
literal is declared where it is planted; **a declaration is scoped to the file
that earns it.** The moment the slice was committed and became tracked, the
shape half of the identity guard parametrised over it and went red -- *"1
unallowed email hit(s), 0 declared"*. It did not fire earlier because that
guard walks TRACKED files and the slice was untracked when I first ran it, and
the commit hook runs the EXACT-VALUE sweep, which is a different instrument.

The remedy was to stop copying, not to widen the allowlist: the literal is
described by shape and the inventory's point is unchanged. **Copying a planted
control into a prose document moves an identifier-shaped string somewhere
nothing declared it** -- and the reviewer who read the slice's sections and not
its characters was me.

**ONE STALENESS CAVEAT, stated rather than smoothed over:** it enumerates
`read_newsletter_subscriptions`'s returned keys WITHOUT `create_control` and
`create_control_outside_main`, because it read the module before this wave's
own commit landed. Its inventory is therefore a correct reading of the
PRE-WAVE tree, which is what it was asked for. Every number in it that this
report leans on was re-measured here.

### Runs

**THE IDENTITY GATE WAS VERIFIED ARMED, NOT ASSUMED**, and the standing scar
is out of date in the good direction: `scripts/sweep_tracked_for_identity.py`
run from inside this linked worktree reports **218 spellings across 16 classes
loaded**, 0 hits across 543 swept files. It is armed here because
`tests.repo_paths.sanitisation_key_path` resolves the key through
`git rev-parse --git-common-dir` and therefore finds the MAIN checkout's
gitignored wordlist. The loaded-spelling count is the half that proves it; the
zero alone would not.

Green baseline at the untouched tree, 14 files: **1508 passed, 0 failed,
75.03s**. `pytest-xdist` 3.8.0 is installed.

After the change, local sweeps: 1186 passed (surface census, membership row,
identity, page-text, navigation-derived, census-surface pricing), 1081 passed
(the five tree-scanning guards), 608 passed (correction-findability, outage,
identity), 299 passed (the three boundary files), 119 passed (server surface
and the tool-surface pins), 21 passed (the newsletter reader). Zero failures
at any point.

**THE FULL SUITE WAS OFFLOADED RATHER THAN RUN LOCALLY.**
`scripts/impact_gate.py --against bf275cf --plan-only` selected 116 of 172
test files -- 67%, above its own 45% line -- and printed *"WIDENING TO THE FULL
SUITE"*. Another wave already held a full-suite `-n auto` run on this box, and
a second one would have serialised both. Pushed instead, 18 shards across
ubuntu 3.10, ubuntu 3.13 and windows 3.13.

### AND CI CAME BACK RED, AND THE RED WAS NOT THIS WAVE'S

Run `35487644895`, 3 of 18 shards failed, all three on
`tests/test_requirements_pins.py::test_the_two_files_declare_the_same_dependencies`.

**MASTER HAS BEEN RED ON EVERY PUSH SINCE 07:53:49 TODAY.** `970a276` added
`pytest-xdist>=3.5` to `requirements.txt` so CI shards could run their files in
parallel, and did not add it to `pyproject.toml`'s `test` extra. Five master
runs failed on it before this wave pushed: `35485075941`, `35485294903`,
`35485333383`, `35486076330`, `35486105863`. It reached my branch because my
branch is cut from master, and it landed in shard 3 rather than master's shard
0 only because adding a test file reshuffles the distribution.

**THE BRIEF I WAS GIVEN SAID "CI green on every push". That premise stopped
being true at 07:53**, and it is worth surfacing beyond this wave: a shared
gate that is red for everyone is the condition under which a wave's OWN red
gets attributed to the known failure and waved through.

Fixed here rather than reported, because it is one line, reversible, and it
blocks the fleet: `pytest-xdist>=3.5` added to the `test` extra, in the
direction `requirements.txt` argues for in its own comment -- *"(`pip install
-e .[test]` installs the same thing from pyproject.toml)"*. Reproduced red
locally first (1 failed, 7 passed), green after (139 passed with
`test_ci_shard.py`). The red IS the control: the guard was seen failing and
then passing on the one line between them.

Re-pushed as CI run `35488009146`.

Three commits, none carrying an AI attribution trailer:

    6a2a992  probe(newsletter): the manager page draws no analytics and no unsubscribe
    92b6882  feat(newsletter): the create control is an eligibility fact, and it is scoped
    9bd57b3  docs(newsletter): three claims the capture made false, and the register entry
