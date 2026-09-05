"""A probe opens a tab in HIS browser. Closing the context would close HIS.

Two checks with very different tempers, and the difference is the point.

**THE HARD ONE: no script may close the CONTEXT.** In ATTACH mode the context
is the operator's own signed-in Chrome and the tab is ours. `page.close()`
removes what we made; `context.close()` removes what he was using. There are
ZERO offenders today, which is exactly when a guard against a hazard is worth
writing -- it costs nobody anything until somebody reaches for the wrong noun,
and by then the reasoning that made it look right is already in a diff.

**THE SOFT ONE: a ratchet on the leak.** Measured 2026-09-05: 43 scripts open
a session and 4 close their tab, so 39 leak one tab per run into his browser.
That is not a bug to fix here -- each script belongs to its own wave -- and a
test demanding all 39 today would be a red nobody could clear. So the count is
pinned and may only GO DOWN. A new leaking script turns it red; fixing one
turns it red too, with a message saying to lower the pin, which is the cheapest
possible way to make progress visible.

## Why this is worth a test rather than a note

The cost is not untidiness and it is not hypothetical. `connect_over_cdp`
enumerates every target on attach. At 115 targets the handshake measured 13.6s,
16.6s and 17.5s against a then-15s ceiling -- so attaching succeeded or failed
by coin flip, and three probe runs died on a handshake that tabs they had
themselves leaked helped slow. The ceiling is now env-overridable, which buys
time against unbounded growth and does not stop it.

## And a measurement note, because it changed the answer

A first pass matched any `.close(` and reported 10 scripts as fixed. Six of
those close something else entirely -- a file, a capture. **The crude count
overstated fleet progress by more than double.** The matchers below name the
RECEIVER, not just the method, which is the difference between counting what
you meant and counting what matched.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"

#: Opening a browser page, by either route. `own_tab()` is the closing wrapper
#: one probe defines; scripts are standalone here by design, so it is named
#: rather than imported.
OPENS = re.compile(r"BROWSER\.session\s*\(\s*\)|own_tab\s*\(\s*\)")

#: Closing OUR tab. The receiver is named: `.close()` alone matches a file
#: handle, and did.
CLOSES_PAGE = re.compile(r"\b(page|tab|_own_page)\s*\.\s*close\s*\(")

#: Closing HIS browser. This is the one that must never appear.
CLOSES_CONTEXT = re.compile(
    r"\b(context|ctx|browser|BROWSER|_context)\s*\.\s*close\s*\("
)

#: How many session-opening scripts do NOT close their tab, as measured on
#: 2026-09-05. **MAY ONLY DECREASE.** Lower it in the commit that fixes one.
LEAKING_AT_LAST_COUNT = 39


def _sources() -> list[tuple[str, str]]:
    return [
        (path.name, path.read_text(encoding="utf-8", errors="replace"))
        for path in sorted(SCRIPTS.glob("*.py"))
    ]


def _openers(sources=None) -> list[tuple[str, str]]:
    """Session-opening sources. THE CORPUS IS A PARAMETER, deliberately.

    Both corpus checks below are aimed at synthetic corpora as well as at the
    real one. The alternative was planting a offending file in ``scripts/`` for
    a few seconds -- in a tree a dozen waves are writing, where another guard
    scanning that directory would have caught it mid-flight and reported a
    defect nobody introduced.
    """
    if sources is None:
        sources = _sources()
    return [(name, text) for name, text in sources if OPENS.search(text)]


def context_closers(sources=None) -> list[str]:
    return [name for name, text in _openers(sources) if CLOSES_CONTEXT.search(text)]


def leakers(sources=None) -> list[str]:
    return sorted(
        name for name, text in _openers(sources) if not CLOSES_PAGE.search(text)
    )


def test_there_are_scripts_to_scan_and_openers_among_them():
    """A scan that matched nothing would pass everything below.

    The refusal-names-what-it-saw rule: assert the corpus EXISTS before
    asserting it is clean, so a directory rename turns this red rather than
    turning the file into a no-op that reports green forever.
    """
    sources = _sources()
    assert len(sources) > 20, f"only {len(sources)} scripts found"
    openers = _openers()
    assert len(openers) > 20, (
        f"only {len(openers)} scripts appear to open a browser session; the "
        "matcher has probably stopped matching"
    )


def test_no_script_closes_the_operators_context():
    """THE HARD ONE. Zero offenders, and it must stay zero.

    Closing the context in attach mode closes the browser he is signed into.
    Nothing in this package has ever needed to, and a script that does has
    almost certainly reached for `context` while meaning `page`.
    """
    offenders = context_closers()
    assert not offenders, (
        f"these scripts close a browser CONTEXT: {offenders}. In ATTACH mode "
        "the context is the operator's own signed-in Chrome and the tab is "
        "ours -- closing it takes his browser down. Close the PAGE instead: "
        "`if not page.is_closed(): await page.close()` in a finally."
    )


def test_the_tab_leak_only_ever_shrinks():
    """THE SOFT ONE. A ratchet, not a demand.

    39 of 43 session-opening scripts leak a tab per run. Each belongs to its
    own wave, so this does not demand they all be fixed today -- it demands
    that the number not grow, and it makes fixing one visible.
    """
    leaking = leakers()
    assert len(leaking) <= LEAKING_AT_LAST_COUNT, (
        f"{len(leaking)} scripts open a browser session and never close the "
        f"tab, up from {LEAKING_AT_LAST_COUNT}. Every probe process leaves a "
        "tab in the operator's Chrome, and connect_over_cdp enumerates every "
        "target on attach -- this is what put the handshake over its ceiling. "
        "Close the PAGE (never the context) in a finally. "
        f"Leaking: {leaking}"
    )
    if len(leaking) < LEAKING_AT_LAST_COUNT:
        raise AssertionError(
            f"GOOD NEWS, AND THE PIN IS STALE: only {len(leaking)} scripts "
            f"leak now, down from {LEAKING_AT_LAST_COUNT}. Lower "
            "LEAKING_AT_LAST_COUNT to that number in the commit that fixed "
            "one, so the ratchet keeps holding. This is the only failure in "
            "this file that is good news."
        )


def test_the_matchers_name_a_receiver_rather_than_a_method():
    """SHOWN FAILING, on the mistake this file's own first pass made.

    A matcher of `.close(` alone counted six scripts as fixed that close a
    file. These assertions drive the real matchers over synthetic source in
    both directions, so a future simplification to `\\.close\\(` fails here
    rather than quietly doubling the reported progress.
    """
    assert CLOSES_PAGE.search("await page.close()")
    assert CLOSES_PAGE.search("await self._own_page.close()")
    assert not CLOSES_PAGE.search("handle.close()"), (
        "the page matcher accepts a bare receiver, which is the over-count "
        "this file was written after"
    )
    assert not CLOSES_PAGE.search("outfile.close()")

    assert CLOSES_CONTEXT.search("await context.close()")
    assert CLOSES_CONTEXT.search("await ctx.close()")
    assert not CLOSES_CONTEXT.search("await page.close()"), (
        "the context matcher fires on a page close, which would make the hard "
        "check refuse the correct remedy"
    )

    assert OPENS.search("async with BROWSER.session() as page:")
    assert OPENS.search("async with own_tab() as page:")
    assert not OPENS.search("session = requests.Session()")


#: SYNTHETIC CORPORA. Written as explicit source strings rather than files, so
#: no offending script ever exists in ``scripts/`` even for a second -- in a
#: tree a dozen waves are writing, another guard scanning that directory would
#: have caught a planted file mid-flight and reported a defect nobody made.
SYNTHETIC_CLEAN = [
    ("a.py", "async with own_tab() as page:\n    await page.close()\n"),
    ("b.py", "async with BROWSER.session() as page:\n    await page.close()\n"),
]
SYNTHETIC_LEAK = SYNTHETIC_CLEAN + [
    ("c.py", "async with BROWSER.session() as page:\n    pass\n"),
]
SYNTHETIC_HAZARD = SYNTHETIC_CLEAN + [
    ("d.py", "async with BROWSER.session() as page:\n    await context.close()\n"),
]


def test_the_corpus_checks_are_shown_failing_on_a_corpus_that_deserves_it():
    """Both checks, driven over synthetic corpora, in BOTH directions.

    A guard that has only ever been seen passing certifies nothing -- and
    these two run over a real directory that is currently clean of the hazard,
    so without this they would be exactly that.
    """
    assert context_closers(SYNTHETIC_CLEAN) == []
    assert leakers(SYNTHETIC_CLEAN) == []

    assert leakers(SYNTHETIC_LEAK) == ["c.py"], leakers(SYNTHETIC_LEAK)
    assert context_closers(SYNTHETIC_LEAK) == [], (
        "a leaking script is not a hazard, and conflating the two would make "
        "the hard check fire on 39 scripts that do nothing dangerous"
    )

    assert context_closers(SYNTHETIC_HAZARD) == ["d.py"]
    assert leakers(SYNTHETIC_HAZARD) == ["d.py"], (
        "the hazard script also fails to close its PAGE, so it should appear "
        "in both -- if it appeared only in one, the two checks are reading "
        "different things than they claim"
    )
