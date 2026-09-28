"""Tracked fixtures render only DECLARED synthetic people.

THE RULING
----------
``_audit/2026-09-24-rulings-names-at-runtime.md``, mitigation 3, NEVER STORED:
"No third party's name, headline or link is written to a tracked file, a log,
an error field, a receipt, a cache or a fixture. Fixtures use synthetic
people." The orchestrator's order applying it: fixtures use synthetic people
only, and a guard makes sure no tracked fixture carries a name outside a
declared synthetic set.

THE MECHANISM: A NAME CANNOT BE RECOGNISED; A SLOT THAT HOLDS ONE CAN BE
------------------------------------------------------------------------
``tests/test_no_committed_identity.py`` says it of itself: NAMES HAVE NO SHAPE,
and none of its checks detects one. This file does not try. It reads the
PLACES LinkedIn's markup puts a person's name, takes whatever value sits
there, and requires that value to be DECLARED:

1. Enumerate the TRACKED fixtures, ``git ls-files tests/fixtures``. The rule
   is about what the repository ships.
2. Read every person SLOT below. The value a slot holds is a CANDIDATE.
3. Every candidate must be in :data:`SYNTHETIC_PEOPLE` (this file) or in
   ``INVENTED_NAMES`` (``tests/test_a_person_name_is_never_a_literal.py``,
   imported, not copied). AN ENTRY IS A HUMAN CLAIM that the string names
   nobody, exactly as an ``INVENTED_NAMES`` entry is: the declaration is the
   assertion, and making it costs a visible edit.
4. A declared entry that no tracked fixture renders any more fails as STALE.
   A table that outlives its entries is a list of permissions nobody reviews.
5. A FAILURE NEVER PRINTS AN UNDECLARED CANDIDATE. An undeclared value may be
   a real person, and a test failure is published in CI logs. It prints the
   fixture path, line, column, slot kind and a SHA-256 prefix, and nothing
   else about the value.

THE SLOTS, each one measured in the tracked fixtures before it was admitted
---------------------------------------------------------------------------
A MEMBER LINK is an ``<a>`` whose href is a bare member address: ``/in/<slug>``
or ``/in/<slug>/``, relative or on a linkedin.com host, query and fragment
allowed, nothing below the slug. Counts are from 2026-09-27.

* ``member link: first visible text`` -- the first text line inside a member
  link, skipping script, style, template and noscript content and anything
  inside a ``visually-hidden`` element. connections_list.html 5,
  profile_views_analytics.html 4,
  profile_views_analytics_hydrated.html 4,
  synthetic/search_appearances_synthetic.html 1. NOT READ on two kinds of
  member link, both measured holding interface text rather than a person:
  the self alias ``/in/me/`` (connections_list.html's navigation link) and
  links LinkedIn marks ``isSelfProfile=true`` (profile_topcard_hydrated.html:
  an add-section control twice and an open-to-work banner).
* ``member link: heading`` -- the first visible text of an h1-h6 inside, or
  wrapping, a member link, self links included. profile_topcard_hydrated.html
  1: the synthetic stand-in for his own name.
* ``member link: picture alt`` -- the alt of an img inside a member link.
  notifications.html 3.
* ``aria-label: View X's profile`` -- notifications.html 2.
* ``aria-label: X's connection is hiring`` -- notifications.html 1.
* ``aria-label: Send a message to X`` -- 2 in each profile-views fixture.
* ``aria-label: Invite X to connect`` -- 1 in each profile-views fixture.
* ``aria-label: Select conversation with X`` -- a conversation row's label,
  which names every participant: one name, or several joined by ``, `` and a
  last `` and ``, each read as a candidate of its own.
  synthetic/messaging_compose_list.html 3 labels, 4 names. ADDED 2026-09-27
  with the second worked adopter, which returns these labels as people
  records when a caller passes ``include_names``.
* ``class: a conversation card's participant names`` -- the element
  ``linkedin_list_conversations`` reads, split the same way.
  synthetic/messaging_compose_list.html 3 elements, 4 names.
* ``class: an open conversation's title`` -- the element the reply preview
  reads. synthetic/messaging_thread.html 1. Both ADDED 2026-09-27 on lane G's
  cold verification, which found the label slot missing them: a row naming an
  undeclared person in the element and not in a label read nothing.
* ``group link: first visible text`` and ``aria-label: More options for X`` --
  a GROUP's title, which NAMES-AT-RUNTIME counts as people data and a group
  can carry a person's name: the first text of an ``<a>`` whose href is
  ``/groups/<digits>``, and the label of a membership row's menu button.
  synthetic/groups_leave_menu.html 6 and 3. ADDED 2026-09-27 at lane G's
  merge of master 7986ae3 (lane L8's fixture), accepted from their own table,
  SYNTHETIC_GROUPS.
* ``member link: aria-label matching no template`` -- the label is taken
  WHOLE, so a new label shape on a member link fails closed instead of
  passing unread. Measured 0; it is the fallback, not a slot anything uses.

MEASURED AND REJECTED, because the same slot holds text that is not a person:
``Follow X`` (synthetic/company_page_follow.html: 8 company names; the one
person it names in each profile-views fixture is read through that person's
member link anyway); ``View X`` without the possessive (a company page in
notifications.html, interface labels in synthetic/post_summary_counts.html);
``Click to stop following X`` (Pages); ``Dismiss X job``, ``X logo`` and
``Apply to X`` (jobs and companies); ``Edit X skill`` (skills); the document
``<title>`` (his stand-in name on the three profile fixtures, and jobs,
companies and page names on the rest); and the first text of a
notification's own link, measured naming two people and one company in
notifications.html.

WHAT THIS CANNOT SEE, STATED PLAINLY
------------------------------------
* NAMES OUTSIDE THE RECOGNISED SLOTS ARE INVISIBLE: headlines, post and
  comment bodies, notification sentences, free text, HTML comments,
  visually-hidden text, payloads embedded in a fixture, and non-HTML fixtures.
  Measured, not supposed: notifications.html repeats two of its people inside
  notification sentences, and the stand-in for his own name also sits in the
  ``<title>`` of three profile fixtures and in a heading under a link to the
  site root in profile_topcard.html. Those sightings are covered only because
  the same strings also sit in a slot somewhere; a name that appears ONLY in
  free text passes green.
* A NEW SLOT KIND IS INVISIBLE UNTIL IT IS ADDED HERE. A future capture that
  puts people in markup this file does not read -- a new label template, a
  data attribute, a JSON blob -- passes green until somebody measures it and
  adds the slot. The member-link label fallback narrows this for one family
  of markup and closes it for none.
* WHETHER A DECLARED NAME IS GENUINELY INVENTED IS A HUMAN CLAIM, and nothing
  here can check it. A real name typed into :data:`SYNTHETIC_PEOPLE` passes.
  What the table buys is that naming a person in a fixture is a deliberate
  act with a diff attached.
* UNTRACKED AND IGNORED FILES ARE OUT OF SCOPE. ``git ls-files`` reads the
  index, so a fixture is checked from the moment it is staged, and never
  before.
* THE HASH IS A LOCATOR, NOT A SEAL. It lets a reader match two sightings of
  one value, and keeps the value out of the log's plain text. Anyone holding a
  list of candidate names can test each one against it.
* THIS IS NOT A NAME DETECTOR. A slot holding interface text yields a
  candidate like any other; the remedy is to narrow the slot, never to declare
  interface text a person.
"""

