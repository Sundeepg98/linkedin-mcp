# The save refusal that would not say what it saw

**Wave:** save-label diagnostic. **Commit:** `3aa1e32`, on `master`, not pushed.
**Baseline in:** 1732 passed. **Baseline out:** 1742 passed. **`_state/` unchanged.**

---

## 1. The mechanism, verified from the code rather than from the brief

The wave brief supposed that `shape.SAVE_LABELS` holding one row was the cause and
that "LinkedIn is serving a control whose accessible name is something else." The
second half is right. **The first half names the wrong branch, and the difference
decides what the fix has to be.**

The chain, read out of the source:

1. `dom.SAVE_CONTROL` (`dom.py:599`) is assembled from `dom.SAVE_LABELS_SEEN`, a
   one-entry tuple, into the literal CSS selector `button[aria-label="Save the job"]`.
2. `dom.read_save_control` (`dom.py:622`) counts matches for that selector. A posting
   drawing the control under **any** other accessible name matches **zero** elements,
   so the function returns `{"label": None, "count": 0}` and returns before it ever
   calls `get_attribute`.
3. `shape.save_state(None, count=0)` (`shape.py:1101`) therefore enters its
   **`count == 0`** branch -- not the `known is None` unrecognised-label branch -- and
   returns `unknown` with the sentence beginning *"no save control rendered in a state
   this reader recognises."*
4. `writes._live_control` passed that through; `perform` compared `unknown` against
   `spec.from_state == "not_saved"` and raised.

**Why the branch matters.** The brief described the defect as "a gate that measured
something, made a decision on it, and then discarded the measurement before printing."
That is the right instinct about the *symptom* and the wrong account of the
*mechanism*. Nothing was measured and discarded. The gate's only instrument is a
question that can be answered "yes" or with silence, and it got silence. `label` was
literally `None`. So the fix could not be a better print of the first reading -- there
was nothing in it. It had to be **a second, wider read**, taken only where the first
one is about to refuse.

### Reproduced offline, before anything was written

Derived `tests/fixtures/job_detail_hydrated.html` with the one attribute changed, and
drove the real reader over it in a local headless Chromium:

```
--- as captured ---
  read_save_control -> {'label': 'Save the job', 'count': 1}
  save_state.state  -> not_saved
--- relabelled ---
  read_save_control -> {'label': None, 'count': 0}
  save_state.state  -> unknown
  save_state.why    -> no save control rendered in a state this reader recognises. ...
  page really had   -> ['More options', 'Saved', 'Dismiss', 'Not now', 'Follow']
```

That last line is the whole indictment: five controls were sitting on the page and the
reader walked past all of them, because a CSS selector asking for one exact string
cannot report what it did not match. This is pinned as
`test_the_refusal_the_operator_saw_is_the_count_zero_branch`.

---

## 2. The change

`dom.read_save_candidates` is the second read. `writes._save_candidates_note` turns it
into prose, and `writes._live_control` appends that prose **on the `unknown` branch
only** -- a state that came back known-but-wrong was read off a label the message
already names, so a second sweep there would be round trips spent on repetition.

Three fields, deliberately the same shape as the apply fix's `buttons_total` /
`advance_scan_complete`, plus one the apply fix did not need:

| field | why it exists |
|---|---|
| `candidates` | the shaped, filtered accessible names actually on the page |
| `matched_total` | **not** `len(candidates)`: the list is a set of shapes, so two controls both labelled `Saved` collapse to one entry, and "the page drew two save controls" is what separates a rename from a page the reader cannot scope |
| `buttons_total` | how many labelled controls were counted |
| `scan_complete` | whether the walk finished -- false on over-limit, on a control that would not read, and on a raising locator |

### Behaviour did not change

- `shape.SAVE_LABELS` still holds exactly one row. Nothing was guessed into it.
- An unrecognised state still refuses. There is no fallback that clicks on `unknown`.
- `dom.save_control_selector` still raises for every label outside `SAVE_LABELS_SEEN`,
  so **a name reported in the diagnostic cannot become a click by having been
  reported**. Pinned as `test_a_reported_label_still_cannot_become_a_click`.

### Member privacy, and a leak closed on a path that already existed

