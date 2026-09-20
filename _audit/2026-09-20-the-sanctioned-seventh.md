# The seventh sanctioned mutation: a reason that went false, a boundary that did not move

**2026-09-20. Measured by importing `linkedin_server.readonly` and
`linkedin_server.writes`, not by grep, not inherited from a report.**

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- it states that `set_input_files` is still absent from `SANCTIONED_MUTATIONS`, confirmed at HEAD, and its section 8 table bills a blocker kind `UNSANCTIONED-MUTATION-KIND` at 1 blocker and 16 rows; both were true on 2026-09-03 and are false today, because the verb became entry 7 on 2026-09-04. Its own fourth `CORRECTED BY:` marker is stale too, citing 35 allowlist patterns where there are now 41.

**CORRECTS:** `_audit/2026-09-03-linkedin-capability-census.md` -- it states that `set_input_files` sits in no sanction, closing nine upload capabilities, and that the verb has ONE mention across 51 audit files; it is now entry 7 of `SANCTIONED_MUTATIONS` and appears in at least eight audit documents, though no capability opened, because the upload verb is absent from the performable-action list and every write path is switched off by default.

## What was measured

| thing | value today | what the corpus says |
|---|---:|---|
| `SANCTIONED_MUTATIONS` | **7** entries | `set_input_files` "absent" |
| — entry 7 | `('linkedin_server/writes.py', 'perform', 'set_input_files')` | — |
| `_ALLOWED_URL_PATTERNS` | **41** | 22 in the blockers doc; **35** in its own correction |
| `writes.writes_enabled()` | **False** | — |
| `writes.PERFORMABLE` | **12** actions | — |
| `set_input_files` in `PERFORMABLE` | **no** | — |

## THE BOUNDARY DID NOT MOVE, AND THIS IS THE PART THAT MATTERS

It would be easy to read "file upload is now sanctioned" as a safety boundary
that shifted without a ruling. **It is not, and the distinction is structural
rather than a reassurance.**

`SANCTIONED_MUTATIONS` holds `(file, function, verb)` triples. Entry 7 permits
**`writes.py::perform` to call the Playwright verb `set_input_files`** — it does
not create a capability, and nothing reaches it:

- `PERFORMABLE` — the list of write **actions** a caller can name — holds twelve
  entries (`apply_job`, `comment_on_item`, `follow_company`, `publish_post`,
  `react_to_item`, `save_job`, `send_invitation`, `send_message`,
  `unfollow_company`, `unsave_job`, `update_profile_field`, `update_setting`).
  **`set_input_files` is not one of them.** No caller can ask for an upload.
- `writes_enabled()` reads `LINKEDIN_ENABLE_WRITES` **at call time** and is
  **False**. Every write path is off.
- A write additionally needs a confirm token with a 120-second TTL — deliberately
  short enough that an unattended caller can never hold a live one.

**So nothing became callable.** A verb was permitted at one site inside an
executor that is itself switched off.

## WHAT DID GO WRONG: the reason, not the ruling

The census excludes rows on a reason that no longer describes the code. From
`_audit/_census/profile.md`:

- **`B2`** (profile photo add/change/delete) cites *"a test-enforced
  package-wide ban on `set_input_files`"*, quoting the ban's own words:
  *"UPLOADING IS A DIFFERENT CAPABILITY FROM TYPING. A fill puts his words in a
  box; a file input puts a FILE from this machine into somebody else's inbox,
  chosen by a path string. Nothing in this package should be one edit away from
  that, and the operator has never been asked about it."*
- **`M1`** (upload a resume from Job Application Settings) says *"`set_input_files`
  is unsanctioned on top of that"*.
- A roll-up line bills *"set_input_files, test-enforced (B2, B3, B5, G3) — 4"*.

**There is no package-wide ban today.** There is a ban with one sanctioned
exception, and the exception has existed since 2026-09-05.

**The rows are still excluded correctly** — writes are off, and upload is not in
`PERFORMABLE`, so no caller can reach it. **But they are excluded for a reason
that is false**, and a write-off whose stated reason has gone false is
indistinguishable, to any later reader, from one that was never true. **Right
answer, wrong reason** — which the census cannot tell apart from wrong answer,
wrong reason.

## THE ONE THING HERE THAT IS THE OPERATOR'S TO RULE

The ban's own stated basis was a question about him, not a fact about the code:

> *"Nothing in this package should be one edit away from that, and **the
> operator has never been asked about it**."*

And `_audit/2026-09-03-linkedin-capability-census.md` files upload as **"closed,
deliberately, and ONE OPERATOR ANSWER FROM OPENING"** — *"Nothing needs
measuring first. It needs an answer."*

**No operator answer is recorded anywhere in the corpus.** The sanction is
recorded, honestly and in the right form — a dated snapshot in
`_audit/2026-08-31-linkedin-perform.md` reading *"UPDATE 2026-09-04: FIVE now
… `set_input_files` was the fifth, sanctioning file upload"* — but it records
the change, not a ruling behind it. A grep for a recorded operator answer on
upload returns the question and never the answer.

**Nothing is callable and no capability opened**, so this is not an incident.
But a ban that rested on an unanswered question acquired an exception, and the
answer is still unrecorded. **That is the operator's to settle, not a wave's**,
and until it is settled the honest state is: the verb is permitted at one
switched-off site, the capability is closed, and the question the ban was
waiting on is still open.

This document does not resolve it and no wave should. It is named here so the
question stops being invisible.

Those rows are not repaired here. They belong to the census slices, and
`_audit/_census/profile.md` is under a live wave's hand as this is written.

## A CORRECTION THAT WENT STALE ITSELF, WHICH IS THE SHARPER FINDING

`_audit/2026-09-03-linkedin-gap-blockers.md` already carries **five**
`CORRECTED BY:` markers. The mechanism is not missing and it is not unused. Yet
the fourth of them reads:

> Measured against the live `readonly.is_read_url` (**35 patterns**), 15 of the
> 25 undisputed SURFACE-named blockers have their base address ALREADY ALLOWED
> while the boundary cell below still bills the entry…

**It is 41 today.** That correction was itself a live measurement, correctly
taken, correctly cited — and it is now stale by six patterns. Its own advice is
the remedy and it is worth quoting because it is right: *"Re-derive with
`scripts/classify_surface_blockers.py` rather than reading the cell."*

**A correction is a measurement with a timestamp, exactly like the claim it
corrects.** Marking a document corrected does not make it current; it makes it
current as of the correction. A corpus that corrects in place will, given
enough time, accumulate stale corrections on top of stale claims — and the
marker makes the stale correction look *more* trustworthy than the unmarked
text around it.

The structural answer is in that same sentence: **a cell that can be derived
should name its deriving script instead of publishing a number.** `41` is not a
fact to be written down; it is `len(readonly._ALLOWED_URL_PATTERNS)`.

## Section 4 was never re-read, and that is measurable

The section carrying the false claim was written 2026-09-03 and, per `git
blame`, never edited again — while the same file took 18+ commits to sibling
sections on 2026-09-19. **Nobody re-read it because nobody had a reason to: it
was not wrong when written, and nothing points a reader at a section whose
world has moved.**

## Disposition

- **No census row is changed by this document.** The `set_input_files` rows are
  named above for the wave that owns those slices.
- **No instrument is admitted.** This was a reading, not a check, and nothing
  here has been shown failing.
- The two corrected documents receive `CORRECTED BY:` markers pointing here, so
  a reader arriving at the claim can find this file — a corrector names what it
  corrects, and the corrected document cannot name its corrector unless somebody
  writes it in.
