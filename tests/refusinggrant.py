"""A grant that REFUSES, and an observation that is INERT, so the write
module's READERS can be driven without a write being possible.

## THE CLAIM THIS REPLACES, AND WHY IT WAS NOT A RULING

``tests/test_readers_emit_no_page_string.py`` refused to supply a
``WriteGrant`` and recorded the refusal as *"policy, not capability"*. Five
readers -- ``_live_control``, ``_verify_after``, ``_typeahead_gate``,
``_recipient_gate`` and ``perform`` -- were therefore NOT-DRIVEN, which that
file's own docstring says is never a pass.

Three measurements say the refusal was about the harness's plumbing rather
than about permission:

* **The four gates hold no door.** An AST walk of ``linkedin_server/writes.py``
  finds ZERO calls to ``click``, ``fill``, ``press``, ``type``,
  ``set_input_files``, ``select_option`` or ``goto`` inside ``_live_control``,
  ``_verify_after``, ``_typeahead_gate`` and ``_recipient_gate``, and zero
  calls to ``consume``, ``mint``, ``assert_write_url`` or ``writes_enabled``.
  ``perform`` holds all of them. The four read the page and hand back a
  verdict; the grant reaches them as ``grant.target`` and ``grant.action`` and
  nothing else. **The grant check happens at the call site, not in the
  reading.**
* **The test tree already builds grants**, at nine module sites across five
  files, and inserts them into ``writes._GRANTS`` at six more. ``tests/test_writes.py::_bare_grant``
  does it with a docstring explaining why it is "deliberately not a way round
  ``mint``". One file's local refusal is not a repository ruling when the
  repository's own write-boundary suite settled the question the other way.
* **The server says an Observation built by hand is inert**, in
  ``Observation``'s own docstring: it is redeemable only while its ``receipt``
  is live in ``_OBSERVED``, and ``_record`` is the only function that writes
  there.

## WHAT MAKES THE GRANT BELOW REFUSING RATHER THAN MERELY UNUSED

Four independent refusals, so that removing any one still leaves the object
unable to authorise anything:

1. its ``token`` is the empty string, which ``consume`` refuses by name
   before it looks anything up;
2. it is never inserted into ``writes._GRANTS``, so no token lookup can find
   it;
3. :meth:`RefusingGrant.expired` always answers ``True`` and :meth:`age`
   always answers infinity, so every TTL check refuses it;
4. ``consumed`` stays ``False``, which is the state ``perform`` refuses at its
   third statement -- before it touches the page.

``scripts/_check_the_refusing_grant_can_fail.py`` drives each of those four
red on an object that lacks it, which is this repository's condition for a
check counting as one.

**AND THE PROCESS-WIDE DOOR IS UNTOUCHED.** ``writes_enabled()`` is read at
call time from the environment; nothing in this module sets it, and
``perform`` refuses on it first whatever grant it is handed.

## THE TARGETS ARE SYNTHETIC AND THE SERVER SHAPES THEM

Every value here goes through ``writes._target_for``, which is the same
normaliser ``mint`` and ``consume`` use, so a target this module produces is
one the server would recognise -- rather than a string that half-matches and
sends a reader down a branch nobody wrote. The raw values are placeholders: no
job, company, member or item on LinkedIn is addressed by any of them.
"""

from __future__ import annotations

from typing import Any, Optional

from linkedin_server import writes

#: The raw target for each ``target_kind``, before the server normalises it.
#:
#: DIGIT RUNS ARE REQUIRED, NOT CHOSEN. ``_target_for`` refuses a job id or a
#: company id that is not numeric, because the read url is built from that
#: integer -- so a placeholder here has to be digits or the reader is never
#: reached at all. They are deliberately outside any range this repository has
#: ever captured, and no page in ``tests/fixtures`` renders either of them.
SYNTHETIC_RAW_TARGETS: dict[str, Any] = {
    "job_id": "4600000042",
    "company_id": "9900000001",
    "member": "example-harness-member",
    "item_urn": "example-harness-item",
    "self": "self",
    "post_text": "example-harness-post-text",
    "item_and_text": {
        "item": "example-harness-item",
        "text": "example-harness-comment-text",
    },
    "field_and_value": {"field": "headline", "value": "example-harness-value"},
    # THE ONE ENTRY THAT IS NOT A PLACEHOLDER. ``update_setting``'s value is
    # compared against ``writes.DARK_MODE_STATES`` -- three strings read off
    # the live page -- so a made-up one is refused by ``_target_for`` and the
    # reader is never driven. Taken from the server's own constant rather than
    # typed, so it cannot drift.
    "setting_and_value": {"setting": "dark_mode", "value": writes.DARK_MODE_STATES[0]},
    "member_and_text": {
        "member": "example-harness-member",
        "text": "example-harness-message-text",
    },
}


class RefusingGrant(writes.WriteGrant):
    """A ``WriteGrant`` that every TTL check refuses, always.

    Subclassed rather than constructed with a stale timestamp because a
    timestamp is a value somebody can change; an override is a property of the
    type. ``perform`` does ``isinstance(grant, WriteGrant)``, so this still
    satisfies the type it is standing in for -- which is the point: the reader
    gets the shape it declares, and nothing gets permission.
    """

    def age(self) -> float:
        return float("inf")

    def expired(self) -> bool:
        return True


