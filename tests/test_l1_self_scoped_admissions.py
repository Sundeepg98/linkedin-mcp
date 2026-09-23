"""Five self-scoped read pages are admitted, and each one's NEIGHBOURS are not.

Lane L1 (refused reads), 2026-09-23. The argument for each entry is on its line
in ``linkedin_server/readonly.py``; the per-row record is
``_audit/2026-09-23-lane-l1-refused-reads.md``. This file pins what the five
lines do and, more importantly, what they do NOT do.

AN ALLOWLIST ENTRY IS WORTH EXACTLY WHAT ITS EDGES ARE WORTH, so every entry
carries: its two admitted spellings, a table of neighbours that must stay
refused -- other members, the family, a query, a sub-path, a traversal -- and
a CONTROL that removes that one entry and re-runs everything. The control is
what says a refusal below is carried by the rest of the boundary and not by
the absence of this line; without it a file of refusals passes against a
boundary that refuses everything.

THE REVERT PATH IS PROVEN RATHER THAN ASSUMED, which is condition 4 of the
search-admission ruling applied here: the same control shows each target
REFUSED with its line removed, so deleting the line is a tested rollback.

EVERY VARIABLE SEGMENT IS A PLACEHOLDER. ``someone-else`` carries the token
the identity guard sanctions; post ids are FIVE digits, under the guard's
six-digit urn floor. Nothing here names or addresses a real person or post.
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
POST = "12345"
OTHER = "someone-else"

#: key -> (the target WITH its trailing slash, the census rows it serves).
TARGETS: dict[str, tuple[str, str]] = {
    "contact_info": (f"{B}/in/me/overlay/contact-info/", "P A25"),
    "post_summary": (
        f"{B}/analytics/post-summary/urn:li:activity:{POST}/", "P G6, M C38"
    ),
    "audience": (f"{B}/analytics/creator/audience/", "P L1"),
    "dashboard": (f"{B}/dashboard/", "P L8"),
    "articles": (f"{B}/in/me/recent-activity/articles/", "M C48"),
}

#: key -> the neighbours that must stay refused, each with its reason.
NEIGHBOURS: dict[str, tuple[tuple[str, str], ...]] = {
    "contact_info": (
        (f"{B}/in/{OTHER}/overlay/contact-info/",
         "ANOTHER MEMBER'S overlay. Loading a third party's profile leaves "
         "them a durable record; the `me` form is the whole permission"),
        (f"{B}/in/me/overlay/", "the overlay root, which is not a page"),
        (f"{B}/in/me/overlay/background-photo/", "a DIFFERENT overlay"),
        (f"{B}/in/me/overlay/contact-info/?x=1", "a QUERY"),
        (f"{B}/in/me/overlay/contact-info/detail/", "a SUB-PATH"),
        (f"{B}/in/me/edit/contact-info/",
         "THE EDITOR -- still refused by `/edit/` on gate one"),
        (f"{B}/in/me/overlay/contact-info/../../../in/{OTHER}/",
         "a TRAVERSAL that normalises onto a third party's profile"),
    ),
    "post_summary": (
        (f"{B}/analytics/post-summary/urn:li:share:{POST}/",
         "a `share` urn: never drawn at this address"),
        (f"{B}/analytics/post-summary/urn:li:ugcPost:{POST}/",
         "a `ugcPost` urn: never drawn at this address"),
        (f"{B}/analytics/post-summary/urn%3Ali%3Aactivity%3A{POST}/",
         "a PERCENT-ENCODED urn, never observed in this position"),
        (f"{B}/analytics/post-summary/", "the bare family root"),
        (f"{B}/analytics/post-summary/urn:li:activity:/", "an EMPTY id"),
        (f"{B}/analytics/post-summary/urn:li:activity:{'1' * 21}/",
         "TWENTY-ONE digits, past the closed bound"),
        (f"{B}/analytics/post-summary/urn:li:activity:"
         "\u0661\u0662\u0663\u0664\u0665/",
         "ARABIC-INDIC digits -- what `\\d` would have admitted"),
        (f"{B}/analytics/post-summary/urn:li:activity:"
         "\uff11\uff12\uff13\uff14\uff15/",
         "FULLWIDTH digits -- the same defect"),
        (f"{B}/analytics/post-summary/urn:li:activity:{POST}/?x=1", "a QUERY"),
        (f"{B}/analytics/post-summary/urn:li:activity:{POST}/demographics/",
         "a SUB-PATH -- a demographics tab would be its own decision"),
        (f"{B}/analytics/post-summary/urn:li:activity:{POST}/../../../"
         "mypreferences/d/close-account",
         "a TRAVERSAL onto an account-ending address no substring names"),
    ),
    "audience": (
        (f"{B}/analytics/creator/", "THE PARENT"),
        (f"{B}/analytics/", "THE TREE ROOT"),
        (f"{B}/analytics/creator/top-posts/",
         "THE OTHER DRAWN SIBLING -- no row of this lane's"),
        (f"{B}/analytics/creator/newsletters/",
         "a named, never-observed analytics spelling"),
        (f"{B}/analytics/creator/audience/?x=1", "a QUERY"),
        (f"{B}/analytics/creator/audience/detail/", "a SUB-PATH"),
        (f"{B}/analytics/creator/audience/../../../mypreferences/d/"
         "close-account",
         "a TRAVERSAL onto an account-ending address"),
    ),
    "dashboard": (
        (f"{B}/dashboard/?x=1", "a QUERY"),
        (f"{B}/dashboard/analytics/", "a SUB-PATH"),
        (f"{B}/dashboard/creator-mode/",
         "a SUB-PATH that would be a setting nobody named"),
        (f"{B}/dashboards/", "a longer word"),
        (f"{B}/company/placeholder-org/admin/dashboard/",
         "PAGE ADMINISTRATION -- the anchor at the host refuses it"),
        (f"{B}/dashboard/../mypreferences/d/close-account",
         "a TRAVERSAL onto an account-ending address"),
    ),
    "articles": (
        (f"{B}/in/{OTHER}/recent-activity/articles/",
         "ANOTHER MEMBER'S articles"),
        (f"{B}/in/me/recent-activity/", "the activity root"),
        (f"{B}/in/me/recent-activity/all/",
         "the drawn parent -- a different capability"),
        (f"{B}/in/me/recent-activity/comments/",
         "other people's posts he commented on"),
        (f"{B}/in/me/recent-activity/reactions/",
         "other people's posts he reacted to"),
        (f"{B}/in/me/recent-activity/articles/?x=1", "a QUERY"),
        (f"{B}/in/me/recent-activity/articles/../../../in/{OTHER}/",
         "a TRAVERSAL onto a third party's profile"),
    ),
}

#: The pattern source that carries each target, so the control can remove
#: exactly one line and the structural checks can read exactly one line.
CARRIER_NEEDLE = {
    "contact_info": "overlay/contact-info",
    "post_summary": "post-summary",
    "audience": "creator/audience",
    "dashboard": "com/dashboard",
    "articles": "recent-activity/articles",
}


def _allowed(url: str, patterns=None) -> bool:
    pool = readonly._ALLOWED_URL_PATTERNS if patterns is None else patterns
    return any(pattern.match(url) for pattern in pool)


def _carriers(key: str) -> list[re.Pattern[str]]:
    return [
        p for p in readonly._ALLOWED_URL_PATTERNS
        if CARRIER_NEEDLE[key] in p.pattern
    ]


def _family() -> list[str]:
    urls = []
    for key, (target, _rows) in TARGETS.items():
        urls += [target, target.rstrip("/")]
        urls += [url for url, _why in NEIGHBOURS[key]]
    return urls


@pytest.mark.parametrize("key", sorted(TARGETS))
def test_the_target_is_admitted_through_the_shipped_gate(key):
    """Both spellings, through ``is_read_url`` -- gate one AND gate two."""
    target, rows = TARGETS[key]
    assert readonly.is_read_url(target), (key, rows)
    assert readonly.is_read_url(target.rstrip("/")), (key, rows)


@pytest.mark.parametrize("key", sorted(TARGETS))
def test_the_target_carries_no_forbidden_substring(key):
    """No exemption was needed and none was added: gate one is untouched."""
    target, _rows = TARGETS[key]
    carried = [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in target.lower()]
    assert carried == [], (key, carried)


@pytest.mark.parametrize(
    "key,url,why",
    [(key, url, why) for key in sorted(NEIGHBOURS) for url, why in NEIGHBOURS[key]],
)
def test_the_neighbours_are_refused(key, url, why):
    assert not readonly.is_read_url(url), (key, why)


@pytest.mark.parametrize("key", sorted(TARGETS))
def test_exactly_one_pattern_carries_each_target(key):
    target, _rows = TARGETS[key]
    matching = [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(target)]
    assert len(matching) == 1, (key, [p.pattern for p in matching])
    assert _carriers(key) == matching, (key, [p.pattern for p in _carriers(key)])


@pytest.mark.parametrize("key", sorted(TARGETS))
def test_the_control_removing_this_line_refuses_the_target_and_nothing_moves(key):
    """THE CONTROL, and the proven revert path.

    Remove this entry's line. The target must flip to REFUSED -- so the line
    is what admits it, and deleting it is a rollback that works -- while
    every neighbour stays refused, so no refusal above was being carried by
    this line's absence.
    """
    carriers = _carriers(key)
    assert len(carriers) == 1, key
    survivors = tuple(
        p for p in readonly._ALLOWED_URL_PATTERNS if p is not carriers[0]
    )
    assert len(survivors) == len(readonly._ALLOWED_URL_PATTERNS) - 1
    target, _rows = TARGETS[key]
    assert not _allowed(target, survivors), key
    assert not _allowed(target.rstrip("/"), survivors), key
    for url, why in NEIGHBOURS[key]:
        assert not _allowed(url, survivors), (key, why)


@pytest.mark.parametrize("key", sorted(TARGETS))
def test_each_line_newly_admits_exactly_its_own_two_spellings(key):
    """THE BLAST RADIUS, measured with the shipped instrument, never a grep.

    The line is taken OUT of the tuple and handed back to
    ``blast_radius.newly_admitted`` as a candidate, over that instrument's own
    corpus plus every family spelling in this file. It must newly admit its
    own target with and without the slash and NOTHING ELSE, and it must
    newly refuse nothing.
    """
    carriers = _carriers(key)
    assert len(carriers) == 1, key
    original = readonly._ALLOWED_URL_PATTERNS
    survivors = tuple(p for p in original if p is not carriers[0])
    corpus = sorted(set(blast_radius.corpus()) | set(_family()))
    try:
        readonly._ALLOWED_URL_PATTERNS = survivors
        result = blast_radius.newly_admitted(carriers[0].pattern, corpus)
    finally:
        readonly._ALLOWED_URL_PATTERNS = original
    target, _rows = TARGETS[key]
    assert sorted(result["newly_admitted"]) == sorted(
        {target, target.rstrip("/")}
    ), (key, result["newly_admitted"])
    assert result["newly_refused"] == [], (key, result["newly_refused"])
    assert result["tested"] == len(corpus)


def test_a_family_pattern_would_have_admitted_what_these_refuse():
    """THE CONTROL ON THE INSTRUMENT: the same measurement CAN fail.

    A family wildcard over the analytics tree, measured the same way, admits
    the traversal onto an account-ending address -- so the zero extra
    admissions above are a reading, not a dead instrument.
    """
    corpus = sorted(set(blast_radius.corpus()) | set(_family()))
    wide = blast_radius.newly_admitted(r"^https://www\.linkedin\.com/analytics/.*$", corpus)
    assert any("close-account" in url for url in wide["newly_admitted"]), wide
    assert len(wide["newly_admitted"]) > 2, wide


@pytest.mark.parametrize("key", sorted(TARGETS))
def test_the_line_can_name_nobody(key):
    """STRUCTURAL, not promised.

    No slug-accepting character class, no wildcard, no query group, and the
    only member segment any of the five may carry is the literal ``me``.
    The post-summary line's single class is the CLOSED, BOUNDED run of the ten
    ASCII digits -- a post id, never a name.
    """
    source = _carriers(key)[0].pattern
    for wildcard in ("[^", ".*", ".+", r"\w", r"\d", "+", "?:", "#"):
        assert wildcard not in source, (key, wildcard, source)
    assert "(" not in source, (key, source)
    if "/in/" in source:
        assert "/in/me/" in source, (key, source)
    classes = re.findall(r"\[[^\]]*\]", source)
    assert classes in ([], ["[0-9]"]), (key, classes)
    if classes:
        assert "[0-9]{1,20}" in source, (key, source)
