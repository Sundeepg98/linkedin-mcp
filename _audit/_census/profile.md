# CENSUS SLICE: PROFILE, IDENTITY, SETTINGS AND PRIVACY

Written 2026-09-03. Read-only. No LinkedIn account was touched: no browser, no
session, no page load, no MCP tool call. The taxonomy was imported by walking
LinkedIn's PUBLIC Help Center; the coverage verdicts come from the repository at
`D:\Sundeep\projects\job-hunting\mcp-servers\linkedin`. Nothing was committed
and no tracked file was edited.

---

## 1. COUNTS

    CAPABILITIES ENUMERATED, IN SCOPE, MAPPED       240

      COVERED-PROVEN                                 19
      COVERED-UNFIRED                                 7
      EXCLUDED-RULED                                105
      GAP                                           109

Set aside BEFORE mapping, and counted so none of them reads as a zero:

    Help Center rows that DOCUMENT behaviour rather than name a
      control he can exercise (troubleshooting, FAQ, "how X works")   101
    DUPLICATES across the three walks (Open To Work, verification,
      public-profile visibility and resumes are each filed by
      LinkedIn under two or three different topics)                  102
    NOT-ENTITLED -- his tier or his country cannot do it either        13
    RETIRED OR PAUSED BY LINKEDIN -- no longer a capability              7
    OWNED BY A SIBLING CENSUS SLICE (jobs, network, messaging)          14
    ------------------------------------------------------------------
    RAW HELP CENTER ROWS HARVESTED                                    477
      (153 profile sections + 145 settings/privacy + 179 job-seeking
       identity / creator / premium)

**Two numbers carry the slice.**

**COVERED-PROVEN is 19 of 240, and every one of the 19 is a READ.** Not one
write in this slice has ever completed against live LinkedIn. Two tools here can
write: `linkedin_update_setting` has never fired at all, and
`linkedin_update_profile_field` fired once and failed before it navigated.

**72 of the 105 EXCLUDED-RULED come from ONE ruling** -- that the settings
family is admitted by name or not at all. An EXCLUDED total of 105 that is
really "one argument plus thirty-three" is a different picture from 105
decisions, and section 6 splits it out rather than letting the total imply the
latter.

---

## 2. HOW A CAPABILITY WAS ASSIGNED A STATE

    COVERED-PROVEN     a tool exists AND an audit records it firing live and
                       returning what it claims. Cited per row.
    COVERED-UNFIRED    a tool exists and would not refuse, and nothing records
                       it running live.
    EXCLUDED-RULED     no tool, and a written passage in this repo gives a
                       reason that BEARS ON THIS CAPABILITY -- naming it, or
                       naming an address family or act-class containing it.
    GAP                no tool and no such passage.

**The line between EXCLUDED-RULED and GAP, stated because it decides 214 rows.**
`readonly._ALLOWED_URL_PATTERNS` is closed by default: every LinkedIn address
not on it is already refused. So "the allowlist refuses it" is NOT a reason --
it is the silence this census exists to measure. A row is EXCLUDED-RULED only
where something was WRITTEN: an entry on `readonly._FORBIDDEN_URL_SUBSTRINGS`
(documented as a second, independent gate, each entry carrying an argument), a
key in `writes.PERMANENTLY_FORBIDDEN`, a `WriteSpec` that refuses in its own
words, or an audit passage measuring the capability unreachable. Everything a
general mechanism merely happens to block is a **GAP with a NAMED BLOCKER** --
recorded in the row so nobody reads "GAP" as "cheap", but not laundered into a
decision. `set_input_files` being unsanctioned is a mechanism; nobody has ever
written a sentence about uploading a profile photo.

**Read and write are separate rows where their states differ.** Nine intro
fields are readable and unwritable, so they appear twice, tagged R and W. Where
the states agree, one row carries both.

---

## 3. THE SERVER SURFACE THIS SLICE IS MEASURED AGAINST

35 tools in `linkedin_server/server.py`. **Nine touch this slice.**
`writes.PERFORMABLE` holds 12 actions; **two are here**. A thirteenth spec,
`set_open_to_work`, exists and is deliberately NOT performable.

| tool | what it does here | live-fire |
|---|---|---|
| `linkedin_my_profile` | name, headline, location, About, public identifier, Open To Work + audience, which sections rendered, and on a second page load the skills list | FIRED-SUCCEEDED. Errored on the first live run 2026-08-21 (`mcp-servers/_audit/2026-08-21-linkedin-parse-fix.md:1`), fixed, read live since; the skills half re-measured 2026-09-03 -- 20 skill cards, all carrying text (`server.py:1745`) |
| `linkedin_profile_editor_fields` | control LABELS inside `/in/me/edit/intro/`, never values | FIRED-SUCCEEDED twice: 23 controls 2026-08-31 (`_audit/2026-08-31-linkedin-perform.md:370`), 17 controls 2026-09-02 (`:2925`) |
| `linkedin_profile_editor_values` | what those controls HOLD -- the restore path for an edit | FIRED-SUCCEEDED 2026-09-02 (`_audit/2026-08-31-linkedin-perform.md:2925`) |
| `linkedin_update_profile_field` | change ONE intro-editor field, behind the two-call gate | **FIRED-FAILED.** Shipped `a540461` 2026-09-02, could not navigate once -- three independent fatal defects, `NAVIGATIONS ATTEMPTED: []` -- while still minting a live `confirm_token` off a real preview he confirmed. Repaired `ea5354d` the same day. **No successful edit is recorded anywhere, before or after.** |
| `linkedin_update_setting` | dark mode: read the three-state radio group, then change it | READ FIRED-SUCCEEDED -- six readings across two days and three builds agree on every count: 20 controls, ZERO forms, 16 links, no dialogs, no redirect, exactly one of three radios checked. **WRITE NEVER FIRED.** |
| `linkedin_surface_census` | control counts on `profile`, `profile_edit_intro`, `settings`, `settings_dark_mode`, `premium` (plus six keys outside this slice) | FIRED-SUCCEEDED on all five of this slice's keys. Readings: profile 4, profile_edit_intro 4, settings 3, settings_dark_mode 2 (`_audit/2026-08-31-linkedin-finish.md:275-279`); premium 3, the third on 2026-09-01 (`_audit/2026-08-31-linkedin-perform.md:2035`) |
| `linkedin_who_viewed_me` | Who's Viewed Your Profile; 365 days on his Premium Career account | FIRED-SUCCEEDED -- "Now 10 rows, 10 distinct names, verified live" (`mcp-servers/_audit/2026-08-21-linkedin-parse-fix.md:5`), corroborated twice more |
| `linkedin_my_activity_items` | his own activity rail -- the profile Activity section | FIRED-SUCCEEDED, and measured UNRELIABLE: 233 controls on one reading, 67 on another, same session, minutes apart |
| `linkedin_server_info` | reports which actions are performable | not a LinkedIn surface |

