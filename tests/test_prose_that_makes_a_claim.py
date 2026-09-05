"""Three guards on prose that makes a DERIVABLE claim, added 2026-09-01.

All three exist for one finding, and it is the one this wave ends on: A CHECK
THAT COULD NOT PASS IS INDISTINGUISHABLE FROM ONE THAT HAS NOT PASSED YET --
and its twin, which is worse, that a CLAIM of being checked is worth less than
nothing when it is the thing stopping somebody from checking.

Each of the three is a real drift that shipped, not a hypothetical:

1. ``server.py``'s module docstring said "THE NUMBERS ABOVE ARE DERIVED, not
   counted by hand" while NOTHING compared those words to anything. It named
   two pins and both were real -- one pinned ``len(tools)`` to the literal 33,
   the other pinned the INSTRUCTIONS string -- and neither read the docstring.
   So when ``update_setting`` entered ``writes.PERFORMABLE`` on 2026-08-31 the
   instructions correctly said SIX and the docstring went on saying FIVE, with
   a sentence on top asserting that it could not.

2. The census tool's description said "one of these five" while eight keys
   existed, and was then corrected to a NINE that named the WRONG NINE --
   listing ``feed_item`` while omitting ``feed_item_commented`` and
   ``premium``. THE COUNT WAS RIGHT AND THE MEMBERSHIP WAS WRONG, which is
   why the test below checks membership rather than a number: a reader
   counting nine names against a stated nine finds nothing to doubt.

3. Three refusal texts told callers that the item permalink was on the
   forbidden-url list, for a day and a half after the boundary was
   deliberately opened to it -- on a server that was opening it. That is the
   general form: A REFUSAL INHERITED FROM A NEIGHBOURING ADDRESS IS NOT A
   MEASUREMENT OF THAT ADDRESS, and it stays uncorrected precisely because a
   refusal is the text nobody re-reads.

WHY THESE ARE IN THEIR OWN FILE. They are not tests of the tool surface, they
are tests of DOCUMENTATION AGAINST CODE, and the mutation that breaks each of
them is an edit to prose. Keeping them together means the next person to
reword one of those paragraphs meets all three at once.
"""

import re

import pytest

from linkedin_server import readonly, server, writes
from linkedin_server.server import mcp

_NUMBER_WORDS: dict[str, int] = {
    # ZERO, ADDED 2026-09-02, and it is not filler. The docstring's third
    # column -- write-shaped, registered, gated, unable to act -- EMPTIED when
    # send_message shipped, and this table could not spell the number, so the
    # check raised KeyError instead of comparing. A vocabulary that cannot say
    # "none" cannot verify a claim that something is none, which is the claim
    # most worth verifying on a surface that gates writes.
    "zero": 0,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "twenty-one": 21, "twenty-two": 22, "twenty-three": 23,
    # TWENTY-FOUR, ADDED 2026-09-03 with the twenty-fourth read tool. The
    # table has to be able to SAY a number before it can check a claim
    # about it -- a missing word raises KeyError, which reads as a broken
    # test rather than as a moved number.
    "twenty-four": 24,
    # TWENTY-FIVE and THIRTY-SEVEN, added 2026-09-05 with
    # ``linkedin_search_appearances``. Same reason as the note above, and it
    # bit exactly as predicted: the first run after registering the tool
    # failed with ``KeyError: 'thirty-seven'``, which says nothing about the
    # docstring being wrong and everything about this table being short.
    "twenty-five": 25,
    "thirty-one": 31, "thirty-two": 32, "thirty-three": 33, "thirty-four": 34,
    "thirty-five": 35, "thirty-six": 36, "thirty-seven": 37,
}


@pytest.fixture
async def tools():
    return {t.name: t for t in await mcp.list_tools()}


def _word(n: int) -> str:
    """The spelling of a number, or a failure naming what to widen.

    Deliberately raises rather than returning ``str(n)``: a silent fallback to
    digits would let this file's own helper paper over a surface that grew
    past the table, which is the disease being treated.
    """
    for word, value in _NUMBER_WORDS.items():
        if value == n:
            return word
    raise AssertionError("no word for %d -- widen _NUMBER_WORDS" % n)


