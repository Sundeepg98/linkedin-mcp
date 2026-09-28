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
- 02:05 -- the corpus-wide guards run over `5eadfe7`: two red, both from this lane -- the
  navigation-derivation guard (a defect, fixed in `dd3d441`; section 6) and the timings table
  (this lane's two new test files; section 8.3). The census cells, the write-class dispositions
  and this record's R2 table written.
- 02:13 -- the impact gate's plan against `9c219c8`: 174 of 236 test files (74%), so it WIDENED
  TO THE FULL SUITE. As the brief orders, the full suite did not run here; the 174 and the
  corpus-wide floor -- 179 files -- ran over `899b24b` instead (section 8.2).
- 02:25 -- a probe of the captures found the defect in section 3.3: LinkedIn's global search is
  a combobox on every page. The fix was written in the scratchpad and applied only after the
  running gate finished, so that gate's result stays attributable to `899b24b`.
- 02:31 -- ten mutations, ten kills (section 8.2).
- 03:30 -- the 179-file gate over `899b24b` finished: 51 failed, 7705 passed. 29 are the pin
  moves of section 7, 19 were harness rows this lane's new write was missing, and 3 were defects
  in this lane's own content (section 8.2).
- 03:48 -- `536300d`: section 3.3's fix, the send gate's words check, the closed `accept` token,
  the harness rows, the landing guard's name match and the two census notes out of donor cells.
- 04:07 -- the final gate over `536300d` (section 8.2); this record's sections 3.3, 7 and 8,
  the `N 4` note, and `_audit/INSTRUMENTS.md` 69.5 to 69.8 written.

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
overlay renders rows is unmeasured (capture spec C4, in the Capture queue).

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
His own reply box is the one place page text is read into this process: the send gate and the
NOT-SENT check read the box -- his words, typed from his grant -- to compare them with the grant,
and keep a boolean and two lengths.

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
   `threads.reply_send_gate`: Send enabled, box not empty, still no recipient box, and the box
   holding EXACTLY his words. A box that changed them as they were typed -- an autocorrect, an
   emoji substitution, a mention picked up -- refuses as `5_words_not_exact`, keeping two lengths
   and no text, because a message cannot be taken back. Only then is Send pressed.
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

**MEASURED 2026-09-27 (section "The name-aimed debts", K.3):** the read boundary ADMITS the
compose-by-identifier address -- `readonly._ALLOWED_URL_PATTERNS` has carried it since 2026-09-03,
and `readonly.assert_read_url` admits it. The paragraph above read a morning state of that day.
What stands is the rest of it: the address takes a member id and no link, and the OBSERVING problem
is exactly as stated -- no instrument has ever seen a committed recipient.

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

### 3.3 THE DEFECT THE FIRST BUILD SHIPPED WITH -- LinkedIn's search box is a combobox on every page

Found after `899b24b` by a probe of the two captures, before any live use, and fixed in
`536300d`. `threads.RECIPIENT_BOX_SELECTOR` was `[role="combobox"]`, on the argument that a
conversation has nobody to choose. LinkedIn's GLOBAL SEARCH input is a `role=combobox` on every
page:

    [role=combobox], composer capture                 2   the global search, and the
                                                          composer's own typeahead
    [role=combobox], /messaging/ capture              1   the global search alone
    ... of those inside any form.msg-form             0   on both
    the global search inside <main>                   no  on both

So every real conversation would have counted one recipient box, `reply_state` would have
answered UNKNOWN ("not a conversation's reply surface"), and `linkedin_send_reply` could never
have typed a word. It failed CLOSED, so nothing unsafe could follow, and no test saw it: both
synthetic fixtures had been cut to the messaging region and drew no global navigation, so the one
element that breaks the selector was absent from every world the tests built. RED REPRODUCTION,
in a scratch copy of the tree at `899b24b` -- a commit on this lane's branch that does not resolve
on `master` until the branch merges; its subject is "send_reply: the same words from the other
side are not his send -- the authorship condition gets its own test" -- drawing the global
search into the thread fixture and
changing nothing else fails 17 of the 63 tests in `tests/test_send_reply.py` and
`tests/test_messaging_threads.py`.

**THE FIX WAS MEASURED BEFORE IT WAS WRITTEN.** On both captures a single `<main>`
(`main#main.scaffold-layout__list-detail.msg__list-detail`) holds the list, the open conversation,
the composer's form and the header; the messaging overlay sits outside it. Every conversation
selector is now scoped to `<main>`, and the recipient box is named by its own component,
`main .msg-connections-typeahead [role="combobox"]` or
`main input.msg-connections-typeahead__search-field`. Each of the 17 selectors was counted in its
old spelling and its scoped one on both captures: **no count moved except the recipient box** --
composer 2 -> 1 (the search dropped, the typeahead kept), `/messaging/` 1 -> 0.

**ONE EXCEPTION, ON PURPOSE: RECEIPT EVIDENCE STAYS PAGE-WIDE.** "Did loading this page display
anybody's conversation?" is not a question about `<main>`: the overlay can hold an open
conversation bubble outside it, and a list page that draws one has displayed a conversation,
whoever opened it. So the list's evidence (`EVIDENCE_EVENT_SELECTOR`,
`EVIDENCE_ACTIVE_ROW_SELECTOR`) counts anywhere on the page, and everything that AIMS -- what this
conversation holds, what a reply would type into -- counts inside `<main>`.

The fixtures now draw the global search outside `<main>` (and the composer's recipient box in its
measured shape, named by a `<label for>` rather than an aria-label), and four tests hold the
line: the global search is a combobox and not a recipient box (counts `(1, 0)` on the thread,
`(2, 1)` with the typeahead drawn); the composer's typeahead IS one, so the composer reads as not
a conversation; an overlay bubble outside `<main>` -- a form, a draft and a message of its own --
is not this conversation (3 messages, one empty editor, reply box EMPTY); and the same bubble on
the list page refuses the guard, opt-in or not. Mutations M12 to M14 (instrument register 69.6)
undo each piece, and each of those tests fails.

**A FINDING NEXT DOOR, RAISED AND NOT CHANGED.** `dom.read_thread_reply_surface`, which
`linkedin_open_messaging` returns as `reply_surface`, counts recipient boxes as
`[aria-label="Enter message recipients"]`. On the composer capture that box is named by a
`<label for>`, not an aria-label: the role-and-name selector the send gate uses finds 1, the
aria-label selector 0. So that reader's zero -- which its caller's comment calls "the finding
rather than a formality" -- is also zero on the composer, where a recipient box IS drawn, and
cannot tell a conversation from the composer. It is not this lane's reader (dom.py was left
untouched); `threads.read_thread`'s count is the one that can fail, and does, on the composer.

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
| `N 4` invite from a search result | BLOCKED | BLOCKED-SEARCH-FIRES-NOTHING | the people-search admission binds that nothing is fired from that surface, and a result row's Connect can send with no dialog: a ruling first, then a CALLER-SUPPLIED profile identity (lane S's readers; not used here). THE CALLER-SUPPLIED ROUTE ALONE WAS CHECKED: acting on a profile he names means loading that member's `/in/<slug>/`, which the read boundary refuses (re-measured), and `writes.PERMANENTLY_FORBIDDEN` prices a stranger's profile load as an emission on them; `linkedin_send_invitation` aims only at the rail on his own profile. Each route needs its own ruling |
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

**`M M7` AND `M M27` CARRY NO CENSUS NOTE, ON PURPOSE.** Each is the donor of a `same` row --
`M M8` resolves to `M M7`'s cell and `M M28` to `M M27`'s -- so a note written into either cell
becomes the argument of the row beneath it. The first version put this lane's notes there, and
the pointer-graph guard showed `M M8` and `M M28` inheriting a class that belongs to a different
capability (section 8.2). Their class lives in `_audit/_census/write-classes.tsv` and the table
above.

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
- **Only the words he confirmed can be sent.** The grant binds the thread AND the exact words;
  after the fill the send gate re-reads the box and refuses unless it holds exactly those words
  (`tests/test_send_reply.py::test_send_is_not_pressed_when_the_box_holds_other_words_than_his`;
  mutation M11 removes the check and the test fails). `text` is a REQUIRED argument of the gate,
  so a caller that forgets it raises rather than skipping the check.