---

## 4. THE TABLE

R = read, W = write.

### A. Intro / top card -- the ONE profile editor this server can address (29)

`/in/me/edit/intro/` is admitted by an EXACT-url exemption past the `/edit/`
forbidden entry. Its live control list was 23 on 2026-08-31 and 17 on
2026-09-02 -- **a different set, not a subset**. Six of the 17 can be aimed at
by name; three cannot, for two different measured reasons.

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| A1 | Headline | R | COVERED-PROVEN | `my_profile` returns it; `profile_editor_values` reads it verbatim |
| A2 | Headline | W | EXCLUDED-RULED | measured unaimable -- *"`headline` because its name IS its content"*. The control is a `div[role=textbox]` with no aria-label, no label-for and no title, so its accessible name resolves to its own text; the reader now returns `<content>` and withholds it |
| A3 | First name | R | COVERED-PROVEN | *"Their values read perfectly -- the value reader returned both"* |
| A4 | First name | W | EXCLUDED-RULED | *"The first-name and last-name inputs have NO ACCESSIBLE NAME AND ARE `required: true` ... they cannot be addressed by name. That is the exact inverse of the problem the ruling was written to solve"* (`_audit/2026-08-31-linkedin-perform.md:2960`) |
| A5 | Last name | R | COVERED-PROVEN | same live reading |
| A6 | Last name | W | EXCLUDED-RULED | same measurement |
| A7 | Additional name (former / maiden / nickname) | R | COVERED-PROVEN | read live; value is the empty string |
| A8 | Additional name | W | COVERED-UNFIRED | aimable by `label-for`; the gate would not refuse it; never fired |
| A9 | Additional-name visibility (4 tiers) | W | GAP | not among the 17 controls read; blocker: unobserved control |
| A10 | Country / Region | R | COVERED-PROVEN | read live |
| A11 | Country / Region | W | COVERED-UNFIRED | aimable by `aria-label` |
| A12 | City | R | COVERED-PROVEN | read live |
| A13 | City | W | COVERED-UNFIRED | aimable by `aria-label` |
| A14 | Postal code | W | GAP | not among the 17 controls |
| A15 | Location display choice | W | GAP | not among the 17 controls |
| A16 | Industry | R | COVERED-PROVEN | read live |
| A17 | Industry | W | COVERED-UNFIRED | aimable by `aria-label` |
| A18 | Pronouns | R | COVERED-PROVEN | read live; option text returned |
| A19 | Pronouns | W | COVERED-UNFIRED | a `select`; `select_option` is the 4th entry on `SANCTIONED_MUTATIONS` |
| A20 | Education shown in intro | R | COVERED-PROVEN | read live; option text returned |
| A21 | Education shown in intro | W | COVERED-UNFIRED | a `select`, same route |
| A22 | Current / primary position shown in intro | W | GAP | no position control among the 17. The 2026-08-31 reading had `School*` and `Month`; both were gone by 2026-09-02 |
| A23 | Name pronunciation audio | W | GAP | mobile app only -- desktop can only delete it. A browser-driven server structurally cannot record it |
| A24 | ID name as additional name | W | GAP | requires an identity verification first (block K) |
| A25 | Contact info panel | R | GAP | the control `Edit contact info` WAS among the 17 read on 2026-09-02; the panel behind it has never been opened |
| A26 | Websites on profile (up to 3) | W | GAP | inside that unopened panel |
| A27 | Phone / address / IM on profile | W | GAP | same |
| A28 | Email address shown on profile | W | GAP | same |
| A29 | Birthday and birthday visibility | W | GAP | same |

### B. Photo, banner, frames, badges (10)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| B1 | Whether a profile photo exists | R | COVERED-PROVEN | `my_profile.completeness.has_photo`, off the topcard images |
| B2 | Profile photo add / change / delete | W | GAP | blocker: `set_input_files` is on `readonly._MUTATION_CALL_PATTERNS` and on NO entry of `SANCTIONED_MUTATIONS`. Nothing in this repo has ever considered photo upload |
| B3 | Profile photo crop / filter / rotate / reposition | W | GAP | same blocker, plus canvas interaction nobody has measured |
| B4 | Profile photo visibility audience (4 tiers) | W | GAP | on `/public-profile/settings`, which no forbidden substring catches AS THE HELP CENTER SPELLS IT -- `"/settings/"` needs a trailing slash and the cited path has none, so whether the entry catches this address depends on a trailing slash nobody has observed -- and no allowlist pattern admits it |
| B5 | Background / banner image add / change / delete | W | GAP | `set_input_files` blocker |
| B6 | #OpenToWork photo frame apply / remove | W | EXCLUDED-RULED | the residue clause of the `set_open_to_work` spec: *"Switching to All LinkedIn members draws a green #OpenToWork frame on the photo that a current employer and his colleagues can see. Taking it down later removes the frame; it does not un-see it."* |
| B7 | #Hiring photo frame apply / remove | W | GAP | the `Open to` menu on his account resolves to exactly three items -- Hiring, Providing services, Finding volunteer opportunities -- measured across all five profile captures. Nothing acts on any of them |
| B8 | Top Voice badge show / hide | W | GAP | no tool, no reason |
| B9 | Premium profile badge show / hide | W | GAP | no tool, no reason |
| B10 | Open Profile setting (who may message without connecting) | W | GAP | no tool, no reason |

