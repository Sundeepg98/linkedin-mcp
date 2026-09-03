"""The door closed on `/messaging/compose?recipient=` is open two doors down.

WHY THIS FILE EXISTS. The wave lead asked whether `send_message` could address
a recipient by IDENTIFIER instead of by name -- a url that opens the composer
with somebody already committed, so the typeahead leaves the send path and the
name-uniqueness problem stops existing rather than getting a seventh regex.

Answering it needed no live read at all. **LinkedIn's own shape is already in
this repository**, captured live and sanitised, in
`tests/fixtures/profile_views_analytics.html`: every "Message" button on the
Who's-Viewed-Me surface is an anchor whose href is

    /messaging/compose/?profileUrn=urn:li:fsd_profile:<id>
                       &recipient=<id>
                       &screenContext=NON_SELF_PROFILE_VIEW
                       &interop=msgOverlay

That is not a guessed shape. It is the one LinkedIn draws, for a first-degree
connection, on a surface this server already reads.

## And it is REFUSED, deliberately, and that refusal is already pinned

`"/messaging/compose"` is on `readonly._FORBIDDEN_URL_SUBSTRINGS`, and the one
composer url admitted is admitted by an EQUALITY key in
`_FORBIDDEN_SUBSTRING_EXEMPTIONS` -- so every query-bearing spelling refuses.
`tests/test_readonly.py` already pins `?recipient=`, `compose/new/` and the
pre-filled overlay as BLOCKED. That is the operator's ruling working exactly as
written, and this file does not touch it.

## THE FINDING: THREE NEIGHBOURING SPELLINGS ARE ADMITTED, AND NOBODY RULED THEM

    /messaging/thread/new/?recipient=<id>      ADMITTED
    /messaging/?composeTo=<id>                 ADMITTED
    /messaging/?recipient=<id>                 ADMITTED

Two mechanisms, both incidental:

* `^https://www\\.linkedin\\.com/messaging/?(\\?[^#]*)?$` admits ANY query on
  the messaging root. It was written to cover the redirect LinkedIn performs
  when `/messaging/` is asked for, and the query group came along with it.
* `^https://www\\.linkedin\\.com/messaging/thread/[A-Za-z0-9%\\-_=]+/?(\\?[^#]*)?$`
  was written for real thread ids, and the literal `new` matches that character
  class like any other id.

**The audit's own sentence is true of the family it names and misleads about
the neighbours**: *"every other spelling in that family refuses exactly as
before"*. True -- of the `/messaging/compose/` family. The `/messaging/` and
`/messaging/thread/` families are different families and they admit an
arbitrary query.

> **An invariant nobody ruled is a coincidence, and something eventually
> depends on it.** Whether LinkedIn HONOURS `?recipient=` on those two
> addresses is unmeasured and is not the point: the boundary currently admits
> more than the ruling that shaped it intended, and that is true whether or not
> the extra surface does anything.

## WHAT THIS FILE DOES AND DOES NOT DO

**IT CHANGES NO BOUNDARY.** Refusing something currently admitted is a ruling,
and it belongs to the operator and the wave lead. This pins the CURRENT
verdicts as an inventory, so the surprising admissions are visible in a test
rather than latent in two regexes, and so any deliberate change to them has to
edit this file and say why.

Same shape as `KNOWN_DERIVED_NAVIGATIONS`: a declaration that is CHECKED, not a
comment that rots. If the boundary is tightened, the entry moves from one table
to the other and this file fails until somebody moves it.

**NO IDENTIFIER-SHAPED STRING APPEARS HERE.** The placeholder is deliberately
not id-shaped: every pattern under test matches the query with `[^#]*` and never
looks at the value, so realism buys nothing. See `FAKE_ID`.
"""

from __future__ import annotations

import pytest

from linkedin_server import readonly
from linkedin_server.errors import WriteAttemptError

#: NOT SHAPED LIKE A PROFILE ID, AND THAT IS THE CORRECTION.
#:
#: The first version of this file used `ACoAAB...` -- the real prefix and the
#: real length -- on the usual reasoning that a self-test needs a SHAPE-VALID
#: literal. `test_no_committed_identity` refused it, and the refusal was right
#: where my reasoning was not: **the id's shape is not load-bearing for this
#: measurement at all.** Every pattern under test matches the query with
#: `[^#]*`, which does not look at the value. So a realistic id bought nothing
#: and cost a tracked file that carries an identifier-shaped string.
#:
#: The rule that generalises: a shape-valid literal is required when the SHAPE
#: is what the code under test reads. When it is not, an unmistakable
#: placeholder is strictly better, because it cannot be mistaken for real and
#: cannot decay into real.
FAKE_ID = "RECIPIENT-ID-PLACEHOLDER"

#: WHAT LINKEDIN ACTUALLY DRAWS, reconstructed from the committed fixture.
#: Kept as its own constant because it is EVIDENCE, not a test input: it is the
#: shape a recipient-addressed compose would have to use, and it is refused.
LINKEDIN_MESSAGE_BUTTON_HREF = (
    "https://www.linkedin.com/messaging/compose/"
    "?profileUrn=urn%3Ali%3Afsd_profile%3A" + FAKE_ID
    + "&recipient=" + FAKE_ID
    + "&screenContext=NON_SELF_PROFILE_VIEW&interop=msgOverlay"
)

