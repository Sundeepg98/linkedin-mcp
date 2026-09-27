"""The one builder a write's preview names a person with.

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
sanitised, capped, carrying the untrusted-third-party-text marker.

Lane G wired its READERS to ``people_data`` directly -- the conversation list
and the messaging overview return records of their own -- so the ``name``
half of the seam lost its callers and is gone. What is left is the half every
PREVIEW that names a person goes through, so one rule reaches all of them:

* ``linkedin_connect_from_profile`` and ``linkedin_message_from_profile`` --
  whom the act resolved to (``named_profile.name_the_profile_target``);
* ``linkedin_send_reply`` -- the conversation's title
  (``threads.name_the_reply_recipient``);
* ``linkedin_send_invitation`` -- the member the needle selected
  (``writes._name_the_invitation_recipient``), which built its record apart
  from the others until this merge.

A HEADLINE THE PAGE DOES NOT DRAW IS ABSENT -- ``None`` -- NEVER ``""`` (the
orchestrator's order of 2026-09-27 for these previews). The operator reads the
record to check WHO, and an empty string reads as a member whose headline is
empty, where the truth is that nothing was drawn to read. The readers that
predate the rule answer "" for the same absence; they are lane G's, unchanged.
"""

from __future__ import annotations

import dataclasses
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
    argument; it is never a link read off the page. A headline that is missing,
    or that sanitises to nothing, comes back ABSENT (``None``).
    """
    record = people_data.Person.from_page(
        name=name, headline=headline, href=href, degree=degree
    )
    if record is None:
        return None
    if not record.headline:
        record = dataclasses.replace(record, headline=None)
    return record.envelope()
