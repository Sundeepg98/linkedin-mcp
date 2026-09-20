# COMPANY-PAGE-SURFACE, built. What shipped, what did not, and what the
# boundary change admits.

Wave `build-company-page`, 2026-09-20, from master `8efa310`.
Scope: the 16 filed rows of `COMPANY-PAGE-SURFACE`, verdict BUILD.
No write was fired. No browser session was opened. No LinkedIn page was loaded.
Every measurement below is offline, against committed fixtures and the shipped
predicate.

---

## 1. THE BOUNDARY CHANGE, IN ONE LINE

```
^https://www\.linkedin\.com/company/[A-Za-z0-9%\-_]{1,100}/?$
```

`_ALLOWED_URL_PATTERNS` 34 -> 35. Digest `5b5d34b6e3cc8059` -> `6577a7bc8a32d7b8`.
Seven of eight pinned digests byte-identical; `<functions>` unmoved; 33 forbidden
substrings before and 33 after; neither exemption table touched.

### WHAT IT ADMITS

Exactly FOUR addresses, measured over 107 concrete spellings with the shipped
predicate (`scripts/_probe_company_family_blast.py`, `blast_radius.corpus()`'s
67 plus 41 company-family spellings):

```
https://www.linkedin.com/company/<slug>/
https://www.linkedin.com/company/<slug>
https://www.linkedin.com/company/<numeric id>/
https://www.linkedin.com/company/<numeric id>
```

`newly_refused` is empty.

### WHAT IT REFUSES

Zero tabs, zero traversals, zero queries, zero admin paths, zero dotted
segments, zero urn forms, zero non-ASCII digit forms. Named individually
because a widening is only narrow if its refusals are stated:

| refused | census row | refused by |
|---|---|---|
| `/company/<x>/people/` (MEMBER ROSTER) | J 108, N 102 | THIS ANCHOR AND NOTHING ELSE |
| `/company/setup/new/` (CREATES a Page) | -- | THIS ANCHOR AND NOTHING ELSE |
| `/company/<x>/admin/`, `/admin/dashboard/` | -- | THIS ANCHOR AND NOTHING ELSE |
| `/company/<x>/about/` | J 106 | the anchor |
| `/company/<x>/jobs/` | J 107 | the anchor |
| `/company/<x>/life/` | J 109 | the anchor |
| `/company/<x>/posts/` | J 110 | the anchor |
| `/company/<x>/products/`, `/services/` | J 111 | the anchor |
| `/company/<x>/insights/` (+ `?insightType=`) | J 113, J 114 | the anchor, twice (sub-path AND query) |
| any query on the admitted root | -- | the anchor |
| `/company/` and `/company` | -- | the anchor |
| traversals onto `close-account` and onto a member profile | -- | the anchor |
| a slug containing `connect` / `invite` / `follow` | -- | `_FORBIDDEN_URL_SUBSTRINGS`, gate one |

**THE THREE WRITE SURFACES AND THE MEMBER ROSTER CARRY NO FORBIDDEN SUBSTRING.**
`/create` is on the denylist and LinkedIn does not spell Page creation with it.
Asserted, not promised, in
`test_the_dangerous_neighbours_are_refused_by_this_anchor_and_nothing_else`.

### WHICH THIRD-PARTY STRINGS IT CAN AND CANNOT REACH

CAN reach, in the sense that the browser may load the bytes: one organisation's
own Page root -- its feed, its own posts, its About blurb, and on some Pages a
module naming employees the operator knows.

CANNOT reach: the People tab in either spelling, a query on the root, and every
other tab. No member profile is addressable from this entry.

**AND NOTHING READS IT YET.** No tool in the package navigates to this address.
`company_page.py` opens nothing and has no page function. This entry bought a
PRECONDITION and a VOCABULARY. That is the honest accounting, and it is the same
one the `/groups/<id>/` entry wrote for itself yesterday.

What the shaper publishes when a reader is eventually written: integers only.
No slug, no href, no name, no id. Asserted over adversarial inputs in
`test_no_segment_of_any_input_survives_into_the_tally`.

