"""The write boundary: a grant, not a mode.

THIS MODULE CAN CHANGE LINKEDIN, and the list has only ever grown. It could
change nothing until 2026-08-23; then it could save a job posting; since
2026-08-30 it can also unsave one, follow a company, unfollow one, and submit
an application. Every one of those sentences stood here in its turn, and each
was true when written. A boundary module that keeps the most comfortable of
its past sentences is the exact failure this design exists to refuse, so this
paragraph is rewritten whenever the answer changes rather than softened. The
count itself is NOT pinned by a test and the prose here has been wrong about
it before -- ``writes.PERFORMABLE`` is the authority. See "WHAT IS HERE, AND
WHAT STILL IS NOT"
at the bottom.

WHY A GRANT AND NOT A FLAG
--------------------------
``readonly.py`` answers one question: *is this a read?* A server that can write
has to answer a strictly HARDER one:

    is this the ONE write he confirmed, on the ONE target he was shown, RIGHT
    NOW?

That is a NARROWER gate than the read-only one, not a weaker one, and the
distinction is the whole design. A mode ("writes are on") answers none of those
three. A grant answers all three by construction: it names one action, it names
one target, it is consumed on first use, and it dies in
:data:`GRANT_TTL_SECONDS`.

Every mechanism in ``readonly.py`` keeps its default-deny posture. None is
relaxed here:

1. **Navigation.** ``assert_read_url`` is untouched -- a zero-line diff, still
   the only door to ``page.goto`` for every read. Writes get a SEPARATE door,
   :func:`assert_write_url`, which is stricter: the url must match the pattern
   for the grant's own action with the target id interpolated FROM THE GRANT,
   not from the caller.
2. **The forbidden list is never shortened.** Each action names exactly ONE
   substring it needs exempted and the exemption is compared with ``==``. A
   grant for ``save`` exempts nothing at all; a future ``apply`` grant would
   exempt ``/jobs/application`` and would still be refused ``/messaging``.
3. **The tool surface.** A name may leave ``FORBIDDEN_TOOLS`` only by ARRIVING
   in :data:`SANCTIONED_WRITES`. ``tests/test_writes.py`` asserts the union
   still covers the original frozen set, so a future edit cannot quietly delete
   a boundary -- only move a name across it, visibly.
4. **The launch boundary is untouched, permanently.** Writes need no third
   Chromium flag. Performing an action the operator confirmed and evading
   automation detection are different activities, and the second is not on the
   table at any point in this design.

THE READ-IT-YOURSELF RULE
-------------------------
Ratified 2026-08-23, and the newest of the three because it closes the hole
the other two were resting on:

    A GATE MAY NOT PRINT A STATE IT WAS TOLD. IT PRINTS ONE IT READ.

The two rules below both end in "the gate refuses unless it is HANDED the
measured state", and for one day that sentence had nobody behind it: the
renderer took ``state`` and ``facts`` as arguments, so every guarantee under
them rested on a not-yet-written caller remembering to read first. It does not
any more. :func:`preview` performs the reads itself, there is no parameter
left through which a state or a fact can arrive, and a grant is mintable only
against a receipt that a real page load produced. See section 5.

THE MEASURED-REVERSIBILITY RULE
-------------------------------
Ratified 2026-08-23 and enforced by :func:`_render`:

    A GATE MAY NOT PRINT A REVERSIBILITY CLAIM THAT HAS NOT BEEN MEASURED.

On the day it was written all four specs printed ``UNMEASURED``. They no
longer do, because the measurement was performed on 2026-08-23 rather than the
rule being relaxed -- and it was performed entirely through READS, which is the
part worth remembering. Reversibility was treated as something only a write
could establish; it is not. LinkedIn STATES the inverse action in the
accessible name of its own controls, and reading that costs one page load and
changes nothing.

What each spec now carries, and why four fields rather than one:

``reversibility_class``
    REVERSIBLE / IRREVERSIBLE / STILL-UNKNOWN. One word, so it cannot be
    skimmed past.
``reversibility_evidence``
    WHAT WAS OBSERVED, on which surface, on which date. A verdict with no
    evidence line is the confident string this rule exists to stop.
``reversible_by``
    WHO can undo it. This is the field that nearly went missing, and it is the
    one most likely to mislead: "reversible" reads as "this tool can undo it"
    and for ``follow_company`` that is FALSE. No unfollow is sanctioned, so a
    follow this server performs is one only he can reverse, by hand, in
    LinkedIn's own interface.
``residue``
    What stays unknown GIVEN the verdict. Membership in a list can be restored
    while its ordering cannot; a badge can be taken down and cannot be un-seen.
    A verdict that swallows its own residue is worse than an honest UNMEASURED.

THE TOGGLE-DIRECTION RULE
-------------------------
Also enforced here, and it is the harder half:

    A GATE THAT CANNOT SAY WHICH WAY IT MOVES A TOGGLE IS NOT A GATE.

Both controls the writes act on are toggles, and until 2026-08-23 every frozen
capture showed only their OFF state -- so nothing could tell Save from Unsave,
or Follow from Unfollow. That was recorded as a blocker on the write. It was
not one: it was a READ nobody had performed. Both ON states are now measured
(see :data:`shape.FOLLOW_LABELS` and the fixtures named there), and
:func:`_direction` REFUSES to render at all unless the read the gate just
performed settled the state, and that state is the one its action is valid
from. Confirming a save on an already-saved posting is not a smaller mistake
than confirming the wrong posting.

The two toggles do NOT read the same way, and the gate says which it used.
Follow is read off the posting page -- the same page the action would act on,
at no extra load. Save takes its DIRECTION from ``linkedin_saved_jobs``, a
different surface, and its ANCHOR from the control on the posting. A different
source, not a weaker one; and the second can answer "I could not tell", which
the first never has to.

THE ORIGINAL REASON FOR THE SPLIT IS GONE AND THE SPLIT IS NOT. Save read off
the list because the control's ON state could not be photographed on this
account; that stopped being true on 2026-08-30 when the ON label was measured
four times. The list read stays because it answers a question the control
cannot: membership of the list is what an unsave acts on, and a control tells
you what the button will do rather than what the list contains. It is now
also, measurably, the weaker of the two -- the Saved tab's rows draw and the
harvest returns none of them, which blocks the save-family previews at
``_direction`` while the control beside them reads perfectly well.

WHAT IS HERE, AND WHAT STILL IS NOT
-----------------------------------
ONE mutating call exists in this package and it is in :func:`perform`: a single
anchored click. ``readonly.scan_source_for_mutations`` still finds it -- the
scanner was not taught to stop looking -- and it is admitted by name, path and
kind in ``readonly.SANCTIONED_MUTATIONS``, which is one line long and which
``tests/test_readonly.py`` fails if it widens or goes stale. Every other module
in the package still scans clean.

WHAT A CALLER CAN DO: preview a save, read the block, and confirm it. That is
two round trips through this module, and between them sit the flag, the live
read, the single-use receipt, the 30-second observation TTL, the 120-second
grant, the rebuilt url, the unrelaxed forbidden list, and a re-read of the very
control about to be pressed.

WHAT STILL CANNOT HAPPEN WITHOUT THE OPERATOR PRESENT: anything at all. The
flag is off in a fresh process; a grant exists only after a human has been
shown a gate built from a live read; the grant dies in two minutes and works
once, which makes an unattended or scheduled write structurally impossible
rather than merely discouraged.

WHAT WAS STILL NOT HERE, until 2026-08-30, and it was one row of a table
rather than a code path: ``unsave_job`` was built, gated and tested on exactly
the same path as ``save_job``, and it REFUSED, because the accessible name
LinkedIn gives the save control when a posting IS saved had never been
observed -- there was nothing saved on the account to observe it on. The first
supervised save was the measurement that lifted it, exactly as this paragraph
predicted, and three read-only re-measurements confirmed the label before the
row was written. See :data:`shape.SAVE_LABELS` and :func:`anchor_label_for`.

WHAT IS STILL NOT HERE is now one surface rather than one row, and it is not
in this module: ``unsave_job`` has its anchor and cannot be PREVIEWED, because
:func:`_direction` refuses on an ``unknown`` origin and the Saved tab that
supplies that origin cannot currently be read. The capability is real; the
route to it runs through a broken list read.
"""

from __future__ import annotations

import os
import re
import secrets
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from linkedin_server import dom, shape
from linkedin_server.errors import WriteAttemptError

# ---------------------------------------------------------------------------
# 0. Off by default
# ---------------------------------------------------------------------------

#: Writes are opt-in per process. A fresh clone, and this repo today, is
#: read-only: nothing registers a write tool and nothing can mint a grant.
#: The flag is read at call time rather than import time so a test can set it
#: without reloading the package.
WRITES_FLAG = "LINKEDIN_ENABLE_WRITES"


def writes_enabled() -> bool:
    return os.environ.get(WRITES_FLAG, "").strip().lower() in {"1", "true", "yes", "on"}


# ---------------------------------------------------------------------------
# 1. The sanctioned set
# ---------------------------------------------------------------------------

#: How long a confirm token stays usable. Two minutes is long enough for a
#: human to read a preview and answer, and short enough that an unattended
#: caller cannot hold one: a scheduler that wakes hourly can never present a
#: live token, which is the point rather than a side effect.
GRANT_TTL_SECONDS = 120.0


@dataclass(frozen=True)
class WriteSpec:
    """One sanctioned action, described completely enough to gate it."""

    action: str
    tool_name: str
    #: What the url must look like, with ``{target}`` filled from the GRANT.
    #: ``None`` where the surface has NEVER BEEN LOADED -- see
    #: :func:`assert_write_url`, which refuses outright rather than guessing a
    #: path. A gate may not name a target surface nobody has opened, for the
    #: same reason it may not print an unmeasured reversibility claim.
    url_template: Optional[str]
    url_pattern: Optional[re.Pattern[str]]
    #: The single forbidden substring this action is allowed to contain, or
    #: None. Compared with ``==`` against the entry in the forbidden list --
    #: never as a shape, because a loose exemption is how a real write hides.
    exempt_substring: Optional[str]
    summary: str

    # -- direction ---------------------------------------------------------
    #: The state this action is valid FROM, and the state it leaves behind.
    #: ``from_state`` of ``None`` means the action is not a binary toggle and
    #: the caller must name its destination (Open To Work, which has three
    #: states rather than two).
    from_state: Optional[str]
    to_state: Optional[str]
    #: WHERE the current state is read. Named in the gate so the operator can
    #: check the reading himself rather than trusting it.
    direction_source: str

    # -- what the gate must read FOR ITSELF ---------------------------------
    #: What ``target`` identifies for this action. A job posting is addressed
    #: by a numeric id; Open To Work is a setting on HIS OWN profile and has
    #: no id at all, so it is ``"self"``. Before this field existed the only
    #: grant Open To Work could hold was a job-id grant for a profile setting,
    #: and the confirm gate printed a ``job_id`` for it.
    target_kind: str
    #: WHICH live read establishes this action's current state. The gate runs
    #: it ITSELF -- see :func:`observe` -- so the state can never arrive as an
    #: argument. Two shapes, and they are NOT the same:
    #:
    #: ``posting_page``
    #:     the state is on the very page the action would act on, so one load
    #:     yields both the facts and the direction. Follow is this shape.
    #: ``saved_list`` / ``profile_topcard``
    #:     the state lives on a DIFFERENT surface and costs a second load.
    #:     Save is this shape because the save control's ON state does not
    #:     exist on this account to read.
    #:
    #: The gate prints which shape it used rather than flattening the two,
    #: because "read off the button I am about to press" and "read off a list
    #: somewhere else" are different promises.
    state_from: str

    # -- reversibility, measured --------------------------------------------
    reversibility: str
    reversibility_measured: bool
    #: What would settle the question. Printed while it is open, so the gap
    #: names its own fix instead of sitting as a caveat.
    reversibility_procedure: str
    reversibility_class: str = "STILL-UNKNOWN"
    #: What to say when the live read lands on a state this action is NOT
    #: valid from. Empty means the TOGGLE sentence, which is the right one for
    #: save, unsave and follow and is FALSE for apply: applying from the wrong
    #: state does not perform the opposite action, it performs an irreversible
    #: one somewhere nobody meant. A generic refusal that misdescribes the
    #: danger is the same species of confident string as an unmeasured
    #: reversibility claim, so each action gets to say its own.
    wrong_state_note: str = ""
    reversibility_evidence: str = ""
    #: WHO can undo it. "this server" and "him, by hand" are not the same
    #: promise and a gate that blurs them is lying by omission.
    reversible_by: str = ""
    #: What stays unknown even given the verdict.
    residue: str = ""
    #: For a setting with an audience: who can see each destination. Empty for
    #: actions that are nobody's business but his own.
    audiences: dict[str, str] = field(default_factory=dict)
    irreversible: bool = False
    spends: Optional[str] = None


