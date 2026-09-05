# Wiring the readers that were built and could not be called

**Wave `wire-readers`, 2026-09-05 evening. Commits `4f6d646`, `55ce03c`.**
All paths in this document are repo-relative; commands run from the repo root.

Five modules were named to this wave as readers built during the day that no
tool could reach. **Three were wired. Two were not, and the reason each was not
is a measurement rather than a shortage of time.** The tool count moved from
**38 to 41**, read off `mcp.list_tools()` before and after, not counted by hand.

---

## 1. What was wired

| tool | reader it makes reachable | loads |
|---|---|---|
| `linkedin_premium_status` | `premium.read_premium_surface` + `premium_entitlement` | `/premium/my-premium/`, 1 page |
| `linkedin_newsletter_subscriptions` | `newsletters.read_newsletter_subscriptions` | `/feed/` then the newsletters page, 2 pages |
| `linkedin_notify_cost_precondition` | `notify_cost.read_notifications_badge` + `notifications_badge` + `measurability` | `/feed/`, 1 page |

Every address is already on the read allowlist. **No allowlist pattern was
added and no boundary digest was re-frozen** -- the boundary-freeze chain has
one head and this wave never touched it.

### The property each module was built to hold, and how the tool keeps it

**`premium.py` -- three states named, one refuted.** The tool publishes **no
boolean and no single number**. `premium_entitlement` already carries `settles`
and `leaves_open` on all five branches, and the tool returns that verdict
whole: `**verdict` is spread into the payload rather than being reduced to a
field. A caller cannot read `entitled` without also reading the sentence saying
that whether a Premium panel renders on a JOB POSTING is a fact about a
different surface. `needles_fired` is published because it is a subset of the
two needle tuples **this package authors** -- naming them names nobody. No
plan, price, date or control label leaves the reader.

**`newsletters.py` -- the obligation the reader states and does not discharge.**
`read_newsletter_subscriptions`' docstring says the caller owns reading
`dom.read_invitation_badge` before and after, and refusing when it cannot be
read. That is done here, on the `linkedin_connections` pattern: badge BEFORE
off the feed's nav, badge AFTER off the newsletters page's nav (no third
navigation), and **three separate refusals** -- unreadable before, unreadable
after, and moved. A moved badge means the load consumed a pending invitation,
so the reading is withheld rather than published beside an unauthorised cost.
The docstring says `distinct` is the answer and `anchors` is not; both numbers
are returned and only one of them is the subscription count.

**`notify_cost.py` -- a precondition, and it spends nothing.** The module ships
no code that could open the notifications page, deliberately, because taking
the AFTER half consumes the operator's unread state. **The tool inherits that
and does not undo it.** It loads `/feed/`, reads the notifications badge off
the nav, and returns `measurability`. It never navigates to `/notifications/`,
and the payload says so in a field (`notifications_page_opened: false`).
`notify_cost.cost_delta` is **left with no caller on purpose** -- wiring it is
what would spend something, and that is the operator's call, not this wave's.

**A note on where the AFTER half belongs.** `notify_cost.py` proposes it be
taken in band inside `linkedin_notifications`. That was considered and NOT
done. `linkedin_notifications` opens a fresh session and navigates straight to
`/notifications/`, so a BEFORE reading there would be taken against a page that
has not loaded yet -- the badge would read unreadable on every call, and
`measurability` would return the same answer for every input, which is an
instrument reporting its own shape. Making it work needs an extra `/feed/` load
inside a shipped tool, changing that tool's behaviour and its pinned page-load
count. That is a ruling, not a wiring.

---

## 2. What was NOT wired, and why

### `groups.py` -- the tally needs a section split no anchor sweep can supply

`groups.py` contains **no page reader at all**. Its three public functions are
`group_identifier(href)`, `membership_tally(hrefs)` and `disjoint(first,
second)`, and the module docstring says plainly: *it does not open a page; it
takes hrefs somebody else read.*

Wiring it therefore means writing a reader, and the obvious cheap one is wrong.
A flat sweep of every anchor on `/groups/` and a hand-off to `membership_tally`
needs no knowledge of the page's structure, because the tally does all the
discrimination -- and **it would publish suggestions as memberships.** The live
reading this surface produced was *five under the membership heading, five
under the suggestion heading, zero identifiers in common*. A flat sweep returns
**ten**, to a precondition question whose answer is five, and it returns it in
the flattering direction.

That is the newsletter anchors-versus-distinct trap one surface over: ten
anchors, five newsletters, and a reader publishing the anchor count answers ten
while looking entirely correct. **`disjoint()` existing at all is the design
telling you it expects two lists.** A section-aware collector needs the live
capture that `groups-events` holds; no tracked fixture of a groups page exists
in this repository (`tests/fixtures/` has none).

**So the blocker is not a tool. It is a section-aware href collector.**

