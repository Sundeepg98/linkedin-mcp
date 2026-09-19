"""The page reader ``groups.py`` was missing, and the cost verdict it cannot earn.

``linkedin_server/groups.py`` is a SHAPER: counts and identifiers and no
names, taking hrefs somebody else read. It shipped 2026-09-05 with no page
reader, so nothing in this package could call it and no tool could reach the
one question ``/groups/`` was admitted to answer -- *does he belong to any
group?* This module is that reader.

## WHY IT IS NOT IN ``dom.py``, AND THE REASON IS NOT TIDINESS

Every previous split of a reader out of ``dom.py`` was a concurrency artefact
and said so. **This one is a safety argument and it should not be undone
casually.**

``server.py`` lifts ``linkedin_publish_post``'s audience refusal by FEATURE
DETECTION -- ``callable(getattr(dom, "read_post_composer_audience", None))``.
It is the only feature-detection site in the package and it keys on ``dom``
alone, so **defining a function on that module can re-arm an irreversible
broadcast.** A reader that does not need to be there should not be there.

The reader did not need to be there because of the next section.

## LOCATOR-ONLY. THE WALK CARRIES NO ``page.evaluate`` WAIVER.

The validated split of this page was written as a script evaluated IN the
page, and ``page.evaluate`` is confined to ``dom.py`` behind an explicit
waiver. **The waiver turned out to be unnecessary**: Playwright's ``xpath=..``
parent step expresses the same climb, and the locator version reproduced the
validated reading exactly on its first live run -- five memberships, five
others, zero identifiers in common, on the real page.

That was not assumed. ``scripts/_probe_groups_locator_walk.py`` refuses to
publish any split that does not reproduce FIVE, precisely because the cheap
wrong answer here is TEN.

## THE RULE, AND WHY THE OBVIOUS READER IS WRONG

    Start at the CONTROL, never at the anchor. Climb parents. The first
    ancestor holding at least one group anchor is the STOPPING ANCESTOR. The
    control QUALIFIES only if that ancestor holds EXACTLY ONE, and that anchor
    is a MEMBERSHIP. Every other group anchor is a suggestion or the root.

**A flat sweep of every group anchor answers TEN to a question whose answer is
FIVE**, in the flattering direction, because LinkedIn draws suggestions on the
same page with the same kind of anchor. ``groups.disjoint`` existing at all is
the design saying it expects two lists.

**AND THE RULE IS NOT SYMMETRIC.** Run from the anchor instead of the control
it resolves ZERO rows -- measured, on the same page, in the same hour, by a
sibling probe. The first ancestor holding exactly one group anchor is not a
definition of A ROW; it is a definition of the smallest element containing
what you started from, and the two coincide only when the start point sits
outside the anchor's own subtree.

## WHAT THIS MODULE MAY SAY

Counts, distinct counts, overlap and the numeric identifiers. **No name.** The
signature is the property: :func:`read_group_memberships` takes a page and
nothing else, and every href it collects leaves through
``groups.membership_tally``, which is never handed a name by construction.
There is no filter here to have got wrong, which is the point of the ruling
this reader implements.

## THE COST, AND THIS MODULE REFUSES TO PRETEND IT MEASURED ONE

A wave declined to build this reader on the grounds that *a groups tool cannot
certify its own cost from the page it loads*. **That reasoning is sound and
its conclusion was one step too far.** ``linkedin_notify_cost_precondition``
reads a badge on ``/feed/`` to say something about ``/notifications/``;
bracketing a load with a reading taken ELSEWHERE is this package's established
pattern, not a workaround.

So :func:`cost_certification` takes nav-badge readings from a page that
carries them and returns one of four verdicts. **Two of them are honest
refusals to claim a measurement**, and they exist because of the trap written
down at ``shape.invitation_badge``:

    a badge sitting at zero cannot distinguish "the page consumed nothing"
    from "there was nothing to consume".

    uncertified   a reading failed. Nothing is said in either direction.
    moved         a counter moved across the load. Something WAS spent.
    degenerate    every readable counter sat at ZERO and did not move. This
                  is NOT evidence the load is free.
    unmoved       a counter stood ABOVE zero and did not move. This is the
                  only verdict that certifies anything, and it certifies it
                  about THAT COUNTER ONLY.

**AND THERE IS A SECOND LAYER OF UNMEASURABILITY ABOVE THE ZERO, which no
future non-zero badge repairs.** The counters this package can read are nav
badges for OTHER surfaces -- pending invitations and unread notifications.
Nothing measured anywhere says a ``/groups/`` load touches either. So even
``unmoved`` on a non-zero badge certifies only that *the counters it names did
not move*, and says nothing about a groups-specific cost, because **this
server holds no instrument that is known to respond to the event being
bracketed.** That is stated in the payload rather than left for a caller to
work out, and it is why the verdict field is never a bare boolean.

**THAT SENTENCE ORIGINALLY NAMED THE INVITATION COUNTER ALONE**, written
before the first live run, and the run made it wrong in a small and
instructive way: the verdict that came back was carried by the NOTIFICATIONS
counter. The wording is generic now because the limit is about the CLASS --
every counter here belongs to another surface -- and naming one instance made
it read as a fact about that instance.
"""
from __future__ import annotations