def _registered_write_tools(tool_names):
    """Sanctioned actions split by whether a TOOL is registered for them.

    Returns ``(performable, refusing, toolless)``. The third is not a leftover.
    ``set_open_to_work`` is sanctioned, is refused by ``_refuse_unperformable``
    and has NO registered tool, so ``len(SANCTIONED_WRITES)`` is THIRTEEN where
    the surface carries TWELVE write-shaped tools. The module docstring states
    that discrepancy out loud, so this derives it instead of assuming it.
    """
    performable, refusing, toolless = [], [], []
    for name, spec in writes.SANCTIONED_WRITES.items():
        if name not in tool_names:
            toolless.append(spec.action)
        elif spec.action in writes.PERFORMABLE:
            performable.append(spec.action)
        else:
            refusing.append(spec.action)
    return performable, refusing, toolless


async def test_the_server_docstring_numbers_are_derived(tools):
    """Every number ``server.py``'s docstring prints, checked against the registry.

    THE HEADLINE, THE THREE-WAY SPLIT AND THE SUM, all three, because the
    failure this replaces was a paragraph whose numbers added up correctly
    while disagreeing with the code. Arithmetic that is internally consistent
    is exactly what a hand-maintained count looks like just before it rots.
    """
    doc = " ".join((server.__doc__ or "").split())
    performable, refusing, toolless = _registered_write_tools(set(tools))
    reads = len(tools) - len(performable) - len(refusing)

    headline = re.search(r"([a-z-]+) tools, ([a-z-]+) of which write", doc)
    assert headline, "the headline sentence changed shape -- reword this test"
    assert _NUMBER_WORDS[headline.group(1)] == len(tools), (
        "the headline says %s tools, mcp.list_tools() returns %d"
        % (headline.group(1), len(tools))
    )
    assert _NUMBER_WORDS[headline.group(2)] == len(performable), (
        "the headline says %s write, writes.PERFORMABLE has %d"
        % (headline.group(2), len(performable))
    )

    # "is" AS WELL AS "are" SINCE 2026-09-02. The third column dropped to
    # ONE when update_profile_field shipped, and "one are write-shaped" is
    # not a sentence. The regex follows the prose rather than the prose
    # being bent to keep a regex happy -- a docstring written for a
    # matcher stops being written for a reader.
    split = re.search(
        r"([A-Z-]+) read, ([A-Z-]+) write, and ([A-Z-]+) (?:is|are) write-shaped",
        doc,
    )
    assert split, "the three-way split sentence changed shape"
    assert _NUMBER_WORDS[split.group(1).lower()] == reads, (
        "docstring says %s read, registry has %d" % (split.group(1), reads)
    )
    assert _NUMBER_WORDS[split.group(2).lower()] == len(performable), (
        "docstring says %s write, writes.PERFORMABLE has %d"
        % (split.group(2), len(performable))
    )
    assert _NUMBER_WORDS[split.group(3).lower()] == len(refusing), (
        "docstring says %s write-shaped and refusing, registry has %d"
        % (split.group(3), len(refusing))
    )

    total = re.search(
        r"([A-Za-z-]+) plus ([a-z-]+) plus ([a-z-]+) is ([a-z-]+)", doc
    )
    assert total, "the sum sentence changed shape"
    addends = [_NUMBER_WORDS[total.group(i).lower()] for i in (1, 2, 3)]
    assert sum(addends) == _NUMBER_WORDS[total.group(4).lower()], (
        "the sum sentence does not add up: %s" % total.group(0)
    )
    assert addends == [reads, len(performable), len(refusing)], (
        "the sum sentence adds up and disagrees with the registry: %s "
        "against read=%d write=%d refusing=%d"
        % (total.group(0), reads, len(performable), len(refusing))
    )


async def test_the_server_docstring_accounts_for_the_action_that_has_no_tool(tools):
    """The thirteen-versus-twelve claim is specific, so it is derived.

    Split from the numbers test on purpose. That one fails when a count rots;
    this one fails when a tool is registered for ``set_open_to_work``, or when
    a SECOND action loses its tool -- different events wanting different
    messages, and a single test reporting both teaches neither.
    """
    doc = " ".join((server.__doc__ or "").split())
    performable, refusing, toolless = _registered_write_tools(set(tools))

    assert toolless == ["set_open_to_work"], toolless
    assert len(performable) + len(refusing) + len(toolless) == len(
        writes.SANCTIONED_WRITES
    )
    assert "set_open_to_work" in doc
    assert _word(len(writes.SANCTIONED_WRITES)) in doc.lower()


