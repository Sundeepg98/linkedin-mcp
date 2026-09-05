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
    distinct identifier values ............ 8
    comment overflow controls on page ..... 4
    attributes carrying it ................ id, componentkey
    longest digit run ..................... 19
    parenthesised ......................... yes
    comma-separated pair inside ........... yes

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

## 3. THE ONE READING I DO NOT UNDERSTAND, STATED AS SUCH

**8 distinct identifiers against 4 comment overflow controls.** That is exactly
2x, and this repository lost a round today to a selector that read 54 rows where
there were 18 because two instruments returned the same MULTIPLE of the truth
and looked corroborated.

So the honest statement is: the identifier count is a factor of two above the
control count and I did not establish why. Candidate explanations -- each node
carrying the value on both `id` and `componentkey`; replies counted alongside
top-level comments; a virtualised list holding offscreen rows -- are three
hypotheses and zero measurements. **Do not build a parser that assumes one
identifier per visible comment until this is settled by a count taken a
different way.**

The 12/8 split is likewise unexplained: 12 nodes carry a value, 8 values are
distinct.

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

## 6. THE GUARD RED I AM LEAVING, NAMED PRECISELY

    file    tests/test_page_text_is_never_printed.py
    test    test_no_file_prints_page_text_beyond_its_pinned_inventory
    line    scripts/_probe_comment_identifier.py  0 -> 14

**This is not a leak and it is still owed.** Every value the probe prints is an
integer, a boolean, or one of its own module constants; no page-chosen string
reaches a print. But the guard is a taint analysis over the AST, and a count
read out of a `page.evaluate` result is tainted no matter what it counts. It is
right to be, and I am not arguing with it.

**The remedy is NOT to add the file to the pinned inventory.** The guard's own
failure text forbids that, and every declaration permanently widens what it
tolerates. The remedy is the carve-out the sibling guard already ships:
`_COUNTING_CALLS = frozenset({"len"})` launders `len(x)`. So the fix is to have
the page return ARRAYS and print `len(...)` of them, rather than returning
pre-counted integers. Roughly six print sites. **I ran out of clock before I
could make that change AND re-verify it live, and shipping an unverified edit to
the file that produced the reading is how two ends come to measure different
things.** The file is committed in the state that produced the numbers above.

Two other files were red on the same guard at the same reading and are not mine:
`scripts/_probe_contact_info_panel.py` (0 -> 1), and
`tests/test_navigation_is_never_derived.py::test_every_relation_definition_is_byte_identical`
plus `_probe_profile_modal_presence.py`, which were red before I touched the tree.

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

1. **Settle the 2x.** Count comment identifiers a second way -- per-node rather
   than per-attribute -- before any parser is written. Section 3.
2. **Then re-cost 46.** With an address in hand, whether `POST-COMMENT-CONTROLS`
   was ever blocked by 47 is one live reading, not an inference.
3. **The `len()` fix in section 6** is small, mechanical, and should be verified
   by re-running the probe, not by re-reading the diff.
