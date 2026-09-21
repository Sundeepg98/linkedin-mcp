# Analytics press preflight -- OFFLINE slice for `what-is-reachable-now`

Scope: closed-form offline inventory for a possible live press on
`/analytics/profile-views/` against `N 134` (`_audit/_census/network.md`) and
`P O3` (`_audit/_census/profile.md`). No browser was opened. Every call below
was driven in-process against the shipped `linkedin_server` package, via the
venv interpreter, from a throwaway script outside the worktree. Nothing in
this repo was executed with a live page.

---

## 1. THE FOUR CONDITIONS, RUN OFFLINE FOR `/analytics/profile-views/`

Driven in-process, `url = "https://www.linkedin.com/analytics/profile-views/"`:

```
>>> press.check_address(url)
{'pressed': False, 'admitted': True}

>>> press.check_shape('[aria-expanded]')
{'pressed': False, 'shape_ok': True}

>>> press.check_basis(url)
{'pressed': False, 'basis_declared': True, 'basis': 'structural',
 'requires_counters': []}

>>> press.sensitivity_basis(url)
{'kind': 'structural',
 'why': "(1) THE SURFACE ADDRESSES NO ONE -- it renders his own "
        "profile-view analytics, with no recipient, no composer, no "
        "third-party subject and nothing naming another account as a "
        "destination; on this package's DESTINATION vs CONTENT line an "
        "outward effect requires a destination and this page has none. "
        "(2) THE PRESS TARGET'S SEMANTICS ARE VISIBILITY, NOT SUBMISSION "
        "-- aria-expanded denotes the expanded state of a region the "
        "control owns, over content already delivered to the client. "
        "(3) THE RULING ALREADY REFUSES THE ALTERNATIVES INDEPENDENTLY "
        "-- navigation, submission, composers, typing and third-party "
        "surfaces are out by construction.",
 'bound': "THIS ARGUES NO OUTWARD EFFECT, NOT NO EFFECT. An expansion "
          "could plausibly cause a client-side or remembered-filter "
          "write. That is a write in the weak sense and NO OTHER PERSON "
          "CAN OBSERVE IT, which is precisely what an outward counter "
          "measures. Anyone using this argument for a surface where that "
          "distinction does not hold is misusing it.",
 'refuters': [
   'the expanded region containing any control that addresses a person '
   '(message, invite, follow, endorse)',
   'the expansion issuing a request whose effect another account could '
   'observe',
   'LinkedIn surfacing a third-party-visible signal from this page, as a '
   'profile view is surfaced to its owner',
   'any counter later shown sensitive to a press here -- which would not '
   'refute the press but would move it from (b) to the stronger (a)']}
```

No exception raised on any of the four calls.

**Corroborating call, not one of the four requested but the gate's own
composite of them** -- `press.evaluate(url=url, shape='[aria-expanded]')`
with no counters supplied (the pre-press branch):

```
{'pressed': False, 'permitted_to_attempt': True, 'basis': 'structural',
 'requires_counters': [], 'still_to_show': ['counters_unmoved',
 'closure_verified']}
```

### Which of the four conditions are decidable offline, and which need the live page

**Condition 1 (page already admitted)** -- FULLY OFFLINE. `check_address`
is documented as PURE ("Separated from the press so the whole gate is
testable with no browser at all", `linkedin_server/press.py:368-371`) and
its only dependency, `readonly.is_read_url`, is a non-raising wrapper around
`assert_read_url` (`linkedin_server/readonly.py:2452-2458`), itself a pure
string/URL-path check. Nothing about it touches a page.

**Condition 2 (control matches an enumerated shape, by attribute) -- SPLIT,
and this is the nuance the brief asked to be precise about.** `check_shape`
(`linkedin_server/press.py:423-438`) is pure and offline, but it answers a
narrower question than "does this control exist on the page": it tests
only that the caller's STRING ARGUMENT is a member of
`SANCTIONED_SHAPES = ('[aria-expanded]', '[aria-haspopup]')` --
i.e. that the key is legal to ask for at all. It says nothing about
whether a node bearing that attribute is actually rendered on THIS page.
That second, page-shaped fact is checked separately, live, inside
`disclose()`:

```python
if not int(await page.locator(shape).count()):
    return _refuse("shape_absent_on_this_page", ...)
```

(`linkedin_server/press.py:874-882`). So condition 2 is genuinely two
facts: a fact about the caller's argument (offline, checked by
`check_shape`) and a fact about the rendered page (only checkable live, by
`disclose`). For this specific surface the live half is not unknown --
census row `N 134` records it was independently measured present-and-
unpressed on 2026-09-05, and the 2026-09-19 press run measured
`shape_total=9` before and after (see section 3) -- but that is a captured
reading from a past live session, not something today's offline run
established.

