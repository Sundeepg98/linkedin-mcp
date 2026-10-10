"""The Premium company panel's lines, returned at runtime as third-party text.

Census row ``J 124`` -- *Premium AI company intelligence (headcount, openings,
strategic priorities)* -- is the panel ``dom.read_job_insight_panels`` returns
as ``company_insights`` on a posting ``linkedin_job_detail`` has already
loaded. Live session 8 (2026-10-10) kept one posting, and lane B4 MEASURED the
panel on it: under ``Insights about the company`` and ``Powered by Bing`` it
draws ``Company focus areas`` (a titled focus area and its summary),
``Hiring & headcount`` (a summary), and the figures -- ``Total employees``,
``2 year growth``, ``Company-wide``, ``Median employee tenure:``. The focus
areas and the summaries are LinkedIn's AI-written prose ABOUT AN ORGANISATION.

THE RULING THAT GOVERNS RETURNING IT: ``THIRD-PARTY-TEXT-AT-RUNTIME`` (the
orchestrator, 2026-10-10, applying the operator's ``NAMES-AT-RUNTIME``): an
organisation's prose is returned at runtime under ``PEOPLE-DATA-MITIGATIONS``
-- returned as untrusted third-party text, sanitised, length-bounded, never
stored. This module is those three in code, for this panel, and it reuses the
package's one sanitiser (``people_data.sanitise``) and its one marker
(``people_data.UNTRUSTED_KEY``) rather than inventing a second of either.

* MARKED: the panel carries ``people_data.UNTRUSTED_KEY`` with
  ``people_data.UNTRUSTED_NOTE``, the key a client model already meets beside
  every third party's words.
* SANITISED: every line through ``people_data.sanitise`` -- NFC, controls,
  zero-width, bidirectional and other invisible characters removed,
  whitespace collapsed -- so a line is its own sanitised form.
* BOUNDED: each line at :data:`LINE_CAP` characters, and the panel at the
  reader's line cap; ``truncated`` says whether either cut anything.
* NEVER STORED: nothing here writes, logs or caches; the page-string guards in
  ``tests/`` convict a page string in a log or an exception wherever it goes.

THE EMPLOYER'S NAME is handled before this, by ``dom.company_panel_lines``
(the panel heading's employer substituted with ``<company>`` in every line).
"""
from __future__ import annotations

from typing import Any, Iterable

from linkedin_server import people_data

#: Characters per line after sanitising. The longest line measured on session
#: 8's posting -- the "Hiring & headcount" summary -- was 816 characters, and
#: LinkedIn's own limit for an organisation's description is 2,000; a line
#: here is one paragraph of the panel, so 1,000 keeps every measured line
#: whole and bounds a pathological one.
LINE_CAP = 1000


def mitigated(lines: Iterable[Any], *, run_capped: bool) -> dict[str, Any]:
    """The panel's lines, sanitised and bounded, with the marker. PURE.

    ``run_capped`` is the reader's own word that the panel drew more lines
    than it read; a line cut at :data:`LINE_CAP` sets ``truncated`` too. A
    line that sanitises to nothing is dropped, never returned empty.
    """
    out: list[str] = []
    cut = bool(run_capped)
    for line in lines:
        whole = people_data.sanitise(line, cap=10 * LINE_CAP)
        kept = people_data.sanitise(line, cap=LINE_CAP)
        if len(whole) > len(kept):
            cut = True
        if kept:
            out.append(kept)
    return {
        "lines": out,
        "truncated": cut,
        people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE,
    }
