SLICE: N 53 follower-chain audit -- occurrence-vs-presence check against the
N 54 defect class

Wave `what-is-reachable-now`. Read-only, entirely offline: no browser opened,
no Chrome started, no LinkedIn session touched. Everything below is source
reading, fixture inspection, and the committed test suite, plus one throwaway
offline probe script (headless Chromium driven over committed fixture HTML
via `page.set_content`, the same pattern `tests/test_company_about_card.py`
already uses -- not a navigation to any live page). Nothing tracked was
modified. Nothing was committed.

---

## 1. THE ROW, QUOTED

`_audit/_census/network.md`, line 400, verbatim (re-confirmed with a direct
`sed -n '400p'`, not just grep, so this is byte-exact):

    | 53 | View a Page's follower count | R | GAP | ~~No `/company/`~~ **THE
    RECORDED BLOCKER IS FALSE TWICE OVER, AND THE ROW IS SERVED TODAY. STATE
    DELIBERATELY UNCHANGED.** (1) `/company/<slug>/` HAS been on the read
    allowlist since 2026-09-20 -- `readonly.is_read_url` returns True for it,
    re-measured 2026-09-21. (2) **The row never needed that address.**
    `linkedin_job_detail` already returns the count:
    `dom.read_company_about_card` -> `shape.company_about_card` ->
    `followers`, parsed by `shape._ABOUT_FOLLOWERS`, published under
    `company_about`. No company Page is opened; the card renders on
    `/jobs/view/<id>`, admitted since the first commit.
    `tests/test_company_about_card.py` asserts an integer follower count and
    asserts it is `None` in BOTH un-hydrated states, so an unhydrated card
    cannot read as "no followers". `_audit/2026-09-20-company-page-built.md`
    found the same thing and filed it "SHIPPED, pre-existing" -- **and the
    row was left carrying the refuted blocker, which is why the correction is
    written here rather than in a document.** WHAT STILL STANDS BETWEEN THIS
    AND A BANK, stated so nobody banks it on this cell: no committed record
    shows `followers` POPULATED in a live fire. The 2026-09-19 fire that
    populated `company_about` is cited on `N 101` for `on_linkedin`, not for
    this key. That is one re-read of an existing artifact, not a build. See
    `_audit/2026-09-21-the-read-triage.md` |

Fields, read off the table structure: id `53`; capability text `View a
Page's follower count`; direction `R` (read); **state column literally reads
`GAP`** -- the surrounding prose argues the blocker is refuted and the
capability is built and tested, but the table's own state cell has not moved
off `GAP`, and this slice does not move it. That distinction (argued-served
vs. state-cell-still-GAP) is exactly the thing to hand back precisely rather
than collapse.

This is a materially different row from `N 54` ("View how many of your
connections follow a Page", `COVERED-CANNOT-DELIVER`, reader `company_root.py`
+ `dom.COUNT_LINES_JS`). `N 53` reads an aggregate stat off a job posting's
own About-the-company card; `N 54` reads a per-connection attribution off a
company Page root. Different capability, different reader, different module.

---

## 2. THE CHAIN, VERIFIED IN SOURCE

Followed hop by hop in `linkedin_server/`, not accepted relayed:

1. **`linkedin_server/server.py:4491`** -- `async def
   linkedin_job_detail(job_id: str) -> dict[str, Any]:`, decorated
   `@mcp.tool()` immediately above with no intervening wrapper.

2. **`linkedin_server/server.py:4878`** -- inside that function's body (the
   nearest enclosing `def`/`async def` above line 4878 is confirmed to be
   line 4491; no other function definition sits between them):

        about = await dom.read_company_about_card(page)

3. **`linkedin_server/server.py:4879-4880`**:

        out["company_about"] = shape.company_about_card(
            about, company=identity.get("company")
        )

4. **`linkedin_server/dom.py:979`** -- `async def
   read_company_about_card(page: Any) -> dict[str, Any]:` returns
   `container`, `sdui`, `lines`, `hrefs`, `hrefs_error`, `error`. This is
   where `about` (step 2) comes from.

5. **`linkedin_server/shape.py:3817`** -- `def
   company_about_card(observation, *, company) -> dict[str, Any]:` is where
   `about` is turned into `followers` (and `industry`, `size_band`,
   `on_linkedin`, `follow_state`, etc). This is where `out["company_about"]`
   (step 3) comes from.

