# The four rows the predecessor measured, built -- and one of them has no address

**Wave `cheap-reads-build`, 2026-09-05.** The predecessor wave `cheap-reads`
measured seven blocker rows against the tree and stopped short of building on
four of them because of the clock, not because of the argument. This wave was
sent to build what was already measured and ruled. It did, for three of the
four. The fourth turned out not to be a unit of work at all.

    row  blocker                   filed        this wave
    ---  -----------------------   ----------   -------------------------------
     40  SCHOOL-PAGE-SURFACE       3R  +1       BUILT   anchored pattern, gated
     75  JOB-COLLECTIONS-SURFACE   1R  +1       BUILT   anchored pattern, gated
     56  PREMIUM-READER-NOT-BUILT  1R  none     BUILT   reader module + tests
     41  PREMIUM-JOBS-SURFACES     3R  +1       RE-COST its +1 names no address

---

## 1. THE GRANT, AND THE CONDITION ATTACHED TO IT

The ruling applied here was given by the coordinator and recorded in
`_audit/2026-09-05-cheap-reads.md` section 12. It is applied rather than
re-sought, and it is repeated here because a ruling that travels without its
reason gets re-argued:

> This boundary's sharpest refusal is about MEMBER PROFILES, and its cause is
> specific rather than general -- loading another member's profile leaves
> **them** a durable record, which `linkedin_who_viewed_me` reads the
> receiving end of. **That cause does not transfer to an organisation page,
> to LinkedIn's own curated furniture, or to his own subscription surfaces.**

A school Page emits no view receipt. A recommended-jobs collection names
nobody at all. The subscription page is his own.

**THE CONDITION ON THE GRANT** is that every nav badge and counter is read
BEFORE and AFTER each first load, that the run reports whether any moved, and
that an unreadable badge at either end is a refusal rather than a zero. The
predecessor discharged it for `/premium/my-premium/` -- **0 nav families
moved, with 2 of 6 badges reading NON-ZERO at both ends**, which is what makes
the zero a fact about the account rather than about a broken reader. That
shape is copied here.

---

## 2. THE BOUNDARY: TWO PATTERNS, NEVER A FAMILY

    _ALLOWED_URL_PATTERNS       ee9817a5cb439e2c -> fa201106ecfce5ef
    allowlist                   29 -> 31
    forbidden substrings        33 -> 33   (unchanged, neither grown nor shortened)
    other seven pinned digests  byte-identical

The two entries, one per surface:

    ^https://www\.linkedin\.com/school/[A-Za-z0-9%\-_]{1,100}/?$
    ^https://www\.linkedin\.com/jobs/collections/recommended/?$

**Seven of eight digests byte-identical is the load-bearing number**, and it
is the instrument's own reading -- the failing assertion printed it before the
re-pin, so it is not the author's summary of what he meant to change.

### The re-pin was attributed, not asserted

The chain has one head and was re-pinned twice earlier today. The tree MINUS
this wave's two lines hashes to **exactly `ee9817a5cb439e2c`**, the value the
new line replaces, so nothing else in a tree with a dozen writers rode in.
Two controls sit beside it, because a needle that matches nothing tells the
same story as one that matches the right thing:

    remove a PRE-EXISTING entry instead   -> ef5c55f83c7a32f1, elsewhere entirely
    a needle no line carries              -> 0 lines dropped, digest unmoved

Instrument: `_audit/_scratch/_probe_cheapreads_refreeze_attribution.py`. It is
under the gitignored scratch tree, so **the evidence does not survive a clone**
and the readonly-invariant comment is where it lives.

### The attribution probe caught a real defect on its first run

The collections entry was first written as a three-line `re.compile(...)`.
Dropping the one line carrying the needle left `re.compile()` behind -- which
still parses, still hashes, and hashes DIFFERENTLY -- and the probe reported
MISMATCH against the prior pin.

**A line-based attribution instrument cannot describe a multi-line entry.**
The fix was to make the entry one line, not to loosen the check. Had the probe
not been run, the re-pin would have been recorded with an attribution claim
that was false and that nothing else would have caught.

