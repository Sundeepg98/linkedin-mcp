# The messaging gap is a WRITE gap, and the reads are blocked on decisions

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- section 4 was stale in all four of the factual claims it makes about the code: the read allowlist holds 41 patterns and not 22, four of the eleven surfaces it calls unreachable are reachable, `set_input_files` has been sanctioned since 2026-09-04, and eight documents discuss it. Ten GAP rows carried the third of those as their stated reason. Section 6 below has the measurement; the census now carries the correction in place plus a guard that re-derives it.

Wave `messaging-and-content`, 2026-09-20, from master `e6b11e5`.
Scope: the **83 GAP rows** of `_audit/_census/messaging-and-content.md`.
**No browser was opened. No LinkedIn page was loaded. No write was fired. No
session was touched.** Every measurement below is offline -- against committed
files, against the shipped modules, and against captures another wave had
already taken and left on disk.

---

## 0. THE HONEST LEDGER LINE, FIRST

    GAP rows at wave start                    83
    rows banked to COVERED-PROVEN              0   forbidden -- that needs a fire
    rows moved to COVERED-UNFIRED              0   and section 3 is why, row by row
    rows moved out of GAP                      1   C43, onto a ruling made 2026-09-05
    rows inflated                              0

    census cells corrected with a MEASUREMENT 16   state unchanged on all 16
    stale claims in section 4 corrected        4   every factual claim it made
    instruments shipped                        3   each shown failing
    guards shipped                             3   each shown failing
    library modules shipped                    1   wired, not orphaned
    defects found in a shipped instrument      1   and fixed: section 5
    defects found in my own output             2   sections 4.2 and 4.3

**THE ONE-LINE READING. Seventy-one of the eighty-three are WRITES on a server
whose `writes_enabled` is false, so no wave with any amount of time closes
them. Eleven are reads and one is a read-and-write; of those twelve, ELEVEN
have no tool at all and the twelfth delivers half its row. Not one of the
twelve is blocked on a reader somebody could sit down and write** -- each is
blocked on an address nobody has opened, a ruling nobody has made, or a press
this package does not sanction. A build-only wave can therefore move very few
rows here, and this document is mostly the evidence for that sentence.

---

## 1. THE TRIAGE, AS EXACT INTEGERS

Produced by `scripts/triage_messaging_gap_rows.py`, which imports three
shipped instruments and reimplements none of them: `count_census_states` for
the parse, `enumerate_gap_rows` for the row set, and
`reader_closable_blockers.direction_of` for the R/W column. It REFUSES to
print a tally unless all three of its controls pass -- see section 6.3.

    ./venv/Scripts/python.exe scripts/triage_messaging_gap_rows.py

### 1.1 By direction, which is the census's own column and not my judgement

| direction | rows | share |
|---|---:|---:|
| **W** -- a write on LinkedIn | **71** | 85.5% |
| **R** -- a read | **11** | 13.3% |
| **R+W** -- a read half and a write half (`M28`) | **1** | 1.2% |
| unreadable direction cell | **0** | |
| | **83** | |

### 1.2 By blocker, from the committed `_audit/_census/blocker-map.tsv`

Nothing here is assigned by this wave; the map is a derived artefact with its
own guard (`tests/test_blocker_map_is_derived.py`) and this is a join.

| blocker | rows | shape |
|---|---:|---|
| `FILE-UPLOAD-UNSANCTIONED` | 10 | W10 |
| `CONVERSATION-OVERFLOW-MENU` | 9 | R1 W7 R+W1 |
| `GROUPS-SURFACE` | 7 | W7 |
| `NEWSLETTER-SURFACE` | 6 | R1 W5 |
| `ARTICLE-SURFACE` | 5 | R1 W4 |
| `COMMENT-IDENTIFIER` | 4 | W4 |
| `MESSAGE-REQUESTS-SURFACE` | 4 | R1 W3 |
| `COLLABORATIVE-CONTENT` | 3 | W3 |
| `EVENTS-SURFACE` | 3 | W3 |
| `MENTION-TAG-CONTROLS` | 3 | W3 |
| `POST-COMMENT-CONTROLS` | 3 | R1 W2 |
| `CONTENT-ANALYTICS-SURFACE` | 2 | R2 |
| `GROUP-CHAT-SURFACE` | 2 | W2 |
| `PER-MESSAGE-OVERFLOW-MENU` | 2 | W2 |
| `PICKER-SURFACES` | 2 | W2 |
| `POLL-SURFACE` | 2 | W2 |
| `SAVED-POSTS-SURFACE` | 2 | W2 |
| `THREAD-REPLY-BOX` | 2 | W2 |
| eleven blockers holding one row each | 11 | R4 W7 |
| | **83** | |