from typing import Any, Optional

from linkedin_server import groups
from linkedin_server.config import BASE_URL

#: The one address this reader opens, and it is already on the read allowlist.
#: Anchored, no query and no sub-path -- ``/groups/<id>/`` and
#: ``/groups/discover/`` are named refusals in ``readonly.py``'s own comment.
GROUPS_URL = f"{BASE_URL}/groups/"

#: The anchor aim, and it is deliberately LOOSER than the rule it serves.
#:
#: A CSS attribute-substring match, so a href carrying the segment in a QUERY
#: matches here where a pathname rule would not. Safe in this direction only:
#: this aim decides which elements are CANDIDATES, and every survivor is
#: re-parsed by ``groups.group_identifier`` with ``urlsplit``, which drops the
#: query before anything is read and refuses a path with no group segment. The
#: loose half can over-collect; it cannot publish.
ANCHOR = 'a[href*="/groups/"]'

#: The control that marks a membership row. A DISCLOSURE, not a label: this
#: surface draws no ``[role=menu]`` content at all, so the aim is the
#: ``aria-expanded`` attribute and never a word LinkedIn chose.
CONTROL = "button[aria-expanded]"

#: How far up to climb before abandoning a control.
#:
#: BOUNDED, and the bound is reported rather than swallowed. An unbounded
#: climb on a page nobody has re-measured today is a cost nobody chose; 40 is
#: far deeper than any row wrapper measured on this surface, and a control
#: that exhausts it lands in ``climbs_exhausted`` so a page restyle shows up
#: as a number instead of as a quietly smaller tally.
MAX_CLIMB = 40

#: What four independent instruments say this account's page holds. Not a
#: filter and not an assertion -- it travels in the payload so a caller can
#: see at a glance whether this reading agrees with the ones that came before.
#: A different number is a finding about the READER until shown otherwise.
CORROBORATED_MEMBERSHIPS = 5


async def _stopping_ancestor(control: Any) -> tuple[Optional[Any], int, int]:
    """The first ancestor of ``control`` holding at least one group anchor.

    Returns ``(locator_or_None, anchors_in_it, depth_climbed)``.

    LOCATORS ONLY -- ``xpath=..`` is Playwright's parent step and no script is
    evaluated in the page. That is the entire reason this module exists
    outside ``dom.py``; see the module docstring.
    """
    node = control
    for depth in range(1, MAX_CLIMB + 1):
        node = node.locator("xpath=..")
        try:
            found = int(await node.locator(ANCHOR).count())
        except Exception:  # noqa: BLE001 - climbed off the top of the document
            return None, 0, depth
        if found >= 1:
            return node, found, depth
    return None, 0, MAX_CLIMB


