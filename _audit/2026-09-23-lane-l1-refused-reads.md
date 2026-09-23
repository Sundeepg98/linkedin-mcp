claude-opus-5-5[1m]

# Lane L1, refused reads: 24 rows at the read boundary, taken one at a time

Wave `lane-l1-refused-reads`, 2026-09-23, worktree branch off master `b0d3ab8`.
**OFFLINE THROUGHOUT.** No browser was started or attached to, no LinkedIn
page was loaded, port 9224 and `_state/chrome-profile` were never touched.
Raw captures under the main checkout's gitignored `_state/` were READ to learn
structure; none was copied into a tracked file.

WRITTEN AS THE WAVE RUNS. Entries are numbered, not timed: an agent's sense of
elapsed time is not an instrument.

---

## 0. THE PLAN, AS OPENED

1. Derive the slice from `_audit/_census/read-addresses.tsv` (class REFUSED)
   and check it against the brief's 24 = 20 NO-PATTERN + 4 FORBIDDEN.
2. For every row: is loading its page a pure read, on cited evidence; is
   there a WRITTEN refusal already standing against it (the brief says
   "nobody ruled these out" -- that is a premise to check per row, not a
   fact to inherit); and is the address one LinkedIn DRAWS, or one somebody
   named.
3. Admit only what survives all three, each with the narrowest anchored
   pattern, closed segments, a measured blast radius and a negative control.
4. Build a reader only where the page's structure is recorded concretely --
   a real capture, or a measured sibling -- and mark the rest NEEDS-CAPTURE.
5. Forbidden-substring carve-outs, if any, in a separate `REVIEW:` commit.
6. Census cells, the side table, generated files, gates, one cold check.

---

## LOG

### Entry 1 -- the slice, derived, and it agrees

**24 = 20 NO-PATTERN + 4 FORBIDDEN, no discrepancy.** Taken by reading the
REFUSED class out of `_audit/_census/read-addresses.tsv` and re-driving every
address through the shipped `readonly.is_read_url` and the checker's own
`check_read_addresses.refusal_of` (imported), at `b0d3ab8`: 24 of 24 refused,
24 of 24 refusal kinds agree with the table. The four FORBIDDEN are exactly the
brief's: P L2b and N A3 on `/follow`, P M12 on `/jobs/application`, N 183 on
`/mypreferences/d/categories/`. The boundary at HEAD: 42 allowed patterns, 33
forbidden substrings (imported, not grepped).

None of the 24 sits under `/messaging/` or `/notifications/`, so the brief's
exclusion removes nothing.

### Entry 2 -- the premise "nobody ruled these out" does not hold for five rows

The brief says the 20 fail "only because the read boundary has no pattern for
them". Checked per row against `readonly.py`'s own entries and
`_audit/RULINGS.md`, that holds for 15 and fails for 5, where a WRITTEN,
reasoned refusal already stands:

    N 178   another member's profile -- the pattern was REMOVED on the
            operator's 2026-09-04 ruling; `known_side_effects` and
            PERMANENTLY_FORBIDDEN name the act (a durable view record)
    N 177   a group's member directory -- "not admitted here or anywhere",
            the lead's 2026-09-05 split, in the groups root entry
    N 102   a company's People tab -- "out of scope by the same ruling that
            put a group's roster out of scope by name" (company entry)
    N 99    a school's alumni tab -- "a roster of MEMBERS ... refused by this
    N 100   anchor rather than by a promise" (school entry)

D3 (the read triage's open question) asks whether those refusals COUNT AS
WRITTEN for the census's EXCLUDED-RULED bar. It does not ask whether to admit
the pages, and this lane does not answer it by admitting them.

### Entry 3 -- a second premise check: where does each payload actually live

**One row's payload was never behind its refused address.** P G6 (per-post
analytics) was filed on `/analytics/post-summary/urn:li:activity:<id>/`. Read
offline off two raw captures in the main checkout's gitignored `_state/`
(shapes only; no id, name or text printed or copied):

    /analytics/creator/content/  2 post-summary links, each reading
                                 "<n> impressions <middle dot> <n> engagements"
                                 then "View analytics"
    his own profile (capture)    3 post-summary links, each reading
                                 "<n> impressions" then "View analytics"

Every one is `urn:li:activity:`, 19 digits, inside `<main>`. The first page is
ADMITTED and is already opened by `linkedin_creator_analytics` (M C40,
COVERED-PROVEN). So the headline per-post numbers are printed IN THE TEXT OF
THE LINK, on a page this server already reads. That became a reader (entry 5).

---

## 1. THE 24, ROW BY ROW

Three outcomes. ADMITTED (the boundary now opens the page) splits into
BUILT (a reader exists, fixture-tested) and NEEDS-CAPTURE (no capture of the
page exists on disk and no concrete structure record, so no reader is built
from imagination -- the live lane loads it once first). REVIEW means a
separate `REVIEW:` commit carries the change and it merges only on the
operator's look.

