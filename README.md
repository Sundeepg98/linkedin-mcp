# linkedin-own

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
| `linkedin_my_profile` | Your own profile: headline, about, skills, which sections are filled in. |
| `linkedin_notifications` | Your notification list. |
| `linkedin_auth_status` | Whether there is a live session, measured by an authenticated request. |
| `linkedin_login_browser` | Opens a window for you to sign in yourself. |
| `linkedin_session_info` | Whether the session is live and **when it lapses**, read from the browser's own cookie jar. |
| `linkedin_cdp_status` | Recovery diagnostic: is there a Chrome this server could attach to? Touches nothing on LinkedIn. |
| `linkedin_server_info` | The boundary, the rate settings and the launch flags, without reading the source. |

## What it deliberately cannot do

Applying to jobs. Saving or unsaving. Messaging, InMail, connection invitations.
Profile edits. Open To Work. Posting, liking, commenting, endorsing. Marking
notifications read. Collecting data about other members.

These are not missing features. If a tool would change anything on LinkedIn's
servers, it is out of scope, and `tests/test_readonly.py` fails the build if one
appears.

### The two side effects, stated rather than hidden

A read that changes something has to say so:

1. **Opening the notifications page clears LinkedIn's unread badge** -- exactly
   as it would if you opened the page yourself. It is inherent to loading the
   page, not an action this server takes, and individual items are not opened.
   If you would rather it did not happen, do not call `linkedin_notifications`.
2. **Running a job search adds to your own recent-search history**, the same as
   typing the query on the site.

Both are disclosed in the tool docstrings and in `linkedin_server_info`.

---

## Setup

```bash
cd D:\Sundeep\projects\job-hunting\mcp-servers\linkedin-own
pip install -r requirements.txt
playwright install chromium
python -m pytest            # 357 passed
```

Then, once the server is registered with a client, **call `linkedin_login_browser`
first.** A window opens at linkedin.com/login. Sign in there yourself -- this
server never sees, types, stores or transmits a password. The persistent Chrome
profile keeps the session afterwards, so this is a one-time step until LinkedIn
expires it.

Confirm with `linkedin_auth_status` before trusting any read.

### Registering it

stdio transport, entry point `linkedin_own.py`:

```json
{
  "mcpServers": {
    "linkedin-own": {
      "command": "python",
      "args": ["D:\\Sundeep\\projects\\job-hunting\\mcp-servers\\linkedin-own\\linkedin_own.py"]
    }
  }
}
```

---

## How "read-only" is enforced rather than asserted

`linkedin_own_server/readonly.py` holds four mechanisms, and the tests show
each of them **failing on a planted violation** before trusting it on the real
package. A check that cannot fail certifies nothing.

1. **A navigation allowlist.** `assert_read_url` is the only door to
   `page.goto`. Every permitted url is an anchored pattern; a keyword you type
   cannot become a navigation to an action url. Blocked targets include
   `/jobs/application/`, `/messaging/`, invitations, `/edit/`, `open-to-work`,
   anything with `action=`, and every host that is not `www.linkedin.com`.

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

The three injected scripts are scanned separately for anything that could
mutate the page (`.click(`, `.value =`, `dispatchEvent`, `fetch(`, ...). They
query the DOM and read text.

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
refused. Enable it with `LINKEDIN_OWN_CDP_ATTACH=1` and this server launches
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
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9224 --user-data-dir="%LOCALAPPDATA%\linkedin-own-cdp"
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
linkedin_own.py              entry point (stdio)
linkedin_own_server/
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
  server.py                  the eleven tools
  errors.py
tests/                       357 tests, mocked, no network, no browser
```

## Status

Built and tested: **357 tests**, no network, no browser, no account.

**Nothing has been verified against a live LinkedIn session.** The selectors,
the profile-views surface, the `/voyager/api/me` response shape and the
`li_at` lifetime are all unconfirmed until someone signs in and runs the
tools. Expect the first live run to need selector adjustments, particularly
on notifications.

One earlier live sign-in attempt failed outright: the browser was launched
with no flags, so Blink advertised `navigator.webdriver = true` and LinkedIn
refused the sign-in. That is what the flag above fixes. Whether the flag alone
is sufficient is **unverified** -- it is what the sibling Naukri server has run
for months on the same machine, and it is where the boundary stops either way.
