# The intro editor's controls are unread because they are UNNAMEABLE, and one blocker is a closed door

**THE HEADLINE, IN FOUR LINES.** Blocker 20 gates zero live GAP rows — its
eleven are already EXCLUDED-RULED, and a wave routed by the ledger alone would
have spent itself measuring a closed door. Blocker 22's editor DOES render, and
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
