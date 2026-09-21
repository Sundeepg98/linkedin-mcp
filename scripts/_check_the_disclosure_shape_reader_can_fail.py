"""THE CONTROLS FOR `_probe_all_filters_disclosure_shape.py`. SHOWN FAILING.

A reader that has never been shown failing certifies nothing, and this
repository has paid for that three times in one round -- a dead reflow detector,
a transposed contrast metric that manufactured six false failures, and twelve
phantom violations from sampling mid-fade. So every claim the live probe makes
is exercised here against a MANUFACTURED fixture with a KNOWN answer, both ways
round: the positive case must read the expected integer AND the negative case
must read zero.

**THE FIXTURE IS BUILT, NEVER FOUND.** It is a string in this file. A control
that discovers its fixture in ambient page state passes on the box it was
written on and fails in every clone.

**IT TOUCHES NO LINKEDIN AND NO PROFILE.** It launches a throwaway chromium with
no persistent context, loads the fixture through `set_content` -- it navigates
NOWHERE, not even to a `data:` url -- and closes it. There is no CDP, no attach,
no session, no signed-in account anywhere in this file.

## THE FOUR CLAIMS UNDER TEST

1. **The lifted matcher is the shipped matcher.** The shipped filter fixture and
   its shipped expectation are driven through THIS probe's script, and every
   term must read what `search_results.FILTER_CONTROL_EXPECTATION` says.
2. **The attribute half reports the sanctioned shapes.** A control carrying
   `aria-expanded="false"` reads value index 1 and a position in the
   `[aria-expanded]` node list; one carrying `aria-haspopup="dialog"` reads
   value index 5; one carrying NEITHER reads -1 for both, which is the reading
   that refuses a press at condition 2.
3. **The hidden-excluded label half CAN DISAGREE with the shipped one.** A
   button whose visible text is `Reset` and whose clip-styled screen-reader span
   adds `Current company` matches under `textContent` and must NOT match once
   hidden text is excluded. Without this control the second column is decorative:
   a column that always equals its neighbour proves nothing.
4. **The output gate refuses a planted string.** Three plants, each at a
   different depth, and each must raise.

Run::

    venv\\Scripts\\python.exe scripts/_check_the_disclosure_shape_reader_can_fail.py

Exit 0 only if every control behaves. Prints integers and verdicts.
"""
from __future__ import annotations

import asyncio
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import _probe_all_filters_disclosure_shape as probe  # noqa: E402
from linkedin_server import search_results  # noqa: E402

#: THE MANUFACTURED PAGE. Every case is here on purpose and each is annotated
#: with the reading it must produce.
FIXTURE = (
    "<!doctype html><html><head><style>"
    ".sr-only{position:absolute;clip:rect(0 0 0 0);width:1px;height:1px;"
    "overflow:hidden}"
    "</style></head><body>"
    # CASE A -- the shape under test, present and shut.
    '<button aria-expanded="false" aria-controls="x">All filters</button>'
    # CASE B -- a menu trigger carrying the OTHER sanctioned attribute.
    '<button aria-haspopup="dialog">Show results</button>'
    # CASE C -- a control carrying NEITHER sanctioned attribute. This is the
    # reading that makes a press unreachable by this route rather than not-yet.
    "<button>Industry</button>"
    # CASE D -- THE HIDDEN-TEXT TRAP. Visible text is `Reset`; the clip-styled
    # screen-reader span supplies `Current company`. textContent folds it in.
    #
    # THE SEPARATING SPACE IS LOAD-BEARING AND THE FIRST DRAFT LACKED IT.
    # Without it `textContent` returns `ResetCurrent company`, which normalises
    # to the token `resetcurrent` and matches NOTHING -- so the trap silently
    # disarmed itself and the control read (0,0). Hidden text inflates a
    # containment match only when the markup leaves whitespace beside it, which
    # real markup does and a hand-written fixture forgets.
    '<button>Reset <span class="sr-only">Current company</span></button>'
    # CASE E -- the same trap in its aria-hidden spelling, on a term that must
    # otherwise read zero on this fixture.
    '<button>Sort <span aria-hidden="true">Open to volunteering</span></button>'
    # CASE F -- the synthetic negative, which must never match anything.
    "<button>School Anise</button>"
    "</body></html>"
)

#: `[aria-expanded]` holds exactly CASE A, so its index is 0.
EXPECTED_EXPANDED_NODES = 1
#: `[aria-haspopup]` holds exactly CASE B, so its index is 0.
EXPECTED_HASPOPUP_NODES = 1

