# CENSUS SLICE: NETWORK AND PEOPLE

Written 2026-09-03. Read-only. **No LinkedIn account was touched**: no browser,
no session, no page load, no `mcp__linkedin__*` call. The taxonomy was imported
by walking LinkedIn's PUBLIC Help Center; the coverage verdicts come from the
repository at `D:\Sundeep\projects\job-hunting\mcp-servers\linkedin`. Nothing was
committed and no tracked file was edited.

---

## 1. COUNTS

    CAPABILITIES ENUMERATED, IN SCOPE, MAPPED       160

      COVERED-PROVEN                                  3
      COVERED-UNFIRED                                 6
      EXCLUDED-RULED                                 78
      GAP                                            73

Counted separately so neither inflates the member denominator:

    PAGE-ADMIN capabilities (require Page admin rights he does
      not hold; all 9 are GAP -- no tool, no ruling)                    9
    ----------------------------------------------------------------
    TOTAL ENUMERATED                                                  169

Raw rows harvested across the three Help Center walks before dedupe and
scoping: **204** (52 invitations + 58 following + 94 discovery). Removed: 26
duplicates across walks, 9 rows owned by the messaging census slice, 9 split
out as Page-admin.

**Three numbers carry this slice.**

**COVERED-PROVEN is 3 of 160, and all three are READS.** They are: the list of
Pages he follows, his profile-viewer list, and the anonymous rows inside it.
**No network or people WRITE has ever completed against live LinkedIn.** Not one
invitation, not one follow, not one unfollow, not one message.

**EXCLUDED-RULED is 78, and it is not 78 decisions.** Six written rulings
produce 71 of the 78. Section 6 splits them out rather than letting the total
imply a deliberation that did not happen 78 times.

**GAP is 73, and 23 of them are one missing surface.** People search --
`/search/results/people/` -- and its thirteen filters account for 23 of the 73.
There is no pattern for it in the read allowlist and, critically, **no sentence
anywhere in the repository about it.** Nobody ruled against people search; it
was never considered.

---

## 2. HOW A CAPABILITY WAS ASSIGNED A STATE

    COVERED-PROVEN     a tool exists AND an audit records it firing live and
                       returning what it claims. Cited per row.
    COVERED-UNFIRED    a tool exists and would not refuse at the gate, and
                       nothing records it completing live.
    EXCLUDED-RULED     no tool, and a written passage in this repo gives a
                       reason that BEARS ON THIS CAPABILITY -- naming it, or
                       naming an address family or act-class containing it.
                       Quoted per row group in section 6.
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

**One state needed a footnote and got one instead of a fifth bucket.**
`linkedin_send_message` HAS run live, twice, and REFUSED both times. That is not
COVERED-PROVEN (nothing completed) and "no evidence it has ever run" is false.
It is filed COVERED-UNFIRED with `RAN-AND-REFUSED` in its note. The distinction
matters: a refusal that fires is a measurement, and this one produced the
finding that killed name-addressing (section 8.3).

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
| 10 | Withdraw a pending invitation you sent | W | EXCLUDED-RULED | R5 + R2 |
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
| 38 | View the list of people you follow | R | GAP | Blocker: `/mynetwork/network-manager/people-follow/following/` is not on the allowlist. Its sibling `/mynetwork/network-manager/company/` IS, and is read successfully today. Probed at `_audit/_scratch/slice-guard-probe.md:44` |
| 39 | View the people you previously unfollowed | R | GAP | Blocker: `/mypreferences/d/unfollowed` -- **found live and written down** at `_audit/2026-08-30-nine-live-census.md`, "People you unfollowed", noted there as bearing on this exact capability. Never built |
| 40 | Re-follow a person you previously unfollowed | W | GAP | REV. Same surface as 39 |
| 41 | Follow a member from one of their articles | W | GAP | REV |
| 42 | Unfollow the articles of a member you are not connected to | W | GAP | REV |
| 43 | Mute a person from a feed post | W | GAP | REV. `mute` has **0 hits** anywhere in `linkedin_server/*.py` |
| 44 | View your own followers | R | GAP | |
| 45 | Be notified when a non-connection follows you | R | **COVERED-UNFIRED** | `linkedin_notifications` |