The eleven singletons: `CELEBRATION-COMPOSER` W, `EMBED-SETTING` W,
`FEED-CONTENT-READ-RULING` R, `MESSAGE-REACTION` W,
`MISSING-PARAM-MESSAGING` R, `OFF-PLATFORM-WIDGET` R, `POST-DRAFT-SURFACE` W,
`PUBLISH-POST-AUDIENCE-PARAM` W, `REPORTING-FLOWS` W,
`SEARCH-RESULTS-SURFACE` R, `UNASSIGNED` W.

### 1.3 The three buckets the brief asked for

| bucket | rows | what it means |
|---|---:|---|
| **WRITES -- not buildable on this server** | **71** | `writes_enabled` is false and connect/message/apply/follow/post were deliberately cut. None of these is a wave's to close |
| **READS with no tool** | **11** | and section 3 shows each is blocked on an address, a ruling or a press -- not on a reader |
| **READS with a tool that delivers part of the row** | **1** | `C38`, and the part it does not deliver is the part the row is named for |

**I did not measure an absence for any row.** `MEASURED-ABSENT` is a real
state and this file does not put a single row into it: measuring an absence
here needs the surface open, and I was forbidden the surface. The three rows
where an absence is now reproduced OFFLINE (`M9`, `M28`, and the composer's
file inputs under `C3`-`C7`) are recorded as repetitions of somebody else's
live reading, which is worth something and is not the same thing.

---

## 2. THE 71 WRITES, AND WHY ONLY ONE COULD BE RE-FILED

The cheap move available to a wave holding 71 write rows is to re-file them as
`EXCLUDED-RULED` under prohibitions that already exist. That move is
sometimes right -- this repository has found it repeatedly, and
`_audit/2026-09-19-cross-slice-rulings.md` section 2 names its signature: *a
GAP row whose own note "states the ruling's own premise and files GAP
anyway."* So it was tested rather than assumed.

**34 of the 71 were swept against every ruling written down in this
repository** -- `writes.PERMANENTLY_FORBIDDEN`'s nine entries, the
MESSAGING-SETTINGS ruling, the MENTION-COMPOSITION ruling, the
FEED-CONTENT-READ-RULING, and the five ruling documents of 2026-09-05 and
2026-09-20. The sweep's verdicts:

| verdict | rows |
|---|---:|
| **RULED-ALREADY** -- a written ruling decides this act | **0** |
| **ADJACENT-NOT-COVERED** -- a prohibition is close and its written scope excludes this act | **5** |
| **NOT-RULED** -- no ruling considers it | **29** |

**The zero is the result, and it is a good one.** It means the propagation
work on this slice is already done: `_audit/2026-09-19-prohibition-key-sweep.md`
ran the nine-key sweep to exhaustion across all 334 GAP rows before this wave
started, and content-tail, article-publish, groups-admission, the-decides and
premium-block each wrote their hits back. **What is left in the write half is
genuinely unruled, not under-propagated**, and a wave that re-filed any of it
would be manufacturing a number.

The five ADJACENT rows are worth naming, because each is a considered
exception rather than an oversight, and re-deriving them would cost somebody a
day:

| row | the near ruling | why it does not reach |
|---|---|---|
| `M25` Leave a conversation | `delete_or_withdraw_anything` | self-removal from participation is not destroying content he published; the census cell already said so |
| `M31` Mark a conversation read or unread | `mark_notifications_read` | the ruling's SECOND ground was 34 controls measured on the notifications surface; that measurement was never taken for messaging, and `_audit/2026-09-19-prohibition-key-sweep.md` declined to extend it |
| `M47` Respond to a Recruiter InMail | `auto_accept_or_auto_reply` | the load-bearing words are *"that he did not read"*; an operator-reviewed reply is an open design question, not a forbidden one (`_audit/2026-09-20-the-premium-block.md`) |
| `C54` Create a collaborative post | `C55`'s collaborator retirement | a collaborative post can be created before anybody is invited |
| `C67` Edit or delete a group post | `delete_or_withdraw_anything` | the delete half meets it; the edit half does not |