---

## 2. THE RULING: WHICH PRECEDENT THIS IS

Yesterday a groups admission was granted (a group id is NUMERIC, so the address
names nobody) and a search-results admission was refused (the page is a list of
people, so it needs a shaper first).

**A COMPANY ADDRESS IS BOTH, DEPENDING ON THE SPELLING, AND THAT IS MEASURED.**

`scripts/_probe_company_path_segments.py`, over every HTML document this
repository has committed:

```
documents           22
characters          615218
total /company/     86
distinct segments   28
  NUMERIC           21   -- the address names nobody
  SLUG               7   -- the address CAN name somebody
```

One of the seven slugs in the corpus is a SURNAME with a word after it. Sole
traders, eponymous firms and personal brands are a category of Page on LinkedIn,
not an edge case. So `groups.py`'s sentence -- *a slug is a name* -- reaches this
surface with a live example rather than a worry.

**THEREFORE THE ADMISSION WAS MADE ON THE SEARCH-RESULTS STANDARD, NOT THE
GROUPS ONE: the name-free shaper landed in the SAME COMMIT.** That shaper is
`linkedin_server/company_page.py`.

### WHY THE SLUG FORM IS IN THE PATTERN AT ALL

The narrower entry `/company/[0-9]{1,20}/?$` admits TWO addresses against this
entry's FOUR, so it looks strictly safer. It is not.

LinkedIn canonicalises an organisation address: the numeric form's LANDING PAGE
is the slug form. A numeric-only entry admits the request and refuses the
arrival -- and `assert_read_url`'s refusal INTERPOLATES THE URL IT REFUSED. That
is the defect `tests/test_navigation_is_never_derived.py` exists for, where
`/in/me/` resolved to a decorated member path and the operator's own slug went
into a traceback. A narrower pattern paid for in third-party slugs in exceptions,
on the ordinary path, is the worse trade.

**THE REDIRECT IS THE ONE HYPOTHESIS AND IS NOT DRESSED AS ANYTHING ELSE.**
Nobody in this repository has opened a company Page. What IS measured is that
LinkedIn draws BOTH spellings: `notifications.html` links a Page by
`/company/5417062` and every tracked posting links one by `/company/<slug>/`.

### THE ASYMMETRY THAT PAYS FOR THE WIDER PATTERN

`company_page.company_page_url` builds the NUMERIC form only. It refuses
anything that is not a bounded run of the ten ASCII digits, reporting the SHAPE
via `jobfilter.describe_shape` and never the value.

**The list admits what the product serves; the package assembles only what names
nobody.**

---

## 3. EVERY GUARD SHIPS SHOWN FAILING

Four planted mutations, each measured against the roster WITHOUT this wave's
entry (the probe's first run was taken with the entry installed and reported
NEWLY ADMITTED 0 for it -- true, and useless):

| candidate | newly admitted of 107 |
|---|---|
| **the shipped entry** | **4** |
| numeric only | 2 |
| `\d+` -- any Unicode decimal digit | **6**, the four extras being the Arabic-Indic, Extended Arabic-Indic, Devanagari and fullwidth spellings of one id |
| a dot inside the class | **7**, adding `/company/./` and `/company/a..company/` |
| `^...\/company\/.*$` -- THE FAMILY PATTERN | **35, EVERY ONE DEFENDED BY NOTHING** |

The family pattern's 35 include Page creation, Page administration, the member
roster in both spellings, and two traversals whose leading segments lie about
where they go -- one normalising onto an account-ending address and one onto a
member profile.

All four are pinned as executable tests in `tests/test_company_page_boundary.py`,
not only in the probe.

### AND TWO GUARDS CAUGHT DEFECTS IN MY OWN MODULE ON THEIR FIRST RUN

Both were real, both were red before they were green, and both are pinned:

1. **`company_identifier` gave the WRONG DIAGNOSIS on the commonest input.**
   The length check ran before the character check, so a real slug -- routinely
   longer than twenty characters -- was refused as `identifier_too_long` rather
   than `identifier_is_not_numeric`. True, and useless: what a caller needs to
   be told is *that is a name, not an id*, and the refusal is the only place it
   gets said. Order reversed. Pinned by
   `test_a_slug_is_refused_as_an_identifier_and_never_echoed`.

2. **`slug_is_addressable` was LOOSER THAN THE BOUNDARY on a query.** Every
   other function in the module drops the query before reading, on the rule that
   a part never read cannot carry anything -- and this one inherited the habit
   where it is exactly wrong, because the admitted pattern takes no query. It
   reported `/company/<slug>/?foo=1` as reachable where the door refuses it.
   Caught by the coupling test, which is the same instrument the groups wave's
   equivalent caught a real divergence with on ITS first run. Pinned by
   `test_the_shaper_and_the_boundary_agree_address_for_address`.

One documented asymmetry REMAINS and is in the safe direction: a slug carrying a
forbidden substring is refused at gate one, which `slug_is_addressable` knows
nothing about. The boundary can be STRICTER than the shaper and never looser.
Asserted on its own in
`test_the_boundary_is_stricter_than_the_shaper_on_a_forbidden_substring`, rather
than folded into the agreement list -- a coupling check that quietly tolerates a
mismatch has stopped coupling anything.

---

## 4. THE 16 ROWS, ONE BY ONE

Legend: SHIPPED = capability exists, is reachable from a registered tool, and is
tested. PARTIAL = some named sub-fields delivered. GAP = still gap, with what is
missing.

### Rows this wave moved

**J 109 -- Company Page Life tab.** PARTIAL, SHIPPED THIS WAVE.
`linkedin_job_detail` now returns `company_page`, a name-free tally of the
About-the-company card's own hrefs. Measured over the four tracked `job_detail`
fixtures: a hydrated card holds FIVE links, of which TWO are
`/company/<slug>/life/`. So the tool now reports *this employer's Page draws a
Life tab* as a count, at zero extra page loads and without publishing the slug.
Delivered by `linkedin_server/company_page.py :: tally` +
`dom.read_company_about_card` (hrefs added). Tested by
`tests/test_company_page.py` (63 assertions) and the fixture measurement in
`tests/test_company_about_card.py`.
STILL MISSING: the tab's CONTENT. `/company/<x>/life/` is not admitted.

**J 110 -- Company Page Home / Posts tabs.** PRECONDITION SHIPPED.
The Home tab IS the admitted root. The address is open; no reader exists.

**N 33 / N 54 -- connections who work at / follow a Page.** PRECONDITION
SHIPPED, AND THE CHEAP ROUTE IS MEASURED DEAD.

Both render on the Page root, which is now addressable. No reader exists, and
whoever writes one owes it the strictness `company_page.py` already defines --
these two modules name employees the operator knows.

**THE POSTING DOES NOT CARRY EITHER NUMBER.** `dom.read_job_insight_panels` was
dumped whole over both hydrated captures: the applicant panel gives applicant
counts, seniority and education; the company panel gives headcount, growth and
tenure; and NO line in either names a connection. So these two cannot be lifted
off a render the server already performs, the way N 53 and J 106 were. Recorded
so the next wave does not spend the same hour proving it.

### Rows already delivered before this wave (found, not built)

**N 53 -- view a Page's follower count.** SHIPPED, pre-existing.
`shape.company_about_card` -> `followers`, returned by `linkedin_job_detail`
under `company_about`. Tested by `tests/test_company_about_card.py`. Off the job
posting; no company Page is opened.

**J 106 -- Company Page About tab (size, industry, locations).** PARTIAL,
pre-existing. `size_band` and `industry` ship via `shape.company_about_card`.

**LOCATIONS DO NOT, AND THAT IS MEASURED RATHER THAN ASSUMED.** Every line of
the About-the-company card was dumped over three fixtures: the meta row is
`<industry> BULLET <size band> BULLET <N on LinkedIn>` and there is no location
line anywhere on the card, at either hydration state. An organisation's
locations live on the About TAB, which this admission did not buy. The job
posting's own location field is a different fact -- where the ROLE is, not
where the company is -- and must not be substituted for it.