async def test_the_census_description_lists_every_surface_it_answers_to(tools):
    """Every key the instrument accepts must be named in what a caller reads.

    MEMBERSHIP FIRST, count second, and that order is the whole lesson: the
    description was corrected once already, to a count that was right about a
    set that was wrong. A caller asking for ``premium`` was told by the
    docstring that no such surface exists while the server measured it happily.
    """
    # THE PARAMETER SCHEMA, not ``.description``. FastMCP lifts the Args block
    # out of the docstring and into the input schema, so the tool description a
    # client sees STOPS before the enumeration -- reading it would check a
    # paragraph that never contained the list, and pass forever.
    schema = tools["linkedin_surface_census"].parameters
    text = " ".join(schema["properties"]["surface"]["description"].split())
    keys = server.census_surface_keys()

    stated = re.search(
        r"A KEY, never a url, and one of these ([a-z-]+): (.+?)\. ", text
    )
    assert stated, "the enumeration sentence changed shape"
    assert _NUMBER_WORDS[stated.group(1)] == len(keys), (
        "the description says %r surfaces and the instrument answers to %d"
        % (stated.group(1), len(keys))
    )

    # THE CLAUSE, not the paragraph. A mutation that swapped "premium" out of
    # the list left this GREEN when it searched the whole description, because
    # a later sentence names "premium" in prose. Membership has to be tested
    # against the list itself or it is testing vocabulary.
    listed = set(re.findall(r'"([a-z_]+)"', stated.group(2)))
    assert listed == set(keys), {
        "named but not answered to": sorted(listed - set(keys)),
        "answered to but not named": sorted(set(keys) - listed),
    }


def _path_tokens(sentence: str) -> list[str]:
    """Every url PATH a sentence names, truncated at a ``<placeholder>``.

    ``/feed/update/<urn>/`` becomes ``/feed/update/``. The concrete prefix is
    the only part a SUBSTRING gate could ever match on, and the placeholder is
    the part that varies, so comparing the prefix is comparing the thing the
    boundary actually tests.
    """
    out = []
    for raw in re.findall(r"/[A-Za-z0-9_<>/.-]{2,}", sentence):
        token = raw.split("<")[0].rstrip(".,;:)")
        if len(token) > 1:
            out.append(token)
    return out


def _every_refusal_a_caller_can_receive() -> dict[str, str]:
    """The refusal text for each sanctioned action ``perform`` will not run.

    Collected by CALLING the refusal path, never by reading the table, so the
    one refusal written inline in ``_refuse_unperformable`` --
    ``set_open_to_work``, which has no ``_NINE_REFUSALS`` entry -- is covered
    like the rest. A guard that read only the table would be blind to exactly
    the entry the table forgot, which is the shape of every miss in this file.
    """
    texts = {}
    for spec in writes.SANCTIONED_WRITES.values():
        if spec.action in writes.PERFORMABLE:
            continue
        try:
            writes._refuse_unperformable(spec)
        except writes.WriteAttemptError as exc:
            texts[spec.action] = str(exc)
        else:  # pragma: no cover
            raise AssertionError(
                "%s is sanctioned, not performable, and did not refuse"
                % spec.action
            )
    return texts


def test_every_refusing_action_produces_text_to_check():
    """The guard below is worthless if its corpus is empty or short.

    A LOOP OVER NOTHING PASSES. This names the number so that an action losing
    its refusal, or the collector losing its way to one, fails HERE with a
    count rather than downstream with a green run over an empty corpus.
    """
    texts = _every_refusal_a_caller_can_receive()
    every = {s.action for s in writes.SANCTIONED_WRITES.values()}
    expected = len(writes.SANCTIONED_WRITES) - len(writes.PERFORMABLE)
    assert len(texts) == expected, (
        "collected %d refusals, expected %d -- missing: %s"
        % (len(texts), expected, sorted(every - set(writes.PERFORMABLE) - set(texts)))
    )
    assert "set_open_to_work" in texts
    assert all(len(t) > 200 for t in texts.values()), {
        k: len(v) for k, v in texts.items()
    }


