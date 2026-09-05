# Fourteen rows are filed against a surface that is not what stops them

**THE COUNT: 14.** Every GAP row in the census was asked a question the census
did not ask -- not *where does LinkedIn draw this control*, but *what address
serves this capability, and does the read gate admit that address today* --
and fourteen rows answer differently from their filing. **Six of the fourteen
sit on an address that was already on the allowlist when the census froze**,
and one of those six needs no new address, no new parser and no new tool: the
key it wants is already extracted by this package and then thrown away three
lines later.

The hypothesis under all of it was stated this morning by the wave that found
the first instance:

> A row filed against the surface where a control is DRAWN is not necessarily
> blocked by that surface.

Its instance was `J 107`, "see all jobs at this company", filed under
`COMPANY-PAGE-SURFACE` because that is where LinkedIn draws the button, and
served by `/jobs/search/?f_C=<numeric id>` -- verified ALLOWED, no boundary
change. **This pass looked for the rest of them.** It is desk work: no
browser, no session, no page load, no `mcp__linkedin__*` call.

**THE SHAPE OF THE ANSWER MATTERS MORE THAN THE NUMBER.** Fourteen is small
against 408. What it buys is that thirteen of the fourteen need no ruling from
the operator at all, and the fourteenth needs a ruling that is already written
down. Against a ranked list whose top twelve blockers reach 146 rows for a
combined cost of 66 artifacts and five operator decisions, a row that costs a
parameter is a different kind of row.

**AND THE SAME PASS FOUND ONE ROW THAT IS COSTED TOO CHEAP.** The audit runs
both ways or it is an advocacy document. `M M34` is filed as a missing
parameter at cost 1 with boundary "none"; the address it needs is refused, so
it is an allowlist edit and cost 1 is not its cost.

---

## 1. THE METHOD, AND WHY IT RUNS IN TWO DIRECTIONS

**INWARD** is the obvious direction and it is the weaker one: read each GAP
row, guess the address, put it to the gate. It is weak because **a row's own
text describes the surface, not the route** -- `J 107` says "Company Page Jobs
tab", and no reading of those five words produces `/jobs/search/?f_C=`.

**OUTWARD** is the direction that finds what the rows cannot say: enumerate
what the boundary already admits, then ask which capabilities each admitted
address could serve. That is where the alert route and the sign-in form came
from; neither row names the address that serves it.

Three instruments, all tracked, all read-only, all printing a control before a
result:

    scripts/_probe_route_vs_surface.py
        32 candidate routes through readonly.assert_read_url at HEAD, with
        seven controls -- three that must be ALLOWED and four that must be
        REFUSED, one of the four for a substring rather than for a missing
        pattern, because a gate that refuses everything and a gate that admits
        everything both produce a clean-looking table. 0 control failures.
        19 of 32 routes ALLOWED.

    scripts/_probe_alert_keywords_survive_shaping.py
        the alert-keyword defect in section 4, run with a second key as its
        control so a zero is legible.

    _audit/_scratch/_route_extract_gaps.py
        the row set: every GAP row parsed structurally out of the four census
        slices, counted against the blockers ledger's own per-file expectation
        (jobs 99, profile 79, messaging 109, network 122) before anything was
        classified.

**THE ROW SET RECONCILES AT 408, NOT 409, AND THE DIFFERENCE IS ACCOUNTED
FOR.** The ledger's expectation is 409 at the freeze. `N 118` was retired to
`MEASURED-ABSENT` in the census file itself by commit `191c2f7`, which is the
whole of the gap. Three of the four slices matched their expectation exactly;
network matched at 121 plus that one retirement. **A parse that had not been
given a number to miss could not have found that.**

**THE GATE'S OWN MESSAGE DOES HALF THE WORK NOW, and this pass is a
beneficiary.** `readonly.assert_read_url` reports, on a substring refusal,
whether a read pattern would have admitted the address anyway. So a refusal
here is recorded as `REFUSED-FORBIDDEN[<substring>]-AND-NO-PATTERN` or
`-PATTERN-WOULD-ADMIT`, and the two are different findings. Every refusal
below is the first kind, which means no result here rests on reading a
substring as the wall when it was merely the first gate.

---

