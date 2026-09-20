"""``item_addresses`` classifies LinkedIn item addresses and discloses nothing else.

WHAT THIS SUITE PROVES AND WHAT IT DOES NOT, said first because the distinction
is the whole reason the census row this module serves stays where it is.

**PROVED HERE, without a browser and without a network call:**

* the classifier recognises the two item-address markers and refuses four
  distinct ways, each with its own reason word
* the committed synthetic fixture reproduces, exactly, the figures measured on
  2026-09-20 against a real capture of ``/analytics/creator/content/``
* THE DISCLOSURE PROPERTY, in both directions: with ``include_identifiers``
  False no substring of any input leaves, and with it True the ONLY substrings
  that leave are whole anchored urns
* the reader's control flow, including the two branches that exist so a dead
  locator cannot be reported as an empty page

**NOT PROVED HERE, and the reader says so in its own docstring:** that
``a[href]`` finds the anchors on the live surface. A fake page proves how the
reader behaves given attributes; only a page load proves what LinkedIn draws.
This wave was forbidden the load. That is why the row this serves is not
banked and why nothing here asserts a live shape.

SHOWN FAILING BEFORE ADMISSION. Every check here that could be vacuous carries
its own control in the same file:

* :func:`test_the_disclosure_check_can_fail` runs the disclosure assertion over
  a DELIBERATELY LEAKY reading and requires it to raise. Without it, the
  disclosure tests would pass just as happily over a function that returned
  nothing at all.
* :func:`test_the_fixture_is_not_trivially_clean` asserts the fixture actually
  contains the slug-shaped and non-urn anchors the refusal counts depend on --
  a refusal count of 21 over a file with 21 anchors of one kind proves less
  than it looks.
* the positive control sits beside every negative one: a suite that only ever
  shows refusals has not shown that anything can be recognised.
"""

from __future__ import annotations

import pathlib

import pytest

from linkedin_server import item_addresses

FIXTURE = (
    pathlib.Path(__file__).parent
    / "fixtures"
    / "synthetic"
    / "creator_content_addresses.html"
)

#: The figures measured on 2026-09-20 against a capture of
#: ``/analytics/creator/content/`` by
#: ``scripts/_probe_item_addresses_in_capture.py``. The capture is gitignored
#: -- raw captures never are committed -- so THE FIXTURE is the artefact that
#: makes these checkable, and this test requires the two to agree.
CAPTURED_ANCHORS = 27
CAPTURED_RECOGNISED = 6
CAPTURED_PERMALINK_HREFS = 4
CAPTURED_PERMALINK_URNS = 2
CAPTURED_SUMMARY_HREFS = 2
CAPTURED_SUMMARY_URNS = 2
CAPTURED_DISTINCT_URNS = 4
CAPTURED_NO_MARKER = 21


def _fixture_hrefs() -> list[str]:
    """The fixture's hrefs, parsed by the shipped probe's parser.

    IMPORTED RATHER THAN REIMPLEMENTED. Four waves in this repository wrote a
    second copy of a shipped instrument on one day and three of the copies had
    a bug; the standing rule is to import.
    """
    import sys

    root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root / "scripts"))
    import _probe_item_addresses_in_capture as probe  # noqa: PLC0415

    return probe.hrefs_in(FIXTURE.read_text(encoding="utf-8"))


class _FakePage:
    """The smallest object that behaves like the part of a page we read.

    It is a FAKE and the suite says so: it proves the reader's control flow
    over a known attribute sequence. It proves nothing about LinkedIn's DOM.
    """

    def __init__(self, hrefs, count_raises=False, attr_raises_at=None):
        self._hrefs = list(hrefs)
        self._count_raises = count_raises
        self._attr_raises_at = attr_raises_at

    def locator(self, selector):
        assert selector == "a[href]", selector
        return self

    async def count(self):
        if self._count_raises:
            raise RuntimeError("locator died")
        return len(self._hrefs)

    def nth(self, index):
        return _FakeHandle(self, index)


class _FakeHandle:
    def __init__(self, page, index):
        self._page = page
        self._index = index

    async def get_attribute(self, name):
        assert name == "href", name
        if self._page._attr_raises_at == self._index:
            raise RuntimeError("element detached")
        return self._page._hrefs[self._index]