**Condition 3 (press shown not to move an outward counter) -- SPLIT.** The
URL-derivable half -- whether ANY basis is declared for this surface, and
if structural, whether it is complete -- is pure and offline
(`sensitivity_basis` / `check_basis`, `linkedin_server/press.py:303-316,
500-528`). For this URL it resolves to `basis_declared: True, basis:
'structural'`, with `requires_counters: []`. **That empty list does not
mean zero counters are needed** -- it means no SPECIFIC counter is named
as required, because the structural route accepts ANY counter that was
read at both ends and did not move. Reading `linkedin_server/press.py:531-
622` (`check_counters`) directly: even the structural route requires
`before` and `after` mappings with at least one shared key
(`no_counter_reading` / `no_counter_prices_this_press` otherwise), and
requires none of the shared keys to have moved (`counter_moved`, terminal)
before it will return `counters_ok: True, condition_3_route:
'structural_argument'`. Producing `before`/`after` requires an actual press
on a live page. So condition 3's declaration-and-completeness half is
offline; its satisfaction is not.

**Condition 4 (closed and closure verified) -- FULLY LIVE.** `check_closure`
(`linkedin_server/press.py:718-740`) is pure as a function of two
arguments, but those arguments (`expanded_before`, `expanded_after`) can
only be produced by actually pressing the control and reading its
attribute before the press and after the dismissal. Nothing offline can
manufacture them.

**Net:** the pre-press composite verdict above -- `permitted_to_attempt:
True, still_to_show: ['counters_unmoved', 'closure_verified']` -- is the
gate's own summary of exactly this split. Two things are already settled
offline (address admitted, shape key legal, a complete structural basis
declared); two things remain and both require a live page
(`counters_unmoved`, `closure_verified`). This is also, by the module's own
account, as far as this surface can ever get offline: nothing about
condition 3's live half or condition 4 is a mechanism gap that more
reading would close.

---

## 2. WHAT THE TWO ROWS ACTUALLY ASK FOR

Quoted verbatim from the census tables. Both are 5-column tables
(`# | capability | R/W | state | note` in `network.md`'s section L;
`# | capability | R/W | state | evidence / blocker` in `profile.md`'s
section O).

### `N 134` -- `_audit/_census/network.md` line 551, section "L. Who viewed your profile (12)"

- **# / capability:** `134` / `See notable or interesting viewers (Premium)`
- **R/W:** `R`
- **state:** `GAP`
- **note (full cell, verbatim):**