### C. Public profile and vanity URL (8)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| C1 | Own public profile URL / slug | R | COVERED-PROVEN | `my_profile.public_identifier`, parsed from the landed url |
| C2 | Customise the public profile URL | W | GAP | `/public-profile/settings`; no tool, no reason |
| C3 | Public profile visibility master switch | W | GAP | same page |
| C4 | Per-section public visibility toggles | W | GAP | same page |
| C5 | Search-engine visibility of the public profile | W | GAP | same page |
| C6 | Unlink a prior public URL | W | GAP | same page |
| C7 | Guest controls / cookie consent | W | EXCLUDED-RULED | `/psettings/guest-controls`; `"/psettings/"` is a forbidden substring |
| C8 | Save profile as PDF | R | GAP | a download, not a page read; nothing in this repo handles a download |

### D. Profile body sections (28)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| D1 | About text | R | COVERED-PROVEN | `my_profile.about`, trimmed to 1200 chars |
| D2 | About text | W | GAP | its editor is `/in/<member>/edit/forms/summary/new/`, named in the `update_profile_field` docstring as measured to exist, and refused by `/edit/`. The exemption table admits ONE url past that entry and this is not it |
| D3 | Which profile sections rendered | R | COVERED-PROVEN | `completeness.sections_present` / `sections_not_rendered`, with the tool's own rule that absent means UNKNOWN, never zero |
| D4 | Experience entries | R | GAP | `/in/<member>/details/experience/` **IS on the read allowlist and nothing navigates to it.** `my_profile` hands back the url in `details_urls` and reports `experience_entries: None` |
| D5 | Add / edit / delete a position | W | GAP | `/edit/` blocker |
| D6 | Employment type, skills, media on a position | W | GAP | `/edit/` plus `set_input_files` |
| D7 | Notify network of a job change | W | GAP | the standing broadcast setting is O-block |
| D8 | Reorder current positions | W | GAP | `/edit/` blocker |
| D9 | Career break | W | GAP | `/edit/` blocker |
| D10 | Education entries | R | GAP | `/in/<member>/details/education/` on the allowlist, unvisited -- same shape as D4 |
| D11 | Add / edit / delete education | W | GAP | `/edit/` blocker |
| D12 | Reorder education | W | GAP | `/edit/` blocker |
| D13 | Licenses and certifications | W | GAP | `/edit/`; and its Help Center article `answer/a567169` is itself HTTP 404, so the form fields are unconfirmed on BOTH sides |
| D14 | Courses | W | GAP | `/edit/`; no dedicated Help Center article exists |
| D15 | Projects | W | GAP | same |
| D16 | Publications | W | GAP | same |
| D17 | Patents | W | GAP | same |
| D18 | Honors and awards | W | GAP | same |
| D19 | Test scores | W | GAP | same |
| D20 | Languages | W | GAP | same |
| D21 | Organizations | W | GAP | same |
| D22 | Volunteer experience | W | GAP | same |
| D23 | Causes you care about | W | GAP | `/edit/` blocker |
| D24 | Open to volunteering block | W | GAP | one of the three items the `Open to` menu actually resolves to; nothing acts on it |
| D25 | "Add profile section" menu contents | R | GAP | never opened |
| D26 | Profile level meter / All-Star | R | EXCLUDED-RULED | `my_profile` docstring: *"LinkedIn's own profile-strength meter is not exposed here, so this server does not report one. What it reports is derived and labelled as such."* |
| D27 | Create / edit / delete a secondary-language profile | W | GAP | no tool, no reason |
| D28 | View a profile in multiple languages | R | GAP | no tool, no reason |

### E. Skills and endorsements (8)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| E1 | Own skills list | R | COVERED-PROVEN | 20 skill cards off `/in/me/details/skills/`, live 2026-09-03 |
| E2 | Add / remove skills | W | GAP | `/edit/` blocker |
| E3 | Reorder skills / pin top skills | W | GAP | `/edit/`; `drag_to` is an unsanctioned mutation class |
| E4 | Endorse another member's skills | W | EXCLUDED-RULED | `PERMANENTLY_FORBIDDEN["endorse_or_recommend"]`: *"zero endorse controls across 13 tracked fixtures ... and zero among the 222 controls read live on his own profile on 2026-08-30. You cannot endorse yourself, so the only surface that would carry the control is a THIRD PARTY'S PROFILE -- and loading one leaves them a durable record ... IMPOSSIBLE AS SPECIFIED, not unwanted"* |
| E5 | Remove an endorsement you gave | W | EXCLUDED-RULED | same key, plus `PERMANENTLY_FORBIDDEN["delete_or_withdraw_anything"]` |
| E6 | Hide / show an endorsement received | W | GAP | blocker: `"/endorse"` is a forbidden substring. **The written reason does not reach this act** -- `endorse_or_recommend` argues about making a statement about another person, and this is housekeeping on his own profile |
| E7 | Endorsements received | R | GAP | same blocker, same absence of a reason |
| E8 | Opt out of endorsements entirely | W | EXCLUDED-RULED | a settings-family toggle (`a551156`); see section 6 |

### F. Recommendations (9)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| F1 | Recommendations received | R | GAP | no tool, no reason |
| F2 | Request a recommendation | W | GAP | no tool, no reason; it reaches another member |
| F3 | Give a recommendation | W | EXCLUDED-RULED | named in the `PERMANENTLY_FORBIDDEN` key `endorse_or_recommend`. **NAMED BUT UNARGUED** -- finding 7.4 |
| F4 | Revise a recommendation you gave | W | EXCLUDED-RULED | same key, same caveat |
| F5 | Delete a recommendation you sent | W | EXCLUDED-RULED | `delete_or_withdraw_anything`: *"destruction is not a write this design covers, at any confirm level"*; `/delete` is also forbidden |
| F6 | Accept or dismiss a recommendation received | W | GAP | no tool, no reason |
| F7 | Ask for a revision of one received | W | GAP | no tool, no reason |
| F8 | Decline a requested recommendation | W | GAP | no tool, no reason |
| F9 | Hide / unhide recommendations on the profile | W | GAP | no tool, no reason |

