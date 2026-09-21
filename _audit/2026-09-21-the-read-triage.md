# The read rows are GATED, not backlogged -- but nineteen of the fifty-nine are not

**CORRECTS:** `_audit/_census/network.md` -- nine cells whose stated reason is measurably false at HEAD: rows `33`, `53`, `54`, `79`, `99`, `100`, `102`, `104` and `132`, each corrected in place.

**CORRECTS:** `_audit/_census/profile.md` -- row `K8`, whose reason cell reads "no tool, no reason" when the reading exists and was taken at allowlist +0.

**No state moved on any of the ten**; the GAP total is 285 before and after, re-measured by the shipped counter with `--expect J=57,P=55,M=82,N=91`.

**CORRECTED BY:** `_audit/2026-09-21-the-fourteen-fired.md` -- **the sentence above is still true of THIS wave and its `--expect` command is now stale.** That wave fired the people-search surface live and moved `N 83` GAP to COVERED-PROVEN, so the counter's current expectation is `--expect J=57,P=55,M=82,N=90` and the census total is 284. Nothing here is retracted: this wave moved no state, which is what it claimed. It also identified rows `80`-`94` as sharing row `79`'s expired blocker and could not re-price them because it was forbidden the browser; that is the gap the successor closed.

Wave `read-triage`, 2026-09-21, from master `f80ee02`.
Scope: the **59 READ-direction GAP rows** of `_audit/_census/profile.md` (17)
and `_audit/_census/network.md` (42).
**No browser was opened. No LinkedIn page was loaded. No session was touched.
No write was fired.** Every measurement is offline: the shipped predicate
`readonly.is_read_url` driven in-process, the shipped census instruments, and
committed source.

---

## 0. THE ANSWER TO THE QUESTION, FIRST

The sibling messaging wave found that of its 12 read rows, **not one is blocked
on a reader somebody could sit down and write.** I was asked whether that holds
across profile and network.

**IT HOLDS FOR PROFILE. IT DOES NOT HOLD FOR NETWORK, AND THE REASON IS DATED:
the boundary moved on 2026-09-20 and nineteen rows have been sitting behind an
expired blocker since.**

    verdict        profile   network   total    what it means
    BUILDABLE            1        18      19    a shipped tool already reaches the
                                                payload, or a reader over an
                                                ALREADY-ADMITTED address would
    ADDRESS             10         5      15    the surface exists, nothing admits it
    RULING               2        16      18    somebody has to decide something
    PRESS                3         2       5    behind a control this package does
                                                not sanction clicking
    SERVED               1         1       2    reachable today; the row is stale
                        17        42      59

So: **38 of 59 are gated** -- 15 on an address, 18 on a decision, 5 on a press.
**19 are build work**, and 16 of those 19 are one surface admitted five days
ago whose rows nobody went back to re-price.

**THE HONEST SHAPE OF THE 19, because "buildable" is doing two different jobs
in that column and a lead scheduling from it should know which:**

    BUILT AND UNFIRED -- the tool ships; what is missing is one browser slot   14
    A READER, OVER AN ADMITTED ADDRESS, THAT NOBODY HAS WRITTEN                 5

Fourteen of the nineteen need **no code at all**. They need somebody to open
one page with the signed-in profile.

---

## 1. THE DENOMINATOR, RE-DERIVED RATHER THAN ACCEPTED

The brief handed me 17 and 42. I re-derived both by importing
`scripts/count_census_states.py` instead of trusting them, because a number one
agent hands another is a reading with a timestamp the receiver cannot see.

    profile.md   GAP  55    of which direction R   17     R/W 1   W 37
    network.md   GAP  91    of which direction R   42             W 49
                                                   --
                                                   59

Both match. The direction column is read **by value** using the shipped
`reader_closable_blockers.direction_of`, not positionally -- the R/W cell sits
at `c[2]` in these two slices and at `c[4]` in messaging, and a positional
reader has already reported a Help Center reference as a direction.

The whole-census figure is unchanged at **GAP 285 of 704 stated rows**.

### 1.1 A SHIPPED INSTRUMENT COULD NOT RUN IN A WORKTREE, AND THAT TOOK DOWN THE TRIAGE

`scripts/reader_closable_blockers.py` -- the instrument whose whole job is
"which live blockers could a reader actually close" -- **died on its first line
in this worktree**, and so did every report downstream of it:

    FileNotFoundError: [WinError 2] The system cannot find the file specified

`scripts/enumerate_gap_rows.py :: control` re-runs the shipped counter as a
subprocess and spelled the interpreter `root / "venv" / "Scripts" /
"python.exe"`. **`venv/` is gitignored, so it does not exist in any linked
worktree** -- which is the only tree a fan-out wave has. Not a soft skip: the
instrument could not report at all.

Repaired here to `sys.executable`, which is the right answer rather than merely
a working one: the control's job is to re-run the shipped counter **over this
tree**, and `count_census_states.py` imports nothing outside the standard
library, so the interpreter is not part of what is being measured. Reaching for
a named venv asserted a dependency this control does not have.

