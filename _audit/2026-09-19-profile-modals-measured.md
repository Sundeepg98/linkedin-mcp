# The intro editor's controls are unread because they are UNNAMEABLE

> **CORRECTION, 2026-09-19 -- READ AMENDMENT E BEFORE SECTION 1.**
> This document's original title and section 1 claimed blocker 20 is a
> CLOSED DOOR. **That is wrong.** I identified its eleven rows as
> `profile.md` `I2`-`I12` on a count-and-R/W match and never checked
> whether those rows were in the frozen GAP set the ledger divided. They
> were not. The blocker's real rows are `J92`-`J98` + `P I13`-`I16`, and
> it gates LIVE rows. Amendment E has the verification and the method
> error. Section 1 is left standing, wrong, so the correction has
> something to point at.

**THE HEADLINE — with its first clause now RETRACTED, see Amendment E.**
~~Blocker 20 gates zero live GAP rows.~~ It does not; that claim rested on a
row identification I got wrong. Blocker 22's editor DOES render, and
**5 of its 11 fields carry no accessible name by any route**, which is why the
shipped census sees them and cannot list them. Blocker 38's entry control
carries **no activation relation at all**. Blocker 42 reproduces the prior
wave's ambiguity exactly, fourteen days on.

Read-only. No pattern added, no boundary touched, **nothing pressed and nothing
written**. One tab per probe, closed in a `finally`.

---

## 1. BLOCKER 20 `OPEN-TO-WORK-MODAL` IS A CLOSED DOOR

Its eleven rows are `_audit/_census/profile.md` block I rows **I2–I12**, and
every one reads **EXCLUDED-RULED** today. The identification is exact on two
axes rather than approximate:

    ledger row 20 says       11 rows, 11W
    profile.md I2-I12 is     11 rows, 11W      <- count AND R/W split match

and `_audit/2026-09-05-profile-modals.md` section 2 reached the same
identification independently, quoting the census's own words: *"Open To Work
stays EXCLUDED-RULED and was NOT promoted to the fifth state"*.

**I did not measure this blocker.** The brief's instruction for a closed door
is to report it and move on, and the prior wave already established the deeper
reason: the editor is not url-addressed, its entry control fires a request named
`saveAndFetchNextStep`, so *the one click that would first REVEAL it is also the
first that could CHANGE it*. It is an operator-present DECIDE row, not a MEASURE
row.

### 1.1 But the capability is NOT retired — it is filed twice, in opposite states

This is the part that is more than a stale row count. The Open To Work FIELDS
appear in **two** slices, and the two disagree:

| capability | `profile.md` | `jobs.md` |
|---|---|---|
| OTW field: job titles | I4 EXCLUDED-RULED | J92 **GAP** |
| OTW field: locations | I5 EXCLUDED-RULED | J93 **GAP** |
| OTW field: workplace types | I6 EXCLUDED-RULED | J94 **GAP** |
| OTW field: start date | I8 EXCLUDED-RULED | J95 **GAP** |
| OTW field: employment types | I7 EXCLUDED-RULED | J96 **GAP** |
| India-only: notice period, salary | I9, I10 EXCLUDED-RULED | J97 **GAP** |

**The rows that AGREE are the control that makes this readable rather than a
guess**, because the same pairing is consistent everywhere else in the block:

| capability | `profile.md` | `jobs.md` | agree? |
|---|---|---|---|
| Turn OTW on / off | I2 EXCLUDED-RULED | J89 XR | yes |
| Change the audience | I3 EXCLUDED-RULED | J90 XR | yes |
| Delete the OTW card | I11 EXCLUDED-RULED | J91 XR | yes |
| Minimum pay preference | I13 GAP | J98 GAP | yes |

So the disagreement is not a slice-wide drafting difference. It is **six
adjacent capabilities and nothing else** — the signature of a retirement pass
that touched `profile.md` block I and not `jobs.md` section F.

**Retiring one slice's view of a capability does not retire the capability.**
Nine GAP rows (J92–J100) still stand on this ground, blocked by the same
operator ruling. **I am flipping nothing**: removing capabilities on my own
inference is the undercount the recovery pass exists to fix. Routed.

---

## 2. BLOCKER 22 — THE EDITOR RENDERS, AND ITS OWN FIELDS HAVE NO NAMES

