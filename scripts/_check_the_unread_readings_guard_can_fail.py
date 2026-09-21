"""Show every check in `tests/test_the_unread_readings_were_never_driven.py` failing.

A check that cannot fail certifies nothing, and this package has shipped one of
those. So before that file counts as evidence about what `hrefs_error`,
`pill_label` and `census_shape` carry, each of its assertions is handed a
defect and shown convicting it.

## THE MUTATIONS ARE ON THE DEFECT LINE, NOT ON THE FUNCTION

Replacing a whole function with a fake proves the test can tell that function
from a different one. It does not prove the test can tell the SHIPPED function
from the one-token variant somebody will actually write. So each mutation below
edits ONE line of `linkedin_server/dom.py` or `linkedin_server/shape.py` in a
re-executed copy of the module, and several of them are the exact variant the
source's own comments say was deliberately avoided:

* `marker = type(exc).__name__` becomes `f"{type(exc).__name__}: {exc}"` --
  the formula the SIBLING field six lines up uses, which the comment between
  them calls *"a deliberate difference"*. That is the hazard, spelled the way
  it would really arrive.
* `"url_before": shape.redact_thread_id(before)` loses its redactor, which is
  the defect that actually shipped and put a real conversation identifier into
  a transcript on 2026-09-03.

## A MUTATION THAT DOES NOT APPLY IS A LOUD FAILURE

Every replacement asserts its target appears an EXACT number of times before
substituting. Zero occurrences means the source moved and the control silently
stopped controlling anything -- the failure mode
`scripts/_check_the_landing_guard_can_fail.py` records paying for. Zero
convictions is likewise a failure, not a pass.

## NOTHING IS WRITTEN TO DISK

The mutated build is compiled from a source STRING into a throwaway module
object and rebound in process. The tree is never edited, so there is nothing to
forget to restore; the restore is still verified at the end.

Run::

    python scripts/_check_the_unread_readings_guard_can_fail.py
"""

from __future__ import annotations

import asyncio
import pathlib
import sys
import types

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# The mutation engine
# ---------------------------------------------------------------------------


def _rebuild(module_name: str, old: str, new: str, expect: int) -> types.ModuleType:
    """Re-execute a module with one line replaced. Never touches the tree."""
    import importlib.util

    spec = importlib.util.find_spec(module_name)
    if spec is None or not spec.origin:
        raise SystemExit("cannot locate %s" % module_name)
    path = pathlib.Path(spec.origin)
    source = path.read_text(encoding="utf-8")

    found = source.count(old)
    if found != expect:
        raise SystemExit(
            "CONTROL BROKEN: %r occurs %d times in %s, expected %d. The source "
            "moved and this mutation would have planted nothing."
            % (old, found, module_name, expect)
        )
    mutated = source.replace(old, new)

    module = types.ModuleType(module_name)
    module.__file__ = str(path)
    module.__package__ = module_name.rsplit(".", 1)[0]
    exec(compile(mutated, str(path), "exec"), module.__dict__)
    return module


def _convict(label: str, why: str, plant, run) -> bool:
    """Plant a defect, run one assertion, restore. True when it went RED."""
    undo = plant()
    try:
        run()
    except AssertionError as exc:
        # A BARE `assert x` CARRIES NO MESSAGE, and str(exc) is then "".
        # Printing the empty line was fine; indexing splitlines()[0] was not,
        # and it crashed this control on its seventh conviction.
        lines = str(exc).strip().splitlines()
        first = lines[0][:130] if lines else "(assertion carried no message)"
        print("   CONVICTED  %-52s %s" % (label, first))
        return True
    except Exception as exc:  # noqa: BLE001
        print(
            "   NOT A CONVICTION  %-44s raised %s instead of asserting"
            % (label, type(exc).__name__)
        )
        return False
    else:
        print("   *** NOT CONVICTED *** %-42s  %s" % (label, why))
        return False
    finally:
        undo()


