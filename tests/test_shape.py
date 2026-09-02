"""Tests for linkedin_server.shape -- the pure card-to-record layer.

Every test states one property of the shapers, exercised against fixture text
shaped like real LinkedIn card innerText: labels duplicated by screen-reader
spans, button chrome mixed in with content, relative timestamps landing in
awkward positions.

No browser, no network, no account: shape.py is pure, so this whole file runs
in milliseconds and is where a parsing regression should be caught.
"""

import pytest

from linkedin_server import shape
from linkedin_server.config import MAX_TEXT_CHARS
from linkedin_server.shape import (
    absolute_url,
    clean_lines,
    content_lines,
    envelope,
    find_time_ago,
    is_chrome,
    job_id_from,
    parse_job_card,
    parse_notification,
    parse_person_card,
    profile_slug_from,
    trim,
)

# ---------------------------------------------------------------------------
# Fixture text -- what innerText actually looks like on a LinkedIn card
# ---------------------------------------------------------------------------

#: LinkedIn paints title, company and location twice: once visually and once
#: in a visually-hidden span for screen readers.
JOB_CARD_WITH_SCREEN_READER_DUPLICATES = """\
Senior Node.js Engineer
Senior Node.js Engineer
Acme Corp
Acme Corp
Riverton, Fairhaven, United States (Hybrid)
Riverton, Fairhaven, United States (Hybrid)
2 weeks ago
Easy Apply
"""

#: The title itself begins with the word "Applied".
APPLIED_SCIENTIST_JOB_CARD = """\
Applied Scientist
Applied Scientist
Globex Research
Hyderabad, Telangana, India
Promoted
"""

#: The status really is a status, on its own line, as the applied-jobs list
#: renders it.
APPLIED_STATUS_JOB_CARD = """\
Senior Node.js Engineer
Acme Corp
Riverton, Fairhaven, United States
Applied
3 days ago
"""

APPLICATION_VIEWED_JOB_CARD = """\
Backend Engineer (Node.js)
Initech Software
Remote (India)
Application viewed
1 day ago
"""

CLOSED_JOB_CARD = """\
Staff Software Engineer
Umbrella Systems
Pune, Maharashtra, India
No longer accepting applications
"""

APPLIED_ON_A_DATE_JOB_CARD = """\
Full Stack Engineer
Soylent Labs
Chennai, Tamil Nadu, India
Applied on August 12
"""

#: Every button LinkedIn hangs off a job card, and nothing else.
CHROME_ONLY_JOB_CARD = """\
Promoted
Easy Apply
Save
Dismiss
See more
"""

JOB_CARD_BURIED_IN_CHROME = """\
Promoted
Senior Node.js Engineer
Acme Corp
Riverton, Fairhaven, United States
Actively recruiting
Easy Apply
Save
"""

#: A "who viewed your profile" row for a signed-in, named viewer.
NAMED_VIEWER_CARD = """\
Priya Sharma
Engineering Manager at Globex
Riverton, Fairhaven, United States
2 days ago
Message
Connect
"""

#: The same row when the viewer browsed in private mode.
ANONYMOUS_VIEWER_CARD = """\
LinkedIn Member
Software Engineer at a stealth startup
3 days ago
"""

#: The timestamp sits between the name and the headline.
VIEWER_CARD_WITH_LEADING_TIMESTAMP = """\
Priya Sharma
2 days ago
Engineering Manager at Globex
"""

#: The timestamp sits between the title and the company.
JOB_CARD_WITH_TIMESTAMP_BEFORE_COMPANY = """\
Senior Node.js Engineer
3 days ago
Acme Corp
Riverton, Fairhaven, United States
"""

NOTIFICATION_CARD = """\
Acme Corp posted a job that may interest you: Senior Node.js Engineer
2 hours ago
"""

#: Name line -> the marker in shape._ANONYMOUS_MARKERS it is meant to trip.
ANONYMOUS_NAME_LINES = [
    ("LinkedIn Member", "linkedin member"),
    ("Someone at Acme Corp", "someone at"),
    ("Anonymous LinkedIn Member", "anonymous linkedin member"),
    ("Private mode viewer", "private mode"),
    ("Viewer from Riverton, United States", "viewer from"),
]