Rows `P A9` (additional-name visibility), `A14` (postal code), `A15` (location
display choice), `A22` (primary position). Boundary charged "none", correctly:
`/in/me/edit/intro/` is already exempted from `/edit/` and is the registered
census surface `profile_edit_intro`.

### 2.1 First I was wrong, and the control caught it

I put the census rows' own wording to the page as needles and got three clean
zeros. **Those zeros were a fact about the needles.** The census rows are
sourced to Help Center articles, and this repo has already measured that
LinkedIn's rendered wording and its article wording differ — a probe aimed at
`add profile in another language` read 0 while `profile language` read 1 on the
same page.

My second hypothesis was also wrong: the shipped census on this address returns
252 controls carrying the PROFILE's activity rail at counts identical to
`/in/me/` (Comment x8, Repost x8, `Invite <member> to connect` x8), which read
as "the editor never mounts". A wait series settled it against me:

| sampled at | dialogs | text inputs in dialog | selects | labels |
|---|---:|---:|---:|---:|
| `/in/me/edit/intro/` 1.5s → 20s | 5 | **6** | **3** | **15** |
| `/in/me/` (control), same waits | 4 | **0** | 1 | 7 |

**Flat from 1500ms to 20s.** The editor is server-rendered and present
immediately; the profile DOM sits underneath it, which is what made the census
aggregate look like a profile read.

### 2.2 The enumeration, shaped by the shipped shaper

Eleven fields in the editor dialog. Labels passed through
`shape.census_shape` — the function `linkedin_surface_census`'s whole privacy
property rests on — before printing, so this list is publishable by
construction rather than by my judgement. **0 of 11 labels were withheld by the
shaper.** No `.value` is read anywhere in the probe; there is no branch that
can.

| field | control | named? |
|---|---|---|
| (unnamed, required) | `input[type=text]` | **NO** |
| (unnamed, required) | `input[type=text]` | **NO** |
| Additional name | `input[type=text]` | yes |
| Pronouns | `select`, 5 options | yes |
| (unnamed) | `div[role=textbox]` | **NO** |
| Country/Region | `input` | yes |
| City | `input` | yes |
| Education | `select`, 2 options | yes |
| Industry | `input` | yes |
| (unnamed) | `input[type=checkbox][role=switch]` | **NO** |
| (unnamed) | `input[type=checkbox][role=switch]` | **NO** |

**THE BLOCKER'S NAME IS LITERALLY CORRECT AND NOW MEASURED. Five of eleven
fields resolve to no accessible name by ANY route** — not `aria-label`, not
`aria-labelledby`, not `label[for]`, not an ancestor `<label>`. That is why the
shipped census returns them as `{'shape': '', 'name_source': 'none'}`: it sees
them and cannot say what they are. The controls are unread because they are
**unnameable**, not because nobody looked.

### 2.3 What that does to the four rows

| row | capability | verdict |
|---|---|---|
| A14 | Postal code | **NOT DRAWN** in the rendered editor |
| A15 | Location display choice | **NOT DRAWN** |
| A22 | Primary Position | **NOT DRAWN** |
| A9 | Additional-name visibility | **UNRESOLVED** — the `Additional name` field is drawn; no named visibility control accompanies it. One of the two unnamed switches is a candidate and I will not guess which |

**THE RENDER GATE IS CLOSED ON THE THREE "NOT DRAWN" VERDICTS**, which is the
difference between *absent* and *absent from what rendered*. The dialog was
scrolled to the bottom of every scrollable box inside it — **3 boxes found and
scrolled, twice** — and the field count held at 11 both times. A count that
does not move under a scroll that genuinely found scrollable regions is
evidence the list is complete. Had zero boxes been scrollable the test would
have been void, and it says so.

**Stated limit:** this is one account, one locale, one render. A field
LinkedIn draws only for other countries, or only after a Country/Region change,
would not appear here — and changing Country/Region is a write, so that variant
is not measurable by any read.

---

## 3. BLOCKER 38 `CONTACT-INFO-PANEL` — THE ENTRY CONTROL IS INERT

Rows `P A25–A29`, an exact 1R/4W match to the ledger. This blocker was **not**
in the prior wave's scope; it is the genuinely unworked one of the four.

