# LOAD A was taken. The emission is real, and one line of my own verdict overclaimed.

Date: 2026-09-05, 14:24. `SEARCH-APPEARANCES-SURFACE`, the reciprocal reading
named LOAD A by `_audit/2026-09-05-search-results-consent.md`.

**The page was opened. Twice. It served, it reports a non-zero number, and
that number is reported to him.**

---

## 0. THE SENTENCE THAT GOES FIRST

The consent brief's opening sentence was: *"I could not establish that opening
a people-search results page leaves the people it lists untouched, and nobody
in this repository ever has."*

**That is no longer true, and it resolves against the surface.** LinkedIn
records how often a member turns up in other people's results and reports the
count to that member. `D1` -- "a results load leaves no durable record on the
people listed" -- is **DEAD**, measured rather than argued.

---

## 1. WHAT WAS READ, AND HOW

`scripts/_probe_search_appearances_live.py`, attach mode on the shared Chrome
(`LINKEDIN_CDP_ATTACH=1`, port 9224). No profile lock taken. Two loads of
`https://www.linkedin.com/analytics/search-appearances/` and nothing else --
`/search/results/people/` was not opened, is still refused by the read
boundary, and this reading exists precisely so that it need not be.

Everything below came out of `dom.read_search_appearances`. No raw label, no
href and no accessible name crossed out of the page.

| | first | second |
|---|---|---|
| headline value | **108** | **108** |
| second metric | 13 | 13 |
| `anchors.person` | **5** | 5 |
| `anchors.company` | 0 | 0 |
| `anchors.total` | 18 | 18 |
| `main_chars` | 2005 | 2005 |
| `redirected` | False | False |
| authwall | no | no |

**TWO IDENTICAL READINGS, which is what makes these numbers worth anything.**
A surface read once has no baseline. Nothing moved between the loads, which
also answers the badge question the census key's own comment left open: **no
counter on this page was observably spent by loading it.**

The four labelled rows, read as `<label>` text and nothing else:

    Posts                      75.9%
    Search                     12%
    Network recommendations    11.1%
    Comments                   < 1%

---

## 2. WHAT IS SETTLED

**E1, VERIFIED-BY-INSTRUMENT. A search is recorded and reported back to the
person who was found.** 108, twice, on his own analytics page. Result-set
membership is a durable, member-visible event. The claim that a people-search
leaves the listed people untouched is refuted.

**E2, VERIFIED-BY-INSTRUMENT, and it is the sharper half. `Search` is a NAMED
DISCOVERY CHANNEL that LinkedIn attributes appearances to, at 12%.** This is
the finding the consent brief could not reach. It is not merely that "some
signal exists" -- LinkedIn separates Search from Posts, from Network
recommendations and from Comments, and tells the found member which channel
found them. So a search is not an anonymous read: it is an attributed one.

**Consequence for the 21 rows (19 reads).** The gate's Q2 -- emission -- is no
longer "no class, this is the hole". It is answered, and answered against the
surface. `R2`'s principle now reaches a people-search results page by
MEASUREMENT and not only by analogy: the act emits, the emission is durable,
and the cost lands on people who are not him.

---

## 3. WHAT IS NOT SETTLED, INCLUDING A LINE OF MY OWN THAT WENT TOO FAR

**THE PROBE'S OWN VERDICT SAID "the record does not merely count, it NAMES.
The emission is identifying." THAT IS AN OVERCLAIM AND I AM WITHDRAWING IT.**

`anchors.person` counts `/in/` hrefs inside `main`. Five is a true count of
member links on the page. It does **not** establish what those links point at.
At least three candidates are consistent with the number and this instrument
separates none of them:

* the searchers themselves, named;
* a "people also viewed" or suggestion rail, which is other people but not
  searchers;
* page chrome -- **his own profile link is plausibly one of the five.**

An integer that answers "are there member links here" was read as though it
answered "does the record name the searchers". Those are different questions,
and the second needs a capture this wave did not take. **The count is the
measurement; the interpretation was not.**

Still open, unchanged:

* **D2, what a searcher SEES.** Untouched. Only LOAD B settles the card
  contents, the parser cost, and Q1's badge.
* **WHICH class of search feeds the counter.** `Search 12%` establishes that
  search-as-a-category is tracked and attributed. Whether a Recruiter search,
  a logged-out search and an ordinary member search all feed it is not
  answered. The burden sits on the addition, so this argues for refusing.
* **What the 108 and the 13 MEAN.** Both labels came back `<redacted>` -- see
  section 4. The numbers are real; their captions are not established.

---

## 4. THE READER BEHAVED AS DESIGNED, AND ITS DESIGNED FAILURE MODE FIRED

Both metric labels returned `entity_linked: "unwalked"` and therefore
`label_shape: "<redacted>"`. The ancestor walk ran out of its six hops before
reaching a page root, so the reader could not establish that the pair's row
carries no member link, and **anything but a flat `no` costs the label.**

That is the conservative branch working. It is also a real limitation and the
constant's own docstring predicted this exact outcome in advance: *"If the
live read shows the headline is not among the first two pairs, this reader
returns two shaped labels that do not say what was wanted -- a visible miss,
which is the failure to have."* The miss is visible; nothing leaked.

**The fix is a capture, not a bigger hop budget.** Raising the budget would
make the walk reach `main` and answer `yes` everywhere, which redacts more
rather than less. What is needed is the real DOM shape, and this wave did not
capture it.

Other measured facts about the live page, recorded because no capture of this
surface existed anywhere before today:

* **No `data-view-name` attributes at all** -- `view_names` empty,
  `view_name_counts` empty. The hydrated-render anchors that
  `PROFILE_VIEWS_INSIGHTS_JS` prefers are absent here, and both of this
  reader's fallback routes carried the reading. The `<label>` fallback is what
  produced the four channel rows.
* `trend: null`. No chart carrying a "data point" sentence.
* 12 paragraphs, 21 list items, 6 headings, 7 images, 18 anchors, 2005 chars
  of `main`.
* **`redirected: False`.** The analytics address serves directly, so the
  `/me/search-appearances/` spelling deliberately left off the allowlist was
  correctly left off.
* `pairs_withheld: 0` -- only two numberish pairs exist on this render, so the
  withholding rule had nothing to withhold. **On this page, on this reading,
  the primary defence was not exercised.** It is proven only against the
  synthetic fixture. Said plainly rather than left to be assumed.

---

## 5. WHAT THE DECISION LOOKS LIKE NOW

The consent brief offered three: (1) open the 19 reads, (2) close them
EXCLUDED-RULED with a written reason, (3) measure first and rule after.

**Option 3 was taken and it has returned.** The choice is now between 1 and 2
with Q2 answered rather than empty, and the answer runs against 1:

* the act emits;
* the emission is durable and member-visible;
* LinkedIn attributes it to Search **by name**;
* the people in the set are, by `D4`, the first people-set this server would
  enumerate with no relationship to him at all;
* and by `D3` a ranker, not he, chooses whose names leave the process.

`N 4` (invite a stranger from a search result) and `N 96` (clear search
history) remain outside this, exactly as the brief ruled.

**This document does not make the ruling.** It removes the reason the ruling
could not be made.