### G. Featured and Activity sections (7)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| G1 | Own activity items | R | COVERED-PROVEN, WITH A MEASURED RELIABILITY DEFECT | `my_activity_items` reads the rail, which returned 233 controls on one reading and 67 on another in the same session. The spec's own words: *"A check that answers nothing on some readings it can take is not a verification."* |
| G2 | Activity section default view | W | GAP | no tool, no reason |
| G3 | Featured section: add work samples | W | GAP | `set_input_files` blocker |
| G4 | Featured: reorder / edit / remove | W | GAP | `/edit/` plus `drag_to` |
| G5 | Feature content pulled from other profile sections | W | GAP | `/edit/` blocker |
| G6 | Per-post analytics | R | GAP | no tool, no reason. Two impressions links were counted on an item permalink 2026-09-01 and never followed |
| G7 | Profile search appearances | R | GAP | no tool, no reason |

### H. Services / "Providing services" (11)

A Service Page is a profile-attached identity surface open to every member, so
it is in scope. **All eleven are GAPs: nothing in this repo mentions a Service
Page in any capacity.**

| # | capability | R/W | state | blocker |
|---|---|---|---|---|
| H1 | Create a Service Page / add services | W | GAP | one of the three items the `Open to` menu resolves to; never actioned |
| H2 | Service categories and specific services | W | GAP | no tool, no reason |
| H3 | Service Page About / expertise text | W | GAP | typing -- `fill` IS sanctioned, so this is a surface gap, not a class gap |
| H4 | Work location and remote availability | W | GAP | no tool, no reason |
| H5 | Starting rate or contact-for-pricing | W | GAP | no tool, no reason |
| H6 | Edit the Service Page | W | GAP | no tool, no reason |
| H7 | Unpublish the Service Page | W | GAP | no tool, no reason |
| H8 | Link / unlink the Service Page to a Company Page | W | GAP | no tool, no reason |
| H9 | Request service reviews (up to 20 invitations) | W | GAP | reaches real people; no tool, no reason |
| H10 | Turn off / manage services reviews | W | GAP | no tool, no reason |
| H11 | "Providing services" section as rendered on the profile | R | GAP | no tool, no reason |

### I. Open To Work and job-seeking identity (16)

**The block where the repo argues most and can act least.** The state is read;
the editor has never been loaded, and its absence is a measurement rather than
an admission. From `writes.py`, `set_open_to_work.reversibility_procedure`:

> *"THE ABSENCE OF A URL IS NOW A MEASUREMENT RATHER THAN AN ADMISSION, taken
> 2026-08-24: 237 distinct urls and 37 payload paths were enumerated across all
> five profile captures and ZERO reach an open-to-work editor, a job-preferences
> page or a career-interests page; the strings 'opentowork' and 'open-to-work'
> occur zero times anywhere. The editor is not url-addressed AT ALL -- its
> screens are addressed by an internal screen id, and its entry control fires a
> request whose own name is saveAndFetchNextStep. So the one click that would
> first REVEAL the editor is also the first click that could CHANGE it, which is
> why no capture of it may be taken except with him watching."*

`opentowork` and `open-to-work` are also both forbidden substrings, and the spec
carries `url_template=None`, so `mint` refuses it a grant at ISSUE -- no
`confirm_token` for this action can exist, for anyone.

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| I1 | Open To Work on/off AND its current audience | R | COVERED-PROVEN | `my_profile.open_to_work`, off the topcard at no extra page load, at BOTH hydration states. LinkedIn prints the audience verbatim ("Open to work - Recruiters only"); confirmed against the frozen fixtures and again live 2026-08-23 |
| I2 | Turn Open To Work on or off | W | EXCLUDED-RULED | the quote above |
| I3 | Change the audience | W | EXCLUDED-RULED | same, plus the green-frame residue clause |
| I4 | OTW field: job titles | W | EXCLUDED-RULED | editor never loaded |
| I5 | OTW field: locations | W | EXCLUDED-RULED | same |
| I6 | OTW field: location / workplace types | W | EXCLUDED-RULED | same |
| I7 | OTW field: employment types | W | EXCLUDED-RULED | same |
| I8 | OTW field: start date | W | EXCLUDED-RULED | same |
| I9 | OTW field: notice period (INDIA ONLY -- applies to him) | W | EXCLUDED-RULED | same |
| I10 | OTW field: expected annual salary (INDIA ONLY -- applies to him) | W | EXCLUDED-RULED | same |
| I11 | Delete the Open To Work card | W | EXCLUDED-RULED | same, plus `delete_or_withdraw_anything` |
| I12 | Job preferences / career-interests page | W | EXCLUDED-RULED | measured: zero of 237 urls reach one |
| I13 | Minimum pay preference | W | GAP | lives on that same unreachable page and is named nowhere in this repo |
| I14 | Signal interest in working for a company | W | GAP | no tool, no reason |
| I15 | Remove interest in working for a company | W | GAP | no tool, no reason |
| I16 | Share how you found your job | W | GAP | no tool, no reason |

### J. Open To Hiring (4)

| # | capability | R/W | state | blocker |
|---|---|---|---|---|
| J1 | Turn on #Hiring / share that you are hiring | W | GAP | the `Open to` menu item IS observed across five captures; nothing acts on it |
| J2 | #Hiring photo frame add / remove | W | GAP | same |
| J3 | Which job the #Hiring frame links to | W | GAP | same |
| J4 | Current #Hiring state | R | GAP | `my_profile` parses only the open-to-WORK line off the topcard |

