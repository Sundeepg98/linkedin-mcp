"""His follower list's PEOPLE, as records (census ``P L2b``, the WHO half).

THE LANE LEAD'S RULING, 2026-10-10: the row's payload is WHO, so a counts-only
reader does not deliver it (WHO-WHICH-COUNTS-ARE-NOT-DELIVERY), and the names
come back at runtime (NAMES-AT-RUNTIME) as people records under
PEOPLE-DATA-MITIGATIONS. ``followers_list.read_followers_list`` keeps every
count it returned before and adds ``followers``: one
``people_data.Person`` envelope per row read, beside that row's relation.

THE PAGE: ``tests/fixtures/synthetic/followers_list_people.html``, built by
``scripts/_build_followers_people_fixture.py`` from the session-2 skeleton --
the same markup, each row's member links, name and headline replaced by the
repository's DECLARED synthetic people. The first test rebuilds it in memory
and compares, so the page is provably that skeleton plus those people.

THE MITIGATIONS, each shown failing without its code: sanitised (a zero-width
and a direction override planted in a name), marked, declared fields only,
bounded (a page drawing 120 rows), visible only ("LinkedIn Member" stays
that), and nothing written. A name planted in every button's ``aria-label``
never appears.

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``,
every request refused first.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Any

from linkedin_server import followers_list, people_data
from tests.plantedpage import PLANT, carries_a_plant_word
from tests.test_writes import browser_page  # noqa: F401 -- fixture

REPO = Path(__file__).resolve().parents[1]
SKELETON = REPO / "tests" / "fixtures" / "live2" / "followers.html"
FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "followers_list_people.html"
MODULE = REPO / "linkedin_server" / "followers_list.py"

sys.path.insert(0, str(REPO / "scripts"))
import _build_followers_people_fixture as builder  # noqa: E402

#: A row's follow-state word, in document order, as the skeleton draws it.
ROW_WORD = re.compile(
    r'<span class="artdeco-button__text">\s*(Following|Follow)\s*</span>\s*</button>'
)
ROW_MARK = builder.ROW_MARK


def _fixture() -> str:
    return FIXTURE.read_text(encoding="ascii")


async def _refused(route: Any) -> None:
    await route.abort()


async def _read(page: Any, html: str) -> dict[str, Any]:
    await page.route("**/*", _refused)
    await page.set_content(html, wait_until="domcontentloaded")
    return await followers_list.read_followers_list(page)


def _expected() -> set[tuple[str, str, str, Any]]:
    """(name, headline, link, relation) per row, from the builder's tables and
    the skeleton's own words -- the TEST pairs them in document order; the
    reader never does."""
    words = ROW_WORD.findall(_fixture())
    assert len(words) == len(builder.PEOPLE) == 10, words
    out = set()
    for index, ((name, slug), word) in enumerate(zip(builder.PEOPLE, words)):
        headline = builder.HEADLINES[index % len(builder.HEADLINES)]
        link = f"https://www.linkedin.com/in/{slug}/"
        out.add((name, headline, link, word == "Following"))
    return out


def _got(answer: dict[str, Any]) -> set[tuple[str, Any, Any, Any]]:
    return {
        (f["member"]["name"], f["member"]["headline"], f["member"]["link"], f["he_follows_back"])
        for f in answer["followers"]
    }


def outside_records(answer: Any) -> list[str]:
    """Strings in ``answer`` that are neither inside a people record nor one
    of the module's own closed words. Empty means the declared channel is the
    only one page text took."""
    allowed = {
        "own_follower_list", "not_read", followers_list.SCOPE,
        *followers_list.SIDES, *followers_list.REFUSALS,
    }
    found: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            if people_data.as_record(value) is not None:
                return
            for key, item in value.items():
                walk(key, f"{path} key")
                walk(item, f"{path}[{key!r}]")
        elif isinstance(value, (list, tuple)):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")
        elif isinstance(value, str) and value not in allowed and not path.endswith(" key"):
            found.append(path)
        elif isinstance(value, str) and path.endswith(" key") and value not in _KEYS:
            found.append(f"{path} {value!r}")

    walk(answer, "$")
    return found


_KEYS = frozenset(
    {
        "surface", "side", "refused", "tabs_seen", "lists_seen", "rows_seen",
        "rows_read", "he_follows_back", "he_does_not_follow_back", "unknown",
        "unknown_why", "one_page", "beyond_first_render", "readable", "scope",
        "followers", "names_unread", "headlines_unread", "member",
        *followers_list.UNKNOWN_REASONS,
    }
)


# ---------------------------------------------------------------------------
# The fixture is the skeleton plus declared people, and nothing else
# ---------------------------------------------------------------------------


def test_the_fixture_is_exactly_what_the_builder_writes_from_the_skeleton() -> None:
    assert builder.build(SKELETON.read_text(encoding="ascii")) == _fixture()
    text = _fixture()
    for name, slug in builder.PEOPLE:
        assert text.count(f"/in/{slug}?") == 2, slug
        assert text.count(name) == 1, name
    assert "in/x?miniProfileUrn" not in text


# ---------------------------------------------------------------------------
# The records
# ---------------------------------------------------------------------------


async def test_each_follower_comes_back_as_a_record_beside_its_relation(browser_page) -> None:
    answer = await _read(browser_page, _fixture())
    # Every count is the counts reader's, unchanged.
    assert (answer["side"], answer["refused"], answer["rows_seen"], answer["rows_read"]) == (
        "followers", None, 10, 10
    ), answer
    assert (answer["he_follows_back"], answer["he_does_not_follow_back"], answer["unknown"]) == (
        9, 1, 0
    ), answer
    assert (answer["names_unread"], answer["headlines_unread"]) == (0, 0), answer
    assert _got(answer) == _expected()
    for follower in answer["followers"]:
        assert set(follower) == {"member", "he_follows_back"}, follower
        member = follower["member"]
        assert frozenset(member) == people_data.PERSON_SHAPE, member
        assert member[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
        assert member["degree"] is None
        assert type(people_data.as_record(member)) is people_data.Person
    assert outside_records(answer) == []


async def test_a_name_in_every_button_label_never_appears(browser_page) -> None:
    """Live, the follow-state button's label is the member's NAME. Planted in
    every row button's ``aria-label`` and every photo's ``alt``, it appears
    nowhere -- the records hold the row links' names, as before."""
    planted = _fixture().replace('<button aria-label="x" id="k', f'<button aria-label="{PLANT}" id="k')
    planted = planted.replace('alt="x"', f'alt="{PLANT}"')
    assert planted.count(PLANT) >= 20
    answer = await _read(browser_page, planted)
    assert not carries_a_plant_word(repr(answer))
    assert _got(answer) == _expected()