6. **`linkedin_server/shape.py:3758`** -- `_ABOUT_FOLLOWERS =
   re.compile(r"^([\d,N]+)\s+followers$", re.I)` is the pattern
   `company_about_card` matches lines against (applied at
   `shape.py:3964`, `match = _ABOUT_FOLLOWERS.match(line)`).

7. **`linkedin_server/server.py:4906`** -- `return out`, the last statement
   of the function's `try` block. Nothing after step 3 touches
   `out["company_about"]` again (the two statements after it set
   `company_page` and `pages_loaded`/`source_url`, unrelated keys), and
   `return out` is the function's only non-error return. `except Exception as
   exc: return _error(exc)` is the only other path out.

8. No sanitiser or generic response wrapper sits between `return out` and the
   MCP transport: `server.py` has no `_SANITISERS`-style construct at all
   (`grep -n "_SANITISERS" linkedin_server/server.py` -- zero hits; that
   mechanism, referenced in a different memory, lives in a different tool's
   module, not here), and `@mcp.tool()` decorates `linkedin_job_detail`
   directly with nothing between the decorator and the `async def`.

**VERDICT ON THE CHAIN: CONFIRMED, ACCURATE, NOT REFUTED.** The triage
document's chain (`linkedin_job_detail -> dom.read_company_about_card ->
shape.company_about_card -> followers`, published under `company_about`) is
exactly what the source shows, and `followers` reaches
`linkedin_job_detail`'s published envelope unmodified once
`shape.company_about_card` sets it.

---

## 3. THE OCCURRENCE-VS-PRESENCE AUDIT

This is the part the brief asked to be hunted hardest, because `N 54` looked
clean (six distinct values, textbook discrimination) and was still wrong for
two compounding reasons: an off-by-one from matching a phrase that was a
SUFFIX of a longer sentence, and that phrase recurring 2-8 times per page
because presence, not occurrence, was tested. Point by point, against
`shape._ABOUT_FOLLOWERS` and `dom.read_company_about_card`:

**Does it test presence of a phrase, or count occurrences?**
Neither, in the sense that broke `N 54`. `dom.read_company_about_card`
first turns the container's rendered text into a LIST OF LINES
(`text.splitlines()`, each `.strip()`-ed, blanks dropped -- `dom.py`, inside
`read_company_about_card`, just after the `inner_text` read). `
shape.company_about_card` then walks that list once
(`shape.py:3960-3966`) and, for each line, tries a FULL-LINE match; the
first line that matches wins (`if out["followers"] is None: ... continue`).
Because the pattern is anchored on both ends (`^...$`) and applied with
`.match()` on a single already-split line, there is no "phrase found inside
a longer string" case at all -- a line either IS exactly `"<count>
followers"` or the whole line fails to match and contributes nothing. There
is no partial-credit, no suffix credit.

**Is the match anchored, or could it match as a suffix the way `N 54`'s
did?** Anchored, both ends, per line: `^([\d,N]+)\s+followers$`. `N 54`'s
defect came from matching `"connections follow this page"` as a SUFFIX of
LinkedIn's real, longer line `"<entity> & n other connections follow this
page"` (a construction that names an entity and then counts OTHERS). That
shape cannot silently match `_ABOUT_FOLLOWERS`: any leading entity name,
`"&"`, or `"other"` token before the digits, or any trailing text after
`"followers"`, breaks the match outright (returns no match, not a wrong
number). This is the correct failure direction -- loud absence over silent
wrong number -- and it is a structural property of full-line anchoring, not
a promise about wording.

**Is the digit run taken from before or after the phrase, and could an
"& n other" construction sit between them?** The digit run (`group(1)`) is
captured immediately BEFORE the literal word `"followers"`, separated only
by `\s+` -- one whitespace run, nothing else permitted between them by the
pattern. There is no slot for an `"& n other"`-style infix; if LinkedIn's
real markup inserted one, the line would fail to match `_ABOUT_FOLLOWERS`
entirely (see the fixture evidence below for what the real markup actually
does).

