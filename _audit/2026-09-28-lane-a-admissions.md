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
    M C93                          /search/results/all/                                           allowlist silence                           (b)     NOT ADMITTED: a fifth search vertical is D2's to grant (3.4, 7)
    J 38                           /jobs/search-results/?...&alertAction=viewjobs&...             action= (re-addressed to the drawn alert    (a)     NOT ADMITTED: no exact address for action=; a D6 route on /notifications/ (4)
                                                                                                  spelling)
    P S1, P S3, N 199,             (allowlist-silence pages drawn by LinkedIn)                    allowlist silence                           (b)     ADMITTED (3.4)
      J 16, J 50-J 52, J 106,
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
capture lines. **GATE after `cf8109a`:** 1766 passed, the boundary invariant
and the gap-row pin among them.

### 3.4 Twenty-four pages refused by allowlist silence alone

The ruling's second clause: "A page refused by allowlist SILENCE alone, with no
substring, is admitted the same way when a row needs it and no ruling holds
it." Twenty-four anchored lines, one per address, in a `LANE A, CONTINUED`
block; NO exemption is involved, so `_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS`
is byte-identical and only the allowlist digest moves.

    his own profile      /in/me/details/featured/                          P S1
                         /in/me/skill-insights/[0-9]{1,4}/                 P S3
    Premium              /premium/matches/                                 N 199
    his job tracker      ?stage=interview / archived / clicked_apply       J 50, J 51, J 52   (one line each; the three-word line is untouched)
    search               /jobs/search-results/ + query                     J 16
                         /explore-career-insights/ + query                 J 160
    LinkedIn Learning    /learning/, /browse/, /browse/certifications/     J 152
                         /learning/me/my-library/, .../in-progress/        J 154
                         /learning/career-journey/                         J 156   (the read half)
    a company Page       /company/<seg>/about/ life/ products/ product/    J 106, J 109, J 111, J 113, J 114, J 165
                         services/ events/ and insights/?insightType=HEADCOUNT
                         /showcase/<seg>/, /products/<seg>/                J 167, J 166
    resume tailoring     /job-apply-resources/?jobPostingId=[0-9]{1,20}    J 147, J 148, J 149