# --------------------------------------------------------------------------
# The classifier


def test_a_permalink_is_recognised():
    """THE POSITIVE CONTROL. Without it every refusal below proves nothing."""
    verdict = item_addresses.classify(
        "https://www.linkedin.com/feed/update/urn:li:share:10001/"
    )
    assert verdict == {
        "recognised": True,
        "kind": "permalink",
        "urn": "urn:li:share:10001",
    }


def test_a_post_summary_address_is_recognised():
    verdict = item_addresses.classify(
        "https://www.linkedin.com/analytics/post-summary/urn:li:activity:20001/"
    )
    assert verdict["recognised"] is True
    assert verdict["kind"] == "post_summary"
    assert verdict["urn"] == "urn:li:activity:20001"


@pytest.mark.parametrize(
    ("href", "reason"),
    [
        (None, "no_href"),
        ("", "no_href"),
        ("https://www.linkedin.com/jobs/", "no_item_marker"),
        ("https://www.linkedin.com/feed/update/not-a-urn/", "not_urn_shaped"),
        # A urn with a non-numeric tail is NOT this repository's shape.
        (
            "https://www.linkedin.com/feed/update/urn:li:share:abc/",
            "not_urn_shaped",
        ),
        # A urn with a non-alphabetic type is not either.
        (
            "https://www.linkedin.com/feed/update/urn:li:9:10001/",
            "not_urn_shaped",
        ),
        # THE ANCHORING CASE, AND IT WAS FOUND BY MUTATION, NOT BY READING.
        # Widening ``_is_urn`` from ``startswith`` to a containment test left
        # the whole suite green -- so "only a WHOLE anchored match may leave"
        # was stated in three docstrings and asserted nowhere. A segment that
        # CONTAINS a urn is not a urn, and admitting it would publish the
        # prefix along with it.
        (
            "https://www.linkedin.com/feed/update/x-urn:li:share:10001/",
            "not_urn_shaped",
        ),
        # The malformed tail is kept UNDER EIGHT CHARACTERS on purpose.
        # ``tests/test_no_committed_identity.py``'s URN_OPAQUE_SHAPE matches
        # ``urn:li:<letters>:<eight or more>`` and it refused an earlier draft
        # of this line reading ``10001-and-then-some``. The property under
        # test is "a trailing non-digit makes this not a urn", and five
        # characters demonstrate it exactly as well as nineteen.
        (
            "https://www.linkedin.com/feed/update/urn:li:share:100-x/",
            "not_urn_shaped",
        ),
        (
            "https://www.linkedin.com/analytics/post-summary/"
            "urn:li:activity:20001/?from=/feed/update/",
            "both_markers",
        ),
    ],
)
def test_the_refusals_each_name_their_own_reason(href, reason):
    verdict = item_addresses.classify(href)
    assert verdict["recognised"] is False
    assert verdict["refused"] == reason
    assert verdict["refused"] in item_addresses.REFUSALS