**J 107 -- Company Page Jobs tab / "see all jobs at this company".** SHIPPED,
pre-existing, and it needs no company Page at all.
`linkedin_search_jobs(company_id=...)` -> `jobfilter.company_filter_param` ->
`/jobs/search/?f_C=<numeric id>`, an address admitted since the first commit;
the id comes from `shape.company_id_from_insight_cards`. Tested by
`tests/test_company_job_filter.py` and `tests/test_company_id_resolver.py`.
This row is GAP in the census and the capability exists.

**N 101 -- list an organization's employees via its employee count.**
COVERED-CANNOT-DELIVER, pre-existing and correctly filed. The COUNT ships
(`company_about.on_linkedin`); the LIST is a member roster and is out of scope.

**J 86 -- "I'm interested".** READ HALF SHIPPED (`company_about.interest_control`
is a boolean saying the control is on the page). WRITE HALF REFUSED: it needs its
own url, its own `SANCTIONED_MUTATIONS` entry and its own ruling. Not this wave's.

**N 47 -- follow an organization's Page from the Page itself.** WRITE. The read
half ships as `company_about.follow_state` (Follow / Following). The write is
`linkedin_follow_company`, which addresses from a POSTING, not from the Page.
The Page-side write is not bought and cannot be reached from this entry.

### Rows still GAP, with what is missing

