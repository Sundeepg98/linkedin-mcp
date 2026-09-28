"""A page double that answers locators FROM A PARSED HTML SKELETON.

WHAT THIS IS FOR. The reader-leak guard
(``tests/test_readers_emit_no_page_string.py``) drives readers with
:class:`tests.plantedpage.PlantedPage`, which answers every page read with the
plant and counts its reads. Some readers reach their success path only on a
page with STRUCTURE -- a ``main`` holding filter pills, a heading whose
ancestor holds its section's lines -- and some go on past a click. For those a
drive hands the reader a :class:`SkeletonPage`: a double OVER a planted page
that answers each locator from a committed, sanitised HTML skeleton
(LinkedIn's interface words kept, every member's text reduced to shape), puts
the plant where the skeleton shaped a member's text (``answer_text``), and
STANDS IN FOR A CLICK by moving to the document a capture shows after it
(``on_click``). Pure Python, standard library only: no browser.

## THE FIDELITY RULE, INHERITED

``tests/plantedpage.py`` states it: a double that answers what a page cannot
answer manufactures findings that cannot happen. So wherever PLAYWRIGHT
decides a behaviour, this double does what Playwright does, and each such
choice below was read off the driver bundled with the installed ``playwright``
package (1.63, ``driver/package/lib/coreBundle.js``) and its Python client
(``playwright/_impl/_locator.py``), not recalled:

* STRICTNESS. Every read that acts on one element is strict (the client
  passes ``strict=True``): several matches raise :class:`Error` naming the
  count, as Playwright's "strict mode violation" does; nothing uses the first.
* NO MATCH. ``get_attribute``, ``inner_text``, ``text_content``,
  ``is_enabled``, ``is_checked``, ``click`` and ``wait_for`` WAIT on a live
  page and then raise ``TimeoutError``. A skeleton cannot change while it
  waits, so this double raises :class:`TimeoutError` at once.
  ``is_visible`` is the exception, in Playwright and here: it does not wait,
  and no match answers ``False`` (``isVisibleInternal`` returns false when
  nothing resolves). ``count`` and ``element_handles`` are never strict.
* ORDER. A comma list is the union of its alternatives in DOCUMENT ORDER,
  de-duplicated (the ``is`` engine concatenates, then ``sortInDOMOrder``). A
  chained ``.locator`` queries each current match in turn and unions the
  results in that order, de-duplicated and NOT re-sorted
  (``InjectedScript.querySelectorAll``). For CSS that union is document order;
  for ``xpath=..`` over several matches it is the order of the children, as in
  Playwright.
* SCOPE. Under a chained locator the scope element itself never matches a
  compound, and no ancestor above it is considered (``_matchesSimple`` returns
  false for the scope; ``parentElementOrShadowHostInContext`` stops there).
  So ``loc.locator("div span")`` finds a span whose ``div`` ancestor lies
  strictly inside ``loc`` -- not ``loc`` itself, not above it.
* ``nth``. ``slice(nth, nth + 1)`` with ``-1`` meaning the last
  (``_queryNth``): past the end matches nothing; other negatives count from
  the end the way JavaScript's ``slice`` does.
* ``xpath=..``. The parent element. The XPath engine keeps element nodes only,
  so the parent of a top-level element -- the document -- matches nothing.
* ``wait_for``. Strict too, with Playwright's four states: ``attached``,
  ``detached``, ``visible`` (the default), ``hidden``.
* EXCEPTIONS. Playwright's ``TimeoutError`` derives from its own ``Error``,
  which derives from ``Exception`` -- NOT from the builtin ``TimeoutError``.
  This module mirrors that, and it matters twice: a reader's
  ``except Exception`` catches these exactly as it catches Playwright's; and
  on Python 3.11+ ``asyncio.TimeoutError`` IS the builtin, so the guard's
  ``except asyncio.TimeoutError`` (its drive-timeout clause) would misfile an
  escaped builtin as "timed out". This one cannot be misfiled.

Where the page's RENDERING would decide (innerText, visibility), there is no
layout here, and the brief's rules for a page with no author CSS apply; the
known divergences from a browser are listed at :func:`_inner_text`.

## THE DOCUMENT

:func:`parse` builds an :class:`Element` tree with ``html.parser``, tolerant
of unclosed tags exactly the way ``scripts/_build_people_search_skeleton.py``'s
``Tree`` is: an end tag closes the nearest open element of that name and
everything inside it; a stray end tag is ignored; ``<x/>`` is closed at once;
void elements never hold children. Unlike a browser there are no implied end
tags (``<p>`` inside ``<p>`` nests) and no synthesised ``html``/``body``.
Comments are dropped, and so are ``script`` and ``style`` elements WITH their
text. Whitespace-only text is KEPT (a browser keeps it, and ``innerText``
needs it between inline elements). Attribute names are lower-cased, the first
of a duplicated attribute wins, and a valueless attribute's value is ``""``.

## LAZINESS AND THE CLICK STAND-IN

A :class:`SkeletonLocator` stores its selector chain and resolves against
``page.document`` AT EVERY ACTION, never at creation, as Playwright's
locators do. ``view_switch.apply_and_restore`` builds its locators before its
first click; a stand-in that replaces ``page.document`` is read by them next.

``click`` on exactly one match calls ``on_click(locator, page)`` with a
locator PINNED to that element; the stand-in may replace ``page.document``
(or ``page.url``), or raise ``NavigationAttempted`` for a transition no
capture shows. It is synchronous, so it inspects what was pressed through
:meth:`SkeletonLocator.element` and :func:`text_of`. With no stand-in, the
click raises the planted page's own refusal, ``NavigationAttempted``.

## READS

``page.locator(...)`` counts ONE read on the planted page (it calls
``planted.locator`` and discards the answer); ``page.evaluate(...)`` counts
one. Chained ``.locator``, ``nth``, ``first``, ``last`` and every locator
read count nothing, as on the planted page. A selector refused by the grammar
is refused BEFORE its read is counted: a read the double could not answer is
not a read.

## REFUSALS A READER CAN SWALLOW, RECORDED

A reader wraps its reads in ``except Exception`` -- rightly, for a live page
-- and so it catches this double's ``ValueError`` for a selector outside the
grammar, or an ``AttributeError`` for a locator method this double does not
model, and turns it into its own answer. A drive would then read as a reader
that refused, when the truth is that the DOUBLE could not answer. So every
such refusal is also appended to :attr:`SkeletonPage.unmodelled`, and a drive
should assert it is empty after the reader returns. Reads this double hands
to the planted page instead of the skeleton -- an ``evaluate`` with no
registered stand-in, a page read such as ``get_by_role`` reached through the
fallback -- are appended to :attr:`SkeletonPage.planted_answers`: they
answered, with the plant, not from the skeleton.

Nothing this module raises or records quotes page text or a selector: a
refusal names its reason from a closed vocabulary, a failed read names its
method and a count.
"""

