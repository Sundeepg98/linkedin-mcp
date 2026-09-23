# The profile-views recapture: one generation, not two, and a defect that was diagnosed backwards

Wave `premium4-analyticsshape`, 2026-09-20, main checkout, master `771b323`.
A LIVE AUTHENTICATED SESSION. Read-only throughout: nothing was connected,
messaged, applied to, followed, posted or pressed. No allowlist change is made
or proposed. The one address opened was already admitted.

---

## 0. THE HONEST LEDGER, FIRST

    rows banked out of GAP                 0    and that is the correct number
    rows inflated                          0
    census rows EDITED                     0    N 136 was already right
    prior HYPOTHESES refuted               2    "two generations", "scope artifact"
    prior AUDIT claims corrected           1    live-capture.md s5, corrected in place
    prior readings reproduced              1    the live one, to the character
    live samples, shipped reader           4    all four identical
    live samples, independent probe        3    all three identical
    lifecycle polls across a full load   155    peak data-view-name = 0
    defects found in MY OWN work           2    section 8, both were zeros that were parse misses
    limits named and NOT discharged        1    the unpressed "Show more analytics"
    questions left open                    2    section 9
    raw captures committed                 0
    instruments registered                 1    a method, section 33; section 7 says why not a script

**THE QUESTION WAS WHETHER TWO DOM GENERATIONS OF THIS PAGE EXIST. THEY DO
NOT.** The evidence for a second generation is a single committed fixture, and
that fixture is the other committed fixture with attributes added by hand --
proven byte-identical, section 3. Every live observation ever recorded of this
page, across three separate dates and two instruments, agrees.

**AND THE DEFECT THIS WAVE WAS SENT TO CONFIRM IS NOT A DEFECT.** The scope was
already fixed before the reading that diagnosed it, the fix changed nothing,
and it could not have: section 4.

---

## 1. THE LANDING URL, WHICH IS THE THING THAT GETS ASSUMED

Recorded on all four samples, never inferred from "the load succeeded":

    requested   https://www.linkedin.com/analytics/profile-views/
    landed      https://www.linkedin.com/analytics/profile-views/
    pages_loaded  1        (4 of 4 samples)

**NO REDIRECT.** Three admitted addresses were measured serving redirects
elsewhere today; this is not one of them. `linkedin_who_viewed_me` carries a
second address, `/me/profile-views/`, which it loads only when the first
returns no rows. It never fired: `pages_loaded` was 1 on every sample, so the
classic address is untested here and this document claims nothing about it.

---

## 2. THE MEASUREMENTS, WITH THEIR DENOMINATORS

### 2a. The shipped reader -- 4 samples, 13:50:38 / 13:53:39 / 13:54:33 / 14:03:39

Every field identical on all four. One row, because four identical rows is one
reading taken four times:

| field | value | note |
|---|---:|---|
| `count` | 10 | rows returned to the caller |
| `page_had` | **12** | rows the outer harvest found |
| `unparsed_rows` | 2 | 12 - 10, and the envelope says so itself |
| `capped` | false | limit was 100 |
| rows anonymous / named | 4 / 6 | |
| rows carrying a profile link | 6 | see section 8, defect 2 |
| rows carrying a recipient id | 4 | |
| `insights_error` | none | the reader did not fail |
| `main_present` | true | |
| `main_chars` | **1835** | |
| `viewer_rows` (in-JS) | **0** | |
| `view_names` | **[]** | |
| `view_name_counts` | {} | |
| `metrics_seen` | 2 | |
| headline | value 2 chars, label 15 chars | |
| delta | value 3 chars, label 16 chars | |
| trend | present, description 31 chars | |
| filters | **5**, label lengths [12, 19, 7, 32, 31] | |

### 2b. An independent instrument on the same DOM -- 3 samples

The shipped reader cannot tell "the attribute is absent" from "I looked in the
wrong box", because both come back as `[]`. So the same document was measured
by a second instrument that reports BOTH scopes. Counts and tag names only --
no text, no href values, no accessible names leave the page.

