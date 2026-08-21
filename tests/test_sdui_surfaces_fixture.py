"""The three surfaces LinkedIn rebuilt, tested against the pages it served.

A companion to ``test_profile_views_fixture.py`` and written for the same
reason: the defects here do not live in the shaping, they live in where a row
STOPS and in what the DOM hands back, and hand-written card text cannot
exercise either. All three tools were measured broken on live pages on
2026-08-21 while every pure test passed.

WHAT WAS BROKEN, and what each fixture pins:

* ``jobs_tracker_row.html`` -- one real job in the tracker. The row walk stops
  when an ancestor holds more than one deduped KEY, and this card carries TWO
  anchors to the SAME job id, so the count never rose, the walk ran to
  ``maxHops``, and the row came back as ``title: "Job tracker"``,
  ``company: "Saved <dot> 0"``. Confidently wrong, and invisible for as long as
  the list stayed empty.
* ``jobs_tracker_empty.html`` -- the same page with nothing in it. Its subject
  is the tab strip: LinkedIn's own count is the only thing on the page that
  can tell an empty list from a failed read.
* ``notifications.html`` -- six real cards. Screen-reader-only text ("Unread
  notification.", "Status is reachable") was welded to every body, and ``when``
  was null on all 22 rows of the live page because LinkedIn writes "2h" in an
  element of its own and the word "ago" appears nowhere.
* ``profile_topcard.html`` / ``profile_topcard_hydrated.html`` -- the profile
  before and after hydration. The page carries ZERO ``h1`` and none of the
  ``about``/``experience``/``skills`` ids the reader used to look for, so every
  field read null and the tool errored on its owner's own profile. Both renders
  are kept because agreeing across them is the property being claimed.
* ``profile_skills.html`` -- the skills page. ``main ul li`` matched the three
  filter pills, so "All", "Industry Knowledge" and "Tools & Technologies" were
  being reported as his skills.

Every fixture is the region named above and nothing else, with scripts, styles,
svg and images stripped, and with names, companies, slugs and member ids
replaced by invented ones. Stripping the styles makes these renders HARSHER
than the live page -- without CSS, ``innerText`` runs hidden menu items and
duplicated bodies together -- which is deliberate: a parser that survives both
layouts cannot be reading one particular render.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_own_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

TRACKER_ROW = FIXTURE_DIR / "jobs_tracker_row.html"
TRACKER_EMPTY = FIXTURE_DIR / "jobs_tracker_empty.html"
NOTIFICATIONS = FIXTURE_DIR / "notifications.html"
PROFILE_PRE = FIXTURE_DIR / "profile_topcard.html"
PROFILE_HYDRATED = FIXTURE_DIR / "profile_topcard_hydrated.html"
PROFILE_SKILLS = FIXTURE_DIR / "profile_skills.html"

BOTH_PROFILES = ["pre_hydration", "hydrated"]
PROFILE_FIXTURES = {
    "pre_hydration": PROFILE_PRE,
    "hydrated": PROFILE_HYDRATED,
}

#: chr(0xB7) is the middle dot LinkedIn separates a tab from its count with,
#: and a company from its location with. Spelled this way so this file stays
#: pure ASCII, as shape.py does.
DOT = chr(0xB7)

#: The one job on the tracker fixture.
JOB_ID = "4011223344"
JOB_TITLE = "Platform Integration Engineer"
JOB_COMPANY = "Ashgrove Systems"
JOB_LOCATION = "Fairhaven (Remote)"

#: The page furniture that became the row when the walk overshot.
PAGE_HEADING = "Job tracker"

NAME = "Alex Rivera"
HEADLINE = (
    "Senior Backend Engineer | Node.js, TypeScript, React | "
    "Building reliable services | Riverton"
)
LOCATION = "Riverton, Fairhaven, United States"
SCHOOL = "Lakeside Institute of Technology"

SKILLS = [
    "Node.js",
    "TypeScript",
    "React.js",
    "Next.js",
    "Apache Kafka",
    "Systems Design",
]
#: What the old ``main ul li`` selector returned instead.
FILTER_PILLS = ("All", "Industry Knowledge", "Tools & Technologies")


# ---------------------------------------------------------------------------
# The browser harness
# ---------------------------------------------------------------------------


async def _with_page(path: Path, work):
    """Run ``work(page)`` over one frozen page in a LOCAL headless Chromium."""
    playwright = pytest.importorskip("playwright.async_api")
    html = path.read_text(encoding="utf-8")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await browser.close()


# ---------------------------------------------------------------------------
# 1. The fixtures themselves
# ---------------------------------------------------------------------------
#
# No browser. Their job is to stop everything below from going vacuous: a
# fixture quietly emptied or regenerated wrong would make every assertion
# about "the rows" true of nothing at all.

ALL_FIXTURES = [
    TRACKER_ROW,
    TRACKER_EMPTY,
    NOTIFICATIONS,
    PROFILE_PRE,
    PROFILE_HYDRATED,
    PROFILE_SKILLS,
]


@pytest.mark.parametrize("path", ALL_FIXTURES, ids=lambda p: p.name)
def test_the_fixture_exists_and_is_pure_ascii(path):
    assert path.exists(), f"missing fixture: {path}"
    raw = path.read_bytes()
    assert raw, f"empty fixture: {path}"
    raw.decode("ascii")


@pytest.mark.parametrize("path", ALL_FIXTURES, ids=lambda p: p.name)
def test_the_fixture_carries_no_session_material(path):
    html = path.read_text(encoding="utf-8")
    for token in ("li_at", "JSESSIONID", "csrfToken", "urn:li:member", "Bearer "):
        assert token not in html, token


@pytest.mark.parametrize("path", ALL_FIXTURES, ids=lambda p: p.name)
def test_no_fixture_names_a_real_person_or_employer(path):
    """These files are committed. Nobody real may be identifiable in one."""
    lowered = path.read_text(encoding="utf-8").lower()
    for token in (
        "sundeep",
        "redacted",
        "redacted",
        "redacted",
        "redacted",
        "redacted",
        "redacted",
        "redacted",
        "redacted",
        "redacted",
        "redacted",
        "redacted",
    ):
        assert token not in lowered, token


def test_the_tracker_fixture_keeps_the_duplicate_anchor():
    """The whole bug. One card, two links, one job id.

    A fixture that ended up with a single anchor would pass every assertion
    below against the OLD walk as well, and pin nothing.
    """
    html = TRACKER_ROW.read_text(encoding="utf-8")
    assert html.count(f"/jobs/view/{JOB_ID}") == 2


def test_the_profile_fixtures_have_no_h1_and_no_section_ids():
    """The two anchors the old profile reader was built on. Both gone."""
    for path in (PROFILE_PRE, PROFILE_HYDRATED):
        html = path.read_text(encoding="utf-8")
        assert "<h1" not in html, path.name
        for section_id in ('id="about"', 'id="experience"', 'id="skills"'):
            assert section_id not in html, (path.name, section_id)


def test_the_skills_fixture_does_not_contain_the_filter_pills():
    """So a passing skills test cannot be passing by accident."""
    html = PROFILE_SKILLS.read_text(encoding="utf-8")
    for pill in FILTER_PILLS:
        assert f">{pill}<" not in html, pill


# ---------------------------------------------------------------------------
# 1b. The anchors the old readers were built on, run against today's pages
# ---------------------------------------------------------------------------
#
# These pass both before and after the fix, and that is the point: they are
# the executable statement of WHY the readers had to change, in a form that
# goes red if LinkedIn ever puts these anchors back. Without them the profile
# and skills tests below fail on the pre-fix code only because the functions
# they call did not exist yet, which proves nothing about the page.

OLD_PROFILE_SELECTORS = {
    "name": ["main h1", "h1"],
    "headline": [
        "main .text-body-medium.break-words",
        "main .top-card-layout__headline",
        "main h1 + div",
    ],
    "location": [
        "main .text-body-small.inline.t-black--light.break-words",
        "main .top-card__subline-item",
    ],
    "photo": [
        "main img.pv-top-card-profile-picture__image",
        'main img[class*="profile-photo"]',
    ],
    "sections": ["#about", "#experience", "#education", "#skills"],
}

_COUNT_SELECTORS_JS = """
(selectors) => {
  const out = {};
  for (const [field, list] of Object.entries(selectors)) {
    let found = 0;
    for (const selector of list) {
      try { found += document.querySelectorAll(selector).length; } catch (e) {}
    }
    out[field] = found;
  }
  return out;
}
"""


@pytest.mark.parametrize("which", BOTH_PROFILES)
async def test_every_anchor_the_old_profile_reader_used_is_gone(which):
    """Measured: the old reader returned null for every field, on both renders."""

    async def work(page):
        return await page.evaluate(_COUNT_SELECTORS_JS, OLD_PROFILE_SELECTORS)

    found = await _with_page(PROFILE_FIXTURES[which], work)
    assert found == {
        "name": 0,
        "headline": 0,
        "location": 0,
        "photo": 0,
        "sections": 0,
    }, found


async def test_the_selector_the_old_skills_reader_used_finds_nothing():
    """``main ul li`` -- which on the live page matched the three filter pills."""

    async def work(page):
        records = await dom.harvest_block_cards(
            page, selectors=["main ul li"], max_items=200, max_chars=300
        )
        return records

    assert await _with_page(PROFILE_SKILLS, work) == []


# ---------------------------------------------------------------------------
# 2. The job tracker: the row, over the real markup
# ---------------------------------------------------------------------------


async def _tracker_rows(path: Path):
    async def work(page):
        records = await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )
        rows, dropped = dom.parse_all(records, shape.parse_job_card)
        return records, rows, dropped

    return await _with_page(path, work)


async def test_the_tracker_row_is_the_job_and_not_the_page():
    """The defect, stated as the values it got wrong.

    Every one of these was non-empty before the fix, which is exactly why
    "the field is populated" is not an assertion.
    """
    _, rows, dropped = await _tracker_rows(TRACKER_ROW)

    assert len(rows) == 1, rows
    assert dropped == 0
    assert rows[0] == {
        "title": JOB_TITLE,
        "company": JOB_COMPANY,
        "location": JOB_LOCATION,
        "status": "no longer accepting applications",
        "job_id": JOB_ID,
        "url": f"https://www.linkedin.com/jobs/view/{JOB_ID}",
    }


async def test_no_tracker_field_is_page_furniture():
    """The heading and the tab strip are the values the old walk returned."""
    _, rows, _ = await _tracker_rows(TRACKER_ROW)
    forbidden = (PAGE_HEADING, "Saved", "Applied", "Interview", "Date posted", DOT)
    for row in rows:
        for field in ("title", "company", "location"):
            value = row.get(field) or ""
            for token in forbidden:
                assert token not in value, (field, value, token)


async def test_the_harvested_tracker_record_stops_at_the_card():
    """The walk's own output, before any shaping touches it."""
    records, _, _ = await _tracker_rows(TRACKER_ROW)

    assert len(records) == 1, records
    text = records[0]["text"]
    assert JOB_TITLE in text
    assert PAGE_HEADING not in text, text[:200]
    assert "Date posted" not in text, text[:200]


