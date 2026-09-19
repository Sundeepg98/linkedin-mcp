# The content tail: three rows banked, and four cost corrections that all run the same way

**CORRECTS:** `_audit/2026-09-05-article-publish.md` -- its section 5 address table reports `/article/new/` and `/feed/` as True on BARE PATHS, but `is_read_url` matches absolute `https://www.linkedin.com/...` spellings only and returns False for both bare forms; the ten verdicts are unchanged when re-measured with absolute spellings, so this corrects a transcription and not a conclusion. Detail in section 5.

Wave `content-tail`, 2026-09-19, 08:31 to 09:5x by the box (`date`, stamps in
section 7). Six blockers, ~17 rows. Nothing pushed. **No page was loaded, no
browser attached, no write fired, and the boundary was not moved.**

Numbers RECOMPUTED at freeze rather than re-read: `_ALLOWED_URL_PATTERNS` **32**,
unchanged by this wave; the new instrument **8 passed**; the shipped identity
sweep taken AT THE GATE, not at the start; AI attribution verified per commit.

## 1. THE HEADLINE: A WAVE EARNED TWO ROWS AND DELIBERATELY DID NOT BANK THEM

`_audit/2026-09-05-article-publish.md` ruled `C10` (mention in a post) and `C28`
(mention in a comment) EXCLUDED-RULED, on the operator's typing ruling, and
then said so plainly in its own section 8:

> **No ledger edit.** Sections 2 and 4 specify moves; none is applied. Anyone
> quoting a new row count off this document is quoting an intention.

That was the correct call for that wave -- it was 45 minutes over six blockers
and an unapplied move is honest where a half-applied one is not. **But an
intention left in an audit document is exactly the thing this repository has
now named twice**, most recently as that same wave's closing law: *a ruling not
attached to the row it decides gets re-derived.* Two weeks later the rows still
read GAP, and the next reader of `C10` would have started from zero.

**Applied here: `C10`, `C28`, and `C55`.** Three rows move GAP ->
EXCLUDED-RULED. The count is small and the mechanism is the point.

## 2. `C55` IS THE ONE THAT WAS NOT ALREADY RULED, AND IT RETIRES ON SHIPPED CODE

The mention ruling reaches a mention. It was never asked about a COLLABORATOR,
and the collaborative rows sat in a different blocker.

**It did not need to be asked. The assertion was already shipped.**
`tests/test_no_write_tool_names_a_third_party.py` carries `collaborator` and
`collaborators` in `FORBIDDEN_PARAMETER_NAMES` -- a tested, shown-failing
promise that no publishing tool takes a parameter whose value is another
member. `C55` is *manage collaborators on a collaborative post*: inviting a
named collaborator carries a third party's identity into content this server
publishes, and LinkedIn notifies the person named.

**The line is DESTINATION, not presence** -- the article-publish wave's own
distinction, and it is what separates this from `send_invitation`'s needle. A
needle goes INTO the page and integers come back. A collaborator invitation
goes the other way: outward, permanent, third-party visible.

### THE SPLIT, and it is the part a planner wants

`C54` and `C56` do **NOT** retire with it. A collaborative post can be created
before anybody is invited, and removing YOURSELF from one names no third party.
Blocker 51's four rows now split three ways rather than one, which is the
published correction being honoured rather than restated.

## 3. THE INSTRUMENT: A RETIREMENT MAY NOT OUTLIVE ITS REASON

`tests/test_a_retired_row_rests_on_a_live_assertion.py`, 8 tests, 0.30s.

For each retired row it checks the census STATE and the SHIPPED ASSERTION
together, so **deleting the rule turns the rows resting on it red** instead of
leaving three retirements standing on something nobody ships any more.

`scripts/count_census_states.py` cannot do this and is not failing to: it counts
states, and a row retired on a live rule and a row retired on a rule deleted
last week are the same green to it. **That gap is the whole subject.**

**SHOWN FAILING THREE WAYS, each against a COPY so no contended file was
edited, with discrimination proofs rather than one assertion repeated:**

    natural state, before the census edit   RED   3 failed, 5 passed
                                                  (state red, assertion GREEN --
                                                   the two halves separate)
    MUT-1  C55's row deleted from a copy    RED   named missing, not passed over
           discrimination: C10              PASS  the mutation is row-specific
           control: census still readable   PASS  the red is about the row
    MUT-2  'collaborators' removed from
           the shipped forbidden set        RED   named the assertion
           discrimination: C10              PASS  C10 rests on 'mentions'