| field | S1 13:51:53 | S2 13:53:48 | S4 14:03:4x |
|---|---:|---:|---:|
| `main` elements | 1 | 1 | 1 |
| `main` innerText chars | 1835 | 1835 | 1835 |
| `body` innerText chars | 1998 | 1998 | 1998 |
| document outerHTML chars | 143554 | 143556 | 143547 |
| `main` outerHTML chars | 113337 | 113339 | 113336 |
| **`[data-view-name]` DOCUMENT-WIDE** | **0** | **0** | **0** |
| **`[data-view-name]` inside `main`** | **0** | **0** | **0** |
| distinct view-name values | {} | {} | {} |
| `a[href*="/in/"]` doc-wide / in `main` | 7 / 7 | 7 / 7 | 7 / 7 |
| distinct row containers | 7 | 7 | 7 |
| **row element type** | **div x7** | div x7 | div x7 |
| `li` doc-wide / in `main` | 8 / 0 | 8 / 0 | 8 / 0 |
| `article` doc-wide / in `main` | 0 / 0 | 0 / 0 | 0 / 0 |
| `p` doc-wide / in `main` | **61 / 61** | 61 / 61 | 61 / 61 |
| `label` doc-wide / in `main` | **5 / 5** | 5 / 5 | 5 / 5 |
| `section` / `img` / `button` | 2 / 10 / 23 | same | same |

The 7-to-9-character drift in the two HTML lengths is the only thing that
moved in thirteen minutes. It is worth keeping rather than rounding away: it
is the proof the page is live and re-rendering, so the stability of every
other row is a property of the page and not of a frozen tab.

### 2c. The row arithmetic reconciles exactly

`page_had: 12` has been read as a `data-view-name` count before. It is not one.
It is the link-anchored harvest, and it adds up:

    7   a[href*="/in/"]                         named viewers (measured, 2b)
    4   anonymous rows (search-results links)   measured by the reader, 2a
    1   the "N recruiters viewed your profile" row
    --
    12  = page_had, and 12 - 2 unparsed = 10 returned

---

## 3. THE TWO-GENERATIONS HYPOTHESIS IS REFUTED, AND THE REFUTATION IS ONE COMMAND

The repository holds two committed fixtures of this page. One carries 45
`data-view-name` attributes; the other carries none. That pair is the entire
evidential basis for "two DOM generations".

**THEY ARE ONE DOCUMENT.** Strip `data-view-name` from both and they are
byte-identical:

    profile_views_analytics.html            8963 bytes on disk
    profile_views_analytics_hydrated.html  10612 bytes on disk

    after removing every data-view-name attribute:
      plain     8945 chars   sha256 023cc963a5659cd7...
      hydrated  8945 chars   sha256 023cc963a5659cd7...
      IDENTICAL: True

    CONTROL, so that "identical" is a reading and not a no-op stripper:
      1667 chars removed from hydrated; data-view-name count 45 -> 0

Same placeholder people in the same order, same chart sentence, same headline
pair, same class hash on the root `section`. The `_hydrated` fixture is not a
capture of a second generation. It is the first fixture with the attribute
written in, so that the reader's attribute-anchored branch has something to
run against. Both are synthetic -- the people are invented and the employers
use `.example` domains.

**WHY THIS MATTERED.** `dom.py` explains the live page's behaviour by citing
"the committed capture" and its "45 data-view-name elements". That explanation
is built on the hand-authored variant, not on anything LinkedIn served.

Against that, every live observation ever recorded:

| when | what was observed | source |
|---|---|---|
| 2026-09-03 | "carried NO data-view-name attribute ANYWHERE" | `dom.py` comment |
| 2026-09-20 am | scoped reader saw 0 `data-view-name` | `2026-09-20-the-live-capture.md` s5 |
| 2026-09-20 pm | **0 doc-wide, 0 in `main`, 3 samples** | section 2b |
| 2026-09-20 pm | **0 at every instant of a full load, 155 polls** | section 5 |