> Same. **THE PANEL EXISTS AND ITS CONTROL IS RENDERED UNPRESSED** --
> `Interesting viewers` counted twice on the unpressed page, 2026-09-05
> 17:18, and `Show more analytics` is drawn under exactly the name the
> blocker predicted. **So a reader needs no press to know the panel is
> there; whether its CONTENTS render unpressed is NOT established**, and
> that distinction is the whole row. Same ruling as `N 133` and no further
> measurement will settle it without one. Evidence
> `_audit/_scratch/_progress-analytics-creator.md` s11 (a self-correction:
> that wave's s1 had reported the page carries no such controls and s11
> measured that FALSE), capture
> `_audit/_scratch/_live-analytics-controls-4.txt`
>
> **RULED 2026-09-19, PERMITTED, AND STILL BLOCKED -- the distinction is
> the point.** `_audit/2026-09-19-the-disclosing-press-ruling.md`
> (`a0379d5`) grants the disclosing press this row was waiting on, under
> FOUR CONDITIONS THAT MUST ALL HOLD: (1) the page is ALREADY ADMITTED --
> a press never extends reach; (2) the control matches an ENUMERATED
> DISCLOSURE SHAPE **by ATTRIBUTE** (`[aria-expanded]`,
> `[aria-haspopup]`), never by label text; (3) the press is SHOWN not to
> move an outward counter, on the `read_invitation_badge` discipline, and
> **where no counter can price a press, unmeasurable resolves AGAINST the
> press**; (4) it is closed and the closure VERIFIED. Refused regardless:
> navigation, submission, composers, any third-party surface, and
> **typing -- a press is not a fill**. **SO THIS ROW IS NOW BLOCKED ON THE
> MECHANISM, NOT ON A RULING**, and that re-filing is deliberate:
> `messaging-measure` owns the boundary and is building the enumerated
> shape list, the refusal shown failing, and the counter check. **Nobody
> presses until it lands** -- a ruling is not permission to act ahead of
> the guard that bounds it, which is how a narrow ruling becomes a wide
> practice.
>
> **UPDATED 2026-09-19 ON THE SHIPPED GATE.** The press mechanism SHIPPED
> 2026-09-19 (`linkedin_server/press.py`, `tests/test_press.py`,
> `9c69ae9`), so this row is **no longer blocked on the mechanism** and
> the census should not keep saying so -- a deferral that will never
> resolve consumes a future wave, and these three do not all resolve the
> same way. Put through `press.evaluate` rather than inferred: **`/
> analytics/profile-views/` + `[aria-expanded]` passes address and
> shape**; the remaining conditions are `counters_unmoved` and
> `closure_verified`, neither of which can be evaluated without a run.
> **BLOCKED ON EXECUTION AND ON WHETHER A COUNTER EXISTS AT THIS
> ADDRESS** -- not on the mechanism and not on a ruling. The controls
> themselves were measured present and unpressed on 2026-09-05, so
> condition 2 has its evidence already
>
> **FIRST SANCTIONED PRESS TAKEN 2026-09-19 ~11:32, AND THIS ROW IS STILL
> GAP.** `press.disclose` PERMITTED the press on `/analytics/profile-
> views/` with shape `[aria-expanded]`: condition 1 admitted (checked
> before any load), condition 2 an enumerated shape KEY, condition 3
> **priced by TWO counters** (`invitations` 0, `notifications_unread` 6,
> neither moved across the press), condition 4 closure verified and the
> page identical on every measured field before and after. Verdict
> verbatim: `{"permitted": true, "pressed": true, "priced_by":
> ["invitations", "notifications_unread"], "shape": "[aria-expanded]"}`.
> **BUT A PERMITTED PRESS IS NOT A COVERED CAPABILITY.** `aria-expanded`
> read the same value at both ends and the page carried `expanded_true=0`
> before AND after, which fits two readings equally: the panel opened and
> Escape closed it, or **the press did nothing at all**. Nothing in the
> run distinguishes them -- condition 4 verifies the page was left as
> found, never that anything happened in between. **No content was read,
> so nothing is banked.** NEXT ARTIFACT, and it is a READER not another
> press: a DISCLOSURE WITNESS that fails if the panel did not open (a
> region that exists only while expanded, or `aria-expanded="true"`
> observed WHILE held open, before Escape), plus a name-free shaper for
> what the panel draws. **The witness is the harder half and worth
> building first: without it, a permitted press cannot be told from a
> press that missed.** Full evidence:
> `_audit/2026-09-19-the-first-sanctioned-press.md`

Note for the lead: this note cell predates the 2026-09-21 repairs (route
(b)/structural basis recorded in `press.SENSITIVITY_BASES`, and the
pre-press `check_basis` short-circuit) that section 1 above measured live
against the current tree. The row's own `state` is still `GAP` and nothing
here banks it; the cell's account of the 2026-09-19 press (permitted, safe,
undiagnostic) matches `_audit/2026-09-19-the-first-sanctioned-press.md`
exactly (section 3 below).

### `P O3` -- `_audit/_census/profile.md` line 535, section "O. Visibility and privacy (23)"

- **# / capability:** `O3` / `WVYP Premium insights and filters`
- **R/W:** `R`
- **state:** `GAP`
- **evidence / blocker (full cell, verbatim):** `no tool, no reason`

`O3`'s cell is the entire row -- no elaboration, no history, no blocker
name beyond the three words quoted. It is the thinnest row either wave
touches: it does not even carry a filed blocker name (contrast `N 134`'s
`ANALYTICS-CONTROLS-UNPRESSED`), which the lead's brief already
characterised correctly as a GAP row.

