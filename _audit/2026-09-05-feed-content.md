# feed-content -- the comment identifier is READABLE, and the keystone unblocks

Wave `feed-content`, 2026-09-05. Six blockers, 18 rows, on the feed and comment
surfaces. Times below are box times taken with `date`, not estimated.

## THE HEADLINE

`COMMENT-IDENTIFIER` was filed **BLOCKED** on the premise that a comment has no
address this server can name. **That premise is refuted.** A comment carries its
own identifier as a DOM attribute on a page this server ALREADY OPENS -- the
item permalink behind the existing `feed_item_commented` census key. No new
address, no new capture, no press, no clipboard.

Four rows were waiting behind that premise. They are not waiting on an address.

## 1. WHAT WAS MEASURED, AND ON WHAT

One live run, `scripts/_probe_comment_identifier.py`, against Chrome pid 1252
in ATTACH mode. Two navigations, both to his own pages. Route A pressed
nothing; route B pressed one overflow control and sent Escape.

### The control ran FIRST, and it is the reason the reading counts

A reader that finds nothing prints the same empty output whether the thing is
absent or the reader is blind. This repository has shipped exactly that twice
-- a census aimed at a menu role that did not exist, and a tabbed surface that
read zero because nobody pressed the tab. So the identifier reader was pointed
first at a page where comment nodes are known absent.

| reading | elements on page | nodes carrying a comment identifier |
|---|---:|---:|
| CONTROL -- his own profile | 2620 | **0** |
| his own item permalink | 1089 | **12** |

The control page drew 2620 elements and matched zero, so the zero is about the
absence and not about a page that failed to load. The instrument has been shown
both reporting absence and reporting presence, on the same run, minutes apart.

### Route A -- the identifier is in the document

    nodes carrying an identifier ......... 12
    distinct identifier values ............ 8   (8 on id, 4 on componentkey)
    comment overflow controls on page ..... 4
    attributes carrying it ................ id, componentkey
    attributes outside the asked vocab .... 0
    longest digit run ..................... 19
    colon-delimited segments .............. 5
    parenthesised ......................... yes
    comma-separated pair inside ........... yes

Both figures reproduced exactly on a second run against a differently-rendered
copy of the same page -- see section 3.

The value is never held or printed. Its STRUCTURE is: the schema marker
`urn:li:comment`, then a parenthesised pair of two 19-digit runs separated by a
comma. That is what a WriteSpec would have to accept, stated without anybody's
identifier in it.

### Route B -- the overflow menu, pressed once

Pressed because a census that never presses reports a clean absence.
`dom.CENSUS_CONTROL_SELECTOR` carries **no menu role at all**, so a menu drawn
the ordinary way is invisible to a census delta; this read the menu roles
directly and read `aria-expanded` on the control it pressed, so "the menu did
not open" and "the menu opened and was not seen" stop being one answer.

    before press:  menus 2   items 0   expanded comment controls 0
    after press:   menus 3   items 7   expanded comment controls 1

    menu carries copy link : True
    menu carries     edit  : False
    menu carries   delete  : True
    menu carries   report  : True
    menu carries    share  : False
    items not in the asked vocabulary: 4

The menu demonstrably opened -- items went 0 -> 7 and the pressed control's
`aria-expanded` went to true. Both are required: an item count that grew with
no expanded control would be somebody else's menu.

**Route B corroborates route A without sharing its defect.** Route A reads
attributes and never presses; route B presses and never reads an attribute.
The repository's own law is that agreement between two instruments sharing a
defect is worth nothing, and disagreement between two that do not share one is
the cheapest signal available. These two do not share one, and they agree: a
comment has an address, and LinkedIn itself offers a copy-link affordance for
it.

**Route B is corroboration, not a route.** `Copy link to comment` targets the
CLIPBOARD -- a permission-gated surface this package has never touched -- and
costs one press per comment. It proves an address EXISTS. Only route A makes
one READABLE here.

## 2. THE RE-COST