async def test_an_empty_tracker_yields_no_rows_at_all():
    """The other half: nothing to parse, and nothing invented."""
    records, rows, _ = await _tracker_rows(TRACKER_EMPTY)
    assert records == []
    assert rows == []


# ---------------------------------------------------------------------------
# 3. The job tracker: the counts that make an empty list believable
# ---------------------------------------------------------------------------


async def _main_text(path: Path) -> str:
    return await _with_page(path, dom.read_main_text)


async def test_the_empty_tracker_publishes_its_own_counts():
    text = await _main_text(TRACKER_EMPTY)

    assert shape.parse_tracker_tabs(text) == {
        "saved": 0,
        "in_progress": 1,
        "applied": 0,
        "interview": 0,
    }
    assert shape.tracker_empty_state(text) == "No jobs here"


async def test_the_populated_tracker_publishes_its_own_counts():
    text = await _main_text(TRACKER_ROW)

    counts = shape.parse_tracker_tabs(text)
    assert counts == {"saved": 0, "draft": 1, "applied": 0, "interview": 0}
    # A tab LinkedIn draws without a count is absent rather than reported as
    # zero, because zero is a claim.
    assert "archived" not in counts
    # This page has a row, so it drew no empty state.
    assert shape.tracker_empty_state(text) is None


