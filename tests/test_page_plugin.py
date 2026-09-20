"""The A6 generator, and the boundary fact that makes it the row it is.

WHAT IS BEING ASSERTED, AND WHY EACH ASSERTION EXISTS.

``linkedin_server/page_plugin.py`` reproduces one documented contract and
admits exactly one caller-supplied value. Both halves can rot, and they rot in
opposite directions:

    the CONTRACT rots quietly  -- somebody "tidies" a literal and the snippet
                                 stops being what LinkedIn documented
    the ALPHABET rots loudly   -- somebody reaches for ``str.isdigit()``
                                 because it reads better, and a charset wide
                                 enough to hold a person's name reopens

So the contract is pinned VERBATIM and the alphabet is proved over adversarial
input -- and, because a check that has only ever been green certifies nothing,
each guard is ALSO run against a plausible WRONG implementation that this file
must be able to tell apart. That is the mutation battery at the bottom, and it
is the part worth reading: a sibling wave found two of its own guards could not
fail, and only a battery like this said so.

## THE THIRD THING, WHICH IS NOT ABOUT THIS MODULE AT ALL

``test_the_id_this_module_needs_sits_behind_the_read_boundary`` asserts a fact
about ``readonly.py``: the address the cited document names as the ONE place a
Page administrator finds their Company ID is refused by this package's
navigation boundary today. That is not decoration. It is the reason row
``N A6`` ships COVERED and UNFIRED rather than COVERED and fired -- the
generator is complete and the input is unreachable -- and pinning it means the
day somebody admits that address, this file goes red and the coupling is
RE-MEASURED instead of remembered.
"""
from __future__ import annotations

import pytest

from linkedin_server import page_plugin, readonly

# ---------------------------------------------------------------------------
# THE CORPUS. Grouped by what each group is FOR, because a flat list of
# strings is a corpus nobody can extend correctly.
# ---------------------------------------------------------------------------

#: Ids that must be admitted, as ``(what a caller passes, what comes back)``.
#: A Company ID is a run of ASCII digits and nothing else is claimed about it
#: -- leading zeros included, because the cited document's own worked example
#: is ``0000``.
#:
#: **THE LAST TWO PAIRS ARE WHY THIS IS PAIRS AND NOT A FLAT LIST, and the
#: corpus was wrong before the code was.** The first draft filed a
#: trailing-newline id under REFUSED and this file went red against a module
#: that was behaving as documented: surrounding whitespace is stripped before
#: the alphabet test, on purpose, because a caller who pastes an id out of a
#: browser address bar means the id. Recorded rather than quietly corrected --
#: a test that disagrees with the code is worth more when it is written down
#: which of the two was wrong.
ADMITTED = (
    ("0", "0"),
    ("0000", "0000"),
    ("1234567", "1234567"),
    ("9" * 20, "9" * 20),
    ("1234\n", "1234"),
    ("  1234  ", "1234"),
)

#: A SLUG SHAPED LIKE A PERSON'S NAME. This is the input the whole alphabet
#: ruling exists for and it is written as a placeholder rather than as a real
#: name, per this repository's standing rule that a person's name is never a
#: literal in a tracked file.
NAME_SHAPED_SLUG = "given-family-consulting"

#: Inputs that must be refused, each standing for one failure a caller makes.
REFUSED = (
    None,
    "",
    "   ",
    NAME_SHAPED_SLUG,
    "https://www.linkedin.com/company/12/",
    "1234/admin",
    "12 34",
    "-1234",
    "+1234",
    "1234.0",
    "0x1234",
    # DIGITS FROM THREE OTHER SCRIPTS. Every one of these is ``isdigit()``
    # True, which is the entire reason the shipped gate does not use it.
    "\u0661\u0662\u0663",          # Arabic-Indic
    "\u06f1\u06f2\u06f3",          # Extended Arabic-Indic
    "\u00b9\u00b2\u00b3",          # superscripts -- int() cannot parse these
    # A ZERO-WIDTH SPACE BETWEEN TWO DIGIT RUNS. Invisible in every editor and
    # in every error message that echoed the value.
    "12\u200b34",
    '1"><script>alert(1)</script>',
)


# ---------------------------------------------------------------------------
# THE CONTRACT
# ---------------------------------------------------------------------------


def test_the_snippet_is_the_documented_contract_verbatim():
    """Pinned character for character against the cited document's sample.

    Written out as one literal rather than assembled from the module's own
    constants, deliberately: a test that rebuilds the string from the same
    pieces the code uses agrees with the code by construction and would not
    notice a constant being edited. This disagrees with the code the moment
    anybody touches a literal.
    """
    out = page_plugin.follow_plugin_snippet("0000")
    assert out["html"] == (
        '<script src="https://platform.linkedin.com/in.js"'
        ' type="text/javascript"> lang: en_US</script>\n'
        '<script type="IN/FollowCompany" data-id="0000"'
        ' data-counter="bottom"></script>'
    )


