# Slice: AST census of Playwright strict-mode call sites

Instrument: `scripts/_census_strict_mode_call_sites.py`
Machine-readable output: `scripts/_census_strict_mode_call_sites.json`
Scope read: `linkedin_server/*.py` only (never `tests/`, never `scripts/`).

## HEADLINE TOTALS

Out of 85 candidate call sites (every call to one of the 37 STRICT_METHODS,
or to `wait_for_selector`, found by walking the AST of `linkedin_server/*.py`):

| verdict    | count |
|------------|------:|
| VULNERABLE |     6 |
| IMMUNE     |    74 |
| UNRESOLVED |     5 |
| **total**  |  **85** |

### IMMUNE, broken down by WHY

| reason                 | count |
|-------------------------|------:|
| `.first`                |    27 |
| `.last`                 |     0 |
| `.nth(...)`              |    19 |
| page-level-non-strict   |    28 |
| `.all()` element         |     0 |
| other                   |     0 |

`.last` and `.all()`/`element_handles()` are measured zero, not assumed zero:
`grep -n "\.last\b"` and `grep -n "\.all()\|element_handles("` over
`linkedin_server/*.py` both return no matches at all in this corpus. The
instrument still carries full logic for both (proven in the selftest fixture
below) -- they are absent from the census because they are absent from the
package today, not because the walk cannot see them.

## PER-MODULE TABLE