**SHOWN FAILING, BOTH DIRECTIONS, on the same tree:** before the repair,
`reader_closable_blockers.py` raised and printed no table; after it, all four of
its own controls pass and it prints 285 GAP rows with 71 reader-reachable
(59 here + 12 messaging). The evidence is the traceback above and the run in
section 7.

`scripts/pre_commit_boundary_gate.py` already solved the same problem the other
way -- `_tooling_root()` off `--git-common-dir` -- and its comment names this
exact case: *"absent in EVERY linked worktree, which is not an infrastructure
case at all."* That fix is correct THERE because that gate runs pytest and
genuinely needs the installed environment. **The knowledge existed in this
repository and had not reached the file next door.** Three other tracked
scripts carry the same spelling and are reported unfixed in section 6.3.

---

## 2. THE NINETEEN. WHAT A READER WOULD READ, ROW BY ROW

### 2.1 Sixteen rows behind a blocker that expired on 2026-09-20

`_audit/_census/network.md` row 79 states the blocker for the whole run:
*"no `/search/results/` pattern; the only `/search` pattern is
`/jobs/search/`."*

**Measured 2026-09-21, in-process:**

    readonly.is_read_url("https://www.linkedin.com/search/results/people/")
        -> True

The admission landed 2026-09-20 **with** its shaper
(`linkedin_server/search_results.py`) and its tool
(`linkedin_people_search_shape`), because condition 1 of the granting ruling is
that admitting without the shaper *"does not partially satisfy it, it violates
it."*

**FOURTEEN ROWS ARE SERVED BY CODE THAT SHIPS TODAY.** The shaper carries a
census map in source, `search_results.FILTER_TERM_ROWS`, positionally aligned
to `FILTER_TERMS`, and I read it out of the loaded module rather than off the
page:

    FILTER_TERMS      14 entries
    FILTER_TERM_ROWS  14 entries
    rows served       N 80 N 81 N 82 N 83 N 84 N 85 N 86 N 87
                      N 88 N 89 N 90 N 91 N 92 N 93

**WHAT A READER WOULD READ.** `linkedin_people_search_shape()` takes no
parameter, opens `search_results.PEOPLE_SEARCH_URL` with no query, and returns
`filters.by_term` -- a COUNT per term, matched inside the page against a
vocabulary shipped in, so no label crosses the boundary -- plus
`filters.by_value_class`, `results.by_kind`, and a `denominators` block that
distinguishes *"this page offers no filters"* from *"the selector changed"*.
Fourteen of these rows ask which filters the search offers. That is the exact
payload.

**WHAT IS ACTUALLY MISSING, AND IT IS NOT CODE.** The tool has never met the
live surface. Its own payload says so in `not_claimed`: *"that this classifier
has ever met a live search page; no capture of this surface exists and its fit
to LinkedIn's rendered dialect is unmeasured."* The admitting wave deliberately
did not bank the rows on that basis -- *"banking them on that basis would be
the over-claim"* -- and named what remains as **one browser slot**: open the
address once, read `landed_where_it_was_sent`, read `unmatched_controls`, build
a capture-then-scrub fixture PAIR (before and after settle, both committed,
never normalised into one).

**So these fourteen are BUILT AND UNFIRED. A build wave has nothing to do here.
A browser slot closes them or refutes them, and `denominators` is designed so
that a refutation is visible rather than silent.**

### 2.2 A DEFECT IN THAT SHAPER'S OWN PROSE, found by measuring it

`search_results.py` says twice that it serves *"`N 80`-`N 94` -- sixteen
consecutive FILTER rows"*. **Both halves are wrong and the second one matters.**
`N 80..N 94` inclusive is fifteen rows, not sixteen; and `FILTER_TERM_ROWS`
holds fourteen, stopping at `N 93`. **`N 94` has no term.**

That is not my opinion about the row -- it is the module's own rule applied to
its own table: *"a term that serves no row is a term nobody asked for; a row
with no term is a row this shaper cannot serve, and both are findings rather
than opinions."* `N 94` asks to put **more than one location** in a single
search, which is a multi-valued query on a tool that sends no query at all.
Filed RULING with `N 79`, not BUILDABLE with its neighbours.

The prose is left as found and reported here. Editing a shipped module's
comment on a triage wave's authority is how a comment stops being a standing
instruction.

### 2.3 `N 33` and `N 54` -- the Page root is admitted and nothing opens it

    readonly.is_read_url("https://www.linkedin.com/company/<numeric id>/") -> True
    readonly.is_read_url("https://www.linkedin.com/company/<slug>/")       -> True

Both rows render on that root. **No reader opens it**: `company_page.py`'s own
docstring says *"It opens nothing. There is no page function here"*, and the
allowlist entry agrees -- *"No tool in this package navigates to this address
today."*