**Is the reader scoped to one card/element, or does it run over the whole
document?** Scoped to ONE element. `dom.read_company_about_card` selects
`page.locator(ABOUT_COMPANY_CONTAINER).first` (`dom.py:960`,
`ABOUT_COMPANY_CONTAINER = 'div[componentkey^="JobDetails_AboutTheCompany"]'`)
and reads `container.inner_text(...)` off that ONE located element
(`dom.py:1046`) -- never the page, never a wider region. `N 54`'s own row
text says its underlying construction ("connections follow this page")
recurs 2-8 times per Page because a Page root draws that line once per
RECOMMENDED organisation as well as for the subject -- i.e. the hazard there
comes from reading over a region wide enough to contain OTHER entities'
cards. The About-the-company card, by contrast, is a single company's own
section on a JOB POSTING (not a Page root with a recommendations rail), and
nothing in `dom.py`'s own documentation of this card's contents (header,
name, follower line, Follow control, industry/size/on_linkedin meta row,
description, "Key areas of focus", interest control, "Show more") describes
any construct that repeats per-other-entity the way a recommendations rail
does. I did not independently re-audit `company_root.py` / `COUNT_LINES_JS`
myself (out of this slice's scope; the comparison above is drawn from the
census's own `N 54` text plus `dom.py`'s comments on the `COUNT_LINES_JS`
constant, not independently re-verified against `company_root.py`), so this
paragraph is a documented CONTRAST, not a re-audit of the other row.

