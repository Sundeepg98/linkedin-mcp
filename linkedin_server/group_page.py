"""Open one GROUP by its numeric id and answer in INTEGERS. No post, no name.

``/groups/<id>/`` was admitted on 2026-09-19 and census row ``N 175`` -- *reach
a private unlisted group through a direct link or an invitation* -- has sat GAP
ever since for a reason the allowlist entry states about itself:

    CONDITION 4 -- NOTHING IS FIRED, AND NOTHING HERE FIRES ANYTHING. This
    entry opens two addresses. It builds no tool, and **no tool in this
    package can navigate to either**: measured by parsing ``server.py``,
    ZERO of its registered tools take a url, an href or a link as a
    parameter, and the one group tool takes no parameter at all.

This module is the reader that entry says nobody had written. It is the whole
of the navigation half: :func:`group_page_url` builds the one address, and
:func:`read_group_page` reduces whatever LinkedIn draws there to counts.

## THE OBLIGATION THIS MODULE IS PAYING, QUOTED RATHER THAN PARAPHRASED

The same entry names the price of being first, and it is the reason this file
is a shaper and not three lines inside a tool:

    AND THE WARNING THAT OUTLIVES THIS ENTRY: ``/groups/<id>/`` DRAWS A
    GROUP FEED -- other members' posts in full. This list decides what may
    be OPENED and the shaper decides what may be SAID, and today there is no
    reader and therefore no shaper. **Whoever writes the first reader for
    this address owes it a shaper as strict as the search-results one.**

"As strict as the search-results one" is a measurable bar and it is met here by
**not building a second instrument at all**. ``search_results.py``'s strictness
is the vocabulary-in / index-out engine; ``anchors.py`` ships that engine over a
route table that already carries ``member_profile`` at index 0 and
``feed_update``, which are the exact two classes a group feed is made of. So
this module CALLS the shipped classifier rather than writing a group-flavoured
copy of it:

    A GROUP PAGE IS READ THROUGH ``anchors.read_anchors``. No new script is
    injected, no new vocabulary is shipped into a page, and the evaluate
    waiver budget in ``tests/test_readonly.py`` does not move for this row.

That is deliberate and it is this repository's own law -- *import the shipped
instrument* -- applied where the temptation to re-write was strongest, because
the shipped instrument already refuses the thing a fresh one would have had to
be told about: a raw href on this page carries ``/in/<slug>``, and a slug is a
name.

## WHAT THE ROW ACTUALLY ASKS, AND WHY THE ANSWER IS A VERDICT AND NOT A FEED

*Reach a private unlisted group through a direct link.* The question is whether
the link REACHES, not what the group says. So the reading that discharges it is
a verdict over integers:

    feed_update anchors > 0     the feed rendered, so the direct link reached
                                a group this account can see
    anchors seen == 0           the page drew nothing; the reading is about
                                the READER and not about the group
    anything else               AMBIGUOUS, and it stays ambiguous

**THE AMBIGUOUS BRANCH IS THE HONEST ONE AND IT IS NOT A HEDGE.** A membership
gate, an empty group and a LinkedIn restyle that moved the permalink all draw
a page with no post anchors on it, and nothing in this process can separate
them -- there is no known-gated group id here to calibrate against, exactly as
``groups_page.interpret_zero`` says of a membership count of zero. A reading no
instrument can fail is not a reading, so this one declines to pick the
flattering branch.

**AND MEASURED 2026-09-21, THE THIRD OF THOSE THREE IS THE ONE THAT IS TRUE,
SO ``feed_drawn`` CANNOT FIRE AT ALL TODAY.** The tool was run against three
groups this account belongs to and returned ``ambiguous`` on all three, over
pages drawing 86, 35 and 47 anchors with 16, 3 and 9 member-profile anchors
among them -- so the pages rendered and the direct link reached them. A route
census of those three captures, resolving absolute hrefs to their paths, found
``/feed/`` six times (the nav home link, twice per page) and **``/feed/update/``
zero times.** A group feed's post permalinks do not wear the route this
module's positive branch is gated on.

That is not an ambiguity, and the distinction is this repository's own: a
verdict whose positive case cannot occur is the same defect as a check that
cannot fail, seen from the other side. The row is filed
COVERED-CANNOT-DELIVER on that measurement rather than left reading as though
three private groups had been probed and found gated. Closing it needs
``anchors.ROUTE_TABLE`` to learn the shape a group post permalink actually
wears, which is an edit to a script three other readers run and is still not
this row's to make. Receipts: ``_audit/2026-09-21-the-fires-and-the-controls.md``,
``scripts/_probe_group_feed_permalinks.py``.

## NO NAME, POST, SLUG OR ADDRESS IS A RETURN VALUE OF ANYTHING HERE

* :func:`read_group_page` returns the integers ``anchors.read_anchors`` returns
  plus three named counts lifted out of them. No post text, no author, no
  href, no heading and no label is read anywhere: the classifier reads
  ``getAttribute("href")`` inside the page and answers with a POSITION in a
  table defined in ``anchors.py``.
* :func:`reachability` takes the reading and returns a token from
  :data:`REACH_STATES` plus prose this module authored, with INTEGERS
  interpolated into it and nothing else.
* **ONE FUNCTION TAKES AN IDENTIFIER AND THAT IS THE DELIBERATE EXCEPTION**,
  on the rule ``jobfilter.py`` set and ``company_page.py`` restated: a BUILDER
  has to be handed the thing it builds from. :func:`group_page_url` is that
  function, and its refusal reports the SHAPE through
  ``jobfilter.describe_shape`` rather than echoing the candidate -- because
  the most probable wrong value here is a group SLUG, and a group named after
  a person gets that person's name in its slug.

## THE ONE LIMIT, NAMED BECAUSE A LIMIT NOBODY MEASURED IS INDISTINGUISHABLE
## FROM A LIMIT NOBODY HAS

``dom.ANCHOR_CLASSIFY_JS`` HAS NO DOT-SEGMENT RULE. That is the closure
``search_results.py`` added and called *"not a refinement, it is the defect the
condition-2 amendment measured"*: an href whose leading segments say ``groups``
and whose browser-normalised form is some other page entirely is counted here
under whatever its leading segments claim.

**WHAT THAT COSTS HERE IS A MISCOUNTED BUCKET AND NOTHING ELSE**, and the
reason is structural rather than lucky: no href read on this page is ever
returned, navigated to, or built into a url. The only address this module
produces comes from :func:`group_page_url`, which is a template filled from a
value already proven to be ten-ASCII-digit only. A traversal on the page can
move one integer; it cannot move this process anywhere.

Closing it properly means a dot rule in the shipped classifier, which is an
edit to a script three other readers run and is not this row's to make.

## IT FIRES NOTHING

No function here presses, submits, joins, leaves, posts or takes a confirm
token. ``/groups/<id>/invite/`` is refused twice over by the read boundary and
is not reachable from anything in this file; joining a group (census ``N 163``,
``N 164``) still needs its own url, its own sanction entry and its own ruling,
exactly as the allowlist entry says.
"""

