# Slice: port the isRendered guard to HARVEST_BLOCK_CARDS_JS

Date: 2026-08-31. Branch `master`, HEAD `77ecd2b`. NOT committed, NOT staged --
edits left in the working tree.

Files changed (exactly the two owned):

* `D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\linkedin_server\dom.py`
  -- 58 lines added inside `HARVEST_BLOCK_CARDS_JS` only, `+0/-0` everywhere
  else. `HARVEST_LINKED_CARDS_JS` and `shape.py` untouched (confirmed by
  `git diff`: both hunks fall between line 346 and the loop at line 420, which
  is inside the string).
* `D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\tests\test_sdui_surfaces_fixture.py`
  -- new section 4c (line 1033), plus one refactor of the existing
  `_notification_rows` helper described below.

---

## 0. READ THIS FIRST -- one instruction I could not satisfy literally

The brief said "Never launch Chrome or any browser; these are offline fixture
tests." It also said to drive the red case "through the real
`dom.harvest_block_cards` path the existing tests use" and to verify with
`pytest tests/test_sdui_surfaces_fixture.py tests/test_readonly.py`.

Those cannot all be true at once: `harvest_block_cards` is `page.evaluate` of a
JS string, and every existing test in that module runs through
`_with_html` -> `playwright.chromium.launch(headless=True)` ->
`page.set_content(...)`. There is no browserless path to the code under test.

I read the instruction as forbidding a LIVE browser (the operator's Chrome, a
real linkedin.com page) and proceeded on the existing harness, because the
mandated verify command runs it regardless. What actually ran:

* headless Chromium `151.0.7922.34` from the repo venv's Playwright.
* `page.set_content()` on markup written in this file. No network, no profile,
  no cookie, no linkedin.com. Nothing was navigated.
* a FRESH `browser` and `page` per call, closed in a `finally` -- isolated by
  construction, one context per measurement. `window.innerWidth` measured 1280
  on every probe run.
* no browser was killed by image name or otherwise.

If that reading is wrong, this slice needs a different design and should bounce.

---

## 1. RED FIRST -- the defect is reachable from the notifications caller

`harvest_block_cards`'s one production caller is
`linkedin_server/server.py:1651`. The new case feeds it a notification card in
the live shape (`article.nt-card` in a `div.nt-card-list`, one anchor, the
timestamp in its own `p.nt-card__time-ago`) whose entire body is repeated in a
`span.visually-hidden` styled `display:none`.

Run against **unmodified** `dom.py`, before any edit to it:

```
$ venv\Scripts\python.exe -m pytest tests/test_sdui_surfaces_fixture.py -k "display_none" -vv

_____ test_a_body_repeated_in_a_display_none_span_is_not_eaten _____

        records, rows, dropped = await _notifications_from(
            notification_card("display:none")
        )

        assert len(records) == 1, records
        # The headline, asserted first, so a regression reports the lost body
        # rather than the mechanism that lost it.
>       assert [row["text"] for row in rows] == [DUPLICATED_BODY], (records, rows)
E       AssertionError: ([{'href': 'https://www.linkedin.com/feed/update/<urn>/', 'text': 'Priya Sharma commented on your post: Congratulations on the launch!
E
E         2h', 'hidden': ['Priya Sharma commented on your post: Congratulations on the launch!'], 'time': '2h', ...}], [])
E       assert [] == ['Priya Sharma commented on your post: Congratulations on the launch!']
E
E         Right contains one more item: 'Priya Sharma commented on your post: Congratulations on the launch!'
E
E         Full diff:
E         + []
E         - [
E         -     'Priya Sharma commented on your post: Congratulations on the launch!',
E         - ]

tests\test_sdui_surfaces_fixture.py:1115: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_sdui_surfaces_fixture.py::test_a_body_repeated_in_a_display_none_span_is_not_eaten
================= 1 failed, 2 passed, 112 deselected in 2.72s =================
```

The record printed in the failure is the whole argument: `hidden` carried the
body, `text` carried it exactly ONCE, so the by-count subtraction spent its one
removal on the visible copy. `parse_notification` was left with no line,
returned `None`, and the row was **dropped** -- `records=1, dropped=1`, the
same signature the Saved tab showed.

