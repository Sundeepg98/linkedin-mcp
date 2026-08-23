"""The write boundary: a grant, not a mode.

NOTHING IN THIS MODULE CAN CHANGE ANYTHING ON LINKEDIN TODAY, and that is
deliberate rather than unfinished. See "WHAT IS NOT HERE" at the bottom.

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

WHAT IS NOT HERE, AND WHY
-------------------------
There is no ``page.click``. No mutating Playwright call of any kind appears in
this module, so ``readonly.scan_source_for_mutations`` still reports ZERO hits
for every file in the package and ``test_readonly.py`` keeps its zero-line
diff.

That is the design, not a gap. The operator's harness still refuses LinkedIn
writes at the permission classifier, so a click authored today could not be
exercised even once -- and an unexercised write against the least
automation-tolerant platform in the family, on his only account, is the worst
available outcome. So the CAGE is built and exercised now; the animal arrives
the day the classifier rule exists and a supervised save/unsave round trip can
be watched. :func:`perform` is that seam, and it refuses to act.
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
            "HIM, by hand, in LinkedIn's own interface. NOT this server: no "
            "unfollow is sanctioned, so a follow performed here is one this "
            "server cannot take back. Read that before reading the word "
            "'reversible' above."
        ),
        residue=(
            "STILL-UNKNOWN, and unmeasurable by reading: WHO SAW IT. A follow "
            "can surface in his network's feed, so the data is restorable and "
            "the impression is not. Nothing on any readable surface reports "
            "whether it was shown to anyone."
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
            "all. The control that edits it sits on that card and is present "
            "in both frozen renders as aria-label=\"Open to\"."
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
            "of the audience control at any hydration state."
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
        "act is server-side on page serve so it cannot even be confirmed first"
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
            f"target reads {state!r}. On a toggle, performing an action from "
            "the wrong state performs its OPPOSITE -- confirming a save on an "
            "already-saved posting would UNSAVE it -- so this is refused "
            "rather than treated as a harmless no-op. You may have wanted the "
            "inverse action."
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
        out["what_happens_next"] = (
            "NOTHING has been done, and nothing can be: NO CONFIRM TOKEN IS "
            "ISSUED for this action. Its editor has never been loaded by this "
            "server, so there is no page to act on and a grant would be "
            "permission to do something unreachable. What you are reading is "
            "the WARNING, not an offer -- change it yourself in LinkedIn if "
            "you want it changed."
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
# 7. The seam where the click will go, and does not yet
# ---------------------------------------------------------------------------


async def perform(page: Any, grant: WriteGrant) -> dict[str, Any]:
    """The one function that will ever act. It refuses.

    Everything above is exercised by ``tests/test_writes.py``. THIS is the part
    that cannot be exercised: the operator's permission classifier still
    refuses LinkedIn writes, so a click authored here could not be run even
    once before shipping -- against the least automation-tolerant platform in
    the family, on his only account.

    So it raises, and the refusal is the deliverable. When the rule exists, the
    body becomes a single anchored click and this docstring becomes its
    history. The anchor is already known and already frozen at BOTH hydration
    states in ``tests/fixtures/job_detail*.html``:

        button[aria-label="Save the job"]   -- present pre- and post-hydration
        button[aria-label="Follow"]         -- present pre- and post-hydration

    Anchored on the accessible name, never on ``data-view-name`` (which is
    absent before hydration) and never on a class (which is a build hash).

    THE TOGGLE PROBLEM, WHICH WAS THE STATED BLOCKER, IS SOLVED -- and it was
    solved by reading, which is the part worth carrying to the next platform.
    Both anchors are TOGGLES and every capture frozen before 2026-08-23 showed
    only their OFF state, so nothing could tell Save from Unsave or Follow from
    Unfollow. That was recorded as something a write would have to establish.
    It was not: it was a READ nobody had performed.

        follow, MEASURED 2026-08-23 by loading a posting from a company he
        already follows:
            not following -> button[aria-label="Follow"]
            following     -> button[aria-label="Following"]
        The two carry BYTE-IDENTICAL class attributes and the page has no
        aria-pressed anywhere, so the accessible name is the entire signal.
        Frozen at both renders in ``job_detail_following*.html``.

        save: the ON state of the save control has NOT been observed, and
        cannot be -- he has no saved posting on the account to observe it on.
        Direction for save therefore comes from ``linkedin_saved_jobs``, the
        list read, which is corroborated by LinkedIn's own per-tab count. That
        is a different source, not a weaker one, and it is named in the spec.

    :func:`_direction` REFUSES to render a gate without the measured state,
    refuses on ``unknown``, and refuses when the state is not the one the
    action is valid from -- because on a toggle, acting from the wrong state
    performs the opposite action. And since 2026-08-23 that state is one the
    gate READ rather than one it was handed: see section 5.

    WHAT THIS FUNCTION WILL CHECK ON THE DAY IT ACTS, recorded now while the
    reasoning is fresh. ``grant.observation`` carries the reading the preview
    performed. A grant is allowed to be two minutes old because a human was
    reading it; the READING is not, because anything else touching the account
    invalidates it. So the click, when it exists, re-checks the observation's
    age before it moves anything -- a fresh confirmation of a stale reading is
    still a write aimed at a page that has changed.
    """
    raise WriteAttemptError(
        "no write is implemented. The grant machinery, the narrowed url door, "
        "the confirm gate and the sanctioned set are all built and tested; the "
        "action itself is deliberately absent until the permission classifier "
        "allows a supervised round trip to exercise it. Nothing about this "
        "server can change LinkedIn today."
    )