**VERDICT: one live generation, which has never carried `data-view-name`, plus
one synthetic fixture variant that invented it.** The `<main>` difference
between fixture and live page is real but is not a generation difference
either: both fixtures are reduced captures, full of `<!--stripped-->` markers,
and the reducer kept the `section[aria-label="Primary content"]` subtree
without the `<main>` wrapper around it.

---

## 4. THE SCOPE DEFECT WAS FIXED BEFORE IT WAS DIAGNOSED, AND THE FIX CHANGED NOTHING

**CORRECTS:** `_audit/2026-09-20-the-live-capture.md` -- its section 5 rules the empty `view_names` a proven scope artifact and the reader "looking in the wrong box"; both halves are refuted below, because the scope fix had already landed when that reading was taken and `data-view-name` is absent document-wide anyway.

That section rules the empty `view_names` is "a proven scope artifact" and that
the reader is "looking in the wrong box". **Both halves are wrong, and each
fails for its own reason.**

**(1) The box was already the whole document.** The server's own
`stale_process` field reports what it loaded:

    loaded_commit  8b58dcb84e4b        process_started_at 2026-09-20T04:22:38Z
    disk_commit    771b323cdae5        stale: true (31 modules moved since)

and `353c04f` -- the commit that changed `const scope = main || document.body`
to `const scope = document.body` -- **is an ancestor of `8b58dcb`**
(`git merge-base --is-ancestor`, confirmed). So the live reading that diagnosed
a scope defect was taken through the document-scoped reader. The server is
genuinely stale against master, and on this one line it is not.

**(2) On this page the two scopes are the same scope.** Everything the reader
looks at is inside `main` already -- measured, section 2b:

    <p>     61 doc-wide, 61 in main      metrics come from these
    <label>  5 doc-wide,  5 in main      filters come from these
    /in/     7 doc-wide,  7 in main
    [data-view-name]  0 doc-wide, 0 in main

The only elements outside `main` are 8 `<li>` of page furniture, which the
reader never reads. **Widening the scope on this surface cannot change any
field the reader returns**, and the measurement confirms it did not: master's
fixed reader returns exactly the numbers the pre-fix reader returned.

**So `view_names: []` is a TRUE reading of the page.** The attribute is absent.
The reader is not blind here for the reason recorded -- but it *is* still
blind, for a different one, and section 6 turns on that distinction.

Corrected in place at the head of that document's section 5, so a reader who
starts from the claim finds the correction rather than only this file.

---

## 5. THE TEST NEITHER PRIOR READING COULD RUN

`dom.py` records that `data-view-name` may be "attached by the client AFTER
hydration or not at all". **A read taken at settle cannot tell "never
attached" from "attached, then replaced"** -- and every reading before this one,
including both of mine in section 2b, was taken at settle.

So one tab was polled ~3x/second through a complete server-driven navigation:
155 polls over 55 s, printing only on change.

    t+s    ready      dvn  main_chars  /in/    doc_len
     0.2   complete     0        1835     7     143554
     3.6   loading      0          -1     0      23413
     4.0   complete     0         151     0     539626
     5.2   complete     0        1404     7     112699
     5.8   complete     0        1555     7     125995
     7.1   complete     0        1835     7     143556
    --- 155 polls; PEAK data-view-name seen = 0

**THE CONTROL IS IN THE TABLE ITSELF.** The probe tracked `main` from absent
(-1) through 151, 1404, 1555 to 1835 chars, the document from 23 KB through a
539 KB peak down to 143 KB, and `/in/` anchors from 0 to 7. An instrument that
followed all of that and still printed 0 for `data-view-name` is reporting the
page, not failing to look. **A zero beside four columns that moved is a
reading.**

The attribute is absent at every instant of the lifecycle, not merely at
settle.

---

## 6. `N 136` -- THE RULING

