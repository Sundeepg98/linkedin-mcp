# Lane S (settings): the settings of his own account, built behind the grant

Lane S (settings), `ls2-settings-lead`. Brief written by the orchestrator on
2026-09-28; relaunched and run on 2026-10-10 from master `3c8edc2` (CI green,
run 36460989178), on its own worktree branch, never pushed. Not to be confused
with the earlier lane S of 2026-09-28 (people search, the offline frontier),
whose record is `_audit/2026-09-24-lane-s-people-search.md`.

The ruling applied is `HIS-OWN-SETTINGS-NOT-OUTWARD`
(`_audit/2026-09-28-rulings-build-classes.md`, section 2): a setting of his own
account is not an outward act; it is built behind the single-use grant and
live-proven read, benign value, read back, restore the exact original, read
back, one setting at a time, STOP-ALL on any failed restore. Admission stays
by name, one page at a time (`ONE-NAMED-SETTINGS-PAGE-AT-A-TIME`,
`MESSAGING-SETTINGS-CAPABILITY-LEVEL`).

No live load was taken. The live session that was running when this lane
started closed during it; every test here ran on frozen pages.

## 0. What landed, in one screen

* The five build-class rulings of 2026-09-28, copied byte-identical and
  registered (the lane's first commit), and the two gates their registration
  tripped, repaired.
* `linkedin_set_admitted_setting` -- THE GENERIC SETTINGS WRITER. ONE admitted
  settings page, ONE control on it, named by the label LinkedIn draws, behind
  the single-use grant. Only a switch, a radio group or a select; every other
  kind refused by name. Read, set, wait for the control to read it, check that
  ONLY that control moved, Save if the page has one, re-read on a fresh render.
  Module `linkedin_server/settings_writer.py`; the action
  `set_admitted_setting` in `linkedin_server/writes.py`; the tool in one block
  headed "lane S" in `linkedin_server/server.py`.
* ONE PAGE ADMITTED FOR WRITING, the only settings page with a real capture of
  its controls: "Share profile updates", its one switch "Share key profile
  updates".
* ONE ROW MOVED: `P O17` ("share profile updates with your network") split
  from `P O6-O20` and went GAP -> COVERED-UNFIRED by its own bar.
* 93 settings rows enumerated (94 after the split); every other one stays GAP with a capture spec
  (section 5) and a line in `_audit/_census/capture-queue-settings.tsv`.
* The live-proof plan for the live lane (section 6).

## 1. The rows, enumerated

The brief names four sources. All four were walked by a script over the
committed census (`census_completion.walk_cells`, the shipped walk), the
committed `write-classes.tsv` and the committed `blocker-map.tsv`:

    P-R block, P P2 - P P23                                  22 rows
    blocker-map FORBIDDEN-CLASS-FIX-LANDED                    8 rows
      (P B4, P C2-P C6, P O5, P N12)
    blocker-map MESSAGING-SETTINGS                            5 rows
      (M M37, M M41, M M42, M M46, M M50)
    write-classes act profile-setting or notification-preference, and
    every W row whose cell names the settings family or a settings address
                                                            the rest

The union is 115 candidate rows. Each was read and placed IN (a setting of his
own account that a write changes) or OUT (named reason). **93 IN, 22 OUT** --
94 IN after the split of section 4, which adds `P O17`.
Twins are kept as the census keeps them (`N 159`/`P B10`, `N 115`/`P E8`,
`M C88`/`P N26`, `N 170`/`M M42`): two rows, one control, one capture.

The surface each row waits on is my reading of LinkedIn's settings layout from
the census cells, the help articles they cite and the one captured index; it
is UNVERIFIED for every category page until that page is captured, and the
capture settles it. The ACCOUNT category's pages are not a reading: the
captured index draws each one's address (section 5).

IN: 93 rows. OUT: 22 rows. Candidates: 115.

| surface | address | state of the capture | rows (live-proof class) |
|---|---|---|---|
| S0-SHARE-PROFILE-UPDATES | `/mypreferences/d/settings/notify-network-for-updates` (settings page) | CAPTURED (live2/setting.html, 2026-09-28); admitted by name | `P O6-O20` (ALLOWED) |
| C-VISIBILITY | `/mypreferences/d/categories/profile-visibility` (category page) | not captured | `P O4` (VISIBLE), `N 137` (VISIBLE), `N 138` (VISIBLE), `N 139` (VISIBLE), `N 67` (VISIBLE), `N 68` (VISIBLE), `N 69` (VISIBLE), `N 70` (VISIBLE), `N 71` (VISIBLE), `N 72` (VISIBLE), `N 74` (VISIBLE), `N 77` (VISIBLE), `N 159` (VISIBLE), `P B10` (VISIBLE), `M C88` (VISIBLE), `M C89` (VISIBLE), `P N26` (VISIBLE), `N 183` (VISIBLE), `N 115` (VISIBLE), `P E8` (VISIBLE), `N 116` (VISIBLE) |
| C-PRIVACY | `/mypreferences/d/categories/privacy` (category page) | not captured | `P P4` (ALLOWED), `P P5` (ALLOWED), `P P6` (ALLOWED), `P P7` (ALLOWED), `P P8` (ALLOWED), `P N25` (ALLOWED), `M C73` (VISIBLE), `M M35` (ALLOWED), `M M36` (ALLOWED), `M M37` (VISIBLE), `M M39` (VISIBLE), `M M41` (ALLOWED), `M M46` (ALLOWED), `M M50` (ALLOWED), `P M10` (ALLOWED) |
| C-ADS | `/mypreferences/d/categories/ads` (category page) | not captured | `P P10` (ALLOWED), `P P11` (ALLOWED), `P P12` (ALLOWED), `P P13` (ALLOWED), `P P14` (ALLOWED) |
| C-NOTIFICATIONS | `/mypreferences/d/categories/notifications` (category page) | not captured | `P P17` (ALLOWED), `P P18` (ALLOWED), `P P19` (ALLOWED), `P P20` (ALLOWED), `P P21` (ALLOWED), `P P22` (ALLOWED), `P P23` (ALLOWED), `N 58` (ALLOWED), `N 73` (ALLOWED), `N 75` (ALLOWED), `N 78` (ALLOWED), `N 117` (ALLOWED), `N 140` (ALLOWED), `M M24` (ALLOWED) |
| C-SIGNIN | `/mypreferences/d/categories/sign-in-and-security` (category page) | not captured; credential surfaces (question 2) | `P N4` (CREDENTIAL), `P N5` (CREDENTIAL), `P N6` (CREDENTIAL), `P N7` (CREDENTIAL), `P N8` (CREDENTIAL), `P N10` (CREDENTIAL), `P N11` (CREDENTIAL) |
| A-LANGUAGE | `/mypreferences/d/settings/language` (settings page) | drawn on the captured index | `P N15` (CANNOT-BE-PUT-BACK) |
| A-CONTENT-LANGUAGE | `/mypreferences/d/language-for-translation` (settings page) | drawn on the captured index | `P S7` (ALLOWED) |
| A-AUTOPLAY | `/mypreferences/d/settings/autoplay-videos` (settings page) | drawn on the captured index | `P N16` (ALLOWED) |
| A-SOUNDS | `/mypreferences/d/settings/enable-sounds-desktop` (settings page) | drawn on the captured index | `P N17` (ALLOWED) |
| A-PROFILE-PHOTOS | `/mypreferences/d/settings/show-profile-photos` (settings page) | drawn on the captured index | `P N18` (ALLOWED) |
| A-PREFERRED-VIEW | `/mypreferences/d/settings/preferred-view` (settings page) | drawn on the captured index | `M C100` (ALLOWED) |
| A-SYNCING | `/mynetwork/settings/manage-syncing/` (settings page) | drawn on the captured index (twice: calendar, contacts) | `P N20` (ALLOWED), `P N21` (CANNOT-BE-PUT-BACK) |
| A-MICROSOFT | `/mypreferences/d/connected-microsoft-accounts` (settings page) | drawn on the captured index | `P N23` (ALLOWED) |
| A-BASIC-INFO | `/profile/edit-basic-info` (editor page) | drawn on the captured index | `P N19` (VISIBLE) |
| A-DEMOGRAPHIC | `/mypreferences/d/demographic-info-copy` (settings page) | drawn on the captured index; reading it reads his self-identification answers (question 3) | `P S6` (SENSITIVE) |
| O-PUBLIC-PROFILE | `/public-profile/settings` (settings page) | named by the census; not captured | `P C2` (CANNOT-BE-PUT-BACK), `P C3` (VISIBLE), `P C4` (VISIBLE), `P C5` (VISIBLE), `P C6` (CANNOT-BE-PUT-BACK), `P B4` (VISIBLE) |
| O-GUEST-CONTROLS | `/psettings/guest-controls` (legacy settings address) | named by the census; may redirect | `P C7` (ALLOWED) |
| O-PERMITTED-SERVICES | `/psettings/permitted-services` (legacy settings address) | named by the census; may redirect | `P N24` (ALLOWED) |
| O-GENAI-DATA | `/mypreferences/d/settings/data-for-ai-improvement` (settings page) | named by census finding 7.2 | `P P9` (ALLOWED) |
| O-MEMBER-COOKIES | `/mypreferences/d/member-cookies` (settings page) | named by census finding 7.1 | `P P16` (ALLOWED) |
| O-JOB-APPLICATION-SETTINGS | `/jobs/application-settings/` (settings page) | named by the census; refused on an ACT substring (READ-PAST-AN-ACT-SUBSTRING) | `P M7` (ALLOWED), `P M8` (VISIBLE) |
| O-GROUP-SETTINGS | `/psettings/group/<id>/` (per-group settings page) | named by the census; the address carries a group id (question 4) | `N 176` (ALLOWED), `M M42` (ALLOWED), `N 170` (ALLOWED) |
| O-BADGE | `/badges/profile/create` (creation page) | named by the census; refused on '/create', an ACT substring (READ-PAST-AN-ACT-SUBSTRING) | `P O5` (ALLOWED) |
| O-SIGNIN | `/uas/login` (sign-in surface) | READ-PAST does not reach a sign-in surface (question 2) | `P N12` (CREDENTIAL) |
| X-POSITION-EDITOR | `his experience editor (per-edit control)` (editor dialog) | not a settings page | `P D7` (VISIBLE) |
| X-ACTIVITY-SECTION | `his profile's Activity section` (profile section) | not a settings page; queued DEFAULT-ACTIVITY-FORM | `P G2` (ALLOWED) |

| row | capability | surface | live-proof class | note |
|---|---|---|---|---|
| `P O6-O20` | fifteen further visibility toggles: contact-info and email visibility, connection-list visibility, who can see | S0-SHARE-PROFILE-UPDATES | ALLOWED | SPLIT: 'share profile updates with your network' is the admitted switch (BUILT); the other 14 toggles stay GAP on C-VISIBILITY |
| `P O4` | Profile viewing options (his own browsing mode) | C-VISIBILITY | VISIBLE | profile viewing options: the radio group N 137-139 name its three values |
| `N 137` | Set your profile viewing option to "Your name and headline" | C-VISIBILITY | VISIBLE | a value of P O4's radio group |
| `N 138` | Set your profile viewing option to private characteristics | C-VISIBILITY | VISIBLE | a value of P O4's radio group |
| `N 139` | Set your profile viewing option to private mode | C-VISIBILITY | VISIBLE | a value of P O4's radio group |
| `N 67` | Limit who can follow you to your 1st-degree connections | C-VISIBILITY | VISIBLE | who can follow you |
| `N 68` | Allow everyone on LinkedIn to follow you | C-VISIBILITY | VISIBLE | who can follow you (the other value) |
| `N 69` | Make Follow the primary action on your profile | C-VISIBILITY | VISIBLE | primary profile action |
| `N 70` | Make Connect the primary action on your profile | C-VISIBILITY | VISIBLE | primary profile action (the other value) |
| `N 71` | Set who can see the members you follow | C-VISIBILITY | VISIBLE | who can see members you follow |
| `N 72` | Choose who can send you invitations to connect | C-VISIBILITY | VISIBLE | who can send you invitations |
| `N 74` | Choose whether your connections can see your connections list | C-VISIBILITY | VISIBLE | connections-list visibility |
| `N 77` | Control whether you appear in the connections-who-follow-a-Page list | C-VISIBILITY | VISIBLE | appearing in a Page's connections-who-follow list |
| `N 159` | Enable or disable Open Profile on your own profile | C-VISIBILITY | VISIBLE | Open Profile (Premium); twin of P B10 |
| `P B10` | Open Profile setting (who may message without connecting) | C-VISIBILITY | VISIBLE | Open Profile (Premium); twin of N 159 |
| `M C88` | Choose whether members can mention, tag or collaborate with you | C-VISIBILITY | VISIBLE | mentions, tags, collaborations; twin of P N26 |
| `M C89` | Set the visibility of mentions and tags | C-VISIBILITY | VISIBLE | visibility of mentions and tags |
| `P N26` | Mentions, tags and collaborations permission | C-VISIBILITY | VISIBLE | mentions, tags, collaborations; twin of M C88 |
| `N 183` | Receive event invitations only from your 1st-degree connections | C-VISIBILITY | VISIBLE | who may invite him to events |
| `N 115` | Opt out of receiving endorsements entirely | C-VISIBILITY | VISIBLE | opt out of endorsements; twin of P E8 |
| `P E8` | Opt out of endorsements entirely | C-VISIBILITY | VISIBLE | opt out of endorsements; twin of N 115 |
| `N 116` | Manage endorsement settings | C-VISIBILITY | VISIBLE | endorsement settings |
| `P P4` | Change or correct his data -- the data right "Change or Correct Data" | C-PRIVACY | ALLOWED | a data-rights REQUEST, not a switch; the capture says what it draws |
| `P P5` | Restrict or object to the use of his data -- the data right "Restrict or Object to the use of Data" | C-PRIVACY | ALLOWED | a data-rights REQUEST, not a switch; the capture says what it draws |
| `P P6` | Salary data: the settings page for the salary data he has shared with LinkedIn | C-PRIVACY | ALLOWED | salary data page; a delete half would split off (census cell) |
| `P P7` | Research invitations: whether LinkedIn may invite him to take part in research | C-PRIVACY | ALLOWED | research invitations |
| `P P8` | Harmful message detection: turn it on or off | C-PRIVACY | ALLOWED | harmful message detection |
| `P N24` | Permitted Services -- third-party app access | O-PERMITTED-SERVICES | ALLOWED | third-party app access |
| `P N25` | LinkedIn Services (DMA) connect / disconnect | C-PRIVACY | ALLOWED | LinkedIn services (DMA) connect / disconnect; nav path only |
| `M C73` | Allow or disallow your posts being embedded | C-PRIVACY | VISIBLE | embedding of his posts |
| `M M35` | Choose Messaging inbox layout | C-PRIVACY | ALLOWED | messaging inbox layout |
| `M M36` | Manage how new conversations open (conversation windows) | C-PRIVACY | ALLOWED | conversation windows |
| `M M37` | Turn read receipts and typing indicators on or off | C-PRIVACY | VISIBLE | read receipts and typing indicators (others see them) |
| `M M39` | Set or edit an away message (Premium) | C-PRIVACY | VISIBLE | away message (Premium): a TYPED message, a refused kind; its switch half alone is settable |
| `M M41` | Manage smart features in Messaging | C-PRIVACY | ALLOWED | smart features in messaging |
| `M M46` | Opt out of receiving InMail messages | C-PRIVACY | ALLOWED | InMail opt-out |
| `M M50` | Manage LinkedIn message nudges | C-PRIVACY | ALLOWED | message nudges |
| `P M7` | Opt out of saving job application data | O-JOB-APPLICATION-SETTINGS | ALLOWED | opt out of saving job application data |
| `P M8` | "Share resume data with recruiters" toggle | O-JOB-APPLICATION-SETTINGS | VISIBLE | share resume data with recruiters |
| `P M10` | Autofill for work emails | C-PRIVACY | ALLOWED | autofill for work emails |
| `P C7` | Guest controls / cookie consent | O-GUEST-CONTROLS | ALLOWED | guest controls / cookie consent |
| `P P9` | Data for generative AI improvement: whether LinkedIn may use his data to train its content-generating AI | O-GENAI-DATA | ALLOWED | data for generative AI improvement |
| `P P10` | Profile data LinkedIn uses to show him ads | C-ADS | ALLOWED | profile data for ads |
| `P P11` | Activity and inferred data LinkedIn uses to show him ads | C-ADS | ALLOWED | activity and inferred data for ads |
| `P P12` | Off-LinkedIn data LinkedIn uses to show him ads | C-ADS | ALLOWED | off-LinkedIn data for ads |
| `P P13` | Ads personalization | C-ADS | ALLOWED | ads personalization |
| `P P14` | Demographic data LinkedIn uses to show him ads | C-ADS | ALLOWED | whether ads use his demographic data: the switch records no attribute itself; P S6 is the attribute page |
| `P P16` | Cookie preferences: his cookie consent as a signed-in member | O-MEMBER-COOKIES | ALLOWED | his cookie consent |
| `P P17` | Choose which notifications about invitations and messages he gets, and on which channels | C-NOTIFICATIONS | ALLOWED | category: invitations and messages; channels are its parameter |
| `P P18` | Choose which notifications about jobs and opportunities he gets, and on which channels | C-NOTIFICATIONS | ALLOWED | category: jobs and opportunities |
| `P P19` | Choose which notifications about activity that involves him he gets, and on which channels | C-NOTIFICATIONS | ALLOWED | category: activity that involves him |
| `P P20` | Choose which notifications about news and articles he gets, and on which channels | C-NOTIFICATIONS | ALLOWED | category: news and articles |
| `P P21` | Choose which notifications about offers and tips from LinkedIn he gets, and on which channels | C-NOTIFICATIONS | ALLOWED | category: offers and tips |
| `P P22` | Choose which notifications about updates from events he gets, and on which channels | C-NOTIFICATIONS | ALLOWED | category: updates from events |
| `P P23` | Job-post email notifications: whether he gets them | C-NOTIFICATIONS | ALLOWED | job-post emails; folds into P P18 if it is that row's email channel |
| `N 58` | Unsubscribe from newsletter emails while staying subscribed on the feed | C-NOTIFICATIONS | ALLOWED | one newsletter's emails |
| `N 73` | Turn Page / Event / Newsletter invitations on or off | C-NOTIFICATIONS | ALLOWED | Page / Event / Newsletter invitations |
| `N 75` | Opt out of receiving invitations to follow Pages | C-NOTIFICATIONS | ALLOWED | invitations to follow Pages |
| `N 78` | Manage notifications about your connections' activity | C-NOTIFICATIONS | ALLOWED | connections' activity |
| `N 117` | Manage skill-endorsement notifications | C-NOTIFICATIONS | ALLOWED | skill-endorsement notifications |
| `N 140` | Unsubscribe from Who's-viewed-your-profile emails | C-NOTIFICATIONS | ALLOWED | who-viewed-your-profile emails |
| `M M24` | Manage group-chat notification settings | C-NOTIFICATIONS | ALLOWED | group-chat notifications |
| `P N15` | Interface language | A-LANGUAGE | CANNOT-BE-PUT-BACK | interface language: once changed, every label LinkedIn draws changes language, so the control can no longer be found by its admitted label to put it back |
| `P S7` | Choose the content language, a settings page apart from the interface language | A-CONTENT-LANGUAGE | ALLOWED | content language |
| `P N16` | Autoplay videos | A-AUTOPLAY | ALLOWED | autoplay videos |
| `P N17` | Sound effects | A-SOUNDS | ALLOWED | sound effects |
| `P N18` | Showing other members' profile photos | A-PROFILE-PHOTOS | ALLOWED | showing other members' photos (a display preference) |
| `M C100` | Choose the feed's default view: most relevant or most recent posts | A-PREFERRED-VIEW | ALLOWED | preferred feed view (also HIS-OWN-CURATION-NOT-OUTWARD) |
| `P N20` | Calendar sync | A-SYNCING | ALLOWED | calendar sync |
| `P N21` | Contact / address-book sync | A-SYNCING | CANNOT-BE-PUT-BACK | contact sync: turning it on uploads other people's contact data, which turning it off does not withdraw |
| `P N23` | Partners and services / Microsoft account link | A-MICROSOFT | ALLOWED | Microsoft account link |
| `P N19` | Name / location / industry via settings | A-BASIC-INFO | VISIBLE | name, location, industry: typed and autocomplete fields, refused kinds; the intro editor rows carry them |
| `P S6` | Personal demographic information, a page of the account settings | A-DEMOGRAPHIC | SENSITIVE | personal demographic information |
| `P C2` | Customise the public profile URL | O-PUBLIC-PROFILE | CANNOT-BE-PUT-BACK | custom public URL: releasing an address another member may take, and every link to it breaks |
| `P C3` | Public profile visibility master switch | O-PUBLIC-PROFILE | VISIBLE | public profile master switch |
| `P C4` | Per-section public visibility toggles | O-PUBLIC-PROFILE | VISIBLE | per-section public visibility |
| `P C5` | Search-engine visibility of the public profile | O-PUBLIC-PROFILE | VISIBLE | search-engine visibility |
| `P C6` | Unlink a prior public URL | O-PUBLIC-PROFILE | CANNOT-BE-PUT-BACK | unlinking a prior public URL |
| `P B4` | Profile photo visibility audience | O-PUBLIC-PROFILE | VISIBLE | profile photo audience |
| `P N4` | Two-step verification on / off | C-SIGNIN | CREDENTIAL | two-step verification |
| `P N5` | Change password | C-SIGNIN | CREDENTIAL | change password: a typed field, a refused kind |
| `P N6` | Passkeys add / delete | C-SIGNIN | CREDENTIAL | passkeys |
| `P N7` | Email addresses -- add / remove / change primary | C-SIGNIN | CREDENTIAL | email addresses |
| `P N8` | Phone numbers -- add / remove / choose reset number | C-SIGNIN | CREDENTIAL | phone numbers |
| `P N10` | Sign out of one session / all sessions | C-SIGNIN | CREDENTIAL | sign out of sessions: ends this server's own session |
| `P N11` | Devices that remember your password | C-SIGNIN | CREDENTIAL | devices that remember the password |
| `P N12` | Keep me logged in / auto sign-in | O-SIGNIN | CREDENTIAL | keep me logged in, on the sign-in page |
| `N 176` | Prevent your network being updated when you join a group | O-GROUP-SETTINGS | ALLOWED | network updates when he joins a group; queued GROUP-SETTINGS-PAGE |
| `M M42` | Settings to allow or prevent messages from group members | O-GROUP-SETTINGS | ALLOWED | messages from group members; twin of N 170 |
| `N 170` | Allow or prevent other group members from messaging you | O-GROUP-SETTINGS | ALLOWED | messages from group members; twin of M M42 |
| `P O5` | Public profile badge creation | O-BADGE | ALLOWED | public profile badge: creates an embed snippet, not a setting the writer sets |
| `P D7` | Notify network of a job change | X-POSITION-EDITOR | VISIBLE | the per-edit 'notify network' control in the position editor; its standing default is the admitted switch |
| `P G2` | Activity section default view | X-ACTIVITY-SECTION | ALLOWED | Activity section default view; its own queue stands |

| row | capability | why it is not a settings write of his own account |
|---|---|---|
| `P P2` | Delete his data -- the data right LinkedIn names "Delete Data" | EXCLUDED-RULED on ACCOUNT-DESTRUCTION-STAYS-MANUAL (deleting his data); stays |
| `P P3` | Get a copy of his data -- the data right "Access and Download Data": request an archive and download it, in ei | a READ (get a copy of his data); not a write row -- its blocker stands, and C-PRIVACY's capture serves it |
| `P P15` | See his advertising-data settings: the Advertising data page | a READ (the advertising-data page); not a write row -- C-ADS's capture is its page |
| `P N27` | Merge or close duplicate accounts | EXCLUDED-RULED on ACCOUNT-DESTRUCTION-STAYS-MANUAL |
| `P N28` | Close (delete) account | EXCLUDED-RULED on ACCOUNT-DESTRUCTION-STAYS-MANUAL and '/close-accounts' |
| `P N29` | Hibernate account | EXCLUDED-RULED on '/hibernate-account' |
| `P O21` | Block / unblock a member | blocking a member is a relation act toward another member (RELATION-REMOVALS-BUILT-BEHIND-GRANTS), not his setting |
| `N 142` | Unblock a member | unblocking a member: the inverse of a relation act toward another member, not his setting |
| `M C97` | Delete a notification | deleting one notification card is curating his own item (HIS-OWN-CURATION-NOT-OUTWARD), not a setting |
| `M C52` | Manage your LinkedIn feed preferences (follow / unfollow topics and sources) | following and unfollowing topics and sources is curation (HIS-OWN-CURATION-NOT-OUTWARD); its page is behind '/unfollow' |
| `N A7` | Turn on automatic invitations to content engagers (Premium) | an admin act on a Page or group he administers, not his account's setting |
| `N A8` | Turn off automatic invitations (Premium) | an admin act on a Page or group he administers, not his account's setting |
| `P A24` | ID name as additional name | identity verification, queued CREDENTIAL-OPERATOR-ONLY; not a setting |
| `P K2` | Identity verification via DigiLocker (India -- his route) | identity verification (DigiLocker); not a setting |
| `P K3` | Workplace verification by work email | workplace verification; not a setting |
| `P K4` | Workplace verification via Microsoft Entra Verified ID | workplace verification; not a setting |
| `P K5` | Workplace verification via a company LinkedIn Learning licence | workplace verification; not a setting |
| `P K6` | Phone number verification | phone verification; not a setting |
| `P M1` | Upload a resume from Job Application Settings | uploading a resume: the uploads lane's verb |
| `P M3` | Delete a saved resume | deleting stored application data, queued JOB-APPLICATION-SETTINGS: deletion of his own item |
| `P M6` | Saved screening-question answers | stored screening answers: records he edits, not a setting (R/W) |
| `P M9` | Stored job applicant accounts | stored applicant accounts: records he views or removes, not a setting (R/W) |

## 2. The exclusions the ruling names, per row

Every IN row carries one live-proof class:

    ALLOWED              49   proven read, benign value, read back, restore, read back
    VISIBLE              31   ALLOWED, and the change shows to other members:
                              restored inside the same minute (question 5)
    CREDENTIAL            8   CREDENTIAL-SETTINGS-NEED-THE-OPERATOR's set: built,
                              never live-proven unless he names it
    CANNOT-BE-PUT-BACK    4   built, never live-proven unless he names it
    SENSITIVE             1   built, never live-proven unless he names it

The four that cannot be put back exactly, and why:

* `P C2` custom public URL and `P C6` unlinking a prior one -- the ruling's own
  examples: an address released may be taken by another member, and every
  link to his profile from his resume and his applications breaks.
* `P N21` contact sync -- turning it on uploads other people's contact data,
  and turning it off does not withdraw what was uploaded.
* `P N15` interface language -- MY APPLICATION, stated as one: once the
  language changes, every label LinkedIn draws changes with it, so the switch
  back cannot be found by its admitted English label. This writer could not
  put it back; only he could, by hand (question 6).

The one SENSITIVE row is `P S6`, his personal demographic information: a test
value would itself assert an attribute. `P P14` (whether ads may use his
demographic data) is a switch that records no attribute and is ALLOWED.

## 3. The generic settings writer

### 3.1 What it is

`linkedin_set_admitted_setting(settings_page, control, value, confirm_token="")`
(`settings_page`, never `page`, which in this package means a browser page). Two
calls; the first loads the page, reads the control and returns a block naming
the PAGE, the CONTROL, its CURRENT value and the REQUESTED one, what each value
means, whether anybody else sees the change, how the page stores it, and the
live-proof class -- with a token bound to exactly that page, control and value
for two minutes. The second call, with the token, acts.

* ADMISSION: `settings_writer.ADMITTED_PAGES`. A page enters by its NAME (the
  heading LinkedIn draws) with every control described from a real capture.
  The target `<page> / <control> :: <value>` is resolved and respelled in
  LinkedIn's own words in `writes._target_for`, the one point preview and mint
  both pass, so an unadmitted page, control or value is refused before any page
  loads and before any token exists.
* THE ADDRESS is the registry's constant for the page's name
  (`url_target_of`); a page may veto an act, never supply its address. The
  write door's pattern admits the admitted addresses and nothing beside them;
  the address trips `"/settings/"` and `"settings"`, which the spec excuses by
  equality through a new `WriteSpec.exempt_substrings` -- the one-entry
  `exempt_substring` is unchanged for every other action. The read door is the
  shipped one; the page was already admitted for reading.
* KINDS: a switch, a radio group, a select (`check_kind`). A text field,
  textarea, autocomplete, checkbox list, button, link and file input are
  refused by name, with why.
* READ: counts and booleans through Playwright's role engine; every doubt is
  `unknown` -- a name drawn twice (in either spelling, switch or checkbox), an
  undeclared choice or option, nothing checked, a checked property that
  disagrees with aria-checked, a landing that did not keep the address.
* PRESS: through `writes.perform`'s one click site (a switch by its own name,
  a radio group on the radio named for the destination) or its one
  `select_option` site (a select, by the option's label). Nothing new is added
  to `readonly.SANCTIONED_MUTATIONS`; the press is strict (a second match at
  press time throws).
* WAIT: `profile_editor.wait_for_state`, the bounded liveness wait of
  `c3b2393`, for the control to read the requested value.
* ONLY THAT CONTROL MOVED: every switch, checkbox, radio and select on the page
  is read before the press and after it, position by position, and the page
  may move exactly what one press of the control's kind moves -- one checkable
  for a switch, two radios for a group, one select -- and nothing else. A
  select's value is compared in this process and never leaves it.
* SAVE: only if that holds and the page draws one (exactly one enabled control
  of that name). A page whose capture drew no Save stores on the press; if
  another control moved there, the change is already stored and the receipt
  says STOP.
* VERIFY: a fresh navigation to the page and a re-read of the control;
  `performed` is true, false or "unknown".
* RESTORE: the receipt's `restore` block holds the value the click-time read
  found and the exact call that puts it back. Nothing restores on its own.

The one admitted page, measured on its capture (the live lane's session 2,
2026-09-28, tracked as the skeleton `tests/fixtures/live2/setting.html`; the
raw page stays in that lane's gitignored session state): the heading "Share
profile updates", ONE `input[type=checkbox][role=switch]` named through
`aria-labelledby` "Share key profile updates", read off, the text "Off" beside
it, a Back link, and NO button and NO form in `main` -- so the press is the
store. The settings index calls the same setting "Sharing profile edits";
neither that name nor the heading names a control on the page, which a test
holds.

### 3.2 Red first

* The end-to-end file `tests/test_set_admitted_setting.py` was written before
  the integration and run against it: **5 failed, 1 passed** (the one that
  passed refused because the action did not exist yet, which is why it is not
  counted as evidence). After the integration: **6 passed** -- the real page
  previewed off -> on, confirmed, pressed, read on with nothing else moved, and
  verified on a fresh render; a fresh render still off reported false; the
  token bound to its value; a no-op refused; an unadmitted page, control or
  value loaded nothing and minted nothing; and the three synthetic patterns,
  registered at the admitted address, through the shipped doors -- a select
  saved once, a select whose choice also moved a second select NOT saved, a
  late choice and a late radio waited for, a switch whose press also flipped
  another reported with STOP, an inert press reported not moved.
* Seven guards of the module were each broken alone in a copy-restored file
  and the test meant to catch each was run. Six were caught at once. ONE WAS
  NOT: loosening the switch reader's name count from "exactly one" to "at least
  one" still read the two-switches world as unknown, through a later step, so
  the test could not say which guard held. The case that guard exists for is a
  switch and a checkbox sharing one name, where the loosened reader reads a
  state while another control answers to the same name. The fixture gained
  that case and the test now requires the count's own refusal; re-run, the
  mutation is caught. All seven: caught. The file was restored byte-identical
  after each (sha256 checked).

| guard broken | caught by |
|---|---|
| M1 the switch reader's exact-one name count | `test_the_switch_reader_and_a_press_on_div_switches` (after the fixture gained a switch and a checkbox sharing a name) |
| M2 only-that-control-moved compares only its own kind | `test_only_that_control_moved` |
| M3 a radio group with an undeclared choice is read | `test_the_radio_group_reader_and_a_press_on_the_destination` |
| M4 a landing elsewhere is read as the page | `test_a_landing_elsewhere_reads_unknown_whatever_the_page_drew` |
| M5 a second or disabled Save is pressed | `test_the_select_reader_the_choice_and_the_save_gate` |
| M6 a page name admitted case-folded | `test_a_page_and_a_control_are_admitted_by_their_exact_names` |
| M7 a refused kind accepted | `test_a_kind_that_is_not_a_switch_radio_group_or_select_is_refused_by_name` |
| W1 (`writes.py`) Save asked for without the only-that-control-moved check | `test_the_three_patterns_through_the_shipped_doors` (a select that moved a second select was saved) |
| W2 (`writes.py`) the write door ignores `exempt_substrings` | `test_the_write_door_admits_the_admitted_page_and_exempts_only_its_own_two_substrings` |
| W3 (`writes.py`) the select path skips its wait and its check | `test_the_three_patterns_through_the_shipped_doors` |
| W4 (`writes.py`) a landing elsewhere is pressed on | `test_a_landing_elsewhere_is_refused_before_any_press` |

The four `writes.py` mutations ran the same way, on the integration's own
hooks, after it landed: all four caught, the file restored byte-identical.

### 3.3 What the shipped guards caught in the integration, and what changed

* `tests/test_unverifiable_outcomes.py` finds an action's verification branch
  by its LITERAL name; the first draft compared `spec.action` against the
  module's constant, so the branch was invisible to it. Every comparison in
  `writes.py` now spells `"set_admitted_setting"`, and a test pins the
  module's constants to the same strings.
* `tests/refusinggrant.py` builds one synthetic target per TARGET KIND, and
  `setting_and_value`'s sample is dark mode's. This action checks its target
  against the admitted registry in `_target_for`, so the sample was refused --
  and the refusal stopped the reader-leak guard's whole measurement, not one
  spec. The harness gained a per-action sample read from the registry; two
  more tests that key targets by kind gained the same.
* THE READER-LEAK GUARD CAUGHT A REAL PROPERTY: the first snapshot RETURNED
  each select's `input_value()`, which is text the page chose, although only
  equality is ever asked of it. The value is now reduced to a digest inside
  the reader, and the test holds the whole snapshot free of the values.
* The guard discovers every coroutine taking a parameter called `page` as a
  page reader, and the tool's first draft named the admitted page's NAME
  `page`. It is `settings_page` now.
* The guard records `read_control` and `save_gate` as not driven (it cannot
  build their `AdmittedControl` / `AdmittedPage` arguments) and `snapshot` as
  clean. Both are driven by `tests/test_settings_writer.py` over the synthetic
  pages and the real capture, and each returns only declared values,
  constants and counts.

## 4. The row moved

**`P O17`: GAP -> COVERED-UNFIRED**, split from `P O6-O20` under
COMPOUND-ROW-SPLITS-ONLY-ON-STATE. "Share profile updates with your network"
is one of the fifteen toggles `O6-O20` collapsed; its page is captured and its
switch is built on that capture, the other fourteen are not, so the halves need
different states. Its bar is the census's own: code aimed at real captured
markup that has never returned a live payload. The code is the writer above;
the markup is the tracked skeleton of the live capture; nothing fired. Its cell
cites `RELEASED BY HIS-OWN-SETTINGS-NOT-OUTWARD`, registered as a release in
`scripts/ruling_holds.py`, so its live proof is held by no ruling: a setting of
his own needs no named target.

`P O6-O20` stays GAP with its fourteen, its blocker restated: each waits on its
page's capture (first the Visibility category page) and that page's admission.

Every other IN row stays GAP. Its write is built -- the same writer -- and what
it lacks is its page in the registry, which needs a capture of the page and
the page's admission by name.

## 5. The capture specs

`_audit/_census/capture-queue-settings.tsv` holds one line per uncaptured
surface a GAP row waits on: 23 lines, columns surface-id, address, presses,
save, loads, searches, rows. Every capture is a ZERO-PRESS load: the page is
loaded and read; nothing on it is pressed.

What to save, per line:

* a CATEGORY page: the raw page in the live lane's gitignored state; a tracked
  skeleton (`scripts/_build_capture_skeleton.py`); every settings link it draws
  -- address and LinkedIn's label. The index capture of 2026-09-23 is the
  model: it drew the ACCOUNT category's links and no control at all.
* a SETTINGS page: the raw page; a tracked skeleton; per control, its kind,
  accessible name, the names of its values and its current state; whether
  `main` draws a Save; and the landed address (a legacy `/psettings/` address
  may redirect, and a redirect is recorded, not followed).

Grouped so one load captures several rows: the Visibility category page
serves 21 rows, Data privacy 15, Notifications 14, Advertising data 5, and
"Public profile settings" 6. The ACCOUNT category was captured on 2026-09-23 and
drew these addresses, so their pages need no category load first: language,
content language, autoplay videos, sound effects, showing profile photos,
preferred feed view, syncing (calendar and contacts on one page), the
Microsoft link, basic info and personal demographic info.

ADMISSION. Every one of these addresses is refused by the read boundary today,
and each is admitted by name, one at a time, before its load
(ONE-NAMED-SETTINGS-PAGE-AT-A-TIME; question 1). Two are refused on an ACT
substring and fall under `READ-PAST-AN-ACT-SUBSTRING`: the job application
settings page (`"/jobs/application"`) and the badge page (`"/create"`). Not in
the queue, with the reason:

* `/uas/login` (`P N12`) -- a sign-in surface, which READ-PAST does not reach
  (question 2);
* his position editor (`P D7`) and his profile's Activity section (`P G2`) --
  not settings pages; their own rows' editor captures carry them.

LOADS. 23 lines at one load each, of which three wait on a question (the
Sign in & security category, the demographic page, a group's settings page),
so **20 loads clear without a ruling**. The category loads then name the
settings pages below them: the 55 rows behind the four category pages sit on
pages not yet seen, at most one load each and fewer where pages are shared.

## 6. The live-proof plan (the live lane runs it, not this lane)

### 6.1 The rule, per setting

1. READ: a preview of the setting's change (one load), which reads the current
   value off the control and mints a token.
2. BENIGN VALUE: the opposite of what was read (a switch), or for a group or a
   select the value that changes the least for others; confirm the token (one
   load to the page, one load for the verification's fresh render).
3. READ BACK: the verification is the read back; `performed` must be true and
   `setting_press.check.proceed` true.
4. RESTORE THE EXACT ORIGINAL: the receipt's `restore.to_put_it_back` call --
   preview (one load), confirm (two loads).
5. READ BACK AGAIN: the restore's verification, and one more preview naming the
   restored value's opposite, never confirmed (one load): it reads the value
   off the control a second time and its token expires unused.

ONE SETTING AT A TIME: nothing else runs between step 2 and step 5, and no
other write runs while any setting is away from its original. STOP-ALL: if the
restore's `performed` is not true, or `setting_press` carries `stop`, every
write stops; the page is opened by hand and every control on it put back
before anything else.

### 6.2 The one built setting: "Share key profile updates"

    load 1  preview  value="on"   reads the current value (the capture read off;
                                  if it reads on, swap on and off throughout)
    load 2  confirm               the press, on the page
    load 3                        the verification's fresh render: must read on
    load 4  preview  value="off"  the restore's preview: must read on
    load 5  confirm               the press
    load 6                        the verification: must read off
    load 7  preview  value="on"   an independent read: must read off; never confirmed

**SEVEN LOADS.** At the session's spacing of 20 s per load
(LIVE-BUDGET-40-LOADS) the switch is away from off from the press at load 2
to the press at load 5, about 60 s. While it reads on, a profile edit could be
shared with his network, so NO profile edit runs from load 2 to load 6, and
the intro-edit rows' condition 1 is unaffected because it reads this switch
before any edit. Nobody else sees the switch itself.

### 6.3 The order for the settings still to be built

When their pages are captured and admitted: first the ones nobody else sees
(autoplay, sound effects, other members' photos, preferred feed view, content
language, the advertising and research switches, the notification
categories), then the VISIBLE ones, each restored inside the same minute and
read before and after, never two in a row without a read between. The
CREDENTIAL, CANNOT-BE-PUT-BACK and SENSITIVE rows are never in the plan unless
he names them.

## 7. The side tables

* `write-classes.tsv`: `P O17` enters as a built line,
  `built:set_admitted_setting`, act profile-setting, R3 -- the split moves to
  16 R1 + 37 R2 + 337 R3 = 390. The IN rows that were `classify-only` are
  queued on their surface's capture, `queued:SETTINGS-<surface-id>`; rows
  another lane had already queued keep their queue (`P G2`, `N 176`).
* The census cells of the IN rows each gain one sentence naming the writer,
  their surface's line in the capture queue, and their live-proof class.

## 8. Pins re-derived, each from its measured value

* `tests/census_row_pin.json` by `scripts/pin_census_rows.py --write`, with
  `PINNED_ROW_TOTAL` 771 -> 772 and `PINNED_SLICE_ROWS` P 236 -> 237.
* `census_completion.PINNED`, nine figures, each +1: stated_rows 772,
  capabilities 786, capabilities_achievable 748, achievable 734, adjudicated
  185, delivered_broad 131, unfired 30, b1_no_ruling 13, b1_released 2; and
  `PINNED_B1_ROWS` gains `P O17` under no ruling.
* The write-classes split (16, 37, 336) -> (16, 37, 337).
* The tool surface: 61 -> 62 tools, 96 -> 100 parameters; writes.PERFORMABLE
  and the hand-typed write lists in `tests/test_server_surface.py`; the server
  instructions and the module docstring's counts (forty-four read, eighteen
  write, sixty-two; nineteen actions, eighteen tools); the strict-press set.

## 9. Gates run

(filled at the lane's close)

## 10. Questions for the orchestrator

Each with its ground quoted. None blocks anything this lane built; each blocks
captures or live proofs the live lane would otherwise take.

1. **ADMITTING THE CAPTURE QUEUE'S PAGES -- ONE AT A TIME, OR AS A BATCH?**
   Ground: `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME`, *"ONE NAMED settings page
   below /mypreferences/d/ is admitted, one at a time"*; the brief: *"each
   settings page is admitted by NAME, exactly, with a control shown failing"*.
   Twenty pages clear without any other ruling (section 5), the four category
   pages first. May the live lane admit them as one reviewed batch -- each its
   own exact anchored line and its own failing control -- or must each
   admission precede only its own capture?
2. **THE SIGN IN AND SECURITY CATEGORY AND THE SIGN-IN PAGE -- CAPTURED AT
   ALL?** Ground: `READ-PAST-AN-ACT-SUBSTRING`, *"It does NOT reach a substring
   whose ground is the read itself: ... a credential, recovery, session or
   security surface; a sign-in challenge"*; and `CREDENTIAL-SETTINGS-NEED-THE-
   OPERATOR`. Those pages draw his email addresses, phone numbers and sessions.
   Until he says, `P N4`-`P N8`, `P N10`, `P N11` (surface C-SIGNIN) and
   `P N12` (`/uas/login`) stay GAP on this question, named rather than queued.
3. **THE DEMOGRAPHIC PAGE -- MAY IT BE READ?** Ground:
   `HIS-OWN-SETTINGS-NOT-OUTWARD`, *"a setting that records a sensitive
   personal attribute: demographics, disability or veteran status, or
   self-identification answers. A test value would itself assert that
   attribute."* A capture would READ and keep (gitignored) his answers. `P S6`
   is queued (A-DEMOGRAPHIC) but its load waits on this answer.
4. **A GROUP'S SETTINGS PAGE CARRIES A GROUP ID.** Ground:
   `READ-PAST-AN-ACT-SUBSTRING`, *"Such a page is admitted by ONE exact,
   anchored pattern"*, and ONE-NAMED-SETTINGS-PAGE-AT-A-TIME. `N 176`, `M M42`
   and `N 170` sit on `/psettings/group/<id>/`. Is the admission one exact
   line per group he names (the id from his call, never from a page), or does
   a per-group settings page need its own ruling?
5. **"INSIDE THE SAME MINUTE" AGAINST 20 SECONDS BETWEEN LOADS.** Ground:
   `HIS-OWN-SETTINGS-NOT-OUTWARD`, *"A setting whose change shows to other
   people ... is proven by restoring it inside the same minute"*; and
   LIVE-BUDGET-40-LOADS, *"40 LinkedIn page loads per live session, 20s+
   apart"*. Between a benign press and its restore press sit three loads (the
   verification, the restore's preview, the restore's press), so at the
   minimum spacing the restore lands about 60 s later. Does that satisfy the
   ruling for the 31 VISIBLE rows, or may the loads inside one proof run
   closer than 20 s?
6. **`P N15`, THE INTERFACE LANGUAGE, IS FILED CANNOT-BE-PUT-BACK -- MY
   APPLICATION.** Ground: the ruling's exclusion, *"a setting whose change
   cannot be put back exactly"*. Changing the language changes every label
   LinkedIn draws, so this writer could not find the switch back by its
   admitted label. Confirm, or rule that a proof may restore it by hand.
7. **THE WRITE DOOR EXCUSES TWO FORBIDDEN ENTRIES FOR ONE ACTION.** Ground:
   `assert_write_url`, which honoured exactly one `exempt_substring` per spec.
   The admitted address trips `"/settings/"` and `"settings"`, so the spec
   carries a new field, `exempt_substrings`, excusing both by equality -- the
   first spec to excuse two. Confirm the field, or prefer a per-page exemption
   table beside the registry.

ON MERGING: three other lanes copy and register the same five ruling ids. The
copies of the rulings document are byte-identical; the register entries in
`scripts/build_rulings_index.py` are this lane's own wording and will conflict
at the tail of `REGISTER`. Keep one set and regenerate `_audit/RULINGS.md`.

## 11. Instruments

Registered as section 85 of `_audit/INSTRUMENTS.md`.