Only modules that contain at least one candidate site are listed (13 of the
package's modules; the other ~28 contain none).

| module                | vulnerable | immune | unresolved | total |
|------------------------|-----------:|-------:|-----------:|------:|
| dom.py                 |          6 |     51 |          0 |    57 |
| events.py               |          0 |      4 |          0 |     4 |
| writes.py               |          0 |      4 |          2 |     6 |
| press.py                |          0 |      4 |          1 |     5 |
| newsletters.py          |          0 |      3 |          0 |     3 |
| groups_page.py          |          0 |      2 |          0 |     2 |
| job_collections.py      |          0 |      2 |          0 |     2 |
| creator_analytics.py    |          0 |      1 |          0 |     1 |
| item_addresses.py       |          0 |      1 |          0 |     1 |
| notify_cost.py          |          0 |      1 |          0 |     1 |
| premium.py              |          0 |      1 |          0 |     1 |
| buildinfo.py            |          0 |      0 |          1 |     1 |
| cdp_bridge.py           |          0 |      0 |          1 |     1 |
| **total**               |      **6** | **74** |      **5** |**85** |

### Which STRICT_METHODS actually appear (context, not asked for but cheap)

`get_attribute` 31, `evaluate` 22, `inner_text` 11, `wait_for` 4, `clear` 3,
`click` 3, `is_visible` 2, `is_enabled` 2, `wait_for_selector` 1,
`is_disabled` 1, `text_content` 1, `press` 1, `set_input_files` 1,
`select_option` 1, `fill` 1. The other 22 STRICT_METHODS names never occur as
an attribute access on anything in this package.

## VULNERABLE SITES (6) -- module.py::function, and the source line only

```
dom.py::read_radio_label_binding  L1381  .get_attribute(
    input_id = await control.get_attribute("id")

dom.py::read_radio_label_binding  L1433  .get_attribute(
    bound_to = await labels.get_attribute("for")

dom.py::read_apply_modal  L2668  .get_attribute(
    ("submit_name", submit.get_attribute("aria-label")),

dom.py::read_apply_modal  L2669  .get_attribute(
    ("_disabled", submit.get_attribute("disabled")),

dom.py::read_apply_modal  L2670  .get_attribute(
    ("_aria_disabled", submit.get_attribute("aria-disabled")),

dom.py::read_apply_modal  L2677  .is_visible(
    visible = bool(await submit.is_visible())
```

### Observed context on these six (read by hand, not computed by the walk)

All six sit on a `Locator` bound by an unqualified `page.locator(SEL)` (no
`.first`/`.nth`) that is used, in the SAME function, ONLY after an explicit
`int(await X.count()) != 1: return ...` guard a few lines above:
`read_radio_label_binding` guards `control` at L1366/L1374 and `labels` at
L1392/L1400; `read_apply_modal` guards `submit` at L2653/L2658. So all six are
reached, in this reading of the code, only on a path where the same locator
was already confirmed to match exactly one element moments earlier.

This is a HUMAN OBSERVATION laid on top of the mechanical count above, not a
change to it -- the brief's classification rule is about `.first`/`.last`/
`.nth(...)` qualification, not about runtime count guards, and this walk does
no control-flow or data-flow analysis (deciding whether every path to a use
passed through a satisfied guard is a different, much larger kind of static
analysis than the AST-shape walk this slice was asked to build). Two things
the guard does NOT retire as a concern, stated so this is not read as a
clean bill of health: (1) a `Locator` re-queries the LIVE DOM on every
operation rather than reading a snapshot, so if the page mutates between the
`.count()` call and the later strict-method call, the guard's result can be
stale by the time it matters -- this is a general property of Playwright's
Locator API, not something driven or observed against this codebase's actual
runtime behaviour in this slice; (2) `read_apply_modal`'s three
`get_attribute` sites at L2668-2670 build coroutine objects in a tuple that is
only awaited later, in a loop at L2673, one line each -- the guard still
precedes all three, but the point is that the count-guard argument is a
by-hand reading of six sites, not a claim this instrument verifies.

## INTERPOLATED SELECTORS (73)

Every call to `.locator(`, `.get_by_text(`, `.filter(`, or `.wait_for_selector(`
whose selector/text argument (or `has_text=` keyword) is not a plain string
literal. `:has-text(...)` from the brief is Playwright's `has_text=` keyword
(available on `.locator()`/`.filter()`/`.get_by_text()`); see METHOD for why
this table checks that keyword explicitly. Shape counts:

| shape                     | count |
|----------------------------|------:|
| name (bare variable)       |    53 |
| other-non-literal:Call     |    11 |
| concat (`+`)               |     6 |
| f-string                   |     2 |
| other-non-literal:Subscript|     1 |
| **total**                  |**73** |

72 of the 73 are `.locator(...)`; 1 is `.wait_for_selector(...)`
(`dom.py::read_typeahead_options` L6798). None are `.get_by_text(` or
`.filter(has_text=` in the live corpus -- both are exercised only in the
selftest fixture.

**The "name" bucket is the majority and is the least interesting on its own**:
most are references to an ALL-CAPS module-level selector constant
(`SAVE_CONTROL`, `APPLY_CONTROL`, `ANCHOR`, ...), which is a harmless pattern
by itself. This walk does not trace a bare name back to its own definition to
decide whether IT was built from page content -- "you are not asked to decide
whether the interpolated value is page-derived, only to enumerate the sites"
-- so all 53 are listed and the lead judges which, if any, are worth a second
look. The `other-non-literal:Call` (11) and `concat` (6) rows are the more
interesting shapes: a selector assembled at the call site from a helper
function or string concatenation, which is exactly the shape that would carry
page-derived content into a selector string if any of its inputs did.

Full list (module::function, line, `.attr(arg_kind)`, `[shape]`, source line):

```
creator_analytics.py::collect_labels  L61  .locator(positional)  [name]
    locator = page.locator(LABEL_SELECTOR)
dom.py::read_job_identity  L887  .locator(positional)  [name]
    block = page.locator(COMPANY_BLOCK).first
dom.py::read_company_about_card  L1028  .locator(positional)  [name]
    container = page.locator(ABOUT_COMPANY_CONTAINER).first
dom.py::read_company_about_card  L1040  .locator(positional)  [name]
    out["sdui"] = bool(await page.locator(ABOUT_COMPANY_SDUI).count())
dom.py::read_radio_label_binding  L1365  .locator(positional)  [other-non-literal:Call]
    control = page.locator(named_role_selector(role, name))
dom.py::read_radio_label_binding  L1391  .locator(positional)  [other-non-literal:Call]
    labels = page.locator(settings_radio_label_selector(name))
dom.py::read_save_control  L1487  .locator(positional)  [name]
    controls = page.locator(SAVE_CONTROL)
dom.py::_sweep_save_shaped  L1607  .locator(positional)  [name]
    controls = page.locator(SAVE_SWEEP_SELECTOR)
dom.py::_sweep_save_shaped  L1618  .locator(positional)  [name]
    out["labelled_buttons"] = int(await page.locator(SAVE_LABELLED_BUTTONS).count())
dom.py::_sweep_save_shaped  L1622  .locator(positional)  [name]
    out["main_buttons_total"] = int(await page.locator(MAIN_BUTTONS).count())
dom.py::wait_for_save_control  L1784  .locator(positional)  [name]
    await page.locator(SAVE_CONTROL).first.wait_for(
dom.py::read_apply_control  L1877  .locator(positional)  [name]
    controls = page.locator(APPLY_CONTROL)
dom.py::read_follow_control  L1979  .locator(positional)  [name]
    controls = page.locator(FOLLOW_CONTROL)
dom.py::harvest_followed_pages  L2090  .locator(positional)  [name]
    buttons = page.locator(FOLLOWED_PAGE_BUTTON)
dom.py::harvest_followed_pages  L2106  .locator(positional)  [name]
    link = button.locator(_FOLLOWED_PAGE_ID_SCOPE).locator(
dom.py::harvest_followed_pages  L2106  .locator(positional)  [name]
    link = button.locator(_FOLLOWED_PAGE_ID_SCOPE).locator(
dom.py::read_unfollow_control  L2205  .locator(positional)  [name]
    controls = page.locator(selector)
dom.py::wait_for_job_description  L2336  .locator(positional)  [name]
    await page.locator(JOB_DESCRIPTION_SLOT).first.wait_for(
dom.py::read_apply_modal  L2647  .locator(positional)  [name]
    out["modal_present"] = int(await page.locator(APPLY_MODAL_SELECTOR).count()) > 0
dom.py::read_apply_modal  L2652  .locator(positional)  [name]
    submit = page.locator(APPLY_SUBMIT_SELECTOR)
dom.py::read_apply_modal  L2708  .locator(positional)  [f-string]
    buttons = page.locator(f"{APPLY_MODAL_SELECTOR} button")
dom.py::read_post_composer  L5545  .locator(positional)  [other-non-literal:Call]
    out["editors"] = int(await page.locator(post_editor_selector()).count())
dom.py::read_post_composer  L5546  .locator(positional)  [other-non-literal:Call]
    submits = page.locator(post_submit_selector())
dom.py::read_typeahead_pattern_census  L6672  .locator(positional)  [name]
    out[label] = int(await page.locator(selector).count())
dom.py::read_typeahead_options  L6798  .wait_for_selector(positional)  [name]
    await page.wait_for_selector(
dom.py::read_typeahead_options  L6812  .locator(positional)  [name]
    out["per_selector"][selector] = await page.locator(selector).count()
dom.py::read_typeahead_options  L6818  .locator(positional)  [other-non-literal:Subscript]
    out["matches"] = await page.locator(out["selector"]).count()
dom.py::read_compose_send_state  L7000  .locator(positional)  [other-non-literal:Call]
    control = page.locator(compose_send_selector())
dom.py::read_compose_send_state  L7003  .locator(positional)  [other-non-literal:Call]
    await page.locator(compose_body_selector()).count()
dom.py::read_comment_surface  L7127  .locator(positional)  [other-non-literal:Call]
    await page.locator(comment_editor_selector()).count()
dom.py::_count_links_with  L7347  .locator(positional)  [concat]
    return int(await page.locator('a[href*="' + fragment + '"]').count())
dom.py::read_thread_reply_surface  L7503  .locator(positional)  [concat]
    await page.locator(
dom.py::read_thread_reply_surface  L7507  .locator(positional)  [other-non-literal:Call]
    send = page.locator(compose_send_selector())
dom.py::read_reaction_surface  L7539  .locator(positional)  [name]
    controls = page.locator(REACTION_CONTROL)
dom.py::read_reaction_surface  L7546  .locator(positional)  [concat]
    await page.locator(
dom.py::read_reaction_surface  L7551  .locator(positional)  [concat]
    await page.locator(
dom.py::read_invitation_surface  L7656  .locator(positional)  [name]
    out["controls"] = int(await page.locator(INVITE_CONTROL).count())
dom.py::read_invitation_badge  L7839  .locator(positional)  [concat]
    await page.locator(
dom.py::read_invitation_badge  L7843  .locator(positional)  [other-non-literal:Call]
    badges = page.locator(invitation_badge_selector())
dom.py::wait_for_tracker_list  L7967  .locator(positional)  [other-non-literal:Call]
    await page.locator(tracker_list_selector()).first.wait_for(
dom.py::read_tracker_evidence  L8077  .locator(positional)  [name]
    out["rows_matching"] = int(await page.locator(TRACKER_ROW_LINK).count())
dom.py::read_tracker_evidence  L8091  .locator(positional)  [f-string]
    await page.locator(f"{TRACKER_ROW_LINK}:visible").count()
events.py::_announced_total  L252  .locator(positional)  [name]
    controls = footer.locator(EVENTS_HOME_FOOTER_CONTROL_SELECTOR)
events.py::read_events_home  L357  .locator(positional)  [name]
    cards = page.locator(EVENTS_HOME_CARD_SELECTOR)
events.py::read_events_home  L370  .locator(positional)  [name]
    headings = card.locator(EVENTS_HOME_HEADING_SELECTOR)
events.py::read_events_home  L381  .locator(positional)  [name]
    rows = await card.locator(EVENTS_HOME_ROW_SELECTOR).count()
events.py::read_events_home  L385  .locator(positional)  [name]
    links = await card.locator(EVENTS_HOME_LINK_SELECTOR).count()
events.py::read_events_home  L396  .locator(positional)  [name]
    bodies = card.locator(EVENTS_HOME_CARD_BODY_SELECTOR)
events.py::read_events_home  L407  .locator(positional)  [name]
    await body.locator(
events.py::read_events_home  L418  .locator(positional)  [name]
    footers = card.locator(EVENTS_HOME_CARD_FOOTER_SELECTOR)
events.py::read_events_home  L431  .locator(positional)  [name]
    await footer.locator(
groups_page.py::_stopping_ancestor  L162  .locator(positional)  [name]
    found = int(await node.locator(ANCHOR).count())
groups_page.py::read_group_memberships  L222  .locator(positional)  [name]
    anchors = page.locator(ANCHOR)
groups_page.py::read_group_memberships  L230  .locator(positional)  [name]
    controls = page.locator(CONTROL)
groups_page.py::read_group_memberships  L250  .locator(positional)  [name]
    str(await row.locator(ANCHOR).first.get_attribute("href") or "")
job_collections.py::read_job_collection  L321  .locator(positional)  [name]
    slots_in_main = int(await page.locator(SLOT_SELECTOR).count())
job_collections.py::read_job_collection  L322  .locator(positional)  [name]
    slots_anywhere = int(await page.locator(SLOT_SELECTOR_ANYWHERE).count())
job_collections.py::read_job_collection  L323  .locator(positional)  [name]
    cards_in_main = int(await page.locator(CARD_SELECTOR).count())
job_collections.py::read_job_collection  L324  .locator(positional)  [name]
    cards_anywhere = int(await page.locator(CARD_SELECTOR_ANYWHERE).count())
job_collections.py::read_job_collection  L325  .locator(positional)  [name]
    boxes_in_main = int(await page.locator(CONTAINER_SELECTOR).count())
job_collections.py::read_job_collection  L326  .locator(positional)  [name]
    boxes_anywhere = int(await page.locator(CONTAINER_SELECTOR_ANYWHERE).count())
job_collections.py::read_job_collection  L351  .locator(positional)  [name]
    slots = page.locator(SLOT_SELECTOR)
newsletters.py::read_newsletter_subscriptions  L295  .locator(positional)  [name]
    headings = page.locator(HEADING_SELECTOR)
newsletters.py::read_newsletter_subscriptions  L306  .locator(positional)  [name]
    in_main = int(await page.locator(CREATE_SELECTOR).count())
newsletters.py::read_newsletter_subscriptions  L307  .locator(positional)  [name]
    anywhere = int(await page.locator(CREATE_SELECTOR_ANYWHERE).count())
newsletters.py::read_newsletter_subscriptions  L311  .locator(positional)  [name]
    anchors = page.locator(ANCHOR_SELECTOR)
newsletters.py::read_newsletter_subscriptions  L317  .locator(positional)  [name]
    paragraphs = item.locator(PARAGRAPH_SELECTOR)
notify_cost.py::read_notifications_badge  L130  .locator(positional)  [concat]
    await page.locator(
notify_cost.py::read_notifications_badge  L134  .locator(positional)  [other-non-literal:Call]
    badges = page.locator(notifications_badge_selector())
premium.py::read_premium_surface  L168  .locator(positional)  [name]
    controls = page.locator(_CONTROL_SELECTOR)
press.py::disclose  L874  .locator(positional)  [name]
    locator = page.locator(shape).nth(index)
press.py::disclose  L876  .locator(positional)  [name]
    if not int(await page.locator(shape).count()):
press.py::_read_witness  L947  .locator(positional)  [name]
    out[name] = int(await page.locator(selector).count())
```

Rows whose printed source is only `await page.locator(` (or `wait_for_selector(`)
are calls whose argument spans multiple source lines -- the source field is
the line the Call node opens on, never more than that one line, per
instruction.

## METHOD -- exactly how this walk enumerates and resolves

**Candidate sites.** Every `ast.Call` in `linkedin_server/*.py` whose `.func`
is an `ast.Attribute` with `.attr` in the 37-name STRICT_METHODS set, or equal
to `wait_for_selector` (the one Page/Frame-only method sharing the same
`strict=` switch, absent from both named sets because `Locator` has no such
method at all -- see the module docstring). `NON_STRICT_METHODS` names
(`count`, `all`, `.first`, `.nth`, `locator`, `get_by_*`, ...) are never
candidate sites; they cannot raise the violation this census is about.

**Scoping.** Each `FunctionDef`/`AsyncFunctionDef` at ANY nesting depth is
its own independent scope, plus one `<module>` pseudo-scope for top-level
code (none occurred in this corpus -- every real site is inside a function).
A custom walk (`_iter_own_scope`), not a blanket `ast.walk`, stops at any
nested function/lambda/class boundary so a closure's own assignments are
never pulled into its enclosing function's binding map and vice versa. (This
package has exactly one nested `def`, in `server.py`, unrelated to locators;
20 `class` definitions exist, none in a locator-heavy module -- confirmed by
grep before writing the walk, not assumed.)

