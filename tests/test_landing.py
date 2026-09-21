"""What ``landing.py`` may say about an address, and the proof it says nothing else.

The module's claim is one sentence: **every string it can emit is a literal it
declares, an integer, or a boolean.** That is the whole safety property, so it
is asserted directly -- over an adversarial table, field by field, against the
declared alphabets -- rather than by spot-checking one output.

NO REAL IDENTITY IS HERE. Every needle carries the token ``example``, which is
one of ``tests/test_no_committed_identity.SYNTHETIC_SLUG_TOKENS``, and every
numeric id is one already in that file's ``SYNTHETIC_IDS``. This file moves no
allowlist to exist.
"""

from __future__ import annotations

import json
import re

import pytest

from linkedin_server import landing
from linkedin_server.config import AUTHWALL_MARKERS
from tests.leakwalk import find_leaks

# ---------------------------------------------------------------------------
# The needles. Person-shaped, invented, and placed in a DIFFERENT position in
# each row -- a plant that only ever sits in one slot tests one slot.
# ---------------------------------------------------------------------------

#: The plant every row carries. One token, so a single ``find_leaks`` call
#: answers "did any part of the landing survive" for the whole table.
PLANT = "example-markersurname-associates"

#: ``(label, url)``. THE POSITION IS THE VARIABLE. Section C's whole argument
#: is that a describer can be clean in the slot its author thought about and
#: leaky in the one they did not.
PLANTED_LANDINGS: tuple[tuple[str, str], ...] = (
    (
        "in the redirect parameter, absolute and encoded -- the MEASURED shape",
        "https://www.linkedin.com/authwall?trk=x&trkInfo=y&original_referer="
        "&sessionRedirect=https%3A%2F%2Fwww.linkedin.com%2Fcompany%2F"
        + PLANT
        + "%2F",
    ),
    (
        "in the redirect parameter, relative -- the shape the fixtures ship",
        "https://www.linkedin.com/login?session_redirect=%2Fcompany%2F" + PLANT,
    ),
    (
        "in the redirect parameter, undecoded",
        "https://www.linkedin.com/uas/login?session_redirect=/school/" + PLANT,
    ),
    (
        "in the landing's own path",
        "https://www.linkedin.com/authwall/" + PLANT + "/",
    ),
    (
        "under a parameter name this package does not declare",
        "https://www.linkedin.com/authwall?" + PLANT + "=%2Fcompany%2Fx",
    ),
    (
        "as the parameter NAME on a value that is an address",
        "https://www.linkedin.com/authwall?" + PLANT + "=https%3A%2F%2Fx.com%2Fy",
    ),
    (
        "in the fragment",
        "https://www.linkedin.com/authwall#" + PLANT,
    ),
    (
        "as the host",
        "https://" + PLANT + ".example.com/authwall?sessionRedirect=%2Ffeed",
    ),
    (
        "in the userinfo, which is a place nobody looks",
        "https://" + PLANT + "@www.linkedin.com/authwall",
    ),
    (
        "nested two redirects deep",
        "https://www.linkedin.com/authwall?sessionRedirect=https%3A%2F%2F"
        "www.linkedin.com%2Fuas%2Flogin%3Fsession_redirect%3D%252Fcompany"
        "%252F" + PLANT,
    ),
)


#: The complete vocabulary ``jobfilter.describe_shape`` can name. Declared
#: here rather than imported because it is spelled as literals inside that
#: function; the coupling is deliberate and this test is what holds it. A new
#: class there turns this red, and somebody confirms it is a class name rather
#: than a piece of the value.
SHAPE_CLASSES = frozenset(
    {
        "digits",
        "letters",
        "hyphen-or-underscore",
        "whitespace",
        "punctuation",
        "empty",
    }
)