async def read_group_memberships(page: Any) -> dict[str, Any]:
    """Split an already-open Groups page into memberships and everything else.

    **TAKES A PAGE AND NOTHING ELSE.** No name is a parameter of this function
    and none is a parameter of anything it calls, which is the ruling
    ``groups.py`` was written to implement, inherited rather than restated.

    ASSUMES THE PAGE IS ALREADY ON :data:`GROUPS_URL`. It navigates nowhere --
    navigation and the cost bracket around it belong to the caller, because
    the caller is the one that can read a counter on a DIFFERENT page.

    Returns counts, the two tallies, the overlap, and the diagnostics that
    make a wrong number legible:

    ``anchors``/``controls``      what the page drew
    ``rows_found``                controls whose stopping ancestor held one
    ``rows_not_row_scoped``       controls scoped to a block or the page
    ``climbs_exhausted``          controls that hit :data:`MAX_CLIMB`
    ``stopping_widths``           anchors-per-stopping-ancestor histogram
    ``memberships``/``others``    ``groups.membership_tally`` on each list
    ``overlap``                   ``groups.disjoint`` on the pair
    ``agrees_with_corroborated``  whether ``distinct`` is
                                  :data:`CORROBORATED_MEMBERSHIPS`

    **THE HISTOGRAM IS NOT DECORATION.** The discriminating fact on this
    surface is that suggestions get list-level controls and only memberships
    get a per-row one, so a page restyle that broke the rule would show up as
    the widths collapsing rather than as a plausible different number.

    IT NEVER RAISES ON A ROW IT CANNOT READ. One unusable anchor on a page of
    thirty is not an error, and ``groups.group_identifier`` already reports
    what it refused and why.

    **A NON-ZERO ``overlap.in_common`` IS NOT AUTOMATICALLY A DEFECT, AND THE
    TEMPTING FIX WOULD DESTROY THE MEASUREMENT.** The two lists are separated
    by HREF STRING, not by identifier, so a group LinkedIn writes twice on one
    page -- once relative, once absolute -- puts one copy in each list and
    reports itself as one group in common. De-duplicating across the lists by
    identifier would make that disappear.

    It must not, because ``in_common`` is the DISCRIMINATING measurement on
    this surface: it is what says the two sections are two sets rather than
    one set drawn twice, which is the whole reason ``groups.disjoint`` exists.
    A cross-list de-duplication would guarantee zero overlap by construction
    and turn the deciding number into a constant -- an instrument reporting
    its own shape.

    So the overlap is reported RAW and a reader investigates. Measured zero on
    this account at both live runs; if it ever reads non-zero, the question is
    *did LinkedIn draw one group in both sections, or write one row's href
    twice*, and that is answerable by looking rather than by patching this.
    """
    anchors = page.locator(ANCHOR)
    total = int(await anchors.count())
    all_hrefs: list[str] = []
    for index in range(total):
        all_hrefs.append(
            str(await anchors.nth(index).get_attribute("href") or "")
        )

    controls = page.locator(CONTROL)
    control_count = int(await controls.count())

    with_control: list[str] = []
    rows_found = 0
    rows_not_scoped = 0
    climbs_exhausted = 0
    stopping_widths: dict[int, int] = {}

    for index in range(control_count):
        row, found, _depth = await _stopping_ancestor(controls.nth(index))
        if row is None:
            climbs_exhausted += 1
            continue
        stopping_widths[found] = stopping_widths.get(found, 0) + 1
        if found != 1:
            rows_not_scoped += 1
            continue
        rows_found += 1
        with_control.append(
            str(await row.locator(ANCHOR).first.get_attribute("href") or "")
        )

    # EVERYTHING ELSE = every anchor MINUS one occurrence per claimed href.
    # A COUNT subtraction, not a set difference: a page drawing the same group
    # twice loses one copy rather than both, and two controls resolving to one
    # anchor are COUNTED rather than silently merged -- a row drawing two
    # disclosures is a fact about the page a reader should be able to see.
    remaining = list(all_hrefs)
    rows_sharing_an_anchor = 0
    claimed: list[str] = []
    for href in with_control:
        if href in remaining:
            remaining.remove(href)
            claimed.append(href)
        else:
            rows_sharing_an_anchor += 1

    memberships = groups.membership_tally(claimed)
    others = groups.membership_tally(remaining)
    overlap = groups.disjoint(claimed, remaining)

    reading = {
        "anchors": total,
        "controls": control_count,
        "rows_found": rows_found,
        "rows_not_row_scoped": rows_not_scoped,
        "climbs_exhausted": climbs_exhausted,
        "rows_sharing_an_anchor": rows_sharing_an_anchor,
        "stopping_widths": stopping_widths,
        "memberships": memberships,
        "others": others,
        "overlap": overlap,
        "corroborated_memberships": CORROBORATED_MEMBERSHIPS,
        "agrees_with_corroborated": (
            memberships["distinct"] == CORROBORATED_MEMBERSHIPS
        ),
    }
    reading["zero_reading"] = interpret_zero(reading)
    return reading


