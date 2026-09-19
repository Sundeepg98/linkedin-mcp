# The unassigned 21, attacked with evidence the row-walk did not use

**RESULT: 0 rows filed. 1 contest SETTLED with a swap named for the integrator.
20 declines, each with what was searched. 2 previously-filed rows audited and
both confirmed, one of them on a source neither wave read.**

Zero filings is the expected shape, not a failed search: the coordinator's
slot census says 12 fillable slots against 21 rows, so at least 9 of these rows
have nowhere to go. **Measured from the row side, the count of rows for which
no slot exists AT ALL is ten** -- `N 51`, `N 59`, `N 60`, `N 61`, `P B8`,
`P D24`, `J 150`, `J 99`, `J 100`, `M C82` -- and each one's exclusion below is
POSITIVE (a committed enumeration, a measured four-item menu, a full blocker)
rather than "I looked and found nothing."

---

## 0. WHAT I MEASURED, AND THE INSTRUMENTS

Tree `201b757`, my own worktree, clean at start.
`./venv/Scripts/python.exe scripts/build_blocker_map.py` (read-only; `--write`
deliberately not run):

    frozen GAP rows at 1c08e5f    409
    assigned from committed       388
    UNASSIGNED                     21
    complete 86   partial 8   absent 3

The 21 in the map are the 21 in my brief. The three ABSENT blockers are
`FOUND-A-JOB-FLOW`, `MESSAGE-ADDRESSING`, `PREMIUM-APPLY-SURFACES` (computed by
differencing the ledger's 97 names against the 94 distinct names in
`_audit/_census/blocker-assignments.tsv` column 1; the ledger's 97 is two tables,
88 numbered rows at `_audit/2026-09-03-linkedin-gap-blockers.md:169-258` plus the
nine cost-0 rows at `:316-326`).

**A LIVE GATE READING, taken because one cheap measurement could have settled
section 1 and it is the only one that could.** Shipped `readonly.assert_read_url`
at this tree, called directly on each candidate address. **The runner is DECLARED
DISPOSABLE** -- it is a loop over the list below calling
`readonly.assert_read_url(url)` inside `try/except` and printing the exception's
first line, so the reading below is reproducible from this page without it (it
lived in the gitignored `_audit/_scratch/`, which does not survive this
worktree):

    /jobs/search-history/             REFUSED -- not on the read-only allowlist (PATTERN MISS)
    /mypreferences/d/search-history   REFUSED -- not on the read-only allowlist (PATTERN MISS)
    /psettings/search-history         REFUSED -- contains '/psettings/'        (FORBIDDEN SUBSTRING)
    /jobs/search/                     ALLOWED
    /premium/my-premium/              ALLOWED
    /jobs/view/<id>/top-choice/       REFUSED -- pattern miss
    /mypreferences/d/verification     REFUSED -- contains 'verification'       (FORBIDDEN SUBSTRING)

Two results carry below. **The `verification` substring is live and it refuses
by substring**, which matters for `J 81`. And **the gate does NOT discriminate
between the two search-history candidates** -- both are pattern misses, so both
cost the same `allowlist +1`. The measurement that could have decided section 1
cheaply comes back neutral, and I report that before the evidence that does
decide it.

**Three mechanical slices were delegated** (children, deliverables on disk in the
gitignored `_audit/_scratch/`, reviewed by me before use): a 21-row corpus
mention sweep, a ledger extraction for every open blocker, and an intra-slice
duplicate measurement. Nothing below rests on a child's judgment; every verdict
is mine and every locator was re-opened.

---

## 1. `J 18` / `J 19` vs `N 95` / `N 96` -- SETTLED. The blocker's pair is the JOBS pair.

**VERDICT: `SEARCH-HISTORY-SURFACE`'s two published rows are `J 18` and `J 19`.
The filing that holds those slots does not survive its own stated method. I am
NOT appending, because the append would break the build for every wave; the swap
is written out in 1.6 for whoever owns both halves.**

### 1.1 The row-walk's strongest stated ground is FALSE, and the true ground is stronger

**CORRECTS:** `_audit/2026-09-19-the-row-walk.md` -- its line 214 states the network slice has no *what each gap would take* section and concludes from that absence that a BLOCKER IS MISSING. The section exists, at line 573 of that slice, and line 583 prices the disputed rows. The conclusion does not follow.

It declined on "`network.md` ... has no *what each gap would take* section."
**It has one.** `_audit/_census/network.md:573`, section 5, *"THE 107 GAPS: WHAT
EACH FAMILY WOULD TAKE"*. And it covers the disputed rows:

> `_audit/_census/network.md:583` -- **People search + 13 filters** | **79-96 (18)**
> | READ | REV | *One allowlist pattern for `/search/results/people/` plus a query
> builder, and a person-card parser*

