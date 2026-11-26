"""Worlds for the scheduled-posts read's tests, built from live session 11's own captures.

THE MARKUP IS REAL; ONLY THE BEHAVIOUR IS A FIXTURE CHOICE. Load 25 of live
session 11 drew the post composer EMPTY and then its two dialogs, nothing
typed: ``tests/fixtures/live11/sharebox_words.html`` (the composer),
``sharebox_schedule_open_words.html`` (Schedule post pressed) and
``sharebox_scheduled_list_open_words.html`` (View all scheduled posts pressed,
the list EMPTY) -- the tracked skeletons with LinkedIn's words put back by
keyed shape. A world here is the composer capture plus one script:

* Schedule post puts the SCHEDULE capture's own share-box modal in place of
  the page's (parsed out of that capture in the page, byte for byte);
* View all scheduled posts puts the LIST capture's own modal in;
* the modal's own Dismiss takes the modal off the page.

What Dismiss does is NOT measured (the captures stop at the open list), and
neither is a populated list or a draft prompt: every world that draws one
names it in its config, and no test reads a choice as a measurement.

Nothing here reaches LinkedIn: every page is set into a local headless
Chromium and every request it starts is refused by the test's own route.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LIVE11 = Path(__file__).parent / "fixtures" / "live11"
COMPOSER_PAGE = (LIVE11 / "sharebox_words.html").read_text(encoding="utf-8")
SCHEDULE_PAGE = (LIVE11 / "sharebox_schedule_open_words.html").read_text(encoding="utf-8")
LIST_PAGE = (LIVE11 / "sharebox_scheduled_list_open_words.html").read_text(encoding="utf-8")

def _js(text: str) -> str:
    """A JSON string safe inside an inline script: no ``</`` can close it."""
    return json.dumps(text).replace("</", "<\\/")


_BEHAVIOUR = r"""
<script>
(function () {
  var cfg = window.__scheduleConfig || {};
  var PAGES = {schedule: %SCHEDULE%, list: %LIST%};
  var MODAL = '[role="dialog"].share-box-v2__modal';
  window.__presses = {schedule: 0, view_all: 0, dismiss: 0, other: 0};
  function swapModal(which) {
    var doc = new DOMParser().parseFromString(PAGES[which], 'text/html');
    var next = doc.querySelector(MODAL);
    if (which === 'list' && cfg.listPopulated) {
      var empty = next.querySelector('.share-post-list-view__empty-state');
      if (empty) {
        var filled = doc.createElement('ul');
        filled.className = 'scaffold-finite-scroll__content';
        filled.innerHTML = '<li>x</li><li>x</li>';
        empty.replaceWith(filled);
      }
    }
    document.querySelector(MODAL).replaceWith(document.importNode(next, true));
  }
  if (cfg.startsWithText) {
    var editor = document.querySelector(MODAL + ' div[role="textbox"]');
    if (editor) { editor.classList.remove('ql-blank'); editor.textContent = 'x'; }
    var post = document.querySelector(MODAL + ' button.share-actions__primary-action');
    if (post) { post.removeAttribute('disabled'); post.classList.remove('artdeco-button--disabled'); }
  }
  document.addEventListener('click', function (event) {
    var target = event.target;
    if (target.closest('button.share-actions__scheduled-post-btn')) {
      window.__presses.schedule += 1;
      if (!cfg.noSchedule) swapModal('schedule');
      return;
    }
    var button = target.closest('button');
    if (button && button.textContent.trim() === 'View all scheduled posts') {
      window.__presses.view_all += 1;
      swapModal('list');
      return;
    }
    if (target.closest('button.artdeco-modal__dismiss')) {
      window.__presses.dismiss += 1;
      if (cfg.dismissDoesNothing) return;
      var modal = document.querySelector(MODAL);
      if (modal) modal.remove();
      if (cfg.dismissDrawsDialog) {
        var prompt = document.createElement('div');
        prompt.setAttribute('role', 'alertdialog');
        prompt.innerHTML = '<p>x</p><button>x</button><button>x</button>';
        document.body.appendChild(prompt);
      }
      if (cfg.dismissDrawsToast) {
        var toasts = document.querySelector('section.artdeco-toasts .artdeco-toasts_toasts');
        if (toasts) { var toast = document.createElement('div'); toast.textContent = 'x'; toasts.appendChild(toast); }
      }
      return;
    }
    window.__presses.other += 1;
  }, true);
})();
</script>
"""


def world(**config: Any) -> str:
    """The composer capture with the behaviour and ``config`` spliced in.

    ``config`` keys, each a FIXTURE CHOICE: ``noSchedule`` (Schedule post
    draws nothing), ``listPopulated`` (the list draws two rows in place of its
    empty state -- a shape never captured), ``dismissDoesNothing``,
    ``dismissDrawsDialog`` (an alert dialog after Dismiss, the shape a draft
    prompt might take), ``dismissDrawsToast``, ``startsWithText`` (the
    composer opens holding text, Post enabled -- the shape a kept draft might
    take).
    """
    assert COMPOSER_PAGE.count("</body>") == 1
    script = (
        "<script>window.__scheduleConfig = " + json.dumps(config) + ";</script>"
        + _BEHAVIOUR.replace("%SCHEDULE%", _js(SCHEDULE_PAGE)).replace(
            "%LIST%", _js(LIST_PAGE)
        )
    )
    return COMPOSER_PAGE.replace("</body>", script + "</body>")