And the address can be reached **without assembling a name**:
`linkedin_job_detail` now returns `company_page_url`, built by
`company_page.company_page_url` from a NUMERIC organisation id read off the
posting's insights panel. *"A slug is a name and a digit run cannot be one"*;
the builder refuses anything but ten ASCII digits and reports the SHAPE rather
than the value.

**WHAT A READER WOULD READ:** the connection-count lines on
`/company/<numeric id>/`, opened from an address a shipped tool already
publishes. It owes a COUNT and never a list -- the same discrimination that
banked `N 101` as CANNOT-DELIVER rather than PROVEN, *"a tool that reports HOW
MANY does not cover a row asking WHICH."*

**AND ONE ROUTE IS MEASURED DEAD, which is worth as much as the two that are
open.** `_audit/2026-09-20-company-page-built.md` dumped
`dom.read_job_insight_panels` whole over both hydrated captures: the applicant
panel gives applicant counts, seniority and education; the company panel gives
headcount, growth and tenure; **no line in either names a connection.** These
cannot be lifted off the posting the way `N 53` was, and that hour is already
spent.

`N 33` has a second, independent route named before the boundary moved:
`linkedin_connections` returns one row per connection over an admitted address,
and `_audit/2026-09-19-the-read-rows.md` calls the aggregation *"the cheapest
genuine BUILD left in this set."*

### 2.4 `N 175` -- an admitted address no tool can navigate to

    readonly.is_read_url("https://www.linkedin.com/groups/<id>/") -> True

The row is *"reach a private unlisted group through a direct link or an
invitation"*, and the direct-link half is that address with a caller-supplied
id. **Every tool on this surface takes no parameter.**
`linkedin_group_memberships()` opens `groups_page.GROUPS_URL` -- the root -- and
nothing else, so a group id has nowhere to go.

**WHAT A READER WOULD READ:** the group page at `/groups/<numeric id>/`, id
supplied by the caller. `groups.group_identifier` already exists, caps an
identifier at 20 digits, and refuses a path carrying both a group and a member
segment as FOREIGN.

**AND THE ALLOWLIST ENTRY STATES THE OBLIGATION THAT COMES WITH IT**, which is
quoted here rather than paraphrased because it is the whole cost of this row:

> `/groups/<id>/` DRAWS A GROUP FEED -- other members' posts in full. This list
> decides what may be OPENED and the shaper decides what may be SAID, and today
> there is no reader and therefore no shaper. **Whoever writes the first reader
> for this address owes it a shaper as strict as the search-results one.**

This is BUILDABLE with a named, non-trivial price. It is not a cheap row.

### 2.5 `N 134` and `P O3` -- the ruling was granted, the guard was built, and nobody wired it

These two have the most moving parts and every one of them is now in place.

    condition                                     status at HEAD
    the address is admitted                       /analytics/profile-views/ -> True
    the press is ruled permitted                  RULED 2026-09-19, "PERMITTED"
    the guard that bounds the ruling exists       linkedin_server/press.py, disclose()
    a sanctioned shape is present on the page     [aria-expanded] x9, measured live
    the press is priced by outward counters       two, both read, neither moved
    the DISCLOSURE WITNESS exists                 press.WITNESS_SELECTORS,
                                                  press.witness_verdict, _read_witness

That last line is the one that changed. On 2026-09-19 the first sanctioned
press was permitted, safe, and **blind**: `expanded_after` was read AFTER the
Escape, so *"a successful Escape guarantees that equality whether or not
anything ever opened. The gate takes exactly two readings, and both are outside
the open state. Two readings cannot describe three states."* That document
named the next artifact precisely -- **(1) a disclosure witness, (2) a name-free
shaper for whatever the panel draws** -- and said *"the witness is the harder
half and it is the one worth building first."*

**The harder half is built.** `press.disclose` now reads a witness before and
after and returns `witness_verdict(...)`, and the witness rides alongside the
verdict rather than becoming a fifth condition.

**AND `press.disclose` HAS NO CALLER IN THE PACKAGE.** Measured: it is called
from `scripts/_probe_first_sanctioned_press.py` and from two test files. Zero
`@mcp.tool()` functions reach it.

**WHAT A READER WOULD READ:** `/analytics/profile-views/` -- which
`linkedin_who_viewed_me` already loads -- press the one unpressed control
(`_audit/2026-09-20-the-premium-block.md` measures *exactly one* on that render,
`analytics-section-show-more`) through `press.disclose`, and read the disclosed
panel through a name-free shaper. The notable-viewers panel is made of other
people, so that shaper is the second half and is not optional;
`linkedin_who_viewed_me` already states the resolution it must hold --
*"numbers, filter labels, the chart's own sentence and COUNTS of page regions,
and nothing else."*

**ONE THING THIS DOES NOT COVER, and it is the neighbouring row.** `N 133` is
*filter* your viewer data, and applying a filter **submits**. The ruling refuses
submits by name -- *"Anything that navigates, submits, or opens a composer or
editor"* -- so `N 133` is a PRESS row, not a BUILDABLE one, and it is the
neighbour most likely to be swept in by accident.

---

## 3. THE TWO ROWS THAT ARE ALREADY SERVED