`A25`'s census note records that the `Edit contact info` control WAS read on
2026-09-02 and *the panel behind it has never been opened*. That is a presence
reading with no aim attached. Aim is what decides whether a press is even
defined, so aim is what I measured:

| surface | named | aria-haspopup | aria-expanded | aria-controls | verdict |
|---|---:|---:|---:|---:|---|
| `/in/me/` | 1 | **0** | **0** | **0** | NAMED BUT INERT |
| `/in/me/edit/intro/` | 2 | **0** | **0** | **0** | NAMED BUT INERT |

Stable across two absolute reads of each address.

**Nothing on either render evidences that this control opens anything.** A
press would not be a measurement; it would be a guess about an element whose
behaviour the DOM does not declare — and this repo's rule is that *named is not
pressable*. The row does not need a WriteSpec next. It needs either a route
that declares itself, or the finding that this panel is reachable only by an
undeclared handler.

**Why I did not press it anyway.** The five rows behind it are his website,
phone number, instant-messenger accounts and birthday. A panel that edits those
is the one surface on this profile made entirely of values that must never be
printed, and an unevidenced press on it is the worst-shaped risk available for
the smallest information gain.

---

## 4. BLOCKER 42 `OPEN-TO-HIRING-MODAL` — THE AMBIGUITY REPRODUCES EXACTLY

Rows `P J1–J4`. The prior wave got this to the aim and stopped there, reporting
`open_to` ambiguous at 3 of 5 and `hiring` named 3 times with no relation. I
re-took both on a fresh session fourteen days later:

| needle | named | with activation relation | verdict |
|---|---:|---:|---|
| `open to` | 5 | 3 | **AMBIGUOUS** — a press would be choosing |
| `hiring` | 3 | 0 | **NAMED BUT INERT** |

**Identical to the prior reading on every number**, stable across two reads of
each of two addresses. This is a replication, not a re-derivation: the same
verdict from an independent session is worth more than the original alone.

**So the next step is still not a press**, and the prior wave's framing holds:
deciding which of the three `open_to` openers is the menu is settled by reading
their relations, not by pressing one and seeing what happens. The `Open to`
button is additionally a known trap — its own 2026-08-24 correction proved it
resolves to three items and **none is the audience editor** — so a capture
aimed there fails silently and reports "the editor draws three controls".

---

## 5. WHAT I DID NOT DO

* **No press, anywhere.** Not the contact-info control, not `Open to`, not a
  switch in the intro editor.
* **No WriteSpec.** Three of blocker 22's four rows name controls the editor
  does not draw; a WriteSpec for them would specify a guess. The fourth is
  unresolved between two unnamed switches, and a spec that targets a control by
  a name it does not have cannot be written either.
* **No row flipped.** The counter is unchanged by my hand.
* **No boundary edit.** Both addresses used were already admitted.

## 6. THE INSTRUMENT'S LIMITS, STATED

* The AIM reader's verdicts rest on `aria-haspopup` / `aria-expanded`. **A
  control wired by a JavaScript handler with no ARIA relation is INDISTINGUISH-
  ABLE from an inert one to this reader.** So "NAMED BUT INERT" means *nothing
  here declares that it opens*, never *this does not open*. That distinction is
  the whole of blocker 38's verdict and it must not be rounded off.
* The verdict function was shown producing all three of its outcomes — ABSENT,
  NAMED BUT INERT, ONE OPENER — against markup the probe owns, before any live
  number was reported. A reader proven only to FIND things cannot be trusted
  when it reports zero.
* `must_be_absent`, a needle LinkedIn draws nowhere, read 0 on every live
  surface. That proves the reader can stay silent; it says nothing about its
  sensitivity to any particular real label, which is exactly the failure that
  produced my three wrong zeros in 2.1.

---

# AMENDMENT A — 2026-09-19, and it corrects section 3 rather than extending it

## A1. The contact-info control is NOT inert. It is WIRED and UNDECLARED.

Section 3 reports `Edit contact info` as NAMED BUT INERT, and section 6 states
the limit that makes that verdict narrow: *a control wired by a JavaScript
handler with no ARIA relation is indistinguishable from an inert one to that
reader.* **That limit was answerable without pressing anything, so I answered
it.**