from __future__ import annotations

import functools
import hashlib
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from typing import NamedTuple, Optional

import pytest

from tests.test_a_person_name_is_never_a_literal import INVENTED_NAMES

REPO = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = "tests/fixtures"

# ===========================================================================
# THE DECLARED TABLE -- every synthetic person the tracked fixtures render
# ===========================================================================

#: EVERY SYNTHETIC PERSON A TRACKED FIXTURE IS ALLOWED TO NAME.
#:
#: THE ENTRY IS THE CLAIM. Nothing here verifies that a listed value is really
#: invented -- nothing could. Names on ``INVENTED_NAMES`` are accepted too and
#: are NOT repeated here; see
#: :func:`test_the_two_declared_tables_do_not_overlap`.
#:
#: DECLARED 2026-09-27 FROM THE SLOTS, ON EVIDENCE RATHER THAN ON LOOKS. Every
#: entry below was read out of a slot by this file's own extractor, and each
#: one's words are the words of a member slug that
#: ``tests/test_no_committed_identity.SYNTHETIC_SLUGS`` already declares
#: invented -- the name and the address were invented together. A name that
#: agreed with no declared slug would have been reported, not listed.
SYNTHETIC_PEOPLE = frozenset(
    {
        # profile_topcard_hydrated.html -- the stand-in for his OWN name, in
        # the heading of his own top card.
        "Alex Rivera",
        # profile_views_analytics.html and its hydrated twin: the four
        # viewers, which that pair's own test records as replaced with
        # synthetic ones. The first also appears in
        # synthetic/search_appearances_synthetic.html.
        "Priya Sharma",
        "Arun Balakrishnan",
        "Meera Iyer",
        "Rohan Desai",
        # connections_list.html: five invented people on an invented page,
        # which test_no_committed_identity records as never captured.
        "Farhan Qureshi",
        "Anita Krishnan",
        "Daniel Okonkwo",
        "Lakshmi Menon",
        "Sunita Rao",
        # notifications.html: the three people its notification cards link.
        "Dana Whitfield",
        "Robin Ellery",
        "Sam Okonkwo",
        # synthetic/messaging_compose_list.html: the participants of its three
        # conversation rows (declared 2026-09-27, with the conversation slot).
        # No slug declares these; the basis is the fixture's own header -- "Its
        # CONTENT is invented. The names are not anybody's" -- and every one
        # carries a word this repository uses for a stand-in.
        "Kai Example",
        "Juno Fixture",
        "Ivo Placeholder",
        "Lea Sample",
        # synthetic/named_profile.html (declared 2026-09-27 at lane L5's
        # merge of master 52b55b6): the owner of the invented profile the
        # named-person acts read, whose invented slug casey-example-3f9a
        # carries the declared token `example`, and the stranger drawn in its
        # rail. The fixture's header says which parts are measured structure
        # and that its people are invented.
        "Casey Example",
        "Morgan Example",
    }
)

#: EVERY SYNTHETIC GROUP A TRACKED FIXTURE IS ALLOWED TO NAME. A group's title
#: is people data too -- NAMES-AT-RUNTIME returns "people's names, and the
#: titles of groups and events", and a group can be named after a person.
#: DECLARED 2026-09-27 at lane G's merge of master 7986ae3, from the two group
#: slots below, all six read out of lane L8's
#: tests/fixtures/synthetic/groups_leave_menu.html, whose header says "EVERY
#: GROUP HERE IS INVENTED -- names, ids and all". The entry is the claim, as
#: for people.
SYNTHETIC_GROUPS = frozenset(
    {
        "Brindlewick Society",
        "Marrowby Guild",
        "Oakhollow Exchange",
        "Pellucid Roundtable",
        "Quillfeather Circle",
        "Tessaline Forum",
        # synthetic/compose_suggestions.html (declared 2026-09-28, lane S, with
        # the typeahead-card slot): the title of the one group conversation
        # the composer's suggestion list draws, invented by
        # scripts/_build_capture_skeleton.py and said so in the fixture's
        # header.
        "Example Group",
    }
)