#: The complete set of writes this server may ever perform without a new,
#: deliberate edit here. Three, all chosen for being REVERSIBLE.
#:
#: Cut by the operator on 2026-08-23 after review, and the reasoning is kept
#: because an omission that does not explain itself reads as an oversight:
#: apply, connect and message/InMail were removed from the round as the three
#: least reversible actions, none of them measured, on the least
#: automation-tolerant platform in the family, on his only account. They return
#: only with reversibility measured rather than assumed.
SANCTIONED_WRITES: dict[str, WriteSpec] = {
    "linkedin_save_job": WriteSpec(
        action="save_job",
        tool_name="linkedin_save_job",
        url_template="https://www.linkedin.com/jobs/view/{target}/",
        url_pattern=re.compile(r"^https://www\.linkedin\.com/jobs/view/(\d{6,})/$"),
        exempt_substring=None,
        summary="Bookmark one job posting on LinkedIn.",
        from_state="not_saved",
        to_state="saved",
        target_kind="job_id",
        state_from="saved_list",
        direction_source=(
            "linkedin_saved_jobs, which reads /jobs-tracker/?stage=saved. The "
            "direction for save comes from the LIST rather than from the "
            "button. That began as a necessity -- the save control's ON state "
            "had never been observed, so the button could not answer -- and "
            "since 2026-08-30 it is a CHOICE: the ON label is measured, and "
            "the list is still the right source because membership of the "
            "list is what a save changes, while the button reports what a "
            "click would do. The list read is corroborated -- it reports "
            "LinkedIn's own per-tab count and its empty state, and raises "
            "rather than returning [] when the two disagree. Measured "
            "2026-08-30, it is also currently FAILING that way: the Saved "
            "tab's rows draw and the harvest returns none, so this direction "
            "source reports 'unknown' and the gate refuses."
        ),
        reversibility="reversible by unsaving the same posting",
        reversibility_measured=True,
        reversibility_class="REVERSIBLE",
        reversibility_evidence=(
            "MEASURED 2026-08-23 by observation, not by experiment. His own "
            "saved-jobs surface renders an Unsave control in the bulk-action "
            "bar of /jobs-tracker/?stage=saved, and that control is ABSENT "
            "from ?stage=applied -- so it is bound to the saved stage rather "
            "than being page furniture that appears everywhere. LinkedIn "
            "offers the inverse action on the same surface that holds the "
            "thing."
        ),
        reversible_by=(
            "this server: linkedin_unsave_job is sanctioned alongside this "
            "one AND performable since 2026-08-30, so the undo is inside the "
            "same boundary rather than promised by it. One caveat that is not "
            "this action's fault: the undo's own preview reads the Saved tab "
            "for its direction, and that read is currently failing, so the "
            "undo may have to be done by hand until it is fixed."
        ),
        residue=(
            "STILL-UNKNOWN: whether re-saving restores the original saved "
            "DATE, and therefore the list's order. Reversible in membership "
            "is not reversible in ordering, and only a round trip settles the "
            "second. Nothing readable distinguishes them."
        ),
        reversibility_procedure=(
            "save one posting, then call linkedin_saved_jobs and confirm it "
            "appears; unsave it and confirm it leaves. Both directions read "
            "through an EXISTING read tool, so the measurement needs no new "
            "surface -- only a supervised round trip the harness currently "
            "refuses to allow. That round trip is what would settle the "
            "ordering residue above; it is not needed for the verdict."
        ),
    ),
    "linkedin_unsave_job": WriteSpec(
        action="unsave_job",
        tool_name="linkedin_unsave_job",
        url_template="https://www.linkedin.com/jobs/view/{target}/",
        url_pattern=re.compile(r"^https://www\.linkedin\.com/jobs/view/(\d{6,})/$"),
        exempt_substring=None,
        summary="Remove one job posting from your saved list.",
        from_state="saved",
        to_state="not_saved",
        target_kind="job_id",
        state_from="saved_list",
        direction_source="linkedin_saved_jobs, exactly as for save_job",
        reversibility="reversible by saving the same posting again",
        reversibility_measured=True,
        reversibility_class="REVERSIBLE",
        reversibility_evidence=(
            "MEASURED 2026-08-23. The state an unsave returns the posting to "
            "is the state in which the posting page renders "
            'aria-label=\"Save the job\" -- present on every posting captured '
            "at both hydration states, including the live one loaded that day. "
            "The inverse control is not merely offered somewhere; it is on the "
            "posting itself."
        ),
        reversible_by=(
            "this server: linkedin_save_job is sanctioned and performable."
        ),
        residue=(
            "the same ordering question as save_job. The second residue this "
            "field used to carry is DISCHARGED: it read 'the ON state of the "
            "save control has never been seen', and on 2026-08-30 it was "
            "seen -- once by the write path on his first save, then three "
            "times by a read-only route that costs no write. So moving the "
            "direction off the list and onto the button is no longer an "
            "unmeasured step. It is simply not the right question to ask a "
            "button, which is why the list read stays."
        ),
        reversibility_procedure=(
            "the same round trip as save_job, driven in the other order. Note "
            "the asymmetry worth measuring: re-saving restores the bookmark "
            "but NOT its original saved-date, so 'reversible' may be true of "
            "the list and false of its ordering."
        ),
    ),
    "linkedin_unfollow_company": WriteSpec(
        action="unfollow_company",
        tool_name="linkedin_unfollow_company",
        # NO ``{target}`` IN THE URL, and that is not an oversight. This action
        # is performed on a LIST, and the list has one address; the target
        # selects a ROW within it. ``str.format`` ignores an unused keyword, so
        # ``assert_write_url`` rebuilds this constant from the grant exactly as
        # it rebuilds an interpolated one, and the target is enforced instead
        # at the only place it can be -- the row the click is anchored to.
        url_template="https://www.linkedin.com/mynetwork/network-manager/company/",
        url_pattern=re.compile(
            r"^https://www\.linkedin\.com/mynetwork/network-manager/company/$"
        ),
        exempt_substring=None,
        summary="Stop following one company Page.",
        from_state="following",
        to_state="not_following",
        target_kind="company_id",
        state_from="followed_pages",
        direction_source=(
            "linkedin_followed_companies, which reads LinkedIn's Manage Pages "
            "list at /mynetwork/network-manager/company/. The direction is "
            "read off the SAME page the click lands on, at no extra page load "
            "-- the ideal shape, and the second action in this design to have "
            "it. The reading is reconciled against LinkedIn's own stated total "
            "and answers 'unknown' rather than 'not following' whenever the "
            "rendered rows are a fraction of that total, which on this surface "
            "is the usual case."
        ),
        reversibility="reversible by following the company again",
        reversibility_measured=True,
        reversibility_class="REVERSIBLE",
        reversibility_evidence=(
            "MEASURED 2026-08-24 by observation. LinkedIn writes the inverse "
            'action into this control\'s own accessible name -- "Click to stop '
            'following <Page>" -- across 80 rows in five independent captures '
            "at both hydration states. The undo direction is corroborated on a "
            "second surface: a company he does NOT follow renders "
            'aria-label="Follow" on its job postings, which is the state an '
            "unfollow returns him to."
        ),
        reversible_by=(
            "HIM, by hand, in LinkedIn's own interface. NOT this server: "
            "linkedin_follow_company is sanctioned but is not performed, so a "
            "re-follow through this server does not exist. The pair is "
            "deliberately ASYMMETRIC and neither half pretends the other "
            "covers it -- this server can stop a follow and cannot start one. "
            "Read that before reading the word 'reversible' above."
        ),
        residue=(
            "STILL-UNKNOWN, and unmeasurable by reading: whether the company "
            "is told. A Page's admin sees a follower count, so the number "
            "moves; nothing on any readable surface reports whether an "
            "individual departure is surfaced to anyone. Second, smaller: "
            "LinkedIn may or may not restore the original follow DATE on a "
            "re-follow, and nothing distinguishes that from a fresh one."
        ),
        reversibility_procedure=(
            "SETTLED 2026-08-24 by reading rather than by a round trip: the "
            "control names its own inverse. What a supervised round trip would "
            "add is only the residue above, which no read can reach."
        ),
    ),
    "linkedin_apply_job": WriteSpec(
        action="apply_job",
        tool_name="linkedin_apply_job",
        # ADDRESSED FROM 2026-08-25, and the address is the POSTING page
        # rather than the apply url. That is not a workaround; it is what the
        # measurement showed. Navigating to
        # /jobs/view/<id>/apply/?openSDUIApplyFlow=true LANDS BACK ON
        # /jobs/view/<id>/ with the flow drawn as a modal over the posting --
        # so the posting page IS the apply surface. This is why apply needs no
        # new allowlist entry and no shortening of any denylist: the four
        # frozen denylists are byte-identical across this change.
        #
        # WHAT THIS COMMENT USED TO SAY, kept because the reversal is the
        # point: "NEVER LOADED ... thirteen job captures contain the apply
        # CONTROL and not one contains what appears after it is activated."
        # True when written, false now. The flow was captured on 2026-08-24:
        # 2 forms, 1 file input, 1 dialog, 43 buttons, and one enabled
        # "Submit application" with no Next beside it.
        url_template="https://www.linkedin.com/jobs/view/{target}/",
        url_pattern=re.compile(r"^https://www\.linkedin\.com/jobs/view/(\d{6,})/$"),
        exempt_substring=None,
        summary="Submit an application to one job posting.",
        from_state="linkedin_apply",
        to_state="applied",
        target_kind="job_id",
        state_from="apply_control",
        wrong_state_note=(
            "This is not a toggle and the danger is not that it would do the "
            "opposite. THE OFF-SITE ROUTE IS NOT THIS SERVER'S TO PERFORM: the "
            "application would be filled in and submitted on a third party's "
            "applicant-tracking system, on their domain, under their terms, "
            "with their fields -- and this server has no business driving a "
            "form it has never seen on a site it was not built for. An "
            "'unknown' route is refused for the plainer reason that nobody "
            "could say where the application would go."
        ),
        direction_source=(
            "linkedin_job_detail's apply_path, read off the SAME posting page "
            "the action would act on, at no extra page load. LinkedIn draws "
            "the apply control as an ANCHOR, so its destination is readable "
            "before anything is activated -- which is why the route can be "
            "identified without touching it. Two routes have been measured: "
            'aria-label="LinkedIn Apply to this job" pointing at the posting\'s '
            'own apply url, and aria-label="Apply on company website" wrapping '
            "a third-party ATS in LinkedIn's outbound interstitial. Neither "
            "the label nor the href classifies alone; both must agree."
        ),
        reversibility="STILL-UNKNOWN whether an application can be withdrawn",
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "NOT MEASURED, and it cannot be measured by reading on this "
            "account. The surface that would show a withdraw affordance is his "
            "applied list, and that list is EMPTY -- both captures of "
            "/jobs-tracker/?stage=applied read a count of zero with no job "
            "rows at all. The absence of a withdraw control in an empty list "
            "is not evidence about anything. What IS certain is narrower and "
            "is stated in reversible_by."
        ),
        reversible_by=(
            "NOBODY, through this server, in either direction. Withdrawing is "
            "in PERMANENTLY_FORBIDDEN ('destruction is not a write this design "
            "covers, at any confirm level') and /withdraw is on the read "
            "boundary's forbidden list. So whatever LinkedIn's product may "
            "allow, an application this server sent is one it can never take "
            "back, and it must be treated as irreversible on that ground alone."
        ),
        residue=(
            "IRREVERSIBLE IN AUDIENCE, and that half is certain even though "
            "the state half is not. An application is READ BY A HUMAN at the "
            "employer, usually within a day. Withdrawing it later -- if "
            "LinkedIn even permits it -- removes a row from a list; it does "
            "not un-read what a recruiter has already read, and it does not "
            "un-send the notification that told them it arrived. There is no "
            "readable surface anywhere that reports whether it was seen."
        ),
        irreversible=True,
        reversibility_procedure=(
            "NOBODY HAS ESTABLISHED THAT LINKEDIN OFFERS A WITHDRAW AT ALL, "
            "and that is a worse sentence than 'this server cannot withdraw "
            "it' -- which would invite you to assume LinkedIn can. It might. "
            "It has not been measured. "
            "The measurement is: load /jobs-tracker/?stage=applied on an "
            "account that HAS an application and look for a withdraw control "
            "on a row. That requires an application to exist, which requires "
            "performing the very action whose reversibility is in question. "
            "Measured 2026-08-25, this account's Applied tab reads 0 with "
            "LinkedIn's own 'No matches' empty state, so there is no row to "
            "read. The loop resolves in one direction only: the first "
            "application made here is the one that settles the question, and "
            "if the answer is no, it will have been settled by an "
            "application nobody can take back. "
            "THE FLOW ITSELF IS NO LONGER A GAP, and this sentence used to "
            "say the opposite -- 'no capture in this repo shows the LinkedIn "
            "apply form at all'. It was captured on 2026-08-24 by "
            "scripts/_probe_apply_flow.py, which reaches the flow by "
            "NAVIGATION rather than by a click and contains no mutating "
            "call: 2 forms, 1 file input, 1 dialog, 43 buttons, and one "
            "enabled 'Submit application' with no Next beside it. That same "
            "run also metered LinkedIn's own tracker before and after and "
            "saw NO counter move, which contradicted the expectation that "
            "opening a flow creates a draft -- read as 'nothing COUNTED "
            "changed' on one posting, not as proof that nothing was created."
        ),
    ),
    "linkedin_follow_company": WriteSpec(
        action="follow_company",
        tool_name="linkedin_follow_company",
        url_template="https://www.linkedin.com/jobs/view/{target}/",
        url_pattern=re.compile(r"^https://www\.linkedin\.com/jobs/view/(\d{6,})/$"),
        exempt_substring=None,
        summary=(
            "Follow the company that posted one job, from the posting page "
            "itself."
        ),
        from_state="not_following",
        to_state="following",
        target_kind="job_id",
        state_from="posting_page",
        direction_source=(
            "linkedin_job_detail's company_follow_state, read off the SAME "
            "page the action would be performed on, at no extra page load. "
            'The control is aria-label=\"Follow\" when not following and '
            'aria-label=\"Following\" when following -- measured 2026-08-23 '
            "on his live account by loading a posting from a company he "
            "already follows. The class attributes of the two states are "
            "BYTE-IDENTICAL and aria-pressed appears nowhere on the page, so "
            "the accessible name is the whole of the signal. "
            "linkedin_followed_companies reads the same fact standalone, but "
            "it is the weaker source: LinkedIn renders 20 rows under a "
            "heading saying 58, so it answers 'unknown' more often than it "
            "answers 'no'."
        ),
        reversibility="reversible by unfollowing",
        reversibility_measured=True,
        reversibility_class="REVERSIBLE",
        reversibility_evidence=(
            "MEASURED 2026-08-23 on THREE independent surfaces, and it is the "
            "strongest evidence of the four because LinkedIn writes the "
            "inverse action into the control's own accessible name: "
            '\"Click to stop following <Page>\" on Manage Pages, '
            '\"Following, click to unfollow <Name>\" in the profile Interests '
            'list, and \"Following\" on the job posting. The undo affordance '
            "is not somewhere else in the product; it is the same button."
        ),
        reversible_by=(
            "HIM, by hand, in LinkedIn's own interface. NOT this server -- and "
            "the reason changed on 2026-08-24 without the answer changing. An "
            "unfollow IS sanctioned and performable now, so the old reason "
            "('nothing here can unfollow') is gone. The new one is that the "
            "undo CANNOT BE AIMED at what a follow creates: a posting names "
            "its employer by slug, the unfollow surface addresses rows by "
            "numeric company id, and nothing resolves one to the other. Read "
            "that before reading the word 'reversible' above; see the residue "
            "below for the measurement."
        ),
        residue=(
            "STILL-UNKNOWN, and unmeasurable by reading: WHO SAW IT. A follow "
            "can surface in his network's feed, so the data is restorable and "
            "the impression is not. Nothing on any readable surface reports "
            "whether it was shown to anyone. "
            "SECOND, AND IT IS WHY THIS ACTION IS STILL NOT PERFORMED: THE "
            "UNDO CANNOT BE AIMED. A posting identifies its employer by SLUG "
            "(/company/<slug>/); the unfollow surface identifies rows by "
            "NUMERIC ID (/company/<digits>/); and a census of every capture in "
            "this repo on 2026-08-24 found zero postings carrying a numeric id "
            "and zero Manage-Pages rows carrying a slug, with no in-page "
            "resolution between them anywhere. THIRD: even given the id, "
            "Manage Pages renders 20 rows of a stated 58 with no pagination "
            "control of any kind in five captures, so roughly two thirds of "
            "the list cannot be reached in one page load. A follow performed "
            "here could therefore be one this server cannot point its own "
            "unfollow at."
        ),
        reversibility_procedure=(
            "SETTLED 2026-08-23, and it was settled by a read rather than the "
            "round trip this line used to demand. What remains open is only "
            "the residue above, which no read can reach: a follow that has "
            "already appeared in somebody's feed cannot be un-appeared, and "
            "no supervised round trip would show that either."
        ),
    ),
    "linkedin_set_open_to_work": WriteSpec(
        action="set_open_to_work",
        tool_name="linkedin_set_open_to_work",
        # NEVER LOADED. The state is read off the profile topcard, which is on
        # the read allowlist; the EDITOR is a modal opened from that card and
        # no capture of it exists at any hydration state. So there is no url
        # here, and assert_write_url refuses this action outright. Specced
        # rather than left out, because the previous pass left it unspecced and
        # the omission read as an oversight instead of as a missing capture.
        url_template=None,
        url_pattern=None,
        exempt_substring=None,
        summary=(
            "Change who your Open To Work signal is shared with, or turn it "
            "off."
        ),
        from_state=None,
        to_state=None,
        target_kind="self",
        state_from="profile_topcard",
        direction_source=(
            "linkedin_my_profile's open_to_work, read off the profile topcard "
            "at no extra page load. LinkedIn prints the CURRENT AUDIENCE "
            "verbatim next to the label -- 'Open to work <dot> Recruiters "
            "only' -- and it does so at BOTH hydration states, confirmed "
            "against the frozen topcard fixtures and again live on "
            "2026-08-23. So the gate never has to describe the state he is in; "
            "it can quote it."
        ),
        reversibility="reversible: the setting can be changed back or turned off",
        reversibility_measured=True,
        reversibility_class="REVERSIBLE",
        reversibility_evidence=(
            "MEASURED 2026-08-23: the current setting is readable before a "
            "change and would be readable after, off the same card, at both "
            "hydration states -- which is what makes a change checkable at "
            "all. "
            "CORRECTION, 2026-08-24, AND THE OLD SENTENCE IS QUOTED SO THE "
            "MISTAKE IS LEGIBLE. This field used to end: \"The control that "
            "edits it sits on that card and is present in both frozen renders "
            "as aria-label=\\\"Open to\\\".\" THAT WAS FALSE. A census of all "
            "five profile captures measured the \"Open to\" button's menu "
            "resolving to exactly three items -- Hiring, Providing services, "
            "Finding volunteer opportunities -- and NONE of them is the "
            "audience editor; the entry LinkedIn would have used is absent "
            "precisely BECAUSE the setting is already on. The real entry point "
            "is a control whose accessible name is \"Edit\", on the "
            "open-to-work card itself, and it is pinned in both frozen renders "
            "-- so the evidence survives, attached to the right control. A "
            "capture attempt that had started from \"Open to\" would have "
            "failed silently, which is what a gate printing an unverified "
            "evidence line buys."
        ),
        reversible_by=(
            "HIM, in LinkedIn's own interface. Not this server: the editor's "
            "surface has never been loaded, so nothing here can reach it in "
            "either direction."
        ),
        residue=(
            "IRREVERSIBLE IN AUDIENCE, and this is the field that matters "
            "more than the verdict. Switching to All LinkedIn members draws a "
            "green #OpenToWork frame on the photo that a current employer and his "
            "colleagues can see. Taking it down later removes the frame; it "
            "does not un-see it. Second gap: only ONE of the three states has "
            "ever been observed on this account -- 'Recruiters only'. Neither "
            "the all-members state nor the off state has been seen, so the "
            "reader recognises the audience string it has met and refuses to "
            "interpret one it has not."
        ),
        audiences={
            "recruiters only": (
                "visible only to recruiters using LinkedIn Recruiter. No "
                "badge is drawn on your photo. YOUR CURRENT EMPLOYER DOES NOT "
                "SEE IT -- though LinkedIn itself declines to guarantee that "
                "recruiters at your own company are excluded, so this is "
                "quieter rather than secret."
            ),
            "all linkedin members": (
                "PUBLIC. A green #OpenToWork frame is drawn on your profile "
                "photo and everyone who can see your profile can see it, "
                "INCLUDING A CURRENT EMPLOYER AND COLLEAGUES. If you are "
                "job-hunting while employed, this is the one setting in this "
                "whole design an employer can read."
            ),
            "off": (
                "no signal is shared with anyone, and recruiters filtering "
                "for open-to-work candidates stop finding you."
            ),
        },
        reversibility_procedure=(
            "SETTLED for the setting on 2026-08-23 by reading the profile "
            "card. What is NOT settled and cannot be: whether the badge was "
            "seen while it was up. What would have to be measured before this "
            "action could ever be performed is the SURFACE -- the editor has "
            "never been loaded, so there is no url, no anchor, and no capture "
            "of the audience control at any hydration state. "
            "THE ABSENCE OF A URL IS NOW A MEASUREMENT RATHER THAN AN "
            "ADMISSION, taken 2026-08-24: 237 distinct urls and 37 payload "
            "paths were enumerated across all five profile captures and ZERO "
            "reach an open-to-work editor, a job-preferences page or a "
            "career-interests page; the strings 'opentowork' and "
            "'open-to-work' occur zero times anywhere. The editor is not "
            "url-addressed AT ALL -- its screens are addressed by an internal "
            "screen id, and its entry control fires a request whose own name "
            "is saveAndFetchNextStep. So the one click that would first REVEAL "
            "the editor is also the first click that could CHANGE it, which is "
            "why no capture of it may be taken except with him watching."
        ),
    ),
    # -----------------------------------------------------------------
    # THE SEVEN ADDED 2026-08-30, on the standing ruling that whatever is
    # technically possible should be achieved. Each is SANCTIONED -- it may
    # hold a spec, render a gate and refuse in its own words -- and NONE is
    # in PERFORMABLE. That is not a soft version of building them. A spec is
    # what makes an action expressible at all: without one there is no
    # target normalisation, no live read, no reversibility verdict and no
    # place for a refusal to be written down, which is the state all seven
    # were in this morning and is why the server's own instructions said
    # they did not exist.
    #
    # EVERY ONE PERFORMS A REAL LIVE READ. Not a stored sentence: the
    # preview loads a page that is ALREADY on the read allowlist, counts the
    # controls that bear on the capability, and refuses with what it just
    # saw. No boundary was widened to build these -- the four frozen
    # denylists are byte-identical across this change, and that is checkable
    # rather than asserted.
    #
    # WHY NONE OF THEM CARRIES A ``url_template``. Every one of the seven
    # would act on an address that ``readonly._FORBIDDEN_URL_SUBSTRINGS``
    # refuses, or on a control nobody has photographed, or both. ``mint``
    # refuses a grant at ISSUE for a spec with no url, so these cannot hold
    # a confirm token at all -- the operator reads a WARNING rather than an
    # offer, which is exactly what ``set_open_to_work`` has done since
    # August. The blockers are itemised per action in ``_NINE_REFUSALS``.
    "linkedin_publish_post": WriteSpec(
        action="publish_post",
        tool_name="linkedin_publish_post",
        url_template=None,
        url_pattern=None,
        exempt_substring=None,
        summary="Publish a post to your LinkedIn feed, under your own name.",
        from_state="composer_present",
        to_state="post_published",
        target_kind="post_text",
        state_from="feed_composer",
        direction_source=(
            "linkedin_surface_census(feed), taken live by this gate. It reads "
            "three things off the feed and none of them from memory: how many "
            "controls named 'Start a post' are drawn, how many contenteditable "
            "nodes exist, and whether the two url-addressed publish routes are "
            "present. MEASURED 2026-08-30: one composer control, ZERO "
            "contenteditable, and both routes present as real anchors -- "
            "'Write article' pointing at /article/new/ and 'Create a post' at "
            "/preload/sharebox/. The zero is the load-bearing number: the "
            "editor is inside a modal and has never been seen."
        ),
        wrong_state_note=(
            "This is not a toggle and the danger is not the opposite action. "
            "If the composer control is not on the feed, the page either did "
            "not hydrate or LinkedIn has moved it -- and in both cases the "
            "honest answer is that nothing here knows where a post would go."
        ),
        reversibility="STILL-UNKNOWN whether a published post can be deleted",
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "NOT MEASURED, and the shape of the gap is worth stating because "
            "it is the same one the notifications census hit. Each post draws "
            "an overflow control -- 'Open control menu for post by <him>', "
            "measured 8 times on his own profile -- and it renders "
            "aria-expanded='false'. Its ITEMS have never been read. So "
            "whether LinkedIn offers Delete on a post is something this "
            "server has not established, and the notifications precedent is "
            "that an unopened overflow menu is not evidence about what is "
            "inside it."
        ),
        reversible_by=(
            "NOBODY, through this server. Deleting is in "
            "PERMANENTLY_FORBIDDEN ('destruction is not a write this design "
            "covers, at any confirm level') and '/delete' is on the read "
            "boundary's forbidden list. Whatever LinkedIn's product allows, a "
            "post published here is one this server can never take down."
        ),
        residue=(
            "IRREVERSIBLE IN AUDIENCE, and this half is certain even though "
            "the state half is not. A post is BROADCAST: his profile reports "
            "275 followers and LinkedIn's own analytics on that page show "
            "past posts reaching 103, 308 and 1,284 impressions. Deleting a "
            "post -- if it can be deleted -- removes a row; it does not "
            "un-read what several hundred people have already read, and it "
            "does not recall the notification that told them it existed. "
            "SECOND, AND IT IS THE ONE A JOB HUNT SHOULD WEIGH: a post is the "
            "one artefact here a CURRENT EMPLOYER sees without looking."
        ),
        irreversible=True,
        reversibility_procedure=(
            "Open the overflow menu on one of his own posts and read its "
            "items -- the same measurement that settled what the "
            "notifications overflow holds, on a surface already allowed. That "
            "establishes whether a delete affordance exists AT ALL, which is "
            "the question, and it costs one click on his own content with "
            "nothing published. It has not been taken because this wave "
            "performed nothing."
        ),
    ),
    "linkedin_comment_on_item": WriteSpec(
        action="comment_on_item",
        tool_name="linkedin_comment_on_item",
        url_template=None,
        url_pattern=None,
        exempt_substring=None,
        summary=(
            "Publish a comment under one feed item, under your own name."
        ),
        from_state="comment_control_present",
        to_state="comment_published",
        target_kind="item_and_text",
        state_from="feed_item",
        direction_source=(
            "linkedin_surface_census(feed), taken live by this gate, reading "
            "the comment affordance and the item permalinks beside it. "
            "MEASURED 2026-08-30 in BOTH of its shapes, which are not the "
            "same control: a text-named button on /feed/ (count 3) that opens "
            "an inline composer, and an ANCHOR on his profile (count 8) "
            "pointing at /feed/update/<urn>/. The anchor is the only place a "
            "target key has been seen."
        ),
        wrong_state_note=(
            "Not a toggle. A comment is added, never flipped -- so a wrong "
            "reading here does not mean the opposite would happen, it means "
            "nothing on the page tells this gate where the comment would go."
        ),
        reversibility="STILL-UNKNOWN whether a published comment can be deleted",
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "NOT MEASURED. No comment has ever been opened by this server and "
            "no comment's own overflow menu has been read, so whether "
            "LinkedIn offers a delete on one is unestablished -- the same gap "
            "as publish_post and for the same reason."
        ),
        reversible_by=(
            "NOBODY, through this server: deletion is permanently forbidden "
            "here and '/delete' is on the read boundary's forbidden list."
        ),
        residue=(
            "IRREVERSIBLE IN AUDIENCE, and worse than a post's in one "
            "specific way: A COMMENT SITS UNDER SOMEBODY ELSE'S ITEM. It is "
            "published to that item's audience rather than to his followers, "
            "it notifies the author, and it stays attached to their content. "
            "Deleting it later -- if that is even possible -- removes it from "
            "the thread and not from the notification the author already "
            "received."
        ),
        irreversible=True,
        reversibility_procedure=(
            "Two things, and the first is the cheap one: open the overflow "
            "menu on one of his OWN existing comments and read its items. "
            "That settles whether a delete exists without publishing "
            "anything. The second is the boundary question -- whether this "
            "server may load /feed/update/<urn>/ at all -- which is a ruling "
            "and not a measurement."
        ),
    ),
    "linkedin_react_to_item": WriteSpec(
        action="react_to_item",
        tool_name="linkedin_react_to_item",
        url_template=None,
        url_pattern=None,
        exempt_substring=None,
        summary="React to one feed item, under your own name.",
        from_state="no_reaction",
        to_state="reacted",
        target_kind="item_urn",
        state_from="feed_item",
        direction_source=(
            "The CONTROL'S OWN ACCESSIBLE NAME, which on this surface carries "
            "the toggle state: aria-label='Reaction button state: no "
            "reaction'. MEASURED 2026-08-30 across eleven controls -- 3 on "
            "/feed/ and 8 on his profile -- every one of them in the OFF "
            "state. That is the same convention as the follow control and the "
            "unfollow row, and it is the strongest direction source of the "
            "seven: the state and the button are the same object. The gate "
            "reads it live and refuses unless EVERY rendered control agrees, "
            "because a mixed page cannot say which item a direction belongs "
            "to."
        ),
        reversibility="STILL-UNKNOWN whether a reaction can be taken back here",
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "NOT MEASURED, and the distinction is worth keeping sharp because "
            "this one is TEMPTING to call reversible. A control whose "
            "accessible name reports a STATE is almost certainly a toggle, "
            "and almost certainly is not a measurement. THE ON-STATE LABEL "
            "HAS NEVER BEEN SEEN -- all eleven controls read 'no reaction', "
            "because nothing on either surface had been reacted to. This is "
            "the identical position unsave_job has been in since August: the "
            "OFF label is measured, the ON label is not, and the missing half "
            "is not guessed. 'Reaction button state: like' and 'Reaction "
            "button state: liked' are both plausible and neither has been "
            "observed."
        ),
        reversible_by=(
            "UNKNOWN, and not this server in any case: with the ON label "
            "unmeasured there is no selector for the inverse, so nothing here "
            "could aim an un-react even if LinkedIn offers one."
        ),
        residue=(
            "A reaction NOTIFIES THE AUTHOR and can surface in his own "
            "network's feed. Removing it later -- if that is possible -- "
            "takes back the row and not the notification, and not whatever "
            "was shown to whoever saw it. The data is restorable; the "
            "impression is not. That is the same residue the follow action "
            "carries, and it is the reason 'reversible' would be a "
            "half-truth here even once the ON label is known."
        ),
        reversibility_procedure=(
            "React to one item and READ THE LABEL THE CONTROL CHANGES INTO. "
            "That single string settles both halves at once -- it is the "
            "anchor for the inverse action and the evidence that an inverse "
            "exists -- and it can only be taken immediately after a real "
            "reaction on a real account, exactly as the missing half of "
            "shape.SAVE_LABELS can only be taken after a real save. Note the "
            "asymmetry with save: an unreacted item is his to experiment on "
            "only if it is HIS OWN item, and 8 of the 11 measured controls "
            "are on his own posts."
        ),
    ),
    "linkedin_update_profile_field": WriteSpec(
        action="update_profile_field",
        tool_name="linkedin_update_profile_field",
        url_template=None,
        url_pattern=None,
        exempt_substring=None,
        summary="Change one field on your own LinkedIn profile.",
        from_state="editor_addressed",
        to_state="field_changed",
        target_kind="field_and_value",
        state_from="profile_editors",
        direction_source=(
            "His own profile, read live by this gate, counting the editor "
            "ANCHORS on it and the forms the page carries. MEASURED "
            "2026-08-30: three editors addressed by ordinary hrefs -- "
            "/in/<member>/edit/intro/, "
            "/in/<member>/edit/forms/summary/new/ and "
            "/in/<member>/overlay/contact-info/ -- and 2 forms where every "
            "tracked profile fixture carries 0. The gate refuses unless at "
            "least one editor anchor is actually on the page, because a "
            "profile that drew no editor is one this server cannot describe "
            "an edit to."
        ),
        wrong_state_note=(
            "Not a toggle. If no editor anchor rendered, either the page did "
            "not hydrate or LinkedIn has moved the editors again -- and the "
            "second is exactly what happened between the fixtures and the "
            "live page, which is why this reads rather than remembers."
        ),
        reversibility="STILL-UNKNOWN whether an edit made here could be undone",
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "NOT MEASURED. The editors have never been OPENED, so no field, "
            "no save control and no previous-value affordance has been "
            "observed. What is measured is only that the editors have "
            "addresses. An address is not an undo."
        ),
        reversible_by=(
            "HIM, by hand, in LinkedIn's own interface -- and only if he "
            "still knows the previous value, which nothing here records. NOT "
            "this server: '/edit/' is on the read boundary's forbidden list, "
            "so it cannot reach the editor in either direction."
        ),
        residue=(
            "HIS PROFILE IS WHAT RECRUITERS READ, and it is read continuously "
            "rather than at a moment he chooses -- his own profile reports 29 "
            "profile views. An edit that is reverted an hour later was still "
            "live for an hour. And LinkedIn notifies a network about some "
            "profile changes, which is a broadcast this server has not "
            "measured and would not control."
        ),
        reversibility_procedure=(
            "Open one editor and census it: whether it renders the CURRENT "
            "value in its field (which is what makes an edit revertible by "
            "hand at all), what its save control is called, and whether a "
            "cancel exists. That requires loading an address the read "
            "boundary currently forbids, so it is a ruling before it is a "
            "measurement."
        ),
    ),
    "linkedin_update_setting": WriteSpec(
        action="update_setting",
        tool_name="linkedin_update_setting",
        url_template=None,
        url_pattern=None,
        exempt_substring=None,
        summary="Change one LinkedIn account setting.",
        from_state="setting_addressed",
        to_state="setting_changed",
        target_kind="setting_and_value",
        state_from="settings_index",
        direction_source=(
            "The settings surface, read live by this gate, counting how many "
            "settings it ADDRESSES and how many it can switch. MEASURED "
            "2026-08-30: 33 links, ZERO forms, ONE button, and zero "
            "checkboxes, selects or switches. Every setting is its own "
            "address -- /mypreferences/d/settings/language, "
            "/mypreferences/d/dark-mode, /mypreferences/d/categories/privacy. "
            "So this page hands out addresses and switches nothing, and the "
            "value lives one page further down where nothing has looked."
        ),
        wrong_state_note=(
            "Not a toggle at this level. A settings index that drew no links "
            "is a page that did not render, not a signal about any setting."
        ),
        reversibility="STILL-UNKNOWN, and it differs by setting",
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "NOT MEASURED, and a single verdict for 'a setting' would be "
            "false whatever it said. The 33 addresses on that index are not "
            "one kind of thing: 'Dark mode' is a display preference and "
            "'Close and delete account' and 'Hibernate account' are on the "
            "same list. No page below the index has been loaded, so no "
            "control and no confirmation flow has been observed for any of "
            "them."
        ),
        reversible_by=(
            "HIM, in LinkedIn's own interface. NOT this server: "
            "'/mypreferences/d/categories/' and '/settings/' are both on the "
            "read boundary's forbidden list, so the pages carrying the values "
            "are unreachable in either direction."
        ),
        residue=(
            "TWO OF THE THIRTY-THREE ADDRESSES ARE ACCOUNT DESTRUCTION -- "
            "'Close and delete account' and 'Hibernate account' -- and they "
            "sit in the same url family as 'Dark mode'. That is the fact that "
            "should govern any future ruling here: a permission written for "
            "the family would carry those two with it, so a setting has to be "
            "admitted BY NAME or not at all. Separately: some settings "
            "(profile visibility, open-to-work) have an AUDIENCE, and an "
            "audience once shown is not un-shown."
        ),
        reversibility_procedure=(
            "Census ONE NAMED setting page -- not the family -- and read "
            "whether it renders the current value, what the control is, and "
            "whether changing it is confirmed. That needs a boundary ruling "
            "on that one address first."
        ),
    ),
    "linkedin_send_invitation": WriteSpec(
        action="send_invitation",
        tool_name="linkedin_send_invitation",
        url_template=None,
        url_pattern=None,
        exempt_substring=None,
        summary="Send one connection invitation to another LinkedIn member.",
        from_state="invite_control_present",
        to_state="invitation_sent",
        target_kind="member",
        state_from="profile_invitations",
        direction_source=(
            "HIS OWN PROFILE, and choosing that surface is the finding rather "
            "than a detail. The obvious surface for this is /mynetwork/, "
            "which is REFUSED because loading it consumes the "
            "pending-invitation badge -- a cost measured twice in this "
            "package on the two sibling badges. MEASURED 2026-08-30 instead: "
            "9 invitation controls on his own profile, a page this server "
            "already loads and which carries no such counter. So the "
            "capability has a route that costs no badge, and this gate uses "
            "it. The controls are COUNTED and their labels are never read -- "
            "see _NINE_REFUSALS for why that is a rule and not a limitation."
        ),
        wrong_state_note=(
            "Not a toggle. No invitation control on the page means the rail "
            "did not render, not that there is nobody to invite."
        ),
        reversibility="STILL-UNKNOWN whether an invitation can be withdrawn",
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "NOT MEASURED, and it cannot be measured from here. The surface "
            "that would show a withdraw affordance is the sent-invitations "
            "manager, whose address contains 'invitation' and is on the read "
            "boundary's forbidden list -- so this server has never seen it "
            "and holds no evidence either way."
        ),
        reversible_by=(
            "NOBODY, through this server. Withdrawing is destruction, which "
            "is in PERMANENTLY_FORBIDDEN, and '/withdraw' and 'invitation' "
            "are both on the read boundary's forbidden list."
        ),
        residue=(
            "AN INVITATION IS A REQUEST TO A REAL PERSON, and it lands as a "
            "notification with his name on it. Withdrawing one later -- if "
            "LinkedIn permits it, which is unestablished -- removes it from a "
            "pending list; it does not un-notify. There is a second, quieter "
            "cost: LinkedIn restricts accounts whose invitations are "
            "frequently ignored or marked 'I don't know this person', so this "
            "is the one action here whose repetition has a consequence for "
            "the account itself. Nothing readable reports that limit."
        ),
        irreversible=True,
        reversibility_procedure=(
            "Load the sent-invitations manager and look for a withdraw "
            "control on a pending row. That address is forbidden here, so it "
            "is a boundary ruling first; and it needs a pending invitation to "
            "exist, which means the question resolves in one direction only, "
            "exactly as it does for apply."
        ),
    ),
    "linkedin_send_message": WriteSpec(
        action="send_message",
        tool_name="linkedin_send_message",
        url_template=None,
        url_pattern=None,
        exempt_substring=None,
        summary=(
            "Send one message or InMail to another LinkedIn member."
        ),
        from_state="composer_unmeasured",
        to_state="message_sent",
        target_kind="member_and_text",
        state_from="messaging_badge",
        direction_source=(
            "THE NAV BADGE, READ OFF A PAGE ALREADY OPEN, and the restraint "
            "is the point. This gate does NOT load messaging. Loading it is "
            "measured to redirect into one specific conversation of "
            "LinkedIn's choosing -- so the load itself opens somebody's "
            "thread -- and the nav badge counts new-since-last-visit and "
            "resets when the tab is opened. A gate that opened messaging in "
            "order to describe the cost would have spent exactly the thing it "
            "is warning about, on a third party. So it reads the badge, which "
            "IS the counter that would be consumed, and stops. Measured "
            "2026-08-30: 'Messaging, 0 new notifications'. If the surface is "
            "to be measured, he calls linkedin_open_messaging himself."
        ),
        wrong_state_note=(
            "Not a toggle and not a state this gate can improve on. The "
            "composer has never been observed because observing it costs a "
            "stranger's thread, and that cost is his to spend rather than "
            "this gate's."
        ),
        reversibility="STILL-UNKNOWN whether a sent message can be recalled",
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "NOT MEASURED. No thread has been opened by this server for this "
            "purpose and no message control has ever been read, so whether "
            "LinkedIn offers a delete-for-everyone on a sent message is "
            "unestablished here."
        ),
        reversible_by=(
            "NOBODY, through this server: deletion is permanently forbidden "
            "here and '/messaging/compose' is on the read boundary's "
            "forbidden list, so nothing here can reach a composer in either "
            "direction."
        ),
        residue=(
            "A MESSAGE IS READ BY A PERSON, usually within a day, and it "
            "arrives as an email as well as a notification. Recalling it -- "
            "if LinkedIn permits that -- removes it from a thread; it does "
            "not un-send the email and it does not un-read what somebody has "
            "read. This is the most irreversible-in-audience action in the "
            "whole design, and unlike an application it is addressed to a "
            "named individual rather than to a company's process."
        ),
        irreversible=True,
        spends=(
            "POSSIBLY AN INMAIL CREDIT, and that is UNMEASURED rather than "
            "denied. Messaging a member outside his network uses InMail, "
            "which is a metered allowance on Premium Career. This server has "
            "never read his balance: /premium/my-premium/ is not on the read "
            "allowlist and no tool here reports a credit count. So a send "
            "could consume a finite resource whose size is unknown to the "
            "thing spending it, which is its own reason not to perform this "
            "unattended."
        ),
        reversibility_procedure=(
            "He calls linkedin_open_messaging -- the tool that pays the "
            "opened-thread cost knowingly and says so in its own name -- and "
            "the send-surface counts it already returns answer whether a "
            "composer is rendered at all. Then linkedin_open_messaging("
            "message_filter='inmail') for the InMail half. Neither call was "
            "made by this wave, deliberately: the cost lands on somebody who "
            "is not him."
        ),
    ),
}