# ---------------------------------------------------------------------------
# 1. The duplicate-line collapse
# ---------------------------------------------------------------------------


def test_clean_lines_collapses_consecutive_screen_reader_duplicates():
    raw = JOB_CARD_WITH_SCREEN_READER_DUPLICATES
    assert len([ln for ln in raw.splitlines() if ln.strip()]) == 8
    assert clean_lines(raw) == [
        "Senior Node.js Engineer",
        "Acme Corp",
        "Riverton, Fairhaven, United States (Hybrid)",
        "2 weeks ago",
        "Easy Apply",
    ]


def test_duplicate_lines_do_not_become_the_company():
    card = parse_job_card(
        {
            "href": "/jobs/view/senior-node-js-engineer-at-acme-corp-3912345678",
            "text": JOB_CARD_WITH_SCREEN_READER_DUPLICATES,
        }
    )
    assert card is not None
    assert card["title"] == "Senior Node.js Engineer"
    assert card["company"] == "Acme Corp"
    assert card["company"] != card["title"]
    assert card["location"] == "Riverton, Fairhaven, United States (Hybrid)"
    assert card["when"] == "2 weeks ago"


def test_clean_lines_collapses_duplicates_case_insensitively():
    assert clean_lines("Acme Corp\nACME CORP\nRiverton") == [
        "Acme Corp",
        "Riverton",
    ]


# ---------------------------------------------------------------------------
# 2. A status line is a status; "Applied Scientist" is a job title
# ---------------------------------------------------------------------------


def test_applied_scientist_stays_the_title_and_is_not_read_as_a_status():
    card = parse_job_card(
        {"href": "/jobs/view/3912345678", "text": APPLIED_SCIENTIST_JOB_CARD}
    )
    assert card is not None
    assert card["title"] == "Applied Scientist"
    assert card["company"] == "Globex Research"
    assert card["location"] == "Hyderabad, Telangana, India"
    assert "status" not in card


def test_standalone_applied_line_becomes_the_status():
    card = parse_job_card(
        {"href": "/jobs/view/3912345678", "text": APPLIED_STATUS_JOB_CARD}
    )
    assert card is not None
    assert card["status"] == "applied"
    assert card["title"] == "Senior Node.js Engineer"
    assert card["company"] == "Acme Corp"
    assert card["location"] == "Riverton, Fairhaven, United States"


def test_application_viewed_line_becomes_the_status():
    card = parse_job_card(
        {"href": "/jobs/view/3912345679", "text": APPLICATION_VIEWED_JOB_CARD}
    )
    assert card is not None
    assert card["status"] == "application viewed"
    assert card["title"] == "Backend Engineer (Node.js)"
    assert card["company"] == "Initech Software"
    assert card["when"] == "1 day ago"


def test_no_longer_accepting_applications_line_becomes_the_status():
    card = parse_job_card({"href": "/jobs/view/3912345680", "text": CLOSED_JOB_CARD})
    assert card is not None
    assert card["status"] == "no longer accepting applications"
    assert card["title"] == "Staff Software Engineer"
    assert card["company"] == "Umbrella Systems"
    assert card["location"] == "Pune, Maharashtra, India"


def test_applied_with_a_trailing_date_is_still_the_applied_status():
    card = parse_job_card(
        {"href": "/jobs/view/3912345681", "text": APPLIED_ON_A_DATE_JOB_CARD}
    )
    assert card is not None
    assert card["status"] == "applied"
    assert card["title"] == "Full Stack Engineer"
    assert card["company"] == "Soylent Labs"


# ---------------------------------------------------------------------------
# 3. Anonymous viewers
# ---------------------------------------------------------------------------


def test_linkedin_member_viewer_is_anonymous_and_has_no_profile_url():
    card = parse_person_card(
        {"href": "/in/acoaaab-anonymous-1234/", "text": ANONYMOUS_VIEWER_CARD}
    )
    assert card is not None
    assert card["name"] == "LinkedIn Member"
    assert card["anonymous"] is True
    assert "profile" not in card
    assert card["viewed"] == "3 days ago"