---

## 3. THE BOUNDARY TRAP, PLANTED -- AND IT IS LARGER THAN ITS HEADLINE

The standing trap says a settings-FAMILY pattern would admit the most
expensive irreversible act on the platform as a side effect of a tidy
refactor, with nothing in the diff naming it. Neither pattern here is a family
pattern. That is asserted in
`tests/test_school_and_collections_boundary.py` rather than promised, and the
assertion is a MUTATION rather than a passing check: the family pattern the
trap names is built in the test file and applied to every account-ending
address this repository can spell.

    the family pattern matches            6 of 6 account-ending spellings
    of those, carrying NO forbidden substring   3

### The sharpening, and it is the useful half

The trap is written about `close-account`. Measured with the shipped
predicate at this tree, the spellings do not share a defence:

    /mypreferences/d/close-accounts     PLURAL     forbidden substring AND no pattern -- TWO gates
    /mypreferences/d/hibernate-account             forbidden substring AND no pattern -- TWO gates
    /mypreferences/d/close-account      SINGULAR   NO forbidden substring, no pattern -- ONE gate
    /mypreferences/d/account-closure               NO forbidden substring, no pattern -- ONE gate

**The addresses a family pattern would actually open are the spellings the
denylist never learned.** The plural is defended twice; the singular is
defended once, and the one thing defending it is the absence of a pattern --
which is precisely what a family pattern removes.

That is this repository's own recurring shape arriving again: a list anchored
to the spellings whoever wrote it happened to meet. The same finding produced
the ten additions of 2026-09-03, and it is worth saying that this is the
fourth known instance rather than presenting it as new.

### The first version of that assertion was wrong in the flattering direction

It said four matched and two were undefended. The run said six and three.
The author had forgotten that the hibernation address is a
`/mypreferences/d/` sibling like the rest, and that the trailing-slash
spellings are separate strings.

**The trap is 50 percent larger than the person writing its guard believed**,
and that gap is the whole argument for planting the mutation instead of
reasoning about it. Recorded because the numbers most worth recomputing are
the ones that flatter the author, and this one flattered by making the danger
look smaller and the guard look adequate.

### What the two entries deliberately did not buy

Asserted through the real predicate, not listed in a comment:

* the school Page's own tabs -- `/people/` (a roster of MEMBERS, the one place
  under this root where the member-profile cause could start to apply again),
  `/jobs/`, `/posts/`, `/about/`;
* a query string on the school address, which is where a filter naming a
  person would arrive;
* the `/school/` parent and the bare root;
* a DOTTED segment, and with it the `..` normalisation escape -- a browser
  normalises `/school/../in/someone/` away, turning an admitted address into
  another page. A dotted slug is a real if uncommon spelling and it FAILS
  CLOSED here deliberately;
* every other collection, and the `/jobs/collections/` parent;
* both sub-path forms.

Two of these are asserted as PROPERTIES rather than as example lists, because
an example list can only cover the spellings somebody thought of: the school
pattern is shown to admit one path segment and no more, and the collections
pattern is shown to match a NAMED address and not a namespace.

### And gate one is not excused

A school whose slug carries a refused substring -- `connect`, `invite`,
`follow` -- still refuses. That is a real limitation, recorded so the next
reader meets it as a deliberate fail-closed rather than as a bug to route
around by shortening a denylist, which is the most dangerous edit available in
this package.

---

## 4. ROW 41 IS NOT A UNIT OF WORK. ITS `allowlist +1` NAMES NO ADDRESS

This wave was sent to apply a granted ruling to row 41. **There is nothing to
apply it to**, and that is a measurement rather than a refusal.

`PREMIUM-JOBS-SURFACES` appears in exactly four places across every tracked
file in this repository (`git grep`):

    _audit/2026-09-03-linkedin-gap-blockers.md:211   the ledger row itself
    _audit/2026-09-05-cheap-reads.md:276, 500, 584   the predecessor's pointer

**Not one of them names an address.** The census rows behind it -- cover-letter
assistance, marking a job Top Choice, AI job-fit tips -- describe FEATURES, and
the census's own consolidation line for the 123-126 block says only that they
"need other surfaces", without saying which.