**So the defect is reachable, not merely latent.** It is one live page carrying
one `display:none` duplicate away from eating a notification.

### The raw measurement behind it

Probed directly against unmodified `dom.py` (three separate runs, one browser
each, `innerWidth` 1280 on all three):

| hidden span style | card `text` copies | `hidden` | rows | dropped |
|---|---|---|---|---|
| `display:none` | 1 | `[body]` | `[]` | **1 -- THE BUG** |
| `visibility:hidden` | 1 | `[]` | 1 row, body intact | 0 |
| clip pattern | 2 | `[body]` | 1 row, body intact | 0 |

`visibility:hidden` is **not** part of the defect on this script and I did not
dress it up as one. The element IS rendered, so `innerText` runs its rendering
algorithm and returns `''` for it; `textOf()` therefore yields an empty string
and it was never pushed onto `hidden` either way. That matches what 8573b8b
recorded from the other side (there the option moves only its skip counter,
2 -> 0, and leaves the budget identical). The brief asked for both patterns; the
`visibility:hidden` case is pinned as a **measured control**, with its docstring
saying plainly that the guard changes nothing for it.

---

## 2. The guard as ported

Inserted after `textOf` in `HARVEST_BLOCK_CARDS_JS` (`dom.py:395`), verbatim in
behaviour from `git show 8573b8b -- linkedin_server/dom.py`:

```js
  const isRendered = (el) => {
    try {
      if (el && el.checkVisibility) {
        return el.checkVisibility({
          contentVisibilityAuto: true,
          visibilityProperty: true
        });
      }
    } catch (e) { /* fall through to the permissive answer */ }
    return true;
  };
```

and the one call site, in the `if (cfg.hiddenSelector)` loop (`dom.py:420`):

```js
        for (const el of marked) {
          if (!isRendered(el)) continue;
          const value = textOf(el);
          if (value) hidden.push(value.slice(0, cfg.maxChars));
        }
```

Both documented properties are intact: the same
`checkVisibility({contentVisibilityAuto: true, visibilityProperty: true})`, and
UNKNOWN COUNTS AS RENDERED (`return true` on a missing or throwing API). No
different visibility test was invented.

**ONE DELIBERATE DIFFERENCE FROM THE SIBLING, and it is the only one.** The
sibling increments `skippedHidden` and returns it as
`census.hidden_not_rendered`. This script does **not**, because
`harvest_block_cards` returns a bare `list` of cards (`dom.py:768`
`return list(records or [])`, post-edit line number), not an object -- adding a counter means changing
the return shape and therefore every caller, for a diagnostic nothing has asked
this surface for. The skip is a plain `continue`. This is written into the
comment in `dom.py` rather than left for a reader to discover.

The comment block above the helper follows the file's voice: it states the
premise, the measurement with its date, what is deliberately absent, and what
no test reaches.

---

## 3. Green, and the clip pattern STILL CHARGED

After the guard:

```
$ venv\Scripts\python.exe -m pytest -q tests/test_sdui_surfaces_fixture.py tests/test_readonly.py
228 passed in 29.46s
```

(225 before this slice; +3 new cases. `test_sdui_surfaces_fixture.py` now
collects 115.)

The clip control is `test_a_clipped_duplicate_is_still_charged_on_this_surface`
(line 1129). It asserts, in this order:

```python
assert records[0]["text"].count(DUPLICATED_BODY) == 2, records[0]   # both copies really present
assert records[0]["hidden"] == [DUPLICATED_BODY], records[0]        # STILL CHARGED
assert dropped == 0, records
assert [row["text"] for row in rows] == [DUPLICATED_BODY], rows     # exactly one survives
```

The first line is not decoration: without it the rest would also hold of a page
that never had a duplicate to subtract, which is how a control quietly stops
being one. Notifications are the surface the subtraction was built for -- the
six frozen cards in section 4 weld "Unread notification." and a repeated body
onto every innerText -- and all of section 4 stayed green.

---

## 4. Mutation evidence

Each mutation applied to `dom.py`, the three section-4c cases run, then
`dom.py` restored and asserted byte-identical. Mutations B/C/D were textually
scoped to the `HARVEST_BLOCK_CARDS_JS` region so `HARVEST_LINKED_CARDS_JS` was
never edited, not even for the duration of a run.