THE SHAPES ARE THE DRAWN ONES, NARROWED: the company, showcase and product
segment is the roster lines' class, `[A-Za-z0-9\-_]{1,100}` -- no percent and
no dot, so neither an encoded nor a literal dot segment can reach a traversal;
the skill segment is the small integer the tracked skills fixture draws (the
side table's word placeholder for `P S3` was re-addressed to it); the
Insights tab admits exactly `?insightType=HEADCOUNT`, the only value drawn
anywhere; the resume-tailoring page exactly `?jobPostingId=` and digits. The
two search-shaped lines take a query as the classic job search line does,
values from a tool's arguments (D1-SEARCH-AS-READS) -- and the forbidden tuple
still runs first, so the alert links LinkedIn draws into the AI search, which
carry `alertAction=`, stay refused on `action=`.

**`M C93` WAS WRITTEN AND WITHDRAWN BEFORE IT LANDED.** The all-results search
page is refused by allowlist silence alone, and a line for it went in with the
others. The discovery run then went red in three search-admission tests on one
premise: `tests/test_search_admission_blast_radius.py`'s
`test_exactly_the_four_d2_verticals_are_admitted` and its planted-prefix
control, and `tests/test_the_search_results_address_is_refused_before_admission.py`'s
"other five verticals" test. Those pin the measured scope of
D2-SEARCH-VERTICALS-WIDENED -- exactly four closed words -- and a fifth vertical
is that ruling's to grant, not this clause's. The line came out; `M C93` stays
REFUSED with the reason on its row, and section 7 asks it.

**`J 38` IS NOT AMONG THEM EITHER, AND WHY.** The table's address for it was a
constructed keyword search; the page that holds the jobs an alert DELIVERED is
the alert link, which carries `alertAction=` and stays refused. The line was
re-addressed to that drawn spelling (values as placeholders), REFUSED on
`FORBIDDEN[action=]+PATTERN-WOULD-ADMIT`. An exemption for `action=` on a query
of unfixed key order is no exact address. The D6 route is section 4's.

**WHAT DISK SAYS ABOUT THE DRAWN BASIS, read off the raw captures and tracked
fixtures by a read-only child over 169 files (shapes only):** the company
about, life and insights tabs are drawn; products, product, services, events,
top-level showcase and products pages, and `/premium/matches/` are NOT in the
current corpus -- their census cells record each drawn on a 2026-09-21 or
2026-09-23 capture no longer on disk, and the tracked live fixtures are
skeletons whose path words outside the harness list are blanked, so a zero
there is not an absence. The cells' records stand; each capture line says a
redirect is a finding. No stage token but `draft` is drawn anywhere, so
interview, archived and clicked_apply rest on `readonly.py`'s own record that
LinkedIn's payload names them (NAMED basis).

**NOT ADMITTED from the same clause, each with its reason in 2.6/2.7:** a
course video, the AI coach, the Ad Library, news, games, a live video event,
creator hub, the drafts spellings, the comments metric, content search, the
all-results search, the filtered attendee roster, his Page's admin surfaces, a
newsletter's own page.

**RED FIRST:** the twenty-four entries against the previous `readonly.py`, 96
failed, 92 passed -- the four presence tests of each new entry failing, every
sibling and table check passing before and after; with the block, 188 passed.
**THE BLAST-RADIUS TEST CAUGHT A REAL THING ON ITS FIRST RUN:**
`blast_radius.corpus()` already carried `/search/results/all/?keywords=x`, which
the then-present all-results line admitted -- a spelling the author had not
listed. That entry left with its line.

**PINS:** the allowlist digest `fc6839c2e877c011` -> `d3c96a8103316665`, every
other key byte-identical and the tree minus the block hashing to the prior pin;
census count cell 61 -> 85; `tests/test_readonly.py` (three tracker stages and
five company tabs leave its refused tables, recorded, replaced by a second key,
a near spelling, the bare Insights tab and another insightType; the tracker
test's permitted set grows to six with the three-word line asserted
unchanged); `tests/test_company_page_boundary.py` (six tabs move to a
`TABS_ADMITTED_BY_THEIR_OWN_LINE` tuple asserted the roster's way -- exactly one
line, never the root entry; the refusal example becomes the Posts tab);
`tests/test_company_page.py` (the About tab leaves the shaper-boundary
agreement corpus for a `TABS_ON_THEIR_OWN_LINES` check, the People tab's
shape); `tests/test_refusal_names_both_gates.py` (its allowlist-sentence needle
moves from the About tab to the Jobs tab); `tests/test_job_home.py` (the AI
search route it called refused is admitted; the property it guards -- the
home's reader is no route -- now rests on that module carrying no navigation
call, asserted, and on the navigation guard); `census_completion.py`
`b3_admitted` 56 -> 59, `b3_refused` 25 -> 22, `jobs_admitted` 15 -> 34,
`jobs_refused` 31 -> 12. Six also-driven verdicts in the two side tables turned
True with these lines and were re-recorded; both checkers GREEN (98 of 98, 108
of 108).

**A GATE THIS LANE MISSED, FOUND HERE.** The discovery run -- every test file
that drives the read boundary, 80 files, 7010 passed / 29 failed in 24 minutes
on a shared box -- also convicted two things older than this commit:
`tests/test_job_alerts_read_boundary.py` pins the pattern-exemption table's
size, and it had been red since `8a0636a`, because each earlier gate here was a
hand-picked list that left that direct importer out (now 10, each new entry
named); and `tests/test_no_committed_identity.py` read `/company/12345/` in this
lane's own test file as seven undeclared company ids (now the declared
synthetic id the company boundary test already uses). Both are fixed in this
commit. The lesson is the brief's own: the gate is the files that IMPORT what
changed, enumerated, not the files one remembers.

---