def _alphabet_violations(described: dict) -> list[str]:
    """Every field of a descriptor that is not a declared literal or a number.

    A FUNCTION rather than an inline block, because the control at the bottom
    has to be able to aim it at a describer that quoted its input. A predicate
    only ever run on data that passes has never been shown to reject anything.
    """
    out: list[str] = []
    markers = set(AUTHWALL_MARKERS) | {landing.MARKER_NONE}
    hosts = set(landing.HOSTS) | {
        landing.HOST_OTHER,
        landing.HOST_NONE,
        landing.HOST_UNPARSEABLE,
    }
    routes = set(landing.ROUTE_CLASSES)

    if described.get("marker") not in markers:
        out.append("marker=%r" % (described.get("marker"),))
    if described.get("host") not in hosts:
        out.append("host=%r" % (described.get("host"),))
    if described.get("route") not in routes:
        out.append("route=%r" % (described.get("route"),))
    if described.get("bounced_from") not in routes:
        out.append("bounced_from=%r" % (described.get("bounced_from"),))
    for name in described.get("named_address_params", ()) or ():
        if name not in landing.ADDRESS_PARAMS:
            out.append("named_address_params carries %r" % (name,))
    for key in (
        "path_segments",
        "query_params",
        "params_with_an_address",
        "unnamed_address_params",
    ):
        value = described.get(key)
        if not isinstance(value, int) or isinstance(value, bool):
            out.append("%s=%r is not an int" % (key, value))
    # The one free-form field, and it is free-form only in the sense that it
    # carries a NUMBER and a set of CHARACTER-CLASS names. ``describe_shape``
    # is the shipped instrument; this pins the grammar AND the vocabulary it
    # may answer in, by parsing rather than by a regex over the whole line --
    # the first version of this check was a regex, and it rejected every real
    # answer while still admitting prose of the right shape.
    shape = described.get("shape")
    matched = re.fullmatch(r"(\d+) characters, containing (.+)", str(shape or ""))
    if not isinstance(shape, str) or matched is None:
        out.append("shape=%r" % (shape,))
    else:
        for token in matched.group(2).split(" + "):
            if token not in SHAPE_CLASSES:
                out.append("shape names %r" % (token,))
    return out


# ---------------------------------------------------------------------------
# 1. THE VOCABULARY IS ONE VOCABULARY, held to anchors.py by assertion
# ---------------------------------------------------------------------------


def test_every_route_row_here_is_one_anchors_already_ships():
    """The copy may not drift. ``landing.py`` says why it is a copy at all."""
    from linkedin_server import anchors

    extra = set(landing.ROUTE_TABLE) - set(anchors.ROUTE_TABLE)
    assert not extra, (
        "landing.ROUTE_TABLE has rows anchors.ROUTE_TABLE does not: %r. The "
        "two tables are one rule with two homes and the copy is checked, not "
        "trusted." % (sorted(extra),)
    )


def test_every_class_token_here_is_one_anchors_already_ships_but_one():
    """One token is deliberately new, and the exception is named rather than
    silent.

    ``no_path`` has no counterpart in ``anchors.ROUTE_CLASSES`` because that
    classifier always has an href to place. Here the input can be a url with
    no path at all, and collapsing that into ``other_internal`` would report
    "I could not place this path" for a url that had none -- the same
    distinction the three HOST refusal literals exist for.
    """
    from linkedin_server import anchors

    shared = set(landing.ROUTE_CLASSES) - {landing.ROUTE_NONE}
    assert shared <= set(anchors.ROUTE_CLASSES), sorted(
        shared - set(anchors.ROUTE_CLASSES)
    )
    assert landing.ROUTE_NONE not in anchors.ROUTE_CLASSES
    assert landing.ROUTE_UNCLASSIFIED == anchors.UNCLASSIFIED


def test_a_route_term_is_a_whole_segment_and_never_a_substring():
    """``anchors.py``'s scar, followed here rather than re-derived.

    Measured there: containment reclassified a help article, a messaging
    thread and a school page as member profiles, because the term ``in`` is a
    substring of ``linkedin``, ``messaging`` and ``institute``.
    """
    assert landing._route_of("/institute/x/") == landing.ROUTE_UNCLASSIFIED
    assert landing._route_of("/linkedin/x/") == landing.ROUTE_UNCLASSIFIED
    assert landing._route_of("/in/x/") == "member_profile"
    # A SECOND SEGMENT IS REQUIRED WHERE THE TABLE REQUIRES ONE.
    assert landing._route_of("/jobs/view/5417062/") == "job_posting"
    assert landing._route_of("/jobs/") == landing.ROUTE_UNCLASSIFIED