The brief asked me to reuse `shape.py`'s census reduction. I did, and it is **not
sufficient on its own** -- stating that plainly because the gap is the reason the
design has two gates rather than one. `census_shape` returns an ASCII name under 60
characters verbatim; the census's actual privacy property comes from combining it with
`census_redact_rare` (which needs a per-surface count) and `census_href_identifies_entity`
(which needs an href). Neither is available on a button sweep of one posting. So this
takes the brief's stated fallback -- a conservative pattern, disclosed in the payload:

1. the accessible name must carry the **whole word** `save`/`saved`/`unsave`/`unsaved`;
2. what survives is reduced by `shape.census_shape`.

**The word boundary is load-bearing and it closed a live leak.** The sweep's existing
filter was `"sav" in text.casefold()`, which also matches the member names *Savita* and
*Savannah* -- on a page that draws a hiring team and a "people also viewed" rail. That
filter was not only mine to inherit: it governs `dom.read_any_save_control_label`,
whose **raw** value `writes.perform` prints after a supervised save. So the substring
rule was a member-name filter that let member names through, on a path that already
shipped. Both now share one walk and one filter.

`census_redact_rare` is deliberately **not** applied, and that is a decision rather
than an omission: it blanks a run of two capitalised words in any shape seen once, and
the save control is drawn once -- a genuine ON label reading `Saved Job` would come
back `<redacted>`, destroying the exact measurement the function was called to take.

The same shared walk also replaces `read_any_save_control_label`'s silent
`min(total, 60)` with the reported `dom.SAVE_SCAN_LIMIT = 200`. That silent cap was the
identical defect class, sitting inside the one instrument meant to cure it.

### What it now says

Over the derived page whose control reads `Saved`:

```
refusing to click: 'save_job' is valid only from 'not_saved' and the control on the
page reads 'unknown'. no save control rendered in a state this reader recognises.
[...] WHAT WAS ON THE PAGE: 7 labelled controls, ALL of them read. Save-worded
controls: 1, reading ['Saved']. THAT IS THE MEASUREMENT THIS REFUSAL EXISTS TO
PRODUCE -- and it is not yet the fix. Which state such a label MEANS has to be
established before it is written into shape.SAVE_LABELS, because a label mapped to
the wrong state points a click at the opposite action; a name that does not say its
own direction is not a measurement. Filtered, and deliberately: only controls under
<main> whose accessible name carries the whole word save/saved/unsave/unsaved are
reported, and each is reduced by shape.census_shape. A job posting names its hiring
team and a 'people also viewed' rail, so the full control list is never printed. A
rename to a word outside that set therefore shows up here as zero candidates against
a non-zero scan, which is itself the finding.
```

### The diff

The full production diff is `git show 3aa1e32 -- linkedin_server/dom.py
linkedin_server/writes.py` (329 lines). The two behavioural hunks:

```diff
--- a/linkedin_server/writes.py
+++ b/linkedin_server/writes.py
@@ _live_control, save family fall-through
-    return (
-        str(verdict.get("state") or UNKNOWN),
-        str(verdict.get("why") or ""),
-        dom.save_control_selector(anchor),
-    )
+    state = str(verdict.get("state") or UNKNOWN)
+    why = str(verdict.get("why") or "")
+    if state == UNKNOWN:
+        # A REFUSAL THAT REPORTS NOTHING IT SAW MAKES GUESSING THE ONLY WAY
+        # FORWARD, and on a toggle a guessed label performs the opposite
+        # action -- which is the failure this whole gate exists to prevent.
+        why = f"{why} {_save_candidates_note(await dom.read_save_candidates(page))}"
+    return (state, why, dom.save_control_selector(anchor))
```

```diff
--- a/linkedin_server/dom.py
+++ b/linkedin_server/dom.py
@@ the sweep's filter
-    for index in range(min(total, 60)):
-        ...
-        if text and "sav" in text.casefold():
+SAVE_SCAN_LIMIT = 200
+_SAVE_WORD = re.compile(r"\b(?:un)?saved?\b", re.IGNORECASE)
+SAVE_SWEEP_SELECTOR = "main button[aria-label], main a[aria-label]"
+    ...
+        if text and _SAVE_WORD.search(text):
```

`SAVE_SWEEP_SELECTOR` covers anchors as well as buttons: every capture draws the save
control as a `<button>`, but the apply control beside it is an `<a>` in every capture,
so a save control that had become an anchor is a shape worth being able to see.

---

## 3. The tests, each shown failing at the mutation it catches

