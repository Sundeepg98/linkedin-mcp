# Slice report: parity census -- skill coverage, deliberate exclusions, test-count pin

Date: 2026-08-22
Scope: READ-ONLY census. No file edited except this one. No MCP tool called, no
browser launched, no pytest run.

**ASCII note.** One source file quoted below (the memory file) contains
non-ASCII punctuation -- em dashes and arrows. Every quotation in this report
renders them as `--` and `->` so this file stays strict ASCII. Quotations are
otherwise verbatim.

---

## TWO DEVIATIONS FROM THE BRIEF, reported rather than papered over

**1. The skill is not where the brief said it is.** The brief located it "under
`C:\Users\Dell\.claude\`, likely `C:\Users\Dell\.claude\skills\linkedin-jobs\SKILL.md`,
else ... `C:\Users\Dell\.claude\plugins`". Both are wrong:
`C:\Users\Dell\.claude\skills\` **does not exist**, and a recursive name search
of the whole of `C:\Users\Dell\.claude` returns no `linkedin-jobs` directory --
only the memory file. The skill is **project-scoped**:

    D:\Sundeep\projects\job-hunting\.claude\skills\linkedin-jobs\

holding `SKILL.md` (18071 bytes, 348 lines), `parse_digest.py`,
`career_insights.py`, `referral_join.py`, `alert-tuning.md`,
`inmail-targeting.md`, `fixtures/`. This is the file the session's skill
listing advertises, and it is the file censused below.

**2. Part (3)'s premise does not hold: NO test count is pinned anywhere.**
Details in section 3. Nothing in `scripts/ci_full_run_check.py` or
`.github/workflows/ci.yml` hardcodes an expected total, and **adding tests
requires updating no number to keep the build green.** Three DIFFERENT counts
appear in the repo as prose, and they disagree with each other.

---

# 1. What the `linkedin-jobs` SKILL already covers

Source of truth: `D:\Sundeep\projects\job-hunting\.claude\skills\linkedin-jobs\SKILL.md`
(cited as `SKILL.md:N`) and
`C:\Users\Dell\.claude\projects\D--Sundeep-projects-job-hunting\memory\linkedin-jobs-skill.md`
(cited as `memory:N`).

## 1a. The data classes it OBTAINS from Gmail

### CLASS A -- Job-alert cards (primary)

`SKILL.md:24`

    | `jobalerts-noreply@linkedin.com` | saved job alerts (`origin=SEMANTIC_SEARCH_JOB_ALERT_EMAIL`) | up to 6 per email | primary -- ranked against the profile |

Per-card fields, `SKILL.md:121-123`:

    For each `View job:` line, walk **upwards**:
    ...
    3. The next three lines upward are, in order: **location, company, title**.

Job id and clean URL, `SKILL.md:110-112`:

    linkedin\.com/comm/jobs/view/(\d+)(?=[/?&#]|$)
        -> dedup key
        -> https://www.linkedin.com/jobs/view/{id}     tracking-free, hand this to the user

Measured yield, `SKILL.md:27-30`:

    Measured cadence: 5 job-alert emails/day on a staggered 2-hour cycle (04:44, 06:44,
    08:44, 10:44, 12:44 UTC), plus roughly one recommendation email. 29 threads in the 7 days
    to 2026-08-20 (28 alerts + 1 recommendation), carrying **166 cards / 154 unique jobs /
    43 with network proximity** across 26 companies.

### CLASS B -- Job recommendations (secondary)

`SKILL.md:25`

    | `jobs-noreply@linkedin.com` | "Jobs You Might Be Interested In" (`origin=FACET_SUGGESTIONS_COMMS_EMAIL`) | ~6, grouped 2 per facet | secondary -- markedly weaker, no flags |

### CLASS C -- Network proximity (the exclusive field)

`SKILL.md:13-16`

    The payload is worth having for one reason above all: the digests carry
    **network proximity** -- `2 connections`, `1 company alum` -- which LinkedIn computes
    against the user's own social graph. No scraper and no job-board API can produce that
    field. Rank on it.

The literal set, `SKILL.md:138-142`:

    | `This company is actively hiring` | hiring velocity |
    | `Apply with resume & profile` | Easy Apply eligible |
    | `N connection` / `N connections` | **network proximity -- the exclusive field** |
    | `N company alum` / `N company alumni` | **network proximity.** Both forms occur; live values run 1 to 28 |
    | `N school alum` / `N school alumni` | **network proximity**, rarer and weaker than company |

So CLASS C is three proximity counts plus two per-card badges: Easy-Apply
eligibility and hiring velocity.

### CLASS D -- Alert metadata / market telemetry

`SKILL.md:152-157`

    - `Your job alert for {QUERY} in {GEO}` -- which alert produced this. More reliable than
      the subject. Confirmation emails instead say
      `Your job alert has been created: {QUERY} in {GEO}.`
    - `{N} new jobs match your preferences.` -- market-volume telemetry only. **It is not the
      card count.** "18 new jobs" delivers 6. Never derive the expected card count from it.
    - `savedSearchId=` in the unsubscribe URL -- stable per-alert id.

### CLASS E -- Named first-degree PEOPLE (weekly career-insights email)

`SKILL.md:222-226`

    ## The weekly career-insights email -- people, not jobs

    A second, higher-value email: LinkedIn's weekly `Career trends in your network`. Verified
    cadence roughly every 7-8 days. Handled by `career_insights.py`.

Five sections, `SKILL.md:241-247`:

    | Section | Signal | Company available? |
    |---|---|---|
    | `Hiring in your network` | `hiring` | no -- and no profile link either |
    | `Open to work` | `open_to_work` | only inferable from the headline |
    | `Offering professional services` | `services` | only inferable from the headline |
    | `Job changes` | `job_change` | **yes, stated**: `New position as <Title> at <Company>` |
    | `Career milestones` | `work_anniversary` | **yes, stated**: `N years at <Company>` |

Per-entry fields: name, headline (absent in `Job changes`), a `/comm/in/` slug,
and a trailing fact line (new position, or tenure). `SKILL.md:265-270` records
that the `Hiring` section carries a post URL and **no slug at all**, so those
entries cannot be resolved to a person:

    **The hiring section is the weakest, not the strongest.** Its entries carry a post URL and
    **no `/comm/in/` slug at all** -- verified across every sampled week, and asserted in the
    selftest.

### CLASS F -- Derived: the warm-referral join (skill-computed, not read from mail)

`SKILL.md:272-280`

    ## Warm referrals and InMail -- `referral_join.py`

    The single most valuable thing in this skill: **companies where he has already applied and
    also has network.** That pairing does not appear in any UI he uses.

    It joins the job-alert proximity data and the career-insights people against the Naukri
    applications table at `mcp-servers/naukri/naukri.db`. **Open that database READ-ONLY
    (`mode=ro`) and never write to it.**

Live result, `memory:17-21`:

    **v2 added the highest-value object in the system: the warm-referral join.** It cross-references
    first-degree contacts from LinkedIn's weekly career-insights email against the **151 real
    applications in `naukri.db`** (opened READ-ONLY). Live result: **6 companies where he has BOTH an
    open application AND network** -- notably a first-degree connection who *just changed jobs to Amazon*
    against a live SDE application there. 142 of 151 applications are joinable; 9 have NULL company.

### CLASS G -- Degree of connection (asserted from a URL parameter, not counted)

`SKILL.md:294-296`

    **Everyone in the career-insights email is a first-degree connection**, so messaging them
    is a free direct message and costs no credit. This is not an inference -- LinkedIn's own
    hero link in that email carries `network=["F"]`, its code for first-degree.

## 1b. What the skill does NOT obtain -- stated so a tool proposal is not judged against a false baseline

**InMail credit COUNT is NOT read from Gmail or anywhere else.** The brief
listed it as a candidate class; it is not one. What exists is *arithmetic plus a
hand-kept ledger*.

`SKILL.md:307-311`

    Credit arithmetic, per `inmail-targeting.md`: 5 a month, accumulating to a 15 cap, each
    expiring 90 days after grant, and **refunded on accept, decline or reply within 90 days --
    only silence actually costs anything**. There are no follow-up sequences: he cannot message
    the same person again until they respond.

`memory:31-33`

    ... The tool
    splits free actions (1st-degree DM, replying to a received InMail, 300-char notes) from paid
    (out-of-network only) and ranks free first. **It cannot observe sends, so the credit ledger is
    hand-maintained -- a stated limit, not papered over.**

**Four Gmail senders are deliberately left unparsed**, `SKILL.md:56-59`:

    Genuinely card-free, and excluded by the sender filter alone: Premium upsells from
    `linkedin@em.linkedin.com`, and everything from `messages-noreply@`, `updates-noreply@`,
    `newsletters-noreply@`, `notifications-noreply@`. Those last three are networking and
    recruiter-inbound surfaces -- real value, but they reward human attention, not parsing.

Consequently the skill produces **no** equivalent of: profile views /
who-viewed-me, the LinkedIn-side application list and its statuses, saved jobs,
own-profile fields, or the notification list. Those five have no Gmail source in
this skill.

## 1c. The skill's own Scope clause bears directly on this census

`SKILL.md:339-348` -- quoted in full because it is a standing instruction about
this very repository:

    ## Scope

    Do not scrape LinkedIn, do not use the user's LinkedIn session or cookies, and do not
    revive `mcp-servers/linkedin/`. Reading mail LinkedIn sent to this inbox is a first-party
    relationship with an unsubscribe link; automating access to linkedin.com is not, and the
    asset at risk is the user's professional identity.

    For breadth beyond the 6-card cap, the JobSpy MCP already covers LinkedIn's logged-out
    search plus seven other boards. The two channels select differently -- measured overlap
    was 2 of 12 -- so run both rather than treating either as redundant.

`memory:43-45` says the same:

    **It is a SKILL over the existing user-scope Gmail MCP -- not a server, no credentials, no new
    process.** It replaces the retired scraping approach in `mcp-servers/linkedin/`, which is being
    stood down.

**Flagged, not adjudicated:** the skill (2026-08-20) and the memory both record
`mcp-servers/linkedin/` as retired / being stood down, while the server in that
directory is live and was being worked on as recently as 2026-08-22
(`_audit/2026-08-22-linkedin-preflight.md`). Whether the skill's Scope clause is
stale or still binding is a judgment for the lead. It is reported here because
part (1) exists to decide duplication, and this clause speaks to it directly.

## 1d. Overlap table -- skill coverage vs the eleven live tools

Mechanical comparison only; no recommendation attached.

| Live tool (`tests/test_server_surface.py:16-28`) | Skill equivalent? | Basis |
|---|---|---|
| `linkedin_search_jobs` | PARTIAL -- different selection, measured overlap 2 of 12 | `SKILL.md:346-348` |
| `linkedin_saved_jobs` | NO | no Gmail source |
| `linkedin_my_applications` | NO on the LinkedIn side; the Naukri applications table is joined instead | `SKILL.md:278-280` |
| `linkedin_who_viewed_me` | NO | no Gmail source |
| `linkedin_my_profile` | NO | no Gmail source |
| `linkedin_notifications` | NO -- `notifications-noreply@` explicitly unparsed | `SKILL.md:57-59` |
| `linkedin_auth_status` / `_login_browser` / `_session_info` / `_cdp_status` / `_server_info` | N/A -- server plumbing | |
| (no tool) network proximity per job | SKILL ONLY | `SKILL.md:13-16`, `138-142` |
| (no tool) named first-degree contacts | SKILL ONLY | `SKILL.md:241-247` |
| (no tool) warm-referral join | SKILL ONLY | `SKILL.md:272-280` |

---

# 2. Recorded DELIBERATE exclusions in the linkedin server

All paths relative to `D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\`.

## 2.1 README.md -- "What it deliberately cannot do"

`README.md:49-57`

    ## What it deliberately cannot do

    Applying to jobs. Saving or unsaving. Messaging, InMail, connection invitations.
    Profile edits. Open To Work. Posting, liking, commenting, endorsing. Marking
    notifications read. Collecting data about other members.

    These are not missing features. If a tool would change anything on LinkedIn's
    servers, it is out of scope, and `tests/test_readonly.py` fails the build if one
    appears.

| Excluded surface | Stated reason | Cite |
|---|---|---|
| Applying to jobs | changes state on LinkedIn's servers | `README.md:51,55-57` |
| Saving / unsaving jobs | same | `README.md:51,55-57` |
| Messaging, InMail, connection invitations | same | `README.md:51,55-57` |
| Profile edits, Open To Work | same | `README.md:52,55-57` |
| Posting, liking, commenting, endorsing | same | `README.md:52,55-57` |
| Marking notifications read | same | `README.md:52-53,55-57` |
| Collecting data about other members | scope: "Your data only ... No enumerating or harvesting other members" | `README.md:24`, `53` |

Two adjacent README statements of the same boundary:

`README.md:6-7`

    It reads. That is all it does. There is no write path in this repository -- not
    disabled, not stubbed, not behind a flag.

`README.md:24-25`

    | Your data only | Your profile views, your applications, your saved jobs, your profile, your notifications. No enumerating or harvesting other members. |
    | Reads only | Nothing is applied to, saved, sent, posted, endorsed, invited or edited. |

## 2.2 README.md -- non-write exclusions (capability limits, deliberately not built)

| Excluded surface | Stated reason | Cite |
|---|---|---|
| Experience / Education / Skills on the profile page | "LinkedIn defers them until it is scrolled, and this server does not scroll. They are reported as UNKNOWN, never as zero" | `README.md:379-382` |
| Auto-paging a search | "Ask for the next page of a search deliberately with `start=25`. Every list result carries `capped`, `page_had` and `limit`, so '25 results' is never mistaken for '25 results exist'." | `README.md:290-292` |
| More than one page load per tool call | rate discipline; sole exception is `linkedin_my_profile(include_skills=True)` at `pages_loaded: 2` | `README.md:287-289` |
| Jitter / stealth / fingerprint spoofing | "Throttling, not disguise: it is deliberately not jittered to resemble anything." | `README.md:285-286` |
| Any third Chromium flag | one flag only, enforced at launch; `tests/test_launch_boundary.py` fails the build if a third appears | `README.md:23`, `139-140` |
| Port 9223 | "Port **9224**, deliberately not the sibling Naukri server's 9223." | `README.md:275` |
| Closing the operator's browser in attach mode | "on teardown **disconnects without closing your browser**" | `README.md:278-281` |
| `artdeco-entity-lockup` class names as parse anchors | the fix "deliberately does not use" them, so they stay available as an independent check | `README.md:403-404` |

Two side effects are disclosed rather than excluded, `README.md:59-74` (relevant
because they are the two reads that are NOT side-effect-free):

    ### The two side effects, stated rather than hidden
    ...
    1. **Opening the notifications page clears LinkedIn's unread badge** ...
       **The only way not to clear the badge is not to call `linkedin_notifications`.**
    ...
    2. **Running a job search adds to your own recent-search history**, the same as
       typing the query on the site.

## 2.3 `linkedin_server/readonly.py` -- the comment above the `jobs-tracker` pattern

`readonly.py:50-69`, verbatim:

    # The job tracker, which is where /my-items/saved-jobs/ now redirects (the
    # cardType query is dropped on the way, and that older address is no longer
    # on this list because nothing builds it any more). ``?stage=`` selects
    # which of his own lists renders. It is a read: measured 2026-08-22 by
    # opening three stages in turn and re-reading the default view afterwards,
    # where every tab count was unchanged. The tab strip itself is a set of
    # client-side radios with no url of their own, so ``?stage=`` is the ONLY
    # way to reach the applied list without clicking -- which is exactly why
    # this pattern exists rather than a click.
    #
    # The two stages are ENUMERATED rather than left as ``?[^#]*``. LinkedIn's
    # own payload also names interview, archived, draft and clicked_apply, and
    # a wildcard would have admitted all of them plus ``?stage=withdraw`` and
    # ``?apply=1`` -- unreachable today, since the stage is a literal in
    # server.py and never a tool argument, but an allowlist should permit what
    # is opened rather than what happens to be harmless. A third stage needs a
    # deliberate edit here, which is the point.
    re.compile(
        r"^https://www\.linkedin\.com/jobs-tracker/\?stage=(saved|applied)$"
    ),

| Excluded surface | Stated reason | Cite |
|---|---|---|
| `?stage=interview`, `archived`, `draft`, `clicked_apply` | enumerated allowlist: "an allowlist should permit what is opened rather than what happens to be harmless. A third stage needs a deliberate edit here, which is the point." | `readonly.py:60-66` |
| `?stage=withdraw`, `?apply=1` | a wildcard query would have admitted them | `readonly.py:62-63` |
| `/my-items/saved-jobs/?cardType=...` | removed from the allowlist because "nothing builds it any more" | `readonly.py:50-52` |

## 2.4 `tests/test_readonly.py` -- the `BLOCKED` list and its inline rationale

`test_readonly.py:247-285`. The action-URL and scale-harvest entries, verbatim:

    BLOCKED = [
        # Actions on LinkedIn.
        "https://www.linkedin.com/jobs/application/12345",
        "https://www.linkedin.com/messaging/thread/2-abc/",
        "https://www.linkedin.com/mynetwork/invitation-manager/",
        "https://www.linkedin.com/in/someone/edit/topcard/",
        "https://www.linkedin.com/psettings/open-to-work",
        "https://www.linkedin.com/feed/update/urn:li:activity:123/",
        "https://www.linkedin.com/voyager/api/relationships/invitations",
        "https://www.linkedin.com/notifications/?action=markAllRead",
        # Other people's data at scale, and other hosts entirely.
        "https://www.linkedin.com/search/results/people/?keywords=cto",
        "https://www.linkedin.com/company/acme/people/",

then the job-tracker group, `test_readonly.py:265-278`:

        # The job tracker, which the allowlist admits at exactly two addresses.
        # A wildcard query would have let every one of these through.
        "https://www.linkedin.com/jobs-tracker/",
        "https://www.linkedin.com/jobs-tracker/?stage=withdraw",
        "https://www.linkedin.com/jobs-tracker/?stage=archived",
        "https://www.linkedin.com/jobs-tracker/?apply=1",
        "https://www.linkedin.com/jobs-tracker/?stage=saved&save=1",
        ...
        # The address the tracker replaced. Nothing builds it any more, so it is
        # off the list -- a pattern kept for a url the server never opens is a
        # door with nobody watching it.
        "https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED",

The entries elided above and at `:260-264` / `:279-284` are hostile-input
negative test cases (foreign hosts, `javascript:`, `file:`, percent-encoding,
path traversal, a lookalike host, CR/LF and leading/trailing whitespace). They
are fixtures asserted to be REFUSED, not LinkedIn surfaces under consideration.

Three inline rationale comments, each a stated reason:

| Excluded surface | Stated reason | Cite |
|---|---|---|
| Every `jobs-tracker` address except the two allowed | "A wildcard query would have let every one of these through." | `test_readonly.py:265-266` |
| `/my-items/saved-jobs/?cardType=SAVED` | "Nothing builds it any more, so it is off the list -- a pattern kept for a url the server never opens is a door with nobody watching it." | `test_readonly.py:275-278` |
| Trailing/leading whitespace forms | "'$' matches before a trailing newline and '[^#]*' matches a CRLF." | `test_readonly.py:279-280` |

Companion pin in the same suite, `test_readonly.py:288-301`: the `/edit/`
refusal is asserted to come from the FORBIDDEN gate, not the allowlist --

    ``dom.SKILL_HREF`` matches an inline edit affordance, and the argument that
    it can never become a navigation rests on ``/edit/`` being refused BEFORE
    the allowlist is consulted.

## 2.5 `linkedin_server/server.py` -- last paragraph of the `linkedin_saved_jobs` docstring

`server.py:544-545`, verbatim:

    The tracker also holds In Progress, Interview and Archived tabs. They are
    not exposed as tools: this reads the two lists it names and nothing else.

| Excluded surface | Stated reason | Cite |
|---|---|---|
| In Progress tab | "not exposed as tools: this reads the two lists it names and nothing else" | `server.py:544-545` |
| Interview tab | same | `server.py:544-545` |
| Archived tab | same | `server.py:544-545` |

This is the tool-surface half of the same boundary `readonly.py:60-66` enforces
at the URL half. The two agree.

## 2.6 `linkedin_server/server.py` -- other recorded exclusions

`server.py:981-989`, the machine-readable list returned by `linkedin_server_info`:

    "out_of_scope_by_design": [
        "applying to jobs",
        "saving or unsaving jobs",
        "messaging, InMail, connection invitations",
        "profile edits and Open To Work",
        "posting, liking, commenting, endorsing",
        "marking notifications read",
        "collecting data about other members",
    ],

with `server.py:970-971`:

    "read_only": True,
    "writes_available": [],

and `server.py:990-993`:

    "known_side_effects": [
        "opening the notifications page clears the unread badge",
        "running a job search adds to your own recent-search history",
    ],

`server.py:89-94` -- the FastMCP `instructions` string, which is what a client
model reads first:

    "Read-only window onto the operator's OWN LinkedIn account, driven by "
    "his own signed-in browser on his own machine. Every tool reads; none "
    "of them changes anything on LinkedIn. There is no apply, no save, no "
    "message, no connection request, no profile edit -- those are out of "
    "scope by design, so do not look for them or suggest they exist. "

`server.py:709-718` -- `linkedin_my_profile`:

    On completeness: LinkedIn's own profile-strength meter is not exposed
    here, so this server does not report one. What it reports is derived and
    labelled as such.

    One honest limitation, stated because its absence would otherwise read as
    data: LinkedIn now defers Experience, Education and Skills until the page
    is SCROLLED, and this server does not scroll. Those sections are therefore
    usually absent from the render, and absent means UNKNOWN here, never zero.

`server.py:595-598` -- `linkedin_search_jobs`:

    One page load per call, no scrolling and no auto-paging -- LinkedIn puts
    roughly 25 results on a page, so ask for the next page deliberately with
    start=25, start=50 and so on.

| Excluded surface | Stated reason | Cite |
|---|---|---|
| Profile-strength meter | "not exposed here, so this server does not report one" | `server.py:709-711` |
| Experience / Education / Skills sections | "this server does not scroll ... absent means UNKNOWN here, never zero" | `server.py:713-718` |
| Scrolling, auto-paging | one page load per call | `server.py:595-597` |

## 2.7 `tests/test_server_surface.py` -- the negative tool-name list

`test_server_surface.py:30-49`, verbatim:

    #: Names a reader must never grow. Listed explicitly so that adding one is a
    #: failing test rather than a code review someone might skim.
    FORBIDDEN_TOOLS = {
        "linkedin_apply",
        "linkedin_apply_job",
        "linkedin_easy_apply",
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_send_message",
        "linkedin_send_inmail",
        "linkedin_connect",
        "linkedin_invite",
        "linkedin_endorse",
        "linkedin_follow",
        "linkedin_post",
        "linkedin_update_profile",
        "linkedin_set_open_to_work",
        "linkedin_mark_notification_read",
        "linkedin_withdraw_application",
    }

Module docstring, `test_server_surface.py:1-7`:

    """The tool surface: eleven tools, and not one of them offers a write.

    The brief for this server drew a hard line -- no writes, not now, not stubbed,
    not "for later". This file is that line expressed as assertions, including on
    the docstrings, because a tool that merely SOUNDS like it can apply to a job
    will be called as though it can.
    """

Note the overlap with the skill: `linkedin_send_inmail` is a build-failing name
here (`test_server_surface.py:39`), while InMail *targeting advice* is a skill
capability (`SKILL.md:272`, `307-314`). The skill draws the same line at
`SKILL.md:313-314`:

    The tool **recommends only**. It never sends, drafts-and-sends, or touches LinkedIn. He
    sends by hand in the browser. Do not add sending.

## 2.8 `linkedin_server/readonly.py` -- the docstring-check carve-out

`readonly.py:331-334`

    #: Words that turn a write verb into a boundary statement rather than a claim.
    #: "has no way to add or remove" is exactly the sentence a read-only tool
    #: SHOULD contain, so a docstring check that banned the verbs outright would
    #: forbid the clearest possible documentation of the boundary.

Reason a check was deliberately built as negation-aware rather than a keyword
ban. Mirrored in prose at `README.md:133-137`.

## 2.9 `_audit/` -- what is there

Two files, neither a parity or exclusion document.

- `_audit/_slice-cookie-jar.md` -- cookie-jar reader slice, 2026-08-22.
  Scope-limiting statements only; no LinkedIn surface excluded. Its three
  SURPRISES (`:167-186`) are: a live Playwright Chromium holding the profile at
  PID 31472; **no `_state\chrome-profile.lock` despite that process holding the
  profile** (`:180-183`, "Outside this slice -- flagged, not touched"); and
  **`_audit/` is not covered by `.gitignore`** (`:184-186`), so this census file
  is likewise tracked-by-default. One design exclusion,
  `_slice-cookie-jar.md:107-111`: "No cookie value is ever fetched. The query is
  a module constant naming five metadata columns; there is no wildcard select
  and the sealed blob column is never named anywhere in the file."
- `_audit/2026-08-22-linkedin-preflight.md` -- preflight + `session_info` slice.
  One exclusion-shaped statement, `:11`: "`authenticated` still comes only from a
  real `GET /voyager/api/me`; offline it is `null`, never a cookie's presence."

**NOT FOUND in `_audit/`:** any prior parity census, any list of surfaces
considered-and-rejected, any record of a proposed tool being declined.

---

# 3. The exact test count and how it is asserted

## 3.1 The finding: NOTHING pins the test count

`scripts/ci_full_run_check.py` hardcodes **no** expected total. Both numbers it
compares are computed at run time from the same checkout.

`ci_full_run_check.py:16-24` states the design:

    Neither shows up in a green check mark. So this script compares two numbers
    that come from the SAME checkout and must therefore agree:

      * COLLECTED -- what ``pytest --collect-only`` says exists;
      * RAN -- what the junit report says was executed.

    A gap between them is a deselection. A non-zero skip count is a test that
    decided it could not run here. Both fail this check, and both print the exact
    number rather than a summary word.

The whole of the assertion logic, `ci_full_run_check.py:117-146`, verbatim
(the third `problems.append` message elided at its tail only):

    collected = collected_count(argv[1])
    totals = junit_totals(argv[2])
    ran = totals["tests"]
    skipped = totals["skipped"]
    executed = ran - skipped

    publish(
        f"collected {collected} | reported {ran} | executed {executed} | "
        f"skipped {skipped} | failed {totals['failures']} | "
        f"errors {totals['errors']}"
    )

    problems = []
    if collected == 0:
        problems.append("collection found ZERO tests, so nothing was gated")
    if ran != collected:
        problems.append(
            f"{collected - ran} test(s) were DESELECTED: collection found "
            f"{collected} but only {ran} reached the report. A deselected "
            f"test leaves no trace in junit, which is why this is compared "
            f"against collection rather than read off the report"
        )
    if skipped:
        problems.append(
            f"{skipped} test(s) SKIPPED. ..."
        )

`collected` comes from `collected.txt` (`ci.yml:151`,
`python -m pytest --collect-only -q | tee collected.txt | tail -1`); `ran` comes
from `junit.xml` (`ci.yml:157`). The only literal in the file's matching logic is
the regex, `ci_full_run_check.py:76`:

    _COLLECTED = re.compile(r"(\d+)\s+tests?\s+collected")

which captures whatever number is present.

**Answer to "does adding new tests require updating that number?": NO.** The
three comparisons -- `collected == 0`, `ran != collected`, `skipped != 0` -- are
all relative. A new test appears in both `collected.txt` and `junit.xml`, and the
gate stays green with no edit anywhere.

What the gate DOES catch, `ci_full_run_check.py:4-14`: a suite that silently
shrinks, by deselection (`-m`, `--ignore`, `--deselect`) or by environment skip.
Skips are a hard failure by choice, `ci_full_run_check.py:30-38`.

## 3.2 The three numbers that DO appear, all prose, none asserted

| Number | Where | Executes? |
|---|---|---|
| **576** | `README.md:341` -- "tests/                       576 tests, no network, no account" | no -- code-tree diagram |
| **576** | `README.md:347` -- "Built and tested: **576 tests**, no network and no account." | no -- prose |
| **576** | `README.md:86` -- "python -m pytest            # 576 passed" | no -- a comment inside a fenced setup block |
| **650** | `_audit/2026-08-22-linkedin-preflight.md:14` -- "**579 -> 650 tests, all passing.** Commits `oldsha03`, `oldsha21`, pushed." | no -- audit prose |
| **684** | `.github/workflows/ci.yml:3` -- "# This suite has 684 tests and has never run anywhere but one Windows laptop." | no -- YAML comment |
| **684** | `.github/workflows/ci.yml:11` -- "# browser binary absent, 77 of the 684 fail, all with the identical error:" | no -- YAML comment |
| **684** | `scripts/ci_full_run_check.py:73-74` -- "#: pytest 8 ends ``--collect-only -q`` with a line like '684 tests collected / in 0.42s'" | no -- an EXAMPLE of the regex's input format |
| **684** | `scripts/ci_full_run_check.py:13` -- "marked skipped, and a human reading '684 passed, 79 skipped' in a collapsed log" | no -- illustrative prose |

**These disagree: 576 (README) vs 650 (audit, 2026-08-22) vs 684 (ci.yml).**
Since none is asserted, none can be failed by a build, and the divergence is
invisible to CI by construction. Reported as an observation.

The 684 in `ci.yml` also carries a dependent number that would move with it,
`ci.yml:9-11`: "With the browser binary absent, 77 of the 684 fail", the
justification for installing chromium on CI (`ci.yml:133-137`).

**The live collected count is UNMEASURED.** The brief forbids running pytest, and
`pytest --collect-only` is the only thing that produces it. A raw grep of
`^\s*(async )?def test_` across `tests/` returns **416** function definitions --
that is a DERIVED LOWER BOUND, not the collected count, because
`@pytest.mark.parametrize` expands one definition into many (for instance
`test_readonly.py:304` and `:309` parametrize over the `ALLOWED` and `BLOCKED`
lists). Do not read 416 as comparable to 576 / 650 / 684.

## 3.3 What IS pinned as a literal, and does require updating

The **tool** count, not the test count. `tests/test_server_surface.py:57-59`,
verbatim:

    async def test_the_surface_is_exactly_the_eleven_reads(tools):
        assert set(tools) == EXPECTED_TOOLS
        assert len(tools) == 11

`EXPECTED_TOOLS` is the eleven-name set at `test_server_surface.py:16-28`:

    EXPECTED_TOOLS = {
        "linkedin_auth_status",
        "linkedin_login_browser",
        "linkedin_who_viewed_me",
        "linkedin_my_applications",
        "linkedin_saved_jobs",
        "linkedin_search_jobs",
        "linkedin_my_profile",
        "linkedin_notifications",
        "linkedin_server_info",
        "linkedin_session_info",
        "linkedin_cdp_status",
    }

**Adding a tool therefore requires two edits in this file** -- the name into
`EXPECTED_TOOLS` (`:16-28`) and the integer `11` (`:59`) -- or the build fails.
That is the only hardcoded count in the gate path found by this census.

Adjacent non-gating literals: `README.md:339` describes `server.py` as "the
eleven tools", and `test_server_surface.py:1` as "eleven tools". Prose, not
asserted. `README.md:35-47` is the eleven-row tool table.

## 3.4 One further CI note relevant to counts

`ci.yml:139-146` runs a standalone import check that prints the registered tool
count without asserting it:

    - name: The server imports and registers its tools
      run: |
        python -c "import asyncio; from linkedin_server.server import mcp; \
        print('tools registered:', len(asyncio.run(mcp.list_tools())))"

Printed, not gated -- `ci.yml:141-143` says so: a decorator error "would surface
as a wall of assertion failures rather than as one line saying the surface is
empty." `test_server_surface.py:59` is what gates it.

Suite config, `pytest.ini:1-4`: `testpaths = tests`, `pythonpath = .`,
`addopts = -ra`. No count, no marker filter, no `--ignore`. `pytest.ini:19` sets
`asyncio_mode = auto`.

---

# Provenance

Every line quoted above was read from disk in this slice. Files opened:

    D:\Sundeep\projects\job-hunting\.claude\skills\linkedin-jobs\SKILL.md
    C:\Users\Dell\.claude\projects\D--Sundeep-projects-job-hunting\memory\linkedin-jobs-skill.md
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\README.md
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\linkedin_server\readonly.py
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\linkedin_server\server.py
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\tests\test_readonly.py
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\tests\test_server_surface.py
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\scripts\ci_full_run_check.py
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\.github\workflows\ci.yml
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\pytest.ini
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\_audit\_slice-cookie-jar.md
    D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\_audit\2026-08-22-linkedin-preflight.md

Not run: pytest, any MCP tool, any browser, any git command.