| # | blocker | was | now | why |
|---|---|---|---|---|
| 47 | `COMMENT-IDENTIFIER` | BLOCKED, cost 6 | **BUILD, cost 4** | the address exists and is readable; a parser on a page already opened replaces the missing surface. WriteSpec still owed |
| 46 | `POST-COMMENT-CONTROLS` | MEASURE, cost 6 | **MEASURE, cost 6 -- UNCHANGED** | see the caveat below. Its 4 rows were assumed to wait on 47; that assumption is now testable and was NOT tested |

**I am deliberately not re-costing 46, 44, 69, 73 or 84 off this finding.** The
brief's hypothesis was that `POST-COMMENT-CONTROLS` likely waits on
`COMMENT-IDENTIFIER`. Unblocking 47 makes that hypothesis cheap to test; it
does not test it. A row moved on an inference is the same defect this document
just corrected on somebody else.

Rows 73 and 84 were measured separately and are unchanged -- see section 4.

## 3. THE 2x, WHICH WAS THE THING TO BE SUSPICIOUS OF -- AND IS NOW SETTLED

The first run read **8 distinct identifiers against 4 comment overflow
controls**: exactly 2x. This repository lost a round today to a selector that
read 54 rows where there were 18, because two instruments returned the same
MULTIPLE of the truth and looked corroborated. A clean 2x is the shape to stop
at, not the shape to build on.

So the reader was rewritten to split the count PER ATTRIBUTE and re-run:

| reading | run 1 | run 2 |
|---|---:|---:|
| elements on the page | 1089 | **838** |
| nodes carrying an identifier | 12 | 12 |
| distinct values, all attributes | 8 | 8 |
| distinct values on `id` | -- | **8** |
| distinct values on `componentkey` | -- | **4** |
| nodes carrying it on both attributes | -- | 4 |
| comment overflow controls | 4 | 4 |

**THE ANSWER: the 2x lives on `id` and not on the surface.** `componentkey`
carries exactly 4 distinct values against 4 comment overflow controls;
`id` carries 8, of which `componentkey`'s 4 are a subset. The 12 nodes
decompose as 4 carrying the identifier on both attributes plus 8 carrying it on
one.

**So a parser should key on `componentkey`, and that is now evidence rather than
preference.** It is the attribute whose cardinality tracks the rendered
comments; `id` is the one that would have produced a reader silently returning
twice as many comments as exist.

**The limit on that, stated because 4 == 4 is itself a correspondence and not a
proof:** two numbers agreeing is exactly what the 54-vs-18 defect looked like.
What raises confidence here is that they agree while being counted from
different things -- an attribute value set versus an accessible-name prefix
match -- and that the two are not derived from each other. It is still one
page. A second item with a different comment count would settle it properly and
was not run.

### THE SECOND ITEM WAS ATTEMPTED AND COULD NOT BE REACHED

A `LINKEDIN_PROBE_WALK_ALL=1` mode was added to walk every item on the rail
rather than stopping at the first with comments, precisely to turn 4 == 4 from
a correspondence into a relation. **It was run and it did not get there.** The
rail refused, twice, before any item was opened:

    REFUSED at the rail: no_overflow_controls

**The refusal is correct and is the best-behaved thing in this document.** It
names WHAT IT SAW rather than what it failed to match, and its own words are
"an empty rail is not an authorship claim, and this reader does not treat
'nobody disagreed' as agreement." A reader that had returned an empty item list
instead would have reported that he has posted nothing.

**The cause is a partial render, and the element count is what dates it:**

| run | profile page elements | rail |
|---|---:|---|
| 1 | 2620 | 8 items |
| 3 | 648 | REFUSED |
| 4 | 834 | REFUSED |

The profile page draws inconsistently on a Chrome a dozen waves are sharing,
and the rail depends on controls that had not rendered. **I did not retune the
probe's settle time to chase a successful read** -- adjusting an instrument
until it returns the answer you went looking for is how a probe set comes to
agree with its author, which this repository has now caught three times.

**So the 4 == 4 correspondence stands unpromoted.** The identifier finding does
not depend on it: that rests on two successful runs of the reader plus a
control, and section 3's per-attribute split is a decomposition of a single
page rather than a claim across pages.

