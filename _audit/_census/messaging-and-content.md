# Capability census -- MESSAGING AND CONTENT

**Slice owner: census wave, messaging-and-content. 2026-09-03. Read-only; nothing in the
repo was modified and nothing was committed. The operator's LinkedIn account was not
touched -- no browser, no session, no page load was performed for this document.**

The question the whole census answers is *"everything I can do on LinkedIn directly --
can I do it through this MCP?"* This file computes the messaging-and-content part of the
denominator by walking LinkedIn's own Help Center topic tree and mapping each capability
it advertises against the code in `linkedin_server/`.

---

## 1. THE COUNTS

**REVISED 2026-09-03 after a second pass over this file's own declared holes, using
LinkedIn's help-article index (`/help/linkedin/search?q=`). The denominator moved
120 -> 142. Every added row is a GAP but one.** Section 2 records what the re-check
found, hole by hole, including the holes that came back empty.

| | first pass | after re-check | delta |
|---|---:|---:|---:|
| **denominator** | **120** | **142** | **+22** |
| messaging | 45 | 51 | +6 |
| content | 75 | 91 | +16 |

**Denominator: 142 member-performable capabilities** -- 51 messaging, 91 content.
Every row is sourced to a LinkedIn Help Center page; none was recalled from memory.

| state | count | share | delta |
|---|---:|---:|---:|
| COVERED-PROVEN -- tool exists, audits record it firing and returning its payload | **2** | 1.4% | 0 |
| COVERED-UNFIRED -- tool exists, never returned its payload live | **7** | 4.9% | 0 |
| COVERED-CANNOT-DELIVER -- tool exists and is structurally unable to complete | **2** | 1.4% | 0 |
| EXCLUDED-RULED -- no tool, written reason in the repo | **22** | 15.5% | +1 |
| GAP -- no tool and no reason; nobody considered it | **109** | 76.8% | +21 |
| | **142** | | |

Split by half:

| | messaging (51) | content (91) |
|---|---:|---:|
| COVERED-PROVEN | 1 | 1 |
| COVERED-UNFIRED | 3 | 4 |
| COVERED-CANNOT-DELIVER | 2 | 0 |
| EXCLUDED-RULED | 5 | 17 |
| GAP | 40 | 69 |

**The coverage numerator did not move.** 22 capabilities were added and not one of them
found hidden coverage: 21 are GAPs and 1 (delete an article) falls under an existing
prohibition. That is the load-bearing result of the re-check -- **the hole was bigger,
not shallower.**

**The one-line reading: this slice is 9 capabilities covered out of 142, and 109 of the
142 have never been thought about.** The repo's own prose is dense, careful and honest
about the 21 it ruled on -- and that density is what makes the 88 easy to miss. A reader
of `README.md` or of the tool docstrings would come away believing the messaging and
content surface had been thoroughly considered. It has been thoroughly considered along
ONE axis -- publish / comment / react / send-one-message -- and not at all along the
other twelve (attachments, group chats, conversation management, saved posts, hashtags,
Groups, Events, Live, newsletters, analytics, collaborative posts, media of any kind).

A fifth state was added rather than forcing a four-way fit. `send_message` is not
COVERED-UNFIRED: it HAS fired, live, against a real composer, and it cannot deliver.
Filing it as UNFIRED would say "nobody has tried yet", which is the opposite of what was
measured. See section 3.

---

## 2. WHAT WAS WALKED, AND WHAT WAS NOT

An unwalked area is a hole in the denominator, not a zero.

### Walked (topic trees enumerated in full)

| Help Center area | URL | articles enumerated |
|---|---|---:|
| Help root topic list | `/help/linkedin` | 6 top-level topics |
| **Messaging** | `/help/linkedin/topic/a148003` | 28 |
| **Share Content** | `/help/linkedin/topic/a148004` | 60 |
| **Post** | `/help/linkedin/topic/a150004` | 60 |
| **Groups** | `/help/linkedin/topic/a153002` | 14 |
| Events | `/help/linkedin/topic/a150003` | **0 -- the topic page is empty** |
| LinkedIn Live | `/help/linkedin/topic/a151003` | **0 -- the topic page is empty** |

The two empty topic pages are a real hazard: Events and LinkedIn Live plainly exist as
products (`/help/linkedin/answer/a554183`, `a548541`, `a550232` are live Events articles
reachable by search), but their topic pages return `0 articles`, so a walker who trusted
the topic tree alone would score them as non-existent. They were recovered by search and
are counted here; anything else hiding behind an empty topic page is not.

### Walked (individual articles read in full)

`a564261` LinkedIn Messaging overview - `a563259` photo/video/GIF/emoji in a message -
`a552485` message requests - `a550661` edit or delete a sent message - `a1347212`
schedule posts - `a528190` LinkedIn reactions - `a524166` comment on posts and reply to
a comment - `a527126` save content in your feed - `a525047` repost - plus targeted
searches that surfaced `a563264` (forward), `a568326` (leave a conversation), `a550440`
(archive/restore), `a567370` (read receipts and typing indicators), `a711117` (Focused
Inbox), `a550614` (away message, Premium), `a569446`/`a552111` (smart/reply suggestions),
`a528144` (hashtags and follow topics), `a566460`/`a540824`/`a542733` (Groups membership),
video meetings in messaging.

### The instrument that closed the holes (added 2026-09-03)

    https://www.linkedin.com/help/linkedin/search?q=<terms>

It queries LinkedIn's OWN article index, so unlike an external engine it cannot miss an
article nobody crawled. The parameter name is load-bearing: `?query=`, `?keywords=`,
`?searchTerm=`, `?term=` and `?text=` all return HTTP 400. Fourteen queries were run.
**This instrument is strictly better than a topic-tree walk and should be the default for
any future census pass** -- it recovered 22 capabilities that four fully-enumerated topic
trees did not contain.

### Holes re-checked, hole by hole

| hole declared in pass 1 | verdict | delta |
|---|---|---:|
| `/help/recruiter/*` licence assumption | **CONFIRMED, with a correction** | +2 |
| `/help/lms/*`, `/help/sales-navigator/*` | **CONFIRMED empty for a Premium Career member** | 0 |
| Pages-admin content | **CONFIRMED as a real boundary** | 0 |
| `Data and Privacy` (`topic/a65`) | **CHECKED, near-empty for this slice** | +3 |
| `Basics` (`topic/a51`) | **CHECKED, empty of anything new** | 0 |
| Newsletters | **REAL HOLE** | +5 |
| Articles | **REAL HOLE** | +4 |
| Polls | **REAL HOLE** | +1 |
| Scheduled posts | **CONFIRMED correct** | 0 |
| Live-adjacent | **REAL HOLE, reassigned** | 0 (see s10) |
| Comments / reactions / mentions | **REAL HOLE** | +6 |
| Messaging attachments, voice, archive, InMail | **REAL HOLE** | +6 |
| Saved posts | **CHECKED, empty** | 0 |
| Hashtags | **SOURCE WAS DEAD** | -1 |

