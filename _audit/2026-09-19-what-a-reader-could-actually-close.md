# A READER CANNOT CLOSE 233 OF THE 315 STILL-GAP ROWS

> Measured 2026-09-19 ~12:10 by the box, against the working tree, with
> `scripts/reader_closable_blockers.py`. Four controls, all shown passing, and
> the instrument REFUSES TO REPORT if any fails.

**The standing assignment is "LIVE blockers where a reader is the whole
remaining cost". The first thing worth saying is how few of them there are.**

    still-GAP rows                                     315
    reader-reachable (direction R or R+W)               82
    a reader cannot be the remaining cost for          233

## 1. THE BLOCKER'S GAP COUNT IS THE WRONG NUMBER TO SCHEDULE FROM

`GROUPS-SURFACE` is the biggest blocker in the census by GAP count. Of its 22
still-GAP rows, **15 are writes** -- join, leave, post, comment, react, invite,
message. No reader closes those, and this repository refuses them outright.

| blocker | GAP | reads | writes | a reader could close |
|---|---:|---:|---:|---:|
| `SEARCH-RESULTS-SURFACE` | 21 | 20 | 1 | **20** |
| `GROUPS-SURFACE` | 22 | 7 | 15 | **7** |
| `EVENTS-SURFACE` | 16 | 5 | 11 | **5** |
| `NEWSLETTER-SURFACE` | 12 | 3 | 9 | **3** |
| `ADMIN-RIGHTS-NOT-HELD` | 15 | 2 | 13 | **2** |
| `SERVICES-PAGE-SURFACE` | 11 | 1 | 10 | **1** |
| `FILE-UPLOAD-UNSANCTIONED` | 15 | 0 | 10 | **0** |

**Scheduling `GROUPS-SURFACE` as 22 rows of reader work over-states it by 3x**,
and `FILE-UPLOAD-UNSANCTIONED`'s 15 rows contain no reader work at all.

## 2. AND "REACHABLE BY A READER" IS NOT "A READER IS THE WHOLE COST"

The second cut is the read boundary. A read row whose address is refused is
**blocked on a decision, not on a reader** -- and the largest reader-shaped
blocker in the census is exactly that case.

**ADMITTED -- a reader is plausibly the whole remaining cost:**

| blocker | reads | address | reader today |
|---|---:|---|---|
| `GROUPS-SURFACE` | 7 | `/groups/` | `groups_page.read_group_memberships` EXISTS |
| `EVENTS-SURFACE` | 5 | `/events/` | `events.read_events_home` EXISTS |
| `CONTENT-ANALYTICS-SURFACE` | 4 | `/analytics/creator/content/` | -- |
| `NEWSLETTER-SURFACE` | 3 | `/mynetwork/network-manager/newsletters/` | -- |
| `SCHOOL-PAGE-SURFACE` | 2 | `/school/<name>/` | -- |
| `ANALYTICS-CONTROLS-UNPRESSED` | 2 | `/analytics/profile-views/` | blocked on the DISCLOSURE WITNESS, not a reader |
| `SEARCH-APPEARANCES-SURFACE` | 1 | `/analytics/search-appearances/` | -- |
| `PROFILE-PDF-DOWNLOAD` | 1 | `/in/me/` | -- |
| `PEOPLE-FOLLOW-LISTS` | 1 | `/mynetwork/network-manager/company/` | -- |

**REFUSED BY THE READ BOUNDARY -- a ruling is the remaining cost, not a reader:**

| blocker | reads | the address it needs |
|---|---:|---|
| **`SEARCH-RESULTS-SURFACE`** | **20** | `/search/results/*` -- NO allowlist entry |
| `CREATOR-HUB-SURFACE` | 3 | `/creator-hub/` -- no entry |
| `RESUME-TOOLS-SURFACE` | 2 | `/jobs/application-settings/` -- no entry |
| `RECOMMENDATIONS-SURFACE` | 1 | `/in/me/details/recommendations/` -- the pattern admits only `skills\|experience\|education` and `interests` |
| `ARTICLE-SURFACE` | 1 | `/pulse/...` -- no entry |
| `SEARCH-HISTORY-SURFACE` | 1 | `/search/...` -- no entry |