`DOMDebugger.getEventListeners` over CDP reports the listeners REGISTERED on a
node. Registration is not activation — reading the table runs no handler, fires
no request and changes nothing. It is strictly a read, and a cheaper one than
the click it replaces.

    contact info control   level 0 (the node)   click x1   ->  WIRED
    open to    control     level 0 (the node)   click x1   ->  WIRED

**THE CONTROL FOR THIS READING, because both targets said yes and two yeses
are not a measurement.** A reader that had only ever reported listeners had not
been shown able to report none. Against three static nodes on the same live
page:

    document.documentElement   listeners: NONE
    first <li>                 listeners: NONE
    first <span>               listeners: NONE

So the reader can report zero on a live node, and the two WIRED verdicts are
not an artefact of a method that answers yes to everything.

## A2. What that changes, stated exactly

**Blocker 38's obstacle is not that no route exists. It is that the route is
UNDECLARED.** The control opens something; the DOM simply does not say what.
The corrected reading of section 3's table:

| was | is |
|---|---|
| "nothing evidences that this control opens anything" | **a click handler is registered on it; nothing declares its TARGET** |
| "the row needs a declared route" | the row needs either a declared target, or a press |

`ONE OPENER` versus `NAMED BUT INERT` is a statement about **ARIA**, not about
**behaviour**, and section 6 said so in advance. This is that stated limit being
cashed rather than a surprise — but the conclusion it changes is section 3's,
so the correction belongs here beside it.

## A3. What it does NOT settle, and I am not rounding this off

**Whether the handler WRITES is not determinable from a listener table.** For
the open-to-work editor this repo holds the request's own name —
`saveAndFetchNextStep` — which is why that surface is ruled unmeasurable by any
read. **No equivalent record exists for the contact-info control**, so I have
evidence that it acts and no evidence about what it does. Absence of a recorded
write is not evidence of a read.

So I still did not press it, and the reason is now sharper than "it looks
inert": the five rows behind that control are his website, phone number,
instant-messenger accounts and birthday, and the one thing I could not
establish is precisely the one that decides whether opening it is free.

**The next unit of work on blocker 38 is therefore a DECIDE, not a MEASURE** —
the same shape the prior wave found for blocker 20, reached by a different
route and with a much smaller residual unknown: one press, on a control now
known to be wired, whose handler nobody has named.

---

# AMENDMENT B — the cross-slice split generalises, and one case is adjudicable against code

Section 1.1 found six Open-To-Work capabilities filed in two slices in opposite
states. The obvious next question is whether that is a one-off. It is not.

## B1. The sweep, and its precision stated before its count

A lexical sweep over all four census slices — normalise the capability text,
score every cross-slice pair by sequence similarity plus shared distinctive
tokens — returns **233 candidate pairs whose two rows are in different states**.

**233 IS A CANDIDATE COUNT AND MUST NOT BE READ AS A FINDING COUNT.** The top
15 different-state candidates were hand-inspected in their section context:
**7 are plausibly the same capability and 8 are not** — mostly "send X to a
1st-degree connection" collisions, where message, recommendation, endorsement
and removal share the phrase and are four different capabilities. So roughly
half of the head is noise, and the true population is unknown rather than
"about 116".

Calibration and its bugs, recorded because they decide whether the recall
figure means anything: the six confirmed pairs are all recovered, but only
after two real defects were found and fixed —

* a corpus-frequency stopword cutoff at 6% stripped `job` as filler, which
  broke the very pair the sweep was calibrated on;
* **`difflib.SequenceMatcher.ratio()` is not symmetric.** The same two strings
  scored 0.533 and 0.667 depending on argument order, and the loop fixed the
  order alphabetically, so one direction of every comparison was being silently
  penalised.

What the method cannot see, stated: true paraphrases sharing no vocabulary; the
collapsed blocks (`profile.md` states 15 and 45 capabilities as single rows),
which dilute against any single matching row; and a capability that is a row in
one slice and prose in another. It is lexical, not semantic.

## B2. The InMail balance — THREE slices, two states, and the code settles it

| slice | row | capability | state |
|---|---|---|---|
| `jobs.md` | 127 | Read the InMail credit balance | **GAP** |
| `messaging-and-content.md` | M4 | View available InMail credit balance | **EXCLUDED-RULED** |
| `network.md` | 157 | View your available InMail credits | **EXCLUDED-RULED** |

**This one does not need adjudicating by argument, because the two rows disagree
about a FACT and the fact is checkable.**

