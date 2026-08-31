# Slice: complete the README read-tool table

Scope: `README.md` only. One file modified, 15 insertions, 2 deletions. Nothing
under `tests/` or `linkedin_server/` was touched. Nothing committed, nothing
staged, `_state/` untouched, no browser launched, no `mcp__linkedin__*` call.

Base: branch `master`, HEAD `24cba07`, tree clean at start.

---

## 1. The numbers, derived rather than taken from the brief

The brief's numbers were checked against the pins before a word was written,
and all three hold.

| Claim | Where it is pinned | Read value |
|---|---|---|
| 31 registered tools | `tests/test_server_surface.py:356` -- `assert len(tools) == 31` | 31 |
| 19 non-write tools | `tests/test_server_surface.py:413` -- `assert len(set(tools) - SANCTIONED_WRITE_TOOLS) == 19` | 19 |
| 12 write-shaped names | `tests/test_server_surface.py:391-405` -- the `set(tools) & SANCTIONED_WRITE_TOOLS` literal | 12 |
| 5 performable writes | `tests/test_server_surface.py:1250` -- `f"{words[len(writes.PERFORMABLE)]} write" in text` | `len(writes.PERFORMABLE) == 5` |

The brief pointed at "line 1252" for the write count. The nearest assertion is
at line 1250, and it asserts the count INDIRECTLY, through
`len(writes.PERFORMABLE)` rendered as an English word into `mcp.instructions`,
not as a bare integer. Same number, different mechanism; noted so the pointer
is not carried forward wrong.

Also worth stating precisely, because the brief calls the 19 "read tools" and
the test does not: line 413 asserts the NON-WRITE count, and the test's own
comment says so ("THE NON-WRITE COUNT MOVES TO SIXTEEN"). Two of the 19 are not
reads in the strict sense -- `linkedin_login` opens a sign-in window and
`linkedin_logout` erases the local cookie jar -- but neither writes to LinkedIn,
which is the line the table's `Reads` column has always drawn (the pre-existing
`linkedin_logout` row already says "The one destructive tool here"). The table
was completed on the registered-non-write set, so its rows are exactly the set
line 413 counts.

## 2. The 19, enumerated from `@mcp.tool()` in `linkedin_server/server.py`

31 decorated functions were enumerated from source, then the 12 write-shaped
names were subtracted. The remainder was verified by set equality against a
live `mcp.list_tools()` and against the table rows parsed back out of the
edited README -- `table == reads: True`, no missing, no extra, no duplicates.

Subtracted, 5 performable: `linkedin_save_job`, `linkedin_unsave_job`,
`linkedin_unfollow_company`, `linkedin_follow_company`, `linkedin_apply_job`.

Subtracted, 7 write-shaped refusers: `linkedin_publish_post`,
`linkedin_comment_on_item`, `linkedin_react_to_item`,
`linkedin_update_profile_field`, `linkedin_update_setting`,
`linkedin_send_invitation`, `linkedin_send_message`.

The 19 that remain, with whether the table already carried them:

| # | Tool | In the table before this slice? |
|---|---|---|
| 1 | `linkedin_auth_status` | yes |
| 2 | `linkedin_login` | NO -- added |
| 3 | `linkedin_login_browser` | yes, but as the primary login row |
| 4 | `linkedin_session_info` | yes |
| 5 | `linkedin_logout` | yes |
| 6 | `linkedin_cdp_status` | yes |
| 7 | `linkedin_who_viewed_me` | yes |
| 8 | `linkedin_my_applications` | yes |
| 9 | `linkedin_draft_applications` | NO -- added |
| 10 | `linkedin_new_messages` | NO -- added |
| 11 | `linkedin_open_messaging` | NO -- added |
| 12 | `linkedin_saved_jobs` | yes |
| 13 | `linkedin_search_jobs` | yes |
| 14 | `linkedin_job_detail` | yes |
| 15 | `linkedin_followed_companies` | yes |
| 16 | `linkedin_my_profile` | yes |
| 17 | `linkedin_notifications` | yes, one clause, no side effect stated |
| 18 | `linkedin_surface_census` | NO -- added |
| 19 | `linkedin_server_info` | yes |

Fourteen rows, nineteen reads, five omitted. The brief's count is exact.

## 3. What was written, and the docstring each row came from

Every description was taken from the tool's own docstring in `server.py`.
Nothing was invented and no capability was widened.

**`linkedin_login`** (added) -- from `server.py:476`. Sources: "A browser opens
and YOU type; nothing is automated"; "never sees, types, stores or transmits a
password"; "THE CANONICAL NAME, from 2026-08-25" with the three sibling
spellings; "A cookie appearing does not end the wait"; "On timeout the result
is authenticated false with a reason, never an optimistic success"; "THERE IS
NO REAUTH HERE, and that is deliberate rather than missing... LinkedIn issues
this server no refresh token".