**The row does not need banking. It is already banked, and it is right.**

`_audit/_census/network.md` row 136 -- *"See top locations, industries and
companies of your viewers (Premium)"* -- already reads **MEASURED-ABSENT**,
citing two independent sources from 2026-09-03 and 2026-09-05, and carries an
explicit REOPENER: *"a breakdown panel drawn under any name on that page."*
The live-capture wave did not change that row; it argued in its audit that the
row should be reopened because the instrument behind it was scope-blind.

**That argument is refuted (section 4), so the reopener is not tripped on those
grounds.** But refuting the argument is not the same as testing the row, and
`view_names` genuinely cannot see a panel here -- not because of scope, but
because the page carries no `data-view-name` at all. **This row has now been
ruled on twice by instruments that could not have seen the thing.** So it was
measured with one that can.

### 6a. A rendered-text and raw-source census, with live controls

Denominators: **1998 characters of rendered text, 143556 characters of source.**

    CONTROLS (words other instruments already proved present)
      needle       drawn   raw
      viewer           2    17
      profile          5    27
      chart            5   109
      filter           1    16
      recent           1     1
      CONTROL TOTAL DRAWN = 14  -> the probe can speak

    TARGETS
      location         0     0        <- not in the text, and not in the source
      top location     0     0
      country          0     0
      seniority        0     0
      job title        0     0
      school           0     0
      insight          0     0
      top compan       0     4
      region           0     3
      function         0     1
      compan           2    18
      industr          1     3
      city             1    64
      analytics        1     5

**The word "location" occurs zero times in 143,556 characters** -- not rendered,
not in the served source.

### 6b. The three non-zero targets are not panels, and structure proves it

`compan 2`, `industr 1` and `city 1` are exactly the kind of hit that would
reopen the row if read as a count. They were located structurally instead --
ancestor tag chains and ARIA roles only, no text emitted, lengths reported so
nothing quotable leaves the page:

| needle | own-text length | structural position | what it is |
|---|---:|---|---|
| `compan` | 7 | `label` inside `div[role=button]` | **the Company FILTER** |
| `compan` | 44 | `p` inside an `a` viewer row | a viewer's own headline |
| `industr` | 79 | `span<p` inside an `a` viewer row | a viewer's own headline |
| `city` | 21 | `span<p` inside an `a` viewer row | a substring inside a headline |
| `show more` / `analytics` | 19 | `span<span<button` | the Show more analytics button |
| `recent` | 11 | `button[tab]` in `div[role=tablist]` | the Most recent / Most relevant tabs |
| **`location`** | -- | **0 elements carry it** | -- |

Every non-zero target sits inside a viewer row or is a filter caption. **No
breakdown panel is drawn under any name.** The only non-row structures on the
surface are five filter labels, one tablist, and one Show more button.

### 6c. The ruling, and the limit it is bounded by

**`N 136` STAYS MEASURED-ABSENT. No census edit is required. The reopener filed
against it by the live-capture wave is refuted, and the row now has a third
independent source, taken for the first time by an instrument shown able to
speak on this page (14 control hits).**

**THE LIMIT, NAMED RATHER THAN BURIED.** This is the default render: default
filters, no scrolling, and **the `Show more analytics` button was NOT pressed**
-- it exists live (section 6b), and pressing it is an interaction this wave had
no ruling for. A breakdown panel that renders only behind that press would be
absent from every measurement above without being absent from the product.
What the raw-source zero does add: "location" is absent from the served
document as well as the rendered one, so a purely client-rendered panel would
have to bring its own label with it.

**That limit is the honest reopener, and it is narrower than the one on the row
today.** It is one press wide.

---

## 7. WHY NO NEW SCRIPT WAS COMMITTED

The four probes behind this document are one-shot measurement scripts holding a
hardcoded address literal. `tests/test_navigation_is_never_derived.py` sweeps
`scripts/*.py`, and `tests/test_staged_navigation_guard.py` is parametrised over
`["linkedin_server", "scripts"]`. Committing a probe with a URL literal into
`scripts/` is a plausible way to ship red for no gain.

