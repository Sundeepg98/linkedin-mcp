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

from collections.abc import Mapping
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


class NavigationAttempted(BaseException):
    """A reader tried to drive the browser. It is NOT-DRIVEN, not clean.

    Raised rather than silently accepted so that a reader which navigates,
    clicks or types is reported as a site this offline harness could not
    measure -- with its name -- instead of passing on a no-op.

    A ``BaseException``, NOT A ``RuntimeError`` (2026-09-28), so the reader
    under test cannot catch it. Readers wrap their presses and loads in
    ``except Exception`` -- rightly, for a live page -- and as a
    ``RuntimeError`` this signal was caught there and turned into the
    reader's own answer: a load swallowed became "returned without reading
    the page", and a click swallowed after a read would have come back
    clean. The harness catches it by name; nothing else should.
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

    # PLAYWRIGHT'S LOCATOR ALGEBRA (added 2026-09-28). Missing, a reader that
    # narrows a locator with one raised AttributeError inside its own handler
    # and returned ``{"error": "AttributeError"}`` -- and three readers were
    # recorded clean on exactly that: ``read_opened_conversation``,
    # ``read_account_share_updates``, ``recognise_intro_editor_switches``.
    def and_(self, *args: Any, **kwargs: Any) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    def or_(self, *args: Any, **kwargs: Any) -> "PlantedLocator":
        return PlantedLocator(self._depth + 1)

    def filter(self, *args: Any, **kwargs: Any) -> "PlantedLocator":
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
    """Playwright's page, wired to the same split as :class:`PlantedLocator`.

    IT COUNTS ITS OWN READS (2026-09-27), in :attr:`reads`: every use of a
    method in :data:`READ_ENTRY_POINTS`, the calls through which a reader
    reaches what a page holds. Counted in ``__getattribute__`` so a subclass
    that overrides a read is counted too. A reader driven here that returns
    with ``reads == 0`` never read the page, and its verdict says nothing
    about what a page can make it carry -- which is how readers were recorded
    clean having read nothing (``tests/test_readers_emit_no_page_string.py``).
    """

    #: A real LinkedIn read address, so a reader that checks where it is does
    #: not bail before reaching its coercions. It carries no identifier.
    url = "https://www.linkedin.com/feed/"

    #: The page's read entry points. ``url`` is not one: it is the address the
    #: harness set, not something the page drew.
    READ_ENTRY_POINTS = frozenset(
        {
            "locator", "get_by_role", "get_by_text", "frame_locator", "evaluate",
            "evaluate_handle", "eval_on_selector", "eval_on_selector_all",
            "content", "title", "inner_text", "text_content", "query_selector",
            "query_selector_all", "wait_for_selector",
        }
    )

    #: Reads so far. A class default, so a subclass that skips ``__init__``
    #: still counts from zero.
    reads = 0

    def __init__(self) -> None:
        self.context = None
        self.keyboard = _PlantedKeyboard()

    def __getattribute__(self, name: str) -> Any:
        if name in PlantedPage.READ_ENTRY_POINTS:
            object.__setattr__(self, "reads", object.__getattribute__(self, "reads") + 1)
        return object.__getattribute__(self, name)

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


# ---------------------------------------------------------------------------
# THE BLANK PAGE -- the same calls, over a page that draws nothing.
#
# Added 2026-10-10 (lane G2). "A read and something back" let a reader be
# recorded clean on what it hands back whatever the page drew: a refusal tally
# with every count zero, a poll budget, its own sentence. Measured that day, 17
# readers were clean on exactly that, the guard's own control reader
# (``anchors.read_anchors``) among them. A success path leaves something the
# PAGE made, and the measure of that is what the same call returns over a page
# that draws nothing: a value the planted page changed is the page's; a value
# both pages give is the reader's own.
#
# FAITHFUL TO A REAL EMPTY PAGE, because an unfaithful null manufactures
# agreement: every locator counts 0 and is not visible, every page-controlled
# read answers empty (``None`` where Playwright answers ``None``), and every
# WAIT TIMES OUT -- raising ``TimeoutError``, the name this package's readers
# classify a wait's expiry by -- because on a page that never draws the thing,
# that is what Playwright does. A first version whose waits returned at once
# read seven wait readers as "attached" on both pages and convicted them for
# the double's fault. Actions are refused as on the planted page.
#
# ITS ONE KNOWN DEPARTURE, named so nobody mistakes it for a finding: a
# script answers ``None`` here, where a real engine returns whatever the
# script returns over an empty document (a dict of zeros, usually). A reader
# that reads that answer outside its own ``try`` raises over this page --
# ``dom.read_sdui_actions`` does -- and the guard then calls the drive not
# driven, because nothing shows which of its values the page made. That
# departure can only ever withhold a clean verdict; it can never grant one.
# ---------------------------------------------------------------------------


class BlankLocator:
    """Playwright's locator over a page that draws nothing."""

    def locator(self, *args: Any, **kwargs: Any) -> "BlankLocator":
        return BlankLocator()

    def get_by_role(self, *args: Any, **kwargs: Any) -> "BlankLocator":
        return BlankLocator()

    def get_by_text(self, *args: Any, **kwargs: Any) -> "BlankLocator":
        return BlankLocator()

    def nth(self, index: int) -> "BlankLocator":
        return BlankLocator()

    @property
    def first(self) -> "BlankLocator":
        return BlankLocator()

    @property
    def last(self) -> "BlankLocator":
        return BlankLocator()

    def and_(self, *args: Any, **kwargs: Any) -> "BlankLocator":
        return BlankLocator()

    def or_(self, *args: Any, **kwargs: Any) -> "BlankLocator":
        return BlankLocator()

    def filter(self, *args: Any, **kwargs: Any) -> "BlankLocator":
        return BlankLocator()

    async def count(self) -> int:
        return 0

    async def is_visible(self, **kwargs: Any) -> bool:
        return False

    async def is_enabled(self, **kwargs: Any) -> bool:
        return False

    async def is_disabled(self, **kwargs: Any) -> bool:
        return False

    async def is_checked(self, **kwargs: Any) -> bool:
        return False

    async def is_editable(self, **kwargs: Any) -> bool:
        return False

    async def is_hidden(self, **kwargs: Any) -> bool:
        return True

    async def bounding_box(self, **kwargs: Any) -> None:
        return None

    async def wait_for(self, **kwargs: Any) -> None:
        raise TimeoutError("the blank page draws nothing to wait for")

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> None:
        return None

    async def evaluate_all(self, script: Any, arg: Any = None) -> list[Any]:
        return []

    async def inner_text(self, **kwargs: Any) -> str:
        return ""

    async def text_content(self, **kwargs: Any) -> str:
        return ""

    async def inner_html(self, **kwargs: Any) -> str:
        return ""

    async def input_value(self, **kwargs: Any) -> str:
        return ""

    async def get_attribute(self, name: str, **kwargs: Any) -> None:
        return None

    async def all_text_contents(self) -> list[str]:
        return []

    async def all_inner_texts(self) -> list[str]:
        return []

    async def all(self) -> list["BlankLocator"]:
        return []

    async def element_handle(self, **kwargs: Any) -> None:
        return None

    async def element_handles(self) -> list["BlankLocator"]:
        return []

    async def click(self, **kwargs: Any) -> None:
        raise NavigationAttempted("locator.click")

    async def fill(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("locator.fill")

    async def set_input_files(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("locator.set_input_files")

    async def select_option(self, *args: Any, **kwargs: Any) -> None:
        raise NavigationAttempted("locator.select_option")


class BlankPage(PlantedPage):
    """Playwright's page over a document that draws nothing.

    A :class:`PlantedPage` subclass so the harness finds it, counts its reads
    and resolves a paired Observation against it exactly as against the
    planted page; every read the planted page answers is overridden here --
    ``tests/test_readers_emit_no_page_string.py`` holds that no read of this
    page answers the plant.
    """

    def locator(self, *args: Any, **kwargs: Any) -> BlankLocator:  # type: ignore[override]
        return BlankLocator()

    def get_by_role(self, *args: Any, **kwargs: Any) -> BlankLocator:  # type: ignore[override]
        return BlankLocator()

    def get_by_text(self, *args: Any, **kwargs: Any) -> BlankLocator:  # type: ignore[override]
        return BlankLocator()

    def frame_locator(self, *args: Any, **kwargs: Any) -> BlankLocator:  # type: ignore[override]
        return BlankLocator()

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> None:  # type: ignore[override]
        return None

    async def evaluate_handle(self, script: Any, arg: Any = None) -> None:  # type: ignore[override]
        return None

    async def eval_on_selector(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        return None

    async def eval_on_selector_all(self, *args: Any, **kwargs: Any) -> list[Any]:  # type: ignore[override]
        return []

    async def content(self) -> str:  # type: ignore[override]
        return "<html><head></head><body></body></html>"

    async def title(self) -> str:  # type: ignore[override]
        return ""

    async def inner_text(self, *args: Any, **kwargs: Any) -> str:  # type: ignore[override]
        return ""

    async def text_content(self, *args: Any, **kwargs: Any) -> str:  # type: ignore[override]
        return ""

    async def query_selector(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        return None

    async def query_selector_all(self, *args: Any, **kwargs: Any) -> list[Any]:  # type: ignore[override]
        return []

    async def wait_for_selector(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        raise TimeoutError("the blank page draws nothing to wait for")


# ---------------------------------------------------------------------------
# THE FAILING PAGE -- what a library SAID while failing, as the only channel.
#
# Added 2026-09-24 (lane G). The page above answers in strings so a reader's
# COERCIONS can be measured. This one answers nothing: every read FAILS, and
# the failure's message carries :data:`RAISED_PLANT`. That models the leak
# class the error envelope's ruling names -- a failed request renders the
# request, ``int()`` quotes what it refused, a selector error quotes the
# selector, V8's JSON.parse quotes the input it choked on -- none of which the
# package composed.
#
# BECAUSE EVERY READ FAILS, NO READ CAN RETURN THE MARKER. So a reader whose
# RETURN VALUE carries it put an exception's text into its output, and nothing
# else could have. That is the whole design: one channel open, one marker.
#
# A RAISED exception carrying the marker is NOT this double's subject. That is
# the ``$.message`` channel, ruled at the raise by
# ``ERROR-MESSAGE-RULED-AT-THE-RAISE`` -- a library's own text is publishable
# there and the twelve ``dom.py`` raise sites were deliberately left carrying
# it. What the ruling forbids is the value arriving where it was not decided:
# a returned field, printed onward by a write gate's refusal.
# ---------------------------------------------------------------------------

#: What every failing read says. Distinct from :data:`PLANT` on purpose: an
#: ``Observation`` built on the ordinary page may carry PLANT legitimately, and
#: this hunt must not confuse the two. Not name-shaped, like
#: :data:`SYNTHETIC_ARGUMENT`.
RAISED_PLANT = "example-library-quoted-this"


class PlantedLibraryError(Exception):
    """A library call that failed and quoted text nobody here composed."""


#: The ACTIONS stay loud refusals; the one TIMER stays a no-op, because a
#: sleep does not fail. Everything else async on the ordinary doubles FAILS on
#: the failing ones -- derived from those classes below, not listed, so a read
#: added to :class:`PlantedPage` tomorrow is a failing read here the same day.
_NOT_A_READ = frozenset({
    "click", "fill", "set_input_files", "select_option", "goto", "close",
    "wait_for_timeout",
})


def _async_reads(cls: type) -> list[str]:
    import inspect

    return sorted(
        name
        for name, member in vars(cls).items()
        if inspect.iscoroutinefunction(member) and name not in _NOT_A_READ
    )


def _failing(qualified: str) -> Any:
    async def fail(self: Any, *args: Any, **kwargs: Any) -> Any:
        raise PlantedLibraryError(f"{qualified}: {RAISED_PLANT}")

    fail.__name__ = qualified.rsplit(".", 1)[-1]
    return fail


class RaisingLocator(PlantedLocator):
    """:class:`PlantedLocator` whose every read fails with the marker."""

    def locator(self, *args: Any, **kwargs: Any) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)

    def get_by_role(self, *args: Any, **kwargs: Any) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)

    def get_by_text(self, *args: Any, **kwargs: Any) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)

    def nth(self, index: int) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)

    @property
    def first(self) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)

    @property
    def last(self) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)

    def and_(self, *args: Any, **kwargs: Any) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)

    def or_(self, *args: Any, **kwargs: Any) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)

    def filter(self, *args: Any, **kwargs: Any) -> "RaisingLocator":
        return RaisingLocator(self._depth + 1)