**`linkedin_login_browser`** (rewritten) -- from `server.py:514`. It was the
table's primary login row and it is the DEPRECATED ALIAS. Sources: "DEPRECATED
ALIAS. Call ``linkedin_login`` instead; this forwards to it"; "removing a name
that used to work is a worse failure than carrying one"; "there is no plan to
remove it".

**`linkedin_draft_applications`** (added) -- from `server.py:804`. Sources: "the
job applications you STARTED on LinkedIn and never sent"; the tab is "LABELLED
'In Progress' and ADDRESSED as ``?stage=draft``"; "A DRAFT IS NOT AN
APPLICATION... an empty list here is not evidence about anything you did send";
the unpressed row controls including "Delete" and its dialog; "An empty result
says so explicitly and carries LinkedIn's own count for the tab".

**`linkedin_new_messages`** (added) -- from `server.py:852`. Sources: "Has
anything ARRIVED since you last opened Messaging? Nothing is opened"; "THIS IS
NOT AN UNREAD COUNT"; the badge "counts NEW-SINCE-LAST-VISIT and resets the
moment you open the Messaging tab"; measured "with a genuinely unread recruiter
InMail on screen, the badge read 0"; "never opens a conversation, and never
loads the messaging surface at all. It reads the badge off your feed"; and the
third outcome, "``null`` when the badge did not render -- which is NOT the same
as zero and is never reported as zero".

**`linkedin_open_messaging`** (added) -- from `server.py:901`. Sources: "OPENS A
THREAD"; "it redirects into ONE SPECIFIC CONVERSATION, and LinkedIn chooses
which... Measured twice"; "WHETHER OPENING MARKS THAT MESSAGE READ IS
UNMEASURED, and after three attempts it is believed unmeasurable from
outside... The only signal that would settle it requires performing the act
being measured. If the person who wrote to you can see read receipts, they may
see one"; "UNREAD IS PAIRED TO THE ROW"; "THE COUNT IS A FLOOR, NOT A TOTAL";
"NAMES ARE OFF BY DEFAULT" and "The thread identifier in the landed url is
always redacted"; "Only seven named pills can be activated... an arbitrary
string can never become a click target"; "all six are buttons with no href, so
that surface is not reachable by navigation".

**`linkedin_notifications`** (existing row expanded) -- from `server.py:1635`.
Sources: the "SIDE EFFECT -- READ FIRST" block: "Loading the notifications page
CLEARS YOUR UNREAD BADGE"; "MEASURED, not theorised: one call on 2026-08-21
took the badge from 1 to 0, and it does not come back"; "no click, no scroll
and no per-item open is involved, and there is no mark-as-read call anywhere in
this package"; "The only way not to clear the badge is not to call this tool";
"each row carries 'unread'... which is the fact the page load is about to
destroy".

**`linkedin_surface_census`** (added) -- from `server.py:1822`. Sources: the
"WHAT THIS IS FOR -- READ FIRST" block; "IT LOADS EXACTLY ONE PAGE AND CLICKS
NOTHING"; "A CONTROL BEING PRESENT IS NOT EVIDENCE THAT ACTIVATING IT IS SAFE";
"THE CENSUS REPORTS SHAPES, NEVER NAMES"; "ON COMPLETENESS -- ABSENT MEANS
UNKNOWN, NEVER ZERO"; the five-key enumeration and "A KEY, never a url"; and
"Notifications, /mynetwork/ and messaging are deliberately not offered... a
census is not worth a side effect".

### The one place the brief and the source disagree, and what was written instead

The brief grouped `linkedin_open_messaging` AND `linkedin_new_messages` under
one sentence: "opening messaging clears the messaging badge AND opens one
conversation LinkedIn chooses, measured twice."

That is true of `linkedin_open_messaging` and FALSE of `linkedin_new_messages`.
The latter's docstring is explicit: "This never sends a message, never opens a
conversation, and never loads the messaging surface at all. It reads the badge
off your feed, which this server already loads. One page." Its implementation
navigates to `FEED_URL` and returns `"opened_a_conversation": False`.

The badge-reset fact appears in that docstring for the OPPOSITE reason: the
badge resetting when YOU open the Messaging tab is why the number it returns is
new-since-last-visit rather than an unread count. It is a caveat on the reading,
not a cost of the call.

Writing the brief's sentence into the `linkedin_new_messages` row would have
invented a side effect the tool does not have, on the one tool built to avoid
it. So the rows were split: `linkedin_open_messaging` carries the thread-opening
and the badge reset; `linkedin_new_messages` states that it opens nothing and
loads no messaging surface, and carries the not-an-unread-count caveat instead.

Second, smaller: the brief listed `linkedin_notifications` among "the missing
ones". It was not missing -- it was row 8, reading "Your notification list." in
full, with no side effect stated. The substance of the instruction was clear and
was followed: the row now carries the badge clear. Only the framing was off.

## 4. The call on `linkedin_surface_census`: INCLUDED, labelled

It is in the table, and its row opens with what it is rather than what it does:
"**An instrument for extending this server, not a job-search tool**".

