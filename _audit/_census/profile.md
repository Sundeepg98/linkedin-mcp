# CENSUS SLICE: PROFILE, IDENTITY, SETTINGS AND PRIVACY

Written 2026-09-03. **REVISION 2** -- widened after the lead reported that Help
topic pages can render `0 articles` for products that exist, and after a fifth
state was added to the schema. What changed is recorded in section 11.

Read-only. No LinkedIn account was touched: no browser, no session, no page
load, no MCP tool call. The taxonomy was imported by walking LinkedIn's PUBLIC
Help Center and then, in a second pass, by SEARCHING FOR PRODUCT NAMES where a
topic index looked thin. The coverage verdicts come from the repository at
`D:\Sundeep\projects\job-hunting\mcp-servers\linkedin`. Nothing was committed and
no tracked file was edited.

---

## 1. COUNTS

    CAPABILITIES ENUMERATED, IN SCOPE, MAPPED       260

      COVERED-PROVEN                                 19
      COVERED-UNFIRED                                 7
      COVERED-CANNOT-DELIVER                          5
      EXCLUDED-RULED                                150
      GAP                                            79

Set aside BEFORE mapping, and counted so none of them reads as a zero:

    Help Center rows that DOCUMENT behaviour rather than name a
      control he can exercise (troubleshooting, FAQ, "how X works")   101
    DUPLICATES across the three primary walks                         102
    RECOVERY-PASS rows that confirmed or enriched a row already
      counted, rather than adding a capability                         40
    NOT-ENTITLED -- his tier or his country cannot do it either        13
    RETIRED OR PAUSED BY LINKEDIN -- no longer a capability              7
    OWNED BY A SIBLING CENSUS SLICE (jobs, network, messaging)         14
    ------------------------------------------------------------------
    RAW HELP CENTER ROWS HARVESTED                                    537
      three primary walks               477
      two product-name recovery passes   60

**Three numbers carry the slice.**

**COVERED-PROVEN is 19 of 260, and every one of the 19 is a READ.** Not one
write in this slice has ever completed against live LinkedIn.

**123 of the 150 EXCLUDED-RULED come from THREE address-family rulings**, not from
123 decisions: the settings family (93), the `/edit/` family (23) and
`/jobs/application` (7). Section 6 splits that out. The shape it reveals is the
real one: this server is bounded by three family refusals plus a handful of named
acts, and **not one of those 123 capabilities was weighed on its own merits.**

**The reported hazard did NOT reduce this denominator.** Every topic index this
slice relied on rendered a full article list -- `a64` 55, `a51` 26, `a153003` 49,
`a149001` 18, `a65` 40. The `0 articles` failure appears to be specific to Events
and LinkedIn Live rather than a general property of topic pages. The recovery
passes still added 20 capabilities, but they came from products with no topic
home at all, not from an index that rendered empty. Detail in section 10.

---

## 2. HOW A CAPABILITY WAS ASSIGNED A STATE

    COVERED-PROVEN          a tool exists AND an audit records it firing live
                            and returning what it claims. Cited per row.
    COVERED-UNFIRED         a tool exists and would not refuse, and nothing
                            records it running live.
    COVERED-CANNOT-DELIVER  a tool exists, it HAS fired live, and it cannot do
                            this thing. Filing these as UNFIRED would say
                            "nobody has tried", which inverts a measurement.
    EXCLUDED-RULED          no tool, and a written passage in this repo gives a
                            reason that BEARS ON THIS CAPABILITY -- naming it,
                            or naming an address family or act-class containing
                            it.
    GAP                     no tool and no such passage.

**The line between EXCLUDED-RULED and GAP, which decides 229 rows.**
`readonly._ALLOWED_URL_PATTERNS` is closed by default: every LinkedIn address not
on it is already refused. So "the allowlist refuses it" is NOT a reason -- it is
the silence this census exists to measure. A row is EXCLUDED-RULED only where
something was WRITTEN: an entry on `readonly._FORBIDDEN_URL_SUBSTRINGS` (each
entry carries an argument), a key in `writes.PERMANENTLY_FORBIDDEN`, a
`WriteSpec` refusing in its own words, or an audit passage measuring the
capability unreachable. Everything a general mechanism merely happens to block is
a **GAP with a NAMED BLOCKER** -- recorded so nobody reads "GAP" as "cheap", but
not laundered into a decision.

**The settings-family ruling is capability-level, not path-level.** It says a
setting is admitted BY NAME or not at all. That excludes every page below the
settings index whatever its URL spelling -- which is why finding 7.1, where six
of those URLs slip past the denylist, **changes no state in this census.** The
capability-level ruling does the excluding; the denylist is defence in depth, and
it is the defence that has holes.

**Read and write are separate rows where their states differ.** Where they agree,
one row carries both.

---

## 3. THE SERVER SURFACE THIS SLICE IS MEASURED AGAINST

35 tools in `linkedin_server/server.py`. **Nine touch this slice.**
`writes.PERFORMABLE` holds 12 actions; **two are here**.

| tool | what it does here | live-fire |
|---|---|---|
| `linkedin_my_profile` | name, headline, location, About, public identifier, Open To Work + audience, which sections rendered, and on a second page load the skills list | FIRED-SUCCEEDED. Errored on the first live run 2026-08-21 (`mcp-servers/_audit/2026-08-21-linkedin-parse-fix.md:1`), fixed, read live since; skills re-measured 2026-09-03 -- 20 skill cards, all carrying text |
| `linkedin_profile_editor_fields` | control LABELS inside `/in/me/edit/intro/`, never values | FIRED-SUCCEEDED twice: 23 controls 2026-08-31 (`_audit/2026-08-31-linkedin-perform.md:370`), 17 controls 2026-09-02 (`:2925`) |
| `linkedin_profile_editor_values` | what those controls HOLD -- the restore path for an edit | FIRED-SUCCEEDED 2026-09-02 (`:2925`) |
| `linkedin_update_profile_field` | change ONE intro-editor field, behind the two-call gate | **FIRED-FAILED.** Shipped `a540461` 2026-09-02, could not navigate once -- three independent fatal defects, `NAVIGATIONS ATTEMPTED: []` -- while minting a live `confirm_token` off a real preview he confirmed. Repaired `ea5354d` the same day. **No successful edit exists, before or after the repair. "It fired" is not "it worked", and no prose calling it well-verified counts as coverage.** |
| `linkedin_update_setting` | dark mode: read the three-state radio group, then change it | READ FIRED-SUCCEEDED -- six readings, two days, three builds, agreeing on every count: 20 controls, ZERO forms, 16 links, no dialogs, no redirect, exactly one of three radios checked. **WRITE NEVER FIRED.** For any setting but dark mode the tool refuses in Python and loads nothing: `READABLE_SETTINGS` has exactly one key |
| `linkedin_surface_census` | control counts on `profile`, `profile_edit_intro`, `settings`, `settings_dark_mode`, `premium` (plus six keys outside this slice) | FIRED-SUCCEEDED on all five of this slice's keys: profile 4, profile_edit_intro 4, settings 3, settings_dark_mode 2 (`_audit/2026-08-31-linkedin-finish.md:275-279`); premium 3 (`_audit/2026-08-31-linkedin-perform.md:2035`) |
| `linkedin_who_viewed_me` | Who's Viewed Your Profile; 365 days on his Premium Career account | FIRED-SUCCEEDED -- "Now 10 rows, 10 distinct names, verified live" (`mcp-servers/_audit/2026-08-21-linkedin-parse-fix.md:5`) |
| `linkedin_my_activity_items` | his own activity rail -- the profile Activity section | FIRED-SUCCEEDED, and measured UNRELIABLE: 233 controls on one reading, 67 on another, same session, minutes apart |
| `linkedin_server_info` | reports which actions are performable | not a LinkedIn surface |

**There is no `linkedin_set_open_to_work` tool.** The spec exists in `writes.py`;
nothing on the tool surface calls it. `server.py:82`:

> *"`set_open_to_work` has no tool registered for it at all, so it is not part of
> the thirty-five: it is a spec behind the gate with nothing on the surface to
> call it. `writes.mint` refuses it a grant at issue, so no confirm token for it
> can exist for anyone."*