`tests/test_save_candidates_fixture.py`, 10 tests. **Against the unfixed production
code, 8 of 10 fail.** The headline one fails at the defect itself rather than at a
missing attribute -- it drives the real `perform` over a real grant, watches the
refusal happen correctly, and fails on the sentence:

```
    with pytest.raises(WriteAttemptError) as caught:
        await writes.perform(nav, browser_page, grant)
    message = str(caught.value)
    assert "refusing to click" in message        # passes
    assert "reads 'unknown'" in message          # passes
>   assert "'Saved'" in message, message
E   AssertionError: refusing to click: 'save_job' is valid only from 'not_saved' and
E   the control on the page reads 'unknown'. no save control rendered in a state this
E   reader recognises. That is NOT evidence the posting is unsaved, and it is not
E   evidence it is saved either: [...] This reading is fresher than the one in the
E   preview and it wins.
```

The two that pass both before and after are guards asserting behaviour did **not**
change, so they were mutation-tested separately. Every guard in the module was driven
against a mutation of the thing it protects; all five went red:

| mutation | guard | failure |
|---|---|---|
| filter back to `"sav"` substring | `..._member_name_containing_sav_is_not_reported` | `assert ['Saved', 'Savita Krishnan'] == ['Saved']` |
| `SAVE_LABELS_SEEN` widened by a guess to include `"Saved"` | `..._reported_label_still_cannot_become_a_click` | `Failed: DID NOT RAISE ExtractionFailedError` |
| over-limit page calls itself scanned | `..._empty_list_and_an_unfinished_scan_do_not_look_alike` | `assert ['Saved'] == []` |
| `census_shape` dropped from the payload | `..._save_worded_label_is_still_reduced...` | `assert ['Saved xxxx...'] == ['<opaque>']` |
| anchored reader stops matching | `..._recognised_control_still_reads_not_saved...` | `assert {'label': None, 'count': 0} == {'label': 'Save the job', 'count': 1}` |

The unreadable-control branch (`scan_complete` false because one node raised) is driven
over a fake page object, because a DOM cannot be made to fail one `get_attribute` and
not its neighbours.

---

## 4. What the lead should call, and where to read the answer

**The vocabulary half is blocked, and not for the reason the brief anticipated.** The
`mcp__linkedin__*` tools ARE exposed to me this wave. The block is structural: the
diagnostic lives in **gate 5**, inside `writes.perform`, which is reached only by
redeeming a `confirm_token` -- and passing one is forbidden to me and is the lead's
call to make, not mine.

I checked for a read-only route and there is none:

- `linkedin_surface_census` takes a key from a fixed set `{feed, profile, settings}`
  and **never a url** (`server.py:1566`), so it cannot be pointed at a posting.
- `readonly.py` contains no read of the save control, so `linkedin_job_detail` does not
  report its label either.

So the measurement costs exactly one redeemed save, and the call is:

```
linkedin_save_job(job_id="4456021840")                      # preview, mints a token
linkedin_save_job(job_id="4456021840", confirm_token="...") # redeem within 2 minutes
```

**Read the answer from the `message` field of the returned dict.** The refusal reaches
the caller through `server._error`, which returns `{"error": ..., "message": scrub(str(exc))}`
-- there is no structured field, so the diagnostic is deliberately in the message text.
Look for the sentence beginning `WHAT WAS ON THE PAGE`. Three outcomes:

- **`Save-worded controls: N, reading [...]`** -- the label(s). This is the measurement.
- **`NOT ONE carries a save word`** against a non-zero total -- the control was renamed
  off the save vocabulary entirely, or the posting renders none. Bigger problem than a
  rename; do not widen the word list to chase it without a capture.
- **`WHAT WAS ON THE PAGE IS UNKNOWN` / `ONLY PARTLY KNOWN`** -- the scan did not run or
  did not finish. The list is a floor, not an inventory.

If the redemption instead **succeeds**, the label comes back in the existing `became`
field, which `read_any_save_control_label` fills from the same sweep -- raw, because
that is the string a human copies into `shape.SAVE_LABELS`.

### The half I did not do, and the condition on doing it

