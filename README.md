# linkedin

An MCP server that shows you your own LinkedIn account data as structured tool
results instead of pages you have to click through.

**Thirty-three tools ship. Twenty-one read. Five write. The other seven are
write-shaped, gated, and cannot act at all.**

This line said *"Fourteen of its seventeen tools read and change nothing.
Three write"* until 2026-08-31, and it is corrected rather than quietly
widened: every one of those three numbers was stale, and the write count was
stale in the direction that matters. The numbers above are derived rather
than counted by hand -- thirty-three and twenty-one are pinned in
`tests/test_server_surface.py`, five is `len(writes.PERFORMABLE)`, and the
seven that cannot act are what is left over. The five are named in
[The five that write](#the-five-that-write).

It then read *"Thirty-one tools ship. Nineteen read"* for the rest of that
same day, until `linkedin_profile_editor_fields` was registered. That one is
a READ and the write count did not move, which is why the correction is worth
one sentence rather than a paragraph -- but it is written down, because the
failure this section records is a count going stale by one and nobody
noticing.

And it read *"Thirty-two tools ship. Twenty read"* for the rest of THAT day,
until `linkedin_my_activity_items` was registered -- also a READ, also with
the write count unmoved. Two stale-by-one corrections in one day is not a
coincidence worth smoothing over: it is what a hand-carried count does, and
it is why the sentence above says the numbers are derived and names where.

Until 2026-08-23 this paragraph said *"It reads. That is all it does. There is
no write path in this repository -- not disabled, not stubbed, not behind a
flag."* That was true, it was enforced rather than asserted, and it stopped
being true the day `linkedin_save_job` shipped. A README that keeps the
comfortable sentence is the first thing a reader trusts and the first thing
that misleads them.

What is true now:

- The package contains **exactly one** call that can change anything on
  LinkedIn: a single anchored click in `writes.perform`. The source scanner
  still reports it -- it was not taught to stop looking -- and it is admitted by
  path, function and kind in a one-line allowlist that the tests fail if it
  widens.
- **Writes are off unless you turn them on.** `LINKEDIN_ENABLE_WRITES=1`, per
  process. A fresh clone cannot write to LinkedIn at all.
- **Every write is two calls.** The first performs nothing and hands you a
  block to read; the second redeems a single-use token from it. The token is
  bound to one action on one target and dies in 120 seconds, which makes a
  scheduled or unattended write structurally impossible rather than merely
  discouraged.
- `linkedin_unsave_job` is built, gated and **performable since 2026-08-30**.
  It refused for a month for want of one measured label; see
  [The one that refused, and how it stopped](#the-one-that-refused-and-how-it-stopped).
- **It does not submit applications, and that is not a shrug.**
  `linkedin_job_detail` reports `apply_path`: whether a posting applies on
  LinkedIn or hands you to an outside applicant-tracking system, and names
  that system. The identifying half ships as a read. The submitting half is
  refused for a measured reason -- see
  [Applying: the half that ships](#applying-the-half-that-ships-and-the-half-that-does-not).

---

## Read this part before anything else

**LinkedIn's User Agreement restricts automated access to the site.** That is
true regardless of how this server is built, and nothing below changes it.

What this design does is minimise exposure rather than pretend it away:

| Choice | Why it lowers the risk |
|---|---|
| Human-directed only | Every call is one you made, in the moment. Nothing runs on a timer, nothing runs while you sleep. |
| One action at a time | One page load per tool call. No scroll loops, no auto-paging, no fan-out. |
| Your own session, your own machine, your own IP | No cookie is exported to any third party. No proxy, no datacentre IP, no headless farm. |
| An ordinary browser, one flag | No stealth plugin, no user-agent or platform spoofing, no fingerprint patching, no proxy, no timing engineered to imitate a human. One Chromium flag is passed -- `--disable-blink-features=AutomationControlled`, which stops Blink setting `navigator.webdriver` -- because LinkedIn checks it at sign-in and refuses one without it. That is the whole of it, it is enforced at launch by `readonly.assert_launch_flags_permitted`, and `tests/test_launch_boundary.py` fails the build if a third flag appears. |
| Your data only | Your profile views, your applications, your saved jobs, your profile, your notifications. No enumerating or harvesting other members. |
| Reads, except for five named writes | Nothing is sent, posted, endorsed, invited or edited. Saving, unsaving, unfollowing, following and applying are the exceptions: off by default, one at a time, each one confirmed by you against a block built from a live read, with a token that works once and dies in two minutes. This row said "Reads only" until 2026-08-23 and the sentence is corrected rather than quietly widened. It then said "three named writes", listed only saving, unsaving and unfollowing, and opened with "Nothing is applied to" until 2026-08-31 -- corrected the same way, because by then applying and following both shipped and that clause denied one of them outright. |

**This lowers exposure. It does not eliminate it.** Automated access can still
result in a rate limit, a challenge, or account action, and that risk is yours
to accept. Decide that deliberately before you register the server.

### This is not an anti-detection tool, and here is the evidence rather than the assurance

The one Chromium flag above is the sort of thing that makes a repository *look*
like an evasion project. It is worth saying plainly what was measured, because
the claim is checkable and the reader should not have to take it on tone.

Audited 2026-08-24 across all 105 tracked files:

- **Fingerprint shaping: zero.** No user-agent, platform, locale, timezone,
  geolocation, viewport-spoofing, device-scale, WebGL or canvas patching; no
  `page.route` interception, no injected init script, no extra headers, no
  proxy. Each was searched for by name across the package and each returned
  **zero call sites**. One caveat so a reader who greps is not misled:
  `add_init_script` appears twice in `readonly.py`, both times as the
  *scanner's own pattern* for detecting such a call. The scanner names the
  things it forbids, which is why its source contains them and the rest of the
  package does not -- `partition_mutation_hits` confirms it independently, at
  zero unsanctioned. This audit was taken 2026-08-24, when the sanctioned side
  was one call. **Corrected 2026-09-04: the sanctioned side is now five** --
  four in `writes.perform` (`click`, `fill`, `select_option`,
  `set_input_files`) and one in `dom.activate_messaging_filter` (`click`),
  read off the live `readonly.SANCTIONED_MUTATIONS`. The unsanctioned count,
  the load-bearing half of this sentence, is unchanged at zero.
- **No stealth dependency.** Four dependencies, none of them an anti-detection
  library, and `readonly.scan_source_for_evasion` returns zero hits across the
  package -- its only hits anywhere are a deliberately planted control in a
  test.
- **Timing is fixed, not humanised.** Every delay is a constant. `import
  random` appears **0 times**. The 3-second gap between page loads is
  `MIN_INTERVAL - elapsed`, slept exactly -- machine-regular. Randomised jitter
  is what a tool imitating a human does; a flat interval is throttling.
- **The flag itself is bounded by a gate**, not by good intentions:
  `readonly.assert_launch_flags_permitted` runs at every launch and
  `tests/test_launch_boundary.py` fails the build if a third flag appears.

The flag stops Blink advertising `navigator.webdriver`, which LinkedIn checks
at sign-in and which makes an automated browser unusable for the account's own
owner. That is the whole of it. **Making an automated browser work and evading
detection are different activities, and only the first one is here.**

### The licence follows from that, and it is deliberately not permissive

This repository is **proprietary: all rights reserved, provided for reference,
with no permission to use, copy, modify or distribute it.**

That is not an oversight or a placeholder. This server drives an authenticated
LinkedIn session under a User Agreement that prohibits automation. A permissive
licence would invite strangers to point it at their own accounts -- or at other
people's -- with the author's name on the repository that told them how.

**It is a portfolio artifact. It is meant to be read, not deployed.** Read the
design, the boundary, the gates and the audit trail; that is what it is for.

---

## What it can do

All twenty-one reads are here. This table listed FOURTEEN of them until
2026-08-31, and it is completed rather than quietly left disagreeing with the
count at the top of this file; the five it omitted were `linkedin_login`,
`linkedin_draft_applications`, `linkedin_new_messages`,
`linkedin_open_messaging` and `linkedin_surface_census`. It also led with
`linkedin_login_browser`, which is the deprecated alias, so the canonical name
now leads and the alias is labelled as one.

The twentieth, `linkedin_profile_editor_fields`, was added later the same day
and the count above moved with it in the same edit -- which is the whole
discipline this paragraph exists to record. A row added without the count
moved is how this table came to be five short.

The twenty-first, `linkedin_my_activity_items`, arrived after that, on the
same day again, and its row and the count moved in one edit for the same
reason.

**AND THE DISCIPLINE THOSE TWO PARAGRAPHS RECORD HAS SINCE LAPSED, MEASURED
2026-09-05.** `linkedin_search_appearances` has a row above and this count did
NOT move to twenty-two, because moving it to twenty-two would make it wrong in
a new way. Counted off the live registry rather than off this page: the server
registers 37 tools and this table names 27 of them, so **ten registered tools
have no row here** -- `linkedin_comment_on_item`, `linkedin_compose_fields`,
`linkedin_connections`, `linkedin_profile_editor_values`,
`linkedin_publish_post`, `linkedin_react_to_item`, `linkedin_send_invitation`,
`linkedin_send_message`, `linkedin_update_profile_field`, and this wave's own
until the row above was written. Several are writes and are described
elsewhere in this file; that is a reason some of them are absent, not a reason
the number twenty-one is right.

So the honest state is: the sentence "All twenty-one reads are here" is the
same defect its own two paragraphs were written about, and it is recorded here
rather than patched, because fixing it means auditing which of the ten belong
in THIS table and which are documented in the write sections -- a different
job from adding one row, and one that should be done by somebody who reads the
whole file rather than as a side effect of a wave that touched one tool.

| Tool | Reads |
|---|---|
| `linkedin_who_viewed_me` | Who viewed your profile. Where the account has Premium Career this reaches back 365 days -- the highest-intent signal in a job search. |
| `linkedin_search_appearances` | **The reciprocal of the row above** -- that one reads the receiving end of a profile view, this one the receiving end of a SEARCH: how often other people's searches put you in front of them. Your own analytics, no argument, and the address carries no member segment so it can only ever resolve to whoever is signed in. **It is the only tool here whose page nobody had opened when it shipped**, and its docstring says so rather than letting you find out: the parser was built against a fixture that is SYNTHETIC and labelled so, which proves the tool refuses to publish the third parties put in front of it and proves nothing about whether it reads the real surface. Past the first two number-and-caption pairs the caption is withheld INSIDE the page and never reaches the process -- LinkedIn's breakdown panels describe the SEARCHERS, in exactly the shape a headline metric has, and those are other people's employers and titles. `anchors.person` is a COUNT of member links and is the field worth reading first: non-zero means LinkedIn's record of a search names the people in it. **A zero settles less than it looks like** -- zero appearances is equally consistent with "searches leave no record" and "nobody searched for you this week", and this tool cannot separate them; `headline: null` means no metric was found at all, which is a different answer again. |
| `linkedin_my_applications` | Jobs you applied to, with the status LinkedIn shows. |
| `linkedin_draft_applications` | The applications you STARTED and never sent -- the tracker tab LinkedIn labels "In Progress" and addresses as `?stage=draft`, with title, company, location, how long ago, and the job id. A draft is not a stalled application: nothing went anywhere, so an empty list here is not evidence about anything you did send. It reads the list and nothing else -- the row's own Delete control, and the discard dialog behind it, are never pressed from here. An empty result carries LinkedIn's own tab count, so "you have no drafts" and "this could not be read" are never the same answer. |
| `linkedin_saved_jobs` | Jobs you bookmarked. |
| `linkedin_search_jobs` | Job search with keywords, location, remote, date posted, experience level. |
| `linkedin_job_detail` | One posting in full -- pay range, LinkedIn's applicant count, workplace and employment type, hiring status, and the description. None of these is on a search or saved-jobs card. Also `apply_path`: which of the two apply routes this posting uses, and for the off-site route, whose applicant-tracking system it would send you to. |
| `linkedin_followed_companies` | The company Pages you follow, with the numeric id of each -- which is what `linkedin_unfollow_company` is addressed by. LinkedIn renders about twenty rows of however many you follow and offers no way to page through the rest, so this reports what it covered rather than implying it covered everything. |
| `linkedin_my_profile` | Your own profile: headline, about, skills, and which sections rendered. Experience/Education/Skills are deferred by LinkedIn until the page is scrolled, so they read UNKNOWN rather than zero. |
| `linkedin_notifications` | Your notification list, each row carrying `unread` as LinkedIn had it at the moment of reading. **Loading the page clears your unread badge** -- exactly as opening the page yourself would, and measured rather than theorised: one call on 2026-08-21 took the badge from 1 to 0 and it does not come back. It cannot be avoided, because LinkedIn marks the list seen on the server when it serves the page; no click, no scroll and no mark-as-read call is involved anywhere in this package, and the only way not to clear the badge is not to call this. The per-row flag is the one fact the page load destroys, which is why it is captured. |
| `linkedin_new_messages` | Whether anything has ARRIVED since you last opened Messaging, read off the badge in the feed's nav. One page, and it opens no conversation and never loads the messaging surface at all. **This is not an unread count**: LinkedIn's badge counts new-since-last-visit and resets when the Messaging tab is opened, so a 0 here means nothing has landed since your last look and never that your inbox is clear -- measured with a genuinely unread recruiter InMail on screen. A badge that did not render comes back null, which is not zero and is never reported as zero. |
| `linkedin_open_messaging` | Your conversations, each one's unread flag paired to its own row rather than reported as a count beside a list of names. **It opens a thread, and that is why the cost is in the name**: asking LinkedIn for the messaging surface does not stay on a list, it redirects into ONE conversation LinkedIn chooses, measured twice -- and opening the tab resets the new-since-last-visit badge that `linkedin_new_messages` reads. Whether opening marks that message read is an honest UNKNOWN after three attempts, because the only signal that would settle it requires performing the act being measured; if the sender has read receipts they may see one. The count is a floor, not a total. Correspondents' names are off by default and the thread identifier in the landed url is always redacted. `message_filter` activates one of seven named pills -- `inmail` among them, since those pills are buttons with no href and no url can reach them -- and anything outside that fixed set is refused, not clicked. |
| `linkedin_auth_status` | Whether there is a live session, measured by an authenticated request. |
| `linkedin_login` | Opens a browser window at LinkedIn's sign-in page for YOU to type into; nothing is automated and this server never sees, types, stores or transmits a password. The canonical name since 2026-08-25, matching `naukri_login`, `instahyre_login` and `uplers_login` in the same family. The window stays open until the identity endpoint confirms a real session, you close it, or the wait runs out -- a cookie appearing only causes the endpoint to be asked again, and a timeout reports authenticated false with a reason rather than an optimistic success. There is no reauth here and that is deliberate rather than missing: LinkedIn issues this server no refresh token, so a `linkedin_reauth` would be this tool under another name. |
| `linkedin_login_browser` | DEPRECATED ALIAS for `linkedin_login`, which it forwards to. Identical behaviour, and kept working because things already call it -- removing a name that used to work is the worse failure. There is no plan to remove it. |
| `linkedin_session_info` | Whether the session is live and **when it lapses**, read from the browser's own cookie jar. Reports the credential, the csrf cookie that supports it, durability, and why no silent reauth exists here. `renewal.session_lapses_at` is the date past which no renew can help and you sign in by hand -- the field to compare across servers, and on LinkedIn it equals the cookie's own expiry because nothing here can carry the session past it. |
| `linkedin_logout` | Ends the **local** sign-in by erasing this machine's cookie jar. The one destructive tool here: `confirm=False` (the default) performs nothing and previews what would go. Issues no request, so LinkedIn is never told. |
| `linkedin_cdp_status` | Recovery diagnostic: is there a Chrome this server could attach to? Touches nothing on LinkedIn. |
| `linkedin_server_info` | The boundary, the rate settings and the launch flags, without reading the source. |
| `linkedin_surface_census` | **An instrument for extending this server, not a job-search tool** -- its own docstring leads with that, and no answer about finding, comparing or tracking a job is in here. It measures what controls one page carries, so a capability this server has never built can be costed from what the page really holds instead of from a guessed selector found to be wrong at the moment it would fire. It takes a KEY and never a url, from a fixed set of five: `feed`, `profile`, `profile_edit_intro`, `settings`, `settings_dark_mode`. One page load, and it clicks nothing. It reports SHAPES and never names, so it identifies no member. Absent means UNKNOWN, never zero -- this server does not scroll, so a count describes the first render and nothing below the fold. A control being present is not evidence that using it is safe. Notifications, the network page and messaging are deliberately not offered: loading them costs a badge or opens somebody's conversation, and a census is not worth a side effect. |
| `linkedin_profile_editor_fields` | **The second instrument, and the one tool here that publishes control NAMES.** It names the controls inside the intro editor on your own profile -- which `linkedin_surface_census` will not do, because the census reports shapes and returns `<opaque>` for any name failing its length or character gate. That gate is what makes the census safe to point at a page full of strangers, and it is why `linkedin_update_profile_field` cannot name a field to type into. This tool relaxes it on ONE ground and establishes that ground per call: it loads `/in/me/`, requires LinkedIn's own `isSelfProfile=true` on the landed url, loads the intro editor, and requires the same member segment on both -- and if either half fails it returns a refusal carrying no field data at all, so a refusal can never be read as "there are none". The container is found structurally, as the nearest dialog ancestor of the control named Save, never by an index; two such controls or none is a refusal rather than a guess. It takes NO ARGUMENT, so no caller can aim it at another page. Two page loads, and it clicks nothing. **LABELS, NEVER VALUES** -- a label is "First name", a value is your first name, and no value and no href leaves the page. Your member slug is compared and discarded: it is in no part of the answer. |
| `linkedin_my_activity_items` | **The item keys, for your own posts only** -- which nothing else here returns, and which is why `linkedin_comment_on_item` and `linkedin_react_to_item` are registered and refusing: neither was ever blocked by the read boundary or by the click anchor, they simply had nothing to aim at. `linkedin_surface_census` cannot supply one by construction, since it substitutes every urn out before it counts, and the feed carries zero item permalinks. It reads `/in/me/` and takes NO ARGUMENT, so no caller can aim it at another page. **Authorship is established, not inferred from where an item sits**, and it takes all three of: LinkedIn's own `isSelfProfile=true` on the landed url; one single author name across every item overflow control on the page, so a rail carrying somebody else's item is refused outright; and that name standing in a prefix relation to the page's own `h1`. If any of the three fails there is no `items` key at all, so a refusal can never be read as "you have no posts". **No name ever leaves the page** -- the comparison happens inside the document and only booleans come back. A urn is published only if it matches the exact `urn:li:<type>:<digits>` shape and sits inside an item root that itself carries an overflow control; anything else is counted and dropped. **The output is real identifiers**: do not paste one into a tracked file in this repository, which is public and swept for exactly that shape. |

## The six that write

**This heading said "The three that write" over a three-row table until
2026-08-31**, stale by two: `linkedin_apply_job` shipped 2026-08-25 and
`linkedin_follow_company` 2026-08-30, and neither had been added here. It went
to five that day and to SIX later the same day, when `linkedin_update_setting`
became performable. The count is `len(writes.PERFORMABLE)` and it is pinned
against these tool names in `tests/test_server_surface.py`, so the table below
cannot fall behind the server again without that test failing.

| Tool | What it does |
|---|---|
| `linkedin_save_job` | Bookmarks one posting. Call it with no `confirm_token` and it performs nothing: it reads the posting and your saved list live and returns a block naming the job by title and employer, which way the toggle would move, where each fact came from, and how to undo it. Call it again with the token from that block to act. |
| `linkedin_unsave_job` | Same shape, same gates, and it **acts** -- since 2026-08-30, when the label its click anchors on was finally measured. It still refuses from any state it does not recognise, and its preview is currently blocked by a separate defect in the Saved-tab read. See below. |
| `linkedin_unfollow_company` | Stops following one company Page. Same shape and the same five gates. Addressed by the **numeric company id**, never by name -- names collide, change, and are not yours to rely on, and the click is anchored to the row carrying the id, so what you name and what gets pressed are the same row by construction. |
| `linkedin_apply_job` | Submits an application to one **LinkedIn-hosted** posting, since 2026-08-25. Same two-call gate plus a second one: the apply modal is re-read before the submit is pressed, and it is only pressed if exactly one control carries LinkedIn's own submit hook and zero advance controls are present. Off-site postings are reported, never driven. **This is the one write nobody has established LinkedIn can undo** -- the honest form is stronger than "this server cannot withdraw it". |
| `linkedin_follow_company` | Follows the company that posted one job, from the posting page itself, since 2026-08-30. Same shape and the same five gates; the direction is read off the posting at no extra page load. A follow **is** reversible on LinkedIn. This row used to end "but this server cannot aim the undo ... with nothing resolving one to the other", and since 2026-09-05 that is half wrong: `linkedin_job_detail` returns `company_id`, the employer's numeric Page id, read off the canned people-search link in LinkedIn's Premium insights panel on the same posting. So the undo can be aimed from the posting you followed from -- **when that panel renders.** It is Premium and LinkedIn draws it for some employers and not others, so `company_id.state` is often `absent`, and `reversible_by` on the preview is still written against the weaker fact. |

| `linkedin_update_setting` | Changes ONE named account setting -- dark mode, and nothing else -- since 2026-08-31. The first write here that touches neither a job nor a company Page. Same two-call gate; the destination is NAMED rather than derived, because the setting has three states and no direction can be inferred from two, and the token binds to the destination as well as the setting. The control clicked is the radio named for where you are going, and the SELECTOR IS BUILT FROM THE ROLE THAT CONTROL ACTUALLY CARRIES rather than an assumed one. Verified by a fresh navigation and a re-read of the whole group's own `checked` property, which is the strongest verification in this package. **It is also the cheapest write here**: dark mode is a per-account display preference with no audience, observable by nobody, and the same tool sets it back. Asking about any other setting loads NOTHING. |

**Seven more tools are write-shaped and cannot act at all**: `publish_post`,
`comment_on_item`, `react_to_item`, `update_profile_field`,
`set_open_to_work`, `send_invitation` and `send_message`. Each holds a full spec and reads its own
surface live when previewed, then refuses with what it just saw and the one
measurement that would complete it. None is in `writes.PERFORMABLE`, none
holds a `url_template`, and `writes.mint` refuses each of them a grant at
issue -- so no confirm token for any of them can exist. They are on the
surface because a tool that names its own missing measurement is correctable
and a silence is not.

After the click, the result is confirmed from a **different surface** -- your
saved list, with LinkedIn's own per-tab count -- rather than from the button
that was just pressed. `performed` comes back `true`, `false`, or `"unknown"`.
On `"unknown"`, do not retry: a retry on a toggle that did land performs the
opposite action.

### The one that refused, and how it stopped

**This section described a permanent-looking refusal for a month. It is kept as
the worked example, because how it ended is more useful than that it ended.**

LinkedIn identifies the save control by its accessible name. Every capture this
repo holds -- four postings, both hydration states, two different days -- shows
`aria-label="Save the job"`, the **unsaved** state. The name it wears when a
posting **is** saved had never been observed, and it could not be observed by
reading: there was nothing saved on the account to observe it on. So
`linkedin_unsave_job` had no anchor, and this server would not guess one --
`"Saved"` and `"Unsave the job"` were both plausible and it had seen neither.

That was circular: the only way to see the label was to perform the action its
inverse gated.

**What broke it, on 2026-08-30.** The operator authorised a save. `perform`
read back the label the control changed into and reported `"Unsave the job"`.
The prediction held exactly -- one row of a table, not a missing code path.

**And one reading was not enough to write it down.** A label reached by
performing its own inverse can only be re-measured by performing it again,
which makes it a measurement nobody can afford to check. So the row waited for
a **read-only route**: `linkedin_job_detail` now reports `save_state` off the
control on a posting it has already loaded, for no write and no extra page
load. Three further readings through it agreed with the first. The row went in
on four observations across two independent routes.

**Which label it was mattered too.** `"Unsave the job"` names its own inverse;
the measured OFF row establishes that this control is named for the ACTION it
performs, not the state it is in. `"Saved"` would have been ambiguous between
the two readings, and a label mapped to the wrong state points a click at the
opposite action. Had the measurement come back `"Saved"`, the row would still
be missing.

**What still refuses.** The refusal narrowed rather than disappearing:
`unsave_job` acts only from a state it recognises. And it is not yet reachable
end to end -- its preview takes its direction from your Saved tab, and that
list currently cannot be read (the rows draw; the harvest returns none of
them). The capability is real; the route to it runs through a broken read.

**The general form**, which is the reason this section survives: when a
measurement can only be bought with an irreversible act, the next thing to
build is not the row -- it is the cheap way to take that measurement again.

### Applying: the half that ships, and the half that does not

**`linkedin_job_detail` tells you how a posting is applied to.** LinkedIn draws
the apply control as a link rather than a button, so its destination is legible
without touching it, and `apply_path` reports one of three answers:

- `linkedin_apply` -- the application is filled in and submitted on LinkedIn.
- `offsite` -- LinkedIn hands you to the employer's own applicant-tracking
  system. The destination is decoded out of LinkedIn's outbound wrapper **by
  string alone**: no redirect is followed and no third-party host is contacted.
  You get the host, so you know whose form you are about to fill in.
- `unknown` -- it would not say. This is a real answer and it is the important
  one; see below.

That is the useful half, it costs no extra page load, and it is a pure read.

**It does not submit.** Not because applying is beneath this server's remit,
but for reasons that were measured:

1. **The apply FLOW has never been captured.** Across thirteen job captures
   there are zero forms, zero file inputs, zero dialogs, zero screening
   questions and zero controls that submit anything. Nothing here has seen what
   would be filled in or pressed. This is the same standard `unsave_job` is
   held to, applied to the action that deserves it most.
2. **An application cannot be undone from here**, at any confirm level, in any
   circumstances. Withdrawing is permanently forbidden.
3. **The off-site half is not this server's to do at all**, however good a
   capture got. Driving somebody else's form, on somebody else's domain, under
   their terms, is a different piece of software.

`apply_job` is therefore fully specced and gated in `writes.py`, registers no
tool, and holds no url, so a grant for it is refused at issue rather than at
use.

**And the gap has an address, which is what makes it unmeasured rather than
permanent.** `scripts/_probe_apply_flow.py` captures the LinkedIn-hosted flow
and inventories exactly the controls every existing capture lacks -- forms,
file inputs, dialogs, screening questions, the control that submits. It reaches
the flow by **navigation, not by a click** (LinkedIn draws the apply control as
a link), the package's own mutation scanner finds **zero** mutating calls in
it, and it takes the job id as a required argument so no default picks a
posting for you. It also reads LinkedIn's own applied-tab count **before and
after**, because opening an Easy Apply flow may create a draft -- a hypothesis
nobody has verified, labelled as one, and measured rather than assumed.

**It has not been run.** Run it with somebody watching, on a posting whose
`apply_path` reads `linkedin_apply`.

**Why the classifier demands several fields agree**, when one obvious field
looks sufficient. Each candidate was measured and each fails alone:
`data-view-name="job-apply-button"` is present on one capture in thirteen and
absent from a fully hydrated off-site posting, so its absence carries no
information at all. The outbound wrapper is generic -- one capture holds two of
them and only one is the apply control. The accessible name is the strongest
single field and is the one LinkedIn has already changed: **the string "Easy
Apply" appears in zero accessible names**, and twice in prose on the same page,
so a parser keyed on the name everybody knows the feature by matches nothing.
And the pre-hydration payload is worse than useless -- an off-site posting was
measured carrying the on-site flow's own marker, for the same job id, because
LinkedIn ships the whole apply state machine as a per-posting template.

## What it deliberately cannot do

**THIS SECTION WAS REWRITTEN ON 2026-08-31 RATHER THAN PATCHED, and the reason
is worth the two lines.** It listed *following a company* and *submitting
applications* among the things this server deliberately cannot do, while both
had shipped -- one six days earlier, one the day before -- and it said a follow
"is still not performable" three paragraphs after a table row describing it
performing. Patching individual sentences in a section whose premise has moved
produces a section that contradicts itself in more places, which is what the
last three attempts at it did. What follows is organised by WHY a thing is
refused, because that is the axis that actually predicts whether it will ever
change.

**Sending a message or an InMail. Publishing a post. Commenting. Reacting.
Editing a profile field.** This paragraph described all five as registered,
specced and refusing, blocked by the same measured thing -- that they would
have to TYPE, and no typing kind was sanctioned anywhere in this package --
and **that stopped being true on 2026-09-01.** It is corrected in place
rather than deleted, because the section it sits in is organised by WHY a
thing is refused, and this paragraph is now the record of a refusal that
ENDED rather than a live example of one.

`fill` was sanctioned inside `writes.perform` on 2026-09-01, and
`select_option` on 2026-09-02. **All five of these now perform, behind the
same two-call token gate as every other write in this package** -- verified
2026-09-04 against the live `writes.PERFORMABLE`, which carries
`send_message`, `publish_post`, `comment_on_item`, `react_to_item` and
`update_profile_field` alongside the rest. None of the five was handed a new
refusal to replace the old one: the sentence this paragraph used to close
on -- "`perform` may CLICK -- that is one entry ... and it may do nothing
else" -- is false in both halves now. `perform` may CLICK, FILL and SELECT,
three entries and not one, and "no measurement and no url admits any of
these five" does not hold for a single one of the five any more.

**Endorsing a skill is IMPOSSIBLE rather than refused**, and it is the only one
of these where the refusal is on somebody else's behalf. The control exists
only on a third party's profile, and `linkedin_who_viewed_me` reads the
RECEIVING end of exactly that signal: loading a stranger's profile leaves them
a durable record, 365 days deep. That cost lands on a person who did not agree
to it, so it is not the operator's to clear.

**Sending a connection invitation is refused on something narrower than a
boundary.** The route costs no badge -- the invitation controls are on his own
profile -- and the aiming works: a word he supplies is handed INTO the page,
the comparison happens there, and three integers come back, with exactly one
match aimable and two or more refused as ambiguous. What stops it is that **the
confirm block cannot name the person.** The aiming is safe precisely because no
label enters this process, so the block can say "one of nine controls carries
your word, at position three" and cannot say who. Every other write here names
its target in terms you can check.

**Marking notifications read** is not offered, and the honest form is that
there is no way to avoid it rather than that it is refused: LinkedIn marks the
list seen on the server when the page is served. See the side effects below.

**Open To Work** has no url at all -- re-measured 2026-08-31, its control is a
button with no href -- so its editor opens as a modal, and the single click
that would first SHOW it is also the first click that could CHANGE it. It is
the one setting here a current employer can see.

**Collecting data about other members** is out of scope by construction rather
than by policy. `linkedin_surface_census` reduces every accessible name and
every href to a SHAPE before counting, so a row identifies a kind of control
and never a person, and a shape seen exactly once has any run of capitalised
words blanked.

**Reading your own inbox is neither refused nor unmeasured any more**, and this
paragraph said it was both. The boundary was narrowed on 2026-08-26 on the
operator's ruling and `linkedin_open_messaging` and `linkedin_new_messages`
ship. The hypothesis the old text called unverified has been MEASURED, twice,
and it was right: `/messaging/` does not stay on a list -- LinkedIn redirects
it into one conversation of its own choosing, so the load opens somebody's
thread and resets the nav badge. That cost is now stated in the tools' own
names and docstrings rather than denied by a list that could not enforce it.
`/messaging/compose` stayed forbidden through that narrowing and is admitted
today as ONE exact url, by an exemption, for a capture that has not been taken.

Anything else that would change something on LinkedIn's servers is out of
scope, and `tests/test_readonly.py` fails the build if a mutating call appears
anywhere in the package outside the entries `SANCTIONED_MUTATIONS` names --
five of them, read off the live module 2026-09-04. This line said "two" and
is corrected in place rather than left carrying a bare number that goes stale
at the next widening.

One tool changes something on **this machine**: `linkedin_logout(confirm=True)`
erases the local cookie jar. It issues no request, so LinkedIn is never told,
and `linkedin_server_info` names it under `local_state_writes` rather than
folding it into the `read_only` field.

### The side effects, stated rather than hidden

**This heading said "The two side effects" over a list that had grown**, which
is the same rot as the write count and is worth naming rather than silently
renumbering. A read that changes something has to say so:

1. **Opening the notifications page clears LinkedIn's unread badge** -- exactly
   as it would if you opened the page yourself. Measured, not theorised: one
   call on 2026-08-21 took the badge from 1 to 0, and it does not come back.
   It cannot be avoided: LinkedIn marks the list seen on the server when the
   page is served, so there is no read of this surface that leaves the badge
   alone. No click, no scroll and no per-item open is involved, and there is no
   mark-as-read call anywhere in the package. **The only way not to clear the
   badge is not to call `linkedin_notifications`.** Since the badge is going
   either way, each row carries `unread` as LinkedIn had it at the moment of
   reading -- the one fact the page load destroys.
2. **Running a job search adds to your own recent-search history**, the same as
   typing the query on the site.
3. **Opening messaging clears the messaging badge AND opens one conversation
   LinkedIn chooses** -- measured twice. `/messaging/` does not stay on a
   list. Only `linkedin_open_messaging` and `linkedin_new_messages` can incur
   this, and only when called; `linkedin_send_message` deliberately does not
   open messaging at all -- it reads the nav badge off a page already loaded,
   and refuses.
4. **Three census surfaces may cost something merely by being opened**, and
   each returns a `cost` field saying what. The two publishing composers can
   autosave a draft this server has NO REACHABLE SURFACE to detect -- 17
   candidate draft addresses were run against the read boundary and all 17
   were refused -- and the message composer is on the surface point 3
   describes. Every other census key still renders state and leaves nothing.

Each is disclosed in the tool docstrings and in `linkedin_server_info`.

**THERE IS NO COUNT IN THAT SENTENCE AND THAT IS DELIBERATE.** It said "both"
over a list of two, then stayed "both" while the list grew, then said "all
four" for about an hour. A count in prose beside a list is a second
enumeration of the same thing and it goes stale the moment somebody adds to
the list without reading the paragraph above it -- which is exactly how the
write count in this file was wrong four times. The list is the enumeration;
`known_side_effects` in `linkedin_server_info` is the machine-readable one,
and `tests/test_server_surface.py` is what pins the numbers that ARE
countable.

---

## Setup

```bash
cd D:\workspace\projects\job-hunting\mcp-servers\linkedin
pip install -r requirements.txt
playwright install chromium
python -m pytest            # 2304 passed
```

Then, once the server is registered with a client, **call `linkedin_login_browser`
first.** A window opens at linkedin.com/login. Sign in there yourself -- this
server never sees, types, stores or transmits a password. The persistent Chrome
profile keeps the session afterwards, so this is a one-time step until LinkedIn
expires it.

Confirm with `linkedin_auth_status` before trusting any read.

### Registering it

stdio transport, entry point `linkedin.py`:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "python",
      "args": ["D:\\workspace\\projects\\job-hunting\\mcp-servers\\linkedin\\linkedin.py"]
    }
  }
}
```

---

## How "read-only" is enforced rather than asserted

`linkedin_server/readonly.py` holds four mechanisms, and the tests show
each of them **failing on a planted violation** before trusting it on the real
package. A check that cannot fail certifies nothing.

1. **A navigation allowlist.** `assert_read_url` is the only door to
   `page.goto`. Every permitted url is an anchored pattern; a keyword you type
   cannot become a navigation to an action url. Blocked targets include
   `/jobs/application/`, `/messaging/`, invitations, `/edit/`, `open-to-work`,
   anything with `action=`, and every host that is not `www.linkedin.com`.
   The job-posting pattern is the tightest on the list: it admits a numeric
   id and **no query string at all**, because the url is built from an integer
   and so never has one to preserve. The slug form LinkedIn also serves
   (`/jobs/view/senior-node-engineer-at-acme-4600000042`) is refused for the
   same reason -- a slug is a job title, and a title is a string.

2. **A source scanner.** The package is grepped for calls that could change
   state -- `click`, `fill`, `type`, `press`, `select_option`, `set_input_files`,
   form submission, and any non-GET request. **This said "exactly one" until
   2026-09-04** -- and the verb list two lines up had already named
   `set_input_files` before that correction, so this paragraph had been
   internally inconsistent with itself since before today. It finds **five**,
   read off the live `readonly.SANCTIONED_MUTATIONS`: four inside
   `writes.perform` (`click`, `fill`, `select_option`, `set_input_files`) and
   one click in `dom.activate_messaging_filter`.

   The scanner was **not** relaxed to accommodate any of them. It still
   reports every mutating call unconditionally, and what admits these five is
   a separate one-line allowlist, `readonly.SANCTIONED_MUTATIONS`, keyed on
   `(path, function, kind)`. **Six near-misses are shown failing, not five**
   -- corrected 2026-09-04, counted directly off
   `tests/test_readonly.py::test_the_exception_does_not_widen`: the
   sanctioned click in the wrong FILE (`dom.py`), the sanctioned kind in the
   wrong FUNCTION of `writes.py`, two wrong KINDS inside `perform` itself
   (`page.type` and `page.press` -- a `fill` inside `perform` stopped being
   one of these on 2026-09-01, when it was sanctioned and the test case was
   re-aimed from `page.fill` to `page.type` rather than deleted), a click
   buried in a closure one scope down (attribution is to the innermost
   enclosing function, so the closure is named as itself and inherits
   nothing), and a click at module level with no enclosing function at all.
   The package is separately asserted to contain exactly as many mutating
   calls as the list has entries, which is what catches a *second* click
   inside `perform` that the triple alone cannot distinguish from the first.

   **The fifth kind, `set_input_files`, is bounded by `linkedin_server/uploads.py`
   rather than by this allowlist** -- a declared root, a refusal on any
   symlink in the chain, a regular-file check, and a digest read at preview
   and re-read before the browser is handed the file; the allowlist controls
   the WIDTH of the opening, the guard controls what comes through it.

   `evaluate` is flagged too: the three read-only DOM harvesters waive it with a
   trailing `# readonly-ok`, so any new `evaluate` fails the build until somebody
   waives it in a reviewable diff.