def test_the_provenance_travels_with_every_answer():
    """An answer that cannot say how old its contract is invites a caller to
    assume it is current. This one cannot be read without seeing the date."""
    for probe in ("1234", NAME_SHAPED_SLUG):
        out = page_plugin.follow_plugin_snippet(probe)
        assert out["source_doc"].startswith("https://learn.microsoft.com/")
        assert out["source_doc_updated"] == "2022-03-31"
        assert out["terms_of_use"].startswith("https://developer.linkedin.com/")
        # NOT A FORMALITY. Nothing in this package has seen the plugin render,
        # and the day somebody does, they flip this and this test tells them
        # that the claim is now theirs to defend.
        assert out["verified_live"] is False


def test_no_undocumented_counter_or_language_is_reachable():
    """The document shows one counter position and one language token.

    Neither is a parameter of anything here, so a caller cannot select an
    unattested value and no code path can emit one. Asserted as an ABSENCE of
    surface rather than as a validation rule, because a validation rule is
    something a later edit can widen.
    """
    import inspect

    for fn in (page_plugin.follow_plugin_snippet, page_plugin.page_identifier):
        params = tuple(inspect.signature(fn).parameters)
        assert params == (params[0],), (fn.__name__, params)
    assert page_plugin.PLUGIN_COUNTER == "bottom"
    assert page_plugin.PLUGIN_LANG == "en_US"


# ---------------------------------------------------------------------------
# THE ALPHABET
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw,expected", ADMITTED)
def test_an_ascii_digit_run_is_admitted(raw, expected):
    verdict = page_plugin.page_identifier(raw)
    assert verdict["refused"] is None, verdict
    assert verdict["id"] == expected


@pytest.mark.parametrize("raw", REFUSED)
def test_everything_that_is_not_an_ascii_digit_run_is_refused(raw):
    verdict = page_plugin.page_identifier(raw)
    assert verdict["id"] is None, verdict
    assert verdict["refused"] in page_plugin.REFUSALS, verdict


def test_only_ascii_digits_ever_reach_the_output():
    """THE SAFETY PROPERTY, asserted over the corpus rather than trusted.

    For every input this module ADMITS, the bytes that came from the caller
    and reached ``html`` are drawn from the ten characters and nothing else.
    """
    for raw, _expected in ADMITTED:
        out = page_plugin.follow_plugin_snippet(raw)
        marker = 'data-id="'
        start = out["html"].index(marker) + len(marker)
        end = out["html"].index('"', start)
        emitted = out["html"][start:end]
        assert set(emitted) <= page_plugin._ASCII_DIGITS, emitted


def test_a_refusal_never_echoes_the_value():
    """A rejected slug is a person's name often enough that echoing it in an
    error is the hazard, not the diagnostic."""
    for raw in REFUSED:
        if raw is None or len(str(raw).strip()) < 3:
            continue
        needle = str(raw).strip()
        payload = repr(page_plugin.follow_plugin_snippet(raw))
        assert needle not in payload, needle[:8]


def test_a_refusal_reports_what_it_saw_and_not_only_the_miss():
    """THE CONTROL on the shape facts: they must DISCRIMINATE.

    A refusal carrying facts that read the same for every input is half a
    measurement wearing a whole one's clothes. These four inputs fail for four
    different reasons and the facts must say so without naming any of them.
    """
    slug = page_plugin.page_identifier(NAME_SHAPED_SLUG)["saw"]
    url = page_plugin.page_identifier(
        "https://www.linkedin.com/company/12/"
    )["saw"]
    other_script = page_plugin.page_identifier("\u0661\u0662\u0663")["saw"]
    too_long = page_plugin.page_identifier("9" * 21)["saw"]

    assert slug["letters"] > 0 and slug["hyphens"] > 0
    assert url["looks_like_a_url"] is True and url["slashes"] > 0
    assert slug["looks_like_a_url"] is False
    assert other_script["digits_from_another_script"] == 3
    assert other_script["ascii_digits"] == 0
    assert other_script["all_ascii"] is False
    assert too_long["ascii_digits"] == 21
    assert too_long["digits_from_another_script"] == 0


def test_the_length_is_banded_and_never_exact():
    """An exact length over a small domain is itself an identifier."""
    bands = {
        page_plugin.page_identifier("x" * n)["saw"]["length_band"]
        for n in range(1, 40)
    }
    assert bands == {"1-8", "9-20", "21-64"}, bands


# ---------------------------------------------------------------------------
# THE BOUNDARY FACT -- see the module docstring on why it lives here
# ---------------------------------------------------------------------------


