# The COVERED-vs-GAP pair list, adjudicated -- 1 true of 61

> **THIS LIST IS SPENT. Do not re-run it.** All 61 pairs in
> `_audit/_scratch/_for-small-measures-covered-vs-gap.tsv` were adjudicated on
> 2026-09-19. **One is a true propagation failure (`J 27`, banked). The other
> sixty are false**, and s2 says which families they fall into so the next
> reader does not re-find them.

## The one true pair

**`J 27` "Verification badge on a posting" -> COVERED-UNFIRED.**

Its twin `profile.md K10` ("Verification badge as it appears on job posts") was
banked COVERED-UNFIRED earlier the same day on shipped-code evidence, while
`J 27` still read `--` in its note column. **Same capability, one build, two
slices, one banked.**

Verified END TO END from the tree, not from the twin's cell -- the standing
lesson that another wave's word is the lead and never the evidence:

    server.py:3410   async def linkedin_job_detail(job_id)
    server.py:3665   out["insights"] = await dom.read_job_insight_panels(page)
    dom.py:8313      "verified_job": bool(markers.get("verified"))
    server.py        return out

**UNFIRED rather than PROVEN, deliberately.** The field is surfaced; no run has
been recorded asserting a value on a live posting. Matching the twin's honesty
is worth more than an upgrade nobody measured.

## 2. WHERE THE SIXTY FALSE PAIRS CLUSTER

The list is lexical. Precision on the handed-over top 15 was measured at
**7 true / 8 false**; across the whole 61 it is **1 of 61**, because the head
was score-sorted and the tail is almost entirely one family:

| family | count | why it is false |
|---|---:|---|
| job-search filter vs **connections** filter | ~34 | `Filter: Location` / `Filter: Company` / `Filter: Easy Apply only` on `/jobs/search/` paired against `Filter by Locations` / `Filter by Past company` / `Filter by School` on the connections list. **Same words, different surface, different tool.** Every cross-pairing of the two filter sets appears, which is why one family dominates the count |
| `M1` "Send a message to a 1st-degree connection" | 7 | the documented false family -- "send X to a 1st-degree connection" matches message, message request, group-admin message, event invitation and recruiter message |
| follow/unfollow object mismatch | 6 | `Follow a company` paired with `Follow a hashtag`, `Mute a company`, `Follow a skills Page` |
| read vs write of one subject | 4 | `C60 Access your LinkedIn Groups` (a read) paired with `Join a group` and `Leave a group` (writes) |
| generic-verb collisions | 9 | `Sort by Most relevant / Most recent` on job search vs **sorting comments**; `Unsave a job` vs `Unsave a saved post`; `About text` vs `Read a post's text`; `Own skills list` vs `Follow a skills Page` |

### Three that looked true and are not, each checked rather than assumed

* **`P G7` / `N 132`** -- search appearances. `N 132` is the **SWITCH** between
  two analytics views, a different capability from reading the appearances.
  Independently adjudicated by a sibling wave the same day; my reading agrees.
* **`J 88` / `P J4`** -- `J 88` reads OPEN-TO-WORK; `P J4` is **#Hiring**, the
  other badge. `J4`'s own cell states it: *"`my_profile` parses only the
  open-to-WORK line off the topcard."* Correctly GAP.
* **`J 105` / `P L2b`** -- `J 105` lists companies **you follow**; `L2b` is
  **your own follower list**. Opposite directions of the same relation.

## 3. WHAT THE RESULT MEANS FOR THE METHOD

**A 1-of-61 precision is not a criticism of the sweep that produced it.** The
handover said so in its own words -- a CANDIDATE list, not findings, with its
measured precision stated and not rounded up. That honesty is what made it
safe to work: the list was read as a worklist, every pair was adjudicated, and
nothing was banked on a similarity score.

**The failure mode it avoided is worth naming.** A lexical matcher scores
`Filter: Location` against `Filter by Locations` at 0.595 -- higher than the
true pair `K10`/`J 27` at 0.589. **The highest-scoring pairs in this list are
false and the true one sits below them**, so any threshold that admitted the
top of the list would have banked dozens of wrong rows while missing nothing.
Score ordering is not evidence ordering.

**It is the same law this repository found twice today from the other end:** a
positive control that counts hits and not their content can be satisfied
entirely by coincidence. Here the coincidence is a shared product word, and
the only thing that separates a true pair from a false one is knowing which
SURFACE each row lives on -- which is semantic, and which is why a person read
all 61.

## 4. WHAT THIS BOUNDS

Three seams have now been run to exhaustion by this wave:

| seam | method | yield |
|---|---|---:|
| already BUILT | undetectable by heuristic; hand cross-reference | ~11 rows |
| already RULED | enumerable prohibition keys, rule read in full | 2 rows |
| COVERED twin vs GAP twin | handed-over lexical candidate list | 1 row |

**None of the three is where the remaining GAP lives.** 332 rows are still GAP
and the great majority are genuinely unbuilt, genuinely unruled, and have no
covered twin anywhere.