from __future__ import annotations

from typing import Any, Optional

from linkedin_server import anchors, coerce, groups, jobfilter

# NO URL PARSER IS IMPORTED HERE ON PURPOSE. ``groups.group_identifier`` is the
# one that reads a landing, and a second parser inside this module would be the
# two-guards-that-drift failure this repository has paid for twice.

#: The only host a group address may name.
_HOST = "www.linkedin.com"
_SCHEME_HOST = "https://" + _HOST

#: The one address form this package will ASSEMBLE for this surface, and the
#: only one the allowlist admits: ``/groups/<digits>/``. There is no slug form
#: to be tempted by -- the boundary refuses ``/groups/<slug>/`` outright.
_URL_TEMPLATE = _SCHEME_HOST + "/groups/{identifier}/"

#: THE LITERAL PUBLISHED IN PLACE OF AN HREF, taken from ``groups.py`` rather
#: than written again so the two surfaces cannot disagree about it. A "shape"
#: derived from the value would be a channel; a constant is not.
PUBLISHED_HREF = groups.PUBLISHED_HREF

#: THE TEN ASCII DIGITS, WRITTEN OUT, because ``str.isdigit()`` is not this and
#: neither is ``\\d``. Restated from ``groups.py`` the way ``company_page.py``
#: restates it, and ``tests/test_group_page.py`` couples the two so a change in
#: either lands as a red rather than as a boundary that opens an address its
#: own shaper then refuses.
_ASCII_DIGITS = frozenset("0123456789")