# ---------------------------------------------------------------------------
# 2. Permanently forbidden
# ---------------------------------------------------------------------------

#: No grant is ever minted for these, and each carries its reason so a later
#: reader does not mistake the omission for something nobody got round to.
#
# THREE ENTRIES WERE REWRITTEN OR REMOVED ON 2026-08-30 AND THE OLD TEXT IS
# QUOTED IN EACH, because the reason they went is the point. The operator
# dissolved the POLICY bucket: a refusal survives here only if the thing is
# IMPOSSIBLE with a measurement behind it, or if performing it would be
# unattended -- taste and discomfort are not grounds, and three of these were
# nothing else.
PERMANENTLY_FORBIDDEN: dict[str, str] = {
    "repost_or_share": (
        "NARROWED 2026-08-30 from an entry that read 'post_or_comment_or_like_"
        "or_share: public speech in his name, unbounded blast radius, no "
        "job-hunt value'. Three quarters of that entry is gone because its "
        "ground was TASTE and the operator dissolved that bucket: posting, "
        "commenting and reacting are now sanctioned specs behind the gate, "
        "each refusing on a measured blocker rather than on distaste. What "
        "survives is the fourth: a repost republishes SOMEBODY ELSE'S item to "
        "his network under his name, so the thing broadcast is not his and "
        "the audience is. Measured beside the others -- 'Repost' is a button "
        "with aria-expanded='false', 3 on the feed and 8 on his profile, and "
        "its menu has never been opened, so what a repost even offers is "
        "unobserved. It was not among the capabilities asked for, and it is "
        "not quietly added here"
    ),
    "endorse_or_recommend": (
        "REASON REPLACED 2026-08-30. It used to read 'a statement ABOUT "
        "ANOTHER PERSON, which is not his to automate' -- which was POLICY, "
        "and was overtaken by the operator's own 2026-08-25 ruling that an "
        "endorsement is a gift to the person receiving it rather than an "
        "extraction from them. The refusal survives on a MEASUREMENT instead, "
        "and the measurement was re-taken the day the reason changed: zero "
        "endorse controls across 13 tracked fixtures with zero shaping "
        "blindness, zero on his own skills surface, and zero among the 222 "
        "controls read live on his own profile on 2026-08-30. You cannot "
        "endorse yourself, so the only surface that would carry the control "
        "is a THIRD PARTY'S PROFILE -- and loading one leaves them a durable "
        "record, which this package measures from the receiving end with "
        "linkedin_who_viewed_me. IMPOSSIBLE AS SPECIFIED, not unwanted"
    ),
    "deanonymise_a_viewer": (
        "six of ten profile viewers chose anonymity; the row LinkedIn renders "
        "him is the whole of what he is entitled to"
    ),
    "load_a_third_partys_profile_to_measure_a_control": (
        "ADDED 2026-08-30, and it is the rule the endorsement ruling above "
        "rests on rather than a restatement of it. A profile view is an "
        "EMISSION, and this server can read the receiving end of that signal: "
        "linkedin_who_viewed_me returns rows, reaching 365 days back on his "
        "Premium Career account, and every row is somebody who loaded a "
        "profile and left a record its owner can still read most of a year "
        "later. So loading a stranger's profile in order to find out what "
        "controls it carries spends THEIR privacy on OUR measurement, and the "
        "cost lands entirely on somebody who is not him. Whether HE chooses "
        "to open a profile is his own affair; this server may not do it for a "
        "measurement"
    ),
    "delete_or_withdraw_anything": (
        "destruction is not a write this design covers, at any confirm level. "
        "NOTE WHAT NOW DEPENDS ON THIS ENTRY, added 2026-08-30 and CORRECTED "
        "the same day after a review counted it: FIVE of the specs above cite "
        "it in reversible_by -- an application, a post, a comment, an "
        "invitation and a message all say NOBODY can take them back through "
        "this server, and this line is the reason. Shortening it would "
        "silently make five reversibility claims wrong at once. The list first "
        "written here named a REACTION and omitted an APPLICATION, which was "
        "wrong in both directions at once; react_to_item does not lean on this "
        "entry at all, because its reversible_by rests on a different gap -- "
        "the ON-state label has never been observed, so there is no selector "
        "for the inverse whatever this list says"
    ),
    "mark_notifications_read": (
        "clearing his unread badge destroys signal he has not seen, and the "
        "act is server-side on page serve so it cannot even be confirmed "
        "first. SECOND GROUND, MEASURED 2026-08-24 and independent of the "
        "first: THERE IS NOTHING TO CLICK AND NOTHING TO AIM AT. A census of "
        "the notifications surface found 34 activatable controls across 6 "
        "cards and not one of them changes read state; the per-card overflow "
        "menu is present in the DOM before activation and holds exactly three "
        "distinct items (change preferences, delete, show less like this). No "
        "notification carries an id of any kind, so even a hypothetical "
        "control would have no target. THIRD: the read tool ALREADY has the "
        "full effect -- opening the page clears the badge -- so a write here "
        "could only ever run after its own consequence had landed"
    ),
    "auto_accept_or_auto_reply": (
        "a reply in his name that he did not read is a message from a stranger "
        "wearing his face"
    ),
    "any_loop_sweep_or_scheduled_write": (
        "one write per invocation, always. The grant TTL makes an unattended "
        "write structurally impossible and that is the intended consequence"
    ),
    "any_anti_detection_technique": (
        "performing a confirmed action and evading detection are different "
        "activities; the launch boundary never moves for a write"
    ),
    # REMOVED 2026-08-30: "profile_edit_beyond_open_to_work: his profile is a
    # document he owns; silently editing it is a category error, not a
    # feature." Every word of that is about TASTE, and the word doing the work
    # is "silently" -- which describes an unattended edit, not this design. An
    # edit here is two calls, the second carrying a single-use token minted
    # from a preview that printed the field and the value. It is the opposite
    # of silent. So the entry was not merely dissolved along with the policy
    # bucket; it was arguing against something this server does not do.
    #
    # The capability is now the ``update_profile_field`` spec above, sanctioned
    # and NOT performable, refusing on two measured blockers: '/edit/' is on
    # the read boundary's forbidden list, and no field inside any editor has
    # ever been observed. That is a refusal with a fix attached, which the
    # entry it replaced was not.
}


# ---------------------------------------------------------------------------
# 3. The grant
# ---------------------------------------------------------------------------


@dataclass
class WriteGrant:
    """Permission to perform ONE action, on ONE target, ONCE, soon.

    Held in memory only and never written to disk: a grant that outlived the
    process would be a grant a scheduler could pick up, and no scheduler may
    ever hold one.
    """

    action: str
    target: str
    token: str
    minted_at: float
    consumed: bool = False
    preview: dict[str, Any] = field(default_factory=dict)
    #: The reading this grant was minted from. Not decoration: it is the only
    #: durable evidence that a grant came from a preview that looked, and the
    #: future :func:`perform` reads it to refuse a grant whose reading has
    #: gone stale even though the grant itself has not.
    observation: Optional["Observation"] = None

    def age(self) -> float:
        return time.monotonic() - self.minted_at

    def expired(self) -> bool:
        return self.age() > GRANT_TTL_SECONDS


#: Live grants by token. Process-local by construction.
_GRANTS: dict[str, WriteGrant] = {}


def mint(action: str, target: str, *, receipt: str) -> WriteGrant:
    """Issue a single-use grant, and ONLY against a live read receipt.

    "Only a PREVIEW may call this" used to be the whole of the enforcement,
    written in this docstring. It is now the signature: there is no way in
    without a ``receipt``, receipts exist only in :data:`_OBSERVED`, and the
    only function that puts one there is :func:`observe`, which loads pages.

    TWO REFUSALS THAT WERE NOT HERE BEFORE, both found by a cold review on
    2026-08-23:

    * **A SURFACE-LESS ACTION GETS NO GRANT AT ALL.** ``set_open_to_work`` has
      no ``url_template`` -- its editor has never been loaded -- and yet a
      grant for it could be minted and consumed, with ``assert_write_url`` the
      single thing standing between it and a navigation. An invariant enforced
      only at the point of use is one a future click has to remember; this
      enforces it at issue. A grant is permission to ACT, and there is nothing
      to act on.
    * **THE TARGET IS CHECKED AGAINST THE ACTION'S OWN SHAPE**, not against
      ``isdigit`` alone. That check read "a grant needs a numeric target id",
      which for a profile setting was simply false, so the only grant Open To
      Work could ever hold was a job-id grant for something that is not a job.
    """
    if not writes_enabled():
        raise WriteAttemptError(
            f"writes are disabled: set {WRITES_FLAG}=1 to enable them. This "
            "server is read-only unless that flag is set deliberately."
        )
    if action not in {spec.action for spec in SANCTIONED_WRITES.values()}:
        raise WriteAttemptError(
            f"{action!r} is not a sanctioned write. The complete set is "
            f"{sorted(spec.action for spec in SANCTIONED_WRITES.values())}."
        )
    spec = spec_for_action(action)
    if spec.url_template is None:
        raise WriteAttemptError(
            f"no grant is minted for {action!r}: its surface has never been "
            "loaded by this server, so there is no page for a grant to be "
            "permission to act on. Refused at ISSUE rather than only at use, "
            "because an invariant a future click has to remember to check is "
            "not an invariant."
        )
    target = _target_for(spec, target)
    observation = _take_observation(receipt, spec=spec, target=target)
    grant = WriteGrant(
        action=action,
        target=target,
        token=secrets.token_urlsafe(24),
        minted_at=time.monotonic(),
        observation=observation,
    )
    _GRANTS[grant.token] = grant
    return grant


def consume(token: str, *, action: str, target: str) -> WriteGrant:
    """Redeem a token for the ONE action and target it was minted against.

    Every refusal below is a way a write could otherwise happen that the
    operator did not confirm: a stale token, a replayed one, a token minted for
    a different posting, a token minted for a different verb, or a caller
    passing something that was never a token at all.
    """
    if not writes_enabled():
        raise WriteAttemptError("writes are disabled")
    if not isinstance(token, str) or not token:
        raise WriteAttemptError(
            "no confirm token. A write performs nothing until it is handed the "
            "token from its own preview -- a boolean cannot stand in, because "
            "a boolean can be set by a caller that never saw a preview."
        )
    grant = _GRANTS.get(token)
    if grant is None:
        raise WriteAttemptError("unknown or already-discarded confirm token")
    if grant.consumed:
        raise WriteAttemptError(
            "this confirm token has already been used. Grants are single-use, "
            "so a replayed confirmation performs nothing."
        )
    if grant.expired():
        _GRANTS.pop(token, None)
        raise WriteAttemptError(
            f"this confirm token expired after {GRANT_TTL_SECONDS:.0f}s. Run "
            "the preview again and read it before confirming."
        )
    if grant.action != action:
        raise WriteAttemptError(
            f"token was minted for {grant.action!r}, not {action!r}"
        )
    if grant.target != str(target):
        raise WriteAttemptError(
            f"token was minted for target {grant.target!r}, not {str(target)!r}"
        )
    grant.consumed = True
    _GRANTS.pop(token, None)
    return grant


def discard_all() -> None:
    """Drop every live grant AND every live reading.

    Both, because they are two halves of the same permission: a receipt that
    outlived a kill switch is a grant waiting to be minted.
    """
    _GRANTS.clear()
    _OBSERVED.clear()


# ---------------------------------------------------------------------------
# 4. The separate door
# ---------------------------------------------------------------------------


def assert_write_url(url: str, grant: WriteGrant) -> str:
    """Return ``url`` only if it is THIS grant's own target. Else raise.

    Deliberately not a relaxation of :func:`readonly.assert_read_url`, which is
    untouched. This is a second, narrower door: the url is REBUILT from the
    grant and compared, so a caller cannot hand in a url at all -- there is
    nothing for a caller to influence.
    """
    from linkedin_server import readonly

    spec = spec_for_action(grant.action)
    if spec.url_template is None or spec.url_pattern is None:
        raise WriteAttemptError(
            f"write blocked: {grant.action!r} has no measured surface. Its "
            "editor has never been loaded by this server, so there is no url "
            "to rebuild and no anchor to aim at. A gate may not name a target "
            "surface nobody has opened, for the same reason it may not print "
            "an unmeasured reversibility claim -- and inventing a plausible "
            "path here is exactly the confident string that rule exists to "
            "stop. Capture the surface first."
        )
    expected = spec.url_template.format(target=grant.target)
    if url != expected:
        raise WriteAttemptError(
            f"write blocked: {url!r} is not this grant's target. A write url "
            f"is rebuilt from the grant ({expected!r}), never accepted from a "
            "caller."
        )
    if not spec.url_pattern.match(url):
        raise WriteAttemptError(f"write blocked: {url!r} fails its own pattern")

    # The forbidden list is NOT shortened for writes. Each action may exempt
    # exactly one entry, by equality, and everything else still refuses.
    lowered = url.lower()
    for bad in readonly._FORBIDDEN_URL_SUBSTRINGS:
        if bad in lowered and bad != spec.exempt_substring:
            raise WriteAttemptError(
                f"write blocked: {url!r} contains {bad!r}, which this action "
                f"does not exempt (it exempts {spec.exempt_substring!r})"
            )
    return url


def spec_for_action(action: str) -> WriteSpec:
    for spec in SANCTIONED_WRITES.values():
        if spec.action == action:
            return spec
    raise WriteAttemptError(f"{action!r} is not a sanctioned write")


# ---------------------------------------------------------------------------
# 5. The read the gate performs FOR ITSELF
# ---------------------------------------------------------------------------
#
# THE RULE THIS SECTION EXISTS FOR is one the design already stated and did
# not enforce:
#
#     A GRANT IS MINTED ONLY BY A PREVIEW THAT RE-READ THE TARGET LIVE.
#
# Until 2026-08-23 that sentence was a docstring. The renderer took the
# measured ``state`` and the target's ``facts`` as ARGUMENTS, so a caller
# could hand it a direction nobody had read and get back a confident gate
# naming a posting that does not exist. Measured at oldsha14, before the fix:
#
#     render_preview(follow_company,
#                    facts={"title": "a title I made up",
#                           "company": "a company I made up"},
#                    state="not_following")
#         -> where    : a title I made up / a company I made up
#            direction: not_following -> following
#            reversibility: reversible by unfollowing
#
# That is the SAME failure as a boolean standing in for a confirm token, one
# level down, and it takes the same fix. A boolean can be set by a caller that
# never saw a preview; A STATE STRING CAN BE TYPED BY A CALLER THAT NEVER
# PERFORMED A READ. So the state now arrives as a RECEIPT that only a real
# read can mint, and :func:`preview` performs that read itself -- there is no
# parameter left through which a caller can supply either half.
#
# TWO SHAPES, AND THE GATE PRINTS WHICH ONE IT USED. They are different
# promises, and flattening them would be the same species of confident string
# this module keeps refusing to print:
#
#   FOLLOW  -- the state is on the VERY PAGE the action would act on, read
#              from the control's own accessible name at no extra page load.
#              The state and the action share a rendering. That is the ideal
#              shape and it is available for exactly one of the four.
#   SAVE    -- the state comes from ``linkedin_saved_jobs``, a DIFFERENT
#              surface. Originally because the save control's ON state did not
#              exist on this account to read; since 2026-08-30 both labels are
#              measured and the split is a choice -- LIST MEMBERSHIP is what a
#              save changes, and the button reports what a click would do. It
#              costs a second page load and it can answer "I could not tell",
#              which the button never needs to. Measured 2026-08-30, that is
#              no longer hypothetical: the list read is the failing half while
#              the button reads cleanly.
#   OPEN TO WORK -- a third surface again, his own profile topcard.

#: How long an observation stays redeemable. Much shorter than the grant TTL,
#: and deliberately so: a grant is a HUMAN holding a confirmation and is
#: allowed to be two minutes old, while an observation is a READING OF
#: LINKEDIN and a reading goes stale the moment anything else touches the
#: account. Nothing today holds one across a call -- :func:`preview` mints and
#: redeems it in the same breath -- so this is a ceiling on a future edit that
#: tries to, not a live constraint.
OBSERVATION_TTL_SECONDS = 30.0

#: What a read says when it will not answer. Spelled once, because three
#: layers have to agree that "could not tell" is a real answer rather than a
#: falsy stand-in for "no".
UNKNOWN = "unknown"

#: Where each state is read. Built from these constants and from the SPEC's
#: own url template -- never from anything a caller passed -- which is the
#: same discipline :func:`assert_write_url` applies to a write url.
SAVED_LIST_URL = "https://www.linkedin.com/jobs-tracker/?stage=saved"
PROFILE_URL = "https://www.linkedin.com/in/me/"
#: Manage Pages. The one surface in this design where the state is read off the
#: SAME page the click lands on AND the click is anchored to a row rather than
#: to the whole page.
FOLLOWED_PAGES_URL = "https://www.linkedin.com/mynetwork/network-manager/company/"

