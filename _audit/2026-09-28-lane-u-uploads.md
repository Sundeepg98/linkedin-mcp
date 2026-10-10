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

**LANE U'S OWN COMMITS, cited below by short SHA:** `d295e6e`, `3e6b7b7`,
`e4c6cca`, `18dd736`, `4710609`, `f4d3eeb`, `7f9caa6`, `1096eef`, `45466b8`.
They are on lane U's branch and do not resolve on `master` until the
orchestrator merges it. Each one's subject, which survives a rebase, is in
the table below.

| short SHA | subject |
|---|---|
| `d295e6e` | rulings: the orchestrator's build classes of 2026-09-28, copied and registered |
| `3e6b7b7` | rulings + census: the operator's upload decision registered, and the 15 upload rows relabelled within the ledger's capacity |
| `e4c6cca` | uploads: hand the browser the verified bytes, not a path to read again |
| `18dd736` | uploads: the drain point's path-guard refusal speaks in perform's own words |
| `4710609` | writes: send_attachment -- one file into one conversation he names, built behind the grant and unfired |
| `f4d3eeb` | merge master 53908ea into lane U: the CI fast lane and live session 7 under the upload work |
| `7f9caa6` | record + INSTRUMENTS 84: the mutations, the merge, and the hand-off's two lessons registered |
| `1096eef` | lane U, lane CI's first run answered: the surface pin, the envelope baseline, and three citations of unmerged commits |
| `45466b8` | merge master fe119de into lane U: lane K's ledger, the CI lane's local-master fix and one-process sweep |

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
   rewords it. **The other three lanes copying this file will meet this
   guard and the next one.**
3. **The correction guard** read the copy's line 101 as an undeclared
   correction of the upload wave's record. It cites that record in
   agreement, so the pair is triaged onto `NOT_A_CORRECTION` with its reason.
   That guard was red at `d295e6e` -- it was not in the first targeted set --
   and is green from `3e6b7b7`.

