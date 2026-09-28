"""Readers DRIVEN AS THEY SHIP, over the page a TRACKED fixture draws.

WHY THIS FILE EXISTS (2026-09-28, the orchestrator's order to lane G). Since
2026-09-27 the reader-leak guard, ``tests/test_readers_emit_no_page_string.py``,
counts a drive clean only when the reader's SUCCESS PATH ran: it read the page
and returned something that is not an empty shape and not a refusal -- and,
for a reader whose code reaches a people-record builder, a people record.
Driven by its signature alone, 22 readers could not earn that. Each was
triaged: a tracked fixture or skeleton draws the page its success path needs,
and its drive is HERE; or nothing tracked does, and the guard's
``WHAT_WOULD_DRIVE_IT`` names what would.

EVERY DRIVE HERE KEEPS THE THREE RULES the guard's own as-shipped drives keep:

1. A DOUBLE WRAPS THE PLANTED PAGE and answers ONLY what the cited fixture
   shows the page draws -- a script's answer, a selector's element, a count.
   Every other read is the planted page's own, so page text is still the
   plant, and a reader that carries it out is still convicted.
2. THE ARGUMENTS ARE THE SERVER'S -- its constants, its tables, the words a
   grant carries -- or the harness's own synthetic values. Never invented.
3. THE EVIDENCE IS CITED, AND CHECKED: each drive names its fixture and the
   markup that shows the shape, and reads the fixture before it runs. A drive
   whose fixture stopped drawing that shape RAISES (:func:`_drawn`) -- which
   the guard records as not driven, never as clean.

WHERE A SUCCESS PATH NEVER MEETS THE PLANT, the drive says so. The composer
readers compare the box with the CALLER's words and return a boolean; the id
join returns ids the fixture draws. Those drives prove the success path runs
and carries nothing else out; the signature variants, which hand the same
readers the plant, still run beside them and still convict a reader that
starts returning what it read.

TWO TABLES, AND ONLY THE FIRST EARNS ANYTHING:

* :data:`DRIVES` -- to the success path. The guard runs each beside its
  reader's signature variants (``AS_SHIPPED``).
* :data:`TO_THE_PRESS` -- as far as a press, which the planted page refuses by
  design. Run too, so every read BEFORE the press is hunted for the plant;
  each ends on the harness's refusal of the click, which the reader's own
  handler can no longer catch, and is recorded ``navigates (locator.click)``.

FOUR DRIVES WERE HELD OUT FOR A RULING, and are in :data:`DRIVES` since the
orchestrator gave it (2026-09-28 04:25): each reaches its reader's success
path and what comes back is page text outside a people record -- his own
profile's text, or an aggregate over his viewers that identifies no one.
Both kinds are admitted to the text inventory, each reader named with its
reason in the guard's ``ADMITTED_TEXT``; the one field that could name
another member (an endorsement line) was converted instead.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Optional

from tests.plantedpage import PLANT, PageAnswer

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _drawn(fixture: str, *shapes: str) -> str:
    """The fixture's text, once it is shown to still draw every one of
    ``shapes`` -- the markup a drive rests on. Otherwise this RAISES, so a
    drive built on a fixture that changed is not driven rather than clean."""
    text = (FIXTURES / fixture).read_text(encoding="utf-8")
    missing = [shape for shape in shapes if shape not in text]
    if missing:
        raise AssertionError(
            f"tests/fixtures/{fixture} no longer draws what this drive rests on: {missing}"
        )
    return text


class _Over:
    """A double OVER a planted object. Every attribute it does not define is
    the wrapped object's own -- so every read it does not answer is the
    planted page's, and is still counted as a read of it."""

    def __init__(self, wrapped: Any) -> None:
        self._wrapped = wrapped

    def __getattr__(self, name: str) -> Any:
        return getattr(self._wrapped, name)


def _planted_answer_with(**shown: Any) -> PageAnswer:
    """The planted page's answer to a script with ONLY ``shown`` keys
    replaced -- through ``get``, ``[]`` and the concrete storage alike, so
    ``dict(answer)`` keeps them. Every other key still answers the plant."""

    class _Answer(PageAnswer):
        def get(self, key: Any, default: Any = None) -> Any:
            return shown[key] if key in shown else super().get(key, default)

        def __getitem__(self, key: Any) -> Any:
            return shown[key] if key in shown else super().__getitem__(key)

    answer = _Answer()
    dict.update(answer, shown)
    return answer


# ---------------------------------------------------------------------------
# dom:read_any_save_control_label -- the save read-back
# ---------------------------------------------------------------------------


class _LabelledControlsInMain(HTMLParser):
    """``main button[aria-label], main a[aria-label]`` -- the labels, in
    document order, which is the order ``querySelectorAll`` answers in."""

    def __init__(self) -> None:
        super().__init__()
        self._in_main = 0
        self.labels: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag == "main":
            self._in_main += 1
        elif self._in_main and tag in ("button", "a"):
            label = dict(attrs).get("aria-label")
            if label is not None:
                self.labels.append(label)

    def handle_endtag(self, tag: str) -> None:
        if tag == "main" and self._in_main:
            self._in_main -= 1


#: The label ``tests/fixtures/job_detail_hydrated.html`` draws on its save
#: control -- ``dom.SAVE_LABELS_SEEN``'s OFF label.
SAVE_LABEL = "Save the job"


class _TheSaveControl(_Over):
    async def get_attribute(self, name: str, **kwargs: Any) -> Any:
        if name == "aria-label":
            return SAVE_LABEL
        return await self._wrapped.get_attribute(name, **kwargs)


class _TheSaveSweep(_Over):
    """The sweep's locator: the capture's count, its save control at the
    capture's position, every other control the planted one."""

    def __init__(self, wrapped: Any, count: int, at: int) -> None:
        super().__init__(wrapped)
        self._count = count
        self._at = at

    async def count(self) -> int:
        return self._count

    def nth(self, index: int) -> Any:
        control = self._wrapped.nth(index)
        return _TheSaveControl(control) if index == self._at else control


class _TheCapturedPosting(_Over):
    def __init__(self, wrapped: Any, count: int, at: int) -> None:
        super().__init__(wrapped)
        self._count = count
        self._at = at

    def locator(self, selector: Any, *args: Any, **kwargs: Any) -> Any:
        from linkedin_server import dom

        located = self._wrapped.locator(selector, *args, **kwargs)  # the read, counted
        if selector == dom.SAVE_SWEEP_SELECTOR:
            return _TheSaveSweep(located, self._count, self._at)
        return located


async def read_any_save_control_label_as_shipped(page: Any) -> Any:
    """``writes.perform``'s save read-back (the save family's "became"), on
    the posting ``tests/fixtures/job_detail_hydrated.html`` captures.

    THE SIGNATURE DRIVE: every planted ``aria-label`` is the plant, which
    carries no save word, so the sweep keeps no name and the reader returns
    ``None`` (``names[0] if names else None``) -- a read and an empty shape.

    THE FIXTURE: under ``<main>`` the sweep selector matches seven labelled
    controls, and the third is ``<button aria-label="Save the job">``. Both
    are counted off the fixture here, by the standard library's parser, in
    document order; ``tests/test_save_candidates_fixture.py`` derives every
    page it drives this reader over from the same capture.

    THE DOUBLE answers the sweep's count and the save control's label. The
    other six labels are the plant, so a reader that let a label past its
    save-word rule would return the plant, and the verdict would say so --
    shown (by lane G's child, 2026-09-28): with that rule replaced by "any
    text", this drive comes back ``returns_text``.
    """
    from linkedin_server import dom

    parser = _LabelledControlsInMain()
    parser.feed(_drawn("job_detail_hydrated.html", f'aria-label="{SAVE_LABEL}"'))
    if parser.labels.count(SAVE_LABEL) != 1:
        raise AssertionError("the capture's main no longer draws exactly one save control")
    at = parser.labels.index(SAVE_LABEL)
    return await dom.read_any_save_control_label(
        _TheCapturedPosting(page, len(parser.labels), at)
    )


