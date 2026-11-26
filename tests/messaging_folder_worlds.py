"""Worlds for the folder switch's tests, built from live session 11's own captures.

THE MARKUP IS REAL; ONLY THE BEHAVIOUR IS A FIXTURE CHOICE. Load 39 of live
session 11 drew the messaging folder pill closed, open and switched to
Archived (``tests/fixtures/live11/messaging_guarded.html``,
``messaging_folder_open.html``, ``messaging_archived.html``), and the
composer's own list (``messaging_list.html``) draws the same pill, closed. A
world here is the composer's list, unchanged, plus one script:

* pressing the pill opens it -- the OPEN capture's own four choices, cut out of
  ``messaging_folder_open.html`` byte for byte, are put into the closed page's
  empty dropdown -- and pressing it again closes it;
* choosing a folder closes the dropdown, puts the word on the pill, and swaps
  the conversation list: ``Archived`` puts in the ARCHIVED capture's own list
  (cut out of ``messaging_archived.html``, byte for byte); the folder the page
  started on puts the original list back.

What a choice does on the COMPOSER's page is not measured (the switch was
captured on ``/messaging/``), so every world names the behaviour it chooses in
its config, and no test reads a choice as a measurement.

Nothing here reaches LinkedIn: every page is set into a local headless
Chromium, every request it starts is refused by the test's own route, and the
address a page "has" is a proxy's attribute (:class:`AtAddress`).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

LIVE11 = Path(__file__).parent / "fixtures" / "live11"
COMPOSE_LIST_PAGE = (LIVE11 / "messaging_list.html").read_text(encoding="utf-8")
OPEN_PAGE = (LIVE11 / "messaging_folder_open.html").read_text(encoding="utf-8")
ARCHIVED_PAGE = (LIVE11 / "messaging_archived.html").read_text(encoding="utf-8")

#: The open dropdown's choices, cut out of the OPEN capture: the one content
#: node reading ``aria-hidden="false"`` inside the folder dropdown root holds
#: one ``artdeco-dropdown__content-inner``, and that is what is carried over.
_OPEN_CHOICES = re.search(
    r'data-test-messaging-inbox-filters__folder-dropdown="">.*?'
    r'<div tabindex="-1" aria-hidden="false" [^>]*>\n'
    r'(<div class="artdeco-dropdown__content-inner">.*?</ul>\n</div>)\n</div>',
    OPEN_PAGE,
    re.S,
)
assert _OPEN_CHOICES is not None, "the open capture no longer holds one open folder dropdown"
OPEN_CHOICES_MARKUP: str = _OPEN_CHOICES.group(1)

#: The words the open capture draws, parsed out of it rather than typed.
CAPTURED_CHOICES: list[str] = [
    word.strip()
    for word in re.findall(
        r'<div role="button" [^>]*data-test-messaging-inbox-filters__folder-dropdown="x"[^>]*>\n([^<]+)\n</div>',
        OPEN_CHOICES_MARKUP,
    )
]

_LIST = re.compile(
    r'<ul class="list-style-none msg-conversations-container__conversations-list"[^>]*>.*?</ul>',
    re.S,
)


def _one_list(page: str) -> str:
    found = _LIST.findall(page)
    assert len(found) == 1, f"expected one conversation list, found {len(found)}"
    return found[0]


#: The ARCHIVED capture's own conversation list, byte for byte.
ARCHIVED_LIST_MARKUP: str = _one_list(ARCHIVED_PAGE)

def _js(text: str) -> str:
    """A JSON string safe inside an inline script: no ``</`` can close it."""
    return json.dumps(text).replace("</", "<\\/")


_BEHAVIOUR = r"""
<script>
(function () {
  var cfg = window.__folderConfig || {};
  var CHOICES = %CHOICES%;
  var ARCHIVED = %ARCHIVED%;
  window.__presses = {pill: 0, choices: {}};
  var pill = document.querySelector('main button[data-test-messaging-inbox-filters__folder-pill]');
  if (!pill) return;
  var root = pill.parentElement;
  var content = root.querySelector('.artdeco-dropdown__content');
  function listNow() {
    return document.querySelector('main ul.msg-conversations-container__conversations-list');
  }
  function wordNode() {
    for (var i = 0; i < pill.childNodes.length; i++) {
      var node = pill.childNodes[i];
      if (node.nodeType === 3 && node.nodeValue.trim()) return node;
    }
    return null;
  }
  function word() { var n = wordNode(); return n ? n.nodeValue.trim() : null; }
  function setWord(w) { var n = wordNode(); if (n) n.nodeValue = '\n' + w + '\n'; }
  var original = {word: word(), list: listNow() ? listNow().outerHTML : ''};
  function swapList(markup) {
    var now = listNow();
    if (!now) return;
    var holder = document.createElement('div');
    holder.innerHTML = markup;
    now.replaceWith(holder.firstElementChild);
  }
  function render() {
    var html = CHOICES;
    (cfg.drop || []).forEach(function (w) {
      html = html.split('\n' + w + '\n').join('\nx\n');
    });
    return html;
  }
  function open() {
    pill.setAttribute('aria-expanded', 'true');
    content.setAttribute('aria-hidden', 'false');
    content.innerHTML = render();
  }
  function close() {
    pill.setAttribute('aria-expanded', 'false');
    content.setAttribute('aria-hidden', 'true');
    content.innerHTML = '';
  }
  pill.addEventListener('click', function () {
    window.__presses.pill += 1;
    if (pill.getAttribute('aria-expanded') === 'true') { close(); } else { open(); }
  });
  content.addEventListener('click', function (event) {
    var item = event.target.closest('[role="button"]');
    if (!item) return;
    var w = item.textContent.trim();
    window.__presses.choices[w] = (window.__presses.choices[w] || 0) + 1;
    if (cfg.choiceStaysOpen) return;
    close();
    if (cfg.noSwitch) return;
    if (cfg.stuck && word() === 'Archived') return;
    setWord(w);
    if (w === 'Archived') { swapList(ARCHIVED); }
    else if (w === original.word) {
      var back = original.list;
      if (cfg.listDiffers) {
        back = back.replace('msg-conversation-listitem msg-conversations-container__convo-item',
                            'msg-conversation-listitem msg-conversation-card--occluded msg-conversations-container__convo-item');
      }
      swapList(back);
    }
  });
})();
</script>
"""


def _with_behaviour(base: str, config: dict[str, Any]) -> str:
    assert base.count("</body>") == 1
    script = (
        "<script>window.__folderConfig = " + json.dumps(config) + ";</script>"
        + _BEHAVIOUR.replace("%CHOICES%", _js(OPEN_CHOICES_MARKUP)).replace(
            "%ARCHIVED%", _js(ARCHIVED_LIST_MARKUP)
        )
    )
    return base.replace("</body>", script + "</body>")


def world(**config: Any) -> str:
    """The composer's list with the folder behaviour and ``config`` spliced in.

    ``config`` keys, each a FIXTURE CHOICE: ``drop`` (choices drawn as the
    reduced ``x``), ``noSwitch`` (a choice closes the dropdown and changes
    nothing), ``stuck`` (once on Archived, no choice switches back),
    ``listDiffers`` (switching back draws the original list with its first
    row reduced to a placeholder), ``choiceStaysOpen`` (a choice does nothing,
    the dropdown stays open).
    """
    return _with_behaviour(COMPOSE_LIST_PAGE, config)


def two_pill_world() -> str:
    """The composer's list drawing the pill TWICE (a fixture choice): nothing
    may be pressed on a page whose pill is not the one measured."""
    marker = "<button aria-expanded=\"false\" id=\"kdcdacdcf\""
    assert COMPOSE_LIST_PAGE.count(marker) == 1
    start = COMPOSE_LIST_PAGE.index(marker)
    end = COMPOSE_LIST_PAGE.index("</button>", start) + len("</button>")
    pill = COMPOSE_LIST_PAGE[start:end]
    return _with_behaviour(COMPOSE_LIST_PAGE[:end] + pill + COMPOSE_LIST_PAGE[end:], {})


class AtAddress:
    """A real page, wearing an address: ``url`` is this proxy's attribute (a
    page set by ``set_content`` reads ``about:blank``), everything else is the
    page's. ``leave_on`` names a choice whose click moves the address to
    ``leave_to`` -- a fixture choice, for the world where the switch navigates."""

    def __init__(self, page: Any, url: str, *, leave_on: str | None = None, leave_to: str = ""):
        self._page = page
        self.url = url
        self._leave_on = leave_on
        self._leave_to = leave_to

    async def click(self, selector: str, **kwargs: Any) -> None:
        await self._page.click(selector, **kwargs)
        if self._leave_on and f'name="{self._leave_on}"s' in selector:
            self.url = self._leave_to

    def __getattr__(self, name: str) -> Any:
        return getattr(self._page, name)
