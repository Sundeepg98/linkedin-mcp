"""No log record in this package carries a caught exception's TEXT. Its type, yes.

A LOG RECORD IS ANOTHER WAY OUT OF THE PROCESS -- this package says so already
(``test_as_count_logs_the_type_and_never_the_value``). Until the lane G
follow-up of 2026-09-24, 45 logging calls rendered a caught exception's message,
and a library's message can quote a selector carrying his needle, a request, an
address carrying his slug, or an absolute path under his user directory.

WHERE THESE RECORDS LAND, MEASURED BEFORE DECIDING (2026-09-24):

* The ``linkedin`` logger has ONE handler, a ``StreamHandler`` -- stderr -- with
  ``propagate = False``, at the level ``LINKEDIN_LOG_LEVEL`` names, default INFO
  (``linkedin_server/config.py``).
* ``LINKEDIN_LOG_LEVEL`` was unset in the process, user and machine scopes, is
  set by no launcher, and the MCP registration carries no env block.
* The server is registered as an HTTP endpoint and started by
  ``scripts/start_server.ps1``, which redirects stderr to
  ``_state/http-server.err.log`` -- gitignored, and ON DISK. That file held 5
  lines, all INFO lifecycle lines; none came from these sites.
* So at the default level the 41 DEBUG sites landed nowhere, and the 4 others --
  two INFO in ``auth.py``, two WARNING in ``profile_lock.py`` -- land in that file
  whenever they fire. At ``LINKEDIN_LOG_LEVEL=DEBUG``, the setting one reaches for
  when diagnosing, all 45 would.

WHY TYPE-ONLY AND NOT REDACTED. ``config.scrub`` substitutes this server's own
paths and nothing else, and the page-text rule records, as a finding, that this
package has no instrument that can decide whether a string is a person's name
(``tests/test_page_text_is_never_printed.py``, ``TEXT_SANITISERS``). A redacted
log would promise what nothing here can check. The type names the failure's
class; the call site's own words say which read it was.

Held two ways: this structural pin over every module, and a driven check in
``tests/test_readers_emit_no_page_string.py`` that runs every reader against a
page whose reads all fail, with the logger captured at DEBUG.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "linkedin_server"

_LEVELS = frozenset(
    {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}
)


def log_renders(source: str) -> list[tuple[int, str]]:
    """Every logging call that passes a caught exception's TEXT.

    A use of the bound name is harmless only as ``type(e)`` or
    ``isinstance(e, ...)``. ``logger.exception`` would log the traceback, which
    quotes the message, so it counts wherever it appears inside a handler.
    """
    tree = ast.parse(source)
    parents = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }
    out: set[tuple[int, str]] = set()
    for handler in ast.walk(tree):
        if not isinstance(handler, ast.ExceptHandler):
            continue
        for statement in handler.body:
            for call in ast.walk(statement):
                if not (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and call.func.attr in _LEVELS
                ):
                    continue
                if call.func.attr == "exception":
                    out.add((call.lineno, "exception"))
                    continue
                if not handler.name:
                    continue
                for argument in list(call.args) + [k.value for k in call.keywords]:
                    for use in ast.walk(argument):
                        if not (isinstance(use, ast.Name) and use.id == handler.name):
                            continue
                        parent = parents.get(use)
                        if (
                            isinstance(parent, ast.Call)
                            and isinstance(parent.func, ast.Name)
                            and parent.func.id in {"type", "isinstance"}
                        ):
                            continue
                        out.add((call.lineno, call.func.attr))
    return sorted(out)


def test_no_logging_call_renders_a_caught_exception():
    found = {
        path.name: log_renders(path.read_text(encoding="utf-8"))
        for path in sorted(PACKAGE.glob("*.py"))
    }
    found = {name: sites for name, sites in found.items() if sites}
    assert found == {}, (
        "these logging calls pass a caught exception's TEXT, which can quote a "
        "selector, a request, an address or a path: "
        f"{found}. Log type(exc).__name__ and say, in the call's own words, "
        "which step failed."
    )


def test_the_scan_reads_every_module():
    """A scan over nothing passes everything."""
    assert len(list(PACKAGE.glob("*.py"))) > 40


def test_that_scan_can_fail():
    """SHOWN FAILING on synthetic source, and silent on the type-only form."""
    dirty = (
        "def f():\n"
        "    try:\n"
        "        g()\n"
        "    except Exception as exc:\n"
        "        logger.debug('read failed: %s: %s', type(exc).__name__, exc)\n"
        "    try:\n"
        "        g()\n"
        "    except OSError as e:\n"
        "        logger.warning('could not read %s: %s', PATH, e)\n"
        "    try:\n"
        "        g()\n"
        "    except Exception:\n"
        "        logger.exception('boom')\n"
    )
    clean = (
        "def f():\n"
        "    try:\n"
        "        g()\n"
        "    except Exception as exc:\n"
        "        logger.debug('read failed: %s', type(exc).__name__)\n"
    )
    assert [line for line, _ in log_renders(dirty)] == [5, 9, 13]
    assert log_renders(clean) == []