* `M4` says `readonly.py` *admits* `/premium/my-premium/` for exactly this, and
  the page carries no balance.
* `jobs.md 127` says *"the boundary entry and reader are **NOT built**"*.

Put to the shipped predicate at this tree:

    is_read_url("https://www.linkedin.com/premium/my-premium/")   True
    is_read_url("https://www.linkedin.com/premium/my-premium")    True

**The boundary entry EXISTS.** `M4`'s account matches the code; `jobs.md 127` is
GAP on the strength of a claim its own package refutes.

And the jobs row contradicts itself in its own slice: its collapsed-block entry
reads *"`/premium/my-premium/` is already ruled admitted as a census key; the
boundary entry and the reader were deliberately not built."* **Admitted as a
census key and the boundary entry not built cannot both be true** — a census key
must be admitted by the read boundary before the census can load it, which is
what the two `True`s above are.

**The defensible reading is that the row's evidence conflates two things**: the
BOUNDARY ENTRY, which is built and measured here, and the READER for the
balance, which may genuinely not be. Only the second can still be blocking, and
"the boundary entry is not built" is false today whatever its status was when
written.

## B3. I am flipping nothing, and the reason is the same as in section 1.1

Three rows across three slices, two of which I did not measure and none of which
is mine. Removing a capability on an inference is the undercount the recovery
pass exists to fix. What is owed is a ruling by whoever owns those slices, and
they now start from a predicate reading rather than from two prose claims that
disagree.

The candidate list is at `_audit/_scratch/_cross-slice-duplicates.md` with the
script beside it, both untracked. **Do not paste that list anywhere as findings:
half of its head is noise and it says so.**

---

# AMENDMENT C — a second adjudicated instance, and the class already had a name

## C1. `M5` is GAP for a capability another slice EXCLUDED-RULED under four rulings

| slice | row | capability | state | basis |
|---|---|---|---|---|
| `messaging-and-content.md` | M5 | Send an Open Profile message | **GAP** | "needs a third party's profile loaded to find the control" |
| `network.md` | 158 | Send an Open Profile message without spending an InMail | **EXCLUDED-RULED** | **R9**, NOT-REV |

`network.md`'s ruling **R9** is not a one-line note. It is headed *"InMail and
outreach automation. Produces 3 rows. FOUR independent rulings, none
contradicted"*, and its verdict is quoted in the slice itself:

> *the sending half is where all of the risk lives and almost none of the
> value.*

with the arithmetic beside it — five InMail credits a month, no follow-ups
permitted, and a paid subscription that a restriction would strand.

**Sending an Open Profile message is a sending action, so R9 reaches it.** The
two rows are not weighing the same evidence and landing differently; **one slice
received a ruling and the other did not.**

Note the asymmetry in what each side is actually saying. `M5`'s note gives a
BLOCKER — no route to the control — which is a reason the capability is *not
built*. `N158` gives a VERDICT — it will not be built. Those are compatible
sentences about the world and **incompatible states in a census**, which is
precisely how this kind of split survives review: each row reads defensibly on
its own.

## C2. And R9 is the same ruling that settles B2

R9 produces three rows: `N156` (InMail outside your network), **`N157` (view
InMail credits)** and `N158`. `N157` is the third slice of the InMail balance
capability in B2. So the pattern across both amendments is one thing, not two:

    network.md              applied R9 across its rows          156, 157, 158
    messaging-and-content   applied it at M4 and NOT at M5
    jobs.md                 applied it at neither               (127 still GAP)

**A ruling propagating to some of its twins and not the others** — which is the
identical shape as the OTW retirement pass in section 1.1, and as this
repository's own recurring finding that *a redaction was applied at one site and
not at its twin.*

## C3. The class was already named. What is new is its extent.

`_audit/2026-09-05-settings-tail.md` records, in passing, that a retirement wave
found *"the profile slice and the messaging slice filing the same ruling in
opposite states."* **So this is a known class, and nobody had measured how big
it is.** This wave's contribution is that measurement — 233 different-state
candidate pairs with a hand-counted 7-of-15 precision at the head — plus two
instances adjudicated against something better than prose: B2 against the
shipped predicate, C1 against a ruling quoted in the census itself.