**And the control is the part that got stronger.** It read zero identifiers at
2620, 834 and 648 elements -- three renders of the same page, one of them a
third the size of another. A control that only passes on a fully-drawn page is
not much of a control.

### And an unplanned stability result worth more than either number

**The page drew 1089 elements on the first run and 838 on the second -- a 23%
difference -- and every identifier figure was byte-identical across both.**
Nobody set out to measure that; the element count is in the output only as a
denominator, so that a zero from a blind reader could be told from a zero on a
page that failed to load.

That is the difference between a control and a repetition, and this repository
already has the law: a control proves the instrument CAN speak, and only
repetition proves what it said was stable. The identifier reading survived a
substantially different render of the same page. The element count did not, and
would have been the wrong thing to pin.

## 4. ROWS 73 AND 84 -- MEASURED, AND THE LEDGER IS RIGHT

Both are costed `allowlist +1`. That assumption has been wrong twice in this
repo this week, so it was measured against the SHIPPED predicate
(`linkedin_server.readonly.assert_read_url`, imported not reimplemented) rather
than reasoned about.

| candidate | verdict |
|---|---|
| `/my-items/saved-posts/` | REFUSED, absent from `_ALLOWED_URL_PATTERNS` |
| `/my-items/` | REFUSED, absent |
| `/feed/saved/` | REFUSED, absent |
| `/my-items/posts/` | REFUSED, absent |
| `/post/new/` | REFUSED, forbidden substring `/post/` |
| `/feed/drafts/` | REFUSED, absent |
| `/article/new/` | **ADMITTED**, matches an existing pattern |

**Row 73 `allowlist +1` is CORRECT. Row 84 `allowlist +1` is CORRECT.** The one
admitted address is the blank compose-an-article entry point, which is a
separately costed capability and not a surface listing existing drafts.

**The control is the part worth keeping.** The first control chosen -- his own
connections list, picked because `/invite` and `/connect` are forbidden
substrings -- came back ADMITTED. Rather than swapping it silently for one that
gave the expected answer, the run stopped and read the source: a deliberate
2026-09-03 exemption admits that page precisely because those two substrings
also catch it. A third control one word away on the same prefix
(`/mynetwork/invite-connect/invitations/`) came back cleanly REFUSED, which is
what shows the predicate discriminating right beside its own exemption. **A
control that returns the unexpected answer is a result about the world or about
the harness, and which one it is has to be read, not assumed.**

## 5. AN INSTRUMENT DEFECT IN MY OWN MASK, recorded because it nearly misled me

The first revision masked a value by replacing digit runs with `d<len>` and
then letter runs with `a<len>`. **The second pass eats the first pass's own
marker**: a 19-digit run becomes `d19`, and then the `d` is itself a
one-letter run and becomes `a1`, printing as `a119`. Read quickly, `a119` looks
like a 119-character run. It is a 19-digit one.

Nothing was concluded from the wrong reading, because the structural facts in
section 1 are counted in the page and not parsed out of the skeleton. But an
order-dependent mask that silently re-consumes its own output is the kind of
thing that reads as data. It is why the shipped revision returns integers
computed in the document instead of a skeleton string.

## 6. THE GUARD RED I RAISED, AND CLEARED

    file    tests/test_page_text_is_never_printed.py
    test    test_no_file_prints_page_text_beyond_its_pinned_inventory
    guard introduced at 881a11f

    first revision   scripts/_probe_comment_identifier.py  0 -> 14   RED
    then             scripts/_probe_comment_identifier.py  0 ->  2   RED
    shipped          (absent from the moved-inventory list)         GREEN

**It was never a leak, and the guard was still right.** Every value the probe
printed was an integer, a boolean, or one of its own module constants. But the
guard is a taint analysis over the AST: a count read out of a `page.evaluate`
result is tainted no matter what it counts, because the analysis cannot see
what was counted and should not guess.

