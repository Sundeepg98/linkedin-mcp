# The five DECIDEs, ruled against committed evidence

Wave `decide-16`, 2026-09-20. Scope: the five highest rows-per-cost blockers the
ledger's ranking table queues `DECIDE` or `DECIDE-RETIRE`. Nothing was pushed.
No census row was moved. `scripts/build_blocker_map.py --write` was not run.

**THE SHORT VERSION. Four of the five were already decided and nobody wrote it
back. The fifth is genuinely open, two of its three sub-questions are already
answered, and the cheap route somebody costed at "one line" is measured
refused.**

---

## 0. THE HEADLINE IS AN ARITHMETIC ONE, AND IT IS MEASURED

The brief says 45 rows sit behind these five blockers. **Measured today with the
shipped enumerator against the census files themselves, 23 do.**

    ./venv/Scripts/python.exe scripts/enumerate_gap_rows.py --state GAP
    303 rows GAP at HEAD in this worktree

| blocker | ledger publishes | still `GAP` today | where the rest went |
|---|---:|---:|---|
| `FILE-UPLOAD-UNSANCTIONED` | 16 | **15** | `M C86` retired 2026-09-19, tag/mention action class |
| `AI-INTERVIEW-PRODUCT` | 14 | **3** | 11 retired 2026-09-05 by `990bbd3` |
| `MESSAGING-SETTINGS` | 5 | **0** | all 5 re-filed 2026-09-05 by `990bbd3` |
| `CONTACT-IMPORT` | 5 | **0** | all 5 retired 2026-09-05 by `990bbd3` |
| `MATCH-DETAILS-COLLAPSED` | 5 | **5** | -- |
| | **45** | **23** | |

**22 of the 45 left GAP fifteen days ago.** The rows are not the defect; the
LEDGER'S RANKING TABLES are. `_audit/2026-09-03-linkedin-gap-blockers.md` has
been amended repeatedly in prose -- its line 354 already carries a `CORRECTED BY`
for the retire queue, and its line 544 already records that `MESSAGING-SETTINGS`
"were already ruled" -- **but the ranking tables at L171-188 and L365-375, which
are what a reader ranks from, still publish the freeze figures.** A correction
that lands in prose beside a table it cannot reach is the same failure
`readonly.py` documents about its own prose at lines 48-63.

**I did not reason from slot counts.** Every figure above is the shipped
instrument's, re-run in this worktree; the blocker map's `state_today` column
agreed with it on all 45 rows and is not what any figure here rests on.

**ONE CONTROL WAS DISARMED AND I AM SAYING SO.** `enumerate_gap_rows.py --control`
shells out to `./venv/Scripts/python.exe`, which does not exist in a worktree --
a worktree carries no gitignored files. The run above is therefore the enumerator
WITHOUT its self-check. I re-ran the four census slices against the row ids by
hand and by grep against the census markdown and got the same 23; that is a
second reading, not the shipped control.

### 0b. THE THREE RETIRED BLOCKERS WERE RE-READ INDEPENDENTLY, ROW BY ROW, AGAINST THE PRIMARY SOURCE

A verification slice walked all 24 rows of `MESSAGING-SETTINGS`, `CONTACT-IMPORT`
and `AI-INTERVIEW-PRODUCT` in the census markdown itself -- not in the derived
map -- and carries per-row `file:line` locators. Findings, which I spot-checked
on two rows before accepting them (`jobs.md:375` = `136 ... GAP`,
`network.md:378` = `109 ... EXCLUDED-RULED`, both exact):

* **All 24 rows found. Zero disagreements** between the census file and
  `blocker-map.tsv` column 7. 21 `EXCLUDED-RULED` + 3 `GAP`, on both sides, row
  for row. So the derived map is not drifting from the source here, and none of
  the counts in section 0 rests on the map.
* **`990bbd3`'s central claim is MEASURED, not taken on its word.** Its message
  asserts "+37 / -37 across four files, and all 37 changed lines carry
  EXCLUDED-RULED". Counted off the diff body: 15 + 10 + 7 + 5 = 37 changed lines
  (`jobs.md` / `messaging-and-content.md` / `network.md` / `profile.md`), and
  **37 of 37 `+` lines contain the literal `EXCLUDED-RULED`, 0 of 37 do not.**
  That matters because every retirement in sections 2-4 rests on that commit
  having done what it said.