**Name resolution.** Within each scope, every plain-`Name` assignment target
is recorded with its line number -- from `Assign`/`AnnAssign`/`AugAssign`,
`for`/`async for` loop targets, and `with ... as NAME`. Deliberately, ALL
assignments are recorded, not only ones that look locator-shaped: this is
what makes shadowing resolve correctly. If `x` is bound to a locator chain on
line 10 and REBOUND to something unrelated on line 15, a use on line 20 must
see the line-15 binding, not the stale line-10 one -- pre-filtering the map to
"only qualifying assignments" would have let the stale binding leak through.
Classification of whichever binding is nearest-above a given use happens
STRUCTURALLY at resolution time (`classify_receiver`), not by pre-judging the
assignment's shape at collection time. A resolved name recurses into its own
bound expression (capped at 8 hops, matching the fixed-point convention this
repository's `_census_page_coercions.py` already uses for the same kind of
walk) so `a = page.locator(x); b = a; c = b.nth(2)` resolves `c` correctly
(proven by `case_multihop_alias` in the selftest below).

**Qualification.** A receiver is IMMUNE at the outermost syntactic node if it
is `X.first`, `X.last`, or `X.nth(...)` -- checked BEFORE any name resolution,
because `card.text_content()` is immune regardless of what `card` itself
turns out to be. A `for`/`async for` target bound from `<expr>.all()` or
`<expr>.element_handles()` is IMMUNE for the same structural reason (each
iteration yields one element). Everything else that resolves to an unqualified
`X.locator(...)`/`X.get_by_*(...)`/`X.filter(...)`/`X.or_(...)`/`X.and_(...)`
call is VULNERABLE -- INCLUDING when its own receiver was itself qualified:
`row.first.locator(b)` is VULNERABLE at the `.locator(b)` level, because
narrowing to one element and then searching within it can match 2+ again.