### 2.1 The one write-side correction that WAS owed, and it is a reason, not a state

Ten of the 71 -- `M14 M15 M18 C3 C4 C5 C6 C7 C27 C45` -- carried
*"`set_input_files` unsanctioned (s4)"* as their stated reason. **That has been
false since 2026-09-04.** It is entry 7 of 7 in
`readonly.SANCTIONED_MUTATIONS`, sanctioned by the operator at `615a5c4`, and
eight documents under `_audit/` discuss it.

**The rows stay GAP** -- `_audit/2026-09-20-the-decides.md` section 1.5 ruled
exactly that, *"the blocker RETIRES as a blocker ... Its 15 rows stay GAP,
correctly"* -- and `writes.UPLOAD_ACTIONS` ships `frozenset()`, pinned empty.
So all ten cells now name the successor blocker that actually holds them,
which that document had already enumerated and nobody had written back into
the census:

    M14 M15 M18   UPLOAD-WIRING-UNBUILT    aim measured, mechanism built, wiring left
    C3 C4 C5 C6 C7 COMPOSER-PRESS-REFUSED  a SHIPPED TERMINAL REFUSAL
    C27            PICKER-SURFACES
    C45            ARTICLE-SURFACE

---

## 3. THE TWELVE READS, ROW BY ROW -- WHY A READER CLOSES NONE OF THEM

Every `linkedin_*` tool registered in `linkedin_server/server.py` was checked
against every one of the twelve, by following the payload into the reader that
produces it rather than by grepping tool names.

| row | verdict | what actually blocks it |
|---|---|---|
| `M9` Review declined message requests | NO-TOOL | no address. Three independent mechanisms now read zero for a requests destination -- their href census, their button census, and this wave's offline vocabulary run. **All three are facts about the vocabulary**, and 30 of 42 accessible names stayed unmatched |
| `M28` View and restore archived conversations | NO-TOOL | `dom.MESSAGING_FILTERS` is a closed set of seven and holds no `archive`. The affordance is in a menu that needs a press this package does not sanction |
| `M34` Search messages by keyword | NO-TOOL | the allowlist admits `/messaging/` with **no query string at all**, so a url-driven search is refused before a parameter could be added; and the inbox draws no `<form>`, so the search is client-side and needs a fill on a read path |
| `M49` Read delivery / read indicators | NO-TOOL | `shape.messaging_overview` publishes HIS receiver-side `unread` flag, a different fact. The sender-side indicator lives in a thread; `/messaging/thread/<id>/` IS admitted, so this one is blocked on a reader **plus** the cost of opening somebody's thread |
| `C29` Sort comments | NO-TOOL | needs a post to be addressable (`C42`) and a sort control nobody has enumerated |
| `C38` View post analytics | **PARTIAL** | `linkedin_creator_analytics` returns an account-wide per-DAY impressions series. The row asks for PER-POST and for VIEWER DEMOGRAPHICS, and it returns neither. See 3.1 |
| `C39` Analytics for your comments | NO-TOOL | `chart_labels.MEASURED_METRICS` is `("impressions",)`, and the allowlist entry for that address carries no query group while LinkedIn selects a metric with `?metricType=` -- so no other metric is reachable through this server at all |
| `C43` Read a post's text | **RULED** | see section 4.1 -- this is the one row that moved |
| `C48` View all your articles | NO-TOOL | `/in/me/recent-activity/articles/` and `/pulse/` both refuse; the blocker's single `allowlist +1` is owed at least twice |
| `C70` Search content within Groups | NO-TOOL | `search_results.py` was built FOR this row and is deliberately unwired, and no `/search/` address is on the allowlist. It is waiting on a decision in another slice |
| `C72` Share a post off LinkedIn (read half) | NO-TOOL | no reader returns a post's shareable link or embed code. See 3.2 -- I declined to claim this one |
| `C83` View newsletter analytics | NO-TOOL | `/newsletters/<slug>/analytics/` is unmeasured and unadmitted, and `tests/test_analytics_creator_boundary.py` holds the second candidate as a MUST-REFUSE. `linkedin_newsletter_subscriptions` records the absence as measured: the three words appear **zero** times in its own 74,234-character capture |