* **A correction to my brief's framing, and it is worth carrying.** `990bbd3`
  says "two new blockers were opened for them", and "them" is the FIVE
  handed-back rows across two files -- `J 136 137 138` plus `N 76` and `M C72`.
  **Exactly ONE of those two reaches `J 136 137 138`:**
  `AI-INTERVIEW-RESULTS-NO-ADDRESS`. The second,
  `LINK-FOR-OFF-PLATFORM-USE` (2 rows, 2R, BUILD, cost 2), covers `N 76` and
  `M C72` and is outside this wave's scope entirely.
* **`J 136 137 138` name their successor NOWHERE in the census.** The row text
  mentions `AI-INTERVIEW-PRODUCT` only to say what happened to the other eleven;
  `AI-INTERVIEW-RESULTS-NO-ADDRESS` exists only in
  `_audit/2026-09-05-decide-retire-rulings.md` lines 300-303. **A reader who
  opens the census to check one of those three rows cannot learn which blocker
  holds it** -- which is the precise failure `990bbd3` set out to fix for the 37
  it did edit ("EACH ROW CARRIES ITS OWN REASON, NOT A POINTER"), left standing
  on the three it deliberately did not touch. Section 6E.

**A third, independent reading agrees on the top row.** A sibling wave yesterday
published `FILE-UPLOAD-UNSANCTIONED` at **15** GAP
(`_audit/2026-09-19-what-a-reader-could-actually-close.md:28`), reached by a
different question ("what could a reader close?"), and concluded its 15 rows
"contain no reader work at all". Three instruments, three days, same number.

---

## 1. `FILE-UPLOAD-UNSANCTIONED` -- **DECIDED, 2026-09-04, BY THE OPERATOR. THE BLOCKER RETIRES; THE 15 ROWS DO NOT.**

### 1.1 The decision is not mine and it is not outstanding

The blocker's name asserts the negation of what shipped. `set_input_files` has
been sanctioned for sixteen days.

    linkedin_server/readonly.py:2115
        ("linkedin_server/writes.py", "perform", "set_input_files"),

Landed in `615a5c4`, 2026-09-04, *"feat(uploads): the question test_readonly.py
asked has an answer"*. **The ruling is the operator's, not a wave's**, and the
code says so in its own words at `readonly.py:2040-2049`:

> IT EXISTS BECAUSE THE OPERATOR WAS ASKED AND ANSWERED. The absence of
> `set_input_files` from this list was not an oversight: it was an OPEN
> QUESTION [...] and counted in `_audit/2026-09-03-linkedin-gap-blockers.md` as
> the single highest-value blocker in the census -- 16 capability rows, one
> ruling. He was asked on 2026-09-04 and opened it FULLY: profile photo, post
> media and message attachments.

The scope of his ruling is restated independently in `linkedin_server/uploads.py`
lines 8-12 and 58-60 -- *"photo, video, document and attachment paths"* -- and
that module exists only because he opened it.

**The durable assertion, so this cannot rot back into a question:**
`tests/test_readonly.py:406`, `test_exactly_one_place_in_this_package_can_reach_a_file_input`,
whose docstring opens *"THE QUESTION THIS TEST CARRIED FOR THREE DAYS HAS BEEN
ANSWERED."* It was `test_nothing_in_this_package_can_reach_a_file_input` and was
inverted by name. A reader who finds the old sentence in history sees what
changed and on whose say-so.

**Two waves have already worked this blocker** and neither is cited in the
ranking table: `_audit/2026-09-04-file-input-survey.md` and
`_audit/2026-09-05-upload-sanction.md`. The second opens with the finding in its
title: *"The upload sanction was already granted. What was missing was an aim,
and a guard."* Its section 1 records a brief that ordered the sanction ADDED,
measured it already present, and refused to re-land it -- sites asserting the
list LENGTH would have gone red on a duplicate, so re-landing it would have read
like a real regression. That wave cost zero and is the precedent for this one.

**AND ITS OWN NUMBER HAS SINCE GONE STALE, which is the point rather than a
footnote.** That document says "five entries" and was right on 2026-09-05.
**Measured at HEAD today: `len(readonly.SANCTIONED_MUTATIONS) == 7`**
(`tests/test_readonly.py:161,270`) -- the disclosing-press ruling added the
`press.disclose` click/press pair on 2026-09-19. `readonly.py:48-54` predicted
this exact decay in its own words: *"a count in prose beside a list it cannot
read goes stale in silence, and knowing that does not stop you writing one."*
Cite the entry, never the length.

### 1.2 So the DECIDE is closed and the COST OF 1 IS FALSE

The ledger's own body text (L383-392) got the shape right before anyone ruled:
*"a yes does not ship 16 capabilities -- it UNBLOCKS them. Each still needs its
composer surface afterwards."* That is exactly what happened. The mechanism
landed whole:

* `writes.UPLOAD_CONTROL_KIND` (`writes.py:2847`) and the drain point at
  `writes.py:8648`, the single sanctioned `page.set_input_files` call site.
* A digest re-read immediately before handover, so the bytes uploaded are the
  bytes the preview showed (`writes.py:8580-8589`).
* A control-kind gate directly above the call (`writes.py:8632-8644`) that
  refuses any action wired into `UPLOAD_ACTIONS` without an arm that MEASURED a
  file input. It was shown failing both ways on a copy of the tree -- guard
  removed (2 red), guard made unconditional (1 red) -- so it is not a check that
  cannot fail.
* `writes.UPLOAD_ACTIONS` (`writes.py:2818`) ships `frozenset()`, deliberately,
  and `tests/test_uploads.py:674` pins it empty.

**What is left is per-surface wiring, and it is not cost 1.** Cost 1 in the
ledger bought the ruling. The ruling is bought.

### 1.3 The 15 rows re-file into five successors. They are already enumerated; I re-price two of them with my own measurement.

`_audit/2026-09-05-upload-sanction.md` section 5 resolves all sixteen row by row.
I confirm that mapping and correct its costing in two places.

| rows | n | successor blocker (proposed) | what it is actually blocked on |
|---|---:|---|---|
| `M M14 M15 M18` | 3 | `UPLOAD-WIRING-UNBUILT` | **Nothing unknown. Wiring.** Aim MEASURED live 2026-09-05: the two file inputs on `/messaging/compose/` carry DIFFERENT `accept` declarations (`image=True video=False documents=False` vs `image=True video=True documents=True`), so LinkedIn itself distinguishes them where a name and a count both fail. Needs: a `_live_control` arm returning `UPLOAD_CONTROL_KIND`, a target shape, a tool, consent text. **This is the only buildable sub-group and it is where the whole value of the blocker now sits.** |
| `M C3 C4 C5 C6 C7` | 5 | `COMPOSER-PRESS-REFUSED` | **A SHIPPED TERMINAL REFUSAL, not a missing sanction.** The post composer drew ZERO file inputs live 2026-09-04 and builds one on demand behind `Add media`, so it needs a press -- and `/preload/sharebox` is in `press._COMPOSER_MARKERS` (`press.py:151-158`), which refuses it `terminal=True` with the reason *"composers and editors are refused for pressing even when admitted for reading"* (`press.py:358-369`). Overturning that means overturning the autosave argument, not writing a new allowlist line. |
| `M C27` | 1 | `PICKER-SURFACES` (exists) | a picker surface nobody has captured |
| `M C45` | 1 | `ARTICLE-SURFACE` (exists) | depends on `C44`, the article composer |
| `J 70` | 1 | `RESUME-MANAGER-ADDRESS` | a resume-manager address that is not on the read allowlist |
| `J 146 147 148 149` | 4 | see 1.4 -- **NOT AN UPLOAD BLOCKER** | |

**THE COSTING CORRECTION THAT MATTERS.** `_audit/2026-09-04-file-input-survey.md`
section 3 costs the message composer as *"a `_live_control` arm + a name
needle"*. There is no needle: read live 2026-09-05, both inputs come back with an
EMPTY shaped name and `name_source=none`. The `accept` route (upload-sanction
section 3b) is what replaced it. Anyone wiring `M M14/15/18` must aim by
declaration and must NOT aim at the names `Attach a file for your draft
conversation` / `Attach an image for your draft conversation` that
`tests/test_readonly.py:426-428` still carries from the 2026-09-01 reading --
those names were not reproducible by any instrument on 2026-09-05.

### 1.4 `J 146 147 148 149` are in the wrong blocker, and the retire-ruling already noticed

`_audit/2026-09-05-decide-retire-rulings.md`, closing section 3.1:

> **WHAT THIS RULING DOES NOT REACH:** rows 146-149 (resume tips) are a different
> product and are already filed under `FILE-UPLOAD-UNSANCTIONED`, rank 1, DECIDE.
> Nothing here touches them.

It was right to leave them and right to flag them. Read the four capabilities:

    J 146  Upload a resume for analysis against one specific job posting
    J 147  Receive personalized insights on the job and how to enhance the resume
    J 148  Refine sections of the resume with suggested language
    J 149  Export the result, or attach it to a LinkedIn application

**Only `J 146` involves a file at all.** `J 147` and `J 148` are LinkedIn running
a model over his resume and returning generated prose; `J 149` is downstream of
both. They are the same product family as `Create cover letter`, which A13
measured sitting on the same `/preload/guideOverlay/` path as `Show match
details` -- i.e. the family in section 5 below, not the upload family. Filing
them here has been inflating the top of the ranking table by four rows for
seventeen days.