class RaisingPage(PlantedPage):
    """:class:`PlantedPage` whose every read fails with the marker."""

    def locator(self, *args: Any, **kwargs: Any) -> RaisingLocator:
        return RaisingLocator()

    def get_by_role(self, *args: Any, **kwargs: Any) -> RaisingLocator:
        return RaisingLocator()

    def get_by_text(self, *args: Any, **kwargs: Any) -> RaisingLocator:
        return RaisingLocator()

    def frame_locator(self, *args: Any, **kwargs: Any) -> RaisingLocator:
        return RaisingLocator()


for _name in _async_reads(PlantedLocator):
    setattr(RaisingLocator, _name, _failing(f"locator.{_name}"))
for _name in _async_reads(PlantedPage):
    setattr(RaisingPage, _name, _failing(f"page.{_name}"))


def carries_the_raised_plant(obj: Any) -> list[str]:
    """Every place in ``obj`` holding what a failing library said."""
    from tests.leakwalk import walk

    return [path for path, text in walk(obj) if RAISED_PLANT in text]


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


def carries_the_plant_outside_records(obj: Any) -> tuple[list[str], int]:
    """``(places holding the plant OUTSIDE a people record, records seen)``.

    NAMES-AT-RUNTIME, applied by PEOPLE-DATA-MITIGATIONS: a people reader
    returns another member's words, and returns them ONLY inside a
    ``linkedin_server.people_data`` record's ENVELOPE -- a dict with exactly
    the declared keys, the marker's exact note and fields that rebuild into a
    valid record. Such a record is the declared channel and is not walked.
    EVERYTHING AROUND IT IS: a plant beside a record, in a key, in a widened
    record-shaped dict, in an error field or an exception, is still found. A
    dict that merely LOOKS like a record fails ``as_record`` and is walked
    like any other dict.

    HARDENED 2026-09-27 on lane G's cold verification, in two ways:

    * A record INSTANCE is not the declared channel, only its envelope: the
      server publishes an instance without the marker, so an instance is
      walked like any other value.
    * Outside a record the plant is found in ANY SPELLING that carries one of
      its words -- a first name alone, a slug, another case, a no-break
      space, an entity, a prefix -- not only verbatim. Each word of
      :data:`PLANT` is long and invented, so one found anywhere is the plant.
      (The plain hunt, :func:`carries_the_plant`, still matches verbatim; this
      one is consulted once the verbatim plant is known to be present.)
    """
    from linkedin_server.people_data import as_record
    from tests.leakwalk import walk

    records: list[Any] = []

    def is_record(value: Any) -> bool:
        if not isinstance(value, dict) or as_record(value) is None:
            return False
        records.append(value)
        return True

    hits = [
        path for path, text in walk(obj, skip=is_record) if carries_a_plant_word(text)
    ]
    return hits, len(records)


