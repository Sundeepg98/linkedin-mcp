"""Is a Top Voice badge, or a second-language profile affordance, DRAWN on his own profile?

WHY THIS EXISTS. Ledger rows 43 `BADGES-SURFACE` (census K8/K10) and 72
`MULTILANG-PROFILE` (census D27/D28) are each charged `allowlist +1`. Both
charges are HYPOTHESES about what blocks the row. The contact-info panel was
opened on 2026-09-05 at allowlist +0, by PRESSING an affordance that
`/in/me/` -- an already-admitted address -- already draws. This probe asks
whether these two rows are the same shape, and it asks it without adding an
address.

WHAT LEAVES THE PAGE: INTEGERS AND NOTHING ELSE. The in-page script has no
branch that returns a substring of the document. It returns counts keyed by
this file's own literals. That is a STRUCTURAL property, not a filter, and it
is the property `linkedin_server/recommendations.py` shipped on the same day:
no published value is derived from page content. A badge sits beside his name
and a language selector names a language; both are the class of thing where a
shape-based guard does not save you, because `census_substitute` returns a
person's name unchanged.

WORD BOUNDARY, NOT SUBSTRING. The contact-info probe measured `im` scoring 2
by substring and ZERO by word boundary on the same dialog -- `im` occurs
inside ordinary English words. Every needle here is matched with a
neighbour-character test. That test needs no escaping and cannot be
mis-quoted, which is why it is used instead of a JavaScript `RegExp` built
from a Python string: that construction aborted a run on 2026-09-05 with
`Invalid regular expression: missing /`.

TWO ABSOLUTE READINGS, NEVER A DELTA. This surface was measured hydrating --
`/in/me/` read 67 then 80 then 235 census controls in one process with
nothing pressed and nothing navigated. A delta cannot answer a question about
presence, so every number below is an absolute count, and the profile is read
TWICE with the pair printed side by side.

NAMING NOTE, AND IT IS NOT A STYLE PREFERENCE. The taint guard
(`tests/test_page_text_is_never_printed.py`) tracks names across a MODULE, not
per scope. A name bound from a page-derived object is tainted in every
function in this file, including ones that touch no page. So the in-page
result is unpacked under names used NOWHERE in `report()`, and `report()`
iterates under its own distinct names. Two waves have paid for this already:
`196394d` (locals `before`/`after`) and the contact-info probe (`key`/`value`
in a comprehension). Do not "tidy" these names back together.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_server import config, dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

# The control page. An ADMITTED read address that draws no badge and no
# language selector, so a working reader must report absence here.
CONTROL_URL = "https://www.linkedin.com/mypreferences/d/dark-mode"
PROFILE_URL = "https://www.linkedin.com/in/me/"

# Needles. Each is matched with a WORD-BOUNDARY test over lowercased text.
#
# `dark` is the MUST-FIND needle on the control page: that page is a
# three-state dark-mode radio group, measured six times across two days by
# `linkedin_update_setting`. If `dark` reads 0 on the control page the reader
# is broken and the live numbers are not printed at all.
#
# `zzq_no_surface_draws_this` is the MUST-BE-ABSENT needle, on BOTH pages. A
# reader that matches everything is then visible as broken rather than as
# thorough. A zero from a working reader and a zero from a dead aim are the
# same character without it.
NEEDLES = (
    "dark",
    "top voice",
    "verified",
    "verification",
    "premium",
    "another language",
    "profile language",
    "add profile in another language",
    "zzq_no_surface_draws_this",
)

#: THE SAME NINE STRINGS UNDER A SECOND NAME, AND THIS IS NOT DUPLICATION --
#: IT IS THE FIX FOR A MEASURED GUARD RED. Do not "tidy" this back into one
#: constant.
#:
#: MEASURED 2026-09-05 19:38 by running the shipped taint engine
#: (`tests/test_page_text_is_never_printed.py::_tainted_names`) over this
#: file. It returned:
#:
#:     tainted names: ['NEEDLES', 'probe_count', 'probe_word', 'raw',
#:                     'slot', 'tally']
#:
#: `NEEDLES` is a tuple of literals written in this file. It is tainted
#: because it is passed INTO `page.evaluate`, and the engine follows the
#: BINDING rather than the content -- correctly, since a check that tried to
#: reason about content is the check this repository keeps catching being
#: wrong for the inputs it was imagined against. Taint then flowed
#: `NEEDLES -> probe_word -> probe_count` and reached a `print`.
#:
#: So the page-call path and the printing path may not share a name. NEEDLES
#: crosses into the page; REPORT_LABELS never does. Two waves paid for this
#: same module-scope mechanism first: `196394d` (locals `before`/`after`) and
#: the contact-info probe (`key`/`value` in a comprehension).
#:
#: `test_the_two_vocabularies_are_byte_identical` in
#: `tests/test_badge_and_language_affordances.py` asserts they cannot drift.
REPORT_LABELS = (
    "dark",
    "top voice",
    "verified",
    "verification",
    "premium",
    "another language",
    "profile language",
    "add profile in another language",
    "zzq_no_surface_draws_this",
)

MUST_FIND_ON_CONTROL_AT = 0
MUST_BE_ABSENT_AT = 8

# Structural readings that name nothing. `lang` attributes are the strongest
# multi-language signal available that carries no text at all: a member with a
# secondary-language profile has a page that declares more than one language.
_SCRIPT = """
(needles) => {
  const text = (document.body ? document.body.innerText : "").toLowerCase();
  const isWordChar = (c) => c !== undefined && /[a-z0-9]/.test(c);
  const hits = [];
  for (const n of needles) {
    let from = 0;
    let found = 0;
    for (;;) {
      const at = text.indexOf(n, from);
      if (at === -1) break;
      const left = at === 0 ? undefined : text[at - 1];
      const right = text[at + n.length];
      if (!isWordChar(left) && !isWordChar(right)) found += 1;
      from = at + n.length;
    }
    hits.push(found);
  }

  const langNodes = document.querySelectorAll("[lang]");
  const langValues = new Set();
  langNodes.forEach((el) => langValues.add((el.getAttribute("lang") || "").toLowerCase()));
  const docLang = (document.documentElement.getAttribute("lang") || "").toLowerCase();
  langValues.delete("");

  return {
    hits: hits,
    controls: document.querySelectorAll(
      'button, a[href], input, textarea, select, [role="button"], [role="link"]'
    ).length,
    dialogs: document.querySelectorAll('[role="dialog"]').length,
    lang_nodes: langNodes.length,
    distinct_langs: langValues.size,
    langs_other_than_document: docLang === "" ? langValues.size
                                              : (langValues.has(docLang) ? langValues.size - 1
                                                                         : langValues.size),
    text_length: text.length,
  };
}
"""


async def _read(page, url):
    """Navigate and read. Returns a dict of INTEGERS keyed by this file's literals."""
    await page.goto(url, wait_until="domcontentloaded")
    await page.wait_for_timeout(2500)
    raw = await page.evaluate(_SCRIPT, list(NEEDLES))
    return {
        "needle": [int(n) for n in raw["hits"]],
        "controls": int(raw["controls"]),
        "dialogs": int(raw["dialogs"]),
        "lang_nodes": int(raw["lang_nodes"]),
        "distinct_langs": int(raw["distinct_langs"]),
        "langs_other_than_document": int(raw["langs_other_than_document"]),
        "text_length": int(raw["text_length"]),
    }