**J 108 -- Company Page People tab.** GAP, AND DELIBERATELY SO. It is a member
roster. Out of scope by the same ruling that put `N 165` (a group's roster) out
of scope by name. Refused by this anchor and by nothing else.

**N 102 -- read employee insights on a Page's People tab.** GAP, same address,
same ruling.

**J 111 -- Products / Services tabs.** GAP. Two sub-paths, neither admitted,
neither drawn anywhere the package already reads.

**J 113 -- Insights tab (Premium).** GAP, AND THE ROUTE IS KNOWN, which is
worth recording because the next wave should not re-derive it.
`https://www.linkedin.com/company/<slug>/insights/?insightType=HEADCOUNT` is
drawn on the job posting itself -- measured in `job_detail.html`,
`job_detail_hydrated.html` and `job_detail_following_hydrated.html`. It needs
TWO boundary changes, not one: a sub-path AND a query, and this admission takes
neither.
**IT IS NOT IN THE ABOUT-THE-COMPANY CONTAINER.** The new tally reads that
container only, and the insights link sits outside it. Reaching it needs a
SECOND anchored container reader -- never a widening of this one, whose
container scoping is the property that keeps a card from being read off the
wrong employer.

**J 114 -- Premium Page Insights CONTENT.** PARTIAL, PRE-EXISTING AND ALREADY
REACHABLE, and this is the largest thing in this report that nobody had
written down. The tab is shut; a large part of its CONTENT is not.

`dom.read_job_insight_panels` reads the *"Exclusive Job Seeker Insights about
<company>"* panel LinkedIn draws on the JOB POSTING, and
`linkedin_job_detail` returns it whole at
`result["insights"]["company_insights"]["lines"]` -- verified on disk at
`server.py`'s `out["insights"] = await dom.read_job_insight_panels(page)`.
Against the committed fixture those lines carry a current headcount total, a
company-wide two-year growth figure, ONE FUNCTION'S two-year growth figure
(which is *growth by function*, for whichever function LinkedIn draws), median
employee tenure, and a bare notice that a 25-point headcount-over-time chart
exists. The chart's own axis description is dropped as noise, so no time-series
VALUES survive.

NOT delivered by it: notable alumni (absent from the package entirely) and job
openings by seniority. Do not confuse the latter with
`result["insights"]["applicant_insights"]["seniority"]`, which is the seniority
mix of CURRENT APPLICANTS to one posting -- a different fact with a similar name.

`dom.company_panel_lines` substitutes the employer out of the rows before they
are published, for the reason its own docstring gives: shaping the heading and
shipping the name three lines below it would be a rule that only looked like
one. Tested by `tests/test_free_read_panels.py ::
test_the_company_panel_is_reported_by_shape_and_is_present` and
`:: test_the_company_panel_carries_its_rows_and_not_its_plumbing`, both green
here.

**So J 114 should not be carrying the same GAP state as J 113.** That is a
census observation from a build wave and is handed over rather than filed.

**N 104 -- find an organization's Page by searching for it.** PARTIAL,
SHIPPED THIS WAVE, by the route that is not search.

"By searching" is `SEARCH-RESULTS-SURFACE`, a different blocker, still held.
What shipped is the other route, and the gap it closed was a SEAM rather than a
feature -- the exact shape `jobfilter.py`'s own first paragraph describes about
J 10: *both halves of that blocker are now built and the row is still GAP,
because nothing joined them.*

The halves: `shape.company_id_from_insight_cards` reads a NUMERIC organisation
id off the posting's Premium insights panel, and `/company/<numeric id>/` went
on the allowlist in this wave. `linkedin_job_detail` now returns
`company_page_url` -- the built address, or `None` when the id did not resolve.

**THE ADDRESS IS PUBLISHABLE BECAUSE IT IS NUMERIC.** A slug is a name and a
digit run cannot be one; `company_page.company_page_url` refuses anything else
and reports the shape rather than the value. Tested by
`tests/test_job_detail_wiring.py :: test_the_tool_joins_the_resolved_id_to_a_page_address`,
which also asserts the shipped door admits what the tool hands over, and by its
control `:: test_a_posting_with_no_resolved_id_gets_no_address_rather_than_a_guess`
-- the id is absent on four of the five tracked captures, so the `None` branch
is the normal case rather than an edge.

STILL MISSING: finding a Page by NAME. That needs the search surface.

### ONE CREDIT I WAS OFFERED AND REFUSED

A recon slice run for this wave proposed PARTIAL for J 110 (Home / Posts) and
J 111 (Products / Services) on the reasoning that `company_page.tally` returns
a count at every position in `TAB_KINDS`, so every tab gets "a link-existence
count".

**I am not taking those two.** The count at `posts_tab` and at `products_tab`
is ZERO on every tracked posting, because the About-the-company card links
neither. A zero in a positional list is not evidence that a tab exists; it is
the absence of evidence either way, and crediting it would be the same move as
reading an empty harvest as "this employer has no follower count" -- the
confusion `dom.read_company_about_card` keeps a three-way state to prevent.

J 109 is credited because its count is TWO and was measured; J 110 and J 111
stay GAP.

### The measured zero worth carrying forward

`company_page.page_roots` is **0** on every tracked posting. **The
About-the-company card never links the Page ROOT, only the Life tab.** So "is
this employer's Page addressable" is not answerable from the card, and a future
wave that assumes otherwise will get a zero and misread it as "no Page".

---

## 4b. A DEFECT FOUND ON THE WAY, AND FIXED

`dom.unfollow_control_selector` builds an XPath that a CLICK is assembled from,
and its docstring promised *"company_id must be digits, so nothing a caller
supplies can escape the quoting or widen the predicate."* It was written with
`str.isdigit()`.

**MEASURED AT HEAD: it accepted the Arabic-Indic spelling of a four-digit id
and built the selector.** Nothing was ever at risk -- LinkedIn's hrefs are
ASCII, so that selector matches nothing -- and that is not the point. A guard
on a write-path string was certifying a property it did not have, which is the
same finding `groups.py` made on its own identifier gate: *a charset wide
enough to hold a slug is wide enough to hold a name.*

Narrowed to a membership test against the ten ASCII digits, and bounded at
twenty -- `jobfilter._MAX_ID_LEN`'s number rather than a new one. Pinned by
`tests/test_unfollow_fixture.py :: test_the_selector_refuses_another_script_s_digits`
(all four scripts, each asserted `str.isdigit()` True first, so the case stops
meaning anything the day it stops being accepted) and
`:: test_the_selector_refuses_an_unbounded_digit_run`, which asserts both sides
of the cap.

NO WRITE WAS FIRED. This narrows a guard; it does not exercise one.

---

## 5. WHAT THE CENSUS SAID AND WHAT THE CODE SAYS

`network.md` section 5 prices this family as *"One pattern for
`/company/<slug>/`. Also closes `follow_company`'s residue: a posting gives a
slug, unfollow addresses a numeric id, nothing resolves one to the other. A
company page carries both."*

The pattern shipped. **The residue did NOT close, and the costing's premise is
half right.** Measured on `job_detail_following_hydrated.html`: one posting
carries FOUR distinct company slugs and ONE numeric id. The three extra slugs
belong to OTHER organisations on the insight cards, so "the posting gives a
slug" is true and picking the EMPLOYER's slug requires the same discrimination
`company_id_from_insight_cards` already performs for the id -- it is not a grab.
A company Page would carry both unambiguously; nobody has opened one.

---

## 6. FILES

Shipped:

- `linkedin_server/company_page.py` -- NEW. The name-free shaper.
- `linkedin_server/readonly.py` -- ONE allowlist entry and its comment.
- `linkedin_server/dom.py` -- `unfollow_control_selector`'s digit guard
  narrowed from `str.isdigit()` to the ten ASCII digits, bounded at twenty;
  `read_company_about_card` returns `hrefs`;
  `ABOUT_COMPANY_MAX_LINKS`. A plain Playwright read: **no script is injected**,
  so `INJECTED_SCRIPTS`, the `EXECUTED_SCRIPTS` count and the `dom.py` waiver cap
  are all unmoved.
- `linkedin_server/server.py` -- the import, and TWO fields on
  `linkedin_job_detail`'s result: `company_page` (the tally) and
  `company_page_url` (the N 104 join).
- `scripts/_probe_company_path_segments.py` -- NEW instrument: is a company slug
  a name? Asks the corpus.
- `scripts/_probe_company_family_blast.py` -- NEW instrument: the entry's blast
  radius plus four controls, measured against the pre-wave roster.

Tests:

- `tests/test_company_page.py` -- NEW, 64 tests. The shaper.
- `tests/test_company_page_boundary.py` -- NEW, 45 tests. The limits, with
  four planted mutations shown firing.
- `tests/test_readonly.py` -- `/company/example-co/` left `MUST_STAY_UNREADABLE`
  and NINETEEN neighbours joined it. Recorded, not silently dropped: the risk
  was never that one root opened, it was that a family did.
- `tests/test_readonly_boundary_invariant.py` -- re-pinned, both dicts, with the
  ledger entry and the attribution.
- `tests/test_refusal_names_both_gates.py` -- its needle moved one segment
  deeper, because the old one became readable.
- `tests/test_job_detail_wiring.py` -- FOUR new tests on the seam: the tally
  is plumbed, no slug survives onto the wire, the N 104 join, and its
  unresolved-id control.
- `tests/test_unfollow_fixture.py` -- the digit-class guard, shown failing.

Attribution: the tree MINUS this wave's one allowlist line hashes to
`5b5d34b6e3cc8059`, the value it replaces. Controls behave -- dropping the
pre-existing `/school/` line instead lands on `bd5f83178ce63d94`, and a needle no
line carries drops zero lines and moves nothing.

Local runs: a 14-file GREEN BASELINE was taken at the tree before anything was
touched -- 1516 passed, 0 failed. After the change, sweeps over the touched set
and its neighbours: 1005, 855, 752, 328, 190 and 118 passed, 0 failed.

**THE FULL SUITE IS CI'S.** The first commit is CERTIFIED GREEN: run
35481841288 completed success across all 18 jobs -- ubuntu 3.10 x 6 shards,
ubuntu 3.13 x 6, windows 3.13 x 6. Later commits are queued behind it on the
same branch.