### 1.1 Admitted in the main commit -- five lines, six rows

For each: is loading it a pure read; is it drawn by LinkedIn or only named;
and what stands between the page and a reader.

**P A25 -- contact info panel -> `/in/me/overlay/contact-info/`. ADMITTED,
NEEDS-CAPTURE.**
* Drawn: yes. One `<a>` named "Contact info" on his own profile in each of the
  TRACKED fixtures `tests/fixtures/profile_topcard.html` and `_hydrated`
  (slug form, sanitised), one on the 2026-09-20 profile capture, and the
  suffix is `dom.PROFILE_EDITOR_HREFS`, measured on `/in/me/` 2026-08-30.
* Ruled, not argued: `PROFILE-EDITOR-ADDRESSES-ALLOWED` (2026-08-31) -- his own
  profile's editor surfaces are his to open. `dom.PROFILE_EDITOR_HREFS` classes
  this very href as one of those surfaces. The intro editor was admitted under
  the same ruling in the same `/in/me/` form.
* Pure read: it is a GET navigation to his own profile with an overlay open --
  what clicking the drawn link does. It is NOT the press the disclosing-press
  ruling refused (that control declares no `aria-*` shape; this is an href).
  Nothing is pressed; the edit pencil inside stays unpressed and A26-A29 stay
  writes. UNMEASURED: no load has been taken, so no counter was bracketed.
* Payload: email, phone, website, birthday. The standing rule
  (`scripts/_probe_contact_info_panel.py`) is that none of it crosses back;
  a reader returns closed-vocabulary presence and integers only.
* Why no reader: the overlay's content has never been captured.

**P G6 -- per-post analytics. BUILT, COVERED-UNFIRED (see entry 5).** Its
refused address is ALSO admitted, below, for the half the link text cannot
carry.