def test_named_viewer_is_not_anonymous_and_carries_a_profile_url():
    card = parse_person_card(
        {"href": "/in/priya-sharma-12ab34/", "text": NAMED_VIEWER_CARD}
    )
    assert card is not None
    assert card["name"] == "Priya Sharma"
    assert card["anonymous"] is False
    assert card["profile"] == "https://www.linkedin.com/in/priya-sharma-12ab34"
    assert card["headline"] == "Engineering Manager at Globex"
    assert card["viewed"] == "2 days ago"


@pytest.mark.parametrize("name_line, marker", ANONYMOUS_NAME_LINES)
def test_every_anonymous_marker_suppresses_the_profile_url(name_line, marker):
    text = name_line + "\nWorks in software\n4 days ago\n"
    card = parse_person_card({"href": "/in/some-real-slug-99/", "text": text})
    assert card is not None, marker
    assert card["anonymous"] is True, marker
    assert "profile" not in card, marker


def test_anonymous_marker_cases_cover_every_marker_in_the_module():
    covered = {marker for _, marker in ANONYMOUS_NAME_LINES}
    assert covered == set(shape._ANONYMOUS_MARKERS)


# ---------------------------------------------------------------------------
# 4. Time-ago extraction
# ---------------------------------------------------------------------------


def test_find_time_ago_keeps_one_day_singular():
    assert find_time_ago(["Viewed 1 day ago"]) == "1 day ago"


def test_find_time_ago_keeps_three_days_plural():
    assert find_time_ago(["Viewed 3 days ago"]) == "3 days ago"


def test_find_time_ago_reads_weeks():
    assert find_time_ago(["Posted 2 weeks ago"]) == "2 weeks ago"


@pytest.mark.parametrize(
    "line, expected",
    [
        ("Viewed today", "today"),
        ("Viewed yesterday", "yesterday"),
        ("Just now", "just now"),
    ],
)
def test_find_time_ago_recognises_relative_words(line, expected):
    assert find_time_ago([line]) == expected


def test_find_time_ago_returns_none_when_no_timestamp_is_present():
    assert find_time_ago(["Senior Node.js Engineer", "Acme Corp"]) is None


def test_time_line_does_not_become_the_person_headline():
    card = parse_person_card(
        {
            "href": "/in/priya-sharma-12ab34/",
            "text": VIEWER_CARD_WITH_LEADING_TIMESTAMP,
        }
    )
    assert card is not None
    assert card["viewed"] == "2 days ago"
    assert card["headline"] == "Engineering Manager at Globex"


def test_time_line_between_title_and_company_does_not_become_the_company():
    card = parse_job_card(
        {
            "href": "/jobs/view/3912345678",
            "text": JOB_CARD_WITH_TIMESTAMP_BEFORE_COMPANY,
        }
    )
    assert card is not None
    assert card["title"] == "Senior Node.js Engineer"
    assert card["company"] == "Acme Corp"
    assert card["location"] == "Riverton, Fairhaven, United States"
    assert card["when"] == "3 days ago"


# ---------------------------------------------------------------------------
# 5. Ids and slugs
# ---------------------------------------------------------------------------


def test_job_id_from_slugged_job_view_url():
    href = "/jobs/view/senior-node-engineer-at-acme-3912345678"
    assert job_id_from(href) == "3912345678"


def test_job_id_from_bare_numeric_job_view_url():
    assert job_id_from("/jobs/view/3912345678") == "3912345678"


def test_job_id_from_current_job_id_query_parameter():
    href = (
        "https://www.linkedin.com/jobs/collections/recommended/"
        "?currentJobId=3912345678"
    )
    assert job_id_from(href) == "3912345678"


def test_job_id_from_returns_none_when_the_url_carries_no_id():
    assert job_id_from("https://www.linkedin.com/jobs/collections/recommended/") is None
    assert job_id_from("") is None


def test_job_card_carries_job_id_and_canonical_url_from_href():
    card = parse_job_card(
        {
            "href": (
                "https://www.linkedin.com/jobs/view/"
                "senior-node-js-engineer-at-acme-corp-3912345678?refId=abc123"
            ),
            "text": JOB_CARD_WITH_SCREEN_READER_DUPLICATES,
        }
    )
    assert card is not None
    assert card["job_id"] == "3912345678"
    assert card["url"] == "https://www.linkedin.com/jobs/view/3912345678"


def test_profile_slug_from_public_identifier_url():
    assert profile_slug_from("/in/alex-r-12ab34/") == "alex-r-12ab34"