## 3. THE HEADLINE, AND IT IS A BACKLOG ITEM RATHER THAN A REPORT

**The single largest reader-reachable blocker in the census is
`SEARCH-RESULTS-SURFACE`: 20 rows, every one a READ, and there is no admitted
address for any of them.** It is not waiting on a reader, an instrument, or a
measurement. **It is waiting on a decision nobody has made.**

This repository's own record says this has been reported before -- *"people
search had no address at all, logged in my own audit as 23 gaps nobody
considered"* -- and the standing rule is that **a refusal reported twice is a
design gap wearing a safety costume, not an answer.** So it is filed here as a
costed item rather than relayed as a blocker:

* **What it needs:** an admit-and-measure wave for `/search/results/*`,
  carrying its own blast radius and a revert path. That is Amendment A10's
  shape and it is a ruling the lead can make.
* **Why it is not obviously safe:** search results are made of OTHER PEOPLE, so
  admission and a name-free shaper have to land together. **The address being
  admitted is necessary and nowhere near sufficient.**
* **Why it is not obviously unsafe either:** reading a result page invites
  nobody and messages nobody. The rows are reads.

**Nothing here admits anything.** The boundary stands until it is ruled.

## 4. WHAT THE INSTRUMENT REFUSES TO DO, WHICH IS WHY ITS NUMBERS ARE WORTH HAVING

The R/W cell **is not at a fixed index** -- `c[2]` in `profile.md` and
`network.md`, **`c[4]` in `messaging-and-content.md`**, and **`jobs.md` has no
per-row direction column at all.** A positional reader would have returned
source refs as directions for one slice and called every jobs row a write.

So the direction is found **by value** -- a short cell that IS a direction
token -- and **ambiguity is its own answer**: `unknown` when no cell matches,
`ambiguous` when two disagree. Neither is folded into a direction. That is why
`COMPANY-PAGE-SURFACE` reports 8 unknown rather than 8 writes: those are jobs
rows, and **the column is not there to be read.**

**The four controls, each shown passing before any number is printed:**

1. the shipped enumerator's per-slice row and GAP counts match
   `count_census_states.py` -- **the instrument does not get a vote on what a
   stated row is**
2. **known answers across DIFFERENT layouts**, including one in the slice where
   the column sits at `c[4]`. A finder that hardcoded `c[2]` passes every other
   check and fails this one
3. **shown refusing**, on cases built to fool it: a prose note mentioning R and
   W resolves `unknown`; two direction cells resolve `ambiguous`; a swapped
   column order still resolves correctly
4. the join loses nothing -- 314 joined + 1 unjoined = 315 enumerated, and the
   unjoined row is REPORTED rather than dropped

## 5. A CORRECTION TAKEN MID-ANALYSIS, BECAUSE IT CHANGED THE ANSWER

My first pass at section 2 tested **addresses I guessed** and concluded that
`CONTENT-ANALYTICS-SURFACE`, `NEWSLETTER-SURFACE` and `PEOPLE-FOLLOW-LISTS`
were all refused. **All three are admitted.** I had tried
`/analytics/post-analytics/` and `/newsletters/`; the allowlist carries
`/analytics/creator/content/` and
`/mynetwork/network-manager/newsletters/`.

> **"This URL is refused" is not "this surface has no admitted address."** The
> first is a fact about the string I chose.

Reading the 32 allowlist patterns instead of guessing moved three blockers from
the wrong column. **And the check that followed was also wrong** -- a substring
grep over the patterns reported 32 of them "mentioning" recommendations, which
is the same grep-instead-of-parse error this repository has paid for
repeatedly. The authoritative test is `is_read_url` on a concrete URL, and it
is the only one used above.