**A bare `page`/`frame` receiver, or any `wait_for_selector` call regardless
of receiver**, is routed to the Page/Frame-level rule instead: IMMUNE unless
a `strict=True` keyword (a literal `ast.Constant` `True`) is present on the
call, in which case VULNERABLE. Measured: `strict=` does not appear anywhere
in `linkedin_server/*.py` today (`grep -n "strict="` returns nothing), so this
branch is exercised only by the fixture below in the live census -- a
non-constant `strict=some_flag` would be scored page-level-non-strict here
(only a literal `True` is treated as the vulnerable case, per instruction);
none occurs, so this is a stated limitation, not a live gap.

**UNRESOLVED** means: a bare Name with no local binding and not one of
`page`/`frame`/`root`/`el`/`container`/`scope` (`no-binding`); one of
`root`/`el`/`container`/`scope` used bare with no local binding at all, i.e.
an opaque incoming parameter this walk cannot see the caller's side of
(`opaque-root-param`); an `X.locator(...)`-shaped call whose own receiver does
not resolve back to a recognised root (`unrecognised-root`); or any other
expression shape not covered above (`unrecognised-shape:<ast type>`).
UNRESOLVED sites are never folded into VULNERABLE or IMMUNE. All 5 live
UNRESOLVED sites were read by hand and are genuine PLAYWRIGHT-UNRELATED name
collisions, not walk failures: `_CACHE.clear()` / `_GRANTS.clear()` /
`_OBSERVED.clear()` (`dict`/set `.clear()` -- this exact collision is
independently documented in `readonly.py`'s own comments as a reason a text
scanner cannot be trusted here), `asyncio.wait_for(...)` (stdlib, not
`Locator.wait_for`), and `page.keyboard.press("Escape")` (Playwright's
`Keyboard.press`, a different class from `Locator.press`, receiver shape
`page.keyboard` -- an `Attribute` whose own attr is `keyboard`, not `first`/
`last`, so it falls through to `unrecognised-shape`, correctly).

