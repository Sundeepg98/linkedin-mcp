"""P A22 -- which current role his intro shows -- is the intro editor's
"Organization" select, drawn since the live lane's session 7 (2026-10-10), and
the shipped field write chooses it, saves it, and puts it back.

THE MEASUREMENT (lane B1, 2026-10-10, offline). Session 7 kept his intro
editor as a keyed skeleton. Its one dialog holding Save draws ELEVEN controls,
each accounted for by its label's keyed shape under the session's own key:
two unnamed text inputs (the first- and last-name fields, P A4), "Additional
name", "Pronouns" (a select of five), "Country/Region", "City" and "Industry"
(each an input carrying aria-autocomplete="list"), "Organization" (a select of
two: "Please select" with an empty value, and one entry whose value is a
ten-digit company id), "Education" (a select of two) and the two settings
switches. Session 1's capture (2026-09-23) drew the same dialog WITHOUT the
"Organization" select. Help article a550169 names the control: "If you've
already added Primary Position(s) select the company you want to show in your
intro" -- the company shown in the intro is chosen with exactly this select,
beside its school counterpart "Education" (P A21, proven both directions by
the same route in session 6). That the label means that act is DERIVED from
those words and that placement; the control itself is MEASURED.

THE WORLD. ``tests/fixtures/live7/editor.html``, built by
``scripts/_build_intro_editor_live7_fixture.py`` from that skeleton: every text
of his one ``x``, LinkedIn's labels and option words restored by their keyed
shapes, the organization and school options INVENTED ("Example Organisation",
"Example School"). Its inputs stay on the live lane's box, so the digest is
pinned here. The world below renders the stored choice, plants a notify
control read off (condition 1 of SELF-PROFILE-EDITS-NOT-OUTWARD, as every
editor world in this suite plants it) and a Save listener that persists the
select's chosen text and closes the dialog, as LinkedIn does on a save.

WHAT IS DRIVEN. The real two calls -- ``preview`` (mints) and ``consume``
(redeems) -- then ``writes.perform``, then the navigation a following tool
call would make: the act (the unset option, no organization in the intro) and
its INVERSE (the exact original, from the receipt's own ``to_put_it_back``).

RED FIRST: the same write over session 4's tracked editor
(``tests/fixtures/live4/editor.html``), which draws no "Organization" select,
is refused and stores nothing -- so the pass below is the control's presence,
not the harness's.

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
from html.parser import HTMLParser

import pytest

from linkedin_server import writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_an_empty_original_is_restored_by_a_clear import _fetch_nothing
from tests.test_profile_editor_commit import (
    _EDITOR_URL,
    _LANDED_EDITOR,
    _LANDED_PROFILE,
    _PROFILE_HTML,
)
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = pathlib.Path(__file__).resolve().parents[1]
LIVE7_EDITOR = REPO / "tests" / "fixtures" / "live7" / "editor.html"
LIVE4_EDITOR = REPO / "tests" / "fixtures" / "live4" / "editor.html"

#: The committed fixture's digest, over its TEXT. Its builder's inputs stay on
#: the live lane's box; re-run the builder with ``--check`` there.
LIVE7_EDITOR_SHA256 = "e02c798cc1612a1b31887b3d5cf49ffd8986cd8eff1601a94261611adac598af"

_ACTION = "update_profile_field"
_SPEC = spec_for_action(_ACTION)

FIELD = "Organization"
UNSET = "Please select"
#: INVENTED by the builder: the one entry of the select, never a real one.
ORIGINAL = "Example Organisation"

_NOTIFY_OFF = '<label for="b1-notify">Notify network</label><input id="b1-notify" type="checkbox" role="switch">'

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr"}


# ---------------------------------------------------------------------------
# The fixture, read offline
# ---------------------------------------------------------------------------


class _Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.kids: list[_Node] = []
        self.text: list[str] = []


class _Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs, self.cur)
        self.cur.kids.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(_Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.parent is not None:
            self.cur = node.parent

    def handle_data(self, data):
        if data.strip():
            self.cur.text.append(" ".join(data.split()))


def _walk(node):
    yield node
    for kid in node.kids:
        yield from _walk(kid)


def _text(node) -> str:
    return " ".join([*node.text, *(_text(k) for k in node.kids)]).strip()


def _dialog_controls(html: str) -> list[tuple[str, str, str]]:
    """(tag, accessible name by label-for / aria-label, kind) for every form
    control inside the ONE dialog holding a button reading exactly Save."""
    tree = _Tree()
    tree.feed(html)
    nodes = list(_walk(tree.root))
    dialogs = [n for n in nodes if n.tag == "dialog"
               and sum(1 for b in _walk(n) if b.tag == "button" and _text(b) == "Save") == 1]
    assert len(dialogs) == 1, len(dialogs)
    labels = {n.attrs.get("for"): _text(n) for n in nodes if n.tag == "label" and n.attrs.get("for")}
    out = []
    for c in _walk(dialogs[0]):
        if c.tag not in ("input", "select", "textarea"):
            continue
        name = labels.get(c.attrs.get("id")) or c.attrs.get("aria-label") or ""
        if c.tag == "select":
            kind = "select of " + str(sum(1 for o in _walk(c) if o.tag == "option"))
        elif c.attrs.get("role") == "switch":
            kind = "switch"
        elif c.attrs.get("aria-autocomplete") not in (None, "none"):
            kind = "autocomplete"
        else:
            kind = "text"
        out.append((c.tag, name, kind))
    return out


def test_the_fixture_is_the_pinned_build():
    text = LIVE7_EDITOR.read_text(encoding="ascii")
    assert hashlib.sha256(text.encode("ascii")).hexdigest() == LIVE7_EDITOR_SHA256


def test_session_7s_dialog_draws_exactly_these_eleven_controls():
    """The C1 reading, held on the tracked copy: every control by its name and
    kind. No postal code and no location display choice is among them (P A14,
    P A15); "Organization" is (P A22)."""
    assert _dialog_controls(LIVE7_EDITOR.read_text(encoding="ascii")) == [
        ("input", "", "text"),
        ("input", "", "text"),
        ("input", "Additional name", "text"),
        ("select", "Pronouns", "select of 5"),
        ("input", "Country/Region", "autocomplete"),
        ("input", "City", "autocomplete"),
        ("select", "Organization", "select of 2"),
        ("select", "Education", "select of 2"),
        ("input", "Industry", "autocomplete"),
        ("input", "Tap to toggle setting", "switch"),
        ("input", "Tap to toggle setting", "switch"),
    ]


def test_session_4s_dialog_draws_no_organization_select():
    """The other side of the control: two weeks earlier the dialog had none."""
    names = [name for _tag, name, _kind in _dialog_controls(LIVE4_EDITOR.read_text(encoding="ascii"))]
    assert FIELD not in names


# ---------------------------------------------------------------------------
# The world, and the real calls
# ---------------------------------------------------------------------------


def _select_id(html: str) -> str:
    """The dom id the label reading exactly ``Organization`` names."""
    found = re.findall(r'<label\b[^>]*\bfor="([^"]+)"[^>]*>\s*<div[^>]*>\s*' + FIELD + r"\s*</div>", html)
    assert len(found) == 1, found
    return found[0]


class _Live7World:
    """The tracked copy of session 7's editor, its Organization select
    rendering what LinkedIn has STORED. Save -- the only thing that stores --
    persists the select's chosen TEXT and closes the dialog; ``goto`` collects a
    save on the page it is leaving before rendering the next, so a dialog
    nobody saved is discarded, as on the site."""

    def __init__(self, *, fixture: pathlib.Path = LIVE7_EDITOR, organization: str = ORIGINAL):
        self.fixture = fixture
        self.store = {FIELD: organization}
        self.gotos: list[str] = []
        self.saves = 0
        self.routed = False

    def editor_html(self) -> str:
        html = self.fixture.read_text(encoding="ascii")
        if self.fixture == LIVE7_EDITOR:
            sid = _select_id(html)
            start = html.index('id="' + sid + '"', html.index("<select"))
            start = html.rindex("<select", 0, start)
            end = html.index("</select>", start) + len("</select>")
            block = html[start:end]
            stored = self.store[FIELD]
            chosen = re.sub(
                r"(<option\b[^>]*)>(\s*" + re.escape(stored) + r"\s*</option>)",
                lambda m: m.group(1) + " selected>" + m.group(2), block, count=1,
            )
            assert chosen != block, "the stored choice is not an option of the select"
            html = html[:start] + chosen + _NOTIFY_OFF + html[end:]
            listener = (
                "<script>document.addEventListener('click', function (e) {"
                " var b = e.target && e.target.closest ? e.target.closest('button') : null;"
                " if (!b || (b.textContent || '').trim() !== 'Save') { return; }"
                " var s = document.getElementById('" + sid + "');"
                " window.__saved = JSON.stringify({'" + FIELD + "': s.options[s.selectedIndex].text.trim()});"
                " var d = b.closest('dialog'); if (d) { d.remove(); } }, true);</script>"
            )
        else:
            # Session 4's editor: no Organization select to render or save.
            html = html.replace("</dialog>", _NOTIFY_OFF + "</dialog>", 1)
            listener = ""
        assert html.count("</body>") == 1
        return html.replace("</body>", listener + "</body>", 1)

    async def goto(self, page, url: str) -> str:
        try:
            saved = await page.evaluate(
                "() => { const s = window.__saved; delete window.__saved; "
                "return (typeof s === 'string') ? s : null; }"
            )
        except Exception:  # noqa: BLE001 - a fresh page holds nothing
            saved = None
        if saved:
            self.store.update(json.loads(saved))
            self.saves += 1
        if not self.routed:
            # The skeleton still names its images and stylesheet by address
            # (each an https://x/ placeholder): the page aborts them all.
            await _fetch_nothing(page)
            self.routed = True
        self.gotos.append(url)
        if url == writes.PROFILE_URL:
            html, landed = _PROFILE_HTML, _LANDED_PROFILE
        elif url == _EDITOR_URL:
            html, landed = self.editor_html(), _LANDED_EDITOR
        else:
            raise AssertionError("the write asked for " + repr(url) + ", which this world does not serve")
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return landed


async def _preview(page, world, value: str) -> dict:
    return await preview(_SPEC, target={"field": FIELD, "value": value}, navigator=world, page=page)


async def _write(page, world, value: str) -> dict:
    """preview (mints), consume (redeems), perform -- then the navigation a
    following tool call would make, which persists a save that happened."""
    target = {"field": FIELD, "value": value}
    block = await _preview(page, world, value)
    grant = consume(block["to_confirm"], action=_ACTION, target=target)
    receipt = await writes.perform(world, page, grant)
    await world.goto(page, writes.PROFILE_URL)
    return receipt


def _put_it_back(receipt: dict) -> tuple[str, str]:
    """``to_put_it_back`` parsed: the (field, value) of the exact call."""
    call = receipt["restore"]["to_put_it_back"].partition("#")[0]
    node = ast.parse(call.strip(), mode="eval").body
    assert isinstance(node, ast.Call) and node.func.id == "linkedin_update_profile_field"
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords}
    return kwargs["field"], kwargs["value"]


async def test_the_preview_names_the_resolved_target(writes_on, browser_page):
    world = _Live7World()
    block = await _preview(browser_page, world, UNSET)
    assert block["where"]["field"] == FIELD
    assert block["where"]["value"] == UNSET
    assert block["where"]["target"] == FIELD + writes.TARGET_JOIN + UNSET
    assert world.saves == 0, "a preview stored something"


async def test_the_write_chooses_the_unset_option_and_saves_it(writes_on, browser_page):
    world = _Live7World()
    receipt = await _write(browser_page, world, UNSET)
    assert receipt["performed"] is True, json.dumps(
        {k: receipt.get(k) for k in ("verification", "field_press", "editor_save_gate", "restore")}, default=str
    )
    assert world.store[FIELD] == UNSET
    assert world.saves == 1


async def test_its_inverse_puts_the_exact_original_back(writes_on, browser_page):
    """The round trip, over the real-capture skeleton: the receipt names the
    call that restores, and that call restores exactly."""
    world = _Live7World()
    first = await _write(browser_page, world, UNSET)
    assert first["performed"] is True, first.get("verification")
    field, value = _put_it_back(first)
    assert (field, value) == (FIELD, ORIGINAL)
    second = await _write(browser_page, world, value)
    assert second["performed"] is True, second.get("verification")
    assert world.store[FIELD] == ORIGINAL
    assert world.saves == 2


async def test_red_session_4s_editor_refuses_the_same_write(writes_on, browser_page):
    """THE CONTROL: where the select is not drawn, the same write stores
    nothing -- so the passes above are the control's presence."""
    world = _Live7World(fixture=LIVE4_EDITOR)
    block = await _preview(browser_page, world, UNSET)
    grant = consume(block["to_confirm"], action=_ACTION, target={"field": FIELD, "value": UNSET})
    with pytest.raises(WriteAttemptError, match="0 controls in this editor are named 'Organization'"):
        await writes.perform(world, browser_page, grant)
    await world.goto(browser_page, writes.PROFILE_URL)
    assert world.saves == 0