That is why every Open To Work write below is EXCLUDED-RULED and **not**
COVERED-CANNOT-DELIVER: the fifth state needs a tool that exists and has fired,
and here nothing exists to fire.

---

## 4. THE TABLE

R = read, W = write.

### A. Intro / top card -- the ONE profile editor this server can address (29)

`/in/me/edit/intro/` is admitted by an EXACT-url exemption past the `/edit/`
forbidden entry. Its live control list was 23 on 2026-08-31 and 17 on 2026-09-02
-- **a different set, not a subset**. Six of the 17 can be aimed at by name;
three cannot, for two different measured reasons, and those three are the fifth
state's clearest instances.

Help Center `a547248` names the desktop editor's fields as: Name, Profile photo,
Background photo, Headline, Current position, Education, Location, Industry,
Contact info, "Open to". **It names no pronouns field and no postal code**, both
of which appear below on other evidence.

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| A1 | Headline | R | COVERED-PROVEN | `my_profile` returns it; `profile_editor_values` reads it verbatim |
| A2 | Headline | W | COVERED-CANNOT-DELIVER | `update_profile_field` exists; `profile_editor_fields` fired live 2026-09-02 and measured the control unaimable -- *"`headline` because its name IS its content"*. A `div[role=textbox]` with no aria-label, no label-for and no title, so its accessible name resolves to its own text; the reader returns `<content>` and withholds it |
| A3 | First name | R | COVERED-PROVEN | *"Their values read perfectly -- the value reader returned both"* |
| A4 | First name | W | COVERED-CANNOT-DELIVER | *"The first-name and last-name inputs have NO ACCESSIBLE NAME AND ARE `required: true` ... they cannot be addressed by name. That is the exact inverse of the problem the ruling was written to solve"* (`:2960`) |
| A5 | Last name | R | COVERED-PROVEN | same live reading |
| A6 | Last name | W | COVERED-CANNOT-DELIVER | same measurement |
| A7 | Additional name (former / maiden / nickname) | R | COVERED-PROVEN | read live; value is the empty string |
| A8 | Additional name | W | COVERED-UNFIRED | aimable by `label-for`; the gate would not refuse it; never fired |
| A9 | Additional-name visibility | W | GAP | four options, named by `a545784`: Only you / Your connections / Your network / All LinkedIn members. Not among the 17 controls read; blocker: unobserved control |
| A10 | Country / Region | R | COVERED-PROVEN | read live |
| A11 | Country / Region | W | COVERED-UNFIRED | aimable by `aria-label` |
| A12 | City | R | COVERED-PROVEN | read live |
| A13 | City | W | COVERED-UNFIRED | aimable by `aria-label` |
| A14 | Postal code | W | GAP | not among the 17 controls, and `a547248` does not name it either -- see NOT REACHED #12 |
| A15 | Location display choice | W | GAP | not among the 17 controls |
| A16 | Industry | R | COVERED-PROVEN | read live |
| A17 | Industry | W | COVERED-UNFIRED | aimable by `aria-label` |
| A18 | Pronouns | R | COVERED-PROVEN | read live; option text returned. **Enumerated from the server's own live control list, not from LinkedIn's documentation, which has no pronouns article** |
| A19 | Pronouns | W | COVERED-UNFIRED | a `select`; `select_option` is the 4th entry on `SANCTIONED_MUTATIONS` |
| A20 | Education shown in intro | R | COVERED-PROVEN | read live; option text returned |
| A21 | Education shown in intro | W | COVERED-UNFIRED | a `select`, same route |
| A22 | Primary Position(s) -- which current role shows in the intro | W | GAP | real control, named verbatim in `a550169`: *"If you've already added Primary Position(s) select the company you want to show in your intro"*. Distinct from reordering (`a786867`). No position control among the 17 |
| A23 | Name pronunciation audio | W | GAP | `a550527`: max 10 seconds, **mobile iOS/Android app only** -- cannot be recorded or edited on desktop, only deleted. A browser-driven server structurally cannot record it |
| A24 | ID name as additional name | W | GAP | `a7153330`; requires an identity verification first (block K) |
| A25 | Contact info panel | R | GAP | the control `Edit contact info` WAS among the 17 read on 2026-09-02; the panel behind it has never been opened |
| A26 | Website on profile | W | GAP | inside that unopened panel |
| A27 | Phone number on profile | W | GAP | same. **There is no address field** -- `a565128` enumerates exactly six: LinkedIn profile link, email, phone, website, instant messenger, birthday |
| A28 | Instant messenger accounts on profile | W | GAP | same panel |
| A29 | Birthday on profile, and its visibility | W | GAP | same panel |

### B. Photo, banner, frames, badges (10)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| B1 | Whether a profile photo exists | R | COVERED-PROVEN | `my_profile.completeness.has_photo`, off the topcard images |
| B2 | Profile photo add / change / delete | W | EXCLUDED-RULED | `tests/test_readonly.py:306-341`, a test-enforced package-wide ban on `set_input_files`: *"UPLOADING IS A DIFFERENT CAPABILITY FROM TYPING. A fill puts his words in a box; a file input puts a FILE from this machine into somebody else's inbox, chosen by a path string. Nothing in this package should be one edit away from that, and the operator has never been asked about it."* An OPEN QUESTION, not silence -- finding 7.11 |
| B3 | Profile photo crop / filter / adjust | W | EXCLUDED-RULED | same ruling. `a541850` names the pop-up controls -- Edit, Add photo, Frames, Delete |
| B4 | Profile photo visibility audience | W | GAP | `/public-profile/settings`, which no forbidden substring catches and no allowlist pattern admits |
| B5 | Background / banner image add / change / delete | W | EXCLUDED-RULED | same ruling |
| B6 | #OpenToWork photo frame apply / remove | W | EXCLUDED-RULED | the residue clause of the `set_open_to_work` spec: *"Switching to All LinkedIn members draws a green #OpenToWork frame on the photo that a current employer and his colleagues can see. Taking it down later removes the frame; it does not un-see it."* |
| B7 | #Hiring photo frame apply / remove | W | GAP | implied by `a519730` and never enumerated -- **no Help Center article lists the frame set at all**, so the full frame inventory is unknown on both sides |
| B8 | Top Voice badge show / hide | W | GAP | `a1577365`; no tool, no reason |
| B9 | Premium profile badge show / hide | W | GAP | `a569234`; no tool, no reason |
| B10 | Open Profile setting (who may message without connecting) | W | GAP | `a541684`; no tool, no reason |

### C. Public profile and vanity URL (8)

`/public-profile/settings` is not below the settings index, so the settings-family
ruling does not reach it. Nothing else in this repo names it either.

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| C1 | Own public profile URL / slug | R | COVERED-PROVEN | `my_profile.public_identifier`, parsed from the landed url |
| C2 | Customise the public profile URL | W | GAP | `/public-profile/settings`; no tool, no reason |
| C3 | Public profile visibility master switch | W | GAP | `a528138`: *"Your profile's public visibility"* Off hides it from public view |
| C4 | Per-section public visibility toggles | W | GAP | `a518980`; the default photo setting is Public |
| C5 | Search-engine visibility of the public profile | W | GAP | same page |
| C6 | Unlink a prior public URL | W | GAP | same page |
| C7 | Guest controls / cookie consent | W | EXCLUDED-RULED | `/psettings/guest-controls`; `"/psettings/"` is a forbidden substring |
| C8 | Save profile as a PDF | R | GAP | `a541960`: desktop only, **200 downloads per month**, English-only, and it works on **another member's profile too** -- which would collide with `PERMANENTLY_FORBIDDEN["load_a_third_partys_profile_to_measure_a_control"]` if ever built for anyone but him |