**RECONCILED AT THE MERGE OF MASTER `fe119de`.** Lane K registered the same
five ids on master first, from the same copy (commit `4b78e5f`, "rulings:
register the five class rulings of 2026-09-28"), and met the same three
guards. The copy merged clean, both sides holding the same sha256. Lane U's
five entries, its asserted-names pin and its correction triage were dropped
for master's, verbatim; the claims the register prints are lane K's wording.
Lane U's one register entry of its own is `FILE-UPLOAD-OPENED` (1.2), now the
register's last entry: 74 rulings, master's 73 and that one. Lanes A and S
still owe the same reconciliation.

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
`files=[{name, mimeType, buffer}]`. A refusal by the path guard at the drain
point now reaches the receipt as a sentence of `perform`'s own -- what may
have happened, and that a second preview prints the guard's exact reason --
where it used to leave as an exception type only. It does not quote the
guard: an exception's text is not carried into a receipt
(`tests/test_a_write_receipt_carries_no_library_message.py`, which `e4c6cca`
met and `18dd736` answered). No extension or type allowlist was added;
nothing is refused for its type.

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

**`linkedin_send_attachment(thread_id, file, confirm_token)`** -- spec
`send_attachment` in `writes.SANCTIONED_WRITES`, in `PERFORMABLE`, and the
first and only member of `writes.UPLOAD_ACTIONS`. Off by default, two calls
behind the single-use grant, one file, one conversation. The readers and
gates are in `linkedin_server/attachments.py` (new). In `writes.py` the spec
is one contiguous lane U block; its arms (`anchor_label_for`,
`_live_control`, the preview's thread reader, `_verify_after`) and its rows
in the per-action tables sit beside their siblings, each marked lane U. The
tool is one contiguous lane U block in `server.py`. Tests in
`tests/test_send_attachment.py`.

**WHY THIS SURFACE AND NO OTHER.** It is the only one of the three the
operator opened -- profile photo, post media, message attachments -- whose
file input is in a real capture. The live lane's session 3 drew a
conversation's reply form (`tests/fixtures/live3/presence.html`, and the
same footer in `compose_c5-open.html`): two `input[type=file]`, each in its
own `div.msg-form__upload-attachment` beside ONE button, one labelled
"Attach an image for your draft conversation", the other "Attach a file for
your draft conversation". The post composer draws no file input at all, and
no profile-photo surface has been captured.

**THE AIM.** By the label of the button the input shares its wrapper with --
never by position, never by an id -- and cross-checked by the input's own
`accept` declaration read live as `threads`' closed token: `images` for the
image input, `images_and_documents` for the file input (the declarations
measured live on 2026-09-05; the skeleton keeps no attribute values). An
image, by the type read from its bytes, goes to the image input; everything
else to the file input. A disagreement between label and declaration refuses.
`test_the_aim_resolves_on_the_real_capture` runs the shipped selectors over
the capture itself: one form, one wrapper per label, one input in each -- and
the aim refusing there, by its cross-check, because the skeleton blanked the
declarations.

**THE ACT, step by step.**

1. Preview: one load of the conversation, held to the thread id. The reply
   box must read EMPTY with Send DISABLED -- so nothing, words or an earlier
   attachment, waits to go with the file -- and exactly one input must be
   aimable. The block names the file, its exact size, the extension its name
   claims and the type its bytes declare (and whether they agree), a digest,
   which input it goes to, and who the file would reach: the conversation's
   title and headline as a people record, read by the reply's own namer
   (`threads.name_the_reply_recipient`, PREVIEW-NAMES-THE-RESOLVED-TARGET).
   The target holds the file as its path RELATIVE to the upload root, so no
   absolute path -- which carries a username -- is bound, printed or kept.
2. Confirm: the landing is re-checked; the box and the aim are re-read; the
   file is read ONCE, its digest compared, and those bytes handed over
   (section 3).
3. The read-back before Send: a bounded wait (20 s, a liveness bound, deciding
   nothing), then the gate. Send is appended to the one click queue ONLY if
   the form draws the file's name EXACTLY ONCE, the box holds no words, no
   recipient box is drawn, and Send is enabled. The press is strict.
4. The verification: in place first -- does the form still draw the file
   with Send on? -- then a FRESH LOAD of the conversation: SENT only if the
   count of messages drawing the file's name rose by exactly one and the
   last message is his. A sent attachment drawn without its name reads
   UNKNOWN: never SENT, never NOT SENT.

**WHAT IS AIMED AT A CAPTURE AND WHAT IS NOT, stated plainly.** The inputs
and their wrappers: a real capture. The read-back and the verification: a
PROPERTY (the file's name drawn), because no capture shows a composer
holding an attachment or a sent attachment message (lane L5's C3 part b was
never taken). If LinkedIn draws an image attachment as a thumbnail without
its name, the gate refuses and nothing is sent -- the first live run is the
measurement (section 7).

**NO WORDS GO WITH THE FILE.** A message carrying both needs a three-part
target, which `_file_component_of`'s docstring names as the shape this
vocabulary does not express and leaves to "the wave that first needs it";
and a composer holding both has never been captured. Lane U chose the
attachment alone; the proof sends its words first through the proven
`linkedin_send_reply` (section 9, Q3).

**RED FIRST, AND SHOWN FAILING.** Every new guard has a test that fails
without it. Five mutations, each applied alone to this lane's own worktree
file and restored with its sha256 verified, five kills:

| mutation | failed |
|---|---|
| M1 the aim's declaration cross-check removed | 3 (the swapped declarations; the real capture, image and document) |
| M2 the read-back's "the file named exactly once" made always true | 1 (the form never draws the file: Send would have been pressed) |
| M3 the file held as its absolute path | 1 (the root-relative target) |
| M4 a sent message without the file's name read as NOT SENT | 1 (it must read UNKNOWN) |
| M5 the live arm's empty-box re-read removed | 1 (something waiting in the composer after the preview) |

The instruments are registered in `_audit/INSTRUMENTS.md` section 84.

---

## 5. The surfaces, row by row

| row | state | why, measured |
|---|---|---|
| M M14 photo | GAP | the input is aimed at a real capture and the act is built; the composer holding an attachment and the sent attachment message are not captured, and lane L5's cell names both as its bar. Capture U-REPLY-ATTACHMENT-SENT and -PENDING |
| M M15 video | GAP | as M M14; a video goes to the file input, whose 2026-09-05 declaration lists `.mov` and `.mp4` |
| M M18 files | GAP | as M M14. The cell's "max 5, 20 MB total" stays unsourced: `multiple` is absent on both inputs, and this server's 25 MB cap is its own |
| M C3, C4, C5 | GAP | `/preload/sharebox/` draws no file input (live 2026-09-04, offline 2026-09-20); the media control builds one behind a press nobody has captured, and `press._COMPOSER_MARKERS` refuses composer presses for a read. Capture U-POST-MEDIA |
| M C6, M C7 | GAP | C5 and C3 first |
| M C27 | GAP | the comment box's picker, never captured; the same press question. Capture U-COMMENT-MEDIA |
| M C45 | GAP | the article composer (C44) first; re-filed to ARTICLE-SURFACE. Capture U-ARTICLE-MEDIA |
| J 70 | GAP | `/jobs/application-settings/` is refused by the `/jobs/application` substring, whose recorded ground is the apply act. Capture U-RESUME-MANAGER |
| J 146-149 | GAP | see below. Capture U-RESUME-TAILOR |

**J 146-J 149: DOES LINKEDIN STILL OFFER IT? YES, AS FAR AS ANY COMMITTED
READING GOES.** The entry point is drawn on a posting in the committed job
capture `tests/fixtures/job_detail_hydrated.html` -- an anchor to
`/job-apply-resources/?jobPostingId=<id>` on an "entrypoint" button -- and
J 146's own cell records it drawn again by lane Y2 on 2026-09-24, keyed by
the posting. What has never been opened is the surface BEHIND it: the read
gate refuses that address by allowlist silence (measured 2026-10-10). So
nothing was designed. THE MEASUREMENT is capture U-RESUME-TAILOR: admit that
one address as a read (READ-PAST-AN-ACT-SUBSTRING's last paragraph covers a
page refused by silence alone), load it once for a posting he names, and
record whether it serves, redirects -- a redirect away is the MEASURED-ABSENT
reading -- or offers an upload, a stored-resume picker and the controls that
generate text. J 147 and J 148 carry no file of their own; they are
LinkedIn's generation over a resume J 146 would upload.

---

## 6. Capture queue

`_audit/_census/capture-queue-uploads.tsv`, columns `surface-id, address,
presses, save, loads, searches, rows`. Seven lines; every row this lane
leaves GAP is on at least one.

| surface-id | loads | rows | the gate it needs first |
|---|---:|---|---|
| U-REPLY-ATTACHMENT-SENT | 1 | M M14 M15 M18 | none: a read of a conversation he names |
| U-REPLY-ATTACHMENT-PENDING | 0 | M M14 M15 M18 | none: taken inside the live proof |
| U-POST-MEDIA | 1 | M C3 C4 C5 C6 C7 | a call on the composer press (Q4) |
| U-COMMENT-MEDIA | 1 | M C27 | the same call |
| U-ARTICLE-MEDIA | 1 | M C45 | ARTICLE-SURFACE's article-editor capture, then the same call |
| U-RESUME-MANAGER | 1 | J 70 | one anchored read admission under READ-PAST-AN-ACT-SUBSTRING |
| U-RESUME-TAILOR | 1 | J 146-149 | one anchored read admission under the same ruling |

Each press line intercepts the page's file chooser BEFORE the press (a
Playwright `filechooser` listener, never answered), so no native dialog can
open on his screen and no file can be chosen.

---

## 7. The live-proof spec (the live lane runs it; this lane loaded nothing)

**THE TARGET (OPERATOR-NAMES-THE-TARGET).** The first-degree member the
operator named for `M M1` and `M M17` -- the conversation `M M1` made and
`M M17` replied in, by its thread id from the lane's own state. Named here
by role only.

**THE FILE.** `linkedin-tool-test.png`, generated for the test by
`python scripts/make_benign_upload_image.py` into the declared upload root
(`config.UPLOAD_ROOT`: `uploads/` under the server's state directory, or
`LINKEDIN_UPLOAD_DIR`). A 96 x 32 flat light-grey PNG, no text, no metadata,
the same bytes on every run: **122 bytes, sha256 prefix `5d03126f1fd64701`,
`image/png`**. Never one of his files. The script refuses a missing root
(creating it is the operator's act) and refuses to overwrite other bytes.

**THE WORDS.** "Testing a LinkedIn tool I'm building. Please ignore this
message." -- sent FIRST, through `linkedin_send_reply`, in the same
conversation. The attachment follows as its own message (section 4: no
words go with the file).

**THE STEPS AND THE READINGS EXPECTED.**

1. *(1 load)* Resolve the conversation as session 6 did for `M M17`.
2. *(3 loads)* `linkedin_send_reply(thread_id, <the words>)`: preview,
   confirm, fresh load. Expected exactly as session 6: `reply_box_empty`,
   Send on within the 5 s wait, `reply_sent` on the fresh load.
3. *(1 load)* `linkedin_send_attachment(thread_id, "linkedin-tool-test.png")`,
   PREVIEW. Expected block: `file.file_name` `linkedin-tool-test.png`;
   `file.size` "122 bytes (122 bytes exactly)"; `file.extension` `.png`;
   `file.type_from_bytes` "image/png -- PNG image";
   `file.the_name_and_the_bytes` "they agree"; `file.sha256_prefix`
   `5d03126f1fd64701`; `where.file` `linkedin-tool-test.png`;
   `who_this_would_reach` a person record whose name is the member he named
   (CHECK IT before confirming);
   `where.what_the_page_showed.the_input_this_file_goes_to`: `input_label`
   "Attach an image for your draft conversation", `labelled_wrappers` 1,
   `inputs` 1, `declaration` `images`; state `reply_box_empty`; one token.
   **STOP HERE if** the declaration reads anything but `images`, or either
   count is not 1: no token is minted, nothing was attached, and that closed
   reading is the measurement -- LinkedIn's inputs moved.
4. *(1 load)* CONFIRM with the token. Expected receipt: `uploaded` with
   `sha256_prefix` `5d03126f1fd64701` (the preview's), `handed_over` "the
   verified bytes, not the path", `type_handed_over` `image/png`,
   `bytes_handed_over` 122, `files_handed_to_the_browser` 1. Then
   `send_gate`:
   * **PROCEEDED** -- `observed`: `forms` 1, `names_drawn` 1, `editors` 1,
     `editor_empty` true, `recipient_boxes` 0, `send_controls` 1,
     `send_enabled` true; `clicked.clicks_made` 1.
   * **OR REFUSED, the likelier first outcome, and still the measurement:**
     `refused_condition` `2_one_attachment_naming_the_file` with
     `names_drawn` 0 -- LinkedIn drew the image without its name. Send is NOT
     pressed; `performed` is false (`attachment_held_in_composer`). THE FILE
     HAS STILL REACHED LINKEDIN (it is uploaded at the hand-off) and sits in
     his composer: save capture U-REPLY-ATTACHMENT-PENDING now, then the
     operator removes the pending attachment by hand -- no remove control is
     captured or built. Do not retry: the next preview of this conversation
     refuses while Send is enabled.
5. *(1 load, inside step 4)* The verification's fresh load. Expected
   `verification.observed_state` `attachment_sent` -- `events_with_the_name`
   one more than the preview's, the last message his -- or `unknown`, which
   means Send was pressed and the sent message does not draw the name: open
   the conversation, look, and DO NOT RETRY. Save capture
   U-REPLY-ATTACHMENT-SENT from this load either way.

**THE COST.** 7 loads (1 + 3 + 1 + 1 + 1), inside LIVE-BUDGET-40-LOADS,
serial and 20 s apart; 0 searches; nothing metered (a message inside an
existing conversation is not an InMail). **WHAT CANNOT BE UNDONE:** the
words and the file reach the member; the file reaches LinkedIn at the
hand-off even if Send is never pressed.

---

## 8. Gates

Local gates were targeted, never the suite: serial while the live lane's
flag stood, a few workers in the hour it was down (from session 7's close,
about 13:00, until it was back by 14:00), serial again after, and each group
held under two minutes from the 11:35 order on. The suite is certified on
lane CI (below).

| commit | what ran | result |
|---|---|---|
| `d295e6e` rulings | the register, asserted names, audit index, blocker map, pointer graph, ruling holds | 142 passed, 2 failed, fixed before commit (section 1.1); then 33 passed. The correction guard was NOT in this set, and was red at this commit |
| `3e6b7b7` relabel | blocker map, register, ruling holds, unassigned reason, reason locator, state cells, corrections; five corpus guards | 190 passed; 77 passed; committed identity 1044 passed |
| `e4c6cca` hand-off | the two upload files; readonly and boundary pins; doc guards, derived views, writes_nine, typed bytes, model-id, page-text, ignored-path | 67 passed 3 skipped; 647 passed; 308 passed. The receipt-message pin was NOT in this set, and was red at this commit |
| `18dd736` wording | the receipt-message pin and the hand-off tests | 21 passed |
| `4710609` the verb | every test file that fans out over the write registries, in batches; the new tests; the surface and count pins; the reader-leak guard with its refreshed baseline (five new readers, all `clean`, nothing else moved) | batch 1: 16 failed, fixed; batch 2: 83 failed (one missing harness row stopped every writes reader), fixed; the reruns 29, 152 and 915 passed. Census: `census_completion` "every headline figure matches its pin"; `check_write_classes`, `check_read_addresses`, `check_jobs_directions`, `ruling_holds` GREEN |
| mutations on `4710609` | five, section 4 | five kills, every restore verified by sha256 |
| `f4d3eeb` merge of master `53908ea` | the three derived views regenerated (the only conflicts) and `--check`; `census_completion` | all clean; "every headline figure matches its pin" |
| INSTRUMENTS 84 | register numbering, probe controls, corrections, asserted names | 38 passed |
| `7f9caa6`, the merged tree | the direct importers of `threads.py` not yet run (messaging threads, the people reader, the reply's Send wait, the reply surface, the first contact) | 224 passed |
| LANE CI, run 38036873514 on `7f9caa6` | the suite on four shards, pushed to `ci/<branch>` with `lane_ci.py push` | FAILURE, 16 failed. Shard 0: 2444 passed; shard 3: 3368 passed; shard 1: 15 failed, 3410 passed; shard 2: 1 failed, 3471 passed. TWO were this lane's and are fixed in the next commit: the tool-surface pin (`linkedin_send_attachment` appeared with no census decision recorded in the pin) and the tool-envelope baseline (a new tool, unclassified). FOURTEEN were the cited-SHA family on the missing local `master`, the known infrastructure failure the CI lane fixed on master. One of those fourteen, the ratchet, ALSO hid a finding of this lane's own: three commit-slot citations of the unmerged commits above. Disclosed at the top of this record |
| the two CI fixes | the surface pin re-pinned at 62 tools and 99 parameters; the envelope baseline regenerated (one line added, `not_driven`, the verdict every other write tool carries) | 68 passed |
| `1096eef` the fixes and the disclosure | the cited-SHA file, on the record before the disclosure and after; committed identity; six doc guards (correction, asserted names, person-name literal, ignored path, pointer graph, audit index) in one group | cited-SHA: 1 failed (the three sites, `d295e6e` x2 and `3e6b7b7`), then 44 passed; identity 1055 passed. The doc-guard group ran past its 115 s cap at 61 passed and no failure: NOT counted as run; re-run on the merge |
| `45466b8` merge of master `fe119de` | the reconciliation of section 1.1; the three derived views regenerated with their own writers, then `--check`; seven census instruments | RULINGS 74 rulings, every anchor resolving, every declaration accounted for; INDEX 263 documents; blocker map 409 lines, every column. Exit 0 and GREEN: `census_completion` ("every headline figure matches its pin"), `check_next_step` (585 GAP rows, each once), `check_write_classes` (387 lines), `check_read_addresses` (98 of 98), `check_jobs_directions` (108 of 108), `ruling_holds`, `check_exclusion_basis` (40 of 40) |
| `45466b8`, targeted, seven serial groups under a 115 s cap each | the surface and count pins with the envelope guard; the reader-leak guard (both sides' baseline lines); the register, asserted names, corrections, register numbering and lane K's next-step test; the writes fan-out (writes_nine, preview and click state, reaching each control); and three groups that ran past the cap: the upload files with master's unfollow and badge tests, the writes and receipt group, the committed-identity sweep | 139 passed; 683 passed; 64 passed; 212 passed. The three capped groups stopped with no failure (80 passed 3 skipped; about 100 passed; about 1000 passed) and are NOT counted as run. The pushed commits' blobs were swept for identity by the pre-push hook: 0 hits across 1104 blobs, 226 needles |
| LANE CI, run 38038976360 on `45466b8` | the suite on four shards, every test file | SUCCESS, wall 6m16s. Shard 0: 4314 passed, 1 skipped; shard 1: 3166 passed, 2 skipped, 1 xfailed; shard 2: 2076 passed, 1 skipped; shard 3: 3214 passed, 4 skipped. 12770 passed, nothing failed: the cited-SHA family green with master's local-master step and this record's disclosure |

**THE TWO REDS I LEFT AND THEN CLOSED, said plainly.** `d295e6e` was red on
the correction guard and `e4c6cca` on the receipt-message pin, each because
the targeted set I chose did not include the guard the change met. Both were
closed in the next commit. The lesson is the repository's own: a scoped gate
may not claim more than it ran, and the next scope widened to every file
that fans out over what I touched.

---

## 9. Questions for the orchestrator

**Q1. THE 14 ROWS' BLOCKER: A LEDGER ACT, OR AN ADJUDICATED OVER-COUNT?**
Every destination that fits them is full or outside the 97. Grounds, quoted:
`scripts/build_blocker_map.py` -- *"Creating a blocker is a LEDGER act: it
needs an entry in one of the two published tables AND a re-total"*; and
`test_no_blocker_recounts_higher_than_the_ledger_published` -- *"It is a
finding for a person to adjudicate, not a number to absorb -- do not widen
the published count to clear it."* Either (a) open successor blockers in the
ledger's tables and re-total (97 blockers and 409 rows are pinned), or (b)
rule the over-counts on JOBS-APPLICATION-FORBIDDEN (4 of 3), RESUME-TOOLS-
SURFACE (6 of 2), THREAD-REPLY-BOX (5 of 2) and PICKER-SURFACES (8 of 2).
Until then the notes carry what blocks each row.

**Q2. HIS WORDS ON UPLOADS ARE NOT ON RECORD.** FILE-UPLOAD-OPENED is
registered on `615a5c4` and the decides record, which report the decision in
their authors' words. If the register should quote him, his words have to be
asked for; nothing committed holds them.

**Q3. WORDS AND A FILE IN ONE MESSAGE?** Built attachment-only.
`_file_component_of`'s docstring: *"an action carrying BOTH text and a file
... needs a THREE-part target ... the wave that wires the first such
composer owns that decision and will have a live surface to take it
against."* No composer holding both has been captured. The proof therefore
sends the words first through `linkedin_send_reply`, then the image. If one
message is wanted, that is a three-part target kind and a capture.

**Q4. A CALL ON THE COMPOSER PRESS FOR THREE CAPTURES.** U-POST-MEDIA,
U-COMMENT-MEDIA and U-ARTICLE-MEDIA each need one press of a media control
inside a composer, with the file chooser intercepted and never answered.
`press._COMPOSER_MARKERS` refuses it, `terminal=True`: *"composers and
editors are refused for pressing even when admitted for reading"*. Press-gate
defaults are the orchestrator's (OUTWARD-ACTS-NEED-THE-OPERATOR).

**Q5. TWO READ ADMISSIONS UNDER READ-PAST-AN-ACT-SUBSTRING.** U-RESUME-MANAGER
(`/jobs/application-settings/`, refused by the `/jobs/application` substring,
whose ground is the apply act) and U-RESUME-TAILOR
(`/job-apply-resources/?jobPostingId=<id>`, refused by allowlist silence
alone). Each is one exact anchored pattern with a control shown failing; this
lane built neither, because each is a boundary change and the brief asked
for the specs.

**Q6. THE COPIED RULINGS TRIP TWO GUARDS IN EVERY LANE THAT COPIES THEM.**
Lane U and lane K are reconciled at the merge (section 1.1): one register
entry per id, one pin, one triage. Lanes A and S still owe it. A one-word
rewording of section 5's "is read under" would let the shared asserted-names
pin narrow.

**Q7. THE FULL SUITE.** `writes.py`, `server.py`, `threads.py` and
`uploads`' hand-off changed; the local gate ran only targeted files. The lane
CI runs are reported in section 8.

**Q8. ON A `ci/` RUN THE CITED-SHA RATCHET CONVICTS A LANE'S OWN COMMITS.**
`check_cited_shas_resolve.resolves` asks `merge-base --is-ancestor <sha>
master`, and since the CI lane's local-master step a `ci/` run's `master` is
`origin/master`, which no lane commit reaches before its merge. Measured
here: three sites, red locally, answered by the disclosure at the top. Every
lane record that writes "commit" or "at" before its own short SHA meets this
on its `ci/` run. And the ratchet's own message advises *"say in the document
that the SHA resolves only on a branch"*, which `_DISCLOSURE` does not read:
measured, `disclosed_tokens` returns nothing for that wording and returns the
token for "does not resolve on `master`". The message or the vocabulary
should move, the owner's call.

**Q9. LANE NP IS ON LOCAL MASTER AND NOT ON ORIGIN.** Local master reads
`0b41978` (lane NP's merge); `origin/master` reads `fe119de`, which this
branch merged as ordered. NP was not taken: a `ci/` push of it would publish
master commits nobody has pushed. When the two meet, the tool-surface pin
collides by text -- NP moved `PINNED_PARAMETER_COUNT` 96 to 97, this lane 96
to 99 -- and the merged value is 100, at 62 tools. Both lanes changed
`writes.py`.

**Q10. LANE K'S LEDGER NAMES THIS LANE FOR ITS 15 ROWS.** `next-step.tsv`
carries `SIBLING:lane-U` on all fifteen, which stays true:
`check_next_step` is GREEN on the merged tree. Folding this lane's seven
capture lines into the ledger's ranked queue and replacing the fifteen
SIBLING steps is an edit to lane K's judged tables; left for the
orchestrator to assign.
