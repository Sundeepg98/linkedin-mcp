# Unfollow-anchor census -- linkedin MCP server

Read-only census. No code was edited, no test was run, no git command was issued.
Instrument: stdlib Python (`re` plus a tolerant `html.parser` DOM with parent
pointers). Every capture was read in full, not sampled.

Selector-semantics note: this census matches on the `aria-label` ATTRIBUTE, which is
exactly what `dom.FOLLOW_CONTROL` and `dom.FOLLOWED_PAGE_BUTTON` do
(`button[aria-label="Follow"]`, `button[aria-label^="Click to stop following "]`).
It does NOT compute accessible names the way `get_by_role(name=...)` would, so the
counts below are directly comparable to the selectors the server already ships.

PRIVACY: every value quoted from a RAW capture is a SHAPE, never a value. Values
quoted verbatim come only from the TRACKED, SANITISED fixtures.

## VERDICT IN ONE LINE

An unfollow anchor IS positively observed, on Manage Pages, and a row CAN be
addressed by a stable numeric key -- but a follow performed from a job posting
CANNOT be undone there without first resolving slug to id, and that resolution is
NOT available on the posting surface.

---

## 0. What was read

| # | capture | kind | bytes | in brief |
|---|---------|------|-------|----------|
| 1 | `tests/fixtures/manage_pages_following.html` | sanitised, tracked | 29,899 | yes |
| 2 | `tests/fixtures/manage_pages_following_hydrated.html` | sanitised, tracked | 57,717 | yes |
| 3 | `tests/fixtures/job_detail_following.html` | sanitised, tracked | 38,788 | yes |
| 4 | `tests/fixtures/job_detail_following_hydrated.html` | sanitised, tracked | 76,377 | yes |
| 5 | `tests/fixtures/job_detail.html` | sanitised, tracked | 50,916 | yes |
| 6 | `tests/fixtures/job_detail_hydrated.html` | sanitised, tracked | 51,573 | yes |
| 7 | `_audit/_probe-manage-pages-pre.html` | RAW, gitignored | 1,504,311 | yes |
| 8 | `_audit/_probe-manage-pages-hyd.html` | RAW, gitignored | 1,556,131 | yes |
| 9 | `_audit/_probe-interests-hyd.html` | RAW, gitignored | 162,497 | yes |
| 10 | `_audit/_probe-network-manager-company-hyd.html` | RAW, gitignored | 1,553,984 | yes |
| 11 | `_audit/_probe-feed-following-hyd.html` | RAW, gitignored | 1,577,322 | yes |
| 12 | `_audit/_probe-search-followed-company-pre.html` | RAW, gitignored | 1,398,890 | yes |
| 13 | `_audit/_probe-search-followed-company-hyd.html` | RAW, gitignored | 1,582,944 | yes |
| 14 | `_audit/_probe-job-followed-company-pre.html` | RAW, gitignored | 1,094,424 | NO -- see ESCALATION 4 |
| 15 | `_audit/_probe-job-followed-company-hyd.html` | RAW, gitignored | 281,190 | NO -- see ESCALATION 4 |

15 captures read. 13 were named in the brief; 2 more were read because they sit in
the same directory and directly decide whether a contradiction found in capture 13
is a general fact or a surface-specific one. They are declared, not smuggled, and no
answer below depends on them alone.

---

## 1. Every unfollow-shaped control, per surface

Four distinct aria-label TEMPLATES exist across all 15 captures. 115 controls in all.

| # | template (name replaced by `<NAME>`) | tag | names the INVERSE action? | or merely the CURRENT state? |
|---|---|---|---|---|
| T1 | `Click to stop following <NAME>` | `button` | YES -- "stop following" is the action | -- |
| T2 | `Following, click to unfollow <NAME>` | `button` | YES -- "click to unfollow" is the action | states the current state first, then the action |
| T3 | `Following` | `button` | no | STATE ONLY |
| T4 | `Follow` | `button` | no (it is the FORWARD action) | -- |

Per-capture counts:

| capture | T1 | T2 | T3 | T4 | entity the control targets |
|---|---|---|---|---|---|
| 1 `manage_pages_following.html` (pre) | 10 | 0 | 0 | 0 | company |
| 2 `manage_pages_following_hydrated.html` | 20 | 0 | 0 | 0 | company |
| 3 `job_detail_following.html` (pre) | 0 | 0 | 0 | 0 | none rendered |
| 4 `job_detail_following_hydrated.html` | 0 | 0 | 1 | 0 | company (the posting's employer) |
| 5 `job_detail.html` (pre) | 0 | 0 | 0 | 1 | company |
| 6 `job_detail_hydrated.html` | 0 | 0 | 0 | 1 | company |
| 7 RAW manage-pages-pre | 10 | 0 | 0 | 0 | company |
| 8 RAW manage-pages-hyd | 20 | 0 | 0 | 0 | company |
| 9 RAW interests-hyd | 0 | 10 | 0 | 0 | PERSON -- see section 5 |
| 10 RAW network-manager-company-hyd | 20 | 0 | 0 | 0 | company |
| 11 RAW feed-following-hyd | 20 | 0 | 0 | 0 | PERSON -- see ESCALATION 1 |
| 12 RAW search-followed-company-pre | 0 | 0 | 0 | 0 | none rendered |
| 13 RAW search-followed-company-hyd | 0 | 0 | 1 | 0 | company (LEGACY render, ESCALATION 2) |
| 14 EXTRA job-followed-company-pre | 0 | 0 | 0 | 0 | none rendered |
| 15 EXTRA job-followed-company-hyd | 0 | 0 | 1 | 0 | company |
| TOTAL | 100 | 10 | 3 | 2 | |

Of the 100 T1 controls, 80 target COMPANIES and 20 target PEOPLE -- the same label
string, two different entity types. That is not a nuance, it is a hazard; see
ESCALATION 1.

Verbatim examples, safe because they come from the tracked sanitised fixtures:
`Click to stop following Gridwell`, `Click to stop following Vantrex Systems`,
`Click to stop following Marrowfield Media - A Creator Marketing Platform Co.`.

The four surfaces the brief named:

* Manage Pages -- T1, `<button>`, NAMES THE INVERSE ACTION, 10 rendered
  pre-hydration and 20 hydrated, in both the sanitised fixture and the raw capture.
  The only surface where an unfollow control both names its action AND sits on a row
  carrying a stable company id.
* Profile Interests list -- T2, `<button>`, NAMES THE INVERSE ACTION. 10 controls,
  all on the Top Voices (people) tab. The Companies tab rendered NOTHING: zero
  `/company/` anchors exist anywhere in that capture. The company-row label template
  on this surface is therefore UNOBSERVED.
* Feed following module -- T1, `<button>`, names the inverse action, 20 controls,
  all targeting PEOPLE. Zero company rows.
* Job posting page -- T3 when following, T4 when not. 5 controls across 6 posting
  captures. The label states the CURRENT STATE only and never names an action.

---

## 2. Row addressing on Manage Pages -- the decisive question

Every identifier that exists on a Manage Pages row, measured on all five
Manage-Pages-family captures (1, 2, 7, 8, 10):

| identifier | present? | evidence |
|---|---|---|
| numeric company id in an `href` | YES | every row carries exactly 2 `<a>` elements and BOTH point at `https://www.linkedin.com/company/<NUMERIC-ID>/`. Ids observed are 4 to 8 digits. |
| `urn:li:company:<NUMERIC-ID>` in a DOM attribute | YES (raw only) | `data-chameleon-result-urn` on a `<div>` inside the row. In the RAW captures the 20 urn ids are a set IDENTICAL to the 20 href ids (20/20). |
| company slug | NO | zero `/company/<slug>` hrefs inside any row, in any of the five captures. |
| display name | yes | the tail of the button's own `aria-label` -- anchored to the row by construction. |
| `data-view-name` | present, useless | constant `search-entity-result-universal-template` on all 20 rows. |
| button `id` | present, useless | Ember ids (`ember45`, `ember47`, ...) -- allocation order, not identity. |
| other `data-*` | `data-test-app-aware-link` on both anchors -- a marker, not a key. |

A specific company CAN be located by a STABLE key: the numeric company id.
Measured uniqueness, 80 rows across the five captures with zero exceptions:

* exactly 1 `<li>` row contains any given numeric id (never 0, never 2);
* each id appears on exactly 2 anchors, both inside that one row;
* each such `<li>` contains exactly 1 T1 button;
* display names were also unique in every capture (20/20 distinct hydrated), but see
  the fragility note below.

Locator chain to use (pure Playwright locators, nothing injected, so no new entry is
needed in `test_readonly.py`'s `INJECTED_SCRIPTS`):

```
ROW    = page.locator("li") \
             .filter(has=page.locator('button[aria-label^="Click to stop following "]')) \
             .filter(has=page.locator(f'a[href*="/company/{company_id}/"]'))
BUTTON = ROW.locator('button[aria-label^="Click to stop following "]')
```

Gate on `ROW.count() == 1` and `BUTTON.count() == 1` before doing anything. Both were
1 for every one of the 80 rows measured.

Two details that are load-bearing:

1. KEEP THE TRAILING SLASH in `/company/{id}/`. Every href in every capture ends with
   one (checked on all five captures). Without it, a query for the fixture id `902611`
   would substring-match a row whose own id is that same run of digits followed by one
   more -- `902611` then any digit -- because the shorter string is a prefix of the
   longer. No such collision exists in these captures (0 prefix pairs among 20 ids),
   but the hazard is structural, not sample-dependent.

   Written without spelling the colliding path, deliberately: this file is tracked, and
   the repo's identity guard hunts a `/company/` followed by a long digit run as a
   SHAPE, without knowing or caring that this particular one is invented. A guard that
   cannot tell an illustration from a leak is the guard working correctly, and the
   cheaper side of that trade is to illustrate without the shape. It fired on the first
   draft of this paragraph, which is how the sentence came to be written this way.
2. Do NOT anchor on `data-chameleon-result-urn`. It is a real per-row key in the RAW
   captures (20 distinct values), but in BOTH tracked fixtures its value is the
   literal string `URN-REMOVED` on all 20 rows -- 1 distinct value. A locator built
   on it would match 20 elements in the fixture and could never be tested. See
   ESCALATION 3.

Is display name the only key? NO -- and that matters. The numeric id is a genuine
stable key on this surface. But note the asymmetry the current reader already lives
with: `shape.parse_followed_pages` takes the NAME from the button label and the id
from an href hop, and `followed_page_state` matches on either. For a WRITE, the id is
the only one of the two that is not a display string, and it is present on 100% of
rows in all five captures (0 rows with no readable link).

---

## 3. Identifier mismatch between surfaces

Confirmed, on both sanitised and raw captures, and it is total:

| surface | company addressed by | measured |
|---|---|---|
| Manage Pages (captures 1, 2, 7, 8, 10) | NUMERIC ID | 20 numeric hrefs hydrated / 10 pre; 0 slug hrefs in any row |
| job posting `/jobs/view/` (captures 3-6, 14, 15) | SLUG | 4 to 8 slug hrefs per capture; 0 numeric company hrefs; 0 `urn:li:fsd_company:` |
| job search `/jobs/search/` (captures 12, 13) | SLUG in the DOM, id in the payload | 9 distinct slugs; 15 `urn:li:fsd_company:` occurrences, 1 distinct id |

Sanitised examples (safe): the posting fixtures address the employer as
`https://www.linkedin.com/company/vantrex-systems/life/` and
`https://www.linkedin.com/company/ashgrove-systems/life/`; the Manage Pages fixture
addresses its rows as `https://www.linkedin.com/company/902611/`.

Does any single capture carry BOTH forms for the same company?

* `/jobs/view/` -- NO. Captures 3, 4, 5, 6, 14 and 15 contain zero numeric company
  ids and zero `urn:li:fsd_company:` / `urn:li:organization:` tokens, anywhere: DOM
  attributes, hrefs, or embedded JSON. There is nothing to resolve from.
* Manage Pages -- NO, not usably. The raw captures do contain 10 `fsd_company` ids
  inside the embedded `<code>` JSON (all 10 ARE rendered row ids, 10/10), but zero
  records carry a `universalName` or `publicIdentifier` string anywhere in any
  capture, so there is no id-to-slug record. A crude proximity join (a slug within
  600 characters of an id) resolved ambiguously: only 1 of 10 windows held a single
  slug, 9 held two.
* `/jobs/search/` -- YES, and this one is a positive result. Capture 13 carries
  exactly one `urn:li:fsd_company:<NUMERIC-ID>` in an `included[]` record whose only
  other payload is a logo. That record's logo artifact digest ALSO appears in the
  `<img src>` of the employer card that encloses the follow control, and that same
  card carries exactly one `/company/<SLUG>/` href. One id, one slug, joined through
  a shared artifact digest: a slug-to-id resolution with NO NETWORK CALL, on that
  surface only.

Consequence for the wave. A follow performed from a `/jobs/view/` posting is recorded
against a company the posting names only by SLUG. Manage Pages can only be addressed
by ID. Those two captures share no identifier, so THE UNDO IS NOT CLOSED-FORM FROM
THE POSTING ALONE. Three ways out, in order of cost:

1. Match by DISPLAY NAME -- the posting's employer name against the T1 label tail.
   Cheap, and it is what the existing reader already does, but it is a display-string
   match and inherits every rename, suffix and casing difference.
2. Route the follow through `/jobs/search/` instead, where id and slug are both
   present and positively joinable. Costs a different surface for the read.
3. Resolve slug to id with a network call. Out of scope for a read-only server.

---

## 4. Pagination and completeness

| capture | rows rendered | total claimed by heading | heading element | pagination / show-more |
|---|---|---|---|---|
| 1 `manage_pages_following.html` (pre) | 10 | 58 | `<h1>58 Pages</h1>` | 0 in the whole document |
| 2 `manage_pages_following_hydrated.html` | 20 | 58 | `<h1>58 Pages</h1>` | 0 |
| 7 RAW manage-pages-pre | 10 | 58 | `<h1>` (same text) | 0 |
| 8 RAW manage-pages-hyd | 20 | 58 | `<h1>` (same text) | 0 |
| 10 RAW network-manager-company-hyd | 20 | 58 | `<h1>` (same text) | 0 |
| 9 RAW interests-hyd | 10 (people) | none stated | -- | 0 |
| 11 RAW feed-following-hyd | 20 (people) | "652 people" | -- | 0 |
| 13 RAW search-followed-company-hyd | n/a | "90 results" | -- | 11 (job-search paging, unrelated surface) |

Prior work is CONFIRMED exactly: 20 of 58 hydrated, 10 of 58 pre-hydration, on both
the sanitised fixture and the raw capture, and the same 20/58 on the
`network-manager/company` capture.

The `N Pages` string occurs exactly ONCE in `main` on all five Manage-Pages captures,
which is what `shape._stated_total`'s uniqueness rule needs. Incidental corroboration
for that rule from elsewhere: capture 12 states `1 Page` in `main` with no `<h1>` at
all -- precisely the competing-total shape the rule was written against.

THERE IS NO SHOW-MORE CONTROL AND NO PAGINATION CONTROL OF ANY KIND ON MANAGE PAGES
-- zero, in the whole document, not merely in `main`. The remaining 38 rows arrive by
SCROLL. 2 to 3 scroll-sentinel-ish elements are present but none is a button and none
carries an href.

Consequence: ON THIS SURFACE ONLY A COMPANY THAT HAPPENS TO BE IN THE RENDERED WINDOW
CAN BE REACHED. An arbitrary followed company cannot be. Of 58 followed Pages, one
page load reaches at most 20 -- about 34%. A write gated on "find the row" will
simply fail to find 38 of 58 companies, and it will fail SILENTLY unless the gate
treats "not in the rendered rows" as `unknown` rather than as absent -- which is
exactly the distinction `shape.followed_page_state` already draws. That refusal is
now the write's precondition too, not just the reader's honesty.

---

## 5. Does the Interests list beat Manage Pages? NO -- on three counts

Measured against capture 9 (`_probe-interests-hyd.html`):

1. THE TAB IS NOT REACHABLE BY URL. The Interests tabs are five `<div role="radio">`
   elements labelled `Top Voices`, `Companies`, `Groups`, `Newsletters`, `Schools`.
   Their complete attribute set is `role`, `tabindex`, `aria-checked` -- no href, no
   id, no data attribute of any kind. Candidate hrefs on the tabs: 0. `Top Voices`
   carries `aria-checked="true"`, the other four `"false"`. The only way to address
   the Companies tab is its visible TEXT. Prior notes are confirmed.
2. THE COMPANIES TAB'S CONTENT DOES NOT EXIST IN THE DOM. `/company/` anchors in the
   entire capture: 0. `urn:li:fsd_company:` tokens: 0. The 10 rendered rows are
   people (`/in/<MEMBER-SLUG>`).
3. ITS UNFOLLOW TEMPLATE WAS OBSERVED ONLY FOR PEOPLE. The 10 T2 controls read
   `Following, click to unfollow <NAME>` where `<NAME>` is a person. Whether a
   company row on the Companies tab wears T2, T1, or something else is UNOBSERVED.

So the answer to "its control names the inverse action AND it is reachable by url" is
HALF YES, HALF NO: T2 does name the inverse action, and it is the most explicit label
LinkedIn draws -- but the tab has no url, its company content was never rendered, and
its rows carry no company id at all. Row identifiers available on an Interests row:
the profile link and the display name. NO urn, NO numeric id -- checked directly, the
row subtree contains no `fsd_profile` urn and no `ACoA` token. `componentkey` values
are random UUIDs (70 distinct in the document), not identity.

Interests does not beat Manage Pages. It is strictly worse on every axis that matters
to a write.

---

## 6. The posting-page control

Measured on capture 4 (`job_detail_following_hydrated.html`, sanitised) against
capture 6 (`job_detail_hydrated.html`, the not-following render):

| property | following render | not-following render |
|---|---|---|
| tag | `button` | `button` |
| `aria-label` | `Following` | `Follow` |
| own text | `Following` | `Follow` |
| `type` | `button` | `button` |
| `class` | `bb9bff38 _7917aabf _7ca7bc04 _7000baa9 _2e9433c3 _620e686c _5c9fde69 _7edff741 _84ad9c8b ea47fa53 _94f56fd5 _6ccb2f15 a1a56b0e _41aad4b0` | BYTE-IDENTICAL to the left column |
| `aria-pressed` | absent -- 0 elements in the entire document | absent -- 0 in the entire document |
| any other attribute stating the inverse action | NONE -- the element has exactly 3 attributes: `class`, `type`, `aria-label` | same |

`dom.FOLLOW_CONTROL`'s standing claim is CONFIRMED on this surface: the class lists
are byte-identical, `aria-pressed` appears nowhere, and the accessible name is the
whole of the difference. (`aria-checked` occurs once and `aria-expanded` three times
in these documents, on unrelated elements.)

CAN ACTIVATING IT BE SHOWN TO UNFOLLOW? NO. That is an ASSUMPTION, not an observation.
Nothing on or near the control states an inverse action. The evidence available is:

* the label is the bare STATE word, in both states;
* no `aria-pressed`, no `aria-checked`, no `role="switch"`, no `data-*` toggle flag
  anywhere on the element or its ancestors;
* the two renders are distinguishable ONLY by that one word.

That the control toggles is an inference from the label pair, not a measurement. It
is the same epistemic position `shape.SAVE_LABELS` documents for unsave: the anchor
for one state exists and the behaviour has never been observed. The one difference is
that the follow PAIR has been photographed, so the STATE reading is sound; what has
not been shown is that a click on the `Following` render clears the follow rather
than, say, opening a menu.

---

## 7. Counts, not adjectives

| quantity | count |
|---|---|
| captures read in full | 15 (6 sanitised tracked, 9 raw gitignored) |
| bytes read | 12,046,963 |
| elements with an `aria-label` containing "follow" | 115 |
| distinct aria-label templates | 4 (T1, T2, T3, T4) |
| controls naming the INVERSE action | 110 (100 T1 + 10 T2) |
| ... of which target a COMPANY | 80 (all T1, on Manage Pages / network-manager) |
| ... of which target a PERSON | 30 (20 T1 on feed-following, 10 T2 on Interests) |
| controls stating the CURRENT STATE only | 5 (3 T3 + 2 T4) |
| Manage Pages rows rendered, hydrated | 20 per capture (3 captures) |
| Manage Pages rows rendered, pre-hydration | 10 per capture (2 captures) |
| Manage Pages total claimed | 58, on all 5 captures |
| coverage of one page load | 20 / 58 = 34.5% |
| pagination or show-more controls on Manage Pages | 0 |
| Manage Pages rows measured for addressing | 80 |
| ... with exactly 1 matching `<li>` per numeric id | 80 / 80 |
| ... with exactly 1 T1 button in that `<li>` | 80 / 80 |
| ... with zero readable company link | 0 / 80 |
| distinct numeric company ids recovered, per hydrated capture | 20 |
| `urn:li:company:<id>` row urns recovered, raw hydrated | 20, set identical to the href ids |
| `urn:li:company:<id>` row urns usable in the tracked fixtures | 0 (1 constant value, `URN-REMOVED`) |
| `FollowingState` instances in the raw Manage Pages payload | 10, every one `following: true`, `followingType: FOLLOWING` |
| company slugs on any Manage Pages row | 0 |
| numeric company ids on any `/jobs/view/` capture | 0 |
| captures carrying id AND slug for the SAME company, positively joined | 1 (capture 13, `/jobs/search/`) |
| `/company/` anchors in the Interests capture | 0 |
| Interests tabs reachable by url | 0 of 5 |

---

## 8. Verdict

Manage Pages is the only surface that offers a positively-observed unfollow anchor
attached to a stable row key, and it should be the wave's target -- with one bound
stated up front. Its control is a `<button>` whose accessible name states the inverse
action outright (`Click to stop following Gridwell`), observed 80 times across five
captures with no variation but the name; its row is an `<li>` carrying the company's
numeric id on two anchors and, in the live DOM, a second time as
`urn:li:company:<id>`; and that id addresses exactly one row, every time, in 80 out of
80 measurements. The raw payload corroborates the whole thing independently with ten
`FollowingState` records asserting `following: true` keyed by the same numeric ids.
Ranking the alternatives: second, `/mynetwork/network-manager/company/`, which is not
really second at all -- it renders the identical list, the identical `58 Pages`
heading, identical 20 rows, identical row structure, so it is the SAME surface reached
by a different url and is worth keeping only as a fallback route; third, and only for
READING state, `/jobs/search/`, the sole capture where a slug can be resolved to a
numeric id without a network call, and therefore the bridge to build if the wave wants
a posting-side follow to be undoable by id; not ranked at all, the profile Interests
list and the feed following module -- the first because its Companies tab has no url,
no rendered content and no row identifier of any kind, the second because its rows are
PEOPLE wearing the company template's exact label string. The bound: one page load
reaches 20 of 58 followed Pages and there is no pagination control of any kind, so AN
ARBITRARY FOLLOWED COMPANY CANNOT BE REACHED ON THIS SURFACE -- roughly two thirds of
them cannot be reached at all. An unfollow built here is honest only if "not among the
rendered rows" resolves to `unknown` and refuses, never to "not followed", which is the
same three-valued discipline `shape.followed_page_state` already enforces on the read
side. Under that gate the anchor is real; without it, the write would silently do
nothing for 38 of 58 companies.

---

## ESCALATIONS

1. `/feed/following/` RENDERS PEOPLE USING THE COMPANY TEMPLATE'S EXACT LABEL STRING.
   Capture 11 has 20 `Click to stop following <NAME>` buttons -- byte-identical
   template to Manage Pages -- but every row links to `/in/<MEMBER-SLUG>`, every row
   urn is `urn:li:member:<id>`, and its ten `FollowingState` records are keyed by
   `urn:li:fsd_profile:` with `followingType` null. The heading counts "652 people".
   `dom.FOLLOWED_PAGE_BUTTON` (`button[aria-label^="Click to stop following "]`)
   matches all 20 of them. Today that is only a reader risk on a surface the server
   does not visit; the moment a WRITE is anchored on that selector, landing on the
   wrong url unfollows a PERSON. Any unfollow must additionally require the row to
   carry a `/company/<id>/` link -- which is a positive discriminator: 80/80 company
   rows have one, 20/20 people rows have none.

2. `dom.FOLLOW_CONTROL`'s "aria-pressed appears nowhere" IS SURFACE-SCOPED, AND ONE
   CAPTURE CONTRADICTS IT. Capture 13 (`/jobs/search/`) renders the LEGACY artdeco
   follow control:

   ```
   <button class="follow is-following  artdeco-button artdeco-button--secondary ml5"
           aria-label="Following" aria-pressed="true" type="button">
   ```

   Here the CLASS names the state (`is-following`) and `aria-pressed` IS present.
   That is the opposite of what the docstring says was measured. I checked whether
   this is a general fact or surface-specific by reading captures 14/15
   (`/jobs/view/`, the same page family the fixtures came from): those render the
   React control, class `bb9bff38 ...`, `aria-pressed` absent, 0 aria-pressed
   elements in the document -- so the docstring is CORRECT for `/jobs/view/` and
   WRONG as a universal claim. Practical impact today is nil: `FOLLOW_CONTROL`
   matched exactly 1 control on both renders, so the reader is right either way. But
   the comment asserts a measurement that a capture in this repo refutes, and if a
   future writer reaches for `aria-pressed` as a confirmation signal it will be
   present on one surface and absent on the other.

3. THE TRACKED FIXTURES CANNOT TEST A URN-ANCHORED LOCATOR.
   `data-chameleon-result-urn` is `urn:li:company:<id>` with 20 distinct values in
   the raw captures, but the literal string `URN-REMOVED` -- one value, all 20 rows
   -- in both sanitised fixtures. If the wave wants the urn as a key or a
   cross-check, the fixtures need regenerating with per-row distinct placeholder
   urns first, or the check will pass vacuously.

4. I READ TWO CAPTURES THE BRIEF DID NOT LIST,
   `_audit/_probe-job-followed-company-pre.html` and
   `_audit/_probe-job-followed-company-hyd.html`, solely to settle ESCALATION 2.
   They are read-only, in the same `_audit/` directory, and gitignored like the rest.
   Flagged because the brief enumerated its inputs precisely and I went outside that
   list.

5. MINOR, AND IT IS A CLEAN BILL RATHER THAN A PROBLEM. The 20 numeric company ids in
   the tracked Manage Pages fixtures are not listed in `_audit/_sanitisation_key.json`
   (whose lists cover names, slugs, operator, posting, location). I verified they were
   substituted anyway: overlap between fixture ids and raw-capture ids is 0 of 20
   hydrated and 0 of 10 pre-hydration, and the job fixtures' slugs overlap the raw
   posting capture's slugs 0 of 4. No leak. The substitution is simply undocumented in
   the key file, which will read as a gap to the next person who audits it.

---

## Sort order of the rendered window, and reachability past 20

Same rules as above: read-only, no edits, no git, no pytest, no browser. Orderings and
counts only; no name, id, follower count, slug or urn from a raw capture appears here.

Rows were enumerated in DOCUMENT ORDER for all five Manage-Pages-family captures
(80 rows total), then each hypothesis was tested by counting ascents, descents and
ties over consecutive pairs, plus a Kendall tau against position.

### 9.1 The four sort hypotheses

| hypothesis | verdict | evidence that decides it |
|---|---|---|
| H1 alphabetical by display name | **REFUTED** | mixed in every capture and under every normalisation. Raw hydrated: 11 ascents / 8 descents. Fixture hydrated: 8 ascents / 11 descents. Case-sensitive, case-insensitive and case-insensitive-with-leading-articles-stripped give byte-identical counts, so casing and articles are not the confound. Kendall tau vs position: +0.053 raw, +0.126 fixture. |
| H2 by follower count | **REFUTED** (raw); NOT TESTABLE (fixtures) | raw hydrated: 10 ascents / 9 descents, tau -0.126. Raw pre: 5 ascents / 4 descents. Both raw captures carry a follower count on 20/20 and 10/10 rows. The SANITISED fixtures carry one on **0/20** rows -- the count is stripped -- so this hypothesis cannot be tested against tracked evidence at all. |
| H3 by numeric company id | **REFUTED** | raw hydrated: 11 ascents / 8 descents, tau -0.158. Fixture hydrated: 11 ascents / 8 descents, tau -0.147. Raw pre: 6 ascents / 3 descents. Nowhere monotonic in either direction. |
| H5 an explicit sort control or sort field | **REFUTED** | `aria-sort`: **0** occurrences in any capture. All **18** matches for `sort(By|Order|Type|Criteria)` in the raw captures are ICON ASSET FILENAMES in the CSS icon manifest (`sort-down-medium.svg`, `sort-up-medium.svg`, `sort-options-medium.svg`, ...) -- not one is a JSON key, a URL parameter or a control. `sortBy` / `sortOrder` as a payload key or query param: **0**. `recentlyFollowed`: **0**. `followedByViewer`: **0**. `paginationToken` is present but its value is **null**. |
| H4 recency of follow | **INFERRED BY ELIMINATION -- NOT MEASURED** | it is what remains after H1, H2, H3 and H5 are killed. Nothing in any capture measures it. The model HAS the field -- `"followedAt"` occurs exactly **once**, and it is a SCHEMA TYPE NODE (`"followedAt":{"type":"com.linkedin.voyager.dash.deco.common.text.TextViewModel"}`), never an instance value -- so this page did not request follow dates and none are present to check. |

**The order is decided by the server; the client does not sort.** This is measured,
not assumed: the embedded payload's `items` array (length 10) is in EXACTLY the DOM
order of the first 10 rendered rows -- same sequence, same set -- in BOTH raw
captures. Whatever the API returns is rendered verbatim. That closes off the
possibility that a client-side comparator is doing something the DOM hides.

Supporting structural fact: this list is served by the SEARCH stack, not by a
dedicated following endpoint. Every row carries
`data-view-name="search-entity-result-universal-template"`, and the payload's
metadata record is `com.linkedin.voyager.dash.search.SearchClusterCollectionMetadata`
(`totalResultCount` 58, `queryType` null, `primaryResultType` null,
`paginationToken` null), delivered through `voyagerSearchDashClusters`. A filtered
search result with no keyword and no stated sort has whatever default ordering the
search backend applies -- which is exactly why elimination cannot name it.

### 9.2 Pre-hydration versus hydrated, and cross-capture

| check | result |
|---|---|
| pre-10 ids are an exact PREFIX of the hyd-20 ids, same order | **YES** -- in BOTH the sanitised fixture and the raw capture |
| positions of the pre-10 inside the hyd-20 | `[0,1,2,3,4,5,6,7,8,9]` -- 0..9 in order, both captures |
| display names agree at every shared index | **YES**, both captures |
| does the pre-hydration payload carry MORE than 20 records? | **NO. It carries 10.** `com.linkedin.restli.common.CollectionMetadata` = `{count: 10, start: 0, total: 58}`. The `items` array is length 10. |
| is the rendered 20 a prefix of the payload order, or a re-sort of it? | **A PREFIX, extended.** The 10 payload records render as rows 1-10 in payload order; rows 11-20 came from a SECOND fetch whose payload is NOT in the captured HTML (only one paging block exists, and it is `start: 0`). |
| RAW manage-pages-hyd vs RAW network-manager-company-hyd | **IDENTICAL id sequence in document order**, identical length, identical set. Captured about four minutes apart, so the ordering is stable at least over minutes. |
| RAW search-followed-company-hyd | lists **no followed companies at all** -- 0 T1 controls; it is a job-search page whose only company id is the posting's employer. It does not bear on the ordering. |

So hydration APPENDS a page; it does not re-sort. That is a useful stability
property on its own: a row's position does not move when the second page arrives.

### 9.3 Second question -- is anything past row 20 reachable?

Every search term run against all five captures. The two SANITISED fixtures scored
**0 on every term** except one "show more" (which belongs to a job card, not the
list). Counts below are for the raw hydrated Manage Pages capture; the raw
pre-hydration and network-manager captures gave identical counts.

| search term | hits | what they actually are |
|---|---|---|
| `start=` (as `?start=`, `&start=`, `"start":`) | 15 | ALL are `"paging":{"count":N,"start":0,"links":[]}` blocks or `"start":{"type":"int"}` schema field definitions. None is a URL parameter. |
| `count=` | 13 | same -- paging blocks, schema definitions, and unrelated `BadgingItemCount` records |
| `page=` | 1 | `aria-current="page"` on a nav link |
| `offset` | 4 | CSS class names (`global-alert-offset-top`) |
| `paginationToken` | 3 | one INSTANCE with value **null**, two schema definitions |
| `hasMore` / `moreAvailable` / `hasNextPage` | **0** | -- |
| `aria-sort` | **0** | -- |
| `IntersectionObserver` | **0** | -- |
| `data-*` pagination / scroll / infinite attributes | **0** | -- |
| "see all" / "show all" / "view all" | **0** | -- |
| "show more" / "load more" / "see more" | 1 (hydrated only) | on a job card, not on the followed list |
| "next page" / "View next" | **0** | -- |
| URLs anywhere in the document carrying `start=`, `count=`, `page=` or `offset=` as a QUERY PARAMETER | **0** | of all distinct absolute URLs in a 1.5 MB document |

**There is no url-addressable way, no rendered affordance, no sentinel element and no
observer.** Combined with section 4's zero pagination controls, the absence is now a
measurement across thirteen distinct search terms, not an impression.

**One affordance does exist, and it is not on the page.** The payload states a
Rest.li paged-collection contract: `CollectionMetadata {count: 10, start: 0,
total: 58}`, served by `voyagerSearchDashClusters`. That is the standard `start` /
`count` pagination contract, so rows past 20 ARE reachable at the API level. It is
NOT a path this server can take as built: it drives a signed-in browser and reads the
DOM, it does not call the voyager API, and adding that would be a new capability with
its own scope question -- not a detail of this wave. Reporting it as an affordance
that exists, not as a route that is available.

### 9.4 One measurement that looks like evidence and is not

The single company the job-probe captures are about sits at **position 10 of the 20**
rendered Manage Pages rows -- inside the window, and exactly at the boundary of the
first API page. I am reporting the number because it was asked for implicitly by the
reachability question, and then declining to read anything into it: the probe session
that chose that company almost certainly chose it BY reading this same list, so its
position is a selection artefact of how the capture was made, not a fact about how
LinkedIn orders follows. It is not evidence for recency ordering in either direction.

### 9.5 Verdict, and why it does not unblock `follow_company`

H1, H2, H3 and H5 are all refuted with counts. **H4, recency of follow, survives ONLY
by elimination and is labelled INFERRED-BY-ELIMINATION, not measured.** And
elimination has a hole that is fatal for the decision this was meant to make: **it
gives no DIRECTION.** Both readings survive every measurement in this file equally:

* **newest-first (descending)** -- a newly followed company lands at position 1, is
  inside the rendered window immediately, and stays there until roughly 20 further
  follows displace it. Follow would be safe to enable.
* **oldest-first (ascending)** -- a newly followed company lands at position 58, is
  outside the rendered window from the instant it is created, and can never be
  reached in one page load. Follow must stay blocked.

Nothing in fifteen captures distinguishes those two. **This census therefore cannot
unblock `follow_company`, and I will not manufacture a direction to let it.**

**What would settle it, without performing a follow from this server.** The direction
is a one-observation question, and the server already owns the instrument:
`linkedin_followed_companies` reads this exact surface. If the operator follows ONE
company by hand in his own browser, a single subsequent call to that existing
read tool answers it outright -- the new company's POSITION is the whole experiment.
Position 1 means newest-first and follow can be unblocked; absent from the rendered
rows means oldest-first and it cannot. That is one manual click plus one existing
read, no new write, no new capability, and it converts an inference into a
measurement. A cheaper variant with no click at all: store today's 20-row snapshot
and re-read on a later day, then diff -- but that only pays off if the followed set
happens to change on its own, so the manual follow is the reliable version.

**A bound that survives even the good case.** If the order is newest-first, a new
follow is reachable, but reachability is TIME-BOUNDED, not permanent: it decays as
further follows push the row past the twentieth. An unfollow that works only inside a
recency window is not a general undo, and if follow is unblocked on that basis the
tool description has to say so rather than imply a symmetric pair. The 20-of-58
ceiling from section 4 is unchanged for every company already followed: roughly two
thirds of them remain unreachable in one page load regardless of which direction the
sort turns out to be.