**A real bug this method caught in its own first draft, and how it was
fixed.** The first version checked `expr.id in TRACKED_ROOTS` BEFORE checking
for a local binding, so a LOCAL variable that happens to share a name with one
of `page`/`frame`/`root`/`el`/`container`/`scope` was always treated as an
opaque, unbound parameter -- even when it had just been assigned on the line
above. This mis-scored a REAL site,
`dom.py::read_company_about_card` L1028/L1046 (`container =
page.locator(ABOUT_COMPANY_CONTAINER).first` then a bare
`container.inner_text(...)`), as UNRESOLVED when it is actually IMMUNE
(`.first`). Found by reading every UNRESOLVED site's real source against the
first live run, not by the selftest -- the fixture did not have a case for a
TRACKED_ROOTS name that is ALSO locally reassigned. Fixed by checking the
binding map first and falling back to "opaque root parameter" only when no
local binding exists; `case_tracked_root_name_locally_shadowed` was added to
the fixture as a permanent regression case, and the live UNRESOLVED count
dropped from 6 to 5 (IMMUNE rose from 73 to 74) after the fix. This is
disclosed here rather than silently folded into a clean-looking final run
because a check that has only ever been shown passing certifies less than one
that is shown catching its own defect.

**Interpolated-selector table (separate question).** Checks the first
positional argument, AND a `has_text=` keyword argument, of every call to
`.locator(`, `.get_by_text(`, `.filter(`, `.wait_for_selector(`. `:has-text(...)`
from the brief is Playwright's `has_text=` keyword parameter -- available on
`.locator()`, `.filter()`, and `.get_by_text()` -- so this table checks that
keyword explicitly rather than only positional arguments, which is how it
would actually appear in this codebase's calling convention. Detection is
BROADER than the brief's four named forms (f-string / `%`-format / `.format()`
/ `+` concat / bare variable): ANY non-`ast.Constant` argument is flagged and
sub-labelled by shape, because a bare call to a selector-building helper
(`named_role_selector(role, name)`, `compose_send_selector()`, ...) is exactly
the hazard shape and none of the four named forms would have caught it -- 11
of the 73 rows here are exactly that shape (`other-non-literal:Call`). This
table does not decide provenance, only enumerates; per instruction, the lead
judges which rows are page-derived.

