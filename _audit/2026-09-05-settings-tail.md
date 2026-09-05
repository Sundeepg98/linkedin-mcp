# The settings tail: one blocker retired with an instrument, seven re-costed against a ruling that already shipped

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- seven settings-shaped
rows are queued BUILD when their earliest binding constraint is a shipped ruling
or a missing address, and `NOTIFY-COST-UNMEASURED` was waiting on an instrument
rather than on an experiment.

Wave `settings-tail`, 2026-09-05. Sixteen blockers were assigned, 22 rows.
**This document covers 8 of them and says plainly which 8 it does not.**
Everything below is measured at the working tree of this date unless it says
otherwise. No write was fired. Nothing was pushed.

---

## 0. THE HEADLINE, IN THREE LINES

1. **`NOTIFY-COST-UNMEASURED` is retired as a blocker and replaced by a
   precondition.** The cost was never unmeasurable; it was unmeasurable
   *without an instrument this package did not hold*. It holds one now, and
   the live reading says the cost **is measurable today** -- badge at 2.
   It was not spent.
2. **Seven settings-shaped rows are mis-costed, not un-built.** A ruling that
   already ships governs them, and the ranked table charges them as
   engineering.
3. **A hardening gap found on the way, and left for its owner:** the
   destructive settings pages are held out by the ABSENCE OF A PATTERN, not
   by a denylist entry.

---

## 1. `NOTIFY-COST-UNMEASURED` -- the row is not what it says

### 1.1 The two true statements that look like a contradiction

`linkedin_notifications` states its own side effect in its docstring, and
calls it measured:

> Loading the notifications page CLEARS YOUR UNREAD BADGE [...] MEASURED, not
> theorised: one call on 2026-08-21 took the badge from 1 to 0, and it does
> not come back.

The blocker on the same surface says the cost is unmeasured. Both are true,
and the reconciliation is the finding:

    THE 2026-08-21 READING WAS TAKEN BY HAND.

Measured, not inferred: this package ships `dom.read_messaging_badge` and
`dom.read_invitation_badge`, and **no reader for the notifications badge at
all**. So the server can STATE the cost and cannot RE-TAKE it -- on any day,
by any caller, for any reason. The row was never waiting on an experiment. It
was waiting on an instrument.

### 1.2 And a zero would have settled it wrongly

This repository had already written the trap down, one surface over, at
`shape.invitation_badge`:

> the reason the cost it guards has never been measured is that a badge
> sitting at zero cannot distinguish "the page consumed nothing" from "there
> was nothing to consume".

That is the existence-question distinction this project has now made in three
places, and it applies here unchanged. A before/after pair reading `0 -> 0` is
not evidence that the page is free; it is evidence that nothing was available
to spend. **A wave running that pair on a quiet account would publish a fact
about the DAY as a fact about the PLATFORM.**

So the deliverable is deliberately NOT a measurement. It is the precondition
that says whether a measurement could mean anything today.

### 1.3 What was built

`linkedin_server/notify_cost.py`, a new module:

| function | what it answers |
|---|---|
| `read_notifications_badge(page)` | the nav badge, read off a page already open -- **zero page loads** |
| `notifications_badge(reading)` | parses it; **zero is a read, not an unreadable** |
| `measurability(before)` | `measurable` / `not_today` / `unreadable` -- three states, never two |
| `cost_delta(before, after)` | the cost, and **three distinguishable refusals** |

`measurability`'s `not_today` carries a `reversible: True` field. That field
is the whole reason the function is not a boolean: a zero here is reversible
by one arriving notification, and a caller who cannot see that distinction
files the row as permanently closed.

**Why a new module rather than a third function beside its two siblings in
`dom.py`:** contention, not design. `dom.py` and `server.py` were the two
contended files all afternoon. The docstring records this as a concurrency
artefact and says a later reader should move it in, rather than defending the
split as architecture.

### 1.4 The instrument was shown failing before it was admitted

`tests/test_notify_cost.py`, 19 tests, driven entirely from synthetic
readings -- the detector is factored out of its assertion in the literal
sense: the tests hand the parser a dict and read what it concluded, and none
can be satisfied by a browser behaving a particular way.

    19 passed in 0.46s