3. **A tool-surface check.** No tool name contains a write verb, and no tool
   docstring makes an affirmative write claim. Docstrings may still say what a
   tool *cannot* do -- "has no way to add or remove anything" is the sentence a
   read-only tool should contain, so the check looks for negation rather than
   banning the words.

4. **A launch boundary.** `assert_launch_flags_permitted` refuses any Chromium
   flag outside the two sanctioned ones, and refuses
   `--disable-blink-features` carrying any value but `AutomationControlled` --
   that flag can switch off arbitrary Blink behaviour, so permitting the name
   is not enough. `browser.py` runs it **before every launch**, so it binds at
   runtime and not only in CI. A companion scanner rejects an anti-detection
   library arriving as a dependency (`playwright_stealth`,
   `undetected_chromedriver`, captcha solvers, TLS-spoofing clients), matched
   on import lines only so this file can go on describing the boundary in
   prose.

The injected scripts are scanned separately for anything that could mutate the
page (`.click(`, `.value =`, `dispatchEvent`, `fetch(`, ...). They query the
DOM and read text.

That scan is bound to **what actually runs**, not to what is named a certain
way. The tests parse the package, find the first argument of every
`page.evaluate(...)` call, resolve it to its module-level constant and scan
that -- so a script cannot be injected without being read, and one this check
cannot resolve (assembled at runtime, say) fails the build outright. The
earlier version scanned a hand-written list of three names ending in `_JS`; a
cold review put a constant called `EVIL_INLINE`, carrying `localStorage.setItem`
and `fetch(`, through the existing call site and shipped it with every test
green. That hole is closed, and the attack is now a test.