And the `/premium/` namespace is fully enumerated in tracked files. Three
addresses exist anywhere in the tree, and their states are already settled:

    /premium/my-premium/            ADMITTED, and opened twice
    /premium/my-premium/upgrade     pinned in MUST_STAY_UNREADABLE
    /premium/products/              pinned in MUST_STAY_UNREADABLE

So the `+1` cannot even be discharged by elimination.

**This is the settings-rows finding repeating.** The lead measured earlier
today that seven settings rows each charged `allowlist +1` while not one of
them names an in-product address, and concluded: *the `allowlist +1` charged
against each is not a unit of work; it is a placeholder for an unknown. Nobody
should build against that number.* Row 41 is the eighth.

**A PATTERN WAS NOT WRITTEN, AND THE REASON IS THE TRAP IN SECTION 3.** The
only way to satisfy a `+1` whose address nobody has named is to write a
pattern shaped for a FAMILY and hope the row falls inside it. That is the
exact edit the standing trap forbids, arriving in a costume -- not as a tidy
refactor, but as an unnamed row's cost being taken literally. **A cost figure
is not a specification.**

### What row 41 actually needs, stated so it is not re-sought

One census pass that names the address each of its three rows renders at. The
entitlement question underneath it is already answered -- the predecessor
measured ENTITLED on management verbs with no sales verbs -- so the row cannot
be retired as unreachable-in-principle, and it cannot be built either. It
needs an address, and an address is found by opening a page, not by costing a
ledger.

---

## 5. THE GRANT CONDITION: DISCHARGED, BUT NOT WHERE IT WAS ASKED FOR

**Both addresses SERVE.** That is not a formality -- `/in/me/details/interests/`
is admitted and REDIRECTS, so this repository already holds one door that opens
onto nothing.

    /school/<slug>/                  relation SERVED, exact
    /jobs/collections/recommended/   relation SERVED, same depth, different url
    authwall on either              False

### And then the badge condition failed, in the way it was written to fail

    badge controls on the school Page            0
    badge controls on the collections page       0
    read IMMEDIATELY after load                  0
    read again after a 4 SECOND settle           0
    reproduced                                   twice, two independent runs

**NEITHER SURFACE DRAWS THE NAV CONTROLS THIS PACKAGE'S BADGE READER CAN SEE.**
The grant says an unreadable badge at either end is a refusal rather than a
zero, so this is reported as a refusal: **no post-load reading taken ON either
page can say what that page cost.**

The hydration control is what makes that a statement about the PAGES rather
than about the reader. A read-zero taken before a nav hydrates is a fact about
the instrument -- the render-gate lesson, already paid for in this repository
by a tabbed category that drew zero rows until its tab was pressed. Reading
immediately and again after four seconds, twice, on two pages, returns the
same zero. **Hydration is refuted; the controls are not there.**

Note also what the raw movement line said, and why it is not a finding:
five families reading `0 -> None` is the UNREADABLE state, not a counter that
fell to zero. Those two are different results and a run that prints them the
same way manufactures an incident.

### The reading relocated, on the surface where the reader demonstrably works

The counter the loads could have consumed lives on the nav, and the nav renders
on the feed. So the post was taken there, after both loads:

    feed BEFORE   6 badge controls   notifications 2, one other 1   2 of 6 NON-ZERO
    feed AFTER    6 badge controls   notifications 2, one other 1   2 of 6 NON-ZERO
    nav families that MOVED across BOTH loads    0
    mynetwork pending                            0 -> 0

**The instrument control fired at BOTH ends**, which is the whole reason the
zero means anything -- two badges carried live non-zero counts on both renders,
so the reader resolves real values here rather than returning a default zero.
That is the failure mode that would make "nothing moved" a fact about the
instrument, and it is excluded by measurement rather than by assumption.