### K. Verification and badges (10)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| K1 | Verifications section on the profile | R | GAP | `/mypreferences/d/verifications`. **Refused by the allowlist only -- no forbidden substring catches it.** Finding 7.1 |
| K2 | Identity verification via DigiLocker (India -- his route) | W | GAP | same address |
| K3 | Workplace verification by work email | W | GAP | same address |
| K4 | Workplace verification via Microsoft Entra Verified ID | W | GAP | same address |
| K5 | Workplace verification via a company LinkedIn Learning licence | W | GAP | same address |
| K6 | Phone number verification | W | GAP | same address |
| K7 | Remove a verification | W | EXCLUDED-RULED | `delete_or_withdraw_anything`, and `/delete` |
| K8 | Top Voice blue badge on the profile | R | GAP | no tool, no reason |
| K9 | Show / hide the Top Voice badge | W | GAP | no tool, no reason |
| K10 | Verification badge as it appears on job posts | R | GAP | no tool, no reason |

### L. Creator tools, followers and analytics (8)

Creator mode itself is RETIRED (see section 8); these are the capabilities that
survived it, which LinkedIn's Help Center now states are open to all members.

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| L1 | Creator analytics / audience analytics | R | GAP | no tool, no reason |
| L2 | Own follower count and follower list | R | GAP | the count IS read incidentally -- *"his profile reports 275 followers"* is quoted inside `publish_post.residue` -- and no tool returns it |
| L3 | Create / edit / delete a newsletter | W | GAP | no tool, no reason |
| L4 | Newsletter analytics | R | GAP | no tool, no reason |
| L5 | Host a LinkedIn Live | W | GAP | he clears the >150-follower gate at 275; no tool, no reason |
| L6 | Audio events | W | GAP | no tool, no reason; the Help Center article itself 404s |
| L7 | "Ideas for your next post" | R | GAP | no tool, no reason |
| L8 | Analytics and tools hub | R | GAP | no tool, no reason |

### M. Resumes and application documents (12)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| M1 | Upload a resume from Job Application Settings | W | EXCLUDED-RULED | `/jobs/application-settings/` contains `"/jobs/application"`, the FIRST entry on the forbidden-substring tuple. `set_input_files` is unsanctioned on top of that |
| M2 | Saved resumes list (4 most recent) | R | EXCLUDED-RULED | same address, same entry |
| M3 | Delete a saved resume | W | EXCLUDED-RULED | same address, plus `delete_or_withdraw_anything` and `/delete` |
| M4 | Download a saved resume | R | EXCLUDED-RULED | same address |
| M5 | View the resume used for a specific application | R | EXCLUDED-RULED | same address |
| M6 | Saved screening-question answers | R/W | EXCLUDED-RULED | same address |
| M7 | Opt out of saving job application data | W | EXCLUDED-RULED | same address |
| M8 | "Share resume data with recruiters" toggle | W | EXCLUDED-RULED | settings family (section 6) |
| M9 | Stored job applicant accounts | R/W | GAP | `/mypreferences/d/job-application-accounts` -- **caught by no forbidden substring.** `"/jobs/application"` does not match `job-application`. Finding 7.1 |
| M10 | Autofill for work emails | W | EXCLUDED-RULED | settings family |
| M11 | Resume Builder | R/W | GAP | no tool, no reason; entitlement unverified |
| M12 | Resume Tips (AI resume feedback) | R | GAP | no tool, no reason; entitlement unverified |

### N. Account preferences, sign-in and security (24)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| N1 | Dark mode current state | R | COVERED-PROVEN | six readings, two days, three builds: 20 controls, ZERO forms, 16 links, no dialogs, no redirect, exactly one of three radios checked |
| N2 | Dark mode change | W | COVERED-UNFIRED | in `PERFORMABLE`; verification is a fresh navigation and a re-read of all three radios. Never fired |
| N3 | Which settings sections exist (the index) | R | COVERED-PROVEN | census `settings`, 34 controls, live 2026-08-30, three readings |
| N4 | Two-step verification on / off | W | GAP | `/mypreferences/d/two-factor-authentication` -- **caught by no forbidden substring.** The most consequential uncaught address found. Finding 7.1 |
| N5-N22 | eighteen further settings-family controls: interface language, autoplay video, sound effects, showing others' photos, name/location/industry via settings, calendar sync, contact sync, subscriptions and payments, partners and services, Microsoft account link, mentions and tags permission, email addresses, phone numbers, change password, passkeys, where you're signed in, devices that remember your password, merge duplicate accounts | R/W | EXCLUDED-RULED | section 6 |
| N23 | Close (delete) account | W | EXCLUDED-RULED | `"/close-accounts"` was added to the forbidden tuple 2026-08-31 precisely because nothing else caught it, plus `delete_or_withdraw_anything` |
| N24 | Hibernate account | W | EXCLUDED-RULED | `"/hibernate-account"`, added the same day, same reason |

### O. Visibility and privacy (22)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| O1 | Who's Viewed Your Profile list | R | COVERED-PROVEN | 10 rows, 10 distinct names, verified live; 365 days back on Premium Career |
| O2 | De-anonymise a private-mode viewer | R | EXCLUDED-RULED | `PERMANENTLY_FORBIDDEN["deanonymise_a_viewer"]`: *"six of ten profile viewers chose anonymity; the row LinkedIn renders him is the whole of what he is entitled to"* |
| O3 | WVYP Premium insights and filters | R | GAP | no tool, no reason |
| O4 | Profile viewing options (his own browsing mode) | W | EXCLUDED-RULED | settings family |
| O5-O20 | sixteen further visibility toggles: public-profile edit via settings, contact-info and email visibility, connection-list visibility, who can see members you follow, who can follow you / make follow primary, representing your organization, Page owners exporting your data, discoverability by email, discoverability by phone, visibility for partners, off-LinkedIn visibility, active status, share profile updates with your network, visibility of shared posts, sharing public posts on and off LinkedIn, Page visit visibility | W | EXCLUDED-RULED | section 6 |
| O21 | Block / unblock a member | W | EXCLUDED-RULED | settings family; independently an act on another member's relationship |
| O22 | Whether a photo, banner or headline change notifies the network | R | GAP | the `update_profile_field` docstring states this as an UNMEASURED cost: *"LinkedIn notifies a network about some profile changes, which this server has not measured and would not control."* A named unknown, not a considered exclusion |

