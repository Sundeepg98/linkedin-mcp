"""His all-activity list is admitted, in the ``/in/me/`` form, and its
NEIGHBOURS are not.

The live lane, 2026-09-24, Part 2 (d) of the orchestrator's integration order:
"Admit /in/me/recent-activity/all/ (his own activity, a closed segment) so his
own poll posts can be found" -- census ``M C85``. The argument is on the line
in ``linkedin_server/readonly.py``; the record is
``_audit/2026-09-23-live-lane-session-1.md``, Part 2 (d).

THE SHAPE IS LANE L1's (``tests/test_l1_self_scoped_admissions.py``), and it is
reused rather than re-derived, because an allowlist entry is worth exactly
what its edges are worth: the two admitted spellings, a table of neighbours
that must stay refused, a CONTROL that removes this one line and re-runs
everything (so no refusal below is carried by the line's absence, and the
revert path is proven), the blast radius measured with the shipped
instrument, and a structural check that the line can name nobody.

EVERY VARIABLE SEGMENT IS A PLACEHOLDER. ``someone-else`` carries the token
the identity guard sanctions. Nothing here names or addresses a real person.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

from linkedin_server import readonly

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"
OTHER = "someone-else"
TARGET = f"{B}/in/me/recent-activity/all/"
ROW = "M C85"

#: What must stay refused, each with its reason. The articles list is NOT
#: here: it is admitted by its own line (lane L1), and this file asserts that
#: separately so the two lines cannot be mistaken for one.
NEIGHBOURS: tuple[tuple[str, str], ...] = (
    (f"{B}/in/{OTHER}/recent-activity/all/",
     "ANOTHER MEMBER'S activity. Loading a third party's profile pages leaves "
     "them a durable record; the `me` form is the whole permission"),
    (f"{B}/in/me/recent-activity/", "the activity root"),
    (f"{B}/in/me/recent-activity/comments/",
     "other people's posts he commented on"),
    (f"{B}/in/me/recent-activity/reactions/",
     "other people's posts he reacted to"),
    (f"{B}/in/me/recent-activity/shares/", "another activity tab, never named"),
    (f"{B}/in/me/recent-activity/images/", "another activity tab, never named"),
    (f"{B}/in/me/recent-activity/videos/", "another activity tab, never named"),
    (f"{B}/in/me/recent-activity/documents/", "another activity tab, never named"),
    (f"{B}/in/me/recent-activity/events/", "another activity tab, never named"),
    (f"{B}/in/me/recent-activity/all/?x=1", "a QUERY"),
    (f"{B}/in/me/recent-activity/all/detail/", "a SUB-PATH"),
    (f"{B}/in/me/recent-activity/allx/", "a longer word"),
    (f"{B}/in/me/recent-activity/all/../../../in/{OTHER}/",
     "a TRAVERSAL onto a third party's profile"),
    (f"{B}/in/me/recent-activity/all/../../../mypreferences/d/close-account",
     "a TRAVERSAL onto an account-ending address no substring names"),
)

CARRIER_NEEDLE = "recent-activity/all"


def _allowed(url: str, patterns=None) -> bool:
    pool = readonly._ALLOWED_URL_PATTERNS if patterns is None else patterns
    return any(pattern.match(url) for pattern in pool)


def _carriers() -> list[re.Pattern[str]]:
    return [p for p in readonly._ALLOWED_URL_PATTERNS if CARRIER_NEEDLE in p.pattern]


def _family() -> list[str]:
    return [TARGET, TARGET.rstrip("/")] + [url for url, _why in NEIGHBOURS]


def test_the_target_is_admitted_through_the_shipped_gate():
    """Both spellings, through ``is_read_url`` -- gate one AND gate two."""
    assert readonly.is_read_url(TARGET), ROW
    assert readonly.is_read_url(TARGET.rstrip("/")), ROW


def test_the_target_carries_no_forbidden_substring():
    """No exemption was needed and none was added: gate one is untouched."""
    carried = [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in TARGET.lower()]
    assert carried == [], carried


@pytest.mark.parametrize("url,why", NEIGHBOURS)
def test_the_neighbours_are_refused(url, why):
    assert not readonly.is_read_url(url), why


def test_the_articles_list_is_admitted_by_its_own_line_not_this_one():
    """TWO LINES, NOT ONE: removing this line leaves the articles list
    admitted, so neither admission is standing in for the other."""
    articles = f"{B}/in/me/recent-activity/articles/"
    assert readonly.is_read_url(articles)
    survivors = tuple(p for p in readonly._ALLOWED_URL_PATTERNS if p not in _carriers())
    assert _allowed(articles, survivors)


def test_exactly_one_pattern_carries_the_target():
    matching = [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(TARGET)]
    assert len(matching) == 1, [p.pattern for p in matching]
    assert _carriers() == matching, [p.pattern for p in _carriers()]


def test_the_control_removing_this_line_refuses_the_target_and_nothing_moves():
    """THE CONTROL, and the proven revert path.

    Remove this line. The target must flip to REFUSED -- so the line is what
    admits it, and deleting it is a rollback that works -- while every
    neighbour stays refused, so no refusal above was being carried by this
    line's absence.
    """
    carriers = _carriers()
    assert len(carriers) == 1
    survivors = tuple(p for p in readonly._ALLOWED_URL_PATTERNS if p is not carriers[0])
    assert len(survivors) == len(readonly._ALLOWED_URL_PATTERNS) - 1
    assert not _allowed(TARGET, survivors)
    assert not _allowed(TARGET.rstrip("/"), survivors)
    for url, why in NEIGHBOURS:
        assert not _allowed(url, survivors), why


def test_the_line_newly_admits_exactly_its_own_two_spellings():
    """THE BLAST RADIUS, measured with the shipped instrument, never a grep.

    The line is taken OUT of the tuple and handed back to
    ``blast_radius.newly_admitted`` as a candidate, over that instrument's own
    corpus plus every spelling in this file. It must newly admit its own
    target with and without the slash and NOTHING ELSE, and newly refuse
    nothing.
    """
    carriers = _carriers()
    assert len(carriers) == 1
    original = readonly._ALLOWED_URL_PATTERNS
    survivors = tuple(p for p in original if p is not carriers[0])
    corpus = sorted(set(blast_radius.corpus()) | set(_family()))
    try:
        readonly._ALLOWED_URL_PATTERNS = survivors
        result = blast_radius.newly_admitted(carriers[0].pattern, corpus)
    finally:
        readonly._ALLOWED_URL_PATTERNS = original
    assert sorted(result["newly_admitted"]) == sorted({TARGET, TARGET.rstrip("/")}), (
        result["newly_admitted"]
    )
    assert result["newly_refused"] == [], result["newly_refused"]
    assert result["tested"] == len(corpus)


def test_a_family_pattern_would_have_admitted_what_this_refuses():
    """THE CONTROL ON THE INSTRUMENT: the same measurement CAN fail. A family
    wildcard over his activity, measured the same way, admits the tabs, the
    comments and reactions lists and the traversal onto a third party."""
    corpus = sorted(set(blast_radius.corpus()) | set(_family()))
    wide = blast_radius.newly_admitted(
        r"^https://www\.linkedin\.com/in/me/recent-activity/.*$", corpus
    )
    admitted = set(wide["newly_admitted"])
    assert f"{B}/in/me/recent-activity/comments/" in admitted, wide
    assert f"{B}/in/me/recent-activity/all/../../../in/{OTHER}/" in admitted, wide
    assert len(admitted) > 2, wide


def test_the_line_can_name_nobody():
    """STRUCTURAL, not promised: no class, no wildcard, no group, no query
    allowance, and the only member segment is the literal ``me``."""
    source = _carriers()[0].pattern
    for wildcard in ("[^", ".*", ".+", r"\w", r"\d", "+", "?:", "#", "["):
        assert wildcard not in source, (wildcard, source)
    assert "(" not in source, source
    assert "/in/me/" in source, source
    assert source.startswith(r"^https://www\.linkedin\.com/"), source
    assert source.endswith("/?$"), source
