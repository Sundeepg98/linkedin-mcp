# Lane S (settings): the settings of his own account, built behind the grant

Lane S (settings), `ls2-settings-lead`. Brief written by the orchestrator on
2026-09-28; relaunched and run on 2026-10-10 from master `3c8edc2` (CI green,
run 36460989178), on its own worktree branch, merged with master as it moved
(`53908ea`, `fe119de`, `1027bf8`, `f93104c`, `16ee59a`, `71d83ca`, `0103810`),
pushed only to its
`ci/` ref by `scripts/lane_ci.py`. Not to be confused with the earlier lane S of 2026-09-28
(people search, the offline frontier), whose record is
`_audit/2026-09-24-lane-s-people-search.md`.

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
  tripped, repaired. Lane K registered the same five on master; at the merge
  of `fe119de` master's register entries were kept and this lane's dropped.
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
* 100 settings rows IN and 28 OUT (section 1): 115 candidates walked by script,
  then 13 more -- `P O17` made by the split, eleven rows lane K's next-step
  ledger names as this lane's that the walk had missed, and `N 96`, which a
  cold review named -- and two IN rows (`P N10`, `P N21`) left scope at master
  `71d83ca` on the orchestrator's rulings on lane K's questions. Every IN row
  but `P O17` stays GAP: 92 wait on a line of
  `_audit/_census/capture-queue-settings.tsv` (22 lines, section 5), 3 are
  kinds the writer refuses, 3 are not settings pages, and `P N12` waits on
  question 2.
* A COLD REVIEW of the writer, fourteen findings, the first of them HIGH: the
  receipt's STOP fired for one failure shape of five. Every finding is fixed
  or answered (section 3.4); each of the ten fixes in code comes with a
  mutation that turns its test red, and the rest are census and record
  changes read back by the census instruments.
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
own account that a write changes) or OUT (named reason): 93 IN, 22 OUT.

THE WALK MISSED TWELVE, AND LANE K'S LEDGER AND THE COLD REVIEW FOUND THEM.
It read no jobs row:
the jobs slice is not in `write-classes.tsv`, and its cells name the settings
family in other words, so neither source 3 nor source 4 saw `J 74`-`J 76`
(the job application settings page `P M7` and `P M8` already sit on). Lane
K's next-step ledger (`_audit/_census/next-step.tsv`, held by
`scripts/check_next_step.py`), cross-checked against this lane's rows after
the merge of `fe119de`, names eleven rows as this lane's that the walk had
not reached, and the cold review named `N 96`; the split made a thirteenth
row, `P O17`. Each was read and placed like the 115: eight IN (`J 35`, `J 36`, `J 41`, `J 74`,
`J 75`, `J 76`, `J 100`, `M M52`), four OUT (`J 81`, `J 83`, `J 157`,
`N 96`), and `P O17` IN as the one built: 102 IN, 26 OUT. Then, at the
merge of master `71d83ca`, lane K's application of the orchestrator's rulings
on its own questions took two of the IN rows out of scope -- `P N10` (signing
out of sessions, on SESSION-SURFACE) and `P N21` (contact sync, on
CONTACT-IMPORT-STAYS-MANUAL) -- and they are OUT with those rulings named.
**100 IN, 28 OUT.** The walk was a
scratch script and is not kept: its four rules are the list above, and the
ledger's checker is the committed cross-check that caught what it missed.

Twins are kept as the census keeps them (`N 159`/`P B10`, `N 115`/`P E8`,
`M C88`/`P N26`, `N 170`/`M M42`, `J 74`/`P M8`, `J 76`/`P M7`): two rows, one
control, one capture.

A WRITER IS BUILT FOR THREE KINDS, AND A ROW'S KIND IS ITS CAPTURE'S TO SAY.
The census sentence on each IN row says which of these is known of it (a
cold review found the first form said "the write is BUILT" of all of them,
including rows whose own note named a refused kind):

    the capture decides the kind: a switch, radio group or select
      is set; a typed field, button or link is refused            79 rows
    reads as an act or a typed value (add, remove, connect, sign
      out, a request, a typed address): the capture decides, and
      such a control would be refused                             11 rows
    half settable: `M M39`, its switch and not its typed message   1 row
    a kind the writer refuses, so not queued: `P N5`, `P N19`,
      `P O5`                                                       3 rows
    not a settings page: `P D7`, `P G2`, `M M52`                   3 rows
    on the sign-in page, waiting on question 2: `P N12`            1 row
    the split's two rows, written by hand: `P O17` (built) and
      `P O6-O20` (the fourteen left)                               2 rows
                                                                 ---
                                                                 100

Counted from the census itself: 79 cells carry the first sentence (7 in the
jobs slice, 12 in messaging, 23 in network, 37 in profile).

The surface each row waits on is my reading of LinkedIn's settings layout from
the census cells, the help articles they cite and the one captured index; it
is UNVERIFIED for every category page until that page is captured, and the
capture settles it. The ACCOUNT category's pages are not a reading: the
captured index draws each one's address (section 5).

IN: 100 rows. OUT: 28 rows. Candidates: 128.