**What this walk does not do**, stated so absence is not mistaken for a
clean result: no control-flow or data-flow analysis (a `count() != 1: return`
guard immediately above a VULNERABLE site is not detected -- see the six
sites' write-up above, added by hand); no cross-function tracking (a value
passed as an argument INTO a function is not traced back to its caller's
locator); no resolution of a bare bound name back to ITS OWN definition to
judge whether a `name`-shaped interpolation argument is itself page-derived.

## CONTROL -- the selftest, shown failing and shown passing

27 cases in an inline fixture manufactured inside the script (never found
elsewhere in the repo): 18 site-classification cases (one of which,
`case_non_strict_method_not_a_site`, asserts ZERO sites), 6 interpolation
cases, 2 no-interpolation cases (a fully literal selector and a fully literal
`has_text=` must produce nothing). Every required minimum case from the brief
is present (qualified `.first`, qualified `.nth(0)`, a bare vulnerable site, a
page-level non-strict site, a page-level `strict=True` site, an `.all()` loop
element, an unresolved receiver, an f-string selector) plus 19 more covering
`.last`, `element_handles()` loop elements, `wait_for_selector` both ways, an
opaque root parameter, reassignment shadowing, multi-hop aliasing, a locator
built after `.first` (still vulnerable), a `container`-rooted chain, all four
non-literal selector forms plus `.format()`, a `get_by_text` variable, both
`has_text=` forms, and the shadowing regression above.

### GREEN -- the committed script, all 27 passing

