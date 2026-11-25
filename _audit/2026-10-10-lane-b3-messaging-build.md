# Lane B3, 2026-10-10: messaging and content -- one item's words read, two session-1 pages read, and the rest held by what was measured

Lane `lb3-messaging-build`, briefed by the orchestrator at 15:18 IST. Built
OFFLINE in its own worktree; nothing here loaded LinkedIn. Base: master
`f93104c` (origin/master at 15:16, re-fetched before each `ci/` push). One
child (general-purpose, its own worktree) built the two session-1 pages' readers,
`M C48` and `M C38`, as a closed slice; it is reviewed and merged here (section 3).

THE BRIEF'S SIXTEEN ROWS, each `next=BUILD` in lane K's ledger:

    row     capture the ledger named                  verdict here
    M C43   live2/own_post.html                       COVERED-UNFIRED (section 2)
    M C48   live1/articles.html (built here)          COVERED-UNFIRED (section 3)
    M C38   live1/post_summary.html (built here)      COVERED-UNFIRED (section 3)
    M M20   live8/thread.html                         GAP: no opened conversation captured (4.1)
    M M40   live8/thread.html                         GAP: the same (4.1)
    M M51   live8/thread.html                         GAP: the same (4.1)
    M M26   live3/compose_c9-open.html                GAP: the menu cannot be bound to a named thread (4.2)
    M M27   live3/compose_c9-open.html                GAP: the same, and the inverse's folder unmeasured (4.2)
    M M29   live3/compose_c9-open.html                GAP: the same binding (4.2)
    M M31   live3/compose_c9-open.html                GAP: the same binding (4.2)
    M M16   live3/compose_c5-open.html                GAP: what a tile press does is unmeasured (4.3)
    M C18   synthetic/own_post_menu.html              GAP: the editor the item opens is uncaptured (4.4)
    M C23   synthetic/own_post_menu.html              GAP: the dialog the item opens is uncaptured (4.4)
    M C90   synthetic/own_post_menu.html              GAP: not one of the menu's nine items (4.4)
    M C29   live2/own_post.html                       GAP: a sort is not the shipped switch's shape (4.5)
    M C97   notifications.html                        GAP: no card can be named by its caller (4.6)

---

## 1. Two things disk said that the brief did not