@pytest.mark.parametrize(
    "linkedin_count, empty_state, believable",
    [
        (0, "No jobs here", True),
        (0, "No matches", True),
        # LinkedIn says there are three. Nothing parsed. That is a broken read
        # and reporting it as an empty list is the lie this guards.
        (3, "No jobs here", False),
        # No empty state drawn: the page may simply not have rendered.
        (0, None, False),
        # The tab strip could not be read, so there is nothing to corroborate.
        (None, "No jobs here", False),
        (None, None, False),
    ],
)
def test_a_zero_is_only_believed_when_the_page_says_so(
    linkedin_count, empty_state, believable
):
    assert (
        shape.empty_is_believable(
            linkedin_count=linkedin_count, empty_state=empty_state
        )
        is believable
    )


# ---------------------------------------------------------------------------
# 4. Notifications
# ---------------------------------------------------------------------------

#: What the six frozen cards must come back as. Written out in full rather
#: than checked for non-emptiness: every one of these bodies was non-empty
#: before the fix too, just with "Unread notification." on the front.
EXPECTED_NOTIFICATIONS = [
    ("Senior Software Engineer: new opportunities in Riverton.", "22 minutes ago", True),
    (
        "Suggested for you: A note on hiring feedback: even a short reply after "
        "an interview means a great deal to a candidate. #Hiring #Career "
        "1,613 reactions 31 comments",
        "1 hour ago",
        False,
    ),
    (None, "1 hour ago", False),
    (
        "Robin Ellery commented on Marco Benitez's post: Congratulations Marco!!",
        "2 hours ago",
        False,
    ),
    ("Full Stack Engineer: new opportunities in Riverton.", "3 hours ago", False),
    (
        "Sam Okonkwo's connection is hiring for a Senior Software Engineer "
        "(SDE-3) Java at Brightpath. Explore jobs in your network.",
        "4 hours ago",
        False,
    ),
]