def test_no_refusal_calls_a_path_forbidden_that_is_not_forbidden():
    """A refusal may not inherit its ground from a boundary that has moved.

    ``/feed/update`` was removed from ``_FORBIDDEN_URL_SUBSTRINGS`` on
    2026-08-31 -- the first removal this package has ever made -- and
    ``comment_on_item``, ``react_to_item`` and ``_WHY_NOT_PERFORMED`` went on
    telling callers the item permalink could not be opened.

    THE RULE IS DELIBERATELY NARROW so it cannot misfire on ordinary prose: if
    a SENTENCE contains the word "forbidden", every url path in that sentence
    must relate to a real entry of ``_FORBIDDEN_URL_SUBSTRINGS``. It says
    nothing about paths in sentences that make no such claim, and it does not
    try to police the opposite claim -- "is on the allowlist" is checked by
    ``assert_read_url`` itself, which is a better instrument than a regex.
    """
    sources = dict(_every_refusal_a_caller_can_receive())
    for action, text in server._WHY_NOT_PERFORMED.items():
        sources["_WHY_NOT_PERFORMED[%s]" % action] = text

    # DERIVED, NOT A FLOOR. This read ``> 10`` and started failing on
    # 2026-09-01 when the ninth write shipped -- because every action that
    # becomes performable makes this corpus SMALLER, so a hardcoded minimum
    # turns into a false alarm exactly as the work succeeds. What must be true
    # is that the corpus accounts for every refusal that still exists, which
    # fails when the collector breaks and stays quiet when an action ships.
    expected = (
        len(writes.SANCTIONED_WRITES) - len(writes.PERFORMABLE)
    ) + len(server._WHY_NOT_PERFORMED)
    assert len(sources) == expected, (len(sources), expected, sorted(sources))

    forbidden = readonly._FORBIDDEN_URL_SUBSTRINGS
    for where, text in sources.items():
        for sentence in " ".join(text.split()).split(". "):
            if "forbidden" not in sentence.lower():
                continue
            for token in _path_tokens(sentence):
                assert any(
                    bad in token or token in bad for bad in forbidden
                ), "%s calls %r forbidden and it is not. Sentence: %s" % (
                    where, token, sentence,
                )
# ---------------------------------------------------------------------------
# A FOURTH DRIFT, and it is the most dangerous shape this file guards
# ---------------------------------------------------------------------------
#
# The three above are a docstring understating a COUNT, a description naming
# the WRONG MEMBERS, and a refusal citing a boundary that had moved. This one
# is a docstring understating a CAPABILITY -- and not any capability: the two
# it was found on are the only write tools that put the operator's words in
# front of another person.
#
# FOUND 2026-09-03, ON TWO TOOLS, BY CENSUS RATHER THAN BY NOTICE. The wave
# lead ran ``linkedin_send_message`` and it minted real confirm tokens while
# its own Args block said ``no token is ever issued for this action``. Fixing
# the tool that was noticed would have left the class: counting every
# PERFORMABLE action against that sentence found ``update_profile_field``
# saying it too, and nobody had reported that one.
#
# **A TOOL DESCRIPTION IS READ INSTEAD OF THE SOURCE, WHICH INVERTS WHO A
# STALE SENTENCE ENDANGERS.** A caller reading "no token is ever issued"
# concludes the call is inert and may offer it freely. Understating a
# capability is therefore strictly more dangerous than overstating one: the
# overstatement makes a caller too careful, and this makes them careless in
# exact proportion to how much they trust the docs.


def _registered_tool(tools, action: str):
    """The registered tool object for one sanctioned action, or None."""
    for name, spec in writes.SANCTIONED_WRITES.items():
        if spec.action == action and name in tools:
            return tools[name]
    return None


def _live_claim(text: str) -> str:
    """The FIRST PARAGRAPH of a description -- where a live claim lives.

    BOTH CHECKS BELOW READ ONLY THIS, and the reason is the same one that
    keeps the headline check on the summary line: **this repo requires a
    corrected docstring to say what it used to say**, verbatim, so a caller
    who read the old text learns it was wrong. That disclosure necessarily
    contains the false sentence.

    A guard matching anywhere in the description therefore fires on the FIX --
    measured, on the first run of these two checks: both corrected docstrings
    came back red for quoting the sentence they had just retracted. That is
    this repo's own self-refuting shape (``test_path_hygiene`` proving it
    detects real paths by carrying one) arriving in a guard.

    So the split is structural rather than clever: a live claim is what the
    description LEADS with; a retraction is a later paragraph, set off by a
    blank line. Reading the first paragraph keeps the check sharp on the claim
    and blind to the history, which is the only arrangement in which both can
    coexist.
    """
    return " ".join((text or "").strip().split("\n\n")[0].split())


