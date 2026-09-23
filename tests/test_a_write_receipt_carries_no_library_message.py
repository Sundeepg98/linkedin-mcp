"""A write's RECEIPT may say that a step failed, and never what a library said.

``writes.perform`` runs the only clicks this package makes, and its receipt is
what the operator reads after an act that may not be undoable. Until the lane G
follow-up of 2026-09-24 two of its lines rendered an exception's TEXT into that
receipt:

* ``click_error``, from anything raised inside the fill-and-click loop. That
  loop presses selectors this package composed -- and the typeahead's carries
  HIS NEEDLE, the name of the person he is messaging. A Playwright timeout
  quotes the selector it was waiting on.
* ``verified_why``, from a verification read that raised. That read navigates,
  and a refusal at the read boundary interpolates the address it refused.

Both now carry the exception's TYPE and a sentence this package composed --
the ruling ``ERROR-MESSAGE-RULED-AT-THE-RAISE`` decides a field where the value
enters it, and a field is not the ``$.message`` channel that ruling leaves to
library text.

WHY A DRIVEN TEST AND A STRUCTURAL ONE. ``tests/test_readers_emit_no_page_string.py``
drives every page READER against a page whose reads all fail, and it cannot
reach ``perform``: the process-wide writes door stands in front of it. So the
two failures are injected here through the follow-a-Page harness, end to end on
a local headless page, and a structural pin holds the rest of ``writes.py``,
which no driven test reaches -- any exception text written anywhere but a
``raise`` is a red, whoever adds it.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

from linkedin_server import writes
from linkedin_server.writes import consume, preview
from tests.test_follow_company_page import (
    _ACTION,
    _SPEC,
    COMPANY_PAGE_FOLLOW_ID,
    COMPANY_PAGE_FOLLOW_MARKUP,
    _navigator,
)
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

WRITES_SOURCE = Path(writes.__file__)

#: What every injected failure says. Not name-shaped, and not anything the
#: harness itself supplies, so finding it can only mean the message leaked.
LIBRARY_SAID = "example-library-quoted-the-selector"


async def _granted(page):
    nav = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    block = await preview(
        _SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=page
    )
    return consume(block["to_confirm"], action=_ACTION, target=COMPANY_PAGE_FOLLOW_ID)


async def test_a_failed_click_is_reported_by_type(writes_on, browser_page, monkeypatch):
    """The click raises quoting its selector; the receipt names only the type."""
    grant = await _granted(browser_page)

    async def failing_click(selector, **kwargs):
        raise TimeoutError(f"Timeout waiting for {selector} ({LIBRARY_SAID})")

    monkeypatch.setattr(browser_page, "click", failing_click)
    receipt = await writes.perform(
        _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID),
        browser_page,
        grant,
    )

    assert receipt["clicked"]["error"] == "TimeoutError", receipt["clicked"]
    assert LIBRARY_SAID not in json.dumps(receipt), receipt["clicked"]


async def test_a_failed_verification_is_reported_by_type(
    writes_on, browser_page, monkeypatch
):
    """The verification read raises quoting an address; the receipt says the
    read failed, names the type, and still says where to look."""
    grant = await _granted(browser_page)

    async def failing_verify(*args, **kwargs):
        raise RuntimeError(f"refused https://www.linkedin.com/in/{LIBRARY_SAID}/")

    monkeypatch.setattr(writes, "_verify_after", failing_verify)
    receipt = await writes.perform(
        _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID),
        browser_page,
        grant,
    )

    blob = json.dumps(receipt)
    assert LIBRARY_SAID not in blob, blob[:400]
    assert "RuntimeError" in blob
    assert "the verification read itself failed" in blob


def _exception_text_renders(source: str) -> list[tuple[int, str]]:
    """Every use of a caught exception's TEXT outside a ``raise`` statement.

    A use of the bound name is harmless only as ``type(exc)`` or
    ``isinstance(exc, ...)``, or inside a ``raise`` -- the ``$.message``
    channel, ruled at the raise and deliberately left alone here.
    """
    tree = ast.parse(source)
    parents = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }
    out: list[tuple[int, str]] = []
    for handler in ast.walk(tree):
        if not isinstance(handler, ast.ExceptHandler) or not handler.name:
            continue
        for statement in handler.body:
            for use in ast.walk(statement):
                if not (
                    isinstance(use, ast.Name)
                    and use.id == handler.name
                    and isinstance(use.ctx, ast.Load)
                ):
                    continue
                parent = parents.get(use)
                if (
                    isinstance(parent, ast.Call)
                    and isinstance(parent.func, ast.Name)
                    and parent.func.id in {"type", "isinstance"}
                ):
                    continue
                node = use
                while node in parents and not isinstance(node, ast.stmt):
                    node = parents[node]
                if isinstance(node, ast.Raise):
                    continue
                out.append((use.lineno, ast.unparse(node).splitlines()[0][:80]))
    return sorted(out)


def test_writes_renders_no_exception_text_outside_a_raise():
    """THE REST OF THE MODULE, which no driven test reaches."""
    found = _exception_text_renders(WRITES_SOURCE.read_text(encoding="utf-8"))
    assert found == [], (
        "writes.py writes an exception's TEXT somewhere other than a raise: "
        f"{found}. Write type(exc).__name__, or a reason this package composed. "
        "A library's message can quote a selector carrying his needle, or an "
        "address carrying his slug, and every string here can reach a receipt."
    )


def test_that_scan_can_fail():
    """SHOWN FAILING on synthetic source, and silent on the two forms it allows."""
    dirty = (
        "def f():\n"
        "    try:\n"
        "        g()\n"
        "    except Exception as exc:\n"
        "        why = f'{type(exc).__name__}: {exc}'\n"
    )
    clean = (
        "def f():\n"
        "    try:\n"
        "        g()\n"
        "    except Exception as exc:\n"
        "        why = type(exc).__name__\n"
        "        raise RuntimeError(f'could not: {exc}') from exc\n"
    )
    assert [line for line, _ in _exception_text_renders(dirty)] == [5]
    assert _exception_text_renders(clean) == []