#: Text the page marks screen-reader-only. None of it is a notification.
A11Y_NOISE = (
    "Unread notification.",
    "Status is reachable",
    "Status is offline",
    "Status is online",
    "Profile image for several companies on LinkedIn",
)


async def _notification_rows():
    async def work(page):
        records = await dom.harvest_block_cards(
            page,
            selectors=dom.NOTIFICATION_SELECTORS,
            max_items=40,
            hidden_selector=dom.NOTIFICATION_HIDDEN_SELECTOR,
            time_selector=dom.NOTIFICATION_TIME_SELECTOR,
            unread_class=dom.NOTIFICATION_UNREAD_CLASS,
        )
        rows, dropped = dom.parse_all(records, shape.parse_notification)
        return records, rows, dropped

    return await _with_page(NOTIFICATIONS, work)


async def test_the_notification_harvest_finds_every_card():
    records, rows, dropped = await _notification_rows()
    assert len(records) == 6, records
    assert len(rows) == 6
    assert dropped == 0


async def test_no_notification_body_carries_accessibility_text():
    """The defect. "Unread notification." was welded to the front of a body."""
    _, rows, _ = await _notification_rows()
    for row in rows:
        for noise in A11Y_NOISE:
            assert noise not in row["text"], (noise, row["text"])


async def test_every_notification_body_is_exactly_what_the_page_showed():
    _, rows, _ = await _notification_rows()
    for row, (expected, _, _) in zip(rows, EXPECTED_NOTIFICATIONS):
        if expected is None:
            continue
        assert row["text"] == expected


async def test_a_body_the_page_prints_twice_keeps_one_copy():
    """The trap under the fix.

    Three of these cards repeat their whole body in a hidden span. Deleting
    every hidden string by phrase would empty them, so the subtraction is by
    count -- one removal per hidden element -- and this is the card that
    proves it did not take both.
    """
    _, rows, _ = await _notification_rows()
    body = rows[2]["text"]
    assert body.startswith("Forgeworks was live for redacted with Boulder:")
    assert body.count("Forgeworks was live") == 1


async def test_every_notification_carries_the_time_the_page_wrote():
    """``when`` was null on all 22 rows of the live page."""
    _, rows, _ = await _notification_rows()
    assert [row.get("when") for row in rows] == [
        when for _, when, _ in EXPECTED_NOTIFICATIONS
    ]


async def test_a_notification_body_does_not_end_with_its_own_timestamp():
    _, rows, _ = await _notification_rows()
    for row in rows:
        assert not row["text"].rstrip().endswith(("22m", "1h", "2h", "3h", "4h"))


async def test_the_unread_flag_is_read_before_the_page_load_destroys_it():
    """Exactly one of the six was unread, and the badge is about to be cleared."""
    _, rows, _ = await _notification_rows()
    assert [row.get("unread") for row in rows] == [
        unread for _, _, unread in EXPECTED_NOTIFICATIONS
    ]
    assert sum(1 for row in rows if row["unread"]) == 1