### 3.1 `C38` is the closest any of them comes, and the blocker is now NARROWER rather than closed

Measured 2026-09-20 against a capture of `/analytics/creator/content/` -- an
address already on the allowlist, already opened by a tool banked
COVERED-PROVEN:

    anchors parsed                                   27
    /feed/update/urn:li:share:<digits>/               4 hrefs, 2 distinct urns
    /analytics/post-summary/urn:li:activity:<digits>/ 2 hrefs, 2 distinct urns

**`/analytics/post-summary/` IS the per-post surface `C38` has been costed an
unnameable `allowlist +1` for, and LinkedIn draws it on a page this server
already opens.** That is the ninth instance of this repository's
`allowlist +1` finding, and the first time in this slice that the address
exists rather than being a placeholder for an unknown.

**The row still does not move, for three reasons and each is independent:**
the address is not admitted here and an admitted address is not a served one;
no reader exists for it; and the viewer-demographics half needs a shaped
reader, which `readonly.py`'s own entry for the sibling address already scopes
-- *"this line admits no reader, and any reader built on it must go through
`census_shape` plus `census_redact_rare`."* What this wave supplies is the urn
that address needs (section 4.2).

### 3.2 `C72` -- the row I could have claimed and did not

`linkedin_server/item_addresses.py` returns `/feed/update/urn:li:share:...`
permalinks for his own posts, and a post's permalink is, in plain terms, the
link you would paste off LinkedIn. Reading the row's words loosely, that is
its read half.

**I am not claiming it.** The row's blocker is `OFF-PLATFORM-WIDGET`; LinkedIn's
off-platform share offers a copy-link, third-party share buttons and an EMBED
CODE, and a tool that returns a canonical permalink does none of those things
by pressing anything LinkedIn drew. A tool that cannot do what its row claims
is worse than an untouched GAP. **Flagged for the operator as a judgement
call rather than banked on my own say-so.**

---

## 4. WHAT WAS BUILT

### 4.1 `C43` -- the one row that moved, and the ruling is fifteen days old

**`C43` *Read a post's text*: GAP -> EXCLUDED-RULED.** Not a new decision.

The lead ruled it on 2026-09-05
(`_audit/2026-09-05-lead-rulings-round-two.md` section 5):

> Reading the feed means reading other people's posts. Ruled: counts and
> relations only, never text or names, built structurally as in 3.

and, in the same section, why a filter could not discharge it:

> `census_substitute` returns a person's name **UNCHANGED** ... **No
> shape-based guard will catch a name.**

It was BUILT the same week as `linkedin_server/feed.py`
(`_audit/2026-09-05-settings-rest.md` section 1) with the guarantee in the
SIGNATURE in both directions. **A post's text is the exact payload that ruling
names and forbids** -- not an adjacent one. And the twin row of the same
blocker, `C74` *Read your feed*, was banked out of GAP on the same reasoning
on 2026-09-19. `C43` was the half nobody wrote back.

Bound by `tests/test_c43_rests_on_the_feed_content_ruling.py`, which is a
second instance of the law `tests/test_a_retired_row_rests_on_a_live_assertion.py`
states -- that file could not hold this row, because its own invariant is that
every entry names a parameter in `FORBIDDEN_PARAMETER_NAMES` and this row
rests on a different assertion.

**SHOWN FAILING, three ways, each against a COPY of the census so no contended
file was edited:**

    CONTROL: the real tree, unmutated                     reds 0
    MUTATION 1: C43's state flipped back to GAP           reds 1  names the row and its state
    MUTATION 2: the C43 row deleted outright              reds 1  names it MISSING, not absent
    MUTATION 3: `text` added to feed._PERMITTED_...       reds 1  names the assertion

**REOPENER: the operator ruling that a post's text may cross the boundary,
shaped.** That is the mechanism, not a consolation -- it is how dark mode
became the one writable setting.