---

## 3. THE EXISTING PROBE

File: `scripts/_probe_first_sanctioned_press.py` (231 lines). Read only;
not executed.

**Exactly what it presses:** shape key `"[aria-expanded]"` (module
constant `SHAPE`, line 69), `index=0` (the call at line 189:
`press.disclose(page, shape=SHAPE, index=0, read_counters=reader)`), on
`TARGET_URL = f"{BASE_URL}/analytics/profile-views/"` (line 68). It
presses exactly one control, once, and does not retry (stated in its own
docstring, lines 42-45).

**What it reads:**
- Two counters, via a `read_counters` closure it builds
  (`make_counter_reader`, lines 85-110): `invitations` from
  `dom.read_invitation_badge(page)` (`linkedin_server/dom.py:7796`) and
  `notifications_unread` from `notify_cost.read_notifications_badge(page)`
  (`linkedin_server/notify_cost.py:98`). Both are coerced through a local
  `_as_int` that returns `None` rather than a false zero on anything
  unparseable (lines 72-82).
- Page state before and after (`_page_state`, lines 113-135): whether the
  page landed on the target address (`url_relation`: `"target"` or
  `"MOVED"` -- never the literal URL), `expanded_true` / `expanded_false`
  counts, `dialogs` count, and `shape_total` count.
- Whatever `press.disclose` itself reads and returns (conditions 1-4 plus,
  under the current `press.py`, the `witness` block -- see below).

**Whether it refuses to run outside attach mode:** yes. Line 139-141:
`if not config.CDP_ATTACH: print("REFUSED: LINKEDIN_CDP_ATTACH is not
set."); return 2` -- this is the first thing `main()` does, before any
import-time side effect beyond module load, and before any page contact.
`config.CDP_ATTACH` (`linkedin_server/config.py:183-190`) is `True` only
when the `LINKEDIN_CDP_ATTACH` env var is set to a truthy string. With it
unset, the script prints one line and exits 2 without touching a browser.