**I am not moving them.** Two siblings are building in other worktrees and the
brief forbids it. The exact lines are in section 6.

### 1.5 VERDICT

**The blocker `FILE-UPLOAD-UNSANCTIONED` RETIRES as a blocker** -- its question
was answered on 2026-09-04 and its name is now false. **Its 15 rows stay `GAP`**,
correctly, and re-file across five successors. **None of the five is cost 1.**
The one worth queueing is `UPLOAD-WIRING-UNBUILT` at 3 rows: it is the only
sub-group where the aim is measured, the mechanism is built and shown working
end to end, and what remains is ordinary wiring.

---

## 2. `AI-INTERVIEW-PRODUCT` -- **ALREADY RETIRED, 11 OF 14, ON 2026-09-05. THE LEDGER ROW IS FIFTEEN DAYS STALE.**

`990bbd3`, *"docs(census): the 37 ruled rows leave GAP in the files, not only in
the ruling"*. Eleven of these fourteen were in that 37. Measured today: `J 132
133 134 135 139 140 141 142 143 144 145` are all `EXCLUDED-RULED` in
`_audit/_census/jobs.md`; only `J 136 137 138` remain `GAP`.

The ruling is `_audit/2026-09-05-decide-retire-rulings.md` section 3.1, and it
does **not** rest on "it is an AI product" -- it rests on three separate grounds,
which is why it does not generalise to section 5 below:

* **`J 132 133 134 135 139`** -- a real-time spoken session in a separate product
  in a new tab. LinkedIn publishes a help article (`a10133010`) whose entire
  subject is granting CAMERA AND MICROPHONE permission for it. This server drives
  a browser with no audio or video to give one. Structural, not preferential.
* **`J 140 141 142`** -- irreversible acts inside a live hiring process with an
  employer at the other end. `J 142` is the sharpest: LinkedIn documents
  declining as safe, so an automated participation decision would be a career
  call rather than a mechanical one, and nothing here can price it.
* **`J 143 144 145`** -- messages to a human hirer, in LinkedIn's own words
  (*"by contacting the hirer"*). Already the class the shipped
  `auto_accept_or_auto_reply` prohibition names.

The ruling also records `J 144` disagreeing with itself and retires it as a
message rather than smoothing the disagreement, which is why I am content to rely
on it.

**THE 3 HANDED-BACK ROWS ARE NOT UNDECIDED EITHER -- they have a named
successor.** Same document: **`AI-INTERVIEW-RESULTS-NO-ADDRESS`, 3 rows, 3R,
queue MEASURE, cost 4 (allowlist +1, capture +1, parser +1, tool +1), ratio
0.75.** The results (readiness score, strengths summary, transcript) are
CONFIRMED to exist by direct fetch of `a8336402`; their ADDRESS is confirmed
undocumented. Nobody has looked for it.

**AND THERE IS A PRECONDITION THAT IS NOT A PERMISSION QUESTION.** The ruling
puts it exactly right: *"has he ever taken one?"* If he has not, there are no
results to read and the rows are unreachable for a reason that has nothing to do
with this server -- a fact about USE, not about REACHABILITY, and the census
counts reachability. **That is one sentence from the operator, and it is the
cheapest thing on this entire page.** It is a fact only he holds, not a ruling
I am asking him to make.

### VERDICT

**RETIRE -- already done, 11 rows, by `990bbd3` on evidence I have checked and
concur with.** The ledger entry "14 rows, cost 1, DECIDE-RETIRE" should read
**3 rows under `AI-INTERVIEW-RESULTS-NO-ADDRESS`, cost 4, MEASURE, ratio 0.75**,
gated on one factual question to the operator.

---

## 3. `MESSAGING-SETTINGS` -- **ALREADY RE-FILED, 5 OF 5. ZERO LIVE ROWS. AND IT WAS NEVER A NEW DECISION.**

Measured today: `M37 M41 M42 M46 M50` are all `EXCLUDED-RULED` in
`_audit/_census/messaging-and-content.md` (M37 at line 368). Zero remain `GAP`.

**The strongest fact here is that nobody ever owed this decision.** The census
row carries it in its own text:

> **RE-FILED 2026-09-05 as EXCLUDED-RULED under `MESSAGING-SETTINGS` (3.10). NOT
> a new decision -- the operator already made it and two census slices applied it
> differently.**

The ruling is live in the shipped code: `linkedin_update_setting` admits exactly
one page below the settings index, admitted BY NAME on the operator's ruling;
`/psettings/` and `/settings/` are forbidden substrings. **A setting is admitted
by name or not at all** -- that is the mechanism, and it is how dark mode got in.
The profile slice had applied that same ruling to 93 rows as `EXCLUDED-RULED`
while the messaging slice filed five as `GAP`; the ruling says *a setting*, not
*a profile setting*.

The ledger itself had already flagged this as its own open question at L544 and
already carries the inline correction. **The ranking table at L174 is the only
place still publishing 5 rows.**

**REOPENER, carried on every row:** the operator naming a setting. That is not a
gate; it is the documented route in.

### VERDICT

**RETIRE -- already done, and correctly filed as a RE-FILE rather than a
retirement, because the decision predates the blocker.** Strike the ledger row.
Zero rows, zero cost, nothing owed by anyone.

---

## 4. `CONTACT-IMPORT` -- **ALREADY RETIRED, 5 OF 5. ZERO LIVE ROWS.**

Measured today: `N105 N106 N107 N108 N109` are all `EXCLUDED-RULED` in
`_audit/_census/network.md`. Zero remain `GAP`.

`_audit/2026-09-05-decide-retire-rulings.md` section 3.2 retires them on **three
different reasons rather than one**, which is what makes it a ruling rather than
a mood:

* **`N 105`** -- a mobile address-book flow. A browser driver has no address book
  to offer.
* **`N 106`** -- a Gmail import is an OAuth consent screen on Google's domain,
  and this server already ships the rule, quoted verbatim from
  `linkedin_server/server.py`: *"Driving a form on somebody else's domain, under
  their terms, is not this server's to do at any capture quality."* Written about
  applicant-tracking systems; it is a rule about DOMAINS.
* **`N 107 108`** -- sub-steps inside an import that cannot start. Retired WITH
  the flow and explicitly not on their own merits, so they reopen automatically
  if either route does.
* **`N 109`** -- reached by a PERMANENTLY_FORBIDDEN key,
  `any_loop_sweep_or_scheduled_write`: *"one write per invocation, always."* A
  bulk invite is a sweep by construction, and the census calls this row the
  highest-blast-radius row in the whole census. **This one is the operator's
  entry and only he moves it** -- I record whose it is rather than ruling over
  it.

The family was already half-ruled: `N 110` was `EXCLUDED-RULED` under R5 before
this pass. And the ruling correctly bounds itself -- it says nothing about
reading his mail (the `linkedin-jobs` skill already does that from Gmail with no
LinkedIn session) and nothing about `linkedin_send_invitation`, which is built,
per-person and gated.

### VERDICT

**RETIRE -- already done.** Strike the ledger row. Zero rows, zero cost.

---

## 5. `MATCH-DETAILS-COLLAPSED` -- **THE ONLY GENUINELY OPEN ONE. Two of its three questions are already answered, and the cheap route is measured refused.**

Rows `J 116 117 118 119 120`, all five still `GAP`. This is 5 of the 23.

### 5.1 The blocker's founding premise is measured FALSE, twice, and the second time live

Ledger section 6 (L472-484) filed all five as *"present, COLLAPSED behind `Show
match details`"* and queued DECIDE on the premise that *"pressing a disclosure
control is a different permission from reading a render"*.

Amendment A13 (L1202-1250) measured that premise false on one unsanitised
capture, and graded itself honestly: the anchor structure VERIFIED-BY-INSTRUMENT,
the generative reading DERIVED.

**`a14c027`, 2026-09-05, measured BOTH halves live on THREE postings** --
*"probe(jobs): nothing is collapsed, so MATCH-DETAILS-COLLAPSED is misnamed and
its five rows are unreachable"*. The instrument is
`scripts/_probe_match_details_control.py`, and it carries three must-fire needles
so that ten zeros are a reading and not a blind probe:

    Show match details / Create cover letter / Help me stand out
                                        1 visible, 1 html   on all three
    all ten target needles              0 visible AND 0 html on all three
    control elements                    3, all <a>, all with href
    href path                           /preload/guideOverlay/ on all three
    aria-expanded / aria-controls / aria-haspopup    ABSENT on all three

**Nothing is collapsed. There is no region, in any state.**

### 5.2 QUESTION ONE -- "may this server press a disclosure control?" -- IS RULED, AND IT REFUSES THIS CONTROL

`_audit/2026-09-19-the-disclosing-press-ruling.md` names this blocker in its
opening as one of the standing questions filed under it, and **rules the press
PERMITTED under four conjunctive conditions.** Condition 2:

> The control must match an ENUMERATED DISCLOSURE SHAPE, by attribute. Not by
> label text. [...] Anything not on that list is REFUSED.

    press.SANCTIONED_SHAPES  (linkedin_server/press.py:138-141)
        "[aria-expanded]"
        "[aria-haspopup]"

`a14c027` measured both absent on all three postings. **So the press question is
not pending for these rows -- it was ruled, and the ruling refuses this control
by a measurement taken two weeks before it.** That is a decision nobody wrote
back, and it is the second one this wave found.

### 5.3 QUESTION TWO -- "is there a panel to read?" -- IS MEASURED NO

Ten needles, zero in visible text and zero in HTML, three postings, with the
control firing. `How you match` reads 0 in HTML on a settled live posting,
twice, independently (ledger L1244-1247). The blocker's NAME is false: nothing is
collapsed.

### 5.4 QUESTION THREE -- "may this server invoke a generation product?" -- IS GENUINELY UNRULED

Swept the whole repository for a ruling on this. There is none: one DERIVED label
in `_audit/2026-09-19-premium-apply-surfaces.md:237` and nothing else.

**And the AI-INTERVIEW precedent does NOT reach it.** Section 2's three grounds
are a media session this server cannot supply, an irreversible act in a live
hiring process, and a message to a person. `Show match details` is none of the
three. **I will not retire five rows by analogy to a ruling that does not cover
them** -- that would be exactly the "reader's work in both steps" that
`_audit/2026-09-19-premium-apply-surfaces.md` section 2.4 declined a stronger
route for.

### 5.5 MY OWN MEASUREMENT: the "one line" boundary cost is FALSE

A13 (L1252-1254) says: *"`/preload/guideOverlay/` is a sibling of
`/preload/sharebox/`, already on the allowlist -- so the boundary cost would be
one line."*

Measured today against this worktree's own `readonly.py`, with three positive
controls firing first:

    ADMIT   https://www.linkedin.com/feed/
    ADMIT   https://www.linkedin.com/preload/sharebox/
    ADMIT   https://www.linkedin.com/jobs/view/<id>/
    REFUSE  https://www.linkedin.com/preload/sharebox/?foo=bar
    REFUSE  https://www.linkedin.com/preload/guideOverlay/
    REFUSE  https://www.linkedin.com/preload/guideOverlay
    REFUSE  https://www.linkedin.com/preload/guideOverlay/?query=<label>

**Two facts, and the second is the one that matters.** The overlay is not on the
allowlist in any form. And the sibling it was compared to is admitted by an
ANCHORED pattern that takes no query string at all
(`readonly.py:1007`: `^https://www\.linkedin\.com/preload/sharebox/?$`) -- so
`/preload/sharebox/?foo=bar` is refused too.

