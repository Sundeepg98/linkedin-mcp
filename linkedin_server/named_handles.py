"""The two handles the read he names hands BACK to its caller -- lane NP, 2026-10-10.

``linkedin_read_named_profile`` reads the profile of ONE member he names, once,
behind its single-use grant (ruling NAMED-PROFILE-READ-BEHIND-A-GRANT). Its
answer was the person -- name, headline and link, as a people record -- and
nothing a caller could ACT with. The live lane's session 7 (2026-10-10, 11:38
to 11:45) hit the two walls that left:

* ``linkedin_people_search_shape(connections_of=...)`` takes the member's
  opaque TOKEN (census ``N 30``, ``N 85``, ``N 172`` and ``N 31``), and no tool
  returned the token of a member he names. Lifting it off the page inside a
  tool is what PAGE-MAY-VETO-NEVER-SUPPLY forbids, and the live lane rightly
  refused to.
* ``linkedin_react_to_item`` takes an item key (``M C32``), and no tool
  returned the key of a post on a profile he names -- though the profile's
  first render draws its Activity section, measured that session.

THE SANCTIONED PATTERN, which this module is: the read RETURNS the two values
as declared fields, and the CALLER passes them back as tool arguments if he
chooses. Nothing in this package consumes them: no tool reads this module's
output to build an address, and the navigation-derivation guard
(``tests/test_navigation_is_never_derived.py``) and this lane's own tests hold
that. A page never supplies; the caller, who named the member, does.

THE TWO FIELDS, AND WHAT EACH RESTS ON:

``member_token`` -- the PROFILE OWNER'S member id, exactly as LinkedIn writes it
  in the owner's own topcard links. Returned ONLY when the chain M M1's first
  contact rests on closes, end to end, on this one load:

    1. the page is the named person's profile -- the read's own identity check
       (``named_profile.identity_confirmed``) and the landing veto before it;
    2. the topcard draws ONE visible Message control, it is the OWNER'S, it is
       the composer link, and its address names the member the topcard's own id
       names (``dom.read_named_profile``: ``message_member_bound``) -- M M1's
       chain, read by the engine the press would use;
    3. EVERY link the topcard writes that names a member names that one member:
       every composer link, and every people-search link carrying
       ``connectionOf`` (``dom.read_named_profile_handles``) -- so the token is
       the one value LinkedIn wrote in all of them, never an id of anyone else
       on the page.

  Absent -- ``None``, with the first step that did not close -- whenever any
  step fails. Never guessed, and never taken from any other place on the page.

``activity_items`` -- the item keys (``urn:li:<type>:<digits>``, the shape
  ``linkedin_my_activity_items`` returns and ``linkedin_react_to_item`` takes)
  of the posts the first render's Activity section draws, at most ten, each
  with ``author``: ``owner`` (the profile owner's own post), ``another_member``
  (a repost, a comment, a post somebody else wrote: reacting to it would act
  on a stranger) or ``unknown``. ``None`` when the page draws no single
  Activity section; ``[]`` when it draws one with no item.

PEOPLE-DATA-MITIGATIONS, item by item, as these two fields keep them: (1)
declared fields only -- a token of one shape, item keys of one shape and a
closed token; no name, label or other page text; (2) nothing here is a
member's words, so there is nothing to sanitise, and the shapes are re-closed in
Python; (3) never stored -- this module holds no state, and the answer is in no
grant, no log and no file; (4) one page -- the read's one load, no scroll; (5)
visible only -- what the first render drew; (6) not a target by itself -- a
token or a key reaches an act only as an argument HE passes, behind that act's
own preview and grant.
"""

from __future__ import annotations

from typing import Any, Optional

from linkedin_server import coerce, dom

#: Why the token is absent, in the words a caller reads, per first failing step.
MEMBER_WHY_SENTENCES: dict[str, str] = {
    "chain_closed": (
        "the owner's own topcard names one member in every link it writes -- "
        "its own id, its Message link, and its connections links -- and the "
        "one visible Message control is the owner's and names that member. "
        "This is that member's token, exactly as LinkedIn wrote it."
    ),
    "no_profile_title": "the page's title is not a profile's title.",
    "no_topcard": "the page draws no topcard.",
    "more_than_one_topcard": "the page draws more than one topcard.",
    "heading_is_not_the_title": (
        "the topcard's first heading is not the name the page's title gives."
    ),
    "topcard_id_names_no_member": (
        "the topcard's own id does not carry a member token of the measured shape."
    ),
    "no_composer_link_in_topcard": (
        "the topcard draws no Message link, and the token is read only off the "
        "chain the owner's Message link closes (M M1's)."
    ),
    "a_composer_link_names_another_member": (
        "a Message link in the topcard names a member other than the one the "
        "topcard's id names: the owner's own card has no reason to draw one."
    ),
    "a_connections_link_names_another_member": (
        "a connections link in the topcard names a member other than the one "
        "the topcard's id names: the owner's own card has no reason to draw one."
    ),
}

