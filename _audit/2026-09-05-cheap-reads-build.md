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

## 5. ROW 56: THE READER IS BUILT, AND IT CANNOT PUBLISH A NUMBER THAT PICKS

Placeholder -- filled at freeze.

---

## 6. WHAT THIS WAVE DID NOT DO, STATED PLAINLY

Placeholder -- filled at freeze.

---

## 7. FREEZE

Placeholder -- filled at freeze, RECOMPUTED and not re-read.