The natural red is the one worth noting. Before the census edit the STATE check
failed on all three rows while the ASSERTION check passed on all three -- which
is the proof that this file is two properties and not one restated, obtained
free, from the tree as it stood.

**Two controls, because a guard that reads an empty corpus refuses nothing:**
the census must parse >= 80 `C` rows and contain `C1`, and the imported
forbidden set must hold >= 10 names. A slice rename or a table reformat would
otherwise leave every assertion passing over zero rows and reading as coverage.

**WHAT IT DOES NOT ASSERT**, stated so it is not read as wider than it is: it
does not claim any row is CORRECTLY retired -- that is a judgement no test
makes -- and it does not require a row to retire because a rule exists. It
asserts only that a retirement and its stated reason cannot be separated.

## 4. FOUR COST CORRECTIONS, AND EVERY ONE MOVES IN THE UNFLATTERING DIRECTION

None of these retires a row. All four say a row is HARDER or LESS KNOWN than
the ledger prices it, which is the class that does not get found by re-reading
your own table.

### 4.1 `SAVED-POSTS-SURFACE` (`C36`, `C37`) rests on an UNMEASURED premise

The census calls this the cheap one: *"`/my-items/saved-posts/` is one allowlist
entry away. Fully reversible, private, no third party. Directly analogous to
`save_job`, which is built and PROVEN."* Every clause of that is true except the
first, and the first is the one the cost is computed from.

**The `/my-items/` family's behaviour was ASSERTED, NEVER MEASURED.**
`readonly.py`'s comment states *"the job tracker, which is where
/my-items/saved-jobs/ now redirects"* as settled fact. Traced through history:
the claim enters in `543660c` (2026-08-22) with **no before/after landing
measurement behind it**, and the old pattern's removal the same day is justified
as dead-code hygiene -- *"nothing builds it any more"* -- not as a fresh redirect
check. Every other `/my-items/` hit in the tree is an offline
`assert_read_url()` refusal (which confirms only *absent from the allowlist*,
and never touches LinkedIn) or prose.

**AND THE ONE INSTRUMENT THAT COULD SETTLE IT STRUCTURALLY CANNOT BE POINTED
HERE.** `scripts/_probe_landed_address_sweep.py` gates on
`readonly.is_read_url(url)` *before* it calls `BROWSER.goto()`, so it can only
measure addresses that are already admitted. That is correct design and it
produces a genuine chicken-and-egg: **the landing cannot be measured until the
address is admitted, and admitting it first is Amendment A10's "a boundary
opened with nothing behind it".**

**SO THIS WAVE MOVED NO PATTERN.** The honest sequence for whoever takes it is:
admit the address narrowly and anchored, run the landed-address check IN THE
SAME WAVE, and if it lands somewhere the allowlist refuses, the pattern names
the LANDED address or is reverted before the wave closes. That is a real cost
and the ledger's "allowlist +1" does not carry it.

### 4.2 `C88`/`C89` are NOT reachable through the shipped settings tool -- measured

The article-publish wave left this as its next question: blocker 64's two
settings rows might be reachable through `linkedin_update_setting`, *"and if
those two rows are reachable through the tool that already exists, that cost is
wrong in the expensive direction."*

**Measured at this tree: they are not, and the reason is structural rather than
a gap.** `linkedin_update_setting` refuses any setting outside
`READABLE_SETTINGS` and **opens no page at all** when it does. Its docstring
states the boundary in its own words:

> ONE SETTING IS WRITABLE, AND ASKING ABOUT ANY OTHER LOADS NOTHING. The read
> allowlist admits exactly one page below the settings index, admitted BY NAME
> on the operator's ruling.

Confirmed offline: `/mypreferences/d/categories/` and
`/mypreferences/d/categories/visibility` both return **False** through
`is_read_url`, against controls that behaved (`/feed/` True,
`/article/newsletter/new/` False).