### D. Profile body sections (29)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| D1 | About text | R | COVERED-PROVEN | `my_profile.about`, trimmed to 1200 chars |
| D2 | About text | W | EXCLUDED-RULED | its editor is `/in/<member>/edit/forms/summary/new/`, named in the `update_profile_field` docstring as measured to exist, and refused by `/edit/`. The exemption table admits ONE url past that entry and this is not it |
| D3 | Which profile sections rendered | R | COVERED-PROVEN | `completeness.sections_present` / `sections_not_rendered`, with the tool's own rule that absent means UNKNOWN, never zero |
| D4 | Experience entries | R | COVERED-CANNOT-DELIVER | `my_profile` DECLARES the field and always returns `experience_entries: None`, because it does not scroll and the section is deferred. It fires live and structurally cannot fill the field it promises. **`/in/<member>/details/experience/` IS on the read allowlist and nothing navigates to it** -- the tool hands the caller the url instead |
| D5 | Add / edit / delete a position | W | EXCLUDED-RULED | `/edit/` family ruling. `a593695` covers jobs, volunteering, military, board service; it does not enumerate field names |
| D6 | Employment type, skills, media on a position | W | EXCLUDED-RULED | `/edit/` family ruling PLUS the upload ban -- two independent written refusals |
| D7 | Notify network of a job change | W | EXCLUDED-RULED | the standing broadcast setting is O-block; `a547248` names `/psettings/activity-broadcast` |
| D8 | Reorder current positions | W | EXCLUDED-RULED | `/edit/` family ruling. `a786867`: Sort then Reorder, click-hold-drag; `drag_to` is also an unsanctioned mutation class |
| D9 | Career break | W | EXCLUDED-RULED | `/edit/` family ruling. Confirmed to EXIST as a **Core** item in the Add-profile-section menu (`a540837`) and **documented nowhere** -- absent from a 55-article Profile index |
| D10 | Education entries | R | COVERED-CANNOT-DELIVER | same shape as D4: `education_entries: None` declared and never filled; `/details/education/` allowlisted and unvisited |
| D11 | Add / edit / delete education | W | EXCLUDED-RULED | `/edit/` family ruling |
| D12 | Reorder education | W | EXCLUDED-RULED | `/edit/` family ruling |
| D13 | Licenses and certifications | W | EXCLUDED-RULED | `/edit/` family ruling; and its Help article `a567169` is **HTTP 404 on all three verticals tried**. Its content survives only as a cached search snippet, so its form fields are UNVERIFIED |
| D14 | Courses | W | EXCLUDED-RULED | `/edit/` family ruling; **name-searched, no dedicated Help article exists** |
| D15 | Projects | W | EXCLUDED-RULED | same. One official fact only: the Project URL field is not available for newly-added projects |
| D16 | Publications | W | EXCLUDED-RULED | same |
| D17 | Patents | W | EXCLUDED-RULED | same |
| D18 | Honors and awards | W | EXCLUDED-RULED | `/edit/` family ruling. `a563433` documents add/edit/delete but says only *"enter the required information"* -- it does not name the fields |
| D19 | Test scores | W | EXCLUDED-RULED | `/edit/`; name-searched, no dedicated article |
| D20 | Languages | W | EXCLUDED-RULED | `/edit/`; name-searched, every hit is a Page-language or UI-language article |
| D21 | Organizations | W | EXCLUDED-RULED | `/edit/`; name-searched, no dedicated article |
| D22 | Volunteer experience | W | EXCLUDED-RULED | `/edit/`; name-searched, every hit is the Experience section, the Page Volunteer button, or opportunity discovery |
| D23 | Causes you care about | W | EXCLUDED-RULED | `/edit/` family ruling. An **Additional** item in `a540837` |
| D24 | Open to volunteering | W | GAP | `a6862361`. Real fields: areas of interest, skills, On-site / Hybrid / Remote, locations, an "Email me matching opportunities" toggle, plus Edit and Delete. Reached from the `Open to` button, one of the three items measured on his account |
| D25 | "Add profile section" menu contents | R | GAP | now enumerated from `a540837`: **Core** About, Education, Position, Services, Career break, Skills; **Recommended** Featured, Licenses and certifications, Projects, Courses, Recommendations; **Additional** Volunteer experience, Publications, Patents, Honors and awards, Test scores, Languages, Organizations, Causes. Nineteen items; no tool reads the menu |
| D26 | Profile level meter / All-Star | R | EXCLUDED-RULED | `my_profile` docstring: *"LinkedIn's own profile-strength meter is not exposed here, so this server does not report one. What it reports is derived and labelled as such."* |
| D27 | Create / delete a secondary-language profile | W | GAP | `a541878`: desktop only; *"Translations aren't done for you"* |
| D28 | View a profile in multiple languages | R | GAP | `a541878`, `a544976` |
| D29 | Add a LinkedIn Learning certificate of completion to the profile | W | GAP | `a704787`. Lands in a "Certificates of Completion and Skills" section. **Blocked if the profile already has over 100 skills** -- he has 20, so it is available to him |

### E. Skills and endorsements (8)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| E1 | Own skills list | R | COVERED-PROVEN | 20 skill cards off `/in/me/details/skills/`, live 2026-09-03 |
| E2 | Add / remove skills | W | EXCLUDED-RULED | `/edit/` family ruling; the editor address is measured in this repo's own fixtures as `/in/<member>/details/skills/edit/forms/<n>/` |
| E3 | Reorder skills / pin top skills | W | EXCLUDED-RULED | `/edit/` family ruling, plus `drag_to` |
| E4 | Endorse another member's skills | W | EXCLUDED-RULED | `PERMANENTLY_FORBIDDEN["endorse_or_recommend"]`: *"zero endorse controls across 13 tracked fixtures ... and zero among the 222 controls read live on his own profile on 2026-08-30. You cannot endorse yourself, so the only surface that would carry the control is a THIRD PARTY'S PROFILE -- and loading one leaves them a durable record ... IMPOSSIBLE AS SPECIFIED, not unwanted"* |
| E5 | Remove an endorsement you gave | W | EXCLUDED-RULED | same key, plus `delete_or_withdraw_anything` |
| E6 | Hide / show an endorsement received | W | GAP | blocker: `"/endorse"` is a forbidden substring. **The written reason does not reach this act** -- `endorse_or_recommend` argues about making a statement about another person; this is housekeeping on his own profile |
| E7 | Endorsements received | R | GAP | same blocker, same absence of a reason |
| E8 | Opt out of endorsements entirely | W | EXCLUDED-RULED | a settings-family toggle (`a551156`); section 6 |

### F. Recommendations (9)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| F1 | Recommendations received | R | GAP | no tool, no reason |
| F2 | Request a recommendation | W | GAP | no tool, no reason; it reaches another member |
| F3 | Give a recommendation | W | EXCLUDED-RULED | named in `PERMANENTLY_FORBIDDEN["endorse_or_recommend"]`. **NAMED BUT UNARGUED** -- finding 7.4 |
| F4 | Revise a recommendation you gave | W | EXCLUDED-RULED | same key, same caveat |
| F5 | Delete a recommendation you sent | W | EXCLUDED-RULED | `delete_or_withdraw_anything`: *"destruction is not a write this design covers, at any confirm level"*; `/delete` is also forbidden |
| F6 | Accept or dismiss a recommendation received | W | GAP | no tool, no reason |
| F7 | Ask for a revision of one received | W | GAP | no tool, no reason |
| F8 | Decline a requested recommendation | W | GAP | no tool, no reason |
| F9 | Hide / unhide recommendations on the profile | W | GAP | no tool, no reason |

### G. Featured and Activity sections (7)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| G1 | Own activity items | R | COVERED-PROVEN, WITH A MEASURED RELIABILITY DEFECT | the rail returned 233 controls on one reading and 67 on another in the same session. The spec's own words: *"A check that answers nothing on some readings it can take is not a verification."* |
| G2 | Activity section default view | W | GAP | no tool, no reason |
| G3 | Featured section: add work samples | W | EXCLUDED-RULED | same ruling |
| G4 | Featured: reorder / edit / remove / unpin | W | EXCLUDED-RULED | `/edit/` family ruling, plus `drag_to` |
| G5 | Feature content pulled from other profile sections | W | EXCLUDED-RULED | `/edit/` family ruling |
| G6 | Per-post analytics | R | GAP | no tool, no reason. Two impressions links were counted on an item permalink 2026-09-01 and never followed |
| G7 | Profile search appearances | R | GAP | no tool, no reason |

### H. Services / "Providing services" (11)

