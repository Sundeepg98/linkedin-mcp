# linkedin

An MCP server that shows you your own LinkedIn account data as structured tool
results instead of pages you have to click through.

**Fourteen of its seventeen tools read and change nothing. Three write.**

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
- `linkedin_unsave_job` is built, gated and **refuses to act**. See
  [The one that refuses](#the-one-that-refuses).
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
| Reads, except for three named writes | Nothing is applied to, sent, posted, endorsed, invited or edited. Saving, unsaving and unfollowing are the exceptions: off by default, one at a time, each one confirmed by you against a block built from a live read, with a token that works once and dies in two minutes. This row said "Reads only" until 2026-08-23 and the sentence is corrected rather than quietly widened. |

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
  one sanctioned mutating call and zero unsanctioned.
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

| Tool | Reads |
|---|---|
| `linkedin_who_viewed_me` | Who viewed your profile. Where the account has Premium Career, this reaches back 365 days -- the highest-intent signal in a job search. |
| `linkedin_my_applications` | Jobs you applied to, with the status LinkedIn shows. |
| `linkedin_saved_jobs` | Jobs you bookmarked. |
| `linkedin_search_jobs` | Job search with keywords, location, remote, date posted, experience level. |
| `linkedin_job_detail` | One posting in full -- pay range, LinkedIn's applicant count, workplace and employment type, hiring status, and the description. None of these is on a search or saved-jobs card. Also `apply_path`: which of the two apply routes this posting uses, and for the off-site route, whose applicant-tracking system it would send you to. |
| `linkedin_followed_companies` | The company Pages you follow, with the numeric id of each -- which is what `linkedin_unfollow_company` is addressed by. LinkedIn renders about twenty rows of however many you follow and offers no way to page through the rest, so this reports what it covered rather than implying it covered everything. |
| `linkedin_my_profile` | Your own profile: headline, about, skills, and which sections rendered. Experience/Education/Skills are deferred by LinkedIn until the page is scrolled, so they read UNKNOWN rather than zero. |
| `linkedin_notifications` | Your notification list. |
| `linkedin_auth_status` | Whether there is a live session, measured by an authenticated request. |
| `linkedin_login_browser` | Opens a window for you to sign in yourself. |
| `linkedin_session_info` | Whether the session is live and **when it lapses**, read from the browser's own cookie jar. Reports the credential, the csrf cookie that supports it, durability, and why no silent reauth exists here. `renewal.session_lapses_at` is the date past which no renew can help and you sign in by hand -- the field to compare across servers, and on LinkedIn it equals the cookie's own expiry because nothing here can carry the session past it. |
| `linkedin_logout` | Ends the **local** sign-in by erasing this machine's cookie jar. The one destructive tool here: `confirm=False` (the default) performs nothing and previews what would go. Issues no request, so LinkedIn is never told. |
| `linkedin_cdp_status` | Recovery diagnostic: is there a Chrome this server could attach to? Touches nothing on LinkedIn. |
| `linkedin_server_info` | The boundary, the rate settings and the launch flags, without reading the source. |

## The three that write

| Tool | What it does |
|---|---|
| `linkedin_save_job` | Bookmarks one posting. Call it with no `confirm_token` and it performs nothing: it reads the posting and your saved list live and returns a block naming the job by title and employer, which way the toggle would move, where each fact came from, and how to undo it. Call it again with the token from that block to act. |
| `linkedin_unsave_job` | Same shape, same gates, and **it refuses**. See below. |
| `linkedin_unfollow_company` | Stops following one company Page. Same shape and the same five gates. Addressed by the **numeric company id**, never by name -- names collide, change, and are not yours to rely on, and the click is anchored to the row carrying the id, so what you name and what gets pressed are the same row by construction. |

After the click, the result is confirmed from a **different surface** -- your
saved list, with LinkedIn's own per-tab count -- rather than from the button
that was just pressed. `performed` comes back `true`, `false`, or `"unknown"`.
On `"unknown"`, do not retry: a retry on a toggle that did land performs the
opposite action.

### The one that refuses

LinkedIn identifies the save control by its accessible name. Every capture this
repo holds -- four postings, both hydration states, two different days -- shows
`aria-label="Save the job"`, the **unsaved** state. The name it wears when a
posting **is** saved has never been observed, and it cannot be observed by
reading: there is nothing saved on the account to observe it on.

So `linkedin_unsave_job` has no anchor, and this server does not guess one.
`"Saved"` and `"Unsave the job"` are both plausible and it has seen neither.
The refusal names that reason rather than saying "not implemented", because
"not implemented" invites somebody to implement it by picking a string.

**The fix is one measured line.** The first supervised save produces it:
`perform` reads back the label the control changed into and reports it. Write
that into `shape.SAVE_LABELS` and `unsave_job` acquires its anchor. It is one
row of a table, not a missing code path.

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

Messaging, InMail, connection invitations. Profile edits. Open To Work.
Following a company. Posting, liking, commenting, endorsing. Marking
notifications read. Collecting data about other members. Submitting
applications, per the section above.

These are not missing features, and they are not all the same kind of "no".
`linkedin_server_info` labels each one POLICY, MEASURED or UNMEASURED, because
"we refuse this on principle", "we looked and it will not work" and "nobody has
looked" are three different statements and a list that flattens them is how an
unexamined gap comes to read as a design decision.

**Following is the interesting one**, and its reason changed on 2026-08-24
without its answer changing. It used to be blocked because no unfollow existed
-- this server could create a state it could not clear. One exists now. It is
still not performable, because **the undo cannot be aimed**: a job posting names
its employer by slug, the unfollow surface addresses rows by numeric company id,
and no capture in this repo carries both for one company on a surface either
action uses. That surface also renders about twenty rows of fifty-eight with no
pagination control, so most of the list is unreachable in one page load. The
refusal names both, and names what would lift them.

**Reading your own inbox is UNMEASURED, not refused.** The read boundary blocks
`/messaging`, and every written rationale for that block is phrased against
*sending*. Whether reading is even possible has never been tested.
`scripts/_probe_messaging.py` exists to test it, and to test something the
question usually skips. The hypothesis -- **unverified, which is the point** --
is that LinkedIn's desktop messaging view opens a conversation on arrival, so a
"read" of the inbox would mark a thread read, which would be the notifications
objection arriving through a tool that calls itself a read.
The probe measures that by reading the nav badge from `/feed/` before and after,
a surface the load does not touch. **It has not been run**, and the forbidden
list is unchanged until it is: a boundary does not move on an unmeasured claim.

Anything else that would change something on LinkedIn's servers is out of
scope, and `tests/test_readonly.py` fails the build if a second mutating call
appears anywhere in the package.

One tool changes something on **this machine**: `linkedin_logout(confirm=True)`
erases the local cookie jar. It issues no request, so LinkedIn is never told,
and `linkedin_server_info` names it under `local_state_writes` rather than
folding it into the `read_only` field.

### The two side effects, stated rather than hidden

A read that changes something has to say so:

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

Both are disclosed in the tool docstrings and in `linkedin_server_info`.

---

## Setup

```bash
cd D:\Sundeep\projects\job-hunting\mcp-servers\linkedin
pip install -r requirements.txt
playwright install chromium
python -m pytest            # 986 passed
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
      "args": ["D:\\Sundeep\\projects\\job-hunting\\mcp-servers\\linkedin\\linkedin.py"]
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
   form submission, and any non-GET request. It finds **exactly one**: the click
   in `writes.perform`.

   The scanner was **not** relaxed to accommodate it. It still reports every
   mutating call unconditionally, and what admits this one is a separate
   one-line allowlist, `readonly.SANCTIONED_MUTATIONS`, keyed on
   `(path, function, kind)`. All three parts refuse something real: a click in
   `dom.py`, a click in a different function of `writes.py`, and a `fill` inside
   `perform` are each rejected -- and so is a click buried in a closure one scope
   down, because attribution is to the innermost enclosing function. Those five
   near-misses are each **shown failing**. The package is separately asserted to
   contain exactly as many mutating calls as the list has entries, which is what
   catches a *second* click inside `perform` that the triple alone cannot
   distinguish from the first.

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
  server.py                  the seventeen tools
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