**The control.** The zero guard in `cost_delta` was neutralised in place
(`if b.get("unread") == 0:` -> `if False:`) and the suite re-run:

    2 failed, 17 passed
      FAILED test_a_zero_before_refuses_even_when_the_pair_is_clean
      FAILED test_the_three_refusals_are_distinguishable_from_each_other

The module was then restored from a copy taken before the edit and verified
`cmp`-identical, not retyped -- a rollback you retype is not a rollback.
19 passed again after restore.

**The mutation-sensitive test's input was chosen from the BRANCH STRUCTURE,
not from a model of the risk**, which is the 14:05 ruling applied. Its pair
has nothing whatever wrong with it: both halves readable, both carrying a
well-formed count, no error, no missing control. Every OTHER refusal branch in
`cost_delta` passes that input. The zero guard is the only thing standing
between it and a confident `delta: 0` -- a number that reads as "no cost" and
means "no experiment". The assertion is therefore on the **refusal reason**;
asserting `delta != 5` would have survived the mutation.

### 1.5 The live reading -- and the control that makes it mean anything

`scripts/_probe_notify_cost_precondition.py`, run against Chrome pid 1252 on
9224 at **18:57:14 by the box**:

    1. navigation
       relation: served-the-requested-surface

    2. control -- the two SHIPPED badge readers, same page
       invitation badge : state=read   links=2  counted=1
       messaging badge  : resolved=True  links=1
       at least one shipped reader resolved: True

    3. the notifications badge -- the reader this wave added
       notifications links drawn : 1
       of those, carrying a count: 1
       read error                : None

    4. the precondition
       state      : measurable
       measurable : True
       unread now : 2

**The control is not decoration.** A reader that cannot see its badge and a
reader seeing a badge at zero are indistinguishable from outside, and this
probe's entire output is a claim about which happened. Both shipped sibling
readers resolved on the same page, so a zero from the new reader would have
been a fact about the account. It did not read zero: it read **2**.

**THE COST WAS NOT SPENT.** Taking the AFTER half consumes the operator's
unread state. This wave was briefed to design and gate and fire nothing, and
whether to spend two unread notifications is his call, not a probe's. The
module contains no code that could open that page.

**The probe prints counts and states only.** No address, no aria-label, no
page text. The nav label is page text and the shaped label is still page text,
so neither is printed although both are held. Navigation is reported as a
RELATION (`served-the-requested-surface`). It closes the PAGE it opens in a
`finally`, never the context.

### 1.6 What this changes for the row, stated exactly

| | before | after |
|---|---|---|
| blocker | `NOTIFY-COST-UNMEASURED` | **the operator's go to spend 2 unread items** |
| queue | MEASURE | **DECIDE** (one answer, and it is cheap) |
| cost | 1 | 0 engineering; the instrument is built and green |

The measurement is now a by-product rather than an expedition: the pair can be
taken **in band, for free, by whoever legitimately calls
`linkedin_notifications` anyway**, on a call that was going to happen.

**What it does NOT settle, said plainly:** the cost itself is still unmeasured
by this server. I established that today CAN answer, not what the answer is.

---

## 2. The seven settings-shaped rows are MIS-COSTED, and the ruling that governs them already ships

### 2.1 The ruling, quoted from the shipping code

`server.py:6874`, in `linkedin_update_setting`'s own docstring:

> `Close and delete account` and `Hibernate account` are addresses in it. A
> permission written for the FAMILY would carry those with it, **which is why
> a setting is admitted by name or not at all** -- and it is why this tool
> shipping does NOT mean the next setting is a small step.

The same sentence is in the tool's live refusal payload, attributed to the
operator's ruling. **This is not a proposal. It is shipped, and it is his.**

### 2.2 What the ranked table charges instead

