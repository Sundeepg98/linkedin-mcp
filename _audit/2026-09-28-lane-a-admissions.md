# Lane A: refused reads past an act substring, and the rows a press or a ruling holds

Lane A (`la-admissions-lead`). Brief written by the orchestrator 2026-09-28
22:55 IST; relaunched 2026-10-10 from master `3c8edc2` (CI green, run
36460989178) on its own worktree branch.

**OFFLINE THROUGHOUT.** No LinkedIn page was loaded, no browser was started or
attached to, port 9224 was never touched. A live session (session 7, another
lane's) ran on this box the whole time, so every test run here was targeted and
serial (`-p no:randomly`, no `-n`), and from 11:35 IST under the orchestrator's
narrower gate policy: the touched tests, their direct importers and the census
instruments, each run in the background, never the full suite.

WRITTEN AS THE LANE RUNS. Sections land with the commits that make them true;
anything not yet landed is not described.

---

## 0. The slice, enumerated -- and where disk disagreed with the brief

**(i) 72 refused read rows, measured, not inherited:**

    _audit/_census/read-addresses.tsv  class REFUSED   38 = 19 forbidden substring + 19 allowlist silence
    _audit/_census/jobs-directions.tsv class REFUSED   34 =  4 forbidden substring + 30 allowlist silence
                                                            (3 on "/jobs/application", 1 on "job-application")

The 72 rows sit on 48 distinct addresses. Every address was driven through the
shipped `readonly.assert_read_url` and, separately, against every entry of
`readonly._FORBIDDEN_URL_SUBSTRINGS` -- not only the first one the gate names.

**(ii) 17 admitted read rows held by a press or a ruling, not 12.** The brief
names twelve, all in `read-addresses.tsv`: RULING `N 82`, `N 174`, `M C43`;
PRESS `P C8`, `M C96`, `N 76`, `N 86`, `N 90`, `N 91`, `N 92`, `N 133`,
`N 197`. Its own definition ("the admitted read rows whose gate column is
RULING or PRESS") also reaches five lines of `jobs-directions.tsv`: RULING
`J 17`, `J 57`, `J 110`, `J 131` and PRESS `J 56`. Section 5 treats all
seventeen.

**THREE THINGS DISK SAID THAT THE TABLES DID NOT:**

1. `/jobs/application-settings/` IS DRAWN. `tests/fixtures/synthetic/drawn_routes.txt`
   -- the corpus of route shapes drawn by anchors on six surfaces a live
   authenticated session captured on 2026-09-20 -- carries it. The side table
   files `P M12`'s spelling INFERRED and the other seven rows' NAMED; the
   address is served-and-drawn, which strengthens every admission below that
   rests on it.
2. Several refused addresses trip MORE than the substring the gate names first:
   `/jobs/application-settings/` also trips `settings`; `/psettings/sessions`
   also trips `settings`; the connections list's query variants trip both
   `/invite` and `/connect`. An exemption that excused only the first would
   have admitted nothing, so every exemption below names the full measured set.
3. The alert notifications LinkedIn draws on the admitted `/notifications/`
   page link to the semantic search with a key `originToLandingJobPostings`
   whose value is the list of job ids the alert delivered -- `J 38`'s payload,
   on a page already read (tracked `tests/fixtures/notifications.html`, four
   such links). Section 4 takes it up as a D6 route.

---

## 1. The rulings commit, and the control it turned red

`ec7d245` copies `_audit/2026-09-28-rulings-build-classes.md` byte-identical
(sha256 prefix `db2876cf82fd2d7e`, ASCII, LF) and registers its five ids in
`scripts/build_rulings_index.py` after NAMED-PROFILE-READ-BEHIND-A-GRANT:
EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS, HIS-OWN-SETTINGS-NOT-OUTWARD,
HIS-OWN-CURATION-NOT-OUTWARD, PURCHASES-STAY-MANUAL, READ-PAST-AN-ACT-SUBSTRING.
Each anchor is the ruling's own `RULED:` line, present once. Derived views
regenerated to a fixed point (73 rulings, 260 documents).

**THE REGISTER'S FOUNDING CONTROL WENT RED, AND THE FIX IS IN THE JUDGED TEXT,
NOT THE TEST.** `tests/test_the_rulings_register_is_derived.py::test_the_question_that_caused_this_register_is_findable`
asks `find("does a forbidden substring alone count as a ruling")` and requires
EXCLUDED-RULED-ADMISSION and INCIDENTAL-CAPTURE-IS-NOT-A-RULING first. The
ranker counts distinct query tokens by SUBSTRING match, so READ-PAST scored 4
("alone" in its note, "count" inside "account" in its claim) and
EVERY-OUTWARD-CLASS scored 2 (`ACCOUNT-DESTRUCTION`, `PERMANENTLY_FORBIDDEN` in
its note) and sorted ahead of INCIDENTAL on the id tie-break. `1a8d51f`
rewords the judged claim and notes; measured after: 3, 2, 2, every other entry
below 2. **MERGE NOTE for the three lanes copying the same document:** an
entry for READ-PAST that says "account" or "alone" reddens this control again
at the merge.

---

## 2. The 72 refused rows, address by address

Classes as the brief defines them: (a) the substring's recorded ground is an
ACT and the page is his own account's -- admit; (b) allowlist silence only and
no ruling holds the page -- admit; (c) the ground is the READ itself; (d) the
ground is a ruling of the operator's; (e) the page serves only a row whose
purpose is doubtful. Two further outcomes are not classes but facts, and each
is named where it applies: NO SERVED SPELLING (the address on record is a
constructed placeholder, so no exact pattern can be written) and PRECONDITION
UNMEASURED.

### 2.1 The six act substrings of the server's first commit

`"/jobs/application"`, `"/invite"`, `"invitation"`, `"/connect"`, `"/follow"`
and `"/unfollow"` all arrived together in `1a94cf9` (2026-08-21, "feat:
read-only LinkedIn reader MCP server"), with no per-entry argument. The
recorded ground is the tuple's own comment, unchanged since:

> Substrings that must never appear in a navigation target, checked before
> the allowlist as a second, independent gate. Belt and braces: a future
> pattern edited too loosely still cannot reach these.

and the commit message's account of what the gate is for:

> a navigation allowlist, the only door to page.goto, so a keyword cannot
> become a navigation to an action url

An ACT ground: each word names an action url family (applying, inviting,
connecting, following, unfollowing). Ruling (b) of 2026-09-23
(`WRITE-CLASS-B`) withdrew the read-only rule the fence served, as the census
cells lane R returned to GAP already record ("a purpose ruling (b) of
2026-09-23 withdrew"). (`git log -S` under Git Bash returned nothing for the
slash-led needles until `MSYS_NO_PATHCONV=1` stopped MSYS rewriting `/invite`
into a Windows path; the attribution was then read off `git show 1a94cf9`.)

### 2.2 R1, and the one question it leaves open

`N 13`, `N 14` and `N 19` carry R1 as well as R2. R1 is
`_audit/2026-08-30-linkedin-nine.md` section 2.2, a WAVE's side-effect gate,
not an operator's ruling and not registered:

> Q1 consumption | YES | E1. `/mynetwork/` carries the pending-invitation
> badge. This package has MEASURED two members of that badge family and both
> reset on load ...
> Q2 emission | unmeasured, and the cost lands on someone else | Whether an
> invitation marked seen is visible to its SENDER has never been measured.

and the document itself: "This is a DERIVED refusal". Under
READ-PAST-AN-ACT-SUBSTRING, "a badge the load may clear is a passive cost
(`D5-PASSIVE-COST-IS-NOT-A-ROW`), recorded on the row" -- that answers Q1.
**Q2 is not a badge; it would be a cost to other people, and nobody has
measured it.** The received tab is admitted (the brief names "his invitation
manager" among the pages the ruling is for), Q2 is recorded on all three rows
and named in section 7, and nothing loads the page until the orchestrator
merges its capture line.

### 2.3 What row P M1 actually rests on

`P M2`, `M4`, `M5`, `M6` (and the side table's `P M12`) say "reopening it is the
operator's (row M1)". `P M1`'s cell carries two layers. The older one, a wave's
REOPENER:

> REOPENER, NAMED, in two independent halves because this row has two
> reasons: the forbidden-substring entry `"/jobs/application"` being
> re-ruled by the operator, OR the upload verb entering
> `writes.PERFORMABLE`.

and the newer one, lane R's return to GAP on the orchestrator's delegated
call:

> BLOCKER, NAMED: "/jobs/application" (the read-only server's first commit,
> no argument recorded) refuses /jobs/application-settings/: a fence for a
> read-only server whose purpose, the apply cut and the read-only rule,
> ruling (b) withdrew

So M1 rests on the forbidden substring and nothing else. "Re-ruled by the
operator" is a wave's reopener, not a ruling of his; the substring has no
recorded argument beyond 2.1; and the operator's own ruling (b) is the thing
that withdrew the apply cut. Class (a), not (d).

### 2.4 The settings family

`/jobs/application-settings/` also trips `settings`;
`/mypreferences/d/job-application-accounts`, `/mypreferences/d/unfollowed` and
`/mypreferences/d/categories/ads` sit under the settings tree. Their grounds:

* `"/mypreferences/d/categories/"` and `"/psettings/"`, `42e90e3` (2026-08-30):
  "the category pages carrying the toggles are refused twice over"; the
  readonly comment, "The category pages carry the toggles; they are the part
  that must stay unreachable however the allowlist is edited later." An ACT
  ground: a toggle is a write.
* `"settings"` and `"job-application"`, the 2026-09-03 block `8e20f27` pinned
  ("closing three classes the anchored allowlist was refusing alone ... a
  defence-in-depth asymmetry rather than an open door"): a second gate for the
  same toggle-bearing family.

Admission into the family is by name: ONE-NAMED-SETTINGS-PAGE-AT-A-TIME (the
operator's, 2026-08-31: "ONE NAMED settings page below `/mypreferences/d/` --
one at a time, never the family, never a wildcard ... A second page needs a
second ruling") and MESSAGING-SETTINGS-CAPABILITY-LEVEL ("a setting is admitted
BY NAME or not at all"). The second page was admitted 2026-09-27 as "the
orchestrator's APPLICATION of the ruling above", and
HIS-OWN-SETTINGS-NOT-OUTWARD (2026-09-28) restates "Settings pages are still
admitted one by name". Lane A applies it the same way: each page by its exact
anchored address, never a family line. How many named pages that ruling's
"one at a time" allows at once is the orchestrator's reading, and section 7
asks it.

### 2.5 The table

    rows                           address (as admitted, or as on record)                         refusal (every substring tripped)           class   outcome
    N 13, N 14, N 19               /mynetwork/invitation-manager/                                 invitation                                  (a)     ADMITTED (3.1)
    N 9, N 11                      /mynetwork/invitation-manager/sent/                            invitation                                  (a)     ADMITTED (3.1); the table carried the root, the Sent tab is this leaf
    N 38                           /mynetwork/network-manager/people-follow/following/            /follow                                     (a)     ADMITTED (3.1)
    P M2, M4, M5, M6, M12;         /jobs/application-settings/                                    /jobs/application, settings                 (a)     see 3.2
      J 71, J 72, J 73
    P M9, J 77                     /mypreferences/d/job-application-accounts                      job-application                             (a)     see 3.2
    N 39                           /mypreferences/d/unfollowed                                    /unfollow                                   (a)     see 3.2
    P P15                          /mypreferences/d/categories/ads                                /mypreferences/d/categories/                (a)     see 3.2
    N 24, N 27, N 28               /mynetwork/invite-connect/connections/?<query>                 /invite, /connect (the exemption stops      (a)     NO SERVED SPELLING: ?foo=1 is the boundary's own placeholder; see 2.7
                                                                                                  at the bare list)
    N A3                           /company/<slug>/admin/following/                               /follow                                     --      PRECONDITION UNMEASURED: whether he administers any Page; two candidate spellings
    P N9                           /psettings/sessions                                            /psettings/, settings                       (c)     NOT ADMITTED: a session and security surface
    P N13                          /checkpoint/                                                   allowlist silence                           (c)     NOT ADMITTED: a sign-in challenge
    J 82                           /jobs/view/<digits>/apply/?openSDUIApplyFlow=true              allowlist silence                           (c)     NOT ADMITTED: "Opening it is the first step of an application"
    J 116-J 120, J 126             /preload/guideOverlay/?interop=guideOverlay&query=<prompt>     allowlist silence                           (c)     NOT ADMITTED: "opening it starts a generation rather than a read"
    P M11                          /resume-builder/                                               allowlist silence                           (c)?    NOT ADMITTED: INFERRED address; "a builder is a composer-class surface that may autosave"
    M C95                          /video/event/<urn>                                             allowlist silence                           (c)?    NOT ADMITTED: see 2.6
    J 153                          /learning/<digits>/<digits>/                                   allowlist silence                           (c)?    NOT ADMITTED: see 2.6
    N 65, N 103, N 178             /in/<member>/                                                  allowlist silence                           (d)     NOT ADMITTED: NO-THIRD-PARTY-PROFILE-LOAD as amended; see 2.6
    M C99                          /games/<name>/                                                 allowlist silence                           (e)     NOT ADMITTED
    M C98                          /news/story/<slug>/                                            allowlist silence                           (e)     NOT ADMITTED
    J 159                          /ad-library/search/?companyIds=<digits>                        allowlist silence                           (e)     NOT ADMITTED
    M C101                         /newsletters/<slug>/                                           allowlist silence (a written refusal in     (b)     NOT ADMITTED here; named, see 2.6
                                                                                                  the newsletters entry)
    J 155                          /learning/chatbot/                                             allowlist silence                           (b)     NOT ADMITTED: the read half exists only after a typed question, a write
    N A5                           /company/<slug>/admin/                                         allowlist silence                           (b)     PRECONDITION UNMEASURED, and the credit-balance sub-path is unrecorded
    P L7                           /creator-hub/                                                  allowlist silence                           (b)     NO SERVED SPELLING: NAMED only, and LinkedIn draws the hub as /dashboard/ (P L8)
    M C39                          /analytics/creator/content/?metricType=<token>                 allowlist silence                           (b)     NO SERVED SPELLING for the comments metric
    M C47                          /pulse/drafts/ (also /drafts/, /content/drafts/)               allowlist silence                           (b)     NO SERVED SPELLING: three NAMED guesses, none drawn
    M C70                          /search/results/content/                                       allowlist silence                           (b)     NO SERVED SPELLING for the row's page (search INSIDE a group)
    N 189                          /events/<digits>/attendees/?facetConnectionOf=<x>              allowlist silence                           (b)     NO SERVED SPELLING: a test fixture's, never captured
    P S1, P S3, N 199, M C93,      (allowlist-silence pages drawn by LinkedIn)                    allowlist silence                           (b)     see 3.3
      J 16, J 38, J 50-J 52, J 106,
      J 109, J 111, J 113, J 114,
      J 147-J 149, J 152, J 154,
      J 156, J 160, J 165-J 167

### 2.6 The rows not admitted, each with its ground quoted

**(c) the read itself.**
* `P N9` `/psettings/sessions`: the census cell -- "Shows location, IP, device,
  browser, last sign-in", "Class: a pure read (SECURITY: the active
  sessions)". A session surface is exactly what the ruling excludes ("a
  credential, recovery, session or security surface"), and
  CREDENTIAL-SETTINGS-NEED-THE-OPERATOR names its sibling P N10.
* `P N13` `/checkpoint/`: "the challenge renders at /checkpoint/ ...
  config.AUTHWALL_MARKERS turns a landing into a reported failure" -- a sign-in
  challenge, excluded by the ruling's own words.
* `J 82`, the Easy Apply route: the side table, "Opening it is the first step
  of an application, apply_job's territory" -- a GET that changes state.
* `J 116`-`J 120`, `J 126`, the guide overlay: "Its query is a prompt and its
  href carries a conversation id, so opening it starts a generation rather than
  a read" (Amendment A13 of `_audit/2026-09-03-linkedin-gap-blockers.md`, as the
  side table records it). The flag half of `J 116` is already derivable
  (`linkedin_premium_job_collection(0)`), per the same note.
* `P M11` `/resume-builder/` -- lane L1's ground, "a builder is a
  composer-class surface that may autosave", on an INFERRED address nothing
  draws. Marked (c)? because the ground is argued, not measured.
* `M C95` `/video/event/<urn>` -- **THIS LANE'S INFERENCE, labelled as one**:
  a LIVE broadcast is a page whose load may register a viewer the broadcaster
  sees. Nothing on record measures it either way, and the drawn address
  carries a urn (`/video/event/urn:li:ugcPost:<digits>` in the tracked
  notifications fixture), not the table's `/video/event/12345/`.
* `J 153` a course video -- INFERRED address (invented segments), and playing a
  course records progress in his own Learning history, a state change; this
  lane's inference, not a recorded ground.

**(d) a ruling of the operator's.** `N 65`, `N 103`, `N 178`: another member's
profile. `NO-THIRD-PARTY-PROFILE-LOAD` (op=YES, the operator's removal of the
third-party profile pattern, 2026-09-04) as amended by
NAMED-PROFILE-READ-BEHIND-A-GRANT -- the operator, 2026-09-28 08:01, verbatim
"Yes, I'm giving you permission." -- which built the named-profile door, a
second and narrower door this table does not govern. The rows already say so
("this line stays REFUSED; the row waits on a capture").

**(e) purpose doubtful.** `M C99` LinkedIn's daily games (the brief's own
example; "a game is played by presses no gate sanctions"); `M C98` a LinkedIn
News story, editorial content with no tie to his search or his account;
`J 159` the Ad Library, which ads a company runs. Each is named, not admitted;
any of them reopens on the orchestrator's word that it serves the product.

**`M C101`, a newsletter's own page -- written grounds, named rather than
overridden.** The newsletters entry in `readonly.py` refuses
`/newsletters/<slug>/` in its own words: "Its slug is ROUTINELY ITS AUTHOR'S
NAME" and "THIS PACKAGE COULD NEVER ASSEMBLE THIS ADDRESS ... No numeric
newsletter address is known to exist". Under D3 those are an allowlist
comment, not a ruling; NAMES-AT-RUNTIME answers the first for what a read
RETURNS, and PAGE-MAY-VETO-NEVER-SUPPLY lets the slug come from the caller.
What remains is the comment's other premise -- "it would put one in every log
line that records a page load" -- which is a question about what this package
PERSISTS, and that is the orchestrator's to weigh against PEOPLE-DATA-MITIGATIONS
("never stored"). Section 7.

**`J 155`** the Learning AI coach: R+W, and its read half -- the coach's
answers -- exists only after a typed question, "a write to an AI product" (the
census cell). Admitting the page buys no read.

### 2.7 No served spelling, or a precondition first

* `N 24`, `N 27`, `N 28` -- sort, "Talks about" and "Open to" on his
  connections list. The admitted pair stops at the bare list, and its own
  comment refuses any query ("a query is where a filter that names a person
  would arrive") -- an allowlist comment (D3). The substrings' ground is an act
  (2.1), so (a) holds in principle; but `?foo=1` is the boundary's placeholder,
  not LinkedIn's spelling, and an exact pattern needs the real one. The D6
  precedent is lane S's: `N 25` and `N 26` left the table for COVERED-UNFIRED
  through the people search filtered to his first degree. Section 4 records
  what the people search composes today and what a capture must record.
* `N A3` and `N A5` -- his Page's following list and invitation-credit balance.
  Both need a measurement that he administers any Page first (lane L1, read
  triage 6.2), and `N A3` has two candidate spellings
  (`/admin/following/`, `/admin/page-following/`) of which only the first
  carries `/follow`.
* `P L7`, `M C39`, `M C47`, `M C70`, `N 189` -- the address on record is a
  name nobody has seen served or a placeholder; each gets a capture line that
  records the spelling LinkedIn draws.

---

## 3. The admissions as built

### 3.1 His invitation manager and the people he follows

Three lines in a contiguous `LANE A` block of `readonly._ALLOWED_URL_PATTERNS`
(after the follower-list line) and three entries in a `LANE A` block of
`readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS`, each pair naming one
address:

    /mynetwork/invitation-manager/                          excuses {"invitation"}   N 13, N 14, N 19
    /mynetwork/invitation-manager/sent/                     excuses {"invitation"}   N 9, N 11
    /mynetwork/network-manager/people-follow/following/     excuses {"/follow"}      N 38

No query, no sub-path; `_FORBIDDEN_URL_SUBSTRINGS` unchanged at 33.

**RED FIRST.** `tests/test_lane_a_admissions.py` was written before it could
pass and run against the base `readonly.py` (the file restored from `HEAD`,
then put back and compared byte-for-byte):

    18 failed, 5 passed in 1.10s

The 18 are every admission, line-shape, exemption, either-gate-alone and
blast-radius test on each of the three addresses. The 5 that passed are the
three sibling-refusal tests, the tuple-size test and the duplicate check --
true before and after, which is what a control that the admission must not
move should do. With the lines: `23 passed`.

**THE CONTROLS** (each in that file): both slash forms admitted; exactly one
anchored line matches, with no `.*`, `.+`, `\w`, `\S` or `[^`; the exemption
excuses exactly the substrings the address trips, measured against the shipped
tuple; every sibling still refused on the gate that names it -- a query, an
unrecorded `received/` leaf, act-shaped sub-paths (`accept/`, `withdraw/`,
`unfollow/`), traversals, `/mynetwork/invite-connect/invitations/`, a group
invite, `/in/me/follow/`, a Page's follow and unfollow, `/feed/follows/`, his
Page's following list, the people-follow family root and `/mynetwork/` itself;
drop the exemption and the substring refuses saying "A READ PATTERN DOES ADMIT
THIS ADDRESS"; drop the line and the allowlist refuses; and each pair newly
admits exactly its two spellings over `blast_radius.corpus()` plus every
address in the file, refusing nothing new.

**PINS MOVED, each with its cause:** `tests/test_readonly.py` (the invitation
manager and the following list leave two refused tables, recorded "WAS HERE
UNTIL 2026-10-10", replaced by their query and sub-path neighbours);
`tests/test_l1_follower_list_carve_out.py` (its sibling control is now the
following list WITH a query); `tests/test_refusal_names_both_gates.py` and
`tests/test_read_addresses.py` (their FORBIDDEN+NO-PATTERN control is now his
Page's following list, `N A3`'s address); the boundary-invariant digests
(`_ALLOWED_URL_PATTERNS` `18e5958586c2c367` -> `c0249a5bfde871da`,
`_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS` `14f567fd160048a8` ->
`6f99bceb4d139db3`; the base file, which is the tree minus exactly the lane A
block, hashes to the prior pin on all thirteen keys); the census count cell
(55 -> 58 patterns).

**CENSUS.** Six rows REFUSED -> ADMITTED, gate MEASURE, in `read-addresses.tsv`
(checker GREEN, 98 of 98); each census cell gains a dated note; state GAP
unchanged on all six (no capture, no reader). `census_completion.py`:
`b3_admitted` 43 -> 49 and `b3_refused` 38 -> 32, re-derived from the measured
values in the same commit.

**GATE, after the commit** (`8a0636a`, with the triage commit `2f94b79`
before it): the lane A file, the boundary, refusal and side-table tests, the
census-prose and gap-row guards, the four document guards, the three derived
views, the identity sweep over the committed blob and the dict-literal guard --
1667 passed in 186s.

### 3.2 His job application settings

One more pair in the same blocks, its own commit so it can be taken or left
alone:

    /jobs/application-settings/     excuses {"/jobs/application", "settings"}
                                    P M2, P M4, P M5, P M6, P M12, J 71, J 72, J 73

Both substrings the address trips are excused, and only for it -- the 2026-09-03
`settings` word keeps its full reach on every other spelling (a settings page
the dark-mode entry declined by name, `/public-profile/settings`), and
`/jobs/application` keeps it on an application, the applied-jobs list and any
query or sub-path of this page. `/mypreferences/d/job-application-accounts`
stays refused on `job-application` (2.6).

**RED FIRST:** the file's new entry against the previous `readonly.py`, 6
failed, 1 passed (the sibling test, true before and after); with the pair, 30
passed.

**PINS:** digests `c0249a5bfde871da` -> `94bf0916c1be3824` and
`6f99bceb4d139db3` -> `ffebed391e628195`, the base hashing to the prior pin on
all thirteen keys; census count cell 58 -> 59. **BASIS RAISED** to MEASURED on
all eight lines: the drawn-route corpus carries the address (section 0). The
side tables keep each row's own source, because their checkers accept
`.py/.md/.tsv/.json` citations and the corpus is a `.txt` file; the note
names it. Both checkers GREEN (98 of 98; 108 of 108).
`census_completion.py`: `b3_admitted` 49 -> 54, `b3_refused` 32 -> 27,
`jobs_admitted` 12 -> 15, `jobs_refused` 34 -> 31, re-derived. One capture
line added (`job-application-settings`).

**P M12 STAYS HONEST ABOUT ITS PAGE.** The side table tied "AI resume feedback"
to this address by inference from M1; the live lane captured a job posting for
the same row on 2026-09-28. Both captures record whether they carry it, and
the reader is whichever page does.

**THE GATE AFTER THIS COMMIT (`435a133`) WENT RED TWICE, AND ONE OF THE TWO WAS
REAL.** 1764 passed, 2 failed:

* `test_the_read_only_boundary_is_where_it_was_re_frozen` -- NOT this commit's
  defect. The background run read `readonly.py` while the next commit's two
  lines were being written into it; the live digest it reported is that next
  state's. Re-run after the next commit (3.3).
* `test_gap_rows_on_refused_addresses_is_pinned`, expected 78, measured 76 --
  REAL, and missed here: a GAP row whose cell backticks an address the gate
  refuses on a substring stops counting when that address is admitted. Run
  against the lane's base boundary and against the tree and diffed, the rows
  that left are exactly `P M1` (its cell backticks `/jobs/application-settings/`;
  it left in THIS commit, so this commit's true count was 77 and its pin
  stayed 78 for one commit) and `P P15` (the next commit). Fixed forward in
  3.3, with both named.

### 3.3 Two named settings pages: what he unfollowed, and his advertising data

A commit of their own, for the reason 2.4 gives: how many named pages
ONE-NAMED-SETTINGS-PAGE-AT-A-TIME allows at once is the orchestrator's reading.

    /mypreferences/d/unfollowed         excuses {"/unfollow"}                       N 39
    /mypreferences/d/categories/ads     excuses {"/mypreferences/d/categories/"}    P P15

`N 39`'s address is MEASURED (its cell: "found live and written down");
`P P15`'s is drawn on the settings index (the live lane's capture,
2026-09-23). Every other category page, the category root, a query, a
sub-path and a longer leaf stay refused on the category substring; a Page's
unfollow, the people list's query and an act-shaped sub-path stay refused on
`/unfollow`; `/mypreferences/d/demographic-info-copy` stays refused by the
allowlist alone (a sensitive-attribute page HIS-OWN-SETTINGS-NOT-OUTWARD
names).

**RED FIRST:** the two new entries against the previous `readonly.py`, 12
failed, 2 passed (the two sibling tests); with the pairs, 44 passed.

**NOT ADMITTED, AND WHY, FOR THE THIRD SETTINGS-FAMILY PAGE ON THE LIST:**
`/mypreferences/d/job-application-accounts` (`P M9`, `J 77`). Its census cell
calls it "Stored job applicant accounts" / "View / delete stored third-party
applicant accounts". Read as written, these are accounts LinkedIn holds on his
behalf for signing into employers' application systems -- a credential-adjacent
surface, which the ruling excludes. That reading is THIS LANE'S, not a recorded
measurement; the page has never been loaded. Section 7 asks it.

**PINS:** digests `94bf0916c1be3824` -> `fc6839c2e877c011` and
`ffebed391e628195` -> `28643e7ca768b7df` (the base hashing to the prior pins on
all thirteen keys); census count cell 59 -> 61;
`tests/test_the_settings_index_addresses_are_pinned.py` moves both addresses
to "allowlist match" and its named-refusal count 16 -> 14;
`tests/test_gap_rows_on_refused_addresses.py` 78 -> 76 with both rows named;
`census_completion.py` `b3_admitted` 54 -> 56, `b3_refused` 27 -> 25. Two
capture lines.