def test_profile_slug_from_me_returns_none():
    assert profile_slug_from("/in/me/") is None


def test_profile_slug_from_returns_none_for_a_non_profile_url():
    assert profile_slug_from("/jobs/view/3912345678") is None


def test_absolute_url_makes_relative_hrefs_absolute_and_drops_tracking():
    assert (
        absolute_url("/jobs/view/3912345678?refId=abc&trackingId=xyz")
        == "https://www.linkedin.com/jobs/view/3912345678"
    )
    assert (
        absolute_url("https://www.linkedin.com/in/priya-sharma-12ab34?trk=nav")
        == "https://www.linkedin.com/in/priya-sharma-12ab34"
    )
    assert absolute_url("") is None


# ---------------------------------------------------------------------------
# 6. Chrome filtering
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line",
    [
        "Message",
        "Connect",
        "Easy Apply",
        "Promoted",
        "Save",
        "message",
        "PROMOTED",
        "Promoted.",
        "- Save",
    ],
)
def test_chrome_labels_are_recognised_as_chrome(line):
    assert is_chrome(line) is True


@pytest.mark.parametrize(
    "line",
    ["Senior Node.js Engineer", "Acme Corp", "Applied Scientist", "Saved searches"],
)
def test_real_content_is_not_mistaken_for_chrome(line):
    assert is_chrome(line) is False


def test_content_lines_drops_chrome_and_keeps_content():
    assert content_lines(JOB_CARD_BURIED_IN_CHROME) == [
        "Senior Node.js Engineer",
        "Acme Corp",
        "Riverton, Fairhaven, United States",
    ]


def test_chrome_lines_do_not_become_job_title_company_or_location():
    card = parse_job_card(
        {"href": "/jobs/view/3912345678", "text": JOB_CARD_BURIED_IN_CHROME}
    )
    assert card is not None
    assert card["title"] == "Senior Node.js Engineer"
    assert card["company"] == "Acme Corp"
    assert card["location"] == "Riverton, Fairhaven, United States"


def test_chrome_lines_do_not_become_the_person_headline():
    # The timestamp is not decoration here: a profile-view row without one is
    # not treated as a viewer at all (see the test below).
    text = (
        "Priya Sharma\nMessage\nConnect\nEngineering Manager at Globex\n"
        "2 days ago\n"
    )
    card = parse_person_card({"href": "/in/priya-sharma-12ab34/", "text": text})
    assert card is not None
    assert card["name"] == "Priya Sharma"
    assert card["headline"] == "Engineering Manager at Globex"


def test_a_row_without_a_viewed_time_is_not_a_viewer():
    """The rule that rejects page furniture without needing to recognise it.

    Every row LinkedIn draws on the profile-views surface carries a "Viewed
    <when>" line. The page heading block and the "N recruiters viewed your
    profile" roll-up do not, and both were being emitted as people. Requiring
    the timestamp rejects them structurally; the cost is that if LinkedIn
    ever stops rendering it this surface reads as zero rows, which the tool
    reports as a failure rather than as an empty list.
    """
    text = "Priya Sharma\nEngineering Manager at Globex\n"
    assert parse_person_card({"href": "/in/priya-sharma-12ab34/", "text": text}) is None


# ---------------------------------------------------------------------------
# 7. trim
# ---------------------------------------------------------------------------


def test_trim_collapses_whitespace_including_newlines():
    assert trim("  Senior   Node.js\n\tEngineer  ") == "Senior Node.js Engineer"


@pytest.mark.parametrize("text", [None, "", "   ", "\n\t \n"])
def test_trim_returns_none_for_empty_or_whitespace_only_input(text):
    assert trim(text) is None


def test_trim_truncates_over_length_text_at_the_configured_limit():
    result = trim("A" * 200)
    assert result == "A" * (MAX_TEXT_CHARS - 3) + "..."
    assert len(result) == MAX_TEXT_CHARS


def test_trim_truncates_a_long_headline_and_marks_it_with_an_ellipsis():
    headline = (
        "Engineering Manager at Globex, building distributed Node.js services " * 5
    )
    result = trim(headline)
    assert len(result) <= MAX_TEXT_CHARS
    assert result.endswith("...")
    assert result.startswith("Engineering Manager at Globex")


