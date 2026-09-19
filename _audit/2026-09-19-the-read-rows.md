# The read rows: two passes, eight banked, and a base rate that points the other way

**Wave `read-rows`, 2026-09-19.** Pass 1 ran to a 18:10 stop; the stop was lifted and pass 2
took the 33 rows pass 1 had named but not examined. Every one of the 39 read-shaped rows
now has a disposition.

The brief's thesis was that the reads are where the remaining capability is -- 22 of 36
resolved read rows became `COVERED-*` (61%) against 0 of 63 for writes. **Measured on the
census, that thesis does not hold, and section 4 is the number.**

---

## 1. TWO CORRECTIONS TO THE BRIEF, BOTH LOAD-BEARING

**The denominator is 32, not 44.** 44 is the registered tool total; the server's own
instructions name **twelve writes**. The closed read set is 32. An inflated denominator
makes coverage look thinner than it is, and those twelve names are exactly the ones a read
row must never be banked against.

**The read population is 37, not 39.** `M M28` ("View **and restore** archived
conversations") and `P K9` ("**Show / hide** the Top Voice badge") carry write verbs inside
read-shaped headlines. The census's own blocker notes confirm both were ruled W rows at
`12c20e1`. Pass 2 found a third: `J 71` ("List / **delete** stored resumes") is compound
the same way. The leading-verb filter admits all three; the capability is not a read.

---

## 2. THE METHOD -- A SECOND CLOSED SET NOBODY HAD ENUMERATED

Pass 1 ran the brief's method: enumerate the small closed set of tools and map it onto the
rows. It worked, but slowly, and it could not answer the question that actually decides most
of these rows -- **does any tool reach the surface at all?**

That question has its own closed set. `linkedin_server/readonly.py` holds the read boundary,
and **reachability is decided there before any tool runs**. Measured by *importing the
module and calling `is_read_url`* on a candidate address per row:

    ALLOWED URL PATTERNS      32
    FORBIDDEN SUBSTRINGS      33   (checked BEFORE the allowlist, as a second gate)

**Enumerating it by grep gave 24 and 11.** A one-line `grep "re.compile(r"` misses every
multi-line pattern, and the forbidden tuple was undercounted three-fold because its entries
are interleaved with long comment blocks. The module is the artifact; its text is a
rendering of it. Every reachability claim below is a call into the shipped gate, not a
reading of its source.

The resulting frame is two-dimensional and it resolves rows the tool list alone cannot:

| | tool reaches it | no tool reaches it |
|---|---|---|
| **refused by a written gate** | -- | `EXCLUDED-RULED` |
| **refused by allowlist silence** | -- | `GAP` with a named blocker |
| **admitted, tool fired, wrong quantity** | `COVERED-CANNOT-DELIVER` | -- |

The census's own section 2 is emphatic that *"the allowlist does not list it" is NOT a
reason* -- that is the silence the census exists to measure. A `_FORBIDDEN_URL_SUBSTRINGS`
entry **is** a reason, and it is named as such. That distinction is what three of this
wave's banks turn on.

**I built no fifth census scanner.** `scripts/unbanked_row_sweep.py` convicts four, and its
conclusion -- that only a human cross-reference has produced a correct answer -- held. The
boundary probe is not a fifth scanner: it does not scan the census at all, it interrogates
the shipped gate.

---

## 3. BANKED: 8

### 3.1 `COVERED-CANNOT-DELIVER` -- 5

The bar is the census's own: *a tool exists, it HAS fired live, and it cannot do the thing.*
All three clauses checked per row.

| row | capability | tool | why not PROVEN |
|---|---|---|---|
| **N 57** | View the newsletters you subscribe to | `linkedin_newsletter_subscriptions` | Returns `distinct` -- a count. `shape.subscription_row` **redacts the title unconditionally**, so the answer says a subscription exists and never which one. Fired live 2026-09-05 (ten anchors, five newsletters). |
| **N 181** | Find events hosted by Pages you follow | `linkedin_events_home` | **A consistency fix, not a new measurement.** The row's own cell declared it one decision with `N 180` -- and `N 180` was already banked `COVERED-CANNOT-DELIVER` while this row sat GAP. The tool publishes *"how many rather than which"* with no organisers at all. Fired live (a recommendation section drew three rows while its own control announced fifty events). |
| **N 101** | List an organization's employees via its employee count | `linkedin_job_detail` | **The recorded blocker `No /company/` is stale** -- the About-the-company card is read off the *job posting* page at no extra load. Shipped code names the row: `shape._ABOUT_ON_LINKEDIN` is commented *"This is the census's `N 101` capability ... in its READ half only: **it is a COUNT of people and never a list of them.**"* Fired live today on two postings. |
| **N 44** | View your own followers | `linkedin_my_profile` | Ships a `followers` field, fired live 2026-09-04: *"his topcard holds exactly ONE such line and it is connections, so `followers` is null here and that is the page's answer."* The list route is separately refused on `/follow`. |
| **M C74** | Read your feed | `linkedin_surface_census(surface="feed")` | **The cell was already the cannot-deliver argument, filed as GAP.** The census measured `/feed/` live carrying zero item permalinks and eight different authors. *"THE CENSUS REPORTS SHAPES, NEVER NAMES"* is structural -- three shaping functions stand between the page and the caller. |

The through-line is one sentence: **a tool that reports HOW MANY does not cover a row asking
WHICH.** In every one of these five, `COVERED-PROVEN` was reachable on a surface-level test
and would have been wrong.

### 3.2 `EXCLUDED-RULED` -- 3

Each sits on an entry of `_FORBIDDEN_URL_SUBSTRINGS` -- the second, independent gate the
census names as a qualifying written reason.

| row | address | gate |
|---|---|---|
| **N 38** | `/mynetwork/network-manager/people-follow/following/` | `/follow` |
| **J 71** | `/jobs/application-settings/` | `/jobs/application` |
| **J 73** | any application address | `/jobs/application` |

**N 38 is the one worth reading.** Its recorded blocker said *"is not on the allowlist"* --
allowlist silence, which the census says explicitly is not a reason. The real gate is the
forbidden list, and `readonly.py` writes the argument against this exact capability:

> The PEOPLE he follows live at `/mynetwork/network-manager/people-follow/following/`, which
> contains the substring `/follow` and is therefore refused ... That is luck, not design --
> and **the right response to the luck running out is to leave the people list unread, never
> to shorten the forbidden list.**

The sibling `/mynetwork/network-manager/company/` is admitted only because it happens not to
carry the substring. A row recorded against the weaker gate reads as cheap; against the real
one it reads as decided.

**Verified on disk**, not from an exit status: GAP **310 -> 302** across the two passes, and
the shipped counter (`scripts/count_census_states.py`) agrees -- `COVERED-CANNOT-DELIVER`
15, `EXCLUDED-RULED` 267, `GAP` 303 stated.

---

## 4. THE THESIS TEST -- AND IT INVERTS

The brief asked me to test, not assume, my pass-1 note that the 61% came from a population
where the tool was built *for* the row. Measured over the frozen row set (409 GAP rows at
the census commit), split by the brief's own leading-verb filter:

|  | frozen | resolved | `COVERED-*` incl. CANNOT-DELIVER | **an actual capability** (PROVEN or UNFIRED) |
|---|---|---|---|---|
| **read-shaped** | 50 | 19 | 9/19 = **47%** | **2/19 = 11%** |
| **not read-shaped** | 359 | 88 | 18/88 = 20% | **18/88 = 20%** |

**The reads convert to a capability at 11%. Everything else converts at 20%. The reads are
worse, not better.**

The 61% headline survives only because **`COVERED-CANNOT-DELIVER` is a `COVERED-*` state and
is not a capability.** Counting it as one answers a different question from the one a planner
is asking. Strip it out and the read rows' advantage disappears and reverses.

**My own eight are the sharpest version of this.** Five `CANNOT-DELIVER`, three
`EXCLUDED-RULED`, **zero capabilities** -- and I roughly doubled the resolved read
population doing it. The prediction in pass 1 was that `CANNOT-DELIVER` would be the modal
honest outcome. It is modal (5 of 8), and the remainder did not land on capability either.

**I could not reproduce 22/36.** Under this filter and this population the pre-wave read
figures are 11 resolved with 4 `COVERED-*` (36%); post-wave, 19 and 9 (47%). Neither is 61%.
The brief's population was defined differently and I do not know how -- stated as an open
discrepancy rather than papered over, because the number motivated the wave.

**What this changes:** the remaining read rows are not a capability reserve. They are mostly
rows where a tool lands on the right surface and returns the wrong quantity, or where a
written gate already refused the address. Planning against 61% would buy 11%.

---

## 5. NOT BANKED: 31 -- and two of these declines are the point

### 5.1 Declined although they meet the literal definition -- prior rulings stand

| row | why I did not bank it |
|---|---|
| **N 174** | View the groups you have requested to join. **A wave already measured this and deliberately refused to close it**, with a better argument than mine: the `/groups/` root draws two sections, neither a pending-requests list, and *"a section that is absent when empty reads identically to one that does not exist. A reading no instrument can fail is not a reading."* Creating a pending request to observe the surface is a WRITE. My pass-1 decline stands on stronger grounds than I had. |
| **M C38** | View post analytics. Its cell was **updated today** to *"STAYS GAP, AND THE BLOCKER IS NARROWER 2026-09-19"* -- the row wants per-post analytics and viewer demographics; the shipped read returns a per-day account series for one metric. That wave's ground was *"Not blocked on a reader."* |
| **M C39** | View analytics for your comments. Same tool, same surface, fired live. The comments metric needs `?metricType=`, which the anchored pattern refuses (measured). Declined **for consistency with the M C38 ruling**, not for lack of evidence. |

### 5.2 THE ESCALATION -- the state vocabulary has two holes, and they are costing banks both ways

**Hole 1: there is no state for "a tool fired, cannot do it, but a different tool could."**
`COVERED-CANNOT-DELIVER` is defined as *a tool exists, it HAS fired live, and it cannot do
the thing.* `N 174`, `M C38` and `M C39` all satisfy that sentence literally. They were kept
GAP on the ground that the blocker is a surface, a shaper or an allowlist decision rather
than a reader. **Both readings are defensible and they disagree**, which means the state a
row lands in currently depends on which wave reaches it. Five rows are affected.

**Hole 2: `EXCLUDED-RULED`'s enumeration does not list the refusal that actually refuses
these rows.** The definition names four qualifying sources: a `_FORBIDDEN_URL_SUBSTRINGS`
entry, a `writes.PERMANENTLY_FORBIDDEN` key, a `WriteSpec` refusing in its own words, or an
audit passage measuring the capability unreachable. **A reasoned refusal written into the
allowlist itself is not on that list.** Five rows sit on exactly that:

| row | the written refusal | where |
|---|---|---|
| **N 99** | View the Alumni page for your school. `/school/<slug>/` is admitted; `/people/` is *"a roster of members -- the one place under this root where the member-profile cause could start to apply again. **It is refused, and it is refused by this anchor rather than by a promise.**"* Measured: root ALLOW, `/people/` REFUSE. And the school address *"carried no reader at all"*. | `readonly.py` school entry |
| **N 172, N 177, N 178** | All three need a group's member directory or another member's profile. *"a group's MEMBER DIRECTORY is other people and is not admitted here **or anywhere**"*, and loading another member's profile *"leaves THEM a durable record"* -- the census's own sharpest refusal. Measured: `/groups/<id>/members/` REFUSE, `/in/<other>/` REFUSE. | `readonly.py` groups entry |
| **M C83** | View newsletter analytics. `readonly.py` lists `/newsletters/<slug>/analytics/` among addresses NOT admitted and **names this row by id**. Measured REFUSE. | `readonly.py:764` |

I declined all five rather than launder a readonly.py comment into a state the census's own
enumeration does not authorise. **A one-line ruling on whether a reasoned allowlist refusal
counts as "written" banks all five at once.** That is the single highest-yield decision left
in this row set.

### 5.3 Declined on the evidence -- GAP with a named blocker

| rows | why |
|---|---|
| **N 134** | See notable or interesting viewers. `linkedin_who_viewed_me` reaches the surface and fired live, but the blocker is literally `ANALYTICS-CONTROLS-UNPRESSED` -- the panel is behind a control nobody pressed. Banking CANNOT-DELIVER would assert an inability where the truth is "not yet pressed". **That is the laundering the census warns about**, so it stays GAP. |
| **P D28** | View a profile in multiple languages. A live reading measured `distinct_langs 1`, `langs_other_than_document 0`, but the measuring document says plainly *"WHAT I DID NOT ESTABLISH ... It does not prove a pressable control exists, and I did not press anything."* Self-limiting evidence. |
| **M M49** | Read message delivery / read indicators. `linkedin_new_messages` says *"THE UNREAD COUNT IS NOT AVAILABLE, and not for want of trying"* -- but that is HIS read state. The row's own cell says the **sender-side** indicators *"were never enumerated"*. Nobody looked, so "cannot" is unproven. |
| **N 33** | See how many of your connections work at an organization. `linkedin_connections` reaches an admitted address and returns `name`/`headline`/`profile` per row -- the ingredients -- but performs no aggregation by employer, and its docstring records **no live run of the full tool**. A cheap BUILD candidate, not a closed row. |
| **N 101's siblings: N 102, N 104, N 54** | `/company/` and `/search/results/companies/` are not admitted and **nothing is written against them**. Allowlist silence, which is GAP by definition. |
| **N 194** | `/search/results/` is not admitted, and the census states it outright: *"Nobody ruled against people search; it was never considered."* |
| **N 61** | View your followed hashtags. `/feed/following/` and `/feed/hashtag/` both REFUSE; `/in/me/details/interests/` is admitted, but the measurement that the Interests tabs are url-less client-side radios was taken on the **Companies** tab. Extending it to hashtags is inference, not measurement. |
| **J 82** | Observe the Easy Apply daily limit. `easyapply`, `easy-apply` and `/jobs/application` are all forbidden, but **I could not establish that the limit state lives at one of those addresses**, and the row is `UNASSIGNED`. Refused to guess the address in order to earn a ruling. |
| **N A3, N A5** | Page admin surfaces. `/company/<x>/admin/` REFUSE, no written passage. `ADMIN-RIGHTS-NOT-HELD`, and the Manage Pages capture carries 58 Pages and **zero admin markers**. |
| **M C43** | Read a post's text. `/post/` is forbidden, but the item permalink `/feed/update/urn:li:activity:<digits>/` **is admitted** and `surface_census` can be pointed at it. I found no record of that surface firing live, and `CANNOT-DELIVER` requires a live firing. Stated as a near-miss, not banked. |
| **M M28, P K9** | Compound rows with write verbs -- not reads. |
| **J 37, J 38, J 39, J 40, J 57** | `SERVED-BY-GMAIL-SKILL`. Served by the `linkedin-jobs` Gmail skill, not by any tool here. **A source disagreement worth recording:** `readonly.py:1045` admits `/jobs/alerts/` and cites *"census row J37, blocker 36 `JOB-ALERTS-SURFACE`"*, while the blocker-map files J 37 under `SERVED-BY-GMAIL-SKILL`. The address is admitted and **no tool reads it** -- Amendment A10's bought-and-unread shape, the same one `collections_page.py` records for the school/collections boundary. |

---

## 6. WHAT A SUCCESSOR SHOULD DO FIRST

1. **Rule on the two vocabulary holes** (5.2). One line each; it settles eight rows.
2. **Re-run the leading-verb filter with the compound-verb correction.** Three of 39 admitted
   rows are not reads.
3. **Do not plan against 61%.** The measured capability conversion for read rows is 11%.
4. `N 33` is the cheapest genuine BUILD left in this set: the data is already returned, only
   the aggregation is missing.

---

## 7. CONSTRAINTS

**No write was fired. The server was never restarted.** Every finding is read off the tree,
off committed measurements, or off a call into the shipped read boundary.

**Attribution verified 0** across both commits, by grep over message, author and email.

**Gates.** The pre-commit hook could not run in a worktree (hard-coded relative venv path);
pass 1 junctioned the venv in and both gates ran green. That path has since been fixed at
source. **The gap disclosed in pass 1 remains true**: worktrees carry no gitignored files, so
the identity gate's exact-value wordlist is absent and only the shape half runs. Nothing in
this deliverable emits a value -- the relations are named, the identifiers are not.

**Delegation.** Three `implementer` children extracted tool contracts to files
(`tools-A/B/C.md` in the session scratchpad); their output was reviewed before any of it
entered a bank, and two of their fired-live readings were re-derived from source rather than
relayed.