### P-R. Data privacy, advertising data, notification settings (34)

Thirty-two of the thirty-four resolve to a `/psettings/...`,
`/mypreferences/d/categories/...` or `/mypreferences/d/settings/...` address and
are EXCLUDED-RULED by the family ruling in section 6: data archive download,
manage personal data, data log, search history, salary data, demographic
information, research participation, GenAI training data, objection and access
forms, who can send invitations, network invitations, research invitations,
InMail opt-out, read receipts and typing indicators, message nudges, harmful
message detection, job-post email notifications, permitted services, the seven
advertising toggles, and the seven notification-channel controls.

The two that are not:

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| P1 | Mark notifications read | W | EXCLUDED-RULED | `PERMANENTLY_FORBIDDEN["mark_notifications_read"]`, on three independent grounds, the third being that *"the read tool ALREADY has the full effect -- opening the page clears the badge -- so a write here could only ever run after its own consequence had landed"* |
| P2 | Stop invitation emails to join LinkedIn | W | GAP | an unauthenticated opt-out form, not a settings page; no tool, no reason |

---

## 5. WHAT THE 109 GAPS WOULD TAKE

Reversibility matters more than difficulty here, because the asset at risk is
his professional identity. Grouped by build shape, counts summing to 109.

**5.1 -- Behind `/edit/` (32).**
`D2, D5-D9, D11-D23, E2, E3, G4, G5` plus the nine intro-adjacent rows `A9, A14,
A15, A22, A25-A29`.
Shape: one more EXACT-url exemption per editor, on the model of the single one
that already exists for `/in/me/edit/intro/`, plus a live control read per
editor. **Write, with a read as its precondition.** Reversible ONLY if the
previous value is captured first -- `profile_editor_values` does exactly that
for the intro editor and every other editor would need its own. The docstring's
own framing of the cost: *"An edit reverted an hour later was still live for an
hour."*

**5.2 -- Behind an unsanctioned mutation class (4).** `B2, B3, B5, G3`.
Shape: a fifth entry in `SANCTIONED_MUTATIONS` for `set_input_files` -- a larger
decision than a url, because that list is documented as the thing a reviewer
reads. Write. Reversible in STATE (a photo can be replaced) and **irreversible
in AUDIENCE**: a photo or banner change is broadcast to 275 followers before
anybody decides it was wrong.

**5.3 -- Reads whose door is already open (2).** `D4, D10`.
`/in/<member>/details/experience/` and `/details/education/` are ON the read
allowlist and nothing navigates to them; `my_profile` already hands the caller
both urls and reports `None` for both counts. **The cheapest group in this
census by a wide margin**: no boundary moves, no new permission, one harvest
function of exactly the shape as the skills read that already works. Read,
trivially reversible.

**5.4 -- `/mypreferences/d/<name>` addresses no denylist catches (8).**
`K1-K6` share one address; `M9`; `N4`.
Shape: one allowlist pattern per address -- the same cost `settings_dark_mode`
was. But see finding 7.1: the honest first move is not to admit them, it is to
decide whether they should be DENIED. Read, then write. **N4 is irreversible in
the worst direction**: turning 2FA off is a security downgrade, and turning it
on can lock the account out of the very browser session this server depends on.

**5.5 -- `/public-profile/settings` (6).** `B4, C2-C6`.
Shape: one allowlist pattern; also uncaught by any denylist. Write.
**C5 is irreversible in audience** -- once a profile is indexed by a search
engine, un-indexing it does not un-cache it.

**5.6 -- Surfaces nobody in this repo has ever named (57).**
`A23, A24, B7-B10, C8, D24, D25, D27, D28, E6, E7, F1, F2, F6-F9, G2, G6, G7,
H1-H11, I13-I16, J1-J4, K8-K10, L1-L8, M11, M12, O3, O22, P2`.
Shape: a surface census first, then a spec, then a gate -- the full path every
existing write took. Mixed read and write. The irreversible-in-audience ones,
named rather than lumped: **F2 and H9 send a request to a real person**; **H1-H8
publish a public Service Page under his name**; **J1-J3 tell a network he is
hiring**; **L3 and L5 broadcast**; **I14 tells a company's recruiters he wants
to work there**. The safely reversible ones are all reads: `C8, D25, D28, E7,
F1, G6, G7, H11, J4, K8, K10, L1, L2, L4, L7, L8, M12, O3, O22`.

---

## 6. THE ONE RULING THAT PRODUCES 72 OF THE 105 EXCLUSIONS

Every settings toggle in `C7, E8, M8, M10, N5-N22, O4-O21` and 32 of the 34
P-R rows resolves to an address on `readonly._FORBIDDEN_URL_SUBSTRINGS` --
`"/psettings/"`, `"/mypreferences/d/categories/"` or `"/settings/"`. **72
capabilities, one argument.** From `linkedin_update_setting`:

> *"ONE SETTING IS WRITABLE, AND ASKING ABOUT ANY OTHER LOADS NOTHING. The read
> allowlist admits exactly one page below the settings index, admitted BY NAME
> on the operator's ruling. ... READ THIS BEFORE ASKING FOR THE FAMILY TO BE
> OPENED. `Close and delete account` and `Hibernate account` are addresses in
> it. A permission written for the FAMILY would carry those with it, which is
> why a setting is admitted by name or not at all -- and it is why this tool
> shipping does NOT mean the next setting is a small step."*

That ruling is real, argued and correct, and this census does not dispute it.
What it insists on is the arithmetic: **no individual setting among those 72 has
ever been considered on its own merits.** The ruling says the family stays shut;
it does not say that "who can see your connections" or "email notification
frequency" was weighed and declined. If the operator asks tomorrow which
settings this server should read, the honest answer today is that nobody has an
opinion about 71 of them.

Split of the 105, so the total is legible:

    settings-family address ruling (ONE argument)                    72
    /jobs/application forbidden entry (M1-M7)                         7
    set_open_to_work spec, per field (I2-I12, B6)                    12
    PERMANENTLY_FORBIDDEN named keys
      (E4, E5, F3, F4, F5, K7, N23, N24, O2, P1)                     10
    intro-editor controls measured unaimable (A2, A4, A6)             3
    my_profile's own declaration (D26)                                1
    ---------------------------------------------------------------
                                                                    105

