# Lane U: uploads -- the decision registered, the rows relabelled, the verb made performable

Lane U (`lu-uploads-lead`) of the LinkedIn MCP capability census. Brief
written 2026-09-28, paused before any work landed, relaunched 2026-10-10 from
master `3c8edc2`. Every number below was measured in this lane's worktree on
2026-10-10; nothing was loaded live, and no file of the operator's was read.

**THE SHORT VERSION.**

* The orchestrator's five build-class rulings of 2026-09-28 are copied
  byte-identical and registered (section 1).
* The operator's 2026-09-04 upload decision now has a register entry,
  `FILE-UPLOAD-OPENED`. No committed source records his words, and the entry
  says so (section 1).
* Of the 15 upload rows, ONE could be re-filed inside the ledger's arithmetic
  (`M C45`, to ARTICLE-SURFACE). The other 14 keep their membership and their
  notes now say what blocks each; the choice that would move them is a
  ledger act, put to the orchestrator (section 2).
* The preview-to-perform window is closed: the drain point hands the browser
  the bytes it compared, not a path to read again. Shown on the node, red on
  the parent commit and green after (section 3).
* The upload verb is performable for one surface, the reply form of a
  conversation he names, aimed at markup from a real capture (section 4).
* No row moves state. Each row that stays GAP has a capture spec in
  `_audit/_census/capture-queue-uploads.tsv` (sections 5 and 6).
* The live-proof spec is section 7. This lane took no live loads.

---

## 1. The rulings

### 1.1 The build classes, copied and registered

`_audit/2026-09-28-rulings-build-classes.md` is the paused-lanes copy,
byte-identical (sha256 `db2876cf82fd2d7e`..., 140 lines, ASCII). Its five
declarations are registered in `scripts/build_rulings_index.py` after
NAMED-PROFILE-READ-BEHIND-A-GRANT, the way the 2026-09-27 pair was:

| id | binds |
|---|---|
| EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS | writes -- every act toward other people |
| HIS-OWN-SETTINGS-NOT-OUTWARD | live proofs -- settings of his own account |
| HIS-OWN-CURATION-NOT-OUTWARD | live proofs -- curating his own feed and items |
| PURCHASES-STAY-MANUAL | writes -- purchases and paid upgrades |
| READ-PAST-AN-ACT-SUBSTRING | read boundary -- forbidden substrings written to stop an act |

Each anchor is the ruling's own opening words up to its id. Commit `d295e6e`.

Three guards spoke about the copy, and none was answered by editing it:

1. **The register's positive control.** The first claims I wrote outranked
   the two rulings that answer *"does a forbidden substring alone count as a
   ruling"*. The finder counts query tokens as SUBSTRINGS: "account" carries
   "count", and a note carried "alone". The claims now say only what each
   ruling says, and the control ranks its two rulings first again.
2. **The asserted-names guard** read section 5's "is read under" beside the
   backticked id of a registered ruling as a blocker citation. The text may
   not be edited by a lane, so the site is pinned in
   `tests/test_an_asserted_name_resolves.py` beside the five 2026-09-23 sites
   of the same slot phrase; the ratchet narrows the pin when the orchestrator
   rewords it. **The other three lanes copying this file will meet the same
   two guards.**
3. **The correction guard** read the copy's line 101 as an undeclared
   correction of the upload wave's record. It cites that record in
   agreement, so the pair is triaged onto `NOT_A_CORRECTION` with its reason.
   That guard was red at `d295e6e` -- it was not in the first targeted set --
   and is green from `3e6b7b7`.

### 1.2 The operator's upload decision

`FILE-UPLOAD-OPENED`: *this server may upload a file from this machine: the
operator opened file upload on 2026-09-04, in full -- profile photo, post
media and message attachments.* Aliases: FILE-UPLOAD-UNSANCTIONED, "the
upload sanction". Commit `3e6b7b7`.