def _param_claim(tools, action: str, param: str) -> str:
    """One parameter's live claim, as a caller sees it in the JSON schema.

    THE DESCRIPTION ALONE WOULD HAVE MISSED IT, and that was measured while
    writing this. FastMCP splits an authored docstring: the prose becomes
    ``description`` and the ``Args:`` block becomes per-parameter
    ``description`` entries in the schema. The sentence that started this --
    ``no token is ever issued for this action`` -- lives in the Args block, so
    a guard reading ``tool.description`` reports CLEAN over a false claim the
    caller can read in the schema. That is this file's own disease: a check
    aimed at the half of the surface where the defect was not.
    """
    tool = _registered_tool(tools, action)
    if tool is None:
        return ""
    schema = getattr(tool, "parameters", None) or {}
    field = (schema.get("properties") or {}).get(param) or {}
    return _live_claim(str(field.get("description") or ""))


@pytest.mark.anyio
async def test_no_performable_tool_claims_it_never_issues_a_token(tools):
    """A tool that CAN act may not tell a caller that it cannot.

    Asserted over every PERFORMABLE action rather than the one that was
    reported, because the reported one was not the only one -- and a guard
    written against a single instance would have shipped green over the
    second.
    """
    lying = [
        action
        for action in sorted(writes.PERFORMABLE)
        if "no token is ever issued"
        in _param_claim(tools, action, "confirm_token")
    ]
    assert not lying, (
        "these actions are PERFORMABLE and their confirm_token description "
        "says no token is ever issued for them: %s" % lying
    )

    # AND THE CHECK CAN STILL SEE, which is not free given what it reads.
    # Narrowing to the first paragraph is exactly the move that could turn
    # this into a check that cannot fail -- if the parameter descriptions
    # stopped reaching it, every action would pass for the wrong reason. So
    # the corpus is asserted non-empty first.
    described = [
        action
        for action in sorted(writes.PERFORMABLE)
        if _param_claim(tools, action, "confirm_token")
    ]
    assert len(described) == len(writes.PERFORMABLE), (
        "confirm_token has no readable description on: %s"
        % sorted(set(writes.PERFORMABLE) - set(described))
    )


@pytest.mark.anyio
async def test_no_performable_tool_headlines_itself_as_refusing(tools):
    """The FIRST line is the summary a caller sees in a tool list.

    ``BUILT, GATED, AND REFUSING`` is the correct headline for an action that
    refuses, and four docstrings still carry the phrase HISTORICALLY -- "this
    said X until 2026-09-01" -- which is exactly the disclosure this repo
    wants and must keep passing. So this reads only the summary line, where
    the phrase is a live claim rather than a record of one.
    """
    refusing = []
    for action in sorted(writes.PERFORMABLE):
        tool = _registered_tool(tools, action)
        summary = ((tool.description or "") if tool else "").strip().splitlines()
        if summary and "REFUSING" in summary[0].upper():
            refusing.append((action, summary[0].strip()))
    assert not refusing, (
        "these actions PERFORM and their summary line says they refuse: %s"
        % refusing
    )


# ---------------------------------------------------------------------------
# A FIFTH DRIFT: prose about a url the code DELIBERATELY NEVER BUILDS
# ---------------------------------------------------------------------------
#
# THIS IS THE GAP THE THIRD GUARD ABOVE NAMES AND DECLINES, and the reason it
# declined does not cover this case. Its docstring says it "does not try to
# police the opposite claim -- 'is on the allowlist' is checked by
# ``assert_read_url`` itself, which is a better instrument than a regex."
#
# That is true of a REFUSAL TEXT, which describes a url the code was about to
# open, so the boundary evaluates it either way. It is FALSE of a source
# comment whose entire subject is a url this package deliberately never
# builds. ``assert_read_url`` is never called on an address nobody constructs,
# so no runtime instrument can ever contradict a claim about it. The comment
# is unreachable by the better instrument, which is exactly why it drifted and
# exactly why it needed a worse one.
#
# THE DRIFT, found 2026-09-05. ``PROFILE_DETAIL_URLS`` carried "The vanity
# slug is never used to build one of these, even though the allowlist would
# accept it". The read boundary had since dropped the third-party profile
# patterns, so the allowlist REFUSES that spelling -- and a second comment in
# the SAME FILE, on ``details_urls``, already said so. Two sites, one fact,
# opposite answers, and the one a reader meets first was the wrong one.
#
# The clause was load-bearing in the wrong direction: it told the next reader
# a slug-built address would pass the door, and it sold a mechanism as a
# preference.