## 2. THE TABLE

Boundary measured at HEAD by importing the module under
`venv/Scripts/python.exe`: **allowlist 27 patterns, forbidden 33 substrings.**
"pattern since" is the commit that first put the serving address on the
allowlist, taken by `git log -S` over `linkedin_server/readonly.py`.

| row | capability | filed as | address that serves it | gate at HEAD | pattern since | verdict |
|---|---|---|---|---|---|---|
| `J 37` | list and manage all alerts | `SERVED-BY-GMAIL-SKILL`, NOT-OURS, cost 0 | `/jobs/search/?keywords=<the alert's own query>` | ALLOWED | `b7e210b` 2026-08-22 | **REACHABLE NOW** |
| `J 38` | read the jobs an alert delivered | same | same | ALLOWED | `b7e210b` 2026-08-22 | **REACHABLE NOW** |
| `J 10` | filter a job search by company | `COMPANY-ID-RESOLVER`, BUILD, cost 2 | `/jobs/search/?f_C=<numeric Page id>` | ALLOWED | `b7e210b` 2026-08-22 | **REACHABLE NOW** |
| `J 107` | see all jobs at this company | `COMPANY-PAGE-SURFACE`, BUILD, cost 9 | same | ALLOWED | `b7e210b` 2026-08-22 | **REACHABLE NOW** |
| `P J4` | current #Hiring state | `OPEN-TO-HIRING-MODAL`, MEASURE, cost 7 | `/in/me/` | ALLOWED | `b7e210b` 2026-08-22 | REACHABLE BUT UNBUILT |
| `P N12` | keep me logged in / auto sign-in | EXCLUDED-RULED, on `/uas/login` | `/login` | ALLOWED | `b7e210b` 2026-08-22 | REACHABLE BUT UNBUILT |
| `P E6` | hide or show an endorsement received | `ENDORSE-SUBSTRING-OVERREACH`, denylist x1, cost 7 | `/in/me/details/skills/` | ALLOWED | `b7e210b` 2026-08-22 | STILL BLOCKED, other blocker |
| `P E7` | endorsements received | same | same | ALLOWED | `b7e210b` 2026-08-22 | STILL BLOCKED, other blocker |
| `N 114` | hide an endorsement from a particular member | same | same | ALLOWED | `b7e210b` 2026-08-22 | STILL BLOCKED, other blocker |
| `M C60` | access your LinkedIn Groups | `GROUPS-SURFACE`, allowlist +2, cost 10 | `/groups/` | ALLOWED | `6b5dad5` 2026-09-05 | REACHABLE BUT UNBUILT |
| `N 173` | the list of groups you belong to | same | same | ALLOWED | `6b5dad5` 2026-09-05 | REACHABLE BUT UNBUILT |
| `N 174` | the groups you have requested to join | same | same | ALLOWED | `6b5dad5` 2026-09-05 | REACHABLE BUT UNBUILT |
| `N 180` | events recommended to you | `EVENTS-SURFACE`, allowlist +1, cost 9 | `/events/` | ALLOWED | `6b5dad5` 2026-09-05 | REACHABLE BUT UNBUILT |
| `M M34` | search messages by keyword | `MISSING-PARAM-MESSAGING`, BUILD, cost 1, boundary "none" | `/messaging/?searchTerm=<q>` | **REFUSED-NO-PATTERN** | -- | costed too cheap |

**PROVENANCE INSIDE THE TABLE, because five of these are not this pass's
finds.** `J 107` is the `company-page` wave's; this pass re-took the gate
reading independently rather than relaying it. `M C60`, `N 173`, `N 174` and
`N 180` moved because `6b5dad5` opened those two roots today, and that commit
names `N 173`, `N 174` and `C 60` in its own boundary comment -- so those rows
are already claimed in the code, and appear here because a reader of the
census cannot see that from the census. **The eight rows that move on evidence
taken here are `J 37`, `J 38`, `J 10`, `P J4`, `P N12`, `P E6`, `P E7` and
`N 114`.**

### The three categories, and which one a reader should care about

* **REACHABLE NOW** -- the address passes and a tool could be built with no
  ruling, no capture and no boundary change. Four rows.