### 3.1 `N 53` -- view a Page's follower count. SHIPPED, AND THE BLOCKER IS FALSE TWICE OVER

Recorded blocker: *"No `/company/`"*.

1. `/company/<slug>/` **has** been admitted since 2026-09-20.
2. **The row never needed it.** The count comes off the job posting:
   `linkedin_job_detail` -> `dom.read_company_about_card` ->
   `shape.company_about_card` -> `followers`, parsed by
   `shape._ABOUT_FOLLOWERS`, published under `company_about`. The posting
   address has been admitted since the first commit.

I followed that chain in source rather than accepting it relayed.
`tests/test_company_about_card.py` asserts an integer follower count and
asserts `None` in both unhydrated states -- so an unhydrated card cannot read as
*"this employer has no followers."*

`_audit/2026-09-20-company-page-built.md` found the same thing five days ago
and filed it *"SHIPPED, pre-existing"* -- **and the census row was left carrying
the refuted blocker.** A finding that lands in a document and not in the row is
a finding the census cannot see.

**WHAT STANDS BETWEEN THIS AND A BANK, stated so nobody banks it on my
sentence:** no committed record shows `followers` POPULATED in a live fire. The
2026-09-19 fire that populated `company_about` is cited on `N 101` for
`on_linkedin`, a different key. That is one re-read of an artifact that already
exists, not a build and not a browser slot.

### 3.2 `P K8` -- Top Voice badge. "no tool, no reason" is half false

The reading exists, it was taken at **allowlist +0** on the already-admitted
`/in/me/`, and it is better than most: `top voice` reads **0 in the text corpus
and 0 in the accessible-names corpus**, on an instrument shown able to disagree
with itself on the same page (`premium` 0 in text and 19 in names; `verified` 4
and 5). A double zero from an instrument that can split is a reading; a double
zero from one that cannot is a dead needle, and that discrimination is the
whole value of the control.

The *"no tool"* half is true and separate: `Top Voice` and `top_voice` occur
**zero times** in `linkedin_server/`.

**NO STATE MOVED, AND THE REASON IS NOT TIMIDITY.** The obvious move is
MEASURED-ABSENT. That state is a claim about a SURFACE, the reading is sixteen
days old, and this wave was forbidden the browser. Naming it as a candidate
with its evidence costs the next holder of the signed-in profile one re-read;
banking it from here would be asserting a live fact from an offline chair.

---

## 4. THE DECISIONS NOBODY HAS MADE

Named as decisions, not as rows. Six, covering 18 of the 59.

### D1 -- MAY A SEARCH KEYWORD BE PASSED? (`N 79`, `N 93`'s needle half, `N 94`, `N 194`)

`linkedin_people_search_shape` takes no parameter **by design**: *"A keyword is
where a name is typed [...] so no needle can be handed to it, by a caller or by
a mistake."* The allowlist pattern admits a query SHAPE so the address stays
usable *"if a later wave rules that a keyword may be passed. Nothing today
passes one."*

The decision is already costed and the price is specific rather than vague:
`_audit/2026-09-19-search-admission-preconditions.md` B.4 measures that **8 of
11 ordinary search keywords** (`password`, `settings`, `invitation` ...) are
refused by the forbidden-substring list. **A keyword-taking tool must decide
what to answer when a caller's ordinary word trips a write guard** -- and
"taking no keyword dissolves that question instead of answering it" is what the
shipped design chose.

### D2 -- WIDEN THE SEARCH ADMISSION BEYOND THE PEOPLE VERTICAL? (`N 104`, `N 161`, `N 179`)

**I am the later wave the reopening clause describes**, so this is filed as the
request it invites rather than as a complaint:

> a later wave showing the narrow pattern is TOO narrow to serve the 20 rows,
> which is a request to widen it and gets its own blast radius, not an
> extension of this one.

**THE MEASUREMENT THAT MAKES IT A REQUEST:** the people-only pattern serves 14
of the blocker's 20 reads. `N 104` needs `/search/results/companies/`, `N 161`
needs `/search/results/groups/`, `N 179` needs `/search/results/events/`. All
three measure `is_read_url` **False with zero forbidden substrings** -- refused
by allowlist silence, not by any rule anybody wrote.

`N 161`'s refusal is written down and is explicitly deferred to this decision:
`readonly.py`'s groups entry lists `/search/results/groups/` among what it does
not inherit, *"belongs to SEARCH-RESULTS-SURFACE, which is queued DECIDE and is
not this entry's to inherit."* **That DECIDE has since happened -- for people
only** -- so the row is waiting on a narrower and better-specified thing than
its cell says.

The blast radius is already tabulated: people-only newly admits 5 addresses;
`people|groups|events` admits 7; a `/search/` wildcard admits 18, including a
traversal whose normalised form is an account-ending address that **no
forbidden substring names**. The closed-segment spelling is what refuses that,
not the anchor.

### D3 -- DOES A REASONED ALLOWLIST REFUSAL COUNT AS "WRITTEN"? (`N 99`, `N 172`, `N 177`, `N 178`)

