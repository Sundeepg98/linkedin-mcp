"""Are the 12 ``url=_url_of(page)`` raise sites in dom.py REACHABLE, and does
``server._error`` publish that url?

WHAT IS ALREADY KNOWN (measured by the lead, not re-measured here): given an
``ExtractionFailedError`` whose ``url`` carries a name, ``server._error``
copies it into ``out["url"]`` unscrubbed. WHAT THIS MEASURES is the other
half -- whether a caller can actually drive each of the twelve dom.py readers
to its own ``raise``.

## HOW EACH SITE IS SHAPED, AND WHY THIS IS NOT A THIRD PAGE DOUBLE

All twelve sites have one shape::

    try:
        data = await page.evaluate(<ONE MODULE-LEVEL SCRIPT CONSTANT>, cfg)
    except Exception as exc:
        raise ExtractionFailedError(..., url=_url_of(page)) from exc

so the raise is reachable exactly when ``page.evaluate`` raises for THAT
script, and by no other route. The double is therefore
``tests.plantedpage.PlantedPage`` -- the repository's registered page double,
whose key vocabulary is harvested from the package source -- SUBCLASSED to do
two things and nothing else:

* answer ``url`` with a synthetic name-bearing authwall landing;
* raise for ONE script object, chosen by identity against the ``dom`` module
  constant, and defer to the shipped ``PlantedPage.evaluate`` for every other.

The per-script selectivity is not decoration. ``read_job_insight_panels``
opens by awaiting ``read_profile_fields(page)``, which owns raise site #3; a
double that raised for every script would send it out through THAT site and
this probe would record the wrong line as reached. Selectivity is what lets
each site be attributed to its own function.

The call arguments come from ``tests.test_readers_emit_no_page_string`` --
``_build_call``, which already knows this package's parameter shapes, puts
keyword-only parameters in kwargs, and produces the second
every-optional-supplied variant. Reusing it is the point: a hand-built call is
a list of the parameters its author remembered.

## THE THREE VERDICTS, AND WHICH FRAME PROVES WHICH

``reached``      an ``ExtractionFailedError`` came out AND the deepest dom.py
                 traceback frame is the target function at its expected line.
``wrong_site``   an ``ExtractionFailedError`` came out through a DIFFERENT
                 function or line. Never a pass for the target.
``not_driven``   no ``ExtractionFailedError``, or the harness refused to build
                 a call. Never a pass.

A site is only ``reached`` if the traceback says so. "The right exception type
came out" is not the measurement -- three of these readers can raise the same
class from a neighbour's site.

## THE TWO NEEDLES, AND WHY THERE ARE TWO

``URL_NEEDLE``   sits only in the page's ``url``. Finding it in ``out["url"]``
                 can only have travelled ``_url_of(page)`` -> ``exc.url`` ->
                 ``_error``.
``INNER_NEEDLE`` sits only in the message of the exception ``evaluate``
                 raises. It measures the SECOND channel: every one of these
                 twelve messages is built ``f"...: {type(exc).__name__}: {exc}"``,
                 so whatever the browser put in its exception is interpolated
                 into ``out["message"]``.

Two distinct values, so a hit in either field names its own path. One needle
could not tell the two channels apart.

Both are synthetic, carry the sanctioned token ``example``
(``tests.test_no_committed_identity.SYNTHETIC_SLUG_TOKENS``), and are past
``leakwalk.MIN_SECRET`` so the shipped walker will hunt them rather than
refuse them.

## THE CONTROLS

A check that cannot fail certifies nothing, so this runs three:

* NEGATIVE, per reader -- the same call with a double that raises for NO
  script. If the reader still raises ``ExtractionFailedError``, the raise was
  not caused by this probe's shaping and the ``reached`` verdict above is
  unattributed.
* POSITIVE and NEGATIVE on the hunt itself -- the walker must find a needle
  planted in a dict and must not find one in a needle-free dict.
* The reader -> script mapping is READ OFF dom.py's AST rather than typed
  out, and a disagreement with the table below is reported, not silently
  overridden.

Offline. Opens no browser, writes nothing into the repository.
"""

from __future__ import annotations

import ast
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