`N 95` and `N 96` are inside `79-96`. **So the network slice DOES price them --
and it prices them with no denylist exemption and no WriteSpec, on the
people-search pattern.** That is not blocker 74's charge. A wave that declines
on "the slice is silent" can be refuted by finding the sentence; a wave that
declines on "the slice speaks and says something else" cannot.

### 1.2 What blocker 74 publishes, and the only census line in the corpus that generates it

    _audit/2026-09-03-linkedin-gap-blockers.md:244
    | 74 | `SEARCH-HISTORY-SURFACE` | 2 | 1R/1W | allowlist +1, denylist x1, WriteSpec | no | 8 | 0.25 | BUILD |

    _audit/_census/jobs.md:428
    | 18-19 | recent searches read / clear | a new read surface (`/jobs/search-history/`
    or equivalent) on the allowlist; the clear is a destructive verb and `"delete"`/`"remove"`
    are on the mutation-verb denylist | R + W | clear is NOT reversible |

Every component, in one sentence: allowlist +1, denylist x1, a write (WriteSpec),
direction `R + W`, and a named address. **Four measurements on how unique that
is:**

1. `| R + W |` occurs **5 times in the whole census, all five in `jobs.md`**
   (`network.md` 0, `profile.md` 0, `messaging-and-content.md` 0). Of the five,
   **`18-19` is the only group of exactly two rows.**
2. **Exactly two ledger blockers are published `2 | 1R/1W`**: `#72
   MULTILANG-PROFILE` (the profile language pair) and `#74`.
3. **Exactly two ledger blockers charge `allowlist +1, denylist x1, WriteSpec`**:
   `#36 JOB-ALERTS-SURFACE` and `#74`. `#36`'s recipe is generated by
   `jobs.md:430` -- **the line adjacent to 428 in the same costing table.**
4. `N 95`/`N 96` cannot generate that recipe: `network.md` names the mutation-verb
   denylist **nowhere** in connection with them, and its table carries no
   Help-Center citation column at all (measured: 0 intra-file article groups in
   `network.md`, against 33 in `jobs.md`).

### 1.3 The group-to-blocker correspondence is MEASURED, and not by me

`_audit/2026-09-19-blocker-map-ruling-requests.md:345-356` tested `jobs.md`
section 2's groups against the ledger's published splits: **15 groups fall wholly
inside a blocker, 14 agree, 1 contradicts** (`78-83`). That is a committed
instrument establishing that this costing table's groups map one-to-one onto
ledger blockers. I reached the same structure independently before reading it
(`9-14` -> `JOB-SEARCH-PARAMS` 6R; `15-16` -> `ALL-FILTERS-PANEL` 2R; `17` ->
`DEVICE-GEOLOCATION` 1R; `31-36,41` -> `JOB-ALERTS-SURFACE` 7W; `42` ->
`JOB-COLLECTIONS-SURFACE` 1R; `54-56` -> `TRACKER-ROW-MENU` 3W). **`18-19` sits
inside that correspondence and the only blocker it can be is `#74`.**