| # | mutation | result |
|---|---|---|
| **A** | delete `if (!isRendered(el)) continue;` -- the guard itself | **RED.** `test_a_body_repeated_in_a_display_none_span_is_not_eaten` fails, `assert [] == ['Priya Sharma commented ...']`, record shows `hidden: [body]` |
| **B** | `isRendered` always returns `false` (skip every hidden element) | **RED.** `test_a_clipped_duplicate_is_still_charged_on_this_surface` fails, `assert [] == ['Priya Sharma commented ...']`, record shows `hidden: []` with the body present TWICE in `text` |
| **C** | drop `visibilityProperty: true` from the options | **all 3 green -- NOT REACHED** |
| **D** | flip the fallback `return true` to `return false` | **all 3 green -- NOT REACHED** |

A and B are the two that matter and both bite: A proves the fix is load-bearing,
B proves the control is. **C and D are honest holes and are recorded as such in
`dom.py` rather than papered over.** D is dead in this engine by measurement,
not by argument: Chromium 151.0.7922.34 has `checkVisibility` and does not
throw, so the fallback line never evaluates. Both lines are kept anyway --
`visibilityProperty` so the two walks ask the DOM one question instead of
drifting apart, and the fallback because an engine that lacks the API returning
`false` would silently halve every subtraction on this surface. A fallback wrong
in the safe direction is worth more than a line count.

I did not write a test that deletes `Element.prototype.checkVisibility` to reach
D. That was outside the six steps I was given, and the sibling shipped the same
line unreached and said so; inventing coverage for it here would be scope I was
not handed. Flagging it as available if wanted.

---

## 5. Readonly scan (step 6)

```
$ venv\Scripts\python.exe -m pytest tests/test_readonly.py -k "cannot_mutate or scripts_executed_are_exactly"
7 passed, 106 deselected in 0.21s

$ python -c "readonly.scan_js_for_mutations(dom.HARVEST_BLOCK_CARDS_JS)"
[]
```

`checkVisibility` is a read and matches none of the 23 entries in
`readonly.JS_MUTATION_TOKENS`. No forbidden token was introduced.

---

## 6. The one refactor in the test file, declared

`_notification_rows()` (line 854) previously inlined the harvest configuration.
Section 4c needs the same configuration over hand-written markup, so the
harvest moved into `_notifications_from(html)` (line 830) and
`_notification_rows()` became a one-line delegate reading the frozen fixture.
Behaviour is unchanged -- `_with_page` was already
`_with_html(path.read_text(...))`. The motive is the drift hazard: a selector
changed in one of two copies would leave the surface under test and the surface
being pinned quietly different, and all six existing section-4 assertions stayed
green across the change.

---

## 7. HONEST SCOPE STATEMENT

**What is proven.** The defect is a real, reachable mechanism on this caller. A
notification card that repeats its body inside a `display:none` element loses
that body entirely and the row is DROPPED, measured through
`dom.harvest_block_cards` -> `shape.parse_notification` on the exact selectors
`server.py:1651` passes. The guard fixes it, the clip pattern is still charged,
and both facts are mutation-checked.

**What is NOT proven.** *This is not established as what the live notifications
page does.* No live page was read for this slice -- no browser was pointed at
linkedin.com, and nothing here says LinkedIn currently ships a `display:none`
duplicate in a notification card. The markup is written by hand, and it is
written by hand precisely because none of the six captured cards in
`tests/fixtures/notifications.html` carries a non-rendered duplicate. So this
closes a latent hole on a real caller; it does not report a live symptom the way
8573b8b's tracker case did.

**And unlike the sibling, this surface has no instrument that could settle it.**
8573b8b added `census.hidden_not_rendered` so a restart could answer "does the
page actually carry these?" for the tracker. `harvest_block_cards` has no census
path and this slice did not add one (section 2). Confirming the live
notifications page therefore still needs either a census field on this script or
a one-off probe -- neither of which is in this slice. Naming that as an open
question rather than letting the fix imply it was answered.

**Suite.** Not run in full -- three sibling agents are editing other files in
this tree concurrently, per the brief. Only the two mandated modules were run:
228 passed.