**I flipped nothing here either.** `M5` and `N158` belong to two slices, neither
mine, and the fix is a ruling about which verdict governs — not an edit I can
justify from a similarity score.

---

# AMENDMENT D — re-taken after the outage, and the press ruling closes two rows by refusing them

## D1. The outage, and why nothing here needed unwinding

The automation Chrome was down roughly **09:48–10:04**. The hazard is not the
outage but the error text: an attach failure blames Chrome, and a wave can
record the resulting zero as MEASURED-ABSENT.

**No row of mine moved on any reading, in or out of that window** — this wave
flipped nothing anywhere, so there was no claim to unwind, only readings to
re-confirm.

**Re-taken 10:21–10:22 against the restarted browser (pid 3104,
Chrome/153.0.8010.48). All four reproduce:**

| reading | then | now |
|---|---|---|
| contact-info listeners | `click` x1 on the node | **identical** |
| its negative control | NONE on 3 static live nodes | **identical** |
| intro-editor field enumeration | 11 fields, 5 unnamed | **identical, field for field** |
| render gate (scroll) | 3 boxes, count held at 11 | **identical** |

**And the silent-zero failure mode is structurally impossible in these
probes**, which is worth stating because it is a property of the instrument
rather than luck: every probe's only `try` is a `try/finally` for tab closure.
There is no `except` anywhere, so `BROWSER.session()` raising
`BrowserUnavailableError` propagates and the run dies with a traceback. That is
exactly what happened at **09:50:03**, when one probe crashed loudly with
`ECONNREFUSED` and recorded nothing. **A probe with no exception handler cannot
file an outage as an absence.**

## D2. The press ruling REFUSES both of my open presses — on its own terms

`_audit/2026-09-19-the-disclosing-press-ruling.md` condition 2: the control must
match an enumerated disclosure shape **by attribute** — `[aria-expanded]` or
`[aria-haspopup]` — *"not by label text"*, and *"anything not on that list is
REFUSED"*.

**Blocker 38's contact-info control carries NEITHER.** That is the same
measurement as section 3's table (`haspopup=0, expanded=0, controls=0`), read
against the ruling instead of against my own verdict vocabulary.

**And the irony is structural, not incidental: the finding in Amendment A is
exactly what disqualifies it.** The control is WIRED by a click handler and
DECLARES NOTHING. A control that declares nothing can only be matched by label
text, and label text is the one route condition 2 forbids. **So the ruling
permits pressing controls that announce themselves, and this one is precisely a
control that does not.**

It is refused a second time independently: the ruling refuses *"anything that
navigates, submits, or opens a composer or editor"*, and the control is named
for opening an editor.

## D3. A9 is closed too, and by three measurements rather than one

The two unnamed switches were A9's only candidates. Measured on the restarted
browser — **the read the outage had blocked**:

| identifier route | result across all 11 fields |
|---|---|
| accessible name (4 routes) | **5 of 11 resolve to nothing** |
| `aria-expanded` / `aria-haspopup` | **0 of 11 carry either** |
| `id` | **every one shapes to `<opaque>`** — fails the shaper's gate |
| `name` attribute | **absent on all 11** |

So the two switches cannot be identified by name, cannot be identified by id,
carry no `name`, and **match no sanctioned press shape**. Pressing one would in
any case be a WRITE — a switch toggles a setting, it does not disclose one —
and they sit inside an editor, which the ruling refuses outright.

**A9 is therefore NOT "blocked on the press mechanism".** It is refused by the
ruling's terms and unidentifiable by every non-press route this server can read.
Filing it as awaiting the mechanism would have been wrong in a way that looks
patient: the mechanism, when it exists, will not reach this row.

## D4. What each of my four blockers is actually waiting on, final

| # | waiting on |
|---|---|
| 20 | nothing — **closed door**, 11 rows EXCLUDED-RULED. Its live twin is `jobs.md` J92–J100, which a ruling never reached (section 1.1) |
| 22 | **A14/A15/A22: nothing measurable** — not drawn, render gate closed. **A9: refused**, see D3 |
| 38 | **a ruling**, not the press mechanism — the control is off the sanctioned shape list and opens an editor. Reopening it needs the shape list widened, which the ruling says grows only by a further ruling |
| 42 | still the aim: deciding which of three `open_to` openers is the menu, **by reading relations**. These DO carry `aria-expanded`, so this is the one row of mine the press mechanism could serve once it exists |