Adding the observed label to `shape.SAVE_LABELS` is **not** done here, and it should not
be done from the label alone. A name has to be mapped to the state it *means*, and
`Saved` is genuinely ambiguous about direction: it can be read as "this job is saved"
(state `saved`, so `unsave_job` becomes valid from it) or as an imperative. `Unsave the
job` names its own inverse and is unambiguous; `Saved` does not and is not. If the
measurement comes back `Saved`, the honest next step is a corroborating read of the
saved list on the same posting, not a table edit. The refusal text says so on its own
face, so the next reader gets the caveat without needing this document.

---

## 5. Receipts

**Suite.** `venv\Scripts\python.exe -m pytest -q`

- Before, at `21d9ba0`: `1732 passed in 444.07s`. The brief's 1730 was stale by two;
  reporting what I measured.
- After the code change, before committing: `1742 passed in 437.08s` -- 1732 + the 10
  new tests, zero regressions.
- **Final, on the committed tree: `1746 passed in 399.50s`, zero failures.**

**The total is not a constant, and the extra four above the ten are not tests I wrote.**
`test_no_committed_identity` and `test_path_hygiene` are parametrized over TRACKED
files, so committing a file adds test cases. `1732 -> 1746` is the 10 new tests plus 4
parametrized entries for files that became tracked during the wave -- this audit, the
test module, and the concurrent writer's audit. Anyone re-deriving the delta by
subtraction should expect that gap rather than read it as coverage from nowhere.

**One red on the way, and it was the repo catching me.** The first committed draft of
this file failed `test_no_committed_identity`: the full `session.json` digest I pasted
as a receipt contains a ten-digit decimal run that matches the Indian-mobile shape. The
fix was to shorten the receipt, twice -- the second time because the sentence explaining
the first fix quoted the offending run. The guard was not touched and no allowance was
declared for it.

**`_state/` untouched.** `_state/session.json` is byte-identical, same size and same
mtime as at wave start:

```
before  sha256 f0892e35688868fa...  7813 bytes  Aug 26 00:41
after   sha256 f0892e35688868fa...  7813 bytes  Aug 26 00:41
```

(The digest is printed as a 16-hex-character prefix, not in full, and that is not
tidiness. `test_no_committed_identity` refused the first draft of this file: further
into the digest sits a run of ten consecutive decimal digits opening `9`, which is the
shape of an Indian mobile number. The guard cannot tell that run from a real one and
should not try, so the receipt got shorter rather than the guard weaker -- and this
sentence names the shape without reproducing it, which is the second half of the same
lesson. Re-derive in full with `sha256sum _state/session.json`.)

The Chrome profile was never launched from a script; every reading in this wave was
taken by the test suite's own local headless Chromium over frozen local HTML, which
touches no profile and makes no network request. `git status` after the commit shows
only the audit file.

**Commit.** `3aa1e32 fix(save): the refusal that would not say what it saw` on `master`,
**not pushed**. No `Co-Authored-By` line. Files: `linkedin_server/dom.py`,
`linkedin_server/writes.py`, `tests/test_save_candidates_fixture.py`
(622 insertions, 20 deletions).

**All files ASCII-clean**, verified by byte scan.

**A second writer was in this tree.** `f2b9a3c docs(audit): five of the nine, measured
live` landed at 11:16, between the baseline run and this commit, and is now the parent
of `3aa1e32`. It is **docs-only** -- one new file, `_audit/2026-08-30-nine-live-census.md`,
87 lines, no code and no tests -- so the 1732 baseline is still a baseline for this
change and `1732 + 10 = 1742` holds. No file is touched by both commits. Recorded rather
than assumed away, because the arithmetic would have been wrong had it carried tests.

No `_TEAM_LEAD_*.md` ruling was present at the worktree root or its parent at freeze.

---
---

# Part 2 -- the measurement arrived, and it was not a label

**Commit:** `08c8936`, on `master`, not pushed. **Suite: 1746 -> 1756.** `_state/` unchanged.

The lead redeemed a token twice against `4456021840`, forty seconds apart, and got:

```
attempt 1: 2 labelled controls, ALL of them read, and NOT ONE carries a save word.
attempt 2: 1 labelled controls, ALL of them read, and NOT ONE carries a save word.
```

Running it twice is what produced the finding. **A renamed control gives a stable
count.** A count that moves is a page in a different state of readiness each time.

## What Part 1 got wrong, stated plainly

The sentence my own diagnostic printed on that reading was not merely uninformative.
**It asserted a false conclusion:**