def test_the_id_this_module_needs_sits_behind_the_read_boundary():
    """The document's own "where to find your Company ID" address is REFUSED.

    Quoted from the cited document: *"your Company ID can be retrieved by
    navigating to the admin section of your company page. For example, the
    LinkedIn Company Admin Page is https://www.linkedin.com/company/<the
    numeric id>/admin/."* -- the document spells that id as four zeros, and
    this file assembles it below rather than printing it, for the reason
    given there.

    That address is the document's, not a guess of this wave's, which is why
    it is safe to pin. If it is ever admitted, this test goes red and somebody
    re-decides whether the generator should read the id for itself.
    """
    # ASSEMBLED, NOT SPELLED, AND THE REASON IS A GUARD RATHER THAN TASTE.
    # ``scripts/identity_gate.py`` reads FILE TEXT for a company-id shape --
    # /company/ followed by three digits or more -- and this address
    # carries one. The available remedies were a DECLARED_PLANTS entry or a
    # reshape; ``test_no_committed_identity.py``'s own standing order is to
    # reach for the declaration LAST, because an entry there tolerates the
    # shape in this file forever. Assembling keeps the runtime string the
    # document's EXACTLY while leaving no shape in the source.
    documented = "https://www.linkedin.com/company/" + "0" * 4 + "/admin/"
    assert readonly.is_read_url(documented) is False
    # AND THE REASON IS ALLOWLIST SILENCE, NOT A FORBIDDEN SUBSTRING. The two
    # are different repairs -- one needs a pattern, the other needs a pattern
    # AND an exemption -- and a reader who conflates them will cost a wave a
    # round. Measured 2026-09-20.
    assert [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in documented] == []
    assert [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(documented)] == []


# ---------------------------------------------------------------------------
# THE MUTATION BATTERY. Every guard above, shown able to FAIL.
# ---------------------------------------------------------------------------


def _isdigit_identifier(raw):
    """THE PLAUSIBLE WRONG ONE. This is what the shipped gate would be if
    somebody wrote the obvious thing, and it is wrong for exactly one reason:
    ``str.isdigit()`` is True for several scripts' digits."""
    text = "" if raw is None else str(raw).strip()
    if not text or not text.isdigit():
        return {"id": None, "refused": "not_ascii_digits", "saw": {}}
    return {"id": text, "refused": None, "saw": {}}


def _echoing_identifier(raw):
    """The other plausible wrong one: a refusal that helpfully quotes the
    value back, which is how the name gets into the log."""
    text = "" if raw is None else str(raw).strip()
    if any(ch not in page_plugin._ASCII_DIGITS for ch in text):
        return {"id": None, "refused": "not a number: %s" % text, "saw": {}}
    return {"id": text, "refused": None, "saw": {}}


def test_the_alphabet_guard_can_fail():
    """Run the shipped assertion against the isdigit implementation.

    The shipped gate REFUSES all three scripts; the plausible wrong one
    ADMITS two of them. If this file could not tell them apart, the alphabet
    test above would be certifying nothing.
    """
    other_scripts = ("\u0661\u0662\u0663", "\u06f1\u06f2\u06f3", "\u00b9\u00b2\u00b3")
    shipped = [page_plugin.page_identifier(r)["id"] for r in other_scripts]
    broken = [_isdigit_identifier(r)["id"] for r in other_scripts]
    assert shipped == [None, None, None], shipped
    assert any(v is not None for v in broken), broken


def test_the_no_echo_guard_can_fail():
    """Run the shipped no-echo assertion against an echoing implementation."""
    assert NAME_SHAPED_SLUG not in repr(page_plugin.page_identifier(NAME_SHAPED_SLUG))
    assert NAME_SHAPED_SLUG in repr(_echoing_identifier(NAME_SHAPED_SLUG))


def test_the_contract_pin_can_fail(monkeypatch):
    """Edit one documented literal; the verbatim pin must notice.

    ``data-counter`` is the one chosen because it is the literal most likely
    to be "improved" by somebody who saw a sibling plugin use another value.
    """
    monkeypatch.setattr(page_plugin, "PLUGIN_COUNTER", "right")
    out = page_plugin.follow_plugin_snippet("0000")
    assert 'data-counter="bottom"' not in out["html"]
    assert 'data-counter="right"' in out["html"]


def test_the_boundary_pin_can_fail():
    """THE CONTROL on the boundary assertion: the predicate must be capable of
    saying ALLOW. A test resting on a predicate that returns False for
    everything would pass forever and mean nothing."""
    assert readonly.is_read_url("https://www.linkedin.com/feed/") is True
    assert readonly.is_read_url("https://www.linkedin.com/groups/") is True