def test_trim_honours_an_explicit_limit():
    assert trim("abcdefghij", limit=5) == "ab..."


def test_trim_does_not_leave_a_dangling_space_before_the_ellipsis():
    assert trim("ab cdefghij", limit=6) == "ab..."


def test_trim_leaves_text_at_exactly_the_limit_untouched():
    text = "B" * MAX_TEXT_CHARS
    assert trim(text) == text


# ---------------------------------------------------------------------------
# 8. Nothing invented -- a parser that read nothing returns None
# ---------------------------------------------------------------------------


def test_empty_job_card_returns_none_rather_than_a_dict_of_nones():
    assert parse_job_card({"href": "/jobs/view/3912345678", "text": ""}) is None


def test_chrome_only_job_card_returns_none():
    assert (
        parse_job_card({"href": "/jobs/view/3912345678", "text": CHROME_ONLY_JOB_CARD})
        is None
    )


def test_job_card_of_only_a_status_and_a_timestamp_returns_none():
    assert (
        parse_job_card(
            {"href": "/jobs/view/3912345678", "text": "Applied\n2 days ago"}
        )
        is None
    )


def test_single_line_job_card_leaves_company_and_location_none_not_invented():
    card = parse_job_card(
        {
            "href": "/jobs/view/3912345678",
            "text": "Senior Node.js Engineer\nEasy Apply",
        }
    )
    assert card is not None
    assert card["title"] == "Senior Node.js Engineer"
    assert card["company"] is None
    assert card["location"] is None


def test_empty_person_card_returns_none():
    assert parse_person_card({"href": "/in/priya-sharma-12ab34/", "text": ""}) is None


def test_chrome_only_person_card_returns_none():
    assert (
        parse_person_card(
            {"href": "/in/priya-sharma-12ab34/", "text": "Message\nConnect\nFollow"}
        )
        is None
    )


def test_empty_notification_returns_none():
    assert parse_notification({"href": "/jobs/view/3912345678", "text": ""}) is None


def test_chrome_only_notification_returns_none():
    assert (
        parse_notification(
            {"href": "/jobs/view/3912345678", "text": "Dismiss\nSee all"}
        )
        is None
    )


def test_notification_keeps_its_body_and_link_without_the_timestamp_line():
    card = parse_notification(
        {"href": "/jobs/view/3912345678?refId=abc123", "text": NOTIFICATION_CARD}
    )
    assert card is not None
    assert (
        card["text"]
        == "Acme Corp posted a job that may interest you: Senior Node.js Engineer"
    )
    assert "2 hours ago" not in card["text"]
    assert card["when"] == "2 hours ago"
    assert card["link"] == "https://www.linkedin.com/jobs/view/3912345678"


# ---------------------------------------------------------------------------
# 9. envelope
# ---------------------------------------------------------------------------

ROWS = [
    {"title": "Senior Node.js Engineer", "company": "Acme Corp"},
    {"title": "Backend Engineer", "company": "Initech Software"},
    {"title": "Staff Software Engineer", "company": "Umbrella Systems"},
]

SOURCE = "https://www.linkedin.com/my-items/saved-jobs/"


def test_envelope_is_capped_when_rows_exceed_the_limit():
    out = envelope(ROWS, limit=2, source_url=SOURCE)
    assert out["capped"] is True


def test_envelope_is_not_capped_when_rows_exactly_fill_the_limit():
    out = envelope(ROWS, limit=3, source_url=SOURCE)
    assert out["capped"] is False


def test_envelope_is_not_capped_when_rows_are_under_the_limit():
    out = envelope(ROWS[:1], limit=25, source_url=SOURCE)
    assert out["capped"] is False


def test_envelope_page_had_is_the_pre_trim_count_and_count_is_post_trim():
    out = envelope(ROWS, limit=2, source_url=SOURCE)
    assert out["page_had"] == 3
    assert out["count"] == 2
    assert out["limit"] == 2
    assert out["source_url"] == SOURCE
    assert out["pages_loaded"] == 1


def test_envelope_results_hold_the_trimmed_rows():
    out = envelope(ROWS, limit=2, source_url=SOURCE)
    assert out["results"] == ROWS[:2]
    assert len(out["results"]) == out["count"]


