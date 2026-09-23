claude-opus-5-5[1m]

# Lane L5 -- MESSAGING: deliverable sends and a receipt-safe inbox

Written as the lane runs. Worktree branch `worktree-agent-a6bb3cc0961290132`, cut from `master` at
`9c219c8`. OFFLINE throughout: no browser was attached to LinkedIn, no grant was issued outside the
fixture tests, `writes_enabled()` stayed False in every process this lane started, and nothing
touched port 9224 or the Chrome profile. The two captures this lane measured are gitignored files in
the main checkout's `_state/`; they were opened in a local headless Chromium with JavaScript
disabled and every request aborted, and only SHAPES and COUNTS left them (section 1). The fixtures
this lane committed are SYNTHETIC: structure measured, content invented.

## 0. Status log

- 00:38 -- lane opened; read `_audit/2026-09-23-rulings-write-class-and-delegated-calls.md`, the
  messaging census (sections 3.1 and 5), the 23 R2 lines and the 9 R3 messaging lines of
  `_audit/_census/write-classes.tsv`, the lane-L4 record, and `writes.py`'s grant, observe,
  preview, perform and verify paths end to end.
- 01:05 -- the captures measured (section 1). THE BRIEF'S ROUTE HAS ONE PREMISE THE PAGE DOES NOT
  SUPPORT, and it is recorded before any design: a conversation-list row carries NO thread
  identifier, so a listing cannot mark a caller-supplied thread id unread (section 2).
- 01:50 -- `5eadfe7`: the build (sections 2 and 3), its fixtures and 80 tests, green over the
  three new or changed test files (39 + 41 passed, on a box running five other lanes' suites).
- 02:05 -- the corpus-wide guards run over `5eadfe7`: two red, one of them this lane's (section
  8.2). The census cells, the write-class dispositions and this record's R2 table written.

## 1. WHAT THE CAPTURES SHOW (measured offline, shapes and counts only)