### And the collector already exists -- in a probe, behind a waiver this wave may not take

This section was first written as *"it belongs to whoever holds the capture"*
and that was the weaker answer. `scripts/_probe_membership_tally_live.py` is
`groups.py`'s existing caller and it **already splits the page structurally**,
on a rule validated by a sibling probe: for each group anchor, walk up to the
first ancestor holding exactly one group anchor; that ancestor is the ROW; a
row containing a control declaring `aria-expanded` is a MEMBERSHIP row, one
containing none is a SUGGESTION row. No heading and no label is read. Run
against the real page it returned **5 memberships / 5 suggestions / 0 in
common**, agreeing with two offline signals that share no input feature with
it.

So the obvious move is `premium.py`'s: package a proven probe's logic into the
reader the package ships. **Three measured reasons say not in this window, and
they are stronger than the scheduling one:**

1. **The walk is a `page.evaluate` call.** That is the one thing this package
   confines to `dom.py`, behind an explicit waiver. `premium.py` exists as a
   standalone module precisely BECAUSE its read is locator-only and needs no
   waiver, and it says so. A groups reader carrying this walk has to land in
   `dom.py` -- the most contended file in the tree, and the module the
   `linkedin_publish_post` feature detection keys on.
2. **The locator-only alternative is the wrong number**, per the paragraph
   above. Avoiding the waiver by sweeping anchors flat answers ten where the
   answer is five.
3. **A groups tool cannot certify its own cost from the page it loads.**
   Measured in `_audit/2026-09-05-groups-surface-measured.md`: the feed's nav
   draws a mynetwork link carrying a count, and the groups page's nav draws two
   that carry none -- the invitation badge reads UNREADABLE there. So the
   before/after discipline `linkedin_newsletter_subscriptions` discharges above
   would need a THIRD navigation back to the feed, and the badge sits at zero
   anyway, which is the degenerate reading `shape.invitation_badge` names.

**That third reason is a design question, not an implementation one**, and it
is the one a wiring wave should not answer by itself.

### `recommendations.py` -- no admitted address, and nothing has been run live

Two independent reasons, either sufficient:

1. **No recommendations address is on the read allowlist.** Measured: grepping
   `linkedin_server/readonly.py` for the word finds only `/groups/discover/`
   (described as recommendations) and prose. Wiring needs a boundary widening
   -- an allowlist pattern plus a digest re-freeze on a chain that has one head
   and is contended.
2. **The module says of itself that nothing in it has been run against a live
   capture.** Its branch structure is carried over from `groups.py`'s measured
   design, and it says so rather than claiming otherwise. Building a DOM aim
   for a page nobody in this repository has opened is the thing two waves
   already declined and were right to: an invented aim fails CLOSED and answers
   *he has no recommendations*, which is the exact reading the surface would be
   opened to produce.

Its stronger property was checked against what a tool would do to it: **no
public function returns any string derived from its input.** Nothing was wired,
so nothing was added that could return one -- no parameter, no field, no slug,
no digest. The digest question is settled inside the module and was not
reopened.

### Both are invisible to the guard that exists to catch exactly this

`tests/test_readers_outside_dom_are_a_pinned_inventory.py` selects functions
whose name begins with `read_`. `groups.py` and `recommendations.py` contain
none, so **neither was ever on the pinned inventory** -- correctly, by that
detector's rule, and misleadingly if the inventory is read as a list of
unreachable code. A module can be unreachable in precisely the way that file
exists to catch and be invisible to it, because the thing it lacks is a page
reader rather than a caller. That is now written into the file itself, where
somebody counting readers will find it.

---

## 3. The tool count, by measurement

    before   38    mcp.list_tools()
    after    41    mcp.list_tools()
    split    29 read + 12 write + 0 write-shaped-and-unable = 41

The write side is **byte-identical** across this change, which is the half that
matters when three tools arrive at once.

Sites that had to move, all four found by running wider than this wave's own
files:

| site | what moved |
|---|---|
| `tests/test_every_tool_is_on_the_surface.py` | `assert len(_tool_names()) == 41` |
| `tests/test_server_surface.py` | the pinned `EXPECTED_TOOLS` set, `== 41`, the read split `== 29`, and the test's own NAME |
| `linkedin_server/server.py` docstring | headline and three-way split, both regex-read by a test |
| `README.md` | the registry half of a hand-maintained sentence |

`tests/test_readers_outside_dom_are_a_pinned_inventory.py` lost all three of
its entries in the same commit as the wiring, which is the mechanism that file
was built with. **Its list is now empty** -- the end state its own docstring
said could not be committed that day. An empty inventory is not a disarmed
guard: the detector is still shown failing on a planted unwired reader, and the
next reader added with no consumer turns it red with an empty pin exactly as it
would have with three entries.

---

## 4. The count pin is a CONTROL, and it was shown still failing afterwards