**1. The licence assumption was right, and resting on it cost two rows anyway.**
`q=recruiter inmail` returned ten articles and **all ten sit under `/help/linkedin/`, the
member index, not `/help/recruiter/`.** So excluding the Recruiter PRODUCT is correct
(`a1376069` "Individual Account vs. Recruiter Account", `a417251` on the Recruiter tiers,
confirm the licence line is real) -- but the member index carries member-side InMail
capabilities that my Messaging topic walk did not list: **M46 opt out of receiving InMail**
and **M47 respond to a Recruiter InMail**. The assumption was sound; not measuring it
still hid two rows, one of which is the most job-hunt-relevant messaging action in the
slice.

**2. `/help/lms/*` and `/help/sales-navigator/*` -- confirmed empty.** No query returned
a member-performable capability from either. The only crossings were `a549501`
"Automatically archived Sponsored Messaging ads" and `a1382752`, both advertiser-side.
Checked and empty is a result, not silence.

**3. Pages-admin -- confirmed as a real boundary, and the check strengthened it.**
`q=scheduled post` returned five Page-level scheduling articles (`a1419179`, `a548192`,
`a1424039`, `a1427033`, `a9599594`) sitting beside the one member article `a1347212`.
LinkedIn documents the two surfaces separately, which is exactly what a defensible
exclusion needs. Same pattern for `a551424` (repost a Page post), `a548396` (delete
comments on a Page post), `a567534` (edit a Page article). The member/Page split holds.

**4. `Data and Privacy` -- checked, and near-empty FOR THIS SLICE.** `q=privacy settings
visibility` returned eleven articles; nine are profile or network identity (connection
visibility, birthday, email, profile photo, last name, who's-viewed). Only `a595755`
"Follow visibility" and the generic `a1338877` touch content. The mention/tag privacy
family (`a522861`, `a524212`, `a524346`) came in through `q=mention tag people in post`
instead and is counted as C87-C89. **The hole cost three rows, not thirty** -- worth
knowing, because it is the hole I was least able to size from outside.

**5. `Basics` -- walked, 26 articles, nothing new.** Its only two content articles are
`a526256` and `a528132` (edit and delete comments in the feed), both already recovered
through `q=comment`. Genuinely empty.

**6. The thin-index class was the real damage.** Newsletters went 2 rows -> 7,
articles 5 -> 9, polls 1 -> 2, and the comment/reaction/mention families gained six.
None of it was hiding behind an empty topic page -- **it was hiding inside topic pages
that listed 60 articles each and still did not list these.** That is a worse failure mode
than the Events/Live empty-index hazard, because a 60-article listing reads as exhaustive.

**7. One row was WRONG, not merely missing.** C52/C53 rested on `a528144`
("Use Hashtags and Follow Topics"), which **returns HTTP 404**. Two independent index
queries (`q=hashtag`, `q=follow topics interests feed`) return no hashtag-following
article at all. The URL had reached me through an external search with a mangled locale
suffix. C52 is rewritten to what LinkedIn's index does document (`a528074`, feed
preferences) and C53 is retired in place rather than deleted. **This is the one place
where the first pass asserted a LinkedIn capability that its own help index does not
support.**

### Still NOT reached

1. **The `Media`, `Creators Core` and `Custom Content` subtopic pages** as topic trees.
   Their articles were reached transitively and via search, so coverage is good but not
   provably exhaustive.
2. **Group-admin and Event-organizer surfaces.** `q=group members invite` returned eight
   "(Group Management)" articles -- approve, block, unblock, remove, promote, merge,
   message all members. Excluded as admin, on the same basis as Pages. If the operator
   owns a group, that is another unwalked surface.
3. **Mobile-only affordances.** Every count is the desktop web surface, the only one this
   server can drive. Mobile-only paths are still counted as capabilities, because the
   question is what LinkedIn offers.
4. **Whether the operator administers a Page or owns a Group.** Both exclusions in this
   file are conditioned on him doing neither, and that is still an assumption. It is a
   one-question answer and nobody has asked it.

---

## 3. THE TWO SETTLED FACTS (recorded, not re-derived)

### 3.1 `linkedin_send_message` is a tool that exists and cannot deliver

It is not unbuilt, not ungated and not untried. It shipped 2026-09-02, it fired live on
2026-09-03 against the operator's real composer, and its addressing route is dead.

`_audit/2026-09-03-typeahead-name-matching-is-dead.md:24-30`:

> ```
> every row LinkedIn returns contains the needle            10 of 10
> no row BEGINS with the needle                              0 of 10
> the needle starts at ELEVEN different character offsets
> the offsets sum to 17 placements across 10 rows
> the labels run 49 to 178 characters
> ```

and at `:44-47`:

> **A NAME IS THE WRONG ADDRESSING PRIMITIVE FOR THIS SURFACE.** Every other write in
> this package addresses its target by IDENTIFIER: a job id, a company id, an item urn.
> `send_message` was the only one addressing a human being by the text of their name, and
> the text is not theirs.

The prior live run at `:49-53` is the fire itself -- a real fill landed in a real
composer and the gate stopped before Send:

> **2026-09-03, earlier.** `linkedin_send_message` shipped expecting to refuse, and it
> did. A supervised run typed a correct, first-degree name into an empty composer;
> `writes._recipient_gate` returned `1_no_recipient_committed` with all four chip
> selectors reading zero. **A bare fill commits nobody.** Typing into a typeahead is not
> choosing from it.

The replacement route is found and not built (`:186-203`): LinkedIn's own
compose-by-identifier url, currently refused by the read boundary on purpose while three
accidental sibling spellings are closed first. And the residue that survives the fix,
same file:

> **WHAT STILL LANDS ON WHOEVER TAKES IT:** *no instrument has ever observed a committed
> recipient.* The chip selectors in section 3.1 have never matched anything on any page.
> Addressing by identifier removes the CHOOSING problem; it does not remove the OBSERVING
> one.

Two further properties, both from `linkedin_server/server.py:4542-4568`, make the state
name exact rather than pessimistic -- it can report NOT SENT and can never report SENT:

> IT CAN REPORT NOT SENT AND CAN NEVER REPORT SENT. The only surface that could confirm a
> send is the thread, which is forbidden here and costs a read receipt to look at.

**So M1 and M2 are COVERED-CANNOT-DELIVER: a tool that exists, has run, and cannot put a
message in front of a named person.** Any downstream planning that reads "send_message
exists" as "messaging is covered" is wrong in the way that matters.

### 3.2 Post deletion is recorded UNMEASURED because the overflow menu has never been opened

`linkedin_server/server.py:4098-4101` (the `linkedin_publish_post` docstring):

