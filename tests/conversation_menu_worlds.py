"""Worlds for the conversation menu's tests, built from live session 11's own captures.

THE MARKUP IS REAL; ONLY THE BEHAVIOUR IS A FIXTURE CHOICE. Load 40 of live
session 11 drew the conversation he named twice: with the active row's
options menu CLOSED (``tests/fixtures/live11/msg_thread.html``) and OPEN
(``tests/fixtures/live11/c_b3_1_menu_open.html``). A world here is the closed
page, unchanged, plus one script: pressing the active row's trigger puts the
OPEN capture's own menu markup -- cut out of the second file, byte for byte --
into the closed page's empty menu, and Escape takes it out again. What a press
of an item does is NOT measured, and each world names the behaviour it
chooses in its config (``after``), so no test reads a choice as a
measurement.

Nothing here reaches LinkedIn: every page is set into a local headless
Chromium by the test's own navigator.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

LIVE11 = Path(__file__).parent / "fixtures" / "live11"
CLOSED_PAGE = (LIVE11 / "msg_thread.html").read_text(encoding="utf-8")
OPEN_PAGE = (LIVE11 / "c_b3_1_menu_open.html").read_text(encoding="utf-8")

#: The open menu's inner markup, cut out of the OPEN capture: the one content
#: node whose ``aria-hidden`` reads false holds exactly one
#: ``artdeco-dropdown__content-inner``, and that is what is carried over.
_OPEN_CONTENT = re.search(
    r'<div tabindex="-1" aria-hidden="false" id="[^"]+" '
    r'class="msg-thread-actions__dropdown-options--inbox-shortcuts[^"]*"[^>]*>\n'
    r'(<div class="artdeco-dropdown__content-inner">.*?</ul>\n</div>)\n</div>',
    OPEN_PAGE,
    re.S,
)
assert _OPEN_CONTENT is not None, "the open capture no longer holds one open menu"
OPEN_MENU_MARKUP: str = _OPEN_CONTENT.group(1)

#: The words the open capture draws, parsed out of it rather than typed.
CAPTURED_WORDS: list[str] = [
    word.strip()
    for word in re.findall(
        r'class="msg-thread-actions__dropdown-option[^"]*"[^>]*>\n([^<]+)\n</div>',
        OPEN_MENU_MARKUP,
    )
]

_BEHAVIOUR = r"""
<script>
(function () {
  var cfg = window.__menuConfig || {};
  var MENU = %MENU%;
  window.__presses = {trigger: 0, escape: 0, items: {}, dialog: 0};
  function activeRow() {
    var rows = document.querySelectorAll('main li.msg-conversation-listitem');
    for (var i = 0; i < rows.length; i++) {
      if (rows[i].querySelector('.msg-conversations-container__convo-item-link--active')) return rows[i];
    }
    return null;
  }
  var row = activeRow();
  if (!row) return;
  var trigger = row.querySelector('button.msg-thread-actions__control');
  var content = row.querySelector('.msg-thread-actions__dropdown-options--inbox-shortcuts');
  var swaps = cfg.swap || {};
  function render() {
    var html = MENU;
    Object.keys(swaps).forEach(function (from) {
      html = html.split('\n' + from + '\n').join('\n' + swaps[from] + '\n');
    });
    (cfg.drop || []).forEach(function (word) {
      html = html.split('\n' + word + '\n').join('\nx\n');
    });
    return html;
  }
  function open() {
    if (cfg.openDrawsNothing) { trigger.setAttribute('aria-expanded', 'true'); return; }
    trigger.setAttribute('aria-expanded', 'true');
    content.setAttribute('aria-hidden', 'false');
    content.innerHTML = render();
  }
  function close() {
    trigger.setAttribute('aria-expanded', 'false');
    content.setAttribute('aria-hidden', 'true');
    content.innerHTML = '';
  }
  trigger.addEventListener('click', function () {
    window.__presses.trigger += 1;
    if (trigger.getAttribute('aria-expanded') === 'true') { close(); } else { open(); }
  });
  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    window.__presses.escape += 1;
    if (!cfg.escapeStaysOpen) close();
  });
  content.addEventListener('click', function (event) {
    var item = event.target.closest('.msg-thread-actions__dropdown-option');
    if (!item) return;
    var word = item.textContent.trim();
    window.__presses.items[word] = (window.__presses.items[word] || 0) + 1;
    var after = (cfg.after || {})[word] || {};
    if (after.swap) { Object.keys(after.swap).forEach(function (k) { swaps[k] = after.swap[k]; }); }
    close();
    if (after.dropActive) {
      var link = row.querySelector('.msg-conversations-container__convo-item-link--active');
      if (link) link.classList.remove('msg-conversations-container__convo-item-link--active');
    }
    if (after.dialog) {
      var dialog = document.createElement('div');
      dialog.setAttribute('role', 'dialog');
      dialog.innerHTML = after.dialog;
      dialog.addEventListener('click', function () { window.__presses.dialog += 1; });
      document.body.appendChild(dialog);
    }
  });
})();
</script>
"""


def _with_behaviour(base: str, config: dict[str, Any]) -> str:
    assert base.count("</body>") == 1
    script = (
        "<script>window.__menuConfig = " + json.dumps(config) + ";</script>"
        + _BEHAVIOUR.replace("%MENU%", json.dumps(OPEN_MENU_MARKUP))
    )
    return base.replace("</body>", script + "</body>")


def world(**config: Any) -> str:
    """The CLOSED capture with the press behaviour and ``config`` spliced in.

    ``config`` keys, each a FIXTURE CHOICE: ``swap`` (word -> word drawn in its
    place when the menu opens), ``drop`` (words drawn as the reduced ``x``),
    ``after`` (per pressed word: ``swap`` for later opens, ``dropActive`` to
    take the active marker off the row, ``dialog`` markup to draw),
    ``escapeStaysOpen`` and ``openDrawsNothing``.
    """
    return _with_behaviour(CLOSED_PAGE, config)


def muted_world(**config: Any) -> str:
    """A world whose menu draws ``Unmute`` where the capture drew ``Mute`` --
    the DERIVED word, a fixture choice, never measured."""
    swap = dict(config.pop("swap", {}) or {})
    swap.setdefault("Mute", "Unmute")
    return world(swap=swap, **config)


def unread_world(**config: Any) -> str:
    """A world whose menu draws ``Mark as read`` where the capture drew ``Mark
    as unread`` -- the DERIVED word, a fixture choice, never measured."""
    swap = dict(config.pop("swap", {}) or {})
    swap.setdefault("Mark as unread", "Mark as read")
    return world(swap=swap, **config)


def no_active_row_world() -> str:
    """The closed capture with its active marker taken off -- the shape a
    conversation's own address would draw if its row were not in the list."""
    marker = "msg-conversations-container__convo-item-link--active"
    assert CLOSED_PAGE.count(marker) == 1
    return _with_behaviour(
        CLOSED_PAGE.replace(marker, "msg-conversations-container__convo-item-link"), {}
    )