# ---------------------------------------------------------------------------
# 2. THE ALPHABET IS CLOSED, over an adversarial table
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label,url", PLANTED_LANDINGS, ids=lambda v: v)
def test_no_descriptor_field_leaves_the_declared_alphabet(label, url):
    assert _alphabet_violations(landing.describe_landing(url)) == []


@pytest.mark.parametrize("label,url", PLANTED_LANDINGS, ids=lambda v: v)
def test_no_part_of_a_planted_landing_reaches_the_descriptor(label, url):
    """THE PROPERTY, asserted where the plant moves position row by row."""
    described = landing.describe_landing(url)
    assert find_leaks(described, PLANT) == []
    assert find_leaks(landing.render(described), PLANT) == []
    assert find_leaks(landing.withheld(url), PLANT) == []


def test_the_parameter_NAME_may_be_said_and_its_VALUE_may_not():
    """The one place a site-chosen string is repeated, and why it is bounded.

    ``sessionRedirect`` is in :data:`landing.ADDRESS_PARAMS`, a closed set this
    package declares, so it is LinkedIn's vocabulary rather than a third
    party's text -- the vocabulary-in / index-out discipline ``anchors.py`` and
    ``search_results.py`` are built on. A parameter LinkedIn invents tomorrow
    is COUNTED and never quoted, which is the half worth asserting.
    """
    known = landing.describe_landing(
        "https://www.linkedin.com/authwall?sessionRedirect=%2Fcompany%2Fx"
    )
    assert known["named_address_params"] == ("sessionRedirect",)
    assert known["unnamed_address_params"] == 0

    invented = landing.describe_landing(
        "https://www.linkedin.com/authwall?" + PLANT + "=%2Fcompany%2Fx"
    )
    assert invented["named_address_params"] == ()
    assert invented["unnamed_address_params"] == 1
    assert invented["params_with_an_address"] == 1


# ---------------------------------------------------------------------------
# 3. IT RUNS ON AN ERROR PATH, SO IT MAY NOT RAISE
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        0,
        b"https://www.linkedin.com/authwall",
        ["https://www.linkedin.com/authwall"],
        {"url": "x"},
        "http://[::1/authwall",
        "://////",
        "https://www.linkedin.com/authwall?" + "a=" * 4000,
        # NON-ASCII, WRITTEN AS ESCAPES SO THE SOURCE FILE STAYS ASCII. A
        # landing can carry any codepoint LinkedIn puts in it, and
        # ``describe_shape`` counts CHARACTERS rather than bytes, so this row
        # is the one that would catch a length or a class rule that assumed
        # latin-1.
        "https://www.linkedin.com/authwall?q=\\u00e9\\u4e2d\\u6587",
        "/authwall",
        "authwall",
    ],
    ids=lambda v: repr(v)[:40],
)
def test_it_describes_anything_and_raises_on_nothing(value):
    """A describer that can raise turns one failure into a less informative one.

    ``urlsplit`` raises ``ValueError`` on a malformed IPv6 literal, which is
    why there is a guarded ``_split`` rather than a bare call, and why the
    refusal for that case is a LITERAL -- an unparseable landing is still
    described rather than dropped.
    """
    described = landing.describe_landing(value)
    assert _alphabet_violations(described) == []
    assert isinstance(landing.render(described), str)
    assert landing.withheld(value)


def test_an_unparseable_landing_says_so_rather_than_guessing():
    described = landing.describe_landing("http://[::1/authwall")
    assert described["host"] == landing.HOST_UNPARSEABLE


# ---------------------------------------------------------------------------
# 4. THE VERDICT DID NOT MOVE. Only the reported marker is new.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        "https://www.linkedin.com/login",
        "https://www.linkedin.com/authwall?trk=x",
        "https://www.linkedin.com/uas/login-submit",
        "https://www.linkedin.com/checkpoint/challenge/",
        "https://www.linkedin.com/feed/",
        "https://www.linkedin.com/notifications/",
        "https://www.linkedin.com/company/5417062/",
        "",
        None,
    ],
)
def test_the_marker_verdict_is_the_one_that_shipped(url):
    """``authwall_marker`` replaced an ``any(marker in url ...)``. The
    replacement is a REFACTOR of the verdict and an ADDITION to the report, and
    a test that only exercised the new half would not have said so."""
    shipped = any(marker in (url or "") for marker in AUTHWALL_MARKERS)
    assert (landing.authwall_marker(url) is not None) is shipped


