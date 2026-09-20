"""A page that answers in STRINGS, so a reader's coercions can be measured.

WHAT THIS IS FOR, in one sentence. ``int()`` puts the value it refused verbatim
into its ``ValueError``; an exception is not a return value; so a reader that
returns nothing but integers still carries a page string out of the process the
moment the page hands it one. This module supplies the page that hands it one.

## THE FIDELITY RULE, AND IT IS THE WHOLE DESIGN

    A DOUBLE THAT ANSWERS EVERYTHING IN STRINGS MANUFACTURES LEAKS
    THAT CANNOT HAPPEN.

``await locator.count()`` is awaited and CANNOT be a string: Playwright
computes that integer itself and its type is part of Playwright's API, not the
document's. ``await page.evaluate(...)`` can be anything the document's
JavaScript returned. Making ``count()`` answer with a name would convict
``events.py`` and ``groups_page.py`` of leaks they are structurally incapable
of -- both coerce nothing but ``.count()`` results and ``len()`` of text -- and
a measurement that cries wolf is one nobody acts on.

So this double splits its answers exactly where Playwright's own contract
splits them:

* **PAGE-CONTROLLED** -- ``evaluate``, ``inner_text``, ``text_content``,
  ``get_attribute``, ``content``, ``title``, ``input_value``. These answer with
  :data:`PLANT`, because the document chooses them.
* **PLAYWRIGHT-TYPED** -- ``count``, ``is_visible``, ``is_enabled``,
  ``bounding_box``. These answer with the type Playwright promises. A page
  cannot make them lie.

## WHY THE ANSWER IS KEY-AGNOSTIC, WITH THE FALSE NEGATIVE THAT FORCED IT

The survey shipped in ``scripts/_check_the_shaper_leak_guard_can_fail.py`` drove
the siblings with a fixed superset payload::

    {"anchors": 1, "counts": [...], "headings": 1, "groupings": [...], ...}

and reported ``collections_page.read_collections`` **clean**. It is not clean.
That reader reads ``raw.get("matches")`` -- and ``matches`` is not a key in
that payload, so the list was empty, the comprehension iterated nothing, and
the coercion never ran. **The reader was never driven, and "not driven" printed
as "clean".**

A HAND-WRITTEN PAYLOAD CAN ONLY EXERCISE THE KEYS ITS AUTHOR THOUGHT OF, which
is the same defect as a leak detector that is a list of known-bad strings --
recorded twice already in ``tests/leakwalk.py``'s docstring. So :class:`PageAnswer`
answers EVERY key, and no reader can dodge the plant by reading a field the
harness's author did not predict.

## THE PLANT IS NOT THE ARGUMENT

Readers that take a needle (``read_selected_recipients(page, needle)``) legally
echo their own argument back, and that is not a leak -- it is the caller's own
string returning to the caller. The harness therefore supplies
:data:`SYNTHETIC_ARGUMENT` for required parameters and hunts :data:`PLANT`, two
values that are never equal. Hunting a value the harness itself passed in would
convict every echoing reader and prove nothing.

## THE PLANT IS SYNTHETIC AND DELIBERATELY NOT A PERSON

It carries ``example``, which is in the shape guard's own synthetic vocabulary,
so it passes the identity gate on sight -- the same reasoning
``anchors.control_fixture`` gives for its slugs. It is also past
``leakwalk.MIN_SECRET`` so ``leakwalk.find_leaks`` will hunt it rather than
refuse it, which a shorter marker would have done silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

#: The name the page answers with. Name-SHAPED, synthetic, and long enough for
#: ``leakwalk.find_leaks`` to accept it as a hunt target (>= MIN_SECRET = 24).
PLANT = "Exampleperson Markersurname"

#: What the harness passes for a reader's own required arguments. NEVER equal
#: to :data:`PLANT` -- see the module docstring.
SYNTHETIC_ARGUMENT = "example-harness-argument"

#: How deep a nested locator walk may go before ``count()`` answers 0. A real
#: page terminates because it is finite; a double has to be told.
MAX_DEPTH = 6

#: What a Playwright ``count()`` answers at every level above the cap. One,
#: rather than a large number, because the question is whether a reader coerces
#: page text at all -- not how fast it does it.
CHILDREN_PER_LEVEL = 1


class PageString(str):
    """A string the DOCUMENT chose, which also answers like a container.

    It is a real ``str`` -- ``isinstance(x, str)`` holds and ``int(x)`` raises
    a ValueError quoting it, which is the entire point. The container methods
    exist so that a reader reaching THROUGH the value still meets the plant:

    * ``.get(k)`` answers itself, so ``row.get("index", -1)`` is planted.
    * ``__iter__`` yields itself ONCE rather than character by character.
      Without this, ``list(page_string)`` becomes ``['E', 'x', ...]`` and the
      reader coerces a single letter -- which no leak detector flags, because
      one character is not a run. The measurement would come back clean on a
      reader that leaks.
    * ``keys()`` plus a mapping ``__getitem__`` means ``dict(value)`` yields
      ``{plant: plant}`` instead of raising, so a reader that normalises a
      field into a dict is driven rather than crashed.

    Integer and slice subscripts fall through to ``str`` so ordinary string
    handling -- and ``leakwalk``'s own run-slicing -- behaves normally.
    """

    def get(self, key: Any, default: Any = None) -> "PageString":
        return self

    def keys(self) -> tuple[str, ...]:
        return (str(self),)

    def values(self) -> tuple["PageString", ...]:
        return (self,)

    def items(self) -> tuple[tuple[str, "PageString"], ...]:
        return ((str(self), self),)

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, (int, slice)):
            return str.__getitem__(self, key)
        return self

    def __iter__(self) -> Iterator["PageString"]:
        return iter((self,))


def _harvest_key_vocabulary() -> tuple[str, ...]:
    """Every string literal this package ever looks up in a mapping.

    ## THE BUG THIS EXISTS FOR, AND IT WAS IN THIS HARNESS

    :class:`PageAnswer` overrides ``get`` so that no reader can dodge the plant
    by reading a field the harness's author did not predict. ``dom.py`` then
    does this, fourteen times::

        data = dict(data or {})

    ``dict()`` of a dict SUBCLASS copies the concrete storage and never calls
    the overridden ``get``. So a key-agnostic double is flattened back into
    whatever keys it literally holds, and every subsequent ``data.get("controls")``
    answers ``None``. Measured: ``dom.read_surface_census`` returned
    ``controls_read: 0`` -- it had been handed a page that answers every key
    with a name and reported having seen nothing.

    **THE HARNESS WAS MANUFACTURING CLEAN VERDICTS**, which is the same defect
    as the sibling survey's missing ``matches`` key, one level up and in the
    tool built to catch it.

    ## WHY THE VOCABULARY IS READ OFF THE SOURCE RATHER THAN TYPED OUT

    A hand-written key list is a list of the keys its author thought of -- the
    exact failure above. Scanning for ``x.get("literal")`` and ``x["literal"]``
    across the package yields the keys the readers ACTUALLY read, and a key
    introduced by a reader written tomorrow is in the vocabulary the moment it
    is written, with no edit here.
    """
    import ast

    package = Path(__file__).resolve().parents[1] / "linkedin_server"
    keys: set[str] = set()
    for path in sorted(package.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"get", "pop", "setdefault"}
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                keys.add(node.args[0].value)
            elif (
                isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)
            ):
                keys.add(node.slice.value)
    return tuple(sorted(keys))


#: Harvested once at import. See :func:`_harvest_key_vocabulary`.
KEY_VOCABULARY: tuple[str, ...] = _harvest_key_vocabulary()


class PageAnswer(dict):
    """What ``page.evaluate`` hands back: a mapping that answers EVERY key.

    Two mechanisms, because one is not enough:

    * ``get``/``__getitem__``/``__missing__`` answer any key at all, so a
      reader cannot dodge the plant with a field nobody predicted;
    * the CONCRETE STORAGE is seeded with :data:`KEY_VOCABULARY`, so the plant
      survives ``dict(data or {})`` -- which bypasses every override above.

    Non-empty on purpose in both cases. Readers in this package are written
    ``(raw or {}).get(...)``, and an empty dict is falsy -- an empty double
    would route every one of them down the ``{}`` branch and measure nothing.
    """

    def __init__(self) -> None:
        super().__init__({key: PageString(PLANT) for key in KEY_VOCABULARY})

    def get(self, key: Any, default: Any = None) -> PageString:
        return PageString(PLANT)

    def __getitem__(self, key: Any) -> PageString:
        return PageString(PLANT)

    def __missing__(self, key: Any) -> PageString:
        return PageString(PLANT)


class NavigationAttempted(RuntimeError):
    """A reader tried to drive the browser. It is NOT-DRIVEN, not clean.

    Raised rather than silently accepted so that a reader which navigates,
    clicks or types is reported as a site this offline harness could not
    measure -- with its name -- instead of passing on a no-op.
    """


class PlantedLocator:
    """Playwright's locator, answering page text as text and counts as ints."""

    def __init__(self, depth: int = 0) -> None:
        self._depth = depth

    # -- structure ---------------------------------------------------------
    def locator(self, *args: Any, **kwargs: Any) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    def get_by_role(self, *args: Any, **kwargs: Any) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    def get_by_text(self, *args: Any, **kwargs: Any) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    def nth(self, index: int) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    @property
    def first(self) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    @property
    def last(self) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    # -- PLAYWRIGHT-TYPED: the page cannot make these lie -------------------
    async def count(self) -> int:
        return CHILDREN_PER_LEVEL if self._depth < MAX_DEPTH else 0

    async def is_visible(self, **kwargs: Any) -> bool:
        return True

    async def is_enabled(self, **kwargs: Any) -> bool:
        return True

    async def is_disabled(self, **kwargs: Any) -> bool:
        return False

    async def is_checked(self, **kwargs: Any) -> bool:
        return False

    async def is_editable(self, **kwargs: Any) -> bool:
        return True

    async def is_hidden(self, **kwargs: Any) -> bool:
        return False

    async def bounding_box(self, **kwargs: Any) -> dict[str, float]:
        return {"x": 0.0, "y": 0.0, "width": 1.0, "height": 1.0}

    async def wait_for(self, **kwargs: Any) -> None:
        return None

    # -- PAGE-CONTROLLED: every one of these can be a name ------------------
    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> PageAnswer:
        return PageAnswer()

    async def evaluate_all(self, script: Any, arg: Any = None) -> list[PageAnswer]:
        return [PageAnswer()]

    async def inner_text(self, **kwargs: Any) -> PageString:
        return PageString(PLANT)

    async def text_content(self, **kwargs: Any) -> PageString:
        return PageString(PLANT)

    async def inner_html(self, **kwargs: Any) -> PageString:
        return PageString(PLANT)

    async def input_value(self, **kwargs: Any) -> PageString:
        return PageString(PLANT)

    async def get_attribute(self, name: str, **kwargs: Any) -> PageString:
        return PageString(PLANT)

    async def all_text_contents(self) -> list[PageString]:
        return [PageString(PLANT)]

    async def all_inner_texts(self) -> list[PageString]:
        return [PageString(PLANT)]

    async def all(self) -> list["PlantedLocator"]:
        if self._depth >= MAX_DEPTH:
            return []
        return [PlantedLocator(self._depth + 1)]

    async def element_handle(self, **kwargs: Any) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    async def element_handles(self) -> list["PlantedLocator"]:
        return [PlantedLocator(self._depth + 1)]

    # -- ACTIONS: refused, loudly -------------------------------------------
    async def click(self, **kwargs: Any) -> None:
        raise NavigationAttempted("locator.click")

    async def fill(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("locator.fill")

    async def set_input_files(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("locator.set_input_files")

    async def select_option(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("locator.select_option")


class PlantedPage:
    """Playwright's page, wired to the same split as :class:`PlantedLocator`."""

    #: A real LinkedIn read address, so a reader that checks where it is does
    #: not bail before reaching its coercions. It carries no identifier.
    url = "https://www.linkedin.com/feed/"

    def __init__(self) -> None:
        self.context = None
        self.keyboard = _PlantedKeyboard()

    # -- structure ---------------------------------------------------------
    def locator(self, *args: Any, **kwargs: Any) -> PlantedLocator:
        return PlantedLocator()

    def get_by_role(self, *args: Any, **kwargs: Any) -> PlantedLocator:
        return PlantedLocator()

    def get_by_text(self, *args: Any, **kwargs: Any) -> PlantedLocator:
        return PlantedLocator()

    def frame_locator(self, *args: Any, **kwargs: Any) -> PlantedLocator:
        return PlantedLocator()

    def is_closed(self) -> bool:
        return False

    # -- PAGE-CONTROLLED ----------------------------------------------------
    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> PageAnswer:
        return PageAnswer()

    async def evaluate_handle(self, script: Any, arg: Any = None) -> PageAnswer:
        return PageAnswer()

    async def eval_on_selector(self, *args: Any, **kwargs: Any) -> PageAnswer:
        return PageAnswer()

    async def eval_on_selector_all(self, *args: Any, **kwargs: Any) -> list[PageAnswer]:
        return [PageAnswer()]

    async def content(self) -> PageString:
        return PageString(PLANT)

    async def title(self) -> PageString:
        return PageString(PLANT)

    async def inner_text(self, *args: Any, **kwargs: Any) -> PageString:
        return PageString(PLANT)

    async def text_content(self, *args: Any, **kwargs: Any) -> PageString:
        return PageString(PLANT)

    async def query_selector(self, *args: Any, **kwargs: Any) -> PlantedLocator:
        return PlantedLocator()

    async def query_selector_all(self, *args: Any, **kwargs: Any) -> list[PlantedLocator]:
        return [PlantedLocator()]

    async def wait_for_selector(self, *args: Any, **kwargs: Any) -> PlantedLocator:
        return PlantedLocator()

    # -- TIMING: instant, so a wait loop terminates -------------------------
    async def wait_for_timeout(self, timeout: Any = 0) -> None:
        return None

    async def wait_for_load_state(self, *args: Any, **kwargs: Any) -> None:
        return None

    # -- ACTIONS: refused, loudly -------------------------------------------
    async def goto(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("page.goto")

    async def click(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("page.click")

    async def fill(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("page.fill")

    async def set_input_files(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("page.set_input_files")

    async def select_option(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("page.select_option")

    async def close(self, **kwargs: Any) -> None:
        raise NavigationAttempted("page.close")


class _PlantedKeyboard:
    async def press(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("keyboard.press")

    async def type(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("keyboard.type")


#: Phrases only a FAILED COERCION produces. No contract field in this package
#: says any of these, so a returned string carrying one is an exception message
#: that was caught and put into the output.
COERCION_FAILURE_SIGNATURES: tuple[str, ...] = (
    "invalid literal for int()",
    "could not convert string to float",
    "invalid literal for int() with base",
)


def carries_a_laundered_exception(obj: Any) -> list[str]:
    """Places where a RETURN VALUE holds a caught coercion's MESSAGE.

    ## THE HOLE THIS CLOSES IN THE GUARD ABOVE IT

    The family guard treats a raised exception carrying the plant as a LEAK and
    a returned string carrying page text as CONTRACT. Between those two sits a
    third thing:

        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"

    which this package does at **18 sites across 6 modules**. If a coercion
    inside such a ``try`` refuses a page string, the ValueError never escapes --
    its MESSAGE is returned instead, quoting the name in a field, and the guard
    would call that ``returns_text`` and pass it.

    > **A NAME THAT LEAVES THROUGH A CAUGHT EXCEPTION HAS STILL LEFT.**

    Measured 2026-09-20: **22 coercion sites sit inside such a try**, and all 22
    are ``int(await ...count())`` -- Playwright integers, which the page cannot
    turn into a string. **The hazard is real and empty BY CONSTRUCTION, not by
    luck**, which is the PAGE-CONTROLLED/PLAYWRIGHT-TYPED distinction holding up
    under a second, independent test. This detector exists so that the day
    somebody puts a page-derived coercion inside one of those eighteen
    handlers, it is caught rather than found.

    The signature match is what makes this precise rather than a heuristic: no
    field in this package's contract says *"invalid literal for int()"*.
    """
    from tests.leakwalk import walk

    return [
        path
        for path, text in walk(obj)
        if any(signature in text for signature in COERCION_FAILURE_SIGNATURES)
    ]


def carries_the_plant(obj: Any) -> list[str]:
    """Every place in ``obj`` -- return value OR exception -- holding the plant.

    Delegates the walk to ``tests.leakwalk``, which already walks dict keys,
    bytes, exception ``args``, ``str(exc)``, ``repr(exc)`` and unknown types
    via ``repr``. Reusing it is deliberate: this repository has measured that
    every fresh instrument built in a session had a bug on its first attempt,
    and ``leakwalk`` is driven in both directions by ``tests/test_leakwalk.py``.
    """
    from tests.leakwalk import walk

    return [path for path, text in walk(obj) if PLANT in text]
