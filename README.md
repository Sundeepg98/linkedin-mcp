# linkedin

A **strictly read-only** MCP server that shows you your own LinkedIn account data
as structured tool results instead of pages you have to click through.

It reads. That is all it does. There is no write path in this repository -- not
disabled, not stubbed, not behind a flag.

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
| Reads only | Nothing is applied to, saved, sent, posted, endorsed, invited or edited. |

**This lowers exposure. It does not eliminate it.** Automated access can still
result in a rate limit, a challenge, or account action, and that risk is yours
to accept. Decide that deliberately before you register the server.

---

## What it can do

| Tool | Reads |
|---|---|
| `linkedin_who_viewed_me` | Who viewed your profile. Where the account has Premium Career, this reaches back 365 days -- the highest-intent signal in a job search. |
| `linkedin_my_applications` | Jobs you applied to, with the status LinkedIn shows. |
| `linkedin_saved_jobs` | Jobs you bookmarked. |
| `linkedin_search_jobs` | Job search with keywords, location, remote, date posted, experience level. |
| `linkedin_job_detail` | One posting in full -- pay range, LinkedIn's applicant count, workplace and employment type, hiring status, and the description. None of these is on a search or saved-jobs card. |
| `linkedin_my_profile` | Your own profile: headline, about, skills, and which sections rendered. Experience/Education/Skills are deferred by LinkedIn until the page is scrolled, so they read UNKNOWN rather than zero. |
| `linkedin_notifications` | Your notification list. |
| `linkedin_auth_status` | Whether there is a live session, measured by an authenticated request. |
| `linkedin_login_browser` | Opens a window for you to sign in yourself. |
| `linkedin_session_info` | Whether the session is live and **when it lapses**, read from the browser's own cookie jar. Reports the credential, the csrf cookie that supports it, durability, and why no silent reauth exists here. `renewal.session_lapses_at` is the date past which no renew can help and you sign in by hand -- the field to compare across servers, and on LinkedIn it equals the cookie's own expiry because nothing here can carry the session past it. |
| `linkedin_logout` | Ends the **local** sign-in by erasing this machine's cookie jar. The one destructive tool here: `confirm=False` (the default) performs nothing and previews what would go. Issues no request, so LinkedIn is never told. |
| `linkedin_cdp_status` | Recovery diagnostic: is there a Chrome this server could attach to? Touches nothing on LinkedIn. |
| `linkedin_server_info` | The boundary, the rate settings and the launch flags, without reading the source. |

## What it deliberately cannot do

Applying to jobs. Saving or unsaving. Messaging, InMail, connection invitations.
Profile edits. Open To Work. Posting, liking, commenting, endorsing. Marking
notifications read. Collecting data about other members.

These are not missing features. If a tool would change anything on LinkedIn's
servers, it is out of scope, and `tests/test_readonly.py` fails the build if one
appears.

One tool changes something on **this machine**: `linkedin_logout(confirm=True)`
erases the local cookie jar. It issues no request, so the boundary above --
which is about LinkedIn -- is intact, and `linkedin_server_info` names it under
`local_state_writes` rather than folding it into `read_only: true`.

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
python -m pytest            # 989 passed
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
   form submission, and any non-GET request. It finds none. `evaluate` is
   flagged too: the three read-only DOM harvesters waive it with a trailing
   `# readonly-ok`, so any new `evaluate` fails the build until somebody waives
   it in a reviewable diff.

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
  dom.py                     the three read-only harvesters
  shape.py                   pure parsers and the result envelope
  server.py                  the thirteen tools
  errors.py
tests/                       989 tests, no network, no account
  fixtures/                  frozen LinkedIn markup, scrubbed
```

## Status

Built and tested: **989 tests**, no network and no account. Most run with no
browser at all; the four fixture-driven modules launch a local headless
Chromium to run the real injected harvester over frozen markup, which reaches
nothing outside the machine.

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