#: What a candidate may be: declared here, or declared on the neighbouring
#: table for invented people.
ACCEPTED = SYNTHETIC_PEOPLE | INVENTED_NAMES | SYNTHETIC_GROUPS

#: LINKEDIN'S OWN WORDS, MEASURED AS THE FIRST VISIBLE TEXT OF A MEMBER LINK,
#: AHEAD OF WHATEVER PERSON THE LINK NAMES. The slot rule, NARROWED as this
#: file's own remedy says, never a declaration: such a word is SKIPPED and not
#: taken, so the member link's NEXT visible text is read as its person, and a
#: name that follows one of these words is convicted exactly as before
#: (:func:`test_THIS_CONTROL_CAN_FAIL_an_interface_word_does_not_hide_the_name_after_it`).
#: Only the whole value is skipped, compared exactly.
#:
#: MEASURED 2026-09-28 in the live lane's session-2 skeletons
#: (``tests/fixtures/live2/``), 19 sites, each word a LinkedIn label kept
#: verbatim by that capture's closed word list: "Send" 11 (his profile 9, the
#: brother's profile 2), "Show all" 4 (2 and 2), "Premium" 4 (the profile
#: card in the left rail of the jobs, groups, notifications and post pages).
MEMBER_LINK_INTERFACE_WORDS = frozenset({"Premium", "Send", "Show all"})

# ===========================================================================
# THE SLOTS
# ===========================================================================

MEMBER_TEXT = "member link: first visible text"
MEMBER_HEADING = "member link: heading"
MEMBER_PICTURE = "member link: picture alt"
MEMBER_LABEL_UNPARSED = "member link: aria-label matching no template"
LABEL_VIEW_PROFILE = "aria-label: View X's profile"
LABEL_CONNECTION_HIRING = "aria-label: X's connection is hiring"
LABEL_SEND_MESSAGE = "aria-label: Send a message to X"
LABEL_INVITE = "aria-label: Invite X to connect"
LABEL_CONVERSATION = "aria-label: Select conversation with X"
CLASS_PARTICIPANTS = "class: a conversation card's participant names"
CLASS_THREAD_TITLE = "class: an open conversation's title"
GROUP_TEXT = "group link: first visible text"
LABEL_GROUP_MENU = "aria-label: More options for X"
TYPEAHEAD_NAME = "typeahead card: its name"
ALT_SUGGESTED_PHOTO = "alt: Suggested: Photo of X"

#: THE COMPOSER'S SUGGESTION CARD, added 2026-09-28 (lane S's cold review):
#: ``presence.read_suggested_presence`` reads a person's name from the
#: ``<dt>`` of an element wearing this view name, and the card's photo
#: carries the same person in its alt. Neither sat in any slot here, so the
#: fixture built for that reader passed this guard having never been read.
TYPEAHEAD_CARD = "messaging-type-ahead-card"
SUGGESTED_PHOTO = re.compile(r"^Suggested: Photo of (?P<name>.+?)\.?$")

#: SLOTS READ BY CLASS, where the messaging readers read names: the first
#: visible text inside an element wearing the class token, split into
#: participants. Added 2026-09-27: lane G's cold verification found the
#: conversation label slot missing the element ``linkedin_list_conversations``
#: actually reads (``threads.PARTICIPANT_NAMES_SELECTOR``), and the thread
#: title (``threads.TITLE_SELECTOR``) unread.
CLASS_SLOTS = {
    "msg-conversation-card__participant-names": CLASS_PARTICIPANTS,
    "msg-entity-lockup__entity-title": CLASS_THREAD_TITLE,
}

#: Every slot kind that holds a person in the tracked fixtures today. The
#: fallback is not on it: it exists to fail closed, and nothing uses it.
MEASURED_SLOTS = (
    MEMBER_TEXT,
    MEMBER_HEADING,
    MEMBER_PICTURE,
    LABEL_VIEW_PROFILE,
    LABEL_CONNECTION_HIRING,
    LABEL_SEND_MESSAGE,
    LABEL_INVITE,
    LABEL_CONVERSATION,
    CLASS_PARTICIPANTS,
    CLASS_THREAD_TITLE,
    GROUP_TEXT,
    LABEL_GROUP_MENU,
    TYPEAHEAD_NAME,
    ALT_SUGGESTED_PHOTO,
)

#: A conversation's label joins its participants with ``, `` and a last
#: `` and `` -- measured on the one group row the tracked fixtures draw.
_PARTICIPANT_SEPARATORS = re.compile(r", | and ")

#: The typographic apostrophe LinkedIn serves beside the plain one. BUILT FROM
#: ITS CODE POINT, and the reason is measured: this file's first draft wrote
#: it as an escape, and the tool that wrote the file decoded the escape into
#: the literal character -- three sites, nine non-ASCII bytes, in a file whose
#: brief was strict ASCII. :func:`test_this_file_stays_ascii` now holds that.
RIGHT_APOSTROPHE = chr(0x2019)
_APOSTROPHE = "['" + RIGHT_APOSTROPHE + "]"

#: aria-label templates that embed a person, with the person as ``name``. An
#: apostrophe is matched in both of the spellings LinkedIn serves.
LABEL_TEMPLATES = (
    (
        LABEL_VIEW_PROFILE,
        re.compile(r"^View (?P<name>.+)" + _APOSTROPHE + r"s profile\.?$"),
    ),
    (
        LABEL_CONNECTION_HIRING,
        re.compile(r"^(?P<name>.+?)" + _APOSTROPHE + r"s connection is hiring\b"),
    ),
    (LABEL_SEND_MESSAGE, re.compile(r"^Send a message to (?P<name>.+?)\.?$")),
    (LABEL_INVITE, re.compile(r"^Invite (?P<name>.+) to connect\.?$")),
    (LABEL_CONVERSATION, re.compile(r"^Select conversation with (?P<name>.+?)\.?$")),
    # A membership row's menu button: "THE LABEL CARRIES THE NAME" of the
    # group (lane L8's fixture header).
    (LABEL_GROUP_MENU, re.compile(r"^More options for (?P<name>.+?)\.?$")),
)