def interpret_zero(reading: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Is a membership count of ZERO about the ACCOUNT or about this READER?

    **THE QUESTION THE NEWSLETTER TOOL ASKS WITH ``heading_seen``, ASKED HERE
    BECAUSE THIS SURFACE NEEDS IT MORE.** A zero from a reader that could not
    see is a fact about the instrument; a zero from a reader that could is a
    fact about the account. They never share a field, and a caller that
    reports the first when it measured the second has answered the question
    backwards -- which is a defect this repository has now recorded on three
    separate surfaces.

    ``state`` is one of:

    ``not_zero``      memberships were found. Nothing to interpret.
    ``instrument``    the page drew no group anchor, or no disclosure control,
                      or the climb exhausted its bound. The reader could not
                      see, so the zero says nothing about his memberships.
    ``ambiguous``     the walk ran cleanly over real anchors and real controls
                      and resolved no row-scoped control.

    **``ambiguous`` IS THE HONEST ANSWER AND IT IS NOT A HEDGE.** It is what a
    genuinely group-less account would look like -- LinkedIn draws suggestion
    rows with no per-row control, so a page of suggestions alone produces
    exactly this reading -- AND it is what a LinkedIn restyle that moved the
    control would look like. **Nobody here can separate them, because there is
    no known-empty groups account to test the reader against.** That is the
    same shape as the freeze ruling's note about the profile's Groups tab: a
    reading no instrument can fail is not a reading, and the correct response
    is to say so rather than to pick the flattering branch.

    IT NEVER ASSERTS THE ACCOUNT HAS NO GROUPS. There is no branch that says
    that, on purpose, for exactly the reason above.
    """
    seen = dict(reading or {})
    memberships = dict(seen.get("memberships") or {})
    distinct = memberships.get("distinct")
    anchors = seen.get("anchors")
    controls = seen.get("controls")
    exhausted = seen.get("climbs_exhausted")

    if distinct:
        return {
            "state": "not_zero",
            "about_the_account": None,
            "why": (
                "%d distinct memberships were resolved, so there is no zero "
                "to interpret." % int(distinct)
            ),
        }

    blind: list[str] = []
    if not anchors:
        blind.append("the page drew no anchor carrying a group segment")
    if not controls:
        blind.append("the page drew no control declaring aria-expanded")
    if exhausted:
        blind.append(
            "%d control(s) exhausted the %d-level climb bound"
            % (int(exhausted), MAX_CLIMB)
        )
    if blind:
        return {
            "state": "instrument",
            "about_the_account": False,
            "why": (
                "this zero is a fact about the READER, not about his "
                "memberships: " + "; ".join(blind) + ". A page that had not "
                "hydrated, a restyle, or a wrong aim all land here, and not "
                "one of them is evidence about his account in either "
                "direction."
            ),
        }
    return {
        "state": "ambiguous",
        "about_the_account": None,
        "why": (
            "the walk ran cleanly over %s anchor(s) and %s control(s) with no "
            "climb exhausted, and resolved no row-scoped control. That is "
            "what an account with no groups looks like AND what a restyle "
            "that moved the per-row control looks like, and NOTHING HERE CAN "
            "SEPARATE THEM -- there is no known-empty groups account to test "
            "this reader against. So this is reported as AMBIGUOUS and never "
            "as a membership count about the account." % (anchors, controls)
        ),
    }


def cost_certification(
    before: Optional[dict[str, Any]], after: Optional[dict[str, Any]]
) -> dict[str, Any]:
    """What a pair of nav-counter readings can and cannot say about a load.

    ``before`` and ``after`` are mappings of ``{counter_name: reading}``, each
    reading being the parsed shape its own module produces -- a ``state`` of
    ``"read"`` plus a count under ``pending`` or ``unread``. Taking the whole
    parsed reading rather than a bare number is the argument
    ``shape.invitation_badge`` already makes: *unreadable* and *zero* are
    different answers and a function handed an integer could not tell them
    apart.

    FOUR VERDICTS, and only one of them certifies anything:

    ``uncertified``  a counter present in one half is missing or unreadable in
                     the other. A pair with a missing half is not a pair.
    ``moved``        a counter moved. Something was spent, and it is named.
    ``degenerate``   every readable counter sat at ZERO and stayed there. A
                     ``0 -> 0`` pair cannot distinguish "consumed nothing"
                     from "nothing to consume", so this is **UNMEASURABLE**
                     and is not reported as a cost of zero.
    ``unmoved``      at least one counter stood ABOVE zero and did not move.

    **``unmoved`` IS STILL NOT A CLEAN BILL, and the payload says so in
    ``certifies``.** Every counter this package can read is a nav badge for a
    DIFFERENT surface -- pending invitations, unread notifications. Nothing
    measured anywhere establishes that a ``/groups/`` load touches either. So
    the strongest available verdict certifies that THOSE COUNTERS did not
    move, and a caller must not read it as "this load costs nothing".

    **A SILENT ZERO IS THE FAILURE MODE THIS FUNCTION EXISTS TO PREVENT.**
    There is no branch that returns a cost of zero.

    **WHY TWO COUNTERS AND NOT ONE, and this was decided before the run that
    vindicated it.** The invitation badge is known to sit at zero on this
    account, so a bracket built on it alone is degenerate by construction --
    it would report UNMEASURABLE every time and could never do anything else.
    Adding the notifications badge costs nothing (both render on the same nav
    of the same already-loaded page) and gives the pair a chance of carrying
    information. Measured on the first live run: invitations 0 -> 0
    (degenerate), notifications 1 -> 1 (unmoved above zero). **The cheapest
    repair for a degenerate instrument is a SECOND instrument, not a better
    argument about the first.**
    """
    seen_before = dict(before or {})
    seen_after = dict(after or {})
    names = sorted(set(seen_before) | set(seen_after))

    counters: dict[str, Any] = {}
    unreadable: list[str] = []
    movedlist: list[str] = []
    above_zero_unmoved: list[str] = []
    zero_unmoved: list[str] = []

    for name in names:
        b = dict(seen_before.get(name) or {})
        a = dict(seen_after.get(name) or {})
        b_value = b.get("pending", b.get("unread"))
        a_value = a.get("pending", a.get("unread"))
        b_ok = b.get("state") == "read" and b_value is not None
        a_ok = a.get("state") == "read" and a_value is not None
        entry = {
            "before_state": b.get("state"),
            "after_state": a.get("state"),
            "before": b_value if b_ok else None,
            "after": a_value if a_ok else None,
        }
        if not b_ok or not a_ok:
            entry["verdict"] = "unreadable"
            unreadable.append(name)
        elif b_value != a_value:
            entry["verdict"] = "moved"
            movedlist.append(name)
        elif int(b_value) > 0:
            entry["verdict"] = "unmoved_above_zero"
            above_zero_unmoved.append(name)
        else:
            entry["verdict"] = "unmoved_at_zero"
            zero_unmoved.append(name)
        counters[name] = entry

    # A MOVE OUTRANKS EVERYTHING. Something was spent and that is the finding,
    # whatever the other counters did.
    if movedlist:
        return {
            "state": "moved",
            "measured": True,
            "certifies": None,
            "counters": counters,
            "why": (
                "these counters moved across the load: %s. Something was "
                "consumed. The values are recorded above -- this is the "
                "measurement the surface has been waiting for, and it should "
                "not be discarded as a failure." % ", ".join(movedlist)
            ),
        }
    if not names or unreadable:
        return {
            "state": "uncertified",
            "measured": False,
            "certifies": None,
            "counters": counters,
            "why": (
                "no before/after pair is constructible for %s, so nothing is "
                "said in either direction. An unreadable counter is NOT a "
                "counter at zero." % (", ".join(unreadable) or "any counter")
            ),
        }
    if above_zero_unmoved:
        return {
            "state": "unmoved",
            "measured": True,
            "certifies": (
                "these counters stood above zero and did not move: %s. That "
                "is ALL this certifies. Every counter this package can read "
                "is a nav badge for a DIFFERENT surface, and nothing "
                "measured establishes that a groups load touches one, so "
                "this is not a statement that the load is free."
                % ", ".join(above_zero_unmoved)
            ),
            "counters": counters,
            "why": (
                "at least one counter had something to lose and did not lose "
                "it, which is the only reading in this family that carries "
                "information."
            ),
        }
    return {
        "state": "degenerate",
        "measured": False,
        "certifies": None,
        "counters": counters,
        "why": (
            "every readable counter (%s) sat at ZERO and stayed there. A "
            "0 -> 0 pair cannot distinguish 'the load consumed nothing' from "
            "'there was nothing to consume', so THE COST OF THIS LOAD IS "
            "UNMEASURABLE TODAY and is reported as such rather than as zero. "
            "This is a fact about THIS ACCOUNT TODAY and reverses the moment "
            "one invitation or one notification arrives -- and even then it "
            "would only speak for that counter."
            % ", ".join(zero_unmoved)
        ),
    }