A Service Page is a profile-attached identity surface open to every member --
`Services` is a **Core** item in the Add-profile-section menu. **All eleven are
GAPs: nothing in this repo mentions a Service Page in any capacity.**

| # | capability | R/W | state | blocker |
|---|---|---|---|---|
| H1 | Create a Service Page / add services | W | GAP | one of the three items the `Open to` menu resolves to on his account; never actioned |
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

**The block where the repo argues most and can act least.** The state is read; the
editor has never been loaded, and its absence is a measurement rather than an
admission. From `set_open_to_work.reversibility_procedure`:

> *"THE ABSENCE OF A URL IS NOW A MEASUREMENT RATHER THAN AN ADMISSION, taken
> 2026-08-24: 237 distinct urls and 37 payload paths were enumerated across all
> five profile captures and ZERO reach an open-to-work editor, a job-preferences
> page or a career-interests page; the strings 'opentowork' and 'open-to-work'
> occur zero times anywhere. The editor is not url-addressed AT ALL -- its screens
> are addressed by an internal screen id, and its entry control fires a request
> whose own name is saveAndFetchNextStep. So the one click that would first REVEAL
> the editor is also the first click that could CHANGE it, which is why no capture
> of it may be taken except with him watching."*

`opentowork` and `open-to-work` are both forbidden substrings; the spec carries
`url_template=None`; **and no tool is registered for the action at all.**

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| I1 | Open To Work on/off AND its current audience | R | COVERED-PROVEN | `my_profile.open_to_work`, off the topcard at no extra page load, at BOTH hydration states. LinkedIn prints the audience verbatim ("Open to work - Recruiters only"); confirmed against frozen fixtures and live 2026-08-23 |
| I2 | Turn Open To Work on or off | W | EXCLUDED-RULED | the quote above; no tool exists |
| I3 | Change the audience | W | EXCLUDED-RULED | same, plus the green-frame residue clause. Help `a507508` documents THREE audiences -- All LinkedIn Members, Recruiters only, **Visible only to you** -- against the spec's three, which differ; finding 7.3 |
| I4 | OTW field: job titles | W | EXCLUDED-RULED | editor never loaded |
| I5 | OTW field: locations | W | EXCLUDED-RULED | same |
| I6 | OTW field: location / workplace types | W | EXCLUDED-RULED | same |
| I7 | OTW field: employment types | W | EXCLUDED-RULED | same |
| I8 | OTW field: start date | W | EXCLUDED-RULED | same |
| I9 | OTW field: notice period (INDIA ONLY -- applies to him) | W | EXCLUDED-RULED | same |
| I10 | OTW field: expected annual salary (INDIA ONLY -- applies to him) | W | EXCLUDED-RULED | same |
| I11 | Delete the Open To Work card | W | EXCLUDED-RULED | same, plus `delete_or_withdraw_anything` |
| I12 | Job preferences / career-interests page | W | EXCLUDED-RULED | measured: zero of 237 urls reach one |
| I13 | Minimum pay preference | W | GAP | on that same unreachable page, and named nowhere in this repo |
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

`/mypreferences/d/verifications` is a page below the settings index, so the
settings-family ruling reaches it -- see section 6, and see finding 7.1 for why
the denylist does not.

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| K1 | Verifications section on the profile | R | EXCLUDED-RULED | settings family |
| K2 | Identity verification via DigiLocker (India -- his route) | W | EXCLUDED-RULED | settings family |
| K3 | Workplace verification by work email | W | EXCLUDED-RULED | settings family |
| K4 | Workplace verification via Microsoft Entra Verified ID | W | EXCLUDED-RULED | settings family |
| K5 | Workplace verification via a company LinkedIn Learning licence | W | EXCLUDED-RULED | settings family |
| K6 | Phone number verification | W | EXCLUDED-RULED | settings family |
| K7 | Remove a verification | W | EXCLUDED-RULED | `delete_or_withdraw_anything`, and `/delete` |
| K8 | Top Voice blue badge on the profile | R | GAP | no tool, no reason |
| K9 | Show / hide the Top Voice badge | W | GAP | `a1577365`; no tool, no reason |
| K10 | Verification badge as it appears on job posts | R | GAP | no tool, no reason |

### L. Creator tools, followers and analytics (8)

Creator mode itself is RETIRED (section 8); these survived it, and LinkedIn's
Help Center now states all members have access.

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| L1 | Creator analytics / audience analytics | R | GAP | no tool, no reason |
| L2 | Own follower count and follower list | R | GAP | the count IS read incidentally -- *"his profile reports 275 followers"* is quoted inside `publish_post.residue` -- and no tool returns it |
| L3 | Create / edit / delete a newsletter | W | GAP | no tool, no reason |
| L4 | Newsletter analytics | R | GAP | no tool, no reason |
| L5 | Host a LinkedIn Live | W | GAP | he clears the >150-follower gate at 275; no tool, no reason |
| L6 | Audio events | W | GAP | no tool, no reason; the Help article itself 404s |
| L7 | "Ideas for your next post" | R | GAP | no tool, no reason |
| L8 | Analytics and tools hub | R | GAP | no tool, no reason |

### M. Resumes and application documents (12)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| M1 | Upload a resume from Job Application Settings | W | EXCLUDED-RULED | `/jobs/application-settings/` contains `"/jobs/application"`, the FIRST entry on the forbidden tuple; `set_input_files` is unsanctioned on top of that |
| M2 | Saved resumes list (4 most recent) | R | EXCLUDED-RULED | same address, same entry |
| M3 | Delete a saved resume | W | EXCLUDED-RULED | same address, plus `delete_or_withdraw_anything` and `/delete` |
| M4 | Download a saved resume | R | EXCLUDED-RULED | same address |
| M5 | View the resume used for a specific application | R | EXCLUDED-RULED | same address |
| M6 | Saved screening-question answers | R/W | EXCLUDED-RULED | same address |
| M7 | Opt out of saving job application data | W | EXCLUDED-RULED | same address |
| M8 | "Share resume data with recruiters" toggle | W | EXCLUDED-RULED | settings family |
| M9 | Stored job applicant accounts | R/W | EXCLUDED-RULED | settings family (`/mypreferences/d/job-application-accounts`); denylist-uncaught, finding 7.1 |
| M10 | Autofill for work emails | W | EXCLUDED-RULED | settings family |
| M11 | Resume Builder | R/W | GAP | no tool, no reason; entitlement unverified |
| M12 | Resume Tips (AI resume feedback) | R | GAP | no tool, no reason; entitlement unverified |