# ---------------------------------------------------------------------------
# 4b. The same card as the LIVE page lays it out
# ---------------------------------------------------------------------------
#
# The fixtures have their styles stripped, which runs the hidden copy and the
# visible one together on one innerText line. The live page puts them on
# separate lines. Both must give the same answer, so the live layout is pinned
# here as a literal -- and with a control that shows the hidden list is what
# does the work, rather than something else cleaning up after it.

LIVE_CARD = {
    "href": "https://www.linkedin.com/jobs/search-results/?keywords=Senior",
    "text": (
        "Profile image for several companies on LinkedIn\n\n"
        "Unread notification.\n\n"
        "Senior Software Engineer: new opportunities in Riverton.\n"
        "Senior Software Engineer: new opportunities in Riverton.\n"
        "View jobs\nView jobs\n\n22m"
    ),
    "hidden": [
        "Profile image for several companies on LinkedIn",
        "Unread notification.",
        "Senior Software Engineer: new opportunities in Riverton.",
        "View jobs",
    ],
    "time": "22m",
    "unread": True,
}


def test_the_live_layout_body_is_stripped_of_accessibility_text():
    """Red against the pre-fix code, through an API that already existed.

    ``parse_notification`` predates this fix, so this is one of the few places
    the OLD behaviour can be exercised directly: before it, this same record
    came back as "Profile image for several companies on LinkedIn Unread
    notification. Senior Software Engineer ... View jobs 22m".
    """
    row = shape.parse_notification(LIVE_CARD)
    assert row is not None
    assert row["text"] == "Senior Software Engineer: new opportunities in Riverton."


def test_the_live_layout_carries_the_time_the_page_wrote():
    """The other half, split out so its own failure is visible on its own."""
    row = shape.parse_notification(LIVE_CARD)
    assert row is not None
    assert row["when"] == "22 minutes ago"
    assert row["unread"] is True


def test_without_the_hidden_list_the_accessibility_text_survives():
    """The control. A check that cannot fail certifies nothing."""
    stripped = dict(LIVE_CARD)
    stripped.pop("hidden")
    row = shape.parse_notification(stripped)
    assert row is not None
    assert "Unread notification." in row["text"]


def test_without_the_time_element_there_is_no_when():
    """The other control: the body genuinely does not contain a readable time."""
    stripped = dict(LIVE_CARD)
    stripped["time"] = ""
    row = shape.parse_notification(stripped)
    assert row is not None
    assert "when" not in row


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("22m", "22 minutes ago"),
        ("1h", "1 hour ago"),
        ("2h", "2 hours ago"),
        ("3d", "3 days ago"),
        ("1w", "1 week ago"),
        ("2mo", "2 months ago"),
        ("1y", "1 year ago"),
    ],
)
def test_a_bare_compact_time_is_spelled_out(raw, expected):
    assert shape.compact_time_ago(raw) == expected


@pytest.mark.parametrize("text", ["1 reaction", "", "hello", "5x", "12", "3M Co"])
def test_a_bare_compact_time_reader_refuses_everything_else(text):
    assert shape.compact_time_ago(text) is None


def test_the_two_time_readers_disagree_about_3m_on_purpose():
    """The reason there are two of them, in one assertion.

    ``compact_time_ago`` is handed the notification card's OWN time element --
    a string LinkedIn has already declared to be a timestamp -- so "3M" there
    is three minutes and reading it as such is right. ``find_time_ago`` scans
    free prose, where "3M" is a company, so it requires the word "ago" and
    finds nothing. Folding the two together would break one or the other.
    """
    assert shape.compact_time_ago("3M") == "3 minutes ago"
    assert shape.find_time_ago(["3M Company"]) is None


@pytest.mark.parametrize("text", ["3M Company", "1 reaction", "Head of 5d Printing"])
def test_free_text_scanning_still_refuses_a_time_with_no_ago(text):
    """The guard the compact reader must not have loosened."""
    assert shape.find_time_ago([text]) is None


# ---------------------------------------------------------------------------
# 5. The profile
# ---------------------------------------------------------------------------


async def _profile(which: str):
    async def work(page):
        fields = await dom.read_profile_fields(page)
        sections = fields.get("sections") or []
        topcard = shape.pick_topcard(sections, fields.get("title"))
        return fields, sections, topcard

    return await _with_page(PROFILE_FIXTURES[which], work)