---

## 7. FINDINGS

### 7.1 -- Three live `/mypreferences/d/<name>` addresses are refused by the allowlist only, and one of them is two-step verification

`readonly._FORBIDDEN_URL_SUBSTRINGS` gained `"/close-accounts"` and
`"/hibernate-account"` on 2026-08-31, with this reasoning in the source:

> *"The settings audit assumed 'Close and delete account' and 'Hibernate
> account' ... were covered by the `/mypreferences/d/categories/` entry three
> lines up. THEY ARE NOT. ... The only thing that had ever refused them was the
> anchored allowlist. ... for the two worst addresses on the account there was
> no second gate at all."*

The Help Center names **three more addresses of exactly that shape**, and none
is caught by any entry on the tuple:

    /mypreferences/d/two-factor-authentication      (help article a1381088)
    /mypreferences/d/verifications                  (help article a1359065)
    /mypreferences/d/job-application-accounts       (help article a507642)

Checked by hand against all 23 forbidden substrings. `"/settings/"` needs a
trailing slash and these have none; `"/mypreferences/d/categories/"` needs the
`categories/` segment; `"/jobs/application"` does not match `job-application`.
The net refusal still holds -- the allowlist admits none of them -- which is the
exact sentence the 2026-08-31 entry used about the two it then fixed. **The fix
taken that day was per-address; the class it belongs to has three more members,
and one of them is the account's second authentication factor.**

This is the highest-value item in the slice and it is not a capability request.

### 7.2 -- The comment on `"/settings/"` says it catches nothing current. It catches five live addresses.

The source says:

> *"LinkedIn moved its settings to `/mypreferences/d/`, and the legacy address
> is `/psettings/` ... The only address the old entry ever caught is a
> `/settings/` LinkedIn no longer serves."*

The measurement behind that sentence was taken on the two INDEX urls,
`/mypreferences/d/` and `/psettings/`. Current Help Center articles name five
per-setting addresses in a third shape the entry does catch:

    /mypreferences/d/settings/discover-me-by-email-address
    /mypreferences/d/settings/discover-me-by-phone-number
    /mypreferences/d/settings/profile-visibility-for-partners
    /mypreferences/d/settings/data-export-by-page-admins
    /mypreferences/d/settings/data-for-ai-improvement

`"/settings/"` is doing real work today. Nothing needs to change except the
sentence, which currently tells the next reader the entry is dead weight -- and
the entry is exactly what makes those five EXCLUDED-RULED rather than GAP.
EVIDENCE CLASS: DERIVED. The paths come from a Help Center walk (article
`a548106`, read in full), not from a live LinkedIn page load, which this slice
was forbidden.

### 7.3 -- The Open To Work spec knows three audiences. LinkedIn documents four.

`set_open_to_work.audiences` enumerates `recruiters only`, `all linkedin
members` and `off`, and the spec states only ONE has ever been observed on this
account. Help Center article `a507508` documents a **"Visible only to you"**
state alongside those. The design already handles this correctly -- *"the reader
recognises the audience string it has met and refuses to interpret one it has
not"* -- so this cannot act wrongly. It is a fourth string the reader would
refuse, and knowing its name is cheaper than meeting it.

### 7.4 -- `endorse_or_recommend` names recommendations and argues only about endorsements