### N. Account preferences, sign-in, security and account lifecycle (31)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| N1 | Dark mode current state | R | COVERED-PROVEN | six agreeing readings across two days and three builds |
| N2 | Dark mode change | W | COVERED-UNFIRED | in `PERFORMABLE`; verification is a fresh navigation and a re-read of all three radios. Never fired |
| N3 | Which settings sections exist (the index) | R | COVERED-PROVEN | census `settings`, 34 controls, live 2026-08-30, three readings. The six sections are fixed by `a1337839`: Account preferences, Sign in & security, Visibility, Data privacy, Advertising data, Notifications |
| N4 | Two-step verification on / off | W | EXCLUDED-RULED | settings family. Methods named by `a1381088`: authenticator app, SMS. **Denylist-uncaught -- finding 7.1, and the most consequential of the six** |
| N5 | Change password | W | EXCLUDED-RULED | settings family. `a1379143`: min 8 chars, plus a "Require all devices to sign in with new password" checkbox. Denylist-uncaught |
| N6 | Passkeys add / delete | W | EXCLUDED-RULED | settings family. `a1621596`: max 5 per account |
| N7 | Email addresses -- add / remove / change primary | W | EXCLUDED-RULED | settings family, `/psettings/email` |
| N8 | Phone numbers -- add / remove / choose reset number | W | EXCLUDED-RULED | settings family |
| N9 | Where you're signed in -- list active sessions | R | EXCLUDED-RULED | settings family, `/psettings/sessions`. Shows location, IP, device, browser, last sign-in |
| N10 | Sign out of one session / all sessions | W | EXCLUDED-RULED | settings family, same page. A distinct act from reading the list |
| N11 | Devices that remember your password | W | EXCLUDED-RULED | settings family |
| N12 | Keep me logged in / auto sign-in | W | GAP | `/uas/login` -- not a settings-index page, caught by no substring, named nowhere in this repo. `a1342645`: unavailable when 2FA is on |
| N13 | Sign-in security prompt / email code / CAPTCHA | R | GAP | an interstitial, not a page. `config.AUTHWALL_MARKERS` already turns a `/checkpoint/` landing into a reported failure, which is adjacent but not this |
| N14 | Identity verification for account recovery (Persona) | W | GAP | `a1342692`; no path, no tool, no reason |
| N15 | Interface language | W | EXCLUDED-RULED | settings family. `a521833` names ONE language control |
| N16 | Autoplay videos | W | EXCLUDED-RULED | settings family |
| N17 | Sound effects | W | EXCLUDED-RULED | settings family |
| N18 | Showing other members' profile photos | W | EXCLUDED-RULED | settings family |
| N19 | Name / location / industry via settings | W | EXCLUDED-RULED | settings family; also reachable through the intro editor (block A) |
| N20 | Calendar sync | W | EXCLUDED-RULED | settings family; mobile app only |
| N21 | Contact / address-book sync | W | EXCLUDED-RULED | settings family |
| N22 | Subscriptions and payments | R | EXCLUDED-RULED | settings family |
| N23 | Partners and services / Microsoft account link | W | EXCLUDED-RULED | settings family |
| N24 | Permitted Services -- third-party app access | W | EXCLUDED-RULED | settings family, `/psettings/permitted-services` |
| N25 | LinkedIn Services (DMA) connect / disconnect | W | GAP | `a6222119`: Jobs, Marketing Solutions, Learning. Nav path only -- no URL, so no address to rule on |
| N26 | Mentions, tags and collaborations permission | W | EXCLUDED-RULED | settings family, `a522861` |
| N27 | Merge or close duplicate accounts | W | EXCLUDED-RULED | settings family |
| N28 | Close (delete) account | W | EXCLUDED-RULED | `"/close-accounts"` was added to the forbidden tuple 2026-08-31 precisely because nothing else caught it, plus `delete_or_withdraw_anything` |
| N29 | Hibernate account | W | EXCLUDED-RULED | `"/hibernate-account"`, added the same day, same reason |
| N30 | Deceased member -- request account closure | W | GAP | `a1380121`, via a Help Center form (`/help/linkedin/ask/ts-rmdmlp`). Not his own act; included because it is an account-lifecycle capability the product offers |
| N31 | Deceased member -- request memorialization | W | GAP | same article, different form slug (`/help/linkedin/ask/TS-RDMLP` -- note the case differs) |

### O. Visibility and privacy (23)

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| O1 | Who's Viewed Your Profile list | R | COVERED-PROVEN | 10 rows, 10 distinct names, verified live; 365 days back on Premium Career |
| O2 | De-anonymise a private-mode viewer | R | EXCLUDED-RULED | `PERMANENTLY_FORBIDDEN["deanonymise_a_viewer"]`: *"six of ten profile viewers chose anonymity; the row LinkedIn renders him is the whole of what he is entitled to"* |
| O3 | WVYP Premium insights and filters | R | GAP | no tool, no reason |
| O4 | Profile viewing options (his own browsing mode) | W | EXCLUDED-RULED | settings family. `a568195`: "Your name and headline" / "Private profile characteristics" / "Private mode" |
| O5 | Public profile badge creation | W | GAP | `/badges/profile/create` -- caught by no substring, on no allowlist pattern, named nowhere in this repo |
| O6-O20 | fifteen further visibility toggles: contact-info and email visibility, connection-list visibility, who can see members you follow, who can follow you, representing your organization ("Profile information on content"), Page owners exporting your data, discoverability by email, discoverability by phone, profile discovery off LinkedIn, off-LinkedIn visibility, manage active status, share profile updates with your network, visibility of shared posts, sharing public posts on and off LinkedIn, Page visit visibility | W | EXCLUDED-RULED | settings family; section 6 |
| O21 | Block / unblock a member | W | EXCLUDED-RULED | settings family; independently an act on another member's relationship |
| O22 | See a list of who you blocked | R | EXCLUDED-RULED | settings family |
| O23 | Whether a photo, banner or headline change notifies the network | R | GAP | the `update_profile_field` docstring states this as an UNMEASURED cost: *"LinkedIn notifies a network about some profile changes, which this server has not measured and would not control."* A named unknown, not a considered exclusion |

### P-R. Data privacy, advertising data, notification settings (45)

Forty-four of the forty-five resolve to a `/psettings/...`,
`/mypreferences/d/categories/...` or `/mypreferences/d/settings/...` address and
are EXCLUDED-RULED by the settings-family ruling (section 6). The enumeration is
kept at LinkedIn's own published granularity:

* **The four data rights**, named verbatim by `a1340649`: Delete Data; Access and
  Download Data; Change or Correct Data; Restrict or Object to the use of Data.
* **Download your data, two tiers**: 37 categories "within 10 minutes", 30
  categories "within 48 hours", download available for 72 hours. (`a1339364`
  states both "10 minutes / 48 hours" in the lists and "minutes / 24 hours" in
  its prose; the discrepancy is on the page and is not reconciled here.)
* **The seven notification categories**, named verbatim by `a1341821`:
  Invitations and messages; Jobs and opportunities; Activity in your network;
  Activity that involves you; News and articles; Offers and tips from LinkedIn;
  Updates from events. Plus channel controls (in-app / push / email) and the four
  connection-notification toggles.
* **Eight advertising controls**: profile data, activity and inferred data,
  off-LinkedIn data, ads personalization, demographic data, research invitations,
  the ads category page, cookie preferences.
* Search history, salary data, invitations-to-connect audience, research
  invitations, InMail opt-out, read receipts and typing indicators, message
  nudges, harmful message detection, job-post email notifications.

The one that is not settings-family:

| # | capability | R/W | state | evidence / blocker |
|---|---|---|---|---|
| P1 | Mark notifications read | W | EXCLUDED-RULED | `PERMANENTLY_FORBIDDEN["mark_notifications_read"]`, on three independent grounds, the third being that *"the read tool ALREADY has the full effect -- opening the page clears the badge -- so a write here could only ever run after its own consequence had landed"* |

(`P1` is counted in the 45; the settings-family share of this block is 44.)

---

## 5. WHAT THE 79 GAPS WOULD TAKE

Reversibility matters more than difficulty, because the asset is his professional
identity. Counts sum to 79, and every one was counted off the table above rather
than asserted.

**5.1 -- Controls inside the ONE editor this server can already open (9).**
`A9, A14, A15, A22, A25-A29`.
`/in/me/edit/intro/` is admitted; these controls were simply not among the 17 read
on 2026-09-02. Shape: open the panel (`Edit contact info` is itself one of the 17)
and re-read. **No boundary moves and no new permission is needed** -- this is the
one group blocked by a missing observation rather than a standing refusal. Write,
with a read as its precondition; reversible only if `profile_editor_values` is
extended to the panel first.

**5.2 -- `/public-profile/settings` and its neighbours (6).** `B4, C2-C6`.
Not below the settings index, so the settings ruling does not reach it; caught by
no denylist entry; named nowhere in this repo. Shape: one allowlist pattern. Write.
**C5 is irreversible in audience** -- once a profile is indexed by a search engine,
un-indexing it does not un-cache it.

**5.3 -- Surfaces nobody in this repo has ever named (64).**
`A23, A24, B7-B10, C8, D24, D25, D27-D29, E6, E7, F1, F2, F6-F9, G2, G6, G7,
H1-H11, I13-I16, J1-J4, K8-K10, L1-L8, M11, M12, N12-N14, N25, N30, N31, O3, O5,
O23`.
Shape: a surface census first, then a spec, then a gate -- the full path every
existing write took. Mixed read and write. The irreversible-in-audience ones, named
rather than lumped: **F2 and H9 send a request to a real person**; **H1-H8 publish
a public Service Page under his name**; **J1-J3 tell a network he is hiring**;
**L3 and L5 broadcast**; **I14 tells a company's recruiters he wants to work
there**; **N30 and N31 act on somebody's account after their death.** The safely
reversible ones are all reads: `C8, D25, D28, E7, F1, G6, G7, H11, J4, K8, K10, L1,
L2, L4, L7, L8, M12, N13, O3, O23`.