- **Error fields carry a type or a composed reason.** Every `except` in `threads.py` records
  `type(exc).__name__`; every refusal is built from counts and closed tokens; a landing is
  described through `landing.withheld`, never quoted. `_send_gate` and the other existing gates
  (lane G's) are untouched: the reply has its own gate, `threads.reply_send_gate`.
- **Nothing third-party is returned.** No message body, correspondent's name or thread id leaves
  any reader. The two named exceptions: `include_names` on the list (his own inbox, opt-in, as
  `linkedin_open_messaging` already offered) and the reply preview's `who_this_would_reach`,
  asserted absent from `grant.preview`, the grant's target and every receipt.

## 7. EXPECTED PIN MOVES -- not re-pinned here, as the brief orders

Every line below was MEASURED red by a gate on this branch (section 8.2), not predicted, and each
names the file that holds the pin and the move it needs. None was edited here. Where a pin is a
recorded DECISION rather than a count, the decision is taken below and only the typing is left.

**The census.** `scripts/census_completion.py --check`, over `899b24b`:

    adjudicated            434 -> 437
    b1_no_ruling            15 ->  16     M M49
    b1_standing             10 ->  12     M M10, M M17 (OPERATOR-NAMES-THE-TARGET)
    b3_admitted             40 ->  39     M M49: it left bucket 3, where its address was admitted
    b3_blocked_on_nothing    8 ->   7     M M49: ... and blocked on nothing
    delivered_broad        100 -> 103
    gap                    270 -> 267
    gap_read                66 ->  65     M M49
    gap_write              150 -> 148     M M10, M M17
    unfired                 25 ->  28
    PINNED_B1_ROWS         + M M10 and M M17 on OPERATOR-NAMES-THE-TARGET, + M M49 on no ruling

(The two `b3_` lines were added when the check was re-run over `899b24b`; the first draft of
this table listed eight of the ten figures it names.) `scripts/count_census_states.py --expect
J=54,P=54,M=74,N=85` MATCHES at 267 (messaging 77 -> 74; stated rows 704, unchanged;
`pin_census_rows` no drift). Two tests carry the same movement:
`tests/test_ruling_holds.py` (PINNED_B1_ROWS; its direction-flip plant now picks `M M10`, the first
COVERED-UNFIRED write row in walk order, and passes once `M M10` is pinned) and
`tests/test_triage_instrument.py` (the messaging slice's split, 77 `{R 10, W 65, R+W 2}` -> 74
`{R 9, W 63, R+W 2}`, and the report that quotes it).

**The tool surface** -- `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py`
(PINNED_TOOL_SURFACE), `tests/test_server_surface.py`, `tests/test_every_tool_is_on_the_surface.py`:

    tools                     51 -> 54    + linkedin_list_conversations, linkedin_open_thread
                                            (reads), linkedin_send_reply (a write)
    read / write split     38 / 13 -> 40 / 14
    pinned parameters         69 -> 76    + include_names; + thread_id, allow_unread;
                                            + thread_id, text, confirm_token; and
                                            linkedin_open_messaging + allow_unread

**The write surface** (PERFORMABLE 13 -> 14, SANCTIONED_WRITES 14 -> 15, both + `send_reply`):

| file | pin | move |
|---|---|---|
| `tests/test_server_surface.py` | `SANCTIONED_WRITE_TOOLS` and the two sets asserted equal to it; `DOCSTRING_WRITE_TOOLS` | + `linkedin_send_reply` |
| same | server_info's two PERFORMABLE lists | + `send_reply` |
| same | `performable_and_irreversible`, typed by hand ("a sixth arriving is a decision") | + `send_reply`. DECIDED HERE: irreversible, as `send_message` is -- a message cannot be taken back through this server |
| same | the instructions must say `fourteen write` and name `linkedin_send_reply` (the number-words map now reaches 14) | the server's instructions text |
| `tests/test_writes.py` | the sanctioned set; `_UNMEASURED_REVERSIBILITY`; `REVERSIBILITY_CLASS`, `REVERSIBILITY_MEASURED` | + `send_reply`; `"STILL-UNKNOWN"`; `False` |
| `tests/test_writes_nine.py` | the actions whose `reversible_by` leans on `delete_or_withdraw_anything` | + `send_reply`; and that entry's note in `writes.PERMANENTLY_FORBIDDEN` says FIVE ("an application, a post, a comment, an invitation and a message") -- six, with a reply |
| `tests/test_receipt_names_its_own_action.py` | the acknowledged PERFORMABLE count | 13 -> 14. The acknowledgement it asks for was DONE here: `send_reply`'s rows were read, its `_VERIFIED_FROM` row holds no owned phrase, and "LinkedIn messages" was re-derived with it as a second owner |
| `tests/test_preview_state_and_click_state.py` | `len(PERFORMABLE)`, `len(REACHED)` | 13 -> 14 each; `send_reply` is now REACHED over the thread fixture |

**Prose counts** -- `tests/test_the_other_two_count_claims_are_pinned_too.py` (README's headline
and module listing: fifty-four) and `tests/test_prose_that_makes_a_claim.py` (the server docstring:
"fifty-one tools, thirteen of which write" -> fifty-four and fourteen; the sanctioned total,
fifteen).

**Derived baselines**, each written by its own module at merge: `tests/reader_leak_baseline.json`
(the new readers -- driven only since the fix commit repaired the harness, section 8.2),
`tests/tool_envelope_baseline.json` (the three tools), `tests/landing_interpolation_baseline.json`
(two new sites, both WITHHELD by measurement: `threads.off_thread_result` and
`writes._assert_landed_on_target`), and
`scripts/ci_shard_timings.json`, which prices 157 test files and falls under two thirds of 236
because this lane added two (section 8.3).

## 8. COMMITS, GATES, AND WHAT DID NOT RUN

### 8.1 Commits -- on `worktree-agent-a6bb3cc0961290132`, none pushed, no AI attribution in any

| commit | what |
|---|---|
| `5eadfe7` | the build: `linkedin_server/threads.py`; spec `send_reply` and its arms in `writes.py`; three tools and the guard in front of `linkedin_open_messaging` in `server.py`; `send_message`'s in-place read-back; the checker's R2 rule; two synthetic fixtures; the tests |
| `dd3d441` | this record, the census cells, the 23 R2 and 9 R3 dispositions, section 69, the generated indexes; and the navigation-derivation fix (section 6) |
| `899b24b` | the reply verdict's authorship condition gets its own test |
| `536300d` | section 3.3's fix (every conversation selector scoped to `<main>`, the recipient box named by its component, receipt evidence page-wide, the fixtures drawing the global search); the send gate's words check (section 3); the closed `accept` token; the harness rows the new write was missing; the landing guard's name match; the two census notes out of donor cells (8.2); five tests |
| the commit carrying this section | sections 3.3, 5's last paragraph, 7 and 8, the status log, the `N 4` note, `_audit/INSTRUMENTS.md` 69.5 to 69.8, and the generated indexes |

### 8.2 Gates run

1. **The lane's own tests at the build** (`5eadfe7`): the three new or changed test files, 39 + 41
   passed, on a box running five other lanes' suites.
2. **The corpus-wide guards over `5eadfe7`**: two red, both from this lane. The
   navigation-derivation guard convicted `observe` (section 6) -- fixed in `dd3d441`. The timings
   guard went under two thirds because this lane added two test files (8.3).
3. **The impact gate's plan**, `scripts/impact_gate.py --against 9c219c8 --plan-only`: 174 of
   236 test files (74%), at or above its 45% line, so it WIDENED TO THE FULL SUITE. Per the brief
   the full suite was NOT run; the 174 plus the corpus-wide floor -- 179 files -- ran instead,
   over `899b24b`, `-n 3 --dist loadfile`:

   **51 failed, 7705 passed, 4 skipped, 1 xfailed, in 4295 s** (72 minutes; five other lanes'
   suites shared the box). Every red was read and put in one of three classes:

   - **29 are the pin moves section 7 lists**: the tool surface (4), the write surface (14),
     prose counts (4), the census (3), derived baselines (3), the timings table (1). Left for
     the merge by the brief's order.
   - **19 were harness rows this lane's new write was missing, added in `536300d`.** The worst
     of them was silent in effect: `tests/refusinggrant.py` had no synthetic target for
     `thread_and_text`, and its KeyError stopped five writes readers -- `perform`,
     `_live_control`, `_verify_after`, `_recipient_gate`, `_typeahead_gate` -- being driven for
     ANY spec, so the page-string guard certified less than its baseline says (5, and 3 twins in
     `tests/test_the_harness_grant_cannot_authorise_a_write.py`). The rest:
     `tests/test_writes_nine.py`'s clean component for `thread` (8), the per-kind shape in
     `tests/test_a_performable_action_can_reach_its_control.py` (2), and `send_reply` as a second
     owner of "LinkedIn messages" in `tests/test_receipt_names_its_own_action.py` (1).
     `send_reply` also entered the preview/click-state ledger's `REACHED`, over the thread
     fixture; that file stays red only on its two count pins.
   - **3 were defects in this lane's own content, fixed in `536300d`.** The landing guard matched
     `server.py`'s `landed_reading` by its NAME; the value is `read_thread`'s counts and an
     exception type name, and it was renamed rather than ruled, because that guard rules per
     function and a ruling would pre-excuse any future site in `linkedin_open_messaging` (1). And
     the pointer-graph guard (2): the R3 notes this lane had appended to `M M7` and `M M27` were
     inherited, through `same`, by `M M8` and `M M28`, rows about other capabilities (section 5).

   Reading the readers the repaired harness now drives turned up one thing the guard could not
   see: `read_thread` returned each file input's `accept` attribute lowercased and cut to an
   alphabet -- still a page string. The guard's plant is matched as a case-sensitive substring
   (`tests/plantedpage.py`), so a lowercased copy with its space removed reads CLEAN; the
   reader passed for that reason and no other. It is a closed token now (`images`,
   `images_and_documents`, `any_file`, `unrecognised`).

4. **The census instruments over `899b24b`**: `census_completion --check` exits 1 on exactly
   the ten pinned figures and three bucket-1 rows section 7 lists (the two `b3_` figures were
   added to section 7 by this run) and nothing else; `count_census_states --expect
   J=54,P=54,M=74,N=85` MATCH at 267; `check_read_addresses` GREEN, 65 of 65 bucket-3 rows;
   `check_write_classes` GREEN, 151 lines (R1 11, R2 23, R3 117); `ruling_holds` GREEN (1 hold, 3
   lifted, 1 release); `pin_census_rows --check` no drift, 704 rows. The three generated files at
   a fixed point: `build_audit_index --check`, `build_rulings_index --check`,
   `build_blocker_map --check`, each exit 0.
5. **Ten mutations at `899b24b`, ten kills** (instrument register 69.6; `899b24b` does not resolve
   on `master` until this lane's branch merges -- its subject is in 3.3), each applied alone to a
   scratch copy of the tree and each failing its named test at the assertion named for it; the
   unmutated copy passed all ten.
6. **The defect of section 3.3, reproduced red and then fixed in a scratch copy first.** Red: the
   fixture change alone, under the shipped selector, failed 17 of 63 lane tests. Fixed, in the
   copy: 86 of 86 across the three lane test files. With the words check added, the lane files
   and five source guards: 875 passed, 6 failed -- all six the harness gap of item 3, seen there
   first. Four more mutations over the fix, four kills: the words check removed (M11), the
   recipient box back to any combobox (M12), the receipt evidence scoped to `<main>` (M13), the
   conversation's messages unscoped (M14). After the harness rows, in the worktree, the five
   harness files: 266 passed, 3 failed, all three pins.
7. **The final gate over `536300d`.** The analyser's plan for the delta, `--against 899b24b`,
   selected 191 of 236 test files (81%) and widened again, so the full suite was again not run.
   What ran is what the change can reach, read off the change itself -- every test file the
   commit edited, every file that was red over `899b24b` for a reason the commit addressed, every
   module importing an edited test module or `tests/refusinggrant.py` -- plus the 17-file
   corpus-wide floor: **24 failed, 3957 passed, 3 skipped, 1 xfailed, in
   915 s**, over 40 files (23 reached, 17 floor). All 24 are pins section 7 lists, each red over
   `899b24b` for the same reason; the 19 harness rows and the 3 defects of item 3 are green. The
   five pin tests red over `899b24b` that lie outside these 40 files -- two in the tool-surface
   pin file, one in `tests/test_every_tool_is_on_the_surface.py`, two in
   `tests/test_prose_that_makes_a_claim.py` -- test counts the fix did not move.

   The page-string guard's shrink test stops at its FIRST assertion, so its whole delta was
   measured separately: 133 readers live against 126 in the baseline; 7 appeared, all seven
   CLEAN (the six `threads` readers and `writes._read_thread_reply_box`); none vanished; none
   regressed; and three moved the safe way, `returns_text` -> `clean` (`writes._verify_after`,
   `writes._read_follow_state`, `dom.read_follow_control`). And the harness's own control,
   `scripts/_check_the_refusing_grant_can_fail.py`, PASS on all five sections, driving fifteen
   sanctioned actions with `send_reply` among them.

### 8.3 NOT run, and what that leaves open

- **THE FULL SUITE, locally -- by the brief's order.** The impact gate widened to it; the 57 test
  files outside the 179 never ran on this branch. It runs on CI after merge.
- **CI.** Nothing was pushed.
- **LIVE.** Nothing. Every row the Live queue names is unfired, and the two derived shapes the
  first live preview settles -- that a conversation draws the composer's `msg-form`, and that his
  own messages lack `--other` -- are still derived.
- **A SECOND RUN OF THE WIDENED SELECTION, OVER THE FIX.** The fix commit was gated by what it
  can reach and the corpus-wide floor (8.2, item 7), not by the 191 files the analyser selected:
  it couples `threads.py` to every importer of `writes.py`, which is nearly the whole suite, while
  the change is selector strings, one list reader's evidence lines, one gate's words check and its
  one caller, one closed token, harness rows, one renamed local and census notes. The files that
  selection holds and item 7 did not run were last run over `899b24b`.

RAISED FOR THEIR OWNERS, NOT CHANGED HERE:

- **The named-cost detector** (`tests/test_a_named_cost_names_a_tool_that_can_incur_it.py`)
  cannot resolve navigation made through `threads.COMPOSE_URL` or `threads.thread_url(...)`, so
  it does not see that `linkedin_list_conversations`, `linkedin_open_thread` and
  `linkedin_send_reply` load messaging. It stays green by not seeing them -- a blind spot, not a
  pass. `known_side_effects`' "Only ... can incur this" sentence was deliberately not edited.
- **The timings table.** `scripts/ci_shard_timings.json` prices 157 test files; this lane's two
  new files take the suite to 236 and the coverage under two thirds, so
  `tests/test_ci_shard.py::test_the_timings_table_still_prices_most_of_the_suite` is red here.
  The table is written only from a CI junit with provenance (`ci_shard.py --write-timings ...
  --label`), so it is not hand-edited: regenerate it from the first CI run after merge.
- **Three derived baselines** -- `tests/tool_envelope_baseline.json`,
  `tests/reader_leak_baseline.json` and `tests/landing_interpolation_baseline.json` -- need
  entries for the three new tools, the new readers and two WITHHELD sites, written by each
  module's own writer at merge (section 7).
- **`dom.read_thread_reply_surface`'s `recipient_boxes`** counts an aria-label the composer's
  recipient box does not carry, so its zero cannot tell a conversation from the composer
  (section 3.3).
- **`writes.perform`'s `click_error`** is built as `f"{type(exc).__name__}: {exc}"`, predating
  this lane (the same line is in `9c219c8`), and every write's receipt carries it, `send_reply`'s
  included. A library's own exception text is publishable under ERROR-MESSAGE-RULED-AT-THE-RAISE,
  but a Playwright click error can quote the element it failed on, and that is a value the page
  chose. Lane G's territory; not touched here.

THE DOCUMENTATION DELTA. The commit carrying this section is gated after it is written --
by the corpus-wide floor, the census instruments, the pointer-graph guard and the three
generators at a fixed point. A record cannot carry the result of a gate that runs over it;
that result is in the lane's closing message.

## Integration 2026-09-24

THE ORDER (the orchestrator's, sampled at 05:10) was obeyed only after the disk agreed with it: this
lane's head was `f3c862a` and clean, and local `master` was `ff98a7f` -- 30 commits past the base by
`git rev-list --count 9c219c8..master` (the order said 31) -- carrying lanes R, G and S and rulings
batch 3. `master` was re-read before each commit of the first merge below and had not moved.
It moved three times afterwards -- to `9b9a4d0`, `603f4d3` and `66aaa95` -- and the second
and third merge subsections say what each brought.
(This sentence said "before each commit below" until the third merge was recorded.)

### The merge and its conflicts

`123186c` merges `ff98a7f` (parents `f3c862a`, `ff98a7f`). Seven paths conflicted, and no line was
changed on both sides:

| path | blocks | resolution |
|---|---|---|
| `_audit/_census/messaging-and-content.md` | 5 | ROW BY ROW against the base, each row taken from the side that changed it: 29 rows in the blocks, 17 this lane's cells and 12 lane R's returns (`M3`, `M5`, `M19`, `M23`, `M24`, `M39` to `M42`, `M46`, `M50`, `M51`) |
| `_audit/_census/network.md` | 3 | the same: 13 rows, 6 this lane's (`4`, `5`, `6`, `160`, `166`, `167`) and 7 lane R's (`3`, `158`, `159`, `163`, `164`, `165`, `168`) |
| `_audit/_census/write-classes.tsv` | 1 | this lane's `N A11` to `A13` dispositions, then lane R's 174 appended lines; checked with `scripts/check_write_classes.py`: GREEN, 325 lines (R1 16, R2 35, R3 274) |
| `_audit/INSTRUMENTS.md` | 1 | both sides appended: master's 66 and 67, then this lane's 69, with the register's `---` separator |
| `_audit/INDEX.md`, `_audit/RULINGS.md`, `_audit/_census/blocker-map.tsv` | generated | master's copies taken, every other path staged first, all three regenerated to a fixed point (two write rounds, three `--check` exit 0) |

Checked after the resolution: each census file differs from `master` only in this lane's rows, and
from this lane's head only in master's. Auto-merged and read: `server.py` (lane S's five
people-search parameters and this lane's three tools sit apart), `writes.py` (lane G changed one
line, `_recipient_gate`'s error field; this lane's hunks are elsewhere), `check_write_classes.py`
(lane R's range-id row form beside this lane's R2 rule), `test_write_classes.py`,
`test_server_surface.py`, and `_audit/_census/read-addresses.tsv`, which `check_read_addresses`
re-drove GREEN, 93 of 93: lane R's returned read rows in, `M M49` out.

LANE R'S RETURNED ROWS ARE LANE R'S. Twelve of its lines are R2 -- `M M3`, `M M5`, `M M19`,
`M M23`, `M M40`, `M M51`, `M C66`, `N 3`, `N 15`, `N 18`, `N 156`, `N 158` -- and this lane classed
none of them; they stay classify-only. The table's header said "every other R2 line names its
blocker or capture", which the merge made false, and now says which 21 this lane classed.

### Every pin, re-derived on the merged tree

Section 7 was written as deltas from `9c219c8`. Each figure below is master's pin moved by this
lane's rows, and every one was read off the merged tree. Committed in `7d13af2`.

- `scripts/census_completion.py`: adjudicated 194 -> 197, delivered_broad 105 -> 108, unfired
  30 -> 33, gap 510 -> 507, gap_read 94 -> 93, gap_write 324 -> 322, b3_admitted 40 -> 39,
  b3_blocked_on_nothing 2 -> 1 (`P K1` is the one left), b1_standing 10 -> 12, b1_no_ruling
  20 -> 21; `PINNED_B1_ROWS` gains `M M10` and `M M17` (OPERATOR-NAMES-THE-TARGET) and `M M49` (no
  ruling). `--check` exit 0. `count_census_states --expect J=92,P=152,M=114,N=149` MATCH at 507.
- The triage split, re-derived with master's `scripts/triage_messaging_gap_rows.py`: 117
  `{R 13, W 101, R+W 3}` -> 114 `{R 12, W 99, R+W 3}`; RETURNED-OUTSIDE-LEDGER stays 14. Y2's
  bucket had not landed on `master` at the merge.
- The tool surface: 51 -> 54 tools, 74 -> 81 parameters (lane S's five included).
- The write surface, in every list that types it: `SANCTIONED_WRITE_TOOLS` (which is also the
  docstring exemption), `EXPECTED_TOOLS`, both `server_info` lists, `performable_and_irreversible`
  (`send_reply` added by hand: irreversible, as `send_message` is), the reversibility tables
  (STILL-UNKNOWN, unmeasured), the destruction-refusal list and `writes.py`'s FIVE -> SIX note, and
  the receipt and preview-state counts, 13 -> 14.
- Prose: the README headline "Fifty-four tools ship. Forty read. Fourteen write." and its module
  listing, `server.py`'s docstring (headline, split, sum, the action with no tool),
  `__init__.py`, and `test_server_surface.py`'s own first line.
- THE INSTRUCTIONS a client answers from: FOURTEEN WRITE naming `linkedin_send_reply`, and a
  paragraph for the reply. Two claims this lane had made false are corrected in place, quoted:
  `send_message` "can never report SENT", and "Each call loads exactly one page".
- NOT TOUCHED, by the order: `scripts/ci_shard_timings.json`.
  `tests/test_ci_shard.py::test_the_timings_table_still_prices_most_of_the_suite` reads 157 of
  237 and stays red until the table is regenerated after the train.

### The three baselines, each by its own writer (`python -m tests.<module> --write-baseline`)

- `tests/reader_leak_baseline.json`: 126 -> 133 readers. Seven appeared, all CLEAN (the six
  `threads` readers and `writes._read_thread_reply_box`). Three verdicts moved `returns_text` ->
  `clean` -- `dom.read_follow_control`, `writes._read_follow_state`, `writes._verify_after` -- and
  NOT because of this lane: a scratch extract of `master` `ff98a7f`, driven reader by reader, reads
  the same three clean. The committed baseline was stale, because the shrink test flags only a
  regression.
- `tests/tool_envelope_baseline.json`: `linkedin_list_conversations` CLEAN; `linkedin_open_thread`
  and `linkedin_send_reply` NOT DRIVEN ("never read the page"). Every tool that takes an id and
  every write reads the same, because the harness passes one synthetic string, which is no thread
  id, and a write refuses at the flag. The lane's own tests drive both over the fixtures.
- `tests/landing_interpolation_baseline.json`: two new sites, both WITHHELD by measurement
  (`threads.off_thread_result`, `writes._assert_landed_on_target`).

### Item 3: `dom.read_thread_reply_surface`, in this lane's domain now

RED FIRST: `tests/test_thread_reply_surface.py` gained the composer in its MEASURED shape (a
`<label for>`, the typeahead's class), and on the unfixed reader it read 0 against the expected
1. The reader now counts `dom.compose_recipient_selector()` -- the role and the accessible name the
send gate types into -- and a second new test holds the other side: LinkedIn's global search, a
combobox on every page, is not a recipient box. Committed in `346b78f`. Measured offline on both
captures after the fix: the composer reads 1 (the old aria-label selector 0), the `/messaging/`
conversation 0, and `threads.read_thread` agrees on both. The synthetic composer fixture's label
read "To", which no capture holds; it now carries the measured label text.

### Item 4: the named-cost reader sees the messaging tools

RED FIRST: a planted server source (never written into the package) reaches a messaging address
through a module constant (`threads.COMPOSE_URL`), a local bound to a helper that formats a module
template (`threads.thread_url`), and a write whose navigation is its spec's `url_template`
(`_write_tool("send_reply", ...)`). On the old reader it found none of the three. The reader now
resolves all three -- read by AST, never imported -- and its control, a write whose spec is a job
posting, stays unseen. On the real server it then saw four more tools load a messaging address:
`linkedin_list_conversations`, `linkedin_open_thread`, `linkedin_send_reply`, and
`linkedin_send_message` when a send is performed. `known_side_effects` and its README twin name them
in a second clause, "these also load a messaging address", open rather than closed and apart from
the "Only ... can incur this" clause whose cost is the root's. The recorded defect is unchanged:
exactly `linkedin_compose_fields`. The two copies are checked to name the same set, and every tool
the clause names is checked to exist and to navigate there.

OF THE ITEMS SECTION 8.3 RAISED, three are closed here (the named-cost reader, the baselines, the
dom reader), one waits for the train (the timings table), and one is still lane G's:
`writes.perform`'s `click_error` carries the exception's text.

### The second merge: master moved to `9b9a4d0` while this section was being written

After `fd485c2` was committed, local `master` read `9b9a4d0`: the live lane's merge (session 1 --
four rows proven live and `linkedin_own_item_link`, a read that presses) and a rulings commit.
The order says to integrate the then-current `master`, and lane S did the same when `master`
moved under it, so `9fbdef0` merges `9b9a4d0` (parents `fd485c2`, `9b9a4d0`). The figures in the
subsections above are the first merge's; this one moved them again.

Fourteen paths conflicted, and each was a count both sides moved or a note both sides wrote:

- `_audit/_census/messaging-and-content.md`: `M M47` and `M M48` this lane's alone. `M M33`,
  `M M43` and `M M49` changed on BOTH sides, and each was merged by its measured shape, verified
  before it was applied: the live lane PREPENDED a dated note to each note cell and this lane
  APPENDED one to `M M33` and `M M43`, so both notes stand where each side put them. On `M M49`
  this lane moved the state to COVERED-UNFIRED and put its note first, so the cell reads this
  lane's note, then the live lane's dated one ("not built, not fired ... no capture of that page
  exists"), then the original -- with one sentence joining them: a capture of that landing does
  exist, the 2026-09-20 one of section 1.4, of a sponsored conversation whose last message is
  theirs.
- The counts, measured on the merged registry: 55 tools, 85 parameters, 41 read, 14 write, 12
  sanctioned mutating calls (the live lane brought five). README, `__init__.py`, `server.py`'s
  docstring, the two surface tests and the tool pin each keep both sides' dated notes.
- `scripts/census_completion.py`: every pinned figure MEASURED on the merged tree, and each equals
  master's pin moved by this lane's three rows: adjudicated 197 -> 200, delivered_broad 108 ->
  111, delivered_strict 79 (the live lane's), unfired 29 -> 32, gap 507 -> 504, gap_read 91 -> 90,
  b3_admitted 37 -> 36, b1_no_ruling 19 -> 20; b1_standing 12, gap_write 322 and
  b3_blocked_on_nothing 1 as at the first merge. `--check` exit 0, no bucket-1 row off its pin.
- The triage split, re-derived with `scripts/triage_messaging_gap_rows.py`: 116 over the live
  lane -> 113 `{R 11, W 99, R+W 3}`; RETURNED-OUTSIDE-LEDGER 14.
- `tests/reader_leak_baseline.json` and `tests/tool_envelope_baseline.json`: both sides' new
  entries, then each regenerated by its own writer; the regeneration was byte-identical to the
  union. `tests/landing_interpolation_baseline.json` did not conflict and regenerated unchanged.
- `_audit/INDEX.md`, `_audit/RULINGS.md`, `_audit/_census/blocker-map.tsv`: master's copies, every
  other path staged first, regenerated to a fixed point.

### The third merge: master moved to `603f4d3`, then `66aaa95`, while the second was being checked

After `ad7254b`, local `master` read `603f4d3` -- lane L7's merge: `linkedin_mark_company_interest`,
a write (census `P I14`, COVERED-UNFIRED), and `linkedin_update_profile_field` pressing Save -- and,
by the time the cold re-check of `ad7254b` had finished, `66aaa95`, which fixed the two tests CI
failed on `603f4d3`. The merge was resolved in a scratch dry run first (`git merge-tree` of this
branch and `master`, each diff3 block resolved by its index with its content asserted), and the
real merge's index stages were then checked byte-identical to the blobs the dry run resolved.
`cb2457b` merges `66aaa95` (parents `ad7254b`, `66aaa95`). Sixteen paths conflicted; no census row
and no write-class line changed on both sides.

- THE CHANGES BOTH SIDES MADE IDENTICALLY, AND THE ORDINAL BOTH SIDES CLAIMED. Each lane made its
  own new write the fourteenth. Where both sides changed a line the SAME way, a three-way merge
  takes one copy without a conflict: `FOURTEEN WRITE` in the instructions and "FIFTEEN actions
  where this surface registers FOURTEEN write-shaped tools" merged clean and wrong, and the
  instruction-words map's `14` and the receipt and preview-state `== 14` conflicted only through
  their comments. Those were found by listing every line both sides added identically against
  `9b9a4d0` (21 files changed on both sides). Where each side wrote the same ordinal about a
  different action -- the instructions' paragraphs, the spec and `PERFORMABLE` comments, both
  hand-typed `server_info` lists -- a search for the ordinal found them. Each was moved by hand:
  fifteen write tools, sixteen sanctioned actions; `mark_company_interest` is the fourteenth,
  because it landed on `master` first, and `send_reply` the fifteenth. Section 3, written before
  either merge, still calls it the fourteenth, and sections 7 and 8 keep their pre-merge counts.
  (This read "Sections 3 and 8 ... still call it the fourteenth" until a cold re-check found the
  ordinal in section 3 only.)
- The counts, MEASURED on the merged registry: 56 tools, 87 parameters, 41 read, 15 write, 15
  performable, 16 sanctioned actions (`set_open_to_work` still has no tool), 12 sanctioned
  mutating calls -- lane L7's 53 and 80 plus this lane's three tools and seven parameters. README,
  `__init__.py`, `server.py`'s docstring and instructions, the two surface tests and the tool pin
  each keep both sides' dated notes.
- `scripts/check_write_classes.py`: the two lanes relaxed the same rule differently on the same
  day. Lane L7 let R3 carry a disposition and kept R2 classify-only; this lane let R2 and R3 both
  (WRITE-CLASS-B let R2 be built: `M M10` and `M M17` are `built:send_reply`, `M M47` is queued).
  The merge keeps the wider rule -- lane L7's R2 clause would convict three of this lane's lines --
  and lane L7's two R3 tests pass under it. The header in `tests/test_write_classes.py` that said
  R2 "is still classify-only" was made false by the merge and is corrected in place.
- `_audit/_census/write-classes.tsv`: merged row by row against the base, each line from the side
  that changed it -- 31 this lane's, 36 lane L7's (its profile-family rows, `N 114` and `N 176`),
  none changed on both -- and the preamble this lane's, which lane L7 had left as it was.
  `check_write_classes` GREEN, 325 lines.
- `scripts/census_completion.py`: every figure MEASURED on the merged tree, and each equals lane
  L7's pin moved by this lane's three rows: adjudicated 198 -> 201, delivered_broad 109 -> 112,
  unfired 30 -> 33, gap 506 -> 503, gap_write 323 -> 321, b1_standing 11 -> 13; delivered_strict
  79, gap_read 90, b3_admitted 36, b3_blocked_on_nothing 1 and b1_no_ruling 20 not moved by the
  merge, because lane L7 moved no read row. `--check` exit 0; bucket 1 reads 13 standing (`P I14`
  beside `M M10` and `M M17`) and 20 held by no ruling, of 33.
- The triage split, re-derived with `scripts/triage_messaging_gap_rows.py`: 113
  `{R 11, W 99, R+W 3}`, RETURNED-OUTSIDE-LEDGER 14 -- unchanged, because lane L7 moved no
  messaging row.
- `tests/test_gap_rows_on_refused_addresses.py`, one of the two tests `66aaa95` repaired, pins 60
  on `master`. Its script counts 55 on this lane's previous head, as on `9b9a4d0`, and 60 on the
  merged tree, where the test passes.
- `tests/reader_leak_baseline.json` and `tests/tool_envelope_baseline.json`: both sides' entries,
  then each regenerated by its own writer, byte-identical to the union.
  `tests/landing_interpolation_baseline.json` regenerated unchanged.
- `_audit/INSTRUMENTS.md`: both sides appended -- this lane's 69, then lane L7's 70.
- `_audit/INDEX.md`, `_audit/RULINGS.md`, `_audit/_census/blocker-map.tsv`: master's copies, every
  other path staged first, all three regenerated to a fixed point (two write rounds, three
  `--check` exit 0).

THE METHOD, FOR THE NEXT MERGE OF TWO LANES THAT EACH ADD A WRITE: a clean auto-merge of a count
is not evidence the count is right. Before trusting one, list the lines both sides added
identically against the merge base, and search both sides' additions for the ordinal each one
claimed; here those two searches found the sites this merge moved by hand. The dry-run scripts
(the merge-tree preview, the per-block resolver, the identical-line lister, the row merger) lived
in a scratch directory outside the repository and are declared disposable.

WHERE THE CHASE STOPS: `master` read `66aaa95` when this subsection was committed. If it has
moved again, this branch is one more merge behind it, and nothing here was measured against it.

### The fourth merge: master moved to `530227e`, then `1902fcb`, while the third was being gated

When the third merge was recorded, local `master` read `66aaa95`; minutes later it read `530227e`,
lane Y2's merge -- 43 capabilities the census never enumerated, admitted as GAP rows (704 -> 747
stated rows), `J 158` then COVERED-UNFIRED, the refused-address pin 60 -> 70, and its triage
bucket, which the order had said might land first -- and then `1902fcb`, a rulings commit (names
at runtime, their six mitigations, and the classes built behind the grant) that touches documents,
the rulings generator and the generated files only. (This said "documents and the rulings
generator only" until a cold re-check found eight lines of the generated blocker map in it.) `6d60867` merges `1902fcb` (parents `8d1cdf7`, `1902fcb`),
resolved in a scratch dry run first as the third was; the index stages were checked
byte-identical to the blobs the dry run resolved. Eight paths conflicted:

- `_audit/_census/messaging-and-content.md` and `_audit/_census/network.md`, row by row. Five rows
  changed on BOTH sides -- `M M1`, `M M14`, `M M18`, `M M29` and `N 4` -- and on each, both sides
  APPENDED a note to the last cell and changed nothing else, verified before it was applied: each
  cell now reads the base, then lane Y2's DRAWN note, then this lane's. Every other row came from
  the one side that changed it, lane Y2's eleven admitted messaging rows among them.
- `_audit/_census/write-classes.tsv`: row by row, no line changed on both sides -- lane Y2's
  fourteen admitted write rows and this lane's 31 lines kept. `check_write_classes` GREEN, 339
  lines, 16 R1 / 36 R2 / 287 R3, lane Y2's pin.
- `scripts/census_completion.py`: every figure MEASURED on the merged tree, and each equals lane
  Y2's pin moved by this lane's three rows: adjudicated 199 -> 202, delivered_broad 110 -> 113,
  unfired 31 -> 34, gap 548 -> 545, gap_read 104 -> 103, gap_write 337 -> 335, b3_admitted 42 ->
  41, b3_blocked_on_nothing 5 -> 4, b1_standing 11 -> 13, b1_no_ruling 20 -> 21. THE LAST MERGED
  CLEAN AND WRONG: both sides moved `b1_no_ruling` 19 -> 20, lane Y2 by `J 158` and this lane by
  `M M49`, and git keeps one copy of an identical change; the list of lines both sides added
  identically found it, as it found the third merge's. `--check` exit 0.
- `tests/test_triage_instrument.py`: lane Y2's 127 `{R 18, W 105, R+W 4}` and this lane's 113 are
  kept as history, and the split the merged tree's `scripts/triage_messaging_gap_rows.py` measures
  is pinned: 124 `{R 17, W 103, R+W 4}`.
- `_audit/INDEX.md`, `_audit/RULINGS.md`, `_audit/_census/blocker-map.tsv`: master's copies,
  every other path staged first, all three regenerated to a fixed point.
- Unconflicted, and measured: `count_census_states --expect J=107,P=160,M=124,N=154` MATCH at 545;
  `check_read_addresses` GREEN 103 of 103 (lane Y2's admitted read lines in, `M M49`'s out);
  `pin_census_rows` no drift at 747; the refused-address GAP rows 70, lane Y2's pin, so this
  lane's three built rows were none of the ten lane Y2 named.

THE NAMES-AT-RUNTIME RULINGS, READ AGAINST THIS LANE, and not acted on here -- an integration
merges rulings, it does not implement them. `linkedin_list_conversations` and
`linkedin_open_messaging` return participant names when `include_names` is passed; the names are
whitespace-normalised, and mitigation 2's other steps (control, zero-width and bidirectional
characters stripped, a length cap, marked as untrusted third-party text) are not yet applied to
them. And the same commit schedules `delete_or_withdraw_anything` to leave the forbidden list when
the delete path is built, at which point `send_reply`'s `reversible_by`, which cites it, is to be
re-read with the other five.

WHERE THE CHASE STOPS NOW: `master` read `1902fcb` when this subsection was committed.

### The fifth merge: master moved to `7d89b8d` while the fourth was being gated

`590a610` merges `7d89b8d` (parents `ba66c48`, `7d89b8d`): lane L7's follow-up --
`profile_editor.py` recognising the intro editor's two unnamed switches by structure, five lines
of `writes.py`, a synthetic fixture and its test, one `profile.md` note and one write-classes
line. Nothing conflicted; none of those lines is one this lane wrote. Measured on the merged tree
rather than assumed from the clean merge: 56 tools, 87 parameters, 15 write, 15 performable, 12
sanctioned mutating calls; the census instruments green with every figure on its pin (GAP 545,
339 write-class lines, 103 of 103 addresses, 747 rows, 66 pointers); the three baselines
regenerated by their own writers, byte-identical to the merged copies; the blocker map
regenerated after staging, because lane L7's record text moves the locator's candidate counts.

WHERE THE CHASE STOPS: `master` read `7d89b8d` when this subsection was committed. Five merges
in, every one of them the then-current `master`; the next lane to land puts this branch one
merge behind again.

### Integration commits

| commit | what |
|---|---|
| `123186c` | the merge of `master` `ff98a7f`; conflicts as above; generated files at a fixed point |
| `346b78f` | item 3, red first |
| `7d13af2` | every pin, the baselines, item 4 (red first), the instructions, the tsv header |
| `fd485c2` | this section as first written, `_audit/INSTRUMENTS.md` 69.9 and 69.10, the generated files |
| `9fbdef0` | the merge of `master` `9b9a4d0`; conflicts as in the subsection above |
| `ad7254b` | the second merge's subsection, and the generated files |
| `cb2457b` | the merge of `master` `66aaa95` (lane L7's merge and its CI fix); conflicts as in the third merge's subsection |
| `afe9b1c` | the merge's dated notes name the master it merged, `66aaa95`; they said `603f4d3`, the commit the resolutions were first built against |
| `8d1cdf7` | the third merge's subsection, and the generated files |
| `6d60867` | the merge of `master` `1902fcb` (lane Y2's admission, then the names-at-runtime rulings); conflicts as in the fourth merge's subsection |
| `ba66c48` | the fourth merge's subsection; it moved no generated file (this row said it did, until a cold re-check read the commit) |
| `590a610` | the merge of `master` `7d89b8d` (lane L7's follow-up); clean |
| the commit carrying this line | the fifth merge's subsection; the generators, run after it was staged, moved no file |

### Gates run on the integrated branch

- The census instruments over `7d13af2`: `census_completion --check` exit 0 (every figure on its
  pin); `count_census_states` MATCH at 507; `check_read_addresses` GREEN 93 of 93;
  `check_write_classes` GREEN 325; `ruling_holds` GREEN; `pin_census_rows` no drift, 704;
  `measure_pointer_graph --check` PASS, 69 pointers.
- The pin and lane files (26), over the tree between `346b78f` and `7d13af2`, before the commit:
  1884 passed, 2 failed -- the timings table, and `test_server_surface.py`'s own headline, which
  was then corrected and passed.
- SEVENTEEN MUTATIONS, SEVENTEEN KILLS, over a scratch copy of `7d13af2`: the
  lane's fourteen, re-run on the merged tree, and three for the integration's new code --
  M15 the dom reader back on the aria-label, M16 the reader's write-spec branch dead, M17 its
  module-constant branch dead. The unmutated copy passed all sixteen named tests; each mutation
  failed its test at the assertion named for it; every file was restored byte for byte.
- The census instruments again over `9fbdef0`: `census_completion --check` exit 0;
  `count_census_states --expect J=92,P=151,M=113,N=148` MATCH at 504; `check_read_addresses`
  GREEN 90 of 90; `check_write_classes` GREEN 325; `ruling_holds` GREEN; `pin_census_rows` no
  drift, 704; `measure_pointer_graph --check` PASS, 67 pointers. The seventeen mutations were
  run again over a copy of `9fbdef0`: seventeen kills, every file restored byte for byte.
- The gate over `ad7254b` (the corpus-wide floor of 18 files and 31 lane and pin files): 4434
  passed, 1 xfailed, 0 failed. A cold re-check of `ad7254b` against a fourteen-item checklist
  passed thirteen items; the one it marked failed by its letter, a search of the added lines
  for path strings, found three uses of the bare word for a scratch directory and no path.
- THE THIRD MERGE, over the merge's own tree (`cb2457b`): the census instruments --
  `census_completion --check` exit 0; `count_census_states --expect J=92,P=150,M=113,N=148`
  MATCH at 503; `check_read_addresses` GREEN 90 of 90; `check_write_classes` GREEN 325;
  `ruling_holds` GREEN; `pin_census_rows` no drift, 704; `measure_pointer_graph --check` PASS,
  66 pointers. The identity sweep: PASS, 0 hits across 854 files; the pre-commit identity gate
  on the merge: 0 hits across 33 staged files. No added line against `master` or against this
  branch's previous head holds a non-ASCII byte.
- SEVENTEEN MUTATIONS over a copy of `cb2457b`: seventeen kills, each failing the test named for
  it; every anchor was found once, every file was restored byte for byte, and the unmutated copy
  passed all sixteen named tests.
- The gate over `cb2457b`, 94 test files -- the corpus-wide floor, the lane and pin files, the two
  tests CI failed on `603f4d3`, lane L7's two test files, and every test file that reads the
  census -- sharded over four workers by file: 5982 passed, 3 skipped (a symlink this platform
  will not create), 1 xfailed (the known defect whose strict marker holds it), 0 failed.
- The impact gate's plan, `--against ff98a7f`: 222 of 237 test files (94%), so it WIDENED TO THE
  FULL SUITE. By the order the full suite was NOT run locally; CI certifies at merge. Against
  `9b9a4d0`: 227 of 242. Against `66aaa95`: 229 of 244 (94%), widened the same way.
- The gate over `8d1cdf7` -- the corpus-wide floor, the pin and prose files, the files the
  dated-notes commit touched, and the document guards: 3409 passed, 0 failed.
- THE FOURTH MERGE, over the merge's own tree (`6d60867`): the census instruments --
  `census_completion --check` exit 0; `count_census_states --expect J=107,P=160,M=124,N=154`
  MATCH at 545; `check_read_addresses` GREEN 103 of 103; `check_write_classes` GREEN 339;
  `ruling_holds` GREEN; `pin_census_rows` no drift, 747; `measure_pointer_graph --check` PASS,
  66 pointers; and the triage script's 124 `{R 17, W 103, R+W 4}`. The identity sweep: PASS, 0
  hits across 857 files; the pre-commit identity gate on the merge: 0 hits across 32 staged
  files; no added line against `master` or against this branch's previous head holds a
  non-ASCII byte. Lane Y2 changed no module under `linkedin_server/`, so the gate after this
  merge is the census side -- the corpus-wide floor, every test file that reads the census,
  lane Y2's test files, the triage and pin tests -- and it runs over the commit carrying this
  section.
- The gate over `ba66c48` -- the fourth merge's census side: the corpus-wide floor, 71 test files
  that read the census, lane Y2's test files, the triage and pin tests; 82 files, sharded over
  four workers: 5590 passed, 3 skipped, 1 xfailed, 2 FAILED. Both failures are in
  `tests/test_click_is_not_its_own_evidence.py`, and both refused `1_no_listbox` where a listbox
  was expected to render. That file, re-run alone over the same commit: 30 passed, 1 xfailed.
  Read as a render-timing failure under load -- four workers beside other lanes' suites -- and
  not as a merge defect; that reading is an inference from two facts, that the same commit
  passes the file alone and that the merge changed nothing under `linkedin_server/`.
- A cold re-check of `ba66c48` against a ten-item checklist: all ten pass, the five rows both
  sides appended to among them, each read as base, lane Y2's note, then this lane's. It found
  the two wording slips corrected above.
- THE FIFTH MERGE, over the merge's own tree (`590a610`): the figures in its subsection, each
  measured; the pre-commit identity gate on the merge: 0 hits across 12 staged files; no added
  line against this branch's previous head holds a non-ASCII byte.
- The final gate over the commit carrying this section is reported in the lane's closing
  message: a record cannot carry the result of a gate that runs over it.

### NOT run

- The full suite, locally, by the order.
- CI: nothing was pushed.
- LIVE: nothing. The Live queue and Capture queue below are unchanged by the integration.

## Live queue

Every call below runs in a process the live lane owns, spaced by its own budget. Loads are page
loads; "HE NAMES" means OPERATOR-NAMES-THE-TARGET applies and nothing fires without it.

| row | call | target | loads | what banks it |
|---|---|---|---|---|
| `M M43` | `linkedin_list_conversations()` | none (own inbox, nothing opened) | 1 | COVERED-PROVEN when it returns rows with `opened_a_conversation.opened == false` and `rows_rendered >= 1`. Its `rows[].unread` and `unread_rendered` are also the reading capture C1 wants whenever a row is unread |
| `M M33` | `linkedin_open_messaging(message_filter="inmail")` | none (own inbox, read conversation) | 2, plus one pill press | COVERED-PROVEN when `receipt_guard.proceed` is true, `active_filter.activated` is true and `url_movement` is `filter_state`. If the guard refuses -- a rendered row reads unread -- it spends 1 load and banks nothing: he reads that conversation himself first, or passes `allow_unread=True` |
| `M M49` | `linkedin_open_messaging()`; if its `landed_conversation.read_indicator.state` is `not_applicable` (the last message there is theirs), `linkedin_open_thread(thread_id=<a read conversation whose last message is his>)` | none (own inbox, read conversation) for the first; HE NAMES a thread id for the second | 2, then 2 | COVERED-PROVEN when `read_indicator.state` is `not_drawn` or `drawn` -- and a `drawn` reading also turns the derived `--with-seen-receipt` marker into a measured one |
| `M M10` | `linkedin_send_reply(thread_id=<HE NAMES>, text=<HE NAMES>)`, he reads `who_this_would_reach`, then the same call with `confirm_token=<token>` within 120 s | HE NAMES the conversation and the exact words | 1 (preview), then 2 (act, and the fresh read-back) | COVERED-PROVEN when the receipt reads `performed: true, verified: true`. The preview alone also delivers capture C3(a) and C7's footer reading, as counts. A `send_gate.refused_condition` of `5_words_not_exact` sent NOTHING and is itself a finding: its two lengths say how the box changed his words |
| `M M17` | as `M M10`, with an emoji inside `text` | HE NAMES | 1, then 2 | COVERED-PROVEN on `performed: true`. If the box changes the emoji as it is typed, the send gate refuses BEFORE Send (`5_words_not_exact`) and nothing is sent; `unknown` after a send means the conversation drew it differently. Record either; do NOT retry |
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

## Follow-up: the named-person route

**THE ORDER** (the orchestrator, 2026-09-24 after the lane's merge at `96c1165`, restated on the
resume of 2026-09-27 13:25): ruling `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET` -- admit
`/in/<slug>/` for a CALLER-SUPPLIED slug, reachable only from inside an outward write, never by a
read and never for a measurement; build Connect and Message on it, each grant-gated, off by
default, aimed by a profile link or id and never a name, each reporting WHOM IT RESOLVED before
it acts (PEOPLE-DATA-MITIGATIONS item 6); build only against captured DOM and write an exact
NEEDS-CAPTURE spec for the rest; leave `include_names`' mitigation 2 to lane G's sanitiser
through a seam and a failing-until-adopted test. Disk at the resume matched the order: HEAD
`96c1165`, clean.

**WHAT SHIPPED, in one paragraph.** A second door in `readonly.py`, reachable from one function;
two writes, `linkedin_connect_from_profile` and `linkedin_message_from_profile`; a module,
`linkedin_server/named_profile.py`, holding the target parser, the landing veto, the verdicts,
the opened-conversation and send gates, and the one step that prints whom an act resolved to;
`linkedin_server/people_seam.py`, where lane G's record adopts every name lane L5 returns; and
two test files. A cold re-check refuted six claims of the first build and two warm ones found
ten more; every one is fixed except two that need a capture or a boundary change first (F.16):
the press names no position -- the topcard's only control of its kind, pressed strictly -- the
conversation his words go into must be titled with exactly that person's name, a receipt never
reads a control or a conversation swapped in place as his, a failed press is reported by what
the package built rather than by the browser library's text, and the door no longer readmits,
through an encoding or a letter that draws as blank, what its literal rules refuse. Census:
`M M1` COVERED-CANNOT-DELIVER -> COVERED-UNFIRED, `N 4` GAP ->
COVERED-UNFIRED by D6; `N 5` and `M M6` stay GAP, each now waiting on a capture this route's first
supervised press makes. NOT BUILT: the note on an invitation (`N 5`) -- an exact spec only, F.6.
NOTHING WAS FIRED: the lane stays offline, and every live proof waits on a person he names.

### F.1 What the captures show -- measured offline, counts and shapes only

Read over the 95 captures on disk (gitignored); no name, slug or member text was copied out.

    a third party's profile (/in/<other>/, canonical)            0 of 95
    'Invite <X> to connect'                                     52: 44 <button> with no href,
                                                                8 <a> to /preload/search-custom-invite
                                                                (people search only)
    'Message <X>'                                               18, ALL <a>: 16 to /messaging/compose/,
                                                                2 to /messaging/thread/; never a <button>
    <X> in both labels                                          the full name, 2 or 3 words
    document titles with a leading '(N) ' count                 21 of 95
    profile titles ending ' | LinkedIn'                         all
    his OWN profile's topcard                                   the one [id$="Topcard"] (6 captures);
                                                                its name an h2; h1 count 0
    the overlay conversation bubble                             captured minimised and sponsored only,
                                                                with no msg-form in it: 4 captures,
                                                                one bubble; its header a <header>, its
                                                                title ONE h2.msg-overlay-bubble-header__title
                                                                (text drawn directly, 6 words, not a name)
    the invitation dialog; a 'Pending' label                    0 captures of either

**SO NOTHING A NAMED ACT AIMS AT HAS EVER BEEN CAPTURED ON THE PAGE IT AIMS AT.** The labels are
measured on people cards, the topcard template on his own profile, the reply form on the
conversation pages. Every structural fact the acts need on a third party's profile is therefore a
VETO: the act refuses unless the page shows the measured shape, and each refusal reports what it
found as counts and closed tokens, so the first supervised act on a person he names IS the capture
(F.7). The synthetic fixture, `tests/fixtures/synthetic/named_profile.html`, says element by
element which parts are borrowed from a measured surface and which are derived.

### F.2 The second door, and who may call it

`readonly.assert_named_profile_url` admits EXACTLY `https://www.linkedin.com/in/<segment>/` --
three to a hundred letters, digits, hyphens, underscores or percent-encoded NON-ASCII letters
(the unit was any octet until the cold re-check, F.16 R5), and never one of the six letters that
draw as nothing or as blank space (the warm re-checks, NEW-1 and R3-NEW-1), the address composed by
`readonly.named_profile_url` from the caller's own segment -- and applies the
forbidden-substring list with NO exemption table (a segment carrying `/invite` or `settings` is
refused; it costs the caller one profile). `assert_read_url` and `is_read_url` are
byte-identical: the READ door still refuses every such address, and `tests/test_named_profile_route.py`
asserts it.

**A DOOR ADMITS AN ADDRESS FOR EVERY CALLER, AND THIS RULING IS ABOUT WHO**, so the callers are
what is pinned. `browser.LinkedInBrowser.goto(..., named_profile=True)` swaps the read door for
the second one -- the rate slot, navigation and settle are the same code. One function in the
package passes that keyword, `writes._load_named_profile` (an AST pin), and it refuses every spec
outside `NAMED_PROFILE_ACTIONS`; only `browser.py` and `writes.py` name the door (a second AST
pin). `tests/test_probe_navigation_budget.py`'s package-navigation guarantee counts the second
door as a guard in that one (file, function) and nowhere else (`SECOND_DOOR_GUARD`), rather than
adding it to `GUARD_CALLS`, which would have let any function call it and then navigate.

`readonly.py`'s `<functions>` digest was re-frozen `d7e1d0922e3af446 -> 6bdd6beaef275129`, with
the attribution this file's convention asks for: the tree MINUS exactly the door's three
functions hashes to the value replaced; dropping `is_read_url` instead lands elsewhere
(`f42c70c7413142d5`); a name no function carries moves nothing. Seven of eight digests
byte-identical. No `SANCTIONED_MUTATIONS` entry was added: the click and the fill are
`perform()`'s own. **RE-FROZEN AGAIN after the cold re-check narrowed the door:**
`<functions>` `6bdd6beaef275129 -> 4221c17c31fdd935`, and the door's two shapes PINNED for the
first time -- `NAMED_PROFILE_SEGMENT` `b3de160186fb187d`, `_NAMED_PROFILE_URL`
`32c49c9c6bc0626f` -- because the re-check measured that widening either moved no digest.
Attributed two ways: minus the door's three functions the tree still hashes to master's
`d7e1d0922e3af446` (nothing outside the door moved), and with the two changed functions swapped
back to their `cc8a509` source it hashes to `6bdd6beaef275129` (those two and nothing else).
Controls: swapping back the unchanged `assert_named_profile_url` moves nothing; dropping
`is_read_url` lands on `00aa3e33eda0838f`. **AND A THIRD TIME** for the letters that draw as
nothing: `<functions>` `4221c17c31fdd935 -> c191182c4f66d789` and `_INVISIBLE_LETTER_CODES`
pinned -- `80bce706e3a2b2c2` since the second warm re-check added the two Egyptian blanks, a
move of that digest alone -- attributed the same two ways.

**PAGE-MAY-VETO-NEVER-SUPPLY, where each half lives.** The landing is compared with the named
segment (case and percent-encoding folded) in a condition, never bound to a navigation, and
withheld through `landing.withheld` when it vetoes -- including a member id LinkedIn redirects to a
vanity address, which the act refuses rather than adopts (C-P6). Each control was addressed by
the POSITION `dom.NAMED_PROFILE_JS` computed inside the page; after two re-checks (F.16) it is
addressed by NO position -- as the only control of its kind inside the owner's topcard, pressed
strictly -- and what the page's script establishes, from a comparison that never leaves it, is
that the one control is the owner's:
the owner's name from the title (less a leading `(N) `), checked against the topcard's first
heading, and every Connect and Message control's accessible name checked against it. What crosses
is integers, booleans and closed tokens -- no position, since the re-checks;
`dom.read_named_profile` re-closes every field in Python.

**THE RULING'S SECOND CONDITION -- "the page's shaper stays name-free" -- AND ITEM 6, RECONCILED.**
The reader that aims is name-free, as above. The one place a name crosses is the confirm block's
`whom_this_resolves_to`, which item 6 of PEOPLE-DATA-MITIGATIONS requires ("the tool reports whom
it resolved before it acts"): read by `READ_PROFILE_JS` and the topcard parser on the preview's
own load, held to the title's name, added to a NEW dict after `grant.preview` was assigned (the
discipline of `_name_the_invitation_recipient` and `threads.name_the_reply_recipient`), and
asserted absent from the grant, the observation, every receipt and every error.

### F.3 The target -- a link or a member id, never a name

`named_profile.profile_segment` accepts a profile link (with or without scheme, `www` or a
two-or-three-letter country host, a trailing slash, a query or fragment -- which are dropped), a
member id (`ACoAA...`) or a member urn, and composes the canonical target as the LINK, so a second
normalisation returns it unchanged. It refuses a bare word BY ITS OWN RULE -- a one-word name and a
vanity segment are the same shape -- and says so, rather than letting the host check one line later
refuse it for a reason that sends him looking for the wrong mistake; it refuses `/in/me/`, any
sub-page, any other host, whitespace and control characters. Both tools run that normalisation
BEFORE a browser session is opened, so a name costs nothing at all.

### F.4 Connect -- `N 1`'s route through the profile, and `N 4` by D6

PREVIEW: one load through the door; the landing held to the segment; the page must name its own
owner (a profile title, exactly one topcard, its first heading equal to the title's name) and draw
exactly ONE control named `Invite <owner> to connect`, INSIDE that topcard, with no dialog open.
It prints whom it resolved to and a token.

**THE TOPCARD RULE WAS FOUND BY THE FIRST TEST RUN, NOT DESIGNED.** A world meant to model "the
page belongs to somebody else" named its owner Morgan -- and the fixture's side card already drew
`Invite Morgan Example to connect`. The in-page comparison matched that card: exactly one control
naming the page's owner, and it was a stranger's. A same-name person in 'People also viewed' is
the realistic form of that world. So a control is the owner's only inside the owner's topcard,
both acts refuse otherwise (C-P1 names where a third party's profile draws them), and the fresh
render's "still drawn" is counted inside the topcard too.

PERFORM: the address rebuilt by the write door, loaded through the second door, the landing held
again, the control re-read live (`_live_control`) -- the topcard must hold exactly ONE Connect
control, the owner's -- and pressed by `dom.topcard_invite_control_selector()`, the topcard scope
and nothing else, with `strict=True`: a page redrawn while the press retries that draws a second
match anywhere the scope reaches stops the press instead of handing it on (F.16 R2 and NEW-3).
PRESSING CONNECT MAY SEND AT ONCE; the preview says so.

VERIFY, in place and then on a FRESH render: in place first, because a reload discards the one
thing it can see -- whether a dialog opened, and whether ANY control naming the person is still
drawn: none at all reads UNKNOWN whatever the fresh render says, because a control swapped in
place during the press would have been pressed (F.16, R3-NEW-2). Then the fresh render: the
owner's Connect drawn again means NO INVITATION WAS SENT (`performed: false`). Gone reads UNKNOWN, with what the page's
controls naming the owner now read as closed tokens (`pending`, `withdraw`, `follow`, `unfollow`,
`more`, `remove`, `unrecognised`) -- never SENT, because what a pressed Connect becomes has never
been captured (C-P2). If a dialog opened, nothing in it was pressed (C-P3). The receipt says DO NOT
RETRY and points at My Network > Manage > Sent.

### F.5 Message -- `M M1`, and `M M6`'s capture

PREVIEW: as Connect's, and exactly one control named `Message <owner>` inside the topcard, of a
shape this act may press -- a `<button>`, or an `<a>` whose href is the composer (16 of the 18
measured); a link to anywhere else would navigate where the page chose, and is refused before
anything is pressed -- with no conversation composer already on the page. The block says, from
the topcard's degree line, whether the words will be typed: only for `1st`.

PERFORM: the press is the first click -- the topcard's only Message control, by the topcard scope
alone, STRICT, as Connect's is; the fill and the Send press are strict too -- and nothing is
queued before it (`OPEN_THEN_TYPE_ACTIONS`). After it, a BOUNDED
WAIT (up to 3 s) for a composer to be drawn, which decides nothing, and then
`named_profile.opened_conversation_gate` must pass, IN ORDER: the press did not move the browser
(the address after it equal to the one before, compared in a condition); the page still names
the same owner; the degree reads `1st`; the page is readable; exactly one composer, inside
exactly one overlay conversation, with one Send; **THAT CONVERSATION IS THE NAMED PERSON'S -- its
one title (`h2.msg-overlay-bubble-header__title`, the class measured on the captured bubble)
reads exactly the name the profile's own title gives, compared in the page, a boolean crossing**
(F.16 R3); no recipient box; empty, with Send DISABLED -- the measured empty form; and the number
of messages already carrying his exact words counted, the before-count. Only then are his words
queued -- a FOURTH `fill_plan.append`, held by `tests/test_typed_bytes.py` to the bar the other
three are: a bare `_text_component_of(spec, grant.target)`. After the fill,
`named_profile.composer_send_gate` applies the reply's five refusals -- no recipient box, one
editor, one Send, the fill landed, and the box holds EXACTLY his words -- and a SIXTH: with his
words in the box, the conversation's title is checked again. The Message press is counted apart from the submits (`opener_clicks`), so a run that typed
and refused reports the words left in his composer rather than a submit.

VERIFY, IN PLACE: the composer still holding his words with Send enabled is NOT SENT; SENT needs
his exact words as the conversation's last message, without `--other`, and the count of messages
carrying them up by EXACTLY ONE against the before-count, in a conversation still titled with the
person's name after Send (read by the page's own comparison -- F.16, R3-NEW-3); anything else is
UNKNOWN with every count, and DO NOT RETRY. **WEAKER THAN `send_reply`'s VERDICT, AND SAYS SO:** a reply is confirmed
on a fresh load of the conversation its caller named; this conversation's address is on the page
and this route never navigates to a page-supplied address, so it is read where it opened -- the
page's own redraw, with a before-count behind it.

FOR ANYONE WHOSE PROFILE DOES NOT READ `1st` the act presses Message, records what opened as
counts (`opened_conversation_gate.observed`), and STOPS BEFORE TYPING: a message there may be an
InMail that spends a credit, or a message request, and that composer has never been captured. That
reading is `M M6`'s capture (C-P5); nothing is sent, and the preview says so before the press.

### F.6 `N 5` -- NOT BUILT, and the exact spec for when it can be

WHY NOT: pressing Connect can send the invitation at once, so an act that carries a note could
send WITHOUT it -- an invitation he did not approve -- and the dialog a note needs has never been
captured. Nothing in this route presses anything inside a dialog.

WHAT THE CAPTURE MUST HOLD (C-P3), taken on the first supervised `linkedin_connect_from_profile`
press on a person he names, IF a dialog opens. THE RECEIPT ALREADY CARRIES ITS FIRST READING,
taken in place before the verification's reload discards the dialog: how many dialogs opened,
each control in them as a closed token, and how many note fields they hold. What only a page
capture adds (the live lane's `page.content()`, gitignored, read offline for shapes -- and since
the reload discards the dialog, taken by a capture probe that presses the SAME control on the
SAME person, stops at the dialog, presses nothing in it, and closes it): the dialog's container
(`[role="dialog"]`, its classes); every button in it (tag, `type`, disabled state); whether a note
control exists before any press (a `textarea` or contenteditable, its `maxlength`) or appears only
after an 'Add a note' press; and whether the default button sends without a note. THAT PROBE IS
A SECOND PRESS AND NEEDS HIS GO LIKE THE FIRST: it is reasonable only after the receipt showed a
dialog opening and the fresh render drew Connect again (nothing sent), and even then that the same
press opens the same dialog rather than sending is DERIVED, not measured -- if it sends, it sends
the invitation he already confirmed to that same person.

THE BUILD, ONCE THAT IS KNOWN -- a proposed tool, `linkedin_connect_with_note(profile, note, confirm_token)`,
which does not exist yet: a composite target (profile, note) typed exactly like a message; press Connect only where a dialog
is REQUIRED to open (refuse, having pressed nothing further, if the invitation sends at once); press
the note control only if measured as not dispatching; fill the note; press send only when the box
holds EXACTLY the note; verify on a fresh render as Connect does, never SENT off the dialog.

### F.7 NEEDS-CAPTURE -- C-P1 to C-P6, and what the receipt already records

Every one is taken inside the first supervised act on a person HE names; none needs a load of its
own except C-P6.

| id | what | where it lands today | the capture adds |
|---|---|---|---|
| C-P1 | a third party's topcard: its container, headings, degree line, where Connect and Message sit | the preview's `what_the_page_showed` (counts and tokens: `topcards`, `topcard_headings`, `heading_matches_title`, `degree`, `invite_in_topcard`, `message_in_topcard`, `more_actions`, ...) | the page's shape, offline: is the owner's heading the topcard's first h1/h2, and are the two controls inside `[id$="Topcard"]` |
| C-P2 | what a pressed Connect turns into | the receipt's `verification` (the fresh render's `named_controls` tokens) and the in-place reading | the new control's accessible name, so a later build can name the sent state |
| C-P3 | the invitation dialog | the in-place reading, taken before the reload discards it: how many dialogs opened, their controls as closed tokens (`add_a_note`, `send_without_a_note`, `send`, `cancel`, `dismiss`, `connect`, `unrecognised`) and how many note fields, read in the page | F.6's list |
| C-P4 | what a profile's Message press opens | `opened_conversation_gate.observed` -- composers, overlay bubbles, recipient boxes, empty, Send disabled, messages drawn; the conversation's titles, whether its one title reads exactly the person's name and whether it merely CONTAINS it (a hint no gate reads), and how long the composer took to be drawn (`composer_waited_ms`) | the bubble's markup, whether the form is the measured reply form, and what a person's conversation title holds besides the name -- if it holds more, the act refuses having typed nothing and that reading says what the comparison must be |
| C-P5 | the composer a NON-connection gets | the same block, on a person whose profile does not read `1st` (the act stops there), with two booleans -- whether the opened conversation says "InMail", or "credit" -- a hint no gate reads | whether it is a message request or an InMail, and what names a credit spend |
| C-P6 | whether a member id redirects to a vanity address | a preview called with a member id: the landing veto, withheld | nothing further: a redirect vetoes, and the remedy is to pass the link |

### F.8 The seam lane G adopts -- mitigation 2

`linkedin_server/people_seam.py` is the one place lane L5's name-bearing outputs pass through:
`people_seam.name` for the `include_names` rows of `threads.read_conversation_list`
(`linkedin_list_conversations`) and `shape.messaging_overview` (`linkedin_open_messaging`), and
-- since the cold re-check found it bypassing the seam (F.16 R4) -- for the conversation title
`linkedin_send_reply`'s preview prints as `who_this_would_reach`; `people_seam.person` for the
named acts' `whom_this_resolves_to`. OUTSIDE THIS LANE, and named in the seam's docstring so
adoption does not miss it: `writes._name_the_invitation_recipient` (2026-08-31) prints
`linkedin_send_invitation`'s recipient label through neither function. TODAY THEY COLLAPSE WHITESPACE
AND NOTHING ELSE -- what the list's reader always did, and one step more than the overview's
`.strip()` did -- and `person` adds a `mitigation_2` field saying the text is not yet sanitised and
is to be read as data. No second sanitiser was built.

**THE FAILING-UNTIL-ADOPTED TESTS** are `tests/test_people_seam.py`'s TWELVE strict xfails (nine
until the fourth output was routed), one property per reader per test -- no zero-width or bidirectional character survives, a name (for
the identity block, a headline) is capped at lane G's caps, the untrusted marker rides beside it --
asserted on what each READER returns for a planted name, so they flip whether lane G swaps the
seam's bodies or wires its record into the readers directly. `raises=AssertionError` makes any
other failure a real one; four controls (one per reader) pass today and after adoption, proving
the plant reaches the reader. Routing tests pass today and fail if a reader stops using the seam.
The reply's sentence quotes the title with `repr`, which ESCAPES an invisible character rather
than removing it, so its three are held on the title read back out of its quotes -- a check on
the sentence's characters would have passed today for the wrong reason.

**THE ADOPTION WAS RUN ONCE, IN SCRATCH.** Lane G's WIP sanitiser (`90e087b`, a commit on lane G's
own branch that does not resolve on `master` until that lane merges; `people_data.sanitise` and
`Person.from_page(...).envelope()`) wired into the seam's two bodies by
a scratch pytest plugin, with `--runxfail`: SEVEN OF THE NINE FLIP. The two that stay failing are
the list's and the overview's MARKER: a string field cannot carry `untrusted_third_party_text`, so
lane G's merge must mark those two envelopes (per row, or once per result). **RUN AGAIN after the fourth output joined, on `9d65c6f`: NINE OF THE TWELVE FLIP**, and the three that
stay are the three MARKERS on string outputs -- the list's, the overview's and now the reply
sentence's. And
`test_the_identity_record_has_the_four_declared_fields_and_says_it_is_pending` goes red on
adoption by design: it pins the pending field the adoption replaces.

**FOR LANE G'S FOUNDATION MERGE, exactly:** replace `people_seam.name`'s body with
`people_data.sanitise(raw, cap=people_data.CAPS["name"])` and `people_seam.person`'s with
`Person.from_page(...).envelope()` (or wire the record into the four readers and leave the seam
unused -- the routing tests then say so); add the untrusted marker to `threads.list_result`'s and
`shape.messaging_overview`'s results and beside the reply preview's `who_this_would_reach`;
remove the twelve xfail markers as they XPASS (strict turns each into a failure until it is
removed); retire or rewrite the pending-field test.

### F.9 The census -- MEASURED on the branch, not summed

`scripts/census_completion.py --check`, re-pinned with the move stated in its comment:

    adjudicated         202 -> 203     delivered_broad   113 -> 115     unfired     34 -> 36
    cannot_deliver       19 ->  18     gap               545 -> 544     gap_write  335 -> 334
    b1_standing          13 ->  15     PINNED_B1_ROWS    + M M1, N 4 on OPERATOR-NAMES-THE-TARGET

`scripts/count_census_states.py --expect J=107,P=160,M=124,N=153` MATCHES at 544 (network 154 ->
153). `_audit/_census/write-classes.tsv`: `N 4` `built:connect_from_profile`; `N 5`
`queued:CAPTURE-C-P3-INVITATION-DIALOG`; `M M6` `queued:CAPTURE-C-P5-NON-CONNECTION-COMPOSER`;
each citing `RULING:THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET` (and `N 4` D6).
`scripts/check_write_classes.py`'s known answers moved with the row: `N 4` was a known-IN
write-direction GAP row and is a known-OUT built write now; `N 5` takes its place.

**`M M2` STAYS COVERED-CANNOT-DELIVER, AND ITS ARGUMENT WAS WRITTEN OUT.** Its cell opened "same
tool, same gate" -- a positional pointer to `M M1`. `M M1` moved to a different tool, so `M M2`
would have inherited an argument that is not its own; the cell now names `linkedin_send_message`
and its gate itself, and says why `linkedin_message_from_profile` does not reach an InMail. The
pointer graph was re-pinned (`--pin`: 66 -> 65 pointers; the re-pin also refreshed `M M8`'s
reason-head column, pinned before lane L5's R3 note entered `M M8`'s own cell -- `--check` does not
compare that column). Two literals moved with it: the selftest's calibration line (`all 65 pinned
pointers`), and the G3 control's "56 remain elsewhere", stale since the pin fell from 69 and now
COUNTED from the edges rather than typed.

The notes: `M M1` (the state move), `M M2` (the write-out), `M M6` (still GAP; the addressing half
is open and the composer is not), `N 1` (a second route exists), `N 4` (the move, by D6, and the
search admission's condition 5 standing), `N 5` (a capture now, not a block). After the cold
re-check: `M M1`'s two sentences corrected to what the code checks, dated in the cell; `N 2`
annotated -- its ground no longer holds for a person he names -- and put to the orchestrator
(F.16); `M M5`'s reason completed. No state moved, and the census battery says so (F.14).

### F.10 The pins that moved, each MEASURED red before it was moved

A discovery run of 81 files over the uncommitted build went red on 94 tests; every one was one of
these, or the harness row F.11 names:

- the tool surface: 56 -> 58 tools, 87 -> 92 parameters (`PINNED_TOOL_SURFACE`, `EXPECTED_TOOLS`,
  the two exemption sets, the count, the read split 41 unchanged; the test renamed
  `..._fifty_eight_tools`); `test_every_tool_is_on_the_surface`'s 56 -> 58;
- the write surface: `PERFORMABLE` 15 -> 17 and `SANCTIONED_WRITES` 16 -> 18 in `tests/test_writes.py`
  (the sanctioned and performable sets, the reversibility tables: both STILL-UNKNOWN, unmeasured);
  server_info's two hand-typed lists and `performable_and_irreversible` (the seventh and eighth,
  typed by hand, and the message now says a NINTH is a decision); the instructions' word map to
  seventeen and `SEVENTEEN WRITE` naming both tools, with a paragraph on the route;
  `tests/test_writes_nine.py`: the destruction refusal's leaning set SIX -> EIGHT, by name, and the
  composite harness's clean `profile` component;
- `tests/test_receipt_names_its_own_action.py`: the acknowledged count 15 -> 17, earned as its
  docstring asks -- `message_from_profile` a second owner of "composer" and a third of "LinkedIn
  messages" (it reads the composer its press opened, then the conversation), `connect_from_profile`
  a second owner of "My Network", and the invitation pair a third sanctioned shared place (one act,
  two routes, one Sent list); no row was reworded to dodge a phrase. Its test named for "the two
  sanctioned pairs" is renamed for the groups;
- `tests/test_typed_bytes.py`: fill sites 3 -> 4 and the extractor list, extended not weakened;
- `tests/test_readonly.py`: `NAMED_PROFILE_JS` declared (its privacy argument beside it), executed
  scripts 23 -> 24, the dom.py waiver budget 22 -> 23 with the answer to "why not a locator chain";
- `tests/test_preview_state_and_click_state.py`: both actions REACHED over the synthetic profile,
  17 of 17;
- prose counts: `server.py`'s headline, split, sum and sanctioned-versus-tools paragraph;
  `README.md`'s headline (with its stale text kept beside it) and module listing;
  `tests/test_server_surface.py`'s derived first line; the `known_side_effects` sentence that said
  no tool loads a third party's profile (it now names the two, and dates its correction);
  `read_boundary_scope` (the one navigation it does not gate); two comments in `readonly.py` that
  cited that sentence; `linkedin_send_invitation`'s docstring;
- `writes._render`'s "THE SEVEN", stale since this lane's own `thread_and_text` made it eight on
  2026-09-24, now "THE REST -- TEN", with that slip recorded in place;
- baselines, each by its own writer: `reader_leak` (+7 readers, all clean or not driven),
  `tool_envelope` (+2, not driven: writes refuse at the flag), `landing_interpolation` (+4 sites;
  the second door's three refusals ruled ASKED_FOR -- it quotes the caller's own composed address
  back before any navigation -- and one more WITHHELD in `_assert_landed_on_target`);
- AFTER THE RE-CHECKS: `tests/test_selectors_resolve.py` (the two topcard builders resolved
  against a page that now draws one topcard; it was RED on the removed `message_control_selector`,
  F.16); `tests/test_readonly_boundary_invariant.py` (`PINNED` +3 -- the door's two shapes and the
  blank letters -- and three re-freezes, each with its attribution); `tests/test_writes.py`'s
  pinned click call site, which gained `strict=press_strictly` (still ONE site);
  `tests/test_readonly.py`'s note on `NAMED_PROFILE_JS`, which no longer says a position crosses;
  `tests/reader_leak_baseline.json` (+1 reader, `wait_for_opened_composer`, clean, by its own
  writer); the opened gate's conditions 6 to 8 renumbered 7 to 9 in the route's tests;
- `scripts/ci_shard_timings.json`: the two new files, measured by a junit run of the two alone,
  serially, NOT a quiet box, RE-MEASURED at `c79216d` after the fix rounds added tests: 118 tests
  in 74.1 s and 28 in 14.0 s. Earlier readings -- 51.1 s and 11.3 s for 77 and 23 on the merged
  tree, and 102.9 s and 18.9 s for 70 and 23 on the branch with other lanes' agents busy -- are
  kept in the table's own provenance so no drop is mistaken for a speed-up.

### F.11 Findings along the way

- **A NEW TARGET KIND AGAIN STOPPED THE PAGE-STRING HARNESS** (69.7's lesson, re-met):
  `tests/refusinggrant.py` had no synthetic target for `profile`, and the KeyError stopped every
  writes reader being driven for any spec -- 42 of the 94 reds from that one table. Three more
  kind-keyed tables (`test_writes_nine`'s components, the reach-its-control shapes, the
  preview-state reach) made it 54. Each row was added before anything else was read.
- **THE EDIT TOOL DECODED FOUR ESCAPE SEQUENCES INTO THE CHARACTERS THEY SPELL** -- a middle dot, an
  ellipsis, a zero-width space and a direction override, each written as a backslash-u escape
  and landed as the character. Found by the ASCII check over the diff, fixed by a script that
  builds every character with `chr()`; the first checkpoint commit (`a241623`) carries two of
  them in its history, the tree carries none.
- **AN INSERTION BROKE AN if/elif CHAIN IN `perform()` WITHOUT A SYNTAX ERROR**: the block taking
  the address before the Message press was first placed between two `elif` arms, so every later
  arm hung off the new `if`. Found by reading the diff before the first commit, and moved after
  the chain.
- `tests/test_write_classes.py`'s `N 1` plant copied the FIRST network line -- `N 4`, a queued line
  until this build. A built line may name a COVERED-UNFIRED row, so the plant stopped being
  convicted of what the test is about; it now takes the first QUEUED network line.
- **EDITING A MODULE WHILE A GATE RAN MADE SEVEN REDS THAT WERE NOT THERE.** A prose edit to
  `writes.py` landed during a run of `tests/test_click_is_not_its_own_evidence.py`, whose AST checks
  read `inspect.getsource(writes.perform)`: the module was imported before the edit and the lines
  were read after it, so `getsource` returned one line of something else and seven checks went
  red. Re-run on the committed tree: green. Commit first, then gate -- and edit nothing a running
  gate reads.
- `tests/test_a_person_name_is_never_a_literal.py` flagged the route's member-id constant, then
  named `MEMBER`, which that guard reads as a person-carrying name; renamed `MEMBER_ID` -- it holds
  a declared synthetic member token, which is what the identity guard's `SYNTHETIC_MEMBER_TOKENS`
  exists to declare.

### F.12 Live queue -- the named-person route

Every call runs in a process the live lane owns, inside its budget (`live-fire-budget-40-loads`:
40 page loads a live session, 20 s or more apart, one live lane). "HE NAMES" is
OPERATOR-NAMES-THE-TARGET: nothing here fires at anybody he has not named. **The live-proof
targets he named are in the gitignored identity key, class `operator_named_live_targets`, and
NEVER in a tracked file.** Each is resolved to the person's exact profile LINK first -- by him,
from his own browser -- and the link is what the call takes; a name is refused by the tool
itself. He reads `whom_this_resolves_to` in every preview and confirms only if it names the
person he meant: a link to the wrong person is the one failure no gate here can catch.

| row | call | target | loads | what banks it |
|---|---|---|---|---|
| `M M1` | `linkedin_message_from_profile(profile=<link>, text=<HE NAMES>)`, he checks whom it resolved to, then the same call with `confirm_token` within 120 s | a FIRST-DEGREE connection he names, and the exact words | 1 (preview), then 1 (act, verified in place) | COVERED-PROVEN on `performed: true, verified: true`. `opened_conversation_gate.observed` is capture C-P4 either way -- including whether the conversation's title reads exactly the name (`conversation_names_the_owner`) or merely contains it, and `composer_waited_ms`; any refusal there typed NOTHING and is itself the finding |
| `N 4` | `linkedin_connect_from_profile(profile=<link>)`, he checks whom, then confirms | a person he names who is not yet a connection, and whose profile draws Connect | 1, then 2 (act, fresh render) | the receipt reads `unknown` BY DESIGN when the control changes (C-P2), with what it became as tokens; he opens My Network > Manage > Sent, and the invitation there banks COVERED-PROVEN on his reading. `performed: false` (Connect drawn again) banks nothing and is a finding. If a dialog opened, the receipt names its controls (C-P3) and nothing in it was pressed |
| C-P5 (`M M6`) | `linkedin_message_from_profile` on a person he names whose profile does NOT read `1st` | a non-connection he names | 1, then 1 | nothing banks: Message is pressed and nothing is typed. `opened_conversation_gate.observed` (with its InMail and credit hints) IS the capture; the live lane's page capture of the opened composer adds its shape |
| C-P6 | the `M M1` preview called with his member id in place of the link | the same person | 1 | the landing: served at the id, or vetoed as a redirect, withheld |

One pass: 8 loads. `N 5`'s capture needs no load of its own: it rides the `N 4` press (F.6).


### F.13 Mutations -- thirty-nine, each broken ALONE in a scratch copy of the tree

A copy of the tracked files at `c79216d`; every named test passed on the unmutated copy first
(39 of 39), then each mutation was applied alone, its tests run, and the file restored and
checked byte for byte. **39 OF 39 KILLED**, each as a test failure, none as an error. The first
twenty were killed at `daf157f` too (20 of 20); re-aimed where the code moved, they and the
sixteen written for the first two fix rounds were killed at `9d65c6f` (36 of 36) before round
three added three more.

    N1   the second door's forbidden-substring check removed          takes_no_exemption
    N2   the browser always takes the second door                      swaps_the_door
    N3   the loader stops refusing specs that are not named acts       loader_refuses
    N4   the loader navigates without calling the second door          package_navigation_guarantee,
                                                                       referenced_only_by
    N5   a bare word no longer refused by its own rule                 bare_word (3)
    N6   every landing reads as the named profile                      vetoes_and_mints_nothing,
                                                                       landing_moved
    N7   Connect need not be inside the topcard                        same_name_stranger,
                                                                       only_a_stranger_matches
    N8   Message need not be inside the topcard                        same_name_stranger
    N9   the topcard may hold a second control of the kind             second_control_of_the_kind
    N10  the page's heading not compared with the title                somebody_other_than_the_title
    N11  Message types for anyone, not only a first-degree connection  second_degree_message
    N12  a press that moved the browser is typed into anyway           ...[navigates]
    N13  Send pressed on words that are not his                        other_words_than_his
    N14  the SENT delta weakened from exactly one to at least none     cannot_stand_in
    N15  the name read not held to the title's name                    cannot_tie_to_the_title
    N16  whom it resolved to written into the retained block           keeps_it_nowhere
    N17  the words queued whatever the opened-conversation gate said   second_degree_message
    N18  the Message press counted as a submit                         other_words_than_his
    N19  the conversation list's names bypass the people seam          conversation_lists_names
    N20  the messaging overview's names bypass the people seam         overviews_names
      -- the cold re-check (F.16) --
    N21  the segment's encoded unit admits any octet again             no_encoding_lets_back_in
    N22  the decoded segment not held to letters                       no_encoding_lets_back_in
    N23  the Connect spec's own address pattern widened                address_pattern_refuses
    N24  the Connect press aimed page-wide again                       re_render_during_the_press
    N25  the opened conversation's title not checked                   somebody else's, did_not_open
    N26  the title not checked again before Send                       changes_hands
    N27  the title compared by containment, not equality               ...[group]
    N28  no bounded wait before the opened gate reads                  drawn_a_moment_after
    N29  a failed press reported with the library's text again         press_that_fails,
                                                                       reported_whole
    N30  the reply recipient's name bypasses the people seam           reply_recipients_name
      -- the warm re-checks --
    N31  the Message press aimed page-wide again                       re_render_during_the_message_press
    N32  the named acts' presses and fill not strict                   second_match_drawn_mid_press,
                                                                       second_send_drawn
    N33  the press in flight not recorded                              press_that_fails, and the
                                                                       apply test's second click
    N34  the first bubble's title read, not the holding one's          holding_the_composer
    N35  the page does not count the topcard's controls of the kind    second_control_of_the_kind
    N36  the blank-drawing letters admitted                            no_encoding_lets_back_in
    N37  a Connect gone in place read as not sent                      swapped_in_place_mid_press
    N38  a conversation not titled theirs after Send read as his       swapped_in_place_during_send
    N39  the two Egyptian blanks admitted                              no_encoding_lets_back_in

N9 changed meaning with the design: at `daf157f` it made the page report the first Connect's
position; with no position left, it removes the rule that the topcard hold one control of the
kind. At `149e787` two of the VERIFIER's mutations survived -- the Message press aimed page-wide,
and the first bubble's title read -- which is what N31 and N34 now kill; the verifier's five
mutations on round two were all killed.

Five of the first twenty's tests were written for the mutation that would otherwise have survived:
N5 (the host check refused a bare word one line later, so only the MESSAGE told the two apart),
N10, N14, N15 and N18. A check that cannot fail certifies nothing, and those five could not until
then.

### F.14 Gates run on the branch, before the merge

- A DISCOVERY run over the uncommitted build, 81 files: 94 failed, every one a pin or a harness
  row listed in F.10 and F.11.
- The gate over `f132155`, 84 files with `-n 4 --dist loadfile`: **5724 passed, 10 xfailed (this
  follow-up's nine and one standing), 3 skipped, 4 failed.** Two were this run reading files
  that were being edited while it ran -- an identity hit on a test value replaced minutes later
  (clean on re-run) and the rulings register, stale by one phrase count until the record was
  written (regenerated below). Two were REAL pins the build had missed: the package docstring's
  write-tool count and `readonly.py`'s top-level function count, 14 -> 17. Both fixed in
  `daf157f`.
- The census instruments at `daf157f`: all green but the rulings register (the same phrase count).
- The mutations (F.13) and the adoption dry-run (F.8).
- The two new files alone, serially, with a junit record: F.10's timings.

**AFTER THE MERGE -- the three fix rounds (F.16), each gated on its own commit:**

- ROUND ONE (`149e787`). The route, seam, selector and reply files: 166 passed, 12 xfailed. The
  boundary and page-string guards (11 files), on a tree being edited: 8 red -- SEVEN were this
  lead editing `writes.py` while `tests/test_click_is_not_its_own_evidence.py` ran (its AST checks
  read `inspect.getsource(writes.perform)`, and the module imported before the edit was read at
  the lines after it; green on the committed tree), and ONE was real: the reader-leak baseline
  lacked the new reader, regenerated by its own writer. The 123-file gate on `149e787`: 7001
  passed, 13 xfailed, 3 skipped, 2 failed -- the rulings register (known) and
  `tests/test_apply_modal_fixture.py::test_a_proceeding_gate_appends_the_second_click`, a REAL red
  that round one's own fix caused (F.16, NEW-2). The 14 write-pipeline files over the fix: 1106
  passed, 3 skipped, 1 xfailed.
- ROUND TWO (`9d65c6f`). The route and boundary files: 10 collection errors, every one the selector
  test still handing an index to the no-argument builders (fixed before the commit; 49 passed); the
  123-file gate on `9d65c6f`: 7011 passed, 13 xfailed, 3 skipped, 1 failed -- the rulings register.
- ROUND THREE (`c79216d`, gated on the working tree the commit then took unchanged): the corpus
  floor, the route and seam, the read boundary and the write pipeline's guards, 37 files: 4421
  passed, 13 xfailed.
- The census battery after the census prose moved (F.9): green but the rulings register, which is
  regenerated with this record.
- The adoption dry-run again (F.8): nine of the twelve flip.
- Two warm re-checks by the verifier (F.16).

### F.15 The one integration: master `2eb90ad`, merged once, at the end

Master had moved from `96c1165` to `2eb90ad` -- 52 commits, seven on its first parent: lane S's
follow-up (four search verticals, member rosters, an encoded-dot hole closed), the live lane's
Part 2, lane D (`N 132` under D6, the PDF download transport), two fixes, lane Y2's follow-up (the
P-R settings block itemized into 22 rows) and lane L7's `P B9`. It was sampled at `9f6e272` and
had moved again by the time of the merge; the merge took the SHA, not the moving name.

**FOUR FILES CONFLICTED, and `git merge-tree` named the same four before the merge ran:**

- `linkedin_server/writes.py` -- three hunks, each TWO INDEPENDENT ADDITIONS in the same place:
  `_verify_after`'s parameters (this route's `opened`/`typed` beside `P B9`'s
  `badge_before`/`witness`), the click loop's arms (this route's open-then-type arm beside the
  premium badge's `switch` arm -- disjoint conditions: an action in `OPEN_THEN_TYPE_ACTIONS`
  against a control kind of `switch`), and the call's keywords. Resolved as the union, both
  kept whole.
- `tests/test_readonly_boundary_invariant.py` -- the two branches' re-freeze NOTES met. Master's
  kept first, this route's after, and a merge note: on the merged tree `<functions>` is this
  route's `6bdd6beaef275129` and `_ALLOWED_URL_PATTERNS` master's `6240409ec52c4ab2`, each
  MEASURED, and the tree minus the door's three functions still hashes to master's own
  `<functions>`, `d7e1d0922e3af446`. All eight digests match.
- `scripts/ci_shard_timings.json` -- master's table taken whole and this route's two files
  re-added by the same script that added them on the branch (`_files` and `_total_seconds`
  recomputed, the provenance appended).
- `scripts/census_completion.py` -- master's pins taken whole and the census RE-MEASURED on the
  merged tree: the same seven figures move by the same amounts over master's pins (F.9's block,
  re-stated there against `2eb90ad`), and `PINNED_B1_ROWS` gains `M M1` and `N 4` beside master's
  rows. `count_census_states --expect J=107,P=180,M=124,N=152` matches (network 152: master's
  `N 132` and this route's `N 4`).

**NOTHING ELSE CONFLICTED, AND NOTHING ELSE COULD BE ASSUMED.** Every pin this route moved was
re-measured on the merged tree rather than carried: master added no tool and no write, so the
surface stays 58 tools, 92 parameters, 17 performable, 18 sanctioned.

**GATES ON THE MERGED TREE.** The 26 files whose pins this route moved, on the merged tree before the merge
commit: 2161 passed, 9 xfailed. The wide list (91 files: the floor, the census instruments, the
surface and its pins, lane G's guards, the read boundary, messaging and the write neighbours) on
`cc8a509`: 6104 passed, 10 xfailed, 3 skipped, 1 failed -- the rulings register, stale by one
phrase count (regenerated with this record). The census battery on the merged tree: green but that
register. A file the lists did not hold was red all along: see F.16's closing paragraphs.

### F.16 The cold re-check, and the warm re-checks that followed

A `general-purpose` verifier with no part in the build (agent `aaaf98ea9c3abda66`), briefed to
REFUTE, read-only on a snapshot of `daf157f` (868 blobs, checked before and after), offline. It
returned **6 REFUTED, 3 COULD-NOT-CHECK, 11 CONFIRMED**, each refutation DEMONSTRATED on the
synthetic fixture rather than argued. All six were real. The fixes are `149e787`, each held by a
test that fails without it and by a mutation that is killed (F.13):

| # | what it demonstrated | the fix | held by |
|---|---|---|---|
| R1 | a press that FAILED put the browser library's call log in `clicked.error` -- `Invite <owner> to connect`, `Message <owner>`, and the Message link's member id -- because `perform` reported every exception as `Type: text` (shared with `send_invitation`, so not new code; the claim "whom it resolved to, nowhere but the preview" was this lane's) | `writes.describe_click_error`: this package's own `WriteAttemptError` whole; anything else COMPOSED from what the package knows at the call -- the exception's type and, when a page call was in flight, its kind and the selector `perform` built for it (`in_flight`, set around each press, fill, choice and upload; the call sites themselves unchanged by it). The first version reported the type alone, and the fix round's gate caught what that cost: `tests/test_apply_modal_fixture.py` proves the apply flow's second click was attempted by finding its selector in this line | `test_a_press_that_fails_is_reported_by_its_type_and_names_nobody` (both acts, a press held under a transparent layer until it times out: the line is exactly the type and the topcard selector, no call log), `test_this_packages_own_refusal_is_still_reported_whole`, and the apply test; N29, N33 |
| R2 | the press was `INVITE_CONTROL >> nth=K` over the WHOLE page, and Playwright re-resolves a selector whose element is re-rendered while the press retries: with the owner's Connect redrawn and a stranger's drawn at the top of the page mid-press, THE STRANGER WAS PRESSED -- and the fresh render then read "NO INVITATION WAS SENT" | FIRST (`149e787`): the position counted INSIDE the owner's topcard and the press scoped to `[id$="Topcard"]`; the page-wide `message_control_selector` removed. THEN, after the warm re-check found the position itself was the hole (NEW-3, below): no position at all -- `dom.topcard_invite_control_selector()` / `topcard_message_control_selector()` are the topcard scope alone, the topcard must hold exactly ONE control of the kind, and the press is strict | `test_a_re_render_during_the_press_cannot_hand_it_to_a_stranger` (the verifier's world), `test_a_re_render_during_the_message_press_cannot_hand_it_to_a_stranger`, `test_the_press_is_the_topcards_only_control_of_its_kind_pressed_strictly`; N24, N31 |
| R3 | nothing compared the conversation the words went into with the person named: a press that opened somebody else's conversation, and a press that opened NOTHING while a conversation appeared during it, both took his words and read SENT -- counts ("none before, one after") cannot say whose | the page's script compares the one holding bubble's title with the owner's name from the document title and returns booleans; `opened_conversation_gate` refuses `6_not_their_conversation` (7 to 9 renumbered); `composer_send_gate` checks it AGAIN with his words in the box; a bounded wait (3 s, deciding nothing) lets a composer drawn a moment after the press be found | the parametrised refusals (somebody else's, and a GROUP that includes the named person), `test_a_conversation_headed_by_somebody_else_is_read_and_refused_in_the_page`, `test_a_conversation_the_press_did_not_open_never_takes_his_words` (the verifier's second world), `test_send_is_not_pressed_when_the_conversation_changes_hands_after_the_fill`, `test_a_conversation_drawn_a_moment_after_the_press_is_still_found`; N25 to N28 |
| R4 | `send_reply`'s `who_this_would_reach` printed the other participant's name with ZERO seam calls, and `tests/test_people_seam.py` did not list it | `threads.name_the_reply_recipient` takes the title through `people_seam.name` (the same expression `_normalise` applied, so no value moves) | `test_the_reply_recipients_name_comes_out_of_the_seam`, a plant control and three more strict xfails (F.8); N30 |
| R5 | the segment's percent-encoded unit `%[0-9A-Fa-f]{2}` admitted EVERY octet: `.../in/Casey%20Example/` (a two-word NAME) passed the link parser, and an encoded slash, NUL, newline or `%2Finvite` reached the door | the unit is `%[89A-Fa-f][0-9A-Fa-f]` (the octets UTF-8 uses for non-ASCII letters), in `readonly.NAMED_PROFILE_SEGMENT` and both WriteSpec patterns, and `valid_named_profile_segment` decodes the segment (strict UTF-8) and holds it to letters, digits, hyphens and underscores; the freeze now PINS the door's two shapes | `test_no_encoding_lets_back_in_what_the_segment_refuses` (ten segments), `test_the_write_specs_own_address_pattern_refuses_an_encoded_ascii_octet`, `test_a_vanity_name_with_a_non_ascii_letter_is_still_admitted`; N21 to N23 |
| R6 | `M M1`'s cell said the Message control "opens a conversation that already has its recipient" as fact, and that the act typed only when "the press opened exactly one empty conversation composer" -- neither was what the code checked; and `N 2`, "Send an invitation from a named member's profile", still reads EXCLUDED-RULED under R4 while `linkedin_connect_from_profile` performs exactly that | `M M1`'s two sentences rewritten to what the code now checks, the correction dated in the cell; `N 2` annotated and PUT TO THE ORCHESTRATOR (below), not moved; `M M5`'s reason completed. No state moved | the census battery (F.14) |

**THE LOW FINDINGS.** (a) The reader-leak baseline records `named_profile:name_the_profile_target`
as `clean`, and the harness makes ZERO page reads inside it: it hands the reader a planted page
whose facts confirm nobody, so it returns at its first guard -- an unearned clean by that file's
own rule, the same shape `threads.name_the_reply_recipient` already had. NOT FIXED HERE: the
harness is lane G's guard, and making it drive a reader that needs a page naming one person is a
harness change; the route's own tests hold the property instead (the identity block in the preview
and nowhere else, `_clean` over every grant, observation and receipt). **For lane G: a reader the
harness drives without a single page read should read `not_driven`, not `clean`.** (b) The second
door's two shapes were not in the freeze's pinned tables, so widening the door moved no digest --
FIXED: both pinned (F.10).

**COULD-NOT-CHECK (3):** the identity guard and one login test need `.git`, which a snapshot does not
have (both run in this lane's gates); and anything about LinkedIn itself -- a third party's profile,
what Connect becomes, the dialog, what a Message press opens and when -- which is NEEDS-CAPTURE
C-P1 to C-P6 by this record's own account.

**CONFIRMED (11)**, among them: no read tool, probe or other write reaches the second door (an AST
scan); the read door is byte-identical and still refuses every `/in/<x>/` but `/in/me/`; nothing is
typed for a profile that does not read `1st`; Send only on the exact words; SENT only on a delta of
exactly one with authorship; the four census instruments green with the pin moves matching the two
state moves exactly; no guard widened beyond the two actions; 4357 added lines, 0 non-ASCII bytes,
every identity-shaped token a declared synthetic one.

**PUT TO THE ORCHESTRATOR, NOT DECIDED HERE: `N 2` -> COVERED-UNFIRED by
`linkedin_connect_from_profile`, under ruling `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET`.** Its ground,
R4, is exactly what that ruling lifts for a person he names, and the capability is the route itself,
so no D6 argument is even needed. The ruling's unblock list omitted the row and the lane followed
the list; moving a ruled row the ruling left out is the orchestrator's call. If moved: EXCLUDED-RULED
-1, COVERED-UNFIRED +1, and `scripts/census_completion.py`'s pins move with it.

**THE WARM RE-CHECK -- the same verifier, on `149e787`, its snapshot checked blob for blob:
FIXED 7 (R1 to R6 and LOW (b), every earlier demonstration failing to reproduce), NOT FIXED 1
(LOW (a), deliberately -- above), NEW 7.** Six are closed in `9d65c6f`; one waits on a capture:

| new | what it demonstrated | what was done |
|---|---|---|
| NEW-2 | `149e787` RED on `tests/test_apply_modal_fixture.py::test_a_proceeding_gate_appends_the_second_click`: R1's type-only line removed the selector that test's evidence rode in (this lane's own fix-round gate showed the same red) | the line composed from the call in flight -- above, R1 |
| NEW-3 | THE POSITION WAS THE HOLE. Scoped to the topcard, the press was still `<scope> >> nth=K`, re-resolved mid-press: a stranger's Connect drawn INSIDE the topcard, or in a second `[id$="Topcard"]` element, took the press, and the receipt read NOT SENT | no position at all. The page's script returns how many controls of each kind the topcard holds (`invite_controls_in_topcard`, `message_controls_in_topcard`) and no index; `connect_state` / `message_state` refuse unless exactly ONE, the owner's; the selector is the topcard scope alone; and `perform` presses and fills STRICTLY for the named acts (`strict=press_strictly`), so two matches at press time THROW. MEASURED before relying on it: on a local page with two matching buttons `page.click` pressed the first; with `strict=True` it raised a strict mode violation. Held by `test_a_second_match_drawn_mid_press_stops_the_press` (both worlds: nothing pressed, the line names the strict press) and `test_a_topcard_holding_a_second_control_of_the_kind_is_refused`; N9, N32, N35 |
| NEW-5 | the Send press was page-wide and re-resolvable: with the owner's Send redrawn and a restored conversation holding a DRAFT drawn first, THAT DRAFT WAS SENT | the same strictness: a second Send at press time throws -- `test_a_second_send_drawn_during_the_send_press_stops_it` (neither his words nor the draft sent); N32 |
| NEW-1 | the four default-ignorable code points that are LETTERS (the Hangul fillers U+115F, U+1160, U+3164, U+FFA0) pass `isalnum()`, so a two-word name with U+3164 in place of the space passed the door | refused by code point (`readonly._INVISIBLE_LETTER_CODES`, measured as exactly those four over the default-ignorable ranges with Unicode 15.1), and the tuple PINNED in the freeze -- re-frozen `4221c17c31fdd935 -> c191182c4f66d789`, attributed as before (minus the door: master's `d7e1d0922e3af446`; the one changed function swapped back: the value replaced); four more segments in the door tests; N36 |
| NEW-6 | `_audit/RULINGS.md` stale by one phrase count since `daf157f` (consistent at `96c1165` and at master) | regenerated with this record |
| two surviving mutations | the Message press aimed page-wide again stayed green (no Message re-render world), and reading the FIRST bubble's title instead of the holding one's stayed green (no world drew two bubbles) | `test_a_re_render_during_the_message_press_cannot_hand_it_to_a_stranger`, and `test_the_title_compared_is_the_one_on_the_conversation_holding_the_composer` (two bubbles, both orders); both mutations now killed (N31, N34) |
| NEW-4 | NAME EQUALITY IS NOT IDENTITY: a different person with the named person's exact name, whose conversation was drawn during a press that opened nothing, received his words, and the verdict read SENT | **NOT CLOSED.** The only closing compares something identity-bearing in the bubble -- a participant's profile link, a member id -- with the profile named, in the page, as a boolean; and a person's conversation bubble has never been captured (the one on disk is minimised, sponsored, and carries no link in its title). It is now C-P4's FIRST question. What the risk needs, all at once: the press opening nothing, LinkedIn drawing a conversation by itself within the moment of the press, and that conversation's other member bearing exactly the named person's name |

**THE SECOND WARM RE-CHECK -- on `9d65c6f`: FIXED 7 (NEW-1, NEW-2 -- the apply test green again --
NEW-3 in both worlds, NEW-5, both surviving mutations, LOW (b)); NOT FIXED 3 (NEW-4 and LOW (a),
deliberately; NEW-6, regenerated with this record); five mutations of its own on round two, all
killed; and three NEW, all LOW, answered in `c79216d`:**

| new | what it demonstrated | what was done |
|---|---|---|
| R3-NEW-1 | two letters that draw as BLANK SPACE without being default-ignorable -- EGYPTIAN HIEROGLYPH FULL BLANK and HALF BLANK, U+13441 and U+13442 -- passed the segment check | refused; and the list is now DERIVED rather than found one re-check at a time: a sweep of every code point `isalnum()` accepts whose Unicode name carries FILLER, BLANK, SPACE, INVISIBLE, NULL or EMPTY found exactly these six (the four fillers and the two blanks), besides the MATHEMATICAL MONOSPACE letters, which match on the substring and draw as letters. Only the tuple's digest moved in the freeze (`02528c398b97abab -> 80bce706e3a2b2c2`); two more door segments; N39 |
| R3-NEW-2 | STRICTNESS BINDS THE COUNT, NOT THE PERSON: the owner's Connect replaced IN PLACE by a stranger's mid-press (still one Connect in the topcard) was pressed, and the receipt read NO INVITATION WAS SENT | **THE PRESS IS NOT PREVENTED -- a residual, below.** The receipt no longer lies: when, right after the press, the page draws no control naming the person at all, `connect_verdict` says UNKNOWN and DO NOT RETRY -- `test_a_control_swapped_in_place_mid_press_is_never_reported_not_sent`; N37 |
| R3-NEW-3 | the same for Send: the owner's whole conversation swapped in place during the Send press for another holding a draft -- that draft was sent, the receipt read unknown | **NOT PREVENTED -- the same residual.** The verdict now says why: after Send, `_verify_after` reads whose conversation holds the composer (the page's own comparison, one boolean), and `message_verdict` never reads a conversation not titled with the person's name as his -- so SENT now requires it too. `test_a_conversation_swapped_in_place_during_send_is_never_read_as_his`; N38 |
| observation | an open shadow root inside the topcard: the page's script counts one Connect, Playwright's scoped selector sees two (it pierces), so the gate says pressable and the strict press throws every time | fail-closed; recorded. If LinkedIn's topcard ever carries a shadow root the act refuses at the press rather than at the preview, and C-P1 shows it |

**WHAT REMAINS OPEN, AND WHAT WOULD CLOSE IT.** (1) NEW-4, name equality is not identity: C-P4's
first question, above. (2) R3-NEW-2 and R3-NEW-3, a control or a conversation swapped IN PLACE
during the press: strictness binds the count and not the person. The closing the verifier
proposed, and the one this lane would build: a Playwright selector engine that resolves, IN THE
PAGE, "the one control of this kind in the topcard whose label names the title's owner" (and "the
Send of the conversation titled with that name"), so that every retry re-checks identity and no
name crosses. That is a new kind of script the page runs -- registered with the browser, not passed
to `evaluate` -- which the read boundary's script declarations do not yet know how to see, so it is
a boundary change of its own and NOT built under this order. What the risk needs: LinkedIn
redrawing the named person's own topcard, or conversation, for somebody else, without a
navigation, inside the moment of a press.

**AND ONE FINDING OF THE LEAD'S OWN, FROM THE STRICTNESS MEASUREMENT, OUTSIDE THIS LANE.** Six
comments in other lanes' code say Playwright's strict mode holds their press to one element --
`company_interest.OFF_CONTROL_IN_CARD`, `dom`'s company-page follow block, `profile_editor.SAVE_SELECTOR`,
and `writes._live_control`'s arms for `mark_company_interest`, the company-page follow and the posting
follow's relabelled control. Every press goes through `perform`'s one `page.click`, which passed no
`strict` until this follow-up and passes `False` for those actions now; measured, `page.click` is not
strict unless asked. So those six claims are false today. NOT CHANGED HERE: making those presses
strict changes other lanes' acts, some of them fired live. **Put to the orchestrator: add those
actions to `press_strictly` (their gates already require exactly one match), or correct the six
comments.**

**FOUND BY THE FIX ROUND ITSELF, AND WORTH MORE THAN ONE LINE.** `tests/test_selectors_resolve.py`
-- which enumerates every `*_selector` builder in `dom.py` by AST and resolves each in a browser --
was RED at `daf157f` and at the merge: this follow-up added `message_control_selector` and none of
its gate lists included that file. The lists were HAND-BUILT around the files the build touched,
and a guard coupled to the diff by a naming convention rather than by an import was invisible to
them. The shipped impact analyser does select it; it selects 225 of 253 files for this round (the
edited modules are imported by nearly everything), which is the full suite the order rules out
locally -- so the fix round's gate is the analyser's DATA couplings taken whole, every file naming
a symbol this round touched, every file that drives `perform()`, and the previous wide list (F.14),
with the 130 files it did not run LISTED in the scratch provenance. And the two new builders are
named `*_selector` on purpose: the first draft named them `..._in_topcard`, which that same
enumeration would never have seen.

**THAT GATE THEN CAUGHT THE FIRST R1 FIX BREAKING ANOTHER LANE'S GUARD.** Reported by type alone,
a failed press no longer said WHICH press failed, and
`tests/test_apply_modal_fixture.py::test_a_proceeding_gate_appends_the_second_click` proves the
apply flow's second click was attempted by finding that click's selector in `clicked.error` --
evidence that rode in the very library text the fix removed. The line is now composed from what
the package knows at the call (the type, the call's kind, the selector it built), which carries
the evidence without the call log, and the apply test passes unchanged.

### F.17 NOT run

- The full suite, locally, by the order. The shipped impact analyser selects 242 of 253 test files for
  this follow-up against master and 225 for the fix rounds alone -- the full suite by its own rule
  -- so each fix round's gate was a derived union, and 130 of 253 files were not in it (their names
  are in the scratch provenance). CI certifies on the orchestrator's push; nothing was pushed.
- A third warm re-check of `c79216d` (round three's two receipt checks and two refused letters): its
  worlds and mutations are this lane's own (F.13), not an independent verifier's.
- LIVE: nothing. Every row in F.12 waits on a person he names.
- RED IN THIS WORKTREE UNTIL THE MERGE: `tests/test_a_cited_sha_resolves.py` checks every commit this
  corpus cites against `master`, and this record cites four of this branch's own commits in the slots
  that guard reads. It reads them as not yet on `master` until the orchestrator's merge makes them
  ancestors of it -- a merge that keeps this branch's history; a squash would strand them.

### F.18 Commits -- on this branch, none pushed, no AI attribution in any

    a241623  (1 of n) the second door, Connect and Message from a profile he names -- source and fixture
    f132155  (2 of n) the route's tests, pins, census and baselines
    f246e89  (3 of n) the first supervised act records its own captures; five tests that can fail
    daf157f  (4 of n) the package docstring and the readonly function count
    cc8a509  the ONE integration: master 2eb90ad merged (F.15)
    149e787  (5 of n) the cold re-check's findings, fixed
    9d65c6f  (6 of n) the warm re-check's findings: no position in the press, strict presses
    c79216d  (7 of n) the second warm re-check: two blank letters, and receipts that re-check whose
    323857d  (8 of n) this record, `_audit/INSTRUMENTS.md` 69.11, the re-measured timings and
             the regenerated register
    749d90a  (9 of n) the two doc-guard reds the record's own gate raised: the proposed N 5 tool
             marked as proposed, and the regenerated register triaged as no correction
    (10 of n) this list brought up to date

## Integration: lane L5's merge of master 52b55b6

The orchestrator's order of 2026-09-27 20:00 IST: integrate master `52b55b6` (lane L8's `7986ae3`
and lane G's foundation) into this branch, keep the branch's history, adopt lane G's foundation,
and make five calls. Disk was sampled first and agreed with the order: the branch head clean
(`7fce01a`), master still `52b55b6`, and master's CI run for it green (Actions run 36325539823,
`success`, completed 14:28 UTC). The merge base was `2eb90ad`. One merge commit, no squash; its
parents are the branch head and master.

### I.1 The merge -- 21 files conflicted, and one auto-merged hunk was wrong

37 files changed on both sides. 21 conflicted, and every conflict was resolved by reading both
sides; 16 merged on their own.

- THE AUTO-MERGE THAT WAS WRONG. In `linkedin_server/writes.py` both sides appended a
  `_VERIFIED_FROM[...]` entry after `send_reply`'s -- this route's `message_from_profile` and lane
  L8's `withdraw_from_group`. Git kept the shared closing parenthesis ONCE, so this route's entry
  never closed: a `SyntaxError` in a region git reported as merged cleanly. Found by parsing every
  Python file after the resolution, not by reading the conflict list. It is the one non-conflict
  hunk edited by hand. Every other `.py` file in the tree parses.
- `writes.py`'s conflicts: master's click-error rule kept -- a failed press is reported by the
  exception's TYPE alone unless the refusal is this package's own -- which REPLACED this route's
  composed `describe_click_error` (the type, the call's kind and the selector). The rule is lane
  G's, ruled package-wide the same day for the same leak; the selector a caller could use is in
  `clicked.selector` anyway. The route's tests now read `TimeoutError` and `Error`.
- THE RETIRED REFUSAL, AGAIN. This route's two specs and two tool descriptions leaned on
  `delete_or_withdraw_anything`, which master retired on 2026-09-24
  (OUTWARD-CLASSES-BUILT-BEHIND-GRANTS) while this branch was forked -- the class
  `_audit/INSTRUMENTS.md` 80.6 names. Restated in master's form: `connect_from_profile` "NOT YET
  through this server; by hand, he can", onto `outward_classes`' `withdraw_invitation` (BLOCKED),
  as `send_invitation` is; `message_from_profile` "NOBODY: a delivered message cannot be recalled",
  as `send_message` is. The old sentences are quoted as retractions. `tests/test_writes_nine.py`'s
  restatement test names EIGHT specs now, and its whole-set twin read both new specs and both
  descriptions clean.
- Also restated in passing: a WriteSpec comment above `connect_from_profile` still said each
  control is "addressed by a position the page's own script computes" -- the position this
  route's second re-check removed. Stale since that re-check; three verification rounds read past
  it.
- `README.md`, `linkedin_server/__init__.py`, `server.py` and the count tests: both sides'
  histories kept, and every number measured on the merged registry (I.3).
- `tests/test_readonly_boundary_invariant.py`: both sides' re-freeze notes and pinned names kept
  (lane G's five tables, this route's three), and `<functions>` re-frozen (I.3).
- `tests/test_receipt_names_its_own_action.py`: both lanes' owned phrases kept, and each lane's
  rows read against the other's phrases ("Groups page", "Groups root"; "composer", "LinkedIn
  messages", "My Network") -- none holds another's.
- `tests/test_no_message_publishes_a_landing.py`: master retired `browser.py:goto`'s entry; this
  route's `readonly.py:assert_named_profile_url` entry stays, on `assert_read_url`'s ground (a
  gate refusing the address it was handed, before any navigation), not `goto`'s.
- `scripts/ci_shard_timings.json`: both sides' entries, totals re-derived: 183 files, 1727.1 s.
  The integration's one new test file is unpriced and is estimated at the mean rate.
- `_audit/RULINGS.md`, `_audit/INDEX.md`, `_audit/_census/blocker-map.tsv`: regenerated by their
  builders to a fixed point (67 rulings; the index and the map were already there).

### I.2 Lane G's foundation, adopted

- THE SEAM, SWAPPED (F.8's promise). `people_seam.person` now builds a `people_data.Person` and
  returns its envelope -- sanitised, capped, marked `untrusted_third_party_text`. Lane G wired the
  two conversation READERS to `people_data` directly, so the seam's `name` half had no callers and
  went, with its pending note. What is left is the ONE builder every write PREVIEW that names a
  person goes through: the named acts' `whom_this_resolves_to`, `send_reply`'s
  `who_this_would_reach`, and -- the order's last item -- `send_invitation`'s, which built its own
  record until now. Lane G's bounded-reader test declared the previews that build records behind
  the write door; its declared set moves from those two functions to `people_seam.person`, with a
  note.
- THE TWELVE SEAM TESTS PASS -- three properties by four outputs: invisible characters stripped,
  the cap, the untrusted marker ON THE RECORD (the reply's output was a plain sentence until lane G
  made it a record). The `xfail(strict=True)` markers are gone, so a regression is a plain
  failure.
- PREVIEW-NAMES-THE-RESOLVED-TARGET, on this route's two previews: the resolved name and headline
  travel inside the people record, and a headline the page does not draw is ABSENT -- `None`,
  never `""`. `people_data.Person.headline` now admits `None` for that (a change to lane G's
  module, stated here and in its docstring; `from_page` is unchanged). Receipts carry only the
  caller-supplied target: a message sent, its receipt, the grant store and the observation store
  are read for the owner's name and headline and hold neither, while the receipt names his link.
- A STATED LIMIT, pinned by a test rather than fixed: the topcard parser was measured on HIS
  profile, where one eligible line above Contact info is a headline. A third party's topcard that
  draws a location and NO headline therefore reads the location AS the headline. Nothing on the
  lines tells the two apart and no third party's topcard is captured (C-P1); the preview's CHECK
  IT covers it. A topcard drawing neither reads `None`.
- AND ONE DEFECT OF THE SAME DERIVED READING, FIXED. With nothing drawn above Contact info to be
  a headline, the parser fell back to the first eligible line ANYWHERE -- on the synthetic
  profile, the action buttons' labels, "Message Connect More", which its chrome list (measured on
  his own profile) does not know -- and the record would have printed them as the person's
  headline. Shown failing: the ABSENT test read exactly that. The namer now cuts the topcard's
  lines at its Contact info line before parsing (`named_profile._above_contact_info`), the
  separator the parser was measured against; his own profile's reader is untouched.
- LANE G'S GUARDS AGAINST THIS ROUTE'S CODE:
  - `tests/test_no_write_is_aimed_by_a_name.py`: the two target kinds classified, in two classes
    added to its closed vocabulary -- `profile_link_or_member_id` (`profile`) and
    `profile_link_or_member_id_and_own_text` (`profile_and_text`); "id" names no person and NAME is
    the word the parser refuses. Both tools are in `KNOWN_WRITE_TOOLS`.
  - The namer leaves through records, and THE READER-LEAK HARNESS NOW DRIVES IT THROUGH A REAL
    PAGE READ. Driven by signature alone, it was handed an observation built off the planted page,
    whose identity reading is never a confirmed identity, and took its first-line early return --
    recorded `clean` having read nothing. The harness gained an `AS_SHIPPED` variant: a planted
    page that confirms the named profile's identity and draws the plant as its owner, with the
    facts `observe` records there. Its verdict is `returns_records` -- the plant only inside the
    people record -- and `test_the_named_profile_namer_is_driven_through_a_real_read` holds that
    the signature variants alone read `clean`, so the verdict is the real read's work. The
    baseline was regenerated by its writer.
  - The synthetic people the route's fixture renders in a person slot -- the owner and the
    stranger in its rail -- are declared in `SYNTHETIC_PEOPLE`, the fixture guard's table.
    Not `INVENTED_NAMES`: that table's unused-entry rule requires a person-carrying constant to
    hold each entry, and no constant here does.
  - The mutation scanner counts this route's presses as `perform`'s: the package still has
    exactly one click and one fill call site, both in `perform`, and 15 sanctioned mutations
    (`tests/test_readonly.py`, `tests/test_writes.py`'s count of four mutating calls in the write
    module).

### I.3 Every pin, re-derived on the merged tree -- measured, never summed

| pin | master `52b55b6` | this branch | merged, measured |
|---|---|---|---|
| tools / read / write / write-shaped and refusing | 57 / 41 / 16 / 0 | 58 / 41 / 17 / 0 | 59 / 41 / 18 / 0 |
| tool parameters | 90 | 92 | 95 |
| sanctioned actions / performable | 17 / 16 | 18 / 17 | 19 / 18 |
| `PERMANENTLY_FORBIDDEN` | master's six | -- | master's six |
| `readonly.SANCTIONED_MUTATIONS` | 15 | 12 | 15 |
| pointer graph | 65 | 65 | 64 |

The pointer graph is the scar `git-merges-equal-pin-moves-as-one` names: both sides moved 66 to 65
by removing DIFFERENT pointers (lane L8's `M C63`, this route's `M M2`), git merged the literal as
one move, and the merged tree measures 64.

THE READ-ONLY FREEZE: sixteen digests. `<functions>` takes a value neither side had,
`bd677a42da1d190f`, and is ATTRIBUTED: the merged `readonly.py` minus the second door's three
functions (71 lines) hashes to master's `ff43e832d6f2b685` exactly; the three door names equal
this branch's, and the thirteen master pins equal master's. Controls: minus `is_read_url` hashes
to `2ecccd9f7752394d`; a name no function carries moves nothing.

THE CENSUS, `scripts/census_completion.py`, ten figures moved over master's pins, each measured
on the merged tree:

    capabilities_achievable 741 -> 742   out_of_scope 43 -> 42   achievable 727 -> 728
    adjudicated 179 -> 180   delivered_broad 117 -> 120   gap 591 -> 590   cannot_deliver 19 -> 18
    unfired 38 -> 41   gap_write 378 -> 377   b1_standing 15 -> 18

`M M1` (COVERED-CANNOT-DELIVER), `N 4` (GAP, by D6) and `N 2` (EXCLUDED-RULED, I.4) all
COVERED-UNFIRED; the three are W rows the write hold binds with no marker, so bucket 1 is 18
standing, 23 none, 7 released, of 41. `PINNED_B1_ROWS`' `OPERATOR-NAMES-THE-TARGET` carries all
three. GAP by slice: jobs 109, profile 187, messaging 131, network 163; stated rows 770.

### I.4 The five calls

- (a) `N 2` EXCLUDED-RULED -> COVERED-UNFIRED, built: `linkedin_connect_from_profile`. Its only
  ground, R4, is the one `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET` dissolved for a person he names;
  this APPLIES that ruling and adds no register entry. NOT-REV stays. The row's cell says so, its
  line left `exclusion-basis.tsv` (`check_exclusion_basis`: population 42, table 42), and it needs
  no write-classes line -- that table classes GAP rows, and `N 2` was never GAP.
- (b) THE STRICT-MODE COMMENTS. Master held seven such comments, not six (lane L8's
  `group_leave.py` added one), and a recording run found an eighth broken across two lines in
  `writes.py`. A `general-purpose` child ran every test that presses for the five actions they
  describe on a snapshot of master, with a plugin that counted each press's matches at the
  moment of the press: 76 presses, none counting 0 or 2+ -- `mark_company_interest` 6,
  `follow_company_page` 6, `update_profile_field` Save 12 and the badge switch 8,
  `withdraw_from_group` 16 and its leave item 9. `follow_company` was NEVER PRESSED in any test;
  its label-form control counts exactly one on each of its three captured postings, and its
  prefixed form, the one its comment describes, counts 0 on all 33 fixtures. NONE SHOWED MORE THAN
  ONE, so no comment was corrected to say strict mode is absent: all five actions now press
  strictly (`writes.STRICT_PRESS_ACTIONS`), each comment says since when, and the `follow_company`
  one says its strictness is by construction, not by a measured press. FILLS ARE NOT IN IT: only
  the named acts' fill was measured strict. `tests/test_a_strict_mode_claim_is_a_strict_press.py`
  holds the set, the call arguments and every claim-shaped sentence together, shown failing both
  ways, and through the real call a second OFF control drawn mid-press stops the
  `mark_company_interest` press with `Error` while the same world without the membership is
  pressed.
- (c) The two open gaps, accepted as written for supervised first acts: nothing built; the custom
  selector engine waits.
- (d) `tests/test_selectors_resolve.py`'s repeated `settings_radio_label_selector` key: the second
  entry is keyed `settings_radio_label_selector[Device settings]`, the fixture page draws a
  standalone "Always on" label (bound to nothing, so the role test's single radio stays single),
  and `test_build_all_names_every_selector_once` convicts the file with the key put back. The AST
  duplicate-key scan over every dict and set literal in `linkedin_server/`, `tests/` and
  `scripts/`, shown failing on its own plant first, found exactly two: this one, and
  `tests/test_api_call_sites.py`'s `_FETCH_NAMES`, a SET repeating `"urlretrieve"` -- harmless
  (a set overwrites nothing), on master since 2026-08-24, and not this lane's; left.
- (e) No model-id line added. This record still opens with one: it is one of the 19 lane G is
  removing on its branch.

### I.5 A finding for other owners: the suite reaches LinkedIn

The recording run in (b) logged every non-local request its browsers made: four went to
`https://www.linkedin.com`, from `tests/test_verification_that_could_not_read.py`. The whole
suite, run with the guard below, measured the full count: ELEVEN tests in TWO files -- those
four, and seven in `tests/test_apply_modal_fixture.py`. Each presses the apply anchor of a job
posting capture (`tests/fixtures/job_detail.html` and its siblings), whose href is LinkedIn's,
and a fresh headless Chromium starts that navigation -- no cookies, no profile, never port 9224,
but a request to LinkedIn, on every run of those files, locally and in CI.
`tests/conftest.py` opens "No test in this suite reaches the network or an account"; the first
half is false for those eleven tests. NOT FIXED HERE -- it is shared test infrastructure, and the
fix belongs where the fixtures are served (a route that aborts non-local requests in the shared
browser fixtures would make the sentence true).

What this lane's own gates did instead: a scratch pytest plugin gives every Playwright context a
route that lets loopback, `data:`, `about:`, `blob:` and `file:` through and ABORTS and records
everything else before it leaves. Shown working first, outside any test: a page's request to
`https://www.example.com/` aborted and recorded, a loopback request passed through. In the
whole-suite run it aborted exactly the eleven requests named above and nothing else, and every
one of the eleven tests passed with its navigation aborted.

### I.6 Gates

- THE WHOLE SUITE, on the merge commit, locally, `-n auto --dist loadfile`, with the I.5 guard:
  11160 passed, 2 failed, 9 skipped, 1 xfailed -- 11172 tests in 267 files -- in 1362 s of
  wall clock. The eleven navigations to LinkedIn were aborted; no other request tried to leave.
  - RED BY DESIGN: `tests/test_a_cited_sha_resolves.py::test_no_new_unresolvable_citation_appears`,
    on this record's four branch commits in eight citation slots, and on nothing else. It stays
    red until master carries them -- the order's merge, keeping this branch's history, makes them
    ancestors of master; a squash would strand them. This section cites none of its own commits
    in a slot that guard reads.
  - RED AND THIS LANE'S OWN, since the follow-up's first build:
    `tests/test_the_search_shape_reading.py::test_the_shape_pass_adds_no_evaluate_waiver` caps
    `dom.py`'s `# readonly-ok` evaluate waivers at 22 -- a second copy of the ceiling in
    `tests/test_readonly.py`, which the follow-up moved to 23 for `dom.read_named_profile` with
    its argument. The follow-up's gates were hand-derived lists, and this file was not in any
    (F.17 names 130 files outside them). Measured: 22 at the base, 23 on the branch, 22 on master,
    23 merged, and the one waiver master lacks is `read_named_profile`'s. The copy now reads 23,
    and says whose the twenty-third is and that the shape pass still adds none.
- The whole suite again on the commit that carries that fix, the same way and under the same
  guard: 11161 passed, 1 failed -- the cited-SHA guard, by design, and nothing else -- 9 skipped, 1 xfailed; 11172 tests in 267 files, in 1725 s of wall clock (the box's load was not measured). The same eleven navigations to LinkedIn were aborted, and nothing else tried to leave.
- Before the merge commit, three focused runs on the resolved tree: 40 files (7 failed and one
  file's collection errored -- each fixed above); 19 files with the I.5 guard (1395 passed, 2
  failed: the ABSENT-headline test before the Contact info cut); 3 files with the guard (674
  passed).
- The census battery on the merge commit, twelve instruments, all green:
  `census_completion --check` (every figure matches its pin), `count_census_states --expect
  J=109,P=187,M=131,N=163` (GAP 590), `check_read_addresses` (104 of 104),
  `check_write_classes` (385 lines), `check_exclusion_basis` (42 of 42), `ruling_holds`,
  `pin_census_rows --check` (770 rows), `measure_pointer_graph --check` (64),
  `check_gap_rows_on_refused_addresses`, and the three derived views --
  `build_blocker_map --check`, `build_rulings_index --check` (67 rulings) and
  `build_audit_index --check` (257 documents).
- The document guards run inside the whole suite: every one green but the cited-SHA guard above.
- Parse and repeated-key checks over the merged tree: every Python file parses; the AST scan over
  every dict and set literal and every module-level keyed assignment finds only
  `tests/test_api_call_sites.py`'s harmless set (I.4 (d)); no JSON file repeats a key.

### I.7 NOT run

- CI. Nothing was pushed, by the order; CI certifies on the orchestrator's push.
- The whole suite WITHOUT the I.5 guard -- deliberately: eleven of its tests would send a browser
  to LinkedIn. How those eleven behave with the navigation live, as CI runs them, was not
  measured here; aborted, all eleven pass.
- LIVE: nothing. Every named-person act waits on a person he names (F.12).
- An independent cold verification of this integration: not ordered, and not run; every check in
  this section is this lane's own.
- The integration's new test file is unpriced in `scripts/ci_shard_timings.json`; the sharder
  estimates it at the measured mean rate.
- The standalone "Always on" label in `tests/test_selectors_resolve.py` proves the selector FINDS
  a label; whether a label is bound to its radio is `tests/test_radio_label_binding.py`'s
  question, unchanged.

### I.8 Commits -- on this branch, none pushed, no AI attribution in any

    02f95eb  the merge of master 52b55b6 (parents: the branch head and master): conflicts
             resolved, lane G's foundation adopted, the five calls applied, every pin re-derived
    99eef0f  the waiver ceiling's second copy, and this record's gates
    (next)   this record's last gate paragraph and this list

## Integration 2: lane L5's merge of master b6993e5

The orchestrator's order of 2026-09-27 22:32 IST: master moved on purpose, to `b6993e5` (lane G's
residuals, `ae24426`, and the live lane's session-2 preparation); finish the running gate, then
merge the new master once more. Disk was sampled first and agreed: master `b6993e5`, its CI run
36334801033 `success` (completed 17:00 UTC), and this branch's head descending from the first
merge. The first merge's gate had already finished (I.6: both whole-suite runs). The merge base
was `52b55b6`. One merge commit, history kept.

### J.1 Seven files conflicted

- `linkedin_server/people_data.py`: MASTER'S, WHOLE. Lane G made the ABSENT convention the
  record's own -- `people_data.ABSENT` (`None`) where no reading drew a headline, and a headline
  that was read sanitised, which may come back `""`, drawn empty. The first merge's admission of
  `None` into `Person.headline` is superseded by it.
- `linkedin_server/people_seam.py` (merged without a conflict, then edited): the seam now passes
  what its caller READ and adds no rule of its own. Until this merge it also turned `""` into
  `None`, which erased the difference lane G's records keep. The named previews still read
  `None` where a topcard draws no headline (the parser answers `None`, and the first merge's
  Contact-info cut keeps the buttons out), so the order's item 3 holds: null when not drawn,
  never `""`.
- `linkedin_server/threads.py`: MASTER'S reply preview, WHOLE. It reads the line the header
  draws under the title and returns a GROUP conversation as its title record
  (`threads.conversation_with`) -- a shape a person builder does not make -- so the reply no
  longer goes through the seam; its import and this branch's docstring sentence reverted to
  master's. Its record is still held to mitigation 2 (`tests/test_people_seam.py`, section 3).
- `linkedin_server/writes.py`: two independent additions at one place -- this route's
  `NAMED_PROFILE_ACTIONS`, `STRICT_PRESS_ACTIONS` and `_load_named_profile` beside the live
  lane's `_read_account_share_updates` -- both kept; and in `perform`, the account-setting
  reading (editor writes only) runs first, then this route's named-profile door or the read
  door, as each side wrote it.
- `tests/test_a_people_reader_reads_one_page.py`: `PREVIEW_BUILDERS` is what the derivation
  MEASURED on the merged tree -- `people_seam.person` (the named previews and the invitation's),
  `threads.name_the_reply_recipient` and `threads.conversation_with` -- not a hand union.
- `tests/test_readonly_boundary_invariant.py`: both sides' notes kept, master's first, and a
  check note. Sixteen digests, NONE NEW: `_ALLOWED_URL_PATTERNS` `18e5958586c2c367` and
  `_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS` `14f567fd160048a8` are master's (the live lane's
  admission), `<functions>` `bd677a42da1d190f` and the door's three are this branch's, and the
  merged tree minus the door's three functions still hashes to master's `ff43e832d6f2b685`.
- `scripts/ci_shard_timings.json`: both sides' entries, totals re-derived: 186 files, 1810.6 s.
- `_audit/RULINGS.md`: regenerated to a fixed point, 67 rulings.

### J.2 The order's items

- THE PILL SELECTOR, as lane G's record asks: `threads`' list reader reads its pills inside the
  ONE filter bar -- `dom.FILTER_BAR_SELECTOR`, then `dom.FILTER_PILL_IN_BAR`, the scoping the
  activator presses by -- and a page drawing no bar or two reports none.
  `test_the_list_reads_pills_only_inside_the_one_filter_bar`: a hooked button planted outside the
  bar is not counted (the page-wide selector counts six), and two bars read no pills.
- NO MODEL-ID LINE: this record's first line is its title. Master removed the line and the
  merge kept master's; lane G's guard for it runs in the whole suite.
- THE BOUNDARY COUNTS, measured: 55 allowlist patterns (the live lane's +1), 33 forbidden
  substrings, 4 pattern exemptions, 15 sanctioned mutations.
- EVERY OTHER PIN, re-derived on the merged tree and unmoved: 59 tools (41 read, 18 write, 0
  refusing), 95 parameters, 19 sanctioned and 18 performable actions -- master added no tool;
  the census battery, all twelve, with every headline figure at its pin and GAP by slice
  109 / 187 / 131 / 163; the pointer graph at 64; the three baselines regenerated by their
  writers with no change. The AST duplicate-key scan finds only the old harmless set.

### J.3 Gates

- THE WHOLE SUITE on the second merge commit, locally, `-n auto --dist loadfile`, under the I.5
  guard: 11384 passed, 2 failed, 9 skipped, 1 xfailed -- 11396 tests in 271 files -- in 1077 s of wall clock. The two reds: the cited-SHA guard, by design, on the same four branch commits and nothing else; and `tests/test_tracker_readiness.py::test_an_empty_tab_is_not_delayed`, a real-browser wait bounded at 300 ms that read 319 ms under the full parallel load. That file passed alone three times of three (60 tests); it is unchanged since `52b55b6`, and so is the function it waits on, `dom.wait_for_tracker_list` (compared by source); both whole-suite runs of the first integration passed it. A timing bound, not this merge -- stated, not fixed. The same eleven navigations to LinkedIn were aborted, and nothing else tried to leave.
- Before it, on the resolved tree: 25 affected test files under the same guard, 1983 passed, no
  request left.
- The census battery on the merge commit, the same twelve instruments as I.6, all green, the
  three derived views among them (67 rulings; 258 documents).
- Parse and repeated-key checks: every Python file parses; the AST scan finds only the old
  harmless set.

### J.4 NOT run

- CI: nothing pushed. The whole suite WITHOUT the I.5 guard, for I.5's reason.
- LIVE: nothing.
- An independent verification of either integration: not ordered, not run.
- `focused` and `other` remain in `linkedin_open_messaging`'s permitted set though they can never
  be activated on the measured page; lane G's record leaves that to the tool's owner, and this
  order did not ask for it. Left as it is.

### J.5 Commits -- on this branch, none pushed, no AI attribution in any

    02f95eb  the merge of master 52b55b6 (Integration, I.1-I.5)
    99eef0f  the waiver ceiling's second copy, and I.6
    eafc6e9  I.6's last run, I.7 and I.8
    d4b3b90  the merge of master b6993e5 (Integration 2, J.1-J.3's first form)
    (next)   J.3's whole-suite result, J.4 and this list

## The name-aimed debts: the orchestrator's order of 2026-09-27 23:36

The order, in its own words: "Convert both debts so NO write is aimed by a name" --
`linkedin_send_invitation` (N 1) is to "aim by the caller-supplied profile link or member id,
compared inside the page against the card's own profile link, never against its name";
`linkedin_send_message` is to be "either aim[ed] the same way ... or retire[d] in favour of
`linkedin_message_from_profile`. The choice is yours; argue it in your record." Both leave lane
G's debt list, whose test "must pass with no debt entries left"; the receipts stay
caller-target-only; every pin, count and census cell the moves touch is re-derived. Item 2:
`focused` and `other` leave `linkedin_open_messaging`'s accepted values and schema.

Disk was sampled first and agreed with the order: HEAD = master = `687b07c`, CI run 36338770074
`success`, a clean tree.

### K.1 Item 2: the folder's choices are not filter values (`0f6bb24`)

`dom.MESSAGING_FILTERS` holds the five pills -- `unread`, `jobs`, `connections`, `inmail`,
`starred` -- and `message_filter` is a `Literal` of those five and `""`, so the registered schema
carries the enum. The value is checked before any page loads. `focused` and `other` are the
FOLDER dropdown's choices on the measured page (lane G's record, R.2), which lane G's bar scoping
already refused on every page. `tests/test_the_folder_choices_are_not_filter_values.py` holds the
set, the schema's enum, the description, a refusal before a session opens -- and its control,
`inmail`, entering one, so the fake that records entry is shown able to see it -- and the
activator's refusal before a locator. Census `M M33` notes it; no state moves.

### K.2 `send_invitation`: aimed by the person's profile link (`f099461`)

THE NEEDLE IS GONE. `linkedin_send_invitation(profile, confirm_token)` takes the person's
profile link (or member id). `_target_for` parses it with the named-profile parser, so a bare
word -- which could be a name -- is refused before a browser opens, and the refusal repeats
nothing.

MEASURED FIRST, offline, over the 95 captures on disk, counts and shapes only: 52 controls wear
the invitation suffix. The 32 on his own profile's suggestion rail (four captures of `/in/me/`,
eight each) each sit in a card -- the nearest ancestor holding any `/in/` link -- that holds
EXACTLY ONE member segment and EXACTLY ONE control, the link's text naming the person the control
names; all 32 are VANITY links, none a member id. The eight on people search are anchors carrying
their own `href`, and are not this route.

THE AIM is `dom.rail_invite_control_selector(segment)`: XPath the browser evaluates -- the
invitation button whose card links to that segment and to no other segment, and holds one such
button. The segment is ASCII-folded on both sides (vanity segments are case-insensitive), cut at
`/`, `?` or `#`, and refused unless it is letters, digits, hyphens, underscores or
percent-encoded octets, so nothing can close the expression. Run over the 16 captures holding
invitation buttons: 44 of 44 matched exactly one element, the card's own control; upper-cased,
44 of 44; a segment no card carries matched none on all 16.

`dom.read_invitation_rail` runs NO SCRIPT: two locator counts. `INVITE_NEEDLE_JS`,
`read_invitation_surface`, `invite_control_selector(index)` and `writes.aim_invitation` left.
`writes.aim_invitation_by_link` answers AIMED only for exactly one card; two are AMBIGUOUS and
refuse ("choosing either would be choosing by position"); none says so and, for a MEMBER ID,
says why -- the rail's cards carry vanity links, 32 of 32 -- and names
`linkedin_connect_from_profile`, which loads the profile an id names. No answer repeats the
link. The press is the selector the gate counted, pressed STRICTLY (`STRICT_PRESS_ACTIONS` gains
`send_invitation`). The preview names whom the link selected as a people record -- the label's
name, sanitised and marked; the link HIS; the headline ABSENT, because the rail card's headline
has never been captured. The grant and the receipt carry only his link, nothing the page drew.

`tests/test_an_invitation_is_aimed_by_a_link.py`, 24 tests in a real headless Chromium over
synthetic rail cards whose buttons record their own presses: one aim; a relative link with a
query; the fold on each side; no card; a member id; two cards; a card holding two people's
links; a card holding two controls; a control in no card; the reader runs no script and returns
only numbers; the builder refuses seven shapes; a bare word is refused before a page opens; his
link is compared and never navigated to; end to end, the press lands on his card and the receipt
names his link and no name; and a SECOND CARD drawn while the press waits stops the strict press,
where the same world pressed without strictness lands on the card drawn FIRST -- not his. That
pair was written the other way first and went red, and the red is the finding: a redraw that
only ADDS a card leaves the pressed element connected, Playwright keeps its handle, and
strictness never gets a second look. The redraw has to detach it.

`tests/test_needle_never_escapes.py` keeps its name and its ruling -- his target may live in a
grant, never in an exception or a log -- on the link. ITS LOG HALF COULD NOT FAIL FOR A DEBUG
LINE: it set DEBUG on a logger called `linkedin_server`, which nothing logs through; the package
logger is `linkedin`, at INFO, so every debug line was dropped before capture. The rewrite's
first control ("was the unreadable rail logged at all?") read an empty channel, which is how it
surfaced. It now sets DEBUG on `config.logger.name`, proves the channel hears DEBUG with a control
record, and drives the rail reader over a page whose library error QUOTES the selector -- the one
route by which the segment could come back -- which keeps only the error's type.

FOUND, NOT FIXED (outside this order): 12 more `caplog` sites set DEBUG on the ROOT logger, and
the package logger stays at INFO under all of them, so their absence checks cannot fail for a
DEBUG-level record -- `tests/test_a_preview_names_the_resolved_target.py` 2,
`tests/test_auth.py` 3, `tests/test_auth_reason_withholds_the_request.py` 4,
`tests/test_leakwalk.py` 3. The conftest fixture attaches the handler and leaves the level; one
line there, or the logger's name at each site, closes it.

Lane G's `tests/test_no_write_is_aimed_by_a_name.py` went red on this commit exactly as designed
-- "send_invitation is no longer aimed by a name. The debt is paid: delete its NAME_AIMED_DEBT
entry and its DEBT_PARAMETERS pair" -- and both went. `rail_profile` is classified
`profile_link_or_member_id`, and the controls that leaned on the real debt entries now fail on
plants, so they keep failing whether the table holds one entry or none. Census: `N 1` keeps
COVERED-UNFIRED and its note records the aim; `N 5` and mcp-inventory `34` note the signature.

### K.3 `send_message`: retired, and why not re-aimed

A RE-AIM NEEDS A ROUTE TO THE COMPOSER THAT IS NOT THE TYPEAHEAD, and there is exactly one: the
composer addressed by identifier,
`/messaging/compose/?profileUrn=urn%3Ali%3Afsd_profile%3A<id>&recipient=<id>`. The read boundary
ADMITS it -- `readonly._ALLOWED_URL_PATTERNS` has carried it since 2026-09-03, and
`assert_read_url` admits it, measured today. It cannot do the part the order asks for. It is
addressed by the member ID alone, which a profile link does not carry, so a caller holding a
link -- the form every profile and every rail card draws -- cannot use it without first loading
the profile. And whom it addressed could only be confirmed on the committed recipient, which no
instrument here has ever observed: the four chip spellings in `dom.RECIPIENT_CHIP_SELECTORS`
have never matched anything, and no capture shows that composer with a recipient in it. A re-aim
would type his words into a composer whose addressee nothing can confirm -- the precondition the
retired recipient gate refused on, every time.

THE CAPABILITY ALREADY EXISTS WITHOUT ANY OF THAT. `linkedin_message_from_profile` reaches a
person by their PROFILE LINK, presses that profile's own Message control so LinkedIn sets the
recipient, types only when exactly one empty composer opened in a conversation titled with that
person's name (compared in the page) and the profile reads '1st', and confirms SENT by a delta.
For somebody he already talks to, `linkedin_send_reply` fixes the recipient by thread id. The
retired tool never sent: a typed name commits nobody (2026-09-03), and every refusal left the
name sitting in his composer. SO IT IS RETIRED. One limit carried forward rather than hidden:
`linkedin_message_from_profile` accepts a member id and loads `/in/<id>/`, and whether LinkedIn
serves that address without redirecting to the vanity one is unmeasured -- a redirect vetoes the
act (`named_profile.landed_on_profile`). For a caller holding only an id, the identifier-addressed
composer is the route a later build would take, after its capture.

THIS ARGUMENT ONCE STOOD ON A BOUNDARY CLAIM THAT DID NOT HOLD. Section 3.1 of this record and
census `M M6` said the identifier address was one "the read boundary refuses on purpose". It had
been admitted the same day as the reading that said so; both places now carry the measurement
(`M M6`'s cell, and a line under 3.1). The argument above does not rest on the boundary.

WHAT WENT, measured before the cut -- an AST walk of every use in `linkedin_server/`, `scripts/`
and `tests/` (`np_reach.py`, `np_dom_graph.py`, `np_dangling.py`) of what nothing reached once
the write path was gone:

- `server.py`: the tool; its `_WHY_NOT_PERFORMED` entry; every sentence describing it as live --
  the instructions now name it RETIRED and point to `linkedin_message_from_profile`, and their
  surviving cost is the invitation's (it does not open `/mynetwork/`).
- `writes.py`: the spec; the `member_and_text` kind; its PERFORMABLE and TYPING entries; its
  anchor, click-time and verification branches; `ADDRESSED_TYPING_ACTIONS` and `perform`'s
  branches for it; `_typeahead_gate`, `_recipient_gate` and `_send_gate`;
  `_read_messaging_badge` and its surface entry; `_subject_component_of`, whose one reason was
  this action; the receipt's `typeahead_clicks`, `typeahead_gate` and `recipient_gate`.
- `dom.py`: `SELECTED_RECIPIENT_JS` and `read_selected_recipients`, the typeahead family
  (`TYPEAHEAD_OPTION_SELECTORS` through `read_typeahead_options`), `read_compose_send_state`,
  `compose_body_selector`, and `read_messaging_badge` -- whose one shipped caller was this
  action's preview; `tests/test_reader_reachability.py` deletes a dom reader no tool reaches
  rather than parking it, and the two probes that still read the badge carry the same two reads
  locally.
- `threads.sent_in_place`, which nothing called.
- `scripts/_probe_typeahead_commit.py`, the mutating probe that measured the typeahead dead -- it
  drove this spec's `_live_control` and `_typeahead_gate` -- with its test, and the four test files
  of the retired gates: `test_send_message_gate.py`, `test_typeahead_gate.py`,
  `test_click_is_not_its_own_evidence.py` and `test_the_needle_is_matched_as_a_bare_substring.py`.
  What they measured is kept in `_audit/2026-09-03-typeahead-name-matching-is-dead.md` and in git.

WHAT STAYED, because a read still uses it: `compose_recipient_selector` and
`compose_send_selector` (`read_thread_reply_surface` counts them) and their labels,
`RECIPIENT_CHIP_SELECTORS` (the messaging census probe), `read_compose_fields` and
`read_compose_modes` (`linkedin_compose_fields`), the identifier-addressed composer on the read
boundary, and `WriteSpec.click_from_state` -- no spec sets it now; the mismatch it names belongs to
any action whose preview and click read different surfaces.

THE NAME WENT BACK ON THE FORBIDDEN LIST. `tests/test_writes.py`'s conservation law accepts only
one way off `SANCTIONED_WRITES` -- back onto `FORBIDDEN_TOOLS`, visibly -- and
`linkedin_send_message` is there again; `test_send_message_is_retired_and_its_name_is_forbidden_again`
pins the whole retirement. Lane G's debt table is EMPTY and pinned empty (`test_no_debt_is_left`);
`member_and_text` left its classification; the file passes with no debt entries.

### K.4 Pins, counts and census cells -- each re-derived by its instrument

| what | before | after | how |
|---|---:|---:|---|
| tools | 59 | 58 | `mcp.list_tools()`; three surface pins moved with it, the test renamed `..._fifty_eight_tools`; 58 on the merged tree too (K.8) |
| parameters | 95 | 92 | the tool-surface pin (`member`, `text`, `confirm_token` left; `member` -> `profile` moves no count); 93 on the merged tree, with lane S's `include_names` (K.8) |
| write tools / sanctioned / performable | 18 / 19 / 18 | 17 / 18 / 17 | the server docstring's derived split, README, `__init__`, the hand-typed lists |
| strict-press set | 7 | 8 | `send_invitation` joined, pinned by name |
| executed scripts | 24 | 22 | `INVITE_NEEDLE_JS` (K.2), `SELECTED_RECIPIENT_JS` (K.3) |
| `dom.py` evaluate waivers (ceiling) | 23 (23) | 21 (21) | the ceiling brought down to the count |
| name-aimed debt entries | 2 | 0 | pinned empty |
| error-url feeder sites | 20 (+12 out of scope) | 19 (+10) | three dom sites left |
| tab-leaking probes | 39 | 38 | the deleted probe was one |
| decorative-control ratchet | 134 | 132 | its two entries |
| CI shard timings | 186 files, 1810.6 s | 181, 1760.8 s | the five deleted files' entries |
| reader-leak baseline | -- | -9 readers | regenerated by its writer, under the offline guard; the RETURNS_TEXT inventory shrank by four |

Census, every figure measured by `scripts/census_completion.py` on this tree and re-pinned with
the line saying what moved it: `M M2` COVERED-CANNOT-DELIVER -> GAP (its only tool retired; classed
R2 in `write-classes.tsv`, queued on capture C-P5, as `M M6` is); `N 155` COVERED-CANNOT-DELIVER ->
COVERED-UNFIRED (the same capability as `M M1`, on `linkedin_message_from_profile`, never fired;
pinned in bucket 1 under OPERATOR-NAMES-THE-TARGET); `M M1`, `J 128` and mcp-inventory `35`
re-pointed with no state move (`M M1` also says its Message control is pressed by the topcard
selector, strictly -- not by position, as its older sentence still read). So: adjudicated
180 -> 179, delivered_broad 120 -> 121, gap 590 -> 591, cannot_deliver 18 -> 16, unfired 41 -> 42,
gap_write 377 -> 378, b1_standing 18 -> 19; GAP by slice J 109, P 187, M 132, N 163. On the
merged tree (K.8) the same moves sit on lane S's: gap 588, unfired 45, adjudicated 182,
delivered_broad 124, cannot_deliver 16; N 160.

### K.8 The merge of master 64afa6c

The order: "Integrate the then-current master once at your end." Master had moved from `687b07c`
to `64afa6c` -- 18 commits: lane S's people search returning WHO (`include_names`, three census
rows), and lane G's network guard (no test reaches the network), its earned-clean reader rule,
the CI timings rebuilt from run 36338770074, and its record. One merge commit, history kept.

THREE FILES CONFLICTED, each resolved by what the instrument measured on the merged tree:

- `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py`: master's two re-pin blocks, then
  this branch's, then 58 tools and 93 parameters -- measured off the merged registry (master's 59
  and 96 carry lane S's `include_names`; this branch takes one tool and three parameters).
- `scripts/census_completion.py`: master's comment lines, then this branch's, then the value the
  instrument measured on the merged tree, never summed: adjudicated 182, delivered_broad 124, gap
  588, cannot_deliver 16, unfired 45. The figures git merged without a conflict (gap_write 378,
  b1_standing 19, the bucket-1 rows with `N 155`) were checked by the same run: every headline
  figure at its pin.
- `scripts/ci_shard_timings.json`: MASTER'S table -- regenerated from a green CI run by its writer
  -- less the five files this branch deleted, `_files` and `_total_seconds` re-derived (271 -> 266,
  3258.6 -> 3113.6 s) and the provenance line saying so.

ONE MORE CHANGE THE MERGE NEEDED, found by the reference scan rather than by a conflict: lane G's
reader-leak harness drove the invitation namer through an as-shipped variant that answered
`dom.INVITE_NEEDLE_JS`, which this branch removed. The variant now answers the rail's two locator
counts with one card and the label with the plant, every read through the planted page, and its
observation carries the canonical profile link the server would have observed;
`test_the_preview_namers_are_driven_to_the_records_they_build` passes for both namers. The three
baselines, regenerated by their writers under the offline guard on the merged tree, came back
byte-identical to what git merged: a fixed point.

On the merged tree: every Python file parses; the AST duplicate-key scan finds only the old
harmless `urlretrieve` pair; the census battery, all twelve, is green -- GAP 588, by slice J 109,
P 187, M 132, N 160 -- with 67 rulings and 258 documents in the derived views.

### K.5 Gates

- THE WHOLE SUITE, on the merge of master 64afa6c (its hash is in K.7): the impact gate's plan
  widened to it (86 changed
  paths since `687b07c`, one of them `tests/conftest.py`, which the analyser has no model of), so it
  ran whole -- locally, `-n auto --dist loadfile`, in the background, under the `np_offline`
  plugin: 11364 passed, 8 failed, 9 skipped, 1 xfailed -- 11382 tests -- in 1094 s. Two requests
  tried to leave, and both were the planted ones of lane G's own guard tests, to the synthetic host
  `network-guard-plant.invalid`; nothing else did.
- THE EIGHT: two are lane G's guard testing ITSELF -- `test_a_planted_request_is_refused_before_it_leaves`
  and `test_a_context_the_test_opens_itself_is_guarded_too` assert that THEIR guard aborted the
  request, and `np_offline`'s route aborted it first. Run without the plugin, under G's guard
  alone, `tests/test_no_test_reaches_the_network.py` passes 17 of 17. The other six were this
  order's own moves reaching instruments that pin them, each fixed at the instrument in the final
  commit: the write-class split (R2 36 -> 37, `M M2`), the messaging slice's GAP split (131 -> 132),
  `M M2`'s cell naming its blocker (the triage instrument reads `Blocker:`), the contingent
  write-offs' pinned exemption for `M M2` (self-retired: the row left COVERED-CANNOT-DELIVER), and
  one test borrowing an invented name the retired tests had held.
- THE CONTROL SCRIPT this order re-pointed, `scripts/_check_the_refusing_grant_can_fail.py`, was
  RED on its first re-point: section 3's subject `writes._live_control` did not go red under the
  plant, because no shipped reader hands a raw page reading to `coerce.as_count` any more -- the
  script's own sweep found none. Its subject is now the retired gate's SHAPE, built in the script:
  red under the plant, back to its pre-plant verdict after. All five sections pass.
- THE FINAL COMMIT'S DELTA, impact-gated: see K.9.
- THE CENSUS BATTERY on the merged tree, all twelve instruments green (K.8), and again on the final
  tree (K.9).

### K.6 NOT run

- CI: nothing pushed, as ordered.
- The whole suite WITHOUT `np_offline`: only lane G's guard-test file was run without it (17
  passed); lane G's guard now keeps every test on the machine, and the order asked for the plugin.
- `scripts/impact_gate.py` executing its own run: its plan was computed and read, and the run it
  called for was made through `np_offline` instead.
- LIVE: nothing. The two probes this order edited (`_probe_events_home_live.py`,
  `_probe_notify_cost_precondition.py`) and the retired typeahead probe drive a signed-in browser
  and were not run; the edits are held by the import-safety and static probe tests.
- An independent, cold verification of the link aim or of the retirement: not ordered, not run.
- The 12 `caplog` sites that cannot hear a DEBUG record (K.2): found, not fixed.

### K.7 Commits -- on this branch, none pushed, no AI attribution in any

    0f6bb24  item 2: the folder's choices are not filter values
    f099461  item 1a: send_invitation aimed by the person's profile link
    930e96c  item 1b: send_message retired; the debt list empty; pins, census, this section
    7d3d023  the merge of master 64afa6c (K.8)
    a5135be  the final run's six instrument consequences, the control's subject, K.5-K.7
    795adc5  the two findings of the whole suite on a5135be, both in this order's prose (K.9)
    (last)   K.9's gate results -- this file only, gated by its own plan (K.9)

### K.9 The final delta

- THE WHOLE SUITE on `a5135be`, the tree K.5 left: 11368 passed, 4 failed, 9 skipped, 1 xfailed --
  11382 tests -- in 1224 s, under `np_offline`; the two requests that tried to leave were lane G's
  planted ones again. Two of the four are lane G's guard testing itself (K.5). The other two were
  this order's own prose, each caught by a corpus guard:
  - `M M2`'s cell named its blocker as a backticked capture id in a blocker slot, and
    `tests/test_an_asserted_name_resolves.py` resolves such a name against the gap-blockers
    ledger, which holds no capture ids. The cell now names the capture in words; the triage
    instrument still reads its `Blocker:`.
  - K.5 cited this branch's merge by its hash in a commit slot, and
    `tests/test_a_cited_sha_resolves.py` asks for ancestry of master, which a branch commit has not
    got until the branch merges. The sentence now names the merge by what it merged; K.7's list,
    which no slot reads, keeps the hashes.
  Before that fix was committed, the six instruments its lines reach: 120 passed.
- THE IMPACT GATE on the commit that fixed them: two changed paths selected 138 of 270 test files
  (51%), over the analyser's 45% line, so it WIDENED to the whole suite -- run locally, in the
  background, `-n auto --dist loadfile`, under `np_offline`: 11370 passed, 2 failed, 9 skipped,
  1 xfailed -- 11382 tests -- in 1670 s. The two failures are lane G's guard testing itself, as in
  K.5, and the two requests that tried to leave were its planted ones, to
  `network-guard-plant.invalid`; nothing else did. Run alone without the plugin, under G's guard,
  `tests/test_no_test_reaches_the_network.py` passes 17 of 17 on the same tree.
- THE CENSUS BATTERY on that commit, all twelve green: every headline figure at its pin; GAP 588,
  by slice J 109, P 187, M 132, N 160; 386 write-class lines (R1 16, R2 37, R3 333), every class
  derived and every citation resolving; 101 of 101 bucket-3 rows agreeing with the live boundary;
  42 exclusions traced; 64 pinned pointers holding; and the derived views' `--check`s matching --
  the blocker map, 67 rulings, 258 documents.
- THE COMMIT CARRYING THIS PARAGRAPH changes this file and nothing else. Its own impact plan and
  that plan's result are in the report that returns the head sha: a record cannot hold the gate of
  the commit that writes it.

## The read he names: the orchestrator's order of 2026-09-28 08:06, and its addendum of 08:43

**THE ORDER.** The operator ruled YES on reading a profile he names (08:01, verbatim: "Yes, I'm
giving you permission."). Copy his ruling's document into `_audit/`, register it, build a read tool
over this lane's named-person door -- `profile` (a link or member id) and a `confirm_token`, behind
the single-use grant; a preview naming the resolved member and stating that LinkedIn may show that
member the view; on confirm, one load and the declared fields as people records, name, headline and
the groups `N 178` needs -- ABSENT where no capture shows them; one page per call, nothing stored,
never aimed by a name, `PERMANENTLY_FORBIDDEN`'s third-party entry narrowed to exactly this; `N 178`
moved only if its section is captured, else a capture spec for the live lane's session 3.

**THE ADDENDUM (08:43).** Measured live that morning: `linkedin_message_from_profile` was REFUSED
on a first-degree profile the operator named -- the preview's reading came back `unknown`, and
nothing was pressed or sent. `dom.read_named_profile`, built over an invented page, was not
live-true. The live lane took one skeleton of that profile; rebuild the reader and its topcard
selectors over it, keep every refusal, keep the invented page as the secondary case and say which is
live-true, and build the read over the same reader.

Disk at 08:04 agreed with the order: master `c94c39e`, this branch inside it; fast-forwarded.

**THE RESUME ORDER (10:02),** after the laptop restarted: re-gate `cee979c`, and if the gate finds
anything, fix it at its site, red first, and commit. Disk agreed -- this branch `cee979c`, clean.
The gate was begun and then stopped (R.9); the cold verifier's salvaged findings were fixed at
their sites, shown red first and committed (R.4).

**THE ADDENDUM (11:25).** Master fast-forwarded to `02560b0`, the live lane's session-2 wrap-up:
13 commits, among them 28 tracked skeletons under `tests/fixtures/live2/`, one of them this same
profile. After the gate then running: integrate master once if its CI is green, keeping the
history; regenerate derived views to a fixed point; re-derive every pin; run the duplicate-key
check; reconcile the fixtures to ONE live-true source; gate the final tree; commit without
attribution. Disk at 11:26 agreed but for timing -- master `02560b0` here, the remote still
`c94c39e`, no CI run yet -- and within three minutes the remote was `02560b0` and its CI in
progress, as the addendum said. The gate then running was on `5afa484`, not `cee979c`: the cold
check's fixes had been committed after the addendum's sample. R.7 and R.8 carry it out.

### R.1 The ruling, registered

- `_audit/2026-09-28-rulings-named-profile-read.md`, copied from the orchestrator's scratch copy.
  ONE CHANGE, forced by a document guard, and the order's own rule for that case: the backticks
  around `PEOPLE-DATA-MITIGATIONS` on its line 37 are removed -- no word changed, two bytes.
  `tests/test_an_asserted_name_resolves.py` reads "under" at the end of line 36 and a backticked
  upper-kebab name opening line 37 as a BLOCKER citation, resolved against the gap-blockers ledger,
  which holds no ruling ids. sha256 before `de3d032f079b2ca0`, after `18f0c8809ea97ea8`.
- The register entry, `scripts/build_rulings_index.py`, with the order's fields verbatim --
  id `NAMED-PROFILE-READ-BEHIND-A-GRANT`, claim, binds, document, anchor, note -- and the status
  `AMENDS NO-THIRD-PARTY-PROFILE-LOAD`. FOUND ON DISK, AND NOT IN THIS REGISTER: his 2026-09-04
  removal of the third-party profile pattern has no entry in the rulings register. It is registered
  in the EXCLUSION register, `scripts/check_exclusion_basis.py`, as the family
  `NO-THIRD-PARTY-PROFILE-LOAD` -- made by the OPERATOR, op=YES, anchored on the removal's own
  comment in `readonly.py` ("THE THIRD-PARTY PROFILE PATTERN WAS REMOVED 2026-09-04, ON THE
  OPERATOR'S"). That id is the one the status names. `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET` was
  the other candidate and is not it: it is the orchestrator's application of ruling (b) of
  2026-09-24, not his removal. `RULINGS.md` regenerated: 68 rulings; `INDEX.md`: 259 documents.

### R.2 The read: `linkedin_read_named_profile(profile, confirm_token)`

- **THE PREVIEW LOADS NOTHING.** The mitigation he approved reads "a single-use confirmation for
  each view, stating the possible trace": the view IS the load, so the confirmation must come first.
  The preview is a sentence and a token, and never opens a browser (a test drives it with a browser
  that fails on any session). THE ONE PLACE THIS DEPARTS FROM THE ORDER'S WORDS: the order said the
  preview names the resolved member "as a people record". It cannot, and stay inside the ruling: a
  record needs a name (`people_data.Person` refuses one without), and the name is on the page whose
  load is being confirmed. So the preview names the member by the ONE address it resolved from his
  argument -- a link says WHO -- says it has not read the name and why, and tells him to check the
  link; the people record comes back from the confirmed call, read once. The order's two other
  sentences -- "states that LinkedIn may show that member the view" and "on confirm it loads the
  profile once" -- are exactly this design. The preview asks the door FIRST: a segment the
  named-profile door refuses gets no token and is not quoted back (added after the cold check, R.4).
- **THE GRANT.** The writes' shape, its own registry: `writes.mint` grants only a sanctioned WRITE,
  only against a reading a preview LOADED, and only with writes on -- three facts this read does not
  share. So `named_profile` keeps read grants with the same properties: a 24-byte token, bound to the
  canonical link, 120 s (pinned equal to `writes.GRANT_TTL_SECONDS`), single-use at the token AND at
  the load, swept on every mint and consume, in process memory only. A grant holds his argument,
  never a page string. A token that would be refused -- unminted, replayed, expired, or minted for
  another profile -- is refused BEFORE a browser session opens (`named_profile.check_read_token`,
  added after the cold check: until then the refusal came from inside the session, which loaded
  nothing but started a browser for a call that could not proceed). NOT BEHIND THE WRITES FLAG: the
  ruling calls it a read and its conditions are the grant, the preview's statement and the records,
  each enforced; a flag named WRITES would misname it. The orchestrator can flip that.
- **ONE LOAD.** `named_profile.load_the_confirmed_profile` redeems the token FIRST, marks the grant
  loaded, composes the address with the boundary (`readonly.named_profile_url`), checks it with
  `assert_named_profile_url` and loads it through the second door. A landing that is not the named
  address vetoes the whole read (a member id LinkedIn redirects: C-P6), and the preview says so when
  it was given a member id. No scroll, no press. THE LANDING, AS THE COLD CHECK LEFT IT: a vanity
  segment compared percent-decoded and ASCII case folded only, a member id compared exactly, and an
  EMPTY landing vetoes. Before, the comparison was Unicode `casefold()` -- which equates a sharp s
  with "ss", the Kelvin sign with "k", a ligature with its letters and a long s with "s", and two
  member ids that differ only in case -- and an empty landing defaulted to the composed address and
  passed the veto.
- **WHAT COMES BACK.** `person` -- name, headline, link, as a people record through
  `named_profile.person_from_the_topcard`, the ONE parse the named acts' preview now shares (split
  out of `name_the_profile_target`, not copied; a line with no letter or digit is dropped before it,
  because the live topcard draws two). Degree ABSENT: no capture shows a third party's degree line's
  words. `groups` ABSENT, with its reason. `capture_hints.group_links_drawn`: one count, for C-P7,
  naming no group. Counts of what the page showed. Nothing else.
- **NEVER FOR A MEASUREMENT, AS FACTS ABOUT THE TREE:** no file under `scripts/` names the read by
  any of its six names (a test, shown catching a planted probe), and one tool reaches its loader.
- **NEVER A NAME:** `named_profile.profile_segment` refuses a name, a bare word, a sub-page, his own
  `/in/me/` and an invisible character before a browser session or a grant exists.
- `tests/test_named_profile_read.py`: 32 tests, 51 cases collected. Five are controls that plant a
  property false -- a preview that opens a browser, a reusable token, a read of the groups, a probe
  naming the read, the landing veto removed -- and each is caught by the real test it plants
  against.

### R.3 The door, and the permanent refusal

- The second door now has TWO callers, each pinned: `writes._load_named_profile` (the named acts)
  and `named_profile.load_the_confirmed_profile` (the read). `tests/test_named_profile_route.py`'s
  two pins became "exactly two functions ask for the door" and "only `browser.py`, `writes.py` and
  `named_profile.py` name it"; `tests/test_probe_navigation_budget.py` counts the door as a guard in
  exactly those two (file, function)s (`SECOND_DOOR_GUARDS`). The read door is unchanged.
- The loader's locals are named for it (`profile_address`, `read_landing`): bound to `landed`, the
  navigation guard's module-wide taint spread through `landed_on_profile`'s `parts` and
  `profile_segment`'s `segment` into this navigation, and read it as one the page chose -- measured
  red, then renamed, as `writes._read_account_share_updates` records the same trap.
- `writes.PERMANENTLY_FORBIDDEN["load_a_third_partys_profile_to_measure_a_control"]`: the key and
  its measured ground unchanged; the text now takes exactly this read out of it, by name and ruling,
  and says everything else stays forbidden -- a probe, a census, an instrument, an unconfirmed read.

### R.4 The addendum: the reader rebuilt over the live skeleton -- twice

- **THE LIVE REFUSAL, REPRODUCED OFFLINE.** The old reader, run on the fixture built from the
  skeleton, before any edit: title, one topcard, its first heading the title's name, degree `1st`
  -- identity confirmed -- and `message_state` `unknown`: "0 Message control(s) are named for this
  person". `message_matches` 0, `message_controls_in_topcard` 0. The topcard's Message control is a
  composer link named by its own text, "Message", with NO label -- drawn TWICE, in two action rows,
  one hidden -- and every LABELLED Message control on the page (`Message <name>`) is another
  person's, on a rail. The old reader matched the label alone. Pinned by
  `test_the_old_reader_refuses_the_live_page_as_it_did_live`, over the old gate's frozen conditions.
- **THE FIXTURE.** `scripts/_build_named_profile_skeleton.py` (committed) turns the live lane's
  skeleton -- every non-furniture value already a keyed shape -- into
  `tests/fixtures/synthetic/named_profile_live.html`: the capture's structure, 1415 elements; the
  owner the declared `Casey Example` (the invented page's person, so the two fixtures are one person
  on two drawings); other people REDUCED TO SHAPE and given `someone-example-<n>` slugs (20 of
  them); LinkedIn's class names DROPPED, so no reader here can lean on them. Its capture run
  printed: 185 texts reduced to shape, 7 dotted, 16 labels refilled from their control's own word,
  36 placeholder labels, 11 labels dropped on member links, 8 unclassified labels ("Verified", then
  absent from master's copy of the live lane's word list; kept since the merge, R.8), 0
  unclassified texts, 0 unclassified attribute values, 75 addresses rebuilt, 8 dropped (off
  LinkedIn's host), 73 ids mapped, and the STRUCTURE DIGEST `iefnpejnhfajibng`. Run over its own
  output it is a FIXED POINT and prints the same digest; re-run from the skeleton it reproduces the
  committed page byte for byte. `tests/test_named_profile_live_skeleton.py` pins both, and its
  controls fail on an svg deletion, a text edit, an edit inside a kept attribute and a capture that
  draws an Interests section (and, since R.8, a structural edit of the tracked source). THE
  TEXT-EDIT CONTROL FAILED FIRST: the builder kept any text that was not a shape, so a hand edit
  survived its own fixed point. It keeps now only LinkedIn's words on a closed list -- held to the
  live lane's list by a test -- and the values it writes; anything else becomes "Example text",
  counted. The kept-attribute and Interests controls came from the cold check (below).
- **DERIVED, AND SAID SO IN THE FIXTURE AND THE BUILDER:** the topcard container's id suffix
  (shaped in the skeleton; its shape, 80 characters, 71 letters, 4 digits, is the measured
  `com.linkedin.sdui.profile.card.ref<member id>Topcard` -- his own profile's three raw captures
  each carry exactly one topcard id of that form, and six sibling cards on the skeleton fit the same
  pattern with their own suffix lengths; were it wrong, the reader finds no topcard and refuses);
  WHICH of the two action rows is hidden (the second, here; the tests also hide the first); the
  degree line's words; "Contact info".
- **THE FIRST REBUILD** (on `cee979c`) counted, inside the owner's topcard, each kind's controls with
  a visibility test of the page's own -- a non-empty box and no `visibility:hidden` -- over the
  page's own `querySelectorAll`, and judged each the owner's or FOREIGN in the same script. The act
  needed exactly ONE VISIBLE control of the kind and that one the owner's; the press selectors
  carried `:visible`. The next bullet is why that was not enough.
- **THE COLD CHECK.** A cold verifier -- a fresh general-purpose agent, briefed to break the rebuilt
  reader offline and to press nothing -- was run on `cee979c`. It died with the laptop's restart;
  its disk outputs were salvaged and its instruments re-run by this lane. It built 22 pages from the
  two fixtures and asked Playwright, with a TRIAL click, which element the strict press WOULD reach.
  On SIX, the gate passed and the press would have reached a control that is not the owner's:
  1. a stranger's card nested inside the topcard with its own unlabelled "Message" link, the
     owner's visible link gone -- an unlabelled "Message" was taken for the owner's wherever it sat
     in the topcard;
  2. the same, the stranger's link named by `aria-labelledby` rather than `aria-label`;
  3. the owner's Message `visibility:collapse`, and a stranger's labelled Message in an open SHADOW
     ROOT inside the topcard -- the page's own test called the collapsed control visible, the page's
     `querySelectorAll` never entered the shadow root, and Playwright's engine, which the press
     uses, did the opposite of both;
  4. the only visible Message a composer link on ANOTHER HOST -- the destination token read the
     path of any host;
  5. the owner's Connect collapsed, and a stranger's Connect in a shadow root;
  6. a same-name stranger's card nested inside the topcard with ITS Connect, the owner's gone.

  On four more the gate and the press disagreed without reaching anyone -- `display:contents`,
  `visibility:collapse`, `content-visibility:hidden`, a closed `<details>` -- so a pass was followed
  by a press that found nothing, or a control the press would reach was refused. It also found the
  landing comparison, the token opening a browser before its refusal, and the preview minting a
  token for an address the door refuses (R.2), and two holes in the builder: a canary written into
  `role`, `dir` and `aria-current` survived it and was a fixed point of it, because a kept
  attribute was kept whatever it held; and it reduced "Interests" and "Groups" to "Example text",
  so a capture that DID draw the groups section would have been built into a fixture where the
  `N 178` test could not see it. And one of its measurements convicted the fixture's members: the
  builder gave every composer link inside the topcard the owner's member and every link outside it
  a stranger's -- by POSITION -- while the capture's own links say which member each names.
  NOTED, NOT CHANGED: a Message control moved off-screen passes the gate and the press then times
  out -- it fails safe; and a refused read for ANOTHER profile does not burn the token, by design.
- **THE SECOND REBUILD, WHICH IS THE READER NOW.** One engine answers both questions:
  `dom.read_named_profile` resolves each kind through the PRESS SELECTOR ITSELF (`:visible`, in
  Playwright's engine, shadow roots included) and through its all-of-kind twin (hidden included),
  and judges ownership on exactly those elements with `dom.CONTROL_FACTS_JS`, run by
  `evaluate_all` from one call site; `dom._closed_facts` re-closes every field it returns (two
  booleans and two closed tokens per element, no name, label, href or id). A control is the owner's
  only if it sits in the ONE topcard (`closest()` does not cross a shadow boundary, so a control in a
  shadow root is foreign), and: a Connect labelled `Invite <owner> to connect`; a Message labelled
  `Message <owner>` whose composer address, if any, names no other member; or an UNLABELLED Message
  that says exactly "Message", is an `<a>`, and whose `recipient` and `profileUrn` both name the
  member in the topcard's own id. The destination token reads a composer path only on a relative
  address or `https://www.linkedin.com`. The press gate first asks that the topcard be ONE person's
  card -- one heading drawn in it, at most one member linked from it -- then exactly one visible
  control of the kind, that one the owner's, and no foreign one of the kind, visible or not. The
  visible More count the refusals print is a locator count. Every refusal kept: exactly one, a
  re-check before any press, `unknown` refuses.
- **MEASURED FOR THAT OWNERSHIP RULE, ON THE SKELETON** (keyed hashes compared, never printed): the
  page draws seven composer links; the topcard's two name one member in both `recipient` and
  `profileUrn`; one outside the topcard names the same member; the four on the rails name others.
  The builder now maps members by the capture's own `recipient`, so links that named one member
  still name one, and the page carries the owner's link outside the topcard as the owner's.
- **SHOWN RED FIRST, ON THE FIRST REBUILD'S CODE, THEN GREEN.**
  `tests/test_named_profile_adversarial.py` (new) builds the pages as scripts run in a local page
  -- 12 worlds, the two committed pages among them -- and asserts that the gate's visible count equals the count of the press selector in
  Playwright's engine, that the seven worlds putting a stranger's control within reach are refused,
  and that where the gate passes the one element the press resolves is the owner's: 22 of its 34
  cases red on the old reader. The new read and skeleton tests: 15 of 18 red on the old code. All
  green on the new. The verifier's own world instrument, adapted to the new reading's keys and re-run
  on the fixed tree: every world in which the press could reach a stranger now reads `unknown`.
- **ON THE BUILT PAGE, NOW:** 2 Message controls in the topcard, 1 visible, the owner's, 0 foreign,
  a composer link -- `message_control_drawn`, and the press selector matches exactly 1. With the
  FIRST row hidden instead: the same. With both rows shown: 2 visible, refused. The read he names
  returns `Casey Example` and the headline as a people record, groups absent, `group_links_drawn`
  0.
- **WHICH FIXTURE IS LIVE-TRUE:** as the addendum of 08:43 asked it, `named_profile_live.html`
  against the invented page. Since the merge of the live lane's session-2 wrap-up the answer is
  sharper, and R.8 gives it: the ONE live-true source is the live lane's tracked copy of the same
  capture; `named_profile_live.html` is the page built from it. `named_profile.html` says in its
  header that it is the SECONDARY case, kept for what the live page cannot show: a Connect control,
  another degree, a same-name stranger, the conversation a Message press opens. Its route tests that
  pinned the old reasons pin the new ones, each intent unchanged.
- **ONE GUARD NARROWED -- SUPERSEDED IN THE MERGE (R.8):** `test_fixtures_hold_only_synthetic_people`
  read "Send" (twice) and "Show all" (twice) as the first text of links to the owner's profile --
  the live page draws a post's share action and a section footer as such links -- and this lane
  passed exactly those two words in the member-text slot. The live lane narrowed the same slot the
  same day with a better rule, which the merge keeps.
- **THE GUARDS THE NEW SCRIPT MOVED, EACH WITH ITS ARGUMENT:** `CONTROL_FACTS_JS` is declared in
  `tests/test_readonly.py`'s injected scripts; the evaluate waiver budget for `dom.py` 21 -> 22 and
  the executed-script pin 22 -> 23, the two counts still one apart. The landing-interpolation
  baseline +1, `dom.py:_closed_facts`, which builds no address (a NAMES_NO_ADDRESS ruling in
  `tests/test_no_message_publishes_a_landing.py`).
- The tool that wrote this lane's files decoded three escapes into the characters they spell (a
  middle dot, a zero-width space); all three are ASCII spellings again, checked byte by byte.

### R.5 The census

- **`N 178` STAYS GAP; NEEDS-TARGET STANDS.** Its section is not in the capture: the live skeleton,
  one load without a scroll, draws no Interests section and no link under `/groups/`. A test pins
  both, on the built page and -- since R.8 -- on the tracked source, whose writer keeps "Interests"
  and the path word "groups" verbatim; a control shows the builder keeping an Interests section a
  capture does draw. Its cell records the ruling, the tool and the blocker, named in words: the
  capture C-P7. The address table's note moves with it; its line stays REFUSED, because that table
  is the READ door's, and the read goes through the second door.
- **THE FOUR READ ROWS PUT TO THE ORCHESTRATOR, NOT MOVED.** R4's section records the narrowing. The
  rows filed EXCLUDED-RULED on it that are READS of a member's profile content -- `N 30` (a
  connection's connections), `N 31` (shared connections), `N 65` (the Interests section) and
  `N 103` (similar profiles) -- rest on a ground now narrowed for a member he names, and by
  EXCLUDED-RULED-ADMISSION a row whose written ground no longer reaches it is GAP with a named
  blocker. The ruling's own unblock list names `N 178` alone, so, as with `N 2` on 2026-09-27, their
  state is kept and the move is the orchestrator's: to GAP, each blocked on a capture of its section
  and a declared field, would move GAP 584 -> 588 and EXCLUDED-RULED 30 -> 26. The acts on R4 keep
  their ground.
- No state moved: J 108, P 186, M 131, N 159, GAP 584 -- the figures master carries, before the
  merge and after it (R.7).

#### C-P7 -- a member's groups, for the live lane's session 3

Taken INSIDE the first confirmed `linkedin_read_named_profile` of a member HE names for his own
reason -- never a load of its own; a load to capture is a load for a measurement, which stays
forbidden.

1. The member: one he names, ideally one who belongs to at least one group he can see. He confirms
   the read himself, after its preview.
2. After the confirmed call returns, with the page still on screen in the server's own tab: save its
   DOM with the session-2 skeleton writer, nothing pressed, no scroll.
3. The read's own `capture_hints.group_links_drawn` says at once whether that load drew a group
   link. Session 2's first-degree profile drew none.
4. Offline, counts and shapes only, the capture must answer: is an Interests section drawn at load;
   its tabs (a closed vocabulary) and which is selected; whether the Groups panel is in the DOM
   before any press; each group entry's shape (a link under `/groups/<digits>/`, a title element);
   and whether a "Show all" link to the member's `details/interests` sub-page is drawn, with its tab
   index.
5. If the groups are NOT on that load, the next step is a ruling, not a load: a scroll (the scroll
   ruling covers infinite scroll, not one scroll to a section), a tab press
   (DISCLOSING-PRESS-PERMITTED has four conditions), or the sub-page -- which the named-profile
   door does not admit. The capture's answer is what that ruling decides on.

The same save refreshes C-P1 for a profile of another degree; session 2's skeleton took it for a
first-degree one. Its tracked copy keeps the words "Interests" and "Groups" and the path word
"groups", and so does this lane's builder, so a capture that draws the section survives into both.

### R.6 Pins and counts, each measured

- The surface: 61 tools, 95 parameters (+1 tool, +2 parameters); 44 read, 17 write, 0 write-shaped.
  `test_server_surface.py`'s headline, its count test (`..._sixty_one_tools`) and its split;
  `test_every_tool_is_on_the_surface.py`; the pinned surface, with its census decision written
  beside the pin; `server.py`'s headline, its three-way split and its instructions;
  `known_side_effects` and `read_boundary_scope`, which said no read tool loads a profile.
- `people_data.PEOPLE_TOOLS`: 7, with the read (the bounded-reader guard derives it).
- The reader-leak baseline, regenerated by its writer, offline:
  `named_profile:read_the_confirmed_profile` `returns_records` (driven as the tool calls it),
  `named_profile:load_the_confirmed_profile` `not_driven:raises WriteAttemptError` (the harness's
  token is no grant); unchanged by the second rebuild and by the merge. The tool-envelope baseline:
  the read `not_driven:never read the page`. The landing baseline: +1 (R.4).
- The page-string guard's record path now includes the read, its reader and the shared parse.

### R.7 The integration of master `02560b0` (the addendum of 11:25)

- **ITS CI FIRST.** Run 36384163528 on `02560b0`: 20 of 20 jobs green, finished 11:36. Only then
  ONE merge, keeping the history: `981848e`, whose parents are this branch's `5afa484` and master's
  `02560b0`.
- **FOUR FILES CONFLICTED, EACH RESOLVED AT ITS SITE.** `_audit/_census/network.md`: row 177 is
  master's (its capture note on a group's member list; this lane never touched the row) and row 178
  is this lane's (the ruling and the read; master never touched it) -- measured word by word
  against the merge base, one insertion on each side. `tests/test_fixtures_hold_only_synthetic_people.py`:
  master's, whole (R.8). `_audit/RULINGS.md` and `_audit/INDEX.md`: regenerated by their writers.
  The three other files both sides touched merged clean: `linkedin_server/browser.py` (master's
  last-tab rule, this lane's door prose), `tests/test_readers_emit_no_page_string.py` (a drive
  each) and `tests/reader_leak_baseline.json`.
- **DERIVED VIEWS, TO A FIXED POINT.** `RULINGS.md` (68 rulings), `INDEX.md` (259 documents) and
  `_census/blocker-map.tsv` rewritten by their writers, then written a second time with no change.
  The three baselines rewritten by their writers, offline: no change from the merge, and no
  request left the machine.
- **PINS RE-DERIVED, NEVER ADDED.** The census counter over the merged tree: GAP 584 (J 108,
  P 186, M 131, N 159), COVERED-PROVEN 70, COVERED-UNFIRED 34, CP 21, CU 3, EXCLUDED-RULED 30,
  MEASURED-ABSENT 10, 770 stated rows; every `census_completion` headline at master's pins. The
  live lane's twelve moves are COVERED-UNFIRED to COVERED-PROVEN, so GAP does not move, and this
  lane moves no state -- `N 178` stays GAP -- so nothing of this lane's lands on their figures.
  The tool surface is this lane's alone, master changing no tool: 61 tools, 95 parameters. The
  census battery's twelve instruments: all green.
- **THE AST DUPLICATE-KEY CHECK** over the merged tree, its plant convicting a dict, a set and a
  re-assigned key first: ONE duplicate, `"urlretrieve"` twice in `_FETCH_NAMES`, line 83 of
  `tests/test_api_call_sites.py` -- on master, not this lane's, left for its owner; a third name
  was probably meant.

### R.8 One live-true source for the profile's markup (the addendum of 11:25)

- **THE TWO FILES ARE ONE CAPTURE, MEASURED.** The live lane's tracked copy,
  `tests/fixtures/live2/first_degree_profile.html`, and the gitignored skeleton this lane's builder reads
  have IDENTICAL tag and attribute-name sequences, 1830 elements each. What differs is only what the
  tracked copy reduces: every keyed shape of a text one `x` (203 texts), every query value one `x`
  -- the seven composer links all read `profileUrn=x&recipient=x` -- ids kept as `k` and their
  8-hex hash, and LinkedIn's class names kept. Over the tracked copy's body the builder's structure
  digest is `iefnpejnhfajibng`: the digest it printed from the skeleton, and the built page's.
- **THE DECISION: ONE SOURCE, ONE PAGE BUILT FROM IT, KEPT BECAUSE THEY TEST DIFFERENT THINGS.**
  The LIVE-TRUE SOURCE of that profile's markup is the tracked copy. `named_profile_live.html` is
  not a second source: it is the builder's output from the same capture, its builder kept with its
  pinned digest, and a new test holds it to the source by that digest -- computed from tracked
  files, so anyone can re-derive it, where before only a box holding the gitignored skeleton could;
  its control breaks the tie with one structural edit of the source. The builder keeps reading the
  skeleton, and its docstring says why: the tracked copy reduces exactly what a page for this reader
  needs -- the keyed hash that finds the owner's name wherever it stands, the hash in each composer
  link's `recipient` that says which member the link names (the measurement the ownership rule
  rests on, R.4), and the letters, digits and length that find the degree line, the headline and
  the contact overlay.
  - WHAT THE SOURCE TESTS: the live lane's harness reads it for the topcard's action bars by their
    class names -- which bar his width shows, and the More handle (their fix 3). The reader now runs
    on it too, and REFUSES -- no name, no member id, no topcard id -- as it must on any page that
    names no one; and `N 178`'s reason is read off it (R.5).
  - WHAT THE BUILT PAGE TESTS: everything that needs a person -- the identity reading, the ownership
    of the unlabelled Message by the topcard's member, the gate against the press
    (`tests/test_named_profile_adversarial.py`), the read he names returning a people record.
  - The invented page, `tests/fixtures/synthetic/named_profile.html`, stays the SECONDARY case; its
    header and the built page's now name the source first.
- **THE READER ON THE SOURCE WAS RED FIRST, UNDER THE SUITE'S OWN NETWORK GUARD:** the tracked copy
  keeps its stylesheet and image addresses' path words, so loading it asked for four of them, each
  refused before it left -- as the live lane found for their first such test. The test now refuses
  every request in the page's own route first.
- **"VERIFIED" KEPT.** The live lane's list of LinkedIn's words gained "Verified" with the session-2
  wrap-up, so the builder keeps the eight labels the skeleton drew with it, where it wrote the
  placeholder before; the page is regenerated, still a fixed point, its digest unchanged.
- **THE MEMBER-LINK WORDS: THEIRS KEPT, MINE DROPPED.** Both lanes narrowed the same slot of
  `tests/test_fixtures_hold_only_synthetic_people.py` the same day over the same live sites. The live
  lane's `MEMBER_LINK_INTERFACE_WORDS` ("Premium", "Send", "Show all") SKIPS the word and reads the
  link's next text as its person; this lane's `MEMBER_LINK_INTERFACE_TEXT` ("Send", "Show all") took
  the word and closed the slot, so a name after it, in its own element, was never read. The merge
  keeps theirs whole and drops mine with its control.
- **THREE STATEMENTS THE CAPTURE MADE FALSE, CORRECTED:** `dom.py`'s account of how the topcard's
  Message is judged still gave the FIRST rebuild's rule, the one the cold check broke; its note that
  a third party's profile "has never been captured"; and the identity refusal's "A third party's
  profile has never been captured", which the server says to its caller -- it now says the shape
  was measured on his own profile and on the one third party's captured, and keeps NEEDS-CAPTURE
  C-P1 for any other.

### R.9 Gates

- **THE RESUME ORDER'S GATE ON `cee979c`, STOPPED.** The whole suite, begun 10:06, was stopped at
  77% with 0 failures when this lane began editing the tree under it for the cold check's findings.
  No result is claimed from it.
- **THE COLD CHECK'S FIXES, RED FIRST** on the first rebuild's code: 15 of the 18 new read and
  skeleton cases, 22 of the 34 adversarial ones. Green on the new code after two test-side
  corrections -- a route test whose Message link to a thread is now refused one step earlier, as a
  control not the owner's, so its expected reason moved; and the reusable-token control, whose
  plant the new pre-session check caught first, so it now plants a registry that forgets uses --
  243 passed. Then the guards the change reaches found seven, each fixed at its site: the readonly
  scanner's five pins and `tests/test_writes.py`'s count of mutating calls, all six for the new
  script's call sites until they were one, declared with its argument (R.4); and a literal profile
  address in a test, which the identity sweep caught and the module's constant replaced. And one
  more on the rerun: the visible More count in the topcard, which a `:text-is` selector read as 0
  and a role query reads as the 1 visible. Last: 3879 passed, 1 skipped.
- **THE IDENTITY GATE ON EACH COMMIT** -- the pre-commit hook, 226 spellings, its key read from the
  main checkout: 11 staged files for `5afa484`, 97 for the merge, 6 for `0017f42`, 2 for
  `c04b20f`; 0 hits each.
- **THE WHOLE SUITE on `5afa484`.** The impact gate's plan against `c94c39e` selected 259 of 282
  test files (92%) and widened. Run in the background, `-n auto --dist loadfile`, under the suite's
  own offline guards: 12101 passed, 9 skipped, 1 xfailed -- 12111 tests -- in 1098 s.
  `tests/test_no_committed_identity.py` 982 of 982, its exact-value sweep among them. The nine
  skips: three symlink tests this box cannot run, four empty parameter sets, one test that arms
  itself when its reader arrives, and the navigation guard's whole-tree complement, which runs only
  under CI (run below with CI=1). The one xfail is the people-search reader's declared limit.
- **THE CENSUS BATTERY on `5afa484`:** twelve instruments, all green.
- **MASTER'S CI, THEN THE MERGED TREE:** R.7 -- master's run green; derived views at a fixed point;
  baselines unchanged; the census battery green; one duplicate key, master's.
- **THE RECONCILIATION:** its new tests red first where R.8 says, then 19 of 19 in the file; the
  thirteen files the change reaches, 3178 passed, 1 skipped (the complement); the navigation guard
  with CI=1, 683 of 683.
- **THE RECORD'S OWN PATHS, before their commit:** the impact gate's own run over them, 45 test
  files (2898 tests), PASS -- and it says so, over nothing else.
- **THE FINAL GATE, on `c04b20f`** -- the tree the reconciliation and this record left. The impact
  gate's plan against master `02560b0` selected 258 of 283 test files (91%) and widened; the whole
  suite, in the background, `-n auto --dist loadfile`, under its own offline guards: 12200 passed,
  9 skipped, 1 xfailed -- 12210 tests -- in 956 s, the same nine skips and the same xfail.
  `tests/test_no_committed_identity.py` 1011 of 1011 on the committed tree, its exact-value sweep
  among them; the live lane's harness 128 of 128; this lane's named-profile files 34, 19, 51 and
  121, every case. The census battery on it: twelve of twelve green. The navigation guard with
  CI=1: 683 of 683. The builder, re-run from the skeleton: the committed page byte for byte. The
  duplicate-key check: master's one, nothing new.
- **THE COMMIT CARRYING THIS PARAGRAPH** changes this file and nothing else. Its own impact plan and
  that plan's result are in the report that returns the head sha -- a record cannot hold the gate
  of the commit that writes it.

### R.10 NOT run

- CI on this branch: nothing is pushed, as ordered. The whole suite ran on this box only --
  Windows, Python 3.13 -- not on CI's Linux 3.10 and 3.13 cells.
- LIVE: nothing. No LinkedIn, no browser attached, no Chrome profile, no port. Every page in every
  test is local, and the network guard refused every request that tried to leave.
- A cold verification of the SECOND rebuild: the first verifier's instrument was re-run warm, by
  this lane, adapted to the new reading's keys; no fresh verifier was spawned for it.
- The builder over the tracked copy: it cannot run there (R.8); the tie is the digest.
- The four read rows `N 30`, `N 31`, `N 65` and `N 103`: put to the orchestrator, not moved (R.5).
- The duplicate `"urlretrieve"` in `tests/test_api_call_sites.py`: found, not fixed (R.7).
- `scripts/impact_gate.py` executing its own WHOLE-SUITE run: its plans were computed and read, and
  the two whole-suite runs they called for ran through this lane's runner under the suite's own
  guards. (Over the record's two paths it did run itself, R.9.)

### R.11 Commits -- on this branch, none pushed, no AI attribution in any

    9813d77  rulings: NAMED-PROFILE-READ-BEHIND-A-GRANT, his ruling of 08:01
    32efd34  the read, and the named-person reader rebuilt over the live skeleton
    970b463  census and record: N 178 stays GAP on its capture
    cee979c  the whole suite's four findings on 970b463, fixed at their sites
    5afa484  the cold check's findings on cee979c, fixed at their sites (R.4)
    981848e  the merge of master 02560b0 (R.7)
    0017f42  one live-true source; three stale capture claims corrected (R.8)
    c04b20f  this record, R.2 to R.11, and the instrument register's 69.14
    (last)   R.9's final gate, and its skip sentence corrected -- this file only

## The orchestrator's calls of 2026-09-28 12:32: four reads back to GAP, a neutral name, a repeated member

**THE ORDER.** Master was fast-forwarded to this branch's head and pushed, its CI running. Three calls
on the three items this lane had put to him: (1) `N 30`, `N 31`, `N 65` and `N 103` to GAP -- their
only exclusion ground was R4, loading a third party's profile, which NAMED-PROFILE-READ-BEHIND-A-GRANT
narrowed to a read of a profile he names -- each cell naming its blockers (a capture showing that
section on a profile he names; then an extension of `linkedin_read_named_profile` returning it as
declared fields or people records; a target he names), `N 30`'s R2 recorded as incidental capture,
GAP 584 -> 588 and EXCLUDED-RULED 30 -> 26 measured, every pin re-derived; (2) the tracked copy of
the first-degree profile renamed to a neutral structural name, every reference updated; (3)
`_FETCH_NAMES`'s repeated member resolved from the intent of the commit that wrote it, and a guard
that no set literal repeats a member, shown failing on today's file.

Disk at 12:30 agreed: master, the remote and this branch on the head the order named. Its CI run
finished green, 20 of 20 jobs, at 12:36.

### S.1 The four rows

- **`N 65` AND `N 103`, AS CALLED.** GAP, the call's three blockers named in each cell. Neither
  section is in any capture: the live lane's first-degree capture, one load without a scroll, draws
  no Interests section (`N 178`'s test pins it), and its rails are headed 'People you may know' (6
  member links) and 'You might like' (4 Page links, 5 member links) -- no rail headed 'People also
  viewed' or 'More profiles for you' (measured on the tracked copy: headings and link paths, nothing
  of anybody's). Whether 'You might like' is the rail `N 103` names, a skeleton cannot settle.
  C-P7's save, specified for `N 178`, answers `N 65` too: the same section, its other tabs.
- **`N 30` AND `N 31`: THE CALL'S PREMISE, MEASURED, IS NARROWER THAN THESE TWO ROWS.** The call
  reads each row as a section of the named member's profile. The capture says these two lists are
  not profile sections but LINKS INTO PEOPLE SEARCH, drawn inside the topcard -- three of them, each
  to `/search/results/people/` with `origin` and `connectionOf`:

      link 1   origin, connectionOf, network   connectionOf 43 characters: one member id in a
                                               JSON list; network 9 characters, 2 letters
      link 2   origin, network, connectionOf   both percent-encoded lists: connectionOf 51
      link 3   the same as link 2              characters, network 13 characters, 3 letters

  (shapes read off the gitignored skeleton; values never read). DERIVED from those shapes: link 1
  carries `network` `["F","S"]` -- the member's connections -- and links 2 and 3 `["F"]` -- the
  shared ones, his first degree. The read door ADMITS both addresses, and R2 catches neither
  (measured). So, holding the state the call set and writing the blockers as measured:
  - `N 30`. `linkedin_people_search_shape(connections_of=<member token>, include_names=True)`
    already composes that `connectionOf` -- `people_search.compose` writes exactly the
    percent-encoded list LinkedIn drew on links 2 and 3 -- and returns the member's connections as
    people records, the route `N 172` is COVERED-UNFIRED on; a 1st-degree connection's token is the
    `recipient_id` `linkedin_connections` returns; and the two-value `network` narrows nothing,
    since every connection of a 1st-degree connection is within two degrees of him. The cell takes
    the call's blockers in turn: (1) CAPTURED; (2) NOT NEEDED on the drawn route; (3) STANDS, for the
    first fire. Its move on to COVERED-UNFIRED, by D6-CAPABILITY-OVER-AFFORDANCE as `N 4`'s was, is
    PUT TO THE ORCHESTRATOR; until he rules, GAP. The address table gates it BUILT-UNFIRED, the read
    triage SERVED.
  - `N 31`. The same search composes `connectionOf` but not LinkedIn's `network` facet, so it
    returns the member's connections at every degree, one page per call, each with a degree; the
    shared ones are the 1st-degree among them, on that page only. (1) CAPTURED; (2) the extension is
    people search's composition gaining `network` -- a closed vocabulary LinkedIn wrote on this page
    in two spellings -- not `linkedin_read_named_profile`; nothing blocks building it; (3) STANDS,
    for the first fire. The address table gates it READER -- the one row in bucket 3 BLOCKED ON
    NOTHING -- and the triage BUILDABLE.
  - `N 30`'s R2, RECORDED AS INCIDENTAL CAPTURE, a blocker and not a ruling
    (INCIDENTAL-CAPTURE-IS-NOT-A-RULING): the forbidden substring "/connect" also matches the word
    "connections" -- `/in/<slug>/details/connections/` is refused on it before the allowlist is
    asked, and `/in/<slug>/overlay/connections/` too (measured). On the route the capture draws, R2
    catches nothing.
- **A FINDING FOR ANOTHER CELL'S OWNER, NOT ACTED ON HERE.** `N 85`'s cell calls the `connectionOf`
  spelling DERIVED -- "on record nowhere LinkedIn wrote it". Links 2 and 3 are LinkedIn writing it,
  percent-encoded, the spelling `people_search.compose` sends. The cell is lane S's, and a pointer
  instrument pins its argument, so it is reported rather than edited.
- **THE SIDE TABLES.** The four `_audit/_census/exclusion-basis.tsv` lines left with their rows.
  `_audit/_census/read-addresses.tsv` gained one line each: `N 30` and `N 31` ADMITTED (the two
  people searches, values placeholders), `N 65` and `N 103` REFUSED on a member's profile, the
  named-profile door not governed by that table -- as `N 178`'s line says. The read triage
  (`scripts/triage_read_gap_rows.py`), whose CONTROL 4 refuses a read-GAP row with no verdict, gained
  one each: `N 30` SERVED, `N 31` BUILDABLE, `N 65` and `N 103` RULING with a decided annotation --
  RETURNED is lane R's own class, and its marker names lane R. `network.md`'s section 1 records the
  delta; R4's section records the move.

### S.2 Pins, before -> after, each measured on the edited tree

    count_census_states     GAP 584 -> 588 (N 159 -> 163; J 108, P 186, M 131 unchanged)
                            EXCLUDED-RULED 30 -> 26; stated rows 770
    census_completion       gap 584 -> 588          gap_read 98 -> 102
                            out_of_scope 42 -> 38   achievable 728 -> 732
                            capabilities_achievable 742 -> 746
                            adjudicated 186 -> 182
                            b3_admitted 43 -> 45    b3_refused 38 -> 40
                            b3_blocked_on_nothing 0 -> 1
    check_exclusion_basis   population 42 -> 38, table 38, 0 problems
    check_read_addresses    98 -> 102 bucket-3 rows, every verdict agreeing with the boundary
    triage_read_gap_rows    75 -> 79 verdicts; decided since the triage 9 -> 11
    network.md, file-wide   EXCLUDED-RULED 15 -> 11, GAP 159 -> 163

The exclusion-basis table and the census instruments agree: population and table are both 38, and
NO-THIRD-PARTY-PROFILE-LOAD holds six rows, the acts 35, 66 and 144 to 147. `RULINGS.md` was
regenerated -- two of its corpus counts move by one, for the ruling id `N 30`'s cell cites -- and
`INDEX.md` and the blocker map were re-written unchanged, each at a fixed point. The pointer graph
holds its 64 pins.

### S.3 The rename

- `tests/fixtures/live2/first_degree_profile.html`, by `git mv`; content byte-identical.
- **REFERENCES TO THE OLD NAME: 7, ALL UPDATED** -- the live lane's harness test 4 (the name handed
  to `_serve_profile`), this lane's skeleton test 1 (`SOURCE`), `M M1`'s census cell 1, this record 1
  (R.8's path). No tracked file names the old file.
- **WHAT NAMED ONLY THE DIRECTORY NOW NAMES THE FILE:** the builder (its docstring, and the header it
  writes -- the built page regenerated, still a fixed point, digest `iefnpejnhfajibng` unchanged),
  the invented page's header, `dom.py`'s comment, INSTRUMENTS 69.14, and the skeleton test's header
  assertions, which now assert the exact path.
- **THE ROLE WORD LEFT CODE PROSE** -- 7 sites: four test docstrings pytest can print in a traceback,
  two comments, one module docstring -- each saying what the profile is, first-degree. It stays in
  record prose under `_audit/` (14 lines, 3 documents), as the call allows.
- **NOT RENAMED, AND NOT THIS LANE'S TO RENAME:** the gitignored skeleton in the live lane's own
  `_state/live2/`, read-only for this lane. `export_fixtures` names each tracked copy after its
  skeleton, so a re-export there would write the old name back; the harness's 28-copy count would
  then go red on the extra file. The live lane should rename its state file.

### S.4 The set that repeated a member

- **THE INTENT, READ.** `fbedfca` wrote `frozenset({"urlopen", "urlretrieve", "urlretrieve"})`.
  Its message and its audit (the 2026-08-24 publish audit, section 6) name the one shape it had
  missed, a bare `urlopen`; the standard library's `urllib.request` has exactly two module-level
  callables that fetch by name, these two (measured: `build_opener` builds, `urlcleanup` cleans
  up); and the package's only by-name HTTP import is `cdp_bridge`'s `urlopen`. No third name was
  meant. The repeat is dropped, and the comment above the set says why.
- **THE GUARD,** `tests/test_a_literal_repeats_no_member.py`: no set display -- nor `set(...)` or
  `frozenset(...)` over a list or tuple display -- and no dict display, in any committable Python
  file, holds two members Python would collapse: equal constant values, or the same bare name or
  dotted attribute. A member that may evaluate differently each time is never compared, and a file
  that does not parse FAILS rather than skips. Dict keys are in it beyond the call's words: they are
  the "ast duplicate-key check" each order asked for at a merge, which this lane ran by hand; it
  stands now.
- **SHOWN FAILING ON TODAY'S FILE:** before the fix, 1 failed, 18 passed -- the one offender
  `tests/test_api_call_sites.py:83`, `'urlretrieve'` twice. After: 19 passed, and 30 with the
  call-sites file. It read 596 files, 732 set displays and 4449 dict displays, the same under
  Python 3.13 and, through `uv`, 3.10. Its controls plant the line as it stood and each kind of
  repeat, and show the members it must not compare staying unconvicted.
- **DECLARED ALWAYS-RUN** in `scripts/impact_gate.py`: it reads every committable `.py` through an
  imported `git ls-files`, which the gate's own detector cannot see; corpus-wide guards 29 -> 30.

### S.5 Gates

- The literal guard: red on today's file, green on the fix (S.4). The impact gate's detection
  guard, `tests/test_impact_gate_selects_data_dependencies.py`, with it: 61 passed.
- The rename: the nine files it reaches, 1354 passed; the census battery, 12 of 12 green.
- The census move: the census battery, 12 of 12 green on the edited tree. THE IMPACT GATE over its
  six paths FOUND TWO RED FIRST -- `tests/test_triage_read_gap_rows.py`, CONTROL 4: four read-GAP
  rows with no triage verdict -- fixed at their site (S.1's triage lines); then 61 files, 3412
  tests, PASS.
- The identity gate on each commit: 3, 13 and 6 staged files; 0 hits each.
- THE FINAL GATE, on the commit carrying this section: its impact plan and result are in the report
  that returns the head sha -- a record cannot hold the gate of the commit that writes it.

### S.6 NOT run

- CI on this branch: nothing pushed, as ordered.
- LIVE: nothing -- no LinkedIn, no browser, no port. The capture was read from files only, for
  shapes, counts, headings and link paths.
- `N 30`'s and `N 31`'s route never fired: nothing here shows what a `connectionOf` results page
  draws (`N 172`'s cell says the same of its own route).
- The live lane's state file keeps its old name (S.3).
- `N 85`'s cell: reported, not edited (S.1).

### S.7 Commits -- on this branch, none pushed, no AI attribution in any

    c397ee6  a literal repeats no member: _FETCH_NAMES held two of its three names
    5e84802  a neutral fixture name: the first-degree profile's tracked copy
    06c05ec  census: N 30, N 31, N 65 and N 103 back to GAP, R4 narrowed by the read he names
    (last)   this section, and the instrument register's 69.15

## Integration 3: lane L5's merge of master a9cb2e3 (the orchestrator's addendum of 2026-09-28 14:20)

**THE ORDER.** Master was being fast-forwarded to `a9cb2e3`, the live lane's session-3 wrap-up
(14 tracked copies under `tests/fixtures/live3/`, `J 107`, `N 194` and `M M53` to COVERED-PROVEN,
delivered_strict 94, unfired 34, b1_no_ruling 15, GAP 584). Finish and gate the 12:32 calls,
integrate `a9cb2e3` once -- never a red master -- keeping this lane's state and cell on rows `31`
and `103` with the live lane's note appended, re-deriving every pin on the merged tree, and running
the duplicate-key check; report after the integration, so it can merge before the first-contact
build lands.

Disk at 14:20: this branch at the 12:32 calls' last commit, gated; master at `a9cb2e3` locally, the
remote not yet moved and no CI run. The first-contact work in progress was set aside as a patch
first, so the integration carries none of it. At 14:22 the remote moved and CI started; at 14:31
it finished green, 20 of 20 jobs. Then the merge, keeping the history.

### T.1 The conflicts, each resolved at its site

- `_audit/_census/network.md` rows `31` and `103`: this lane's GAP state and cell, then the live
  lane's session-3 note, appended whole. Each note is the count a blocker in the cell asks about:
  `31`'s, one mutual-connections phrase on the named read's first render; `103`'s, no 'People also
  viewed' and one 'People you may know'. Row `30` is this lane's; master had not touched it.
- `network.md`'s counts section: the live lane's back-pointer line and session-3 delta first -- they
  follow the session-2 delta above them -- then this lane's delta of 12:32.
- `_audit/_census/messaging-and-content.md` row `M1`: master's cell with its session-3 note,
  carrying this lane's rename of the tracked copy's path.
- MERGED CLEAN, THEN RENAMED: master's harness test added a parametrize naming the old file --
  it would have put the relation into a test id -- and a docstring's role word; both now say
  first-degree. No tracked file names the old file. `_probe_live_lane_session_2.py` and
  `census_completion.py` merged clean.

### T.2 Pins, re-derived on the merged tree

`census_completion.py --check`: every headline figure at its pin -- gap 588, gap_read 102,
out_of_scope 38, achievable 732, capabilities_achievable 746, adjudicated 182, b3 admitted 45,
refused 40, blocked on nothing 1 (the 12:32 calls') beside delivered_strict 94, unfired 34,
b1_no_ruling 15 (the live lane's). The counter: GAP 588 (J 108, P 186, M 131, N 163),
EXCLUDED-RULED 26, COVERED-PROVEN 73, COVERED-UNFIRED 31, 770 stated rows. The two sides moved
different rows, so no figure needed more than the merge -- each was measured, not assumed. `INDEX.md`
and the blocker map re-written by their writers twice, at a fixed point; `RULINGS.md` unchanged.

### T.3 Gates

- The census battery on the merged tree, twelve of twelve green.
- The duplicate check: `tests/test_a_literal_repeats_no_member.py` 19 of 19 -- 596 files, 732 set
  and 4450 dict displays, no repeat -- and the scratch walker's re-assigned-key half, none.
- The identity gate on the merge commit: 26 staged files, 0 hits.
- THE WHOLE SUITE on the merge commit: the impact plan against `a9cb2e3` selected 251 of 284 test
  files (88%) and widened -- run in the background, `-n auto --dist loadfile`, under
  the suite's own offline guards: 12257 passed, 9 skipped, 1 xfailed -- 12267 tests -- in 933 s.
  `tests/test_no_committed_identity.py` 1026 of 1026 on the committed tree, the live lane's
  harness 136 of 136. The navigation guard's whole-tree complement with CI=1: 683 of 683.
- This section's own commit is gated after it; its result is in the report.

### T.4 NOT run

- CI on this branch: nothing pushed. The merge is Windows, Python 3.13, locally.
- LIVE: nothing.

### T.5 Commits -- on this branch, none pushed, no AI attribution in any

    91932b0  merge master a9cb2e3, the live lane's session-3 wrap-up
    (last)   this section

## The first-contact path: the orchestrator's addendums of 2026-09-28 13:03 and 14:20

**THE ORDER.** Session 3 measured `linkedin_read_named_profile` PROVEN live, and
`linkedin_message_from_profile` REFUSED twice by `6_not_their_conversation`: there was no
conversation, so the press opened a NEW-MESSAGE composer, inside a SHADOW ROOT. The addendum of
13:03 gave the first contact a chain: (1) the target is the caller's link and identity is
confirmed; (2) the pressed control is the owner's one visible Message link and its address names
the profile's own member; (3) after the press exactly one bubble, exactly one committed recipient,
its text the topcard's name, whole, and no other recipient; (4) type only then, Send, then verify a
conversation exists headed by that name -- the receipt, never recording the name; (5) close by the
header's close control, found by its text -- Escape is not enough. Every condition refuses on doubt;
tests over a committed fixture BUILT from the skeleton, with synthetic names, a builder and a pinned
digest; the existing path stays as it is; no browser. The addendum of 14:20 set the order of work --
the 12:32 calls, then the merge of `a9cb2e3`, then this, over the live lane's tracked copy
`tests/fixtures/live3/m1_composer_bubble.html` -- and asked for a report after each.

Disk when this began: the integration committed, gated and reported (section "Integration 3");
master and the remote at `a9cb2e3`. The work in progress had been set aside as a patch at 14:20 and
went back on unchanged -- none of the four code files it touches moved in the merge. The path was
built, gated on the whole suite, then read by a cold reviewer, whose one defect and gaps were taken
up before this was reported (U.5).

### U.1 The chain, link by link, and the condition that holds each

    link  what must hold                              condition that refuses, and where it is read
    1     still on the link he gave                   1_navigated_away (the address before the press)
          the topcard is the person the title names   2_identity_lost: title shape, one topcard, its
                                                      first heading IS the title's name -- in the page
          a first-degree connection                   3_not_a_first_degree_connection
          no composer open anywhere before the press  the preview and the act refuse before pressing:
                                                      counted by the page's own script AND by the
                                                      engine the press uses (``composer_editors_pierced``)
    2     the owner's one visible Message control     the preview's existing conditions (unchanged)
          its address names the profile's member      6f_press_not_bound_to_them: every member slot in
                                                      the pressed address IS the profile's own member,
                                                      compared in the page (``CONTROL_FACTS_JS``)
    3     one composer in one bubble, one Send        5_not_one_conversation
          the new message readable                    4_unreadable (a failed piercing read)
          exactly one bubble on the page              6f_not_one_bubble
          somebody committed in the recipient box     7_recipient_box (a box with no one in it)
          the bubble is a new message                 6f_not_a_new_message (its one title, a token)
          one box, in that bubble, one recipient      6f_not_one_recipient -- every pill counted,
                                                      dismissible or not
          that recipient's drawn text IS the name     6f_recipient_not_theirs -- the name the title
                                                      gives, which link 1 tied to the topcard
          nobody else on the way in                   6f_another_recipient_on_the_way (search field)
          the recipient card links that profile only  6f_card_not_theirs (its /in/ segment, one, and
                                                      the topcard's own; a member id exactly)
          the one Send is that bubble's               6f_send_not_in_the_bubble
          empty, Send disabled; a before-count taken  8_not_empty, 9_no_before_count (unchanged)
    4     his words in the box, exactly               the send gate's 2 to 5, as for every message
          all of link 3 again, with the words in      0_read_failed, 6f_recipient_changed -- the
          the box                                     last moment
          SENT: a conversation headed by the name,    ``message_verdict``, on a reading taken in place
          holding his words, their count 0 -> 1       right after the press (``title_kind`` "owner",
                                                      a closed token -- no name crosses); the wait for
                                                      it kept in the receipt (``sent_words_wait``)
    5     one bubble, holding the composer            1_not_one_bubble
          one header control whose text opens         2_not_one_close_control
          on "Close"
          the close selector resolves one element,    3_selector_count -- the press is strict
          and it is one of the bubble's header
          controls
          the composer is empty                       4_words_in_the_box

Every reading starts at None or False and every condition asks for `is True` or a count of one, so
a field that could not be read refuses; a reading that raised is reported by its type and refuses.
The conditions marked `6f`, and 7 as it now reads, run only when a recipient box is drawn -- the
first contact's shape; a conversation that already exists takes condition 6 as before, and 1 to 5,
8 and 9 hold for both.

**WHERE THE READINGS COME FROM.** The overlay is in an open shadow root, so the bubble is judged by
``dom.BUBBLE_FACTS_JS`` over the elements Playwright's piercing engine resolves
(``dom.read_bubbles``, one call site, declared in `tests/test_readonly.py`: its evaluate budget 22 ->
23, its executed scripts 23 -> 24). It returns per bubble counts, booleans and one title token;
``dom._closed_bubble_facts`` re-closes each, and a value off its vocabulary reads in the direction
that refuses. The title and the recipient's name are compared on their DRAWN text (``innerText``),
as the page's own script compares a title; a member id in a card's address is compared exactly, a
vanity name with its ASCII case folded, as ``same_segment`` compares them.

**THE CLOSE CONTROL.** On the capture the header draws two controls, each carrying its words as its
own text: the expand button's and the close button's. The close button is a circle button, and its
words sit in its `artdeco-button__text` span -- which a circle button may draw visually hidden -- so
the control is found by its own text, the accessible name that text gives:
``role=button[name=/^Close\b/]`` inside the bubble's header controls, pressed through the one strict
click site, and the gate requires that one element to be one of the bubble's header controls. The
capture's words were reduced; "Close your draft conversation" is DERIVED from their shape (26
letters in four words, and the form's own "... for your draft conversation" labels) -- its first
word too, and only that word is read. Escape is never pressed.

### U.2 The fixture: built, synthetic, pinned

- `scripts/_build_first_contact_bubble.py` reads the live lane's tracked copy -- its default source
  -- and writes `tests/fixtures/synthetic/first_contact_bubble.html`: 125 elements, structure digest
  `ligiiccbckljhmoo` (tags and nesting), pinned in `tests/test_first_contact_message.py`. Built from
  the tracked copy and from the gitignored skeleton that copy was made from, the output is the same,
  byte for byte, digest and all. The fixture is a fixed point of its builder, and the words the
  builder keeps are a subset of the live lane's own kept list (a test says so).
- NOBODY IN IT IS ANYBODY: the recipient is the profile builder's declared synthetic person. The
  values put in place of reduced ones are named in the builder's docstring, each by the element it
  stands in, and four are argued as DERIVED -- the pill's label, the degree's words, the presence
  words, the close control's words. On the skeleton, by keyed hash and never read: the pill's text
  and the card's name WERE the topcard's name, and the card's two links named the topcard's own
  `/in/` segment. Those two comparisons cannot be re-derived from tracked files.
- THE SHADOW ROOT IS NOT IN THE FILE: the test's stand-in for LinkedIn's script opens the bubble
  inside an open shadow root when the owner's Message link is pressed, as the live page does -- and
  one test opens it outside one, to show the reading does not depend on where it is drawn. Each
  world is one named deviation from the capture.

### U.3 Red first, then green

- THE PATH, ON THE CODE BEFORE IT (this branch's head before the path): 16 of the first 23 cases
  red, 7 green. The 7 are the fixture's own tests. Of the 16: 11 the act refusing by
  `6_not_their_conversation` -- the live refusal reproduced offline; 2 more the act refusing at the
  opened gate; 3 on readings the path adds. After the build: 23 of 23.
- THE CORRECTIONS, ON THE PATH'S FIRST COMMIT (U.10): the test file, now 44 cases, 11 red, 33
  green. 8 red on substance: the defect (below), the preview issuing a confirmation beside it, a
  second recipient drawn as another pill, a minimised bubble beside the new one at the opened gate
  and again while typing, a Send outside the bubble at the opened gate and moved out of it while
  typing, and the conversation path acting in the shadow root. 3 red on readings added with them
  (the pierced count, the box in the bubble, the post-send wait). THE DEFECT, REPRODUCED on that commit's code by a scratch probe: a conversation titled with
  the name, open in the shadow root before the press, the press's own bubble 3 s late -- the act
  proceeded on the conversation path, the send gate passed, the old conversation took his words
  (`preSubmitted: 1`) and the receipt read `message_sent`. After the corrections: 44 of 44, and that
  world is refused before anything is pressed.

### U.4 What the repository's own guards found, fixed where they pointed

- THE NAVIGATION GUARD, red on the first draft: its taint is by NAME and module-wide, and the first
  contact's reading was bound to ``after``, ``state`` and ``why`` from a structure carrying the opened
  gate, which read ``page.url`` -- so two navigations' ``url`` read as derived. The locals took
  names of their own (``sent_*``), the remedy the named-profile loader took on the same trap.
- THE READER-LEAK GUARD: five new page-taking functions. Its baseline, regenerated by its own
  writer: four clean; ``named_profile.holding_bubble`` not driven, because the harness presses
  nothing and so no bubble holds a composer -- declared in ``WHAT_WOULD_DRIVE_IT`` as an ACTION,
  naming the test that drives it. The envelope and landing baselines rewrote unchanged, then and
  after the corrections.

### U.5 A cold review, and what it changed

A reviewer that wrote none of this read the path's first commit statically -- no tests run, no
browser, nothing edited -- against the addendum's chain: 1 DEFECT, 5 GAP headings, 23 NOTEs. It found
no way to type into, or Send, a new message addressed to anyone but the named person. Its findings,
each verified here before anything changed:

- **THE DEFECT: THE CONVERSATION PATH, MADE LIVE, COULD TYPE INTO A CONVERSATION THE PRESS DID NOT
  OPEN.** The first build had given the conversation path the piercing reading beside the page's own
  -- a change the order had not asked for, made so it could see a conversation in the shadow root.
  Its precondition "no composer open before the press" was still counted by the page's own script,
  blind there; the wait after the press returns on any composer; so a conversation already open,
  titled with the name -- a namesake's included -- took his words and read SENT (reproduced, U.3).
  TWO CHANGES: the precondition is counted by the engine the press uses too, at the preview and
  again before the press, for both paths; and the conversation path is LEFT AS IT WAS, as ordered --
  its "whose conversation" is the page's own reading again, at the opened gate, the send gate and
  the verdict, byte for byte, with one sentence added to its refusal saying what the piercing
  reading saw.
- GAPS AND NOTES TAKEN UP: exactly one bubble on the page (the chain's words; a minimised one beside the new
  message refuses, at both gates); every committed recipient counted, whatever pill it wears; the
  one box and the one Send are the new message's own; a failed piercing read refuses as unreadable,
  not as a missing recipient; the title and the recipient compared on their drawn text only; a
  member id compared exactly; the close gate's pressed element tied to the header controls; and a
  test for every reading of the last-moment check, the close gate's refusals 1 to 4 (its 0, a read
  that raises, has no world), a SENT
  denied when the title is not the name after the press, a labelled link naming no member (so the
  member binding, not the label, is what refuses), and the Escape counter shown counting one.
- NOTES RECORDED, NOT ACTED ON: a first contact's before-count is zero by construction, so SENT
  rests on the redraw alone (C2); the "last message is his" reading rests on a DERIVED selector (C4,
  as before); the close gate does not re-read whose bubble it closes -- it closes an empty composer,
  which sends nothing (D3); the bubble reader is capped at eight bubbles, safe only because every
  gate also counts page-wide (G2); the card could also be compared with the caller's own link, not
  only the topcard's (G4, a tightening, offered); the stand-in's post-send redraw is DERIVED (G5);
  the close gate's refusal 0 has no world that drives it; a recipient box now leads to the
  first-contact chain where condition 6 used to run first, and every bubble refused before is
  still refused (E2); the bubble's close-control count is read and reported, and the close gate
  decides on its own reading (G11's other half).

### U.6 The conversation path, left as it was -- and the question it leaves

Where LinkedIn draws an existing conversation inside the shadow root, the conversation path
refuses at 6, as it always has there; where the page's own script can see it, it acts as before (a
test holds each). Whether LinkedIn draws it there is DERIVED -- session 3 opened only a new message.
If it does, a second Message to the same person through this tool, after session 4's first
contact, refuses at 6; `linkedin_send_reply` in that conversation is the route, and it reads the
conversation's own page, not the overlay. Making the
conversation path live is the orchestrator's call: the change is the piercing reading beside the
page's own -- now that the precondition counts with the same engine -- and its residual is one
this path has always had in the page itself: a conversation restored DURING the press, headed by a
namesake, while the press draws nothing, would be taken for his. The first contact cannot be fooled
that way: its card must link the topcard's own profile.

### U.7 The record and the docs

- `_audit/_census/messaging-and-content.md` `M M1`: the path noted; state unchanged,
  COVERED-UNFIRED. `linkedin_message_from_profile`'s docstring describes the first contact.
- `_audit/INSTRUMENTS.md` 69.16, with the law the review taught.

### U.8 Gates

- RED FIRST, THEN GREEN: U.3, for the path and for its corrections.
- THE PATH'S FIRST COMMIT: before it, the guards the change reaches most directly -- 17 files, 1342
  of 1342; the navigation guard with CI=1 and the readonly scanner, 1028 of 1028; the census
  battery, 12 of 12. On it: the identity gate, 12 staged files, 0 hits; the navigation guard alone
  with CI=1, 685 of 685; the literal-repeat guard, 19 of 19 (598 files, 746 set and 4479 dict
  displays, no repeat); the builder re-run from the tracked copy and from the gitignored skeleton,
  both byte-identical to the committed fixture. THE WHOLE SUITE: the impact plan selected 258 of 285
  test files (91%) and widened -- PASS, 12316 tests, 1309 s.
- THE CORRECTIONS' COMMIT: before it, 19 guard files -- the navigation guard with CI=1, readonly,
  people and identity, reader leak, envelopes, landing, reachability, correction-findability,
  performable action, strict press, the named-profile read, route, adversarial and live-skeleton
  tests, page strings, writes, the literal-repeat guard and this path's own -- 2401 of 2401; this
  path's file, 44 of 44; the three derived baselines regenerated by their writers and unchanged; the
  census battery, 12 of 12, the index, blocker map and rulings register each at its fixed point.
  The identity gate on the commit: 7 staged files, 0 hits. THE WHOLE SUITE on it: the impact plan
  against the path's first commit selected 251 of 285 test files (88%) and widened -- PASS, 12337
  tests, 1981 s (the mutation check below shared the box for its first minutes).
- A MUTATION CHECK of the corrections, on an archived copy of their commit: each new check removed
  in turn, with the one test that should catch it -- 16 mutations, all as expected. 14 caught: the
  last-moment check's bubble, title, page-wide box, name, search, card and Send; the opened gate's
  one bubble and Send; every pill counted; the pre-press count, at the act and at the preview; the
  member binding against the label; and the conversation path given the piercing reading again. 2
  stay green because another check implies them, which is what they were run to show: one box in
  the bubble (the search field is that box) and one recipient (the name check counts recipients).
  NOT PINNED BY ANY WORLD: the failed-read refusals, names compared on drawn text only, the member id
  compared exactly, and the close press's tie to the header controls.
- This section's own commit is gated after it; its result is in the report.

### U.9 NOT known, and NOT run

- LIVE: nothing. The path has never fired; its first fire is session 4's, and that fire is its
  proof.
- UNMEASURED ON A LIVE PAGE: the bubble AFTER a first contact's Send -- that it becomes a
  conversation headed by the name, holding his words, with a close control whose text opens on
  "Close". The stand-in draws it so. If the page does otherwise the verdict does not read SENT, or
  the close gate refuses and the bubble stays on his screen; neither presses anything else.
- The close control's words are DERIVED from their shape; only "Close" is read.
- CI on this branch: nothing pushed.

### U.10 Commits -- on this branch, none pushed, no AI attribution in any

    fe09de5  message_from_profile: a first contact, proven by a chain and read through the
             shadow root
    dc6e349  message_from_profile: a cold review's defect and gaps, and the conversation path
             left as it was
    (last)   this section

## Session 4's refusal: the Send wait and the draft rule (the orchestrator's order of 2026-09-28 17:37)

**THE ORDER.** Session 4 fired the first-contact path live. Every link of the chain held -- one
bubble, a new message, one box with one committed recipient equal to the name, the search field
empty, the card linking his profile, the pressed link naming his member, Send in the bubble, the
composer in 1.3 s -- and the words went in, 65 of 65, exact. Then the last-moment check refused at
`4_fill_not_landed`: Send read DISABLED straight after the fill. Nothing was pressed and nothing
reached him; the verdict read unknown, his words left in the composer. About a second later a
piercing skeleton of the same bubble drew Send WITHOUT `disabled`. The order: (1) after the fill, a
BOUNDED liveness wait -- up to 5 s, through the piercing engine -- for the bubble's own Send to lose
`disabled`, then the whole check as now, pressing only if every condition still holds, and refusing
as today if Send never turns on; (2) THE DRAFT RULE -- LinkedIn may keep the unsent words, and the
next press opens the composer non-empty, which refuses at 8 forever: a box holding text EXACTLY
the grant's words, whole and nothing else, skips typing and goes to the wait and the check, and any
other pre-filled text refuses as today; (3) fixtures built from the live lane's captures through
the builder, synthetic names, pinned digests, red first on today's code; (4) the gates; (5) commit
with no attribution, no push, and the then-current master integrated once at the end.

Disk at 17:37 agreed: master and the remote at this branch's head (the first-contact path's last
commit), the live lane's session-4 files present in its own gitignored state -- read only, and read
REDACTED: numbers, booleans and short closed tokens, every other string its length only. `shape.key`
was not opened.

### V.1 What the live lane's files show

- THE RECEIPT, VERIFIED from its numbers and booleans: the opened gate proceeded -- bubbles 1, one
  holding the composer, the box in it 1, recipients 1, theirs, the search empty, the card theirs,
  Send in the bubble 1, the pressed link naming the member, the editor empty, Send disabled, the
  composer drawn in 1347 ms. The send gate refused with the words exact (65 of 65) and
  `send_enabled` false. The typed-text block: entered, submit never pressed, left in the composer.
  Clicks 1, the opener only.
- THE LATER READING, by this lane's own bubble reader on the live page: one bubble, a new message,
  one pill naming the owner, the search empty, the card matching, one Send in the bubble -- and ONE
  HEADER CONTROL WHOSE TEXT OPENS ON "Close". The close control's first word is now MEASURED; the
  rest of its words stay DERIVED and are never read.
- THE TWO SKELETONS SIDE BY SIDE (their outlines, shapes only): the bubble after the fill differs
  from session 3's empty one in exactly three places -- the editor's paragraph holds a text of 65
  characters where it held a line break, two classes moved (the content container's active state,
  the placeholder's own class), and Send lost `disabled`.

### V.2 The Send wait

`named_profile.wait_for_send_enabled`: after his words are in the box, a first contact waits, up to
`SEND_ENABLED_WAIT_MS` (5 s), for the Send INSIDE the one bubble holding the composer to be drawn
without `disabled` -- a CSS locator through Playwright's piercing engine, the bubble being in a
shadow root; no script runs in the page. It decides nothing: `writes._first_contact_send_check`
runs it and then the whole last-moment check as before -- the editor, the Send, the fill landed,
the words exact, and every link of the chain again -- and Send is queued only if all of that holds.
A Send still disabled at the bound refuses at 4 as before. The receipt carries the wait
(`send_enabled_wait`: whether Send turned on, and the milliseconds waited). A first contact only:
the conversation path is left as it was.

### V.3 The draft rule

- THE READING: `read_opened_conversation` now also says whether the one editor holds EXACTLY the
  grant's words, whole and nothing else (`editor_holds_the_words`), compared in this process as the
  send gate compares them; only the boolean crosses.
- THE CONDITION: at 8, a FIRST CONTACT whose box is not empty but holds exactly those words
  proceeds, marked `words_in_place`, with Send's state left to the wait and the check. Any other
  text -- other words, his words and more, part of his words -- refuses at 8 as before; so does
  every box on the conversation path.
- THE ROUTE: `writes.perform` types nothing for it and goes straight to the wait and the check; the
  verdict counts his words as in the box; the receipt's typed-text block says NOTHING WAS TYPED and
  the words were already there, and whether Send was pressed -- where it would have said there was
  no draft to clear.

### V.4 The fixture: the second capture

`scripts/_build_first_contact_bubble.py --kind filled`, over the live lane's session-4 skeleton,
wrote `tests/fixtures/synthetic/first_contact_bubble_filled.html`: 124 elements, structure digest
`ppnjobnklaocacjm` -- printed over the skeleton and over the built file -- a fixed point of its
builder. The same declared synthetic person; the editor's words are the builder's `TYPED_WORDS`,
declared, fitted to the reduced words' shape (65 characters, 53 letters, no digit), and a test
grants exactly them to model a draft. The empty fixture came out byte-identical under the builder's
change. The session-4 skeleton has no tracked copy yet, so this fixture cannot be re-derived from
tracked files; if the live lane exports one, a test can pin it as the session-3 copy is pinned.

THE DRAFT WORLD IS DERIVED: nobody has captured a reopened draft. The tests model it as the filled
bubble opened by the press; what LinkedIn draws on the next press is session 5's measurement. If it
keeps the words but not an enabled Send, the wait runs out and the check refuses at 4 -- nothing
pressed.

### V.5 Red first, then green

- `tests/test_first_contact_message.py`, 59 cases, on MASTER'S CODE (the builder and the new
  fixture copied in, so every red is the product's): 11 red, 48 green. 2 red ON SUBSTANCE -- the
  session-4 world, Send turning on a second after the fill, and a draft holding exactly his words.
  9 red on the readings the order adds (the wait, its bound, its receipt field, the draft's
  reading). PROBES of master's code in those two worlds: the first -- the opened gate passes, the
  check refuses at 4 with Send disabled and the words exact, the verdict unknown, the words typed
  and left in the box: SESSION 4'S RECEIPT, REPRODUCED OFFLINE; the second -- refused at 8, and the
  receipt said there was no draft to clear.
- Here: 59 of 59.
- A MUTATION CHECK on an archived copy of the commit, each new check removed in turn with the one
  test that should catch it: 8 of 8 caught -- no wait; the wait taking a disabled Send (twice: the
  timing world, and the empty capture); the draft rule taking any text, or part of his words; the
  draft rule on the conversation path too; a draft's words not counted as in the box; the residue
  not told of the draft. Control: the same 8 targets pass unmutated.

### V.6 The record and the docs

- `_audit/_census/messaging-and-content.md` `M M1`: the wait, the draft rule and the measured
  first word noted; state unchanged, COVERED-UNFIRED, its first fire session 5's.
- `linkedin_message_from_profile`'s docstring: the wait and the draft rule, in his words.
- `_audit/INSTRUMENTS.md` 69.17.

### V.7 Gates

- RED FIRST, THEN GREEN, AND MUTATED: V.5.
- BEFORE THE COMMIT: the guard files -- the navigation guard with CI=1, readonly, people and
  identity, reader leak, envelopes, landing, reachability, correction-findability, performable
  action, strict press, the named-profile read, route, adversarial and live-skeleton tests, page
  strings, writes, the literal-repeat guard and this path's own -- 19 files, 2424 of 2424; the
  three derived baselines regenerated by their writers (two new readers, both clean; the envelope
  and landing baselines unchanged); the census battery, 12 of 12, the index, blocker map and
  rulings register each at its fixed point; the record and people guards, 183 of 183.
- THE IDENTITY GATE ON THE COMMIT: 9 staged files, 0 hits.
- THE WHOLE SUITE on the commit: the impact plan against master's head selected 222 of
  285 test files (78%) and widened -- PASS, 12360 tests, 3336 s (two other lanes' gates shared the
  box for most of it).
- This section's own commit is gated after it; its result is in the report.

### V.8 NOT known, NOT run, and put to the orchestrator

- THE VERDICT WHEN SEND IS NEVER PRESSED reads "unknown", as it did in session 4, with its "do not
  retry" -- the shared verdict cannot see the title in the shadow root -- although no Send press
  happened and the receipt says so. Kept, as ordered ("refuse as today"); making it read "not sent"
  when no Send was pressed is one change, the orchestrator's call.
- THE BOUND: 5 s against a measured "about a second" -- measured no finer.
- A DRAFT'S ATTACHMENT: if LinkedIn kept a file or image with the words, nothing here reads it; no
  capture holds one.
- THE CONVERSATION PATH has the same race in principle, and is untouched: left as it was, and blind
  in the shadow root at 6 before any fill.
- LIVE: nothing. CI on this branch: nothing pushed.

### V.9 Commits -- on this branch, none pushed, no AI attribution in any

    5fcab6b  message_from_profile: wait for a first contact's Send to turn on, and do not
             retype a draft of his words
    (last)   this section
