"""No reader or gate in ``writes.py`` may coerce a page value with ``int()``.

THE CLASS. ``int("<some words>")`` raises ``ValueError: invalid literal for
int() with base 10: '<some words>'`` -- it QUOTES the value it refused. Every
function below turns a page reading into a count with ``int(x or 0)``, so a
reading that came back as text carries that text out of the process inside an
exception, which is the leak class this repository has repaired one site at a
time since 2026-09-21 (``_audit/2026-09-21-the-ungrantable-readers.md``).
``coerce.as_count`` is the repair: it answers exactly what ``int`` answered on
every integer, and on anything else substitutes a LOGGED zero that names the
value's type and never the value.

THE COUNT, MEASURED AT THE LANE-L4 MERGE, 2026-09-23: 28 ``int()`` calls in 14
functions. The lane's own record had named ten functions -- the four submit and
send gates were missing from its list, and the scan below is how that was
found. By where the value comes from, which is the difference between a leak
and a latent one:

* PAGE-CONTROLLED -- the reading is ``page.evaluate`` output, so the page's own
  script decides the value: ``_read_item_comment_box`` and
  ``_comment_submit_gate`` (``dom.read_comment_surface``), and
  ``_read_profile_invitations``, ``aim_invitation`` and
  ``_name_the_invitation_recipient`` (``dom.read_invitation_surface``).
* PLAYWRIGHT-TYPED -- ``locator.count()`` and friends, which a document cannot
  make answer with a string: the other nine. ``int()`` could not be handed text
  there TODAY; it is converted anyway, so the file carries ONE rule a test can
  hold, and a reader later rewritten onto ``page.evaluate`` does not silently
  re-open the leak.

TWO HALVES, BOTH SHOWN FAILING against the unrepaired module before the repair
landed: a STRUCTURAL scan that finds every ``int()`` call in ``writes.py``, and
a DRIVE of each of the fourteen functions over a reading whose counts are
planted words, asserting nothing raises and no ``why`` quotes them.

WHAT THIS DOES NOT COVER, said so its green is not read as more: a raw reading
value interpolated into a ``why`` without passing through ``int()`` at all.
The four sites that re-quoted the very field just coerced were repaired with
this file; the others are listed in ``_audit/2026-09-23-lane-l4-writes.md``
section 10.
"""
from __future__ import annotations

import ast
import pathlib
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import dom, writes  # noqa: E402
from tests.test_writes import _bare_grant  # noqa: E402

# NO MODULE-LEVEL UPPER-CASE CONSTANT BEYOND ``ROOT``, on the impact gate's
# rule: a test file that names an upper-case constant another staged file
# defines is coupled to it, and a generic name couples half the suite.

#: Words a page could draw where a count belongs. Not a name, not a number.
_planted = "Planted Page Words QX"

#: Functions allowed an ``int()`` call, with the reason. EMPTY BY DESIGN: an
#: entry here is a claim that the value cannot come off a page, and it has to
#: be written down to be made.
_int_allowed_in: dict[str, str] = {}


def _int_calls(source: str) -> list[tuple[int, str, str]]:
    """(line, enclosing function, call text) for every builtin ``int(...)``."""
    tree = ast.parse(source)
    spans = [(n.lineno, n.end_lineno or n.lineno, n.name) for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    found = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "int"):
            owners = [s for s in spans if s[0] <= node.lineno <= s[1]]
            owner = max(owners, key=lambda s: s[0])[2] if owners else "<module>"
            found.append((node.lineno, owner,
                          ast.get_source_segment(source, node) or "int(...)"))
    return sorted(found)


def _writes_source() -> str:
    return (ROOT / "linkedin_server" / "writes.py").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# THE STRUCTURAL HALF
# ---------------------------------------------------------------------------


def test_the_scan_finds_a_planted_int_call():
    """The scan is seen answering yes before its no is believed."""
    planted = (
        "def reader(reading):\n"
        "    return int(reading.get('count') or 0)\n"
    )
    assert _int_calls(planted) == [
        (2, "reader", "int(reading.get('count') or 0)")]


def test_writes_holds_no_int_call():
    found = [c for c in _int_calls(_writes_source())
             if c[1] not in _int_allowed_in]
    assert not found, (
        f"{len(found)} int() call(s) in writes.py; each can raise a ValueError "
        "that quotes the value it refused, and a reading's value is the page's "
        "choice. Use coerce.as_count (a count) or coerce.as_int (and refuse on "
        "None):\n" + "\n".join(f"  line {n} in {fn}: {text}"
                               for n, fn, text in found)
    )


