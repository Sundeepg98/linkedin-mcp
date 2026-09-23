claude-opus-5-5[1m]

# Bucket 3, measured: 67 rows, 33 on an admitted page, and 5 a reader could close today

**CORRECTS:** `_audit/2026-09-21-the-read-triage.md` -- four address verdicts: P F1 and P H11 are pages on the admitted profile, not ADDRESS/ABSENT, and P L4 and N 61 wait on a live read, not on a refused address anybody has seen served.

**CORRECTED BY:** `_audit/2026-09-23-readers-four-rows.md` -- of the five "blocked on nothing", `M C85` is gated RULING (no sanctioned source for a poll post's address) and `P O3`, `N 134` and `M C72` are gated PRESS, measured live the same day; only `M M49` remains, so the figure is 1 of 67, not 5.

Wave `bucket3-addresses`, 2026-09-23, from master `79c5f8e`. **READ-ONLY AND
OFFLINE THROUGHOUT.** No browser was started or attached to, no page was
loaded, no session was touched, and `writes_enabled` was never read or moved.
Every verdict below is the shipped `readonly.is_read_url` called in-process on
a placeholder address; every refusal kind is read off the exception the shipped
`readonly.assert_read_url` raises.

---

## 0. THE DENOMINATOR -- DERIVED, AND IT AGREES

**N = 67, no discrepancy.** Taken by importing `census_completion.walk()` --
the walk that prints the 67 -- and keeping folded state GAP with direction R or
R+W: **R 64 + R+W 3**. By slice: profile 18 (17 R, and P M11 at R+W),
messaging 12 (10 R, and M M28 and M C85 at R+W), network 37. The jobs slice
contributes none because its tables carry no per-row direction column, which
`census_completion.py` already reports as its own unclassified bucket.

It is the 68 of the 2026-09-21 reachability wave less N 53, which that wave
banked, so every prior per-row reading of this population was reusable.

---

## 1. THE ANSWER, FIRST

    class           rows   what the shipped boundary says about the row's page
    ADMITTED          33   it may be opened today
    REFUSED           24   it may not: allowlist silence 20, a forbidden substring 4
    NO-ADDRESS         2   the capability has no page of its own
    NEEDS-SESSION      6   the page exists and its address is unknown offline
    UNDETERMINED       2   neither the corpus nor a live look has found an address
                    ----
                      67

    of the 33 ADMITTED, the first thing past the boundary:
    READER             2   a reader over the admitted page is the whole cost
    PRESS-PERMITTED    3   the reader must press, and the shipped press gate permits it
    MEASURE            3   a live look must come first: render or structure unknown
    BUILT-UNFIRED      4   the reader ships and has never fired
    PRESS             12   the payload is behind a press the shipped gate refuses
    RULING             9   a named decision nobody has made comes first

**THE REAL SIZE OF "BLOCKED ON NOTHING AT ALL" IS 5 OF 67.** Five rows sit on a
page the boundary admits AND have nothing between that page and a reader but
the reader itself: M M49 and M C85 (READER), P O3, N 134 and M C72
(PRESS-PERMITTED). Seven more need only a session first -- a live look (P F1,
P H11, P K8) or a fire of code that already ships (N 80, N 81, N 88, N 89).
The other 55 are gated: 21 behind a refused press or an unmade decision, 24 at
the boundary itself, and 10 with no address to put through it.

**The upper bound was more than thirteen times the measured number.** Bucket 3 was, in its own
words, "the set a reader could close IN PRINCIPLE". Measured at the boundary and
at the first gate past it, a reader wave sized on 67 would find 5.

---

## 2. THE FIVE CLASSES, DEFINED

The ADDRESS of a row is **the page whose load would draw the row's READ
payload**. For a row with a read half and a write half (P M11, M M28, M C85) it
is the read half's page. A payload drawn behind a control with no url of its
own has its HOST page as its address, and the press becomes the row's gate
(section 3), never its address.

* **ADMITTED** -- an address was found and `readonly.is_read_url` returns true
  for it, so the boundary does not stand between a reader and the page. **It
  says nothing about whether the page draws what the row wants** -- ALLOWED IS
  NOT SERVED -- and nothing about the gates past the boundary, which section 3
  names.
* **REFUSED** -- an address was found and the boundary refuses it. The kind of
  refusal is recorded per row, read off the shipped gate's own sentence, and is
  one of three (quoted verbatim at the end of section 5): **allowlist silence**
  (`NO-PATTERN`), **a forbidden substring with no pattern behind it**
  (`FORBIDDEN[s]+NO-PATTERN` -- the row needs a pattern AND an exemption), or
  **a forbidden substring on an address a pattern would admit**
  (`FORBIDDEN[s]+PATTERN-WOULD-ADMIT` -- none of the 67).
* **NO-ADDRESS** -- the capability is not drawn on any page of its own: it is a
  cost, rule or consequence that derives from another act. The row says what it
  derives from.
* **NEEDS-SESSION** -- the capability does have a page, but no committed source
  records its address, and a live page would reveal it. The row says exactly
  what is unknown.
* **UNDETERMINED** -- no committed source records an address AND the one live
  look already taken found no way to it, so a session alone is not known to
  settle it. The row says why.

**THE BASIS OF EACH ADDRESS IS RECORDED BESIDE IT**, because a verdict is only
as good as the address it was taken on: **MEASURED** (seen served, or drawn on
a live page or a capture), **NAMED** (written in code, a test, the census or an
audit, never observed served) or **INFERRED** (constructed as representative by
a prior wave or this one). Of the 57 addresses, 28 are MEASURED, 22 NAMED and
7 INFERRED; section 6 lists the seven.

---

## 3. THE GATE PAST AN ADMITTED BOUNDARY

Recorded for the 33 ADMITTED rows only. It is the FIRST thing a reader wave
would hit past the boundary, not every thing -- the convention of the read
triage. Every gate other than READER names its committed source in the row.

* **READER** -- nothing named but writing a reader over the admitted page.
* **PRESS-PERMITTED** -- the payload is behind a disclosing press, and the three
  conditions that settle offline all pass through the shipped `press` gate:
  `check_address` admitted, `check_shape` on a sanctioned shape, and
  `check_basis` finding a declared sensitivity basis. Measured in-process for
  `/feed/` (basis `sensitive`) and `/analytics/profile-views/` (basis
  `structural`).
* **MEASURE** -- a live look must come before a reader can be designed: the
  payload's render or structure on the admitted page is unestablished and a
  prior attempt said so.
* **BUILT-UNFIRED** -- the reading ships in the package and has never met the
  live page. One browser slot closes or refutes it.
* **PRESS** -- the payload needs a press the shipped gate refuses today:
  `no_sensitivity_basis` on `/in/me/` and on `/search/results/people/`
  (measured in-process), a shape the ruling cannot reach, a submit, or a
  second press that is not a disclosure.
* **RULING** -- a named, unmade decision comes first: D1 (may a search keyword
  be passed), D4 (may the package create its own browser context), D6 (do two
  addresses discharge a row named for a control), the label reading N 82 would
  need, and the write that would make N 174 observable at all.

**"BLOCKED ON NOTHING" IS ADMITTED WITH A GATE OF READER OR PRESS-PERMITTED**:
a reader could be written today with no ruling, no boundary edit and no press
the shipped gate refuses. MEASURE and BUILT-UNFIRED rows are blocked on a
session and nothing else; PRESS and RULING rows are blocked on a decision.

---

## 4. METHOD

**Reused, not redone.** The 2026-09-19 read-rows wave measured 39 rows by hand
by calling the shipped gate on a candidate address per row; the 2026-09-21
triage priced the 59 profile and network rows; a 2026-09-21 recheck re-drove 30
addresses. Their addresses were taken as the first candidates, and each was
driven again here rather than quoted.

**One address per row, from the strongest committed source**, in this order: a
shipped code symbol; a committed test fixture or probe literal tagged with the
row; the row's own census cell; a prior audit. When sources name different
pages, the one that draws the READ payload wins and the others are driven too,
in the table's `also_driven` column, so a disputed row carries every candidate
and every verdict. When the candidates disagree and nothing committed says
which draws the payload, the row is NEEDS-SESSION, never a guess.

**Placeholders, and why they do not move a verdict.** Every variable segment is
synthetic -- `placeholder-org`, `placeholder-school`, `placeholder-member`,
`placeholder-newsletter`, `someone-else`, `12345`, `2-ABCdef123`. The allowlist
patterns accept a SHAPE, never a value, so the verdict cannot depend on which
value stands there; and five-digit ids sit under the identity guard's six-digit
urn floor, the reshape `scripts/_probe_route_vs_surface.py` already made.

**The boundary is imported, never re-read.** 42 allowed patterns, 33 forbidden
substrings, two exact and two pattern exemptions -- counted by importing
`linkedin_server.readonly`, since a grep of its source is how the read-rows wave
first counted 24 and 11.

**The press gate, likewise.** The PRESS and PRESS-PERMITTED gates rest on
`press.check_address`, `press.check_shape` and `press.check_basis`, called
in-process for `/feed/`, a feed permalink, `/in/me/`,
`/analytics/profile-views/` and `/search/results/people/`.

**Drift control, three rows of the read-rows wave, re-driven as that document
spelled them:** M C83 (the per-newsletter analytics spelling), N 99 (the school
root and its alumni tab), N 61 (the following page, the hashtag root, and the
interests detail page). **6 of 6 addresses agree at HEAD; nothing moved.**

**A completeness cross-check, one-time and disposable.** Every backticked
address the 67 rows' own census cells name was collected with the shipped
`check_gap_rows_on_refused_addresses.ADDR` pattern and compared with what the
table drives. Nothing it found would move a class: the misses are family
prefixes (`/search/results/`, `/school/`), bare substrings (`/follow`,
`/invite`, `/edit/`), and context addresses a cell names for another purpose
(the counter candidates in M C72's cell, the jobs search in N 79's).

**Delegation: one closed-form slice, and it was a check, not a judgement.**
Classifying a row needed the judgement this document records, so none of that
was handed down. Verifying it was: an implementer child, read-only and with no
part in writing the table, re-resolved every row's source and quoted the
supporting line for every claim in its note. Its report was read line by line
before anything entered the table; section 6 says what it changed.

---

## 5. THE 67, BY CLASS

Generated from `_audit/_census/read-addresses.tsv` rather than typed, so the
two cannot disagree. Sources are written as plain paths; the table carries the
same text.

### ADMITTED -- 33

| row | address | basis | gate | source | why |
|---|---|---|---|---|---|
| M C85 | `/feed/update/urn:li:activity:12345/` | NAMED | **READER** | _audit/_census/messaging-and-content.md row C85 | The READ half is poll results, COUNTS on the post, under the feed-content ruling C43 and C74 rest on (counts and relations only). The permalink is admitted; no reader exists. UNVERIFIED and not recorded anywhere: whether per-option results render before voting (a vote is an irreversible write). |
| M M49 | `/messaging/thread/2-ABCdef123/` | MEASURED | **READER** | _audit/_census/messaging-and-content.md row M49 | The indicators live in a thread, and /messaging/ is measured to redirect into /messaging/thread/<id> (live capture 12.2). The row's own cell: blocked on a reader plus the cost of opening a thread, not on an address; linkedin_open_messaging already carries that cost for the thread LinkedIn lands on, and documents it (a read receipt may be seen). A reader confined to that landed thread adds no cost; one that CHOOSES a thread by id would be a new decision. Thread id is the synthetic from scripts/_probe_route_vs_surface.py. |
| P O3 | `/analytics/profile-views/` | MEASURED | **PRESS-PERMITTED** | _audit/_census/profile.md row O3 | Loaded today by linkedin_who_viewed_me. Press conditions 1-3 settle offline (admitted; [aria-expanded] sanctioned; the structural basis press.SENSITIVITY_BASES declares for this surface) and the witness fired 2026-09-21: the panel opens. Blocked on ONE unbuilt artifact, a name-free content shaper, with dom.py's readonly-ok waiver budget at 22 of 22. |
| M C72 | `/feed/` | MEASURED | **PRESS-PERMITTED** | _audit/_census/messaging-and-content.md row C72 | The share triggers render on /feed/ (measured live 2026-09-19); the off-platform items are built on demand behind an [aria-haspopup] trigger. Offline, press conditions 1-3 settle: admitted, shape sanctioned, and press.SENSITIVITY_BASES declares /feed/ 'sensitive' on off_state. What is missing is a caller wiring read_reaction_surface as the counter, then a fire. |
| N 134 | `/analytics/profile-views/` | MEASURED | **PRESS-PERMITTED** | _audit/_census/network.md row 134 | Same surface and artifact as P O3: conditions 1-3 settle offline, the witness fired (the panel opens), and the one unbuilt thing is a name-free shaper for a panel made of other people. |
| P F1 | `/in/me/` | NAMED | **MEASURE** | scripts/_probe_profile_sections_live.py::PROFILE_URL | The detail address (also driven) is refused, so the route the repository pursues is the recommendations SECTION on the admitted profile, whose heading shape.PROFILE_SECTION_HEADINGS already lists among the profile's own sections. Its structure is UNMEASURED: four instruments failed their controls finding it (2026-09-19) and scroll is not sanctioned. recommendations.py (the name-free shaper) ships unwired. Corrects the read triage's ADDRESS/ABSENT, which priced only the detail spelling. **Also driven:** `/in/me/details/recommendations/` refused. |
| P H11 | `/in/me/` | NAMED | **MEASURE** | _audit/2026-09-05-network-tail.md section 3 | The row is the section AS RENDERED ON THE PROFILE, so its page is /in/me/ (admitted); the two other spellings (also driven) are refused and serve the ten writes, not this read. Render gate unmeasured: nobody knows whether the section renders on a passive load. The read triage says the phrase sits in shape._TOPCARD_CHROME; measured, that set holds the 'add services' PROMPT, not the section, so no parser in the package reads the section either way. Corrects the read triage's ADDRESS/ABSENT, which priced the details spelling. **Also driven:** `/in/me/details/services/` refused, `/services/page/` refused. |
| P K8 | `/in/me/` | MEASURED | **MEASURE** | _audit/2026-09-05-profile-rest.md | A reading exists at allowlist +0: top voice 0 in text AND 0 in accessible names, on an instrument shown able to disagree with itself. What remains is one live re-read to bank MEASURED-ABSENT (read triage 3.2), not a reader. |
| N 80 | `/search/results/people/` | MEASURED | **BUILT-UNFIRED** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Fired live 2026-09-21 (route half: 18 person_result anchors, landed where sent). The term 'people' read 0; the label-SHAPE reading that would settle it (dom.FILTER_PANEL_JS windowMatch / search_results.read_filters 'decorated') is BUILT and NOT FIRED. |
| N 81 | `/search/results/people/` | MEASURED | **BUILT-UNFIRED** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Single-word term read 0, which cannot separate absent from decorated; the All-filters press is refused terminally. The label-SHAPE reading is BUILT and NOT FIRED. |
| N 88 | `/search/results/people/` | MEASURED | **BUILT-UNFIRED** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Single-word term read 0, which cannot separate absent from decorated; the label-SHAPE reading is BUILT and NOT FIRED (row cell, 2026-09-21). |
| N 89 | `/search/results/people/` | MEASURED | **BUILT-UNFIRED** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Single-word term read 0, which cannot separate absent from decorated; the label-SHAPE reading is BUILT and NOT FIRED (row cell, 2026-09-21). |
| P D28 | `/in/me/` | MEASURED | **PRESS** | _audit/2026-09-03-linkedin-gap-blockers.md Amendment C2 | The phrase 'profile language' was measured rendering on /in/me/ (read half +0). Binding gate per the read triage: PRESS -- the reading found distinct_langs 1, and no pressable language control is proven; press.check_basis refuses /in/me/ with no_sensitivity_basis. |
| P J4 | `/in/me/` | MEASURED | **PRESS** | scripts/_probe_route_vs_surface.py::CANDIDATES (P J4) | The hiring state sits behind the Open-to menu. Measured twice, fourteen days apart: hiring NAMED BUT INERT, the opener AMBIGUOUS, the menu holding three options and no state (read triage). press.check_basis refuses /in/me/ with no_sensitivity_basis. |
| M C29 | `/feed/update/urn:li:activity:12345/` | INFERRED | **PRESS** | scripts/_probe_route_vs_surface.py::CANDIDATES (one post, by permalink) | INFERRED BY THIS WAVE: the probe tags this permalink for M C43, M C34 and N 148, never for this row; it is used here because comments render under the post they belong to. The class cannot move on it: both pages a post's comments render on, the permalink and the feed (also driven), are admitted, and press.check_basis finds the /feed/ basis for both. But sorting is SELECTING an option, a second press that is not a disclosure, and the control was never named or measured, so no ruled press reaches it. **Also driven:** `/feed/` admitted. |
| N 76 | `/in/me/` | MEASURED | **PRESS** | _audit/_census/network.md row 76 | One [aria-haspopup] and zero menus on /in/me/, so the follow link is behind a built-on-demand menu. press.check_basis refuses /in/me/ with no_sensitivity_basis before anything is read; the row's cell re-files it as a RULING REQUEST for a SENSITIVITY_BASES entry, and states why the argument would be circular. |
| N 84 | `/search/results/people/` | MEASURED | **PRESS** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Multi-word term 'current company' read 0 on 83 drawn controls, so the control sits in the All-filters panel. That press is refused TERMINALLY (condition 2: neither aria-expanded nor aria-haspopup; condition 3: no sensitivity basis). The press-free route (response bodies) needs a reader this package lacks, with an admission heavier than the press. |
| N 85 | `/search/results/people/` | MEASURED | **PRESS** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Multi-word term 'connections of' read 0 on 83 drawn controls, so the control sits in the All-filters panel. That press is refused TERMINALLY (condition 2: neither aria-expanded nor aria-haspopup; condition 3: no sensitivity basis). The press-free route (response bodies) needs a reader this package lacks, with an admission heavier than the press. |
| N 86 | `/search/results/people/` | MEASURED | **PRESS** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Multi-word term 'followers of' read 0 on 83 drawn controls, so the control sits in the All-filters panel. That press is refused TERMINALLY (condition 2: neither aria-expanded nor aria-haspopup; condition 3: no sensitivity basis). The press-free route (response bodies) needs a reader this package lacks, with an admission heavier than the press. |
| N 87 | `/search/results/people/` | MEASURED | **PRESS** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Multi-word term 'past company' read 0 on 83 drawn controls, so the control sits in the All-filters panel. That press is refused TERMINALLY (condition 2: neither aria-expanded nor aria-haspopup; condition 3: no sensitivity basis). The press-free route (response bodies) needs a reader this package lacks, with an admission heavier than the press. |
| N 90 | `/search/results/people/` | MEASURED | **PRESS** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Multi-word term 'profile language' read 0 on 83 drawn controls, so the control sits in the All-filters panel. That press is refused TERMINALLY (condition 2: neither aria-expanded nor aria-haspopup; condition 3: no sensitivity basis). The press-free route (response bodies) needs a reader this package lacks, with an admission heavier than the press. |
| N 91 | `/search/results/people/` | MEASURED | **PRESS** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Multi-word term 'open to volunteering' read 0 on 83 drawn controls, so the control sits in the All-filters panel. That press is refused TERMINALLY (condition 2: neither aria-expanded nor aria-haspopup; condition 3: no sensitivity basis). The press-free route (response bodies) needs a reader this package lacks, with an admission heavier than the press. |
| N 92 | `/search/results/people/` | MEASURED | **PRESS** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Multi-word term 'service categories' read 0 on 83 drawn controls, so the control sits in the All-filters panel. That press is refused TERMINALLY (condition 2: neither aria-expanded nor aria-haspopup; condition 3: no sensitivity basis). The press-free route (response bodies) needs a reader this package lacks, with an admission heavier than the press. |
| N 133 | `/analytics/profile-views/` | MEASURED | **PRESS** | _audit/_census/network.md row 133 | The filter controls were measured rendered and unpressed. Applying a filter SUBMITS, and the disclosing-press ruling refuses submission by name. |
| P C8 | `/in/me/` | NAMED | **RULING** | _audit/2026-09-21-the-read-triage.md D4 | D4: may this package create its own browser context. accept_downloads is a context-creation option and ATTACH mode never creates one; pinned by tests/test_profile_pdf_download_is_blocked_on_transport.py. The address carries no boundary cost. |
| N 79 | `/search/results/people/?keywords=placeholder` | NAMED | **RULING** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | D1: may a search keyword be passed. The pattern admits a query SHAPE; the shipped tool takes no parameter by design, and 8 of 11 ordinary keywords trip a forbidden substring. |
| N 82 | `/search/results/people/` | MEASURED | **RULING** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | Matched live (2, stably) and refused: an unscoped selector plus a textContent fallback, and nothing available tells a people filter from a jobs badge without reading the label, which this surface forbids. |
| N 93 | `/search/results/people/` | MEASURED | **RULING** | linkedin_server/search_results.py::PEOPLE_SEARCH_URL | The label-SHAPE reading is built and unfired and would confirm the predicted decorated label without closing the row: it also waits on D1, the parameter ruling row 79 names. |
| N 94 | `/search/results/people/?geoUrn=%5B%22100%22%2C%22200%22%5D` | INFERRED | **RULING** | _audit/_census/network.md row 94 | The cell measured the address True with an unrecorded multi-value query; a representative multi-value spelling is constructed and driven. Nothing can compose a query (every reader takes a page only): D1, and a second question about the query's shape behind it. |
| N 132 | `/analytics/search-appearances/` | MEASURED | **RULING** | _audit/_census/network.md row 132 | Both sides of the switch are admitted and served by shipped tools; what is unbuilt is only the CONTROL. D6: do two addresses discharge a row named for a control. **Also driven:** `/analytics/profile-views/` admitted. |
| N 172 | `/search/results/people/?connectionOf=placeholder-member` | NAMED | **RULING** | tests/test_the_search_shaper_emits_no_name.py::NAME_SHAPED_ROUTES | A member's connection list is the people search with a connectionOf query, and that shape has been ADMITTED since 2026-09-20 (the pattern takes any query). The prior audits priced this row on the member's profile (also driven, refused) before the search admission landed. Still not buildable: the value is another member's identifier -- D1's needle -- and the row is filed under D3's other-people cause. **Also driven:** `/in/placeholder-member/` refused. |
| N 174 | `/groups/` | MEASURED | **RULING** | linkedin_server/readonly.py (groups root entry: WHAT THIS SERVES ... N 174) | Read live: the root draws two sections, neither a pending-requests list, and an absent-when-empty section reads the same as a missing one. Observable only once a pending request exists, and creating one is a WRITE at a real group (filed RULING by the read triage). |
| N 194 | `/search/results/people/?keywords=%23hiring` | NAMED | **RULING** | _audit/_census/network.md row 194 | The needle is a hashtag typed into a search: D1. The feed hashtag route (also driven) stays refused. **Also driven:** `/feed/hashtag/hiring/` refused. |

### REFUSED -- 24

| row | address | basis | refusal | source | note |
|---|---|---|---|---|---|
| P A25 | `/in/me/overlay/contact-info/` | MEASURED | `NO-PATTERN` | linkedin_server/dom.py::PROFILE_EDITOR_HREFS | The panel's own address. The anchor suffix /overlay/contact-info/ was measured on /in/me/ 2026-08-30; the drawn href carries his own slug, which is never written here, so the self-alias spelling is driven and no pattern admits either. The admitted intro editor (also driven) draws only the Edit-contact-info control, and the census cell records that press as refused (off press.SANCTIONED_SHAPES, and the ruling refuses opening editors). **Also driven:** `/in/me/edit/intro/` admitted. |
| P G6 | `/analytics/post-summary/urn:li:activity:12345/` | MEASURED | `NO-PATTERN` | _audit/_census/messaging-and-content.md row C38 | Per-post analytics. Two anchors of the shape /analytics/post-summary/urn:li:<type>:<digits>/ were counted on a capture of the admitted /analytics/creator/content/ (2026-09-20). No pattern admits the shape. Five-digit id so no identity shape is written. |
| P L1 | `/analytics/creator/audience/` | MEASURED | `NO-PATTERN` | _audit/2026-09-20-the-live-capture.md 12.8 | Drawn as an anchor on the admitted /analytics/creator/content/ (2026-09-20) and filed as an unadmitted candidate; pinned refused by a committed test. |
| P L2b | `/mynetwork/network-manager/people-follow/followers/` | NAMED | `FORBIDDEN[/follow]+NO-PATTERN` | scripts/_probe_network_tail_boundary.py (the follow-list candidate tagged N 44 / P L2b) | A read refused by a write guard. _audit/2026-09-05-network-tail.md section 2 wrote the repair as a spec (allowlist +2, pattern exemptions +2, denylist unchanged) and did not apply it; nobody has since. |
| P L7 | `/creator-hub/` | NAMED | `NO-PATTERN` | _audit/2026-09-20-the-live-capture.md 12.9 | The creator hub's address. The classifier's other candidate (also driven, admitted) was adjudicated NOT the hub: that page's source carries creator-hub 0 times and draws no creator/hub/mode/tools words. **Also driven:** `/analytics/creator/content/` admitted. |
| P L8 | `/analytics/` | INFERRED | `NO-PATTERN` | _audit/_census/_wave-address-recheck.tsv (P-L8 analytics tree root) | The hub's address is DISPUTED in the corpus. The class does not depend on the dispute: the tree root, the blocker's /creator-hub/ and /dashboard/ (one href of that path is drawn on the hydrated profile fixture; its tie to this row is this wave's inference, UNVERIFIED) all refuse. **Also driven:** `/creator-hub/` refused, `/dashboard/` refused. |
| P M11 | `/resume-builder/` | INFERRED | `NO-PATTERN` | scripts/classify_surface_blockers.py::SURFACE_ADDRESSES (the resume-tools entry) | The only address the corpus names, and its own module calls the table a CLAIM, not a derivation. No pattern among the 42 names any resume path, and the capture of the admitted /premium/my-premium/ draws resume/cv/builder 0 times (live capture 12.10). Entitlement unverified. |
| P M12 | `/jobs/application-settings/` | INFERRED | `FORBIDDEN[/jobs/application]+NO-PATTERN` | _audit/2026-09-21-the-read-triage.md section 5 | Inferred from the sibling row M1 (the recheck tsv marks it SYNTHETIC-REPRESENTATIVE). Refused by the FIRST forbidden substring; reopening it is the operator's (row M1). Whether AI resume feedback renders on an admitted job posting is unmeasured. |
| M C38 | `/analytics/post-summary/urn:li:activity:12345/` | MEASURED | `NO-PATTERN` | _audit/_census/messaging-and-content.md row C38 | The row asks PER-POST analytics and viewer demographics. The account-level page (also driven) is admitted and read by linkedin_creator_analytics but serves a per-day account series for one metric; the per-post address is drawn on it and refused. **Also driven:** `/analytics/creator/content/` admitted. |
| M C39 | `/analytics/creator/content/?metricType=x` | NAMED | `NO-PATTERN` | tests/test_analytics_creator_boundary.py (MUST-REFUSE) | Tied to this row by the 2026-09-19 read-rows wave (5.1): the comments metric needs ?metricType=. LinkedIn selects a metric that way (chart_labels.py), and the admitted pattern has no query group -- readonly.py states why -- so the comments metric is unreachable at any value; the fixture's value is driven. Same tool and surface as C38, fired live. |
| M C48 | `/in/me/recent-activity/articles/` | NAMED | `NO-PATTERN` | _audit/_census/messaging-and-content.md row C48 | Both spellings the row's own cell measured refuse; the single allowlist +1 its blocker is billed is owed at least twice. **Also driven:** `/pulse/` refused. |
| M C70 | `/search/results/content/` | NAMED | `NO-PATTERN` | _audit/_census/messaging-and-content.md row C70 | Both spellings of this capability's address refuse (row cell, re-measured 2026-09-21). D2 (widen the search admission past people) plus a per-group address; doubly gated. **Also driven:** `/search/results/groups/` refused. |
| N 99 | `/school/placeholder-school/people/` | NAMED | `NO-PATTERN` | scripts/_probe_route_vs_surface.py::CANDIDATES (a school's alumni tab) | The root (also driven) is admitted; the alumni tab is refused by the school entry's anchor, in its own words, carrying zero forbidden substrings. D3: does a reasoned allowlist refusal count as written. **Also driven:** `/school/placeholder-school/` admitted. |
| N 100 | `/school/placeholder-school/people/` | NAMED | `NO-PATTERN` | scripts/_probe_route_vs_surface.py::CANDIDATES (a school's alumni tab) | Same tab and cause as row 99. Its second half, contacting alumni, is a write the direction cell does not show. |
| N 102 | `/company/placeholder-org/people/` | NAMED | `NO-PATTERN` | linkedin_server/readonly.py (company entry: /company/<x>/people/) | A MEMBER ROSTER, refused 'by this anchor and by nothing else' (measured: zero forbidden substrings); the root is admitted. D3's cause. **Also driven:** `/company/placeholder-org/` admitted. |
| N 104 | `/search/results/companies/` | NAMED | `NO-PATTERN` | _audit/_census/network.md row 104 | D2: widen the search admission past the people vertical. The non-search half (company_page_url off a posting) already ships. |
| N 161 | `/search/results/groups/` | NAMED | `NO-PATTERN` | _audit/_census/network.md row 161 | The groups entry's comment declines to inherit this address; D2. |
| N 177 | `/groups/12345/members/` | NAMED | `NO-PATTERN` | _audit/2026-09-19-the-read-rows.md section 5.2 | The read-rows wave tied this row to a group's member directory. linkedin_server/readonly.py refuses that roster by name -- as census row N 165, the row put out of scope for it -- and its groups root entry states the cause: a group's MEMBER DIRECTORY is other people and is 'not admitted here or anywhere'. D3. |
| N 178 | `/in/someone-else/` | NAMED | `NO-PATTERN` | _audit/2026-09-19-the-read-rows.md section 5.2 | The read-rows wave tied this row to another member's profile. A member's groups would sit on THEIR profile -- the interests tab, also driven, is this wave's inference of where, taken from a third-party interests literal scripts/_probe_newsletter_routes.py uses as a refusal control. Loading a third party's profile leaves them a durable record, the boundary's sharpest refusal. D3. **Also driven:** `/in/someone-else/details/interests/` refused. |
| N 179 | `/search/results/events/` | NAMED | `NO-PATTERN` | _audit/_census/network.md row 179 | D2, plus the D1 parameter ruling (a keyword nothing on this surface accepts). |
| N 183 | `/mypreferences/d/categories/placeholder/` | INFERRED | `FORBIDDEN[/mypreferences/d/categories/]+NO-PATTERN` | linkedin_server/readonly.py (events entry: N 183 is a SETTING under preferences) | Which preference page holds it is unrecorded. The settings index draws navigation only and the toggles live one level down under categories/, which is denylisted as a family (_audit/2026-09-19-settings-tail-addresses.md), so every spelling there refuses on the same substring. D5's second costume: if the settings ruling reaches it, it is EXCLUDED-RULED. |
| N 184 | `/events/12345/` | NAMED | `NO-PATTERN` | linkedin_server/readonly.py (events entry names N 184 at /events/<id>/) | The events family admits the root only (also driven), one segment narrower than groups; pinned by a committed test. **Also driven:** `/events/` admitted. |
| N A3 | `/company/placeholder-org/admin/following/` | NAMED | `FORBIDDEN[/follow]+NO-PATTERN` | _audit/2026-09-20-admin-rights-ready.md (A3) | Refused on /follow before the allowlist; the alternative spelling (also driven) carries no forbidden substring and is refused by the anchor alone, so the gate's grip depends on the spelling LinkedIn serves. Precondition unmeasured: whether he administers any Page. **Also driven:** `/company/placeholder-org/admin/page-following/` refused. |
| N A5 | `/company/placeholder-org/admin/` | INFERRED | `NO-PATTERN` | linkedin_server/company_page.py (admin_surface: /company/<x>/admin/) | The credit-balance sub-path is unrecorded; the census cell says /invite, and the recheck tsv's synthetic spelling of that claim is driven too. Every spelling under the admin root refuses, because the company pattern admits the root only. Precondition unmeasured, as A3. **Also driven:** `/company/placeholder-org/admin/invite/` refused. |

### NO-ADDRESS -- 2

| row | dir | source | derives from |
|---|---|---|---|
| P O23 | R | _audit/_census/profile.md row O23 | Derives from a profile WRITE: whether a photo, banner or headline change notifies the network is observed on OTHER accounts after the act, not on any page of his. Measurable only by firing a profile write and watching another account; writes_enabled is False. |
| N 171 | R | _audit/_census/network.md row 171 | Derives from the JOIN write: exposure to a group's members is a cost of joining, not a page. D5: is a passive cost a capability row. |

### NEEDS-SESSION -- 6

| row | dir | source | what is unknown, exactly |
|---|---|---|---|
| P D25 | R | _audit/_census/profile.md row D25 | Unknown: the href of the three 'Add section' anchors on /in/me/. A live probe measured them (rel same-host-path, path_depth 2, no ARIA disclosure) and drove their target through is_read_url, recording False with zero forbidden tokens -- but it recorded the boolean and deliberately never the address, and the census cell says the operator must name it. Not re-drivable offline. |
| P L4 | R | linkedin_server/readonly.py (newsletters entry comment) | Unknown: which address serves newsletter analytics. The shipped boundary says so itself: the per-newsletter spelling is UNMEASURED, the page listing his newsletters links no analytics address, and the row is waiting on a LIVE READ that establishes which address serves. Every candidate the corpus names is driven below and refuses, but a client-side tab on an admitted analytics page is not excluded. **Also driven:** `/newsletters/placeholder-newsletter/analytics/` refused, `/analytics/creator/newsletters/` refused, `/analytics/newsletter/` refused. |
| M C83 | R | linkedin_server/readonly.py (newsletters entry comment) | Same unknown as P L4: which address serves newsletter analytics. readonly.py names this row by id and says it waits on a LIVE READ, not on an allowlist line. NOTE the conflict: census_completion.RULING_BLOCKED_NAMED files this row under D3 (a reasoned allowlist refusal); the shipped comment says the refused spelling was never observed served. **Also driven:** `/newsletters/placeholder-newsletter/analytics/` refused, `/analytics/creator/newsletters/` refused, `/analytics/newsletter/` refused. |
| M M34 | R | _audit/_census/messaging-and-content.md row M34 | Unknown: whether LinkedIn addresses a message search by url at all. If it does, the admitted messaging pattern takes NO query group, so any query spelling refuses (a representative spelling, constructed here, is driven); if it is typing into the box, the press ruling refuses typing outright. Both branches are closed; which one is the real one is unestablished. **Also driven:** `/messaging/?keywords=placeholder` refused. |
| N 61 | R | _audit/2026-09-19-the-read-rows.md 5.3 | Unknown: where followed hashtags are drawn. /feed/following/ refuses on /follow and /feed/hashtag/ has no pattern; /in/me/details/interests/ is admitted but measured to redirect to the profile, and the Interests tabs were measured url-less radios on the COMPANIES tab only -- extending that to hashtags is inference. The two candidates carry opposite verdicts, so the class waits on a look. **Also driven:** `/feed/following/` refused, `/feed/hashtag/` refused, `/in/me/details/interests/` admitted. |
| N 95 | R | _audit/2026-09-19-the-unassigned-21.md section 1 | Unknown: where the list of recent PEOPLE searches is drawn. The two history spellings the corpus names (driven) both refuse and neither is shown to draw this list; the census's own section 5 prices rows 79-96 on the people-search pattern plus a query builder, which is the RE-RUN half and is D1. Unrouted in the blocker map (UNASSIGNED). **Also driven:** `/mypreferences/d/search-history` refused, `/jobs/search-history/` refused. |

### UNDETERMINED -- 2

| row | dir | source | what is unknown, exactly |
|---|---|---|---|
| M M9 | R | _audit/2026-09-20-the-live-capture.md 12.3-12.4 | No committed source names a message-requests address. The only admitted messaging address (also driven) redirects INTO one thread LinkedIn chooses and drew no requests entry point (requests 0, message request 0, against focused/unread/starred 1 each); none of the seven sanctioned filter pills is a requests pill. That wave ruled further browser loads useless here: what is missing is an address that LISTS conversations, which is desk work. **Also driven:** `/messaging/` admitted. |
| M M28 | R+W | _audit/2026-09-20-the-live-capture.md 12.3-12.4 | Same hole as M9 for the VIEW half: archived 0 on the only admitted messaging address, no archive pill among the seven sanctioned, and no address lists conversations. The RESTORE half is a write. **Also driven:** `/messaging/` admitted. |

### The three refusal sentences, verbatim from `readonly.assert_read_url`

Every REFUSED row above carries one of these kinds. `<url>` is the row's
address and `<s>` the substring named in its refusal column.

* **`NO-PATTERN`, 20 rows** -- *"navigation blocked: `<url>` is not on the
  read-only allowlist. Add a pattern to readonly._ALLOWED_URL_PATTERNS only if
  the target is genuinely a page that displays the operator's own data."*
* **`FORBIDDEN[<s>]+NO-PATTERN`, 4 rows** (P L2b and N A3 on `/follow`, P M12 on
  `/jobs/application`, N 183 on `/mypreferences/d/categories/`) -- *"navigation
  blocked: `<url>` contains `<s>`, which is not a read surface. This is the
  READ door and it refuses; a write goes through assert_write_url, which is
  narrower still. If you reached this, a url was built wrong. AND NO READ
  PATTERN ADMITS THIS ADDRESS EITHER, so removing this substring would not make
  it readable. Both gates refuse it, and the substring is merely the first."*
* **`FORBIDDEN[<s>]+PATTERN-WOULD-ADMIT`, 0 rows** -- the same sentence ending
  *"A READ PATTERN DOES ADMIT THIS ADDRESS, so this substring is the ONLY thing
  refusing it"*. No bucket-3 row is refused by a write guard alone.

**Which of the 20 allowlist-silence refusals rest on a cause somebody wrote
down is exactly the question D3 asks, and this wave does not answer it.** A
first draft of this section split them 9 and 11 and was withdrawn before it
landed: several of the "11" (N A5's admin root, M C39's query group, N 184's
event page) turn out to carry a written cause in `readonly.py` after all. The
refusal KIND is measured; the refusal's REASON is a reading of prose, and this
table does not claim it.

---

## 6. WHAT COULD NOT BE DETERMINED, AND WHY

**Ten rows carry no address at all**, and the boundary question is open for
every one of them:

    NO-ADDRESS      P O23   derives from a profile write, observed on other accounts
                    N 171   derives from the join write -- a cost, not a page
    NEEDS-SESSION   P D25   the href of three drawn anchors, measured and never recorded
                    P L4    which address serves newsletter analytics
                    M C83   the same unknown as P L4
                    M M34   whether a message search is url-addressed at all
                    N 61    where followed hashtags are drawn
                    N 95    where the recent-search list is drawn
    UNDETERMINED    M M9    no address lists conversations; the one live look found none
                    M M28   the same hole, for the archived view

**Seven addresses are INFERRED, and for six of them the class cannot move** --
every spelling in the family gets the same verdict: P L8 (all three hub
candidates refuse), P M11 (no pattern among the 42 names any resume path),
M C29 (both pages a post's comments render on, its permalink and the feed, are
admitted), N 94 (the people pattern admits any query), N 183 (the whole
`categories/` family refuses on one substring) and N A5 (the company pattern
admits the root only, so everything under `/admin/` refuses). **P M12 is the
one whose class could move**: its address is inferred from the sibling row M1,
and whether AI resume feedback renders on an admitted job posting has never
been looked at.

**A cold source check ran over all 67 rows and was taken at its word only
after its evidence was read.** A verifier with no part in writing the table
re-resolved every row's source against the tree and quoted the supporting line
for every claim. It returned 67 supported, and its two caveats were real: the
literals first cited for M C29 and N 178, and the passage first cited for
N 177, are tagged in their own files for OTHER rows. All three were re-sourced
to the audit that actually ties them, and M C29's basis dropped to INFERRED.
Reading its evidence also turned up one inherited imprecision it had passed:
the read triage says P H11's phrase sits in `shape._TOPCARD_CHROME`, and that
set holds the "add services" prompt, not the section.

**Two statements in the table are UNVERIFIED and marked so in their rows**:
that M C85's poll results render before a vote (a vote is an irreversible
write), and that `/dashboard/` is the hub P L8 names.

**The gate column is a judgement, not a measurement.** Each non-READER gate
names its committed source, and the PRESS and PRESS-PERMITTED gates rest on the
shipped press gate called in-process, but no instrument can check that the
FIRST gate named is the first a reader wave will actually meet.

**And none of the 33 ADMITTED verdicts says the page draws the payload.** The
interests detail page is the standing counter-example: admitted, and measured
to redirect to the profile.

---

## 7. WHAT THE MEASUREMENT FOUND BESIDES THE COUNT

### 7.1 Two rows sit on the admitted profile, not on the detail spellings the triage priced

The read triage filed P H11 and P F1 as ADDRESS/ABSENT, pricing
`/in/me/details/services/` and `/in/me/details/recommendations/`. Both
spellings do refuse, and both are driven in the table. But neither is where
the repository's own evidence puts the payload.

P H11 is *"the Providing services section AS RENDERED ON THE PROFILE"*, and the
2026-09-05 network-tail wave measured `/in/me/` admitted for exactly that
reason, noting the read row costs zero allowlist entries. P F1's route, per the
recommendations module's own ruling and the four-instrument section probe, is
the recommendations SECTION on `/in/me/`. Both are ADMITTED with a MEASURE
gate: nobody has established that either section renders on a passive load.

    network-tail, section 3:            `_audit/2026-09-05-network-tail.md`
    the section probe and its ruling:   scripts/_probe_profile_sections_live.py,
                                        tests/test_every_orphan_module_is_ruled.py

### 7.2 N 172's page has been admitted since the people-search admission

A member's connection list is the people search with a `connectionOf` query.
`tests/test_the_search_shaper_emits_no_name.py` carries that spelling as a
people-search route, and the people pattern admits any query, so
`/search/results/people/?connectionOf=placeholder-member` is ADMITTED. The
2026-09-19 wave priced this row on the member's profile, which still refuses,
the day before the search admission landed. **The row is not buildable
anyway**: the value is another member's identifier, which is the needle D1
keeps out, and the row is filed under the other-people cause of D3. It moves
from the boundary to a decision -- RULING, not REFUSED.

### 7.3 M C83 is on the D3 list and the boundary says its address was never seen

`census_completion.RULING_BLOCKED_NAMED` files M C83 under D3, "is a reasoned
allowlist refusal written". The shipped boundary's own newsletters entry says
the refused spelling is UNMEASURED -- nobody has seen LinkedIn serve it, the
page listing his newsletters links no analytics address -- and that the row
waits on a LIVE READ, not on an allowlist line. Both can hold. But ruling D3
would not make M C83 buildable, because the address it would rule about has
never been observed.

### 7.4 One shipped instrument next to this one is red at HEAD, and nothing runs it

`scripts/triage_read_gap_rows.py` fails its own CONTROL 4: its table carries
verdicts for N 33, N 53, N 54, N 83 and N 175, all out of GAP. The 2026-09-21
reachability wave saw four of the five and deliberately did not re-key it. Not
repaired here either -- it is another instrument's table -- but no test runs
it, which is how it came to be red without anybody being told.
`tests/test_read_addresses.py` runs this wave's checker so the same cannot
happen to it.

### 7.5 Where one decision moves several rows

* **D1 (may a search keyword be passed) holds 5 of the 9 RULING rows**: N 79,
  N 93, N 94, N 172, N 194. It is the highest-yield open decision inside
  bucket 3.
* **One refusal stands first in front of 3 PRESS rows**: no sensitivity basis
  is declared for `/in/me/` (P D28, P J4, N 76). An entry would clear that
  condition for all three and prove nothing else about them -- P J4's control
  was measured inert and P D28's is not proven to exist -- and N 76's own cell
  states why the argument for such an entry is circular: it would assert the
  absence of exactly what only the press could reveal.
* **One control holds 7 PRESS rows**: the All-filters panel on the people
  search (N 84, N 85, N 86, N 87, N 90, N 91, N 92), refused at condition 2
  terminally. The press-free route through response bodies needs a reader the
  package lacks, with an admission heavier than the press.

---

## 8. THE REAL SIZE OF "BLOCKED ON NOTHING"

    bucket 3 as census_completion.py counts it                   67
    ADMITTED at the boundary                                     33
    ADMITTED and a reader can be written today                    5
        READER            M M49   a thread page; the indicators live there
                          M C85   a post permalink; poll results as counts
        PRESS-PERMITTED   P O3    one name-free shaper for a panel of people
                          N 134   the same shaper, same surface
                          M C72   a caller wiring the off_state counter
    ADMITTED and a session is the only thing first                7
        MEASURE           P F1, P H11, P K8
        BUILT-UNFIRED     N 80, N 81, N 88, N 89

**5 is the number a reader-building wave should be sized on.** 12 if that wave
also holds a browser slot. Two of the five (P O3, N 134) are one artifact, and
`dom.py`'s readonly-ok waiver budget is at its cap of 22, so that shaper must
reuse an already-declared in-page script or argue for the cap.

---

## 9. THE INSTRUMENT, AND HOW IT IS SHOWN FAILING

`scripts/check_read_addresses.py` reads `_audit/_census/read-addresses.tsv`,
takes the bucket-3 population from `census_completion.walk()`, and exits 1 on:
a recorded verdict the live `readonly.is_read_url` disagrees with; a refusal
kind the live `readonly.assert_read_url` disagrees with; an `also_driven`
verdict that has moved; a bucket-3 row with no line; a line for a row that has
left the bucket; a duplicated row; a moved direction cell; a source that no
longer resolves (the file, a `::SYMBOL` in it, or a census row it names --
24, 19 and 24 of each on the real table); and any break in the table's
vocabulary. Before it compares anything it shows the boundary saying
both words -- `/feed/` admitted, a third party's profile refused -- so a gate
mutated into admit-everything is named as the cause rather than seen as drift.

**The boundary is imported lazily**, inside the three functions that need it.
`census_completion.py` imports this module to count the table, and
`scripts/_check_census_completion_can_fail.py` runs that instrument inside a
copy of the tree with no `linkedin_server` package in it.

**SHOWN FAILING**, in `tests/test_read_addresses.py`, every plant into a COPY of
the real table and every one asserted red AND naming its row:

    a consistent wrong verdict on an ADMITTED row     only the live boundary convicts it
    a consistent wrong verdict on a REFUSED row       the same, the other direction
    a missing row                                     "NO line in the table"
    a row that left the bucket                        "NOT a bucket-3 row today"
    a duplicated row, a moved direction cell
    a wrong refusal kind, a wrong also_driven verdict
    a class contradicting its own verdict, or its own refusal,
    an off-alphabet gate, an addressless row with no reason
    a source whose file, symbol or census row is gone, or that is not a path
    a table that does not exist                       a named problem, never a traceback
    a boundary monkeypatched to admit everything      the control names it

and **green on the real table**, with the population asserted equal to the
table's keys. The two plants that matter most are the consistent ones: class,
verdict, refusal and gate all agree with each other and are all untrue, and
nothing but the live boundary can tell.

**`census_completion.py` counts the table and pins the split** --
`b3_admitted` 33, `b3_refused` 24, `b3_no_address` 2, `b3_needs_session` 6,
`b3_undetermined` 2, `b3_blocked_on_nothing` 5. If the table stops covering
today's bucket 3 the split is WITHHELD rather than zeroed, so each of those
pins has nothing to check and `--check` fails naming all six.
`scripts/_check_census_completion_can_fail.py` shows it: demonstration B moves
a still-GAP write row to R, the row enters the bucket with no line, and the
split is withheld alongside the two direction figures that move -- all three
demonstrations pass, unchanged.

---

## 10. GATES RUN, AND GATES NOT RUN

**RUN, all on this worktree, all offline:**

    scripts/check_read_addresses.py                GREEN, 67 of 67 rows
    scripts/census_completion.py --check           exit 0, every pin matches (six new b3_ pins)
    scripts/_check_census_completion_can_fail.py   ALL THREE DEMONSTRATIONS PASS
    scripts/count_census_states.py --expect J=56,P=55,M=77,N=86
                                                   all four MATCH, GAP 274, stated rows 704
    scripts/reader_closable_blockers.py            controls 1-4 OK, reader-reachable 67
    scripts/pin_census_rows.py                     no drift: live population is the pin
    tests/test_read_addresses.py                   28 passed; its first run failed 1 of 21 on
                                                   its OWN assertion (the letters of RED inside
                                                   BUILT-UNFIRED), fixed before the first commit
    scripts/impact_gate.py --against 79c5f8e       PASS over 36 files, 1969 tests, 221.3s wall;
                                                   NOT CHECKED 179 of 215 files, said by the gate itself
    the three generators, twice                    INDEX, RULINGS, blocker map at a fixpoint
    the pre-commit identity gate                   0 hits, on every commit of this wave
    the drift control (section 4)                  6 of 6 addresses agree with 2026-09-19
    a cold source verification (section 6)         67 of 67 supported; two caveats acted on

**NOT RUN, and why:**

* **The full suite.** The impact gate scoped this change and said so; the
  files it did not select did not run here. CI runs the whole suite on three
  platforms on push, and this wave does not push. **Its first plan for this
  wave selected 98 of 215 files and widened itself to the full suite** -- the
  new test's module-level constant `REAL` matched the word REAL in dozens of
  docstrings under the gate's constant-coupling rule. The constant was removed
  in this wave's second commit and the plan fell to 36.
* **`scripts/triage_read_gap_rows.py` green.** It is red at HEAD on its own
  control for a reason that predates this wave (section 7.4), and it was re-run
  only to confirm that the red is the same five rows.
* **Anything live.** No reading in this document came from a browser, and none
  was needed: every verdict is the boundary called in-process.

---

## 11. WHAT NEEDS THE OPERATOR

1. **D1 -- may a search keyword be passed?** It is the first gate on 5 of the
   33 admitted rows (N 79, N 93, N 94, N 172, N 194). No reader wave can take
   those five until it is ruled either way.
2. **Whether `/in/me/` gets a sensitivity-basis entry.** It is the first
   refusal in front of P D28, P J4 and N 76, and N 76's own cell argues the
   entry cannot be written honestly. A ruling that it will NOT be written would
   let those three leave the queue as decided rather than sit there.
3. **M C83's D3 filing.** `census_completion.RULING_BLOCKED_NAMED` names it
   under D3, but the boundary's own comment says its address has never been
   seen served; a D3 ruling would not make it buildable. Either the list or the
   row's reason should say so -- this wave changed neither.
4. **Merge notes, not rulings.**
   * `tests/test_read_addresses.py` goes red, by design, the moment any
     bucket-3 row changes state or direction. If a sibling wave in the same
     merge batch banks or re-directs a read row, the table needs the matching
     edit at merge time; the checker names every row it disagrees with, and
     `census_completion.py --check` will report the six `b3_` pins as having
     nothing to check until it is made.
   * `_audit/INDEX.md`, `_audit/RULINGS.md` and `_audit/_census/blocker-map.tsv`
     are generated and every wave regenerates them, so they will conflict:
     regenerate at the merge head rather than hand-merging either side.
   * `scripts/census_completion.py` is touched in five places, all inside this
     wave's own concern: one import, a new `bucket3_split()` after `pct()`, the
     bucket-3 block and the section-5 caveat inside `report()`, the returned
     figures, and six pins appended to `PINNED`. A sibling wiring bucket 1 or 2
     will likely touch the neighbouring lines.
   * The register section is numbered 57, not 55, so the siblings that read 54
     as the maximum do not collide with it.

---

## 12. THE WAVE'S OWN LOG, KEPT AS WRITTEN

### The plan, as opened

1. Derive N from `scripts/census_completion.py` myself. The order says N = 67
   (R 64 + R+W 3). Any discrepancy is recorded at the TOP of this file before anything else.
2. Read `_audit/2026-09-19-the-read-rows.md` and reuse its method. Reuse its verdicts
   where they still hold at HEAD; re-check 3 of its rows as a drift control.
3. For every bucket-3 row: find the page address (code symbol, test fixture, census prose,
   prior audit), run it through the SHIPPED `readonly.is_read_url`, and classify it
   ADMITTED / REFUSED / NO-ADDRESS / NEEDS-SESSION (definitions below, once fixed).
4. Write the side table `_audit/_census/read-addresses.tsv`.
5. Write the instrument `scripts/<name>.py` that re-runs every recorded address through the
   shipped boundary and exits 1 on any disagreement or any missing bucket-3 row; show it
   failing (planted wrong verdict, planted missing row) and green on the real table.
6. Wire the measured split into bucket 3 of `scripts/census_completion.py`, update its
   section-5 caveat; `--check` must still pass.
7. Gates: scoped gate for what changed, census guards, new tests. Report what ran and what
   did not.

Offline and read-only throughout: no browser, no live page, `writes_enabled` untouched.

### Log

(appended as rows land)

**THE TWO ENTRIES BELOW FIRST CARRIED CLOCK TIMES, AND THE TIMES WERE GUESSED.**
They read 16:50 and 17:35; the box clock read 16:33 when the impact gate ran,
after both entries were written. An agent's sense of elapsed time is not an
instrument, so they are numbered instead. The wave opened at 15:47 by the box
clock, which was read.

#### Entry 1 -- denominator confirmed, prior work located, one shipped instrument found RED

* **N = 67, as ordered, and no discrepancy.** Derived by importing
  `census_completion.walk()` and filtering folded state `GAP` with direction `R`
  or `R+W`: R 64 + R+W 3. By slice: profile 18 (17 R + `P M11` R+W),
  messaging 12 (10 R + `M M28`, `M C85` R+W), network 37. `jobs.md` contributes
  none because it carries no per-row direction column.
* **This is the 68 of `_audit/2026-09-21-what-is-reachable-now.md` less `N 53`**,
  which that wave banked. So the prior per-row work is directly reusable:
  `_audit/2026-09-19-the-read-rows.md` (39 rows by hand),
  `_audit/2026-09-21-the-read-triage.md` (59 P+N rows by remaining cost),
  `_audit/_census/_wave-address-recheck.tsv` (30 addresses re-driven 2026-09-21).
* **`scripts/triage_read_gap_rows.py` is RED at HEAD, on its own CONTROL 4**:
  its hand-authored table still carries verdicts for `N 33`, `N 53`, `N 54`,
  `N 83`, `N 175`, all of which have left GAP. `what-is-reachable-now` saw four
  of the five and deliberately did not re-key it. Not repaired here either; it
  is reported because it is the instrument nearest to this one and nothing
  gates it.
* **The boundary at HEAD: 42 allowed patterns, 33 forbidden substrings**, two
  exact exemptions, two pattern exemptions (listed by importing the module, not
  by grep -- the read-rows scar).

#### Entry 2 -- all 67 rows classified; the side table is on disk

`_audit/_census/read-addresses.tsv` written, 67 data lines, every verdict and
refusal column measured by calling the shipped `readonly.is_read_url` /
`assert_read_url` in-process. Draft split (instrument and census wiring not yet
built):

    ADMITTED 33   REFUSED 24 (NO-PATTERN 20, FORBIDDEN 4)   NO-ADDRESS 2
    NEEDS-SESSION 6   UNDETERMINED 2                         total 67

    of the 33 ADMITTED, first thing past the boundary:
    READER 2   PRESS-PERMITTED 3   MEASURE 3   BUILT-UNFIRED 4   PRESS 12   RULING 9

    BLOCKED ON NOTHING (a reader can be written today): 5 of 67
        M M49, M C85 (READER); P O3, M C72, N 134 (PRESS-PERMITTED)

Drift control on three rows of `_audit/2026-09-19-the-read-rows.md` (M C83,
N 99, N 61; six addresses as that document spelled them): **6 of 6 AGREE, 0
MOVED.** A one-time cross-check of every backticked address the 67 rows' own
census cells name, against what the table drives, found no address that would
change a class (all misses are family prefixes, substrings or context
addresses).
