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

Every spec below carries ``reversibility_measured``. Where it is False the
preview prints UNMEASURED and names the procedure that would settle it, rather
than a confident sentence nobody checked. **All three are False today**, which
is the rule biting its own author: structurally the save button is a toggle and
"reversible" is the obvious guess, but a guess printed in a confirm gate is
exactly the confident string standing in for a fact that this project keeps
being bitten by.

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
    url_template: str
    url_pattern: re.Pattern[str]
    #: The single forbidden substring this action is allowed to contain, or
    #: None. Compared with ``==`` against the entry in the forbidden list --
    #: never as a shape, because a loose exemption is how a real write hides.
    exempt_substring: Optional[str]
    summary: str
    reversibility: str
    reversibility_measured: bool
    #: What would settle the reversibility question. Printed while it is open,
    #: so the gap names its own fix instead of sitting as a caveat.
    reversibility_procedure: str
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
        reversibility="reversible by unsaving the same posting",
        reversibility_measured=False,
        reversibility_procedure=(
            "save one posting, then call linkedin_saved_jobs and confirm it "
            "appears; unsave it and confirm it leaves. Both directions read "
            "through an EXISTING read tool, so the measurement needs no new "
            "surface -- only a supervised round trip the harness currently "
            "refuses to allow."
        ),
    ),
    "linkedin_unsave_job": WriteSpec(
        action="unsave_job",
        tool_name="linkedin_unsave_job",
        url_template="https://www.linkedin.com/jobs/view/{target}/",
        url_pattern=re.compile(r"^https://www\.linkedin\.com/jobs/view/(\d{6,})/$"),
        exempt_substring=None,
        summary="Remove one job posting from your saved list.",
        reversibility="reversible by saving the same posting again",
        reversibility_measured=False,
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
        reversibility="reversible by unfollowing",
        reversibility_measured=False,
        reversibility_procedure=(
            "UNSETTLED AND THE HARDEST OF THE THREE. This server has no read "
            "that reports follow state, so unlike save there is no existing "
            "tool to confirm either direction, and the frozen fixtures carry "
            "only the UNFOLLOWED button. Following is also visible on his "
            "profile to his network, which makes it reversible in data and "
            "not reversible in what was seen. Needs a follow-state read "
            "before it can ship."
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


def render_preview(
    spec: WriteSpec, *, target: str, facts: dict[str, Any], token: str
) -> dict[str, Any]:
    """Build the block a human reads before confirming.

    ``facts`` must come from a LIVE re-read of the target, never from a cache
    and never from the caller's own argument: the whole value of a confirm gate
    is that the thing named in it is the thing that will be acted on. An id is
    not something a person can check; a job title and a company are.
    """
    if not facts.get("title") or not facts.get("company"):
        raise WriteAttemptError(
            "refusing to render a confirm gate without a live re-read of the "
            "target: a gate naming only an id asks the operator to confirm "
            "something he cannot check."
        )

    if spec.reversibility_measured:
        reversibility = spec.reversibility
    else:
        # THE MEASURED-REVERSIBILITY RULE, enforced rather than documented.
        reversibility = (
            "UNMEASURED -- this server has not verified that this action can "
            "be undone, so it will not claim it. What would settle it: "
            + spec.reversibility_procedure
        )

    return {
        "action": spec.action,
        "what": spec.summary,
        "where": {
            "job_id": target,
            "title": facts.get("title"),
            "company": facts.get("company"),
            "url": spec.url_template.format(target=target),
        },
        "reversibility": reversibility,
        "reversibility_measured": spec.reversibility_measured,
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

    THE OPEN PROBLEM, recorded so whoever finishes this does not walk into it:
    both anchors are TOGGLES, and the frozen captures only ever show the OFF
    state. Nothing here can currently tell "Save" from "Unsave", and a gate
    that cannot say which way it is about to move the toggle is not a gate. For
    save that is solvable with an existing read (``linkedin_saved_jobs``); for
    follow it is not, and that is why follow needs a follow-state read before
    it ships.
    """
    raise WriteAttemptError(
        "no write is implemented. The grant machinery, the narrowed url door, "
        "the confirm gate and the sanctioned set are all built and tested; the "
        "action itself is deliberately absent until the permission classifier "
        "allows a supervised round trip to exercise it. Nothing about this "
        "server can change LinkedIn today."
    )