### 4.2 `linkedin_server/item_addresses.py` -- a second route to the item urn

The census's `C42` records the constraint more of this slice's content half
rests on than any missing control: *"To open `/feed/update/<urn>/` you need a
urn, and no tool in this server returns one."*

**That sentence is no longer literally true and the part that matters still
is.** `linkedin_my_activity_items` DOES return item keys, off `/in/me/`, and
says so in its own docstring -- but every recorded live run of that route
refused (`no_page_owner_heading`, then `no_self_assertion` on five consecutive
calls). The primitive exists in code and is unavailable in practice.

This module reads the same primitive off a page that is MEASURED TO SERVE.
Counts by default; whole anchored `urn:li:<letters>:<digits>` matches only on
explicit opt-in, copied from `linkedin_open_messaging`'s `include_names` and
for its reason. Wired into `creator_analytics.read_content_analytics` as an
ADDITIVE field -- same page, no extra navigation, and `C40`'s banked keys
unchanged.

**A DEFECT IN MY OWN OUTPUT, found by running the probe I had just written.**
The field was called `distinct_items` and the module docstring said *distinct
items 2*. The probe returned **4**, because LinkedIn draws TWO urn families --
`urn:li:share:` on the permalink and `urn:li:activity:` on the analytics
address -- whose digit runs do not match (overlap 0 over four 19-digit runs).
So four distinct urns are consistent with two posts drawn twice and equally
consistent with four posts, **and nothing in the reading separates them.** A
field called `items` would have answered *four* to a question it cannot
answer. Renamed `distinct_urns`, and a test asserts the module publishes no
field called `items` at all. This is the defect `newsletters.py` records in
its own docstring -- ten anchors, five newsletters -- caught this time by
running the instrument instead of by reading it.

**A SECOND DEFECT IN MY OWN OUTPUT, found by mutation.** The disclosure
property was first asserted as *no four-character substring of any input
appears in the output*. It went red on `link` -- a fragment of this module's
own word `permalink` that is also a fragment of `linkedin.com`. **A check
whose failures are ordinary English gets its threshold raised until it
certifies nothing.** Replaced with the closed-alphabet property `menus.py`
carries: every published string must be a word the module declares.

### 4.3 The offline label probe, and a defect in a SHIPPED instrument

`scripts/_probe_labels_in_capture.py` asks the questions the live menu probe
asks, of a capture already on disk. It imports `menus.classify` / `menus.tally`
rather than matching labels itself, so the single-word rule that the
`Star Anise` defect bought is not re-bought; `menus.tally` takes no label as a
parameter and its output alphabet is 28 closed words, which is what makes it
safe to run over `/messaging/` at all -- there, a label IS a person's name by
LinkedIn's own design.

Its first run found a hole in the instrument it imports. See section 5.

### 4.4 `scripts/triage_messaging_gap_rows.py` -- the triage, as a script

Section 1's integers are its output. It refuses to print a tally unless its
three controls pass, because a triage that cannot be trusted to have read
every row should print nothing.

---

## 5. THE VOCABULARY COULD NOT SEE THE CONTROL THE SURFACE DRAWS ELEVEN TIMES

Run over a capture of `/messaging/` taken 2026-09-20 by a sibling wave:

    aria-labels parsed   42      matched   1      buttons  50

**One.** And eleven of those 42 nodes carry the accessible name
`Star conversation`.

`menus.VOCABULARY` holds a `star` term. It did not match, and it was RIGHT not
to under its own rule: `star` is a ONE-WORD term, and a one-word term must
match the WHOLE label, because a given name adds tokens. That rule exists
because `classify("Star Anise")` once returned `star`. **The rule is correct
and the phrase list was short** -- nobody had added the two-word form LinkedIn
actually draws.

The same run over `/messaging/compose/`: 40 labels, **two** `input[type=file]`
nodes, and `attach` matched **one** of them. `Attach a file ...` was in the
list; `Attach an image ...` was not. A tally understating a two-input upload
surface by half is the worst direction to be wrong in on a surface whose whole
question is what it can be given.

Both phrases added. Both are multi-word, which is what makes them safe under
the module's own rule: a multi-word phrase may be CONTAINED, and no name
contains `star conversation`. **Only the observed direction was added** -- no
`unstar conversation` was invented, because nobody has seen one.

    before   messaging: matched  1      compose: attach 1 of 2 file inputs
    after    messaging: matched 12      compose: attach 2 of 2