The reason is the argument `tests/test_server_surface.py` already makes about
this exact tool, at lines 330-337: it is counted "because this file counts what
is REGISTERED -- a tool that is exempt from the surface count because somebody
classified it as internal is exactly the hole this set-equality exists to
close." The table now claims to be all nineteen reads. Omitting the census
because it is "not really a feature" would open that same hole one document
over, and would put the table back into disagreement with the count in the
opening line of the README -- which is the defect this slice exists to fix.

Including it while letting it read like a feature would be the other failure,
so the row leads with the disclaimer, says no job-search answer is in it, and
carries the three limits the docstring is emphatic about (shapes not names,
absent means unknown, presence is not permission).

## 5. Stale claims found in README.md

### Corrected, in scope

1. **The table was 14 rows for 19 reads.** Completed, with a note above the
   table naming the five that were omitted -- the house convention of
   correcting rather than quietly widening, matching the existing "This row
   said 'Reads only' until 2026-08-23" sentence.
2. **The table's login row was the deprecated alias.** `linkedin_login_browser`
   was the only login row and carried the description; `linkedin_login` is the
   canonical name and was absent. The canonical name now leads with the full
   description and the alias row is labelled as an alias.
3. **`linkedin_notifications` was one clause with no side effect.** The tool
   whose docstring opens with "SIDE EFFECT -- READ FIRST" was described as
   "Your notification list." The table is where a reader looks before calling
   something, so the badge clear is now in the row.

No stale COUNT was found in the section heading or in an introductory sentence.
The heading is `## What it can do` and the table header is `| Tool | Reads |`;
neither carries a number, and there was no sentence between them. The count the
14 rows contradicted lives in the opening line of the file -- "**Thirty-one
tools ship. Nineteen read. Five write. The other seven are write-shaped, gated,
and cannot act at all.**" -- which is CORRECT and was left alone. The added note
points at it explicitly.

### Found and deliberately NOT changed -- out of slice, flagged for the lead

These are real and they are all in `## What it deliberately cannot do`
(README.md lines 279-341 before this edit; +15 after). They are not the read
table, so they were not touched. Every one of them is a claim the 2026-08-30
wave falsified.

1. **"Following a company." is listed as something the server cannot do**, and
   the paragraph beginning "**Following is the interesting one**" says it "is
   still not performable". `linkedin_follow_company` ships as one of the five
   performable writes, and the README's own write table says so. The two
   sections contradict each other.
2. **"Submitting applications, per the section above."** `linkedin_apply_job`
   ships. The pointer to "the section above" may carry this, since off-site
   applications genuinely are refused, but the bare clause in the list reads as
   a flat denial.
3. **"Messaging, InMail, connection invitations. Profile edits. Open To Work...
   Posting, liking, commenting, endorsing."** Seven tools for these are now
   REGISTERED and refusing. "Cannot do" is still true of the effect; the list
   now under-describes the surface, which is the same shape of staleness
   `tests/test_server_surface.py:1261-1275` records for `mcp.instructions`.
4. **"Reading your own inbox is UNMEASURED, not refused... It has NOT been run,
   and the forbidden list is unchanged until it is."** Both halves are now
   false. `linkedin_open_messaging` reads the inbox and is registered, the read
   boundary admits the messaging surface, and the hypothesis this paragraph
   calls unverified -- that the view opens a conversation on arrival -- is
   exactly what the tool's docstring reports as measured twice.
5. **The heading "### The two side effects, stated rather than hidden" and its
   two-item list.** There is at least a third: `linkedin_open_messaging` opens
   somebody's conversation and resets the messaging badge. The count in that
   heading is stale in the same way the read-table count was.

### Found outside README.md, not touched (not my file)

6. **`linkedin_server/server.py:1655`**, inside the `linkedin_notifications`
   docstring: "It is the ONE server-side change any tool here causes.
   Everything else in this package leaves LinkedIn exactly as it found it."
   `linkedin_open_messaging` opens a conversation and resets a badge, and five
   tools perform writes. This sentence is a claim, it is false, and it is in a
   docstring an assistant answers from. Flagged only; `linkedin_server/` is out
   of this slice.

## 6. Constraints, checked

- **Strict ASCII.** README.md verified byte-wise: zero bytes above 127, zero
  CRLF, no em-dash or smart-quote codepoints. Only `--` is used.
- **PII guard.** No email, no digit run a phone shape could match, no member
  slug, no urn, no sha of any length. `tests/test_no_committed_identity.py`
  passes. No `DECLARED_PLANTS` entry was added or needed.
- **Verification.** `venv\Scripts\python.exe -m pytest -q
  tests/test_server_surface.py tests/test_no_committed_identity.py
  tests/test_path_hygiene.py` -> **236 passed** in 20.56s. The full suite was
  not run, per the brief.
- **Independent check.** The 19 rows parsed back out of the edited README were
  asserted set-equal to `mcp.list_tools()` minus the 12 write-shaped names:
  equal, no missing, no extra, no duplicate row.
- `git status --short` shows exactly ` M README.md` plus this untracked file.