#: A group's own address: ``/groups/<digits>``, relative or on a linkedin.com
#: host, nothing below the id but an optional slash, query or fragment.
GROUP_HREF = re.compile(
    r"^(?:(?:https?:)?//(?:[a-z0-9-]+\.)*linkedin\.com)?"
    r"/groups/[0-9]{1,20}/?(?:[?#].*)?$",
    re.IGNORECASE | re.DOTALL,
)

#: A member's own address and nothing below it. Addresses BELOW a member --
#: ``/details/``, ``/overlay/``, ``/opportunities/``, ``/skill-insights/``,
#: ``/recent-activity/`` -- are sections of a profile and were measured
#: carrying section text, not a person: profile_topcard.html,
#: profile_topcard_hydrated.html, profile_skills.html, and a newsletter title
#: in synthetic/newsletter_subscriptions.html.
MEMBER_HREF = re.compile(
    r"^(?:(?:https?:)?//(?:[a-z0-9-]+\.)*linkedin\.com)?"
    r"/in/(?P<slug>[^/?#\s]+)/?(?:[?#].*)?$",
    re.IGNORECASE | re.DOTALL,
)

#: LinkedIn's alias for the viewer. It names nobody; its link reads "Me".
SELF_ALIAS = "me"

#: LinkedIn's own marker on a link to the viewer's profile.
SELF_PROFILE_MARK = re.compile(r"[?&]isSelfProfile=true\b", re.IGNORECASE)

_VOID = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
     "meta", "param", "source", "track", "wbr"}
)
_UNREAD = frozenset({"script", "style", "template", "noscript"})
_HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
_HIDDEN_CLASS = "visually-hidden"


class Candidate(NamedTuple):
    """One value read out of one slot. ``value`` never reaches a message."""

    slot: str
    line: int
    col: int
    value: str


class _Link:
    """An open ``<a>``: is it a member or a group link, and does its text get
    read?"""

    __slots__ = ("member", "group", "reads_text", "text_taken")

    def __init__(self, member: bool, reads_text: bool, group: bool = False) -> None:
        self.member = member
        self.group = group
        self.reads_text = reads_text
        self.text_taken = False


class _Element:
    """An open element: its tag, whether it hides its text from sight, its
    link record when it is an ``<a>``, the class slot it opens if any, and
    whether a heading or that slot was read yet."""

    __slots__ = ("tag", "hidden", "link", "slot", "text_taken", "card")

    def __init__(
        self, tag: str, hidden: bool, link: Optional[_Link], slot: Optional[str] = None,
        card: bool = False,
    ) -> None:
        self.tag = tag
        self.hidden = hidden
        self.link = link
        self.slot = slot
        self.text_taken = False
        self.card = card


def _link_for(href: str) -> _Link:
    if GROUP_HREF.match(href.strip()):
        return _Link(member=False, reads_text=True, group=True)
    match = MEMBER_HREF.match(href.strip())
    if match is None:
        return _Link(member=False, reads_text=False)
    own = match.group("slug").lower() == SELF_ALIAS or bool(
        SELF_PROFILE_MARK.search(href)
    )
    return _Link(member=True, reads_text=not own)


def _template_for(label: str) -> Optional[tuple[str, str]]:
    for slot, pattern in LABEL_TEMPLATES:
        match = pattern.match(label)
        if match:
            return slot, match.group("name")
    return None


def _first_line(data: str, line: int, offset: int) -> tuple[str, int, int]:
    """The first non-blank line of a text node, and where it starts (1-based)."""
    for number, chunk in enumerate(data.split("\n")):
        text = " ".join(chunk.split())
        if text:
            lead = len(chunk) - len(chunk.lstrip())
            if number == 0:
                return text, line, offset + lead + 1
            return text, line + number, lead + 1
    return "", line, offset + 1