**SHOWN FAILING:** removing either phrase turns
`tests/test_labels_in_capture.py` red. And the widening's BOUND is asserted
too -- `Star Anise` must stay unmatched, and four name-shaped labels whose
first token is a vocabulary term must match nothing.

**WHAT THIS BUYS A CENSUS ROW.** `M30` reads *"starring itself was never
considered."* It is drawn eleven times on the surface the vocabulary was
written for. The row stays GAP -- starring is a write -- but **its blocker
assignment is wrong**: the map files it under `CONVERSATION-OVERFLOW-MENU` and
the control is drawn directly on the conversation row with no menu to open.
Handed to whoever owns `scripts/build_blocker_map.py`; not edited here,
because two siblings are building in other worktrees.

---

## 6. SECTION 4 OF THE CENSUS WAS STALE IN EVERY FACTUAL CLAIM IT MADE

The section is titled *THE READ BOUNDARY IS THE STRUCTURAL CAUSE OF MOST OF
THE 88*. It is the section that explains why most of this slice is a GAP. It
was written 2026-09-03 and never re-run against the code, while the same file
took eighteen further commits on 2026-09-19 that edited other sections.

| the section says | measured 2026-09-20 |
|---|---|
| the allowlist is **22** url patterns | **41**. 20 of the 22 survive; **2 were deliberately DROPPED** (the generic `/in/<slug>/` pair, at `956358d` on 2026-09-04 -- no pattern today can address a third party's profile by slug at all); **21 added** |
| nothing in it reaches Groups / Events / Live / newsletters / saved posts / hashtags / article drafts / post analytics / creator analytics / scheduled posts / media upload | **4 of the 11 are reachable today**: `/groups/`, `/events/`, `/mynetwork/network-manager/newsletters/`, `/analytics/creator/content/`. The other 7 refuse, and the substring checks confirm rather than assume it: `schedul`, `hashtag`, `live`, `video` each match **0** of 41 patterns |
| `set_input_files` has not been sanctioned, and no document has ever discussed it | **false both ways.** Entry **7 of 7**, since `615a5c4` on 2026-09-04; **8** documents under `_audit/` discuss it |
| "`fill` has since been sanctioned" | still true, entry 5 of 7 |

**THE REPAIR IS NOT A NEW NUMBER.** A corrected count rots exactly as fast as
the one it replaced, and `readonly.py` predicted this in its own words: *"a
count in prose beside a list it cannot read goes stale in silence, and knowing
that does not stop you writing one."* So the census now has a guard,
`tests/test_the_census_prose_matches_the_boundary.py`, which reads the claims
out of the document and compares them with the shipped boundary. The DOCUMENT
is the subject; the census is what fails.

### 6.1 The code that produced those figures, so they are re-derivable

    from linkedin_server import readonly
    len(readonly._ALLOWED_URL_PATTERNS)                       # 41
    readonly.is_read_url("https://www.linkedin.com/groups/")  # True
    readonly.is_read_url("https://www.linkedin.com/events/")  # True
    readonly.is_read_url(
        "https://www.linkedin.com/mynetwork/network-manager/newsletters/")  # True
    readonly.is_read_url(
        "https://www.linkedin.com/analytics/creator/content/")             # True
    {v for _p, _f, v in readonly.SANCTIONED_MUTATIONS}
    # {'click', 'press', 'fill', 'select_option', 'set_input_files'}

The controls, run in the same session, because a table of False verdicts from
a dead instrument looks exactly like a careful measurement:

    readonly.is_read_url("https://www.linkedin.com/feed/")       # True   accepts
    readonly.is_read_url("https://www.linkedin.com/psettings/")  # False  refuses
    readonly.is_read_url("https://example.com/")                 # False  refuses

### 6.2 And the capture figures, re-derivable by anyone holding a capture

    ./venv/Scripts/python.exe scripts/_probe_item_addresses_in_capture.py --capture <a capture>
    ./venv/Scripts/python.exe scripts/_probe_labels_in_capture.py        --capture <a capture>

Both refuse to report when they parse nothing, both have `--self-test`, and
neither can print an identifier: the first hard-wires `include_identifiers`
False with no flag to turn it on, the second publishes only `menus.tally`'s
closed alphabet. **The captures themselves are gitignored and always will be**
-- they carry full PII. `tests/fixtures/synthetic/creator_content_addresses.html`
is the committed artefact that reproduces the analytics figures exactly, and
`tests/test_item_addresses.py` requires the two to agree, which is what makes
those numbers checkable from a clone.

### 6.3 The triage instrument's three controls, and each is shown failing

| control | what it catches | shown failing by |
|---|---|---|
| the shipped counter agrees | a join that silently dropped rows | `test_the_counter_agreement_control_can_fail` -- hand it a total wrong by one |
| every row joins to a blocker | a tally over 80 of 83 that looks identical to one over 83 | `test_the_join_coverage_control_can_fail` -- punch a hole in the map |
| the direction reader refuses | a clean table of `unknown` from a dead reader | inherited from `reader_closable_blockers.control_negative`, which prints its own four planted cases |

---

## 7. WHAT I DECLINED TO DO, AND WHY

**1. The `open_overflow_menu` sanction, handed to "the next wave" by name.**
`_audit/2026-09-19-messaging-menu-enumeration.md` section 3.1 proposes a
fourth `SANCTIONED_MUTATIONS` entry with four conditions and prices it at *one
digest recompute, tests shown failing, one page load. Pay-off: 13 of these 19
rows.* Nine of those rows are mine.

**I did not build it**, for the reason its own author gave and one more.
Theirs: *"a menu's CONTENTS are unknown in a way the seven filter pills are
not ... An overflow menu is a plausible home for `Delete`."* Mine: the entry
is pinned three separate ways in `tests/test_readonly.py` -- a verbatim
tuple-equality pin, a live recount, and a hardcoded `7` -- on a file two live
waves are editing, and **the entry cannot be verified without the page load
this wave was forbidden.** Widening the mutation boundary and leaving it
unfired is the one change in this package I would least like to hand over
unverified. The proposal stands where its author left it.

**2. Re-filing write rows to move a number.** Section 2. The sweep returned
zero and zero is the answer.

**3. Claiming `C72`.** Section 3.2.

**4. Moving `C88`/`C89` under the settings ruling.** They are settings, the
ruling reads *a setting is admitted by name or not at all*, and their cells
state its premise -- which is the propagation signature. But
`_audit/2026-09-19-content-tail.md` section 4.2 MEASURED these two rows
yesterday and left them GAP deliberately. **Overriding a considered decision
taken one day ago, with no new evidence, is re-litigation, not propagation.**

**5. Editing `blocker-map.tsv` for `M30`.** The assignment is wrong and the
map is a derived artefact another wave owns. Reported, not edited.

---

## 8. FOR WHOEVER TAKES THIS SLICE NEXT

1. **The reads are worth four decisions, not four readers.** `SEARCH-RESULTS-SURFACE`
   (`C70` here, 20 rows census-wide) needs an address ruling. `ARTICLE-SURFACE`
   needs `allowlist +2`, not +1. `CONTENT-ANALYTICS-SURFACE` needs
   `/analytics/post-summary/` admitted -- and that address is now NAMED, which
   it was not this morning.
2. **`M49` is the cheapest read left.** Its surface is already admitted
   (`/messaging/thread/<id>/`), so it is a reader plus the cost of opening
   somebody's thread -- the only one of the twelve where no decision is owed
   first.
3. **`UPLOAD-WIRING-UNBUILT` (`M14 M15 M18`) is the only buildable write
   sub-group in the slice**, and it is three rows: aim measured by `accept`
   declaration, mechanism built and shown working end to end,
   `writes.UPLOAD_ACTIONS` pinned empty. Do NOT aim at the two accessible
   names -- `_audit/2026-09-20-the-decides.md` section 1.3 records both
   unreproducible live on 2026-09-05, and this wave's offline run reproduces
   the names off an 11:45 capture only, which is not the same thing.
4. **The overflow-menu proposal is still the biggest single pay-off here** and
   it needs one page load plus a boundary widening. It is an operator-shaped
   decision, not a wave-shaped one.