**NO COMMITTED SOURCE RECORDS HIS WORDS.** Searched, not assumed: commit
`615a5c4`'s message reports the decision in its author's words ("He was asked
on 2026-09-04 and opened it fully"); the comment above the sanction in
`linkedin_server/readonly.py` reports it the same way; and the decides record
reports it in its section 1. None quotes him. So the entry is registered as
*recorded by `615a5c4` and the decides record*, anchored on that record's
section 1 heading, and its note says so in those words. Its date column
prints 2026-09-20, the record's date; the decision's date is in the claim.
The register's finder now answers "may this server upload a file" with this
entry first.

---

## 2. The relabel: what blocks each row today

Measured 2026-10-10 against the shipped code. The read gate was asked
directly (`readonly.is_read_url`): `/jobs/application-settings/` and
`/job-apply-resources/?jobPostingId=<id>` are refused, `/messaging/thread/<id>/`
and `/preload/sharebox/` are admitted.

| row | what blocks it today | the published blocker that fits | room in it |
|---|---|---|---|
| J 70 | its address: stored resumes live under `/jobs/application-settings/`, refused by the `/jobs/application` substring | JOBS-APPLICATION-FORBIDDEN | 3 of 3 held |
| J 146 | the tailoring surface: its entry point is drawn on a posting (a committed job capture and the row's own 2026-09-24 cell), the address is refused by allowlist silence, and nothing has opened it | RESUME-TOOLS-SURFACE | 2 of 2 held |
| J 147, J 148, J 149 | the same unopened surface, downstream of J 146; no file of their own | RESUME-TOOLS-SURFACE | 2 of 2 held |
| M C3, C4, C5 | the post composer draws no file input (live 2026-09-04, offline 2026-09-20); its media control builds one behind a press nobody has captured | PICKER-SURFACES, at best | 2 of 2 held |
| M C6, M C7 | C5 and C3 first: a title and alt text need an attached file | as C5 and C3 | -- |
| M C27 | the comment box's picker, never captured | PICKER-SURFACES | 2 of 2 held |
| M C45 | the article composer (C44) | ARTICLE-SURFACE | **5 of 6 -- one W slot open** |
| M M14, M15, M18 | the reply form's two file inputs ARE captured; the composer holding an attachment and the sent attachment message are not | THREAD-REPLY-BOX | 2 of 2 held |

**WHAT WAS DONE.** `M C45` is RE-FILED to ARTICLE-SURFACE in
`_audit/_census/blocker-assignments.tsv`, with a `RE_FILED` entry in
`scripts/build_blocker_map.py`. The decides record's successor table names
that destination, the blocker held 5 of its published 6 with a W slot open,
and the map's own notes had enumerated this W row as one of two candidates
for it. FILE-UPLOAD-UNSANCTIONED now reads ACCOUNTED (15 held, one re-filed).

**WHAT WAS NOT DONE, AND WHY: the other 14.** Every destination that fits
them is full at its published count, or is a successor name outside the
ledger's 97. The map refuses both:

* filing onto a name outside the 97 fails the build itself -- *"Creating a
  blocker is a LEDGER act: it needs an entry in one of the two published
  tables AND a re-total"* (`scripts/build_blocker_map.py`);
* filing onto a full blocker fails
  `test_no_blocker_recounts_higher_than_the_ledger_published` -- *"It is a
  finding for a person to adjudicate, not a number to absorb -- do not widen
  the published count to clear it."*

So the 14 keep the ledger's division as membership only, and each line's
note now opens *"MEMBERSHIP ONLY SINCE 2026-10-10"* and names what blocks the
row today. The map carries those notes. This is a question for the
orchestrator (section 9, Q1).

---

## 3. The window between the check and the hand-off, closed

**THE DEFECT, as the brief stated it and as measured.** `writes.perform`
re-read the file's digest at the drain point, compared it with the
preview's, and then handed the browser the PATH. A browser reads a path when
it is handed one, or later, so a file swapped after the comparison uploaded
bytes nobody compared.

**THE FIX.** `linkedin_server/attachments.py` (new) reads the file ONCE in
`read_once`, re-running every property of the path guard (the declared
root, no link on the chain, a regular readable file, the size cap), and
returns the bytes with the digest of exactly those bytes. `perform` compares
that digest and hands over those bytes as Playwright's
`files=[{name, mimeType, buffer}]`. The path guard's own refusals now reach
the receipt in words (they were reported as an exception type only). No
extension or type allowlist was added; nothing is refused for its type.

**THE TYPE, READ FROM THE BYTES.** `attachments.sniff` reads the signature:
PNG, JPEG, GIF, WebP; ISO base-media video (MP4, QuickTime); PDF; ZIP
containers, one level further for OOXML documents; the OLE2 container; UTF-8
text; and otherwise "unrecognised" with `application/octet-stream`. The
preview prints it beside the extension and says whether the name and the
bytes agree; the hand-off declares it to the browser.

**RED FIRST.** `tests/test_upload_hands_over_verified_bytes.py` wraps the
page so the file on disk is rewritten INSIDE the hand-off call, after every
check the code can make, and reads what the browser holds off the node
(`arrayBuffer()`, `name`, `type`). On the parent tree (only the new module
present, `writes.py` unchanged):

    FAILED test_a_file_swapped_after_the_check_does_not_reach_the_browser
      AssertionError: THE BROWSER RECEIVED BYTES NOBODY COMPARED: the file was
      swapped after the digest check and the hand-off read the path.
    FAILED test_the_type_handed_over_is_the_type_read_from_the_bytes
      assert 'text/plain' == 'image/png'
    2 failed, 12 passed

After the hand-off change, the same file: 14 passed; with
`tests/test_uploads.py`, 67 passed and 3 skipped (the three symlink tests,
which skip on this box as before). Two pins in `tests/test_uploads.py`
described the old call -- `str(upload_file.path)` -- and now pin the new
property: the argument is the payload of a name bound once, to
`attachments.read_once` of the queued file, and the digest compared is that
same read's.

---

## 4. The verb, performable: an attachment into a conversation he names

(written as it lands)

---

## 5. The surfaces, row by row

(written as it lands)

---

## 6. Capture queue

(written as it lands)

---

## 7. The live-proof spec

(written as it lands)

---

## 8. Gates

(written as it lands)

---

## 9. Questions for the orchestrator

(written as it lands)