#: The plant's words, case-folded. See :func:`carries_the_plant_outside_records`.
PLANT_WORDS = tuple(word.casefold() for word in PLANT.split())


def carries_a_plant_word(text: str) -> bool:
    """Does ``text`` carry any word of the plant, in any case?"""
    folded = str(text).casefold()
    return any(word in folded for word in PLANT_WORDS)


#: The two verdict words the ratchet below turns on, shared by the reader guard
#: and the tool-envelope guard (both baselines store ``"<verdict>:<reason>"``,
#: so a verdict is compared by the part before the first colon).
RETURNS_TEXT_VERDICT = "returns_text"
RETURNS_RECORDS_VERDICT = "returns_records"


def _verdict_class(value: Any) -> str:
    return str(value).split(":", 1)[0].strip()


def text_ratchet(
    baseline: dict[str, str],
    live: dict[str, str],
    admitted: Mapping[str, Any] | None = None,
) -> list[str]:
    """What a live verdict table may not do against its committed baseline.

    THE LEGACY INVENTORY MAY SHRINK AND MAY NOT GROW (2026-09-24,
    PEOPLE-DATA-MITIGATIONS). Three problems, one line each, names only:

    * ``new text path``   -- live returns text outside records where the
      baseline does not say so: a page string leaving by a path that is not the
      declared record. Return people data through ``people_data`` records.
    * ``stale inventory`` -- the baseline says text and the live verdict is
      anything else: the inventory is larger than the truth; regenerate it so
      it shrinks.
    * ``lost records``    -- the baseline says records and the live verdict is
      anything else: a converted reader fell back.

    ``admitted`` names readers a RULING admitted to the inventory, each with
    its reason (2026-09-28: PEOPLE-DATA-MITIGATIONS binds OTHER members' data;
    his own profile's text, and aggregates that identify no one, are
    admitted). Only such a name may join; it is the one door, and the caller
    holds the table that says why.

    Names present on only one side are the callers' existing appeared/vanished
    checks, and are skipped here.
    """
    problems: list[str] = []
    for name in sorted(set(baseline) & set(live)):
        was, now = _verdict_class(baseline[name]), _verdict_class(live[name])
        if now == RETURNS_TEXT_VERDICT and was != RETURNS_TEXT_VERDICT:
            if admitted and name in admitted:
                continue
            problems.append(f"new text path: {name} ({was} -> {now})")
        elif was == RETURNS_TEXT_VERDICT and now != RETURNS_TEXT_VERDICT:
            problems.append(f"stale inventory: {name} ({was} -> {now})")
        elif was == RETURNS_RECORDS_VERDICT and now != RETURNS_RECORDS_VERDICT:
            problems.append(f"lost records: {name} ({was} -> {now})")
    return problems


def text_paths_a_baseline_may_not_record(
    baseline: dict[str, str],
    live: dict[str, str],
    admitted: Mapping[str, Any] | None = None,
) -> list[str]:
    """Names a baseline WRITER must refuse: live text outside records where the
    committed baseline does not already record text -- including names it does
    not record at all. So a new page-text path cannot be written into the
    inventory; it has to return records -- unless a ruling ``admitted`` it
    (see :func:`text_ratchet`)."""
    return sorted(
        name
        for name, verdict in live.items()
        if _verdict_class(verdict) == RETURNS_TEXT_VERDICT
        and _verdict_class(baseline.get(name, "")) != RETURNS_TEXT_VERDICT
        and not (admitted and name in admitted)
    )
