# SEARCH-RESULTS: the two pre-admission conditions, discharged. NO PATTERN LANDED.

> Wave `search-admission`. All measurements taken 2026-09-19 **12:28-12:46 by
> the box** (`date`, pasted at each run), against the working tree at
> `9421af9`. `linkedin_server/readonly.py` is **unmodified** -- verify with
> `git diff --stat linkedin_server/readonly.py`, which is empty.

The ruling at `569dc5e`, section 6 of
`_audit/2026-09-19-two-census-conventions-ruled.md`, grants
`SEARCH-RESULTS-SURFACE` **in principle** on five binding conditions.
Conditions 3 and 4 are by their own wording pre-admission work. **They are the
whole of this wave, and nothing else was done.**

**WHAT THIS WAVE DELIBERATELY DID NOT DO**, because doing any of it would have
violated the ruling rather than partially satisfied it:

* **No pattern was added to `_ALLOWED_URL_PATTERNS`.** Not one character.
* **No address was admitted**, on the strength of this measurement or anything
  else. Condition 1 binds the admission to a name-free shaper landing in the
  same commit, and no shaper was built here.
* **No shaper was built**, and no card parser.
* **No browser was opened, no search was performed, no page was loaded.** Every
  `/search/` address is refused today, and section 4 of the same ruling forbids
  a discovery probe from navigating to a refused address even to find out
  whether it should be admitted.
* **No candidate was CHOSEN.** Four plausible spellings are named below with
  their measured blast radii. Picking one is the admitting wave's call, or the
  lead's; this document is the input to that decision and not the decision.

---

## A. THE CANDIDATE PATTERNS -- WRITTEN DOWN, NOT INSTALLED

### A.1 Which addresses the 20 rows actually need

21 rows carry `SEARCH-RESULTS-SURFACE` in
`_audit/_census/blocker-assignments.tsv` (counted 12:31): `N 4`, `N 79`-`N 94`,
`N 161`, `N 179`, `N 194`, `M C70`. `N 4` is the one WRITE -- send an
invitation from a people-search result -- and section 4 of the 09-05 consent
document rules explicitly that a yes to the reads is **not** a yes to it. That
leaves **20 reads**, matching the figure in
`_audit/2026-09-19-what-a-reader-could-actually-close.md`.

| rows | vertical | address the row needs | evidence |
|---|---|---|---|
| `N 79`-`N 94` (16) | people | `/search/results/people/` + filter query | consent doc s4 |
| `N 161`, `M C70` (2) | groups | `/search/results/groups/` | `2026-09-05-groups-surface-measured.md:213` |
| `N 179` (1) | events | `/search/results/events/` | `2026-09-05-events-surface-recosted.md:252` |
| `N 194` (1) | content/hashtag | **UNSETTLED** -- `/search/results/content/?keywords=%23...` or `/feed/hashtag/<tag>/`, which is a different family | see A.4 |

**CORRECTS:** `_audit/2026-09-05-search-results-consent.md:163` -- it lists two rows as unattributed
and names `N 104` (find an organization's Page by
searching) as one of the candidates. Those two have since been resolved to
`N 161` and `N 179`, and **`N 104` appears nowhere in
`_audit/_census/blocker-assignments.tsv` at all** -- not under this blocker and
not under any other. Checked at 12:43 against BOTH `HEAD` and the working tree,
because that file is uncommitted in another wave's tree right now; the
`SEARCH-RESULTS-SURFACE` id set is byte-identical in the two.

**The consequence is not cosmetic: `/search/results/companies/` serves no
assigned row**, so admitting it buys nothing and costs blast radius.

**16 of the 20 are one vertical.** That is the single most useful fact for
choosing a spelling: a people-only pattern serves 80% of the blocker.

