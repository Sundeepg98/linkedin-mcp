# Which file inputs exist on surfaces this server can legitimately reach

**A READ. Nothing was uploaded, no LinkedIn session was opened, no page was
fetched, and the read boundary was not widened by one character.** Every page
measured below is a capture already committed to this repo, rendered in
headless Chromium and measured with `dom.read_file_inputs`.

The question was set after a measurement dissolved the previous plan. Wiring
`writes.UPLOAD_ACTIONS` would not have made file upload reachable: there is no
`_live_control` arm that returns a file input, so the sanctioned drain point
cannot land on a real composer whatever the set contains. Before choosing a
consumer, somebody had to find out where a file input actually IS.

---

## 1. THE ANSWER, in one table

| surface | address on the read allowlist? | file input present? | what an upload would expose |
|---|---|---|---|
| **post composer** (`/preload/sharebox/`) | **YES** | **ZERO, MEASURED LIVE 2026-09-04.** The composer rendered -- 2 editors, 1 dialog, a `Post` button -- and drew NO file input. It draws an `Add media` button instead. | his whole network and the public. Irreversible. |
| **own profile / photo control** (`/in/me/`) | **YES** | **MEASURED ZERO**, on both topcard captures | his own profile surface. Replaceable, and nobody receives a new artifact. |
| profile photo editor (`/in/me/edit/photo/`) | **NO** | not asked | -- |
| **Easy Apply resume** (`/jobs/view/<id>/`) | **YES** | **ONE**, page-level count, measured 2026-08-24. The only positive in the survey. | one employer. Irreversible. |
| **message composer** (`/messaging/compose/`) | **YES** | **TWO**, measured live 2026-09-01 | one person he names. Irreversible, and its spec says it possibly spends an InMail credit whose balance this server has never read. |

**The photo editor address is a GUESS and it is not allowlisted. That is the
answer for that surface**, recorded rather than worked around: no pattern was
added to reach it. If the photo control is ever wanted, somebody rules on the
address first.

---

## 1a. THE POST COMPOSER, READ LIVE -- and the answer is ZERO, not absent

**Taken 2026-09-04 as a probe against the package on disk**, not through the
MCP tool: the running server process was 41 commits stale and carried neither
`read_file_inputs` nor the `file_inputs` block, so the tool could not have
answered this. Profile lock taken and released. Two allowlisted addresses
opened, nothing clicked, typed, selected or uploaded --
`readonly.scan_source_for_mutations` reports zero mutating calls in
`scripts/_probe_file_inputs_live.py`.

    post composer  /preload/sharebox/
      composer     editors=2  buttons=20  dialogs=1     -- IT RENDERED
      file_inputs  count=0    undercounted=False
      VERDICT      ZERO -- the composer rendered and draws no file input

**THIS IS A ZERO AND NOT AN ABSENCE, and the distinction is the whole value of
the reading.** A file-input count of zero taken off a page that never drew a
composer says nothing. This page drew two editors, twenty buttons and a
dialog; the composer is there, and it has no file input in it.

**WHY IT HAS NONE, which a bare zero would not have told anybody.** The
composer's own control shapes carry the answer:

        1 x 'Add media' (button)
        1 x 'Text editor for creating content' (div/textbox)
        1 x 'Post' (button)
        1 x 'Schedule post' (button)

**The input is built ON DEMAND, behind `Add media`.** So the post composer's
upload path is not reachable by rendering at all: it needs a CLICK first, and
a click is a mutation that would need its own sanction and its own argument on
top of everything else this surface already costs. That moves it from "cheapest
unknown" to the MOST expensive of the three reachable candidates -- and it is
also the most exposed of them.

Note that `Add media` is a REAL measured name, short and plain, which survives
the census shaping intact. It is the opposite case to the `Resume` label in
section 2, and the contrast is worth keeping: one was read off LinkedIn, the
other off a fixture somebody wrote.

## 1b. THE FEED REFUSED ITSELF, WHICH IS THE FIELD DOING ITS JOB

    feed  /feed/
      buttons=177  links=192  dialogs=10   -- past CENSUS_MAX_CONTROLS
      file_inputs  count=0  undercounted=TRUE
      VERDICT      UNKNOWN -- the census was truncated; no count may be read
                   off this

