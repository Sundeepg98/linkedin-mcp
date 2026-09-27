"""The three outward classes built behind the grant, and what each one needs.

RULED 2026-09-24, ``OUTWARD-CLASSES-BUILT-BEHIND-GRANTS`` (the orchestrator
applying the operator's 08:11 principle, registered in ``_audit/RULINGS.md``;
``_audit/2026-09-24-rulings-names-at-runtime.md``). Three classes are BUILT
behind the single-use :class:`writes.WriteGrant`, off by default, and each
fires only at a target the operator names in that call:

* reposting or sharing an item;
* endorsing a skill, or requesting or giving a recommendation;
* deleting or withdrawing one of HIS OWN items.

``writes.PERMANENTLY_FORBIDDEN`` keeps only the entries whose grounds are
themselves mitigations: anti-detection, loops / sweeps / scheduled writes,
auto-accept or auto-reply, de-anonymising a viewer, loading a third party's
profile for a measurement, and marking notifications read.

THIS MODULE HOLDS TWO THINGS AND DOES NOTHING. It imports nothing that opens
a page, and no function in it touches a browser.

1. :data:`RETIRED_PERMANENT_REFUSALS` -- the three entries that left
   ``writes.PERMANENTLY_FORBIDDEN`` on 2026-09-24, VERBATIM as each last read
   on master: two as at ``1902fcb``, and ``delete_or_withdraw_anything`` as
   lane L5 left it (``7d13af2``, merged at ``96c1165``), its note counting SIX
   specs once ``send_reply`` joined -- the text this lane's merge of master
   removed. They are kept, not deleted, for the reason the census keeps an
   emptied exclusion family: their grounds were re-taken as MEASUREMENTS on
   2026-08-30, the measurements are still true, and an attribution deleted
   with its entry is a ruling nobody can find again. What changed is not the
   facts but what they are FOR: each fact now sits in the spec below that
   needs it, as ``carried_facts``, instead of standing as a refusal.
2. :data:`OUTWARD_CLASS_SPECS` -- one record per act the ruling built, with
   its STATUS stated honestly:

       BUILT          a sanctioned, performable write in ``writes`` (same
                      name, same action), ready to fire and unfired
       NEEDS-CAPTURE  no build yet, because the control the act would press
                      has never been captured. The record carries the exact
                      capture -- page, state, element -- and WHY TAKING THAT
                      CAPTURE CANNOT FIRE THE ACT. The rule this lane was
                      given: build a spec only against a DOM that has been
                      captured.
       BLOCKED        something other than a capture stands first (an address
                      the read boundary refuses, or a capability LinkedIn
                      itself does not offer), named in ``blocked_by``.

WHAT EVERY RECORD OBEYS, and ``tests/test_outward_classes.py`` pins each:

* THE TARGET IS A LINK OR AN ID THE CALLER SUPPLIES, NEVER A NAME
  (``PEOPLE-DATA-MITIGATIONS`` item 6). A name read off a page never chooses
  a target (``MENTION-COMPOSITION-RULING`` stands).
* THE PAGE MAY VETO, NEVER SUPPLY (``PAGE-MAY-VETO-NEVER-SUPPLY``). Every
  address in a record is composed from the caller's argument or is a
  constant; page content can only refuse.
* A THIRD PARTY'S PROFILE IS LOADED ONLY INSIDE HIS NAMED ACT
  (``THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET``) -- which is how endorsing and
  recommending reach their controls, and why their captures can only be
  taken inside an act he names.
* EVERY LIVE PROOF FIRES ONLY AT A TARGET HE NAMES
  (``OPERATOR-NAMES-THE-TARGET``). ``live_proof`` says what he names.

THE REVERSIBILITY CLAIMS OF SIX SHIPPED SPECS LEANED ON ONE RETIRED ENTRY.
``delete_or_withdraw_anything`` was the stated reason an application, a
post, a comment, an invitation, a message and a reply each said NOBODY
could take them back through this server -- five on this lane's base, and
lane L5's ``send_reply`` the sixth, restated at the merge that brought it.
Retiring the entry did not make any of the six reversible: each
``reversible_by`` in ``writes.SANCTIONED_WRITES`` now names the record here
that governs its undo (and its status), or says why none can exist --
LinkedIn offers no withdraw of a submitted application, and a delivered
message or reply cannot be recalled.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

#: The ruling every record here rests on, by its registered id.
OUTWARD_CLASSES_RULING = "OUTWARD-CLASSES-BUILT-BEHIND-GRANTS"

#: The three classes, by the names the ruling gives them. The first two reuse
#: the retired keys' own words; the third is narrower than the retired
#: ``delete_or_withdraw_anything`` on purpose -- HIS OWN items only.
OUTWARD_CLASS_NAMES: tuple[str, ...] = (
    "repost_or_share",
    "endorse_or_recommend",
    "delete_or_withdraw_own",
)

#: The three statuses a record may carry. See the module docstring.
OUTWARD_CLASS_STATUSES: tuple[str, ...] = ("BUILT", "NEEDS-CAPTURE", "BLOCKED")

#: What a target may be. Every one is a LINK or an ID the caller supplies;
#: none of them is a name, and ``tests/test_outward_classes.py`` refuses a
#: record whose kind is not on this list.
OUTWARD_TARGET_KINDS: tuple[str, ...] = (
    "item_urn",
    "item_urn_and_text",
    "profile_link_and_skill",
    "profile_link_and_text",
    "comment_urn",
    "invitation_id",
    "group_id",
    "none",
)

#: What remains in ``writes.PERMANENTLY_FORBIDDEN`` after the ruling: the six
#: entries whose grounds are themselves mitigations. Pinned here and asserted
#: against the live dict, so the ruling's list and the code cannot drift.
SURVIVING_PERMANENT_REFUSALS: tuple[str, ...] = (
    "any_anti_detection_technique",
    "any_loop_sweep_or_scheduled_write",
    "auto_accept_or_auto_reply",
    "deanonymise_a_viewer",
    "load_a_third_partys_profile_to_measure_a_control",
    "mark_notifications_read",
)


# ---------------------------------------------------------------------------
# 1. The three retired entries, verbatim
# ---------------------------------------------------------------------------

#: RETIRED 2026-09-24 FROM ``writes.PERMANENTLY_FORBIDDEN`` UNDER
#: ``OUTWARD-CLASSES-BUILT-BEHIND-GRANTS``. Byte-for-byte the text each entry
#: last carried on master (the module docstring says which commit), so the
#: census families that were filed under them
#: (``scripts/check_exclusion_basis.py``: PF-REPOST-OR-SHARE,
#: PF-ENDORSE-OR-RECOMMEND, PF-DELETE-OR-WITHDRAW) still resolve their
#: citation after the refusal itself is gone.
#:
#: WHERE EACH ONE'S FACTS WENT:
#:
#: ``repost_or_share``        its measurement ('Repost' is a disclosure button,
#:                            3 on the feed and 8 on his profile, its menu never
#:                            opened) is the capture ``repost_item`` still
#:                            needs; its "not asked for" ground was answered by
#:                            ruling (b) and this ruling.
#: ``endorse_or_recommend``   its measurement (zero endorse controls on every
#:                            surface this package may load; only a third
#:                            party's profile carries one) is WHY endorsing
#:                            routes through THIRD-PARTY-PROFILE-FOR-A-NAMED-
#:                            TARGET -- the measurement stands and now says
#:                            where the control is, not that it is out of reach.
#: ``delete_or_withdraw_anything``
#:                            its note that six specs lean on it (five until
#:                            send_reply joined) is answered spec by spec: each
#:                            ``reversible_by`` in writes.py now names its own
#:                            route or why there is none.
RETIRED_PERMANENT_REFUSALS: dict[str, str] = {
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
    "delete_or_withdraw_anything": (
        "destruction is not a write this design covers, at any confirm level. "
        "NOTE WHAT NOW DEPENDS ON THIS ENTRY, added 2026-08-30 and CORRECTED "
        "the same day after a review counted it: SIX of the specs above cite "
        "it in reversible_by (FIVE until 2026-09-24, when send_reply joined) "
        "-- an application, a post, a comment, an invitation, a message and "
        "a reply all say NOBODY can take them back through "
        "this server, and this line is the reason. Shortening it would "
        "silently make six reversibility claims wrong at once. The list first "
        "written here named a REACTION and omitted an APPLICATION, which was "
        "wrong in both directions at once; react_to_item does not lean on this "
        "entry at all, because its reversible_by rests on a different gap -- "
        "the ON-state label has never been observed, so there is no selector "
        "for the inverse whatever this list says"
    ),
}


# ---------------------------------------------------------------------------
# 2. The records
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CaptureSpec:
    """The capture a NEEDS-CAPTURE act waits on, in four parts.

    ``why_it_cannot_fire`` is the part that goes missing, and it is the one
    that matters: a capture that could perform the act it is meant to inform
    is buying the answer with the thing it was supposed to precede.
    """

    page: str
    state: str
    element: str
    why_it_cannot_fire: str


@dataclass(frozen=True)
class OutwardClassSpec:
    """One act of the three classes, as far as it has been taken."""

    action: str
    outward_class: str
    status: str
    #: What the caller supplies. A link or an id -- never a name.
    target_kind: str
    target: str
    #: The census rows this act governs, slice-qualified.
    census_rows: tuple[str, ...]
    #: The one-line summary the census and the lane record quote.
    summary: str
    #: The measured facts this act rests on -- including those carried from
    #: the retired permanent refusals, quoted rather than paraphrased.
    carried_facts: str
    #: Whether, and by whom, the act can be undone.
    reversible_by: str
    #: What he names for a live proof, and the page loads it costs.
    live_proof: str
    #: Required for NEEDS-CAPTURE. A BLOCKED record may carry the capture that
    #: comes AFTER its blocker; a BUILT one carries none.
    capture: Optional[CaptureSpec] = None
    #: Required for BLOCKED: what stands first, in words.
    blocked_by: str = ""


_PERMALINK = "https://www.linkedin.com/feed/update/<urn>/"
_PROFILE = "https://www.linkedin.com/in/<slug>/"

#: WHAT STANDS BEFORE EVERY CAPTURE ON A NAMED MEMBER'S PROFILE. These three
#: records read NEEDS-CAPTURE until the cold verification of lane L8
#: (2026-09-27, finding F-4) showed that their capture page is REFUSED by the
#: read boundary -- which is BLOCKED by this module's own definition, the
#: status ``withdraw_invitation`` got for the same kind of refusal.
_NAMED_PROFILE_ROUTE = (
    "the named member's profile, /in/<slug>/, is refused by the read boundary "
    "(the third-party profile pattern, removed 2026-09-04). "
    "THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET admits that load only inside the "
    "act he names, and no code path does it yet -- the route the connect and "
    "message builds (N 1, M M1) would make. That route comes first; the "
    "capture below comes after it."
)

#: THE RECORDS, one per act. Order: the three classes, in the ruling's order.
OUTWARD_CLASS_SPECS: dict[str, OutwardClassSpec] = {
    # ---- repost or share --------------------------------------------------
    "repost_item": OutwardClassSpec(
        action="repost_item",
        outward_class="repost_or_share",
        status="NEEDS-CAPTURE",
        target_kind="item_urn",
        target=(
            "the item's urn, as linkedin_react_to_item and "
            "linkedin_comment_on_item take it -- composed into the item's "
            "permalink, never read off a feed"
        ),
        census_rows=("M C20",),
        summary="Repost one item he names to his network, without a note.",
        carried_facts=(
            "From the retired repost_or_share entry, measured 2026-08-30: "
            "'Repost' is a button with aria-expanded='false', 3 on the feed "
            "and 8 on his profile, and its menu has never been opened, so what "
            "a repost even offers is unobserved. A repost republishes somebody "
            "else's item to his network under his name: the thing broadcast "
            "is not his and the audience is. The permalink is on the read "
            "allowlist since 2026-08-31 and two writes already act there "
            "(react_to_item, comment_on_item)."
        ),
        reversible_by=(
            "deleting the repost (census M C22), itself NEEDS-CAPTURE: a "
            "repost's own menu has never been opened, and none exists on his "
            "account to open. Until that is built, NOBODY through this "
            "server; and a repost's audience has seen it either way."
        ),
        live_proof=(
            "HE NAMES the item (its permalink urn). Two page loads: the "
            "preview's read of the permalink and the perform's; one "
            "verification read."
        ),
        capture=CaptureSpec(
            page=_PERMALINK + " -- composed from the urn he names",
            state=(
                "the item's own 'Repost' control (a button declaring "
                "aria-expanded='false') pressed ONCE through the shipped "
                "disclosing press, so the menu it controls is open"
            ),
            element=(
                "the menu that press discloses -- its items (expected: "
                "'Repost' and 'Repost with your thoughts'), their role and "
                "container, and whether the first opens a confirmation"
            ),
            why_it_cannot_fire=(
                "the control declares aria-expanded, so pressing it is a "
                "DISCLOSURE: it opens a menu and publishes nothing. The "
                "capture presses nothing inside the menu and closes it with "
                "Escape, and the press is priced at both ends by the item's "
                "own reaction toggle, as share_link prices its press on the "
                "same permalink."
            ),
        ),
    ),
    "repost_item_with_thoughts": OutwardClassSpec(
        action="repost_item_with_thoughts",
        outward_class="repost_or_share",
        status="NEEDS-CAPTURE",
        target_kind="item_urn_and_text",
        target=(
            "the item's urn and HIS text, verbatim -- the text a slice of the "
            "grant, as comment_on_item types it"
        ),
        census_rows=("M C21",),
        summary="Repost one item he names with his own words above it.",
        carried_facts=(
            "The same unopened Repost menu as repost_item (retired "
            "repost_or_share: 'its menu has never been opened'). The "
            "composer it is expected to open is the sharebox publish_post "
            "already types into, measured on /preload/sharebox/ (31 "
            "controls, 'Post' drawn DISABLED while empty); whether the "
            "repost variant draws the same editor is unobserved."
        ),
        reversible_by=(
            "deleting the repost (census M C22), NEEDS-CAPTURE; until then "
            "NOBODY through this server, and his words have been read."
        ),
        live_proof=(
            "HE NAMES the item and writes the text. Two page loads and one "
            "verification read."
        ),
        capture=CaptureSpec(
            page=_PERMALINK + " -- composed from the urn he names",
            state=(
                "AFTER repost_item's capture has READ the Repost menu's items "
                "(nothing pressed), the menu open again and the item whose "
                "whole accessible name is exactly 'Repost with your thoughts' "
                "pressed -- only if exactly one visible item carries that "
                "exact name -- so its composer is open and EMPTY of his text"
            ),
            element=(
                "the composer that item opens: its editor, its post control "
                "and whether that control is drawn disabled while empty"
            ),
            why_it_cannot_fire=(
                "opening a composer publishes nothing: publishing needs its "
                "own post control, which the capture never presses, and "
                "nothing is typed. The composer is closed with Escape; a "
                "discard prompt, if drawn, is answered discard. THE MISAIM IS "
                "THE RISK, and it is closed by the exact-name rule: the menu's "
                "expected sibling, 'Repost', may republish in ONE press and is "
                "a PREFIX of the item this presses, so the aim is the whole "
                "name, read first by repost_item's capture, never a prefix and "
                "never a position; anything else stops before a press. (Added "
                "2026-09-27, finding F-5 of lane L8's cold verification.)"
            ),
        ),
    ),
    # ---- endorse or recommend ---------------------------------------------
    "endorse_skill": OutwardClassSpec(
        action="endorse_skill",
        outward_class="endorse_or_recommend",
        status="BLOCKED",
        target_kind="profile_link_and_skill",
        target=(
            "the member's profile link (/in/<slug>/) and the skill, both as "
            "he supplies them; the slug is never read off a page"
        ),
        census_rows=("P E4", "N 111", "N 112"),
        summary="Endorse one skill of a 1st-degree connection he names.",
        carried_facts=(
            "From the retired endorse_or_recommend entry, re-taken "
            "2026-08-30: zero endorse controls across 13 tracked fixtures "
            "with zero shaping blindness, zero on his own skills surface, "
            "and zero among the 222 controls read live on his own profile. "
            "You cannot endorse yourself, so the only surface that would "
            "carry the control is a THIRD PARTY'S PROFILE. The operator's "
            "2026-08-25 ruling: an endorsement is a gift to the person "
            "receiving it. THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET lets that "
            "profile load inside the act he names; no code path loads "
            "/in/<slug>/ yet (the read boundary refuses the third-party "
            "profile pattern, removed 2026-09-04), and the connect and "
            "message builds that ruling unblocks (N 1, M M1) are what "
            "would build that route."
        ),
        reversible_by=(
            "removing an endorsement he gave (census P E5 / N 113), on the "
            "same profile, behind the same blocked route and then its own "
            "capture. The endorsed member is notified either way."
        ),
        live_proof=(
            "HE NAMES a 1st-degree connection's profile link and one skill. "
            "Two loads of that profile (preview, perform) and one "
            "verification read of the same profile -- each a profile view "
            "recorded in that member's viewer list, part of the act he "
            "ordered toward that same person."
        ),
        capture=CaptureSpec(
            page=_PROFILE + " -- composed from the link he names, loaded "
            "ONLY inside the endorsement he orders",
            state=(
                "the profile as first rendered for a 1st-degree connection, "
                "with its Skills section drawn"
            ),
            element=(
                "the per-skill endorse controls and the label they wear once "
                "a skill is endorsed; where the skill's name sits relative "
                "to its control"
            ),
            why_it_cannot_fire=(
                "loading a profile and reading its controls presses nothing, "
                "and the capture presses nothing in the Skills section. Its "
                "one cost -- a profile view that member can read -- is why it "
                "is taken only inside the endorsement he names, where that "
                "view is part of the act he ordered toward that same person "
                "and never a measurement spent on a stranger "
                "(load_a_third_partys_profile_to_measure_a_control stands)."
            ),
        ),
        blocked_by=_NAMED_PROFILE_ROUTE,
    ),
    "request_recommendation": OutwardClassSpec(
        action="request_recommendation",
        outward_class="endorse_or_recommend",
        status="BLOCKED",
        target_kind="profile_link_and_text",
        target=(
            "the member's profile link and his message, verbatim; the "
            "relationship and position are chosen from what the form draws"
        ),
        census_rows=("P F2", "N 119"),
        summary="Ask a member he names, by profile link, for a recommendation.",
        carried_facts=(
            "The retired endorse_or_recommend entry NAMED recommendations "
            "and measured only ENDORSE controls (profile.md finding 7.4); no "
            "census of recommendation controls has ever been taken. The "
            "route through his own profile's request form picks the person "
            "from a typeahead by NAME, which is measured dead "
            "(_audit/2026-09-03-typeahead-name-matching-is-dead.md) and "
            "which PEOPLE-DATA-MITIGATIONS item 6 forbids as an aim -- so the "
            "route is the named member's own profile."
        ),
        reversible_by=(
            "NOBODY known: no withdraw of a sent request has been observed "
            "anywhere, and the request reaches the member as a notification."
        ),
        live_proof=(
            "HE NAMES a connection's profile link and writes the message. "
            "Two profile loads and one verification read."
        ),
        capture=CaptureSpec(
            page=_PROFILE + " -- composed from the link he names, loaded "
            "ONLY inside the request he orders",
            state=(
                "the profile's own overflow ('More') disclosure opened and its "
                "items READ, none pressed; then, in the same session, the item "
                "whose whole accessible name is the request item's -- as that "
                "read found it, and only if exactly one visible item carries "
                "it -- pressed, so the request form is open and EMPTY"
            ),
            element=(
                "the menu's items and roles, the request item, the form it "
                "opens (relationship and position choices, the message box) "
                "and its send control"
            ),
            why_it_cannot_fire=(
                "the overflow is a disclosure and the item opens a FORM: "
                "nothing is sent until the form's send control is pressed, "
                "and the capture never presses it or types. The form is "
                "dismissed. Taken only inside the request he names, for the "
                "profile-view reason endorse_skill gives. THE MISAIM IS THE "
                "RISK: this menu has never been read, and a profile's overflow "
                "may carry one-press acts beside the request (UNVERIFIED -- no "
                "capture exists), so the menu is read before anything in it is "
                "pressed, the aim is an exact whole name from that read, never "
                "a prefix or a position, and anything else stops. (Added "
                "2026-09-27, finding F-5 of lane L8's cold verification.)"
            ),
        ),
        blocked_by=_NAMED_PROFILE_ROUTE,
    ),
    "give_recommendation": OutwardClassSpec(
        action="give_recommendation",
        outward_class="endorse_or_recommend",
        status="BLOCKED",
        target_kind="profile_link_and_text",
        target="the member's profile link and his recommendation text, verbatim",
        census_rows=("P F3", "N 120"),
        summary="Write and send a recommendation for a member he names.",
        carried_facts=(
            "As request_recommendation: the retired entry named "
            "recommendations and measured endorse controls only. The act "
            "publishes his words about another person onto their profile "
            "once they accept it."
        ),
        reversible_by=(
            "deleting a recommendation he sent (census P F5 / N 125) -- his "
            "own recommendations section is refused by the read boundary, so "
            "an admission comes first -- or revising it (P F4 / N 124, "
            "through the same blocked profile route); the member has been "
            "notified either way."
        ),
        live_proof=(
            "HE NAMES a connection's profile link and writes the text. Two "
            "profile loads and one verification read."
        ),
        capture=CaptureSpec(
            page=_PROFILE + " -- composed from the link he names, loaded "
            "ONLY inside the recommendation he orders",
            state=(
                "the profile's 'More' disclosure opened and its items READ, "
                "none pressed; then the item whose whole accessible name is "
                "the recommend item's -- only if exactly one visible item "
                "carries it -- pressed, so the recommendation form is open "
                "and EMPTY"
            ),
            element=(
                "the menu's items and roles, the recommend item, the form "
                "(relationship, position, text box) and its send control"
            ),
            why_it_cannot_fire=(
                "as request_recommendation: a disclosure and a form, nothing "
                "typed, the send control never pressed, the form dismissed, "
                "taken only inside the act he names -- and the same exact-name "
                "rule after a read of the never-read menu (finding F-5)."
            ),
        ),
        blocked_by=_NAMED_PROFILE_ROUTE,
    ),
    # ---- delete or withdraw one of HIS OWN items ------------------------------
    "delete_own_post": OutwardClassSpec(
        action="delete_own_post",
        outward_class="delete_or_withdraw_own",
        status="NEEDS-CAPTURE",
        target_kind="item_urn",
        target=(
            "the urn of HIS OWN post; the page may veto (the post's menu must "
            "draw the owner items), never supply"
        ),
        census_rows=("M C19",),
        summary="Delete one of his own posts, named by its urn.",
        carried_facts=(
            "MEASURED LIVE by the live lane on his own post's permalink "
            "(linkedin_server/share_link.py, 2026-09-23 and 2026-09-24): the "
            "control menu's trigger is the only 'Open control menu' control "
            "in main; its items render AFTER the press as div[role=button] "
            "in li in ul in main, no role=menu; the normalised items include "
            "'delete post' and 'edit post', which are ABSENT on another "
            "member's item. What 'delete post' does when pressed -- a "
            "confirmation, or the deletion itself -- has never been observed."
        ),
        reversible_by=(
            "NOBODY: no control this server knows restores a deleted post, "
            "and its audience has read it."
        ),
        live_proof=(
            "HE NAMES a post of his own he wants deleted. Two permalink "
            "loads and one verification read."
        ),
        capture=CaptureSpec(
            page=_PERMALINK + " -- a post HE NAMES FOR DELETION",
            state=(
                "the control menu opened through the shipped disclosing "
                "press (as share_link opens it) and its 'delete post' item "
                "pressed"
            ),
            element=(
                "whatever that press draws -- expected a confirmation dialog "
                "with a confirm and a cancel control -- and, if it draws "
                "none, the permalink's state after it"
            ),
            why_it_cannot_fire=(
                "the menu open is a disclosure. Pressing 'delete post' MAY "
                "itself delete if LinkedIn draws no confirmation, so this "
                "capture is taken ONLY on a post he names for deletion, where "
                "either outcome is the act he ordered. If a dialog is drawn "
                "the capture presses its cancel (or Escape) and nothing is "
                "deleted."
            ),
        ),
    ),
    "delete_own_comment": OutwardClassSpec(
        action="delete_own_comment",
        outward_class="delete_or_withdraw_own",
        status="NEEDS-CAPTURE",
        target_kind="comment_urn",
        target=(
            "the urn of HIS OWN comment and of the item it sits under; the "
            "page may veto (his comment's menu draws 'Edit', which only the "
            "author is offered), never supply"
        ),
        census_rows=("M C31",),
        summary="Delete one of his own comments, named by its urn.",
        carried_facts=(
            "MEASURED 2026-09-04 (_audit/INSTRUMENTS.md, the census-delta "
            "second half): a comment's own overflow menu draws three "
            "[role=menuitem] nodes -- 'Copy link to comment', 'Edit', "
            "'Delete'. The menu's trigger names the commenter "
            "('View more options for <member>'s comment'), so the aim must "
            "be structural and never by that name. Whether a comment's own "
            "id is readable on its element is measured on one page only "
            "(_audit/2026-09-05-feed-content.md s3). What 'Delete' does when "
            "pressed has never been observed."
        ),
        reversible_by=(
            "NOBODY: no control this server knows restores a deleted "
            "comment, and the item's author was notified when it posted."
        ),
        live_proof=(
            "HE NAMES a comment of his own he wants deleted. Two permalink "
            "loads and one verification read."
        ),
        capture=CaptureSpec(
            page=_PERMALINK + " -- the item carrying a comment HE NAMES FOR "
            "DELETION",
            state=(
                "that comment's overflow menu opened, aimed by the comment's "
                "id, and its 'Delete' item pressed"
            ),
            element=(
                "the comment's id on its element (so a later aim needs no "
                "name), and whatever 'Delete' draws -- expected a "
                "confirmation dialog"
            ),
            why_it_cannot_fire=(
                "opening the menu is a disclosure; pressing 'Delete' may "
                "itself delete, so the capture is taken ONLY on a comment he "
                "names for deletion. If a dialog is drawn the capture "
                "presses cancel (or Escape) and nothing is deleted."
            ),
        ),
    ),
    "withdraw_invitation": OutwardClassSpec(
        action="withdraw_invitation",
        outward_class="delete_or_withdraw_own",
        status="BLOCKED",
        target_kind="invitation_id",
        target=(
            "the pending invitation he names -- by the member's profile link "
            "or an invitation id read off his own sent list and handed back "
            "by him, never chosen by the package"
        ),
        census_rows=("N 10", "N 12"),
        summary="Withdraw one pending invitation he sent.",
        carried_facts=(
            "LinkedIn DOES offer the withdraw: its Help Center (a568295, "
            "fetched and quoted by the network census, "
            "_audit/_census/network.md s8.5) documents My Network, "
            "Invitations, the Sent tab, Withdraw, then Withdraw again in a "
            "confirmation pop-up, and the price: 'You won't be able to send a "
            "new invitation to the same member for up to three weeks.' "
            "send_invitation's own "
            "unverifiable block names the only surface: the Sent "
            "Invitations manager under My Network > Manage > Sent. Its "
            "address contains 'invitation', on "
            "readonly._FORBIDDEN_URL_SUBSTRINGS and checked before the "
            "allowlist (network R2, whose purpose -- to stop this server "
            "SENDING invitations -- ruling (b) withdrew, while the entry "
            "still refuses); and /mynetwork/ loads consume the "
            "pending-invitation badge, a cost measured twice on its sibling "
            "badges and never on the sent sub-page."
        ),
        reversible_by=(
            "NOBODY: a withdrawn invitation is re-sent only as a new "
            "invitation, which LinkedIn refuses for up to three weeks "
            "(Help Center a568295)."
        ),
        live_proof=(
            "HE NAMES a pending invitation he sent. One manager load for the "
            "preview, one for the perform, one verification read -- each "
            "priced by the badge gate linkedin_connections carries."
        ),
        blocked_by=(
            "the Sent Invitations manager is refused by the read boundary "
            "('invitation') and unadmitted; an exact-url admission, with "
            "its badge cost measured, comes first. Then the capture: the "
            "sent list with his named pending invitation, its row's "
            "withdraw control and the confirmation pop-up LinkedIn documents "
            "(a568295), taken only on an invitation he names for withdrawal."
        ),
    ),
    "withdraw_application": OutwardClassSpec(
        action="withdraw_application",
        outward_class="delete_or_withdraw_own",
        status="BLOCKED",
        target_kind="none",
        target="none -- there is nothing to aim at",
        census_rows=(),
        summary="Withdraw an application he submitted through LinkedIn.",
        carried_facts=(
            "NOT A LINKEDIN CAPABILITY for an application submitted through "
            "LinkedIn: its Help Center (a512388) reads 'You cannot edit or "
            "withdraw an application once submitted through LinkedIn. To make "
            "changes, contact the job poster via InMail.' -- fetched and "
            "quoted by the jobs census (_audit/_census/jobs.md), which "
            "excluded it from the denominator rather than counting a GAP. "
            "The nearest act LinkedIn does offer is discarding a DRAFT "
            "application (census J 69), whose Delete control and its "
            "dialog 'Discard draft application and remove this job?' are "
            "captured in tests/fixtures/jobs_tracker_row.html."
        ),
        reversible_by="not applicable -- the act does not exist",
        live_proof="none",
        blocked_by=(
            "LinkedIn offers no withdraw of a submitted LinkedIn "
            "application (Help Center a512388)."
        ),
    ),
    "withdraw_from_group": OutwardClassSpec(
        action="withdraw_from_group",
        outward_class="delete_or_withdraw_own",
        status="BUILT",
        target_kind="group_id",
        target=(
            "the group's numeric id; the page may veto (no membership row "
            "carries it), never supply"
        ),
        census_rows=("M C63", "N 64"),
        summary="Leave one LinkedIn group he is a member of.",
        carried_facts=(
            "MEASURED 2026-09-05 (_audit/2026-09-05-groups-surface-measured.md "
            "s1; scripts/_probe_groups_menu.py): five per-row menus on "
            "/groups/, 'Leave this group' on all five, row-scoped by "
            "containment; the rows are aimed by the numeric group id on the "
            "row's own anchors, never by the menu's label, which carries the "
            "group's name. Captured 2026-09-20 with the menu content present "
            "in the DOM inside an aria-hidden container. What pressing "
            "'Leave this group' draws has never been observed."
        ),
        reversible_by=(
            "NOT through this server: no join write is built (census M C61), "
            "rejoining an approval-gated group needs a manager, and an "
            "unlisted group may not be findable again."
        ),
        live_proof=(
            "HE NAMES a group he belongs to and is willing to leave, by "
            "numeric id -- not his last membership, or the verification "
            "answers unknown by construction. Three /groups/ loads: the "
            "preview, the perform and the fresh-render verification."
        ),
    ),
}


def records_by_status(status: str) -> tuple[str, ...]:
    """The actions carrying ``status``, sorted. Pure."""
    return tuple(sorted(a for a, r in OUTWARD_CLASS_SPECS.items() if r.status == status))


def records_for_row(row: str) -> tuple[str, ...]:
    """The actions governing census row ``row`` (e.g. ``"M C19"``). Pure."""
    return tuple(sorted(a for a, r in OUTWARD_CLASS_SPECS.items() if row in r.census_rows))