**Whether it opens its own tab and closes it in a `finally`, and never
the context:** yes, on both counts, and this is structural rather than a
choice the script makes itself. It opens a page via `async with
BROWSER.session() as opened: page = opened` (line 165-166).
`BrowserManager.session()` (`linkedin_server/browser.py:380-397`) yields a
page from `self._page()`; in ATTACH mode (the only mode this script can
reach, since it refuses otherwise) `_page()` (lines 399-428) explicitly
opens a NEW tab of its own (`self._own_page = await ctx.new_page()`) with
the comment "we always work in a tab of our own" (`browser.py:404-415`)
rather than reusing any tab the operator has open, and `session()`'s own
`finally` only touches an idle timer, never closing the page or the
context. The probe's own `finally` (lines 219-225) calls `await
page.close()` on exactly that one page and nothing else -- no `context`,
no `browser` object is even in scope in this file. So: its own tab, opened
by the framework specifically to avoid touching an operator tab, and
closed by the probe itself, never the context.

**What it prints, and whether any of it could carry a page string, a
name, an employer or a URL:** I read every `print` in the file. It prints:
booleans and dicts from `readonly.is_read_url` / `press.check_address` /
`press.check_shape` (fixed-vocabulary values, no page content); the
`SANCTIONED_SHAPES` tuple (a module constant); the page-state dict
described above, whose only string field is `url_relation` restricted to
the literal words `"target"` or `"MOVED"`; the two counters as ints-or-
`None`; the full `verdict` dict via `json.dumps(verdict, sort_keys=True)`;
and, on exception, only `type(exc).__name__` (three sites: lines 94, 106,
and inside `disclose()` itself per `press.py:902-912` -- never `str(exc)`
or the exception's args). The verdict dict itself, per section 1's reading
of `press.py`, is built entirely from fixed template strings
(`SENSITIVITY_BASES` prose), counts, booleans, and the fixed
`WITNESS_SELECTORS` names (`expanded_true`, `dialogs`, `menus`,
`menuitems`, `listboxes`) -- none of it is page TEXT. **I found nothing in
this file that could print a name, an employer, or a literal URL.** The
one thing worth flagging for the lead rather than silently passing: this
is a property of `press.py`'s current design (witness counts, never
witness text) and of this probe's own restraint (it never calls
`inner_text` / `text_content` on anything) -- it is not enforced by any
guard inside the probe itself, so a future edit to this file could
introduce a leak that nothing here would catch.

**Whether it can be run as-is, or needs a change:** as far as static
reading can establish, **it is runnable as-is against the current tree,
with a behavior change since it was last run that is worth naming.** Every
symbol it imports and calls still exists with a matching signature --
verified by grep, not assumed: `config.CDP_ATTACH`
(`linkedin_server/config.py:187`), `BROWSER.session` / `BROWSER.goto`
(`linkedin_server/browser.py:381,444`), `dom.read_invitation_badge`
(`linkedin_server/dom.py:7796`), `notify_cost.read_notifications_badge`
(`linkedin_server/notify_cost.py:98`), and `press.disclose(page, *,
shape, index=0, read_counters=None)` (`linkedin_server/press.py:833-839`)
all match the call sites in this file. The behavior change: when this
probe last ran (2026-09-19 ~11:32, before the `structural` basis was
recorded and before the witness mechanism existed), condition 3 passed on
the OLD "any counter read at both ends and unmoved" rule and the verdict
carried no `witness` key at all. Section 1 above confirms the surface now
has a declared, complete `structural` basis, and `disclose()` now attaches
`verdict["witness"]` unconditionally (`press.py:931-933`). So a run of
this unmodified file today would still reach a live click under the same
two counters this file already supplies (nothing in the structural route
requires a DIFFERENT counter -- section 1's `requires_counters: []`), and
the printed verdict would, for the first time, include a witness reading
that can distinguish "opened and closed" from "never opened" -- which
`_audit/2026-09-19-the-first-sanctioned-press.md` section 5/6 names as
exactly the missing piece. That is a reason the lead might WANT to run it
again, not a defect that blocks running it.

### What `_audit/2026-09-19-the-first-sanctioned-press.md` says the first press actually observed

Read in full (353 lines). The press was **taken**, on 2026-09-19 ~11:32,
and the file's own headline (section header) is: *"The first sanctioned
press -- PERMITTED, safe, and it discloses nothing yet."* Verdict
recorded verbatim (section 3): `{"permitted": true, "pressed": true,
"priced_by": ["invitations", "notifications_unread"], "shape":
"[aria-expanded]"}`. Page state was identical before and after on every
measured field (`expanded_true=0`, `expanded_false=9`, `dialogs=0`,
`shape_total=9`, both ends) and the CDP page count was unchanged (10
before, 10 after) -- no tab leaked.

**What was left unbuilt, in the document's own words:** the run could not
tell "the panel opened and Escape closed it" apart from "the press did
nothing at all," because the gate (as it stood then) took exactly two
readings of `aria-expanded`, both OUTSIDE the open state -- once before
the click, once after the dismissal -- so a clean Escape produces the same
two-reading equality whether or not anything ever opened ("Two readings
cannot describe three states," section 6). The document names this a limit
of the GATE, not of that one run, and hands over two concrete unbuilt
items (section 5): (1) a disclosure witness -- something that fails if the
panel did not open; (2) a name-free shaper for whatever the panel draws,
tied to the resolution `linkedin_who_viewed_me` already states for this
page. Section 1 above confirms item (1) has since shipped inside
`press.py` itself (`WITNESS_SELECTORS`, `_read_witness`,
`witness_verdict`). Item (2) -- the shaper for the notable-viewers panel's
CONTENTS -- is not present anywhere I read in `linkedin_server/`; nothing
in `dom.py` or `shape.py` names "notable" or "interesting" viewers.
Section 7-8 of the document also record that the ORIGINAL condition-3
reasoning for this press ("priced by two counters") was later ruled to
have overstated its evidence -- a merely-readable counter is not a
sensitive one -- and the structural argument now in `press.py`'s
`SENSITIVITY_BASES` (quoted in full in section 1 above) is the corrected,
weaker, explicitly-bounded basis that replaces it. None of this changes
the verdict of the press already taken, and none of it banks `N 133` /
`N 134`; the document says so explicitly in both section 4 and section 8.

---

## 4. WHAT `linkedin_who_viewed_me` PUBLISHES TODAY

Defined at `linkedin_server/server.py:1627-1781` (`@mcp.tool()` at 1627,
`async def linkedin_who_viewed_me(limit: int = DEFAULT_LIMIT)` at 1628).
Read only -- not modified.

**Published envelope keys.** Built by `shape.envelope(rows, limit=limit,
source_url=last_url, pages_loaded=attempt, dropped=dropped, extra=extra)`
at `server.py:1759-1766`. `shape.envelope` itself
(`linkedin_server/shape.py:4326-4358`) always returns: `count`,
`page_had`, `capped`, `limit`, `pages_loaded`, `source_url`, plus
`unparsed_rows` only when rows were dropped, plus everything in `extra`
merged in (`out.update(extra)`), plus `results` (the row list, trimmed to
`limit`). For this tool, `extra` is set at `server.py:1752-1758` to either
`{"insights": <dict>}` on success or `{"insights_error":
<exception-type-name>}` if the insights read raised -- so the top-level
envelope carries an `insights` key on the normal path. The `insights`
dict itself is exactly what `dom.read_profile_views_insights` returns
(`linkedin_server/dom.py:8834-8909`): `headline`, `delta` (both either
`None` or one of the parsed number/caption pairs), `trend` (`None`, or
`{"present": True, "description": <chart's own one-line sentence or
None>}`), `filters` (list of `<label>` strings), and `observed` (a
sub-dict of `metrics_seen`, `view_names`, `view_name_counts`,
`viewer_rows`, `main_present`, `main_chars`). Separately, each row inside
`results` carries a `recipient_id` field (member id string or `None`),
attached in place by `_attach_recipient_ids` (`server.py:1590-1624`)
*before* the envelope is built, joined by the row's own profile-URL slug
-- explicitly never by list position, because the id-reader and the
row-harvest are different-length lists.

**The resolution it says it holds itself to,** quoted from its own
docstring (`server.py:1628-1673`): on the viewer rows themselves, "Rows
carry name, headline, when the view happened, and a profile link,"
privacy-limited viewers appear "exactly as LinkedIn shows them to you and
no more... flagged `anonymous: true`," and "This server makes no attempt
to work out who they are, and there is no code here that could: nothing
is fetched about any viewer, and no viewer's profile is ever opened." On
`insights` specifically, the binding line for a future shaper: **"insights
reads NO name and NO text from any viewer row... the reader takes
numbers, filter labels, the chart's own sentence and COUNTS of page
regions, and nothing else."** And, on scope: "THERE IS NO TOP-COMPANIES OR
TOP-LOCATIONS BREAKDOWN HERE, and their absence is deliberate rather than
unbuilt... No key is returned for either, because a field that is always
null is a claim the page does not support."

**Which module does its DOM reading.** All live page contact is in
`linkedin_server/dom.py`: `dom.harvest_linked_cards`
(`dom.py:532-576`, using `HARVEST_LINKED_CARDS_JS` and
`CARD_HIDDEN_SELECTOR`) for the viewer-row cards, called with
`sibling_rows=True` specifically because anonymous viewers draw no link
(`server.py:1698-1706`); `dom.read_recipient_ids`
(`dom.py:6907`, via `RECIPIENT_IDS_JS`) for the id enrichment; and
`dom.read_profile_views_insights` (`dom.py:8834`, via
`PROFILE_VIEWS_INSIGHTS_JS`) for the surrounding aggregates. The
INTERPRETATION of a harvested card into a person row is a separate,
browser-free step in a different module -- `dom.parse_all`
(`dom.py:2552`) dispatches each raw record to `shape.parse_person_card`
(`linkedin_server/shape.py:327`), which is where the "which field is the
company, which is the location" decisions live, testable with no browser
at all. So: **page contact is `dom.py`; row shaping is `shape.py`.** A
disclosed-panel shaper for the notable-viewers content would most
naturally slot in as a new field returned by (an extended)
`dom.read_profile_views_insights`, sitting beside `headline` / `delta` /
`trend` / `filters` / `observed` inside the same `insights` key, under the
same numbers-labels-counts-only discipline the docstring already commits
this tool to.

---

## 5. THE HAZARD INVENTORY FOR A NAME-FREE SHAPER

**Hidden-text selectors: both exist, and neither is wired into the
analytics-insights reader.** `linkedin_server/dom.py:2499`:
`CARD_HIDDEN_SELECTOR = ".visually-hidden, .a11y-text, .sr-only,
.screen-reader-text"`; `dom.py:2503`: `NOTIFICATION_HIDDEN_SELECTOR =
".visually-hidden"`. `CARD_HIDDEN_SELECTOR` IS wired into the viewer-row
harvest this same tool already uses -- it is passed as `hiddenSelector`
into `HARVEST_LINKED_CARDS_JS` at both its call sites
(`dom.py:569,621`, i.e. inside `harvest_linked_cards` and its sibling
`harvest_census`) -- and into `company_root.py:347` and the notification
reader at `server.py:5457` (via `NOTIFICATION_HIDDEN_SELECTOR`). **It is
NOT referenced anywhere in `read_profile_views_insights`
(`dom.py:8834-8909`) or its script `PROFILE_VIEWS_INSIGHTS_JS`** -- I
grepped both hidden-selector names across the whole repository and every
hit is listed above; none falls inside that function or that script. This
is by design, not an oversight: that reader's own docstring states it
reads only "paragraph pairs where the first is a bare number, the
`<label>` text inside a filter control, the chart's own one-sentence
description, and COUNTS of `data-view-name` values... it never reads text
from inside a viewer row." A reader that never harvests generic element
text has no hidden-screen-reader-copy hazard to guard against in the
first place -- the discipline substitutes for the selector rather than
needing it. **Implication for a notable-viewers shaper:** if it is built
by extending `PROFILE_VIEWS_INSIGHTS_JS`'s existing narrow-field
discipline (numbers / `<label>` text / view-name counts), it does not need
`CARD_HIDDEN_SELECTOR`. If it is instead built by reusing
`harvest_linked_cards`-style generic card text extraction against the
expanded panel, `CARD_HIDDEN_SELECTOR` is the already-wired, already-
tested mechanism for it and should be reused rather than reinvented --
this is exactly the class of hazard it exists to catch (a visible copy of
a line sitting beside a screen-reader copy that names a person).

**The `# readonly-ok` waiver cap in `tests/test_readonly.py`: currently AT
the cap, zero headroom.** The assertion (`tests/test_readonly.py:798`):
`assert waived_in.get("dom.py", 0) <= 22, waived_in`. I counted the actual
waiver sites myself rather than trusting the comment: `grep -c
"# readonly-ok" linkedin_server/dom.py` returns 27 raw hits, but several
of those are PROSE mentioning the marker rather than a trailing waiver on
a call (e.g. `dom.py:28`, `:3583`, `:4055`, `:6082`, and `:6791`, the last
of which is a comment headed "NO ... HERE, DELIBERATELY" -- i.e. it
states in words that this site deliberately carries no waiver). Filtering
to lines whose stripped text actually ENDS with `# readonly-ok` (the same
test on the string that `tests/test_readonly.py:503` uses) gives exactly
**22** call sites: `dom.py:573, 634, 742, 779, 802, 3470, 4066, 4515,
5271, 5747, 6058, 6404, 6955, 7667, 8529, 8867, 9502, 9771, 9790, 10170,
10322, 10458`. That is exactly the cap, confirmed by a second, independent
assertion in the same file (`tests/test_readonly.py:1225`): `assert
len(EXECUTED_SCRIPTS) == 22, sorted(EXECUTED_SCRIPTS)`, which the file's
own comment (`:775-781,1217-1225`) states is "THE SAME 22 CALL SITES" as
the waiver count, measured, not derived. **So: 0 waiver sites are left
before the cap itself must be edited.** The file's own comment
(`:753-765`) is explicit about the way around this: "The cap is a ratchet
on WHERE evaluate may appear, not on how many scripts exist," and reusing
an ALREADY-DECLARED script spends no waiver at all -- it gives the
`N 175` group-reader as the worked precedent, which added a whole new
surface by calling an existing classifier rather than a new
`page.evaluate`. **Implication:** extending `PROFILE_VIEWS_INSIGHTS_JS`'s
own returned JS object (still one call site, `dom.py:8867`, already inside
the 22) costs zero new waivers; adding any brand-new `page.evaluate` call
anywhere in `dom.py` for this panel would require bumping the cap itself,
which this file's own comment treats as a deliberate, reviewed ratchet
move, not a routine edit.