#: THE REPO ROOT IS DERIVED, NEVER SPELLED. An absolute workspace path in
#: a tracked file publishes this machine's layout, and the hard-coded one
#: this probe was written with would have named a worktree that will not
#: exist tomorrow. It is also NOT `REPO / "venv" / ...` anywhere: that
#: directory is gitignored and absent in every worktree, and resolving an
#: interpreter through it has been repaired four times in two days.
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from linkedin_server import dom, server  # noqa: E402
from linkedin_server.errors import ExtractionFailedError  # noqa: E402
from tests import plantedpage  # noqa: E402
from tests.leakwalk import walk  # noqa: E402
from tests.test_readers_emit_no_page_string import _build_call  # noqa: E402

# ---------------------------------------------------------------------------
# The needles
# ---------------------------------------------------------------------------

#: The synthetic member slug the landing carries. Token ``example`` is
#: sanctioned by tests/test_no_committed_identity.SYNTHETIC_SLUG_TOKENS.
URL_NEEDLE = "example-person-placeholder"

#: A name-bearing authwall landing. ``/authwall`` is one of
#: ``config.AUTHWALL_MARKERS``, and the redirect target carries the slug --
#: which is the whole shape of the hazard: LinkedIn bounces a signed-out read
#: to an address that quotes who was being read.
PLANT_URL = (
    "https://www.linkedin.com/authwall?sessionRedirect="
    "https%3A%2F%2Fwww.linkedin.com%2Fin%2F" + URL_NEEDLE
)

#: What the browser's own exception says. Distinct from URL_NEEDLE so a hit
#: names which of the two channels carried it.
INNER_NEEDLE = "example-inner-marker-string"

# ---------------------------------------------------------------------------
# The twelve sites
# ---------------------------------------------------------------------------

#: ``(reader, script constant, line of the ``raise``)`` at commit a29c281.
TARGETS: tuple[tuple[str, str, int], ...] = (
    ("harvest_linked_cards", "HARVEST_LINKED_CARDS_JS", 574),
    ("harvest_block_cards", "HARVEST_BLOCK_CARDS_JS", 780),
    ("read_profile_fields", "READ_PROFILE_JS", 803),
    ("read_surface_census", "CENSUS_JS", 3311),
    ("read_self_owned_editor_fields", "EDITOR_FIELDS_JS", 3907),
    ("read_self_owned_editor_values", "EDITOR_VALUES_JS", 4356),
    ("read_own_activity_items", "ACTIVITY_ITEMS_JS", 5112),
    ("read_compose_modes", "COMPOSE_MODES_JS", 5899),
    ("read_selected_recipients", "SELECTED_RECIPIENT_JS", 6248),
    ("read_job_insight_panels", "JOB_INSIGHT_MARKERS_JS", 8377),
    ("read_profile_views_insights", "PROFILE_VIEWS_INSIGHTS_JS", 8720),
    ("read_search_appearances", "SEARCH_APPEARANCES_JS", 9356),
)

#: A multi-line ``raise`` reports its statement's first line, but which line
#: of a statement a traceback names has moved between interpreter releases.
#: A window rather than equality, with the measured value always reported.
LINE_WINDOW = 8


# ---------------------------------------------------------------------------
# The double
# ---------------------------------------------------------------------------


class EvaluateRaises(plantedpage.PlantedPage):
    """The shipped double, landed on the plant, refusing ONE script.

    ``target`` is the script OBJECT, compared by identity. A substring match
    on the script text would be the loose version of this and would fire on
    whichever of two scripts happened to share a helper.
    """

    url = PLANT_URL

    def __init__(self, target: Any) -> None:
        super().__init__()
        self._target = target

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> Any:
        if self._target is not None and script is self._target:
            raise RuntimeError(INNER_NEEDLE)
        return await super().evaluate(script, arg, **kwargs)


def _with_page(value: Any, page: Any) -> Any:
    """Swap the harness's plain double for the shaped one, in place."""
    return page if isinstance(value, plantedpage.PlantedPage) else value


# ---------------------------------------------------------------------------
# Driving
# ---------------------------------------------------------------------------