## The login gate: a cookie is never a login

A sibling server shipped the opposite of this the day before this one was
built: it reported success the moment a session cookie appeared. LinkedIn hands
cookies to signed-out visitors too, so that success meant nothing.

Here, the verdict comes from `GET /voyager/api/me` -- the identity call
LinkedIn's own web app makes on page load. A `li_at` cookie appearing is only
ever a reason to **ask** the endpoint again.

Three outcomes are reported, not two:

- `authenticated: true` -- the endpoint returned an identity.
- `authenticated: false` -- the endpoint refused, or the feed redirected to the
  signed-out wall.
- `authenticated: null` -- neither could be established. **Unknown does not
  collapse into "signed out"**, or the server would tell you to sign in again
  while your session was perfectly fine.

Corroboration can only ever turn an unknown into a `false`. It is never allowed
to manufacture a `true` on weaker evidence.

Cookie **values** are credentials: they are never logged, never persisted by
this server, and never appear in a tool result. Only their presence is
reported, and two tests assert that.

## Signing in, and how long it lasts

**Call `linkedin_login_browser`.** A Chrome window opens at LinkedIn's sign-in
page and you type into it. This server never sees, types, stores or transmits
a password -- there is no code path that could. The window stays open until the
identity endpoint confirms a real session, you close it, or `wait_seconds`
elapses (300 by default; pass a larger number if you need longer).