### F. Following organizations, newsletters, hashtags, groups (21)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 46 | Follow the company attached to a job posting | W | **COVERED-UNFIRED** | `linkedin_follow_company`, from `/jobs/view/{id}/`. REV in LinkedIn, **NOT-REV through this server** -- see 8.2 |
| 47 | Follow an organization's Page from the Page itself | W | GAP | REV. Blocker: no `/company/` pattern. `follow_company`'s own `residue` names the slug-vs-numeric-id gap |
| 48 | Unfollow an organization's Page | W | **COVERED-UNFIRED** | `linkedin_unfollow_company`, by numeric company id off Manage Pages. REV in LinkedIn, NOT-REV here |
| 49 | Follow a skills Page | W | GAP | REV |
| 50 | Follow a company or school via an off-site Follow button | W | GAP | REV. Off-platform |
| 51 | Mute a company | W | GAP | REV. `mute` 0 hits |
| 52 | View the list of Pages you follow | R | **COVERED-PROVEN** | `linkedin_followed_companies`, 2 live readings, PASS |
| 53 | View a Page's follower count | R | GAP | No `/company/` |
| 54 | View how many of your connections follow a Page | R | GAP | No `/company/` |
| 55 | Subscribe to a newsletter | W | GAP | REV. `newsletter` 0 hits |
| 56 | Unsubscribe from a newsletter | W | GAP | REV |
| 57 | View the newsletters you subscribe to | R | GAP | |
| 58 | Unsubscribe from newsletter emails while staying subscribed on the feed | W | GAP | REV |
| 59 | Follow a hashtag | W | GAP | REV. `hashtag` 0 hits in the package. **HC page 404'd -- see 9.2** |
| 60 | Unfollow a hashtag | W | GAP | REV. Same |
| 61 | View your followed hashtags | R | GAP | Same |
| 62 | Follow topics from the My Network page | W | EXCLUDED-RULED | R1 |
| 63 | Join a LinkedIn group | W | GAP | REV |
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
| 76 | Copy your personal Follow link for use off LinkedIn | R | GAP |
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
| 101 | List an organization's employees via its employee count | R | GAP | No `/company/` |
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
| 105 | Import contacts from your mobile address book | W | GAP | Mobile-only flow; not a page this server can drive |
| 106 | Import your Gmail contacts | W | GAP | OAuth flow |
| 107 | Choose which device contacts to upload instead of all | W | GAP | |
| 108 | Select or deselect the connection recommendations an import produces | W | GAP | |
| 109 | Send connection requests to the imported contacts you selected | W | GAP | **NOT-REV, and it is the highest-blast-radius row in the census** -- one confirmation sends many invitations |
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
| 118 | Read the endorsement counts on your own skills | R | GAP | **Costed at zero extra page loads and never built.** `_audit/2026-08-22-parity-linkedin.md:18`: "the `/details/skills/` page is *already loaded* by `linkedin_my_profile(include_skills=True)`; counts are dropped today. **0 extra page loads.** Smallest real win left" |

### K. Recommendations (10) -- all EXCLUDED-RULED under R3

| # | capability | R/W |
|---|---|---|
| 119 | Request a recommendation from a 1st-degree connection | W |
| 120 | Write and send a recommendation for a 1st-degree connection | W |
| 121 | Accept a received recommendation onto your profile | W |
| 122 | Dismiss a recommendation you received | W |
| 123 | Ask for a revision of a recommendation you received | W |
| 124 | Revise a recommendation you have given | W |
| 125 | Delete a recommendation you have sent | W (also R5) |
| 126 | Hide or unhide a recommendation you received | W |
| 127 | Set the visibility of a recommendation you have given | W |
| 128 | Decline a recommendation request someone sent you | W |

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
| 132 | Switch between Search appearances and Who viewed your profile | R | GAP | Search appearances are never read |
| 133 | Filter your profile-viewer data (Premium) | R | GAP | **The page is already open** -- see 8.1 |
| 134 | See notable or interesting viewers (Premium) | R | GAP | Same |
| 135 | See the weekly viewer trend graph (Premium) | R | GAP | Same |
| 136 | See top locations, industries and companies of your viewers (Premium) | R | GAP | Same |
| 137 | Set your profile viewing option to "Your name and headline" | W | EXCLUDED-RULED | R11 |
| 138 | Set your profile viewing option to private characteristics | W | EXCLUDED-RULED | R11 |
| 139 | Set your profile viewing option to private mode | W | EXCLUDED-RULED | R11. **Going anonymous costs him rows 129-130** -- LinkedIn withdraws your own viewer list while you browse privately |
| 140 | Unsubscribe from Who's-viewed-your-profile emails | W | EXCLUDED-RULED | R11 |

### M. Blocking, reporting, muting (14)