## 4. Past the boundary: no reader is owed yet, and the captures that come first

**NO ADMITTED PAGE HAS A TRACKED SKELETON FROM A LIVE CAPTURE, so no reader was
built and no row moved state.** Measured two ways: a search of `tests/fixtures/**`
for each admitted page's own content (the fixtures draw LINKS to several of
these pages -- the skills page's skill-insight anchors, the posting's
resume-tailoring and Insights anchors, the notifications' AI-search anchors --
and never the pages themselves), and a read-only child's census of the 169
files in the raw capture store and the tracked fixtures. A reader built on
anything else would be built on synthetic markup, which moves no row and has
failed live once already. Every admitted row is therefore GAP with gate
MEASURE, and every one has a line in `_audit/_census/capture-queue-reads.tsv`.

**THE QUEUE, 24 lines in Lane K's columns** (surface-id, address, presses,
save, loads, searches, rows):

    admitted pages (15 lines)    invitations-received, invitations-sent, people-followed,
                                 job-application-settings, unfollowed, ads-settings,
                                 featured, skill-insights, premium-matches, tracker-stages,
                                 ai-job-search, career-insights, learning,
                                 company-tabs, resume-tailoring
    spellings first (5 lines)    connections-sort-and-filters (N 24, N 27, N 28),
                                 page-admin-precondition (N A3, N A5),
                                 creator-hub-on-the-dashboard (P L7),
                                 comments-metric-spelling (M C39),
                                 article-drafts-spelling (M C47)
    section 5's specs (4 lines)  people-search-facets, profile-views-pills,
                                 tracker-date-posted, posting-credentials-badge

Nothing on any line is pressed unless the line names the ruling that permits
the press; every address takes its variable segment from the operator or a
tool's arguments, never from a page; the `/mynetwork/` lines share one
badge bracket (the control page before and after, as `linkedin_connections`
takes it). Loads, if every line were taken once: about 45, more than one
session's LIVE-BUDGET-40-LOADS -- the orchestrator orders them.

`M C70` and `N 189` already have capture specs (lane S, `F.4` and `F.8` in
`_audit/2026-09-24-lane-s-people-search.md`); no second line was written.

**D6 ROUTES, found on the way, none built here:**

* `J 38`, the jobs an alert delivered: the alert notifications on the admitted
  `/notifications/` page carry `originToLandingJobPostings`, the delivered job
  ids (tracked `tests/fixtures/notifications.html`, four links).
  `shape.notification_handles` already lifts `search_keywords` and
  `company_id` out of those links and not this key; returning the ids lets
  `linkedin_job_detail` read each. Whether the in-app list carries every
  delivered job is unmeasured.
* `N 86`, followers of a member: the people-search facet `followerOf` is on
  record in three tracked live fixtures; its value is a member id, which
  OTHER-MEMBER-IDS-AS-READS permits from a tool's arguments.
* `N 24`, `N 27`, `N 28`: lane S moved `N 25` and `N 26` (the same list's
  search and filter) to COVERED-UNFIRED through the people search filtered to
  his first degree. Whether sort, Talks-about and Open-to have a people-search
  spelling is what the `connections-sort-and-filters` line records.
* `N 82`, `J 17`, `J 57`, `N 197`: section 5.

---

## 5. The 17 admitted rows a press or a ruling holds

One paragraph each: the decision the row waits on, its evidence, and this
lane's recommendation. The evidence was gathered read-only by a child into a
scratch file and every quote re-checked against the tree before it entered
here. No press default is implemented: for none of the PRESS rows below is the
shipped gate's evidence pattern -- a per-control basis AND a before/after
reading proving no state change -- already on record for that row's control,
so each gets a measurement spec instead (section 4 lists the lines).

