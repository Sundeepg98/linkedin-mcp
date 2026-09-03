"""The messaging probe's redactor must fire, and must not fire on structure.

WHY THIS TEST EXISTS. ``scripts/_probe_messaging.py`` prints what it finds on
a live inbox. Its first version printed every aria-label and a slice of the
page text, which published real people's names and a live member urn into a
transcript, and wrote full-page captures of the inbox to disk. The redactor
that replaced all that is the only thing standing between a future run and the
same leak -- and a redactor is exactly the kind of code that looks fine while
doing nothing.

IT IS TESTED IN BOTH DIRECTIONS ON PURPOSE. A redactor that collapses every
input to ``<NAME>`` would pass a leak-only test perfectly while destroying the
structure the probe exists to report. Three real defects were found by running
these two directions against each other while writing it: base64 thread ids
passed through untouched, ``Conversation List`` was flattened to ``<NAME>``,
and a one-letter middle initial broke the name run so ``Jane Q Public``
survived intact.

NO REAL IDENTITY APPEARS IN THIS FILE, AND THAT SENTENCE WAS FALSE WHEN IT WAS
FIRST WRITTEN. The version of this file added by ``206ca3d`` carried the actual
member urn the probe had printed, and a thread id truncated from the real one
rather than invented -- so the test written to prove the redactor removes real
identifiers contained two of them. That is the same defect as the probe it
guards, one level up.

**A SELF-TEST NEEDS A SHAPE-VALID LITERAL, NEVER A TRUE ONE.** An invented
nine-digit id exercises exactly the same regex and proves exactly the same
property. Truncating a real value is not inventing one: the surviving prefix is
still real, which is how the thread id got through a guard that caught the urn.

Every literal below is now invented and chosen only for its SHAPE -- two plain
tokens, a middle initial, non-ASCII letters, a nine-digit id, an opaque base64
blob. The non-ASCII case is written as escape sequences so this file itself
stays ASCII while still handing the redactor a non-ASCII string at runtime.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_PROBE = Path(__file__).resolve().parents[1] / "scripts" / "_probe_messaging.py"


def _probe_module():
    spec = importlib.util.spec_from_file_location("_probe_messaging", _PROBE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: Inputs that MUST be changed. Every one is a shape that leaked, or that the
#: redactor was measured failing on while it was being written.
MUST_REDACT = [
    ("Select conversation with Dara Whitfield", "conversation template"),
    ("Message from Ivo Karlsson", "other template"),
    # Invented, not truncated. 123456789 is nine digits like a real member id
    # and is not anybody's; the thread blob is base64-shaped and shares no
    # prefix with any real conversation.
    ("urn:li:member:123456789", "member urn"),
    ("https://www.linkedin.com/messaging/thread/2-QUJDREVGSElKS0xNTk9Q==/", "thread id"),
    ("Jane Q Public", "bare name with a one-letter initial"),
    ("Ingr\u00edd \u00d6sterberg", "non-ascii name"),
    # THE VANITY SLUG, ADDED 2026-09-03 AFTER IT WAS FOUND PASSING THROUGH
    # BYTE-IDENTICAL. `_redact` is called on `page.url` for EVERY page this
    # probe loads and had no slug rule at all, so a member's public identity
    # was printed by the function standing between this probe and a leak.
    #
    # THE SLUG IS SHAPE-VALID ON PURPOSE AND A PLACEHOLDER WOULD BREAK THIS.
    # The rule matches `/in/` followed by 3+ slug characters; `/in/<SLUG>` does
    # not match it, so the test would pass on a redactor that had lost the rule
    # entirely. The value is `some-real-slug-99`, already sanctioned in
    # SYNTHETIC_SLUGS in tests/test_no_committed_identity.py -- blessed there
    # rather than declared here, so no allowlist moves.
    ("https://www.linkedin.com/in/some-real-slug-99/", "vanity slug in a url"),
]

#: Inputs that MUST SURVIVE. These are the probe's actual output vocabulary;
#: if the redactor eats them it reports nothing while appearing to work.
MUST_SURVIVE = [
    "Star conversation",
    "Conversation List",
    "Global Navigation",
    "Open messenger dropdown menu",
    "you are on the messaging overlay",
    "Date posted",
]


@pytest.mark.parametrize("value,why", MUST_REDACT, ids=[w for _, w in MUST_REDACT])
def test_identity_is_redacted(value: str, why: str) -> None:
    redacted = _probe_module()._redact(value)
    assert redacted != value, f"{why}: passed through unredacted"


@pytest.mark.parametrize("value", MUST_SURVIVE)
def test_structure_survives(value: str) -> None:
    assert _probe_module()._redact(value) == value


#: Names `_redact` CANNOT see, because its name rule takes the maximal run of
#: letter-words and requires EVERY word in it to be capitalised -- so one
#: lowercase word ("to", "profile", "sent") exempts the run and the name with
#: it. These are not in MUST_REDACT because MUST_REDACT tests `_redact`, and
#: `_redact` is deliberately NOT where this is fixed.
LEAKED_BESIDE_A_LOWERCASE_WORD = [
    "Reply to Jane Public",
    "Open Jane Public profile",
    "Send message to Jane Q Public",
    "Jane Public sent a message",
]


def _shapes(labels: list[str]) -> list[str]:
    html = "".join('<a aria-label="%s"></a>' % one for one in labels)
    return _probe_module()._label_shapes(html)


@pytest.mark.parametrize("value", LEAKED_BESIDE_A_LOWERCASE_WORD)
def test_a_name_beside_a_lowercase_word_is_blanked_on_the_label_path(value):
    """THE FIX IS AT THE TALLY, WHICH IS WHY THIS TESTS `_label_shapes`.

    Making `_redact` itself blank any capitalised run closes these four and
    also blanks 32 shapes across this repo's committed fixtures that are JOB
    TITLES -- "Apply to Staff Engineer", "Back End Developer with
    verification". No property of the STRING separates a job title from a
    person's name, which is the premise `shape.census_redact_rare` rests on:
    furniture repeats across a surface and a member does not. The
    discriminator is the COUNT, and the count does not exist until the shapes
    merge.
    """
    shaped = _shapes([value])[0]
    for token in ("Jane", "Public"):
        assert token not in shaped, (value, shaped)


def test_the_template_survives_what_the_count_rule_blanks():
    """BLANKED, NOT DROPPED -- the structure is the whole point of the probe.

    A redactor that returned "<redacted>" for the entire label would pass the
    test above perfectly and report nothing, which is the failure mode this
    file was written against in the first place.
    """
    assert _shapes(["Reply to Jane Public"])[0].startswith("Reply to <redacted>")
    assert _shapes(["Jane Public sent a message"])[0].endswith("sent a message x1")


def test_repeated_furniture_is_not_eaten_by_the_count_rule():
    """THE COST CONTROL. The count rule fires at count == 1 ONLY, so a label
    the surface repeats keeps its text -- which is what makes the rule
    affordable on furniture while still blanking a singleton name."""
    rows = _shapes(["Conversation List", "Conversation List",
                    "Global Navigation", "Global Navigation"])
    assert "Conversation List x2" in rows, rows
    assert "Global Navigation x2" in rows, rows


def test_the_count_rule_is_actually_reached():
    """A CONTROL FOR THE CONTROL. If `_label_shapes` stopped calling
    `census_redact_rare`, every assertion above about blanking would fail --
    but a future edit could also make the rule unreachable while these pass by
    accident, so the singleton/repeat DIFFERENCE is asserted directly."""
    once = _shapes(["Reply to Jane Public"])[0]
    twice = _shapes(["Reply to Jane Public", "Reply to Jane Public"])[0]
    assert "<redacted>" in once
    assert twice.endswith("x2")


def _tagged(label: str, href: str | None, times: int = 1) -> list[str]:
    attrs = 'aria-label="%s"' % label
    if href:
        attrs = 'href="%s" ' % href + attrs
    return _probe_module()._label_shapes(("<a %s></a>" % attrs) * times)


#: Both spellings LinkedIn writes member links in -- MEASURED to appear on one
#: page -- plus a company link, because the structural rule covers both entity
#: kinds and a test of only one would leave half of it unexercised.
#:
#: EVERY ID HERE IS SHAPE-VALID AND DECLARED. `_ENTITY_HREF` needs real slug
#: and id characters after the prefix, so a placeholder would stop the rule
#: firing and the test would pass on a redactor that had lost it. The first
#: version of this list used a bare ascending five-digit company id and the
#: identity guard failed it within the minute -- correctly, since it was not in
#: SYNTHETIC_IDS and nothing about it says invented. THE VALUE IS NOT QUOTED
#: HERE, and that is the point: naming it in the comment put it straight back
#: into the file and failed the guard a SECOND time, on the very line
#: explaining the first. A retraction that must quote a forbidden literal
#: cannot be written in the file that forbids it. `5300011` and
#: `some-real-slug-99` are both
#: already sanctioned in tests/test_no_committed_identity.py, so no allowlist
#: moves and no plant is pinned.
ENTITY_HREFS = ["/in/some-real-slug-99/",
                "https://www.linkedin.com/in/some-real-slug-99/",
                "/company/5300011/"]


@pytest.mark.parametrize("href", ENTITY_HREFS)
def test_an_entity_link_is_refused_however_often_it_repeats(href):
    """THE LAYER THE COUNT RULE CANNOT PROVIDE.

    `census_redact_rare` rests on "furniture repeats and a member does not",
    and that premise FAILS on a conversation surface, where one participant
    appearing twice is normal rather than exceptional. Measured before this
    layer existed: at count 2 the name shipped verbatim.

    A destination does not depend on the premise. `/in/<slug>` is a link to a
    member however the label reads and however many times it appears, so the
    refusal is on the STRUCTURE of the control -- the same move
    `shape.census_href_identifies_entity` makes for the census.
    """
    for times in (1, 2, 3):
        row = _tagged("Reply to Jane Public", href, times)[0]
        for token in ("Jane", "Public"):
            assert token not in row, (href, times, row)


def test_the_pairing_survives_attribute_order():
    """MEASURED, NOT ASSUMED. LinkedIn writes these attributes in both orders,
    and a pattern requiring `aria-label` before `href` matches nothing on half
    the controls -- an absence that reads exactly like a clean page."""
    first = _tagged("Reply to Jane Public", "/in/some-real-slug-99/", 2)[0]
    both = _probe_module()._label_shapes(
        '<a aria-label="Reply to Jane Public" href="/in/some-real-slug-99/"></a>' * 2
    )[0]
    assert "Jane" not in first and "Jane" not in both, (first, both)


def test_a_non_entity_href_is_not_swallowed():
    """THE OTHER DIRECTION. A rule that called everything an entity link would
    pass every leak test and report nothing at all."""
    row = _tagged("Star conversation", "/messaging/", 2)[0]
    assert row == "Star conversation x2", row


def test_the_residual_gap_is_pinned_rather_than_hidden():
    """WHAT NEITHER LAYER COVERS, asserted so it cannot be forgotten.

    A control with NO href whose repeated label carries a name: the structural
    rule has no destination to read, and the count rule declines above one.
    The census documents the same residual for the same reason. Pinned as a
    KNOWN state -- if a future change closes it, this test fails and the gap
    gets deleted from the docs deliberately rather than by drift.
    """
    row = _probe_module()._label_shapes(
        '<button aria-label="Reply to Jane Public"></button>' * 2
    )[0]
    assert "Jane Public" in row, (
        "the hrefless repeated-name gap is CLOSED -- update this test and the "
        "probe's docstring, which both still describe it as open: %r" % row
    )


def test_the_probe_writes_no_capture() -> None:
    """The other half of the leak was files, not prints.

    Checked as a property of the SOURCE rather than by running it: the probe
    drives a live browser, so the only cheap way to assert it never writes a
    capture is that it contains no write call at all.
    """
    source = _PROBE.read_text(encoding="utf-8")
    for forbidden in ("write_text(", "write_bytes(", "open("):
        assert forbidden not in source, (
            f"{_PROBE.name} contains {forbidden!r}: this probe reads a live "
            "inbox and must never persist one"
        )


def test_probe_does_not_print_page_text() -> None:
    """A 900-character slice of the inbox is how the member urn escaped."""
    source = _PROBE.read_text(encoding="utf-8")
    assert "text head" not in source