| surface | address | state of the capture | rows (live-proof class) |
|---|---|---|---|
| S0-SHARE-PROFILE-UPDATES | `/mypreferences/d/settings/notify-network-for-updates` (settings page) | CAPTURED (live2/setting.html, 2026-09-28); admitted by name | `P O17` (ALLOWED) |
| C-VISIBILITY | `/mypreferences/d/categories/profile-visibility` (category page) | not captured | `P O6-O20` (VISIBLE), `P O4` (VISIBLE), `N 137` (VISIBLE), `N 138` (VISIBLE), `N 139` (VISIBLE), `N 67` (VISIBLE), `N 68` (VISIBLE), `N 69` (VISIBLE), `N 70` (VISIBLE), `N 71` (VISIBLE), `N 72` (VISIBLE), `N 74` (VISIBLE), `N 77` (VISIBLE), `N 159` (VISIBLE), `P B10` (VISIBLE), `M C88` (VISIBLE), `M C89` (VISIBLE), `P N26` (VISIBLE), `N 183` (VISIBLE), `N 115` (VISIBLE), `P E8` (VISIBLE), `N 116` (VISIBLE) |
| C-PRIVACY | `/mypreferences/d/categories/privacy` (category page) | not captured | `P P4` (ALLOWED), `P P5` (ALLOWED), `P P6` (ALLOWED), `P P7` (ALLOWED), `P P8` (ALLOWED), `P N25` (ALLOWED), `M C73` (VISIBLE), `M M35` (ALLOWED), `M M36` (ALLOWED), `M M37` (VISIBLE), `M M39` (VISIBLE), `M M41` (ALLOWED), `M M46` (ALLOWED), `M M50` (ALLOWED), `P M10` (ALLOWED) |
| C-ADS | `/mypreferences/d/categories/ads` (category page) | not captured | `P P10` (ALLOWED), `P P11` (ALLOWED), `P P12` (ALLOWED), `P P13` (ALLOWED), `P P14` (ALLOWED) |
| C-NOTIFICATIONS | `/mypreferences/d/categories/notifications` (category page) | not captured | `P P17` (ALLOWED), `P P18` (ALLOWED), `P P19` (ALLOWED), `P P20` (ALLOWED), `P P21` (ALLOWED), `P P22` (ALLOWED), `P P23` (ALLOWED), `N 58` (ALLOWED), `N 73` (ALLOWED), `N 75` (ALLOWED), `N 78` (ALLOWED), `N 117` (ALLOWED), `N 140` (ALLOWED), `M M24` (ALLOWED), `J 41` (ALLOWED) |
| C-SIGNIN | `/mypreferences/d/categories/sign-in-and-security` (category page) | not captured; credential surfaces (question 2) | `P N4` (CREDENTIAL), `P N6` (CREDENTIAL), `P N7` (CREDENTIAL), `P N8` (CREDENTIAL), `P N11` (CREDENTIAL) |
| A-LANGUAGE | `/mypreferences/d/settings/language` (settings page) | drawn on the captured index | `P N15` (CANNOT-BE-PUT-BACK) |
| A-CONTENT-LANGUAGE | `/mypreferences/d/language-for-translation` (settings page) | drawn on the captured index | `P S7` (ALLOWED) |
| A-AUTOPLAY | `/mypreferences/d/settings/autoplay-videos` (settings page) | drawn on the captured index | `P N16` (ALLOWED) |
| A-SOUNDS | `/mypreferences/d/settings/enable-sounds-desktop` (settings page) | drawn on the captured index | `P N17` (ALLOWED) |
| A-PROFILE-PHOTOS | `/mypreferences/d/settings/show-profile-photos` (settings page) | drawn on the captured index | `P N18` (ALLOWED) |
| A-PREFERRED-VIEW | `/mypreferences/d/settings/preferred-view` (settings page) | drawn on the captured index | `M C100` (ALLOWED) |
| A-SYNCING | `/mynetwork/settings/manage-syncing/` (settings page) | drawn on the captured index (twice: calendar, contacts) | `P N20` (ALLOWED) |
| A-MICROSOFT | `/mypreferences/d/connected-microsoft-accounts` (settings page) | drawn on the captured index | `P N23` (ALLOWED) |
| A-DEMOGRAPHIC | `/mypreferences/d/demographic-info-copy` (settings page) | drawn on the captured index; reading it reads his self-identification answers (question 3) | `P S6` (SENSITIVE) |
| O-PUBLIC-PROFILE | `/public-profile/settings` (settings page) | named by the census; not captured | `P C2` (CANNOT-BE-PUT-BACK), `P C3` (VISIBLE), `P C4` (VISIBLE), `P C5` (VISIBLE), `P C6` (CANNOT-BE-PUT-BACK), `P B4` (VISIBLE) |
| O-GUEST-CONTROLS | `/psettings/guest-controls` (legacy settings address) | named by the census; may redirect | `P C7` (ALLOWED) |
| O-PERMITTED-SERVICES | `/psettings/permitted-services` (legacy settings address) | named by the census; may redirect | `P N24` (ALLOWED) |
| O-GENAI-DATA | `/mypreferences/d/settings/data-for-ai-improvement` (settings page) | named by census finding 7.2 | `P P9` (ALLOWED) |
| O-MEMBER-COOKIES | `/mypreferences/d/member-cookies` (settings page) | named by census finding 7.1 | `P P16` (ALLOWED) |
| O-JOB-APPLICATION-SETTINGS | `/jobs/application-settings/` (settings page) | named by the census; refused on an ACT substring (READ-PAST-AN-ACT-SUBSTRING) | `P M7` (ALLOWED), `P M8` (VISIBLE), `J 74` (VISIBLE), `J 75` (VISIBLE), `J 76` (ALLOWED) |
| O-GROUP-SETTINGS | `/psettings/group/<id>/` (per-group settings page) | named by the census; the address carries a group id (question 4) | `N 176` (ALLOWED), `M M42` (ALLOWED), `N 170` (ALLOWED) |
| O-JOB-ALERTS | `/jobs/jam/` (job alerts page) | ADMITTED for reading (J 37's address); its controls not captured | `J 35` (ALLOWED), `J 36` (ALLOWED), `J 100` (VISIBLE) |
| R-REFUSED-KIND | `(none: a kind the writer refuses)` (no page to queue) | not queued: a capture would not unblock it | `P N19` (VISIBLE), `P N5` (CREDENTIAL), `P O5` (ALLOWED) |
| O-SIGNIN | `/uas/login` (sign-in surface) | READ-PAST does not reach a sign-in surface (question 2) | `P N12` (CREDENTIAL) |
| X-POSITION-EDITOR | `his experience editor (per-edit control)` (editor dialog) | not a settings page | `P D7` (VISIBLE) |
| X-ACTIVITY-SECTION | `his profile's Activity section` (profile section) | not a settings page; queued DEFAULT-ACTIVITY-FORM | `P G2` (ALLOWED) |
| X-COMPOSER | `the compose window's send-options menu` (composer control) | not a settings page | `M M52` (ALLOWED) |

| row | capability | surface | live-proof class | note |
|---|---|---|---|---|
| `P O17` | Share profile updates with your network (the switch Share key profile updates) | S0-SHARE-PROFILE-UPDATES | ALLOWED | SPLIT from O6-O20 on 2026-10-10: the admitted switch, BUILT on its capture, COVERED-UNFIRED |
| `P O6-O20` | fifteen further visibility toggles: contact-info and email visibility, connection-list visibility, who can see | C-VISIBILITY | VISIBLE | the fourteen visibility toggles left when O17 split out; each its own control, none captured |
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
| `P P4` | Change or correct his data -- the data right "Change or Correct Data" | C-PRIVACY | ALLOWED | a data-rights REQUEST: reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P P5` | Restrict or object to the use of his data -- the data right "Restrict or Object to the use of Data" | C-PRIVACY | ALLOWED | a data-rights REQUEST: reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P P6` | Salary data: the settings page for the salary data he has shared with LinkedIn | C-PRIVACY | ALLOWED | salary data page; a delete half would split off (census cell) |
| `P P7` | Research invitations: whether LinkedIn may invite him to take part in research | C-PRIVACY | ALLOWED | research invitations |
| `P P8` | Harmful message detection: turn it on or off | C-PRIVACY | ALLOWED | harmful message detection |
| `P N24` | Permitted Services -- third-party app access | O-PERMITTED-SERVICES | ALLOWED | third-party app access (remove an app): reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P N25` | LinkedIn Services (DMA) connect / disconnect | C-PRIVACY | ALLOWED | LinkedIn services (DMA) connect / disconnect; nav path only: reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `M C73` | Allow or disallow your posts being embedded | C-PRIVACY | VISIBLE | embedding of his posts |
| `M M35` | Choose Messaging inbox layout | C-PRIVACY | ALLOWED | messaging inbox layout |
| `M M36` | Manage how new conversations open (conversation windows) | C-PRIVACY | ALLOWED | conversation windows |
| `M M37` | Turn read receipts and typing indicators on or off | C-PRIVACY | VISIBLE | read receipts and typing indicators (others see them) |
| `M M39` | Set or edit an away message (Premium) | C-PRIVACY | VISIBLE | away message (Premium): the message is TYPED, a refused kind; only its on/off switch is a kind the writer sets |
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
| `P N23` | Partners and services / Microsoft account link | A-MICROSOFT | ALLOWED | Microsoft account link (connect / disconnect): reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P N19` | Name / location / industry via settings | R-REFUSED-KIND | VISIBLE | name, location, industry: typed and autocomplete fields, kinds the writer refuses; the intro editor rows carry them |
| `P S6` | Personal demographic information, a page of the account settings | A-DEMOGRAPHIC | SENSITIVE | personal demographic information |
| `P C2` | Customise the public profile URL | O-PUBLIC-PROFILE | CANNOT-BE-PUT-BACK | custom public URL, a typed address: releasing it lets another member take it, and every link to it breaks; reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P C3` | Public profile visibility master switch | O-PUBLIC-PROFILE | VISIBLE | public profile master switch |
| `P C4` | Per-section public visibility toggles | O-PUBLIC-PROFILE | VISIBLE | per-section public visibility |
| `P C5` | Search-engine visibility of the public profile | O-PUBLIC-PROFILE | VISIBLE | search-engine visibility |
| `P C6` | Unlink a prior public URL | O-PUBLIC-PROFILE | CANNOT-BE-PUT-BACK | unlinking a prior public URL: reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P B4` | Profile photo visibility audience | O-PUBLIC-PROFILE | VISIBLE | profile photo audience |
| `P N4` | Two-step verification on / off | C-SIGNIN | CREDENTIAL | two-step verification |
| `P N5` | Change password | R-REFUSED-KIND | CREDENTIAL | change password: a typed field, a kind the writer refuses |
| `P N6` | Passkeys add / delete | C-SIGNIN | CREDENTIAL | passkeys (add, remove): reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P N7` | Email addresses -- add / remove / change primary | C-SIGNIN | CREDENTIAL | email addresses (add, remove): reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P N8` | Phone numbers -- add / remove / choose reset number | C-SIGNIN | CREDENTIAL | phone numbers (add, remove): reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P N11` | Devices that remember your password | C-SIGNIN | CREDENTIAL | devices that remember the password (add, remove): reads as an act or a typed value, which the writer refuses by kind; the capture decides its control's kind |
| `P N12` | Keep me logged in / auto sign-in | O-SIGNIN | CREDENTIAL | keep me logged in, on the sign-in page |
| `N 176` | Prevent your network being updated when you join a group | O-GROUP-SETTINGS | ALLOWED | network updates when he joins a group; queued GROUP-SETTINGS-PAGE |
| `M M42` | Settings to allow or prevent messages from group members | O-GROUP-SETTINGS | ALLOWED | messages from group members; twin of N 170 |
| `N 170` | Allow or prevent other group members from messaging you | O-GROUP-SETTINGS | ALLOWED | messages from group members; twin of M M42 |
| `P O5` | Public profile badge creation | R-REFUSED-KIND | ALLOWED | public profile badge: creates an embed snippet, not a value the writer sets; and whether loading its creation page creates is unmeasured, so it is not queued |
| `P D7` | Notify network of a job change | X-POSITION-EDITOR | VISIBLE | the per-edit 'notify network' control in the position editor; its standing default is the admitted switch |
| `P G2` | Activity section default view | X-ACTIVITY-SECTION | ALLOWED | Activity section default view; its own queue stands |
| `J 35` | Set alert frequency (daily / weekly) | O-JOB-ALERTS | ALLOWED | an alert's frequency (daily / weekly) |
| `J 36` | Set alert delivery channel (email / app / both) | O-JOB-ALERTS | ALLOWED | an alert's delivery channel (email / app / both) |
| `J 100` | Signal your interest to recruiters at companies you have created job alerts for | O-JOB-ALERTS | VISIBLE | signal interest to recruiters at companies he has alerts for (recruiters see it) |
| `J 41` | Subscribe / unsubscribe the job-collections weekly digest | C-NOTIFICATIONS | ALLOWED | the job-collections weekly digest (an email subscription) |
| `J 74` | Toggle Share resume data with recruiters | O-JOB-APPLICATION-SETTINGS | VISIBLE | share resume data with recruiters; twin of P M8 |
| `J 75` | Toggle Share your full profile when you click Apply (and the Undo banner) | O-JOB-APPLICATION-SETTINGS | VISIBLE | share his full profile on Apply (employers see it) |
| `J 76` | Opt out of saving job-application data | O-JOB-APPLICATION-SETTINGS | ALLOWED | opt out of saving job-application data; twin of P M7 |
| `M M52` | Choose the message composer's send options (the menu beside Send) | X-COMPOSER | ALLOWED | the composer's send options: a menu in the compose window, not a settings page |

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
| `J 81` | Verify account to raise the Easy Apply daily limit | account verification to raise a limit, as P K2-K6: not a setting |
| `J 83` | Save voluntary self-identification answers for reuse | stored self-identification answers: records he edits, as P M6, and a sensitive attribute |
| `J 157` | Change LinkedIn Learning settings | a LinkedIn Learning settings page: its own blocker, LEARNING-SURFACE, stands, and whether HIS-OWN-SETTINGS-NOT-OUTWARD reaches a Learning page is a question for the orchestrator |
| `N 96` | Clear your search history | clearing his search history is a button that deletes his own record -- no value the writer sets, and nothing restores it |
| `P N10` | Sign out of one session / all sessions | EXCLUDED-RULED on SESSION-SURFACE (the orchestrator's ruling on lane K's questions, 2026-10-10) |
| `P N21` | Contact / address-book sync | EXCLUDED-RULED on CONTACT-IMPORT-STAYS-MANUAL (the orchestrator's ruling on lane K's questions, 2026-10-10) |

## 2. The exclusions the ruling names, per row

Every IN row carries one live-proof class:

    ALLOWED              54   proven read, benign value, read back, restore, read back
    VISIBLE              35   ALLOWED, and the change shows to other members:
                              restored inside the same minute (question 5)
    CREDENTIAL            7   CREDENTIAL-SETTINGS-NEED-THE-OPERATOR's set: built,
                              never live-proven unless he names it
    CANNOT-BE-PUT-BACK    3   built, never live-proven unless he names it
    SENSITIVE             1   built, never live-proven unless he names it

Counted over the 100 IN rows, after the split: `P O17` is ALLOWED and the
fourteen toggles left in `P O6-O20` are VISIBLE, on the Visibility category
page's line. (This record's first form counted `P O6-O20` as the switch that
left it -- ALLOWED, on the switch's own page -- which a cold review caught.)

The three that cannot be put back exactly, and why (a fourth, `P N21`
contact sync -- turning it on uploads other people's contact data, which
turning it off does not withdraw -- left scope at `71d83ca`):

* `P C2` custom public URL and `P C6` unlinking a prior one -- the ruling's own
  examples: an address released may be taken by another member, and every
  link to his profile from his resume and his applications breaks.
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
* PRESS: through `writes.perform`'s one click site (a switch by its own name;
  a radio group on the `<label for>` bound to the radio named for the
  destination, the binding read live by `dom.read_radio_label_binding` just
  before the press -- LinkedIn covers a settings radio's input, measured on
  the dark-mode page) or its one `select_option` site (a select, by the
  option's label). Nothing new is added to `readonly.SANCTIONED_MUTATIONS`.
  The click is strict, and so is the choice, for this action alone (a second
  match at the moment of the press throws); the select reader counts every
  combobox wearing the name, as the press's selector would match them.
* BEFORE THE PRESS: every switch, checkbox, radio and native select on the
  page is read. A page whose controls cannot all be read, or that draws more
  than the reader's ceiling, is not pressed at all: the check after the press
  could never pass.
* WAIT: `profile_editor.wait_for_state`, the bounded liveness wait of
  `c3b2393`, for the control to read the requested value.
* ONLY THAT CONTROL MOVED: the same four kinds read again after the press,
  position by position and by each position's IDENTITY (its role and
  accessible name, digested), so a page that redrew -- fewer controls, more,
  or as many but not the same -- is refused rather than compared; the page may
  move exactly what one press of the control's kind moves -- one checkable for
  a switch, two radios for a group, one select -- and nothing else. NOTHING
  ELSE ON THE PAGE IS READ: a pressed button, a menu item, a custom listbox or
  a typed value that moved would not be seen, and the pass says so. A select's
  value and every name are compared in this process and never leave it.
* SAVE: only if that holds and the page draws one (exactly one enabled control
  of that name). A page whose capture drew no Save stores on the press, so
  EVERY press there whose check did not pass -- another control moved, the
  control did not move, the page redrew, the read after failed, or the press
  raised -- carries STOP: open the page, read every control, put each one back
  by hand before anything else runs. A press refused before it is made is not
  one.
* VERIFY: a fresh navigation to the page and a re-read of the control;
  `performed` is true, false or "unknown". The receipt prints the address
  asked for, never the landing.
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

After the cold review (section 3.4), ten more, one per fix in code, the same way:

| guard broken | caught by |
|---|---|
| R1 STOP set for `another_control_moved` alone, as first shipped | `test_the_three_patterns_through_the_shipped_doors` |
| R2 the identity comparison dropped | `test_the_three_patterns_through_the_shipped_doors` (the other switch replaced, same count) |
| R3 the radio pressed on its covered input again | `test_the_three_patterns_through_the_shipped_doors` (the late radio: the press times out) |
| R4 the select reader counts native selects only | `test_the_select_reader_the_choice_and_the_save_gate` (a div combobox wearing the name) |
| R5 a colliding audience overwrites in silence | `test_the_audiences_are_every_value_with_its_control_and_a_collision_is_refused` |
| W5 (`writes.py`) a page whose controls could not all be read is pressed | `test_a_page_whose_controls_cannot_all_be_read_is_never_pressed` |
| W6 (`writes.py`) a radio label pressed without its binding read | `test_a_radio_whose_label_is_not_bound_to_it_is_never_pressed` |
| W7 (`writes.py`) the verification prints the landing | `test_the_real_page_end_to_end_off_to_on_verified_on_a_fresh_render` (a landing with a query) |
| W8 (`writes.py`) the click block prints the landing | the same test |
| W9 (`writes.py`) STOP told no press was attempted | `test_the_three_patterns_through_the_shipped_doors` |

All ten caught; both files restored byte-identical after each (sha256
checked). Two of the `writes.py` anchors first matched nothing -- the runner
wrote them with LF line ends and the file is checked out with CRLF -- and were
re-run with the file's own line ends; the runner reports such a mutation as
SKIPPED, never as caught.

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
* THE LANE'S FIRST CI RUN (38036544654) failed eleven tests outside the cited-
  SHA family the coordinator named as infrastructure, each fixed in `959a1dc`
  and its follow-ups: the navigation guard convicted the observe and verify
  loads (the address now comes through the spec's own template and the landing
  is COMPARED, never handed to a call); `valid_from` returned an exception's
  text; a package module named a tracked fixture outside a sentence; a
  module-level `url_pattern` read; the count claims in the README, the package
  docstring and the server docstring; the locator's row total; the landing and
  tool-envelope baselines; an asserted name; and `tests/test_writes.py`'s
  hand-typed tables. THE CROSS-MODULE WALK, which runs only where `CI` is set,
  then convicted `writes.py` and a probe script through the registry: the
  admitted page's address field was called `url`, and the guard reads every
  `.url` attribute as an address the browser chose. It is `address` now.

### 3.4 What a cold review found, and what was done

A cold reviewer read the lane as it stood in `baa2fe1` ("settings: what the
shipped guards caught in the integration, fixed") -- the record, the module,
the integration and the census edits -- with no pytest and no browser, and ran
pure-Python probes over an archive of that commit. Fourteen findings; every
one is fixed or answered in `c4edf60` ("settings: what a cold review of the
writer found, fixed and each shown failing") and the record commit after it.
Both hashes, and every other hash of this lane's own commits, resolve on the
lane's branch until it merges into master; the subjects are the key that
survives.

| # | severity | finding | done |
|---|---|---|---|
| F1 | HIGH | STOP fired for one failure shape of five, and no test read it | STOP on every unpassed press on a page that stores on the press (`settings_writer.press_stop`); a page whose controls cannot all be read before the press is never pressed; every end-to-end scenario asserts STOP or its absence (R1, W5, W9) |
| F2 | MEDIUM | the split counted one capability twice (786, 748) | `COLLAPSED` `O6-O20` 15 -> 14; capabilities 785; the cell and the write-classes note say fourteen |
| F3 | MEDIUM | 89 cells said "the write is BUILT", six of them rows the record called refused kinds | four sentence forms (section 1); three refused kinds leave the queue |
| F4 | MEDIUM, latent | the choice was not strict; the reader counted native selects only | strict for this action; the reader counts every combobox wearing the name (R4) |
| F5 | MEDIUM, latent | the radio press aimed at the input LinkedIn covers | the bound label, read live; the synthetic radio page covers its inputs (R3, W6) |
| F6 | MEDIUM | the live-proof plan: STOP-ALL keyed on the narrow STOP, no failure branch at step 3, load 7 not independent, spacing inside a confirm | section 6 rewritten on each point; question 5 |
| F7 | MEDIUM-LOW | "only that control moved" claimed more than it checked | each position's identity compared (R2); the pass names the four kinds it reads |
| F8 | LOW | the receipt printed LinkedIn's landing | the address asked for, in both places (W7, W8) |
| F9 | LOW | the switch named `P O6-O20`, which the record classed as the switch | `rows=("P O17",)`; `P O6-O20` VISIBLE on the Visibility line; 54 ALLOWED, 35 VISIBLE |
| F10 | LOW | `N 96` missed; the walk not kept | `N 96` OUT with its reason, and eleven more found by lane K's ledger (section 1); the walk's rules are written in section 1 rather than kept as a script |
| F11 | LOW | `P D7` and `P N12` named queue lines that do not exist; "93 queued" | both `classify-only` again; this lane's queued dispositions are 86. The title of `0ae7946` ("... 93 settings rows queued on their pages") counted IN rows, not queued lines |
| F12 | LOW | "20 loads clear" included the badge page and a page under `/mynetwork/` | the badge page left the queue with `P O5`; the syncing page's cost is named; 19 (section 5) |
| F13 | LOW | the retry sentence and the server instructions did not hold for this action | both rewritten |
| F14 | LOW, latent | a second admitted switch would overwrite the audiences in silence | the builder refuses a collision (R5) |

THE REVIEW'S OWN EVIDENCE CLASSES, kept: it marked every test count and the
seven mutations UNVERIFIED because it could not run pytest. Those counts are
pytest's (section 9), and the mutation runner's log for each set is in the
lane's scratch, restored byte-identical each time.

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
Its capability cell names fourteen now, and `census_completion.COLLAPSED`
counts it as fourteen: a split moves a capability between rows and adds none.

Every other IN row stays GAP. What each lacks is said in its cell (section 1):
for 79, its page captured and admitted by name, and the capture showing a
switch, a radio group or a select; for 11 that read as acts or typed values,
the same capture, which will most likely show a control this writer refuses;
for the three refused kinds, a write of their own.

## 5. The capture specs

`_audit/_census/capture-queue-settings.tsv` holds one line per uncaptured
surface a GAP row waits on: 22 lines, columns surface-id, address, presses,
save, loads, searches, rows. Every capture is a ZERO-PRESS load: the page is
loaded and read; nothing on it is pressed. (23 lines in this record's first
form: the basic-info and badge pages left with `P N19` and `P O5`, whose
kinds the writer refuses, and the job alerts page joined for `J 35`, `J 36`
and `J 100`.)

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
serves 22 rows, Data privacy 15, Notifications 15, Advertising data 5, "Public
profile settings" 6, the job application settings page 5 and the job alerts
page 3. The ACCOUNT category was captured on 2026-09-23 and drew these
addresses, so their pages need no category load first: language, content
language, autoplay videos, sound effects, showing profile photos, preferred
feed view, syncing (calendar; contacts left scope), the Microsoft link and
personal demographic info.

ADMISSION. Every one of these addresses but one is refused by the read
boundary today, and each is admitted by name, one at a time, before its load
(ONE-NAMED-SETTINGS-PAGE-AT-A-TIME; question 1). The exception is the job
alerts page, already admitted for reading (`J 37`'s address), so its capture
needs no admission. One is refused on an ACT substring, which the ruling
READ-PAST-AN-ACT-SUBSTRING reaches: the job application settings page
(`"/jobs/application"`). Not in the queue, with the reason:

* `/uas/login` (`P N12`) -- a sign-in surface, which READ-PAST does not reach
  (question 2);
* his position editor (`P D7`), his profile's Activity section (`P G2`) and
  the compose window's send options (`M M52`) -- not settings pages; their
  own rows' captures carry them;
* the basic-info page (`P N19`) and the badge page (`P O5`) -- kinds the
  writer refuses, so a capture would not unblock them; and the badge page's
  address ends `/create`, and whether loading it creates anything is not
  measured.

LOADS. 22 lines at one load each, of which three wait on a question (the
Sign in & security category, the demographic page, a group's settings page),
so **19 loads clear without a ruling** -- and one of the 19 carries a cost
nobody has measured: the syncing page sits under `/mynetwork/`, whose root
the boundary refuses because opening it is BELIEVED to consume his
pending-invitation badge (the boundary's own word; it was never measured).
Whether this sub-page does is unknown; the instrument that would say is
`dom.read_invitation_badge`, read before and after the load, as
`linkedin_connections` does for its own sub-page. The category loads then name the settings pages below them: the rows
behind the four category pages sit on pages not yet seen, at most one load
each and fewer where pages are shared.

## 6. The live-proof plan (the live lane runs it, not this lane)

### 6.1 The rule, per setting

1. READ: a preview of the setting's change (one load), which reads the current
   value off the control and mints a token.
2. BENIGN VALUE: the opposite of what was read (a switch), or for a group or a
   select the value that changes the least for others; confirm the token (one
   load to the page, one load for the verification's fresh render).
3. READ BACK: the verification is the read back; `performed` must be true and
   `setting_press.check.proceed` true. If either is not, it is STOP-ALL
   (below) -- not a retry.
4. RESTORE THE EXACT ORIGINAL: the receipt's `restore.to_put_it_back` call --
   preview (one load), confirm (two loads).
5. READ BACK AGAIN: the restore's verification, and then a preview of the
   ORIGINAL value (one load), which must REFUSE as a no-op -- the control
   already reads it -- and so mints no token. It is the same tool, reader and
   page as the verification, a second render rather than an independent
   witness: no read-only route to a settings control exists outside dark
   mode's.

ONE SETTING AT A TIME: nothing else runs between step 2 and step 5, and no
other write runs while any setting is away from its original. STOP-ALL: on ANY
receipt of the proof -- the benign write's or the restore's -- whose
`performed` is not true, whose `setting_press.check.proceed` is not true, or
whose `setting_press` carries `stop`, every write stops; the page is opened by
hand and every control on it put back before anything else. (This record's
first form keyed STOP-ALL on `stop`, which then fired for one failure shape of
five.)

THE SPACING. A confirm makes two loads in one call, back to back -- the page
for the press, then the verification's fresh render -- as every shipped
write's confirm does. The 20 s spacing of the live budget is kept between
calls; inside a confirm it cannot be (question 5).

### 6.2 The one built setting: "Share key profile updates"

    load 1  preview  value="on"   reads the current value (the capture read off;
                                  if it reads on, swap on and off throughout)
    load 2  confirm               the press, on the page
    load 3                        the verification's fresh render: must read on
    load 4  preview  value="off"  the restore's preview: must read on
    load 5  confirm               the press
    load 6                        the verification: must read off
    load 7  preview  value="off"  must REFUSE as a no-op (it reads off); no token

**SEVEN LOADS**, two of them inside each confirm. With 20 s between calls
(LIVE-BUDGET-40-LOADS), the switch is away from off from the press at load 2
to the press at load 5 -- the verification, the restore's preview, the
restore's confirm -- about 45 s. While it reads on, a profile edit could be
shared with his network, so NO profile edit runs from load 2 to load 6, and
the intro-edit rows' condition 1 is unaffected because it reads this switch
before any edit. Nobody else sees the switch itself.

ONE RISK THE CAPTURE CANNOT SETTLE. The writer presses the switch's own
`input` by its role and name. Dark mode learned live (2026-09-03, recorded
in `dom.settings_radio_label_selector`) that LinkedIn covered its radio inputs
and only the bound label took a press -- which is why this writer's radio
path now presses the label -- and a styled switch may be covered the same way;
a skeleton with no stylesheet cannot show it. If the input is covered,
Playwright refuses to click it and the press raises after its timeout; if it
is clicked and the switch does not move, the bounded wait ends unreached and
the check reads `the_control_did_not_move`. On this page, which stores on
the press, BOTH receipts carry STOP -- a press that raised may have
dispatched, and a press on a switch of his has been measured landing minutes
late (the Premium badge, `writes.perform`'s note). So either is STOP-ALL:
the page is read by hand, and what received the press is the measurement
for the next build.

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
  `built:set_admitted_setting`, act profile-setting, R3. On this branch the
  split read 16 R1 + 37 R2 + 337 R3 = 390; at the merge of `fe119de`, where
  PURCHASES-STAY-MANUAL had taken `P S9` and `M C71` out of the table, it is
  16 + 37 + 335 = 388, measured by `check_write_classes`; at the merge of
  `71d83ca`, where lane K's rulings took fourteen lines out (`P N10` and
  `P N21` among them), 16 + 37 + 321 = 374; at the merge of `0103810`, where
  lane U's three message rows left for COVERED-UNFIRED, 16 + 34 + 321 = 371.
  84 IN rows that were
  `classify-only` are queued on their surface's capture,
  `queued:SETTINGS-<surface-id>`, each naming a line the queue holds; the three
  refused kinds, `P D7` and `P N12` are `classify-only` again, with a note
  saying why; rows another lane had already queued keep their queue (`P G2`,
  `N 176`). The jobs rows are not in this table (the jobs slice keeps its own
  direction table), and `M M52` stays `classify-only`.
* The census cells of the IN rows each carry one sentence in one of the forms
  of section 1, naming the writer, the surface's line in the capture queue
  where there is one, and the live-proof class.
* The citation triage (`tests/test_a_correction_is_findable_from_the_claim.py`)
  holds one entry per slice file whose cells cite this record near words a
  correction would use: profile, network and messaging since the first form,
  and the jobs slice since its seven rows gained the sentence. Every hit was
  read; each belongs to a neighbouring row's own history.

## 8. Pins re-derived, each from its measured value

* `tests/census_row_pin.json` by `scripts/pin_census_rows.py --write`, with
  `PINNED_ROW_TOTAL` 771 -> 772 and `PINNED_SLICE_ROWS` P 236 -> 237.
* `census_completion.PINNED`, as first pinned on this branch, each +1:
  stated_rows 772, capabilities 786, capabilities_achievable 748, achievable
  734, adjudicated 185, delivered_broad 131, unfired 30, b1_no_ruling 13,
  b1_released 2; and `PINNED_B1_ROWS` gains `P O17` under no ruling. AT THE
  MERGE OF MASTER `53908ea` (live session 7 had banked `N 25`, `N 81`, `N 26`
  and moved `N 155`), two were RE-MEASURED on the merged tree, not summed:
  unfired 26 (master 25 + `P O17`) and b1_no_ruling 10 (master 9 + `P O17`).
  THE CAPABILITY PAIR WAS ONE TOO HIGH (the cold review's F2): `O6-O20`'s
  collapse kept counting 15 after `P O17` left it. `COLLAPSED` is 14, and at
  the merge of `fe119de` (PURCHASES-STAY-MANUAL had excluded `P S9` and
  `M C71`) the figures are capabilities 785, capabilities_achievable 745,
  achievable 732, adjudicated 187 -- `--check` green on the merged tree. At
  the merge of `1027bf8` (live session 8 banked `N 48`, `J 104`, `N 46` and
  `J 103`), unfired is 22: master's 21 plus `P O17`, measured. AT THE MERGE
  OF `71d83ca` (lane K applied the orchestrator's rulings on its questions),
  master's figures plus `P O17`, measured: stated_rows 772, capabilities 785,
  capabilities_achievable 724, achievable 711, adjudicated 211,
  delivered_broad 133, unfired 22, b1_no_ruling 10, b1_released 2. At the
  merge of `0103810` (lane U's `M M14`, `M M15`, `M M18` COVERED-UNFIRED):
  adjudicated 214, delivered_broad 136, unfired 25 -- master's plus `P O17`.
* The write-classes split (16, 37, 336) -> (16, 37, 337) on this branch, and
  (16, 37, 335) = 388 at the merge of `fe119de`.
* The tool surface: 61 -> 62 tools, 96 -> 100 parameters on this branch; at
  the merge of `1027bf8`, 62 tools and 101 parameters (lane NP had added one
  parameter to master's 61 tools); at the merge of `0103810`, 63 TOOLS AND
  104 PARAMETERS: lane U's `linkedin_send_attachment` had landed on master
  first as the sixty-second tool and eighteenth write, so this lane's is the
  sixty-third and the nineteenth. Both branches had moved every count from 61
  to 62 and 17 to 18, and git merged those equal moves as ONE -- each was
  re-derived on the merged tree, and the number-word map of the instructions
  test raised on nineteen, as it is built to. writes.PERFORMABLE and the
  hand-typed write lists in `tests/test_server_surface.py`; the server
  instructions and the module docstring's counts (forty-four read, nineteen
  write, sixty-three; twenty actions, nineteen tools); the strict-press set.

## 9. Gates run

Every local run was TARGETED and SERIAL (`-p no:randomly`, no `-n`): while
the live session's flag stood, by the brief; after it, by the orchestrator's
order of 11:35 (the tests touched, their importers and the census instruments;
the full suite runs on CI), and from 14:02 each local gate under two minutes,
by the coordinator's resume order. Counts are pytest's own.

| what | result |
|---|---|
| the five rulings registered: the register, the audit index, ruling holds, the citation triage, the reason locator, the identity guard | first run 2 failed / 1198 passed (the two gates of section 0); after the repair **1200 passed** |
| `tests/test_settings_writer.py` | **43 passed**; seven module mutations, **7 caught** (one only after its test was strengthened, section 3.2) |
| `tests/test_set_admitted_setting.py` | before the integration **5 failed / 1 passed**; after it **6 passed**, then 7 with the landing test |
| the first sixteen pin files (tool surface, server surface, write door, scanner, reachability, write classes, ...) | **14 failed / 727 passed** -- every failure a pin the new write should move; after the re-pins **233 passed** on the failed files |
| the browser-heavy action tables and the reader-leak guard | after the re-pins **769 passed / 3 failed** (the reader guard, section 3.3); after the fixes **797 passed** (with the lane's files, the tool pins and the gap-on-refused pin) |
| the census tests (row pin, write classes, literal repeats, ruling holds, offline frontier, triage, pointer graph, exclusion basis, gap-on-refused) | **182 passed / 1 failed** (the gap-on-refused pin, moved by addresses in the appended sentences; removed, section 7); then inside the 797 |
| the landing test and `tests/test_no_committed_identity.py` after the guard commit | **1053 passed** |
| four `writes.py` mutations of the integration's hooks | **4 caught** |
| the merge of master `53908ea`, focused | **173 passed** |
| lane CI, first run (`38036544654`, on `b9cb2e7`) | failed: eleven tests outside the cited-SHA family the coordinator named as infrastructure, each fixed (section 3.3) |
| the merge of master `fe119de`: the census instruments, then the pin and ledger tests | every instrument GREEN (below); **46 passed** |
| `tests/test_no_committed_identity.py` after each commit, scoped to the files this lane changed against master (every unparametrized test, and the per-file test of each changed file) | **95 passed** at the merge; again after the review commit and the record commit (below) |
| the navigation guards with `CI=1` (the cross-module walk and the per-file walk) | after the `address` rename **308 passed**; on the review commit **308 passed** |
| `tests/test_settings_writer.py` after the review's fixes | **58 passed** |
| `tests/test_set_admitted_setting.py`, the notify-setting admission and the server surface | **83 passed** |
| the review's ten mutations (R1-R5, W5-W9) | **10 caught**; two anchors first matched nothing and were re-run (section 3.2) |
| the census-text guards after the sentences were rewritten | the citation triage found one new pair (the jobs slice; triaged, section 7) -- then **92 passed** with the derived views, the locator and the write classes |
| the receipt, prose and landing guards | **117 passed / 1 failed**: an asserted name in this record's committed form, reworded here; then passed |
| the reader-leak guard and the tool-envelope guard | the reader guard could no longer drive `snapshot` -- its planted page had no accessibility snapshot -- so the harness gained one (`tests/plantedpage.py`); then **683 passed** and **4 passed** |
| `tests/test_writes.py`'s hand-typed tables and the receipt-ownership test | **14 passed**, **17 passed** |
| the census instruments, after every census edit and on each merged tree | `census_completion`: *every headline figure matches its pin*; `check_write_classes` GREEN (388 lines; 374 at `71d83ca`), `check_read_addresses` GREEN (98 of 98; 92 at `71d83ca`), `check_jobs_directions` GREEN (108 of 108; 104 at `71d83ca`), `ruling_holds` GREEN (1 hold, 3 lifted, 2 releases), `check_next_step` GREEN (585 GAP rows once; 561 at `71d83ca`), `check_exclusion_basis` 0 problems (61 rows at `71d83ca`); the three derived views regenerated |
| the merge of `1027bf8` (lane NP, lane G2, live session 8): the tool and parameter pins, the census pins, the count claims, the end-to-end file | **118 passed**; the reader-leak guard, in master's larger form, first failed on its blank page (the blank locator had no accessibility snapshot -- added), then ran every test to 100% with no failure before the two-minute bound cut its summary line |
| `tests/test_no_committed_identity.py`, scoped, against master `1027bf8` | **99 passed** |
| the pre-commit identity gate, every commit; the pre-push sweep on the `ci/` push | armed: *226 spellings*, 0 hits; the push swept *1213 blobs, 226 needles, 0 hits* |
| lane CI, second run (`38043402778`, on `c956797`, after the merges of `1027bf8`, `f93104c` and `16ee59a`) | **failure, one test**: `test_no_new_unresolvable_citation_appears` read three of this lane's own commit hashes in this record in the guard's slot forms -- they resolve on the lane's branch, not yet on master -- and they are cited by subject now (section 3.4). Shard 0: 1 failed / 2545 passed / 5 skipped; shards 1-3 green. The cited-SHA family the coordinator named as infrastructure passed: the local-master fix had landed |
| lane CI, third run (`38044337714`, on `ae27fe5`) | **success**, all four shards |
| the merge of `71d83ca` (lane K's application of the orchestrator's rulings): every census instrument, the write-classes and completion pins | `census_completion --check`: every headline figure matches its pin; `check_write_classes` GREEN (374 lines); the rest below |
| the merge of `0103810` (lane U's attachment write), on a box at 100% CPU from other lanes' suites | the surface, tool-pin, count-claim and prose tests **170 passed**; the end-to-end file **10 passed**; `test_writes.py`'s tables **18 passed**; the census instruments GREEN (371 write-class lines; 558 GAP rows once); the rest certified on CI |
| lane CI on the commit that carries this table | a record cannot carry its own run: the lane's final message names it |

NOT RUN LOCALLY: the full suite, and the browser-heavy action tables
(`tests/test_preview_state_and_click_state.py`,
`tests/test_a_performable_action_can_reach_its_control.py`,
`tests/test_writes_nine.py`), which run past two minutes on this box; CI runs
them.

## 10. Questions for the orchestrator

Each with its ground quoted. None blocks anything this lane built; each blocks
captures or live proofs the live lane would otherwise take.

1. **ADMITTING THE CAPTURE QUEUE'S PAGES -- ONE AT A TIME, OR AS A BATCH?**
   Ground: `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME`, *"ONE NAMED settings page
   below /mypreferences/d/ is admitted, one at a time"*; the brief: *"each
   settings page is admitted by NAME, exactly, with a control shown failing"*.
   Nineteen pages clear without any other ruling (section 5), the four
   category pages first, and one of them (syncing, under `/mynetwork/`) has a
   load cost nobody has measured. May the live lane admit them as one reviewed
   batch -- each its own exact anchored line and its own failing control -- or
   must each admission precede only its own capture?
2. **THE SIGN IN AND SECURITY CATEGORY AND THE SIGN-IN PAGE -- CAPTURED AT
   ALL?** Ground: `READ-PAST-AN-ACT-SUBSTRING`, *"It does NOT reach a substring
   whose ground is the read itself: ... a credential, recovery, session or
   security surface; a sign-in challenge"*; and `CREDENTIAL-SETTINGS-NEED-THE-
   OPERATOR`. Those pages draw his email addresses, phone numbers and sessions.
   Until he says, `P N4`, `P N6`-`P N8`, `P N11` (surface C-SIGNIN) and
   `P N12` (`/uas/login`) stay GAP on this question, named rather than
   queued. (`P N5`, the password, is a typed field the writer refuses either
   way.)
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
   apart"*. Every confirm makes two loads in one call, back to back -- the
   page, then the verification's fresh render -- as every shipped write's
   confirm does, so the 20 s spacing can only hold between calls. With it
   held between calls, a benign press and its restore press sit about 45 s
   apart. Does that reading satisfy both rules for the 35 VISIBLE rows?
6. **`P N15`, THE INTERFACE LANGUAGE, IS FILED CANNOT-BE-PUT-BACK -- MY
   APPLICATION.** Ground: the ruling's exclusion, *"a setting whose change
   cannot be put back exactly"*. Changing the language changes every label
   LinkedIn draws, so this writer could not find the switch back by its
   admitted label. Confirm, or rule that a proof may restore it by hand.
7. **A LINKEDIN LEARNING SETTINGS PAGE (`J 157`).** Ground: its cell's own
   question, *"Whether the settings-family ruling reaches a Learning settings
   page"*, and its census blocker, LEARNING-SURFACE, which no ruling of
   2026-09-28 names. Lane K's ledger assigns the row to this lane, citing
   HIS-OWN-SETTINGS-NOT-OUTWARD; this lane holds it OUT until you say that
   ruling reaches a Learning page.
8. **THE WRITE DOOR EXCUSES TWO FORBIDDEN ENTRIES FOR ONE ACTION.** Ground:
   `assert_write_url`, which honoured exactly one `exempt_substring` per spec.
   The admitted address trips `"/settings/"` and `"settings"`, so the spec
   carries a new field, `exempt_substrings`, excusing both by equality -- the
   first spec to excuse two. Confirm the field, or prefer a per-page exemption
   table beside the registry.

NOTED, NOT ASKED: dark mode's receipt (`update_setting`) prints the same
retry sentence the cold review found untrue here -- *"it may do the same thing
twice, to the same person or the same employer"* -- of a radio aimed at a
value. This lane changed its own action's sentence and left that one to its
owner.

## 11. Instruments

Registered as section 85 of `_audit/INSTRUMENTS.md`.