**It is a one-time step, not a per-session one.** The session lives in an
on-disk Chrome profile under `_state/chrome-profile/`, so it survives:

| Event | Session survives? | Why |
|---|---|---|
| This server restarting | Yes | The session is on disk, not in the process. |
| The machine rebooting | Yes | Same. |
| The profile directory being deleted | No | That directory *is* the session. |
| Signing out inside the window | No | LinkedIn revokes it. |
| LinkedIn expiring the cookie | No | See below. |

**How long LinkedIn gives you.** `linkedin_session_info` reports the `li_at`
cookie's expiry date and the days remaining, read live from the browser's own
cookie jar -- so you never have to guess, and it is a measurement rather than a
claim in a README. For calibration, LinkedIn's own long-lived cookies in this
profile (`bcookie`, `bscookie`) were issued with a **365-day** expiry. The
`li_at` figure is the one that governs the login, and only a real sign-in can
produce it.

Cookie **values** are credentials: never logged, never persisted by this
server, never in a tool result. Only the name, the presence and the expiry.

**When it lapses**, every read tool says so -- `{"error": "not_authenticated",
"message": "..."}` naming `linkedin_login_browser` as the way back. It never
returns an empty list instead; an empty list from an expired session is
indistinguishable from an empty list because you genuinely have none.