#: REFUSED, and every one of these is the ruling working as written.
REFUSED_TODAY: dict[str, str] = {
    LINKEDIN_MESSAGE_BUTTON_HREF: (
        "LinkedIn's own Message-button href. The exemption is an EQUALITY key, "
        "so a query-bearing composer url carries the forbidden substring and "
        "refuses"
    ),
    "https://www.linkedin.com/messaging/compose/?recipient=" + FAKE_ID: (
        "the minimal recipient-addressed composer"
    ),
    "https://www.linkedin.com/messaging/compose?recipient=" + FAKE_ID: (
        "and without the trailing slash, so the refusal is not an artefact of "
        "one spelling"
    ),
}

#: ADMITTED, AND UNRULED. Nobody argued for these; two regexes let them
#: through. Pinned so the fact is visible rather than latent.
ADMITTED_TODAY: dict[str, str] = {
    "https://www.linkedin.com/messaging/compose/": (
        "THE ONE DELIBERATE ADMISSION -- an exact-url exemption, argued on the "
        "operator's 2026-08-31 ruling and conditioned on the messaging badge "
        "reading zero first"
    ),
    "https://www.linkedin.com/messaging/thread/new/?recipient=" + FAKE_ID: (
        "UNRULED. `new` matches the thread-id character class, which was "
        "written for real thread ids"
    ),
    "https://www.linkedin.com/messaging/?composeTo=" + FAKE_ID: (
        "UNRULED. The messaging-root pattern admits any query"
    ),
    "https://www.linkedin.com/messaging/?recipient=" + FAKE_ID: (
        "UNRULED. Same pattern, and it is the same parameter name the "
        "composer's refused spelling uses"
    ),
}


def _verdict(url: str) -> str:
    try:
        readonly.assert_read_url(url)
    except WriteAttemptError:
        return "refused"
    return "admitted"


@pytest.mark.parametrize("url", sorted(REFUSED_TODAY), ids=range(len(REFUSED_TODAY)))
def test_a_recipient_addressed_composer_url_is_refused(url):
    """The operator's ruling, still holding on every composer spelling."""
    assert _verdict(url) == "refused", (url, REFUSED_TODAY[url])


@pytest.mark.parametrize("url", sorted(ADMITTED_TODAY), ids=range(len(ADMITTED_TODAY)))
def test_the_currently_admitted_messaging_urls_are_pinned(url):
    """AN INVENTORY, NOT AN ENDORSEMENT.

    Three of these four were never argued for. Pinning them is what turns "two
    regexes happen to allow this" into a fact somebody can rule on -- and makes
    tightening the boundary a change that edits this file rather than one that
    silently passes.
    """
    assert _verdict(url) == "admitted", (url, ADMITTED_TODAY[url])


def test_the_unruled_admissions_are_named_as_unruled():
    """A DECLARATION THAT DOES NOT SAY WHICH ENTRIES ARE ACCIDENTS IS A LIST.

    Exactly one admission was argued. The rest carry ``UNRULED`` in their own
    reason string, so the count of deliberate admissions is asserted rather
    than left to be inferred from prose that may be skimmed.
    """
    unruled = [why for why in ADMITTED_TODAY.values() if why.startswith("UNRULED")]
    assert len(unruled) == 3, unruled
    deliberate = [
        why for why in ADMITTED_TODAY.values() if "DELIBERATE" in why
    ]
    assert len(deliberate) == 1, deliberate


def test_the_two_families_are_not_the_same_family():
    """THE SENTENCE THAT MISLEADS, PINNED AS THE MEASUREMENT THAT CORRECTS IT.

    The audit records that "every other spelling in that family refuses exactly
    as before". True of `/messaging/compose/`. The neighbouring families admit
    the same parameter on a different path, and asserting the DIFFERENCE is
    what stops the reassuring half being read as the whole.
    """
    composer = "https://www.linkedin.com/messaging/compose/?recipient=" + FAKE_ID
    root = "https://www.linkedin.com/messaging/?recipient=" + FAKE_ID
    assert _verdict(composer) == "refused"
    assert _verdict(root) == "admitted"
    assert _verdict(composer) != _verdict(root), (
        "the two families now agree -- if the boundary was tightened, move the "
        "root url into REFUSED_TODAY and delete this test's premise"
    )


def test_the_evidence_url_matches_the_shape_linkedin_draws():
    """THE FIXTURE IS THE SOURCE, so this cannot drift into a made-up shape.

    `LINKEDIN_MESSAGE_BUTTON_HREF` is reconstructed from the committed
    Who's-Viewed-Me fixture rather than invented, and the four parameter names
    are what make it evidence rather than a guess. If LinkedIn's Message button
    changes shape, the fixture changes and this has to be re-derived.
    """
    fixture = (
        pytest.importorskip("pathlib").Path(__file__).parent
        / "fixtures"
        / "profile_views_analytics.html"
    )
    markup = fixture.read_text(encoding="utf-8", errors="replace")
    assert "/messaging/compose/?profileUrn=" in markup
    for parameter in ("recipient=", "screenContext=", "interop=msgOverlay"):
        assert parameter in markup, parameter
        assert parameter in LINKEDIN_MESSAGE_BUTTON_HREF, parameter