> *"So this is not a save control wearing a new name -- either the posting renders no
> save control at all, or it renders one worded in a way no rule here anticipated."*

Both branches of that sentence are claims about **LinkedIn's vocabulary**, and a page
that never finished drawing supports neither. Part 1 fixed a refusal that said nothing;
it replaced it with one that said something wrong, with more confidence. That is the
worse of the two failures, and it is the one the lead's second run caught.

## The hypothesis survives, with one correction to its evidence

The lead's reading -- *the interactive layer has not attached* -- is **verified**. But one
plank of its support has to be removed, because it points the other way:

> *"the SAME call read the posting's real title and employer off the page"*

That is not corroboration. Measured on a derived page with every `<button>` stripped and
nothing else touched:

| what survives with zero buttons | value |
|---|---|
| `job_detail_is_believable` | **True** |
| company read | `Ashgrove Systems` |
| apply controls | **1** |
| buttons under `<main>` | **0** |

Title, employer and the apply control all survive the exact state we are trying to
detect -- the first two because LinkedIn server-renders them, the third because the apply
control is an `<a>` and anchors attach before buttons. So reading them correctly says
nothing at all about whether the controls had drawn. The hypothesis is right; this
particular reason for believing it was not a reason.

## The refutation attempt, and what it killed

The lead named the refutation: if the count is small and unstable even on a definitely
rendered page, the inference is worthless. So the discriminator must **not** be the total
count. Measured across every job capture in the repo, counting `<button>` under `<main>`:

| capture | buttons |
|---|---|
| `job_detail_shell` (un-hydrated) | **0** |
| `job_detail_following` | 2 |
| `job_detail` | 8 |
| `job_detail_hydrated` | 8 |
| `job_detail_following_hydrated` | 12 |

Zero on the shell; never fewer than two on a posting that drew. That is the signal, and
`test_the_hydration_discriminator_is_measured_not_argued` pins it, so a future capture
breaking the premise fails in the suite rather than in a live refusal telling somebody
their page never rendered.

**The obvious candidate was tried first and it failed.** The apply control is present in
all four rendered captures and is measured across thirteen -- and it is an `<a>`, so it
survives on an unattached page (table above). A readiness signal that cannot fail in the
state it exists to detect is not a signal. That is now an assertion in a test rather than
a preference in a comment.

**Honest limit:** five captures of two postings. I cannot rule out a real posting that
renders one or two buttons -- which is exactly why the count is a **reported
discriminator** and never a gate. The gate waits for the save control itself.

## The design

The existing settle is the root cause and deserves naming: `browser.goto` tries
`networkidle`, LinkedIn's long-poll connections mean it "rarely settles" (its own
comment), so **every read falls through to a flat `SETTLE_MS = 3500` timer**. The read
lands wherever 3.5 seconds happens to put it. The 2-then-1 reading is that bet losing
twice in a row.

`dom.wait_for_save_control` waits for the control to **attach** -- a named element, not a
duration -- bounded at `SAVE_READY_TIMEOUT_MS = 10_000`, **one wait and one verdict, no
retry loop**. Measured cost on a ready page: **27ms**. On timeout it REFUSES, and the
refusal now leads with which failure it was:

| evidence | verdict |
|---|---|
| control attached | `THE CONTROL LAYER IS READY` -- not a timing artefact |
| timeout, `main_buttons_total == 0` | `THE PAGE NEVER BECAME READY` + **`DO NOT WIDEN shape.SAVE_LABELS`** |
| timeout, `main_buttons_total >= 1` | `THE PAGE WAS READY AND THE CONTROL WAS NOT THERE` -- a vocabulary finding |
| non-`TimeoutError` failure | `THE READINESS CHECK ITSELF FAILED` -- evidence for neither |
| count unavailable | `WHETHER THE PAGE WAS READY IS UNKNOWN` |

The sweep also splits its total into buttons and links, which is what makes the live
reading legible: **2 labelled controls = 0 buttons + 2 anchors**, on a page carrying zero
buttons of any kind. Not two mysterious controls -- the anchor layer, alone.

`shape.SAVE_LABELS` is untouched. One row. No label has been observed and there is
nothing to widen it with.

## The red

Against the shipped Part 1 build, the two states produce verdicts differing by **one
digit**, both carrying the same false conclusion:

```
BUTTON LAYER NEVER ATTACHED : WHAT WAS ON THE PAGE: 2 labelled controls, ALL of them
                              read, and NOT ONE carries a save word. So this is not a
                              save control wearing a new name -- either ...
READY, CONTROL RENAMED AWAY : WHAT WAS ON THE PAGE: 7 labelled controls, ALL of them
                              read, and NOT ONE carries a save word. So this is not a
                              save control wearing a new name -- either ...

DIFFERENCE BETWEEN THE TWO VERDICTS:
    -WHAT WAS ON THE PAGE: 2 labelled controls ...
    +WHAT WAS ON THE PAGE: 7 labelled controls ...
```

Through the real gate, with the wait stubbed out as always-ready:

```
E  AssertionError: refusing to click: ... THE CONTROL LAYER IS READY: the save control
E  attached after 0ms of a 0ms wait ... WHAT WAS ON THE PAGE: 2 labelled controls --
E  0 button(s) and 2 link(s), with 0 button(s) of any kind under <main> ...
E  assert 'NEVER BECAME READY' in "refusing to click: ..."
```

**Two mutations came back GREEN on the first pass, and both were real:**

1. *"readiness failure opens the gate"* was **mis-aimed** -- `if state == UNKNOWN:`
   appears twice in `writes.py` and my script hit the wrong one. Re-run against the right
   anchor: red.
2. *"an unreported button count defaults to zero"* was correctly aimed at code **no test
   reached** -- every note test hand-builds its own dict and never drives the sweep. A
   genuine gap, and it sat on the discriminator's own default: the value that decides
   whether a page gets told it never rendered. Closed by
   `test_a_button_count_that_failed_is_reported_as_unreported`, which goes red at that
   mutation with `assert 0 is None`.

Ten new tests (20 in the module). Every guard shown failing at its own mutation: the wait
deleted, the discriminator ignored, a locator failure relabelled as a timeout, the wait
re-raising, the button/anchor split collapsed, the diagnostic dropped from the refusal,
the wait never called.

## Question 4: `linkedin_job_detail` -- a SEPARATE wave, and here is why

The lead's two `extraction_failed` results are the **same root cause and a different
layer**, so the same condition will not serve.

- The save gate fails when the **button layer** has not attached. The text layer was
  fine -- `_read_posting_facts` passed, which is why a confirm gate was rendered at all.
- `linkedin_job_detail` fails at `server.py:1124` when the **text layer** has not
  rendered: `job_detail_is_believable` is false. A wait for the save control would not
  help it, and a wait for body text would not help the save gate.

Two further reasons to keep it separate rather than widen this wave: it is a **read**
path, carrying none of this one's click risk and none of its urgency; and it has a defect
of its own that wants its own measurement. Its message says:

> *"Either the page had not finished rendering, or the posting is no longer there."*

That is **two failures wearing one sentence** -- the identical defect this wave just fixed
for save, still live on the read path. Separating them needs a capture of a removed
posting, which this repo does not hold and nobody has taken. That is a wave with a
measurement in it, not a patch.

**Recommendation:** a follow-up wave covering both -- a readiness condition on the
`job_detail` text layer, and a discriminator between "not rendered" and "posting gone".
Not started, and not silently begun.

## Receipts, part 2

- **Suite:** `1756 passed in 321.73s`, zero failures, on the committed tree. Previous was
  1746, **not 1742** -- that figure predates Part 1's own audit commits, and the
  parametrized identity and path-hygiene guards grow with the tracked-file count.
- **`_state/session.json` byte-identical**, still `sha256 f0892e35688868fa...`, 7813
  bytes, mtime Aug 26 00:41. The Chrome profile was never launched from a script; every
  reading here was taken by the test suite's local headless Chromium over frozen local
  HTML.
- **No `confirm_token` was passed by me at any point.** The live measurement is the
  lead's; every state reproduced above is a local derived fixture.
- **Commit** `08c8936` on `master`, not pushed, no `Co-Authored-By`. All files ASCII-clean.

---
---

# Part 3 -- the reader-difference theory is wrong, and the table is not stable

**Commit:** `13bd75a`, on `master`, not pushed. **Suite: 1756 -> 1764.** `_state/` unchanged.

The lead asked me to kill this theory if it was wrong rather than let it be inherited.
**It is wrong.** Both halves of it are wrong, and each for a different reason.

## 1. There is no second implementation. There is one reader, written out twice