#: The two surfaces the seven sanctioned-and-refusing actions read, both
#: ALREADY on the read allowlist before this wave and neither widened for it.
#: The feed is loaded here for the same reason ``linkedin_auth_status`` loads
#: it -- it is the cheapest signed-in page -- and the settings index is the one
#: admitted on 2026-08-30's side-effect ruling.
#:
#: WHAT THE SETTINGS URL ACTUALLY REACHES, measured 2026-08-30 and recorded
#: because it surprised the ruling that admitted it: LinkedIn REDIRECTS
#: ``/mypreferences/d/`` to ``/mypreferences/d/categories/account``, which is a
#: url ``readonly._FORBIDDEN_URL_SUBSTRINGS`` refuses. ``assert_read_url``
#: gates the REQUESTED url and the landed url is never re-checked, so the
#: forbidden entry added that same day does not stop this. That is the same
#: shape as the ``/messaging/`` redirect this package already documents, and
#: it is reported rather than papered over: the second gate is a gate on what
#: is ASKED FOR, not on where LinkedIn takes you.
FEED_URL = "https://www.linkedin.com/feed/"
SETTINGS_URL = "https://www.linkedin.com/mypreferences/d/"

#: ONE job posting, as a READ. Named separately from any spec's
#: ``url_template`` and used by exactly one action -- ``apply_job``, which has
#: NO write surface at all and must still be able to look at the posting in
#: order to say why it will not act. Keeping it distinct is the whole point: a
#: read url borrowed as a write template is how an action with no measured
#: surface acquires one by accident.
JOB_POSTING_URL = "https://www.linkedin.com/jobs/view/{target}/"

#: Rows to harvest from the saved list. Generous on purpose: this is not a
#: display limit, it is how much of the list the reconciliation gets to see,
#: and a harvest capped below LinkedIn's own count would MANUFACTURE the
#: "partial list" answer instead of measuring it.
SAVED_LIST_MAX_ROWS = 150


@dataclass(frozen=True)
class Observation:
    """What ONE live read actually saw, and the receipt proving it happened.

    An Observation a caller builds by hand is INERT: it is redeemable only
    while its ``receipt`` is live in :data:`_OBSERVED`, and the only function
    that puts one there is :func:`observe`, which loads pages. That is the
    whole mechanism. It is not a strong claim about a hostile caller -- one
    that fakes the browser is faking the world, and no gate defends against
    that -- it is a claim about the failure that actually happened here: a
    plausible state string, typed by a caller that never looked.
    """

    target: str
    target_kind: str
    #: What the operator can actually CHECK. An id is not something a person
    #: can verify; a job title and an employer are, and so is his own name.
    facts: dict[str, Any]
    #: The url the facts were read from. RECORDED rather than assumed, because
    #: "the page I loaded" and "the page I meant to load" differ exactly when
    #: it matters.
    facts_url: str
    state: str
    #: WHY the state is what it is, including why it is ``unknown``. The read
    #: layer already returns a reason, and dropping it here would collapse
    #: several distinguishable failures back into one word.
    state_why: str
    state_url: str
    #: True only when the state was read off the very page the action would
    #: act on.
    same_page_as_action: bool
    receipt: str
    observed_at: float

    def age(self) -> float:
        return time.monotonic() - self.observed_at

    def expired(self) -> bool:
        return self.age() > OBSERVATION_TTL_SECONDS


#: Live observations by receipt. Process-local, never written to disk, and
#: written to by exactly ONE function -- ``tests/test_writes.py`` asserts that
#: by walking this module's own syntax tree.
_OBSERVED: dict[str, Observation] = {}


#: The longest target string this module will normalise. THIS SERVER'S cap and
#: not LinkedIn's -- LinkedIn's own limits on a post, a comment and an InMail
#: have never been measured here, and citing one would be inventing a number.
#: What the ceiling is actually for is bounding a string that ends up inside a
#: grant, a confirm block and several error messages.
MAX_TARGET_CHARS = 3000

#: How a two-part target is spelled once it is canonical. The separator has to
#: be stable, printable and the same on both calls, because the WHOLE canonical
#: string is what ``consume`` compares -- which is how content gets bound to a
#: token without a second mechanism being invented for it. Change this and
#: every live grant stops matching, which is the correct failure.
TARGET_JOIN = " :: "

#: Targets that are ONE opaque string this server has never measured the shape
#: of, and says so rather than validating a guessed one.
_OPAQUE_TARGET_KINDS: frozenset[str] = frozenset({"item_urn", "member"})

#: Targets made of a SUBJECT and the CONTENT that would be published or set.
#: Mapped to the two argument names each takes, so the error a caller reads
#: names its own fields rather than a generic pair.
_COMPOSITE_TARGET_KINDS: dict[str, tuple[str, str]] = {
    "post_text": ("text", ""),
    "item_and_text": ("item", "text"),
    "field_and_value": ("field", "value"),
    "setting_and_value": ("setting", "value"),
    "member_and_text": ("member", "text"),
}


def _clean_target_part(spec: WriteSpec, name: str, value: Any) -> str:
    """One component of a target, checked for the things that ARE checkable."""
    text = str(value if value is not None else "").strip()
    if not text:
        raise WriteAttemptError(
            f"{spec.action!r} needs {name!r} and got {value!r}. An empty "
            "component would make two different targets canonicalise to the "
            "same string, and the whole canonical string is what binds a "
            "confirm token to what it was minted for."
        )
    if len(text) > MAX_TARGET_CHARS:
        raise WriteAttemptError(
            f"{spec.action!r} was given {len(text)} characters for {name!r} "
            f"and this server normalises at most {MAX_TARGET_CHARS}. The cap "
            "is this server's, not LinkedIn's -- nobody here has measured "
            "LinkedIn's."
        )
    if TARGET_JOIN in text:
        raise WriteAttemptError(
            f"{spec.action!r} was given {TARGET_JOIN!r} inside {name!r}. That "
            "is the separator a two-part target is canonicalised with, so a "
            "component containing it could make two different targets produce "
            "one canonical string -- and a token bound to an ambiguous target "
            "is bound to nothing."
        )
    if any(character in text for character in "\r\n\t"):
        raise WriteAttemptError(
            f"{spec.action!r} was given a control character inside {name!r}. A "
            "target ends up inside a confirm block a human reads and inside "
            "an error message, and a newline in either is how a reader is "
            "shown one thing while another is bound."
        )
    return text


def _opaque_target(spec: WriteSpec, raw: str) -> str:
    """A single-component target whose SHAPE this server has never measured.

    THIS DECLINES TO VALIDATE, AND THAT IS THE HONEST ANSWER RATHER THAN A
    GAP. A feed item is addressed by a urn and a member by a slug, and this
    server has read NEITHER unshaped: ``linkedin_surface_census`` substitutes
    ``<urn>`` and ``<member>`` out before anything is counted, deliberately,
    so that a census cannot publish an identifier. So the exact form is
    unmeasured, and a normaliser that enforced ``urn:li:activity:<digits>``
    would be doing precisely what this package refuses to do with a selector:
    asserting a shape nobody has seen.

    WHY ACCEPTING IT IS SAFE TODAY. Both actions that use this hold no
    ``url_template``, so :func:`mint` refuses them a grant at ISSUE and no
    target of this kind can ever reach a navigation or a click. If either is
    ever made performable, THIS FUNCTION IS THE FIRST THING THAT MUST CHANGE,
    and the measurement that would let it is one unshaped read of a permalink
    href.
    """
    return _clean_target_part(spec, spec.target_kind, raw)


def _composite_target(spec: WriteSpec, target: Any) -> str:
    """A target made of a subject and the content that would be published.

    CONTENT IS PART OF THE TARGET, and that is the whole mechanism by which a
    confirm token is bound to the words it was shown for. There is no second
    gate: :func:`consume` already refuses a token whose ``target`` does not
    match, and the tool rebuilds the same canonical string from the same
    arguments on both calls -- so changing the text between the preview and
    the confirmation produces "token was minted for target X, not Y" for free.

    Without this, a caller could read a preview of one comment and confirm a
    different one, which is the same class of hole as a boolean standing in
    for a token: the thing the human approved and the thing that happens would
    be joined by nothing but good intentions.
    """
    first, second = _COMPOSITE_TARGET_KINDS[spec.target_kind]
    if not second:
        value = target
        if isinstance(target, dict):
            value = target.get(first)
        return _clean_target_part(spec, first, value)
    if not isinstance(target, dict):
        raise WriteAttemptError(
            f"{spec.action!r} is addressed by {first!r} AND {second!r} "
            f"together, so its target is a mapping of the two, not "
            f"{type(target).__name__}. The content is part of the target on "
            "purpose: it is what binds a confirm token to the exact words the "
            "preview showed."
        )
    return (
        _clean_target_part(spec, first, target.get(first))
        + TARGET_JOIN
        + _clean_target_part(spec, second, target.get(second))
    )


def _target_for(spec: WriteSpec, target: Any) -> str:
    """Normalise ``target`` to the shape THIS action is addressed by, or raise.

    Two kinds, because the four actions are not all addressed the same way and
    pretending they were produced a real defect: before this existed, the only
    grant ``set_open_to_work`` could hold was a JOB-ID grant for a profile
    setting, and the block the operator read printed a ``job_id`` for it.
    """
    raw = str(target if target is not None else "").strip()
    if spec.target_kind == "job_id":
        if not raw.isdigit() or len(raw) < 6:
            raise WriteAttemptError(
                f"{spec.action!r} is addressed by a numeric LinkedIn job id, "
                f"got {target!r}. The read url is built from that integer, "
                "which is why it may not be a string a caller chose."
            )
        return raw
    if spec.target_kind == "company_id":
        # THE NUMERIC ID AND NOT THE NAME, though the name is what the control
        # this acts on says out loud. A display name is chosen by somebody
        # else, collides, and changes; the id is the only stable key the
        # surface offers, and the row must carry it for the click to be
        # anchored at all. The gate still PRINTS the name -- an id is not
        # something a person can check.
        if not raw.isdigit() or len(raw) < 4:
            raise WriteAttemptError(
                f"{spec.action!r} is addressed by the numeric LinkedIn company "
                f"id, got {target!r}. Call linkedin_followed_companies to read "
                "the id beside each Page you follow. A name is not accepted "
                "here: names collide and are not yours to rely on, and the "
                "click is anchored to the row carrying the id."
            )
        return raw
    if spec.target_kind == "self":
        if raw.casefold() not in {"self", "me", ""}:
            raise WriteAttemptError(
                f"{spec.action!r} acts on YOUR OWN PROFILE and takes no id, so "
                f"{target!r} names nothing. Pass 'self'."
            )
        return "self"
    if spec.target_kind in _OPAQUE_TARGET_KINDS:
        return _opaque_target(spec, raw)
    if spec.target_kind in _COMPOSITE_TARGET_KINDS:
        return _composite_target(spec, target)
    raise WriteAttemptError(
        f"{spec.action!r} declares target_kind {spec.target_kind!r}, which "
        "this module has no way to address."
    )


async def _load(navigator: Any, page: Any, url: str, *, surface: str) -> str:
    """Open one allowlisted READ url and return where we actually landed.

    THE PREVIEW IS A READ, so it goes through the READ door -- the same
    ``assert_read_url`` every read tool uses, unrelaxed and still a zero-line
    diff. It is checked HERE as well as inside the navigator so that a
    navigator which skipped it (a test's, a future refactor's) still cannot
    point this module at a surface the allowlist refuses.
    """
    from linkedin_server import readonly
    from linkedin_server.auth import assert_not_authwall

    readonly.assert_read_url(url)
    landed = str(await navigator.goto(page, url) or url)
    assert_not_authwall(landed, surface=surface)
    return landed


async def _read_posting_facts(
    page: Any, target: str, *, navigator: Any = None
) -> dict[str, Any]:
    """The title and employer of one posting, off the posting itself.

    Held to the SAME believability standard as ``linkedin_job_detail``: a
    shell that never drew the job still carries a server-rendered document
    title, so a title with no body is not a posting. A gate built on one would
    name a job that was not on the page.
    """
    reading = await dom.read_job_posting(page)
    detail = reading["detail"]

    # THE SAME READER AS ``linkedin_job_detail``, and that is now enforced by
    # there being one of it. What differs here is the REQUIREMENT, declared as
    # data: this gate additionally needs the employer, because a confirm block
    # that cannot name the company is a block he cannot check the job against.
    #
    # That extra requirement is currently IMPLIED rather than independent --
    # see shape.JOB_DETAIL_REQUIRED_FOR_GATE -- and it used to be written here
    # as ``or not detail.get("company")``, a clause that could never decide
    # anything and was twice mistaken for evidence that the two read paths had
    # different strictness. Declaring it is honest; the dead clause was not.
    missing = shape.job_detail_missing(
        detail, require=shape.JOB_DETAIL_REQUIRED_FOR_GATE
    )
    if missing:
        raise WriteAttemptError(
            f"refusing to render a confirm gate for job {target}: the posting "
            "page loaded but no posting could be read from it. A gate naming a "
            "job it did not actually read is the failure this section exists "
            "to stop. "
            + shape.job_detail_failure_note(
                missing,
                main_present=reading["main_present"],
                main_chars=reading["main_chars"],
                # THE GATE INHERITS THE READINESS FIX FOR FREE, which is the
                # half of it that matters most: the apply and save confirm
                # gates read the SAME page through the SAME reader, so a gate
                # refusing here now says whether it looked too early or
                # whether the page really never drew. ``navigator`` is
                # optional only so a test may drive this without a browser;
                # in production it is BROWSER and it is always passed.
                description_wait=reading["description_wait"],
                settle=dict(getattr(navigator, "last_settle", None) or {}),
            )
        )
    return {"title": detail.get("title"), "company": detail.get("company")}


async def _read_follow_state(page: Any) -> tuple[str, str]:
    """The follow direction, off the control on the page already open."""
    control = await dom.read_follow_control(page)
    verdict = shape.follow_state(
        control.get("label"), count=int(control.get("count") or 0)
    )
    return str(verdict.get("state") or UNKNOWN), str(verdict.get("why") or "")


async def _read_followed_state(
    page: Any, target: str
) -> tuple[dict[str, Any], str, str]:
    """Does he follow company ``target``, and what is that company CALLED?

    Returns the facts as well as the state because on this surface they come
    from the same read: the row's own button says ``Click to stop following
    <Page>``, so the name a human can check arrives attached to the id the
    click is anchored to, and neither can be another row's.

    THE RECONCILIATION IS THE POINT, and it is inherited rather than
    reimplemented -- ``shape.parse_followed_pages`` already refuses to call a
    partial list complete, and this surface is never complete: measured across
    five captures, LinkedIn renders 20 rows under a heading stating 58, with
    no pagination control of any kind. So "his Page is not in the rows that
    drew" is ``unknown`` and not ``not_following``, which for an UNFOLLOW is
    the safe direction twice over -- it refuses rather than clicking, and it
    refuses rather than telling him he does not follow somebody he does.
    """
    rows = await dom.harvest_followed_pages(page)
    parsed = shape.parse_followed_pages(rows, await dom.read_main_text(page))
    verdict = shape.followed_page_state(target, parsed)
    matched = verdict.get("matched") or {}
    facts = {
        "company": matched.get("name"),
        "company_id": matched.get("id"),
        "rendered": parsed.get("rendered"),
        "total_followed": parsed.get("total_followed"),
    }
    return facts, str(verdict.get("state") or UNKNOWN), str(verdict.get("why") or "")


async def _read_apply_route(page: Any, target: str) -> tuple[str, str]:
    """Which way this posting is applied to, off the posting already open.

    Not a toggle state -- a ROUTE. The gate's ``from_state`` for apply is the
    route it is willing to act on, so the same machinery that refuses to save
    an already-saved posting refuses to apply through a path nobody has
    identified. See ``shape.apply_route`` for why the classification demands
    several fields agreeing rather than the one obvious one.
    """
    control = await dom.read_apply_control(page)
    verdict = shape.apply_route(
        control.get("label"),
        control.get("href"),
        count=int(control.get("count") or 0),
        job_id=target,
        link_target=control.get("link_target"),
    )
    return str(verdict.get("route") or UNKNOWN), str(verdict.get("why") or "")


async def _read_saved_state(
    page: Any, target: str, *, navigator: Any = None
) -> tuple[str, str]:
    """Is THIS posting in his saved list? Three answers, and the third is real.

    This is the Manage-Pages discipline applied to a second surface, and it is
    the half of the save gate most likely to be loosened later. ABSENCE FROM A
    PARTIAL LIST IS NOT ABSENCE. The tracker loads one page and does not
    scroll, so "I did not see it" is only "it is not there" when LinkedIn's own
    per-tab count agrees the whole list was drawn.

    The reconciliation refuses in BOTH directions. Fewer rows than the stated
    count means the rest are below the fold; MORE rows than the stated count
    means something that is not a saved job is being read as one, and a list
    that disagrees with itself cannot settle a direction either way.

    THE GATE INHERITS THE TRACKER'S READINESS WAIT, and on this surface it
    matters more than on the read tool: ``unsave_job`` takes its DIRECTION from
    this function, so a list read before it drew does not merely produce an
    empty answer, it produces ``unknown`` and the gate refuses. Measured
    2026-08-30, that is exactly what the operator met.
    """
    list_wait = await dom.wait_for_tracker_list(page)
    main_text = await dom.read_main_text(page)
    stated = shape.parse_tracker_tabs(main_text).get("saved")
    empty_state = shape.tracker_empty_state(main_text)

    records = await dom.harvest_linked_cards(
        page, href_pattern=dom.JOB_HREF, max_items=SAVED_LIST_MAX_ROWS
    )
    rows, dropped = dom.parse_all(records, shape.parse_job_card)
    ids = {str(row.get("job_id")) for row in rows if row.get("job_id")}

    if stated is None:
        return (
            UNKNOWN,
            "LinkedIn's own Saved tab count could not be read, so the rows "
            "that did render have nothing to be reconciled against and a "
            "posting absent from them may simply be one that was not drawn.",
        )
    if len(rows) > stated:
        return (
            UNKNOWN,
            f"{len(rows)} rows were read while LinkedIn's own Saved tab says "
            f"{stated}. More rows than the page claims means something that is "
            "not a saved job is being parsed as one, and a list that disagrees "
            "with itself cannot settle a direction.",
        )
    if target in ids:
        return (
            "saved",
            f"this posting is one of the {len(rows)} rows LinkedIn rendered in "
            f"the Saved tab, whose own count for that tab is {stated}.",
        )
    if not rows:
        if shape.empty_is_believable(
            linkedin_count=stated, empty_state=empty_state
        ):
            return (
                "not_saved",
                "the Saved tab is EMPTY and corroborated empty: LinkedIn's own "
                f"count for it reads {stated} and the page drew its empty state "
                f"({empty_state!r}). An empty list contains nothing, so this "
                "posting is not in it.",
            )
        return (
            UNKNOWN,
            "no saved rows could be read AND the page does not corroborate an "
            f"empty list: the Saved tab count reads {stated!r} and the empty "
            f"state ({empty_state!r}) is what would have to show. Nothing here "
            "distinguishes an empty list from a read that failed. "
            + shape.tracker_read_note(
                await dom.read_tracker_evidence(page),
                list_wait,
                dict(getattr(navigator, "last_settle", None) or {}),
                records=len(records),
                dropped=dropped,
                census=await dom.harvest_census(
                    page, href_pattern=dom.JOB_HREF, max_items=SAVED_LIST_MAX_ROWS
                ),
                row_shape=await dom.read_tracker_row_shape(page),
                traces=[
                    shape.parse_job_card_trace(rec) for rec in records[:3]
                ],
            ),
        )
    if len(rows) == stated:
        return (
            "not_saved",
            f"all {stated} rows LinkedIn counts in the Saved tab were read, and "
            "this posting is not among them.",
        )
    return (
        UNKNOWN,
        f"{len(rows)} of the {stated} rows LinkedIn counts in the Saved tab "
        "were read -- this loads one page and does not scroll, so the rest are "
        "below the fold rather than missing. Absence from a list that is a "
        "fraction of itself is not absence.",
    )


async def _read_profile_state(
    page: Any, spec: WriteSpec
) -> tuple[dict[str, Any], str, str]:
    """His own name, and the Open To Work audience LinkedIn prints beside it.

    The ORIGIN is validated here, not only the destination. An audience string
    this server has never seen LinkedIn render comes back ``unknown`` rather
    than being echoed into a gate: a setting whose current audience cannot be
    named is one whose change cannot be described, and this is the single
    action in the design a current employer can see.
    """
    fields = await dom.read_profile_fields(page)
    sections = [s for s in (fields.get("sections") or []) if s]
    topcard = shape.pick_topcard(sections, fields.get("title"))
    lines = (topcard or {}).get("lines") or []

    identity = shape.parse_profile_topcard(lines)
    if not identity.get("name"):
        raise WriteAttemptError(
            "refusing to render a confirm gate for a profile setting without "
            "reading the profile: the topcard drew no name, so this gate "
            "cannot show him WHOSE setting it is about."
        )
    facts = {"name": identity.get("name"), "headline": identity.get("headline")}

    open_to_work = shape.parse_open_to_work(lines)
    if open_to_work.get("on") is not True:
        return (
            facts,
            UNKNOWN,
            "no 'Open to work' line rendered on the topcard. That is NOT the "
            "same as the setting being off -- the off state has never been "
            "observed on this account, so nothing here can tell 'switched off' "
            "from 'the card did not draw'. "
            + str(open_to_work.get("who_can_see_it") or ""),
        )
    audience = str(open_to_work.get("audience") or "").strip()
    if audience.casefold() not in spec.audiences:
        return (
            facts,
            UNKNOWN,
            f"LinkedIn reports the audience as {audience!r}, which is not one "
            "of the settings this server has seen it render "
            f"({sorted(spec.audiences)}). A gate that cannot say who can "
            "currently see a setting must not offer to change it.",
        )
    return (
        facts,
        audience,
        f"LinkedIn prints the audience verbatim beside the label: {audience!r}",
    )


# ---------------------------------------------------------------------------
# 5b. The live reads the SEVEN refusing actions perform for themselves
# ---------------------------------------------------------------------------
#
# EACH OF THESE EXISTS SO A REFUSAL CAN BE A MEASUREMENT RATHER THAN A MEMORY.
# The seven capabilities added on 2026-08-30 are sanctioned and not
# performable, and the lazy way to build that is a constant string saying so.
# The failure mode of the lazy way is already documented three times in this
# package: a stored "cannot" outlives the reason for it and is then read as
# current. So each of these loads the surface, counts what bears on the
# capability, and hands the gate a state it read seconds ago.
#
# EVERY URL BELOW WAS ALREADY ON THE READ ALLOWLIST. No pattern was added and
# no forbidden substring was shortened to make these possible; the four frozen
# denylists are byte-identical across the change that introduced them.
#
# NONE OF THEM READS A THIRD PARTY'S NAME. The invitation reader is the one
# that could -- LinkedIn writes a member's name into that control's accessible
# name -- and it returns a count and nothing else. See
# ``dom.read_invitation_surface``.