**P C8 (PRESS) -- save his profile as a PDF.** Waits on two presses on
`/in/me/`: the More-menu opener, a disclosure, which the shipped gate now
answers `control_not_judged` (the side table's `no_sensitivity_basis` is the
pre-404da96 name; same outcome) because the `[aria-expanded]` shape also
matches nine member links on the capture of his profile, so only a
position-pinned judgement could admit it; and the Save-to-PDF item, an ACT
press whose shape was never measured. The download transport is built
(`linkedin_server/cdp_download.py`, off by default). No evidence pattern on
record. RECOMMENDATION: the orchestrator decides once whether a position-pinned
judgement (a control identified by its index on a recorded capture, re-verified
by shape at press time) is admissible -- the same question holds `N 76` -- and
the item press is specified as his own act (not outward: it downloads his own
profile) with its own capture.

**M C96 (PRESS) -- the content-credentials panel on a posting's image.** Waits
on measuring the badge control's shape; `press.py` declares no basis for
`/jobs/view/`. No evidence on record. RECOMMENDATION: a capture of a posting
that draws the badge, recording the control's attributes and the panel it
opens; then the press default is the orchestrator's, on that evidence.

**N 76 (PRESS) -- the follow link behind a menu on his own profile.** Waits on
the orchestrator's undecided call on index-pinned disclosure judgements (as
`P C8`): the trigger's `[aria-haspopup]` shape is judged an action on `/in/me/`
because all nine matches on the capture are member links. No evidence pattern.
RECOMMENDATION: decide the position-pinned question once for both rows.

**N 82 (RULING) -- a people-search filter whose label this surface may not
read.** The row is held because "nothing available tells a people filter from
a jobs badge without reading the label". D6 OFFERS ANOTHER ROUTE: lane L2 and
lane S recorded the LinkedIn-written facet `activelyHiring` among the query
keys of LinkedIn-authored people-search hrefs; `linkedin_server/people_search.py`
does not compose it, and no tracked fixture carries it (audits only).
RECOMMENDATION: the gate is not a ruling; compose `activelyHiring` from a tool
argument under D1-SEARCH-AS-READS once a tracked capture carries the facet (a
capture line, `people-search-facets`, records it), and the row moves by D6 on
the shipped people-search reader.

**N 86 (PRESS) -- "TERMINAL BY THIS ROUTE" stands, and D6 now has a route on
record that nobody reported.** The All-filters press is not relitigated. But
the LinkedIn-written facet `followerOf` IS on record: three tracked live
fixtures (`tests/fixtures/live2/n84.html`, `n87.html`, `n94.html`, committed
`5f70af8` on 2026-09-28) carry it in eleven hrefs, after the side-table note,
the census cell and lane L2 said "No people-search facet for this filter is on
record". Its value is a member id, which `OTHER-MEMBER-IDS-AS-READS` permits
from a tool's arguments, never from a page. `people_search.py` does not
compose it. RECOMMENDATION: compose `followerOf` from a caller-supplied member
id; the people-search reader already reads the captured results markup, so the
row can move to COVERED-UNFIRED by D6 on that build. Not built in this lane
(section 7).

**N 90, N 91, N 92 (PRESS) -- TERMINAL BY THIS ROUTE, and no facet on record.**
The facet census over the tracked fixtures finds none for these three filters.
RECOMMENDATION: nothing to rule; a capture line records any LinkedIn-written
people-search href carrying these filters on the surfaces that already draw
search links (profiles, company Pages, the jobs pages), and D1 applies the
moment one is found.

**N 133 (PRESS) -- applying a viewer filter on his profile-views page.** The
side table calls the restore-and-prove press "a build"; it WAS built
(`linkedin_server/view_switch.py`) and fired with a proving before/after
reading -- for `N 134`'s option ("Interesting viewers / verified", live lane
session 1, Entry 7). `N 133` was never re-assessed against it. The evidence on
record covers that one option, not the time-range or Company pills this row
needs. RECOMMENDATION: re-gate `N 133` PRESS -> MEASURE: one live run of the
shipped view switch over each remaining pill, with the same before/after
reading, is the whole of what remains (a measurement spec, not a decision).