class _SlotReader(HTMLParser):
    """Walks one document and records the value in every person slot."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: list[Candidate] = []
        self._open: list[_Element] = []

    def _add(self, slot: str, value: str, line: int, col: int) -> None:
        value = " ".join(value.split())
        if value:
            self.found.append(Candidate(slot, line, col, value))

    def _innermost_link(self) -> Optional[_Link]:
        for element in reversed(self._open):
            if element.link is not None:
                return element.link if element.link.member else None
        return None

    def handle_starttag(self, tag, attrs):
        line, offset = self.getpos()
        col = offset + 1
        values = {key: (value or "") for key, value in attrs}
        link = _link_for(values.get("href", "")) if tag == "a" else None

        label = " ".join(values.get("aria-label", "").split())
        if label:
            templated = _template_for(label)
            if templated is not None:
                slot, value = templated
                parts = (
                    _PARTICIPANT_SEPARATORS.split(value)
                    if slot == LABEL_CONVERSATION
                    else [value]
                )
                for part in parts:
                    self._add(slot, part, line, col)
            elif link is not None and link.member:
                self._add(MEMBER_LABEL_UNPARSED, label, line, col)

        if tag == "img" and self._innermost_link() is not None:
            self._add(MEMBER_PICTURE, values.get("alt", ""), line, col)

        if tag == "img":
            suggested = SUGGESTED_PHOTO.match(" ".join(values.get("alt", "").split()))
            if suggested is not None:
                self._add(ALT_SUGGESTED_PHOTO, suggested.group("name"), line, col)

        if tag not in _VOID:
            classes = values.get("class", "").split()
            hidden = _HIDDEN_CLASS in classes
            slot = next((s for c, s in CLASS_SLOTS.items() if c in classes), None)
            if slot is None and tag == "dt" and any(e.card for e in self._open):
                slot = TYPEAHEAD_NAME
            card = values.get("data-view-name", "") == TYPEAHEAD_CARD
            self._open.append(_Element(tag, hidden, link, slot, card))

    def handle_endtag(self, tag):
        for index in range(len(self._open) - 1, -1, -1):
            if self._open[index].tag == tag:
                del self._open[index:]
                return

    def handle_data(self, data):
        if any(element.tag in _UNREAD for element in self._open):
            return
        if any(element.hidden for element in self._open):
            return
        text, line, col = _first_line(data, *self.getpos())
        if not text:
            return
        # A CLASS SLOT is read wherever it sits, member link or not: its first
        # visible text, split into participants.
        owner = next((e for e in reversed(self._open) if e.slot), None)
        if owner is not None and not owner.text_taken:
            owner.text_taken = True
            for part in _PARTICIPANT_SEPARATORS.split(text):
                self._add(owner.slot, part, line, col)
            return
        # A GROUP LINK's first visible text is its title.
        anchor = next((e.link for e in reversed(self._open) if e.link is not None), None)
        if anchor is not None and anchor.group:
            if not anchor.text_taken:
                anchor.text_taken = True
                self._add(GROUP_TEXT, text, line, col)
            return
        member = self._innermost_link()
        if member is None:
            return
        heading = next(
            (e for e in reversed(self._open) if e.tag in _HEADINGS), None
        )
        if heading is not None:
            if not heading.text_taken:
                heading.text_taken = True
                member.text_taken = True
                self._add(MEMBER_HEADING, text, line, col)
            return
        if member.reads_text and not member.text_taken:
            if text in MEMBER_LINK_INTERFACE_WORDS:
                return
            member.text_taken = True
            self._add(MEMBER_TEXT, text, line, col)


def candidates_in(text: str) -> list[Candidate]:
    """Every value sitting in a person slot of one document, in order."""
    reader = _SlotReader()
    reader.feed(text)
    reader.close()
    return reader.found


def fingerprint(value: str) -> str:
    """A locator for a value, never the value. See THE HASH IS A LOCATOR."""
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def is_reduced_to_shape(value: str) -> bool:
    """A value whose every letter is ``X`` or ``x``: a name REDUCED TO SHAPE.

    ADDED 2026-09-28 (lane G, slice S) for the profile-views skeletons, which
    ``scripts/_build_profile_views_skeleton.py`` writes with every member's
    text reduced to shape -- upper-case letters to ``X``, the rest to ``x``,
    digits, spaces and punctuation kept. Such a value is the LENGTH of a name
    and none of its letters. Declaring it in SYNTHETIC_PEOPLE would be the
    wrong claim (it is nobody, not an invented somebody), and it is not
    interface text either, so neither remedy :func:`render_failure` offers
    fits it. THE ALPHABET IS THE WHOLE ARGUMENT: one letter that is not ``X``
    or ``x`` and the value is a candidate again, which
    :func:`test_THIS_CONTROL_CAN_FAIL_one_real_letter_makes_a_shape_a_candidate`
    shows. A value with no letter at all is not a shape and stays a candidate.
    """
    letters = [character for character in value if character.isalpha()]
    return bool(letters) and all(character in "Xx" for character in letters)


def violations(rel: str, text: str, accepted) -> list[str]:
    """One line per undeclared candidate. A PURE FUNCTION of its inputs, so the
    rule can be shown failing on a planted string without a planted file."""
    return [
        "%s:%d:%d [%s] undeclared value %s"
        % (rel, found.line, found.col, found.slot, fingerprint(found.value))
        for found in candidates_in(text)
        if found.value not in accepted and not is_reduced_to_shape(found.value)
    ]


def render_failure(found: list[str]) -> str:
    """The message a red run publishes. Built from :func:`violations` lines,
    which carry no value, so nothing here can print one either."""
    return (
        "%d value(s) in a person slot of a tracked fixture are not declared:\n"
        "  %s\n"
        "The values are deliberately NOT printed: an undeclared value may be a "
        "real person, and this message is published in CI logs. Open the "
        "fixture at the line shown. IF THE VALUE IS INVENTED, add it to "
        "SYNTHETIC_PEOPLE in tests/test_fixtures_hold_only_synthetic_people.py "
        "-- that edit is the claim. IF IT MAY BE A REAL PERSON, it does not "
        "belong in a tracked file at all: replace it with a synthetic person. "
        "IF THE SLOT HOLDS INTERFACE TEXT, narrow the slot rule; never declare "
        "interface text a person."
        % (len(found), "\n  ".join(found))
    )


def stale(declared, rendered) -> list[str]:
    """Declared entries that no fixture renders any more."""
    return sorted(set(declared) - set(rendered))


def tracked_fixtures() -> list[str]:
    """Every fixture git tracks, as repo-relative posix paths."""
    proc = subprocess.run(
        ["git", "ls-files", "--", FIXTURE_ROOT],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, "git ls-files failed: %s" % proc.stderr
    return [line for line in proc.stdout.splitlines() if line.strip()]


@functools.lru_cache(maxsize=1)
def _corpus() -> tuple[tuple[str, str], ...]:
    return tuple(
        (rel, (REPO / rel).read_text(encoding="utf-8", errors="replace"))
        for rel in tracked_fixtures()
    )


def _rendered() -> set[str]:
    return {found.value for _rel, text in _corpus() for found in candidates_in(text)}


def _slot_id(slot: str) -> str:
    """A parameter id without spaces, colons or apostrophes."""
    return re.sub(r"[^a-z0-9]+", "-", slot.lower()).strip("-")


# ---------------------------------------------------------------------------
# The rule, over every tracked fixture
# ---------------------------------------------------------------------------


def test_tracked_fixtures_render_only_declared_synthetic_people():
    """THE RULE. A person arrives in a fixture by being declared, or not at all."""
    found = [
        line for rel, text in _corpus() for line in violations(rel, text, ACCEPTED)
    ]
    assert found == [], render_failure(found)


def test_every_declared_synthetic_person_is_still_rendered():
    """A declared entry no tracked fixture renders is STALE, and goes.

    Printing the stale entries is safe: they are this file's own claims, on
    the table above already.
    """
    gone = stale(SYNTHETIC_PEOPLE | SYNTHETIC_GROUPS, _rendered())
    assert gone == [], (
        "declared in SYNTHETIC_PEOPLE or SYNTHETIC_GROUPS and rendered by no "
        "tracked fixture: %s. Delete the entry -- a permission nobody uses is a "
        "permission nobody reviews." % gone
    )


def test_the_sweep_reads_the_tracked_fixtures():
    """A sweep over an empty listing is a green test that checked nothing."""
    listed = tracked_fixtures()
    assert len(listed) >= 25, listed
    assert all(rel.startswith(FIXTURE_ROOT + "/") for rel in listed), listed
    assert sum(len(candidates_in(text)) for _rel, text in _corpus()) >= 20


@pytest.mark.parametrize("slot", MEASURED_SLOTS, ids=_slot_id)
def test_every_measured_slot_still_reads_something(slot):
    """A SLOT RULE THAT MATCHES NOTHING IS INDISTINGUISHABLE FROM A BROKEN ONE.

    Each slot was admitted because a tracked fixture uses it. If none does any
    more, either the rule broke or the slot left the corpus; both need a
    person to look, and neither may pass as green.
    """
    seen = sum(
        1
        for _rel, text in _corpus()
        for found in candidates_in(text)
        if found.slot == slot
    )
    assert seen >= 1, "no tracked fixture fills slot %r" % slot


# ---------------------------------------------------------------------------
# Controls, built from strings -- no fixture is edited to prove anything
# ---------------------------------------------------------------------------

#: THE PLANTED VALUE: invented, and UNDECLARED ON PURPOSE -- a control built
#: from an accepted value cannot fail. It is held under a name that
#: ``tests/test_a_person_name_is_never_a_literal.PERSON_CONSTANTS`` does not
#: list, deliberately: that guard would require it on ``INVENTED_NAMES``,
#: which this file ACCEPTS, and every control below would be disarmed by the
#: declaration.
PLANTED = "Zzqx Plantperson"

#: The member address the plants use. Its slug carries tokens
#: ``tests/test_no_committed_identity.SYNTHETIC_SLUG_TOKENS`` already
#: sanctions, so the plants add no identifier for that guard to find.
PLANT_MEMBER = "/in/someone-placeholder-0001/"

#: One planted document per slot kind, with the person as ``{name}``. Each is
#: modelled on the markup the slot was measured in, including the text around
#: the name that the slot must NOT read: a visually-hidden duplicate, a
#: presence status, a self link's interface text, a non-member link's label.
PLANTS = {
    MEMBER_TEXT: (
        '<a href="' + PLANT_MEMBER + '"><span>{name}</span>'
        '<span class="visually-hidden">{name}</span></a>'
    ),
    MEMBER_HEADING: (
        '<a href="https://www.linkedin.com' + PLANT_MEMBER + '?isSelfProfile=true">'
        "<h2>{name}</h2><span>Add section</span></a>"
    ),
    MEMBER_PICTURE: (
        '<a href="' + PLANT_MEMBER + '"><img alt="{name}" src="p.png">'
        '<span class="visually-hidden">Status is offline</span></a>'
    ),
    # EACH TEMPLATE IN BOTH APOSTROPHES, between the corpus and the plants.
    # notifications.html spells this label's apostrophe as the entity &#8217;
    # (typographic), so the plant spells it &#39; (plain) -- both arrive as
    # entities the parser decodes before the template sees the label.
    LABEL_VIEW_PROFILE: (
        '<a href="' + PLANT_MEMBER + '" aria-label="View {name}&#39;s profile."></a>'
    ),
    # And the other way round: notifications.html spells this one plain.
    LABEL_CONNECTION_HIRING: (
        '<a href="' + PLANT_MEMBER + '" aria-label="{name}' + RIGHT_APOSTROPHE
        + 's connection is hiring for a Plant Role at Plant Company."></a>'
    ),
    LABEL_SEND_MESSAGE: (
        '<a href="/messaging/" aria-label="Send a message to {name}">Message</a>'
    ),
    LABEL_INVITE: '<button aria-label="Invite {name} to connect">Connect</button>',
    LABEL_CONVERSATION: (
        '<div tabindex="0" aria-label="Select conversation with {name}"></div>'
    ),
    GROUP_TEXT: '<a href="/groups/12345/"><span>{name}</span></a>',
    LABEL_GROUP_MENU: (
        '<button type="button" aria-expanded="false" '
        'aria-label="More options for {name}"></button>'
    ),
    CLASS_PARTICIPANTS: (
        '<h3 class="msg-conversation-card__participant-names t-16">'
        "<div><span>{name}</span></div></h3>"
    ),
    CLASS_THREAD_TITLE: (
        '<dt class="msg-entity-lockup__entity-title-wrapper">'
        '<span class="msg-entity-lockup__entity-title">{name}</span></dt>'
    ),
    MEMBER_LABEL_UNPARSED: '<a href="' + PLANT_MEMBER + '" aria-label="{name}"></a>',
    # The composer's suggestion card, as the capture drew it: the presence
    # line and the headline beside the name, neither of which is the slot.
    TYPEAHEAD_NAME: (
        '<li role="option" data-view-name="messaging-type-ahead-card"><div>'
        '<img alt="" src="p.png"><div><span>Status is offline</span></div></div>'
        "<div><dl><dt>{name}</dt><dd>Plant Role at Plant Company</dd></dl></div></li>"
    ),
    ALT_SUGGESTED_PHOTO: '<img alt="Suggested: Photo of {name}" src="p.png">',
}

PLANTED_PATH = "tests/fixtures/planted.html"


def test_every_slot_kind_has_a_planted_control():
    """A slot added without a plant would certify without ever having failed."""
    assert set(PLANTS) == set(MEASURED_SLOTS) | {MEMBER_LABEL_UNPARSED}


@pytest.mark.parametrize("slot", sorted(PLANTS), ids=_slot_id)
def test_an_undeclared_name_in_each_slot_is_convicted(slot):
    """CAN-IT-FAIL, per slot kind, on the real extractor and the real rule.

    The slot must read EXACTLY the planted value and nothing else from the
    plant -- a reader that flagged everything would pass the conviction and
    fail this.
    """
    planted = PLANTS[slot].format(name=PLANTED)
    read = [(found.slot, found.value) for found in candidates_in(planted)]
    assert read == [(slot, PLANTED)], [kind for kind, _value in read]

    found = violations(PLANTED_PATH, planted, ACCEPTED)
    assert len(found) == 1, found
    assert "[%s]" % slot in found[0], found


@pytest.mark.parametrize("slot", sorted(PLANTS), ids=_slot_id)
def test_the_same_plant_with_a_declared_synthetic_name_passes(slot):
    """THE CONTROL FOR THE CONTROL. Without it, a rule refusing everything
    would pass every conviction above and make every fixture unwritable."""
    declared = sorted(SYNTHETIC_PEOPLE)[0]
    planted = PLANTS[slot].format(name=declared)
    assert [(found.slot, found.value) for found in candidates_in(planted)] == [
        (slot, declared)
    ]
    assert violations(PLANTED_PATH, planted, ACCEPTED) == []


#: A name as the profile-views skeleton builder writes one, and the same shape
#: with ONE letter left as the page drew it.
SHAPED_NAME = "Xxxxx Xxxxxxxxx"
SHAPED_BUT_ONE = "Xxxxx Xxxxxxxxa"


def test_a_name_reduced_to_shape_is_read_but_not_convicted():
    """The slot still READS the shape -- a reader that stopped reading would
    pass this -- and the rule does not convict it: it names nobody."""
    planted = PLANTS[MEMBER_TEXT].format(name=SHAPED_NAME)
    assert [(found.slot, found.value) for found in candidates_in(planted)] == [
        (MEMBER_TEXT, SHAPED_NAME)
    ]
    assert violations(PLANTED_PATH, planted, ACCEPTED) == []


def test_THIS_CONTROL_CAN_FAIL_one_real_letter_makes_a_shape_a_candidate():
    """The exemption is the alphabet and nothing wider."""
    planted = PLANTS[MEMBER_TEXT].format(name=SHAPED_BUT_ONE)
    found = violations(PLANTED_PATH, planted, ACCEPTED)
    assert len(found) == 1 and "[%s]" % MEMBER_TEXT in found[0], found


def test_an_interface_word_first_in_a_member_link_is_skipped_not_taken():
    """The narrowing, as the session-2 skeletons draw it: the word first, the
    person after it. The word is not a candidate; the person still is."""
    for word in sorted(MEMBER_LINK_INTERFACE_WORDS):
        planted = ('<a href="/in/xxxx/"><span>%s</span><span>%s</span></a>'
                   % (word, SHAPED_NAME))
        assert [(f.slot, f.value) for f in candidates_in(planted)] == [
            (MEMBER_TEXT, SHAPED_NAME)
        ], word
        alone = '<a href="/in/xxxx/"><span>%s</span></a>' % word
        assert candidates_in(alone) == [], word


def test_THIS_CONTROL_CAN_FAIL_an_interface_word_does_not_hide_the_name_after_it():
    """A real-looking name after a skipped word is convicted -- the skip moves
    the slot to the next text, it never closes it -- and a word that only
    CONTAINS an interface word is a candidate like any other."""
    planted = ('<a href="/in/xxxx/"><span>Premium</span><span>%s</span></a>'
               % PLANTED)
    found = violations(PLANTED_PATH, planted, ACCEPTED)
    assert len(found) == 1 and "[%s]" % MEMBER_TEXT in found[0], found
    contains = '<a href="/in/xxxx/"><span>Premium %s</span></a>' % PLANTED
    assert len(violations(PLANTED_PATH, contains, ACCEPTED)) == 1


def test_a_name_on_the_invented_table_is_accepted_by_the_import():
    """``INVENTED_NAMES`` is IMPORTED, and the import is what accepts it.

    The entry is the one the neighbouring module uses as its own invented
    stand-in. Checked against both tables, so a regression that stopped
    importing would show here rather than as a mystery red on a fixture.
    """
    # "Wren Fixturewright" since 2026-09-27: "Thornwick M" left the
    # neighbour's table with the send_message tests that held it.
    invented = "Wren Fixturewright"
    assert invented in INVENTED_NAMES, "the neighbour's table changed; pick another"
    assert invented not in SYNTHETIC_PEOPLE
    planted = PLANTS[MEMBER_TEXT].format(name=invented)
    assert violations(PLANTED_PATH, planted, ACCEPTED) == []
    assert len(violations(PLANTED_PATH, planted, SYNTHETIC_PEOPLE)) == 1


def test_a_declared_entry_no_fixture_renders_is_reported_stale():
    """The staleness rule, run against the REAL corpus with one planted
    declaration nothing renders."""
    assert stale(SYNTHETIC_PEOPLE | {PLANTED}, _rendered()) == [PLANTED]


def test_a_failure_message_never_carries_the_value_it_convicts():
    """A CI LOG IS A PUBLICATION CHANNEL. One plant in every slot kind, one
    message, and no token of the planted value anywhere in it -- while the
    locator a reader needs is."""
    planted = "\n".join(PLANTS[slot].format(name=PLANTED) for slot in sorted(PLANTS))
    found = violations(PLANTED_PATH, planted, ACCEPTED)
    assert len(found) == len(PLANTS), found

    message = render_failure(found)
    for token in PLANTED.split():
        assert token not in message, "the failure printed the value it convicted"
    assert fingerprint(PLANTED) in message
    assert PLANTED_PATH + ":" in message
    for slot in PLANTS:
        assert "[%s]" % slot in message, slot


def test_a_conversation_label_is_read_one_participant_at_a_time():
    """THE SPLIT, SHOWN BOTH WAYS. A group conversation's label names several
    people; each is a candidate of its own, so a declared name cannot vouch
    for an undeclared one beside it -- and the declared ones pass."""
    declared = sorted(SYNTHETIC_PEOPLE)[0]
    planted = PLANTS[LABEL_CONVERSATION].format(
        name=declared + ", Kai Example and " + PLANTED
    )
    assert [found.value for found in candidates_in(planted)] == [
        declared, "Kai Example", PLANTED
    ]
    found = violations(PLANTED_PATH, planted, ACCEPTED)
    assert len(found) == 1 and fingerprint(PLANTED) in found[0], found
    fine = PLANTS[LABEL_CONVERSATION].format(name=declared + " and Kai Example")
    assert violations(PLANTED_PATH, fine, ACCEPTED) == []


def test_an_unparsed_label_on_a_member_link_is_taken_whole():
    """THE FALLBACK FAILS CLOSED. A declared name inside a label shape no
    template knows is NOT trusted for containing a declared name: the whole
    label is the value, and it is undeclared."""
    declared = sorted(SYNTHETIC_PEOPLE)[0]
    label = declared + ", 2nd degree connection"
    planted = '<a href="%s" aria-label="%s"></a>' % (PLANT_MEMBER, label)
    assert [(found.slot, found.value) for found in candidates_in(planted)] == [
        (MEMBER_LABEL_UNPARSED, label)
    ]
    assert len(violations(PLANTED_PATH, planted, ACCEPTED)) == 1


# ---------------------------------------------------------------------------
# The limits, demonstrated rather than only stated
# ---------------------------------------------------------------------------

#: Places a name can sit that this guard does NOT read, one per limit the
#: module docstring states. Each is a plant the extractor must MISS.
LIMITS = {
    "free text": "<p>{name} shared a post</p>",
    "a notification sentence": (
        '<a href="/feed/"><strong>{name}</strong> posted this</a>'
    ),
    "a headline inside a member link": (
        '<a href="' + PLANT_MEMBER + '"><span>First Line</span>'
        '<p class="headline">{name}</p></a>'
    ),
    "a Follow label": '<button aria-label="Follow {name}">Follow</button>',
    "visually-hidden text": (
        '<a href="' + PLANT_MEMBER + '"><span class="visually-hidden">{name}</span></a>'
    ),
    "the self alias": '<a href="/in/me/">{name}</a>',
    "his own profile outside a heading": (
        '<a href="https://www.linkedin.com' + PLANT_MEMBER + '?isSelfProfile=true">'
        "<span>{name}</span></a>"
    ),
    "an address below a member": (
        '<a href="' + PLANT_MEMBER + 'details/skills/">{name}</a>'
    ),
    "an HTML comment": "<!-- {name} -->",
    "an embedded payload": '<code style="display: none">{{"title": "{name}"}}</code>',
    "the document title": "<title>{name} | LinkedIn</title>",
    "a picture outside a member link": '<img alt="{name}" src="p.png">',
}


@pytest.mark.parametrize("where", sorted(LIMITS), ids=_slot_id)
def test_what_this_cannot_see_is_really_unseen(where):
    """THE LIMITS ARE MEASURED, NOT JUST CONFESSED.

    If one of these starts being caught, the guard has grown a slot and the
    docstring's account of what it cannot see is wrong. Update both.
    """
    planted = LIMITS[where].format(name=PLANTED)
    assert not any(PLANTED in found.value for found in candidates_in(planted))


def test_the_limits_are_stated_where_a_reader_will_see_them():
    """The sentences that bound what green means, asserted so an edit that
    deletes one fails rather than quietly widening the claim."""
    doc = __doc__ or ""
    for phrase in (
        "NAMES OUTSIDE THE RECOGNISED SLOTS ARE INVISIBLE",
        "A NEW SLOT KIND IS INVISIBLE UNTIL IT IS ADDED HERE",
        "WHETHER A DECLARED NAME IS GENUINELY INVENTED IS A HUMAN CLAIM",
        "UNTRACKED AND IGNORED FILES ARE OUT OF SCOPE",
        "THE HASH IS A LOCATOR, NOT A SEAL",
        "THIS IS NOT A NAME DETECTOR",
    ):
        assert phrase in doc, phrase


def test_the_two_declared_tables_do_not_overlap():
    """One claim, one place. A name on both tables survives the deletion of
    either entry, which is how a stale permission outlives its review."""
    assert sorted(SYNTHETIC_PEOPLE & INVENTED_NAMES) == []
    assert sorted(SYNTHETIC_GROUPS & (SYNTHETIC_PEOPLE | INVENTED_NAMES)) == []


def test_this_file_stays_ascii():
    """See :data:`RIGHT_APOSTROPHE`: an escape written into this file once
    arrived as the character it named. Reported by offset, never by value."""
    data = Path(__file__).read_bytes()
    assert [i for i, byte in enumerate(data) if byte > 127] == []