# ---------------------------------------------------------------------------
# THE DRIVEN HALF -- every function over a reading whose counts are words
# ---------------------------------------------------------------------------


def _spec(action: str):
    return next(s for s in writes.SANCTIONED_WRITES.values()
                if s.action == action)


def _whys(result) -> list[str]:
    """Every human-facing sentence a result carries."""
    if isinstance(result, dict):
        return [str(result.get("why") or "")]
    if isinstance(result, tuple):
        return [part for part in result if isinstance(part, str)]
    return []


def _cases():
    grant = _bare_grant(action="send_message",
                        target="Needle Q" + writes.TARGET_JOIN + "a body")
    observation = types.SimpleNamespace(target="Needle Q",
                                        facts={"controls": _planted})
    return [
        ("_read_follow_state", "read_follow_control",
         {"label": "Follow", "count": _planted},
         lambda: writes._read_follow_state(None)),
        ("_read_apply_route", "read_apply_control",
         {"label": "Easy Apply", "href": None, "count": _planted,
          "link_target": None},
         lambda: writes._read_apply_route(None, "4000000001")),
        ("_read_feed_composer", "read_composer_surface",
         {"composer_controls": _planted, "editors": _planted,
          "article_routes": 0, "sharebox_routes": 0},
         lambda: writes._read_feed_composer(None, _spec("publish_post"))),
        ("_read_item_permalink", "read_reaction_surface",
         {"controls": _planted, "off_state": _planted, "labels": []},
         lambda: writes._read_item_permalink(None, _spec("react_to_item"))),
        ("_read_item_comment_box", "read_comment_surface",
         {"editors": _planted, "names": {dom.COMMENT_CONTROL_NAME: _planted},
          "controls_read": _planted, "unnamed": _planted, "menus": _planted,
          "error": None},
         lambda: writes._read_item_comment_box(None, _spec("comment_on_item"))),
        ("_read_profile_editors", "read_profile_editor_surface",
         {"editors": {"intro": _planted}, "forms": 0},
         lambda: writes._read_profile_editors(None,
                                              _spec("update_profile_field"))),
        ("_read_profile_invitations", "read_invitation_surface",
         {"controls": _planted, "matches": _planted, "index": _planted},
         lambda: writes._read_profile_invitations(
             None, _spec("send_invitation"), target="Needle Q")),
        ("_read_messaging_badge", "read_messaging_badge",
         {"links": _planted, "label": None},
         lambda: writes._read_messaging_badge(None, _spec("send_message"))),
        ("_name_the_invitation_recipient", "read_invitation_surface",
         {"controls": _planted, "matches": _planted, "label": None},
         lambda: writes._name_the_invitation_recipient(
             None, _spec("send_invitation"), observation, {})),
        ("_comment_submit_gate", "read_comment_surface",
         {"editors": _planted, "names": {}, "menu_items": _planted,
          "controls_read": 0, "menus": 0, "error": None},
         lambda: writes._comment_submit_gate(None, {})),
        ("_publish_submit_gate", "read_post_composer",
         {"editors": _planted, "submits": _planted, "error": None},
         lambda: writes._publish_submit_gate(None)),
        ("_typeahead_gate", "read_typeahead_options",
         {"total": _planted, "matches": _planted, "error": None},
         lambda: writes._typeahead_gate(None, grant)),
        ("_send_gate", "read_compose_send_state",
         {"textboxes": _planted, "controls": _planted, "error": None},
         lambda: writes._send_gate(None)),
    ]


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c[0])
async def test_a_count_that_is_words_is_never_quoted(case, monkeypatch):
    name, reader, reading, call = case

    async def planted_reader(*_args, **_kwargs):
        return dict(reading)

    monkeypatch.setattr(dom, reader, planted_reader)
    try:
        result = await call()
    except Exception as exc:  # noqa: BLE001 -- the assertion is the point
        assert _planted not in str(exc), (
            f"{name} raised {type(exc).__name__} quoting the planted page "
            f"words: {exc}")
        raise
    for why in _whys(result):
        assert _planted not in why, f"{name}'s why quotes the page: {why!r}"


@pytest.mark.parametrize("reading", [
    {"controls": _planted, "matches": None},
    {"controls": 3, "matches": _planted},
    {"controls": 3, "matches": 1, "index": _planted},
], ids=["controls", "matches", "index"])
def test_aim_invitation_refuses_a_count_that_is_words(reading):
    """The pure aim, driven directly: a malformed count or position REFUSES --
    no aim is returned -- and the refusal quotes nothing it was handed."""
    state, why, aim = writes.aim_invitation(dict(reading))
    assert aim is None, f"a malformed reading produced an aim: {state}"
    assert _planted not in why, why