# ---------------------------------------------------------------------------
# named_profile:composer_holds and threads:composer_holds -- words never sent
# ---------------------------------------------------------------------------


class _HoldsTheWords(_Over):
    """A composer locator whose first element's text is the typed words.
    Everything else -- its count included -- is the planted locator's."""

    def __init__(self, wrapped: Any, words: str) -> None:
        super().__init__(wrapped)
        self._words = words

    @property
    def first(self) -> "_HoldsTheWords":
        return _HoldsTheWords(self._wrapped.first, self._words)

    async def inner_text(self, **kwargs: Any) -> str:
        return self._words


class _TheBoxHoldsTheWords(_Over):
    """The planted page, whose one composer (``editor``) still holds the words."""

    def __init__(self, wrapped: Any, editor: str, words: str) -> None:
        super().__init__(wrapped)
        self._editor = editor
        self._words = words

    def locator(self, selector: Any, *args: Any, **kwargs: Any) -> Any:
        located = self._wrapped.locator(selector, *args, **kwargs)  # the read, counted
        return _HoldsTheWords(located, self._words) if selector == self._editor else located


def _typed_words(action: str) -> str:
    """The words ``writes.perform`` compares the box with for ``action``:
    ``_text_component_of(spec, grant.target)``, on the harness's own refusing
    grant, so the words are the harness's synthetic text -- never the plant."""
    from linkedin_server import writes

    from tests import refusinggrant

    spec = writes.spec_for_action(action)
    return writes._text_component_of(spec, refusinggrant.grant_for(spec).target)


async def named_profile_composer_holds_as_shipped(page: Any) -> Any:
    """``composer_holds`` as ``writes.perform`` calls it after a
    ``message_from_profile`` Send -- on the profile's composer, holding the
    words that were typed and never dispatched.

    THE SIGNATURE DRIVE: the one planted composer holds the plant, which is
    neither empty nor the argument, so the reader falls through to ``None``
    after two reads.

    THE FIXTURE: ``tests/fixtures/synthetic/named_profile.html``'s script
    draws ONE ``form.msg-form`` with ONE ``msg-form__contenteditable`` textbox
    and ONE ``msg-form__send-button`` of type submit; Send is enabled once the
    box holds words, and a submit on a form without ``data-dispatches`` returns
    before touching the box. So the words stay and Send stays enabled -- the
    reader's ``True``, and the only one of its answers that is not an empty
    shape (``False`` and ``None`` are).

    THE DOUBLE answers only the composer's text, with the typed words. The
    counts (1, 1) and Send's enabled state are the planted page's own, which
    is what the fixture draws in that state.
    """
    from linkedin_server import named_profile

    _drawn(
        "synthetic/named_profile.html",
        "msg-form__contenteditable", "msg-form__send-button", "data-dispatches",
    )
    words = _typed_words("message_from_profile")
    return await named_profile.composer_holds(
        _TheBoxHoldsTheWords(page, named_profile.COMPOSER_EDITOR_SELECTOR, words), words
    )


async def threads_composer_holds_as_shipped(page: Any) -> Any:
    """``composer_holds`` as ``writes.perform`` calls it after a
    ``send_reply`` press -- on the thread's reply box, holding the words that
    were typed and never dispatched.

    THE SIGNATURE DRIVE: as the profile composer's -- the plant in the box,
    ``None`` after two reads.

    THE FIXTURE: ``tests/fixtures/synthetic/messaging_thread.html`` draws one
    reply form (``#reply-editor``, ``#reply-send``) whose input listener
    enables Send once words are typed and whose submit, without
    ``data-dispatches``, leaves them in the box.
    ``tests/test_send_reply.py::test_a_reply_that_never_left_the_box_reports_not_sent``
    drives that fixture end to end to ``threads.REPLY_HELD``, which
    ``threads.reply_verdict`` returns only on this reader's ``True``.
    """
    from linkedin_server import threads

    _drawn(
        "synthetic/messaging_thread.html",
        'id="reply-editor"', 'id="reply-send"', "data-dispatches",
    )
    words = _typed_words("send_reply")
    return await threads.composer_holds(
        _TheBoxHoldsTheWords(page, threads.REPLY_EDITOR_SELECTOR, words), words
    )


# ---------------------------------------------------------------------------
# server:_attach_recipient_ids -- the Message buttons' ids, joined by slug
# ---------------------------------------------------------------------------

#: Where one viewer row ends and the next begins, in the capture's markup.
VIEWER_ROW_DIVIDER = '<hr role="presentation">'

#: A row's person link, as the capture draws it (already canonical).
VIEWER_LINK = re.compile(r'href="(https://www\.linkedin\.com/in/[A-Za-z0-9_%-]+/)"')

#: A Message anchor's id in the RAW markup, where the separator is ``&amp;``.
RECIPIENT_IN_MARKUP = re.compile(r"(?:\?|&amp;|&)recipient=([A-Za-z0-9_-]{1,64})")

#: The page script's climb from each Message anchor to its row, replayed on
#: the capture offline (the script's own climb and stop rule): five, and it
#: never leaves the row.
HOPS_ON_THE_CAPTURE = 5


class _DrawsTheMessageButtons(_Over):
    def __init__(self, wrapped: Any, answer: dict[str, Any]) -> None:
        super().__init__(wrapped)
        self._answer = answer

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> Any:
        from linkedin_server import dom

        answer = await self._wrapped.evaluate(script, arg, **kwargs)  # the read, counted
        return self._answer if script == dom.RECIPIENT_IDS_JS else answer


async def attach_recipient_ids_as_shipped(page: Any) -> Any:
    """``_attach_recipient_ids`` over the viewer rows of the Who's-Viewed-Me
    capture, ``tests/fixtures/profile_views_analytics.html``, returning what
    it WROTE -- each row's ``recipient_id``, in row order. The reader returns
    ``None`` by design; its work is the join.

    THE SIGNATURE DRIVE hands it ``rows=[]``, so the join iterates nothing,
    and the planted answer's recipient is the plant, which
    ``dom.is_recipient_id`` refuses: a read and ``None``.

    THE FIXTURE: four named viewer rows, each ending at LinkedIn's
    ``<hr role="presentation">`` and holding one person link; TWO of them draw
    a Message anchor carrying ``recipient=<id>``, the other two Connect and
    Follow. ``tests/test_recipient_ids_from_the_viewer_list.py`` runs the real
    script over the capture and pins that answer. Slugs and ids are READ OFF
    THE CAPTURE HERE, at run time, so no identifier is written in this file.

    THE DOUBLE answers only ``dom.RECIPIENT_IDS_JS``, one entry per Message
    anchor; it is this reader's only page read, so the plant cannot reach it
    on this drive -- the signature variant is the one that hands it the plant.
    Two buttons meet four rows: pairing by position would put an id on a
    Connect row, and the join by slug puts ``None`` there.
    """
    from linkedin_server import dom, server

    markup = _drawn("profile_views_analytics.html", VIEWER_ROW_DIVIDER)
    viewers: list[tuple[str, list[str]]] = []
    for block in markup.split(VIEWER_ROW_DIVIDER):
        links = VIEWER_LINK.findall(block)
        if len(links) == 1:
            viewers.append((links[0], RECIPIENT_IN_MARKUP.findall(block)))
    messageable = [(link, ids[0]) for link, ids in viewers if len(ids) == 1]
    if not messageable or len(messageable) == len(viewers):
        raise AssertionError(
            "the capture no longer draws both a messageable and an unmessageable viewer row"
        )
    answer = {
        "rows": [
            {
                "slug": re.search(dom.PERSON_HREF, link).group(1),
                "recipient": recipient,
                "hops": HOPS_ON_THE_CAPTURE,
                "left_the_row": False,
            }
            for link, recipient in messageable
        ],
        "buttons": sum(len(ids) for _link, ids in viewers),
    }
    rows: list[dict[str, Any]] = [{"person": {"link": link}} for link, _ids in viewers]
    await server._attach_recipient_ids(_DrawsTheMessageButtons(page, answer), rows)
    return [row.get("recipient_id") for row in rows]