#: An invented public identifier. Taken from ``SYNTHETIC_SLUGS`` in
#: ``tests/test_no_committed_identity.py``, which is the register of values
#: this repository has established are invented -- so reusing one widens
#: NOTHING, where declaring a fresh plant would widen what that guard
#: tolerates in this file forever.
_INVENTED_SLUG = "some-real-slug-99"

#: The three spellings the drifted clause claimed were admissible.
_SLUG_SPELLINGS = (
    "https://www.linkedin.com/in/%s/details/skills/" % _INVENTED_SLUG,
    "https://www.linkedin.com/in/%s/details/experience/" % _INVENTED_SLUG,
    "https://www.linkedin.com/in/%s/" % _INVENTED_SLUG,
)


def _profile_detail_comment() -> str:
    """The contiguous comment block directly above ``PROFILE_DETAIL_URLS``.

    Located by CONTENT, never by line number. Line numbers in this file have
    moved three times in an hour under concurrent writers, and a guard that
    reads a fixed offset measures the tree's churn rather than its prose.
    """
    import pathlib

    anchor = "PROFILE_DETAIL_URLS: dict[str, str] = {"
    lines = pathlib.Path(server.__file__).read_text(
        encoding="utf-8", errors="replace"
    ).splitlines()
    index = next((i for i, ln in enumerate(lines) if ln.startswith(anchor)), -1)
    assert index > 0, "anchor not found in server.py: %r" % anchor
    block: list[str] = []
    cursor = index - 1
    while cursor >= 0 and lines[cursor].lstrip().startswith("#"):
        block.append(lines[cursor])
        cursor -= 1
    assert block, "no comment block above %r" % anchor
    return "\n".join(reversed(block))


def test_the_profile_detail_comment_was_found_and_is_the_right_one():
    """A LOOP OVER NOTHING PASSES, and so does a regex over an empty string.

    The two guards below read a block located by an anchor. If the anchor ever
    stops matching -- a rename, a reformat -- an empty block would make both
    of them pass while checking nothing. This fails HERE instead, and names
    what it did find rather than only what it did not.
    """
    block = _profile_detail_comment()
    assert len(block.splitlines()) > 5, block
    assert "/in/me/" in block, block


def test_the_read_boundary_refuses_every_slug_spelling_of_a_details_page():
    """The MEASUREMENT half. Prose is checked against this, not the reverse.

    If the boundary is ever widened to admit a member-slug profile address
    again, this goes red -- and the comment above ``PROFILE_DETAIL_URLS``,
    which argues from this refusal, has to be re-read rather than silently
    becoming wrong a second time.
    """
    admitted = []
    for url in _SLUG_SPELLINGS:
        try:
            readonly.assert_read_url(url)
        except Exception:
            continue
        admitted.append(url.split("/in/", 1)[1])
    assert admitted == [], (
        "the read boundary now ADMITS a slug-built profile address: %s"
        % admitted
    )
    # THE CONTROL, and it is the whole reading. Without it an empty
    # ``admitted`` could mean the boundary refuses everything, or that
    # ``assert_read_url`` raises unconditionally, or that the urls above are
    # malformed. The ``/in/me/`` spelling MUST be admitted for the refusals
    # above to be about the SLUG rather than about the path.
    readonly.assert_read_url("https://www.linkedin.com/in/me/details/skills/")


