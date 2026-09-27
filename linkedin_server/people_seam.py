"""The one builder the named-person previews and the invitation preview name a
person with.

RULING ``PREVIEW-NAMES-THE-RESOLVED-TARGET`` (the orchestrator, 2026-09-27,
applying NAMES-AT-RUNTIME; ``_audit/2026-09-27-rulings-previews-and-receipts.md``):
a preview names whom the tool resolved -- the name and headline read off the
page, sanitised, marked as another member's words, and carried inside a people
record -- returned at runtime and never written. A receipt, anything that
persists after a write fires, carries only the target the caller supplied.

WHAT THIS MODULE WAS, AND WHAT IT IS NOW. Lane L5 left it as the SEAM where
lane G's shared sanitiser would adopt the names lane L5 returns
(PEOPLE-DATA-MITIGATIONS item 2), with the promise that adoption was a body
swap. Lane G's foundation, :mod:`linkedin_server.people_data`, reached master
at ``52b55b6``, and lane L5's merge of it (2026-09-27) made that swap:
:func:`person` builds a :class:`people_data.Person` and returns its envelope --
sanitised, capped, carrying the untrusted-third-party-text marker. Lane G
wired its READERS to ``people_data`` directly, so the seam's ``name`` half
lost its callers and is gone.

WHO GOES THROUGH IT, since lane L5's merge of master ``b6993e5``:

* ``linkedin_connect_from_profile`` and ``linkedin_message_from_profile`` --
  whom the act resolved to (``named_profile.name_the_profile_target``);
* ``linkedin_send_invitation`` -- the member the needle selected
  (``writes._name_the_invitation_recipient``), routed here at the
  ``52b55b6`` merge on the orchestrator's order.

``linkedin_send_reply`` went through it at the ``52b55b6`` merge and does not
any more: lane G's reply preview on ``b6993e5`` reads the line the header
draws under the title and returns a GROUP conversation as the conversation's
TITLE record (``threads.conversation_with``) -- a shape this person builder
does not make -- so the reply builds its records beside the list reader's.

THE HEADLINE FOLLOWS LANE G'S CONVENTION (``people_data.ABSENT``): a headline
no reading drew is ``None``, and one the page drew is sanitised -- and may
come back ``""``, drawn empty. So this passes what its caller READ and adds
no rule of its own. Until the ``b6993e5`` merge it also turned ``""`` into
``None``; lane G's convention tells a headline drawn empty from one not drawn,
and a caller of this builder that read none passes ``None``.
"""

from __future__ import annotations

from typing import Any, Optional

from linkedin_server import people_data


def person(
    *,
    name: Any,
    headline: Any = None,
    href: Any = None,
    degree: Any = None,
) -> Optional[dict[str, Any]]:
    """WHOM a preview resolved to: a people record's envelope, or ``None``
    when no name survives sanitising.

    ``href`` is the address THIS SERVER loaded, composed from the caller's own
    argument; it is never a link read off the page. ``headline=None`` -- the
    caller read none -- is :data:`people_data.ABSENT`.
    """
    record = people_data.Person.from_page(
        name=name, headline=headline, href=href, degree=degree
    )
    return None if record is None else record.envelope()