### The cold start, and the trap in it

`li_at` is a **persistent** cookie. `JSESSIONID` -- which LinkedIn's own web app
copies into the `csrf-token` header, and without which the identity endpoint
will not answer an authenticated request -- is a **session** cookie
(`is_persistent=0` in this profile's cookie store). So every time the browser
starts, the jar holds a perfectly good login and no csrf token.

A server that asked the identity endpoint straight away would send a request
with no token, be refused, and tell you to sign in again while your session was
fine. So on a cold jar `check_auth` loads one LinkedIn page first, which makes
LinkedIn issue the cookie, and only then asks. That load doubles as the
corroborating read, so it costs no extra request.

## The recovery path: attaching to your own Chrome

**Not the daily path.** The persistent profile above is the answer; this is the
fallback for the day that profile's session dies and a fresh sign-in is being
refused. Enable it with `LINKEDIN_CDP_ATTACH=1` and this server launches
nothing -- it attaches over CDP to a Chrome **you** started.

Two things silently defeat this, both measured on this machine:

1. **A Chrome opened from the taskbar has no DevTools port.** "My browser is
   open" is not enough; it has to have been started with
   `--remote-debugging-port`.
2. **Chrome's singleton eats the flag.** If any Chrome is already running,
   starting a second one with the flag hands the arguments to the first and
   exits -- no port, no error, exit code zero.

So either quit Chrome completely first (windows *and* the background instance),
which keeps your real profile and therefore your real LinkedIn session:

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9224
```

or give it a profile of its own, which works alongside your running Chrome but
is signed into nothing, so you sign in to LinkedIn once inside that window:

```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9224 --user-data-dir="%LOCALAPPDATA%\linkedin-cdp"
```

Confirm it worked by opening `http://127.0.0.1:9224/json/version` -- JSON means
the port is live. Or call `linkedin_cdp_status`, which probes it for you and
reports the command when nothing answers. The address is `127.0.0.1` and not
`localhost`: Chrome binds the port on IPv4 only, so the name resolves to `[::1]`
first and eats a timeout (measured at 2085 ms against 35 ms).

Port **9224**, deliberately not the sibling Naukri server's 9223.

In attach mode this server takes **no profile lock** (it owns no profile), works
in **a tab of its own** rather than driving one of yours, and on teardown
**disconnects without closing your browser** -- Playwright's `close()` on a CDP
connection only drops the client, which was measured against a real Chrome
before it was relied on. The read-only allowlist is identical in both modes.

## Rate discipline

- A flat **3-second minimum between page loads**, enforced globally. Throttling,
  not disguise: it is deliberately not jittered to resemble anything.
- **One page load per tool call.** The only exception is
  `linkedin_my_profile(include_skills=True)`, which loads a second page and
  reports `pages_loaded: 2`.
- **No auto-paging.** Ask for the next page of a search deliberately with
  `start=25`. Every list result carries `capped`, `page_had` and `limit`, so
  "25 results" is never mistaken for "25 results exist".
- **One call at a time**, serialised in-process; **one process at a time**,
  serialised by a cross-process lock on the Chrome profile. Two processes on one
  Chromium user-data dir corrupt it and your session is gone -- that cost a
  sibling server 37 minutes.
- **The window does not linger.** The browser closes after 5 idle minutes and
  releases the lock.

## When something cannot be read

The server raises instead of returning an empty list. An empty list from a page
that failed to render is indistinguishable from an empty list because you
genuinely have none, and those two must never be confusable. A failed read comes
back as `{"error": "extraction_failed", "url": ..., "hint": ...}` so you can open
the same page yourself and see what it saw.

The one exception is `linkedin_search_jobs`, where zero results is a real
answer; it returns `results: []` with a `note`.

## How the pages are read

LinkedIn's class names are generated and its GraphQL query ids rotate with every
deploy, so both make brittle anchors. What does not rotate is the shape of a
link: a person is behind `/in/<slug>`, a job is behind `/jobs/view/<id>`. Every
list surface is harvested by finding those links and reading the text of the
card around them, then parsed by pure functions in `shape.py` -- which is why
the parsing is tested without a browser, a network or an account.

Notifications is the one surface with no dependable per-item link, so it is
anchored on structure instead. It is the most likely to need updating, and it
raises rather than returning an empty list when it misses.

## Layout

```
linkedin.py              entry point (stdio)
linkedin_server/
  config.py                  paths, timeouts, caps, the rate floor,
                             the two launch flags
  readonly.py                the allowlist, the scanners, the verb list,
                             the launch boundary
  profile_lock.py            cross-process lock on the Chrome profile
  browser.py                 persistent context, single-flight, idle close
  auth.py                    the login gate, session lifetime, cold start
  cdp_bridge.py              the recovery path: attach to a running Chrome
  dom.py                     the read-only harvesters and the control readers
  shape.py                   pure parsers and the result envelope
  server.py                  the thirty-three tools
  errors.py
tests/                       1393 tests, no network, no account
  fixtures/                  frozen LinkedIn markup, scrubbed
```

## Status

Built and tested: **1393 tests**, no network and no account. Most run with no
browser at all; the fixture-driven modules launch a local headless Chromium to
run the real readers over frozen markup, which reaches nothing outside the
machine.

These counts are the ones this file has most often had wrong. They said 986 for
three waves after the suite passed a thousand, which is harmless on its own and
is the same habit that let four documents go on saying this server could not
write. They are re-measured at each wave now rather than carried forward.

**First live run: 2026-08-21.** Sign-in succeeded and the session persisted,
so the flag above is now **verified sufficient** on this machine, and
`/voyager/api/me` and the `li_at` lifetime (365 days) are confirmed. Every
read tool was then run once against the real account. Four of the eleven
worked; the sweep is written up in
`../_audit/2026-08-21-linkedin-parse-fix.md`, and this is what it found.

`linkedin_who_viewed_me` **was returning names that were not names.** Every
row carried the page heading, "Who's viewed your profile", attached to a real
person's profile link -- four rows, one repeated name, all four links
genuine. It was fixed the same day: the row boundary no longer depends on an
attribute LinkedIn attaches after hydration, privacy-limited viewers are no
longer silently dropped (they were six of ten), and the timestamps are read.
Verified live: 10 rows, 10 distinct names, none missing a field.

**Second pass, 2026-08-22.** The three surfaces that pass left broken were
repaired and verified live. All four defects had the same shape: a reader
anchored on markup LinkedIn no longer emits, or on markup whose presence
depends on how far the page had rendered.

| tool | was | now |
|---|---|---|
| `linkedin_my_profile` | errored: no name could be read | reads name, headline, location, About and photo from a page with **zero** `h1`. A section is now the largest ancestor of its heading holding exactly ONE heading -- the same rule the row walk uses -- which gives identical output pre- and post-hydration. Verified live. |
| `linkedin_saved_jobs`, `linkedin_my_applications` | errored on a redirect | read `/jobs-tracker/?stage=saved` and `?stage=applied`. Both lists are genuinely empty, and an empty result now says so **explicitly**, with LinkedIn's own tab count and the empty-state wording. A zero the page does not corroborate is still an error. Verified live. |
| `linkedin_notifications` | rows, with noise | screen-reader text is subtracted by count rather than by phrase, and `when` comes from the card's own time element. Each row also carries `unread` as it stood when read. Verified against a frozen capture of the live page. |
| skills, inside `my_profile` | returned `All`, `Industry Knowledge`, `Tools & Technologies` | returns the real list -- 20 skills on the live account -- keyed on the only per-skill anchor the page offers. |

One thing the profile reader will not do: **Experience, Education and Skills
are not on the profile page at all.** LinkedIn defers them until it is
scrolled, and this server does not scroll. They are reported as UNKNOWN, never
as zero, and `details_urls` gives you the page for each.

**Third pass, 2026-08-22.** `linkedin_search_jobs` was the last broken tool.
On a row for a verified employer LinkedIn adds a screen-reader line reading
"<title> with verification"; read positionally, that line became the `company`
and pushed the real company down into `location` -- 5 of 14 rows across two
live searches.

The fix is not a rule about that string. Fields are no longer read as "line 1,
line 2, line 3", because any line LinkedIn inserts shifts every field after
it, and the same two pages carried "Promoted", "Apply", "Viewed", "Actively
reviewing applicants", a salary chip and an alumni line. Each field is now
anchored on the thing that IDENTIFIES it: the **title** on the text of the
link that makes the row a job row, with the page's own screen-reader copies
subtracted by count; the **company** on the accessible name LinkedIn gives the
employer's logo, which is an image and so cannot be moved by a line; the
**location** on the metadata list inside the entity lockup, where the lockup
is found without any class name as the smallest ancestor of the link that also
holds that logo. A surface offering none of those -- the job tracker offers
none -- falls back to reading lines in order, as before.

Verified live on the same query: 7 of 7 rows agree with LinkedIn's own
`artdeco-entity-lockup` elements, which the fix deliberately does not use, and
3 of those 7 carried the verification decoration. The tests inject a
decoration LinkedIn has **not** shipped at every position in every frozen row
and require the answer not to move, with a control that shows the same
injection breaking the fields once the anchors are taken away.