```
SELFTEST -- 18 site cases, 1 no-site cases, 6 interpolation cases, 2 no-interpolation cases

  [ok  ] case_all_loop_element                          expected=IMMUNE,all-element                 actual=IMMUNE,all-element
  [ok  ] case_bare_vulnerable                           expected=VULNERABLE,bare:.locator           actual=VULNERABLE,bare:.locator
  [ok  ] case_bare_vulnerable_inline                    expected=VULNERABLE,bare:.locator           actual=VULNERABLE,bare:.locator
  [ok  ] case_container_root_chain                      expected=IMMUNE,nth                         actual=IMMUNE,nth
  [ok  ] case_element_handles_loop                      expected=IMMUNE,all-element                 actual=IMMUNE,all-element
  [ok  ] case_multihop_alias                            expected=IMMUNE,nth                         actual=IMMUNE,nth
  [ok  ] case_nested_locator_after_first                expected=VULNERABLE,bare:.locator           actual=VULNERABLE,bare:.locator
  [ok  ] case_page_level_non_strict                     expected=IMMUNE,page-level-non-strict       actual=IMMUNE,page-level-non-strict
  [ok  ] case_page_level_strict_true                    expected=VULNERABLE,page-level-strict-true  actual=VULNERABLE,page-level-strict-true
  [ok  ] case_qualified_first                           expected=IMMUNE,first                       actual=IMMUNE,first
  [ok  ] case_qualified_last                            expected=IMMUNE,last                        actual=IMMUNE,last
  [ok  ] case_qualified_nth                             expected=IMMUNE,nth                         actual=IMMUNE,nth
  [ok  ] case_reassignment_shadow                       expected=UNRESOLVED,no-binding              actual=UNRESOLVED,no-binding
  [ok  ] case_tracked_root_name_locally_shadowed        expected=IMMUNE,first                       actual=IMMUNE,first
  [ok  ] case_unresolved_opaque_root                    expected=UNRESOLVED,opaque-root-param       actual=UNRESOLVED,opaque-root-param
  [ok  ] case_unresolved_receiver                       expected=UNRESOLVED,no-binding              actual=UNRESOLVED,no-binding
  [ok  ] case_wait_for_selector_non_strict              expected=IMMUNE,page-level-non-strict       actual=IMMUNE,page-level-non-strict
  [ok  ] case_wait_for_selector_strict                  expected=VULNERABLE,page-level-strict-true  actual=VULNERABLE,page-level-strict-true
  [ok  ] case_non_strict_method_not_a_site              expected=0 sites                            actual=0 site(s)
  [ok  ] case_concat_selector                           expected=[('locator', 'positional', 'concat')] actual=[('locator', 'positional', 'concat')]
  [ok  ] case_dot_format_selector                       expected=[('locator', 'positional', 'dot-format')] actual=[('locator', 'positional', 'dot-format')]
  [ok  ] case_fstring_selector                          expected=[('locator', 'positional', 'f-string')] actual=[('locator', 'positional', 'f-string')]
  [ok  ] case_get_by_text_variable                      expected=[('get_by_text', 'positional', 'name')] actual=[('get_by_text', 'positional', 'name')]
  [ok  ] case_has_text_kwarg_variable                   expected=[('filter', 'has_text=', 'name')]  actual=[('filter', 'has_text=', 'name')]
  [ok  ] case_percent_format_selector                   expected=[('locator', 'positional', 'percent-format')] actual=[('locator', 'positional', 'percent-format')]
  [ok  ] case_literal_selector_not_interpolated         expected=0 interpolation rows               actual=0 row(s)
  [ok  ] case_has_text_kwarg_literal                    expected=0 interpolation rows               actual=0 row(s)

SELFTEST: 27/27 passed, 0 failed.
```

Exit code: 0.

### RED -- `case_qualified_first`'s expected value deliberately inverted

One line changed: `EXPECTED_SITES["case_qualified_first"]` set to
`("VULNERABLE", "bare:.locator")` (a wrong expectation -- the fixture code
itself, `row.first` then `card.text_content()`, was NOT touched).