| # | capability | R/W | state | note |
|---|---|---|---|---|
| 141 | Block a member | W | EXCLUDED-RULED | R4 -- initiated from the member's profile. NOT-REV in practice: unblocking carries a LinkedIn cooldown before you can re-block |
| 142 | Unblock a member | W | EXCLUDED-RULED | R11 -- the blocked list is a settings page |
| 143 | See the list of members you have blocked | R | EXCLUDED-RULED | R11 |
| 144 | Report a member's profile | W | EXCLUDED-RULED | R4. NOT-REV |
| 145 | Report a fake or impersonating profile | W | EXCLUDED-RULED | R4. NOT-REV |
| 146 | Report inaccurate information on another member's profile | W | EXCLUDED-RULED | R4. NOT-REV |
| 147 | Report a profile video | W | EXCLUDED-RULED | R4. NOT-REV |
| 148 | Report a post or a comment in your feed | W | GAP | NOT-REV. Blocker: the feed-item permalink is readable; its overflow menu has never been opened |
| 149 | Report a message | W | GAP | NOT-REV. Surface owned by the messaging census slice |
| 150 | Report a whole conversation thread | W | GAP | NOT-REV. Messaging slice |
| 151 | Mark a system-flagged message as safe instead of reporting it | W | GAP | Messaging slice |
| 152 | Report harassment or a safety concern | W | GAP | NOT-REV. A Help Center form, off the product surface |
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
| 155 | Message a 1st-degree connection | W | **COVERED-UNFIRED (RAN-AND-REFUSED)** | `linkedin_send_message`. NOT-REV. Fired live and refused; see 8.3 |
| 156 | Send an InMail to a member outside your network | W | EXCLUDED-RULED | R9 -- four written rulings. NOT-REV |
| 157 | View your available InMail credits | R | EXCLUDED-RULED | R9. The `premium` census key was added 2026-09-01 to ask exactly this and settled that the balance is not on the composer |
| 158 | Send an Open Profile message without spending an InMail | W | EXCLUDED-RULED | R9. NOT-REV |
| 159 | Enable or disable Open Profile on your own profile | W | EXCLUDED-RULED | R11. REV |
| 160 | Send, receive and manage message requests | W | GAP | Messaging slice |

### O. Page-admin capabilities -- counted separately (9, all GAP)

He does not administer a Page, so none of these is a capability he currently
has. All nine are GAP: no tool, and no written reason.

| # | capability | R/W |
|---|---|---|
| A1 | Notify employees of a Page post | W |
| A2 | Follow another organization's Page on behalf of your Page | W |
| A3 | View the Pages your Page follows | R |
| A4 | Invite connections to follow a Page you manage | W |
| A5 | View your Page's invitation credit balance | R |
| A6 | Build a Page Follow button for your organization's website | W |
| A7 | Turn on automatic invitations to content engagers (Premium) | W |
| A8 | Turn off automatic invitations (Premium) | W |
| A9 | Invite followers of similar Pages to follow your Page (Premium) | W |

---

## 5. THE 73 GAPS: WHAT EACH FAMILY WOULD TAKE

A shape, not a design. Reversibility is stated because it dominates this slice.

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
server for exactly three of 160 capabilities, and all three are reads.**

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

## 8. FOUR THINGS THIS CENSUS FOUND THAT ARE NOT ROWS

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
| **24 linked-but-unwalked pages** in the following cluster | Link budget | Enumerated in `_audit/_scratch/_census-hc-following.md` |

### 9.3 NOT WALKED AT ALL -- deliberate scope calls, listed so they are visible

| area | why it was left | risk it carries |
|---|---|---|
| **LinkedIn Groups help tree** | Only join/leave were harvested, via "alternatives to inviting". The Groups topic was never opened | Group member directories, group messaging and group invitations are a people surface and are **entirely uncounted**. If the lead wants groups in the denominator, this needs a walk |
| **LinkedIn Events help tree** | Touched only through the invitation-type filter | Event attendee lists and event invitations are uncounted |
| **Sales Navigator and Recruiter help centers** | Separate products; the free-account boundary was taken from `linkedin.com/help/linkedin` only | The brief asked for "Sales-Navigator-adjacent features available on a normal account". What is answered is what the CONSUMER help center says a free account can do. Anything Sales Navigator exposes that leaks into the consumer product is not counted |
| **Company Page admin tree** | 9 rows harvested opportunistically, not exhaustively | The admin block is a sample, not a census |
| **Mobile-only network surfaces** | Not walked separately | Contact sync (rows 105-107) is mobile-first; its desktop equivalents may differ |
| **Localised / India-specific variants** | Not walked | Unknown |

### 9.4 One number LinkedIn does not state

**The weekly invitation cap has NO Help Center number.** The commonly cited
100/200-per-week figures trace only to member-written Pulse posts, not to any
Help Center page walked. This matters because `send_invitation`'s own `residue`
(`writes.py:1533`) leans on the restriction being real:

```
"There is a second, quieter "
"cost: LinkedIn restricts accounts whose invitations are "
"frequently ignored or marked 'I don't know this person', so this "
"is the one action here whose repetition has a consequence for "
"the account itself. Nothing readable reports that limit."
```

The last sentence is confirmed by this walk from the outside as well: **nothing
LinkedIn publishes reports that limit either.** LinkedIn does state the network
size limit (30,000 connections), invitation expiry (six months), reminder count
(two), and the post-withdrawal cooldown (up to three weeks).

Two Help Center self-contradictions were found and are recorded rather than
resolved: the personalized-note allowance reads three per month on `a563153`
and five per month plus a 300-character Premium limit on `a6239760`.

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

## 11. PROVENANCE

Repo state: branch `master`, working tree as of 2026-09-03 15:10. Line numbers
are as of that tree.

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

No LinkedIn account was accessed at any point by this slice or by any of its
children. No tracked file was modified. Nothing was committed.