**P G6 / M C38 -- one post's analytics page ->
`/analytics/post-summary/urn:li:activity:[0-9]{1,20}/`. ADMITTED,
NEEDS-CAPTURE (for M C38's demographics half).**
* Drawn: yes -- twice on the creator-content capture (reproduced in the tracked
  `tests/fixtures/synthetic/creator_content_addresses.html`,
  `item_addresses.POST_SUMMARY_MARKER`) and three times on his profile.
* Narrow: the activity urn only (every drawn instance); `share`, `ugcPost`
  and a percent-encoded urn refused; the ten ASCII digits, at most 20 (the
  groups bound), because `\d` admits other scripts' digits -- measured, 5
  admitted against 2.
* Names nobody: a post id is not a member identifier, and every drawn
  instance sits beside one of HIS posts.
* Pure read: an analytics page of his own; the sibling
  `/analytics/creator/content/` was measured with the invitation badge before
  and after, twice, unmoved. That is a sibling's measurement, not this page's.
* Payload: viewer demographics are other people, aggregated -- a reader owes
  `census_shape` plus `census_redact_rare`, as the creator-content entry says.
* Why no reader for this page: never captured. M C38 stays GAP on exactly that.

**P L1 -- audience analytics -> `/analytics/creator/audience/`. ADMITTED,
NEEDS-CAPTURE.**
* Drawn: yes, the analytics nav's "Audience analytics" link on the admitted
  content page; the 2026-09-20 live capture (12.8) filed it as a candidate
  meeting the standard the role-play admission was granted on.
* `tests/test_analytics_creator_boundary.py` had pinned it refused with the
  words "a reason to CONSIDER an address, never a reason to have admitted it".
  This line is the consideration with its own argument; that file now pins it
  admitted by its own entry and keeps its query and sub-path refused.
* Payload: follower demographics -- the reader's obligation, not the address's.

**P L8 -- analytics and tools hub -> `/dashboard/`. ADDRESS FOUND, ADMITTED,
NEEDS-CAPTURE.** The row carried an INFERRED `/analytics/`. The tie to
`/dashboard/` is LinkedIn's own words: the tracked
`tests/fixtures/profile_topcard_hydrated.html` draws it as a link whose
accessible name is "Show all analytics", and the analytics nav on the content
page draws it as "Overview". `/analytics/` and `/creator-hub/` stay refused.
Anchored at the host, so `/company/<x>/admin/dashboard/` is unreachable
through it.

**M C48 -- all your articles -> `/in/me/recent-activity/articles/`. ADMITTED
ON A NAMED BASIS, NEEDS-CAPTURE.** The one of the five that NO capture draws:
the census row's own cell spells it; his profile draws only the parent
`/recent-activity/all/` ("Show all posts"). Admitted on the precedent
`/in/me/details/interests/` and `/jobs/alerts/` set -- a self-owned address
opened once to learn whether LinkedIn serves it, which widens nothing if it
redirects. `/recent-activity/all/`, `/comments/` and `/reactions/` (other
people's posts he acted on) stay refused.

**THE FIVE, MEASURED TOGETHER** with `scripts/blast_radius.newly_admitted`
(imported) over its own 67 addresses plus 75 family spellings: each newly
admits exactly its own target with and without the trailing slash, nothing
else, `newly_refused` empty. Controls: `/analytics/.*` admits 22 including a
traversal onto `/mypreferences/d/close-account`; `/in/me/.*` admits 16
including a traversal onto a third party's profile; `/dashboard/.*` admits 5;
`\d+` for the post id admits Arabic-Indic and fullwidth spellings; a needle no
line carries moves nothing. None of the five targets carries a forbidden
substring, so no exemption was touched.

**WHAT IS RE-DERIVED ON EVERY RUN AND WHAT IS NOT.** The per-line figure is
shipped: `tests/test_l1_self_scoped_admissions.py` takes each line out,
hands it back to the instrument over the shipped corpus plus that file's 48
family spellings, and asserts +2 and nothing else -- and asserts the
`/analytics/.*` family admits more, close-account among it. The exact control
counts above (22, 16, 5, 5-against-2) came from a disposable scratch driver
over the wider 142-address set (it also carried the REVIEW rows' spellings)
and are NOT re-derived by anything shipped; the cold verifier reproduced
their direction on its own 74-address corpus, not their numbers. They are
dated readings.

### 1.2 Left refused -- and why, per row

| row | address | why it stays refused |
|---|---|---|
| P L7 | `/creator-hub/` | NAMED only. No capture draws it; the content page carries `creator-hub` zero times; its own record (live capture 12.9) sequences it "a ruling, then an entry, then a load" |
| P M11 | `/resume-builder/` | INFERRED; nothing draws it (the premium hub draws resume/cv/builder 0 times); a builder is a composer-class surface that may autosave |
| M C39 | `/analytics/creator/content/?metricType=...` | The only `metricType` value drawn anywhere on disk is `IMPRESSIONS`, the default view already served bare. The comments token has never been drawn; the jobs-tracker precedent admits a query value only once read off an anchor |
| M C70 | `/search/results/content/` | D2 AND D1: a content search is a keyword search |
| N 104 | `/search/results/companies/` | D2 AND D1: "find a Page BY SEARCHING" needs a keyword, and no tool may pass one until D1 is ruled. A vertical admitted without it buys no row and still owes a name-free shaper in the same commit (`SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS`, condition 1) |
| N 161 | `/search/results/groups/` | as N 104 |
| N 179 | `/search/results/events/` | as N 104 |
| N 99, N 100 | `/school/<x>/people/` | a written member-roster cause (entry 2) |
| N 102 | `/company/<x>/people/` | a written member-roster cause (entry 2) |
| N 177 | `/groups/<id>/members/` | out of scope BY NAME (entry 2) |
| N 178 | `/in/<other>/` | the operator's 2026-09-04 ruling (entry 2) |
| N A5 | `/company/<x>/admin/` | INFERRED; the credit-balance sub-path is unrecorded; admin rights unmeasured (read triage 6.2); the admin root is Page ADMINISTRATION, which the company entry names as defended by nothing were a family pattern to reach it |

### 1.3 The four forbidden-substring rows

| row | substring | outcome |
|---|---|---|
| P L2b | `/follow` | **REVIEW: commit** (section 2) |
| N A3 | `/follow` | RECORDED, not implemented -- what it needs is below |
| P M12 | `/jobs/application` | RECORDED, not implemented |
| N 183 | `/mypreferences/d/categories/` | RECORDED, not implemented |

**N A3 needs, in order:** (1) a measurement that he administers any Page
(`ADMIN-RIGHTS-NOT-HELD` is a claim the read triage 6.2 found unsupported,
not refuted); (2) the SERVED spelling of the Page's following list -- the
corpus names `/company/<x>/admin/following/` and an alternative
`/admin/page-following/` that carries no forbidden substring, and which one
LinkedIn serves decides whether any carve-out is needed at all; (3) then an
anchored allowlist line, plus -- only if the served spelling carries `/follow`
-- a pattern exemption excusing `/follow` alone, the connections-list
mechanism.

**P M12 needs:** a SERVED spelling (the address is inferred from sibling M1),
and then the operator re-ruling the first forbidden entry, which was written
to stop APPLYING and whose reopener row M1 already names as his. Also open:
whether AI resume feedback renders on an admitted job posting at all -- a
live look at `/jobs/view/<id>/` could make this row need no carve-out.

**N 183 needs:** the NAME of the preference page that holds the setting (it
is unrecorded; the settings index draws navigation only), then -- under
`ONE-NAMED-SETTINGS-PAGE-AT-A-TIME` -- an exact-url `_FORBIDDEN_SUBSTRING_
EXEMPTIONS` key (the dict; the url is a constant) plus an anchored allowlist
line. The dark-mode precedent weighs against it: that page was chosen partly
because it needed NO forbidden substring narrowed, and the `categories/` pages
were deliberately not admitted. D5 may make the row EXCLUDED-RULED first.

### 1.4 Admitted only by a `REVIEW:` commit

| row | address | why a REVIEW commit, in one line |
|---|---|---|
| P L2b | `/mynetwork/network-manager/people-follow/followers/` | a read bought past the `/follow` write guard (pattern exemption excusing that one substring), and a written stance against reading the people-follow lists stands beside it -- section 2.1 |
| N 184 | `/events/<[0-9]{1,20}>/` | reverses the events root entry's stated scope, on the four conditions the groups id was admitted under -- section 2.2 |

Both are NEEDS-CAPTURE if taken: neither page has ever been captured, and no
reader ships with either.

(log continues below)

### Entry 4 -- the five lines landed, and what the tree said about them

Five one-line entries appended as one block at the end of
`_ALLOWED_URL_PATTERNS` (42 -> 47). The first run of the 82 test files that
touch the boundary (4933 passed) went red in exactly the places a widening
should turn red, and each was answered by moving the claim, never the
assertion:

    tests/test_readonly_boundary_invariant.py   the allowlist digest moved:
        1f9a6cef81e844af -> 7d442864f68f61fc. ATTRIBUTION: the tree minus
        exactly the five lines hashes to the old value; dropping the
        pre-existing /school/ line instead gives c097bad13e06f159. Seven of
        eight digests byte-identical; <functions> unmoved.
    tests/test_analytics_creator_boundary.py    it pinned the audience page
        refused and counted five analytics patterns. The audience line is
        now asserted to be carried by ITS OWN entry; its query and sub-path
        stand in as the refusals; the count is RAISED to seven, with the
        reason, as that test's own docstring prescribes.
    tests/test_the_census_prose_matches_the_boundary.py   the census said
        42 patterns and that post analytics refuses. The census cell now
        says 47 and names post analytics among the reachable surfaces.
    tests/test_read_addresses.py   six rows' verdicts moved. The side table
        now records them (below), and the checker is GREEN on 66 of 66.
    tests/test_stale_process_is_announced.py   six reds, NOT MINE: the
        loaded-build digest differed from disk because this lane edited
        package files WHILE that run was in flight. A process that loaded
        the old bytes is, correctly, stale.

### Entry 5 -- P G6 built: a reader over text the page already draws

`linkedin_server/post_summary_counts.py`. Locator reads only (`count`,
`get_attribute`, `inner_text`) -- no injected script, so `dom.py`'s evaluate
waiver budget (22 of 22) does not move. Selection is by structure: `<main>`
links carrying the post-summary marker, and only `urn:li:activity:` ones (the
shape the allowlist line admits). The FIRST LINE of each link must match one
anchored shape -- an integer and `impressions`, optionally a single separator
character, an integer and `engagements` -- or it is counted in `unparsed` and
dropped. One entry per distinct urn; the urn is used in-process to
de-duplicate and is never returned. The output is integers, booleans, `None`
and one sentence this module wrote.

Wired ADDITIVELY into `creator_analytics.read_content_analytics` as
`per_post`, so `linkedin_creator_analytics` (C40, COVERED-PROVEN) carries it
with no parameter change and one navigation, exactly as `item_addresses` was
added on 2026-09-20. Every key C40 was banked on is unchanged. The tool's
docstring states the field and its scope, and passes the write-verb
docstring check (zero affirmative claims).

**Census:** P G6 GAP -> COVERED-UNFIRED, scope stated in the cell
(impressions and engagements of the items the page features; the split and
the demographics live on the per-post page). Pinned in
`tests/test_a_covered_row_names_the_artifact_that_covers_it.py` with a chain
test for the passthrough (reader -> `per_post` key -> the tool's whole dict),
and a control that shows each join check failing on a mutated copy.

**The fixture is synthetic and reproduces the measured structure only** --
`tests/fixtures/synthetic/post_summary_counts.html`, five-digit ids, no name,
plus decoys (a link outside `<main>`, a permalink carrying "impressions"
text, a `share` urn, a duplicate, an unparsable line). Built by an implementer
child against a closed brief; reviewed before it entered the commit.

### Entry 6 -- the live harness, so NEEDS-CAPTURE is one command and not a brief

`scripts/_probe_l1_admitted_reads_live.py` (built by a second implementer
child, reviewed and then corrected by the lead -- entry 7). One closed, ordered
table of keys, each naming its census row, its address and a
structure-agnostic reader that returns integers, booleans and closed metric
words only: the anchor-class census `anchors.read_anchors` already ships, the
chart-label series `chart_labels` already ships, and the `per_post` field
above. Every address is a module constant or a template filled with a
validated 1-20 ASCII-digit id supplied on the command line -- never a value
read off a page. Each address is PRE-CHECKED with `readonly.is_read_url`, so
a key whose REVIEW commit has not merged is skipped at zero page loads. Raw
captures go to the gitignored `_state/l1-<key>.html` and nowhere else; that
file is what the next offline wave builds a fixture from.

It has never attached to a browser. It is PROVISIONAL-UNSMOKED, and register
section 58.3 says so.

### Entry 7 -- what reviewing the two slices caught, before anything froze

Both children delivered green files. Review still found four things, and
none of them was visible in a green run:

1. **THE HARNESS'S BRACKET COULD NOT SEE.** Its first draft read the
   invitation badge on a freshly opened tab -- no nav is drawn there, so both
   readings would have been UNREADABLE and the consumption line UNKNOWN on
   every run. The child read "the control twice" as the badge read itself.
   Fixed by the lead: the sibling probes' jobs-search control page is loaded
   before and after, the run is VOID and stops if it does not serve, and the
   badge is read on it.
2. **THE SAME DRAFT HELD A DECORATIVE CONTROL.**
   `tests/test_probe_controls_are_never_decorative.py` found `badge_before`
   printed and never branched on -- a finding the child's sweep list did not
   include. The fix above branches on it (an unreadable badge is announced
   before the first key, not discovered at the end).
3. **A CHILD REPORTED AN ESCAPE THAT WAS NOT ONE.** Its result file says the
   Arabic-Indic digits in its offline test were written as `\u0661`-style
   escapes, "kept strict-ASCII in source". A byte scan found the literal
   characters: the file-writing tool had decoded the escapes. The lead's own
   test file had the same defect, from the same cause, and both are now
   escaped and re-scanned. **A child's "I kept it ASCII" is a claim; a byte
   scan is the measurement.**
4. **A GUARD THE LEAD'S OWN FILE TRIPPED.**
   `tests/test_a_person_name_is_never_a_literal.py` holds `OTHER` among the
   constant names that must carry a declared invented name, and this lane's
   boundary test bound `OTHER = "someone-else"`. The guard's own remedy was
   taken -- the value declared in `INVENTED_NAMES` with its reason -- rather
   than renaming the constant out of the guard's sight. The REVIEW tests'
   `NEEDLE` constants were renamed `CARRIER` BEFORE they landed, because a
   regex fragment is not a name and declaring it as one would spend the
   guard's precision on nothing.

### Entry 8 -- the two REVIEW commits, the gate, and what it caught

Both REVIEW commits were written from drafts prepared while the main commit's
children were still running, each with its digest precomputed in memory by
the invariant's own `ast_digest` before anything was written to disk, and
each checked against its attribution afterwards (the tree minus the new line
hashes to the prior pin).

**THE GATE WENT RED ON TWO TESTS, AND BOTH WERE THIS LANE'S OWN WORDS, NOT
ITS CODE** (full suite, 8516 passed, 2 failed):

1. `tests/test_a_correction_is_findable_from_the_claim.py` -- three census
   cells now cite a document with correction vocabulary within two lines. Read
   line by line, all three are ADJACENCY: the matched word is `false` on the
   NEIGHBOURING row (G7's "IS NOW HALF FALSE", L3's "no published cell is
   false", the correction block's "FALSE BOTH WAYS"), and each citing cell
   rests its own claim on the cited document rather than withdrawing anything
   from it. Triaged in `NOT_A_CORRECTION` with the reason and what would make
   each entry wrong, as that file prescribes; the network-tail citation in the
   follower-list cell was rewritten as prose, so it needed no entry at all.
2. `tests/test_gap_rows_on_refused_addresses.py` -- its pinned count went
   4 -> 5 because the follower-list cell wrote `/follow` in backticks, and
   that checker reads every backticked path in a cell as an ADDRESS. A bare
   substring in prose made the row read as a GAP row sitting on a refused
   address. The cell now says it in words; the count is 4 again.

**A WRITTEN STANCE THE FOLLOWER-LIST COMMIT HAD NOT QUOTED.** Reading `N 38`'s
and `N 44`'s cells for the pin record turned up `readonly.py`'s Manage-Pages
entry: *"the right response to the luck running out is to leave the people
list unread, never to shorten the forbidden list"*. It was written about the
FOLLOWING list and it is the ground `N 38` is EXCLUDED-RULED on. The admission
does not shorten the forbidden list, but it does read a people list, so the
stance bears directly on the review. It is quoted in the REVIEW commit's own
comment, census cell and side-table note.

**ALL THREE REPAIRS WERE FOLDED INTO THE COMMITS THEY BELONG TO** with
`git commit --fixup` and a non-interactive `git rebase --autosquash` on this
unpushed branch: the triage entries into the main commit (whose own census
cells produce two of the pairs), the rest into the follower-list REVIEW
commit. So either REVIEW commit can be declined without leaving a triage
entry that names a pair that no longer exists -- the stale-entry test would
catch that -- and the review of the follower list cannot be taken without the
stance it must weigh. Comment-only in `readonly.py`: no digest moved.

### Entry 9 -- the one cold pass, and what it changed

A child with no part in the work verified the three commits read-only: ten
checks, **all PASS, no FAIL** -- attribution, ASCII over 3417 added lines,
identity, 77 adversarial urls of its own (0 wrongly admitted; all seven
targets admitted in both slash forms), the exemption excusing exactly
`/follow` and only there, the side table GREEN with all 24 rows agreeing
between the audit, the table and the census, the evidence claims against the
tracked fixtures, shapes-only counts off the raw captures (2 of 2 creator
post-summary links read "<n> impressions"; 3 numeric `/events/<id>/` anchors
beside 30 slug-form ones on the events root), the reader's closed alphabet,
and the harness's discipline. Its two flags, both acted on here:

1. **This document promised sections it had not yet written** -- true when
   checked; they are the sections below, and section 1.4 now places P L2b and
   N 184 where the verifier looked for them.
2. **The wildcard control counts were not reproducible from anything
   shipped** -- true; section 1.1 now says which figures a shipped test
   re-derives and which are dated readings from a disposable driver.

It also reported "a second active writer" in this worktree during its pass.
That writer was the lead, landing the fixups and the rebase recorded in entry
8. The verifier's SHA-anchored checks were immune to it by construction and
its working-tree checks were re-run after it, which is the discipline that
made the report usable.

One more correction came out of the final read, not the verifier: the live
harness said its twenty-digit id bound was "more than twice the longest id"
on a LinkedIn address. The ids on disk are nineteen digits. Corrected in the
harness.

---

## 2. THE TWO `REVIEW:` COMMITS

Neither merges without the operator's look. Both are boundary-only: no reader
ships with either, because neither page has ever been captured.

### 2.1 `de486b3` -- his own follower list past `/follow` (P L2b)

A WRITE GUARD MATCHING A READ ADDRESS, the connections-list shape of
2026-09-03. `/follow` exists to stop this server following somebody;
`/mynetwork/network-manager/people-follow/followers/` follows nobody -- it
lists the people who already follow him. The spec was written on 2026-09-05
(network-tail, section 2: "allowlist +2, exemptions +2, denylist UNCHANGED")
and handed over unapplied. This commit applies ONE of its two halves: the
following list is `N 38`'s -- EXCLUDED-RULED in the network slice -- and stays
refused, pinned.

    _ALLOWED_URL_PATTERNS                    +1  anchored, no query, no sub-path
    _FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS  +1  excuses exactly {"/follow"}
    _FORBIDDEN_URL_SUBSTRINGS                 0  33 before and after

**Does it weaken the send guard?** Measured, not argued, in
`tests/test_l1_follower_list_carve_out.py`: `/in/me/follow/`,
`/company/<x>/follow/`, `/company/<x>/unfollow/`, `/feed/follows/`, the
following list, this address with a query, with an `/unfollow` sub-path and
with a traversal onto a third party all still refuse, each on the substring
that names it; the exemption set is empty for every one of them; EITHER gate
alone refuses the address; the pair newly admits exactly its two spellings.

**The basis is NAMED.** No capture draws this address. LinkedIn's own bundle
names the sibling `people-follow/following` i18n namespace on every capture on
disk -- evidence for the FAMILY, not this leaf. The first load settles it.

**AND A WRITTEN STANCE POINTS THE OTHER WAY; THE REVIEW MUST WEIGH IT.**
`readonly.py`'s Manage-Pages entry says of this family: *"the right response
to the luck running out is to leave the people list unread, never to shorten
the forbidden list."* This admission shortens nothing -- `/follow` keeps its
full reach -- but it does READ a people list. The passage was written about the
FOLLOWING list, and the census files `N 38` EXCLUDED-RULED on it; whether it
reaches the list of people who follow HIM is the question this REVIEW puts to
the operator. It was found only when a later reading of `N 38`'s and `N 44`'s
cells turned it up, after the REVIEW commit was first written, and it was
folded into that commit's own comment, census cell and side-table note (not a
separate commit) so the review cannot be taken without it.

**If it merges, one sentence elsewhere goes stale:** `N 44` -- this row's
twin in the network slice, COVERED-CANNOT-DELIVER on the COUNT route -- says the
LIST route is refused by `/follow`. That cell is not this lane's; its owner
corrects it at merge.

### 2.2 `2292899` -- one event by its numeric id (N 184)

It REVERSES A STATED SCOPE: the `/events/` root entry listed `/events/<id>/`
among what it did not admit, and `tests/test_the_events_boundary_is_root_only.py`
enforced that. That list scoped the root's widening rather than ruling on the
address -- the groups root listed `/groups/<id>/` the same way, and that was
admitted fourteen days later on the lead's ruling. **This line is held to the
same four conditions:** a closed `[0-9]{1,20}` segment (`\d+` admits
Arabic-Indic digits and a 21-digit id: 5 against 3); the NUMERIC form only --
LinkedIn draws it itself on the captured events root, while the slug form (a
title run into the id) stays refused; the blast radius measured (exactly the
numeric-event spellings; an `/events/.*` family admits 12, the attendee roster
among them); and nothing fired. The tests it moved were MOVED, not deleted --
the numeric page left two must-stay-refused tables with its query spelling
standing in.

Pure read, ARGUED BY CAUSE and not measured: an event is an entity page, and
nothing in this repository says it records its viewers.

### 2.3 If only one of them is taken

The two commits touch the same lines of `readonly.py`, the digest pin and the
census count cell, so cherry-picking one alone conflicts mechanically. The
digests every combination needs, computed with the invariant's own
`ast_digest` (also written into its ledger entry):

    _ALLOWED_URL_PATTERNS     main only 7d442864f68f61fc   + followers c8c476ea47f0dfdd
                              + event    f0fcc25ebc21c2a3   + both      c37e98f84ee443f2
    _FORBIDDEN_SUBSTRING_     with the follower list 76d7b10899530d69,
      PATTERN_EXEMPTIONS      without it             419e64a3cd92ec7e
    census section-4 count    47 main, 48 with one, 49 with both

---

## 3. EXPECTED PIN MOVES -- NOT RE-PINNED, ON THE BRIEF

`scripts/census_completion.py --check` at the head of the lane (`2292899`), seven figures:

    adjudicated        430 -> 431   (+1)   P G6 banked
    b3_admitted         33 ->  40   (+7)   five main + follower list + event
    b3_refused          24 ->  16   (-8)   the seven admitted, and P G6 leaving
    delivered_broad     96 ->  97   (+1)   P G6 COVERED-UNFIRED
    gap                274 -> 273   (-1)
    gap_read            67 ->  66   (-1)
    unfired             21 ->  22   (+1)

Unmoved: `b3_no_address` 2, `b3_needs_session` 6, `b3_undetermined` 2,
`b3_blocked_on_nothing` 5. Without the two REVIEW commits: `b3_admitted` 38
and `b3_refused` 18, the rest as above.

Elsewhere: `scripts/count_census_states.py --expect J=56,P=55,M=77,N=86` now
measures P=54 (GAP 273). `scripts/pin_census_rows.py` reports no drift -- the
row population did not move, only a state.

**MERGE NOTES.** `_audit/INDEX.md`, `_audit/RULINGS.md` and
`_audit/_census/blocker-map.tsv` are regenerated at every commit here and will
conflict with any sibling; regenerate at the merge head. The side table, the
census cells, `tests/reader_leak_baseline.json` (one line) and
`tests/test_readonly_boundary_invariant.py` (the digest dict) are the other
shared files this lane touched.

---

## 4. GATES RUN, AND GATES NOT RUN

**RUN, all on this worktree, all offline:**

    scripts/impact_gate.py --against b0d3ab8    FULL SUITE -- the gate widened itself (168 of 220 files reachable, 76%): 8516 passed, 2 failed, 8 skipped, 1 xfailed, 2312s wall on a box running two other lanes' suites. Both failures were this lane's own census prose (entry 8); repaired, and the 470 tests covering what the repair touched re-run green. The full suite was NOT re-run after the repair.
    new tests, 184 in five files                 69 test_l1_self_scoped_admissions,
                                                 28 test_post_summary_counts,
                                                 50 test_l1_live_harness_offline,
                                                 17 test_l1_follower_list_carve_out,
                                                 20 test_l1_event_by_id_admission
                                                 -- all green, and inside the gate
    82 boundary-touching files, first run        4933 passed, 14 failed -- eight a
                                                 claim the widening moved, each
                                                 answered; six the stale-process
                                                 check reading edits made while
                                                 that run was in flight (entry 4)
    the same set after the answers               163 passed (the six touched files)
    fixture / identity / reader-leak guards      1843 passed
    probe sweeps over scripts/                   905 passed
    scripts/check_read_addresses.py              GREEN, 66 of 66, after each commit
    scripts/census_completion.py --check         RED BY DESIGN: 7 figures moved,
                                                 not re-pinned (section 3)
    scripts/_check_census_completion_can_fail.py RED BY DESIGN, for the same
                                                 reason: it refuses to demonstrate
                                                 anything while the unmutated copy
                                                 disagrees with its pins; green
                                                 again once they are re-pinned
    scripts/count_census_states.py --expect      P=54 against the pinned 55, the
                                                 same move
    scripts/pin_census_rows.py                   no drift
    the three generators, twice per commit       INDEX, RULINGS, blocker map at a
                                                 fixpoint before every commit
    the pre-commit identity gate                 0 hits on every commit
    one cold verification pass (a child with no
    part in the work)                            all 10 checks PASS, 0 FAIL; two flags, both acted on (entry 9)
    the commit carrying this record's final      1013 passed in 13 files: the three
    sections, before it landed                   derivation checks and the blocker
                                                 reason locator, the citation scan,
                                                 the live harness's offline suite,
                                                 the five probe sweeps, the gap-row
                                                 and person-name guards

**NOT RUN, and why:**

* **Anything live.** The brief forbids it and nothing here needed it: every
  verdict is the boundary called in-process, and every reader is tested
  against fixtures. The five NEEDS-CAPTURE pages and the two REVIEW pages
  have never been loaded; the live queue below is what loads them.
* **CI.** This lane does not push.
* **`scripts/triage_read_gap_rows.py`** -- the cleanup wave's, and red at HEAD
  for its own reasons (bucket-3 audit, section 7.4).

---

## 5. WHAT NEEDS THE OPERATOR

1. **The two `REVIEW:` commits** -- take both, one, or neither (section 2.3
   has what each combination costs to merge).
2. **D1 before D2.** Four rows of this slice (M C70, N 104, N 161, N 179) are
   searches BY KEYWORD, so widening the search verticals (D2) buys none of
   them while no keyword may be passed (D1). The order is D1 first.
3. **The member rosters (N 99, N 100, N 102, N 177) and another member's
   profile (N 178)** were not admitted because written refusals stand against
   them. Whether those count as WRITTEN for EXCLUDED-RULED is D3, and it moves
   five census states without moving any capability.
4. **N A3, P M12 and N 183** each need something only a live look or a
   ruling supplies -- section 1.3 lists exactly what, in order. One thing
   found on the way narrows P M12: the tracked `tests/fixtures/job_detail.html`
   draws a `JobDetails_ResumeReview` module on the ADMITTED job posting ("Get a
   resume review" / "Hire a resume writer"), and its only link is
   `/service-marketplace/create-project/` -- a request to HIRE a writer, a
   write the `/create` substring refuses. That is the services marketplace, not
   AI resume tips, so on the evidence on disk the posting does not carry this
   row's payload.
5. **M C39's comments metric** needs its `metricType` token read off a drawn
   control. The metric selector on `/analytics/creator/content/` is not an
   anchor on the captures on disk; if it is a disclosure, reading it is the
   press lane's question, not this one's.

---

## Live queue

One harness runs every line: `scripts/_probe_l1_admitted_reads_live.py`,
attached to the Chrome on 9224 (`LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224`),
one key per line with `--only <key>` or all of them in one run. Every run also
loads the jobs-search CONTROL page before and after (2 loads) and reads the
invitation badge on it; a control that does not serve voids the run. Nothing
on any line is pressed, typed or submitted. Raw captures land in the
gitignored `_state/l1-<key>.html` for the next offline build.

    row      reader or tool                         page address                                                   loads  press
    P G6     linkedin_creator_analytics -> per_post  /analytics/creator/content/                                      1     none   (key per_post; banks PROVEN if per_post.readable, CANNOT-DELIVER if the links carry no numbers)
    P A25    capture + anchor census + dialog count  /in/me/overlay/contact-info/                                     1     none   (key contact; the edit pencil is never touched; no contact value may be printed)
    P L1     capture + chart-label series + anchors  /analytics/creator/audience/                                     1     none   (key audience)
    P L8     capture + chart-label series + anchors  /dashboard/                                                      1     none   (key overview)
    M C48    capture + anchors + /pulse/ link count  /in/me/recent-activity/articles/                                 1     none   (key articles; NAMED address -- a redirect is the finding)
    M C38    capture + chart-label series + anchors  /analytics/post-summary/urn:li:activity:<id>/                    1     none   (key post_summary --post-id <digits of an urn:li:activity: key of HIS>; linkedin_my_activity_items returns item keys off /in/me/, and if those are not activity urns, item_addresses.read_item_addresses(include_identifiers=True) on /analytics/creator/content/ lists the post_summary urns, which are -- +1 load if fetched for this)
    P L2b    capture + member-anchor COUNT only      /mynetwork/network-manager/people-follow/followers/              1     none   (key followers; ONLY after REVIEW de486b3 merges -- until then the harness skips it at zero loads)
    N 184    capture + anchor census                 /events/<id>/                                                    1     none   (key event --event-id <digits>; ONLY after REVIEW 2292899 merges; an id the operator shares is the row's own premise)

A full run with both REVIEW commits merged and both ids supplied: 8 row loads
plus 2 control loads, 10 in all; 8 without the REVIEW rows.