### THIS IS A WEAKER CLAIM THAN THE PREMIUM PROBE'S AND IT IS STATED AS ONE

    WHAT IT SAYS      the six nav counters are where they were after both loads,
                      measured where they are readable, with a live control at
                      both ends
    WHAT IT DOES NOT  say what either counter did AT THE INSTANT either page was
                      open. Nothing here can see that, because neither page
                      draws the counters.
    SAFETY            discharged by ABSENCE for the invitation badge -- nothing
                      pending was consumed, because nothing was pending.
    COST              UNMEASURED, and it stays unmeasured until a day the badge
                      is not zero.

Those last two are two claims and this run makes only the first. The
predecessor drew exactly that line for `/premium/my-premium/` and it is drawn
again here rather than quietly rounded up.

---

## 6. ROW 56: THE READER IS BUILT, AND IT CANNOT PUBLISH A NUMBER THAT PICKS

`linkedin_server/premium.py` + `tests/test_premium_reader.py`, at `2097401`.
345 and 438 lines, 33 tests, zero deletions.

The objection that stopped two earlier waves is discharged rather than argued
around: an invented DOM fails closed as *he has no premium features* -- the
exact answer the surface exists to produce -- and the page has now been opened,
serves, and costs nothing measurable, so the reader is aimed at a real render.
The logic is PORTED from the live probe's needle tuples and verdict rather than
re-derived, and no new browser session was opened to build it.

    read_premium_surface(page)     async, returns integers/booleans/None only
    premium_entitlement(reading)   pure, returns the verdict

### The three states, and the field that stops a number picking between them

Every verdict carries `settles` and `leaves_open` as literal strings, on EVERY
branch including the entitled one. Measured by calling the shaper on five
hand-built readings:

    state           strength       settles / leaves open
    ------------    -----------    ---------------------------------------------
    entitled        thin           A REFUTED; B versus C left open EXPLICITLY
    not_entitled    corroborated   A; and what a needle it does not name would say
    ambiguous       corroborated   nothing -- an upsell can sit beside a live plan
    unmatched       thin           NOTHING ABOUT THE ACCOUNT -- about the INSTRUMENT
    error           None           everything; the read failed before any count

**A verdict that cannot return "cannot tell" is not a verdict**, and both
`ambiguous` and `unmatched` are reachable. `unmatched` says in its own payload
that it is a reading about the instrument and not about the account -- the
distinction a bare zero destroys.

**`error` shapes to `error`, never to `not_entitled`.** Failing closed as "he
has no premium" is the precise defect this module exists to avoid, and it is a
test rather than a comment.

### Shown failing before admission

    leak planted in the scan loop (a matched control name retained)   1 failed
    leak reverted                                                     1 passed

The no-page-text guard is therefore one that has been seen firing. 33 pass on
the module's own file; 254 pass across the two shipped taint guards, with zero
new entries needed in either pinned inventory -- `premium.py` has no print, no
logging and no `goto`.

### What is NOT done, and it is deliberate

**The reader is not wired to a tool.** `server.py` and `dom.py` are the two
most contended files in this tree and a slice was not sent into either. That
leaves `premium.py` in the same state as `membership_row` -- **a reader with no
consumer** -- and that is said here plainly rather than left for someone to
discover: the hole is real, it is not live, and both halves belong in the same
sentence.

---

## 7. WHAT THIS WAVE DID NOT DO, STATED PLAINLY

* **No pattern was written for row 41.** Section 4. Its `+1` names no address
  and the only way to satisfy it is the family pattern the standing trap
  forbids.
* **`premium.py` is not wired into `server.py` and no MCP tool calls it.** A
  reader with no consumer, said plainly in section 6.
* **The census rows are NOT edited.** Rows 40, 75 and 56 still read GAP in
  `_audit/_census/`, and a re-count taken today returns the old figure and
  would be right to. That file was edited by another wave earlier today and a
  grouped row cannot be flipped by whoever happens to have built one of its
  members. Naming the owner by artifact: whoever holds `_audit/_census/jobs.md`
  and the applier behind `990bbd3`.
* **The ledger row for 41 is not edited either**, for the same reason, and it
  is the more dangerous of the two: a census row is read as CURRENT TRUTH by
  whoever plans from it next, and `allowlist +1` on row 41 is a standing
  instruction to build against a number that specifies nothing.
