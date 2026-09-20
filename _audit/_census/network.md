# CENSUS SLICE: NETWORK AND PEOPLE

Written 2026-09-03. Read-only. **No LinkedIn account was touched**: no browser,
no session, no page load, no `mcp__linkedin__*` call. The taxonomy was imported
by walking LinkedIn's PUBLIC Help Center; the coverage verdicts come from the
repository at ``. Nothing was
committed and no tracked file was edited.

---

## 1. COUNTS

    CAPABILITIES ENUMERATED, IN SCOPE, MAPPED       194

      COVERED-PROVEN                                  3
      COVERED-UNFIRED                                  5
      COVERED-CANNOT-DELIVER                          1
      EXCLUDED-RULED                                 78
      GAP                                           107

**DELTA SINCE THE FREEZE, 2026-09-04. The block above is UNCHANGED**, so every
document citing those numbers still resolves against them. What moved:

    CAPABILITIES ENUMERATED      194  ->  194   no row added or removed
      MEASURED-ABSENT              0  ->    1   N 118, endorsement counts
      GAP                        107  ->  106   N 118 left it

`MEASURED-ABSENT` is defined in section 2, added the same day: no tool, and a
LIVE READING of the surface says LinkedIn does not draw the thing. Filing N 118
as GAP would say "no tool and no reason", which INVERTS A MEASUREMENT -- the
reason exists, and it is stronger than a ruling, because nobody decided against
the capability. **The row is retired, not deleted**, and its reading is quoted
inside it: a deleted row is indistinguishable from a row nobody thought of, and
this census has already sent a wave to build something that is not there.

**CORRECTED BY:** `_audit/2026-09-20-the-reopener-triggers.md` -- row `N 157` moved EXCLUDED-RULED to MEASURED-ABSENT, because its cell reports a measurement and not a decision.

**SECOND DELTA, 2026-09-20, and it is a VOCABULARY correction rather than a
finding.** The two blocks above stay UNCHANGED. What moved:

    EXCLUDED-RULED              92  ->   91    N 157 left it
    MEASURED-ABSENT              2  ->    3    N 157 joined it

**`N 157` was never a ruling.** Its cell reported that a page was read and a
number was not on it, which is this section's own definition of
MEASURED-ABSENT, and it was filed under `R9` -- a ruling about outreach
AUTOMATION -- while being a READ. The twin rows `J 127` and `M M4` assert the
identical fact about the identical object and `J 127` already reads
MEASURED-ABSENT, so this removes a three-way disagreement inside the census
rather than creating one. `_audit/2026-09-20-the-first-firing.md` s4d named the
defect, recorded the evidence and deferred the state word to whoever owns the
vocabulary; `_audit/2026-09-20-the-reopener-triggers.md` is that ruling.
**GAP is untouched and no capability was added or removed.**

Counted separately so neither inflates the member denominator:

    ADMIN-ONLY capabilities (Page admin, group owner/manager,
      event organizer -- rights he does not hold; all 15 are
      GAP -- no tool, no ruling)                                       15
    ----------------------------------------------------------------
    TOTAL ENUMERATED                                                  209

**REVISED 2026-09-03, SECOND PASS.** The first pass mapped 160. A hazard
reported by the team lead -- LinkedIn Help TOPIC pages render "0 articles" for
products that plainly exist, so a topic-tree walk undercounts INVISIBLY -- sent
this slice back to recover four areas that had come back empty or 404. **That
recovery added 34 in-slice capabilities and 6 admin ones, all 34 of them GAPs.**
Section 11 records the delta against the frozen top-level total; section 12
records the instrument that closed the hazard.

Raw rows harvested: **260** (52 invitations + 58 following + 94 discovery + 56
recovery). Removed: 26 duplicates across the first three walks, 16 recovery rows
that duplicate an existing row or belong to the content and messaging slices, 9
rows owned by the messaging census slice, 15 split out as admin-only.

**Three numbers carry this slice.**

**COVERED-PROVEN is 3 of 194, and all three are READS.** They are: the list of
Pages he follows, his profile-viewer list, and the anonymous rows inside it.
**No network or people WRITE has ever completed against live LinkedIn.** Not one
invitation, not one follow, not one unfollow, not one message.

**EXCLUDED-RULED is 78, and it is not 78 decisions.** Six written rulings
produce 71 of the 78. Section 6 splits them out rather than letting the total
imply a deliberation that did not happen 78 times.

**GAP is 107, and 57 of them are three missing surfaces.** People search
(`/search/results/people/`, 23 rows), Groups (18) and Events (15) account for 56
of the 107, and the seventh hashtag row makes 57.
There is no pattern for it in the read allowlist and, critically, **no sentence
anywhere in the repository about it.** Nobody ruled against people search; it
was never considered.

---

## 2. HOW A CAPABILITY WAS ASSIGNED A STATE

    COVERED-PROVEN     a tool exists AND an audit records it firing live and
                       returning what it claims. Cited per row.
    COVERED-UNFIRED    a tool exists and would not refuse at the gate, and
                       nothing records it completing live.
    COVERED-CANNOT-     a tool exists, it HAS fired live, and it cannot do the
      DELIVER          thing. Filing this as COVERED-UNFIRED would say "nobody
                       has tried", which inverts a measurement.
    EXCLUDED-RULED     no tool, and a written passage in this repo gives a
                       reason that BEARS ON THIS CAPABILITY -- naming it, or
                       naming an address family or act-class containing it.
                       Quoted per row group in section 6.
    MEASURED-ABSENT    no tool, and a LIVE READING of the surface says LinkedIn
                       does not draw the thing. Added 2026-09-04 by team-lead
                       ruling, for the same reason COVERED-CANNOT-DELIVER
                       exists one row up: filing this as GAP would say "no
                       tool and no reason", which INVERTS A MEASUREMENT. The
                       reason exists and is stronger than a ruling -- nobody
                       decided against it, the page simply does not carry it.
                       THE ROW SURVIVES RATHER THAN BEING DELETED, and its
                       evidence is quoted in it, because a deleted row is
                       indistinguishable from a row nobody thought of -- and
                       this census has already sent one wave to build
                       something that is not there.
    GAP                no tool and no such passage.

This matches the convention already set by `_audit/_census/profile.md` section
2, deliberately, so the four slices add up.

**The line between EXCLUDED-RULED and GAP.** `readonly._ALLOWED_URL_PATTERNS`
is closed by default: every LinkedIn address not on it is already refused. So
"the allowlist does not list it" is NOT a reason -- it is exactly the silence
this census exists to measure. A row is EXCLUDED-RULED only where something was
WRITTEN: an entry on `readonly._FORBIDDEN_URL_SUBSTRINGS` (a second, independent
gate whose entries carry arguments), a key in `writes.PERMANENTLY_FORBIDDEN`, a
`WriteSpec` refusing in its own words, or an audit passage measuring the
capability unreachable. Everything a general mechanism merely happens to block
is a **GAP with a NAMED BLOCKER**, recorded in the row so nobody reads GAP as
"cheap", but not laundered into a decision.

**THE FIFTH STATE, adopted from a sibling slice on the lead's ruling.**
`linkedin_send_message` HAS run live, twice, and REFUSED both times. The first
pass filed it COVERED-UNFIRED with a footnote; that was wrong, because
COVERED-UNFIRED asserts nobody has tried, and somebody did -- the trying is what
produced the measurement. It is now the slice's ONE
**COVERED-CANNOT-DELIVER** (row 155).

**Exactly one row qualifies, and the boundary is worth stating.** The state
needs a tool NAMED FOR THE CAPABILITY that fired and could not deliver it. Rows
132-136 are not it: `who_viewed_me` has fired successfully and does deliver what
it is named for; the viewer AGGREGATES on the same page are simply not parsed by
anything. No tool is named for them, so they stay GAP. Rows 1, 46 and 48 are not
it either -- those three have never fired at all.

---

## 3. THE SERVER SURFACE THIS SLICE IS MEASURED AGAINST

35 tools in `linkedin_server/server.py`. **Seven touch this slice.**
`writes.PERFORMABLE` holds 12 actions; **four are here** (`send_invitation`,
`follow_company`, `unfollow_company`, `send_message`).

| tool | what it does here | live-fire |
|---|---|---|
| `linkedin_send_invitation` | sends ONE invitation, aimed by a needle among the invitation controls **on his own profile** | **NEVER-FIRED.** Shipped 2026-09-01 as "the FIRST that reaches another person"; failed blocker 2 (whole-url landing against a redirecting `/in/me/`); repaired in `ea5354d` 2026-09-02. No run recorded before or after |
| `linkedin_follow_company` | follows the company **attached to a job posting**, from `/jobs/view/{id}/` | **NEVER-FIRED** |
| `linkedin_unfollow_company` | unfollows a Page by numeric company id, from his Manage Pages list | **NEVER-FIRED** |
| `linkedin_followed_companies` | reads `/mynetwork/network-manager/company/` -- the Pages he follows | **FIRED-SUCCEEDED**, 2 readings, PASS (`_audit/2026-08-31-linkedin-finish.md:273`) |
| `linkedin_who_viewed_me` | Who's Viewed Your Profile off `/analytics/profile-views/`; 365 days on his Premium Career account | **FIRED-SUCCEEDED** -- "Now 10 rows, 10 distinct names, verified live" (`mcp-servers/_audit/2026-08-21-linkedin-parse-fix.md:5`) |
| `linkedin_notifications` | reads `/notifications/`; the delivery path for invite-received and new-follower signals | **NEVER-FIRED.** Three audits state it was never called (`_audit/2026-08-23-linkedin-auth-slice.md:197`, `:351`, `:441`; `_audit/2026-08-23-measure-linkedin.md:69`) and no later file supersedes them. The badge-clearing claim at `server.py:1895` is a docstring assertion; the 34-control census behind it was taken from a captured fixture |
| `linkedin_send_message` | types a name, CHOOSES from the typeahead, then checks who is committed | **FIRED-REFUSED**, newest 2026-09-03 |

`linkedin_surface_census` accepts **11** surface keys and **not one of them is a
network or people surface.** There is no `mynetwork`, `connections`,
`invitations`, `people_search`, `company` or `school` key. Its own docstring
names "the two network-graph gestures" among the things it exists to cost
(`server.py:2394`), and eleven keys later that costing has not been done.

### 3.1 The read boundary is the structural cause of most of this slice

Of the 14 network/people surfaces probed against `readonly._ALLOWED_URL_PATTERNS`,
**10 are ABSENT, 3 are PRESENT, and 1 is an anomaly.**

| surface | verdict |
|---|---|
| `/notifications/` | PRESENT (costs the unread badge on load) |
| `/me/profile-views/` + `/analytics/profile-views/` | PRESENT |
| `/mypreferences/d/` | PRESENT, index only |
| `/in/<member>/` | admitted by pattern `readonly.py:221`, **built by no code path**, and the act is separately in `PERMANENTLY_FORBIDDEN` |
| `/mynetwork/` | ABSENT -- ruled, badge cost |
| `/mynetwork/invitation-manager/` | ABSENT twice -- no pattern, AND `invitation` is a forbidden substring |
| `/mynetwork/invite-connect/connections/` | ABSENT twice -- `/invite` and `/connect` both forbidden |
| `/search/results/people/` | ABSENT -- the only `/search` pattern is `/jobs/search/` |
| `/in/<member>/recent-activity/` | ABSENT |
| `/company/<x>/` and `/company/<x>/people/` | ABSENT |
| `/school/<x>/` | ABSENT -- zero grep hits for `/school/` in the package |
| `/newsletters/` | ABSENT -- zero grep hits for `newsletter` in the package |
| `/feed/hashtag/` | ABSENT -- zero grep hits for `hashtag` in the package |
| `/psettings/` | ABSENT and explicitly forbidden |

**What that means in one sentence: this server can see who viewed him and it can
see the Pages he follows, and that is the whole of its people signal.** It
cannot enumerate his connections, cannot search people, cannot open a company
page, cannot read the people he follows, and cannot open the invitation manager
in either direction.

---

## 4. THE TABLE

R = read, W = write. REV = reversible through ordinary LinkedIn use.
NOT-REV = cannot be undone, or its undo is unestablished.

### A. Sending invitations (8)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 1 | Send an invitation from the suggestion rail on your OWN profile | W | **COVERED-UNFIRED** | `linkedin_send_invitation`. NOT-REV. Acts on `/in/me/`, which drew **9 invitation controls** measured 2026-08-30. Aimed by a needle compared inside the page; two matches refuse rather than shortlist |
| 2 | Send an invitation from a named member's profile | W | EXCLUDED-RULED | R4. NOT-REV |
| 3 | Send an invitation from People You May Know | W | EXCLUDED-RULED | R1. NOT-REV |
| 4 | Send an invitation from a people-search result | W | GAP | NOT-REV. Blocker: no people search exists here at all |
| 5 | Add a personalized note to an invitation | W | GAP | NOT-REV. `linkedin_send_invitation(member, confirm_token)` takes no note parameter. Nothing in the repo discusses notes |
| 6 | Re-invite a member after the previous invitation expired | W | GAP | NOT-REV. Requires knowing an invitation expired -- the Sent surface is ruled out |
| 7 | Invite your connections to follow your employer's Page (30/month) | W | GAP | REV |
| 8 | Invite your connections to follow a Page you do not manage (50/month) | W | GAP | REV |

**Row 1 carries the slice's sharpest scope limit and it is not written down
anywhere else.** `send_invitation` can only invite somebody LinkedIn happens to
have drawn into the 9-control suggestion rail on his own profile. It cannot
invite an arbitrary named person, because reaching one requires a third party's
profile and that is `PERMANENTLY_FORBIDDEN`. The tool's docstring says where it
acts and why; it does not say that this bounds WHO can be invited to whoever
LinkedIn chose to suggest that day.

### B. Managing invitations you sent (4) -- all EXCLUDED-RULED

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 9 | View the invitations you have sent (Sent tab) | R | EXCLUDED-RULED | R2. Named verbatim in `send_invitation`'s own `unverifiable` block as the surface that would confirm a send and cannot be opened |
| 10 | Withdraw a pending invitation you sent | W | EXCLUDED-RULED | R5 + R2. **LinkedIn DOES offer this -- verified against the Help Center, see 8.5.** The server's spec calls it UNMEASURED; that is true of the server and false of the product. **REOPENER, NAMED 2026-09-20: the operator moving `delete_or_withdraw_anything`, which is the whole of what holds this row.** Same shape as `CONTACT-IMPORT`'s row 109, where the reopener is also an operator act and not a measurement. WHO: the operator. **AND THE WORLD-FACT IN THIS CELL REOPENS NOTHING, which is why it is worth saying out loud:** *LinkedIn offers it* is already TRUE and the row is excluded anyway, so a reader who takes the Help Center line as the live half of this write-off has it backwards -- the contingent-looking clause is settled and the settled-looking clause (`R5`, ours) is the one that can move |
| 11 | View the Page-follow invitations you have sent | R | EXCLUDED-RULED | R2 |
| 12 | Withdraw a Page-follow invitation you sent | W | EXCLUDED-RULED | R5 + R2 |

