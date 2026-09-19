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

**Denominator: 138 member-performable capabilities** -- 51 messaging, 91 content, **MINUS the 4 subtracted 2026-09-19 under this slice's own section-10 condition** (`C60`, `C61`, `C63`, `C69` -- the sibling claimed them). **The figure was 142 until then and section 10 records exactly which four moved and why.** Note this is the CAPABILITY denominator: the file still holds 142 stated ROWS, and `scripts/count_census_states.py` still counts them, because rows are not capabilities -- that script's own docstring makes the same distinction.
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
| M1 | Send a message to a 1st-degree connection | a541865 | **COVERED-CANNOT-DELIVER** | W | **NOT** | `linkedin_send_message`; fired live 2026-09-03, refused at `_recipient_gate`. See s3.1 |
| M2 | Send an InMail to a non-connection | a546814 | **COVERED-CANNOT-DELIVER** | W | **NOT** | same tool, same gate; additionally spends a metered credit whose size is unreadable |
| M3 | Choose the dispatch mode (message vs InMail) | a546814 | EXCLUDED-RULED | W | NOT | `_TEAM_LEAD_SUCCESSOR_BRIEF.md:63-80`: "**DO NOT touch the dispatch radios.** Use the checked default" |
| M4 | View available InMail credit balance | a543685 | EXCLUDED-RULED | R | REV | `readonly.py:411-433` admits `/premium/my-premium/` for exactly this and it carries no balance; `perform.md:3462-3487`: InMail on the composer is "a conversation FILTER PILL -- five independent readings" |
| M5 | Send an Open Profile message | a544787 | EXCLUDED-RULED | W | **NOT** | R9 (`network.md:745`, four independent rulings) -- twin `N158` *Send an Open Profile message without spending an InMail* is EXCLUDED-RULED under it, and sending an Open Profile message is a sending action. **This row's own note also stated R4's condition** (*needs a third party's profile loaded*), and R4 makes that permanently forbidden. Adjudicated in `_audit/2026-09-19-profile-modals-measured.md` amendment C |
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
| M19 | Send a voice message | a148003 | EXCLUDED-RULED | W | NOT | zero hits for "voice" in the repo; needs microphone capture, outside anything this design contemplates **RETIRED 2026-09-05, `VOICE-CAPTURE` (3.11).** DERIVED: the control records live audio from a microphone, and this server drives a browser with no audio input to give one -- nothing in this package has ever supplied media to a page. UNTESTED and stated as such: the composer has not been opened, so whether a voice note is also offered as an ATTACHMENT is unknown. REOPENER: `linkedin_surface_census` on `messaging_compose` -- and it then reopens as `FILE-UPLOAD-UNSANCTIONED`, not as this. See `_audit/2026-09-05-decide-retire-rulings.md` |
| M20 | Start or schedule a video meeting from a message | video-meetings help | GAP | W | REV (a link can be revoked) | never named |
| M21 | Create a group chat | a566306 | GAP | W | **NOT** | multi-recipient addressing; strictly harder than M1, which is dead |
| M22 | Add or remove group-chat participants | a554447 | GAP | W | NOT | never named |
| M23 | Mention people in a group chat | a565352 | EXCLUDED-RULED | W | NOT | never named  **RETIRED 2026-09-19 on the MENTION/TAG ACTION-CLASS RULING, which was reached 2026-09-05 and only half applied.** `_audit/2026-09-05-article-publish.md:82`: *"The ruling reaches the ACTION CLASS -- compose a mention or a tag into published content -- and whoever holds the map should apply it ROW BY ROW rather than take my count."* That document enumerates four mention rows; `C10` and `C28` were applied in `58ba421` and these were not. A mention is an entity the composer inserts, not text: typing `@Name` produces no mention, so delivering this needs the server to compose a third party's identity into outgoing content. `mentions` is the forbidden name. Enforced by `FORBIDDEN_PARAMETER_NAMES` (`tests/test_no_write_tool_names_a_third_party.py:54-70`), asserted over every `linkedin_*` signature off the AST by `test_no_tool_takes_a_third_partys_identity_as_a_parameter`; bound to this row by `tests/test_a_retired_row_rests_on_a_live_assertion.py`, so deleting the name re-opens the row instead of leaving the retirement standing. **NOT a re-derivation of the ruling -- the source names this row.** |
| M24 | Manage group-chat notification settings | a1420321 | EXCLUDED-RULED | W | REV | R11 (`network.md:814`) -- the row's own note reads *a settings sub-surface, unenumerated*, and notification settings live at `/mypreferences/d/categories/notifications`, enumerated live off the settings index 2026-09-19 and measured `is_read_url=False`. Twin rows `N116`/`N117` (endorsement settings / notifications) are EXCLUDED-RULED under R11 |
| M25 | Leave a conversation | a568326 | GAP | W | **NOT** ("you will not be able to reply or re-join") | never named; adjacent to but not covered by `delete_or_withdraw_anything` |
| M26 | Delete a conversation or group chat | a543838 | EXCLUDED-RULED | W | **NOT** | `writes.py:1801-1814`, same entry as M12 |
| M27 | Archive a conversation | a550440 | GAP | W | REV (restorable) | zero hits for "archive" as a messaging action |
| M28 | View and restore archived conversations | a550440 | GAP | R+W | REV | same |
| M29 | Mute or unmute a conversation | a565292 | GAP | W | REV | zero hits for "mute" |
| M30 | Star a conversation | a1430963 | GAP | W | REV | "Starred" exists in the repo only as one of seven activatable FILTER pills (`dom.py:2269-2276`); starring itself was never considered |
| M31 | Mark a conversation read or unread | a549532 | GAP | W | REV (both directions exist in the product) | never named. The `mark_notifications_read` prohibition is a different surface, though its reasoning transfers |
| M32 | Bulk delete / archive / mark read | a549532 | EXCLUDED-RULED | W | mixed | never named; the delete third would be caught by `delete_or_withdraw_anything`. **RE-FILED 2026-09-19: the cell had found ONE THIRD of the ground and stopped.** The delete third is indeed refused by `PERMANENTLY_FORBIDDEN['delete_or_withdraw_anything']` -- but **BULK is refused for ALL THREE THIRDS**, independently, by `PERMANENTLY_FORBIDDEN['any_loop_sweep_or_scheduled_write']` (`writes.py:2036`): *"one write per invocation, always. The grant TTL makes an unattended write structurally impossible and that is the intended consequence."* **A bulk operation is not expensive here, it is structurally unexpressible** -- archive-in-bulk and mark-read-in-bulk are refused by the same line that refuses delete-in-bulk, and the reversibility column reading `mixed` is what made it look like only part of the row was settled. TWO independent grounds, neither of them an allowlist question. REOPENER: a ruling that more than one write may issue per invocation |
| M33 | Apply an inbox filter pill (Focused, Other, Unread, Starred, Connections, Jobs, InMail) | a711117, a542831 | COVERED-UNFIRED | R | REV | `linkedin_open_messaging(message_filter=...)`; closed set of 7 at `dom.py:2269-2276`, the second entry in `readonly.SANCTIONED_MUTATIONS`. Never run live |
| M34 | Search messages by keyword | a539848, a542831 | GAP | R | REV | `linkedin_open_messaging` takes no query parameter |
| M35 | Choose Messaging inbox layout | a7449032 | GAP | W | REV | never named |
| M36 | Manage how new conversations open (conversation windows) | a563389, a569449 | GAP | W | REV | never named |
| M37 | Turn read receipts and typing indicators on or off | a567370 | EXCLUDED-RULED | W | REV | `linkedin_update_setting` exists but reaches exactly one setting (`/mypreferences/d/dark-mode`); `/psettings/` and `/settings/` are forbidden substrings, so a route exists as a boundary while the capability itself was never reasoned about **RE-FILED 2026-09-05 as EXCLUDED-RULED under `MESSAGING-SETTINGS` (3.10). NOT a new decision -- the operator already made it and two census slices applied it differently.** `linkedin_server/server.py`, in `linkedin_update_setting` (7401-7402 at 2026-09-19 -- **cite the SYMBOL; this line number already drifted once, and 6476-6484 is now `_write_tool`**): the read allowlist admits exactly one page below the settings index, admitted BY NAME on the operator's ruling; a setting is admitted by name or not at all. REOPENER: the operator naming one. That is the mechanism, not a consolation -- it is how dark mode got in. See `_audit/2026-09-05-decide-retire-rulings.md` |
| M38 | Report a message as spam | a564261 | GAP | W | NOT | never named |
| M39 | Set or edit an away message (Premium) | a550614 | EXCLUDED-RULED | W | REV | `writes.py:1829-1832` `auto_accept_or_auto_reply`: "a reply in his name that he did not read is a message from a stranger wearing his face" |
| M40 | Use smart replies / reply suggestions | a569446, a552111 | EXCLUDED-RULED | W | NOT (the reply is sent) | never named; the away-message ruling does not cover a suggestion the operator picks **RETIRED 2026-09-05, `AI-ASSIST-MESSAGING` (3.6) -- by the consent architecture, not by a missing surface.** The existing prohibition genuinely does not cover these, which is why it needed a ruling. The reason is one layer down: `mint` binds a confirm token to a canonical TARGET, and for `send_message` that target CARRIES THE MESSAGE TEXT -- so text he has not read cannot be consented to. REOPENER: the assist control filling an EDITABLE composer, which makes a read-back-then-mint shape possible; settle it with `linkedin_surface_census` on `messaging_compose`. See `_audit/2026-09-05-decide-retire-rulings.md` |
| M41 | Manage smart features in Messaging | a1431517 | EXCLUDED-RULED | W | REV | never named **RE-FILED 2026-09-05 as EXCLUDED-RULED under `MESSAGING-SETTINGS` (3.10). NOT a new decision -- the operator already made it and two census slices applied it differently.** `linkedin_server/server.py`, in `linkedin_update_setting` (7401-7402 at 2026-09-19 -- **cite the SYMBOL; this line number already drifted once, and 6476-6484 is now `_write_tool`**): the read allowlist admits exactly one page below the settings index, admitted BY NAME on the operator's ruling; a setting is admitted by name or not at all. REOPENER: the operator naming one. That is the mechanism, not a consolation -- it is how dark mode got in. See `_audit/2026-09-05-decide-retire-rulings.md` |
| M42 | Settings to allow or prevent messages from group members | a541708 | EXCLUDED-RULED | W | REV | never named **RE-FILED 2026-09-05 as EXCLUDED-RULED under `MESSAGING-SETTINGS` (3.10). NOT a new decision -- the operator already made it and two census slices applied it differently.** `linkedin_server/server.py`, in `linkedin_update_setting` (7401-7402 at 2026-09-19 -- **cite the SYMBOL; this line number already drifted once, and 6476-6484 is now `_write_tool`**): the read allowlist admits exactly one page below the settings index, admitted BY NAME on the operator's ruling; a setting is admitted by name or not at all. REOPENER: the operator naming one. That is the mechanism, not a consolation -- it is how dark mode got in. See `_audit/2026-09-05-decide-retire-rulings.md` |
| M43 | Open the inbox and list conversations | a564261 | COVERED-UNFIRED | R | REV | `linkedin_open_messaging`. Deliberately never called: `_audit/2026-08-30-linkedin-writes.md:335-336` -- "**This wave did NOT call `linkedin_open_messaging`.** The cost lands on somebody who is not him, so it is his to spend." |
| M44 | See the unread-messages badge count | a564261 | **COVERED-PROVEN** | R | REV | `linkedin_new_messages`; measured `Messaging, 0 new notifications` on both feed and profile, 2026-08-30. Reads the badge off a page already open; loads no messaging surface |
| M45 | Open a blank compose window | a541865 | COVERED-UNFIRED | R | REV | `linkedin_compose_fields` loads `/messaging/compose/` by exemption. Fired live 2026-09-02 and returned `refused: name_shaped_label_present`; the design was confirmed by a different instrument and the repaired build has not been re-run |
| M46 | Opt out of receiving InMail messages | a554229 | EXCLUDED-RULED | W | REV | recovered 2026-09-03 by help-index search. A member-side InMail control the whole InMail discussion in this repo never mentions -- every sentence there is about SPENDING a credit, none about the receiving end **RE-FILED 2026-09-05 as EXCLUDED-RULED under `MESSAGING-SETTINGS` (3.10). NOT a new decision -- the operator already made it and two census slices applied it differently.** `linkedin_server/server.py`, in `linkedin_update_setting` (7401-7402 at 2026-09-19 -- **cite the SYMBOL; this line number already drifted once, and 6476-6484 is now `_write_tool`**): the read allowlist admits exactly one page below the settings index, admitted BY NAME on the operator's ruling; a setting is admitted by name or not at all. REOPENER: the operator naming one. That is the mechanism, not a consolation -- it is how dark mode got in. See `_audit/2026-09-05-decide-retire-rulings.md` |
| M47 | Respond to a Recruiter InMail (Interested / Not interested) | a552643 | GAP | W | **NOT** | recovered by help-index search. Distinct from a plain reply: it is a structured response with its own affordances, and it is the single most job-hunt-relevant messaging action in this slice |
| M48 | React to a message with an emoji | a552661 | GAP | W | REV | recovered by help-index search. Reactions exist on MESSAGES as well as posts; `react_to_item` addresses feed items only and nothing in the repo mentions the messaging case |
| M49 | Read message delivery / read indicators | a569649 | GAP | R | REV | recovered by help-index search. `linkedin_open_messaging` returns per-row unread flags for HIS state; the sender-side indicators are a different signal and were never enumerated |
| M50 | Manage LinkedIn message nudges | a568627 | EXCLUDED-RULED | W | REV | recovered by help-index search; never named **RE-FILED 2026-09-05 as EXCLUDED-RULED under `MESSAGING-SETTINGS` (3.10). NOT a new decision -- the operator already made it and two census slices applied it differently.** `linkedin_server/server.py`, in `linkedin_update_setting` (7401-7402 at 2026-09-19 -- **cite the SYMBOL; this line number already drifted once, and 6476-6484 is now `_write_tool`**): the read allowlist admits exactly one page below the settings index, admitted BY NAME on the operator's ruling; a setting is admitted by name or not at all. REOPENER: the operator naming one. That is the mechanism, not a consolation -- it is how dark mode got in. See `_audit/2026-09-05-decide-retire-rulings.md` |
| M51 | Use LinkedIn AI-powered conversation in messaging | a10346037 | EXCLUDED-RULED | W | NOT (it sends) | recovered by help-index search. Distinct from M40 smart replies; adjacent to the `auto_accept_or_auto_reply` prohibition without being covered by it **RETIRED 2026-09-05, `AI-ASSIST-MESSAGING` (3.6) -- by the consent architecture, not by a missing surface.** The existing prohibition genuinely does not cover these, which is why it needed a ruling. The reason is one layer down: `mint` binds a confirm token to a canonical TARGET, and for `send_message` that target CARRIES THE MESSAGE TEXT -- so text he has not read cannot be consented to. REOPENER: the assist control filling an EDITABLE composer, which makes a read-back-then-mint shape possible; settle it with `linkedin_surface_census` on `messaging_compose`. See `_audit/2026-09-05-decide-retire-rulings.md` |

---

## 6. CONTENT -- 75 capabilities

| # | capability | Help Center | state | R/W | REV | evidence, or what a GAP would take |
|---|---|---|---|---|---|---|
| C1 | Publish a text post | a518996 | COVERED-UNFIRED | W | **NOT** | `linkedin_publish_post`. Zero `confirm_token`s ever minted or used (`perform.md:1794-1799`); its submit selector was measured broken on 2026-09-01 and repaired without ever firing (`perform.md:2620-2662`) |
| C2 | Choose the post's audience / visibility | a523141 | GAP | W | NOT | `linkedin_publish_post(text, confirm_token)` has no audience parameter. Every post it could publish goes out at whatever LinkedIn's default is, unread and unchosen  **STILL GAP 2026-09-19; the ruling and the guard both exist and the MEASUREMENT does not.** Amendment A9 decided the fork (admit the audience option set as a closed vocabulary, on the `dom.MESSAGING_FILTERS` precedent) and `tests/test_the_audience_reader_arrives_with_its_contract.py` already asserts that the reader cannot arrive alone and re-arm an irreversible broadcast on the strength of its name. What is missing is one read of the composer to establish the option set -- and that read carries C12's autosave hazard, which is why the two rows close together or not at all. See `_audit/2026-09-19-content-tail.md` section 4.4 |
| C3 | Post a photo | a527229 | GAP | W | NOT | `set_input_files` unsanctioned (s4) |
| C4 | Post a video | a7174587, a554001 | GAP | W | NOT | same |
| C5 | Post a document (PDF / carousel) | a518909 | GAP | W | NOT | same |
| C6 | Add a title to an uploaded document | a517910 | GAP | W | REV | depends on C5 |
| C7 | Add alt text to a post image | a519856 | GAP | W | REV | depends on C3; an accessibility obligation nobody has counted |
| C8 | Create a poll | a522948 | GAP | W | NOT | zero hits for "poll"; a distinct composer mode never censused |
| C9 | Post a celebration ("Celebrate an occasion") | a518996 | GAP | W | NOT | zero hits for "celebration" |
| C10 | Mention a person or company in a post | a525082 | EXCLUDED-RULED | W | NOT | zero hits. Note the opposing constraint: `tests/test_typed_bytes.py` asserts on the AST node "because the substring version passed a mutation that appended a hashtag" -- the suite actively guards against the server adding anything to his text  **RETIRED 2026-09-19, `MENTION-COMPOSITION-RULING`.** The opposing constraint this row already recorded IS the ruling: the operator's typing ruling requires text the caller supplied rather than this server composing it, and a mention cannot be caller-supplied because typing the characters produces no mention -- the platform requires a typeahead commit, so the bytes and their position are the server's. Two rulings derived independently agree and the operator's is the wider one. See `_audit/2026-09-05-article-publish.md` section 1 and `_audit/2026-09-19-content-tail.md` |
| C11 | Add a hashtag to a post | a528144 | EXCLUDED-RULED | W | NOT | as C10. The operator can put a `#` in his own `text`; the server may not compose one. **RE-FILED 2026-09-19 out of `HASHTAG-EXISTENCE`, and NOT on a measurement -- this row was never about whether hashtags exist.** It is refused by a shipped rule: `tests/test_typed_bytes.py:115-145` asserts on the AST node that EVERYTHING APPENDED TO THE FILL QUEUE MUST BE AN EXTRACTOR'S RESULT, and its own docstring records that the substring version was killed by a mutation which appended a hashtag. The suite actively guards against the server adding anything to his text. REOPENER: the operator ruling that composed text may be appended to his own |
| C12 | Save a post as a draft | a767101 | GAP | W | REV | `_audit/2026-08-31-linkedin-lift.md:61-137` proves no draft surface is READABLE; creating one deliberately was never proposed  **COUPLED TO C2, MEASURED 2026-09-19, and the coupling is the finding.** `_audit/2026-09-05-article-publish.md` section 6 declined to open the post composer because doing so *may autosave a draft this server has no reachable surface to detect*, and this row's own citation proves the second half -- no draft surface is readable. Together: if the autosave happens, this server performs THIS ROW'S ACT as a side effect of a read it prices at zero, and is structurally unable to observe that it did. `/article/new/` is admitted today, so the exposure is live rather than hypothetical. NOT MEASURED: whether the autosave happens. The read that would settle it is the read that would cause it, and the `read_invitation_badge` before/after discipline cannot be applied here because the counter sits on a page the boundary refuses. See `_audit/2026-09-19-content-tail.md` section 4.4 |
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
| C28 | Mention someone in a comment | a524166 | EXCLUDED-RULED | W | NOT | never named **RETIRED 2026-09-19, `MENTION-COMPOSITION-RULING`, on the OPERATOR'S TYPING RULING, which is older and wider than the lead's and is already asserted in code.** `tests/test_typed_bytes.py` requires the typed text to come from `_text_component_of(spec, grant.target)` and from nowhere else; typing `@Name` produces no mention, because the platform requires a typeahead commit, so a mention is bytes the SERVER inserts at a position the SERVER chooses. `tests/test_no_write_tool_names_a_third_party.py` forbids `mention(s)` as a tool parameter and is shown failing under a planted one. REOPENER: LinkedIn exposing a mention target as an opaque identifier the caller already holds, with no name read to obtain it. See `_audit/2026-09-05-article-publish.md` section 1 and `_audit/2026-09-19-content-tail.md` |
| C29 | Sort comments (Most relevant / Most recent) | a524166 | GAP | R | REV | never named; a pure view filter, the same class the messaging pills were admitted under |
| C30 | Edit your comment | a542920 | GAP | W | NOT | never named |
| C31 | Delete your comment | a524166 | EXCLUDED-RULED | W | **NOT** | `writes.py:1801-1814` names "a comment" among the five specs that lean on the entry |
| C32 | React to a post | a528190 | COVERED-UNFIRED | W | **NOT** | `linkedin_react_to_item`. Fired live 2026-08-31 with `item="placeholder-not-a-real-item"` (`finish.md:122-130`) which confirmed the OFF anchor and refused; never confirmed on a real target |
| C33 | Choose WHICH reaction (Celebrate, Support, Love, Insightful, Funny) | a528190 | EXCLUDED-RULED | W | NOT | `server.py:4206-4213`: "pressing this control applies whatever LinkedIn's default reaction is, and nobody has measured which one that is. `Open reactions menu` is a separate control beside the toggle and has never been opened" |
| C34 | React to a comment | a528190 | GAP | W | NOT | the permalink draws exactly one reaction control, the post's; comment-level reaction controls were never enumerated |
| C35 | Remove or change a reaction | a528190 | EXCLUDED-RULED | W | partial (the row goes, the notification does not) | `writes.py:1801-1814`: "react_to_item does not lean on this entry at all, because its reversible_by rests on a different gap -- the ON-state label has never been observed, so there is no selector for the inverse" |
| C36 | Save a post or article to Saved Items | a527126 | GAP | W | REV | `/my-items/saved-posts/` appears exactly once in the repo, as row 8 of the 17 refused draft-hunt addresses. Never considered as a capability  **COST CORRECTED 2026-09-19, `SAVED-POSTS-SURFACE`, and it moves the expensive way.** The ledger prices this at one allowlist pattern on the strength of this census calling it *one allowlist entry away*. That rests on an UNMEASURED premise: `readonly.py` states that `/my-items/saved-jobs/` *now redirects* to the job tracker as settled fact, and the claim enters in `543660c` (2026-08-22) with no before/after landing measurement behind it -- the pattern's removal the same day is justified as dead-code hygiene, not as a redirect check. Every other `/my-items/` hit in the tree is an offline `assert_read_url()` refusal (which confirms only *absent from the allowlist*) or prose. AND THE INSTRUMENT THAT WOULD SETTLE IT CANNOT BE POINTED HERE: `scripts/_probe_landed_address_sweep.py` gates on `is_read_url` BEFORE `BROWSER.goto()`, so a landing can only be measured for an address already admitted, and admitting one first is Amendment A10. Whoever takes this must admit the address and run the landed-address check IN THE SAME WAVE. See `_audit/2026-09-19-content-tail.md` section 4.1 |
| C37 | Unsave a saved post | a527126 | GAP | W | REV | same  **COST CORRECTED 2026-09-19 with C36; the same unmeasured `/my-items/` landing premise gates both, and the write question sits behind the address question.** See `_audit/2026-09-19-content-tail.md` section 4.1 |
| C38 | View post analytics (impressions, viewer demographics) | a525196, a516971 | GAP | R | REV | `/analytics/creator/content/` appears once, in the same refused-address list. The impression figures the repo cites (113/319/1,287) were read off the profile by hand, not by any tool  **STAYS GAP, AND THE BLOCKER IS NARROWER 2026-09-19.** The address is no longer refused and is now READ BY A TOOL (`linkedin_creator_analytics`, see `C40`), so the impressions half is reachable -- but this row asks for **PER-POST** analytics and **VIEWER DEMOGRAPHICS**, and the shipped read delivers neither: it returns a per-DAY series for the account, with one metric. **Demographics are a description of other people however aggregated** and need a name-free resolution before anything reads them. Per-post needs a per-post surface this address does not serve. Not blocked on a reader |
| C39 | View analytics for your comments | a7436043 | GAP | R | REV | never named |
| C40 | View your creator analytics | a704175 | COVERED-PROVEN | R | REV | **BANKED 2026-09-19 -- `linkedin_creator_analytics` SHIPPED AND CALLED OVER THE TOOL PATH, not just a reader.** Returned a complete Sep 13-19 impressions series, `points_found` 7, values `[0, 0, 2, 4, 6, 10, 10]`, `readable` true. **THE VALUES ARE IN THE ACCESSIBLE NAMES, NOT THE TEXT** -- the document carries 1,869 chars of text in total, `main` 1,690 of them, with ZERO `table`/`h3`/`canvas` against 56 `svg`, so the numbers are drawn and `aria-label` on the chart nodes is the only text route in. **The headings are a trap and are recorded as one**: `h2` here reads FEED-shaped chrome (`Feed post`, `Ad Options`), identical to the feed's own, and the first reading of this surface went that way and said nothing about analytics. **The discrimination is the difficulty, not the parsing** -- 34 labelled nodes, and the nav (`Notifications, 6 new notifications`) is the same shape as a datapoint to any reader selecting labels with a digit in them; a label is admitted only when it carries a DATE and a closed-vocabulary metric. Evidence `scripts/_probe_creator_content_analytics.py`, parser `linkedin_server/chart_labels.py` (23 tests, shown REFUSING on the live nav before accepting). **REOPENER:** `points_found` 0 with `labels_seen` large means the route died, not that the account has no data |
| C41 | View your own activity feed | a546122 | COVERED-UNFIRED | R | REV | `linkedin_my_activity_items`. Every recorded live run refused -- `perform.md:276-286` shows `refused: no_page_owner_heading`, `owner_headings 0`; a later run gave `no_self_assertion, five consecutive calls`. It has never returned an item |
| C42 | Address a specific post by identifier (precondition for C25, C32, C34) | -- | EXCLUDED-RULED | R | REV | `finish.md:565-592`: "**AND THE TARGET CANNOT BE NAMED, which the ruling did not reach.** To open `/feed/update/<urn>/` you need a urn, and **no tool in this server returns one.** The census substitutes `<urn>` out before counting, deliberately" |
| C43 | Read a post's text | a546122 | GAP | R | REV | `/feed/update/<urn>/` is on the allowlist and `linkedin_surface_census` reduces every name to a SHAPE, so the permalink is readable and its content is not. No tool returns post text |
| C44 | Write and publish an article | a522427 | EXCLUDED-RULED | W | **NOT** | `writes.py:926-929`: "THE ARTICLE ROUTE IS DELIBERATELY NOT USED. `/article/new/` is on the allowlist too and is WORSE measured: its publish control comes back `<redacted>`, blanked as a singleton, so that route has no measured anchor where this one does" |
| C45 | Add or edit rich media in an article | a521719 | GAP | W | REV | depends on C44; `set_input_files` unsanctioned |
| C46 | Embed content within an article | a522472 | GAP | W | REV | never named |
| C47 | Manage, share or duplicate article drafts | a523042 | EXCLUDED-RULED | R+W | REV | `lift.md:88-92`: `/pulse/drafts/`, `/drafts/`, `/content/drafts/` all `REFUSE  not on the allowlist`, enumerated deliberately |
| C48 | View all your articles | a520701 | GAP | R | REV | never named  **MEASURED 2026-09-19: no article read row is one pattern away.** `/in/me/recent-activity/articles/` and `/pulse/` both refuse through `is_read_url` (absolute spellings, controls behaving), so `ARTICLE-SURFACE`'s single `allowlist +1` is owed at least twice -- once for the article list and once for `/pulse/` -- and this wave established no reader behind either. See `_audit/2026-09-19-content-tail.md` section 5 |
| C49 | Manage comments on your articles | a522438 | GAP | W | mixed | never named |
| C50 | Create a newsletter | a522525, a591266 | GAP | W | **NOT** (it mails subscribers) | zero hits for "newsletter" anywhere in the repo |
| C51 | Manage a newsletter | a517925 | GAP | W | REV | same |
| C52 | Manage your LinkedIn feed preferences (follow / unfollow topics and sources) | a528074 | EXCLUDED-RULED | W | REV | **CORRECTED 2026-09-19 BY THE WAVE THAT GOT IT WRONG, SECOND TIME TODAY.** This row was moved to MEASURED-ABSENT in `09d56d4` on a live read of the FEED. **That was the wrong surface for this row and the state is withdrawn.** The capability is not absent: a sibling wave measured its real address, `/mypreferences/d/unfollowed`, and it is **refused at the FORBIDDEN-SUBSTRING gate by `/unfollow`** (`readonly.py:1096`) -- so an allowlist edit cannot reach it at all. See `_audit/2026-09-19-settings-tail-addresses.md:108`, which also declined to adopt my state change and flagged it as not its claim, correctly. **HOW I GOT IT WRONG, because it is the third instance of one disease in this wave:** this row's hashtag wording was CORRECTED OUT on 2026-09-03 (see the tail of this cell) and it now reads *feed preferences*. I measured hashtags on the feed -- the surface the row USED to name -- and labelled the row on that. Same error as `P D25`, where the needle came from a help article the row was already recorded as having outgrown: **a measurement aimed by a row's stale wording rather than by what the row now says.** **THIS ALSO SETTLES CONFLICT C** of `_audit/2026-09-06-corpus-sweep-blocker-evidence.md` s3: `M C52` is `FEED-PREFERENCES`, not `HASHTAG-EXISTENCE`, corroborated from two independent directions -- `_audit/2026-09-05-settings-tail.md:224` names it fully-qualified, and the address measurement above reaches the same verdict by the gate. My own hashtag reading does not support the `HASHTAG-EXISTENCE` assignment; it undermines it, because it finds no hashtag surface for this row to have been about. **THE HASHTAG READING ITSELF STANDS -- it is simply evidence about a DIFFERENT question** (the hashtag surface, and thereby `network.md` rows 59-61) and is preserved below unchanged: **READ LIVE 2026-09-19 -- the feed draws no followable hashtag surface.** Two loads on two instruments 13 minutes apart, both with their page control passing (census 263 controls, settle CONSISTENT against a ~277 baseline): `a[href*='hashtag']` **0**, `a[href*='/feed/hashtag/']` **0**, `/feed/hashtag/` 0 in html, `#hiring` 0, `Followed hashtags` 0, `hashtag` 0 in main text. **STATED LIMITATION, because a refusal that reports only what it missed is half a measurement:** the raw HTML carries 20 then 15 occurrences of the word across the two loads, and my context classifier accounted for **0 of 15** -- all seven classes (href, path, attribute name, json key, json string, class token, urn) read zero, so those occurrences live somewhere I did not enumerate. Zero anchors does not depend on that. **LIMITATION REPAIRED SAME DAY.** The guessed classes were replaced with a PARTITION -- script content vs everywhere else, exhaustive by construction, with its sum asserted and printed rather than assumed. Two further loads: 23 in `<script>` + 10 elsewhere = 33, `PARTITION SUMS: PASS`; then 0 + 10 = 10, `PARTITION SUMS: PASS`. **The raw count is unstable across loads (20, 15, 33, 10) -- the feed is not a settled surface and every count here is a reading with a timestamp. What is stable across all four readings is the part that matters: 0 in main text, 0 `a[href*="hashtag"]`, 0 `a[href*="/feed/hashtag/"]`.** A word in a payload is not a surface a member can reach. The lesson the first classifier taught is worth more than the counts: **seven guessed buckets that all read zero look exactly like absence, and were really a classifier that did not fit** -- which is why the replacement is a partition whose arithmetic can fail. **This does NOT rule on `network.md` rows 59-61**, which were deliberately kept mapped because removing capabilities on an inference is the same undercount that pass exists to fix. Evidence `_audit/_scratch/_probe-small-measures-live.txt`, `_probe-unmeasured-surfaces-live.txt`. **ROW CORRECTED 2026-09-03.** It previously read "Follow a hashtag / topic" sourced to `a528144`, which **returns HTTP 404**, and two independent help-index queries (`q=hashtag`, `q=follow topics interests feed`) return no hashtag-following article at all. What the index does document is feed preferences and the profile Interests section (`a569139`). The capability as I first stated it is not sourceable from LinkedIn's own index; this row is what survives |
| C53 | *(retired -- see C52)* | -- | -- | -- | -- | the unfollow half of an unsourceable row. Retired rather than kept, and recorded rather than deleted |
| C54 | Create a collaborative post | a14240120 | GAP | W | **NOT** | zero hits  **COST CORRECTED 2026-09-19. This row needs NO allowlist pattern: the post composer is an address already loaded.** Blocker 51's single `allowlist +1` is owed by C76 alone, which is a different LinkedIn product. AND IT DOES NOT RETIRE WITH C55: a collaborative post can be created before anybody is invited, so the create half names no third party. See `_audit/2026-09-19-content-tail.md` section 2 |
| C55 | Manage collaborators on a collaborative post | a14180127 | EXCLUDED-RULED | W | REV | zero hits **RETIRED 2026-09-19, `MENTION-COMPOSITION-RULING`, on the SAME shipped assertion as C10 and C28, reached from the other end.** Inviting a named collaborator carries a third party's identity into content this server publishes AND notifies the person named -- the line is DESTINATION, not presence, and this destination is outward and permanent. `collaborator`/`collaborators` are already in `FORBIDDEN_PARAMETER_NAMES` (`tests/test_no_write_tool_names_a_third_party.py`), so the ruling was shipped and tested before this row was ever read against it. `tests/test_a_retired_row_rests_on_a_live_assertion.py` now couples the two, so deleting that name turns this row red. NOTE THE SPLIT: C54 and C56 do NOT retire with it -- a collaborative post can be created before anybody is invited, and removing YOURSELF names no third party. REOPENER: as C10. See `_audit/2026-09-19-content-tail.md` |
| C56 | Remove yourself from a collaborative post | a14250134 | GAP | W | NOT | zero hits  **COST CORRECTED 2026-09-19 with C54: no allowlist pattern, and removing YOURSELF names no third party, so C55's retirement does not reach it.** See `_audit/2026-09-19-content-tail.md` section 2 |
| C57 | Create a LinkedIn Event | a554183 | GAP | W | REV (an event can be edited or cancelled) | zero hits for "event" as a capability |
| C58 | Attend or leave a LinkedIn Event | a548541 | GAP | W | REV | attending puts him on a public attendee list |
| C59 | Create or broadcast a LinkedIn Live | topic a151003 | EXCLUDED-RULED | W | **NOT** | zero hits; needs a third-party streaming tool, so it is outside a browser driver regardless **RETIRED 2026-09-05, `LIVE-BROADCAST` (3.5), on LinkedIn's own sentence fetched this pass:** `a568503` -- you cannot stream directly from LinkedIn, a streaming tool is needed to broadcast LinkedIn Lives. A browser driver cannot supply a video stream and LinkedIn says outright that no native path exists. REOPENER: browser-native go-live with no external encoder. See `_audit/2026-09-05-decide-retire-rulings.md` |
| C60 | Access your LinkedIn Groups | a566460 | COVERED-PROVEN | R | REV | **BOTH HALVES OF THIS CELL WERE STALE AND THE ROW WAS NEVER MOVED.** It read "zero hits for Groups as a capability; `/groups/` is on neither the allowlist nor the forbidden list" -- `/groups/` ROOT has been ADMITTED since 2026-09-05 (`readonly.py:572`, root only; `/groups/<id>/`, `/members/`, `/requests/`, `/discover/` and `/search/results/groups/` stay named refusals), and the capability shipped as **`linkedin_group_memberships`** (`server.py:1894`, wired through `groups_page.read_group_memberships` onto `groups.py`). Re-verified independently 2026-09-19 by reading the tree: `tests/test_the_groups_tool_keeps_its_properties.py` **30 passed**, `tests/test_every_tool_is_on_the_surface.py` 15 passed. **FIRED LIVE 2026-09-05 ~22:17** with a cost bracket taken on the FEED at both ends, because the Groups page's own nav carries no count-bearing control -- it returned `unmoved` (notifications badge ONE before, ONE after), refuting its own docstring's prediction that the cost would read `degenerate`. **NAME-FREE STRUCTURALLY, not by filtering:** every href goes into `groups.membership_tally`, which takes no name as a parameter anywhere, and a non-numeric path segment is refused BECAUSE A SLUG IS A NAME. The membership count is corroborated by four instruments sharing no input feature (heading boundary, per-row control, row-scoped containment, and `Leave this group` drawn per row) |
| C61 | Join a group | a540824 | GAP | W | REV | **RE-COSTED 2026-09-19: this is DECIDE, not MEASURE, and no measurement moves it.** The joinable surface was measured absent where it could be looked for: the prior wave found NO join control drawn on any suggestion row on `/groups/` -- nothing repeats across the five, and a join affordance would wear one label on all of them and tally 5. So this needs `/groups/<id>/` or `/groups/discover/`, and **both are NAMED REFUSALS in `readonly.py`'s own comment** (`:540-549`), not merely undeclared. **AND A BOUNDARY CHANGE ALONE WOULD NOT BUY IT.** That same comment: *"NO WRITE IS BOUGHT BY THIS. Joining, leaving, posting and inviting all need their own url, their own sanction and their own ruling."* So the real price is THREE things -- an address, a write sanction, and a ruling -- against a ledger that prices `GROUPS-SURFACE` at `allowlist +2, WriteSpec`. Evidence `_audit/_scratch/_progress-groups-surface.md`, `_audit/2026-09-05-groups-surface-measured.md` |
| C62 | Withdraw a group membership request | a542733 | EXCLUDED-RULED | W | REV | same; `/withdraw` is a forbidden substring, which would catch the url incidentally. **RE-FILED 2026-09-19 BY THE CROSS-CUTTING SWEEP. NOT a new decision, and the cell UNDERSTATED the ground it already named.** The url being caught incidentally is the weaker half; the ACT is squarely refused by `writes.PERMANENTLY_FORBIDDEN['delete_or_withdraw_anything']` (`writes.py:2004`): *"destruction is not a write this design covers, AT ANY CONFIRM LEVEL."* **A withdraw is the named act, not a url that happens to match** -- so no allowlist edit, no confirm token and no WriteSpec reaches it, and finding a differently-spelled address would not reopen it. That entry is load-bearing well beyond this row: five shipped specs cite it in `reversible_by`, which is how an application, a post, a comment, an invitation and a message can each say NOBODY can take them back through this server. REOPENER: the operator ruling that destruction is covered |
| C63 | Leave a group | a566460 | GAP | W | REV (re-joinable, possibly by approval) | same |
| C64 | Post content in a group feed | a539929 | GAP | W | **NOT** | a second publishing surface with its own composer, entirely uncensused |
| C65 | Add a comment to a group conversation | a545818 | GAP | W | NOT | same |
| C66 | Mention group members in a conversation | a563278 | EXCLUDED-RULED | W | NOT | same  **RETIRED 2026-09-19 on the MENTION/TAG ACTION-CLASS RULING, which was reached 2026-09-05 and only half applied.** `_audit/2026-09-05-article-publish.md:82`: *"The ruling reaches the ACTION CLASS -- compose a mention or a tag into published content -- and whoever holds the map should apply it ROW BY ROW rather than take my count."* That document enumerates four mention rows; `C10` and `C28` were applied in `58ba421` and these were not. The fourth of that document's four mention rows, and the same act on a group surface: the identity named is carried to every member of the conversation. `mentions` is the forbidden name. Enforced by `FORBIDDEN_PARAMETER_NAMES` (`tests/test_no_write_tool_names_a_third_party.py:54-70`), asserted over every `linkedin_*` signature off the AST by `test_no_tool_takes_a_third_partys_identity_as_a_parameter`; bound to this row by `tests/test_a_retired_row_rests_on_a_live_assertion.py`, so deleting the name re-opens the row instead of leaving the retirement standing. |
| C67 | Edit or delete a group post or comment | a542920 | GAP | W | NOT | edit never named; the delete half would meet `delete_or_withdraw_anything` |
| C68 | Submit a group post for admin approval | a551360 | GAP | W | REV | never named |
| C69 | Invite connections to join a group | a547071 | EXCLUDED-RULED | W | NOT | R2 (`network.md:639`) -- **this row's own note already stated R2's condition**: *reaches third parties; `/invite` is a forbidden substring*. Re-verified 2026-09-19: `/invite`, `/connect`, `invitation` and `/withdraw` are all on `_FORBIDDEN_URL_SUBSTRINGS`. A row that names the ruling's own premise and is filed GAP is the propagation failure in its purest form |
| C70 | Search for content within Groups | a548435 | GAP | R | REV | never named. **NEEDS A RULING, NOT A MEASUREMENT -- and the refusal is already written down.** `/search/results/groups/` is a NAMED REFUSAL in `readonly.py`'s own groups comment (`:547-549`), which says in terms why it was not inherited there: *"belongs to SEARCH-RESULTS-SURFACE, which is queued DECIDE and is not this entry's to inherit."* So the boundary question was deliberately left to this blocker rather than settled sideways by a neighbouring one. No further measurement moves this row; what it needs is the DECIDE its own queue column already names. Doubly gated here: content search inside groups needs BOTH a search-results address AND a per-group address, and `/groups/<id>/` is itself a named refusal -- two boundary changes, not one |
| C71 | Boost a post (paid promotion) | a7421378, a10403062 | EXCLUDED-RULED | W | NOT (money is spent) | never named; the only capability in this slice that costs currency **RETIRED 2026-09-05, `PAID-BOOST` (3.12).** The only capability on this census that costs currency. This server has no payment authority and must never acquire one: a confirm token binds to a canonical target, and a boost's target is a budget, a duration and an audience chosen across a multi-screen wizard, not a control with a value. Every consent line must say what it costs him, and here the amount is unknowable before the flow is entered. No undo. REOPENER: nothing that keeps the shape. This does NOT reach READING a post's analytics. See `_audit/2026-09-05-decide-retire-rulings.md` |
| C72 | Share a post off LinkedIn | a7443434 | GAP | R | REV | never named  **THE WRITE HALF WAS RETIRED AND THIS READ HALF WAS DELIBERATELY PRESERVED.** `N 50` retired 2026-09-05 because the ACT is pressing a button embedded on a third party's website, which `server.py:5706-5711` already rules out -- driving a form on somebody else's domain, under their terms, is not this server's to do at any capture quality. **That ruling explicitly spared the READ**, which is this row: obtaining the link or embed is done ON LinkedIn, on pages already admitted. **So this is a MEASURE, mis-queued as DECIDE-RETIRE** -- there is nothing left to decide, because the decision was made and it came down in this row's favour. NEXT ARTIFACT: a needle pass for the control on an already-admitted address; zero boundary cost.  **MEASURED LIVE 2026-09-19 UP TO THE PRESS BOUNDARY, AND THE BOUNDARY IS WHERE IT STOPS.** `/feed/`, page control PASS, nothing pressed. **The share TRIGGERS RENDER:** `Send` 3 and `Repost` 3 in main text, `Share` 56 in html. **The off-platform ITEMS do not:** `Copy link` 0/0, `Share via` 0/0, `Embed this post` 0/0. **AND THOSE ZEROS ARE UNINFORMATIVE BY CONSTRUCTION, which was PREDICTED BEFORE THE RUN rather than discovered after it** -- the page draws 10 `[aria-haspopup]` triggers against exactly **1** `[role=menuitem]` and 3 `[role=menu]`, so the menus are BUILT ON DEMAND and a control absent until its menu opens reads identically to one that does not exist. **SO THE ROW IS NOT BLOCKED ON A SURFACE OR A BOUNDARY: it is blocked on a PRESS**, on a feed item, and that press is the same open question as `N 133`/`N 134` and `MATCH-DETAILS-COLLAPSED`. It is NOT the same as pressing a button on a third party's site, which is what `N 50` was retired for. Evidence `_audit/_scratch/_probe-off-platform-controls.txt`; instrument `scripts/_probe_off_platform_controls.py`, shown failing before admission  **RULED 2026-09-19, PERMITTED, AND STILL BLOCKED -- the distinction is the point.** `_audit/2026-09-19-the-disclosing-press-ruling.md` (`a0379d5`) grants the disclosing press this row was waiting on, under FOUR CONDITIONS THAT MUST ALL HOLD: (1) the page is ALREADY ADMITTED -- a press never extends reach; (2) the control matches an ENUMERATED DISCLOSURE SHAPE **by ATTRIBUTE** (`[aria-expanded]`, `[aria-haspopup]`), never by label text; (3) the press is SHOWN not to move an outward counter, on the `read_invitation_badge` discipline, and **where no counter can price a press, unmeasurable resolves AGAINST the press**; (4) it is closed and the closure VERIFIED. Refused regardless: navigation, submission, composers, any third-party surface, and **typing -- a press is not a fill**. **SO THIS ROW IS NOW BLOCKED ON THE MECHANISM, NOT ON A RULING**, and that re-filing is deliberate: `messaging-measure` owns the boundary and is building the enumerated shape list, the refusal shown failing, and the counter check. **Nobody presses until it lands** -- a ruling is not permission to act ahead of the guard that bounds it, which is how a narrow ruling becomes a wide practice.  **UPDATED 2026-09-19 ON THE SHIPPED GATE.** The press mechanism SHIPPED 2026-09-19 (`linkedin_server/press.py`, `tests/test_press.py`, `9c69ae9`), so this row is **no longer blocked on the mechanism** and the census should not keep saying so -- a deferral that will never resolve consumes a future wave, and these three do not all resolve the same way. Put through `press.evaluate` rather than inferred: **`/feed/` + `[aria-haspopup]` passes address and shape, then REFUSES at condition 3** -- `no_counter_prices_this_press`, *"no counter was read at BOTH ends, so nothing prices this press."* This is the concern this wave flagged to `messaging-measure` before the gate was built, and it is the RULING WORKING rather than a gap: on a 2026-09-19 read of `/feed/` no counter moved for either nav badge, and a feed item belongs to a third party, so *unmeasurable resolves AGAINST the press* has to bite there if anywhere. **BLOCKED ON FINDING A COUNTER, NOT ON THE MECHANISM.** The refusal is explicitly `reachable_by_this_route: true` -- **NOT YET, not NEVER** -- so a counter that prices a share-menu press would unblock it without any further ruling. Unswept candidates: the item's own reaction and comment counts, a saved-items count, the notification badge, any per-post state the shaper already emits. If an exhaustive search finds none, **this becomes EXCLUDED-RULED, not a standing deferral**  **CORRECTED AGAIN 2026-09-19, AND THE CORRECTION IS AGAINST THIS WAVE'S OWN READING.** The cell above says no counter prices a feed press. **A counter DOES exist.** My reading was ACCURATE AND IRRELEVANT, which is a different failure from being wrong: I read the NAV BADGES, which count pending invitations and unread messages -- **neither of which a feed press could plausibly move.** **A COUNTER THAT CANNOT MOVE FOR THE ACT IN QUESTION PRICES NOTHING**, so that reading could not have answered the question in either direction. It is the sibling of this repo's own scar that a badge at zero cannot separate *consumed nothing* from *there was nothing to consume*. **THE RIGHT INSTRUMENT CLASS IS PER-CONTROL STATE ON THE PAGE THE PRESS HAPPENS ON**, and it already ships: `dom.read_reaction_surface` (`dom.py:7204`) returns `off_state`, counting `button[aria-label="Reaction button state: no reaction"]` (`REACTION_OFF_LABEL`, `dom.py:6857`). One `/feed/` read, nothing pressed: **off_state = 3**, non-zero, alongside 3 reaction controls, 4 menus and 63 buttons as the firing control. A reaction is visible to the post's author, which is what makes it OUTWARD rather than a render detail. **AVAILABILITY IS VERIFIED BY INSTRUMENT; SENSITIVITY IS DERIVED AND NOT VERIFIED** -- the counter exists and reads 3, and a reaction necessarily leaves that state because of what the label MEANS, not because anybody has watched it move. Watching it move needs a press, and the first sanctioned press is what would upgrade this to verified. **SO: BLOCKED ON TAKING THE MEASUREMENT.** Not on the mechanism, and NOT EXCLUDED-RULED. `press.disclose` accepts any `read_counters` callable, so wiring `read_reaction_surface` in is caller-side work needing no change to the gate. **TWO COUNTER CANDIDATES RULED OUT WITHOUT A LOAD, recorded so nobody re-checks them:** `/my-items/saved-posts/` and `/my-items/` are **refused by the read boundary** (`is_read_url` False on both, verified here), so a saved-items count is unreachable -- the same shape as the drafts problem; and `/notifications/` is admitted but has no reader in this package and is measured to RESET ITS OWN BADGE ON LOAD, so pricing a press with it would spend the very thing being counted. Source: `messaging-measure`, who corrected their own confirmation of my finding after the lead ruled that one wave's read of one page is not an exhaustive search. |
| C73 | Allow or disallow your posts being embedded | a7462020 | GAP | W | REV | never named |
| C74 | Read your feed | a1480504 | COVERED-CANNOT-DELIVER | R | REV | `/feed/` is on the allowlist and has been censused dozens of times -- for CONTROL COUNTS. No tool returns a feed item. "286 controls, 1 form, 0 contenteditable" is what the feed looks like from here **BANKED 2026-09-19: THIS CELL WAS ALREADY THE CANNOT-DELIVER ARGUMENT, FILED AS GAP.** `linkedin_surface_census(surface="feed")` exists and HAS fired live on this surface -- the same census measured `/feed/` carrying ZERO item permalinks and EIGHT DIFFERENT authors. It cannot return feed content, and that is structural rather than a setting: "THE CENSUS REPORTS SHAPES, NEVER NAMES", enforced by `shape.census_shape`, `census_href_identifies_entity` and `census_redact_rare`. A tool that reports HOW MANY CONTROLS does not cover a row asking to READ THE FEED. |
| C75 | Read notifications about engagement on your content | -- | **COVERED-PROVEN** | R | **NOT** (loading clears the badge) | `linkedin_notifications`; one measured call 2026-08-21 took the badge from 1 to 0 and it did not come back. Overlaps the network slice -- flagged rather than double-counted there |
| C76 | Contribute to a collaborative article | a1413111, a1443723 | GAP | W | **NOT** | recovered 2026-09-03 by help-index search. A whole LinkedIn product -- AI-seeded articles members add sections to under their own name, with a Top Voice badge attached to doing it well. Absent from the Share Content and Post topic trees entirely  **RE-FILED 2026-09-19 as `COLLABORATIVE-ARTICLES` (1W, allowlist +1). This row is the ONLY one of blocker 51's four that owes a boundary pattern**, measured through `is_read_url` at this tree: `/collaborative-articles/` and `/pulse/collaborative-articles/` both refuse, while the post composer the other three use is already loaded. See `_audit/2026-09-19-content-tail.md` section 2 |
| C77 | Delete an article | a522451 | EXCLUDED-RULED | W | **NOT** | `writes.py:1801-1814` `delete_or_withdraw_anything`. LinkedIn's own article is titled *"Unable to retrieve deleted articles"*, which is the platform confirming the irreversibility the repo's entry asserts |
| C78 | Set the visibility of your articles | a517863 | GAP | W | REV | recovered by help-index search; never named |
| C79 | Follow or unfollow member articles | a519786 | GAP | W | REV | recovered by help-index search. Distinct from following a person; never named |
| C80 | Subscribe or unsubscribe to a newsletter | a1644939 | GAP | W | REV | recovered by help-index search. A READER-side capability -- the two newsletter rows I had were both author-side |
| C81 | Create a Newsletter Page | a518936 | GAP | W | REV | recovered by help-index search |
| C82 | Share a Newsletter Page | a521766 | GAP | W | REV | recovered by help-index search |
| C83 | View newsletter analytics | a1658525 | GAP | R | REV | recovered by help-index search |
| C84 | Manage multiple newsletters | a6588862 | GAP | W | REV | recovered by help-index search |
| C85 | Vote in a poll / view poll results | a527273, a527270 | GAP | W | **NOT** | recovered by help-index search. My original poll row was author-side only; voting is the reader-side act and it cannot be changed once cast |
| C86 | Tag people in your photos | a522896 | EXCLUDED-RULED | W | NOT once posted | recovered by help-index search. Distinct from an `@` mention in text -- a coordinate-anchored tag on an image  **RETIRED 2026-09-19 on the MENTION/TAG ACTION-CLASS RULING, which was reached 2026-09-05 and only half applied.** `_audit/2026-09-05-article-publish.md:82`: *"The ruling reaches the ACTION CLASS -- compose a mention or a tag into published content -- and whoever holds the map should apply it ROW BY ROW rather than take my count."* That document enumerates four mention rows; `C10` and `C28` were applied in `58ba421` and these were not. **This row is the TAG half of that action class, not the mention half.** The ruling reads "a mention **or a tag**", and five of the thirteen forbidden names are tag spellings (`tag`, `tags`, `tagged`, `tagged_person`, `tagged_people`), which is the shape the rule was built around. A coordinate-anchored tag names a third party on media published to others. Enforced by `FORBIDDEN_PARAMETER_NAMES` (`tests/test_no_write_tool_names_a_third_party.py:54-70`), asserted over every `linkedin_*` signature off the AST by `test_no_tool_takes_a_third_partys_identity_as_a_parameter`; bound to this row by `tests/test_a_retired_row_rests_on_a_live_assertion.py`, so deleting the name re-opens the row instead of leaving the retirement standing. **Deliberately NOT extended to `C87`, `C88`, `C89`** -- the same source rules those out by article id as self-scoped privacy controls governing who may tag HIM. |
| C87 | Remove a mention or tag of yourself | a524346 | GAP | W | REV | recovered by help-index search. The one capability in this family that acts on somebody ELSE's content, on his own behalf  **RE-FILED 2026-09-19: this row's EARLIEST binding constraint is the target-naming gap, not a mention control.** To act on a post you must address it, and C42 is already EXCLUDED-RULED for exactly that -- *to open `/feed/update/<urn>/` you need a urn, and no tool in this server returns one*. Under the ledger's own assignment rule (one blocker per row, the earliest binding constraint) this row belongs against the post-identifier gap: it would be blocked there even if every mention control in LinkedIn were mapped. `MENTION-TAG-CONTROLS` therefore holds TWO rows, not three, and both are settings. NOT retired -- re-filed. See `_audit/2026-09-19-content-tail.md` section 4.3 |
| C88 | Choose whether members can mention, tag or collaborate with you | a522861 | GAP | W | REV | recovered by help-index search; a setting, never named  **MEASURED 2026-09-19: NOT reachable through the shipped settings tool, and this answers the open question in `_audit/2026-09-05-article-publish.md` section 2b.** `linkedin_update_setting` refuses any setting outside `READABLE_SETTINGS` and opens NO PAGE AT ALL when it does; its docstring states *one setting is writable, and asking about any other loads nothing*. Confirmed offline: `/mypreferences/d/categories/` and `/mypreferences/d/categories/visibility` both refuse through `is_read_url`, against controls that behaved. And the reason is the boundary trap itself, in the tool's own words: *`Close and delete account` and `Hibernate account` are addresses in it. A permission written for the FAMILY would carry those with it.* So the cost is not *reuse a shipped tool* -- it is an address NOBODY HAS OPENED, this repository's measured `allowlist +1` placeholder class. The ledger's 7 is not too high; it is not yet a number. See `_audit/2026-09-19-content-tail.md` section 4.2 |
| C89 | Set the visibility of mentions and tags | a524212 | GAP | W | REV | recovered by help-index search  **MEASURED 2026-09-19 with C88: same refusal, same reason, same unopened address.** See `_audit/2026-09-19-content-tail.md` section 4.2 |
| C90 | Verified comments filter on your post | a10721097 | GAP | W | REV | recovered by help-index search; a per-post comment control |
| C91 | React in a group conversation | a549002 | GAP | W | REV | recovered by help-index search. Reactions have a third surface -- posts, messages (M48) and group conversations -- and the repo names only the first |
| C92 | Comment on an Event and reply to Event comments | a738312 | GAP | W | NOT | recovered by help-index search. See s10 -- overlaps the sibling's Events slice and is flagged rather than claimed |

**CORRECTED BY:** `_audit/2026-09-05-routes-already-admitted.md` -- row `C60` above says `/groups/` is on neither the allowlist nor the forbidden list; commit `6b5dad5` admitted the `/groups/` root on 2026-09-05 and it is machine-verified ALLOWED at HEAD, so what holds that row is the render and the missing reader rather than the boundary.

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
preferable to dropping between two agents. If the sibling's slice claims them,
subtract exactly the rows named here.

**EXECUTED 2026-09-19. THE CONDITION WAS MEASURED MET FOR FOUR OF THESE ROWS AND
THE DENOMINATOR IS NOW 138.** This is not a new decision -- it is this section's
own conditional, fired once its trigger was checked, which nobody had done.

| subtracted | the sibling row that claims it | matched how |
|---|---|---|
| `C60` Access your LinkedIn Groups | `N 173` Access the list of groups you belong to | hand-read; both COVERED-PROVEN |
| `C61` Join a group | `N 63` Join a LinkedIn group | hand-read |
| `C63` Leave a group | `N 64` Leave a LinkedIn group | hand-read |
| `C69` Invite connections to join a group | `N 168` Invite your connections to join a group | hand-read; both now EXCLUDED-RULED under R2 |

**The other twelve flagged rows have NO sibling twin and are correctly still
counted** -- `C62`, `C64`-`C68`, `C91`, `C57`, `C58`, `C92`, `C59`, `C75`.
`network.md` has no group-composer rows and no create-an-Event row, so those
capabilities exist in this slice alone.

**MATCHED BY HAND, NOT BY SCORE, and that mattered:** a similarity pass over
these sixteen at a 0.62 bar returned nine twins of which only three were real --
it scored *Create a LinkedIn Event* against *Leave a LinkedIn group* at **0.67**.
The four above were read, not ranked.

**The rows are NOT deleted**, per this section's own title: their content and
evidence stay here for whoever reads them. What changed is that they no longer
count toward this slice's capability denominator, because the sibling counts
them. Nothing was pinned to 142 -- checked across `tests/` and `scripts/` before
the edit.

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