> WHAT IT COSTS. This is a BROADCAST under your own name -- 274 followers, and past posts
> measured at 113, 319 and 1,287 impressions. **Whether a post can be deleted is
> UNMEASURED: the per-post overflow menu has never been opened.**

The same finding, longer, in the spec's own reversibility evidence at
`linkedin_server/writes.py:991-999`:

> NOT MEASURED, and the shape of the gap is worth stating because it is the same one the
> notifications census hit. Each post draws an overflow control -- `Open control menu for
> post by <him>`, measured 8 times on his own profile -- and it renders
> `aria-expanded='false'`. **Its ITEMS have never been read.** So whether LinkedIn offers
> Delete on a post is something this server has not established, and the notifications
> precedent is that an unopened overflow menu is not evidence about what is inside it.

Restated in the wave record at `_audit/2026-08-31-linkedin-finish.md:554-559`, with the
sentence that sets the stakes for every content write in this slice:

> Whether a post can be deleted is UNMEASURED -- the per-post overflow menu renders
> collapsed and its items have never been read -- and deletion is permanently forbidden
> here regardless. It is also the one artefact in this whole design that a current
> employer sees without looking for it.

---

## 4. THE READ BOUNDARY IS THE STRUCTURAL CAUSE OF MOST OF THE 88

Before the tables, the single fact that explains the shape of this slice. The complete
read allowlist in `linkedin_server/readonly.py` is 22 url patterns:

```
/messaging/                            /in/me/
/messaging/thread/<id>/                /in/<slug>/
/messaging/compose/     (exact, by exemption)
/analytics/profile-views/              /in/<slug>/details/(skills|experience|education)/
/me/profile-views/                     /in/me/edit/intro/
/jobs-tracker/?stage=(saved|applied|draft)
/jobs/search/                          /mynetwork/network-manager/company/
/jobs/view/<digits>/                   /mypreferences/d/
/feed/                                 /mypreferences/d/dark-mode/
/feed/update/urn:li:<type>:<digits>/   /notifications/
/preload/sharebox/                     /premium/my-premium/
/article/new/                          /login/
```

**Nothing in that list reaches Groups, Events, LinkedIn Live, newsletters, saved posts,
hashtags, article drafts, post analytics, creator analytics, the scheduled-posts surface,
or any media-upload surface.** Those are not refused capabilities; they are addresses
nobody has ever proposed. `_audit/2026-08-31-linkedin-lift.md:61-137` enumerates 17
addresses tried and refused during the draft hunt -- and every one of the 17 was tried
in service of ONE capability (detecting a draft before publishing a post). No comparable
enumeration exists for any other content surface.

Second structural fact, `linkedin_server/writes.py:4874-4880`:

> WHAT THE LIST DOES STILL REFUSE, and it is the real blocker for four of the remaining
> seven: `fill`, `type`, `press` and `keyboard` are all on
> `readonly._MUTATION_CALL_PATTERNS` and NONE of them is on `SANCTIONED_MUTATIONS` for
> any function in this package.

`fill` has since been sanctioned. `set_input_files` -- the mutation class every media
upload in this slice needs (photo, video, document, article cover image, message
attachment, voice note) -- **has not been, and no document in the repo has ever discussed
it.** That single unsanctioned mutation class silently accounts for 9 of the 88 GAPs.

---

## 5. MESSAGING -- 45 capabilities

R/W = whether the capability is a read or a write on LinkedIn.
REV = REVERSIBLE / NOT, judged from LinkedIn's own product behaviour as documented, not
from what this server could do about it.