Two captures, both taken 2026-09-20 and held gitignored in the main checkout's `_state/`:
`/messaging/compose/` (the composer, admitted by exact-url exemption) and `/messaging/` (which
redirected into a conversation of LinkedIn's choosing). Every other capture in `_state/` was
scanned for the messaging overlay.

### 1.1 The overlay draws no list

Twelve captures of other admitted pages (job search, collections, events, groups, the sharebox,
job alerts, search appearances) each carry the messaging overlay -- 24 `msg-overlay` class
occurrences and 4 `msg-overlay-list-bubble` -- and ZERO conversation rows
(`msg-conversation-listitem` 0 in every one). The bubble wears
`msg-overlay-list-bubble--is-minimized`; the two occurrences of the word "unread" on those pages
are the filter pill and a `data-test` hook, not rows. **The overlay is not a receipt-free list on
this account as captured**: minimised, it renders no conversation at all. Whether an EXPANDED
overlay renders rows is unmeasured (capture spec C4, section 9).

### 1.2 The composer page draws the whole list and opens no conversation

`/messaging/compose/` (the 2026-09-20 capture):

    li.msg-conversation-listitem                        20
      rendered rows                                     10
      placeholders (msg-conversation-card--occluded)    10   no content: virtualised
    rows carrying 'Select conversation with <name>'    10
    li.msg-s-message-list__event (a thread's messages)   0   NO CONVERSATION IS OPEN
    rows wearing the active-conversation marker          0
    the composer form (form.msg-form)                    1   one role=textbox editor,
                                                              Send drawn DISABLED
    filter pills (button, no href)                       6   Focused Jobs Unread Connections
                                                              InMail Starred

Against `/messaging/`, captured the same minute:

    li.msg-s-message-list__event                         1   A THREAD IS OPEN
    rows wearing msg-conversations-container__convo-item-link--active   1   (row 1)
    hidden text 'Active conversation'                     1   (row 1)

So the composer draws the same conversation list the inbox does and opens nothing. That is the
receipt-free list the brief asked for, and it is on an address already admitted (census `M45`,
COVERED-PROVEN, fired 2026-09-20 through `linkedin_compose_fields`).

### 1.3 A row carries no thread identifier

Across the 10 rendered rows of BOTH captures, every attribute on every row and every descendant
was checked for a messaging urn, a `/messaging/thread/` path, or a `2-`-prefixed token: **zero**.
The row's clickable element is `div.msg-conversation-listitem__link` with `tabindex=0` and no
href; LinkedIn routes a row to its thread in client state. Nor does either page embed conversation
entities in a data payload (`msg_conversation` 0, `unreadCount` 0, `conversationUrn` 0).

### 1.4 The thread view (one capture, and it is a sponsored conversation)

The conversation `/messaging/` opened was a SPONSORED one (`msg-sponsored-conversation-thread`), so
it draws no reply form (`form` 0, `role=textbox` 0). What it does draw, measured:

    ul.msg-s-message-list-content, in DOM order:
      li.msg-s-message-list__top-of-list, __top-banner, (unclassed), __loader
      li.msg-s-message-list__event ... the LAST one also wears msg-s-message-list__last-msg-
      li.msg-s-message-list__typing-indicator-container--without-seen-receipt
      li.msg-s-message-list__bottom-of-list
    div.msg-s-event-listitem  --other  (the other party's message)  with data-event-urn
      div.msg-s-message-group__meta > .msg-s-message-group__name, time.msg-s-message-group__timestamp
      p.msg-s-event-listitem__body
    thread header: exactly one span.msg-entity-lockup__entity-title (the correspondent's name)
                   button.msg-thread__star-icon (a real button, two-word aria-label)
                   button.msg-thread-actions__control (the conversation's options dropdown)
    sponsored actions: 'I want to know more!' (button), a link, 'Not interested' (button)

What is NOT in any capture, and every reader below says so where it matters:
- a message HE sent (so "his" is derived from the ABSENCE of the measured `--other` modifier);
- a DRAWN seen receipt (only the `--without-seen-receipt` modifier is measured);
- a thread's reply form (measured on the composer, which uses the same `msg-form` component and
  class `msg-form--thread-footer-feature`; that it is the same form in a thread is derived);
- an UNREAD row in the current markup (every rendered row read);
- a Recruiter InMail's response controls (the captured response UI is a sponsored message's).

### 1.5 The composer's form, control by control (UI text, no member data)

    div.msg-form__contenteditable  role=textbox  aria-label 'Write a message...' (U+2026)
    button.msg-form__expand-btn    'Maximize compose field'
    input.msg-form__attachment-upload-input  type=file  accept image/*
    button  'Attach an image for your draft conversation'
    input.msg-form__attachment-upload-input  type=file  accept image/*,.ai,.psd,.pdf,.doc,...,.mp4
    button  'Attach a file for your draft conversation'
    button  'Open GIF Keyboard'
    button  'Open Emoji Keyboard'
    button.msg-form__send-button   type=submit  'Send'  DISABLED while empty
    button.msg-form__send-toggle   'Open send options'

And on the list: the row's star is `div[role=img][aria-label='Star conversation']` -- an ICON, not
a control; the pressable star is the thread header's `button.msg-thread__star-icon`. The row's
options trigger is `button.msg-thread-actions__control[aria-expanded=false]`; its menu items are
not in the DOM until it is opened. The filter pills are `button`s whose `data-test` hook values
are UPPERCASE (`JOB`, `UNREAD`, `CONNECTIONS`, `INMAIL`, `STARRED`); the FOLDER is a separate
dropdown trigger reading `Focused`. The minimised overlay's own hidden text says pressing it
"open[s] the list of conversations" -- a list, not a thread (capture spec C4).

## 2. THE RECEIPT-SAFE ROUTE, AS BUILT -- and the one place it had to be coarser than asked

The brief asked for three things. What the captures allowed, each against its ask:

| asked | built | what the page decided |
|---|---|---|
| list conversations WITH their unread state WITHOUT opening any | `linkedin_list_conversations` -- reads `/messaging/compose/` | the composer draws the list and opens nothing (section 1.2). One load. The result carries the evidence as counts: messages on the page, rows marked active, whether the landing was the composer |
| open only a CALLER-SUPPLIED thread id at `/messaging/thread/<id>/` | `linkedin_open_thread(thread_id, allow_unread=False)` | the id is a tool argument, validated against the read allowlist's own digit-first shape, formatted into one constant template, and compared against the landing; a landing elsewhere is NOT read. Two loads |
| refuse, by default, to open a thread THE LISTING MARKED unread | the guard refuses while ANY rendered row reads unread; `allow_unread=True` is the opt-in | **COARSER THAN ASKED, AND THE CAUSE IS MEASURED:** a list row carries no thread identifier (section 1.3), so no listing can say which row a caller's thread id is. Refusing only "that row" is not expressible; refusing on any unread row is the tightest rule the page supports |

The same guard now fronts `linkedin_open_messaging` (the tool the live lane held `M M33` and
`M M43` on): the composer's list is read FIRST, and `/messaging/` is asked for only when no
rendered row reads unread. When that holds, the conversation LinkedIn chooses is one he has read
(on the one capture of the choice, the most recent row), so the load shows nobody a new "seen".
Its result gains `receipt_guard` and `landed_conversation` -- the read indicator on the last words
he wrote in whatever conversation it opened, which banks `M M49` with no target at all.

**WHAT THE GUARD CANNOT SEE, stated in every answer it gives (`receipt_guard.residue`):** the
placeholder rows (LinkedIn renders about ten rows and leaves the rest empty), conversations older
than those, and folders the default view does not draw -- the list's folder control reads
`Focused`, so an unread InMail filed under Other would not stop it. The argument for why the
rendered rows are the ones that matter -- a new incoming message moves its conversation to the
top -- is DERIVED, not measured, and the residue is printed rather than rounded away.

**UNREAD ITSELF IS MATCHED AS A UNION** -- a class token containing `unread`, the whole word in
text or an accessible name, or a notification badge -- because every rendered row on both
captures was read, so the current unread markup is in no capture (capture spec C1). The READ form
is measured; a row unread in a fourth way would read false, and the capture spec says how to
settle it without opening anything.

**WHAT CROSSES INTO THIS PROCESS.** Every reader in `linkedin_server/threads.py` is a Playwright
locator chain -- no injected script, so no `evaluate` waiver was spent (the budget in
`tests/test_readonly.py` forces exactly that question). Text is compared inside the page by
Playwright's own text engine (`get_by_text(..., exact=True)` inside `filter(has=...)`) and only
counts come back. No message body, no correspondent's name and no thread id is returned, except
the list's names when the caller passes `include_names` and the reply preview's title (section 3).

## 3. `M M10` -- A REPLY INSIDE A CALLER-SUPPLIED CONVERSATION, AND A SEND THAT CONFIRMS ITSELF

`linkedin_send_reply(thread_id, text, confirm_token="")` -- spec `send_reply`, the fourteenth in
`writes.PERFORMABLE`, grant-gated and off by default like every other write. No boundary moved:
the fill and the click are `perform()`'s existing ones, `readonly.SANCTIONED_MUTATIONS` is
unchanged, and the thread address was already admitted.

1. PREVIEW -- loads the conversation by the grant's thread id (one load), refuses unless the
   landing IS that thread, reads the reply box: exactly one editor, empty, one Send drawn
   DISABLED, no recipient box. It records how many messages ALREADY carry exactly his words
   (the before-count). It prints the conversation's title as `who_this_would_reach` -- read off
   the conversation's own header, added to a NEW dict after `grant.preview` was assigned, kept in
   no grant, no log and no file (the invitation ruling's own argument, 2026-08-31, applied to a
   conversation named by id).
2. PERFORM -- reloads the conversation, holds the landing to the thread id again, re-reads the
   box (`_live_control`), fills his words (the grant's own slice), and runs
   `threads.reply_send_gate`: Send enabled, box not empty, still no recipient box. Only then is
   Send pressed.
3. VERIFY -- first IN PLACE: does the box still hold his words with Send enabled (the NOT-SENT
   evidence a reload would erase)? Then a FRESH LOAD: `reply_sent` needs ALL of -- his words are
   the LAST message, that message carries no `--other` modifier, and the count of messages
   carrying exactly his words rose by EXACTLY ONE against the preview's before-count.
   `reply_box_holds_text` (performed False) when the box held them and nothing new appeared.
   Anything else is `unknown`, with every count, and the receipt says do NOT retry.

**WHAT IS DERIVED IN IT, and how each fails.** That a conversation draws the composer's form: if
not, the preview reads UNKNOWN and mints nothing. That his messages lack `--other`: if they carry
some other marker, the verdict reads UNKNOWN on a reply that landed -- never SENT on one that did
not, because the text-delta condition still has to hold.

### 3.1 Thread-first and the addressing problem -- the answer, recorded

**THREAD-FIRST REMOVES THE ADDRESSING PROBLEM FOR EVERY RECIPIENT WHO ALREADY HAS A CONVERSATION
WITH HIM, AND FOR NOBODY ELSE.** A conversation fixes its recipient, so the typeahead (measured
dead) and the chip selectors (never matched) are simply not on the path; the only aiming question
left is "is the browser on the thread he named", which an id inside an admitted address answers,
compared before the click and after. For a FIRST contact there is no thread and no thread id, and
thread-first offers nothing: that still needs the compose-by-identifier address the read boundary
refuses on purpose (`_audit/2026-09-03-typeahead-name-matching-is-dead.md`), and even then the
OBSERVING problem stays open -- no instrument has ever seen a committed recipient. The thread id
comes from him (his browser's address bar); this server never reads one off a page, and the list
cannot hand one over because rows carry none.

### 3.2 `M M1` / `M M2` -- the send that could never say SENT

`linkedin_send_message` said, in its own docstring, that it CAN REPORT NOT SENT AND CAN NEVER
REPORT SENT, because the only surface that could confirm a send -- the conversation -- was
forbidden. Ruling `WRITE-CLASS-B` lifted that. `_verify_after`'s `send_message` arm now reads the
conversation a send leaves drawn on the SAME page, in place -- its id is page-derived and is never
navigated to -- and returns `message_sent` when his exact words are its last message
(`threads.sent_in_place`). It is weaker than the reply's verdict and says so: with no before-count,
an identical earlier last message of his in the same conversation reads the same. The test that
pinned SENT unreachable (`test_verify_after_can_never_return_the_to_state`) argued in its own
docstring that a future SENT return would have to argue with it; the argument is its replacement,
`test_verify_after_reaches_the_to_state_only_through_the_conversation_read_back`, which shows the
composer readings still never SENT, a drawn conversation carrying his words SENT, and other words
UNKNOWN. **THE STATES DO NOT MOVE:** both rows stay COVERED-CANNOT-DELIVER, because the recipient
gate still refuses before any send, and thread-first (3.1) reaches only existing conversations.

## 4. THE 23 R2 ROWS -- one verdict each

BUILT = grant-gated, off by default, with failing controls. The `queued:` token is what the
row's line in `_audit/_census/write-classes.tsv` now carries; every token is this lane's own name
for what binds, and none is a blocker-ledger entry.

| row | verdict | token | why |
|---|---|---|---|
| `M M10` reply in a thread | **BUILT** | built:send_reply | section 3; COVERED-UNFIRED |
| `M M17` send an emoji | **BUILT, by ruling D6** | built:send_reply | an emoji is a character of the words `linkedin_send_reply` types; the emoji keyboard is not reproduced. Limit: an existing conversation only, and if LinkedIn draws the emoji as an image the exact-text read-back answers UNKNOWN, never SENT. COVERED-UNFIRED |
| `M M47` Recruiter InMail response | NEEDS-CAPTURE | CAPTURE-C2-RECRUITER-INMAIL-RESPONSE | the only response UI in any capture is a SPONSORED conversation's ('I want to know more!', 'Not interested', no reply box); a Recruiter InMail's controls are not known to be the same. Once captured, the press is `M10`'s shape |
| `M M11` edit a sent message | NEEDS-CAPTURE | CAPTURE-C6-OWN-MESSAGE-MENU | the per-message menu on his own message has never been opened |
| `M M14` photo | NEEDS-CAPTURE | CAPTURE-C3-CONVERSATION-ATTACHMENTS | thread-first removes the recipient problem; the conversation's own file inputs and an attachment message's markup are unmeasured, and `UPLOAD_ACTIONS` stays empty until they are |
| `M M15` video | NEEDS-CAPTURE | CAPTURE-C3-CONVERSATION-ATTACHMENTS | as `M M14` |
| `M M18` files | NEEDS-CAPTURE | CAPTURE-C3-CONVERSATION-ATTACHMENTS | as `M M14` |
| `M M16` GIF | NEEDS-CAPTURE | CAPTURE-C5-GIF-PICKER | the control is measured ('Open GIF Keyboard'); the picker, and whether choosing dispatches at once, are not |
| `M M20` video meeting | NEEDS-CAPTURE | CAPTURE-C7-VIDEO-MEETING-CONTROL | the composer's footer was measured with FOUR controls and none of them is a video meeting; where it lives is unmeasured |
| `M M6` message request | BLOCKED | BLOCKED-FIRST-CONTACT-ADDRESSING | no conversation, so no thread id; the only route addresses a new recipient -- by name (measured dead) or by an identifier address the read boundary refuses on purpose. Needs a ruled compose-by-identifier admission AND an observed committed recipient |
| `M M13` forward | BLOCKED | BLOCKED-FIRST-CONTACT-ADDRESSING | a forward chooses a NEW recipient in a picker |
| `M M21` group chat | BLOCKED | BLOCKED-FIRST-CONTACT-ADDRESSING | several new recipients |
| `N 160` message requests (compound) | BLOCKED | BLOCKED-FIRST-CONTACT-ADDRESSING | its send half is `M M6` |
| `N 4` invite from a search result | BLOCKED | BLOCKED-SEARCH-FIRES-NOTHING | the people-search admission binds that nothing is fired from that surface, and a result row's Connect can send with no dialog: a ruling first, then a CALLER-SUPPLIED profile identity (lane S's readers; not used here) |
| `N 5` note on an invitation | BLOCKED | BLOCKED-N1-FIRST-FIRE | the note field appears only after Connect is pressed, and pressing Connect can send at once, so no capture of it can be made safe; the first supervised `N 1` send at a target he names is the capture |
| `N 6` re-invite after expiry | BLOCKED | BLOCKED-SENT-INVITATIONS-SURFACE | knowing it expired needs the Sent manager, whose address carries a forbidden substring |
| `N 166` invite a group member | BLOCKED | BLOCKED-GROUP-MEMBERS-ADDRESS | `/groups/<id>/members/` refused; ruling `GROUPS-ADDRESS-BUYS-NO-WRITE` |
| `N 167` request to a group member | BLOCKED | BLOCKED-GROUP-MEMBERS-ADDRESS | as `N 166`, and `M M6`'s addressing |
| `N 191` message attendees (connections) | BLOCKED | BLOCKED-EVENT-ATTENDEES-ADDRESS | `/events/<id>/attendees/` refused. An attendee he already has a conversation with is reached by `linkedin_send_reply` -- not claimed, because the row's capability is reaching them from the event |
| `N 192` InMail attendees | BLOCKED | BLOCKED-EVENT-ATTENDEES-ADDRESS | as `N 191`, plus first-contact addressing; the InMail half's exclusion is the census owner's call |
| `N A11`, `N A12`, `N A13` admin messaging | BLOCKED | BLOCKED-ADMIN-SURFACE-AND-SECOND-HUMAN | a group or event he administers, its admin surface unadmitted, and a second consenting human; none is on record |

    BUILT 2 (M M10, M M17)   NEEDS-CAPTURE 7   BLOCKED 14   = 23

**THE CHECKER HAD TO MOVE FOR THIS TABLE TO BE WRITTEN.** `scripts/check_write_classes.py`
refused any disposition but `classify-only` on a non-R1 line -- lane L4's scope, stated in its own
error text as "classify-only in this lane". `WRITE-CLASS-B` let R2 be built, so R2 and R3 lines
may now carry `built:` and `queued:` like R1; an R1 line may still not be `classify-only`. The
plant that tested the old rule is replaced by one that tests the rule that remains, and a second
test shows a queued R2 line drawing no problem.

## 5. THE NINE R3 MESSAGING ROWS -- classed, none built

The brief asked for private-and-reversible or not, on evidence. The evidence is the census's own
REV column and LinkedIn's help articles; none of these controls has ever been read by this server.

| row | class | evidence | token |
|---|---|---|---|
| `M M27` archive | PRIVATE AND REVERSIBLE | an archived conversation is restorable, and archiving changes only his inbox | CAPTURE-C9-CONVERSATION-OPTIONS-MENU |
| `M M29` mute / unmute | PRIVATE AND REVERSIBLE | his own notifications for one conversation; nobody else is told | CAPTURE-C9-CONVERSATION-OPTIONS-MENU |
| `M M30` star | PRIVATE AND REVERSIBLE | a star is his own filter; the row's 'Star conversation' node is a `div role=img` ICON, and the pressable control is the header's `button.msg-thread__star-icon` -- aimable thread-first. Its ON label is uncaptured | CAPTURE-C10-STAR-ON-LABEL |
| `M M31` mark read / unread | UNREAD: PRIVATE AND REVERSIBLE. READ: NOT KNOWN TO BE PRIVATE | marking read may show the sender a "seen" -- unmeasured | CAPTURE-C9-CONVERSATION-OPTIONS-MENU |
| `M M8` decline a request | REVERSIBLE; PRIVACY UNMEASURED | a declined request can be accepted later (REV); whether the sender learns of it is unmeasured | CAPTURE-C8-MESSAGE-REQUESTS |
| `M M7` accept a request | NOT PRIVATE, NOT REVERSIBLE | the requester can then write to him and sees it accepted | CAPTURE-C8-MESSAGE-REQUESTS |
| `M M22` add / remove participants | NOT PRIVATE | the others see who joined or left | CAPTURE-C9-CONVERSATION-OPTIONS-MENU |
| `M M25` leave a conversation | NOT PRIVATE, NOT REVERSIBLE | "you will not be able to reply or re-join" | classify-only |
| `M M48` react to a message | NOT PRIVATE, REVERSIBLE | the author is shown the reaction | CAPTURE-C6-OWN-MESSAGE-MENU |

**WHY NONE WAS BUILT.** The four private-and-reversible ones all need a control nobody has read:
archive, mute and mark-unread sit in the conversation's options menu (its items are not in the DOM
until opened -- measured, section 1.5), and the star's ON label is uncaptured. A write aimed at an
unread control is the guess this package refuses; C9 and C10 are one disclosure press and one
page capture respectively, and both are safe on the composer or on a read conversation.

## 6. THE SAFETY THE BRIEF ASKED FOR, AND WHERE EACH PIECE IS

- **No capture press can send.** Every capture spec below that needs a press says why that press
  cannot dispatch anything; the unsafe ones (Connect, a GIF choice) are either refused or stop at
  the disclosure.
- **A thread id comes from a tool argument only.** `threads.thread_url` formats one constant
  template with the caller's id after checking the allowlist's own shape; the landing is compared
  (`threads.landed_on_thread`), never read back or returned. No function here reads an id off a
  page. The navigation-derivation guard was run over the change and convicted a first version:
  `observe` passed the landing into the reader's call, which bound three names to it, and the
  guard's module-wide name taint spread to `url` in `_load`. The landing is now compared in a
  condition and bound to nothing (section 8.2).
- **No new write widens a set without a test that fails without the grant.** `PERFORMABLE` gains
  `send_reply` and `SANCTIONED_WRITES` gains `linkedin_send_reply`; `tests/test_send_reply.py`
  refuses without a grant (writes off; no token, `None`, `True`, a forged token; an unredeemed
  grant; a non-grant -- zero navigations), refuses a grant for another thread, other words, or
  another action, and refuses a second use at both doors, with the second-use guard shown failing
  when its flag is cleared. `UPLOAD_ACTIONS` is unchanged (empty).
  `readonly.SANCTIONED_MUTATIONS` is unchanged: the fill and the click are `perform()`'s own.
- **Error fields carry a type or a composed reason.** Every `except` in `threads.py` records
  `type(exc).__name__`; every refusal is built from counts and closed tokens; a landing is
  described through `landing.withheld`, never quoted. `_send_gate` and the other existing gates
  (lane G's) are untouched: the reply has its own gate, `threads.reply_send_gate`.
- **Nothing third-party is returned.** No message body, correspondent's name or thread id leaves
  any reader. The two named exceptions: `include_names` on the list (his own inbox, opt-in, as
  `linkedin_open_messaging` already offered) and the reply preview's `who_this_would_reach`,
  asserted absent from `grant.preview`, the grant's target and every receipt.

## 7. EXPECTED PIN MOVES -- not re-pinned here, as the brief orders

`scripts/census_completion.py --check`, run on this branch after the census edits:

    adjudicated        434 -> 437
    b1_no_ruling        15 ->  16     M M49
    b1_standing         10 ->  12     M M10, M M17 (OPERATOR-NAMES-THE-TARGET)
    delivered_broad    100 -> 103
    gap                270 -> 267
    gap_read            66 ->  65     M M49
    gap_write          150 -> 148     M M10, M M17
    unfired             25 ->  28
    PINNED_B1_ROWS     + M M10 and M M17 on OPERATOR-NAMES-THE-TARGET, + M M49 on no ruling

`scripts/count_census_states.py --expect J=54,P=54,M=74,N=85` MATCHES at 267 (messaging 77 -> 74;
stated rows 704, unchanged; `pin_census_rows` reports no drift -- no row entered or left).

The tool surface, pinned in `tests/test_server_surface.py`,
`tests/test_every_tool_is_on_the_surface.py` and
`tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py`:

    tools                     51 -> 54    + linkedin_list_conversations, linkedin_open_thread
                                            (reads), linkedin_send_reply (a write)
    read / write split     38 / 13 -> 40 / 14
    pinned parameters         69 -> 76    + include_names; + thread_id, allow_unread;
                                            + thread_id, text, confirm_token; and
                                            linkedin_open_messaging + allow_unread
    PERFORMABLE               13 -> 14    + send_reply (pinned at 13 in
                                            tests/test_preview_state_and_click_state.py and
                                            tests/test_receipt_names_its_own_action.py)
    SANCTIONED_WRITES         14 -> 15    + linkedin_send_reply
    prose counts              README.md, server.py and __init__.py name the tool total

Two derived tables that measure the change rather than pin it, also left for the merge:
`tests/tool_envelope_baseline.json` and `tests/reader_leak_baseline.json` (one entry per new tool
and reader, written with each module's own `--write-baseline`), and `scripts/ci_shard_timings.json`,
which prices 157 test files and now falls under two thirds of 236 because this lane added two
(section 8.2).

## 8. COMMITS, GATES, AND WHAT DID NOT RUN

(Filled at the end of the lane; see 8.1 to 8.3.)

## Live queue

Every call below runs in a process the live lane owns, spaced by its own budget. Loads are page
loads; "HE NAMES" means OPERATOR-NAMES-THE-TARGET applies and nothing fires without it.

| row | call | target | loads | what banks it |
|---|---|---|---|---|
| `M M43` | `linkedin_list_conversations()` | none (own inbox, nothing opened) | 1 | COVERED-PROVEN when it returns rows with `opened_a_conversation.opened == false` and `rows_rendered >= 1`. Its `rows[].unread` and `unread_rendered` are also the reading capture C1 wants whenever a row is unread |
| `M M33` | `linkedin_open_messaging(message_filter="inmail")` | none (own inbox, read conversation) | 2, plus one pill press | COVERED-PROVEN when `receipt_guard.proceed` is true, `active_filter.activated` is true and `url_movement` is `filter_state`. If the guard refuses -- a rendered row reads unread -- it spends 1 load and banks nothing: he reads that conversation himself first, or passes `allow_unread=True` |
| `M M49` | `linkedin_open_messaging()`; if its `landed_conversation.read_indicator.state` is `not_applicable` (the last message there is theirs), `linkedin_open_thread(thread_id=<a read conversation whose last message is his>)` | none (own inbox, read conversation) for the first; HE NAMES a thread id for the second | 2, then 2 | COVERED-PROVEN when `read_indicator.state` is `not_drawn` or `drawn` -- and a `drawn` reading also turns the derived `--with-seen-receipt` marker into a measured one |
| `M M10` | `linkedin_send_reply(thread_id=<HE NAMES>, text=<HE NAMES>)`, he reads `who_this_would_reach`, then the same call with `confirm_token=<token>` within 120 s | HE NAMES the conversation and the exact words | 1 (preview), then 2 (act, and the fresh read-back) | COVERED-PROVEN when the receipt reads `performed: true, verified: true`. The preview alone also delivers capture C3(a) and C7's footer reading, as counts |
| `M M17` | as `M M10`, with an emoji inside `text` | HE NAMES | 1, then 2 | COVERED-PROVEN on `performed: true`. `unknown` means LinkedIn drew the emoji as something other than the text -- record it; do NOT retry |
| `M M1`, `M M2` | none | -- | 0 | nothing can bank them: the recipient gate still refuses before any send. For an existing conversation the route is `M M10` |

Total for the five rows, one pass: 9 to 11 loads.

## Capture queue

Each spec names the page, the state it must be in, the element, and why taking it opens no unread
conversation and sends nothing. "Capture" means the live lane's own page capture (`page.content()`
after the settle it already uses), saved gitignored and read offline for SHAPES only.

- **C1 -- an unread row on the composer's list** (`M M33`, `M M43`, `M M49`'s guard). PAGE
  `/messaging/compose/`. STATE at least one conversation he has not read. ELEMENT every rendered
  `li.msg-conversation-listitem`: class tokens on the row and descendants containing `unread`, its
  visually-hidden texts, any badge element, and the class tokens of
  `.msg-conversation-card__participant-names` (a bold name is a candidate signal). WHY SAFE the
  composer draws the list and opens no conversation (measured: 0 messages, 0 active rows); no press
  is made. LOADS 1.
- **C2 -- a Recruiter InMail's response controls** (`M M47`). PAGE `/messaging/thread/<id>/`, the
  id HE NAMES, of a Recruiter InMail he has ALREADY READ. STATE nothing unread among the composer's
  rendered rows -- `linkedin_open_thread(thread_id)` enforces that and is itself one of the two
  loads. ELEMENT every button and link in the conversation's response area (the sponsored form was
  `.msg-s-sponsored-message-actions`): tag, `type`, text, whether inside a form. WHY SAFE the
  conversation is read, and nothing is pressed. LOADS 2.
- **C3 -- a conversation's own reply form and an attachment message** (`M M14`, `M M15`,
  `M M18`; confirms `M M10`'s derived form). PART (a) costs nothing extra: the first
  `linkedin_send_reply` PREVIEW reports `file_inputs`, `file_input_accepts`, `footer_actions`,
  `editors` and `send_controls` for the named conversation. PART (b): PAGE a READ conversation he
  names in which he has already sent an attachment; ELEMENT the attachment message's markup (class
  tokens, whether a file name is drawn). WHY SAFE read conversation, no press. LOADS 1 (b).
- **C4 -- the expanded overlay** (an alternative receipt-free list, optional). PAGE any admitted
  page drawing the overlay, e.g. `/feed/`. PRESS `button.msg-overlay-bubble-header__button` -- its
  own hidden text says it opens the list of conversations. WHY THE PRESS CANNOT SEND it is a
  `type=button` toggle outside any form, and its stated effect is a list, not a conversation.
  RECORD whether rows render inside `.msg-overlay-list-bubble` and that
  `li.msg-s-message-list__event` stays 0; then minimise it again and verify, by the
  disclosing-press rules. LOADS 1.
- **C5 -- the GIF picker** (`M M16`). PAGE `/messaging/compose/` -- deliberately the COMPOSER:
  with no recipient committed nothing can be dispatched from it at all. PRESS 'Open GIF Keyboard'
  (`type=button`, inside the form but not a submit). WHY THE PRESS CANNOT SEND it is not a submit,
  the composer has no recipient, and the capture STOPS at the open picker; no GIF is chosen.
  Escape closes it. RECORD the picker's structure and whether choosing inserts or dispatches.
  LOADS 1.
- **C6 -- the per-message menu on his OWN message** (`M M11`, `M M48`). PAGE a READ conversation
  he names whose last message is his, under 60 minutes old. PRESS the per-message options control
  on that message (hover-revealed). WHY THE PRESS CANNOT SEND a menu trigger outside the form; the
  items are read and none is pressed; Escape closes. RECORD the item labels. LOADS 2 (guarded open).
- **C7 -- where the video-meeting control lives** (`M M20`). First the `M M10` preview's
  `footer_actions`: if a conversation draws `video_meeting`, that is the measurement. If not, a
  page capture of the read conversation's footer. No press. LOADS 0 or 1.
- **C8 -- the folder menu: message requests, archived** (`M M7`, `M M8`, `M M9`, `M M28`). PAGE
  `/messaging/compose/`. PRESS the folder trigger reading `Focused`
  (`[data-test-messaging-inbox-filters__folder-pill]`, `aria-expanded=false`). WHY THE PRESS
  CANNOT SEND a dropdown trigger outside the form; items read, none pressed; Escape closes.
  RECORD the folder items and that `li.msg-s-message-list__event` stays 0. LOADS 1.
- **C9 -- a conversation's options menu** (`M M22`, `M M27`, `M M29`, `M M31`). PAGE
  `/messaging/compose/`. PRESS one READ row's `button.msg-thread-actions__control`
  (`aria-expanded=false`). WHY THE PRESS CANNOT SEND a menu trigger outside the form; its
  `.msg-thread-actions__dropdown-options--inbox-shortcuts` items are read and none pressed; Escape
  closes; the count of `li.msg-s-message-list__event` is re-read and must still be 0, proving no
  conversation opened. RECORD the item labels. LOADS 1.
- **C10 -- the star's ON label** (`M M30`). PAGE a READ conversation he has ALREADY STARRED in
  LinkedIn himself, id HE NAMES. ELEMENT `button.msg-thread__star-icon`: `aria-label` and
  `aria-pressed`. WHY SAFE no press; read conversation. LOADS 2 (guarded open).