**THIS DECISION IS NOT MINE AND IT IS NOT NEW.** `_audit/2026-09-19-the-read-rows.md`
section 5.2 filed it, called it *"the single highest-yield decision left in this
row set"*, and named the five rows it banks at once (four of mine plus
`M C83`). **A search of every document under `_audit/` finds it named in
exactly one: the one that filed it.** Nobody has answered it in two days.

The question: the census's CANNOT-DELIVER definition names four qualifying
sources -- a `_FORBIDDEN_URL_SUBSTRINGS` entry, a `writes.PERMANENTLY_FORBIDDEN`
key, a `WriteSpec` refusing in its own words, or an audit passage measuring the
capability unreachable. **A reasoned refusal written into the allowlist itself
is not on that list**, and these four rows sit on exactly that -- the
member-roster cause, stated in `readonly.py` in its own words and measured true
(the school and company `/people/` tabs carry **zero** forbidden substrings, so
the anchor is the entire refusal).

I re-file it unchanged rather than re-argue it. A wave inventing an answer here
to move four numbers is the worst available outcome.

### D4 -- MAY THIS PACKAGE CREATE ITS OWN BROWSER CONTEXT? (`P C8`)

Save-profile-as-PDF is not blocked on a press or an address --
`https://www.linkedin.com/in/me/` is already admitted, so the row carries no
boundary cost. It is blocked on **transport**, and there is a committed test
that pins why, `tests/test_profile_pdf_download_is_blocked_on_transport.py`:

> In ATTACH mode this package NEVER CREATES A CONTEXT. `cdp_bridge` does
> `contexts = list(client.contexts)` and returns `contexts[0]` verbatim.
> `accept_downloads` is a CONTEXT CREATION OPTION [...] *"not 'nobody wrote it
> yet', but there is nowhere to write it."*

The decision is whether this package may create a context rather than attach to
the operator's -- which changes the session model the whole server is built on.
**It is a decision with a real cost, which is why it is stated rather than
routed around.**

### D5 -- IS A PASSIVE COST A CAPABILITY ROW? (`N 171`, and `N 183` in a second costume)

`N 171` is *"expose your profile to every member of a group you join"*. The
census's own note says it: *"a cost of joining, not an action."* Nothing reads
it, nothing presses it, no address serves it -- **it is a consequence of an act,
and this server's act-classes have no slot for one.**

`N 183` is the same shape wearing settings clothes: *"receive event invitations
only from your 1st-degree connections"* is a preference value, and
`readonly.py`'s `/events/` entry classes it outright as a SETTING *"which lives
under preferences and not here."* The standing settings ruling
(`linkedin_update_setting`: *"a setting is admitted by name or not at all"*) is
what governs R11 in this very slice and the messaging slice's
MESSAGING-SETTINGS. **Whether it reaches this row has never been decided**, and
if it does the row is EXCLUDED-RULED rather than GAP.

Cheap to rule; it retires two rows and gives the census a vocabulary for the
next cost it meets.

### D6 -- DOES TWO ADDRESSES DISCHARGE A ROW NAMED FOR A CONTROL? (`N 132`)

`N 132` is *switch between* Search appearances and Who viewed your profile.
Both sides are reachable today by two shipped tools over two admitted
addresses. The row's own cell concedes the situation and stops: *"each is
reached by its own address here rather than by pressing a control. Nothing in
this package presses that switch, and nothing needs to."*

**What is unbuilt is the control, and only the control.** Whether a capability
this package delivers structurally by two addresses discharges a row named for
the affordance that switches between them is a census convention nobody has
ruled -- and it does not govern only this row. It governs every row named for
an affordance this package replaces rather than reproduces.

### And one that is NOT a decision, stated because it looks like one

**`N 174`** -- view the groups you have requested to join -- is unmeasurable by
any read on this account's current state, and the census already says why: a
pending request must exist for the surface to be observable at all, and
creating one is a **WRITE at a real group**. It is filed RULING because the
only thing that changes it is somebody deciding to fire that write; it is not a
reader, an address or a press. The row's refusal to retire on a comfortable
zero is correct and is left alone -- *"a reading no instrument can fail is not a
reading."*

---

## 5. THE OTHER FORTY, IN ONE TABLE

Verdict, the binding gate, and for ADDRESS rows whether the address is
**REFUSED** (a forbidden substring names it -- it fires BEFORE the allowlist, so
the row needs a pattern AND an exemption) or **ABSENT** (no pattern names it and
nothing refuses it either). The census has repeatedly recorded one as the
other, and they are different costs.

Every address below is written with a placeholder segment. The measurements are
`readonly.is_read_url` run in-process on this tree, 2026-09-21.