**AND THE REASON IS THE BOUNDARY TRAP ITSELF**, stated by the tool: *"`Close and
delete account` and `Hibernate account` are addresses in it. A permission
written for the FAMILY would carry those with it."* So the cost of `C88`/`C89`
is not "reuse a shipped tool". It is an address **nobody has opened**, which is
this repository's measured `allowlist +1` placeholder class -- *nine instances
measured, 0 of 9 rows names an in-product address.* The ledger's 7 is not too
high; it is **not yet a number**.

### 4.3 `C87` is filed against the wrong blocker, by the ledger's own assignment rule

`C87` is *remove a mention or tag of yourself* -- the one capability in the
family that acts on somebody ELSE's content. To act on a post you must address
it, and **`C42` is already EXCLUDED-RULED for exactly that**: *"To open
`/feed/update/<urn>/` you need a urn, and no tool in this server returns one."*

Section 3's assignment rule is *one blocker per row, the EARLIEST binding
constraint*. `C87`'s earliest binding constraint is the target-naming gap, not a
mention control -- it would be blocked there even if every mention control in
LinkedIn were mapped. **Re-file `C87` against the post-identifier gap.** Blocker
64 holds two rows, not three, and both are settings.

### 4.4 `C12` and `C2` are COUPLED, and the coupling is an unsanctioned write

`C12` is *save a post as a draft*; `C2` is *choose the post's audience*. They
look independent and are not.

`C2`'s remaining measurement is one read of the post composer. The
article-publish wave declined to take it for a stated reason: **opening a
composer may autosave a draft this server has no reachable surface to detect.**
`_audit/2026-08-31-linkedin-lift.md` establishes the second half -- `/pulse/drafts/`,
`/drafts/` and `/content/drafts/` are all refused, enumerated deliberately.

**Put those together and the consequence is sharper than either document says:
if the autosave happens, this server performs `C12`'s act as a SIDE EFFECT of a
read it considers free, and is structurally unable to observe that it did.**
That is an unsanctioned, unverifiable write occurring inside an admitted read --
and `/article/new/` is on the allowlist today, so the exposure is live, not
hypothetical.

**I did not measure whether the autosave happens.** It is the one live read this
tail owes and it is genuinely two-sided: the read that would settle it is the
read that would cause it. The clean sequence is to open the composer with the
draft surfaces checked before and after -- which is the `read_invitation_badge`
discipline this repo already uses to prove a read did not move a counter, and
here it cannot be applied, **because the counter is on a page the boundary
refuses.** That is the finding: not that the read is expensive, but that this
server cannot currently price it.

## 5. `ARTICLE-SURFACE`: the prior wave's table is right and its SPELLING is not

`_audit/2026-09-05-article-publish.md` section 5 lists ten addresses through
`readonly.is_read_url` and reports `/article/new/ True` and `/feed/ True` on
BARE PATHS. At this tree a bare path is False for both: `is_read_url` matches
absolute `https://www.linkedin.com/...` spellings only.

**The verdicts are unchanged** -- re-measured here with absolute spellings, the
same eight refusals and the same two admissions come back, controls behaving --
so this corrects a transcription and not a conclusion. It is worth one paragraph
only because the next reader would otherwise paste those strings and conclude
the boundary had closed around them.

Re-measured 2026-09-19, absolute spellings, `_ALLOWED_URL_PATTERNS` = 32:

    CONTROL  /feed/                             True
    CONTROL  /article/newsletter/new/           False
             /article/new/                      True
             /pulse/                            False
             /in/me/recent-activity/articles/   False
             /collaborative-articles/           False
             /article/edit/                     False
             /posts/                            False
             /my-items/saved-posts/             False
             /my-items/                         False

`C44` remains EXCLUDED-RULED on `writes.py:926-929`. `C48` (view all your
articles) is the blocker's 1R and its address is refused; `C46`, `C49` and `C78`
are W rows on a surface with no admitted address, so **no article row is one
pattern away** -- the blocker's `allowlist +1` is owed at least twice, once for
the article list and once for `/pulse/`, and this wave did not establish that
either pattern has a reader behind it.

## 6. WHAT THIS WAVE DID NOT DO

* **No live read of any kind.** No browser attached, no page loaded, no composer
  opened. Two waves wanted the browser and this tail's owed read (section 4.4)
  is the one that cannot be taken cheaply.
* **No boundary change.** 32 patterns in, 32 out. Section 4.1 is why.
* **No write fired.** Nothing was designed as a WriteSpec either: the two write
  blockers with a favourable ratio (`SAVED-POSTS-SURFACE`, `POST-DRAFT-SURFACE`)
  are both blocked on an address question ahead of the write question, and a
  gate built on an unmeasured address is A10 with extra steps.