from __future__ import annotations

import inspect
import operator
import re
import string
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Callable, Iterator, Optional, Union

from tests.plantedpage import NavigationAttempted, PlantedLocator, PlantedPage

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class Error(Exception):
    """Playwright's ``Error``, as this double raises it.

    Raised for a strict-mode violation (a single-element read on a locator
    matching several), a ``wait_for`` state outside Playwright's four, and a
    click on an element no longer in the page's document. An ``Exception``,
    as Playwright's is, so a reader's own handler catches it exactly as it
    would catch the live one."""


class TimeoutError(Error):  # noqa: A001 -- Playwright's own name; NOT the builtin, see the module docstring
    """Playwright's ``TimeoutError``: a read that needs one element found none.

    A subclass of :class:`Error` and NOT of the builtin ``TimeoutError``,
    exactly as Playwright's is. Raised at once: a skeleton cannot change while
    a live page would be waiting."""


#: The message of every grammar refusal, as the brief fixes it.
GRAMMAR_REFUSAL = "selector outside the skeleton grammar"


class SelectorOutsideGrammar(ValueError):
    """``ValueError("selector outside the skeleton grammar")``.

    ``reason`` says WHICH construct was refused, from :data:`REFUSAL_REASONS`
    -- this module's own words, never a piece of the selector, so a refusal
    can be printed and logged without carrying anything a page drew."""

    def __init__(self, reason: str) -> None:
        super().__init__(GRAMMAR_REFUSAL)
        self.reason = reason


_R_NOT_A_STRING = "the selector is not a string"
_R_EMPTY = "an empty selector"
_R_ENGINE = "a selector engine other than css= and xpath="
_R_IMPLICIT_ENGINE = "an implicit xpath or text selector"
_R_XPATH = "an xpath other than .."
_R_COMBINATOR = "a combinator other than the descendant one"
_R_PSEUDO = "a pseudo-class or pseudo-element"
_R_CLASS_OR_ID = "a class or id selector"
_R_NAMESPACE = "a namespace"
_R_EMPTY_COMPOUND = "an empty compound"
_R_TYPE_AFTER = "a type selector after an attribute or another type"
_R_ATTRIBUTE_NAME = "an attribute name that is not an identifier"
_R_OPERATOR = "an attribute operator outside =, *= and ^="
_R_VALUE = "an attribute value that is neither quoted nor an identifier"
_R_STRING = "an unterminated string"
_R_ESCAPE = "an escape inside a string or identifier"
_R_FLAG = "an attribute flag other than i"
_R_BRACKET = "an unterminated attribute selector"
_R_CHARACTER = "an unexpected character"
_R_FILTER = "a locator filter argument (has, has_text, has_not, has_not_text)"

#: Every reason a grammar refusal can carry. Closed.
REFUSAL_REASONS: tuple[str, ...] = (
    _R_NOT_A_STRING, _R_EMPTY, _R_ENGINE, _R_IMPLICIT_ENGINE, _R_XPATH,
    _R_COMBINATOR, _R_PSEUDO, _R_CLASS_OR_ID, _R_NAMESPACE, _R_EMPTY_COMPOUND,
    _R_TYPE_AFTER, _R_ATTRIBUTE_NAME, _R_OPERATOR, _R_VALUE, _R_STRING,
    _R_ESCAPE, _R_FLAG, _R_BRACKET, _R_CHARACTER, _R_FILTER,
)