# ---------------------------------------------------------------------------
# server:_profile_views_press_counters -- the counters a press is priced by
# ---------------------------------------------------------------------------


def _captured_headline() -> str:
    """The headline viewer count the analytics capture draws, read off it."""
    markup = _drawn("profile_views_analytics.html", "<p>Profile viewers</p>")
    found = re.search(r"<p>([0-9][0-9,]*)</p><p>Profile viewers</p>", markup)
    if found is None:
        raise AssertionError("the capture no longer draws its headline count")
    return found.group(1)


class _TheProfileViewsHeadline(_Over):
    """The planted page, whose insights script draws the capture's headline
    COUNT -- its label stays the plant, as page text does."""

    def __init__(self, wrapped: Any, headline: str) -> None:
        super().__init__(wrapped)
        self._headline = headline

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> Any:
        from linkedin_server import dom

        answer = await self._wrapped.evaluate(script, arg, **kwargs)  # the read, counted
        if script == dom.PROFILE_VIEWS_INSIGHTS_JS:
            return _planted_answer_with(metrics=[{"value": self._headline, "label": PLANT}])
        return answer


async def profile_views_press_counters_as_shipped(page: Any) -> Any:
    """The counter FACTORY, then one call of the closure it returns -- what
    every shipped caller does next (``_open_profile_views_filter_menus``,
    ``reveal.reveal``, ``view_switch.apply_and_restore``).

    THE SIGNATURE DRIVE calls the factory alone: a function, after no read.

    THE FIXTURE: ``tests/fixtures/profile_views_analytics.html`` draws the
    headline as ``<p>27</p><p>Profile viewers</p>``;
    ``tests/test_free_read_panels.py`` pins the insights script's answer on the
    hydrated render to ``{"value": "27", "label": "Profile viewers"}``.

    THE DOUBLE answers the insights script's ``metrics`` with that count and
    a label that is the plant; both nav badges are the planted page's and do
    not read, so they are left out of the set, as the closure leaves them.
    The plant IS on this path -- in the label -- and does not come out.
    """
    from linkedin_server import server

    read_counters = await server._profile_views_press_counters(
        _TheProfileViewsHeadline(page, _captured_headline())
    )
    return await read_counters()


# ---------------------------------------------------------------------------
# people_results:read_result_people -- the people search's result cards
# ---------------------------------------------------------------------------

#: The capture's member-link SHAPE, with the plant's words as its slug, so a
#: link that left a record would still be found by the plant-word hunt.
PEOPLE_CARD_LINK = "https://www.linkedin.com/in/" + "-".join(PLANT.lower().split()) + "/"

#: What the skeleton's title paragraph draws after the name link: a bullet
#: (U+2022, ``&#8226;`` in the markup) and the degree. Spelled by code point
#: so this file stays ASCII.
PEOPLE_DEGREE_DRAWN = chr(0x2022) + " 2nd"


class _Node(_Over):
    """One element of a result card as the skeleton draws it, reached as a
    HANDLE. It answers the structural queries the skeleton answers and
    nothing else: a query it was not built with RAISES (with a message that
    quotes no page), and the reader counts that failure by type, so a drive
    off this model cannot come back a record."""

    def __init__(
        self,
        wrapped: Any,
        *,
        href: Optional[str] = None,
        text_content: Optional[str] = None,
        text_after: str = "",
    ) -> None:
        super().__init__(wrapped)
        self._href = href
        self._text_content = text_content
        self._text_after = text_after
        self.one: dict[str, Optional["_Node"]] = {}
        self.many: dict[str, list["_Node"]] = {}

    async def get_attribute(self, name: str, **kwargs: Any) -> Any:
        if name == "href" and self._href is not None:
            return self._href
        return await self._wrapped.get_attribute(name, **kwargs)

    async def text_content(self, **kwargs: Any) -> Any:
        if self._text_content is not None:
            return self._text_content
        return await self._wrapped.text_content(**kwargs)

    async def inner_text(self, **kwargs: Any) -> Any:
        drawn = await self._wrapped.inner_text(**kwargs)
        return drawn + self._text_after if self._text_after else drawn

    async def query_selector(self, selector: str) -> Optional["_Node"]:
        if selector not in self.one:
            raise LookupError("a query the skeleton model was not built with")
        return self.one[selector]

    async def query_selector_all(self, selector: str) -> list["_Node"]:
        if selector not in self.many:
            raise LookupError("a query the skeleton model was not built with")
        return list(self.many[selector])


def _result_card(handle: Any) -> _Node:
    """One result card as ``people_search_results.html`` draws each of its
    three, over one planted handle."""
    from linkedin_server import people_results as pr

    card = _Node(handle, href=PEOPLE_CARD_LINK)
    name_link = _Node(handle.locator(pr.MEMBER_LINK), href=PEOPLE_CARD_LINK)
    title = _Node(handle.locator(pr.TITLE_BLOCK), text_after=PEOPLE_DEGREE_DRAWN)
    children = [_Node(handle.locator(pr.NESTED), text_content="") for _ in range(2)]
    lines = [_Node(handle.locator(pr.BESIDE_BLOCK)) for _ in range(pr.CAPTURED_LINES)]
    paragraphs = [_Node(handle.locator(pr.LINE_PARAGRAPH)) for _ in lines]

    card.one = {pr.ENCLOSING_RESULT: None, pr.MEMBER_LINK: name_link}
    name_link.one = {pr.TITLE_BLOCK: title}
    name_link.many = {pr.NESTED: children}
    title.one = {pr.BLOCK_OWNER: card, pr.BEFORE_BLOCK: None}
    title.many = {pr.BESIDE_BLOCK: lines}
    for line, paragraph in zip(lines, paragraphs):
        line.one = {pr.ANY_LINK: None}
        line.many = {pr.LINE_PARAGRAPH: [paragraph]}
    return card


class _TheResultList(_Over):
    async def element_handles(self) -> list[_Node]:
        return [_result_card(handle) for handle in await self._wrapped.element_handles()]


class _DrawsTheResultCards(_Over):
    def locator(self, selector: Any, *args: Any, **kwargs: Any) -> Any:
        from linkedin_server import people_results

        located = self._wrapped.locator(selector, *args, **kwargs)  # the read, counted
        return _TheResultList(located) if selector == people_results.RESULT_CARD else located