**N 174 (RULING) -- his pending group requests.** Observable only once a
pending request exists; creating one is an act toward a group, now built behind
the grant under EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS ("RSVPs and group
membership requests") and fired only at a group he names
(OPERATOR-NAMES-THE-TARGET). The join write itself (census `M C61`) is not
built. RECOMMENDATION: build the join request behind the grant; the row then
waits only on the operator naming a group.

**N 197 (PRESS) -- copy a link to a group.** The side table places the control
in "the group page's own menu" at `/groups/<id>/`; the 2026-09-05 measurement
opened the per-row menus on the `/groups/` ROOT and never the item. D6 is the
row's own open question: a group's address is composed from its numeric id.
RECOMMENDATION: apply D6 -- the package composes `/groups/<id>/` from a
caller-supplied id, which is the link the control copies -- and the row moves
on that route's proof; the press is then unnecessary.

**M C43 (RULING) -- a post's text, shaped.** Held by FEED-CONTENT-READ-RULING
(counts and relations only). NAMES-AT-RUNTIME (the operator's, 2026-09-24) is
registered as amending that ruling for what a read RETURNS, but its declared
returns are names and group and event titles, not post text, and nothing has
applied it to this row. RECOMMENDATION: the orchestrator applies the
operator's 08:11 principle ("do not ask whether to deliver a capability ...
mitigate the risk") to post text as it was applied to names: returned at
runtime, sanitised, marked untrusted, never stored, one post per call. That is
a call on what may be RETURNED, not an outward act.

**J 17 (RULING) -- search from his device's current location.** Waits on the
operator: a geolocation grant over CDP would persist in his real browser
profile. Its own record already says the capability is served another way:
"the location parameter already reaches every documented result set (a523131,
decide-retire s3.7)". RECOMMENDATION: keep the grant with the operator, and
ask the orchestrator to apply D6 -- the search he wants is delivered by naming
the location -- which needs no grant at all.

**J 56 (PRESS) -- filter his tracker by date posted.** The side table says "a
checkbox is off press.SANCTIONED_SHAPES"; the fixtures it cites draw the
opener as `div[role=button][aria-expanded]`, a sanctioned shape. What refuses
it is the missing basis for `/jobs-tracker/`. RECOMMENDATION: the basis is a
press-gate default (the orchestrator's); no before/after reading is on record,
so a capture line opens the pill under the shipped view switch and reads the
tracker's counts before and after.

**J 57 (RULING) -- his connections reachable for a tracked job.** Waits on
the composition question (`_audit/2026-09-21-the-jobs-direction.md` 6.1); lane
D's D6 sweep left it out (a boolean against a count). Since NAMES-AT-RUNTIME,
the people-search reader may return WHO. RECOMMENDATION: re-run D6 on it --
the people search filtered to his first degree and the posting's company, both
composed from tool arguments, returns exactly the connections the row asks
for.

**J 110 (RULING) -- a company Page's Home and Posts prose.** Held by
`shape.company_about_card`'s docstring, which calls "THE DESCRIPTION IS
MEASURED AND NOT PUBLISHED ... a ruling rather than an oversight". It is
unregistered and names no decider; D3's logic reaches it (a refusal written
beside code is a question, not a ruling). RECOMMENDATION: the orchestrator
decides it under NAMES-AT-RUNTIME and the 08:11 principle as for `M C43`
(organisation prose returned at runtime, untrusted, never stored); note also
that the drawn `/company/<slug>/home/` and `/posts/` spellings stay refused.

**J 131 (RULING) -- whom to message about a job, and whether it costs a
credit.** The names half is answered (NAMES-AT-RUNTIME); what remains is
whether the server should duplicate a ranking the `linkedin-jobs` skill
already serves from mail -- unregistered. RECOMMENDATION: an orchestrator's
call on duplication, applying the same rule to every row filed
SERVED-BY-GMAIL-SKILL at once rather than row by row.

---

## 7. Questions for the orchestrator, each with its ground

1. **R1's second question, on the invitation manager's received tab (`N 13`,
   `N 14`, `N 19`).** Ground: `_audit/2026-08-30-linkedin-nine.md` 2.2, "Q2
   emission | unmeasured, and the cost lands on someone else | Whether an
   invitation marked seen is visible to its SENDER has never been measured."
   The tab is admitted (the badge is a passive cost by the ruling's own
   words); nothing loads it until its capture line is merged. If the
   orchestrator reads Q2 as an outward cost, the received-tab line and its
   exemption come out together (both carry `invitation-manager/?$`), and the
   sent tab is unaffected.
2. **How many named settings pages "one at a time" allows (`N 39`, `P P15`,
   and `/jobs/application-settings/`).** Ground: ONE-NAMED-SETTINGS-PAGE-AT-A-TIME,
   "ONE NAMED settings page below `/mypreferences/d/` -- one at a time, never
   the family, never a wildcard ... A second page needs a second ruling", and
   the 2026-09-27 admission recorded as "the orchestrator's APPLICATION of the
   ruling above". Lane A applied it the same way, each page by exact address.
   The two `/mypreferences/d/` pages are commit `cf8109a` alone; the
   application-settings page is `435a133` alone.
3. **Is "stored job applicant accounts" a credential surface (`P M9`,
   `J 77`)?** Ground: the census cell, "Stored job applicant accounts" /
   "View / delete stored third-party applicant accounts", and the ruling's
   exclusion of "a credential, recovery, session or security surface". This
   lane read it as accounts held for signing into employers' systems and left
   it refused on `job-application`; that is an inference, not a measurement.
4. **The two (c)? rows that rest on this lane's inference, not a record:
   `M C95` (a live broadcast may register its viewer to the broadcaster) and
   `J 153` (playing a course records progress).** Ground: none on record
   either way; each census cell names only the payload ("a reader could
   publish ... facts, never its words").
5. **The three (e) rows: `M C99` games, `M C98` LinkedIn News, `J 159` the Ad
   Library.** Ground: the brief's own class (e), with games as its example;
   news and the ad library are this lane's reading of "purpose doubtful" for a
   server whose rows are his account and his search. Overridable by one word.
6. **`M C101`, a newsletter's own page.** Ground: `readonly.py`'s newsletters
   entry -- "Its slug is ROUTINELY ITS AUTHOR'S NAME", "THIS PACKAGE COULD NEVER
   ASSEMBLE THIS ADDRESS", and "it would put one in every log line that records
   a page load". Under D3 these are not a ruling; NAMES-AT-RUNTIME and
   PAGE-MAY-VETO-NEVER-SUPPLY answer two of the three. The third is whether a
   navigated address is PERSISTED anywhere, which PEOPLE-DATA-MITIGATIONS
   ("never stored") would forbid for a slug that is a name.
7. **`M C93`, the all-results search, as a fifth search vertical.** Ground:
   D2-SEARCH-VERTICALS-WIDENED, "four CLOSED segments,
   /search/results/(people|companies|groups|events)/", and its measured scope
   in `tests/test_search_admission_blast_radius.py`
   (`test_exactly_the_four_d2_verticals_are_admitted`). The page is drawn (as
   hashtag links on posts) and refused by allowlist silence alone; widening D2
   to `all` is a re-application of D2, and the line lane A wrote for it was
   withdrawn when those tests named that scope.
8. **Decisions section 5 recommends rather than takes:** whether a
   position-pinned control judgement is admissible (`P C8`, `N 76`); applying
   D6 to `J 17` (the location parameter), `N 197` (a group link composed from
   its id) and `J 57` (people search, first degree and the company); applying
   the 08:11 principle to post text (`M C43`) and organisation prose
   (`J 110`); duplication of skill-served rows (`J 131`); press-gate defaults
   for `/jobs-tracker/` (`J 56`) and `/jobs/view/` (`M C96`).
9. **Two D6 builds this lane names but did not take** (section 4): composing
   the people-search facet `followerOf` (on record in three tracked live
   fixtures) for `N 86`, and returning an alert notification's
   `originToLandingJobPostings` job ids for `J 38`.