| row | verdict | the binding gate |
|---|---|---|
| `P A25` | PRESS | entry control declares no `aria-expanded`, no `aria-haspopup`, no `aria-controls` -- **OFF `press.SANCTIONED_SHAPES`**, so the ruling cannot reach it. A listener table shows a `click` handler, so it is wired and undeclared; *"whether the handler WRITES is not determinable from a listener table."* The overlay address is unadmitted in BOTH the self and third-party spelling |
| `P C8` | RULING | D4. Address already admitted; no boundary cost |
| `P D25` | ADDRESS / ABSENT | measured `is_read_url` False with `forbidden_tokens_present []`. **UNDECLARED, NOT FORBIDDEN.** The row itself records what is owed: the operator naming the address, because reading it off the page is navigation derived from page content, which this repository forbids |
| `P D28` | PRESS | measured `distinct_langs 1`, `langs_other_than_document 0` -- and the measuring document self-limits: *"It does not prove a pressable control exists, and I did not press anything"* |
| `P F1` | ADDRESS / ABSENT | the `/in/me/details/` admission is restricted to `experience`, `education`, `skills`; the recommendations spelling is refused in BOTH the self and third-party form. **`recommendations.py` ships and is FULLY UNWIRED** -- the shaper exists, the address does not. Cheapest ADDRESS row in this slice |
| `P G6` | ADDRESS / ABSENT | no per-post analytics address admitted, and no module builds one from a urn -- `item_addresses.py` runs the other way (it PARSES an href that exists) and says *"This module does not admit that address and does not open it"* |
| `P H11` | ADDRESS / ABSENT | the services detail address is unadmitted. The phrase lives in `shape._TOPCARD_CHROME`, an EXCLUSION set -- it is actively discarded as furniture before the topcard is parsed |
| `P J4` | PRESS | the hiring state is behind the Open-to menu. Measured twice, fourteen days apart, in independent sessions, on every number: `hiring` NAMED BUT INERT (0 activation relations), the opener AMBIGUOUS (5 named, 3 with a relation). *"The next step is still not a press."* The menu was separately measured to hold three OPTIONS, none of them a state |
| `P K8` | SERVED | section 3.2 |
| `P L1` | ADDRESS / ABSENT | `/analytics/creator/audience/` unadmitted and **pinned refused by a committed test** whose own case text reads *"Being drawn by an admitted page is a reason to CONSIDER an address, never a reason to have admitted it"* |
| `P L2b` | ADDRESS / **REFUSED** | every follower-list spelling carries `/follow`. No exemption covers it: the four entries in both exemption tables excuse exactly `/edit/`, `/messaging/compose`, and the `/invite`+`/connect` pair on one address |
| `P L4` | ADDRESS / ABSENT | the newsletter analytics address is named in `readonly.py` among those NOT admitted -- and that entry names a census row **by id**, which is the shape D3 is about |
| `P L7` | ADDRESS / ABSENT | creator hub. The blocker's address is DISPUTED in the corpus and unadmitted under either spelling |
| `P L8` | ADDRESS / ABSENT | same hub, same dispute; the analytics tree root is refused |
| `P M12` | ADDRESS / **REFUSED** | the application-settings address contains `/jobs/application`, the FIRST entry on the forbidden tuple. The sibling row `P M1` already names the reopener and its owner: **the operator re-ruling that entry** |
| `P O23` | RULING | measurable only by firing a profile write and observing another account. `writes.writes_enabled()` is False. The `update_profile_field` docstring already carries it as a named unmeasured cost |
| `N 61` | ADDRESS / **REFUSED** | both followed-hashtag spellings contain `/follow` -- **matching inside the word "followed"**. A substring hit, not a ruling anybody wrote about hashtags. Nothing in the package reads followed hashtags at all |
| `N 76` | PRESS | named by the disclosing-press ruling as one of its four consumers. Nothing has pressed it, and `linkedin_page_plugin_snippet` builds an off-platform widget for a PAGE, which is a different subject |
| `N 79` | RULING | D1 |
| `N 94` | RULING | D1, and section 2.2 -- no term serves it |
| `N 95` | ADDRESS / ABSENT | no search-history address is admitted and none is refused. **Also UNROUTED in the blocker map**, see 6.1 |
| `N 99` `N 100` | RULING | D3. Root ALLOWS, alumni tab REFUSES, tab carries zero forbidden substrings |
| `N 102` | RULING | D3's cause. The entry names this row while refusing it, *"refused by this anchor and by nothing else"* -- measured true |
| `N 104` `N 161` `N 179` | RULING | D2 |
| `N 132` | RULING | D6, and one stale clause corrected in place |
| `N 133` | PRESS | applying a filter SUBMITS; the ruling refuses submits by name. The filter controls were measured RENDERED and UNPRESSED, and they are filters rather than disclosures -- *"the data is simply unfiltered until one is used"* |
| `N 171` | RULING | D5 |
| `N 172` `N 177` `N 178` | RULING | D3. All three need a group's member directory or another member's profile; the boundary's sharpest refusal, *"not admitted here or anywhere"* |
| `N 174` | RULING | section 4's closing note |
| `N 183` | RULING | D5's second costume |
| `N 184` | ADDRESS / ABSENT | **the events family admits the root only.** `/events/` True, `/events/<id>/` False -- one segment narrower than the groups family, which admits `/groups/<id>/`. That asymmetry is pinned by a committed test and is the single reason `N 175` is BUILDABLE and this row is not |
| `N 194` | RULING | D1. Its recorded blocker (*"no people search"*) has EXPIRED; the needle is a hashtag typed into a search, which is a keyword |
| `N A3` `N A5` | ADDRESS / **REFUSED** | `/follow` and `/invite` respectively, firing before the allowlist -- so each needs a pattern AND an exemption, a double cost the census does not record. **And the precondition is unmeasured**, see 6.2 |