async def read_result_people_as_shipped(page: Any) -> Any:
    """``read_result_people`` as ``linkedin_people_search_shape`` calls it --
    on the page it was handed, no argument but the page -- over the planted
    page drawn as the skeleton's results list.

    THE SIGNATURE DRIVE: the card's ``href`` is the plant, not a member link,
    so ``_read_card`` skips it (``no_member_link``) and the reader returns its
    denominators and no person -- lane S's NO_RECORD.

    THE SKELETON: ``tests/fixtures/synthetic/people_search_results.html``
    (``scripts/_build_people_search_skeleton.py``). Each result is a member
    link holding a title paragraph whose same-href name link has two children
    carrying no text, followed by ``&#8226; 2nd``; the paragraph is the first
    of three siblings, the two after it each one paragraph and no link; and
    nothing wraps a card. ``tests/test_people_search_names.py::
    test_the_reader_returns_each_result_as_a_person`` runs this reader over
    it and asserts three people, every headline read, degree ``2nd``.

    THE DOUBLE answers the STRUCTURE (which element each of the reader's own
    query constants finds, or that it finds none), each ``href``, the degree
    drawn after the name, and the name link's two empty children. The NAME
    and the HEADLINE are the plant, every visibility the planted ``True``, and
    the number of cards the planted page's one: so the record that comes back
    carries the plant, inside the record, where the rule says it may.
    """
    from linkedin_server import people_results

    _drawn(
        "synthetic/people_search_results.html",
        "&#8226; 2nd", 'href="https://www.linkedin.com/in/',
    )
    return await people_results.read_result_people(_DrawsTheResultCards(page))


# ---------------------------------------------------------------------------
# profile_editor:read_premium_badge -- the badge row, by counts
# ---------------------------------------------------------------------------

#: ``tests/fixtures/synthetic/intro_editor_switches.html``
#: (``scripts/_build_intro_editor_switches_fixture.py``): the markup this
#: drive's counts rest on, each with how many times the fixture draws it.
INTRO_EDITOR_MARKUP = (
    ('<dialog open aria-labelledby="intro-dialog-header">', 1),
    ('<div data-testid="lazy-column"><div><p>Placeholder section</p>', 1),
    ('<button type="button">Save</button>\n</dialog>', 1),
    ('<div role="switch" aria-checked="true" tabindex="0" aria-label="Tap to toggle setting">', 2),
    ('<label for="intro-switch-1"></label>'
     '<input role="switch" type="checkbox" checked="" id="intro-switch-1">', 1),
    ('<label for="intro-switch-2"></label>'
     '<input role="switch" type="checkbox" checked="" id="intro-switch-2">', 1),
    ("<p>Placeholder setting A</p>", 1),
    ("<p>Placeholder setting B</p>", 1),
)


def _the_intro_editor() -> str:
    """The fixture's text, once it is shown to draw exactly the transcribed
    row: one dialog anchored by one Save, one row, two switch blocks in the
    recorded order -- and no control this drive did not transcribe."""
    markup = _drawn("synthetic/intro_editor_switches.html")
    for snippet, times in INTRO_EDITOR_MARKUP:
        if markup.count(snippet) != times:
            raise AssertionError("intro_editor_switches.html no longer draws the transcribed row")
    if markup.count('type="checkbox"') != 2 or markup.count("<button") != 1:
        raise AssertionError("intro_editor_switches.html draws controls this drive did not transcribe")
    if markup.index("Placeholder setting A") > markup.index("Placeholder setting B"):
        raise AssertionError("intro_editor_switches.html's blocks are no longer in the recorded order")
    return markup


class _CountsAs(_Over):
    def __init__(self, wrapped: Any, drawn: int) -> None:
        super().__init__(wrapped)
        self._drawn = drawn

    async def count(self) -> int:
        return self._drawn


class _TheBadgeRowDialog(_Over):
    """The editor dialog, whose OTHER block carries no title."""

    def __init__(self, wrapped: Any, untitled: str) -> None:
        super().__init__(wrapped)
        self._untitled = untitled

    def locator(self, selector: Any, *args: Any, **kwargs: Any) -> Any:
        inner = self._wrapped.locator(selector, *args, **kwargs)
        return _CountsAs(inner, 0) if selector == self._untitled else inner


class _TheIntroEditor(_Over):
    def __init__(self, wrapped: Any, untitled: str) -> None:
        super().__init__(wrapped)
        self._untitled = untitled

    def locator(self, selector: Any, *args: Any, **kwargs: Any) -> Any:
        from linkedin_server import profile_editor

        located = self._wrapped.locator(selector, *args, **kwargs)  # the read, counted
        if selector == profile_editor._EDITOR_DIALOG:
            return _TheBadgeRowDialog(located, self._untitled)
        return located


async def read_premium_badge_as_shipped(page: Any) -> Any:
    """``read_premium_badge`` as the badge write reads it -- ``page`` and
    nothing else -- on the intro editor
    ``tests/fixtures/synthetic/intro_editor_switches.html`` draws.

    THE SIGNATURE DRIVE: every planted count is 1, so BOTH of the badge row's
    blocks count the title, and the reader returns its
    ``4_title_not_on_exactly_one_block`` refusal after two reads.

    THE FIXTURE draws the dialog, its one Save, the one ``lazy-column`` row
    and its two setting blocks, each a checked unnamed switch in an
    ``aria-checked`` wrapper -- checked here, byte for byte, at every drive.
    Its block titles are the builder's PLACEHOLDERS: WHICH block carries the
    badge's title is the capture's identification, recorded in the builder's
    docstring and in ``profile_editor.INTRO_SWITCH_IDENTITIES`` -- the world
    ``tests/test_premium_badge.py::test_the_reader_returns_counts_positions_and_states_only``
    builds from this fixture and reads with this reader, asserting it
    aimable, the badge at position 2, both switches on.

    THE DOUBLE answers one count: the title on the OTHER block, 0. Every other
    count is the planted page's own 1, which is the fixture's. The reader asks
    counts and nothing else, so no page string can reach what it returns: the
    drive shows its success path runs and returns counts, positions, states
    and a selector built from its constants.
    """
    from linkedin_server import profile_editor

    _the_intro_editor()
    badge = profile_editor.INTRO_SWITCH_IDENTITIES.index("profile_premium_badge")
    if len(profile_editor.PREMIUM_BADGE_ROW_BLOCKS) != 2 or badge not in (0, 1):
        raise AssertionError("the badge row is no longer two blocks")
    other = profile_editor.PREMIUM_BADGE_ROW_BLOCKS[1 - badge]
    untitled = "css=" + other + profile_editor._BADGE_TITLED
    return await profile_editor.read_premium_badge(_TheIntroEditor(page, untitled))


# ---------------------------------------------------------------------------
# TO THE PRESS: press:disclose, share_link:copy_own_post_link
# ---------------------------------------------------------------------------


class _AtTheAddress(_Over):
    """The planted page at an address the tool itself loads. ``url`` is not
    a read: it is where the harness put the page."""

    def __init__(self, wrapped: Any, url: str) -> None:
        super().__init__(wrapped)
        self.url = url


class _TheProfileViewsPage(_AtTheAddress):
    """``/analytics/profile-views/``, whose insights script draws the
    capture's headline count (its label the plant).

    THE COUNT IS READ OFF THE CAPTURE BY THE DRIVE, BEFORE THE READER RUNS,
    and handed in. Read here, inside ``evaluate``, a capture that stopped
    drawing it raised INSIDE the counter reader's own ``except Exception``,
    which swallowed it: on a broken fixture the disclose drive went on to
    its click and the reveal drive came back refused, neither raising
    (2026-09-28, the premise control). A premise checked inside a double is
    checked inside the reader's handlers."""

    def __init__(self, wrapped: Any, url: str, headline: str) -> None:
        super().__init__(wrapped, url)
        self._headline = headline

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> Any:
        from linkedin_server import dom

        answer = await self._wrapped.evaluate(script, arg, **kwargs)  # the read, counted
        if script == dom.PROFILE_VIEWS_INSIGHTS_JS:
            return _planted_answer_with(metrics=[{"value": self._headline, "label": PLANT}])
        return answer