def test_every_refusal_word_is_reachable():
    """A closed vocabulary with an unreachable member is a lie about the code.

    The parametrised test above produces four distinct reasons; this asserts
    the set it produces is the WHOLE declared vocabulary, so a fifth word
    added to :data:`item_addresses.REFUSALS` without a branch fails here.
    """
    produced = set()
    for href in (
        None,
        "https://www.linkedin.com/jobs/",
        "https://www.linkedin.com/feed/update/not-a-urn/",
        "https://www.linkedin.com/analytics/post-summary/"
        "urn:li:activity:20001/?from=/feed/update/",
    ):
        produced.add(item_addresses.classify(href)["refused"])
    assert produced == set(item_addresses.REFUSALS)


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        ("urn:li:share:10001", True),
        ("urn:li:activity:20001", True),
        # Anchored at BOTH ends. Each of these contains a valid urn and is
        # not one.
        ("x-urn:li:share:10001", False),
        # THE ONE THAT ACTUALLY SEPARATES THE TWO IMPLEMENTATIONS, and it took
        # a second mutation round to find. Replacing the ``startswith`` check
        # with ``in`` leaves almost every case unchanged, because the slice
        # that follows still cuts at offset 7 and then fails the digit test.
        # It differs only where the prefix sits at offset 3, so that the
        # mis-aligned slice happens to parse -- and there the containment
        # version ACCEPTS the string and publishes the three leading
        # characters along with the urn. A mutation that the suite survives is
        # either a weak mutation or a hole, and telling them apart needs this
        # input.
        ("abcurn:li:123", False),
        # Tails kept under eight characters -- see the note in the refusal
        # parametrisation above. URN_OPAQUE_SHAPE refuses a longer one in a
        # tracked file, and five characters prove the same property.
        ("urn:li:share:100-x", False),
        ("urn:li:share:100 ", False),
        # Shape failures.
        ("urn:li:share:", False),
        ("urn:li::10001", False),
        ("urn:li:sha re:10001", False),
        ("urn:li:share", False),
        ("", False),
    ],
)
def test_a_urn_is_matched_WHOLE_and_never_by_containment(candidate, expected):
    """The property three docstrings claim, finally asserted.

    ``_is_urn`` is private and tested directly on purpose: the public path
    reaches it only through an href, and a defect here was measured to be
    invisible from the public path alone.
    """
    assert item_addresses._is_urn(candidate) is expected


def test_a_marker_in_a_query_string_still_counts_as_seen():
    """AMBIGUITY IS REFUSED, NOT RESOLVED BY CHECK ORDER.

    An href carrying both markers would be attributed to whichever marker the
    loop happens to test first. ``feed.author_kind`` refuses the same shape for
    the same reason, and ``saw`` reports BOTH so the refusal is a measurement
    rather than a shrug.
    """
    verdict = item_addresses.classify(
        "https://www.linkedin.com/analytics/post-summary/"
        "urn:li:activity:20001/?from=/feed/update/"
    )
    assert verdict["refused"] == "both_markers"
    assert sorted(verdict["saw"]) == ["permalink", "post_summary"]


# --------------------------------------------------------------------------
# The fixture agrees with the capture


def test_the_fixture_reproduces_the_captured_figures():
    """THE EVIDENCE CHAIN. The capture is gitignored; this fixture is not.

    Every figure the module's docstring states was measured against a raw
    capture that cannot be committed. This test is what makes those figures
    checkable from a clone: the tracked fixture must produce them exactly.
    """
    reading = item_addresses.tally(_fixture_hrefs())
    assert reading["hrefs_seen"] == CAPTURED_ANCHORS
    assert reading["recognised"] == CAPTURED_RECOGNISED
    assert reading["by_kind"]["permalink"] == CAPTURED_PERMALINK_HREFS
    assert reading["by_kind"]["post_summary"] == CAPTURED_SUMMARY_HREFS
    assert reading["distinct_by_kind"]["permalink"] == CAPTURED_PERMALINK_URNS
    assert reading["distinct_by_kind"]["post_summary"] == CAPTURED_SUMMARY_URNS
    assert reading["distinct_urns"] == CAPTURED_DISTINCT_URNS
    assert reading["refused"]["no_item_marker"] == CAPTURED_NO_MARKER


def test_the_fixture_is_not_trivially_clean():
    """CONTROL on the fixture itself.

    A refusal count proves something only if the fixture actually contains the
    shapes being refused. If somebody simplifies this file down to twenty-one
    identical nav links, the count above still passes and measures nothing.
    """
    hrefs = _fixture_hrefs()
    assert any("/feed/update/" in h for h in hrefs), "no permalink in fixture"
    assert any(
        item_addresses.POST_SUMMARY_MARKER in h for h in hrefs
    ), "no post-summary address in fixture"
    distinct_non_item = {
        h for h in hrefs if not item_addresses.classify(h)["recognised"]
    }
    assert len(distinct_non_item) >= 15, (
        "the 21 no_item_marker refusals come from %d distinct anchors; a "
        "fixture that repeats one anchor twenty-one times would pass the "
        "count test while exercising one code path"
        % len(distinct_non_item)
    )