def report(label, reading):
    """Print one reading. Touches no page and binds nothing page-derived."""
    print("  %s" % label)
    print("    controls %-6d dialogs %-4d text_length %d"
          % (reading["controls"], reading["dialogs"], reading["text_length"]))
    print("    lang_nodes %-4d distinct_langs %-4d other_than_document %d"
          % (reading["lang_nodes"], reading["distinct_langs"],
             reading["langs_other_than_document"]))
    for at in range(len(REPORT_LABELS)):
        print("    needle %-34s %d" % (REPORT_LABELS[at], reading["needle"][at]))


async def main():
    async with BROWSER.session() as session:
        page = await session.context.new_page()
        try:
            badge_first = await dom.read_invitation_badge(page)
            print("invitation badge BEFORE  %s" % badge_first)

            control = await _read(page, CONTROL_URL)
            print()
            print("CONTROL PAGE (admitted, draws no badge and no language selector)")
            report("dark-mode", control)

            gate_find = control["needle"][MUST_FIND_ON_CONTROL_AT]
            gate_absent = control["needle"][MUST_BE_ABSENT_AT]
            print()
            print("CONTROL GATE  must_find=%d (want >0)   must_be_absent=%d (want 0)"
                  % (gate_find, gate_absent))
            if gate_find == 0 or gate_absent != 0:
                print("CONTROL FAILED -- the reader is broken. Live numbers NOT printed.")
                return

            first = await _read(page, PROFILE_URL)
            second = await _read(page, PROFILE_URL)
            print()
            print("HIS OWN PROFILE -- two absolute readings, never subtracted")
            report("read 1", first)
            print()
            report("read 2", second)

            print()
            print("LIVE GATE  must_be_absent read1=%d read2=%d (want 0)"
                  % (first["needle"][MUST_BE_ABSENT_AT],
                     second["needle"][MUST_BE_ABSENT_AT]))

            badge_last = await dom.read_invitation_badge(page)
            print("invitation badge AFTER   %s" % badge_last)
        finally:
            await page.close()
            print()
            print("page closed: %s" % page.is_closed())


if __name__ == "__main__":
    import asyncio

    _ = config
    asyncio.run(main())