_NO_MATCH = (
    "no element in the skeleton matches this locator ({method}); a live page "
    "would wait and then raise TimeoutError, and a skeleton cannot change "
    "while it waits"
)
_STRICT = "strict mode violation: this locator resolved to {count} elements ({method})"
_STATE_NOT_REACHED = "the skeleton's match is not in the state wait_for asked for ({state})"
_BAD_STATE = "state: expected one of (attached|detached|visible|hidden)"
_DETACHED = "element is not attached to the DOM (click)"

# ---------------------------------------------------------------------------
# The document
# ---------------------------------------------------------------------------

#: The tag of the root :func:`parse` returns. Never matched by any selector.
DOCUMENT_TAG = "#document"

#: Elements that never hold children -- the people-search builder's ``VOID``.
VOID_ELEMENTS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
     "meta", "param", "source", "track", "wbr"}
)

#: Elements dropped at parse, with their text.
DROPPED_ELEMENTS = frozenset({"script", "style"})


class Text:
    """A text node: ``data`` and ``parent``. Its repr carries a length, never
    the text, so a failing assertion cannot print what a fixture draws."""

    __slots__ = ("data", "parent")

    def __init__(self, data: str, parent: Optional["Element"]) -> None:
        self.data = data
        self.parent = parent

    def __repr__(self) -> str:
        return f"<Text {len(self.data)} chars>"


class Element:
    """An element: ``tag``, ``attrs`` (names lower-cased), ``children``,
    ``parent``. Its repr carries the tag and sizes, never a value or a text."""

    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(
        self,
        tag: str,
        attrs: Optional[dict[str, str]] = None,
        parent: Optional["Element"] = None,
    ) -> None:
        self.tag = tag
        self.attrs: dict[str, str] = dict(attrs or {})
        self.children: list[Union["Element", Text]] = []
        self.parent = parent

    def __repr__(self) -> str:
        return f"<Element {self.tag} attrs={len(self.attrs)} children={len(self.children)}>"


def _attributes(pairs: list[tuple[str, Optional[str]]]) -> dict[str, str]:
    """The FIRST occurrence of a name wins, as in a browser; valueless is ""."""
    out: dict[str, str] = {}
    for name, value in pairs:
        if name not in out:
            out[name] = "" if value is None else value
    return out