* **REACHABLE BUT UNBUILT** -- the address passes and no reader exists.
  Writing one without a capture would be guessed selectors, so this is a
  build with a measurement in front of it and **no decision attached**. Six
  rows.
* **STILL BLOCKED** -- three rows, and their filing points at the wrong thing.
  Section 5.

---

## 3. WHAT THE OUTWARD PASS FOUND FIRST: THE RICHEST DOOR HAS BEEN OPEN SINCE
## THE FIRST COMMIT

`/jobs/search/` is admitted with **any query string** --

    ^https://www\.linkedin\.com/jobs/search/?(\?[^#]*)?$

-- and it has been on the allowlist since `b7e210b`, 2026-08-22, the commit
that made this the canonical linkedin server. Everything LinkedIn expresses as
a job-search facet is therefore already inside the boundary. Five of the
fourteen rows above are served by that one pattern, and the six job-filter
rows the ranked list put second (`f_AL`, `f_JT`, `f_EA`, `f_JIYN`, `f_FCE`)
have shipped since, measured live with a negative control before they were
written -- so that pattern has now delivered eleven census rows without ever
being edited.

**THE COMPANION FINDING IS THE ADDRESS LINKEDIN ITSELF HANDS OVER, AND IT IS
REFUSED.** LinkedIn's own in-app job-alert notifications and its own job-alert
emails both link to

    https://www.linkedin.com/jobs/search-results/?keywords=<the alert's query>

which is `REFUSED-NO-PATTERN` -- one hyphenated word away from the pattern
that has been admitted all along. The tracked fixture
`tests/fixtures/notifications.html` carries five such links. So anything that
followed LinkedIn's own href verbatim would be refused, and the route that
works is to rebuild the address rather than to follow it. That is worth a
sentence in the boundary rather than a discovery in a future wave.

### The rest of the twenty-seven, and what each could serve

| already admitted | census rows it bears on | state |
|---|---|---|
| `/jobs/search/` + any query | `J 9-14`, `J 10`, `J 37`, `J 38`, `J 107`, `J 151`, `J 15`, `J 16` | six shipped, five move here |
| `/premium/my-premium/` | `J 127`, the InMail balance | opened 2026-09-01 for exactly this and **read by no tool**; `linkedin_surface_census` opens it to COUNT controls, which is not the same as reading a balance |
| `/mynetwork/invite-connect/connections/` | `N 169`, `N 187` | opened `5e33aa9`; a reader now exists and returns name, headline, link and `recipient_id` -- **none of the four fields those two rows filter on** |
| `/analytics/profile-views/` + any query | `N 133 134 136`, `P O3` | the ledger already files these with boundary "none"; the query half means a filter might be addressable rather than pressed, and that is one live read nobody has taken |
| `/analytics/search-appearances/` | `P G7`, `N 132` | opened today; reader built, no tool, no live read -- and the census already carries that in both rows |
| `/in/me/details/interests/` | the newsletter and following families | admitted 2026-09-04 and **measured not to serve**: it redirects to the profile, with two same-run siblings as the control |
| `/feed/update/urn:li:<type>:<id>/` | `M C43`, `M C34`, `N 148`, the comment controls | admitted; what is in front of these is a ruling, not an address |
| `/messaging/thread/<id>/` | `M M47`, `M M10` and the per-message menu | admitted; `M M47` is the nearest write in the package that needs no address at all |
| `/messaging/` bare | the conversation-overflow family | admitted, and already measured: no popup trigger exists in 1.28 MB of settled inbox |

**AND A NEGATIVE RESULT ABOUT A CHECK SOMEBODY WILL BE TEMPTED TO BUILD
CHEAPLY.** The gap-blockers ledger's A12 recommends counting allowlist
patterns that no code navigates to, and warns that the check must parse
navigation calls rather than grep for urls. That warning reproduces: a scan of
`CENSUS_SURFACES` plus every module-level constant naming a linkedin address
leaves **14 of the 27 patterns apparently unreached**, and at least **11 of
those 14 demonstrably have readers** -- job search, job view, the tracker,
both profile-views spellings, notifications, the item permalink, a thread, the
self-profile detail pages, the manage-Pages list and the addressed composer.
The addresses are built by f-strings inside functions, which no constant scan
sees. **A cheap version of A12's check would report 14 and be wrong by 11.**
It is named here so the next reader does not build the cheap one.