def synthetic_target(spec: writes.WriteSpec) -> str:
    """The canonical target for ``spec``, normalised by the server itself."""
    return writes._target_for(spec, SYNTHETIC_RAW_TARGETS[spec.target_kind])


def grant_for(spec: writes.WriteSpec) -> RefusingGrant:
    """A refusing grant carrying ``spec``'s own action and a synthetic target.

    Paired with the spec ON PURPOSE. A grant is permission for ONE action, so
    a grant for ``save_job`` handed to ``follow_company``'s reader is a state
    the server can never be in, and a verdict taken there would be about a
    branch nobody wrote -- the same argument ``_domain_values`` makes for
    driving every shipped ``WriteSpec`` rather than a chosen one.
    """
    return RefusingGrant(
        action=spec.action,
        target=synthetic_target(spec),
        token="",
        minted_at=float("-inf"),
    )


def anchor_for(spec: writes.WriteSpec) -> str:
    """The control label ``perform`` would hand ``_live_control``.

    DERIVED, NEVER INVENTED. ``perform`` computes this with
    ``anchor_label_for(spec, grant.target)`` and there is no other source for
    it. Measured: a synthetic string here leaves ``save_job`` and
    ``unsave_job`` raising ``ExtractionFailedError`` instead of reaching their
    readings -- two of thirteen branches silently unmeasured, which is the
    false-clean shape this harness exists to refuse.
    """
    try:
        return str(writes.anchor_label_for(spec, synthetic_target(spec)) or "")
    except Exception:  # noqa: BLE001 -- an action with no anchor has none
        return ""


#: What :func:`observation_for` puts in ``state_why`` when the spec's
#: ``state_from`` names no table-driven reader. Spelled out rather than left
#: blank so a dump of the observation says why its facts are empty.
NO_SURFACE_READER = (
    "harness: this spec's state_from is read by a BRANCH of writes.observe "
    "rather than by an entry in _SURFACE_READS or _PERMALINK_READS, so no "
    "reader could be run here and the facts are empty"
)


async def observation_for(page: Any, spec: writes.WriteSpec) -> writes.Observation:
    """An ``Observation`` whose facts came from the spec's OWN surface reader.

    ``observe`` builds its facts by running a reader over a page it has just
    loaded. This runs the same reader over the planted page and skips the
    load, so the facts are the ones this page would really have produced --
    rather than a dict this module invented, which would drive branches on
    values the server cannot generate.

    IT IS INERT AND THAT IS THE SERVER'S OWN CLAIM, not this module's: an
    Observation is redeemable only while its ``receipt`` is live in
    ``writes._OBSERVED``, ``writes._record`` is the only writer of that map,
    and this ``receipt`` is the empty string.
    """
    target = synthetic_target(spec)
    facts: dict[str, Any] = {}
    state = writes.UNKNOWN
    why = NO_SURFACE_READER
    reader: Optional[Any] = None
    if spec.state_from in writes._SURFACE_READS:
        reader = writes._SURFACE_READS[spec.state_from][2]
    elif spec.state_from in writes._PERMALINK_READS:
        reader = writes._PERMALINK_READS[spec.state_from]
    if reader is not None:
        try:
            facts, state, why = await reader(page, spec, target=target)
        except Exception as exc:  # noqa: BLE001 -- see the two rules below
            # THE TYPE AND NEVER THE MESSAGE. An exception raised by a reader
            # driven against the planted page QUOTES THE PLANT -- that is the
            # entire finding this harness exists for -- so putting ``str(exc)``
            # here would plant the marker inside the observation and convict
            # the NEXT reader of a leak the harness itself committed.
            #
            # And it is reported rather than swallowed: an observation whose
            # facts are empty because its reader failed is a different object
            # from one whose spec has no reader, and a verdict taken on either
            # should say which.
            why = (
                f"harness: {spec.state_from}'s reader raised "
                f"{type(exc).__name__} against the planted page, so the facts "
                "are empty (the message is not carried, by design)"
            )
    return writes.Observation(
        target=target,
        target_kind=spec.target_kind,
        facts=dict(facts or {}),
        facts_url="",
        state=str(state),
        state_why=str(why),
        state_url="",
        same_page_as_action=False,
        receipt="",
        observed_at=float("-inf"),
    )


def refusal_failures(grant: Any) -> list[str]:
    """Which of the four refusals ``grant`` does NOT carry. Empty is good.

    ALL FOUR ARE REPORTED, never just the first. A control script that stops
    at one failure cannot say whether the other three are real refusals or
    merely untested, and this object's whole claim is that the four are
    independent.
    """
    out: list[str] = []
    if getattr(grant, "token", None):
        out.append("token: it is not empty, so consume() would look it up")
    if getattr(grant, "token", None) in writes._GRANTS:
        out.append("unregistered: it IS in writes._GRANTS, so a lookup finds it")
    if not grant.expired():
        out.append("expired: expired() answers False, so a TTL check admits it")
    if getattr(grant, "consumed", False):
        out.append("unconsumed: consumed is True, the state perform acts from")
    return out