---

## 6. THREE THINGS FOUND ON THE WAY THAT ARE NOT ROWS

### 6.1 THREE ROWS IN MY SCOPE ARE UNROUTED, AND THE SHIPPED TRIAGE REFUSES BECAUSE OF ONE

`P L2b`, `N 61` and `N 95` carry no entry in
`_audit/_census/blocker-assignments.tsv`. `N 61` and `N 95` land in the blocker
map's `UNASSIGNED` bucket; **`P L2b` has no row in the map at all**, because it
was split out of `L2` after the map was built and the map still carries the
compound predecessor.

Consequence, measured: `scripts/triage_messaging_gap_rows.py --slice P`
**refuses to print a tally**, on its own coverage control:

    REFUSING: 1 of 55 GAP rows carry no blocker assignment: L2b

That control is doing its job and I did not route around it. Assigning a
blocker needs a COMMITTED SOURCE stating the assignment -- that is what the
`evidence_class` column is for -- and inventing one to make an instrument green
is the failure mode the whole map exists to prevent.

### 6.2 `N A3` AND `N A5` REST ON A PRECONDITION THE REPOSITORY DOES NOT MEASURE

Both are Page-admin rows under `ADMIN-RIGHTS-NOT-HELD`, whose name is a claim:
*"He administers no Page."* The supporting evidence has already been retracted
by the wave that re-read it -- both committed fixtures are a FRAGMENT with no
`<html>`, `<body>` or `<nav>`, every href in both is a company address, `/admin`
appears **0** times, and **an instrument that captured no page chrome could not
have found an admin marker if one existed.**

That retraction is propagated into `network.md`'s own prose. So for the PAGE
family the repository records **no measurement in either direction** -- the
claim is *unsupported*, not refuted, which is a different and more actionable
thing. Both rows stay ADDRESS on their own merits (each address is
substring-refused), and this is recorded so nobody prices them off a blocker
name that asserts more than anybody measured.

### 6.3 THREE MORE TRACKED SCRIPTS CARRY THE WORKTREE-BLIND INTERPRETER PATH

Reported, not fixed -- each needs its own judgement about whether it wants the
CONTENT root or the TOOLING root, and section 1.1's answer (`sys.executable`) is
correct only where the interpreter is not part of what is measured.

    scripts/leak_matrix.py          PY = REPO / "venv" / "Scripts" / "python.exe"
    scripts/purge_denied_term.py    python = REPO / "venv" / "Scripts" / "python.exe"
    scripts/clean_install_check.py  builds its own venv -- this one is correct

`scripts/pre_commit_boundary_gate.py` is **already correct** and is the model:
it takes the TOOLING root deliberately, via `_tooling_root()` off
`--git-common-dir`, and its comment names the worktree case.

---

### 6.4 FOUR GUARDS FIRED ON THIS WAVE'S OWN OUTPUT, AND ALL FOUR WERE RIGHT

Recorded because a wave that reports only what it found, and not what caught
it, is reporting half a run. The full suite went **5 failed, 7360 passed**
before any of this was addressed; every one of the five was mine.

**1. THE CORRECTION MUST BE FINDABLE FROM THE CLAIM.**
`tests/test_a_correction_is_findable_from_the_claim.py` refused a `CORRECTS:`
marker with no `CORRECTED BY:` back-pointer in the corrected file. It also
produced **8 candidate pairs** for triage, and the triage is the point: seven
are a corrector paired with its EVIDENCE or a back-pointer read from the wrong
end, and each is now on `NOT_A_CORRECTION` with the reason, written after
reading the line. **A marker naming TWO documents on one line declared only
one** -- the parser takes one target per marker -- so the fix was two markers,
not a longer one.

**2. A POINTER CELL IS NOT A DEFECT TO TIDY AWAY.**
`tests/test_pointer_graph_guard.py` caught `N 100` leaving the pinned pointer
graph, because my first edit began the cell `~~Same~~` and the detector anchors
on `^\**same\b`. Restored as a pointer, with the reason written into the cell.

**3. AND THEN IT CAUGHT THE THING THE PIN IS ACTUALLY FOR.** With the pointer
restored, the guard reported `DONOR VERDICT MOVED`: `N 100` still points at
`N 99`, but `N 99`'s write-off kind moved `-` (unclassifiable) to `US-BOUNDARY`
**because I corrected the donor**. That is the correction landing -- the row's
real blocker IS our own anchor and the cell now says so -- and it changed a
dependent row's inherited argument without that row being edited, which is
exactly the class the pin exists to make visible. **Re-pinned deliberately**,
as the guard's own failure text instructs, and said here and in the commit
message rather than only in a tsv diff.