@pytest.mark.parametrize("which", BOTH_PROFILES)
async def test_the_profile_identity_is_read_from_a_page_with_no_h1(which):
    """The defect: name, headline and location all read null and the tool errored."""
    _, _, topcard = await _profile(which)
    identity = shape.parse_profile_topcard((topcard or {}).get("lines") or [])

    assert identity["name"] == NAME
    assert identity["headline"] == HEADLINE
    assert identity["location"] == LOCATION


@pytest.mark.parametrize("which", BOTH_PROFILES)
async def test_the_school_is_not_mistaken_for_the_location(which):
    """It sits between the headline and the location on this render.

    Reading the location as "the second eligible line" returned the school,
    which is a plausible-looking wrong answer -- the worst kind.
    """
    _, _, topcard = await _profile(which)
    identity = shape.parse_profile_topcard((topcard or {}).get("lines") or [])
    assert identity["location"] != SCHOOL
    assert identity["headline"] != SCHOOL


async def test_both_renders_produce_the_same_identity():
    """Hydration timing must not change what the operator is told."""
    answers = []
    for which in BOTH_PROFILES:
        _, _, topcard = await _profile(which)
        answers.append(
            shape.parse_profile_topcard((topcard or {}).get("lines") or [])
        )
    assert answers[0] == answers[1]


@pytest.mark.parametrize("which", BOTH_PROFILES)
async def test_the_topcard_is_found_by_name_not_by_position(which):
    _, sections, topcard = await _profile(which)
    assert topcard is not None
    assert topcard["heading"] == NAME
    assert sections[0]["heading"] == NAME


def test_the_topcard_is_still_found_when_it_is_not_the_first_section():
    """Position is a fallback, so it must not be the only route."""
    sections = [
        {"heading": "Analytics", "lines": ["Analytics"], "images": 0},
        {"heading": NAME, "lines": [NAME, HEADLINE], "images": 1},
    ]
    picked = shape.pick_topcard(sections, f"{NAME} | LinkedIn")
    assert picked["heading"] == NAME


async def test_the_photo_is_detected_on_a_page_with_no_photo_class():
    """``img[class*="profile-photo"]`` matched nothing, so has_photo read false."""
    _, _, topcard = await _profile("hydrated")
    assert topcard["images"] > 0


async def test_the_about_text_is_read_from_the_hydrated_render():
    _, sections, _ = await _profile("hydrated")
    about = shape.profile_section_lines(sections, "About")
    assert about == [
        "I build production backend services in Node.js and TypeScript, and I "
        "have spent five years doing it across payments, messaging "
        "infrastructure and consumer health."
    ]


async def test_the_pre_hydration_render_simply_has_no_about_section():
    """And that is UNKNOWN, not "he has no About" -- the tool says which."""
    _, sections, _ = await _profile("pre_hydration")
    assert [s["heading"] for s in sections] == [NAME]
    assert shape.profile_section_lines(sections, "About") == []


async def test_the_hydrated_render_shows_which_sections_arrived():
    _, sections, _ = await _profile("hydrated")
    assert [s["heading"] for s in sections] == [NAME, "Analytics", "About"]


# ---------------------------------------------------------------------------
# 6. The skills page
# ---------------------------------------------------------------------------


async def _skills():
    async def work(page):
        records = await dom.harvest_linked_cards(
            page, href_pattern=dom.SKILL_HREF, max_items=200, max_chars=300
        )
        skills: list[str] = []
        for record in records:
            lines = shape.content_lines(record.get("text", ""))
            if not lines:
                continue
            name = shape.trim(lines[0], 80)
            if name and name not in skills:
                skills.append(name)
        return records, skills

    return await _with_page(PROFILE_SKILLS, work)


async def test_the_skills_page_yields_skills_and_not_filter_pills():
    """It was returning "All", "Industry Knowledge", "Tools & Technologies"."""
    records, skills = await _skills()
    assert len(records) == 6
    assert skills == SKILLS
    for pill in FILTER_PILLS:
        assert pill not in skills


async def test_a_skill_keeps_only_its_name_not_its_evidence_lines():
    """The first entry carries two extra lines. Neither is the skill."""
    _, skills = await _skills()
    assert skills[0] == "Node.js"
    assert not any("experiences at" in skill for skill in skills)
    assert not any("Skill Assessment" in skill for skill in skills)