**The cheapest work in this census is not in this section at all.** `D4` and `D10`
-- reading his own Experience and Education entries -- are COVERED-CANNOT-DELIVER,
because `my_profile` already declares both fields, already hands back both urls,
and both urls are **already on the read allowlist**. No boundary moves, no new
permission, one harvest function of the same shape as the skills read that works
today. That is the single highest-value buildable item this slice found.

## 6. THREE FAMILY RULINGS PRODUCE 123 OF THE 150 EXCLUSIONS

**The settings family -- 93 rows.** Every settings-index page in `C7, E8, K1-K6,
M8-M10, N4-N11, N15-N24, N26-N27, O4, O6-O22` and 44 of the 45 P-R rows. From
`linkedin_update_setting`:

> *"ONE SETTING IS WRITABLE, AND ASKING ABOUT ANY OTHER LOADS NOTHING. The read
> allowlist admits exactly one page below the settings index, admitted BY NAME on
> the operator's ruling. ... READ THIS BEFORE ASKING FOR THE FAMILY TO BE OPENED.
> `Close and delete account` and `Hibernate account` are addresses in it. A
> permission written for the FAMILY would carry those with it, which is why a
> setting is admitted by name or not at all -- and it is why this tool shipping
> does NOT mean the next setting is a small step."*

**The `/edit/` family -- 23 rows.** Every profile-section editor: `D2, D5-D9,
D11-D23, E2, E3, G4, G5`. Those addresses are measured in this repo's own fixtures
(`/in/<member>/details/skills/edit/forms/<n>/`) and the argument is written beside
the one exemption that was granted:

> *"Narrowing was refused: `/edit/` must keep refusing the whole rest of that
> family, on his own profile and on everybody else's, and buying one page by
> weakening a standing refusal is the trade this module exists to make somebody
> argue for."*

**`/jobs/application` -- 7 rows.** `M1-M7`, the whole Job Application Settings
page, refused by the first entry on the forbidden tuple.

All three rulings are real, argued and correct, and this census disputes none of
them. What it insists on is the arithmetic: **not one of those 123 capabilities has
been considered on its own merits.** A family ruling says the family stays shut; it
does not say that "who can see your connections", "read my verification badges" or
"add a certification to my profile" was weighed and declined. Asked tomorrow which
of them this server should reach, the honest answer is that nobody has an opinion
about any of the 123. Exactly three addresses have ever been let out of these
families, each admitted BY NAME on the operator's own ruling: dark mode, the intro
editor, and the skills details page.

Split of the 150:

    settings-family ruling                                           93
    /edit/ family ruling                                             23
    set_open_to_work spec, per field (I2-I12, B6)                    12
    PERMANENTLY_FORBIDDEN named keys
      (E4, E5, F3, F4, F5, K7, N28, N29, O2, P1)                     10
    /jobs/application forbidden entry (M1-M7)                         7
    set_input_files, test-enforced (B2, B3, B5, G3)                    4
    my_profile's own declaration (D26)                                1
    ---------------------------------------------------------------
                                                                    150

## 7. FINDINGS

### 7.1 -- SIX live `/mypreferences/d/<name>` addresses slip past the denylist, and one of them is the password-change page

`readonly._FORBIDDEN_URL_SUBSTRINGS` gained `"/close-accounts"` and
`"/hibernate-account"` on 2026-08-31, with this reasoning in the source:

> *"The settings audit assumed 'Close and delete account' and 'Hibernate account'
> ... were covered by the `/mypreferences/d/categories/` entry three lines up.
> THEY ARE NOT. ... The only thing that had ever refused them was the anchored
> allowlist. ... for the two worst addresses on the account there was no second
> gate at all."*

The Help Center names **six more addresses of exactly that shape**. Each was run
through all 23 forbidden substrings programmatically; none matches:

    /mypreferences/d/change-password                (a1379143)
    /mypreferences/d/two-factor-authentication      (a1381088)
    /mypreferences/d/verifications                  (a1359065)
    /mypreferences/d/job-application-accounts       (a507642)
    /mypreferences/d/member-cookies                 (a1336669)
    /mypreferences/d/profile-visibility-for-partners (a518980)

Four more settings-shaped addresses are also uncaught: `/public-profile/settings`,
`/uas/login`, `/badges/profile/create`, and **`/mwlite/settings` -- an entire
parallel mobile-web settings tree the denylist does not touch at all.**

**AND ONE SETTING HAS TWO SPELLINGS, ONE CAUGHT AND ONE NOT.** LinkedIn's own Help
corpus prints `profile-visibility-for-partners` both ways, for what the articles
describe as the same setting:

    /mypreferences/d/profile-visibility-for-partners           (a518980)  UNCAUGHT
    /mypreferences/d/settings/profile-visibility-for-partners  (a548106)  caught by "/settings/"

This repo has already written the rule that covers this, about the messaging
composer: *"A ruling that one spelling cannot express is not a ruling, it is a
spelling filter."* The same shape has recurred on the settings family.

**This changes no state in this census.** The capability-level ruling in
`update_setting` excludes these regardless of spelling. What is missing is the
second, independent gate the denylist is documented to be -- and the 2026-08-31
fix was per-address where the class has at least ten more members.

### 7.2 -- The comment on `"/settings/"` says it catches nothing current. It catches five live addresses.

The source says:

> *"LinkedIn moved its settings to `/mypreferences/d/`, and the legacy address is
> `/psettings/` ... The only address the old entry ever caught is a `/settings/`
> LinkedIn no longer serves."*

The measurement behind that sentence was taken on the two INDEX urls. Current Help
articles name five per-setting addresses in a third shape the entry does catch:
`discover-me-by-email-address`, `discover-me-by-phone-number`,
`profile-visibility-for-partners`, `data-export-by-page-admins`,
`data-for-ai-improvement`, all under `/mypreferences/d/settings/`. `"/settings/"`
is doing real work today; only the sentence needs changing.
EVIDENCE CLASS: DERIVED -- from Help Center reads (`a548106` read in full,
per-string existence probes), not from a live LinkedIn page load, which this slice
was forbidden.

### 7.3 -- The Open To Work spec and LinkedIn agree on a count and disagree on a member