def main() -> int:
    from linkedin_server import dom, shape
    from tests import test_the_unread_readings_were_never_driven as T

    original_about = dom.read_company_about_card
    original_filter = dom.activate_messaging_filter
    original_filters = dom.MESSAGING_FILTERS
    original_shape = shape.census_shape
    original_badge = shape.invitation_badge

    print("THE UNREAD-READINGS CHECKS, SHOWN FAILING")
    print("=" * 78)
    print()

    def sync(coro_fn, *args):
        return lambda: asyncio.run(coro_fn(*args))

    # -- dom.read_company_about_card -------------------------------------
    def plant_about(old, new, expect):
        def _plant():
            mutated = _rebuild("linkedin_server.dom", old, new, expect)
            dom.read_company_about_card = mutated.read_company_about_card

            def _undo():
                dom.read_company_about_card = original_about

            return _undo

        return _plant

    def plant_filter(old, new, expect):
        def _plant():
            mutated = _rebuild("linkedin_server.dom", old, new, expect)
            dom.activate_messaging_filter = mutated.activate_messaging_filter

            def _undo():
                dom.activate_messaging_filter = original_filter

            return _undo

        return _plant

    def plant_shape(attr, old, new, expect):
        def _plant():
            mutated = _rebuild("linkedin_server.shape", old, new, expect)
            setattr(shape, attr, getattr(mutated, attr))

            def _undo():
                setattr(
                    shape,
                    attr,
                    original_shape if attr == "census_shape" else original_badge,
                )

            return _undo

        return _plant

    results = []

    print("1. hrefs_error -- the field that tells an empty read from a failed one")
    results.append(
        _convict(
            "healthy path stops being null",
            "a non-null marker on a successful read went unnoticed",
            plant_about('marker: Optional[str] = None', 'marker: Optional[str] = "planted"', 1),
            sync(T.test_hrefs_error_is_null_when_the_links_were_actually_read),
        )
    )
    results.append(
        _convict(
            "marker gains the sibling's formula",
            "THE HAZARD ITSELF went undetected -- str(exc) in hrefs_error",
            plant_about(
                "marker = type(exc).__name__",
                'marker = f"{type(exc).__name__}: {exc}"',
                1,
            ),
            sync(T.test_a_page_value_in_the_raise_does_not_reach_hrefs_error),
        )
    )
    results.append(
        _convict(
            "the positive control is blinded",
            "the control cannot notice its own instrument going blind",
            plant_about(
                'out["error"] = f"{type(exc).__name__}: {exc}"',
                'out["error"] = type(exc).__name__',
                # ELEVEN, NOT THREE. This is a package-wide idiom in dom.py,
                # not a habit of one function, and the count was WRONG in this
                # control's first draft -- the exact-count assertion refused to
                # plant and said so, which is the assertion earning its keep
                # before the guard it checks ever ran.
                11,
            ),
            sync(T.test_the_sibling_error_field_does_carry_the_page_value),
        )
    )
    print()

    print("2. pill_label -- the page string published at active_filter.pill_label")
    results.append(
        _convict(
            "an eighth raw field is added",
            "the SET pin did not notice a new page-text field",
            plant_filter(
                '"pill_label": label,',
                '"pill_label": label,\n        "pill_label_echo": label,',
                1,
            ),
            sync(T.test_exactly_one_returned_field_carries_page_text, "inmail"),
        )
    )
    results.append(
        _convict(
            "the label becomes the argument",
            "the test could not tell the page's string from the caller's",
            plant_filter('"pill_label": label,', '"pill_label": wanted,', 1),
            sync(T.test_the_pill_label_is_not_drawn_from_the_closed_tuple),
        )
    )
    results.append(
        _convict(
            "url_before loses its redactor",
            "THE 2026-09-03 DEFECT went undetected",
            plant_filter(
                '"url_before": shape.redact_thread_id(before),',
                '"url_before": label,',
                1,
            ),
            sync(T.test_the_two_redacted_url_fields_are_still_redacted_beside_it),
        )
    )

    def plant_open_set():
        dom.MESSAGING_FILTERS = tuple(original_filters) + (
            "example-harness-argument",
        )

        def _undo():
            dom.MESSAGING_FILTERS = original_filters

        return _undo

    results.append(
        _convict(
            "the closed set admits the harness argument",
            "a stale not_driven baseline would go unreported",
            plant_open_set,
            T.test_the_reader_guard_cannot_supply_a_permitted_filter_name,
        )
    )
    print()

    print("3. the premise shape.invitation_badge rests on")
    results.append(
        _convict(
            "census_shape redacts everything",
            "the refutation passes even when the shaper DOES redact",
            plant_shape(
                "census_shape",
                # ANCHORED ON THE GATE'S OWN TAIL. A bare `return shaped`
                # occurs TWICE in shape.py -- census_substitute ends the same
                # way -- and mutating both would have changed the substituter
                # this function calls, convicting for the wrong reason.
                "        return CENSUS_OPAQUE\n    return shaped\n",
                "        return CENSUS_OPAQUE\n    return CENSUS_OPAQUE\n",
                1,
            ),
            T.test_census_shape_does_not_redact_a_name_shaped_string,
        )
    )
    results.append(
        _convict(
            "census_shape redacts nothing at all",
            "the both-directions half is not actually checked",
            plant_shape(
                "census_shape",
                "    if len(shaped) > CENSUS_NAME_LIMIT:\n"
                "        return CENSUS_OPAQUE\n"
                '    residue = _CENSUS_PLACEHOLDER.sub("", shaped)\n'
                "    if not _CENSUS_SAFE_CHARS.match(residue):\n"
                "        return CENSUS_OPAQUE\n"
                "    return shaped\n",
                "    return shaped\n",
                1,
            ),
            T.test_census_shape_does_not_redact_a_name_shaped_string,
        )
    )
    results.append(
        _convict(
            "shaped_label stops being published",
            "the publication point was not actually pinned",
            plant_shape(
                "invitation_badge",
                '"shaped_label": label,',
                '"shaped_label": None,',
                # TWO, AND THE TWO ARE THE TWO BRANCHES. Both sites are inside
                # invitation_badge: one in the nested _unreadable closure, one
                # on the success return. That is the same pair the test asserts
                # over, so mutating both is the mutation, not an over-reach.
                2,
            ),
            T.test_the_shaped_label_is_published_on_both_branches,
        )
    )
    print()

    # -- restore, verified ------------------------------------------------
    restored = (
        dom.read_company_about_card is original_about
        and dom.activate_messaging_filter is original_filter
        and dom.MESSAGING_FILTERS is original_filters
        and shape.census_shape is original_shape
        and shape.invitation_badge is original_badge
    )
    print("=" * 78)
    print("convictions           %d of %d" % (sum(results), len(results)))
    print("every binding restored %s" % restored)
    if not restored:
        print("FAIL: the tree's in-process bindings were not restored")
        return 2
    if not all(results):
        print("FAIL: at least one check could not be made to fail.")
        return 1
    print("PASS: every assertion in the guard was shown convicting a defect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