1. THE 2026-10-10 LEDGER RULINGS WERE NOT ON MASTER WHEN THE LANE STARTED.
   The standing rules say every registered ruling, "the 2026-10-10 ledger
   rulings" included, is in `_audit/RULINGS.md` on master. At 15:16 and again
   at 15:20 origin/master was `f93104c`, and its register held no
   `THIRD-PARTY-TEXT-AT-RUNTIME`; the ruling was registered on lane K's branch
   (`865e57f`) and its text was in
   `_state/rulings/2026-10-10-rulings-ledger-questions.md`. By 16:30 master
   had moved 35 commits (lane K's application of the rulings, lane U's
   attachments, the CI lane's last items) and its register holds the ruling;
   this lane merged that master (`0103810`), so the id `M C43` cites resolves
   on this branch.
2. THE SESSION-8 "THREAD" IS THE NEW-MESSAGE COMPOSER. Lane U measured it
   (its builder's docstring: "the NEW-MESSAGE composer in its detail pane --
   the heading 'New message', one recipient typeahead, no message list"), and
   the coordinator's correction of 15:31 says the same. Measured again here,
   section 4.1.

---

## 2. `M C43`: an item's own words, read off its permalink

### 2.1 What was built

`linkedin_read_item_text(item)` (`linkedin_server/server.py`, the lane B3
block) and its reader `linkedin_server/item_text.py`, under ruling
`THIRD-PARTY-TEXT-AT-RUNTIME` (orchestrator, 2026-10-10, applying the
operator's `NAMES-AT-RUNTIME`): "a post's own text (M C43) ... returned at
runtime under PEOPLE-DATA-MITIGATIONS" -- untrusted, sanitised, bounded, never
stored; `FEED-CONTENT-READ-RULING`'s counts-only rule "still governs what is
STORED".

- THE ADDRESS IS THE CALLER'S. `item` must be one item key,
  `urn:li:<letters>:<digits>` (both runs bounded), as
  `linkedin_my_activity_items` and a named profile's `activity_items` return
  it. `item_text.permalink` composes `https://www.linkedin.com/feed/update/<key>/`
  from it alone (the read allowlist's existing permalink pattern); a key of any
  other shape is refused with a message that never repeats it. A landing on
  any other path reads nothing (`landed_on_the_item`).
- THE WORDS LEAVE ONLY INSIDE ONE `people_data.Post` RECORD -- the record lane
  G2 declared today and no reader had adopted. Its `author` is the person
  record `item_author.read_item_author` already builds from the item's own
  header (imported, not retyped); its `link` is the permalink this server
  loaded; its `text` is `inner_text` of the item's words container,
  sanitised and cut at `CAPS["text"]` (3,000, LinkedIn's own limit), with the
  untrusted-text marker. `truncated` says when the cap cut; `expanded` is
  False when a control is drawn inside the description.
- NEVER STORED: no log line carries a page string (a failed read is logged by
  its exception type), nothing is cached or written; the tool joins
  `people_data.PEOPLE_TOOLS`. `feed.py` is unchanged and still returns no
  substring of its input.

### 2.2 Evidence classes

MEASURED, offline through a real engine on `tests/fixtures/live2/own_post.html`
(his own item's permalink, live session 2, the only tracked permalink
capture), inside `main`: one `.feed-shared-update-v2`; one
`.feed-shared-update-v2__description`; one
`.update-components-update-v2__commentary` in it AND in the whole of `main`
(the seven comments carry their words in `.comments-comment-item__main-content`;
`.update-components-text` alone counts 8, so the description scope is what
keeps a comment out); the description wears
`feed-shared-inline-show-more-text--expanded` and holds 0 buttons; one member
actor link.

DERIVED, and said in the module: that another member's permalink draws the
same blocks (no capture shows one -- `item_author` records the same gap); that
a long item renders expanded on its permalink. An organisation Page's item has
no record type (`people_data.Post.from_page` returns `None` without a member
author), so its words are NOT returned and `why` says so.

### 2.3 Red, then green

RED, with the module absent (15:40):

    tests\test_item_text.py:33: in <module>
        from linkedin_server import item_text, people_data
    E   ImportError: cannot import name 'item_text' from 'linkedin_server'
    1 error in 0.80s

A SECOND RED, the harness's own: the first green attempt failed 13 of 33
because the capture keeps its image and tracker addresses' shapes and the
network guard refused 14 requests per load. The house pattern (route every
request to abort before `set_content`, as the reaction test over the same
capture does) fixed it; and one assertion leaned on how the engine collapses
whitespace beside a zero-width space, rewritten to hold the sanitising
property itself.

GREEN: `tests/test_item_text.py` 33 passed (143 s on this box). Plants, each
written into the real capture by the test's own page script: the item's words
(returned, sanitised, a RLO and a ZWSP gone); 3,500 characters (cut to 3,000,
`truncated`); a comment's words (never in the output); a second item
description, a second words container inside it, one outside it, an
organisation actor, no description (each: no record, no words anywhere in the
output, the closed `why`); a control in the description (`expanded` False);
nothing at DEBUG in any log record. CONTROLS, each shown failing: with both
uniqueness checks weakened to "the first match", a second item's words come
through; with only the main-wide count weakened, a container outside the
description gets past (`test_control_each_check_weakened_lets_its_plant_through`).

### 2.4 The census

`M C43` GAP -> COVERED-UNFIRED, its cell's bar being a tool aimed at real
captured markup that has never returned a live payload. The binding
`tests/test_c43_rests_on_the_feed_content_ruling.py` required GAP; it now
requires COVERED-UNFIRED, the cell naming `THIRD-PARTY-TEXT-AT-RUNTIME` (the
ruling that moved it) AND `FEED-CONTENT-READ-RULING` (which still governs
storage), and it still holds `feed.py`'s IN and OUT halves. The row left
bucket 3, so its line left `_audit/_census/read-addresses.tsv` and lane K's
`_audit/_census/next-step.tsv`, and it entered bucket 1 under NO RULING
(`PINNED_B1_ROWS`).

---

## 3. `M C48` and `M C38`: the two session-1 pages (child)

Built by the lane's child (general-purpose, its own worktree, branch
`worktree-agent-aae4845b01117efe1`, five commits `2d021f3`..`3203e27`),
reviewed and merged here; its report is the source of the reds below.

### 3.1 The tracked skeletons

`scripts/_build_live1_l1_fixtures.py` builds `tests/fixtures/live1/articles.html`
and `tests/fixtures/live1/post_summary.html` from the live lane's raw session-1
captures (`_state/l1-articles.html`, `_state/l1-post_summary.html`; gitignored,
read, never copied) through the SHIPPED reduction, imported and not rewritten
(`_probe_live_lane_session_2.skeleton_of`, then `tracked_copy`), with a fresh
random key per run. One substitution between the two: a closed tuple of
LinkedIn's fixed words kept where a whole text node or label equals one --
"All activity", "Top demographics", "All", and the six category words. Every
demographic VALUE and percentage stays x. The builder prints counts only and
refuses if a keyed shape survives; `tests/test_no_committed_identity.py` and
`tests/test_fixtures_hold_only_synthetic_people.py` pass over both.

### 3.2 `M C48`: what the page draws, and the reader

MEASURED on the skeleton (counts and LinkedIn's words only): the address is
SERVED as the "All activity" shell -- one section, its heading "All
activity", one filter pill "Posts", and one SDUI screen slot holding one
CHILDLESS container; 22 anchors on the page, 0 `/pulse/`, no list, no
empty-state words. `linkedin_server/own_articles.py` keys on the heading (a
fixed word) and the slot (an attribute name), never a position; it returns
`readable`, `articles` (`/pulse/<one segment>/` paths, titles sanitised and
capped), `count`, `empty` and `truncated`. On the real skeleton: readable,
no article, empty. DERIVED: the entry shape (no capture draws an article),
and the reading of an empty slot as drawn rather than still streaming (the
same session's analytics slot drew 653 elements, so the page had settled).

RED (child): `ImportError: cannot import name 'own_articles'`; a harness red
on the network guard (the same as section 2.3's), fixed with the route
refusal. GREEN: 6 passed.

THE LEAD'S FIX AT THE MERGE, red first: `empty` was computed from a count
helper that turns a FAILED count into 0, so a page whose section and slot
were found but whose content count failed read `empty: True` -- the module's
own docstring says "an unreadable page is never empty". The new test makes
the content count raise (a selector the engine refuses) and failed on the
child's code (`assert True is False`); `empty` now reads a count that is
`None` when it fails. 7 passed.

### 3.3 `M C38`: the demographics card is drawn

MEASURED: the per-post page DRAWS a viewer-demographics card -- title "Top
demographics", a nav of seven buttons ("All" with `aria-current`, then Job
title, Location, Seniority, Company, Industry, Company size), five rows each
with a category word, a value, a percentage and a `role=progressbar` whose
`aria-valuenow` equals the percentage; no anchor and no member link inside
the card. Session 1's "38 chart labels, none in the metric vocabulary" was
the creator-analytics `aria-label` route, which cannot see text and
`aria-valuenow`; it was never an absence. The page's other people card (a
Premium list of members) sits outside the card and nothing selects it.

`linkedin_server/post_viewer_demographics.py` finds the card from its one
title, reads tabs and rows by structure, takes category words only from the
closed vocabulary, cross-checks each percentage against its progressbar, and
lets each VALUE leave only through `shape.census_shape` then
`shape.census_redact_rare` at count one -- the cell's own requirement. Its
residual, stated in the module: a one-word value survives that redactor, as
the redactor documents of itself; it names a bucket, never a viewer. On the
real skeleton: card found, categories read, 5 rows drawn, 0 points (the
values are x). On a copy with synthetic rows planted: 5 points, multi-word
values `<redacted>`, the reader-leak guard's own plant nowhere in the reading,
a row whose progressbar disagrees with its text refused.

RED (child): `ImportError: cannot import name 'post_viewer_demographics'`.
GREEN: 7 passed.

### 3.4 The tools

`linkedin_my_articles()` loads the constant address; `linkedin_item_viewer_demographics(item)`
takes `urn:li:activity:<digits>` from its caller and refuses anything else
before loading. The child's first name for the second carried the word "post",
and the name law refused it ("post" is a write verb), so it ships under
the item vocabulary. Both are in the one lane B3 block of `server.py`; the
child's mid-file import moved to the module's import list at the merge.
Envelope verdicts, each driven through its guard's own function: `clean` for
the articles tool; `not_driven:never read the page` for the demographics tool
(the harness's argument is not an activity key -- the verdict
`linkedin_company_page_counts` carries for the same reason). Both readers
are `clean` in the reader-leak baseline.

WHAT THE GUARDS DO NOT REACH, stated by the child and kept here: the
reader-leak harness's plant is never a `/pulse/` address nor a category word,
so its `clean` covers the paths it reached, not the title path or the value
path; those are covered by the modules' own plant tests. Reaching them
through the guard means a shipped drive and `ADMITTED_TEXT` entries (his own
titles as HIS_OWN, the values as AGGREGATE) -- the guard's one door, left as
question 5.

### 3.5 The census

`M C48` and `M C38` GAP -> COVERED-UNFIRED, each by its cell's bar: a tool
aimed at real captured markup that has never returned a live payload. `M
C38`'s impressions half was already read by `linkedin_creator_analytics`'s
`per_post` (`P G6`); its demographics half is this tool, and the row's state
is the weaker of the two. Whether LinkedIn serves the per-post page for
another member's item is UNMEASURED; a page that draws no card reads nothing.

---

## 4. The rows left GAP, each by what was measured

### 4.1 `M M20`, `M M40`, `M M51`: no opened conversation has ever been captured

- `_state/live8/lk_thread.skeleton.html` (the live lane's, read-only) is the
  NEW-MESSAGE composer: its `main form.msg-form` draws an editor labelled
  "Write a message...", Send, the send-mode toggle and exactly four footer
  actions -- "Attach an image ...", "Attach a file ...", "Open GIF Keyboard",
  "Open Emoji Keyboard". No video-meeting, smart-reply or assist control.
- Over every real capture on disk (the tracked fixtures and the live lane's
  `_state`), each message footer draws exactly 4 footer actions (ten
  captures, the M1 bubble addressed to a real recipient among them), and NO
  real capture draws an opened conversation: `msg-s-message-list` and
  `msg-s-event-listitem` count 0 in all of them; only the synthetic
  `messaging_thread.html` draws one. The "video-meeting" strings in five raw
  captures are static icon-asset names in a payload; "Smart replies" is a
  messaging SETTINGS label (`suggestReplies`), not a control on a thread.
- So none of the three rows' bars is about the composer: `M M20` asks for a
  conversation's own footer (its cell: "Where the control lives is
  unmeasured"), and `M M40`/`M M51` need an incoming message's suggestions and
  whether the assist fills an EDITABLE composer -- both only on an opened
  thread. NEEDS-CAPTURE: an opened conversation, ideally one already read
  (`OWN-INBOX-READS-COVERED-BY-B`), its footer and any suggestion chips, zero
  presses.

### 4.2 `M M26`, `M M27`, `M M29`, `M M31`: the captured menu cannot be bound to the conversation he names

- THE MENU IS REAL. `tests/fixtures/live3/compose_c9-open.html` draws one
  conversation's options menu open: nine `msg-thread-actions__dropdown-option`
  items, LinkedIn's words kept -- "Move to Other", one reduced to x, "Mark as
  unread", "Star", "Mute" (`data-view-name="message-toolbar-dropdown-toggle-mute"`),
  "Archive" (`...-toggle-archive`), "Report / Block", "Delete conversation",
  "Manage settings" (a link).
- BUT IT IS A LIST ROW'S MENU ON THE COMPOSE PAGE. Measured here through a
  real engine over all nine real messaging captures: 20 or 5 rows, half of
  them carrying a `msg-thread-actions__control` trigger, and ZERO rows wearing
  the active marker (`msg-conversations-container__convo-item-link--active`).
  `threads.py` measured on 2026-09-24 that "a list row carries NO thread
  identifier". So no captured menu can be bound to a thread id the caller
  passes, and a row chosen off the page would be the page supplying the target
  (`PAGE-MAY-VETO-NEVER-SUPPLY`).
- NEEDS-CAPTURE (one capture serves all four): `/messaging/thread/<id>/` for a
  conversation he has already read, with the ACTIVE row's options menu -- or
  the thread header's own, whichever is drawn -- opened and closed on Escape;
  a menu is a disclosure under the capture-press probe rule (ruling 1 of `_audit/2026-10-10-rulings-ledger-questions.md`), nothing
  committed. Then each act is built on that menu, its inverse in the same
  change: `M M29` Mute and its inverse on the same toggle; `M M31` "Mark as
  unread" (drawn, on a read row) and "Mark as read" (DERIVED -- and a read mark
  may show the sender a seen receipt, so its live proof uses a conversation
  already read); `M M27` Archive, whose inverse lives in the Archived folder
  (unmeasured: the folder pill is captured, its contents are not); `M M26`
  Delete conversation, irreversible, whose confirmation is unmeasured.

### 4.3 `M M16`: what a GIF tile press does is unmeasured

`tests/fixtures/live3/compose_c5-open.html` draws the picker open:
`section.tenor-gif__search-popover`, one `tenor-gif__search-input`, and 40
`button.tenor-gif__select-gif` tiles in two columns, each an `img` whose alt is
reduced to x. Whether pressing a tile sends at once or attaches to the draft
is unmeasured, and a send is outward and irreversible, so that measurement is
itself an act at a recipient he names (`OPERATOR-NAMES-THE-TARGET`). And the
grant binds a message's CONTENT (`AI-ASSIST-MESSAGING`'s reasoning: "text he
has not read cannot be consented to"): a GIF chosen by a search word and an
index is content he has not seen, so the preview must show the chosen GIF's
address before a token can be minted. Both are design before build.

### 4.4 `M C18`, `M C23`, `M C90`: his own item's menu -- the real one -- and what it opens

The ledger names `tests/fixtures/synthetic/own_post_menu.html`, which is a
behaviour-scripted SYNTHETIC fixture built for `share_link.py`; by the standing
rules it moves no row. The REAL menu is the live lane's raw session-1 capture
`_state/live1/post-open-menu.html` (gitignored; read for its UI words only),
whose open `feed-shared-control-menu__content` draws nine items: "Feature on
top of profile", "Save", "Copy link to post", "Embed this post", "Edit post",
"Delete post", "Who can comment on this post?", "Who can see this post?",
"View analytics".

- `M C18` (edit a published post): "Edit post" opens an editor nobody has
  captured, and the capture-press probe rule (ruling 1 of `_audit/2026-10-10-rulings-ledger-questions.md`) admits "never a composer or an
  editor". Its capture is an act on an item he names.
- `M C23` (turn off or limit comments): "Who can comment on this post?" opens
  a dialog nobody has captured. Opening it commits nothing, so the probe rule
  can reach it: one capture, his own item, Escape.
- `M C90` (verified comments filter): not one of the nine items. Where
  LinkedIn draws it is unmeasured -- the comment-control dialog of `M C23` is
  the first place to look, in the same capture.

### 4.5 `M C29`: a comment sort is not the shipped view switch's shape

On `live2/own_post.html` the sort control is drawn:
`div.comments-sort-order-toggle`, one `aria-expanded` trigger reading "Most
relevant", and its `comments-sort-order-toggle__content` EMPTY while closed --
the options render only on open. `view_switch.py`, the one sanctioned
view-switch press, drives a pill popover of checkbox or radio options closed
by a "show results" button; a single-choice dropdown that applies on select is
a different shape, so it needs its own entry in `readonly.SANCTIONED_MUTATIONS`
and its own restore proof. And the payload is WHICH comments in which order --
other members' words -- which a counts-only reader does not deliver
(`WHO-WHICH-COUNTS-ARE-NOT-DELIVERY`) and for which `people_data` has no
comment record. Not built here: design first.

### 4.6 `M C97`: no notification card can be named by its caller

The current notifications captures (`live2` to `live5`) draw each card's menu
closed in the DOM (9 cards, 9 `nt-card-settings-dropdown__trigger`, 129
`nt-card-settings-dropdown-item` nodes on `live5`), but the tracked copies
reduce its words to x; "Delete notification" is word-measured only on
`tests/fixtures/notifications.html`, the 2026-08-22 pre-rebuild capture. And a
card carries no key: its only attributes are `aria-label`,
`data-nt-card-index` (a position) and `data-view-name`, and no tool returns a
notification key. A target chosen by position is the page supplying it
(`PAGE-MAY-VETO-NEVER-SUPPLY`). First: a key a caller can pass.

**CORRECTED BY:** `_audit/2026-11-25-build-jmn26.md` -- `Delete notification` is word-measured on today's captures as well: the keyed skeletons of live sessions 5 and 10 match it on every card (9 of 9, 10 of 10). The blocker, a card key a caller can pass, stands.

---

## 5. Pins re-derived, on measured values

`scripts/census_completion.py` after the move, measured, never summed -- on
the branch, and again on the tree merged with master `0103810` (lanes K and U
had moved their own rows in between; C43 moves the same seven figures by one
each on both):

    figure           branch (base f93104c)   merged with 0103810
    adjudicated      186 -> 187              213 -> 214
    b1_no_ruling       9 -> 10                 9 -> 10
    b3_admitted       43 -> 42                41 -> 40
    delivered_broad  130 -> 131              135 -> 136
    gap              585 -> 584              558 -> 557
    gap_read          98 -> 97                92 -> 91
    unfired           21 -> 22                24 -> 25

and at the child's merge, `M C48` and `M C38` moved the same seven by two
each, measured: adjudicated 216, b1_no_ruling 12, b3_admitted 38,
delivered_broad 138, gap 555, gap_read 89, unfired 27 -- both rows join
`PINNED_B1_ROWS` under NO RULING and leave the ledger and the address table;
the triage constant `AFTER_LANE_B3_CHILD_READS` reads (120, R 10); the tool
surface reads 65 tools (47 reads, 18 writes) and 102 parameters

and `PINNED_B1_ROWS` gains `M C43` under NO RULING. It ends "every headline
figure matches its pin". `tests/test_triage_instrument.py` gains
`AFTER_LANE_B3_ITEM_TEXT` -- (129, R 15) on the branch, (122, R 12) merged;
the 2026-09-20 report's own headline is left as the history it is. The
tool-count sites moved together, measured off `mcp.list_tools()`: 62 tools,
45 reads, 17 writes on the branch; 63 tools, 45 reads, 18 writes merged (lane
U's `linkedin_send_attachment` is a write); the surface pin 63 tools and 101
parameters.
`tests/reader_leak_baseline.json` gains `item_text:read_item_text:
returns_records` and `tests/tool_envelope_baseline.json`
`linkedin_read_item_text: not_driven:never read the page` -- each driven
through its guard's own `drive`, one entry each, nothing else regenerated.
The envelope harness passes a synthetic argument, which the key check refuses
before any load -- the same verdict `linkedin_read_named_profile` records --
so the READER is the half that guard drives (`returns_records`).

THE LEDGER AND THE ADDRESS TABLE. `M C43` left GAP, so its lines left
`_audit/_census/next-step.tsv` (check_next_step GREEN, 557 rows on the merged
tree) and `_audit/_census/read-addresses.tsv` (91 of 91). The other thirteen
rows' ledger lines still say BUILD on the capture the ledger named; section 8
proposes their true next steps to lane K, whose judged table it is.

---

## 6. Gates run

LOCAL, targeted, serial (`-p no:randomly`, never `-n`), the live-session flag
checked before each file and absent throughout; the full suite on CI only.

    file / instrument                                        result
    tests/test_item_text.py                                  red first (ImportError), a harness red
                                                               (network guard, 13 of 33), then 33 passed
    tests/test_no_committed_identity.py (after commit)       1076 passed
    tests/test_c43_rests_on_the_feed_content_ruling.py       16 passed (re-bound)
    tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py  red (62 == 61), re-pinned, 64 passed
    tests/test_every_tool_is_on_the_surface.py               red (62 == 61), 19 passed
    tests/test_server_surface.py                             red twice (EXPECTED_TOOLS; 45 == 44), 52 passed
    tests/test_prose_that_makes_a_claim.py                   red (the headline count), 16 passed
    tests/test_a_people_reader_reads_one_page.py             91 passed
    tests/test_page_strings_leave_only_as_people_records.py  44 passed
    tests/test_feed_tally.py                                 30 passed
    tests/test_triage_instrument.py                          red (130 -> 129), 17 passed
    tests/test_tool_envelopes_emit_no_page_string.py         red (unclassified), 4 passed
    tests/test_readers_emit_no_page_string.py                red (no verdict; then a helper discovered
                                                               as a reader), 704 passed
    tests/test_a_literal_repeats_no_member.py                19 passed
    tests/test_next_step.py                                  10 passed
    scripts/census_completion.py                             every headline figure matches its pin
                                                               (branch, and both merged trees)
    scripts/check_next_step.py, check_read_addresses.py,     GREEN on the merged tree
      check_write_classes.py, ruling_holds.py
    scripts/build_audit_index.py, build_rulings_index.py,    --write, then --check clean
      build_blocker_map.py
    pre-commit identity gate                                 226 spellings, 0 hits, every commit

CI (`scripts/lane_ci.py`): see the lane's final message for the run id and
conclusion. The first `push` was refused locally (origin/master had moved to
`2b165fd`; merged); the second was rejected by the remote with a bare
"(failed)" after the local gate passed (0 hits across 1125 blobs); the
third, unchanged, created `ci/worktree-agent-a008721ba8a0553be` at
`7a3ada1` -- a transient remote failure, recorded as such.

---

## 7. The live-proof spec, per moved row

`M C43` -- `linkedin_read_item_text`:

- TARGET: one of HIS OWN items, so no third party's words are read for a
  proof. Its key from `linkedin_my_activity_items` (one load of his own
  activity rail; reuse a key the session already holds and it is zero).
- LOADS: 1 -- the item's permalink. Nothing pressed.
- THE BAR (the cell's): `readable` true; `item` a `people_data.Post` record
  whose author is the member the header names (his own name, read at runtime);
  `text` non-empty and equal in substance to what the permalink shows;
  `expanded` true, `truncated` false for an item under 3,000 characters; `why`
  the "read" sentence; nothing of the words in any log line or error field.
  Then `M C43` COVERED-UNFIRED -> COVERED-PROVEN.
- INVERSE: none -- a read changes nothing on the item.
- STOP-ALL: a landing anywhere but the permalink asked for; an auth wall or a
  checkpoint; `readable` false on his own item (the reader's structure has
  drifted -- record the counts the reading returns and stop that row); any
  page string outside the record in the envelope. Never another member's
  item for the proof unless he names it.

`M C48` -- `linkedin_my_articles`:

- TARGET: his own articles list, a constant address. LOADS: 1. Nothing pressed.
- THE BAR: `readable` true. If he has no article the honest reading is
  `articles` [] with `empty` true, and the proof records whether the slot drew
  anything at all; if an article is drawn, each entry a `/pulse/` path and a
  title matching what the page shows. Then COVERED-PROVEN, with the entry shape
  measured only if one was drawn.
- INVERSE: none. STOP-ALL: a redirect off the address; an auth wall;
  `readable` false (record the counts and stop the row).

`M C38` -- `linkedin_item_viewer_demographics`:

- TARGET: one of HIS OWN items, its key from `linkedin_my_activity_items` --
  ideally the one session 1 loaded. LOADS: 1. Nothing pressed (no tab).
- THE BAR: `card_found` true and `points_found` > 0, each row a category
  word, an integer percentage agreeing with its progressbar, and a value that
  is either one word or `<redacted>`/`<opaque>`. Then COVERED-PROVEN.
- INVERSE: none. STOP-ALL: a redirect off the per-post address; an auth wall;
  any multi-word value leaving unredacted (the shaper failed -- stop and
  report, never store it); never another member's key.

---

## 8. Questions for the orchestrator, each with its ground

1. CHILDREN'S TYPE. This lane's fleet prompt says children are spawned as
   `implementer`; the standing rules say "general-purpose (never
   implementer)", and the user-scope rule pins every subagent to the Opus
   family. The child ran as general-purpose. Which binds?
2. LANE K'S LEDGER, THIRTEEN LINES. Each still says BUILD on the capture the
   ledger named; what comes first, measured (section 4): `M M20`, `M M40`,
   `M M51` -- CAPTURE (an opened conversation's footer); `M M26`, `M M27`,
   `M M29`, `M M31` -- CAPTURE (the active row's or thread header's menu on
   `/messaging/thread/<id>/`); `M C23`, `M C90` -- CAPTURE (the
   comment-control dialog of his own item); `M C18` -- a RULING, since the
   probe rule admits "never a composer or an editor"; `M M16` and `M C29` --
   design (a preview that shows the chosen GIF; a single-choice sort press and
   a comment record type); `M C97` -- a notification key a caller can pass.
3. `M C29`'S PAYLOAD. Which comments, in which order, is other members'
   words. `people_data` has no comment record, and a counts-only reader does
   not deliver WHICH (`WHO-WHICH-COUNTS-ARE-NOT-DELIVERY`). Whoever owns
   `people_data` decides a comment record before a sort is built.
4. A PAGE'S ITEM. `people_data.Post` requires a member author, so an
   organisation Page's item returns no words. Lane G2's new `Organisation`
   record could carry that author; widening `Post` is that owner's call.
5. THE TWO TEXT PATHS THE READER GUARD CANNOT REACH (section 3.4). His own
   article titles and the shaped demographic values leave outside a
   `people_data` record, covered by the modules' own plant tests but not by
   the reader-leak harness, whose plant never takes those shapes. Admit them
   through a shipped drive and `ADMITTED_TEXT` (HIS_OWN, AGGREGATE), or have
   the titles leave inside a record type -- the guard's one door, so the
   orchestrator's call.