**That last line is the useful one for scheduling:** of my four blockers, exactly
one is a genuine customer for the disclosing-press mechanism, and it is 42.

---

# AMENDMENT E — SECTION 1 IS WRONG. Blocker 20 is not a closed door.

`skew-gate` refused eleven of my twenty-three handed-over assignment lines
(`3a1e2df`) and the refusal is correct. I re-verified it against the frozen
commit myself rather than accept it, because a correction taken on trust is the
same defect as a claim taken on trust.

## E1. The verification, at the frozen commit `1c08e5f`

    P I2 - I12     EXCLUDED-RULED      <- already ruled AT THE FREEZE
    J 92 - J 98    GAP   (7 rows)
    P I13 - I16    GAP   (4 rows)

**The ledger divided the FROZEN GAP SET.** `I2`–`I12` were not in it, so they
cannot be blocker 20's rows. `J92`–`J98` + `I13`–`I16` is **11 rows, all W, all
GAP at the freeze** — which is the blocker's published `11 / 11W` exactly.

## E2. The method error, named precisely

I identified `I2`–`I12` on **count plus R/W split** — 11 rows, 11W against a
published 11 rows, 11W — and called it "exact on two independent axes".

**It was one axis wearing two names, and it was a coincidence.** `J92`–`J98` +
`I13`–`I16` is also 11 and also all-W. Two different row sets satisfied my test,
so the test never identified anything.

**The property that actually decides membership is the one I never checked: was
the row GAP at the frozen commit the ledger divided?** A duplicate check cannot
see this either — `skew-gate`'s sharpest line is that **a row can be unique and
still not be in the denominator**, which is two questions and I asked one.

**And the corroboration I leaned on made it worse, not better.** I cited the
2026-09-05 wave as reaching the same identification independently. Two readers
agreeing is not evidence when both made the same unchecked assumption; it is one
error with two witnesses. **This repository's own law — date both readings
before adjudicating either — has a sibling I had not met: ask what each reading
CHECKED, not just when it was taken.**

## E3. The sting: my own table pointed at the right rows

Section 1.1 pairs the Open-To-Work FIELD capabilities across two slices and
finds them EXCLUDED-RULED in `profile.md` and **GAP in `jobs.md`**. The GAP side
is where a frozen-GAP-set row must live. **I published the table that located the
blocker's real rows and drew the opposite conclusion from it in the section
above it.**

## E4. What this changes, and what it does not

**RETRACTED:** "blocker 20 gates zero live GAP rows", "closed door", and the
advice to report it and move on. It gates live rows and was worth measuring.
Section 1 is left standing rather than rewritten, so this correction has
something to point at.

**NOT retracted — the six flips in `539752b` stand on their own artifacts**,
which never depended on which rows the ledger assigned:

1. `profile.md` `I4`–`I10` are EXCLUDED-RULED on the NEVER-LOADED ruling;
2. `jobs.md`'s **own** collapsed-block note says `92`–`100` live behind the same
   modal as `89`–`91`, and those are XR in that same slice.

**But the consequence is now larger than when I made them, and the lead should
have it in one line:** those six were blocker 20's own rows, so the flip moved
**6 of its 11**, leaving `J98` + `I13`–`I16` — **5 live GAP rows**. The
reopening path is written into each flipped row: one operator-present consented
capture reopens the block.

**Also retracted by implication:** section 1.1's closing sentence that *"nine GAP
rows (J92–J100) still stand on this ground"* is stale twice over — six of them
are now EXCLUDED-RULED by my own commit, and the set was never nine.

## E5. Why this one is worth the space