| # | capability | Help Center | state | R/W | REV | evidence, or what a GAP would take |
|---|---|---|---|---|---|---|
| M1 | Send a message to a 1st-degree connection | a541865 | **CANNOT-DELIVER** | W | **NOT** | `linkedin_send_message`; fired live 2026-09-03, refused at `_recipient_gate`. See s3.1 |
| M2 | Send an InMail to a non-connection | a546814 | **CANNOT-DELIVER** | W | **NOT** | same tool, same gate; additionally spends a metered credit whose size is unreadable |
| M3 | Choose the dispatch mode (message vs InMail) | a546814 | EXCLUDED-RULED | W | NOT | `_TEAM_LEAD_SUCCESSOR_BRIEF.md:63-80`: "**DO NOT touch the dispatch radios.** Use the checked default" |
| M4 | View available InMail credit balance | a543685 | EXCLUDED-RULED | R | REV | `readonly.py:411-433` admits `/premium/my-premium/` for exactly this and it carries no balance; `perform.md:3462-3487`: InMail on the composer is "a conversation FILTER PILL -- five independent readings" |
| M5 | Send an Open Profile message | a544787 | GAP | W | **NOT** | needs a third party's profile loaded to find the control -- collides with the `who_viewed_me` emission ruling |
| M6 | Send a message request | a552485 | GAP | W | **NOT** | zero hits for "message request" anywhere in the repo |
| M7 | Accept a message request | a552485 | GAP | W | NOT | a control on a surface never enumerated |
| M8 | Decline a message request | a552485 | GAP | W | REV (a declined request can be reviewed and accepted later) | same |
| M9 | Review previously declined requests | a552485 | GAP | R | REV | an unnamed sub-surface of `/messaging/` |
| M10 | Reply to a message in a thread | a541934 | GAP | W | **NOT** | `/messaging/thread/<id>/` IS on the read allowlist; nothing writes to it. A reply-in-thread editor has never been censused |
| M11 | Edit a sent message (60-min window) | a550661 | GAP | W | NOT (edit leaves an "Edited" label) | per-message overflow menu, never opened. `/edit/` is a forbidden substring but it is a url guard and this control is in-thread |
| M12 | Delete a sent message (60-min window) | a550661 | EXCLUDED-RULED | W | **NOT** | `writes.py:1801-1814` `delete_or_withdraw_anything`: "destruction is not a write this design covers, at any confirm level" |
| M13 | Forward a message | a563264 | GAP | W | **NOT** | never named; forwards a third party's words to another third party |
| M14 | Attach a photo to a message | a563259 | GAP | W | NOT | needs `set_input_files` sanctioned -- an unsanctioned mutation class (s4) |
| M15 | Attach a video to a message | a563259 | GAP | W | NOT | same mutation class |
| M16 | Send a GIF | a563259 | GAP | W | NOT | a picker surface, never censused |
| M17 | Send an emoji | a563259 | GAP | W | NOT | a picker surface, never censused |
| M18 | Attach files (max 5, 20 MB total) | a148003 | GAP | W | NOT | same mutation class as M14 |
| M19 | Send a voice message | a148003 | GAP | W | NOT | zero hits for "voice" in the repo; needs microphone capture, outside anything this design contemplates |
| M20 | Start or schedule a video meeting from a message | video-meetings help | GAP | W | REV (a link can be revoked) | never named |
| M21 | Create a group chat | a566306 | GAP | W | **NOT** | multi-recipient addressing; strictly harder than M1, which is dead |
| M22 | Add or remove group-chat participants | a554447 | GAP | W | NOT | never named |
| M23 | Mention people in a group chat | a565352 | GAP | W | NOT | never named |
| M24 | Manage group-chat notification settings | a1420321 | GAP | W | REV | a settings sub-surface, unenumerated |
| M25 | Leave a conversation | a568326 | GAP | W | **NOT** ("you will not be able to reply or re-join") | never named; adjacent to but not covered by `delete_or_withdraw_anything` |
| M26 | Delete a conversation or group chat | a543838 | EXCLUDED-RULED | W | **NOT** | `writes.py:1801-1814`, same entry as M12 |
| M27 | Archive a conversation | a550440 | GAP | W | REV (restorable) | zero hits for "archive" as a messaging action |
| M28 | View and restore archived conversations | a550440 | GAP | R+W | REV | same |
| M29 | Mute or unmute a conversation | a565292 | GAP | W | REV | zero hits for "mute" |
| M30 | Star a conversation | a1430963 | GAP | W | REV | "Starred" exists in the repo only as one of seven activatable FILTER pills (`dom.py:2269-2276`); starring itself was never considered |
| M31 | Mark a conversation read or unread | a549532 | GAP | W | REV (both directions exist in the product) | never named. The `mark_notifications_read` prohibition is a different surface, though its reasoning transfers |
| M32 | Bulk delete / archive / mark read | a549532 | GAP | W | mixed | never named; the delete third would be caught by `delete_or_withdraw_anything` |
| M33 | Apply an inbox filter pill (Focused, Other, Unread, Starred, Connections, Jobs, InMail) | a711117, a542831 | COVERED-UNFIRED | R | REV | `linkedin_open_messaging(message_filter=...)`; closed set of 7 at `dom.py:2269-2276`, the second entry in `readonly.SANCTIONED_MUTATIONS`. Never run live |
| M34 | Search messages by keyword | a539848, a542831 | GAP | R | REV | `linkedin_open_messaging` takes no query parameter |
| M35 | Choose Messaging inbox layout | a7449032 | GAP | W | REV | never named |
| M36 | Manage how new conversations open (conversation windows) | a563389, a569449 | GAP | W | REV | never named |
| M37 | Turn read receipts and typing indicators on or off | a567370 | GAP | W | REV | `linkedin_update_setting` exists but reaches exactly one setting (`/mypreferences/d/dark-mode`); `/psettings/` and `/settings/` are forbidden substrings, so a route exists as a boundary while the capability itself was never reasoned about |
| M38 | Report a message as spam | a564261 | GAP | W | NOT | never named |
| M39 | Set or edit an away message (Premium) | a550614 | EXCLUDED-RULED | W | REV | `writes.py:1829-1832` `auto_accept_or_auto_reply`: "a reply in his name that he did not read is a message from a stranger wearing his face" |
| M40 | Use smart replies / reply suggestions | a569446, a552111 | GAP | W | NOT (the reply is sent) | never named; the away-message ruling does not cover a suggestion the operator picks |
| M41 | Manage smart features in Messaging | a1431517 | GAP | W | REV | never named |
| M42 | Settings to allow or prevent messages from group members | a541708 | GAP | W | REV | never named |
| M43 | Open the inbox and list conversations | a564261 | COVERED-UNFIRED | R | REV | `linkedin_open_messaging`. Deliberately never called: `_audit/2026-08-30-linkedin-writes.md:335-336` -- "**This wave did NOT call `linkedin_open_messaging`.** The cost lands on somebody who is not him, so it is his to spend." |
| M44 | See the unread-messages badge count | a564261 | **COVERED-PROVEN** | R | REV | `linkedin_new_messages`; measured `Messaging, 0 new notifications` on both feed and profile, 2026-08-30. Reads the badge off a page already open; loads no messaging surface |
| M45 | Open a blank compose window | a541865 | COVERED-UNFIRED | R | REV | `linkedin_compose_fields` loads `/messaging/compose/` by exemption. Fired live 2026-09-02 and returned `refused: name_shaped_label_present`; the design was confirmed by a different instrument and the repaired build has not been re-run |
| M46 | Opt out of receiving InMail messages | a554229 | GAP | W | REV | recovered 2026-09-03 by help-index search. A member-side InMail control the whole InMail discussion in this repo never mentions -- every sentence there is about SPENDING a credit, none about the receiving end |
| M47 | Respond to a Recruiter InMail (Interested / Not interested) | a552643 | GAP | W | **NOT** | recovered by help-index search. Distinct from a plain reply: it is a structured response with its own affordances, and it is the single most job-hunt-relevant messaging action in this slice |
| M48 | React to a message with an emoji | a552661 | GAP | W | REV | recovered by help-index search. Reactions exist on MESSAGES as well as posts; `react_to_item` addresses feed items only and nothing in the repo mentions the messaging case |
| M49 | Read message delivery / read indicators | a569649 | GAP | R | REV | recovered by help-index search. `linkedin_open_messaging` returns per-row unread flags for HIS state; the sender-side indicators are a different signal and were never enumerated |
| M50 | Manage LinkedIn message nudges | a568627 | GAP | W | REV | recovered by help-index search; never named |
| M51 | Use LinkedIn AI-powered conversation in messaging | a10346037 | GAP | W | NOT (it sends) | recovered by help-index search. Distinct from M40 smart replies; adjacent to the `auto_accept_or_auto_reply` prohibition without being covered by it |

---

## 6. CONTENT -- 75 capabilities

