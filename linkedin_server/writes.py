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

THE MEASURED-REVERSIBILITY RULE
-------------------------------
Ratified 2026-08-23 and enforced by :func:`render_preview`:

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
:func:`render_preview` REFUSES to render at all unless it is handed the
target's measured current state and that state is the one its action is valid
from. Confirming a save on an already-saved posting is not a smaller mistake
than confirming the wrong posting.

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

    def age(self) -> float:
        return time.monotonic() - self.minted_at

    def expired(self) -> bool:
        return self.age() > GRANT_TTL_SECONDS


#: Live grants by token. Process-local by construction.
_GRANTS: dict[str, WriteGrant] = {}


def mint(action: str, target: str, preview: dict[str, Any]) -> WriteGrant:
    """Issue a single-use grant. Only a PREVIEW may call this."""
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
    if not target or not str(target).isdigit():
        raise WriteAttemptError(
            f"a grant needs a numeric target id, got {target!r}. The url is "
            "built from this integer, which is why it may not be a string a "
            "caller chose."
        )
    grant = WriteGrant(
        action=action,
        target=str(target),
        token=secrets.token_urlsafe(24),
        minted_at=time.monotonic(),
        preview=preview,
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
    """Drop every live grant. Used at teardown and by the kill switch."""
    _GRANTS.clear()


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
# 5. The gate the operator actually reads
# ---------------------------------------------------------------------------


def _direction(
    spec: WriteSpec, state: Optional[str], to_state: Optional[str]
) -> dict[str, Any]:
    """Say which way this action moves the toggle, or refuse to render at all.

    THE TOGGLE-DIRECTION RULE, enforced. Three separate refusals, and each of
    them is a real way a confirm gate could otherwise mislead him:

    1. **No state at all.** The caller did not read the target before asking.
       A gate built on that is describing a posting it has not looked at.
    2. **State unknown.** The read ran and came back ``unknown`` -- the control
       had not rendered, or there were several of them, or LinkedIn labelled it
       something this server has never seen. Proceeding on ``unknown`` is
       proceeding on a guess wearing a measurement's clothes.
    3. **Wrong state.** The posting is already saved and the action is save.
       This is the refusal most likely to be argued with, because the outcome
       looks harmless -- and it is not: on a TOGGLE, performing the action from
       the wrong state performs its OPPOSITE. A save confirmed on a saved
       posting unsaves it.
    """
    if spec.from_state is None:
        # Not a binary toggle. Open To Work has three states, so the
        # destination cannot be derived and the caller has to name it.
        if not state:
            raise WriteAttemptError(
                f"refusing to render a confirm gate for {spec.action!r} "
                "without its current setting. " + spec.direction_source
            )
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
        return {
            "currently": state,
            "after": to_state,
            "read_from": spec.direction_source,
            "who_can_see_it_now": spec.audiences.get(
                state.strip().casefold(), "UNRECOGNISED -- this server will not say"
            ),
            "who_will_see_it_after": spec.audiences[to_state.strip().casefold()],
        }

    if not state:
        raise WriteAttemptError(
            f"refusing to render a confirm gate for {spec.action!r} without "
            "the target's measured current state. Both controls this design "
            "touches are TOGGLES, and a gate that cannot say which way it "
            "moves one is not a gate. Read it first: " + spec.direction_source
        )
    if state == "unknown":
        raise WriteAttemptError(
            f"the current state of this target came back 'unknown', so "
            f"{spec.action!r} cannot say which way it would move the toggle. "
            "That is a refusal, not a delay -- proceeding here would be "
            "guessing. " + spec.direction_source
        )
    if state != spec.from_state:
        raise WriteAttemptError(
            f"{spec.action!r} is valid only from {spec.from_state!r} and this "
            f"target reads {state!r}. On a toggle, performing an action from "
            "the wrong state performs its OPPOSITE -- confirming a save on an "
            "already-saved posting would UNSAVE it -- so this is refused "
            f"rather than treated as a harmless no-op. You may have wanted "
            f"the inverse action."
        )
    return {
        "currently": state,
        "after": spec.to_state,
        "read_from": spec.direction_source,
    }


def render_preview(
    spec: WriteSpec,
    *,
    target: str,
    facts: dict[str, Any],
    token: str,
    state: Optional[str] = None,
    to_state: Optional[str] = None,
) -> dict[str, Any]:
    """Build the block a human reads before confirming.

    ``facts`` must come from a LIVE re-read of the target, never from a cache
    and never from the caller's own argument: the whole value of a confirm gate
    is that the thing named in it is the thing that will be acted on. An id is
    not something a person can check; a job title and a company are.

    ``state`` must come from the same live read. See :func:`_direction`.
    """
    if not facts.get("title") or not facts.get("company"):
        raise WriteAttemptError(
            "refusing to render a confirm gate without a live re-read of the "
            "target: a gate naming only an id asks the operator to confirm "
            "something he cannot check."
        )

    direction = _direction(spec, state, to_state)

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

    out: dict[str, Any] = {
        "action": spec.action,
        "what": spec.summary,
        "where": {
            "job_id": target,
            "title": facts.get("title"),
            "company": facts.get("company"),
            "url": spec.url_template.format(target=target)
            if spec.url_template
            else (
                "UNMEASURED -- this action's surface has never been loaded by "
                "this server, so it cannot name the page it would act on."
            ),
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
        "what_happens_next": (
            "NOTHING has been done. To perform this, call the same tool again "
            "with confirm_token set to the value below. The token is good for "
            f"{GRANT_TTL_SECONDS:.0f} seconds, works once, and only for this "
            "action on this target."
        ),
        "to_confirm": token,
    }
    if spec.audiences:
        out["who_can_see_it"] = direction.get("who_will_see_it_after")
    return out


# ---------------------------------------------------------------------------
# 6. The seam where the click will go, and does not yet
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

    :func:`_direction` now REFUSES to render a gate without the measured state,
    refuses on ``unknown``, and refuses when the state is not the one the
    action is valid from -- because on a toggle, acting from the wrong state
    performs the opposite action.
    """
    raise WriteAttemptError(
        "no write is implemented. The grant machinery, the narrowed url door, "
        "the confirm gate and the sanctioned set are all built and tested; the "
        "action itself is deliberately absent until the permission classifier "
        "allows a supervised round trip to exercise it. Nothing about this "
        "server can change LinkedIn today."
    )