```
SELFTEST -- 18 site cases, 1 no-site cases, 6 interpolation cases, 2 no-interpolation cases

  [ok  ] case_all_loop_element                          expected=IMMUNE,all-element                 actual=IMMUNE,all-element
  [ok  ] case_bare_vulnerable                           expected=VULNERABLE,bare:.locator           actual=VULNERABLE,bare:.locator
  [ok  ] case_bare_vulnerable_inline                    expected=VULNERABLE,bare:.locator           actual=VULNERABLE,bare:.locator
  [ok  ] case_container_root_chain                      expected=IMMUNE,nth                         actual=IMMUNE,nth
  [ok  ] case_element_handles_loop                      expected=IMMUNE,all-element                 actual=IMMUNE,all-element
  [ok  ] case_multihop_alias                            expected=IMMUNE,nth                         actual=IMMUNE,nth
  [ok  ] case_nested_locator_after_first                expected=VULNERABLE,bare:.locator           actual=VULNERABLE,bare:.locator
  [ok  ] case_page_level_non_strict                     expected=IMMUNE,page-level-non-strict       actual=IMMUNE,page-level-non-strict
  [ok  ] case_page_level_strict_true                    expected=VULNERABLE,page-level-strict-true  actual=VULNERABLE,page-level-strict-true
  [FAIL] case_qualified_first                           expected=VULNERABLE,bare:.locator           actual=IMMUNE,first
  [ok  ] case_qualified_last                            expected=IMMUNE,last                        actual=IMMUNE,last
  [ok  ] case_qualified_nth                             expected=IMMUNE,nth                         actual=IMMUNE,nth
  [ok  ] case_reassignment_shadow                       expected=UNRESOLVED,no-binding              actual=UNRESOLVED,no-binding
  [ok  ] case_tracked_root_name_locally_shadowed        expected=IMMUNE,first                       actual=IMMUNE,first
  [ok  ] case_unresolved_opaque_root                    expected=UNRESOLVED,opaque-root-param       actual=UNRESOLVED,opaque-root-param
  [ok  ] case_unresolved_receiver                       expected=UNRESOLVED,no-binding              actual=UNRESOLVED,no-binding
  [ok  ] case_wait_for_selector_non_strict              expected=IMMUNE,page-level-non-strict       actual=IMMUNE,page-level-non-strict
  [ok  ] case_wait_for_selector_strict                  expected=VULNERABLE,page-level-strict-true  actual=VULNERABLE,page-level-strict-true
  [ok  ] case_non_strict_method_not_a_site              expected=0 sites                            actual=0 site(s)
  [ok  ] case_concat_selector                           expected=[('locator', 'positional', 'concat')] actual=[('locator', 'positional', 'concat')]
  [ok  ] case_dot_format_selector                       expected=[('locator', 'positional', 'dot-format')] actual=[('locator', 'positional', 'dot-format')]
  [ok  ] case_fstring_selector                          expected=[('locator', 'positional', 'f-string')] actual=[('locator', 'positional', 'f-string')]
  [ok  ] case_get_by_text_variable                      expected=[('get_by_text', 'positional', 'name')] actual=[('get_by_text', 'positional', 'name')]
  [ok  ] case_has_text_kwarg_variable                   expected=[('filter', 'has_text=', 'name')]  actual=[('filter', 'has_text=', 'name')]
  [ok  ] case_percent_format_selector                   expected=[('locator', 'positional', 'percent-format')] actual=[('locator', 'positional', 'percent-format')]
  [ok  ] case_literal_selector_not_interpolated         expected=0 interpolation rows               actual=0 row(s)
  [ok  ] case_has_text_kwarg_literal                    expected=0 interpolation rows               actual=0 row(s)

SELFTEST: 26/27 passed, 1 failed.
```

Exit code: 1.

### GREEN again -- restored, byte-identical to the first GREEN run

The one line was reverted (`EXPECTED_SITES["case_qualified_first"]` back to
`("IMMUNE", "first")`) and `--selftest` re-run: output was diffed byte-for-byte
against the first GREEN capture above and is IDENTICAL (`diff` exit 0), exit
code 0, 27/27 passed. This is the version committed.

## Artifacts

- Instrument: `scripts/_census_strict_mode_call_sites.py`
- JSON: `scripts/_census_strict_mode_call_sites.json` (85 sites, 73
  interpolation rows -- regenerated from the final, restored-green script)
- This report: `_audit/_slice-strict-call-sites.md`

Run it again with:

```
venv/Scripts/python.exe scripts/_census_strict_mode_call_sites.py
venv/Scripts/python.exe scripts/_census_strict_mode_call_sites.py --json scripts/_census_strict_mode_call_sites.json
venv/Scripts/python.exe scripts/_census_strict_mode_call_sites.py --selftest
```