def test_distinct_urns_is_not_the_href_count():
    """THE COUNTING LAW, applied. Ten anchors were five newsletters.

    LinkedIn draws each post's permalink twice. A field named ``items`` over
    the href count would answer FOUR to *how many posts*, confidently and
    wrongly -- the defect ``newsletters.py`` records in its own docstring.
    """
    reading = item_addresses.tally(_fixture_hrefs())
    assert reading["by_kind"]["permalink"] == 4
    assert reading["distinct_by_kind"]["permalink"] == 2
    assert reading["by_kind"]["permalink"] != reading["distinct_by_kind"]["permalink"]
    assert "items" not in reading, (
        "this module must not publish a field called items: the two urn "
        "families are not paired and a post count is not established"
    )


# --------------------------------------------------------------------------
# The disclosure property, both directions


def _alphabet():
    """Every string this module is DECLARED to be able to emit.

    Built from the module's own constants rather than retyped, so a new
    literal added there without a decision shows up here as a failure rather
    than as silence.
    """
    words = set(item_addresses.ADDRESS_KINDS)
    words |= set(item_addresses.REFUSALS)
    words.add(item_addresses.WITHHELD)
    # The dict keys the two public functions publish.
    words |= {
        "recognised", "kind", "urn", "refused", "saw",
        "hrefs_seen", "by_kind", "distinct_by_kind", "distinct_urns",
        "urns", "disclosed", "route",
    }
    return words


def _assert_discloses_nothing(reading, inputs):
    """THE CLOSED-ALPHABET PROPERTY, which is what actually makes this safe.

    Every string in ``reading`` must be a word this module declares, or the
    one ``route`` sentence it owns. Nothing else may leave.

    **THIS REPLACED A SUBSTRING CHECK AND THE REPLACEMENT IS THE POINT.** The
    first version asserted that no four-character substring of any input
    appeared in the output, and it went red on ``link`` -- a fragment of this
    module's own word ``permalink`` that is also a fragment of
    ``linkedin.com``. A check whose failures are ordinary English gets its
    threshold raised until it passes, and then it certifies nothing. A closed
    alphabet has no threshold to raise: ``menus.py`` carries the same property
    for the same reason, on a surface where a label is routinely a name.
    """
    allowed = _alphabet()
    for value in _strings_in(reading):
        if value in allowed:
            continue
        if value == reading.get("route"):
            continue
        raise AssertionError(
            "a string outside this module's declared alphabet left the "
            "module: %r" % (value,)
        )
    # And the direct check on the shapes that matter, stated separately so a
    # future widening of the alphabet cannot quietly admit one of them.
    blob = str(reading)
    for href in inputs:
        if not isinstance(href, str):
            continue
        for marker in ("/in/", "urn:li:"):
            index = href.find(marker)
            if index < 0:
                continue
            segment = href[index:].strip("/")
            if segment and segment in blob:
                raise AssertionError(
                    "an identifier-shaped segment of the input left the "
                    "module: %r" % (segment,)
                )