Every other correction in this document was the instrument catching me — a
control, a wait series, a negative control. **This one was a peer catching me,
on a claim I had wrapped in the language of rigour** ("exact on two independent
axes", "corroborated independently"). Confident phrasing is not an evidence
class, and the two phrases I reached for were both describing the same unchecked
assumption.

---

# AMENDMENT F — every profile row of mine audited against the `/in/me/` shell report

`content-tail` measured `/in/me/` serving **2,146 chars, 0.197% of the recorded
prior**, with the feed full in the same session. That makes every profile zero
taken today suspect. **All of mine were audited; none moved.**

## F1. The audit, row by row

| row | rests on | exposed? | outcome |
|---|---|---|---|
| `P A9` | a live zero on the intro editor | **YES** | **re-taken, stands** — see F2 |
| `P A25` | aim zeros on `/in/me/` | **YES** | **re-taken, stands** — and see F3 |
| `P B10` | R11 + a **positive** enumeration of 20 settings addresses on `/mypreferences/d/` | no | different address, and a positive |
| `P F2/F6/F7/F8/F9` | `network.md` R3 + the three-of-eight control inside block F | no | document evidence, not a live read |
| the 32 anchored rows | nothing live; no state changed | no | — |

Non-profile rows were checked too and none is exposed: `N 39` rests on
`is_read_url` returning False (a **code** measurement), `M C69`/`M24`/`M5` and
`J92`–`J97`/`J99` on document evidence.

## F2. `P A9`, three fresh readings

    /in/me/ html    398,365 / 398,234 / 398,424      controls 236 / 235 / 236
    intro editor    10-11 fields, 8 labelled, in all three
    the zeros       aria-expanded 0, aria-haspopup 0, name attribute 0  -- all three

**36.5% of the recorded prior, not 0.2%**, and stable to within 200 chars across
three reads. **A shell cannot draw a labelled form.**

## F3. `P A25` — and the reason it was never really a zero

    contact_info   named=1   haspopup=0  expanded=0  controls=0   stable over 2 reads
    listener       click x1 registered on the node                  WIRED

**`named=1` is a POSITIVE.** The control was FOUND; what was zero is the ARIA
relations *on a control that is there*. A shell returns `named=0`.

## F4. THE GENERAL POINT, which is worth more than the audit

Every one of my zero-bearing rows carries **a positive finding from the same
reading of the same surface** — 11 labelled fields beside A9's attribute zeros,
`named=1` and a click listener beside A25's.

> **A zero taken alongside a positive from the same read is SELF-CONTROLLING.**
> The positive proves the surface rendered, so the zero is a fact about the data
> rather than about the reader.

That is why these rows survived a report that could have invalidated them, and
it is a cheaper discipline than re-taking every zero after the fact: **record
one positive from the same read, and the zero carries its own control.**

## F5. Two of my own thresholds were miscalibrated, reported not dropped

* **I used the FEED as a size control with an arbitrary 200,000-char bar**, and
  it printed `CONTROL FAILED`. The feed measured **175,185 → 187,871 → 199,811**
  across three reads: **it grows as it paginates.** A surface whose size depends
  on dwell time cannot be a size control for another surface, and my bar was a
  number I picked rather than derived.
* **My verdict line required `fields==11`** and printed DIFFERS when it read 10 —
  conflating *"the zero reproduces"* with *"the whole reading reproduces"*. A9
  rests on the attribute zeros; the field count is known to drift here.

**NO THEORY is offered for the shell.** It was not reproduced; a transient
hydration failure, a session state and a product change are all consistent with
what I can see, and nothing here separates them.

## F6. The shell finding was RETRACTED, and the two retakes used DIFFERENT instruments

`content-tail` withdrew the 2KB finding (`9938b0d`) on its own re-measurement:
`payload_chars` is **stable within a load and varies by three orders of magnitude
ACROSS loads of the same address** — it read 5,063,129 / 2,146 / 5,147,717 on the
feed. One reading of it establishes nothing about a page.

**My retake reached the same place from a different instrument, and the contrast
is the useful part:**

| instrument | across 3 separate loads of one address |
|---|---|
| `payload_chars` (theirs) | 5,063,129 / 2,146 / 5,147,717 — **3 orders of magnitude** |
| `documentElement.outerHTML.length` (mine) | 398,365 / 398,234 / 398,424 — **±200 chars** |

> **For the question "did this page render", outerHTML length is the stabler
> instrument and `payload_chars` is not fit for it.** Two waves now have
> cross-load readings on one measure each, which is what makes this a comparison
> rather than a preference.

**And the convergence is not corroboration.** We agree the shell is not there,
but we did not run the same check — they re-measured their own number and found
it unstable; I measured a different number and found it stable. **Two waves
agreeing after measuring different things is worth more than two agreeing after
measuring the same thing**, and it is the opposite of the failure I recorded in
Amendment E, where two readers agreed because both had made the same unchecked
assumption.