def test_envelope_reports_unparsed_rows_only_when_some_were_dropped():
    kept = envelope(ROWS, limit=25, source_url=SOURCE, dropped=2)
    assert kept["unparsed_rows"] == 2
    clean = envelope(ROWS, limit=25, source_url=SOURCE, dropped=0)
    assert "unparsed_rows" not in clean


def test_envelope_merges_extra_fields():
    out = envelope(
        ROWS, limit=25, source_url=SOURCE, pages_loaded=2, extra={"query": "node.js"}
    )
    assert out["query"] == "node.js"
    assert out["pages_loaded"] == 2
    assert out["results"] == ROWS


# ---------------------------------------------------------------------------
# describe_name_shaped -- and the circular oracle that used to "check" it
# ---------------------------------------------------------------------------

#: Label, and the descriptor a HUMAN says it should produce. Literal expected
#: values are the whole point: see the docstring below.
DESCRIPTOR_CASES = [
    ("Ada Lovelace will send message", 1, False, "will send message"),
    ("Ada Lovelace to Grace Hopper will send message", 2, True, "will send message"),
    ("Grace Hopper", 1, False, ""),
    ("Send", 1, False, ""),
    ("Open send options", 1, False, "send options"),
    # NONE, NOT "". No run was found, so no name-free tail can be derived.
    # An empty tail would mean "the name ran to the end of the string",
    # which is a different fact and is what ``Send`` above reports.
    ("", 0, False, None),
]


@pytest.mark.parametrize("label,runs,joined,tail", DESCRIPTOR_CASES)
def test_the_descriptor_returns_the_tail_a_reader_would_write_down(
    label, runs, joined, tail
):
    """The descriptor's invariant, checked with an INDEPENDENT oracle.

    THIS TEST REPLACED A CIRCULAR ONE, and the circularity is the finding
    rather than the bug it hid. The previous version asserted:

        assert not shape.looks_name_shaped(tail)

    -- it validated the descriptor USING THE PREDICATE THE DESCRIPTOR IS BUILT
    ON. When the tail IS somebody's name, ``looks_name_shaped(tail)`` is False,
    so ``not False`` passes and the test AGREES WITH THE BUG BY CONSTRUCTION.
    No amount of care in writing that assertion would have helped, because the
    oracle and the subject were the same rule.

    A CHECKER MAY NEVER BE ITS OWN ORACLE. The expected values here are
    written out by hand, so the only way this test can agree with a broken
    descriptor is for a person to have written the broken answer down.
    """
    out = shape.describe_name_shaped(label)
    assert (out["runs"], out["joined_by_to"], out["tail"]) == (runs, joined, tail)


@pytest.mark.parametrize(
    "label",
    [
        "\u00c9lodie will send message",
        "\u674e\u96f7 will send message",
        "\u0410\u043d\u043d\u0430 will send message",
    ],
    ids=["latin-accent", "han", "cyrillic"],
)
def test_a_name_outside_ascii_does_not_survive_into_the_tail(label):
    """The hole the circular oracle could not express, now closed.

    THIS WAS AN ``xfail(strict=True)`` UNTIL THE FIX LANDED, and that is why
    the marker is GONE rather than relaxed: a strict xfail that starts
    passing FAILS, so the fix could not land without someone deleting it.
    The documentation of the defect was forced to die with the defect,
    instead of outliving it as prose nobody re-read.

    THE DEFECT. ``_NAME_SHAPE_RUN`` matches ``[A-Z]``, which is ASCII, so a
    name in any other script scored ZERO runs -- the guard passed it and the
    descriptor handed back the whole string as a "name-free tail" with the
    name still in it.

    THE CENSUS NEVER HAD IT, and the reason is structural rather than lucky:
    ``_CENSUS_SAFE_CHARS`` is ASCII-only ON PURPOSE, so a name in another
    script is refused BY THE GATE rather than by a rule somebody remembered
    to write. The publication path never ran that gate -- two paths, one
    with a structural refusal and one with a remembered rule.
    """
    out = shape.describe_name_shaped(label)
    assert out["runs"] == 0
    # Not the whole string, and not a truncation of it either.
    assert out["tail"] is None
    # And the guard refuses it, which is the half that decides publication.
    assert shape.looks_name_shaped(label) is True