#: What a caller does with each field, said where he reads it.
MEMBER_TOKEN_USE = (
    "Pass it back yourself, as an argument: "
    "linkedin_people_search_shape(connections_of=<this token>, include_names=True) "
    "lists this member's connections; add network='F' for the ones you share. "
    "Nothing in this server uses it on its own, and it is in no file of this server's."
)
ACTIVITY_ITEMS_USE = (
    "Pass a key back yourself, as an argument -- linkedin_react_to_item(item=<key>) "
    "previews a reaction on that post. 'owner' is the profile owner's own post; "
    "'another_member' names somebody else as its author or actor (a repost, a "
    "comment), so reacting to it would act on a stranger's post; 'unknown' is a "
    "post the page did not say whose it is. First render only, no scroll: a "
    "post that is absent here is UNKNOWN, not one they did not write."
)


def absent(why: str) -> dict[str, Any]:
    """The two fields when the read did not get as far as reading them."""
    return {
        "member_token": None,
        "member_token_why": why,
        "activity_items": None,
        "activity_items_why": why,
    }


def declared_fields(
    handles: dict[str, Any], *, message_chain: bool, message_chain_why: str = ""
) -> dict[str, Any]:
    """The two declared fields, from :func:`dom.read_named_profile_handles`'s
    re-closed reading and the read's own verdict on M M1's Message chain.

    PURE: a dict in, a dict out. ``message_chain`` is the named read's verdict
    that the topcard's one visible Message control is the owner's composer link
    and names the topcard's own member; the token needs it AND the page's own
    chain over every topcard link.
    """
    out: dict[str, Any] = {}
    member = handles.get("member")
    why = handles.get("member_why")
    error = handles.get("error")
    if error:
        out["member_token"] = None
        out["member_token_why"] = f"the topcard could not be read ({error})."
    elif not message_chain:
        out["member_token"] = None
        out["member_token_why"] = (
            "the owner's Message control did not close the chain: "
            + (message_chain_why or "it is not the one visible composer link "
               "naming the topcard's own member.")
        )
    elif why == "chain_closed" and isinstance(member, str) and dom.NAMED_MEMBER_TOKEN.fullmatch(member):
        out["member_token"] = member
        out["member_token_why"] = MEMBER_WHY_SENTENCES["chain_closed"]
    else:
        out["member_token"] = None
        out["member_token_why"] = MEMBER_WHY_SENTENCES.get(
            str(why), MEMBER_WHY_SENTENCES["no_profile_title"]
        )
    out["member_token_chain"] = {
        "message_control_is_the_owners_and_names_the_topcard_member": message_chain,
        "topcard_composer_links": coerce.as_count(handles.get("composer_links")),
        "naming_the_topcard_member": coerce.as_count(handles.get("composer_links_owner")),
        "topcard_connections_links": coerce.as_count(handles.get("connection_links")),
        "naming_the_topcard_member_too": coerce.as_count(handles.get("connection_links_owner")),
    }
    out["member_token_use"] = MEMBER_TOKEN_USE if out["member_token"] else None

    sections = coerce.as_count(handles.get("activity_sections"))
    items = handles.get("items") if isinstance(handles.get("items"), list) else []
    if error:
        out["activity_items"] = None
        out["activity_items_why"] = f"the Activity section could not be read ({error})."
    elif sections != 1:
        out["activity_items"] = None
        out["activity_items_why"] = (
            f"the first render draws {sections} Activity section(s), where exactly "
            "one is the only shape read; ABSENT, not empty."
        )
    else:
        out["activity_items"] = [
            {"item": entry["item"], "author": entry["author"]} for entry in items
        ]
        out["activity_items_why"] = (
            f"{len(items)} item(s) drawn in the Activity section's first render"
            + (", more than the ten returned" if handles.get("truncated") else "")
            + "."
        )
    out["activity_counts"] = {
        "permalink_anchors": coerce.as_count(handles.get("permalink_anchors")),
        "unrecognised": coerce.as_count(handles.get("unrecognised")),
        "unpaired": coerce.as_count(handles.get("unpaired")),
        "dropped": coerce.as_count(handles.get("dropped")),
        "truncated": handles.get("truncated") is True,
    }
    out["activity_items_use"] = ACTIVITY_ITEMS_USE if out["activity_items"] else None
    return out


def message_chain(reading: dict[str, Any], why_not: Optional[str]) -> tuple[bool, str]:
    """M M1's Message chain, from :func:`dom.read_named_profile`'s reading and
    ``named_profile._the_one_visible_and_theirs``'s verdict on the Message kind:
    the one visible Message control is the owner's, a composer LINK, and its
    address names the topcard's own member."""
    if why_not:
        return False, why_not
    if reading.get("message_tag") != "a" or reading.get("message_href") != "compose":
        return False, (
            "the owner's Message control is not a composer link, so no address "
            "of it names a member."
        )
    if reading.get("message_member_bound") is not True:
        return False, (
            "the owner's Message link does not name the member the topcard's own "
            "id names."
        )
    return True, ""