The overlay is useless without its query: `query` IS the control label, and
`pageContextJobPostingUrns` is what binds the call to a posting. **So admitting it
means admitting a query-bearing address carrying entity URNs -- wider than any
entry currently on that list, and straight into
`tests/test_navigation_is_never_derived.py`, which exists because a real slug
reached a transcript three times.** That is not one line and it is not a
sibling's cost.

### 5.6 VERDICT: UNDECIDED -- and here is the measurement that settles it

**RETIRE is not available**: no shipped rule reaches these rows, and the
capability is documented by LinkedIn.
**BUILD is not available**: the destination is unknown, and the only way to look
at it today is to navigate to an address the boundary refuses -- the measurement
would BE the act it is meant to authorise. That is a real deadlock and I will not
paper it.

**THE MEASUREMENT THAT BREAKS IT, and it needs no new address and no press.**

The three anchors carry ten parameter names. A13 read the values of exactly one
of them (`query`) and read the other nine as names only. Three of the nine are
prose-shaped and are LinkedIn's own declaration of what the destination does:

    intent          originalIntent          customContext

**Read those three VALUES off the posting page this server already loads.** No
new allowlist entry, no press, no click -- `linkedin_job_detail` performs that
navigation today, and `a14c027` already read these anchors' attributes on that
same page.