| # | blocker | boundary charged | cost | queue |
|---|---|---|---:|---|
| 74 | `SEARCH-HISTORY-SURFACE` | allowlist +1, denylist x1, WriteSpec | 8 | BUILD |
| 79 | `LEARNING-CERTIFICATE` | allowlist +1, WriteSpec | 7 | BUILD |
| 80 | `ACTIVITY-VIEW-SETTING` | allowlist +1, WriteSpec | 7 | BUILD |
| 82 | `VIDEO-MEETING-INTEGRATION` | allowlist +1, WriteSpec | 7 | BUILD |
| 85 | `FEED-PREFERENCES` | allowlist +1, WriteSpec | 7 | BUILD |
| 86 | `EMBED-SETTING` | allowlist +1, WriteSpec | 7 | BUILD |
| 87 | `SKILL-PAGE-SURFACE` | allowlist +1, WriteSpec | 7 | BUILD |

**BUILD means "engineering only, no ruling needed, the shape is known".** For
any of these that sits in the settings family, that is false in all three
clauses.

The table's own ASSIGNMENT RULE settles it: *one blocker per row, the
EARLIEST binding constraint.* A settings-family row is blocked by the by-name
ruling **before** it is blocked by a missing pattern -- so the blocker is
misassigned, exactly as the retirement wave found the profile slice and the
messaging slice filing the same ruling in opposite states.

### 2.3 But the rows name no address, and that is the finding underneath

