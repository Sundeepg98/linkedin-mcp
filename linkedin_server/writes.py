"""The write boundary: a grant, not a mode.

THIS MODULE CAN CHANGE ONE THING ON LINKEDIN, as of 2026-08-23: it can save a
job posting, and it can unsave one the day the unsave anchor has been measured.
It could change nothing at all until that date, and the sentence that used to
stand here said so. Both sentences were true when written; only one of them is
true now, and a boundary module that keeps the comfortable one is the exact
failure this design exists to refuse. See "WHAT IS HERE, AND WHAT STILL IS NOT"
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
at no extra load. Save is read off ``linkedin_saved_jobs``, a different
surface, because he has nothing saved and so the save control's ON state does
not exist on this account to be photographed. A different source, not a weaker
one; and the second can answer "I could not tell", which the first never has
to.

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

WHAT IS STILL NOT HERE, and it is one row of a table rather than a code path:
``unsave_job`` is built, gated and tested on exactly the same path as
``save_job``, and it REFUSES, because the accessible name LinkedIn gives the
save control when a posting IS saved has never been observed -- there is
nothing saved on the account to observe it on. See :data:`shape.SAVE_LABELS`
and :func:`anchor_label_for`. The first supervised save is the measurement that
lifts it.
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
            "button, and that is not a shortcut: he has no saved job on the "
            "account, so the save control's ON state has never been observed "
            "anywhere and could not be read even if the gate wanted to. The "
            "list read is corroborated -- it reports LinkedIn's own per-tab "
            "count and its empty state, and raises rather than returning [] "
            "when the two disagree."
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
            "this server, once writes ship: linkedin_unsave_job is sanctioned "
            "alongside this one, so the undo is inside the same boundary."
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
            "this server, once writes ship: linkedin_save_job is sanctioned."
        ),
        residue=(
            "the same ordering question as save_job, and one more: the ON "
            "state of the save control has never been seen, because there is "
            "no saved posting on the account to see it on. If the direction "
            "ever moves off the list read and onto the button, THAT is the "
            "unmeasured step."
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
        # NEVER LOADED, exactly as for set_open_to_work, and for a reason that
        # is measured rather than assumed: thirteen job captures contain the
        # apply CONTROL and not one contains what appears after it is
        # activated. Zero forms, zero file inputs, zero dialogs, zero
        # Submit/Review/Next controls, zero rendered apply pages. So there is
        # no url here, no anchor, and assert_write_url refuses this action
        # outright. Specced rather than omitted, because the operator asked for
        # apply by name and an omission would read as nobody having looked.
        url_template=None,
        url_pattern=None,
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
            "load /jobs-tracker/?stage=applied on an account that HAS an "
            "application and look for a withdraw control on a row. That "
            "requires an application to exist, which requires performing the "
            "very action whose reversibility is in question -- so this "
            "measurement cannot be taken before the first apply, only after "
            "it, and the first apply must therefore be made on the assumption "
            "that it is permanent. THE FLOW ITSELF IS THE LARGER GAP: no "
            "capture in this repo shows the LinkedIn apply form at all, so "
            "before any apply could be attempted there would have to be a "
            "capture containing the form, its fields, its resume selection, "
            "any screening questions, and the control that submits it. "
            "THAT CAPTURE NOW HAS A PROCEDURE, which is the difference "
            "between an unmeasured gap and a permanent one: "
            "scripts/_probe_apply_flow.py. It reaches the flow by NAVIGATION "
            "rather than by a click, contains no mutating call, takes the job "
            "id as a required argument so no default chooses a posting, and "
            "reads LinkedIn's own applied-tab count before and after -- "
            "because opening an Easy Apply flow MAY create a draft, which is "
            "a hypothesis nobody here has verified and is labelled as one. It "
            "has not been run."
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
                "INCLUDING YOUR CURRENT EMPLOYER AND colleagues. You are "
                "job-hunting while employed; this is the one setting in this "
                "whole design that a current employer can read."
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
}


# ---------------------------------------------------------------------------
# 2. Permanently forbidden
# ---------------------------------------------------------------------------

#: No grant is ever minted for these, and each carries its reason so a later
#: reader does not mistake the omission for something nobody got round to.
PERMANENTLY_FORBIDDEN: dict[str, str] = {
    "post_or_comment_or_like_or_share": (
        "public speech in his name, unbounded blast radius, no job-hunt value"
    ),
    "endorse_or_recommend": (
        "a statement ABOUT ANOTHER PERSON, which is not his to automate"
    ),
    "deanonymise_a_viewer": (
        "six of ten profile viewers chose anonymity; the row LinkedIn renders "
        "him is the whole of what he is entitled to"
    ),
    "profile_edit_beyond_open_to_work": (
        "his profile is a document he owns; silently editing it is a category "
        "error, not a feature"
    ),
    "delete_or_withdraw_anything": (
        "destruction is not a write this design covers, at any confirm level"
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
#              surface, because the save control's ON state does not exist on
#              this account to read: he has nothing saved. A different source,
#              not a weaker one -- it is LinkedIn's own per-tab count with a
#              distinguishable empty state -- but it costs a second page load
#              and it can answer "I could not tell", which the button never
#              needs to.
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


async def _read_posting_facts(page: Any, target: str) -> dict[str, Any]:
    """The title and employer of one posting, off the posting itself.

    Held to the SAME believability standard as ``linkedin_job_detail``: a
    shell that never drew the job still carries a server-rendered document
    title, so a title with no body is not a posting. A gate built on one would
    name a job that was not on the page.
    """
    identity = await dom.read_job_identity(page)
    detail = shape.parse_job_detail(
        await dom.read_main_text(page),
        company=identity.get("company"),
        document_title=identity.get("document_title"),
    )
    if not shape.job_detail_is_believable(detail) or not detail.get("company"):
        raise WriteAttemptError(
            f"refusing to render a confirm gate for job {target}: the posting "
            "page loaded but no posting could be read from it. LinkedIn sets "
            "the document title on the server, so a title with nothing behind "
            "it is what an unrendered shell looks like -- and a gate naming a "
            "job it did not actually read is the failure this section exists "
            "to stop."
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


async def _read_saved_state(page: Any, target: str) -> tuple[str, str]:
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
    """
    main_text = await dom.read_main_text(page)
    stated = shape.parse_tracker_tabs(main_text).get("saved")
    empty_state = shape.tracker_empty_state(main_text)

    records = await dom.harvest_linked_cards(
        page, href_pattern=dom.JOB_HREF, max_items=SAVED_LIST_MAX_ROWS
    )
    rows, _dropped = dom.parse_all(records, shape.parse_job_card)
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
            "distinguishes an empty list from a read that failed.",
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
        facts = await _read_posting_facts(page, target)
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
        facts = await _read_posting_facts(page, target)
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
        facts = await _read_posting_facts(page, target)
        state_landed = await _load(
            navigator, page, SAVED_LIST_URL, surface="saved jobs"
        )
        state, why = await _read_saved_state(page, target)
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
    else:
        where["whose"] = "your own LinkedIn profile"
        where["name"] = observation.facts.get("name")
        where["headline"] = observation.facts.get("headline")
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
#: ``follow_company`` is sanctioned and is NOT here. It is genuinely reversible
#: -- three surfaces write the inverse action into the control's own accessible
#: name -- but reversible BY HIM, BY HAND: no unfollow is sanctioned, so a
#: follow performed here is one this server cannot take back. An action whose
#: undo is hand-only does not go first, and the operator cut it from this round
#: on that ground rather than on a technical one.
#:
#: ``set_open_to_work`` is not here either, and could not be: its editor is a
#: modal that has never loaded in any capture, it holds no ``url_template``, and
#: :func:`mint` already refuses it a grant at issue. Its residue is also the one
#: irreversibility in this design that is measured in AUDIENCE rather than in
#: state -- a badge taken down is not a badge un-seen.
#:
#: ``apply_job`` is not here and is the one whose absence needs saying plainly,
#: because it is the action that was asked for by name. Its CONTROL is measured
#: -- two routes, positively distinguishable, and the identification half ships
#: as a read. Its FLOW is not: thirteen job captures contain zero forms, zero
#: file inputs, zero dialogs and zero submit controls, so nothing in this repo
#: has ever seen what a caller would have to fill in or press. It also holds no
#: ``url_template``, so :func:`mint` refuses it a grant at issue exactly as it
#: refuses Open To Work. An apply cannot be taken back by this server under any
#: circumstances, which makes it the last action in the design that should ever
#: be performed on a guessed selector.
PERFORMABLE: frozenset[str] = frozenset(
    {"save_job", "unsave_job", "unfollow_company"}
)

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
    that indirection is the whole mechanism by which ``unsave_job`` refuses
    today and works tomorrow WITHOUT A CODE CHANGE. The table maps a measured
    accessible name to the state it means; this reads it backwards, from the
    state an action is valid FROM to the name it would have to see.

        save_job    valid from ``not_saved`` -> "Save the job"  (MEASURED)
        unsave_job  valid from ``saved``     -> nothing         (NEVER SEEN)

    Add the observed ON label to ``shape.SAVE_LABELS`` and unsave acquires its
    anchor. Until somebody has actually seen it, this returns ``None`` and
    :func:`perform` refuses -- which is the correct behaviour and not a
    limitation to be worked around by picking a plausible string.

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
    for label, state in shape.SAVE_LABELS.items():
        if state == spec.from_state:
            return label
    return None


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
    if spec.action == "follow_company":
        raise WriteAttemptError(
            "follow_company is sanctioned but is not performed by this server, "
            "and the reason CHANGED on 2026-08-24 rather than going away. It "
            "used to be that no unfollow existed. One does now -- "
            "linkedin_unfollow_company is performable -- and the objection it "
            "was built to remove has been replaced by a measured one: THE UNDO "
            "CANNOT BE AIMED AT WHAT THIS WOULD CREATE. A follow is performed "
            "from a job posting, which names its employer by SLUG; the unfollow "
            "surface addresses rows by NUMERIC COMPANY ID; a census of every "
            "capture in this repo found no posting carrying an id, no "
            "Manage-Pages row carrying a slug, and no way to resolve one to "
            "the other without a network call this server does not make. And "
            "even given the id, that surface renders 20 rows of a stated 58 "
            "with no pagination control at all, so about two thirds of the "
            "list is unreachable in the one page load this server performs. "
            "WHAT WOULD LIFT THIS: a measured slug-to-id resolution on a "
            "surface already on the read allowlist, or evidence that a newly "
            "followed Page sorts into the rendered window."
        )
    if spec.action == "apply_job":
        raise WriteAttemptError(
            "apply_job is sanctioned and is NOT performed, and this is the "
            "refusal least likely to be lifted by trying harder. The apply "
            "CONTROL is measured: two routes, positively distinguishable, and "
            "linkedin_job_detail reports which one a posting uses. THE APPLY "
            "FLOW IS NOT MEASURED AT ALL. Thirteen job captures in this repo "
            "contain zero forms, zero file inputs, zero dialogs, zero "
            "screening questions and zero controls that submit anything -- "
            "nothing here has ever seen what a caller would have to fill in or "
            "press. An application cannot be withdrawn by this server under "
            "any circumstances (withdrawal is permanently forbidden), so it is "
            "the last action in this design that may be attempted on a guessed "
            "selector. AND HALF OF IT IS NOT THIS SERVER'S TO PERFORM EVEN "
            "THEN: the off-site route submits on a third party's applicant- "
            "tracking system, which this server was not built for and has no "
            "business driving. "
            "WHAT WOULD LIFT THE FIRST HALF, so this reads as UNMEASURED "
            "rather than as permanent: scripts/_probe_apply_flow.py captures "
            "the LinkedIn-hosted flow and inventories exactly the controls "
            "every existing capture lacks. It NAVIGATES rather than clicks -- "
            "LinkedIn draws the apply control as a link, so the flow is "
            "reachable without pressing anything -- and the package's own "
            "scanner finds zero mutating calls in it. It has NOT been run. "
            "Run it with him present, on a posting whose apply_path reads "
            "'linkedin_apply'."
        )
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

    control = await dom.read_save_control(page)
    verdict = shape.save_state(
        control.get("label"), count=int(control.get("count") or 0)
    )
    return (
        str(verdict.get("state") or UNKNOWN),
        str(verdict.get("why") or ""),
        dom.save_control_selector(anchor),
    )


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
    if anchor is None:
        raise WriteAttemptError(
            f"{spec.action!r} has no measured anchor and will not be "
            f"performed. It is valid from {spec.from_state!r}, and the "
            "accessible name the save control wears in that state has NEVER "
            "BEEN OBSERVED -- every capture this repo holds shows the OFF "
            f"state {sorted(shape.SAVE_LABELS)}, because there is nothing "
            "saved on the account to photograph the other one on. A selector "
            "cannot be guessed here: 'Saved' and 'Unsave the job' are both "
            "plausible and neither has been seen. THE SUPERVISED SAVE IS THE "
            "MEASUREMENT -- this function reports the label the control "
            "changes into, and writing that one line into shape.SAVE_LABELS "
            "is what lifts this refusal."
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
    click_error: Optional[str] = None
    try:
        await page.click(selector, timeout=CLICK_TIMEOUT_MS)
    except Exception as exc:  # noqa: BLE001 - reported, never re-raised
        click_error = f"{type(exc).__name__}: {exc}"

    # The label the control changed INTO. Read for a human, never branched on:
    # this is the one measurement that can settle the missing half of
    # shape.SAVE_LABELS, and it can only be taken here, immediately after a
    # real save on a real account. SAVE FAMILY ONLY -- an unfollow's row is
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
                "recorded for a human and nothing branches on it. If it is not "
                f"{anchor!r}, it is the state this repo has never been able to "
                "photograph -- write it into shape.SAVE_LABELS and unsave_job "
                "acquires its anchor."
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

    save: the ON state of the save control has NOT been observed, and cannot
    be by reading -- he has no saved posting on the account to observe it on.
    Direction for save therefore comes from ``linkedin_saved_jobs``, the list
    read, which is corroborated by LinkedIn's own per-tab count. That is a
    different source, not a weaker one, and it is named in the spec.

THAT REMAINING HALF IS NOW THE ONLY THING BETWEEN THIS SERVER AND A ROUND TRIP.
``save_job`` has its anchor and performs. ``unsave_job`` is built on the same
path and refuses at one named point -- :func:`anchor_label_for` returns None,
because ``shape.SAVE_LABELS`` has no entry for the saved state. The supervised
save is the measurement that fills it: :func:`perform` reads the label the
control changes into and reports it for a human to write down. One line, and it
must be measured rather than guessed -- "Saved" and "Unsave the job" are both
plausible and this server has seen neither.
"""