| # | capability | Help Center | state | R/W | REV | evidence, or what a GAP would take |
|---|---|---|---|---|---|---|
| C1 | Publish a text post | a518996 | COVERED-UNFIRED | W | **NOT** | `linkedin_publish_post`. Zero `confirm_token`s ever minted or used (`perform.md:1794-1799`); its submit selector was measured broken on 2026-09-01 and repaired without ever firing (`perform.md:2620-2662`) |
| C2 | Choose the post's audience / visibility | a523141 | GAP | W | NOT | `linkedin_publish_post(text, confirm_token)` has no audience parameter. Every post it could publish goes out at whatever LinkedIn's default is, unread and unchosen |
| C3 | Post a photo | a527229 | GAP | W | NOT | `set_input_files` unsanctioned (s4) |
| C4 | Post a video | a7174587, a554001 | GAP | W | NOT | same |
| C5 | Post a document (PDF / carousel) | a518909 | GAP | W | NOT | same |
| C6 | Add a title to an uploaded document | a517910 | GAP | W | REV | depends on C5 |
| C7 | Add alt text to a post image | a519856 | GAP | W | REV | depends on C3; an accessibility obligation nobody has counted |
| C8 | Create a poll | a522948 | GAP | W | NOT | zero hits for "poll"; a distinct composer mode never censused |
| C9 | Post a celebration ("Celebrate an occasion") | a518996 | GAP | W | NOT | zero hits for "celebration" |
| C10 | Mention a person or company in a post | a525082 | GAP | W | NOT | zero hits. Note the opposing constraint: `tests/test_typed_bytes.py` asserts on the AST node "because the substring version passed a mutation that appended a hashtag" -- the suite actively guards against the server adding anything to his text |
| C11 | Add a hashtag to a post | a528144 | GAP | W | NOT | as C10. The operator can put a `#` in his own `text`; the server may not compose one |
| C12 | Save a post as a draft | a767101 | GAP | W | REV | `_audit/2026-08-31-linkedin-lift.md:61-137` proves no draft surface is READABLE; creating one deliberately was never proposed |
| C13 | Schedule a post | a1347212 | EXCLUDED-RULED | W | REV (modifiable until it fires) | `server.py:4093-4096`: "A scheduled-posts surface would have fixed this and does not exist for this server: measured on a settle-confirmed composer render, the page draws seven links and none reaches a posted or scheduled list" |
| C14 | View all scheduled posts | a1347212 | EXCLUDED-RULED | R | REV | same measurement |
| C15 | Modify a scheduled post's schedule | a1347212 | EXCLUDED-RULED | W | REV | same |
| C16 | Edit a scheduled post | a1347212 | EXCLUDED-RULED | W | REV | same |
| C17 | Delete a scheduled post | a1347212 | EXCLUDED-RULED | W | REV (nothing was published) | same, plus `delete_or_withdraw_anything` |
| C18 | Edit a published post | a522811 | EXCLUDED-RULED | W | NOT | `lift.md:88-92` enumerates `REFUSE /post/edit/<id>/ forbidden substring '/post/'` and `REFUSE /article/edit/<id>/ forbidden substring '/edit/'`; `readonly.py:486-490` keeps `/edit/`, `/delete`, `/withdraw`, `action=` checked before the allowlist |
| C19 | Delete a published post | a523181 | EXCLUDED-RULED | W | **NOT** | `writes.py:1801-1814` `delete_or_withdraw_anything`. And whether the affordance even exists is UNMEASURED -- see s3.2 |
| C20 | Repost without a note | a525047 | EXCLUDED-RULED | W | **NOT** | `writes.py:1754-1768` `repost_or_share`: "a repost republishes SOMEBODY ELSE'S item to his network under his name, so the thing broadcast is not his and the audience is ... 'Repost' is a button with `aria-expanded='false'`, 3 on the feed and 8 on his profile, and its menu has never been opened" |
| C21 | Repost with your thoughts | a525047 | EXCLUDED-RULED | W | **NOT** | same entry |
| C22 | Delete a repost | a525047 | EXCLUDED-RULED | W | NOT | `delete_or_withdraw_anything` |
| C23 | Turn off or limit comments on your post | a523384 | GAP | W | REV | never named; a per-post overflow item, and that menu has never been opened |
| C24 | Hide a comment on your post | a6247516 | GAP | W | REV | same menu |
| C25 | Comment on a post | a524166 | COVERED-UNFIRED | W | **NOT** | `linkedin_comment_on_item`. Never invoked; 0 tokens minted. Ships expecting to refuse: `server.py:4121-4131` -- "This tool can type the comment into the box and then STOP WITHOUT POSTING IT, on purpose" |
| C26 | Reply to a comment | a524166 | GAP | W | NOT | `linkedin_comment_on_item(item, text)` targets an item urn. A comment is not an item; no comment identifier is read anywhere |
| C27 | Add an emoji, GIF or image to a comment | a524166 | GAP | W | NOT | picker + `set_input_files`, neither considered |
| C28 | Mention someone in a comment | a524166 | GAP | W | NOT | never named |
| C29 | Sort comments (Most relevant / Most recent) | a524166 | GAP | R | REV | never named; a pure view filter, the same class the messaging pills were admitted under |
| C30 | Edit your comment | a542920 | GAP | W | NOT | never named |
| C31 | Delete your comment | a524166 | EXCLUDED-RULED | W | **NOT** | `writes.py:1801-1814` names "a comment" among the five specs that lean on the entry |
| C32 | React to a post | a528190 | COVERED-UNFIRED | W | **NOT** | `linkedin_react_to_item`. Fired live 2026-08-31 with `item="placeholder-not-a-real-item"` (`finish.md:122-130`) which confirmed the OFF anchor and refused; never confirmed on a real target |
| C33 | Choose WHICH reaction (Celebrate, Support, Love, Insightful, Funny) | a528190 | EXCLUDED-RULED | W | NOT | `server.py:4206-4213`: "pressing this control applies whatever LinkedIn's default reaction is, and nobody has measured which one that is. `Open reactions menu` is a separate control beside the toggle and has never been opened" |
| C34 | React to a comment | a528190 | GAP | W | NOT | the permalink draws exactly one reaction control, the post's; comment-level reaction controls were never enumerated |
| C35 | Remove or change a reaction | a528190 | EXCLUDED-RULED | W | partial (the row goes, the notification does not) | `writes.py:1801-1814`: "react_to_item does not lean on this entry at all, because its reversible_by rests on a different gap -- the ON-state label has never been observed, so there is no selector for the inverse" |
| C36 | Save a post or article to Saved Items | a527126 | GAP | W | REV | `/my-items/saved-posts/` appears exactly once in the repo, as row 8 of the 17 refused draft-hunt addresses. Never considered as a capability |
| C37 | Unsave a saved post | a527126 | GAP | W | REV | same |
| C38 | View post analytics (impressions, viewer demographics) | a525196, a516971 | GAP | R | REV | `/analytics/creator/content/` appears once, in the same refused-address list. The impression figures the repo cites (113/319/1,287) were read off the profile by hand, not by any tool |
| C39 | View analytics for your comments | a7436043 | GAP | R | REV | never named |
| C40 | View your creator analytics | a704175 | GAP | R | REV | never named |
| C41 | View your own activity feed | a546122 | COVERED-UNFIRED | R | REV | `linkedin_my_activity_items`. Every recorded live run refused -- `perform.md:276-286` shows `refused: no_page_owner_heading`, `owner_headings 0`; a later run gave `no_self_assertion, five consecutive calls`. It has never returned an item |
| C42 | Address a specific post by identifier (precondition for C25, C32, C34) | -- | EXCLUDED-RULED | R | REV | `finish.md:565-592`: "**AND THE TARGET CANNOT BE NAMED, which the ruling did not reach.** To open `/feed/update/<urn>/` you need a urn, and **no tool in this server returns one.** The census substitutes `<urn>` out before counting, deliberately" |
| C43 | Read a post's text | a546122 | GAP | R | REV | `/feed/update/<urn>/` is on the allowlist and `linkedin_surface_census` reduces every name to a SHAPE, so the permalink is readable and its content is not. No tool returns post text |
| C44 | Write and publish an article | a522427 | EXCLUDED-RULED | W | **NOT** | `writes.py:926-929`: "THE ARTICLE ROUTE IS DELIBERATELY NOT USED. `/article/new/` is on the allowlist too and is WORSE measured: its publish control comes back `<redacted>`, blanked as a singleton, so that route has no measured anchor where this one does" |
| C45 | Add or edit rich media in an article | a521719 | GAP | W | REV | depends on C44; `set_input_files` unsanctioned |
| C46 | Embed content within an article | a522472 | GAP | W | REV | never named |
| C47 | Manage, share or duplicate article drafts | a523042 | EXCLUDED-RULED | R+W | REV | `lift.md:88-92`: `/pulse/drafts/`, `/drafts/`, `/content/drafts/` all `REFUSE  not on the allowlist`, enumerated deliberately |
| C48 | View all your articles | a520701 | GAP | R | REV | never named |
| C49 | Manage comments on your articles | a522438 | GAP | W | mixed | never named |
| C50 | Create a newsletter | a522525, a591266 | GAP | W | **NOT** (it mails subscribers) | zero hits for "newsletter" anywhere in the repo |
| C51 | Manage a newsletter | a517925 | GAP | W | REV | same |
| C52 | Manage your LinkedIn feed preferences (follow / unfollow topics and sources) | a528074 | GAP | W | REV | **ROW CORRECTED 2026-09-03.** It previously read "Follow a hashtag / topic" sourced to `a528144`, which **returns HTTP 404**, and two independent help-index queries (`q=hashtag`, `q=follow topics interests feed`) return no hashtag-following article at all. What the index does document is feed preferences and the profile Interests section (`a569139`). The capability as I first stated it is not sourceable from LinkedIn's own index; this row is what survives |
| C53 | *(retired -- see C52)* | -- | -- | -- | -- | the unfollow half of an unsourceable row. Retired rather than kept, and recorded rather than deleted |
| C54 | Create a collaborative post | a14240120 | GAP | W | **NOT** | zero hits |
| C55 | Manage collaborators on a collaborative post | a14180127 | GAP | W | REV | zero hits |
| C56 | Remove yourself from a collaborative post | a14250134 | GAP | W | NOT | zero hits |
| C57 | Create a LinkedIn Event | a554183 | GAP | W | REV (an event can be edited or cancelled) | zero hits for "event" as a capability |
| C58 | Attend or leave a LinkedIn Event | a548541 | GAP | W | REV | attending puts him on a public attendee list |
| C59 | Create or broadcast a LinkedIn Live | topic a151003 | GAP | W | **NOT** | zero hits; needs a third-party streaming tool, so it is outside a browser driver regardless |
| C60 | Access your LinkedIn Groups | a566460 | GAP | R | REV | zero hits for Groups as a capability; `/groups/` is on neither the allowlist nor the forbidden list |
| C61 | Join a group | a540824 | GAP | W | REV | same |
| C62 | Withdraw a group membership request | a542733 | GAP | W | REV | same; `/withdraw` is a forbidden substring, which would catch the url incidentally |
| C63 | Leave a group | a566460 | GAP | W | REV (re-joinable, possibly by approval) | same |
| C64 | Post content in a group feed | a539929 | GAP | W | **NOT** | a second publishing surface with its own composer, entirely uncensused |
| C65 | Add a comment to a group conversation | a545818 | GAP | W | NOT | same |
| C66 | Mention group members in a conversation | a563278 | GAP | W | NOT | same |
| C67 | Edit or delete a group post or comment | a542920 | GAP | W | NOT | edit never named; the delete half would meet `delete_or_withdraw_anything` |
| C68 | Submit a group post for admin approval | a551360 | GAP | W | REV | never named |
| C69 | Invite connections to join a group | a547071 | GAP | W | NOT | reaches third parties; `/invite` is a forbidden substring |
| C70 | Search for content within Groups | a548435 | GAP | R | REV | never named |
| C71 | Boost a post (paid promotion) | a7421378, a10403062 | GAP | W | NOT (money is spent) | never named; the only capability in this slice that costs currency |
| C72 | Share a post off LinkedIn | a7443434 | GAP | R | REV | never named |
| C73 | Allow or disallow your posts being embedded | a7462020 | GAP | W | REV | never named |
| C74 | Read your feed | a1480504 | GAP | R | REV | `/feed/` is on the allowlist and has been censused dozens of times -- for CONTROL COUNTS. No tool returns a feed item. "286 controls, 1 form, 0 contenteditable" is what the feed looks like from here |
| C75 | Read notifications about engagement on your content | -- | **COVERED-PROVEN** | R | **NOT** (loading clears the badge) | `linkedin_notifications`; one measured call 2026-08-21 took the badge from 1 to 0 and it did not come back. Overlaps the network slice -- flagged rather than double-counted there |
| C76 | Contribute to a collaborative article | a1413111, a1443723 | GAP | W | **NOT** | recovered 2026-09-03 by help-index search. A whole LinkedIn product -- AI-seeded articles members add sections to under their own name, with a Top Voice badge attached to doing it well. Absent from the Share Content and Post topic trees entirely |
| C77 | Delete an article | a522451 | EXCLUDED-RULED | W | **NOT** | `writes.py:1801-1814` `delete_or_withdraw_anything`. LinkedIn's own article is titled *"Unable to retrieve deleted articles"*, which is the platform confirming the irreversibility the repo's entry asserts |
| C78 | Set the visibility of your articles | a517863 | GAP | W | REV | recovered by help-index search; never named |
| C79 | Follow or unfollow member articles | a519786 | GAP | W | REV | recovered by help-index search. Distinct from following a person; never named |
| C80 | Subscribe or unsubscribe to a newsletter | a1644939 | GAP | W | REV | recovered by help-index search. A READER-side capability -- the two newsletter rows I had were both author-side |
| C81 | Create a Newsletter Page | a518936 | GAP | W | REV | recovered by help-index search |
| C82 | Share a Newsletter Page | a521766 | GAP | W | REV | recovered by help-index search |
| C83 | View newsletter analytics | a1658525 | GAP | R | REV | recovered by help-index search |
| C84 | Manage multiple newsletters | a6588862 | GAP | W | REV | recovered by help-index search |
| C85 | Vote in a poll / view poll results | a527273, a527270 | GAP | W | **NOT** | recovered by help-index search. My original poll row was author-side only; voting is the reader-side act and it cannot be changed once cast |
| C86 | Tag people in your photos | a522896 | GAP | W | NOT once posted | recovered by help-index search. Distinct from an `@` mention in text -- a coordinate-anchored tag on an image |
| C87 | Remove a mention or tag of yourself | a524346 | GAP | W | REV | recovered by help-index search. The one capability in this family that acts on somebody ELSE's content, on his own behalf |
| C88 | Choose whether members can mention, tag or collaborate with you | a522861 | GAP | W | REV | recovered by help-index search; a setting, never named |
| C89 | Set the visibility of mentions and tags | a524212 | GAP | W | REV | recovered by help-index search |
| C90 | Verified comments filter on your post | a10721097 | GAP | W | REV | recovered by help-index search; a per-post comment control |
| C91 | React in a group conversation | a549002 | GAP | W | REV | recovered by help-index search. Reactions have a third surface -- posts, messages (M48) and group conversations -- and the repo names only the first |
| C92 | Comment on an Event and reply to Event comments | a738312 | GAP | W | NOT | recovered by help-index search. See s10 -- overlaps the sibling's Events slice and is flagged rather than claimed |