### 1.4 The filing that holds the slots is the count-plus-split class, and the rival exists

    _audit/2026-09-05-settings-tail.md:220-222
    Row ids located and cross-checked (row-level lookup delegated; verified
    against the ranked table's own counts and R/W splits):
    | `SEARCH-HISTORY-SURFACE` | N 95, N 96 | 1R/1W | **no** |

`J 18`/`J 19` match that count (2) and that split (1R/1W) identically. **By the
standing rule -- a row admitted by a count it SHARES WITH A RIVAL is not
admitted -- that filing does not survive the rival's existence.** And the same
document's section 2.2 reaches blocker 74 by grouping it with the settings family
(`74, 79, 80, 82, 85, 86, 87`), i.e. by the blocker's NAME sounding like a
setting. That is the one-column error the `ACCOUNT-VERIFICATION` filing names as
having hidden `PICKER-SURFACES` and `EASY-APPLY-MULTISTEP`
(`blocker-assignments.tsv:401`), made on a third axis.

**Both corroborations of the settings reading are DOWNSTREAM of it, dated:**
`scripts/_probe_search_admission_blast_radius.py:105-110` ("A DIFFERENT BLOCKER
-- SEARCH-HISTORY-SURFACE, 1R/1W") was introduced at `ee92087`, **2026-09-19** --
fourteen days after `settings-tail`. It names no row id. Against it,
`scripts/_probe_route_vs_surface.py:114` -- `("J 18 J 19", "recent job searches",
f"{BASE}/jobs/search-history/")` -- was introduced at `2288993`, **2026-09-05**,
and it names both row ids against the address `jobs.md:428` names.

### 1.5 What I did NOT find, stated because its absence is the honest part

**No committed source pairs `J 18`/`J 19` with the string
`SEARCH-HISTORY-SURFACE`.** I checked the main checkout's own evidence index
(`_audit/_scratch/_blocker-rowid-evidence.tsv`, 331 KB): the only line pairing
row ids with this blocker's name is `settings-tail:222`, the one above. My case
is a DERIVED identification from two first-party sources (the ledger's boundary
column and the census's costing sentence), plus a correspondence another wave
measured at 14 of 15. It is stronger than the filing it displaces; it is not a
naming.

### 1.6 THE SWAP, and why I am not making it

`scripts/build_blocker_map.py:259` **fails the build on a positive delta**
(*"FAIL: the map assigns MORE rows than the ledger published"*). Appending two
rows to a COMPLETE 2-row blocker would take it to 4 of 2 and break the map for
every wave. So this is a swap, and a swap is an integration act:

    REMOVE (two lines, blocker-assignments.tsv:139-140)
      SEARCH-HISTORY-SURFACE  N 95  ... settings-tail L222
      SEARCH-HISTORY-SURFACE  N 96  ... settings-tail L222

    ADD
      SEARCH-HISTORY-SURFACE  J 18  RECON-CENSUS-COMMITTED  _audit/_census/jobs.md  L428
      SEARCH-HISTORY-SURFACE  J 19  RECON-CENSUS-COMMITTED  _audit/_census/jobs.md  L428

**ITS COST, STATED SO NOBODY DISCOVERS IT AFTERWARDS.** `N 95`/`N 96` do not
become homeless -- their own slice prices them inside the people-search family
(`network.md:583`), whose blocker is `SEARCH-RESULTS-SURFACE`, and
`_audit/2026-09-05-search-results-consent.md:164-166` lists both inside that
blocker's 21. But that blocker reads COMPLETE 21 of 21 today only because a
later reconstruction carved them back OUT to make the count land
(`blocker-assignments.tsv:299`, the `N 79` note). **Putting them back re-opens a
21-row membership that has now been reconstructed three ways.** That is why the
swap is the integrator's and not mine.

---

## 2. `J 81` -- RULED ON THE LEDGER'S OWN ASSIGNMENT RULE: the rule does not fire. DECLINE.

**Reached independently from the sources, as instructed; I was not told any
sibling's verdict.**

### 2.1 The rule, applied properly rather than cited

    _audit/2026-09-03-linkedin-gap-blockers.md:166-169
    ASSIGNMENT RULE: one blocker per row, the EARLIEST binding constraint. A row
    that looks blocked by a missing write but has no way to find its target is
    filed against the missing surface, not the missing write.

Two candidate constraints for `J 81`:

* **(a) `PREMIUM-APPLY-SURFACES` (#61)** -- `allowlist +2, WriteSpec`: a pattern
  miss. MEASURED above: `/jobs/view/<id>/top-choice/` is refused as a pattern
  miss, `/premium/my-premium/` is already allowed.
* **(b) `ACCOUNT-VERIFICATION`** -- cost-0, RE-FILE, *"the new `verification`
  substring probably bites"*. MEASURED above: the substring is real and refuses
  by substring.

The row-walk is RIGHT that (b) would be the earlier constraint if it applied:
`_audit/2026-09-05-settings-tail.md:275-276` states the ordering as a first-party
rule -- *"A forbidden substring cannot be lifted by adding a pattern; a
pattern-miss is admitted the moment somebody adds one."*

**But the rule has an antecedent, and the antecedent is a measurement nobody
has.** For (b) to reach `J 81`, `J 81`'s target address must contain the
substring. `J 81`'s census reason cell is literally `--` (`jobs.md:277`); no row
in the corpus names the address of the verify-account flow; and the ledger says
so about this exact blocker, twice, refusing to supply it:

> `:324` -- *"no row names a url, so the address is ASSUMED and this is NOT
> machine-verified"*
> `:541-543` -- *"the `verification` substring almost certainly reaches them, but
> no census row names a url, and I will not invent an address to make a check
> pass."*

**So the assignment rule does not select `ACCOUNT-VERIFICATION` for `J 81`. It
is blocked on the one input the ledger's own author declined to invent.** A rule
whose antecedent is unmeasured does not fire, and firing it anyway is inventing
that address on the author's behalf.

### 2.2 And the source classifies the row at ROW level, which answers the objection the ruling was challenged with

The committed ruling (`_audit/2026-09-19-the-three-ruling-requests-ruled.md:88-94`)
rested on the census's SECTIONING, and the row-walk answered that the section
test "proves too much" because `J 78`-`J 83` are all in section D. **That
objection is refuted by a column the ruling never used.** Measured over
`jobs.md`:

    | 78 | Cover Letter Assistance (Premium AI drafting)        | a7121956 |
    | 79 | Mark a job "Top Choice" (Premium, 3/month)           | a1462229 |
    | 80 | Attach an optional message ... with a Top Choice mark| a1462229 |
    | 81 | Verify account to raise the Easy Apply daily limit   | a8068422 |
    | 82 | Observe the Easy Apply daily limit / rate-pause state| a8068422 |
    | 83 | Save voluntary self-identification answers for reuse | a507694  |

**Four distinct Help-Center citations across the six rows, so the citation column
discriminates INSIDE the block that the sectioning could not.** And
`a8068422` occurs **exactly twice in the entire corpus** -- rows 81 and 82.
The census's own provenance column binds `J 81` to the Easy Apply daily-limit
article, alongside "Observe the Easy Apply daily limit". **`J 81`'s subject is
the limit; verification is the remedy that article documents.** That is the
source's classification at row level, and it is strictly stronger than the
section grouping the ruling used and than the "subject is the account" test the
recommendation used.

(The campaign already treats a shared article id as evidence at this strength:
the `BADGES-SURFACE` ruling turned on `B8` and `K9` sharing `a1577365`.)

### 2.3 What I verified rather than inherited

The `ACCOUNT-VERIFICATION` filing claims *"the only other verification-shaped row
in the corpus is `J 81`"* (`blocker-assignments.tsv:401`). **I re-measured it:**
`grep -i verif` across the four census files, restricted to GAP rows, returns
`J 81`, `P A24`, `P N14`, plus `M C90` ("Verified comments filter", already filed
to `POST-COMMENT-CONTROLS`) and two incidental "entitlement unverified" cells.
**The claim holds.** I did not take it on trust and I do not vouch for the rest
of that line.

### 2.4 Verdict and consequence

**`J 81` stays UNASSIGNED. The ruling at `12c20e1` stands -- not honoured,
CONFIRMED, on evidence it did not have.** `ACCOUNT-VERIFICATION` stays 2 of 3,
and its third slot is a strong candidate for the "slot with no row" class: the
ledger's own cell says the blocker's applicability is assumed, so the third row
may never have been a distinct row.

---

## 3. `J 78`, `J 79`, `J 80`, `J 82`, `J 83` -- DECLINE. Over-named by one, and the map's stated reason for them is FALSE.

The only committed source pairing these rows with a blocker is
`scripts/_probe_jobs_tail_boundary.py:63` -- `# 61 PREMIUM-APPLY-SURFACES --
census rows J78-J83.` **It names six against a published five and claims nothing
that separates them**; `J 82`'s filing on the published `1R` was retracted at
`0aca3d0` and Request 4 retired the `1R` as a discriminator.

**TWO THINGS I ADD.**

1. **The map's UNASSIGNED reason string is false for these six** -- it says *"no
   committed source names this row against any blocker"* and a tracked probe
   does. (Confirmed independently; the coordinator flagged the same defect.) It
   is a generator default, not a finding, and a future wave reading it as
   evidence of absence will re-derive the probe from scratch.
2. **The probe comment's own body does not reach `J 81`.** The three URLs under
   that header are `/premium/my-premium/`, `/premium/products/` and
   `/jobs/view/<id>/top-choice/` -- cover-letter/Top-Choice/premium-hub
   addresses. The `J78-J83` range is a HEADER LABEL on a URL list, in the same
   shorthand style as the `# 36 alerts` and `# 62 tracker` blocks beside it. It
   is a real row-id enumeration and it is also a shorthand; both are true.

**What would close this blocker: a ruling on whether the ledger's `5` or the
probe's `6` is right.** If it is a LEDGER UNDER-COUNT, all six file at once on
the strongest class short of the ledger, exactly as `N 104` was banked against a
contested count (`blocker-assignments.tsv`, the `N 104` line). I cannot execute
that: six rows into five published slots trips the build FAIL at
`build_blocker_map.py:259`, so it is a declared-over-run decision, which is
the integrator's -- and it is the same shape as ruling D of `201b757`.

---

## 4. `N 61` -- DECLINE, excluded by TWO committed enumerations, and its siblings go with it

`N 59` (W), `N 60` (W), `N 61` (R) are one family with one cause
(`network.md:292-294`, all three carrying *"EXISTENCE UNCERTAIN -- see 9.2"*),
and their 1R/2W split matches `HASHTAG-EXISTENCE`'s published `3 | 1R/2W`
exactly. **That match is a trap and it is the reason the trio reads placeable.**

**Exclusion 1, the ledger's own amendment** (`2026-09-03-linkedin-gap-blockers.md:1173-1177`)
enumerates the blocker's three published rows by id -- `N 194`, `C 11`, `C 52` --
and that trio ALSO satisfies 1R/2W. Two different row sets satisfy the split, so
the split identifies nothing (the defect Amendment E named as *"one axis wearing
two names"*). The amendment names ids; the split does not. Ruled at `201b757` B,
and `N 61` was removed on it.

**Exclusion 2, the only other enumeration that could take an R row.**
`network.md:586` lists the people-follow family by id -- *"Following people (read
side) | 38, 39, 40, 44 (4)"* -- and `PEOPLE-FOLLOW-LISTS` is COMPLETE at 4
holding exactly those. `N 61` is not in it.

**So the division has NO blocker for hashtag following at all.** `N 59`, `N 60`,
`N 61` are three rows with no slot -- a ledger under-count of one blocker, not a
lost row. The census itself flags the family as unmeasured
(`network.md:1026`, *"Rows 59-61 are a floor, not a saturation claim"*), which is
consistent: you cannot divide what you have not enumerated.

---

## 5. `P B8` -- VERIFIED duplicate. It reveals a population the duplicate register does not have.

**Verified character-for-character** (measured by instrument, not read by eye):

    profile.md:244 | B8 | Top Voice badge show / hide | W | GAP | `a1577365`; no tool, no reason |
    profile.md:420 | K9 | Show / hide the Top Voice badge | W | GAP | `a1577365`; no tool, no reason |

Direction IDENTICAL, state IDENTICAL, notes cell IDENTICAL, article-id set
IDENTICAL. `a1577365` occurs **exactly twice in the whole census** -- these two
rows.

**THE NEW PART: the duplicate register cannot see this pair, by construction.**
`_audit/2026-09-19-duplicate-register.md` adjudicates 13 pairs and all 13 are
CROSS-slice; its method section states the population as *"two slices stating one
capability"* (`:101-102`). `B8`/`K9` are both in `profile.md`. The `BADGES-SURFACE`
ruling already noticed the asymmetry -- *"the standing hold covers CROSS-slice
duplicates where this pair is INTRA-slice"* -- without drawing the consequence:
**the register has no intra-slice population, so no instrument in this campaign
is looking at that class.**

**I measured the class.** Over all four slices, intra-file, by shared article id
and by normalised capability-text similarity: in `profile.md`, exactly ONE pair
scores 1.000 with the SAME direction and the SAME state -- `B8`/`K9`. Every other
1.000 pair there is the census's deliberate read/write split of one capability
(`A1`/`A2` Headline R and W, and seven more of that shape), which is a feature,
not a duplicate. The runner-up is `B7`/`J2` at 0.667 (both W, both GAP, capability
text "#Hiring photo frame apply / remove" against "#Hiring photo frame add /
remove"), whose notes cells differ.

**VERDICT: `P B8` is not a row wanting a blocker.** Its capability is filed, as
`K9`, on a tiebreak the ruling itself recorded as a coin-flip and explicitly not
a precedent. It is also not subtractable: the register's standing rule is no
subtraction without a documented conditional, and this pair has none. It should
be entered in the register as the first member of an INTRA-SLICE section, with
`B7`/`J2` beside it as the near-miss.

**AND THE OVERSTATEMENT IS BOUNDED AT EXACTLY ONE ROW, which is the part a
future wave needs.** The same measurement ran over all four slices, and I checked
every intra-file near-duplicate pair scoring 0.6 or higher against my pool:
`jobs.md` returns 2 pairs (`118`/`119`, `94`/`96`), `network.md` 12,
`messaging-and-content.md` 3 (`M11`/`M12`, `C24`/`C25`, `C50`/`C81`),
`profile.md` 15. **Not one of those pairs contains any of my other twenty rows.**
So `P B8` is the only member of the residue that duplicates a row already filed,
the residue is overstated by one and not by more, and nobody needs to re-run this
search to find out.

---

## 6. `J 99` / `J 100` -- DECLINE. The elimination still does not close, and nobody has named the discriminator.

`OPEN-TO-WORK-MODAL` is published `11 | 11W` and reads COMPLETE holding
`J 92`-`J 98` + `P I13`-`I16`, filed on Amendment E of
`_audit/2026-09-19-profile-modals-measured.md`. **Amendment E's added check was
real** -- membership requires being GAP at the frozen commit, which is what
convicted the earlier `I2`-`I12` identification.

**But at `1c08e5f` the candidate set is thirteen, not eleven.** `J 99` and
`J 100` were GAP at the freeze (they are in the frozen 409; that is why they are
in my pool), and `jobs.md:439` puts them in the same family as the rest --
*"92-100 | every job-preference FIELD, Minimum Pay, recruiter visibility | all
live behind the same modal as rows 89-91"*. **Amendment E's eleven are chosen
from thirteen by taking the contiguous block `92`-`98`; it states no
discriminator that excludes `99` and `100`, and I could not find one.**

So this is two rows against a blocker that is full, where the fullness rests on
contiguity. **Declined, concurring with the row-walk, and the weakness is
reported rather than acted on**: it is a filing inside the recovered 388, not
mine to move, and moving it would strand two others.

(`J 99` is separately EXCLUDED-RULED today by container inheritance. That changes
its state, not its frozen membership.)

---

## 7. THE REMAINING TWELVE, each with what was searched

### 7.1 `M M13` "Forward a message" -- DECLINE. One candidate, one hole, no link.

This is the sharpest near-miss in the set and I am declining it deliberately.

**What is true:** `PER-MESSAGE-OVERFLOW-MENU` publishes `2 | 2W`, holds `M M11`
(edit), one W slot open. **Every other per-message act in the frozen set now has
a home, each taken by another wave on a committed source** -- `M10` ->
`THREAD-REPLY-BOX` (the rival released it in writing), `M47` ->
`THREAD-REPLY-BOX` (ledger Amendment A23), `M48` -> `MESSAGE-REACTION`, `M49` ->
`CONVERSATION-OVERFLOW-MENU`. `M12` (delete) was EXCLUDED-RULED at the freeze and
is not in the 409 at all, so the natural "edit + delete" pair for this menu was
never available. **`M M13` is the last per-message act without a blocker, it is
`W`, and the slot is `W`.**

**Why that is not enough.** No source puts forward in that menu: `M11`'s cell
names the menu, `M13`'s cell says *"never named"*. The only family statement
about `M13` points somewhere ELSE -- `messaging-and-content.md:496` lists
"forward" in the 18-row composition family whose stated blocker is *"there is no
working way to address a human being on this surface"*, i.e. `MESSAGE-ADDRESSING`
(`#57`, `1 | 1W`, EMPTY). **And I checked that family: 17 of its 18 members are
filed, to ten different blockers, so the family cell is demonstrably not a
blocker enumeration** -- it scatters. Elimination over a set that was never
co-extensive is not a filing. One candidate plus one hole plus no positive link
is the shape of a coincidence.

**The one observation I add for whoever rules it:** `MESSAGE-ADDRESSING` is
published `1 | 1W` with boundary **`none`** and cost **2, MEASURE** -- no
WriteSpec charged, where the ledger's own cost model charges 3 for a WriteSpec
once per blocker. A blocker whose single row is a write but which buys no
WriteSpec is costed as a MEASUREMENT, which matches the family cell's *"nothing
here is worth building until compose-by-identifier lands and a committed
recipient has been OBSERVED"*. `PER-MESSAGE-OVERFLOW-MENU` by contrast is
`2 | 2W | WriteSpec | cost 6 | MEASURE` -- a menu capture plus a WriteSpec, which
is exactly what forwarding would need. That is a cost-shape argument, it is
DERIVED, and it is not a naming.

**What would force it:** one capture of an open per-message overflow menu showing
Forward among its items. The blocker is already queued MEASURE for precisely
that capture.

### 7.2 `M C82` "Share a Newsletter Page" -- DECLINE. A row with no slot, not a row with no evidence.

`NEWSLETTER-SURFACE` is COMPLETE at 12 of 12. **`C82`'s family membership is not
in doubt and I can now show it from tracked code rather than prose:**
`scripts/_probe_newsletter_routes.py:106,108` probes one newsletter page against
the row tuple `("M C80 N 55 N 56 M C82")` -- three of those four are filed to
this blocker. The obstacle is arithmetic, not evidence: the published 12 is full,
and `build_blocker_map.py:259` FAILs the build on 13 of 12.

The blocker is full partly of confirmed duplicates it may not subtract: the
register's CLEAN pair #7 (`P L4` / `M C83`, newsletter analytics, both GAP) is
inside it, and so is `M C80`, which the register's BUNDLED class says spans
`N 55` and `N 56` -- also both inside. **Three rows for what may be two
capabilities, and one distinct capability outside with nowhere to go.** A swap
was already proposed and declined by the wave that owns the blocker
(`_audit/2026-09-19-partial-blockers-closed.md:252-282`). It becomes fileable the
moment a duplicate subtraction is ruled; until then the register's own no-
subtraction rule keeps the seat occupied.

### 7.3 `N 41`, `N 42` -- DECLINE. Two W candidates, one W slot, and I measured that the family cannot break the tie.

`ARTICLE-SURFACE` publishes `6 | 1R/5W` and holds `C46` (W), `C48` (R), `C49`
(W), `C78` (W), `C79` (W) = 1R/4W. **The open slot is exactly one W.** Both
`N 41` and `N 42` are W (`network.md:269-270`) and both reason cells read, in
full, `REV`.

**The family line cannot discriminate, and I can show why rather than assert
it.** `network.md:590` groups them -- *"Groups, articles, misc follow | 37, 41,
42, 43, 49, 50, 51, 63, 64, 76 (10)"* -- and that family's ten members went to
SIX different blockers: `50`,`76` -> `OFF-PLATFORM-WIDGET`; `49` ->
`SKILL-PAGE-SURFACE`; `63`,`64` -> `GROUPS-SURFACE`; `37`,`43` ->
`FEED-ITEM-OVERFLOW-MENU`. **Seven have homes and the three without are exactly
`N 41`, `N 42`, `N 51`** -- my three network rows. A family that scatters across
six blockers is not an enumeration of any one of them.

I also agree with the row-walk against the standing "cross-slice duplicate of
`C79`" ground: `M C79` "Follow or unfollow member articles" is a BUNDLED row, and
the register's own rule is that a bundled row is not a clean duplicate and must
not be subtracted as one. The decline stands on the tie, not on the duplicate.

### 7.4 `N 51` "Mute a company" -- DECLINE, positively excluded.

`network.md:584` enumerates the company family by id -- *"Company pages | 33, 47,
53, 54, 101, 102, 104 (7)"* -- and 51 is not in it; `COMPANY-PAGE-SURFACE`'s own
filed rows all carry the census cell *"no `/company/` pattern"*, where `N 51`'s
cell reads only *"REV. `mute` 0 hits"*. The only mute-shaped blocker,
`FEED-ITEM-OVERFLOW-MENU`, is COMPLETE at 5 and already holds the mute-a-person
row `N 43`. **No blocker in the division is named for muting a company.**

### 7.5 `N 59`, `N 60` -- DECLINE. See section 4; the whole trio has no blocker.

### 7.6 `J 150` "Writing Assistant recruiter message" -- DECLINE, and it is positively excluded rather than ambiguous.

`_audit/2026-09-05-decide-retire-rulings.md:84` files `AI-ASSIST-MESSAGING` at
2/2 with `M M40` and `M M51` and says in the same cell: *"three rows share the
family (`J 150` is the third)"*. **The document that filled the blocker names
`J 150` as the one left out.** The alternative reading it offers -- Writing
Assistant as an addressing failure -- is refused by the census itself, which
prices `J 150` behind a send-VERIFICATION wall (`jobs.md:447`, *"nothing here can
verify a send"*), and no published blocker is named for send-verification: the
rows that hit that wall (`M1`, `M2`) left GAP as COVERED-CANNOT-DELIVER and so
were never divided.

### 7.7 `P D24` "Open to volunteering" -- DECLINE, and the missing blocker is now MEASURED.

`OPEN-TO-HIRING-MODAL` publishes `5 | 1R/4W` and holds `P J1 J2 J3` (W) + `P J4`
(R); one W slot. `D24` is a W whose cell says it is *"reached from the `Open to`
button, one of the three items measured on his account"*, and the arithmetic
closes. **It closes and it is wrong, and `profile.md` proves it in its own
words:**

> `_audit/_census/profile.md:754-763` -- *"A census of all five profile captures
> measured the `Open to` button's menu resolving to exactly three items --
> Hiring, Providing services, Finding volunteer opportunities ... LinkedIn
> documents four items (`a547248` names three: finding a new job, hiring,
> providing services; **`a6862361` adds finding volunteer opportunities**)."*

`a6862361` is the article `D24` itself cites. **So volunteering is the FOURTH
`Open to` item, and the ledger has a blocker for three of the four** --
`OPEN-TO-WORK-MODAL` (finding a job), `OPEN-TO-HIRING-MODAL` (hiring),
`SERVICES-PAGE-SURFACE` (providing services). A volunteering row wants a fourth
that does not exist. **A wave routed to the HIRING modal opens the wrong tab.**

### 7.8 `J 18`, `J 19` -- see section 1. Contest settled, swap named, not appended.

### 7.9 `J 81` -- see section 2. Declined on the ledger's own rule.

---

## 8. THE TWO ROWS THE ROW-WALK FILED -- AUDITED, BOTH CONFIRMED

I was asked to check them and I did not take the integration ruling as the check.

**`M M49` -- CONFIRMED, arithmetic re-measured from the census rows.** Directions
read off `messaging-and-content.md` row by row: `M25 W`, `M27 W`, `M28 R+W`,
`M29 W`, `M30 W`, `M31 W`, `M32 W`, `M36 W` (the eight LEDGER-AMENDMENT rows),
plus `M35 W` and `M49 R`. That is **8W + 1RW + 1R = 10 against a published
`1R/8W/1RW`, closing with zero headroom.** `M49` was the only unassigned R in the
messaging slice, so the R slot had no rival. The refusal it overturned did
describe a different row: `M37` "Turn read receipts and typing indicators on or
off" is the setting and is filed to `MESSAGING-SETTINGS`; `M49` is
`EXCLUDED-RULED`-free and reads the sender-side indicator.

**`M M35` -- CONFIRMED, and I found a corroboration neither wave used.**
`_audit/2026-09-19-unfired-but-built.md:129` groups `M M35, M M36, N 176, P N12`
as rows whose needed route is a settings page against `update_setting`'s single
address. **`M M36` is a LEDGER-AMENDMENT member of `CONVERSATION-OVERFLOW-MENU`.**
So an independent document pairs `M35` with a confirmed member of the very
blocker it was filed to, and the ledger's own author had already placed that
partner there.

**THE RESIDUAL RISK, NAMED.** `M35`'s membership rests on the census's
conversation-management grouping at `messaging-and-content.md:498` -- the cell
ruled dead for DIRECTION at `201b757` C. Used for membership only, it is the same
usage the campaign has accepted elsewhere. But at filing time the open W slot had
four other unassigned W rivals (`C82`, `M13`, `M5`, `M47`); two have since been
filed elsewhere, and the two that remain are not conversation-management acts.
**So the filing is sound and its ground is membership-by-grouping, not a row-id
enumeration.** A source naming this blocker's ten rows by id would settle it; none
exists.

---

## 9. FINDINGS THAT ARE NOT ROW VERDICTS

1. **`OPEN-TO-HIRING-MODAL` is a candidate LEDGER OVER-COUNT of one.**
   `profile.md` section J is *"Open To Hiring (4)"* and all four rows are filed.
   The published 5 needs a fifth W. No unassigned row is an Open-To-Hiring act
   (section 7.7). The only other #Hiring write in the corpus is `P B7`, which is
   filed to `BADGES-SURFACE` and closes that blocker's `2R/3W` exactly (`K8` R,
   `K10` R, `B7` W, `B9` W, `K9` W) -- so it cannot move without breaking a
   COMPLETE neighbour. Same shape as the two over-counts ruled at `201b757` E.
2. **The map's UNASSIGNED reason string lies for `J 78`-`J 83`** (section 3).
   It is a generator default and should be specialised or blanked; as printed it
   will cost a future wave the re-derivation of a probe that already exists.
3. **The duplicate register has no intra-slice population** (section 5), and the
   one measured member of that class, `B8`/`K9`, is in my pool and is inflating
   the residue by one row.
4. **`MESSAGE-ADDRESSING` (#57) is EMPTY and its only natural candidate left the
   pool tonight.** `M M5` was filed to `THIRD-PARTY-PROFILE-FORBIDDEN` by a
   sibling; the row-walk had recommended `M M5` for `MESSAGE-ADDRESSING`. **I did
   not write that filing and I do not vouch for it**; I record only that the
   blocker whose subject is the addressing wall now has no candidate in the
   corpus, and that its cost shape (boundary `none`, cost 2, MEASURE, no
   WriteSpec) fits a measurement row rather than a buildable write.
5. **Two ledger UNDER-counts are implied by my declines**, and they are the
   honest reading of "some rows have no slot": hashtag following (`N 59`,
   `N 60`, `N 61` -- three rows, no blocker) and the fourth `Open to` item
   (`P D24` -- one row, no blocker). Both are supported by measurements inside
   the census itself, not by arithmetic on the residue.

---

## 10. WHAT I FOUND GENUINELY AMBIGUOUS

Three, and only three. Everything else above is a decline with a positive
exclusion.

1. **`M M13`** (7.1). The elimination has closed to exactly one candidate for
   exactly one slot, with every rival removed by another wave on a committed
   source -- and the census's only statement about the row points at a different
   blocker. The cost-shape argument breaks the tie for me toward
   `PER-MESSAGE-OVERFLOW-MENU`, and a cost shape is not a naming. **This is the
   row most likely to be filed correctly by a wave with one capture in hand.**
2. **`N 41` vs `N 42`** (7.3). One W slot, two W rows, identical cells. I could
   not construct a discriminator from any source and I do not believe one exists
   in the corpus. If the slot is ever filled it will be a `BADGES-SURFACE`-style
   coin-flip, and it should be recorded as one.
3. **The `J 18`/`J 19` swap's SECOND half** (1.6). That the blocker's pair is the
   jobs pair, I am confident and it is measured. Where `N 95`/`N 96` land
   afterwards, I am not: their own slice prices them inside the people-search
   family, and that family's blocker closes at exactly 21 today only because a
   reconstruction carved them out. **I settled the contest; I did not settle the
   consequence.**

---

## 11. WHAT THIS DOES NOT CLAIM

Locating a row does not measure it, unblock it or schedule it, and I located
none: every one of the 21 stays where it was. The gate readings in section 0 are
readings of the SHIPPED read boundary at this tree and say nothing about what
LinkedIn serves. **I did not write the filings I audited in sections 8 and 9.4,
and nothing here vouches for the rest of the recovered 388.**