def _profile_views_address() -> str:
    from linkedin_server import config

    return f"{config.BASE_URL}/analytics/profile-views/"


async def disclose_to_the_press(page: Any) -> Any:
    """``press.disclose`` as ``linkedin_who_viewed_me(open_filter_menus=True)``
    presses a filter pill -- ``shape="[aria-expanded]"``, scoped to ``main``,
    priced by the server's own counter reader -- on the page the tool loads.

    THE SIGNATURE DRIVE: ``check_shape`` refuses the synthetic shape before
    any read.

    AS FAR AS THE PRESS: the candidate count, the control's state, the
    witness, the open-moment reading and the counters are all read; then the
    click, which the planted locator refuses. (Before 2026-09-28
    ``disclose``'s own handler turned that into ``press_failed`` and the drive
    read as clean.) Nothing after the press runs offline.

    WHAT NO TRACKED FIXTURE SHOWS, said: the PILL. Both profile-views captures
    draw no ``<main>`` and no ``[aria-expanded]``; the one candidate here is
    the planted page's own, at ``disclose``'s default index 0. The headline
    is the capture's (``<p>27</p><p>Profile viewers</p>``), answered so the
    counters are in the state the tool guarantees before it ever presses.
    """
    from linkedin_server import press, server

    at = _TheProfileViewsPage(page, _profile_views_address(), _captured_headline())
    counter_reader = await server._profile_views_press_counters(at)
    return await press.disclose(
        at,
        shape="[aria-expanded]",
        index=0,
        read_counters=counter_reader,
        reading=server.PROFILE_VIEWS_MENU_READING,
        scope="main",
    )


class _ItsMain(_Over):
    def __init__(self, wrapped: Any, selector: str, answer: Callable[[Any], Any]) -> None:
        super().__init__(wrapped)
        self._selector = selector
        self._answer = answer

    def locator(self, selector: Any, *args: Any, **kwargs: Any) -> Any:
        inner = self._wrapped.locator(selector, *args, **kwargs)
        return self._answer(inner) if selector == self._selector else inner


#: ``tests/fixtures/synthetic/own_post_menu.html``: ``main [aria-expanded]``
#: draws the decoy toggle, then the trigger its script appends.
OWN_POST_DISCLOSURES = 2
OWN_POST_TRIGGER_AT = 1
OWN_POST_TRIGGER_LABEL = "Open control menu for post"


class _TheTrigger(_Over):
    async def get_attribute(self, name: str, **kwargs: Any) -> Any:
        if name == "aria-label":
            return OWN_POST_TRIGGER_LABEL
        return await self._wrapped.get_attribute(name, **kwargs)


class _ItsDisclosures(_Over):
    async def count(self) -> int:
        return OWN_POST_DISCLOSURES

    def nth(self, index: int) -> Any:
        control = self._wrapped.nth(index)
        return _TheTrigger(control) if index == OWN_POST_TRIGGER_AT else control


class _TheOwnPostPermalink(_AtTheAddress):
    def locator(self, selector: Any, *args: Any, **kwargs: Any) -> Any:
        located = self._wrapped.locator(selector, *args, **kwargs)  # the read, counted
        if selector == "main":
            return _ItsMain(located, "[aria-expanded]", _ItsDisclosures)
        return located


async def copy_own_post_link_to_the_press(page: Any) -> Any:
    """``copy_own_post_link`` as ``linkedin_own_item_link`` takes it, on the
    post's own permalink, priced by ``read_item_price`` as the tool prices it.

    THE SIGNATURE DRIVE: ``activity_digits`` is annotated ``Any``, the harness
    hands it a page double, and the reader returns ``bad_activity_id`` before
    any page contact.

    AS FAR AS THE PRESS: the post's address, exactly one ``main
    [aria-expanded]`` control whose label starts with the menu prefix, and the
    two named counters (which already read as integers on the planted page);
    then the trigger's click, refused. The menu, the owner check, the copy
    and the ``link`` -- the one page string this reader exists to return --
    are not reached.

    THE FIXTURE: ``tests/fixtures/synthetic/own_post_menu.html``. Its
    ``<main>`` holds ``#decoy-toggle[aria-expanded]`` and ``#post-root``, into
    which its script appends the trigger, ``aria-label="Open control menu for
    post"``: two controls, the trigger second. Its synthetic ``POST_ID`` is
    the id ``tests/test_share_link.py`` uses.
    """
    from linkedin_server import share_link

    markup = _drawn(
        "synthetic/own_post_menu.html", 'id="decoy-toggle"', f'"{OWN_POST_TRIGGER_LABEL}"'
    )
    found = re.search(r'POST_ID = "([0-9]+)"', markup)
    if found is None:
        raise AssertionError("the fixture no longer declares its synthetic post id")
    digits = found.group(1)
    at = _TheOwnPostPermalink(page, share_link.post_url(digits))

    async def own_item_counters() -> Any:
        return await share_link.read_item_price(at)

    return await share_link.copy_own_post_link(
        at, activity_digits=digits, read_counters=own_item_counters
    )


# ---------------------------------------------------------------------------
# ADMITTED BY THE RULING OF 2026-09-28: success paths that return page text
# outside a record -- his own profile's, or an aggregate that names no one
# ---------------------------------------------------------------------------

#: The skill cards ``tests/fixtures/profile_skills.html`` draws, anchored on
#: the links ``dom.PROFILE_DETAIL_ENTRY_HREF["skills"]`` matches.
SKILLS_DETAIL_LINK = "/details/skills/edit/forms/"


class _TheSkillsDetailsPage(_Over):
    """The planted page whose card harvest answers in the script's own SHAPE
    -- a list of card records, one per card the capture draws -- each card
    the planted page's own answer, so every field of it is the plant."""

    def __init__(self, wrapped: Any, cards: int) -> None:
        super().__init__(wrapped)
        self._cards = cards

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> Any:
        from linkedin_server import dom

        answer = await self._wrapped.evaluate(script, arg, **kwargs)  # the read, counted
        if script == dom.HARVEST_LINKED_CARDS_JS:
            return [PageAnswer() for _ in range(self._cards)]
        return answer


async def read_profile_detail_entries_as_shipped(page: Any) -> Any:
    """``read_profile_detail_entries`` as ``linkedin_my_profile`` calls it
    with its own defaults (``include_skills=True``): section "skills", on
    ``/in/me/details/skills/``.

    THE SIGNATURE DRIVE: the synthetic section is refused (``unknown_section``)
    before any read. With "skills" and no double it raises, because the
    planted page answers the harvest script with a mapping, not a list.

    THE FIXTURE: ``tests/fixtures/profile_skills.html`` draws six skill cards;
    ``tests/test_sdui_surfaces_fixture.py`` runs the real harvest and the real
    reader over it and asserts six records and the six skill names.

    WHAT COMES BACK: ``entries`` is card text, as plain strings, outside any
    people record -- ``returns_text``. It is the reader's success path, it
    predates the 2026-09-24 inventory (added 2026-09-03), and the inventory
    missed it because nothing drove it. HIS OWN PROFILE'S TEXT -- his skills,
    and the lines under them -- so ADMITTED by the ruling of 2026-09-28; the
    one line that could name another member, an endorsement's, was converted.
    """
    from linkedin_server import dom

    markup = _drawn("profile_skills.html", SKILLS_DETAIL_LINK)
    cards = markup.count(SKILLS_DETAIL_LINK)
    return await dom.read_profile_detail_entries(
        _TheSkillsDetailsPage(page, cards), section="skills"
    )