This is not a new technique. It is exactly what settled the message composer:
upload-sanction section 3b aimed two unnameable, uncountable file inputs by
reading the `accept` declaration LinkedIn authored about them, after a name and a
count had both failed. **A control's own declaration of its destination is a
property to match on where structure has run out.**

Two constraints on whoever runs it, both from this repo's own scars:

1. **Emit a CLOSED VOCABULARY, never the raw values.** The upload probe was
   reduced to `tokens=16 image=True video=True documents=True` for exactly this
   reason, and `_audit/2026-09-05-upload-sanction.md` section 4 measured that a
   dict subscript launders navigation taint past the shipped consent guard. The
   other seven parameters (`conversationUrn`, `contextUrns`, `trackingId`,
   `pageContextJobPostingUrns`, `interop`, `originalThreadMailbox`) must not be
   printed at all.
2. **It must carry a must-fire control.** `a14c027`'s three labels read 1/1 on
   all three postings; reuse them, and report NO VERDICT rather than a page of
   comfortable zeros.

**What the reading decides.** If `intent` names a retrieval, the five rows are
reads behind an address ruling and the question is the ordinary allowlist one. If
it names a generation, the rows are writes of a class this repository has never
ruled on, and THAT is a question for the operator -- with the measurement in hand
rather than a name.