`linkedin_job_detail` (`server.py`) and `writes._read_posting_facts` do this:

```python
identity = await dom.read_job_identity(page)
detail = shape.parse_job_detail(
    await dom.read_main_text(page),
    company=identity.get("company"),
    document_title=identity.get("document_title"),
)
```

Character for character the same, in the same order, behind the same navigation
(`BROWSER.goto`, `wait_until="domcontentloaded"`, then the same flat `SETTLE_MS = 3500`).

| | `linkedin_job_detail` | the save gate's facts read |
|---|---|---|
| selectors | `read_job_identity` + `read_main_text` | **identical** |
| wait strategy | `BROWSER.goto`, networkidle-then-flat 3500ms | **identical** |
| readiness condition | **none** | **none** |
| treats as "rendered" | `title` and `description` | `title`, `description`, **and `company`** |
| url | `/jobs/view/<id>` | `/jobs/view/<id>/` |

Only two things differ, and neither can produce the observed table.

## 2. The one difference that looked like strictness is DEAD CODE

The write gate read `if not job_detail_is_believable(detail) or not detail.get("company")`.
For that second term ever to be the deciding one, a reading would have to be believable
**and** carry no company. **No such reading exists**, because
`shape.job_title_from_document_title` returns `None` when the employer is unknown:

```
company     believable  title                         company       extra clause decides
None        False       None                          None          False
''          False       None                          None          False
'   '       False       None                          None          False
'Ashgrove'  True        'Backend Engineer | Remote'   'Ashgrove'    False
```

Company absent forces title absent, so the base requirement has already failed. **The two
readers are behaviourally identical.** I asserted the opposite in Part 2 -- I wrote that
the write gate "is STRICTLY STRICTER" -- and that was wrong in effect, though right in
text. It is corrected here rather than quietly.

Empirically confirmed as well: across all five job captures plus two derived failure
states, the two requirement sets never reach opposite verdicts
(`test_the_two_read_paths_agree_on_every_captured_state`).

## 3. The cells are not stable -- I flipped one myself

The disagreement table treats each cell as a property of (posting x reader). Measured
live today, one session, reads only, no tokens:

| call | lead, ~1h earlier | me |
|---|---|---|
| `linkedin_job_detail(4456021840)` Gunpowder | failed ~4/4 | **failed** 1/1 |
| `linkedin_job_detail(4448301715)` Fivetran | **succeeded 2/2** | **failed 3/3** |
| `linkedin_search_jobs` | rendered fine | **rendered fine** -- 7 results, full data |

**The Fivetran cell has now produced both outcomes.** Same reader, same url, same build,
one hour apart. And `linkedin_search_jobs` returned complete results in the same session
seconds after the failures, so the session, the auth and the browser were all healthy --
the failure is specific to the standalone `/jobs/view/<id>` surface.

That is the answer to "the variable is the reader": **it is not.** The variable is time,
and the table was assembled from single readings of a surface that disagrees with itself.

Two smaller facts fell out of the same run:

- LinkedIn **does not redirect** `/jobs/view/<id>` to the trailing-slash form -- the
  error payload's `url` (which is the post-redirect `final_url`) comes back without the
  slash. So the url difference is real but inert: two different urls, both served, same
  page.
- I could not run the save-gate side myself. `linkedin_save_job` was **denied by the
  permission classifier**, even in its preview form. I did not work around it. So the
  write-side column of the table above is the lead's measurement only, and the code
  argument in sections 1-2 is what carries that half.

## 4. The ruling

**They must keep different requirements; they must not keep different implementations.**
The lead's prior was half right, and the half that was wrong matters.

- *Different requirements, deliberately.* `linkedin_job_detail` hands a posting to a
  human; a missing employer is a degraded but honest result. The save gate renders a
  confirm block the operator reads before authorising an irreversible action; a block
  that cannot name the employer is one he cannot check the job against. Collapsing them
  would either weaken the gate or break the read tool on postings with no parseable
  employer.
- *Same implementation, now enforced.* `dom.read_job_posting` is the single reader.
  `shape.JOB_DETAIL_REQUIRED` and `JOB_DETAIL_REQUIRED_FOR_GATE` declare the thresholds
  as data. The dead clause is gone -- replaced by the named requirement, kept because
  the intent outlives the coupling: if title extraction ever stops depending on company,
  the gate must still demand it. A test fires if that day comes.