#: The intro editor's four controls, as ``dom.EDITOR_FIELDS_JS`` and
#: ``dom.EDITOR_VALUES_JS`` draw them on the fixture: the city field
#: (label-for), two unnamed switches, and Save -- the one anchor, inside the
#: one dialog. The city field's LABEL and VALUE are free page text the two
#: readers PUBLISH, so here they are the plant; Save is the anchor's own name
#: (``dom.EDITOR_ANCHOR_NAME``), a closed word the anchor rule counts.
_EDITOR_CONTROLS: tuple[dict[str, Any], ...] = (
    {"name": PLANT, "name_source": "label-for", "tag": "input", "type": "text",
     "role": None, "checked": None, "value": PLANT, "value_source": "native"},
    {"name": "", "name_source": "none", "tag": "input", "type": "checkbox",
     "role": "switch", "checked": True, "value": None, "value_source": "state_not_value"},
    {"name": "", "name_source": "none", "tag": "input", "type": "checkbox",
     "role": "switch", "checked": True, "value": None, "value_source": "state_not_value"},
    {"name": "Save", "name_source": "text", "tag": "button", "type": None,
     "role": None, "checked": None, "value": None, "value_source": "none"},
)


def _editor_reading(values: bool) -> PageAnswer:
    """The editor script's answer on the fixture: one anchor, a dialog, the
    four controls -- each ONLY the keys its reader projects; every other key
    the planted page's own."""
    controls = []
    for index, control in enumerate(_EDITOR_CONTROLS):
        shown: dict[str, Any] = {
            key: control[key] for key in ("name", "name_source", "tag", "type", "role")
        }
        if values:
            value = control["value"]
            shown.update(
                index=index, value=value, value_source=control["value_source"],
                value_chars=None if value is None else len(value), value_truncated=False,
            )
        else:
            checked = control["checked"]
            shown.update(
                disabled=False, checked=checked,
                checked_source="native" if checked is not None else "none",
                required=False if control["tag"] == "input" else None,
                has_href=False,
            )
        controls.append(_planted_answer_with(**shown))
    return _planted_answer_with(
        anchor_controls=1, container_kind="dialog", controls_inside=len(controls),
        truncated=False, controls=controls,
    )


class _TheEditorScript(_Over):
    def __init__(self, wrapped: Any, script: str, answer: PageAnswer) -> None:
        super().__init__(wrapped)
        self._script = script
        self._answer = answer

    async def evaluate(self, script: Any, arg: Any = None, **kwargs: Any) -> Any:
        answer = await self._wrapped.evaluate(script, arg, **kwargs)  # the read, counted
        return self._answer if script == self._script else answer


async def read_self_owned_editor_fields_as_shipped(page: Any) -> Any:
    """``read_self_owned_editor_fields`` as the Save gate calls it (the
    default projection) on the intro editor the fixture draws.

    THE SIGNATURE DRIVE: the planted answer's anchor count is the plant,
    ``as_count`` makes it 0, and the reader refuses ``no_anchor``.

    THE FIXTURE: ``tests/fixtures/synthetic/intro_editor_switches.html``'s one
    dialog holds four controls -- ``<label for="intro-city">City</label>`` on
    a text input, two unnamed checked switches, and ``<button>Save</button>``;
    ``tests/test_intro_editor_switches.py`` reads it through this reader
    (via ``profile_editor.read_save_gate``) in a browser.

    WHAT COMES BACK: the reader publishes a control's LABEL ungated, under the
    self-owned-container ruling; with the label the plant, that is page text
    outside a record at ``$.fields[0].name``. The inventory recorded this
    reader clean on its ``no_anchor`` refusal and never saw it. (The write
    path's ``include_dom_id=True`` call adds the element's id.) HIS OWN
    EDITOR'S LABELS, so ADMITTED by the ruling of 2026-09-28.
    """
    from linkedin_server import dom

    _the_intro_editor()
    return await dom.read_self_owned_editor_fields(
        _TheEditorScript(page, dom.EDITOR_FIELDS_JS, _editor_reading(values=False))
    )


async def read_self_owned_editor_values_as_shipped(page: Any) -> Any:
    """``read_self_owned_editor_values`` as the restore path calls it, on the
    same editor.

    THE SIGNATURE DRIVE: ``no_anchor``, as the fields reader's.

    THE FIXTURE: the same four controls; the city input holds a value
    (``value="Placeholdertown"``), each switch is ``state_not_value``.

    WHAT COMES BACK: the reader returns a field's VALUE verbatim -- the restore
    path's whole purpose -- and its label ungated; with both the plant, page
    text outside a record at ``$.fields[0]``. WHAT HE TYPED INTO HIS OWN
    PROFILE, so ADMITTED by the ruling of 2026-09-28.
    """
    from linkedin_server import dom

    _the_intro_editor()
    return await dom.read_self_owned_editor_values(
        _TheEditorScript(page, dom.EDITOR_VALUES_JS, _editor_reading(values=True))
    )


# ---------------------------------------------------------------------------
# THE PROFILE-VIEWS PAGE, AS ITS SKELETONS DRAW IT (the order of 2026-09-28 04:25)
# ---------------------------------------------------------------------------
#
# Four committed skeletons of /analytics/profile-views/, each built by
# ``scripts/_build_profile_views_skeleton.py`` from one capture of the live
# lane (``_audit/2026-09-23-live-lane-session-1.md``): LinkedIn's interface
# words kept, every other member's text reduced to SHAPE (every letter x or
# X). The drives read them through ``tests.skeleton_page``: a double that
# answers locators from the parsed skeleton, counts each page read on the
# planted page beneath it, answers another member's shaped text as the plant,
# and leaves every script it has no stand-in for to the planted page.

#: The skeletons, by the state of the page each capture shows, and the
#: capture each was built from.
VIEWS_CLOSED = "synthetic/profile_views_closed.html"
VIEWS_PILL_OPEN = "synthetic/profile_views_pill_open.html"
VIEWS_VERIFY = "synthetic/profile_views_verify.html"
VIEWS_REVEALED = "synthetic/profile_views_revealed.html"
VIEWS_SOURCES: dict[str, str] = {
    VIEWS_CLOSED: "pv-closed.html -- Entry 3's load, every filter pill closed",
    VIEWS_PILL_OPEN: "pv-open-pill-1.html -- the same load, the Interesting viewers pill open",
    VIEWS_VERIFY: "pv_verify.html -- Entry 7's fresh load, the switch run's rows and headline",
    VIEWS_REVEALED: "pv_switch.html -- Entry 7's switch run at its end, Show more analytics pressed",
}

#: What each drive rests on, checked in the skeleton before the reader runs:
#: its builder's header, and the state it is named for.
VIEWS_NEEDLES: dict[str, tuple[str, ...]] = {
    VIEWS_CLOSED: ("Interesting viewers", 'aria-expanded="false"', ">Show more analytics<"),
    VIEWS_PILL_OPEN: (
        'aria-expanded="true"', 'aria-label="Works at a company you follow"', ">Show results<",
    ),
    VIEWS_VERIFY: (">Show more analytics<", ">Profile viewers<"),
    VIEWS_REVEALED: (">Highlights<", ">Details<", ">Companies<"),
}