`set_open_to_work.audiences` enumerates `recruiters only`, `all linkedin members`
and `off`; the spec states that only ONE has ever been observed on this account.
Help `a507508` names three too -- **All LinkedIn Members, Recruiters only, and
"Visible only to you"** -- with no "off". So the reader's third string may never
appear and a fourth it has never met may. The design already handles this
correctly (*"the reader recognises the audience string it has met and refuses to
interpret one it has not"*), so it cannot act wrongly; knowing the name is cheaper
than meeting it.

### 7.4 -- `endorse_or_recommend` names recommendations and argues only about endorsements

The key covers two acts. The reason under it, rewritten 2026-08-30, is entirely a
measurement of ENDORSE controls -- *"zero endorse controls across 13 tracked
fixtures ... zero among the 222 controls read live"* -- and says nothing about
recommendations, whose controls have never been counted. `F3` and `F4` are
excluded by a key that names them and a reason that does not reach them. The old
reason that DID reach them (*"a statement ABOUT ANOTHER PERSON, which is not his
to automate"*) was retired as policy on 2026-08-25.

### 7.5 -- The best-verified write in the package has never successfully written

`linkedin_update_profile_field` is described, in the live server's own MCP
instructions, as *"the only one here that can verify its own outcome by reading the
field back"*. Its complete firing record: shipped 2026-09-02 in `a540461`, driven
end to end, `NAVIGATIONS ATTEMPTED: []`, repaired the same day in `ea5354d`, never
driven again.

**The 2026-09-02 ship-and-repair is still not written into `_audit/` at all.** It
lives in a commit message, a test docstring
(`tests/test_a_performable_action_can_reach_its_control.py:25`), and the untracked
`_TEAM_LEAD_SUCCESSOR_BRIEF.md`. Anyone reading `_audit/` alone finds only the
pre-ship refusal at `_audit/2026-08-31-linkedin-perform.md:3436`, which says the
action REFUSES -- true when written, false since.

### 7.6 -- The intro editor's control set changed completely in two days

23 controls on 2026-08-31, 17 on 2026-09-02, and *"a different set"*: `First name*`
and `Last name*` lost their accessible names entirely, `School*` and `Month`
vanished, `Pronouns` and `Education` appeared, and six new controls including
`Write with AI` arrived. **Every COVERED-UNFIRED and COVERED-CANNOT-DELIVER row in
block A rests on a reading that is now a day old on a surface with a measured
two-day half-life.**

### 7.7 -- Two of this slice's proven reads LAND outside the read boundary

Recorded by `_audit/2026-08-31-linkedin-finish.md:275-279` rather than found here,
and repeated because both landings are in this slice:

* `my_profile` and census `profile` request `/in/me/` and land on
  `/in/<member>/?isSelfProfile=true`, which **FAILS the allowlist**;
* census `settings` requests `/mypreferences/d/` and lands on
  `/mypreferences/d/categories/account`, which **HITS a forbidden substring**.

`assert_read_url` gates the REQUESTED url only; the landed url is never
re-checked. The finish audit measures the settings-page exposure as NIL. So the
`categories/` entry that helps exclude 92 rows is, on one surface, a door this
server is already standing behind.

### 7.8 -- The repo's measurement of the "Open to" menu is CONFIRMED by LinkedIn's documentation

A census of all five profile captures measured the `Open to` button's menu
resolving to exactly three items -- Hiring, Providing services, Finding volunteer
opportunities -- and concluded the entry LinkedIn would have used for job-seeking
*"is absent precisely BECAUSE the setting is already on"*. LinkedIn documents four
items (`a547248` names three: finding a new job, hiring, providing services;
`a6862361` adds finding volunteer opportunities). **Four documented minus the one
already enabled is exactly the three measured.** The repo's inference was right and
is now corroborated from outside.

### 7.9 -- The contact-info panel has six fields and no address field

`a565128` enumerates exactly six: LinkedIn profile link, email address, phone
number, website, instant messenger accounts, birthday. **No address field and no
Twitter/X field.** Revision 1 of this census listed "address" as a contact-info
capability; it is removed. Per-field visibility is documented only for email,
website, birth date and last name (`a545600`) -- **phone and instant messenger have
no documented visibility rule at all.**

### 7.10 -- Eight profile sections are undocumented by LinkedIn itself

Courses, Projects, Publications, Patents, Test scores, Languages, Organizations and
Volunteer experience were each searched BY PRODUCT NAME and each is absent from a
Profile topic index that rendered 55 articles. LinkedIn documents them only as menu
items in `a540837` and one-line descriptions in `a564064`. **The form-field
granularity does not exist on either side of the ledger**, so rows D14-D22 are
counted at section granularity and their sub-fields are uncounted for a reason that
is not this census's fault and cannot be fixed by more searching.

---

### 7.11 -- SOME OF THIS REPOSITORY'S SHARPEST RULINGS LIVE IN TEST DOCSTRINGS, AND THIS CENSUS ALMOST MISSED ONE

Revision 1 scored profile-photo and banner upload as GAP -- "nothing in this repo
has ever considered photo upload". **That was wrong**, and the correction came from
the lead rather than from this census's own method.
`tests/test_readonly.py:306-341` carries a complete, argued, test-enforced ban: it
scans every module for `set_input_files`, PLANTS a mutation to prove the pattern
still bites, and asserts the kind absent from `SANCTIONED_MUTATIONS` by name. Its
docstring states the ground:

> *"UPLOADING IS A DIFFERENT CAPABILITY FROM TYPING. A fill puts his words in a
> box; a file input puts a FILE from this machine into somebody else's inbox,
> chosen by a path string. Nothing in this package should be one edit away from
> that, and the operator has never been asked about it."*

That is EXCLUDED-RULED holding an explicit open question, which is a different
thing from a GAP: somebody decided, wrote it down, made it fail-fast, and named
what remains unanswered.

**THE METHOD DEFECT IS THE FINDING.** This census read `_audit/` (54 files) and the
seven `linkedin_server/` modules. It did NOT read `tests/` -- **74 files, 55,185
lines** -- and a ruling that lives only in a test docstring scores as
never-considered. So **GAP is over-counted and EXCLUDED-RULED under-counted, by an
amount nobody has measured, and in the OPPOSITE DIRECTION to the topic-page
hazard.** The two error sources push apart, which is worse than either alone,
because they do not cancel and neither is bounded.

**WHAT WAS DONE ABOUT IT, and what was not.** After the correction, `tests/` was
swept for ruling-shaped phrases (*"never been asked"*, *"must never"*, *"may not"*,
*"deliberately not"*, *"not a capability"*) and for every subject noun in this
slice. That sweep found the upload ban and found **no test-level ruling** for
recommendations, newsletters, verifications, Service Pages, `/public-profile/`,
or the `details/experience` and `details/education` reads -- zero keyword hits for
each, so those GAPs and D4/D10's CANNOT-DELIVER stand. **A keyword sweep is not a
read of 55,185 lines.** The residual over-count is real, unmeasured, and named here
rather than quietly absorbed.

## 8. THE SET-ASIDE BUCKETS, ITEMISED

**NOT-ENTITLED (13)** -- Premium Career, in India. He cannot do these on LinkedIn
directly either: custom cover image (USA only); cover-image slideshow (Premium
Business / Sales Nav / Recruiter); custom profile CTA button (same); "increase
button visibility" (same); website link in the intro section (Premium Business);
media on a Service Page (Premium Business); Services Showcase with ratings (Premium
Business); "Request services" button across surfaces (Premium); identity
verification via CLEAR (US / Canada / Mexico); workplace verification via an active
Recruiter licence; voluntary self-identification demographic data (US only);
LinkedIn Page notification settings (Page admin); manage Page visit visibility
settings (Page admin).

**RETIRED OR PAUSED BY LINKEDIN (7)** -- measured, not assumed: creator mode toggle
(removed March 2024, `a5999182`; old articles `a522537` and `a524035` both 404);
profile hashtags / topics (removed February 2024); skill assessments (badges removed
from profiles during 2024, `a1690529`); Community Top Voice gold badge (retired
8 October 2024, `a6245087`); Professional sources (removed, data deleted);
educational-institution verification (paused for new applicants); Profinder Pro.

**OWNED BY A SIBLING CENSUS SLICE (14)** -- follow / unfollow a company; follow /
unfollow a person; connections and invitations; the messaging composer and InMail
send; the InMail credit balance as a spend gate; reading the notifications list; job
alerts; job tracker; saved jobs; the apply flow; groups followed; newsletters
subscribed; schools followed; influencers followed. The profile-rendered Interests
section is a genuine boundary between this slice and the network slice and neither
claims it.

**HELP-CENTER DOCUMENTATION (101)** -- troubleshooting pages, FAQs and "how X works"
explainers across the three primary walks. Dropped before mapping so the denominator
counts things he can DO.

**RECOVERY-PASS CONFIRMATIONS (40)** -- of the 60 rows the two product-name passes
returned, 20 were capabilities not already in the denominator and are in the table
above; the other 40 confirmed a row already counted, added field-level detail to one,
or were documentation.

---

## 9. WHAT REVISION 2 CHANGED

| | rev 1 | rev 2 |
|---|---|---|
| mapped capabilities | 240 | 260 |
| COVERED-PROVEN | 19 | 19 |
| COVERED-UNFIRED | 7 | 7 |
| COVERED-CANNOT-DELIVER | -- | 5 |
| EXCLUDED-RULED | 105 | 150 |
| GAP | 109 | 79 |
| uncaught denylist addresses (finding 7.1) | 3 | 6, plus 4 more shapes |
| sources read for rulings | `_audit/` + modules | + a keyword sweep of `tests/` |

Moves: `A2, A4, A6` EXCLUDED-RULED to COVERED-CANNOT-DELIVER (a tool exists and an
instrument fired live and measured it unable to aim). `D4, D10` GAP to
COVERED-CANNOT-DELIVER (`my_profile` declares the field, fires, and returns `None`
by construction). `K1-K6, M9, N4` GAP to EXCLUDED-RULED, on the ruling that the
settings-family argument is capability-level and reaches every page below the
settings index whatever its URL spelling -- a correction to rev 1, which had
assigned those by denylist reachability instead. **Open To Work stays
EXCLUDED-RULED and was NOT promoted to the fifth state**: the fifth state needs a
tool that exists and has fired, and `set_open_to_work` has no tool registered at
all (section 3). `B2, B3, B5, G3` GAP to EXCLUDED-RULED on the test-enforced `set_input_files` ban
(finding 7.11). `D2, D5-D9, D11-D23, E2, E3, G4, G5` -- 23 rows -- GAP to
EXCLUDED-RULED on the `/edit/` family ruling, applied for consistency with the
settings family: rev 1 had treated one argued family refusal as a decision and the
other as a mere mechanism. Twenty new capabilities from the recovery passes.

**Net: GAP fell from 109 to 79, and every row that left it left because a WRITTEN
DECISION was found, never because a capability was.** The actionable list got
shorter and sharper; the server did not get one bit more capable.

The rev-2 split was reconciled against the table row by row rather than carried
forward: an earlier draft of this revision said 149/80 where the rows say 150/79.
The table is the authority and the summary was corrected to it.

---

## 10. WHICH HELP CENTER AREAS WERE WALKED, AND WHICH WERE NOT

**THE REPORTED HAZARD DID NOT REPRODUCE IN THIS SLICE.** Every topic index relied
on here rendered a full article list, checked directly: `a64` Your Profile 55,
`a51` Basics 26, `a153003` Search and Apply for Jobs 49, `a149001` Settings 18,
`a65` Data and Privacy 40. The `0 articles` failure looks specific to Events
(`a150003`) and LinkedIn Live (`a151003`). The recovery passes still added 20
capabilities -- but from products that have **no topic home at all** (Sign in &
security, Visibility, Notifications and Advertising data have no standalone tree),
not from an index that rendered empty. Both failure modes undercount; only the
second is invisible, and this slice did not hit it.

**WALKED** -- five passes, 267 tool calls in the primary walks plus 111 in recovery,
public `linkedin.com/help/linkedin/...` pages only, no login, no account-bearing
page: topic `a64` plus hub `a564064` and `a540837`; topics `a149001`, `a65`,
`a151002`; and product-name searches across the profile sections, the four
index-less settings sections, data rights, and the job-seeking identity surfaces.

**HOLES CLOSED SINCE REVISION 1:**

* the seven notification category names -- found in `a1341821`, an article neither
  earlier-read article linked to. **The names hypothesised in the brief ("Searching
  for a job", "Network catch-up", "Groups", "Pages", "Events") appear only in
  third-party blogs, never in LinkedIn Help.** The earlier refusal to invent them
  was correct.
* "Representing your organization and interests" -- `a566358`, control named
  "Profile information on content".
* "Content language" -- **positively established as NOT EXISTING.** `a521833` names
  one language control and says member content displays in the language it was
  written in, offering only per-item translation.
* the contact-info field list -- `a565128`, a different article from the `a570132`
  the first walk checked.
* the full "Add profile section" menu -- 19 items in three groups.
* the eight undocumented profile sections -- now a MEASURED ABSENCE rather than an
  unwalked area (finding 7.10).

**STILL NOT REACHED -- holes in the denominator, not zeroes:**

1. **`a567169` "Manage Licenses & certifications" is HTTP 404 on all three
   verticals tried**, and no replacement exists in the 55-article Profile index. Its
   content survives only as a cached search snippet, so D13's form fields are
   UNVERIFIED.
2. **Pronouns has no locatable Help Center article, and was never name-searched** --
   the search budget capped on that exact query. Absent from `a64` (55), `a51` (26),
   `a547248` and `a545784`. Status: no article located, **not proven absent.** A18
   and A19 are enumerated from the server's own live control list.
3. **Profile video / Cover Story: my two recovery passes DISAGREE.** One concluded it
   is retired (no member-recorded video documented anywhere; the only cover-* articles
   are cover IMAGE). The other refused that conclusion, noting LinkedIn does publish
   retirement notices -- `a10421005` for Professional sources -- and none exists for
   Cover Story. **Unresolved, and reported as unresolved rather than picked.**
4. **"Message suggestions" and "focused inbox"** -- never reached; the WebSearch
   budget refused those calls. Cannot confirm they exist as settings.
5. **"Social, economic, and workplace research"** -- the literal string is absent
   from `a1340649` and `a1336543`, the two best-matched articles. A settings path was
   harvested for it in the first walk and no article names it.
6. **"Data log" / "Manage data permissions"** -- my two walks disagree: the first
   cites `a1341842` and `/psettings/data-log`; the recovery pass probed `a1340649` and
   found both strings absent. Both can be true (different articles); recorded as a
   disagreement rather than resolved.
7. **Search history view-and-delete** -- no dedicated control documented. "Search
   Queries" exists only as a data-export category.
8. **Close vs delete: what survives** -- `a1347782` covers only the enterprise-account
   precondition and states nothing about what is deleted or any reopen window.
9. **Security keys** -- searched; LinkedIn Help documents passkeys and 2FA and no
   separate hardware-key control. A measured negative.
10. **Audio events** -- three URLs 404'd (`a759884` twice, `a597255`, hub `a173033`).
    L6 rests on a search snippet.
11. **No Help Center page in the profile subtree names a `/in/<vanity>/details/...`
    path.** Probed across seven articles. D4 and D10 are grounded in this repo's
    allowlist and the live skills read, not in LinkedIn's documentation.
12. **Postal code / "location within this area"** -- `a547248` was fetched and names
    only "Location" and "Country/Region". `a548419` "Updated location data available
    to members" exists in `a64` and was NOT fetched; it is the best remaining lead.
13. **About 60 of the 145 first-walk settings rows were read from a topic listing or
    the help search index rather than from the article body.** URLs and titles are
    real; descriptions are snippets. None changed a state assignment, because in every
    case the state was decided by the address family rather than the description.
14. **Mobile-only surfaces were not separated systematically.** A23 and N20 are
    flagged; there are probably others, and a browser-driven server cannot reach any
    of them. `/mwlite/settings` (finding 7.1) is the mobile-web settings tree and
    nothing in this repo has ever named it.

**TWO INSTRUMENT LIMITS THAT BOUND EVERYTHING ABOVE, and they are session-wide
rather than mine:**

* **The WebSearch budget hit its cap at 200/200 mid-recovery**, consumed largely by
  sibling agents in this session. Both recovery passes lost queries to it and both
  kept "NOT REACHED (budget)" strictly separate from "searched and found nothing".
  Items 2, 3 and 4 above are budget casualties, not measured negatives.
* **LinkedIn's own Help search endpoint is dead** -- `/help/linkedin/search?query=`
  returns HTTP 400 and `/help/linkedin/solutions?query=` returns HTTP 404. There is
  no in-house fallback when an external search engine is unavailable, and DuckDuckGo
  and Mojeek returned CAPTCHA / HTTP 403 when tried as substitutes.
* **A method caveat worth carrying to every other slice:** WebFetch summarisation is
  lossy in BOTH directions. The same cached page yielded six settings paths under an
  open prompt and only one under a prompt demanding strict verbatim quoting -- the
  stricter-sounding prompt silently dropped markdown link targets. Every load-bearing
  path in finding 7.1 was confirmed by a per-string existence probe, not by a
  summarising fetch.

---

## 11. WHAT THIS CENSUS DID NOT ESTABLISH

1. **Whether the six aimable intro fields are still aimable.** The reading is from
   2026-09-02, on a surface that changed completely in the two days before it.
   Settling it costs one `linkedin_profile_editor_fields` call and zero writes.
2. **Whether the ten uncaught addresses in finding 7.1 should be denied.** They are
   refused by the allowlist today and excluded by the family ruling, so this is a
   defence-in-depth decision rather than a measurement, and taking it requires no
   page load.
3. **Whether Cover Story exists.** Two independent passes reached opposite
   conclusions; see item 3 of section 10.