**Declared in-page scripts in `dom.py`, by name** (21 distinct scripts,
matching both my own grep of top-level `..._JS = """` constants in
`dom.py` and the `INJECTED_SCRIPTS` dict `tests/test_readonly.py:805`
declares them under -- the 22nd call site is `HARVEST_LINKED_CARDS_JS`
used twice, at `dom.py:573` and `:634`):

```
HARVEST_LINKED_CARDS_JS   dom.py:111   (two call sites: 573, 634)
HARVEST_BLOCK_CARDS_JS    dom.py:363
READ_PROFILE_JS           dom.py:489
TRACKER_ROW_SHAPE_JS      dom.py:657
CENSUS_JS                 dom.py:3204
EDITOR_FIELDS_JS          dom.py:3752
EDITOR_VALUES_JS          dom.py:4254
ACTIVITY_ITEMS_JS         dom.py:4792
SDUI_ACTIONS_JS           dom.py:5618
COMPOSE_MODES_JS          dom.py:5859
SELECTED_RECIPIENT_JS     dom.py:6345
RECIPIENT_IDS_JS          dom.py:6859
INVITE_NEEDLE_JS          dom.py:7270
JOB_INSIGHT_MARKERS_JS    dom.py:8459
PROFILE_VIEWS_INSIGHTS_JS dom.py:8695  (the script this tool already runs)
SEARCH_APPEARANCES_JS     dom.py:9233
ANCHOR_CLASSIFY_JS        dom.py:9591
COLLECTION_GROUPINGS_JS   dom.py:9692
COUNT_LINES_JS            dom.py:9825
SEARCH_RESULTS_JS         dom.py:10191
FILTER_PANEL_JS           dom.py:10345
```