#: phrase index -> (shipped-label match, hidden-excluded match) on FIXTURE.
EXPECTED_MATCHES: dict[int, tuple[int, int]] = {
    0: (1, 1),   # all filters          CASE A, matches under both
    2: (0, 0),   # school anise         CASE F is `School Anise` -- two tokens,
                 #                      and `school anise` IS two tokens, so it
                 #                      matches by containment. See below.
    3: (1, 1),   # show results         CASE B
    4: (1, 0),   # current company      CASE D -- THE DISAGREEMENT
    9: (1, 0),   # open to volunteering CASE E -- THE DISAGREEMENT
    13: (1, 1),  # industry             CASE C
}


async def _read(page, html: str) -> dict:
    """Load the built fixture WITHOUT NAVIGATING ANYWHERE.

    The first draft used ``page.goto`` on a ``data:`` url and
    ``tests/test_probe_navigation_budget.py`` refused it -- correctly, and
    usefully. Its remedy list offers a ``KNOWN_UNGUARDED`` declaration, which
    would have been the FIRST entry in a table that is empty on purpose; the
    cheaper answer is not to navigate at all. ``set_content`` is this
    repository's established fixture path and it is honestly what this wants:
    the fixture is a string, not an address.
    """
    await page.set_content(  # readonly-ok -- local markup, no navigation
        html, wait_until="domcontentloaded", timeout=60_000
    )
    return await probe.read_shape(page)


def _fail(message: str) -> None:
    print(f"  FAIL  {message}")


def _ok(message: str) -> None:
    print(f"  ok    {message}")