#: The ruled switch and the decided reveal, as the tool presses them.
SWITCH_KEY = "interesting_viewers_verified"
REVEAL_KEY = "profile_views_show_more_analytics"

#: EACH PRESS A DRIVE STANDS IN FOR, with its source (ruling (2) of
#: 2026-09-28: "The leak harness's page double may stand in for a click by
#: moving the fixture to the state the real page draws after that click ...
#: Record each transition's source (which capture shows the after-state). A
#: transition no capture shows stays not driven."). ``None``: no capture shows
#: the page after that press, so the double refuses it, as the planted page
#: refuses every press, and the drive ends there.
TRANSITIONS: tuple[tuple[str, str, Optional[str]], ...] = (
    ("the Interesting viewers pill", VIEWS_CLOSED, VIEWS_PILL_OPEN),
    ("its 'verified' option", VIEWS_PILL_OPEN, None),
    ("Show more analytics", VIEWS_VERIFY, VIEWS_REVEALED),
)

#: A run of shaped words: the builder turned every letter of another member's
#: text into x or X.
_SHAPED_RUN = re.compile(r"[Xx]+(?:[ ][Xx]+)*")


def _shaped_as_plant(text: str) -> str:
    """ANOTHER MEMBER'S TEXT IS THE PLANT. A text whose every letter is x or X
    is one the skeleton builder reduced to shape -- a viewer's name, a
    headline, an employer; the double answers each run of shaped words with
    the plant, keeping the digits and punctuation around it ("Xxxxx (13.3%)"
    -> "<plant> (13.3%)"). Interface words, kept verbatim, pass through."""
    letters = [ch for ch in text if ch.isalpha()]
    if letters and all(ch in "xX" for ch in letters):
        return _SHAPED_RUN.sub(PLANT, text)
    return text


def _views_document(name: str) -> Any:
    """One skeleton, parsed -- once the file is shown to still be its
    builder's output in the state it is named for; otherwise this RAISES."""
    from tests import skeleton_page

    return skeleton_page.parse(
        _drawn(name, "_build_profile_views_skeleton.py", *VIEWS_NEEDLES[name])
    )


def _collapsed(element: Any) -> str:
    from tests import skeleton_page

    return " ".join(skeleton_page.text_of(element).split())


_BARE_NUMBER = re.compile(r"^[0-9][0-9,.]*%?$")


def _headline_metrics(page: Any, arg: Any = None) -> PageAnswer:
    """``dom.PROFILE_VIEWS_INSIGHTS_JS``'s ``metrics``, from the skeleton: each
    ``<p>`` whose text is a bare number followed by a sibling ``<p>`` holding
    text -- "paragraph pairs where the first is a bare number", as the
    reader's docstring names them -- in document order, inside ``main``; a
    ``<p>`` holding only a space between them is stepped over, as the capture
    draws one there. The label goes through the double's text answer, so a
    shaped label is the plant. Every other key is the planted page's own."""
    from tests import skeleton_page

    mains = skeleton_page.select(page.document, "main")
    scope = mains[0] if mains else page.document
    metrics = []
    for paragraph in skeleton_page.select(scope, "p"):
        if not _BARE_NUMBER.match(_collapsed(paragraph)):
            continue
        siblings = [child for child in paragraph.parent.children if hasattr(child, "tag")]
        after = [el for el in siblings[siblings.index(paragraph) + 1:] if _collapsed(el)]
        if after and after[0].tag == "p":
            metrics.append({
                "value": _collapsed(paragraph),
                "label": _shaped_as_plant(_collapsed(after[0])),
            })
    return _planted_answer_with(metrics=metrics)


class _ViewsTransitions:
    """THE CLICK STAND-IN (ruling (2) of 2026-09-28), over :data:`TRANSITIONS`.

    A press the capture record shows the page after moves the double to that
    capture's skeleton; any other press is refused, as the planted page
    refuses every press. The controls are recognised by the readers' OWN
    constants: the pill by ``view_switch``'s entry caption, the reveal's
    button by ``reveal``'s decided phrase. ``presses`` records each press and
    what the double did, so a test can say which press a drive stopped at."""

    def __init__(self, documents: dict[str, Any]) -> None:
        self._documents = documents
        self.presses: list[str] = []

    def __call__(self, locator: Any, page: Any) -> None:
        from linkedin_server import reveal, view_switch

        from tests.plantedpage import NavigationAttempted

        element = locator.element()
        said = view_switch.normalised(_collapsed(element))
        switch = view_switch.view_switch(SWITCH_KEY) or {}
        decided = reveal.decided_reveal(REVEAL_KEY) or {}
        if (
            page.document is self._documents[VIEWS_CLOSED]
            and "aria-expanded" in element.attrs
            and said == switch.get("pill_caption")
        ):
            self.presses.append(TRANSITIONS[0][0])
            page.document = self._documents[VIEWS_PILL_OPEN]
            return
        if (
            page.document is self._documents[VIEWS_VERIFY]
            and element.tag == "button"
            and said == decided.get("phrase")
        ):
            self.presses.append(TRANSITIONS[2][0])
            page.document = self._documents[VIEWS_REVEALED]
            return
        self.presses.append("refused")
        raise NavigationAttempted("locator.click")


def _views_page(page: Any, start: str) -> Any:
    """The planted page at the tool's address, drawn as the ``start``
    skeleton, standing in for the presses :data:`TRANSITIONS` sources."""
    from linkedin_server import dom

    from tests import skeleton_page

    documents = {name: _views_document(name) for name in VIEWS_SOURCES}
    return skeleton_page.SkeletonPage(
        page,
        documents[start],
        url=_profile_views_address(),
        answer_text=_shaped_as_plant,
        on_click=_ViewsTransitions(documents),
        scripts={dom.PROFILE_VIEWS_INSIGHTS_JS: _headline_metrics},
    )


def _modelled(at: Any, value: Any) -> Any:
    """``value``, once the double is shown to have answered every read the
    reader made: a locator method or selector it does not model is a refusal
    the reader could have swallowed, and a drive over it measures nothing."""
    if at.unmodelled:
        raise AssertionError("the skeleton double could not answer: %s" % sorted(set(at.unmodelled)))
    return value


async def pill_positions_over_the_skeleton(page: Any) -> Any:
    """``view_switch._pill_positions`` as ``apply_and_restore`` calls it before
    any press, for the ruled switch's caption, on the closed page.

    THE SIGNATURE DRIVE: every planted role is the plant, not "button", so no
    pill is found -- a read and an empty list. THE SKELETON: ``main
    [aria-expanded]`` draws a dialog button, then the three filter pills --
    Past 90 days, Interesting viewers, Company -- each a ``div[role=button]``
    holding a ``<label>``, then two more controls whose captions are shaped;
    the ruled caption is found at position 2."""
    from linkedin_server import view_switch

    at = _views_page(page, VIEWS_CLOSED)
    entry = view_switch.view_switch(SWITCH_KEY)
    return _modelled(at, await view_switch._pill_positions(at, entry["pill_caption"]))


async def option_positions_over_the_skeleton(page: Any) -> Any:
    """``view_switch._option_positions`` for the ruled option, with the pill
    open: the popover's two ``div[role=checkbox]`` options, "Works at a company
    you follow" and "Verified", both unchecked; the ruled one is at 1."""
    from linkedin_server import view_switch

    at = _views_page(page, VIEWS_PILL_OPEN)
    entry = view_switch.view_switch(SWITCH_KEY)
    return _modelled(at, await view_switch._option_positions(at, entry["option"]))


