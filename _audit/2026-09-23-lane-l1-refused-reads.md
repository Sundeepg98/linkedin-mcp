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

(sections 2 onward -- the REVIEW commits, the gates, the pin moves and the
live queue -- follow as they land)
