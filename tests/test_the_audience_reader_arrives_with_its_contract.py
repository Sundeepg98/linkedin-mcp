"""Defining a NAME lifts the publish refusal. A name is not a contract.

WHAT IS ALREADY BUILT, and it is good: ``server._publish_post_audience_refusal``
holds ``linkedin_publish_post`` shut because nothing here can say who a post
would reach, and ``server._composer_audience_is_readable()`` decides when to
stop refusing by FEATURE DETECTION::

    return callable(getattr(dom, _COMPOSER_AUDIENCE_READER, None))

The reasoning beside it is right and this file does not dispute it -- a boolean
"would have to be flipped by hand and would go stale exactly the way the seven
spec sentences corrected on 2026-09-03 did". Keying on the capability beats
keying on a flag.

**THE PROPERTY THAT FOLLOWS FROM IT, WHICH NOBODY WROTE DOWN.** The act that
lifts the refusal is *defining a function with a particular name on* ``dom``.
Not landing a reader. Not proving it reads anything. A stub, a placeholder, a
``def read_post_composer_audience(): pass`` written to sketch an interface --
each of them satisfies ``callable(...)`` and each of them re-arms an action this
server declares IRREVERSIBLE and whose outcome it declares UNVERIFIABLE.

**THIS IS A MEASURED DEFECT CLASS IN THIS REPOSITORY, NOT A HYPOTHETICAL.**
``_redact`` was admitted to ``readonly._SANITISERS`` "on the strength of its
NAME and turned out to carry no slug rule at all". The remedy adopted then is
the remedy adopted here: ``_relation`` was admitted **with the test that proves
its contract**. This file is that requirement, written BEFORE the reader exists
rather than after it goes wrong -- which is the only order in which it costs
nothing.

WHAT THIS FILE DOES NOT DO. It does not check that the reader is CORRECT; it
cannot, because the thing the reader must return has never been established.
Amendment A9 of ``_audit/2026-09-03-linkedin-gap-blockers.md`` rules the post
audience admissible as a CLOSED VOCABULARY on the ``dom.MESSAGING_FILTERS``
precedent, and names the blocker: *"the audience option set has never been
written down in this repository"*, so it "has to be established before it can
be written". Until that live read is taken there is no vocabulary to assert
membership in. **So this file asserts the one thing available before the
measurement: that the reader does not arrive alone.**

SHOWN FAILING before admission: with the attribute injected onto ``dom`` at
runtime and no contract test on disk, the assertion goes red naming both. See
``_audit/2026-09-05-article-publish.md``.
"""

import pathlib

import pytest

from linkedin_server import dom, server

_TESTS = pathlib.Path(__file__).resolve().parent

#: A contract test for the reader must match one of these. Kept as a prefix
#: match rather than an exact filename so the author names their own file.
CONTRACT_TEST_PREFIXES = ("test_post_composer_audience", "test_composer_audience")


def test_the_refusal_is_still_keyed_on_a_name_and_this_is_the_name() -> None:
    """The control. Everything below is void if this wiring is not what I read.

    Pins the exact string the refusal is keyed on. If somebody renames the
    reader, this fails HERE -- with the reason -- rather than leaving the file
    below silently guarding an attribute nothing consults.
    """
    assert server._COMPOSER_AUDIENCE_READER == "read_post_composer_audience"
    assert callable(server._composer_audience_is_readable)
    assert callable(server._publish_post_audience_refusal)


def test_the_refusal_actually_names_the_audience_as_its_reason() -> None:
    """A second control: that the refusal this file protects is the live one."""
    refusal = server._publish_post_audience_refusal()
    assert refusal["error"] == "audience_unread"
    assert "audience" in refusal["message"].lower()


def _contract_test_exists() -> list[str]:
    return sorted(
        p.name
        for p in _TESTS.glob("test_*.py")
        if p.name.startswith(CONTRACT_TEST_PREFIXES)
    )


def test_the_audience_reader_does_not_arrive_without_a_contract_test() -> None:
    """The assertion. Defining the name is not enough to re-arm publishing."""
    reader = getattr(dom, server._COMPOSER_AUDIENCE_READER, None)
    if not callable(reader):
        pytest.skip(
            "the reader does not exist yet, which is the state this file was "
            "written in; it arms itself the moment somebody adds the name"
        )
    assert _contract_test_exists(), (
        f"dom.{server._COMPOSER_AUDIENCE_READER} now exists, so "
        "server._composer_audience_is_readable() returns True and "
        "linkedin_publish_post no longer refuses -- an IRREVERSIBLE broadcast "
        "under his own name is re-armed by the existence of a name. No test "
        f"file starting with {CONTRACT_TEST_PREFIXES} is on disk. Add one that "
        "proves what the reader RETURNS, against the closed vocabulary "
        "Amendment A9 rules admissible -- the precedent is _relation, admitted "
        "to _SANITISERS with the test that proves its contract, after _redact "
        "was admitted on the strength of its name and carried no rule at all."
    )


def test_this_guard_can_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """The instrument shown failing, with the detector factored out.

    Injects the name onto ``dom`` and asserts the guard above turns red. The
    mutation is a monkeypatch, so no file on a contended tree is edited and the
    demonstration costs no staging window. If a contract test IS on disk by
    then, this asserts the guard passes instead -- both branches are real
    outcomes and the test says which one it took.
    """
    monkeypatch.setattr(dom, server._COMPOSER_AUDIENCE_READER, lambda: None, raising=False)
    assert callable(getattr(dom, server._COMPOSER_AUDIENCE_READER, None))
    assert server._composer_audience_is_readable() is True, (
        "the injected name did not satisfy the server's own feature detection, "
        "so this file is guarding something other than the live mechanism"
    )
    if _contract_test_exists():
        test_the_audience_reader_does_not_arrive_without_a_contract_test()
        return
    with pytest.raises(AssertionError, match="no longer refuses"):
        test_the_audience_reader_does_not_arrive_without_a_contract_test()