def _deepest_dom_frame(exc: BaseException) -> tuple[str, int]:
    """``(function, line)`` of the LAST dom.py frame in the traceback."""
    found = ("", 0)
    tb = exc.__traceback__
    while tb is not None:
        code = tb.tb_frame.f_code
        if code.co_filename.replace("\\", "/").endswith("linkedin_server/dom.py"):
            found = (code.co_name, tb.tb_lineno)
        tb = tb.tb_next
    return found


def _hits(obj: Any, needle: str) -> list[str]:
    """Every path in ``obj`` whose text carries ``needle``, via the shipped walker."""
    return [path for path, text in walk(obj) if needle in text]


def _drive(fn: Any, target: Any) -> dict[str, Any]:
    """One reader, every call variant, against a double refusing ``target``."""
    variants, refusal = _build_call(fn)
    if variants is None:
        return {"outcome": "not_driven", "why": f"harness refused a call: {refusal}"}

    attempts: list[dict[str, Any]] = []
    for index, (args, kwargs) in enumerate(variants):
        page = EvaluateRaises(target)
        call_args = [_with_page(a, page) for a in args]
        call_kwargs = {k: _with_page(v, page) for k, v in kwargs.items()}
        attempts.append(_drive_once(fn, call_args, call_kwargs, index))

    for attempt in attempts:
        if attempt["outcome"] == "raised":
            return attempt
    return {
        "outcome": "not_driven",
        "why": "; ".join(sorted({a.get("why", "") for a in attempts if a.get("why")})),
        "variants": len(variants),
    }


def _drive_once(
    fn: Any, args: list[Any], kwargs: dict[str, Any], index: int
) -> dict[str, Any]:
    async def _run() -> Any:
        return await asyncio.wait_for(fn(*args, **kwargs), timeout=10.0)

    try:
        result = asyncio.run(_run())
    except ExtractionFailedError as exc:
        name, line = _deepest_dom_frame(exc)
        envelope = server._error(exc)
        return {
            "outcome": "raised",
            "variant": index,
            "frame": name,
            "line": line,
            "exc_url": getattr(exc, "url", ""),
            "exc_hint": getattr(exc, "hint", ""),
            "envelope_keys": sorted(envelope),
            "envelope_url": envelope.get("url", ""),
            "url_needle_at": _hits(envelope, URL_NEEDLE),
            "inner_needle_at": _hits(envelope, INNER_NEEDLE),
        }
    except BaseException as exc:  # noqa: BLE001 - every other end is not_driven
        return {
            "outcome": "other",
            "variant": index,
            "why": f"{type(exc).__name__}: {str(exc)[:160]}",
        }
    return {
        "outcome": "returned",
        "variant": index,
        "why": f"returned {type(result).__name__} without raising",
    }


# ---------------------------------------------------------------------------
# The AST cross-check: which script does each reader actually evaluate?
# ---------------------------------------------------------------------------


