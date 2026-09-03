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
from typing import Any, Optional, Union
from urllib.parse import urlsplit

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
class Unverifiable:
    """THE DECLARATION THAT AN OUTCOME CANNOT BE CONFIRMED, in three parts.

    Added 2026-09-01 on the operator's ruling that an unverifiable outcome is a
    shippable outcome PROVIDED IT SAYS SO. He was shown what he was accepting
    -- a write that fires and cannot tell him whether it worked, and that for
    an invitation or a message he would be checking after the fact, on a person
    -- and took it. This class is the "provided it says so".

    WHY A STRUCTURE AND NOT A SENTENCE. Three separate things have to reach
    him, and a paragraph that carries all three is a paragraph that can lose
    one without anything noticing. The field that goes missing is always the
    third, because the first two are about the software and only the third is
    about him:

    * ``surface_that_would_confirm`` -- WHAT would settle it, named.
    * ``why_it_cannot`` -- why this server cannot read that surface. The
      MEASUREMENT, not a shrug.
    * ``what_he_must_do`` -- the instruction he can act on. "Open your Sent
      Invitations and look" is the shape.

    THE DISTINCTION THIS EXISTS TO PROTECT, and it is the whole content of the
    ruling: A CHECK THAT CANNOT PASS MAY NEVER SHIP AS THOUGH IT MIGHT. That
    was ``apply_job``'s defect -- a ``to_state`` compared against a reader that
    could never return it, presented as a verification. What is permitted now
    is the opposite: a write that declares up front that its outcome is
    unverifiable and names why. Never compare against a reader that cannot
    return the value. If there is no surface, say there is none.

    ``tests/test_unverifiable_outcomes.py`` enforces that an action has EXACTLY
    ONE of {a verification branch in ``_verify_after``, one of these} -- never
    neither, and never both. Both would be the ``apply_job`` shape wearing a
    disclosure as cover.
    """

    surface_that_would_confirm: str
    why_it_cannot: str
    what_he_must_do: str

    def as_block(self) -> dict[str, str]:
        """The three parts, for the preview AND for the result.

        Both, deliberately. He reads the preview before deciding and the
        result after acting, and the sentence he needs after acting is the one
        telling him what to go and look at.
        """
        return {
            "outcome_is_verifiable": "NO",
            "what_would_confirm_it": self.surface_that_would_confirm,
            "why_this_server_cannot": self.why_it_cannot,
            "what_you_must_do_to_find_out": self.what_he_must_do,
        }


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
    #: THE DESTINATIONS A MULTI-STATE ACTION MAY TAKE, mapped to who can see
    #: each. Empty for a binary toggle.
    #:
    #: THAT FIRST LINE SAID "For a setting with an audience: who can see each
    #: destination" UNTIL 2026-08-31, and it under-described the field's real
    #: job in a way that mattered. ``_direction`` validates BOTH the requested
    #: destination AND the measured origin against ``sorted(spec.audiences)``
    #: and refuses anything absent from it -- so THE KEYS ARE THE ENUMERATION
    #: OF LEGAL STATES, and the audience text is what hangs off them. A reader
    #: who took the old sentence literally would conclude that an action with
    #: no audience should leave this empty, which for a multi-state action
    #: makes ``_direction`` refuse every destination there is.
    #:
    #: The correction is not cosmetic: ``update_setting`` covers dark mode,
    #: which HAS no audience and still needs its three states enumerated here.
    #: Its values say "NOBODY" in words rather than being left blank, because
    #: a blank would be indistinguishable from nobody having filled it in.
    audiences: dict[str, str] = field(default_factory=dict)
    irreversible: bool = False
    spends: Optional[str] = None
    #: THE STATE THAT MEANS "IT DID NOT HAPPEN", when that is not the state
    #: the action is valid FROM. Added 2026-08-31 for apply.
    #:
    #: ``perform`` decides between False and "unknown" by comparing the
    #: verification against ``from_state``, which works for a TOGGLE because a
    #: toggle that did not move is still in the state it was valid from. Apply
    #: is not a toggle: its ``from_state`` is ``"linkedin_apply"``, a claim
    #: about which ROUTE the posting's control takes, and the surface that
    #: verifies an apply -- the tracker's Applied tab -- establishes nothing
    #: about a control on a posting. It can say an application exists or,
    #: when LinkedIn's own count corroborates the whole list was drawn, that
    #: none does. That second answer is what this names.
    #:
    #: Without it, "no application exists" fell through to ``"unknown"``, and
    #: ``"unknown"`` on this action is the one answer a caller cannot resolve
    #: by retrying -- the docstring forbids the retry, because a retry on an
    #: act that may have half-landed is the failure being guarded against.
    not_performed_state: Optional[str] = None
    #: THE STATE THE CLICK-TIME READING MUST REPORT, when that is NOT the state
    #: the PREVIEW's reading reports. ``None`` means they are the same string,
    #: which is true of every action but one.
    #:
    #: ADDED 2026-09-02, AND IT IS THE TENTH INSTANCE OF ONE PATTERN.
    #: ``from_state`` is compared against a live reading TWICE, at opposite
    #: ends of a write, and the two readings are not taken off the same thing:
    #:
    #:   PREVIEW    ``_direction`` compares ``observation.state`` -- read off
    #:              whichever surface ``state_from`` names -- against this
    #:              spec's ``from_state``.
    #:   CLICK      ``valid_from``, from ``perform``'s gate 5, compares what
    #:              ``_live_control`` returned -- read off THE VERY CONTROL the
    #:              click will land on -- against the SAME field.
    #:
    #: For all ten binary toggles those produce the same string. NOTHING
    #: ANYWHERE REQUIRED THAT. It is the same unruled coincidence that cost
    #: nine sites when url-presence and performability turned out not to
    #: coincide, and like those it is exposed by the first action to violate
    #: it. ``tests/test_preview_state_and_click_state.py`` is the instrument.
    #:
    #: ``send_message`` VIOLATES IT BY DESIGN, which is why this field exists
    #: rather than being avoidable. Its preview reads the NAV BADGE off a page
    #: already open and deliberately does NOT load messaging -- looking costs a
    #: stranger's thread -- so its preview state is ``composer_unmeasured``,
    #: which is CORRECT and must not be "fixed": see the long note on that
    #: field in its own spec, and the wrong-state refusal that overwriting it
    #: produced once. Its click-time reading is taken on the composer, which by
    #: then is open in front of it. The two cannot be one string without one of
    #: them lying.
    #:
    #: READ BY ``valid_from`` AND BY NOTHING ELSE. ``_direction`` still reads
    #: ``from_state``, so the preview is untouched; ``anchor_label_for`` and
    #: ``perform``'s ``unchanged_state`` read it too. Naming this field for the
    #: ONE question it answers is what stops it becoming a fifth meaning
    #: stacked on the four that field already carries.
    click_from_state: Optional[str] = None
    #: DECLARED WHEN NOTHING CAN CONFIRM THIS ACTION'S OUTCOME. See
    #: :class:`Unverifiable`. ``None`` means this action HAS a verification,
    #: and ``_verify_after`` must carry a branch that can actually return the
    #: value it compares against -- the pairing is enforced, in both
    #: directions, by ``tests/test_unverifiable_outcomes.py``.
    unverifiable: Optional[Unverifiable] = None


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
            "rather than returning [] when the two disagree. "
            "IT WAS MEASURED FAILING THAT WAY ON 2026-08-30 -- the Saved "
            "tab's rows drew and the harvest returned none, so this direction "
            "source reported 'unknown' and the gate refused -- AND IT WAS "
            "FIXED ON 2026-08-31. Both dates, rather than the present tense "
            "this sentence carried for four days after it stopped being "
            "true: nothing in this gate re-measures its own prose."
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
            "same boundary rather than promised by it. "
            "THE CAVEAT THAT USED TO CLOSE THIS FIELD IS DISCHARGED, and it "
            "is quoted rather than deleted: \"the undo's own preview reads "
            "the Saved tab for its direction, and that read is currently "
            "failing, so the undo may have to be done by hand until it is "
            "fixed.\" MEASURED FAILING 2026-08-30, FIXED 2026-08-31 -- the "
            "harvest was subtracting a duplicate innerText it had never "
            "carried, and rows hidden with visibility:hidden were what broke "
            "the block walk. The dates are here because a present-tense "
            "\"currently failing\" is a claim NOTHING IN THIS GATE "
            "RE-MEASURES: it was true for one day and printed for four."
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
            "HIM, by hand, in LinkedIn's own interface. NOT this server -- "
            "and the REASON changed on 2026-08-30 without the answer "
            "changing. This field used to say linkedin_follow_company \"is "
            "sanctioned but is not performed\". It IS performed, since that "
            "day, and the verdict stands on the better ground stated inside "
            "that action's own reversible_by: A RE-FOLLOW CANNOT BE AIMED AT "
            "WHAT AN UNFOLLOW REMOVED. This surface addresses rows by NUMERIC "
            "COMPANY ID; linkedin_follow_company acts from a JOB POSTING, "
            "which names its employer by SLUG; and nothing resolves one to "
            "the other -- a census of every capture in this repo found zero "
            "postings carrying a numeric id and zero Manage-Pages rows "
            "carrying a slug. So the pair is still deliberately ASYMMETRIC "
            "and neither half pretends the other covers it: this server can "
            "stop a follow, and cannot point a follow back at the one it "
            "stopped. Read that before reading the word 'reversible' above."
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
        # THE VERIFICATION'S "it did not happen" ANSWER. See the field's own
        # comment: a tracker read cannot report ``linkedin_apply``, so without
        # this every apply that did NOT submit reported "unknown" -- on the
        # one action where "unknown" is unresolvable by retrying.
        not_performed_state="not_applied",
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
            "SECOND, AND IT IS WHAT HE IS ACCEPTING WHEN HE CONFIRMS ONE: THE "
            "UNDO CANNOT BE AIMED. This clause used to read \"AND IT IS WHY "
            "THIS ACTION IS STILL NOT PERFORMED\", and it went false on "
            "2026-08-30 when follow_company entered PERFORMABLE -- the "
            "blocker was NOT lifted, the action shipped with it open, and a "
            "residue that describes itself as the reason for a refusal is "
            "unreadable once the refusal is gone. "
            "A posting identifies its employer by SLUG "
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
        # THE SHAREBOX, and the url carries NO ``{target}`` -- his text is the
        # target here, and text never enters a navigation. Measured on three
        # settle-agreeing readings of 31 controls, the third carrying the
        # census's own "consistent" verdict.
        #
        # THE ARTICLE ROUTE IS DELIBERATELY NOT USED. /article/new/ is on the
        # allowlist too and is WORSE measured: its publish control comes back
        # <redacted>, blanked as a singleton, so that route has no measured
        # anchor where this one does. Two routes was never a requirement.
        url_template="https://www.linkedin.com/preload/sharebox/",
        url_pattern=re.compile(
            r"^https://www\.linkedin\.com/preload/sharebox/$"
        ),
        exempt_substring=None,
        summary="Publish a post to your LinkedIn feed, under your own name.",
        from_state="composer_present",
        to_state="post_published",
        target_kind="post_text",
        state_from="feed_composer",
        # RULING 1, 2026-09-01. This one is UNRELIABLE rather than absent, and
        # the declaration says which -- a surface that answers on some
        # readings and not others is not a verification, and calling it one is
        # the apply_job defect wearing better clothes.
        unverifiable=Unverifiable(
            surface_that_would_confirm=(
                "your own activity rail, which lists what you have posted and "
                "is the only surface that would show a new post exists"
            ),
            why_it_cannot=(
                "that rail RENDERS INTERMITTENTLY and this server has the "
                "measurements: 233 controls with LinkedIn's own "
                "isSelfProfile=true assertion on one reading, and 67 controls "
                "with no redirect on another, in the same session minutes "
                "apart. A check that answers nothing on some readings it can "
                "take is not a verification, and shipping one as though it "
                "were is exactly the defect apply_job carried until "
                "2026-08-31. THE SCHEDULED-POSTS SURFACE WOULD HAVE FIXED "
                "THIS and does not exist for this server: measured 2026-09-01 "
                "on a settle-CONFIRMED composer render, the whole page draws "
                "seven links and none reaches a scheduled or posted list -- "
                "'Schedule post' is a BUTTON opening a modal, and a modal is "
                "not an address"
            ),
            what_he_must_do=(
                "open your profile and look at your recent activity. If the "
                "post is there it published; this server cannot tell you "
                "reliably either way"
            ),
        ),
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
        # THE ITEM PERMALINK. The target is composite -- item AND text -- and
        # only the ITEM half reaches this url, because assert_write_url
        # formats the SUBJECT. His prose never enters a navigation.
        url_template="https://www.linkedin.com/feed/update/{target}/",
        url_pattern=re.compile(
            r"^https://www\.linkedin\.com/feed/update/"
            r"urn:li:[A-Za-z]+:[0-9]+/$"
        ),
        exempt_substring=None,
        summary=(
            "Publish a comment under one feed item, under your own name."
        ),
        from_state="comment_control_present",
        to_state="comment_published",
        target_kind="item_and_text",
        state_from="feed_item",
        # RULING 1, 2026-09-01, and this declaration carries TWO things no
        # other does: no count exists to verify against, and the ACT ITSELF
        # may leave something behind that cannot be found.
        unverifiable=Unverifiable(
            surface_that_would_confirm=(
                "the item permalink itself -- the page the comment would be "
                "posted on, which is also the page this acts on"
            ),
            why_it_cannot=(
                "NOTHING ON THAT PAGE COUNTS COMMENTS. Measured 2026-09-01: "
                "91 controls enumerated, and the complete numeric inventory "
                "is four '0' controls (one per rendered comment row, paired "
                "1:1 with four 'Reply' buttons, so per-comment and not a post "
                "total), '33 reactions 33', two impressions links, a profile "
                "viewers link and five nav badges. THE INSTRUMENT HAS ITS OWN "
                "CONTROL ON THAT READING: '33 reactions 33' is lowercase, "
                "numeric and seen exactly once -- the precise shape "
                "shape.census_redact_rare would blank if it blanked anything "
                "-- and it came through INTACT, so this is an absence on the "
                "page and not one in the reader. AND THE FALLBACK FAILS ON "
                "THE SAME CAPTURE: counting rendered comment rows is not a "
                "total, because the list sits under a 'Most relevant' control "
                "and the reader takes a first render without scrolling -- a "
                "comment posted seconds ago with no engagement has no "
                "guaranteed place in a relevance-ordered first page"
            ),
            what_he_must_do=(
                "open the post and look at the comments. Yours will be "
                "attributed to you. AND IF THIS REFUSES AFTER TYPING: a "
                "comment draft may be left in the box, and whether that draft "
                "is local to this browser or saved to your account is "
                "UNMEASURED -- 17 candidate draft-listing addresses are all "
                "refused by the read boundary, so there is no surface on "
                "which one could be found or removed. Open the post and clear "
                "the box yourself if you do not want it there"
            ),
        ),
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
        # THE ITEM PERMALINK, admitted to the read allowlist 2026-08-31 and
        # given a write surface 2026-09-01. The pattern is the urn shape
        # dom.ACTIVITY_ITEMS_JS emits and nothing wider -- a target that is
        # not a urn cannot build a url at all.
        url_template="https://www.linkedin.com/feed/update/{target}/",
        url_pattern=re.compile(
            r"^https://www\.linkedin\.com/feed/update/"
            r"urn:li:[A-Za-z]+:[0-9]+/$"
        ),
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
            "half-truth here even once the ON label is known. "
            "AND THE THING THE VERDICT ITSELF CANNOT SETTLE, which the "
            "operator ruled on 2026-09-01 and which must be read before "
            "confirming: PRESSING THIS CONTROL APPLIES WHATEVER LINKEDIN'S "
            "DEFAULT REACTION IS, AND NOBODY HAS MEASURED WHICH ONE THAT IS. "
            "'Open reactions menu' is a SEPARATE control beside this toggle "
            "and its contents have never been opened, so whether the toggle "
            "applies a default Like immediately or opens that picker is "
            "unestablished. If it opens a picker, this gate REPORTS THAT and "
            "chooses nothing from it -- a gate that cannot say what it is "
            "about to express under his name does not get to guess. And the "
            "ON label has still never been seen, so the check after the click "
            "can say the control MOVED and cannot say what it moved to."
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
        # ADDRESSED 2026-09-02, and this spec carried NO URL AT ALL until
        # then -- which the refusal never said. It named "/edit/ is on
        # _FORBIDDEN_URL_SUBSTRINGS", a real obstacle, while omitting the
        # larger one: there was nothing to refuse, because nothing was
        # addressed. Two entries in this table were caught OVERSTATING their
        # blockers; this one UNDERSTATED, by naming the smaller of two.
        #
        # THE URL IS A CONSTANT, not a template with a target: the target of
        # this action is a FIELD AND A VALUE, not a page. So the pattern is
        # exact and anchored, on the same address the reads already use --
        # readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS has held it as an equality
        # key since the editor became readable.
        #
        # ADDRESSING IS NOT PERMISSION. PERFORMABLE is a hand-written
        # frozenset and this action is not in it, so _refuse_unperformable
        # raises before any url is used. That ordering is asserted rather
        # than assumed: a NEGATIVE CONTROL in tests/test_writes.py adds this
        # action to PERFORMABLE and shows the refusal stop firing. The day
        # somebody flips that frozenset for real, it goes red and names what
        # they just turned on.
        url_template="https://www.linkedin.com/in/me/edit/intro/",
        url_pattern=re.compile(
            r"^https://www\.linkedin\.com/in/me/edit/intro/$"
        ),
        # THE ONE FORBIDDEN SUBSTRING THIS EXACT URL MAY CARRY. Per-substring
        # by design: a url exempted for "/edit/" that also contained
        # "/delete" is still refused by "/delete". And the exemption is
        # deliberately NARROWER than the pattern -- the slashless spelling
        # /in/me/edit/intro stays refused, the conservative direction and the
        # one already chosen for the reads.
        exempt_substring="/edit/",
        summary="Change one field on your own LinkedIn profile.",
        from_state="editor_addressed",
        to_state="field_changed",
        # WHAT PROVES IT DID NOT HAPPEN. The field still holding exactly what
        # it held before the write is the unchanged state, and unlike
        # send_message's equivalent this action can ALSO prove the positive:
        # the value reads back as the one that was asked for. Both arms are
        # reachable, which makes this the best-verified write here.
        not_performed_state="value_unchanged",
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
            "NOT MEASURED, AND THE GAP IS NARROWER THAN THIS FIELD CLAIMED "
            "UNTIL 2026-09-03. The old sentence is quoted so the mistake is "
            "legible: \"The editors have never been OPENED, so no field, no "
            "save control and no previous-value affordance has been "
            "observed.\" All three clauses were false by then. The intro "
            "editor was opened and censused on 2026-08-31 -- 23 controls "
            "inside its dialog, with LinkedIn's own self-ownership assertion "
            "-- and dom.read_self_owned_editor_values reads the CURRENT VALUE "
            "of a named control out of it, which IS the previous-value "
            "affordance and is wired into this write's own path. "
            "WHAT IS STILL UNMEASURED IS THE ACTUAL QUESTION: whether "
            "LINKEDIN offers an undo of its own -- a version history, an edit "
            "log, a revert -- has never been looked for. Reading the old "
            "value back is not LinkedIn restoring it, and putting that string "
            "back through this server is A SECOND EDIT rather than an undo: "
            "whatever the field's history records, it records both changes."
        ),
        reversible_by=(
            "HIM, by hand -- but NOT FROM MEMORY, and that is the half this "
            "field had backwards until 2026-09-03. It said the previous value "
            "was one \"nothing here records\". This server records it: perform "
            "reads the field BEFORE it types, and the result carries a "
            "'restore' block with the previous value verbatim, how it was "
            "read, and the exact linkedin_update_profile_field call that puts "
            "it back. "
            "NOT THIS SERVER, IN THE ONE SENSE THAT IS STILL TRUE: it will "
            "not RUN that call. Restoring is a write and gets its own "
            "preview, its own token and his own confirmation -- a ruling, not "
            "a missing capability. "
            "AND THE SECOND CLAUSE WAS FALSE TOO -- it read \"'/edit/' is on "
            "the read boundary's forbidden list, so it cannot reach the "
            "editor in either direction.\" The SUBSTRING is forbidden in "
            "general; THIS EXACT URL is an exemption, and it is this action's "
            "own address, which is how the editor is read at all. "
            "THE ONE CASE WHERE HAND-RESTORING IS ALL HE HAS: a "
            "'previous_value' of null means it could not be read, which is "
            "not the same as it having been empty."
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
        # A REAL SURFACE, 2026-08-31, and it is the FIRST of the eight
        # surface-less actions to get one. Every clause of that sentence was
        # earned by a measurement rather than by a ruling alone:
        #
        # * THE PAGE LOADS AND DOES NOT REDIRECT. Six readings across two days
        #   and three builds, every one landing on this exact url and every
        #   one reporting 20 controls, 0 forms, 1 button, 16 links, 0 dialogs.
        #   That matters twice over: ``_assert_landed_on_target`` compares the
        #   whole url for a non-posting target, so a surface that redirected
        #   could not be performed on at all.
        # * THE ANCHOR IS READ, NOT GUESSED. Three inputs named through
        #   aria-labelledby, of which exactly one reports ``checked`` -- and
        #   since ``input_type`` joined the census the ROLE those inputs carry
        #   is read too, so the click selector is built from what the page
        #   says rather than from an assumed ``radio``.
        # * THERE IS NOTHING TO TYPE. This is the whole reason it is first:
        #   the click is the entire action, and ``perform`` already holds the
        #   only sanctioned click in this package. Nothing new was permitted
        #   to make it performable -- ``readonly.SANCTIONED_MUTATIONS`` is the
        #   two entries it has been since 2026-08-26.
        #
        # NO ``{target}`` IN THE TEMPLATE, deliberately. The target names a
        # setting and a value, and NEITHER belongs in a url: the page is one
        # fixed address and the destination is chosen by which control is
        # clicked on it. ``.format(target=...)`` over a string with no
        # placeholder returns it unchanged, so ``assert_write_url``'s
        # rebuild-and-compare still runs and still refuses any url a caller
        # could influence -- there is simply nothing for the target to
        # influence.
        url_template="https://www.linkedin.com/mypreferences/d/dark-mode",
        url_pattern=re.compile(
            r"^https://www\.linkedin\.com/mypreferences/d/dark-mode/?$"
        ),
        exempt_substring=None,
        summary="Change one LinkedIn account setting.",
        # NOT A BINARY TOGGLE, changed 2026-08-31. Dark mode has THREE
        # destinations, so the caller names one and it cannot be derived --
        # the same shape as set_open_to_work.
        from_state=None,
        to_state=None,
        target_kind="setting_and_value",
        # MOVED OFF THE INDEX, 2026-08-31, and this is the whole of what the
        # census's new ``checked`` reading bought. It read ``settings_index``
        # until today: a page that hands out ADDRESSES and switches nothing,
        # so the "state" it produced was "this surface addresses 33 settings"
        # -- true, and not a fact about any setting's VALUE. ``_direction``
        # then refused to render, correctly, because a gate that cannot say
        # which way it moves a control is not a gate.
        state_from="setting_dark_mode",
        direction_source=(
            "The dark-mode page itself -- /mypreferences/d/dark-mode -- read "
            "live by this gate, reporting WHICH of its three radios is "
            "checked. MEASURED on six readings across two days and three "
            "builds, every one agreeing: 20 controls, ZERO forms, one button, "
            "16 links, no dialogs, no redirect, and three inputs named "
            "through aria-labelledby of which exactly one reports checked. "
            "That is read off the very control a change would move, which is "
            "the strongest direction source in this design -- and it replaced "
            "a reading of the settings INDEX, which could only ever say how "
            "many settings exist."
        ),
        wrong_state_note=(
            "Not a toggle. This setting has three destinations and the gate "
            "refuses unless exactly one radio reports checked: at zero the "
            "group drew with nothing selected, which is a page nobody has "
            "seen, and at two or more choosing between them would be choosing "
            "by position."
        ),
        # THE THREE DESTINATIONS, and the field is doing the job its docstring
        # now admits it does: it is the ENUMERATION ``_direction`` validates
        # both the origin and the destination against, and only incidentally a
        # map of audiences. Dark mode HAS no audience, and each value says so
        # rather than leaving a caller to infer it from silence.
        audiences={
            "always off": (
                "NOBODY. Dark mode is a per-account display preference: no "
                "other member can observe it, it is broadcast nowhere, and it "
                "appears in no feed and no notification."
            ),
            "always on": (
                "NOBODY, for the same reason -- this setting has no audience "
                "at all, which is why it was the one settings page admitted."
            ),
            "device settings": (
                "NOBODY. This destination defers to the operating system's "
                "own light/dark preference rather than pinning a value."
            ),
        },
        reversibility=(
            "STILL-UNKNOWN as a VERDICT, and the structure is as good as it "
            "gets short of one: the inverse of this action IS this action, "
            "with a different destination named. The three states are all "
            "measured to exist, all readable, and all reachable from each "
            "other through the same three controls on the same page."
        ),
        # STILL FALSE, AND DELIBERATELY. Nobody has performed a dark-mode
        # change and read it back, so the round trip is UNPERFORMED -- and
        # ``_reversibility_disagreement`` enforces that an unmeasured claim
        # may not wear a measured class. The structural argument above is
        # strong and it is not a measurement, and this package's whole
        # discipline is that the second does not become the first by being
        # convincing.
        reversibility_measured=False,
        reversibility_class="STILL-UNKNOWN",
        reversibility_evidence=(
            "THE ROUND TRIP HAS NOT BEEN PERFORMED, which is what would make "
            "this MEASURED. What IS measured: the page renders three radios, "
            "exactly one reports checked, and this server can read which -- "
            "six agreeing readings across two days and three builds. So the "
            "state before and the state after are both readable, which is the "
            "precondition for ever measuring reversibility here and is more "
            "than follow_company has. What is NOT measured is whether "
            "LinkedIn accepts the change, whether it confirms it, and whether "
            "setting it back lands -- and none of those is knowable without "
            "performing one, which is his call and not this server's. NOTE "
            "the evidence for the FAMILY is unchanged and still governs any "
            "future ruling: the 33 addresses on that index are not one kind "
            "of thing, and two of them end the account."
        ),
        reversible_by=(
            "THIS SERVER, by calling this same tool with a different "
            "destination -- and that sentence is new on 2026-08-31. It read "
            "'NOT this server: the pages carrying the values are unreachable "
            "in either direction', which was true of every settings page when "
            "it was written and is false of THIS one now: /mypreferences/d/"
            "dark-mode is on the read allowlist and is this action's write "
            "surface. The forbidden entries it cited -- "
            "'/mypreferences/d/categories/' and '/settings/' -- are both "
            "still there and still make every OTHER setting unreachable in "
            "both directions, so the old sentence is narrowed rather than "
            "deleted."
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
            "ONE ROUND TRIP, WATCHED. Read the state, change it to one of the "
            "other two, read it back, change it back, read it again. Every "
            "one of those five steps is available now -- the page is on the "
            "read allowlist and this tool performs the change -- so what "
            "stands between this claim and a MEASURED verdict is a decision "
            "to spend one cosmetic, self-observable setting on his own "
            "account. That is his to make and nothing here will make it for "
            "him. The procedure used to read 'census one named setting page, "
            "which needs a boundary ruling first'; the ruling was made and "
            "the census was taken, so the procedure has moved on to what is "
            "actually left."
        ),
    ),
    "linkedin_send_invitation": WriteSpec(
        action="send_invitation",
        tool_name="linkedin_send_invitation",
        # HIS OWN PROFILE, and the url carries NO ``{target}``. That is not a
        # simplification: the target here is his NEEDLE, which has no
        # measurable shape and must never reach a navigation. The controls
        # live on a page addressed by a constant, and the aiming is done by
        # aim_invitation refusing anything but exactly one match -- so the
        # needle selects a control and never a url.
        #
        # This surface costs NO BADGE. /mynetwork/ would consume the
        # pending-invitation counter, which is why no tool here loads it; his
        # own profile draws the same controls and carries no such counter.
        url_template="https://www.linkedin.com/in/me/",
        url_pattern=re.compile(r"^https://www\.linkedin\.com/in/me/$"),
        exempt_substring=None,
        summary="Send one connection invitation to another LinkedIn member.",
        from_state="invite_control_present",
        to_state="invitation_sent",
        target_kind="member",
        state_from="profile_invitations",
        # RULING 1, 2026-09-01. Nothing can confirm this, and the gate says so
        # in three parts rather than one paragraph -- the third is the only
        # one that is about HIM, and a paragraph is what loses it.
        unverifiable=Unverifiable(
            surface_that_would_confirm=(
                "your Sent Invitations manager, under My Network > Manage > "
                "Sent, which is the one surface that lists invitations you "
                "have sent and would show this one as pending"
            ),
            why_it_cannot=(
                "this server cannot open it, for two separate measured "
                "reasons and either would be enough. Its address contains "
                "'invitation', which is on readonly._FORBIDDEN_URL_SUBSTRINGS "
                "and is checked before the allowlist is consulted. And "
                "reaching it goes through /mynetwork/, whose load CONSUMES "
                "the pending-invitation badge -- a cost measured twice, paid "
                "by you, and spent on somebody else's notification rather "
                "than on anything this call needs. NOR IS THERE A POST-CLICK "
                "STATE ON THE PAGE IT DOES ACT ON: no invitation control has "
                "ever been observed after being pressed, so this server "
                "cannot even report that the control changed"
            ),
            what_he_must_do=(
                "open My Network, then Manage, then Sent, and look for the "
                "person. That is the only way to know whether this landed"
            ),
        ),
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
        # ADDRESSED 2026-09-02. The composer's exact url has been on the read
        # allowlist since 2026-08-31, admitted by the operator's ruling as the
        # NARROWEST entry on that list -- ``"/messaging/compose"`` STAYS on
        # ``readonly._FORBIDDEN_URL_SUBSTRINGS`` and this one address is let
        # past it by an EXACT-url exemption, so every other spelling in that
        # family refuses exactly as before.
        #
        # A CONSTANT, not a template: the target of this action is a MEMBER
        # AND A TEXT, not a page, so ``{target}`` appears nowhere and the
        # pattern is anchored whole. ``send_invitation`` has the same shape
        # for the same reason.
        url_template="https://www.linkedin.com/messaging/compose/",
        url_pattern=re.compile(
            r"^https://www\.linkedin\.com/messaging/compose/$"
        ),
        exempt_substring="/messaging/compose",
        summary=(
            "Send one message or InMail to another LinkedIn member."
        ),
        # "composer_unmeasured", AND IT IS NOT STALE -- it was changed to
        # "composer_holds_text" on 2026-09-02 and changed straight back, which
        # is worth recording because the mistake is a subtle one and a sweep
        # for stale clauses is primed to make it.
        #
        # THE CONFLATION. The composer HAS been measured -- 77 controls, both
        # dispatch radios, the body editor, Send drawn DISABLED while empty.
        # All true, and none of it is what this field means. This is the state
        # THE GATE reads before acting, and the gate deliberately does not open
        # messaging to find out: doing so redirects into one conversation of
        # LinkedIn's choosing and spends a stranger's thread. So the gate has
        # never observed this composer and says so.
        #
        #   the composer has been measured by the census   TRUE
        #   THIS GATE can observe the composer's state     FALSE, BY DESIGN
        #
        # Overwriting it produced a gate that refused with a WRONG-STATE error
        # -- "valid only from composer_holds_text, this reads
        # composer_unmeasured" -- instead of its designed refusal. The safety
        # property held; the reason he would have READ was wrong.
        from_state="composer_unmeasured",
        to_state="message_sent",
        # WHAT PROVES IT DID *NOT* HAPPEN -- apply_job's mechanism, and the
        # answer to a blocker this entry named wrongly for a week.
        #
        # The refusal said the way out was A VERIFICATION SURFACE. There is
        # none: the composer carries no countable total, and the only surface
        # that could confirm a send is the thread, which is forbidden AND
        # costs a read receipt on a real person.
        #
        # BUT PROVING A SEND HAPPENED WAS NEVER THE ONLY OPTION. perform()
        # compares the verified state against expected_after for True and
        # against unchanged_state for False, falling to UNKNOWN between them.
        # Reading the state that proves NOTHING WAS DISPATCHED -- the composer
        # still holding its text with Send still enabled -- turns the worst
        # answer into the second best.
        #
        # AND THE PROPERTY THAT MAKES THIS ADMISSIBLE IS THE ONE THAT
        # DISQUALIFIED THE ALTERNATIVE, INVERTED. A "composer cleared means
        # sent" rule could only be validated BY SENDING, and a verification
        # you can only validate by performing the irreversible thing is not a
        # verification. The negative direction needs no such thing: fill the
        # composer, do not send, and observe what UNCHANGED looks like. That
        # is a read.
        #
        # IT STILL CANNOT REPORT "sent". expected_after is "message_sent" and
        # verified_state initialises to UNKNOWN, so with no surface writing
        # that state the True arm is unreachable by construction. This action
        # can be shown NOT to have happened and cannot be shown to have
        # happened.
        #
        # AND WHY THIS NAMES A COMPOSER STATE WHILE from_state ABOVE DOES NOT.
        # The two fields are read at opposite ends of the action and the cost
        # of looking is not the same at both:
        #
        #   from_state           read BEFORE, by a gate that must not open
        #                        messaging -- looking costs a stranger's thread
        #   not_performed_state  read AFTER, when the composer is already open
        #                        in front of you -- re-reading costs nothing
        #
        # That asymmetry is the whole reason one says "unmeasured" and the
        # other names what it expects to find. Collapsing them looks like
        # tidying and is how the wrong-state refusal got introduced once.
        not_performed_state="composer_holds_text",
        # THE CLICK-TIME STATE, AND THE REASON THIS FIELD EXISTS AT ALL.
        #
        # ``from_state`` above is ``composer_unmeasured`` and that is CORRECT
        # -- it describes what the PREVIEW's gate has seen, and that gate
        # deliberately does not open messaging to find out. By click time the
        # composer IS open, because ``perform`` navigated to it, so the
        # click-time reading is a real reading of a real composer and cannot
        # honestly be called unmeasured.
        #
        # ONE FIELD CANNOT BE BOTH. Before this existed, ``valid_from``
        # compared the click-time reading against ``from_state`` -- so this
        # action would have refused EVERY reading it could ever take, with a
        # wrong-state error, which is a gate that cannot pass rather than a
        # gate refusing something. That is precisely the failure
        # ``update_setting`` had when a multi-state action was compared against
        # a single ``from_state``, one field along.
        click_from_state="composer_empty",
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
            "NOBODY, through this server, and the VERDICT is unchanged while "
            "half its reasoning was false until 2026-09-03. What is true is "
            "the whole of it: deletion is permanently forbidden here, at any "
            "confirm level, so an un-send does not exist in this design. "
            "WHAT THIS FIELD USED TO ADD WAS WRONG -- \"'/messaging/compose' "
            "is on the read boundary's forbidden list, so nothing here can "
            "reach a composer in either direction.\" The SUBSTRING is "
            "forbidden in general; THIS EXACT URL is an exemption and is this "
            "action's own address, which is how it reaches a composer at all. "
            "Reaching one is what it does. What it cannot do is take back "
            "what it sent."
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


def _sweep_expired_grants() -> int:
    """Drop every grant past its TTL. Returns how many went.

    THE TTL BOUNDED WHEN A GRANT COULD BE USED AND NOT HOW LONG IT WAS HELD,
    which is a different property and the one that was missing. A grant was
    written at :func:`mint` and removed only by :func:`consume` or
    :func:`discard_all` -- no timer, no task, no ``atexit`` -- so a
    minted-but-never-confirmed grant kept its target in process memory for the
    life of the process, long after the token itself had stopped working.

    WHY IT MATTERS MORE FROM 2026-08-31 THAN IT DID BEFORE. Until today no
    composite action could be granted at all, so every held target was a job
    id or a company id. ``update_setting`` is performable now, so a PREVIEW
    mints -- and previews are the common case, while confirmations are the
    rare one. Held targets are about to be the normal state rather than the
    exception, and the specs whose targets carry CONTENT (a comment, a post, a
    message) are the ones a future wave would add next.

    SWEPT ON EVERY MINT AND EVERY CONSUME rather than on a timer. A timer is a
    background task, and a background task holding write grants is exactly the
    thing ``GRANT_TTL_SECONDS`` exists to make impossible; sweeping on the
    paths that already run keeps this synchronous and gives it no schedule of
    its own. The cost is bounded by how many grants a process can hold, which
    is small by construction.
    """
    dead = [token for token, grant in _GRANTS.items() if grant.expired()]
    for token in dead:
        _GRANTS.pop(token, None)
    return len(dead)


def grant_is_possible(spec: WriteSpec) -> bool:
    """Could a grant for this action ever be permission to do anything?

    ONE PREDICATE, BECAUSE THE ALTERNATIVE IS HOW THIS WENT WRONG. Three
    places needed this answer and all three computed it from ``url_template``
    alone: ``mint``'s refusal, ``preview``'s decision whether to mint at all,
    and ``linkedin_server_info``'s ``can_hold_a_grant``. That agreed with
    reality only while no unperformable action carried a url, which nothing
    ever required.

    Addressing ``update_profile_field`` on 2026-09-02 broke all three at once
    and in different ways -- a live confirm token from ``mint``, an exception
    escaping ``preview`` instead of a refusal block, and a field reporting the
    opposite of the truth. Each was a separate site of one accident, and
    fixing them separately would have left a fourth copy to drift.

    BOTH HALVES ARE REAL AND THEY ARE DIFFERENT QUESTIONS. Membership is
    PERMISSION -- the write door refuses a non-member however the grant was
    obtained. The url is ADDRESSING -- there is no page for the grant to be
    permission to act on. ``mint`` raises separately for each because the
    REASON is what a reader needs; this returns only whether either applies.
    """
    return spec.action in PERFORMABLE and spec.url_template is not None


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
    # THE REASON IS PERMISSION, AND UNTIL 2026-09-02 THIS ASKED ABOUT ADDRESS.
    #
    # The check below used to be `url_template is None` alone, reasoned as "a
    # grant is permission to ACT and there is nothing to act on". That stopped
    # the unperformable actions -- and it stopped them BY ACCIDENT, because
    # none of them happened to carry a url. Nothing ever required that.
    #
    # Addressing update_profile_field broke it immediately and silently: the
    # action still could not perform, but mint() no longer refused it, and a
    # LIVE CONFIRM TOKEN existed in the process for an action the write door
    # would always reject. The only thing left between that token and a
    # navigation was a check a future click has to remember to run, which is
    # the exact condition this refusal was written to prevent.
    #
    # It was caught by a test asserting the TOKEN. The field this server
    # publishes about the layer -- can_hold_a_grant -- had already been
    # "fixed" to say url AND membership, so the description was right while
    # the layer stayed removed. A property is not tested by asserting what the
    # system says about it.
    if spec.action not in PERFORMABLE:
        raise WriteAttemptError(
            f"no grant is minted for {action!r}: it is sanctioned but NOT "
            "PERFORMABLE, so the write door would refuse it however the grant "
            "were used. Refused at ISSUE rather than only at use, because an "
            "invariant a future click has to remember to check is not an "
            "invariant -- and a live token for an action that cannot act is "
            "the thing this refusal exists to keep out of the process. The "
            "reason is MEMBERSHIP, not the url: an address is not permission, "
            "and this check asked about the address until 2026-09-02."
        )
    # AND THE SECOND QUESTION, WHICH IS GENUINELY ABOUT THE ADDRESS. Kept as a
    # separate refusal because it is not the same fact: a performable action
    # with no surface has nothing to navigate to. No such action exists today
    # -- that is site five of the same coincidence -- and this fires BEFORE the
    # click, where _verify_after's equivalent guard can only fire after it.
    if spec.url_template is None:
        raise WriteAttemptError(
            f"no grant is minted for {action!r}: it is performable and its "
            "surface has never been loaded by this server, so there is no "
            "page for a grant to be permission to act on. Give it a measured "
            "surface before making it performable, not after."
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
    # AFTER the insert, never before: sweeping first would leave this grant
    # unswept for its whole life and make the sweep one call behind forever.
    _sweep_expired_grants()
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
    # NORMALISED THE SAME WAY ``mint`` NORMALISED IT, and this line closes a
    # defect that would have gone live the moment any composite-target action
    # became performable.
    #
    # It read ``grant.target != str(target)`` -- a RAW comparison against a
    # value ``mint`` had put through :func:`_target_for` first. For a job id
    # and a company id the two agree, because normalising those is a strip;
    # for a COMPOSITE target they never can. ``mint`` stores
    # ``"dark_mode :: Always on"`` and the tool layer handed ``consume`` a
    # mapping, whose ``str()`` is its repr. So every composite action's token
    # was unredeemable BY CONSTRUCTION -- not refused for a reason, just
    # never equal -- and nothing caught it because no such action could reach
    # ``mint`` either.
    #
    # ONE NORMALISER, BOTH DOORS. That is the property worth having rather
    # than the bug worth fixing: a second spelling of "what this target is"
    # is a second thing that can disagree with the first, and the whole job
    # of a canonical target is to be the ONE string a token is bound to.
    spec = spec_for_action(action)
    wanted = _target_for(spec, target)
    if grant.target != wanted:
        raise WriteAttemptError(
            f"token was minted for target {grant.target!r}, not {wanted!r}"
        )
    grant.consumed = True
    _GRANTS.pop(token, None)
    # SWEPT LAST, AND THAT PLACEMENT IS A CORRECTION. Sweeping before the
    # lookup was the obvious spot and it cost something real: an expired token
    # stopped getting "this confirm token expired after 120s -- run the
    # preview again and read it before confirming" and started getting
    # "unknown or already-discarded confirm token". Both refuse; only one
    # tells him what to do, and the difference lands on somebody who has just
    # taken too long reading a block this design asked him to read carefully.
    # So THIS token keeps its own specific answer and every OTHER expired
    # grant is dropped here.
    _sweep_expired_grants()
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

#: The tracker tab that answers "did an application submit". Added 2026-08-31,
#: after an apply was performed live and its verification read the SAVED tab.
#:
#: THE DEFECT WAS NOT A WRONG STRING, IT WAS A CHECK THAT COULD NOT PASS.
#: ``apply_job``'s ``to_state`` is ``"applied"`` and ``_read_saved_state``
#: returns ``"saved"``, ``"not_saved"`` or ``"unknown"`` -- so the comparison
#: ``verified_state == "applied"`` was FALSE on every possible reading, and
#: every apply this server can ever perform was going to report
#: ``performed: "unknown"``. It reported that the posting is still in his
#: Saved list, which was true and is not evidence about an application.
#:
#: WHY THAT MATTERS MORE HERE THAN ANYWHERE ELSE. The verification block is
#: what a human reads to decide whether an IRREVERSIBLE act landed, and
#: ``"unknown"`` on this action is the one answer he cannot resolve by
#: retrying -- the docstring forbids it, because a retry on something that may
#: have half-landed is the failure being guarded against. Pointing the read at
#: the tab that carries the answer makes ``"unknown"`` mean what it says.
APPLIED_LIST_URL = "https://www.linkedin.com/jobs-tracker/?stage=applied"
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

#: ONE NAMED SETTINGS PAGE, and the only one below the index this server may
#: reach. Admitted to ``readonly._ALLOWED_URL_PATTERNS`` on 2026-08-31 by an
#: anchored pattern naming this page and nothing else, on the operator's ruling
#: that a setting is admitted BY NAME or not at all -- ``Close and delete
#: account`` and ``Hibernate account`` live in the same address family.
#:
#: WHY THIS IS A SEPARATE CONSTANT FROM :data:`SETTINGS_URL` rather than a
#: format string over it. A template would make the family addressable from one
#: place, which is exactly the shape the ruling refused; two literals cannot be
#: pointed at a third page without somebody writing that page's name down.
#:
#: WHAT IT RENDERS, measured FOUR TIMES across two days -- twice on 2026-08-31
#: in the previous wave, and twice today, the second of those the first reading
#: ever taken with a ``checked`` field to read. All four agree: 20 controls,
#: ``forms: 0``, ``buttons: 1``, ``links: 16``, ``dialogs: 0``, and NO
#: REDIRECT. Three radios named through ``aria-labelledby``, none of them
#: inside a container.
DARK_MODE_URL = "https://www.linkedin.com/mypreferences/d/dark-mode"

#: The three destinations dark mode has, EXACTLY as LinkedIn renders them and
#: in the case it renders them in. Read off the live page rather than typed
#: from memory, which is why they are here rather than inline: a destination
#: this server has never seen rendered is one its gate may not offer.
DARK_MODE_STATES: tuple[str, ...] = ("Always off", "Always on", "Device settings")

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


def _text_component_of(spec: WriteSpec, target: str) -> str:
    """The part of a canonical target that would be TYPED. Never composed here.

    A composite target is ``subject :: content`` and a ``post_text`` target is
    content alone. This returns the content half and nothing else, so the
    string handed to the one fill site is provably a slice of the very target
    the preview printed and the token was minted against.

    IT REFUSES RATHER THAN GUESSING. An action that types must declare a
    target kind this function knows how to split; anything else raises, which
    is a refusal before a fill rather than a fill of the wrong string.
    """
    kind = spec.target_kind
    if kind not in _COMPOSITE_TARGET_KINDS:
        raise WriteAttemptError(
            f"{spec.action!r} is in TYPING_ACTIONS and its target_kind "
            f"{kind!r} has no content component, so there is nothing measured "
            "to type. A fill will not be built from a target this module "
            "cannot split."
        )
    first, second = _COMPOSITE_TARGET_KINDS[kind]
    if not second:
        return target
    if target.count(TARGET_JOIN) != 1:
        raise WriteAttemptError(
            f"{spec.action!r} holds a target that is not the canonical "
            "two-part form, so its content half cannot be identified. "
            "Refusing to type any part of it."
        )
    return target.split(TARGET_JOIN, 1)[1]


def _subject_component_of(spec: WriteSpec, target: str) -> str:
    """The part of a canonical target that names WHO or WHAT. Never composed here.

    THE MIRROR OF :func:`_text_component_of`, and it exists for exactly one
    reason: ``send_message`` types TWO things -- a recipient and a body -- and
    both must be provably slices of the target the token was minted against.

    THE PROPERTY THIS PRESERVES is the one ``tests/test_typed_bytes.py``
    asserts on the AST: **this server never composes what it types under his
    name.** That test pinned a single fill site whose text was a bare call to
    ``_text_component_of``. A second thing to type could have been handled by
    relaxing it to "the text contains a call"; it was not. The test was
    EXTENDED so both components carry the same proof, which is the only
    acceptable way to argue with a test that has to change.

    IT REFUSES RATHER THAN GUESSING, on the same rule: a one-part target has
    no subject to split off, and returning the whole string would type the
    body into the recipient field.
    """
    kind = spec.target_kind
    if kind not in _COMPOSITE_TARGET_KINDS:
        raise WriteAttemptError(
            f"{spec.action!r} has target_kind {kind!r}, which has no subject "
            "component, so there is nothing measured to type into a second "
            "control."
        )
    first, second = _COMPOSITE_TARGET_KINDS[kind]
    if not second:
        raise WriteAttemptError(
            f"{spec.action!r} is addressed by {first!r} alone -- its target is "
            "one component, so it has no subject half. Refusing to type any "
            "part of it into a second control."
        )
    if target.count(TARGET_JOIN) != 1:
        raise WriteAttemptError(
            f"{spec.action!r} holds a target that is not the canonical "
            "two-part form, so its subject half cannot be identified. "
            "Refusing to type any part of it."
        )
    return target.split(TARGET_JOIN, 1)[0]


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

    WHY ACCEPTING IT WAS SAFE UNTIL 2026-09-01, AND WHERE THE PROTECTION LIVES
    NOW. This paragraph used to read: *"Both actions that use this hold no
    ``url_template``, so mint refuses them a grant at ISSUE... If either is
    ever made performable, THIS FUNCTION IS THE FIRST THING THAT MUST
    CHANGE."* ``react_to_item`` became performable on 2026-09-01 and that
    sentence stopped being true the same day, so it is corrected here rather
    than left as a guarantee nobody re-read.

    THIS FUNCTION DID NOT HAVE TO CHANGE, and the reason is worth stating
    because the old warning aimed at the wrong place. The protection is not
    validation here; it is :data:`WriteSpec.url_pattern`, enforced by
    :func:`assert_write_url`, which REBUILDS the url from the grant and
    refuses it unless the whole thing matches an anchored pattern. For
    ``react_to_item`` that pattern is ``urn:li:[A-Za-z]+:[0-9]+``, so a target
    that is not a urn cannot produce a url that passes the write door -- the
    shape is enforced where the string is USED rather than where it arrives,
    which is strictly stronger because it also covers a target that changed
    shape in between.

    SO THE RULE FOR THE NEXT ONE, stated as a check rather than a warning: an
    opaque-kind action that becomes performable must carry a ``url_pattern``
    that CONSTRAINS its target, and
    ``tests/test_opaque_targets.py`` fails if one does not.
    ``send_invitation`` is the case that shows why the rule is about the
    pattern and not about this function: its target is a NEEDLE, which has no
    shape to enforce at all, and its url_template is a constant carrying no
    ``{target}`` -- so its target never reaches a url, and its aiming is done
    by :func:`aim_invitation` refusing anything but exactly one match.
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
    if isinstance(target, str) and target.count(TARGET_JOIN) == 1:
        # THE CANONICAL FORM IS A VALID SPELLING OF THE TARGET, and accepting
        # it is what makes this function IDEMPOTENT. It was not, and the
        # consequence was structural rather than cosmetic: ``preview`` mints
        # with ``observation.target``, which ``observe`` had already
        # canonicalised, so ``mint`` re-normalised its own output -- and for a
        # two-part kind that raised "its target is a mapping of the two, not
        # str". THE FIRST COMPOSITE ACTION TO GET A URL_TEMPLATE COULD NOT BE
        # PREVIEWED AT ALL, and nothing had caught it because until then
        # ``mint`` refused every composite action one line earlier, on the
        # missing surface.
        #
        # EXACTLY ONE SEPARATOR, and that is not a formality. Two would make
        # the split ambiguous, and a target that can be read two ways is bound
        # to neither -- which is the same property ``_clean_target_part``
        # protects by refusing a component that CONTAINS the separator. A
        # string with no separator stays refused by the message below, because
        # for a two-part kind it names only half of what is being confirmed.
        subject, _, content = target.partition(TARGET_JOIN)
        return (
            _clean_target_part(spec, first, subject)
            + TARGET_JOIN
            + _clean_target_part(spec, second, content)
        )
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


@dataclass(frozen=True)
class _TrackerStage:
    """One tab of the jobs tracker, described completely enough to read it.

    ADDED 2026-08-31 SO THAT A SECOND TAB COULD BE READ WITHOUT A SECOND COPY
    OF THE RECONCILIATION. That reconciliation is the subtle part -- absence
    from a partial list is not absence, and it refuses in BOTH directions --
    and two copies of it are two things that can drift. The alternative was
    duplicating ninety lines for the Applied tab, which is how the two would
    have ended up disagreeing about what an empty list means.
    """

    url: str
    #: The key ``shape.parse_tracker_tabs`` returns this tab's count under.
    tab_key: str
    #: What LinkedIn calls the tab, for the sentences a human reads.
    tab_label: str
    #: The state when the posting IS one of the rows.
    present: str
    #: The state when the list is READ WHOLE and the posting is not in it.
    absent: str


SAVED_STAGE = _TrackerStage(
    url=SAVED_LIST_URL,
    tab_key="saved",
    tab_label="Saved",
    present="saved",
    absent="not_saved",
)

#: THE ABSENT STATE HERE IS NOT ``apply_job``'s ``from_state``, and that is
#: deliberate rather than an oversight. ``from_state`` is ``"linkedin_apply"``,
#: which is a claim about the CONTROL on the posting -- which route the apply
#: takes -- and a tracker read establishes nothing about that. What a
#: corroborated absence from this tab establishes is narrower and is exactly
#: what the caller needs: no application exists. It gets its own name, and
#: ``WriteSpec.not_performed_state`` is what tells ``perform`` to read it as
#: "it did not happen" rather than as "nobody could tell".
APPLIED_STAGE = _TrackerStage(
    url=APPLIED_LIST_URL,
    tab_key="applied",
    tab_label="Applied",
    present="applied",
    absent="not_applied",
)


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

    A THIN WRAPPER SINCE 2026-08-31, and the name is kept because it is what
    every caller and every test already says. The reconciliation moved to
    :func:`_read_tracker_membership` so the Applied tab could be read by the
    same rules rather than by a second copy of them.
    """
    return await _read_tracker_membership(
        page, target, SAVED_STAGE, navigator=navigator
    )


async def _read_applied_state(
    page: Any, target: str, *, navigator: Any = None
) -> tuple[str, str]:
    """Does an application for THIS posting exist? Same rules, other tab.

    IT IS THE SAME QUESTION AS THE SAVED READ AND IT CARRIES MORE WEIGHT.
    Absence from a partial Saved list means a save cannot be confirmed;
    absence from a partial APPLIED list, read as an answer, would mean telling
    him an irreversible act did not happen when the row may simply be below
    the fold. So the same refusal applies and it is the more important
    instance of it: this returns ``"not_applied"`` only when LinkedIn's own
    count for the tab corroborates that the whole list was drawn.
    """
    return await _read_tracker_membership(
        page, target, APPLIED_STAGE, navigator=navigator
    )


async def _read_tracker_membership(
    page: Any, target: str, stage: _TrackerStage, *, navigator: Any = None
) -> tuple[str, str]:
    """Is ``target`` one of the rows in this tracker tab? See the two wrappers
    above for what the question means on each of them."""
    list_wait = await dom.wait_for_tracker_list(page)
    main_text = await dom.read_main_text(page)
    stated = shape.parse_tracker_tabs(main_text).get(stage.tab_key)
    empty_state = shape.tracker_empty_state(main_text)

    records = await dom.harvest_linked_cards(
        page, href_pattern=dom.JOB_HREF, max_items=SAVED_LIST_MAX_ROWS
    )
    rows, dropped = dom.parse_all(records, shape.parse_job_card)
    ids = {str(row.get("job_id")) for row in rows if row.get("job_id")}

    if stated is None:
        return (
            UNKNOWN,
            f"LinkedIn's own {stage.tab_label} tab count could not be read, "
            "so the rows that did render have nothing to be reconciled "
            "against and a posting absent from them may simply be one that "
            "was not drawn.",
        )
    if len(rows) > stated:
        return (
            UNKNOWN,
            f"{len(rows)} rows were read while LinkedIn's own "
            f"{stage.tab_label} tab says {stated}. More rows than the page "
            "claims means something that is not a job row is being parsed as "
            "one, and a list that disagrees with itself cannot settle a "
            "direction.",
        )
    if target in ids:
        return (
            stage.present,
            f"this posting is one of the {len(rows)} rows LinkedIn rendered in "
            f"the {stage.tab_label} tab, whose own count for that tab is "
            f"{stated}.",
        )
    if not rows:
        if shape.empty_is_believable(
            linkedin_count=stated, empty_state=empty_state
        ):
            return (
                stage.absent,
                f"the {stage.tab_label} tab is EMPTY and corroborated empty: "
                f"LinkedIn's own count for it reads {stated} and the page drew "
                f"its empty state ({empty_state!r}). An empty list contains "
                "nothing, so this posting is not in it.",
            )
        return (
            UNKNOWN,
            "no rows could be read AND the page does not corroborate an "
            f"empty list: the {stage.tab_label} tab count reads {stated!r} "
            "and the empty "
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
            stage.absent,
            f"all {stated} rows LinkedIn counts in the {stage.tab_label} tab "
            "were read, and this posting is not among them.",
        )
    return (
        UNKNOWN,
        f"{len(rows)} of the {stated} rows LinkedIn counts in the "
        f"{stage.tab_label} tab were read -- this loads one page and does not "
        "scroll, so the rest are below the fold rather than missing. Absence "
        "from a list that is a fraction of itself is not absence.",
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
    page: Any, spec: WriteSpec, *, target: str = ""
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
    page: Any, spec: WriteSpec, *, target: str = ""
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
    page: Any, spec: WriteSpec, *, target: str = ""
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


async def _read_dark_mode(
    page: Any, spec: WriteSpec, *, target: str = ""
) -> tuple[dict[str, Any], str, str]:
    """WHICH dark-mode setting is selected, off the page that carries it.

    THE ONE READER HERE THAT REPORTS A VALUE RATHER THAN A COUNT, and the
    difference is the whole point of it. Its six siblings answer "is the
    control there", because for their capabilities that was the open question.
    For this one the control was never in doubt -- three radios, measured four
    times across two days -- and what was missing was WHICH of them is on.

    NO NEW SCRIPT AND NO NEW ``evaluate`` WAIVER. This calls
    ``dom.read_surface_census``, which already reads ``checked`` and
    ``checked_source`` off every control and shapes every name before
    returning it. A purpose-built reader here would have been a second
    implementation of a chain that already exists, declared and scanned, to
    answer a question the existing one answers.

    THE SHAPES ARE SAFE TO COMPARE AGAINST LITERALS, which is not true of
    every surface: these three names pass the census's own character and
    length gate, so they arrive readable rather than as ``<opaque>``. That is
    a property of THIS page and is why :data:`DARK_MODE_STATES` may be a tuple
    of literals at all.

    EXACTLY ONE CHECKED IS THE ONLY READABLE STATE, and the two refusals
    either side of it refuse different things:

    * ZERO checked -- the group rendered and nothing is selected. That is a
      page this server has never seen and cannot describe, not a default.
    * TWO OR MORE -- impossible for a radio group, reachable the moment
      LinkedIn rebuilds these as checkboxes, and it must not be resolved by
      picking the first. Picking one would be picking by position.

    The state is also checked against :data:`DARK_MODE_STATES` HERE, one layer
    above ``_direction``'s own check of it. That duplication is deliberate and
    follows ``_read_profile_state``, which casefold-checks the audience itself
    and returns ``unknown`` on a miss: the reader refusing a name it has never
    seen rendered is what keeps the gate's backstop a backstop instead of the
    only thing standing there.
    """
    census = await dom.read_surface_census(page)
    rows = [row for row in census["controls"] if row.get("checked") is not None]
    on = [str(row.get("shape") or "") for row in rows if row.get("checked") is True]
    off = [str(row.get("shape") or "") for row in rows if row.get("checked") is False]
    facts: dict[str, Any] = {
        "checkable_controls": len(rows),
        # THE ROWS THEMSELVES, reduced to four fields, added 2026-08-31 when
        # this action became performable. Two things need them and neither is
        # decoration:
        #
        # * ``_live_control`` builds the click selector from the ROLE the
        #   destination control actually carries, which is decided by
        #   ``input_type``. Reading it here rather than taking a second census
        #   in that function means the selector is built from the same reading
        #   the direction was.
        # * ``_render`` puts the whole facts dict in the confirm block under
        #   ``what_the_page_showed`` for a composite target, so the operator
        #   sees the three radios and which one is on before he confirms --
        #   which is the thing he is actually being asked about.
        #
        # SHAPES, NOT NAMES: every ``shape`` here came through
        # ``census_shape`` like any other census row. This page's three names
        # pass its gate, which is a property of this page and is the same
        # property that lets DARK_MODE_STATES be literals at all.
        # ``role`` IS IN THIS LIST BECAUSE IT WAS LEFT OUT OF IT FIRST, and
        # the omission is the third instance of one defect in this package:
        # an enumerated projection that drops a field the next reader needs.
        # ``container`` was lost that way on the day it was added, the census
        # row was mislabelled by index, and this dropped ``role`` --
        # ``dom.aria_role_of`` consults it FIRST, so every control here was
        # answered as though it carried no role attribute at all. It produced
        # the right refusal for a ``button[role=switch]`` by accident and
        # would have refused a legitimate ``div[role=radio]`` for the wrong
        # reason. Caught by a mutation, not by reading.
        "rows": [
            {
                "shape": str(row.get("shape") or ""),
                "tag": row.get("tag"),
                "role": row.get("role"),
                "input_type": row.get("input_type"),
                "checked": row.get("checked"),
            }
            for row in rows
        ],
        "checked": sorted(on),
        "unchecked": sorted(off),
        "checked_sources": sorted(
            {str(row.get("checked_source") or "none") for row in rows}
        ),
        "controls_read": int(census.get("controls_read") or 0),
        "forms": int((census.get("counts") or {}).get("forms") or 0),
    }

    if not rows:
        return (
            facts,
            UNKNOWN,
            "no checkable control rendered on the settings page at all, so "
            "there is no state to read. Absence on a first render is unknown "
            "rather than off -- and note that a control built as a div with "
            "role=radio produces NO CENSUS ROW at all rather than a row with "
            "no state, which is a limit of the control selector and is pinned "
            "in tests/test_surface_census.py.",
        )
    if len(on) != 1:
        return (
            facts,
            UNKNOWN,
            f"{len(rows)} checkable control(s) rendered and {len(on)} of them "
            "report checked. Exactly one is the only state this reader can "
            "describe: at zero the group drew with nothing selected, which is "
            "a page nobody has seen, and at two or more the group is not "
            "behaving as radios and choosing between them would be choosing "
            f"by position. The unchecked ones read {sorted(off)}.",
        )

    state = on[0]
    if state not in DARK_MODE_STATES:
        return (
            facts,
            UNKNOWN,
            f"the selected control reads {state!r}, which is not one of the "
            f"three this server has seen LinkedIn render ({list(DARK_MODE_STATES)}). "
            "A relabelled, translated or reshaped setting is refused rather "
            "than passed on, because a gate that cannot name the state it is "
            "in must not offer to change it.",
        )
    return (
        facts,
        state,
        f"the setting reads {state!r}, read off the radio group on "
        f"{DARK_MODE_URL} -- the very control a change would move. "
        f"{len(rows)} checkable control(s) were found and exactly one is "
        f"selected; the other {len(off)} read {sorted(off)}. The page carries "
        f"{facts['forms']} form(s) and {facts['controls_read']} control(s) in "
        "total, which is the shape it has rendered on all four readings taken "
        "across two days -- so this is not a half-rendered page reporting a "
        "state it had not drawn yet.",
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
    page: Any, spec: WriteSpec, *, target: str = ""
) -> tuple[dict[str, Any], str, str]:
    """Which ONE invitation control his needle picks out, or why none.

    A COUNT ONLY UNTIL 2026-08-31, and the needle never reached it: ``observe``
    handed its readers no target, so ``aim_invitation`` -- the matcher this
    whole capability is built around -- had no caller in this package at all.
    It aims now, and the aim is three integers.

    THE LABEL IS NOT READ HERE, and that is structural rather than tidy. This
    reader's answer becomes ``Observation.facts``, and an Observation is
    RETAINED on the grant -- so anything it returns is held for the life of
    that grant. The one label the operator's ruling admits is read by
    :func:`preview` instead, off the page this call already opened, and it
    reaches the confirm block and nothing else.
    """
    reading = await dom.read_invitation_surface(page, target or None)
    controls = int(reading.get("controls") or 0)
    # THE LABEL KEY IS DROPPED BEFORE THE FACTS ARE BUILT, not merely left
    # unset. This reader is never asked to reveal one, so the key is always
    # None here -- and popping it means a future edit that flips the default
    # cannot leak through this path without also changing this line.
    facts = {key: value for key, value in reading.items() if key != "label"}
    if controls < 1:
        return (
            facts,
            UNKNOWN,
            "no control whose accessible name ends "
            f"{dom.INVITE_CONTROL_SUFFIX!r} rendered on this page. The rail "
            "that carries them is a suggestion rail and need not be drawn, so "
            "this is unknown rather than zero.",
        )
    aim, aim_why, index = aim_invitation(reading)
    facts["aim"] = aim
    facts["aim_index"] = index
    if aim != INVITE_AIMED:
        # NOT AIMABLE IS NOT A STATE THIS ACTION IS VALID FROM. Zero matches
        # and two-or-more are different failures and ``aim_why`` says which;
        # both come back UNKNOWN, so ``_direction`` refuses to render a gate
        # rather than rendering one aimed at nobody in particular.
        return (
            facts,
            UNKNOWN,
            f"{controls} invitation control(s) are on HIS OWN PROFILE -- a "
            "page this server already loads, carrying no pending-invitation "
            f"counter -- and the aim did not settle. {aim_why} The comparison "
            "ran INSIDE the page and no label crossed into this process, "
            "which is why this can say how many matched and not who they are.",
        )
    return (
        facts,
        "invite_control_present",
        f"exactly one of {controls} invitation control(s) on HIS OWN PROFILE "
        f"carries the word given, at position {index} in the suffix-matched "
        "list. That page is one this server already loads and it carries no "
        "pending-invitation counter, so this route costs no badge -- which is "
        "the finding /mynetwork/ was refused for. The match was made inside "
        "the page and no label crossed into this reader.",
    )


async def _read_messaging_badge(
    page: Any, spec: WriteSpec, *, target: str = ""
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
    "profile_invitations": (PROFILE_URL, "profile", _read_profile_invitations),
    "messaging_badge": (FEED_URL, "feed", _read_messaging_badge),
    # THE ONE ENTRY HERE THAT READS A VALUE RATHER THAN COUNTING CONTROLS,
    # added 2026-08-31 when the census gained a ``checked`` reading and "which
    # of the three is selected" became answerable for the first time.
    #
    # IT REPLACES ``settings_index`` RATHER THAN JOINING IT, and the swap is
    # the point: that entry pointed at a page which hands out ADDRESSES and
    # switches nothing, so the only state it could ever report was how many
    # settings exist. ``_read_settings_index`` went with it -- this spec was
    # its only caller, and a reader kept for a state nobody consults is a
    # reader that goes stale unread.
    #
    # AND ``dom.read_settings_surface`` WENT WITH IT TOO, on 2026-09-02,
    # eighteen months of nothing later in reading time and two days later in
    # real time. This comment used to end: "remains available and is now
    # uncalled from this module" -- one sentence after stating the rule that
    # condemns it. THE FACT WAS OBSERVED AND THE RULE WAS STATED AND THE TWO
    # WERE NEVER CONNECTED, which is a different failure from every silent
    # one this package has caught: nothing was hidden, nothing failed to
    # fire, and the conclusion simply was not drawn.
    #
    # It was found by ``tests/test_reader_reachability.py``, whose call graph
    # cannot be talked out of a conclusion the way a reader of this paragraph
    # was. The reader is recoverable from history: 21 lines, deleted in the
    # commit that added this note, uncalled since 2026-08-31.
    "setting_dark_mode": (DARK_MODE_URL, "settings_dark_mode", _read_dark_mode),
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
        # THE TARGET REACHES THE READER, added 2026-08-31, and it closes a gap
        # that made a whole mechanism dead code.
        #
        # ``aim_invitation`` -- the needle matcher the previous wave built,
        # with its exactly-one rule, its ambiguous refusal and its
        # three-integer return -- HAD NO CALLER IN THIS PACKAGE. Only tests
        # called it. ``_read_profile_invitations`` counted controls and never
        # saw a needle, because this line handed the reader no target, so the
        # aiming this design is built around had never run against a page.
        #
        # That is the same shape as ``_direction``'s multi-state branch, which
        # was hardened in August against a KeyError nothing could reach: a
        # mechanism can be built, tested and argued about at length while
        # being unreachable from production, and the only thing that shows it
        # is following the value.
        #
        # A KEYWORD WITH A DEFAULT, so a reader that has no use for it says so
        # by ignoring it rather than by having a different signature. Five of
        # the six do exactly that.
        facts, state, why = await reader(page, spec, target=target)
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

    # THE VERIFICATION DISCLOSURE, printed in the preview and again in the
    # result. Ruling 1, 2026-09-01: an unverifiable outcome may ship PROVIDED
    # IT SAYS SO, and this is the saying.
    #
    # NOTE WHICH SIDE IS THE DEFAULT. An action with no declaration gets the
    # affirmative "YES", because the pairing test refuses a performable action
    # that has neither a declaration nor a real branch -- so reaching this
    # line without a declaration MEANS a branch exists. The block is never
    # silent about verifiability: a preview that simply omitted the question
    # is how "nobody checked" and "it checks out" become the same reading.
    if spec.unverifiable is not None:
        out["verification"] = spec.unverifiable.as_block()
    else:
        out["verification"] = {
            "outcome_is_verifiable": "YES",
            "what_would_confirm_it": spec.direction_source,
            "read_after_the_act": (
                "this server re-reads that surface after acting and reports "
                "what it found, rather than reporting that it clicked."
            ),
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
        # ASKED THE SAME WAY mint ANSWERS IT, rather than by a proxy.
        # This used to test `url_template is not None`, so an addressed
        # but unperformable action reached mint and its refusal escaped
        # as an exception where a refusal BLOCK belongs -- the caller
        # got a traceback instead of a gate explaining itself.
        if grant_is_possible(spec):
            grant = mint(
                spec.action, observation.target, receipt=observation.receipt
            )
            token = grant.token
        block = _render(spec, observation, direction, token)
        if grant is not None:
            # THE STORED BLOCK IS ASSIGNED BEFORE THE LABEL EXISTS, and the
            # order is the enforcement rather than a convention. See
            # :func:`_name_the_invitation_recipient` below: the label is added
            # to a NEW dict afterwards, so the object retained on the grant
            # provably never held it -- there is no scrubbing step to get
            # wrong and no copy to forget.
            grant.preview = block
        block = await _name_the_invitation_recipient(page, spec, observation, block)
        return block
    finally:
        _OBSERVED.pop(observation.receipt, None)


async def _name_the_invitation_recipient(
    page: Any,
    spec: WriteSpec,
    observation: Observation,
    block: dict[str, Any],
) -> dict[str, Any]:
    """Print WHO one invitation would reach, in the confirm block and nowhere
    else. Returns the block to hand back.

    THE PROBLEM THIS SOLVES, and it is the one that kept ``send_invitation``
    refusing after every boundary question had been answered. The aiming is
    safe precisely BECAUSE no label enters this process -- the needle goes
    into the page, three integers come back. So the block could say "exactly
    one of nine controls carries the word you gave, at position 3" and could
    not say WHO. Every other action here names its target in terms he can
    check: a job title and an employer, a company name, his own name and
    headline. A gate that fires an irreversible, third-party-visible act while
    unable to say who receives it is a confirm prompt with the important word
    missing.

    THE RULING, 2026-08-31, and the distinction it turns on. Loading a
    stranger's PROFILE stays refused because it EMITS -- ``who_viewed_me``
    reads the receiving end of exactly that signal, so the cost lands on
    somebody who did not agree to it. Reading one accessible name off a page
    already rendered on HIS OWN profile emits NOTHING: nobody is notified, no
    record is created, the person is not made aware. And he already knows the
    name, because he supplied the needle -- so this CONFIRMS that the control
    his own word selected is the person he meant, which is verification of his
    input rather than collection of somebody's identity.

    WHERE IT GOES AND WHERE IT MUST NOT, by construction and not by care:

    * INTO the returned block, as prose he reads.
    * NOT into ``grant.preview`` -- assigned above, before this runs, so the
      retained object never held it.
    * NOT into ``grant.target``, which stays HIS OWN NEEDLE. That is the
      guarantee this design declined to trade away and it is untouched.
    * NOT into the ``Observation`` -- which is why
      ``_read_profile_invitations`` does not read the label at all: its answer
      becomes ``observation.facts`` and an Observation is retained on a grant.
      This reads it separately, here.
    * NOT into ``consume``'s mismatch message, which interpolates targets.
    * NOT into a log line: ``dom.read_invitation_surface`` deliberately does
      not stringify its own exceptions, for exactly this reason.

    NO SECOND PAGE LOAD. ``observe`` has just loaded his profile and left the
    page on it. THAT IS CHECKED RATHER THAN ASSUMED, and the check is about
    the RAIL rather than the url: this re-read must find the same number of
    invitation controls the observation recorded, and the needle must still
    pick out exactly one. A url comparison would have been the obvious guard
    and it is the weaker one -- a page can be re-rendered at the same address,
    and the thing that matters is whether the control the name is read off is
    the control the aim was taken on.
    """
    if spec.action != "send_invitation":
        return block
    reading = await dom.read_invitation_surface(
        page, observation.target, reveal_single_match=True
    )
    # THE SAME RAIL, STILL AIMING AT ONE. Either half failing means the page
    # is not the one the observation describes, and a name read off some other
    # page is a name nobody's needle selected.
    if int(reading.get("controls") or 0) != int(
        (observation.facts or {}).get("controls") or -1
    ):
        return block
    if int(reading.get("matches") or 0) != 1:
        return block
    label = reading.get("label")
    if not isinstance(label, str) or not label:
        return block
    # A NEW DICT. The one on the grant is not touched, and this adds a
    # top-level key only -- so nothing nested is shared into.
    out = dict(block)
    out["who_this_would_reach"] = (
        "LinkedIn labels the ONE control your word selected: "
        f"{label!r}. That is read off your own profile, where it was already "
        "rendered -- nobody is notified, no record is created, and this "
        "server keeps no copy of it: it is printed here for you to check and "
        "is in no grant, no log and no file. CHECK IT. Your word picked this "
        "control out uniquely, and a word that uniquely picks out the WRONG "
        "person is the one failure this gate cannot catch for you."
    )
    return out


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
        # THE TWELFTH, 2026-09-02, AND IT SHIPS EXPECTING TO REFUSE.
        #
        # It is here on the operator's ruling and on a design that is NOT the
        # one first briefed. The briefed gate was publish_post's: fill the
        # recipient, fill the body, and proceed if `Send` became enabled.
        # THAT GATE CANNOT CARRY THIS ACTION. "Send became enabled" says
        # LinkedIn thinks this is sendable; it does not say the recipient is
        # the person he named -- and if the typeahead commits anything on the
        # blur the SECOND fill causes, the gate's own evidence is satisfied by
        # exactly the thing that is wrong, and the message reaches whoever
        # LinkedIn drew first. That is verbatim what aim_invitation exists to
        # refuse, on the action this spec itself calls the most
        # irreversible-in-audience in the design.
        #
        # SO THE GATE IS THE NAME MATCH, NOT THE COUNT: exactly ONE committed
        # recipient WHOSE ACCESSIBLE NAME CARRIES HIS OWN NEEDLE, compared
        # inside the page, integers only coming back. A count of one with the
        # wrong name refuses. A count of zero refuses.
        #
        # AND THE ORDER IS THE SAFETY PROPERTY: the recipient gate runs
        # BETWEEN the two fills, so HIS WORDS ARE NEVER TYPED until a
        # recipient has been confirmed. A refusal costs him a typed name in a
        # composer, not his message.
        #
        # IT IS EXPECTED TO REFUSE ON FIRST USE AND THE REFUSAL IS THE
        # MEASUREMENT. Nobody has typed into that combobox through this
        # server; whether a bare fill commits a recipient at all is unknown;
        # and the selectors that would find a committed one have never matched
        # anything on any page, on either branch of the only test that covers
        # them -- its double DISCARDS the selector argument. The per-selector
        # counts the refusal returns cannot be obtained any other way, because
        # taking the measurement requires typing into the box. Exactly the
        # shape comment_on_item shipped in, and unsave_job before it.
        #
        # WHAT IT STILL CANNOT DO is report "sent". to_state is
        # "message_sent" and no surface this server may read writes that
        # state, so the True arm is unreachable by construction; what it CAN
        # report is NOT SENT, from not_performed_state. And the InMail cost
        # stays UNMEASURED rather than denied -- the preview says so.
        "send_message",
        # THE ELEVENTH, 2026-09-02, on the operator's ruling "I want all
        # capabilities". Everything the earlier refusal named as missing was
        # built for it rather than around it: an exact-url exemption for the
        # editor, an aiming branch that reads the live control list and
        # refuses unless EXACTLY ONE control is named as asked, a fourth
        # sanctioned mutation kind that can only choose an option the page
        # already defines, an empty-into-required refusal, a verification that
        # reads the field back, and a restore path that hands him the previous
        # value and the call that puts it back WITHOUT this server ever
        # restoring anything itself.
        #
        # ENABLING IS NOT FIRING. It stays behind the same two-call gate as
        # every other write; what changed is that a token he confirms would
        # now reach a working action instead of a refusal.
        "update_profile_field",
        "save_job",
        "unsave_job",
        "unfollow_company",
        "apply_job",
        "follow_company",
        # THE SEVENTH, 2026-09-01, and the first admitted under the operator's
        # ruling that a write may apply something this server cannot name.
        # Every clause the other six needed is true of it:
        #
        #   a measured surface   /feed/update/<urn>/, the item permalink, on
        #                        the read allowlist since 2026-08-31 and
        #                        loaded four times since with no redirect
        #   a measured anchor    'Reaction button state: no reaction', read on
        #                        the feed, on his profile, and on the
        #                        permalink itself -- LinkedIn writes the
        #                        toggle state into the accessible name
        #   an aimable target    the permalink draws EXACTLY ONE reaction
        #                        control where the feed and profile draw
        #                        eight, so the picking-by-position objection
        #                        that blocked this action does not arise here
        #   a real verification  a fresh render of the permalink; the control
        #                        present and no longer wearing the OFF label
        #                        returns to_state, which is the property
        #                        apply_job lacked
        #   no new permission    the click is perform()'s existing one;
        #                        readonly.SANCTIONED_MUTATIONS is unchanged
        #
        # WHAT IT STILL CANNOT SAY is WHICH reaction, and that is disclosed in
        # `residue` rather than fixed: the ON label has never been observed
        # and the picker has never been opened. The operator ruled explicitly
        # that this may ship with that stated. It is NOT the apply_job shape
        # -- the check answers WHETHER and answers it honestly; what is
        # unknown is a different question, and it is named.
        "react_to_item",
        # THE EIGHTH, 2026-09-01, and the FIRST that reaches another person.
        # It ships under Ruling 1 -- nothing can confirm it -- with the
        # declaration in `unverifiable` naming the Sent Invitations manager,
        # why this server cannot open it, and what he must do himself.
        #
        # WHAT PROTECTS THE THIRD PARTY, unchanged and load-bearing:
        #
        #   the RECIPIENT is supplied by him per call and never DISCOVERED.
        #   The needle is his own word; the LABEL is LinkedIn's string, and
        #   the comparison happens INSIDE THE PAGE, which is what makes
        #   "never stored" enforceable rather than promised.
        #
        #   the AIM refuses anything but exactly one match. Two matches erase
        #   the index rather than shortlisting -- an invitation that reaches
        #   whoever was drawn first is the failure this exists to refuse.
        #
        #   NO THIRD PARTY'S PROFILE IS LOADED. The controls are on HIS OWN
        #   profile, which draws nine of them and costs no badge, where
        #   /mynetwork/ would consume the pending-invitation counter.
        "send_invitation",
        # THE NINTH, 2026-09-01, AND THE FIRST THAT TYPES. Everything above
        # it presses a control that already exists; this one puts his words on
        # a page. That is a different kind of capability and it cost the
        # package its "it types nothing" guarantee, which was true, was
        # printed in three places, and was corrected in the same commit.
        #
        #   a measured surface   /preload/sharebox/, three settle-agreeing
        #                        readings at 31 controls, the third carrying
        #                        the census's own "consistent" verdict
        #   a measured anchor    'Text editor for creating content', and
        #                        'Post' -- observed DISABLED on an empty
        #                        composer, which is what makes a post-fill
        #                        gate possible at all
        #   the text             a slice of the GRANT, never composed here.
        #                        One fill site, draining a queue, asserted by
        #                        tests/test_typed_bytes.py on the AST NODE
        #                        rather than on a substring -- because the
        #                        substring version passed a mutation that
        #                        appended a hashtag
        #   a post-fill gate     four conditions, and the load-bearing one is
        #                        the TRANSITION: disabled to enabled. A fill
        #                        that did not land leaves the control disabled
        #                        and this refuses
        #   an empty-box guard   an ALREADY-enabled control means the composer
        #                        is not empty, and page.fill replaces. It
        #                        refuses rather than typing over a draft it
        #                        cannot read back
        #
        # AND ITS OUTCOME IS UNVERIFIABLE, declared: the activity rail renders
        # intermittently (233 controls once, 67 another, same session), and a
        # check that answers nothing on some readings is not a check. The
        # scheduled-posts surface that would have fixed this was measured on
        # 2026-09-01 not to exist for this server.
        "publish_post",
        # THE TENTH, 2026-09-01, and the one that ships EXPECTING TO REFUSE.
        #
        # Its surface, its editor and its aim are all measured. What is NOT
        # measured is the accessible name of the control that posts a comment,
        # because that control does not exist until the box has content -- and
        # putting content in the box is the act this gate authorises. So the
        # submit is identified by ARRIVAL (_comment_submit_gate), and when two
        # controls end up sharing the name 'Comment', which his own screenshot
        # suggests, THE GATE REFUSES AND REPORTS WHAT IT SAW.
        #
        # That refusal is the instrument rather than a failure: the first
        # supervised run produces the measurement nobody could take any other
        # way. Exactly the shape unsave_job took when its ON label could not
        # be observed until one write produced it.
        "comment_on_item",
        # THE SIXTH, 2026-08-31, and the FIRST that is not about a job or a
        # company Page. It is here because every clause the other five needed
        # is now true of it and not because a rule was relaxed:
        #
        #   a measured surface   /mypreferences/d/dark-mode, six readings
        #                        across two days and three builds, no redirect
        #   a measured anchor    three inputs named through aria-labelledby,
        #                        exactly one checked, the role read off the row
        #   a readable origin    which of the three is on, in one call
        #   a real verification  a fresh navigation and a re-read of the
        #                        group's own checked property
        #   no new permission    the click is perform()'s existing one;
        #                        readonly.SANCTIONED_MUTATIONS is unchanged
        #
        # AND NOTHING TO TYPE, which is why this one and not another. Four of
        # the seven capabilities beside it need TEXT ENTRY, and ``fill``,
        # ``type``, ``press`` and ``keyboard`` are on
        # readonly._MUTATION_CALL_PATTERNS and on no entry of
        # readonly.SANCTIONED_MUTATIONS -- so for those the missing thing is a
        # mutation class nobody has sanctioned, not a url.
        "update_setting",
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


def destination_of(spec: WriteSpec, target: str) -> str:
    """The VALUE half of a two-part target, or ``""``.

    A composite target is ``"<subject> :: <value>"`` and the value is the
    destination a multi-state action moves to -- the setting's new value, the
    field's new content. Split here rather than in three call sites, because
    the separator is what binds a token to what the preview showed and a
    second spelling of the split is a second way to disagree with it.
    """
    if spec.target_kind not in _COMPOSITE_TARGET_KINDS:
        return ""
    _first, second = _COMPOSITE_TARGET_KINDS[spec.target_kind]
    if not second:
        return ""
    parts = str(target).split(TARGET_JOIN)
    return parts[1] if len(parts) == 2 else ""


def valid_from(spec: WriteSpec, state: str, target: str) -> tuple[bool, str]:
    """Is ``state`` a state this action may be performed FROM? And why not.

    TWO SHAPES, because the specs have two and collapsing them made one of
    them unperformable. A BINARY TOGGLE is valid from exactly one named
    state, and ``perform``'s gate 5 has always compared against
    ``spec.from_state`` directly. A MULTI-STATE action has ``from_state`` of
    ``None`` -- there is no single origin -- so that same comparison refuses
    EVERY real reading it could ever take, which is not a gate refusing
    something, it is a gate that cannot pass.

    For a multi-state action the question is the one ``_direction`` already
    asks at preview: is the live state one this server has seen LinkedIn
    render, and is it something OTHER than where we are going. Asked again
    here because gate 5's whole job is that the reading at click time is the
    one that counts -- the preview's reading is up to two minutes old, and on
    a setting he may have changed in another tab in between.
    """
    # THE CLICK-TIME STATE, WHICH IS NOT ALWAYS THE PREVIEW'S. See
    # ``WriteSpec.click_from_state``: this is the ONLY reader of that field,
    # and it defaults to ``from_state`` so the ten actions whose two readings
    # coincide are unchanged. What the field buys is that the coincidence is
    # now RULED rather than relied on.
    wanted_here = spec.click_from_state or spec.from_state
    if wanted_here is not None:
        if state == wanted_here:
            return True, ""
        return False, (
            f"{spec.action!r} is valid only from {wanted_here!r} at click time "
            f"and the control on the page reads {state!r}."
        )
    destination = destination_of(spec, target)
    if not destination:
        return False, (
            f"{spec.action!r} has more than two states and this grant names "
            "no destination, so there is no direction to move in."
        )
    if state.strip().casefold() not in spec.audiences:
        return False, (
            f"the control on the page reads {state!r}, which is not a state "
            f"this server has seen LinkedIn render. The known ones are "
            f"{sorted(spec.audiences)}, and a state that cannot be named "
            "cannot be moved from."
        )
    if state.strip().casefold() == destination.strip().casefold():
        return False, (
            f"the setting already reads {state!r}, which is where this grant "
            "was going. Nothing to change -- and this reading is fresher than "
            "the preview's, so it may have been changed elsewhere since."
        )
    return True, ""


def anchor_label_for(
    spec: WriteSpec, target: Optional[str] = None
) -> Optional[str]:
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
    if spec.action == "comment_on_item":
        # THE EDITOR, and there is no submit to name. Unlike publish_post,
        # whose submit is drawn from the start, this action's submit does not
        # exist until the fill lands -- _comment_submit_gate finds it by
        # ARRIVAL afterwards, or refuses.
        return dom.COMMENT_EDITOR_LABEL

    if spec.action == "publish_post":
        # THE EDITOR, NOT THE SUBMIT, and that is the whole difference a
        # typing action makes to this function. For a click action the anchor
        # names the control that will be PRESSED. For a typing action it names
        # the control that will be FILLED -- the submit is not addressed here
        # at all, because it is not addressable until there is something to
        # submit. _publish_submit_gate finds it after the fill, or refuses.
        return dom.POST_EDITOR_LABEL

    if spec.action == "send_invitation":
        # THE SUFFIX, NOT A NAME, and this is the one anchor in the package
        # that is deliberately PARTIAL. LinkedIn labels these controls with
        # another person's name plus " to connect". The name half is a third
        # party's identity and this server does not read it; the suffix half
        # is the part that establishes the control is an invitation, and it is
        # the only part an anchor needs.
        return dom.INVITE_CONTROL_SUFFIX

    if spec.action == "react_to_item":
        # THE OFF LABEL, MEASURED ON THREE SURFACES -- the feed, his profile,
        # and the item permalink itself. LinkedIn writes the toggle state into
        # the accessible name, which makes this the most self-describing
        # anchor in the package: the control says which state it is in.
        #
        # THE ON LABEL HAS STILL NEVER BEEN SEEN, and that gap is carried in
        # `residue` rather than here, because it is about what the gate can
        # say AFTERWARDS and not about what it may press.
        return dom.REACTION_OFF_LABEL

    if spec.action == "update_setting":
        # THE ANCHOR IS PER-CALL, WHICH NO OTHER ACTION'S IS, and that is why
        # this function grew a ``target`` parameter rather than a table entry.
        # The control to be clicked is the one named for the DESTINATION --
        # click ``Always on`` to get Always on -- so the label cannot be
        # derived from the spec alone the way ``Save the job`` can.
        #
        # IT IS STILL NOT A CALLER'S STRING. The destination came through
        # ``_target_for``, is bound into the grant the operator confirmed, and
        # is checked HERE against the closed set of three states this server
        # has actually seen rendered. Anything else returns None and
        # ``perform`` refuses rather than building a selector from it.
        destination = destination_of(spec, str(target or ""))
        for known in DARK_MODE_STATES:
            if destination.strip().casefold() == known.casefold():
                return known
        return None
    if spec.action == "send_message":
        # THE RECIPIENT COMBOBOX, NOT THE SEND CONTROL, and that is the same
        # distinction ``publish_post``'s arm makes: for a typing action the
        # anchor names the control that will be FILLED FIRST, not the one that
        # will be pressed. ``Send`` is not addressed here at all -- it is
        # reached only through ``_send_gate``, after a recipient has been
        # confirmed and the body has landed, or not at all.
        #
        # MEASURED: an input with ``role=combobox`` named ``Enter message
        # recipients`` through ``label-for``, on a 77-control census of
        # ``/messaging/compose/`` taken 2026-08-31 and agreeing again
        # 2026-09-02.
        return dom.MESSAGE_RECIPIENT_LABEL

    if spec.action == "update_profile_field":
        # THE FIELD NAME, PER CALL, and this arm was MISSING when the action
        # shipped in a540461 on 2026-09-02. Its absence was not a subtlety and
        # it is the second time this exact function has had it:
        #
        #     'update_profile_field' has no measured anchor and will not be
        #     performed. ... anchor_label_for has no branch for it ...
        #     NAVIGATIONS ATTEMPTED: []
        #
        # Zero. It raised at ``perform``'s FIRST guard -- before the write
        # door, before the navigation, before any control was read -- while
        # ``grant_is_possible`` still returned True, so ``mint`` handed out a
        # live confirm token, he read a real preview off a real read of his
        # profile, he confirmed, and the second call died. A capability that
        # asks for authorisation and then refuses is worse than one that
        # refuses, because it spends his judgement rather than his time.
        #
        # SEE THE COMMENT ON THE apply_job ARM BELOW. It records the identical
        # defect, in this function, on 2026-08-26 -- "registered, listed in
        # PERFORMABLE, and reported by server_info as performable and
        # irreversible -- and could not run". Seven days apart, and the prose
        # naming the first was on screen when the second was written. That is
        # why ``tests/test_a_performable_action_can_reach_its_control.py``
        # exists and why it fans out over PERFORMABLE rather than listing
        # actions: a comment describing a defect does not prevent its
        # recurrence in the function it is written in.
        #
        # IT IS NOT CHECKED AGAINST A TABLE, and ``update_setting``'s is, and
        # that difference is a fact about the two surfaces rather than a
        # relaxation. Dark mode has THREE STATES THIS SERVER HAS SEEN
        # RENDERED, so a closed set exists to check a destination against. The
        # editor's field list is whatever that container draws today -- the
        # "six approved fields" is prose in a comment, not a measured
        # constant -- and ``_live_control`` checks this name against THE LIVE
        # CONTROL LIST, requiring exactly one match, on the very page the
        # write will act on. That is strictly stronger than any table written
        # at spec time, and it is taken at the moment that counts.
        #
        # AND IT DISCLOSES NOTHING NEW. The field name is already in the
        # grant, already in the canonical target ``consume`` binds the token
        # to, and already printed in the preview he confirms.
        field, _, _ = str(target or "").partition(TARGET_JOIN)
        return field.strip() or None
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
    # ``"publish_post"`` LEFT THIS TABLE ON 2026-09-01. Its refusal named two
    # blockers and BOTH were real; they resolved differently.
    #
    # TYPING was a permission, and the operator granted it -- one page.fill,
    # one drain point, text taken from the grant and never composed here.
    #
    # THE VERIFICATION did not close and was RULED ON. The activity rail is
    # still intermittent and this action still cannot confirm itself; the
    # difference is that the gate now DECLARES that in three parts instead of
    # refusing over it. The declaration also records the thing that would have
    # fixed it and does not exist: a scheduled-posts surface, measured absent
    # on a settle-confirmed composer render the same day.
    # ``"comment_on_item"`` LEFT THIS TABLE ON 2026-09-01, and it is the only
    # action that left while one of its blockers was still OPEN AND NOT RULED
    # ON. Typing was granted and the verification was declared -- but the
    # SUBMIT CONTROL is still unobserved, and no ruling can measure a control.
    # What changed is that the gate now finds it by ARRIVAL after the fill,
    # and REFUSES WITH THE OBSERVATION when it cannot. Shipping a gate that
    # expects to refuse is only honest because the refusal is what produces
    # the missing measurement.
    # ``"update_profile_field"`` LEFT THIS TABLE ON 2026-09-02 by SHIPPING,
    # which is the only way anything is meant to leave it. Its refusal named
    # two blockers and both were real; both were BUILT AWAY rather than ruled
    # around or measured away. The url boundary became an exact-url exemption
    # for one address, and "no field inside any editor has ever been observed"
    # stopped being true when the editor's controls and their values became
    # readable.
    #
    # The three items that refusal listed as remaining -- a select_option
    # sanction, an empty-into-required refusal, and a restore path -- were
    # built WITH the call site rather than before it, which is why they are no
    # longer validators nothing calls.
    # ``"update_setting"`` WAS HERE UNTIL 2026-08-31 AND IS GONE BECAUSE THE
    # ACTION SHIPS. It is removed rather than reworded, on this function's own
    # standing rule: ``_refuse_unperformable`` is for actions that are
    # sanctioned and NOT performed, and ``follow_company`` and ``apply_job``
    # were each removed from it on the day they entered PERFORMABLE. Text left
    # behind for a shipped action is unreachable AND false, which is the pair
    # this package has twice paid for.
    #
    # WHAT IT SAID AND WHY THAT STOPPED BEING TRUE, kept because the entry was
    # specific and whoever comes looking for it deserves the answer rather
    # than a silence. It said: this action holds NO url_template, so
    # writes.mint refuses it a grant AT ISSUE and no confirm_token can exist
    # for it, for anyone; performing it would need a measured write surface
    # AND a new entry in SANCTIONED_MUTATIONS.
    #
    # THE FIRST HALF WAS TRUE AND IS NOW CLOSED: it holds a url_template, on a
    # surface measured six times across two days and three builds.
    #
    # THE SECOND HALF WAS WRONG, and the error is worth carrying because it
    # shaped a whole wave's conclusions. A NEW ENTRY IN SANCTIONED_MUTATIONS
    # WAS NEVER REQUIRED. That list is keyed by (path, function, kind) and
    # already carries ``("linkedin_server/writes.py", "perform", "click")``,
    # so ``perform`` may click any control it can NAME -- what the list
    # refuses is a click somewhere else, or a mutation of another KIND. The
    # sentence read a permission scoped to a CALL SITE as though it were
    # scoped to an ACTION. The audit that quoted it concluded that none of the
    # seven capabilities could have been lifted by any measurement or ruling
    # reachable from here; for this one, and for the two beside it that also
    # need only a click, that was false.
    #
    # WHAT THE LIST DOES STILL REFUSE, and it is the real blocker for four of
    # the remaining seven: ``fill``, ``type``, ``press`` and ``keyboard`` are
    # all on ``readonly._MUTATION_CALL_PATTERNS`` and NONE of them is on
    # ``SANCTIONED_MUTATIONS`` for any function in this package. So an action
    # that has to TYPE something -- publish_post, comment_on_item,
    # update_profile_field, send_message -- needs a mutation CLASS sanctioned,
    # which is a different and larger decision than a url.
    # ``"send_invitation"`` LEFT THIS TABLE ON 2026-09-01, and its two
    # blockers resolved in two different ways worth telling apart.
    #
    # THE AIM CLOSED. It refused because the label is another person's NAME,
    # which this server will not read, so the measurable suffix selected all
    # nine controls. ``aim_invitation`` now resolves HIS OWN needle to exactly
    # one control, with the comparison run inside the page, and refuses two
    # matches rather than shortlisting them.
    #
    # THE VERIFICATION DID NOT CLOSE. It was RULED ON instead: nothing this
    # server may read can confirm a sent invitation, and that is now a
    # declaration the gate prints -- ``unverifiable`` on the spec, naming the
    # Sent Invitations manager, both reasons it is unreachable, and what he
    # must do himself -- rather than a reason to refuse.
    # ``"send_message"`` LEFT THIS TABLE ON 2026-09-02 BY SHIPPING, which is
    # the only way anything is meant to leave it, and it left with one of its
    # three blockers still open -- the same terms comment_on_item shipped on.
    #
    # TYPING was solved on 2026-09-01 and this entry already said so.
    #
    # THE COST was measured and stays UNMEASURABLE: no countable InMail
    # balance exists on either surface this server MAY read -- the composer's
    # `InMail` is a conversation FILTER PILL with aria-checked=false, and
    # /premium/my-premium/ carries no numeric balance of any kind. The gate
    # now DISCLOSES that instead of refusing over it.
    #
    # THE VERIFICATION did not close and was RULED ON, exactly as this entry
    # predicted: nothing can prove a send happened, so the spec names
    # not_performed_state and the action reports NOT SENT or UNKNOWN and never
    # SENT.
    #
    # WHAT THIS ENTRY NEVER NAMED, AND IT IS THE ONE THAT SHAPED THE BUILD:
    # THE RECIPIENT. It listed a surface, a cost and a verification and said
    # nothing about how a message gets ADDRESSED. The recipient control is a
    # typeahead nobody has typed into, and "Send became enabled" is not an
    # aiming fact. That is why the shipped gate requires a committed recipient
    # whose name carries his own needle rather than a count, and why the
    # action ships expecting to refuse.


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
            "set_open_to_work is sanctioned and cannot be performed, and the "
            "ground CHANGED on 2026-09-01 -- it is no longer the absence of a "
            "url. WHAT WAS ALREADY MEASURED, 2026-08-24: its editor is not "
            "addressed by a url at all. 237 distinct urls and 37 payload "
            "paths across five profile captures, zero of which reach it. It "
            "opens as a MODAL from a control on his own profile, and the "
            "single click that would first SHOW that editor is also the first "
            "that could CHANGE it -- the request that click fires is named, "
            "by LinkedIn, saveAndFetchNextStep, and it writes two optimistic "
            "SetState values before the request even leaves. "
            "THE OPERATOR THEN RULED, 2026-09-01, that a click MEASURED to "
            "issue no ServerRequest is by effect a READ -- which is a real "
            "route to a modal, and it is the route this action needed. The "
            "same census nominates the safe first click: a Show details "
            "control whose action list holds one Navigate and NO "
            "ServerRequest. "
            "WHAT REFUSES IT NOW IS THAT THE RULING'S PRECONDITION CANNOT BE "
            "SATISFIED THROUGH THIS TRANSPORT. Those action lists live in the "
            "React flight payload, and the payload is GONE by the time this "
            "server is able to look at the page. Measured live on 2026-09-01, "
            "on a SETTLE-CONFIRMED reading of his profile -- verdict "
            "'consistent', 233 controls expected and 233 read, so the page "
            "had fully arrived: 2 script blocks and 2,146 payload characters, "
            "against 17 blocks and 1,091,238 characters measured "
            "pre-hydration on 2026-08-24. Zero occurrences of every SDUI "
            "action token. Zero needle hits. dom.read_sdui_actions returned "
            "readable=false with error=null -- so the reader RAN and the "
            "payload was ABSENT, which are different diagnoses and this is "
            "the second. "
            "THE DOM CONTROLS ARE ALL STILL THERE -- 'Open to' with "
            "aria-expanded='false', and 'Edit' at count 1. What is gone is "
            "the EVIDENCE ABOUT WHAT THEY DO, and the ruling turns on that "
            "evidence rather than on the controls. A click this server cannot "
            "first measure is not covered by the ruling, and the ruling is "
            "not stretched to cover a control it was not measured for. "
            "WHAT WOULD LIFT IT, and it is HIS decision rather than an "
            "engineering task: the payload exists PRE-HYDRATION. Reaching it "
            "means capturing the document response before the page hydrates, "
            "which is request interception -- 'route' is on "
            "readonly._MUTATION_CALL_PATTERNS -- and that is a materially "
            "LARGER capability than the click this would have authorised: it "
            "lets this server see raw traffic rather than one measured "
            "control. AND IT MAY NOT BE WORTH IT EVEN THEN: the Edit control "
            "still fires saveAndFetchNextStep, so the editor stays behind a "
            "click that saves, and the payload would only settle whether the "
            "AUDIENCE control happens to sit one level shallower. "
            "AND THE OBVIOUS CHEAPER ROUTE WAS CHECKED AND IS FORECLOSED, "
            "recorded here so nobody re-opens it. A plain authenticated HTTP "
            "GET of the profile never hydrates, so it WOULD return the flight "
            "payload intact and restore exactly the measurement this "
            "precondition needs -- with no interception at all. It is "
            "rejected because it is the LARGER change of the two, not the "
            "smaller: 'route' stays inside Playwright, which this server "
            "already is, whereas an HTTP client is a NEW DATA PATH in a "
            "server whose defining property is not having one. pyproject.toml "
            "says so in its own words -- dependencies are exactly "
            "['fastmcp', 'playwright'], and the comment beside them reads "
            "'This server has no HTTP data path at all: every tool drives a "
            "real signed-in Chrome, so an install without playwright is an "
            "install that cannot answer a single call.' Giving a browser-only "
            "server a raw HTTP path to fetch one payload is a louder change "
            "than the interception it would replace. "
            "AND NOTE WHY EVEN THE SAFE CLICK IS UNREACHABLE, which is the "
            "cleanest statement of why this action is stuck: the census rates "
            "steps 1-6 PROVABLY SAFE, and that proof is drawn from the same "
            "flight payload that is absent from a live load. So the safe "
            "first click is blocked by the IDENTICAL missing evidence rather "
            "than by permission. There is nothing to click, because there is "
            "nothing to measure. "
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
    # Added 2026-08-31 with update_setting. It is read by a human at the
    # moment a write hit an auth wall, so "linkedin" -- the default this would
    # otherwise fall back to -- tells him nothing about where to go and look.
    "setting_and_value": "settings",
}


#: WHERE HE GOES TO SETTLE AN OUTCOME THIS SERVER COULD NOT, per action, as
#: ``(url, what to call it in a sentence)``.
#:
#: WHY A TABLE RATHER THAN THE THREE IF/ELSE CHAINS IT REPLACES. Those chains
#: were written when this package performed four actions, all of them about a
#: job or a company Page, and every one of them ended in an ``else`` carrying
#: THE SAVE PAIR'S OWN TEXT. Seven more actions arrived and inherited it
#: silently, because inheriting an ``else`` looks exactly like being handled --
#: which is the same thing ``_verify_after``'s no-catch-all raise exists to
#: stop, one layer further out, in the block that REPORTS the verification
#: rather than in the one that takes it.
#:
#: MEASURED BEFORE IT WAS BUILT, on 2026-09-02, across the five action-keyed
#: chains in ``perform``'s receipt: **8 of the 11 performable actions carried
#: at least one field whose text was written for a different action.** The
#: three clean ones -- ``save_job``, ``unsave_job``, ``unfollow_company`` --
#: are precisely the actions the chains were written for. Live on a
#: ``publish_post`` receipt: the post's own text came back under the key
#: ``company_id``; ``read_this_if_unsure`` called a post a toggle and sent him
#: to his saved jobs; and ``verification.surface`` told him LinkedIn's saved
#: list had confirmed it, on the one action whose spec DECLARES that nothing
#: can confirm it.
#:
#: A MISSING ROW DOES NOT BORROW A NEIGHBOUR'S. :func:`_where_to_look` returns
#: ``None`` and every caller says so in words, because "nobody wrote this for
#: your action" and "open your saved jobs" are different sentences and only one
#: of them can be true. ``tests/test_receipt_names_its_own_action.py`` fails on
#: any performable action absent from this table, so the gap is loud at test
#: time rather than quiet at read time.
#:
#: IT IS A PHRASE AND NOT A URL, deliberately. Three of these places have no
#: address this server may print at all -- ``send_invitation``'s Sent
#: Invitations manager is behind ``/mynetwork/`` and its address contains
#: ``invitation``, which is on ``readonly._FORBIDDEN_URL_SUBSTRINGS`` -- and
#: two more are the acted-on page, whose url is per-target rather than
#: constant. The url the verification ACTUALLY read is already reported, in
#: ``verification.read_from``; this field answers the different question of
#: where a HUMAN goes, and he can open a page this server may not.
_WHERE_TO_LOOK: dict[str, str] = {
    "save_job": "your saved jobs",
    "unsave_job": "your saved jobs",
    "apply_job": "the Applied tab of your job tracker",
    "unfollow_company": "your followed companies",
    # THE FOLLOW'S SECOND OPINION, and it is the one ``_verify_after`` already
    # tells him to take: that branch verifies from the control it just
    # clicked, names itself the weakest witness in this design, and ends
    # "Open your followed companies if you want a second opinion." This is
    # that sentence, in the field built for it.
    "follow_company": "your followed companies",
    "update_setting": "your dark-mode setting",
    "update_profile_field": "the profile editor for that field",
    # THE TWELFTH, and the only row here naming a surface this server
    # deliberately will NOT open. Reading the thread is what would settle
    # a send, and it costs a read receipt on a real person -- his to
    # spend, not this gate's.
    "send_message": "your own LinkedIn messages",
    # THE FOUR WHOSE ANSWER IS NOT ON A SURFACE THIS SERVER MAY READ, and each
    # names the place a HUMAN would look rather than the place this server
    # would. That distinction is the whole value of the field: it is read
    # after an act that may not be repeatable, by somebody who can open any
    # page he likes and is not bound by this server's read boundary.
    "react_to_item": "the post itself",
    "comment_on_item": "the post you commented on",
    "publish_post": "your profile's recent activity",
    "send_invitation": "My Network, then Manage, then Sent",
}

#: THE ACTIONS THAT ARE ACTUAL TOGGLES, for the one sentence that is only true
#: of a toggle.
#:
#: ``read_this_if_unsure`` has warned since August that "a retry on a toggle
#: that did land performs the opposite action". TRUE, and it was printed on
#: all eleven -- including ``apply_job``, where the danger is the opposite
#: shape and worse: a retry does not undo an application, it may file a second
#: one. A generic warning that misdescribes the danger is the same species of
#: confident string as an unmeasured reversibility claim, which is why
#: ``WriteSpec.wrong_state_note`` exists one layer up. This is that rule
#: applied to the receipt.
_TOGGLE_ACTIONS: frozenset[str] = frozenset(
    {"save_job", "unsave_job", "follow_company", "unfollow_company",
     "react_to_item"}
)


def _where_to_look(action: str) -> Optional[str]:
    """The place a human opens to settle this action, or ``None``.

    ``None`` is returned rather than a default, and that is the whole point of
    the function existing. A default here is a sentence sending him to a page
    that cannot answer his question, which is strictly worse than no sentence:
    he reads it, opens it, sees nothing, and concludes something about the
    write from the silence of a surface that was never going to speak.
    """
    return _WHERE_TO_LOOK.get(action)


#: WHAT THE VERIFICATION'S EVIDENCE ACTUALLY IS, per action, in the words the
#: receipt prints beside the verdict.
#:
#: THESE ARE THREE DIFFERENT PROMISES AND THE RECEIPT SAYS WHICH IT MADE. A
#: DIFFERENT surface from the one clicked is the ideal shape; the SAME page
#: reloaded is a fresh render from LinkedIn and is weaker; reading back the
#: control that was just pressed is the weakest, because it is testifying about
#: its own effect. Flattening them would be the same species of confident
#: string this module keeps refusing to print -- and until 2026-09-02 the
#: flattening was in the other direction: six actions printed the save pair's
#: "a DIFFERENT surface ... LinkedIn's own saved list", which for all six named
#: evidence that does not exist.
_VERIFIED_FROM: dict[str, str] = {
    "save_job": (
        "a DIFFERENT surface from the one clicked. A control that redraws "
        "itself is the weakest possible witness to its own effect, so the "
        "confirmation comes from LinkedIn's own saved list with its own "
        "per-tab count."
    ),
    "apply_job": (
        "a DIFFERENT surface from the one clicked -- the tracker's APPLIED "
        "tab, with LinkedIn's own per-tab count reconciling it. Until "
        "2026-08-31 this read the SAVED tab, whose three answers do not "
        "include 'applied', so the comparison could not pass and every apply "
        "reported 'unknown'."
    ),
    "unfollow_company": (
        "THE SAME PAGE, RELOADED, and there is no other: LinkedIn lists "
        "followed Pages on exactly one surface. A fresh navigation is a fresh "
        "render from LinkedIn rather than a control that redrew itself in "
        "place -- stronger than reading the button just pressed, weaker than "
        "an independent surface, and said plainly rather than implied. The "
        "verdict rests on LinkedIn's own stated total, not on the row's "
        "absence."
    ),
    "update_setting": (
        "THE SAME PAGE, RELOADED, and read through LinkedIn's own checked "
        "property on a group of three rather than through a label the control "
        "chose to draw. There is no second surface for a setting -- the page "
        "that renders the value is the page that sets it -- so this is a "
        "fresh render from LinkedIn rather than an independent witness, and "
        "saying which is the point. It is stronger than reading back the "
        "button just pressed: a control that redrew wrongly would have to "
        "report itself checked AND the other two report themselves unchecked "
        "to pass this."
    ),
    "react_to_item": (
        "THE SAME PAGE, RELOADED. There is only one surface carrying this "
        "item's reaction state, so this is a fresh RENDER from LinkedIn "
        "rather than a second source. What it reads is the control's own "
        "accessible name, which LinkedIn writes the toggle state into. It "
        "says the reaction MOVED and does not say what to -- the ON label has "
        "never been observed."
    ),
    "update_profile_field": (
        "THE SAME PAGE, and there is no other -- the editor is the only place "
        "this value lives. So this is a FRESH READ rather than an independent "
        "corroboration, and the difference between those two is the "
        "difference between evidence and the appearance of it. What it buys "
        "is the value as the page holds it now, after the write."
    ),
    "follow_company": (
        "THE CONTROL THAT WAS JUST CLICKED, on the page it was clicked on. "
        "That is the WEAKEST verification in this design and it is labelled "
        "as such rather than presented as equal to the other two: the control "
        "is testifying about its own effect. The stronger read is not "
        "available here because this action's direction came from the posting "
        "rather than from a list that could be counted before and after."
    ),
}
_VERIFIED_FROM["send_message"] = (
    "THE COMPOSER, RE-READ, and it answers only the NEGATIVE. A composer "
    "still on screen with Send still enabled is what holding un-dispatched "
    "text looks like on this surface, so that reading reports NOT SENT. "
    "Nothing here can report SENT: the only surface that could is the thread, "
    "which is forbidden AND costs a read receipt on a real person. So this "
    "action can be shown not to have happened and cannot be shown to have "
    "happened, which is the honest shape rather than a shortfall."
)
_VERIFIED_FROM["unsave_job"] = _VERIFIED_FROM["save_job"]


#: A landed profile path, split into the MEMBER SEGMENT and everything after
#: it. Used only by :func:`_assert_landed_on_target`, and only to allow the
#: segment to differ while holding the rest exact.
#:
#: NOT IMPORTED FROM ``server.py``, which has ``_MEMBER_SEGMENT`` and
#: ``_path_without_member`` for its own self-ownership block. ``server``
#: imports ``writes``, so the dependency only runs one way, and a second
#: spelling here is the cost of that. It is a THREE-LINE regex whose job is
#: different from theirs -- they redact a segment for printing, this compares
#: the path around one -- so the two are not a rule with two implementations.
_MEMBER_PATH = re.compile(r"^(?:/in/)([^/?#]+)(/.*)?$")


def _path_of(url: str) -> str:
    """The path of a url, with no scheme, host, query or fragment."""
    return urlsplit(str(url or "")).path


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

    # THE SELF-PROFILE SHAPE, ADDED 2026-09-02, AND WITHOUT IT NO ``/in/me/``
    # ACTION COULD EVER HAVE PASSED THIS GUARD.
    #
    # ``/in/me/`` REDIRECTS. That is not an edge case -- it is the entire
    # reason that spelling is the only profile form on the read allowlist, and
    # ``readonly``'s own comment beside the pattern says so: "Own profile.
    # /in/me/ redirects to whoever is signed in." A whole-url comparison was
    # never going to hold against it, and it held only because nothing had
    # ever navigated there to WRITE. Measured live 2026-09-01 and recorded in
    # _audit/2026-08-31-linkedin-perform.md:
    #
    #     requested  /in/me/edit/intro/
    #     landed     /in/<member>/edit/intro     (and no trailing slash)
    #
    # TWO ACTIONS ARE AFFECTED, not one: ``update_profile_field`` and
    # ``send_invitation``, whose surface is ``/in/me/``. The second resolves
    # its anchor cleanly and failed HERE, which is why it looked healthy.
    #
    # WHAT MAKES THE RELAXATION SAFE, and it is a property of the REQUEST
    # rather than of the landing. The member segment is allowed to differ; the
    # path after it is not. And the reason a differing segment cannot be a
    # stranger is that the url was not chosen by a caller -- ``assert_write_url``
    # REBUILDS it from the grant, ``readonly`` admits only the ``/in/me/``
    # spelling, and ``/in/me/`` can resolve to exactly one member: the one
    # signed in. So this accepts "LinkedIn told us who you are" and refuses
    # everything else.
    #
    # IT IS NOT ``census_substitute`` ON BOTH SIDES, which was the first thing
    # tried and is WRONG. That reduces EVERY member segment to the same
    # ``<member>`` token, so HIS editor path and A STRANGER'S editor path
    # normalise to one identical string and compare EQUAL -- measured before
    # it was rejected. A comparison that cannot tell those two apart is not a
    # landing check. The exactly-one-member-can-answer argument above is what
    # does the work, and it needs the REQUESTED segment to be literally ``me``.
    #
    # (The two example paths are described rather than written out. They were
    # written out in the first draft of this comment and
    # ``test_no_committed_identity`` refused the file for two SLUG-SHAPED
    # strings -- invented ones, which is no defence, because the rule is on
    # the shape and a reviewer cannot tell an invented vanity slug from a real
    # one. Same guard, same lesson, as the urn literal it caught an hour
    # earlier in a test file.)
    expected_member = _MEMBER_PATH.match(_path_of(expected))
    if expected_member is not None and expected_member.group(1) == "me":
        landed_member = _MEMBER_PATH.match(_path_of(landed))
        if landed_member is None:
            raise WriteAttemptError(
                f"refusing to click: this action is performed on his own "
                f"profile at {expected!r} and the browser landed on {landed!r}, "
                "which is not a /in/<member>/ url at all. A redirect that "
                "leaves the profile family is not the redirect this action "
                "expects."
            )
        want = (expected_member.group(2) or "").rstrip("/")
        got = (landed_member.group(2) or "").rstrip("/")
        if want != got:
            raise WriteAttemptError(
                f"refusing to click: this action is performed on {expected!r} "
                f"and the browser landed on {landed!r}. The member segment is "
                "allowed to differ -- /in/me/ redirects to whoever is signed "
                f"in -- but the path after it is not: this expects {want!r} "
                f"and the page is showing {got!r}."
            )
        return

    if str(landed).rstrip("/") != expected.rstrip("/"):
        # THE SENTENCE IS THE ACTION'S OWN, and until 2026-09-02 it was the
        # unfollow's, printed on everything that reached here. A profile field
        # edit was told "a list write is anchored to a row on one page", which
        # is the borrowed-prose defect commit 3742a2d removed from the
        # RECEIPT -- arriving here in a GATE. A refusal is the worse place for
        # it: a receipt describes what happened, a refusal is what he reads
        # while the server is STOPPING him, and a wrong explanation there
        # teaches him the wrong model of what is safe.
        raise WriteAttemptError(
            f"refusing to click: this action is performed on {expected!r} and "
            f"the browser landed on {landed!r}. "
            + (
                "A list write is anchored to a row on one page, so landing "
                "anywhere else means the row this grant names is not on the "
                "screen."
                if spec.target_kind == "company_id"
                else "This action acts on one measured surface and that is "
                "not it, so nothing here is the control this grant names."
            )
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
) -> Union[tuple[str, str, str], tuple[str, str, str, str]]:
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
    if spec.action == "update_profile_field":
        # AIM FROM THE LIVE CONTROL LIST, never from a remembered selector.
        # ``perform`` has already navigated to the editor, so this reads the
        # controls that are on the page RIGHT NOW and matches the requested
        # field against them. The surface moved once in thirty-six hours; a
        # selector baked at design time would have aimed at whatever replaced
        # it.
        # ``include_dom_id=True`` IS THE ONLY PLACE THIS FLAG IS PASSED, and
        # it is what makes the arm below able to aim at all. The reader's
        # default projection deliberately omits the id so the TOOL path never
        # publishes one; this call is the write path, which needs a selector
        # and never prints what it builds it from.
        reading = await dom.read_self_owned_editor_fields(
            page, include_dom_id=True
        )
        if reading.get("refused"):
            return (UNKNOWN, str(reading.get("reason") or ""), "")

        controls = list(reading.get("fields") or [])
        wanted, _, new_value = grant.target.partition(TARGET_JOIN)
        wanted = wanted.strip()

        matches = [c for c in controls if str(c.get("name") or "") == wanted]
        if len(matches) != 1:
            # NAMING WHAT IT SAW, BUT NOT RAW. This reader returns accessible
            # names UNGATED -- that is its documented nature and the reason it
            # is safe only inside a container measured to be his own. One of
            # the controls in this editor is named by its OWN CONTENT (the
            # headline), which is why that field is refused outright, and a
            # refusal that echoed the list verbatim would publish it while
            # explaining why it would not.
            #
            # So the list is shaped before it is printed: a label route keeps
            # its name, anything named by its own text becomes <opaque>, and
            # the guard gets the last word on either.
            seen = []
            for control in controls:
                name = str(control.get("name") or "")
                source = str(control.get("name_source") or "")
                if source in ("aria-label", "aria-labelledby", "label-for",
                              "label-ancestor") and not shape.looks_name_shaped(name):
                    seen.append(name)
                else:
                    seen.append(shape.CENSUS_OPAQUE)
            return (
                UNKNOWN,
                f"{len(matches)} controls in this editor are named {wanted!r}, "
                f"where exactly one is required. What the editor drew: {seen}. "
                "Aiming at one of several, or at none, would be aiming by "
                "document order -- which is the thing this gate exists not to "
                "do. Nothing was typed.",
                "",
            )

        control = matches[0]

        # THE EMPTY-INTO-REQUIRED REFUSAL. It reads the ``required`` flag the
        # label reader returns, which is a tri-state: True, False, or None for
        # a control that cannot be required at all.
        #
        # IT GUARDS AN EMPTY SET TODAY, and saying so is the point rather than
        # a hedge -- none of the six approved fields has been observed
        # required. It is here because the page moved once in thirty-six hours
        # and because clearing a required field is the one edit whose failure
        # mode is a profile LinkedIn will not let him save, discovered after
        # the value is already gone.
        if control.get("required") is True and not new_value.strip():
            return (
                "editor_addressed",
                f"{wanted!r} is drawn REQUIRED and the requested value is "
                "empty. Emptying a required field is refused rather than "
                "attempted: the old value is gone either way, and what comes "
                "back is a form that will not save.",
                "",
            )

        # THE ADDRESSABLE HANDLE. `dom_id` was added to EDITOR_FIELDS_JS for
        # exactly this: the six editable fields are `label-for` named, so the
        # name is what a human reads and the id is what a write can aim at.
        # NO FALLBACK. A control with no id is refused rather than addressed
        # by position or by text -- both of those are the aiming this gate
        # exists to refuse.
        dom_id = str(control.get("dom_id") or "").strip()
        if not dom_id:
            return (
                "editor_addressed",
                f"{wanted!r} was found exactly once and carries no id, so "
                "there is no way to aim at it that is not positional. "
                "Refused rather than addressed by document order.",
                "",
            )
        # REFUSE, DO NOT SANITISE. An id carrying a member token is one this
        # server does not aim with, and there are two independent ways to be
        # unusable:
        #
        #   IT LOOKS LIKE IDENTITY  -- ``census_substitute`` CHANGES it, which
        #       means it matched a urn, a member path, a company path or a
        #       long digit run. LinkedIn does write ids of that shape
        #       (``ember-view-urn:li:fsd_profile:<id>``).
        #   IT WOULD BREAK THE SELECTOR -- a character that ends the quoting.
        #
        # SANITISING IS NOT THE ALTERNATIVE and would be worse in both cases:
        # a substituted id addresses nothing, so the write would aim at a
        # control that does not exist while reporting success on the fill. A
        # refusal states the situation; a scrubbed id hides it. This is the
        # rule ``dom.comment_submit_selector`` already applies to a shaped
        # name carrying ``<``.
        #
        # NEITHER BRANCH ECHOES THE ID. The one on the left is the thing being
        # refused for possibly carrying identity, so printing it to explain
        # the refusal would be the disclosure the refusal exists to prevent --
        # the same rule ``_comment_submit_gate`` follows when it declines to
        # quote a shaped label.
        if shape.census_substitute(dom_id) != dom_id:
            return (
                "editor_addressed",
                f"the control named {wanted!r} carries a dom id that this "
                "server's own identity substitution CHANGES -- so it matched a "
                "urn, a member or company path, or a long digit run. It is "
                "refused rather than scrubbed, and it is NOT printed here: an "
                "id that failed this check is the one string on this path most "
                "likely to name somebody. Nothing was typed.",
                "",
            )
        if any(bad in dom_id for bad in dom._SELECTOR_UNSAFE):
            return (
                "editor_addressed",
                f"the control named {wanted!r} carries a dom id containing a "
                "character that would end the selector's own quoting, so no "
                "safe selector can be built from it. Refused rather than "
                "escaped: an escaping rule is a second predicate nobody has "
                "reviewed. Nothing was typed.",
                "",
            )
        if control.get("disabled") is True:
            return (
                "editor_addressed",
                f"{wanted!r} is drawn disabled. A disabled control is not "
                "typed into to find out what happens.",
                "",
            )

        # WHICH MUTATION THIS CONTROL TAKES, decided HERE because this is where
        # the control was read. ``dom.aria_role_of`` sets the pattern: a kind
        # is derived from the row that was measured, never guessed at the call
        # site from a selector string.
        #
        # A FOURTH ELEMENT RATHER THAN A WIDER TUPLE EVERYWHERE. The other
        # eight arms answer a question that has one answer -- their control is
        # clicked -- and rewriting all of them to say "click" would be eight
        # chances to typo inside the function that presses things. ``perform``
        # unpacks with a star and defaults to a click, so only the arm that
        # has something new to say says it.
        tag = str(control.get("tag") or "").lower()
        kind = "select_option" if tag == "select" else "fill"
        return (
            "editor_addressed",
            f"the editor drew exactly one control named {wanted!r}, it is "
            f"enabled, it carries an id to aim at, and it is a {tag!r} so this "
            f"write would {kind}. Read live from the page this write would act "
            f"on, not from the preview.",
            "#" + dom_id,
            kind,
        )

    if spec.action == "update_setting":
        # THE SAME READER THE PREVIEW USED, ON THE SAME PAGE -- so this is
        # FRESHNESS rather than a second source, and it is labelled that way
        # here for the reason ``follow_company``'s branch is: a gate that
        # implied two independent readings when it took one would be
        # overstating its own evidence.
        #
        # NO NEW SCRIPT AND NO NEW WAIVER. ``_read_dark_mode`` calls
        # ``dom.read_surface_census``, which is declared and scanned, and this
        # calls ``_read_dark_mode``.
        facts, state, why = await _read_dark_mode(page, spec)
        if state == UNKNOWN:
            return (UNKNOWN, why, "")
        ok, refusal = valid_from(spec, state, grant.target)
        if not ok:
            # No selector, so ``perform`` stops. Returning the state and the
            # reason rather than raising keeps the refusal in one place.
            return (state, refusal + " " + why, "")
        # THE ROLE IS READ, NOT ASSUMED, and this is what ``input_type`` was
        # added to the census for. An ``<input>``'s ARIA role is decided by
        # its type -- ``radio`` and ``checkbox`` are two different roles
        # wearing one tag -- and the accessible-name selector engine needs the
        # role spelled correctly or it matches nothing. Six readings of this
        # page establish three checkable inputs; NONE of them establishes
        # which of the two types they are, because the census's ``checked``
        # gate admits both. So it is read here, off the row about to be
        # clicked, and an unexpected type refuses rather than guessing.
        rows = [
            row
            for row in facts.get("rows", [])
            if str(row.get("shape") or "").strip().casefold()
            == anchor.strip().casefold()
        ]
        if len(rows) != 1:
            return (
                state,
                f"{len(rows)} controls on this page are named {anchor!r} and "
                "exactly one is required: at zero the destination is not "
                "rendered and at two or more choosing between them would be "
                "choosing by position. " + why,
                "",
            )
        role = dom.aria_role_of(rows[0])
        # CHECKED AGAINST THE MAPPED SET, not merely against ``None``, and the
        # difference is whether this branch can fire at all. ``_read_dark_mode``
        # only ever yields rows whose ``checked`` is not ``None``, and an
        # ``<input>`` gets one only when its type is radio or checkbox -- both
        # mapped -- so a ``None`` role cannot arrive from an input and the
        # branch would have been unreachable. WHAT CAN ARRIVE is an element
        # carrying ``aria-checked``: a ``div[role=switch]`` named for the
        # destination is a checkable row whose role this package maps nothing
        # from. Without this it reaches ``named_role_selector``, which RAISES
        # rather than refusing -- a safe failure wearing the wrong shape, and
        # one that skips ``wrong_state_note``.
        if role not in set(dom.INPUT_TYPE_ROLES.values()):
            return (
                state,
                f"the control named {anchor!r} is a "
                f"{str(rows[0].get('tag') or '?')!r} carrying role {role!r}, "
                "which is not a shape this server has seen this setting "
                "rendered as. Six readings of this page found three checkable "
                "INPUTS; a control that is something else -- a switch, a "
                "div wearing aria-checked -- is refused rather than clicked, "
                "because what a wrong role produces here is a selector that "
                "matches nothing or matches something else. " + why,
                "",
            )
        # AIM AT THE LABEL, NOT THE INPUT -- measured 2026-09-03, after the
        # first live fire came back clicks_made: 0 with the input resolved
        # correctly and every click intercepted by a decorative div. The role
        # check above still runs and still refuses an unmeasured shape: what
        # changed is only WHICH element carrying that name gets pressed. See
        # dom.settings_radio_label_selector for the two candidates measured
        # and why a direct label[for=] query refuted the inference drawn from
        # the census's name_source.
        # AND THE BINDING IS VERIFIED BEFORE THE SELECTOR IS HANDED BACK.
        #
        # The builder matches a label by its TEXT, which is a naming relation.
        # What moves a radio is <label for=X> binding to the control with id X,
        # which is an ACTIVATION relation. They look identical on a page and
        # only one of them does anything -- confusing them is what cost this
        # round, so the second is read rather than inferred.
        #
        # IT PASSES TODAY, measured on all three radios. It is here because
        # nothing in the markup requires it to keep passing, and because the
        # failure it catches is the one that looks like success: a label with
        # the right text and no 'for' would click cleanly and set nothing.
        # THE LABEL AIM APPLIES TO RADIOS ONLY, because a radio is the only
        # shape whose input was MEASURED unclickable. On 2026-09-03 the live
        # dark-mode page covered its three radio inputs with a decorative div
        # and every click was intercepted; that is the defect this route
        # exists for. NOTHING HAS MEASURED A CHECKBOX ON THIS SURFACE, and
        # applying a radio's remedy to a shape nobody has read would be the
        # same guess this arm refuses everywhere else -- it was applied to
        # every checkable role for about an hour and three tests said so.
        if role != "radio":
            return (state, why, dom.named_role_selector(role, anchor))

        binding = await dom.read_radio_label_binding(page, role, anchor)
        if not binding["bound"]:
            return (
                state,
                "the control is in the right state and this server will not "
                "press its label: " + str(binding["why"]) + " " + why,
                "",
            )
        return (
            state,
            why + " " + str(binding["why"]),
            dom.settings_radio_label_selector(anchor),
        )

    if spec.action == "comment_on_item":
        # THE FILL TARGET. There is no emptiness check to make here and the
        # absence is deliberate: publish_post can tell an empty composer from
        # a full one because its submit is DISABLED while empty, and this
        # surface has no such signal -- which is the same measured fact that
        # forces the delta gate. So this checks what it can (exactly one
        # editor, on a page drawing the comment affordance) and leaves the
        # submit question to the gate that runs after the fill.
        reading = await dom.read_comment_surface(page)
        if reading.get("error"):
            return (UNKNOWN, str(reading["error"]), "")
        editors = int(reading.get("editors") or 0)
        if editors != 1:
            return (
                UNKNOWN,
                f"{editors} comment editor(s) rendered on this permalink, "
                "where exactly one is the shape measured on 2026-09-01. Zero "
                "is a page that had not arrived -- an absent editor is "
                "UNKNOWN and never an empty comment box.",
                "",
            )
        names = dict(reading.get("names") or {})
        affordances = int(names.get(dom.COMMENT_CONTROL_NAME, 0))
        return (
            "comment_control_present",
            "the permalink drew exactly one editor named "
            f"{dom.COMMENT_EDITOR_LABEL!r}, and "
            f"{affordances} control(s) named {dom.COMMENT_CONTROL_NAME!r} "
            "were counted BEFORE anything was typed -- which is the baseline "
            "the delta gate will diff against after the fill. Note this "
            "server cannot tell whether the box is already empty: on this "
            "surface nothing changes state with content, which is the whole "
            "reason a delta is needed.",
            dom.comment_editor_selector(),
        )

    if spec.action == "send_message":
        # THE COMPOSER MUST BE EMPTY, AND EVERY CLAUSE HERE IS A MEASURED
        # SHAPE RATHER THAN A PRECAUTION.
        #
        # ``read_compose_fields`` refuses outright if ANY recipient is already
        # committed, and that refusal is reused rather than re-implemented:
        # once somebody is in the box this reader's whole self-ownership
        # argument evaporates, and a composer holding a stranger is not a
        # composer this gate may type into. It also enforces exactly two
        # dispatch radios with exactly one checked, and exactly one
        # ``div[role=textbox]`` -- which is what identifies the body, since
        # the body carries no usable label.
        reading = await dom.read_compose_fields(page)
        if reading.get("refused"):
            return (
                UNKNOWN,
                "the composer was not in the state this gate acts from: "
                + str(reading.get("why") or reading.get("refused")),
                "",
            )

        send = await dom.read_compose_send_state(page)
        if send.get("error"):
            return (UNKNOWN, str(send["error"]), "")
        if int(send.get("textboxes") or 0) != 1:
            return (
                UNKNOWN,
                f"{send.get('textboxes')} div[role=textbox] on this page, "
                "where the composer's body is measured at exactly one. The "
                "body carries no label this server may use, so the COUNT is "
                "its whole identification -- at any other number a fill would "
                "be aiming by document order.",
                "",
            )
        if int(send.get("controls") or 0) != 1:
            return (
                UNKNOWN,
                f"{send.get('controls')} control(s) named "
                f"{dom.MESSAGE_SEND_NAME!r} are drawn, where exactly one is "
                "the measured shape. Zero is a page that had not arrived; "
                "more than one and pressing either would be picking by "
                "position.",
                "",
            )
        if send.get("enabled") is not False:
            # AN ENABLED SEND ON AN EMPTY COMPOSER IS NOT THE MEASURED STATE.
            # ``Send`` is measured DISABLED with no recipient and no body, so
            # an enabled one means something is already in this composer that
            # this server did not put there and cannot read back. Same rule as
            # publish_post's already-enabled refusal, and the same reason: a
            # fill REPLACES, and replacing a draft he wrote is a side effect
            # he did not ask for.
            return (
                UNKNOWN,
                "the Send control is already ENABLED before anything was "
                "typed. On this surface it is measured DISABLED on an empty "
                "composer, so something is already in that box -- a draft "
                "LinkedIn restored, most likely his. This gate will not type "
                "over content it cannot read back. Open the composer yourself "
                "and clear it.",
                "",
            )
        return (
            "composer_empty",
            "the composer is empty and in the shape this action is measured "
            f"to act from: no recipient committed, exactly one "
            f"div[role=textbox] for the body, and exactly one control named "
            f"{dom.MESSAGE_SEND_NAME!r} drawn DISABLED -- which on this "
            "surface is what empty looks like. The recipient combobox is the "
            "first fill target; the body is typed only if the recipient gate "
            "confirms a committed recipient carrying your own needle.",
            dom.compose_recipient_selector(),
        )

    if spec.action == "publish_post":
        # THIS RETURNS THE FILL TARGET, not a click target. perform routes it
        # into fill_plan rather than click_plan for anything in
        # TYPING_ACTIONS, and the publish control is reached only through
        # _publish_submit_gate afterwards.
        reading = await dom.read_post_composer(page)
        if reading.get("error"):
            return (UNKNOWN, str(reading["error"]), "")
        editors = int(reading.get("editors") or 0)
        submits = int(reading.get("submits") or 0)
        if editors != 1 or submits != 1:
            return (
                UNKNOWN,
                f"the composer drew {editors} editor(s) and {submits} publish "
                "control(s), where exactly one of each is the shape measured "
                "on three agreeing readings. Zero of either is a page that "
                "had not arrived, which is UNKNOWN and never an empty "
                "composer.",
                "",
            )
        if reading.get("submit_enabled") is not False:
            # THE COMPOSER IS NOT EMPTY, AND THIS REFUSES RATHER THAN TYPING.
            #
            # page.fill REPLACES a field's contents. The publish control is
            # measured DISABLED on an empty composer, so an ENABLED one means
            # something is already in the box -- a draft LinkedIn restored,
            # most likely his. Filling over it would destroy text this server
            # never saw and cannot recover, and it would do so silently.
            #
            # There is no reachable surface on which such a draft could be
            # inspected first: 17 candidate draft-listing addresses were run
            # against the read boundary on 2026-08-31 and all 17 refused.
            return (
                UNKNOWN,
                "the publish control is already ENABLED before anything was "
                "typed, which on this surface means the composer is NOT "
                "empty -- it is measured disabled when it is. Something is in "
                "that box, most likely a draft LinkedIn restored, and this "
                "gate will not type over content it cannot read back or "
                "restore. Open the composer yourself and clear it.",
                "",
            )
        return (
            "composer_present",
            "the composer drew exactly one editor named "
            f"{dom.POST_EDITOR_LABEL!r} and exactly one publish control named "
            f"{dom.POST_SUBMIT_NAME!r}, and that control is DISABLED -- which "
            "on this surface is what an empty composer looks like, so there "
            "is nothing here to type over.",
            dom.post_editor_selector(),
        )

    if spec.action == "send_invitation":
        # THE NEEDLE IS HANDED STRAIGHT INTO THE PAGE and the comparison
        # happens there. That is what makes "the label is never stored"
        # ENFORCEABLE rather than promised: a name that reaches Python can
        # reach a traceback, a log line or a cache key, and no care downstream
        # un-rings that. See dom.INVITE_NEEDLE_JS.
        #
        # reveal_single_match is NOT asked for here. The label is revealed
        # only in the preview, by _name_the_invitation_recipient, into a dict
        # built AFTER grant.preview is assigned -- so the grant provably never
        # held it. Asking for it again at click time would put it in this
        # function's scope for no purpose, and the purpose is the whole test.
        reading = await dom.read_invitation_surface(page, grant.target)
        verdict, why, index = aim_invitation(reading)
        if verdict != INVITE_AIMED or index is None:
            # THE NEEDLE IS NOT IN ``why`` and must never be: aim_invitation
            # builds these sentences out of COUNTS. Asserted by
            # tests/test_needle_never_escapes.py, shown failing at a mutation
            # that interpolates it.
            return (UNKNOWN, why, "")
        return (
            "invite_control_present",
            why,
            dom.invite_control_selector(index),
        )

    if spec.action == "react_to_item":
        # THE PERMALINK DRAWS EXACTLY ONE, which is the whole reason this
        # action is aimed at a permalink and not at the feed. The feed and his
        # profile draw eight, and choosing among eight would be choosing by
        # position -- the objection that blocked this action until the
        # permalink was admitted.
        reading = await dom.read_reaction_surface(page)
        controls = int(reading.get("controls") or 0)
        off = int(reading.get("off_state") or 0)
        if controls != 1:
            return (
                UNKNOWN,
                f"{controls} reaction control(s) rendered on this permalink "
                "and exactly one is the only shape this gate can act on. Zero "
                "means the page had not drawn the item -- an absent control "
                "is UNKNOWN and never 'no reaction' -- and more than one means "
                "this is not the single-item render it was measured to be, so "
                "pressing either would be picking by position.",
                "",
            )
        if off != 1:
            return (
                "reacted",
                "the one reaction control on this permalink is NOT wearing "
                f"{dom.REACTION_OFF_LABEL!r}, so this item already carries a "
                "reaction. This action is valid only from the un-reacted "
                "state, and the label that would say WHICH reaction is "
                "already there has never been measured -- so it cannot even "
                "report what it is declining to overwrite.",
                "",
            )
        return (
            "no_reaction",
            "the one reaction control on this permalink reads "
            f"{dom.REACTION_OFF_LABEL!r}, read off the very control the click "
            "will land on, after the click url was loaded. LinkedIn writes "
            "the toggle state into this name, so this is the control stating "
            "its own state rather than an inference from anything around it.",
            dom.reaction_control_selector(),
        )

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


async def _editor_value_of(page: Any, field: str) -> tuple[Optional[str], str]:
    """The current value of ONE named control in the open editor.

    Returns ``(value, why)``; ``value`` is None when it could not be read, and
    None is never collapsed into an empty string -- "I could not read it" and
    "it is empty" are the two answers this package refuses to conflate, and
    they are the two that matter most on a restore.

    NOT A SECOND SURFACE, AND IT SAYS SO. The editor is the only place this
    value lives, so this is a FRESH READ of the same page rather than an
    independent corroboration. ``update_setting``'s branch makes the same
    distinction for the same reason: a gate that implied two readings when it
    took one would be overstating its own evidence.

    FOR A SELECT IT RETURNS THE OPTION'S RENDERED TEXT, not the value
    attribute -- which is what makes the restore exact. The same string is
    what ``select_option(label=...)`` matches, what the preview printed, and
    what he agreed to.
    """
    reading = await dom.read_self_owned_editor_values(page)
    if reading.get("refused"):
        return (None, str(reading.get("reason") or "the editor could not be read."))
    records = [
        record
        for record in (reading.get("fields") or [])
        if str(record.get("name") or "") == field
    ]
    if len(records) != 1:
        return (
            None,
            f"{len(records)} controls named {field!r} carry a value, where "
            "exactly one is required.",
        )
    value = records[0].get("value")
    if value is None:
        return (None, f"{field!r} was found but its value could not be read.")
    return (str(value), f"read live from the editor after the write.")


async def _verify_after(
    navigator: Any,
    page: Any,
    spec: WriteSpec,
    grant: WriteGrant,
    observation: Observation,
    prior_value: Optional[str] = None,
) -> tuple[str, str, str]:
    """Read whether it landed, and read it somewhere the click did not reach.

    Returns ``(state, why, read_from_url)``.

    THE SAVE PAIR gets the ideal shape: the click happens on the posting and
    the confirmation is read off the saved list, a different surface entirely,
    carrying LinkedIn's own per-tab count.

    APPLY GETS THE SAME SHAPE ON A DIFFERENT TAB, since 2026-08-31, and until
    then it got the saved one. That was not a wrong string but a check that
    could not pass: apply's ``to_state`` is ``"applied"`` and the saved read
    returns ``saved`` / ``not_saved`` / ``unknown``, so the comparison was
    false on every reading it could take. It reads ``?stage=applied`` now, by
    the same reconciliation -- absence counts only when LinkedIn's own tab
    count says the whole list was drawn, which matters more here than on the
    saved tab: reporting an unreconciled absence would be telling him an
    IRREVERSIBLE act did not happen when the row is merely below the fold.

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

    A DECLARED-UNVERIFIABLE ACTION RETURNS BEFORE ANY OF THAT, added
    2026-09-01. It does not navigate, does not read, and does not compare --
    it returns ``UNKNOWN`` carrying the declaration's own words. THAT ORDER IS
    THE SAFETY PROPERTY, not a shortcut: the failure this replaces was a
    comparison that ran, could not pass, and reported its own failure as
    though it were a finding. An action that has nothing to check must reach
    NO comparison at all, because a comparison that exists is a comparison
    somebody will later read as evidence.
    """
    if spec.unverifiable is not None:
        return (
            UNKNOWN,
            spec.unverifiable.why_it_cannot
            + " This is a DECLARED unverifiable outcome, not a check that "
            "failed: nothing was read and nothing was compared, because there "
            "is nothing that could answer it. "
            + spec.unverifiable.what_he_must_do,
            "",
        )
    # EVERY BRANCH BELOW THAT RE-NAVIGATES FORMATS ``spec.url_template``, and
    # until 2026-09-02 none of them checked it first. That was safe, and it was
    # safe BY COINCIDENCE: all ten performable actions happen to carry a url,
    # and nothing anywhere requires that. It is the same accident found four
    # times elsewhere the same day -- three assertions and one derived safety
    # property encoding "unperformable implies unaddressed" -- running in the
    # OPPOSITE direction here: "performable implies addressed".
    #
    # An action made performable without a url would not have been refused. It
    # would have raised AttributeError on ``None.format`` from inside the
    # verification step, AFTER the click had already happened -- reporting a
    # crash where a boundary belongs, on the one code path where the operator
    # most needs to know what did and did not occur.
    if spec.url_template is None:
        raise WriteAttemptError(
            f"{spec.action!r} is performable and has no url_template, so the "
            "outcome cannot be verified: there is no surface to re-read. This "
            "is refused rather than attempted because the alternative is an "
            "AttributeError raised after the write has already landed. Give "
            "the action a measured surface, or declare the outcome "
            "unverifiable on its spec and say why."
        )
    if spec.action == "update_profile_field":
        # THE BEST-VERIFIED WRITE IN THIS PACKAGE, and that is worth saying
        # plainly because almost nothing else here can say it. publish_post
        # ships with its outcome DECLARED unverifiable; apply_job can only
        # establish that it did NOT happen; send_message is the same. This one
        # can read the field back and see the value it asked for.
        #
        # IT IS A FRESH READ OF THE SAME SURFACE, NOT A SECOND ONE. The editor
        # is the only place this value lives. What that buys is freshness --
        # the value as the page holds it now, after the write -- and saying so
        # is the difference between evidence and the appearance of it.
        wanted, _, requested = grant.target.partition(TARGET_JOIN)
        wanted = wanted.strip()
        current, why = await _editor_value_of(page, wanted)
        if current is None:
            return (UNKNOWN, why, "")
        if current == requested:
            return (
                "field_changed",
                f"{wanted!r} now reads back as the value this write asked "
                f"for. {why}",
                "",
            )
        if prior_value is not None and current == prior_value:
            return (
                "value_unchanged",
                f"{wanted!r} still holds exactly what it held before this "
                f"write, so nothing was changed. {why}",
                "",
            )
        # NEITHER THE REQUESTED VALUE NOR THE OLD ONE. Reported as unknown
        # rather than guessed at: LinkedIn may normalise what it stores, and a
        # gate that called a normalised value a failure would be wrong in the
        # direction that makes him undo a change that worked.
        return (
            UNKNOWN,
            f"{wanted!r} reads back as neither the requested value nor the "
            f"previous one. LinkedIn may have normalised it, or something "
            f"else may have changed it. {why} The exact strings are in this "
            "block for you to compare.",
            "",
        )

    if spec.action == "react_to_item":
        # A FRESH NAVIGATION AND A RE-READ OF THE CONTROL. Not an independent
        # surface -- there is only one page that carries this item's reaction
        # state -- so this is a fresh RENDER from LinkedIn rather than a
        # second source, and it says so instead of implying otherwise.
        #
        # THIS BRANCH CAN RETURN ``to_state``, which is the property
        # tests/test_unverifiable_outcomes.py exists to enforce and the one
        # apply_job lacked. ``to_state`` is "reacted" and the reading below
        # produces exactly that when the control is present and has stopped
        # wearing the OFF label.
        #
        # WHAT IT STILL CANNOT SAY IS **WHICH** REACTION, because the ON label
        # has never been observed. That is not a defect in this check -- the
        # check answers whether, and answers it honestly -- so it lives in
        # ``residue``, which the gate prints as what stays unknown even given
        # the verdict.
        landed = await _load(
            navigator,
            page,
            spec.url_template.format(target=grant.target),
            surface="the item permalink",
        )
        reading = await dom.read_reaction_surface(page)
        controls = int(reading.get("controls") or 0)
        off = int(reading.get("off_state") or 0)
        if controls != 1:
            return (
                UNKNOWN,
                f"{controls} reaction control(s) rendered on the re-read, "
                "where the permalink is measured to draw exactly one. An "
                "absent control is a page that had not arrived, NOT a "
                "reaction: reporting it as either outcome would be reading a "
                "half-rendered page as a result.",
                landed,
            )
        if off == 0:
            return (
                "reacted",
                "the one reaction control on this permalink has stopped "
                f"wearing {dom.REACTION_OFF_LABEL!r}. LinkedIn writes the "
                "toggle state into that name, so a control that is present "
                "and no longer says 'no reaction' is the strongest statement "
                "this surface makes. WHICH reaction it now carries is not "
                "readable -- the ON label has never been observed -- so this "
                "says that it moved and does not say what to.",
                landed,
            )
        return (
            "no_reaction",
            "the one reaction control still reads "
            f"{dom.REACTION_OFF_LABEL!r} after the click, so the reaction did "
            "not take effect.",
            landed,
        )

    if spec.action == "update_setting":
        # A FRESH NAVIGATION AND A RE-READ OF THE GROUP, which is the
        # strongest verification available to any action in this package and
        # is worth saying plainly rather than leaving to be inferred.
        #
        # The save pair is confirmed from a DIFFERENT surface, which is the
        # ideal shape and costs a second load of a list that renders part of
        # itself. This is confirmed from the SAME surface -- there is only one
        # -- but from a fresh render by LinkedIn, and what it reads is not a
        # label the control chose to draw: it is the browser's own ``checked``
        # property on a group of three, where exactly one being on is a
        # structural fact rather than a string. A control that redrew itself
        # wrongly would have to also report itself checked to fool this, and
        # the other two would have to report themselves unchecked.
        #
        # AND IT REUSES ``_read_dark_mode``'s REFUSALS. Zero checked or two
        # checked comes back ``unknown`` here exactly as it does at preview,
        # so a group that stopped behaving as radios after the click is
        # reported as unknown rather than resolved by position.
        landed = await _load(
            navigator, page, DARK_MODE_URL, surface="settings"
        )
        _facts, state, why = await _read_dark_mode(page, spec)
        return state, why, landed

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

    if spec.action == "apply_job":
        # THE TAB THAT CARRIES THE ANSWER, and until 2026-08-31 this fell
        # through to the SAVED read below.
        #
        # THAT WAS NOT A WRONG STRING, IT WAS A CHECK THAT COULD NOT PASS.
        # ``to_state`` is ``"applied"`` and the saved read returns ``saved`` /
        # ``not_saved`` / ``unknown``, so ``verified_state == "applied"`` was
        # FALSE on every reading it could ever take -- every apply this server
        # performs was going to report ``performed: "unknown"``. Measured on a
        # live apply: it reported the posting is still in his Saved list,
        # which was true and is not evidence about an application.
        #
        # A DIFFERENT SURFACE FROM THE ONE CLICKED, which is the ideal shape
        # and the one the save pair already has: the click happens on the
        # posting and the confirmation comes off the tracker, with LinkedIn's
        # own per-tab count reconciling it.
        landed = await _load(
            navigator, page, APPLIED_LIST_URL, surface="applied jobs"
        )
        state, why = await _read_applied_state(
            page, grant.target, navigator=navigator
        )
        return state, why, landed

    if spec.action == "send_message":
        # THE BRANCH THAT PROVES IT DID **NOT** HAPPEN, and cannot prove that
        # it did. That asymmetry is the design and it is stated rather than
        # worked around.
        #
        # WHY NOT ``unverifiable``. That declaration short-circuits this
        # function to UNKNOWN before any comparison runs -- correct for
        # ``publish_post``, where nothing can answer -- and here it would
        # DELETE the answer this action does have while keeping the flag that
        # says there is none. ``not_performed_state`` exists precisely so an
        # action that cannot prove the positive can still prove the negative,
        # which is how ``apply_job`` stopped reporting "unknown" on every run.
        #
        # AND THE READ COSTS NOTHING. ``from_state`` says the composer is
        # unmeasured because the PREVIEW's gate must not open messaging; by
        # the time this runs the composer is already open in front of us, so
        # re-reading it spends nobody's thread. That asymmetry is why one
        # field says "unmeasured" and this one names what it expects to find.
        reading = await dom.read_compose_send_state(page)
        if reading.get("error"):
            return (
                UNKNOWN,
                "the composer could not be re-read after the attempt, so this "
                f"says nothing about whether anything was sent: {reading['error']}",
                "",
            )
        boxes = int(reading.get("textboxes") or 0)
        if boxes != 1:
            return (
                UNKNOWN,
                f"{boxes} div[role=textbox] on the re-read, where the "
                "composer draws exactly one. An absent body is a page that "
                "changed, NOT evidence that a message left -- reporting it as "
                "either outcome would be reading a half-rendered page as a "
                "result.",
                "",
            )
        if reading.get("enabled") is True:
            return (
                "composer_holds_text",
                "the composer is still on screen with Send still ENABLED, "
                "which on this surface is what a composer holding its "
                "content looks like. NOTHING WAS DISPATCHED. That is the "
                "strongest statement this action can make, and it is the "
                "negative one: this server can show that a message did not "
                "go, and cannot show that one did.",
                "",
            )
        return (
            UNKNOWN,
            "the composer no longer has Send enabled. This server will NOT "
            "read that as 'sent': a cleared composer and a composer that "
            "never received the text look identical from here, and the only "
            "surface that could tell them apart is the thread -- which is "
            "forbidden AND costs a read receipt on a real person. Open your "
            "messages and look.",
            "",
        )

    if spec.action in ("save_job", "unsave_job"):
        landed = await _load(navigator, page, SAVED_LIST_URL, surface="saved jobs")
        state, why = await _read_saved_state(page, grant.target)
        return state, why, landed

    if spec.action != "unfollow_company":
        # NO CATCH-ALL. THIS LINE USED TO READ THE SAVED TAB FOR EVERY ACTION
        # THAT WAS NOT AN UNFOLLOW, and that is precisely how apply_job spent
        # months comparing "applied" against a reader that could only ever say
        # saved / not_saved / unknown. The fallthrough was invisible because
        # falling through LOOKED like being handled.
        #
        # An action that reaches here now is one somebody made performable
        # without giving it either a branch or an ``unverifiable``
        # declaration, and it RAISES rather than borrowing somebody else's
        # reader. The raise is the point: a loud failure on an action nobody
        # finished is strictly better than a quiet verification that cannot
        # pass, because the quiet one gets read as evidence.
        #
        # tests/test_unverifiable_outcomes.py asserts the pairing statically
        # so this raise should be unreachable; it exists because "should be
        # unreachable" is what the last fallthrough was too.
        raise WriteAttemptError(
            f"{spec.action!r} is performable but _verify_after has no branch "
            "for it and its spec declares no `unverifiable`. Refusing to "
            "verify it with another action's reader -- that is the defect "
            "apply_job carried until 2026-08-31. Give it a branch, or declare "
            "the outcome unverifiable and say why."
        )

    if spec.action == "unfollow_company":
        # AN EXPLICIT POSITIVE BRANCH, 2026-09-01. This body used to be
        # reached by FALLING PAST a negative test, which made it invisible
        # to any check asking "which actions does _verify_after handle?" --
        # and that question is the one that would have caught apply_job.
        # Being handled and being seen to be handled are different things,
        # and only the second one survives somebody adding a seventh write.
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

    # THE TWO GUARDS ABOVE AGREE, AND THIS ASSERTS THAT THEY DO. The negative
    # test raises for every action that is not ``unfollow_company``, so the
    # positive block below it always runs -- but they are two separate ``if``
    # statements, so nothing checks that the pair stays exhaustive. Without
    # this, the declared ``tuple[str, str, str]`` is a lie on a path a reader
    # can see: falling off the end returns None, and the caller unpacks it
    # somewhere far from where the mistake was made.
    #
    # NOT COLLAPSED INTO AN ``else``. The positive branch is written positively
    # on purpose -- being handled and being SEEN to be handled are different
    # things, and that distinction is what would have caught apply_job. So the
    # shape is kept and the gap is closed with a raise instead.
    raise WriteAttemptError(
        f"unreachable: {spec.action!r} passed the not-unfollow_company raise "
        "and then failed the is-unfollow_company test. The two guards in this "
        "function have stopped being exhaustive."
    )


#: THE ACTIONS THAT TYPE BEFORE THEY CLICK. Kept as a set rather than tested
#: by target_kind, because "has a text component" and "types it into the page"
#: are different claims -- ``update_setting``'s target has a value component
#: and that value is a RADIO DESTINATION, clicked and never typed.
TYPING_ACTIONS: frozenset[str] = frozenset(
    {"publish_post", "comment_on_item", "send_message"}
)


#: THE ACTIONS THAT TYPE **TWO** THINGS: a subject into one control and the
#: content into another. Only ``send_message``, and it is a set rather than a
#: test on ``target_kind`` for the same reason ``TYPING_ACTIONS`` is --
#: ``comment_on_item`` also has a two-part target and types only one half of
#: it, because the other half is an item urn that addresses the page.
#:
#: THE ORDER IS THE SAFETY PROPERTY. The SUBJECT is typed first and the
#: content is queued only if ``_recipient_gate`` confirms it, so his words are
#: never in a composer until the recipient has been checked against his own
#: needle. Appending on PROCEED rather than clearing on refuse is deliberate:
#: the default has to be "do not type", so that forgetting a branch fails
#: closed.
ADDRESSED_TYPING_ACTIONS: frozenset[str] = frozenset({"send_message"})


#: ACTIONS WHOSE SUBMIT CONTROL DOES NOT EXIST UNTIL THE FILL LANDS, so it
#: cannot be named in advance and must be identified by ARRIVAL.
#:
#: WHY THIS IS A SEPARATE SET FROM TYPING_ACTIONS. ``publish_post`` types too
#: and needs no delta: its submit is drawn from the start and merely DISABLED,
#: so the fill produces a state change on a control that was already there.
#: The comment surface draws a control named ``Comment`` that is ENABLED while
#: the box is empty -- so "present and enabled" is true before anything is
#: typed, and a gate keyed on it would press the FOCUS AFFORDANCE and return
#: something indistinguishable from success. One measured boolean separates
#: the two surfaces and it changes which instrument works.
DELTA_SUBMIT_ACTIONS: frozenset[str] = frozenset({"comment_on_item"})


async def _comment_submit_gate(
    page: Any, before: dict[str, int]
) -> dict[str, Any]:
    """THE DELTA GATE: identify the submit by the fact that it ARRIVED.

    A name is shared by two controls here and a position is not a property, so
    neither can identify the submit. What identifies it is that IT DID NOT
    EXIST until there was something to submit.

    THE RULE, and every branch of it refuses rather than guessing:

    * exactly ONE name that was absent before is present after -> that name is
      the submit, and the click is aimed at it;
    * a name's COUNT merely grew (``Comment`` 1 -> 2) -> REFUSED. Two controls
      share a name and only position separates them, which is the thing this
      package will not do;
    * nothing new, or several new -> REFUSED.

    IT IS EXPECTED TO REFUSE ON FIRST USE, and that is the design rather than a
    defect. His screenshot shows a blue button reading ``Comment`` beside an
    existing control named ``Comment``, which is the second branch. Nobody has
    MEASURED the submit's accessible name -- measuring it requires the fill,
    and the fill is the act this gate exists to authorise. So the refusal
    carries the observation, and the first supervised run is what settles it:
    exactly the shape ``unsave_job`` took when its ON label could not be
    observed until one write produced it.

    THE NEW NAME MUST ALSO BE SELECTOR-SAFE. ``read_comment_surface`` returns
    SHAPES, so a control whose label carried a member's name comes back with
    the identity substituted out -- and therefore unusable to build a selector
    from. That is the correct outcome: a control this server cannot name
    without naming a person is a control it does not press.
    """
    reading = await dom.read_comment_surface(page)
    out: dict[str, Any] = {
        "proceed": False,
        "selector": "",
        "observed": {
            "editors": reading.get("editors"),
            "controls_read": reading.get("controls_read"),
        },
        "why": "",
        "refused_condition": None,
        # WHAT ARRIVED, reported whether or not it is usable. This is the
        # measurement the first refusal exists to produce.
        "arrived": [],
        "grew": [],
    }
    if reading.get("error"):
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the permalink could not be read after the fill, so nothing is "
            f"known about what appeared: {reading['error']}"
        )
        return out
    if int(reading.get("editors") or 0) != 1:
        out["refused_condition"] = "1_editor_absent"
        out["why"] = (
            f"{reading.get('editors')} comment editor(s) after the fill, "
            "where exactly one is the shape measured. Zero means the page "
            "changed under the gate, not that the comment is ready."
        )
        return out

    after = dict(reading.get("names") or {})
    arrived = sorted(name for name in after if name not in before)
    grew = sorted(
        name
        for name, count in after.items()
        if name in before and count > before[name]
    )
    out["arrived"] = arrived
    out["grew"] = grew

    if len(arrived) != 1:
        out["refused_condition"] = (
            "2_nothing_arrived" if not arrived else "3_several_arrived"
        )
        out["why"] = (
            f"{len(arrived)} control name(s) appeared after the fill that were "
            f"not there before, where exactly one is aimable. Names whose "
            f"COUNT grew instead: {grew or 'none'}. A count growing means two "
            "controls now share one name -- most likely the submit wearing "
            f"the same name as the {dom.COMMENT_CONTROL_NAME!r} affordance "
            "already on the page -- and only position separates them, which "
            "is what this refuses. THIS IS THE MEASUREMENT: the submit's real "
            "accessible name has never been observed, and observing it needs "
            "the fill that just happened. Report these lists."
        )
        return out

    name = arrived[0]
    try:
        selector = dom.comment_submit_selector(name)
    except Exception as exc:  # noqa: BLE001 - a refusal, not a failure
        out["refused_condition"] = "4_name_not_selector_safe"
        out["why"] = (
            f"exactly one control arrived and its shaped name cannot build a "
            f"selector: {type(exc).__name__}. That happens when the name "
            "carried somebody's identity and was substituted out, which is "
            "the correct outcome -- a control this server cannot name without "
            "naming a person is one it does not press."
        )
        return out
    out["proceed"] = True
    out["selector"] = selector
    out["why"] = (
        f"exactly one control name appeared after the fill -- {name!r} -- "
        "that was not on the page before it. It is identified by ARRIVAL "
        "rather than by a name two controls share or a position that is not a "
        "property, and it is the first observation of this control anywhere."
    )
    return out


async def _publish_submit_gate(page: Any) -> dict[str, Any]:
    """THE GATE BETWEEN THE FILL AND THE CLICK, and the reason typing is safe.

    The fill puts text in the composer and publishes nothing. This decides
    whether the publish control may be pressed, by READING the composer that
    the fill just changed rather than assuming it now looks the way it did in
    a capture.

    WHY A TRANSITION IS THE EVIDENCE, and why this action has one when its
    nearest neighbour does not. ``Post`` is measured **disabled on an empty
    composer**, on three settle-agreeing readings. So a fill that worked
    produces something this server can SEE: the control becomes enabled. That
    is not an inference about what the fill did to LinkedIn -- it is a reading
    of the page after it.

    THE COMMENT SURFACE HAS NO SUCH TRANSITION, which is why this gate is not
    reusable there and why ``comment_on_item`` is not shipping on this
    machinery. Its control is named ``Comment`` and is measured ENABLED while
    the box is empty, count 1, on the same permalink. A gate asking "is a
    control named Comment present and enabled" is satisfied by the page
    BEFORE anything is typed, so it would press the focus affordance and
    produce something indistinguishable from success. Same family, opposite
    outcome, one measured boolean apart.

    FOUR CONDITIONS, all required:

    1. the editor is still there -- exactly one, so the fill landed somewhere
       this gate can account for;
    2. exactly one publish control is drawn;
    3. it is ENABLED, which on this surface means the composer has content;
    4. the read itself did not error.

    An abort here is cheap and the cost is stated rather than implied: the
    composer holds typed text that was never published, and whether LinkedIn
    saves that as a draft is UNMEASURED -- 17 candidate draft-listing
    addresses were run against the read boundary on 2026-08-31 and all 17 were
    refused, so there is no surface on which one could be found or removed.
    """
    reading = await dom.read_post_composer(page)
    out: dict[str, Any] = {
        "proceed": False,
        "selector": dom.post_submit_selector(),
        "observed": reading,
        "why": "",
        "refused_condition": None,
    }
    if reading.get("error"):
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the composer could not be read after the fill, so nothing is "
            f"known about whether it is ready to publish: {reading['error']}"
        )
        return out
    if int(reading.get("editors") or 0) != 1:
        out["refused_condition"] = "1_editor_absent"
        out["why"] = (
            f"{reading.get('editors')} post editor(s) are on the page after "
            "the fill, where exactly one is the shape this was measured on. "
            "Zero means the composer is gone, which is a page that changed "
            "under the gate rather than a composer declining to publish."
        )
        return out
    submits = int(reading.get("submits") or 0)
    if submits != 1:
        out["refused_condition"] = "2_no_submit_control"
        out["why"] = (
            f"{submits} publish control(s) named {dom.POST_SUBMIT_NAME!r} are "
            "drawn, where exactly one is required. More than one and pressing "
            "either would be picking by position."
        )
        return out
    if reading.get("submit_enabled") is not True:
        out["refused_condition"] = "3_submit_disabled"
        out["why"] = (
            "the publish control is drawn and NOT enabled after the fill. On "
            "this surface it is measured disabled while the composer is "
            "empty, so this reads as the text not having landed -- and a "
            "disabled control is not pressed to find out."
        )
        return out
    out["proceed"] = True
    out["why"] = (
        "the editor is present and the publish control went from the "
        "disabled state this surface draws when empty to enabled, which is "
        "the observable transition a fill produces here."
    )
    return out


async def _typeahead_gate(page: Any, grant: WriteGrant) -> dict[str, Any]:
    """THE GATE BETWEEN THE RECIPIENT FILL AND THE TYPEAHEAD CLICK.

    **THE MISSING STEP, MEASURED RATHER THAN ASSUMED.** On 2026-09-03 a
    supervised run typed a correct, first-degree name into an empty composer
    and ``_recipient_gate`` returned ``1_no_recipient_committed`` with all four
    chip selectors reading ZERO. That settles the question the recipient gate
    was shipped to ask: **a bare fill does not commit a recipient.** Typing
    into a typeahead is not choosing from it, and this gate is the choosing.

    **IT CLICKS A CONTROL DRAWN FROM SOMEBODY'S NAME, WHICH IS A NEW CLASS.**
    Every other click this package makes targets UI furniture -- ``Save the
    job``, ``Send``, a filter pill. A suggestion row exists BECAUSE LinkedIn
    matched a person, so the design has to hold that rather than route around
    it. Two properties do the holding, and both are the recipient gate's own,
    reused one step earlier:

    * **Exactly one, or refuse.** Zero refuses, two refuse, and a row whose
      name does not carry his needle refuses. It never falls back to the first
      row -- picking from a dropdown of three same-named people by position is
      verbatim the ``aim_invitation`` failure, on the action whose audience is
      the least recoverable in this package.
    * **The comparison runs in the page.** Playwright's ``name=`` matches the
      accessible name inside the browser and hands back a COUNT. No
      suggestion's label, id or urn enters this process, so there is nothing
      here for a traceback or a log line to publish.

    **AND THE CLICK IS NOT ITS OWN EVIDENCE.** This gate says a uniquely-named
    suggestion exists and may be pressed. It does NOT say a recipient was
    committed -- ``_recipient_gate`` still runs afterwards, unchanged, and
    remains the only thing that authorises his words to be typed. A gate that
    both performed an act and certified it would be reading its own homework,
    which is the defect ``apply_job`` spent months inside.

    **IT MAY STILL REFUSE AFTER A SUCCESSFUL CLICK**, and that is correct
    rather than wasteful: the cost is a name sitting in his composer, which is
    what the recipient gate's ordering already buys, and it is the only way to
    learn whether clicking a suggestion is what commits one.
    """
    needle = _subject_component_of(spec_for_action(grant.action), grant.target)
    out: dict[str, Any] = {
        "proceed": False,
        "observed": {},
        "why": "",
        "refused_condition": None,
        "selector": None,
    }
    try:
        reading = await dom.read_typeahead_options(page, needle)
    except Exception as exc:  # noqa: BLE001 - reported, never raised
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the typeahead could not be read after the name was typed, so "
            "nothing is known about what it offered: "
            f"{type(exc).__name__}: {exc}"
        )
        return out

    out["observed"] = {
        "appeared": reading.get("appeared"),
        "per_selector": reading.get("per_selector"),
        "total": reading.get("total"),
        "matches": reading.get("matches"),
        "selectors_tried": list(dom.TYPEAHEAD_OPTION_SELECTORS),
        # HOW MANY ROWS EACH CANDIDATE MATCHER WOULD MATCH, added 2026-09-03
        # after a live run returned ten options and ten matches. That reading
        # is the substring matcher counting LinkedIn's own result set -- a
        # typeahead returns a row BECAUSE it matched what was typed -- so the
        # shipped discriminator cannot discriminate, and these counts are what
        # says which one could. Integers only; no accessible name is read.
        "pattern_census": reading.get("pattern_census"),
        "what_the_census_is": (
            "how many suggestion rows each CANDIDATE matcher would match, "
            "counted in the page. It is a measurement and not a choice: the "
            "aim is still 'substring', and which matcher presses is a "
            "decision that waits on these numbers rather than being taken by "
            "them."
        ),
    }
    if reading.get("error"):
        out["refused_condition"] = "0_selector_unbuildable"
        out["why"] = str(reading["error"])
        return out

    total = int(reading.get("total") or 0)
    matches = int(reading.get("matches") or 0)

    # THE LISTBOX AND THE OPTIONS ARE ASKED ABOUT SEPARATELY, because "it never
    # opened" and "it opened empty" are different facts about LinkedIn and only
    # the second one says anything about whether he has this connection.
    if not reading.get("appeared"):
        out["refused_condition"] = "1_no_listbox"
        # WHAT THIS BRANCH MAY AND MAY NOT ASSERT. It knows one thing: no
        # element matching the WRAPPER selector attached inside the wait. It
        # said "there was nothing to choose from", which is a claim about the
        # OPTIONS -- and the option counts are taken afterwards and may be
        # non-zero, because a page can draw rows without the wrapper this
        # reader waits on. A refusal that states something it did not check is
        # the defect this repository spends most of its time removing, so the
        # sentence is built from what was counted.
        out["why"] = (
            f"no element matching {dom.TYPEAHEAD_LISTBOX_SELECTOR!r} attached "
            f"within the bounded wait, and {total} option(s) were counted "
            "afterwards. Nothing was clicked. THIS IS A FACT ABOUT THIS "
            "READER AND THIS PAGE TOGETHER, not about the person you named. "
            + (
                "AND THE OPTION COUNT IS NOT ZERO, so rows ARE drawn here and "
                "it is the WRAPPER that is missing -- which makes this a "
                "finding about the wait rather than about the dropdown, and "
                "is exactly why this refusal does not tell you the list was "
                "empty."
                if total
                else "Every candidate selector counted zero as well, so "
                "either the dropdown did not open, or it uses none of the "
                "spellings this server knows -- and the per-selector counts "
                "above are how a human tells those two apart."
            )
            # THE CLOSING SENTENCE IS VERBATIM WHAT IT WAS, and that is
            # deliberate rather than incidental: a refusal on this branch
            # must not be readable as "he is not on LinkedIn", and
            # tests/test_typeahead_gate.py pins the exact words. Rewriting
            # the sentence around it is a correction; rewriting the
            # sentence itself would delete a promise somebody is relying on.
            + " Neither of them is a statement that the person you named "
            "is not reachable."
        )
        return out
    if total == 0:
        out["refused_condition"] = "2_no_options"
        out["why"] = (
            "the listbox drew ZERO suggestions for the name you supplied. "
            "Nothing was clicked and nothing was typed into the body."
        )
        return out
    if matches == 0:
        out["refused_condition"] = "3_no_option_carries_the_needle"
        out["why"] = (
            f"the listbox drew {total} suggestion(s) and NOT ONE of them "
            "carries the name you supplied -- the comparison ran inside the "
            "page and returned zero matches. Refused, and the labels are not "
            "reported here, because they are other people's names and this "
            "server does not read one to explain itself."
        )
        return out
    if matches > 1:
        out["refused_condition"] = "4_several_options_match"
        # THE ADVICE THAT USED TO BE HERE COULD NOT WORK, and it was removed
        # on 2026-09-03 rather than softened. It said "supply a name that
        # distinguishes them". A typeahead returns a row BECAUSE it matched
        # what was typed, so a longer needle narrows LinkedIn's RESULT SET
        # while every row in it still contains the needle -- the ratio does
        # not move, and the live run that measured ten of ten is the expected
        # shape rather than an unlucky one. Telling him to try harder at
        # something that cannot help is worse than telling him nothing.
        census = dict(reading.get("pattern_census") or {})
        strictest = census.get(dom.TYPEAHEAD_STRICTEST_PATTERN)
        if strictest is None or strictest < 0:
            verdict = (
                "The per-pattern census could not be taken, so this refusal "
                "cannot say whether any stricter matcher would separate them."
            )
        elif strictest == 1:
            verdict = (
                f"AND ONE CANDIDATE DOES SEPARATE THEM: "
                f"{dom.TYPEAHEAD_STRICTEST_PATTERN!r} matches exactly one of "
                "these rows. This gate is not aiming by it -- the aim is "
                "still the substring, and which matcher presses is a decision "
                "that waits on this measurement rather than being taken by it."
            )
        elif strictest == 0:
            verdict = (
                f"AND EVERY STRICTER CANDIDATE MATCHES NOTHING: "
                f"{dom.TYPEAHEAD_STRICTEST_PATTERN!r} counted zero. That says "
                "these rows do not BEGIN with the name you supplied -- so the "
                "name sits somewhere else in the row, and a matcher anchored "
                "at the start would refuse everybody rather than refuse "
                "correctly."
            )
        else:
            verdict = (
                f"AND THE ROWS ARE NOT SEPARABLE BY THE NAME YOU GAVE: the "
                f"strictest candidate, {dom.TYPEAHEAD_STRICTEST_PATTERN!r}, "
                f"still matches {strictest}. Your name is a PREFIX of more "
                "than one of these people, and if it is somebody's whole "
                "display name then there is no longer name to give. This is "
                "the case no matcher fixes, and it is named rather than "
                "papered over: what is ambiguous is the NAME, not the reading."
            )
        out["why"] = (
            f"{matches} of the {total} suggestion(s) carry the name you "
            "supplied. This action reaches ONE person; choosing among several "
            "rows that all match would be choosing by position, which is the "
            "one thing this gate exists to refuse. " + verdict + " The "
            "per-pattern counts are in 'observed' and they are the "
            "measurement nobody can take another way -- reading the live "
            "shape directly would mean reading other people's names."
        )
        return out

    out["proceed"] = True
    out["selector"] = reading["selector"]
    out["why"] = (
        f"exactly one of the {total} suggestion(s) carries the name you "
        "supplied, matched on its ACCESSIBLE NAME inside the page rather than "
        "by position, so no label entered this process. That row may be "
        "pressed. It does NOT mean a recipient is committed -- the recipient "
        "gate runs after the click and remains the only thing that lets your "
        "message be typed."
    )
    return out


async def _recipient_gate(page: Any, grant: WriteGrant) -> dict[str, Any]:
    """THE GATE BETWEEN THE RECIPIENT FILL AND THE BODY FILL.

    **WHAT MAKES THIS SAFE IS THE NAME MATCH, NOT THE COUNT.** A count of one
    says LinkedIn has committed a recipient; it does not say the recipient is
    the person he named. Those are different claims and only the second one
    matters when the thing being sent reaches a named individual. So this
    requires EXACTLY ONE committed recipient WHOSE ACCESSIBLE NAME CARRIES HIS
    OWN NEEDLE, compared inside the page, with only integers coming back.

    WHY THE BRIEFED DESIGN WAS NOT ENOUGH. The obvious gate is the one
    ``publish_post`` uses: fill both fields, then check that ``Send`` became
    enabled. That answers "does LinkedIn think this is sendable" and nothing
    else -- and if the typeahead commits anything on the blur that the SECOND
    fill causes, the gate's own evidence is satisfied by exactly the thing
    that is wrong, and the message reaches whoever LinkedIn drew first. That
    is verbatim the failure ``aim_invitation`` exists to refuse, on the action
    this package's own spec calls the most irreversible in audience.

    THE ORDERING IS THE SAFETY PROPERTY. This runs after the RECIPIENT fill
    and before the BODY fill, so **his words are never typed until a recipient
    has been confirmed against his needle.** A refusal here costs him a typed
    name sitting in a composer; the alternative ordering costs him his message
    in a composer, or worse, sent.

    IT IS EXPECTED TO REFUSE ON FIRST USE, and that is the design rather than
    a defect. Nobody has ever typed into that combobox through this server, so
    nobody knows whether a bare fill commits a recipient at all -- and the
    selectors that would find a committed one have never matched anything, on
    any page, on either branch of the only test that covers them. **The
    counts this refusal returns ARE the measurement**, and there is no way to
    take it that does not involve typing into the box. Exactly the shape
    ``comment_on_item`` shipped in, and ``unsave_job`` before it.

    IT FAILS CLOSED, which is what makes shipping it honest. An unvalidated
    selector that matches nothing reads zero and REFUSES. A selector that
    matches a chip carrying the wrong name reads zero MATCHES and refuses. The
    only way through is a chip that both exists and carries his needle.
    """
    needle = _subject_component_of(spec_for_action(grant.action), grant.target)
    out: dict[str, Any] = {
        "proceed": False,
        "observed": {},
        "why": "",
        "refused_condition": None,
    }
    try:
        reading = await dom.read_selected_recipients(page, needle)
    except Exception as exc:  # noqa: BLE001 - reported, never raised
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the composer could not be read after the recipient was typed, so "
            f"nothing is known about who is in it: {type(exc).__name__}: {exc}"
        )
        return out

    # THE COUNTS ARE THE POINT OF THIS BLOCK. Per-selector, so a refusal says
    # WHICH candidate matched and which found nothing -- the difference
    # between "there is nobody here" and "my selector is wrong", which on this
    # surface are the difference between refusing and sending.
    out["observed"] = {
        "per_selector": reading.get("per_selector"),
        "total": reading.get("total"),
        "matches": reading.get("matches"),
        "selectors_tried": list(dom.RECIPIENT_CHIP_SELECTORS),
    }
    total = int(reading.get("total") or 0)
    matches = int(reading.get("matches") or 0)

    if total == 0:
        out["refused_condition"] = "1_no_recipient_committed"
        out["why"] = (
            "NO COMMITTED RECIPIENT WAS FOUND BY ANY CANDIDATE SELECTOR after "
            "the name was typed, so nothing was typed into the body and "
            "nothing was sent. THIS IS THE EXPECTED FIRST RESULT AND IT IS "
            "THE MEASUREMENT: typing into a typeahead is not the same as "
            "choosing from it, and whether a bare fill commits a recipient on "
            "this surface has never been observed. The per-selector counts "
            "above are what nobody could obtain any other way -- a zero from "
            "every candidate means either that the fill committed nobody, or "
            "that none of these selectors is how LinkedIn draws a committed "
            "recipient, and those two need a human looking at the screen to "
            "tell apart."
        )
        return out
    if total > 1:
        out["refused_condition"] = "2_several_recipients"
        out["why"] = (
            f"{total} committed recipients are in this composer. This action "
            "sends to one person named by you; a composer holding several is "
            "not a state this gate acts from, and choosing among them would "
            "be choosing by position."
        )
        return out
    if matches != 1:
        out["refused_condition"] = "3_needle_does_not_match"
        out["why"] = (
            "exactly one recipient is committed and it does NOT carry the "
            "name you supplied -- the comparison ran inside the page and "
            f"returned {matches} match(es). THE COUNT IS NOT THE PROPERTY: a "
            "committed recipient means LinkedIn thinks this is sendable, and "
            "only the name match means it is sendable TO THE PERSON YOU "
            "NAMED. Refused, and the label is not reported here, because it "
            "is somebody's name and this server does not read one to explain "
            "itself."
        )
        return out

    out["proceed"] = True
    out["why"] = (
        "exactly one recipient is committed and its accessible name carries "
        "the needle you supplied, compared INSIDE the page so no name entered "
        "this process. That is the property this gate exists for -- not that "
        "the composer looks sendable, but that it is addressed to the person "
        "you named. The body may now be typed."
    )
    return out


async def _send_gate(page: Any) -> dict[str, Any]:
    """THE GATE BETWEEN THE BODY FILL AND THE SEND CLICK.

    The same measured transition ``publish_post``'s gate rests on: ``Send`` is
    drawn DISABLED on an empty composer, so a fill that landed produces
    something this server can SEE rather than an inference about what the fill
    did.

    IT IS THE SECOND GATE AND NOT THE ONLY ONE. Reaching it means a recipient
    was already confirmed against his needle, which is the claim this gate
    cannot make and does not pretend to: all it adds is that the body landed.
    """
    reading = await dom.read_compose_send_state(page)
    out: dict[str, Any] = {
        "proceed": False,
        "selector": dom.compose_send_selector(),
        "observed": reading,
        "why": "",
        "refused_condition": None,
    }
    if reading.get("error"):
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the composer could not be read after the body was typed, so "
            f"nothing is known about whether it is ready: {reading['error']}"
        )
        return out
    if int(reading.get("textboxes") or 0) != 1:
        out["refused_condition"] = "1_body_absent"
        out["why"] = (
            f"{reading.get('textboxes')} div[role=textbox] after the fill, "
            "where exactly one is the shape measured. Zero means the composer "
            "is gone -- a page that changed under the gate, not a composer "
            "declining to send."
        )
        return out
    if int(reading.get("controls") or 0) != 1:
        out["refused_condition"] = "2_no_send_control"
        out["why"] = (
            f"{reading.get('controls')} control(s) named "
            f"{dom.MESSAGE_SEND_NAME!r} are drawn, where exactly one is "
            "required."
        )
        return out
    if reading.get("enabled") is not True:
        out["refused_condition"] = "3_send_disabled"
        out["why"] = (
            "the Send control is drawn and NOT enabled after the body was "
            "typed. On this surface it is measured disabled while the "
            "composer is empty, so this reads as the text not having landed "
            "-- and a disabled control is not pressed to find out."
        )
        return out
    out["proceed"] = True
    out["why"] = (
        "the body is present and Send went from the disabled state this "
        "surface draws when empty to enabled, which is the observable "
        "transition a fill produces here."
    )
    return out


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
        # WHICH OF THE FIVE REFUSED, as a code rather than only as prose.
        # ``None`` on the proceed path.
        #
        # ADDED 2026-08-31, AFTER AN APPLY WAS PERFORMED LIVE AND STOPPED
        # HERE. The gate held, on an irreversible action, on a real posting
        # with a real employer at the other end -- that is the design working.
        # What it could not do is say WHICH condition stopped it: this dict
        # was assigned inside ``perform`` and never read again, so every
        # sentence below reached nobody.
        #
        # It is the same defect this package has fixed three times elsewhere
        # -- ``save_job``'s refusal that would not say what it saw,
        # ``_read_tracker`` discarding its own counts, ``parse_job_card``'s
        # two indistinguishable ``None``s -- and APPLY IS WHERE IT MATTERS
        # MOST, because the caller cannot re-run to learn more: a retry on an
        # action that may have half-landed is what the docstring forbids.
        "refused_condition": None,
    }
    if not modal.get("modal_present"):
        out["refused_condition"] = "1_modal_absent"
        out["why"] = (
            "the apply modal never rendered after the control was clicked, so "
            "nothing was submitted. This is the same non-hydration that makes "
            "postings read as having no apply control at all."
        )
        return out
    if not modal.get("submit_present"):
        out["refused_condition"] = "2_no_submit_control"
        out["why"] = modal.get("why") or (
            "the modal rendered but carries no submit control this reader "
            "recognises."
        )
        return out
    if not modal.get("advance_scan_complete"):
        out["refused_condition"] = "5_advance_scan_incomplete"
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
        out["refused_condition"] = "5_multi_step_flow"
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
        out["refused_condition"] = "3_submit_disabled"
        out["why"] = (
            "the submit control is present but disabled, which means the form "
            "wants something it has not got. What that something is has never "
            "been measured, and supplying it would be guessing at required "
            "fields on an irreversible action."
        )
        return out
    name = str(modal.get("submit_name") or "")
    if "submit" not in name.lower():
        out["refused_condition"] = "4_name_does_not_corroborate"
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


def typed_text_residue(
    spec: WriteSpec,
    *,
    fills_made: int,
    submit_clicks: int,
    click_error: Optional[str],
) -> Optional[dict[str, Any]]:
    """What is left IN HIS COMPOSER after a typing action, said out loud.

    ``submit_clicks`` IS NOT THE NUMBER OF CLICKS, and the rename is the
    fix rather than the decoration. This parameter was ``clicks_made`` and
    it was handed ``perform``'s raw click counter, which was sound while
    every click a typing action made WAS a submit. ``send_message`` broke
    that on 2026-09-03: it presses a TYPEAHEAD SUGGESTION between its two
    fills, and that click dispatches nothing. Fed the raw count, this
    function would have reported ``submit_was_pressed: True`` and
    ``left_in_the_composer: False`` on a run that pressed a name in a
    dropdown and then REFUSED at the recipient gate -- both false, on the
    action where a false receipt costs the most, and it would have told
    him there was nothing on his screen while his composer held somebody's
    name.

    So the caller subtracts, and the parameter is NAMED for the claim it
    makes. A click that is not a submit must not move the submit count,
    and a parameter called ``clicks_made`` invites the next caller to make
    the same substitution for the same reason.

    THE FAILURE THIS EXISTS FOR, found 2026-09-02. ``publish_post`` and
    ``comment_on_item`` FILL and then CLICK, and for a day and a half the
    click could not resolve at all -- so the text landed in his composer, the
    submit raised, ``perform`` caught it into ``click_error``, and the receipt
    reported a failure. It failed SAFE. **It did not fail CLEANLY.**

    A draft sitting in his UI that he did not put there is a side effect he
    did not consent to, even though nothing published. Nothing in the old
    receipt said the text was there; a reader saw an error and would
    reasonably conclude nothing had happened.

    IT IS NOT A CLEARING MUTATION AND MUST NOT BECOME ONE. The operator's
    ruling is to TELL HIM and let him decide. Clearing would mean a second
    write to undo a failed write, which is more machinery pointed at his
    account, taken on this server's own judgement, at exactly the moment this
    server has just demonstrated it cannot reliably press a button.

    ALWAYS PRESENT FOR A TYPING ACTION, never omitted on the happy path. An
    absent block would make "no text was left" and "nobody checked" the same
    answer, which is the absent-is-not-zero rule on the field where the wrong
    reading leaves his words on screen.
    """
    if spec.action not in TYPING_ACTIONS:
        return None
    if fills_made < 1:
        return {
            "text_was_entered": False,
            "left_in_the_composer": False,
            "what_to_do": (
                "Nothing was typed. The action stopped before the fill, so "
                "there is no draft to clear."
            ),
        }
    submitted = submit_clicks > 0
    return {
        "text_was_entered": True,
        # WHETHER THE SUBMIT WAS PRESSED, which is NOT whether it posted.
        # ``verification`` answers the second question and this one does not
        # pretend to.
        "submit_was_pressed": submitted,
        "left_in_the_composer": not submitted,
        "click_error": click_error,
        "what_to_do": (
            "THE TEXT WAS TYPED AND THE SUBMIT WAS NEVER PRESSED, so it is "
            "still sitting in the composer on LinkedIn where anyone using "
            "this browser would see it. Nothing was published. GO AND CLEAR "
            "IT YOURSELF if you do not want it there -- this server will not "
            "type again to undo a failed write, and it is telling you rather "
            "than deciding for you."
            if not submitted
            else
            "The text was typed and the submit WAS pressed. Whether it "
            "actually posted is a different question and is answered by "
            "'verification', not here."
        ),
    }


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

    VERIFICATION IS FROM A DIFFERENT SURFACE WHERE ONE EXISTS. The click
    happens on the posting; the confirmation is read off the tracker, because
    a control that redraws itself is the weakest possible witness to its own
    effect. WHICH TAB depends on the action, and this sentence named only one
    of them until 2026-08-31: the save pair is confirmed from
    ``?stage=saved`` and an APPLY from ``?stage=applied``. Apply fell through
    to the saved read, whose three answers do not include ``"applied"``, so
    the comparison could not pass and every apply this server performed was
    going to report ``"unknown"``. ``update_setting`` has no second surface at
    all and says so rather than implying one.

    Returns a block whose ``performed`` field has THREE values, not two:
    ``True``, ``False``, and ``"unknown"``. The third is for a click whose
    effect nobody could establish -- a verification read that raised, or a
    list too partial to settle it. IT IS NOT THE ANSWER FOR "it did not
    happen": that is ``False``, and an action whose "did not happen" state is
    not the state it was valid FROM names it in
    ``WriteSpec.not_performed_state``. Apply is the one that needs it, and it
    is the one where the distinction matters most, because the docstring
    forbids retrying to find out.
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

    anchor = anchor_label_for(spec, grant.target)
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
    # A STAR SO THE OTHER EIGHT ARMS NEED NO EDIT. Only the arm with a choice
    # to report returns a fourth element; everything else is a click, which is
    # what this defaults to.
    live_state, live_why, selector, *live_kind = await _live_control(
        page, spec, grant, anchor
    )
    control_kind = live_kind[0] if live_kind else "click"
    # THE ORIGIN CHECK GOES THROUGH ``valid_from`` NOW, and that is what makes
    # a multi-state action performable at all. It was ``live_state !=
    # spec.from_state``, which for an action whose ``from_state`` is ``None``
    # -- there is no single origin -- refuses EVERY reading it could ever
    # take. That is not a gate refusing something; it is a gate that cannot
    # pass, and it was invisible while no such action was in PERFORMABLE.
    origin_ok, origin_why = valid_from(spec, live_state, grant.target)
    if not origin_ok or not selector:
        raise WriteAttemptError(
            f"refusing to click: {origin_why or 'no selector was built.'} "
            f"{live_why} "
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
    # HOW MANY OF THOSE CLICKS SUBMITTED NOTHING, counted separately
    # because the two numbers stopped being the same one on 2026-09-03.
    # It is INCREMENTED WHERE THE CLICK IS RECOGNISED rather than derived
    # afterwards from the action and the count: a derivation would have to
    # re-decide which click this was, and that decision already exists
    # twenty lines below. See ``typed_text_residue``.
    typeahead_clicks = 0
    fills_made = 0
    apply_gate: Optional[dict[str, Any]] = None
    publish_gate: Optional[dict[str, Any]] = None
    recipient_gate: Optional[dict[str, Any]] = None
    typeahead_gate: Optional[dict[str, Any]] = None
    send_gate: Optional[dict[str, Any]] = None

    # THE TYPING PLAN, and it is a QUEUE FOR THE SAME REASON THE CLICK PLAN IS.
    #
    # readonly.SANCTIONED_MUTATIONS is keyed by (path, function, kind) and the
    # scanner counts CALL SITES, so draining a queue keeps the guarantee that
    # list exists to give: there is ONE place in this package that types, and a
    # reviewer reads it. A second literal page.fill anywhere would be a second
    # place to audit and a second entry to justify.
    #
    # THE TEXT IS NEVER COMPOSED HERE. It comes out of the GRANT, which is the
    # canonical target the preview printed and the token was minted against --
    # so the bytes typed are the bytes he read, and consume() already refused
    # any token whose target did not match. That is the operator's "exact text
    # verbatim in the preview" condition enforced by construction rather than
    # by care, and tests/test_typed_bytes.py asserts the identity.
    fill_plan: list[tuple[str, str]] = []
    # THE THIRD MUTATION KIND, 2026-09-02. A profile field is either typed into
    # or CHOSEN FROM, and which one is a property of the CONTROL rather than of
    # the action -- ``City`` is an input and ``Country/Region`` is a select, in
    # the same editor, behind the same tool.
    #
    # STILL EXACTLY ONE ``fill_plan.append``, and that is deliberate rather
    # than tidy. ``test_the_fill_types_the_grants_own_text_and_nothing_else``
    # asserts on the AST that this module has ONE fill site, so that the string
    # typed is provably a slice of the very target the token was minted
    # against. A second append would have satisfied the same behaviour while
    # dissolving that proof, so the branch chooses a PLAN and the append
    # happens once.
    select_plan: list[tuple[str, str]] = []
    if control_kind == "select_option":
        select_plan.append((selector, _text_component_of(spec, grant.target)))
    elif spec.action in ADDRESSED_TYPING_ACTIONS:
        # THE SUBJECT ONLY. The content is appended by ``_recipient_gate``
        # inside the loop, and ONLY if that gate confirms a committed
        # recipient carrying his own needle -- so the queue starts one entry
        # long and grows only on evidence. See ADDRESSED_TYPING_ACTIONS for
        # why appending on proceed beats clearing on refuse.
        fill_plan.append((selector, _subject_component_of(spec, grant.target)))
    elif spec.action in TYPING_ACTIONS or control_kind == "fill":
        fill_plan.append((selector, _text_component_of(spec, grant.target)))
    click_plan: list[str] = (
        [] if (fill_plan or select_plan) else [selector]
    )

    # THE BEFORE-READING FOR A DELTA ACTION, taken here because it must happen
    # BEFORE the fill and nowhere else. It is a READ -- a census of shaped
    # control names -- so it adds no mutation and no call site.
    comment_gate: Optional[dict[str, Any]] = None
    before_names: dict[str, int] = {}
    if spec.action in DELTA_SUBMIT_ACTIONS:
        before_names = dict(
            (await dom.read_comment_surface(page)).get("names") or {}
        )

    # THE PRIOR VALUE, READ BEFORE ANYTHING IS TYPED and on a page already
    # open. It is the whole of the restore path: this server will not put a
    # value back, so the ONE thing it owes him is the exact string it is about
    # to overwrite, verbatim, while it still exists to be read.
    #
    # A READ, ON THE SAME PAGE, THROUGH A DECLARED SCRIPT. No navigation, no
    # new waiver, and it happens here rather than in the preview because the
    # preview reads his profile and the value lives in the editor.
    prior_value: Optional[str] = None
    prior_why = ""
    if spec.action == "update_profile_field":
        prior_field, _, _ = grant.target.partition(TARGET_JOIN)
        prior_value, prior_why = await _editor_value_of(page, prior_field.strip())

    selects_made = 0
    try:
        while select_plan:
            select_selector, select_text = select_plan.pop(0)
            # BY THE OPTION'S OWN LABEL, never by value and never by index.
            # ``label=`` matches the text the page itself renders, which is the
            # same string the value reader observed and the same one the
            # preview printed. An index would be position-aiming; ``value=``
            # would be a submission token the page chose, and neither is the
            # thing he agreed to.
            await page.select_option(
                select_selector, label=select_text, timeout=CLICK_TIMEOUT_MS
            )
            selects_made += 1
        # ONE LOOP OVER TWO QUEUES, AND CLICKS DRAIN FIRST.
        #
        # THIS WAS TWO SEQUENTIAL LOOPS -- every fill, then every click -- and
        # ``send_message`` cannot be expressed that way. Its order is fill the
        # recipient, CLICK a suggestion, then fill the body: a click BETWEEN
        # two fills, which a fills-then-clicks structure cannot produce.
        #
        # THE ALTERNATIVE WAS A SECOND ``page.click`` CALL SITE, AND IT WAS
        # REFUSED. ``readonly.SANCTIONED_MUTATIONS`` grants
        # ``(writes.py, perform, click)`` once, and the boundary is policed by
        # COUNTED LITERAL CALL SITES, not by the triple -- a second literal
        # ``.click(`` here fails ``test_the_package_contains_exactly_as_many_
        # mutating_calls_as_are_listed`` and its writes.py twin, and the suite
        # already carries ``test_a_second_click_inside_perform_is_still_caught``
        # as the shown-failing control for exactly this. So the typeahead click
        # drains the SAME queue through the SAME call site that apply's second
        # click, the comment submit, the publish submit and the send all
        # already use. **No new exemption is bought, and none is needed.**
        #
        # NOTHING ELSE REORDERS. ``click_plan`` starts non-empty only when
        # there is no fill and no select to do (see its construction above), so
        # for every other action the queues are never both loaded and
        # click-first is the same sequence it always was.
        while fill_plan or click_plan:
            if click_plan:
                await page.click(click_plan.pop(0), timeout=CLICK_TIMEOUT_MS)
                clicks_made += 1
                if spec.action in TWO_CLICK_ACTIONS and clicks_made == 1:
                    apply_gate = await _apply_submit_gate(page)
                    if apply_gate["proceed"]:
                        click_plan.append(apply_gate["selector"])
                elif spec.action in ADDRESSED_TYPING_ACTIONS and clicks_made == 1:
                    # THE TYPEAHEAD CLICK JUST LANDED, AND IT PROVES NOTHING.
                    # The recipient gate runs here, unchanged, and is still the
                    # only thing that appends his message to the queue. The
                    # click is how a recipient gets committed; this is what
                    # says one did.
                    #
                    # AND IT DISPATCHED NOTHING, so it is recorded as a click
                    # that is not a submit. This is the only branch that knows
                    # which click this was, which is why the counter moves here
                    # and is not reconstructed later from the action name.
                    typeahead_clicks += 1
                    recipient_gate = await _recipient_gate(page, grant)
                    if recipient_gate["proceed"]:
                        fill_plan.append(
                            (
                                dom.compose_body_selector(),
                                _text_component_of(spec, grant.target),
                            )
                        )
                continue
            fill_selector, fill_text = fill_plan.pop(0)
            await page.fill(fill_selector, fill_text, timeout=CLICK_TIMEOUT_MS)
            fills_made += 1
            # THE GATE BETWEEN THE FILL AND THE CLICK. The submit selector is
            # appended only if a fresh read says it should be, so the decision
            # to submit is taken AFTER the text is in the box rather than
            # planned before it.
            #
            # TWO GATES BECAUSE THE TWO SURFACES ANSWER DIFFERENT QUESTIONS. A
            # composer's submit is already drawn and merely disabled, so the
            # fill produces a STATE CHANGE. A comment's submit does not exist
            # until the fill lands, so it is identified by ARRIVAL. Same act,
            # two instruments, and using either on the other's surface would
            # press the wrong control.
            if spec.action in ADDRESSED_TYPING_ACTIONS:
                # TWO FILLS, TWO GATES, AND THE RECIPIENT ONE RUNS FIRST.
                #
                # THE REPORTED REASON USED TO BE WHICHEVER GATE RAN LAST,
                # because this loop ran one gate after every fill and kept one
                # variable. With two fills that would report the SEND gate's
                # verdict on a run that stopped at the RECIPIENT gate, which
                # is the wrong sentence at the worst moment. Each gate keeps
                # its own block, and ``fills_made`` says which fill this pass
                # is -- so a refusal names WHICH fill it stopped on rather
                # than reporting a composite.
                if fills_made == 1:
                    # THE NAME IS TYPED; NOW IT HAS TO BE CHOSEN. Measured
                    # 2026-09-03: a bare fill commits nobody, all four chip
                    # selectors zero on a clean composer with a correct
                    # first-degree name. So the recipient gate no longer runs
                    # here -- it runs after the click, where there is
                    # something for it to find.
                    typeahead_gate = await _typeahead_gate(page, grant)
                    if typeahead_gate["proceed"]:
                        click_plan.append(typeahead_gate["selector"])
                else:
                    send_gate = await _send_gate(page)
                    if send_gate["proceed"]:
                        click_plan.append(send_gate["selector"])
            elif spec.action in DELTA_SUBMIT_ACTIONS:
                comment_gate = await _comment_submit_gate(page, before_names)
                if comment_gate["proceed"]:
                    click_plan.append(comment_gate["selector"])
            else:
                publish_gate = await _publish_submit_gate(page)
                if publish_gate["proceed"]:
                    click_plan.append(publish_gate["selector"])
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
            navigator, page, spec, grant, observation, prior_value=prior_value
        )
    except Exception as exc:  # noqa: BLE001 - the click already happened
        # WHERE TO GO AND LOOK, when the verification read itself failed.
        # This is the sentence a human follows after an irreversible act, so
        # it must name the surface that carries the answer -- it said SAVED
        # for an apply until 2026-08-31, sending him to a tab that cannot
        # settle it, and it said SAVED for seven more actions until
        # 2026-09-02, by falling out of the same else.
        #
        # ``state_landed`` IS NOW EMPTY HERE, AND THAT IS THE CORRECTION
        # RATHER THAN A LOSS. This block runs when the verification read
        # RAISED, which means it landed NOWHERE -- so the url this field held
        # was a page the verification never reached, printed under the key
        # ``verification.read_from``, whose entire job is saying where the
        # answer was read from. A url in that field is a claim that a read
        # happened there. Empty says no read happened, which is the fact.
        #
        # The place a HUMAN goes is a different question and is answered
        # separately, by ``_where_to_look``, in words rather than in an
        # address -- three of the eleven have no address this server may
        # print at all.
        state_landed = ""
        where = _where_to_look(spec.action)
        verified_why = (
            f"the verification read itself failed ({type(exc).__name__}: "
            f"{exc}), so this says nothing about whether the click landed, "
            "and nothing was read anywhere -- this is not a reading that came "
            "back empty. "
            + (
                f"Open {where} and look."
                if where
                else (
                    "AND THIS SERVER CANNOT TELL YOU WHERE TO LOOK: no "
                    f"surface is recorded for {spec.action!r}. That is a gap "
                    "in this package, not a statement that no surface exists."
                )
            )
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
    # THE EXPECTED-AFTER AND THE UNCHANGED STATE, both of which a multi-state
    # action carries on the GRANT rather than on the spec. ``spec.to_state``
    # and ``spec.from_state`` are ``None`` for one, so this branch used to
    # compare every outcome against ``None``: a change that landed perfectly
    # reported ``performed: "unknown"``, which is the worst answer available
    # here -- the operator is told to go and look at something that worked.
    #
    # ``anchor`` is the CANONICAL destination for a multi-state action, not
    # the caller's spelling of it: ``anchor_label_for`` matched what was asked
    # for against the closed set of states this server has seen rendered and
    # returned that. So this compares two strings LinkedIn produced rather
    # than one of LinkedIn's and one of a caller's.
    expected_after = spec.to_state or anchor
    unchanged_state = spec.not_performed_state or spec.from_state or live_state
    verified = bool(expected_after) and verified_state == expected_after
    if verified:
        performed: Any = True
    elif verified_state == unchanged_state:
        performed = False
    else:
        performed = UNKNOWN

    # WHAT THIS WRITE ACTED ON, KEYED BY ITS OWN TARGET KIND.
    #
    # THIS WAS ``job_id`` OR ELSE ``company_id`` UNTIL 2026-09-02, and the
    # else was not a default -- it was ``unfollow_company``'s branch with no
    # name on it. Six actions whose target is neither fell into it, so the
    # receipt reported a company id for something that is not a company. Live
    # on a ``publish_post`` receipt the same day:
    #
    #     "target": {"company_id": "Shipping a small thing today.", ...}
    #
    # HIS POST, UNDER THE KEY ``company_id``. Not a cosmetic mislabel: the
    # receipt is what he reads to find out what this server just did, and this
    # field is the part that says to WHAT.
    #
    # THE KIND IS NAMED WHATEVER HAPPENS, so an unmapped target kind produces
    # a field that says which kind it was rather than borrowing a key from a
    # kind it is not. Absent is not zero, applied to the receipt.
    target_block: dict[str, Any] = {"url": url, "kind": spec.target_kind}
    if spec.target_kind == "job_id":
        target_block["job_id"] = grant.target
        target_block["title"] = observation.facts.get("title")
        target_block["company"] = observation.facts.get("company")
    elif spec.target_kind == "company_id":
        target_block["company_id"] = grant.target
        target_block["company"] = observation.facts.get("company")
    else:
        # THE SUBJECT AND THE VALUE, SPLIT, for every composite kind -- and
        # ``subject`` is EMPTY for a one-component target rather than being
        # filled with the content a second time. ``destination_of`` already
        # owns the split; a second spelling of it here would be a second way
        # to disagree with the separator that binds a token to what the
        # preview showed.
        value = destination_of(spec, grant.target)
        target_block["subject"] = (
            grant.target[: -(len(value) + len(TARGET_JOIN))] if value else ""
        )
        target_block["value"] = value or grant.target
        target_block["what_these_are"] = (
            "the two halves of this action's canonical target, split on the "
            "separator the confirm token was bound across. For a one-part "
            "target 'subject' is empty and 'value' is the whole of it. "
            "Neither is a job id or a company id, and this block no longer "
            "calls them one."
        )

    # THE RESTORE PATH, AND IT IS NOT AN UNDO BUTTON. Ruling, 2026-09-02.
    #
    # THIS SERVER RESTORES NOTHING ON ITS OWN. What it owes him is the exact
    # string it overwrote and the exact call that puts it back -- both here,
    # both copy-pasteable, so the act of restoring is HIS and goes through the
    # same two-call gate as any other write.
    #
    # WHY NOT AN UNDO. An undo that this server could fire would be a second
    # write authorised by the first, and there is no such permission. It would
    # also be wrong the moment LinkedIn normalises what it stored -- the value
    # to put back is the one that was READ, and he is the one who can see
    # whether that is still the right answer.
    #
    # `previous_value` IS VERBATIM AND MAY BE None. None means it could not be
    # read, never that it was empty; the two are not collapsed, because on a
    # restore that difference is the whole message.
    restore_block: Optional[dict[str, Any]] = None
    if spec.action == "update_profile_field":
        restore_field, _, _ = grant.target.partition(TARGET_JOIN)
        restore_field = restore_field.strip()
        restore_block = {
            "previous_value": prior_value,
            "how_it_was_read": prior_why,
            "to_put_it_back": (
                None
                if prior_value is None
                else "linkedin_update_profile_field(field="
                + repr(restore_field)
                + ", value="
                + repr(prior_value)
                + ")  # then confirm the token it returns"
            ),
            "this_server_will_not_do_it_for_you": (
                "Restoring is a WRITE and gets its own preview, its own token "
                "and its own confirmation. Nothing here is queued, scheduled "
                "or held. If the previous value reads as null it could not be "
                "read before the change -- which is not the same as it having "
                "been empty, and on a restore that difference is the message."
            ),
        }

    return {
        "action": spec.action,
        "what": spec.summary,
        "target": target_block,
        "performed": performed,
        **({"restore": restore_block} if restore_block is not None else {}),
        # WHAT IS LEFT IN HIS COMPOSER. Beside "clicked" rather than inside
        # it, because it is a fact about HIS SCREEN rather than about this
        # server's click, and a reader looking for consequences should not
        # have to find it under a diagnostic.
        "typed_text": typed_text_residue(
            spec,
            fills_made=fills_made,
            # THE SUBMITS, NOT THE CLICKS. A typeahead suggestion is
            # pressed to ADDRESS the message and dispatches nothing, so
            # counting it here would tell him his words had gone out when
            # what happened was a name being chosen in a dropdown.
            submit_clicks=clicks_made - typeahead_clicks,
            click_error=click_error,
        ),
        "clicked": {
            "selector": selector,
            "on": landed,
            "state_before": live_state,
            "read_from": "the control itself, immediately before the click",
            "error": click_error,
            # HOW MANY CLICKS ACTUALLY HAPPENED, which for a two-click action
            # is the difference between "the flow opened" and "it submitted".
            "clicks_made": clicks_made,
            # AND HOW MANY OF THEM SUBMITTED NOTHING. Reported rather than
            # left to be inferred from the action name, because the whole
            # defect this field exists to close was a reader -- this
            # server's own -- inferring "a click happened" meant "it was
            # sent". For send_message a lone click is the SUGGESTION being
            # pressed and nothing has been dispatched.
            "typeahead_clicks": typeahead_clicks,
        },
        # WHAT THE DELTA GATE SAW, and this block is the POINT of the action
        # rather than a diagnostic. comment_on_item is expected to refuse on
        # its first use -- the submit's accessible name has never been
        # observed and observing it requires the fill -- so `arrived` and
        # `grew` ARE the measurement that first run exists to produce.
        "delta_gate": (
            None
            if comment_gate is None
            else {
                "proceeded": bool(comment_gate.get("proceed")),
                "refused_condition": comment_gate.get("refused_condition"),
                "why": comment_gate.get("why"),
                "arrived": comment_gate.get("arrived"),
                "grew": comment_gate.get("grew"),
                "observed": comment_gate.get("observed"),
            }
        ),
        # WHAT THE RECIPIENT GATE SAW, and this block is THE POINT of the
        # action rather than a diagnostic. send_message is expected to refuse
        # here on first use: nobody has ever typed into that combobox through
        # this server, and the selectors that would find a committed recipient
        # have never matched anything on any page. `per_selector` IS the
        # measurement that first run exists to produce -- it distinguishes
        # "the fill committed nobody" from "none of these is how LinkedIn
        # draws a committed recipient", which are the two answers a human has
        # to tell apart by looking.
        #
        # NO LABEL APPEARS IN IT. The needle comparison happened inside the
        # page and only integers came back; a committed recipient is by
        # definition a third party, so a name here would be the disclosure
        # this whole design avoids.
        # REPORTED SEPARATELY FROM THE RECIPIENT GATE, AND BEFORE IT, because
        # they answer different questions and a run can stop at either. This
        # one says whether a uniquely-named suggestion was found and pressed;
        # the recipient gate says whether pressing it committed anybody. A
        # single "message gate" field would collapse "the dropdown never
        # opened" into "nobody is committed", which are the two facts this
        # whole step exists to tell apart.
        "typeahead_gate": (
            None
            if typeahead_gate is None
            else {
                "proceeded": bool(typeahead_gate.get("proceed")),
                "refused_condition": typeahead_gate.get("refused_condition"),
                "why": typeahead_gate.get("why"),
                "observed": typeahead_gate.get("observed"),
                "what_this_is_not": (
                    "this gate does NOT say a recipient was committed. It "
                    "says exactly one suggestion carried your needle and was "
                    "pressed. Whether pressing it committed anybody is the "
                    "recipient gate's answer, below, and the click is never "
                    "its own evidence."
                ),
            }
        ),
        "recipient_gate": (
            None
            if recipient_gate is None
            else {
                "proceeded": bool(recipient_gate.get("proceed")),
                "refused_condition": recipient_gate.get("refused_condition"),
                "why": recipient_gate.get("why"),
                "observed": recipient_gate.get("observed"),
                "what_this_is_not": (
                    "a count of recipients is not the property this gate "
                    "checks. It requires exactly one committed recipient "
                    "WHOSE NAME CARRIES YOUR NEEDLE -- a count of one with "
                    "the wrong name refuses, because 'LinkedIn thinks this is "
                    "sendable' and 'this is addressed to the person you "
                    "named' are different claims and only the second one is "
                    "worth anything here."
                ),
            }
        ),
        # WHAT THE SEND GATE SAW. Reached only past the recipient gate, so a
        # null here on a send_message run means the recipient gate stopped it
        # and the body was never typed.
        "send_gate": (
            None
            if send_gate is None
            else {
                "proceeded": bool(send_gate.get("proceed")),
                "refused_condition": send_gate.get("refused_condition"),
                "why": send_gate.get("why"),
                "observed": send_gate.get("observed"),
            }
        ),
        # WHAT THE PUBLISH GATE SAW, for the composer.
        "publish_gate": (
            None
            if publish_gate is None
            else {
                "proceeded": bool(publish_gate.get("proceed")),
                "refused_condition": publish_gate.get("refused_condition"),
                "why": publish_gate.get("why"),
                "observed": publish_gate.get("observed"),
            }
        ),
        # WHAT THE APPLY SUBMIT GATE SAW, for the one action that has one.
        #
        # THIS BLOCK IS THE FIX FOR A DEFECT MEASURED ON A LIVE APPLY. The
        # gate produced a specific sentence for whichever of its five
        # conditions refused, and ``perform`` assigned it to a local and NEVER
        # READ IT AGAIN -- so the caller got ``performed: "unknown"`` with no
        # way to learn why, on the single action where re-running to find out
        # is exactly what the docstring forbids.
        #
        # It reports the READING rather than a verdict about the posting: how
        # many buttons the modal drew, whether the advance scan finished,
        # which advance controls it found. An unfinished scan is why=UNKNOWN
        # and not why=none, and the field says which.
        "submit_gate": (
            None
            if apply_gate is None
            else {
                "proceeded": bool(apply_gate.get("proceed")),
                "refused_condition": apply_gate.get("refused_condition"),
                "why": apply_gate.get("why"),
                "observed": {
                    key: (apply_gate.get("modal") or {}).get(key)
                    for key in (
                        "modal_present",
                        "submit_present",
                        "submit_enabled",
                        "submit_name",
                        "advance_names",
                        "advance_scan_complete",
                        "buttons_total",
                    )
                },
                "scan_limit": dom.APPLY_ADVANCE_SCAN_LIMIT,
                "what_this_is_not": (
                    "a verdict about the posting. It says which condition "
                    "stopped this attempt and what was on the screen when it "
                    "did. One reading of a modal is not evidence that this "
                    "posting cannot be applied to -- establish which "
                    "condition failed before concluding anything about the "
                    "job."
                ),
            }
        ),
        "verified": verified,
        # ONE ``verification`` KEY. THERE WERE TWO UNTIL 2026-09-02, IN THIS
        # DICT LITERAL, AND THE LATER ONE SILENTLY WON.
        #
        # The first was built from ``spec.unverifiable.as_block()`` with a
        # comment above it saying it was REPEATED ON PURPOSE, because he reads
        # the preview to decide and the result to find out what happened, and
        # the sentence he needs AFTER acting is the third one -- what to go
        # and look at. Python evaluates both keys and keeps the last, so that
        # block was constructed and discarded inside the expression that
        # returns it. Ruling 1 reached the preview and never reached the
        # result, for the whole of its life.
        #
        # AND WHAT THE SURVIVOR PRINTED IN ITS PLACE WAS WORSE THAN THE GAP.
        # Its ``surface`` fell out of an if/elif chain with no arm for
        # ``publish_post``, so the one action whose spec DECLARES that nothing
        # can confirm it told him: "the confirmation comes from LinkedIn's own
        # saved list with its own per-tab count." Nothing read that list. It
        # is a jobs tab. That is ``apply_job``'s defect one layer further out
        # -- not in the check, in the block that reports it -- which is the
        # exact thing ``Unverifiable``'s docstring forbids: A CHECK THAT
        # CANNOT PASS MAY NEVER SHIP AS THOUGH IT MIGHT.
        #
        # NOTHING CAUGHT IT BECAUSE NOTHING RAN IT.
        # ``tests/test_unverifiable_outcomes.py`` asserts the pairing between
        # the spec and ``_verify_after``, which is a statement about those two
        # and says nothing about what ``perform`` hands back; and the only
        # end-to-end ``perform`` test in the suite drove ``update_setting``,
        # which is verifiable and therefore took the surviving branch. There
        # had never been an end-to-end run of either action carrying an
        # ``Unverifiable``. See ``tests/test_result_verification_block.py``,
        # which is that run.
        #
        # THE BRANCH IS EXCLUSIVE BY THE SAME RULE THE PAIRING TEST ENFORCES:
        # an action has EXACTLY ONE of {a branch in ``_verify_after``, an
        # ``Unverifiable`` on its spec}. So a declaration and a comparison can
        # never both be true of one action, and one key can carry either.
        "verification": (
            spec.unverifiable.as_block()
            if spec.unverifiable is not None
            else {
                # THE DESTINATION AS IT WAS COMPARED, which for a multi-state
                # action is on the grant and not on the spec. Printing
                # ``spec.to_state`` here would print ``None`` beside a verdict
                # that was reached against a real string.
                "expected_state": expected_after,
                "observed_state": verified_state,
                "read_from": state_landed,
                "why": verified_why,
                # WHAT THE EVIDENCE ACTUALLY IS, read out of a table keyed by
                # this action rather than fallen out of an else written for
                # the save pair. Six of the eleven inherited that else until
                # 2026-09-02 and named evidence that does not exist for them.
                #
                # A MISSING ROW SAYS SO. It does not borrow the nearest
                # sentence, because a receipt that describes another action's
                # evidence is worse than one that admits it has none: the
                # first is read and believed.
                "surface": _VERIFIED_FROM.get(
                    spec.action,
                    "NOT RECORDED for this action. That is a gap in this "
                    "package rather than a statement about the evidence -- "
                    "the verification above ran and its reading is reported; "
                    "what is missing is the sentence saying how strong it is. "
                    "Do not read this as 'a different surface': six actions "
                    "printed that sentence by inheritance until 2026-09-02 "
                    "and for all six it was false.",
                ),
            }
        ),
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
            if spec.action == "unfollow_company"
            # AND THE SIX THAT ARE NEITHER, which read the unfollow's sentence
            # until 2026-09-02 and were told an unfollow had removed its own
            # row. ``became`` is a SAVE-FAMILY sweep -- ``perform`` only takes
            # it when ``target_kind`` is ``job_id`` -- so for these it is
            # ``None``, and the field beside a null has to explain the null
            # rather than describe somebody else's action.
            else (
                "not applicable to this action: the label above it is a sweep "
                "for a SAVE control, taken only on a job posting, so it is "
                "null here and means 'not looked for' rather than 'not "
                "found'. Nothing on this action's surface is read back this "
                "way."
            )
        ),
        # THE SURFACE IS NAMED PER ACTION, and it was not until a test caught
        # it: an unfollow whose outcome was unknown told him to go and look at
        # his SAVED JOBS. Sending him to the wrong page to check is how a
        # correct instruction becomes useless.
        #
        # TEN OF THE ELEVEN WERE STILL DOING IT ON 2026-09-02, because the fix
        # that caught the unfollow added ONE arm and left the else. Every
        # other action -- an apply, a post, a comment, an invitation, a
        # profile edit, a dark-mode change -- was sent to his saved jobs.
        #
        # AND THE TOGGLE SENTENCE WAS PRINTED ON ALL ELEVEN, which is true of
        # five. On ``apply_job`` it is not merely inapplicable, it
        # MISDESCRIBES THE DANGER IN THE SAFER DIRECTION: a retry there does
        # not perform the opposite action, it may file a second application to
        # the same employer. A generic warning that gets the danger wrong is
        # the same species of confident string as an unmeasured reversibility
        # claim, and ``WriteSpec.wrong_state_note`` exists one layer up for
        # exactly this reason.
        "read_this_if_unsure": (
            "performed is 'unknown' when the click may or may not have "
            "dispatched. Do NOT retry on 'unknown': "
            + (
                "a retry on a toggle that did land performs the opposite "
                "action."
                if spec.action in _TOGGLE_ACTIONS
                else "this action is NOT a toggle, so a retry does not undo a "
                "first attempt that landed -- it may do the same thing twice, "
                "to the same person or the same employer."
            )
            + (
                " Open " + str(_where_to_look(spec.action)) + " and look first."
                if _where_to_look(spec.action)
                else " AND THIS SERVER CANNOT TELL YOU WHERE TO LOOK: no "
                f"surface is recorded for {spec.action!r}, which is a gap in "
                "this package rather than a claim that none exists. Do not "
                "retry to find out."
            )
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