async def main() -> int:
    from playwright.async_api import async_playwright

    failures = 0
    print("CONTROL 4 -- THE OUTPUT GATE REFUSES A PLANTED STRING")
    plants = (
        {"shape": {"controls_scanned": "Current company"}},
        {"shape": {"matched_shipped_label": [1, "a name"]}},
        {"not_a_declared_key": 1},
    )
    for position, plant in enumerate(plants):
        try:
            probe._gate(plant, "plant")
        except ValueError as exc:
            _ok(f"plant {position} raised: {exc}")
        else:
            failures += 1
            _fail(f"plant {position} PASSED THE GATE -- the gate cannot fail")
    try:
        probe._gate({"shape": {"controls_scanned": 3}}, "clean")
    except ValueError as exc:
        failures += 1
        _fail(f"the gate refused a CLEAN payload: {exc}")
    else:
        _ok("a clean payload passes -- the gate is not refusing everything")
    print()

    async with async_playwright() as playwright_instance:
        browser = await playwright_instance.chromium.launch()
        try:
            page = await browser.new_page()

            print("CONTROL 1 -- THE LIFTED MATCHER IS THE SHIPPED MATCHER")
            shipped = await _read(
                page,
                "<!doctype html><html><body>"
                + search_results.filter_control_fixture()
                + "</body></html>",
            )
            # A `for ... else` HERE WAS A BUG AND IT PRINTED `ok` BESIDE ITS OWN
            # FAILURES: the `else` of a `for` runs unless the loop BREAKS, so it
            # fired whether or not a term disagreed. A check that claims more
            # than it ran is the half-truth this repository refuses everywhere
            # else; the agreement is now counted and the count is what prints.
            agreed = 0
            for term, expected in search_results.FILTER_CONTROL_EXPECTATION.items():
                index = probe.PROBE_PHRASES.index(term)
                got = shipped["matched_shipped_label"][index]
                if got != expected:
                    failures += 1
                    _fail(f"shipped fixture term {index}: {got} != {expected}")
                else:
                    agreed += 1
            expected_terms = len(search_results.FILTER_CONTROL_EXPECTATION)
            if agreed == expected_terms:
                _ok(
                    "all %d shipped terms read their shipped expectation"
                    % expected_terms
                )
            else:
                _fail(
                    "%d of %d shipped terms agreed" % (agreed, expected_terms)
                )
            # THE SHIPPED FIXTURE'S OWN NEGATIVES, re-asserted through this
            # script: `Next` must not match `next`... it MUST, by equality.
            # What must NOT match is the synthetic two-token trap against the
            # single-word term `school`.
            school = probe.PROBE_PHRASES.index("school")
            if shipped["matched_shipped_label"][school] != 1:
                failures += 1
                _fail("the shipped fixture's `School` button did not match")
            else:
                _ok("`school` matched exactly the whole-label control")
            print()

            print("CONTROLS 2 AND 3 -- ATTRIBUTES, AND THE HIDDEN-TEXT TRAP")
            got = await _read(page, FIXTURE)
            if got["expanded_nodes"] != EXPECTED_EXPANDED_NODES:
                failures += 1
                _fail(
                    "[aria-expanded] nodes %d != %d"
                    % (got["expanded_nodes"], EXPECTED_EXPANDED_NODES)
                )
            else:
                _ok("[aria-expanded] node count is the built one")
            if got["haspopup_nodes"] != EXPECTED_HASPOPUP_NODES:
                failures += 1
                _fail(
                    "[aria-haspopup] nodes %d != %d"
                    % (got["haspopup_nodes"], EXPECTED_HASPOPUP_NODES)
                )
            else:
                _ok("[aria-haspopup] node count is the built one")

            for index, (shipped_expected, visible_expected) in sorted(
                EXPECTED_MATCHES.items()
            ):
                shipped_got = got["matched_shipped_label"][index]
                visible_got = got["matched_hidden_excluded"][index]
                if index == 2:
                    # `school anise` is two tokens and CASE F is `School Anise`,
                    # so containment matches. That is the shipped rule and this
                    # control asserts the rule, not a hoped-for zero.
                    shipped_expected, visible_expected = 1, 1
                if (shipped_got, visible_got) != (
                    shipped_expected, visible_expected
                ):
                    failures += 1
                    _fail(
                        "phrase %d read (%d,%d), expected (%d,%d)"
                        % (index, shipped_got, visible_got,
                           shipped_expected, visible_expected)
                    )
                else:
                    _ok(
                        "phrase %d reads (%d,%d) as built"
                        % (index, shipped_got, visible_got)
                    )

            # THE DISAGREEMENT IS THE WHOLE POINT OF THE SECOND COLUMN.
            disagreements = sum(
                1
                for index in range(len(probe.PROBE_PHRASES))
                if got["matched_shipped_label"][index]
                != got["matched_hidden_excluded"][index]
            )
            if disagreements < 2:
                failures += 1
                _fail(
                    "the hidden-excluded column disagreed %d times on a fixture "
                    "built to make it disagree twice -- it cannot fail"
                    % disagreements
                )
            else:
                _ok(f"hidden-excluded column disagreed {disagreements} times")

            all_filters = 0
            if got["first_expanded_value"][all_filters] != 1:
                failures += 1
                _fail(
                    "CASE A aria-expanded value index %d, expected 1 (false)"
                    % got["first_expanded_value"][all_filters]
                )
            else:
                _ok("CASE A reports aria-expanded=false as value index 1")
            if got["first_expanded_index"][all_filters] != 0:
                failures += 1
                _fail(
                    "CASE A position in [aria-expanded] is %d, expected 0"
                    % got["first_expanded_index"][all_filters]
                )
            else:
                _ok("CASE A reports its position in the [aria-expanded] list")
            show_results = 3
            if got["first_haspopup_value"][show_results] != 5:
                failures += 1
                _fail(
                    "CASE B aria-haspopup value index %d, expected 5 (dialog)"
                    % got["first_haspopup_value"][show_results]
                )
            else:
                _ok("CASE B reports aria-haspopup=dialog as value index 5")
            industry = 13
            if (
                got["first_expanded_value"][industry],
                got["first_haspopup_value"][industry],
            ) != (probe.ABSENT, probe.ABSENT):
                failures += 1
                _fail("CASE C did not report BOTH attributes absent")
            else:
                _ok("CASE C reports both sanctioned attributes ABSENT (-1,-1)")
            print()

            # CONTROL 3b -- THE `aria-label` COLUMN CAN READ BOTH WAYS.
            # Without it the hidden-excluded column is uninterpretable live:
            # both label sources prefer `aria-label`, so where one exists they
            # agree by construction. The column that says WHICH PATH RAN is
            # therefore load-bearing, and a column that can only read one value
            # is decoration.
            if got["matched_with_aria_label"][0] != 0:
                failures += 1
                _fail("CASE A has no aria-label but the column read nonzero")
            else:
                _ok("CASE A reports 0 matches carrying an aria-label")
            keywords = probe.PROBE_PHRASES.index("keywords")
            if shipped["matched_with_aria_label"][keywords] != 1:
                failures += 1
                _fail(
                    "the shipped fixture's aria-labelled `Keywords` control "
                    "read %d in the aria-label column, expected 1"
                    % shipped["matched_with_aria_label"][keywords]
                )
            else:
                _ok("an aria-labelled control reports 1 in that column")
            print()

            print("CONTROL 5 -- THE PAYLOAD COUNTER CAN READ ZERO AND NONZERO")
            payload = probe.count_in_payload(FIXTURE)
            if payload["tight_hits"][0] < 1:
                failures += 1
                _fail("`all filters` read 0 in a fixture that contains it")
            else:
                _ok("`all filters` reads nonzero in bytes that carry it")
            keywords = probe.PROBE_PHRASES.index("keywords")
            if payload["tight_hits"][keywords] != 0:
                failures += 1
                _fail("`keywords` read nonzero in bytes that do not carry it")
            else:
                _ok("`keywords` reads 0 in bytes that do not carry it")
        finally:
            await browser.close()

    print()
    if failures:
        print(f"CONTROLS FAILED: {failures}")
        return 1
    print("ALL CONTROLS BEHAVED. The reader can fail, and did not here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