**Cost: one page load on an already-admitted address, plus the probe. The ledger
costs this blocker 3. That was a guess at a build; the measurement is cheaper
than the guess.**

### 5.7 The name is a three-way choice, and it is not mine to take alone

`_audit/2026-09-19-blocker-conflicts.md` section B has already set this out and I
am not relitigating it: `MATCH-DETAILS-COLLAPSED` (committed, and the name the
97-blocker ledger knows), `AI-INTERVIEW-PRODUCT` (a MERGE, which moves five rows
into a retired queue and changes two published counts), `AI-ASSISTANT-OVERLAY`
(A13's proposal, outside the 97, which breaks
`test_the_ledger_tables_still_total_97_blockers_and_409_rows`). **Neither of the
last two is a documentation edit.** The name should follow the 5.6 reading, not
precede it.

---

## 6. WHAT I AM HANDING TO THE LEAD TO INTEGRATE

I moved no census row and edited no census file. Two siblings are building in
other worktrees. These are the exact lines.

**A. The ranking tables are the defect. `_audit/2026-09-03-linkedin-gap-blockers.md`:**

    L171  | 1 | `FILE-UPLOAD-UNSANCTIONED` | 16 | ... | 1 | 16.00 | DECIDE |
    L172  | 2 | `AI-INTERVIEW-PRODUCT`     | 14 | ... | 1 | 14.00 | DECIDE-RETIRE |
    L174  | 4 | `MESSAGING-SETTINGS`       |  5 | ... | 1 |  5.00 | DECIDE-RETIRE |
    L175  | 5 | `CONTACT-IMPORT`           |  5 | ... | 1 |  5.00 | DECIDE-RETIRE |
    L188  | 18 | `MATCH-DETAILS-COLLAPSED` |  5 | ... | 3 |  1.67 | DECIDE |
    L365  | 1 | `FILE-UPLOAD-UNSANCTIONED` | 16 | 16 | 1 | 16.00 | DECIDE |
    L375  | 11 | `MATCH-DETAILS-COLLAPSED` |  5 | 134 | 3 | 1.67 | DECIDE |

All seven publish figures that were true at the 2026-09-03 freeze and are not
true now. **The corrections already exist in the same file, in prose, at L354 and
L544.** The fix is not a better number in a table -- it is that a table nobody
tests against the census will go stale again. `readonly.py` lines 98-112 record
the identical failure and the identical remedy: *"The fix is not a better number.
It is that the number is gone from the prose"* and a test asserts prose against
list.

**B. Four rows are filed under the wrong blocker.** `J 146 147 148 149` are in
`FILE-UPLOAD-UNSANCTIONED` in `_audit/_census/blocker-map.tsv` and in the ledger
at L392. Only `J 146` touches a file. See 1.4. The retire-ruling already flagged
this and declined to act. Whoever owns the map should move them to the
generation-product family, whatever section 5.6 names it.

**C. Three blocker rows should be struck from the ranking as having zero live
rows:** `MESSAGING-SETTINGS` (0), `CONTACT-IMPORT` (0), and
`AI-INTERVIEW-PRODUCT` should be replaced by `AI-INTERVIEW-RESULTS-NO-ADDRESS`
(3 rows, cost 4, MEASURE).

**D. The one question for the operator, and it is a FACT, not a permission:**
*has he ever taken a LinkedIn practice AI interview?* No -> `J 136 137 138` are
unreachable for a reason that is nothing to do with this server. Yes -> they are
the cheapest read on this page and `AI-INTERVIEW-RESULTS-NO-ADDRESS` becomes a
real MEASURE item.

**E. Three rows do not name the blocker that holds them.** `J 136 137 138` in
`_audit/_census/jobs.md:375-377` carry no successor name; it lives only in
`_audit/2026-09-05-decide-retire-rulings.md:300-303`. `990bbd3` wrote the rule
this breaks -- *"EACH ROW CARRIES ITS OWN REASON, NOT A POINTER [...] A reader
who opens the census to check one capability must not have to open a 1563-line
ruling document"* -- and applied it to the 37 rows it edited, correctly not
touching these three. The gap is real and it is a one-cell edit per row, for
whoever owns the map.