### A.2 The four spellings, named rather than picked

    S1  people, open query
        ^https://www\.linkedin\.com/search/results/people/?(\?[^#]*)?$

    S2  four enumerated verticals, open query
        ^https://www\.linkedin\.com/search/results/
        (people|companies|groups|events)/?(\?[^#]*)?$

    S2b three enumerated verticals THAT HAVE ROWS, open query
        ^https://www\.linkedin\.com/search/results/
        (people|groups|events)/?(\?[^#]*)?$

    S3  people, STRUCTURED query
        ^https://www\.linkedin\.com/search/results/people/?
        (\?[a-zA-Z]{1,40}=[^&#/]{0,200}(&[a-zA-Z]{1,40}=[^&#/]{0,200}){0,15})?$

**Why each is a live option, in one line each.**

* **S1** is the shipped house style. `(\?[^#]*)?$` is exactly what
  `/jobs/search/`, `/notifications/` and `/analytics/profile-views/` already
  carry, so it introduces no new shape to review. It serves 16 of 20 rows.
* **S2** closes the blocker in one entry instead of four. Its path segment is a
  **closed enumeration**, which is what condition 2 asks for -- an alternation
  of literal words is not a wildcard. Its cost is that it admits three more
  third-party-dense pages at once.
* **S2b is S2 with `companies` dropped**, and it is strictly better than S2 on
  the evidence: `companies` serves no assigned row (see the correction above),
  so S2 pays for a page nothing asks for. S2b covers **19 of the 20 reads** in
  one entry and admits one address fewer than S2.
* **S3** is the narrowest and the only one that constrains what may follow the
  `?`. It is a NEW shape for this repository, which is a real review cost.

**A note on the trailing `/?`, because it is easy to misread.** In all four,
`people/?` means *an optional trailing slash*, not a literal `?`. The literal
question mark is the escaped `\?` that opens the query group.

### A.3 What separates S1 from S3, measured rather than argued

Two corpus addresses exist purely to tell them apart:

    /search/results/people/?next=/mypreferences/d/close-account   S1 ADMITS, S3 refuses
    /search/results/people/?keywords                              S1 ADMITS, S3 refuses

**Stated honestly: neither is an escalation.** A browser handed the first one
loads the people-search page and LinkedIn ignores the unknown parameter; it
does not navigate to the account-ending address. What the pair shows is a
difference in **shape**, not in reachable pages: under `[^#]*` the allowlist
stops constraining the query entirely, so a whole other path can ride inside
one, and a future tool that built a query from caller-supplied text would get
no help from the boundary. Under S3 the query must be `key=value` pairs with no
slash in a value.

That is the trade to rule on, and it is genuinely a trade -- S3's structure is
a guess about LinkedIn's filter vocabulary, and a filter this repo has not
captured (a value carrying a `/`, or a bare flag) would refuse.

### A.4 The one open question inside A, flagged rather than answered

**`N 194` (find hiring managers through the #Hiring hashtag) may not belong to
any of these patterns.** Its route is either `/search/results/content/` -- which
none of S1, S2, S2b or S3 admits -- or `/feed/hashtag/<tag>/`, which is a different family
entirely. `_audit/2026-09-19-hashtag-surface-live-evidence.md:35` records
`/feed/hashtag/` appearing **zero** times across four live loads, which is
evidence about the feed and not about the address. Whichever way it goes, it is
one row and it should not shape the pattern the other 19 need.

---

## B. THE BLAST RADIUS, MEASURED (condition 3)

### B.1 The instrument is imported, not rewritten

`scripts/blast_radius.py` (commit `d588034`, subject *"tools(boundary): what
would a candidate allowlist pattern newly admit"*) was built for exactly this
admission. It installs a candidate on the in-process tuple, re-runs the shipped
`is_read_url` over concrete urls, diffs the two verdicts and restores the tuple
in a `finally`. **It is used here, not reimplemented** -- the standing rule
after four waves reimplemented a shipped instrument and three got a broken one.

This wave's contribution is the **corpus**, which is the thing the shipped
instrument cannot supply for a surface it does not know about: its own corpus
carried two `/search/` addresses, and it says so itself -- *"an address nobody
put in the corpus is invisible here."*

    scripts/_probe_search_admission_blast_radius.py     the corpus + the controls
    _audit/_scratch/_search-admission-blast-radius.txt  the captured run, 12:36
                                                        UNTRACKED -- `_audit/_scratch/`
                                                        is gitignored. Re-run the
                                                        probe to regenerate it.

**No grep over the pattern list was used anywhere.** Every verdict below is
`is_read_url` on a concrete absolute url.

### B.2 The numbers, stamped 12:36 by the box

    corpus                       90 addresses (67 shipped + 25 added, 2 shared)
    readonly.py on disk          32 allowed patterns, 33 forbidden substrings
    already admitted             12 of the 90

| candidate | newly admitted | of those, defended by nothing |
|---|---:|---:|
| **S1** people, open query | **5** | 5 |
| **S2** four verticals, open query | **8** | 8 |
| **S2b** three verticals that have rows | **7** | 7 |
| **S3** people, structured query | **3** | 3 |
| W1 `/search/.*$` (counterfactual) | **18** | 18 |
| W2 `/search/` unanchored (counterfactual) | **18** | 18 |

**THE "DEFENDED BY NOTHING" COLUMN IS TAUTOLOGICAL FOR THE TARGET AND
INFORMATIVE FOR THE COUNTERFACTUALS, and saying so is the honest reading.** No
forbidden substring names any `/search/` address, so everything a search
candidate admits is by construction defended by nothing -- including the three
addresses the admission is FOR. **The number that carries information is the
difference: 18 against 3.** A family wildcard reaches fifteen addresses beyond
the narrow candidate's, none of them refused by anything else, and the
alternation in S2 costs exactly three of them, and S2b two.

**CORRECTS:** `_audit/2026-09-05-search-results-consent.md:195` -- its boundary snapshot reads
*"33 forbidden substrings, 24 allowed patterns"*. The substring
count still holds; the pattern count is **32** as of 12:34 today. Flagged, not
edited: the document is another wave's and its conclusion is unaffected.

### B.3 The guard shown failing on what it must still refuse

The corpus carries three strings whose **normalised** form is a different page.
A browser resolves `..` segments before it issues a request; `assert_read_url`
matches the string it was handed. Measured:

| spelling | under W1/W2 | why |
|---|---|---|
| `/search/results/people/../../mypreferences/d/close-account` | **ADMITTED** | no forbidden substring names it -- the standing `close-account` example, reached from the search family |
| `/search/results/people/../../psettings/close-account` | refused | `/psettings/` is on the denylist |
| `/search/results/people/../../mynetwork/invite-connect/invitations/` | refused | `/invite` and `invitation` are |

**This is the neighbourhood check the brief asked for, and it found one.** The
denylist bounds a wildcard's blast radius exactly where somebody already wrote
a rule; what it does not bound is what the wildcard reaches that nobody thought
to forbid. **S1, S2, S2b and S3 all refuse all three**, because a closed path
segment cannot be followed by `..`.

**AND THE ANCHOR IS NOT THE FIX.** W1 is anchored at both ends with `.*$` and
admits the traversal exactly as the unanchored W2 does -- both 18. What refuses
it is the path segment being a **closed spelling**, not the presence of a `$`.
That distinction is worth carrying into the admitting wave: "anchored" is not
the property condition 2 is really asking for; "closed" is.

**A GENERAL FINDING, BIGGER THAN THIS SURFACE, FILED NOT FIXED.** Nothing in
`readonly.py` normalises a url before matching it, and no test in `tests/`
mentions path traversal -- grepped 12:38, and every `../` hit in the tree is an
elision ellipsis in a comment, not a traversal. Every pattern on the allowlist today is
closed enough that this cannot bite, so this is a latent property of the
mechanism rather than a live hole -- but the next family-shaped pattern anyone
writes inherits it. It is out of this wave's scope and should be filed as its
own row.

### B.4 The admission does not make the surface usable, and this is new

The denylist is scanned over the **whole lowered url, query included**. Of
eleven ordinary search keywords put through it at 12:37:

    invitation  password  verification  settings
    visibility  cookies   open-to-work  two-factor     -> 8 REFUSED by the denylist
    recruiter   engineer  director                     -> 3 clean

So `?keywords=password` refuses **after** any candidate lands, and it refuses
with a message about a write guard. **The ruling explicitly does not authorise
narrowing the filter** (section 3), so this is not a licence to touch the
denylist -- it is a requirement on the TOOL: it must decide, in advance, what
it does when a caller's keyword trips a guard, and say so in its refusal rather
than emitting "not a read surface" at somebody searching for a security
engineer. **Nothing in the 09-05 consent document or the ruling anticipates
this**; it is this wave's finding and the admitting wave inherits it.

---

## C. THE REVERT TEST -- COMMITTED GREEN, SHOWN RED (condition 4)

    tests/test_the_search_results_address_is_refused_before_admission.py

**Five tests, green at HEAD (12:36, 0.25s).** They assert that all eight
search-results spellings are refused today.

**Shown failing, which is the requirement.** With the S1 candidate installed
on the in-process tuple and `readonly.py` untouched on disk:

    CONTROL PASSED -- the revert test goes RED once the pattern lands:
      AssertionError: search-results address admitted as a read:
      'https://www.linkedin.com/search/results/people/' ...
    and GREEN again with the pattern removed -- rollback proven in-process
    patterns on disk: 32

**Its docstring states its job**, in the file itself: the admitting wave
**deletes this file in the same commit that adds the pattern**, with the
deletion named in the message -- not narrowed, not silenced, not xfailed. A
deleted test is a recorded decision; a silenced one is a rollback nobody can
find.

**And it measures WHY the revert is one line.**
`test_the_refusal_is_the_allowlist_and_not_the_denylist` asserts that no
forbidden substring names any of the eight addresses. That is what makes
removing the pattern the WHOLE rollback, with no denylist surgery to undo --
and if it ever stops being true, the test says so before a rollback is
attempted rather than during one.

The two remaining tests are the controls: one proves the refusal is exactly one
pattern away from lifting (and restores on removal, in-process); one proves the
detector can report *admitted* at all, so the refusal assertions are not
passing vacuously.

---

## D. WHAT THE ADMITTING WAVE INHERITS

1. **Pick a spelling from A.2.** S1 serves 16 of 20 rows in the shipped house
   style; **S2b** serves 19 in one entry at two more admitted pages and
   dominates S2, which pays for a `companies` page no row asks for; S3 is the
   only one that constrains the query, at the cost of a new shape.
2. **Condition 1 is still entirely unmet.** No shaper exists. Admitting on the
   strength of this document alone violates the ruling -- section 6 says so in
   those words.
3. **Delete the revert test in the admitting commit**, and say so in the
   message.
4. **The tool must handle denylisted keywords** (B.4). Not by narrowing the
   denylist.
5. **`N 194`'s address is unsettled** (A.4) and should not shape the pattern.
6. **The AST boundary freeze will fire, and EXACTLY ONE digest moves.**
   Measured 12:42 by running that file's own `ast_digest` over `readonly.py`
   with the S1 candidate appended, on a string in memory -- the file on disk
   was read and never written:

       _ALLOWED_URL_PATTERNS   34f364971cf9e81c -> 2d0695183ccb5a44   MOVES
       the other six pinned structures and <functions>                UNCHANGED

   **The `2d06...` value is specific to S1 appended at the tail** and will
   differ for another spelling or another insertion point -- recompute it.
   What travels is the shape: a pure allowlist addition moves the allowlist
   digest and nothing else, so a run that moves a SECOND digest means the
   admission was not additive and should be re-read before it lands.
7. **File the normalisation finding** (B.3) as its own row. It is not this
   surface's problem and it is not fixed.

---

## E. WHAT WAS RUN, AND THE TWO REDS THAT ARE NOT THIS WAVE'S

**THE TREE IS 27 RED AND THIS SECTION ORIGINALLY REPORTED A SUBSET.**
`_TEAM_LEAD_GATE_IS_27_RED.md`, written 12:46, records a full-suite run taken
at 12:43 by the lead: **27 failed, 5549 passed, 4 skipped, 1 xfailed**, 24
minutes -- and that every wave today, this one included, ran the files it was
editing and reported that as the gate. **A subset reported as a gate is a
different measurement wearing the gate's name.** The subset numbers below are
kept because they are true of the subset and were named as one; they are not
the gate, and this wave did not measure the gate.

Boundary subset at 12:41, 6 files: **607 passed, 2 failed.** Both failures are
`tests/test_navigation_is_never_derived.py::test_no_navigation_derived_value_reaches_an_output_sink`,
parametrised on `_probe_add_section_menu.py` (a standing red named in this
wave's brief) and `_probe_creator_content_analytics.py` (uncommitted in another
wave's working tree at the time of the run). **Neither file is this wave's and
neither was touched.**

**That same test DOES cover this wave's probe, and it passes** -- checked by
name at 12:41, 2 parametrised cases, both green. The check matters because a
test that silently skipped the new file would certify nothing about it.

**ONE OF THE 27 WAS ROUTED TO THIS WAVE AND IS FIXED.**
`test_no_tracked_file_carries_a_real_identifier` was red on
`scripts/blast_radius.py` -- the shipped instrument this wave imports -- with
3 unallowed slug hits and 0 declared. **A red on that guard means UNDECLARED,
never real.** Repaired in the order the lead's downlink sets: renamed to a
sanctioned token rather than declared, and the blast-radius verdicts measured
on both sides of the rename and shown identical (corpus 67, admitted 12, newly
1, undefended set, all unchanged up to the renamed string). Green at 12:49,
and `sweep_tracked_for_identity` passes 0 hits across 465 files.

The other red in that same file -- `REGIONS` in
`_probe_creator_content_analytics.py` -- and all five files under
`test_page_text_is_never_printed` belong to other waves and were not touched.

    identity sweep 12:49     PASS, 0 hits across 465 swept files
    ASCII                    all four artifacts, no byte above 127
    readonly.py              0 lines changed, 32 patterns before and after
    commits                  read `git log`; the count is deliberately not
                             written here, because this repository has watched
                             every count in prose go stale including the ones
                             written by the wave fixing the last. One touches
                             scripts/blast_radius.py, on the lead's routing in
                             _TEAM_LEAD_GATE_IS_27_RED.md; no other touches a
                             file another wave owns.
    AI attribution           0

---

## F. A SECOND WAVE DISCHARGED THE SAME TWO CONDITIONS, ONE MINUTE APART

Found at 12:45 by reading `git log`, not by any message.
`17733f1 guard(search): pin the blast radius BEFORE the search admission
pattern exists` adds `tests/test_search_admission_blast_radius.py` and is
another wave's answer to conditions 3 and 4. It was committed at 12:45:00; the
first of this wave's commits landed at 12:39.

**There is no code conflict.** The two files touch nothing in common and pass
together -- 21 tests, 0.18s, run at 12:45. `readonly.py` is untouched by both.

**There are three substantive disagreements, and they are the lead's to
settle rather than either wave's:**

**1. THE SIBLING'S GUARD FORBIDS THREE OF THIS BLOCKER'S OWN ROWS.** Its
`MUST_STAY_REFUSED` set lists `/search/results/groups/`,
`/search/results/events/` and `/search/results/companies/` as addresses that
must be refused *after* the admission. But `N 161` and `M C70` are groups rows
and `N 179` is an events row, all three assigned to `SEARCH-RESULTS-SURFACE` in
`_audit/_census/blocker-assignments.tsv` -- so that guard, as written, would
forbid serving 3 of the 20 reads it exists to unblock.

   **It is not wrong; it is CHOICE-DEPENDENT and presented as durable.** Under
   S1 (people only) every line of it holds. Under S2b it contradicts the census.
   A guard whose truth depends on a decision nobody has made yet should say so.
   (`companies` is the one that holds either way -- see the correction in A.1.)

**2. DELETE OR REWRITE?** This wave's revert test says the admitting wave
**deletes** it, so the rollback is a recorded decision. The sibling's says its
file is **rewritten and inverted**, so it keeps both directions. Both are
defensible and they cannot both be followed. **Pick one before the admitting
wave reads two contradictory instructions at 2am.**

**3. THE TARGET SET DIFFERS.** The sibling's `ADMISSION_TARGETS` is two urls --
people and the blended `all` tab. This wave's is eight, and includes the
filter-query shape that 13 of the 16 people rows actually need.

**WHAT IS NOT IN DISPUTE**, and it is most of it: nothing is admitted, nothing
is fired, `readonly.py` is unchanged, and both waves refused to land the
pattern without the shaper.