---

## 7. THE 88 GAPS, GROUPED -- WHAT EACH FAMILY WOULD TAKE

Shapes, not designs. "Reversibility dominates" is applied per family, and the asset at
risk throughout is the operator's professional identity.

Regrouped 2026-09-03 over the revised 109. Family counts sum to 109 exactly.

| family | rows | R/W | reversibility | shape of what it would take |
|---|---:|---|---|---|
| **Message composition beyond plain text** (requests send/accept/decline/review, Open Profile, reply-in-thread, edit, forward, GIF, emoji, group chat create/participants/mention, video meeting, smart replies, respond-to-Recruiter-InMail, react-to-message, AI conversation) | 18 | W | NOT | All blocked upstream by s3.1: there is no working way to address a human being on this surface. Nothing here is worth building until compose-by-identifier lands and a committed recipient has been OBSERVED for the first time. **M47 is the exception worth pulling forward** -- responding to an inbound Recruiter InMail needs no addressing at all, because the thread already exists and is already on the read allowlist |
| **Media upload** (message photo/video/file/voice; post photo/video/document/alt-text; article media; photo tagging) | 11 | W | NOT once published | One decision, not eleven: sanction `set_input_files` as a mutation class, with a target allowlist and a file-provenance rule. Still the single largest unlocked block, and still never discussed anywhere in the repo |
| **Conversation management** (archive, restore, mute, star, mark read/unread, bulk, leave, layout, windows, search, delivery indicators) | 11 | W | REV except leave | Every one is a per-conversation overflow-menu item and **that menu has never been opened** -- the exact shape of the post-deletion gap in s3.2. One capture of an open conversation overflow menu would settle eleven rows at once. Low risk: none emits anything to a third party except a read receipt already accepted by `open_messaging` |
| **Groups** (access, join, leave, withdraw, post, comment, mention, edit/delete, approval, invite, react) | 11 | R+W | mostly REV; posting NOT | A whole product surface with no address on either list -- `/groups/` returns zero grep hits across the entire package. Needs `/groups/` on the allowlist, a group-id read, a group composer census. Posting in a group is a second broadcast route with a different audience: treat as C1's equal in risk, not a lesser case |
| **Comment surface** (reply, media, mention, sort, edit, comment-on-comment reaction, turn off/limit, hide, verified filter) | 9 | W | NOT | Needs a comment-level identifier, a strictly harder version of C42 -- and C42 is already the ruled blocker at the post level |
| **Post composition beyond plain text** (audience, poll create, poll vote, celebration, mention, hashtag-in-text, draft) | 7 | W | NOT once published | **C2 (audience) is the one that should not wait**: `publish_post` can broadcast to an audience nobody chose or read back. One parameter and one control on a tool that already exists |
| **Reading content** (feed, post text, own articles, group search, share-off-platform, feed preferences) | 6 | R | REV | The census instrument is built to destroy exactly what these need -- it reduces every name and href to a SHAPE before counting. Reading content needs a SECOND instrument with a different privacy contract, not a flag on this one |
| **Newsletters** (create, manage, multiple, Newsletter Page, share, subscribe/unsubscribe) | 6 | W | NOT (it mails subscribers) | Never considered, and larger than the first pass showed. Higher blast radius than a post; should inherit C1's gate wholesale before anything is built. **C80 subscribe/unsubscribe is the safe half** -- reader-side, private, reversible |
| **Articles** (collaborative articles, visibility, follow member articles, embed, manage comments) | 5 | W | mixed | `/article/new/` is already on the read allowlist and was deliberately not used (C44). Collaborative articles (C76) are a product the repo has never named at all |
| **Events and Live** (create, attend/leave, broadcast, Event comments) | 4 | W | mixed | Reassigned -- see s10. Undercounted here; the sibling's re-walk sizes it properly |
| **Analytics** (post, comment, creator, newsletter) | 4 | R | REV | Four addresses, none on the allowlist. Cheap, read-only, zero third-party cost -- and it would give `publish_post` the outcome check it currently declares unverifiable. **Still the best value-per-risk in the whole slice** |
| **Mentions and tags** (remove a mention of yourself, mention/tag permissions, mention visibility) | 3 | W | REV | Recovered by the re-check. C87 is the only capability in this slice that acts on somebody ELSE's content on his own behalf, and it is the one a job-seeker most plausibly needs in a hurry |
| **Collaborative posts** (create, manage collaborators, remove yourself) | 3 | W | mixed | Never considered |
| **Saved posts** (save, unsave) | 2 | W | REV | `/my-items/saved-posts/` is one allowlist entry away. Fully reversible, private, no third party. Directly analogous to `save_job`, which is built and PROVEN |
| **Messaging settings and controls** (group-chat notifications, read receipts, report spam, smart features, group-member permissions, InMail opt-out, nudges) | 7 | W | REV | `/psettings/` and `/settings/` are forbidden substrings, so the settings family has a boundary but no reasoning. `update_setting` reaches exactly one setting today |
| **Tail** (boost a post, post-embed setting) | 2 | W | mixed | Boost is the only capability in the slice that costs money |

