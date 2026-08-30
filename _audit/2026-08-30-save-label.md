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

- Before: `1732 passed in 444.07s`. The brief's 1730 was stale by two; reporting what I
  measured.
- After: `1742 passed in 437.08s` -- 1732 + the 10 new, zero regressions.

**`_state/` untouched.** `_state/session.json` is byte-identical, same size and same
mtime as at wave start:

```
before  f0892e35688868faef6a3525e54b93e4fd9605770562bc5540d0b133b3165152  7813  Aug 26 00:41
after   f0892e35688868faef6a3525e54b93e4fd9605770562bc5540d0b133b3165152  7813  Aug 26 00:41
```

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
