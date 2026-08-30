# The nine — live census results the offline wave could not run

Run by the lead 2026-08-30 ~11:15 IST against the running server at `21d9ba0`,
after a `/mcp` reconnect. `linkedin-nine` measured everything reachable offline
and reported ZERO live runs because `mcp__linkedin__*` never resolved for it;
these are those runs. Three calls, one page load each, nothing clicked.

**Read every row with the census's own caveat: PRESENCE IS NOT PERMISSION, and
FIRST RENDER ONLY — an absent control is UNKNOWN, never zero.** These establish
that a surface carries a control and what shape it wears. They establish nothing
about whether using it is safe, reversible, or sanctioned.

## #6 settings — `/mypreferences/d/categories/account`

34 controls: **0 forms, 0 contenteditable, 1 button, 33 links.** The index is
pure navigation; every toggle lives one level down, behind the read boundary.

Two hrefs worth carrying forward:
- `/profile/edit-basic-info` — a second route into #4.
- `/mypreferences/d/unfollowed` ("People you unfollowed") — bears on #8.

## #4 profile edits — `/in/<member>/?isSelfProfile=true`

233 controls, **2 forms**, 0 contenteditable, 4 dialogs. URL-addressable editors
are present as real anchors:

| href shape | what |
|---|---|
| `/in/<member>/edit/intro/` | intro editor |
| `/in/<member>/edit/forms/summary/new/` | new summary |
| `/in/<member>/overlay/contact-info/` | contact info overlay |
| `/profile/edit-basic-info` (from settings) | name, location, industry |

**THIS REFUTES A LOAD-BEARING CLAIM IN THE SERVER.** `_WHY_NOT_PERFORMED` in
`server.py` states the profile editor "is not addressed by a url at all -- 237
urls and 37 payload paths measured across five profile captures, zero of which
reach it." Live, `/in/<member>/edit/intro/` is an `<a>` with an href. The offline
fixtures also showed 0 forms; live shows 2. The claim was true of the captures
and is false of the live page — which is exactly the failure mode of measuring
once and never re-measuring. **It must be corrected or narrowed before anything
else cites it.**

## #1 / #2 / #3 — `/feed/`

286 controls, 1 form, **0 contenteditable**, 6 dialogs.

| # | control | shape | note |
|---|---|---|---|
| 1 | `Start a post` | `div[role=button]`, no href | composer is a MODAL, not a form |
| 1 | `Write article` | `<a>` → `/article/new/` | the one URL-addressable publish route |
| 2 | `Comment` ×7 | `button`, text-named | inline composer; on the profile page the same affordance is an `<a>` to `/feed/update/<urn>/` |
| 3 | `Reaction button state: no reaction` ×7 | `button`, aria-label | **the aria-label CARRIES the toggle state** |
| 3 | `Open reactions menu` ×7 | `button`, `aria-expanded=false` | the reaction picker |

## The finding that matters beyond the nine

`Reaction button state: no reaction` shows LinkedIn writing **toggle state into
the accessible name**. That is the same class of control as the save button on a
job posting, whose reader currently knows exactly one string — `"Save the job"` —
and builds its CSS selector *from* that string (`dom.py:592`,
`button[aria-label="{label}"]`). If LinkedIn moved the save control to a
state-carrying label of this family, the selector matches NOTHING, which is
precisely the observed symptom: three identical `save_job` refusals reading
`'unknown'`, on a posting whose title and employer the same call read correctly.

**This is a lead, NOT a measurement, and it was deliberately NOT passed to the
`save-label` agent** — that agent is under instruction never to guess a label,
and handing it a plausible family is a way of guessing at one remove. The
diagnostic it is building returns the real string; that is what goes in.

## Status after this run

| # | capability | before | after |
|---|---|---|---|
| 1 | publish a post | UNMEASURED | surface measured |
| 2 | comment | UNMEASURED | surface measured |
| 3 | react | UNMEASURED | surface measured |
| 4 | profile edit | UNMEASURED | surface measured + a server claim refuted |
| 5 | endorse | IMPOSSIBLE as specified | unchanged |
| 6 | settings | UNMEASURED | surface measured, index only |
| 7 | invitations | REFUSED AT GATE | unchanged |
| 8 | follow a company | UNMEASURED | unchanged — blocker is slug→id, not the gate |
| 9 | message / InMail | REFUSED AT GATE | unchanged |

Incidental, unrelated to the nine: `Home, 1 new notification` on both surfaces —
he has one unread notification. And `Saved items` → `/my-items/saved-posts/` is a
DIFFERENT saved surface from the jobs tracker; nothing here reads it.