* **`C9`, `C54`, `C56`, `C76`, `C36`, `C37`, `C12`, `C2`, `C46`, `C48`, `C49`,
  `C78`, `C87`, `C88`, `C89` all remain GAP.** Twelve of the seventeen rows in
  this tail did not move and section 4 says why for each family.
* **No `readonly.py` edit**, including the unmeasured redirect comment in
  section 4.1. It is a STANDING INSTRUCTION carrying a false premise, which is
  this repository's most-propagating defect class -- and it is a contended file
  another wave was in. Reported rather than swept; it belongs to whoever
  `git log --oneline -3 -- linkedin_server/readonly.py` names.

## 7. STAMPS, by the box

    Sat, Sep 19, 2026  8:31:57 AM    wave start, freeze file read
    Sat, Sep 19, 2026  8:50:16 AM    two child slices back, build starts
    Sat, Sep 19, 2026  8:52:49 AM    three rows retired, instrument green

## 8. A NEIGHBOUR'S LINE IS IN MY COMMIT. Credited, not rewritten.

`f3d2b6c` reports **12 insertions where 11 were staged.** The twelfth is census
row `C11` (*add a hashtag to a post*), moved to EXCLUDED-RULED and re-filed out
of `HASHTAG-EXISTENCE` by another wave. **It is not mine and I do not vouch for
it.** I did not read it before it was committed, because it did not exist when I
read the staged diff.

**HOW IT HAPPENED, precisely, because the mechanism is the transferable part.**
I staged by name, ran the identity sweep AFTER staging, and read
`git diff --cached` line by line -- eleven rows, all mine. I then committed with
`git commit --only`, which commits the named paths **FROM THE WORKING TREE** and
never consults the index for them. The neighbour wrote `C11` into the file in
the seconds between those two commands, and `--only` carried it.

**`--only` WAS WORKING EXACTLY AS DESIGNED AND COULD NOT HELP.** It protects at
FILE granularity: it kept three other waves' dirty census slices (`jobs.md`,
`profile.md`) out of this commit, which is the failure it exists to prevent.
`C11` was inside a path I legitimately named. This repository has recorded that
distinction twice and this is the third instance; what is new is only that the
reading which looked clean was a **line-level** `git diff --cached`, not a
`--numstat`. **Reading the staged LINES narrows the window to the gap between
the read and the commit. It does not close it, because that gap is where this
landed.**

**WHAT I CHECKED BEFORE LEAVING IT THERE**, since adopting somebody's lines
adopts their DISCLOSURE and not only their design: the shipped identity sweep
re-run against the committed tree reads **PASS, 0 hits across 389 swept files**.
The row carries no identifier.

**WHAT I AM NOT DOING:** rewriting `HEAD`. The sanctioned outcome in a
multi-writer tree is an adopt-commit plus credit, and rewriting trades a
mis-attributed line for something genuinely hard to undo while three waves are
writing the same four files.

**THE AUTHOR IS NAMED BY ARTIFACT AND I COULD NOT RESOLVE IT.** The line
re-files out of the `HASHTAG-EXISTENCE` blocker and cites
`tests/test_typed_bytes.py:115-145`; `git log -- _audit/_census/messaging-and-content.md`
names only this wave and two census waves before it, so the artifact does not
resolve to a live name. **I am deliberately NOT guessing**, because a send to a
guessed idle name forks that agent. Routed to the lead instead, who holds the
roster.

**ONE CONSEQUENCE FOR THE COUNT, stated so nobody attributes it to this wave:**
`C11` moves a row, and it is not one of mine. **This wave banked exactly three**
-- `C10`, `C28`, `C55` -- and that number is the only one here worth quoting.

**THE TOTAL IS NOT, AND THE REASON IS A MEASUREMENT I WATCHED GO STALE.** I
wrote *"GAP 366 / EXCLUDED-RULED 233"* into this section, and the counter run in
the same minute read **GAP 362 / EXCLUDED-RULED 234**. Nothing was wrong with
either reading: three census slices were dirty at that moment and other waves
were retiring rows while I typed. The first number was true when taken and false
when read, which is this repository's oldest law arriving inside a paragraph
written to record a different one.

**So a census total in a multi-writer tree is a reading with a timestamp, never
a state, and this document will not publish one.** Run
`scripts/count_census_states.py` yourself; that is what it is tracked for. What
a wave can honestly claim is its own DELTA, and mine is three rows, named.