(Ordered by declaration line, straight from `grep -n` against `dom.py`,
to avoid a hand-copy error. 21 names, 22 call sites -- the extra call
site is `HARVEST_LINKED_CARDS_JS`'s second use at `dom.py:634`.)

Given the cap is exhausted, the one that matters most for this hazard
inventory is `PROFILE_VIEWS_INSIGHTS_JS` itself: it is already the single
call site this tool spends on the surrounding page, it already carries a
vocabulary-in / counts-out discipline that structurally avoids the
hidden-text hazard, and reusing it (rather than declaring a 22nd script)
is the only route that costs neither a new waiver nor a new
`CARD_HIDDEN_SELECTOR` wiring decision.

---

## VERDICT

**Offline vs live, condition by condition:** condition 1 is fully offline
and settled (admitted). Condition 2 is offline only for the shape-KEY
legality check (settled: `[aria-expanded]` is sanctioned); whether a node
of that shape is actually drawn on the live page is a page fact, not
established by today's run (though a past capture, 2026-09-19, measured
`shape_total=9`). Condition 3 is offline only for basis-declared-and-
complete (settled: `structural`, complete); its actual satisfaction always
requires a live press with at least one counter read at both ends and
unmoved. Condition 4 is fully live and cannot be produced offline at all.
**So the pre-press gate itself is already as far as it can go without a
browser** -- its own composite verdict says so:
`permitted_to_attempt: True, still_to_show: ['counters_unmoved',
'closure_verified']`.

**The existing probe, `scripts/_probe_first_sanctioned_press.py`, is
runnable as-is.** Every symbol it calls still exists with a matching
signature; it refuses cleanly (exit 2, no page touched) outside
`LINKEDIN_CDP_ATTACH=1`; it opens and closes only its own dedicated tab,
never the context; and nothing it prints carries page text, a name, an
employer, or a literal URL. Running it again would not be a repeat of
2026-09-19: the gate now attaches a `witness` block
(`press.py:931-933`) that the first run did not have, which is
precisely the missing half `_audit/2026-09-19-the-first-sanctioned-
press.md` named -- so a rerun could, for the first time, distinguish
"the panel opened" from "the press missed." What is still genuinely
unbuilt, confirmed by reading both `dom.py` and `shape.py`, is the
name-free CONTENT shaper for whatever the panel draws -- nothing there
names "notable" or "interesting" viewers. `N 134` / `O3` stay GAP either
way; no content has ever been read from that panel.

File written: `_audit/_census/_slice-analytics-press-preflight.md`
(this file).