**The remedy was NOT a pinned-inventory entry.** The guard's own failure text
forbids that, and every declaration permanently widens what it tolerates. The
remedy is the carve-out the sibling guard already ships --
`_COUNTING_CALLS = frozenset({"len"})` launders `len(x)`, because a length
cannot carry an identifier. So the page now returns ARRAYS OF PLACEHOLDER
ZEROES and the caller takes `len()`: the same number, with the property made
visible to the analysis rather than asserted in a comment.

**The second reading is the instructive one.** Converting the counts took it
from 14 to 2 and the last two were the BOOLEANS -- `bool()` is not a laundering
call and `len()` is, so `carries_paren_pair` had to come back as a
length-1-or-0 array like everything else. A partial application of a rule that
looks complete is this repository's most-repeated defect, and here it was
visible only because the guard was re-run rather than reasoned about.

**The remaining red in that pair is not mine.**
`tests/test_navigation_is_never_derived.py::test_every_relation_definition_is_byte_identical`
fails over `_relation` copies in six other waves' probe files
(`_probe_analytics_controls_live.py`, `_probe_compose_file_inputs.py`,
`_probe_groups_events_capture.py`, `_probe_groups_events_live.py`,
`_probe_newsletter_subscriptions_live.py`, `_probe_notify_cost_precondition.py`,
and more). This probe defines no `_relation` at all. It was red before this wave
touched the tree and is red at the same commit afterwards.

## 7. WHAT I DID NOT DO

* **Fired no write.** `comment_on_item` and `publish_post` were not called, not
  previewed against a real target, and no confirm token was requested. No
  target-specific consent exists for anyone and none was sought.
* **Wrote no WriteSpec.** Five of my six blockers carry one and none was
  written. The keystone had to be settled first, and it was settled with
  25 minutes left.
* **Did not re-cost 44, 46, 69** off the keystone finding. See section 2.
* **Did not press the feed item overflow menu (row 44).** Route B pressed a
  COMMENT's overflow menu. The POST's own overflow menu is a different control
  and remains unpressed; row 44 stays at MEASURE on an unopened menu, which is
  this repo's standing reason to refuse rather than to cost.
* **Did not open the poll, saved-posts or draft surfaces (69, 73, 84).** 73 and
  84 were measured at the boundary only, which is a fact about the address and
  not about the page.
* **Did not establish whose comment was pressed in route B.** The menu carried
  both `delete` and `report`, which is worth someone's attention -- it is
  consistent with a post owner holding a delete on comments he did not write --
  but one reading of one menu is a hypothesis, and I am recording it as one.

## 8. FOR WHOEVER TAKES THIS NEXT

1. **Run the probe on a SECOND item with a different comment count.** Section 3
   settles the 2x on one page; `componentkey == controls` at 4 == 4 is a
   correspondence, and one page cannot separate a relation from a coincidence.
   **The mode for this is built and committed** -- `LINKEDIN_PROBE_WALK_ALL=1`
   walks every item instead of stopping at the first, default deliberately
   unchanged so it costs nobody a page load who did not ask. It was attempted
   and the rail refused on a partial render; see section 3. Re-run it on a
   quieter browser, and do NOT lengthen the settle to force a read.
2. **Then re-cost 46.** With an address in hand, whether `POST-COMMENT-CONTROLS`
   was ever blocked by 47 is one live reading, not an inference. Do not move the
   row on this document alone.
3. **Key any parser on `componentkey`, not on `id`.** `id` carries twice the
   cardinality and would produce a reader that silently returns twice as many
   comments as exist -- which is the failure this repository has now shipped
   twice on other surfaces.
4. **Row 44 needs the POST's overflow menu pressed**, which this wave did not do.
   Route B pressed a COMMENT's menu; they are different controls and an unopened
   menu remains this repo's standing reason to refuse rather than to cost.

### Provenance

Every number above was recomputed at freeze time from the probe's own output,
not carried forward from the earlier draft of this document -- which is how the
element-count difference in section 3 was noticed at all. Both live runs were
made against Chrome pid 1252 in ATTACH mode; the page opened was closed in a
`finally` and `page.is_closed()` read True on both, because a page count cannot
prove a tab closed when a dozen waves share one browser.