#: THE BOUND, AND IT IS ``groups.py``'s NUMBER RATHER THAN A NEW ONE. The
#: allowlist pattern is ``/groups/[0-9]{1,20}/?$`` and it says in its own words
#: that the bound is taken from that module: a cap here that disagreed would
#: open an address this builder refuses, or build one the boundary refuses.
MAX_IDENTIFIER_DIGITS = 20

#: THE CLOSED VERDICT ALPHABET. Every string :func:`reachability` can put in
#: its ``state`` field is a literal in this tuple.
#:
#: ``reader_blind`` IS FIRST for the reason ``member_profile`` is first in
#: ``anchors.ROUTE_CLASSES``: it is the class anything misclassified OUT OF is
#: the defect the rules exist to prevent. A blind reading reported as a fact
#: about the group is this repository's uninterpretable zero arriving again.
REACH_STATES: tuple[str, ...] = (
    "reader_blind",
    "off_group",
    "feed_drawn",
    "ambiguous",
)

#: The route classes this module lifts out of the shipped tally by NAME. They
#: are read from ``anchors.ROUTE_CLASSES`` at import so a rename there is a
#: red here rather than a silent zero.
_FEED_CLASS = "feed_update"
_MEMBER_CLASS = "member_profile"
_OTHER_CLASS = "other_internal"


def group_page_url(candidate: Optional[str]) -> dict[str, Any]:
    """The one group address this package will assemble, or a refusal.

    Returns::

        {"built": True,  "url": <url>, "identifier": <digits>}
        {"built": False, "refused": <reason>, "saw": <shape>, "why": ...}

    **THE REFUSAL REPORTS A SHAPE AND NEVER THE VALUE.** ``jobfilter.py`` ruled
    this on the company surface and the reasoning imports unchanged: the
    overwhelmingly likely wrong value is a group SLUG, and *a group named after
    a person gets that person's name in its slug*. A rule-following refusal
    spelling ``got {candidate!r}`` would publish that name on the single most
    probable mistake.

    **THE CHARACTER CHECK RUNS BEFORE THE LENGTH CHECK**, which is not
    cosmetic: ``company_page.company_identifier``'s own test caught the other
    order answering the commonest wrong input with ``identifier_too_long`` --
    true, and the wrong diagnosis. What a caller needs to be told is *that is a
    name, not an id*.

    IT NEVER RAISES. A refusal is a return value here, so no candidate can
    leave this process inside an exception message.
    """
    text = str(candidate or "").strip()
    if not text:
        return {
            "built": False,
            "refused": "no_identifier",
            "saw": jobfilter.describe_shape(text),
            "why": (
                "a group cannot be addressed by an empty value, and this gate "
                "refuses what it cannot establish."
            ),
        }
    if not set(text) <= _ASCII_DIGITS:
        return {
            "built": False,
            "refused": "identifier_is_not_numeric",
            "saw": jobfilter.describe_shape(text),
            "why": (
                "a group segment that is not a bounded run of the TEN ASCII "
                "DIGITS is a SLUG, and a slug is a name -- a group named "
                "after a person gets that person's name in its slug. The ten "
                "are named explicitly because str.isdigit() is true of "
                "several other scripts' digits as well, and the read "
                "allowlist spells this segment [0-9] for the same reason."
            ),
        }
    if len(text) > MAX_IDENTIFIER_DIGITS:
        return {
            "built": False,
            "refused": "identifier_too_long",
            "saw": jobfilter.describe_shape(text),
            "why": (
                "a digit run longer than "
                f"{MAX_IDENTIFIER_DIGITS} characters is not a LinkedIn group "
                "id, and an unbounded repetition on caller-shaped input is a "
                "cost nobody chose. The bound is the read allowlist's own, so "
                "a longer run would build an address the boundary refuses."
            ),
        }
    return {
        "built": True,
        "url": _URL_TEMPLATE.format(identifier=text),
        "identifier": text,
    }