### C. Invitations you received (10)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 13 | View the invitations you have received | R | EXCLUDED-RULED | R1 + R2 |
| 14 | Filter received invitations by type (People, Events, Pages, Newsletters) | R | EXCLUDED-RULED | R1 + R2 |
| 15 | Accept an invitation to connect | W | EXCLUDED-RULED | R8 + R1. REV (you can remove the connection afterwards) |
| 16 | Ignore an invitation to connect | W | EXCLUDED-RULED | R1 + R2 |
| 17 | Report an invitation sender with "I don't know this person" | W | EXCLUDED-RULED | R1. NOT-REV, and it costs the sender an account penalty |
| 18 | Message an invitation sender without accepting | W | EXCLUDED-RULED | R1. Surface owned by the messaging census slice |
| 19 | Read the personal note on a received invitation | R | EXCLUDED-RULED | R1 + R2 |
| 20 | Be notified when a member invites you to connect | R | **COVERED-UNFIRED** | `linkedin_notifications` |
| 21 | Suggest your connections to a member whose invitation you accepted | W | EXCLUDED-RULED | R1 |
| 22 | View Connections You May Know after accepting | R | EXCLUDED-RULED | R1 |

### D. The connections graph (11) -- 10 EXCLUDED-RULED, 1 GAP

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 23 | View your 1st-degree connections list | R | EXCLUDED-RULED | R2. The list lives only at `/mynetwork/invite-connect/connections/`, which trips BOTH `/invite` and `/connect` |
| 24 | Sort your connections (recently added, first name, last name) | R | EXCLUDED-RULED | R2 |
| 25 | Search your connections by name | R | EXCLUDED-RULED | R2 |
| 26 | Filter your connections by location, company, school, industry | R | EXCLUDED-RULED | R2 |
| 27 | Filter your connections by "Talks about" | R | EXCLUDED-RULED | R2 |
| 28 | Filter your connections by "Open to" | R | EXCLUDED-RULED | R2 |
| 29 | Remove a 1st-degree connection | W | EXCLUDED-RULED | R5 + R2. NOT-REV without a fresh invitation |
| 30 | View a connection's own connections | R | EXCLUDED-RULED | R4 + R2 |
| 31 | View shared connections with a member | R | EXCLUDED-RULED | R4 |
| 32 | View your Contacts page | R | EXCLUDED-RULED | R1 |
| 33 | See how many of your connections work at an organization | R | GAP | Blocker: no `/company/` pattern on the allowlist |

**This is the single most consequential block in the census for the operator's
actual job hunt.** The warm-referral workflow he already runs -- see the
`linkedin-jobs` skill -- needs exactly one thing from LinkedIn: who he knows and
where they work. This server cannot supply it, and the skill's own answer is to
read it out of Gmail instead. Rows 23-33 are why that skill exists.