**4. A NEW DOCUMENT CAN LOOK LIKE A LOCATOR REGRESSION.**
`tests/test_the_blocker_reason_locator_states_its_recall.py` dropped from 7 of
8 hand-found documents in the top 3 to 6, and the obvious reading -- the
locator got worse -- is wrong. Measured: this document and
`_audit/2026-09-19-search-shaper.md` **both score 5.000** for
`SEARCH-RESULTS-SURFACE`, and the shaper document fell to rank 4 **on an
arbitrary tie-break**. The floor was NOT lowered; the hand-found set grew by
one, which is the honest move, and the tie is now written into that test as a
property of the measurement. **A `top3` floor is sensitive to tie-break order
whenever a new document lands on an existing score**, and nobody had said so.

**AND ONE THING I DID NOT FIX, reported as found.**
`test_no_generated_artifact_is_ever_a_candidate` names `blocker-map.tsv`; the
locator's candidate list for `SCHOOL-PAGE-SURFACE` currently ranks
`_audit/_census/pointer-graph.tsv` at 4 and `blocker-assignments.tsv` at 6.
`pointer-graph.tsv` is written by `scripts/measure_pointer_graph.py --pin` and
is as generated as the file that test names. That is a pre-existing gap in a
guard I did not write, in the same family as this document's 45.9 note, and
widening somebody else's guard on a triage wave's authority is not a trade I
will make in passing.

---

## 7. EVIDENCE: EVERY NUMBER HERE IS RE-DERIVABLE FROM A CLONE

| claim | re-derive with |
|---|---|
| 59 read-GAP rows, 17 + 42 | `python scripts/triage_read_gap_rows.py` |
| the five verdict integers | same, and it REFUSES unless its key set equals the census-derived read-GAP set |
| the instrument can fail | same, `--plant drop-a-row`, `--plant bad-verdict`, `--plant stale-census` -- all three exit 1 |
| GAP 285 unchanged by my cell edits | `python scripts/count_census_states.py --expect J=57,P=55,M=82,N=91` |
| 71 reader-reachable rows across four slices | `python scripts/reader_closable_blockers.py` -- which could not run in a worktree before this commit |
| every address verdict | `readonly.is_read_url` on a concrete url, never a substring grep over the patterns |
| the 14 rows the shaper serves | `search_results.FILTER_TERM_ROWS` read out of the loaded module |
| `N 94` has no term | the same tuple, 14 entries against a claimed span of 15 |
| the witness exists | `press.WITNESS_SELECTORS`, `press.witness_verdict`, `_read_witness` in `press.disclose`'s source |
| `press.disclose` has no package caller | grep for `disclose(` across `linkedin_server/`, `scripts/`, `tests/` -- probe and tests only |

**WHAT I DID NOT ESTABLISH, stated because the alternative is that somebody
reads a verdict as a fire:**

* **No live reading of anything.** Every statement about a rendered LinkedIn
  page is quoted from a measurement somebody else took and dated.
* **ALLOWED IS NOT SERVED.** Every BUILDABLE verdict is a claim about an
  address and a shipped reader, never a claim that the page draws what the row
  wants. `/in/me/details/interests/` is this repository's own standing proof:
  admitted, and it redirects.
* **I did not verify that any tool would still work today.**
* **No state moved, on any row, in either slice.** Ten cells carry a correction
  and the GAP total is identical before and after.

---

## 8. THE LEDGER LINE

    read-direction GAP rows triaged                          59
    rows banked to COVERED-PROVEN                             0   needs a fire
    rows moved to COVERED-UNFIRED                             0
    rows moved out of GAP                                     0
    rows inflated                                             0

    census cells corrected with a MEASUREMENT                10   state unchanged on all 10
    decisions named that nobody has made                      6   covering 18 rows
    decisions RE-FILED unchanged from a prior wave            1   D3, unanswered for two days
    defects found in a shipped instrument                     1   and fixed: section 1.1
    defects found in a shipped module's prose                 1   reported, not edited: 2.2
    instruments shipped                                       1   shown failing three ways
    rows unrouted in the blocker map                          3   reported, not assigned
    guards that fired on MY output                            4   all four right: 6.4
    guard floors lowered to pass                              0
    pointer-graph re-pins, deliberate and stated              1

**THE ONE-LINE READING. Thirty-eight of the fifty-nine are gated -- on an
address, a decision, or a press -- and the messaging wave's sentence holds for
every one of them. The other twenty-one are not, and they are concentrated in
one place: a surface admitted on 2026-09-20 whose sixteen rows nobody went back
to re-price, plus two rows a build wave already found shipped and left carrying
a refuted blocker. Fourteen of the nineteen BUILDABLE rows need no code at all
-- they need one browser slot.**