def _scripts_evaluated() -> dict[str, list[str]]:
    """Per function, the NAMES passed first to ``*.evaluate(...)``.

    Read off the source so the table above is checked rather than trusted.
    """
    tree = ast.parse(
        (REPO / "linkedin_server" / "dom.py").read_text(encoding="utf-8")
    )
    out: dict[str, list[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        names: list[str] = []
        for inner in ast.walk(node):
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr == "evaluate"
                and inner.args
                and isinstance(inner.args[0], ast.Name)
            ):
                names.append(inner.args[0].id)
        if names:
            out[node.name] = names
    return out


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------


def _hunt_controls() -> dict[str, Any]:
    """The walker must find a planted needle and must not find an absent one."""
    return {
        "positive_url": bool(_hits({"url": PLANT_URL}, URL_NEEDLE)),
        "positive_inner": bool(_hits({"message": INNER_NEEDLE}, INNER_NEEDLE)),
        "negative": _hits({"url": "https://www.linkedin.com/feed/"}, URL_NEEDLE),
    }


# ---------------------------------------------------------------------------
# The other two questions, answered by PARSING rather than by grepping
# ---------------------------------------------------------------------------
#
# "Does any of these raises carry a url that is not ``_url_of(page)``?" and
# "does any carry a page-derived ``hint``?" are questions about EXPRESSIONS,
# and a line-oriented search answers them plausibly and wrongly -- a keyword
# split across lines, or one inside a docstring, reads the same to grep. So
# the argument expressions are unparsed from the AST and reported verbatim.


def _argument_census(module: str, callee: str) -> list[dict[str, Any]]:
    """Every call to ``callee`` in ``module``, with its ``url``/``hint`` source."""
    path = REPO / "linkedin_server" / f"{module}.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    owner: dict[int, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            for inner in ast.walk(node):
                owner.setdefault(id(inner), node.name)

    out: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name != callee:
            continue
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        out.append(
            {
                "module": module,
                "enclosing": owner.get(id(node), "<module>"),
                "line": node.lineno,
                "url_expr": (
                    ast.unparse(kwargs["url"]) if "url" in kwargs else None
                ),
                "hint_expr": (
                    ast.unparse(kwargs["hint"]) if "hint" in kwargs else None
                ),
            }
        )
    return sorted(out, key=lambda row: row["line"])


def _hint_reaches_the_envelope() -> dict[str, Any]:
    """Does a page-derived ``hint`` survive ``_error``? Driven, not read.

    ``_error`` runs ``scrub`` over the hint, and ``scrub`` substitutes this
    server's own filesystem paths. Whether that leaves heading text intact is
    a fact about ``scrub``, so it is measured by running it rather than by
    reasoning about what it is for.
    """
    shaped = ExtractionFailedError(
        "a synthetic failure",
        url=PLANT_URL,
        hint=f"headings seen: ['{INNER_NEEDLE}']",
    )
    envelope = server._error(shaped)
    return {
        "envelope_keys": sorted(envelope),
        "hint_needle_at": _hits({"hint": envelope.get("hint", "")}, INNER_NEEDLE),
        "hint_out": envelope.get("hint", ""),
    }


def main() -> int:
    evaluated = _scripts_evaluated()
    rows: list[dict[str, Any]] = []

    for reader, script_name, line in TARGETS:
        fn = getattr(dom, reader, None)
        script = getattr(dom, script_name, None)
        row: dict[str, Any] = {
            "reader": reader,
            "script": script_name,
            "expected_line": line,
            "ast_scripts": evaluated.get(reader, []),
            "ast_agrees": script_name in evaluated.get(reader, []),
        }
        if fn is None or script is None:
            row["outcome"] = "not_driven"
            row["why"] = f"dom has no {reader!r} / {script_name!r}"
            rows.append(row)
            continue

        row.update(_drive(fn, script))

        # NEGATIVE CONTROL: the same call with a double that refuses nothing.
        control = _drive(fn, None)
        row["control_outcome"] = control["outcome"]
        row["control_why"] = control.get("why", "")
        row["control_frame"] = control.get("frame", "")
        row["control_line"] = control.get("line", 0)

        if row["outcome"] == "raised":
            same = row.get("frame") == reader
            near = abs(int(row.get("line") or 0) - line) <= LINE_WINDOW
            row["verdict"] = "reached" if (same and near) else "wrong_site"
        else:
            row["verdict"] = "not_driven"
        rows.append(row)

    # THE SECOND ROUTE OUT OF ONE READER, MEASURED RATHER THAN ASSERTED.
    # ``read_job_insight_panels`` opens by awaiting ``read_profile_fields``, so
    # a caller of the job reader can receive an envelope raised at a DIFFERENT
    # site carrying the same url. This is what the per-script selectivity above
    # exists to separate, and a claim about it is worth exactly as much as the
    # traceback that backs it.
    transitive = _drive(dom.read_job_insight_panels, dom.READ_PROFILE_JS)

    raises = _argument_census("dom", "ExtractionFailedError") + _argument_census(
        "server", "ExtractionFailedError"
    )
    payload = {
        "commit": "a29c281",
        "url_needle": URL_NEEDLE,
        "inner_needle": INNER_NEEDLE,
        "plant_url": PLANT_URL,
        "hunt_controls": _hunt_controls(),
        "rows": rows,
        "raises_carrying_url": [r for r in raises if r["url_expr"] is not None],
        "raises_carrying_hint": [r for r in raises if r["hint_expr"] is not None],
        "require_rows_calls": _argument_census("dom", "require_rows")
        + _argument_census("server", "require_rows"),
        "hint_through_error": _hint_reaches_the_envelope(),
        "job_panels_via_read_profile_fields": transitive,
    }
    print(json.dumps(payload, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
