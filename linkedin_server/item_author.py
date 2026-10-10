"""WHOSE POST a reaction lands on, read off the item's own permalink -- at runtime.

RULING ``PREVIEW-NAMES-THE-RESOLVED-TARGET`` (the orchestrator, 2026-09-27,
applying NAMES-AT-RUNTIME; ``_audit/2026-09-27-rulings-previews-and-receipts.md``):
a preview names whom the tool resolved -- the name and headline read off the
page, sanitised, marked as another member's words, inside a people record --
returned at runtime and never written; a receipt carries only the target the
caller supplied. For a REACTION the person resolved is the POST'S AUTHOR: a
reaction notifies its author, and the item is the caller's argument, which may
be one of his own posts or another member's (``linkedin_react_to_item``'s
docstring, WHOSE ITEM). Lane NP, child B, 2026-10-10.

WHAT THIS ADDS TO THE CONFIRM BLOCK, and nothing else:

* ``who_this_would_reach`` -- the author, as the people record
  :func:`people_seam.person` builds: name, headline where the actor block
  draws one (``people_data.ABSENT`` where it draws none), the link NULL, the
  degree absent. The key is the one the invitation and reply previews use.
* ``author_kind`` -- a closed token, one of :data:`AUTHOR_KINDS`.
* ``who_this_would_reach_check`` -- the sentence saying where it was read and
  what its evidence class is.

WHERE IT MUST NOT GO, by construction and not by care -- the discipline of
``writes._name_the_invitation_recipient``:

* NOT into ``grant.preview``: ``writes.preview`` assigns that BEFORE this
  module runs, and :func:`name_the_item_author` returns a NEW dict.
* NOT into the observation: ``writes._read_item_permalink`` reads the reaction
  toggle and nothing else, and the observation is what a grant retains.
* NOT into a log: a read that fails is logged by its exception's TYPE.
* NOT into a receipt: ``writes.perform`` never calls this module.

WHAT WAS MEASURED, offline on 2026-10-10, over every tracked capture. The ONLY
item-permalink capture is ``tests/fixtures/live2/own_post.html`` -- HIS OWN
post; no tracked capture shows another member's post on its permalink
(``live2/group_home.html`` draws other members' posts as FEED cards). On it:

* inside ``main``, exactly ONE actor meta link (:data:`ACTOR_LINK`), to a
  MEMBER -- ``https://www.linkedin.com/in/<x>?miniProfileUrn=<x>`` -- with ONE
  name span and ONE headline span inside it (:data:`ACTOR_NAME`,
  :data:`ACTOR_HEADLINE`);
* in the left sidebar, exactly ONE identity card link ``/in/<x>/``
  (:data:`VIEWER_CARD`), in the same ``aside`` as his private creator-analytics
  link -- a widget LinkedIn shows only the signed-in member;
* ZERO analytics links inside ``main``. The post-analytics link the brief
  offered as an own-post signal is ABSENT on his own post's permalink, so its
  absence cannot mean "another member's post", and it decides nothing here.
  It is still COUNTED (:data:`MAIN_ANALYTICS`), so the first live preview on a
  named post re-measures it at no cost;
* the control menu's content is EMPTY before a press -- the owner items ("edit
  post", "delete post") render only after one (measured live by
  ``share_link``), and nothing here presses.

So NO AUTHOR-ONLY AFFORDANCE IS DRAWN WITHOUT A PRESS on his own post's
permalink, and ``author_kind`` rests on something else: whether the actor's
member link and his own identity card's link name the SAME member, compared by
:func:`same_member`. That signal is POSITIVE on his own post and present on
its capture -- the comparison returns True over it -- and that is all the
capture can show: every name and every member segment in it is sanitised to
the same placeholder, so it cannot show the comparison returning False.

WHAT IS DERIVED, said here and in the block: that the comparison returns
False on ANOTHER member's post; that another member's permalink draws the same
actor block and the same sidebar; and that LinkedIn spells both links with the
same member segment for him (a vanity segment on one and a member id on the
other would read "another_member" on his own post -- the cautious direction,
and still wrong). Hence ``author_kind`` is labelled DERIVED wherever it is
printed, and the people record beside it is what he checks.

WHY THE LINK IS NULL. ``people_seam.person``'s ``href`` is "the address THIS
SERVER loaded, composed from the caller's own argument; it is never a link read
off the page". The one address loaded here is the item's PERMALINK, which is
not a profile and canonicalises to nothing; the author's profile link is ON
the page, and a preview record handing a caller an address the page chose is
what PAGE-MAY-VETO-NEVER-SUPPLY forbids. The permalink itself is printed in the
block's ``where.url``.

WHY THE COMPARISON IS IN PYTHON AND NOT IN THE PAGE. A script that compared
the two links in the page would be a new ``page.evaluate``, and
``tests/test_readonly.py`` admits that only in ``dom.py``, under a pinned
waiver budget. So the two hrefs are read with ``get_attribute``, canonicalised
by the people-record builder's own :func:`people_data.canonical_profile_link`,
compared by the house's :func:`named_profile.same_segment`, and dropped: they
are in no return value, no log line and no exception text. Only the boolean
leaves this module.

IT READS AND RETURNS. Counts, ``inner_text`` and ``get_attribute``, on the page
the preview already loaded -- no navigation, no press, no script.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from linkedin_server import coerce, dom, named_profile, people_data, people_seam
from linkedin_server.config import logger

#: The actions whose preview names the post's author.
REACTION_ACTIONS: frozenset[str] = frozenset({"react_to_item"})

#: The closed vocabulary of ``author_kind``.
AUTHOR_KINDS: tuple[str, ...] = ("you", "another_member", "unknown")

#: The post's actor link, inside ``main``. MEASURED: exactly 1 on his own
#: post's permalink capture; 4 on a group feed of other members' posts.
ACTOR_LINK = "main a.update-components-actor__meta-link"

#: The same link when it points at a MEMBER's profile rather than an
#: organisation Page. MEASURED shape: ``/in/<x>?miniProfileUrn=<x>``.
MEMBER_ACTOR_LINK = 'main a.update-components-actor__meta-link[href*="/in/"]'

#: The actor's name: the visible half of the title, INSIDE the member link,
#: so the name read is the name of the actor whose link is compared.
#: MEASURED: exactly 1 inside the actor link on his own post's capture.
ACTOR_NAME = (
    MEMBER_ACTOR_LINK
    + ' .update-components-actor__title span[dir="ltr"] > span[aria-hidden="true"]'
)

#: The actor's headline, inside the same link. MEASURED: exactly 1.
ACTOR_HEADLINE = (
    MEMBER_ACTOR_LINK
    + ' .update-components-actor__description > span[aria-hidden="true"]'
)

#: HIS OWN identity card: a profile-card link in an ``aside`` that also draws
#: an analytics link -- the private widget, shown only to the signed-in member,
#: is what makes the card his rather than any author card a page might draw.
#: MEASURED: exactly 1 on his own post's capture, beside one such link.
VIEWER_CARD = (
    'aside:has(a[href*="/analytics/"]) a.profile-card-profile-link[href*="/in/"]'
)

#: Analytics links inside ``main``. MEASURED: 0 on his own post's permalink.
#: Counted and reported; it decides nothing.
MAIN_ANALYTICS = 'main a[href*="/analytics/"]'

#: What :func:`read_item_author` counts, and under which key.
_COUNTED: tuple[tuple[str, str], ...] = (
    ("actor_links", ACTOR_LINK),
    ("member_actor_links", MEMBER_ACTOR_LINK),
    ("names_drawn", ACTOR_NAME),
    ("headlines_drawn", ACTOR_HEADLINE),
    ("viewer_cards", VIEWER_CARD),
    ("analytics_links_in_main", MAIN_ANALYTICS),
)

#: Every key a reading carries. ``None`` means NOT READ -- never a zero.
READING_KEYS: tuple[str, ...] = (
    "toggle_state",
    "toggles_drawn",
    *(key for key, _selector in _COUNTED),
    "actor_is_viewer",
    "person",
)

#: The address prefix of a canonical profile link (``people_data``'s form).
_PROFILE_PREFIX = "https://www.linkedin.com/in/"


def _member_segment(href: Any) -> Optional[str]:
    """The member segment of a profile link, in the people-record builder's
    canonical form; ``None`` for anything that is not a profile link."""
    link = people_data.canonical_profile_link(href)
    if not isinstance(link, str) or not link.startswith(_PROFILE_PREFIX):
        return None
    return link[len(_PROFILE_PREFIX):].rstrip("/") or None


def same_member(first: Any, second: Any) -> Optional[bool]:
    """Do two profile links name the same member? ``None`` when either is not
    a profile link -- unanswered, never "no". PURE; it returns a boolean and
    nothing of either link."""
    one, other = _member_segment(first), _member_segment(second)
    if one is None or other is None:
        return None
    return named_profile.same_segment(one, other)


async def read_item_author(page: Any) -> dict[str, Any]:
    """The actor of the one post on this permalink, and whether it is HIM.

    COUNTS AND A BOOLEAN, AND ONE PEOPLE RECORD. The name and headline cross
    into this process only to be handed straight to :func:`people_seam.person`;
    the two hrefs only to be compared and dropped. Every read is wrapped: a read
    that fails leaves its field ``None`` and is logged by its TYPE.

    THE TOGGLE IS RE-READ TOO, through the same pure reader the preview used,
    so :func:`name_the_item_author` can check this is the render the
    observation described before it names anybody off it.
    """
    out: dict[str, Any] = {key: None for key in READING_KEYS}
    try:
        reaction = await dom.read_reaction_surface(page)
        out["toggle_state"], out["toggles_drawn"] = dom.reaction_toggle_state(reaction)
    except Exception as exc:  # noqa: BLE001 - a read for a human, never raised
        logger.debug("post author: the toggle did not read (%s)", type(exc).__name__)
    for key, selector in _COUNTED:
        try:
            out[key] = coerce.as_int(await page.locator(selector).count())
        except Exception as exc:  # noqa: BLE001 - an unread count stays None
            logger.debug("post author: a count did not read (%s)", type(exc).__name__)
    one_member = out["actor_links"] == 1 and out["member_actor_links"] == 1
    if one_member and out["viewer_cards"] == 1:
        try:
            out["actor_is_viewer"] = same_member(
                await page.locator(MEMBER_ACTOR_LINK).first.get_attribute("href"),
                await page.locator(VIEWER_CARD).first.get_attribute("href"),
            )
        except Exception as exc:  # noqa: BLE001 - unanswered, never "no"
            logger.debug("post author: a link did not read (%s)", type(exc).__name__)
            out["actor_is_viewer"] = None
    if one_member and out["names_drawn"] == 1 and out["headlines_drawn"] in (0, 1):
        try:
            name = await page.locator(ACTOR_NAME).first.inner_text()
            headline = None
            if out["headlines_drawn"] == 1:
                headline = await page.locator(ACTOR_HEADLINE).first.inner_text()
            out["person"] = people_seam.person(name=name, headline=headline)
        except Exception as exc:  # noqa: BLE001 - names nobody, never raised
            logger.debug("post author: the name did not read (%s)", type(exc).__name__)
            out["person"] = None
    return out


def _same_render(state: Any, reading: Mapping[str, Any]) -> bool:
    """Is the reading of the render the observation described? Its own re-read
    of the toggle must settle the same state, off exactly one toggle."""
    return (
        state in ("no_reaction", "reacted")
        and reading.get("toggle_state") == state
        and _exactly_one(reading.get("toggles_drawn"))
    )


def _exactly_one(value: Any) -> bool:
    """1 and only 1: a boolean is not a count, and ``True == 1`` in Python."""
    return coerce.as_int(value) == 1


def _one_member(reading: Mapping[str, Any]) -> bool:
    """The post's actor is ONE member: one actor link, and it is a member's."""
    return _exactly_one(reading.get("actor_links")) and _exactly_one(
        reading.get("member_actor_links")
    )


def author_kind(state: Any, reading: Mapping[str, Any]) -> str:
    """``you``, ``another_member`` or ``unknown``. PURE.

    ``you`` -- the one member actor's link and his own identity card's link
    name the same member. ``another_member`` -- the actor is ONE member and the
    two links differ, on a page whose reaction toggle WAS read and settled.
    Anything else -- the page read differently from the preview, two actors, an
    organisation, his card not drawn exactly once, a link that did not read --
    is ``unknown``. The split is DERIVED; see the module docstring.
    """
    if not _same_render(state, reading) or not _one_member(reading):
        return "unknown"
    if not _exactly_one(reading.get("viewer_cards")):
        return "unknown"
    same = reading.get("actor_is_viewer")
    if same is True:
        return "you"
    if same is False:
        return "another_member"
    return "unknown"


_KIND_SENTENCES: dict[str, str] = {
    "you": (
        "'you': the actor's profile link names the same member as your own "
        "identity card on this page, so this is YOUR OWN post."
    ),
    "another_member": (
        "'another_member': the post's one actor is a member whose profile "
        "link is not your own identity card's, so this is ANOTHER MEMBER'S "
        "post, and the act notifies them."
    ),
    "unknown": (
        "'unknown': this page did not settle whether the post is yours -- "
        "your identity card, or the private analytics widget that makes it "
        "yours, was not drawn exactly once, or a link did not read."
    ),
}


def name_the_item_author(
    observation: Any, reading: Mapping[str, Any], block: dict[str, Any]
) -> dict[str, Any]:
    """The block with whose post this is added -- a NEW dict. PURE.

    It names the author only off a reading of the SAME render the observation
    described, and only when the post's actor is ONE member; otherwise
    ``who_this_would_reach`` is ``None`` and the sentence says why.
    """
    state = getattr(observation, "state", None)
    kind = author_kind(state, reading)
    person = None
    if _same_render(state, reading) and _one_member(reading):
        candidate = reading.get("person")
        if people_data.as_record(candidate) is not None:
            person = candidate
    out = dict(block)
    out["who_this_would_reach"] = person
    out["author_kind"] = kind
    if person is None:
        out["who_this_would_reach_check"] = (
            "This permalink did not draw exactly one member as the post's "
            "actor, or it read differently from the preview's own reading, so "
            "this server cannot tell you whose post this is. Open the post "
            "yourself and check it before confirming."
        )
        return out
    out["who_this_would_reach_check"] = (
        "who_this_would_reach is the AUTHOR of the post this act lands on -- "
        "the name and headline its one actor block draws, read off the "
        "permalink already on your screen; a reaction notifies its author. "
        "author_kind is " + _KIND_SENTENCES[kind] + " AUTHOR_KIND IS DERIVED: it "
        "compares the actor's profile link with your own identity card's, and "
        "no capture has yet shown that comparison telling another member's "
        "post apart -- every name in the tracked captures is sanitised. The "
        "record's link is null by design: this server loaded the post, not "
        "the author's profile. This server keeps no copy: it is in no grant, "
        "no log and no file. CHECK IT before confirming."
    )
    return out