async def _read_feed_composer(
    page: Any, spec: WriteSpec
) -> tuple[dict[str, Any], str, str]:
    """Is there a composer on this page, and is its editor rendered?"""
    reading = await dom.read_composer_surface(page)
    controls = int(reading.get("composer_controls") or 0)
    editors = int(reading.get("editors") or 0)
    facts = dict(reading)
    if controls < 1:
        return (
            facts,
            UNKNOWN,
            "no control named "
            f"{dom.COMPOSER_CONTROL_NAME!r} rendered on the feed. That is NOT "
            "evidence that publishing is unavailable -- this loads one page "
            "and does not scroll, and the feed hydrates after it lands -- so "
            "nothing here can tell 'LinkedIn moved it' from 'it had not drawn "
            "yet'.",
        )
    return (
        facts,
        "composer_present",
        f"{controls} composer control(s) named {dom.COMPOSER_CONTROL_NAME!r} "
        f"and {editors} contenteditable node(s) on the page. The second "
        "number is the one that decides this: a composer's EDITOR is a "
        "contenteditable node, and at zero the editor is behind a modal that "
        "has never been opened. "
        f"{reading.get('article_routes')} anchor(s) to "
        f"{dom.ARTICLE_COMPOSER_HREF} and "
        f"{reading.get('sharebox_routes')} to {dom.SHAREBOX_COMPOSER_HREF} "
        "were also counted -- publishing IS url-addressed, on two addresses "
        "the read boundary does not permit.",
    )


async def _read_feed_item(
    page: Any, spec: WriteSpec
) -> tuple[dict[str, Any], str, str]:
    """The comment and reaction controls on the feed, and the states worn.

    ONE READER, TWO VERDICTS, and they are computed differently on purpose.
    A comment is ADDED, so the question is only whether the affordance is
    there. A reaction is a TOGGLE whose state is written into its own
    accessible name, so the question is whether every rendered control agrees
    -- a page carrying a mix of states cannot say which item a direction
    belongs to, and picking one would be picking by position.
    """
    reading = await dom.read_reaction_surface(page)
    facts = dict(reading)
    controls = int(reading.get("controls") or 0)
    off_state = int(reading.get("off_state") or 0)
    comments = int(reading.get("comment_controls") or 0)
    permalinks = int(reading.get("permalinks") or 0)
    tail = (
        f" {permalinks} item permalink(s) were counted on the page; that "
        "address family is /feed/update/<urn>/, which the read boundary "
        "forbids, so a key exists on the page and cannot be followed."
    )

    if spec.action == "comment_on_item":
        if comments < 1:
            return (
                facts,
                UNKNOWN,
                "no control named "
                f"{dom.COMMENT_CONTROL_NAME!r} rendered. The feed hydrates "
                "after it lands and this does not scroll, so absence here is "
                "unknown rather than zero." + tail,
            )
        return (
            facts,
            "comment_control_present",
            f"{comments} comment control(s) and "
            f"{reading.get('editors', 0)} contenteditable node(s). The "
            "composer opens in place when the control is pressed, so a zero "
            "for editors is the expected reading and is also why the comment "
            "box itself has never been observed." + tail,
        )

    if controls < 1:
        return (
            facts,
            UNKNOWN,
            "no reaction control rendered. Absence on a first render is "
            "unknown, not zero." + tail,
        )
    if off_state != controls:
        return (
            facts,
            UNKNOWN,
            f"{controls} reaction control(s) rendered and only {off_state} of "
            f"them read {dom.REACTION_OFF_LABEL!r}. The rest are wearing a "
            "state this reader has never seen, and the labels found were "
            f"{reading.get('labels')}. A mixed page cannot settle a direction "
            "for any single item, and an unrecognised label is refused rather "
            "than interpreted -- that unseen string is exactly the ON-state "
            "label this action is waiting for." + tail,
        )
    return (
        facts,
        "no_reaction",
        f"all {controls} reaction control(s) on the page read "
        f"{dom.REACTION_OFF_LABEL!r}. LinkedIn writes the toggle state into "
        "the accessible name, so this is read off the very control a reaction "
        "would move -- the strongest direction source in this design. It "
        "settles the STATE and not the TARGET: several items are on the page "
        "and none of them can be selected from here." + tail,
    )


async def _read_profile_editors(
    page: Any, spec: WriteSpec
) -> tuple[dict[str, Any], str, str]:
    """Which profile editors this page addresses by url."""
    reading = await dom.read_profile_editor_surface(page)
    editors = reading.get("editors") or {}
    found = sorted(key for key, count in editors.items() if int(count or 0) > 0)
    facts = dict(reading)
    if not found:
        return (
            facts,
            UNKNOWN,
            "none of the three measured editor addresses "
            f"({list(dom.PROFILE_EDITOR_HREFS)}) is anchored on the page. "
            "Either it had not hydrated or LinkedIn has moved the editors "
            "again -- and the second is what happened between this repo's "
            "profile fixtures and the live page, which is the reason this "
            "reads instead of remembering.",
        )
    return (
        facts,
        "editor_addressed",
        f"{len(found)} of the three measured editor addresses are anchored on "
        f"the page ({found}), and it carries {reading.get('forms')} form(s). "
        "Both numbers contradict the fixtures, which carry no editor anchor "
        "and no form at all: a profile editor IS url-addressed. What stops "
        "this action is the boundary, not the address -- '/edit/' is on the "
        "read boundary's forbidden list -- and the fact that no field inside "
        "any editor has ever been observed.",
    )


async def _read_settings_index(
    page: Any, spec: WriteSpec
) -> tuple[dict[str, Any], str, str]:
    """How many settings this surface addresses, and how many it can switch."""
    reading = await dom.read_settings_surface(page)
    links = int(reading.get("links") or 0)
    facts = dict(reading)
    if links < 1:
        return (
            facts,
            UNKNOWN,
            "the settings surface drew no setting links at all, so it did not "
            "render. LinkedIn also interposes a re-auth challenge in front of "
            "parts of settings; when it does the landed url carries "
            "'/checkpoint/' and the auth-wall check reports it rather than "
            "letting a half-read pass.",
        )
    return (
        facts,
        "setting_addressed",
        f"{links} setting(s) are addressed by url from this surface, which "
        f"itself carries {reading.get('forms')} form(s) and "
        f"{reading.get('controls')} switch-like control(s). A settings index "
        "that hands out addresses and switches nothing is the measurement: "
        "every VALUE lives one page further down, on an address the read "
        "boundary forbids, and no page below this one has ever been loaded.",
    )


#: THE FOUR ANSWERS A NEEDLE CAN PRODUCE, and only the last is aimable.
#: Written as constants because three of them are REFUSALS and a refusal
#: compared against a typo'd string literal is a refusal that stops refusing.
INVITE_UNASKED = "no_needle"
INVITE_NO_MATCH = "no_match"
INVITE_AMBIGUOUS = "ambiguous"
INVITE_AIMED = "aimed"


def aim_invitation(reading: dict[str, Any]) -> tuple[str, str, Optional[int]]:
    """Which ONE invitation control a needle picked out, or why none.

    EXACTLY ONE MATCH IS THE ONLY AIMABLE STATE, and the two refusals either
    side of it are refusing different things:

    * **none** -- nobody drawn on this surface carries that word. Not "try
      again with a click"; there is nothing here to aim at.
    * **two or more** -- AMBIGUOUS, and this is the refusal that matters. The
      controls are indistinguishable to this function; picking one would be
      picking BY POSITION, which is how a request lands on a stranger who
      merely sorted earlier. ``unfollow_company`` refuses on exactly this
      ground when a company id resolves more than one row, and an invitation
      is less recoverable than an unfollow, not more.
    * **one** -- aimable, and the index IS the aim.

    THIS FUNCTION NEVER SEES THE NEEDLE, which is not an accident of the
    signature -- it is the signature doing the work. Its inputs are three
    integers and its ``why`` strings are built from counts, so there is no
    branch on which a person's name could reach the text a caller reads,
    stores or logs. The needle lives in :func:`dom.read_invitation_surface`'s
    argument list and nowhere downstream of it.

    AN INDEX IS NOT A PROMISE. It describes the list AS READ. Anything that
    would act on it must re-resolve it against the page immediately before
    acting, because a rail that re-renders between a preview and a
    confirmation renumbers everything on it. Nothing acts on it today.
    """
    matches = reading.get("matches")
    controls = int(reading.get("controls") or 0)
    if matches is None:
        return (
            INVITE_UNASKED,
            f"{controls} invitation control(s) are drawn and no needle was "
            "given, so none of them was picked out. A count is not an aim.",
            None,
        )
    matches = int(matches)
    if matches < 1:
        return (
            INVITE_NO_MATCH,
            f"none of the {controls} invitation control(s) on this surface "
            "carries the word given. The comparison ran inside the page and "
            "what came back was a count of zero -- no label was read here, so "
            "this cannot say who IS drawn, only that nobody matched.",
            None,
        )
    if matches > 1:
        return (
            INVITE_AMBIGUOUS,
            f"{matches} of the {controls} invitation control(s) match, and "
            "that is a refusal rather than a shortlist. Nothing here "
            "distinguishes them, so choosing one would be choosing by "
            "position -- which is how an invitation reaches somebody who was "
            "merely drawn first. Narrow the word until exactly one matches.",
            None,
        )
    position = reading.get("index")
    if position is None:
        # UNREACHABLE FROM THE SCRIPT, and kept because a check that cannot
        # fail certifies nothing while THIS one can: it fires if the reader
        # ever reports a single match without a position -- a partial read, a
        # hand-built dict, a future reader that forgets the field. The safe
        # answer to "one match, no index" is the ambiguous refusal, never a
        # guess at 0.
        return (
            INVITE_AMBIGUOUS,
            "exactly one control matched and the reader returned no position "
            "for it. That combination should not occur, and an aim cannot be "
            "invented from a missing index, so this refuses.",
            None,
        )
    position = int(position)
    return (
        INVITE_AIMED,
        f"exactly 1 of the {controls} invitation control(s) matches, at "
        f"position {position} in the suffix-matched list. The match was made "
        "inside the page; no label crossed into this process.",
        position,
    )


async def _read_profile_invitations(
    page: Any, spec: WriteSpec
) -> tuple[dict[str, Any], str, str]:
    """How many invitation controls his own profile draws. A COUNT ONLY."""
    reading = await dom.read_invitation_surface(page)
    controls = int(reading.get("controls") or 0)
    facts = dict(reading)
    if controls < 1:
        return (
            facts,
            UNKNOWN,
            "no control whose accessible name ends "
            f"{dom.INVITE_CONTROL_SUFFIX!r} rendered on this page. The rail "
            "that carries them is a suggestion rail and need not be drawn, so "
            "this is unknown rather than zero.",
        )
    return (
        facts,
        "invite_control_present",
        f"{controls} invitation control(s) on HIS OWN PROFILE -- a page this "
        "server already loads, and one carrying no pending-invitation "
        "counter. That is the finding: the capability has a route which does "
        "NOT cost the badge that /mynetwork/ would. Only the count was read. "
        "The label is the other person's name and is never fetched, which is "
        "also why a suffix selects all "
        f"{controls} of these controls and cannot select one.",
    )


async def _read_messaging_badge(
    page: Any, spec: WriteSpec
) -> tuple[dict[str, Any], str, str]:
    """The messaging badge, read WITHOUT opening messaging."""
    reading = await dom.read_messaging_badge(page)
    facts = dict(reading)
    if int(reading.get("links") or 0) < 1:
        return (
            facts,
            UNKNOWN,
            "no messaging link is on this page, so not even the badge could "
            "be read. Nothing was opened to find that out.",
        )
    return (
        facts,
        "composer_unmeasured",
        "the messaging nav badge currently reads "
        f"{reading.get('label')!r}, read off a page that was already open. "
        "THAT NUMBER IS THE COST: LinkedIn's messaging badge counts "
        "new-since-last-visit and resets when the tab is opened, and "
        "/messaging/ does not stay on a list -- it redirects into one "
        "specific conversation of LinkedIn's choosing, so the load opens "
        "somebody's thread. This gate did not pay either cost to tell you "
        "that. The composer itself remains unobserved, which is a separate "
        "fact from the badge and is why this action refuses.",
    )


#: WHICH SURFACE EACH REFUSING ACTION READS, and it is chosen by the SPEC's own
#: ``state_from`` rather than by anything a caller passes -- the same rule the
#: four original actions follow. Each entry is (url, surface name for the
#: auth-wall message, reader).
_SURFACE_READS: dict[str, tuple[str, str, Any]] = {
    "feed_composer": (FEED_URL, "feed", _read_feed_composer),
    "feed_item": (FEED_URL, "feed", _read_feed_item),
    "profile_editors": (PROFILE_URL, "profile", _read_profile_editors),
    "settings_index": (SETTINGS_URL, "settings", _read_settings_index),
    "profile_invitations": (PROFILE_URL, "profile", _read_profile_invitations),
    "messaging_badge": (FEED_URL, "feed", _read_messaging_badge),
}


def _record(
    spec: WriteSpec,
    *,
    target: str,
    facts: dict[str, Any],
    facts_url: str,
    state: str,
    state_why: str,
    state_url: str,
    same_page_as_action: bool,
) -> Observation:
    """Mint the receipt. THE ONLY WRITER of :data:`_OBSERVED`."""
    observation = Observation(
        target=target,
        target_kind=spec.target_kind,
        facts=dict(facts),
        facts_url=facts_url,
        state=state,
        state_why=state_why,
        state_url=state_url,
        same_page_as_action=same_page_as_action,
        receipt=secrets.token_urlsafe(24),
        observed_at=time.monotonic(),
    )
    _OBSERVED[observation.receipt] = observation
    return observation


async def observe(
    navigator: Any, page: Any, spec: WriteSpec, target: Any
) -> Observation:
    """Read the target LIVE, and mint the receipt that lets a grant exist.

    One or two page loads, all of them READS through the read door, none of
    them clicking anything. WHICH surfaces are opened is decided by the SPEC's
    own ``state_from``, never by an argument -- so a caller chooses which
    sanctioned action to preview and nothing else about it.
    """
    if not writes_enabled():
        raise WriteAttemptError(
            f"writes are disabled: set {WRITES_FLAG}=1 to enable them. This "
            "server is read-only unless that flag is set deliberately."
        )
    target = _target_for(spec, target)

    if spec.state_from == "posting_page":
        # ONE load. The state and the action share a page, which is the only
        # shape where the thing being described and the thing being acted on
        # cannot drift apart.
        url = str(spec.url_template or "").format(target=target)
        landed = await _load(navigator, page, url, surface="job posting")
        facts = await _read_posting_facts(page, target, navigator=navigator)
        state, why = await _read_follow_state(page)
        return _record(
            spec,
            target=target,
            facts=facts,
            facts_url=landed,
            state=state,
            state_why=why,
            state_url=landed,
            same_page_as_action=True,
        )

    if spec.state_from == "apply_control":
        # ONE load, and the facts and the route come off the same page. The
        # route is read from the CONTROL rather than from the payload, which
        # is not a stylistic choice: an off-site posting was measured carrying
        # the on-site apply flow's own marker inside its pre-hydration payload,
        # for the same job id, so a payload search classifies nothing.
        url = str(spec.url_template or JOB_POSTING_URL).format(target=target)
        landed = await _load(navigator, page, url, surface="job posting")
        facts = await _read_posting_facts(page, target, navigator=navigator)
        state, why = await _read_apply_route(page, target)
        return _record(
            spec,
            target=target,
            facts=facts,
            facts_url=landed,
            state=state,
            state_why=why,
            state_url=landed,
            same_page_as_action=True,
        )

    if spec.state_from == "followed_pages":
        # ONE load, and the click lands on this very page. The facts come from
        # the row's own button, so the name printed in the gate and the row the
        # click is anchored to are the same DOM element by construction.
        landed = await _load(
            navigator, page, FOLLOWED_PAGES_URL, surface="followed companies"
        )
        facts, state, why = await _read_followed_state(page, target)
        return _record(
            spec,
            target=target,
            facts=facts,
            facts_url=landed,
            state=state,
            state_why=why,
            state_url=landed,
            same_page_as_action=True,
        )

    if spec.state_from == "saved_list":
        # TWO loads, and the gate says so. The facts come off the posting; the
        # direction comes off his saved list, because the save control's ON
        # state does not exist on this account to be read.
        url = str(spec.url_template or "").format(target=target)
        landed = await _load(navigator, page, url, surface="job posting")
        facts = await _read_posting_facts(page, target, navigator=navigator)
        state_landed = await _load(
            navigator, page, SAVED_LIST_URL, surface="saved jobs"
        )
        state, why = await _read_saved_state(page, target, navigator=navigator)
        return _record(
            spec,
            target=target,
            facts=facts,
            facts_url=landed,
            state=state,
            state_why=why,
            state_url=state_landed,
            same_page_as_action=False,
        )

    if spec.state_from == "profile_topcard":
        landed = await _load(navigator, page, PROFILE_URL, surface="profile")
        facts, state, why = await _read_profile_state(page, spec)
        return _record(
            spec,
            target=target,
            facts=facts,
            facts_url=landed,
            state=state,
            state_why=why,
            state_url=landed,
            same_page_as_action=False,
        )

    if spec.state_from in _SURFACE_READS:
        # THE SEVEN. One load each, of a page ALREADY on the read allowlist,
        # and the state is whatever the page says right now -- which is the
        # difference between a refusal that looked and a refusal that
        # remembers. Every one of them then fails to mint, because none holds
        # a url_template; what the operator gets back is the warning block
        # with a fresh measurement inside it.
        url, surface, reader = _SURFACE_READS[spec.state_from]
        landed = await _load(navigator, page, url, surface=surface)
        facts, state, why = await reader(page, spec)
        return _record(
            spec,
            target=target,
            facts=facts,
            facts_url=landed,
            state=state,
            state_why=why,
            state_url=landed,
            same_page_as_action=False,
        )

    raise WriteAttemptError(
        f"{spec.action!r} declares state_from {spec.state_from!r}, which names "
        "no live read. A gate whose state has no measured source may not "
        "render at all -- that is the same rule as refusing to name a target "
        "surface nobody has opened."
    )


def _take_observation(receipt: Any, *, spec: WriteSpec, target: str) -> Observation:
    """Redeem a receipt for the ONE read it was minted by. Single use."""
    if not isinstance(receipt, str) or not receipt:
        raise WriteAttemptError(
            "no read receipt. A grant is minted only by a preview that re-read "
            "the target live, and a state string cannot stand in -- a state "
            "string can be typed by a caller that never performed a read."
        )
    observation = _OBSERVED.pop(receipt, None)
    if observation is None:
        raise WriteAttemptError(
            "unknown or already-redeemed read receipt. Observations are "
            "single-use, so a replayed reading mints nothing."
        )
    if observation.expired():
        raise WriteAttemptError(
            f"this reading is older than {OBSERVATION_TTL_SECONDS:.0f}s and "
            "will not be used. Read the target again."
        )
    if observation.target != target or observation.target_kind != spec.target_kind:
        raise WriteAttemptError(
            f"this reading is of {observation.target!r}, not {target!r}"
        )
    if not observation.state or observation.state == UNKNOWN:
        raise WriteAttemptError(
            f"this reading did not settle the state of {target!r}, so no grant "
            "is minted from it. " + observation.state_why
        )
    return observation


# ---------------------------------------------------------------------------
# 6. The gate the operator actually reads
# ---------------------------------------------------------------------------


def _direction(
    spec: WriteSpec, observation: Observation, to_state: Optional[str]
) -> dict[str, Any]:
    """Say which way this action moves the toggle, or refuse to render at all.

    THE TOGGLE-DIRECTION RULE, enforced. Three separate refusals, and each of
    them is a real way a confirm gate could otherwise mislead him:

    1. **No state at all.** Unreachable through :func:`preview`, which always
       observes first, and kept because it is the guard that would catch a
       future edit routing round the read.
    2. **State unknown.** The read ran and came back ``unknown`` -- the control
       had not rendered, or several did, or the saved list was a fraction of
       itself, or LinkedIn labelled something a name this server has never
       seen. Proceeding on ``unknown`` is proceeding on a guess wearing a
       measurement's clothes.
    3. **Wrong state.** The posting is already saved and the action is save.
       This is the refusal most likely to be argued with, because the outcome
       looks harmless -- and it is not: on a TOGGLE, performing the action from
       the wrong state performs its OPPOSITE. A save confirmed on a saved
       posting unsaves it.

    THE FIRST TWO NOW RUN BEFORE THE BRANCH, and that is a fix rather than a
    tidy-up. Until 2026-08-23 the multi-state branch returned BEFORE the
    unknown check, so ``set_open_to_work`` -- the one action whose residue is
    IRREVERSIBLE IN AUDIENCE -- would render a gate on an origin nobody had
    read, describe the current audience as "UNRECOGNISED", and offer to change
    it anyway. Found by a cold review on the day the branch shipped.
    """
    state = observation.state
    if not state:
        raise WriteAttemptError(
            f"refusing to render a confirm gate for {spec.action!r} without "
            "the target's measured current state. Both controls this design "
            "touches are TOGGLES, and a gate that cannot say which way it "
            "moves one is not a gate. " + spec.direction_source
        )
    if state == UNKNOWN:
        raise WriteAttemptError(
            "the current state of this target came back 'unknown', so "
            f"{spec.action!r} cannot say which way it would move. That is a "
            "refusal, not a delay -- proceeding here would be guessing. "
            + observation.state_why
        )

    read_from: dict[str, Any] = {
        "read_from": spec.direction_source,
        "read_from_url": observation.state_url,
        "read_by": "this gate, on this call",
        "why": observation.state_why,
        "same_page_as_the_action": observation.same_page_as_action,
        "what_that_means": (
            "the direction was read off the very control this action would "
            "move, at no extra page load"
            if observation.same_page_as_action
            else (
                "the direction came from a DIFFERENT surface ("
                + observation.state_url
                + "), which costs a second page load. A different source, not "
                "a weaker one."
            )
        ),
    }

    if spec.from_state is None:
        # Not a binary toggle. Open To Work has three states, so the
        # destination cannot be derived and the caller has to name it.
        if not to_state:
            raise WriteAttemptError(
                f"{spec.action!r} has more than two states, so the "
                "destination must be named rather than derived. Choose one of "
                f"{sorted(spec.audiences)}."
            )
        if to_state.strip().casefold() not in spec.audiences:
            raise WriteAttemptError(
                f"{to_state!r} is not a setting this server has ever seen "
                f"LinkedIn render. The known ones are {sorted(spec.audiences)}, "
                "and a gate that cannot say who can see a setting must not "
                "offer it."
            )
        if state.strip().casefold() == to_state.strip().casefold():
            raise WriteAttemptError(
                f"the setting is already {state!r}. Nothing to change."
            )
        if state.strip().casefold() not in spec.audiences:
            # THE ORIGIN GETS THE SAME CHECK THE DESTINATION ALREADY HAD.
            # Above this line the state has only been tested for emptiness and
            # for ``unknown``; the block below then subscripts
            # ``spec.audiences[...]`` with it. A relabelled or translated
            # audience -- anything LinkedIn renders that this spec has not met
            # -- came out of that subscript as a raw KeyError rather than a
            # sentence, on the one action whose residue is IRREVERSIBLE IN
            # AUDIENCE. Measured 2026-08-31: state 'Anyone on LinkedIn' raised
            # ``KeyError: 'anyone on linkedin'`` at writes.py:2722.
            #
            # It refuses rather than defaulting, and that is the load-bearing
            # half. A fallback string would let the gate print WHO CAN SEE IT
            # NOW for a setting it cannot identify, which is the exact claim
            # ``_read_profile_state`` already declines to make one layer up.
            #
            # UNREACHABLE THROUGH ``preview`` TODAY, like refusal 1 above:
            # ``_read_profile_state`` casefold-checks the audience itself and
            # returns ``unknown`` on a miss. Kept for the same reason -- it is
            # the guard that catches a future edit routing round that read.
            raise WriteAttemptError(
                f"the current setting reads {state!r}, which is not one this "
                f"server has seen LinkedIn render. The known ones are "
                f"{sorted(spec.audiences)}, and a gate that cannot say who "
                "can see the setting he is in must not offer to change it. "
                + observation.state_why
            )
        out = dict(read_from)
        out.update(
            {
                "currently": state,
                "after": to_state,
                "who_can_see_it_now": spec.audiences[state.strip().casefold()],
                "who_will_see_it_after": spec.audiences[
                    to_state.strip().casefold()
                ],
            }
        )
        return out

    if state != spec.from_state:
        raise WriteAttemptError(
            f"{spec.action!r} is valid only from {spec.from_state!r} and this "
            f"target reads {state!r}. "
            + (
                spec.wrong_state_note
                or (
                    "On a toggle, performing an action from the wrong state "
                    "performs its OPPOSITE -- confirming a save on an "
                    "already-saved posting would UNSAVE it -- so this is "
                    "refused rather than treated as a harmless no-op. You may "
                    "have wanted the inverse action."
                )
            )
            + " "
            + observation.state_why
        )
    out = dict(read_from)
    out.update({"currently": state, "after": spec.to_state})
    return out