* **The post-load badge condition was NOT discharged on the target pages** --
  section 5. It was relocated to the feed, and the weaker claim is labelled.
* **B versus C is untouched.** Separating them needs a JOB POSTING load with
  the 1/1/0 control firing, and that was not attempted. Nothing in this wave
  moves that pair, and the reader is built so that it cannot appear to.
* **No full-clone gate was run.** The runs below are TARGETED and clear SHAPE
  violations only; an enumeration guard fires on *somebody added a caller* and
  is invisible to any run scoped to a file list.
* **Nothing was pushed.** The push is blocked on an unrelated matter recorded
  in the freeze file, and this wave did not touch it.
* **A second probe was commissioned as a tracked instrument and never
  arrived.** The live reading in section 5 was taken with
  `_audit/_scratch/_probe_two_new_reads.py`, which is GITIGNORED -- so the
  instrument does not survive a clone and the output in section 5 is where the
  evidence lives. That is a gap, not a preference.

---

## 8. FREEZE. RECOMPUTED FROM GIT, NOT CARRIED FORWARD FROM A SENTENCE ABOVE

    3 commits   1507 insertions   2 deletions   6 distinct files

| commit | + | - | what |
|---|---:|---:|---|
| `db0dc40` | 493 | 2 | the two anchored patterns, the re-freeze, the boundary tests |
| `2097401` | 783 | 0 | `premium.py`, `tests/test_premium_reader.py` |
| `0c077a9` | 231 | 0 | this document, sections 1-4 |

**THE TWO DELETIONS ARE NAMED RATHER THAN ROUNDED TO ZERO.** Both are the
same line in `tests/test_readonly_boundary_invariant.py` -- the old
`_ALLOWED_URL_PATTERNS` digest, replaced in the two dicts that pin it. No
neighbour's line entered any commit here, which is worth measuring rather than
recalling: five separate incidents of exactly that happened in this tree today,
and this wave read `git diff -U0` immediately before each commit and found the
only removed lines were its own two pins.

**AI attribution: 0 lines, checked per commit across all three** rather than
across the range.