---

## 4. THE ROW THAT COSTS TWO LINES: A KEY THIS PACKAGE EXTRACTS AND THEN
## DELETES

`J 37` and `J 38` are filed cost 0, NOT-OURS -- available to him today through
the Gmail skill, with no LinkedIn session at all, and therefore not this
server's to hold. That filing is defensible and it misses something that was
already in the code.

**`shape.notification_handles` exists to turn a notification url into
something a tool here accepts**, and its own comment names the payoff: *"A
keyword a caller can pass straight to linkedin_search_jobs is worth more than
the dozen tokens it occupies."* Job-alert notifications carry that keyword in
their query string.

**`shape.parse_notification` deletes the query string before calling it.**

    link = absolute_url(record.get("href", ""))
    ...
    out.update(notification_handles(link))

`absolute_url` ends `return url.split("?", 1)[0]`. Measured, with a second key
as the control:

| | raw link | link as `parse_notification` hands it over |
|---|---|---|
| `search_keywords` -- lives in the QUERY | `{'search_keywords': 'Senior Software Engineer'}` | `{}` |
| `company_id` -- lives in the PATH | `{'company_id': '1035'}` | `{'company_id': '1035'}` |

**THE CONTROL IS WHY THIS IS A FINDING AND NOT AN OBSERVATION.** One of the
two keys still fires, on every notification that carries a company link. So
the extractor looks alive, the field it cannot emit looks like a notification
that simply had no keyword, and nothing anywhere reports a difference. A
reading with only the first key would have been ambiguous between a broken
extractor and an input with nothing to find.

**THE EVIDENCE HAS BEEN ON DISK THE WHOLE TIME.**
`tests/fixtures/notifications.html` -- tracked, so it survives a clone --
carries **five** links with `keywords=` on them. `tests/test_notification_handles.py`
asserts `search_keywords` twice and both assertions call
`notification_handles` directly, never through the shaper that a tool calls.
So the unit is green, the fixture holds the counter-example, and the path
between them is the one thing nothing exercises.

**WHAT IT BUYS.** With the keyword surviving, `linkedin_notifications` hands a
caller the exact query a job alert was built from, and `linkedin_search_jobs`
already takes that argument and already builds `/jobs/search/?keywords=` on an
address admitted since the first commit. That is the alert's own result set,
re-run through this server, with no new address, no new parser and no new
tool. It does not make the Gmail skill redundant -- the skill reads what the
alert actually delivered, and this re-runs the search behind it, which is a
different reading of the same alert -- but it moves two rows off NOT-OURS.

**IT IS A DEFECT, NOT A FEATURE REQUEST, AND IT IS NOT FIXED HERE.**
`linkedin_server/shape.py` had another wave writing in it during this pass.
The probe is tracked so the next reader can re-take the reading rather than
re-derive it.

---

## 5. WHERE THE FILING IS ACTIVELY MISLEADING RATHER THAN MERELY
## SURFACE-SHAPED

The brief asked for these separately, and there are two.

### 5.1 `P E6`, `P E7`, `N 114` -- costed a denylist edit that buys nothing

All three are filed under a blocker named for the forbidden substring
`/endorse`. Measured at HEAD: **that substring appears at exactly one site in
`linkedin_server/` -- its own entry in the tuple.** Nothing in this package
builds an address containing it, and the page all three rows live on,
`/in/me/details/skills/`, is ALLOWED.

So the denylist edit costed into that blocker (`denylist x1`, contributing to
cost 7) purchases nothing, because no address of this capability meets that
substring.

**AND THE REAL BLOCKER IS BETTER EVIDENCED THAN THE NAMED ONE.** A live
reading on 2026-09-04 found **zero** occurrences of `endors` anywhere on that
page -- 20 skill cards, 2,359 characters of `main`, on a page that DREW. So
what stops these rows is that LinkedIn draws no endorsement line for this
account to read, which is a measurement, where the substring was an
inference. The rows stay blocked and the reason changes.

### 5.2 `P N12` -- subtracted on an address nothing here builds

