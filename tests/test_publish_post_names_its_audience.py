"""A broadcast may not go out at an audience nobody read.

THE DEFECT, 2026-09-03. ``linkedin_publish_post(text, confirm_token)`` had NO
visibility parameter, and its docstring said "visibility", "audience",
"Anyone" and "connections" exactly ZERO times -- measured, not estimated. What
it did say at length was REACH: a follower count and three impression figures.

THAT WORD COLLISION IS HOW IT HID. "Audience" was present in the spec meaning
HOW MANY -- ``residue`` opens "IRREVERSIBLE IN AUDIENCE" -- while the SETTING
meaning WHO was absent everywhere. A reader searching for the word found it
and stopped. Reach is how many people saw the last post; audience is who gets
the next one, and it is a control on the composer.

THE CONTROL WAS SEEN AND NEVER NAMED. A live capture on 2026-08-31 read 31
controls off the composer and wrote the finding down in three words -- "and an
audience control" -- in ``_audit/2026-08-31-linkedin-perform.md``. Seen,
recorded, never named, never read, never wired. Re-measured 2026-09-03 at 32
controls on a settle-consistent reading: the dialog's only aria-label-named
button with ``aria-expanded="false"`` is it, and the census REDACTS its
accessible name, so nothing in this package can say what it is set to.

WHY A REFUSAL AND NOT A DEFAULT. A post is declared ``irreversible`` and its
outcome is declared ``Unverifiable``, so a wrong audience can be neither
detected afterwards nor taken back. Every other gate here QUOTES the state it
is about to change -- ``set_open_to_work`` prints "Open to work <dot>
Recruiters only" verbatim off the topcard. For a post, the state that decides
who sees it is unread.

WHAT THIS FILE HAS TO PROVE, and it is BOTH directions. A guard that can only
refuse is a brick, and a brick gets deleted by the next person who wants the
feature. So:

    * it refuses TODAY, on both doors -- the preview that would mint a token
      and the confirmation that would consume one already held;
    * it reaches NO PAGE while refusing, because a refusal that first opened
      the composer would spend the autosave cost the census documents to say
      something already known;
    * and it STOPS refusing the moment the reader exists, which is asserted by
      attaching one and watching the call go through.

The third is the important one. The guard is keyed on whether
``dom.read_post_composer_audience`` exists, not on a flag somebody has to
remember to flip -- and a flag is exactly what went stale in the seven spec
sentences corrected the same day.
"""

from __future__ import annotations

import inspect

import pytest

from linkedin_server import dom, server, writes

_SENTINEL = {"reached": "_write_tool", "performed": False}


@pytest.fixture
def never_writes(monkeypatch):
    """``_write_tool`` replaced by a tripwire that records being reached.

    Not an exception, because "did the guard run" and "did anything explode"
    are different questions and only the first is under test here.
    """

    async def _tripwire(*args, **kwargs):
        return dict(_SENTINEL)

    monkeypatch.setattr(server, "_write_tool", _tripwire)


def test_the_reader_that_would_lift_this_does_not_exist_yet():
    """The premise of the whole file, asserted rather than assumed.

    If somebody builds the reader, this goes red FIRST and names what to do:
    the refusal below is now dead code and the audience belongs in the gate.
    """
    assert not server._composer_audience_is_readable()
    assert not hasattr(dom, server._COMPOSER_AUDIENCE_READER)


async def test_it_refuses_with_no_token(never_writes):
    """The preview door: no token, and nothing is minted."""
    out = await server.linkedin_publish_post(text="hello")
    assert out["error"] == "audience_unread"
    assert out["performed"] is False
    assert out != _SENTINEL


async def test_it_refuses_with_a_token_already_in_hand(never_writes):
    """The confirm door, and it matters MORE than the preview door.

    A token minted before this guard existed is still a live token. If the
    refusal sat only on the no-token branch, the one caller who already held
    one would walk straight past it -- which is the shape of every gate that
    checks the cheap path and not the expensive one.
    """
    out = await server.linkedin_publish_post(text="hello", confirm_token="anything")
    assert out["error"] == "audience_unread"
    assert out["performed"] is False
    assert out != _SENTINEL


async def test_refusing_reaches_no_page_and_no_write_machinery(never_writes):
    """It costs nothing. A composer load may autosave a draft nothing can see."""
    for token in ("", "anything"):
        out = await server.linkedin_publish_post(text="hello", confirm_token=token)
        assert out.get("reached") is None, (
            "the refusal reached _write_tool, which would load the composer "
            "-- CENSUS_SURFACE_COST records that opening it may autosave a "
            "draft this server has no surface to detect or remove"
        )


async def test_it_stops_refusing_the_moment_the_audience_can_be_read(
    monkeypatch, never_writes
):
    """THE ARM THAT PROVES THIS IS A GATE AND NOT A BRICK.

    Attach a reader by the name the guard looks for and the call goes
    through. Without this, a guard that refuses unconditionally is
    indistinguishable from one whose condition never fires, and the next
    person to want this feature deletes it rather than satisfying it.
    """

    async def _fake_reader(page):  # pragma: no cover - never called here
        return {"audience": "Anyone"}

    monkeypatch.setattr(
        dom, server._COMPOSER_AUDIENCE_READER, _fake_reader, raising=False
    )
    assert server._composer_audience_is_readable()

    out = await server.linkedin_publish_post(text="hello")
    assert out == _SENTINEL, "the guard did not stand down for a real reader"


def test_the_refusal_names_the_reader_the_guard_actually_looks_for():
    """The message and the condition may not drift apart.

    A refusal that names the wrong fix is worse than one that names none: it
    sends the next person to build something that will not lift it.
    """
    refusal = server._publish_post_audience_refusal()
    assert server._COMPOSER_AUDIENCE_READER in refusal["what_would_lift_it"]


def test_the_refusal_says_what_it_is_not_claiming():
    """It may not assert that a post would go out public.

    Nobody measured that. The redaction is why the current value is unknown,
    and "unknown" is the claim -- a refusal that overstated its evidence to
    sound more urgent would be the same confident string this package's
    reversibility rules exist to stop.
    """
    refusal = server._publish_post_audience_refusal()
    not_claimed = refusal["not_claimed"].casefold()
    assert "unmeasured" in not_claimed
    assert "does not assert" in not_claimed


def test_the_tool_still_takes_no_audience_argument_and_says_so():
    """The signature and the docstring, checked against each other.

    THE ORIGINAL DEFECT WAS A SILENCE, so silence is what this pins. Zero
    occurrences of the word was the whole of it: a tool that broadcasts and
    never mentions who to is one nobody thinks to ask about. If the parameter
    is ever added, this fails and sends somebody to the guard above -- which
    is the correct order, because accepting an audience it cannot apply would
    be worse than accepting none.
    """
    signature = inspect.signature(server.linkedin_publish_post)
    assert "audience" not in signature.parameters
    assert "visibility" not in signature.parameters

    doc = (server.linkedin_publish_post.__doc__ or "").casefold()
    assert "audience" in doc
    assert "visibility" in doc
    assert "refuses" in doc


def test_the_spec_still_calls_this_irreversible_and_unverifiable():
    """The two facts the refusal rests on, read off the spec rather than typed.

    If either stopped being true the argument for refusing would be weaker,
    and this is where that would surface.
    """
    spec = writes.spec_for_action("publish_post")
    assert spec.irreversible is True
    assert spec.unverifiable is not None
    assert "IRREVERSIBLE IN AUDIENCE" in spec.residue