### E. Following and unfollowing people (12) -- 3 EXCLUDED-RULED, 8 GAP, 1 COVERED-UNFIRED

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 34 | Follow a person who is not a connection | W | EXCLUDED-RULED | R4. REV |
| 35 | Unfollow a person from their profile | W | EXCLUDED-RULED | R4. REV |
| 36 | Unfollow a person you ARE connected to, staying connected | W | EXCLUDED-RULED | R4. REV |
| 37 | Unfollow a person directly from a feed post | W | GAP | REV. Blocker: `/feed/update/<urn>/` IS readable and two writes already act there, but the post overflow menu has never been opened -- the same measurement gap `repost_or_share` records |
| 38 | View the list of people you follow | R | EXCLUDED-RULED | Blocker: `/mynetwork/network-manager/people-follow/following/` is not on the allowlist. Its sibling `/mynetwork/network-manager/company/` IS, and is read successfully today. Probed at `_audit/_scratch/slice-guard-probe.md:44` **THE BLOCKER RECORDED HERE NAMES THE WRONG GATE, AND THE RIGHT GATE IS A WRITTEN RULING.** "Not on the allowlist" is allowlist silence, which section 2 of this file says explicitly is NOT a reason. The real refusal is the SECOND, independent gate: the address contains `/follow`, an entry on `readonly._FORBIDDEN_URL_SUBSTRINGS`, checked BEFORE the allowlist -- measured by calling `is_read_url` on it. And `readonly.py` writes the argument against this exact capability: "The PEOPLE he follows live at ``/mynetwork/network-manager/people-follow/following/``, which contains the substring ``/follow`` and is therefore refused ... That is luck, not design -- and the right response to the luck running out is to leave the people list unread, never to shorten the forbidden list." A forbidden-substring entry is this census's own named bar for EXCLUDED-RULED. The sibling `/mynetwork/network-manager/company/` is admitted only because it happens not to carry the substring, which that same passage calls luck. |
| 39 | View the people you previously unfollowed | R | EXCLUDED-RULED | Blocker: `/mypreferences/d/unfollowed` -- **found live and written down**. **EXCLUDED-RULED 2026-09-19 by PROPAGATION, not a new decision.** That is a settings-family page, so **R11** governs it -- *the settings family is admitted by name or not at all* (same ruling as `linkedin_update_setting` and messaging's `MESSAGING-SETTINGS` 3.10). Re-verified at this tree: `is_read_url` False, and `/unfollow` is on `_FORBIDDEN_URL_SUBSTRINGS`, so it is refused at the gate that runs BEFORE the allowlist -- an allowlist addition cannot reach it. Neighbours `N35`/`N36` are already EXCLUDED-RULED. This row's note recorded the ruling's own premise and did not weigh its scope, which is the propagation-failure shape rather than a considered exception. REOPENER, per the ruling: the operator naming this page. NOT applied to `N38`, whose address is a different family and an allowlist miss rather than a denylist block. REV |
| 40 | Re-follow a person you previously unfollowed | W | GAP | REV. Same surface as 39 |
| 41 | Follow a member from one of their articles | W | GAP | REV |
| 42 | Unfollow the articles of a member you are not connected to | W | GAP | REV |
| 43 | Mute a person from a feed post | W | GAP | REV. `mute` has **0 hits** anywhere in `linkedin_server/*.py` |
| 44 | View your own followers | R | COVERED-CANNOT-DELIVER | **BOTH ROUTES ARE CLOSED AND ONE OF THEM WAS MEASURED SHUT.** `linkedin_my_profile` ships a `followers` field and fired live 2026-09-04: "his topcard holds exactly ONE such line and it is connections, so `followers` is null here and that is the page's answer". So a tool exists, it has fired, and the page does not draw the number. The LIST route `/mynetwork/network-manager/people-follow/followers/` is refused by `readonly._FORBIDDEN_URL_SUBSTRINGS` on `/follow`, before the allowlist is consulted -- measured by calling `is_read_url` on it. Filing this GAP would say "no tool and no reason"; there is a tool and there is a measurement. |
| 45 | Be notified when a non-connection follows you | R | **COVERED-UNFIRED** | `linkedin_notifications` |

### F. Following organizations, newsletters, hashtags, groups (21)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 46 | Follow the company attached to a job posting | W | **COVERED-UNFIRED** | `linkedin_follow_company`, from `/jobs/view/{id}/`. REV in LinkedIn, **NOT-REV through this server** -- see 8.2 |
| 47 | Follow an organization's Page from the Page itself | W | GAP | REV. Blocker: no `/company/` pattern. `follow_company`'s own `residue` names the slug-vs-numeric-id gap |
| 48 | Unfollow an organization's Page | W | **COVERED-UNFIRED** | `linkedin_unfollow_company`, by numeric company id off Manage Pages. REV in LinkedIn, NOT-REV here |
| 49 | Follow a skills Page | W | GAP | REV |
| 50 | Follow a company or school via an off-site Follow button | W | EXCLUDED-RULED | REV. Off-platform **RETIRED 2026-09-05, `OFF-PLATFORM-WIDGET` (3.4).** The act is pressing a button embedded on a third party's website, and `server.py:5706-5711` already rules that out: driving a form on somebody else's domain, under their terms, is not this server's to do at any capture quality. Only the ROUTE is retired, not the outcome -- `linkedin_follow_company` holds the same follow and is built. REOPENER: none plausible; a third-party widget drivable without leaving linkedin.com is a contradiction. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 51 | Mute a company | W | GAP | REV. `mute` 0 hits |
| 52 | View the list of Pages you follow | R | **COVERED-PROVEN** | `linkedin_followed_companies`, 2 live readings, PASS |
| 53 | View a Page's follower count | R | GAP | No `/company/` |
| 54 | View how many of your connections follow a Page | R | GAP | No `/company/` |
| 55 | Subscribe to a newsletter | W | GAP | REV. `newsletter` 0 hits |
| 56 | Unsubscribe from a newsletter | W | GAP | REV |
| 57 | View the newsletters you subscribe to | R | COVERED-CANNOT-DELIVER | `linkedin_newsletter_subscriptions` reaches the newsletters surface and returns `distinct` -- A COUNT (`anchors` is the decoy: ten anchors, five newsletters, measured 2026-09-05). Every row leaves through `shape.subscription_row`, which redacts the title UNCONDITIONALLY and publishes a constant href shape, so the answer says a subscription EXISTS and never WHICH. The row asks which. A tool that reports HOW MANY does not cover a row asking WHICH -- banked CANNOT-DELIVER rather than PROVEN for that reason |
| 58 | Unsubscribe from newsletter emails while staying subscribed on the feed | W | GAP | REV |
| 59 | Follow a hashtag | W | GAP | REV. **EXISTENCE UNCERTAIN -- see 9.2.** The recovery pass found a528144 DEAD on eight URL forms and no follow-a-hashtag article of any id across 16 query phrasings, alongside a dated retirement receipt (a5999182, profile hashtags removed Feb/Mar 2024). LinkedIn may have RETIRED the member hashtag-follow surface. **Kept mapped, because that reading is an inference and removing capabilities on an inference is the same undercount this pass exists to fix** |
| 60 | Unfollow a hashtag | W | GAP | REV. Same uncertainty |
| 61 | View your followed hashtags | R | GAP | Same uncertainty |
| 62 | Follow topics from the My Network page | W | EXCLUDED-RULED | R1 |
| 63 | Join a LinkedIn group | W | GAP | REV. **RE-COSTED 2026-09-19: this is DECIDE, not MEASURE, and no measurement moves it.** The joinable surface was measured absent where it could be looked for: the prior wave found NO join control drawn on any suggestion row on `/groups/` -- nothing repeats across the five, and a join affordance would wear one label on all of them and tally 5. So this needs `/groups/<id>/` or `/groups/discover/`, and **both are NAMED REFUSALS in `readonly.py`'s own comment** (`:540-549`), not merely undeclared. **AND A BOUNDARY CHANGE ALONE WOULD NOT BUY IT.** That same comment: *"NO WRITE IS BOUGHT BY THIS. Joining, leaving, posting and inviting all need their own url, their own sanction and their own ruling."* So the real price is THREE things -- an address, a write sanction, and a ruling -- against a ledger that prices `GROUPS-SURFACE` at `allowlist +2, WriteSpec`. Evidence `_audit/_scratch/_progress-groups-surface.md`, `_audit/2026-09-05-groups-surface-measured.md` |
| 64 | Leave a LinkedIn group | W | GAP | REV |
| 65 | View a member's Interests section (what they follow, subscribe to, joined) | R | EXCLUDED-RULED | R4 |
| 66 | Follow an interest from another member's Interests section | W | EXCLUDED-RULED | R4 |

### G. Settings that govern who reaches you (12) -- 11 EXCLUDED-RULED

Every row here lives at `/mypreferences/d/categories/<name>`, forbidden at
`readonly.py:521`. `linkedin_update_setting` exists but is anchored to exactly
one URL, `/mypreferences/d/dark-mode`. **The settings family is admitted by name
or not at all**, and none of these twelve has been named.

| # | capability | R/W | state |
|---|---|---|---|
| 67 | Limit who can follow you to your 1st-degree connections | W | EXCLUDED-RULED (R11) |
| 68 | Allow everyone on LinkedIn to follow you | W | EXCLUDED-RULED (R11) |
| 69 | Make Follow the primary action on your profile | W | EXCLUDED-RULED (R11) |
| 70 | Make Connect the primary action on your profile | W | EXCLUDED-RULED (R11) |
| 71 | Set who can see the members you follow | W | EXCLUDED-RULED (R11) |
| 72 | Choose who can send you invitations to connect | W | EXCLUDED-RULED (R11 + R2) |
| 73 | Turn Page / Event / Newsletter invitations on or off | W | EXCLUDED-RULED (R11 + R2) |
| 74 | Choose whether your connections can see your connections list | W | EXCLUDED-RULED (R11) |
| 75 | Opt out of receiving invitations to follow Pages | W | EXCLUDED-RULED (R11 + R2) |
| 76 | Copy your personal Follow link for use off LinkedIn | R | GAP  **THE WRITE HALF WAS RETIRED AND THIS READ HALF WAS DELIBERATELY PRESERVED.** `N 50` retired 2026-09-05 because the ACT is pressing a button embedded on a third party's website, which `server.py:5706-5711` already rules out -- driving a form on somebody else's domain, under their terms, is not this server's to do at any capture quality. **That ruling explicitly spared the READ**, which is this row: obtaining the link or embed is done ON LinkedIn, on pages already admitted. **So this is a MEASURE, mis-queued as DECIDE-RETIRE** -- there is nothing left to decide, because the decision was made and it came down in this row's favour. NEXT ARTIFACT: a needle pass for the control on an already-admitted address; zero boundary cost.  **MEASURED LIVE 2026-09-19, SAME INSTRUMENT AS `M C72`, SAME BOUNDARY.** `/in/me/`, page control PASS (`Open to` 2, `Add` 2 in main text), nothing pressed. `Contact info` renders (main 1); `More` is in html 3 but not main text; **`Copy link`, `Follow link`, `Share profile` and `Personal link` are all 0 in BOTH main text and html.** The profile draws only **1** `[aria-haspopup]` and **zero** `[role=menu]` / `[role=menuitem]`, so whatever that one trigger opens is built on demand and cannot be read unpressed. **A zero here is a fact about an unpressed page, not about the account** -- stated rather than banked. So this row is blocked on a PRESS, not on a surface or a boundary, and it is the same press ruling as `M C72`, `N 133` and `N 134`. Evidence `_audit/_scratch/_probe-off-platform-controls.txt`; instrument `scripts/_probe_off_platform_controls.py`, shown failing before admission  **RULED 2026-09-19, PERMITTED, AND STILL BLOCKED.** `_audit/2026-09-19-the-disclosing-press-ruling.md` (`a0379d5`) grants the disclosing press under FOUR CONDITIONS THAT MUST ALL HOLD: page already admitted; control matched by an ENUMERATED SHAPE **by ATTRIBUTE**, never by label text; the press SHOWN not to move an outward counter, with **unmeasurable resolving AGAINST the press**; closed and closure verified. Typing is refused outright -- a press is not a fill. **RE-FILED: blocked on the MECHANISM, not on a ruling.** `messaging-measure` is building the shape list, the refusal shown failing and the counter check; nobody presses until it lands. **This row's own 2026-09-19 measurement is evidence FOR that shape list**: the profile draws 1 `[aria-haspopup]` and zero `[role=menu]`/`[role=menuitem]`, so the trigger is attribute-identifiable without reading any label -- which is exactly what condition 2 requires.  **UPDATED 2026-09-19 ON THE SHIPPED GATE.** The press mechanism SHIPPED 2026-09-19 (`linkedin_server/press.py`, `tests/test_press.py`, `9c69ae9`), so this row is **no longer blocked on the mechanism** and the census should not keep saying so -- a deferral that will never resolve consumes a future wave, and these three do not all resolve the same way. Put through `press.evaluate` rather than inferred: **`/in/me/` + `[aria-haspopup]` is PERMITTED.** Pre-press: `permitted_to_attempt: true`, `still_to_show: [counters_unmoved, closure_verified]`; with a counter unmoved at both ends it returns `permitted: true, priced_by: [...]`. **This is the clean case and this row's own measurement is why** -- `/in/me/` draws exactly ONE `[aria-haspopup]` and zero `[role=menu]`/`[role=menuitem]`, so the trigger is attribute-identifiable without reading any label, which is condition 2 exactly. **BLOCKED ONLY ON EXECUTION: a run through `press.disclose` with a counter reader.** `disclose()` takes a shape KEY from a closed tuple, never a selector, and REQUIRES a `read_counters` callable -- there is no path through it that presses unpriced. STILL UNKNOWN AND STATED: whether a counter is readable AT this address; the gate prices a press, it does not supply the counter |
| 77 | Control whether you appear in the connections-who-follow-a-Page list | W | EXCLUDED-RULED (R11) |
| 78 | Manage notifications about your connections' activity | W | EXCLUDED-RULED (R11) |

**OVERLAP WARNING for the top-level tally.** These twelve are network-governing
settings, and `_audit/_census/profile.md` counts a 145-row settings/privacy walk
under the same R11 ruling (its section 6, "the ONE ruling that produces 72 of
the 105 exclusions"). **Rows 67-78 may already be inside that 72.** They are
counted here because the brief names invitation limits, blocking and the
follower/connection distinction; the lead should de-duplicate at the top level
rather than adding the two slices' EXCLUDED totals.

### H. People search and discovery (26) -- 23 GAP, 3 EXCLUDED-RULED

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 79 | Search for a person by keyword or natural-language query | R | GAP | Blocker: no `/search/results/` pattern; the only `/search` pattern is `/jobs/search/` |
| 80 | Narrow search results to People | R | GAP | |
| 81 | Filter a people search by Degree of connections | R | GAP | |
| 82 | Filter by Actively hiring | R | GAP | |
| 83 | Filter by Locations | R | GAP | |
| 84 | Filter by Current company | R | GAP | |
| 85 | Filter by Connections of | R | GAP | |
| 86 | Filter by Followers of | R | GAP | |
| 87 | Filter by Past company | R | GAP | |
| 88 | Filter by School | R | GAP | |
| 89 | Filter by Industry | R | GAP | |
| 90 | Filter by Profile language | R | GAP | |
| 91 | Filter by Open to volunteering | R | GAP | |
| 92 | Filter by Service categories | R | GAP | |
| 93 | Filter by Keywords (first name, last name, title, company, school) | R | GAP | |
| 94 | Add more than one location to a single search | R | GAP | |
| 95 | View and re-run a recent search | R | GAP | |
| 96 | Clear your search history | W | GAP | NOT-REV |
| 97 | Browse People You May Know suggestions | R | EXCLUDED-RULED | R1 |
| 98 | Remove or dismiss a People You May Know suggestion | W | EXCLUDED-RULED | R1. NOT-REV |
| 99 | View the Alumni page for your school | R | GAP | No `/school/` pattern; 0 grep hits for `/school/` |
| 100 | Use a school Page's alumni tab to find and contact alumni | R | GAP | Same |
| 101 | List an organization's employees via its employee count | R | COVERED-CANNOT-DELIVER | No `/company/` **THE RECORDED BLOCKER `No /company/` IS STALE: THIS ROW IS SERVED WITHOUT `/company/`.** `linkedin_job_detail` reads the About-the-company card off the JOB POSTING page at no extra load (`dom.read_company_about_card` -> `shape.company_about_card`), and the posting address is admitted. **SHIPPED CODE NAMES THIS ROW:** `shape._ABOUT_ON_LINKEDIN` is commented "This is the census's ``N 101`` capability, 'list an organisation's employees via its employee count', in its READ half only: it is a COUNT of people and never a list of them." The tool fired live 2026-09-19 on two postings with `company_about` populated. A tool that reports HOW MANY does not cover a row asking WHICH -- banked CANNOT-DELIVER rather than PROVEN for exactly that reason, as `N 57` was. |
| 102 | Read employee insights on a Page's People tab | R | GAP | No `/company/` |
| 103 | View Other Similar Profiles on a member's profile | R | EXCLUDED-RULED | R4 |
| 104 | Find an organization's Page by searching for it | R | GAP | |

**Rows 79-93 are the largest single hole in the slice and the only one that is
pure silence.** Fifteen consecutive rows, all READ, all reversible by
construction, and the repository contains **zero sentences** about any of them:
`search/results/people` returns 0 grep hits, `PYMK` 0, `people you may know` 0.
This is the shape the refusal-census-versus-capability-census distinction was
written for -- you can grep for what a codebase refuses, never for what nobody
considered.

### I. Contact import and sync (6)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 105 | Import contacts from your mobile address book | W | EXCLUDED-RULED | Mobile-only flow; not a page this server can drive **RETIRED 2026-09-05, `CONTACT-IMPORT` (3.2).** LinkedIn documents this as a mobile address-book flow, and a browser driver has no address book to offer -- the same structural refusal as `MOBILE-APP-ONLY`. Verified against this cell; the help article was not re-fetched. REOPENER: a desktop address-book import. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 106 | Import your Gmail contacts | W | EXCLUDED-RULED | OAuth flow **RETIRED 2026-09-05, `CONTACT-IMPORT` (3.2).** A Gmail import is an OAuth consent screen on Google's domain, and `server.py:5706-5711` is a rule about DOMAINS: driving a form on somebody else's domain, under their terms, is not this server's to do at any capture quality. REOPENER: an import completing inside linkedin.com. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 107 | Choose which device contacts to upload instead of all | W | EXCLUDED-RULED | **RETIRED 2026-09-05, `CONTACT-IMPORT` (3.2).** This is a step INSIDE an import, so it has no life independent of one and falls with both routes. REOPENER: either import route reopening. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 108 | Select or deselect the connection recommendations an import produces | W | EXCLUDED-RULED | **RETIRED 2026-09-05, `CONTACT-IMPORT` (3.2).** This is a step INSIDE an import, so it has no life independent of one and falls with both routes. REOPENER: either import route reopening. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 109 | Send connection requests to the imported contacts you selected | W | EXCLUDED-RULED | **NOT-REV, and it is the highest-blast-radius row in the census** -- one confirmation sends many invitations **RETIRED 2026-09-05, `CONTACT-IMPORT` (3.2).** Sending connection requests to a selected batch is a loop write, and `writes.PERMANENTLY_FORBIDDEN['any_loop_sweep_or_scheduled_write']` already forbids it -- this row needs no new reason, only the existing one applied. REOPENER: only the operator moving that prohibition. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 110 | Delete all imported contacts | W | EXCLUDED-RULED | R5. NOT-REV |

### J. Endorsements (8)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 111 | Endorse a 1st-degree connection for a skill | W | EXCLUDED-RULED | R3, and it is a MEASURED refusal -- see 6.3 |
| 112 | Endorse a connection for several skills at once | W | EXCLUDED-RULED | R3 |
| 113 | Remove an endorsement you have given | W | EXCLUDED-RULED | R3 + R5 |
| 114 | Hide or show an endorsement you received from a particular member | W | GAP | REV. **Lives on HIS OWN skills page, which IS readable** (`/in/me/details/skills/`). R3 governs endorsing others, not managing what he received. Nothing written covers the receiving side |
| 115 | Opt out of receiving endorsements entirely | W | EXCLUDED-RULED | R11 |
| 116 | Manage endorsement settings | W | EXCLUDED-RULED | R11 |
| 117 | Manage skill-endorsement notifications | W | EXCLUDED-RULED | R11 |
| 118 | Read the endorsement counts on your own skills | R | MEASURED-ABSENT | **LinkedIn DRAWS NO ENDORSEMENT LINE ON THIS PAGE. Measured live 2026-09-04**, `scripts/_probe_endorse_and_follow_lines.py`: `/in/me/details/skills/` returned 20 skill cards and 2,359 characters of `main`, with **ZERO** occurrences of `endors` anywhere on it -- cards or body. The page DREW, so a stale capture is ruled out; the committed fixture agrees with live LinkedIn. This was NEVER a missing parser. Two worlds fit the evidence and nothing on his own account separates them -- LinkedIn draws the line only for a skill someone endorsed, or it stopped drawing it -- so `dom.read_profile_detail_entries` now RE-TAKES this reading on every call and returns it with the denominator it was taken over, rather than hard-coding an answer that would go on denying a count on the day one appears. Costed at zero extra page loads by `_audit/2026-08-22-parity-linkedin.md:18` and refuted the next day by `_audit/2026-08-23-build-linkedin.md:229`, whose correction this row failed to carry for twelve days. **REOPENER, NAMED 2026-09-20 -- AND IT WAS ALREADY BUILT, WHICH IS THE POINT.** The trigger is `dom.read_profile_detail_entries` returning a non-zero `endorsements` count with a non-zero denominator, on any call. That re-take is described two sentences up and has been shipping since 2026-09-04; what it lacked was the word REOPENER, so no instrument sweeping this census for re-check triggers could see it and this row read as a permanent closure. **A trigger that exists in code and is not named in the cell is invisible to every reader who starts from the census**, which is the whole defect `_audit/2026-09-20-the-reopener-triggers.md` was sent to fix -- and this row is its cheapest instance: zero new code, one clause. WHO: that reader, on every call. **The two worlds in this cell stay unseparated and that is honest** -- a count appearing does not say which of them was true, only that the absence has ended |

### K. Recommendations (10) -- all EXCLUDED-RULED under R3

| # | capability | R/W | state |
|---|---|---|---|
| 119 | Request a recommendation from a 1st-degree connection | W | EXCLUDED-RULED (R3) |
| 120 | Write and send a recommendation for a 1st-degree connection | W | EXCLUDED-RULED (R3) |
| 121 | Accept a received recommendation onto your profile | W | EXCLUDED-RULED (R3) |
| 122 | Dismiss a recommendation you received | W | EXCLUDED-RULED (R3) |
| 123 | Ask for a revision of a recommendation you received | W | EXCLUDED-RULED (R3) |
| 124 | Revise a recommendation you have given | W | EXCLUDED-RULED (R3) |
| 125 | Delete a recommendation you have sent | W (also R5) | EXCLUDED-RULED (R3) |
| 126 | Hide or unhide a recommendation you received | W | EXCLUDED-RULED (R3) |
| 127 | Set the visibility of a recommendation you have given | W | EXCLUDED-RULED (R3) |
| 128 | Decline a recommendation request someone sent you | W | EXCLUDED-RULED (R3) |

**The state column was added 2026-09-05 and carries no new judgement.** This table
shipped with no state column at all, so its ten rows were in no counter's numerator
or denominator in either direction. The value transcribed into every cell is the
one this section's own heading states -- *all EXCLUDED-RULED under R3* -- and the
precision flag immediately below is unchanged and still governs.

**A precision flag on all ten.** The ruling's key is `endorse_or_recommend` and
so it NAMES recommendations. But the measurement behind it counted **endorse
controls only** -- "zero endorse controls across 13 tracked fixtures ... zero
among the 222 controls read live on his own profile on 2026-08-30". No
recommendation control has ever been counted, on any surface, in either
direction. The ruling's reasoning (you cannot endorse yourself, so the only
carrier is a third party's profile) transfers cleanly to GIVING a
recommendation. **It does not transfer to rows 121, 122, 123, 126 and 128**,
which are all things done to recommendations he RECEIVED, on his own profile. To
the letter of the four states those five are EXCLUDED-RULED, because the key
names them. To the evidence, they are unmeasured. Recorded here rather than
silently downgraded.

### L. Who viewed your profile (12)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 129 | See your profile viewers -- name, headline, when, profile link | R | **COVERED-PROVEN** | `linkedin_who_viewed_me`. Reaches 365 days back on his Premium Career account |
| 130 | See anonymous viewers exactly as LinkedIn renders them | R | **COVERED-PROVEN** | Returned with `"anonymous": true`; harvested via `sibling_rows=True` because a link-anchored harvest cannot see them at all |
| 131 | Learn the identity behind an anonymous viewer | R | EXCLUDED-RULED | R6 |
| 132 | Switch between Search appearances and Who viewed your profile | R | GAP | **READ LIVE 2026-09-05, STILL GAP FOR THE SWITCH.** (That sentence stood in the state cell from 2026-09-05 until this row was made countable again; the row is unchanged, only visible.) **STILL A GAP, AND THE BLOCKER CHANGED 2026-09-05.** "Search appearances are never read" was true for a fortnight and is no longer the reason. The address `/analytics/search-appearances/` is now on the read allowlist as one anchored pattern, `dom.read_search_appearances` exists, and `linkedin_surface_census` answers to the key `search_appearances`. **What is missing is the LIVE READ** -- nobody in this repository has opened this page, the reader is proven only against a fixture that says SYNTHETIC in its first line, and no tool returns an appearance count. **THE PAGE HAS NOW BEEN MET** -- read twice on 2026-09-05, 108 appearances both times, `_audit/2026-09-05-search-appearances-load-a.md`. This row stays GAP anyway and the reason is narrow: it is about SWITCHING between the two analytics views, and each is reached by its own address here rather than by pressing a control. Nothing in this package presses that switch, and nothing needs to |
| 133 | Filter your profile-viewer data (Premium) | R | GAP | **The page is already open** -- see 8.1. **CONTROLS MEASURED PRESENT, UNPRESSED, 2026-09-05 17:18** on `/analytics/profile-views/`, an address `linkedin_who_viewed_me` already loads: `Company`, `All filters`, `Past 90 days`, `Most recent`, `Most relevant`, `Reset`, `Submit` are all RENDERED. **They are FILTER controls, not disclosures**, so the panel is not hidden behind anything -- the data is simply unfiltered until one is used. **STAYS GAP AND NEEDS A RULING, NOT A MEASUREMENT: using a filter means PRESSING a control on his live analytics page**, which is the standing open question this repository files under `MATCH-DETAILS-COLLAPSED` -- *pressing a disclosure control is a different permission from reading a render*. Nothing here fires at a person and nothing leaves his own account, so it is a ruling the lead can make on his behalf. Evidence `_audit/_scratch/_progress-analytics-creator.md` s11 (a self-correction: that wave's s1 had reported the page carries no such controls and s11 measured that FALSE), capture `_audit/_scratch/_live-analytics-controls-4.txt`  **RULED 2026-09-19, PERMITTED, AND STILL BLOCKED -- the distinction is the point.** `_audit/2026-09-19-the-disclosing-press-ruling.md` (`a0379d5`) grants the disclosing press this row was waiting on, under FOUR CONDITIONS THAT MUST ALL HOLD: (1) the page is ALREADY ADMITTED -- a press never extends reach; (2) the control matches an ENUMERATED DISCLOSURE SHAPE **by ATTRIBUTE** (`[aria-expanded]`, `[aria-haspopup]`), never by label text; (3) the press is SHOWN not to move an outward counter, on the `read_invitation_badge` discipline, and **where no counter can price a press, unmeasurable resolves AGAINST the press**; (4) it is closed and the closure VERIFIED. Refused regardless: navigation, submission, composers, any third-party surface, and **typing -- a press is not a fill**. **SO THIS ROW IS NOW BLOCKED ON THE MECHANISM, NOT ON A RULING**, and that re-filing is deliberate: `messaging-measure` owns the boundary and is building the enumerated shape list, the refusal shown failing, and the counter check. **Nobody presses until it lands** -- a ruling is not permission to act ahead of the guard that bounds it, which is how a narrow ruling becomes a wide practice.  **UPDATED 2026-09-19 ON THE SHIPPED GATE.** The press mechanism SHIPPED 2026-09-19 (`linkedin_server/press.py`, `tests/test_press.py`, `9c69ae9`), so this row is **no longer blocked on the mechanism** and the census should not keep saying so -- a deferral that will never resolve consumes a future wave, and these three do not all resolve the same way. Put through `press.evaluate` rather than inferred: **`/analytics/profile-views/` + `[aria-expanded]` passes address and shape**; the remaining conditions are `counters_unmoved` and `closure_verified`, neither of which can be evaluated without a run. **BLOCKED ON EXECUTION AND ON WHETHER A COUNTER EXISTS AT THIS ADDRESS** -- not on the mechanism and not on a ruling. The controls themselves were measured present and unpressed on 2026-09-05, so condition 2 has its evidence already  **FIRST SANCTIONED PRESS TAKEN 2026-09-19 ~11:32, AND THIS ROW IS STILL GAP.** `press.disclose` PERMITTED the press on `/analytics/profile-views/` with shape `[aria-expanded]`: condition 1 admitted (checked before any load), condition 2 an enumerated shape KEY, condition 3 **priced by TWO counters** (`invitations` 0, `notifications_unread` 6, neither moved across the press), condition 4 closure verified and the page identical on every measured field before and after. Verdict verbatim: `{"permitted": true, "pressed": true, "priced_by": ["invitations", "notifications_unread"], "shape": "[aria-expanded]"}`. **BUT A PERMITTED PRESS IS NOT A COVERED CAPABILITY.** `aria-expanded` read the same value at both ends and the page carried `expanded_true=0` before AND after, which fits two readings equally: the panel opened and Escape closed it, or **the press did nothing at all**. Nothing in the run distinguishes them -- condition 4 verifies the page was left as found, never that anything happened in between. **No content was read, so nothing is banked.** NEXT ARTIFACT, and it is a READER not another press: a DISCLOSURE WITNESS that fails if the panel did not open (a region that exists only while expanded, or `aria-expanded="true"` observed WHILE held open, before Escape), plus a name-free shaper for what the panel draws. **The witness is the harder half and worth building first: without it, a permitted press cannot be told from a press that missed.** Full evidence: `_audit/2026-09-19-the-first-sanctioned-press.md` |
| 134 | See notable or interesting viewers (Premium) | R | GAP | Same. **THE PANEL EXISTS AND ITS CONTROL IS RENDERED UNPRESSED** -- `Interesting viewers` counted twice on the unpressed page, 2026-09-05 17:18, and `Show more analytics` is drawn under exactly the name the blocker predicted. **So a reader needs no press to know the panel is there; whether its CONTENTS render unpressed is NOT established**, and that distinction is the whole row. Same ruling as `N 133` and no further measurement will settle it without one. Evidence `_audit/_scratch/_progress-analytics-creator.md` s11 (a self-correction: that wave's s1 had reported the page carries no such controls and s11 measured that FALSE), capture `_audit/_scratch/_live-analytics-controls-4.txt`  **RULED 2026-09-19, PERMITTED, AND STILL BLOCKED -- the distinction is the point.** `_audit/2026-09-19-the-disclosing-press-ruling.md` (`a0379d5`) grants the disclosing press this row was waiting on, under FOUR CONDITIONS THAT MUST ALL HOLD: (1) the page is ALREADY ADMITTED -- a press never extends reach; (2) the control matches an ENUMERATED DISCLOSURE SHAPE **by ATTRIBUTE** (`[aria-expanded]`, `[aria-haspopup]`), never by label text; (3) the press is SHOWN not to move an outward counter, on the `read_invitation_badge` discipline, and **where no counter can price a press, unmeasurable resolves AGAINST the press**; (4) it is closed and the closure VERIFIED. Refused regardless: navigation, submission, composers, any third-party surface, and **typing -- a press is not a fill**. **SO THIS ROW IS NOW BLOCKED ON THE MECHANISM, NOT ON A RULING**, and that re-filing is deliberate: `messaging-measure` owns the boundary and is building the enumerated shape list, the refusal shown failing, and the counter check. **Nobody presses until it lands** -- a ruling is not permission to act ahead of the guard that bounds it, which is how a narrow ruling becomes a wide practice.  **UPDATED 2026-09-19 ON THE SHIPPED GATE.** The press mechanism SHIPPED 2026-09-19 (`linkedin_server/press.py`, `tests/test_press.py`, `9c69ae9`), so this row is **no longer blocked on the mechanism** and the census should not keep saying so -- a deferral that will never resolve consumes a future wave, and these three do not all resolve the same way. Put through `press.evaluate` rather than inferred: **`/analytics/profile-views/` + `[aria-expanded]` passes address and shape**; the remaining conditions are `counters_unmoved` and `closure_verified`, neither of which can be evaluated without a run. **BLOCKED ON EXECUTION AND ON WHETHER A COUNTER EXISTS AT THIS ADDRESS** -- not on the mechanism and not on a ruling. The controls themselves were measured present and unpressed on 2026-09-05, so condition 2 has its evidence already  **FIRST SANCTIONED PRESS TAKEN 2026-09-19 ~11:32, AND THIS ROW IS STILL GAP.** `press.disclose` PERMITTED the press on `/analytics/profile-views/` with shape `[aria-expanded]`: condition 1 admitted (checked before any load), condition 2 an enumerated shape KEY, condition 3 **priced by TWO counters** (`invitations` 0, `notifications_unread` 6, neither moved across the press), condition 4 closure verified and the page identical on every measured field before and after. Verdict verbatim: `{"permitted": true, "pressed": true, "priced_by": ["invitations", "notifications_unread"], "shape": "[aria-expanded]"}`. **BUT A PERMITTED PRESS IS NOT A COVERED CAPABILITY.** `aria-expanded` read the same value at both ends and the page carried `expanded_true=0` before AND after, which fits two readings equally: the panel opened and Escape closed it, or **the press did nothing at all**. Nothing in the run distinguishes them -- condition 4 verifies the page was left as found, never that anything happened in between. **No content was read, so nothing is banked.** NEXT ARTIFACT, and it is a READER not another press: a DISCLOSURE WITNESS that fails if the panel did not open (a region that exists only while expanded, or `aria-expanded="true"` observed WHILE held open, before Escape), plus a name-free shaper for what the panel draws. **The witness is the harder half and worth building first: without it, a permitted press cannot be told from a press that missed.** Full evidence: `_audit/2026-09-19-the-first-sanctioned-press.md` |
| 135 | See the weekly viewer trend graph (Premium) | R | COVERED-PROVEN | Same  **BANKED 2026-09-19. BUILT AFTER THE CENSUS FROZE AND THE ROW WAS NEVER MOVED.** Verified END TO END from the tree: `linkedin_who_viewed_me` (`server.py:1268`) sets `extra["insights"] = await dom.read_profile_views_insights(...)` at `:1383`, passes `extra=extra` to `shape.envelope` at `:1394`, and that builder does `out.update(extra)` before `return out` (`shape.py`). The reader emits **`trend`** among its fields. **So the weekly trend chart reaches a caller today.** **COVERED-UNFIRED, not PROVEN:** surfaced, with no recorded run asserting a value live. **NOTE THE NEIGHBOUR THIS CORRECTS:** `N 136` was measured MEASURED-ABSENT (no top-locations panel is drawn) and `N 133`/`N 134` are blocked on a press. This row is neither -- it was simply already built, which is why a blocker cannot be judged by its family.  **PROMOTED TO COVERED-PROVEN 2026-09-20 BY A LIVE RUN, wave `live-capture`.** `linkedin_who_viewed_me` returned `insights.trend.present` true and a `trend.description` of 31 chars matching the shape `<word> chart with <N> data points.`, alongside a 2-digit headline, a 3-char delta and 5 filters. **THE PRESENCE IS SOUND EVEN THOUGH ABSENCES ON THIS PAGE ARE NOT:** the same call measured `main_present` true, `main_chars` 1835 and **0 viewer rows in scope while the outer reader parsed 12 on the same load** -- the scope defect filed in `_audit/2026-09-20-the-premium-block.md` section 5, now confirmed live rather than inferred. A presence found inside a wrong scope is still a presence. See `_audit/2026-09-20-the-live-capture.md` sections 3a and 5. |
| 136 | See top locations, industries and companies of your viewers (Premium) | R | MEASURED-ABSENT | **NO SUCH PANEL IS DRAWN, and two independent sources agree.** (1) `_audit/2026-09-03-linkedin-gap-blockers.md` s6 already corrected the census on exactly this row: *the census names "top companies and top locations"; the live page carries a Company FILTER and no such panel.* (2) An unpressed shape tally of `/analytics/profile-views/` on 2026-09-05 17:18 enumerated every control on the page and **no control names locations, industries or companies as a breakdown** -- the only match is `Company`, which is a filter. **WHAT I DID SEE, because a refusal that reports only what it missed is half a measurement:** `Show more analytics` 1, `Interesting viewers` 2, `Company` 2, `Past 90 days` 2, `All filters` 1, `Most recent / Most relevant / Reset / Submit` 1, `View all recruiters` 1. The instrument that took it was the same one whose author then corrected himself about this page, so it is a measurement that survived its own operator arguing against it. REOPENER: a breakdown panel drawn under any name on that page. Evidence `_audit/_scratch/_progress-analytics-creator.md` s11 (a self-correction: that wave's s1 had reported the page carries no such controls and s11 measured that FALSE), capture `_audit/_scratch/_live-analytics-controls-4.txt` |
| 137 | Set your profile viewing option to "Your name and headline" | W | EXCLUDED-RULED | R11 |
| 138 | Set your profile viewing option to private characteristics | W | EXCLUDED-RULED | R11 |
| 139 | Set your profile viewing option to private mode | W | EXCLUDED-RULED | R11. **Going anonymous costs him rows 129-130** -- LinkedIn withdraws your own viewer list while you browse privately |
| 140 | Unsubscribe from Who's-viewed-your-profile emails | W | EXCLUDED-RULED | R11 |

### M. Blocking, reporting, muting (14)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 141 | Block a member | W | EXCLUDED-RULED | R4 -- initiated from the member's profile. **NOT-REV, and LinkedIn says so outright** -- see 8.6. Blocking destroys the connection and removes that member's endorsements and recommendations, and unblocking reinstates none of them |
| 142 | Unblock a member | W | EXCLUDED-RULED | R11 -- the blocked list is a settings page. Rate-limited: 48 hours before you may re-block, and documented as possibly UNAVAILABLE past 2000 blocks |
| 143 | See the list of members you have blocked | R | EXCLUDED-RULED | R11 |
| 144 | Report a member's profile | W | EXCLUDED-RULED | R4. NOT-REV |
| 145 | Report a fake or impersonating profile | W | EXCLUDED-RULED | R4. NOT-REV |
| 146 | Report inaccurate information on another member's profile | W | EXCLUDED-RULED | R4. NOT-REV |
| 147 | Report a profile video | W | EXCLUDED-RULED | R4. NOT-REV |
| 148 | Report a post or a comment in your feed | W | GAP | NOT-REV. Blocker: the feed-item permalink is readable; its overflow menu has never been opened |
| 149 | Report a message | W | GAP | NOT-REV. TWIN CONFIRMED: `M M38` "Report a message as spam", GAP, filed under `REPORTING-FLOWS`. The queued RE-FILE's premise -- that the messaging slice counts this too -- holds for this row. |
| 150 | Report a whole conversation thread | W | GAP | NOT-REV. NO TWIN, ANYWHERE. Measured under 34 needle spellings over `messaging-and-content.md`, `jobs.md`, `profile.md` and `mcp-inventory.md`: zero. The strings "whole conversation thread" and "system-flagged" occur nowhere in this repository outside the audit tree. THE QUEUED RE-FILE MUST NOT BE EXECUTED ON THIS ROW -- its premise that the messaging slice counts it too is measured untrue, so subtracting it here removes a capability no slice holds. This row is the network slice's until some slice claims it. |
| 151 | Mark a system-flagged message as safe instead of reporting it | W | GAP | NO TWIN, ANYWHERE -- same 34-spelling sweep over all four slices and the tool inventory as row 150. THE QUEUED RE-FILE MUST NOT BE EXECUTED ON THIS ROW. Note the direction: this is the capability to CLEAR a flag, the only row in section M whose act is to undo a report rather than to make one, which is why no reporting-flow twin covers it. |
| 152 | Report harassment or a safety concern | W | EXCLUDED-RULED | NOT-REV. A Help Center form, off the product surface **RETIRED 2026-09-05, `HELP-CENTER-FORM` (3.3).** A harassment or safety report is an accusation with a consequence for the person named, carried by a free-text narrative only he can write, filed to a human review queue off the product surface. REOPENER: an in-product STRUCTURED report -- and even then the narrative stays his. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 153 | Hide a network update from your feed | W | GAP | REV |
| 154 | Hide a single post from your feed without unfollowing its author | W | GAP | REV |

**Zero of the fourteen is covered, and no ruling in the repo is ABOUT safety.**
Every EXCLUDED-RULED here inherits from R4 (third-party profiles) or R11
(settings) -- rulings written for other reasons that happen to contain these
addresses. Nobody has written a sentence about whether this server should be
able to block or report anyone. Given that the asset at risk is the operator's
professional identity, that is the most notable silence in the census after
people search.

### N. Reaching a person directly (6)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 155 | Message a 1st-degree connection | W | **COVERED-CANNOT-DELIVER** | `linkedin_send_message`. NOT-REV. Fired live and REFUSED, twice. The only row in the slice in this state; see 2 and 8.3 |
| 156 | Send an InMail to a member outside your network | W | EXCLUDED-RULED | R9 -- four written rulings. NOT-REV |
| 157 | View your available InMail credits | R | MEASURED-ABSENT | **STATE CORRECTED 2026-09-20, EXCLUDED-RULED -> MEASURED-ABSENT, AND THE PRIOR TEXT IS KEPT BELOW UNCHANGED.** `_audit/2026-09-20-the-first-firing.md` s4d named this exact defect and declined to fix it -- *"they still differ in STATE WORD, and that is a real defect I am naming rather than quietly fixing ... the owner of the state vocabulary can rule it in one line"* -- because two rows had been committed four hours earlier and the question was bigger than that wave. This is that one line. **THE GROUND IS A CONTRADICTION INSIDE THE CENSUS, NOT A PREFERENCE:** `J 127`, `M M4` and this row assert ONE fact about ONE object -- the InMail credit balance is not rendered -- and `J 127` is MEASURED-ABSENT while these two read EXCLUDED-RULED. `9a140a3`, whose entire purpose was the kind distinction, files the twin `M 4` as **WORLD-FACT** and not US-RULING. **A measurement is not a ruling.** EXCLUDED-RULED means somebody decided not to build this; the cell below decides nothing -- it reports that a page was read and a number was not on it, which is exactly section 2's definition of MEASURED-ABSENT: *no tool, and a LIVE READING of the surface says LinkedIn does not draw the thing.* **AND R9 NEVER COVERED IT:** R9 is outreach AUTOMATION and this row is a READ. **REOPENER, NAMED, and deliberately the SAME one `J 127` carries so the three rows agree on trigger as well as on substance: a capture of a Premium surface not among the 25 -- the subscription and manage pages are the untested candidates -- drawing a digit beside an InMail or credit word.** WHO: a capture. **PRIOR TEXT, KEPT:** R9. The `premium` census key was added 2026-09-01 to ask exactly this and settled that the balance is not on the composer |
| 158 | Send an Open Profile message without spending an InMail | W | EXCLUDED-RULED | R9. NOT-REV |
| 159 | Enable or disable Open Profile on your own profile | W | EXCLUDED-RULED | R11. REV |
| 160 | Send, receive and manage message requests | W | GAP | TWINS CONFIRMED: `M M6` send, `M M7` accept, `M M8` decline, all GAP, all filed under `MESSAGE-REQUESTS-SURFACE`. The queued RE-FILE's premise holds for this row. Note the twins carry a DIFFERENT blocker from this row, so a re-file is an accounting act across two blockers, not a move within one. |

### P. LinkedIn Groups as a people surface (18) -- ALL GAP, recovered second pass

**The Groups help tree was never walked in the first pass and is not an empty
area.** `/groups/` returns **0 grep hits** across `linkedin_server/*.py`; so does
`linkedin.com/groups`. No tool, no ruling, no sentence -- the same pure silence
as people search.

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 161 | Search for groups by name or keyword | R | GAP | **NEEDS A RULING, NOT A MEASUREMENT -- and the refusal is already written down.** `/search/results/groups/` is a NAMED REFUSAL in `readonly.py`'s own groups comment (`:547-549`), which says in terms why it was not inherited there: *"belongs to SEARCH-RESULTS-SURFACE, which is queued DECIDE and is not this entry's to inherit."* So the boundary question was deliberately left to this blocker rather than settled sideways by a neighbouring one. No further measurement moves this row; what it needs is the DECIDE its own queue column already names. |
| 162 | Browse groups recommended from attributes you share with their members | R | COVERED-CANNOT-DELIVER | **THE SURFACE IS READ AND THE COUNT IS PUBLISHED; WHICH GROUPS IS STRUCTURALLY WITHHELD -- a SHAPER limit, not a missing build.** `server.py::linkedin_group_memberships` opens the admitted `/groups/` root and splits it STRUCTURALLY, publishing the suggestion side as `others` beside `memberships` with an `overlap` disjointness proof. **FIRED LIVE THROUGH THE REGISTRY 2026-09-05 22:08, and the payload carries THIS row's answer, not only row 173's:** `OTHERS rows 6, groups 5, DISTINCT 5, refused {root: 1}` with `in common 0, DISJOINT True` -- `_audit/2026-09-05-groups-wire.md`, quoted BY ITS TEXT rather than by line: the `REGISTRY: 42 tools` line two above it records that run's count, and the registry answers 44 at HEAD (measured 2026-09-19 13:33), so a line reference into that block ages and the payload string does not. **THE SECTION IDENTITY IS NOT THE TOOL'S OWN READING** -- it reads no heading by design -- it is `scripts/_probe_membership_sections.py`, the heading-boundary instrument, which resolved the suggestions disjoint from the memberships at 5 (`_audit/2026-09-05-groups-surface-measured.md:49`). **WHAT THIS ROW ASKS TO BROWSE IS EXACTLY WHAT THE SHAPER REFUSES TO SAY:** `groups.membership_tally` takes no name as a parameter of any function it calls and refuses a non-numeric path segment BECAUSE A SLUG IS A NAME, so the tool reports HOW MANY groups are recommended and can never report WHICH. **RULED BY THE STATE ITS OWN TWIN ALREADY CARRIES.** Row 180 *See events recommended from your interests* is the same shape one surface along -- an admitted root, a recommendation section made of OTHER PEOPLE'S things, published as a count -- and was moved to `COVERED-CANNOT-DELIVER` on 2026-09-19 on exactly that reasoning: *the BOUNDARY decided this page may be OPENED; the SHAPER decided what may be SAID*. That pass found 180 by cross-referencing the registered tools against GAP rows BY HAND and **did not reach this row, 18 lines above it in this same table** -- which is why this cell cites the twin rather than re-deriving the rule. REOPENER, identical to 180's: a ruling that recommendation-section contents may be published. |
| 163 | Request to join a group | W | GAP | REV (row 64 leaves). **RE-COSTED 2026-09-19: this is DECIDE, not MEASURE, and no measurement moves it.** The joinable surface was measured absent where it could be looked for: the prior wave found NO join control drawn on any suggestion row on `/groups/` -- nothing repeats across the five, and a join affordance would wear one label on all of them and tally 5. So this needs `/groups/<id>/` or `/groups/discover/`, and **both are NAMED REFUSALS in `readonly.py`'s own comment** (`:540-549`), not merely undeclared. **AND A BOUNDARY CHANGE ALONE WOULD NOT BUY IT.** That same comment: *"NO WRITE IS BOUGHT BY THIS. Joining, leaving, posting and inviting all need their own url, their own sanction and their own ruling."* So the real price is THREE things -- an address, a write sanction, and a ruling -- against a ledger that prices `GROUPS-SURFACE` at `allowlist +2, WriteSpec`. Evidence `_audit/_scratch/_progress-groups-surface.md`, `_audit/2026-09-05-groups-surface-measured.md` |
| 164 | Join a group by responding to an invitation from a member or manager | W | GAP | REV |
| 165 | View the full member list of a group you belong to | R | EXCLUDED-RULED | **The one member-directory read on LinkedIn this server could plausibly reach without a third-party profile load** -- and it is REFUSED BY A RULING ALREADY MADE, not by a missing surface. **RE-FILED 2026-09-19; NOT a new decision.** `readonly.py:540-544` records it verbatim as `/groups/<id>/members/`: *"THE MEMBER ROSTER. Census row N 165, and the row the team lead put out of scope by name. It is a list of people who did not choose to be enumerated by him, and which url serves it changes nothing about that."* Corroborated at `_audit/2026-09-05-groups-surface-measured.md:241`. **The reason is the durable part: the objection is to ENUMERATING PEOPLE, so it survives any change of address** -- which is why no allowlist entry can reach it and why finding a different url for the same roster would not reopen it. REOPENER: the operator ruling otherwise, which is his to make and nobody else's |
| 166 | Send a connection invitation to a fellow group member from inside the group | W | GAP | NOT-REV. An invitation route that does NOT require opening the person's profile |
| 167 | Send a message request to a group member you are not connected to | W | GAP | NOT-REV |
| 168 | Invite your connections to join a group you are merely a member of | W | EXCLUDED-RULED | REV for the invitee. **EXCLUDED-RULED 2026-09-19 under this slice's OWN `R2`** -- `invitation`, `/invite`, `/connect`, `/withdraw` are forbidden substrings, re-verified at this tree. Twin `M C69` *Invite connections to join a group* is the same capability and was flipped under R2 earlier today. **I CREATED THIS SPLIT and am closing it**: flipping the messaging row left its network twin GAP, which is precisely the propagation failure this round has been documenting. `messaging-and-content.md` s10 flags C69 as belonging to this slice, and N168 is the row it belongs to. REOPENER, per R2's own form: the operator narrowing that substring. |
| 169 | Filter the connections you invite by location, company, school and industry | W | GAP | **A filtered read over his own connections** -- the capability rows 23-28 are ruled out of |
| 170 | Allow or prevent other group members from messaging you | W | EXCLUDED-RULED | **EXCLUDED-RULED 2026-09-19 by PROPAGATION.** Twin `M M42` *Settings to allow or prevent messages from group members* is the same capability and has been EXCLUDED-RULED since 2026-09-05 under `MESSAGING-SETTINGS` (3.10) -- whose own note says it was *NOT a new decision: the operator already made it and two census slices applied it differently*, and then left THIS row GAP for two weeks. **`MESSAGING-SETTINGS` and this slice's own `R11` are the SAME shipped ruling under two names** -- `linkedin_update_setting` states it as *a setting is admitted by name or not at all*, and R11 states it as *the settings family is admitted by name or not at all*. REOPENER, per the ruling itself: the operator naming this page. REV |
| 171 | Expose your profile to every member of a group you join | R | GAP | A cost of joining, not an action |
| 172 | View a fellow group member's connections only after connecting with them | R | GAP | |
| 173 | Access the list of groups you belong to | R | COVERED-PROVEN | **SHIPPED AND FIRED LIVE 2026-09-05; the row was never moved.** Same capability as `M C60` and served by the same tool, `linkedin_group_memberships` (`server.py:1894`). Re-verified independently 2026-09-19 by reading the tree: 30 tests pass in `tests/test_the_groups_tool_keeps_its_properties.py`, tool registered per `tests/test_every_tool_is_on_the_surface.py`. Returns **counts and numeric ids, never a name** -- structurally, since `groups.membership_tally` accepts no name anywhere and refuses a non-numeric path segment because a slug is a name. **The reading that matters is `memberships.distinct`, NOT `anchors`:** the Groups page draws memberships and LinkedIn's suggestions with the same kind of anchor, so a flat sweep answers TEN to a question whose answer is FIVE -- in the flattering direction, while looking correct. The tool splits the page structurally (nearest anchor-bearing ancestor holding exactly one group anchor) and carries `agrees_with_corroborated` in its payload so a caller can see whether a reading joins the four corroborating instruments or is that known defect arriving again |
| 174 | View the groups you have requested to join | R | GAP | **MEASURED AND DELIBERATELY NOT CLOSED -- A ZERO CANNOT SETTLE THIS ROW.** The `/groups/` root was read live and draws exactly two sections, neither of them a pending-requests list. **That reading is consistent with two different worlds and cannot separate them:** he may have zero pending requests, and a section that is absent when empty reads identically to one that does not exist. **A reading no instrument can fail is not a reading**, so the row stays GAP rather than being retired on a comfortable zero. NEXT ARTIFACT: a pending request would have to exist for the surface to be observable at all -- and creating one is a WRITE at a real group, so this is unmeasurable by any read on this account's current state. Evidence `_audit/_scratch/_progress-groups-surface.md` item 4 |
| 175 | Reach a private unlisted group through a direct link or an invitation | R | GAP | |
| 176 | Prevent your network being updated when you join a group | W | GAP | REV |
| 177 | Find people you know through shared group membership | R | GAP | |
| 178 | See which groups a member belongs to before connecting | R | GAP | Overlaps row 65's surface but is its own read |

**Rows 165, 166 and 169 are the finding in this block.** They are a people
directory, an invitation route and a connection filter that all live on
`/groups/` -- an address family carrying NO badge, NO third-party profile load,
and NO forbidden substring. Every reason rows 23-33 and 34-36 are ruled out
fails to apply here. Nobody has looked.

### Q. LinkedIn Events as a people surface (15) -- ALL GAP, recovered second pass

**The Events topic page `topic/a150003` returns HTTP 200 with a valid title and
ZERO article links** -- re-measured during the recovery pass. It was recovered
by searching the product name. `/events/` returns **0 grep hits** in the package.

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 179 | Search for events by keyword and filter results to the Events tab | R | GAP | |
| 180 | See events recommended from your interests, Pages you follow, and what your network is attending | R | COVERED-CANNOT-DELIVER | **THE SURFACE IS READ AND THE PAYLOAD IS DELIBERATELY WITHHELD -- this is a SHAPER ruling, not a missing build.** `linkedin_events_home` opens the events root (admitted) and reports the recommendation sections; its own docstring states the limit in terms: *"No event titles, dates or organisers. Every section is reported as a COUNT. The recommendation sections are made of OTHER PEOPLE'S EVENTS, and this tool publishes how many rather than which."* So nothing needs building: the row is not GAP and it is not COVERED-PROVEN either, because the thing the row asks to SEE is exactly what the shaper refuses to say. **This is the repository's own split arriving on a row: the BOUNDARY decided this page may be OPENED; the SHAPER decided what may be SAID.** A second limit is stated by the same tool and matters to any consumer: `rows` is what is DRAWN, not what exists -- measured, a recommendation section drew three rows while its own control announced fifty events, which is why the tool carries a partial verdict at all. REOPENER: a ruling that recommendation-section contents may be published. Found 2026-09-19 by cross-referencing the 42 registered tools against GAP rows BY HAND, after an automated sweep of the same question failed four times (`scripts/unbanked_row_sweep.py`) |
| 181 | Find events hosted by Pages you follow | R | COVERED-CANNOT-DELIVER | Composes with row 52, the one COVERED-PROVEN read in the slice. **MEASURED 2026-09-19: THE COMPOSITION IS BLOCKED AT THE SECOND HALF, NOT THE FIRST.** Row 52 (the Pages you follow) is COVERED-PROVEN via `linkedin_followed_companies`. The events half is read by `linkedin_events_home` -- but that tool publishes **no organisers**, by the same deliberate shaper ruling recorded on `N 180`, because recommendation sections are made of other people's events. **You cannot join on a field that is never emitted**, so this row is blocked by a SHAPER decision and not by a surface, a boundary or a parser. It moves if and only if `N 180`'s reopener does, which makes the two one decision rather than two rows of work **BANKED 2026-09-19 BY THE READ-ROWS WAVE, AND IT IS A CONSISTENCY FIX RATHER THAN A NEW MEASUREMENT.** This cell already concluded the row is blocked by a SHAPER decision and that it moves if and only if `N 180`'s reopener does, "which makes the two one decision rather than two rows of work". **`N 180` IS ALREADY `COVERED-CANNOT-DELIVER`.** One of two rows declared a single decision cannot sit in a different state from the other. Against the census's own bar: `linkedin_events_home` exists; it HAS fired live (it measured a recommendation section drawing three rows while its own control announced fifty events); and it publishes "how many rather than which", with no organisers at all. That is a tool that cannot do the thing, not a tool nobody has tried. |
| 182 | Accept or ignore an event invitation | W | GAP | REV |
| 183 | Receive event invitations only from your 1st-degree connections | R | GAP | A setting-shaped constraint |
| 184 | Reach an event through its URL after it has been shared with you | R | GAP | |
| 185 | Attend an event you accepted | W | GAP | REV |
| 186 | Invite your 1st-degree connections to an event you are attending | W | GAP | REV for the invitee. **Weekly cap 1000** -- three orders of magnitude above anything else in this census |
| 187 | Filter your invitee list by location, company, school and industry | W | GAP | Another filtered read over his own connections |
| 188 | View the complete attendee list of an event | R | EXCLUDED-RULED | **A second member directory reachable without a profile load** -- and it is the SAME objection that put `N 165` out of scope, transferred by name rather than by analogy. `readonly.py`'s `/events/` admission comment lists what the root deliberately did not buy and names this row in it: *"THE ATTENDEE LIST -- census rows N 188 and N 189. A second member roster, and out of scope by the same ruling that put N 165 out of scope."* **MOVED 2026-09-19; NOT a new decision -- the ruling is from 2026-09-05 and the only thing that changed is that it is now ENFORCED.** The census stated the exact condition itself, at `_audit/_census/blocker-assignments.tsv` (`0aca3d0`): the verdict rested on *"prose in a source file and not a refusal anything can be shown failing against"*, and *"a row moves only when a shipped, shown-failing rule refuses the capability"*. That rule now ships: `tests/test_the_events_boundary_is_root_only.py` pins the attendee address refused, and is shown failing -- installing an `/events/.*` family pattern in memory turns 9 of its 13 refusals red, this row's among them. **The durable part is N 165's reason: the objection is to ENUMERATING PEOPLE, so it survives any change of address.** REOPENER: the operator ruling otherwise, which is his to make and nobody else's |
| 189 | See which of your 1st-degree connections have confirmed attendance, without attending yourself | R | EXCLUDED-RULED | **The same roster, filtered -- and the filter is applied BY LINKEDIN, so the page served is still the attendee roster.** Named in the same `readonly.py` sentence as `N 188` and moved on the same shipped guard; see that row for the bar and the control. **This one is the more tempting of the pair and that is why it is written out:** a 1st-degree-only view reads like a smaller ask, but it is the same enumeration of people who did not choose to be enumerated, reached by the same address. REOPENER: as `N 188` |
| 190 | Hide your own attendance from non-attending 1st-degree connections | W | GAP | REV |
| 191 | Message attendees who are already your connections | W | GAP | NOT-REV |
| 192 | Reach attendees who are not your connections via InMail | W | GAP | NOT-REV. The InMail half is EXCLUDED-RULED under R9; the ATTENDEE-TARGETING half is not, and is what makes this a distinct row |
| 193 | Share an event you are attending with your network | W | GAP | NOT-REV once posted |

### R. One recovered hashtag row that is people-discovery (1)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 194 | Find hiring managers through the #Hiring hashtag in search | R | GAP | **ASSIGNMENT SETTLED, STATE UNCHANGED.** `skew-gate` applied the A13 re-file in `5073827`; this row is `SEARCH-RESULTS-SURFACE` and that is not reopened here. It stays GAP on its own row text, and a 2026-09-19 feed read adds a second, independent reason it cannot be reached the other way: zero rendered hashtag anchors and zero `/feed/hashtag/` hrefs across four loads (`_audit/2026-09-19-hashtag-surface-live-evidence.md`). **So the people-search blocker is load-bearing whichever way the hashtag question falls** -- a blocker that still blocks when the contested half is removed is the row's real blocker. Blocker: no people search. The other seven recovered hashtag rows are post-composition or Page-admin and belong to the content slice |

### S. Admin-only capabilities -- counted separately (15: 14 GAP, 1 COVERED-UNFIRED)

He administers no Page, owns no group and organizes no event, so fourteen of
these are not capabilities he currently holds. A10-A15 were recovered in the
second pass.

**THIS TABLE GAINED A `state` COLUMN ON 2026-09-20, AND THE COLUMN IS THE
POINT.** It had three columns and no state cell, so its verdict lived only in
the prose above it and was turned into a countable `GAP` by a HARDCODED
OVERRIDE in two scripts -- `count_census_states.main` and
`enumerate_gap_rows.rows`, both spelled `if not st and letter == "N" and
<id matches A-digits>: st = "GAP"`. **That override made every row here
permanently GAP no matter what shipped**, because the state was in the code
rather than in the file. `A6` is the row that proved it: a tool shipped, and
nothing in the census could move. The override's own `if not st` is the
designed escape hatch and this column takes it -- the rows now say what they
are, and the override stays as a backstop for any A-row added without one.

**AND THE SECTION'S REASON IS WEAKER THAN IT READS, which is recorded here
rather than left for somebody to inherit.** "He administers no Page" rests, for
the Page family, on a Manage-Pages capture that is a FRAGMENT -- `<head>` plus
`<main>`, no `<html>`, `<body>` or `<nav>` -- in which all 20 href-bearing
elements are `/company/<digits>/` and zero are anything else. An instrument
that captured no page chrome could not have found an admin marker if one
existed, so "zero admin markers" is a fact about the capture, not about the
account. The EVENT half is genuinely measured (the self-scoped "Your events"
card is a rendered zero against a full sibling card as its control); the GROUP
half rests on five membership rows whose controls are `Leave this group`,
`Copy link to group` and `Update your settings`, with no owner-only control in
the vocabulary that arrived -- an absence never shown against a positive
control. See `_audit/2026-09-20-admin-rights-ready.md`.

| # | capability | R/W | state | note |
|---|---|---|---|---|
| A1 | Notify employees of a Page post | W | GAP | no Page; address refused |
| A2 | Follow another organization's Page on behalf of your Page | W | GAP | refused by `/follow` before the allowlist |
| A3 | View the Pages your Page follows | R | GAP | refused by `/follow` before the allowlist |
| A4 | Invite connections to follow a Page you manage | W | GAP | needs a second consenting human |
| A5 | View your Page's invitation credit balance | R | GAP | refused by `/invite` before the allowlist |
| A6 | Build a Page Follow button for your organization's website | W | COVERED-UNFIRED | `linkedin_page_plugin_snippet`; no Page id exists to build one from |
| A7 | Turn on automatic invitations to content engagers (Premium) | W | GAP | refused by `/settings/` before the allowlist |
| A8 | Turn off automatic invitations (Premium) | W | GAP | refused by `/settings/` before the allowlist |
| A9 | Invite followers of similar Pages to follow your Page (Premium) | W | GAP | needs a second consenting human |
| A10 | Invite your connections to a group you own or manage | W | GAP | needs a second consenting human |
| A11 | Message an individual group member as owner or manager | W | GAP | needs a second consenting human |
| A12 | Send a message request as a group admin to a member you are not connected to | W | GAP | needs a second consenting human |
| A13 | Privately message any event attendee as the organizer, without being connected | W | GAP | needs a second consenting human |
| A14 | Remove an attendee from an event you organize | W | GAP | `/events/<id>/` is not admitted; only the events root is |
| A15 | Withdraw an event invitation before the invitee responds | W | GAP | refused by `/invite`; also needs an invitation already sent |

---

## 5. THE 107 GAPS: WHAT EACH FAMILY WOULD TAKE

A shape, not a design. Reversibility is stated because it dominates this slice.
The eleven families below cover the first pass's 73; the second pass added 34
more in three families -- **Groups (18), Events (15) and one hashtag row** --
all of them READ-and-WRITE mixes on address families with zero prior art in the
package. They are not repeated here; sections P, Q and R carry them.

| family | rows | read/write | reversible | shape |
|---|---|---|---|---|
| **People search + 13 filters** | 79-96 (18) | READ | REV | One allowlist pattern for `/search/results/people/` plus a query builder, and a person-card parser. **`shape.parse_person_card` already exists and already works** -- `who_viewed_me` uses it live. The parser half is done |
| **Company pages** | 33, 47, 53, 54, 101, 102, 104 (7) | 6 READ, 1 WRITE | REV | One pattern for `/company/<slug>/`. Also closes `follow_company`'s residue: a posting gives a slug, unfollow addresses a numeric id, nothing resolves one to the other. A company page carries both |
| **Newsletters + hashtags** | 55-61 (7) | 4 WRITE, 3 READ | REV | Two allowlist patterns. Zero prior art: `newsletter` and `hashtag` are 0 hits |
| **Following people (read side)** | 38, 39, 40, 44 (4) | 3 READ, 1 WRITE | REV | Two patterns. **Row 39's surface was already found live** and written down as bearing on this. Cheapest family in the table |
| **Contact import** | 105-109 (5) | WRITE | NOT-REV | Mobile/OAuth flows. **Row 109 is the highest blast radius in the census** -- one confirm, many invitations. Recommend leaving closed |
| **Reporting and hiding** | 148-154 (7) | WRITE | 4 NOT-REV | Overflow menus that have never been opened. Needs a measurement pass before any design |
| **Profile-view analytics** | 132-136 (5) | READ | REV | **Zero extra page loads.** See 8.1 |
| **Groups, articles, misc follow** | 37, 41, 42, 43, 49, 50, 51, 63, 64, 76 (10) | 8 WRITE, 2 READ | REV | Assorted; no prior art |
| **Endorsements (receiving side)** | 114, 118 (2) | 1 READ, 1 WRITE | REV | **Row 118 is zero extra page loads on a page already open** |
| **Invitations (unreachable variants)** | 4, 5, 6, 7, 8 (5) | WRITE | NOT-REV | Depend on other gaps closing first |
| **Messaging-slice rows** | 149, 150, 151, 160 (4) | WRITE | mixed | Owned by `_audit/_census/messaging-and-content.md` |

**CORRECTED BY:** `_audit/2026-09-05-search-results-consent.md` -- the people-search row above says the parser half is done; measured in-process, parse_person_card returns nothing on a card with no Viewed timestamp, and no capture of that page exists to say whether it carries one

**Two GAPs cost nothing to close and are worth the lead's attention: row 118 and
rows 133-136.** Both sit on pages the server ALREADY loads and ALREADY parses.
Both are pure reads. Neither touches another person.

---

## 6. THE ELEVEN RULINGS, AND WHICH ROWS EACH PRODUCES

78 EXCLUDED-RULED rows come from eleven written passages. Six of them produce
71. Quoted so no row's state rests on a paraphrase.

**The per-ruling counts below OVERLAP and do not sum to 78.** Fifteen rows carry
two rulings (an address that is both forbidden by substring and inside a ruled
family, most often R1+R2 or R11+R2). The distinct total is 78; the eleven
headings below total 93.

### R1 -- `/mynetwork/` is refused, on a measured badge cost. Produces 14 rows.

`_audit/2026-08-30-linkedin-nine.md:311`:

```
### #7 -- connection invitations. Surface `/mynetwork/`. Bucket: UNMEASURED, and it will stay that way.

**Refused at the gate** -- the full ruling is section 2.2. The surface carries the
pending-invitation badge; this package has measured that badge family resetting
on load twice; and the residual cost lands on the people whose invitations would
be marked seen.

**Filing this as a debt would be dishonest**, because a debt implies somebody
should pay it, and the ruling is that nobody should.
```

and the circularity that closes it, same file `:321`:

```
the thing that would change the ruling is a MEASUREMENT that `/mynetwork/` does not
reset its badge -- and taking that measurement requires resetting the badge.
```

Rows: 3, 13, 14, 15, 16, 17, 18, 19, 21, 22, 32, 62, 97, 98. (14 -- row 15 also
carries R8.)

### R2 -- `invitation`, `/invite`, `/connect`, `/withdraw` are forbidden substrings. Produces 15 rows.

`readonly.py:469-471`, checked BEFORE the allowlist. `_audit/2026-08-30-linkedin-nine.md:326`:

```
**One thing worth knowing, since it is free:** `/mynetwork/invitation-manager/`
is refused by the forbidden substring `invitation`, and `/invite` and `/connect`
are on that list too. So even a loosened allowlist cannot reach the invitation
surfaces. That was already true and is not a change.
```

Rows: 9, 10, 11, 12, 23, 24, 25, 26, 27, 28, 29, 30, 72, 73, 75 (plus 13, 14,
16, 19 shared with R1).

**This is the ruling that removes his connections list**, and it does so as a
side effect. The list's only address is `/mynetwork/invite-connect/connections/`,
which contains both `/invite` and `/connect` -- two substrings put on the list
to stop invitations, catching a read that has nothing to do with inviting
anyone.

### R3 -- `endorse_or_recommend`. Produces 13 rows, and it is a MEASUREMENT.

`writes.py:1769`:

```
"endorse_or_recommend": (
    "REASON REPLACED 2026-08-30. It used to read 'a statement ABOUT "
    "ANOTHER PERSON, which is not his to automate' -- which was POLICY, "
    "and was overtaken by the operator's own 2026-08-25 ruling that an "
    "endorsement is a gift to the person receiving it rather than an "
    "extraction from them. The refusal survives on a MEASUREMENT instead, "
    "and the measurement was re-taken the day the reason changed: zero "
    "endorse controls across 13 tracked fixtures with zero shaping "
    "blindness, zero on his own skills surface, and zero among the 222 "
    "controls read live on his own profile on 2026-08-30. You cannot "
    "endorse yourself, so the only surface that would carry the control "
    "is a THIRD PARTY'S PROFILE -- and loading one leaves them a durable "
    "record, which this package measures from the receiving end with "
    "linkedin_who_viewed_me. IMPOSSIBLE AS SPECIFIED, not unwanted"
),
```

Rows: 111, 112, 113, 119-128. See the precision flag under section K -- the key
names recommendations, the measurement counted endorse controls.

**REOPENER, NAMED 2026-09-20 -- and it is named HERE rather than on the rows
because ten of the thirteen (119-128) HAVE NO REASON CELL TO PUT IT IN.** This
ruling is a MEASUREMENT, as its own heading says, so it can go stale the way
every measurement can, and until now nothing said what would tell anybody.
TWO independent conditions, either of which reopens:

1. **A non-zero endorse control count** from a re-take of the same reading on a
   surface this package may load -- the account's own skills surface, or the
   tracked fixture corpus. The zeros are 13 fixtures, the account's own skills
   page, and 222 controls read live on 2026-08-30; a re-take is
   `scripts/_probe_endorse_and_follow_lines.py`. WHO: that instrument.
2. **Any count at all of RECOMMENDATION controls**, which reopens 119-128
   independently of the endorse number. This is the precision flag above,
   turned into a trigger: the key names recommendations, the measurement
   counted ENDORSE controls, and **no census of recommendation controls has
   ever been taken** -- so for those ten rows the measurement under them is not
   merely dated, it is of a different object. WHO: a needle that does not exist
   yet, which is itself the finding.

**WHAT DOES NOT REOPEN THESE ROWS, stated so the reopener cannot be read wider
than it is:** a control found on a THIRD PARTY'S PROFILE. R4 forbids loading
one, that prohibition is ours and is not a measurement, and it survives any
number this reopener produces.

### R4 -- loading a third party's profile is permanently forbidden. Produces 14 rows.

`writes.py:1788`:

```
"load_a_third_partys_profile_to_measure_a_control": (
    "ADDED 2026-08-30, and it is the rule the endorsement ruling above "
    "rests on rather than a restatement of it. A profile view is an "
    "EMISSION, and this server can read the receiving end of that signal: "
    "linkedin_who_viewed_me returns rows, reaching 365 days back on his "
    "Premium Career account, and every row is somebody who loaded a "
    "profile and left a record its owner can still read most of a year "
    "later. So loading a stranger's profile in order to find out what "
    "controls it carries spends THEIR privacy on OUR measurement, and the "
    "cost lands entirely on somebody who is not him. Whether HE chooses "
    "to open a profile is his own affair; this server may not do it for a "
    "measurement"
),
```

Reinforced by `send_invitation`'s own `direction_source` (`writes.py:1506`):
"No third party's profile is ever loaded -- that would leave them a durable
record, which is the one thing this whole family of rulings refuses to spend."

Rows: 2, 30, 31, 34, 35, 36, 65, 66, 103, 141, 144, 145, 146, 147.

**A scope note the lead should see.** The entry's own words are "may not do it
for a MEASUREMENT". Rows 34-36 and 141-147 are ACTS, not measurements. They are
filed EXCLUDED-RULED because `send_invitation`'s design statement generalises
the rule to any load, and because no code path builds such a url. But the
`PERMANENTLY_FORBIDDEN` text alone does not cover acting, and if anyone ever
wants to follow a person through this server, that gap in the wording is where
the argument will happen.

### R5 -- `delete_or_withdraw_anything`. Produces 6 rows.

`writes.py:1801`:

```
"delete_or_withdraw_anything": (
    "destruction is not a write this design covers, at any confirm level. "
    "NOTE WHAT NOW DEPENDS ON THIS ENTRY, added 2026-08-30 and CORRECTED "
    "the same day after a review counted it: FIVE of the specs above cite "
    "it in reversible_by -- an application, a post, a comment, an "
    "invitation and a message all say NOBODY can take them back through "
    "this server, and this line is the reason."
),
```

Rows: 10, 12, 29, 110, 113, 125.

### R6 -- `deanonymise_a_viewer`. Produces 1 row (131).

`writes.py:1784`: "six of ten profile viewers chose anonymity; the row LinkedIn
renders him is the whole of what he is entitled to".

**REOPENER, NAMED 2026-09-20, and it is narrower than it first looks.** The
PROHIBITION is ours and is not contingent on anything: nothing reopens
de-anonymising a viewer who chose anonymity. What IS contingent is the second
clause -- *the row LinkedIn renders is the whole of the entitlement* -- which
is a fact about what LinkedIn draws for this account on a given day, and
"six of ten" is a dated reading rather than a constant. So: **LinkedIn itself
rendering an identity the account is entitled to see reopens this row, because
READING WHAT IS DRAWN IS NOT DE-ANONYMISATION** -- the key forbids inferring an
identity LinkedIn withheld, not reading one it published. WHO: a capture of
`/analytics/profile-views/`; the shape tally already run on that page is the
instrument. **An identity recovered by any inference, join or lookup reopens
nothing**, which is the distinction the key exists to hold.

### R8 -- `auto_accept_or_auto_reply`. Produces 1 row (15).

`writes.py:1829`: "a reply in his name that he did not read is a message from a
stranger wearing his face".

### R9 -- InMail and outreach automation. Produces 3 rows. FOUR independent rulings, none contradicted.

The load-bearing one, `mcp-servers/_audit/2026-08-20-linkedin-parity.md:971`:

```
### NOT RECOMMENDED - outreach or invitation automation. Unchanged, better reasons.
The earlier reasoning (free-tier note caps) was wrong. The correct reasons: the invitation
cap is behavioural, not tier-linked, **automation suspicion is one of its documented
drivers**, Premium does not lift it and capacity cannot be bought "while restricted, or
otherwise"; and at 5 InMail credits with no follow-ups permitted there is nothing
mechanical worth automating. **He now also has a paid subscription that a restriction would
strand.**
```

Its arithmetic, same file `:837`:

```
**Ground 1 - the arithmetic makes sending automation absurd.** He has **5 InMail credits a
month**. That is roughly one send per week. Automating five actions a month is not
engineering, it is ceremony.
```

Its verdict, same file `:875`:

```
**Verdict: the suspicion is confirmed and then some.** Most of the target-choosing value is
already sitting unread in his Gmail, in structured form, with names and profile URLs. The
sending half is where all of the risk lives and almost none of the value.
```

The standing prohibition, `.claude/skills/linkedin-jobs/SKILL.md:329`:

```
The tool **recommends only**. It never sends, drafts-and-sends, or touches LinkedIn. He
sends by hand in the browser. Do not add sending.
```

and the cut named explicitly, `SKILL.md:387`:

```
The original reasoning still stands and is why that server is built the way it is: **the
asset at risk is the user's professional identity.** LinkedIn is the least tolerant
platform in this family. That is why the first write round ships only reversible actions
(save/unsave, follow, Open To Work) behind an off-by-default flag, why apply, connect and
InMail were deliberately cut, and why a gate may not print a reversibility claim that has
not been measured.
```

The skill's reference file, `.claude/skills/linkedin-jobs/inmail-targeting.md:25`:

```
The no-follow-up rule means a single message must stand alone. There is no sequence, no
bump, no second touch. That also caps the value of automating any of this: five
unrepeatable sends a month is not a pipeline, it is five decisions.
```

Rows: 156, 157, 158 (159 is R11).

**One near-miss that is NOT a ruling**, recorded so nobody cites it as one.
`_audit/2026-08-25-cannot-vs-will-not.md:265` is a measurement-ORDER position
and points the other way:

```
**I have zero measurements of the InMail or invitation surface.** Building them
now would mean guessed selectors and a guessed request body, which the same
instruction forbids. So they must be MEASURED first -- that is not a stall, it
is the only order that satisfies both halves.
```

**REOPENER, NAMED 2026-09-20. Three of this ruling's four grounds are facts
about the ACCOUNT, not about the capability, and none of them said so.** Read
them back: a monthly allowance of five, a cap that Premium does not lift, and a
paid subscription that a restriction would strand. Every one of those is a
thing that changes when the account changes, and the ruling was written as
though they were constants. Either of these reopens it:

1. **A monthly InMail allowance materially above five**, read off a Premium
   surface. Ground 1 is arithmetic -- *"five actions a month is not
   engineering, it is ceremony"* -- so it is an argument WITH A THRESHOLD IN
   IT, and a threshold that nobody re-reads is a constant by accident. WHO: a
   capture of a Premium surface.
2. **The account ceasing to hold a paid subscription a restriction would
   strand**, which removes the fourth ground outright. WHO: the operator.

**WHAT THESE DO NOT REOPEN.** The behavioural-cap ground and the
identity-at-risk cut are POLICY and are ours; they survive any allowance. So a
reopened R9 is a smaller ruling, not an absent one -- which is the distinction
between a write-off resting on a fact and one resting on a decision.

**AND 157 IS NOT A SENDING ROW.** This ruling is about outreach AUTOMATION;
`157` is *view your available InMail credits*, a READ, and the only thing
actually holding it was the measured absence of a balance. It is filed
MEASURED-ABSENT 2026-09-20 and carries its own reopener; see its row. Rows
here are now **156 and 158**.

### R11 -- the settings family is admitted by name or not at all. Produces 21 rows.

`readonly.py:521` forbids `/mypreferences/d/categories/`; `:522` forbids
`/psettings/`. The ruling is at `server.py:1949`:

```
* ``/mypreferences/d/`` -- ADMITTED, below. No badge to consume, nothing a
  third party observes, no value changed by the load. The INDEX only: the
  toggles live on ``/mypreferences/d/categories/<name>`` and those are now on
  the forbidden substring list.
```

Rows: 67, 68, 69, 70, 71, 72, 73, 74, 75, 77, 78, 115, 116, 117, 137, 138, 139,
140, 142, 143, 159. (21 -- several also carry R2.)

### R10 / R7 -- not load-bearing here

`/psettings/` (R10) is folded into R11 above. `mark_notifications_read` (R7,
`writes.py:1815`) produces no row in this slice; it is recorded because it is
the third member of the badge family whose measurements ground R1.

---

## 7. THE HEADLINE FINDING

**Everything he can do on LinkedIn's network surface, he can do through this
server for exactly three of 194 capabilities, and all three are reads.**

The four PERFORMABLE network writes -- `send_invitation`, `follow_company`,
`unfollow_company`, `send_message` -- are all COVERED-UNFIRED. Three have never
run at all; the fourth ran and refused. `writes.PERFORMABLE` is not a record of
what works, and this slice is the clearest demonstration of that in the package:
**four sanctioned network writes, zero completions, and the sanctioning is nine
days old.**

The vocabulary trap is worth restating because it decides how this table reads.
`PERFORMS` and `PERFORMED` in the audit corpus are CAPABILITY words meaning "in
`PERFORMABLE` and will not refuse at the gate". `_audit/2026-08-30-linkedin-writes.md`
says `### #8 follow a company -- linkedin_follow_company. **PERFORMED.**` at
line 273 and, at line 27 of the same document, `| writes performed | **NONE.**
No confirm_token was passed to anything, by anyone, at any point |`.

---

## 8. SIX THINGS THIS CENSUS FOUND THAT ARE NOT ROWS

### 8.1 The profile-view analytics are already on screen and thrown away

`linkedin_who_viewed_me` navigates to `https://www.linkedin.com/analytics/profile-views/`
-- the Premium analytics page -- and then runs `dom.harvest_linked_cards` with
`href_pattern=dom.PERSON_HREF`, keeping only person cards. The viewer-trend
graph, the top-locations breakdown, the top-companies breakdown and the notable-
viewers list are **on the page it already loaded**, and are discarded before
parsing. Rows 133-136 are four READ gaps whose surface is open, whose page load
is already paid for, and whose only missing piece is a parser. In a job hunt,
"which companies are looking at me" is a higher-order signal than any single
viewer row.

### 8.2 The follow pair is asymmetric, and the asymmetry now runs the wrong way

`unfollow_company.reversible_by` (`writes.py:575`) still says:

```
"HIM, by hand, in LinkedIn's own interface. NOT this server: "
"linkedin_follow_company is sanctioned but is not performed, so a "
"re-follow through this server does not exist. The pair is "
"deliberately ASYMMETRIC and neither half pretends the other "
"covers it -- this server can stop a follow and cannot start one. "
```

**`follow_company` IS in `PERFORMABLE` today** (writes.py:4397), so the stated
reason is stale. But the conclusion survives on a different and better ground,
which `follow_company.reversible_by` gives (`writes.py:747`): the undo cannot be
AIMED. A posting names its employer by SLUG; the unfollow surface addresses rows
by NUMERIC COMPANY ID; nothing in the package resolves one to the other. So a
follow taken through this server still cannot be undone through this server --
right answer, and one of the two sentences explaining it is out of date. Flagged
for the freeze rather than edited, since the brief forbids touching tracked
files.

### 8.3 Addressing a person by name in the composer was measured dead this morning

`_audit/2026-09-03-typeahead-name-matching-is-dead.md`. The first live run of
`linkedin_send_message` measured that a bare fill commits NOBODY: a clean
composer, a correct first-degree name, all four recipient selectors reading
zero. A typeahead-choose step was added the same day. This is the only network
capability in the slice where a live measurement exists at all, and it exists
because the design chose to refuse rather than proceed on a satisfied-looking
gate.

### 8.4 The 2026-09-02 ship-and-repair is not in `_audit/`

`send_invitation` shipped 2026-09-01 unable to act (blocker 2: a whole-url
landing check against a `/in/me/` surface measured to redirect) and was repaired
in commit `ea5354d` on 2026-09-02. **That record exists only in a commit
message, a test docstring, and the untracked `_TEAM_LEAD_SUCCESSOR_BRIEF.md` at
the repo root.** Grepping all 72 `_audit/*.md` files for `could not act`, `three
blockers`, `NAVIGATIONS ATTEMPTED`, `anchor_label_for` and `shipped dead`
returns nothing. The running audit file `2026-08-31-linkedin-perform.md` ends at
section 105 and mentions neither tool. Anyone reading `_audit/` alone will
conclude `send_invitation` has worked since 2026-09-01.

One further honesty note on that repair: the commit says the failing pair was
"derive[d] ... from the specs rather than listing it". `update_profile_field`'s
failure was measured end to end; **`send_invitation`'s was inferred.** Its
blocker-2 failure has never been observed on a live page. That is why row 1 is
COVERED-UNFIRED and not FIRED-FAILED.

### 8.5 LinkedIn DOES offer a withdraw. The server calls that unmeasured, and it is right about itself and wrong about the product

`send_invitation`'s spec says (`writes.py:1537`):

```
reversibility_evidence=(
    "NOT MEASURED, and it cannot be measured from here. The surface "
    "that would show a withdraw affordance is the sent-invitations "
    "manager, whose address contains 'invitation' and is on the read "
    "boundary's forbidden list -- so this server has never seen it "
    "and holds no evidence either way."
),
```

and its docstring goes further: "whether LinkedIn offers a withdraw at all is
UNMEASURED -- which is a stronger statement than this server lacking one."

**Both sentences are true of the SERVER and the second is false of LINKEDIN.**
Fetched directly from `linkedin.com/help/linkedin/answer/a568295`, a public page
requiring no account: LinkedIn documents the withdraw on desktop and mobile --
My Network, Invitations, Show all or Manage, the Sent tab, Withdraw, then
Withdraw again in a confirmation pop-up. It also documents the price:

```
"You won't be able to send a new invitation to the same member for up to three weeks."
```

The server's evidence claim is correct as scoped -- it holds no evidence, because
its own read boundary forbids the only surface that would show it. The
docstring's generalisation from "this server cannot see it" to "LinkedIn's offer
is unmeasured" is the error, and it is the error a census that never leaves the
repository would repeat.

**The lead's warning against assuming symmetry with applications was right in
both directions.** A sibling slice verified from LinkedIn's own help page that a
submitted application CANNOT be withdrawn. An invitation CAN. Two actions that
this server files identically under `delete_or_withdraw_anything` differ in the
product, and only one of the two is genuinely one-way.

**But the reversibility is of FORM, not of CONSEQUENCE**, and this is the part
that matters for a write gate. Withdrawal is quiet -- "The recipient will not be
notified when you withdraw the invitation" -- and yet
`linkedin.com/help/linkedin/answer/a550555` states:

```
"Withdrawing pending invitations will not remove the restriction"
```

So withdrawing undoes the pending row and does NOT undo the account signal the
invitation contributed to. `send_invitation`'s `residue` -- "this is the one
action here whose repetition has a consequence for the account itself" --
survives the correction intact.

### 8.6 Blocking is documented by LinkedIn as NOT fully undoable

Row 141 said "NOT-REV in practice" on a cooldown argument. The recovery pass
established something stronger from LinkedIn's own pages. From
`answer/a1380117`: blocking means "If you're connected, you won't be connected
anymore" and "We'll remove any endorsements and recommendations from that
member". From `answer/a1338373`, reinstatement is ruled out explicitly:

```
"recommendations from a member you blocked cannot be reinstated if you unblock them"
```

and the endorsement case is confirmed separately at `answer/a565110` as
"automatically removed and not reinstated if you re-establish the connection".

LinkedIn also states an asymmetry outright: "There is no limit to how many
members you can block", one sentence away from a 2000-block threshold past which
UNBLOCKING may fail, plus a 48-hour wait before re-blocking.

**A block therefore destroys reputation artifacts other people wrote about him**
-- their recommendations, their endorsements -- permanently, and the blocked
member is never notified. If a block capability is ever proposed for this
server, that is the sentence its gate has to print.

---

## 9. WHICH HELP CENTER AREAS WERE WALKED, AND WHICH WERE NOT

**An unwalked area is a hole in the denominator. None of the following reads as
a zero.**

### 9.1 Walked

146 page-fetches across three walks (some overlapping): 42 on invitations and
connections, 42 on following and followers, 62 on discovery, social proof,
profile views and safety. Entry points were `linkedin.com/help/linkedin`, the
Connections topic tree `topic/a151001`, and link-following outward from there,
plus `WebSearch` restricted to `linkedin.com`.

Covered: invitations in both directions, the invitation manager, connection
removal, degrees, network size, following and unfollowing people, Pages,
newsletters, articles and topics, followers versus connections, follow
visibility and follow-primary, people search and its filter list, PYMK, alumni,
contact import, Open Profile, endorsements, recommendations, Who's Viewed Your
Profile and its tier boundary, profile-viewing options, blocking, reporting,
muting, and Page-follow invitations including the admin variants.

### 9.2 Attempted and NOT reached -- named holes

| what | why | consequence |
|---|---|---|
| **Hashtag following** (`answer/a528144`) | 404 on all four URL forms tried | Rows 59-61 are a **floor, not a saturation claim**. LinkedIn's hashtag surface may carry capabilities not counted here |
| **Invitation expiry** (`answer/a546712`) | 404 on every URL form while still appearing in search | The six-month expiry and two-reminder numbers were recovered independently from `answer/a548242`, so no capability was lost -- but the dedicated page was not read |
| **AI-powered people-search filters** (`answer/a8085506`) | Renders a gated-rollout notice with no body | **The newest people-search filter set is UNMEASURED.** Rows 81-93 are LinkedIn's classic filter list; if the AI filters have shipped to his account, that block is incomplete |
| **Mute article** (`answer/a524326`) | Indexed under "Follow, unfollow, or mute people" but the body served contained zero mute content across three URL forms | Mute's EXISTENCE is established from two other directly-fetched pages; the exact mute mechanics are not |
| **24 linked-but-unwalked pages** in the following cluster | Link budget | Enumerated in `_audit/_scratch/_census-hc-following.md` -- GITIGNORED working notes that reach no clone, so that path is provenance and not somewhere to look; the 24 are unwalked either way, which is what this row records |

### 9.3 NOT WALKED AT ALL -- deliberate scope calls, listed so they are visible

| area | why it was left | risk it carries |
|---|---|---|
| ~~**LinkedIn Groups help tree**~~ | **CLOSED second pass.** Recovered by searching the product name | 18 in-slice rows added (section P) plus 3 admin. Group member directories, in-group invitations and connection filtering are now counted |
| ~~**LinkedIn Events help tree**~~ | **CLOSED second pass.** The topic page returns HTTP 200 with ZERO article links; recovered by searching the product name | 15 in-slice rows added (section Q) plus 3 admin. Attendee lists and event invitations are now counted |
| **Sales Navigator and Recruiter help centers** | Separate products; the free-account boundary was taken from `linkedin.com/help/linkedin` only | The brief asked for "Sales-Navigator-adjacent features available on a normal account". What is answered is what the CONSUMER help center says a free account can do. Anything Sales Navigator exposes that leaks into the consumer product is not counted |
| **Company Page admin tree** | 9 rows harvested opportunistically, not exhaustively | The admin block is a sample, not a census |
| **Mobile-only network surfaces** | Not walked separately | Contact sync (rows 105-107) is mobile-first; its desktop equivalents may differ |
| **Localised / India-specific variants** | Not walked | Unknown |

### 9.4 The numbers LinkedIn states, and the one it does not

A dedicated limits pass fetched 26 Help Center articles. Established:

| what | LinkedIn's stated value |
|---|---|
| Maximum 1st-degree connections | **30,000**, not liftable by tier |
| Followers | **unlimited**, stated explicitly in both directions |
| At the connection ceiling | Follow becomes the default profile action; you can neither send nor **ACCEPT** invitations until you remove connections |
| Invitation expiry / reminders | **6 months** / up to **2** |
| Cooldown after withdrawing before re-inviting | **3 weeks** |
| How an invitation restriction lifts | by **waiting**; typically **1 week**. Premium does not lift it, and support cannot: "LinkedIn cannot remove or shorten the wait period" |
| Members you may block | **no limit** -- but unblocking is documented as possibly unavailable past **2000** blocks |
| Cooldown before re-blocking | **48 hours** |
| Skills listed | **100** |
| Endorsements given | **150 per 24 hours**, explicitly not increasable |
| Non-admin Page-follow invitations | **30/month** for your employer's Page, **50/month** for other Pages, and only Pages under 5,000 followers |
| Event invitations | **1000 per week** |
| Follow / unfollow notification | a non-connection **IS** notified on follow and on re-follow; **NOT** notified on unfollow |

**And the one LinkedIn does not state: the invitation cap itself.** No page
walked publishes any number of invitations per week, per month or per day.
LinkedIn documents the MECHANISM in full -- restriction is triggered by
invitations "ignored, left pending, or marked as spam by the recipients", cannot
be bought off ("You can't buy or acquire more invitations while you've been
restricted, or otherwise"), and applies to Basic and Premium alike -- and
publishes no threshold for any of it. The widely repeated 100/200-per-week
figures trace only to member-written Pulse posts, which are not sources.

**LinkedIn states outright that the member is blind to the accumulating signal**
(`answer/a540947`):

```
"There is no functionality for a member to see which recipients, or how many
recipients, have selected I don't know this person in response to your invitations"
```

That CORROBORATES `send_invitation`'s own `residue` (`writes.py:1533`) rather
than merely leaving it unchallenged:

```
"There is a second, quieter "
"cost: LinkedIn restricts accounts whose invitations are "
"frequently ignored or marked 'I don't know this person', so this "
"is the one action here whose repetition has a consequence for "
"the account itself. Nothing readable reports that limit."
```

The last sentence is confirmed from the outside: **nothing LinkedIn publishes
reports that limit either.** The server's claim is correct, and now it is
corroborated rather than merely unchallenged.

**One Help Center self-contradiction, and it is three-way rather than two-way.**
The personalized-note allowance reads **3 per month at 200 characters** on
`a563153`; **5 per month** on both `a6239760` and `a550555`; and the character
cap disagrees too -- `a563153` attaches no Premium cap, `a6239760` says 300.
Left unadjudicated: LinkedIn contradicts itself and picking a winner would
manufacture a fact. Row 5 in the table stays a GAP either way, since the tool
takes no note parameter at all.

---

## 10. TWO THINGS THIS CENSUS DID NOT ESTABLISH

1. **Whether `linkedin_notifications` has ever returned a live row.** Four
   audit passages say it was never called, all dated 2026-08-23, and nothing
   later addresses it. Rows 20 and 45 are COVERED-UNFIRED on that reading. If a
   later live run exists and was not written down, both should be
   COVERED-PROVEN and the tool table in section 3 is wrong about it.

2. **Whether rows 67-78 are double-counted against `_audit/_census/profile.md`.**
   Both slices map the settings family under the same R11 ruling. Resolving it
   requires comparing this table against that file's 145-row settings walk
   row-by-row, which is a top-level de-duplication job, not a slice one. Flagged
   in section G rather than silently dropped from either side.

---

## 11. THE DELTA AGAINST THE FROZEN TOP-LEVEL TOTAL

`61d3816` froze the four-slice census at **661 capabilities, 45 proven, one
write that has ever landed**, with this slice contributing 160 mapped + 9 admin.

**This slice is now 194 mapped + 15 admin.** The delta:

| | frozen | now | delta |
|---|---|---|---|
| mapped, in scope | 160 | 194 | **+34** |
| COVERED-PROVEN | 3 | 3 | 0 |
| COVERED-UNFIRED | 6 | 5 | -1 |
| COVERED-CANNOT-DELIVER | -- | 1 | +1 |
| EXCLUDED-RULED | 78 | 78 | 0 |
| GAP | 73 | 107 | **+34** |
| admin-only | 9 | 15 | +6 |

**Every one of the 34 new capabilities is a GAP.** Not one is covered, and not
one is ruled -- `/groups/` and `/events/` return zero grep hits across the whole
package. The recovery did not find hidden coverage; it found that the hole was
bigger than the first pass could see.

**The top-level 661 understates the denominator by at least 34 from this slice
alone**, and the covered numerator is unchanged. The lead should assume the same
hazard bit the other three slices and decide whether to re-freeze. The direction
of the error is one-way: a topic-page walk can only UNDERCOUNT.

## 12. THE INSTRUMENT THAT CLOSED THE HAZARD

The hazard is real and was re-measured directly during the recovery pass by
counting `answer/a` links in each topic page's server-rendered HTML:

| topic page | HTTP | article links rendered |
|---|---|---|
| `/help/linkedin/topic/a150003` (Events) | 200 | **0** |
| `/help/linkedin/topic/a151003` (LinkedIn Live) | 200 | **0** |
| `/help/linkedin/topic/a150001` (Networking) | 200 | 37 |
| `/help/linkedin/topic/a151001` (Connections) | 200 | 29 |

Events returns a valid page with a valid title and zero articles. Nothing in
the response distinguishes that from a product with no features.

**LinkedIn's help center has a server-rendered search index, reachable without
an account, and the parameter name is the whole trick:**

    https://www.linkedin.com/help/linkedin/search?q=<terms>

`?query=`, `?keywords=`, `?searchTerm=`, `?term=` and `?text=` all return
**HTTP 400**, and `/help/linkedin/solutions?query=` returns **404** -- which is
very likely why an earlier walk concluded the help center had no searchable
index. It has one, and it queries LinkedIn's own article index rather than a
third-party crawl, so it cannot miss an article merely because no external
engine indexed it. **This is strictly better than the WebSearch method the
briefs prescribed** and should be the default for any further Help Center work
on any slice.

Two curl-only instruments were built on it, `hcsearch.sh` and `hcbody.sh`, and
both were shown failing as well as succeeding. They belong in the project
instrument register.

**METHOD DEVIATION, DISCLOSED.** Both recovery children found the session's
WebSearch budget already exhausted (200 of 200) before they started, and every
third-party engine blocked (DuckDuckGo CAPTCHA, Mojeek 403, Marginalia
obfuscated). Rather than declare the holes unrecoverable they substituted: one
used the `?q=` index above, the other used `tavily_search` scoped to
linkedin.com with every quote and number **re-read from the live page** rather
than relayed. Both stayed inside every prohibition -- no browser, no login, no
authenticated page, no `mcp__linkedin__` call. Reviewed and accepted; the
evidence rule (a number counts only if a Help Center page states it) held in
both.

**One inference is labelled as one and not acted on.** The recovery could not
find any follow-a-hashtag article: `a528144` is dead on eight URL forms, sixteen
query phrasings across four help centers returned no replacement of any id, and
`a5999182` carries a dated retirement receipt for profile hashtags
(February/March 2024). The best-supported reading is that LinkedIn RETIRED the
member hashtag-follow surface. **Rows 59-61 were nevertheless kept mapped**,
because deleting capabilities on an unverified inference is the same undercount
this pass exists to correct, only pointing the other way.

## 13. PROVENANCE

Repo state: branch `master`. First pass written against the tree at 2026-09-03
15:10; second pass appended after `61d3816` committed this file, so it is now a
tracked file and this revision shows as a modification rather than an addition.
Line numbers are as of the first-pass tree.

Intermediate extractions, all untracked, under `_audit/_scratch/`:

    _census-network-specs.md      the 13 WriteSpecs, PERFORMABLE, the guards,
                                  the read allowlist and the census keys, read
                                  with ast.parse rather than grep; 34 verbatim
                                  blocks re-verified byte-exact against source
    _census-network-livefire.md   8 live-fire verdicts over the 72-file audit
                                  corpus, plus the four InMail rulings and the
                                  three blockers
    _census-hc-invitations.md     52 rows, 42 Help Center pages
    _census-hc-following.md       58 rows, 42 Help Center pages
    _census-hc-discovery.md       94 rows, 62 Help Center pages
    _census-hc-recovery.md        56 rows recovered from four holes that the
                                  topic-tree walk had read as empty; the
                                  ?q= search-index discovery
    _census-hc-limits.md          20 limits established from 26 articles; the
                                  three-way note contradiction; the blocking
                                  irreversibility finding

No LinkedIn account was accessed at any point by this slice or by any of its
children. No tracked file was modified. Nothing was committed.