async def wait_for_option_over_the_skeleton(page: Any) -> Any:
    """``view_switch._wait_for_option`` for the ruled option, with the pill
    open: the first option is visible, and the read finds the ruled one."""
    from linkedin_server import view_switch

    at = _views_page(page, VIEWS_PILL_OPEN)
    entry = view_switch.view_switch(SWITCH_KEY)
    return _modelled(at, await view_switch._wait_for_option(at, entry["option"]))


async def apply_positions_over_the_skeleton(page: Any) -> Any:
    """``view_switch._apply_positions`` with the pill open: of the page's 25
    buttons, the popover's "Show results" is the one ``APPLY_PATTERN`` takes
    (its "Reset" beside it is not)."""
    from linkedin_server import view_switch

    at = _views_page(page, VIEWS_PILL_OPEN)
    return _modelled(at, await view_switch._apply_positions(at))


async def profile_views_switch_to_the_option(page: Any) -> Any:
    """The ruled switch as ``linkedin_who_viewed_me(view_switch=...)`` presses
    it -- ``server._profile_views_switch``, which calls
    ``view_switch.apply_and_restore`` with the server's own view and counter
    readers -- on the closed page, and the drive of BOTH readers.

    AS FAR AS A CAPTURE GOES: the counters read (the headline, 39), the pill
    is found, the view is read, and the pill's press is stood in for by the
    capture of that pill open; the option is found and read unchecked. Its
    press is NOT stood in for: no capture shows the popover with it checked,
    so the double refuses it and the drive ends there, recorded
    ``navigates (locator.click)``."""
    from linkedin_server import server

    at = _views_page(page, VIEWS_CLOSED)
    return _modelled(
        at, await server._profile_views_switch(at, SWITCH_KEY, server.DEFAULT_LIMIT)
    )


async def reveal_over_the_skeletons(page: Any) -> Any:
    """``reveal.reveal`` as ``_profile_views_more_analytics`` presses "Show
    more analytics" -- priced by the server's own counter reader -- on the
    fresh load, the press stood in for by the capture of the page after it.

    THE SIGNATURE DRIVE: ``check_reveal`` refuses the synthetic key before any
    read. HERE: exactly one visible ``main`` button carries the decided phrase
    and none of the three state attributes; the counters read the headline
    (39) before and after; ``main`` grows from the fresh load's elements to the
    revealed page's; the reveal is PERMITTED. Its reading (``COUNT_LINES_JS``)
    has no stand-in: the planted page answers it, so the reading comes back
    unreadable at both moments, which the gate records and does not gate on."""
    from linkedin_server import reveal, server

    at = _views_page(page, VIEWS_VERIFY)
    counters = await server._profile_views_press_counters(at)
    outcome = await reveal.reveal(
        at, key=REVEAL_KEY, read_counters=counters, reading=server.PROFILE_VIEWS_MENU_READING
    )
    return _modelled(at, outcome)


async def profile_views_more_analytics_over_the_skeletons(page: Any) -> Any:
    """``_profile_views_more_analytics`` as ``linkedin_who_viewed_me
    (show_more_analytics=True)`` calls it: the reveal pressed (stood in for),
    then the page's insights and the revealed sections read -- his own
    page's analytics, and the aggregates over his viewers (the ruling admits
    both: ``ADMITTED_TEXT``)."""
    from linkedin_server import server

    at = _views_page(page, VIEWS_VERIFY)
    return _modelled(at, await server._profile_views_more_analytics(at))


async def read_profile_views_more_insights_as_shipped(page: Any) -> Any:
    """``read_profile_views_more_insights`` as ``_profile_views_more_analytics``
    calls it after the reveal: on the page, nothing else -- here the revealed
    page's skeleton, the capture taken after that press.

    THE SIGNATURE DRIVE: the planted heading is neither "highlights" nor
    "details", so every heading is skipped -- a read and an empty shape.

    THE SKELETON draws, in ``main``, a "Highlights" section (three value/label
    pairs) and a "Details" section (a "Companies" pill, then five
    "<company> (<n>%)" entries); every value and company is shaped, so here
    it is the plant.

    WHAT COMES BACK: the highlight values and the company names, as plain
    strings outside any record -- ``returns_text``. AGGREGATES OVER HIS
    VIEWERS THAT IDENTIFY NO ONE, so ADMITTED by the ruling of 2026-09-28; no
    field is a viewer."""
    from linkedin_server import profile_views_more

    at = _views_page(page, VIEWS_REVEALED)
    return _modelled(at, await profile_views_more.read_profile_views_more_insights(at))


# ---------------------------------------------------------------------------
# The tables the guard reads
# ---------------------------------------------------------------------------

#: To the success path: the guard runs each beside its reader's signature
#: variants, and the reader's verdict is the worst of them all.
DRIVES: dict[str, Callable[..., Any]] = {
    "dom:read_any_save_control_label": read_any_save_control_label_as_shipped,
    "named_profile:composer_holds": named_profile_composer_holds_as_shipped,
    "people_results:read_result_people": read_result_people_as_shipped,
    "profile_editor:read_premium_badge": read_premium_badge_as_shipped,
    "server:_attach_recipient_ids": attach_recipient_ids_as_shipped,
    "server:_profile_views_press_counters": profile_views_press_counters_as_shipped,
    "threads:composer_holds": threads_composer_holds_as_shipped,
    # ADMITTED BY THE RULING OF 2026-09-28: each returns page text outside a
    # record on its success path -- his own profile's, or an aggregate that
    # identifies no one -- and is named with its reason in the guard's
    # ADMITTED_TEXT.
    "dom:read_profile_detail_entries": read_profile_detail_entries_as_shipped,
    "dom:read_self_owned_editor_fields": read_self_owned_editor_fields_as_shipped,
    "dom:read_self_owned_editor_values": read_self_owned_editor_values_as_shipped,
    "profile_views_more:read_profile_views_more_insights": (
        read_profile_views_more_insights_as_shipped
    ),
    # OVER THE PROFILE-VIEWS SKELETONS (the order of 2026-09-28 04:25):
    # ruling (3)'s four view_switch readers, and ruling (2)'s click stand-in
    # carrying the reveal -- and the server's reveal, whose revealed page is
    # admitted text -- past the press a capture shows the page after.
    "view_switch:_pill_positions": pill_positions_over_the_skeleton,
    "view_switch:_option_positions": option_positions_over_the_skeleton,
    "view_switch:_wait_for_option": wait_for_option_over_the_skeleton,
    "view_switch:_apply_positions": apply_positions_over_the_skeleton,
    "reveal:reveal": reveal_over_the_skeletons,
    "server:_profile_views_more_analytics": profile_views_more_analytics_over_the_skeletons,
}

#: As far as a press. Run by the guard, so the reads before the press are
#: hunted; each ends on the refused click, recorded ``navigates (locator.click)``.
TO_THE_PRESS: dict[str, Callable[..., Any]] = {
    "press:disclose": disclose_to_the_press,
    "share_link:copy_own_post_link": copy_own_post_link_to_the_press,
    # PAST ONE PRESS AND STOPPED AT THE NEXT: the pill's press is stood in for
    # by the capture of that pill open; no capture shows the option checked.
    "server:_profile_views_switch": profile_views_switch_to_the_option,
    "view_switch:apply_and_restore": profile_views_switch_to_the_option,
}
