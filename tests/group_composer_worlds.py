"""Worlds for the group post's tests, built from live session 11's own captures.

THE MARKUP IS REAL; ONLY THE BEHAVIOUR IS A FIXTURE CHOICE. Load 36 of live
session 11 drew a group he is a member of with its share box CLOSED
(``tests/fixtures/live11/group_member_words.html``) and with its trigger
pressed, the composer OPEN and empty (``group_composer_open_words.html``) --
the tracked skeletons with LinkedIn's words put back by keyed shape. A world
here is the closed page plus one script: pressing ``Start a public post``
puts the OPEN capture's own share-box modal on the page (parsed out of that
capture in the page, byte for byte); typing into its editor turns ``Post`` on,
as the measured disabled-while-empty shape implies; pressing ``Post`` takes
the modal away.

What ``Post`` does is NOT measured, and neither is anything the group draws
after it: every world names the behaviour it chooses in its config, and no
test reads a choice as a measurement.

Nothing here reaches LinkedIn: every page is set into a local headless
Chromium and every request it starts is refused by the test's own route.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LIVE11 = Path(__file__).parent / "fixtures" / "live11"
CLOSED_PAGE = (LIVE11 / "group_member_words.html").read_text(encoding="utf-8")
OPEN_PAGE = (LIVE11 / "group_composer_open_words.html").read_text(encoding="utf-8")
FEED_COMPOSER_PAGE = (LIVE11 / "sharebox_words.html").read_text(encoding="utf-8")


def _js(text: str) -> str:
    """A JSON string safe inside an inline script: no ``</`` can close it."""
    return json.dumps(text).replace("</", "<\\/")


_BEHAVIOUR = r"""
<script>
(function () {
  var cfg = window.__groupConfig || {};
  var OPEN = %OPEN%;
  var MODAL = '[role="dialog"].share-box-v2__modal';
  window.__presses = {trigger: 0, post: 0, typed: 0, other: 0};
  function openComposer() {
    var doc = new DOMParser().parseFromString(OPEN, 'text/html');
    var modal = doc.querySelector(MODAL);
    if (cfg.openDrawsSchedule) {
      var actions = modal.querySelector('button.share-actions__primary-action');
      var schedule = doc.createElement('button');
      schedule.className = 'share-actions__scheduled-post-btn';
      schedule.setAttribute('aria-label', 'Schedule post');
      actions.parentElement.insertBefore(schedule, actions);
    }
    var node = document.importNode(modal, true);
    document.body.appendChild(node);
    var editor = node.querySelector('div[role="textbox"]');
    if (cfg.openHoldsText && editor) { editor.classList.remove('ql-blank'); editor.textContent = 'x'; }
    if (editor) {
      editor.setAttribute('contenteditable', 'true');
      editor.addEventListener('input', function () {
        window.__presses.typed += 1;
        if (cfg.typingAltered && !editor.__altered) { editor.__altered = true; editor.textContent = editor.textContent + ' x'; }
        var post = node.querySelector('button.share-actions__primary-action');
        var has = editor.textContent.trim().length > 0;
        if (has) editor.classList.remove('ql-blank');
        if (post && !cfg.postStaysDisabled) {
          var turn = function () {
            if (has) { post.removeAttribute('disabled'); post.classList.remove('artdeco-button--disabled'); }
            else { post.setAttribute('disabled', ''); }
          };
          if (cfg.enableAfterMs) { setTimeout(turn, cfg.enableAfterMs); } else { turn(); }
        }
      });
    }
  }
  document.addEventListener('click', function (event) {
    var button = event.target.closest('button');
    if (!button) { window.__presses.other += 1; return; }
    var box = button.closest('.share-box-feed-entry__closed-share-box');
    if (box && button.textContent.trim() === 'Start a public post') {
      window.__presses.trigger += 1;
      if (cfg.openAfterMs) { setTimeout(openComposer, cfg.openAfterMs); return; }
      if (!cfg.triggerDoesNothing) openComposer();
      return;
    }
    if (button.closest(MODAL) && button.classList.contains('share-actions__primary-action')) {
      window.__presses.post += 1;
      if (cfg.postKeepsOpen) return;
      var modal = document.querySelector(MODAL);
      if (modal) modal.remove();
      return;
    }
    window.__presses.other += 1;
  }, true);
})();
</script>
"""


def world(**config: Any) -> str:
    """The closed group page with the behaviour and ``config`` spliced in.

    ``config`` keys, each a FIXTURE CHOICE: ``triggerDoesNothing``,
    ``openDrawsSchedule`` (the opened composer draws Schedule post -- the feed
    composer's mark), ``openHoldsText`` (it opens holding a draft),
    ``postStaysDisabled``, ``typingAltered`` (the page changes his words as
    they land), ``postKeepsOpen``, ``openAfterMs`` (the composer is drawn that
    many milliseconds after the press, as a live modal animates in) and
    ``enableAfterMs`` (Post turns on that long after the words land, the lag
    the reply path measured live).
    """
    assert CLOSED_PAGE.count("</body>") == 1
    script = (
        "<script>window.__groupConfig = " + json.dumps(config) + ";</script>"
        + _BEHAVIOUR.replace("%OPEN%", _js(OPEN_PAGE))
    )
    return CLOSED_PAGE.replace("</body>", script + "</body>")