The key covers two acts. The reason under it, rewritten 2026-08-30, is entirely
a measurement of ENDORSE controls -- *"zero endorse controls across 13 tracked
fixtures ... zero among the 222 controls read live"* -- and says nothing about
recommendations, whose controls have never been counted. `F3` and `F4` are
therefore excluded by a key that names them and by a reason that does not reach
them. The old reason that DID reach them (*"a statement ABOUT ANOTHER PERSON,
which is not his to automate"*) was explicitly retired as policy on 2026-08-25.

### 7.5 -- The best-verified write in the package has never successfully written

`linkedin_update_profile_field` is described, in the live server's own MCP
instructions, as *"the only one here that can verify its own outcome by reading
the field back"*. Its complete firing record: shipped 2026-09-02 in `a540461`,
driven end to end, `NAVIGATIONS ATTEMPTED: []`, repaired the same day in
`ea5354d`, never driven again.

**The 2026-09-02 ship-and-repair is still not written into `_audit/` at all.**
It exists in a commit message, a test docstring
(`tests/test_a_performable_action_can_reach_its_control.py:25`), and the
untracked `_TEAM_LEAD_SUCCESSOR_BRIEF.md` at the repo root. Anyone reading
`_audit/` alone finds only the pre-ship refusal at
`_audit/2026-08-31-linkedin-perform.md:3436`, which says the action REFUSES --
true when written, false since.

### 7.6 -- The intro editor's control set changed completely in two days

23 controls on 2026-08-31, 17 on 2026-09-02, and *"a different set"*: `First
name*` and `Last name*` lost their accessible names entirely, `School*` and
`Month` vanished, `Pronouns` and `Education` appeared, and six new controls
including `Write with AI` arrived. **Every COVERED-UNFIRED row in block A rests
on a reading that is now a day old on a surface with a measured two-day
half-life.** The six aimable fields are aimable as of 2026-09-02, not as a
standing property.

### 7.7 -- Two of this slice's proven reads LAND outside the read boundary

Recorded by `_audit/2026-08-31-linkedin-finish.md:275-279` rather than found
here, and repeated because both landings are in this slice and neither is
visible from the tool's own output:

* `my_profile` and census `profile` request `/in/me/` and land on
  `/in/<member>/?isSelfProfile=true`, which **FAILS the allowlist**;
* census `settings` requests `/mypreferences/d/` and lands on
  `/mypreferences/d/categories/account`, which **HITS a forbidden substring**.

`assert_read_url` gates the REQUESTED url only and the landed url is never
re-checked, which is documented behaviour. The finish audit measures the
settings-page exposure as NIL. Both are boundary findings about reads that
succeeded, not read failures -- but they mean the `categories/` entry that
makes 72 rows EXCLUDED-RULED is, on one surface, a door this server is already
standing behind.

---

## 8. THE FOUR SET-ASIDE BUCKETS, ITEMISED

**NOT-ENTITLED (13)** -- his account is Premium Career, in India. These require a
tier, geography or role he does not have, so he cannot do them on LinkedIn
directly either and they are not part of the denominator: custom cover image
(USA only); cover-image slideshow (Premium Business / Sales Nav / Recruiter);
custom profile CTA button (same); "increase button visibility" toggle (same);
website link in the intro section (Premium Business); media on a Service Page
(Premium Business); Services Showcase with ratings (Premium Business); "Request
services" button across surfaces (Premium); identity verification via CLEAR
(US / Canada / Mexico); workplace verification via an active Recruiter licence;
voluntary self-identification demographic data (US only); LinkedIn Page
notification settings (Page admin); manage Page visit visibility settings
(Page admin).

**RETIRED OR PAUSED BY LINKEDIN (7)** -- measured from the Help Center, not
assumed: creator mode toggle (removed from profile Resources March 2024, article
`a5999182`; the old articles `a522537` and `a524035` are both 404); profile
hashtags / topics (removed February 2024); skill assessments (badges removed
from profiles during 2024, `a1690529`); Community Top Voice gold badge (retired
8 October 2024, `a6245087`); Professional sources (removed, data deleted);
educational-institution verification (paused for new applicants); Profinder Pro
provider matching.

**OWNED BY A SIBLING CENSUS SLICE (14)** -- follow / unfollow a company; follow /
unfollow a person; the connections graph and invitations; the messaging composer
and InMail send; the InMail credit balance as a spend gate; reading the
notifications list; job alerts; the job tracker; saved jobs; the apply flow;
groups followed; newsletters subscribed; schools followed; influencers followed.
Some of these are also profile-visible (the Interests section renders followed
companies, groups, newsletters and schools), so **the profile-rendered Interests
section is a genuine boundary between this slice and the network slice, and
neither claims it.**

**HELP-CENTER DOCUMENTATION (101)** -- rows across the three walks that explain
behaviour rather than name a control: troubleshooting pages ("photo will not
upload", "endorsement not appearing", "unable to block a member"), FAQs, and
"how X works" explainers ("why am I seeing ads", "understand message
indicators", "differences between profile appearances and profile views").
Dropped before mapping so the denominator counts things he can DO.

---

## 9. WHICH HELP CENTER AREAS WERE WALKED, AND WHICH WERE NOT

**WALKED** -- three parallel walks, 267 tool calls between them, public
`linkedin.com/help/linkedin/...` pages only, no login, no account-bearing page:

* topic `a64` "Your Profile" (55 articles listed), hub `a564064`, `a540837`
  "Add sections to your profile", and outward through every related link those
  carried
* topic `a149001` Settings; topic `a65` Data and Privacy; topic `a151002`
  Account Access. The six Settings sections are fixed by `a1337839`: Account
  preferences, Sign in and security, Visibility, Data privacy, Advertising data,
  Notifications
* Open To Work (`a507508`, `a510407`); Open To Hiring; Providing Services;
  creator tools (`a5999182`); resumes and documents; verification (`a1359065`
  and its seven method articles); Premium profile features

**NOT REACHED -- holes in the denominator, not zeroes:**

1. **Eight profile sections have NO dedicated Help Center article at all** --
   Courses, Projects, Publications, Patents, Test scores, Languages,
   Organizations, Volunteer experience. They are named on the hub page and
   nothing documents their fields. Rows D14-D22 are counted at SECTION
   granularity; their sub-fields are uncounted on both sides of the ledger.
2. **`answer/a567169` "Manage Licenses & certifications" is HTTP 404**, as is
   its legacy alias `44644`. D13 is recorded from the hub page only.
3. **The named notification-category list does not exist publicly.** `a1378534`
   and `a597801` were both read in full and neither enumerates the categories.
   Block R is counted at channel-and-page granularity, not per category. **The
   real number of notification toggles is larger than what this census counts
   and nobody outside LinkedIn can say by how much.**
4. **"Representing your organization and interests"** and **"Social, economic
   and workplace research"** have confirmed settings paths and no locatable
   article.
5. **"Content language", "message suggestions" and "focused inbox"** returned
   nothing; this census cannot confirm they exist as settings.
6. **Pronouns has no Help Center article** -- only LinkedIn Learning tutorials.
   A18 / A19 are enumerated from the LIVE control list this server read, not
   from LinkedIn's documentation.
7. **Audio events** -- three URLs 404'd (`a759884` twice, `a597255`, hub
   `a173033`). L6 rests on a search snippet quoting the page, not the page.
8. **No Help Center page in the profile subtree ever names a
   `/in/<vanity>/details/...` path.** Probed explicitly across seven articles.
   D4 and D10 are grounded in this repo's allowlist and in the live skills read,
   not in LinkedIn's documentation.
9. **About 60 of the 145 settings rows were read from a topic-tree listing or
   the help search index rather than from the article body.** Their titles and
   URLs are real; their descriptions are listing snippets. None of them changed
   a state assignment, because in every case the state was decided by the
   ADDRESS rather than by the description.
10. **Mobile-only surfaces were not separated systematically.** A23 (name
    pronunciation) and the calendar-sync row are flagged; there are probably
    others, and a browser-driven server cannot reach any of them.

---

## 10. TWO THINGS THIS CENSUS DID NOT ESTABLISH

1. **Whether the six aimable intro fields are still aimable.** The reading is
   from 2026-09-02, on a surface that changed completely in the two days before
   it. Settling this costs one `linkedin_profile_editor_fields` call and zero
   writes.
2. **Whether the three uncaught `/mypreferences/d/<name>` addresses in finding
   7.1 should be denied.** They are refused by the allowlist today, so this is a
   boundary decision rather than a measurement, and taking it requires no page
   load at all.