Row ids located and cross-checked (row-level lookup delegated; verified
against the ranked table's own counts and R/W splits):

| blocker | row id(s) | R/W | names a url? |
|---|---|---|---|
| `SEARCH-HISTORY-SURFACE` | N 95, N 96 | 1R/1W | **no** |
| `ACTIVITY-VIEW-SETTING` | P G2 | 1W | **no** |
| `FEED-PREFERENCES` | M C52 | 1W | no -- a Help Center article id only |
| `EMBED-SETTING` | M C73 | 1W | no -- a Help Center article id only |
| `LEARNING-CERTIFICATE` | P D29 | 1W | no -- a Help Center article id only |
| `VIDEO-MEETING-INTEGRATION` | M M20 | 1W | **no** |
| `SKILL-PAGE-SURFACE` | N 49 | 1W | **no** |

Detail: `_audit/_scratch/_settings-tail-rows.md` (untracked scratch).

**Not one of the eight names an in-product address.** A Help Center article id
is a documentation citation, not a navigable page.

So the "allowlist +1" charged against every one of them is **not a unit of
work at all**: you cannot write an allowlist pattern for a page nobody has
identified. It is a placeholder for an unknown wearing the costume of a task.
That is why these rows have sat at the bottom of the table looking cheap-ish
and never moved.

### 2.4 The correct re-file, and its honest limit

**I am not asserting which of the seven are in the settings family, because
the rows do not say and I did not open the pages.** What is established is the
decision procedure, and that the current filing is wrong either way:

* if the surface **is** in the settings family -> blocker is the shipped
  by-name ruling; queue **DECIDE**; cost **1** (one naming), boundary
  "allowlist +1 BY NAME";
* if it is **not** -> blocker is that **the row names no address**; queue
  **MEASURE**; the first unit of work is identifying the page, not building
  anything.

Neither is `BUILD, cost 7`. **Seven rows are filed under a queue that says no
decision is needed, and every one of them needs a decision or a page load
before a line of code could be written.**

### 2.5 The gate, measured rather than reasoned about

Candidate spellings put through `readonly.assert_read_url` at this tree.
**The distinction between the two refusals is load-bearing and they want
opposite remedies:**

| candidate | verdict | refused by |
|---|---|---|
| `/mypreferences/d/dark-mode` | **ALLOWED** | -- the one admitted by name |
| `/mypreferences/d/categories/` | REFUSED | **forbidden substring** |
| `/feed/follows/` | REFUSED | **forbidden substring** (`/follow`) |
| `/mypreferences/d/close-account` | REFUSED | **no pattern matches** |
| `/mypreferences/d/search-history` | REFUSED | no pattern matches |
| `/mypreferences/d/manage-video-meeting` | REFUSED | no pattern matches |
| `/skill/<term>/` | REFUSED | no pattern matches |
| `/in/me/` | **ALLOWED** | -- see section 3 |

A forbidden substring cannot be lifted by adding a pattern; a pattern-miss is
admitted the moment somebody adds one. **`/feed/follows/` is substring-blocked,
so `FEED-PREFERENCES` cannot be reached by an allowlist edit even if that is
its address.** The table charges it "allowlist +1" regardless.

---

## 3. THE HARDENING GAP, reported and deliberately NOT acted on

The row above that matters most is `close-account`.

    /mypreferences/d/categories/   REFUSED -- forbidden substring
    /mypreferences/d/close-account REFUSED -- NO PATTERN MATCHES

**The destructive leaf is held out by the absence of a pattern. Only the INDEX
is on the denylist.**

The shipped ruling's stated reason is that a family permission "would carry
those with it". That reasoning is **correct and this measurement is what makes
it load-bearing rather than rhetorical**: there is no second line of defence.
A single family pattern -- the obvious way somebody would discharge seven
"allowlist +1" line items in one edit -- would admit `Close and delete
account` along with them, and nothing else would stop it.

**I did not edit the denylist.** A denylist edit is the most dangerous edit in
this tree, this one is a WIDENING rather than a narrowing and so is the safer
direction, but it is a boundary change touching a contested digest chain in
the last half hour of a shared session, and it is not mine: the boundary lists
have an owner and a re-freeze protocol. **Routed, not taken.**

The artifact to re-take it with, rather than the verdict:

    ./venv/Scripts/python.exe -c "from linkedin_server import readonly; readonly.assert_read_url('https://www.linkedin.com/mypreferences/d/close-account')"

---

## 4. `PROFILE-PDF-DOWNLOAD` -- half settled, and I say which half

**The ruling I was given:** it is his own profile as a file, a read of his own
data, fine to build if the surface supports it.

**Established:** `https://www.linkedin.com/in/me/` is **ALLOWED** at this tree.
The address the download is initiated from is already admitted, so this row
carries **no boundary cost at all** -- the table's "cost 2 / DECIDE" overstates
it on the boundary axis.

**NOT established, and it is the half the ruling actually turned on:** whether
the download lands as a file this server can name. I did not press the
control, did not open the profile's overflow menu, and did not verify that
Playwright's download event fires or where the artefact lands. The ruling said
the download itself is the question; **I answered the address and not the
question.** The row stays open.

---

## 5. WHAT I DID NOT DO -- eight blockers, untouched

Stated as a list rather than buried, because a wave that reports 8 of 16 and
does not enumerate the other 8 is reporting a queue, not the work.

| # | blocker | rows | why not |
|---|---|---:|---|
| 83 | `REPORTING-FLOWS` | 1W | not started -- clock |
| 31 | `NO-URL-AT-ALL` | 1W | **not started.** An existence question I was specifically warned about and did not reach |
| 29 | `AUDIO-EVENTS-EXISTENCE` | 1W | **not started.** Same |
| 48 | `ALL-FILTERS-PANEL` | 2R | not started |
| 49 | `FEED-CONTENT-READ-RULING` | 2R | **not started.** The ruling was handed to me (counts and relations only, copy `groups.py`) and I did not build it |
| 68 | `PICKER-SURFACES` | 2W | not started |
| 54 | `RESUME-TOOLS-SURFACE` | 2 | not started; filed BLOCKED upstream anyway |
| 58 | `PROFILE-PDF-DOWNLOAD` | 1R | **half done** -- see section 4 |

Two of the three existence questions I was warned about were not reached.
`NOTIFY-COST-UNMEASURED` was the third and is the one this wave spent itself
on; the trade was deliberate, because it was the one whose answer unblocks
refusals elsewhere.

**Rows moved: 1 of 22, plus 7 re-costed and 1 half-settled.** Recomputed at
freeze rather than re-read.

---

## 6. PROVENANCE

* Live probe run 18:57:14 IST against Chrome pid 1252 / port 9224; attach
  sub-second, page closed in a `finally`.
* Suite for the new module: 19 passed. Shown failing under one mutation:
  2 failed / 17 passed. Restored `cmp`-identical.
* Gate verdicts from `readonly.assert_read_url` at this working tree. **This
  is a reading dated by the TREE, not by a SHA** -- ten waves were writing.
* No write fired. No boundary list edited. No denylist touched. Nothing pushed.
* No name, member id, slug, urn or page text appears in this document, in the
  module, in its tests or in the probe's output.