### Gate

    tests/test_school_and_collections_boundary.py                 12 passed
    + test_premium_reader.py + test_readonly_boundary_invariant   56 passed
    the five neighbouring boundary suites                        301 passed
    test_no_committed_identity + test_navigation_is_never_derived 637 passed
    (the slice's own run) test_page_text + test_navigation        254 passed

    scripts/sweep_tracked_for_identity.py, run AFTER staging the new test file
    PASS: 0 hits across 344 swept files

The sweep was re-run after staging because a sweep from earlier in a session is
not evidence about the tree you push -- that rule has paid for itself twice in
this repository in one afternoon.

### One `git commit --only` failure, and it did NOT destroy anything

Both this wave and the row-56 slice hit the same thing: `--only` refuses with
`pathspec did not match any file(s) known to git` when one of its paths is
UNTRACKED. **That refusal happens before the tree-rollback path**, and the
working tree was verified byte-intact afterwards in both cases -- 53 and 88
insertions still present, the new file still 352 lines, the module still
importing with 31 patterns.

This is worth separating from the destructive failure already recorded today,
because they look identical from the outside and only one of them costs work:

    commit FAILS after the paths resolve   -> working tree ROLLED BACK  (severe)
    commit REFUSES on an unknown pathspec  -> nothing touched            (safe)

The fix is `git add -- <path>` by name first. Not `-A`.

### A neighbour reached the same finding from the other side, within the hour

`85364e7` (`profile-rest`) landed `test(boundary): account deletion is refused
by ACCIDENT -- assert it before someone tidies it` shortly after `db0dc40`.
Two waves converged on the same trap from different directions and neither
swept the other's lines. **Disagreement between instruments not sharing a
defect is the cheapest signal available; agreement between two that reached the
same place by different routes is the next cheapest** -- and it is worth noting
that this one arrived by a route the trap's own author had not written down:
the PLURAL-versus-SINGULAR split.

### Cost, in the predecessor's currency

    page loads          8   (2 feed pre, 2 school, 2 collections, 1 feed post, 1 feed pre re-run)
    allowlist patterns  2
    captures            0
    rulings sought      0
    new modules         2   (premium.py, and one gitignored probe)
    new test files      2
    census rows edited  0

**Eight page loads, counted by re-deriving them from the three probe runs
rather than by recalling how many felt right.** The run in section 5 was
executed three times: once bare, once with the hydration control, once with the
feed return. Two of those three were the same two target pages re-opened, which
is the honest number and is larger than the two this wave set out to spend.

### What a successor should pick up first


1. **Wire `premium.py` to a tool.** It is a reader with no consumer, and that
   is the one class of hole this repository has met twice already.
2. **Row 41 needs an ADDRESS, not a ruling.** One census pass naming where its
   three features render. Do not build against its `+1`.
3. **The badge condition cannot be discharged on a surface that draws no
   badges.** If the fleet keeps opening surfaces outside the SPA nav shell,
   the condition needs a second instrument -- or an explicit rule that the
   feed-return form is what it means. Right now every such wave will re-derive
   this from scratch, as this one did.

---

## 9. FREEZE, AMENDED. SECTION 8 COUNTED THREE; THERE ARE FOUR

> **CORRECTED BY: this section.** Section 8's table is not wrong about any row
> it lists. It is incomplete, because a freeze cannot count the commit that
> carries it. Read this one for totals.

Recomputed from `git` after that commit landed, not carried forward:

    4 commits   1754 insertions   9 deletions   6 distinct files

| commit | + | - | what |
|---|---:|---:|---|
| `db0dc40` | 493 | 2 | the two anchored patterns, the re-freeze, the boundary tests |
| `2097401` | 783 | 0 | `premium.py`, `tests/test_premium_reader.py` |
| `0c077a9` | 231 | 0 | this document, sections 1-4 |
| `73c46e9` | 247 | 7 | this document, sections 5-8 |

**ALL NINE DELETIONS ARE THIS WAVE'S OWN LINES** and they are named rather
than rounded away: two are the superseded `_ALLOWED_URL_PATTERNS` digest in
the two dicts that pin it, and seven are the placeholder headings this
document carried between its first commit and its second. **No neighbour's
line entered any of the four**, in a tree where that happened five times
today, and it is a `--numstat` reading rather than a recollection of having
been careful.

**AI attribution: 0, checked per commit across all four.**

### And the wider gate, run after the last code commit

    tools + server surface + every-tool-on-the-surface + readonly
    + boundary invariant + the two new test files + both second-gate suites

    515 passed

That run is the one that matters for the row-56 slice's own claim -- it said
`premium.py` needed **zero new entries in either pinned inventory**, and the
tool-surface enumeration guards are the tests that would fail if it were
wrong. Verified independently rather than relayed. **It is still a TARGETED
run and clears SHAPE violations only**; the full clone gate is owed and is
not this wave's to run.

### The self-correcting freeze, for the fifth time in two documents

The predecessor's section 11 went stale on the next commit and its section 13
said so. This one went stale the same way, at the same distance, for the same
reason. **A freeze is a reading with a timestamp exactly like every other
reading these documents warn about**, and the honest form is not to stop
writing them but to say which one is current. This one is, until the next
commit.

### Wall clock

Start ~19:34 by the box, freeze written at 19:58 by the box, deadline 20:30 by
the box. Every timestamp in this document was taken with `date` rather than
from a sense of elapsed time -- the standing rule after an agent's own clock
ran roughly two hours fast and truncated a wave that had two hours left.

---

## 10. TWO REDS THE WAVE CAUSED OR INHERITED, BOTH CLEARED, AND ONE SLICE DECLINED

Written after section 9, which is therefore stale by exactly the amount this
section describes. The regress is not worth another amendment; the totals at
the foot of this section are current and the earlier tables are correct about
the rows they list.

### The row-56 slice shipped a reader with no consumer, and a guard said so

    tests/test_readers_outside_dom_are_a_pinned_inventory.py
    newly unwired (add with a reason, or wire it): ['premium.read_premium_surface']

**The slice's own report said 254 passed and it did not run this guard.** That
is not a criticism of the slice -- it ran the two guards its brief named -- it
is a fact about a brief that named two and not three. The guard is an
ENUMERATION guard: it fires on *somebody added a reader*, a condition that does
not exist until the reader does, and it is invisible to any run scoped to the
new file. **A slice cannot be briefed to run the guard that its own existence
turns red unless whoever wrote the brief already knew.**

Cleared at `9ed2b62` by giving the reason the guard asks for rather than
widening the inventory silently. The row is worth reading for one thing beyond
itself: **this is the THIRD reader in one day to arrive with no consumer and
the SECOND to name the last-hour crowding of `server.py` as the cause.** One
instance is a wave running out of clock. Three is a shape, and the shape is
that a reader is cheap and a tool is not -- wiring one moves pinned
tool-inventory counts, an enumeration class no targeted run can clear.

### The last unenrolled sanitiser claimant was the predecessor's, and it is now enrolled

    tests/test_a_sanitiser_earns_its_entry.py
    unenrolled: [('_probe_premium_entitlement.py', '_relation')]

Red since `196394d`, which admitted `_relation` to `_SANITISERS` while touching
five files and none of them the enrolment table -- so every claimant born after
it was trusted BY NAME by a guard that had never measured it. Four of the five
were enrolled by their owners through the day. This is the fifth, it belongs to
`cheap-reads`, and this wave is its direct successor carrying its board, which
is the only reason the row was not somebody else's to add.

**The body was checked BEFORE the row was added, not after** -- byte-identical
to the copies the table already exercises, established by extracting it
programmatically and comparing rather than by reading it. The table's eighth
row records a wave that shipped a DIFFERENT body under this name and leaked its
input on the first run, so *it is the same function* is a claim that has been
wrong here before.

Cleared at `9993170`. **336 passed** across the sanitiser table, both taint
guards and the unwired-reader inventory.

### A promotion attempted and REVERTED, which is a result rather than a failure

The live instrument in section 5 lives in the gitignored scratch tree, so its
evidence does not survive a clone. Promoting it to `scripts/` was attempted and
reverted within minutes, because the page-text guard measured it handing
LinkedIn's own text to a print at **7 sites** -- and that guard's failure
message says explicitly not to clear it by adding a line.

    scripts/_probe_two_new_reads.py   0 -> 7

Reverting cost nothing that was not already recorded: the numbers it produced
are in section 5 of this tracked document, and the gap is NAMED in section 7
rather than hidden. **A gitignored instrument with its output written down is a
worse artifact than a tracked one and a better one than a tracked instrument
that turns a guard red for everybody who runs next.**

### And a commissioned slice was declined rather than shipped

A second probe was commissioned as a tracked instrument, arrived, and was moved
to the scratch tree instead of committed. It would have been the sixth
unenrolled claimant, and its own report flagged that it lands in a fleet-wide
tab-leak ratchet **pinned at 39 and already measuring 41 before its file
existed** -- a ratchet that only ever shrinks, being pushed the wrong way by
several waves at once using the template shape their briefs mandate.

That last number is not this wave's to fix and is passed on rather than
absorbed: **the sanctioned probe template and the tab-leak ratchet disagree,
and the template is winning by being written into every brief.** Whoever owns
that ratchet should know it is being broken by the house pattern, not by
carelessness.

### Totals, recomputed at 20:03 by the box

    7 commits   1855 insertions   9 deletions   8 distinct files

| commit | + | - |
|---|---:|---:|
| `db0dc40` | 493 | 2 |
| `2097401` | 783 | 0 |
| `0c077a9` | 231 | 0 |
| `73c46e9` | 247 | 7 |
| `e868f5d` | 60 | 0 |
| `9ed2b62` | 19 | 0 |
| `9993170` | 22 | 0 |

All nine deletions are still this wave's own lines, named in section 9. **AI
attribution: 0, per commit, across all seven.** Nothing pushed -- the push is
blocked on an unrelated matter recorded in the freeze file, and this wave did
not touch it.