`undercounted` was added on the theory that a filtered list could report "one
file input" about a page with three. Its FIRST LIVE USE was refusing a zero on
the feed, which is exactly the failure it was written for, and without it this
document would now be recording "the feed draws no file input" on a reading
that never saw most of the page.

---

## 2. THE CAPTURE SURVEY -- 30 rendered, 30 answered, ONE positive

Every `.html` under `tests/fixtures/` and `_audit/`, rendered and measured.
Rendered rather than grepped: a grep for `type="file"` matches one spelling and
misses `type='file'`, an unquoted attribute, and anything the markup spells
differently. Rendering asks the DOM, which is the instrument the server uses.

    apply_modal_derived.html                1 file input   'Resume' in form#1
    every other capture (29)                0

    connections_list, job_detail x5, jobs_search x3, jobs_tracker x2,
    manage_pages_following x2, notifications, profile_skills,
    profile_topcard x2, profile_views_analytics x2,
    _probe-job-followed-company-hyd, _probe-tracker-* x9

**THE ONE POSITIVE IS NOT A MEASURED NAME, and this is the trap in the
survey.** `apply_modal_derived.html` is DERIVED, and its own header separates
what was measured from what was invented:

* MEASURED, page-level, 2026-08-24: 2 forms, **1 file input**, 1 role=dialog,
  43 buttons, one enabled submit named `Submit application`.
* NOT MEASURED: **where any of it sat.** The header says so in its own words,
  and adds that the file input is "present only so the file answers to the
  recorded counts."

The accessible name my survey read -- `'Resume'` -- comes from
`<label for="resume">Resume</label>` in that derived markup. **It is fixture
scaffolding, not something LinkedIn was ever seen to draw.** A later wave
aiming at the name `Resume` would be asserting a shape nobody has observed,
which is what this package refuses everywhere else.

So the honest state of the apply modal is: **the COUNT is measured and the NAME
is not.** A count of exactly one is addressable without a name -- "the only
file input in this dialog" is a property, not a guess -- and that is the
cheapest aim available on any of the five surfaces.

---

## 3. WHAT EACH SURFACE ACTUALLY NEEDS NEXT

| surface | what is missing | cost |
|---|---|---|
| Easy Apply resume | nothing measurable. The count of 1 is measured; aim by count-of-one, never by the invented `Resume` label | a `_live_control` arm |
| message composer | nothing measurable. Two inputs, so a count cannot address either -- needs an in-page name comparison, the way `_typeahead_gate` already does it | a `_live_control` arm + a name needle |
| post composer | **ONE READ.** The address is allowlisted and nobody has ever looked | one page load |
| profile photo | **A RULING, then a read.** The topcard draws no file input, so the control is behind something a click opens, and the editor address is not on the allowlist | operator ruling |

`linkedin_surface_census` now reports a `file_inputs` block on any page it
loads, so the post-composer read costs one call and no new code.

---

## 4. TWO THINGS THE SURVEY MEASURED ABOUT ITSELF

**Nine of thirty came back `RENDER FAILED` on the first two runs, and all
thirty render.** The failures correlated with alphabetical position, which is
the tell: a property of a capture does not depend on where it sits in a list.
One earlier capture carries a Trusted Types CSP; once loaded it governs the
PAGE, so every later `set_content` on that same page throws
`This document requires 'TrustedHTML' assignment` and the failure is attributed
to whichever innocent capture came next. Fixed with a fresh page per subject.
Filed as `A-SHARED-PAGE-CARRIES-THE-LAST-SUBJECTS-POLICY` in
`_audit/INSTRUMENTS.md`.

**The handler recorded the exception CLASS and dropped the message.** "Error"
is what a 30-percent hole in a completeness survey looked like for two runs.
The message named the cause on the first one.

---

## 5. WHAT THIS DOES NOT SAY

* It does not say the post composer has no file input. It says **nobody has
  looked**, and those are different answers that must not be collapsed.
* It does not say the profile photo control is not a file input. It says the
  captured topcard draws none, and the editor address is outside the boundary.
* It does not rank the four consumers. Exposure and reachability point at
  different surfaces -- the photo is least exposed and least reachable; the
  apply modal is most aimable and reaches one employer -- and that trade is a
  ruling, not a measurement.