def _reversibility_disagreement(spec: WriteSpec) -> Optional[str]:
    """Do the one-word verdict and the sentence beside it say the same thing?

    A late addition, and it earns its place. The class field was asserted only
    against the set of values that EXIST, so all four specs could be flipped to
    IRREVERSIBLE with the whole suite green -- and the gate would then print
    ``reversibility_class: IRREVERSIBLE`` beside ``reversibility: "reversible
    by unsaving the same posting"``. Two fields contradicting each other inside
    one block is worse than either being wrong alone: the reader cannot tell
    which half to believe, and the block is the only thing he has.
    """
    verdict = spec.reversibility_class.strip().upper()
    prose = spec.reversibility.strip().casefold()
    if verdict not in {"REVERSIBLE", "IRREVERSIBLE", "STILL-UNKNOWN"}:
        return (
            f"reversibility_class is {spec.reversibility_class!r}, which is "
            "not one of the three verdicts"
        )
    if not spec.reversibility_measured:
        if verdict != "STILL-UNKNOWN":
            return (
                f"reversibility_class says {verdict} while the claim itself is "
                "UNMEASURED. An unmeasured verdict may not wear a measured "
                "class -- that is the confident string this rule exists to stop"
            )
        return None
    if verdict == "REVERSIBLE" and not prose.startswith("reversible"):
        return (
            "reversibility_class says REVERSIBLE while the sentence beside it "
            f"reads {spec.reversibility!r}"
        )
    if verdict == "IRREVERSIBLE" and prose.startswith("reversible"):
        return (
            "reversibility_class says IRREVERSIBLE while the sentence beside "
            f"it reads {spec.reversibility!r}"
        )
    return None


def _render(
    spec: WriteSpec,
    observation: Observation,
    direction: dict[str, Any],
    token: Optional[str],
) -> dict[str, Any]:
    """Build the block a human reads before confirming.

    Every fact in here came from the read this gate performed. There is no
    parameter carrying a title, an employer or a state, which is the whole
    point of the section above.
    """
    disagreement = _reversibility_disagreement(spec)
    if disagreement is not None:
        raise WriteAttemptError(
            f"refusing to render a confirm gate for {spec.action!r}: "
            + disagreement
            + ". A block whose two reversibility fields contradict each other "
            "tells the reader less than one that says nothing."
        )

    if spec.reversibility_measured:
        # THE MEASURED-REVERSIBILITY RULE. A measured verdict prints, and it
        # prints WITH its evidence, its owner and its residue -- a bare
        # "reversible" is the confident string the rule exists to stop, and it
        # stays that whether or not somebody has since done the measuring.
        reversibility = spec.reversibility
    else:
        reversibility = (
            "UNMEASURED -- this server has not verified that this action can "
            "be undone, so it will not claim it. What would settle it: "
            + spec.reversibility_procedure
        )

    where: dict[str, Any] = {"read_from_url": observation.facts_url}
    if spec.target_kind == "job_id":
        where["job_id"] = observation.target
        where["title"] = observation.facts.get("title")
        where["company"] = observation.facts.get("company")
    elif spec.target_kind == "company_id":
        # THE NAME IS THE FIELD HE CAN CHECK; the id is what the click is
        # anchored to. Both are printed, and the coverage numbers with them --
        # this list is never complete, so the block says how much of it was
        # actually seen rather than leaving him to assume all of it.
        where["company_id"] = observation.target
        where["company"] = observation.facts.get("company")
        where["read_from_the_rows_own_button"] = True
        where["list_coverage"] = (
            f"{observation.facts.get('rendered')} rows rendered of "
            f"{observation.facts.get('total_followed')} LinkedIn says you "
            "follow. This surface has no pagination control, so the rest were "
            "not shown and could not have been."
        )
    elif spec.target_kind == "self":
        where["whose"] = "your own LinkedIn profile"
        where["name"] = observation.facts.get("name")
        where["headline"] = observation.facts.get("headline")
    else:
        # THE SEVEN. Their target is a subject, or a subject AND the content
        # that would be published, and the content is PRINTED IN FULL rather
        # than summarised or truncated. That is the point of showing him a
        # block at all: a comment, a post and a message are published under
        # his name, and "he approved a post" means nothing unless he was shown
        # the words. The canonical string is printed beside them because it is
        # what a confirm token binds to -- if the two ever disagree, the
        # canonical one is what would act.
        where["target_kind"] = spec.target_kind
        where["target"] = observation.target
        if TARGET_JOIN in observation.target:
            first, second = _COMPOSITE_TARGET_KINDS[spec.target_kind]
            subject, _, content = observation.target.partition(TARGET_JOIN)
            where[first] = subject
            where[second] = content
        where["what_the_page_showed"] = observation.facts
    where["url"] = (
        spec.url_template.format(target=observation.target)
        if spec.url_template
        else (
            "UNMEASURED -- this action's surface has never been loaded by "
            "this server, so it cannot name the page it would act on."
        )
    )

    out: dict[str, Any] = {
        "action": spec.action,
        "what": spec.summary,
        "where": where,
        "read": {
            "performed_by": "this gate, on this call, before anything was shown",
            "facts_url": observation.facts_url,
            "state_url": observation.state_url,
            "same_page_as_the_action": observation.same_page_as_action,
            "page_loads": 1 if observation.facts_url == observation.state_url else 2,
            "age_seconds": round(observation.age(), 3),
        },
        "direction": direction,
        "reversibility": reversibility,
        "reversibility_measured": spec.reversibility_measured,
        "reversibility_class": spec.reversibility_class,
        "reversibility_evidence": spec.reversibility_evidence
        or spec.reversibility_procedure,
        "reversible_by": spec.reversible_by,
        "what_it_cannot_undo": spec.residue,
        "irreversible": spec.irreversible,
        "spends": spec.spends,
        "performed": False,
    }

    if token is None:
        # No surface, so no grant at all. See :func:`mint`.
        out["to_confirm"] = None
        # WRITTEN FOR BOTH SURFACE-LESS ACTIONS, which it was not until
        # 2026-08-24: it said "its EDITOR has never been loaded" and closed
        # with "change it yourself if you want it changed". True of Open To
        # Work, which is a setting behind an editor; nonsense on an APPLY,
        # which has no editor and is not a change. A block whose prose fits
        # one of the two actions it serves is the same defect as an unknown
        # unfollow telling him to open his saved jobs -- correct advice
        # pointed at the wrong thing.
        out["what_happens_next"] = (
            "NOTHING has been done, and nothing can be: NO CONFIRM TOKEN IS "
            "ISSUED for this action. The surface it would have to act on has "
            "never been loaded by this server, so there is no page to act on "
            "and a grant would be permission to do something unreachable. "
            "What you are reading is the WARNING, not an offer -- do it "
            "yourself in LinkedIn if you want it done."
        )
    else:
        out["to_confirm"] = token
        out["what_happens_next"] = (
            "NOTHING has been done. To perform this, call the same tool again "
            "with confirm_token set to the value below. The token is good for "
            f"{GRANT_TTL_SECONDS:.0f} seconds, works once, and only for this "
            "action on this target."
        )
    if spec.audiences:
        out["who_can_see_it"] = direction.get("who_will_see_it_after")
    return out


async def preview(
    spec: WriteSpec,
    *,
    target: Any,
    navigator: Any,
    page: Any,
    to_state: Optional[str] = None,
) -> dict[str, Any]:
    """Read the target live, then render the block he reads. THE ONLY MINTER.

    WHAT A CALLER CAN NO LONGER DO: supply the state, supply the facts, or
    obtain a grant without this function having loaded the pages itself. The
    SIGNATURE is the enforcement -- there is no ``facts`` and no ``state`` to
    pass.

    The receipt never leaves this function. It is minted by :func:`observe`,
    redeemed by :func:`mint`, and discarded in the ``finally`` below whatever
    happens, so no reading survives the call that made it.
    """
    observation = await observe(navigator, page, spec, target)
    try:
        direction = _direction(spec, observation, to_state)
        token: Optional[str] = None
        grant: Optional[WriteGrant] = None
        if spec.url_template is not None:
            grant = mint(
                spec.action, observation.target, receipt=observation.receipt
            )
            token = grant.token
        block = _render(spec, observation, direction, token)
        if grant is not None:
            grant.preview = block
        return block
    finally:
        _OBSERVED.pop(observation.receipt, None)


# ---------------------------------------------------------------------------
# 7. The click
# ---------------------------------------------------------------------------

#: The two actions :func:`perform` will act on. NOT the sanctioned set: the
#: sanctioned set is what may hold a grant, this is what may be executed, and
#: they differ by two on purpose.
#:
#: ``follow_company`` IS HERE SINCE 2026-08-30, and this paragraph said the
#: opposite. Quoted, because the reversal is the point: "``follow_company`` is
#: sanctioned and is NOT here ... An action whose undo is hand-only does not go
#: first, and the operator cut it from this round on that ground rather than on
#: a technical one."
#:
#: Every FACT in that sentence still holds. A follow performed here is still
#: one this server cannot aim its own unfollow at -- the posting names its
#: employer by SLUG and the unfollow surface addresses rows by NUMERIC ID, and
#: that gap was RE-MEASURED on 2026-08-30 by the cheapest route the previous
#: audit named: ``linkedin_job_detail`` on a live posting returned
#: ``company_url: https://www.linkedin.com/company/<slug>/``, a slug and not an
#: id. So route one is now settled and it fails.
#:
#: WHAT CHANGED IS WHO DECIDES. "The undo is hand-only" is a REVERSIBILITY
#: FACT, and this design already has a place for a reversibility fact: the
#: ``reversible_by`` field, which the gate prints in full before he confirms
#: anything. Holding the action back as well amounts to deciding for him on a
#: ground he can read for himself -- and the standing ruling is that a refusal
#: survives only where the thing is IMPOSSIBLE with a measurement, or where the
#: gate is what defers the decision to him. This one is neither impossible nor
#: undeferrable. The anchor is measured (``aria-label="Follow"``), the surface
#: is already on the read allowlist, and the gate refuses on an unhydrated page
#: rather than clicking, which is the failure mode that actually mattered.
#:
#: THE PREREQUISITE THAT WAS MISSING AND IS NOW SUPPLIED. Adding this action to
#: this set alone would have been a defect, not a feature: ``_live_control``
#: had no branch for it, so gate 5 would have fallen through to the SAVE branch
#: and corroborated the wrong element -- the identical bug apply carried until
#: 2026-08-26. A branch was written for it first.
#:
#: ``set_open_to_work`` is not here either, and could not be: its editor is a
#: modal that has never loaded in any capture, it holds no ``url_template``, and
#: :func:`mint` already refuses it a grant at issue. Its residue is also the one
#: irreversibility in this design that is measured in AUDIENCE rather than in
#: state -- a badge taken down is not a badge un-seen.
#:
#: ``apply_job`` IS HERE, since 2026-08-25, and this paragraph said the exact
#: opposite until 2026-08-26 -- every clause of it overtaken and none of them
#: corrected: "its FLOW is not [measured]" (captured 2026-08-24), "thirteen job
#: captures contain zero forms" (true of those captures, irrelevant once the
#: flow itself was opened), "it holds no ``url_template``, so :func:`mint`
#: refuses it a grant" (it holds one, and mint issues grants for it). A comment
#: describing a capability as absent, sitting beside the set that contains it,
#: is the going-stale defect this wave keeps finding -- so the correction is
#: recorded rather than the sentences quietly swapped.
#:
#: What is TRUE, and is the part worth carrying: an apply cannot be taken back
#: by this server under any circumstances, and nobody has established that
#: LINKEDIN offers a withdraw at all. That makes it the last action in the
#: design that should ever be performed on a guessed selector -- which is why
#: it is the only member of :data:`TWO_CLICK_ACTIONS`, why the gate between
#: those clicks re-reads the modal live rather than trusting the preview, and
#: why an unfinished scan for advance controls refuses instead of proceeding.
#: The actions whose control is the SAVE button, and therefore the only ones
#: the save-specific "no measured anchor" refusal in :func:`perform` describes.
#: Named here rather than tested inline so that the guard and the message it
#: guards cannot drift apart.
_SAVE_FAMILY: frozenset[str] = frozenset({"save_job", "unsave_job"})

PERFORMABLE: frozenset[str] = frozenset(
    {
        "save_job",
        "unsave_job",
        "unfollow_company",
        "apply_job",
        "follow_company",
    }
)

#: Actions whose flow takes TWO clicks with a GATE between them. Only apply,
#: and it is named here rather than special-cased inside perform() so the
#: exception is visible from the top of the file instead of buried in a
#: branch. See :func:`_apply_submit_gate` for what the gate requires.
TWO_CLICK_ACTIONS: frozenset[str] = frozenset({"apply_job"})

#: How long to wait for the anchor to be actionable. Generous, because the
#: alternative to waiting is clicking early, and a click that lands on a
#: control that has not settled is the failure mode with no error message.
CLICK_TIMEOUT_MS = 10_000


#: The accessible-name PREFIX the unfollow control wears. A prefix rather than
#: an exact label because LinkedIn writes the Page's own name into it, which is
#: the same property that makes it the best anchor in this package and an
#: unusable dictionary key.
UNFOLLOW_ANCHOR_PREFIX = "Click to stop following "


def anchor_label_for(spec: WriteSpec) -> Optional[str]:
    """The label the control must be wearing before this action may click it.

    Derived from :data:`shape.SAVE_LABELS` rather than written down twice, and
    that indirection did exactly what it was built to do. The table maps a
    measured accessible name to the state it means; this reads it backwards,
    from the state an action is valid FROM to the name it would have to see.

        save_job    valid from ``not_saved`` -> "Save the job"    (MEASURED)
        unsave_job  valid from ``saved``     -> "Unsave the job"  (MEASURED)

    THE SECOND ROW ARRIVED ON 2026-08-30 AND NO CODE CHANGED. This docstring
    used to read "unsave_job valid from saved -> nothing (NEVER SEEN)" and
    promised that adding the observed label would give unsave its anchor
    WITHOUT A CODE EDIT. That is what happened: one row in ``shape.SAVE_LABELS``
    plus its mirror in ``dom.SAVE_LABELS_SEEN``, and this function started
    returning a real label. The indirection is left exactly as it was, because
    the same property applies to the next state nobody has photographed.

    It returns ``None`` when the table maps nothing to ``spec.from_state``, and
    :func:`perform` refuses on that -- still the correct behaviour, and still
    not a limitation to be worked around by picking a plausible string.

    TWO FAMILIES, AND THE DIFFERENCE IS STATED RATHER THAN FLATTENED. The
    save pair is anchored on an EXACT accessible name. ``unfollow_company``
    is anchored on a PREFIX, because LinkedIn writes the Page's own name into
    the label -- ``Click to stop following <Page>``. That is what makes it the
    strongest anchor in this package (the control states its own inverse
    action) and simultaneously unusable as a table key, so it does not live in
    a table. The row is pinned separately, by company id; see
    ``dom.unfollow_control_selector``.
    """
    if spec.action == "unfollow_company":
        return UNFOLLOW_ANCHOR_PREFIX
    if spec.action == "follow_company":
        # READ BACKWARDS OUT OF ``shape.FOLLOW_LABELS``, exactly as the save
        # pair is read backwards out of ``shape.SAVE_LABELS``, rather than the
        # string "Follow" being written here a third time. The table maps a
        # measured accessible name to the state it means; this asks it which
        # name the state this action is valid FROM would be wearing.
        #
        # Unlike the save pair, BOTH halves of this table have been measured
        # -- ``Follow`` and ``Following``, on a live posting from a company he
        # already follows -- so there is no missing state here and no refusal
        # waiting on a capture.
        for label, state in shape.FOLLOW_LABELS.items():
            if state == spec.from_state:
                return label
        return None
    if spec.action == "apply_job":
        # ADDED 2026-08-26, and its absence was not a subtlety: apply fell
        # through to the SAVE_LABELS lookup below, matched nothing, and
        # perform refused every apply with a sentence about the save
        # control's unphotographed ON state. The action was registered,
        # listed in PERFORMABLE, and reported by server_info as performable
        # and irreversible -- and could not run.
        #
        # The apply control's accessible name is a PREFIX because LinkedIn
        # writes the posting's title and employer into it. Measured, not
        # guessed: shape.LINKEDIN_APPLY_PREFIX is the same constant
        # dom.APPLY_CONTROL and shape.apply_route are built from, so the
        # anchor, the classifier and the selector cannot drift apart.
        return shape.LINKEDIN_APPLY_PREFIX
    for label, state in shape.SAVE_LABELS.items():
        if state == spec.from_state:
            return label
    return None


#: WHY EACH OF THE SEVEN IS SANCTIONED AND STILL WILL NOT RUN, in the words a
#: caller meets when it refuses. Added 2026-08-30, when the seven capabilities
#: the operator asked for were BUILT -- built as specs behind the existing
#: gate, with a live read each, and none of them performable.
#:
#: EVERY ENTRY ENDS WITH THE ONE MEASUREMENT THAT WOULD LIFT IT. That is the
#: format rather than a preference: a refusal that does not name its own fix is
#: indistinguishable from a refusal nobody intends to lift, and this package
#: has now twice found a stale "cannot" sitting beside a capability that could.
#:
#: TWO SHAPES OF BLOCKER APPEAR BELOW AND THEY ARE NOT THE SAME, so neither is
#: allowed to stand in for the other:
#:
#:   NO CONTROL     -- the thing that would be clicked has never been observed.
#:                     A capture lifts it.
#:   NO SURFACE     -- the address the action would act on is refused by
#:                     ``readonly._FORBIDDEN_URL_SUBSTRINGS``, which is checked
#:                     before the allowlist and is NOT shortened for a write.
#:                     Only a deliberate boundary ruling lifts it, and this
#:                     wave did not take one.
_NINE_REFUSALS: dict[str, str] = {
    "publish_post": (
        "publish_post is sanctioned and cannot be performed. WHAT IS "
        "MEASURED: the feed carries one composer control, accessible name "
        "'Start a post', drawn as a div with role=button and NO href -- so "
        "the composer opens as a modal and is not reachable by navigation. "
        "Two publish routes ARE url-addressed and both were measured as real "
        "anchors: 'Write article' -> /article/new/ and 'Create a post' -> "
        "/preload/sharebox/. NO CONTROL: the same census measured "
        "contenteditable == 0 across the whole page, so THE EDITOR HAS NEVER "
        "BEEN OBSERVED and neither has whatever control publishes. Clicking "
        "'Start a post' and then guessing at what appears is the one thing "
        "this server does not do on a write. NO SURFACE either: neither "
        "/article/new/ nor /preload/sharebox/ is on the read allowlist. WHAT "
        "WOULD LIFT IT: a capture of the opened composer -- the accessible "
        "name of its editable node and of its publish control, at both "
        "hydration states. That capture requires a click, and the click that "
        "would first SHOW the composer is harmless; it is the second one that "
        "publishes. So this is measurable with him watching, unlike the "
        "endorsement question, and it has simply not been measured."
    ),
    "comment_on_item": (
        "comment_on_item is sanctioned and cannot be performed. WHAT IS "
        "MEASURED: the comment affordance, in both of its two shapes -- a "
        "text-named button on /feed/ (count 3) and an ANCHOR on the profile "
        "pointing at the item's permalink (count 8). The second is where a "
        "target key would come from: a feed item is addressed by its urn. NO "
        "SURFACE: that permalink is /feed/update/<urn>/ and '/feed/update' is "
        "on readonly._FORBIDDEN_URL_SUBSTRINGS, which is checked before the "
        "allowlist and is not shortened for a write. NO CONTROL either: "
        "contenteditable == 0 on both surfaces, so the comment box itself has "
        "never been observed. AND A THIRD THING, which is the one that would "
        "still matter if the other two were fixed: a comment is PUBLIC AND "
        "ATTRIBUTED TO HIM under somebody else's item, so the exact text must "
        "be shown before anything is posted -- which is why the target this "
        "action is addressed by carries the text, not just the item. WHAT "
        "WOULD LIFT IT: a boundary ruling on /feed/update/<urn>/, and a "
        "capture of the opened comment box."
    ),
    "react_to_item": (
        "react_to_item is sanctioned and cannot be performed, and it is the "
        "closest of the seven. WHAT IS MEASURED, and it is the strongest "
        "single string found on 2026-08-30: LinkedIn writes the toggle state "
        "into the control's own accessible name -- aria-label='Reaction "
        "button state: no reaction' -- exactly as it does on the follow "
        "control. Eleven of them were read, 3 on the feed and 8 on the "
        "profile, every one in the OFF state. So the OFF-to-ON anchor is "
        "MEASURED. THE ON-STATE LABEL HAS NEVER BEEN SEEN, because nothing on "
        "either surface had been reacted to -- the identical position "
        "unsave_job was in until 2026-08-30, and it takes the identical "
        "answer: the missing half is not guessed. How unsave got out is the "
        "template rather than a precedent for guessing: one supervised write "
        "produced the label, then a READ-ONLY route re-measured it three "
        "times before the row was written. NO SURFACE: aiming at one item "
        "needs its "
        "permalink, /feed/update/<urn>/, which is on the forbidden list; and "
        "the feed renders several items at once, so choosing one there would "
        "be choosing by position, which this package refuses everywhere else. "
        "WHAT WOULD LIFT IT: a boundary ruling on the item permalink. The "
        "anchor is already in hand."
    ),
    "update_profile_field": (
        "update_profile_field is sanctioned and cannot be performed. WHAT IS "
        "MEASURED, live on 2026-08-30 and CONTRADICTING WHAT THIS SERVER USED "
        "TO SAY: profile editors ARE addressed by url. Three of them are "
        "ordinary anchors on his own profile -- /in/<member>/edit/intro/, "
        "/in/<member>/edit/forms/summary/new/ and "
        "/in/<member>/overlay/contact-info/ -- and the live page carries 2 "
        "forms where every tracked profile fixture carries 0. NO SURFACE: "
        "'/edit/' is on readonly._FORBIDDEN_URL_SUBSTRINGS, checked before "
        "the allowlist and not shortened for a write, so the two edit "
        "addresses are refused twice over. NO CONTROL: contenteditable == 0 "
        "and no field inside any editor has ever been observed, so even given "
        "the address there is nothing measured to type into. WHAT WOULD LIFT "
        "IT: a boundary ruling on the /in/<member>/edit/ family, and a census "
        "of one opened editor."
    ),
    "update_setting": (
        "update_setting is sanctioned and cannot be performed. WHAT IS "
        "MEASURED, live on 2026-08-30: every individual setting IS its own "
        "address -- /mypreferences/d/settings/language, "
        "/mypreferences/d/dark-mode, /mypreferences/d/categories/privacy and "
        "so on, 33 links in total -- and the surface that lists them carries "
        "ZERO forms and ONE button. So settings are url-addressed and the "
        "page that lists them switches nothing. NO CONTROL: no page below the "
        "index has ever been loaded, so no toggle has ever been observed. NO "
        "SURFACE: '/mypreferences/d/categories/' and '/settings/' are both on "
        "the forbidden list, which between them refuse the category pages and "
        "the /mypreferences/d/settings/<name> family. WHAT WOULD LIFT IT: a "
        "boundary ruling on ONE named setting page, and a census of it. Note "
        "which settings sit in that family before ruling: 'Close and delete "
        "account' and 'Hibernate account' are two of the 33."
    ),
    "send_invitation": (
        "send_invitation is sanctioned and cannot be performed. WHAT IS "
        "MEASURED, and it answers the question that mattered most here: THERE "
        "IS A ROUTE THAT COSTS NO BADGE. The invitation control was found on "
        "his OWN PROFILE -- 9 buttons whose accessible name ends ' to "
        "connect' -- a page this server already loads and which carries no "
        "pending-invitation counter. So this action never needs /mynetwork/, "
        "whose load is refused precisely because it consumes that counter. "
        "WHAT STOPS IT ANYWAY, and both halves are real. FIRST, THE LABEL IS "
        "THE OTHER PERSON'S NAME: LinkedIn writes it into the aria-label, the "
        "census blanks a name before counting it, and reading the full label "
        "in order to aim a click would mean collecting a third party's "
        "identity to populate a confirm block. The suffix is the whole of "
        "what may be known without paying that, and a suffix selects nine "
        "controls, not one. SECOND, NO SURFACE: '/invite', 'invitation' and "
        "'/connect' are all on the forbidden list. WHAT WOULD LIFT IT: a "
        "ruling that this server may hold ONE named person's identity long "
        "enough to show it to him and aim one click -- which is a question "
        "about him and a stranger, not a measurement, and is his to answer."
    ),
    "send_message": (
        "send_message is sanctioned and cannot be performed. NO SURFACE: "
        "'/messaging/compose' is on readonly._FORBIDDEN_URL_SUBSTRINGS -- it "
        "is the entry that SURVIVED when the blanket '/messaging' ban was "
        "narrowed on 2026-08-26 so he could read his own inbox, and it was "
        "kept for exactly this. NO CONTROL: no composer has ever been "
        "observed, because measuring one costs something this gate will not "
        "spend on his behalf. THE COST, STATED PRECISELY AND MEASURED "
        "TWICE: /messaging/ DOES NOT STAY ON A LIST -- LinkedIn redirects it "
        "into one specific conversation of its own choosing, so loading it "
        "OPENS SOMEBODY'S THREAD, and whether that fires them a read receipt "
        "is an honest unknown believed unmeasurable from outside. The nav "
        "badge also counts new-since-last-visit and resets when the tab is "
        "opened. THIS PREVIEW THEREFORE DOES NOT LOAD MESSAGING. It reads the "
        "badge off a page already open and stops. If the surface is to be "
        "measured, HE calls linkedin_open_messaging -- the tool that pays that "
        "cost knowingly, and whose own name says so. WHAT WOULD LIFT IT: that "
        "call, plus a boundary ruling on the composer."
    ),
}


