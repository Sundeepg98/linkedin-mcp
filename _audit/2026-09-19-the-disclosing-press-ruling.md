# The disclosing press -- RULED, narrowly, and mechanically

**The question, as `small-measures` filed it:** *may this server press a control
on a page it already reads, when the press discloses content rather than
changing anything?*

Four rows are blocked on exactly this and nothing else: `N 133`, `N 134`
(`ANALYTICS-CONTROLS-UNPRESSED`, his own analytics) and `M C72`, `N 76`
(`OFF-PLATFORM-WIDGET`, feed overflow menus). It is also the standing question
filed under `MATCH-DETAILS-COLLAPSED`.

**It is the lead's to give.** Nothing in that list fires at a person, leaves his
account, or changes a value, and the standing line is that a ruling which is
reversible and non-outward-facing is the lead's while anything that fires at a
person is not.

## RULED: PERMITTED, under four conditions that must ALL hold

**A blanket yes would be wrong, and the reason is measured rather than
cautious.** "Discloses rather than changes" is a claim about a SPECIFIC
CONTROL, not a property of presses. This repo already holds the counterexample:
opening the article composer may **autosave a draft no surface can detect**
(`_audit/2026-09-19-*`, and `/article/new/` is admitted today). A press that
looks like a render can be a write.

So the ruling is conjunctive, and every condition is mechanically checkable
rather than a judgement call per control -- because a boundary enforced by
judgement is forgotten by the next caller, which is this project's own law.

### 1. The page must already be admitted

`readonly.is_read_url` must return True for the address **before** any press.
**A press NEVER extends reach.** If the address is refused, every control on it
is refused, and no press is a route to a surface the allowlist will not admit.
This closes the obvious laundering path: load an admitted page, press into a
refused one.

### 2. The control must match an ENUMERATED DISCLOSURE SHAPE, by attribute

Not by label text -- a label is page text and this server does not read page
text into decisions. The sanctioned shapes are:

    [aria-expanded]    a disclosure toggle
    [aria-haspopup]    a menu trigger

**Anything not on that list is REFUSED**, and the list grows only by a further
ruling, exactly as the URL allowlist does. A test must refuse everything off it
and must be SHOWN FAILING on an off-list shape before admission.

This is the same discipline as the address allowlist and for the same reason:
a family wildcard over "controls that look harmless" would admit the composer.

### 3. The press must be SHOWN not to move an outward counter

Before and after, on an invariant this repo already reads -- the
`read_invitation_badge` discipline used to prove a read did not move a counter.

**A press that moves one is a WRITE, whatever it looked like.** This is the
condition that catches the autosave class empirically rather than by
enumeration, and it is why condition 2 alone is not enough.

Where no counter can price a given press, the press is **NOT PERMITTED** --
"unmeasurable" resolves against the press, not for it.

### 4. It must be closed, and the closure verified

Escape, or the toggle restored, and the page confirmed as found. A disclosure
that is left open is a change to the rendered state the next reader inherits.

## REFUSED regardless of the four conditions

* **Anything that navigates, submits, or opens a composer or editor.** The
  autosave class. A composer is not a disclosure even when it renders like one.
* **Anything on a third party's surface that could plausibly register an
  interaction visible to them.** A profile view is the clear case: it discloses
  content to this server AND discloses this server to the person. That is
  outward-facing and therefore not the lead's to grant.
* **TYPING. A press is not a fill.** `page.fill()` remains refused. This ruling
  sanctions opening and expanding, nothing that enters characters.

## What this ruling does NOT do

It does not sanction the presses already present in `scripts/`. Those were
measured today -- **21 probe files, 45 mutating hits, ten real `.click()` on a
live page, seven `keyboard.press("Escape")`, and one `page.fill()` that types a
name into a message composer** -- and none of it was ever scanned, because
`tests/test_readonly.py` walks `PACKAGE_DIR.glob("*.py")` only.

**This ruling governs the PACKAGE. The probes get their own rule**, which
`messaging-measure` is building, and the `fill()` is refused by this ruling's
own terms whatever that rule says.

## Why permit it at all, stated so it can be argued with

Three reasons, in order of weight.

1. **The information is already his.** His analytics, his feed's menus. The
   boundary exists to stop this server acting on the world and disclosing other
   people, not to stop him reading his own account.
2. **Correct paging does not reach it.** Unlike the scroll question -- where the
   objection was sufficiency, because paging already reached what scrolling
   would buy -- a collapsed panel is not reachable by any other means. There is
   no cheaper route.
3. **The practice already exists, ungoverned.** At least seven probes open a
   menu by clicking and close it with Escape. Ruling it makes the actual
   behaviour legible and testable instead of tacit. An unruled practice is worse
   than a ruled one at the same risk.

## What would reopen this

* A measured instance of a sanctioned SHAPE producing an outward effect --
  which condition 3 exists to catch and which would prove condition 2's list
  too wide.
* LinkedIn attaching telemetry to disclosure presses that it does not attach to
  page loads. Nobody has measured that, and this ruling does not assume it
  absent; condition 3 is the check that would surface it.

## Who does what

* **`messaging-measure`** owns the boundary this round and builds the mechanism:
  the enumerated shape list, the refusal test shown failing, and the before/after
  counter check.
* **`small-measures`** consumes it for `N 133`, `N 134`, `M C72`, `N 76`.
* **Nobody presses anything until the mechanism exists.** A ruling is not a
  permission to act ahead of the guard that bounds it -- that inversion is how
  a narrow ruling becomes a wide practice.