class _Builder(HTMLParser):
    """The skeleton as it was serialised, closed the way the people-search
    builder's ``Tree`` closes it. See the module docstring.

    ONE TEXT NODE PER RUN, AS A BROWSER BUILDS IT. ``html.parser`` hands one
    run of text over in pieces (``a < b`` arrives as three calls), and the
    pieces are joined here into the one node a browser would hold. But a
    comment, a declaration or a dropped ``script``/``style`` stands BETWEEN
    two text nodes in a browser, and ``answer_text`` is called once per text
    node -- so text is never joined across one of those, only across the
    parser's own seams."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Element(DOCUMENT_TAG)
        self._current = self.root
        self._dropping: Optional[str] = None
        self._open_text: Optional[Text] = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._open_text = None
        if self._dropping is not None:
            return
        if tag in DROPPED_ELEMENTS:
            self._dropping = tag
            return
        element = Element(tag, _attributes(attrs), self._current)
        self._current.children.append(element)
        if tag not in VOID_ELEMENTS:
            self._current = element

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._open_text = None
        if self._dropping is not None or tag in DROPPED_ELEMENTS:
            return
        self._current.children.append(Element(tag, _attributes(attrs), self._current))

    def handle_endtag(self, tag: str) -> None:
        self._open_text = None
        if self._dropping is not None:
            if tag == self._dropping:
                self._dropping = None
            return
        walker: Optional[Element] = self._current
        while walker is not None and walker.tag != tag:
            walker = walker.parent
        if walker is not None and walker.parent is not None:
            self._current = walker.parent

    def handle_comment(self, data: str) -> None:
        self._open_text = None

    def handle_decl(self, decl: str) -> None:
        self._open_text = None

    def handle_pi(self, data: str) -> None:
        self._open_text = None

    def unknown_decl(self, data: str) -> None:
        self._open_text = None

    def handle_data(self, data: str) -> None:
        if self._dropping is not None or not data:
            return
        if self._open_text is not None:
            self._open_text.data += data
        else:
            self._open_text = Text(data, self._current)
            self._current.children.append(self._open_text)


def parse(html: str) -> Element:
    """The document root of ``html``, parsed as :class:`_Builder` says."""
    builder = _Builder()
    builder.feed(html)
    builder.close()
    return builder.root


def walk(node: Union[Element, Text]) -> Iterator[Union[Element, Text]]:
    """``node`` and every node under it, in document order."""
    stack: list[Union[Element, Text]] = [node]
    while stack:
        current = stack.pop()
        yield current
        if isinstance(current, Element):
            stack.extend(reversed(current.children))


def _descendant_elements(scope: Element) -> Iterator[Element]:
    """Every element strictly under ``scope``, in document order."""
    stack: list[Union[Element, Text]] = list(reversed(scope.children))
    while stack:
        node = stack.pop()
        if isinstance(node, Element):
            yield node
            stack.extend(reversed(node.children))


def text_of(node: Union[Element, Text]) -> str:
    """The node's descendant text, concatenated, RAW -- before ``answer_text``.

    For a click stand-in, which runs synchronously and has to decide which
    control was pressed from what the skeleton itself draws."""
    if isinstance(node, Text):
        return node.data
    return "".join(n.data for n in walk(node) if isinstance(n, Text))


def _text_content(element: Element, answer: Callable[[str], str]) -> str:
    return "".join(answer(n.data) for n in walk(element) if isinstance(n, Text))


# -- rendering, as far as a page with no author CSS decides it ---------------

#: Where ``innerText`` breaks a line: the brief's block-level elements, plus
#: the UA stylesheet's other block boxes it did not list (``hr``, ``legend``,
#: ``html``, ``body``, ``menu``, ``hgroup``, ``search``, and ``caption``,
#: whose table-caption box breaks a line too).
BLOCK_ELEMENTS = frozenset(
    {"div", "p", "section", "article", "header", "footer", "main", "nav",
     "aside", "ul", "ol", "li", "dl", "dt", "dd", "h1", "h2", "h3", "h4", "h5",
     "h6", "table", "tr", "form", "fieldset", "dialog", "figure",
     "figcaption", "blockquote", "pre", "address", "details", "summary",
     "hr", "legend", "html", "body", "menu", "hgroup", "search", "caption"}
)

#: CSS collapsible white space (space, tab, line breaks, form feed). NOT the
#: no-break space, which a browser keeps -- and Python's ``\s`` would eat.
_ASCII_WHITESPACE = " \t\n\r\f"
_COLLAPSIBLE = re.compile(r"[ \t\n\r\f]+")
_ASCII_LOWER = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)


def _ascii_lower(text: str) -> str:
    return text.translate(_ASCII_LOWER)


def _hidden_itself(element: Element) -> bool:
    """Not rendered by the UA stylesheet: ``[hidden]``, ``input[type=hidden]``."""
    if "hidden" in element.attrs:
        return True
    return element.tag == "input" and _ascii_lower(element.attrs.get("type", "")) == "hidden"


def _visible(element: Element) -> bool:
    """The brief's rule: False if it or an ancestor has ``hidden``, or it is
    ``input[type=hidden]``; else True. (A browser also needs a non-empty box:
    an empty element, a closed ``dialog`` or ``details`` body, and ``head``
    are invisible there and visible here.)"""
    if _hidden_itself(element):
        return False
    walker = element.parent
    while walker is not None:
        if "hidden" in walker.attrs:
            return False
        walker = walker.parent
    return True


def _enabled(element: Element) -> bool:
    """The brief's rule: False if it or an ancestor ``fieldset`` has
    ``disabled``, or it has ``aria-disabled="true"``. (Playwright applies
    ``disabled`` only to native form controls, exempts a disabled fieldset's
    first legend, and inherits ``aria-disabled`` from any ancestor for widget
    roles; none of that is modelled.)"""
    if "disabled" in element.attrs:
        return False
    if _ascii_lower(element.attrs.get("aria-disabled", "")) == "true":
        return False
    walker = element.parent
    while walker is not None:
        if walker.tag == "fieldset" and "disabled" in walker.attrs:
            return False
        walker = walker.parent
    return True


def _checked(element: Element) -> bool:
    """The brief's rule: a ``checked`` attribute, or ``aria-checked="true"``.
    (Playwright raises "Not a checkbox or radio button" for an element that
    is neither a checkable input nor of a checkable role; not modelled.)"""
    return "checked" in element.attrs or element.attrs.get("aria-checked") == "true"


def _inner_text(element: Element, answer: Callable[[str], str], *, rendered: bool) -> str:
    """The brief's approximation of ``innerText`` for a page with no author CSS.

    Text of descendants in order, each text node through ``answer`` first; a
    line break at the start and end of every :data:`BLOCK_ELEMENTS` element
    and at ``br``; collapsible white space collapsed to one space inside a
    line; lines stripped of it, empty lines dropped, joined with "\\n".

    Two rules beyond the brief's list, both the HTML standard's: a descendant
    that is not rendered (``[hidden]``, ``input[type=hidden]``) contributes
    nothing; and an element that is not itself rendered answers its
    ``textContent``, as the ``innerText`` getter's first step says.

    KNOWN DIVERGENCES from a browser: a ``p`` gets one line break, not two
    (and empty lines are dropped anyway); table cells are not separated by a
    tab; ``pre`` white space is collapsed; a script-less DOM (scripts are
    dropped at parse, so nothing they would have appended is here).
    """
    if not rendered:
        return _text_content(element, answer)
    lines: list[list[str]] = [[]]
    stack: list[tuple[Union[Element, Text], bool]] = [(element, False)]
    while stack:
        node, leaving = stack.pop()
        if isinstance(node, Text):
            lines[-1].append(answer(node.data))
            continue
        if leaving:
            if node.tag in BLOCK_ELEMENTS:
                lines.append([])
            continue
        if node is not element and _hidden_itself(node):
            continue
        if node.tag == "br":
            lines.append([])
            continue
        if node.tag in BLOCK_ELEMENTS:
            lines.append([])
        stack.append((node, True))
        stack.extend((child, False) for child in reversed(node.children))
    out: list[str] = []
    for pieces in lines:
        line = _COLLAPSIBLE.sub(" ", "".join(pieces)).strip(_ASCII_WHITESPACE)
        if line:
            out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# The selector grammar -- exactly what the readers this double serves use
# ---------------------------------------------------------------------------
#
#   selector   := "xpath=.." | [ "css=" ] list
#   list       := complex ( "," complex )*
#   complex    := compound ( WHITESPACE compound )*        the descendant combinator
#   compound   := ( tag | "*" )? attribute*                at least one of the two
#   attribute  := "[" name "]"
#               | "[" name ( "=" | "*=" | "^=" ) value ( "i" )? "]"
#   value      := '"' chars '"' | "'" chars "'" | identifier
#
# Anything else raises :class:`SelectorOutsideGrammar`. The readers, and the
# selector each one uses, are listed in ``tests/test_skeleton_page.py``
# (``READER_SELECTORS``), which also harvests every ``.locator(...)`` call in
# those readers and fails when one appears that the list does not hold.


@dataclass(frozen=True)
class _Attribute:
    name: str
    operator: Optional[str]  # None for presence, else "=", "*=" or "^="
    value: str
    fold: bool  # the " i" flag: ASCII case-insensitive comparison


@dataclass(frozen=True)
class _Compound:
    tag: Optional[str]  # None (no type selector), "*", or a lower-case tag name
    attributes: tuple[_Attribute, ...]


@dataclass(frozen=True)
class _Complex:
    compounds: tuple[_Compound, ...]  # joined by the descendant combinator


@dataclass(frozen=True)
class CssSelector:
    """A parsed comma list. ``alternatives`` in written order."""

    alternatives: tuple[_Complex, ...]


@dataclass(frozen=True)
class ParentSelector:
    """``xpath=..``: the parent element."""


ParsedSelector = Union[CssSelector, ParentSelector]

_IDENT_START = frozenset(string.ascii_letters + "_")
_IDENT_CHARS = frozenset(string.ascii_letters + string.digits + "_-")
#: Playwright reads ``name=body`` as an engine when ``name`` is made of these.
_ENGINE_PREFIX = re.compile(r"^([A-Za-z0-9_+:*-]+)=")


class _CssScanner:
    def __init__(self, text: str) -> None:
        self._text = text
        self._at = 0

    def _peek(self, offset: int = 0) -> Optional[str]:
        at = self._at + offset
        return self._text[at] if at < len(self._text) else None

    def _skip_whitespace(self) -> bool:
        start = self._at
        while self._peek() is not None and self._peek() in _ASCII_WHITESPACE:
            self._at += 1
        return self._at > start

    def selector_list(self) -> CssSelector:
        alternatives = [self._complex()]
        while self._peek() == ",":
            self._at += 1
            alternatives.append(self._complex())
        if self._peek() is not None:
            raise SelectorOutsideGrammar(_R_CHARACTER)
        return CssSelector(tuple(alternatives))

    def _complex(self) -> _Complex:
        self._skip_whitespace()
        compounds = [self._compound()]
        while True:
            self._skip_whitespace()
            char = self._peek()
            if char is None or char == ",":
                break
            if char in ">+~":
                raise SelectorOutsideGrammar(_R_COMBINATOR)
            compounds.append(self._compound())
        return _Complex(tuple(compounds))

    def _compound(self) -> _Compound:
        tag: Optional[str] = None
        attributes: list[_Attribute] = []
        char = self._peek()
        if char == "*":
            tag = "*"
            self._at += 1
        elif char is not None and char in _IDENT_START:
            tag = self._identifier().lower()
        while self._peek() == "[":
            attributes.append(self._attribute())
        char = self._peek()
        if char is not None and char not in _ASCII_WHITESPACE and char != ",":
            raise SelectorOutsideGrammar(self._reason_for(char))
        if tag is None and not attributes:
            raise SelectorOutsideGrammar(_R_EMPTY_COMPOUND)
        return _Compound(tag, tuple(attributes))

    @staticmethod
    def _reason_for(char: str) -> str:
        if char == ":":
            return _R_PSEUDO
        if char in ".#":
            return _R_CLASS_OR_ID
        if char in ">+~":
            return _R_COMBINATOR
        if char == "|":
            return _R_NAMESPACE
        if char == "\\":
            return _R_ESCAPE
        if char == "*" or char in _IDENT_START:
            return _R_TYPE_AFTER
        return _R_CHARACTER

    def _identifier(self) -> str:
        start = self._at
        if self._peek() == "-":
            self._at += 1
        char = self._peek()
        if char is None or char not in _IDENT_START:
            self._at = start
            return ""
        while self._peek() is not None and self._peek() in _IDENT_CHARS:
            self._at += 1
        if self._peek() == "\\":
            raise SelectorOutsideGrammar(_R_ESCAPE)
        return self._text[start:self._at]

    def _attribute(self) -> _Attribute:
        self._at += 1  # "["
        self._skip_whitespace()
        if self._peek() == "|" or (self._peek() == "*" and self._peek(1) == "|"):
            raise SelectorOutsideGrammar(_R_NAMESPACE)
        name = self._identifier()
        if not name:
            raise SelectorOutsideGrammar(_R_ATTRIBUTE_NAME)
        name = name.lower()
        self._skip_whitespace()
        char = self._peek()
        if char == "]":
            self._at += 1
            return _Attribute(name, None, "", False)
        if char is None:
            raise SelectorOutsideGrammar(_R_BRACKET)
        operator_: Optional[str] = None
        for candidate in ("*=", "^=", "="):
            if self._text.startswith(candidate, self._at):
                operator_ = candidate
                break
        if operator_ is None:
            if char in "$~|" and self._peek(1) == "=":
                raise SelectorOutsideGrammar(_R_OPERATOR)
            if char == "|":
                raise SelectorOutsideGrammar(_R_NAMESPACE)
            raise SelectorOutsideGrammar(_R_CHARACTER)
        self._at += len(operator_)
        self._skip_whitespace()
        char = self._peek()
        if char in ("'", '"'):
            value = self._string()
        else:
            value = self._identifier()
            if not value:
                if char is None:
                    raise SelectorOutsideGrammar(_R_BRACKET)
                raise SelectorOutsideGrammar(_R_VALUE)
        self._skip_whitespace()
        fold = False
        char = self._peek()
        if char is not None and char in "iI" and (
            self._peek(1) is None or self._peek(1) in _ASCII_WHITESPACE or self._peek(1) == "]"
        ):
            fold = True
            self._at += 1
            self._skip_whitespace()
        elif char is not None and char in "sS" and (
            self._peek(1) is None or self._peek(1) in _ASCII_WHITESPACE or self._peek(1) == "]"
        ):
            raise SelectorOutsideGrammar(_R_FLAG)
        if self._peek() is None:
            raise SelectorOutsideGrammar(_R_BRACKET)
        if self._peek() != "]":
            raise SelectorOutsideGrammar(_R_CHARACTER)
        self._at += 1
        return _Attribute(name, operator_, value, fold)

    def _string(self) -> str:
        quote = self._text[self._at]
        self._at += 1
        start = self._at
        while True:
            char = self._peek()
            if char is None or char == "\n":
                raise SelectorOutsideGrammar(_R_STRING)
            if char == "\\":
                raise SelectorOutsideGrammar(_R_ESCAPE)
            if char == quote:
                value = self._text[start:self._at]
                self._at += 1
                return value
            self._at += 1


def parse_selector(selector: Any) -> ParsedSelector:
    """``selector`` parsed, or :class:`SelectorOutsideGrammar`."""
    if not isinstance(selector, str):
        raise SelectorOutsideGrammar(_R_NOT_A_STRING)
    text = selector.strip()
    if not text:
        raise SelectorOutsideGrammar(_R_EMPTY)
    engine = _ENGINE_PREFIX.match(text)
    if engine is not None:
        name, body = engine.group(1), text[engine.end():].strip()
        if name == "xpath":
            if body == "..":
                return ParentSelector()
            raise SelectorOutsideGrammar(_R_XPATH)
        if name != "css":
            raise SelectorOutsideGrammar(_R_ENGINE)
        text = body
        if not text:
            raise SelectorOutsideGrammar(_R_EMPTY)
    elif text.startswith(("//", "..", '"', "'")):
        raise SelectorOutsideGrammar(_R_IMPLICIT_ENGINE)
    return _CssScanner(text).selector_list()


# -- matching ----------------------------------------------------------------


def _attribute_matches(element: Element, attribute: _Attribute) -> bool:
    actual = element.attrs.get(attribute.name)
    if actual is None:
        return False
    if attribute.operator is None:
        return True
    wanted = attribute.value
    if attribute.fold:
        actual, wanted = _ascii_lower(actual), _ascii_lower(wanted)
    if attribute.operator == "=":
        return actual == wanted
    if not wanted:
        return False  # CSS: an empty *= or ^= value represents nothing
    if attribute.operator == "*=":
        return wanted in actual
    return actual.startswith(wanted)  # "^="


def _compound_matches(element: Element, compound: _Compound, scope: Element) -> bool:
    if element is scope or element.tag == DOCUMENT_TAG:
        return False  # Playwright's _matchesSimple: the scope never matches
    if compound.tag not in (None, "*") and element.tag != compound.tag:
        return False
    return all(_attribute_matches(element, attribute) for attribute in compound.attributes)


def _ancestors_match(element: Element, compounds: tuple[_Compound, ...], index: int, scope: Element) -> bool:
    if index < 0:
        return True
    ancestor = None if element is scope else element.parent
    while ancestor is not None:
        if _compound_matches(ancestor, compounds[index], scope) and _ancestors_match(
            ancestor, compounds, index - 1, scope
        ):
            return True
        ancestor = None if ancestor is scope else ancestor.parent
    return False


def _complex_matches(element: Element, complex_: _Complex, scope: Element) -> bool:
    compounds = complex_.compounds
    return _compound_matches(element, compounds[-1], scope) and _ancestors_match(
        element, compounds, len(compounds) - 2, scope
    )


def _query(root: Element, parsed: ParsedSelector) -> list[Element]:
    """What ``parsed`` finds under ONE root, in document order."""
    if isinstance(parsed, ParentSelector):
        parent = root.parent
        return [parent] if parent is not None and parent.tag != DOCUMENT_TAG else []
    return [
        element
        for element in _descendant_elements(root)
        if any(_complex_matches(element, alternative, root) for alternative in parsed.alternatives)
    ]


def _union(roots: list[Element], parsed: ParsedSelector) -> list[Element]:
    """Playwright's chained part: each root's matches, in root order, de-duplicated."""
    seen: dict[int, Element] = {}
    for root in roots:
        for element in _query(root, parsed):
            seen.setdefault(id(element), element)
    return list(seen.values())


def _nth(elements: list[Element], index: int) -> list[Element]:
    """Playwright's ``_queryNth``: ``slice(nth, nth + 1)``, -1 the last."""
    if index == -1:
        index = len(elements) - 1
    return elements[index:index + 1]