**Reversibility across the 109 GAPs, counted off the tables: 47 NOT reversible, 60
reversible, 2 mixed (C49, C67 -- each bundles an edit with a delete).** By read/write:
94 are writes, 14 are reads, 1 is both. The irreversible 47 cluster almost entirely in
composition -- messages, posts, comments, group posts, newsletters, collaborative posts
and articles. The reversible 60 cluster in management, settings and reading -- archive,
mute, star, save, subscribe, analytics, permissions, drafts.

**The asymmetry is the recommendation, and the re-check sharpened it.** The reversible
60 -- up from 45 -- include several cheaper, safer and more useful than anything
currently blocked: post and newsletter analytics, saved posts, conversation
archive/mute/star, mention-and-tag permissions, InMail opt-out. Every one is private,
undoable, and costs no third party a notification. **The repo has spent its entire design
budget on the irreversible 47, and the reversible 60 grew faster than they did.**

---

## 8. THREE THINGS THIS CENSUS FOUND THAT ARE NOT ROWS

1. **`publish_post` can broadcast at an audience nobody chose.** C2. The tool's signature
   is `(text, confirm_token)`. The docstring is scrupulous about impressions, followers
   and the unmeasured delete -- and silent about visibility. A gate that names its cost in
   impressions while not naming its audience is naming the wrong number.