def _refuse_unperformable(spec: WriteSpec) -> None:
    """Raise unless this action is one :func:`perform` may execute at all.

    Each refusal names its OWN reason. The generic sentence at the bottom is a
    backstop for a future spec, not the answer for any action that exists
    today: "not performable" is true of all three and explains none of them,
    and three different gaps that print the same sentence teach a reader that
    the sentence carries no information.
    """
    if spec.action in PERFORMABLE:
        return
    if spec.action in _NINE_REFUSALS:
        raise WriteAttemptError(_NINE_REFUSALS[spec.action])
    # follow_company WAS HERE UNTIL 2026-08-30 and is now DEAD as well as
    # superseded -- follow entered PERFORMABLE, so the guard at the top of this
    # function returns before reaching it. Its argument was that THE UNDO
    # CANNOT BE AIMED: a posting names its employer by slug, the unfollow
    # surface addresses rows by numeric id, and nothing resolves one to the
    # other. THAT REMAINS TRUE and was re-measured the day it was removed --
    # linkedin_job_detail on a live posting returned a slug company_url, which
    # settles the cheapest of the two routes the previous audit named. What
    # changed is that the fact belongs on the SPEC, in reversible_by, where the
    # gate reads it out to him before he confirms, rather than here where it
    # decided for him. Removed rather than reworded, because this function is
    # for actions that are sanctioned and NOT performed.
    #
    # apply_job WAS HERE UNTIL 2026-08-26, and it was DEAD as well as false.
    # Dead because apply entered PERFORMABLE and the guard at the top of this
    # function returns before reaching it. False because its two load-bearing
    # sentences had both been overtaken: "THE APPLY FLOW IS NOT MEASURED AT
    # ALL" (it was captured 2026-08-24) and "It has NOT been run" (it was run
    # that same day). Twenty-eight unreachable lines asserting two things that
    # had stopped being true.
    #
    # Removed rather than reworded, because this function is for actions that
    # are sanctioned and NOT performed, and apply is performed. The half that
    # SURVIVES any better capture -- that the off-site route submits on a third
    # party's applicant-tracking system and is none of this server's business
    # -- lives on the spec, in wrong_state_note, where the gate reads it out.
    if spec.action == "set_open_to_work":
        raise WriteAttemptError(
            "set_open_to_work is sanctioned and cannot be performed: its "
            "editor is not addressed by a url at all. Measured 2026-08-24 -- "
            "237 distinct urls and 37 payload paths across five profile "
            "captures, zero of which reach it. It opens as a modal from a "
            "control on his own profile, and the single click that would first "
            "SHOW that editor is also the first click that could CHANGE it. "
            "This is the one action in the design a current employer can see."
        )
    raise WriteAttemptError(
        f"{spec.action!r} is not performable. The complete performable set is "
        f"{sorted(PERFORMABLE)}, and it is deliberately smaller than the "
        "sanctioned set."
    )


#: Which surface each target kind's write lands on. Named for the auth-wall
#: check's message, which is read by a human at the worst possible moment.
_WRITE_SURFACE: dict[str, str] = {
    "job_id": "job posting",
    "company_id": "followed companies",
}


def _assert_landed_on_target(
    spec: WriteSpec, grant: WriteGrant, landed: str
) -> None:
    """Refuse unless the browser is on the page this grant is permission for.

    Two shapes, because the two surfaces are identified differently and
    pretending otherwise would make one of the checks vacuous. A POSTING is
    identified by the id inside its url, and LinkedIn also serves a slug form
    of the same posting, so the id is compared rather than the whole string. A
    LIST has one address and no id at all; the target selects a row, so the url
    is compared whole and the row is enforced by the selector the click is
    built from -- which is the only place it can be.
    """
    if spec.target_kind == "job_id":
        landed_id = re.search(dom.JOB_HREF, str(landed))
        if not landed_id or landed_id.group(1) != grant.target:
            raise WriteAttemptError(
                f"refusing to click: the grant is for job {grant.target} and "
                f"the browser landed on {landed!r}, which is not that posting."
            )
        return
    expected = str(spec.url_template or "").format(target=grant.target)
    if str(landed).rstrip("/") != expected.rstrip("/"):
        raise WriteAttemptError(
            f"refusing to click: this action is performed on {expected!r} and "
            f"the browser landed on {landed!r}. A list write is anchored to a "
            "row on one page, so landing anywhere else means the row this "
            "grant names is not on the screen."
        )


#: Said at the end of every save diagnostic, because a filtered list that does
#: not say it is filtered reads as a complete one -- and a reader who believes
#: he has seen every control will conclude the save control is absent when it
#: is merely differently worded.
_SAVE_FILTER_NOTE = (
    "Filtered, and deliberately: only controls under <main> whose accessible "
    "name carries the whole word save/saved/unsave/unsaved are reported, and "
    "each is reduced by shape.census_shape. A job posting names its hiring "
    "team and a 'people also viewed' rail, so the full control list is never "
    "printed. A rename to a word outside that set therefore shows up here as "
    "zero candidates against a non-zero scan, which is itself the finding."
)


def _save_readiness_note(
    reading: dict[str, Any], waited: dict[str, Any]
) -> str:
    """WHICH OF THE TWO FAILURES THIS IS, said before anything is enumerated.

    A refusal that lists what it found is an improvement on one that does not,
    and it is still not a diagnosis: "no save control here" is produced BOTH by
    a control that was renamed and by a page whose button layer had not
    attached when the reader looked. Those want opposite responses -- one is a
    vocabulary problem, the other is a timing problem, and widening the
    vocabulary to cure a timing problem points a click at a guess.

    THE DISCRIMINATOR IS ``main_buttons_total`` AND IT IS MEASURED, not argued:
    the un-hydrated shell capture draws ZERO buttons under ``<main>`` while
    every posting capture that actually rendered draws between two and twelve.
    So no buttons at all is a page that has not attached, and buttons without a
    save control among them is a page that has.

    ``waited`` has NO DEFAULT on purpose. It is the outcome of the wait, it
    cannot be inferred from the reading, and a caller that forgot it would
    otherwise print a confident diagnosis built on a default nobody chose.
    """
    buttons = reading.get("main_buttons_total")
    # THE NUMBERS THAT HAPPENED, not the constant that was supposed to. A
    # refusal quoting a timeout it did not actually spend is a small lie that
    # costs a reader an afternoon.
    spent = f"{waited.get('waited_ms')}ms of a {waited.get('timeout_ms')}ms wait"

    if waited.get("ready"):
        # The control attached, so this is not a timing failure at all. Reached
        # when more than one save control resolved -- ``save_state`` refuses a
        # count it cannot scope, and that refusal is not about hydration.
        return (
            f"THE CONTROL LAYER IS READY: the save control attached after "
            f"{spent}, so nothing below is a timing artefact and re-running "
            "will not change it."
        )

    # A LOCATOR THAT COULD NOT BE ASKED IS NOT A PAGE THAT SAID NO. Playwright
    # reports a genuine expiry as TimeoutError; anything else means the
    # question never reached the page, and reading it as "not ready" would
    # invent a hydration finding out of a broken instrument.
    failure = waited.get("failure")
    if failure and failure != "TimeoutError":
        return (
            f"THE READINESS CHECK ITSELF FAILED after {spent}, with "
            f"{failure}. That is not evidence the page was unready and not "
            "evidence it was ready -- the question never got an answer. "
            "Nothing below should be read as a finding about LinkedIn."
        )

    if buttons is None:
        return (
            f"WHETHER THE PAGE WAS READY IS UNKNOWN: the save control did not "
            f"attach in {spent}, and the button count that would say whether "
            "ANY control layer had rendered could not be taken either. Do not "
            "read the list below as evidence about LinkedIn's vocabulary; it "
            "is not established that the page had finished drawing."
        )

    if buttons == 0:
        return (
            f"THE PAGE NEVER BECAME READY: the save control did not attach in "
            f"{spent} and <main> carries ZERO buttons of any kind. Measured "
            "across every capture in this repo, an un-hydrated shell draws "
            "zero and a posting that rendered draws between two and twelve -- "
            "so this is a page whose interactive layer had not attached, NOT a "
            "control that was renamed. DO NOT WIDEN shape.SAVE_LABELS on this "
            "reading: there is no label here to widen it with. Any text that "
            "WAS read (a title, an employer) arrives in the server-rendered "
            "document and says nothing about whether the controls had drawn."
        )

    return (
        f"THE PAGE WAS READY AND THE CONTROL WAS NOT THERE: <main> carries "
        f"{buttons} buttons, so the interactive layer HAD attached, and the "
        f"save control still did not appear in {spent}. "
        # THE COUNT TRAVELS WITH THE VERDICT, because "ready" is a threshold
        # answer and a threshold answer hides how close it came. Flagged on
        # 2026-08-30 by a live reading of THREE buttons, which passes and sits
        # far below the 8-12 that fully drawn captures carry.
        f"CAUTION ON HOW STRONG THAT IS: the captures in this repo draw "
        f"{dom.SAVE_CAPTURE_BUTTONS_FULL} buttons when fully drawn and "
        f"{dom.SAVE_CAPTURE_BUTTONS_MIN} on the one partially drawn capture -- "
        f"and ALL FOUR carried exactly one save control regardless of count. A "
        f"page drawing {buttons} buttons and NO save control therefore matches "
        "no capture on record, so 'ready' here is the button test passing, not "
        "a page anybody has seen behave this way. That makes this a vocabulary "
        "finding rather than a timing one, and a weakly evidenced one. It is "
        "not licence to guess a label; see below for what was actually read."
    )


def _save_candidates_note(
    reading: dict[str, Any], *, waited: dict[str, Any]
) -> str:
    """Turn the wider reading into the sentence the refusal used to lack.

    FOUR OUTCOMES, KEPT FOUR. The distinction this function exists to protect
    is the one the apply scan already pays for: an empty list and an unfinished
    scan are not the same answer, and a reader handed ``[]`` for both learns
    the opposite of the truth in one of the two cases.

    Defensive about its input on purpose -- ``.get`` with a refusing default,
    so a payload that predates a field reads as "did not finish" rather than as
    "finished and found nothing".

    THE READINESS VERDICT LEADS, because it decides how everything after it
    should be read: the same candidate list means "LinkedIn renamed the
    control" on a page that had drawn and means nothing at all on one that had
    not. See :func:`_save_readiness_note`.
    """
    lead = _save_readiness_note(reading, waited)
    total = reading.get("buttons_total")
    candidates = list(reading.get("candidates") or [])
    # NOT DEFAULTED TO len(candidates), which is the tempting wrong answer:
    # the candidate list is a SET of shapes, so two controls both labelled
    # "Saved" collapse to one entry -- and "the page drew two save controls"
    # is the fact that separates a rename from a page this reader cannot
    # scope. A count that is missing says so rather than being reconstructed.
    matched = reading.get("matched_total", None)
    matched = "unreported" if matched is None else matched

    # The split, printed everywhere the total is printed. A page whose button
    # layer has not attached still draws its ANCHORS, so "2 labelled controls"
    # means something entirely different depending on which kind they were --
    # and it was the undifferentiated total that made the live 2-then-1 reading
    # ambiguous in the first place.
    split = (
        f"{reading.get('labelled_buttons')} button(s) and "
        f"{reading.get('labelled_links')} link(s), with "
        f"{reading.get('main_buttons_total')} button(s) of any kind under "
        "<main>"
    )

    if not reading.get("scan_complete"):
        if isinstance(total, int) and total > dom.SAVE_SCAN_LIMIT:
            head = (
                f"WHAT WAS ON THE PAGE IS UNKNOWN: it drew {total} labelled "
                f"controls, past the {dom.SAVE_SCAN_LIMIT} this reader will "
                "walk, so the sweep was not run at all. That count is itself "
                "unlike any posting this repo has captured."
            )
        else:
            head = (
                f"WHAT WAS ON THE PAGE IS ONLY PARTLY KNOWN: the sweep over "
                f"{total} labelled controls DID NOT FINISH, so the list below "
                f"is a floor and not an inventory -- {candidates}. The part "
                f"that WAS counted: {split}."
            )
        return f"{lead} {head} {_SAVE_FILTER_NOTE}"

    if not candidates:
        return (
            f"{lead} WHAT WAS ON THE PAGE: {total} labelled controls -- "
            f"{split} -- ALL of them read, and NOT ONE carries a save word. "
            f"{_SAVE_FILTER_NOTE}"
        )

    return (
        f"{lead} WHAT WAS ON THE PAGE: {total} labelled controls -- {split} "
        f"-- ALL of them read. Save-worded controls: {matched}, reading "
        f"{candidates}. THAT IS THE MEASUREMENT THIS REFUSAL EXISTS TO "
        "PRODUCE -- and it is not yet the fix. Which state such a label MEANS "
        "has to be established before it is written into shape.SAVE_LABELS, "
        "because a label mapped to the wrong state points a click at the "
        "opposite action; a name that does not say its own direction is not a "
        f"measurement. {_SAVE_FILTER_NOTE}"
    )


async def _live_control(
    page: Any, spec: WriteSpec, grant: WriteGrant, anchor: str
) -> tuple[str, str, str]:
    """GATE 5, per family: re-read the very control, and build its selector.

    Returns ``(state, why, selector)``. The state comes from the CONTROL, on
    the page, right now -- never from the preview -- and the selector is built
    from a label this reader has measured rather than from anything a caller
    supplied.

    For the save pair this is an INDEPENDENT corroboration, because the preview
    took its direction from the saved list and this takes it from the button.
    For ``unfollow_company`` it is not independent -- the preview read the same
    page -- and saying so matters: what it adds there is FRESHNESS and ROW
    IDENTITY, confirming that the row keyed to this company id still exists and
    still carries exactly one unfollow button, which is the precondition a
    click needs and a list read does not.
    """
    if spec.action == "unfollow_company":
        control = await dom.read_unfollow_control(page, grant.target)
        count = int(control.get("count") or 0)
        label = str(control.get("label") or "")
        if count == 0:
            return (
                UNKNOWN,
                f"no unfollow control for company {grant.target} is on this "
                "page. That is NOT evidence he has stopped following them: "
                "this surface renders part of the list and has no pagination "
                "control, so a row that is not drawn and a Page that is not "
                "followed look identical from here.",
                "",
            )
        if count > 1:
            return (
                UNKNOWN,
                f"{count} unfollow controls resolved for company "
                f"{grant.target}. A company id must select exactly one row; "
                "more than one means the row scoping matched across rows, and "
                "picking either would be picking by position.",
                "",
            )
        if not label.startswith(anchor):
            return (
                UNKNOWN,
                f"the control is labelled {label!r}, which does not begin "
                f"{anchor!r}. That prefix is the whole of the evidence that "
                "pressing it stops a follow rather than starting one, so an "
                "unrecognised label is refused rather than interpreted.",
                "",
            )
        return (
            "following",
            f"the row for company {grant.target} draws exactly one control and "
            f"it is labelled {label!r}, which states the inverse action.",
            dom.unfollow_control_selector(grant.target),
        )

    if spec.action == "follow_company":
        # WITHOUT THIS BRANCH FOLLOW WOULD READ THE SAVE BUTTON, which is the
        # exact defect apply carried until 2026-08-26 and the reason this was
        # written BEFORE follow_company was added to PERFORMABLE rather than
        # after. Gate 5 exists to re-read THE VERY CONTROL the click will land
        # on; corroborating a different button on the same page is not a
        # weaker version of that, it is a different check wearing its name.
        #
        # NOT INDEPENDENT of the preview, and saying so matters. The preview
        # read this same control on this same page -- ``state_from`` is
        # ``posting_page`` -- so what this adds is FRESHNESS, not a second
        # source. It is still worth taking: a posting hydrates after it lands,
        # and the follow control is measured to be absent before it settles
        # and present after, so the reading at click time is the one that
        # describes the button about to be pressed.
        control = await dom.read_follow_control(page)
        verdict = shape.follow_state(
            control.get("label"), count=int(control.get("count") or 0)
        )
        state = str(verdict.get("state") or UNKNOWN)
        why = str(verdict.get("why") or "")
        if state != spec.from_state:
            # No selector, so the caller stops. Returning the state and the
            # reason rather than raising keeps the refusal in one place --
            # perform() prints spec.wrong_state_note beside it.
            return (state, why, "")
        label = anchor_label_for(spec) or ""
        return (state, why, dom.follow_control_selector(label))

    if spec.action == "apply_job":
        # WITHOUT THIS BRANCH APPLY READ THE SAVE BUTTON. The fall-through
        # below is the save family's, and gate 5 is supposed to re-read THE
        # VERY CONTROL the click will land on -- so for apply it has to be the
        # apply control or the gate is corroborating the wrong element.
        control = await dom.read_apply_control(page)
        verdict = shape.apply_route(
            control.get("label"),
            control.get("href"),
            count=int(control.get("count") or 0),
            job_id=grant.target,
            link_target=control.get("link_target"),
        )
        route = str(verdict.get("route") or UNKNOWN)
        why = str(verdict.get("why") or "")
        if route != "linkedin_apply":
            # Includes the OFF-SITE route, and that refusal is the important
            # one: an off-site posting hands the application to a third party
            # on their domain under their terms. Returning no selector is what
            # stops it, since the caller requires one.
            return (route, why, "")
        return ("linkedin_apply", why, dom.LINKEDIN_APPLY_CONTROL)

    # GATE 5a: WAIT FOR THE CONTROL, DO NOT BET ON A DURATION.
    #
    # Until 2026-08-30 this read fired whenever the navigation's flat settle
    # happened to end, and two live redemptions ninety seconds apart read
    # 2 then 1 labelled controls on a posting that renders seven -- a count
    # that MOVED, which a renamed control cannot do. Costs nothing on a page
    # that is already drawn: an attached element satisfies the wait at once.
    waited = await dom.wait_for_save_control(page, dom.SAVE_READY_TIMEOUT_MS)

    control = await dom.read_save_control(page)
    verdict = shape.save_state(
        control.get("label"), count=int(control.get("count") or 0)
    )
    state = str(verdict.get("state") or UNKNOWN)
    why = str(verdict.get("why") or "")
    if state == UNKNOWN:
        # A REFUSAL THAT REPORTS NOTHING IT SAW MAKES GUESSING THE ONLY WAY
        # FORWARD, and on a toggle a guessed label performs the opposite
        # action -- which is the failure this whole gate exists to prevent.
        # So the reading that is about to refuse goes and looks again, wider,
        # and prints what is there. See dom.read_save_candidates for why a
        # second read is required rather than a better print of the first.
        #
        # ON THE UNKNOWN BRANCH ONLY. A state that came back KNOWN and merely
        # wrong was read off a label the message already names, and paying for
        # a second sweep to repeat it would be spending round trips on prose.
        reading = await dom.read_save_candidates(page)
        why = f"{why} {_save_candidates_note(reading, waited=waited)}"
    return (state, why, dom.save_control_selector(anchor))


async def _verify_after(
    navigator: Any,
    page: Any,
    spec: WriteSpec,
    grant: WriteGrant,
    observation: Observation,
) -> tuple[str, str, str]:
    """Read whether it landed, and read it somewhere the click did not reach.

    Returns ``(state, why, read_from_url)``.

    THE SAVE PAIR gets the ideal shape: the click happens on the posting and
    the confirmation is read off the saved list, a different surface entirely,
    carrying LinkedIn's own per-tab count.

    THE UNFOLLOW DOES NOT, AND THIS SAYS SO INSTEAD OF IMPLYING OTHERWISE.
    There is exactly one surface that lists followed Pages, so the
    confirmation comes from RELOADING it -- a fresh navigation and a fresh
    render from LinkedIn, which is materially stronger than reading a button
    that redrew itself in place, and weaker than an independent surface. To
    stop the row's mere absence from carrying the verdict on a list that is
    never complete, the evidence is LINKEDIN'S OWN STATED TOTAL: the row must
    be gone AND the count must have dropped by exactly one. A row that vanished
    while the total held is a row that scrolled out of a partial list, and it
    is reported as unknown.
    """
    if spec.action == "follow_company":
        # THE WEAKEST WITNESS CLASS IN THIS DESIGN, and it is labelled as such
        # in the text it returns rather than quietly presented as equal to the
        # other two. The control redraws itself in place, so it is testifying
        # about its own effect.
        #
        # WHY THE STRONGER READ IS NOT AVAILABLE HERE, which is a fact about
        # this action and not a shortcut. The unfollow's verification works
        # because its preview read Manage Pages and therefore holds a BEFORE
        # count to compare against. A follow's preview reads the POSTING -- one
        # page load, the state and the action sharing a rendering, which is the
        # better shape for a gate -- so no before-count exists. Loading Manage
        # Pages now would produce an after-count with nothing to subtract from,
        # and that surface renders about 20 rows of a stated 58 with no
        # pagination, so a newly followed Page may not appear in it at all.
        # An absent row on a partial list is not evidence, which is the same
        # rule the unfollow path already applies in the other direction.
        control = await dom.read_follow_control(page)
        verdict = shape.follow_state(
            control.get("label"), count=int(control.get("count") or 0)
        )
        state = str(verdict.get("state") or UNKNOWN)
        why = (
            str(verdict.get("why") or "")
            + " READ OFF THE CONTROL THAT WAS JUST CLICKED, on the page it was "
            "clicked on. That is the weakest verification in this design -- "
            "the save pair is confirmed from a different surface and the "
            "unfollow from a reloaded list with LinkedIn's own total -- and it "
            "is what this action has, because its direction came from the "
            "posting rather than from a list that could be counted before and "
            "after. Open your followed companies if you want a second opinion."
        )
        return state, why, str(observation.facts_url or "")

    if spec.action != "unfollow_company":
        landed = await _load(navigator, page, SAVED_LIST_URL, surface="saved jobs")
        state, why = await _read_saved_state(page, grant.target)
        return state, why, landed

    landed = await _load(
        navigator, page, FOLLOWED_PAGES_URL, surface="followed companies"
    )
    facts, state, why = await _read_followed_state(page, grant.target)
    if state == "following":
        return (
            "following",
            "the row for this company is still on the page after the click, so "
            "the unfollow did not take effect. " + why,
            landed,
        )
    before = observation.facts.get("total_followed")
    after = facts.get("total_followed")
    if isinstance(before, int) and isinstance(after, int) and after == before - 1:
        return (
            "not_following",
            f"the row is gone AND LinkedIn's own total dropped from {before} "
            f"to {after}. The count is the evidence here; on a list that "
            "renders part of itself, an absent row alone would not be.",
            landed,
        )
    return (
        UNKNOWN,
        "the row is not on the page, but LinkedIn's own total does not "
        f"corroborate a departure (it read {before!r} before and {after!r} "
        "after). This surface renders part of the list, so an absent row is "
        "not by itself evidence of anything. Open your followed companies and "
        "look. " + why,
        landed,
    )