def select(scope: Element, selector: str) -> list[Element]:
    """The elements ``selector`` finds under ``scope``, as a page locator would
    find them there. Counts no read. For a SCRIPT or CLICK stand-in, so that
    it asks the document through this engine rather than a hand-written walk."""
    return _query(scope, parse_selector(selector))


# ---------------------------------------------------------------------------
# The locator
# ---------------------------------------------------------------------------

#: The planted locator's refused actions this double re-raises, as the
#: planted locator raises them. (``click`` is modelled; see :meth:`click`.)
_PLANTED_REFUSALS = frozenset({"fill", "set_input_files", "select_option"})


class SkeletonLocator:
    """Playwright's locator over the skeleton, LAZY: resolved at every action."""

    def __init__(self, page: "SkeletonPage", steps: tuple[tuple[Any, ...], ...]) -> None:
        self._page = page
        self._steps = steps

    def __repr__(self) -> str:
        return f"<SkeletonLocator steps={len(self._steps)}>"

    # -- structure: no read, no resolution ----------------------------------
    def locator(self, selector: str, **kwargs: Any) -> "SkeletonLocator":
        """Descendants of each current match that match ``selector``."""
        self._page._refuse_filters(kwargs)
        parsed = self._page._parse(selector)
        return SkeletonLocator(self._page, self._steps + (("select", parsed),))

    def nth(self, index: int) -> "SkeletonLocator":
        return SkeletonLocator(self._page, self._steps + (("nth", operator.index(index)),))

    @property
    def first(self) -> "SkeletonLocator":
        return self.nth(0)

    @property
    def last(self) -> "SkeletonLocator":
        return self.nth(-1)

    # -- resolution ----------------------------------------------------------
    def _resolve(self) -> list[Element]:
        current: list[Element] = [self._page.document]
        for step in self._steps:
            kind = step[0]
            if kind == "pin":
                current = [step[1]]
            elif kind == "nth":
                current = _nth(current, step[1])
            else:
                current = _union(current, step[1])
        return current

    def _single(self, method: str) -> Element:
        found = self._resolve()
        if not found:
            raise TimeoutError(_NO_MATCH.format(method=method))
        if len(found) > 1:
            raise Error(_STRICT.format(count=len(found), method=method))
        return found[0]

    def element(self) -> Element:
        """The ONE element this locator resolves to now, synchronously -- for a
        click stand-in. Raises as every single-element read does: no match,
        :class:`TimeoutError`; several, :class:`Error` naming the count."""
        return self._single("element")

    # -- PLAYWRIGHT-TYPED ----------------------------------------------------
    async def count(self) -> int:
        return len(self._resolve())

    async def is_visible(self, **kwargs: Any) -> bool:
        """No match is ``False`` at once, as in Playwright (it does not wait)."""
        found = self._resolve()
        if not found:
            return False
        if len(found) > 1:
            raise Error(_STRICT.format(count=len(found), method="is_visible"))
        return self._page._rendered(found[0])

    async def is_enabled(self, **kwargs: Any) -> bool:
        return _enabled(self._single("is_enabled"))

    async def is_checked(self, **kwargs: Any) -> bool:
        return _checked(self._single("is_checked"))

    async def wait_for(self, state: Optional[str] = "visible", **kwargs: Any) -> None:
        """Playwright's four states, strict, answered at once."""
        state = "visible" if state is None else state
        if state not in ("attached", "detached", "visible", "hidden"):
            raise Error(_BAD_STATE)
        found = self._resolve()
        if len(found) > 1:
            raise Error(_STRICT.format(count=len(found), method="wait_for"))
        attached = bool(found)
        visible = attached and self._page._rendered(found[0])
        reached = {
            "attached": attached,
            "detached": not attached,
            "visible": visible,
            "hidden": not visible,
        }[state]
        if not reached:
            raise TimeoutError(_STATE_NOT_REACHED.format(state=state))

    async def element_handles(self) -> list["SkeletonLocator"]:
        """One locator PINNED to each current match, in order."""
        return [SkeletonLocator(self._page, (("pin", element),)) for element in self._resolve()]

    # -- PAGE-CONTROLLED: text through ``answer_text`` -----------------------
    async def get_attribute(self, name: str, **kwargs: Any) -> Optional[str]:
        """The value, ``answer_text``-ed for ``aria-label`` only; ``None`` if
        absent. Names are matched case-insensitively, as HTML's are."""
        element = self._single("get_attribute")
        key = str(name).lower()
        value = element.attrs.get(key)
        if value is None:
            return None
        return self._page._answer_text(value) if key == "aria-label" else value

    async def inner_text(self, **kwargs: Any) -> str:
        element = self._single("inner_text")
        return _inner_text(element, self._page._answer_text, rendered=self._page._rendered(element))

    async def text_content(self, **kwargs: Any) -> str:
        return _text_content(self._single("text_content"), self._page._answer_text)

    # -- THE ONE ACTION ------------------------------------------------------
    async def click(self, **kwargs: Any) -> None:
        """Resolve strictly, then hand the pinned element to the stand-in -- or,
        with none, raise the planted page's own refusal."""
        element = self._single("click")
        if not self._page._attached(element):
            raise Error(_DETACHED)
        stand_in = self._page._on_click
        if stand_in is None:
            # THE PLANTED PAGE'S OWN REFUSAL, reused rather than restated.
            await PlantedLocator().click(**kwargs)
            raise NavigationAttempted("locator.click")  # only if it ever stops refusing
        outcome = stand_in(SkeletonLocator(self._page, (("pin", element),)), self._page)
        if inspect.isawaitable(outcome):
            await outcome

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        if name in _PLANTED_REFUSALS:
            return getattr(PlantedLocator(), name)
        self._page.unmodelled.append(f"locator.{name}")
        raise AttributeError(f"SkeletonLocator does not model {name!r}")


# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------


class SkeletonPage:
    """A double OVER a :class:`PlantedPage`, answering from ``document``.

    ``document`` is a root from :func:`parse`; a click stand-in may replace it
    (and ``url``). ``answer_text`` maps every text node's data, and every
    ``aria-label``, before a reader sees it -- how a drive puts the plant where
    the skeleton shaped a member's text. ``scripts`` maps an ``evaluate``
    script to a stand-in ``(page, arg) -> answer`` (awaited if it returns an
    awaitable); any other script gets the planted page's answer. Every other
    attribute is the planted page's own: ``keyboard``, ``goto``, ``click``...
    which the planted page refuses.
    """

    def __init__(
        self,
        planted: Any,
        document: Element,
        *,
        url: str,
        answer_text: Callable[[str], str] = lambda text: text,
        on_click: Optional[Callable[["SkeletonLocator", "SkeletonPage"], Any]] = None,
        scripts: Optional[dict[str, Callable[["SkeletonPage", Any], Any]]] = None,
    ) -> None:
        self._planted = planted
        self.document = document
        self.url = url
        self._answer_text = answer_text
        self._on_click = on_click
        self._scripts = dict(scripts or {})
        #: Refusals a reader may have swallowed: the double could not answer.
        self.unmodelled: list[str] = []
        #: Reads answered by the planted page, not the skeleton.
        self.planted_answers: list[str] = []

    def __repr__(self) -> str:
        return "<SkeletonPage>"

    def locator(self, selector: str, **kwargs: Any) -> SkeletonLocator:
        """ONE read, counted on the planted page, whose answer is discarded."""
        self._refuse_filters(kwargs)
        parsed = self._parse(selector)
        self._planted.locator(selector)  # THE READ, counted
        return SkeletonLocator(self, (("select", parsed),))

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> Any:
        """ONE read, counted; a registered stand-in's answer, else the planted one."""
        planted_answer = await self._planted.evaluate(script, arg, **kwargs)  # THE READ, counted
        stand_in = self._scripts.get(script) if isinstance(script, str) else None
        if stand_in is None:
            self.planted_answers.append("page.evaluate")
            return planted_answer
        answer = stand_in(self, arg)
        if inspect.isawaitable(answer):
            answer = await answer
        return answer

    async def wait_for_timeout(self, timeout: Any = 0) -> None:
        return None

    async def wait_for_load_state(self, *args: Any, **kwargs: Any) -> None:
        return None

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        planted = object.__getattribute__(self, "_planted")
        if name in PlantedPage.READ_ENTRY_POINTS:
            self.planted_answers.append(f"page.{name}")
        return getattr(planted, name)

    # -- helpers for the locator ---------------------------------------------
    def _parse(self, selector: Any) -> ParsedSelector:
        try:
            return parse_selector(selector)
        except SelectorOutsideGrammar as refusal:
            self.unmodelled.append("selector: " + refusal.reason)
            raise

    def _refuse_filters(self, kwargs: dict[str, Any]) -> None:
        if kwargs:
            self.unmodelled.append("selector: " + _R_FILTER)
            raise SelectorOutsideGrammar(_R_FILTER)

    def _attached(self, element: Element) -> bool:
        walker = element
        while walker.parent is not None:
            walker = walker.parent
        return walker is self.document

    def _rendered(self, element: Element) -> bool:
        return self._attached(element) and _visible(element)