def landed_on_the_same_group(
    landed: Optional[str], identifier: Optional[str]
) -> Optional[bool]:
    """Did the navigation stay on the group it was sent to? A BOOLEAN.

    ``None`` means the question could not be answered -- the landing carries no
    group identifier at all, which is what an auth wall, a redirect to the feed
    and a LinkedIn error page all look like from here.

    **THE LANDING IS NEVER PUBLISHED AND NEVER COMPARED AS A STRING.** It is
    run through ``groups.group_identifier``, which discards the query first,
    refuses a path carrying both a group and a member segment as FOREIGN, and
    returns a bounded digit run or a refusal. Two digit runs are compared; the
    url itself does not leave this function.

    A LinkedIn group address carries an invitation token in its query --
    ``/groups/<id>/?invitedBy=<token>`` -- which is precisely the direct-link
    half of census row ``N 175``, and it is dropped before anything reads it.
    """
    if not identifier:
        return None
    verdict = groups.group_identifier(landed)
    if not verdict.get("identified"):
        return None
    return str(verdict.get("identifier")) == str(identifier)


async def read_group_page(page: Any, html: str = "") -> dict[str, Any]:
    """Classify a group page's anchors. Returns COUNTS and integers.

    THE ONLY FUNCTION HERE THAT TOUCHES A PAGE, and it touches it through
    ``anchors.read_anchors`` rather than through a script of its own -- see the
    module docstring. What crosses the boundary back is the shipped reader's
    own integer payload plus three counts lifted out of it by class NAME.

    ``html`` IS THE CONTROL PATH and is not a reading of anything: it runs the
    same classifier against a detached container, so ``anchors.control_fixture``
    can prove the classifier works without a navigation. It is a parameter of
    the READER and never of :func:`reachability`.

    ``values_refused`` IS A FINDING RATHER THAN A SHAPE. It is normally 0; a
    nonzero means the page answered a count slot with something that is not a
    number, and it is reported as an integer precisely because the value that
    caused it may be a name. Nothing here coerces with ``int()``:
    ``coerce.as_int`` never raises and never quotes its input, and an exception
    is not a return value.
    """
    reading = await anchors.read_anchors(page, html=html or "")
    source = reading if isinstance(reading, dict) else {}
    counts, counts_refused = coerce.counts_only(source.get("counts"))
    scalars, scalars_refused = coerce.scalars_only(
        source,
        (
            ("anchors_seen", "anchors_seen"),
            ("numeric_entity", "numeric_entity"),
            ("non_numeric_entity", "non_numeric_entity"),
            ("classifier_values_refused", "values_refused"),
        ),
    )
    by_class = anchors.tally(counts)["by_class"]
    return {
        "anchors_seen": scalars["anchors_seen"],
        "counts": counts,
        # THE KEY FOR THE LIST ABOVE, and it travels WITH it rather than being
        # left for a caller to look up. ``counts`` is positionally aligned to
        # ``anchors.ROUTE_CLASSES``, and a positional list published without
        # its alphabet is a reading nobody can interpret -- which is one step
        # from a reading somebody interprets WRONGLY. Every entry is a literal
        # this package declares; no page string is in it.
        "counts_are_positions_in": list(anchors.ROUTE_CLASSES),
        # THE THREE THAT ANSWER THE ROW. Lifted by NAME from the shipped
        # alphabet, so a rename in anchors.py is a KeyError-shaped zero here
        # and the coupling test is what says so.
        "feed_update_anchors": by_class.get(_FEED_CLASS, 0),
        "member_profile_anchors": by_class.get(_MEMBER_CLASS, 0),
        "other_internal_anchors": by_class.get(_OTHER_CLASS, 0),
        "numeric_entity": scalars["numeric_entity"],
        "non_numeric_entity": scalars["non_numeric_entity"],
        "values_refused": (
            counts_refused
            + scalars_refused
            + scalars["classifier_values_refused"]
        ),
    }