**Does it use `textContent`?** No. `dom.read_company_about_card` reads
`container.inner_text(timeout=ELEMENT_READ_TIMEOUT_MS)` (`dom.py:1046`) --
Playwright's own rendered-text API, not `textContent`. This matters because
this repository documents, IN ITS OWN COMMENTS, the exact hazard the brief
asked about: `dom.py` around line 9799-9807 (documenting `COUNT_LINES_JS`,
defined at `dom.py:9825`) says LinkedIn "draws the same line twice on a
card: an `aria-hidden` visible span that is name-free, and a screen-reader
span that carries a person's name. `textContent` is unconditional and picks
up both" -- and names `CARD_HIDDEN_SELECTOR` as the purpose-built defense,
wired specifically into that walk-based script. `COUNT_LINES_JS` is the
script behind `company_root.py`, i.e. the `N 33`/`N 54` reader (confirmed by
the census's own `N 33` row: "ARTIFACTS: `linkedin_server/company_root.py`,
`dom.COUNT_LINES_JS` + `dom.read_count_lines`"). `read_company_about_card`
is a different, earlier function (`dom.py:979`) that injects no script at
all for its text read -- its own docstring says so twice ("No script is
injected, nothing is evaluated, no control is pressed, and no page is
loaded"). So the specific documented textContent/duplicate-name hazard is
this repository's own diagnosis of a DIFFERENT reader's risk, not this one's.
I cannot rule out, from source alone, some other accessibility-duplication
technique against `inner_text` specifically (a browser's exact
"rendered text" boundary for an off-screen-but-not-`display:none` span is a
genuine gray area I have not tested against a live DOM) -- but the named,
documented hazard in this codebase is textContent-specific and tied to the
other reader.

**Does any integer coercion call `int()` unsafely, and is `coerce.as_int`
used?** `shape._about_int` (`shape.py:3811`) is the only int coercion on
this path:

    def _about_int(raw: str) -> Optional[int]:
        digits = raw.replace(",", "").strip()
        return int(digits) if digits.isdigit() else None

`int(digits)` is called ONLY after `digits.isdigit()` has already returned
True, so it cannot raise on this path -- there is no code shape here where
`int()` receives a value it could refuse. `coerce.as_int` (`coerce.py:75`)
is NOT used on this path, and correctly so: `as_int`'s own docstring says
"IT NEVER RAISES AND NEVER QUOTES ITS INPUT" and its body is `if
isinstance(value, int): return value` else `None` -- it is a TYPE gate for a
value that is already an int, not a string parser. Handed the string
`"5,288,656"` it would return `None`, not `5288656`; it is structurally the
wrong tool for turning scraped text into a number, and this module correctly
rolled its own gated parser instead of reaching for it. Confirmed by a
committed test: `test_a_sanitised_follower_count_is_null_and_never_zero`
(`tests/test_company_about_card.py:256-268`) feeds `"NNN,NNN followers"`
through the real function and asserts `followers is None` and `"followers"
in why` -- not a raised exception, not a wrong zero.

**EMPIRICAL OCCURRENCE COUNT, taken from the system rather than argued from
the regex alone.** Rather than trust the anchoring argument on its own, I
drove the REAL `dom.read_company_about_card` (same technique
`tests/test_company_about_card.py`'s own `_read()` helper uses: local
headless Chromium, `page.set_content()` from the committed fixture, no
navigation, no live session) over all five tracked `job_detail*` fixtures and
counted how many of the returned lines match `shape._ABOUT_FOLLOWERS`:

    fixture                                lines   matches
    job_detail.html                           25         1
    job_detail_hydrated.html                  25         1
    job_detail_following.html                  0         0   (unhydrated, no text at all)
    job_detail_following_hydrated.html        14         1
    job_detail_shell.html                      0         0   (no container)

Never zero when the card is hydrated and named; never two or more, on any of
the five. The one match per hydrated fixture, with digits redacted to `D`
and structure preserved, reads `D,DDD,DDD followers` (twice) and `NNN,NNN
followers` (once, the deliberately-sanitised fixture) -- a clean, isolated
`"<count> followers"` shape every time, never an entity name or an `"&
other"` construction anywhere near it. This is the direct analogue of the
check that would have caught `N 54` before it shipped (occurrence count, not
presence), run against every tracked sample this row has, and it comes back
1-or-0 on all five, never the 2-8 pattern that convicted `N 54`.

**VERDICT: NO -- `N 53`'s reader is not vulnerable to the `N 54` defect
class**, for the specific mechanism that broke `N 54` (a phrase matching as
a suffix of a longer, entity-naming sentence, recurring across multiple
unrelated entities because the read was scoped wider than one card). That
is a source-level finding (full-line anchoring, single-container scoping, no
`textContent`, a gated int parser) corroborated by an empirical occurrence
count of 1-or-0 across every tracked fixture and hydration state.

This is a narrower claim than "proven, bank it": see section 5 for the
different risk axis (markup drift since capture) that this verdict does not
and cannot close offline.

---

## 4. WHAT THE COMMITTED FIXTURES AND TESTS ALREADY PROVE

`tests/test_company_about_card.py`, 483 lines, 26 tests. Ran it sharded:

    D:\...\linkedin\venv\Scripts\python.exe -m pytest tests/test_company_about_card.py -q -n auto --dist loadfile
    26 passed in 8.87s

**Fixture provenance.** `tests/fixtures/` keeps a `synthetic/` subdirectory
for hand-built markup; `job_detail.html`, `job_detail_hydrated.html`,
`job_detail_following.html`, `job_detail_following_hydrated.html` and
`job_detail_shell.html` are NOT in it. Their size (39-76 KB each) and
content (hashed/obfuscated class names, real `componentkey` and
`data-sdui-component` attribute values matching exactly what `dom.py`'s
comments describe finding by inspection) are consistent with sanitised
captures of real rendered LinkedIn markup, not hand-authored mockups. The
employer name appearing in these fixtures reads as a sanitisation
placeholder (the test file's own constant is literally named `EMPLOYER` and
is reused as the expected-attribution value); per this slice's hard rules I
am not quoting it here and refer to it as `<entity>` (the `job_detail*`
group) and `<entity-2>` (the `job_detail_following*` group, a different
placeholder name).

**What the tests assert about a POPULATED card.** Two layers:
- A pure unit layer calls `shape.company_about_card()` directly against a
  hand-built `observed(CARD)` dict (`CARD` is explicitly documented as "the
  shape `dom.read_company_about_card` returned from `job_detail_hydrated.html`,
  with the description shortened" -- i.e. copied from the real fixture's
  output, not invented). `test_a_whole_card_reads_all_four_fields` asserts
  `state == "read"` and `followers == 5288656`.
- A browser-driven layer (`test_the_reader_finds_the_whole_card_on_a_filled_render`,
  parametrized over `job_detail.html` and `job_detail_hydrated.html`) drives
  the REAL `dom.read_company_about_card` over the REAL committed fixture in a
  local headless Chromium and asserts `verdict["followers"] == 5288656`,
  `size_band == "51-200"`, `on_linkedin == 304`. This is the strongest
  offline evidence available: production code, real captured markup, no
  hand-built intermediate dict.

**What the tests assert about UNHYDRATED / absent states.**
`test_the_skeleton_render_is_unhydrated_on_the_real_markup` (fixture
`job_detail_following.html`, container present, `sdui` False, zero lines)
asserts `state == "unhydrated"`. `test_the_shell_render_has_no_card_at_all`
(fixture `job_detail_shell.html`, no container) asserts `state == "absent"`.
Both assert (via the unit-level tests alongside them)
`followers is None` in these states -- confirmed also by the empirical
occurrence probe in section 3 (0 matching lines on both). So an unhydrated or
absent card cannot be misread as "this employer has zero followers": the
state field distinguishes "not filled in" from "filled in and empty", which
is exactly the property this module's own docstrings say it exists to
preserve.

**What the tests assert about the SANITISED-follower fixture.**
`test_the_followed_employers_card_reads_its_follow_state` (fixture
`job_detail_following_hydrated.html`) asserts `follow_state == "Following"`,
`industry`, `size_band == "10001+"` -- i.e. a fully hydrated, fully named
card -- AND `followers is None`, `state == "partial"`, because that
fixture's follower digits were sanitised to `"NNN,NNN"` at commit time. This
is the same card SHAPE as `<entity>`'s (confirmed in section 3: one matching
line, same `"<count> followers"` construction) with a different real
employer's real digits removed, which is corroborating evidence that the
WORDING/STRUCTURE is consistent across at least two distinct real capture
sessions, even though only one of them still carries a real integer.

**Whether any committed record shows `followers` POPULATED FROM A LIVE
FIRE.** This is the one thing I could NOT find, and it matches what both the
census row and the triage document already say. Specifically:

- The original build wave's own audit, `_audit/2026-09-05-company-about-card.md`,
  section "8. WHAT I DID NOT DO", states outright: **"The About card has not
  been read on a LIVE posting. Every reading here is off committed, sanitised
  fixtures plus one untracked raw capture. The parser is therefore verified
  against markup as of the day those were taken, not against today's."** The
  "one untracked raw capture" is, by definition, not in this tree -- I cannot
  inspect it from here.
- `_audit/2026-09-20-company-page-built.md` states at its top: "No write was
  fired. No browser session was opened. No LinkedIn page was loaded. Every
  measurement below is offline" -- so its "SHIPPED, pre-existing" verdict for
  `N 53` was also a source/fixture read, not a fresh fire.
- The one genuine LIVE fire I can find any trace of is referenced from the
  `N 101` census row (`_audit/_census/network.md` line 471): **"The tool
  fired live 2026-09-19 on two postings with `company_about` populated."**
  This is `linkedin_job_detail` actually being called against real,
  currently-loaded LinkedIn postings. But `followers` and `on_linkedin` are
  parsed by two INDEPENDENT code paths inside `shape.company_about_card`
  (`followers` by the per-line loop at `shape.py:3960-3966`; `on_linkedin` by
  a separate `band_at`/`row_is_whole` structural check at `shape.py:3986` on)
  -- one succeeding does not logically guarantee the other did on that same
  fire. I searched the whole `_audit/` tree (`grep -rl "on_linkedin"`,
  `grep -rl "followers"`) and found no dated 2026-09-19 file and no raw
  JSON/output artifact recording that fire's `company_about` object; only the
  two narrative sentences above (on the `N 101` row and in
  `_audit/2026-09-21-the-read-triage.md` section 3.1) survive in the
  committed tree. I also checked every `_audit/2026-09-21-*.md` file for a
  mention of `N 53` or a follower-count fire more recent than the triage
  document (`the-fires-and-the-controls.md`, `the-fourteen-fired.md`,
  `the-three-readers.md`, `the-compound-rows.md`, `the-open-queue.md`,
  `what-was-ruled.md`) -- none mention this row; the only near-miss is
  `the-compound-rows.md` line 162, which is about a DIFFERENT capability
  ("Own follower count", the user's own profile, not a Page's).

So: the census row's claim that no committed record shows `followers`
specifically populated from a live fire is accurate, and it is a narrower,
more precise gap than "never fired live" -- the tool WAS fired live once on
2026-09-19, but nobody recorded (or has since re-derived) whether the
`followers` field of that specific response came back non-null.

---

## 5. WHAT WOULD DISCRIMINATE

Given that a count alone is not evidence (the `N 54` lesson) and that a
reading that cannot tell this row from its neighbours is not evidence
either, a live firing that actually discriminates `N 53` would need to
report, at minimum:

1. **The real MCP tool, not the offline functions.** Call
   `linkedin_job_detail(job_id)` on a currently-loaded, real posting through
   the live server (not `dom`/`shape` called directly), and read
   `company_about` out of the ACTUAL RETURNED ENVELOPE -- closing the exact
   "published envelope" question this slice could only confirm at the source
   level.

2. **`company_about.state` and `company_about.followers` together, not
   `followers` alone.** `state == "read"` (all four fields parsed) is
   stronger evidence than `followers` merely being non-null under
   `state == "partial"`, because `partial` with `followers` present but
   something else missing would itself be informative about which part of
   the row shape held and which did not.

3. **The occurrence count, not just the final integer** -- the same
   instrument used in section 3, run against the LIVE page's own returned
   `lines` (or logged from inside `read_company_about_card` for this one
   call): how many lines match `_ABOUT_FOLLOWERS`. It must be exactly 1.
   Zero means the card did not hydrate in time or the wording changed; two
   or more would be the `N 54` collision shape reappearing and must not be
   silently resolved by "first match wins" without being reported as a
   finding in its own right.

4. **More than one employer, at more than one follower-count magnitude.**
   The strongest committed evidence right now (section 4) ultimately
   traces to ONE real integer (`5288656`, on one employer, captured once and
   reused across a pre-hydration and a post-hydration fixture of the same
   session) plus ONE corroborating-but-redacted second employer confirming
   only the wording, not a second real number. A live fire against 2-3
   distinct real postings for different employers, ideally spanning small
   (3-4 digit) and large follower counts, would catch a magnitude-dependent
   wording change (an abbreviated form, a singular "1 follower", a "be the
   first to follow" zero-state) that a single large-number sample cannot
   surface. `N 54`'s own row explicitly refused to accept "2K" as a value
   rather than guess at it; nothing here has yet tested whether LinkedIn ever
   draws an abbreviated follower count on this specific card.

5. **The attribution check on live markup, not just on the fixture.**
   `company_about_card`'s refusal-on-mismatch (the `unnamed` state) depends
   on `identity.get("company")` -- `dom.read_job_identity`'s output --
   agreeing with the About card's own opening name. That upstream reader is
   outside this slice's scope and was not audited here; a live fire is also
   the first real test that the two readers agree on a page neither fixture
   author controlled.

6. **A committed record of the result**, even redacted (state, the
   occurrence count, the four field values with the employer name stripped)
   -- so the next reader inherits a fact rather than a sentence pointing at
   an uncommitted one. That is the specific gap both the census row and
   `_audit/2026-09-21-the-read-triage.md` name, and it is the cheapest of
   the six items here to close once a live slot is available, since the
   parser itself is not what section 3 found wanting.

---

## SUMMARY FOR THE WAVE LEAD

- Row quoted verbatim in section 1. State column is literally `GAP`; prose
  argues served; unchanged by this slice.
- Chain CONFIRMED in source, hop by hop, section 2: `followers` does reach
  `linkedin_job_detail`'s published envelope under `company_about`, with no
  sanitiser or wrapper in between.
- Occurrence-vs-presence verdict: **NO**, not vulnerable to the `N 54` defect
  class -- full-line anchored match (not suffix), single-container scoped
  (not page-wide), no `textContent` (uses `inner_text`, and the repository's
  own documented textContent/duplicate-name hazard is tied by name to the
  OTHER reader, `COUNT_LINES_JS`/`company_root.py`), a gated `int()` that
  cannot raise, and an empirical 1-or-0 occurrence count across all five
  tracked fixtures and hydration states (never 2+, never the 2-8 collision
  pattern that convicted `N 54`).
- This verdict is about the DEFECT CLASS specifically, not a "bank it"
  recommendation: the thing actually standing between this row and a bank is
  a different axis (markup drift since an unknown-but-past capture date,
  and only one real underlying integer sample) that offline evidence cannot
  close. Section 5 states exactly what a live fire would need to report to
  close it.
- Tests: 26/26 passed, sharded, offline, against the real reader over
  committed fixtures.