def test_the_reported_marker_is_the_first_one_declared():
    """More than one can match; the order is what makes the answer
    deterministic rather than arbitrary. ``/uas/login-submit`` contains
    ``/login``."""
    assert landing.authwall_marker(
        "https://www.linkedin.com/uas/login-submit"
    ) == "/login"


# ---------------------------------------------------------------------------
# 5. IT DISCRIMINATES. A describer that answers the same thing about
#    everything is over-redacting, which is not a pass.
# ---------------------------------------------------------------------------


def test_two_different_landings_do_not_describe_identically():
    company = landing.withheld(
        "https://www.linkedin.com/authwall?sessionRedirect=%2Fcompany%2Fx%2F"
    )
    member = landing.withheld(
        "https://www.linkedin.com/authwall?sessionRedirect=%2Fin%2Fx%2F"
    )
    bare = landing.withheld("https://www.linkedin.com/login")
    assert company != member
    assert company != bare
    assert "bounced from company_page" in company
    assert "bounced from member_profile" in member


def test_the_field_a_debugger_actually_needs_is_the_one_that_is_kept():
    """``bounced_from`` is the reason this function parses the query at all.

    *You were bounced off a company page* is the diagnosis; WHICH company page
    is the leak. The first is a literal from a closed table and the second is
    a name.
    """
    described = landing.describe_landing(
        "https://www.linkedin.com/authwall?sessionRedirect="
        "https%3A%2F%2Fwww.linkedin.com%2Fcompany%2F" + PLANT + "%2F"
    )
    assert described["bounced_from"] == "company_page"
    assert find_leaks(described, PLANT) == []


# ---------------------------------------------------------------------------
# 6. THE SHIPPED REFUSAL, END TO END, AND THE LOG BESIDE IT
# ---------------------------------------------------------------------------


def test_the_refusal_carries_no_part_of_the_landing_and_neither_does_the_log(
    caplog,
):
    """Both ways out of the process, in one assertion.

    A log record is another way out, which is the rule ``coerce.as_count``
    follows and the reason ``leakwalk.assert_no_leak`` takes a ``caplog`` at
    all. Here the log carries LESS than the refusal, deliberately -- see the
    comment in ``auth.assert_not_authwall`` for the shipped guard that decided
    it.
    """
    import logging

    from linkedin_server import server
    from linkedin_server.auth import assert_not_authwall
    from linkedin_server.errors import NotAuthenticatedError

    url = (
        "https://www.linkedin.com/authwall?sessionRedirect="
        "https%3A%2F%2Fwww.linkedin.com%2Fcompany%2F" + PLANT + "%2F"
    )
    with caplog.at_level(logging.WARNING, logger="linkedin"):
        with pytest.raises(NotAuthenticatedError) as caught:
            assert_not_authwall(url, surface="organisation Page")

    rendered = json.dumps(server._error(caught.value))
    assert find_leaks(rendered, PLANT) == []
    assert find_leaks(caplog.text, PLANT) == []
    assert "sessionRedirect=" not in rendered
    assert "sessionRedirect=" not in caplog.text
    # NOT VACUOUS: the log and the refusal each still do their job.
    assert "organisation Page" in caplog.text
    assert "signed-out wall" in rendered
    assert "bounced from company_page" in rendered


def test_the_refusal_still_names_the_surface_and_the_marker():
    """A refusal that says nothing satisfies an absence check perfectly."""
    from linkedin_server.auth import assert_not_authwall
    from linkedin_server.errors import NotAuthenticatedError

    with pytest.raises(NotAuthenticatedError) as caught:
        assert_not_authwall(
            "https://www.linkedin.com/checkpoint/challenge/", surface="events"
        )
    message = str(caught.value)
    assert "events" in message
    assert "/checkpoint/" in message
    assert "linkedin_login" in message