async def _apply_submit_gate(page: Any) -> dict[str, Any]:
    """THE GATE BETWEEN THE TWO CLICKS, and the reason apply may be performed.

    The first click opens the modal and submits nothing. This decides whether
    the second one may happen, by READING the modal that just opened rather
    than trusting that it resembles the one that was measured.

    WHY THIS IS THE WHOLE SAFETY ARGUMENT. Exactly ONE posting's apply flow has
    ever been observed: a single screen, one enabled "Submit application", no
    Next. Generalising from one observation to every posting on LinkedIn would
    be a guess, and the thing guessed about cannot be taken back. So the
    generalisation is not made -- the shape is re-checked live, and anything
    that is not the measured shape STOPS.

    An abort here is cheap, which is why this is the right place to stop: the
    first click opened a modal and may leave a draft in his job tracker, and a
    draft is not an application. Stopping costs a draft. Being wrong costs an
    application nobody can withdraw.

    FIVE CONDITIONS, all required:

    1. the modal rendered at all;
    2. exactly one control carries LinkedIn's own submit test hook;
    3. that control is visible and not disabled;
    4. its accessible name corroborates the hook -- both fields must agree,
       because the hook still says "easy-apply" while the name says "Submit",
       and each has its own way of being wrong;
    5. **ZERO advance controls are visible.** This is the condition that
       catches the case nobody has measured -- a multi-step posting. A flow
       with a Next in it is a shape this package has never seen finish, and it
       will not be walked on the assumption that it resembles the one that was.
    """
    modal: dict[str, Any] = {}
    for _ in range(15):
        modal = await dom.read_apply_modal(page)
        if modal.get("modal_present") and modal.get("submit_present"):
            break
        await page.wait_for_timeout(1_000)

    out: dict[str, Any] = {
        "proceed": False,
        "selector": dom.APPLY_SUBMIT_SELECTOR,
        "modal": modal,
        "why": "",
    }
    if not modal.get("modal_present"):
        out["why"] = (
            "the apply modal never rendered after the control was clicked, so "
            "nothing was submitted. This is the same non-hydration that makes "
            "postings read as having no apply control at all."
        )
        return out
    if not modal.get("submit_present"):
        out["why"] = modal.get("why") or (
            "the modal rendered but carries no submit control this reader "
            "recognises."
        )
        return out
    if not modal.get("advance_scan_complete"):
        out["why"] = (
            "THE SCAN FOR ADVANCE CONTROLS DID NOT FINISH, so the empty list "
            "beside it means UNKNOWN and not none. This modal draws "
            f"{modal.get('buttons_total')} buttons and the reader walks at "
            f"most {dom.APPLY_ADVANCE_SCAN_LIMIT} of them, refusing rather "
            "than sampling; a control it could not read, or a locator that "
            "raised, lands here too. Condition 5 asks whether this flow has a "
            "Next in it, and an unfinished scan cannot answer that -- so the "
            "answer is no submit, on the same rule this server applies to a "
            "badge that did not render: absent is not zero."
        )
        return out
    if modal.get("advance_names"):
        out["why"] = (
            "THIS FLOW HAS MORE THAN ONE STEP -- it draws "
            f"{modal['advance_names']} alongside its submit. Only a "
            "single-screen flow has ever been measured, so a multi-step one "
            "is refused rather than walked: filling in steps nobody has seen, "
            "to reach a submit that cannot be withdrawn, is exactly the guess "
            "this server does not make. Apply on the posting yourself."
        )
        return out
    if not modal.get("submit_enabled"):
        out["why"] = (
            "the submit control is present but disabled, which means the form "
            "wants something it has not got. What that something is has never "
            "been measured, and supplying it would be guessing at required "
            "fields on an irreversible action."
        )
        return out
    name = str(modal.get("submit_name") or "")
    if "submit" not in name.lower():
        out["why"] = (
            f"the control carrying {dom.APPLY_SUBMIT_HOOK} is named {name!r}, "
            "which does not corroborate the hook. Both fields have to agree "
            "before an irreversible control is pressed."
        )
        return out

    out["proceed"] = True
    out["why"] = (
        f"single-screen flow: one enabled control named {name!r} carrying "
        f"{dom.APPLY_SUBMIT_HOOK}, and zero advance controls out of "
        f"{modal.get('buttons_total')} buttons ALL of which were read. The "
        "count is here because 'none found' is only worth anything alongside "
        "'and the search finished'."
    )
    return out


async def perform(
    navigator: Any, page: Any, grant: WriteGrant
) -> dict[str, Any]:
    """Perform the ONE action this grant is permission for. THE ONLY WRITER.

    This is the only function in this package that changes anything on
    LinkedIn, and the only one named in ``readonly.SANCTIONED_MUTATIONS``. The
    scanner still reports its click; what changed on 2026-08-23 is that the
    report is now expected, by path and function and kind, and a second one
    anywhere would fail ``tests/test_readonly.py``.

    FIVE GATES BEFORE ANYTHING MOVES, and they are not redundant -- each
    refuses something the others let through:

    1. **The flag.** Writes are off per process unless deliberately enabled.
    2. **The grant, REDEEMED.** ``perform`` does not redeem its own permission;
       it requires a grant that :func:`consume` has already burned. So the
       token check -- single use, right action, right target, not expired --
       has provably happened before this function is entered, and a caller
       cannot skip it by handing over a fresh grant object.
    3. **The write door**, :func:`assert_write_url`: the url is REBUILT from
       the grant, never accepted, and the forbidden list is not shortened.
    4. **The read door**, ``readonly.assert_read_url``, on the same navigation,
       plus the auth-wall check. The grant is permission; the url check is the
       door; a navigation passes both or it does not happen.
    5. **THE LIVE LABEL.** The control about to be clicked is re-read ON THE
       PAGE, and must be wearing exactly the accessible name that means the
       state this action is valid from.

    WHY GATE 5 REPLACED THE THING THIS DOCSTRING USED TO PROMISE. It said the
    click would "re-check the observation's age before it moves anything". That
    cannot work as stated, and the arithmetic says so: an observation dies in
    30 seconds while a grant lives for 120, because one is a reading of
    LinkedIn and the other is a human deciding. Enforcing the 30 would refuse
    every confirmation a person actually took time over; enforcing the 120
    would be the grant check wearing a second name. So the age is REPORTED --
    the operator sees how stale the preview he read was -- and the real
    precondition is a fresh read of the very control, which is strictly
    stronger than an age bound and costs nothing, since the page has to be open
    to be clicked. For ``save_job`` it is also an INDEPENDENT corroboration: the
    preview took its direction from the saved LIST, and this takes it from the
    BUTTON.

    NOTHING RAISES AFTER THE CLICK, and that is deliberate rather than sloppy.
    Once the button has been pressed, the single most important fact in the
    world is that it was pressed; an exception thrown on the way home would
    replace that fact with a stack trace, and the operator would retry and
    toggle it back. Every post-click outcome comes back as a field.

    VERIFICATION IS FROM A DIFFERENT SURFACE, always. The click happens on the
    posting; the confirmation is read off ``/jobs-tracker/?stage=saved``, the
    same corroborated list the preview used, because a control that redraws
    itself is the weakest possible witness to its own effect.

    Returns a block whose ``performed`` field has THREE values, not two:
    ``True``, ``False``, and ``"unknown"`` -- the third for a click that raised
    on the way out, where whether it dispatched is exactly what nobody knows.
    """
    # ORDER MATTERS HERE, and it is the order of how fundamental each refusal
    # is rather than the order they were written in. The flag governs whether
    # this process may write AT ALL, so it answers before anything about which
    # action was asked for -- otherwise an unperformable action with writes off
    # reports "not performable", which is true and is not the reason.
    if not writes_enabled():
        raise WriteAttemptError(
            f"writes are disabled: set {WRITES_FLAG}=1 to enable them."
        )
    if not isinstance(grant, WriteGrant):
        raise WriteAttemptError("perform takes a WriteGrant and nothing else")
    spec = spec_for_action(grant.action)
    _refuse_unperformable(spec)
    if not grant.consumed:
        raise WriteAttemptError(
            "this grant has not been redeemed. A write is performed against a "
            "grant that consume() has already burned, so the token checks -- "
            "single use, this action, this target, not expired -- have "
            "provably run. perform does not redeem its own permission."
        )

    observation = grant.observation
    if observation is None:
        raise WriteAttemptError(
            "this grant carries no reading. A grant is minted only by a "
            "preview that re-read the target live, so one without an "
            "observation was not built by preview and will not be acted on."
        )

    anchor = anchor_label_for(spec)
    if anchor is None and spec.action not in _SAVE_FAMILY:
        # A WRONG ERROR IS WORSE THAN NO ERROR. The message below is written
        # for the save family and names the save control by name; it fired on
        # an APPLY until 2026-08-26 and sent its reader off to photograph a
        # save label while the real gap was a missing branch in
        # anchor_label_for. Guarded rather than reworded, so the accurate,
        # specific text survives where it is accurate and cannot be borrowed
        # by an action it does not describe.
        raise WriteAttemptError(
            f"{spec.action!r} has no measured anchor and will not be "
            "performed. Every action perform can execute names the accessible "
            "name its control must be wearing before it may be clicked, and "
            f"anchor_label_for has no branch for {spec.action!r} -- so there "
            "is no measured label to match and a selector would have to be "
            "guessed. That is not a thing this function does on a write. Add "
            "the branch, with the label a capture actually shows."
        )
    if anchor is None:
        # UNREACHABLE THROUGH ANY SHIPPED ACTION SINCE 2026-08-30, and kept
        # DELIBERATELY rather than by inertia -- this repo's own rule is that a
        # check which cannot fail certifies nothing, so the call has to be made
        # out loud. Both save-family actions now resolve an anchor because
        # shape.SAVE_LABELS holds both states; every other performable action
        # returns from its own branch in anchor_label_for above the table
        # lookup. So nothing in PERFORMABLE can arrive here today.
        #
        # It stays because what it now catches is a REGRESSION rather than a
        # missing measurement: a save-family action lands here if and only if
        # shape.SAVE_LABELS loses the row for the state that action is valid
        # from. That is a real way to break this package -- an edit to the
        # table, a bad merge -- and the failure it would otherwise produce is a
        # None anchor reaching save_control_selector.
        #
        # It is REACHABLE ON PURPOSE from the suite, with a synthetic spec
        # whose from_state is in no table, so it is a guard that has been shown
        # failing rather than an assertion nobody has ever fired.
        raise WriteAttemptError(
            f"{spec.action!r} has no measured anchor and will not be "
            f"performed. It is valid from {spec.from_state!r}, and "
            f"shape.SAVE_LABELS maps no accessible name to that state -- it "
            f"currently holds {sorted(shape.SAVE_LABELS)}. THIS DOES NOT MEAN "
            "THE LABEL IS UNMEASURED, and it did until 2026-08-30, when the "
            "ON state was observed four times and written down. It means the "
            "table no longer carries the row this action needs, which for a "
            "shipped action is a regression rather than a gap: check what "
            "removed it. A selector is not guessed here under either reading."
        )

    # Gates 3 and 4: the write door, then the read door, on the same url.
    url = assert_write_url(
        str(spec.url_template or "").format(target=grant.target), grant
    )
    landed = await _load(
        navigator,
        page,
        url,
        surface=_WRITE_SURFACE.get(spec.target_kind, "linkedin"),
    )

    # We must be on the page the grant names -- compared by job id for a
    # posting, and whole for a list. See :func:`_assert_landed_on_target`.
    _assert_landed_on_target(spec, grant, landed)

    # Gate 5: the control itself, read live, on the page about to be clicked.
    live_state, live_why, selector = await _live_control(page, spec, grant, anchor)
    if live_state != spec.from_state or not selector:
        raise WriteAttemptError(
            f"refusing to click: {spec.action!r} is valid only from "
            f"{spec.from_state!r} and the control on the page reads "
            f"{live_state!r}. {live_why} "
            + (
                spec.wrong_state_note
                or (
                    "On a toggle, acting from the wrong state performs the "
                    "OPPOSITE action, so this stops rather than treating it "
                    "as a no-op."
                )
            )
            + " This reading is fresher than the one in the preview and it "
            "wins."
        )

    # ---- everything above may raise; nothing below does --------------------
    #
    # THIS ONE CALL SITE FIRES TWICE FOR APPLY, stated in capitals because
    # readonly.SANCTIONED_MUTATIONS says "one click in writes.perform" and a
    # reader would otherwise reasonably conclude that one click HAPPENS.
    #
    # The allowlist is keyed by (path, function, kind) and the scanner counts
    # CALL SITES, so draining a queue keeps exactly the guarantee that list was
    # written to give -- there is one place in this package that clicks, and a
    # reviewer reads it -- where a second literal page.click would create a
    # second place to audit. The queue is also what makes the SECOND GATE
    # possible: the follow-up click is appended only if a fresh read of the
    # modal says it should be, so the decision to submit is taken AFTER the
    # modal exists rather than planned before it does.
    click_error: Optional[str] = None
    clicks_made = 0
    apply_gate: Optional[dict[str, Any]] = None
    click_plan: list[str] = [selector]
    try:
        while click_plan:
            await page.click(click_plan.pop(0), timeout=CLICK_TIMEOUT_MS)
            clicks_made += 1
            if spec.action in TWO_CLICK_ACTIONS and clicks_made == 1:
                apply_gate = await _apply_submit_gate(page)
                if apply_gate["proceed"]:
                    click_plan.append(apply_gate["selector"])
    except Exception as exc:  # noqa: BLE001 - reported, never re-raised
        click_error = f"{type(exc).__name__}: {exc}"

    # The label the control changed INTO. Read for a human, never branched on.
    # This settled the missing half of shape.SAVE_LABELS on 2026-08-30 -- it
    # reported "Unsave the job" on the operator's first save -- and it is kept
    # because the NEXT rename lands the same way: the anchored reader goes to
    # count 0 and says nothing, and this says what the page drew. Note it is no
    # longer the ONLY route to that label: server._read_save_control_state
    # reports it off any posting already open, for no write, which is how the
    # row was corroborated three times before being written. SAVE FAMILY ONLY
    # -- an unfollow's row is
    # expected to LEAVE the page, so there is no control left to read back and
    # sweeping for one would report whichever neighbouring row redrew first.
    became: Optional[str] = None
    if spec.target_kind == "job_id":
        try:
            became = await dom.read_any_save_control_label(page)
        except Exception:  # noqa: BLE001 - a measurement, not a gate
            became = None

    verified_state = UNKNOWN
    verified_why = ""
    try:
        verified_state, verified_why, state_landed = await _verify_after(
            navigator, page, spec, grant, observation
        )
    except Exception as exc:  # noqa: BLE001 - the click already happened
        state_landed = (
            FOLLOWED_PAGES_URL
            if spec.action == "unfollow_company"
            else SAVED_LIST_URL
        )
        verified_why = (
            f"the verification read itself failed ({type(exc).__name__}: "
            f"{exc}), so this says nothing about whether the click landed. "
            f"Open {state_landed} and look."
        )

    # THREE OUTCOMES, DECIDED BY THE VERIFICATION AND NOT BY THE CLICK.
    #
    # An earlier draft of this branched on ``click_error`` as well, and both of
    # its last two arms returned UNKNOWN -- a distinction that read as
    # meaningful and computed nothing. Worse than redundant: it implied the
    # click's own success was evidence, and it is not. A click that raised on
    # the way out may still have dispatched, and a click that returned cleanly
    # may still have changed nothing. The saved list is the witness; the click
    # is the thing being witnessed. ``click_error`` is REPORTED, in the
    # ``clicked`` block, where a reader can weigh it -- it just does not get a
    # vote here.
    verified = verified_state == spec.to_state
    if verified:
        performed: Any = True
    elif verified_state == spec.from_state:
        performed = False
    else:
        performed = UNKNOWN

    target_block: dict[str, Any] = {"url": url}
    if spec.target_kind == "job_id":
        target_block["job_id"] = grant.target
        target_block["title"] = observation.facts.get("title")
        target_block["company"] = observation.facts.get("company")
    else:
        target_block["company_id"] = grant.target
        target_block["company"] = observation.facts.get("company")

    return {
        "action": spec.action,
        "what": spec.summary,
        "target": target_block,
        "performed": performed,
        "clicked": {
            "selector": selector,
            "on": landed,
            "state_before": live_state,
            "read_from": "the control itself, immediately before the click",
            "error": click_error,
        },
        "verified": verified,
        "verification": {
            "expected_state": spec.to_state,
            "observed_state": verified_state,
            "read_from": state_landed,
            "why": verified_why,
            "surface": (
                (
                    "THE SAME PAGE, RELOADED, and there is no other: LinkedIn "
                    "lists followed Pages on exactly one surface. A fresh "
                    "navigation is a fresh render from LinkedIn rather than a "
                    "control that redrew itself in place -- stronger than "
                    "reading the button just pressed, weaker than an "
                    "independent surface, and said plainly rather than "
                    "implied. The verdict rests on LinkedIn's own stated "
                    "total, not on the row's absence."
                )
                if spec.action == "unfollow_company"
                else (
                    "a DIFFERENT surface from the one clicked. A control that "
                    "redraws itself is the weakest possible witness to its own "
                    "effect, so the confirmation comes from LinkedIn's own "
                    "saved list with its own per-tab count."
                )
            ),
        },
        "preview_age_seconds": round(observation.age(), 3),
        "to_undo": spec.reversible_by,
        "newly_observed_save_label": became,
        "what_that_label_is_for": (
            (
                "the accessible name the save control wears NOW. It is "
                "recorded for a human and nothing branches on it. Both states "
                "are in shape.SAVE_LABELS since 2026-08-30, so the expected "
                "reading is the OTHER one from " + repr(anchor) + " -- this "
                "field said 'write it into shape.SAVE_LABELS and unsave_job "
                "acquires its anchor' while that row was missing, and this is "
                "the field that produced it. A name in NEITHER state is now a "
                "rename on LinkedIn's side and wants the selector re-measured, "
                "not the table widened to whatever turned up here."
            )
            if spec.target_kind == "job_id"
            else (
                "not applicable to this action: an unfollow removes its own "
                "row, so there is no control left to read back and sweeping "
                "for one would report a neighbouring row's."
            )
        ),
        # THE SURFACE IS NAMED PER ACTION, and it was not until a test caught
        # it: an unfollow whose outcome was unknown told him to go and look at
        # his SAVED JOBS. The advice not to retry is the same for both and is
        # the important half; sending him to the wrong page to check is how a
        # correct instruction becomes useless.
        "read_this_if_unsure": (
            "performed is 'unknown' when the click may or may not have "
            "dispatched. Do NOT retry on 'unknown': a retry on a toggle that "
            "did land performs the opposite action. Open "
            + (
                "your followed companies"
                if spec.action == "unfollow_company"
                else "your saved jobs"
            )
            + " and look first."
        ),
    }


# ---------------------------------------------------------------------------
# 7b. The history of this seam, kept because the reasoning is the deliverable
# ---------------------------------------------------------------------------


TOGGLE_MEASUREMENT_RECORD = """The toggle problem IS SOLVED, and it was solved by reading.

WHAT THIS RECORD REPLACED. Until 2026-08-23 :func:`perform` was a ``raise`` and
this text was its docstring, explaining why the refusal was the deliverable: the
operator's permission classifier refused LinkedIn writes, so a click authored
then could not have been exercised even once -- against the least
automation-tolerant platform in the family, on his only account. The classifier
now permits it. The click exists. This is kept as a module constant rather than
deleted because the REASONING is the deliverable and a docstring on a function
that no longer refuses would read as a description of what it does.

THE ANCHORS, frozen at BOTH hydration states in ``tests/fixtures/job_detail*.html``:

    button[aria-label="Save the job"]   -- present pre- and post-hydration
    button[aria-label="Follow"]         -- present pre- and post-hydration

Anchored on the accessible name, never on ``data-view-name`` (absent before
hydration, and GONE ENTIRELY from a posting captured one day later) and never on
a class (a build hash, byte-identical between the two follow states).

THE TOGGLE PROBLEM, WHICH WAS THE STATED BLOCKER. Both anchors are TOGGLES and
every capture frozen before 2026-08-23 showed only their OFF state, so nothing
could tell Save from Unsave or Follow from Unfollow. That was recorded as
something a write would have to establish. It was not: it was a READ nobody had
performed.

    follow, MEASURED 2026-08-23 by loading a posting from a company he
    already follows:
        not following -> button[aria-label="Follow"]
        following     -> button[aria-label="Following"]
    The two carry BYTE-IDENTICAL class attributes and the page has no
    aria-pressed anywhere, so the accessible name is the entire signal.
    Frozen at both renders in ``job_detail_following*.html``.

    save, MEASURED 2026-08-30 and the last of the four to fall:
        not saved -> button[aria-label="Save the job"]
        saved     -> button[aria-label="Unsave the job"]
    The ON label could NOT be reached by reading, and that is the one place
    this record's own thesis did not hold: there was no saved posting on the
    account to read it off, so no read anybody had failed to perform would
    have produced it. It took the write. The operator authorised a save on
    2026-08-30 and :func:`perform`'s post-click sweep reported the new name.
    NO FIXTURE CARRIES IT -- every capture predates the save -- so offline
    tests DERIVE a saved posting by relabelling the control.

    Direction for save still comes from ``linkedin_saved_jobs``, the list
    read, corroborated by LinkedIn's own per-tab count. That is a different
    source, not a weaker one, and it is named in the spec.

THE ROUND TRIP IS CLOSED, AND THE LESSON REVERSED ITSELF ONCE MORE ON THE WAY.
This section used to end: "unsave_job is built on the same path and refuses at
one named point -- anchor_label_for returns None ... 'Saved' and 'Unsave the
job' are both plausible and this server has seen neither." Every clause was
true. The measurement arrived by write, as predicted, and read "Unsave the
job".

But ONE READING FROM THE WRITE PATH WAS NOT ENOUGH TO WRITE IT DOWN, and that
is the part worth carrying. A label reached by performing its own inverse can
only be re-measured by performing it again, which is a measurement nobody can
afford to repeat and therefore one nobody can check. So the row waited for a
READ-ONLY route -- ``server._read_save_control_state``, reporting the control
off a posting already open -- and was written only after three further
observations through it agreed. Four readings, two independent routes, zero
extra writes. THE GENERAL FORM: when a measurement can only be bought with an
irreversible act, the next thing to build is not the row, it is the cheap way
to take that measurement again.
"""