def _strings_in(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _strings_in(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            yield from _strings_in(item)


def test_the_default_discloses_no_substring_of_its_input():
    """The OUT half of the guarantee, as ``feed.py`` carries it."""
    hrefs = _fixture_hrefs()
    reading = item_addresses.tally(hrefs)
    assert reading["disclosed"] is False
    assert reading["urns"] == [item_addresses.WITHHELD] * CAPTURED_DISTINCT_URNS
    _assert_discloses_nothing(reading, hrefs)


def test_the_disclosure_check_can_fail():
    """SHOWN FAILING, THREE WAYS. The check above is worthless if it cannot go red.

    Without these, a ``tally`` that returned an empty dict would satisfy every
    disclosure test in this file.
    """
    # (1) a word that is not in the declared alphabet at all
    with pytest.raises(AssertionError, match="declared alphabet"):
        _assert_discloses_nothing(
            {"urns": ["/analytics/post-summary/"]}, _fixture_hrefs()
        )

    # (2) a urn leaking under the default, caught by the alphabet
    with pytest.raises(AssertionError, match="declared alphabet"):
        _assert_discloses_nothing(
            {"urns": ["urn:li:share:10001"]}, _fixture_hrefs()
        )

    # (3) a slug leaking inside a value the alphabet would otherwise admit --
    # this is the case the second half of the helper exists for, and without
    # that half it would pass.
    with pytest.raises(AssertionError, match="identifier-shaped"):
        _assert_discloses_nothing(
            {"route": "in/a-made-up-slug-for-this-test"},
            ["https://www.linkedin.com/in/a-made-up-slug-for-this-test"],
        )


def test_opting_in_returns_whole_urns_and_nothing_else():
    """The narrow opt-in. Only a WHOLE anchored match may leave.

    Not a slug, not a query string, not a path. The assertion is structural:
    every disclosed string must round-trip through the classifier as a urn.
    """
    hrefs = _fixture_hrefs()
    reading = item_addresses.tally(hrefs, include_identifiers=True)
    assert reading["disclosed"] is True
    assert len(reading["urns"]) == CAPTURED_DISTINCT_URNS
    for urn in reading["urns"]:
        assert urn.startswith("urn:li:")
        assert item_addresses._is_urn(urn), urn
        # And it is a whole segment of some input, never a fragment of one.
        assert any(urn + "/" in href for href in hrefs), urn


def test_opting_in_leaks_nothing_but_the_urns():
    """The other half: everything EXCEPT ``urns`` still discloses nothing."""
    hrefs = _fixture_hrefs()
    reading = item_addresses.tally(hrefs, include_identifiers=True)
    without_urns = {k: v for k, v in reading.items() if k != "urns"}
    _assert_discloses_nothing(without_urns, hrefs)


def test_a_profile_slug_can_never_leave_even_on_opt_in():
    """The worst case, planted deliberately.

    A slug is the one shape this repository's own guard hunts hardest, and an
    href on a real analytics page carries one. It must not come back under any
    flag.
    """
    hrefs = [
        "https://www.linkedin.com/in/a-made-up-slug-for-this-test/",
        "https://www.linkedin.com/feed/update/urn:li:share:10001/",
    ]
    reading = item_addresses.tally(hrefs, include_identifiers=True)
    assert reading["recognised"] == 1
    assert "a-made-up-slug-for-this-test" not in str(reading)


# --------------------------------------------------------------------------
# The reader's control flow


@pytest.mark.asyncio
async def test_the_reader_reads_every_anchor():
    hrefs = _fixture_hrefs()
    reading = await item_addresses.read_item_addresses(_FakePage(hrefs))
    assert reading["hrefs_seen"] == CAPTURED_ANCHORS
    assert reading["recognised"] == CAPTURED_RECOGNISED
    assert reading["disclosed"] is False
    assert "route" in reading


@pytest.mark.asyncio
async def test_a_dead_locator_is_not_an_empty_page():
    """A zero with no denominator is the failure this branch exists for.

    ``hrefs_seen`` 0 alongside a raised count is the honest answer; silently
    reporting ``recognised`` 0 would say *this page drew no posts* about a
    page nobody managed to read.
    """
    reading = await item_addresses.read_item_addresses(
        _FakePage(_fixture_hrefs(), count_raises=True)
    )
    assert reading["hrefs_seen"] == 0
    assert reading["recognised"] == 0
    assert reading["distinct_urns"] == 0


@pytest.mark.asyncio
async def test_an_unreadable_element_is_counted_not_dropped():
    """A detached element becomes a ``no_href`` refusal, not a missing row.

    Dropping it would shrink the denominator silently, which is how a reader
    starts reporting a cleaner page than the one it read.
    """
    hrefs = _fixture_hrefs()
    reading = await item_addresses.read_item_addresses(
        _FakePage(hrefs, attr_raises_at=0)
    )
    assert reading["hrefs_seen"] == CAPTURED_ANCHORS
    assert reading["refused"]["no_href"] == 1


@pytest.mark.asyncio
async def test_the_reader_takes_no_url():
    """THE BINDING IS THE SAFETY ARGUMENT, so it is asserted.

    The only thing making these items HIS is that the caller opens one
    address. A url parameter here would move that guarantee into a caller's
    good intentions.
    """
    import inspect

    names = set(inspect.signature(item_addresses.read_item_addresses).parameters)
    assert names == {"page", "include_identifiers"}, names