`P N12` is "keep me logged in / auto sign-in". The census names its address as
`/uas/login`, and the blockers ledger machine-checked that address refused --
`/uas/` is on the forbidden list -- and subtracted the row to EXCLUDED-RULED
on that basis. Both readings are accurate.

**Nothing in this package builds `/uas/login`.** `config.LOGIN_URL` is
`https://www.linkedin.com/login`, pattern 27 admits it, and `linkedin_login`
opens exactly that address for the operator to sign in himself. The
repository's own `config.AUTHWALL_MARKERS` lists `/login` and `/uas/login`
side by side as the same class of landing.

Verified this pass:

    REFUSED-FORBIDDEN[/uas/]-AND-NO-PATTERN   https://www.linkedin.com/uas/login
    ALLOWED                                   https://www.linkedin.com/login

So the subtraction rests on a refusal of an address this server never
constructs, while the sign-in form it does open is admitted. Whether the row
is worth building is a separate question -- the control is a checkbox on a
form the operator types into himself -- but it is not held out by the
boundary.

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- its A1 ledger subtracts `P N12` to EXCLUDED-RULED because `/uas/login` meets the forbidden substring `/uas/`, and nothing in this package builds that address; the sign-in form this server does open is `config.LOGIN_URL` = `https://www.linkedin.com/login`, machine-verified ALLOWED at HEAD, so the boundary is not what holds that row out.

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- its row `C60` states that `/groups/` is on neither the allowlist nor the forbidden list, and commit `6b5dad5` put the `/groups/` root on the allowlist on 2026-09-05, machine-verified ALLOWED at HEAD, so what holds that row is the render and the missing reader rather than the boundary.

---

## 6. THE ROW THAT MOVES THE OTHER WAY

`M M34`, search messages by keyword, is filed `MISSING-PARAM-MESSAGING`, one
row, BUILD, boundary "none", cost 1 -- on the reading that
`linkedin_open_messaging` takes no query parameter, which is true.

Pattern 1 is anchored and admits no query at all:

    ^https://www\.linkedin\.com/messaging/?$

Measured: `https://www.linkedin.com/messaging/?searchTerm=recruiter` is
`REFUSED-NO-PATTERN`, while the bare `/messaging/` is ALLOWED. So a url-borne
search needs an allowlist edit, and the alternative -- typing into the inbox's
own search box -- is a fill on a surface, which is a different argument again.
Either way cost 1 with boundary "none" is not what this row costs.

**Two more that a reader should not take from this document as cheap**, both
verified refused here: `/jobs-tracker/?stage=applied&f_TPR=r604800` (`J 56`,
filter the tracker by date) and `/in/me/?locale=fr_FR` (`P D28`, view a
profile in another language). Both patterns are anchored against exactly the
query they were opened for. The second is already filed with `allowlist +1`;
the first is the one to check.

---

## 7. THE TRAP THE BRIEF NAMED, REPRODUCED

`https://www.linkedin.com/company/connectwise/` is refused, and the substring
that refuses it is `/connect`:

    REFUSED-FORBIDDEN[/connect]-AND-NO-PATTERN

**A real company is unreachable because of its name.** The refusal is not
about company Pages -- `/company/` has no pattern either, so this address is
refused twice -- but the substring fires first and a reader who stopped there
would conclude the wrong thing about the class.

Two live instances of the same shape, both read addresses meeting a
write-shaped guard, both currently refused by BOTH gates:

    REFUSED-FORBIDDEN[/unfollow]  /mypreferences/d/unfollowed
                                  N 39, N 40 -- the people he previously unfollowed
    REFUSED-FORBIDDEN[/follow]    /mynetwork/network-manager/people-follow/following/
                                  N 38 -- the people he follows

Neither is a new finding: `PEOPLE-FOLLOW-LISTS` already costs a denylist edit
alongside its two allowlist patterns, so the ledger has this right. They are
recorded because they are the same defect the connections list was built to
answer, in that tool's own words -- *"two entries on the forbidden-substring
list, both there to stop this server from ever issuing an invitation, were
ALSO matching the address of the page that merely lists people he already
knows. A write guard was matching a read address."* **The class has a name in
this repository now, and it still has members.**

---