# ---------------------------------------------------------------------------
# The mitigations, each shown failing without its code
# ---------------------------------------------------------------------------

#: Invisible and direction-changing characters, planted inside one name.
ZERO_WIDTH = chr(0x200B)
OVERRIDE = chr(0x202E)


def _rename_first(html: str, into: str) -> str:
    name = builder.PEOPLE[0][0]
    assert html.count(name) == 1
    return html.replace(name, into)


def _rows(html: str, total: int) -> str:
    """The fixture with its ten rows repeated to ``total`` (whole <li> rows)."""
    start = html.index("<li", html.index('<ul role="list"'))
    end = html.index("</ul>", start)
    items = html[start:end]
    copies = (items * (total // 10 + 1))
    starts = [m.start() for m in re.finditer(r"<li ", copies)]
    cut = starts[total] if total < len(starts) else len(copies)
    return html[:start] + copies[:cut] + html[end:]


async def test_each_mitigation_holds_and_fails_without_its_code(browser_page, monkeypatch) -> None:
    html = _fixture()
    first = builder.PEOPLE[0][0]

    # 2. SANITISED: a zero-width space and a direction override inside a name
    # are gone from the record; with the sanitiser stood down they survive.
    dirty = _rename_first(html, first.replace(" ", ZERO_WIDTH + " " + OVERRIDE))
    answer = await _read(browser_page, dirty)
    names = {f["member"]["name"] for f in answer["followers"]}
    assert first in names and not any(ZERO_WIDTH in n or OVERRIDE in n for n in names), names
    with monkeypatch.context() as m:
        m.setattr(people_data, "sanitise", lambda text, *, cap: ("" if text is None else str(text))[:cap])
        unguarded = await _read(browser_page, dirty)
    assert any(ZERO_WIDTH in f["member"]["name"] for f in unguarded["followers"]), "control"

    # 5. VISIBLE ONLY: a row LinkedIn draws as "LinkedIn Member" stays that.
    answer = await _read(browser_page, _rename_first(html, people_data.ANONYMISED_NAME))
    assert people_data.ANONYMISED_NAME in {f["member"]["name"] for f in answer["followers"]}

    # 4. BOUNDED: a page drawing 120 rows gives 100 records, the rest counted
    # and not read; with the bound lifted, all 120 would come back.
    many = _rows(html, 120)
    answer = await _read(browser_page, many)
    assert (answer["rows_seen"], answer["rows_read"], len(answer["followers"])) == (120, 100, 100)
    with monkeypatch.context() as m:
        m.setattr(followers_list, "MAX_ROWS_READ", 1000)
        unbounded = await _read(browser_page, many)
    assert len(unbounded["followers"]) == 120, "control"

    # 1. DECLARED FIELDS ONLY: a record widened by one key is no record, and
    # its words are then found outside the declared channel.
    widened = {"member": {**answer["followers"][0]["member"], "label": PLANT}, "he_follows_back": True}
    assert outside_records({"followers": [widened]}) != []
    assert outside_records({"followers": answer["followers"]}) == []


#: Calls that would store, log or act; ``get_attribute`` is admitted for one
#: literal, ``href`` (the record's link), and checked separately.
_FORBIDDEN = frozenset(
    {
        "click", "press", "fill", "type", "goto", "evaluate", "evaluate_all",
        "scroll_into_view_if_needed", "wheel", "open", "write", "write_text",
        "write_bytes", "dump", "debug", "info", "warning", "error", "exception",
        "critical", "log",
    }
)


def _calls(source: str) -> tuple[set[str], list[Any]]:
    """Method names called, and the first argument of every get_attribute."""
    names: set[str] = set()
    attributes: list[Any] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if name:
                names.add(name)
            if name == "get_attribute":
                first = node.args[0] if node.args else None
                attributes.append(first.value if isinstance(first, ast.Constant) else first)
    return names, attributes


def test_the_module_stores_nothing_and_reads_no_attribute_but_href() -> None:
    """3. NEVER STORED, and the label unread: no write, log or act, and the
    one attribute read is ``href``."""
    names, attributes = _calls(MODULE.read_text(encoding="utf-8"))
    assert not names & _FORBIDDEN, sorted(names & _FORBIDDEN)
    assert attributes == ["href"], attributes


def test_control_the_store_and_attribute_check_can_fail() -> None:
    planted = (
        "async def read(row, log):\n"
        "    label = await row.get_attribute('aria-label')\n"
        "    log.info(label)\n"
        "    open('x').write(label)\n"
    )
    names, attributes = _calls(planted)
    assert names & _FORBIDDEN == {"info", "open", "write"}
    assert attributes == ["aria-label"]
