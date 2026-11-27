"""His invitation manager, both tabs (census ``N 13`` received, ``N 9`` sent), read on live session 11's captures.

THE PAGES ARE REAL. ``tests/fixtures/synthetic/live11_invitations_words.html``
and ``live11_invitations_sent_words.html`` are the live lane's session-11
tracked copies (``tests/fixtures/live11/invitations.html``,
``invitations_sent.html``) with LinkedIn's own words put back where the keyed
shape proves them (``scripts/_build_live11_word_fixtures.py``;
``tests/test_live11_word_fixtures.py`` holds each to its copy token by token).
Every name, headline and label is the skeleton's ``x``. Every test reads one
of those pages, the tracked copy itself, or one of them with one thing
planted.

THE PLANTS, each changing the verdict or, for a name in a label, nothing:

* the tracked copy WITHOUT the words -> no row is an invitation, and it raises;
* the Sent tab current on the received reader (and the Received tab on the
  sent reader) -> the read refuses as the wrong side;
* a third button in a received row -> that row is not read;
* a name in every member link and every name line -> it comes back inside
  the person records and nowhere else;
* a name in every ``aria-label`` -> the answer is identical.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium over ``set_content``,
every request refused first.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import invitation_manager as im
from linkedin_server import people_data
from linkedin_server.errors import ExtractionFailedError
from tests.plantedpage import PLANT, carries_the_plant_outside_records
from tests.test_writes import browser_page  # noqa: F401 -- fixture

REPO = Path(__file__).resolve().parents[1]
RECEIVED = REPO / "tests" / "fixtures" / "synthetic" / "live11_invitations_words.html"
SENT = REPO / "tests" / "fixtures" / "synthetic" / "live11_invitations_sent_words.html"
RECEIVED_COPY = REPO / "tests" / "fixtures" / "live11" / "invitations.html"
SENT_COPY = REPO / "tests" / "fixtures" / "live11" / "invitations_sent.html"

#: A person record as the skeleton yields one: the skeleton's ``x``.
def _person(headline: Any) -> dict[str, Any]:
    return {
        "name": "x", "headline": headline, "link": "https://www.linkedin.com/in/x/",
        "degree": None, people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE,
    }


async def _refused(route: Any) -> None:
    await route.abort()


async def _read(page: Any, html: str, reader: Any) -> dict[str, Any]:
    await page.route("**/*", _refused)
    await page.set_content(html, wait_until="domcontentloaded")
    return await reader(page)


def _text(path: Path) -> str:
    return path.read_text(encoding="ascii")


# ---------------------------------------------------------------------------
# The received tab (N 13)
# ---------------------------------------------------------------------------


async def test_the_received_tab_reads_its_three_invitations(browser_page):
    out = await _read(browser_page, _text(RECEIVED), im.read_received_invitations)
    assert (out["side"], out["refused"]) == ("received", None)
    assert (out["rows_seen"], out["rows_read"]) == (3, 3)
    assert out["kinds"] == {"connection": 2, "newsletter": 1, "other": 0}
    assert out["invitations"] == [
        {"kind": "connection", "sender": _person(None)},
        {"kind": "connection", "sender": _person(None)},
        {
            "kind": "newsletter",
            # The Page's link is a slug on the capture, so it is not kept:
            # a link leaves only in its numeric form.
            "sender": {"organisation": "x", "link": None,
                       people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE},
        },
    ]
    assert out["row_gaps"] == {gap: 0 for gap in im.ROW_GAPS}
    assert out["readable"] is True and out["one_page"] is True


async def test_the_suggestion_cards_on_the_same_page_are_not_invitations(browser_page):
    """The page draws 22 list items: three invitations and nineteen
    suggestions, each with a Connect button and no Accept."""
    html = _text(RECEIVED)
    assert html.count('role="listitem"') == 22
    assert len(re.findall(r">\s*Connect\s*<", html)) == 19
    out = await _read(browser_page, html, im.read_received_invitations)
    assert out["rows_seen"] == 3


async def test_without_linkedins_words_no_row_is_an_invitation_and_it_raises(browser_page):
    """THE RED: the tracked copy, whose Accept and Ignore are the skeleton's
    ``x``, draws no invitation row by LinkedIn's words -- and an
    uncorroborated zero raises, quoting nothing of the page."""
    with pytest.raises(ExtractionFailedError) as raised:
        await _read(browser_page, _text(RECEIVED_COPY), im.read_received_invitations)
    assert "Accept button" in str(raised.value)


async def test_the_sent_tab_current_refuses_the_received_reader(browser_page):
    html = _text(RECEIVED)
    received = re.search(r'<a [^>]*aria-current="true"[^>]*href="[^"]*/received"', html)
    assert received is not None
    html = html.replace(received.group(0), received.group(0).replace(' aria-current="true"', ""), 1)
    html = html.replace(
        'href="https://www.linkedin.com/mynetwork/invitation-manager/sent">',
        'aria-current="true" href="https://www.linkedin.com/mynetwork/invitation-manager/sent">', 1,
    )
    out = await _read(browser_page, html, im.read_received_invitations)
    assert (out["side"], out["refused"]) == ("sent", "not_the_received_side")
    assert out["invitations"] == [] and out["rows_seen"] == 0


async def test_a_received_row_with_a_third_button_is_not_read(browser_page):
    html = _text(RECEIVED)
    first_accept = html.index(">\nAccept\n<")
    cut = html.index("</button>", first_accept) + len("</button>")
    html = html[:cut] + '<button type="button"><span>x</span></button>' + html[cut:]
    out = await _read(browser_page, html, im.read_received_invitations)
    assert out["rows_seen"] == 3
    assert out["row_gaps"]["controls_not_the_measured_pair"] == 1
    assert len(out["invitations"]) == 2


async def test_a_senders_name_comes_back_only_inside_a_record(browser_page):
    html = re.sub(
        r'(<a [^>]*href="https://www\.linkedin\.com/in/x/"[^>]*>\s*<strong[^>]*>\s*)x(\s)',
        lambda m: m.group(1) + PLANT + m.group(2),
        _text(RECEIVED),
    )
    out = await _read(browser_page, html, im.read_received_invitations)
    senders = [i["sender"] for i in out["invitations"] if i["kind"] == "connection"]
    assert [s["name"] for s in senders] == [PLANT, PLANT]
    outside, records = carries_the_plant_outside_records(out)
    assert outside == [] and records > 0


async def test_a_name_in_every_label_is_never_read(browser_page):
    plain = await _read(browser_page, _text(RECEIVED), im.read_received_invitations)
    planted = await _read(
        browser_page, _text(RECEIVED).replace('aria-label="x"', f'aria-label="{PLANT}"'),
        im.read_received_invitations,
    )
    assert planted == plain


# ---------------------------------------------------------------------------
# The sent tab (N 9)
# ---------------------------------------------------------------------------


async def test_the_sent_tab_reads_its_five_invitations_and_their_ages(browser_page):
    out = await _read(browser_page, _text(SENT), im.read_sent_invitations)
    assert (out["side"], out["refused"]) == ("sent", None)
    assert (out["rows_seen"], out["rows_read"]) == (5, 5)
    assert [i["member"] for i in out["invitations"]] == [_person("x")] * 5
    assert [i["sent_ago"] for i in out["invitations"]] == (
        [{"count": 2, "unit": "week"}] * 3 + [{"count": 1, "unit": "month"}] * 2
    )
    assert out["row_gaps"] == {gap: 0 for gap in im.ROW_GAPS}
    assert out["readable"] is True


async def test_without_linkedins_words_the_sent_tab_has_no_row_and_raises(browser_page):
    with pytest.raises(ExtractionFailedError) as raised:
        await _read(browser_page, _text(SENT_COPY), im.read_sent_invitations)
    assert "Withdraw link" in str(raised.value)


async def test_the_received_tab_refuses_the_sent_reader(browser_page):
    out = await _read(browser_page, _text(RECEIVED), im.read_sent_invitations)
    assert (out["side"], out["refused"]) == ("received", "not_the_sent_side")
    assert out["invitations"] == []


async def test_a_sent_members_name_and_headline_come_back_only_inside_a_record(browser_page):
    html = re.sub(r"(<p class=\"[^\"]*\">\n)x(\n</p>)", lambda m: m.group(1) + PLANT + m.group(2),
                  _text(SENT))
    out = await _read(browser_page, html, im.read_sent_invitations)
    assert [i["member"]["name"] for i in out["invitations"]] == [PLANT] * 5
    outside, records = carries_the_plant_outside_records(out)
    assert outside == [] and records > 0


async def test_a_name_in_every_label_of_the_sent_tab_is_never_read(browser_page):
    plain = await _read(browser_page, _text(SENT), im.read_sent_invitations)
    planted = await _read(
        browser_page, _text(SENT).replace('aria-label="x"', f'aria-label="{PLANT}"'),
        im.read_sent_invitations,
    )
    assert planted == plain


@pytest.mark.parametrize(
    ("line", "age"),
    [
        ("Sent 2 weeks ago", {"count": 2, "unit": "week"}),
        ("Sent 1 month ago", {"count": 1, "unit": "month"}),
        ("  Sent 3 days ago ", {"count": 3, "unit": "day"}),
        ("Sent today", {"count": 0, "unit": "day"}),
        ("Sent yesterday", {"count": 1, "unit": "day"}),
        ("Sent 2 weeks ago by somebody", None),
        ("sent 2 weeks ago", None),
        ("Sent a while ago", None),
        (None, None),
    ],
)
def test_the_sent_age_is_linkedins_template_or_nothing(line, age):
    assert im.parse_sent_age(line) == age


# ---------------------------------------------------------------------------
# The landings, and the closed words
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("landed", "received", "sent"),
    [
        ("https://www.linkedin.com/mynetwork/invitation-manager/", True, False),
        # LinkedIn's own tab-strip spelling. Refused here (False) until
        # 2026-11-27: live session 12 LANDED on it (load 28), and lane net7
        # admitted it by its own line and made the reader accept it, on the
        # orchestrator's ruling (tests/test_net7_admissions.py).
        ("https://www.linkedin.com/mynetwork/invitation-manager/received/", True, False),
        ("https://www.linkedin.com/mynetwork/invitation-manager/sent/", False, True),
        ("https://www.linkedin.com/mynetwork/invitation-manager/sent/CONNECTION/", False, False),
        ("https://www.linkedin.com/mynetwork/", False, False),
        ("http://www.linkedin.com/mynetwork/invitation-manager/", False, False),
        (None, False, False),
    ],
)
def test_each_reader_knows_its_own_landing(landed, received, sent):
    assert im.landed_on_received(landed) is received
    assert im.landed_on_sent(landed) is sent


def test_every_refusal_carries_only_closed_words():
    for out in (im.received_landed_elsewhere(), im.sent_landed_elsewhere()):
        assert out["refused"] == "landed_elsewhere" and out["invitations"] == []
        assert out["readable"] is False


def test_the_module_presses_nothing_and_stores_nothing():
    """No click, fill, press, write or log in the module's source."""
    source = (REPO / "linkedin_server" / "invitation_manager.py").read_text(encoding="utf-8")
    for call in (".click(", ".fill(", ".press(", ".check(", ".tap(", "open(", "logging", ".goto("):
        assert call not in source, call