def test_the_guard_still_passes_a_string_with_no_name_in_it():
    """The refusal must not have become unconditional.

    A guard that refused everything would satisfy the test above while making
    every caller dead -- the same control the compose reader carries, turned
    on the predicate itself.
    """
    assert shape.looks_name_shaped("will send message") is False
    assert shape.looks_name_shaped("") is False
    assert shape.looks_name_shaped("send") is False
# ---------------------------------------------------------------------------
# The three name predicates, and where each one is actually reached from
# ---------------------------------------------------------------------------

#: Predicate -> why it exists after the 2026-09-02 re-anchoring. AN ENTRY IS A
#: CLAIM THAT IS ITSELF CHECKED, borrowing the rule from
#: ``tests/test_reader_reachability.py``: listing a predicate as test-only
#: fails if it gains a production caller, and listing one as production fails
#: if it loses its last one. Neither direction is a waiver.
PREDICATE_DISPOSITION = {
    "name_shape_run_pattern": "production",
    "looks_name_shaped": "production",
    # THE ONE THAT IS NOT REACHED FROM THE TOOL SURFACE, and the reason is not
    # "nobody got round to it". The page shapes labels itself, so nothing in
    # production asks Python to shape one. What this function IS now is the
    # REFERENCE IMPLEMENTATION the shipped JavaScript is checked against, in
    # test_the_page_shaping_agrees_with_the_python_descriptor. Moving it into
    # that test would put a third copy of the rule in a third place, which is
    # the drift the whole split exists to prevent -- so it stays here and its
    # job is stated rather than assumed.
    "describe_name_shaped": "reference implementation for the cross-engine check",
}


def _production_call_counts():
    """How many times each predicate is CALLED in linkedin_server/*.py.

    An AST walk over ``ast.Call`` nodes, not a substring search, for the reason
    ``test_reader_reachability`` gives: these names appear in seven docstrings
    and comments across dom.py, and a grep counts every one of them as a use.
    Docstrings do not get a vote on whether code is reachable.
    """
    import ast
    import pathlib

    package = pathlib.Path(shape.__file__).resolve().parent
    counts = {name: 0 for name in PREDICATE_DISPOSITION}
    for path in sorted(package.glob("*.py")):
        if path.name == "shape.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = getattr(func, "attr", None) or getattr(func, "id", None)
            if name in counts:
                counts[name] += 1
    return counts


def test_each_name_predicate_is_reached_the_way_its_entry_says():
    """A predicate nobody calls is a comment, whatever its docstring claims.

    THIS EXISTS BECAUSE THE RE-ANCHORING BROKE ITS OWN STORY. Moving the
    shaping into the page left ``looks_name_shaped`` with ZERO callers, while
    three docstrings and a commit message went on describing it as defence in
    depth. The claim was false for exactly as long as nobody counted -- the
    same shape as ``read_settings_surface``, which sat dead for ten days with a
    comment noting it was uncalled one sentence after arguing that such readers
    go stale unread.

    So the disposition is measured rather than asserted in prose, in both
    directions.
    """
    counts = _production_call_counts()
    for name, disposition in PREDICATE_DISPOSITION.items():
        if disposition == "production":
            assert counts[name] > 0, (
                f"{name} is listed as production and has NO caller in "
                f"linkedin_server/. Either wire it or change its entry -- do "
                f"not leave it described as a guard it is not."
            )
        else:
            assert counts[name] == 0, (
                f"{name} is listed as {disposition!r} but is now CALLED "
                f"{counts[name]} time(s) in production. Update its entry: the "
                f"reason it is kept has changed."
            )


def test_the_reference_implementation_is_actually_referenced():
    """The other half: test-only is a job, not an excuse.

    ``describe_name_shaped`` is kept for one stated purpose -- being the thing
    the shipped ``COMPOSE_MODES_JS`` is compared against. If that comparison
    ever stops naming it, the function is not test-only, it is dead, and this
    fails rather than letting the entry above quietly become the excuse it was
    written not to be.
    """
    import pathlib

    differential = (
        pathlib.Path(__file__).resolve().parent / "test_compose_fields.py"
    ).read_text(encoding="utf-8")
    assert "describe_name_shaped" in differential
    assert "test_the_page_shaping_agrees_with_the_python_descriptor" in differential