## 5. What the refusal says now

The old sentence offered two theories and no way to choose:

> *"Either the page had not finished rendering, or the posting is no longer there."*

Both are about the posting, and today's measurement shows a third possibility neither
covers -- the surface failing while the account is fine. So it now reports evidence:
which fields were missing, whether `<main>` existed, and how much text it carried,
against measured ranges.

**A page that has not drawn is not an empty page**, and that is the trap the numbers had
to close. Measured across the captures:

| capture | `main` chars | missing |
|---|---|---|
| `job_detail_shell` | 1092 | title, description |
| `job_detail_following` | 1358 | description |
| `job_detail` | 5648 | -- |
| `job_detail_hydrated` | 5648 | -- |
| `job_detail_following_hydrated` | 18440 | -- |

The shell renders an aside, a footer and a language picker, so "it rendered something"
is true of a page carrying no posting at all. The refusal now quotes both ranges so the
number it prints is placeable. It also names `linkedin_search_jobs` as the control that
separates a broken session from a broken surface, and asks for a repeat before anything
is concluded -- because every wrong theory in this investigation, mine included, was
built out of single readings.

## 6. The finding that reframes the save question

`job_detail_following` **carries a save control and an apply control while its
description has not arrived.** So the control layer and the text layer render on
independent schedules, and neither one being present is evidence about the other.

That retires the last shape of the hydration story: "the save control is missing" and
"the posting could not be read" were never two views of one fact, and a page can be
ahead on either axis. It also means the Gunpowder observation the lead flagged --
`job_detail` failing while the save gate's facts read succeeded -- needs no reader
difference to explain it at all. One reader, one page, two moments.

## 7. On the readiness floor (ask 4)

The verdict boundary is `0` vs `>= 1` buttons, not `>= 2` -- the `>= 2` was only ever an
assertion about the captures. The lead is right that three is a weak pass. But a floor
would be the wrong instrument: `job_detail_following` draws **two** buttons and still
carries a save control, so a low count does not by itself mean the control is absent.

What IS true of every capture: **all four rendered captures carried exactly one save
control regardless of button count.** So "3 buttons and no save control" matches no
capture on record. The verdict now says exactly that, and carries the count and the
observed ranges with it, so a weak pass is visible to the caller as a weak pass rather
than as READY. No floor invented.

## 8. Receipts, part 3

- **Suite:** `1764 passed in 425.49s`, zero failures, on the committed tree. Previous
  1756, which matches the lead's figure.
- **Eight new tests** (28 in the module), each shown failing at its own mutation: the
  dead clause becoming live, the two requirement sets genuinely diverging, `main_chars`
  collapsed to zero, no-main and empty-main sharing a sentence, the control sentence
  dropped, the readiness caution dropped, and a presence-check failure reported as an
  absent `<main>`. **Two mutations came back green first and both were mine:** one
  changed both requirement sets together and therefore proved nothing, and one found a
  real gap -- a presence default no test drove, closed by
  `test_a_main_presence_check_that_failed_is_not_a_missing_main`.
- **Live calls: reads only.** Five `linkedin_job_detail`, one `linkedin_search_jobs`, one
  `linkedin_auth_status`. **No `confirm_token` was passed.** `linkedin_save_job` was
  denied by the permission classifier and was not worked around.
- **`_state/session.json` byte-identical**, `sha256 f0892e35688868fa...`, 7813 bytes,
  mtime Aug 26 00:41. The Chrome profile was never launched from a script.
- **Commit** `13bd75a` on `master`, not pushed, no `Co-Authored-By`. All files ASCII-clean.

## 9. What I would measure next, and what I would not

**Would not:** anything built on a single reading of `/jobs/view/<id>`. That surface has
now been measured disagreeing with itself, and three theories have died on it.

**Would:** the paired control. Every future job-page reading should be taken with a
`linkedin_search_jobs` call beside it and repeated at least twice. The refusal now says
so on its own face, so the next person does not need this document.

**Still open, and I am not guessing at it:** why `/jobs/view/<id>` renders its body
sometimes and not others while the search surface never fails. Candidates not yet
separated -- LinkedIn throttling the standalone posting route after repeated automated
loads; the two live server processes contending for one profile; a genuine client-side
render race that the flat settle sometimes wins. Separating them needs a run that varies
one thing at a time, which is a wave with a measurement in it. **Not started.**