## 8. WHAT THIS PASS DID NOT SETTLE

**AN ADDRESS PASSING THE GATE IS NOT A CAPABILITY, AND THIS DOCUMENT IS ONE
LAYER ONLY.** The team lead's ruling holds throughout: the boundary decides
what may be OPENED, the shaper decides what may be SAID. Every ALLOWED above
is a statement about the first layer. It says nothing about what a reader
would be permitted to return, and nothing about whether the page renders the
thing at all.

**AND THE RENDER GATE APPLIES TO SEVERAL OF THESE.** A tabbed category's rows
are not in the document until its tab is pressed, proven by control on the
Interests surface. `M C60`, `N 173`, `N 174` and `N 180` are addresses whose
render nobody in this repository has seen.

**`P J4` IS UNVERIFIABLE ON THIS ACCOUNT, AND THAT IS THE POINT OF LISTING
IT.** Its capability is the current #Hiring state, filed against the
Open-To-Hiring modal, and the state is drawn on the topcard `linkedin_my_profile`
already loads -- `shape.parse_open_to_work` reads the sibling line off that
same card. But measured on both tracked topcard captures, with the sibling as
the control:

    "Open to work"   1   1     <- the control fires
    "Hiring"         0   0

So the line shape cannot be established from anything on disk, because he does
not hold the state. Building the parser without a capture would be guessing at
a string, and this repository has already paid for that once, on the
endorsement counts. **The row moves off the modal and onto the topcard; it
does not become buildable.**

**FIVE OF THE FOURTEEN ARE NOT THIS PASS'S FINDS**, and section 2 says which.

**THE `f_C` ROUTE HAS A KNOWN LIMIT.** `linkedin_job_detail` returns the
employer's numeric Page id, which is what `f_C` needs, and it returns it as a
verdict rather than a value: `company_id.state` is `resolved` only when
exactly one canned people-search link was on the page and its card named this
posting's own employer. It is `absent` on four of the five captures held here,
because LinkedIn draws that panel for some employers and not others. So `J 10`
and `J 107` are reachable for the employers whose postings carry the panel,
and that fraction is unmeasured.

**THE PARAMETER SPELLINGS ARE NOT ALL MEASURED.** `f_C` is LinkedIn's own,
read off LinkedIn's own link. The multiple-location spelling for `J 151` is
not, and this repository has a standing method for that -- the four boolean
filters were established with a negative control that proved LinkedIn STRIPPED
an unrecognised parameter from the landed url. `J 151` is not claimed above,
for that reason.

**NOTHING HERE RE-STATES THE GAP TOTAL.** Whether a row whose address is
admitted stops being a GAP is the lead's ruling, the same fork the ledger
recorded for its own eight forbidden-substring rows. This document moves
blockers and costs; it does not move the census.

---

## 9. PROVENANCE

* Boundary read by importing `linkedin_server.readonly` under
  `venv/Scripts/python.exe` -- **allowlist 27, forbidden 33.** HEAD moved
  repeatedly during this pass, so the reading is pinned rather than described:
  taken first at `9b74858`, re-taken at `77fbc29`, identical on both counts.
  The row set reconciles at 408 at both.
* Every route verdict from `scripts/_probe_route_vs_surface.py`: 7 controls,
  **0 control failures**, 32 candidates, 19 ALLOWED.
* The alert-keyword defect from
  `scripts/_probe_alert_keywords_survive_shaping.py`, with `company_id` as its
  control, plus a needle count over `tests/fixtures/notifications.html`.
* Row set from `_audit/_scratch/_route_extract_gaps.py`, reconciled per file
  against the blockers ledger's own expectation before classification.
* Pattern dates from `git log -S` over `linkedin_server/readonly.py`, one
  query per pattern, oldest commit taken.
* `#Hiring` and follower needles counted over
  `tests/fixtures/profile_topcard.html` and its hydrated sibling, with
  `"Open to work"` as the must-fire control.
* `/endorse` site count by grep over `linkedin_server/*.py`.
* Working log: `_audit/_scratch/_progress-route-audit.md`.
* No browser, no session, no page load, no `mcp__linkedin__*` call. Two
  tracked scripts added, one census back-pointer line, one ledger back-pointer
  line. No push.