---

## 6b. INCIDENTAL, AND REPORTED RATHER THAN FIXED: the identity gate may be BLIND in a linked worktree, not merely runnable in one

Found while verifying that my own commits were gated rather than silently
allowed. **It is not this wave's artifact and I have not touched it.** Stated at
its real strength, because a guard finding that outruns its measurement is the
failure this repository names.

**WHAT IS MEASURED.** `.git/hooks/pre-commit` was fixed on 2026-09-19 to resolve
the interpreter against the MAIN checkout, because a worktree has no venv and
"a gate that cannot run is indistinguishable from a gate that passed". That fix
works: the gate runs, and it loads its gitignored wordlist (`REPO` resolves to
the main checkout, which holds it) -- confirmed, because the gate prints a LOUD
`ALLOWING` when the wordlist is absent and printed nothing on either of my
commits.

**But `scripts/pre_commit_identity_gate.py` asks git which paths are staged with
`cwd=REPO`, and `REPO` is that same MAIN checkout** (`_staged_paths`, and
`_staged_content` does it again). Measured just now, with a file staged in this
worktree and a control:

    cwd = this worktree           rc=0   1 staged path   <- CONTROL FIRES
    cwd = the MAIN checkout       rc=0   0 staged paths
    cwd = MAIN + GIT_INDEX_FILE
          set to this worktree's
          index                   rc=0   2 staged paths  <- and one of the two
                                                            was already COMMITTED

**WHAT THAT MEANS, in the two branches, and I cannot yet say which is real.**

* If git does **not** export `GIT_INDEX_FILE` to a pre-commit hook here, the
  gate enumerated ZERO paths on every worktree commit since the fix, inspected
  nothing, and exited 0. It would be armed, loaded, and blind -- the same class
  of failure the fix was written to end, one layer in.
* If git **does** export it, the gate sees the worktree's index but diffs it
  against the MAIN checkout's HEAD. Measured: that returned a file I had already
  committed here. That over-reports rather than under-reports, which is the safe
  direction, but the set is no longer "paths this commit would write".

**EVIDENCE CLASS.** The three readings above are VERIFIED-BY-INSTRUMENT. Whether
git exports `GIT_INDEX_FILE` to this installation's pre-commit hook is
**UNVERIFIED**, and it is the single fact that decides between the branches.

**THE MEASUREMENT THAT SETTLES IT, in one line and seconds:** echo
`GIT_INDEX_FILE` to stderr from the hook, make one commit from a worktree, read
it. **I did not do it**, and the reason is specific rather than squeamish: that
hook is shared by every worktree in this repository and siblings are committing
through it right now. Editing a live shared gate to measure it is the two-writer
hazard this repo has already disclosed once. It belongs to whoever owns the
hook, at a quiet moment.

**AND IT DOES NOT WEAKEN THIS WAVE'S OWN COMMITS.** Both carry documentation
only, both were checked for non-ASCII bytes before staging, and neither contains
a name, city, employer or campus. `tests/test_no_committed_identity` -- the
shape-based guard the gate's own docstring defers to -- is unaffected by any of
this and runs in CI.

---

## 7. WHAT THIS WAVE DID NOT DO

* **It did not move a census row, run `build_blocker_map.py --write`, or touch
  any file under `_audit/_census/`.** Sections 6A-6C are reports.
* **It did not rule on `MATCH-DETAILS-COLLAPSED`.** It closed two of its three
  questions against committed evidence, refuted the cost claim by measurement,
  and named a reading that needs no new permission. The third question is
  genuinely open and stays open.
* **It did not press, click, navigate, or open a browser.** The only code run
  was `scripts/enumerate_gap_rows.py`, a scratch script calling
  `readonly.is_read_url` on literal strings, and a scratch script running
  `git diff --cached --name-only` for section 6b.
* **It did not edit, fix or instrument the shared pre-commit hook** (6b), and it
  did not settle which of that section's two branches is real.
* **It did not re-verify `a14c027`'s live posting readings, the 2026-09-04
  post-composer read, or the 2026-09-05 `accept` read.** All three are carried
  forward on their own waves' measurements, cited so a reader can go and look.
* **It ran no test suite.** CI runs the tests; nothing here changes code.
* **It did not resolve the name disagreement in 5.7**, which belongs after the
  5.6 reading and not before it.