def reachability(
    reading: Optional[dict[str, Any]],
    same_group: Optional[bool] = None,
) -> dict[str, Any]:
    """Did the direct link REACH the group? A token, a boolean and a why.

    **A NEEDLE HANDED HERE DOES NOTHING AND LEAVES NOTHING.** A caller CAN
    pass a string -- Python has no way to stop it -- and what happens then is
    that the argument fails an ``isinstance`` check and every field inside it
    goes through ``coerce.as_int``, so it can neither be read nor echoed nor
    raised. Stated as a claim about BEHAVIOUR rather than about the signature,
    because the previous wording ("cannot reach it even by mistake") was true
    of the signature and false of the mechanism: the argument RAISED on a bare
    string until a cold review drove one through it.

    ``reached`` is a THREE-VALUED answer and the third value is the point:

    ``True``   the feed rendered. The direct link reached a group whose posts
               this account can see, which is the positive half of ``N 175``.
    ``False``  the navigation did not stay on the group it was sent to.
    ``None``   unanswerable from this reading, and it stays unanswerable.

    **``ambiguous`` IS NOT A HEDGE.** A membership gate, an empty group and a
    restyle that moved the post permalink are all a rendered page with no
    ``/feed/update/`` anchor on it, and there is no known-gated group id in
    this repository to calibrate against. ``groups_page.interpret_zero`` refuses
    the same branch on the same grounds; picking the flattering one here would
    assert that a private group was reached on the evidence that nothing was.
    """
    # ``isinstance`` BEFORE ``dict()``. This read ``dict(reading or {})``,
    # which RAISES on a bare int, bool or string -- in a function whose own
    # docstring says a needle cannot reach it. Every FIELD was coerced and the
    # ARGUMENT itself was not. Found by a cold review, and repaired in
    # ``company_root.connection_counts`` in the same edit so the two cannot
    # disagree about it.
    seen = reading if isinstance(reading, dict) else {}
    anchors_seen = coerce.as_count(seen.get("anchors_seen"))
    feed = coerce.as_count(seen.get("feed_update_anchors"))
    members = coerce.as_count(seen.get("member_profile_anchors"))

    if same_group is False:
        return {
            "state": "off_group",
            "reached": False,
            "why": (
                "the navigation did not stay on the group it was sent to. A "
                "reading taken after a redirect is a reading of some other "
                "page, and this one is refused rather than attributed to the "
                "group in the request. The landing is not published: it is "
                "reduced to a bounded digit run and compared as one."
            ),
        }

    if anchors_seen <= 0:
        return {
            "state": "reader_blind",
            "reached": None,
            "why": (
                "the page drew no anchor at all, so this reading is a fact "
                "about the READER and not about the group. A page that had "
                "not hydrated, a session that is not signed in and a restyle "
                "all land here, and not one of them is evidence about the "
                "group in either direction."
            ),
        }

    if feed > 0:
        return {
            "state": "feed_drawn",
            "reached": True,
            "why": (
                "%d feed permalink(s) rendered beside %d member anchor(s), so "
                "the group feed drew and the direct link REACHED a group this "
                "account can see. Nothing about what the posts say is read: "
                "the classifier answers with a position in a table this "
                "package defines." % (feed, members)
            ),
        }

    return {
        "state": "ambiguous",
        "reached": None,
        "why": (
            "the page rendered %d anchor(s) and NOT ONE post permalink. That "
            "is what a membership gate produces, AND what an empty group "
            "produces, AND what a restyle that moved the permalink "
            "produces -- and nothing here can separate them, because there is "
            "no known-gated group to test this reader against. Reported as "
            "AMBIGUOUS and never as a group that was reached or refused."
            % anchors_seen
        ),
    }


def term_for(index: int) -> str:
    """One index -> one literal. Out of range REFUSES rather than clamping.

    A clamp would silently rename one verdict to another -- and index 0 is
    ``reader_blind``, so a clamp could rename "the page drew nothing" into "the
    group was reached". Never clamped.
    """
    if 0 <= index < len(REACH_STATES):
        return REACH_STATES[index]
    return "index_out_of_range"


def emitted_alphabet() -> frozenset[str]:
    """Every ``state`` token this module can publish, plus the refusals.

    The ``why`` field is prose this module authored with integers interpolated
    into it; ``tests/test_group_page.py`` drives the whole module with a planted
    name and asserts it reaches no field, which is the property that matters
    and is stronger than an alphabet over one key.
    """
    return frozenset(REACH_STATES) | {
        "index_out_of_range",
        "no_identifier",
        "identifier_is_not_numeric",
        "identifier_too_long",
    }


def route_classes_this_reader_depends_on() -> tuple[str, ...]:
    """The three ``anchors.ROUTE_CLASSES`` names lifted out by this module.

    Exported so the coupling can be ASSERTED rather than described: a rename in
    ``anchors.py`` silently turns every lifted count into a zero, which is the
    quiet direction, and ``tests/test_group_page.py`` is what makes it loud.
    """
    return (_MEMBER_CLASS, _FEED_CLASS, _OTHER_CLASS)