Bumping a pinned number is the cheapest way in this repository to turn a test
green, so the bump is only honest if the guard can still be demonstrated to
fail. The demonstration is at `_audit/_scratch/_wire_readers_control_demo.py`
and its output was:

    live registry: 41 tools
    broken reading: ['_attach_recipient_ids', 'linkedin_my_profile']

    A. the two rules, over the registry measured while the defect was live
    PASS   rule 1 (a shipped read tool is missing) rejects the broken reading
    PASS   rule 2 (a private helper is on the surface) rejects the broken reading

    B. with the live registry REPLACED by that broken reading, the guard goes red
    PASS   test_every_read_tool_this_package_ships_is_registered goes RED
    PASS   test_no_private_helper_is_a_tool goes RED
    PASS   the CONTROL itself goes RED

    C. live registry INTACT, pinned number WRONG -- only the count may move
    PASS   the pin reads 41 in the file
    PASS   the control goes RED on a WRONG pin
    PASS   rule 1 stays GREEN under the wrong pin
    PASS   rule 2 stays GREEN under the wrong pin

    all demonstrations behaved as stated

**Part C is the one that matters and it is the claim written beside the bump.**
The guard's comment says the count is not what the control controls -- both
rules run over a two-entry reading compared BY CONTENT, so nothing in the
demonstration reads the number. C proves it rather than asserting it: with the
registry intact and only the pin wrong, the two rules stay green and the count
assertion alone moves.

The script is a one-off demonstration, not an instrument, and is filed as
disposable. What is durable is this section and the guard's own comment.

---

## 5. The feature-detection hazard, checked and reported loudly

`server.py` lifts `linkedin_publish_post`'s audience refusal by **feature
detection**:

    _COMPOSER_AUDIENCE_READER = "read_post_composer_audience"
    return callable(getattr(dom, _COMPOSER_AUDIENCE_READER, None))

**Defining a function of that name on `dom` re-arms an irreversible
broadcast.** Measured: grepping `linkedin_server/*.py` for `callable(getattr`
and `hasattr(` returns **exactly one hit**, that one. It keys on `dom` alone.

**This wave added nothing to `dom.py`.** Not one line. The four names it
introduced are `_badge_refusal`, `linkedin_premium_status`,
`linkedin_newsletter_subscriptions` and `linkedin_notify_cost_precondition`,
all in `server.py`, and none of them is the detected name or anything close to
it. The refusal is unchanged and `_composer_audience_is_readable()` still
returns false.

---

## 6. Two things the wider run found that this wave did not go looking for

**A write verb in a read tool's docstring.** The first draft of
`linkedin_newsletter_subscriptions`' headline named the act of subscribing, and
`test_no_docstring_claims_a_write` read that as a READ TOOL ADVERTISING A
WRITE. **The fix is the content, never an exemption** -- the exemption list
carries a control asserting each entry really does claim a write, so parking a
read there would turn a different test red. The headline is reworded and says
in the docstring why, so the next reader does not restore it. The detector was
run against candidate replacements before one was chosen, rather than guessed
at.

**A docstring that went stale under two bumps that moved its own assertion.**
`test_server_surface.py`'s surface test said *THIRTY-SIX NAMES OVER THIRTY-FIVE
CAPABILITIES* three lines above an assertion that had been updated to 37 and
then 38. Corrected to forty-one over forty, with the arithmetic stated -- names
minus capabilities is the login pair and nothing else -- so the claim stays
checkable when the count moves again.

**And one disagreement left visible rather than smoothed.** `README.md` says
the server registers N tools "and this table names 27 of them". N was
re-derived here. **The 27 was not, and it does not reconcile:** counting rows
in that file that begin with a tool name gives **30 rows over 28 distinct
names**, and no reading gives 27. Either the page holds more than one table of
tool rows or a name appears twice. The paragraph beside it already parks that
audit for somebody who reads the whole file, and adding a second wrong number
to a sentence that carries one would be worse than recording the disagreement.

---

## 7. What is still owed

* **A section-aware groups reader** -- see 2 above. The collection rule is
  already written and already validated live; what is owed is a ruling on
  whether it lands in `dom.py` behind the `page.evaluate` waiver, and a
  separate one on how a groups tool certifies a cost its own page cannot read.
  Neither is an implementation question.
* **A recommendations address, or a ruling that there will not be one.**
  Nothing about that module can move until a page is opened, and opening it is
  a boundary decision.
* **`notify_cost.cost_delta`** stays unwired until somebody rules on spending
  the unread state in band. `linkedin_notify_cost_precondition` is what says
  whether spending it would produce evidence at all.
* **Nothing here has been run against a live browser.** Every claim in this
  document is about code, tests and the registry. The three tools were
  registered and their guards run; none of the three pages was opened by this
  wave.
* **Nothing pushed.** The push freeze is the operator's and is untouched.