2. **The overflow menu is one measurement standing between the repo and ~15 rows.** The
   post overflow menu (`Open control menu for post by <him>`, 8 instances, never opened),
   the per-conversation overflow menu (never opened), the Repost menu
   (`aria-expanded='false'`, never opened) and the reactions picker
   (`Open reactions menu`, never opened) are four instances of the same unopened control.
   The repo has an explicit doctrine for this -- "an unopened overflow menu is not
   evidence about what is inside it" -- and has applied it consistently as a reason to
   refuse, never as a task to schedule. Opening those four menus is a read that changes
   nothing.

3. **The topic tree is not a reliable index, and the empty-page hazard was the smaller
   half of that.** Events (`topic/a150003`) and LinkedIn Live (`topic/a151003`) both
   render `0 articles` for products that plainly exist -- that was pass 1's finding and it
   was right. **Pass 2 found the larger failure: the Share Content and Post topic pages
   list 60 articles each and still omit collaborative articles, newsletter analytics,
   Newsletter Pages, newsletter subscription, poll voting, photo tagging, mention
   permissions, mention removal, the verified-comments filter, article visibility,
   member-article following, and the feed-preferences surface.** A 60-article listing
   reads as exhaustive and is not. `?q=` search against LinkedIn's own index is the
   instrument; the topic tree is a browsing aid. Any future census slice should run the
   search first and treat the tree as a cross-check.

4. **A dead help URL survived a full pass as a sourced capability.** `a528144` returns
   404 and it carried two rows. Nothing in the first pass could have caught it, because
   the URL arrived from an external search engine that was serving a stale index. **Every
   capability sourced only to an external search result is unverified until it resolves
   against `/help/linkedin/`.** This is the one defect in pass 1 that produced a wrong
   claim rather than a missing one.

---

## 9. PROVENANCE

**LinkedIn's own product surface** was enumerated from the Help Center pages listed in
s2 on 2026-09-03 via WebFetch and WebSearch. Every capability row cites the article it
came from. No capability in this document was recalled from memory.

**This server's behaviour** was read from `linkedin_server/server.py` (35 tools),
`writes.py` (`PERFORMABLE`, 12 entries; `PERMANENTLY_FORBIDDEN`), `readonly.py` (the
22-pattern allowlist and the 23-entry forbidden-substring list), `dom.py`, `config.py`,
`README.md`, `_TEAM_LEAD_SUCCESSOR_BRIEF.md`, and every `_audit/*.md`. Quotes are
verbatim with path and line; where a line reference came from a delegated extraction it
was re-read against the file before being quoted here.

**Live-firing evidence** was taken from the audit record only. Nothing was run against
LinkedIn for this document.

**Four tools in `PERFORMABLE` belong to this slice**: `send_message`, `publish_post`,
`comment_on_item`, `react_to_item`. Of the four, one has fired against a real target and
refused, one has fired against a placeholder and refused, and two have never been
invoked at all. **Zero `confirm_token`s have ever been minted or consumed for any of
them** -- `perform.md:1794-1799`, restated at the close of every Part through Part Six.

**Re-check pass, 2026-09-03.** Fourteen queries against
`https://www.linkedin.com/help/linkedin/search?q=` -- `recruiter inmail`, `newsletter`,
`poll`, `scheduled post`, `article`, `who can message me settings`, `linkedin live video`,
`comment`, `reaction`, `voice message attachment`, `hashtag`, `archive conversation`,
`saved items`, `group members invite`, `privacy settings visibility`, `events attend`,
`follow topics interests feed`, `mention tag people in post`, `repost share post to
group` -- plus the `Basics` topic tree (`topic/a51`, 26 articles) and one direct fetch of
`answer/a528144` (HTTP 404). No browser, no LinkedIn session, no page load against the
operator's account.

---

## 10. RECONCILIATION -- ROWS THAT MAY BELONG TO A SIBLING

Flagged rather than deleted, per the lead's instruction that double-counting is
preferable to dropping between two agents. **These rows are still counted in this file's
142.** If the sibling's slice claims them, subtract exactly the rows named here.

| rows | capability | my read of where it belongs |
|---|---|---|
| C60-C63, C69 | Groups: access, join, withdraw request, leave, invite connections to a group | **THE SIBLING'S.** These are membership and invitation acts. C69 in particular is a connection-style invitation, and `a541787` "Invite group members to connect" is plainly a network capability |
| C64-C68, C91 | Groups: post in a group feed, comment in a group conversation, mention group members, edit/delete a group post, submit for approval, react in a group conversation | **MINE.** These are composition and engagement inside a group -- a second publishing surface with a different audience. They belong with C1 and C25, not with membership |
| C57, C58, C92 | Events: create, attend/leave, comment on an Event | **SPLIT.** Create and attend are the sibling's; C92 (Event comments, `a738312`) is a comment capability and belongs here |
| C59 | LinkedIn Live: create or broadcast | **THE SIBLING'S**, and **I undercounted it 5:1.** `q=linkedin live video` returned `a554240` (overview), `a548518` (broadcasting FAQ), `a569473` (broadcaster features), `a570593` (video player controls), `a523091` (go live via Zoom), `a8338312` (boost a Live event). My single row should be at least five |
| C75 | Read engagement notifications | Overlaps the network slice; already flagged in pass 1 |

**On the sibling's three no-cost group capabilities** -- view a group's member list, invite
a fellow group member from inside the group, filter connections when inviting. **All three
are network-slice, not mine**, and the help index agrees: they resolve to `a541787`
("Invite group members to connect") and `a547071`, both of which are connection
invitations that merely happen to be reached through a group. My interest in that address
family is different and narrower: **it is the only route to a group COMPOSER**, which is
where C64-C68 live. The sibling's finding that the family carries no badge cost, no
third-party profile load and no forbidden substring **applies to my rows too, and is the
single most useful thing anyone has established about Groups.** If that address family is
admitted for the network slice, the group composer becomes reachable at the same moment
and should be censused in the same pass rather than in a later one.

**Also worth handing over:** `/events/` and `/groups/` return **zero grep hits across the
entire package** -- no tool, no ruling, not one sentence. That is not a finding about
Groups and Events specifically. It is the shape of every one of the 109: **the repo can
only refuse what somebody named, and nobody named these.**