def test_no_comment_claims_the_allowlist_accepts_what_it_refuses():
    """The PROSE half, bound to the measurement above.

    Deliberately narrow, in the shape the third guard established: it fires
    only on a sentence that makes an ADMISSION claim about the allowlist, and
    says nothing about prose that makes no such claim.
    """
    block = " ".join(_profile_detail_comment().replace("#:", " ").split())
    claims = [
        sentence
        for sentence in block.split(". ")
        if re.search(r"allowlist would accept|allowlist accepts", sentence, re.I)
        and not re.search(r"\bREFUSES\b|read \"even though|until 2026", sentence)
    ]
    assert claims == [], (
        "this comment says the allowlist would accept a spelling "
        "assert_read_url refuses: %s" % claims
    )


# ---------------------------------------------------------------------------
# A SIXTH DRIFT, and this one has not happened yet
# ---------------------------------------------------------------------------
#
# The five above are drifts that SHIPPED. This is the same shape caught before
# it moves, and it is here because the sentence that states it is the only
# thing holding it: ``linkedin_my_profile`` says, of the urls it hands back,
#
#     `/in/me/details/<section>/` is both the form a browser resolves for him
#     and the exact form `PROFILE_DETAIL_URLS` above navigates. EMISSION AND
#     NAVIGATION NOW AGREE.
#
# They agree by COINCIDENCE OF TWO LISTS, not by construction. The tool
# NAVIGATES with ``PROFILE_DETAIL_URLS`` and EMITS from a hardcoded
# ``("Experience", "Education", "Skills")`` written 2300 lines away, so a
# fourth section added to the table would leave the emission silently short
# and the sentence silently false.
#
# THAT EXACT SCENARIO IS THE ONE THE TABLE'S OWN COMMENT WORRIES ABOUT --
# "a fourth section admitted without re-reading the call site". The table was
# built as a lookup precisely so a caller's string could never reach a url;
# the emission site then interpolates, safely, from literals. Safe today, and
# the argument for the table says exactly what "safe today" is worth.
#
# NOT FIXED BY EDITING server.py. Deriving the emission from the table would
# make the invariant structural and this guard tautological -- the better
# engineering, and not a change to make inside a shipped read tool in a tree
# eight waves are writing, on a defect that has not fired. Pinned instead, so
# whoever makes that change, or adds the fourth section, meets it.


def _details_emission_sections() -> set[str]:
    """The sections ``linkedin_my_profile`` EMITS urls for, read from source.

    Located by CONTENT. The comprehension has no name to import and no way to
    be called without a live profile read, so the source is the only place the
    list exists.
    """
    import pathlib

    marker = 'out["details_urls"] = {'
    source = pathlib.Path(server.__file__).read_text(
        encoding="utf-8", errors="replace"
    )
    start = source.find(marker)
    assert start > 0, "emission site not found: %r" % marker
    block = source[start : start + 400]
    tup = re.search(r"for section in \(([^)]*)\)", block)
    assert tup, "no section tuple in the emission block: %r" % block[:200]
    return {
        name.strip().strip("\"'").lower()
        for name in tup.group(1).split(",")
        if name.strip()
    }


def test_the_emission_site_was_found_and_is_not_empty():
    """A set comparison between two empty sets passes. This stops that."""
    sections = _details_emission_sections()
    assert len(sections) >= 3, sections
    assert "skills" in sections, sections


def test_emission_and_navigation_agree_on_the_same_sections():
    """The claim, checked. It is true today and nothing was holding it.

    Adding a fourth entry to ``PROFILE_DETAIL_URLS`` without adding it to the
    emission tuple turns this red, which is the whole point: the tool would
    otherwise go on advertising three of four addresses while its own comment
    said emission and navigation agree.
    """
    emitted = _details_emission_sections()
    navigated = set(server.PROFILE_DETAIL_URLS)
    assert emitted == navigated, {
        "emitted, not navigated": sorted(emitted - navigated),
        "navigated, not emitted": sorted(navigated - emitted),
    }


def test_every_navigated_detail_url_has_the_self_resolving_form():
    """The other half of the claim: agreement on SHAPE, not only on keys.

    Two lists can hold the same three names and still point at different
    addresses. Every navigated url must be the ``/in/me/`` spelling the
    emission site writes, which is also the only spelling the read boundary
    admits -- see the guards above.
    """
    wrong = {
        section: url
        for section, url in server.PROFILE_DETAIL_URLS.items()
        if not url.endswith("/in/me/details/%s/" % section)
    }
    assert wrong == {}, wrong