def test_a_signed_in_landing_is_still_let_through():
    """A gate that refuses everything is not discriminating, it is failing."""
    from linkedin_server.auth import assert_not_authwall

    assert_not_authwall(
        "https://www.linkedin.com/company/5417062/", surface="organisation Page"
    )


def test_the_exception_carries_no_url_attribute():
    """``server._error`` publishes ``getattr(exc, "url", "")`` UNSCRUBBED.

    That is ``ExtractionFailedError``'s deliberate contract and it is the one
    way a landing could be put straight back on the wire past every argument
    in ``landing.py``. Asserted so that a future edge-case fix cannot add it
    quietly.
    """
    from linkedin_server import server
    from linkedin_server.auth import assert_not_authwall
    from linkedin_server.errors import NotAuthenticatedError

    with pytest.raises(NotAuthenticatedError) as caught:
        assert_not_authwall(
            "https://www.linkedin.com/authwall?sessionRedirect=%2Fcompany%2F"
            + PLANT,
            surface="feed",
        )
    assert getattr(caught.value, "url", "") == ""
    assert "url" not in server._error(caught.value)


# ---------------------------------------------------------------------------
# 7. THE CORROBORATION NOTE -- the sibling reached by a different path
# ---------------------------------------------------------------------------


def test_the_feed_is_repeated_when_the_feed_is_where_we_landed():
    """An address this server ASKED FOR is its own, and is said plainly."""
    from linkedin_server.auth import _corroboration_note
    from linkedin_server.config import FEED_URL

    note = _corroboration_note(FEED_URL)
    assert note == "GET %s -> %s" % (FEED_URL, FEED_URL)


@pytest.mark.parametrize(
    "landed",
    [
        "https://www.linkedin.com/authwall?sessionRedirect=%2Fcompany%2F" + PLANT,
        "https://www.linkedin.com/feed/?highlightedUpdateUrn=urn%3Ali%3Aactivity"
        "%3A7400000000000000001",
        "https://www.linkedin.com/in/" + PLANT + "/",
    ],
    ids=["an authwall", "the same path with a query", "somewhere else entirely"],
)
def test_anything_that_is_not_the_asked_for_address_is_described(landed):
    """**A QUERY STRING COUNTS AS ELSEWHERE**, and the middle row is why.

    ``/feed/?highlightedUpdateUrn=...`` is the same path and carries an
    identifier this repository's own identity gate would refuse in a commit.
    A rule that compared paths and ignored queries would repeat it.
    """
    from linkedin_server.auth import _corroboration_note

    note = _corroboration_note(landed)
    assert "elsewhere" in note
    assert find_leaks(note, PLANT) == []
    assert "urn%3Ali" not in note
    assert "7400000000000000001" not in note


# ---------------------------------------------------------------------------
# 8. SHOWN FAILING. The alphabet check is a measurement only if it can reject.
# ---------------------------------------------------------------------------


def test_the_alphabet_check_convicts_a_describer_that_quoted_its_input():
    """A do-nothing describer must not pass the check that certifies the real one.

    This is the control ``tests/test_a_sanitiser_earns_its_entry.py`` argues
    for in its own first section: a body that returns its input verbatim once
    passed the same check a missing sanitiser failed.
    """
    leaky = dict(landing.describe_landing(PLANTED_LANDINGS[0][1]))
    leaky["route"] = "/company/" + PLANT + "/"
    violations = _alphabet_violations(leaky)
    assert violations, "the alphabet check cannot reject anything"
    assert any(PLANT in item for item in violations)


def test_the_alphabet_check_convicts_a_describer_that_answered_in_prose():
    """The ``shape`` slot is the one a leak would hide in, so it is pinned."""
    leaky = dict(landing.describe_landing(PLANTED_LANDINGS[0][1]))
    leaky["shape"] = "the url was " + PLANT
    assert _alphabet_violations(leaky)


def test_the_plant_check_convicts_a_descriptor_that_kept_the_landing():
    """And so is the ``find_leaks`` half, aimed at a descriptor that failed."""
    leaky = dict(landing.describe_landing(PLANTED_LANDINGS[0][1]))
    leaky["marker"] = PLANTED_LANDINGS[0][1]
    assert find_leaks(leaky, PLANT) != []