So the durable artifact is the METHOD plus its measurement expression, recorded
in `_audit/INSTRUMENTS.md` section 33 and reproducible from it. Registered as a
method, with its receipt -- the precedent is section 29, which is also a method
rather than a file.

---

## 8. TWO DEFECTS IN MY OWN WORK, BOTH OF THEM ZEROS THAT WERE PARSE MISSES

Reported because this is the exact failure class the fleet has been counting
all day, and it caught me twice in one session.

**(1) I grepped the fixtures for `href="/in/` and reported 0 person links in
both.** The fixtures write the absolute form, `href="https://www.linkedin.com/in/..."`.
The correct count is **4 per fixture**. My zero measured my pattern, not the
document. Corrected before it reached any conclusion here; the fixture
anchor counts in section 3 are the corrected ones.

**(2) My first sampler counted rows carrying `url` / `profile_url` / `link` and
printed 0.** The row key is `profile`. The correct count is **6 of 10**. Had I
banked that zero it would have read as "no viewer row carries a profile link",
which is the opposite of the truth.

Neither zero reached a verdict. Both are the same defect: a zero from an
instrument that was never shown able to return non-zero. Section 5 and section
6a both carry explicit controls because of these two.

---

## 9. WHAT THIS WAVE DID NOT SETTLE

1. **The "24 rows" figure** attributed to the committed capture could not be
   reproduced from either fixture. Counting their anchors gives 4 person links
   + 12 `WHO_VIEWED_ME` search links + 2 recruiter-views links = 18, and the
   hydrated variant carries 11 `data-view-name="viewer-list-item"`. 24 is most
   likely a harvester count under `sibling_rows=True`, which doubles some rows
   -- **but that is a guess and is marked as one.** It does not affect any
   verdict here: the live page is what sections 2 and 5 measure.

2. **Two filters this repository has never documented.** The reader returns 5
   filter captions of lengths [12, 19, 7, 32, 31]. The first three lengths match
   the three captions `dom.py` documents exactly. **Two filters of 32 and 31
   characters are new since the fixture was taken**, and are deliberately not
   identified here -- this wave printed lengths, not labels. They are filters,
   not panels, so they do not touch `N 136`; they are worth one cheap read by
   whoever next holds a session, because an undocumented filter is a real
   surface change.

   **CORRECTED BY:** `_audit/2026-09-23-lane-l2-refused-presses.md` -- the captions of 32 and 31 characters are the two radio labels of a closed `<dialog>` form on this page, which the reader's every-`<label>` fallback collects; they are not filters, and no surface changed.

3. A raw-versus-drawn divergence persists on this surface, consistent with the
   law the live-capture wave established: `city` 1 drawn against 64 raw,
   `region` 0 drawn against 3 raw, `top compan` 0 drawn against 4 raw. Counting
   the source here would have manufactured three findings.

---

## 10. WHAT A FIXTURE OF THIS PAGE MUST NOW SAY

The wave that declined to build a reader off the existing capture was right to
decline, but not for the reason given -- the risk was never "one of two
generations". It is that **both committed fixtures are synthetic, neither has a
`<main>`, and one of them has an attribute the real page has never served.**

A fixture that unblocks that reader needs to be, and to say on its own first
line, that it is: one `<main>`, `main.innerText` ~1835 chars against a ~1998
char body, zero `data-view-name` anywhere, 12 harvestable rows of which 7 carry
`/in/` anchors and 4 are anonymous search links, rows as `div`, 61 `<p>` and 5
`<label>` all inside `main`, no `li` or `article` in `main`.

Those are the numbers in section 2 and they are now measured seven times over.
**The `_hydrated` variant should keep existing and should carry a first line
saying it is hand-authored**, because it is the only thing exercising the
attribute-anchored branch and nothing on the live page ever will.
